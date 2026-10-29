#!/bin/bash
# floorS_recompare.sh   (R6, the floor re-check's acceptance rule as corrected after the run; coordinator-080)
# Read-only. Compares the floor re-check on S's deckgym (floor2S, Oct 29 UTC) with the same 12 pieces on main-4d48844's final
# build (floor2F, Oct 21 ~02:48-03:45 UTC), byte by byte, and prints one line per piece and a RESULT line; exit 0 only if all 12 pass.
#
# Why: floor2.py's own comparison said DIFFERS for 11 pieces, for one line only. A floor page's coverage line names the
# official goldfish (project_manifest.json available_release), which moved from rl/engine-2026-10-12 to rl/engine-2026-10-21
# with the Oct 21 adoption, after floor2F ran. The night's acceptance rule (night_r6.sh step 5: SAME, or DIFFERS and
# "v floor2F: exit 0") did not allow for that line, so it wrote floorS.FAILED. The games were not re-run.
#
# The corrected rule (coordinator-080): a piece passes when
#   - every *_games.jsonl and *_coverage.json is byte-equal to floor2F's (and each games file holds 1,920 games), and
#   - the page (*.md) equals floor2F's after normalising ONLY (a) the engine path, programs/R/deckgym v programs/F/deckgym,
#     and (b) the coverage line's goldfish, rl/engine-2026-10-21/goldfish (sha256 db52d3de...) v rl/engine-2026-10-12/goldfish
#     (sha256 d8cfb779...); exactly those two lines differ before normalising, none after; any other line fails;
#   - run_screen: run_screen.txt equals floor2F's after normalising (a) only.
# Also: the same 12 pieces on both sides, and every file of _ref_stripped/ (the stripped Oct 1 reference games) byte-equal.
# And, as a second reading by the project's own comparators (the refuters' suggestion): sitting1_check.py floor S v F
# --allow-coverage-program (which sets aside exactly the coverage line's program and hash) exits 0 for each page piece, and
# switch_check.py screen S v F exits 0 for run_screen.
set -u
S=${FLOOR_S:-/home/dacz8976/pincand_work/floor2S}; F=${FLOOR_F:-/home/dacz8976/pincand_work/floor2F}
REPO=/home/dacz8976/pincand; CK=$REPO/rl/results/engine_switch_rules2_2026-10/sitting1_check.py; SC=$REPO/rl/results/engine_switch_rules2_2026-10/switch_check.py
NEWG='rl/engine-2026-10-21/goldfish (sha256 db52d3de65ca2577aa39af7539635a1473d4f876842bd711131a3b2c7d797f31;'
OLDG='rl/engine-2026-10-12/goldfish (sha256 d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84;'
PIECES='A_07 A_brew-05b A_brew-06 A_brew-06b A_control14_k3 A_run_screen B_12 B_D_amended B_D_root B_D_victini-passive B_brew-07 B_brew-09'
echo "floorS_recompare: S=$S F=$F"
ps=$(cd $S && ls -d */ | tr -d / | grep -vx _ref_stripped | sort | tr '\n' ' ' | sed 's/ $//')
pf=$(cd $F && ls -d */ | tr -d / | grep -vx _ref_stripped | sort | tr '\n' ' ' | sed 's/ $//')
want=$(echo $PIECES | tr ' ' '\n' | sort | tr '\n' ' ' | sed 's/ $//')
setok=1; [ "$ps" = "$want" ] && [ "$pf" = "$want" ] || setok=0
echo "pieces S: $ps"; echo "pieces F: $pf"; echo "piece sets: $([ $setok = 1 ] && echo 'the same 12' || echo 'NOT the expected 12')"
refok=1; nref=0
while IFS= read -r f; do nref=$((nref+1)); cmp -s "$S/_ref_stripped/$f" "$F/_ref_stripped/$f" || { refok=0; echo "_ref_stripped/$f: DIFFERS or missing in F"; }; done \
  < <(cd $S/_ref_stripped && find . -type f | sed 's#^\./##' | sort)
