#!/bin/bash
# Convert the six new pause games (Recording_QA/BATCH_2026-10-13_REMAINING_SIX) into positions with the fixed converter of main (harness of ../../pause_games_new_2026-10-12),
# and write the deck files, games_meta.json and position_list.tsv/json into this folder. Nothing is run: no bot, no engine.
# The converter reads every game's DECK_USED.json first (the printings one game does not give are borrowed from the others), so the 24 games of Oct 12 are passed too and
# their positions are dropped again (they are already in ../pause_games_new_2026-10-12/).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(dirname "$HERE")
H=$OUT/../pause_games_new_2026-10-12/harness
QA=${QA:-"/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"}
TMP=$(mktemp -d)
G=()
for b in "$QA"/BATCH_2026-10-0[69]_NEW_PAUSE_GAMES "$QA"/BATCH_2026-10-11_NEW_PAUSE_GAMES; do
  for d in "$b"/2026*; do [ -f "$d/TURN_LEDGER.json" ] && G+=("$d"); done
done
# the six new games go through normalize_ledger.py (plays written with `details` only get a target and a result the converter can read)
for d in "$QA"/BATCH_2026-10-13_REMAINING_SIX/2026*; do
  [ -f "$d/TURN_LEDGER.json" ] || continue
  mkdir -p "$TMP/norm"
  python3 -B "$HERE/normalize_ledger.py" "$d" "$TMP/norm/$(basename "$d")"
  G+=("$TMP/norm/$(basename "$d")")
done
python3 -B "$H/ledger_to_positions.py" "$TMP/positions_all.json" "$TMP/report_convert.json" "${G[@]}" | grep -E "261013|total|FAILED" || true
python3 -B "$HERE/split_new.py" "$TMP" "$OUT" "$QA"
mkdir -p "$OUT/decks"
cp "$TMP"/KW261013_*.txt "$OUT/decks/"
python3 -B "$H/position_list.py" "$OUT/positions_all.json" "$HERE/empty.json" "$HERE/empty.json" "$OUT/games_meta.json" "$OUT/decks" "$OUT/position_list"
