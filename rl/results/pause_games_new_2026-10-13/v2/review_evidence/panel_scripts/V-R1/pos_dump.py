import json, sys
P = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
A = json.load(open(P, encoding='utf-8'))
pos = A if isinstance(A, list) else A.get('positions', A)
print(type(A), len(pos))
want = sys.argv[1:]
for p in pos:
    if any(w in p['id'] for w in want):
        print('=' * 80)
        print(json.dumps(p, ensure_ascii=False, indent=1))
