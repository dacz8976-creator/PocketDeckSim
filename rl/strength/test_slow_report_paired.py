#!/usr/bin/env python3
"""Tests of the paired variant of a slow report: `slow_report.py --paired-with BASE_FOLDER --deck VARIANT_FILE` (slow_report_paired.py).

  cd rl/strength && python3 -B -m unittest -v test_slow_report_paired

A variant of a deck (one or two cards swapped) is played on the very deals of an earlier, registered report of the base deck: the same seed_base (no new seed slot), deals,
seats, opponents, threads and school rule, the same program and pin. How a seed becomes a shuffle (engine/src/deck.rs, state/mod.rs): the game's StdRng is seeded with the
seed, each deck is shuffled by Fisher-Yates (which moves positions and looks at no card), only a hand without a Basic is repaired afterwards (which looks at which positions
hold a Basic), then the coin flip and the Energy roll. A card that keeps its place in the deck file therefore keeps its place in the shuffle, and the two games start alike
except for that one card. Everything runs on the World of test_slow_report.py: a temporary repository with synthetic decks, the fake program and a pin that names it.
"""
import contextlib, io, json, os, re, statistics, sys, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402
import slow_report_paired as PAIRED  # noqa: E402
import test_slow_report as T  # noqa: E402

read, write, jsonl = T.read, T.write, T.jsonl


def tree(root):
    """{path relative to root: bytes} of every file under root."""
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            with open(os.path.join(dp, f), 'rb') as fh:
                out[os.path.relpath(os.path.join(dp, f), root)] = fh.read()
    return out

BASE_DECK = 'Energy: Fire\n2 Torchic B1 033\n2 Combusken B1 034\n1 Ilima A3 149\n15 Filler X1 002\n'
CAPE_DECK = 'Energy: Fire\n2 Torchic B1 033\n2 Combusken B1 034\n1 Giant Cape A2 147\n15 Filler X1 002\n'   # Ilima's line holds the Cape: the same place
MOVED_DECK = 'Energy: Fire\n2 Torchic B1 033\n2 Combusken B1 034\n15 Filler X1 002\n1 Giant Cape A2 147\n'  # the Cape on the last line: Ilima's place is not kept
BASICS = {'b1 033', 'x1 002'}   # Torchic and the Filler are Basic Pokémon; the others are not


def is_basic(card_id):
    return card_id in BASICS


def deck_of(*lines):
    return 'Energy: Fire\n' + ''.join(f'{l}\n' for l in lines)


class DeckDiff(unittest.TestCase):
    def diff(self, base, variant, basic=is_basic):
        return PAIRED.diff_decks(base, variant, basic)

    def test_one_swap_in_the_same_place_is_aligned_and_names_both_cards(self):
        d = self.diff(BASE_DECK, CAPE_DECK)
        self.assertEqual((d['swaps'], d['aligned'], d['problems']), (1, True, []))
        self.assertEqual(d['slots'], [4])                      # file order: Torchic 0-1, Combusken 2-3, Ilima 4
        self.assertEqual(PAIRED.swap_text(d), '-1 Ilima A3 149, +1 Giant Cape A2 147')
        self.assertEqual(d['basic_shape'], True)               # neither card is a Basic Pokémon

    def test_the_same_swap_with_the_new_card_moved_to_another_line_is_not_aligned_but_still_a_swap(self):
        d = self.diff(BASE_DECK, MOVED_DECK)
        self.assertEqual((d['swaps'], d['aligned'], d['problems']), (1, False, []))
        self.assertGreater(len(d['slots']), 1)                 # every card after Ilima's old place moved by one

    def test_a_card_taken_from_a_two_copy_line_may_keep_either_copys_place(self):
        base = deck_of('2 Torchic B1 033', '2 Poké Ball P-A 005', '16 Filler X1 002')
        for variant in (deck_of('2 Torchic B1 033', '1 Poké Ball P-A 005', '1 Giant Cape A2 147', '16 Filler X1 002'),
                        deck_of('2 Torchic B1 033', '1 Giant Cape A2 147', '1 Poké Ball P-A 005', '16 Filler X1 002')):
            d = self.diff(base, variant)
            self.assertEqual((d['swaps'], d['aligned']), (1, True), variant)
            self.assertEqual(len(d['slots']), 1)

    def test_two_swaps_are_allowed_and_three_are_refused(self):
        two = deck_of('2 Torchic B1 033', '2 Combusken B1 034', '1 Giant Cape A2 147', '1 Big Malasada A3 142', '14 Filler X1 002')
        d = self.diff(deck_of('2 Torchic B1 033', '2 Combusken B1 034', '1 Ilima A3 149', '1 Cyrus A2 150', '14 Filler X1 002'), two)
        self.assertEqual((d['swaps'], d['aligned'], d['problems']), (2, True, []))
        three = deck_of('2 Torchic B1 033', '1 Giant Cape A2 147', '1 Big Malasada A3 142', '1 Cyrus A2 150', '15 Filler X1 002')
        d = self.diff(deck_of('2 Torchic B1 033', '2 Combusken B1 034', '1 Ilima A3 149', '15 Filler X1 002'), three)
        self.assertEqual(d['swaps'], 3)
        self.assertTrue(any('at most 2' in p for p in d['problems']), d['problems'])

    def test_the_same_cards_in_another_order_are_no_variant(self):
        d = self.diff(BASE_DECK, deck_of('1 Ilima A3 149', '2 Torchic B1 033', '2 Combusken B1 034', '15 Filler X1 002'))
        self.assertEqual(d['swaps'], 0)
        self.assertTrue(any('no card differs' in p for p in d['problems']), d['problems'])

    def test_another_energy_line_is_refused(self):
        d = self.diff(BASE_DECK, CAPE_DECK.replace('Energy: Fire', 'Energy: Water'))
        self.assertTrue(any('Energy line' in p for p in d['problems']), d['problems'])
        self.assertEqual(self.diff(BASE_DECK, CAPE_DECK.replace('Energy: Fire', 'Energy:Fire'))['problems'], [], 'the spelling of the line does not matter')

    def test_a_variant_of_another_size_is_refused(self):
        d = self.diff(BASE_DECK, CAPE_DECK.replace('15 Filler', '14 Filler'))
        self.assertTrue(any('19 cards' in p for p in d['problems']), d['problems'])

    def test_how_the_file_was_saved_does_not_matter(self):
        crlf = CAPE_DECK.replace('\n', '\r\n').encode('utf-8')
        with_bom = b'\xef\xbb\xbf' + CAPE_DECK.encode('utf-8')
        headed = CAPE_DECK.replace('Energy: Fire\n', 'Energy: Fire\nPokémon: 8\nTrainer: 12\n')
        unpadded = CAPE_DECK.replace('A2 147', 'A2 0147').replace('B1 033', 'B1 33')
        for how, variant in {'CRLF': crlf.decode('utf-8'), 'a byte order mark': with_bom.decode('utf-8-sig'), 'heading lines': headed,
                             'a longer printed name': CAPE_DECK.replace('Giant Cape', 'Giant   Cape (art 2)'), 'set codes in lower case': CAPE_DECK.replace('A2 147', 'a2 147')}.items():
            with self.subTest(how=how):
                d = self.diff(BASE_DECK, variant)
                self.assertEqual((d['swaps'], d['aligned'], d['problems']), (1, True, []), d)
        self.assertEqual(self.diff(BASE_DECK, unpadded)['swaps'], 1, 'numbers are read as the engine does: padded to three digits')

    def test_a_basic_swapped_for_a_card_that_is_not_one_changes_the_shape_of_the_opening_hand_repair(self):
        # the engine redeals a hand with no Basic by looking at which positions hold a Basic, so such a swap can move the twin games apart before the card is drawn
        variant = BASE_DECK.replace('15 Filler X1 002', '14 Filler X1 002\n1 Giant Cape A2 147')    # the last Filler (a Basic) becomes the Cape (not one)
        d = self.diff(BASE_DECK, variant)
        self.assertEqual((d['swaps'], d['aligned'], d['slots']), (1, True, [19]))
        self.assertEqual(d['basic_shape'], False)
        self.assertEqual(self.diff(BASE_DECK, variant, None)['basic_shape'], None, 'without a card database it is not known')
        self.assertEqual(self.diff(BASE_DECK, variant, lambda i: None)['basic_shape'], None, 'a card the database does not know leaves it unknown')

    def test_a_card_line_that_is_not_one_is_a_problem_not_a_crash(self):
        d = self.diff(BASE_DECK, CAPE_DECK + 'what is this\n')
        self.assertTrue(d['problems'] and 'not a card line' in d['problems'][0], d['problems'])


