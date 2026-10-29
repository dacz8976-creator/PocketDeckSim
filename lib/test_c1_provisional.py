#!/usr/bin/env python3
"""Tests for the provisional C1 deck-code overlay (release checklist R7, coordinator-077).

lib/c1_provisional_entities.json (built by lib/build_c1_provisional.py, read by lib/check_c1_overlay.py)
gives Dual Fusion printings the deck-code entities learned from 5 real codes, until the community
catalog has C1. Checked here: the overlay against its anchors, rules and reprint mapping; the five
real codes through lib/decode_qr.py and back through lib/encode_qr.py; the refusals (an uncovered
card, a catalog that already has an overlay id); the catalog's precedence; the release check's MATCH
and STOP paths on synthetic catalogs; and encode_qr reading SP1's "SP1 -NN" ids.

    python3 -I lib/test_c1_provisional.py      (standard library only; the tests that rebuild the
                                                overlay need the anchors file, and skip without it)
"""
import base64
import collections
import contextlib
import copy
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import build_c1_provisional as build   # noqa: E402
import card_canon                       # noqa: E402
import check_c1_overlay as c1           # noqa: E402
import decode_qr                        # noqa: E402
import encode_qr                        # noqa: E402

DATA = c1.read()
ENTRIES = {e['id']: e for e in DATA['entries']}
NOT_COVERED = {e['id']: e for e in DATA['not_covered']}
SOURCES = DATA['qr_sources']
CODES = [s['text'] for s in SOURCES]
ALIASES = encode_qr._aliases                        # the catalog both tools read
S216 = {a['deckgym_id']: a for a in ALIASES}
CANON = card_canon.Canon(build.MAP)
with io.open(build.DB, encoding='utf-8') as _f:
    DB = {e[k]['id']: (k, e[k]['name']) for e in json.load(_f) for k in e}
NEW_IDS = [i for i in DB if i.split(' ')[0] in ('C1', 'SP1', 'P-C')]
HAVE_ANCHORS = os.path.exists(build.ANCHORS)
TRAINER_ANCHORS = ['C1 119', 'C1 120', 'C1 121', 'C1 124', 'C1 127', 'C1 129', 'C1 130', 'C1 131']

# Code 1's list (the anchors file), in the code's own order, as a deck file.
CODE1_DECK = """Energy: Lightning
2 Light Ball C1 124
2 Rare Candy A3 144
2 Poké Ball P-A 005
2 Professor's Research P-A 007
1 Cyrus A2 150
1 Dawn A2 154
2 Serena's Choice C1 127
2 Pikachu ex C1 043
2 Pawmi C1 048
2 Pawmo C1 049
2 Pawmot C1 050
"""


def card_name(decoded):
    """'Pikachu ex C1 043 (provisional C1 entity)' -> 'Pikachu ex'."""
    return decoded.replace(' ' + c1.NOTE, '').rsplit(' ', 2)[0]


def card_id(decoded):
    """'Pikachu ex C1 043 (provisional C1 entity)' -> 'C1 043'."""
    return ' '.join(decoded.replace(' ' + c1.NOTE, '').split()[-2:])


