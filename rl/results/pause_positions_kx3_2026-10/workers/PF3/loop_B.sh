#!/bin/bash
O=/mnt/session/outputs; D=$O/PF3
W=$HOME/pg_B; PG=$W/target/release/examples/pg_pos
REPO=$HOME/repo_pf3; cd $REPO
P=rl/results/pause_games_new_2026-10-12; BOT=kx3
DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
N=$(grep -c . rl/results/pause_positions_kx3_2026-10/shards/S3.txt)
mkdir -p $D/runs_B
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
n=0
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
  if [ $rc = 0 ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "$(date -u +%FT%TZ) PF3: position $n of $N done" >> $D/STATUS.txt
  fi
  tar -C $O -cf $O/PF3_checkpoint.tar PF3/
done < $REPO/rl/results/pause_positions_kx3_2026-10/shards/S3.txt
echo "$(date -u +%FT%TZ) PF3: loop finished" >> $D/loop_B.done.txt
