import sys, re
sys.path.insert(0, '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
seen = set()
for c in C.CARDS:
    if C.is_pokemon(c):
        continue
    t = str(c.get('trainer_card_type'))
    eff = str(c.get('effect') or c.get('text') or '')
    if 'Tool' in t and re.search(r'HP', eff):
        k = (C.nname(c['name']), eff)
        if k not in seen:
            seen.add(k)
            print(c['id'], C.nname(c['name']), '|', eff)
for n in sys.argv[1:]:
    for c in C.BYNAME.get(n, []):
        print(n, c['id'], {k: v for k, v in c.items() if k not in ('id',)})
