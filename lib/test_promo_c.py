#!/usr/bin/env python3
"""Tests for the four Promo C ids the game wrote (lib/promo_c_entities.json), read by encode_qr / decode_qr.

The scanned payload is from the owner's in-game QR ('New deck 4', Nov 18 2026). Run: python3 -I lib/test_promo_c.py
"""
import os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import decode_qr, encode_qr  # noqa: E402

SCANNED = 'AZic/BMAWXQAVxwAV5QAV54AV3YAWD4AWGYAVb4AWCAAWWAAVUYAVq4AWI4AWc4AV04AWboAWMoAV0QAVnIDBQcG'
DECK = """Energy: Psychic, Darkness, Fighting
1 Bidoof C1 113
1 Abra C1 053
1 Cosmoem C1 065
1 Lunala P-C 008
1 Deoxys P-C 003
1 Haunter C1 082
1 Seviper C1 086
1 Charizard C1 018
1 Rockruff C1 079
1 Snorlax C1 111
1 Pinsir C1 006
1 Mega Greninja ex C1 042
1 Thievul C1 090
1 Malamar P-C 005
1 Marill C1 058
1 Mega Mewtwo Y ex P-C 002
1 Meltan C1 096
1 Mew ex C1 057
1 Jynx C1 036
1 Sweet Honey C1 119
"""
SCANNED_2 = 'AZidfhMAXXAAXUgAV4oAV5QAV54AV54AV3YATHIAXWYAWcQAWcQAWc4AWc4AWboAWboARowAXXoAWaYAN0YDBQED'
DECK_2 = """Energy: Psychic, Grass, Water
1 Cosmog P-C 006
1 Cosmoem P-C 007
2 Lunala P-C 008
1 Deoxys P-C 003
1 Hisuian Zoroark ex B3b 060
2 Inkay P-C 004
2 Malamar P-C 005
2 Mega Mewtwo Y ex P-C 002
1 Mega Audino ex B3 141
1 Pikachu B2 049
1 Genome Converter Y P-C 009
"""


class PromoC(unittest.TestCase):
    def write(self, text):
        d = tempfile.mkdtemp()
        p = os.path.join(d, 'deck.txt')
        with open(p, 'w', encoding='utf-8') as f:
            f.write(text)
        return p

    def test_card_resolves(self):
        for cid, key in (('P-C 002', 'pokemon:022970'), ('P-C 003', 'pokemon:022390'),
                         ('P-C 004', 'pokemon:022980'), ('P-C 005', 'pokemon:022990'),
                         ('P-C 006', 'pokemon:022410'), ('P-C 007', 'pokemon:022420'),
                         ('P-C 008', 'pokemon:022430'), ('P-C 009', 'trainer:001790')):
            self.assertEqual(encode_qr.card(cid)['entity_key'], key)
        for cid in ('P-C 001', 'P-C 010', 'P-C 013'):     # not in either code: stay refused
            self.assertIsNone(encode_qr.card(cid))
        self.assertEqual(set(encode_qr.PROMO_C), {f'P-C 00{i}' for i in range(2, 10)})
        self.assertFalse(set(encode_qr.PROMO_C) & set(encode_qr.PROVISIONAL))

    def test_byte_identical_to_scan(self):
        energy, cards = encode_qr.parse(self.write(DECK))
        self.assertEqual(encode_qr.encode(energy, cards), SCANNED)

    def test_decode_back(self):
        pk, tr, en = decode_qr.decode(SCANNED)
        self.assertEqual(en, [5, 7, 6])
        names = {k.split(' (')[0] for k in list(pk) + list(tr)}
        self.assertIn('Mega Mewtwo Y ex P-C 002', names)
        self.assertIn('Malamar P-C 005', names)
        # shared numbers read back as the C1 card, as before
        self.assertEqual(decode_qr.lookup('pokemon', 22390)[:2], ('C1 062', 'Deoxys'))
        self.assertEqual(decode_qr.lookup('pokemon', 22430)[:2], ('C1 066', 'Lunala'))
        self.assertEqual(decode_qr.lookup('pokemon', 22970)[:2], ('P-C 002', 'Mega Mewtwo Y ex'))
        self.assertEqual(decode_qr.lookup('pokemon', 22990)[:2], ('P-C 005', 'Malamar'))
        self.assertEqual(decode_qr.lookup('pokemon', 22980)[:2], ('P-C 004', 'Inkay'))
        self.assertEqual(decode_qr.lookup('trainer', 1790)[:2], ('P-C 009', 'Genome Converter Y'))

    def test_second_scan_nov20(self):
        # 'New deck 1', Nov 20: the four starters and Bewear ex have no id anywhere, so only the
        # cards with ids are re-encoded here; the full payload is checked slot by slot instead.
        tr, pk, en = decode_qr.read_code(SCANNED_2)
        self.assertEqual(en, [5, 1, 3])
        self.assertEqual(tr, [1790])
        want = [23920, 23880, 22410, 22420, 22430, 22430, 22390, 19570, 23910, 22980, 22980,
                22990, 22990, 22970, 22970, 18060, 23930, 22950, 14150]
        self.assertEqual(pk, want)
        for n in (23920, 23880, 23910, 23930, 22950):              # left out on purpose
            self.assertIsNone(decode_qr.lookup('pokemon', n))
        # every other card in the code: its id from DECK_2 encodes to exactly the number the game wrote
        ids = [l.split(' ', 1)[1].rsplit(' ', 2)[1:] for l in DECK_2.splitlines()[1:]]
        got = sorted(int(encode_qr.card(' '.join(i))['entity_key'].split(':')[1]) for i in ids)
        self.assertEqual(got, sorted(set(want + tr) - {23920, 23880, 23910, 23930, 22950}))

    def test_roundtrip_by_name(self):
        energy, cards = encode_qr.parse(self.write(DECK))
        code = encode_qr.encode(energy, cards)
        pk, tr, _ = decode_qr.decode(code)
        want = sorted(l.split(' ', 1)[1].rsplit(' ', 2)[0] for l in DECK.splitlines()[1:])
        # strip the trailing '(provisional C1 entity)' words and set/number from the decoded names
        back = sorted(k.replace(' (provisional C1 entity)', '').rsplit(' ', 2)[0] for k in list(pk) + list(tr))
        self.assertEqual(back, want)

    def test_still_refused(self):
        deck = DECK.replace('1 Malamar P-C 005', '1 Stantler P-C 010')
        with self.assertRaises(SystemExit):
            encode_qr.parse(self.write(deck))


if __name__ == '__main__':
    unittest.main()
