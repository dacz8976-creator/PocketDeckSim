#!/usr/bin/env python3
"""check_decks.py DATABASE_JSON CARD_STATUS_JSON R6_CARD_STATUS_JSON DECK_DIR: the smoke decks' legality, before any game.

Per deck, as engine/src/deck.rs (Deck::from_string, Deck::is_valid) reads it: 20 cards, at least one Basic Pokemon, no name more
than twice, every Energy-line type a real type that the Energy Zone can make (not Dragon, not Colorless), every id in the
database; and, beyond is_valid: every Stage 1 / Stage 2 has the Pokemon it evolves from in the deck (Rare Candy aside, none of
these decks relies on it alone), and every card is Complete or RulesUnverified in CARD_STATUS_JSON (what `strength run` refuses
otherwise). Coverage: each of the 55 printings that R6 S's card_status had as Missing* among the new C1/SP1/P-C printings
(R6_CARD_STATUS_JSON) is in at least one a* deck, and the rule-row / item 11 decks (coordinator-148 §2.6) hold their cards.
Prints a report and the PRINTINGS table; exit 0 only if everything holds."""
import collections, json, os, re, sys

db_p, st_p, r6_p, ddir = sys.argv[1:5]
db = {}
for e in json.load(open(db_p, encoding='utf-8')):
    for k, v in e.items():
        db[v['id']] = (k, v)
def load_status(p):
    c = json.load(open(p)); c = c if isinstance(c, list) else c.get('cards', c)
    return {x['id']: x['status'] for x in c}
st, r6 = load_status(st_p), load_status(r6_p)
NEW = ('C1 ', 'SP1 ', 'P-C ')
the55 = sorted(i for i in r6 if i.startswith(NEW) and r6[i] not in ('Complete', 'RulesUnverified'))
ZONE = {'Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal'}
problems, holders = [], collections.defaultdict(list)
decks = sorted(f for f in os.listdir(ddir) if f.endswith('.txt'))
for f in decks:
    cards, energy = [], []
    for raw in open(os.path.join(ddir, f), encoding='utf-8'):
        if '\r' in raw:
            problems.append(f'{f}: CR in the file')
        t = raw.strip()
        if not t or t.startswith(('Pokémon:', 'Trainer:')):
            continue
        if t.startswith('Energy:'):
            energy = [x.strip() for x in t[len('Energy:'):].split(',') if x.strip()]
            continue
        m = re.match(r'^(\d+)\s+(?:.*\s)?([A-Za-z0-9-]+ \d{3})$', t)
        if not m:
            problems.append(f'{f}: unreadable line {t!r}'); continue
        cards += [m[2]] * int(m[1])
    unknown = sorted({i for i in cards if i not in db})
    for i in unknown:
        problems.append(f'{f}: {i} not in the database')
    names = collections.Counter(db[i][1]['name'] for i in cards if i in db)
    over = {n: c for n, c in names.items() if c > 2}
    basics = sum(1 for i in cards if i in db and db[i][0] == 'Pokemon' and db[i][1].get('stage') == 0)
    bad_e = [e for e in energy if e not in ZONE]
    present = {db[i][1]['name'] for i in cards if i in db}
    gaps = sorted({f"{db[i][1]['name']} ({i}) needs {db[i][1]['evolves_from']}" for i in cards if i in db and db[i][0] == 'Pokemon'
                   and db[i][1].get('evolves_from') and db[i][1]['evolves_from'] not in present})
    unsup = sorted({(i, st.get(i)) for i in cards if st.get(i) not in ('Complete', 'RulesUnverified')})
    ru = sorted({i for i in cards if st.get(i) == 'RulesUnverified'})
    ok = len(cards) == 20 and basics >= 1 and not over and energy and not bad_e and not gaps and not unsup and not unknown
    print(f'{f}: {len(cards)} cards, {basics} Basic, Energy {energy}, max per name {max(names.values()) if names else 0}'
          f'{", RulesUnverified " + str(ru) if ru else ""} -> {"OK" if ok else "BAD"}')
    for what, val in (('names over 2', over), ('bad Energy types', bad_e), ('evolution gaps', gaps), ('not playable', unsup)):
        if val:
            problems.append(f'{f}: {what}: {val}')
    if len(cards) != 20 or basics < 1 or not energy:
        problems.append(f'{f}: {len(cards)} cards, {basics} Basic, Energy {energy}')
    for i in set(cards):
        holders[i].append(f)
missing = [i for i in the55 if not any(d.startswith('a') for d in holders.get(i, []))]
print(f'\nthe 55 (R6 S Missing* among C1/SP1/P-C): {len(the55)}; in an a* deck: {len(the55) - len(missing)}; missing: {missing}')
if len(the55) != 55 or missing:
    problems.append(f'coverage: {len(the55)} printings, missing {missing}')
RULES = {'b01-darkrai-sableye.txt': [['A2 110', 'A2 187', 'A2 202', 'A4b 245', 'A4b 378', 'P-A 042'], ['B3a 040', 'P-B 070']],
         'b02-iris-haxorus.txt': [['B2b 067', 'B2b 081', 'B4b 212', 'B4b 378', 'B4b 421'], ['B4b 176', 'B4b 348']],
         'b03-mega-blastoise.txt': [['B1a 020', 'B1a 078', 'B1a 084', 'B4b 054', 'B4b 414']],
         'b04-starting-plains.txt': [['B2 154', 'B4b 235', 'B4b 401'], ['B2 079'], ['B4 089']],
         'b05-urshifu.txt': [['B3 051', 'B3 113']], 'b06-snover-sealeo.txt': [['A2 044'], ['B4 039']]}
for f, groups in RULES.items():
    held = {i for i, ds in holders.items() if f in ds}
    good = all(held & set(g) for g in groups)
    print(f'rule-row deck {f}: {"OK" if good else "MISSING " + str([g for g in groups if not held & set(g)])}')
    if not good:
        problems.append(f'{f}: rule-row cards missing')
print('\n| printing | name | R6 S status | tip status | deck(s) |\n|---|---|---|---|---|')
for i in the55:
    print(f"| {i} | {db[i][1]['name']} | {r6[i]} | {st.get(i)} | {', '.join(sorted(d[:-4] for d in holders.get(i, [])))} |")
print('\nPROBLEMS:' if problems else '\nALL DECKS OK')
for p in problems:
    print('  ' + p)
sys.exit(1 if problems else 0)
