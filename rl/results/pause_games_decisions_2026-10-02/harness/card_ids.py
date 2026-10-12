#!/usr/bin/env python3
"""Card lookup for building positions: card_ids.py NAME [NAME ...]  (case-insensitive substring match on the card name)
Prints one line per printing: the id the harness wants ('Name SET NUM'), type, hp, stage/evolves_from, attacks (title/damage/cost), ability, retreat.
Trainers print their text. Run in WSL:  wsl python3 /mnt/c/.../card_ids.py "Mega Gardevoir ex" "Peculiar Plaza" """
import json, sys

DB = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/engine/database.json'
db = json.load(open(DB, encoding='utf-8'))
cards = db if isinstance(db, list) else db.get('cards', list(db.values()))
want = [a.lower() for a in sys.argv[1:]]
for c in cards:
    inner = c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c
    name = inner.get('name', '')
    if not any(w == name.lower() or (len(w) > 3 and w in name.lower()) for w in want):
        continue
    cid = inner.get('id', '')
    if 'hp' in inner:
        atks = ' ; '.join(f"{a.get('title')} {a.get('fixed_damage')} [{''.join(str(e)[0] for e in a.get('energy_required', []))}]" for a in inner.get('attacks', []))
        ab = inner.get('ability')
        abt = f" | ABILITY {ab.get('title')}" if isinstance(ab, dict) else ''
        print(f"{name} {cid} | {inner.get('energy_type')} hp {inner['hp']} | stage {inner.get('stage')} from {inner.get('evolves_from')} | {atks}{abt} | retreat {len(inner.get('retreat_cost', []))}")
    else:
        print(f"{name} {cid} | TRAINER | {str(inner.get('effect', inner.get('text', '')))[:200]}")