def run(fn, *args):
    """fn(*args) with its printed output captured: (result, printed lines)."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        r = fn(*args)
    return r, out.getvalue().splitlines()


class TempDir(unittest.TestCase):

    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix='test_c1_provisional_')
        self.addCleanup(td.cleanup)
        self.dir = td.name

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        return path


# ---------------------------------------------------------------------------------------------
# The overlay file: provenance, coverage, rules, anchors
# ---------------------------------------------------------------------------------------------

class OverlayFile(TempDir):

    def test_provenance(self):
        self.assertEqual(DATA['label'], 'provisional, until the community catalog has C1')
        self.assertEqual(DATA['approval'], {
            'by': 'Dustin', 'words': "Yes that's fine. We can double check when the community one is available",
            'when': 'Oct 29, 2026, about 02:00Z', 'via': 'coordinator-077'})
        for part in ('check_c1_overlay.py', 'STOP', 'report to the coordinator', 'drop the overlay'):
            self.assertIn(part, DATA['stop_rule'])
        self.assertEqual(len(SOURCES), 5)
        self.assertEqual(len(DATA['inputs']['anchors_file']['sha256']), 64)
        for e in DATA['entries']:
            self.assertTrue(e['derivation'] in ('anchor', 'rule') or e['derivation'].startswith('reprint-of-'), e)
            self.assertEqual('codes' in e, e['derivation'] == 'anchor', e)

    def test_file_is_lf_and_names_are_the_database_names(self):
        with io.open(c1.OVERLAY, 'rb') as f:
            self.assertNotIn(b'\r', f.read())
        for cid, e in list(ENTRIES.items()) + list(NOT_COVERED.items()):
            self.assertEqual(e['name'], DB[cid][1], cid)

    def test_covered_and_not_covered_split_every_new_printing(self):
        self.assertEqual(len(NEW_IDS), 260)
        self.assertEqual(len(ENTRIES), 213)
        self.assertEqual(len(NOT_COVERED), 47)
        self.assertEqual(set(ENTRIES) | set(NOT_COVERED), set(NEW_IDS))
        self.assertFalse(set(ENTRIES) & set(NOT_COVERED))
        self.assertEqual(sorted(i for i in NOT_COVERED if i.startswith('C1 ')), ['C1 118', 'C1 164', 'C1 182', 'C1 214'])
        self.assertEqual(sorted(i for i in NEW_IDS if not i.startswith('C1 ')),
                         sorted(i for i in NOT_COVERED if not i.startswith('C1 ')))   # all of SP1 and P-C
        for e in NOT_COVERED.values():
            self.assertTrue(e['reason'], e)
        self.assertEqual(DATA['counts']['covered'], 213)
        self.assertEqual(DATA['counts']['not_covered'], 47)

    def test_the_rules_and_the_reprint_mapping_hold(self):
        for cid, e in ENTRIES.items():
            n = int(cid.split()[1])
            key = c1.split_key(e['entity_key'])
            with self.subTest(id=cid):
                self.assertEqual(e['entity_key'], c1.entity_key(*key))      # the catalog's padded format
                if n <= 131:
                    self.assertIn(e['derivation'], ('anchor', 'rule'))
                    self.assertEqual(key, build.rule_entity(n))
                    self.assertEqual(CANON.base_id(cid), cid)
                else:
                    base = c1.base_of(e)
                    self.assertEqual(e['derivation'], f'reprint-of-{base}')
                    self.assertEqual(CANON.base_id(cid), base)
                    self.assertTrue(CANON.same_card(cid, base))
                    want = ENTRIES[base]['entity_key'] if base in ENTRIES else S216[base]['entity_key']
                    self.assertEqual(e['entity_key'], want)
                    self.assertNotIn(base, NOT_COVERED)
                    for p in CANON.prints_of(cid):                          # every printing of the card agrees
                        if p in S216:
                            self.assertEqual(S216[p]['entity_key'], e['entity_key'], p)
                self.assertEqual(key[0], DB[cid][0].lower())
        self.assertEqual(ENTRIES['C1 187']['entity_key'], 'pokemon:016690')    # Celebi, B3 004's entity
        self.assertEqual(ENTRIES['C1 187']['derivation'], 'reprint-of-B3 004')

    def test_every_anchor_sits_in_its_code(self):
        anchors = [e for e in DATA['entries'] if e['derivation'] == 'anchor']
        self.assertEqual(len(anchors), 42)
        self.assertEqual([e['id'] for e in anchors if e['entity_key'].startswith('trainer:')], TRAINER_ANCHORS)
        for e in anchors:
            kind, n = c1.split_key(e['entity_key'])
            for i in e['codes']:
                with self.subTest(id=e['id'], code=i):
                    self.assertTrue('decklist' in SOURCES[i - 1] or 'anchors' in SOURCES[i - 1])
                    tr, pk, _ = decode_qr.read_code(CODES[i - 1])
                    self.assertIn(n, pk if kind == 'pokemon' else tr)

    @unittest.skipUnless(HAVE_ANCHORS, 'the anchors file is not on this machine')
    def test_the_overlay_matches_the_anchors_file(self):
        with io.open(build.ANCHORS, 'rb') as f:
            raw = f.read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), DATA['inputs']['anchors_file']['sha256'])
        A = json.loads(raw.decode('utf-8'))
        self.assertEqual(len(A['by_id']), 130)
        for cid, (kind, n, name) in A['by_id'].items():
            with self.subTest(id=cid):
                self.assertEqual(c1.split_key(ENTRIES[cid]['entity_key']), (kind, n))
                self.assertEqual(build.norm(ENTRIES[cid]['name']), build.norm(name))
        for label, key in A['exact'].items():
            self.assertEqual(c1.split_key(ENTRIES[' '.join(label.split()[:2])]['entity_key']), c1.split_key(key))
        self.assertEqual(A['qr_sources'], SOURCES)

    @unittest.skipUnless(HAVE_ANCHORS, 'the anchors file is not on this machine')
    def test_the_build_reproduces_the_file(self):
        with io.open(c1.OVERLAY, encoding='utf-8') as f:
            self.assertEqual(build.render(build.build()), f.read())

    @unittest.skipUnless(HAVE_ANCHORS, 'the anchors file is not on this machine')
    def test_the_build_refuses_a_contradicting_anchor(self):
        with io.open(build.ANCHORS, encoding='utf-8') as f:
            A = json.load(f)
        bad = copy.deepcopy(A)
        bad['by_id']['C1 050'][1] += 10                                    # off the line
        with self.assertRaises(build.Refused):
            build.build(self.write('a1.json', json.dumps(bad)))
        bad = copy.deepcopy(A)
        bad['qr_sources'][0]['decklist'] = bad['qr_sources'][0]['decklist'].replace('2 Pawmo', '2 Pawmot')
        with self.assertRaises(build.Refused):                              # code 1 no longer decodes to its list
            build.build(self.write('a2.json', json.dumps(bad)))
        bad = copy.deepcopy(A)
        bad['qr_sources'][4]['anchors'] = bad['qr_sources'][4]['anchors'].replace('018', '019')
        with self.assertRaises(build.Refused):
            build.build(self.write('a3.json', json.dumps(bad)))


# ---------------------------------------------------------------------------------------------
# lib/decode_qr.py: the real codes, the provisional mark, UNKNOWN, the catalog's precedence
# ---------------------------------------------------------------------------------------------

class Decode(unittest.TestCase):

    def test_the_overlay_is_loaded(self):
        self.assertEqual(sum(len(v) for v in decode_qr.prov.values()), 213)
        self.assertFalse([a for lst in decode_qr.by.values() for a in lst if a.get('provisional')])   # `by` is the catalog's

    def test_every_source_code_decodes_with_no_unknown_card(self):
        for i, code in enumerate(CODES, 1):
            pk, tr, _ = decode_qr.decode(code)
            with self.subTest(code=i):
                self.assertFalse([n for n in list(pk) + list(tr) if n.startswith('UNKNOWN')])
                self.assertEqual(sum(pk.values()) + sum(tr.values()), 20)

    def test_codes_with_a_list_decode_to_it(self):
        for i, src in enumerate(SOURCES, 1):
            if 'decklist' not in src:
                continue
            with self.subTest(code=i):
                pk, tr, en = decode_qr.decode(src['text'])
                got = collections.Counter()
                for n, c in list(pk.items()) + list(tr.items()):
                    got[build.norm(card_name(n))] += c
                want, energy = build.read_decklist(src['decklist'])
                self.assertEqual(got, want)
                self.assertEqual(sorted(en), sorted(energy))

    def test_code_1_decodes_to_its_cards(self):
        pk, tr, en = decode_qr.decode(CODES[0])
        note = ' ' + c1.NOTE
        self.assertEqual(pk, collections.Counter({'Pikachu ex C1 043' + note: 2, 'Pawmi C1 048' + note: 2,
                                                  'Pawmo C1 049' + note: 2, 'Pawmot C1 050' + note: 2}))
        self.assertEqual(tr, collections.Counter({'Light Ball C1 124' + note: 2, 'Rare Candy A3 144': 2,
                                                  'Poké Ball P-A 005': 2, 'Professor’s Research P-A 007': 2,
                                                  'Cyrus A2 150': 1, 'Dawn A2 154': 1,
                                                  "Serena's Choice C1 127" + note: 2}))
        self.assertEqual(en, [4])

    def test_code_5_decodes_to_its_anchor_ids(self):
        pk, tr, _ = decode_qr.decode(CODES[4])
        want = ['C1 018', 'C1 027', 'C1 030', 'C1 036', 'C1 055', 'C1 061', 'C1 062', 'C1 064', 'C1 067',
                'C1 073', 'C1 075', 'C1 077', 'C1 078', 'C1 088', 'C1 089', 'C1 103', 'C1 116', 'C1 117']
        self.assertEqual(sorted(card_id(n) for n in pk), want)
        self.assertTrue(all(n.endswith(c1.NOTE) for n in pk))
        self.assertEqual((pk[[n for n in pk if card_id(n) == 'C1 116'][0]], len(tr)), (2, 0))

    def test_the_five_codes_reencode_byte_for_byte(self):
        for i, code in enumerate(CODES, 1):
            tr, pk, en = decode_qr.read_code(code)
            cards = ([(1, decode_qr.lookup('trainer', n)[0]) for n in tr]
                     + [(1, decode_qr.lookup('pokemon', n)[0]) for n in pk])
            with self.subTest(code=i):
                self.assertEqual(encode_qr.encode(en, cards), code)

    def test_an_uncovered_card_is_unknown(self):
        self.assertIsNone(decode_qr.lookup('pokemon', 22950))             # where C1 118 would be, by the line
        code = base64.b64encode(bytes([0, 1]) + (22950).to_bytes(3, 'big') + bytes([1, 1])).decode()
        pk, tr, en = decode_qr.decode(code)
        self.assertEqual(pk, collections.Counter({'UNKNOWN pokemon:22950': 1}))
        self.assertEqual(decode_qr.name('trainer', 1790), 'UNKNOWN trainer:1790')   # after C1 131

    def test_the_catalog_wins(self):
        self.assertEqual(decode_qr.lookup('pokemon', 16690), ('B3 004', 'Celebi', False))   # C1 187's entity
        for e in DATA['entries']:
            kind, n = c1.split_key(e['entity_key'])
            cid, _, provisional = decode_qr.lookup(kind, n)
            with self.subTest(id=e['id']):
                if c1.base_of(e) in S216:
                    self.assertEqual((cid in S216, provisional), (True, False))
                else:
                    self.assertEqual((cid, provisional), (min(i for i, x in ENTRIES.items()
                                                              if x['entity_key'] == e['entity_key']), True))


# ---------------------------------------------------------------------------------------------
# lib/encode_qr.py: round trips, refusals, the catalog's precedence, "SP1 -NN"
# ---------------------------------------------------------------------------------------------

class Encode(TempDir):

    def test_byid_stays_the_catalog_and_the_overlay_is_apart(self):
        # BYID's other readers (rl/deck_journal/journal.py, the Ladder QR page's build.py) see the catalog only
        self.assertEqual(set(encode_qr.BYID), set(S216))
        for cid, a in encode_qr.BYID.items():
            self.assertIs(a, S216[cid])                                     # the catalog's own entry, unchanged
            self.assertIn('rarity', a)
            self.assertNotIn('provisional', a)
        self.assertEqual(set(encode_qr.PROVISIONAL), set(ENTRIES))
        for cid, a in encode_qr.PROVISIONAL.items():
            self.assertTrue(a['provisional'], cid)
            self.assertEqual(a['entity_key'], ENTRIES[cid]['entity_key'])
            self.assertIs(encode_qr.card(cid), a)
        self.assertIs(encode_qr.card('B3 004'), S216['B3 004'])
        self.assertIsNone(encode_qr.card('C1 118'))
        self.assertEqual(encode_qr.card('C1 187')['entity_key'], S216['B3 004']['entity_key'])
        self.assertEqual(set(encode_qr.NOT_COVERED), set(NOT_COVERED))

    def test_code_1_list_encodes_to_code_1_and_back(self):
        energy, cards = encode_qr.parse(self.write('code1.txt', CODE1_DECK))
        code = encode_qr.encode(energy, cards)
        self.assertEqual(code, CODES[0])
        pk, tr, en = decode_qr.decode(code)
        got = collections.Counter()
        for n, c in list(pk.items()) + list(tr.items()):
            got[card_id(n)] += c
        self.assertEqual(got, collections.Counter({cid: n for n, cid in cards}))
        self.assertEqual(en, energy)

    def test_alternate_printings_round_trip_as_their_card(self):
        deck = self.write('alts.txt', """Energy: Lightning
