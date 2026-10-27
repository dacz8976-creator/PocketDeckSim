#!/bin/bash
L=/home/dacz8976/k21_run/launcher.log
say() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
say "armed: kit d4877c97eb5eb9fc93c2bf72dd7d31e5e25850b9; nights 2026-10-27 2026-10-28 2026-10-30 2026-10-31 at 02:00Z (never 2026-10-29)"
for D in 2026-10-27 2026-10-28 2026-10-30 2026-10-31; do
  T=$(date -u -d "$D 02:00:00" +%s); NOW=$(date -u +%s)
  [ $NOW -ge $((T + 10 * 3600 + 50 * 60)) ] && { say "$D: that night is over"; continue; }
  [ $NOW -lt $T ] && { say "waiting for $D 02:00Z"; sleep $((T - NOW)); }
  [ -e /home/dacz8976/k21_run/DISARM ] && { say "disarmed (k21_run/DISARM): not starting $D"; exit 0; }
  [ -e /home/dacz8976/k21_run/STOPPED ] && { say "a stop holds: not starting $D"; exit 0; }
  [ -e /home/dacz8976/k21_run/DONE ] && { say "K21 done: nothing more"; exit 0; }
  say "$D: starting run_k21.sh"
  ( cd /home/dacz8976/k21_run && bash /home/dacz8976/k21_run/kit/run_k21.sh ) >> /home/dacz8976/k21_run/run_k21.stdout 2>&1
  say "$D: run_k21.sh exit $?; status $(cat /home/dacz8976/k21_run/STATUS_$D 2>/dev/null)"
done
say "the registered nights are over"
