#!/usr/bin/env python3
"""The card-support refusal of the strength program (src/main.rs, `run` and `selfcheck`), which is the slow report's refusal: before any game, a deck that holds
a card the engine cannot play (card_status CardNotFound or Missing*) stops the program with exit 2 and the message `deckgym simulate` gives, through the
engine's one shared check (deckgym::card_support); --allow-unsupported-cards lists the card on stderr and goes on.

  STRENGTH_PROGRAM=/path/to/strength python3 -B -m unittest -v test_strength_card_support     (from rl/strength/)

It runs a REAL program: one built from this checkout's harness against an engine that has deckgym::card_support, WITH the engine's test-utils feature (see
the card below). rl/strength/build.sh builds without it, as the slow report's programs must be, so build this one by hand the way build.sh does, from the
checkout's root (the folder B is yours to pick; the program is B/rl/strength/target/release/strength, or under CARGO_TARGET_DIR if that is set):
  mkdir -p B/rl/strength && cp -r engine B/ && cp -r rl/strength/src rl/strength/Cargo.toml B/rl/strength/ && cp engine/Cargo.lock B/rl/strength/
  (cd B/rl/strength && nice -n 19 cargo build --release --offline --features deckgym/test-utils)
A program built without the feature starts the refused runs (the refusal tests then fail and say why). Without STRENGTH_PROGRAM every test is skipped, and
says so. No game is played: a refused run stops before any, and the others are given --max-games 0 or --games 0.

The card is A1 008 Weedle, a Basic whose only attack, Sting, has no effect text, so the engine plays it. It is refused because every run here names it in
TEST_CARD_SUPPORT_MISSING_ATTACK: an engine built with test-utils reads that variable (deckgym::card_support) and inspects the printings it names as
MissingAttack. A real refused printing would not last: R8 implements the last 55 (this test used C1 019 Volcanion before). The deck is
engine/example_decks/venusaur-exeggutor.txt with its Red Card swapped for it: still a legal 20-card deck, so only the card-support check can refuse it.
"""
import json, os, shutil, subprocess, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PROGRAM = os.environ.get('STRENGTH_PROGRAM')
SUPPORTED = os.path.join(ROOT, 'engine', 'example_decks', 'venusaur-exeggutor.txt')
RED_CARD = '1 Red Card P-A 006'
MISSING_ATTACK_ENV = 'TEST_CARD_SUPPORT_MISSING_ATTACK'   # deckgym::card_support::TEST_MISSING_ATTACK_ENV, read only with test-utils
BLOCKED_ID = 'A1 008'
BLOCKED_CARD = f'1 Weedle {BLOCKED_ID}'
LISTED = f'{BLOCKED_ID} — Weedle — Attack effect not implemented'
FLAG = '--allow-unsupported-cards'
NO_TEST_UTILS = f'(a program built without the engine test-utils feature does not read {MISSING_ATTACK_ENV}: build it as the top of this file says)'


@unittest.skipUnless(PROGRAM, 'set STRENGTH_PROGRAM to a strength program built from this checkout with the engine test-utils feature (the top of this file says how) to run these')
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
        env = {**os.environ, MISSING_ATTACK_ENV: BLOCKED_ID}
        return subprocess.run([PROGRAM, *args], stdin=subprocess.DEVNULL, capture_output=True, encoding='utf-8', errors='replace', timeout=300, env=env)

    def test_run_refuses_a_deck_or_an_opponent_with_a_missing_attack_card_and_writes_nothing(self):
        for tag, deck, opponent, used_by in (('deck', self.blocked_deck, self.ok_deck, 'Used by: deck under_test ('),
                                             ('opponent', self.ok_deck, self.blocked_deck, 'Used by: opponent panel_list (')):
            with self.subTest(blocked=tag):
                man, out = self.manifest(tag, deck, opponent)
                r = self.program('run', '--manifest', man, '--out', out)
                self.assertEqual(r.returncode, 2, f'{r.stderr}\n{NO_TEST_UTILS}')
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
        self.assertIn(f'{FLAG} was given', r.stderr, NO_TEST_UTILS)
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
        self.assertEqual(r.returncode, 2, f'{r.stderr}\n{NO_TEST_UTILS}')
        self.assertIn('Card-support preflight failed; strength selfcheck did not start.', r.stderr)
        self.assertIn(LISTED, r.stderr)
        self.assertIn('Used by: deck A (', r.stderr)
        self.assertNotIn('selfcheck pilot=', r.stdout)


if __name__ == '__main__':
    unittest.main()
