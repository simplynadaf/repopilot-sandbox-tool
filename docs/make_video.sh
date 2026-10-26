#!/usr/bin/env bash
# =============================================================================
# make_video.sh — one-shot build of the RepoPilot sandbox demo video.
# Pipeline: synth Polly VO -> record real-UI walkthrough -> mux VO+bed ->
#           concat intro+demo+outro -> loudnorm -> validate.
# Reuses the Oct-23 toolchain (ffmpeg static, chromium-1248, Polly Matthew).
# =============================================================================
set -euo pipefail

PROJ=/home/ec2-user/weekend-hackathon/build/repopilot-sandbox
REC=/home/ec2-user/repopilot-sandbox-rec
VO=$REC/voiceover
DEMO=$REC/demo
CARDS=$REC/cards
FINAL=$REC/final
FFMPEG=/home/ec2-user/.local/bin/ffmpeg
FFPROBE=/home/ec2-user/.local/bin/ffprobe
NODE_MODULES=/home/ec2-user/repopilot-recording/node_modules
REGION=us-east-1
VOICE=Matthew

mkdir -p "$VO" "$DEMO" "$FINAL"

say() { echo ">>> $*"; }

# ---------------------------------------------------------------------------
# 1. Polly VO — one MP3 per segment. Text matches record_demo_v2.js windows.
# ---------------------------------------------------------------------------
synth() {  # synth <name> <text>
  local name="$1" text="$2"
  say "Polly: $name"
  aws polly synthesize-speech --region "$REGION" --engine neural \
    --voice-id "$VOICE" --output-format mp3 \
    --text "$text" "$VO/$name.mp3" >/dev/null
}

synth hook "I already built an agent that reads a GitHub repo and tells you if it is safe to run. The problem was that word. Reads. It judged the repo from the outside, the README, the file list. A book report. So I gave it one new tool, and it stopped guessing."

synth gap "Here is the gap. The dangerous part of a repo is not what you read. It is what runs the second you type N P M install. A postinstall hook fires with your whole environment, your keys, your tokens. A tool that only reads the repo cannot see it. On this sneaky repo the static read scores it, but it is still just reading."

synth payoff "Now the new tool. Run in sandbox clones the repo and actually runs the install inside a disposable A W S CodeBuild container, then reads the real build log. Same repo. And there it is, caught in the live log. The install piped curl straight into bash. A scan of the README would never have seen that. The container is thrown away after the run, so the untrusted code ran in A W S, never on my machine."

synth balance "On a genuinely safe repo it runs the exact same way and comes back clean. Succeeded, nothing dangerous in the log. It is not paranoid. It just checks by running, not by reading."

synth proof "This is one new tool on an agent I already shipped. The reasoning is Amazon Bedrock with Nova Pro through Strands. The new power is a single Strands tool backed by A W S CodeBuild, with a least privilege role. Both runs you just saw were validated against live A W S."

synth close "Point the same tool at any should I run this decision, and it runs it in a disposable box and decides from the real log. Everyone scans the repo. This agent runs it, so your laptop does not. Code and a live demo are in the description."

# measure each VO length (seconds)
dur() { "$FFPROBE" -v quiet -show_entries format=duration -of csv=p=0 "$1"; }
for s in hook gap payoff balance proof close; do printf "   %-8s %.1fs\n" "$s" "$(dur "$VO/$s.mp3")"; done