# ---------------------------------------------------------------------------------------------------------- a base report and its variant
class PairedWorld(T.World):
    """A registered base report (2 deals, 3 threads) of BASE_DECK and room for variants beside it."""

    def setUp(self):
        super().setUp()
        self.make(BASE_DECK)
        self.cape = os.path.join(self.repo, 'decks', 'events', 'my-list-cape.txt')
        write(self.cape, CAPE_DECK)
        code, out, err = self.cli('--deals', '2', '--threads', '3', '--register-only')
        self.assertEqual(code, 0, out + err)
        self.base = self.rundir()
        self.base_rel = 'rl/results/slow_reports/2026-10-10_my-list'

    def pair(self, *extra, variant=None, base=None, date='2026-10-11', deck_flag=True, basic=is_basic, school='off', deck_check=lambda p, r: []):
        """slow_report.main with --paired-with (the base folder by default) and the variant file as --deck; returns (exit code, stdout, stderr)."""
        argv = ['--paired-with', base or self.base]
        if deck_flag:
            argv += ['--deck', variant or self.cape]
        argv += ['--repo', self.repo, '--pin', self.pin_path, '--poll-s', '1', '--out-root', self.out_root, '--date', date]
        if school is not None:
            argv += ['--school-rule', school]
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = sr.main(argv + list(extra), now=self.clock.now, sleep=self.clock.sleep, spawn=None, deck_check=deck_check, basic_check=basic)
        except SystemExit as e:
            code = e.code
        return code, out.getvalue(), err.getvalue()

    def variant_dir(self, name='2026-10-11_my-list-cape'):
        return os.path.join(self.out_root, name)

    def manifest(self, d):
        return json.loads(read(os.path.join(d, 'manifest.json')))

    def register_variant(self, *extra, **kw):
        code, out, err = self.pair('--register-only', *extra, **kw)
        self.assertEqual(code, 0, out + err)
        return self.variant_dir()

    def refused(self, *extra, **kw):
        code, out, err = self.pair('--register-only', *extra, **kw)
        self.assertNotEqual(code, 0, out + err)
        self.assertFalse(os.path.exists(self.variant_dir()), 'a refusal leaves nothing behind')
        return str(code) + out + err


