import json, sys
P = json.load(open(r'C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\rl\results\pause_games_new_2026-10-12\positions_all.json', encoding='utf-8'))
for p in P:
    if p['id'] in sys.argv[1:]:
        print(json.dumps(p, ensure_ascii=False, indent=1))
