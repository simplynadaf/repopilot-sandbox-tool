"""RepoPilot's new tool: actually RUN the repo in a disposable AWS sandbox.

Before this tool, RepoPilot judged a repository from the outside: it read the README, the
manifests and the file list, then reasoned about whether the setup looked safe and whether
the first-run plan would work. Useful, but a guess.

This tool closes that gap. It clones the repo and runs its detected install/setup inside an
ephemeral AWS CodeBuild container, captures the real build log, and reports what ACTUALLY
happened: did install succeed, what exited non-zero, and did any setup step reach out to the
network in a way that looks like a supply-chain risk (curl | bash, piping a remote script to
a shell, etc.). The container is thrown away after the run. No packets touch your laptop.

Design notes (match RepoPilot's existing tools):
  * Pure-ish and testable: the AWS calls live behind a small client seam so unit tests run
    with a fake client, no AWS needed.
  * Deterministic verdict logic (`summarize_build`) is separated from the AWS plumbing so it
    can be tested directly and reused by the offline/static demo path.

Pain -> tool mapping:
  * "the README says it is safe, but is it really?"  -> run_in_sandbox (real execution)
  * "a postinstall script could curl|bash something" -> danger scan over the real log
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Optional, Any


# --------------------------------------------------------------------------------------
# Result model
# --------------------------------------------------------------------------------------
@dataclass
class SandboxResult:
    """What actually happened when we ran the repo's setup in the sandbox."""

    repo: str
    status: str                      # SUCCEEDED | FAILED | TIMED_OUT | ERROR
    install_ok: bool
    exit_hint: str                   # one-line plain-language cause when it failed
    danger_signals: list[dict] = field(default_factory=list)  # supply-chain red flags found
    log_tail: str = ""               # last lines of the real build log
    duration_s: float = 0.0
    verified: bool = True            # False when we could not run (e.g. no AWS) -> fall back


# --------------------------------------------------------------------------------------
# Danger scan over the REAL execution log (not the static README)
# --------------------------------------------------------------------------------------
# Each pattern: (id, regex, human explanation). Kept conservative to avoid false alarms.
_DANGER_PATTERNS = [
    ("remote_pipe_to_shell",
     re.compile(r"(curl|wget)\s+[^\n|]*\|\s*(sudo\s+)?(bash|sh|zsh)\b", re.I),
     "A setup step piped a script downloaded from the internet straight into a shell."),
    ("eval_remote",
     re.compile(r"\beval\s+\"?\$\((curl|wget)\b", re.I),
     "A setup step eval'd the output of a remote download."),
    ("chmod_then_run_download",
     re.compile(r"(curl|wget)[^\n]+-o\s+\S+[\s\S]{0,120}?chmod\s+\+x[\s\S]{0,120}?\./", re.I),
     "A setup step downloaded a file, made it executable, and ran it."),
    ("sudo_in_install",
     re.compile(r"\bsudo\s+(rm|dd|mkfs|chmod\s+777|chown)\b", re.I),
     "A setup step ran a privileged, potentially destructive command."),
]


def scan_log_for_danger(log_text: str) -> list[dict]:
    """Find supply-chain / destructive red flags in the REAL build log.

    This is the honest upgrade over static README scanning: we match on what the build
    actually executed, so it catches dangers a postinstall hook hid from the README.
    """
    found: list[dict] = []
    for pat_id, rx, why in _DANGER_PATTERNS:
        m = rx.search(log_text or "")
        if m:
            snippet = m.group(0).strip()
            if len(snippet) > 160:
                snippet = snippet[:157] + "..."
            found.append({"id": pat_id, "why": why, "evidence": snippet})
    return found


# --------------------------------------------------------------------------------------
# Verdict logic (pure, testable) over a finished build + its log
# --------------------------------------------------------------------------------------
def summarize_build(repo: str, status: str, log_text: str, duration_s: float = 0.0) -> SandboxResult:
    """Turn a finished CodeBuild status + log into RepoPilot's plain-language verdict."""
    install_ok = status == "SUCCEEDED"
    danger = scan_log_for_danger(log_text)

    exit_hint = ""
    if not install_ok:
        exit_hint = _guess_failure_cause(log_text)

    tail = "\n".join((log_text or "").splitlines()[-25:])
    return SandboxResult(
        repo=repo,
        status=status,
        install_ok=install_ok,
        exit_hint=exit_hint,
        danger_signals=danger,
        log_tail=tail,
        duration_s=round(duration_s, 1),
        verified=True,
    )