nreff=$(cd $F/_ref_stripped && find . -type f | wc -l); [ $nref = $nreff ] && [ $nref -gt 0 ] || refok=0
echo "_ref_stripped: $nref files in S, $nreff in F: $([ $refok = 1 ] && echo 'all byte-equal' || echo 'NOT all byte-equal')"
pass=0
for p in $PIECES; do
  d=$S/$p; fd=$F/$p; ok=1; msg=""
  if [ "$p" = A_run_screen ]; then
    nd=$(diff $d/run_screen.txt $fd/run_screen.txt | grep -c '^[<>]')
    norm=$(diff <(sed 's#programs/R/deckgym#programs/X/deckgym#g' $d/run_screen.txt) <(sed 's#programs/F/deckgym#programs/X/deckgym#g' $fd/run_screen.txt) | grep -c '^[<>]')
    msg=" run_screen.txt: $nd raw differing lines (the engine path), $norm after normalising (a)"
    [ "$norm" = 0 ] || ok=0
    out=$(cd $REPO && python3 -B $SC screen $d/run_screen.txt $fd/run_screen.txt 2>&1); rc=$?
    msg="$msg; switch_check.py screen S v F: exit $rc ($(echo "$out" | tail -n 1 | sed "s#$S/##; s#$F/##" | cut -c1-160))"
    [ $rc = 0 ] || ok=0
  else
    ng=0; nc=0; nm=0
    for g in $d/*_games.jsonl; do ng=$((ng+1)); b=$(basename $g); n=$(wc -l < $g)
      if cmp -s $g $fd/$b && [ $n = 1920 ]; then msg="$msg games byte-equal ($n);"; else ok=0; msg="$msg games $b NOT byte-equal or not 1920 ($n);"; fi; done
    for c in $d/*_coverage.json; do nc=$((nc+1)); b=$(basename $c)
      if cmp -s $c $fd/$b; then msg="$msg coverage byte-equal;"; else ok=0; msg="$msg coverage $b NOT byte-equal;"; fi; done
    for m in $d/*.md; do nm=$((nm+1)); b=$(basename $m)
      nd=$(diff $m $fd/$b | grep -c '^[<>]')
      na=$(diff $m $fd/$b | grep '^<' | grep -c 'programs/R/deckgym'); nb=$(diff $m $fd/$b | grep '^<' | grep -cF "$NEWG")
      norm=$(diff <(sed -e "s#$NEWG#GOLDFISH#" -e 's#programs/R/deckgym#programs/X/deckgym#g' $m) \
                  <(sed -e "s#$OLDG#GOLDFISH#" -e 's#programs/F/deckgym#programs/X/deckgym#g' $fd/$b) | grep -c '^[<>]')
      msg="$msg page: $nd raw differing lines ((a) $na, (b) $nb on S's side), $norm after normalising (a) and (b)"
      [ "$nd" = 4 ] && [ "$na" = 1 ] && [ "$nb" = 1 ] && [ "$norm" = 0 ] || ok=0
      out=$(cd $REPO && python3 -B $CK floor $d $fd ${b%.md} --label "S v F $p" --allow-coverage-program 2>&1); rc=$?
      cov=$(echo "$out" | grep -o 'set aside in the page by --allow-coverage-program[^)]*' | head -n 1 | cut -c1-200)
      msg="$msg; sitting1_check.py floor S v F --allow-coverage-program: exit $rc${cov:+ ($cov)}"
      [ $rc = 0 ] || { ok=0; msg="$msg [$(echo "$out" | tail -n 2 | tr '\n' ' ' | cut -c1-300)]"; }
    done
    [ $ng = 1 ] && [ $nc = 1 ] && [ $nm = 1 ] || { ok=0; msg="$msg (files: $ng games, $nc coverage, $nm pages; want 1 each)"; }
  fi
  if [ $ok = 1 ]; then pass=$((pass+1)); echo "PASS $p:$msg"; else echo "FAIL $p:$msg"; fi
done
if [ $pass = 12 ] && [ $setok = 1 ] && [ $refok = 1 ]; then
  echo "RESULT: 12 of 12 pieces equal to floor2F under the corrected rule (coordinator-080)"; exit 0
fi
echo "RESULT: NOT accepted: $pass of 12 pieces pass; piece sets $setok; _ref_stripped $refok"; exit 1
