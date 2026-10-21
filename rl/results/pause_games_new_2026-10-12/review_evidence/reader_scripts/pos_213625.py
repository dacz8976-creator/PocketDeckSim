import json, sys
p = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
d = json.load(open(p, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('positions', d)
if isinstance(items, dict):
    print('top keys', list(items.keys())[:20])
    items = list(items.values())
for pos in items:
    pid = pos.get('id') or pos.get('position_id')
    if pid and '213625' in pid:
        print('=====', pid)
        print(json.dumps(pos, indent=1, ensure_ascii=False))
