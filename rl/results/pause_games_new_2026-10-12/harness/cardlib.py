#!/usr/bin/env python3
"""Card knowledge for the pause-game converter, read from the engine's own database (engine/database.json).

A *printing* is one id ('A3 096'). A *function* is what a card does: every printing that has the same name and the same gameplay fields
(stage, HP, type, attacks, ability, weakness, retreat cost, trainer effect) is one function, whatever its artwork, rarity or set. Two cards that
share a name can still be two functions (Conkeldurr A3 096 has the Guts Ability and Mega Punch, Conkeldurr B4 089 has Bedrock Breaker), and the
converter must never merge them. The deck lists the recordings give are by function (the QR carries a 'semantic entity' and, often, its printings)."""
import collections, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('PG_CARD_DB') or os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', 'engine', 'database.json'))

ETYPES = ('Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal', 'Dragon', 'Colorless')
PID_RE = re.compile(r'(?<![A-Za-z0-9])([A-Z][A-Za-z0-9\-]{0,4}) (\d{3})(?![0-9])')


def nname(n):
    """a name as the engine spells it"""
    if n is None:
        return ''
    n = str(n).strip().replace('Poke Ball', 'Poké Ball').replace('’', "'")
    n = re.sub(r'\s*[\(\[].*[\)\]]$', '', n)
    n = re.sub(r'^Nidoran\s*(?:male|♂)$', 'Nidoran♂', n, flags=re.I)
    n = re.sub(r'^Nidoran\s*(?:female|♀)$', 'Nidoran♀', n, flags=re.I)
    return re.sub(r'\s+', ' ', n)


def etype(x):
    s = str(x or '').strip().capitalize()
    return s if s in ETYPES else None


def _load():
    with open(DB_PATH, encoding='utf-8') as f:
        db = json.load(f)
    cards = db if isinstance(db, list) else db.get('cards', list(db.values()))
    return [c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c for c in cards]


CARDS = _load()
BYID = {c['id']: c for c in CARDS}
BYNAME = collections.defaultdict(list)
for _c in CARDS:
    BYNAME[nname(_c['name'])].append(_c)


def is_pokemon(c):
    return 'hp' in c


def sig(c):
    """the gameplay fields of a card, as a string: equal for the printings of one function"""
    d = {k: v for k, v in c.items() if k not in ('id', 'rarity', 'booster_pack')}
    return json.dumps(d, sort_keys=True, ensure_ascii=False)


SIG = {c['id']: sig(c) for c in CARDS}


def functions(name):
    """[[ids of one function], ...] for a card name, in database order"""
    g = collections.OrderedDict()
    for c in BYNAME.get(nname(name), []):
        g.setdefault(SIG[c['id']], []).append(c['id'])
    return list(g.values())


def same_function(a, b):
    return a in SIG and b in SIG and SIG[a] == SIG[b]


def known(pid, name=None):
    c = BYID.get(pid)
    return c is not None and (name is None or nname(c['name']) == nname(name))


def attack_titles(c):
    return [a.get('title') for a in (c.get('attacks') or []) if a.get('title')]


def ability_title(c):
    ab = c.get('ability')
    return ab.get('title') if isinstance(ab, dict) else None


def titles(c):
    return [t for t in attack_titles(c) + [ability_title(c)] if t]


def norm_text(s):
    return re.sub(r'[^a-z0-9]+', '', str(s or '').lower().replace('’', "'"))


def score_text(c, text, hp=None):
    """how well a database card fits a ledger's description of a Pokemon ('Nightmare Aura / Dark Prism 80; shiny artwork', 'A2a 053; Tackle20, HP60',
    'Hook 30; 50 HP'): +3 for each of its attack and Ability titles the text names, +2 when HP agrees, +1 when the text names this very id (the reader's ids can
    be swapped, so that is the weakest evidence). Only what a card has counts: a title the text names that the card lacks is not held against it."""
    t = norm_text(text)
    s = 0
    for ti in titles(c):
        if norm_text(ti) and norm_text(ti) in t:
            s += 3
    if hp is not None and c.get('hp') == hp:
        s += 2
    if c['id'] in set(m.group(1) + ' ' + m.group(2) for m in PID_RE.finditer(str(text or ''))):
        s += 1
    return s


def best(cands, text, hp=None):
    """(ids of the best-scoring functions' first printings, ambiguous?) among candidate ids; ties between different functions are ambiguous"""
    if not cands:
        return [], False
    scored = [(score_text(BYID[i], text, hp), i) for i in cands]
    top = max(s for s, _ in scored)
    tops = [i for s, i in scored if s == top]
    funcs = collections.OrderedDict()
    for i in tops:
        funcs.setdefault(SIG[i], i)
    return list(funcs.values()), len(funcs) > 1


def chain_down(card_id):
    """names below a Pokemon by its printed evolution line (a Rare Candy may have skipped a stage)"""
    out, cur = [], BYID[card_id]
    for _ in range(3):
        base = cur.get('evolves_from')
        if not base:
            break
        out.insert(0, nname(base))
        nxt = [c for c in BYNAME.get(nname(base), []) if is_pokemon(c)]
        if not nxt:
            break
        cur = nxt[0]
    return out
