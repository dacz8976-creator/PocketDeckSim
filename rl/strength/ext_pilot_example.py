#!/usr/bin/env python3
"""A minimal external pilot for the strength harness (PROTOCOL.md): prefers an attack, otherwise the first action that is not EndTurn.
    ext:python3 rl/strength/ext_pilot_example.py [first|random|attack]     (random uses the game seed, so it repeats)
It is a protocol example, not a good player."""
import json, random, sys

mode = sys.argv[1] if len(sys.argv) > 1 else 'attack'
rng = random.Random(0)
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    msg = json.loads(line)
    if msg['type'] == 'hello':
        rng = random.Random(msg['seed'] * 2 + msg['seat'])
        continue
    if msg['type'] == 'end':
        break
    if msg['type'] != 'decide':
        continue
    acts = msg['actions']
    pick = None
    if mode == 'random':
        pick = rng.choice(acts)['i']
    elif mode == 'first':
        pick = acts[0]['i']
    else:
        attacks = [a for a in acts if a['label'].startswith('Attack:')]
        others = [a for a in acts if a['label'] != 'EndTurn']
        pick = (attacks or others or acts)[0]['i']
    print(json.dumps({'choice': pick, 'note': f"{mode}: {acts[pick]['label']}"}), flush=True)
