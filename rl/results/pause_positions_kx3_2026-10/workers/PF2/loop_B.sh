#!/bin/bash
export O=/mnt/session/outputs D=/mnt/session/outputs/PF2 P=rl/results/pause_games_new_2026-10-12 PG=/root/pg_B/target/release/examples/pg_pos BOT=kx3
cd /root/pf2clone
DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
mkdir -p $D/runs_B
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
n=0; total=32
while read -r id; do
  [ -n "$id" ] || continue
  n=$((n+1))
  if [ -f $D/runs_B/out_$id.jsonl ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then continue; fi
  echo "$id start $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
  { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $BOT --only $id > $D/runs_B/out_$id.jsonl 2> $D/runs_B/err_$id.txt ; } 2>> $D/runs_B/TIMING.txt
  rc=$?
  echo "$id end $(date -u +%FT%TZ) exit $rc" >> $D/runs_B/TIMING.txt
  if [ $rc = 0 ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "$(date -u +%FT%TZ) PF2: position $n of $total done" >> $D/STATUS.txt
  else
    echo "$(date -u +%FT%TZ) PF2: STOP: position $id exit $rc lines $(grep -c . $D/runs_B/out_$id.jsonl 2>/dev/null)" >> $D/STATUS.txt
    tar -C $O -cf $O/PF2_checkpoint.tar PF2/
    exit 1
  fi
  tar -C $O -cf $O/PF2_checkpoint.tar PF2/
done < /root/pf2clone/rl/results/pause_positions_kx3_2026-10/shards/S2.txt
echo "LOOP_END $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
