#!/bin/bash
# commit_record_r8.sh [--push]   (R8 switch step 5, plan 113 §5 as amended by 151/152/154/155; adapted from R6's commit_record_r6.sh)
# CHECK=1 commit_record_r8.sh   builds the whole record and runs every check and Guardrail B, then removes it (no commit, no push).
#
# Commits the build record of the R8 tip S8 (543dad00) on the R8 branch in /home/dacz8976/r6v_scratch (results only; engine/ untouched),
# as ONE commit directly on S8 (HEAD must be S8 itself):
#   rl/results/r8_catchup_2026-10-29/r8_release/
#     programs_final/   deckgym, legality_scan, goldfish (100755) from ~/pincand_work/RR_R8_543dad00/programs, SHA256SUMS (the three,
#                       in that order), SOURCE_COMMIT
#     RAN_SHA256.txt    the programs that actually ran (the floor's and the 18 replays' programs, sc_kx3's strength_K8, the refusal
#                       test's tu program) against the committed ones and their build records, by sha256
#     RUN_CONTEXT.txt   the checkouts the floor and the replays read, and the byte-equality of their runners with S8's
#     logs/lane_R/      the official build's lane on S8 (build, gencmp hashes, card_status, lane log, replay log, markers)
#     logs/lane_N/      Lane N on 48dec4f5 (same engine tree, same five programs), cited under Q2 (A) (coordinator-151 §3): its lane log,
#                       suite, goldfish steps, status, VERIFY, night log, sc_km3, the strength_L and strength_K8 build records,
#                       K8_RECORD.union.txt
#     logs/replays_R/   the official build's 18 replays (unplanned; coordinator-155 Q1): small files, rows, games sums, V_LANE_N.txt
#     logs/replays_N/   Lane N's 18 replays' rows and games sums (the basis)
#     logs/switch/      sc_kx3, the K8 record check, the strength tests (K8 and the tu program), tu build log, the floor run's log
#     logs/floor_recheck_R8/  the 12 floor pieces on S8's deckgym, RECOMPARE.txt, GOLDFISH_R8_COVERAGE.txt, FLOOR2S_BASIS.txt
#     tools/            the scripts as run and this one; TOOLS.txt
#     FLOOR_TABLE.md, REPLAY_TABLE.md, record.json   (the numbers the adoption draft reads)
# Guardrail B: any expected verdict not met refuses before committing and removes the partial record. --push: Guardrail A
# (r8_push2.sh: the content grep with the never-open exclusion array from the last pushed tip, 543dad00), then the R8 branch to origin.
set -eu
DAY=${DAY:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/616e3a3e74bcec47/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/sw}
SW=/home/dacz8976/relplan/r8/sw
W=/home/dacz8976/pincand_work; RR=$W/RR_R8_543dad00; LN=$W/RR_R8_48dec4f5; N3=$RR/sw3; PG=$RR/programs; PR=$RR/prep; GM=$RR/games
REPO=/home/dacz8976/pincand; WT=/home/dacz8976/r6v_scratch; LWT=/home/dacz8976/lane_r8_w; BR=laptop/r8-catchup-2026-10-29
KBR=laptop/kx3-on-r8-2026-11-04
S=543dad0007a345128ec95e9c2698699c8b5493ce
LANE=48dec4f5361992b2788401333b2f1cc4531f073a
K=b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0; KX=e3ddc0149bb9d35fda1becbb17ab5f71d9461609
P=$LN/strength/K8/strength; PL=$LN/strength/L/strength; TU=$N3/tu_build/rl/strength/target/release/strength
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
SC_KM3='selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1'
SC_KX3='selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
REC=rl/results/r8_catchup_2026-10-29/r8_release
D=$WT/$REC; PF=$D/programs_final; L=$D/logs
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
PUSH=0; [ "${1:-}" = --push ] && PUSH=1; CHECK=${CHECK:-0}
die() { echo "REFUSED: $*" >&2; exit 1; }
CREATED=0; COMMITTED=0; TMPR=
finish() {
  local rc=$?
  [ -n "$TMPR" ] && rm -rf "$TMPR"
  if [ $CREATED = 1 ] && [ $COMMITTED = 0 ]; then
    cd $WT; git reset -q -- $REC 2>/dev/null || true; rm -rf "$D"
    if [ $rc != 0 ]; then echo "Guardrail B: refused after writing; the partial record $D was removed, nothing was committed or pushed" >&2
    else echo "CHECK=1: the record was built and every check passed; it was removed again (nothing committed)"; fi
  fi
}
trap finish EXIT
TOOLS_RUN='step2_build.sh step3_run.sh tu_build.sh wait34.sh floorR8_recompare.sh goldfishR8_floor_coverage.sh replays_v_laneN.sh floor2s_basis.sh r8_push2.sh'

# ---- guards (nothing is written in the repository before these pass) -----------------------------------------------------
cd $WT
[ "$(git rev-parse --abbrev-ref HEAD)" = $BR ] || die "$WT is not on $BR"
[ "$(git rev-parse HEAD)" = $S ] || die "HEAD is $(git rev-parse --short HEAD), not S8: the record goes directly on S8"
[ -z "$(git status --porcelain)" ] || { git status --short; die "$WT is not clean"; }
[ ! -e $D ] || die "$D exists"
[ "$(git rev-parse $S:engine)" = "$(git rev-parse $LANE:engine)" ] || die "S8's engine/ is not Lane N's (48dec4f5)"
[ "$(git rev-parse HEAD:rl/strength)" = "$(git rev-parse $LANE:rl/strength)" ] || die "rl/strength differs between S8 and 48dec4f5"
[ "$(git -C $LWT rev-parse HEAD)" = $S ] && [ -z "$(git -C $LWT status --porcelain --untracked-files=no)" ] || die "$LWT is not clean at S8"
# the official build's lane on S8
[ -e $PR/lane_r.end ] || die "the official lane has not ended"
for s in build_R gen_R status_R replays_R; do [ -e $PR/$s.done ] || die "lane step $s not done"; [ ! -e $PR/$s.FAILED ] || die "lane step $s FAILED"; done
for s in suite_R goldfish_R; do grep -q 'skipped: Q2 (A), coordinator-151' $PR/$s.done || die "$s.done is not the Q2 (A) skip marker"; done
[ "$(cat $PR/R_COMMIT)" = $S ] || die "prep/R_COMMIT is not S8"
[ "$(cat $PG/SOURCE_COMMIT)" = $S ] || die "programs/ is not S8's build"
# Lane N, the cited basis
[ -e $LN/prep/lane_r.end ] && [ -e $LN/night/night.end ] || die "Lane N has not ended"
for s in build_R gen_R status_R suite_R goldfish_R replays_R; do [ -e $LN/prep/$s.done ] || die "Lane N step $s not done"; [ ! -e $LN/prep/$s.FAILED ] || die "Lane N $s FAILED"; done
[ "$(cat $LN/prep/R_COMMIT)" = $LANE ] || die "Lane N's R_COMMIT is not 48dec4f5"
cmp -s $PG/SHA256SUMS $LN/programs/SHA256SUMS || die "the official build's SHA256SUMS differ from Lane N's: Q2 (A) does not hold, run (B)"
(cd $PG && sha256sum -c --quiet SHA256SUMS) || die "programs/ do not match their SHA256SUMS"
grep -qx 'VERIFY PASS' $LN/verify/VERIFY.txt || die "Lane N's VERIFY is not PASS"
[ "$(cat $LN/night/sc_km3.out)" = "$SC_KM3" ] || die "Lane N's sc_km3 differs from the pin text: STOP"
# the switch's checks (sw3)
[ "$(cat $N3/sc_kx3.out)" = "$SC_KX3" ] || die "sc_kx3 differs from the pin text: STOP (coordinator; new texts need Dustin)"
[ "$(cut -d' ' -f1 $N3/sc_kx3.rc)" = 0 ] || die "sc_kx3 rc is not 0"
[ "$(cut -d' ' -f1 $N3/floor.rc)" = 0 ] || die "floor2.py rc is not 0"
grep -q '^RECORD OK ' $N3/record_check.txt || die "the K8 record check is not RECORD OK"
[ -x $P ] && [ -e $P.build.json ] && [ -x $PL ] && [ -e $PL.build.json ] && [ -x $TU ] || die "a strength program or its build record is missing"
[ "$(git rev-parse $K^1) $(git rev-parse $K^2)" = "$LANE $KX" ] || die "K8's parents are not 48dec4f5 and e3ddc014"
K6='engine/examples/playout_smoke.rs engine/src/players/mod.rs engine/src/players/playout_player.rs engine/src/players/playout_pool.rs engine/tests/playout_pilot_extra_lists_test.rs engine/tests/playout_pilot_test.rs'
[ "$(git diff --name-only $LANE $K | tr '\n' ' ' | sed 's/ $//')" = "$K6" ] || die "K8 differs from 48dec4f5 in other than kx3's six files"
[ "$(timeout 120 git ls-remote origin refs/heads/$KBR | cut -f1)" = $K ] || die "K8 is not on origin (ls-remote)"
cmp -s <(tr -d '\r' < $DAY/commit_record_r8.sh) "${BASH_SOURCE[0]}" || die "the running script is not the day copy $DAY/commit_record_r8.sh"
for f in tu_build.out tu_build.log; do [ -e $N3/$f ] || die "missing $N3/$f"; done
python3 -I - $P $K "$(git rev-parse $K:engine)" $HARN <<'EOF' || die "the strength_K8 build record does not match"
import hashlib, json, sys
p, k, t, h = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2')
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
if hashlib.sha256(open(p, 'rb').read()).hexdigest() != r.get('program_sha256'):
    bad['program_sha256'] = 'the program is not the recorded one'
