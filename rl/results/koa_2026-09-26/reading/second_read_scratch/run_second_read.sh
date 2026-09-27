#!/usr/bin/env bash
# Second reader's recomputation of koa's reading. Reads files only; plays no games.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
S="$R/rl/results/koa_2026-09-26/reading/second_read_scratch"
RD="$R/rl/results/koa_2026-09-26/reading"
KPF="$R/rl/results/kpf_2026-09-26/reading"
SB="$R/rl/results/scoreboard_v2_2026-09-25"
cd "$S"
python3 second_read.py > "$S/second_read_output.txt" 2>&1; echo "second_read exit $?" >> "$S/second_read_output.txt"
python3 "$R/rl/results/table_readings_2026-09-24/score.py" --rules v2 \
  --limitless "$SB/limitless_v2_dev.json" \
  --old-games "$KPF/table_kp3.jsonl" --new-games "$RD/table_koa3.jsonl" \
  --mixed "$RD/mixed_koa3_first.jsonl" "$RD/mixed_koa3_second.jsonl" \
  --old kp3 --new koa3 > "$S/score28_noevents.txt" 2>&1; echo "score noevents exit $?" >> "$S/score28_noevents.txt"
python3 "$R/rl/results/table_readings_2026-09-24/score.py" --rules v2 \
  --limitless "$SB/limitless_v2_dev.json" --limitless-events "$SB/limitless_v2_dev_events.json" \
  --old-games "$KPF/table_kp3.jsonl" --new-games "$RD/table_koa3.jsonl" \
  --mixed "$RD/mixed_koa3_first.jsonl" "$RD/mixed_koa3_second.jsonl" \
  --old kp3 --new koa3 > "$S/score28_events.txt" 2>&1; echo "score events exit $?" >> "$S/score28_events.txt"
cd "$R"
for c in "B2b 040" "B1 196" "B1 184"; do python3 lib/card.py "$c" 2>&1 | head -3; done > "$S/cards.txt"
sha256sum "$R/rl/engine-2026-09-27/legality_scan" >> "$S/cards.txt"