# Common, recognisable failure fingerprints -> one-line cause (RepoPilot's patient-teammate voice).
_FAILURE_HINTS = [
    (re.compile(r"E: Unable to locate package|command not found|not found in PATH", re.I),
     "A required system tool or package is missing from the environment."),
    (re.compile(r"ERR_PNPM|npm ERR!|peer dep|ERESOLVE", re.I),
     "The Node install failed, usually a dependency or lockfile mismatch."),
    (re.compile(r"No matching distribution|Could not find a version|ModuleNotFoundError", re.I),
     "A Python dependency could not be resolved or imported."),
    (re.compile(r"permission denied|EACCES", re.I),
     "A step hit a permissions error."),
    (re.compile(r"network|timed out|temporary failure in name resolution|could not resolve host", re.I),
     "A step failed reaching the network from the sandbox."),
    (re.compile(r"version .* required|requires python|unsupported version", re.I),
     "The repo needs a different tool/runtime version than the environment provides."),
]


def _guess_failure_cause(log_text: str) -> str:
    for rx, hint in _FAILURE_HINTS:
        if rx.search(log_text or ""):
            return hint
    return "The setup exited with an error. See the log tail for the failing step."


# --------------------------------------------------------------------------------------
# buildspec: what the disposable container actually runs
# --------------------------------------------------------------------------------------
def build_buildspec(clone_url: str, install_cmd: str) -> str:
    """A CodeBuild buildspec that clones the repo and runs ONLY its detected install step.

    Robust to arbitrary quoting in install_cmd: we base64-encode a small shell script and
    decode+run it at build time, so no quotes in the user's command can break the YAML.
    We run install in a subshell, print clear markers, and do NOT run the app itself.
    """
    import base64
    safe_url = clone_url.replace("'", "").replace('"', "").strip()
    script = (
        'set +e\n'
        'echo "REPOPILOT_SANDBOX_START"\n'
        f'git clone --depth 1 {safe_url} repo || {{ echo "REPOPILOT_CLONE_FAILED"; exit 1; }}\n'
        'cd repo\n'
        f'( {install_cmd.strip()} ) 2>&1\n'
        'code=$?\n'
        'echo "REPOPILOT_INSTALL_EXIT=$code"\n'
        'echo "REPOPILOT_SANDBOX_END"\n'
        'exit $code\n'
    )
    b64 = base64.b64encode(script.encode("utf-8")).decode("ascii")
    return (
        "version: 0.2\n"
        "phases:\n"
        "  build:\n"
        "    commands:\n"
        f"      - echo {b64} | base64 -d > /tmp/repopilot_run.sh\n"
        "      - bash /tmp/repopilot_run.sh\n"
    )


# --------------------------------------------------------------------------------------
# AWS plumbing (behind a seam so tests do not need AWS)
# --------------------------------------------------------------------------------------
class CodeBuildSandbox:
    """Runs a repo's install in an ephemeral AWS CodeBuild project and returns the verdict.

    The CodeBuild project is expected to exist (created by scripts/setup_sandbox.sh with a
    least-privilege role, no outbound beyond what install needs, and a short timeout). We
    override the buildspec per run via startBuild, so one project serves every repo.
    """

    def __init__(self, project_name: str, clients: Optional[dict] = None, region: Optional[str] = None):
        self.project_name = project_name
        if clients is not None:
            self.cb = clients["codebuild"]
            self.logs = clients["logs"]
        else:  # pragma: no cover - needs AWS
            import boto3  # type: ignore
            self.cb = boto3.client("codebuild", region_name=region)
            self.logs = boto3.client("logs", region_name=region)

    def run(self, repo: str, clone_url: str, install_cmd: str,
            poll_s: float = 5.0, max_wait_s: float = 420.0) -> SandboxResult:
        spec = build_buildspec(clone_url, install_cmd)
        start = time.time()
        resp = self.cb.start_build(projectName=self.project_name, buildspecOverride=spec)
        build_id = resp["build"]["id"]

        status = "IN_PROGRESS"
        log_group = log_stream = None
        while time.time() - start < max_wait_s:
            time.sleep(poll_s)
            b = self.cb.batch_get_builds(ids=[build_id])["builds"][0]
            status = b.get("buildStatus", "IN_PROGRESS")
            li = b.get("logs", {})
            log_group, log_stream = li.get("groupName"), li.get("streamName")
            if status != "IN_PROGRESS":
                break

        log_text = self._fetch_log(log_group, log_stream)
        if status == "IN_PROGRESS":
            status = "TIMED_OUT"
        return summarize_build(repo, status, log_text, duration_s=time.time() - start)

    def _fetch_log(self, group: Optional[str], stream: Optional[str]) -> str:
        if not group or not stream:
            return ""
        try:
            events = self.logs.get_log_events(
                logGroupName=group, logStreamName=stream, startFromHead=True, limit=300
            ).get("events", [])
            return "\n".join(e.get("message", "").rstrip() for e in events)
        except Exception:  # pragma: no cover
            return ""


def unavailable_result(repo: str, reason: str) -> SandboxResult:
    """When the sandbox cannot run (no AWS creds / project). RepoPilot falls back to static."""
    return SandboxResult(
        repo=repo, status="ERROR", install_ok=False,
        exit_hint=reason, danger_signals=[], log_tail="", verified=False,
    )
