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

class DualTypeUnsupported(ValueError):
    """A reader whose rule for a dual-type Pokémon is not settled met one. It refuses, naming the
    card and the reader, rather than guessing (reading the first type only, or leaving the card
    out, would change its results silently)."""

def printed_types(v):
    """The printed type set of the Pokémon `v` (a database entry's inner dict), primary first.

    Every card today is single-type ('energy_type': 'Water') and this returns ['Water']. Dual
    Fusion (Oct 29) prints dual-type Pokémon with ONE Weakness; upstream's data shape is not
    settled (deckgym issue #429), so all three candidate shapes are read: 'energy_type' as a
    list (a 'secondary_energy_type' beside it may only repeat its second entry); 'energy_type'
    plus 'secondary_energy_type' (this fork's engine field); an 'energy_types' list (an
    'energy_type' beside it must be its first entry, or the same list). The same rule as the
    engine's PokemonCard reader (engine/src/models/card.rs). Raises ValueError on malformed type
    data: no type, an empty list, more than two types, a repeated type, a name that is not a
    type, shapes that disagree, an unknown field naming a type, a list Weakness. Not for
    Trainers (they have no type)."""
    label = f"{v.get('name', '?')} [{v.get('id', '?')}]"

    def bad(why):
        return ValueError(f'{label}: malformed card type data: {why}')

    weak = v.get('weakness')
    if isinstance(weak, (list, tuple)):
        raise bad(f'Weakness {weak!r} is a list (a card prints one Weakness)')
    # a second type under any other field name would otherwise be read as a single-type card
    unknown = sorted(k for k in v if 'type' in k.lower()
                     and k not in ('energy_type', 'secondary_energy_type', 'energy_types'))
    if unknown:
        raise bad(f'unrecognised type field(s) {unknown!r} (known: energy_type, '
                  f'secondary_energy_type, energy_types)')
    et, sec, ets = v.get('energy_type'), v.get('secondary_energy_type'), v.get('energy_types')
    if isinstance(et, (list, tuple)):
        types = list(et)
        if sec is not None and (len(types) != 2 or types[1] != sec):
            raise bad(f"'secondary_energy_type' {sec!r} disagrees with the 'energy_type' list {types!r}")
    elif et is not None:
        types = [et] if sec is None else [et, sec]
    elif sec is not None:
        raise bad(f"'secondary_energy_type' {sec!r} without 'energy_type'")
    else:
        types = None
    if ets is not None:
        if not isinstance(ets, (list, tuple)):
            raise bad(f"'energy_types' is {ets!r}, not a list")
        ets = list(ets)
        primary_only = isinstance(et, str) and sec is None and ets[:1] == [et]
        if types is not None and types != ets and not primary_only:
            raise bad(f"'energy_types' {ets!r} disagrees with 'energy_type'"
                      + (" + 'secondary_energy_type'" if sec is not None else '') + f' {types!r}')
        types = ets
    if types is None:
        raise bad('no printed type')
    if not types:
        raise bad('the type list is empty')
    if len(types) > 2:
        raise bad(f'{len(types)} types {types!r} (a card prints at most two)')
    if not all(isinstance(t, str) and t in E for t in types):
        raise bad(f'{types!r} holds a name that is not one of {sorted(E)}')
    if len(set(types)) < len(types):
        raise bad(f'{types!r} repeats a type')
    return types

def dual_type_message(name, cid, types, reader):
    return (f'{name} [{cid}] is a dual-type Pokémon ({"/".join(types)}): {reader} has no rule for '
            f'a Pokémon with two printed types yet. Refusing rather than guessing (reading it as '
            f'{types[0]} only, or leaving it out, would change the result silently).')

def single_type(v, reader):
    """The one printed type of the Pokémon `v`, for a reader whose dual-type rule is not settled
    (`reader` names it in the refusal). Raises DualTypeUnsupported on a dual-type card and
    ValueError on malformed type data; for every single-type card it is v['energy_type']."""
    types = printed_types(v)
    if len(types) > 1:
        raise DualTypeUnsupported(dual_type_message(v.get('name', '?'), v.get('id', '?'), types, reader))
    return types[0]

def fmt(kind, v):
    if kind == 'Pokemon':
        # both types for a dual-type card ('Psychic/Fighting'); one Weakness either way
        head = (f"{v['name']}  [{v['id']}]  {'/'.join(printed_types(v))}  Stage {v['stage']}"
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
