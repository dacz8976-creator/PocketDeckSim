import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
load_deck, etype, ebt, instances = C['load_deck'], C['etype'], C['ebt'], C['instances']


def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f'[{i}]')
    else:
        yield path, o


print('== deck energy as parsed vs every energy-ish field in DECK_USED')
for g in GAMES:
    d = deck(g)
    cards, energy, src = load_deck(d)
    fields = {}
    for k, v in d.items():
        if 'energy' in k.lower():
            fields[k] = v
        elif isinstance(v, dict):
            for k2, v2 in v.items():
                if 'energy' in k2.lower():
                    fields[k + '.' + k2] = v2
    # energy types seen in the ledger on his side
    L = led(g)
    seen = collections.Counter()
    for t in L['turns']:
        for key in ('board_at_start', 'board_after'):
            side = ((t.get(key) or {}).get('owner')) or {}
            ez = side.get('energy_zone') or {}
            for slot in ('this_turn', 'next'):
                ty = (ez.get(slot) or {}).get('type')
                if ty:
                    seen[str(ty)] += 1
    print(short_of(g), 'parsed:', repr(energy), '| fields:', json.dumps(fields, ensure_ascii=False)[:300], '| his zone types in ledger:', dict(seen))

print('\n== positions: energy fields and where they came from')
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    b = t['board_at_start']
    ez, oz = b['owner'].get('energy_zone') or {}, b['opponent'].get('energy_zone') or {}
    src = []
    if p['me']['energy_now'] is not None and not etype((ez.get('this_turn') or {}).get('type')):
        src.append(f"energy_now={p['me']['energy_now']} not from the zone (this_turn={ez.get('this_turn')})")
    if not etype((ez.get('next') or {}).get('type')):
        src.append(f"energy_next={p['me']['energy_next']} fallback (next={ez.get('next')})")
    if not etype((oz.get('next') or {}).get('type')):
        src.append(f"opp energy_next={p['opp']['energy_next']} from {'this_turn' if etype((oz.get('this_turn') or {}).get('type')) else 'HIS deck energy'} (opp zone={json.dumps({k: oz.get(k) for k in ('this_turn', 'next')})})")
    if src:
        print(p['id'], ' | '.join(src))
