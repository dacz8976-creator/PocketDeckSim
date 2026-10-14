export O=/mnt/session/outputs D=/mnt/session/outputs/PF4 W=$HOME/pg_B P=rl/results/pause_games_new_2026-10-12 BOT=kx3
export PG=$W/target/release/examples/pg_pos
cd $HOME/PF4_clone
DECKARGS=(); for f in $P/decks/KW*.txt; do DECKARGS+=(--deck "$(basename $f .txt)=$f"); done
N=$(grep -c . rl/results/pause_positions_kx3_2026-10/shards/S4.txt); i=0
mkdir -p $D/runs_B
TIMEFORMAT='elapsed %R s, user %U s, sys %S s'
while read -r id; do
  [ -n "$id" ] || continue
  i=$((i+1))
  if [ -f $D/runs_B/out_$id.jsonl ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then
    echo "position $i of $N done (resume skip)" >> $D/STATUS.txt; continue
  fi
  echo "$id start $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
  { time $PG --positions $P/positions_all.json "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $BOT --only $id > $D/runs_B/out_$id.jsonl 2> $D/runs_B/err_$id.txt ; } 2>> $D/runs_B/TIMING.txt
  rc=$?
  echo "$id end $(date -u +%FT%TZ) exit $rc" >> $D/runs_B/TIMING.txt
  if [ $rc = 0 ] && [ "$(grep -c . $D/runs_B/out_$id.jsonl)" = 13 ]; then echo "$(date -u +%FT%TZ) PF4: position $i of $N done" >> $D/STATUS.txt; fi
  tar -C $O -cf $O/PF4_checkpoint.tar PF4/
done < rl/results/pause_positions_kx3_2026-10/shards/S4.txt
echo "LOOP_FINISHED $(date -u +%FT%TZ)" >> $D/runs_B/TIMING.txt