2 Pikachu ex C1 156
2 Pawmi C1 048
2 Pawmo C1 049
2 Pawmot C1 142
1 Celebi C1 187
1 Mega Dragonite ex C1 211
2 Sweet Honey C1 152
2 Serena's Choice C1 167
2 Poké Ball P-A 005
2 Professor's Research P-A 007
2 Rare Candy A3 144
""")
        pk, tr, en = decode_qr.decode(encode_qr.encode(*encode_qr.parse(deck)))
        note = ' ' + c1.NOTE
        self.assertEqual(pk, collections.Counter({'Pikachu ex C1 043' + note: 2, 'Pawmi C1 048' + note: 2,
                                                  'Pawmo C1 049' + note: 2, 'Pawmot C1 050' + note: 2,
                                                  'Celebi B3 004': 1, 'Mega Dragonite ex C1 100' + note: 1}))
        self.assertEqual(tr, collections.Counter({'Sweet Honey C1 119' + note: 2, "Serena's Choice C1 127" + note: 2,
                                                  'Poké Ball P-A 005': 2, 'Professor’s Research P-A 007': 2,
                                                  'Rare Candy A3 144': 2}))

    def test_an_uncovered_card_is_refused_with_the_reason(self):
        for line, cid in (('1 Bewear ex C1 118', 'C1 118'), ('1 Bewear ex C1 164', 'C1 164'),
                          ('1 Mew SP1 -03', 'SP1 -03'), ('1 Froakie SP1 018', 'SP1 018'),
                          ('1 Pikachu P-C 001', 'P-C 001')):
            with self.subTest(card=cid):
                deck = self.write('uncovered.txt', CODE1_DECK.replace('1 Dawn A2 154', line))
                with self.assertRaises(SystemExit) as cm:
                    encode_qr.parse(deck)
                msg = str(cm.exception)
                self.assertIn(f'{cid} ({DB[cid][1]}) cannot be encoded', msg)
                self.assertIn(NOT_COVERED[cid]['reason'], msg)

    def test_the_cli_names_the_provisional_cards(self):
        deck = self.write('code1.txt', CODE1_DECK)
        r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'encode_qr.py'), deck, '--no-png'],
                           capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0], f'== code1.txt  code={CODES[0]}')
        self.assertEqual(lines[1], '   provisional C1 entities (until the community catalog has C1; '
                                   'lib/c1_provisional_entities.json): C1 124, C1 127, C1 043, C1 048, C1 049, C1 050')

    def test_line_reads_sp1_minus_ids(self):
        m = encode_qr.LINE.match('2 Mew SP1 -03')
        self.assertEqual((m[1], m[2], m[3]), ('2', 'Mew', 'SP1 -03'))
        m = encode_qr.LINE.match('2 Mega Mewtwo X ex C1 056')
        self.assertEqual((m[2], m[3]), ('Mega Mewtwo X ex', 'C1 056'))
        for cid, (_, name) in DB.items():                                   # every database id, as written
            m = encode_qr.LINE.match(f'1 {name} {cid}')
            with self.subTest(id=cid):
                self.assertEqual((m[2], m[3]) if m else None, (name, cid))

    def test_an_sp1_line_reaches_the_card_lookup(self):
        deck = self.write('mew.txt', CODE1_DECK.replace('1 Dawn A2 154', '1 Mew SP1 -01'))
        with self.assertRaises(SystemExit) as cm:
            encode_qr.parse(deck)
        self.assertNotIn('cannot parse line', str(cm.exception))
        self.assertIn('SP1 -01 (Mew) cannot be encoded', str(cm.exception))


# ---------------------------------------------------------------------------------------------
# lib/check_c1_overlay.py load(): refuses any overlap with the catalog
# ---------------------------------------------------------------------------------------------

def alias(cid, key, name='Synthetic'):
    return {'deckgym_id': cid, 'entity_key': key, 'raw_name': name, 'rarity': 'C'}


class Load(TempDir):

    def test_the_real_catalog_loads(self):
        covered, not_covered = c1.load(ALIASES, enabled=True)
        self.assertEqual((len(covered), len(not_covered)), (213, 47))
        self.assertFalse(set(covered) & set(S216))

    def test_a_catalog_with_an_overlay_id_is_refused(self):
        for extra in (alias('C1 043', 'pokemon:022200', 'Pikachu ex'),     # a covered id, same entity
                      alias('C1 043', 'pokemon:099990'),                    # a covered id, another entity
                      alias('C1 118', 'pokemon:022950', 'Bewear ex'),       # a not-covered id
                      alias('SP1 -03', 'pokemon:099990', 'Mew')):
            with self.subTest(extra=extra['deckgym_id']):
                with self.assertRaises(SystemExit) as cm:
                    c1.load(ALIASES + [extra], enabled=True)
                self.assertIn('STOP', str(cm.exception))
                self.assertIn(extra['deckgym_id'], str(cm.exception))
                self.assertIn('check_c1_overlay.py', str(cm.exception))

    def test_a_catalog_using_an_overlay_entity_is_refused(self):
        with self.assertRaises(SystemExit) as cm:
            c1.load(ALIASES + [alias('ZZ 001', 'trainer:001660')], enabled=True)
        self.assertIn('trainer:001660', str(cm.exception))
        self.assertIn('C1 119', str(cm.exception))

    def test_a_reprint_whose_base_changed_entity_is_refused(self):
        aliases = copy.deepcopy(ALIASES)
        for a in aliases:
            if a['deckgym_id'] == 'B3 004':
                a['entity_key'] = 'pokemon:099990'
        with self.assertRaises(SystemExit) as cm:
            c1.load(aliases, enabled=True)
        self.assertIn('C1 187', str(cm.exception))

    def test_off_or_dropped(self):
        self.assertEqual(c1.load(ALIASES, enabled=False), ({}, {}))
        self.assertEqual(c1.load(ALIASES, path=os.path.join(self.dir, 'dropped.json'), enabled=True), ({}, {}))

    def test_a_bad_overlay_file_is_refused(self):
        dup = dict(DATA, entries=DATA['entries'] + DATA['entries'][:1])
        with self.assertRaises(SystemExit):
            c1.read(self.write('dup.json', json.dumps(dup)))
        with self.assertRaises(SystemExit):
            c1.read(self.write('schema.json', json.dumps(dict(DATA, schema='other'))))


# ---------------------------------------------------------------------------------------------
# lib/check_c1_overlay.py: the compare-on-release check
# ---------------------------------------------------------------------------------------------

class Compare(TempDir):

    def catalog(self, key=lambda e: e['entity_key'], drop=(), extra=()):
        """The real catalog plus every overlay id, with entity `key(entry)`: a stand-in for a community
        catalog that has C1."""
        aliases = list(ALIASES) + [alias(e['id'], key(e), e['name']) for e in DATA['entries'] if e['id'] not in drop]
        return self.write('catalog.json', json.dumps({'aliases': aliases + list(extra)}))

    def test_all_match(self):
        rc, lines = run(c1.main, [self.catalog()])
        self.assertEqual(rc, 0)
        self.assertEqual(lines[-1], 'ALL MATCH: drop the overlay')
        self.assertEqual(sum(1 for ln in lines if ln.startswith('MATCH ')), 213)
        self.assertIn('MATCH     C1 001  overlay pokemon:021780  catalog pokemon:021780', lines)

    def test_unpadded_numbers_still_match(self):
        rc, lines = run(c1.main, [self.catalog(key=lambda e: '%s:%d' % c1.split_key(e['entity_key']))])
        self.assertEqual((rc, lines[-1]), (0, 'ALL MATCH: drop the overlay'))

    def test_a_mismatch_or_a_missing_id_is_a_stop(self):
        wrong = lambda e: 'pokemon:021800' if e['id'] == 'C1 002' else e['entity_key']    # noqa: E731
        rc, lines = run(c1.main, [self.catalog(key=wrong, drop=('C1 133',))])
        self.assertEqual(rc, 1)
        self.assertEqual(lines[-1], 'STOP: 2 mismatches (report to the coordinator)')
        self.assertIn('MISMATCH  C1 002  overlay pokemon:021790  catalog pokemon:021800', lines)
        self.assertIn('MISMATCH  C1 133  overlay pokemon:021810  catalog (no such id)', lines)
        self.assertEqual(sum(1 for ln in lines if ln.startswith('MATCH ')), 211)

    def test_a_not_covered_card_is_reported_and_does_not_change_the_verdict(self):
        rc, lines = run(c1.main, [self.catalog(extra=[alias('C1 118', 'pokemon:022950', 'Bewear ex')])])
        self.assertEqual(rc, 0)
        self.assertIn('NOT COVERED  C1 118  catalog pokemon:022950 (the overlay had no entity for it)', lines)

    def test_a_catalog_without_c1_is_no_comparison(self):
        rc, lines = run(c1.main, [encode_qr._cat])
        self.assertEqual(rc, 2)
        self.assertIn('nothing to compare', lines[-1])

    def test_a_catalog_with_only_not_covered_ids_is_a_stop(self):
        pc = [alias(e['id'], 'pokemon:%06d' % (90000 + 10 * i), e['name'])
              for i, e in enumerate(DATA['not_covered']) if e['id'].startswith('P-C ')]
        aliases = list(ALIASES) + pc
        with self.assertRaises(SystemExit):
            c1.load(aliases, enabled=True)                                  # the tools refuse it ...
        rc, lines = run(c1.main, [self.write('catalog.json', json.dumps({'aliases': aliases}))])
        self.assertEqual(rc, 1)                                             # ... and the check says STOP
        self.assertEqual(lines[-1], f'STOP: {len(ENTRIES)} mismatches (report to the coordinator)')
        self.assertIn(f"the catalog has {len(pc)} of the overlay's not-covered ids and none of its covered ids: "
                      'decode_qr and encode_qr refuse it; the coordinator decides', lines)
        self.assertFalse([ln for ln in lines if 'nothing to compare' in ln])

    def test_the_exit_codes(self):
        script = os.path.join(HERE, 'check_c1_overlay.py')
        ok = subprocess.run([sys.executable, '-I', script, self.catalog()], capture_output=True, text=True)
        self.assertEqual((ok.returncode, ok.stdout.splitlines()[-1]), (0, 'ALL MATCH: drop the overlay'))
        wrong = lambda e: 'trainer:001670' if e['id'] == 'C1 119' else e['entity_key']    # noqa: E731
        stop = subprocess.run([sys.executable, '-I', script, self.catalog(key=wrong)], capture_output=True, text=True)
        self.assertEqual((stop.returncode, stop.stdout.splitlines()[-1]),
                         (1, 'STOP: 1 mismatches (report to the coordinator)'))


if __name__ == '__main__':
    unittest.main()
