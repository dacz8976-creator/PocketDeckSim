#!/bin/bash
# The laptop session's watcher (not part of the night job): returns when tonight's K21 job reaches a point the coordinator must hear about:
# the launch line committed (gates passed, rows starting), a stop, a skip, or the end. Prints the status lines only (no result numbers).
#   bash watch_k21.sh [launch|night]   launch: return at the launch line or any end of night 1; night: return at the end of the night
K=/home/dacz8976/k21_run
WHAT=${1:-launch}
M=$K/.watch_since_$$; touch "$M"   # only a status written after the watcher started counts
while :; do
  for s in "$K"/STATUS_*; do
    [ -e "$s" ] || continue
    [ "$s" -nt "$M" ] || continue
    echo "$(basename "$s"): $(cat "$s")"; tail -n 8 "$K/launcher.log"; tail -n 12 "$K/night_${s##*STATUS_}.log" 2>/dev/null | cut -c1-300
    exit 0
  done
  if [ "$WHAT" = launch ] && [ -e "$K/launch/COMMIT" ]; then
    echo "LAUNCHED: $(cat "$K/launch/COMMIT")"; cat "$K/gates.out" | cut -c1-400; tail -n 6 "$K"/night_*.log | cut -c1-300
    exit 0
  fi
  tmux has-session -t k21 2>/dev/null || { echo "the k21 tmux session is gone"; tail -n 8 "$K/launcher.log"; exit 0; }
  sleep 120
done
