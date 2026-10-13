import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
nk, etype = C['nk'], C['etype']
n = 0
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    t = [t for t in led(g)['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    for pl in t.get('plays_in_order') or []:
        if nk(pl.get('kind')) != 'energy_attachment':
            continue
        e = pl.get('energy') or {}
        if not etype(e.get('type')):
            n += 1
            print(p['id'], 'attach with no readable type -> deck fallback | energy', json.dumps(e, ensure_ascii=False)[:120], '| card', pl.get('card_name'), '| res', str(pl.get('result'))[:100])
        # attachments not from the zone (ability / supporter)
        src = (str(e.get('source') or '') + ' ' + str(pl.get('result') or '') + ' ' + str(pl.get('card_name') or '')).lower()
        if re.search(r'wally|ability|supporter|from discard|discard pile|ignition|dragon', src) and 'zone' not in src:
            print(p['id'], 'attach maybe not from the zone |', pl.get('kind'), pl.get('card_name'), str(pl.get('result'))[:120])
print('fallback count', n)
