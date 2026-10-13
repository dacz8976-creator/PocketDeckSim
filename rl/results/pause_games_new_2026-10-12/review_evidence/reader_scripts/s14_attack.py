import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME = C['BYNAME']
# every Attack step in every plan, and the ledger's attack row(s) of that turn
for p in POS:
    atk = [s for s in p['his_plan'] if s.startswith('Attack:')]
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    t = [t for t in led(g)['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    rows = [pl for pl in t.get('plays_in_order') or [] if C['nk'](pl.get('kind')) == 'attack']
    flag = []
    for pl in rows:
        txt = (str(pl.get('card_name')) + ' ' + str(pl.get('result')) + ' ' + str(pl.get('attack_name') or '')).replace('’', "'")
        flag.append(txt[:160])
    note = 'attack title of' in p['notes']
    if note or len(rows) != len(atk) or any(':' not in s for s in atk):
        print(p['id'], 'plan attacks', atk, '| ledger attack rows', flag, '| fallback note' if note else '', '| trunc', p['plan_truncated_at'])
