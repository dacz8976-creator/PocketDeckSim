import json, sys
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
for p in P:
    if any(a in p['id'] for a in sys.argv[1:]):
        print(json.dumps(p, ensure_ascii=False, indent=1))
