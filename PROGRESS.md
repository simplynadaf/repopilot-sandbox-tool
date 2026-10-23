# BUILD PROGRESS — RepoPilot + Sandbox (Weekend Challenge: Give your Agent a Tool)

Project: take our EXISTING RepoPilot agent (Strands + Bedrock + Nova Pro) and add ONE new
tool: actually RUN the repo's install in a disposable AWS CodeBuild sandbox and report the
REAL result + supply-chain danger. Ship a UI with a BEFORE (v1) / AFTER (v2+sandbox) toggle
so judges see the exact capability we added.

Base copied from the published RepoPilot repo into:
  ~/weekend-hackathon/build/repopilot-sandbox/   (git history stripped; this is the new project)
Original (published, do not resubmit): ~/builder-center-challenge/repopilot  and
  github.com/simplynadaf/repopilot-your-first-run-agent (LIVE, so this entry is a NEW project
  centered on the new tool — confirm the "previously unpublished" reading before submitting).

## DONE (this session)
- [x] Chose the winning concept (see ../WINNING-CONCEPT.md UPDATE 3): RepoPilot + CodeBuild
      "actually run it" verification tool. Passes the "is AWS already doing it?" filter.
- [x] DEEP TITLE RESEARCH -> locked names (see NAMING-AND-TITLES.md). Differentiator: the
      whole "vet a repo" field does STATIC scanning; we actually RUN it. Identity = "runs it".
      Repo: repopilot-runs-it. Builder/Dev.to/YouTube titles locked. Tagline:
      "Everyone scans the repo. RepoPilot runs it, in a box, so your laptop doesn't."
- [x] Copied RepoPilot as the base for the new project.
- [x] Wrote the new tool: repopilot/sandbox.py (CodeBuild run, real-log danger scan, verdict,
      graceful fallback), behind a testable client seam.
- [x] Wrote tests/test_sandbox.py (8 tests, all pass, no AWS needed).
- [x] Wired run_in_sandbox_tool into repopilot/agent.py (now 6 tools) + updated SYSTEM_PROMPT.
- [x] Confirmed AWS: account 175662053988, us-east-1, CodeBuild API reachable. Model
      amazon.nova-pro-v1:0 available.
- [x] IAM: least-privilege role (iam/codebuild-trust.json + codebuild-permissions.json, logs-only).
- [x] scripts/setup_sandbox.sh + teardown_sandbox.sh. RAN setup -> created role
      repopilot-sandbox-role + CodeBuild project "repopilot-sandbox" (LINUX_SMALL, 10min timeout,
      CloudWatch logs). LIVE.
- [x] Fixed build_buildspec to base64-encode the run script (survives any quoting). 9/9 tests pass.
- [x] REAL end-to-end validated against live AWS:
      - good repo pallets/click -> SUCCEEDED, install_ok, no danger. 
      - sneaky postinstall -> SUCCEEDED, and CAUGHT "curl | bash" (remote_pipe_to_shell) from the REAL log.
- [x] docs/replay-data.json: captured both real results (for the $0 static demo).
- [x] docs/index.html: the BEFORE/AFTER toggle UI (premium gold/black). Two toggles:
      v1(reads it)/v2(runs it) and Safe/Sneaky repo. v2+Sneaky shows the real log + the caught
      danger. Verified in browser, 0 console errors. THE CENTERPIECE.

## TODO (next session, in order)
Steps 1-4 of the original plan are DONE (see the [x] items above). Remaining:

1. [ ] README.md for the new repo (tool-first, before/after, the "runs it vs scans it" hook,
       locked titles from NAMING-AND-TITLES.md, how-to-run, the SuspicionGate-style reusable
       note for run_in_sandbox). Style like the checkpoint/RepoPilot READMEs. `---` separators.
2. [ ] Enable GitHub Pages for the $0 static demo (docs/index.html already works standalone;
       it uses inline DATA, no live calls). New repo: repopilot-sandbox-tool.
3. [ ] AI-voiceover before/after demo video (<3 min) via youtube-recording skill:
       record the toggle UI (v1 reads -> v2 runs -> Sneaky repo catches curl|bash), Polly
       Matthew narration, intro/outro cards, loudness-normalize. Trim any dead air.
