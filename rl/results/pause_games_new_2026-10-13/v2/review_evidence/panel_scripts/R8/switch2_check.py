"""independent switch-2 flag check by printing: every card (both sides, incl. stacks, tools, stadium, opp discard, his deck file) whose DB text has one of the switch's titles"""
import json, os, re, sys, collections
sys.path.insert(0, '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
V2 = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-13/v2'
P = json.load(open(V2 + '/positions_all.json', encoding='utf-8'))
PL = {r['position_id']: r for r in json.load(open(V2 + '/position_list.json', encoding='utf-8'))}
TITLES = {'Wild Swing', 'Wellspring Dance', 'Tornado Shot', 'Double Splash', 'Triple Bombardment', 'Mischievous Ring', 'Litter', 'Cursed Jewel', 'Spike Armor',
          'Bristling Spikes', 'Needle Lariat', 'Shell Trap', 'Guts', 'Perish Body', 'Victory Star', 'Trap Territory', 'Carefree Steps', 'Celestial Blessing',
          'Guarded Grill', 'Securely Sheltered'}


def affected(cid):
    c = C.BYID.get(cid)
    if not c:
        return 'MISSING'
    t = set(C.titles(c)) & TITLES
    n = C.nname(c['name'])
    if n.startswith('Mega Kangaskhan ex'):
        t.add('Mega Kangaskhan second punch')
    if not C.is_pokemon(c) and (n in ('Will', 'Bounded Field') or 'Luxury Coin' in n or 'Fossil' in str(c.get('trainer_card_type')) or 'Fossil' in n or n == 'Old Amber'):
        t.add(n)
    return sorted(t)


def cid(s):
    m = re.search(r'([A-Z][A-Za-z0-9\-]{0,4} \d{3})$', s)
    return m.group(1)


cnt = collections.Counter()
for p in P:
    cards = list(p['me']['hand']) + list(p['me']['discard'])
    for b in p['me']['board'] + p['opp']['board']:
        cards += [b['card']] + b.get('behind', []) + b.get('tools', [])
    if p.get('stadium'):
        cards.append(p['stadium']['card'])
    cards += p['opp'].get('discard') or []
    deck = open(os.path.join(V2, 'decks', p['deck'] + '.txt'), encoding='utf-8').read().splitlines()[1:]
    cards += [l.split(' ', 1)[1] for l in deck]
    hits = {c: affected(cid(c)) for c in cards}
    hits = {c: v for c, v in hits.items() if v}
    poss = {}
    for a in p.get('opp_ambiguous') or []:
        for alt in a['could_also_be']:
            v = affected(alt)
            if v:
                poss[f"{a['name']} {alt}"] = v
    mine = 'yes' if hits else ('possible' if poss else 'no')
    pl = PL[p['id']]['switch2_flag']
    cnt[(mine, pl)] += 1
    if mine != pl or hits or poss:
        print(p['id'], 'mine', mine, 'list', pl, hits, poss)
print(dict(cnt))
