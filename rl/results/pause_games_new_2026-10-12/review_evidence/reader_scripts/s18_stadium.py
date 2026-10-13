import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname = C['BYNAME'], C['nname']
STADS = {n for n, cs in BYNAME.items() if any('Stadium' in str(c.get('trainer_card_type', '')) for c in cs)}
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    turns = led(g)['turns']
    last = None
    hist = []
    for t in turns:
        if t['turn_number'] >= p['turn_count']:
            break
        who = 'me' if str(t.get('who_played', '')).startswith('owner') else 'opp'
        for pl in t.get('plays_in_order') or []:
            cn = nname(pl.get('card_name'))
            if cn in STADS and 'attempt' not in str(pl.get('kind')) and C['nk'](pl.get('kind')) in ('stadium', 'card_play'):
                last = (who, cn, t['turn_number'])
                hist.append(last)
    t = [t for t in turns if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    st = t['board_at_start'].get('stadium')
    pst = p['stadium']
    exp_owner = None if last is None else (0 if last[0] == 'me' else 1)
    flag = ''
    if pst and last and (nname(pst['card'].rsplit(' ', 2)[0]) != last[1] or pst['owner'] != exp_owner):
        flag = 'MISMATCH'
    if (pst is None) != (last is None):
        flag = 'PRESENCE?'
    # his stadiums replaced by his own
    mine_seq = [h for h in hist if h[0] == 'me']
    if flag or len(hist) > 1:
        print(p['id'], flag, '| pos stadium', pst, '| ledger stadium', json.dumps(st, ensure_ascii=False)[:80], '| history', hist, '| discard stadiums', [c for c in p['me']['discard'] if c.rsplit(' ', 2)[0] in STADS])
