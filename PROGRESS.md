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
Steps 1-4 of the original plan are DONE. README/Pages/repo/article/thumbnail/banner DONE
this session (2026-10-23 evening). Remaining:

1. [x] README.md (advanced, 2387 words, 17 sections, before/after headline, run-vs-scan table,
       threat model, reusable pattern, proof, honest take, FAQ). 0 em dashes. Committed+pushed.
2. [x] New PUBLIC repo LIVE: github.com/simplynadaf/repopilot-sandbox-tool (pushed, main).
3. [x] GitHub Pages LIVE + verified: https://simplynadaf.github.io/repopilot-sandbox-tool/
       (the before/after toggle demo, served from /docs, $0, static replay).
4. [x] Thumbnail docs/thumbnail.png (1280x720, "Stop scanning. Run it." + before/after chips).
       Builder Center cover docs/banner.png (1200x675, repo->sandbox->verdict flow, minimal text).
       Both under 2MB. Committed+pushed.
5. [x] Builder Center ARTICLE: docs/ARTICLE.md (fields block up top: title/desc/tags/cover, then
       ~1250-word body). Passes all hard rules (0 em dashes, no AI tells, `---` separators).
6. [~] AI-voiceover before/after demo video (<3 min). IN PROGRESS:
   [x] DEMO_SCRIPT.md written (shot list + VO, shows OLD RepoPilot UI + NEW toggle, ~2:15).
   [x] Intro card docs/card-intro.html + outro card docs/card-outro.html (GSAP, gold/black).
       Verified intro renders. Recorded both to WebM:
       ~/repopilot-sandbox-rec/cards/intro/*.webm  and  .../outro/*.webm
   [x] Main demo recorded: docs/record_demo.js drives the real toggles (v1 safe -> v1 sneaky
       "looks fine" -> v2 sneaky CATCHES curl|bash -> v2 safe clean -> OLD RepoPilot UI live ->
       close on caught danger). Output: ~/repopilot-sandbox-rec/demo/*.webm (43s). QA frames
       confirmed all key states landed; ends on the caught-danger frame. GOOD.
   [ ] NEXT: synth Polly Matthew VO per DEMO_SCRIPT cues (hook/gap/payoff/safe/real/close) ->
       ~/repopilot-sandbox-rec/voiceover/*.mp3, place with adelay, add quiet sine ambient bed,
       mux onto the concatenated video, loudnorm I=-16. Recorder holds total ~58s but the demo
       segment may need slow-down / re-timing to fit the ~2:15 narration (or tighten the VO).
       Pattern: copy the checkpoint ffmpeg steps in ~/.kiro/skills/youtube-recording AI-voiceover
       section (adelay mix -> bed -> mux -> loudnorm) and the concat (intro + demo + outro).
   [ ] THEN: convert final WebM->MP4, upload to YouTube (title from NAMING-AND-TITLES.md),
       add the YouTube URL into README + docs/ARTICLE.md links.
   Recording env: NODE_PATH=~/repopilot-recording/node_modules, chromium-1248, ffmpeg at
   ~/.local/bin/ffmpeg, Polly Matthew (neural) in us-east-1. Serve demo for re-records:
   (cd docs && python3 -m http.server 8099).
7. [ ] Optional Dev.to syndication (DEVTO-ARTICLE.md) with canonical_url.
8. [ ] S3 backup to s3://sarvars-youtube-videos/repopilot-sandbox-tool/ (repo + article + images).
9. [ ] Fill the Builder Center project form from docs/ARTICLE.md fields block + submit with the
       demo video link.
10.[ ] Promo posts (LinkedIn Unicode bold + link in first comment, X thread).

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

## DELIVERABLES THE USER WANTS (authoritative checklist, keep in mind always)
1. [x] YouTube DEMO VIDEO            -> RENDERED. docs/demo.mp4 (1:30, 1920x1080, 6.6MB, <3min).
                                        Polly Matthew VO + ambient bed + loudnorm. Shows OLD
                                        RepoPilot UI + NEW toggle (v1 reads -> v2 runs ->
                                        catches curl|bash -> safe -> old UI -> close). QA'd:
                                        speech -17..-20dB in every window; frames correct.
                                        Also at ~/repopilot-sandbox-rec/final/ + in S3.
                                        LEFT: upload to YouTube (needs user account).
2. [x] YouTube METADATA              -> docs/YOUTUBE-METADATA.md (title 82ch, desc, tags,
                                        chapters, A/B title, AI-voice disclosure note).
3. [x] DEV.TO ARTICLE               -> docs/DEVTO-ARTICLE.md (front-matter, canonical, 4 tags,
                                        {% embed %} repo, code block). Hard rules pass.
4. [x] PROJECT (Builder Center form) -> docs/SUBMIT-01-project.txt (title 85, desc 306, tags,
                                        cover=banner.png, repo, demo). Ready to paste.
5. [x] POST (challenge space)        -> docs/SUBMIT-02-post.txt (title 104/150, body). Ready.
6. [ ] PROMOTION posts               -> LinkedIn (Unicode bold, link in 1st comment) + X thread
                                        (docs/promo/). NOT DONE YET. Next up.
7. [x] THUMBNAIL 1280x720            -> docs/thumbnail.png
8. [x] COVER IMAGE 1200x675          -> docs/banner.png

ONE STEP THAT NEEDS THE USER: upload docs/demo.mp4 to YouTube (metadata ready). Once we have
the URL, inject it into: README.md, docs/ARTICLE.md, docs/DEVTO-ARTICLE.md,
docs/SUBMIT-01-project.txt, docs/SUBMIT-02-post.txt, docs/YOUTUBE-METADATA.md, docs/promo/*.
Then: submit the Builder Center project + post, publish Dev.to (canonical), post promo.

## STATE SNAPSHOT (end of 2026-10-23, evening session 2)
WORKING DIR: ~/weekend-hackathon/build/repopilot-sandbox  (git, pushed to GitHub, main)

CORE (done, validated against LIVE AWS twice today):
- repopilot/sandbox.py: the new tool. 9/9 tests green.
- repopilot/agent.py: 6 tools (5 original + run_in_sandbox). Imports clean.
- AWS LIVE in acct 175662053988 / us-east-1: role repopilot-sandbox-role + CodeBuild
  project repopilot-sandbox (amazonlinux2-x86_64-standard:5.0, 10min timeout).
- Live re-runs today: pallets/click -> SUCCEEDED, no danger; sneaky -> caught
  remote_pipe_to_shell (curl|bash) from the real log. BOTH PASS.

SHIPPED + PUBLIC:
- Repo:  https://github.com/simplynadaf/repopilot-sandbox-tool  (public, pushed)
- Live demo (Pages, $0, before/after toggle): https://simplynadaf.github.io/repopilot-sandbox-tool/
- README.md: advanced (2387 words, 17 sections). 0 em dashes.
- docs/ARTICLE.md: Builder Center submission (fields block + ~1250-word body). Passes hard rules.
- docs/thumbnail.png (1280x720), docs/banner.png (1200x675 cover). Both <2MB.
- docs/index.html: the before/after toggle UI. docs/replay-data.json: real recorded runs.
- S3 backup: s3://sarvars-youtube-videos/repopilot-sandbox-tool/  (whole project + _BUILD-PROGRESS.md)

OLD vs NEW links (for the judges, both live):
- OLD RepoPilot UI:  https://simplynadaf.github.io/repopilot-your-first-run-agent/
- OLD RepoPilot repo: https://github.com/simplynadaf/repopilot-your-first-run-agent
- NEW demo + repo: the two URLs above.

DEMO VIDEO (DONE and verified):
- docs/demo.mp4: FINAL 1:30, 1920x1080, H.264+AAC, 6.6MB (<3min). Intro card -> old-vs-new
  walkthrough (v1 safe -> v1 sneaky "looks fine" -> v2 sneaky CATCHES curl|bash -> v2 safe
  clean -> OLD RepoPilot UI live -> close on caught danger) -> outro card. Polly Matthew VO
  (hook/gap/payoff/safe/close) placed with adelay + quiet sine ambient bed, loudnorm I=-16.
  QA: speech -17..-20dB each window; payoff + close frames confirmed correct.
  Sources: ~/repopilot-sandbox-rec/ (cards/, demo/, voiceover/, final/). S3 backup done.
- DEMO_SCRIPT.md (shot list + VO), card-intro.html, card-outro.html, record_cards.js,
  record_demo.js (holds re-timed to the VO). Serve to re-record: (cd docs && python3 -m http.server 8099).
- ONLY LEFT: upload docs/demo.mp4 to YouTube (metadata ready in docs/YOUTUBE-METADATA.md).

DEADLINE: Monday Oct 26, 1:00 PM PT (8:00 PM UTC). ~2.5 days left. On track.

## NEXT (in order) when we resume
1. Write PROMOTION posts: LinkedIn (Unicode bold via ~/tools/linkedin-poster/tools/bold.py,
   link in first comment) + X thread. Save to docs/promo/. (video/images already exist.)
2. Upload docs/demo.mp4 to YouTube (needs user account; metadata in docs/YOUTUBE-METADATA.md).
3. Inject the YouTube URL everywhere: README.md, docs/ARTICLE.md, docs/DEVTO-ARTICLE.md,
   docs/SUBMIT-01-project.txt, docs/SUBMIT-02-post.txt, docs/YOUTUBE-METADATA.md, docs/promo/*.
4. Submit the Builder Center PROJECT (SUBMIT-01) + POST (SUBMIT-02). Publish Dev.to (canonical).
   Post the promo.
5. When fully submitted: run scripts/teardown_sandbox.sh (removes CodeBuild project + role).

## How to resume
`cd ~/weekend-hackathon/build/repopilot-sandbox && source ~/agent-experiance/.venv/bin/activate`
`export REPOPILOT_SANDBOX_PROJECT=repopilot-sandbox`
Run sandbox tests: `python -m pytest tests/test_sandbox.py -q` (or the fallback runner, 9/9).
Read ../WINNING-CONCEPT.md, ../PLAYBOOK.md, ../NAMING-AND-TITLES.md first.

## Env / facts
- Python 3.11 venv at ~/agent-experiance/.venv (strands-agents, boto3 installed).
- Model: amazon.nova-pro-v1:0 (us-east-1), verified invoke-accessible.
- New tool reads env REPOPILOT_SANDBOX_PROJECT for the CodeBuild project name.
- ffmpeg: ~/.local/bin/ffmpeg. Polly: Matthew (neural), us-east-1.
- OPEN DECISION (still fine): we frame this as a NEW project centered on the new tool, reusing
  the already-published RepoPilot as "an agent you already built". Repo/titles lead with the TOOL.
- Deadline: Monday Oct 26, 1:00 PM PT (8:00 PM UTC).
