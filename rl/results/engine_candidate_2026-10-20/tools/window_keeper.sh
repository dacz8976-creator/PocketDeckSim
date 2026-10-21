#!/bin/bash
# Dustin, Oct 20 (via the coordinator): heavy laptop work runs at NIGHT only, about 9 pm to 8 am CT (02:00-13:00Z while CDT lasts).
# This keeper freezes ONLY the candidate-pin drivers' process groups (one file per driver in $W/pgids/) at 12:55Z and thaws
# them at 02:00Z. Other sessions' processes are never touched. A manual hold: touch ~/pincand_work/HOLD (stays frozen, even at
# night); rm it to allow the next thaw. Stop the keeper: touch ~/pincand_work/KEEPER_EXIT.
W=/home/dacz8976/pincand_work
LOG=$W/window_keeper.log
mkdir -p $W/pgids
declare -A state
echo "$(date -u +%FT%TZ) keeper armed (stop 12:55Z, resume 02:00Z; groups in $W/pgids/)" >> "$LOG"
while [ ! -e $W/KEEPER_EXIT ]; do
  m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M)))
  if [ $m -ge 120 ] && [ $m -lt 775 ] && [ ! -e $W/HOLD ]; then want=run; else want=stop; fi   # 02:00Z-12:55Z = night
  for f in $W/pgids/*.pgid; do
    [ -e "$f" ] || continue
    pg=$(cat "$f")
    if ! kill -0 -- -"$pg" 2>/dev/null; then echo "$(date -u +%FT%TZ) group $pg ($(basename $f)) is gone; file removed" >> "$LOG"; rm -f "$f"; continue; fi
    if [ "$want" != "${state[$pg]:-unknown}" ]; then
      if [ $want = stop ]; then kill -STOP -- -"$pg"; else kill -CONT -- -"$pg"; fi
      echo "$(date -u +%FT%TZ) $want group $pg ($(basename $f))" >> "$LOG"
      ps -o pid,stat,etime,comm -g "$pg" >> "$LOG" 2>/dev/null
      state[$pg]=$want
    fi
  done
  sleep 30
done
echo "$(date -u +%FT%TZ) keeper exits (KEEPER_EXIT)" >> "$LOG"
