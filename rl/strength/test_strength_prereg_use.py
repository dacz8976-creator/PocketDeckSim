#!/usr/bin/env python3
"""Tests for the `use` stage and the additions to strength_prereg.py that the slow report needs.

  cd rl/strength && python3 -B -m unittest -v test_strength_prereg_use

What is pinned here:
  * the `use` stage: only for the slow report (the config must carry its `slow_report` block), allowed on any deck, recorded as `use`, never development
    evidence; the `dev` and `heldout` stages behave exactly as before (a development run still refuses a held-out deck, by name and by what the file says;
    a held-out run still needs the lock lifted);
  * the held-out content guard compares the CARDS of a deck file (set and number, counts merged), not its bytes and not its Energy line, so a re-exported copy
    (CRLF, a missing final newline, a BOM, a different line order, split counts, odd white space, another Energy line or none) is still recognised; a deck file the
    guard cannot read is a clean REFUSED with the deck's name, never a traceback;
  * the registration is complete only when manifest.sha256 exists: it is written last, after PREREGISTRATION.md;
  * `deck_files`: a deck given by file path (name = file stem), really inside the repository (symlinks are followed), hashed like a registered deck;
  * `selfcheck_given`: a pinned program's self-check text recorded instead of playing the 12 games, only when the program's sha256 was verified, and
    described truthfully (copied from the pin, or replayed by the wrapper);
  * `slow_report`: a free block recorded in the manifest and named in PREREGISTRATION.md, whose resume command replaces the bare program command.

Every harness directory, repository and run directory here is built in a temporary folder with synthetic decks; no real run is read or written.
"""
import errno, gc, hashlib, json, os, re, shutil, stat, subprocess, sys, tempfile, unittest, warnings

HERE = os.path.dirname(os.path.abspath(__file__))
PREREG = os.path.join(HERE, 'strength_prereg.py')
sys.path.insert(0, HERE)
import strength_prereg as P  # noqa: E402  (deck_signature, called directly by DeckSignature)


