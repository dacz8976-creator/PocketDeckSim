#!/usr/bin/env bash
# Quiet hours for the preparation run (Dustin: heavy laptop work pauses during class and travel, for the fans).
# prepare.sh runs as its own process group (it re-executes itself under setsid when it is not a group leader) and
# writes to .prepare.pgid here its group id, the time and the leader's start time (field 22 of /proc/<pid>/stat).
# This acts on that one group only: prepare.sh and its nice'd legality_scan / deckgym / cargo children, nothing else.
# The group counts as the run only while its leader has that recorded start time (a reused pid never matches) and
# still leads its group. No process search by name.
#   pause   SIGSTOP to the group. A paused run keeps its place; no step of the preparation is timed, so a pause changes
#           no result.
#   resume  SIGCONT to the group.
#   stop    the way to stop a run: SIGTERM to the whole group, then SIGCONT (a paused group gets the TERM too). The
#           record says PREPARE STOPPED and a plain restart resumes. A TERM to prepare.sh alone would wait until the
#           current scan ends (bash runs its trap only after the foreground child).
#   status  the group's members.
# The run's lock (.prepare.lock, fd 9) is inherited by its children: an orphaned legality_scan still holds it, so a
# restart cannot race it. After a stop, "status" shows whether anything of the group is left.
# Usage (WSL): bash quiet.sh pause | resume | stop | status        Log: quiet.log here.
set -euo pipefail
O=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$O/quiet.log"; }
[ -s "$O/.prepare.pgid" ] || { echo "no .prepare.pgid: prepare.sh has not started here"; exit 1; }
read -r G _ ST _ < "$O/.prepare.pgid" || true
[[ $G =~ ^[0-9]+$ ]] || { echo ".prepare.pgid does not hold a process group id"; exit 1; }
[[ ${ST:-} =~ ^[0-9]+$ ]] || { echo ".prepare.pgid does not hold the leader's start time (written by an older prepare.sh)"; exit 1; }
alive() {  # the group leader is the prepare.sh that wrote .prepare.pgid (same pid and start time) and still leads its group
  local s c; local -a f
  s=$(cat "/proc/$G/stat" 2> /dev/null) || return 1
  s=${s##*) }; read -r -a f <<< "$s"
  [ "${f[19]:-}" = "$ST" ] && [ "${f[2]:-}" = "$G" ] || return 1
  c=$(tr '\0' ' ' < "/proc/$G/cmdline" 2> /dev/null) || return 1
  [[ $c == *prepare.sh* ]]
}
members() { ps -eo pid=,pgid=,stat=,comm= | awk -v g="$G" '$2 == g {printf "%s(%s,%s) ", $4, $1, $3}'; }
case ${1:-} in
  pause)  alive || { echo "process group $G is not the running prepare.sh; nothing paused"; exit 1; }
          kill -STOP -- "-$G"; log "paused process group $G: $(members)";;
  resume) alive || { echo "process group $G is not the running prepare.sh; nothing to resume"; exit 1; }
          kill -CONT -- "-$G"; log "resumed process group $G: $(members)";;
  stop)   alive || { echo "process group $G is not the running prepare.sh; nothing to stop"; exit 1; }
          kill -TERM -- "-$G"; kill -CONT -- "-$G" 2> /dev/null || true
          log "sent TERM (and CONT) to process group $G; left a moment later: $(sleep 2; members)";;
  status) if alive; then echo "prepare.sh group $G: $(members)"; else echo "prepare.sh group $G is not running; members left: $(members)"; fi;;
  *) echo "usage: bash quiet.sh pause|resume|stop|status"; exit 1;;
esac
