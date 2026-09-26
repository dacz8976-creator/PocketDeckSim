#!/usr/bin/env bash
# Queue (Sept 26): the two gauntlet runs start only after the laptop's rules/09 fix replays end (the replays are the
# critical path; Dustin's call). Waits on the replay's PID (never pgrep -f), then requires the replay log's anchored
# "LAPTOP REPLAY DONE" line; if the replays failed, nothing starts. Then (a), then (b), each with its own STATUS file.
# Usage (in WSL): nohup setsid bash queue_after_replays.sh <replay pid> > ~/gauntlet_queue.log 2>&1 &
set -uo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/gauntlet_runs_2026-09-26"
T="$R/rl/results/rules09_fixes_2026-09-26/timing_laptop.txt"
PID="$1"
echo "$(date -u +%FT%TZ) queue: waiting for replay pid $PID"
while kill -0 "$PID" 2>/dev/null; do sleep 30; done
grep -Eq '^[0-9-]+ [0-9:]+ LAPTOP REPLAY DONE$' "$T" || { echo "$(date -u +%FT%TZ) QUEUE STOPPED: replays did not finish cleanly"; exit 1; }
echo "$(date -u +%FT%TZ) queue: replays done; starting (a)"
bash "$D/run_gauntlet_new.sh"; echo "$(date -u +%FT%TZ) queue: (a) exited $?; $(tail -1 "$D/STATUS_new.txt" 2>/dev/null)"
bash "$D/run_gauntlet_variation.sh"; echo "$(date -u +%FT%TZ) queue: (b) exited $?; $(tail -1 "$D/STATUS_variation.txt" 2>/dev/null)"
echo "$(date -u +%F\ %T) QUEUE DONE"