def write(path, text, binary=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if binary:
        with open(path, 'wb') as f:
            f.write(text)
    else:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(text)


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def card_id(tag):
    """A card id of the form `X1 NNN` that is different for every tag: the held-out guard compares cards by id (the engine ignores printed names)."""
    return f"X1 {int(hashlib.md5(tag.encode()).hexdigest()[:6], 16) % 800 + 100:03d}"


def deck_text(tag):
    return f"Energy: Fire\n2 Card{tag} {card_id(tag)}\n1 Poké Ball P-A 005\n17 Filler X1 002\n"


# Rust's char::is_whitespace (Unicode White_Space), which the engine cuts a line into words on: all of it but the line feed, which ends a line
WHITE_SPACE = ['\t', '\x0b', '\x0c', '\r', ' ', '\x85', '\xa0', ' '] + [chr(c) for c in range(0x2000, 0x200b)] + [' ', ' ', ' ', ' ', '　']
# what Python's str.split() and str.splitlines() would treat as white space or a line end and Rust's White_Space does not: part of a word to the engine
NOT_WHITE_SPACE = ['\x1c', '\x1d', '\x1e', '\x1f', '​', '﻿']
# characters a line-splitting reader (str.splitlines, a universal-newline text file) would take for the end of a line; the engine ends a line at a line feed only
ODD_LINE_ENDS = (('form-feed', '\x0c'), ('vertical-tab', '\x0b'), ('next-line', '\x85'), ('line-separator', ' '), ('paragraph-separator', ' '), ('lone-carriage-return', '\r'))
ODD_SEPARATORS = (('no-break-space', '\xa0'), ('ideographic-space', '　'), ('em-space', ' '), ('form-feed', '\x0c'), ('vertical-tab', '\x0b'), ('next-line', '\x85'),
                  ('line-separator', ' '), ('paragraph-separator', ' '))


def odd_white_space_in_names(ch):
    return lambda t: t.replace('Poké Ball', f'Poké{ch}Ball').replace('Filler', f'Fil{ch}ler').encode()


def odd_white_space_between_words(ch):
    return lambda t: t.replace(' ', ch).encode()


class World(unittest.TestCase):
    """Base class: a temporary harness folder (a copy of strength_prereg.py beside synthetic registry files) and a repository with the decks."""

    def make(self, locked=True):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.harness = os.path.join(self.tmp, 'harness')
        self.repo = os.path.join(self.tmp, 'repo')
        self.out = os.path.join(self.tmp, 'run')
        os.makedirs(self.harness)
        shutil.copy(PREREG, os.path.join(self.harness, 'strength_prereg.py'))
        decks = {'a-deck': 'decks/a.txt', 'held-1': 'decks/held1.txt', 'held-2': 'decks/held2.txt', 't-1': 'decks/t1.txt', 't-2': 'decks/t2.txt'}
        write(os.path.join(self.harness, 'decks.json'), json.dumps({'decks': decks}))
        write(os.path.join(self.harness, 'groups.json'), json.dumps({'panel': ['t-1', 't-2']}))
        write(os.path.join(self.harness, 'heldout.json'), json.dumps({'locked': locked, 'unlocked_by': None if locked else 'test', 'decks': ['held-1', 'held-2']}))
        for n, p in decks.items():
            write(os.path.join(self.repo, p), deck_text(n))
        return self

    def setUp(self):
        self.make()

    def config(self, **kw):
        cfg = dict(name='t', question='q', pilot='kx3', reference='km3', decks=['a-deck'], opponent_groups=['panel'], deals=2, seats=[0, 1], seed_base=24_600_000_000)
        cfg.update(kw)
        return cfg

    def use_config(self, **kw):
        kw.setdefault('slow_report', dict(version=1, headline='kx3 (d513e37b) on a-deck v km3 on the public panel',
                                          pin=dict(path='rl/strength/slow_report_pin.json', sha256='e' * 64)))
        return self.config(stage='use', **kw)

    def prereg(self, cfg):
        cpath = os.path.join(self.tmp, 'config.json')
        write(cpath, json.dumps(cfg))
        return subprocess.run([sys.executable, '-B', os.path.join(self.harness, 'strength_prereg.py'), '--config', cpath, '--out', self.out, '--repo', self.repo],
                              capture_output=True, text=True)

    def manifest(self):
        return json.loads(read(os.path.join(self.out, 'manifest.json')))

    def no_manifest(self):
        return not os.path.exists(os.path.join(self.out, 'manifest.json'))


class DevAndHeldoutStagesUnchanged(World):
    def test_dev_refuses_a_held_out_deck_by_name(self):
        r = self.prereg(self.config(decks=['held-1']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('REFUSED', r.stderr)
        self.assertTrue(self.no_manifest())

    def test_dev_refuses_a_held_out_deck_on_the_opponent_side(self):
        r = self.prereg(self.config(opponent_groups=[], opponents=['held-2']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('REFUSED', r.stderr)

    def test_dev_refuses_a_renamed_byte_copy_of_a_held_out_deck(self):
        write(os.path.join(self.repo, 'decks', 'copy.txt'), deck_text('held-1'))
        r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('REFUSED', r.stderr)

    def test_heldout_stage_refused_while_locked(self):
        r = self.prereg(self.config(decks=['held-1'], stage='heldout'))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('REFUSED', r.stderr)

    def test_heldout_stage_allowed_when_unlocked_and_the_program_still_sees_the_names(self):
        self.make(locked=False)
        r = self.prereg(self.config(decks=['held-1'], stage='heldout'))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['stage'], 'heldout')
        self.assertEqual(m['heldout_decks'], ['held-1', 'held-2'])
        self.assertFalse(m['heldout_locked'])

    def test_an_unknown_stage_is_refused(self):
        for stage in ('exam', 'Use', ''):
            r = self.prereg(self.config(stage=stage))
            self.assertNotEqual(r.returncode, 0, stage)
            self.assertIn('stage', r.stderr)
            self.assertTrue(self.no_manifest())

    def test_dev_manifest_still_carries_the_held_out_names_for_the_program(self):
        r = self.prereg(self.config())
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['stage'], 'dev')
        self.assertEqual(m['heldout_decks'], ['held-1', 'held-2'])
        self.assertTrue(m['heldout_locked'])


class ContentGuard(World):
    """A re-exported copy of a held-out deck is still that deck: the guard compares cards, not bytes."""

    VARIANTS = {
        'crlf': lambda t: t.replace('\n', '\r\n').encode(),
        'no-final-newline': lambda t: t.rstrip('\n').encode(),
        'extra-final-newlines': lambda t: (t + '\n\n').encode(),
        'bom': lambda t: b'\xef\xbb\xbf' + t.encode(),
        'reordered': lambda t: ('\n'.join(reversed(t.strip().split('\n'))) + '\n').encode(),
        'extra-spaces': lambda t: t.replace(' ', '   ').encode(),
        'split-counts': lambda t: t.replace(f'2 Cardheld-1 {card_id("held-1")}\n', f'1 Cardheld-1 {card_id("held-1")}\n1 Cardheld-1 {card_id("held-1")}\n').encode(),
        # the engine reads set and number, never the printed name, and pads the number to three digits
        'accent-folded-names': lambda t: t.replace('Poké', 'Poke').encode(),
        'respelled-names': lambda t: t.replace('Cardheld-1', 'Totally Different Name').replace('Filler', 'filler').encode(),
        'curly-apostrophe-and-case': lambda t: t.replace('Poké Ball', 'POKÉ BALL’S').encode(),
        'energy-without-a-space': lambda t: t.replace('Energy: Fire', 'Energy:Fire').encode(),
        'energy-padded': lambda t: t.replace('Energy: Fire', 'Energy:   Fire  ').encode(),
        'heading-lines': lambda t: ('Pokémon: 3\n' + t.replace('1 Poké Ball', 'Trainer: 1\n1 Poké Ball')).encode(),
        'unpadded-number': lambda t: t.replace('X1 002', 'X1 2').replace('P-A 005', 'P-A 5').encode(),
        'tabs': lambda t: t.replace(' ', '\t').encode(),
        'set-codes-in-lower-case': lambda t: t.replace('X1 ', 'x1 ').replace('P-A ', 'p-a ').encode(),
        'energy-in-lower-case': lambda t: t.replace('Energy: Fire', 'Energy: fire').encode(),
        # the Energy line is not part of what is compared (with none, the engine derives the Energy types from the cards): the same cards are the same deck
        'energy-line-removed': lambda t: t.replace('Energy: Fire\n', '').encode(),
        'another-energy-type': lambda t: t.replace('Energy: Fire', 'Energy: Water').encode(),
        'more-energy-types': lambda t: t.replace('Energy: Fire', 'Energy: Fire, Water, Grass').encode(),
        'energy-line-with-no-type': lambda t: t.replace('Energy: Fire', 'Energy:').encode(),
        'a-second-energy-line': lambda t: (t + 'Energy: Metal\n').encode(),
        'a-card-with-no-printed-name': lambda t: t.replace('1 Poké Ball P-A 005', '1 P-A 005').encode(),
    }
    # a line ends at a line feed only, and a word ends at any Unicode White_Space: neither a form feed, a vertical tab, NEL, U+2028, U+2029 nor a lone carriage return in
    # a printed name cuts the line, and any of them (or a no-break or ideographic space) between the words is a space
    VARIANTS.update({f'{label}-in-a-name': odd_white_space_in_names(ch) for label, ch in ODD_LINE_ENDS})
    VARIANTS.update({f'{label}-between-the-words': odd_white_space_between_words(ch) for label, ch in ODD_SEPARATORS})

    def test_every_variant_of_a_held_out_deck_is_refused_in_a_dev_run(self):
        for name, make in self.VARIANTS.items():
            with self.subTest(variant=name):
                write(os.path.join(self.repo, 'decks', 'copy.txt'), make(deck_text('held-1')), binary=True)
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt']))
                self.assertNotEqual(r.returncode, 0, name)
                self.assertIn('REFUSED', r.stderr)

    def test_every_variant_is_recorded_as_held_out_in_a_use_run(self):
        for name, make in self.VARIANTS.items():
            with self.subTest(variant=name):
                write(os.path.join(self.repo, 'decks', 'copy.txt'), make(deck_text('held-1')), binary=True)
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.use_config(decks=[], deck_files=['decks/copy.txt']))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(self.manifest()['heldout_in_run'], ['copy'])

    def test_a_different_deck_is_not_mistaken_for_a_held_out_one(self):
        write(os.path.join(self.repo, 'decks', 'other.txt'), deck_text('something-else'))
        r = self.prereg(self.config(decks=[], deck_files=['decks/other.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_one_card_or_a_count_changed_is_a_different_deck(self):
        base = deck_text('held-1')
        changed = {'another card id': base.replace('X1 002', 'X1 003'), 'another count': base.replace('17 Filler', '16 Filler'), 'another set': base.replace('X1 002', 'X2 002'),
                   'another number': base.replace('P-A 005', 'P-A 006'), 'one card more': base + '1 Extra Z9 001\n', 'one card less': base.replace('1 Poké Ball P-A 005\n', ''),
                   'a count moved from one card to another': base.replace('1 Poké Ball', '2 Poké Ball').replace('17 Filler', '16 Filler'),
                   'a card line said twice (the counts add up)': base + '1 Poké Ball P-A 005\n'}
        for name, text in changed.items():
            with self.subTest(change=name):
                self.assertNotEqual(text, base)
                write(os.path.join(self.repo, 'decks', 'other.txt'), text)
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(decks=[], deck_files=['decks/other.txt']))
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_different_deck_that_has_the_same_energy_line_is_still_a_different_deck(self):
        """The Energy line is left out of the comparison; it must not be the only thing left out: the same line over other cards is not the held-out deck."""
        for how, line in {'the same Energy line': 'Energy: Fire\n', 'no Energy line': ''}.items():
            with self.subTest(energy=how):
                write(os.path.join(self.repo, 'decks', 'other.txt'), line + deck_text('something-else').replace('Energy: Fire\n', ''))
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(decks=[], deck_files=['decks/other.txt']))
                self.assertEqual(r.returncode, 0, r.stderr)

    ENERGY_LINES = {'Fire': 'Energy: Fire\n', 'both types': 'Energy: Fire, Water\n', 'the types the other way round, with no spaces': 'Energy:Water,Fire\n',
                    'a third type': 'Energy: Grass\n', 'a line with no type': 'Energy:\n', 'no Energy line': ''}

    def test_the_energy_line_does_not_matter_on_either_side(self):
        """With no Energy line the engine derives the Energy types from the cards, so the same cards are the same deck whatever the registered file says and whatever
        the copy says: a copy that differs only in its Energy line, or has none, is refused as a copy."""
        cards = deck_text('held-1').replace('Energy: Fire\n', '')
        for registered_how, registered in self.ENERGY_LINES.items():
            for copy_how, copy in self.ENERGY_LINES.items():
                with self.subTest(registered=registered_how, copy=copy_how):
                    write(os.path.join(self.repo, 'decks', 'held1.txt'), registered + cards)
                    write(os.path.join(self.repo, 'decks', 'copy.txt'), copy + cards)
                    shutil.rmtree(self.out, ignore_errors=True)
                    r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt']))
                    self.assertNotEqual(r.returncode, 0)
                    self.assertIn('copy is a held-out deck', r.stderr)
                    self.assertTrue(self.no_manifest())

    STAGE_VARIANTS = ('crlf', 'bom', 'reordered', 'split-counts', 'energy-line-removed', 'another-energy-type', 'form-feed-in-a-name', 'no-break-space-between-the-words')

    def test_a_copy_is_refused_in_a_locked_held_out_run_and_recorded_in_an_unlocked_one(self):
        """The same copies through the held-out stage: while heldout.json is locked a copy is refused by what it says; once the lock is lifted the run is allowed and the
        copy is listed as the held-out deck it is, next to the names the program's own guard reads."""
        for name in self.STAGE_VARIANTS:
            with self.subTest(locked=True, variant=name):
                write(os.path.join(self.repo, 'decks', 'copy.txt'), self.VARIANTS[name](deck_text('held-1')), binary=True)
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt'], stage='heldout'))
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('copy is a held-out deck', r.stderr)
                self.assertTrue(self.no_manifest())
        self.make(locked=False)
        for name in self.STAGE_VARIANTS:
            with self.subTest(locked=False, variant=name):
                write(os.path.join(self.repo, 'decks', 'copy.txt'), self.VARIANTS[name](deck_text('held-1')), binary=True)
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt'], stage='heldout'))
                self.assertEqual(r.returncode, 0, r.stderr)
                m = self.manifest()
                self.assertEqual((m['stage'], m['heldout_in_run'], m['heldout_decks']), ('heldout', ['copy'], ['held-1', 'held-2']))

    def test_a_copy_without_an_energy_line_is_recorded_not_refused_in_a_use_run(self):
        """A use run lists no held-out names for the program's own guard and keeps them under heldout_registry and heldout_in_run; the copy is one of them."""
        write(os.path.join(self.repo, 'decks', 'copy.txt'), self.VARIANTS['energy-line-removed'](deck_text('held-2')), binary=True)
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/copy.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual((m['heldout_decks'], m['heldout_registry'], m['heldout_in_run']), ([], ['held-1', 'held-2'], ['copy']))

    def test_the_raw_file_sha256_is_still_what_the_manifest_records(self):
        write(os.path.join(self.repo, 'decks', 'copy.txt'), self.VARIANTS['crlf'](deck_text('x')), binary=True)
        r = self.prereg(self.config(decks=[], deck_files=['decks/copy.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.manifest()['decks'][0]['sha256'], sha(os.path.join(self.repo, 'decks', 'copy.txt')))

    def test_a_held_out_deck_in_both_roles_is_listed_once(self):
        r = self.prereg(self.use_config(decks=['held-1'], opponent_groups=[], opponents=['held-1', 't-1']))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.manifest()['heldout_in_run'], ['held-1'])


class UseStage(World):
    def test_use_accepts_any_deck_including_a_held_out_one(self):
        r = self.prereg(self.use_config(decks=['held-1']))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['stage'], 'use')
        self.assertEqual([d['name'] for d in m['decks']], ['held-1'])

    def test_use_is_only_for_the_slow_report(self):
        for cfg in (self.config(stage='use'), self.config(stage='use', slow_report={}), self.config(stage='use', slow_report=dict(version=1)),
                    self.config(stage='use', slow_report=dict(version=1, headline='h'))):
            r = self.prereg(cfg)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('slow report', r.stderr)
            self.assertTrue(self.no_manifest())

    def test_use_manifest_lets_the_frozen_program_run_and_keeps_the_audit_trail(self):
        """The frozen program refuses any name in `heldout_decks` unless stage is heldout and the lock is off, so a use run lists none there; the held-out
        names and the held-out decks this run uses are recorded under other keys, and the lock file is not touched."""
        before = read(os.path.join(self.harness, 'heldout.json'))
        r = self.prereg(self.use_config(decks=['held-1']))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['heldout_decks'], [])
        self.assertEqual(m['heldout_registry'], ['held-1', 'held-2'])
        self.assertEqual(m['heldout_in_run'], ['held-1'])
        self.assertTrue(m['heldout_locked'], 'the lock stays on; a use run does not lift it')
        self.assertEqual(read(os.path.join(self.harness, 'heldout.json')), before)

    def test_use_without_a_held_out_deck_records_none_in_run(self):
        r = self.prereg(self.use_config())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.manifest()['heldout_in_run'], [])

    def test_preregistration_says_use_is_not_development_evidence(self):
        r = self.prereg(self.use_config(decks=['held-1']))
        self.assertEqual(r.returncode, 0, r.stderr)
        text = read(os.path.join(self.out, 'PREREGISTRATION.md'))
        self.assertIn('Stage `use`', text)
        self.assertIn('not development evidence', text)
        self.assertIn('held-1', text.split('## Held-out decks')[1].split('##')[0])

    def test_dev_preregistration_text_has_no_use_paragraph(self):
        self.prereg(self.config())
        self.assertNotIn('not development evidence', read(os.path.join(self.out, 'PREREGISTRATION.md')))


class DeckFiles(World):
    def test_a_deck_file_is_registered_by_stem_and_hashed(self):
        write(os.path.join(self.repo, 'decks', 'events', 'new-list.txt'), deck_text('new'))
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/events/new-list.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['decks'], [dict(name='new-list', path='decks/events/new-list.txt', sha256=sha(os.path.join(self.repo, 'decks', 'events', 'new-list.txt')))])
        self.assertEqual(m['deck_files'], [dict(name='new-list', path='decks/events/new-list.txt')])
        self.assertEqual(m['planned_pairs'], 2)
        self.assertEqual(m['planned_games'], 2 * 2 * 2 * 2)

    def test_a_deck_file_outside_the_repository_is_refused(self):
        outside = os.path.join(self.tmp, 'elsewhere.txt')
        write(outside, deck_text('x'))
        for p in (outside, '../elsewhere.txt'):
            r = self.prereg(self.use_config(decks=[], deck_files=[p]))
            self.assertNotEqual(r.returncode, 0, p)
            self.assertIn('inside the repository', r.stderr)
            self.assertTrue(self.no_manifest())

    def test_a_symlink_that_leaves_the_repository_is_refused(self):
        outside = os.path.join(self.tmp, 'elsewhere.txt')
        write(outside, deck_text('x'))
        os.symlink(outside, os.path.join(self.repo, 'decks', 'sneaky.txt'))
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/sneaky.txt']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('inside the repository', r.stderr)
        self.assertTrue(self.no_manifest())

    def test_a_symlink_that_stays_inside_the_repository_is_accepted(self):
        os.symlink(os.path.join(self.repo, 'decks', 'a.txt'), os.path.join(self.repo, 'decks', 'alias.txt'))
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/alias.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_missing_deck_file_is_refused(self):
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/nope.txt']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('nope.txt', r.stderr)

    def test_a_directory_is_refused_with_a_clear_message(self):
        os.makedirs(os.path.join(self.repo, 'decks', 'adir'))
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/adir']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('not a file', r.stderr)

    def test_a_stem_that_names_a_different_registered_deck_is_refused(self):
        write(os.path.join(self.repo, 'decks', 'other', 't-1.txt'), deck_text('imposter'))
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/other/t-1.txt']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('t-1', r.stderr)

    def test_the_same_path_as_a_registered_deck_is_accepted_once(self):
        r = self.prereg(self.use_config(decks=['a-deck'], deck_files=['decks/a.txt']))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([d['name'] for d in self.manifest()['decks']], ['a-deck'])


class DealsAgainstStride(World):
    def test_deals_may_equal_the_stride_but_not_exceed_it(self):
        r = self.prereg(self.config(deals=10001, pair_stride=10000))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('pair_stride', r.stderr)
        self.assertFalse(os.path.exists(self.out), 'a refusal must not leave the output directory behind')
        r = self.prereg(self.config(deals=10000, pair_stride=10000))
        self.assertEqual(r.returncode, 0, r.stderr)


class SelfcheckGiven(World):
    def fake_program(self):
        p = os.path.join(self.tmp, 'fake_strength')
        write(p, "#!/usr/bin/env python3\nimport sys, os\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'selfcheck_was_run'), 'a').write(' '.join(sys.argv[1:]) + '\\n')\nprint('selfcheck pilot=' + sys.argv[sys.argv.index('--pilot') + 1] + ' digest=0123456789abcdef')\n")
        os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)
        return p

    PIN_SOURCE = 'given in the config (copied from the pin; the program sha256 is the one named there)'

    def test_given_text_is_recorded_and_the_program_is_not_asked(self):
        p = self.fake_program()
        given = {'km3': 'selfcheck pilot=km3 games=12 digest=aaaa', 'kx3': 'selfcheck pilot=kx3 games=12 digest=bbbb'}
        r = self.prereg(self.config(program=p, program_sha256=sha(p), selfcheck_given=given))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['selfcheck'], given)
        self.assertEqual(m['selfcheck_source'], {'km3': self.PIN_SOURCE, 'kx3': self.PIN_SOURCE})
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'selfcheck_was_run')), 'no self-check game may be played when the text is given')
        text = read(os.path.join(self.out, 'PREREGISTRATION.md'))
        self.assertIn('digest=bbbb', text)
        self.assertIn('given in the config', text)
        self.assertIn('not replayed', text)

    def test_a_replayed_selfcheck_is_described_as_replayed(self):
        p = self.fake_program()
        given = {'km3': 'selfcheck pilot=km3 games=12 digest=aaaa', 'kx3': 'selfcheck pilot=kx3 games=12 digest=bbbb'}
        r = self.prereg(self.config(program=p, program_sha256=sha(p), selfcheck_given=given, selfcheck_how='replayed'))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['selfcheck_source']['kx3'], 'replayed by slow_report.py just before registration (equal to the pin)')
        text = read(os.path.join(self.out, 'PREREGISTRATION.md'))
        self.assertIn('replayed by slow_report.py', text)
        self.assertNotIn('not replayed', text)

    def test_given_text_needs_the_program_sha256(self):
        p = self.fake_program()
        r = self.prereg(self.config(program=p, selfcheck_given={'km3': 'x', 'kx3': 'y'}))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('program_sha256', r.stderr)
        self.assertTrue(self.no_manifest())

    def test_given_text_with_the_wrong_program_sha256_is_refused(self):
        p = self.fake_program()
        r = self.prereg(self.config(program=p, program_sha256='0' * 64, selfcheck_given={'km3': 'x', 'kx3': 'y'}))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('program_sha256', r.stderr)

    def test_given_text_must_be_a_mapping_of_text_to_text(self):
        p = self.fake_program()
        for bad in (['km3'], {'km3': 3}, 'text', {'km3': ['a']}):
            r = self.prereg(self.config(program=p, program_sha256=sha(p), selfcheck_given=bad))
            self.assertNotEqual(r.returncode, 0, repr(bad))
            self.assertIn('selfcheck_given', r.stderr)
            self.assertNotIn('Traceback', r.stderr)

    def registry_with_altaria(self):
        write(os.path.join(self.harness, 'decks.json'), json.dumps({'decks': {'a-deck': 'decks/a.txt', 'held-1': 'decks/held1.txt', 'held-2': 'decks/held2.txt',
                                                                               't-1': 'decks/t1.txt', 't-2': 'decks/t2.txt', 't-altaria': 'decks/t1.txt', 't-suicune': 'decks/t2.txt'}}))

    def test_without_given_text_the_program_is_asked_as_before(self):
        self.registry_with_altaria()
        p = self.fake_program()
        r = self.prereg(self.config(program=p))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertIn('digest=0123456789abcdef', m['selfcheck']['kx3'])
        self.assertEqual(m['selfcheck_source'], {'km3': 'run by strength_prereg.py', 'kx3': 'run by strength_prereg.py'})
        self.assertTrue(os.path.exists(os.path.join(self.tmp, 'selfcheck_was_run')))

    def test_given_text_for_only_one_pilot_runs_the_other(self):
        self.registry_with_altaria()
        p = self.fake_program()
        r = self.prereg(self.config(program=p, program_sha256=sha(p), selfcheck_given={'km3': 'selfcheck pilot=km3 digest=aaaa'}))
        self.assertEqual(r.returncode, 0, r.stderr)
        m = self.manifest()
        self.assertEqual(m['selfcheck']['km3'], 'selfcheck pilot=km3 digest=aaaa')
        self.assertIn('digest=0123456789abcdef', m['selfcheck']['kx3'])
        self.assertEqual(m['selfcheck_source']['kx3'], 'run by strength_prereg.py')
        ran = read(os.path.join(self.tmp, 'selfcheck_was_run'))
        self.assertIn('--pilot kx3', ran)
        self.assertNotIn('--pilot km3', ran)


