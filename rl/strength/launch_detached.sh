#!/bin/bash
# Start a long laptop run (strength, slow report, floor, screen, or a chain script that runs them) so that it outlives
# the Windows process that started it: a Claude session that ends, an app update, a closed terminal. The run gets its
# own session and process group (setsid), ignores hangups (nohup), has stdin closed, and writes to a log; its pid, group
# and start time go in a pid file, so a later session can find it, check it, or stop it.
#
#   launch_detached.sh start NAME [--dir DIR] -- COMMAND [ARGS...]   start NAME unless it is already running
#   launch_detached.sh status [NAME]                                 running or not, and the log's last line
#   launch_detached.sh stop NAME                                     SIGTERM to the whole group, then wait up to 2 min
#
# Files: $RUNS/NAME.pid and $RUNS/NAME.log, with RUNS=${KX_RUNS_DIR:-$HOME/runs}. --dir is the working directory
# (default: the current one).
# The run itself must be resumable: `strength run` and slow_report.py resume from the games already written, and a
# game cut off by a stop is played again. Keep chain scripts somewhere durable (the repository or $HOME), not in a
# session's scratchpad: the scratchpad belongs to one session.
#
# WSL: this does not keep the Linux VM alive. Something outside the Claude app has to hold WSL open while the run goes
# (on this laptop, the "Pocket Deck Lab WSL On Demand" scheduled task, a hidden `wsl.exe --exec sleep infinity`).
# If the VM shuts down, every run in it stops; start it again with the same command and it resumes.
set -uo pipefail
RUNS=${KX_RUNS_DIR:-$HOME/runs}
mkdir -p "$RUNS"
now() { date -u +%FT%TZ; }
starttime() { awk '{print $22}' "/proc/$1/stat" 2>/dev/null; }   # clock ticks after boot: tells a reused pid apart

# alive NAME: 0 if the run is still going, else 1. Going means the pid file's process is running and is the same process
# (same start time), or, when that leader has died, a process of its group still carries the run's tag (the environment
# variable LAUNCH_DETACHED_RUN, inherited by everything the run starts), so a reused group number is never taken for it.
alive() {
  local f="$RUNS/$1.pid" pid st pgid tag p
  [ -e "$f" ] || return 1
  pid=$(sed -n 's/^pid=//p' "$f"); st=$(sed -n 's/^starttime=//p' "$f")
  pgid=$(sed -n 's/^pgid=//p' "$f"); tag=$(sed -n 's/^tag=//p' "$f")
  [ -n "$pid" ] && [ -d "/proc/$pid" ] && [ "$(starttime "$pid")" = "$st" ] && return 0
  [ -n "$pgid" ] && [ -n "$tag" ] || return 1
  for p in $(pgrep -g "$pgid"); do
    { tr '\0' '\n' < "/proc/$p/environ"; } 2> /dev/null | grep -qx "LAUNCH_DETACHED_RUN=$tag" && return 0
  done
  return 1
}

status_one() {
  local n=$1 f="$RUNS/$1.pid" pid pgid
  pid=$(sed -n 's/^pid=//p' "$f"); pgid=$(sed -n 's/^pgid=//p' "$f")
  if alive "$n"; then
    echo "$n: RUNNING pid $pid group $pgid since $(sed -n 's/^started=//p' "$f") ($(pgrep -g "$pgid" | wc -l) processes)"
  else
    echo "$n: not running (pid $pid, started $(sed -n 's/^started=//p' "$f"))"
  fi
  [ -s "$RUNS/$n.log" ] && echo "  log: $(tail -n 1 "$RUNS/$n.log" | cut -c1-200)"
}

case "${1:-}" in
  start)
    shift; NAME=${1:?"usage: start NAME [--dir DIR] -- COMMAND..."}; shift
    [[ "$NAME" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "NAME may hold only letters, digits, . _ -" >&2; exit 2; }
    DIR=$PWD
    if [ "${1:-}" = "--dir" ]; then DIR=${2:?"--dir needs a directory"}; shift 2; fi
    [ "${1:-}" = "--" ] || { echo "usage: start NAME [--dir DIR] -- COMMAND..." >&2; exit 2; }
    shift; [ $# -ge 1 ] || { echo "no command" >&2; exit 2; }
    if alive "$NAME"; then echo "STOP: $NAME is already running"; status_one "$NAME"; exit 3; fi
    cd "$DIR" || { echo "no directory $DIR" >&2; exit 2; }
    LOG="$RUNS/$NAME.log"
    echo "[$(now)] launch_detached: start $NAME in $DIR: $*" >> "$LOG"
    # Started in the background of a non-interactive shell, the child is not a group leader, so setsid makes it the
    # leader of a new session and group without forking: $! is the run's own pid, and its pid is its group id.
    TAG="$NAME-$(date -u +%s)-$$"
    LAUNCH_DETACHED_RUN="$TAG" setsid nohup "$@" >> "$LOG" 2>&1 < /dev/null &
    PID=$!
    sleep 1
    if [ ! -d "/proc/$PID" ]; then echo "STOP: $NAME ended within a second; see $LOG"; tail -n 5 "$LOG"; exit 4; fi
    PGID=$(ps -o pgid= -p "$PID" | tr -d ' ')
    { echo "name=$NAME"; echo "pid=$PID"; echo "pgid=$PGID"; echo "starttime=$(starttime "$PID")"
      echo "tag=$TAG"; echo "started=$(now)"; echo "dir=$DIR"; echo "cmd=$*"; } > "$RUNS/$NAME.pid"
    status_one "$NAME"
    [ "$PGID" = "$PID" ] || echo "note: the run is in group $PGID, not its own; stop will signal that group"
    ;;
  status)
    shift
    if [ -n "${1:-}" ]; then
      [ -e "$RUNS/$1.pid" ] || { echo "$1: no pid file in $RUNS"; exit 1; }
      status_one "$1"; alive "$1"
    else
      ls "$RUNS"/*.pid > /dev/null 2>&1 || { echo "no runs in $RUNS"; exit 0; }
      for f in "$RUNS"/*.pid; do status_one "$(basename "$f" .pid)"; done
    fi
    ;;
  stop)
    shift; NAME=${1:?"usage: stop NAME"}
    alive "$NAME" || { echo "$NAME is not running"; exit 0; }
    PGID=$(sed -n 's/^pgid=//p' "$RUNS/$NAME.pid")
    echo "[$(now)] launch_detached: stop $NAME (SIGTERM to group $PGID)" >> "$RUNS/$NAME.log"
    kill -TERM -- "-$PGID"
    for _ in $(seq 120); do pgrep -g "$PGID" > /dev/null || break; sleep 1; done
    if pgrep -g "$PGID" > /dev/null; then echo "$NAME: still running after 2 min (group $PGID); nothing more was sent"; exit 5; fi
    echo "$NAME: stopped"
    ;;
  *)
    sed -n '2,19p' "$0"; exit 2 ;;
esac
