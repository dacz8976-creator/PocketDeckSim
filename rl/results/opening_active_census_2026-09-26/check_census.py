#!/usr/bin/env python3
"""Independent check of census.json (Sept 26, 2026). Written without calling census.py's code.

1. Flags: re-derives each carried Ability's class from its printed text alone (phrases, not the engine
   variant table) and compares with census.json's class and switch membership, per Basic, per list.
   It also re-reads every engine map entry and reports where the text phrases and census.py's variant
   table disagree on the position (Active / Bench / anywhere) or the first-turn condition.
2. Openings: plays the engine's deal literally (deck.rs 129-149) for N deals per list and picks k3/kp3's
   opening with a literal depth-3 search over its own setup actions (place the Active, then up to two more
   placements or end setup), scoring leaves with the setup branch of value_functions.rs 459-478 term by term
   (Bench Retreat reducers applied only when actually benched). Compares with census.json's exact numbers.

python check_census.py [deals_per_list]   (default 40000; standard library only; no engine run)
"""
import io, json, math, os, random, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
SEED = 20_260_926  # a Python RNG for this check only; no engine seed block is used


def text_class(t):
    first = 'first turn' in t
    if 'when you put this Pokémon from your hand onto your Bench' in t:
        pos = 'bench_entry'
    elif 'when you play this Pokémon from your hand to evolve' in t:
        pos = 'evolve'
    elif 'this Pokémon is on your Bench' in t or 'This Pokémon is on your Bench' in t:
        pos = 'bench'
    elif 'this Pokémon is in the Active Spot' in t or 'This Pokémon is in the Active Spot' in t:
        pos = 'active'
    elif "this Pokémon can't attack" in t:
        pos = 'active'
    else:
        pos = 'anywhere'
    low = t.lower()
    board_words = ['opponent', 'your active', 'each of your', 'your pokémon', 'your benched', 'draw',
                   'from your deck', 'your [', 'attacks used by your', 'basic pokémon in play', 'pokémon (both',
                   'of your pokémon', 'each turn', 'your future', 'your evolved']
    self_only = ('this pokémon' in low) and not any(w in low for w in board_words)
    scope = 'self' if self_only else 'board'
    return pos, first, scope


def load_db():
    db = [next(iter(e.items())) for e in json.load(io.open(os.path.join(ROOT, 'lib', 'deckgym-database.json'), encoding='utf-8'))]
    return {v['id']: (k, v) for k, v in db}


def check_flags(census, db):
    out = {'basics_checked': 0, 'disagreements': []}
    for e in census['lists']:
        for b in e['basics']:
            if not b['ability']:
                continue
            out['basics_checked'] += 1
            pos, first, scope = text_class(b['ability_text'])
            m = b['mechanic'] or {}
            a_txt = pos == 'active' and first
            b_txt = pos == 'bench' or (pos == 'anywhere' and scope == 'board')
            diffs = []
            if m.get('pos') != pos:
                diffs.append(f"pos census={m.get('pos')} text={pos}")
            if bool(m.get('first_turn')) != first:
                diffs.append(f"first census={m.get('first_turn')} text={first}")
            if m.get('scope') != scope:
                diffs.append(f"scope census={m.get('scope')} text={scope}")
            if b['switch_a'] != a_txt or b['switch_b'] != b_txt:
                diffs.append(f"switch census A={b['switch_a']} B={b['switch_b']} text A={a_txt} B={b_txt}")
            if diffs:
                out['disagreements'].append({'list': e['list'], 'basic': f"{b['name']} {b['id']}", 'variant': m.get('variant'), 'diffs': diffs})
    return out


