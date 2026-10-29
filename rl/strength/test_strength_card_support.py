#!/usr/bin/env python3
"""The card-support refusal of the strength program (src/main.rs, `run` and `selfcheck`), which is the slow report's refusal: before any game, a deck that holds
a card the engine cannot play (card_status CardNotFound or Missing*) stops the program with exit 2 and the message `deckgym simulate` gives, through the
engine's one shared check (deckgym::card_support); --allow-unsupported-cards lists the card on stderr and goes on.

  STRENGTH_PROGRAM=/path/to/strength python3 -B -m unittest -v test_strength_card_support     (from rl/strength/)

It runs a REAL program: one built from this checkout's harness against an engine that has deckgym::card_support (rl/strength/build.sh ENGINE_DIR_OR_REF OUT;
at R6, the kx3 rebuild). Without STRENGTH_PROGRAM every test is skipped, and says so. No game is played: a refused run stops before any, and the others are
given --max-games 0 or --games 0.

The card is C1 019 Volcanion, a Basic whose only attack, Dynamite Steam ("Flip 2 coins. This attack does 110 damage for each heads."), has no entry in the
engine's EFFECT_MECHANIC_MAP (it has the 2-coin texts for 20 to 100 damage, not 110), so card_status gives MissingAttack (the release lane's card_status at
d0792568). The deck is engine/example_decks/venusaur-exeggutor.txt with its Red Card swapped for it: still a legal 20-card deck, so only the card-support
check can refuse it.
"""
import json, os, shutil, subprocess, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PROGRAM = os.environ.get('STRENGTH_PROGRAM')
SUPPORTED = os.path.join(ROOT, 'engine', 'example_decks', 'venusaur-exeggutor.txt')
RED_CARD = '1 Red Card P-A 006'
BLOCKED_CARD = '1 Volcanion C1 019'
LISTED = 'C1 019 — Volcanion — Attack effect not implemented'
FLAG = '--allow-unsupported-cards'


@unittest.skipUnless(PROGRAM, 'set STRENGTH_PROGRAM to a strength program built from this checkout (rl/strength/build.sh) to run these')
class StrengthCardSupport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='strength_card_support_')
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        with open(SUPPORTED, encoding='utf-8') as f:
            supported = f.read()
        self.assertIn(RED_CARD, supported)
        self.ok_deck = self.write('supported.txt', supported)
        self.blocked_deck = self.write('blocked.txt', supported.replace(RED_CARD, BLOCKED_CARD, 1))

    def write(self, name, text):
        path = os.path.join(self.tmp, name)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(text)
        return path

    def manifest(self, tag, deck, opponent):
        """A run folder (empty) and a manifest with one deck and one opponent, 1 deal in seat 0: two games in the plan, none of them played here."""
        out = os.path.join(self.tmp, f'run_{tag}')
        os.makedirs(out)
        man = {'repo_root': self.tmp, 'pilot': 'r', 'reference': 'r', 'decks': [{'name': 'under_test', 'path': deck}],
               'opponents': [{'name': 'panel_list', 'path': opponent}], 'deals': 1, 'seats': [0], 'seed_base': 1, 'threads': 1, 'log_level': 'none'}
        path = os.path.join(self.tmp, f'manifest_{tag}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(man, f)
        return path, out

    def program(self, *args):
        return subprocess.run([PROGRAM, *args], stdin=subprocess.DEVNULL, capture_output=True, encoding='utf-8', errors='replace', timeout=300)

    def test_run_refuses_a_deck_or_an_opponent_with_a_missing_attack_card_and_writes_nothing(self):
        for tag, deck, opponent, used_by in (('deck', self.blocked_deck, self.ok_deck, 'Used by: deck under_test ('),
                                             ('opponent', self.ok_deck, self.blocked_deck, 'Used by: opponent panel_list (')):
            with self.subTest(blocked=tag):
                man, out = self.manifest(tag, deck, opponent)
                r = self.program('run', '--manifest', man, '--out', out)
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertIn('Card-support preflight failed; strength run did not start.', r.stderr)
                self.assertIn(LISTED, r.stderr)
                self.assertIn(used_by, r.stderr)
                self.assertIn(FLAG, r.stderr, 'the refusal says how to opt out')
                self.assertNotIn('panicked at', r.stderr)
                self.assertEqual(os.listdir(out), [], 'a refused run writes nothing in its folder (no games.jsonl, errors.jsonl or run_log.jsonl)')

    def test_run_with_the_opt_out_lists_the_card_on_stderr_and_starts(self):
        man, out = self.manifest('allowed', self.blocked_deck, self.ok_deck)
        r = self.program('run', '--manifest', man, '--out', out, '--max-games', '0', FLAG)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn(f'{FLAG} was given', r.stderr)
        self.assertIn(LISTED, r.stderr)
        self.assertIn('Used by: deck under_test (', r.stderr)
        self.assertNotIn('preflight failed', r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(out, 'run_log.jsonl')), 'the run started')

    def test_supported_decks_start_and_the_check_says_nothing(self):
        man, out = self.manifest('supported', self.ok_deck, self.ok_deck)
        r = self.program('run', '--manifest', man, '--out', out, '--max-games', '0')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('Card-support preflight', r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(out, 'run_log.jsonl')))

    def test_selfcheck_refuses_too_and_prints_no_selfcheck_line(self):
        r = self.program('selfcheck', '--pilot', 'r', '--deck-a', self.blocked_deck, '--deck-b', self.ok_deck, '--games', '0')
        self.assertEqual(r.returncode, 2, r.stderr)
        self.assertIn('Card-support preflight failed; strength selfcheck did not start.', r.stderr)
        self.assertIn(LISTED, r.stderr)
        self.assertIn('Used by: deck A (', r.stderr)
        self.assertNotIn('selfcheck pilot=', r.stdout)


if __name__ == '__main__':
    unittest.main()
