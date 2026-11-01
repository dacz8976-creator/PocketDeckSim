#!/bin/bash
# (a) Does the went_first field read right, and did G and K have the same first player? Test: with odd turns = the first
#     player's, does the winner own the final turn? Count per arm, using G's went_first for both arms.
# (b) Registration text on intervention points / setup, and on what each pilot knows about the opponent's deck.
D=/home/dacz8976/relplan/gemini/stage2/run
R=/home/dacz8976/credit_work/gemini
python3 -I - "$D" <<'PY'
import json, os, sys, collections
d = sys.argv[1]
arms = {}
for l in open(os.path.join(d, 'games.jsonl')):
    if l.strip():
        a = json.loads(l); arms[a['deal_tag']] = a
deals = [json.loads(l) for l in open(os.path.join(d, 'deals.jsonl')) if l.strip()]
tally = collections.Counter()
first_by_group = collections.Counter()
for dl in deals:
    g, k = arms[dl['g_deal_tag']], arms[dl['k_deal_tag']]
    wf = g['judge']['went_first']
    first_by_group[(dl['bits']['seat'], dl['bits']['deck'], wf)] += 1
    for name, a in (('G', g), ('K', k)):
        r = json.load(open(os.path.join(d, a['result_file'])))
        w = r['outcome']['Win']
        owner = wf if r['final_turn'] % 2 == 1 else 1 - wf
        tally[(name, 'winner owns final turn' if owner == w else 'winner does NOT own final turn')] += 1
for key in sorted(tally):
    print(key, tally[key])
print('first player by (pilot seat, deck bit, seat that went first):')
for key in sorted(first_by_group):
    print('  ', key, first_by_group[key])
PY
echo '=== registration section 3 (intervention points)'
sed -n '107,123p' "$R/rl/ai_judge/GEMINI_GAME_TEST_REGISTRATION.md"
echo '=== opponent knowledge mentions'
grep -nE "knows the opponent|opponent's list|opponent list|opponent-deck|opp_deck|POOL" "$R/rl/ai_judge/GEMINI_GAME_TEST_REGISTRATION.md" | head -20
grep -nE "POOL_SHA256|pool" "$R/rl/ai_judge/game_kit.py" | head -8
