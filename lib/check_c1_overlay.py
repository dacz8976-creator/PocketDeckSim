#!/usr/bin/env python3
"""The provisional C1 deck-code overlay (release checklist R7): its one reader, and the check that
retires it.

lib/c1_provisional_entities.json (built by lib/build_c1_provisional.py; its provenance is inside)
gives Dual Fusion (C1) printings the deck-code entities learned from real deck codes. It is
PROVISIONAL, until the community catalog (lib/s216_card_catalog_v1.json) has C1, and it is never
mixed into that catalog.

load(aliases) is what lib/decode_qr.py and lib/encode_qr.py read beside the catalog's `aliases`,
only for ids and entities the catalog lacks: the catalog always wins. Both keep it apart from their
catalog tables (decode_qr's `by`, encode_qr's BYID), which other code reads. It REFUSES (SystemExit)
when the catalog already has an id the overlay lists, covered or not, or uses an entity the overlay
gives a new card: the community catalog has gained the new cards, so run the check below.
PDL_C1_OVERLAY=off skips the overlay (never the default); a missing overlay file means it was dropped.

THE STOP RULE. When the community catalog gains C1, run

    python3 -I lib/check_c1_overlay.py <that catalog.json> [--overlay PATH]

It compares every overlay entity with the catalog's entity for the same id and prints MATCH or
MISMATCH per id (an id the catalog lacks is a MISMATCH), then "ALL MATCH: drop the overlay" (exit 0)
or "STOP: N mismatches (report to the coordinator)" (exit 1). Any mismatch is a STOP and a report to
the coordinator; if all match, drop the overlay (delete lib/c1_provisional_entities.json). A catalog
that has only not-covered ids (C1 118, SP1, P-C) and no covered one is a STOP too: every covered id is
then a MISMATCH, and load() refuses that catalog. Exit 2: no comparison (the catalog has none of the
overlay's ids, covered or not, or a file cannot be read).

Standard library only.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OVERLAY = os.path.join(HERE, 'c1_provisional_entities.json')
SCHEMA = 'c1_provisional_entities v1'
NOTE = '(provisional C1 entity)'
OFF = 'PDL_C1_OVERLAY'          # PDL_C1_OVERLAY=off skips the overlay; never the default
KINDS = ('pokemon', 'trainer')


def split_key(key):
    """'pokemon:021780' -> ('pokemon', 21780). The catalog pads the number to 6 digits; a deck code
    carries the bare number."""
    kind, _, num = key.partition(':')
    if kind not in KINDS or not num.isdigit():
        raise ValueError(f'bad entity key {key!r}')
    return kind, int(num)


def entity_key(kind, num):
    """The catalog's format: ('pokemon', 21780) -> 'pokemon:021780'."""
    return f'{kind}:{num:06d}'


def base_of(entry):
    """'reprint-of-B3 004' -> 'B3 004'; the entry's own id for 'anchor' and 'rule'."""
    d = entry['derivation']
    return d[len('reprint-of-'):] if d.startswith('reprint-of-') else entry['id']


