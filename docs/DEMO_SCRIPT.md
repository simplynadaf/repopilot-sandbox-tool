# Demo video script: "I gave my agent one new tool" (target 2:15, max 2:40)

Format: screen capture of the LIVE UIs + Polly Matthew voiceover + ambient bed + intro/outro
cards. Shows BOTH the old RepoPilot (reads it) and the new sandbox tool (runs it), so judges
see old vs new live, plus a real AWS result.

Hackathon hits: one new tool, before/after shown, >=1 AWS service (CodeBuild + Bedrock),
under 3 minutes, public links.

Pipeline (same as the checkpoint win):
1. GSAP intro/outro cards -> WebM (record_cards.js)
2. UI walkthrough -> WebM via Playwright recordVideo driving the real toggle (record_demo.js)
3. Polly Matthew narration per cue (segments.txt -> mp3s, placed with adelay)
4. ambient bed (sine drone, quiet) + mux + loudnorm
5. ffmpeg concat: intro + demo + outro -> final.mp4

URLs used on camera:
- OLD RepoPilot UI: https://simplynadaf.github.io/repopilot-your-first-run-agent/
- NEW toggle demo:  served locally at http://127.0.0.1:8099/  (docs/index.html; same as Pages)

---

## Shot list + voiceover

### INTRO CARD  (0:00-0:07)
Card: title "I gave my agent one new tool" + "a disposable AWS sandbox that actually runs the repo".
(no VO over the very start; hook VO begins as the demo opens)

### 0:07-0:28  Hook + the old agent (reads it)
On screen: the NEW demo page header, then flip to "Before / v1 (reads it)" on the Safe repo.
VO (hook): "I already built an agent that looks at a GitHub repo and tells you if it is safe
to run. The problem was that word, looks. It judged the repo by reading it. The README, the
file list. A book report. So I gave it one new tool, and it stopped guessing."

### 0:28-0:50  The gap
On screen: stay on v1, switch the repo toggle to "Sneaky repo". v1 still says "Looks fine."
VO: "Here is the gap. The dangerous part of a repo is not what you read. It is what runs the
second you type npm install. A postinstall hook fires with your whole environment. And a tool
that only reads the repo cannot see it. Watch. On this sneaky repo, the old agent still says,
looks fine."

### 0:50-1:25  The new tool runs it (the payoff)
On screen: flip "After / v2 (runs it)" while still on Sneaky repo. The real sandbox log appears
and the red danger card shows remote_pipe_to_shell with the curl|bash evidence.
VO: "Now the new tool. run_in_sandbox clones the repo and actually runs the install inside a
disposable AWS CodeBuild container, then reads the real build log. Same repo. And there it is,
caught in the log: the install piped curl into bash. A scan would never have seen that. The
container is thrown away after the run, so the untrusted code ran in AWS, never on my machine."

### 1:25-1:45  Safe repo, v2 (balance)
On screen: switch repo to "Safe repo", stay on v2. Green, no danger, SUCCEEDED.
VO: "On a genuinely safe repo it runs the same way and comes back clean. Succeeded, nothing
dangerous in the log. It is not paranoid. It just checks by running, not by reading."

### 1:45-2:05  It is real (the old UI + proof)
On screen: open the ORIGINAL RepoPilot UI in a second tab briefly (the agent I already built),
then back.
VO: "This is one new tool on an agent I already shipped. The talking is Amazon Bedrock with
Nova Pro through Strands. The new power is one Strands tool backed by AWS CodeBuild. Both runs
you just saw were validated against live AWS."

### 2:05-2:20  Close + reusable
On screen: back on the new demo, the tagline line.
VO (close): "Point the same tool at any should-I-run-this decision and it runs it in a
disposable box and decides from the real log. Everyone scans the repo. This agent runs it, so
your laptop does not. Code and a live before-and-after toggle are in the description. If this
made you think twice before your next npm install, give it a star."

### OUTRO CARD  (2:20-2:30)
Card: repo + live demo URLs, socials, like/comment/share.

---

## Timing notes
- The new demo has no cold starts (static replay), so typing/toggle motion is smooth and fast.
- Keep each toggle hold ~2.5-3s so the viewer reads the change.
- Trim any dead frames in the edit; re-time the Polly adelays to the final cut.
- Disclose AI voice on YouTube (synthetic voice, real screen recording).
