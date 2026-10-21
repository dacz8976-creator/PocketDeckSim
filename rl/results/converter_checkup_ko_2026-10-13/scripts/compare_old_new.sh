#!/bin/bash
# The converter of main (origin/main) against this branch's, on the same ledgers, to show which fields of which positions the checkup knock-out change touches.
#   compare_old_new.sh            (run from anywhere; needs the Recording_QA folder; about a minute; nothing is written into the repository except an untracked copy of the old converter
#                                  that is removed again)
# Inputs: the 28 older games as they are; the 14 games of Oct 12-13 through v2's normalize_ledger.py in two forms: WITH its checkup restore step (the ledgers the v2 read used) and WITHOUT it
# (POST set to empty: the arrows, details and decks are normalised, but the knocked-out Pokemon is not put back). The expectations are in README.md.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
H=$ROOT/rl/results/pause_games_new_2026-10-12/harness
V2S=$ROOT/rl/results/pause_games_new_2026-10-13/v2/scripts
QA=${QA:-"/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"}
TMP=${TMP:-/tmp/ck}
git -C "$ROOT" show origin/main:rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py > "$H/_old_ltp.py"
trap 'rm -f "$H/_old_ltp.py"; rm -rf "$H/__pycache__"' EXIT
rm -rf "$TMP"; mkdir -p "$TMP/restore" "$TMP/norestore"
sed 's/^POST = (.*/POST = ()/' "$V2S/normalize_ledger.py" > "$TMP/normalize_norestore.py"
OLDG=(); R=(); N=()
for b in "$QA"/BATCH_2026-10-0[69]_NEW_PAUSE_GAMES "$QA"/BATCH_2026-10-11_NEW_PAUSE_GAMES; do
  for d in "$b"/2026*; do [ -f "$d/TURN_LEDGER.json" ] && OLDG+=("$d"); done
done
for b in BATCH_2026-10-12_NEW_LONG_VIDEOS BATCH_2026-10-12_ADDITIONAL_TWO BATCH_2026-10-13_NEWEST_TWO BATCH_2026-10-13_REMAINING_SIX; do
  for d in "$QA/$b"/2026*; do
    [ -f "$d/TURN_LEDGER.json" ] || continue
    python3 -B "$V2S/normalize_ledger.py" "$d" "$TMP/restore/$(basename "$d")" > /dev/null
    python3 -B "$TMP/normalize_norestore.py" "$d" "$TMP/norestore/$(basename "$d")" > /dev/null
    R+=("$TMP/restore/$(basename "$d")"); N+=("$TMP/norestore/$(basename "$d")")
  done
done
cd "$H"
for set in restore norestore; do
  if [ $set = restore ]; then GG=("${R[@]}"); else GG=("${N[@]}"); fi
  python3 -B _old_ltp.py "$TMP/old_$set.json" "$TMP/old_${set}_rep.json" "${OLDG[@]}" "${GG[@]}" > "$TMP/old_$set.log" 2>&1
  python3 -B ledger_to_positions.py "$TMP/new_$set.json" "$TMP/new_${set}_rep.json" "${OLDG[@]}" "${GG[@]}" > "$TMP/new_$set.log" 2>&1
done
python3 "$HERE/cmp_pos.py" "$TMP/old_restore.json" "$TMP/new_restore.json" "old v new, the v2 read's ledgers (restore step on): expect identical"
python3 "$HERE/cmp_pos.py" "$TMP/old_norestore.json" "$TMP/new_norestore.json" "old v new, ledgers without the restore step: expect only 030351 t07-t15"
python3 "$HERE/cmp_pos.py" "$TMP/new_restore.json" "$TMP/new_norestore.json" "new converter, restore step on v off: expect Energy count and note wording only"
python3 "$HERE/before_after.py" "$TMP/old_norestore.json" "$TMP/new_norestore.json" > "$HERE/../before_after.json"
