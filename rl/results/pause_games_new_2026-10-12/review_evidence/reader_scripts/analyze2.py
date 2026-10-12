import json, os, glob, sys, collections, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2p_copy as L
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
ENT = {int(k): v for k, v in json.load(open(HERE + '/entmap.json', encoding='utf-8')).items()}
POS = json.load(open(SRC + '/positions_all.json', encoding='utf-8'))
bygame = collections.defaultdict(list)
for p in POS:
    bygame[p['game']].append(p)
BYID = {str(c['id']): c for c in L.CARDS}
def textkey(c):
    if 'hp' not in c:
        return (L.nname(c.get('name')), c.get('effect'))
    return (L.nname(c.get('name')), c.get('hp'), c.get('stage'), c.get('energy_type'), json.dumps(c.get('ability'), sort_keys=True),
            json.dumps([(a.get('title'), a.get('fixed_damage'), a.get('effect'), a.get('energy_required')) for a in c.get('attacks', [])]))
def tk(pid):
    c = BYID.get(pid)
    return textkey(c) if c else ('?', pid)
def desc(pid):
    c = BYID[pid]
    if 'hp' not in c: return pid
    return f"{pid} hp{c['hp']} " + ('Ab:' + c['ability']['title'] + ' ' if c.get('ability') else '') + '/'.join(a['title'] for a in c.get('attacks', []))
PR = re.compile(r'[A-Za-z0-9\-]+ \d{3}')

def entity_slots(d):
    best = None
    def walk(v, path):
        nonlocal best
        if isinstance(v, dict):
            for k, v2 in v.items():
                walk(v2, path + '.' + k)
        elif isinstance(v, list):
            def eid(x): return x.get('entity_id', x.get('semantic_entity_id'))
            if v and all(isinstance(x, dict) and x.get('name') and isinstance(eid(x), int) for x in v):
                tot = sum(int(x['count']) if isinstance(x.get('count'), int) else 1 for x in v)
                if tot == 20 and best is None:
                    best = (path, [(L.nname(x['name']), eid(x)) for x in v for _ in range(int(x['count']) if isinstance(x.get('count'), int) else 1)])
    walk(d, '')
    return best

def match_text(name, text, hp_max=None):
    """distinct cards of this name whose attack/ability titles appear in the ledger text (id part removed)"""
    if not text and hp_max is None:
        return None
    t = str(text or '')
    t = re.sub(r'^\s*[A-Za-z0-9\-]+ \d{3}\s*;', '', t)
    cands = {}
    for c in L.BYNAME.get(name, []):
        if 'hp' not in c: continue
        k = textkey(c)
        if k in cands: continue
        titles = [a['title'] for a in c.get('attacks', [])] + ([c['ability']['title']] if c.get('ability') else [])
        score = sum(1 for x in titles if x.lower() in t.lower())
        cands[k] = (score, c, titles)
    best = max((v[0] for v in cands.values()), default=0)
    hits = [v[1] for v in cands.values() if v[0] == best and best > 0]
    if hp_max is not None:
        hh = [c for c in (hits or [v[1] for v in cands.values()]) if c['hp'] == hp_max]
        if hh and (hits or len(hh) == 1):
            hits = hh
        elif hits:
            pass
    return {textkey(c) for c in hits} if hits else None

