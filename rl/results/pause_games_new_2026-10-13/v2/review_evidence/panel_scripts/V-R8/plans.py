import json
V = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2/positions_all.json"
for p in json.load(open(V, encoding='utf-8')):
    if any(g in p['id'] for g in ('225319', '230258', '203719', '010003', '020824', '010706', '210041', '210823')):
        if 'UseStadium' in p['his_plan'] or 'Play:Mesagoza' in p['his_plan']:
            print(p['id'], p['his_plan'])
