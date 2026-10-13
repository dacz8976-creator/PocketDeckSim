import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
for p in POS:
    kos = re.findall(r'knocked out between turns: ([^;.]+)', p['notes'])
    if not kos:
        continue
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    turns = led(g)['turns']
    prev = [t for t in turns if t['turn_number'] == p['turn_count'] - 1]
    txt = ''
    for t in prev:
        for pl in (t.get('plays_in_order') or []) + (t.get('automatic_events_in_order') or []):
            s = json.dumps(pl, ensure_ascii=False)
            if re.search(r'KO|knock', s, re.I):
                if isinstance(pl, dict):
                    txt += ' || ' + (str(pl.get('kind')) + ': ' + str(pl.get('result') or pl.get('description') or pl.get('event') or s))[:200]
                else:
                    txt += ' || ' + s[:200]
    print(p['id'], 'KO notes', kos, '| opp turn KO text:', txt[:500] if txt else 'NONE FOUND')
