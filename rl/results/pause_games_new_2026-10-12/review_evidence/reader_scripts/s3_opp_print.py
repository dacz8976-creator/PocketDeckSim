import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
BYNAME, nname, cid, opp_card, instances = C['BYNAME'], C['nname'], C['cid'], C['opp_card'], C['instances']


def sem(c):
    """the card as the engine plays it: type, hp, stage, attacks (title, cost, damage, text), ability, retreat, weakness"""
    keep = {k: c.get(k) for k in ('hp', 'stage', 'evolves_from', 'retreat_cost', 'weakness', 'type', 'energy_type', 'pokemon_type', 'ability', 'attacks', 'is_ex', 'trainer_card_type', 'text', 'effect')}
    return json.dumps(keep, sort_keys=True, ensure_ascii=False)


print('sample db card keys', list(BYNAME['Magnemite'][0].keys()))
print(json.dumps(BYNAME['Magnemite'][0], ensure_ascii=False)[:800])
# every opponent Pokemon in every converted position: which printing was chosen, and how many semantically different cards survive name+hp+title
amb = collections.defaultdict(list)
hp_mismatch = collections.defaultdict(list)
n_mon = 0
for p in POS:
    short = p['game'][3:]
    g = GBY['20' + short + '_iOS'] if ('20' + short + '_iOS') in GBY else None
    g = [x for x in GAMES if short_of(x) == short][0]
    L = led(g)
    t = [t for t in L['turns'] if t['turn_number'] == p['turn_count'] and str(t.get('who_played', '')).startswith('owner')][0]
    opp_inst = instances(t['board_at_start']['opponent'])
    assert len(opp_inst) == len(p['opp']['board']), p['id']
    for inst, b in zip(opp_inst, p['opp']['board']):
        n_mon += 1
        name = nname(inst['name'])
        chosen = b['card']
        assert chosen == opp_card(name, inst.get('hp_max'), inst.get('variant'))
        cands = [c for c in BYNAME.get(name, []) if 'hp' in c]
        by_hp = [c for c in cands if c.get('hp') == inst.get('hp_max')]
        chosen_c = [c for c in BYNAME[chosen.rsplit(' ', 2)[0]] if cid(c) == chosen][0]
        if chosen_c.get('hp') != inst.get('hp_max'):
            hp_mismatch[(name, inst.get('hp_max'), chosen, chosen_c.get('hp'), str(inst.get('variant')))].append(p['id'])
        pool = by_hp or cands
        vt = str(inst.get('variant') or '').split(';')[0]
        t2 = [c for c in pool if any(vt.startswith(a.get('title', '~')) for a in c.get('attacks', []))]
        pool2 = t2 or pool
        sems = collections.OrderedDict()
        for c in pool2:
            sems.setdefault(sem(c), []).append(c['id'])
        if len(sems) > 1:
            amb[(name, inst.get('hp_max'), str(inst.get('variant')), chosen, tuple(tuple(v) for v in sems.values()), bool(t2))].append(p['id'])
print('opponent Pokemon instances', n_mon)
print('\n== chosen printing HP differs from the ledger hp_max:', sum(len(v) for v in hp_mismatch.values()))
for k, v in hp_mismatch.items():
    print(k, len(v), v[:3])
print('\n== more than one semantically different card left after name+hp+title:', sum(len(v) for v in amb.values()), 'instances in', len({i for v in amb.values() for i in v}), 'positions')
for k, v in sorted(amb.items(), key=lambda kv: -len(kv[1])):
    print(k[:4], 'groups:', k[4], 'title-matched:', k[5], '|', len(v), v[:3])
