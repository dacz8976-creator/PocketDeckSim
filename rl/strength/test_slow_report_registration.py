#!/usr/bin/env python3
"""Tests of the registration side of the slow report: which decks the wrapper and strength_prereg.py recognise as copies, the self-check replay, what a refused or
interrupted registration leaves behind, what the registration records, and the places where git decides what the page says.

  cd rl/strength && python3 -B -m unittest -v test_slow_report_registration

Written after the second adversarial review (findings M2-09, M2-10, M2-17, M2-21, M2-25, M2-29, M2-30, M2-32, M2-33, M2-36); each test below was checked against the
mutant it targets (the mutant is applied to a private copy and the test must fail on it). A copy of a deck is a deck with the same cards (the Energy line is not compared);
the registered question depends on whether the comparison with the baseline pilot is asked for, and says one deal, not 1 deals. Everything runs on the World of test_slow_report.py: a temporary repository
with its own synthetic registry (8 panel lists, 3 held-out decks), the fake program and a pin that names it.

What reads live data, on purpose, and only in LiveRepositoryData and LiveRegistryEndToEnd (which uses the LiveWorld fixture): START_HERE.md, the real decks.json,
groups.json and heldout.json, the real panel and held-out files, and the real deck validator lib/deck_check.py with its card database. Everything else here is synthetic.
"""
import contextlib, datetime, io, json, os, re, shlex, shutil, subprocess, sys, tempfile, unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import slow_report as sr  # noqa: E402
import strength_prereg as P  # noqa: E402
import test_slow_report as T  # noqa: E402

read, write, write_bytes, sha, jsonl, chi = T.read, T.write, T.write_bytes, T.sha, T.jsonl, T.chi
PANEL, HELD, PANEL_TEXT, HELD_TEXT = T.PANEL, T.HELD, T.PANEL_TEXT, T.HELD_TEXT
UTC = datetime.timezone.utc
BLOCK_START = T.BLOCK[0]
REPLAYED = 'replayed by slow_report.py just before registration (equal to the pin)'


def tree(root):
    """{path relative to root: bytes} of every file under root (empty when root is not there)."""
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            with open(os.path.join(dp, f), 'rb') as fh:
                out[os.path.relpath(os.path.join(dp, f), root)] = fh.read()
    return out


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', *args], check=True, capture_output=True, text=True)


# ---------------------------------------------------------------------------------------------------------- copies of a deck
CARD = re.compile(r'^(\d+) (.+) (\S+) (\S+)$', re.M)


def with_heading_lines(text):
    lines = text.split('\n')
    lines.insert(1, 'Pokémon: 8')
    lines.insert(len(lines) // 2, 'Trainer: 12')
    return '\n'.join(lines)


def odd_white_space_in_every_name(ch):
    return lambda t: CARD.sub(lambda m: f'{m.group(1)} {m.group(2)[:1]}{ch}{m.group(2)[1:]} {m.group(3)} {m.group(4)}', t).encode()


# Each form is a way a deck gets re-saved or re-typed that the engine reads as the very same list (it reads, per card line, the count and the last two words, the set and
# the number padded to three digits; the printed name, the case, the heading lines, the line order and the Energy line do not matter: with no Energy line the engine derives
# the Energy types from the cards, so a copy with another Energy line, or none, is the same list; a line ends at a line feed only and a word at any Unicode white space).
COPIES = {
    'CRLF line ends': lambda t: t.replace('\n', '\r\n').encode(),
    'a byte order mark': lambda t: b'\xef\xbb\xbf' + t.encode(),
    'accents folded to ASCII': lambda t: t.replace('é', 'e').encode(),
    'every card respelled': lambda t: CARD.sub(r'\1 Spelled Differently \3 \4', t).encode(),
    'Pokémon and Trainer heading lines': lambda t: with_heading_lines(t).encode(),
    'numbers without their leading zeros': lambda t: re.sub(r' 0+(\d)$', r' \1', t, flags=re.M).encode(),
    'Energy line without a space': lambda t: t.replace('Energy: ', 'Energy:').encode(),
    'set codes in lower case': lambda t: CARD.sub(lambda m: f'{m.group(1)} {m.group(2)} {m.group(3).lower()} {m.group(4)}', t).encode(),
    'lines in another order': lambda t: ('\n'.join(reversed(t.strip().split('\n'))) + '\n').encode(),
    'the Energy line removed': lambda t: re.sub(r'^Energy:.*\n', '', t, flags=re.M).encode(),
    'another Energy type': lambda t: re.sub(r'^Energy: (\w+)', lambda m: 'Energy: ' + ('Metal' if m.group(1) != 'Metal' else 'Fire'), t, flags=re.M).encode(),
    'more Energy types': lambda t: re.sub(r'^Energy: ', 'Energy: Metal, Dragon, ', t, flags=re.M).encode(),
    'an Energy line with no type': lambda t: re.sub(r'^Energy:.*$', 'Energy:', t, flags=re.M).encode(),
    'no-break spaces between the words': lambda t: t.replace(' ', '\xa0').encode(),
    'form feeds between the words': lambda t: t.replace(' ', '\x0c').encode(),
    'a form feed inside every printed name': odd_white_space_in_every_name('\x0c'),
    'a vertical tab inside every printed name': odd_white_space_in_every_name('\x0b'),
    'a next-line character (NEL) inside every printed name': odd_white_space_in_every_name('\x85'),
    'a line separator (U+2028) inside every printed name': odd_white_space_in_every_name(' '),
    'a paragraph separator (U+2029) inside every printed name': odd_white_space_in_every_name(' '),
    'a lone carriage return inside every printed name': odd_white_space_in_every_name('\r'),
}
COPIES['all of these at once'] = lambda t: b'\xef\xbb\xbf' + with_heading_lines(CARD.sub(lambda m: f'{m.group(1)} Spelled {m.group(3).lower()} {m.group(4).lstrip("0")}',
                                                                                         t.replace('é', 'e').replace('Energy: ', 'Energy:'))).replace('\n', '\r\n').encode()


class PanelListCopies(T.World):
    """A copy of one of the 8 public panel lists is that list to the engine however it was saved. kx3 guesses its opponent from those lists, so a report on a copy would
    not be realistic: the wrapper refuses it itself. A dry run never reaches strength_prereg.py, so a refusal there can only be the wrapper's."""

    def test_a_copy_of_each_of_the_eight_lists_in_each_form_is_refused_by_the_wrapper(self):
        for list_name in PANEL:
            original = PANEL_TEXT[list_name]
            for how, make in COPIES.items():
                with self.subTest(list=list_name, copy=how):
                    data = make(original)
                    self.assertNotEqual(data, original.encode(), 'a copy that is the same bytes proves nothing')
                    write_bytes(self.deck, data)
                    code, out, err = self.cli('--deals', '1', '--dry-run')
                    self.assertNotEqual(code, 0)
                    self.assertIn(f'this deck is {list_name} (or a copy of it)', str(code))
                    self.assertNotIn('strength_prereg', str(code) + out + err)
                    self.assertFalse(os.path.exists(self.out_root))

    def test_a_list_that_differs_from_a_panel_list_by_one_card_is_not_taken_for_it(self):
        """The Energy line is not part of what makes a list that list (see COPIES): only the cards and their counts are."""
        for list_name in PANEL:
            text = PANEL_TEXT[list_name]
            changed = {'one card id': text.replace(' A1 ', ' A9 ', 1), 'one set': text.replace('1 Cyrus A2 150', '1 Cyrus A3 150'), 'one number': text.replace('1 Cyrus A2 150', '1 Cyrus A2 151'),
                       'one count': text.replace('7 Filler', '6 Filler', 1), 'one card more': text + '1 Extra Z9 001\n', 'one card less': text.replace('1 Cyrus A2 150\n', ''),
                       'a count moved from one card to another': text.replace('1 Cyrus A2 150', '2 Cyrus A2 150').replace('7 Filler', '6 Filler', 1)}
            for how, new in changed.items():
                with self.subTest(list=list_name, change=how):
                    self.assertNotEqual(new, text)
                    write(self.deck, new)
                    code, out, err = self.cli('--deals', '1', '--dry-run')
                    self.assertEqual(code, 0, str(code) + err)
                    self.assertIn('dry run: nothing written', out)

    def test_the_same_cards_under_any_energy_line_are_the_same_list_and_other_cards_under_its_energy_line_are_not(self):
        text = PANEL_TEXT['t-sceptile']
        cards = re.sub(r'^Energy:.*\n', '', text, flags=re.M)
        energy = re.search(r'^Energy:.*\n', text, flags=re.M).group(0)
        for how, line in {'its own Energy line': energy, 'another Energy type': 'Energy: Metal\n', 'two Energy types': 'Energy: Metal, Dragon\n', 'no Energy line': ''}.items():
            with self.subTest(same_cards_with=how):
                write(self.deck, line + cards)
                code, out, err = self.cli('--deals', '1', '--dry-run')
                self.assertNotEqual(code, 0)
                self.assertIn('this deck is t-sceptile (or a copy of it)', str(code))
        write(self.deck, energy + cards.replace('1 Cyrus A2 150', '1 Cyrus A2 151'))
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, str(code) + err)


