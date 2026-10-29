#!/bin/bash
# goldfishS_floor_coverage.sh   (R6; closes a gap the floor refuters named)
# The floor re-check took its coverage from the official goldfish of that night (rl/engine-2026-10-21/goldfish), so it never ran
# S's own goldfish, which floor.py will use once S is the official release. This runs S's goldfish (programs/R/goldfish) exactly
# as floor.py calls it (--deck <list> --panel decks/screen/opponents --games 0 --coverage <file>, cwd engine/) on the 11 floor
# decks, into a scratch folder, and compares each coverage file byte for byte with floor2S's. No games are played. Read-only
# for the repository and the floor folders.
set -u
R=/home/dacz8976/pincand; PG=/home/dacz8976/pincand_work/programs/R; S=/home/dacz8976/pincand_work/floor2S
OUT=${GF_OUT:-/home/dacz8976/relplan/goldfishS_cov}; rm -rf $OUT; mkdir -p $OUT
DFIRST=rl/results/engine_switch_rules2_2026-10/floor_7c/d_first/draft-D-entei-grimhound.txt
GSHA=$(sha256sum $PG/goldfish | cut -c1-64)
echo "S's goldfish: $PG/goldfish sha256 $GSHA (SOURCE_COMMIT $(cat $PG/SOURCE_COMMIT))"
grep -q "^$GSHA  goldfish\$" $PG/SHA256SUMS && echo "  = its build-time SHA256SUMS line" || { echo "NOT its SHA256SUMS line"; exit 1; }
pass=0; n=0
while read -r piece deck name; do
  n=$((n+1)); cov=$OUT/${piece}_coverage.json
  (cd $R/engine && nice -n 19 $PG/goldfish --deck $R/$deck --panel $R/decks/screen/opponents --games 0 --coverage $cov) > $OUT/$piece.log 2>&1; rc=$?
  if [ $rc = 0 ] && cmp -s $cov $S/$piece/${name}_coverage.json; then pass=$((pass+1)); echo "EQUAL $piece: rc 0, coverage byte-equal to floor2S ($(sha256sum $cov | cut -c1-16))"
  else echo "DIFFERS $piece: rc $rc; $(cmp $cov $S/$piece/${name}_coverage.json 2>&1 | head -n 1); log: $(tail -n 2 $OUT/$piece.log | tr '\n' ' ' | cut -c1-200)"; fi
done <<EOF
A_brew-06 decks/brews/brew-06-pyukumuku-silvally-payback.txt brew-06-pyukumuku-silvally-payback
A_brew-06b decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt brew-06b-pyukumuku-silvally-scyther-grass
A_control14_k3 decks/dustin/14-comfey-raticate-hypno.txt 14-comfey-raticate-hypno
A_brew-05b decks/brews/brew-05b-meowstic-hatterene-comfey.txt brew-05b-meowstic-hatterene-comfey
A_07 decks/dustin/07-skarmory-stall.txt 07-skarmory-stall
B_12 decks/dustin/12-ariados-whimsicott-ogerpon.txt 12-ariados-whimsicott-ogerpon
B_brew-07 decks/brews/brew-07-hoopa-darkrai-sableye.txt brew-07-hoopa-darkrai-sableye
B_brew-09 decks/brews/brew-09-sableye-obstagoon.txt brew-09-sableye-obstagoon
B_D_victini-passive $DFIRST draft-D-entei-grimhound
B_D_root $DFIRST draft-D-entei-grimhound
B_D_amended decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt draft-D-entei-grimhound
EOF
echo "RESULT: S's goldfish gives byte-equal coverage on $pass of $n floor decks"
[ $pass = $n ]
