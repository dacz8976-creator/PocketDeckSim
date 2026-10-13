import sys, json, importlib.util
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py'
spec = importlib.util.spec_from_file_location('l2p', H)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
v = 'Dragon’s Blessing / Draconic Whip 40; 80 HP'
print('opp_card ->', m.opp_card('Dragonair', 80, v))
print('BYNAME order:')
for c in m.BYNAME['Dragonair']:
    print('  ', c.get('id'), 'hp', c.get('hp'), 'retreat', c.get('retreat_cost'), 'attacks', [a.get('title') for a in c.get('attacks', [])], 'ability', (c.get('ability') or {}).get('title') if isinstance(c.get('ability'), dict) else c.get('ability'))
vt = v.split(';')[0]
print('vt =', repr(vt))
for c in m.BYNAME['Dragonair']:
    if c.get('hp') == 80:
        print('  ', c['id'], [ (a.get('title'), vt.startswith(a.get('title', '~'))) for a in c.get('attacks', [])])
# what a tie-break on any title contained in the text would give
for c in m.BYNAME['Dragonair']:
    if c.get('hp') == 80:
        ttl = [a.get('title') for a in c.get('attacks', [])]
        ab = c.get('ability')
        if isinstance(ab, dict):
            ttl.append(ab.get('title'))
        print('  contains-any', c['id'], [(t, t.replace("'", '’') in v or t in v) for t in ttl if t])
# all opponent cards in all games whose variant text does not start with an attack title of the chosen printing, where >1 printing shares the HP
