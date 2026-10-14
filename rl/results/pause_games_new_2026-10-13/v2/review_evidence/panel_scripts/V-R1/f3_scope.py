import json
V2 = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/"
pos = json.load(open(V2 + 'positions_all.json', encoding='utf-8'))
for p in pos:
    pl = p['his_plan']
    for i, s in enumerate(pl):
        if s.startswith('Attack:'):
            nxt = pl[i + 1] if i + 1 < len(pl) else None
            if 'Giga Turbo' in s or 'Turbo' in s or (nxt and 'fx' in nxt):
                print(p['id'], s, '->', nxt, '| ended', p['his_plan_ended'], '| board', [b['card'] for b in p['me']['board']])
