#!/bin/bash
# One look at every run on the laptop's watch list, then one update of STATUS.txt on the branch `laptop-status`.
# The Windows task "PocketDeckSim laptop status" runs it every 30 minutes from outside WSL (Dustin approved it, Oct 9),
# so the status keeps coming after the Claude app or WSL restarts (the task starts WSL if it is down, and a run that died
# with it shows STOPPED), and after a laptop restart once Dustin signs in (the task runs only while he is signed in).
# While a listed run is not done every look is pushed; the first look after that pushes the new state once; then, while
# all are done or the list is empty, it pushes at most every 6 hours (KX_IDLE_PUSH_MIN), as a sign that the laptop is up.
#
# The list is $RUNS/watch.list (RUNS=${KX_RUNS_DIR:-$HOME/runs}), one run per line, fields separated by "|":
#   NAME|RUN_DIR|TOTAL|PATTERN|CHAIN|STALL_MIN|X_LABEL
# RUN_DIR is relative to the repository (or absolute); CHAIN, STALL_MIN and X_LABEL may be empty or left out; a line
# starting with # is skipped; PATTERN and CHAIN can't hold "|". The fields are run_watch.sh's --name, --dir, --total,
# --pattern, --chain, --stall-min and --x-label. Add a line when a long laptop run starts; take it out some time after
# the run is done. One watcher per NAME: don't also start run_watch.sh --every for a listed run.
# Everything it prints goes to $RUNS/watch_all.log (the task's console is hidden). KX_NO_PUSH=1 looks without pushing
# (tests; give them their own KX_RUNS_DIR, since a look moves the run's "+N in M min" starting point).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
RUNS=${KX_RUNS_DIR:-$HOME/runs}
LIST="$RUNS/watch.list"
IDLE_PUSH_MIN=${KX_IDLE_PUSH_MIN:-360}
mkdir -p "$RUNS"
LOG="$RUNS/watch_all.log"
# keep the log short; trimmed before it is opened, so the open file is never the one replaced
[ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 4000 ] && tail -n 2000 "$LOG" > "$LOG.tmp" && mv -f "$LOG.tmp" "$LOG"
exec >> "$LOG" 2>&1
echo "== $(date -u +%FT%TZ) look (pid $$)"
exec 9> "$RUNS/watch_all.lock"
flock -n 9 || { echo "another watch_all.sh is still running; this look is skipped"; exit 0; }
BODY=$(mktemp); trap 'rm -f "$BODY"' EXIT
now=$(date -u +%s)
listed=0 going=0 lines=()
if [ -e "$LIST" ]; then
  while IFS= read -r raw || [ -n "$raw" ]; do
    raw=${raw%$'\r'}
    case $raw in ''|'#'*) continue ;; esac
    IFS='|' read -r name dir total pattern chain stall xlabel <<< "$raw"
    listed=$((listed + 1))
    args=(--name "$name" --dir "$dir" --total "$total" --pattern "$pattern")
    [ -n "$chain" ] && args+=(--chain "$chain")
    [ -n "$stall" ] && args+=(--stall-min "$stall")
    [ -n "$xlabel" ] && args+=(--x-label "$xlabel")
    out=$(bash "$HERE/run_watch.sh" "${args[@]}" < /dev/null 9>&- 2>&1); rc=$?
    case $rc in
      0) line=$out ;;                                       # every game written
      1) line=$out; going=$((going + 1)) ;;                 # not done: running, waiting, stuck or stopped
      *) going=$((going + 1))                               # the look itself failed: keep its reason
         line="$(date -u +%FT%H:%MZ) $name: the look failed (run_watch.sh exit $rc): $(printf '%s\n' "$out" | tail -n 1 | cut -c1-200)" ;;
    esac
    lines+=("$line")
  done < "$LIST"
fi
{
  echo "Laptop checked at $(date -u -d "@$now" +%FT%H:%MZ): $listed run(s) on the watch list, $going not done."
  [ ${#lines[@]} -gt 0 ] && printf '%s\n' "${lines[@]}"
  echo
  echo "Times are UTC (the Z). Rewritten every 30 minutes while a run above is not done, and every 6 hours otherwise."
  echo "If the check time is much older than that, the laptop could not report: off or asleep (the run is paused),"
  echo "restarted and not signed in yet (the run stopped; nothing runs until sign-in), offline, or the push is failing"
  echo "(the reason is in ~/runs/watch_all.log in WSL)."
} > "$BODY"
cat "$BODY"
[ "${KX_NO_PUSH:-0}" = 1 ] && { echo "KX_NO_PUSH=1: no push (a test)"; exit 0; }
last=$(cat "$RUNS/last_push" 2> /dev/null || echo 0)
[[ "$last" =~ ^[0-9]+$ ]] || last=0
if [ "$going" -eq 0 ] && [ $(( (now - last) / 60 )) -lt "$IDLE_PUSH_MIN" ]; then
  echo "nothing going and the last push was $(( (now - last) / 60 )) min ago: no push this time"
  exit 0
fi
if bash "$HERE/run_watch.sh" --push-only --body "$BODY" < /dev/null 9>&-; then
  # after a busy push, 0: the first idle look (a run just finished, or was taken off the list) is pushed at once
  if [ "$going" -gt 0 ]; then echo 0; else echo "$now"; fi > "$RUNS/last_push"
else
  echo "push failed; the next look tries again"
  exit 1
fi
