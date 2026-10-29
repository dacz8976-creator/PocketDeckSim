#!/usr/bin/env python3
"""Tests for the dual-type seam in the Python card-database readers (Dual Fusion prep, step 1).

Every single-type card must be read exactly as on main b78c8997. A dual-type Pokémon (Mega
Mewtwo X ex = Psychic/Fighting, one Weakness) must be shown with both types (lib/card.py), kept
apart in lib/card_canon.py's fingerprint, and REFUSED by the readers whose dual-type rule is not
settled (lib/consistency.py, lib/brew_consistency.py, lib/deck_classifier.py): never read as its
first type, never left out. Most dual-type cards here are synthetic: real cards from
lib/deckgym-database.json with a second type added, in each of the three data shapes upstream may
choose (deckgym issue #429). The real ones, Dual Fusion's (REAL_DUAL_IDS), are checked too.

    python3 lib/test_dual_type_readers.py      (from the project root; standard library only)
"""
import contextlib
import copy
import hashlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import card              # noqa: E402
import card_canon        # noqa: E402
import consistency       # noqa: E402
import brew_consistency  # noqa: E402
import deck_classifier   # noqa: E402

DB = card.load()                          # [(kind, inner dict)], as the readers get it
BY_ID = {v['id']: (k, v) for k, v in DB}
SHAPES = ('secondary', 'list', 'energy_types')
# The real dual-type printings (Dual Fusion, C1, in the engine's 'secondary_energy_type' field):
# Mega Greninja ex (Water/Darkness) and Mega Mewtwo X ex (Psychic/Fighting). Pinned: a refresh
# that adds or drops one must update this list consciously.
REAL_DUAL_IDS = ['C1 042', 'C1 056', 'C1 155', 'C1 157', 'C1 173', 'C1 175', 'C1 185']
REAL_DUAL = [BY_ID[i][1] for i in REAL_DUAL_IDS if i in BY_ID]
SINGLE = [(k, v) for k, v in DB if v['id'] not in REAL_DUAL_IDS]    # read exactly as on main


def db_path():
    """The database file card.load() reads (same search order)."""
    for p in (os.environ.get('PDL_DB', ''), os.path.join(HERE, 'deckgym-database.json'),
              os.path.join(HERE, '..', 'deckgym-database.json'), 'deckgym-database.json'):
        if p and os.path.exists(p):
            return p
    return None


def real(cid):
    """A deep copy of a real card's inner dict."""
    return copy.deepcopy(BY_ID[cid][1])


def dual(cid, primary, secondary, shape='secondary', **extra):
    """A synthetic dual-type Pokémon: real card `cid` printed as primary/secondary, in one of the
    three candidate data shapes. `extra` overrides other fields (weakness, name, id)."""
    v = real(cid)
    v.update(extra)
    if shape == 'secondary':
        v['energy_type'], v['secondary_energy_type'] = primary, secondary
    elif shape == 'list':
        v['energy_type'] = [primary, secondary]
    elif shape == 'energy_types':
        del v['energy_type']
        v['energy_types'] = [primary, secondary]
    else:
        raise AssertionError(shape)
    return v


class FixedRng:
    """A stand-in for random.Random that makes a deal readable: no shuffling, the first choice,
    index 0, every coin tails."""

    def shuffle(self, seq):
        pass

    def choice(self, seq):
        return seq[0]

    def randrange(self, n):
        return 0

    def random(self):
        return 0.99


def old_fmt(kind, v):
    """lib/card.py fmt() as on main b78c8997, copied verbatim."""
    if kind == 'Pokemon':
        head = (f"{v['name']}  [{v['id']}]  {v['energy_type']}  Stage {v['stage']}"
                + (f" (from {v['evolves_from']})" if v.get('evolves_from') else '')
                + f"  HP {v['hp']}  weak {v.get('weakness') or '-'}  retreat {len(v.get('retreat_cost') or [])}")
        lines = [head]
        if v.get('ability'):
            lines.append(f"  Ability {v['ability']['title']}: {v['ability']['effect']}")
        for a in v.get('attacks', []):
            dmg = a.get('fixed_damage')
            lines.append(f"  [{card.cost(a['energy_required'])}] {a['title']}" + (f" {dmg}" if dmg else '')
                         + (f" — {a['effect']}" if a.get('effect') else ''))
        return '\n'.join(lines)
    return f"{v['name']}  [{v['id']}]  {kind}\n  {v.get('effect') or ''}"


