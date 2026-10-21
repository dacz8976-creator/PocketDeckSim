import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, nk, cid, load_deck, convert_game = C['BYNAME'], C['nname'], C['nk'], C['cid'], C['load_deck'], C['convert_game']

decks = {}
for g in GAMES:
    try:
        pos, skip, dk = convert_game(g)
    except Exception as e:
        continue
    decks[short_of(g)] = dk

dropped = collections.defaultdict(list)
allk = collections.Counter()
for p in POS:
    short = p['game'][3:]
    g = [x for x in GAMES if short_of(x) == short][0]
    dk = decks[short]
    MINE = {c['name']: c['name'] + ' ' + c['variant'] for c in dk['counts_by_name_and_variant']}
    ispoke = {n: any('hp' in c for c in BYNAME.get(n, [])) for n in MINE}
    isbasic = {n: bool([c for c in BYNAME.get(n, []) if 'hp' in c]) and all(c.get('stage', 0) == 0 for c in BYNAME.get(n, []) if 'hp' in c) for n in MINE}
    TD = {n for n in MINE if not ispoke[n]}
    TOOLS = {n for n in TD if any('Tool' in str(c.get('trainer_card_type', '')) for c in BYNAME.get(n, []))}
    STAD = {n for n in TD if any('Stadium' in str(c.get('trainer_card_type', '')) for c in BYNAME.get(n, []))}
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    for pl in t.get('plays_in_order') or []:
        kind, card = nk(pl.get('kind')), nname(pl.get('card_name'))
        allk[(pl.get('kind'), kind)] += 1
        br = None
        if kind in ('card_play', 'bench') and card in MINE and ispoke[card] and isbasic[card]:
            br = 'Place'
        elif kind in ('card_play', 'item_evolution', 'stadium') and card == 'Rare Candy':
            br = 'RareCandy'
        elif kind == 'card_play' and card in MINE and ispoke[card]:
            br = 'Evolve(card_play)'
        elif kind in ('card_play', 'stadium') and card in MINE and card not in TOOLS:
            br = 'Play'
        elif kind == 'tool' or (kind == 'card_play' and card in TOOLS):
            br = 'Tool'
        elif kind == 'evolution':
            br = 'Evolve'
        elif kind in ('energy_attachment', 'retreat', 'attack'):
            br = kind
        elif kind == 'ability':
            br = 'ability'
        if br is None and str(pl.get('kind')).lower().replace(' ', '_') not in ('end_turn', 'end_turn_request'):
            dropped[(pl.get('kind'), kind, card)].append((p['id'], pl.get('order'), str(pl.get('target'))[:50], str(pl.get('result'))[:140]))
        if br == 'Evolve' and (card not in MINE):
            dropped[('EVOLVE card not in MINE', kind, card)].append((p['id'], pl.get('order'), str(pl.get('target'))[:50], str(pl.get('result'))[:100]))
        if br == 'Tool' and (card not in MINE):
            dropped[('TOOL card not in MINE', kind, card)].append((p['id'], pl.get('order'), str(pl.get('target'))[:50], str(pl.get('result'))[:100]))
print('owner play kinds in converted positions -> normalized:', sorted(allk.items(), key=lambda x: -x[1]))
print('\n== owner plays that give no plan step (end_turn excluded):', sum(len(v) for v in dropped.values()), 'in', len({x[0] for v in dropped.values() for x in v}), 'positions')
for k, v in dropped.items():
    print('##', k, len(v))
    for x in v:
        print('     ', x)
