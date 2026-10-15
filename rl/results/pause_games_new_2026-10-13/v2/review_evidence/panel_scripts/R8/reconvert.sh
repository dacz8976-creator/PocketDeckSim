#!/bin/bash
# re-run main's converter (HEAD) on the same inputs as v2/scripts/convert.sh, into R8/reconv (read-only on repo and Recording_QA; -B: no bytecode)
set -u
R8=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8
H="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness"
QA="/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"
OUT=$R8/reconv
mkdir -p "$OUT"
G=()
for b in "$QA"/BATCH_2026-10-0[69]_NEW_PAUSE_GAMES "$QA"/BATCH_2026-10-11_NEW_PAUSE_GAMES; do
  for d in "$b"/2026*; do [ -f "$d/TURN_LEDGER.json" ] && G+=("$d"); done
done
for d in "$R8"/norm/2026*; do G+=("$d"); done
echo "games: ${#G[@]}"
cd "$H" && python3 -B "$H/ledger_to_positions.py" "$OUT/positions_all.json" "$OUT/report_convert.json" "${G[@]}" | grep -E "261013|261012_(01|20|21|22|23)|total|FAILED"
