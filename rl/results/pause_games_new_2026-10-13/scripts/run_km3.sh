#!/bin/bash
# run_km3.sh POSITIONS.json DECKS_DIR RUNS_DIR IDS_FILE [SEEDS]: km3 on the official engine (pg_pos_F of ../../pause_positions_kx3_2026-10/builds/builds.txt, sha256 129b96a7...), one position at a
# time (--only), two at a time, at nice 19, seeds 1-12 as in the Oct 12 read and the kx3 spec. Refuses when a DECKGYM_ variable is set or the binary is not the pinned build.
set -euo pipefail
POS=$1; DECKS=$2; RUNS=$3; IDS=$4; SEEDS=${5:-1,2,3,4,5,6,7,8,9,10,11,12}
BIN=${BIN:-/home/dacz8976/pgx/pg_pos_F}
if env | grep -q '^DECKGYM_'; then echo "a DECKGYM_ variable is set; refusing"; exit 2; fi
# (SKIP_SHA=1 only for the older-engine comparison, which runs the Oct 2 harness build /home/dacz8976/pgd/pg_pos of main-8626a35)
[ -n "${SKIP_SHA:-}" ] || sha256sum "$BIN" | grep -q '^129b96a792f5b1ed20afc365acfd65ef0962f6bd259d2df848deecf4185e96ca' || { echo "$BIN is not pg_pos_F (sha256 129b96a7...); refusing"; exit 3; }
mkdir -p "$RUNS"
DECKARGS=""
for f in "$DECKS"/KW*.txt; do DECKARGS="$DECKARGS --deck $(basename "$f" .txt)=$f"; done
run_one() {
    id=$1
    nice -n 19 "$BIN" --positions "$POS" $DECKARGS --seeds "$SEEDS" --bot km3 --only "$id" > "$RUNS/out_$id.jsonl" 2> "$RUNS/err_$id.txt"
}
export -f run_one; export BIN POS DECKARGS SEEDS RUNS
s=$(date +%s)
grep -v '^$' "$IDS" | xargs -P 2 -I{} bash -c 'run_one {}'
echo "ran $(grep -vc '^$' "$IDS") positions x seeds [$SEEDS] with km3 on $(sha256sum "$BIN" | cut -c1-8) in $(( $(date +%s) - s )) s"