class PairedRegistration(PairedWorld):
    def test_the_variant_takes_the_bases_deals_and_no_new_seed_slot(self):
        base = self.manifest(self.base)
        with mock.patch.object(sr, 'pick_seed_base', side_effect=AssertionError('a paired variant never picks a seed slot')):
            d = self.register_variant()
        v = self.manifest(d)
        for key in ('seed_base', 'pair_stride', 'deals', 'seats', 'threads', 'opponents', 'pilot', 'reference', 'stage', 'program_sha256', 'log_level'):
            self.assertEqual(v[key], base[key], key)
        self.assertEqual([x['name'] for x in v['decks']], ['my-list-cape'])
        self.assertEqual(v['decks'][0]['sha256'], sr.sha(self.cape))
        self.assertEqual(v['threads'], 3)
        self.assertEqual(v['slow_report']['paired'], base['slow_report']['paired'])

    def test_the_registration_says_paired_with_the_folder_and_what_differs(self):
        d = self.register_variant()
        v = self.manifest(d)
        pw = v['slow_report']['paired_with']
        self.assertEqual(pw['folder'], self.base_rel)
        self.assertEqual(pw['manifest_sha256'], sr.sha(os.path.join(self.base, 'manifest.json')))
        self.assertEqual((pw['base_deck_name'], pw['base_deck_file'], pw['base_deck_sha256']), ('my-list', self.deck_rel, sr.sha(self.deck)))
        self.assertEqual((pw['swaps'], pw['slots'], pw['aligned'], pw['basic_shape']), (1, [4], True, True))
        self.assertEqual((pw['removed'], pw['added']), (['1 Ilima A3 149'], ['1 Giant Cape A2 147']))
        self.assertIn(f'paired with {self.base_rel}', v['question'])
        self.assertIn(f'paired with {self.base_rel}', read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertIn('-1 Ilima A3 149, +1 Giant Cape A2 147', v['question'])
        reg = [e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'registered'][0]
        self.assertEqual(reg['seed_base'], self.manifest(self.base)['seed_base'])
        self.assertEqual(reg['paired_with'], self.base_rel)

    def test_the_base_folder_is_left_untouched(self):
        before = tree(self.base)
        self.register_variant()
        self.pair('--dry-run')
        self.assertEqual(tree(self.base), before)

    def test_a_base_registered_with_the_rule_off_gives_a_variant_with_the_rule_off(self):
        block = self.manifest(self.register_variant(school=None))['slow_report']   # no --school-rule given: the default of a new registration is on, the base's is off
        self.assertEqual(block['school_rule'], 'off')
        self.assertNotIn('--school-days', block['resume_command'])

    def test_the_school_rule_and_days_are_the_bases_unless_given(self):
        import shutil
        shutil.rmtree(self.out_root)
        code, out, err = self.cli('--deals', '2', '--register-only', '--school-days', 'sat,sun', school='on')   # a base registered with the rule on and two school days
        self.assertEqual(code, 0, out + err)
        block = self.manifest(self.register_variant(school=None))['slow_report']
        self.assertEqual((block['school_rule'], block['school_days']), ('on', 'sat,sun'))
        self.assertIn('--school-days sat,sun', block['resume_command'])
        shutil.rmtree(self.variant_dir())
        block = self.manifest(self.register_variant(school='off'))['slow_report']
        self.assertEqual(block['school_rule'], 'off')

    def test_the_variants_games_have_the_seeds_of_the_bases_games(self):
        """The fake program derives each seed from the manifest as the real one does (seed_base + p x stride + deal): both folders played to the end give each twin one seed."""
        d = self.register_variant()
        for folder in (self.base, d):
            code, out, err = self.cli('--dir', folder, deck=False)
            self.assertEqual(code, 0, out + err)
            self.assertEqual('compared with the base report: kx3: ' in out, folder == d, 'only the variant echoes the change to the terminal')
        twin = lambda g: (g['opp'], g['deal'], g['seat'], g['arm'])
        base_seeds = {twin(g): g['seed'] for g in sr.load_games(self.base)}
        var_seeds = {twin(g): g['seed'] for g in sr.load_games(d)}
        self.assertEqual(len(var_seeds), 8 * 2 * 2 * 2)
        self.assertEqual(var_seeds, base_seeds)

    def test_a_variant_registered_under_the_pin_with_other_irrelevant_entries_is_taken_and_says_so(self):
        pin = json.loads(read(self.pin_path))
        pin['a_note_that_decides_nothing'] = 'x'
        write(self.pin_path, json.dumps(pin))
        d = self.register_variant()
        pw = self.manifest(d)['slow_report']['paired_with']
        self.assertIn('pin file', pw['pin_note'])
        self.assertIn('same', pw['pin_note'])

    def test_the_dry_run_prints_the_pairing_and_writes_nothing(self):
        code, out, err = self.pair('--dry-run')
        self.assertEqual(code, 0, out + err)
        self.assertIn(f'paired with {self.base_rel}', out)
        self.assertIn('-1 Ilima A3 149, +1 Giant Cape A2 147', out)
        self.assertIn('keeps its place in the deck file', out)
        self.assertIn('no new seed slot', out)
        self.assertIn('dry run: nothing written', out)
        self.assertFalse(os.path.exists(self.variant_dir()))

    def test_a_variant_whose_card_loses_its_place_is_taken_with_the_warning(self):
        moved = self._write_variant('moved', MOVED_DECK)
        code, out, err = self.pair('--dry-run', variant=moved)
        self.assertEqual(code, 0, out + err)
        self.assertIn('does NOT keep its place', out)
        self.register_variant(variant=moved, date='2026-10-12')
        man = self.manifest(self.variant_dir('2026-10-12_my-list-moved'))
        pw = man['slow_report']['paired_with']
        self.assertEqual((pw['aligned'], pw['swaps']), (False, 1))
        self.assertIn('does not keep its place', man['question'])

    def test_a_basic_swapped_for_a_non_basic_is_taken_with_the_warning(self):
        text = BASE_DECK.replace('15 Filler X1 002', '14 Filler X1 002\n1 Giant Cape A2 147')
        code, out, err = self.pair('--dry-run', variant=self._write_variant('basic', text))
        self.assertEqual(code, 0, out + err)
        self.assertIn('Basic', out)
        self.assertIn('can differ before the card is drawn', out)

    def _write_variant(self, name, text):
        p = os.path.join(self.repo, 'decks', 'events', f'my-list-{name}.txt')
        write(p, text)
        return p


class PairedRefusals(PairedWorld):
    def test_three_swaps_none_and_another_energy_line_are_refused_with_the_diff(self):
        three = deck_of('2 Torchic B1 033', '1 Combusken B1 034', '1 Giant Cape A2 147', '1 Big Malasada A3 142', '1 Cyrus A2 150', '14 Filler X1 002')
        out = self.refused(variant=self._wv('three', three))
        self.assertIn('at most 2', out)
        self.assertIn('Ilima', out)
        self.assertIn('no card differs', self.refused(variant=self._wv('same', BASE_DECK.replace('Energy: Fire', 'Energy:Fire'))))
        self.assertIn('Energy line', self.refused(variant=self._wv('water', CAPE_DECK.replace('Fire', 'Water'))))

    def test_a_base_that_is_not_a_registered_report_is_refused(self):
        self.assertIn('is not a folder', self.refused(base=os.path.join(self.out_root, 'no-such-folder')))
        os.makedirs(os.path.join(self.tmp, 'empty'))
        self.assertIn('no manifest.json', self.refused(base=os.path.join(self.tmp, 'empty')))

    def test_a_base_whose_registration_was_changed_is_refused(self):
        with open(os.path.join(self.base, 'manifest.json'), 'a') as f:
            f.write(' ')
        self.assertIn('registration has changed', self.refused())

    def test_another_program_than_the_one_the_base_was_played_with_is_refused(self):
        self.set_program(T.FAKE_PROGRAM + '\n# another build\n')
        out = self.refused()
        self.assertIn('program', out)
        self.assertIn('base', out)

    def retag_base(self, **changes):
        """The base's manifest as a registration of another program would have written it (manifest.sha256 follows, so the base is still a registered run)."""
        man = self.manifest(self.base)
        man.update(changes)
        text = json.dumps(man, indent=1, ensure_ascii=False)
        write(os.path.join(self.base, 'manifest.json'), text)
        import hashlib
        write(os.path.join(self.base, 'manifest.sha256'), hashlib.sha256(text.encode('utf-8')).hexdigest() + '  manifest.json\n')

    def test_a_base_played_by_another_program_is_refused_even_when_the_pin_is_the_same(self):
        self.retag_base(program_sha256='a' * 64)
        code, out, err = self.pair('--register-only')
        self.assertIn('the program is not the one the base report was played with', str(code))
        self.assertEqual(str(code).count('\n  '), 1, 'the program is the only thing wrong: ' + str(code))
        self.assertFalse(os.path.exists(self.variant_dir()))

    def test_a_pin_that_decides_something_else_is_refused(self):
        pin = json.loads(read(self.pin_path))
        pin['engine_tree'] = 'f' * 40
        write(self.pin_path, json.dumps(pin))
        out = self.refused()
        self.assertIn('pin', out)
        self.assertIn('engine_tree', out)

    def test_a_pin_with_another_list_of_scrubbed_variables_is_refused(self):
        pin = json.loads(read(self.pin_path))
        pin['scrub_env_prefixes'] = pin['scrub_env_prefixes'][:-1]
        write(self.pin_path, json.dumps(pin))
        out = self.refused()
        self.assertIn('scrub_env_prefixes', out)

    def test_a_panel_list_that_changed_since_the_base_was_registered_is_refused(self):
        write(os.path.join(self.repo, *self.registry['t-altaria'].split('/')), T.PANEL_TEXT['t-altaria'] + '# edited\n')
        out = self.refused()
        self.assertIn('t-altaria', out)
        self.assertIn('changed', out)

    def test_a_base_deck_file_that_changed_since_is_refused(self):
        write(self.deck, BASE_DECK + '\n')
        self.assertIn('base deck file', self.refused())

    def test_a_variant_that_is_a_panel_list_is_still_refused_as_one(self):
        out = self.refused(variant=self._wv('copy', T.PANEL_TEXT['t-sceptile']))
        self.assertIn('t-sceptile', out)

    def test_options_that_would_break_the_pairing_are_refused(self):
        for flag in (['--deals', '3'], ['--seed-base', str(T.BLOCK[0] + 5 * T.STEP)], ['--no-paired']):
            with self.subTest(flag=flag):
                out = self.refused(*flag)
                self.assertIn('--paired-with', out)
                self.assertIn(flag[0], out)
        code, out, err = self.pair('--dir', self.base)
        self.assertNotEqual(code, 0)
        self.assertIn('--paired-with', str(code))

    def test_a_deck_is_needed_once(self):
        self.assertIn('--deck', str(self.pair(deck_flag=False)[0]))
        argv = [self.cape, '--paired-with', self.base, '--deck', self.cape, '--repo', self.repo, '--pin', self.pin_path, '--out-root', self.out_root, '--dry-run']
        with self.assertRaises(SystemExit) as caught:
            with contextlib.redirect_stdout(io.StringIO()):
                sr.main(argv, now=self.clock.now, deck_check=lambda p, r: [])
        self.assertIn('not both', str(caught.exception))

    def test_a_dry_run_that_would_be_refused_says_so_and_exits_with_the_refusal(self):
        self.set_program(T.FAKE_PROGRAM + '\n# another build\n')
        code, out, err = self.pair('--dry-run')
        self.assertNotEqual(code, 0)
        self.assertIn('-1 Ilima A3 149, +1 Giant Cape A2 147', out, 'the plan is printed before the refusal')
        self.assertFalse(os.path.exists(self.variant_dir()))

    def _wv(self, name, text):
        p = os.path.join(self.repo, 'decks', 'events', f'my-list-{name}.txt')
        write(p, text)
        return p


# ---------------------------------------------------------------------------------------------------------- the model of the logged moves
def entry(t, a, act, p=(0, 0), **kw):
    return dict({'t': t, 'a': a, 'act': act, 'p': list(p), 'b': 0, 'n': 3, 'o': (t + 1) // 2, 'ms': 1.0}, **kw)


CARDS = {'Alolan Vulpix': (1, 1), 'Alolan Ninetales ex': (2, 2), "Team Rocket's Rattata": (1, 1)}


def info(name):
    return CARDS.get(name, (None, None))


def log_game(log, first='deck', turns=9, points=(0, 0), winner='opp'):
    return {'first': first, 'log': log, 'turns': turns, 'points': list(points), 'winner': winner}


class LoggedMoves(unittest.TestCase):
    def test_a_charged_pokemon_that_did_not_attack_is_counted_and_a_pokemon_that_was_not_charged_is_not(self):
        g = log_game([entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix'),                                  # turn 1: Vulpix has 1 Energy, its attack costs 1, no attack: charged, idle
                      entry(3, 'Evolve:Alolan Ninetales ex@0', 'Alolan Vulpix'),                        # turn 3: Ninetales ex has 1 Energy, needs 2: not charged
                      entry(5, 'Attach:1Fire@0 zone', 'Alolan Ninetales ex'),                           # turn 5: 2 Energy, no attack: a charged ex, idle
                      entry(7, 'Attach:1Fire@0 zone', 'Alolan Ninetales ex'), entry(7, 'Attack:Binding Snow', 'Alolan Ninetales ex')])
        r = PAIRED.charged_idle_turns(g, info)
        self.assertEqual(r['own_turns'], 5)    # 1, 3, 5, 7, 9
        self.assertEqual((r['idle'], r['idle_ex'], r['attacked'], r['warnings']), (2, 1, 1, 0))

    def test_a_retreat_is_not_an_idle_turn(self):
        g = log_game([entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix'), entry(1, 'Place:Team Rocket\'s Rattata@1', 'Alolan Vulpix'),
                      entry(3, 'Retreat:1', 'Alolan Vulpix')], turns=3)
        r = PAIRED.charged_idle_turns(g, info)
        self.assertEqual((r['idle'], r['attacked']), (1, 0), 'turn 1 is idle; the retreat of turn 3 leaves no charged Active that skipped an attack')

    def test_a_retreat_pays_its_cost_in_energy_so_the_pokemon_that_comes_back_is_not_charged(self):
        g = log_game([entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix'), entry(1, "Place:Team Rocket's Rattata@1", 'Alolan Vulpix'),    # turn 1: Vulpix charged, idle
                      entry(3, 'Retreat:1', 'Alolan Vulpix'),                                                                            # turn 3: it retreats, paying its Energy
                      entry(5, 'Retreat:1', "Team Rocket's Rattata"),                                                                    # turn 5: it comes back
                      entry(7, 'Play:Ilima', 'Alolan Vulpix')], turns=7)                                                                 # turn 7: no Energy left, nothing to count
        self.assertEqual(PAIRED.charged_idle_turns(g, info)['idle'], 1)

    def test_a_game_that_does_not_fit_the_model_is_counted_as_a_warning(self):
        g = log_game([entry(1, 'Attach:1Fire@2 zone', 'Alolan Vulpix')], turns=1)   # an Energy for a slot the model never saw filled
        self.assertGreaterEqual(PAIRED.charged_idle_turns(g, info)['warnings'], 1)

    def test_the_opponents_first_point_is_the_opening_active_when_it_was_never_moved_or_evolved(self):
        g = log_game([entry(2, 'Attach:1Fire@0 zone', 'Alolan Vulpix'), entry(4, 'Attach:1Fire@0 zone', 'Alolan Vulpix'),
                      entry(5, 'Promote:0@1', '', p=(0, 1))], first='opp', points=(0, 1))
        f = PAIRED.first_point(g)
        self.assertEqual((f['opening'], f['scored'], f['opening_ko']), ('Alolan Vulpix', True, True))

    def test_a_first_point_taken_after_the_opening_active_evolved_or_retreated_is_not_the_opening_active(self):
        evolved = log_game([entry(2, 'Evolve:Alolan Ninetales ex@0', 'Alolan Vulpix'), entry(4, 'Promote:0@1', '', p=(0, 2))], first='opp', points=(0, 2))
        retreated = log_game([entry(2, 'Retreat:1', 'Alolan Vulpix'), entry(4, 'Promote:0@1', '', p=(0, 1))], first='opp', points=(0, 1))
        for g in (evolved, retreated):
            f = PAIRED.first_point(g)
            self.assertEqual((f['scored'], f['opening_ko']), (True, False), g)

    def test_a_game_the_opponent_never_scored_in_has_no_first_point(self):
        f = PAIRED.first_point(log_game([entry(2, 'Attach:1Fire@0 zone', 'Alolan Vulpix')], first='opp'))
        self.assertEqual((f['scored'], f['opening_ko']), (False, False))

    def test_a_game_without_a_log_is_not_counted_at_all(self):
        self.assertIsNone(PAIRED.first_point({'first': 'deck', 'turns': 4, 'points': [0, 0]}))
        self.assertIsNone(PAIRED.charged_idle_turns({'first': 'deck', 'turns': 4, 'points': [0, 0]}, info))

    def test_a_switch_of_the_opponents_board_does_not_move_our_pokemon(self):
        # seat 0: Activate:1@2 is our Cyrus bringing up the OPPONENT's benched Pokemon 2; Activate:0@1 is a switch of our own board
        base = [entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix'), entry(1, "Place:Team Rocket's Rattata@1", 'Alolan Vulpix')]
        theirs = log_game(base + [entry(3, 'Activate:1@2', 'Alolan Vulpix'), entry(3, 'Play:Ilima', 'Alolan Vulpix')], turns=3)
        theirs['seat'] = 0
        ours = log_game(base + [entry(3, 'Activate:0@1', 'Alolan Vulpix'), entry(3, 'Play:Ilima', "Team Rocket's Rattata")], turns=3)
        ours['seat'] = 0
        # the opponent's switch leaves our charged Vulpix in front (idle again on turn 3); our own switch puts the uncharged Rattata there
        self.assertEqual(PAIRED.charged_idle_turns(theirs, info)['idle'], 2)
        self.assertEqual(PAIRED.charged_idle_turns(ours, info)['idle'], 1)

    def test_the_opponents_switch_does_not_spoil_the_opening_active_but_our_own_switch_does(self):
        log = [entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix'), entry(1, "Place:Team Rocket's Rattata@1", 'Alolan Vulpix'), entry(3, 'Activate:1@1', 'Alolan Vulpix'),
               entry(4, 'Promote:0@1', '', p=(0, 1))]
        ours_is_seat_1 = log_game(log, first='deck', points=(0, 1))
        ours_is_seat_1['seat'] = 1            # Activate:1 names seat 1, which is us: our own Benched Pokémon came up, so the opening Active had moved
        theirs = log_game(log, first='deck', points=(0, 1))
        theirs['seat'] = 0                    # Activate:1 names seat 1, the opponent: our board did not change
        self.assertTrue(PAIRED.first_point(theirs, info)['opening_ko'])
        self.assertFalse(PAIRED.first_point(ours_is_seat_1, info)['opening_ko'])

    def test_an_attach_of_several_energy_counts_them_all_and_several_parts_each_count(self):
        g = log_game([entry(1, 'Attach:2Fire@0 zone', 'Alolan Ninetales ex')], turns=1)
        self.assertEqual(PAIRED.charged_idle_turns(g, info)['idle_ex'], 1, '2 Energy pay for the 2-Energy attack')
        g = log_game([entry(1, 'Place:Alolan Vulpix@1', 'Alolan Ninetales ex'), entry(1, 'Attach:1Fire@0+1Fire@1 fx', 'Alolan Ninetales ex')], turns=1)
        self.assertEqual(PAIRED.charged_idle_turns(g, info)['idle'], 0, 'one Energy on the ex, which needs two: not charged')

    def test_a_first_point_that_could_be_the_opening_active_or_a_benched_copy_of_it_is_counted_apart(self):
        # Rattata in front and a second Rattata on the Bench: when the opponent scores and no Promote is logged (the lone benched Pokemon steps up by itself) the name in front is the same
        g = log_game([entry(2, "Place:Team Rocket's Rattata@1", "Team Rocket's Rattata"), entry(4, 'Attach:1Fire@0 zone', "Team Rocket's Rattata"),
                      entry(6, 'Attach:1Fire@0 zone', "Team Rocket's Rattata", p=(0, 1))], first='opp', points=(0, 1))
        f = PAIRED.first_point(g, info)
        self.assertEqual((f['scored'], f['opening_ko'], f['opening_ko_maybe']), (True, False, True))
        g = log_game([entry(2, 'Attach:1Fire@0 zone', "Team Rocket's Rattata"), entry(4, 'Promote:0@1', '', p=(0, 1))], first='opp', points=(0, 1))
        f = PAIRED.first_point(g, info)
        self.assertEqual((f['opening_ko'], f['opening_ko_maybe']), (True, False))

    def test_pokemon_put_into_play_are_counted_as_played_and_a_tool_with_no_choice_to_log_is_the_difference(self):
        g = log_game([entry(1, 'Place:Alolan Vulpix@1', 'Alolan Vulpix'), entry(3, 'Evolve:Alolan Ninetales ex@1', 'Alolan Vulpix'), entry(3, 'Place:Alolan Vulpix@2', 'Alolan Vulpix'),
                      entry(3, 'Play:Giant Cape', 'Alolan Vulpix')])    # a Cape played with nothing logged after it: the engine chose its only place
        self.assertEqual(PAIRED.card_use(g, 'Alolan Vulpix', info)['played'], 2)
        self.assertEqual(PAIRED.card_use(g, 'Alolan Ninetales ex', info)['played'], 1)
        u = PAIRED.card_use(g, 'Giant Cape', info)
        self.assertEqual((u['played'], u['targets']), (1, []))

    def test_a_tool_is_traced_to_the_pokemon_it_went_to(self):
        g = log_game([entry(1, 'Place:Alolan Vulpix@2', 'Alolan Vulpix'), entry(1, 'Play:Giant Cape', 'Alolan Vulpix'), entry(1, 'Tool:Giant Cape@2', 'Alolan Vulpix'),
                      entry(3, 'Play:Giant Cape', 'Alolan Vulpix'), entry(3, 'Tool:Giant Cape@0', 'Alolan Vulpix'), entry(3, 'Play:Ilima', 'Alolan Vulpix')])
        u = PAIRED.card_use(g, 'Giant Cape', info)
        self.assertEqual((u['played'], u['turns']), (2, [1, 2]))                  # own turns: global turn 1 is our 1st, 3 is our 2nd
        self.assertEqual(sorted(u['targets']), [('Alolan Vulpix', 'Active'), ('Alolan Vulpix', 'Bench')])
        self.assertEqual(PAIRED.card_use(g, 'Ilima', info)['played'], 1)
        self.assertEqual(PAIRED.card_use(g, 'Big Malasada', info)['played'], 0)


# ---------------------------------------------------------------------------------------------------------- the page
def twin_games(man, deck, results, logs=None):
    """The games of a registered run as the program writes them: results maps (opp, deal, seat, arm) to 'deck' | 'opp' | 'tie' (default 'opp'); logs the same to a log."""
    out = []
    for key in sr.planned_keys(man):
        dn, opp, deal, seat, arm = key.split('|')
        t = (opp, int(deal), int(seat), arm)
        g = {'key': key, 'deck': dn, 'opp': opp, 'deal': int(deal), 'seat': int(seat), 'arm': arm, 'seed': man['seed_base'] + int(deal), 'pilot_deck': 'kx3' if arm == 'X' else 'km3',
             'pilot_opp': 'km3', 'first': 'deck' if int(seat) == 0 else 'opp', 'winner': results.get(t, 'opp'), 'points': [3, 1], 'turns': 9, 'plies': 40,
             'wall_s': 100.0 if arm == 'X' else 1.0, 'moves_deck': {'n': 2, 'total_s': 0.02, 'ms': [10.0, 10.0]}, 'moves_opp': {'n': 1, 'total_s': 0.01, 'ms': [10.0]},
             'started_at': '2026-10-11T10:00:00Z'}
        if logs is not None and t in logs:
            g['log'] = logs[t]
        out.append(g)
    return out


def put_games(d, games):
    with open(os.path.join(d, 'games.jsonl'), 'w', encoding='utf-8') as f:
        for g in games:
            f.write(json.dumps(g) + '\n')


class PairedPage(PairedWorld):
    def setUp(self):
        super().setUp()
        self.var = self.register_variant()
        self.bman, self.vman = self.manifest(self.base), self.manifest(self.var)

    def fill(self, base_results=None, var_results=None, base_logs=None, var_logs=None):
        put_games(self.base, twin_games(self.bman, 'my-list', base_results or {}, base_logs))
        put_games(self.var, twin_games(self.vman, 'my-list-cape', var_results or {}, var_logs))

    def page(self, **kw):
        return sr.write_slow_report(self.var, card_info=info, **kw)

    def test_the_difference_is_the_variants_score_minus_the_bases_on_the_same_deals_with_a_t_range(self):
        wins = {('t-altaria', 0, 0, 'X'): 'deck', ('t-altaria', 1, 1, 'X'): 'deck', ('t-blaziken', 0, 0, 'X'): 'deck', ('t-blaziken', 1, 0, 'X'): 'deck'}
        self.fill(var_results=wins)
        text = self.page()
        d = [1.0] * 4 + [0.0] * 28
        half = sr.t_crit(31) * statistics.stdev(d) / 32 ** 0.5
        self.assertIn('## Compared with the base report', text)
        self.assertIn(sr.range_points(0.125, half), text)
        self.assertIn('+12.5', text)
        self.assertRegex(text, r'\| kx3 \| 32 \| 0\.0% \| 12\.5% \|')                      # paired games, base score, this deck's score
        row = re.search(r'\| t-altaria \|[^\n]*', text).group(0)
        self.assertIn('+50.0', row)                                                         # 2 wins of 4 games v 0 of 4

    def test_the_km3_baseline_games_are_compared_too(self):
        self.fill(base_results={('t-suicune', 0, 0, 'ref'): 'deck'}, var_results={})
        text = self.page()
        self.assertRegex(text, r'\| km3 \| 32 \| 3\.1% \| 0\.0% \|')
        self.assertIn('-3.1', text)

    def test_twin_games_that_ended_alike_and_differently_are_counted(self):
        self.fill(var_results={('t-altaria', 0, 0, 'X'): 'deck', ('t-altaria', 1, 0, 'X'): 'tie'},
                  base_results={('t-altaria', 1, 0, 'X'): 'tie', ('t-weezing', 0, 0, 'X'): 'deck'})
        text = self.page()
        self.assertIn('30 of the 32 kx3 twins ended the same way', text)

    def test_games_missing_on_either_side_are_left_out_of_the_pairs_and_the_page_says_so(self):
        put_games(self.base, twin_games(self.bman, 'my-list', {})[:20])
        put_games(self.var, twin_games(self.vman, 'my-list-cape', {})[10:30])
        text = self.page()
        self.assertIn('PARTIAL', text)
        self.assertRegex(text, r'(?i)only games played in both reports are compared')
        self.assertIn('10 of the 20 games of this report have a twin', text)

    def test_a_missing_base_folder_is_said_not_crashed_on(self):
        import shutil
        self.fill()
        shutil.rmtree(self.base)
        text = self.page()
        self.assertIn('## Compared with the base report', text)
        self.assertIn('not here', text)
        self.assertIn('# Slow report: my-list-cape', text)

    def test_a_base_whose_registration_changed_is_not_compared(self):
        self.fill()
        with open(os.path.join(self.base, 'manifest.json'), 'a') as f:
            f.write(' ')
        text = self.page()
        self.assertIn('registration has changed', text)
        self.assertNotIn('| kx3 | 32 |', text)

    def test_what_was_run_names_the_base_the_shared_seeds_and_the_shuffle_slot(self):
        self.fill()
        text = self.page()
        self.assertIn(f'Paired with `{self.base_rel}`', text)
        self.assertIn('same seeds', text)
        self.assertIn('card 5 of 20', text)
        self.assertIn('the deals differ only in that card', text)

    def test_a_page_of_an_unpaired_run_has_no_comparison_section(self):
        self.fill()
        text = sr.write_slow_report(self.base, card_info=info)
        self.assertNotIn('Compared with the base report', text)

    def test_the_card_counts_come_from_the_logs_and_the_ones_the_records_cannot_give_are_named(self):
        cape = [entry(1, 'Place:Alolan Vulpix@2', 'Alolan Vulpix'), entry(1, 'Play:Giant Cape', 'Alolan Vulpix'), entry(1, 'Tool:Giant Cape@2', 'Alolan Vulpix')]
        cape0 = [entry(1, 'Play:Giant Cape', 'Alolan Vulpix'), entry(1, 'Tool:Giant Cape@0', 'Alolan Vulpix')]
        ilima = [entry(1, 'Play:Ilima', 'Alolan Vulpix')]
        self.fill(var_logs={('t-altaria', 0, 0, 'X'): cape, ('t-altaria', 1, 0, 'X'): cape0, ('t-blaziken', 0, 0, 'X'): cape0},
                  base_logs={('t-altaria', 0, 0, 'X'): ilima})
        text = self.page()
        self.assertRegex(text, r'Giant Cape played \| 0 times in 0 of 32 games \| 3 times in 3 of 32 games')
        self.assertIn('Active Pokémon 2', text)
        self.assertIn('Benched Pokémon 1', text)
        self.assertRegex(text, r'Giant Cape went to \| [^\n]*Alolan Vulpix 3')
        self.assertIn('Ilima played', text)
        self.assertIn('survived an attack it would not have survived without the +20', text)
        self.assertIn('no Hit Points', text)

    def test_the_idle_charged_turns_and_the_opening_active_counts_are_tabled_for_both_pilots(self):
        idle = [entry(1, 'Attach:1Fire@0 zone', 'Alolan Vulpix')]
        self.fill(base_logs={('t-altaria', 0, 0, 'X'): idle, ('t-altaria', 1, 0, 'X'): idle}, var_logs={('t-altaria', 0, 0, 'X'): idle})
        text = self.page()
        self.assertRegex(text, r'turns a charged Pokémon did not attack, all lists \| 2 \| 1 \|')
        self.assertRegex(text, r'turns a charged Pokémon did not attack, against t-altaria \| 2 \| 1 \|')
        self.assertIn('indicator', text)
        self.assertIn('Sleep is not recorded', text)


class PairedPageForTheBigMalasada(PairedWorld):
    def test_big_malasada_rows_and_notes_appear_when_it_is_in_the_diff(self):
        mal = os.path.join(self.repo, 'decks', 'events', 'my-list-mal.txt')
        write(mal, CAPE_DECK.replace('Giant Cape A2 147', 'Big Malasada A3 142'))
        d = self.register_variant(variant=mal, date='2026-10-12')
        d = os.path.join(self.out_root, '2026-10-12_my-list-mal')
        vman, bman = self.manifest(d), self.manifest(self.base)
        plays = [entry(1, 'Play:Big Malasada', 'Alolan Vulpix')]
        put_games(self.base, twin_games(bman, 'my-list', {}))
        put_games(d, twin_games(vman, 'my-list-mal', {}, {('t-altaria', 0, 0, 'X'): plays, ('t-altaria', 0, 1, 'X'): plays}))
        text = sr.write_slow_report(d, card_info=info)
        self.assertRegex(text, r'Big Malasada played \| 0 times in 0 of 32 games \| 2 times in 2 of 32 games')
        self.assertIn('which Special Condition it removed', text)
        self.assertIn('not recorded', text)
        self.assertNotIn('Giant Cape', text)


class PairedPageDetails(PairedWorld):
    def setUp(self):
        super().setUp()
        self.var = self.register_variant()
        self.bman, self.vman = self.manifest(self.base), self.manifest(self.var)

    def page(self, base_logs=None, var_logs=None, var_edit=None, base_edit=None):
        bg, vg = twin_games(self.bman, 'my-list', {}, base_logs), twin_games(self.vman, 'my-list-cape', {}, var_logs)
        for g in vg:
            if var_edit:
                var_edit(g)
        put_games(self.base, bg)
        put_games(self.var, vg)
        return sr.write_slow_report(self.var, card_info=info)

    def test_a_tool_played_without_a_logged_choice_is_shown_as_such_not_as_missing(self):
        chosen = [entry(1, 'Place:Alolan Vulpix@1', 'Alolan Vulpix'), entry(1, 'Play:Giant Cape', 'Alolan Vulpix'), entry(1, 'Tool:Giant Cape@1', 'Alolan Vulpix')]
        forced = [entry(1, 'Play:Giant Cape', 'Alolan Vulpix')]
        text = self.page(var_logs={('t-altaria', 0, 0, 'X'): chosen, ('t-altaria', 1, 0, 'X'): forced, ('t-blaziken', 0, 0, 'X'): forced})
        self.assertRegex(text, r'Giant Cape played \| 0 times in 0 of 32 games \| 3 times in 3 of 32 games')
        self.assertRegex(text, r'Giant Cape went to \| [^\n]*Benched Pokémon 1')
        self.assertRegex(text, r'Giant Cape put on with only one place to put it, so nothing to log \| 0 \| 2 \|')
        self.assertNotRegex(text, r'Ilima put on with only one place')     # a card that is never a Tool has no such row

    def test_a_swap_that_changes_what_a_hand_can_hold_says_the_opponents_deal_and_the_first_player_can_differ_too(self):
        text = self.page()
        self.assertIn('who went first was the same in all 32 kx3 twins', text.replace('Who', 'who'))
        text = self.page(var_edit=lambda g: g.update(first='opp' if g['first'] == 'deck' else 'deck') if (g['opp'], g['deal'], g['seat'], g['arm']) == ('t-altaria', 0, 0, 'X') else None)
        self.assertRegex(text, r'(?i)who went first differed in 1 of the 32 kx3 twins')
        self.assertIn('the opponent', PAIRED.basic_text({'basic_shape': False}))
        self.assertIn('first player', PAIRED.basic_text({'basic_shape': False}))

    def test_twins_with_other_turns_or_plies_are_not_the_same_game(self):
        text = self.page(var_edit=lambda g: g.update(turns=g['turns'] + 1) if g['arm'] == 'X' and g['opp'] == 't-altaria' and g['deal'] == 0 else None,
                         base_logs={('t-altaria', 0, 0, 'X'): [entry(1, 'Play:Ilima', 'Alolan Vulpix')], ('t-altaria', 0, 1, 'X'): [entry(1, 'Play:Ilima', 'Alolan Vulpix')]},
                         var_logs={('t-altaria', 0, 0, 'X'): [entry(1, 'Play:Ilima', 'Alolan Vulpix')], ('t-altaria', 0, 1, 'X'): [entry(1, 'Play:Ilima', 'Alolan Vulpix')]})
        # only the twins with a log on both sides can be told apart (2 of the 32 here); with turns and plies compared, the two edited ones are not the same game
        self.assertIn('of the 2 with a log on both sides, 0 were the same game from start to finish', text)

    def test_a_program_that_changed_during_the_variants_run_is_flagged_in_the_comparison(self):
        put_games(self.base, twin_games(self.bman, 'my-list', {}))
        put_games(self.var, twin_games(self.vman, 'my-list-cape', {}))
        with mock.patch.object(sr, 'is_program_change', return_value=True):
            write(os.path.join(self.var, 'slow_report_log.jsonl'), json.dumps(T.change_event_for(self.vman, 'b' * 64)) + '\n')
            text = sr.write_slow_report(self.var, card_info=info)
        self.assertIn('the program changed 1 time during this run', text)
        self.assertEqual(PAIRED.program_changes(self.var, self.vman), 0, 'without the mock the line is no valid change event')

    def test_the_first_point_row_has_a_row_for_the_cases_that_cannot_be_told_apart(self):
        ambiguous = [entry(2, "Place:Team Rocket's Rattata@1", "Team Rocket's Rattata"), entry(6, 'Attach:1Fire@0 zone', "Team Rocket's Rattata", p=(0, 1))]
        text = self.page(var_logs={('t-altaria', 0, 1, 'X'): ambiguous}, var_edit=lambda g: g.update(points=[0, 1]) if g['key'].endswith('t-altaria|0|1|X') else None)
        self.assertRegex(text, r"the opponent's first point was the opening Pokémon or a benched Pokémon of the same name \(cannot be told apart\) \| 0 \| 1 \|")


class PairedPageIsRobust(PairedWorld):
    def test_a_game_record_the_replay_cannot_read_is_counted_as_having_no_log_and_never_stops_the_page(self):
        self.var = self.register_variant()
        bman, vman = self.manifest(self.base), self.manifest(self.var)
        broken = [{'t': 1, 'a': 'Play:Ilima'}]    # no 'act', no 'p': not a line the program writes
        put_games(self.base, twin_games(bman, 'my-list', {}, {('t-altaria', 0, 0, 'X'): broken}))
        put_games(self.var, twin_games(vman, 'my-list-cape', {}, {('t-altaria', 0, 0, 'X'): broken}))
        text = sr.write_slow_report(self.var, card_info=info)
        self.assertIn('## Compared with the base report', text)
        self.assertIn('### What the change did to the score', text)

    def test_a_failure_in_the_comparison_leaves_the_rest_of_the_page_and_says_so(self):
        self.var = self.register_variant()
        put_games(self.base, twin_games(self.manifest(self.base), 'my-list', {}))
        put_games(self.var, twin_games(self.manifest(self.var), 'my-list-cape', {}))
        with mock.patch.object(PAIRED, 'job_lines', side_effect=RuntimeError('boom')):
            text = sr.write_slow_report(self.var, card_info=info)
        self.assertIn('## Compared with the base report', text)
        self.assertIn('could not be completed: RuntimeError: boom', text)
        self.assertIn('## Against each public list', text)
        self.assertIn('## What was run', text)

    def test_a_base_folder_given_by_an_absolute_path_is_found_where_it_is(self):
        rec = {'folder': self.base}
        self.assertEqual(PAIRED.locate_base(os.path.join(self.tmp, 'elsewhere', 'run'), rec), self.base)

    def test_the_console_summary_of_a_variant_is_the_score_change_lines(self):
        self.var = self.register_variant()
        put_games(self.base, twin_games(self.manifest(self.base), 'my-list', {}))
        put_games(self.var, twin_games(self.manifest(self.var), 'my-list-cape', {}, None))
        text = sr.write_slow_report(self.var, card_info=info)
        lines = PAIRED.console_summary(text)
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith('compared with the base report: kx3: ') and 'points on the same deals' in lines[0], lines)
        self.assertTrue(lines[1].startswith('compared with the base report: km3: '), lines)
        self.assertNotIn('**', ''.join(lines))
        self.assertEqual(PAIRED.console_summary('# Slow report: x\n'), [])


class DocsAndTests(unittest.TestCase):
    def test_the_readme_names_the_paired_mode_and_this_test_file(self):
        readme = read(os.path.join(HERE, 'README.md'))
        self.assertIn('--paired-with', readme)
        self.assertIn('test_slow_report_paired', readme)
        self.assertIn('slow_report_paired.py', readme)

    def test_the_module_says_how_to_use_it(self):
        self.assertIn('--paired-with', sr.__doc__)


if __name__ == '__main__':
    unittest.main()