class HeldOutCopies(T.World):
    """The held-out lock is about development: a held-out deck may be reported on (stage `use`, flagged, lock untouched), and a copy of one is still that deck to both
    guards, in whatever form it was saved."""

    PREREG_COPY = 'strength_prereg.py'

    def dev_registration(self, data):
        """strength_prereg.py itself, development stage, with the copy as the deck under test and the panel as the opponents."""
        write_bytes(self.deck, data)
        cfg = dict(name='t', question='q', pilot='kx3', reference='km3', stage='dev', deck_files=[self.deck_rel], opponent_groups=[self.pin['panel_group']], deals=1,
                   seed_base=BLOCK_START)
        write(os.path.join(self.tmp, 'dev_config.json'), json.dumps(cfg))
        out = os.path.join(self.tmp, 'dev_run')
        shutil.rmtree(out, ignore_errors=True)
        return subprocess.run([sys.executable, '-B', os.path.join(self.harness, self.PREREG_COPY), '--config', os.path.join(self.tmp, 'dev_config.json'), '--out', out,
                               '--repo', self.repo], capture_output=True, text=True)

    def test_a_copy_of_every_held_out_deck_is_flagged_not_refused_in_a_slow_report(self):
        for held in HELD:
            with self.subTest(held=held):
                shutil.rmtree(self.out_root, ignore_errors=True)
                write_bytes(self.deck, COPIES['all of these at once'](HELD_TEXT[held]))
                code, out, err = self.cli('--deals', '1', '--register-only')
                self.assertEqual(code, 0, str(code) + err)
                man = json.loads(read(os.path.join(self.rundir(), 'manifest.json')))
                self.assertEqual((man['stage'], man['heldout_in_run'], man['heldout_decks']), ('use', ['my-list'], []))

    def test_each_form_of_a_held_out_copy_is_flagged_in_a_slow_report(self):
        for how, make in COPIES.items():
            with self.subTest(copy=how):
                shutil.rmtree(self.out_root, ignore_errors=True)
                write_bytes(self.deck, make(HELD_TEXT[HELD[0]]))
                code, out, err = self.cli('--deals', '1', '--register-only')
                self.assertEqual(code, 0, str(code) + err)
                self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['heldout_in_run'], ['my-list'])

    def test_a_copy_of_every_held_out_deck_is_refused_by_strength_prereg_in_a_development_run(self):
        for held in HELD:
            with self.subTest(held=held):
                r = self.dev_registration(COPIES['all of these at once'](HELD_TEXT[held]))
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('is a held-out deck', r.stderr)
                self.assertFalse(os.path.exists(os.path.join(self.tmp, 'dev_run', 'manifest.json')))

    def test_each_form_of_a_held_out_copy_is_refused_by_strength_prereg_in_a_development_run(self):
        for how, make in COPIES.items():
            with self.subTest(copy=how):
                r = self.dev_registration(make(HELD_TEXT[HELD[1]]))
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('is a held-out deck', r.stderr)

    def test_a_development_run_accepts_a_deck_that_only_looks_like_a_held_out_one(self):
        """Only the cards and their counts make a deck that deck; the Energy line does not (see COPIES), so a near-copy differs in a card, a set, a number or a count."""
        text = HELD_TEXT[HELD[0]]
        for how, new in {'another card id': text.replace(' A1 ', ' A9 ', 1), 'another set': text.replace('1 Cyrus A2 150', '1 Cyrus A3 150'),
                         'another number': text.replace('1 Cyrus A2 150', '1 Cyrus A2 151'), 'another count': text.replace('7 Filler', '6 Filler', 1),
                         'one card more': text + '1 Extra Z9 001\n', 'one card less': text.replace('1 Cyrus A2 150\n', '')}.items():
            with self.subTest(change=how):
                self.assertNotEqual(new, text)
                r = self.dev_registration(new.encode())
                self.assertEqual(r.returncode, 0, r.stderr)

    def test_a_development_run_refuses_a_held_out_deck_whatever_its_energy_line_says(self):
        cards = re.sub(r'^Energy:.*\n', '', HELD_TEXT[HELD[2]], flags=re.M)
        for how, line in {'another Energy type': 'Energy: Metal\n', 'more types': 'Energy: Metal, Dragon, Fire\n', 'no Energy line': '', 'no type after it': 'Energy:\n'}.items():
            with self.subTest(energy=how):
                r = self.dev_registration((line + cards).encode())
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('my-list is a held-out deck', r.stderr)


