import json, os, glob, sys, collections, re
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l2p_copy as L
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12'
BASE = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA'
POS = json.load(open(SRC + '/positions_all.json', encoding='utf-8'))
gdirs = {os.path.basename(g).replace('_iOS', '')[2:]: g for g in glob.glob(BASE + '/BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS')}
BYID = {str(c['id']): c for c in L.CARDS}
def textkey(c):
    if 'hp' not in c:
        return (L.nname(c.get('name')), c.get('effect'))
    return (L.nname(c.get('name')), c.get('hp'), c.get('stage'), c.get('energy_type'), json.dumps(c.get('ability'), sort_keys=True),
            json.dumps([(a.get('title'), a.get('fixed_damage'), a.get('effect'), a.get('energy_required')) for a in c.get('attacks', [])]))
PR = re.compile(r'[A-Za-z0-9\-]+ \d{3}')
def match_text(name, text, hp_max=None):
    t = PR.sub(' ', str(text or '')).replace('’', "'")
    cands = {}
    for c in L.BYNAME.get(name, []):
        if 'hp' not in c: continue
        k = textkey(c)
        if k in cands: continue
        titles = [a['title'] for a in c.get('attacks', [])] + ([c['ability']['title']] if c.get('ability') else [])
        cands[k] = (sum(1 for x in titles if x.lower() in t.lower()), c)
    if len(cands) < 2:
        return None, None
    best = max(v[0] for v in cands.values())
    hits = [v[1] for v in cands.values() if v[0] == best] if best > 0 else []
    if hp_max is not None:
        pool = hits or [v[1] for v in cands.values()]
        hh = [c for c in pool if c['hp'] == hp_max]
        if hh and len(hh) < len(cands):
            hits = hh
    if not hits or len(hits) == len(cands):
        return None, None
    named_id = PR.findall(str(text or ''))
    return {textkey(c) for c in hits}, named_id
def raw_text(c):
    if isinstance(c, dict):
        m = re.search(r'[\(\[](.*)[\)\]]\s*$', str(c.get('name') or ''))
        return c.get('name'), ' '.join(str(c.get(k) or '') for k in ('variant', 'card_variant', 'printing')) + ' ' + (m.group(1) if m else '')
    s = str(c)
    m = re.search(r'[\(\[](.*)[\)\]]\s*$', s)
    return s, (m.group(1) if m else '')
led = {}
bad_pos = collections.defaultdict(list)
idswap = []
for P in POS:
    short = P['game'][3:]
    if short not in led:
        led[short] = {t['turn_number']: t for t in json.load(open(gdirs[short] + '/TURN_LEDGER.json', encoding='utf-8'))['turns']}
    t = led[short][P['turn_count']]
    hs = (t.get('hand_at_start') or {}).get('cards_left_to_right') or []
    for i, c in enumerate(P['me']['hand']):
        n = c.rsplit(' ', 2)[0]
        nm, txt = raw_text(hs[i]) if i < len(hs) else (None, '')
        m, ids = match_text(n, txt)
        if m is not None and textkey(BYID[c[len(n)+1:]]) not in m:
            bad_pos[P['id']].append(f'hand[{i}] {c} vs ledger {txt!r}')
        if m is not None and ids:
            for x in ids:
                if x in BYID and L.nname(BYID[x]['name']) == n and textkey(BYID[x]) not in m:
                    idswap.append(f'{P["id"]} hand[{i}] ledger id {x} but text {txt!r}')
    own = L.instances(t['board_at_start']['owner'])
    for i, b in enumerate(P['me']['board']):
        n = b['card'].rsplit(' ', 2)[0]
        lp = own[i] if i < len(own) else {}
        txt = lp.get('variant')
        m, ids = match_text(n, txt, lp.get('hp_max'))
        if m is not None and textkey(BYID[b['card'][len(n)+1:]]) not in m:
            bad_pos[P['id']].append(f'board[{i}] {b["card"]} hp {b["hp"]} vs ledger {txt!r} hp_max {lp.get("hp_max")}')
        if m is not None and ids:
            for x in ids:
                if x in BYID and L.nname(BYID[x]['name']) == n and textkey(BYID[x]) not in m:
                    idswap.append(f'{P["id"]} board[{i}] ledger id {x} but text {txt!r}')
for k in sorted(bad_pos):
    print(k)
    for x in bad_pos[k]:
        print('     ', x)
print('positions with a hand/board card contradicted by the ledger text:', len(bad_pos), 'games', len({k.split('-t')[0] for k in bad_pos}))
print('ledger id vs text disagreements (Codex):')
for x in sorted(set(idswap)):
    print('  ', x)