class SlowReportBlock(World):
    BLOCK = {'version': 1, 'deck_name': 'a-deck', 'paired': True, 'headline': 'kx3 (d513e37b) on a-deck v km3 on the public panel',
             'pin': {'path': 'rl/strength/slow_report_pin.json', 'sha256': 'e' * 64}}

    def test_the_block_is_recorded_and_named_in_the_preregistration(self):
        r = self.prereg(self.use_config(slow_report=self.BLOCK))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.manifest()['slow_report'], self.BLOCK)
        text = read(os.path.join(self.out, 'PREREGISTRATION.md'))
        self.assertIn('## Slow report', text)
        self.assertIn('kx3 (d513e37b) on a-deck v km3 on the public panel', text)

    def test_the_run_block_names_the_wrapper_when_the_block_gives_a_resume_command(self):
        block = dict(self.BLOCK, resume_command='python3 rl/strength/slow_report.py --dir rl/results/slow_reports/2026-10-10_a-deck')
        r = self.prereg(self.use_config(slow_report=block))
        self.assertEqual(r.returncode, 0, r.stderr)
        run = read(os.path.join(self.out, 'PREREGISTRATION.md')).split('## Run')[1]
        self.assertIn('slow_report.py --dir', run)
        self.assertNotIn('strength run --manifest', run, 'a use run is resumed through the wrapper, which scrubs the environment and keeps the school-morning rule')

    def test_a_development_run_still_gets_the_program_command(self):
        self.prereg(self.config())
        self.assertIn('strength run --manifest', read(os.path.join(self.out, 'PREREGISTRATION.md')).split('## Run')[1])

    def test_no_block_no_section(self):
        self.prereg(self.config())
        self.assertNotIn('slow_report', self.manifest())
        self.assertNotIn('## Slow report', read(os.path.join(self.out, 'PREREGISTRATION.md')))


