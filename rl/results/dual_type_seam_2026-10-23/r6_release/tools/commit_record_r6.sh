#!/bin/bash
# commit_record_r6.sh [--push]   (R6 runbook step 9; adapted from release/tools/commit_release2.sh, which made 005c16a6)
# DRAFT, written Oct 29 before the night ended; changed for coordinator-076. Run it once, after night_r6.sh has ended.
#
# Commits the build record of S on the release branch in /home/dacz8976/r6s_w (results only; engine/ untouched), as ONE commit
# directly on S (HEAD must be S itself):
#   rl/results/dual_type_seam_2026-10-23/r6_release/programs_final/  deckgym, legality_scan, goldfish (mode 100755), SHA256SUMS (the
#                                                                   three, in that order), SOURCE_COMMIT
#   .../r6_release/RAN_SHA256.txt       the programs that actually ran (the replays' and the floor's programs/R, the self-checks'
#                                       kx_r4/strength) against the committed ones, by sha256: all must be equal (coordinator-076)
#   .../r6_release/RUN_CONTEXT.txt      the checkout the floor and the replays read (/home/dacz8976/pincand: its HEAD) and the
#                                       byte-equality of the tools they ran with S's or the committed copies
#   .../r6_release/logs/                the lane on S (build, gencmp hashes, card_status, suite, lane log, replay log), the night
#                                       (night.log, switch runs, strength build, self-checks, floor log, refusal test, rl/strength
#                                       suite), replays_S/ (the 18 replays' small files + the r rows), floor_recheck_S/ (the 12 floor
#                                       pieces, and RECOMPARE.txt: floorS_recompare.sh's output, the corrected rule of coordinator-080),
#                                       floorS.FAILED.txt and floorS.done.txt (both kept), strength.build.json, K_overlay.txt,
#                                       programs_R_SHA256SUMS (all five). NOT item 11's suite (suite_I11.log goes with item 11's own report).
#   .../r6_release/tools/               the scripts as run (night_r6.sh, lane_s.sh, mk_ks.sh, replay3.py with side r) and the day
#                                       scripts (this one, adopt_r6.py, verify_r6.sh, the README template); TOOLS.txt
#   .../r6_release/FLOOR_TABLE.md, REPLAY_TABLE.md, record.json   (the numbers adopt_r6.py reads from git)
# Guardrail B: if any expected verdict is not met, it refuses before committing, removes the partial record it wrote, and nothing
# else runs. --push (Guardrail A first, for both): the record branch and K (laptop/kx3-on-r6-2026-10-29), to our origin only.
# GEN_FILES=full commits prep/gen_ids.rs and gen_database.rs (4.5 MB of generated Rust); the default commits only their sha256.
set -eu
DAY=${DAY:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/relplan/r6/day}   # the day scripts' folder
W=/home/dacz8976/pincand_work; N=$W/r6night; PR=$W/prep; GM=$W/games; PG=$W/programs/R
REPO=/home/dacz8976/pincand; WT=/home/dacz8976/r6s_w; BR=laptop/r6-release-2026-10-29; KBR=laptop/kx3-on-r6-2026-10-29
S=affe56e88985e2997a66beb85efaca0c487617bd
K=e3ddc0149bb9d35fda1becbb17ab5f71d9461609
KX=87a7f3404263e1bfe76e8765ba8dd94695e19cfe
P=/home/dacz8976/kx_r4/strength
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
REC=rl/results/dual_type_seam_2026-10-23/r6_release
D=$WT/$REC; PF=$D/programs_final; L=$D/logs
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
PUSH=0; [ "${1:-}" = --push ] && PUSH=1
die() { echo "REFUSED: $*" >&2; exit 1; }
CREATED=0; COMMITTED=0; TMPR=
finish() {
  local rc=$?
  [ -n "$TMPR" ] && rm -rf "$TMPR"
  if [ $rc != 0 ] && [ $CREATED = 1 ] && [ $COMMITTED = 0 ]; then
    cd $WT; git reset -q -- $REC 2>/dev/null || true; rm -rf "$D"
    echo "Guardrail B: refused after writing; the partial record $D was removed, nothing was committed or pushed" >&2
  fi
}
trap finish EXIT

# ---- guards (nothing is written in the repository before these pass) -----------------------------------------------------
cd $WT
[ "$(git rev-parse --abbrev-ref HEAD)" = $BR ] || die "$WT is not on $BR"
[ "$(git rev-parse HEAD)" = $S ] || die "HEAD is $(git rev-parse --short HEAD), not S: the record goes directly on S"
[ -z "$(git status --porcelain)" ] || { git status --short; die "$WT is not clean"; }
[ ! -e $D ] || die "$D exists"
[ -e $N/night.end ] || die "night_r6 has not ended ($N/night.end missing)"
for s in lane_S switch_runs strength_K sc_km3 sc_kx3 floorS strength_tests; do
  [ -e $N/$s.done ] || die "night step $s not done"
  # coordinator-080: floorS alone keeps its FAILED marker (the night's rule missed the goldfish line); it counts as done only with
  # the done file that names coordinator-080, and only if floorS_recompare.sh passes below
  if [ -e $N/$s.FAILED ]; then { [ $s = floorS ] && grep -q 'coordinator-080' $N/$s.done; } || die "night step $s FAILED: $(cat $N/$s.FAILED)"; fi
done
for s in build_R gen_R status_R suite_R replays_R; do
  [ -e $PR/$s.done ] || die "lane step $s not done"; [ ! -e $PR/$s.FAILED ] || die "lane step $s FAILED"; done
