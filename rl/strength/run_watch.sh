#!/bin/bash
# A status line for a long laptop run that needs no Claude session: how many games are written, how many came since the
# last look, when the last one came, and whether the program (and its chain script) is running. With --push the latest
# line of every watched run goes to STATUS.txt on the branch `laptop-status` of origin, so it can be read on GitHub
# (or by the cloud) while the laptop is unattended. Nothing on main is touched: the commit is made with git's plumbing
# (no index, no working tree), so it can't collide with a run's own commits.
#
#   run_watch.sh --name NAME --dir RUN_DIR --total N --pattern REGEX [--chain REGEX] [--stall-min M]
#                [--wait-max M] [--x-label TEXT] [--push] [--every MIN]
#   run_watch.sh --push-only [--body FILE]     push STATUS.txt (FILE, or the latest line of every run) and nothing else
#
#   --pattern  pgrep -f pattern of the program that plays the games
#   --chain    pgrep -f pattern of the script that restarts it (optional): a run waiting out the school-morning rule
#              shows "WAITING", not "STOPPED"; a wait longer than --wait-max (default 900) says WAITING TOO LONG?
#   --stall-min  minutes without a new game (or since the program started) before the line asks whether it is stuck
#              (default 90): LONG GAMES? when the program is busy, STALLED? when it is idle
#   --x-label  what arm X's games are called in the line (default "arm X"; "kx3" for a kx3 run)
#   --every    repeat every MIN minutes until all N games are written (one last line is pushed then); without it,
#              look once. Only for a run that no Windows task watches: one watcher per NAME (they share NAME.watch).
#
# Lines also go to $RUNS/NAME.status (latest) and $RUNS/status_history.log, RUNS=${KX_RUNS_DIR:-$HOME/runs}.
# On the laptop, watch_all.sh (run by a Windows task every 30 minutes) calls this for every run on its list.
set -uo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
RUNS=${KX_RUNS_DIR:-$HOME/runs}
BRANCH=laptop-status
NAME= DIR= TOTAL= PATTERN= CHAIN= STALL=90 WAIT_MAX=900 XLABEL="arm X" PUSH=0 EVERY=0 PUSH_ONLY=0 BODY=
usage() { sed -n '2,22p' "$0"; exit 2; }
while [ $# -gt 0 ]; do
  case $1 in
    --name) NAME=$2; shift 2 ;; --dir) DIR=$2; shift 2 ;; --total) TOTAL=$2; shift 2 ;;
    --pattern) PATTERN=$2; shift 2 ;; --chain) CHAIN=$2; shift 2 ;; --stall-min) STALL=$2; shift 2 ;;
    --wait-max) WAIT_MAX=$2; shift 2 ;; --x-label) XLABEL=$2; shift 2 ;;
    --push) PUSH=1; shift ;; --every) EVERY=$2; shift 2 ;; --repo) REPO=$2; shift 2 ;;
    --push-only) PUSH_ONLY=1; shift ;; --body) BODY=$2; shift 2 ;;
    *) usage ;;
  esac
done
if [ "$PUSH_ONLY" = 0 ]; then
  [ -n "$NAME" ] && [ -n "$DIR" ] && [ -n "$TOTAL" ] && [ -n "$PATTERN" ] || usage
  [[ "$TOTAL" =~ ^[0-9]+$ ]] && [[ "$STALL" =~ ^[0-9]+$ ]] && [[ "$WAIT_MAX" =~ ^[0-9]+$ ]] && [[ "$EVERY" =~ ^[0-9]+$ ]] \
    || { echo "--total, --stall-min, --wait-max and --every take whole numbers" >&2; exit 2; }
  [[ "$NAME" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "NAME may hold only letters, digits, . _ -" >&2; exit 2; }
  case $DIR in /*) ;; *) DIR="$REPO/$DIR" ;; esac
fi
mkdir -p "$RUNS"
STATE="$RUNS/$NAME.watch"
# The first live process matching a pattern, leaving out watchers (their command lines hold the patterns) and a
# pgrep/pkill that happens to be running; a process that ended between pgrep and the read is skipped.
find_pid() {
  local p c
  for p in $(pgrep -f -- "$1"); do
    c=$( { tr '\0' ' ' < "/proc/$p/cmdline"; } 2> /dev/null ) || continue
    case $c in ''|*run_watch.sh*|*watch_all.sh*|pgrep\ *|pkill\ *|*/pgrep\ *|*/pkill\ *) continue ;; esac
    echo "$p"; return
  done
}
# cores a process uses right now: its CPU ticks over 3 seconds (100 ticks = one core-second)
cores_now() {
  local a b
  a=$(awk '{print $14 + $15}' "/proc/$1/stat" 2> /dev/null) || return 1
  sleep 3
  b=$(awk '{print $14 + $15}' "/proc/$1/stat" 2> /dev/null) || return 1
  awk -v d=$(( b - a )) 'BEGIN { printf "%.1f", d / 300 }'
}

