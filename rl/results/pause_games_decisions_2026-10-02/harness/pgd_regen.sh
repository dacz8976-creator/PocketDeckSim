#!/usr/bin/env bash
# regenerate the position file and rerun every position (12 seeds) -- a few seconds
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/pgd
python3 "$HERE/positions_A.py" "$D/positions_A.json" || exit 1
rm -f "$D/runs"/out_*.jsonl "$D/runs"/err_*.txt
bash "$HERE/pgd_runall.sh" "$@"
tail -3 "$D/runall.log"
python3 "$HERE/pgd_problems.py" | grep -v "problems: \[\]" || echo "no position problems"