sys.exit('build record: %r' % bad if bad else 0)
EOF
for f in $TOOLS_RUN; do [ -e $SW/$f ] || die "missing $SW/$f"; done
[ -e $DAY/commit_record_r8.sh ] || die "missing $DAY/commit_record_r8.sh"
[ "$(grep -cP '^r\t' $GM/summary.tsv)" = 18 ] && [ "$(grep -cP '^r\t' $LN/games/summary.tsv)" = 18 ] || die "not 18 r rows on both lanes"
gib=$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 )); echo "C: free $gib GiB"
[ $gib -ge 15 ] || die "C: below 15 GiB"
TMPR=$(mktemp -d -p /home/dacz8976/relplan)

# ---- the read-only checks the record rests on (each re-run here, its output saved) ------------------------------------------
bash $SW/floorR8_recompare.sh > $TMPR/RECOMPARE.txt 2>&1 || { cat $TMPR/RECOMPARE.txt; die "floor2R8 v floor2S: not accepted"; }
grep -qx 'RESULT: 12 of 12 pieces equal to floor2S under the corrected rule (coordinator-080; engine path only)' $TMPR/RECOMPARE.txt || die "no 12-of-12 RESULT line"
[ "$(grep -c '^PASS ' $TMPR/RECOMPARE.txt)" = 12 ] || die "floorR8_recompare.sh: not 12 PASS lines"
GF_OUT=$TMPR/gfcov bash $SW/goldfishR8_floor_coverage.sh > $TMPR/GOLDFISH_R8_COVERAGE.txt 2>&1 || { cat $TMPR/GOLDFISH_R8_COVERAGE.txt; die "R8's goldfish: coverage not byte-equal"; }
grep -qx "RESULT: R8's goldfish gives byte-equal coverage on 11 of 11 floor decks" $TMPR/GOLDFISH_R8_COVERAGE.txt || die "goldfish coverage: no 11-of-11 line"
bash $SW/floor2s_basis.sh > $TMPR/FLOOR2S_BASIS.txt 2>&1 || { tail -n 3 $TMPR/FLOOR2S_BASIS.txt; die "floor2S is not as committed (151 Q3)"; }
bash $SW/replays_v_laneN.sh > $TMPR/V_LANE_N.txt 2>&1 || { cat $TMPR/V_LANE_N.txt; die "the official build's replays do not equal Lane N's"; }
for f in RECOMPARE GOLDFISH_R8_COVERAGE FLOOR2S_BASIS V_LANE_N; do tail -n 1 $TMPR/$f.txt; done

# ---- the programs that ran = the programs to commit --------------------------------------------------------------------------
python3 -I - $PG $GM/r $W/floor2R8 $N3 $P $PL $TU $LN $TMPR/RAN_SHA256.txt <<'EOF' || die "a program that ran is not the program to commit (RAN_SHA256.txt above)"
import hashlib, json, re, sys
from pathlib import Path
PG, RR, F2, N3, P, PL, TU, LN, OUT = map(Path, sys.argv[1:10])
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
built = {l.split()[1]: l.split()[0] for l in (PG / 'SHA256SUMS').read_text().splitlines()}
progs = {n: sha(PG / n) for n in ('deckgym', 'legality_scan', 'goldfish', 'card_status', 'card_enum_generator')}
lines = ['# The programs that actually ran, by sha256, against the programs committed in programs_final/ (copied from',
         '# /home/dacz8976/pincand_work/RR_R8_543dad00/programs, the official build of S8 543dad00) and the recorded builds.',
         '# Every line must say EQUAL.']
bad = []
def eq(what, got, want):
    lines.append(f"{'EQUAL  ' if got == want else 'DIFFERS'} {what}: {got}" + ('' if got == want else f' (want {want})'))
    if got != want:
        bad.append(what)
for n, s in progs.items():
    eq(f'programs/{n} now v its build-time SHA256SUMS line', s, built.get(n))
lnb = {l.split()[1]: l.split()[0] for l in (LN / 'programs/SHA256SUMS').read_text().splitlines()}
for n in progs:
    eq(f"programs/{n} v Lane N's build (48dec4f5, the cited basis)", progs[n], lnb.get(n))
cmds = sorted(RR.glob('*.cmd'))
if len(cmds) != 18:
    bad.append(f'{len(cmds)} replay .cmd files, not 18')
for c in cmds:
    t = c.read_text()
    m = re.search(r'/RR_R8_543dad00/programs/(deckgym|legality_scan|goldfish)\b', t); s = re.search(r'^program sha256 ([0-9a-f]{64})$', t, re.M)
    if not m or not s:
        bad.append(f'replay {c.stem}: no RR_R8_543dad00 program or "program sha256" line'); continue
    eq(f'replay {c.stem} ran RR_R8_543dad00/programs/{m.group(1)}', s.group(1), progs[m.group(1)])
pieces = sorted(p for p in F2.iterdir() if p.is_dir() and p.name != '_ref_stripped')
if len(pieces) != 12:
    bad.append(f'{len(pieces)} floor pieces, not 12')
