import json, sys
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
S = json.load(open(V2 + '/runs_forced/forced_summary.json', encoding='utf-8'))
for s in S:
    if not sys.argv[1:] or any(a in s['id'] for a in sys.argv[1:]):
        print(s['id'], '| force', s['force'], '| note', s['note'])
        for r in s['rows']:
            print('    ', r)
