#!/bin/bash
# verify_r6.sh: R6 runbook step 0 (baseline), step 11 (the draft) and step 12's re-run on main. Python checks only: no build, no
# engine run, no game. Adapted from release/tools/verify_draft.sh. DRAFT: written Oct 29, not run.
#   verify_r6.sh baseline WT [COMMIT]              step 0: a scratch worktree at COMMIT (default origin/main); records every check
#   verify_r6.sh draft    WT COMMIT BASELINE_DIR   steps 11/12: a scratch worktree at the adoption commit (the draft, the final,
#                                                  or main after the move): the commit's shape, the five activation checks, the
#                                                  Python checks and the rl/strength modules, compared with BASELINE_DIR
# WT is ALWAYS given, under /home/dacz8976. Refused by name: /home/dacz8976/adopt_w (verify_draft.sh's default, which it removes),
# the main checkout, pincand_work, relplan and the R6 worktrees. A path that does not exist gets a new worktree. An existing path
# is used only if THIS script made it (listed in /home/dacz8976/relplan/verify/OWNED_WORKTREES, kept with KEEP=1) and it is clean:
# then it is moved to COMMIT with `git checkout --detach` (so baseline, draft, final and main share one 2.4 GiB checkout). Any other
# existing path or registered worktree is refused. At the end the script removes its worktree unless KEEP=1.
# Disk: a new checkout is about 2.4 GiB on the WSL disk, so a new worktree needs C: free >= 15 GiB + its size; a reused one 15 GiB.
# ALLOW_LOW_DISK=1 overrides (the coordinator's call). Python checks only; nothing here builds or plays.
# Output: /home/dacz8976/relplan/verify/<mode>_<sha8>_<UTC time>/: results.tsv (one normalised line per check), raw/ (full
# outputs), commit.txt; for draft also compare.txt (the verdict) and draft_checks.md (a first text for adopt_r6.py --final).
# JOBS (default 2): rl/strength modules run at once, each at nice 19. Run it in a foreground shell (KX_RUNS_DIR is unset here).
set -u
MODE=${1:-}; WT=${2:-}; ARG3=${3:-}; BASE_DIR=${4:-}
REPO=/home/dacz8976/pincand
S=affe56e88985e2997a66beb85efaca0c487617bd
REC=rl/results/dual_type_seam_2026-10-23/r6_release
ED_NEW=rl/engine-2026-10-29
OWNED=/home/dacz8976/relplan/verify/OWNED_WORKTREES
JOBS=${JOBS:-2}
die() { echo "REFUSED: $*" >&2; exit 2; }
usage() { sed -n '2,20p' "$0" >&2; exit 2; }
case "$MODE" in
  baseline) C=${ARG3:-origin/main};;
  draft) C=$ARG3; [ -n "$C" ] && [ -n "$BASE_DIR" ] || usage; [ -s "$BASE_DIR/results.tsv" ] || die "no baseline results in $BASE_DIR";;
  *) usage;;