for p in pieces:
    m = re.search(r'/RR_R8_543dad00/programs/deckgym ([0-9a-f]{64})', (p / 'cmd.txt').read_text())
    eq(f'floor piece {p.name} (cmd.txt) ran RR_R8_543dad00/programs/deckgym', m.group(1) if m else 'none', progs['deckgym'])
run = Path('/home/dacz8976/relplan/r8/sw/step3_run.sh').read_text()
m = re.search(r'^SWT=\S+; P=(\S+)$', run, re.M)
eq('the program step3_run.sh self-checked and refusal-tested (P=)', m.group(1).replace('$W', '/home/dacz8976/pincand_work') if m else 'none', str(P))
sp = sha(P); bj = json.loads(Path(str(P) + '.build.json').read_text())
eq(f'{P} (sc_kx3, the K8 refusal run) v its build record', sp, bj.get('program_sha256'))
m = re.search(r'^RECORD OK ([0-9a-f]{64})$', (N3 / 'record_check.txt').read_text(), re.M)
eq(f'{P} v record_check.txt (the check before sc_kx3)', sp, m.group(1) if m else 'none')
spl = sha(PL); bjl = json.loads(Path(str(PL) + '.build.json').read_text())
eq(f"{PL} (Lane N's sc_km3) v its build record", spl, bjl.get('program_sha256'))
night = (LN / 'night/night.log').read_text(errors='replace')
m = re.search(r'strength_L: RECORD OK program ([0-9a-f]{64})', night)
eq(f"{PL} v Lane N's night.log strength_L line", spl, m.group(1) if m else 'none')
st = sha(TU)
lines.append(f'INFO    the refusal test\'s own program (test-utils; tools/tu_build.sh; not committed, never official): {TU}: {st}')
tb = Path('/home/dacz8976/relplan/r8/sw/tu_build.sh').read_text()
mN = re.search(r'^SWT=\S+; N=(\S+); B=\$N/(\S+)$', tb, re.M); mP = re.search(r'^PT=\$B/(\S+)$', tb, re.M)
eq('the program tu_build.sh built and refusal-tested (N=, B=, PT=)', f"{mN.group(1)}/{mN.group(2)}/{mP.group(1)}" if mN and mP else 'none', str(TU))
m = re.search(r'^program sha256 ([0-9a-f]{64})$', (N3 / 'tu_build.out').read_text(), re.M)
eq('the tu program v the "program sha256" line tu_build.sh printed (its captured stdout, logs/switch/tu_build.out)', st, m.group(1) if m else 'none')
m = re.search(r'^refusal \(test-utils program\): rc=0 Ran 4 tests in \S+ OK', (N3 / 'tu_build.out').read_text(), re.M)
lines.append(f"{'EQUAL  ' if m else 'DIFFERS'} tu_build.out's refusal line (rc=0 Ran 4 tests ... OK) and strength_refusal_tu.log agree: {'yes' if m else 'no'}")
if not m:
    bad.append('tu_build.out refusal line')
OUT.write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
if bad:
    print('NOT EQUAL:', bad)
    sys.exit(1)
EOF

# ---- the checkouts the floor and the replays read, and their runners ---------------------------------------------------------
{ echo "The floor re-check (floor2.py) ran S8's deckgym (/home/dacz8976/pincand_work/RR_R8_543dad00/programs/deckgym) and read decks,"
  echo "the panel and the Python runners from /home/dacz8976/pincand, the laptop's main checkout (not origin/main), as floor2S did on Oct 29."
  echo "pincand: branch $(git -C $REPO rev-parse --abbrev-ref HEAD), HEAD $(git -C $REPO rev-parse HEAD); its reflog's last entry: $(git -C $REPO reflog -1 --date=iso HEAD)"
  echo "Each file: its blob at pincand's HEAD v at S8, and pincand's working tree v its HEAD."
} > $TMPR/RUN_CONTEXT.txt
codebad=0
for f in decks/screen/floor.py decks/screen/run_screen.py current_engine.py lib/deck_check.py \
         rl/results/engine_switch_rules2_2026-10/floor_with.py rl/results/engine_switch_rules2_2026-10/sitting1_check.py \
         rl/results/engine_switch_rules2_2026-10/switch_check.py rl/results/engine_switch_2026-09-30/screen_with.py \
         rl/results/engine_candidate_2026-10-20/release/tools/floor2.py lib/deckgym-database.json project_manifest.json; do
  a=$(git -C $REPO rev-parse HEAD:$f); b=$(git rev-parse $S:$f)
  if git -C $REPO diff --quiet HEAD -- $f; then t=clean; else t=MODIFIED; fi
  if [ $a = $b ]; then e=EQUAL; else e=DIFFERS; fi
  note=
  [ $f = lib/deckgym-database.json ] && note=" (the pre-R5 copy, as at R6: the floor decks hold old cards only)"
  [ $f = project_manifest.json ] && note=" (pincand's manifest names rl/engine-2026-10-21 as the release, so floor.py's coverage step ran that goldfish, as for floor2S; R8's own goldfish gives byte-equal coverage: logs/floor_recheck_R8/GOLDFISH_R8_COVERAGE.txt)"
  echo "$f: pincand HEAD ${a:0:12}, S8 ${b:0:12}: $e; working tree $t$note" >> $TMPR/RUN_CONTEXT.txt
  if [ $t = MODIFIED ] || { [ $e = DIFFERS ] && [ $f != lib/deckgym-database.json ] && [ $f != project_manifest.json ]; }; then codebad=1; fi
