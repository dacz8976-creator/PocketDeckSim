#!/bin/bash
# The whole chain of this folder, from the recordings to the tables (about 6 minutes; km3 at 12 seeds on 92 positions is about a minute). Nothing here runs kx3.
#   1 convert the 14 games (convert.sh)      2 km3 on pg_pos_F, seeds 1-12 (run_km3.sh)       3 the table of his line v km3 (kw_report.py of the Oct 12 harness)
#   4 km3 step by step along his line (forced_runs.py)     5 km3 on the older engine for the positions flagged for rules switch 2     6 the position cards (position_cards.py) and the table (make_table.py)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(dirname "$HERE")
H=$OUT/../pause_games_new_2026-10-12/harness
QA=${QA:-"/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"}
cd "$OUT"
bash "$HERE/convert.sh"
python3 -c "import json; print('\n'.join(p['id'] for p in json.load(open('positions_all.json'))))" > run_ids.txt
rm -rf runs_km3 runs_forced runs_km3_older_engine
bash "$HERE/run_km3.sh" positions_all.json decks runs_km3 run_ids.txt
python3 -B "$H/kw_report.py" positions_all.json runs_km3 km3 km3 games_meta.json > report_out.txt
python3 -B "$HERE/forced_runs.py" positions_all.json decks runs_forced
python3 - <<'EOF'
import csv
rows = list(csv.DictReader(open('position_list.tsv', encoding='utf-8'), delimiter='\t'))
open('run_ids_switch2.txt', 'w').write('\n'.join(r['position_id'] for r in rows if r['switch2_flag'] != 'no') + '\n')
EOF
if [ -x /home/dacz8976/pgd/pg_pos ]; then
  BIN=/home/dacz8976/pgd/pg_pos SKIP_SHA=1 bash "$HERE/run_km3.sh" positions_all.json decks runs_km3_older_engine run_ids_switch2.txt
fi
python3 -B "$HERE/check_deck_assumption.py" positions_all.json decks "$QA" > deck_assumption_check.txt
python3 -B "$HERE/position_cards.py" positions_all.json km3_summary.json runs_km3 position_list.json "$QA" > position_cards.txt
python3 -B "$HERE/make_table.py"
echo done
