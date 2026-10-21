#!/bin/bash
cd $HOME/PocketDeckSim
export O=/mnt/session/outputs D=/mnt/session/outputs/PC2 BOT=kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64 PG=$HOME/pg_B/target/release/examples/pg_pos P=rl/results/pause_games_new_2026-10-12
DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
N=$(grep -c . rl/results/pause_positions_kx3_2026-10/shards/S2.txt)
n=0
mkdir -p $D/runs_B
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
while read -r id; do
  [ -n "$id" ] || continue
  n=$((n+1))
  [ -f $D/runs_B/out_$id.jsonl ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ] && continue
  echo "$id start $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
  { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $BOT --only $id > $D/runs_B/out_$id.jsonl 2> $D/runs_B/err_$id.txt ; } 2>> $D/runs_B/TIMING.txt
  rc=$?
  echo "$id end $(date -u +%FT%TZ) exit $rc" >> $D/runs_B/TIMING.txt
  if [ "$rc" = 0 ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "$(date -u +%FT%TZ) PC2: position $n of $N done" >> $D/STATUS.txt
  fi
  tar -C $O -cf $O/PC2_checkpoint.tar PC2/
done < rl/results/pause_positions_kx3_2026-10/shards/S2.txt
echo "$(date -u +%FT%TZ) PC2: loop finished" >> $D/loop_B.done
