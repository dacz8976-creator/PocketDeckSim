#!/usr/bin/env bash
# Quiet hours for Dustin's class (Sept 28: "limit your laptop core usage", leaving at 12:15, class 1-4 pm Central;
# "I will let you know once I am back home, when you are free to go back to full steam ahead").
# From 17:10 UTC (12:10 pm CDT) every heavy process of this session's runs is paused (SIGSTOP). They are resumed
# (SIGCONT) only when the file quiet_resume.flag appears in this folder, created on Dustin's word. Checks every 20 s,
# so a laptop that was asleep is handled on waking; processes started while quiet are paused too. Nothing is killed.
# Log: quiet_hours.log.
O="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/engine_switch_2026-09-28"
PAT='legality_scan|deckgym simulate|/deckgym |count\.py|floor\.py|run_screen\.py|cargo build|cargo test|rustc'
START=$(date -u -d '2026-09-28 17:10:00' +%s); FLAG="$O/quiet_resume.flag"
log() { echo "$(date -u +%FT%TZ) $*" >> "$O/quiet_hours.log"; }
state=none
log "started; quiet from 17:10Z until quiet_resume.flag exists"
while true; do
  now=$(date -u +%s)
  if [ -e "$FLAG" ]; then
    pids=$(pgrep -f "$PAT" || true)
    [ -n "$pids" ] && kill -CONT $pids 2>/dev/null
    log "resume flag found: resumed $(echo $pids | wc -w) processes; done"; exit 0
  fi
  if [ $now -ge $START ]; then
    pids=$(pgrep -f "$PAT" | grep -v -w $$ || true)
    if [ -n "$pids" ]; then kill -STOP $pids 2>/dev/null; [ $state != paused ] && log "paused: $(echo $pids | wc -w) processes"; fi
    state=paused
  fi
  sleep 20
done
