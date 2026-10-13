import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
nk, nname, BYNAME = C['nk'], C['nname'], C['BYNAME']
# per game: how many of his Stage 2 came by Rare Candy (ledger), and positions whose board puts a Stage 1 under a Rare Candy'd Stage 2
for g in GAMES:
    short = short_of(g)
    ps = [p for p in POS if p['game'][3:] == short]
    if not ps:
        continue
    rc_turns = []
    for t in led(g)['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for pl in t.get('plays_in_order') or []:
            if nname(pl.get('card_name')) == 'Rare Candy' and 'attempt' not in str(pl.get('kind')):
                rc_turns.append(t['turn_number'])
    if not rc_turns:
        continue
    for p in ps:
        if p['turn_count'] <= rc_turns[0]:
            continue
        for b in p['me']['board']:
            n = b['card'].rsplit(' ', 2)[0]
            st = {c.get('stage') for c in BYNAME.get(n, []) if 'hp' in c}
            if st == {2}:
                print(p['id'], 'RC turns', rc_turns, '| Stage 2', b['card'], 'behind', b.get('behind'), '| deck Stage1 count in hand', sum(1 for h in p['me']['hand'] if h in (b.get('behind') or [])[1:]))
