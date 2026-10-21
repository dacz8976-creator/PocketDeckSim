import sys, json, collections, re
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
AFF = {
    '261005_031138000': {'Spritzee', 'Aromatisse', 'Togepi'},
    '261005_032023000': {'Aegislash'},
    '261005_032857000': {'Aegislash'},
    '261005_033529000': {'Aegislash'},
    '261005_034953000': {'Honedge', 'Doublade', 'Aegislash'},
    '261006_012927000': {'Meowth'},
    '261006_020518000': {'Conkeldurr', 'Sandslash'},
    '261010_012303000': {'Conkeldurr'},
    '261010_013009000': {'Conkeldurr'},
    '261004_213625000': {'Caterpie', 'Metapod', 'Butterfree'},
    '261005_003547000': {'Carvanha', 'Wailmer'},
}
tot = 0; direct = 0
for gname, names in AFF.items():
    ps = [p for p in POS if p['game'][3:] == gname]
    d = []
    for p in ps:
        here = {c.rsplit(' ', 2)[0] for c in p['me']['hand']} | {b['card'].rsplit(' ', 2)[0] for b in p['me']['board']} | {x.rsplit(' ', 2)[0] for b in p['me']['board'] for x in b.get('behind', [])}
        if here & names:
            d.append(p['id'].split('-t')[1])
    tot += len(ps); direct += len(d)
    print(gname, sorted(names), 'positions', len(ps), 'with the card in hand/board:', len(d), d)
print('total positions in affected games', tot, '; with an affected name in hand/board', direct)
