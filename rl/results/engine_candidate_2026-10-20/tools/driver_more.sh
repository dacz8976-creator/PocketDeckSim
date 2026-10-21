#!/bin/bash
# The verification's gaps, night only (keeper-managed): (1) step 8/8b rows recorded by the pinned legality_scan, replayed on the
# candidate; (2) the 7c/7c2 km3 rows (no pinned-program recording: old pin and candidate both played tonight); (3) the d_rayquaza
# rows (c-dragonair_mega_rayquaza_ex holds Skull Fossil: #401's reach), old v new for km3, kta3 and k3.
W=/home/dacz8976/pincand_work
mkdir -p $W/pgids
echo "$(ps -o pgid= $$ | tr -d ' ')" > $W/pgids/more.pgid
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $W/driver.log; }
cd /home/dacz8976/pincand
log "driver_more start"
for n in 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_8b_new2_new_k3 08a9b3a_8b_new2_new_km3 \
         08a9b3a_8_will_new_k3 08a9b3a_8_will_new_km3 08a9b3a_8_new_k3 08a9b3a_8_new_km3; do
  grep -q -P "^new\t$n\t" $W/games/summary.tsv || python3 $W/replay.py new $n >> $W/driver.log 2>&1
done
python3 $W/oldnew.py 7c_km3 --from-run 08a9b3a_7c_old_km3 >> $W/driver.log 2>&1
python3 $W/oldnew.py 7c2_km3 --from-run 08a9b3a_7c2_old_km3 >> $W/driver.log 2>&1
for bot in km3 kta3 k3; do
  python3 $W/oldnew.py dray_dev_$bot --args "--pairs /home/dacz8976/pincand/rl/results/kta_tables_2026-09-29/pairs/dev_d_rayquaza.tsv --root /home/dacz8976/pincand --seed-base 22700000000 --bot $bot --pairings 0,1,2,3,4,5,6,7 --games 500" >> $W/driver.log 2>&1
done
log "driver_more done: $(grep -P '^(oldnew|new)\t(7c|dray|08a9b3a_8)' $W/games/summary.tsv | cut -f2,5,6 | tr '\t\n' ' ;')"
date -u +%FT%TZ > $W/more.done
