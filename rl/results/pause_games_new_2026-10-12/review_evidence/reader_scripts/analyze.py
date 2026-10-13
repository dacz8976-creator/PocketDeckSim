import json, os, glob, sys, shutil, collections, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
shutil.copy(SRC + '/harness/ledger_to_positions.py', HERE + '/l2p_copy.py')
sys.path.insert(0, HERE)
import l2p_copy as L

BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
games = sorted(glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS'))
POS = json.load(open(SRC + '/positions_all.json', encoding='utf-8'))
bygame = collections.defaultdict(list)
for p in POS:
    bygame[p['game']].append(p)

E = {'Grass':'G','Fire':'R','Water':'W','Lightning':'L','Psychic':'P','Fighting':'F','Darkness':'D','Metal':'M','Colorless':'C','Dragon':'N'}
def textkey(c):
    if 'hp' not in c:
        return (c.get('name'), c.get('effect'))
    return (c.get('name'), c.get('hp'), c.get('stage'), c.get('energy_type'), json.dumps(c.get('ability'), sort_keys=True),
            json.dumps([(a.get('title'), a.get('fixed_damage'), a.get('effect'), a.get('energy_required')) for a in c.get('attacks', [])]))
BYID = {}
for c in L.CARDS:
    BYID[str(c['id'])] = c
def tk(pid):
    c = BYID.get(pid)
    return textkey(c) if c else ('?', pid)
def short(pid):
    c = BYID.get(pid)
    if not c: return pid + '(?)'
    if 'hp' in c:
        return f"{pid}[hp{c['hp']} {'Ab:'+c['ability']['title']+' ' if c.get('ability') else ''}{'/'.join(a['title'] for a in c.get('attacks', []))}]"
    return pid

PR = re.compile(r'[A-Za-z0-9\-]+ \d{3}')
def truth_entities(d):
    """per-entity printing aliases found anywhere in DECK_USED: {(name, entity_id): (set(printings), count or None)}"""
    out = {}
    def walk(v):
        if isinstance(v, dict):
            if v.get('name') and v.get('entity_id') is not None:
                prs = set()
                for k in ('variant', 'printing_aliases', 'variant_aliases', 'printings'):
                    x = v.get(k)
                    if isinstance(x, str):
                        prs |= set(PR.findall(x))
                    elif isinstance(x, list):
                        for y in x:
                            if isinstance(y, str): prs |= set(PR.findall(y))
                key = (L.nname(v['name']), v['entity_id'])
                old = out.get(key, (set(), None))
                cnt = v.get('count') if isinstance(v.get('count'), int) else old[1]
                out[key] = (old[0] | prs, cnt)
            for v2 in v.values():
                walk(v2)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(d)
    return out

def entity_slots(d):
    """a 20-slot entity list: [(name, entity_id)]"""
    best = None
    def walk(v, path):
        nonlocal best
        if isinstance(v, dict):
            for k, v2 in v.items():
                walk(v2, path + '.' + k)
        elif isinstance(v, list):
            if v and all(isinstance(x, dict) and x.get('name') and x.get('entity_id') is not None for x in v):
                tot = sum(int(x['count']) if isinstance(x.get('count'), int) else 1 for x in v)
                if tot == 20 and best is None:
                    best = (path, [(L.nname(x['name']), x['entity_id']) for x in v for _ in range(int(x['count']) if isinstance(x.get('count'), int) else 1)])
    walk(d, '')
    return best

report = {}
for g in games:
    gn = os.path.basename(g)
    short_ = gn.replace('_iOS', '')[2:]
    key = 'kw-' + short_
    if key not in bygame:
        continue
    d = json.load(open(g + '/DECK_USED.json', encoding='utf-8'))
    cards, energy, src = L.load_deck(d)
    pos2, skip2, deck2 = L.convert_game(g)
    same = json.dumps(pos2, sort_keys=True, ensure_ascii=False) == json.dumps(bygame[key], sort_keys=True, ensure_ascii=False)
    ents = truth_entities(d)
    slots = entity_slots(d)
    # truth multiset of distinct cards per name
    truth = collections.Counter()
    unresolved = []
    if slots:
        for n, eid in slots[1]:
            prs = ents.get((n, eid), (set(), None))[0]
            keys = {tk(x) for x in prs if x in BYID}
            if len(keys) == 1:
                truth[(n, keys.pop())] += 1
            else:
                unresolved.append((n, eid, sorted(prs)))
    conv = collections.Counter()
    for c in deck2['counts_by_name_and_variant']:
        pid = c['variant']
        conv[(c['name'], tk(pid))] += c['count']
    wrong = {}
    for (n, k), c in truth.items():
        got = conv.get((n, k), 0)
        if got < c:
            wrong[n] = wrong.get(n, 0) + (c - got)
    report[short_] = dict(src=src, guessed=deck2['printing_guessed_for'], positions=len(bygame[key]), regenerated_identical=same,
                          slots_src=slots[0] if slots else None, unresolved=unresolved, wrong_copies=wrong,
                          deck={c['name']: (c['variant'], c['count']) for c in deck2['counts_by_name_and_variant']},
                          truth={f"{n}": [] for (n, k) in truth})
    # print detail
    print('====', short_, 'src', src, '| positions', len(bygame[key]), '| regenerated identical:', same, '| slots', slots[0] if slots else None)
    if deck2['printing_guessed_for']:
        print('   notes:', deck2['printing_guessed_for'])
    if unresolved:
        print('   UNRESOLVED truth:', unresolved)
    for n in sorted({n for n, _ in truth}):
        tr = [(k, c) for (nn, k), c in truth.items() if nn == n]
        dv = deck2 and [x for x in deck2['counts_by_name_and_variant'] if x['name'] == n]
        prs_t = []
        for (nn, eid), (prs, cnt) in ents.items():
            if nn == n:
                prs_t.append((eid, sorted(prs)))
        if n in wrong:
            print(f'   WRONG {n}: deck file {[(x["variant"], x["count"]) for x in dv]} ; DECK_USED entities {prs_t} ; wrong copies {wrong[n]}')
json.dump(report, open(HERE + '/report.json', 'w'), indent=1, ensure_ascii=False, default=str)
