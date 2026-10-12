import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
instances = C['instances']
# usage: GAMESUFFIX TURN  -> owner board_after of TURN-2's owner turn ... and the opponent turn plays/auto events between
g = [x for x in GAMES if short_of(x).endswith(sys.argv[1])][0]
turns = led(g)['turns']
tn = int(sys.argv[2])
T = {t['turn_number']: t for t in turns}
pt = T[tn - 2]
print('his previous turn', tn - 2, 'board_after owner:', [(p['name'], p.get('hp_now'), p.get('bench_position')) for p in instances(pt['board_after']['owner'])])
ot = T[tn - 1]
print('opp turn', tn - 1)
for pl in ot.get('plays_in_order') or []:
    print('   play', pl.get('kind'), '|', pl.get('card_name'), '|', pl.get('target'), '|', str(pl.get('result'))[:200])
for e in ot.get('automatic_events_in_order') or []:
    print('   auto', json.dumps(e, ensure_ascii=False)[:300])
print('this turn', tn, 'board_at_start owner:', [(p['name'], p.get('hp_now'), p.get('bench_position')) for p in instances(T[tn]['board_at_start']['owner'])])