games = sorted(glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS'))
tot_aff = 0; tot_pos_any = 0; tot_pos_hb = 0; tot_def = 0
summary = {}
for g in games:
    short = os.path.basename(g).replace('_iOS', '')[2:]
    key = 'kw-' + short
    if key not in bygame:
        continue
    d = json.load(open(g + '/DECK_USED.json', encoding='utf-8'))
    pos2, skip2, deck2 = L.convert_game(g)
    for p in pos2: p.pop('unresolved', None)
    same = json.dumps(pos2, sort_keys=True, ensure_ascii=False) == json.dumps(bygame[key], sort_keys=True, ensure_ascii=False)
    slots = entity_slots(d)
    truth = collections.Counter()
    if slots:
        for n, eid in slots[1]:
            prs = [x for x in ENT.get(eid, {}).get('printings', {}) if x in BYID]
            ks = {tk(x) for x in prs}
            if len(ks) != 1:
                print('  !! entity', n, eid, 'printings', prs)
                continue
            truth[(n, ks.pop())] += 1
    else:
        cards, energy, src = L.load_deck(d)
        for n, v in cards:
            if v: truth[(n, tk(v))] += 1
            else: print('  !! no printing for', n)
    conv = collections.Counter()
    MINE = {}
    for c in deck2['counts_by_name_and_variant']:
        conv[(c['name'], tk(c['variant']))] += c['count']
        MINE[c['name']] = c['name'] + ' ' + c['variant']
    wrong = {}
    for (n, k), c in truth.items():
        got = conv.get((n, k), 0)
        if got < c:
            wrong[n] = wrong.get(n, 0) + (c - got)
    allwrong = {n for n in wrong if conv.get((n, tk(MINE[n][len(n) + 1:])), 0) > 0 and truth.get((n, tk(MINE[n][len(n) + 1:])), 0) == 0}
    print(f'==== {short}: positions {len(bygame[key])}; regenerated==file: {same}; truth source {slots[0] if slots else "load_deck variants"}')
    for n in sorted(wrong):
        tv = [(c, [desc(x) for x in BYID if tk(x) == k][:1]) for (nn, k), c in truth.items() if nn == n]
        print(f'   WRONG {n}: deck file {MINE[n]} x{sum(c for (nn, k), c in conv.items() if nn == n)} [{desc(MINE[n][len(n)+1:])}]; truth {tv}; wrong copies {wrong[n]}; all copies wrong: {n in allwrong}')
    if not wrong:
        continue
    # ledger
    led = json.load(open(g + '/TURN_LEDGER.json', encoding='utf-8'))
    turns = {t['turn_number']: t for t in led['turns']}
    n_hb = 0; n_def = 0
    for P in bygame[key]:
        t = turns[P['turn_count']]
        hand_aff = [c for c in P['me']['hand'] if c.rsplit(' ', 2)[0] in wrong]
        board_aff = [(i, b['card']) for i, b in enumerate(P['me']['board']) if b['card'].rsplit(' ', 2)[0] in wrong]
        behind_aff = [(i, x) for i, b in enumerate(P['me']['board']) for x in b.get('behind', []) if x.rsplit(' ', 2)[0] in wrong]
        disc_aff = [c for c in P['me']['discard'] if c.rsplit(' ', 2)[0] in wrong]
        # definite errors: card with all copies wrong, or ledger text contradicts, or more copies of a distinct card than truth allows
        defs = []
        hs = (t.get('hand_at_start') or {}).get('cards_left_to_right') or []
        for i, c in enumerate(P['me']['hand']):
            n = c.rsplit(' ', 2)[0]
            if n not in wrong: continue
            if n in allwrong:
                defs.append(f'hand {c} (no copy of this card in the list)')
                continue
            lc = hs[i] if i < len(hs) else None
            lv = lc.get('variant') if isinstance(lc, dict) else None
            m = match_text(n, lv)
            if m is not None and tk(c[len(n)+1:]) not in m:
                defs.append(f'hand {c} vs ledger {lv!r}')
        own = L.instances(t['board_at_start']['owner'])
        for i, b in enumerate(P['me']['board']):
            n = b['card'].rsplit(' ', 2)[0]
            if n not in wrong: continue
            lp = own[i] if i < len(own) else {}
            if n in allwrong:
                defs.append(f'board[{i}] {b["card"]} hp {b["hp"]} (no copy in list; ledger {lp.get("variant")!r} hp_max {lp.get("hp_max")})')
                continue
            m = match_text(n, lp.get('variant'), lp.get('hp_max'))
            if m is not None and tk(b['card'][len(n)+1:]) not in m:
                defs.append(f'board[{i}] {b["card"]} hp {b["hp"]} vs ledger {lp.get("variant")!r} hp_max {lp.get("hp_max")}')
        # count over-use: hand+board copies of a distinct card above the truth count
        cnt = collections.Counter(tk(c.split(' ', 0)[0][len(c.rsplit(' ', 2)[0])+1:]) for c in [])
        n_hb += bool(hand_aff or board_aff)
        n_def += bool(defs)
        print(f'   {P["id"]}: hand {hand_aff} board {board_aff} behind {behind_aff} disc {disc_aff}')
        for x in defs:
            print('        DEFINITE:', x)
    print(f'   -> positions with affected name in hand/board: {n_hb}/{len(bygame[key])}; with a definite wrong card in hand/board: {n_def}')
    tot_aff += 1; tot_pos_any += len(bygame[key]); tot_pos_hb += n_hb; tot_def += n_def
print('GAMES affected', tot_aff, 'positions', tot_pos_any, 'with affected name in hand/board', tot_pos_hb, 'definite', tot_def)
