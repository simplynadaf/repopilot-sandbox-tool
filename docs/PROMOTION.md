================================================================================
PROMOTION  —  RepoPilot sandbox tool  (AWS Builder Center weekend challenge)
================================================================================
Fill YOUTUBE_URL after upload, then post. Hard rules: 0 em dashes. Link in first
comment on LinkedIn (the algorithm suppresses posts with outbound links in the body).
================================================================================


--------------------------------------------------------------------------------
LINKEDIN  (post body — put the link in the FIRST COMMENT, not here)
--------------------------------------------------------------------------------
I built an agent that reads a GitHub repo and tells you if it is safe to run.

The problem was that word. Reads.

It judged the repo from the outside. The README, the file list, the manifests. A
book report. And the dangerous part of a repo is not what you read. It is what runs
the second you type npm install, when a postinstall hook fires with your whole
environment, your keys, your tokens.

So for the AWS Builder Center weekend challenge I gave it one new tool.

𝗿𝘂𝗻_𝗶𝗻_𝘀𝗮𝗻𝗱𝗯𝗼𝘅 clones the repo and actually runs the install inside a disposable
AWS CodeBuild container, then reads the real build log.

Same agent. Same sneaky repo.
Before: "Looks fine."
After: "Caught it. The install piped curl into bash." Straight from the live log.

The container is thrown away after the run, so the untrusted code runs in AWS,
never on my laptop.

One new tool on an agent I already shipped. The reasoning is Amazon Bedrock with
Nova Pro through Strands. The new power is a single Strands tool backed by AWS
CodeBuild, with a least privilege role and 9 offline tests. Both runs were
validated against live AWS.

Everyone scans the repo. This agent runs it, so your laptop does not.

Code, a live demo, and a 2 minute before-and-after video in the first comment.

#AWS #AIAgents #CodeBuild #Bedrock #SupplyChainSecurity #DevOps

--- FIRST COMMENT (post immediately after) ---
Demo video: YOUTUBE_URL
Live demo: https://simplynadaf.github.io/repopilot-sandbox-tool/
Code: https://github.com/simplynadaf/repopilot-sandbox-tool


--------------------------------------------------------------------------------
X / TWITTER  (thread, 5 posts)
--------------------------------------------------------------------------------
1/
I built an agent that reads a GitHub repo and says if it is safe to run.

The problem was that word. Reads.

So I gave it one new tool: a disposable AWS sandbox that actually runs the install.

Before vs after 👇

2/
The dangerous part of a repo is not what you read.

It is what runs the second you type npm install. A postinstall hook fires with your
whole environment, your keys, your tokens.

A tool that only reads the repo cannot see it.

3/
run_in_sandbox clones the repo and runs the install inside a disposable AWS
CodeBuild container, then reads the REAL build log.

Same sneaky repo:
Before: "Looks fine."
After: "Caught it, the install piped curl | bash into a shell."

4/
The container is thrown away after the run.

The untrusted code runs in AWS, never on your laptop.

One Strands tool, Amazon Bedrock Nova Pro for the reasoning, a least-privilege
CodeBuild role, 9 offline tests. Both runs validated against live AWS.

5/
Everyone scans the repo. This agent runs it, so your laptop does not.

Built for the AWS Builder Center weekend challenge.

Demo: YOUTUBE_URL
Live: https://simplynadaf.github.io/repopilot-sandbox-tool/
Code: https://github.com/simplynadaf/repopilot-sandbox-tool


--------------------------------------------------------------------------------
YOUTUBE COMMUNITY / SHORT POST
--------------------------------------------------------------------------------
New video: I gave my AI agent one new tool, a disposable AWS sandbox that actually
runs a repo instead of just reading it. It caught a postinstall piping curl into
bash that a static scan would miss. Full before and after in the video.
YOUTUBE_URL


--------------------------------------------------------------------------------
BUILDER CENTER DISCUSSION TAB (optional, short)
--------------------------------------------------------------------------------
Submitted mine: RepoPilot could already read a repo and score it. I added one tool,
run_in_sandbox, that runs the install in a disposable AWS CodeBuild container and
reads the real log, catching a curl | bash postinstall a static scan never sees.
Before and after shown in the demo. Would love feedback.
Project + video linked on the submission.


================================================================================
POSTING ORDER (after YouTube upload + URL injected)
================================================================================
1. Upload video to YouTube -> copy URL -> replace YOUTUBE_URL everywhere above.
2. Submit Builder Center PROJECT (SUBMIT-01) + POST (SUBMIT-02).
3. Publish Dev.to (canonical_url set).
4. LinkedIn: post the body, then immediately add the first comment with the 3 links.
5. X: post the 5-tweet thread.
6. YouTube community post.
7. (Optional) Builder Center discussion tab note.
