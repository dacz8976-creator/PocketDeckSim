#!/usr/bin/env python3
"""Build lib/c1_provisional_entities.json: the PROVISIONAL deck-code entities of Dual Fusion (C1)
printings, until the community catalog has C1 (release checklist R7, coordinator-077).

The community catalog (lib/s216_card_catalog_v1.json) maps card ids to the game's deck-code
entities and has no C1, SP1 or P-C card yet. Another session decoded 5 real deck codes and found the
C1 numbering (the anchors file, read-only here):
  Pokemon  C1 001-117: pokemon:(21780 + 10*(n-1))
  Trainers C1 119-131: trainer:(1660 + 10*(n-119))
  a reprint keeps its original card's entity (Celebi C1 187 = pokemon:16690, B3 004's).
This script turns that into one entry per covered printing, from the anchors file and lib's own data:
  lib/deckgym-database.json      ids, kinds and names;
  lib/CANON_MAP.tsv              which printings are one card (lib/card_canon.py base_id);
  lib/s216_card_catalog_v1.json  the older cards' entities (read only, never mixed in).
Each entry says how it was derived: 'anchor' (the rule's value, also read from a source code whose
card list is known; 'codes' numbers them 1-5 in qr_sources order), 'rule', or 'reprint-of-<base id>'.
C1 118, SP1 and P-C are listed as NOT covered, with the reason. The build REFUSES unless every entry
of the anchors file (by_id, exact, the Celebi example) equals the value derived here, every source
code decodes with no unknown card, and every code with a known list decodes to that list.

    python3 -I lib/build_c1_provisional.py [--anchors PATH]          write the overlay
    python3 -I lib/build_c1_provisional.py --check [--anchors PATH]  rebuild in memory; exit 1 unless
                                                                     the file is this build, byte for byte

Standard library only. The overlay's reader and its release check: lib/check_c1_overlay.py.
"""
import argparse
import base64
import collections
import hashlib
import io
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import card_canon               # noqa: E402  (base_id, prints_of, _sort_key)
import check_c1_overlay as c1   # noqa: E402  (SCHEMA, OVERLAY, the entity-key format)

ANCHORS = ('/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/'
           'b816037a-8268-412e-9510-8518f9b17037/scratchpad/combos/c1_entity_anchors.json')
DB = os.path.join(HERE, 'deckgym-database.json')
MAP = os.path.join(HERE, 'CANON_MAP.tsv')
CATALOG = os.path.join(HERE, 's216_card_catalog_v1.json')
NEW_SETS = ('C1', 'SP1', 'P-C')
ALTS = range(132, 218)          # C1 132-217, the alternate printings
ENERGY = {'grass': 1, 'fire': 2, 'water': 3, 'lightning': 4, 'psychic': 5, 'fighting': 6, 'darkness': 7,
          'metal': 8}
LABEL = 'provisional, until the community catalog has C1'
APPROVAL = {'by': 'Dustin', 'words': "Yes that's fine. We can double check when the community one is available",
            'when': 'Oct 29, 2026, about 02:00Z', 'via': 'coordinator-077'}
STOP_RULE = ('When the community catalog gains C1, run python3 -I lib/check_c1_overlay.py <that catalog.json>. '
             'It compares every entity here with the catalog\'s entity for the same id. Any mismatch is a STOP '
             'and a report to the coordinator. If all match, drop the overlay (delete this file: lib/decode_qr.py '
             'and lib/encode_qr.py then read the catalog alone). Until then both tools refuse to run with a '
             'catalog that has any id listed here.')


class Refused(SystemExit):
    pass


def rule_entity(n):
    """The anchors file's rule for C1 n: (kind, number), or None outside its two ranges."""
    if 1 <= n <= 117:
        return 'pokemon', 21780 + 10 * (n - 1)
    if 119 <= n <= 131:
        return 'trainer', 1660 + 10 * (n - 119)
    return None


def norm(name):
    """A card name for comparing lists: no accents, straight apostrophes, lower case."""
    s = unicodedata.normalize('NFKD', name.replace('’', "'"))
    return ''.join(ch for ch in s if not unicodedata.combining(ch)).strip().lower()


def read_code(text):
    """A deck code's (trainer entity numbers, Pokémon entity numbers, Energy bytes), in its order
    (the layout in lib/decode_qr.py)."""
    b, i = base64.b64decode(text), 0
    out = []
    for offset in (10_000_000, 0):
        n = b[i]
        i += 1
        out.append([int.from_bytes(b[i + 3 * k:i + 3 * k + 3], 'big') - offset for k in range(n)])
        i += 3 * n
    n = b[i]
    energy = list(b[i + 1:i + 1 + n])
    if i + 1 + n != len(b):
        raise Refused(f'build_c1_provisional: REFUSED: deck code {text!r} has trailing bytes')
    return out[0], out[1], energy


