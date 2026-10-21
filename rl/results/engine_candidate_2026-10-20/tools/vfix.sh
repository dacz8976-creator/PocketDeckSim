W=/home/dacz8976/pincand_work
CK=/home/dacz8976/pincand/rl/results/engine_switch_rules2_2026-10/switch_check.py
for bot in km3 kta3 k3; do
  f=$W/games/v/dray_dev_${bot}_V.jsonl
  python3 $CK same $f --ref $W/games/oldnew/dray_dev_${bot}_old.jsonl --expect 3500 --exclude-pairings 3 --label "V v old dray $bot (pairings 0-2, 4-7)" > ${f%.jsonl}.cmp 2>&1
  echo "$(date -u +%FT%TZ) V v old (corrected --expect 3500), dray $bot, pairings 0-2,4-7: exit $? $(tail -1 ${f%.jsonl}.cmp | cut -c1-170)" | tee -a $W/driver.log
done
# V v old on ALL 4,000 per bot (pairing 3 included): one line each
for bot in km3 kta3 k3; do
  f=$W/games/v/dray_dev_${bot}_V.jsonl
  python3 $CK same $f --ref $W/games/oldnew/dray_dev_${bot}_old.jsonl --expect 4000 --label "V v old dray $bot (all)" > ${f%.jsonl}_all.cmp 2>&1
  echo "$(date -u +%FT%TZ) V v old, dray $bot, all 8 pairings: exit $? $(tail -1 ${f%.jsonl}_all.cmp | cut -c1-150)" | tee -a $W/driver.log
done
touch $W/KEEPER_EXIT
echo "$(date -u +%FT%TZ) heavy work done; keeper asked to exit" >> $W/driver.log
sleep 35; tmux ls
