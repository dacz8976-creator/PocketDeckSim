#!/bin/bash
export PG=/root/pg_C/target/release/examples/pg_pos
export P=rl/results/pause_games_new_2026-10-13/v2
export O=/mnt/session/outputs
export D=/mnt/session/outputs/P8
export BOT=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64
DECKARGS=(); for f in $P/decks/*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$P/decks/$(basename $f)"); done
cd /root/PocketDeckSim
mkdir -p $D/runs_C
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
n=0; N=8
while read -r id; do
  [ -n "$id" ] || continue
  if [ -f $D/runs_C/out_$id.jsonl ] && [ "$(grep -c . $D/runs_C/out_$id.jsonl)" = 13 ]; then n=$((n+1)); continue; fi
  echo "$id start $(date -u +%FT%TZ)" >> $D/runs_C/TIMING.txt
  { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $BOT --only $id > $D/runs_C/out_$id.jsonl 2> $D/runs_C/err_$id.txt ; } 2>> $D/runs_C/TIMING.txt
  rc=$?
  echo "$id end $(date -u +%FT%TZ) exit $rc" >> $D/runs_C/TIMING.txt
  tar -C $O -cf $O/P8_checkpoint.tar P8/
  if [ $rc = 0 ] && [ "$(grep -c . $D/runs_C/out_$id.jsonl)" = 13 ]; then n=$((n+1)); echo "$(date -u +%FT%TZ) P8: $n of $N positions done (C)" >> $D/STATUS.txt; fi
done < rl/results/pause_positions_kx3_2026-10/shards/S8.txt
echo "$(date -u +%FT%TZ) P8: C loop script finished" >> $D/loop_C.done
