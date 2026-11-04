#!/bin/bash
# R8 switch steps 3-4 (113 §3-4, as R6 night_r6.sh 155-186): K8 build record re-check, strength_tests, then sc_kx3 and floor2.py in parallel.
set -u
W=/home/dacz8976/pincand_work; RR=$W/RR_R8_543dad00; N=$RR/sw3; mkdir -p $N
SWT=/home/dacz8976/lane_r8_w; P=$W/RR_R8_48dec4f5/strength/K8/strength
K=b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0; T=f33d2c49baf432d4bd1e407b96a6c243471fa9b6
HARN=c4f7da21563393049a21a7ca41778ea3a916b99bde5a9bec33fbe3b700f0a149
GYM=$RR/programs/deckgym; GSHA=75090673c20939a0aee431eb293dde0d2a988194da0b8429604a7570dc150310
SCRUB=$(env | cut -d= -f1 | grep -E '^(KX_|PDL_|DECKGYM_|JEV_|PG_)' | sed 's/^/-u /' | tr '\n' ' ')
[ -e /home/dacz8976/credit_work/PAUSE ] && { echo "PAUSE present: not starting"; exit 1; }
[ "$(git -C $SWT rev-parse HEAD)" = "$(git -C /home/dacz8976/pincand rev-parse 543dad00)" ] && [ -z "$(git -C $SWT status --porcelain --untracked-files=no)" ] || { echo "STOP: lane_r8_w not clean at 543dad00"; exit 1; }
[ "$(sha256sum < $GYM | cut -c1-64)" = $GSHA ] || { echo "STOP: deckgym sha"; exit 1; }
[ -e $W/floor2R8 ] && { echo "STOP: $W/floor2R8 exists"; exit 1; }
echo "== record"
python3 -I - $P $K $T $HARN <<'EOF' | tee $N/record_check.txt
import hashlib, json, sys
p, k, t, h = sys.argv[1:]
r = json.load(open(p + '.build.json'))
want = dict(engine_ref=k, engine_tree_archived=t, harness_source_sha256=h, jobs='2')
bad = {x: (r.get(x), v) for x, v in want.items() if r.get(x) != v}
sha = hashlib.sha256(open(p, 'rb').read()).hexdigest()
if sha != r.get('program_sha256'):
    bad['program_sha256'] = (r.get('program_sha256'), sha)
print(('RECORD OK ' if not bad else 'RECORD BAD %r ' % bad) + sha)
EOF
grep -q '^RECORD OK ' $N/record_check.txt || { echo "STOP: record"; exit 1; }
echo "== sc_kx3 (background)"
setsid nohup bash -c "cd $SWT; s=\$(date +%s); env $SCRUB nice -n 19 $P selfcheck --root $SWT --pilot kx3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12 > $N/sc_kx3.full 2>$N/sc_kx3.err; echo \"\$? \$(( \$(date +%s) - s ))\" > $N/sc_kx3.rc" > /dev/null 2>&1 &
echo "started $(date -u +%FT%TZ)"
echo "== floor2.py (background) v floor2S"
setsid nohup bash -c "cd /home/dacz8976/pincand && s=\$(date +%s); FLOOR2_GYM=$GYM FLOOR2_SHA=$GSHA FLOOR2_OUT=$W/floor2R8 FLOOR2_ALSO_VS=$W/floor2S nice -n 19 python3 -u $W/floor2.py > $N/floor.log 2>&1; echo \"\$? \$(( \$(date +%s) - s ))\" > $N/floor.rc" > /dev/null 2>&1 &
echo "== strength_tests (foreground)"
( cd $SWT/rl/strength && env $SCRUB STRENGTH_PROGRAM=$P nice -n 19 python3 -B -m unittest -v test_strength_card_support ) > $N/strength_refusal.log 2>&1
rrc=$?; echo "refusal: rc=$rrc $(grep -E '^(Ran|OK|FAILED)' $N/strength_refusal.log | tr '\n' ' ')"
( cd $SWT/rl/strength && env $SCRUB nice -n 19 python3 -B -m unittest test_slow_report test_slow_report_runloop test_slow_report_process test_slow_report_page test_slow_report_registration test_strength_prereg_use test_strength_report test_slow_report_existing test_slow_report_paired test_split_collect test_strength_card_support ) > $N/strength_py.log 2>&1
echo "py suite: rc=$? $(grep -E '^(Ran|OK|FAILED)' $N/strength_py.log | tr '\n' ' '); failing: $(grep -E '^(FAIL|ERROR):' $N/strength_py.log | cut -c1-160 | tr '\n' ';')"