look() {  # prints the status line and returns 0 when every game is written
  local now=$(date -u +%s) f="$DIR/games.jsonl" n=0 x=0 last=0 ref prev_n prev_t pid state ago sago cores line
  if [ -e "$f" ]; then
    # complete records only (the harness writes compact JSON with sorted keys, "winner" last): a line cut off by a
    # kill is not a game, and the harness plays that game again
    n=$(grep -cE '"winner":"(deck|opp|tie)"\}$' "$f"); x=$(grep -cE '^\{"arm":"X".*"winner":"(deck|opp|tie)"\}$' "$f")
    last=$(stat -c %Y "$f")
  fi
  { read -r prev_n prev_t < "$STATE"; } 2> /dev/null || { prev_n=$n; prev_t=$now; }
  echo "$n $now" > "$STATE"
  pid=$(find_pid "$PATTERN")
  ago=$(( (now - last) / 60 ))
  ref=$last   # the stall clock starts at the last game or at the program's start, whichever is later
  if [ -n "$pid" ]; then
    local st; st=$(ps -o etimes= -p "$pid" 2> /dev/null | tr -d ' ')
    [[ "$st" =~ ^[0-9]+$ ]] && [ $(( now - st )) -gt "$ref" ] && ref=$(( now - st ))
  fi
  sago=$(( (now - ref) / 60 ))
  if [ ! -d "$DIR" ]; then state="NO RUN FOLDER ($DIR): check the watch list"
  elif [ "$n" -ge "$TOTAL" ]; then state="DONE"
  elif [ -n "$pid" ] && [ "$sago" -ge "$STALL" ]; then
    cores=$(cores_now "$pid") || cores=
    if [ -n "$cores" ] && awk -v c="$cores" 'BEGIN { exit !(c >= 0.5) }'; then
      state="LONG GAMES? program running (pid $pid) and busy ($cores cores), no new game for $sago min"
    else
      state="STALLED? program running (pid $pid) but idle (${cores:-?} cores), no new game for $sago min"
    fi
  elif [ -n "$pid" ]; then state="RUNNING (pid $pid)"
  elif [ -n "$CHAIN" ] && [ -n "$(find_pid "$CHAIN")" ]; then
    if [ "$last" -gt 0 ] && [ "$ago" -ge "$WAIT_MAX" ]; then
      state="WAITING TOO LONG? the chain script is running, the program is not, no new game for $ago min (a school-morning pause is shorter): check the chain's log"
    else
      state="WAITING (the chain script is running, the program is not: the school-morning pause)"
    fi
  else state="STOPPED (neither the program nor the chain script is running)"; [ -z "$CHAIN" ] && state="STOPPED (the program is not running)"; fi
  # a running program whose chain script died: nothing will commit, stop it at 06:30 or restart it after this sitting
  [ -n "$pid" ] && [ -n "$CHAIN" ] && [ "$n" -lt "$TOTAL" ] && [ -z "$(find_pid "$CHAIN")" ] \
    && state="$state; the chain script is NOT running (nothing will commit or restart after this sitting)"
  line="$(date -u +%FT%H:%MZ) $NAME: $n of $TOTAL games"
  [ "$x" -gt 0 ] && line="$line ($x $XLABEL)"
  line="$line, +$(( n - prev_n )) in $(( (now - prev_t) / 60 )) min"
  [ "$last" -gt 0 ] && line="$line, last game $(date -u -d "@$last" +%H:%MZ) ($ago min ago)"
  line="$line; $state"
  echo "$line" | tee "$RUNS/$NAME.status"
  echo "$line" >> "$RUNS/status_history.log"
  [ "$n" -ge "$TOTAL" ]
}

push() {  # STATUS.txt (the --body file, or the latest line of every run) committed on $BRANCH without touching main
  local blob tree parent commit body
  if [ -n "$BODY" ]; then
    body=$(cat "$BODY") || return 1
  else
    body=$(cat "$RUNS"/*.status 2>/dev/null; echo; echo "Written by rl/strength/run_watch.sh on the laptop. Times are UTC (the Z). If the newest time above is much older than the watcher's interval, the laptop could not report (off, asleep, offline, or the push is failing).")
  fi
  export GIT_TERMINAL_PROMPT=0   # unattended: a credential prompt fails at once instead of waiting for a keyboard
  blob=$(printf '%s\n' "$body" | git -C "$REPO" hash-object -w --stdin) || return 1
  tree=$(printf '100644 blob %s\tSTATUS.txt\n' "$blob" | git -C "$REPO" mktree) || return 1
  # Only a remote-tracking ref is written (no local branch: GitHub Desktop would list it, and switching to it would
  # empty the working tree). --no-auto-maintenance: no background gc started from here on the shared repository.
  if timeout 120 git -C "$REPO" fetch -q --no-auto-maintenance origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"; then
    parent=$(git -C "$REPO" rev-parse -q --verify "refs/remotes/origin/$BRANCH")
  else
    echo "fetch of $BRANCH failed; building on the last known status commit" >&2
    parent=$(git -C "$REPO" rev-parse -q --verify "refs/remotes/origin/$BRANCH")
  fi
  commit=$(git -C "$REPO" -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com commit-tree "$tree" ${parent:+-p "$parent"} -m "laptop status $(date -u +%FT%H:%MZ)") || return 1
  timeout 120 git -C "$REPO" push -q origin "$commit:refs/heads/$BRANCH" && echo "pushed $BRANCH ${commit:0:8}"
}

if [ "$PUSH_ONLY" = 1 ]; then push; exit $?; fi

while :; do
  look; done_now=$?
  [ "$PUSH" = 1 ] && { push || echo "push failed; will try again next time"; }
  [ "$done_now" = 0 ] || [ "$EVERY" = 0 ] && break
  sleep $(( EVERY * 60 ))
done
exit "$done_now"   # 0 once every game is written
