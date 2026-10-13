"""read-only: hand cards whose ledger text names an attack/ability (or set number) of a different printing than the position's card"""
import sys, json, os, re
sys.dont_write_bytecode = True
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness'
sys.path.insert(0, H)
import ledger_to_positions as L  # noqa
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
P = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
ALL = json.load(open(P, encoding='utf-8'))
BYID = {L.cid(c): c for c in L.CARDS}


def titles(c):
    t = [a.get('title') for a in c.get('attacks', []) if a.get('title')]
    if isinstance(c.get('ability'), dict) and c['ability'].get('title'):
        t.append(c['ability']['title'])
    return t


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower().replace('’', "'"))


for g in sorted(os.listdir(B)):
    if not g.endswith('_iOS'):
        continue
    short = g.replace('_iOS', '')[2:]
    ps = [x for x in ALL if x['game'][3:] == short]
    if not ps:
        continue
    led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
    T = {t['turn_number']: t for t in led['turns']}
    for p in ps:
        hs = (T[p['turn_count']].get('hand_at_start') or {}).get('cards_left_to_right') or []
        for i, (c, pc) in enumerate(zip(hs, p['me']['hand'])):
            text = (c.get('name', '') + ' ' + str(c.get('variant') or '')) if isinstance(c, dict) else str(c)
            card = BYID.get(pc)
            if card is None or 'hp' not in card:
                continue
            vt = norm(text[len(L.nname(c.get('name') if isinstance(c, dict) else c) or ''):] if False else text)
            mine = titles(card)
            others = [x for x in L.BYNAME.get(L.nname(card['name']), []) if L.cid(x) != pc and sorted(titles(x)) != sorted(mine)]
            hit_other = [L.cid(x) for x in others if any(norm(t) in vt for t in titles(x) if len(norm(t)) >= 4 and norm(t) not in norm(card['name']))]
            hit_mine = any(norm(t) in vt for t in mine if len(norm(t)) >= 4 and norm(t) not in norm(card['name']))
            if hit_other and not hit_mine:
                print(p['id'], 'hand', i, repr(text), '-> position', pc, '; text matches', hit_other)
print('done')
