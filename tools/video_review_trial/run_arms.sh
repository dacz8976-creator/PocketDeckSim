#!/bin/bash
# Video review trial, games 2+: two arms in separate folders (hard-linked frames), so neither sees the other's work.
#   arm S: Sonnet review -> Opus check -> Opus compare with Codex
#   arm T: Haiku transcript -> Sonnet writes the review from it -> Opus check -> Opus compare with Codex
# usage: run_arms.sh <gN> <codex packet dir, WSL path>
export PATH="$HOME/.local/bin:$PATH"
eval "$(grep '^export ANTHROPIC_API_KEY=' ~/.bashrc | tail -1)"
G=/home/dacz8976/video_trial/$1
CODEX="$2"
B=/home/dacz8976/video_trial/briefs
LOG=$G/trial.log
for a in arm_s arm_t; do
  mkdir -p "$G/$a"
  [ -d "$G/$a/frames" ] || cp -al "$G/frames" "$G/$a/frames"
done
cost() {  # arm dir, job name, json output file
  python3 - "$2" "$3" >> "$1/costs.jsonl" <<'EOF'
import json, sys
name, f = sys.argv[1], sys.argv[2]
try:
    d = json.load(open(f))
    print(json.dumps({"job": name, "cost_usd": d.get("total_cost_usd"), "ms": d.get("duration_ms"), "turns": d.get("num_turns"),
                      "is_error": d.get("is_error"), "subtype": d.get("subtype")}))
except Exception as e:
    print(json.dumps({"job": name, "error": str(e)}))
EOF
}
job() {  # arm, name, brief, out dir, model, budget, sed expression for the brief
  A="$G/$1"; mkdir -p "$A/$4"
  echo "$(date -u +%FT%TZ) $1 $2 start ($5, cap $6)" >> "$LOG"
  ( cd "$A" && claude -p "$(sed "$7" "$B/$3") Your output folder is $A/$4 ." --bare --restricted --strict-mcp-config \
      --add-dir "$A/$4" --permission-mode acceptEdits --model "$5" --max-budget-usd "$6" \
      --output-format json > "$A/$4/job.json" 2> "$A/$4/job.err" )
  echo "$(date -u +%FT%TZ) $1 $2 end rc=$?" >> "$LOG"
  cost "$A" "$2" "$A/$4/job.json"
}
codex_in() {  # arm
  mkdir -p "$G/$1/codex"
  find "$CODEX" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$G/$1/codex/" \;
  for sub in independent verification; do
    [ -d "$CODEX/$sub" ] && mkdir -p "$G/$1/codex/$sub" && find "$CODEX/$sub" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$G/$1/codex/$sub/" \;
  done
}
arm_s() {
  job arm_s review_sonnet BRIEF_REVIEW.md out_review claude-sonnet-5-5 15 's/x/x/'
  job arm_s check BRIEF_CHECK1.md out_check claude-opus-5-5 15 's#<REVIEW_DIR>#out_review#g'
  codex_in arm_s
  job arm_s compare BRIEF_COMPARE.md out_compare claude-opus-5-5 8 's#<C_DIR>#out_check#g'
}
arm_t() {
  job arm_t transcribe_haiku BRIEF_TRANSCRIBE.md out_transcribe claude-haiku-5-5 6 's/x/x/'
  job arm_t write_sonnet BRIEF_WRITE.md out_write claude-sonnet-5-5 10 's/x/x/'
  job arm_t check BRIEF_CHECK1.md out_check claude-opus-5-5 15 's#<REVIEW_DIR>#out_write#g'
  codex_in arm_t
  job arm_t compare BRIEF_COMPARE.md out_compare claude-opus-5-5 8 's#<C_DIR>#out_check#g'
}
arm_s & arm_t & wait
echo "$(date -u +%FT%TZ) game done" >> "$LOG"
