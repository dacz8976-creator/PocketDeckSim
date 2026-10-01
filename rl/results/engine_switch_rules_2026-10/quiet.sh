#!/usr/bin/env bash
# Pause, resume or stop sitting1.sh (../engine_switch_2026-09-30/quiet.sh, adapted). sitting1.sh runs as its own process
# group (it re-executes itself under setsid when it is not a group leader) and writes to .sitting1.pgid here its group
# id, the time and the leader's start time (field 22 of /proc/<pid>/stat). This acts on that one group only:
# sitting1.sh, its watchdog and its nice'd legality_scan / deckgym / floor.py / cargo children, nothing else. The group
# counts as the run only while its leader has that recorded start time (a reused pid never matches) and still leads its
# group. No process search by name.
#   pause   SIGSTOP to the group (quiet hours). Nothing in the sitting is timed except the deadline: a pause past it
#           makes the next step boundary pause the sitting, and the watchdog's hard stop still applies once resumed.
#   resume  SIGCONT to the group.
#   stop    the way to stop a run: SIGTERM to the whole group, then SIGCONT (a paused group gets the TERM too). The record
#           says SITTING 1 STOPPED (committed and pushed, best effort) and a plain restart resumes at the step it was
#           in, reusing that step's complete game files.
#   pause and stop first wait (at most 60 s) while the run is inside a checkpoint (.sitting1.ckpt here: its commit and
#   push), as the watchdog does, so no git lock is held through a pause and a stop lands between git steps.
#   status  the group's members.
# Usage (WSL): bash quiet.sh pause | resume | stop | status        Log: quiet.log here.
set -euo pipefail
O=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$O/quiet.log"; }
[ -s "$O/.sitting1.pgid" ] || { echo "no .sitting1.pgid: sitting1.sh has not started here"; exit 1; }
read -r G _ ST _ < "$O/.sitting1.pgid" || true
[[ $G =~ ^[0-9]+$ ]] || { echo ".sitting1.pgid does not hold a process group id"; exit 1; }
[[ ${ST:-} =~ ^[0-9]+$ ]] || { echo ".sitting1.pgid does not hold the leader's start time"; exit 1; }
alive() {  # the group leader is the sitting1.sh that wrote .sitting1.pgid (same pid and start time) and still leads its group
  local s c; local -a f
  s=$(cat "/proc/$G/stat" 2> /dev/null) || return 1
  s=${s##*) }; read -r -a f <<< "$s"
  [ "${f[19]:-}" = "$ST" ] && [ "${f[2]:-}" = "$G" ] || return 1
  c=$(tr '\0' ' ' < "/proc/$G/cmdline" 2> /dev/null) || return 1
  [[ $c == *sitting1.sh* ]]
}
members() { ps -eo pid=,pgid=,stat=,comm= | awk -v g="$G" '$2 == g {printf "%s(%s,%s) ", $4, $1, $3}'; }
ckpt_wait() {  # at most 60 s while sitting1.sh is inside a checkpoint (its commit and push)
  local i
  for i in $(seq 1 60); do [ -e "$O/.sitting1.ckpt" ] || return 0; [ "$i" != 1 ] || echo "inside a checkpoint: waiting (at most 60 s)"; sleep 1; done
  log "still inside a checkpoint after 60 s; going ahead"
}
case ${1:-} in
  pause)  alive || { echo "process group $G is not the running sitting1.sh; nothing paused"; exit 1; }
          ckpt_wait; kill -STOP -- "-$G"; log "paused process group $G: $(members)";;
  resume) alive || { echo "process group $G is not the running sitting1.sh; nothing to resume"; exit 1; }
          kill -CONT -- "-$G"; log "resumed process group $G: $(members)";;
  stop)   alive || { echo "process group $G is not the running sitting1.sh; nothing to stop"; exit 1; }
          ckpt_wait; kill -TERM -- "-$G"; kill -CONT -- "-$G" 2> /dev/null || true
          log "sent TERM (and CONT) to process group $G; left a moment later: $(sleep 2; members)";;
  status) if alive; then echo "sitting1.sh group $G: $(members)"; else echo "sitting1.sh group $G is not running; members left: $(members)"; fi;;
  *) echo "usage: bash quiet.sh pause|resume|stop|status"; exit 1;;
esac