def read_decklist(text):
    """'2 Pikachu ex, Cyrus, ...; Energy Lightning' -> (Counter of normalized names, [Energy bytes])."""
    names, energy = collections.Counter(), []
    for part in text.split(';'):
        part = part.strip()
        if part.lower().startswith('energy'):
            energy += [ENERGY[e.strip().lower()] for e in part[len('energy'):].split(',')]
            continue
        for item in part.split(','):
            m = re.fullmatch(r'(?:(\d+)\s+)?(.+)', item.strip())
            names[norm(m[2])] += int(m[1] or 1)
    return names, energy


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def read_bytes(path):
    with io.open(path, 'rb') as f:
        return f.read()


def num(cid):
    return int(cid.rsplit(' ', 1)[1])


def build(anchors_path=ANCHORS):
    """The overlay as a dict (see render())."""
    def refuse(msg):
        raise Refused(f'build_c1_provisional: REFUSED: {msg}')

    anchors_raw = read_bytes(anchors_path)
    A = json.loads(anchors_raw.decode('utf-8'))
    db_raw, cat_raw, map_raw = (read_bytes(p) for p in (DB, CATALOG, MAP))
    cards = {}                                          # id -> (entity kind, name)
    for e in json.loads(db_raw.decode('utf-8')):
        kind = list(e)[0]
        cards[e[kind]['id']] = (kind.lower(), e[kind]['name'])
    cn = card_canon.Canon(MAP)
    if cn.source_sha256 != sha256(db_raw):
        refuse('lib/CANON_MAP.tsv was not built from lib/deckgym-database.json')
    aliases = json.loads(cat_raw.decode('utf-8'))['aliases']
    s216 = {a['deckgym_id']: a for a in aliases}
    s216_entity = collections.defaultdict(list)         # (kind, number) -> catalog aliases
    for a in aliases:
        s216_entity[c1.split_key(a['entity_key'])].append(a)
    new_ids = sorted((i for i in cards if i.rsplit(' ', 1)[0] in NEW_SETS), key=card_canon._sort_key)
    if any(i in s216 for i in new_ids):
        refuse('the catalog already has new-set ids: compare with lib/check_c1_overlay.py instead')

    entries, not_covered = {}, {}
    # C1 001-117 and 119-131: the rules. Each must be a card of its own (no older printing), or the
    # rule and the reprint rule would disagree.
    for n in list(range(1, 118)) + list(range(119, 132)):
        cid = f'C1 {n:03d}'
        kind, number = rule_entity(n)
        if cards[cid][0] != kind:
            refuse(f'{cid} {cards[cid][1]} is not a {kind} card')
        if cn.base_id(cid) != cid:
            refuse(f'{cid} is the same card as {cn.base_id(cid)}: the rule and the reprint rule disagree')
        entries[cid] = {'id': cid, 'name': cards[cid][1], 'entity_key': c1.entity_key(kind, number),
                        'derivation': 'rule'}
    if cards['C1 118'] != ('pokemon', 'Bewear ex') or cn.base_id('C1 118') != 'C1 118':
        refuse('C1 118 is not the Bewear ex this build expects')
    not_covered['C1 118'] = ('No deck code holds it. The Pokémon line would give it pokemon:022950 (C1 117 + 10), '
                             'but the line is anchored only on C1 001-117, and C1 118 is the last Pokémon '
                             'before the Trainers: not assumed.')
    # C1 132-217: a printing keeps its base card's entity (card_canon base_id).
    for n in ALTS:
        cid = f'C1 {n:03d}'
        base = cn.base_id(cid)
        kind = cards[cid][0]
        if base == cid:
            not_covered[cid] = 'A card of its own (no other printing), and no deck code holds it.'
        elif base in entries:
            entries[cid] = {'id': cid, 'name': cards[cid][1], 'entity_key': entries[base]['entity_key'],
                            'derivation': f'reprint-of-{base}'}
        elif base in s216:
            keys = {s216[p]['entity_key'] for p in cn.prints_of(cid) if p in s216}
            if len(keys) != 1 or c1.split_key(s216[base]['entity_key'])[0] != kind:
                refuse(f'{cid}: the catalog gives its printings {sorted(keys)}')
            entries[cid] = {'id': cid, 'name': cards[cid][1], 'entity_key': s216[base]['entity_key'],
                            'derivation': f'reprint-of-{base}'}
        elif base == 'C1 118':
            not_covered[cid] = 'An alternate printing of C1 118 Bewear ex, whose entity is not known.'
        else:
            not_covered[cid] = f'Its base card {base} has no entity in the catalog or the rules.'
    for cid in new_ids:
        if not cid.startswith('C1 '):
            base, what = cn.base_id(cid), ('Special Pack' if cid.startswith('SP1 ') else 'Promo')
            if base == cid or base.startswith(('SP1 ', 'P-C ')):
                not_covered[cid] = f'{what} card with no printing in another set; no deck code holds it.'
            else:
                not_covered[cid] = (f'{what} printing, the same card as {base} (card_canon), so it probably keeps '
                                    f'that card\'s entity, but no deck code holds a printing from {cid.split()[0]}: '
                                    f'unverified.')
    if set(entries) | set(not_covered) != set(new_ids) or set(entries) & set(not_covered):
        refuse('covered and not-covered ids do not split the new printings exactly')

    # The source codes: each must decode with no unknown card; a code with a known list must decode to
    # it, and its new cards are anchors. Codes with no list only show the rule's reading.
    head = {}                                           # (kind, number) -> lowest overlay id
    for e in sorted(entries.values(), key=lambda e: card_canon._sort_key(e['id']), reverse=True):
        head[c1.split_key(e['entity_key'])] = e['id']
    codes = collections.defaultdict(list)               # id -> code numbers
    without_list = {}
    for i, src in enumerate(A['qr_sources'], 1):
        tr, pk, energy = read_code(src['text'])
        seen, new = collections.Counter(), collections.Counter()
        for kind, numbers in (('trainer', tr), ('pokemon', pk)):
            for number in numbers:
                if (kind, number) in s216_entity:
                    seen[norm(s216_entity[(kind, number)][0]['raw_name'])] += 1
                elif (kind, number) in head:
                    new[head[(kind, number)]] += 1
                    seen[norm(cards[head[(kind, number)]][1])] += 1
                else:
                    refuse(f'code {i} holds {kind}:{number}, which neither the catalog nor the rules explain')
        if 'decklist' in src:
            want, want_energy = read_decklist(src['decklist'])
            if seen != want or sorted(energy) != sorted(want_energy):
                refuse(f'code {i} does not decode to its list: {sorted((seen - want).items())} vs '
                       f'{sorted((want - seen).items())}')
        elif 'anchors' in src:
            want = {f'C1 {m}' for m in re.findall(r'\b(\d{3})\b', src['anchors'])}
            if set(new) != want:
                refuse(f'code {i} holds {sorted(new)}, its anchors are {sorted(want)}')
        else:
            without_list[str(i)] = sorted(new, key=card_canon._sort_key)
            continue
        for cid in new:
            codes[cid].append(i)
    for cid, found in codes.items():
        entries[cid]['derivation'] = 'anchor'
        entries[cid]['codes'] = found

    # The anchors file's own values must all be what was derived here.
    for cid, (kind, number, name) in A['by_id'].items():
        e = entries.get(cid)
        if not e or c1.split_key(e['entity_key']) != (kind, number) or norm(name) != norm(e['name']):
            refuse(f'the anchors file gives {cid} {name} {kind}:{number}; derived here: {e}')
    for label, key in A['exact'].items():
        cid = ' '.join(label.split()[:2])
        if c1.split_key(entries[cid]['entity_key']) != c1.split_key(key):
            refuse(f'the anchors file\'s exact {label} = {key}; derived here: {entries[cid]["entity_key"]}')
    if entries['C1 187']['entity_key'] != c1.entity_key('pokemon', 16690):
        refuse(f'Celebi C1 187 is {entries["C1 187"]["entity_key"]}, the anchors file says pokemon:16690')

    ordered = sorted(entries.values(), key=lambda e: card_canon._sort_key(e['id']))
    derivations = collections.Counter(
        e['derivation'] if not e['derivation'].startswith('reprint-of-')
        else ('reprint of a C1 card' if e['derivation'].startswith('reprint-of-C1 ') else 'reprint of an older card')
        for e in ordered)
    return {
        'schema': c1.SCHEMA,
        'label': LABEL,
        'what': ('Deck-code (QR) entities for Dual Fusion (C1) printings that lib/s216_card_catalog_v1.json lacks. '
                 'Never mixed into that catalog: lib/decode_qr.py and lib/encode_qr.py read it through '
                 'lib/check_c1_overlay.py, only for ids and entities the catalog lacks (the catalog always wins), '
                 'and mark each card read through it provisional.'),
        'approval': APPROVAL,
        'stop_rule': STOP_RULE,
        'built_by': 'lib/build_c1_provisional.py (its --check rebuilds this file and compares it byte for byte)',
        'inputs': {
            'anchors_file': {'path': ANCHORS, 'sha256': sha256(anchors_raw),
                             'note': 'decoded from the 5 codes below by another session; read-only'},
            'lib/deckgym-database.json': sha256(db_raw),
            'lib/CANON_MAP.tsv': sha256(map_raw),
            'lib/s216_card_catalog_v1.json': sha256(cat_raw),
        },
        'rules': {
            'pokemon': 'C1 001-117: pokemon:(21780 + 10*(n-1))',
            'trainer': 'C1 119-131: trainer:(1660 + 10*(n-119))',
            'reprint': ('C1 132-217: the entity of the printing\'s base card (lib/card_canon.py base_id, '
                        'lib/CANON_MAP.tsv): the rules\' value for a C1 001-131 base, the catalog\'s for an older '
                        'base (the anchors file\'s example: Celebi C1 187 = pokemon:16690, B3 004\'s)'),
            'entity_key': ('the catalog\'s format: <kind>:<number padded to 6 digits> (pokemon:021780); a deck code '
                           'carries the bare number (21780)'),
            'derivation': ('anchor = the rules\' value, also read from a source code whose card list is known '
                           '(codes: 1-5 in qr_sources order); rule = from the rules only; reprint-of-<base id> = '
                           'the base card\'s entity'),
        },
        'counts': {
            'new_printings': len(new_ids),
            'covered': len(ordered),
            'by_derivation': dict(sorted(derivations.items())),
            'anchored_pokemon': sum(1 for e in ordered if e['derivation'] == 'anchor'
                                    and e['entity_key'].startswith('pokemon:')),
            'anchored_trainers': sum(1 for e in ordered if e['derivation'] == 'anchor'
                                     and e['entity_key'].startswith('trainer:')),
            'not_covered': len(not_covered),
            'not_covered_by_set': dict(collections.Counter(i.rsplit(' ', 1)[0] for i in not_covered)),
        },
        'evidence': [
            'Every older card in the 5 codes is in the catalog; codes 1 and 4 decode exactly to their lists '
            '(checked by this build).',
            'Code 4, whose list is known, holds 21780, 21790 and 21800 for Bulbasaur, Ivysaur and Venusaur: C1 001 '
            'is on the line (the anchors file\'s third note predates that code).',
            'The coordinator\'s encoder reproduced 3 of the codes byte for byte (reported in the R7 brief, '
            'coordinator-077); lib/test_c1_provisional.py re-encodes all 5 with lib/encode_qr.py.',
            'Deck 03b, encoded with these rules, imported in the game 20/20 with every card right (the anchors '
            'file\'s verified_in_game, copied below). Its list is not in the anchors file, so it is not a test.',
        ],
        'qr_sources': A['qr_sources'],
        'codes_without_list': {k: {'new_cards_by_the_rules': v} for k, v in without_list.items()},
        'anchors_file': {'_about': A['_about'], 'rule': A['rule'], 'exact': A['exact'], 'notes': A['notes'],
                         'verified_in_game': A['verified_in_game'],
                         'by_id': f'{len(A["by_id"])} entries, each equal to its entry below (checked by this build)'},
        'entries': ordered,
        'not_covered': [{'id': cid, 'name': cards[cid][1], 'reason': not_covered[cid]}
                        for cid in sorted(not_covered, key=card_canon._sort_key)],
    }


