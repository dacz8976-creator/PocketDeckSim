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


TYPE_LETTERS = {'G': 'Grass', 'R': 'Fire', 'W': 'Water', 'L': 'Lightning', 'P': 'Psychic', 'F': 'Fighting', 'D': 'Darkness', 'M': 'Metal', 'N': 'Dragon', 'C': 'Colorless'}
HP_BOOST = re.compile(r'gets? \+(\d+) HP', re.I)


def hp_boost(c, tool=None, stadium=None):
    """the HP a Tool on this Pokemon card and a Stadium in play add to it, read from their texts in the database: 'The Stage 1 Pokémon this card is attached to gets +30 HP' (Elegant Cape),
    'Each Basic Pokémon in play (both yours and your opponent's) gets +20 HP' (Starting Plains), 'The [G] Pokémon this card is attached to gets +30 HP' (Leaf Cape), 'The Pokémon this card is
    attached to gets +20 HP' (Giant Cape). A condition this does not know (the Ancient Pokémon of the Booster Energy Capsule: the database has no such flag) adds nothing."""
    total = 0
    for name, is_stadium in ((tool, False), (stadium, True)):
        if not name or str(name).strip().lower() in ('none', 'null', 'empty', 'no stadium'):
            continue
        card = next((x for x in BYNAME.get(nname(name), []) if not is_pokemon(x)), None)
        eff = (card or {}).get('effect') or ''
        m = HP_BOOST.search(eff)
        if not m:
            continue
        cond = eff.split('this card is attached to')[0].lower() if not is_stadium else eff.lower()
        stage = c.get('stage', 0)
        if is_stadium:
            applies = 'basic' in cond and stage == 0
        elif 'stage 1' in cond:
            applies = stage == 1
        elif 'stage 2' in cond:
            applies = stage == 2
        elif re.search(r'\[\w\] pok', cond):
            applies = c.get('energy_type') == TYPE_LETTERS.get(re.search(r'\[(\w)\] pok', cond).group(1).upper())
        else:
            applies = 'ancient' not in cond
        if applies:
            total += int(m.group(1))
    return total


class HP:
    """the HP a ledger shows for a Pokemon on the board, with the Tool on it and the Stadium in play that may have added to it: a card fits when its printed HP plus what they add is the shown HP
    (score 2); a card whose printed HP is the shown HP although they would have added to it fits less (score 1: the ledger did not add the boost)"""

    def __init__(self, hp_max, tool=None, stadium=None):
        self.max, self.tool, self.stadium = hp_max, tool, stadium

    def score(self, c):
        if self.max is None or c.get('hp') is None:
            return 0
        boost = hp_boost(c, self.tool, self.stadium)
        if c['hp'] + boost == self.max:
            return 2
        return 1 if boost and c['hp'] == self.max else 0


def score_text(c, text, hp=None):
    """how well a database card fits a ledger's description of a Pokemon ('Nightmare Aura / Dark Prism 80; shiny artwork', 'A2a 053; Tackle20, HP60',
    'Hook 30; 50 HP'): +3 for each of its attack and Ability titles the text names, +2 when HP agrees (`hp` is the shown HP, or an HP with its Tool and Stadium), +1 when the text names
    this very id (the reader's ids can be swapped, so that is the weakest evidence). Only what a card has counts: a title the text names that the card lacks is not held against it."""
    t = norm_text(text)
    s = 0
    for ti in titles(c):
        if norm_text(ti) and norm_text(ti) in t:
            s += 3
    if isinstance(hp, HP):
        s += hp.score(c)
    elif hp is not None and c.get('hp') == hp:
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
