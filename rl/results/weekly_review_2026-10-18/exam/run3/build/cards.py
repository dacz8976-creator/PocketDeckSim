#!/usr/bin/env python3
"""Card lookup in the database pg_legal_v14 and frozen-7 use (sha256 b5e68fc8...), for the exam v2 builders. Read only.

  cards.py WORDS...          every card whose name contains all the words (case-insensitive), e.g. cards.py mega gyarados
  cards.py --id "B1 016"     one card by its set id
  cards.py --deck v2deck_X   that deck's list (~/exam_v2/decks/v2deck_X.txt), each card in full

A card is named in a position as "<name> <set id>", e.g. "Whimsicott ex B1 016" (the deck files use the same form)."""
import json, os, sys

DB = os.path.expanduser('~/exam_v2/bin/frozen_db_b5e68fc8.json')
db = [v for e in json.load(open(DB, encoding='utf-8')) for v in e.values()]


def show(c):
    if 'hp' in c:
        s = (f"{c['name']} {c['id']} | Pokemon stage {c['stage']} HP {c['hp']} {c['energy_type']}"
             f" | weakness {c.get('weakness')} | retreat {len(c.get('retreat_cost') or [])}"
             + (f" | evolves from {c['evolves_from']}" if c.get('evolves_from') else ''))
        if c.get('ability'):
            a = c['ability']
            s += f"\n    Ability {a.get('title')}: {a.get('effect')}"
        for at in c.get('attacks') or []:
            s += f"\n    Attack {at['title']} [{','.join(at.get('energy_required') or [])}] {at.get('fixed_damage')}: {at.get('effect') or ''}"
    else:
        s = f"{c['name']} {c['id']} | {c.get('trainer_card_type')} | {c.get('effect')}"
    print(s)


if len(sys.argv) < 2:
    sys.exit(__doc__)
if sys.argv[1] == '--id':
    hits = [c for c in db if c['id'] == ' '.join(sys.argv[2:])]
elif sys.argv[1] == '--deck':
    path = os.path.expanduser(f'~/exam_v2/decks/{sys.argv[2]}.txt')
    print(open(path, encoding='utf-8').read())
    hits = []
    for line in open(path, encoding='utf-8'):
        if line[:1].isdigit():
            name = line.split(None, 1)[1].strip()
            sid = ' '.join(name.split()[-2:])
            hits += [c for c in db if c['id'] == sid]
else:
    words = [w.lower() for w in sys.argv[1:]]
    hits = [c for c in db if all(w in c['name'].lower() for w in words)]
for c in hits[:60]:
    show(c)
if len(hits) > 60:
    print(f'... {len(hits) - 60} more; narrow the words')
if not hits and sys.argv[1] != '--deck':
    print('no card found')