# ---------------------------------------------------------------------------
# 2. Serve the real UI and record the walkthrough WebM
# ---------------------------------------------------------------------------
say "Serving docs/ on :8099 and recording the real UI"
rm -f "$DEMO"/*.webm 2>/dev/null || true
( cd "$PROJ/docs" && python3 -m http.server 8099 >/tmp/rec8099.log 2>&1 & echo $! > /tmp/rec8099.pid )
sleep 2
NODE_PATH="$NODE_MODULES" node "$PROJ/docs/record_demo_v2.js"
kill "$(cat /tmp/rec8099.pid)" 2>/dev/null || true
DEMO_WEBM=$(ls -t "$DEMO"/*.webm | head -1)
say "recorded: $DEMO_WEBM  ($(dur "$DEMO_WEBM")s)"

# ---------------------------------------------------------------------------
# 3. Build the VO track: place each segment at its window start with adelay,
#    then mix into one stereo track the length of the demo.
#    Window starts (ms) match the recorder holds (see record_demo_v2.js).
# ---------------------------------------------------------------------------
# segment start offsets in seconds (tuned to the recorder timeline)
declare -A AT=( [hook]=1 [gap]=25 [payoff]=52 [balance]=92 [proof]=116 [close]=138 )
DEMO_LEN=$(dur "$DEMO_WEBM")
say "demo length ${DEMO_LEN}s; building VO mix"

# build ffmpeg inputs + filter
INPUTS=(); FILTER=""; IDX=0; MIXN=0; LABELS=""
for s in hook gap payoff balance proof close; do
  INPUTS+=( -i "$VO/$s.mp3" )
  ms=$(( ${AT[$s]} * 1000 ))
  FILTER+="[$IDX:a]adelay=${ms}|${ms}[a$IDX];"
  LABELS+="[a$IDX]"
  IDX=$((IDX+1)); MIXN=$((MIXN+1))
done
FILTER+="${LABELS}amix=inputs=${MIXN}:dropout_transition=0:normalize=0[vo]"

say "synth VO mix -> vo.wav"
"$FFMPEG" -y "${INPUTS[@]}" -filter_complex "$FILTER" -map "[vo]" -t "$DEMO_LEN" "$VO/vo_mix.wav" >/dev/null 2>&1

# ---------------------------------------------------------------------------
# 4. Quiet ambient sine bed, full demo length
# ---------------------------------------------------------------------------
say "ambient bed"
"$FFMPEG" -y -f lavfi -i "sine=frequency=110:sample_rate=44100" -t "$DEMO_LEN" \
  -af "volume=0.035,aeval=val(0)*0.6|val(1)*0.6" "$VO/bed.wav" >/dev/null 2>&1 || \
"$FFMPEG" -y -f lavfi -i "sine=frequency=110:sample_rate=44100" -t "$DEMO_LEN" \
  -af "volume=0.035" "$VO/bed.wav" >/dev/null 2>&1

# ---------------------------------------------------------------------------
# 5. Mux VO + bed onto the demo video; loudnorm to broadcast -16 LUFS
# ---------------------------------------------------------------------------
say "mux demo + VO + bed -> seg_demo.mp4"
"$FFMPEG" -y -i "$DEMO_WEBM" -i "$VO/vo_mix.wav" -i "$VO/bed.wav" \
  -filter_complex "[1:a][2:a]amix=inputs=2:duration=first:weights='1 0.5'[mix];[mix]loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart \
  "$REC/seg_demo.mp4" >/dev/null 2>&1
say "seg_demo.mp4 ($(dur "$REC/seg_demo.mp4")s)"

# ---------------------------------------------------------------------------
# 6. Convert intro/outro cards to mp4 (silent) at matching 1080p/H.264
# ---------------------------------------------------------------------------
INTRO_WEBM=$(ls "$CARDS"/intro/*.webm | head -1)
OUTRO_WEBM=$(ls "$CARDS"/outro/*.webm | head -1)
enc() { "$FFMPEG" -y -i "$1" -f lavfi -i anullsrc=r=44100:cl=stereo -shortest \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -vf "scale=1920:1080,fps=30" \
  -c:a aac -b:a 160k -movflags +faststart "$2" >/dev/null 2>&1; }
say "encode cards"
enc "$INTRO_WEBM" "$REC/seg_intro.mp4"
enc "$OUTRO_WEBM" "$REC/seg_outro.mp4"

# ---------------------------------------------------------------------------
# 7. Concat intro + demo + outro -> final
# ---------------------------------------------------------------------------
say "concat -> final/repopilot-sandbox-demo.mp4"
# Use the concat FILTER (not demuxer): the demo WebM is VFR and the cards are CFR,
# so normalize each to 30fps / 1080p / 48k stereo, then concat v+a in one graph.
"$FFMPEG" -y -i "$REC/seg_intro.mp4" -i "$REC/seg_demo.mp4" -i "$REC/seg_outro.mp4" -filter_complex \
"[0:v]fps=30,scale=1920:1080,setsar=1[v0];[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];\
 [1:v]fps=30,scale=1920:1080,setsar=1[v1];[1:a]aresample=48000,aformat=channel_layouts=stereo[a1];\
 [2:v]fps=30,scale=1920:1080,setsar=1[v2];[2:a]aresample=48000,aformat=channel_layouts=stereo[a2];\
 [v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart \
  "$FINAL/repopilot-sandbox-demo.mp4" >/dev/null 2>&1

cp "$FINAL/repopilot-sandbox-demo.mp4" "$PROJ/docs/demo.mp4"
say "DONE -> $FINAL/repopilot-sandbox-demo.mp4  +  docs/demo.mp4"
echo "final duration: $(dur "$FINAL/repopilot-sandbox-demo.mp4")s"