def render(data):
    """The file's text: JSON, one entry per line in the two id lists, LF, a final newline."""
    out = []
    for k, v in data.items():
        if k in ('entries', 'not_covered'):
            body = ',\n'.join('  ' + json.dumps(x, ensure_ascii=False) for x in v)
            out.append(f' {json.dumps(k)}: [\n{body}\n ]')
        else:
            out.append(f' {json.dumps(k)}: ' + json.dumps(v, indent=1, ensure_ascii=False).replace('\n', '\n '))
    text = '{\n' + ',\n'.join(out) + '\n}\n'
    if json.loads(text) != data:
        raise Refused('build_c1_provisional: REFUSED: the rendered file does not read back as the build')
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description='Build (or --check) lib/c1_provisional_entities.json.')
    ap.add_argument('--anchors', default=ANCHORS, help='the anchors file (default: %(default)s)')
    ap.add_argument('--check', action='store_true', help='rebuild in memory and compare with the file')
    args = ap.parse_args(argv)
    text = render(build(args.anchors)).encode('utf-8')
    if args.check:
        same = os.path.exists(c1.OVERLAY) and read_bytes(c1.OVERLAY) == text
        print(f'{c1.OVERLAY}: ' + ('SAME as this build' if same else 'DIFFERS from this build'))
        return 0 if same else 1
    with io.open(c1.OVERLAY, 'wb') as f:
        f.write(text)
    data = json.loads(text)
    print(f'wrote {c1.OVERLAY}: {data["counts"]["covered"]} covered, {data["counts"]["not_covered"]} not covered '
          f'{data["counts"]["by_derivation"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
