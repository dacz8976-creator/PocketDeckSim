import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
# usage: s12_turnplays.py GAMESUFFIX TURN [TURN...]
g = [x for x in GAMES if short_of(x).endswith(sys.argv[1])][0]
L = led(g)
for tn in map(int, sys.argv[2:]):
    t = [t for t in L['turns'] if t['turn_number'] == tn][0]
    pid = f'KW-{short_of(g)}-t{tn:02d}'
    print('########', pid, t.get('who_played'))
    for pl in t.get('plays_in_order') or []:
        print('   ', pl.get('order'), '|', pl.get('kind'), '|', pl.get('card_name'), '| tgt:', pl.get('target'), '| en:', json.dumps(pl.get('energy'), ensure_ascii=False) if pl.get('energy') else '', '| res:', str(pl.get('result'))[:220], '| resp:', str(pl.get('response'))[:80])
    p = POSBY.get(pid)
    if p:
        print('   PLAN', p['his_plan'], 'trunc', p['plan_truncated_at'])
        print('   NOTES', p['notes'][:600])
