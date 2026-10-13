"""read-only: per game of the Oct 6 batch, the QR's printing aliases per entity vs the converter's deck file (same card = same DB signature)"""
import sys, json, re, os, glob, collections
sys.dont_write_bytecode = True
H = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness'
sys.path.insert(0, H)
import ledger_to_positions as L  # noqa
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
D = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/decks/'
BYID = {L.cid(c): c for c in L.CARDS}
BYPRINT = {}
for c in L.CARDS:
    BYPRINT[str(c['id'])] = c


def sig(c):
    if c is None:
        return None
    return json.dumps({'n': L.nname(c.get('name')), 'hp': c.get('hp'), 'a': [(a.get('title'), a.get('energy_required') or a.get('cost'), a.get('fixed_damage') or a.get('damage')) for a in c.get('attacks', [])],
                       'ab': (c.get('ability') or {}).get('title') if isinstance(c.get('ability'), dict) else None, 'eff': [a.get('effect') for a in c.get('attacks', [])]}, ensure_ascii=False, sort_keys=True)


def find_entities(o, out):
    if isinstance(o, dict):
        if 'entity_id' in o and 'printing_aliases' in o:
            out[o['entity_id']] = (o.get('name'), o.get('printing_aliases'), o.get('count'))
        for v in o.values():
            find_entities(v, out)
    elif isinstance(o, list):
        for v in o:
            find_entities(v, out)


for g in sorted(os.listdir(B)):
    if not g.endswith('_iOS'):
        continue
    short = g.replace('_iOS', '')[2:]
    df = D + f'KW{short}.txt'
    if not os.path.exists(df):
        continue
    deckfile = collections.Counter()
    for line in open(df, encoding='utf-8').read().splitlines()[1:]:
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})$', line)
        deckfile[(m.group(2), m.group(3))] += int(m.group(1))
    ents = {}
    for f in glob.glob(B + g + '/*.json'):
        if any(x in os.path.basename(f) for x in ('QR', 'DECK_USED', 'DECK_EDIT')):
            try:
                find_entities(json.load(open(f, encoding='utf-8')), ents)
            except Exception as e:
                print('  read fail', f, e)
    # the entity list actually in DECK_USED (ids + counts)
    du = json.load(open(B + g + '/DECK_USED.json', encoding='utf-8'))
    used = collections.Counter()
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, list) and v and all(isinstance(x, dict) and 'entity_id' in x for x in v) and len(v) == 20:
                    for x in v:
                        used[x['entity_id']] += 1
                    return True
                if isinstance(v, (dict, list)) and walk(v):
                    return True
        elif isinstance(o, list):
            for v in o:
                if walk(v):
                    return True
        return False
    walk(du)
    print('=====', short, 'deck file', sum(deckfile.values()), 'QR entities with aliases', len(ents), 'DECK_USED 20-entity list', sum(used.values()))
    if not used:
        # variant-style list
        print('   DECK_USED has no 20-entry entity list; source', [k for k in du.keys()][:30])
    expected = collections.Counter()
    for e, n in used.items():
        if e not in ents:
            print('   entity', e, 'x', n, 'no aliases found')
            continue
        name, al, _ = ents[e]
        expected[(L.nname(name), tuple(al))] += n
    # compare by name: the deck file's printing signature vs each entity's
    byname_file = collections.defaultdict(list)
    for (n, pr), c in deckfile.items():
        byname_file[n].append((pr, c))
    for (n, al), c in sorted(expected.items()):
        fs = byname_file.get(n, [])
        exp_sig = sig(BYPRINT.get(al[0])) if al else None
        match = [(pr, cc) for pr, cc in fs if sig(BYPRINT.get(pr)) == exp_sig]
        if not match:
            print(f'   MISMATCH {n}: QR {al} x{c}; deck file {fs}')
    for n, fs in byname_file.items():
        tot = sum(c for (nn, al), c in expected.items() if nn == n)
        if expected and tot != sum(c for _, c in fs):
            print(f'   COUNT {n}: QR {tot} vs deck file {fs}')
