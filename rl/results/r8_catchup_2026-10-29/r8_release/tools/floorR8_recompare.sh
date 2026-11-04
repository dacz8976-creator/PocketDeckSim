#!/bin/bash
# floorR8_recompare.sh   (R8; a copy of R6's floorS_recompare.sh with the corrected rule of coordinator-080 from the start, 113 §4)
# Read-only. Compares the floor re-check on R8's official deckgym (floor2R8: RR_R8_543dad00/programs/deckgym, sha256 75090673...)
# with the same 12 pieces on R6's S (floor2S, Oct 29 UTC; its sums in r6_release/logs/floor_recheck_S/outputs.sha256), byte by byte.
# One line per piece and a RESULT line; exit 0 only if all 12 pass.
#
# Both runs used floor2.py (unchanged) in /home/dacz8976/pincand at b78c8997 (HEAD unchanged since Oct 22), so the decks and the
# manifest's goldfish (the coverage line) are the same on both sides: unlike R6, the goldfish line is NOT normalised; it must be equal.
# A piece passes when
#   - every *_games.jsonl and *_coverage.json is byte-equal to floor2S's (and each games file holds 1,920 games), and
#   - the page (*.md) equals floor2S's after normalising ONLY the engine path (RR_R8_543dad00/programs/deckgym v programs/R/deckgym);
#     exactly that one line differs before normalising (2 diff lines), none after; any other line fails;
#   - run_screen: run_screen.txt equals floor2S's after normalising the engine path only.
# Also: the same 12 pieces on both sides, and every file of _ref_stripped/ byte-equal. Second reading by the project's comparators:
# sitting1_check.py floor R8 v S (no modes) exits 0 for each page piece; switch_check.py screen R8 v S exits 0 for run_screen.
set -u
S=${FLOOR_NEW:-/home/dacz8976/pincand_work/floor2R8}; F=${FLOOR_REF:-/home/dacz8976/pincand_work/floor2S}
REPO=/home/dacz8976/pincand; CK=$REPO/rl/results/engine_switch_rules2_2026-10/sitting1_check.py; SC=$REPO/rl/results/engine_switch_rules2_2026-10/switch_check.py
NEWP='RR_R8_543dad00/programs/deckgym'; OLDP='programs/R/deckgym'
PIECES='A_07 A_brew-05b A_brew-06 A_brew-06b A_control14_k3 A_run_screen B_12 B_D_amended B_D_root B_D_victini-passive B_brew-07 B_brew-09'
echo "floorR8_recompare: new=$S ref=$F"
ps=$(cd $S && ls -d */ | tr -d / | grep -vx _ref_stripped | sort | tr '\n' ' ' | sed 's/ $//')
pf=$(cd $F && ls -d */ | tr -d / | grep -vx _ref_stripped | sort | tr '\n' ' ' | sed 's/ $//')
want=$(echo $PIECES | tr ' ' '\n' | sort | tr '\n' ' ' | sed 's/ $//')
setok=1; [ "$ps" = "$want" ] && [ "$pf" = "$want" ] || setok=0
echo "pieces new: $ps"; echo "pieces ref: $pf"; echo "piece sets: $([ $setok = 1 ] && echo 'the same 12' || echo 'NOT the expected 12')"
refok=1; nref=0
if [ -d $S/_ref_stripped ]; then
  while IFS= read -r f; do nref=$((nref+1)); cmp -s "$S/_ref_stripped/$f" "$F/_ref_stripped/$f" || { refok=0; echo "_ref_stripped/$f: DIFFERS or missing in ref"; }; done \
    < <(cd $S/_ref_stripped && find . -type f | sed 's#^\./##' | sort)
fi
nreff=$(cd $F/_ref_stripped 2>/dev/null && find . -type f | wc -l); [ "$nref" = "${nreff:-0}" ] && [ $nref -gt 0 ] || refok=0
echo "_ref_stripped: $nref files in new, ${nreff:-0} in ref: $([ $refok = 1 ] && echo 'all byte-equal' || echo 'NOT all byte-equal')"
pass=0
for p in $PIECES; do
  d=$S/$p; fd=$F/$p; ok=1; msg=""
  if [ "$p" = A_run_screen ]; then
    nd=$(diff $d/run_screen.txt $fd/run_screen.txt | grep -c '^[<>]')
    norm=$(diff <(sed "s#$NEWP#X/deckgym#g" $d/run_screen.txt) <(sed "s#$OLDP#X/deckgym#g" $fd/run_screen.txt) | grep -c '^[<>]')
    msg=" run_screen.txt: $nd raw differing lines (the engine path), $norm after normalising"
    [ "$norm" = 0 ] || ok=0
    out=$(cd $REPO && python3 -B $SC screen $d/run_screen.txt $fd/run_screen.txt 2>&1); rc=$?
    msg="$msg; switch_check.py screen new v ref: exit $rc ($(echo "$out" | tail -n 1 | sed "s#$S/##; s#$F/##" | cut -c1-160))"
    [ $rc = 0 ] || ok=0
  else
    ng=0; nc=0; nm=0
    for g in $d/*_games.jsonl; do ng=$((ng+1)); b=$(basename $g); n=$(wc -l < $g)
      if cmp -s $g $fd/$b && [ $n = 1920 ]; then msg="$msg games byte-equal ($n);"; else ok=0; msg="$msg games $b NOT byte-equal or not 1920 ($n);"; fi; done
    for c in $d/*_coverage.json; do nc=$((nc+1)); b=$(basename $c)
      if cmp -s $c $fd/$b; then msg="$msg coverage byte-equal;"; else ok=0; msg="$msg coverage $b NOT byte-equal;"; fi; done
    for m in $d/*.md; do nm=$((nm+1)); b=$(basename $m)
      nd=$(diff $m $fd/$b | grep -c '^[<>]')
      na=$(diff $m $fd/$b | grep '^<' | grep -cF "$NEWP")
      norm=$(diff <(sed "s#$NEWP#X/deckgym#g" $m) <(sed "s#$OLDP#X/deckgym#g" $fd/$b) | grep -c '^[<>]')
      msg="$msg page: $nd raw differing lines (engine path $na on the new side), $norm after normalising"
      [ "$nd" = 2 ] && [ "$na" = 1 ] && [ "$norm" = 0 ] || ok=0
      out=$(cd $REPO && python3 -B $CK floor $d $fd ${b%.md} --label "R8 v S $p" 2>&1); rc=$?
      msg="$msg; sitting1_check.py floor new v ref: exit $rc"
      [ $rc = 0 ] || { ok=0; msg="$msg [$(echo "$out" | tail -n 2 | tr '\n' ' ' | cut -c1-300)]"; }
    done
    [ $ng = 1 ] && [ $nc = 1 ] && [ $nm = 1 ] || { ok=0; msg="$msg (files: $ng games, $nc coverage, $nm pages; want 1 each)"; }
  fi
  if [ $ok = 1 ]; then pass=$((pass+1)); echo "PASS $p:$msg"; else echo "FAIL $p:$msg"; fi
done
if [ $pass = 12 ] && [ $setok = 1 ] && [ $refok = 1 ]; then
  echo "RESULT: 12 of 12 pieces equal to floor2S under the corrected rule (coordinator-080; engine path only)"; exit 0
fi
echo "RESULT: NOT accepted: $pass of 12 pieces pass; piece sets $setok; _ref_stripped $refok"; exit 1
