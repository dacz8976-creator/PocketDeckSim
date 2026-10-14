"""deck_check.py: per game, DECK_USED / QR_DECODE / DECK_LOG_SNAPSHOT vs the v2 deck file (independent of deckspec.py where possible)"""
import json, os, re, sys, glob, collections
REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
sys.path.insert(0, REPO + '/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = REPO + '/rl/results/pause_games_new_2026-10-13/v2'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
PID = re.compile(r'(?<![A-Za-z0-9])([A-Z][A-Za-z0-9\-]{0,4}) (\d{3})(?![0-9])')


def pids(v):
    if v is None:
        return []
    if isinstance(v, str):
        return [m.group(1) + ' ' + m.group(2) for m in PID.finditer(v)]
    if isinstance(v, list):
        o = []
        for x in v:
            o += pids(x)
        return o
    if isinstance(v, dict):
        o = []
        for x in v.values():
            o += pids(x)
        return o
    return []


def deckfile(short):
    lines = open(os.path.join(V2, 'decks', f'KW{short}.txt'), encoding='utf-8').read().splitlines()
    en = [x.strip() for x in lines[0].split(':', 1)[1].split(',')]
    cards = []
    for l in lines[1:]:
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})$', l.strip())
        cards.append((int(m.group(1)), C.nname(m.group(2)), m.group(3)))
    return en, cards


def lists_in(j, path=''):
    out = []
    if isinstance(j, dict):
        for k, v in j.items():
            out += lists_in(v, f'{path}.{k}' if path else k)
    elif isinstance(j, list):
        if j and all(isinstance(x, dict) and isinstance(x.get('name'), str) for x in j):
            out.append((path, j))
        for i, x in enumerate(j):
            if isinstance(x, (dict, list)):
                out += lists_in(x, path + '[]')
    return out


def count_list(lst):
    tot = 0
    for d in lst:
        n = d.get('count', d.get('n'))
        tot += int(n) if isinstance(n, (int, str)) and str(n).isdigit() and 'position' not in d and 'slot' not in d else 1
    return tot


for g in games:
    name = os.path.basename(g)
    short = name.replace('_iOS', '')[2:]
    print('=' * 25, name)
    du = json.load(open(os.path.join(g, 'DECK_USED.json'), encoding='utf-8'))
    print(' DECK_USED keys:', list(du.keys()))
    print(' exact_list_status:', du.get('exact_list_status'))
    for k, v in du.items():
        if 'energy' in k.lower():
            print(f'  energy field {k}: {json.dumps(v, ensure_ascii=False)[:200]}')
    for path, lst in lists_in(du):
        n = count_list(lst)
        print(f'  list {path}: {len(lst)} entries, {n} cards')
        if n == 20 or 'qr' in path.lower() or 'log' in path.lower():
            agg = collections.Counter()
            for d in lst:
                c = d.get('count', d.get('n'))
                c = int(c) if isinstance(c, (int, str)) and str(c).isdigit() and 'position' not in d and 'slot' not in d else 1
                ids = []
                for f in ('variant', 'printing', 'printing_aliases', 'variant_aliases', 'semantic_variant_references', 'id', 'variant_as_shown_in_log'):
                    ids += pids(d.get(f))
                agg[(C.nname(d['name']), d.get('entity_id', d.get('semantic_entity_id')), ' / '.join(dict.fromkeys(ids)))] += c
            for (nm, ent, ids), c in agg.items():
                print(f'     {c} {nm} ent={ent} [{ids}]')
    en, cards = deckfile(short)
    print(' DECK FILE energy', en, 'total', sum(c for c, _, _ in cards))
    for c, nm, pid in cards:
        card = C.BYID.get(pid)
        ok = card is not None and C.nname(card['name']) == nm
        print(f'     {c} {nm} {pid}{"" if ok else "  <-- NOT IN DB / NAME MISMATCH"}')
    for fn in ('QR_DECODE.json', 'DECK_LOG_SNAPSHOT.json', 'DECK_LOG_SNAPSHOT.live_20261013.json'):
        p = os.path.join(g, fn)
        if not os.path.exists(p):
            continue
        j = json.load(open(p, encoding='utf-8'))
        print(f' {fn} keys: {list(j.keys())[:25]}')
        if fn == 'QR_DECODE.json':
            for c in j.get('cards') or []:
                print(f"     QR {c.get('count')} {c.get('name')} ent={c.get('entity_id')} kind={c.get('entity_kind')} aliases={c.get('printing_aliases')}")
            dec = j.get('decoded') or {}
            print('     QR energy', json.dumps(dec.get('energy'), ensure_ascii=False)[:200], '| card_slot_count', j.get('card_slot_count'), dec.get('card_slot_count'))
        else:
            for k in ('energy', 'retrieved_utc', 'status', 'snapshot_status', 'deck_name'):
                if k in j:
                    print(f'     {k}: {json.dumps(j[k], ensure_ascii=False)[:200]}')
            for path, lst in lists_in(j):
                n = count_list(lst)
                agg = collections.Counter()
                for d in lst:
                    c = d.get('count', d.get('n'))
                    c = int(c) if isinstance(c, (int, str)) and str(c).isdigit() else 1
                    ids = []
                    for f in ('variant', 'id', 'printing'):
                        ids += pids(d.get(f))
                    agg[(C.nname(d['name']), ' / '.join(dict.fromkeys(ids)))] += c
                print(f'     list {path}: {n} cards: ' + '; '.join(f'{c} {nm} [{ids}]' for (nm, ids), c in agg.items()))
