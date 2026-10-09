#!/bin/bash
# A status line for a long laptop run that needs no Claude session: how many games are written, how many came since the
# last look, when the last one came, and whether the program (and its chain script) is running. With --push the latest
# line of every watched run goes to STATUS.txt on the branch `laptop-status` of origin, so it can be read on GitHub
# (or by the cloud) while the laptop is unattended. Nothing on main is touched: the commit is made with git's plumbing
# (no index, no working tree), so it can't collide with a run's own commits.
#
#   run_watch.sh --name NAME --dir RUN_DIR --total N --pattern REGEX [--chain REGEX] [--stall-min M]
#                [--push] [--every MIN]
#
#   --pattern  pgrep -f pattern of the program that plays the games
#   --chain    pgrep -f pattern of the script that restarts it (optional): a run waiting out the school-morning rule
#              shows "WAITING", not "STOPPED"
#   --stall-min  minutes without a new game while the program runs before the line says STALLED? (default 90)
#   --every    repeat every MIN minutes until all N games are written (one last line is pushed then); without it,
#              look once. Start a repeating watcher with launch_detached.sh so it outlives the session.
#
# Lines also go to $RUNS/NAME.status (latest) and $RUNS/status_history.log, RUNS=${KX_RUNS_DIR:-$HOME/runs}.
# A watcher in WSL stops with the VM: if the branch's newest line is much older than --every, the laptop is down.
set -uo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
RUNS=${KX_RUNS_DIR:-$HOME/runs}
BRANCH=laptop-status
NAME= DIR= TOTAL= PATTERN= CHAIN= STALL=90 PUSH=0 EVERY=0
while [ $# -gt 0 ]; do
  case $1 in
    --name) NAME=$2; shift 2 ;; --dir) DIR=$2; shift 2 ;; --total) TOTAL=$2; shift 2 ;;
    --pattern) PATTERN=$2; shift 2 ;; --chain) CHAIN=$2; shift 2 ;; --stall-min) STALL=$2; shift 2 ;;
    --push) PUSH=1; shift ;; --every) EVERY=$2; shift 2 ;; --repo) REPO=$2; shift 2 ;;
    *) sed -n '2,22p' "$0"; exit 2 ;;
  esac
done
[ -n "$NAME" ] && [ -n "$DIR" ] && [ -n "$TOTAL" ] && [ -n "$PATTERN" ] || { sed -n '2,22p' "$0"; exit 2; }
[[ "$NAME" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "NAME may hold only letters, digits, . _ -" >&2; exit 2; }
case $DIR in /*) ;; *) DIR="$REPO/$DIR" ;; esac
mkdir -p "$RUNS"
STATE="$RUNS/$NAME.watch"
# the first process matching a pattern, leaving out this watcher (its own command line holds the patterns)
find_pid() { local p; for p in $(pgrep -f -- "$1"); do tr '\0' ' ' < "/proc/$p/cmdline" 2> /dev/null | grep -q run_watch.sh || { echo "$p"; return; }; done; }

look() {  # prints the status line and returns 0 when every game is written
  local now=$(date -u +%s) f="$DIR/games.jsonl" n=0 x=0 last=0 prev_n prev_t pid state ago line
  if [ -e "$f" ]; then
    n=$(grep -c '' "$f"); x=$(grep -c '"arm": *"X"' "$f"); last=$(stat -c %Y "$f")
  fi
  { read -r prev_n prev_t < "$STATE"; } 2> /dev/null || { prev_n=$n; prev_t=$now; }
  echo "$n $now" > "$STATE"
  pid=$(find_pid "$PATTERN")
  ago=$(( (now - last) / 60 ))
  if [ "$n" -ge "$TOTAL" ]; then state="DONE"
  elif [ -n "$pid" ] && [ "$last" -gt 0 ] && [ "$ago" -ge "$STALL" ]; then state="STALLED? program running (pid $pid), no new game for $ago min"
  elif [ -n "$pid" ]; then state="RUNNING (pid $pid)"
  elif [ -n "$CHAIN" ] && [ -n "$(find_pid "$CHAIN")" ]; then state="WAITING (the chain is running, the program is not)"
  else state="STOPPED"; fi
  line="$(date -u +%FT%H:%MZ) $NAME: $n of $TOTAL games"
  [ "$x" -gt 0 ] && line="$line ($x kx3)"
  line="$line, +$(( n - prev_n )) in $(( (now - prev_t) / 60 )) min"
  [ "$last" -gt 0 ] && line="$line, last game $(date -u -d "@$last" +%H:%MZ)"
  line="$line; $state"
  echo "$line" | tee "$RUNS/$NAME.status"
  echo "$line" >> "$RUNS/status_history.log"
  [ "$n" -ge "$TOTAL" ]
}

push() {  # STATUS.txt = the latest line of every watched run, committed on $BRANCH without touching main
  local blob tree parent commit body
  body=$(cat "$RUNS"/*.status 2>/dev/null; echo; echo "Written by rl/strength/run_watch.sh on the laptop. If the newest time above is much older than the watcher's interval, the laptop or its WSL is down.")
  blob=$(printf '%s\n' "$body" | git -C "$REPO" hash-object -w --stdin) || return 1
  tree=$(printf '100644 blob %s\tSTATUS.txt\n' "$blob" | git -C "$REPO" mktree) || return 1
  # its own remote ref, not FETCH_HEAD, which a run's own `git fetch` may rewrite at the same moment
  if git -C "$REPO" fetch -q origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH" 2> /dev/null; then
    parent=$(git -C "$REPO" rev-parse "refs/remotes/origin/$BRANCH")
  else
    parent=$(git -C "$REPO" rev-parse -q --verify "refs/heads/$BRANCH")
  fi
  commit=$(git -C "$REPO" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$tree" ${parent:+-p "$parent"} -m "laptop status $(date -u +%FT%H:%MZ)") || return 1
  git -C "$REPO" push -q origin "$commit:refs/heads/$BRANCH" && git -C "$REPO" update-ref "refs/heads/$BRANCH" "$commit" && echo "pushed $BRANCH ${commit:0:8}"
}

while :; do
  look; done_now=$?
  [ "$PUSH" = 1 ] && { push || echo "push failed; will try again next time"; }
  [ "$done_now" = 0 ] || [ "$EVERY" = 0 ] && break
  sleep $(( EVERY * 60 ))
done
exit "$done_now"   # 0 once every game is written
