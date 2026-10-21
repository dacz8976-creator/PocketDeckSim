#!/bin/bash
# verify_draft.sh COMMIT [WT] [ENGINE_DIR]: check an adoption draft in a scratch worktree (no engine run; python tests only).
C=$1; WT=${2:-/home/dacz8976/adopt_w}; ED=${3:-rl/engine-2026-10-20}
cd /home/dacz8976/pincand
[ -e $WT ] && { git worktree remove --force $WT || exit 1; }
git worktree add -q --detach $WT $C || exit 1
cd $WT
echo "=== HEAD $(git rev-parse --short HEAD); status clean: $(git status --porcelain | wc -l) changes"
echo "=== sha256sum -c"; (cd $ED && sha256sum -c SHA256SUMS); ls -l $ED/ | cut -c1-11,40-
echo "=== current_engine.py"; python3 -B current_engine.py; echo "rc=$?"
ED=$ED python3 -B - <<'EOF'
import json, os
m = json.load(open('project_manifest.json'))
a = m['available_release']
s = dict(l.split()[::-1] for l in open(os.environ['ED'] + '/SHA256SUMS'))
print('manifest v SHA256SUMS:', a['sha256'] == s['deckgym'] and a['legality_scan_sha256'] == s['legality_scan'] and a['goldfish_sha256'] == s['goldfish'])
print('history tail:', [r['name'] for r in m['historical_releases'][-3:]], '| available:', a['name'], a['source_commit'][:8])
EOF
echo "=== make_predictions --selftest"; s=$(date +%s)
python3 -B rl/results/ladder_validation/make_predictions.py --selftest --repo . > /tmp/mp_selftest.txt 2>&1; echo "rc=$? in $(( $(date +%s) - s )) s; FAIL lines: $(grep -c '  FAIL' /tmp/mp_selftest.txt); ok lines: $(grep -c '  ok' /tmp/mp_selftest.txt)"
grep '  FAIL' /tmp/mp_selftest.txt | head; tail -n 3 /tmp/mp_selftest.txt
echo "=== read_ladder --selftest"; python3 -B rl/results/ladder_validation/read_ladder.py --selftest --export rl/results/ladder_validation/selftest_snapshot_2026-10-14 --repo . > /tmp/rl_selftest.txt 2>&1; echo "rc=$?; FAIL lines: $(grep -c '  FAIL' /tmp/rl_selftest.txt)"; grep '  FAIL' /tmp/rl_selftest.txt | head; tail -n 2 /tmp/rl_selftest.txt
echo "=== test_journal"; (cd rl/deck_journal && timeout 900 python3 -B -m unittest test_journal 2>&1 | grep -E '^(FAIL|ERROR):|^Ran|^OK|^FAILED')
echo "=== floor_recheck test_runners"; (cd rl/results/floor_recheck_rules2_2026-10 && timeout 900 python3 -B -m unittest test_runners 2>&1 | tail -n 4)
echo "=== panel_ladder test_calibration_safety"; (cd decks/screen/panel_ladder_2026-09-26 && timeout 900 python3 -B -m unittest test_calibration_safety 2>&1 | tail -n 4)
echo "=== CI: decks/screen test_run_screen_weights, test_floor_pricing_pilot"; (cd decks/screen && timeout 900 python3 -B -m unittest test_run_screen_weights 2>&1 | tail -n 3; timeout 900 python3 -B test_floor_pricing_pilot.py 2>&1 | tail -n 3)
echo "=== CI: km_run read_km --selftest, test_km_thresholds"; (cd rl/results/trainer_pricing_2026-09-28/km_run && timeout 900 python3 -B read_km.py --selftest 2>&1 | tail -n 2; d=$(mktemp -d); timeout 900 python3 -B test_km_thresholds.py $d/km 2>&1 | tail -n 2; rm -rf $d)
echo "=== placeholders"; git grep -I -c '@@' HEAD -- START_HERE.md CLAUDE.md rl/RUN5.md rules project_manifest.json $ED rl/results/ladder_validation/make_predictions.py | head
cd /home/dacz8976/pincand; git worktree remove --force $WT; git worktree prune