def check_map_table():
    """Every engine map entry: text phrases against census.py's variant table (read as data, not called)."""
    src = io.open(os.path.join(ROOT, 'engine', 'src', 'actions', 'effect_ability_mechanic_map.rs'), encoding='utf-8').read()
    csrc = io.open(os.path.join(HERE, 'census.py'), encoding='utf-8').read()
    found = re.findall(r"'(\w+)': \('(\w+)', (True|False)", csrc)
    table = {k: p for k, p, _ in found}
    table_first = {k: f for k, _, f in found}
    pat = re.compile(r'\n\s*map\.insert\(\s*"((?:[^"\\]|\\.)*)",\s*AbilityMechanic::(\w+)([^;]*?)\);', re.S)
    rows = []
    for m in pat.finditer(src):
        text = re.sub(r'\\u\{([0-9a-fA-F]+)\}', lambda mm: chr(int(mm.group(1), 16)), m.group(1))
        variant, fields = m.group(2), m.group(3)
        pos, first, _ = text_class(text)
        if variant in table:
            cpos, cfirst = table[variant], table_first[variant] == 'True'
        else:  # field-dependent entries, resolved the way the variant's own fields say
            if 'require_active: true' in fields or 'EndOfOpponentTurnIfActive' in fields:
                cpos = 'active'
            else:
                cpos = 'anywhere'
            cfirst = 'YourFirstTurn' in fields
        if cpos != pos or cfirst != first:
            rows.append({'line': src.count('\n', 0, m.start()) + 2, 'variant': variant, 'census_pos': cpos,
                         'text_pos': pos, 'census_first': cfirst, 'text_first': first, 'text': text[:140]})
    return {'entries': len(pat.findall(src)), 'disagreements': rows}


# ----------------------------------------------------------------------------------- the deal and the search
def parse(path, db):
    cards = []
    for raw in io.open(path, encoding='utf-8-sig'):
        line = raw.strip()
        if not line or line.lower().startswith('energy'):
            continue
        p = line.split()
        cid = p[-2] + ' ' + p[-1]
        if cid not in db:
            cid = p[-2] + ' ' + p[-1].zfill(3)
        cards += [cid] * int(p[0])
    return cards


def deal(cards, db, rng):
    d = cards[:]
    rng.shuffle(d)
    basic = lambda c: db[c][0] == 'Pokemon' and db[c][1]['stage'] == 0
    if not any(basic(c) for c in d[:5]):
        idx = [i for i in range(5, len(d)) if basic(d[i])]
        j = rng.choice(idx)
        h = rng.randrange(5)
        d[h], d[j] = d[j], d[h]
    return d[:5]


def make_scorer(cards, db, extra):
    pok = {c: db[c][1] for c in set(cards) if db[c][0] == 'Pokemon'}
    names_in_list = {v['name']: v for v in pok.values()}

    def target(v):
        s1 = [w for w in pok.values() if w['stage'] == 1 and w.get('evolves_from') == v['name']]
        s2 = [w for w in pok.values() if w['stage'] == 2 and any(w.get('evolves_from') == x['name'] for x in s1)]
        return (s2 or s1 or [v])[0]

    def online(v):
        t = target(v)
        costs = [tuple(a['energy_required']) for a in t.get('attacks', [])]
        return 1.0 if (not costs or max(costs) == ()) else 0.0

    def ko(v):
        return 3 if v['name'].startswith('Mega ') and v['name'].endswith(' ex') else 2 if v['name'].endswith(' ex') else 1

    def retreat(active, bench):
        r = len(active.get('retreat_cost') or [])
        for b in bench:
            ab = (b.get('ability') or {}).get('effect', '')
            if ab == "As long as this Pokémon is on your Bench, your Active Basic Pokémon's Retreat Cost is 1 less.":
                r -= 1
            m = re.match(r"As long as this Pokémon is on your Bench, your Active \[(\w)\] Pokémon's Retreat Cost is (\d) less\.", ab)
            if m:
                code = {'D': 'Darkness', 'G': 'Grass', 'R': 'Fire', 'W': 'Water', 'L': 'Lightning', 'P': 'Psychic',
                        'F': 'Fighting', 'M': 'Metal', 'C': 'Colorless', 'N': 'Dragon'}[m.group(1)]
                if active['energy_type'] == code:
                    r -= int(m.group(2))
        return max(r, 0)

    def leaf(active, bench, hand_len):
        a = pok[active]
        bench_v = [pok[b] for b in bench]
        value = a['hp'] + sum(b['hp'] for b in bench_v)       # pokemon value, no Energy
        value += hand_len                                         # hand size
        value -= retreat(a, bench_v)                              # Active Retreat Cost
        value += 500.0 * online(a)                                # Active online score
        value += a['hp'] / ko(a)                                  # Active safety
        return value + extra(a)

    def search(active, bench, hand_basics, hand_len, depth):
        best = leaf(active, bench, hand_len)                      # end setup (unpriced: static value)
        if depth == 0 or len(bench) == 3:
            return best
        for b in set(hand_basics):
            rest = list(hand_basics)
            rest.remove(b)
            best = max(best, search(active, bench + [b], rest, hand_len - 1, depth - 1))
        return best

    def choose(hand):
        basics = [c for c in hand if c in pok and pok[c]['stage'] == 0]
        vals = []
        for x in sorted(set(basics)):
            rest = list(basics)
            rest.remove(x)
            vals.append((x, search(x, [], rest, len(hand) - 1, 2)))
        m = max(v for _, v in vals)
        return [x for x, v in vals if abs(v - m) < 1e-9][-1], len(set(basics)), len(basics)

    return choose