done
for p in $(ls -d $W/floor2R8/*/ | xargs -n1 basename | grep -vx _ref_stripped); do
  dk=$(grep -o 'decks/[^ ]*\.txt\|rl/results/[^ ]*\.txt' $W/floor2R8/$p/cmd.txt | head -n 1)
  a=$(git -C $REPO rev-parse HEAD:$dk); b=$(git rev-parse $S:$dk); [ $a = $b ] && e=EQUAL || { e=DIFFERS; codebad=1; }
  git -C $REPO diff --quiet HEAD -- $dk && t=clean || { t=MODIFIED; codebad=1; }
  echo "floor deck $p ($dk): pincand HEAD v S8 $e; working tree $t" >> $TMPR/RUN_CONTEXT.txt
done
for d in decks/screen/opponents rl/results/floor_recheck_rules2_2026-10; do
  [ "$(git -C $REPO rev-parse HEAD:$d)" = "$(git rev-parse $S:$d)" ] && e=EQUAL || { e=DIFFERS; codebad=1; }
  git -C $REPO diff --quiet HEAD -- $d && t=clean || { t=MODIFIED; codebad=1; }
  [ -z "$(git -C $REPO ls-files --others --exclude-standard -- $d)" ] && u=none || { u=PRESENT; codebad=1; }
  echo "$d/ (tree): pincand HEAD v S8 $e; working tree $t; untracked files $u" >> $TMPR/RUN_CONTEXT.txt
done
cmp -s $W/floor2.py <(git show $S:rl/results/engine_candidate_2026-10-20/release/tools/floor2.py) && echo "$W/floor2.py as run: byte-equal to S8's committed copy" >> $TMPR/RUN_CONTEXT.txt || { echo "$W/floor2.py as run: NOT S8's copy" >> $TMPR/RUN_CONTEXT.txt; codebad=1; }
echo "The official build's 18 replays (unplanned; the basis is Lane N's, logs/replays_N/, run by Lane N in the same path on 48dec4f5) ran replay_r8.py side r from lane/ in $LWT (S8; clean at record time) on the archive RR_R8_543dad00/RR (git archive of S8's engine/ and decks/)." >> $TMPR/RUN_CONTEXT.txt
for f in lane_r8.sh replay_r8.py; do cmp -s $LWT/rl/results/r8_catchup_2026-10-29/lane/$f <(git show $S:rl/results/r8_catchup_2026-10-29/lane/$f) && echo "lane/$f in $LWT: S8's" >> $TMPR/RUN_CONTEXT.txt || { echo "lane/$f in $LWT: NOT S8's" >> $TMPR/RUN_CONTEXT.txt; codebad=1; }; done
cat $TMPR/RUN_CONTEXT.txt
[ $codebad = 0 ] || die "a runner, deck or tree the floor or the replays used differs from S8's, or pincand's working tree changed it (RUN_CONTEXT above)"

# ---- the programs --------------------------------------------------------------------------------------------------------
CREATED=1; mkdir -p $PF
for n in deckgym legality_scan goldfish; do cp $PG/$n $PF/; done
chmod 755 $PF/deckgym $PF/legality_scan $PF/goldfish
for n in deckgym legality_scan goldfish; do grep -E "^[0-9a-f]{64}  $n\$" $PG/SHA256SUMS || die "no $n line in programs/SHA256SUMS"; done > $PF/SHA256SUMS
[ "$(wc -l < $PF/SHA256SUMS)" = 3 ] || die "programs/SHA256SUMS does not have one line for each of the three"
cp $PG/SOURCE_COMMIT $PF/
{ cat $TMPR/RAN_SHA256.txt; echo "programs_final/ (the copies to commit): sha256sum -c SHA256SUMS:"; (cd $PF && sha256sum -c SHA256SUMS); } > $D/RAN_SHA256.txt \
  || die "programs_final/ is not programs/"
echo "RESULT: all equal" >> $D/RAN_SHA256.txt
cp $TMPR/RUN_CONTEXT.txt $D/RUN_CONTEXT.txt

# ---- the logs ------------------------------------------------------------------------------------------------------------
mkdir -p $L/lane_R $L/lane_N $L/replays_R $L/replays_N $L/switch $L/floor_recheck_R8 $D/tools
for f in build_R.log status_R.txt card_status.json card_status.err lane_r.log replays.log R_COMMIT gen_ids.err gen_database.err; do cp $PR/$f $L/lane_R/; done
(cd $PR && sha256sum gen_ids.rs gen_database.rs) > $L/lane_R/gen_outputs.sha256
(cd $PR && for m in *.done *.FAILED lane_r.end; do [ -e "$m" ] && echo "$m: $(head -c 200 $m)"; done) > $L/lane_R/markers.txt 2>/dev/null || true
cp $PG/SHA256SUMS $L/lane_R/programs_SHA256SUMS; cp $PG/SOURCE_COMMIT $L/lane_R/
for f in lane_r.log suite_R.log goldfish_plain.log goldfish_test.log goldfish_tu.log status_R.txt build_R.log R_COMMIT; do cp $LN/prep/$f $L/lane_N/; done
(cd $LN/prep && sha256sum gen_ids.rs gen_database.rs) > $L/lane_N/gen_outputs.sha256
cp $LN/programs/SHA256SUMS $L/lane_N/programs_SHA256SUMS
for f in night.log SUMMARY.txt sc_km3.out; do cp $LN/night/$f $L/lane_N/; done
cp $LN/verify/VERIFY.txt $L/lane_N/; cp $LN/k8/K8_RECORD.union.txt $L/lane_N/
cp $PL.build.json $L/lane_N/strength_L.build.json; cp $P.build.json $L/lane_N/strength_K8.build.json
for f in $GM/r/*; do [ -f "$f" ] || continue; case "$f" in *.jsonl|*_coverage.json) ;; *) cp "$f" $L/replays_R/;; esac; done
grep -P '^r\t' $GM/summary.tsv > $L/replays_R/summary_r.tsv
(cd $GM/r && sha256sum *.jsonl *_coverage.json) > $L/replays_R/outputs.sha256
cp $TMPR/V_LANE_N.txt $L/replays_R/V_LANE_N.txt
grep -P '^r\t' $LN/games/summary.tsv > $L/replays_N/summary_r.tsv
(cd $LN/games/r && sha256sum *.jsonl *_coverage.json) > $L/replays_N/outputs.sha256
for f in sc_kx3.out sc_kx3.rc sc_kx3.err record_check.txt strength_refusal.log strength_refusal_tu.log strength_py.log tu_build.log tu_build.out floor.log floor.rc; do cp $N3/$f $L/switch/; done
{ git log -1 --format='commit %H%nparents %P%ndate %cI%n%n%B' $K; echo "engine tree $(git rev-parse $K:engine)"
  echo "48dec4f5 v K8:"; git diff --name-status $LANE $K; echo "origin: $(timeout 120 git ls-remote origin refs/heads/$KBR)"
} > $L/switch/K8_overlay.txt
for p in $W/floor2R8/*/; do
  piece=$(basename $p); [ "$piece" = _ref_stripped ] && continue
  mkdir -p $L/floor_recheck_R8/$piece
  for f in $p*.md $p/cmd.txt $p/cmp*.txt $p/run.log $p/run_screen.txt; do if [ -e "$f" ]; then cp "$f" $L/floor_recheck_R8/$piece/; fi; done
done
cp $W/floor2R8/summary.tsv $L/floor_recheck_R8/
(cd $W/floor2R8 && find . -type f ! -path './_ref_stripped/*' | sort | xargs sha256sum) > $L/floor_recheck_R8/outputs.sha256
for f in RECOMPARE GOLDFISH_R8_COVERAGE FLOOR2S_BASIS; do cp $TMPR/$f.txt $L/floor_recheck_R8/$f.txt; done

# ---- the tools -----------------------------------------------------------------------------------------------------------
for f in $TOOLS_RUN; do cp $SW/$f $D/tools/; done
cp "${BASH_SOURCE[0]}" $D/tools/commit_record_r8.sh
{ echo "The scripts as run on the laptop (copied byte for byte from /home/dacz8976/relplan/r8/sw/) and this record's own script. sha256:"
  (cd $D/tools && sha256sum $(ls | grep -vx TOOLS.txt))
  echo "The official build's lane ran rl/results/r8_catchup_2026-10-29/lane/lane_r8.sh and replay_r8.py as committed at S8 (RUN_CONTEXT.txt);"
  echo "  Lane N ran the same files as committed at 48dec4f5 (its own lane log; not re-checked here)."
  echo "step2_build.sh: the official build from S8: lane_r8.sh in ~/lane_r8_w (cargo in its engine/ under nice 19, lane_r8.sh:66, 85-86), with a fresh"
  echo "  CARGO_TARGET_DIR ~/lane_r8_target (lane_r8.sh:35, 64; step2_build.sh moved Lane N's aside first); suite_R and goldfish_R marked skipped"
  echo "  under Q2 (A). lane_r8.sh:206-207 gate the replays on goldfish_R.done (which that skip marker satisfied), never on replays_R.done, so the"
  echo "  18 replays ran (unplanned; coordinator-155 Q1), and lane_r8.sh:218 runs replay_r8.py without nice. The fix goes in the next lane copy."
  echo "step3_run.sh: the K8 record check; sc_kx3 and floor2.py in parallel (nice 19); the refusal test on K8 and the rl/strength Python suite"
  echo "  (no STRENGTH_PROGRAM, so its 4 card-support tests skip)."
  echo "tu_build.sh: the refusal test's own program (rl/strength/test_strength_card_support.py:8-13: harness and engine from S8 with deckgym/test-utils);"
  echo "  accepted as the refusal step's program (coordinator-155 Q2). Its captured stdout: logs/switch/tu_build.out. The next lane copy's"
  echo "  strength step names this build."
  echo "wait34.sh: waits for sc_kx3 and the floor run, then runs floorR8_recompare.sh."
  echo "floorR8_recompare.sh: the floor's acceptance rule (coordinator-080), stricter than R6's in two ways (coordinator-155 §4): the goldfish line"
  echo "  is not normalised (both sides ran in the same checkout with the same manifest), and sitting1_check.py runs with no modes."
  echo "goldfishR8_floor_coverage.sh: R8's goldfish on the 11 floor decks, coverage only (no games), v floor2R8's coverage files. Its header"
  echo "  comment (lines 2-7) was corrected after the run (it was R6's text); the code from line 8 on is as run, and this record re-ran it."
  echo "floor2s_basis.sh and replays_v_laneN.sh were also re-run by this record (their outputs are the copies in logs/)."
  echo "floor2s_basis.sh: floor2S v R6's committed sums (coordinator-151 Q3; the command of coordinator-155 §1)."
  echo "replays_v_laneN.sh: the official build's replays v Lane N's."
  echo "r8_push2.sh: Guardrail A and the push (coordinator-154: the content grep takes the never-open exclusion array)."
} > $D/tools/TOOLS.txt

# ---- the tables and record.json, then Guardrail B on every expected verdict ----------------------------------------------------
python3 -I - $D $S "$(git rev-parse $S:engine)" $K "$(git rev-parse $K:engine)" $LANE "$(git -C $REPO rev-parse HEAD)" \
            "$(git -C $REPO rev-parse --abbrev-ref HEAD)" $gib $HARN "$SC_KM3" "$SC_KX3" <<'EOF'
import importlib.util, json, re, sys
from pathlib import Path
D, S, STREE, K, KTREE, LANE, PHEAD, PBRANCH, GIB, HARN, SC_KM3, SC_KX3 = sys.argv[1:]
D = Path(D); L = D / 'logs'; W = Path('/home/dacz8976/pincand_work')
def need(m, what):
    if not m:
        sys.exit(f'record.json: no {what}')
    return m
laneR = (L / 'lane_R/lane_r.log').read_text(errors='replace'); laneN = (L / 'lane_N/lane_r.log').read_text(errors='replace')
nightN = (L / 'lane_N/night.log').read_text(errors='replace')
rec = dict(schema='r8-record v1', s=S, s_engine_tree=STREE, k=K, k_engine_tree=KTREE, lane_n=LANE,
           basis=('Q2 (A), coordinator-151 §3: the five programs built from S8 have Lane N\'s sha256, so Lane N\'s suite, goldfish '
                  'steps and replays (48dec4f5, the same engine tree) are cited; the official build ran no suite or goldfish step'))
rec['programs_sha256'] = {l.split()[1]: l.split()[0] for l in (D / 'programs_final/SHA256SUMS').read_text().splitlines()}
rec['programs_all_sha256'] = {l.split()[1]: l.split()[0] for l in (L / 'lane_R/programs_SHA256SUMS').read_text().splitlines()}
rec['programs_equal_lane_n'] = (L / 'lane_R/programs_SHA256SUMS').read_text() == (L / 'lane_N/programs_SHA256SUMS').read_text()
rec['ran_sha256'] = 'all equal (RAN_SHA256.txt)' if (D / 'RAN_SHA256.txt').read_text().rstrip().endswith('RESULT: all equal') else 'NOT EQUAL'
m1 = need(re.search(r'^(\S+) lane_r8 start: R=' + S + '$', laneR, re.M), 'lane_r8 start line')
m2 = need(re.search(r'^(\S+) build_R OK: BUILD OK in (\d+) s$', laneR, re.M), 'build_R OK line')
rec['build'] = dict(lane_start=m1.group(1), build_ok_at=m2.group(1), secs=int(m2.group(2)))
def gencmp(t):
    return {k: need(re.search(r'gen_R ' + k + r': (\S+) ', t), 'gencmp ' + k).group(1) for k in ('ids', 'database')}
rec['gencmp'] = gencmp(laneR); rec['gencmp_lane_n'] = gencmp(laneN)
def cstat(p):
    st = p.read_text()
    return dict(line=need(re.search(r'^card_status: all .*$', st, re.M), 'card_status line').group(0),
                all_by_status=need(re.search(r'^all by status: (.*)$', st, re.M), 'all by status').group(1),
                older=need(re.search(r'^older cards neither Complete nor RulesUnverified: (\d+)', st, re.M), 'older').group(1),
                exact=need(re.search(r'^exact R8 counts .*: (\S+)$', st, re.M), 'exact R8 counts').group(1),
                check=need(re.search(r'^STATUS_CHECK (\S+)', st, re.M), 'STATUS_CHECK').group(1))
rec['card_status'] = cstat(L / 'lane_R/status_R.txt'); rec['card_status_lane_n'] = cstat(L / 'lane_N/status_R.txt')
m = need(re.search(r'suite_R rc=(\d+) in (\d+) s: passed (\d+) failed (\d+) ignored (\d+) compile_errors (\d+)', laneN), 'Lane N suite line')
rec['suite'] = dict(source='Lane N (48dec4f5)', rc=int(m.group(1)), secs=int(m.group(2)), passed=int(m.group(3)), failed=int(m.group(4)),
                    ignored=int(m.group(5)), compile_errors=int(m.group(6)))
gs = need(re.search(r'goldfish_R strings TEST_CARD_SUPPORT_MISSING_ATTACK: programs/deckgym (\d+), programs/goldfish (\d+), rebuilt plain goldfish (\d+)', laneN), 'goldfish strings')
gt = need(re.search(r'goldfish_R plain test rc=(\d+): test result: ok\. (\d+) passed; (\d+) failed', laneN), 'goldfish plain test')
rec['goldfish_steps'] = dict(source='Lane N (48dec4f5)', strings=[int(x) for x in gs.groups()], plain_test_rc=int(gt.group(1)),
                             plain_passed=int(gt.group(2)), plain_failed=int(gt.group(3)))
rec['switch_runs'] = 'dropped (coordinator-151 §3): R8\'s only new env::var is test-utils\' TEST_MISSING_ATTACK_ENV ("TEST_CARD_SUPPORT_MISSING_ATTACK")'
mL = need(re.search(r'strength_L: RECORD OK program ([0-9a-f]{64}) engine tree (\S+) harness (\S+);', nightN), 'strength_L line')
bjK = json.loads((L / 'lane_N/strength_K8.build.json').read_text())
rec['strength'] = dict(program=bjK['program'], sha256=bjK['program_sha256'], engine_ref=bjK['engine_ref'],
                       engine_tree_archived=bjK['engine_tree_archived'], harness=bjK['harness_source_sha256'], jobs=bjK['jobs'],
                       built_at=bjK['built_at'], record='K8_RECORD.union.txt (logs/lane_N/)')
rec['strength_L'] = dict(sha256=mL.group(1), engine_tree=mL.group(2), harness=mL.group(3))
kxrc = (L / 'switch/sc_kx3.rc').read_text().split()
rec['selfchecks'] = dict(km3=(L / 'lane_N/sc_km3.out').read_text().strip(), km3_program='strength_L (Lane N; not rebuilt since, plan 113 §3)',
                         kx3=(L / 'switch/sc_kx3.out').read_text().strip(), kx3_rc=int(kxrc[0]), kx3_secs=int(kxrc[1]))
def ut(p):
    t = p.read_text(errors='replace')
    return dict(ran=int(need(re.search(r'^Ran (\d+) tests?', t, re.M), f'{p.name} Ran').group(1)),
                status=need(re.search(r'^(OK.*|FAILED.*)$', t, re.M), f'{p.name} status').group(1),
                failing=sorted(set(re.findall(r'^((?:FAIL|ERROR): \S+)', t, re.M))),
                passing=sorted(set(re.findall(r'^(\S+) \(test_strength_card_support\.\S+\) \.\.\. ok$', t, re.M))))
rec['refusal_test_k8'] = ut(L / 'switch/strength_refusal.log')
rec['refusal_test_tu'] = ut(L / 'switch/strength_refusal_tu.log')
rec['refusal_test_tu']['program_sha256'] = need(re.search(r'^program sha256 ([0-9a-f]{64})$', (L / 'switch/tu_build.out').read_text(), re.M), 'tu sha').group(1)
rec['refusal_note'] = ('R8 changed test_strength_card_support.py (Weedle, through TEST_CARD_SUPPORT_MISSING_ATTACK, which only a '
                       'test-utils build reads; :8-13). K8 is a plain build (rl/strength/build.sh), so 3 of its 4 tests fail as the '
                       'header says for a plain program (:13); the program the header prescribes (tools/tu_build.sh) passes 4 of 4. '
                       'Accepted, coordinator-155 Q2. The next lane copy\'s strength step names the tu build.')
rec['strength_py'] = ut(L / 'switch/strength_py.log'); rec['strength_py'].pop('passing')
# the replays: Lane N's rows (the basis) and the official build's (unplanned, equal)
GROWL = {'08a9b3a_new17_k3': '8 differing deals of 8500', '08a9b3a_dev_km3_new17': '7 differing deals of 8500', '08a9b3a_8_new_km3': '1 differing deals of 16000'}
def rows_of(p):
    rows = []
    for line in p.read_text().splitlines():
        side, name, games, secs, verdict, detail = (line.split('\t') + [''] * 6)[:6]
        vs = re.search(r'\| v S: (.*)$', detail)
        rows.append(dict(name=name, games=int(games), secs=int(secs), verdict=verdict, detail=detail,
                         vs=vs.group(1).strip() if vs else None,
                         vs_same=bool(vs and (vs.group(1).strip() == 'SAME' or vs.group(1).startswith(('SAME (', 'sha SAME', 'page SAME')))),
                         growl_known=(verdict == 'DIFFERS' and name in GROWL and detail.startswith(GROWL[name] + ';')),
                         rules_clean=bool(re.search(r'rules page: .*: no RULE finding', detail))))
    return rows
def summ(rows):
    return dict(n=len(rows), games_total=sum(r['games'] for r in rows), ref_same=sum(r['verdict'] == 'SAME' for r in rows),
                ref_growl_known=sum(r['growl_known'] for r in rows), vs_same=sum(r['vs_same'] for r in rows),
                rules_clean=sum(r['rules_clean'] for r in rows),
                goldfish=next((r['detail'].split(' | ')[0] for r in rows if r['name'].endswith('_goldfish')), None))
rN, rR = rows_of(L / 'replays_N/summary_r.tsv'), rows_of(L / 'replays_R/summary_r.tsv')
vln = (L / 'replays_R/V_LANE_N.txt').read_text()
t0 = need(re.search(r'^(\S+) replay r \S+$', laneR, re.M), 'first replay line').group(1)
t1 = need(re.search(r'^(\S+) lane_r8 end: done$', laneR, re.M), 'lane end line').group(1)
from datetime import datetime
span = int((datetime.fromisoformat(t1.replace('Z', '+00:00')) - datetime.fromisoformat(t0.replace('Z', '+00:00'))).total_seconds())
rec['replays'] = dict(source='Lane N (48dec4f5), the basis under Q2 (A)', **summ(rN), rows=rN,
                      verify=next((l for l in (L / 'lane_N/VERIFY.txt').read_text().splitlines() if l.startswith('VERIFY ')), None))
rec['replays_official'] = dict(source=(f'the official build on S8, unplanned: lane_r8.sh:206-207 gate the replays on goldfish_R.done (which the '
                                       f'Q2 (A) skip marker satisfied), never on replays_R.done; :218 runs replay_r8.py without nice; '
                                       f'{t0} to {t1} (about {round(span / 60) // 60} h {round(span / 60) % 60} min, lane_R/lane_r.log) (coordinator-155 Q1). '
                                       f'The nice fix goes in the next lane copy.'), span_secs=span,
                               **summ(rR), equal_lane_n=vln.rstrip().endswith("RESULT: the official build's 18 replays equal Lane N's"),
                               v_lane_n=[l for l in vln.splitlines() if l.startswith(('summary', 'games/r'))])
trows = []
for a, b in zip(sorted(rN, key=lambda r: r['name']), sorted(rR, key=lambda r: r['name'])):
    if a['name'] != b['name'] or a['verdict'] != b['verdict'] or a['games'] != b['games']:
        sys.exit(f"REPLAY_TABLE: the rows do not pair: {a['name']} {a['verdict']} v {b['name']} {b['verdict']}")
    head = a['detail'].split(' | ')[0].split('; rules page')[0]
    vs_ = (a['vs'] or 'none').split(' (')[0]
    trows.append(f"| `{a['name']}` | {a['games']:,} | {a['verdict']}: {head} | {vs_} | {b['verdict']} |")
(D / 'REPLAY_TABLE.md').write_text(
    '| Run (replayed command) | Games or deals | Lane N v the 08a9b3a reference | Lane N v R6\'s S ("v S") | The official build\'s run (unplanned; '
    'all 18 equal to Lane N\'s: logs/replays_R/V_LANE_N.txt) |\n'
    '|---|---|---|---|---|\n' + '\n'.join(trows) + '\n', encoding='utf-8')
# the floor: R8 v the recorded page (floor2.py) and v floor2S (floorR8_recompare.sh)
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
def fsum(folder):
    p = W / folder / 'summary.tsv'
    return {l.split('\t')[0]: (l.rstrip('\n').split('\t') + [''] * 5)[:5] for l in p.read_text().splitlines() if l}
R8F, SF = fsum('floor2R8'), fsum('floor2S')
rc_txt = (L / 'floor_recheck_R8/RECOMPARE.txt').read_text(encoding='utf-8')
RPASS = set(re.findall(r'^PASS (\S+):', rc_txt, re.M))
fl = dict(n=0, games=0, deck_games=0, screen_games=0, recompare_pass=sorted(RPASS), other=[],
          v_recorded={}, v_floor2s_floor2py={},
          rule=('coordinator-080\'s corrected rule, stricter in two ways (coordinator-155 §4): the 11 deck pieces\' games and coverage '
                'byte-equal to floor2S (R6\'s pages on S, Oct 29) and each page equal after normalising only the engine path (the '
                'goldfish line not normalised: the same checkout and manifest on both sides); run_screen equal apart from the engine path; '
                'sitting1_check.py floor with no modes and switch_check.py screen exit 0'),
          goldfish_r8_coverage=len(re.findall(r'^EQUAL \S+: rc 0, coverage byte-equal to floor2R8', (L / 'floor_recheck_R8/GOLDFISH_R8_COVERAGE.txt').read_text(), re.M)),
          floor2s_basis=need(re.search(r'^RESULT: (.*)$', (L / 'floor_recheck_R8/FLOOR2S_BASIS.txt').read_text(), re.M), 'basis RESULT').group(1))
frows = []
for piece, (kind, deck, extra, ref_, name) in F2.PIECES.items():
    r, s = R8F.get(piece), SF.get(piece)
    fl['n'] += 1; g = int(r[1] or 0) if r else 0; fl['games'] += g
    fl['screen_games' if kind == 'screen' else 'deck_games'] += g
    fl['v_recorded'][piece] = r[3] if r else 'not run'
    vs_ = re.search(r'v floor2S: exit (\d+)', r[4]) if r else None
    fl['v_floor2s_floor2py'][piece] = (f'exit {vs_.group(1)}' if vs_ else ('SAME v recorded (not compared again)' if r and r[3] == 'SAME' else 'none'))
    if kind == 'screen':
        old, newv = 'run_screen, 20 lines', 'run_screen, 20 lines'
    else:
        refmd = (F2.REF / 'pages' / ref_.split(':', 1)[1] / f'{name}.md') if isinstance(ref_, str) and ref_.startswith('STRIP:') else Path(ref_) / f'{name}.md'
        old, newv = verdict(refmd), verdict(W / 'floor2R8' / piece / f'{name}.md')
    if piece not in RPASS:
        fl['other'].append(piece)
    frows.append(f"| {piece} | {old} | {newv} | {fl['v_recorded'][piece]} | {fl['v_floor2s_floor2py'][piece]} | "
                 f"{'PASS' if piece in RPASS else 'FAIL'}; R6's S: {verdict(W / 'floor2S' / piece / f'{name}.md') if kind != 'screen' else 'run_screen'} |")
rec['floor'] = fl
(D / 'FLOOR_TABLE.md').write_text(
    '| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | S8 (floor2R8) | floor2.py: S8 v recorded | floor2.py: v floor2S | '
    'floorR8_recompare.sh v floor2S (R6\'s S, Oct 29) |\n|---|---|---|---|---|---|\n' + '\n'.join(frows) + '\n\n'
    'floor2.py compares each page with the recorded page of rl/results/floor_recheck_rules2_2026-10/ (main-c045ede); its DIFFERS '
    'there is the engine and coverage lines (and, for brew-07 and brew-09, games, as on main-4d48844 and R6\'s S), and for each it '
    'also compares with floor2S ("v floor2S: exit 0"). The acceptance rule is floorR8_recompare.sh\'s (tools/; output '
    'logs/floor_recheck_R8/RECOMPARE.txt): every games and coverage file byte-equal to floor2S\'s and each page equal apart from '
    'the engine path only. floor2S is as R6 committed it (logs/floor_recheck_R8/FLOOR2S_BASIS.txt), and R8\'s own goldfish gives '
    'byte-equal coverage on the 11 floor decks (GOLDFISH_R8_COVERAGE.txt): floor.py took coverage from pincand\'s official '
    'goldfish (rl/engine-2026-10-21), as floor2S did.\n', encoding='utf-8')
rec['floor_ran_from'] = dict(repo='/home/dacz8976/pincand', branch=PBRANCH, head_at_record_time=PHEAD, note='RUN_CONTEXT.txt')
rec['c_free_gib_at_record'] = int(GIB)
(D / 'record.json').write_text(json.dumps(rec, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
print('replays (Lane N):', {k: v for k, v in rec['replays'].items() if k != 'rows'})
print('replays (official):', {k: v for k, v in rec['replays_official'].items() if k != 'rows'})
print('floor:', {k: v for k, v in fl.items() if k not in ('v_recorded',)})
# Guardrail B: the expected verdicts (113 §5; 151; 155); any miss refuses, and the trap removes the record
CARD = "card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 256, 'RulesUnverified': 4}"
CS = dict(line=CARD, all_by_status="{'Complete': 4565, 'RulesUnverified': 12}", older='0', exact='yes', check='OK')
K8_FAIL = sorted(['FAIL: test_run_refuses_a_deck_or_an_opponent_with_a_missing_attack_card_and_writes_nothing',
                  'FAIL: test_run_with_the_opt_out_lists_the_card_on_stderr_and_starts',
                  'FAIL: test_selfcheck_refuses_too_and_prints_no_selfcheck_line'])
rp, ro = rec['replays'], rec['replays_official']
miss = [what for what, ok in (
    ('the programs that ran are the committed ones', rec['ran_sha256'].startswith('all equal')),
    ("the five programs equal Lane N's (Q2 (A))", rec['programs_equal_lane_n']),
    ('gencmp SAME, SAME (both lanes)', rec['gencmp'] == rec['gencmp_lane_n'] == {'ids': 'SAME', 'database': 'SAME'}),
    ('card_status 4,565 + 12, new 256 + 4, older 0, exact R8 counts, STATUS_CHECK OK (both lanes)', rec['card_status'] == rec['card_status_lane_n'] == CS),
    ("the suite (Lane N): rc 0, 2,633 passed, 0 failed, 0 ignored, 0 compile errors", (rec['suite']['rc'], rec['suite']['passed'], rec['suite']['failed'],
        rec['suite']['ignored'], rec['suite']['compile_errors']) == (0, 2633, 0, 0, 0)),
    ('the goldfish steps (Lane N): no test variable in the plain programs; the plain test 1 passed', rec['goldfish_steps']['strings'] == [0, 0, 0]
        and (rec['goldfish_steps']['plain_test_rc'], rec['goldfish_steps']['plain_passed'], rec['goldfish_steps']['plain_failed']) == (0, 1, 0)),
    ('the self-checks equal the pin (km3 on strength_L, kx3 on strength_K8 rc 0)', rec['selfchecks']['km3'] == SC_KM3 and rec['selfchecks']['kx3'] == SC_KX3
        and rec['selfchecks']['kx3_rc'] == 0),
    ('strength_K8: engine K8, tree as archived = K8\'s, harness c4f7da21, jobs 2', rec['strength']['engine_ref'] == K and rec['strength']['engine_tree_archived'] == KTREE
        and rec['strength']['harness'] == HARN and rec['strength']['jobs'] == '2'),
    ('the refusal test: K8 3 of 4 fail (the header\'s plain-build result), the tu program 4 of 4 OK', rec['refusal_test_k8']['ran'] == 4
        and rec['refusal_test_k8']['failing'] == K8_FAIL and rec['refusal_test_k8']['status'] == 'FAILED (failures=4)'
        and rec['refusal_test_k8']['passing'] == ['test_supported_decks_start_and_the_check_says_nothing']
        and (rec['refusal_test_tu']['ran'], rec['refusal_test_tu']['status'], rec['refusal_test_tu']['failing']) == (4, 'OK', [])),
    ('the rl/strength suite: OK, nothing failing', re.fullmatch(r'OK( \(skipped=\d+\))?', rec['strength_py']['status']) is not None and not rec['strength_py']['failing']),
    ('the replays (Lane N): 18 rows, 15 SAME + the 3 known Growl rows, 18 v S SAME, 11 clean rules pages, goldfish page and coverage =, VERIFY PASS',
     (rp['n'], rp['ref_same'], rp['ref_growl_known'], rp['vs_same'], rp['rules_clean']) == (18, 15, 3, 18, 11) and rp['goldfish'] == 'page =, coverage ='
        and rp['verify'] == 'VERIFY PASS'),
    ("the official build's replays: the same verdicts and equal to Lane N's", (ro['n'], ro['ref_same'], ro['ref_growl_known'], ro['vs_same'], ro['rules_clean'])
        == (18, 15, 3, 18, 11) and ro['equal_lane_n']),
    ('the floor: 12 pieces PASS v floor2S; R8\'s goldfish 11 of 11; floor2S 92 of 92', fl['n'] == 12 and not fl['other'] and len(fl['recompare_pass']) == 12
        and fl['goldfish_r8_coverage'] == 11 and fl['floor2s_basis'] == 'floor2S = 92 of 92 committed sums'),
    ('the build ran on the folder date 2026-11-04 (UTC)', rec['build']['lane_start'][:10] == rec['build']['build_ok_at'][:10] == '2026-11-04'),
) if not ok]
if miss:
    print('Guardrail B: expected verdicts NOT met (bring the record to the coordinator; nothing is committed):')
    for x in miss:
        print('  -', x)
    sys.exit(1)
print('Guardrail B: every expected verdict met')
EOF

# ---- stage, check the modes, commit --------------------------------------------------------------------------------------
git add $REC
git update-index --chmod=+x $REC/programs_final/deckgym $REC/programs_final/legality_scan $REC/programs_final/goldfish
[ -z "$(git diff --cached --name-only | grep -v "^$REC/")" ] || die "something outside $REC is staged"
for n in deckgym legality_scan goldfish; do
  set -- $(git ls-files -s $REC/programs_final/$n)
  [ "$1" = 100755 ] || die "$n is staged as $1, not 100755"
  [ "$2" = "$(git hash-object $PF/$n)" ] || die "$n: the staged blob is not the file"
done
for n in SHA256SUMS SOURCE_COMMIT; do [ "$(git ls-files -s $REC/programs_final/$n | cut -c1-6)" = 100644 ] || die "$n mode"; done
echo "staged: $(git diff --cached --name-only | wc -l) files; $(du -sh $D | cut -f1) on disk"
{ echo "total $(git diff --cached --name-only | wc -l)"; git diff --cached --name-only | sed 's#^#  #'; } > $TMPR/staged.txt; head -n 1 $TMPR/staged.txt
if [ $CHECK = 1 ]; then cp $TMPR/staged.txt /home/dacz8976/relplan/r8/sw/record_check_staged.txt; cp $D/record.json /home/dacz8976/relplan/r8/sw/record_check.json
  cp $D/REPLAY_TABLE.md $D/FLOOR_TABLE.md $D/RAN_SHA256.txt $D/RUN_CONTEXT.txt /home/dacz8976/relplan/r8/sw/; exit 0; fi
$G commit -q -F - <<EOF
R8 build record: the official programs built from ${S:0:8} and the switch's checks

- r8_release/programs_final/: deckgym, legality_scan and goldfish, built once from ${S:0:8} (engine tree
  $(git rev-parse $S:engine | cut -c1-12)) in the clean worktree lane_r8_w (cargo in its engine/), with a fresh target
  directory, CARGO_BUILD_JOBS 2, nice 19 (lane_r8.sh:35, 64-66, 85-86; tools/step2_build.sh); mode 100755. SHA256SUMS (the three), SOURCE_COMMIT. All five programs have Lane N's sha256 (48dec4f5, the
  same engine tree), so Lane N's suite (2,633 passed, 0 failed), goldfish steps and 18 replays are cited
  (coordinator-151 §3, Q2 (A)); the switch runs are dropped (R8's only new env::var is test-utils'
  TEST_MISSING_ATTACK_ENV).
- r8_release/RAN_SHA256.txt: the programs that ran (the floor's and the replays' RR_R8_543dad00/programs,
  sc_kx3's strength_K8, sc_km3's strength_L) are, by sha256, the committed ones and the recorded builds,
  and the refusal test's tu program is the one tu_build.sh printed (logs/switch/tu_build.out).
  RUN_CONTEXT.txt: the checkouts the floor and the replays read and the byte-equality of their runners.
- logs/lane_R/ (the official build: gencmp SAME, SAME; card_status 4,565 Complete + 12 RulesUnverified), logs/lane_N/
  (the cited basis, with VERIFY PASS, sc_km3 and K8_RECORD.union.txt), logs/replays_R/: the official build's
  18 replays, which ran unplanned (lane_r8.sh:206-207 gate them on goldfish_R.done, which the Q2 (A)
  skip marker satisfied, never on replays_R.done; :218 runs them without nice; about 3 h 28) and equal
  Lane N's (coordinator-155 Q1); logs/replays_N/.
- logs/switch/: sc_kx3 on strength_K8 (b5f15351) equal to the pin; the rl/strength suite OK; the
  card-support refusal test: K8, a plain build, fails 3 of 4 as the test's header says for a plain
  program, and the header's own test-utils build (tools/tu_build.sh) passes 4 of 4 (coordinator-155 Q2).
- logs/floor_recheck_R8/: the 12 floor pieces on S8's deckgym, equal to floor2S (R6's pages on S) by
  coordinator-080's rule made stricter (the engine path is the only line normalised; sitting1_check.py
  with no modes); floor2S = 92 of 92 committed sums; R8's goldfish gives byte-equal coverage on the 11
  floor decks.