class UseNeedsTheSlowReportBlock(World):
    """Stage `use` switches the held-out guard of the program off, so it is for the slow report only: the config must carry the report's own block, with a headline
    and the pin it was made under. (This is an audit-trail gate, not a barrier: nothing here checks that the pin is the real one.)"""

    PIN = dict(path='rl/strength/slow_report_pin.json', sha256='e' * 64)

    def test_a_block_that_lacks_a_headline_or_a_pin_or_is_not_a_mapping_is_refused_with_a_message(self):
        bad = {'no block at all': None, 'an empty block': {}, 'a pin but no headline': dict(pin=self.PIN), 'a headline but no pin': dict(headline='h'),
               'an empty headline': dict(headline='', pin=self.PIN), 'an empty pin': dict(headline='h', pin=''), 'text instead of a block': 'headline pin',
               'a list instead of a block': ['headline', 'pin'], 'a number instead of a block': 7}
        for how, block in bad.items():
            with self.subTest(block=how):
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(stage='use', slow_report=block))
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('stage `use` is only for the slow report', r.stderr)
                self.assertNotIn('Traceback', r.stderr)
                self.assertFalse(os.path.exists(self.out), 'a refusal leaves no run directory')

    def test_the_other_stages_do_not_need_a_block(self):
        self.assertEqual(self.prereg(self.config()).returncode, 0)
        self.make(locked=False)
        self.assertEqual(self.prereg(self.config(decks=['held-1'], stage='heldout')).returncode, 0)


