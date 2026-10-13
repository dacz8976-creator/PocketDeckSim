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
# the 14 new games go through normalize_ledger.py (plays written with `details` only get a target and a result the converter can read; a packet without a 20-card list gets the list
# of a game of the same named deck, marked unverified)
donor_of() {
  case "$1" in
    20261012_010706000_iOS) echo "$QA/BATCH_2026-10-13_REMAINING_SIX/20261013_010837000_iOS" ;;   # Glimmora / Alolan Muk / Kingambit / Regigigas
    20261012_203719000_iOS) echo "$QA/BATCH_2026-10-13_REMAINING_SIX/20261013_010003000_iOS" ;;   # New deck 16 (Glimmora / Alolan Muk / Regigigas)
    20261013_030351000_iOS) echo "$QA/BATCH_2026-10-13_NEWEST_TWO/20261013_022530000_iOS" ;;      # Haxorus / Dragonair / Druddigon
    *) echo "" ;;
  esac
}
for b in BATCH_2026-10-12_NEW_LONG_VIDEOS BATCH_2026-10-12_ADDITIONAL_TWO BATCH_2026-10-13_NEWEST_TWO BATCH_2026-10-13_REMAINING_SIX; do
  for d in "$QA/$b"/2026*; do
    [ -f "$d/TURN_LEDGER.json" ] || continue
    mkdir -p "$TMP/norm"
    donor=$(donor_of "$(basename "$d")")
    if [ -n "$donor" ]; then python3 -B "$HERE/normalize_ledger.py" "$d" "$TMP/norm/$(basename "$d")" "$donor"
    else python3 -B "$HERE/normalize_ledger.py" "$d" "$TMP/norm/$(basename "$d")"; fi
    G+=("$TMP/norm/$(basename "$d")")
  done
done
python3 -B "$H/ledger_to_positions.py" "$TMP/positions_all.json" "$TMP/report_convert.json" "${G[@]}" | grep -E "261013|total|FAILED" || true
python3 -B "$HERE/split_new.py" "$TMP" "$OUT" "$QA"
mkdir -p "$OUT/decks"
python3 - "$TMP" "$OUT" <<'EOF'
import glob, json, os, shutil, sys
tmp, out = sys.argv[1:3]
new = {'KW' + k[3:] for k in json.load(open(os.path.join(out, 'games_meta.json')))}
for f in glob.glob(os.path.join(tmp, 'KW*.txt')):
    if os.path.basename(f)[:-4] in new:
        shutil.copy(f, os.path.join(out, 'decks'))
EOF
python3 -B "$H/position_list.py" "$OUT/positions_all.json" "$HERE/empty.json" "$HERE/empty.json" "$OUT/games_meta.json" "$OUT/decks" "$OUT/position_list"