def read(path=OVERLAY):
    """The overlay file, its shape checked. REFUSES another schema, an id listed twice, a bad key."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    if data.get('schema') != SCHEMA:
        raise SystemExit(f'{path}: not a "{SCHEMA}" file')
    ids = [e['id'] for e in data['entries']] + [e['id'] for e in data['not_covered']]
    if len(ids) != len(set(ids)):
        raise SystemExit(f'{path}: an id is listed twice')
    for e in data['entries']:
        split_key(e['entity_key'])
        if not (e['derivation'] in ('anchor', 'rule') or e['derivation'].startswith('reprint-of-')):
            raise SystemExit(f'{path}: {e["id"]} has an unknown derivation {e["derivation"]!r}')
    return data


def _stop(msg):
    return SystemExit(f'STOP: {msg}. The card catalog seems to have the new cards: run '
                      f'python3 -I lib/check_c1_overlay.py <catalog.json>, report to the coordinator, and '
                      f'drop the overlay if all match ({OFF}=off skips it meanwhile).')


def load(aliases, path=OVERLAY, enabled=None):
    """({id: overlay alias}, {id: not-covered entry}) to read beside the catalog `aliases`. An overlay
    alias has deckgym_id, raw_name, entity_key, base_deckgym_id, derivation and 'provisional': True, not
    the catalog's other fields (no rarity), so it is never added to a catalog table. Both empty when the
    overlay is off (PDL_C1_OVERLAY=off, or enabled=False) or dropped (no file). REFUSES any overlap with
    the catalog (see the module docstring)."""
    if enabled is None:
        enabled = os.environ.get(OFF, '').strip().lower() != 'off'
    if not enabled or not os.path.exists(path):
        return {}, {}
    data = read(path)
    by_id = {a['deckgym_id']: a for a in aliases}
    used = {split_key(a['entity_key']) for a in aliases}
    listed = [e['id'] for e in data['entries'] + data['not_covered'] if e['id'] in by_id]
    if listed:
        more = ', ...' if len(listed) > 5 else ''
        raise _stop(f'the card catalog has {len(listed)} id(s) the provisional C1 overlay lists '
                    f'({", ".join(listed[:5])}{more})')
    covered = {}
    for e in data['entries']:
        key, base = split_key(e['entity_key']), base_of(e)
        if base in by_id:                   # a reprint of an older card: the catalog's own entity
            if split_key(by_id[base]['entity_key']) != key:
                raise _stop(f'{e["id"]} reprints {base}, which the card catalog gives '
                            f'{by_id[base]["entity_key"]}, not {e["entity_key"]}')
        elif key in used:
            raise _stop(f'the card catalog already uses {e["entity_key"]}, which the overlay gives {e["id"]}')
        covered[e['id']] = {'deckgym_id': e['id'], 'raw_name': e['name'], 'entity_key': e['entity_key'],
                            'base_deckgym_id': base, 'derivation': e['derivation'], 'provisional': True}
    return covered, {e['id']: e for e in data['not_covered']}


def compare(data, aliases):
    """([(MATCH or MISMATCH, id, overlay key, catalog key or None)] for every covered id,
    [(id, catalog key)] for the not-covered ids the catalog has)."""
    by_id = {a['deckgym_id']: a for a in aliases}
    rows = []
    for e in data['entries']:
        a = by_id.get(e['id'])
        same = a is not None and split_key(a['entity_key']) == split_key(e['entity_key'])
        rows.append(('MATCH' if same else 'MISMATCH', e['id'], e['entity_key'], a['entity_key'] if a else None))
    found = [(e['id'], by_id[e['id']]['entity_key']) for e in data['not_covered'] if e['id'] in by_id]
    return rows, found


def main(argv=None):
    ap = argparse.ArgumentParser(description='Compare the provisional C1 overlay with a card catalog '
                                             'that has C1 (the STOP rule).')
    ap.add_argument('catalog', help='a card catalog in the s216 format (its "aliases")')
    ap.add_argument('--overlay', default=OVERLAY, help='the overlay file (default: %(default)s)')
    args = ap.parse_args(argv)
    try:
        data = read(args.overlay)
        with open(args.catalog, encoding='utf-8') as f:
            aliases = json.load(f)['aliases']
        rows, found = compare(data, aliases)
    except (OSError, ValueError, KeyError, TypeError, SystemExit) as e:
        print(f'cannot compare: {e}')
        return 2
    for cid, cat in found:
        print(f'NOT COVERED  {cid}  catalog {cat} (the overlay had no entity for it)')
    no_covered = not any(cat for _, _, _, cat in rows)
    if no_covered and not found:
        print('the catalog has none of the overlay\'s ids (no C1 yet): nothing to compare, the overlay stays')
        return 2
    for status, cid, mine, cat in rows:
        print(f'{status:<8}  {cid}  overlay {mine}  catalog {cat or "(no such id)"}')
    if no_covered:
        print(f'the catalog has {len(found)} of the overlay\'s not-covered ids and none of its covered ids: '
              f'decode_qr and encode_qr refuse it; the coordinator decides')
    bad = sum(1 for r in rows if r[0] == 'MISMATCH')
    print(f'STOP: {bad} mismatches (report to the coordinator)' if bad else 'ALL MATCH: drop the overlay')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