def main():
    db = load_db()
    census = json.load(io.open(os.path.join(HERE, 'census.json'), encoding='utf-8'))
    report = {'flags': check_flags(census, db), 'map_table': check_map_table(), 'openings': []}
    rng = random.Random(SEED)
    for e in census['lists']:
        cards = parse(os.path.join(ROOT, e['list']), db)
        flags = {b['id']: b for b in e['basics']}

        def ea(v, flags=flags):  # switch A bonus from the text-derived class
            pos, first, _ = text_class((v.get('ability') or {}).get('effect', '')) if v.get('ability') else (None, False, None)
            has_evo = flags[v['id']]['evolves_in_list_to'] is not None
            return 250.0 if (pos == 'active' and first and has_evo) else 0.0

        def eb(v):
            if not v.get('ability'):
                return 0.0
            pos, first, scope = text_class(v['ability']['effect'])
            return -250.0 if (pos == 'bench' or (pos == 'anywhere' and scope == 'board')) else 0.0

        base = make_scorer(cards, db, lambda v: 0.0)
        ca = make_scorer(cards, db, ea)
        cb = make_scorer(cards, db, eb)
        cab = make_scorer(cards, db, lambda v: ea(v) + eb(v))
        choice = opens = 0
        opened = Counter()
        changed = Counter()
        for _ in range(N):
            hand = deal(cards, db, rng)
            x, distinct, _n = base(hand)
            opened[db[x][1]['name'] + ' ' + x] += 1
            if distinct >= 2:
                choice += 1
                for k, f in (('A', ca), ('B', cb), ('AB', cab)):
                    if f(hand)[0] != x:
                        changed[k] += 1
        se = lambda p: 1.96 * math.sqrt(max(p * (1 - p), 1e-12) / N)
        row = {'list': e['list'], 'deals': N,
               'p_opening_choice': [round(choice / N, 4), e['p_opening_choice']],
               'p_changes': {k: [round(changed[k] / N, 4), e['p_opening_changes'][k]] for k in ('A', 'B', 'AB')},
               'kp3_opens': {k: [round(v / N, 4), e['kp3_opens'].get(k, 0.0)] for k, v in opened.most_common()}}
        worst = 0.0
        pairs = [row['p_opening_choice']] + list(row['p_changes'].values()) + list(row['kp3_opens'].values())
        for sim, exact in pairs:
            worst = max(worst, abs(sim - exact) / max(se(exact), 1e-9))
        row['worst_z'] = round(worst, 2)
        report['openings'].append(row)
        print(f"{e['list']}: choice {row['p_opening_choice']} changes {row['p_changes']} worst |z| {row['worst_z']}")
    with io.open(os.path.join(HERE, 'check_census.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    print('flag disagreements (listed Basics):', len(report['flags']['disagreements']))
    for d in report['flags']['disagreements']:
        print('   ', d)
    print('map entries where text phrases and the variant table differ:', len(report['map_table']['disagreements']),
          'of', report['map_table']['entries'])
    for d in report['map_table']['disagreements']:
        print('   ', d)


if __name__ == '__main__':
    main()
