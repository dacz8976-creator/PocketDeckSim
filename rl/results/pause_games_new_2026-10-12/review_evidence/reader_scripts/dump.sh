#!/bin/bash
B='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-11_NEW_PAUSE_GAMES'
O='/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review'
for g in 20261012_003458000_iOS 20261012_004128000_iOS 20261012_004435000_iOS; do
  python3 -I "$O/dump_ledger.py" "$B/$g/TURN_LEDGER.json" "" > "$O/dump_$g.txt" 2>&1
  echo "$g $(wc -l < "$O/dump_$g.txt")"
done