[ "$(cat $N/lane_S.verdict)" = PASS ] || die "lane S verdict: $(cat $N/lane_S.verdict)"
[ "$(cat $PR/R_COMMIT)" = $S ] || die "prep/R_COMMIT is not S"
[ "$(cat $PG/SOURCE_COMMIT)" = $S ] || die "programs/R is not S's build (SOURCE_COMMIT $(cat $PG/SOURCE_COMMIT))"
[ "$(git rev-parse HEAD:engine)" = "$(git rev-parse $S:engine)" ] || die "the branch's engine/ is not S's"
[ "$(cat $N/sc_km3.out)" = "$SC_KM3" ] || die "km3's self-check differs from the pin text: STOP (coordinator; new texts need Dustin)"
[ "$(cat $N/sc_kx3.out)" = "$SC_KX3" ] || die "kx3's self-check differs from the pin text: STOP (coordinator; new texts need Dustin)"
[ -x $P ] && [ -e $P.build.json ] || die "$P or its build record is missing"
[ "$(git rev-parse $K^1) $(git rev-parse $K^2)" = "$KX $S" ] || die "K's parents are not 87a7f340 and S"
[ "$(git diff --name-only $S $K | wc -l)" = 6 ] || die "K differs from S in other than kx3's six files"
[ "$(git rev-parse -q --verify refs/heads/$KBR)" = $K ] || die "the local branch $KBR is not K"
python3 -I - $P $K "$(git rev-parse $K:engine)" $HARN <<'EOF' || die "the strength build record does not match"
import hashlib, json, sys
p, k, t, h = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2')
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
if hashlib.sha256(open(p, 'rb').read()).hexdigest() != r.get('program_sha256'):
    bad['program_sha256'] = 'the program is not the recorded one'
sys.exit('build record: %r' % bad if bad else 0)
EOF
for f in night_r6.sh lane_s.sh mk_ks.sh replay3.py; do [ -e $W/hb/$f ] || die "missing $W/hb/$f"; done
for f in commit_record_r6.sh adopt_r6.py verify_r6.sh README_engine_2026-10-29.md floorS_recompare.sh goldfishS_floor_coverage.sh; do [ -e $DAY/$f ] || die "missing $DAY/$f"; done
[ "$(grep -cP '^r\t' $GM/summary.tsv)" = 18 ] || die "games/summary.tsv does not hold exactly 18 r rows"
gib=$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); echo "C: free $gib GiB"
[ $gib -ge 15 ] || die "C: below 15 GiB"
TMPR=$(mktemp -d -p /home/dacz8976/relplan)
# the floor, by the rule as corrected after the run (coordinator-080; the night's awk rule missed the official goldfish line):
# games and coverage byte-equal to floor2F, the pages equal after normalising only the engine path and that line
tr -d '\r' < $DAY/floorS_recompare.sh > $TMPR/floorS_recompare.sh
bash $TMPR/floorS_recompare.sh > $TMPR/FLOOR_RECOMPARE.txt 2>&1 || { cat $TMPR/FLOOR_RECOMPARE.txt; die "floor2S v floor2F, the corrected rule: not accepted (output above)"; }
grep -qx 'RESULT: 12 of 12 pieces equal to floor2F under the corrected rule (coordinator-080)' $TMPR/FLOOR_RECOMPARE.txt \
  || die "floorS_recompare.sh did not print the 12-of-12 RESULT line"
[ "$(grep -c '^PASS ' $TMPR/FLOOR_RECOMPARE.txt)" = 12 ] || die "floorS_recompare.sh: not 12 PASS lines"
tail -n 1 $TMPR/FLOOR_RECOMPARE.txt
# S's own goldfish on the 11 floor decks (the floor took coverage from the Oct 21 official goldfish; the refuters' gap)
tr -d '\r' < $DAY/goldfishS_floor_coverage.sh > $TMPR/goldfishS_floor_coverage.sh
GF_OUT=$TMPR/gfcov bash $TMPR/goldfishS_floor_coverage.sh > $TMPR/GOLDFISH_S_COVERAGE.txt 2>&1 \
  || { cat $TMPR/GOLDFISH_S_COVERAGE.txt; die "S's goldfish does not give byte-equal coverage on the 11 floor decks (output above)"; }
grep -qx "RESULT: S's goldfish gives byte-equal coverage on 11 of 11 floor decks" $TMPR/GOLDFISH_S_COVERAGE.txt || die "goldfishS_floor_coverage.sh: no 11-of-11 line"
tail -n 1 $TMPR/GOLDFISH_S_COVERAGE.txt

# the programs that ran = the programs to commit (coordinator-076, condition of the build-identity wording)
python3 -I - $PG $GM/r $W/floor2S $N/night.log $P $TMPR/RAN_SHA256.txt <<'EOF' || die "a program that ran is not the program to commit (RAN_SHA256.txt above)"
import hashlib, json, re, sys
from pathlib import Path
PG, RR, F2S, NIGHT, P, OUT = map(Path, sys.argv[1:7])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
progs = {n: sha(PG / n) for n in ('deckgym', 'legality_scan', 'goldfish')}
built = {l.split()[1]: l.split()[0] for l in (PG / 'SHA256SUMS').read_text().splitlines()}
lines = ['# The programs that actually ran, by sha256, against the programs committed in programs_final/ (copied from',
         '# /home/dacz8976/pincand_work/programs/R, the build of S). Every line must say EQUAL.']
bad = []
def eq(what, got, want):
    lines.append(f"{'EQUAL  ' if got == want else 'DIFFERS'} {what}: {got}" + ('' if got == want else f' (want {want})'))
    if got != want:
        bad.append(what)
for n, s in progs.items():
    eq(f'programs/R/{n} now v its build-time SHA256SUMS line', s, built.get(n))
cmds = sorted(RR.glob('*.cmd'))
if len(cmds) != 18:
    bad.append(f'{len(cmds)} replay .cmd files, not 18')