# ---------------------------------------------------------------------------------------------------------- the self-check replay
SELFCHECK_PROGRAM = r'''#!/usr/bin/env python3
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
digests = json.load(open(os.path.join(here, 'digests.json')))
pilot = sys.argv[sys.argv.index('--pilot') + 1]
with open(os.path.join(here, 'selfcheck_calls.jsonl'), 'a') as f:
    f.write(json.dumps({'argv': sys.argv[1:], 'niced': os.environ.get('SR_NICED')}) + '\n')
if os.path.exists(os.path.join(here, 'meanwhile.json')):  # what another registration does while this replay runs (hours, for kx3)
    meanwhile = json.load(open(os.path.join(here, 'meanwhile.json')))
    for path in meanwhile.get('mkdir', []):
        os.makedirs(path, exist_ok=True)
    for path, text in meanwhile.get('write', {}).items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').write(text)
print('selfcheck pilot=%s games=12 digest=%s' % (pilot, digests[pilot]))
'''


class SelfCheckWorld(T.World):
    """A program that answers `selfcheck` with a digest per pilot taken from digests.json beside it (and logs how it was called), and a pin that holds those digests."""

    def make(self, *a, **kw):
        super().make(*a, **kw)
        self.set_program(SELFCHECK_PROGRAM)
        self.pin = json.loads(read(self.pin_path))
        self.pin['selfcheck'] = {s: f'selfcheck pilot={s} games=12 digest={s}pin' for s in ('km3', 'kx3')}
        write(self.pin_path, json.dumps(self.pin))
        self.printed({'km3': 'km3pin', 'kx3': 'kx3pin'})
        return self

    def printed(self, digests):
        write(os.path.join(self.tmp, 'digests.json'), json.dumps(digests))

    def calls(self):
        return jsonl(os.path.join(self.tmp, 'selfcheck_calls.jsonl'))


