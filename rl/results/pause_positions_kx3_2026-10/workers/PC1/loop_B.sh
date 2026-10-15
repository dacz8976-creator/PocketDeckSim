#!/bin/bash
O=/mnt/session/outputs; D=$O/PC1
W=$HOME/pg_B; PG=$W/target/release/examples/pg_pos
R=$HOME/repo_pc1; P=$R/rl/results/pause_games_new_2026-10-12
BOT=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64
DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
export PG P BOT O D
cd $R
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
mkdir -p $D/runs_B
N=$(grep -c . $R/rl/results/pause_positions_kx3_2026-10/shards/S1.txt); n=0
while read -r id; do
  [ -n "$id" ] || continue
  n=$((n+1))
  if [ -f $D/runs_B/out_$id.jsonl ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "position $n of $N done (resume skip $id)" >> $D/STATUS.txt; continue
  fi
  echo "$id start $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
  { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $BOT --only $id > $D/runs_B/out_$id.jsonl 2> $D/runs_B/err_$id.txt ; } 2>> $D/runs_B/TIMING.txt
  rc=$?
  echo "$id end $(date -u +%FT%TZ) exit $rc" >> $D/runs_B/TIMING.txt
  if [ "$rc" = 0 ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "$(date -u +%FT%TZ) PC1: position $n of $N done" >> $D/STATUS.txt
  else
    echo "$(date -u +%FT%TZ) PC1: STOP: position $id exit $rc lines $(grep -c . $D/runs_B/out_$id.jsonl)" >> $D/STATUS.txt
  fi
  tar -C $O -cf $O/PC1_checkpoint.tar PC1/
done < $R/rl/results/pause_positions_kx3_2026-10/shards/S1.txt
echo "LOOP_END $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
