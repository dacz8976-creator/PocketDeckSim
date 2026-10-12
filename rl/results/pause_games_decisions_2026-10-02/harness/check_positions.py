#!/usr/bin/env python3
"""Sanity check for a positions JSON file (a list of position dicts in the harness schema; see examples_positions.json).
  wsl python3 /mnt/c/.../check_positions.py POSITIONS.json DECKLIST.txt
Errors (exit 1): unknown card id; a card used by his side more often than the deck list holds; remaining HP above the card's HP; more than 4 Pokémon on a side;
unknown Energy type. Warnings: a `Play:X` step of his plan that is not in his hand (a card drawn earlier in the same turn is fine, so only a hint).
It does not check the opponent's cards against any list (his deck is unknown)."""
import json, sys, collections

DB = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/engine/database.json'
TYPES = {'Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal', 'Dragon', 'Colorless'}

db = json.load(open(DB, encoding='utf-8'))
cards = db if isinstance(db, list) else db.get('cards', list(db.values()))
HP, NAME, STAGE = {}, {}, {}
for c in cards:
    inner = c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c
    key = f"{inner.get('name')} {inner.get('id')}"
    NAME[key] = inner.get('name')
    if 'hp' in inner:
        HP[key] = inner['hp']
        STAGE[key] = inner.get('stage', 0)

positions = json.load(open(sys.argv[1], encoding='utf-8'))
deck = collections.Counter()
for line in open(sys.argv[2], encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('Energy'):
        continue
    n, rest = line.split(' ', 1)
    deck[rest.strip()] += int(n)

errors, warns = [], []
for p in positions:
    pid = p.get('id', '?')
    used = collections.Counter()

    def use(cid, where, mine):
        if cid not in NAME:
            errors.append(f'{pid}: unknown card id {cid!r} ({where})')
            return
        if mine:
            used[cid] += 1

    me = p['me']
    for c in me.get('hand', []):
        use(c, 'hand', True)
    for c in me.get('discard', []):
        use(c, 'discard', True)
    for side, spec, mine in (('me', me, True), ('opp', p['opp'], False)):
        board = spec.get('board', [])
        if len(board) > 4:
            errors.append(f'{pid}: {side} has {len(board)} Pokemon in play')
        for b in board:
            use(b['card'], f'{side} board', mine)
            for c in b.get('behind', []):
                use(c, f'{side} behind', mine)
            for c in b.get('tools', []):
                use(c, f'{side} tool', mine)
            if 'hp' in b and b['card'] in HP:
                limit = HP[b['card']]
                if any(t.startswith('Giant Cape') for t in b.get('tools', [])):
                    limit += 20  # Giant Cape: +20 HP
                if any(t.startswith('Elegant Cape') for t in b.get('tools', [])):
                    limit += 30  # Elegant Cape: +30 HP (Stage 1)
                if (p.get('stadium') or {}).get('card', '').startswith('Starting Plains') and STAGE.get(b['card'], 0) == 0:
                    limit += 20  # Starting Plains: each Basic Pokemon in play +20 HP
                if b['hp'] > limit:
                    errors.append(f"{pid}: {side} {b['card']} has hp {b['hp']} above its {limit} (printed {HP[b['card']]} plus tool/stadium bonuses)")
            for e in b.get('energy', []):
                if e not in TYPES:
                    errors.append(f'{pid}: {side} unknown energy type {e!r}')
        if side == 'me':
            for e in spec.get('discard_energy', []):
                if e not in TYPES:
                    errors.append(f'{pid}: unknown discard energy type {e!r}')
    for cid, n in used.items():
        if n > deck.get(cid, 0):
            errors.append(f'{pid}: his side uses {cid} {n} times, the deck list holds {deck.get(cid, 0)}')
    hand_names = collections.Counter(NAME.get(c, c) for c in me.get('hand', []))
    for step in p.get('his_plan', []):
        if step.startswith('Play:'):
            nm = step[5:]
            if hand_names.get(nm, 0) == 0:
                warns.append(f'{pid}: plan step {step!r} is not in the starting hand (fine only if drawn earlier in the same turn)')
            else:
                hand_names[nm] -= 1
    if p.get('turn_count', 1) > 1 and p['me'].get('energy_now') is None:
        warns.append(f'{pid}: energy_now is null after game turn 1')
print(f'{len(positions)} positions checked: {len(errors)} errors, {len(warns)} warnings')
for e in errors:
    print('ERROR', e)
for w in warns:
    print('warn ', w)
sys.exit(1 if errors else 0)