for c in cmds:
    t = c.read_text()
    m = re.search(r'/programs/R/(deckgym|legality_scan|goldfish)\b', t); s = re.search(r'^program sha256 ([0-9a-f]{64})$', t, re.M)
    if not m or not s:
        bad.append(f'replay {c.stem}: no programs/R program or "program sha256" line'); continue
    eq(f'replay {c.stem} ran programs/R/{m.group(1)}', s.group(1), progs[m.group(1)])
night = NIGHT.read_text(errors='replace')
m = re.search(r"floorS: floor2\.py on S's deckgym \(([0-9a-f]{64})\)", night)
eq("the floor's deckgym (night.log, floorS line)", m.group(1) if m else 'none', progs['deckgym'])
pieces = sorted(p for p in F2S.iterdir() if p.is_dir() and p.name != '_ref_stripped')
if len(pieces) != 12:
    bad.append(f'{len(pieces)} floor pieces, not 12')
for p in pieces:
    m = re.search(r'/programs/R/deckgym ([0-9a-f]{64})', (p / 'cmd.txt').read_text())
    eq(f'floor piece {p.name} (cmd.txt) ran programs/R/deckgym', m.group(1) if m else 'none', progs['deckgym'])
m = re.search(r'strength: build\.sh \S+ -> (\S+) ', night)
eq('the program night_r6.sh built and self-checked (night.log)', m.group(1) if m else 'none', str(P))
sp = sha(P); bj = json.loads(Path(str(P) + '.build.json').read_text())
eq(f'{P} (the self-checks) v its build record strength.build.json', sp, bj.get('program_sha256'))
m = re.search(r'strength rc=0 in \d+ s; RECORD OK ([0-9a-f]{64})', night)
eq(f'{P} v night.log\'s strength line', sp, m.group(1) if m else 'none')
OUT.write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
if bad:
    print('NOT EQUAL:', bad)
    sys.exit(1)
EOF

# the checkout the floor and the replays read, and the tools they ran (coordinator-076: recorded; the code must be S's)
{ echo "The floor re-check (floor2.py) and the 18 replays (replay3.py) ran S's programs (/home/dacz8976/pincand_work/programs/R) and"
  echo "read decks, pairs files and the Python runners from /home/dacz8976/pincand, the laptop's main checkout (not origin/main)."
  echo "pincand: branch $(git -C $REPO rev-parse --abbrev-ref HEAD), HEAD $(git -C $REPO rev-parse HEAD)"
  echo "Each file: its blob at pincand's HEAD v at S, and pincand's working tree v its HEAD."
} > $TMPR/RUN_CONTEXT.txt
codebad=0
for f in decks/screen/floor.py decks/screen/run_screen.py current_engine.py lib/deck_check.py \
         rl/results/engine_switch_rules2_2026-10/floor_with.py rl/results/engine_switch_rules2_2026-10/sitting1_check.py \
         rl/results/engine_switch_rules2_2026-10/switch_check.py rl/results/engine_switch_2026-09-30/screen_with.py lib/deckgym-database.json; do
  a=$(git -C $REPO rev-parse HEAD:$f); b=$(git rev-parse $S:$f)
  if git -C $REPO diff --quiet HEAD -- $f; then t=clean; else t=MODIFIED; fi
  if [ $a = $b ]; then e=EQUAL; else e=DIFFERS; fi
  note=; [ $f = lib/deckgym-database.json ] && note=" (the pre-R5 copy is expected here: the replayed decks hold old cards only)"
  echo "$f: pincand HEAD ${a:0:12}, S ${b:0:12}: $e; working tree $t$note" >> $TMPR/RUN_CONTEXT.txt
  if [ $t = MODIFIED ] || { [ $e = DIFFERS ] && [ $f != lib/deckgym-database.json ]; }; then codebad=1; fi
