#!/bin/bash
# smoke_r8.sh PLAN PROGRAM OUT: the Lane N smoke runner (coordinator-147 §4, coordinator-148 §2.3, §2.6). Run by night_r8.sh.
#   PLAN = b_km3 | a_km3 | a_kx3 (see smoke_r8.py's docstring); PROGRAM = a strength build (the lane's for km3, K8's for kx3);
#   OUT = /home/dacz8976/pincand_work/RR_R8_<commit>; the games go to OUT/smoke/PLAN/.
# First the decks' legality (check_decks.py, against the lane's own card_status output, OUT/prep/card_status.json), then the
# games, one at a time (smoke_r8.py), at nice 19 / ionice -c3, with the KX_/PDL_/DECKGYM_/JEV_/PG_ variables and
# TEST_CARD_SUPPORT_MISSING_ATTACK removed. Exit: 0 as predicted, 1 STOP, 3 the kx3 smoke stopped (a decision over 120 s).
set -u
PLAN=${1:?usage: smoke_r8.sh PLAN PROGRAM OUT}; PROG=${2:?}; OUT=${3:?}
LW=/home/dacz8976/lane_r8_w
H=$LW/rl/results/r8_catchup_2026-10-29/lane/smoke
case "$PLAN" in b_km3|a_km3|a_kx3) ;; *) echo "unknown plan $PLAN"; exit 1;; esac
[ -x "$PROG" ] || { echo "no program $PROG"; exit 1; }
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_|TEST_CARD_SUPPORT_MISSING_ATTACK$)'); do unset "$v"; done
mkdir -p $OUT/smoke
python3 -I $H/check_decks.py $LW/engine/database.json $OUT/prep/card_status.json \
  $LW/rl/results/dual_type_seam_2026-10-23/r6_release/logs/card_status.json $H/decks > $OUT/smoke/check_decks.txt 2>&1
rc=$?; tail -n 1 $OUT/smoke/check_decks.txt
[ $rc = 0 ] || { echo "STOP: the smoke decks are not all legal and playable (see $OUT/smoke/check_decks.txt)"; exit 1; }
nice -n 19 ionice -c3 python3 -I $H/smoke_r8.py "$PLAN" "$PROG" "$LW" "$OUT/smoke"
