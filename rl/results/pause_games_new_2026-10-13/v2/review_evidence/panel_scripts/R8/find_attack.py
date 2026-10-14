import sys
sys.path.insert(0, '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
for q in sys.argv[1:]:
    print('###', q)
    seen = set()
    for c in C.CARDS:
        ts = C.titles(c)
        if any(q.lower() in t.lower() for t in ts):
            k = C.SIG[c['id']]
            if k in seen:
                continue
            seen.add(k)
            print('  ', c['id'], C.nname(c['name']), c.get('hp'), ts, [a.get('effect') for a in c.get('attacks') or []][:2], (c.get('ability') or {}).get('effect') if isinstance(c.get('ability'), dict) else '')
