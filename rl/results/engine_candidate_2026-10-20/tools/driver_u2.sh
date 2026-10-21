#!/bin/bash
# After tier 2: U-verify every changed run (u_verify.py), then re-run the classifier. Keeper-managed (night only).
W=/home/dacz8976/pincand_work
mkdir -p $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/u2.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $W/driver.log; }
log "driver_u2: waiting for tier2.done"
while [ ! -e $W/tier2.done ]; do
  tmux has-session -t "=pingames" 2>/dev/null || { [ -e $W/tier2.done ] || { log "driver_u2: the games driver ended without tier2.done; stop"; exit 1; }; }
  sleep 60
done
rm -f $W/games/u/verify.tsv
cd /home/dacz8976/pincand
python3 $W/u_verify.py >> $W/driver.log 2>&1
python3 $W/classify.py >> $W/driver.log 2>&1
log "driver_u2: U verification: $(cut -f1,2,4 $W/games/u/verify.tsv | tr '\t\n' ' ;')"
date -u +%FT%TZ > $W/u2.done
