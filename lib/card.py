#!/usr/bin/env python3
"""Print a card's exact text from deckgym-database.json. Use this instead of remembering cards.

usage:
  python lib/card.py "Arceus ex"          every printing whose name contains the text (case-insensitive)
  python lib/card.py "B4a 043"            one printing by id
  python lib/card.py arceus crobat xatu   several lookups at once
  python lib/card.py --exact "Oricorio"   exact name only (Oricorio has seven different printings — id matters)

Finds the database beside this file, one folder up, or via PDL_DB=<path>.
"""
import io, json, os, sys

E = {'Grass':'G','Fire':'R','Water':'W','Lightning':'L','Psychic':'P','Fighting':'F',
     'Darkness':'D','Metal':'M','Colorless':'C','Dragon':'N'}

def load():
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.environ.get('PDL_DB',''), os.path.join(here,'deckgym-database.json'),
              os.path.join(here,'..','deckgym-database.json'), 'deckgym-database.json'):
        if p and os.path.exists(p):
            return [next(iter(e.items())) for e in json.load(io.open(p, encoding='utf-8'))]
    sys.exit('deckgym-database.json not found (run from the project root or set PDL_DB)')

def cost(l): return ''.join(E.get(x, x[:1]) for x in l) or '-'

def fmt(kind, v):
    if kind == 'Pokemon':
        head = (f"{v['name']}  [{v['id']}]  {v['energy_type']}  Stage {v['stage']}"
                + (f" (from {v['evolves_from']})" if v.get('evolves_from') else '')
                + f"  HP {v['hp']}  weak {v.get('weakness') or '-'}  retreat {len(v.get('retreat_cost') or [])}")
        lines = [head]
        if v.get('ability'):
            lines.append(f"  Ability {v['ability']['title']}: {v['ability']['effect']}")
        for a in v.get('attacks', []):
            dmg = a.get('fixed_damage')
            lines.append(f"  [{cost(a['energy_required'])}] {a['title']}" + (f" {dmg}" if dmg else '')
                         + (f" — {a['effect']}" if a.get('effect') else ''))
        return '\n'.join(lines)
    return f"{v['name']}  [{v['id']}]  {kind}\n  {v.get('effect') or ''}"

def main(argv):
    exact = '--exact' in argv
    terms = [a for a in argv if a != '--exact']
    if not terms:
        print(__doc__); return
    cards = load()
    for t in terms:
        tl = t.lower()
        hits = [(k, v) for k, v in cards if v['id'].lower() == tl
                or (v['name'].lower() == tl if exact else tl in v['name'].lower())]
        # keep one line per distinct (name, text) so reprints don't spam; show the ids they share
        seen = {}
        for k, v in hits:
            key = fmt(k, {**v, 'id': '?'})
            seen.setdefault(key, []).append(v['id'])
        print(f"== {t}: {len(hits)} printings, {len(seen)} distinct")
        for key, ids in seen.items():
            print(key.replace('[?]', '[' + ', '.join(ids) + ']'))
        print()

if __name__ == '__main__':
    main(sys.argv[1:])
