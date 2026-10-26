================================================================================
YOUTUBE METADATA  (paste when uploading; add the real URL back into the other files)
================================================================================

------------------------------------------------------------------- TITLE (<=100)
My AI agent ran a malicious repo in an AWS sandbox and caught the curl | bash

Alt A/B title (first-person, keyword-front):
I gave my AI agent one new tool: an AWS sandbox that runs the repo so your laptop doesn't

--------------------------------------------------------------------------- VISIBILITY
Unlisted or Public. If asked about altered/synthetic content: YES, synthetic voice
(Amazon Polly). The footage is a real screen recording; only the narration is AI.

------------------------------------------------------------------- DESCRIPTION
🧪 My AI agent used to judge a GitHub repo by reading it. I gave it one new tool and now it
actually runs the install inside a disposable AWS CodeBuild sandbox, reads the real build
log, and catches the postinstall hook a static scan never sees.

⚠️ The dangerous moment is not when you read a repo. It is the second you run npm install, when
a postinstall hook fires with your whole environment: your keys, your tokens.

🎚️ Before (reads it): "Looks fine."
✅ After (runs it): "Caught it, the install piped curl | bash into a shell."
Same agent, same repo, one new tool.

🏗️ Built for the AWS Builder Center Weekend Challenge: Give your Agent a Tool.
🧠 The agent reasons with Amazon Bedrock (Nova Pro) through the Strands Agents SDK.
☁️ The new tool is backed by AWS CodeBuild with a least-privilege role.
🔒 The container is thrown away after every run, so the untrusted code runs in AWS, never on
your laptop. Both runs shown were validated against live AWS.

🔗 Links
🖥️ Live demo (the real UI, static replay): https://simplynadaf.github.io/repopilot-sandbox-tool/
💻 Code (repo): https://github.com/simplynadaf/repopilot-sandbox-tool

⏱️ Chapters:
0:00 Intro
0:07 The agent that only reads the repo
0:31 The gap: what runs when you npm install
0:58 The new tool runs it in a disposable AWS sandbox
1:38 A genuinely safe repo, verified
2:02 It is real: the original agent + live AWS
2:18 Close

🙋 Follow me:
🌐 Portfolio: https://sarvarnadaf.com
🐙 GitHub: https://github.com/simplynadaf
💼 LinkedIn: https://www.linkedin.com/in/sarvar04/
✍️ Dev.to: https://dev.to/sarvar_04
🛠️ AWS Builder Center: https://builder.aws.com/community/@sarvar
❎ X: https://x.com/SarvarN_04

🎙️ Narration uses a synthetic voice (Amazon Polly). The screen recording is real.

#awsagents #awsbuilder #aicoding #codebuild #bedrock #supplychainsecurity #strands

--------------------------------------------------------------------------- TAGS
AWS agents, give your agent a tool, AWS Builder Center, AWS CodeBuild, Amazon Bedrock,
Nova Pro, Strands agents, AI agent tool, supply chain security, npm install security,
postinstall attack, disposable sandbox, AI DevOps, agentic AI, repo security

--------------------------------------------------------------------------- THUMBNAIL
Upload docs/thumbnail.png  (1280x720, "Stop scanning. Run it." + before/after chips)

--------------------------------------------------------------------------- MUSIC / AUDIO
Narration: Amazon Polly (Matthew, neural). Ambient bed: original quiet sine drone
(no NCS attribution needed since the bed is self-generated). Loudness normalized I=-16.