4. [ ] Articles: Builder Center submission (ARTICLE.md) + optional Dev.to (DEVTO-ARTICLE.md).
       Use the locked titles. Mention the challenge, embed repo + live demo + YouTube. Run the
       writing-craft checks (0 em dashes, `---` separators, no AI tells, 4 tags).
5. [ ] Thumbnail (1280x720) + Builder Center cover banner (1200x675) + social banner, same
       gold/black theme. Reuse the checkpoint generators as templates.
6. [ ] Create NEW public GitHub repo `simplynadaf/repopilot-sandbox-tool`, push. S3 backup to
       s3://sarvars-youtube-videos/repopilot-sandbox-tool/.
7. [ ] Fill the Builder Center project form (field-by-field guide like the checkpoint one):
       title/description/body/tags/repo/demo-video. Submit with the demo video link.
8. [ ] Promo posts (LinkedIn Unicode bold + link in first comment, X thread, Slack).

## OPEN DECISION (resolve first tomorrow)
"Previously unpublished project": our RepoPilot is already published. We are framing THIS as a
NEW project centered on the NEW tool (the sandbox), reusing RepoPilot's code as "an agent you
already built". The new repo name is repopilot-sandbox-tool and public titles lead with the
TOOL, not the word RepoPilot. Confirm this reading is acceptable before publishing/submitting.
If risky: keep RepoPilot code as a private starting point and present the sandbox-verification
agent as the fresh project.

## HOW TO RESUME TOMORROW (exact)
```
cd ~/weekend-hackathon/build/repopilot-sandbox
source ~/agent-experiance/.venv/bin/activate
export REPOPILOT_SANDBOX_PROJECT=repopilot-sandbox      # the live CodeBuild project
```
- Read first: ../NAMING-AND-TITLES.md (locked titles), ../WINNING-CONCEPT.md, ../PLAYBOOK.md.
- Re-run unit tests:  python -m pytest tests/test_sandbox.py -q   (or the fallback runner; 9/9).
- Preview the toggle UI:  (cd docs && python3 -m http.server 8096)  then open /index.html.
- Re-run a LIVE sandbox check if needed (good + sneaky) to re-capture fresh output for the video.
- The CodeBuild project + IAM role are LIVE in account 175662053988 / us-east-1. When fully
  done, run scripts/teardown_sandbox.sh to remove them (cost is pennies; fine to leave over one night).

## STATE SNAPSHOT (end of 2026-10-23)
- Working dir: ~/weekend-hackathon/build/repopilot-sandbox  (git initialized, 1 commit, 29 files)
- Core tool repopilot/sandbox.py: DONE + validated live. 9/9 tests green.
- Agent repopilot/agent.py: 6 tools (5 original + run_in_sandbox). Imports clean.
- UI docs/index.html: before/after toggle, verified, 0 console errors.
- AWS: role repopilot-sandbox-role + project repopilot-sandbox LIVE (us-east-1).
- Deadline: Monday Oct 26, 1:00 PM PT (8:00 PM UTC). ~2.5 days left. On track.
- Titles LOCKED (NAMING-AND-TITLES.md): repo=repopilot-sandbox-tool; Builder="I gave my agent
  one new tool: a disposable AWS sandbox that actually runs the repo"; etc.

## How to resume
`cd ~/weekend-hackathon/build/repopilot-sandbox && source ~/agent-experiance/.venv/bin/activate`
Run sandbox tests: `python -m pytest tests/test_sandbox.py -q` (or the fallback runner).
Read ../WINNING-CONCEPT.md and ../PLAYBOOK.md first.

## Env / facts
- Python 3.11 venv at ~/agent-experiance/.venv (strands-agents, boto3 installed).
- Model: amazon.nova-pro-v1:0 (us-east-1), verified invoke-accessible.
- New tool reads env REPOPILOT_SANDBOX_PROJECT for the CodeBuild project name.
- Deadline: Monday Oct 26, 1:00 PM PT (8:00 PM UTC).
