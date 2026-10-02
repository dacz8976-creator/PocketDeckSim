#!/usr/bin/env bash
# tests of the harness: resume (with a truncated last line), external pilot, held-out guard, selfcheck
T=/home/dacz8976/sh/tree
S=$T/rl/strength
BIN=/home/dacz8976/strength_build/strength
C=/home/dacz8976/sh/cfg
RUNS=/home/dacz8976/sh/runs
cd "$T"

echo "=============== A. resume (stop at 50 games, a torn last line, then finish) and compare with the straight run"
sed 's/smoke_km3_kog3/resume_test/' $C/smoke_km3_kog3.json > $C/resume_test.json
rm -rf $RUNS/resume_test
python3 $S/strength_prereg.py --config $C/resume_test.json --out $RUNS/resume_test --repo "$T" | tail -1
nice -n 19 $BIN run --manifest $RUNS/resume_test/manifest.json --out $RUNS/resume_test --max-games 50 2>&1 | tail -2
echo "after the first stop: $(wc -l < $RUNS/resume_test/games.jsonl) games"
printf '{"key":"torn|line' >> $RUNS/resume_test/games.jsonl
nice -n 19 $BIN run --manifest $RUNS/resume_test/manifest.json --out $RUNS/resume_test 2>&1 | head -1
nice -n 19 $BIN run --manifest $RUNS/resume_test/manifest.json --out $RUNS/resume_test 2>&1 | tail -2
python3 - <<'EOF'
import json
def load(p):
    out = {}
    for l in open(p):
        try: r = json.loads(l)
        except Exception: continue
        out[r['key']] = (r['winner'], tuple(r['points']), r['turns'], r['first'])
    return out
a = load('/home/dacz8976/sh/runs/smoke_km3_kog3/games.jsonl'); b = load('/home/dacz8976/sh/runs/resume_test/games.jsonl')
print('straight run', len(a), 'games; resumed run', len(b), 'games; identical results for every key:', a == b)
EOF

echo "=============== B. an external pilot (the protocol example) against km3: runtime and notes"
cat > $C/ext_test.json <<EOF
{"name": "ext_test", "question": "Protocol test: the example external pilot (prefers an attack) against km3.",
 "pilot": "ext:python3 rl/strength/ext_pilot_example.py attack", "reference": "km3", "decks": ["t-altaria"], "opponents": ["t-blaziken"], "deals": 3, "seats": [0, 1], "threads": 2}
EOF
rm -rf $RUNS/ext_test
python3 $S/strength_prereg.py --config $C/ext_test.json --out $RUNS/ext_test --repo "$T" | tail -1
nice -n 19 $BIN run --manifest $RUNS/ext_test/manifest.json --out $RUNS/ext_test 2>&1 | tail -2
echo "errors: $(wc -l < $RUNS/ext_test/errors.jsonl 2>/dev/null || echo 0)"
python3 - <<'EOF'
import json
for l in open('/home/dacz8976/sh/runs/ext_test/games.jsonl'):
    g = json.loads(l)
    if g['arm'] == 'X':
        print(g['key'], g['winner'], 'turns', g['turns'], 'wall', g['wall_s'], 'decisions', g['moves_deck']['n'], 'notes', len(g.get('ext_deck', {}).get('notes', [])), (g.get('ext_deck', {}).get('notes') or [''])[0])
        break
EOF
python3 $S/strength_report.py --dir $RUNS/ext_test | sed -n '/## Runtime/,/## What more/p' | head -14

echo "=============== C. the held-out guard"
cp $S/heldout.json /tmp/heldout_backup.json
cat > $S/heldout.json <<'EOF'
{"locked": true, "unlocked_by": null, "decks": ["t-lucario"]}
EOF
python3 $S/strength_prereg.py --config $C/smoke_km3_kog3.json --out $RUNS/guard_test --repo "$T" ; echo "prereg exit code: $?"
rm -rf $RUNS/guard_test
cp /tmp/heldout_backup.json $S/heldout.json
# the program's own check: a manifest that lists a held-out deck among its decks
python3 - <<'EOF'
import json
m = json.load(open('/home/dacz8976/sh/runs/ext_test/manifest.json')); m['heldout_decks'] = ['t-blaziken']; m['heldout_locked'] = True
import os; os.makedirs('/home/dacz8976/sh/runs/guard_test', exist_ok=True)
json.dump(m, open('/home/dacz8976/sh/runs/guard_test/manifest.json', 'w'))
EOF
$BIN run --manifest $RUNS/guard_test/manifest.json --out $RUNS/guard_test 2>&1 | grep -E "refusing" | head -1 | cut -c1-200; echo "program exit code: ${PIPESTATUS[0]}"

echo "=============== D. selfcheck digest (a build can be compared with another: same digest = same pilot behaviour)"
$BIN selfcheck --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12
