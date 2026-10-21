#!/bin/bash
# Release follow-through, night lane A: every floor re-check page of rl/results/floor_recheck_rules2_2026-10/ replayed on the
# candidate deckgym (floor2.py; serial, nice 19, ionice -c3). Night window only; the keeper freezes this group at 12:55Z.
set -u
W=/home/dacz8976/pincand_work
R=$W/release
LOG=$R/lane_a.log
mkdir -p $R $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/lane_a.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $LOG; }
in_window() { local m=$((10#$(date -u +%H) * 60 + 10#$(date -u +%M))); [ $m -ge 120 ] && [ $m -lt 770 ]; }
log "lane_a armed (pgid $(cat $W/pgids/lane_a.pgid))"
while ! in_window; do sleep 60; done
log "lane_a start: floor2.py (12 pieces)"
cd /home/dacz8976/pincand
python3 -u $W/floor2.py >> $LOG 2>&1
log "lane_a floor2.py exit $?"
cat $W/floor2/summary.tsv >> $LOG
date -u +%FT%TZ > $R/lane_a.end
