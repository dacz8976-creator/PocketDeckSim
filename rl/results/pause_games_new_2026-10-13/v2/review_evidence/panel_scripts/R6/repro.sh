set -e
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
QA="/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R6/repro"
rm -rf "$OUT"; mkdir -p "$OUT/norm"
for g in 20261013_010837000_iOS 20261013_014423000_iOS; do
  python3 -B "$R/rl/results/pause_games_new_2026-10-13/v2/scripts/normalize_ledger.py" "$QA/$g" "$OUT/norm/$g"
done
cd "$OUT"
python3 -B "$R/rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py" "$OUT/positions.json" "$OUT/report.json" "$OUT/norm/20261013_010837000_iOS" "$OUT/norm/20261013_014423000_iOS" | tail -5
ls "$OUT"