class HeldoutLockRefusals(World):
    def test_a_locked_heldout_run_with_a_held_out_deck_is_refused_naming_the_deck(self):
        r = self.prereg(self.config(decks=['held-1'], stage='heldout'))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('held-1 is a held-out deck', r.stderr)
        self.assertTrue(self.no_manifest())

    def test_a_locked_heldout_run_is_refused_even_when_no_held_out_deck_is_in_it(self):
        r = self.prereg(self.config(stage='heldout'))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('heldout.json is still locked', r.stderr)
        self.assertTrue(self.no_manifest())

    def test_no_stage_touches_the_lock_file(self):
        path = os.path.join(self.harness, 'heldout.json')
        os.utime(path, ns=(1_000_000_000_000_000_000, 1_000_000_000_000_000_000))  # September 2001: any write would show
        stat0 = os.stat(path)
        before = (read(path), stat0.st_mtime_ns, stat0.st_size)
        for how, cfg in {'development': self.config(), 'a use run on a held-out deck': self.use_config(decks=['held-1']), 'a refused run': self.config(decks=['held-1'])}.items():
            with self.subTest(run=how):
                shutil.rmtree(self.out, ignore_errors=True)
                self.prereg(cfg)
                stat1 = os.stat(path)
                self.assertEqual((read(path), stat1.st_mtime_ns, stat1.st_size), before)


class DeckFilesGivenTwice(World):
    def test_a_deck_file_named_twice_is_registered_once(self):
        write(os.path.join(self.repo, 'decks', 'events', 'new-list.txt'), deck_text('new'))
        for how, files, name in (('a registered deck', ['decks/a.txt', 'decks/a.txt'], 'a-deck'), ('a registered deck by another spelling of its path', ['decks/a.txt', 'decks/./a.txt'], 'a-deck'),
                                 ('a deck that is not registered', ['decks/events/new-list.txt', 'decks/events/new-list.txt'], 'new-list')):
            with self.subTest(deck=how):
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.use_config(decks=[], deck_files=files))
                self.assertEqual(r.returncode, 0, r.stderr)
                m = self.manifest()
                self.assertEqual([d['name'] for d in m['decks']], [name])
                self.assertEqual([d['name'] for d in m['deck_files']], [name], 'listed once among the deck files too')
                self.assertEqual(m['planned_pairs'], 2)


class AnalysisPlan(World):
    """The pre-registration fixes the analysis before any game. A `use` run is reported by the slow report page (Wilson ranges, Student t), so its plan says that;
    development and held-out runs keep the plan of the engineering report."""

    def plan(self, cfg):
        r = self.prereg(cfg)
        self.assertEqual(r.returncode, 0, r.stderr)
        return read(os.path.join(self.out, 'PREREGISTRATION.md')).split('## Analysis plan (fixed now)')[1].split('\n## ')[0]

    def test_a_use_run_fixes_the_wilson_and_student_t_method_the_page_reports(self):
        plan = self.plan(self.use_config())
        for needle in ('win 1, tie 0.5, loss 0', 'Wilson 95% range', 'valid at 0% and 100% and for few games', 'and by who went first', 'Student t 95% interval',
                       'what that range does and does not include', 'it has no pass or fail line', 'REPORT.md', 'is a detail, not the headline'):
            self.assertIn(needle, plan)
        for dev_only in ('weights every deck equally', 'narrow the pooled interval', 'sample sd'):
            self.assertNotIn(dev_only, plan)

    def test_a_development_run_keeps_the_mean_and_standard_deviation_plan(self):
        plan = self.plan(self.config())
        for needle in ('**Paired difference** `d = score(arm X) - score(arm ref)`', '**mean ± 1.96·sd/√n** (sample sd, n = paired games)', 'A second pooled figure weights every deck equally',
                       'how many more deals would narrow the pooled interval to ±3 and ±5 points'):
            self.assertIn(needle, plan)
        for use_only in ('Wilson', 'Student t'):
            self.assertNotIn(use_only, plan)

    def test_a_held_out_run_keeps_the_development_plan(self):
        self.make(locked=False)
        plan = self.plan(self.config(decks=['held-1'], stage='heldout'))
        self.assertIn('mean ± 1.96·sd/√n', plan)
        self.assertNotIn('Wilson', plan)

    def test_both_plans_end_with_the_intended_lines_and_no_threshold(self):
        for how, cfg in (('use', self.use_config()), ('development', self.config())):
            with self.subTest(stage=how):
                shutil.rmtree(self.out, ignore_errors=True)
                plan = self.plan(cfg)
                self.assertIn('Intended-line rates from `rl/strength/intended_lines.json`', plan)
                self.assertIn('No pass/fail threshold is set by this document.', plan)

    BLOCK = dict(version=1, headline='kx3 (d513e37b) on a-deck v km3 on the public panel', pin=dict(path='rl/strength/slow_report_pin.json', sha256='e' * 64))
    BASELINE_ON = ('- The baseline comparison is **on** (the default): the **paired difference** `d = score(arm X) - score(arm ref)` on each (deck, opponent, deal, seat), reported as '
                   'its mean with a **Student t 95% interval** over the paired games (a deal and seat played by both pilots), and what that range does and does not include.')
    BASELINE_OFF = ('- The baseline comparison is **off** (`--no-paired`): the reference still plays the deck on the same deals (about a second a game, it is part of the registered games) '
                    'but the page leaves the paired difference out.')

    def test_a_paired_use_run_fixes_the_baseline_comparison_as_on(self):
        for how, block in (('paired: true', dict(self.BLOCK, paired=True)), ('no paired entry (on is the default)', self.BLOCK)):
            with self.subTest(slow_report=how):
                shutil.rmtree(self.out, ignore_errors=True)
                plan = self.plan(self.use_config(slow_report=block))
                self.assertEqual(plan.count(self.BASELINE_ON), 1)
                for gone in ('**off**', '--no-paired', 'leaves the paired difference out'):
                    self.assertNotIn(gone, plan)

    def test_a_use_run_that_is_not_paired_fixes_the_baseline_comparison_as_off_and_the_student_t_interval_is_not_promised(self):
        plan = self.plan(self.use_config(slow_report=dict(self.BLOCK, paired=False)))
        self.assertEqual(plan.count(self.BASELINE_OFF), 1)
        for gone in ('**on**', 'Student t', 'what that range does and does not include', 'played by both pilots'):
            self.assertNotIn(gone, plan)
        self.assertIn('Wilson 95% range', plan, 'the scores are reported either way')

    def test_the_two_use_plans_differ_in_the_baseline_bullet_alone(self):
        on = self.plan(self.use_config(slow_report=dict(self.BLOCK, paired=True)))
        shutil.rmtree(self.out, ignore_errors=True)
        off = self.plan(self.use_config(slow_report=dict(self.BLOCK, paired=False)))
        self.assertEqual(on.replace(self.BASELINE_ON, self.BASELINE_OFF), off)

    def test_a_development_plan_has_no_baseline_bullet_whatever_a_slow_report_block_says(self):
        for paired in (True, False):
            with self.subTest(paired=paired):
                shutil.rmtree(self.out, ignore_errors=True)
                self.assertNotIn('baseline comparison', self.plan(self.config(slow_report=dict(self.BLOCK, paired=paired))))


