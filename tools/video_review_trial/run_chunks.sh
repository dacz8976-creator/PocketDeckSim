#!/bin/bash
# Video review trial, chunked: the recording is cut into 54-s pieces (3 overview sheets), one small transcription job per
# piece (named files, no folder listing needed), then Sonnet merges the pieces into the review, Opus checks, Opus compares
# with Codex. usage: run_chunks.sh <gN> <arm dir name> <piece model> <piece cap USD> <codex packet dir, WSL path>
export PATH="$HOME/.local/bin:$PATH"
eval "$(grep '^export ANTHROPIC_API_KEY=' ~/.bashrc | tail -1)"
G=/home/dacz8976/video_trial/$1; ARM=$2; PM=$3; PCAP=$4; CODEX="$5"
A=$G/$ARM; B=/home/dacz8976/video_trial/briefs; LOG=$G/trial_chunks.log
mkdir -p "$A/out_segments"
[ -d "$A/frames" ] || cp -al "$G/frames" "$A/frames"
cost() {  # name, json
  python3 - "$1" "$2" >> "$A/costs.jsonl" <<'EOF'
import json, sys
name, f = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(f))
    print(json.dumps({"job": name, "cost_usd": d.get("total_cost_usd"), "ms": d.get("duration_ms"), "turns": d.get("num_turns"), "is_error": d.get("is_error")}))
except Exception as e:
    print(json.dumps({"job": name, "error": str(e)}))
EOF
}
run() {  # name, prompt file, out dir, model, cap
  mkdir -p "$A/$3"
  echo "$(date -u +%FT%TZ) $ARM $1 start ($4, cap $5)" >> "$LOG"
  ( cd "$A" && claude -p "$(cat "$2") Your output folder is $A/$3 ." --bare --restricted --strict-mcp-config \
      --add-dir "$A/$3" --permission-mode acceptEdits --model "$4" --max-budget-usd "$5" \
      --output-format json > "$A/$3/job_$1.json" 2> "$A/$3/job_$1.err" )
  echo "$(date -u +%FT%TZ) $ARM $1 end rc=$?" >> "$LOG"
  cost "$1" "$A/$3/job_$1.json"
}
# render one prompt per piece
mkdir -p "$A/prompts"
python3 - "$A" "$B/BRIEF_SEGMENT.md" <<'EOF'
import os, sys
A, brief = sys.argv[1], open(sys.argv[2]).read()
full = sorted(os.listdir(f'{A}/frames/full')); last = int(full[-1][2:6])
sheets = sorted(os.listdir(f'{A}/frames/sheets'))
start = 0; k = 0
while start <= last:
    end = min(start + 53, last); k += 1
    sh = [s for s in sheets if start <= int(s[11:15]) <= end]
    extra = 'Nothing extra.'
    if start == 0:
        extra = ("This piece is the START of the recording. Also record, from full-resolution frames: the deck name or QR; "
                 "who goes first; each player's Energy Zone type icon; Dustin's opening hand (name every card at the bottom); "
                 "and each side's first Active and Bench.")
    if end == last:
        extra = ("This piece is the END of the recording. Also record, from full-resolution frames: the result screen "
                 "(Victory or Defeat, both players' points), any statistics shown (turns, damage done, card of the game) "
                 "and any rank change.") if start else extra + " It is also the END: record the result screen, statistics and rank change."
    t = (brief.replace('<FROM>', str(start)).replace('<TO4>', f'{end:04d}').replace('<TO>', str(end))
              .replace('<SHEETS>', ', '.join('`frames/sheets/' + s + '`' for s in sh))
              .replace('<PART>', f'{k:02d}').replace('<EXTRA>', extra))
    open(f'{A}/prompts/seg_{k:02d}.md', 'w').write(t)
    open(f'{A}/out_segments/PART_{k:02d}.md', 'w').write('PLACEHOLDER - replace me\n')  # the piece job edits it (some models won't create files)
    start += 54
print(k, 'pieces, last second', last)
EOF
# pieces, 5 at a time
n=0
for p in "$A"/prompts/seg_*.md; do
  k=$(basename "$p" .md)
  run "$k" "$p" out_segments "$PM" "$PCAP" &
  n=$((n+1)); [ $((n % 5)) -eq 0 ] && wait
done
wait
echo "$(date -u +%FT%TZ) $ARM pieces done: $(ls "$A"/out_segments/PART_*.md 2>/dev/null | wc -l) parts" >> "$LOG"
run merge "$B/BRIEF_MERGE.md" out_write claude-sonnet-5-5 10
sed 's#<REVIEW_DIR>#out_write#g' "$B/BRIEF_CHECK1.md" > "$A/prompts/check.md"
run check "$A/prompts/check.md" out_check claude-opus-5-5 15
mkdir -p "$A/codex"
find "$CODEX" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$A/codex/" \;
for sub in independent verification; do
  [ -d "$CODEX/$sub" ] && mkdir -p "$A/codex/$sub" && find "$CODEX/$sub" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$A/codex/$sub/" \;
done
sed 's#<C_DIR>#out_check#g' "$B/BRIEF_COMPARE.md" > "$A/prompts/compare.md"
run compare "$A/prompts/compare.md" out_compare claude-opus-5-5 8
echo "$(date -u +%FT%TZ) $ARM done" >> "$LOG"