class SelfCheckReplays(SelfCheckWorld):
    def test_a_reference_pilot_that_differs_from_the_pin_refuses_the_registration(self):
        self.printed({'km3': 'something-else', 'kx3': 'kx3pin'})
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)
        self.assertIn('self-check of km3 does not match the pin', str(code))
        self.assertIn('digest=something-else', str(code))
        self.assertFalse(os.path.exists(self.out_root), 'nothing is written')

    def test_a_pilot_that_differs_from_the_pin_refuses_it_too_and_names_it(self):
        self.printed({'km3': 'km3pin', 'kx3': 'something-else'})
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)
        self.assertIn('self-check of kx3 does not match the pin', str(code))
        self.assertFalse(os.path.exists(self.out_root))

    def test_both_pilots_are_replayed_on_the_pinned_games_at_low_priority_and_recorded_as_replayed(self):
        with mock.patch.object(sr, 'nice_prefix', lambda *a: [shutil.which('env'), 'SR_NICED=yes']):
            code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        man = json.loads(read(os.path.join(self.rundir(), 'manifest.json')))
        self.assertEqual(man['selfcheck'], {'km3': 'selfcheck pilot=km3 games=12 digest=km3pin', 'kx3': 'selfcheck pilot=kx3 games=12 digest=kx3pin'})
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED, 'kx3': REPLAYED})
        calls = self.calls()
        self.assertEqual(sorted(c['argv'][c['argv'].index('--pilot') + 1] for c in calls), ['km3', 'kx3'])
        for c in calls:
            a = c['argv']
            self.assertEqual(a[0], 'selfcheck')
            self.assertEqual(a[a.index('--games') + 1], '12')
            self.assertEqual((a[a.index('--deck-a') + 1], a[a.index('--deck-b') + 1]), (self.registry['t-altaria'], self.registry['t-suicune']), 'the pinned digests are of these two decks')
            self.assertEqual(a[a.index('--root') + 1], self.repo)
            self.assertEqual(c['niced'], 'yes', 'the replay runs at low priority, like the games')
        text = read(os.path.join(self.rundir(), 'PREREGISTRATION.md'))
        self.assertEqual(text.count('(replayed by slow_report.py just before registration and equal to the pin)'), 2, 'one line per pilot says so')
        self.assertNotIn('not replayed', text)

    def test_the_replay_is_refused_in_school_hours_before_it_starts_and_allowed_otherwise(self):
        """It plays 12 games for hours (kx3 on both sides), so the school-morning rule applies to it too."""
        for when, rule, allowed in ((chi(2026, 10, 7, 10, 0), 'on', False), (chi(2026, 10, 7, 18, 0), 'on', True), (chi(2026, 10, 10, 10, 0), 'on', True),
                                    (chi(2026, 10, 7, 10, 0), 'off', True)):
            with self.subTest(at=when.strftime('%a %H:%M'), school_rule=rule):
                self.make()
                self.clock = T.FakeClock(when)
                code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only', school=rule)
                if allowed:
                    self.assertEqual(code, 0, str(code) + err)
                    self.assertEqual(len(self.calls()), 2)
                else:
                    self.assertNotEqual(code, 0)
                    self.assertIn('it is school time', str(code))
                    self.assertIn('Wed 17:00', str(code), 'it says when the replay may start')
                    self.assertEqual(self.calls(), [], 'the program must not be called')
                    self.assertFalse(os.path.exists(self.out_root))

    def meanwhile(self, **what):
        write(os.path.join(self.tmp, 'meanwhile.json'), json.dumps(what))

    def test_a_run_folder_that_appears_while_the_replay_runs_is_not_registered_over_and_not_removed(self):
        """The replay takes hours for kx3; what was checked before it (the folder is free) is checked again after it."""
        self.meanwhile(mkdir=[self.rundir()])
        code, out, err = self.cli('--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)
        self.assertIn('appeared while the self-check ran', str(code))
        self.assertEqual(os.listdir(self.rundir()), [], "the other registration's folder is left as it is")
        self.assertEqual(os.listdir(self.out_root), ['2026-10-10_my-list'])

    def test_the_refusal_for_a_folder_that_appeared_quotes_it_for_a_shell(self):
        spaced = os.path.join(self.tmp, "my results")
        d = os.path.join(spaced, '2026-10-10_my-list')
        self.meanwhile(mkdir=[d])
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--out-root', spaced)
        self.assertNotEqual(code, 0)
        self.assertIn(f'appeared while the self-check ran; resume it with --dir {shlex.quote(d)} (or pick another --date)', str(code))

    def test_a_seed_slot_taken_while_the_replay_runs_is_not_used_and_the_next_free_one_is(self):
        first = sr.pick_seed_base(sha(self.deck), self.out_root, tuple(self.pin['seed_block']), self.pin['seed_step'])
        self.meanwhile(write={os.path.join(self.out_root, '2026-10-09_other-list', 'manifest.json'): json.dumps({'seed_base': first})})
        code, out, err = self.cli('--deals', '1', '--selfcheck', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        self.assertIn(f'seed slot {first} was taken while the self-check ran; using {first + T.STEP}', out)
        self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['seed_base'], first + T.STEP)

    def test_the_default_registration_replays_nothing(self):
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        self.assertEqual(self.calls(), [])


class WrapperRefusalsComeBeforeAnyWork(SelfCheckWorld):
    """strength_prereg.py repeats some of the wrapper's checks a moment later with similar words, and the wrapper cleans up after it, so a test that only sees 'refused'
    cannot tell the layers apart. The wrapper's own come first, before the hours-long self-check replay and before any file is written: with --selfcheck the program must
    never be called, and the words must be the wrapper's."""

    def refused_first(self, path, phrase):
        code, out, err = self.cli_path(path, '--deals', '1', '--selfcheck')
        self.assertNotEqual(code, 0)
        self.assertIn(phrase, str(code))
        self.assertNotIn('strength_prereg', str(code) + out + err, 'refused by the wrapper, not by the registration behind it')
        self.assertNotIn('self-check of', str(code), 'refused before the self-check ran')
        self.assertEqual(self.calls(), [], 'the program must not be called')
        self.assertFalse(os.path.exists(self.out_root), 'nothing is written')

    def test_a_deck_outside_the_repository(self):
        outside = os.path.join(self.tmp, 'elsewhere', 'my-list.txt')
        write(outside, T.DECK_TEXT)
        self.refused_first(outside, 'must be inside the repository')

    def test_a_symlink_that_leaves_the_repository(self):
        outside = os.path.join(self.tmp, 'elsewhere', 'real.txt')
        write(outside, T.DECK_TEXT)
        link = os.path.join(self.repo, 'decks', 'events', 'sneaky.txt')
        os.symlink(outside, link)
        self.refused_first(link, 'must be inside the repository')

    def test_a_panel_list_name_for_a_different_file(self):
        path = os.path.join(self.repo, 'decks', 'events', 't-altaria.txt')
        write(path, T.DECK_TEXT)
        self.refused_first(path, "the deck name 't-altaria' is already a different registered deck")

    def test_a_copy_of_a_panel_list(self):
        path = os.path.join(self.repo, 'decks', 'events', 'my-copy.txt')
        write_bytes(path, COPIES['all of these at once'](PANEL_TEXT['t-weezing']))
        self.refused_first(path, 'this deck is t-weezing (or a copy of it)')

    def test_a_file_name_that_is_not_filename_safe(self):
        path = os.path.join(self.repo, 'decks', 'events', 'my list (v2).txt')
        write(path, T.DECK_TEXT)
        self.refused_first(path, 'the deck file name')


# ---------------------------------------------------------------------------------------------------------- what a refused or interrupted registration leaves
FAKE_PREREG_REFUSES = '#!/usr/bin/env python3\nimport sys\nsys.exit("fake prereg: refused")\n'
FAKE_PREREG_REFUSES_AFTER_WRITING = r'''#!/usr/bin/env python3
import os, sys
out = sys.argv[sys.argv.index('--out') + 1]
open(os.path.join(out, 'manifest.json'), 'w').write('{}')
open(os.path.join(out, 'manifest.sha256'), 'w').write('0' * 64 + '  manifest.json\n')
sys.exit("fake prereg: refused after writing")
'''


class RegistrationCleanup(T.World):
    """A refused or interrupted registration removes what it made and nothing else: earlier slow reports in the same folder are evidence (hours of games), and a run
    whose registration was written is kept even when something fails afterwards."""

    def older_run(self):
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-09', date=False)
        self.assertEqual(code, 0, str(code) + err)
        return self.rundir('2026-10-09_my-list')

    def fake_prereg(self, text):
        path = os.path.join(self.tmp, 'fake_prereg.py')
        write(path, text)
        return mock.patch.object(sr, 'PREREG', path)

    def main_raising(self, exc_type):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(exc_type):
                sr.main(self.argv('--deals', '1'), now=self.clock.now, sleep=self.clock.sleep, deck_check=lambda p, r: [])

    def test_a_refused_registration_keeps_every_other_run_in_the_folder(self):
        self.older_run()
        before = tree(self.out_root)
        with self.fake_prereg(FAKE_PREREG_REFUSES):
            code, out, err = self.cli('--deals', '1')
        self.assertIn('REFUSED by strength_prereg.py', str(code))
        self.assertIn('fake prereg: refused', str(code), "the registration's own words are shown")
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertEqual(tree(self.out_root), before, 'the older run and the folder are as they were')

    def test_a_registration_refused_by_the_real_strength_prereg_keeps_the_other_runs_too(self):
        self.older_run()
        before = tree(self.out_root)
        os.remove(os.path.join(self.repo, *self.registry['t-altaria'].split('/')))  # a panel file strength_prereg.py cannot hash
        code, out, err = self.cli('--deals', '1')
        self.assertIn('REFUSED by strength_prereg.py', str(code))
        self.assertIn(f"REFUSED: the deck file of t-altaria ({self.registry['t-altaria']}) cannot be read (No such file or directory), so the held-out guard cannot compare it; "
                      'nothing was written.', str(code), "the registration's own clean refusal is shown, not a traceback")
        self.assertNotIn('Traceback', str(code))
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertEqual(tree(self.out_root), before)

    def test_a_held_out_deck_file_that_cannot_be_read_refuses_the_registration_by_name_and_leaves_nothing(self):
        """The held-out guard reads every held-out file, whatever deck the report is about: one it cannot read is a clean refusal naming the deck, never a traceback."""
        self.older_run()
        before = tree(self.out_root)
        gone = self.registry[HELD[1]]
        os.remove(os.path.join(self.repo, *gone.split('/')))
        code, out, err = self.cli('--deals', '1')
        self.assertIn('REFUSED by strength_prereg.py (nothing was written)', str(code))
        self.assertIn(f'REFUSED: the deck file of {HELD[1]} ({gone}) cannot be read (No such file or directory), so the held-out guard cannot compare it; nothing was written.', str(code))
        self.assertNotIn('Traceback', str(code))
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertEqual(tree(self.out_root), before)

    def test_an_interrupted_registration_keeps_every_other_run_in_the_folder(self):
        self.older_run()
        before = tree(self.out_root)
        with mock.patch.object(sr, 'run_prereg', side_effect=KeyboardInterrupt):
            self.main_raising(KeyboardInterrupt)
        self.assertFalse(os.path.exists(self.rundir()))
        self.assertEqual(tree(self.out_root), before)

    def test_a_registration_that_fails_after_it_wrote_its_files_still_leaves_nothing(self):
        with self.fake_prereg(FAKE_PREREG_REFUSES_AFTER_WRITING):
            code, out, err = self.cli('--deals', '1')
        self.assertIn('fake prereg: refused after writing', str(code))
        self.assertIn('nothing was written', str(code))
        self.assertFalse(os.path.exists(self.rundir()), 'the half-made run is removed')
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_failure_after_the_registration_was_written_keeps_the_registered_run(self):
        for what, exc in (('a disk error', OSError('disk full')), ('Ctrl-C', KeyboardInterrupt())):
            with self.subTest(what=what):
                self.make()
                older = self.older_run()
                with mock.patch.object(sr, 'log_event', side_effect=exc):
                    self.main_raising(type(exc))
                run = self.rundir()
                for n in ('config.json', 'manifest.json', 'manifest.sha256', 'PREREGISTRATION.md'):
                    self.assertTrue(os.path.exists(os.path.join(run, n)), n)
                man, msha = sr.load_registered(run)
                self.assertEqual(man['slow_report']['deck_name'], 'my-list', 'the registration is intact and can be resumed')
                self.assertTrue(os.path.exists(os.path.join(older, 'manifest.json')))

    def test_a_folder_that_was_already_there_is_left_and_one_this_call_made_is_removed(self):
        os.makedirs(self.out_root)
        with self.fake_prereg(FAKE_PREREG_REFUSES):
            self.cli('--deals', '1')
        self.assertTrue(os.path.isdir(self.out_root), 'an empty slow_reports folder that was there before is not this call\'s to remove')
        self.assertEqual(os.listdir(self.out_root), [])
        shutil.rmtree(self.out_root)
        with self.fake_prereg(FAKE_PREREG_REFUSES):
            self.cli('--deals', '1')
        self.assertFalse(os.path.exists(self.out_root), 'a folder this call made is removed with the run')


# ---------------------------------------------------------------------------------------------------------- what the registration records
class RegistrationRecords(T.World):
    def build(self, **kw):
        pin = json.loads(read(self.pin_path))
        args = dict(pin=pin, pin_path=self.pin_path, deck_rel=self.deck_rel, deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=5, paired=True,
                    seed_base=T.BLOCK[0], threads=2, program_sha=pin['program_sha256'], resume_command='python3 rl/strength/slow_report.py --dir X')
        args.update(kw)
        return sr.build_config(**args)

    def sittings_threads(self, d):
        argv = jsonl(os.path.join(d, 'fake_calls.jsonl'))[-1]['argv']
        return argv[argv.index('--threads') + 1]

    def test_the_thread_count_is_registered_and_a_resume_uses_it_unless_told_otherwise(self):
        d = self.register('--threads', '3')
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['threads'], 3)
        self.assertEqual(json.loads(read(os.path.join(d, 'config.json')))['threads'], 3)
        self.assertIn('Threads: 3', read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertEqual(self.cli('--dir', d, '--max-games', '2', deck=False)[0], 0)
        self.assertEqual(self.sittings_threads(d), '3', 'a resume plays with the registered thread count')
        self.assertEqual(self.cli('--dir', d, '--max-games', '2', '--threads', '1', deck=False)[0], 0)
        self.assertEqual(self.sittings_threads(d), '1', 'a count given at the resume wins for that sitting')

    def test_the_default_thread_count_is_the_pins(self):
        d = self.register()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['threads'], self.pin['threads'])

    def test_the_log_level_is_deck_in_the_config_and_the_manifest(self):
        d = self.register()
        self.assertEqual(json.loads(read(os.path.join(d, 'config.json')))['log_level'], 'deck')
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['log_level'], 'deck')
        self.assertIn('Logging: `deck`', read(os.path.join(d, 'PREREGISTRATION.md')))

    def test_timestamps_are_utc_with_a_z(self):
        self.assertEqual(sr.utc_iso(chi(2026, 10, 10, 22, 0)), '2026-10-11T03:00:00Z', 'Chicago summer time is UTC-5')
        self.assertEqual(sr.utc_iso(chi(2026, 1, 15, 12, 0)), '2026-01-15T18:00:00Z', 'Chicago winter time is UTC-6')
        self.assertEqual(sr.utc_iso(datetime.datetime(2026, 10, 11, 3, 0, tzinfo=UTC)), '2026-10-11T03:00:00Z')
        t0 = datetime.datetime.now(UTC).replace(microsecond=0)
        d = self.register()
        t1 = datetime.datetime.now(UTC)
        stamps = [json.loads(read(os.path.join(d, 'manifest.json')))['created_at'], sr.utc_iso()] + [e['at'] for e in jsonl(os.path.join(d, 'slow_report_log.jsonl'))]
        self.assertEqual(len(stamps), 3)
        for s in stamps:
            self.assertRegex(s, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
            at = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
            self.assertTrue(t0 <= at <= t1 + datetime.timedelta(seconds=1), f'{s} is not the current UTC time ({t0} .. {t1})')

    def test_a_deck_file_name_that_is_not_filename_safe_is_refused_before_anything_is_written(self):
        for bad in ('my list (v2)', '-dash', '.hidden', 'a;b', '$(x)'):
            with self.subTest(name=bad):
                self.make(deck_name=bad)
                code, out, err = self.cli('--deals', '1', '--register-only')
                self.assertNotEqual(code, 0)
                self.assertIn('the deck file name', str(code))
                self.assertFalse(os.path.exists(self.out_root))

    def test_the_pin_path_is_recorded_relative_inside_the_repository_and_as_given_outside_it(self):
        inside = os.path.join(self.repo, 'rl', 'strength', 'pin.json')
        beside = os.path.join(self.tmp, 'repo-two', 'pin.json')  # starts with the repository's path but is not inside it
        write(inside, read(self.pin_path))
        write(beside, read(self.pin_path))
        with mock.patch.object(sr, 'ROOT', self.repo):
            blocks = {p: self.build(pin_path=p)['slow_report']['pin'] for p in (inside, beside, self.pin_path)}
        self.assertEqual(blocks[inside], {'path': 'rl/strength/pin.json', 'sha256': sha(inside)})
        self.assertEqual(blocks[beside], {'path': beside, 'sha256': sha(beside)})
        self.assertEqual(blocks[self.pin_path], {'path': self.pin_path, 'sha256': sha(self.pin_path)})

    def question_config(self, deals, paired):
        pin = dict(json.loads(read(self.pin_path)), pilot='P1', reference='R1', pilot_label='P1 (lbl)', reference_label='R1 lbl', panel_label='the panel')
        return sr.build_config(pin=pin, pin_path=self.pin_path, deck_rel=self.deck_rel, deck_name='my-list', deck_sha='a' * 64, deck_state='committed', deals=deals, paired=paired,
                               seed_base=T.BLOCK[0], threads=2, program_sha=pin['program_sha256'])

    QUESTION_HEAD = ("P1 (lbl) on my-list v R1 lbl on the panel. A slow report on one deck, not development: how does my-list do when the strong, slow pilot P1 plays it against "
                     "the eight public panel lists played by R1, ")
    QUESTION_TAIL = (" Realistic knowledge: P1 plays the deck knowing its own cards; the deck is never one of the lists P1 guesses its opponent from, and the panel side is never "
                     "handed it. No pass or fail line; time per game is reported as a fact.")

    def test_the_question_is_stated_exactly_when_the_gain_over_the_baseline_is_asked(self):
        cfg = self.question_config(5, True)
        self.assertEqual(cfg['question'], self.QUESTION_HEAD + "5 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, "
                         "with 95% ranges; and how much better P1 plays this deck than R1 on the same deals." + self.QUESTION_TAIL)
        self.assertNotIn('--no-paired', cfg['question'])
        self.assertNotIn('unless', cfg['question'], 'the question says what was registered, not what could have been')

    def test_the_question_is_stated_exactly_when_the_baseline_is_left_out_of_the_page(self):
        cfg = self.question_config(5, False)
        self.assertEqual(cfg['question'], self.QUESTION_HEAD + "5 deals x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and against each list, "
                         "with 95% ranges; without the comparison with R1 on the same deals (--no-paired: the R1 games are still played, about a second each, and left out "
                         "of the page)." + self.QUESTION_TAIL)
        self.assertNotIn('how much better', cfg['question'])

    def test_the_question_and_the_summary_say_one_deal_not_1_deals(self):
        self.assertEqual(self.question_config(1, True)['question'], self.QUESTION_HEAD + "1 deal x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and "
                         "against each list, with 95% ranges; and how much better P1 plays this deck than R1 on the same deals." + self.QUESTION_TAIL)
        self.assertEqual(self.question_config(1, False)['question'], self.QUESTION_HEAD + "1 deal x 2 seats each? Primary: the deck's score (win 1, tie 1/2, loss 0) overall and "
                         "against each list, with 95% ranges; without the comparison with R1 on the same deals (--no-paired: the R1 games are still played, about a second each, "
                         "and left out of the page)." + self.QUESTION_TAIL)
        self.assertEqual(self.question_config(1, True)['slow_report']['summary'],
                         'Stage use. 1 deal x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.')
        self.assertEqual(self.question_config(5, True)['slow_report']['summary'],
                         'Stage use. 5 deals x 2 seats against each of the eight public lists. No pass or fail line; not development evidence.')

    def test_the_block_records_whether_the_comparison_was_asked_for_and_how_many_deals(self):
        for deals, paired in ((5, True), (1, False)):
            with self.subTest(deals=deals, paired=paired):
                block = self.question_config(deals, paired)['slow_report']
                self.assertIs(block['paired'], paired)
                self.assertEqual(block['deals'], deals)

    def test_a_registration_through_the_wrapper_records_the_comparison_in_the_question_the_block_and_the_plan(self):
        """The wrapper's choice (--no-paired or not) reaches the manifest, the document's question and its analysis plan, and the three agree."""
        for flag, paired in (([], True), (['--no-paired'], False)):
            with self.subTest(flags=flag):
                shutil.rmtree(self.out_root, ignore_errors=True)
                d = self.register(*flag)
                man = json.loads(read(os.path.join(d, 'manifest.json')))
                text = read(os.path.join(d, 'PREREGISTRATION.md'))
                question = text.split('## Question')[1].split('## Pilots')[0].strip()
                plan = text.split('## Analysis plan (fixed now)')[1].split('\n## ')[0]
                self.assertEqual(man['slow_report']['paired'], paired)
                self.assertEqual(man['question'], question)
                self.assertEqual(('how much better kx3 plays this deck than km3 on the same deals' in question), paired)
                self.assertEqual(('without the comparison with km3 on the same deals (--no-paired: the km3 games are still played' in question), not paired)
                self.assertIn('1 deal x 2 seats each?', question)
                self.assertEqual(('The baseline comparison is **on**' in plan), paired)
                self.assertEqual(('The baseline comparison is **off** (`--no-paired`)' in plan), not paired)

    def test_the_wrapper_echoes_the_size_of_the_registration_with_the_right_number_words(self):
        for deals, line in ((1, '(8 pairs, 1 deal x 2 seats x 2 arms)'), (2, '(8 pairs, 2 deals x 2 seats x 2 arms)')):
            with self.subTest(deals=deals):
                shutil.rmtree(self.out_root, ignore_errors=True)
                code, out, err = self.cli('--deals', str(deals), '--register-only')
                self.assertEqual(code, 0, str(code) + err)
                self.assertIn(f'pre-registered {32 * deals} games {line} in {self.rundir()}\n', out)

    def test_each_pilots_provenance_is_the_pins_for_that_pilot(self):
        pin = dict(json.loads(read(self.pin_path)), pilot_provenance='the pilot came from branch A', reference_provenance='the reference came from branch B')
        cfg = self.build(pin=pin)
        self.assertEqual((cfg['pilot_provenance'], cfg['reference_provenance']), ('the pilot came from branch A', 'the reference came from branch B'))
        write(self.pin_path, json.dumps(pin))
        d = self.register()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual((man['pilot_provenance'], man['reference_provenance']), ('the pilot came from branch A', 'the reference came from branch B'))
        text = read(os.path.join(d, 'PREREGISTRATION.md'))
        self.assertIn('`kx3` (the pilot came from branch A)', text)
        self.assertIn('`km3` (the reference came from branch B)', text)

    def test_the_resume_command_is_quoted_for_a_folder_with_a_space_in_its_path(self):
        spaced = os.path.join(self.tmp, 'my results', 'slow reports')
        code, out, err = self.cli('--deals', '1', '--register-only', '--out-root', spaced)
        self.assertEqual(code, 0, str(code) + err)
        d = os.path.join(spaced, '2026-10-10_my-list')
        recorded = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command']
        self.assertEqual(shlex.split(recorded), ['python3', 'rl/strength/slow_report.py', '--dir', d], 'pasted into a shell it is four words')
        self.assertIn(recorded, read(os.path.join(d, 'PREREGISTRATION.md')).split('## Run')[1])
        code, out, err = self.cli('--dir', d, '--dry-run', deck=False)
        self.assertEqual(code, 0, err)
        self.assertIn(shlex.quote(d), out)

    def test_every_message_that_prints_the_run_folder_to_paste_quotes_it_for_a_shell(self):
        """'already exists', 'stopped after --max-games' and 'appeared while the self-check ran' tell a person what to type next; a folder with a space or an apostrophe in
        its name must come out as one word."""
        for out_root in (os.path.join(self.tmp, 'my results', 'slow reports'), os.path.join(self.tmp, "it's here")):
            with self.subTest(out_root=out_root):
                d = os.path.join(out_root, '2026-10-10_my-list')
                self.assertNotEqual(shlex.quote(d), d, 'the folder needs quoting')
                self.assertEqual(self.cli('--deals', '1', '--register-only', '--out-root', out_root)[0], 0)
                code, out, err = self.cli('--deals', '1', '--register-only', '--out-root', out_root)
                self.assertIn(f'already exists; resume it with --dir {shlex.quote(d)} (or pick another --date)', str(code))
                code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False)
                self.assertEqual(code, 0, str(code) + err)
                self.assertIn(f'stopped after --max-games 2; resume with --dir {shlex.quote(d)}', out)

    def test_the_log_names_the_registration_the_sitting_the_end_and_the_page(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        events = [e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] != 'env_scrubbed']  # (that one appears only on a machine that has tuning variables set)
        self.assertEqual([e['event'] for e in events], ['registered', 'slice_start', 'slice_end', 'complete', 'report_written'])
        for e in events:
            self.assertEqual((e.get('pilot'), e.get('reference')), ('kx3', 'km3'), e)
            self.assertRegex(e['at'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        registered, start, end, complete, report = events
        self.assertEqual(registered['manifest_sha256'], read(os.path.join(d, 'manifest.sha256')).split()[0])
        self.assertEqual((registered['seed_base'], registered['deals'], registered['paired'], registered['threads']), (man['seed_base'], 1, True, 2))
        self.assertEqual((registered['deck_file'], registered['deck_sha256']), (self.deck_rel, sha(self.deck)))
        self.assertEqual((start['remaining_games'], start['threads']), (32, 2))
        self.assertEqual((end['returncode'], end['killed_for_school'], end['new_games']), (0, False, 32))
        self.assertEqual(complete['games'], 32)
        self.assertEqual(report['path'], os.path.join(d, 'SLOW_REPORT.md'))

    def test_a_resumed_run_names_the_deck_in_every_line_and_in_a_refusal(self):
        d = self.register()
        code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False)
        self.assertEqual(code, 0, str(code) + err)
        lines = [l for l in out.splitlines() if l.strip()]
        self.assertTrue(lines)
        for l in lines:
            self.assertTrue(l.startswith(T.HEADLINE_START + 'my-list v km3 on the public panel] '), l)
        write(self.deck, T.DECK_TEXT.replace('Torchic', 'Treecko'))
        code, out, err = self.cli('--dir', d, deck=False)
        self.assertTrue(str(code).startswith(T.HEADLINE_START + 'my-list v km3 on the public panel] REFUSED'), code)


class SeedSlotErrors(unittest.TestCase):
    def test_a_manifest_in_a_neighbouring_folder_that_cannot_be_read_or_is_not_an_object_is_skipped(self):
        with tempfile.TemporaryDirectory() as t:
            first = sr.pick_seed_base('00000001' + '0' * 56, t, T.BLOCK, T.STEP)
            for name, text in (('garbled', '{not json'), ('empty', ''), ('a list', '[1, 2]'), ('null', 'null'), ('a number', '7'), ('a string', '"seed_base"'),
                               ('a list of objects', json.dumps([{'seed_base': first + T.STEP}]))):  # (valid JSON that is not an object holds no slot)
                os.makedirs(os.path.join(t, name))
                write(os.path.join(t, name, 'manifest.json'), text)
            os.makedirs(os.path.join(t, 'older'))
            write(os.path.join(t, 'older', 'manifest.json'), json.dumps({'seed_base': first}))
            self.assertEqual(sr.pick_seed_base('00000001' + '0' * 56, t, T.BLOCK, T.STEP), first + T.STEP, 'the readable one still counts, the others are ignored')

    def test_when_every_slot_is_taken_it_refuses_instead_of_reusing_one(self):
        block = (T.BLOCK[0], T.BLOCK[0] + 2 * T.STEP - 1)  # two slots
        with tempfile.TemporaryDirectory() as t:
            for k in range(2):
                os.makedirs(os.path.join(t, f'run{k}'))
                write(os.path.join(t, f'run{k}', 'manifest.json'), json.dumps({'seed_base': block[0] + k * T.STEP}))
            with self.assertRaises(SystemExit) as cm:
                sr.pick_seed_base('ab' * 32, t, block, T.STEP)
            self.assertIn('every seed slot', str(cm.exception.code))


class ExplicitSeedBase(T.World):
    def test_a_slot_another_report_holds_is_refused_even_when_asked_for_by_number(self):
        with tempfile.TemporaryDirectory() as t:
            slot = T.BLOCK[0] + 7 * T.STEP
            os.makedirs(os.path.join(t, '2026-10-01_older'))
            write(os.path.join(t, '2026-10-01_older', 'manifest.json'), json.dumps({'seed_base': slot}))
            with self.assertRaises(SystemExit) as cm:
                sr.pick_seed_base('ab' * 32, t, T.BLOCK, T.STEP, explicit=slot)
            self.assertIn('2026-10-01_older', str(cm.exception.code), 'the refusal names the report that holds the slot')
            self.assertEqual(sr.pick_seed_base('ab' * 32, t, T.BLOCK, T.STEP, explicit=slot + T.STEP), slot + T.STEP, 'the next slot is free')

    def test_a_second_report_on_the_same_explicit_slot_is_refused_and_leaves_no_folder(self):
        slot = T.BLOCK[0] + 3 * T.STEP
        self.register('--seed-base', str(slot))
        before = tree(self.out_root)
        code, out, err = self.cli('--deals', '1', '--register-only', '--seed-base', str(slot), '--date', '2026-10-11', date=False)
        self.assertNotEqual(code, 0)
        self.assertIn('2026-10-10_my-list', str(code))
        self.assertEqual(tree(self.out_root), before)
        self.assertFalse(os.path.exists(self.rundir('2026-10-11_my-list')))


# ---------------------------------------------------------------------------------------------------------- git decides what the page says about the deck file
class DeckStateInGit(T.World):
    """'committed', 'not committed' or 'unknown (...)': the page says whether the deck file is the committed one, so a person can tell what the report was made from."""

    def repo_with_a_commit(self):
        repo = os.path.join(self.tmp, 'r')
        write(os.path.join(repo, 'other.txt'), 'x\n')
        subprocess.run(['git', '-C', repo, 'init', '-q'], check=True)
        git(repo, 'add', 'other.txt')
        git(repo, 'commit', '-q', '-m', 'first')
        return repo

    def test_a_deck_that_is_not_in_git_yet_is_not_committed_although_the_repository_has_commits(self):
        repo = self.repo_with_a_commit()
        write(os.path.join(repo, 'decks', 'new.txt'), 'x\n')
        self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'not committed')

    def test_a_deck_that_is_staged_but_not_committed_is_not_committed(self):
        repo = self.repo_with_a_commit()
        write(os.path.join(repo, 'decks', 'new.txt'), 'x\n')
        git(repo, 'add', 'decks/new.txt')
        self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'not committed')

    def test_a_committed_deck_is_committed_until_it_changes_even_if_the_change_is_only_staged(self):
        repo = self.repo_with_a_commit()
        write(os.path.join(repo, 'decks', 'new.txt'), 'x\n')
        git(repo, 'add', 'decks/new.txt')
        git(repo, 'commit', '-q', '-m', 'deck')
        self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'committed')
        write(os.path.join(repo, 'decks', 'new.txt'), 'y\n')
        self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'not committed')
        git(repo, 'add', 'decks/new.txt')
        self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'not committed')

    def test_a_folder_that_is_not_a_repository_and_a_machine_without_git_are_unknown_not_committed(self):
        plain = os.path.join(self.tmp, 'plain')
        write(os.path.join(plain, 'a.txt'), 'x\n')
        self.assertEqual(sr.deck_state(plain, 'a.txt'), 'unknown (not a git repository)')
        committed = self.repo_with_a_commit()
        empty_bin = os.path.join(self.tmp, 'empty-bin')
        os.makedirs(empty_bin)
        with mock.patch.dict(os.environ, {'PATH': empty_bin}):
            self.assertEqual(sr.deck_state(committed, 'other.txt'), 'unknown (git not available)')

    def test_the_manifest_and_the_plan_say_what_git_says_about_the_deck_file(self):
        subprocess.run(['git', '-C', self.repo, 'init', '-q'], check=True)
        self.assertEqual(self.cli('--deals', '1', '--dry-run')[1].count('not committed'), 1, 'a deck git has not seen')
        git(self.repo, 'add', self.deck_rel)
        git(self.repo, 'commit', '-q', '-m', 'the deck')
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['deck_file_state'], 'committed')
        self.assertIn(f'({self.deck_rel}, committed)', out)
        self.assertIn('the file is committed', sr.write_slow_report(d))
        # a second deck that is in the folder but not in git
        other = os.path.join(self.repo, 'decks', 'events', 'other-list.txt')
        write(other, T.DECK_TEXT.replace('Torchic', 'Treecko'))
        code, out, err = self.cli_path(other, '--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        self.assertEqual(json.loads(read(os.path.join(self.rundir('2026-10-10_other-list'), 'manifest.json')))['slow_report']['deck_file_state'], 'not committed')
        self.assertIn('(decks/events/other-list.txt, not committed)', out)


# ---------------------------------------------------------------------------------------------------------- the pin file
class PinFile(T.World):
    REQUIRED = ('pilot', 'reference', 'pilot_label', 'reference_label', 'panel_label', 'panel_group', 'program', 'program_sha256', 'selfcheck', 'engine', 'pilot_provenance',
                'reference_provenance', 'seed_block', 'seed_step', 'games_per_hour', 'scrub_env_prefixes', 'threads')

    def test_a_pin_without_a_required_entry_is_refused_naming_it(self):
        pin = json.loads(read(self.pin_path))
        self.assertEqual(sr.load_pin(self.pin_path)['pilot'], pin['pilot'], 'the whole pin loads')
        for key in self.REQUIRED:
            with self.subTest(missing=key):
                broken = os.path.join(self.tmp, f'pin-without-{key}.json')
                write(broken, json.dumps({k: v for k, v in pin.items() if k != key}))
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(broken)
                self.assertIn(repr(key), str(cm.exception.code))

    def test_a_pin_without_a_required_entry_stops_the_wrapper_before_anything_is_written(self):
        pin = json.loads(read(self.pin_path))
        del pin['seed_block']
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1')
        self.assertIn("has no 'seed_block'", str(code))
        self.assertFalse(os.path.exists(self.out_root))


# ---------------------------------------------------------------------------------------------------------- the only tests that read the real repository
class LiveRepositoryData(unittest.TestCase):
    """These read the real repository on purpose, so a failure here means a document, the registry or a list changed, not that slow_report.py broke."""

    def registry(self):
        return json.loads(read(os.path.join(HERE, 'decks.json')))['decks']

    def path_of(self, name):
        return os.path.join(ROOT, *self.registry()[name].split('/'))

    def test_the_panel_group_is_the_eight_lists_and_each_one_has_a_file(self):
        self.assertEqual(json.loads(read(os.path.join(HERE, 'groups.json')))['panel8'], PANEL)
        for n in PANEL:
            self.assertTrue(os.path.isfile(self.path_of(n)), n)

    def test_the_seed_block_starts_clear_of_the_exams_overflow_and_is_recorded_in_start_here(self):
        text = read(os.path.join(ROOT, 'START_HERE.md'))
        self.assertIn('24,601,000,000', text)
        self.assertIn('24,600,070,002', text, 'the exam\'s top seeds spill past its block; START_HERE says so')
        self.assertIn('slow report', text.lower())
        self.assertGreater(T.BLOCK[0], 24_600_070_002)

    def test_a_copy_of_each_real_panel_list_and_held_out_deck_has_that_decks_signature_in_every_form(self):
        names = PANEL + json.loads(read(os.path.join(HERE, 'heldout.json')))['decks']
        changed = {how: 0 for how in COPIES}
        signatures = {}
        with tempfile.TemporaryDirectory() as t:
            for n in names:
                original = P.deck_signature(self.path_of(n))
                signatures[n] = original
                text = read(self.path_of(n))
                for how, make in COPIES.items():
                    copy = os.path.join(t, 'copy.txt')
                    write_bytes(copy, make(text))
                    changed[how] += make(text) != text.encode()
                    with self.subTest(deck=n, copy=how):
                        self.assertEqual(P.deck_signature(copy), original)
        for how, count in changed.items():
            self.assertGreater(count, 0, f'{how} changed none of the real files, so it proved nothing')
        self.assertEqual(len(set(signatures.values())), len(names), 'every real list and held-out deck is a different deck')

    def test_the_real_validator_refuses_a_deck_without_an_energy_line_and_one_with_a_line_it_cannot_read(self):
        first = json.loads(read(os.path.join(HERE, 'groups.json')))['dustin_all'][0]
        lines = read(self.path_of(first)).splitlines()
        with tempfile.TemporaryDirectory() as t:
            ok = os.path.join(t, 'ok.txt')
            write(ok, '\n'.join(lines) + '\n')
            self.assertEqual(sr.default_deck_check(ok, ROOT), [])
            no_energy = os.path.join(t, 'no-energy.txt')
            write(no_energy, '\n'.join(l for l in lines if not l.startswith('Energy:')) + '\n')
            errs = sr.default_deck_check(no_energy, ROOT)
            self.assertEqual(len(errs), 1, errs)
            self.assertIn('Energy', errs[0])
            garbled = os.path.join(t, 'garbled.txt')
            write(garbled, '\n'.join(lines) + '\nTotal: twenty cards\n')
            errs = sr.default_deck_check(garbled, ROOT)
            self.assertEqual(len(errs), 1, errs)
            self.assertIn('could not be read as a deck', errs[0])


class LiveRegistryEndToEnd(T.LiveWorld):
    """The registration against the real registry and the real lists (copied into the temporary repository), in-process: what the synthetic World cannot show."""

    def real_text(self, name):
        return read(os.path.join(ROOT, *self.registry[name].split('/')))

    def test_a_copy_of_each_real_panel_list_is_refused_in_the_forms_a_re_export_takes(self):
        for list_name in PANEL:
            for how in ('accents folded to ASCII', 'all of these at once'):
                with self.subTest(list=list_name, copy=how):
                    write_bytes(self.deck, COPIES[how](self.real_text(list_name)))
                    code, out, err = self.cli('--deals', '1', '--dry-run')
                    self.assertNotEqual(code, 0)
                    self.assertIn(f'this deck is {list_name} (or a copy of it)', str(code))

    def test_a_real_held_out_deck_and_its_ascii_copy_are_flagged_as_held_out_and_the_lock_file_stays_as_it_was(self):
        lock = os.path.join(HERE, 'heldout.json')
        st = os.stat(lock)
        before = (read(lock), st.st_mtime_ns, st.st_size)
        decks = json.loads(read(lock))['decks']  # (every real deck in every form is compared by signature in LiveRepositoryData; here the first and the last go end to end)
        for held, how in ((decks[0], 'CRLF line ends'), (decks[0], 'accents folded to ASCII'), (decks[0], 'all of these at once'), (decks[-1], 'all of these at once')):
            with self.subTest(held=held, copy=how):
                shutil.rmtree(self.out_root, ignore_errors=True)
                write_bytes(self.deck, COPIES[how](self.real_text(held)))
                code, out, err = self.cli('--deals', '1', '--register-only')
                self.assertEqual(code, 0, str(code) + err)
                self.assertEqual(json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['heldout_in_run'], ['my-list'])
        st = os.stat(lock)
        self.assertEqual((read(lock), st.st_mtime_ns, st.st_size), before)


if __name__ == '__main__':
    unittest.main()
