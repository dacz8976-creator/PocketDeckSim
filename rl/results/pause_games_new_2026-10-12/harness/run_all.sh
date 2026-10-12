#!/bin/bash
# run_kw.sh BOT [SEEDS]: the 13 Kingdra ex / Weezing ex positions with pilot BOT (pg_pos of the Oct 2 harness, engine main-8626a35), 2 positions at a time at nice 19
set -euo pipefail
D=/home/dacz8976/pgd
V=${V:-/home/dacz8976/pgd_vr/all}
BOT=$1
SEEDS=${2:-1,2,3,4,5,6,7,8,9,10,11,12}
if env | grep -q '^DECKGYM_'; then echo "a DECKGYM_ variable is set; refusing"; exit 2; fi
RUNS=$V/runs_$BOT
mkdir -p $RUNS
IDS=$(python3 -c "import json; print(' '.join(p['id'] for p in json.load(open('$V/positions_all.json'))))")
DECKARGS=""
for f in $V/KW*.txt; do DECKARGS="$DECKARGS --deck $(basename $f .txt)=$f"; done
run_one() {
    id=$1
    nice -n 19 $D/pg_pos --positions $V/positions_all.json $DECKARGS --seeds "$SEEDS" --bot "$BOT" --only "$id" > "$RUNS/out_$id.jsonl" 2> "$RUNS/err_$id.txt"
}
export -f run_one; export D V SEEDS BOT RUNS DECKARGS
s=$(date +%s)
printf '%s\n' $IDS | xargs -P 2 -I{} bash -c 'run_one {}'
echo "ran $(echo $IDS | wc -w) positions x seeds [$SEEDS] with $BOT in $(( $(date +%s) - s )) s"