done
for pair in "$W/floor2.py:rl/results/engine_candidate_2026-10-20/release/tools/floor2.py" \
            "/home/dacz8976/df0tools/gencmp.py:rl/results/dual_type_seam_2026-10-23/tools/gencmp.py"; do
  f=${pair%%:*}; c=${pair##*:}
  if cmp -s $f <(git show $S:$c); then echo "$f as run: byte-equal to the committed $c" >> $TMPR/RUN_CONTEXT.txt
  else echo "$f as run: NOT equal to the committed $c; the copy as run is in tools/" >> $TMPR/RUN_CONTEXT.txt; echo $f >> $TMPR/copy_tools; fi
done
echo "replay3.py as run: tools/replay3.py (the committed copy plus side r: W/RR, programs/R)." >> $TMPR/RUN_CONTEXT.txt
cat $TMPR/RUN_CONTEXT.txt
[ $codebad = 0 ] || die "a runner the floor or the replays used differs from S's, or pincand's working tree changed it (RUN_CONTEXT above)"

# ---- the programs --------------------------------------------------------------------------------------------------------
CREATED=1; mkdir -p $PF
for n in deckgym legality_scan goldfish; do cp $PG/$n $PF/; done
chmod 755 $PF/deckgym $PF/legality_scan $PF/goldfish
for n in deckgym legality_scan goldfish; do grep -E "^[0-9a-f]{64}  $n\$" $PG/SHA256SUMS || die "no $n line in programs/R/SHA256SUMS"; done > $PF/SHA256SUMS
[ "$(wc -l < $PF/SHA256SUMS)" = 3 ] || die "programs/R/SHA256SUMS does not have one line for each of the three"
cp $PG/SOURCE_COMMIT $PF/
{ cat $TMPR/RAN_SHA256.txt; echo "programs_final/ (the copies to commit): sha256sum -c SHA256SUMS:"; (cd $PF && sha256sum -c SHA256SUMS); } > $D/RAN_SHA256.txt \
  || die "programs_final/ is not programs/R"
echo "RESULT: all equal" >> $D/RAN_SHA256.txt
cp $TMPR/RUN_CONTEXT.txt $D/RUN_CONTEXT.txt

# ---- the logs ------------------------------------------------------------------------------------------------------------
mkdir -p $L/replays_S $L/floor_recheck_S $D/tools
for f in build_R.log suite_R.log status_R.txt card_status.json card_status.err lane_r.log replays.log R_COMMIT gen_ids.err gen_database.err; do
  cp $PR/$f $L/; done
if [ "${GEN_FILES:-hashes}" = full ]; then cp $PR/gen_ids.rs $PR/gen_database.rs $L/
else (cd $PR && sha256sum gen_ids.rs gen_database.rs) > $L/gen_outputs.sha256; fi
for f in night.log switch_.log switch_DECKGYM_FLAT_RETURN_DAMAGE.log switch_DECKGYM_ROUND2_OFF.log switch_core.log strength_K.log \
         sc_km3.out sc_kx3.out sc_kx3.rc floorS.log strength_refusal.log strength_py.log lane_S.verdict; do cp $N/$f $L/; done
(cd $N && ls *.done *.FAILED 2>/dev/null || true) | grep -v '^suite_I11\.' > $L/night_markers.txt || true
cp $PG/SHA256SUMS $L/programs_R_SHA256SUMS
cp $P.build.json $L/strength.build.json
{ git log -1 --format='commit %H%nparents %P%ndate %cI%n%n%B' $K; echo "engine tree $(git rev-parse $K:engine)"
  echo "S v K:"; git diff --name-status $S $K; echo "local branch: $(git branch --list --format='%(refname:short) %(objectname:short)' $KBR)"
} > $L/K_overlay.txt
for f in $GM/r/*; do [ -f "$f" ] || continue; case "$f" in *.jsonl|*_coverage.json) ;; *) cp "$f" $L/replays_S/;; esac; done
grep -P '^r\t' $GM/summary.tsv > $L/replays_S/summary_r.tsv
(cd $GM/r && sha256sum *.jsonl *_coverage.json) > $L/replays_S/outputs.sha256
for p in $W/floor2S/*/; do
  piece=$(basename $p); [ "$piece" = _ref_stripped ] && continue
  mkdir -p $L/floor_recheck_S/$piece
  for f in $p*.md $p/cmd.txt $p/cmp*.txt $p/run.log $p/run_screen.txt; do if [ -e "$f" ]; then cp "$f" $L/floor_recheck_S/$piece/; fi; done
done
cp $W/floor2S/summary.tsv $L/floor_recheck_S/
(cd $W/floor2S && find . -type f ! -path './_ref_stripped/*' | sort | xargs sha256sum) > $L/floor_recheck_S/outputs.sha256
cp $TMPR/FLOOR_RECOMPARE.txt $L/floor_recheck_S/RECOMPARE.txt
cp $TMPR/GOLDFISH_S_COVERAGE.txt $L/floor_recheck_S/GOLDFISH_S_COVERAGE.txt
cp $N/floorS.FAILED $L/floorS.FAILED.txt; cp $N/floorS.done $L/floorS.done.txt

# ---- the tools -----------------------------------------------------------------------------------------------------------
for f in night_r6.sh lane_s.sh mk_ks.sh replay3.py; do cp $W/hb/$f $D/tools/; done
if [ -e $TMPR/copy_tools ]; then for f in $(cat $TMPR/copy_tools); do cp $f $D/tools/; done; fi
for f in commit_record_r6.sh adopt_r6.py verify_r6.sh README_engine_2026-10-29.md floorS_recompare.sh goldfishS_floor_coverage.sh; do tr -d '\r' < $DAY/$f > $D/tools/$f; done
{ echo "The tools as run on the laptop (copied byte for byte) and the day scripts (CR removed). sha256 of each:"
  (cd $D/tools && sha256sum $(ls | grep -vx TOOLS.txt))
  echo "Which runners were byte-equal to S's or to the committed copies: ../RUN_CONTEXT.txt."
  echo "lane_s.sh is lane_r.sh v3 (rl/results/dual_type_seam_2026-10-23/tools/lane_r.sh) with WT=/home/dacz8976/r6s_w; replay3.py adds side r (W/RR, programs/R) to the committed copy."
  echo "floorS_recompare.sh: the floor's acceptance rule as corrected after the run (coordinator-080); its output is ../logs/floor_recheck_S/RECOMPARE.txt."
  echo "goldfishS_floor_coverage.sh: S's own goldfish on the 11 floor decks, coverage only (no games); output ../logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt."
} > $D/tools/TOOLS.txt

# ---- the tables and record.json (what adopt_r6.py reads), then Guardrail B on every expected verdict --------------------------
python3 -I - $D $S "$(git rev-parse $S:engine)" $K "$(git rev-parse $K:engine)" "$(git -C $REPO rev-parse HEAD)" \
            "$(git -C $REPO rev-parse --abbrev-ref HEAD)" $gib <<'EOF'
import importlib.util, json, re, sys
from pathlib import Path
D, S, STREE, K, KTREE, PHEAD, PBRANCH, GIB = sys.argv[1:]
RECOMP = Path(D) / 'logs/floor_recheck_S/RECOMPARE.txt'
D = Path(D); L = D / 'logs'; W = Path('/home/dacz8976/pincand_work')
def need(m, what):
    if not m:
        sys.exit(f'record.json: no {what}')
    return m
night = (L / 'night.log').read_text(errors='replace'); lane = (L / 'lane_r.log').read_text(errors='replace')
rec = dict(schema='r6-record v1', s=S, s_engine_tree=STREE, k=K, k_engine_tree=KTREE)
rec['programs_sha256'] = {l.split()[1]: l.split()[0] for l in (D / 'programs_final/SHA256SUMS').read_text().splitlines()}
rec['programs_R_sha256_all'] = {l.split()[1]: l.split()[0] for l in (L / 'programs_R_SHA256SUMS').read_text().splitlines()}
rec['ran_sha256'] = 'all equal (RAN_SHA256.txt)' if (D / 'RAN_SHA256.txt').read_text().rstrip().endswith('RESULT: all equal') else 'NOT EQUAL'
m1 = need(re.search(r'^(\S+) lane_r start: R=' + S + '$', lane, re.M), 'lane_r start line')
m2 = need(re.search(r'^(\S+) build_R OK: BUILD OK in (\d+) s$', lane, re.M), 'build_R OK line')
rec['build'] = dict(lane_start=m1.group(1), build_ok_at=m2.group(1), secs=int(m2.group(2)))
rec['gencmp'] = {k: need(re.search(r'gen_R ' + k + r': (\S+) ', lane), 'gencmp ' + k).group(1) for k in ('ids', 'database')}
st = (L / 'status_R.txt').read_text()
rec['card_status'] = dict(line=need(re.search(r'^card_status: all .*$', st, re.M), 'card_status line').group(0),
                          older=need(re.search(r'^older cards neither Complete nor RulesUnverified: (\d+)', st, re.M), 'older').group(1),
                          check=need(re.search(r'^STATUS_CHECK (\S+)', st, re.M), 'STATUS_CHECK').group(1))
m = need(re.search(r'suite_R rc=(\d+) in (\d+) s: passed (\d+) failed (\d+) ignored (\d+) compile_errors (\d+)', lane), 'suite line')
rec['suite'] = dict(rc=int(m.group(1)), secs=int(m.group(2)), passed=int(m.group(3)), failed=int(m.group(4)), ignored=int(m.group(5)), compile_errors=int(m.group(6)))
sw = {}
for key, pat in (('default', r'switch runs \[default\] files: passed (\d+) failed (\d+)'),
                 ('DECKGYM_FLAT_RETURN_DAMAGE', r'switch runs \[DECKGYM_FLAT_RETURN_DAMAGE=1\] files: passed (\d+) failed (\d+)'),
                 ('DECKGYM_ROUND2_OFF', r'switch runs \[DECKGYM_ROUND2_OFF=1\] files: passed (\d+) failed (\d+)'),
                 ('core_ROUND2_OFF', r'switch runs \[ROUND2_OFF\] core module: passed (\d+) failed (\d+)')):
    m = need(re.search(pat, night), 'switch runs ' + key); sw[key] = [int(m.group(1)), int(m.group(2))]
rec['switch_runs'] = sw
m = need(re.search(r'strength rc=0 in (\d+) s; RECORD OK ([0-9a-f]{64})', night), 'strength build line')
bj = json.loads((L / 'strength.build.json').read_text())
rec['strength'] = dict(program='/home/dacz8976/kx_r4/strength', sha256=m.group(2), secs=int(m.group(1)), engine_ref=bj['engine_ref'],
                       engine_tree_archived=bj['engine_tree_archived'], harness=bj['harness_source_sha256'], jobs=bj['jobs'])
kxrc = (L / 'sc_kx3.rc').read_text().split()
rec['selfchecks'] = dict(km3=(L / 'sc_km3.out').read_text().strip(), kx3=(L / 'sc_kx3.out').read_text().strip(), kx3_rc=int(kxrc[0]), kx3_secs=int(kxrc[1]))
ref = (L / 'strength_refusal.log').read_text(errors='replace')
rec['refusal_test'] = dict(ran=int(need(re.search(r'^Ran (\d+) tests?', ref, re.M), 'refusal Ran').group(1)),
                           status=need(re.search(r'^(OK.*|FAILED.*)$', ref, re.M), 'refusal status').group(1))
py = (L / 'strength_py.log').read_text(errors='replace')
rec['strength_py'] = dict(ran=int(need(re.search(r'^Ran (\d+) tests?', py, re.M), 'py Ran').group(1)),
                          status=need(re.search(r'^(OK.*|FAILED.*)$', py, re.M), 'py status').group(1),
                          failing=sorted(set(re.findall(r'^((?:FAIL|ERROR): \S+ \([^)]*\))', py, re.M))))
# the 18 replays (side r = S's programs; "v f" = main-4d48844's games)
GROWL = {'08a9b3a_new17_k3': '8 differing deals of 8500', '08a9b3a_dev_km3_new17': '7 differing deals of 8500', '08a9b3a_8_new_km3': '1 differing deals of 16000'}
rows, trows = [], []
for line in (L / 'replays_S/summary_r.tsv').read_text().splitlines():
    side, name, games, secs, verdict, detail = (line.split('\t') + [''] * 6)[:6]
    vf = re.search(r'\| v f: (SAME|DIFFERS|ERROR)(?: \((\d+) deals\))?', detail)
    r = dict(name=name, games=int(games), secs=int(secs), verdict=verdict, detail=detail,
             vf=vf.group(1) if vf else None, vf_deals=int(vf.group(2)) if vf and vf.group(2) else None,
             growl_known=(verdict == 'DIFFERS' and name in GROWL and detail.startswith(GROWL[name] + ' ')),
             rules_clean=bool(re.search(r'rules page: .*: no RULE finding$', detail)))
    rows.append(r)
    head = detail.split(' | ')[0].split('; rules page')[0]
    if name.endswith('_goldfish'):
        vref, vfx = f'{verdict}: {head}', 'not compared (plays no games)'
    else:
        vref, vfx = f'{verdict}: {head}', (f"{r['vf']}" + (f" ({r['vf_deals']} deals)" if r['vf_deals'] is not None else '')) if r['vf'] else 'none'
    trows.append(f"| `{name}` | {int(games):,} | {vref} | {vfx} |")
rep = dict(rows=rows, n=len(rows), games_total=sum(r['games'] for r in rows),
           vf_same=sum(r['vf'] == 'SAME' for r in rows), vf_same_zero=sum(r['vf'] == 'SAME' and r['vf_deals'] == 0 for r in rows),
           vf_other=sum(r['vf'] in ('DIFFERS', 'ERROR') for r in rows),
           ref_same=sum(r['verdict'] == 'SAME' for r in rows), ref_growl_known=sum(r['growl_known'] for r in rows),
           rules_clean=sum(r['rules_clean'] for r in rows),
           goldfish=next((r['detail'] for r in rows if r['name'].endswith('_goldfish')), None),
           run_screen=next((r['detail'] for r in rows if r['name'].endswith('_run_screen')), None))
rec['replays'] = rep
(D / 'REPLAY_TABLE.md').write_text(
    '| Run (replayed command) | Games or deals | v the 08a9b3a reference | v main-4d48844 (side f, Oct 21) |\n|---|---|---|---|\n'
    + '\n'.join(trows) + '\n', encoding='utf-8')
# the floor re-check (floor_table2.py's reading, for S): S v the recorded page, and v main-4d48844's final page (floor2F)
spec = importlib.util.spec_from_file_location('floor2', W / 'floor2.py'); F2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(F2)
VERD = re.compile(r'^\*\*Verdict: (.+?)\*\* (\d+) wins in (\d+) games', re.M)
def verdict(md):
    md = Path(md)
    if not md.exists():
        return '?'
    t = md.read_text(encoding='utf-8'); m = VERD.search(t)
    if m:
        return f'{m.group(1).rstrip(".")}, {int(m.group(2)):,} of {int(m.group(3)):,}'
    m = re.search(r'(\d+) wins in (\d+) games', t)
    return f'{int(m.group(1)):,} of {int(m.group(2)):,} wins' if m else '?'
def summ(folder):
    p = W / folder / 'summary.tsv'
    return {l.split('\t')[0]: (l.rstrip('\n').split('\t') + [''] * 5)[:5] for l in p.read_text().splitlines() if l} if p.exists() else {}
SS, FF = summ('floor2S'), summ('floor2F')
# the corrected rule (coordinator-080): floorS_recompare.sh's PASS lines decide "equal to main-4d48844's final page"; floor2.py's
# own SAME/DIFFERS v the recorded page and v floor2F is kept in the table as it ran (its DIFFERS is the goldfish line alone)
rc_txt = RECOMP.read_text(encoding='utf-8')
RPASS = set(re.findall(r'^PASS (\S+):', rc_txt, re.M))
if not re.search(r'^RESULT: 12 of 12 pieces equal to floor2F under the corrected rule \(coordinator-080\)$', rc_txt, re.M):
    sys.exit('record.json: RECOMPARE.txt has no 12-of-12 RESULT line')
fl = dict(n=0, equal_recorded=[], equal_final_only={}, other=[], games=0, recompare_pass=sorted(RPASS),
          rule=('corrected after the run (coordinator-080): games and coverage byte-equal to floor2F (main-4d48844 final, Oct 21 UTC), '
                'pages equal after normalising only the engine path and the official goldfish line; games unchanged, not re-run'),
          night_rule_failed='floorS.FAILED kept: the night rule (SAME, or DIFFERS and "v floor2F: exit 0") missed the goldfish line',
          goldfish_S_coverage=len(re.findall(r'^EQUAL \S+: rc 0, coverage byte-equal to floor2S',
                                             (Path(D) / 'logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt').read_text(encoding='utf-8'), re.M)))
frows = []
for piece, (kind, deck, extra, ref_, name) in F2.PIECES.items():
    s, f = SS.get(piece), FF.get(piece)
    sv = s[3] if s else 'not run'; det = s[4] if s else ''
    fl['n'] += 1; fl['games'] += int(s[1] or 0) if s else 0
    if kind == 'screen':
        old, fw, sw_ = 'run_screen, 20 lines', (f[3] if f else 'not run'), f'{sv} (floor2.py)'
    else:
        refmd = (F2.REF / 'pages' / ref_.split(':', 1)[1] / f'{name}.md') if isinstance(ref_, str) and ref_.startswith('STRIP:') else Path(ref_) / f'{name}.md'
        old = verdict(refmd)
        fw = f'{f[3] if f else "not run"}: {verdict(W / "floor2F" / piece / f"{name}.md")}'
        sw_ = f'{sv} (floor2.py): {verdict(W / "floor2S" / piece / f"{name}.md")}'
    if piece in RPASS and f and f[3] == 'SAME':
        fl['equal_recorded'].append(piece)
        vfin = 'equal (games, coverage byte-equal; page apart from the program lines): it equals the recorded page as main-4d48844\'s did'
    elif piece in RPASS and f and f[3] == 'DIFFERS':
        fl['equal_final_only'][piece] = verdict(W / 'floor2S' / piece / f'{name}.md')
        vfin = 'equal (games, coverage byte-equal; page apart from the program lines): it differs from the recorded page as main-4d48844\'s did'
    else:
        fl['other'].append(piece); vfin = 'NOT equal, or main-4d48844\'s verdict unknown: ' + det[:120].replace('|', '/')
    frows.append(f'| {piece} | {old} | {fw} | {sw_} | {vfin} |')
rec['floor'] = fl
(D / 'FLOOR_TABLE.md').write_text(
    '| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | main-4d48844 final build v recorded (floor2F, Oct 21 UTC) | S v recorded, as floor2.py said | S v main-4d48844 final page (floorS_recompare.sh) |\n'
    '|---|---|---|---|---|\n' + '\n'.join(frows) + '\n\n'
    'floor2.py says DIFFERS for 11 pieces for one line only: the coverage line names the official goldfish, '
    '`rl/engine-2026-10-21/goldfish` that night (sha256 db52d3de…) where main-4d48844\'s final pages name `rl/engine-2026-10-12/goldfish` '
    '(d8cfb779…); the release moved with the Oct 21 adoption, after those pages were made. The coverage files themselves are byte-equal. The night\'s acceptance '
    'rule did not allow for that line and wrote floorS.FAILED (kept, `logs/floorS.FAILED.txt`). The rule was corrected after the run, '
    'with the games unchanged and not re-run, and reviewed by the coordinator (coordinator-080): games and coverage byte-equal to '
    'main-4d48844\'s final pages, and each page equal after normalising only the engine path and that goldfish line '
    '(`tools/floorS_recompare.sh`, output `logs/floor_recheck_S/RECOMPARE.txt`, `logs/floorS.done.txt`). The project\'s own '
    'comparators agree (sitting1_check.py floor --allow-coverage-program and switch_check.py screen, S v main-4d48844: exit 0). '
    'S\'s own goldfish, run on the 11 floor decks as floor.py runs it (coverage only, no games), gives coverage files byte-equal '
    'to these (`tools/goldfishS_floor_coverage.sh`, `logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt`).\n', encoding='utf-8')
rec['floor_ran_from'] = dict(repo='/home/dacz8976/pincand', branch=PBRANCH, head_at_record_time=PHEAD,
                             note='floor2.py and replay3.py read decks, pairs files and the Python runners from this checkout; RUN_CONTEXT.txt')
rec['c_free_gib_at_record'] = int(GIB)
(D / 'record.json').write_text(json.dumps(rec, indent=1) + '\n', encoding='utf-8')
print('replays:', {k: v for k, v in rep.items() if k != 'rows'})
print('floor:', fl)
# Guardrail B: the expected verdicts (the same ones adopt_r6.py requires); any miss refuses, and the trap removes the record
CARD = ("card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 205, 'MissingAbility': 15, 'MissingAttack': 31, "
        "'MissingTool': 2, 'MissingTrainer': 7}")
HARN_FAIL = re.compile(r'^FAIL: test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on '
                       r'\(test_slow_report_registration\.CommittedPin[.)]')
pyf = rec['strength_py']['failing']
miss = [what for what, ok in (
    ('the programs that ran are the committed ones', rec['ran_sha256'].startswith('all equal')),
    ('gencmp SAME, SAME', rec['gencmp'] == {'ids': 'SAME', 'database': 'SAME'}),
    ("card_status as on Oct 28, older 0, STATUS_CHECK OK", rec['card_status'] == dict(line=CARD, older='0', check='OK')),
    ('the suite: rc 0, 0 failed, 0 ignored, 0 compile errors', (rec['suite']['rc'], rec['suite']['failed'], rec['suite']['ignored'], rec['suite']['compile_errors']) == (0, 0, 0, 0)),
    ('the switch runs 32, 32, 32 and 14, 0 failed', [sw[k] for k in ('default', 'DECKGYM_FLAT_RETURN_DAMAGE', 'DECKGYM_ROUND2_OFF', 'core_ROUND2_OFF')] == [[32, 0]] * 3 + [[14, 0]]),
    ('the self-checks equal the pin, kx3 rc 0', rec['selfchecks']['kx3_rc'] == 0),
    ('the refusal test: 4 tests, OK', (rec['refusal_test']['ran'], rec['refusal_test']['status']) == (4, 'OK')),
    ("the rl/strength suite: only CommittedPin's harness test fails", len(pyf) == 1 and bool(HARN_FAIL.match(pyf[0]))
     and bool(re.fullmatch(r'FAILED \(failures=1(, skipped=\d+)?\)', rec['strength_py']['status']))),
    ('the replays: 18 rows, 17 v f SAME, 0 v f DIFFERS/ERROR, 15 SAME + the 3 known Growl rows, 11 clean rules pages, goldfish page and coverage =',
     (rep['n'], rep['vf_same'], rep['vf_other'], rep['ref_growl_known'], rep['ref_same'], rep['rules_clean']) == (18, 17, 0, 3, 15, 11)
     and rep['goldfish'] == 'page =, coverage ='),
    ("the floor: 12 pieces, each equal to main-4d48844's final page (the corrected rule, coordinator-080)", fl['n'] == 12 and not fl['other']
     and len(fl['equal_recorded']) + len(fl['equal_final_only']) == 12 and len(fl['recompare_pass']) == 12
     and sorted(fl['equal_final_only']) == ['B_brew-07', 'B_brew-09']),
    ("S's own goldfish: byte-equal coverage on the 11 floor decks", fl['goldfish_S_coverage'] == 11),
    ('the build ran on the folder date 2026-10-29 (UTC)', rec['build']['lane_start'][:10] == rec['build']['build_ok_at'][:10] == '2026-10-29'),
) if not ok]
if miss:
    print('Guardrail B: expected verdicts NOT met (bring the night\'s record to the coordinator; nothing is committed):')
    for x in miss:
        print('  -', x)
    sys.exit(1)
print('Guardrail B: every expected verdict met')
EOF

# ---- stage, check the modes, commit --------------------------------------------------------------------------------------
git add $REC
git update-index --chmod=+x $REC/programs_final/deckgym $REC/programs_final/legality_scan $REC/programs_final/goldfish
[ -z "$(git diff --cached --name-only | grep -v "^$REC/")" ] || die "something outside $REC is staged"
git ls-files -s $REC/programs_final
for n in deckgym legality_scan goldfish; do
  set -- $(git ls-files -s $REC/programs_final/$n)
  [ "$1" = 100755 ] || die "$n is staged as $1, not 100755"
  [ "$2" = "$(git hash-object $PF/$n)" ] || die "$n: the staged blob is not the file"
done
for n in SHA256SUMS SOURCE_COMMIT; do [ "$(git ls-files -s $REC/programs_final/$n | cut -c1-6)" = 100644 ] || die "$n mode"; done
echo "staged: $(git diff --cached --name-only | wc -l) files; $(du -sh $D | cut -f1) on disk"
SUITE=$(python3 -I -c "import json,sys; r=json.load(open(sys.argv[1])); print(r['suite']['passed'])" $D/record.json)
$G commit -q -F - <<EOF
R6 build record: the official programs built from S (${S:0:8}) and the night's checks

- r6_release/programs_final/: deckgym, legality_scan and goldfish, built once from ${S:0:8} (engine tree
  $(git rev-parse $S:engine | cut -c1-12)) in the clean worktree r6s_w with the shared target dual_target at CARGO_BUILD_JOBS 2;
  mode 100755. SHA256SUMS (the three), SOURCE_COMMIT.
- r6_release/RAN_SHA256.txt: the programs that ran (the replays' and the floor's programs/R, the self-checks'
  kx_r4/strength) are, by sha256, the committed ones and the recorded build. RUN_CONTEXT.txt: the checkout the
  floor and the replays read and the byte-equality of their runners.
- r6_release/logs/: the lane on S (build, gencmp, card_status, suite $SUITE passed and 0 failed, the 18 identity
  replays v main-4d48844 in replays_S/), the folded hit-back tests under the switches, the floor re-check pages on S's
  deckgym (floor_recheck_S/), kx3's rebuild on K ${K:0:8} (strength.build.json, K_overlay.txt) and both self-checks
  equal to the pin, the card-support refusal test and the rl/strength suite (its one expected failure until the
  re-pin).
- The floor re-check: rule corrected after the run, games unchanged; reviewed by the coordinator (coordinator-080).
  floor2.py said DIFFERS for 11 of 12 pieces, for one line only: the coverage line names the official goldfish
  (rl/engine-2026-10-21 that night, rl/engine-2026-10-12 on main-4d48844's final pages). The night's rule did not allow
  for it (floorS.FAILED, kept). By the corrected rule all 12 pass: games and coverage byte-equal to main-4d48844's
  final pages, each page equal after normalising only the engine path and that line (tools/floorS_recompare.sh,
  logs/floor_recheck_S/RECOMPARE.txt, logs/floorS.done.txt). S's own goldfish gives byte-equal coverage on the
  11 floor decks (tools/goldfishS_floor_coverage.sh, logs/floor_recheck_S/GOLDFISH_S_COVERAGE.txt).
- r6_release/FLOOR_TABLE.md, REPLAY_TABLE.md, record.json: the numbers the adoption draft reads.
- r6_release/tools/: the scripts as run and the day scripts (TOOLS.txt).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
COMMITTED=1

# ---- after the commit ----------------------------------------------------------------------------------------------------
[ "$(git rev-parse HEAD^)" = $S ] || die "the record's parent is not S"
[ "$(git rev-parse HEAD:engine)" = "$(git rev-parse $S:engine)" ] || die "the record changed engine/"
[ -z "$(git diff --name-only $S HEAD | grep -v "^$REC/")" ] || die "the record touches files outside $REC"
[ -z "$(git status --porcelain)" ] || die "the tree is not clean after the commit"
git ls-tree HEAD $REC/programs_final/
git log --oneline -2
echo "RECORD_COMMIT=$(git rev-parse HEAD)"

# ---- push (only with --push): Guardrail A on both, then the record branch and K, to our origin ----------------------------------
# Guardrail A (coordinator-076): the commit's `git show --stat` (with its message), the paths it adds and, for the record, every
# path in r6_release/ must hold none of exam / private-exam / judge / transcript (case-insensitive; "examples", the engine's
# folder, is allowed). Exactly one commit may be new to origin per branch. K's first-parent stat (against 87a7f340) is every
# change main made since Oct 21, all on origin already, so K is checked against S, the engine it lays kx3's six files onto.
guard_a() {  # REV BASE LABEL [RECORD]
  local rev=$1 base=$2 label=$3 f=$TMPR/guard_$3.txt new
  new=$(git rev-list $rev --not --remotes=origin)
  [ "$new" = "$(git rev-parse $rev)" ] || die "Guardrail A: $label would add other commits than $rev to origin: $(echo $new | cut -c1-120)"
  { git log -1 --format='%H%n%B' $rev; git diff --stat $base $rev; git diff --name-only $base $rev; } > $f
  if [ -n "${4:-}" ]; then git show --stat --format='%H%n%B' $rev >> $f; git ls-tree -r --name-only $rev -- $REC >> $f; fi
  local hits; hits=$(grep -inP 'private-exam|exam(?!ples)|judge|transcript' $f || true)
  if [ -n "$hits" ]; then echo "$hits" | head -n 40 >&2; die "Guardrail A: $label holds a forbidden word (lines above); nothing pushed"; fi
  echo "Guardrail A: $label clean ($(grep -c . $f) lines checked)"
}
if [ $PUSH = 1 ]; then
  guard_a HEAD $S record yes
  guard_a $K $S K
  git push -q origin $BR && echo "pushed $BR ($(git rev-parse --short HEAD))"
  git push -q origin $K:refs/heads/$KBR && echo "pushed $KBR (${K:0:8})"
else
  echo "not pushed (pass --push: Guardrail A, then $BR and $KBR to origin)"
fi