def old_fingerprint(entry):
    """lib/card_canon.py fingerprint() as on main b78c8997, copied verbatim."""
    kind = list(entry.keys())[0]; c = entry[kind]
    if kind == 'Pokemon':
        f = {'kind': kind, 'name': c['name'], 'stage': c['stage'],
             'evolves_from': c['evolves_from'], 'hp': c['hp'],
             'energy_type': c['energy_type'], 'ability': c['ability'],
             'attacks': c['attacks'], 'weakness': c['weakness'],
             'retreat_cost': c['retreat_cost']}
    else:
        f = {'kind': kind, 'name': c['name'],
             'trainer_card_type': c.get('trainer_card_type'), 'effect': c.get('effect')}
    return hashlib.sha1(json.dumps(f, sort_keys=True, ensure_ascii=True).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------------------------
# lib/card.py: the one helper
# ---------------------------------------------------------------------------------------------

class PrintedTypes(unittest.TestCase):

    def test_every_real_card_is_exactly_its_energy_type(self):
        n = 0
        for kind, v in SINGLE:
            if kind == 'Pokemon':
                self.assertEqual(card.printed_types(v), [v['energy_type']], v['id'])
                self.assertEqual(card.single_type(v, 'test'), v['energy_type'], v['id'])
                n += 1
        self.assertGreater(n, 3000)

    def test_the_real_dual_type_cards_are_pinned(self):
        found = [v['id'] for kind, v in DB if kind == 'Pokemon' and len(card.printed_types(v)) > 1]
        self.assertEqual(found, REAL_DUAL_IDS)

    def test_every_real_dual_type_card_has_both_types_and_is_refused(self):
        self.assertEqual(len(REAL_DUAL), len(REAL_DUAL_IDS))
        for v in REAL_DUAL:
            with self.subTest(id=v['id']):
                self.assertEqual(card.printed_types(v), [v['energy_type'], v['secondary_energy_type']])
                with self.assertRaises(card.DualTypeUnsupported):
                    card.single_type(v, 'test')

    def test_all_three_shapes(self):
        P, F = 'Psychic', 'Fighting'
        cases = [
            ({'energy_type': 'Water'}, ['Water']),
            ({'energy_type': 'Water', 'secondary_energy_type': None}, ['Water']),
            ({'energy_type': ['Water']}, ['Water']),
            ({'energy_types': ['Water']}, ['Water']),
            ({'energy_type': P, 'secondary_energy_type': F}, [P, F]),
            ({'energy_type': [P, F]}, [P, F]),
            ({'energy_types': [P, F]}, [P, F]),
            ({'energy_type': P, 'energy_types': [P, F]}, [P, F]),      # energy_type kept as the primary
            ({'energy_type': [P, F], 'energy_types': [P, F]}, [P, F]),
            ({'energy_type': P, 'secondary_energy_type': F, 'energy_types': [P, F]}, [P, F]),
            ({'energy_type': P, 'secondary_energy_type': F, 'weakness': 'Darkness'}, [P, F]),
            ({'energy_type': [P, F], 'secondary_energy_type': F}, [P, F]),  # the list's second entry repeated
        ]
        for v, want in cases:
            with self.subTest(v=v):
                self.assertEqual(card.printed_types(v), want)

    def test_returns_a_fresh_list(self):
        v = {'energy_type': ['Psychic', 'Fighting']}
        card.printed_types(v).append('Water')
        self.assertEqual(v['energy_type'], ['Psychic', 'Fighting'])

    def test_malformed_type_data_refused(self):
        P, F = 'Psychic', 'Fighting'
        bad = [
            {},                                                          # no type
            {'energy_type': None},
            {'energy_type': []},                                         # empty
            {'energy_types': []},
            {'energy_type': ''},
            {'energy_type': [P, F, 'Water']},                            # more than two
            {'energy_types': [P, F, 'Water']},
            {'energy_type': P, 'secondary_energy_type': P},              # a repeated type
            {'energy_type': [P, P]},
            {'energy_type': P, 'energy_types': ['Water', 'Darkness']},   # shapes disagree
            {'energy_type': F, 'energy_types': [P, F]},                  # energy_type is not the primary
            {'energy_type': P, 'secondary_energy_type': F, 'energy_types': [P, 'Darkness']},
            {'energy_type': P, 'secondary_energy_type': F, 'energy_types': [P]},
            {'energy_type': [P, F], 'energy_types': [F, P]},
            {'energy_type': [P, F], 'secondary_energy_type': P},         # a secondary field the list disagrees with
            {'energy_type': [P], 'secondary_energy_type': F},
            {'secondary_energy_type': F},                                # a second type with no first
            {'energy_types': P},                                         # not a list
            {'energy_type': [P, 7]},                                     # not a type name
            {'energy_type': P, 'secondary_energy_type': 'Fightning'},    # a misspelt type
            {'energy_type': 'psychic'},
            {'energy_type': P, 'secondary_type': F},                     # an unknown field naming a type
            {'energy_type': P, 'types': [P, F]},
            {'energy_type': P, 'weakness': ['Darkness']},                # a list Weakness
            {'energy_type': P, 'secondary_energy_type': F, 'weakness': ['Darkness', 'Psychic']},
        ]
        for v in bad:
            with self.subTest(v=v):
                with self.assertRaises(ValueError) as cm:
                    card.printed_types(dict(v, name='Synthetic', id='ZZ 001'))
                self.assertNotIsInstance(cm.exception, card.DualTypeUnsupported)
                self.assertIn('Synthetic [ZZ 001]', str(cm.exception))

    def test_single_type_refuses_a_dual_type_card_by_name_and_reader(self):
        self.assertEqual(card.single_type(real('A1 001'), 'the test reader'), 'Grass')
        for shape in SHAPES:
            with self.subTest(shape=shape):
                with self.assertRaises(card.DualTypeUnsupported) as cm:
                    card.single_type(dual('A1 001', 'Grass', 'Psychic', shape), 'the test reader')
                msg = str(cm.exception)
                for part in ('Bulbasaur [A1 001]', 'Grass/Psychic', 'the test reader'):
                    self.assertIn(part, msg)
                self.assertIsInstance(cm.exception, ValueError)


class Fmt(unittest.TestCase):

    def test_every_real_card_prints_as_on_main(self):
        for kind, v in SINGLE:
            self.assertEqual(card.fmt(kind, v), old_fmt(kind, v), v['id'])

    def test_every_real_dual_type_card_shows_both_types(self):
        for v in REAL_DUAL:
            with self.subTest(id=v['id']):
                text, old = card.fmt('Pokemon', v).split('\n'), old_fmt('Pokemon', v).split('\n')
                both = f"{v['energy_type']}/{v['secondary_energy_type']}"
                self.assertEqual(text[0], old[0].replace(f"]  {v['energy_type']}  Stage", f"]  {both}  Stage", 1))
                self.assertIn(both, text[0])
                self.assertEqual(text[1:], old[1:])

    def test_dual_type_shows_both_types_and_one_weakness(self):
        single = card.fmt('Pokemon', real('A1 001')).split('\n')
        self.assertTrue(single[0].startswith('Bulbasaur  [A1 001]  Grass  Stage 0'), single[0])
        for shape in SHAPES:
            with self.subTest(shape=shape):
                text = card.fmt('Pokemon', dual('A1 001', 'Grass', 'Psychic', shape)).split('\n')
                self.assertTrue(text[0].startswith('Bulbasaur  [A1 001]  Grass/Psychic  Stage 0'), text[0])
                self.assertIn('  weak Fire  ', text[0])
                self.assertEqual(text[1:], single[1:])

    def test_printings_differing_only_in_a_second_type_never_merge(self):
        # card.py's main keeps one line per distinct fmt text (ids replaced by '?')
        a = card.fmt('Pokemon', {**real('A1 001'), 'id': '?'})
        b = card.fmt('Pokemon', {**dual('A1 001', 'Grass', 'Psychic'), 'id': '?'})
        self.assertNotEqual(a, b)

    def test_malformed_refused(self):
        with self.assertRaises(ValueError):
            card.fmt('Pokemon', dict(real('A1 001'), weakness=['Fire', 'Water']))


# ---------------------------------------------------------------------------------------------
# lib/card_canon.py: the fingerprint
# ---------------------------------------------------------------------------------------------

def fp(v):
    return card_canon.fingerprint({'Pokemon': v})


class CardCanon(unittest.TestCase):

    def test_every_real_fingerprint_is_byte_for_byte_the_old_one(self):
        for kind, v in SINGLE:
            self.assertEqual(card_canon.fingerprint({kind: v}), old_fingerprint({kind: v}), v['id'])

    def test_a_real_dual_type_card_never_merges_with_its_first_type(self):
        # main's formula hashed energy_type only: it would read Mega Greninja ex as plain Water
        for v in REAL_DUAL:
            with self.subTest(id=v['id']):
                self.assertNotEqual(fp(v), old_fingerprint({'Pokemon': v}))

    def test_refresh_pins_unchanged(self):
        self.assertEqual(card_canon.EXPECTED_IDS, 4577)
        self.assertEqual(card_canon.SET_ORDER, ['A1', 'A1a', 'A2', 'A2a', 'A2b', 'A3', 'A3a', 'A3b', 'A4',
                                                'A4a', 'A4b', 'B1', 'B1a', 'B2', 'B2a', 'B2b', 'B3', 'B3a',
                                                'B3b', 'B4', 'B4a', 'B4b', 'C1', 'P-A', 'P-B', 'P-C', 'SP1'])

    def test_a_second_type_never_merges(self):
        base = fp(real('A1 001'))
        grass_psychic = fp(dual('A1 001', 'Grass', 'Psychic'))
        grass_darkness = fp(dual('A1 001', 'Grass', 'Darkness'))
        psychic_grass = fp(dual('A1 001', 'Psychic', 'Grass'))
        self.assertEqual(len({base, grass_psychic, grass_darkness, psychic_grass}), 4)
        # main's formula hashed energy_type only: it merged Grass/Psychic into plain Grass
        self.assertEqual(old_fingerprint({'Pokemon': dual('A1 001', 'Grass', 'Psychic')}), base)

    def test_one_dual_type_card_is_one_fingerprint_in_any_shape(self):
        self.assertEqual(len({fp(dual('A1 001', 'Grass', 'Psychic', s)) for s in SHAPES}), 1)

    def test_the_weakness_is_in_the_fingerprint(self):
        a = fp(dual('A1 001', 'Psychic', 'Fighting', weakness='Darkness'))
        b = fp(dual('A1 001', 'Psychic', 'Fighting', weakness='Metal'))
        self.assertNotEqual(a, b)
        with self.assertRaises(ValueError):
            fp(dual('A1 001', 'Psychic', 'Fighting', weakness=['Darkness']))

    def test_map_rows_match_when_built_from_this_database(self):
        try:
            cn = card_canon.Canon()
        except SystemExit as e:
            self.skipTest(f'no usable CANON_MAP.tsv: {e}')
        sha = hashlib.sha256(io.open(db_path(), 'rb').read()).hexdigest()
        if sha != cn.source_sha256:
            self.skipTest('CANON_MAP.tsv was built from another database file')
        for kind, v in DB:
            self.assertEqual(card_canon.fingerprint({kind: v}), cn.canon(v['id']), v['id'])

    def test_selftest_passes(self):
        try:
            card_canon.Canon()
        except SystemExit as e:
            self.skipTest(f'no usable CANON_MAP.tsv: {e}')
        out = io.StringIO()                        # its report prints emoji: keep it off a narrow console
        with contextlib.redirect_stdout(out):
            ok = card_canon.selftest()
        self.assertTrue(ok, out.getvalue())


# ---------------------------------------------------------------------------------------------
# lib/consistency.py: refuses where it reads a type
# ---------------------------------------------------------------------------------------------

class Consistency(unittest.TestCase):

    def test_every_real_card_reads_as_on_main(self):
        for kind, v in SINGLE:
            c = consistency.Card(kind, v)
            self.assertEqual(c.etype, v.get('energy_type'), v['id'])     # main: v.get('energy_type')
            self.assertEqual(c.etypes, (v['energy_type'],) if kind == 'Pokemon' else (), v['id'])

    def test_a_real_dual_type_card_loads_but_its_type_is_refused(self):
        for v in REAL_DUAL:
            with self.subTest(id=v['id']):
                c = consistency.Card('Pokemon', v)
                self.assertEqual(c.etypes, (v['energy_type'], v['secondary_energy_type']))
                with self.assertRaises(card.DualTypeUnsupported):
                    _ = c.etype

    def test_a_dual_type_card_loads_but_its_type_is_refused(self):
        c = consistency.Card('Pokemon', dual('A1 001', 'Psychic', 'Grass'))
        self.assertEqual(c.etypes, ('Psychic', 'Grass'))
        with self.assertRaises(card.DualTypeUnsupported) as cm:
            _ = c.etype
        for part in ('Bulbasaur [A1 001]', 'Psychic/Grass', 'lib/consistency.py'):
            self.assertIn(part, str(cm.exception))

    def test_malformed_card_refused_at_load(self):
        with self.assertRaises(ValueError):
            consistency.Card('Pokemon', dict(real('A1 001'), energy_type=[]))

    def forest_filter(self):
        effs, _ = consistency.classify(consistency.resolve('B3 153'))      # Fragrant Forest
        f = [e for e in effs if e['kind'] == 'search_stadium'][0]['filter']
        self.assertEqual((f['basic'], f['etype']), (True, 'Grass'))
        return f

    def test_fmatch_typed_search(self):
        f = self.forest_filter()
        self.assertTrue(consistency.fmatch(f, consistency.resolve('A1 005')))     # Caterpie, Grass Basic
        self.assertFalse(consistency.fmatch(f, consistency.resolve('A1 033')))    # Charmander, Fire Basic
        # main: Psychic/Grass was silently left out (only its SECOND type is Grass), Grass/Psychic
        # silently read as Grass only
        for p, s in (('Psychic', 'Grass'), ('Grass', 'Psychic')):
            for shape in SHAPES:
                with self.subTest(types=(p, s), shape=shape):
                    with self.assertRaises(card.DualTypeUnsupported):
                        consistency.fmatch(f, consistency.Card('Pokemon', dual('A1 005', p, s, shape)))

    def test_fmatch_untyped_search_needs_no_rule(self):
        f = {'basic': True, 'hp_max': None, 'etype': None, 'names': None}       # "Basic Pokémon"
        self.assertTrue(consistency.fmatch(f, consistency.Card('Pokemon', dual('A1 005', 'Psychic', 'Grass'))))

    def solo_turn_one(self, sixth):
        """Own turn 1 (going first) of the solitaire model on a Grass list whose opening hand is
        Bulbasaur, Fragrant Forest and 3 Potions, with `sixth` on top of the deck under the draw."""
        R = consistency.resolve
        potion = R('P-A 001')
        cards = [R('A1 001'), R('B3 153'), potion, potion, potion, sixth] + [potion] * 14
        g = consistency.Solo(consistency.Plan('synthetic list', ['Grass'], cards), FixedRng(), True)
        g.turn(1)
        return g

    def test_fragrant_forest_in_the_solitaire_model(self):
        g = self.solo_turn_one(consistency.resolve('A1 005'))                     # control: Grass Basic found
        self.assertEqual(g.inplay(), {'Bulbasaur', 'Caterpie'})
        g = self.solo_turn_one(consistency.resolve('A1 033'))                     # control: Fire Basic not found
        self.assertEqual(g.inplay(), {'Bulbasaur'})
        self.assertIn(consistency.resolve('A1 033'), g.deck)
        with self.assertRaises(card.DualTypeUnsupported):                         # main: silently not found
            self.solo_turn_one(consistency.Card('Pokemon', dual('A1 005', 'Psychic', 'Grass')))


# ---------------------------------------------------------------------------------------------
# lib/brew_consistency.py: refuses at the Fragrant Forest search
# ---------------------------------------------------------------------------------------------

class BrewConsistency(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = brew_consistency.load_db()

    def forest_turn_one(self, sixth):
        """Own turn 1 (going first) of the brew model on a Grass list whose opening hand is
        Bulbasaur, Fragrant Forest and 3 Potions; the draw takes a Potion, so `sixth` is on top
        of the deck when Fragrant Forest searches."""
        db = self.db
        potion = db['P-A 001']
        cards = [db['A1 001'], db['B3 153'], potion, potion, potion, potion, sixth] + [potion] * 13
        return brew_consistency.Solitaire(['Grass'], cards, [], FixedRng()).play(True, turns=1)

    def test_fragrant_forest_search(self):
        db = self.db
        self.assertIn('Caterpie', self.forest_turn_one(db['A1 005'])['seen'][0])        # control: found
        self.assertNotIn('Charmander', self.forest_turn_one(db['A1 033'])['seen'][0])   # control: not found
        # main: Psychic/Grass silently not found (only its SECOND type is Grass), Grass/Psychic
        # silently found as a Grass Basic
        for p, s in (('Psychic', 'Grass'), ('Grass', 'Psychic')):
            for shape in SHAPES:
                with self.subTest(types=(p, s), shape=shape):
                    with self.assertRaises(card.DualTypeUnsupported) as cm:
                        self.forest_turn_one(dict(dual('A1 005', p, s, shape), kind='Pokemon'))
                    self.assertIn('Fragrant Forest', str(cm.exception))

    def test_parse_list_reads_every_database_id(self):
        # the Dual Fusion refresh added the first ids whose number has a minus sign (SP1's three
        # Mew, 'SP1 -03'..'SP1 -01'): main's parser refused them as 'unresolved card line'
        fd, path = tempfile.mkstemp(suffix='.txt')
        os.close(fd)
        self.addCleanup(os.remove, path)
        ids = sorted(self.db)
        with io.open(path, 'w', encoding='utf-8') as f:
            f.write('Energy: Psychic\n')
            f.writelines(f"1 {self.db[i]['name']} {i}\n" for i in ids)
            f.write('2 Mew SP1 -1\n1 Bulbasaur A1 1\n')                  # unpadded numbers re-pad
        energy, cards = brew_consistency.parse_list(path, self.db)
        self.assertEqual(energy, ['Psychic'])
        self.assertIn('SP1 -01', ids)
        self.assertEqual([c['id'] for c in cards], ids + ['SP1 -01', 'SP1 -01', 'A1 001'])


# ---------------------------------------------------------------------------------------------
# lib/deck_classifier.py: refuses at suggest_for_deck's same-type rule
# ---------------------------------------------------------------------------------------------

class DeckClassifier(unittest.TestCase):

    def load(self, entries):
        """deck_classifier.load_cards on these database entries (written as ASCII JSON, since
        load_cards opens the file with the platform's default encoding)."""
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        self.addCleanup(os.remove, path)
        with io.open(path, 'w', encoding='ascii') as f:
            json.dump(entries, f, ensure_ascii=True)
        return deck_classifier.load_cards(path)

    def test_every_real_card_reads_as_on_main(self):
        cards = self.load([{k: v} for k, v in DB])
        n = 0
        for kind, v in SINGLE:
            rec = cards[v['id']]
            if kind == 'Pokemon':
                self.assertEqual(rec['energy_type'], v['energy_type'], v['id'])
                self.assertEqual(deck_classifier.pokemon_type(rec), v['energy_type'], v['id'])
                n += 1
            else:
                self.assertNotIn('energy_type', rec)
        self.assertGreater(n, 3000)
        for v in REAL_DUAL:                             # loaded with both types, no single one
            with self.subTest(id=v['id']):
                rec = cards[v['id']]
                self.assertEqual(rec['energy_types'], [v['energy_type'], v['secondary_energy_type']])
                self.assertNotIn('energy_type', rec)
                with self.assertRaises(card.DualTypeUnsupported):
                    deck_classifier.pokemon_type(rec)

    def test_a_dual_type_card_loads_without_a_single_type(self):
        cards = self.load([{'Pokemon': dual('A1 001', 'Psychic', 'Grass', id='ZZ 002')}])
        rec = cards['ZZ 002']
        self.assertEqual(rec['energy_types'], ['Psychic', 'Grass'])
        self.assertNotIn('energy_type', rec)
        p = deck_classifier.deck_profile({'energy': ['Psychic'], 'cards': {'ZZ 002': 2}}, cards, {})
        self.assertEqual(p['n_pk'], 2)                                          # no type read, no refusal

    def test_malformed_card_refused_at_load(self):
        with self.assertRaises(ValueError):
            self.load([{'Pokemon': dict(real('A1 001'), energy_type=[])}])

    def suggest(self, types):
        """suggest_for_deck for a Grass deck of 2 Bulbasaur (marked HEAL) whose one candidate
        complement is a Pokémon (marked DMG_REDUCE) printed with `types`."""
        cand = real('A1 001')
        cand.update(id='ZZ 002', name='Synthetic Wall')
        if len(types) == 1:
            cand['energy_type'] = types[0]
        else:
            cand['energy_type'], cand['secondary_energy_type'] = types
        cards = self.load([{'Pokemon': real('A1 001')}, {'Pokemon': cand}])
        cards['A1 001']['families'] = {'HEAL'}
        cards['ZZ 002']['families'] = {'DMG_REDUCE'}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = deck_classifier.suggest_for_deck({'energy': ['Grass'], 'cards': {'A1 001': 2}}, cards)
        return [(f, g, hits) for f, g, _, hits in out], buf.getvalue()

    def test_suggest_for_deck_same_type_rule(self):
        want = [('HEAL', 'DMG_REDUCE', ['Synthetic Wall ZZ 002'])]
        self.assertEqual(self.suggest(['Grass']), (want, ''))                   # control: same type
        self.assertEqual(self.suggest(['Colorless']), (want, ''))               # control: Colorless
        self.assertEqual(self.suggest(['Fire']), ([], ''))                      # control: other type
        # main: Psychic/Grass silently not suggested (only its SECOND type is Grass), Grass/Psychic
        # silently suggested as Grass. Now: left out of the suggestions, and a printed line says so.
        for types in (['Psychic', 'Grass'], ['Grass', 'Psychic']):
            with self.subTest(types=types):
                out, printed = self.suggest(types)
                self.assertEqual(out, [])
                self.assertIn('1 dual-type candidates left out until the dual-type rules are settled', printed)
                self.assertIn('ZZ 002', printed)

    def test_pokemon_type_still_refuses_a_dual_type_card(self):
        cards = self.load([{'Pokemon': dual('A1 001', 'Psychic', 'Grass', id='ZZ 002')}])
        with self.assertRaises(card.DualTypeUnsupported) as cm:
            deck_classifier.pokemon_type(cards['ZZ 002'])
        self.assertIn('suggest_for_deck', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