- r8_release/FLOOR_TABLE.md, REPLAY_TABLE.md, record.json: the numbers the adoption draft reads.
- r8_release/tools/: the scripts as run (TOOLS.txt).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
EOF
COMMITTED=1

# ---- after the commit ----------------------------------------------------------------------------------------------------
[ "$(git rev-parse HEAD^)" = $S ] || die "the record's parent is not S8"
[ "$(git rev-parse HEAD:engine)" = "$(git rev-parse $S:engine)" ] || die "the record changed engine/"
[ -z "$(git diff --name-only $S HEAD | grep -v "^$REC/")" ] || die "the record touches files outside $REC"
[ -z "$(git status --porcelain)" ] || die "the tree is not clean after the commit"
git ls-tree HEAD $REC/programs_final/
git log --oneline -2
echo "RECORD_COMMIT=$(git rev-parse HEAD)"
RC8=$(git rev-parse HEAD)   # r8_push2.sh resolves names in ~/pincand, whose HEAD is main: give it the commit itself
if [ $PUSH = 1 ]; then
  bash $SW/r8_push2.sh scan $RC8 $S && bash $SW/r8_push2.sh push $RC8 $S
else
  echo "not pushed (pass --push, or run r8_push2.sh scan/push $RC8 $S)"
fi
