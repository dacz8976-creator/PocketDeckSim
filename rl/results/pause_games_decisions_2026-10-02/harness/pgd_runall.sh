#!/usr/bin/env bash
# runs every position of positions_A.json with seeds 1..12 at nice 19, two at a time; progress in /home/dacz8976/pgd/runall.log
D=/home/dacz8976/pgd
SEEDS=${1:-1,2,3,4,5,6,7,8,9,10,11,12}
mkdir -p "$D/runs"
IDS=$(python3 -c "import json; print(' '.join(p['id'] for p in json.load(open('$D/positions_A.json'))))")
echo "start $(date -u +%H:%M:%S) seeds=$SEEDS" > "$D/runall.log"
run_one() {
    id=$1
    s=$(date +%s)
    nice -n 19 "$D/pg_pos" --positions "$D/positions_A.json" --deck A="$D/draftA.txt" --seeds "$SEEDS" --only "$id" > "$D/runs/out_$id.jsonl" 2> "$D/runs/err_$id.txt"
    echo "$(date -u +%H:%M:%S) done $id exit $? in $(( $(date +%s) - s )) s" >> "$D/runall.log"
}
export -f run_one; export D SEEDS
printf '%s\n' $IDS | xargs -P 2 -I{} bash -c 'run_one {}'
echo "all done $(date -u +%H:%M:%S)" >> "$D/runall.log"
