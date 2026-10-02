#!/usr/bin/env bash
# The positions as a test set: any pilot code in, its choice at each of Dustin's decision points out.
#   run_pilot.sh BOT [SEEDS] [PG_POS_BINARY]
# Runs every position of positions_A.json that is not held out with the pilot code BOT (a code `parse_player_code` knows, e.g. km3, kog3, or an
# experimental pilot's code in a harness built from that pilot's engine, see pgd_build.sh) at nice 19, two positions at a time, then writes
#   /home/dacz8976/pgd/runs_<BOT>/   raw stdout JSON lines and PGSTEP/PGDUMP root scores (the dump exists for expectiminimax-based pilots)
#   /home/dacz8976/pgd/report_<BOT>/ TABLES.md (a table per game, with the milestone tags), TURBO_SHARK.md, summary.json, totals.json
# The held-out positions (a quarter of the games, chosen by a fixed hash of the game id; positions_heldout.json) are skipped while that file says
# locked: true. Add positions by extending positions_A.py (a position names a deck key; --deck KEY=file supplies the list; this script passes A=draftA.txt).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/pgd
BOT=$1
SEEDS=${2:-1,2,3,4,5,6,7,8,9,10,11,12}
BIN=${3:-$D/pg_pos}
RUNS=$D/runs_$BOT
OUT=$D/report_$BOT
mkdir -p "$RUNS" "$OUT"
python3 "$HERE/filter_positions.py" "$D/positions_A.json" "$D/positions_heldout.json" ${INCLUDE_HELDOUT:+--include-heldout} > "$RUNS/positions_run.json"
IDS=$(python3 -c "import json; print(' '.join(p['id'] for p in json.load(open('$RUNS/positions_run.json'))))")
run_one() {
    id=$1
    nice -n 19 "$BIN" --positions "$RUNS/positions_run.json" --deck A="$D/draftA.txt" --deck D03="$D/deck03.txt" --seeds "$SEEDS" --bot "$BOT" --only "$id" > "$RUNS/out_$id.jsonl" 2> "$RUNS/err_$id.txt"
}
export -f run_one; export D SEEDS BIN BOT RUNS
s=$(date +%s)
printf '%s\n' $IDS | xargs -P 2 -I{} bash -c 'run_one {}'
echo "ran $(echo $IDS | wc -w) positions x seeds [$SEEDS] with $BOT in $(( $(date +%s) - s )) s"
PGD_POSITIONS=$RUNS/positions_run.json PGD_RUNS=$RUNS python3 "$HERE/pgd_report.py" "$OUT" > "$OUT/report_stdout.txt"
PGD_POSITIONS=$RUNS/positions_run.json PGD_RUNS=$RUNS python3 "$HERE/pgd_ts.py" "$OUT" > /dev/null || echo "(no Turbo Shark tables: that pilot printed no root scores)"
tail -30 "$OUT/report_stdout.txt"
