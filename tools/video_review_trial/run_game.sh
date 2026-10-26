#!/bin/bash
# Video review trial, one game: Haiku and Sonnet first passes (blind, in parallel) -> one Opus check of both
# -> Opus compare of the checked review with Codex's. Credit-billed (API key), capped per job.
# usage: run_game.sh <gN> <codex packet dir, WSL path>
export PATH="$HOME/.local/bin:$PATH"
eval "$(grep '^export ANTHROPIC_API_KEY=' ~/.bashrc | tail -1)"
G=/home/dacz8976/video_trial/$1
CODEX="$2"
B=/home/dacz8976/video_trial/briefs
LOG=$G/trial.log
cost() {  # job name, json output file
  python3 - "$1" "$2" >> "$G/costs.jsonl" <<'EOF'
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
job() {  # name, brief, out dir, model, budget
  mkdir -p "$G/$3"
  echo "$(date -u +%FT%TZ) $1 start ($4, cap $5)" >> "$LOG"
  ( cd "$G" && claude -p "$(cat "$B/$2") Your output folder is $G/$3 ." --bare --restricted --strict-mcp-config \
      --add-dir "$G/$3" --permission-mode acceptEdits --model "$4" --max-budget-usd "$5" \
      --output-format json > "$G/$3/job.json" 2> "$G/$3/job.err" )
  echo "$(date -u +%FT%TZ) $1 end rc=$?" >> "$LOG"
  cost "$1" "$G/$3/job.json"
}
job review_haiku BRIEF_REVIEW.md out_review_haiku claude-haiku-5-5 6 &
job review_sonnet BRIEF_REVIEW.md out_review_sonnet claude-sonnet-5-5 15 &
wait
job check BRIEF_CHECK.md out_check claude-opus-5-5 15
mkdir -p "$G/codex"
find "$CODEX" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$G/codex/" \;
for sub in independent verification; do  # Codex keeps its independent check in a subfolder
  [ -d "$CODEX/$sub" ] && mkdir -p "$G/codex/$sub" && find "$CODEX/$sub" -maxdepth 1 -type f \( -name '*.md' -o -name '*.json' \) -exec cp {} "$G/codex/$sub/" \;
done
echo "$(date -u +%FT%TZ) codex files copied: $(ls "$G/codex" | wc -l)" >> "$LOG"
job compare BRIEF_COMPARE.md out_compare claude-opus-5-5 8
echo "$(date -u +%FT%TZ) game done" >> "$LOG"
cat "$G/costs.jsonl"
