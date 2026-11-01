#!/bin/bash
# Who made the setup choices in G games? Kit constant, intervention kinds, calls v interventions, setup and opponent-turn counts.
R=/home/dacz8976/credit_work/gemini
Z=/home/dacz8976/relplan/gemini/stage2
O=$Z/score/setup_check.txt
{
grep -n "SHADOW_FEED" "$R/rl/ai_judge/game_kit.py"
grep -n "SHADOW_FEED\|'setup'" "$R/rl/ai_judge/game_bot.py" | head -12
python3 -I - "$Z/run" <<'PY'
import json, os, sys, collections
d = sys.argv[1]
G = [json.loads(l) for l in open(os.path.join(d, 'games.jsonl')) if l.strip()]
G = [a for a in G if a['arm'] == 'G']
kinds = collections.Counter()
for a in G:
    for k, v in (a['judge'].get('interventions_by_kind') or {}).items():
        kinds[k] += v
print('interventions_by_kind summed over G:', dict(kinds))
print('interventions', sum(a['judge']['interventions'] for a in G), 'calls', sum(a['judge']['calls'] for a in G),
      'fallbacks', sum(a['judge']['fallbacks'] for a in G), 'setup_decisions', sum(a['judge']['setup_decisions'] for a in G),
      'G games with setup decisions', sum(1 for a in G if a['judge']['setup_decisions']))
print('G games with opponent-turn points', sum(1 for a in G if (a['judge'].get('interventions_by_kind') or {}).get('opponent_turn')))
# decision rows: who answered setup rows?
seen = collections.Counter()
for a in G:
    p = os.path.join(d, 'deals', a['deal_tag'].rsplit('-a', 1)[0], 'a1', 'G', 'rows.jsonl')
    for l in open(p):
        r = json.loads(l)
        if r.get('schema') == 'gemini_game_decision_v1' and r.get('kind') == 'setup':
            seen[(r.get('mode'), bool(r.get('judge')), r.get('n_judge_calls'), r.get('fallback'))] += 1
print('setup decision rows by (mode, has judge block, n_judge_calls, fallback):', dict(seen))
r = json.load(open(os.path.join(d, G[0]['result_file'])))
print('engine_version in result files (first G):', r['engine_version'])
PY
} > "$O" 2>&1
cat "$O"
