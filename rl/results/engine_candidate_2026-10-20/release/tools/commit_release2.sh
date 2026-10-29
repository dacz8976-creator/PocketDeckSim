#!/bin/bash
# After tonight's lanes: commit the final build's record on the candidate branch (results only; engine/ untouched):
#   rl/results/engine_candidate_2026-10-20/programs_final/  the final build's programs (100755), SHA256SUMS, SOURCE_COMMIT
#   rl/results/engine_candidate_2026-10-20/release/         floor pages (both builds), replay sample, build and suite logs,
#                                                           lane logs, the keeper's log, tools
# Refuses on anything unexpected. Pushes the branch.
set -eu
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad
W=/home/dacz8976/pincand_work; R=$W/release; REPO=/home/dacz8976/pincand
CAND=rl/results/engine_candidate_2026-10-20; D=$REPO/$CAND/release; PF=$REPO/$CAND/programs_final
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
cd $REPO
[ "$(git rev-parse --abbrev-ref HEAD)" = laptop/engine-candidate-2026-10-20 ] || { echo "not on the candidate branch"; exit 1; }
[ -z "$(git status --porcelain)" ] || { git status --short; echo "tree not clean"; exit 1; }
for s in build_F suite_F floorF; do [ -e $R/$s.done ] || { echo "$s not done"; exit 1; }; done
[ -e $R/lane_a.end ] || { echo "lane A has not ended"; exit 1; }
F=$(cat $R/F_COMMIT)
[ "$(cat $W/programs/F/SOURCE_COMMIT)" = "$F" ] || { echo "programs/F is not F's build"; exit 1; }
[ "$(git rev-parse HEAD:engine)" = "$(git rev-parse $F:engine)" ] || { echo "the branch's engine/ is not F's"; exit 1; }
for f in $W/hb/lane_b2.sh $W/hb/mk_kf.sh $W/hb/replay2.py $W/floor2.py $W/lane_a.sh $W/window_keeper.sh; do [ -e $f ] || { echo "missing $f"; exit 1; }; done

# the final build's programs
mkdir -p $PF
cp $W/programs/F/deckgym $W/programs/F/legality_scan $W/programs/F/goldfish $W/programs/F/SHA256SUMS $W/programs/F/SOURCE_COMMIT $PF/
chmod 755 $PF/deckgym $PF/legality_scan $PF/goldfish
(cd $PF && sha256sum -c SHA256SUMS)

# the record
mkdir -p $D/floor_recheck $D/floor_recheck_final $D/replays_final $D/tools
for pair in "floor2:floor_recheck" "floor2F:floor_recheck_final"; do
  src=$W/${pair%%:*}; dst=$D/${pair##*:}
  for p in $src/*/; do
    piece=$(basename $p); [ "$piece" = _ref_stripped ] && continue
    mkdir -p $dst/$piece
    for f in $p*.md $p/cmd.txt $p/cmp*.txt $p/run.log $p/run_screen.txt; do [ -e "$f" ] && cp "$f" $dst/$piece/; done
  done
  cp $src/summary.tsv $dst/
  (cd $src && find . -type f ! -path './_ref_stripped/*' | sort | xargs sha256sum) > $dst/outputs.sha256
done
python3 -I $S/hb/floor_table2.py > $D/FLOOR_TABLE.md
{ echo "The final build's differing games against the Oct 20 build's (lane A, equal to the recorded pages), per opponent."
  echo "The brought-in cards in those rows (engine/database.json): t-blaziken 1 Rocky Helmet A2 148, which now answers"
  echo "Mega Sableye ex's hit back; t-vespiquen 2 Shuckle ex A4 021, Solid Shell \"This Pokemon takes -20 damage from attacks\","
  echo "which now cuts it. No other list in decks/screen/opponents holds a card item 8 reads. Sort: (a), item 8."
  echo
  python3 -I $S/hb/diff_by_opp.py B_brew-07 brew-07-hoopa-darkrai-sableye_games.jsonl
  python3 -I $S/hb/diff_by_opp.py B_brew-09 brew-09-sableye-obstagoon_games.jsonl; } > $D/floor_recheck_final/DIFF_BY_OPPONENT.txt
for f in $W/games/f/*; do case "$f" in *.jsonl|*_coverage.json) ;; *) cp "$f" $D/replays_final/;; esac; done
grep '^f	' $W/games/summary.tsv > $D/replays_final/summary_f.tsv || true
(cd $W/games/f && sha256sum *.jsonl *_coverage.json 2>/dev/null) > $D/replays_final/outputs.sha256 || true
{ echo "Final build: $F (engine tree $(git rev-parse $F:engine))"; cat $W/programs/F/SHA256SUMS; grep -E 'BUILD OK|^\s+Finished' $R/build_F.log | tail -n 4; } > $D/build_F.txt
{ grep 'suite_F' $R/lane_b.log; grep -E '^test result:' $R/suite_F.log; grep -E '^test .*(hit_back|retaliat|rocky_helmet|rough_skin|heavy_helmet|poltchageist|plus_x|disguise|intimidating|safeguard|p2_off|poison_barb|own_new)' $R/suite_F.log; } > $D/tests_F.txt
cp $R/lane_a.log $R/lane_b.log $D/
sed -n '/2026-10-20T14:3/,$p' $W/window_keeper.log > $D/window_keeper.log
for f in floor2.py lane_a.sh window_keeper.sh; do cp $W/$f $D/tools/; done
for f in lane_b2.sh mk_kf.sh replay2.py; do cp $W/hb/$f $D/tools/; done
for f in hb/adopt_final.py hb/slowpin_final.py hb/floor_table2.py hb/diff_by_opp.py hb/commit_release2.sh hb/arm_b2.sh pin/verify_draft.sh pin/adopt_draft.py pin/floor_table.py; do tr -d '\r' < $S/$f > $D/tools/$(basename $f); done
cp $S/hb/reach/reach_scan.py $S/hb/reach/reach_report.txt $D/tools/ 2>/dev/null || true
git add $CAND/programs_final $CAND/release
git ls-files -s $CAND/programs_final
SHORT=$(python3 -I $S/hb/floor_table2.py | tail -n 1 | python3 -c 'import json,sys; print(json.load(sys.stdin)["short"])')
$G commit -q -F - <<EOF
Engine candidate, release follow-through: the final build (${F:0:8}) and its checks

- programs_final/: the final candidate's programs, built once from ${F:0:8} (engine tree $(git rev-parse $F:engine | cut -c1-12)) in a fresh folder at
  CARGO_BUILD_JOBS 2; mode 100755; the bytes the night's checks ran.
- release/floor_recheck_final/: every piece of rl/results/floor_recheck_rules2_2026-10/ on the final build, compared with the
  recorded page and, where it differs, with the Oct 20 build's page (release/floor_recheck/, lane A). $SHORT.
- release/replays_final/: a sample of the Oct 20 pass's runs on the final build, compared with the reference and with the
  Oct 20 build's games.
- release/build_F.txt, tests_F.txt: the build and the whole suite on it. Logs and the tools as run.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
git push -q origin laptop/engine-candidate-2026-10-20
git log --oneline -2