esac
[ -n "$WT" ] || usage
WT=$(realpath -m "$WT")
case "$WT" in /home/dacz8976/adopt_w|/home/dacz8976/adopt_w/*) die "$WT: adopt_w is never a scratch worktree (verify_draft.sh's default removes it)";; esac
case "$WT" in /home/dacz8976/?*) ;; *) die "WT must be a new folder under /home/dacz8976";; esac
for x in /home/dacz8976/pincand /home/dacz8976/pincand_work /home/dacz8976/r6s_w /home/dacz8976/r6_w /home/dacz8976/prep_w \
         /home/dacz8976/r5_w /home/dacz8976/i11_w /home/dacz8976/relplan; do
  case "$WT" in "$x"|"$x"/*) die "$WT is $x or inside it";; esac; done
C=$(git -C $REPO rev-parse --verify -q "$C^{commit}") || die "no commit $ARG3"
REUSE=0
if [ -e "$WT" ]; then
  grep -qx "$WT" $OWNED 2>/dev/null || die "$WT exists and was not made by verify_r6.sh: this script never touches a folder it did not make"
  git -C $REPO worktree list --porcelain | grep -qx "worktree $WT" || die "$WT is listed as ours but is not a registered worktree"
  [ -z "$(git -C "$WT" status --porcelain)" ] || die "$WT (ours) is not clean: look before reusing it"
  REUSE=1
else
  git -C $REPO worktree list --porcelain | grep -qx "worktree $WT" && die "$WT is a registered worktree"
fi
gib=$(( $(df -B1 --output=avail /mnt/c | tail -n 1 | tr -dc 0-9) / 1073741824 ))
need=0; [ $REUSE = 0 ] && need=$(git -C $REPO ls-tree -r -l $C | awk '$4 ~ /^[0-9]+$/ {s+=$4} END {print int(s / 1073741824) + 1}')
echo "C: free $gib GiB; a new checkout of ${C:0:8} needs about $need GiB more; the floor is 15 GiB"
[ $(( gib - need )) -ge 15 ] || [ "${ALLOW_LOW_DISK:-0}" = 1 ] || die "C: would fall below 15 GiB (free $gib, checkout $need)"
OUT=/home/dacz8976/relplan/verify/${MODE}_${C:0:8}_$(date -u +%Y%m%dT%H%M%SZ); RAW=$OUT/raw; mkdir -p $RAW
RES=$OUT/results.tsv; : > $RES; echo "$C" > $OUT/commit.txt
put() { printf '%s\t%s\n' "$1" "$2" >> $RES; printf '%-44s %s\n' "$1" "$2"; }
MADE=0
cleanup() {
  if [ $MADE = 1 ] && [ "${KEEP:-0}" != 1 ]; then
    cd /; git -C $REPO worktree remove --force "$WT" && { echo "removed $WT"; grep -vx "$WT" $OWNED > $OWNED.new; mv $OWNED.new $OWNED; }
  elif [ $MADE = 1 ]; then echo "kept $WT (KEEP=1); reuse it with the same path"; fi
}
trap cleanup EXIT
if [ $REUSE = 1 ]; then
  git -C "$WT" checkout -q --detach $C || die "git checkout in $WT failed"; MADE=1
else
  git -C $REPO worktree add -q --detach "$WT" $C || die "git worktree add failed"; MADE=1; echo "$WT" >> $OWNED
fi
cd "$WT"
[ "$(git rev-parse HEAD)" = $C ] || die "$WT is not at ${C:0:8}"
for v in $(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_|STRENGTH_PROGRAM$|SLOW_REPORT_ALLOW_UNCOMMITTED_PIN$)'); do unset "$v"; done
echo "=== $MODE: $(git log -1 --format='%h %s' HEAD) in $WT; output $OUT"

# one line from a unittest output: "Ran N | status | sorted FAIL/ERROR lines" (times and the worktree path normalised away)
summ() { python3 -I - "$1" "$WT" <<'EOF'
import re, sys
t = open(sys.argv[1], errors='replace').read().replace(sys.argv[2], '<WT>')
ran = re.findall(r'^Ran (\d+) tests?', t, re.M)
st = re.findall(r'^(OK(?: \(.*\))?|FAILED \(.*\))$', t, re.M)
fails = sorted(set(re.findall(r'^((?:FAIL|ERROR): \S+ \([^)]*\))', t, re.M)))
print(f"Ran {ran[-1] if ran else '?'} | {st[-1] if st else 'no status'} | " + ('; '.join(fails) if fails else 'no FAIL/ERROR'))
EOF
}
ut() {  # KEY DIR MODULE
  if [ ! -e "$2/$3.py" ]; then put "$1" absent; return; fi
  (cd "$2" && timeout 900 nice -n 19 python3 -B -m unittest $3) > $RAW/$1.txt 2>&1; local rc=$?
  put "$1" "rc=$rc | $(summ $RAW/$1.txt)"
}
pf() { if eval "$2"; then put "$1" "PASS${3:+ ($3)}"; else put "$1" "FAIL${3:+ ($3)}"; fi; }

# ---- the commit's shape (draft mode) -----------------------------------------------------------------------------------------
pf shape:clean_checkout '[ -z "$(git status --porcelain)" ]'
if [ $MODE = draft ]; then
  P1=$(git rev-parse HEAD^); NP=$(git rev-list --parents -n 1 HEAD | wc -w); NP1=$(git rev-list --parents -n 1 $P1 | wc -w)
  pf shape:parents '[ $NP = 2 ] && [ $NP1 = 2 ] && [ "$(git rev-parse $P1^)" = $S ]' "HEAD^ ${P1:0:8} (the record), HEAD^^ S"
  pf shape:record_only_results '[ -z "$(git diff --name-only $S $P1 | grep -v "^$REC/")" ]'
  git diff-tree -r --name-status $P1 HEAD | LC_ALL=C sort > $RAW/paths.txt
  { for n in README.md SHA256SUMS deckgym goldfish legality_scan; do printf 'A\t%s\n' "$ED_NEW/$n"; done
    for p in CLAUDE.md START_HERE.md project_manifest.json rl/RUN5.md rl/results/dual_type_seam_2026-10-23/RELEASE_CHECKLIST.md \
             rl/results/dual_type_seam_2026-10-23/RELEASE_NOTES.md rl/results/ladder_validation/make_predictions.py rl/strength/README.md; do
      printf 'M\t%s\n' "$p"; done; } | LC_ALL=C sort > $RAW/paths_want.txt
  pf shape:paths 'cmp -s $RAW/paths.txt $RAW/paths_want.txt' "$(wc -l < $RAW/paths.txt) paths; want the 13 of adopt_r6.py"
fi

# ---- the five activation checks (on the folder the manifest names) -----------------------------------------------------------
ED=$(python3 -I -c "import json; print(json.load(open('project_manifest.json'))['available_release']['artifact'].rsplit('/', 1)[0])")
python3 -I - $ED $S $MODE > $RAW/manifest.txt <<'EOF'
import json, sys
ed, s, mode = sys.argv[1:]
m = json.load(open('project_manifest.json')); a = m['available_release']
print(f"available {a['name']} {a['source_commit'][:8]} {ed}")
print('history tail ' + ' '.join(r['name'] for r in m['historical_releases'][-2:]) + ' | superseded: ' + str('superseded' in m['historical_releases'][-1]))
ok = a['name'] == 'main-' + s[:7] and a['source_commit'] == s and ed == 'rl/engine-2026-10-29' and m['historical_releases'][-1]['name'] == 'main-4d48844' \
     and 'superseded' in m['historical_releases'][-1] and m['latest_source_commit'] == s
print('R6 manifest:', 'PASS' if ok else ('FAIL' if mode == 'draft' else 'n/a (baseline)'))
EOF
put manifest:available "$(sed -n 1p $RAW/manifest.txt)"
put manifest:history "$(sed -n 2p $RAW/manifest.txt)"
put manifest:r6 "$(sed -n 3p $RAW/manifest.txt | cut -d' ' -f3-)"
(cd $ED && sha256sum -c SHA256SUMS) > $RAW/a1.txt 2>&1; a1=$?
pf A1:sha256sum_c '[ $a1 = 0 ] && [ "$(grep -c ": OK$" $RAW/a1.txt)" = 3 ]' "$ED: $(grep -c ': OK$' $RAW/a1.txt) OK lines"
git ls-tree HEAD $ED/ > $RAW/a2.txt
a2ok=1; for n in deckgym legality_scan goldfish; do
  [ "$(git ls-tree HEAD $ED/$n | cut -c1-6)" = 100755 ] || a2ok=0
  if [ $MODE = draft ]; then [ "$(git rev-parse HEAD:$ED/$n)" = "$(git rev-parse HEAD:$REC/programs_final/$n)" ] || a2ok=0; fi
done
if [ $MODE = draft ]; then [ "$(git rev-parse HEAD:$ED/SHA256SUMS)" = "$(git rev-parse HEAD:$REC/programs_final/SHA256SUMS)" ] || a2ok=0; fi
pf A2:ls_tree '[ $a2ok = 1 ]' "$(for n in deckgym legality_scan goldfish; do printf '%s %s ' $n $(git rev-parse HEAD:$ED/$n | cut -c1-8); done)each 100755$([ $MODE = draft ] && echo ', the programs_final blobs')"
python3 -B current_engine.py > $RAW/a3.txt 2>&1; a3=$?
pf A3:current_engine '[ $a3 = 0 ] && [ "$(head -n 1 $RAW/a3.txt)" = "$WT/$ED/deckgym" ]' "rc=$a3, prints $(head -n 1 $RAW/a3.txt | sed "s#$WT#<WT>#")"
a4=$(python3 -I - $ED <<'EOF'
import json, sys
a = json.load(open('project_manifest.json'))['available_release']
s = dict(l.split()[::-1] for l in open(sys.argv[1] + '/SHA256SUMS'))
print(a['sha256'] == s['deckgym'] and a['legality_scan_sha256'] == s['legality_scan'] and a['goldfish_sha256'] == s['goldfish'])
EOF
)
pf A4:manifest_v_sums '[ "$a4" = True ]' "manifest v SHA256SUMS: $a4"
if [ $MODE = draft ]; then
  pf A5:engine_tree '[ "$(git rev-parse HEAD:engine)" = "$(git rev-parse $S:engine)" ]' "HEAD:engine $(git rev-parse HEAD:engine | cut -c1-12), S's $(git rev-parse $S:engine | cut -c1-12)"
else put A5:engine_tree "n/a (baseline; HEAD:engine $(git rev-parse HEAD:engine | cut -c1-12))"; fi

# ---- placeholders ----------------------------------------------------------------------------------------------------------
git grep -n -E '@@[A-Z][A-Z0-9_]*@@' HEAD -- START_HERE.md CLAUDE.md rl/RUN5.md project_manifest.json rl/engine-2026-10-29 \
    rl/results/ladder_validation/make_predictions.py rl/strength/README.md rl/results/dual_type_seam_2026-10-23/RELEASE_NOTES.md \
    rl/results/dual_type_seam_2026-10-23/RELEASE_CHECKLIST.md > $RAW/placeholders.txt
ph=$(grep -o -E '@@[A-Z][A-Z0-9_]*@@' $RAW/placeholders.txt | sort -u | tr '\n' ' ' | sed 's/ $//')
put placeholders "${ph:-none}"

# ---- the Python checks (verify_draft.sh's list) --------------------------------------------------------------------------------
s=$(date +%s); timeout 900 nice -n 19 python3 -B rl/results/ladder_validation/make_predictions.py --selftest --repo . > $RAW/mp.txt 2>&1; rc=$?
put py:make_predictions_selftest "rc=$rc | FAIL lines $(grep -c '  FAIL' $RAW/mp.txt) | ok lines $(grep -c '  ok' $RAW/mp.txt) | $(tail -n 1 $RAW/mp.txt)"
timeout 900 nice -n 19 python3 -B rl/results/ladder_validation/read_ladder.py --selftest --export rl/results/ladder_validation/selftest_snapshot_2026-10-14 --repo . > $RAW/rl.txt 2>&1; rc=$?
put py:read_ladder_selftest "rc=$rc | FAIL lines $(grep -c '  FAIL' $RAW/rl.txt) | $(tail -n 1 $RAW/rl.txt)"
ut py:test_journal rl/deck_journal test_journal
ut py:floor_recheck_test_runners rl/results/floor_recheck_rules2_2026-10 test_runners
ut py:test_calibration_safety decks/screen/panel_ladder_2026-09-26 test_calibration_safety
ut py:test_run_screen_weights decks/screen test_run_screen_weights
(cd decks/screen && timeout 900 nice -n 19 python3 -B test_floor_pricing_pilot.py) > $RAW/fpp.txt 2>&1; rc=$?
put py:test_floor_pricing_pilot "rc=$rc | $(summ $RAW/fpp.txt)"
(cd rl/results/trainer_pricing_2026-09-28/km_run && timeout 900 nice -n 19 python3 -B read_km.py --selftest) > $RAW/km.txt 2>&1; rc=$?
put py:read_km_selftest "rc=$rc | $(tail -n 2 $RAW/km.txt | tr '\n' ' ' | sed "s#$WT#<WT>#g")"
d=$(mktemp -d -p /home/dacz8976/relplan); (cd rl/results/trainer_pricing_2026-09-28/km_run && timeout 900 nice -n 19 python3 -B test_km_thresholds.py $d/km) > $RAW/kmt.txt 2>&1; rc=$?
put py:test_km_thresholds "rc=$rc | $(tail -n 2 $RAW/kmt.txt | tr '\n' ' ' | sed -e "s#$d#<TMP>#g" -e "s#$WT#<WT>#g" -e 's/ in [0-9.]*s / /')"; rm -rf $d

# ---- the rl/strength modules (README's list, plus the night's two), JOBS at a time ---------------------------------------------
MODS="test_slow_report test_slow_report_runloop test_slow_report_process test_slow_report_page test_slow_report_registration
      test_strength_prereg_use test_strength_report test_slow_report_existing test_slow_report_paired test_split_collect test_strength_card_support"
for m in $MODS; do
  while [ "$(jobs -rp | wc -l)" -ge $JOBS ]; do sleep 2; done
  ( if [ ! -e rl/strength/$m.py ]; then echo absent > $RAW/strength_$m.rc; exit 0; fi
    cd rl/strength && timeout 1800 nice -n 19 python3 -B -m unittest $m > $RAW/strength_$m.txt 2>&1; echo $? > $RAW/strength_$m.rc ) &
done
wait
for m in $MODS; do
  if [ "$(cat $RAW/strength_$m.rc)" = absent ]; then put strength:$m absent
  else put strength:$m "rc=$(cat $RAW/strength_$m.rc) | $(summ $RAW/strength_$m.txt)"; fi
done
echo "=== done in $(( $(date +%s) - s )) s: $RES"
[ $MODE = baseline ] && exit 0

# ---- compare with the baseline -------------------------------------------------------------------------------------------------
B=$(cat $BASE_DIR/commit.txt)
git merge-base --is-ancestor $B HEAD || echo "WARNING: the baseline ${B:0:8} is not an ancestor of ${C:0:8}" | tee -a $OUT/compare.txt
python3 -I - $BASE_DIR/results.tsv $RES $B $C $OUT/draft_checks.md <<'EOF' | tee -a $OUT/compare.txt
import re, sys
bf, df, B, C, dc = sys.argv[1:]
rd = lambda p: dict(l.rstrip('\n').split('\t', 1) for l in open(p) if '\t' in l)
base, draft = rd(bf), rd(df)
HARN_TEST = 'FAIL: test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on (test_slow_report_registration.CommittedPin'
OWN = ('shape:', 'A1:', 'A2:', 'A3:', 'A4:', 'A5:', 'manifest:r6')
bad, expected, same = [], [], 0
for k in sorted(set(base) | set(draft)):
    b, d = base.get(k, '(missing)'), draft.get(k, '(missing)')
    if k.startswith(OWN):                                            # judged on the draft alone
        if not d.startswith('PASS'):
            bad.append(f'{k}: {d}')
        continue
    if k in ('manifest:available', 'manifest:history'):
        continue                                                     # expected to change; checked by manifest:r6
    if k == 'placeholders':
        if d not in ('none', '@@DRAFT_CHECKS@@'):
            bad.append(f'{k}: {d}')
        elif b != 'none':
            bad.append(f'{k}: the baseline has {b}')
        else:
            expected.append(f'{k}: {d}')
        continue
    if b == d:
        same += 1
        continue
    if k == 'strength:test_strength_card_support' and b == 'absent' and re.fullmatch(r'rc=0 \| Ran 4 \| OK \(skipped=4\) \| no FAIL/ERROR', d):
        expected.append(f'{k}: new with the preflight; skipped without STRENGTH_PROGRAM ({d})')
        continue
    if k == 'strength:test_slow_report_registration':
        pb, pd = b.split(' | '), d.split(' | ')
        fb = set(x for x in pb[3].split('; ') if x != 'no FAIL/ERROR') if len(pb) > 3 else set()
        fd = set(x for x in pd[3].split('; ') if x != 'no FAIL/ERROR') if len(pd) > 3 else set()
        new = fd - fb
        if len(pb) > 3 and len(pd) > 3 and pb[1] == pd[1] and not (fb - fd) and len(new) == 1 and next(iter(new)).startswith(HARN_TEST):
            expected.append(f'{k}: one more failure, CommittedPin\'s harness test (c4f7da21 v the pin\'s bf9c5d68), red until the re-pin')
            continue
    bad.append(f'{k}:\n    baseline {b}\n    draft    {d}')
print(f'baseline {B[:8]} v {C[:8]}: {same} checks equal; {len(expected)} expected differences; {len(bad)} other')
for e in expected:
    print('  expected:', e)
for x in bad:
    print('  NOT AS EXPECTED:', x)
print('VERDICT:', 'as expected' if not bad else 'NOT as expected: read the lines above, and bring them to the coordinator')
g = lambda k: draft.get(k, '(missing)')
lines = [
    f"Run before main moved, on {C[:8]}, with `r6_release/tools/verify_r6.sh draft <scratch worktree> {C[:8]} <baseline>`; the baseline is the same checks on main {B[:8]} (`verify_r6.sh baseline`). Python tests only, no engine run:",
    f"- The commit's shape: one parent, the build record, whose one parent is S; 13 paths ({g('shape:paths')}).",
    f"- The five activation checks: {g('A1:sha256sum_c')}; {g('A2:ls_tree')}; {g('A3:current_engine')}; {g('A4:manifest_v_sums')}; {g('A5:engine_tree')}. {g('manifest:available')}; {g('manifest:history')}.",
    f"- `make_predictions.py --selftest`: {g('py:make_predictions_selftest')}. `read_ladder.py --selftest`: {g('py:read_ladder_selftest')}.",
    f"- `test_journal`: {g('py:test_journal')}.",
    f"- `floor_recheck_rules2_2026-10/test_runners`: {g('py:floor_recheck_test_runners')}. `test_calibration_safety`: {g('py:test_calibration_safety')}. `test_run_screen_weights`: {g('py:test_run_screen_weights')}. `test_floor_pricing_pilot`: {g('py:test_floor_pricing_pilot')}. `read_km.py --selftest`: {g('py:read_km_selftest')}. `test_km_thresholds`: {g('py:test_km_thresholds')}.",
    "- `rl/strength`'s modules, KX_RUNS_DIR and STRENGTH_PROGRAM unset: " + '; '.join(f"{k.split(':', 1)[1]} {v}" for k, v in sorted(draft.items()) if k.startswith('strength:')) + '.',
    f"- Against the baseline: {same} checks equal; " + ('; '.join(expected) if expected else 'no difference') + ('.' if not bad else f'; NOT AS EXPECTED: {len(bad)}.'),
    f"- Placeholders: {g('placeholders')}.",
]
open(dc, 'w').write('\n'.join(lines) + '\n')
print('a first text for the notes (edit it, then pass it to adopt_r6.py --final as VARS["draft_checks"]):', dc)
EOF
