"""read-only: for every position of the Oct 6 batch, pair each board Pokemon with the ledger's board_at_start entry (same order as the converter)
and check that the position's printing has the ledger's printed HP and the attack/ability names in the ledger's variant text; also HP, Energy, Tool.
Also list deck names whose QR holds more than one distinct entity."""
import sys, json, re, os, collections
sys.dont_write_bytecode = True
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness'
sys.path.insert(0, H)
import ledger_to_positions as L  # noqa

B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
P = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
ALL = json.load(open(P, encoding='utf-8'))
BYID = {}
for c in L.CARDS:
    BYID[L.cid(c)] = c


def titles(c):
    t = [a.get('title') for a in c.get('attacks', []) if a.get('title')]
    if isinstance(c.get('ability'), dict) and c['ability'].get('title'):
        t.append(c['ability']['title'])
    return t


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower().replace('’', "'"))


games = sorted({p['game'][3:] for p in ALL})
for g in sorted(os.listdir(B)):
    if not g.endswith('_iOS'):
        continue
    short = g.replace('_iOS', '')[2:]
    if short not in games:
        continue
    led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
    T = {t['turn_number']: t for t in led['turns']}
    for p in [x for x in ALL if x['game'][3:] == short]:
        t = T[p['turn_count']]
        b = t['board_at_start']
        for sidek, posk in (('owner', 'me'), ('opponent', 'opp')):
            inst = L.instances(b[sidek])
            pb = p[posk]['board']
            if len(inst) != len(pb):
                print(p['id'], sidek, 'COUNT', len(inst), len(pb))
                continue
            for i, (li, pi) in enumerate(zip(inst, pb)):
                c = BYID.get(pi['card'])
                probs = []
                if c is None:
                    probs.append('card id not in DB')
                else:
                    if li.get('hp_max') is not None and c.get('hp') != li.get('hp_max'):
                        probs.append(f"printed HP {c.get('hp')} vs ledger hp_max {li.get('hp_max')}")
                    vt = norm(li.get('variant'))
                    tl = titles(c)
                    if tl and vt and not any(norm(x) in vt for x in tl):
                        # which printing of the name does carry the named attack?
                        alts = [L.cid(x) for x in L.BYNAME.get(L.nname(li['name']), []) if any(norm(y) in vt for y in titles(x))]
                        probs.append(f"titles {tl} not in ledger variant {li.get('variant')!r}; printings carrying it: {alts}")
                if pi['hp'] != li.get('hp_now'):
                    probs.append(f"hp {pi['hp']} vs ledger {li.get('hp_now')}")
                le = collections.Counter()
                for tt, n in L.ebt(li):
                    le[tt] += n
                if collections.Counter(pi.get('energy', [])) != le:
                    probs.append(f"energy {pi.get('energy')} vs ledger {dict(le)} (raw {json.dumps((li.get('attached_energy') or {}), ensure_ascii=False)[:120]})")
                ltool = li.get('tool')
                ltool = None if not ltool or str(ltool).lower() in ('none', 'null') else L.nname(ltool)
                ptool = pi.get('tools', [None])[0]
                if (ltool is None) != (ptool is None) or (ltool and not ptool.startswith(ltool)):
                    probs.append(f"tool {ptool} vs ledger {li.get('tool')}")
                if L.nname(li['name']) != pi['card'].rsplit(' ', 2)[0] and not pi['card'].startswith(L.nname(li['name'])):
                    probs.append(f"name {pi['card']} vs ledger {li['name']}")
                if probs:
                    print(p['id'], sidek, i, li['name'], pi['card'], '::', ' | '.join(probs))
print('done')