class DeckSignature(unittest.TestCase):
    """deck_signature(path) is what both held-out guards (strength_prereg.py's and the slow report's panel check) compare: what the engine reads from a deck file, not how
    it was saved. The engine reads, per card line, the count and the last two words (the set and the number, padded to three digits); the printed name, the letter case, the
    heading lines, the line order and the way the file was saved do not matter. The Energy line does not matter either: with none, the engine derives the Energy types from
    the cards, so the same cards are the same deck for a guard that must refuse near-copies rather than miss them. A line ends at a line feed only; a word ends at any
    Unicode White_Space character (the set Rust's char::is_whitespace uses, as the engine splits a line)."""

    BASE = "Energy: Fire, Water\n2 Torchic B1 033\n1 Poké Ball P-A 005\n1 Pokémon Center Lady A2b 070\n16 Filler X1 002\n"
    CARD = re.compile(r'^(\d+) (.+) (\S+) (\S+)$', re.M)

    SAME = {
        'CRLF line ends': lambda t: t.replace('\n', '\r\n'),
        'a byte order mark': lambda t: b'\xef\xbb\xbf' + t.encode(),
        'no final newline': lambda t: t.rstrip('\n'),
        'blank lines and indentation': lambda t: '\n\n  ' + t.replace('\n', '  \n\n  '),
        'lines in another order': lambda t: '\n'.join(reversed(t.strip().split('\n'))),
        'tabs and extra spaces between the words': lambda t: t.replace(' ', '\t \t'),
        'a count split over two lines': lambda t: t.replace('2 Torchic B1 033\n', '1 Torchic B1 033\n1 Torchic B1 033\n'),
        'a card line with a zero count': lambda t: t + '0 Mew A1 151\n',
        'the printed names respelled': lambda t: DeckSignature.CARD.sub(r'\1 Spelled Differently \3 \4', t),
        'accents folded to ASCII': lambda t: t.replace('é', 'e'),
        'the printed names in capitals': lambda t: DeckSignature.CARD.sub(lambda m: f'{m[1]} {m[2].upper()} {m[3]} {m[4]}', t),
        'set codes in lower case': lambda t: DeckSignature.CARD.sub(lambda m: f'{m[1]} {m[2]} {m[3].lower()} {m[4]}', t),
        'numbers without their leading zeros': lambda t: re.sub(r' 0+(\d)$', r' \1', t, flags=re.M),
        'Pokémon and Trainer heading lines': lambda t: 'Pokémon: 4\n' + t.replace('1 Poké Ball', 'Trainer: 2\n1 Poké Ball'),
        'the Energy line without a space': lambda t: t.replace('Energy: ', 'Energy:'),
        'the Energy types in another order': lambda t: t.replace('Fire, Water', 'Water, Fire'),
        'the Energy types in lower case': lambda t: t.replace('Fire, Water', 'fire, water'),
        'the Energy types with odd spacing': lambda t: t.replace('Fire, Water', ' Water ,Fire , '),
        'an Energy type named twice': lambda t: t.replace('Fire, Water', 'Fire, Water, Fire'),
        # the Energy line is not read at all
        'another Energy type': lambda t: t.replace('Fire, Water', 'Fire, Grass'),
        'one Energy type less': lambda t: t.replace('Fire, Water', 'Fire'),
        'one Energy type more': lambda t: t.replace('Fire, Water', 'Fire, Water, Grass'),
        'no Energy line': lambda t: t.replace('Energy: Fire, Water\n', ''),
        'an Energy line with no type after it': lambda t: t.replace('Energy: Fire, Water', 'Energy:'),
        'a second Energy line': lambda t: t + 'Energy: Metal\n',
        'the Energy line only after the cards': lambda t: t.replace('Energy: Fire, Water\n', '') + 'Energy: Fire, Water\n',
        # white space: a line ends at a line feed only (a form feed, a vertical tab, NEL, U+2028, U+2029 or a lone carriage return inside a name does not cut it), and a
        # word ends at any Unicode White_Space character
        'a form feed inside a printed name': lambda t: t.replace('Poké Ball', 'Poké\x0cBall'),
        'a vertical tab inside a printed name': lambda t: t.replace('Poké Ball', 'Poké\x0bBall'),
        'a next-line character (NEL) inside a printed name': lambda t: t.replace('Poké Ball', 'Poké\x85Ball'),
        'a line separator (U+2028) inside a printed name': lambda t: t.replace('Poké Ball', 'Poké Ball'),
        'a paragraph separator (U+2029) inside a printed name': lambda t: t.replace('Poké Ball', 'Poké Ball'),
        'a lone carriage return inside a printed name': lambda t: t.replace('Poké Ball', 'Poké\rBall'),
        'all of them in one name': lambda t: t.replace('Pokémon Center Lady', 'Pokémon\x0cCenter\x0b\x85Lady  Of\rIt'),
        'a card line with no printed name': lambda t: t.replace('1 Poké Ball P-A 005', '1 P-A 005'),
        'the same card said in two spellings that add up': lambda t: t.replace('2 Torchic B1 033\n', '1 Torchic B1 033\n1 TORCHIC b1 33\n'),
        'a zero-count line of a card already in the deck': lambda t: t + '0 Torchic B1 033\n',
        'an indented heading line and a line of white space only': lambda t: t + '   Trainer: 1\n\t\n',
    }
    for _ch in WHITE_SPACE:
        if _ch != ' ':
            SAME[f'U+{ord(_ch):04X} between every pair of words'] = (lambda ch: lambda t: t.replace(' ', ch))(_ch)
    del _ch
    DIFFERENT = {
        'another card number': lambda t: t.replace('B1 033', 'B1 034'),
        'another set': lambda t: t.replace('B1 033', 'B2 033'),
        'one count changed': lambda t: t.replace('2 Torchic', '3 Torchic'),
        'one card more': lambda t: t + '1 Mew A1 151\n',
        'one card less': lambda t: t.replace('1 Pokémon Center Lady A2b 070\n', ''),
        'two counts swapped between cards': lambda t: t.replace('2 Torchic', '16 Torchic').replace('16 Filler', '2 Filler'),
        'two lines given the same card id (their counts add up)': lambda t: t.replace('2 Torchic B1 033', '2 Torchic X1 002'),
        'a card line said twice (the counts add up)': lambda t: t + '1 Poké Ball P-A 005\n',
        'a card with a four-digit number (the number is padded to three, never cut)': lambda t: t.replace('B1 033', 'B1 0033'),
        'another set code that differs in a letter': lambda t: t.replace('A2b 070', 'A2c 070'),
    }

    def sig(self, content):
        data = content if isinstance(content, bytes) else content.encode('utf-8')
        with tempfile.TemporaryDirectory() as t:
            write(os.path.join(t, 'deck.txt'), data, binary=True)
            return P.deck_signature(os.path.join(t, 'deck.txt'))

    def test_every_way_of_saving_the_same_cards_has_the_same_signature(self):
        base = self.sig(self.BASE)
        self.assertFalse(base.startswith('raw:'), 'the base deck is readable as a deck')
        for how, make in self.SAME.items():
            with self.subTest(how=how):
                new = make(self.BASE)
                self.assertNotEqual(new if isinstance(new, bytes) else new.encode(), self.BASE.encode(), 'a copy that is the same bytes proves nothing')
                self.assertEqual(self.sig(new), base)

    def test_any_change_to_a_card_or_a_count_is_a_different_deck(self):
        base = self.sig(self.BASE)
        seen = {base}
        for how, make in self.DIFFERENT.items():
            with self.subTest(how=how):
                new = make(self.BASE)
                self.assertNotEqual(new, self.BASE)
                s = self.sig(new)
                self.assertFalse(s.startswith('raw:'), 'still readable as a deck')
                self.assertNotIn(s, seen, 'different from the base deck and from every other change')
                seen.add(s)

    def test_the_energy_line_is_not_part_of_the_deck(self):
        """The same cards with another Energy line, or with none, are one deck; the same Energy line over other cards is not."""
        cards = '2 Torchic B1 033\n18 Filler X1 002\n'
        same = self.sig(cards)
        for line in ('Energy: Fire\n', 'Energy: Water, Grass\n', 'Energy:\n', 'Energy: Nonsense\n', 'Energy:Fire,Water,Grass,Lightning\n'):
            with self.subTest(line=line):
                self.assertEqual(self.sig(line + cards), same)
                self.assertEqual(self.sig(cards + line), same)
        self.assertNotEqual(self.sig('Energy: Fire\n' + '2 Torchic B1 034\n18 Filler X1 002\n'), self.sig('Energy: Fire\n' + cards))

    def test_a_line_ends_at_a_line_feed_only(self):
        """A carriage return before the line feed is white space; a carriage return alone is not a line end (the engine reads such a file as one line: the first count,
        the last two words), and neither is a form feed, a vertical tab, NEL, U+2028 or U+2029."""
        cards = ['2 Torchic B1 033', '1 Poké Ball P-A 005', '17 Filler X1 002']
        crlf = self.sig('\r\n'.join(cards) + '\r\n')
        self.assertEqual(crlf, self.sig('\n'.join(cards) + '\n'))
        for how, end in (('a lone carriage return', '\r'), ('a form feed', '\x0c'), ('a vertical tab', '\x0b'), ('NEL', '\x85'), ('a line separator (U+2028)', ' '),
                         ('a paragraph separator (U+2029)', ' ')):
            with self.subTest(line_end=how):
                one_line = self.sig(end.join(cards))
                self.assertEqual(one_line, self.sig('2 Filler X1 002\n'), 'one line: the first count (2), the last two words (X1 002)')
                self.assertNotEqual(one_line, self.sig('\n'.join(cards)))
        self.assertTrue(self.sig(self.BASE.replace('\n', '\r')).startswith('raw:'), 'the Energy line then swallows the whole file, which has no cards left')

    def test_a_word_ends_at_unicode_white_space_and_at_nothing_else(self):
        """Rust's White_Space ends a word. A control character the engine does not count as white space (U+001C to U+001F), a zero-width space or a byte order mark
        stays inside its word: the line reads as another card, and the deck is another deck."""
        base = self.sig('2 Torchic B1 033\n18 Filler X1 002\n')
        for ch in WHITE_SPACE:
            with self.subTest(white_space=f'U+{ord(ch):04X}'):
                self.assertEqual(self.sig(f'2{ch}Torchic{ch}B1{ch}033\n18 Filler X1 002\n'), base)
                self.assertEqual(self.sig(f'{ch}{ch}2 Torchic B1 033{ch}\n18 Filler X1 002\n'), base)
                self.assertEqual(self.sig(f'2 Torchic B1{ch}{ch}033\n18 Filler X1 002\n'), base)
        seen = {base}
        for ch in NOT_WHITE_SPACE:
            with self.subTest(not_white_space=f'U+{ord(ch):04X}'):
                s = self.sig(f'2 Torchic B1{ch}033\n18 Filler X1 002\n')
                self.assertFalse(s.startswith('raw:'), 'still a card line: three or more words')
                self.assertNotIn(s, seen)
                seen.add(s)

    def test_a_number_is_padded_to_three_digits_and_never_cut(self):
        rest = '19 Filler X1 002\n'
        self.assertEqual(self.sig('1 Delta B3 79\n' + rest), self.sig('1 Delta B3 079\n' + rest))
        self.assertEqual(self.sig('1 Delta B3 7\n' + rest), self.sig('1 Delta B3 007\n' + rest))
        self.assertEqual(self.sig('1 Delta B3 0\n' + rest), self.sig('1 Delta B3 000\n' + rest))
        self.assertEqual(self.sig('1 Delta B3 79\n1 Delta B3 079\n' + rest), self.sig('2 Delta B3 079\n' + rest), 'two spellings of one card are one card')
        for other in ('B3 0079', 'B3 790', 'B3 78', 'B3 79b', 'B4 79'):
            with self.subTest(other=other):
                self.assertNotEqual(self.sig(f'1 Delta {other}\n' + rest), self.sig('1 Delta B3 079\n' + rest))

    def test_the_set_is_compared_in_lower_case_and_the_printed_name_not_at_all(self):
        rest = '19 Filler X1 002\n'
        one = self.sig('1 Lady A2b 070\n' + rest)
        for spelling in ('a2b', 'A2B', 'a2B'):
            with self.subTest(set=spelling):
                self.assertEqual(self.sig(f'1 Lady {spelling} 070\n' + rest), one)
        for name in ('LADY', 'Pokémon Center Lady', 'Pokemon Center Lady', 'a name of seven words and 42 digits', '999', 'Ünïcödé ✓ ‘quoted’'):
            with self.subTest(name=name):
                self.assertEqual(self.sig(f'1 {name} A2b 070\n' + rest), one)
        self.assertEqual(self.sig('1 Lady A2b 070\n1 Other a2B 070\n' + '18 Filler X1 002\n'), self.sig('2 Lady A2b 070\n18 Filler X1 002\n'))

    def test_counts_of_one_card_add_up_across_lines_and_a_zero_count_adds_nothing(self):
        self.assertEqual(self.sig('1 A X1 001\n1 B x1 1\n18 F X1 002\n'), self.sig('2 A X1 001\n18 F X1 002\n'))
        self.assertNotEqual(self.sig('1 A X1 001\n18 F X1 002\n'), self.sig('2 A X1 001\n18 F X1 002\n'))
        self.assertEqual(self.sig('02 A X1 001\n18 F X1 002\n'), self.sig('2 A X1 001\n18 F X1 002\n'), 'a count is a number: leading zeros do not matter')
        self.assertEqual(self.sig('2 A X1 001\n0 B X1 009\n18 F X1 002\n'), self.sig('2 A X1 001\n18 F X1 002\n'), 'a card said 0 times is not in the deck')
        self.assertEqual(self.sig('2 A X1 001\n0 A X1 001\n18 F X1 002\n'), self.sig('2 A X1 001\n18 F X1 002\n'))

    def test_a_card_line_of_three_words_has_no_printed_name_and_two_words_is_not_a_card(self):
        self.assertEqual(self.sig('2 B1 033\n18 X1 002\n'), self.sig('2 Torchic B1 033\n18 Filler X1 002\n'))
        for line in ('2 Torchic', '2', 'B1 033', 'Torchic', '2\tTorchic'):
            with self.subTest(line=line):
                text = self.BASE + line + '\n'
                self.assertEqual(self.sig(text), 'raw:' + hashlib.sha256(text.encode()).hexdigest())

    def test_a_file_that_cannot_be_read_as_a_deck_is_known_by_its_bytes(self):
        for how, text in {'a line that is not a card': self.BASE + '# my notes\n', 'a line with a word instead of a count': self.BASE + 'Total 20 cards\n',
                          'a card line missing its count': self.BASE + 'Torchic B1 033\n', 'a count that is not a whole number': self.BASE + '1.5 Torchic B1 033\n',
                          'a card line of two words': self.BASE + '2 Torchic\n', 'a byte order mark in the middle of the file': self.BASE + '﻿1 Mew A1 151\n',
                          'a heading spelled without its accent (only `Pokémon:` is a heading)': 'Pokemon: 4\n' + self.BASE,
                          'a file whose only line ends are lone carriage returns': self.BASE.replace('\n', '\r'),
                          'no cards at all': 'Energy: Fire\n', 'only headings': 'Pokémon: 3\nTrainer: 1\nEnergy: Fire\n', 'only cards said 0 times': 'Energy: Fire\n0 Torchic B1 033\n',
                          'only white space': ' \n\t\n\n', 'an empty file': ''}.items():
            with self.subTest(how=how):
                s = self.sig(text)
                self.assertTrue(s.startswith('raw:'), s)
                self.assertEqual(s, 'raw:' + hashlib.sha256(text.encode()).hexdigest(), 'the signature is the hash of the bytes')
                self.assertEqual(self.sig(text), s, 'the same bytes, the same signature')
                self.assertNotEqual(self.sig(text + '\n\n'), s, 'other bytes, another signature: nothing is guessed about a file the engine cannot read either')
                self.assertNotEqual(s, self.sig(self.BASE))

    def test_bytes_that_are_not_utf8_are_known_by_their_bytes_too(self):
        for how, data in {'a Latin-1 e acute in a name': b'Energy: Fire\n2 Torchic B1 033\n1 Pok\xe9 Ball P-A 005\n17 Filler X1 002\n', 'a stray byte': self.BASE.encode() + b'\xff\n',
                          'a truncated UTF-8 character': self.BASE.encode() + b'1 Mew\xc3 A1 151\n'}.items():
            with self.subTest(how=how):
                self.assertEqual(self.sig(data), 'raw:' + hashlib.sha256(data).hexdigest())

    def test_a_missing_file_is_an_error_the_caller_can_catch(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(OSError):
                P.deck_signature(os.path.join(t, 'nope.txt'))

    def test_a_folder_in_place_of_the_file_is_an_error_the_caller_can_catch_too(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(OSError):
                P.deck_signature(t)

    def test_a_file_that_is_hashed_is_closed_again(self):
        """sha() and deck_signature() read many files in a long run; a file object left to the garbage collector is a ResourceWarning and, in the end, no free descriptors."""
        with tempfile.TemporaryDirectory() as t:
            deck, notes = os.path.join(t, 'deck.txt'), os.path.join(t, 'notes.txt')
            write(deck, self.BASE)
            write(notes, '# not a deck\n')
            calls = (('sha', lambda: P.sha(deck)), ('the signature of a deck', lambda: P.deck_signature(deck)),
                     ('the signature of a file that is not a deck', lambda: P.deck_signature(notes)))
            for how, call in calls:
                with self.subTest(call=how):
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter('always')
                        call()
                        gc.collect()
                    self.assertEqual([str(w.message) for w in caught if issubclass(w.category, ResourceWarning)], [])


class UnreadableDeckFile(World):
    """The held-out guard reads the file of every deck it compares: all the held-out decks, every deck under test and every opponent, in every stage. A file it cannot read
    is a clean REFUSED that names the deck, the path and the reason, before anything is written; it is never a traceback and never a guess."""

    ROLES = {'a held-out deck': ('held-1', 'decks/held1.txt'), 'a deck under test': ('a-deck', 'decks/a.txt'), 'an opponent': ('t-1', 'decks/t1.txt')}
    DAMAGE = {'the file is missing': errno.ENOENT, 'a folder where the file should be': errno.EISDIR, 'a link to nowhere': errno.ENOENT, 'no permission to read it': errno.EACCES}

    def damage(self, how, rel):
        path = os.path.join(self.repo, *rel.split('/'))
        os.remove(path)
        if how == 'a folder where the file should be':
            os.makedirs(path)
        elif how == 'a link to nowhere':
            os.symlink(os.path.join(self.tmp, 'nowhere.txt'), path)
        elif how == 'no permission to read it':
            write(path, deck_text('x'))
            os.chmod(path, 0)
            return os.access(path, os.R_OK)  # (the superuser can read it anyway: nothing to test)
        return False

    def config_for(self, stage):
        return {'dev': self.config, 'use': self.use_config, 'heldout': lambda: self.config(stage='heldout')}[stage]()

    def test_an_unreadable_deck_file_is_refused_by_name_in_every_stage(self):
        for stage in ('dev', 'use', 'heldout'):
            for role, (name, rel) in self.ROLES.items():
                for how, code in self.DAMAGE.items():
                    with self.subTest(stage=stage, role=role, damage=how):
                        self.make(locked=stage != 'heldout')
                        if self.damage(how, rel):
                            continue
                        r = self.prereg(self.config_for(stage))
                        self.assertEqual(r.returncode, 1)
                        self.assertEqual(r.stderr, f'REFUSED: the deck file of {name} ({rel}) cannot be read ({os.strerror(code)}), so the held-out guard cannot compare it; nothing was written.\n')
                        self.assertEqual(r.stdout, '')
                        self.assertFalse(os.path.exists(self.out), 'a refusal leaves no run directory')

    def test_every_held_out_file_is_read_before_any_deck_of_the_run_is_judged(self):
        """The guard cannot compare a file it cannot read, and does not wave it through: one held-out file it cannot read stops the registration, even for a run that asks
        for another held-out deck (which it would otherwise refuse for another reason) and for a run that asks for none."""
        r = self.prereg(self.config(decks=['held-1']))
        self.assertIn('held-1 is a held-out deck', r.stderr)
        os.remove(os.path.join(self.repo, 'decks', 'held2.txt'))
        for cfg in (self.config(decks=['held-1']), self.config(), self.use_config()):
            r = self.prereg(cfg)
            self.assertIn('the deck file of held-2 (decks/held2.txt) cannot be read', r.stderr)
            self.assertNotIn('Traceback', r.stderr)
            self.assertTrue(self.no_manifest())

    def test_a_deck_given_by_a_path_that_is_not_there_is_a_clean_refusal_too(self):
        r = self.prereg(self.use_config(decks=[], deck_files=['decks/nope.txt']))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('deck file decks/nope.txt not found', r.stderr)
        self.assertNotIn('Traceback', r.stderr)


class PreRegisteredLine(World):
    """The line the script prints when it has finished says how big the registration is, with the singular where there is one of a thing."""

    CASES = (
        ('one pair, one deal, one seat', dict(opponent_groups=[], opponents=['t-1'], deals=1, seats=[0]), 'pre-registered 2 games (1 pair, 1 deal x 1 seat x 2 arms) in {out}'),
        ('one pair', dict(opponent_groups=[], opponents=['t-1'], deals=3), 'pre-registered 12 games (1 pair, 3 deals x 2 seats x 2 arms) in {out}'),
        ('one deal', dict(deals=1), 'pre-registered 8 games (2 pairs, 1 deal x 2 seats x 2 arms) in {out}'),
        ('one seat', dict(deals=2, seats=[1]), 'pre-registered 8 games (2 pairs, 2 deals x 1 seat x 2 arms) in {out}'),
        ('more than one of each', dict(deals=3), 'pre-registered 24 games (2 pairs, 3 deals x 2 seats x 2 arms) in {out}'),
    )

    def test_the_line_counts_games_pairs_deals_and_seats_in_the_right_number(self):
        for how, kw, line in self.CASES:
            with self.subTest(case=how):
                shutil.rmtree(self.out, ignore_errors=True)
                r = self.prereg(self.config(**kw))
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(r.stdout.splitlines(), [line.format(out=self.out), 'manifest sha256 ' + sha(os.path.join(self.out, 'manifest.json'))])
                self.assertEqual(self.manifest()['planned_games'], int(line.split()[1]))

    def test_the_same_line_for_a_use_run(self):
        r = self.prereg(self.use_config(opponent_groups=[], opponents=['t-1'], deals=1, seats=[0]))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0], f'pre-registered 2 games (1 pair, 1 deal x 1 seat x 2 arms) in {self.out}')


