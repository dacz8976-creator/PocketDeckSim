#!/bin/bash
# Regenerate the positions, the deck files, what was left out and the position list from Codex's ledgers (nothing is run: no bot, no engine).
#   regenerate.sh [OLD_POSITIONS.json OLD_KM3_SUMMARY.json]   (the first version's files, for the km3_read column; default: the ones in this folder's git history)
# Needs the Recording_QA folder (Codex's packets) and engine/database.json in this checkout. Run from anywhere.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(dirname "$HERE")
QA=${QA:-"/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"}
G=()
for b in "$QA"/BATCH_2026-10-0[69]_NEW_PAUSE_GAMES "$QA"/BATCH_2026-10-11_NEW_PAUSE_GAMES; do
  for d in "$b"/2026*; do [ -f "$d/TURN_LEDGER.json" ] && G+=("$d"); done
done
TMP=$(mktemp -d)
python3 -B "$HERE/ledger_to_positions.py" "$TMP/positions_all.json" "$TMP/report_convert.json" "${G[@]}"
mkdir -p "$OUT/decks"
cp "$TMP"/KW*.txt "$OUT/decks/"
cp "$TMP/positions_all.json" "$TMP/report_convert.json" "$OUT/"
OLD_POS=${1:-"$OUT/superseded_v1/positions_all.json"}
OLD_KM3=${2:-"$OUT/superseded_v1/km3_summary.json"}
python3 -B "$HERE/position_list.py" "$OUT/positions_all.json" "$OLD_POS" "$OLD_KM3" "$OUT/games_meta.json" "$OUT/decks" "$OUT/position_list"