class RegistrationIsCompleteWhenTheShaIsThere(World):
    """manifest.sha256 is written last, after PREREGISTRATION.md: a folder that has a manifest but no manifest.sha256 is an unfinished registration (slow_report.py clears it)."""

    def test_a_registration_that_fails_while_writing_the_document_has_no_manifest_sha256(self):
        os.makedirs(os.path.join(self.out, 'PREREGISTRATION.md'))  # a folder where the document goes: the script fails when it comes to write it
        r = self.prereg(self.config())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('PREREGISTRATION.md', r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.out, 'manifest.json')), 'the manifest was written before the document')
        self.assertFalse(os.path.exists(os.path.join(self.out, 'manifest.sha256')), 'so the registration is not complete')

    def test_a_finished_registration_has_the_three_files_and_they_agree_on_the_manifest(self):
        r = self.prereg(self.config())
        self.assertEqual(r.returncode, 0, r.stderr)
        msha = sha(os.path.join(self.out, 'manifest.json'))
        self.assertEqual(read(os.path.join(self.out, 'manifest.sha256')), msha + '  manifest.json\n')
        self.assertIn(f'(`manifest.json`, sha256 `{msha}`)', read(os.path.join(self.out, 'PREREGISTRATION.md')))
        self.assertEqual(r.stdout.splitlines()[-1], 'manifest sha256 ' + msha)


class PreRegistrationOrderUnchanged(World):
    def test_a_manifest_is_written_once(self):
        self.assertEqual(self.prereg(self.config()).returncode, 0)
        r = self.prereg(self.config())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('already exists', r.stderr)

    def test_a_directory_with_games_is_refused(self):
        os.makedirs(self.out)
        write(os.path.join(self.out, 'games.jsonl'), '{}\n')
        r = self.prereg(self.config())
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('pre-registration comes first', r.stderr)


if __name__ == '__main__':
    unittest.main()
