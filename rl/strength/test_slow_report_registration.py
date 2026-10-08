#!/usr/bin/env python3
"""Tests of the registration side of the slow report: which decks the wrapper and strength_prereg.py recognise as copies, the self-check replay, what a refused or
interrupted registration leaves behind, what the registration records, and the places where git decides what the page says.

  cd rl/strength && python3 -B -m unittest -v test_slow_report_registration

Written after the second adversarial review (findings M2-09, M2-10, M2-17, M2-21, M2-25, M2-29, M2-30, M2-32, M2-33, M2-36); each test below was checked against the
mutant it targets (the mutant is applied to a private copy and the test must fail on it). A copy of a deck is a deck with the same cards (the Energy line is not compared);
the registered question depends on whether the comparison with the baseline pilot is asked for, and says one deal, not 1 deals. Everything runs on the World of test_slow_report.py: a temporary repository
with its own synthetic registry (8 panel lists, 3 held-out decks), the fake program and a pin that names it.

Added with the cloud route (the fix round after the laptop review): ProgramRoutes (what a registration records about the program, for the pinned binary and for a rebuild
given with --program, and the tie of a self-check text to the sha256 of the program it was measured on), the seed slots a pin reserves (ExplicitSeedBase), and the guards on
the committed pin and the documents that quote it (CommittedPin, ReadmeCloudRoute).

Added with the last code changes after that review: the pin must carry seed_reserved, a list of slots whose shape is checked (PinFile, PinSeedReserved); the registration records
the engine tree found in the checkout and says in the registered engine text that a rebuilt program is a rebuild (RegistrationRecords, ProgramRoutes); every wrapper call that
plays games logs a `sitting_call`; a self-check that exits non-zero is no match (SelfCheckReplays); build.sh is run for real, with a stub cargo, for its guard against building over
the frozen binary and for the harness source hash it prints (BuildScript); and the claims of README's cloud section that a machine can check are checked (ReadmeCloudRoute,
ReadmeCloudRouteBehaviour).

What reads live data, on purpose, and only in LiveRepositoryData, CommittedPin, BuildScript, ReadmeCloudRoute, ReadmeCloudRouteBehaviour and LiveRegistryEndToEnd (which uses the
LiveWorld fixture): START_HERE.md, the committed pin, rl/strength/src and Cargo.toml (the harness source hash), build.sh, README.md, the km3 smoke folder, the real decks.json,
groups.json and heldout.json, the real panel and held-out files, and the real deck validator lib/deck_check.py with its card database. Everything else here is synthetic.
(BuildScript runs a COPY of build.sh in a temporary folder with a stub cargo and its own pin: it never builds anything and never touches the real pinned program.)
"""
import contextlib, datetime, hashlib, io, json, os, re, shlex, shutil, subprocess, sys, tempfile, unittest
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
REPLAYED = 'replayed by slow_report.py on this machine just before registration (equal to the committed pin)'
PIN_GIVEN = 'given in the config (copied from the pin, which says it was measured on this exact program sha256)'


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

    def test_a_self_check_that_fails_is_no_match_even_when_it_printed_the_pinned_text(self):
        """The program printed exactly the pin's text and then failed (a panic while closing, a signal): the exit code is part of the answer, the README says so."""
        for how, tail, rc, detail in (('an exit code', "sys.stderr.write('engine panicked while closing\\n')\nsys.exit(3)\n", 3, 'engine panicked while closing'),
                                      ('a signal', "sys.stdout.flush()\nimport signal\nos.kill(os.getpid(), signal.SIGKILL)\n", -9, 'selfcheck pilot=km3 games=12 digest=km3pin')):
            with self.subTest(failure=how):
                self.make()
                self.set_program(SELFCHECK_PROGRAM + tail)
                code, out, err = self.cli('--deals', '1', '--selfcheck')
                self.assertNotEqual(code, 0)
                self.assertIn(f'REFUSED: the self-check of km3 on {self.program} exited with code {rc} ({detail}); a self-check that fails is not a match, whatever it printed. '
                              'Nothing was written.', str(code))
                self.assertNotIn('does not match the pin', str(code), 'it is the failure that is refused, not a difference in the text')
                self.assertEqual([c['argv'][c['argv'].index('--pilot') + 1] for c in self.calls()], ['km3'], 'and nothing more is replayed')
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
        self.assertEqual(text.count('(replayed by slow_report.py on this machine just before registration and equal to the committed pin)'), 2, 'one line per pilot says so')
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
        self.assertEqual(shlex.split(recorded), ['python3', 'rl/strength/slow_report.py', '--dir', d, '--school-rule', 'off'],
                         'pasted into a shell the folder is one word; the registered school choice (this registration is --school-rule off) follows it')
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
                self.assertIn(f'stopped after --max-games 2; resume with: python3 rl/strength/slow_report.py --dir {shlex.quote(d)} --school-rule off\n', out)

    def test_the_log_names_the_registration_the_call_the_sitting_the_end_and_the_page(self):
        code, out, err = self.cli('--deals', '1')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        events = [e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] != 'env_scrubbed']  # (that one appears only on a machine that has tuning variables set)
        self.assertEqual([e['event'] for e in events], ['registered', 'sitting_call', 'slice_start', 'slice_end', 'complete', 'report_written'])
        for e in events:
            self.assertEqual((e.get('pilot'), e.get('reference')), ('kx3', 'km3'), e)
            self.assertRegex(e['at'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        registered, call, start, end, complete, report = events
        self.assertEqual(registered['manifest_sha256'], read(os.path.join(d, 'manifest.sha256')).split()[0])
        self.assertEqual((registered['seed_base'], registered['deals'], registered['paired'], registered['threads']), (man['seed_base'], 1, True, 2))
        self.assertEqual((registered['deck_file'], registered['deck_sha256']), (self.deck_rel, sha(self.deck)))
        self.assertEqual((call['school_rule'], call['school_days'], call['threads'], call['max_games'], call['school_choice_overridden']),
                         ('off', 'mon,tue,wed,thu,fri', 2, None, False), 'what this call was asked for: a registration is not an override of the registered choice')
        self.assertEqual((start['remaining_games'], start['threads']), (32, 2))
        self.assertEqual((end['returncode'], end['killed_for_school'], end['new_games']), (0, False, 32))
        self.assertEqual(complete['games'], 32)
        self.assertEqual(report['path'], os.path.join(d, 'SLOW_REPORT.md'))

    def logged_calls(self, d):
        return [e for e in jsonl(os.path.join(d, 'slow_report_log.jsonl')) if e['event'] == 'sitting_call']

    def test_every_call_that_plays_games_logs_what_it_was_asked_and_a_call_that_plays_none_logs_nothing(self):
        d = self.register('--threads', '3')  # (registered with the rule off, Monday to Friday, 3 threads)
        self.assertEqual(self.logged_calls(d), [], 'a registration is not a sitting')
        for extra, school in ((('--max-games', '2'), None), (('--max-games', '3', '--threads', '1'), None), (('--max-games', '4', '--school-days', 'sat,sun'), None),
                              (('--max-games', '5'), 'off'), (('--max-games', '6', '--school-days', ''), None)):
            self.assertEqual(self.cli('--dir', d, *extra, deck=False, school=school)[0], 0)
        got = [(e['school_rule'], e['school_days'], e['threads'], e['max_games'], e['school_choice_overridden']) for e in self.logged_calls(d)]
        self.assertEqual(got, [('off', 'mon,tue,wed,thu,fri', 3, 2, False), ('off', 'mon,tue,wed,thu,fri', 1, 3, False), ('off', 'sat,sun', 3, 4, True),
                               ('off', 'mon,tue,wed,thu,fri', 3, 5, True), ('off', '', 3, 6, True)],
                         'the registered choice and thread count unless the call gave its own; the choice is "overridden" when the call gave one (a school-days list of nothing is one)')
        before = len(self.logged_calls(d))
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False, school=None)[0], 0)
        self.assertEqual(self.cli('--dir', d, '--dry-run', deck=False, school=None)[0], 0)
        write(self.deck, T.DECK_TEXT.replace('Torchic', 'Treecko'))
        self.assertIn('REFUSED', str(self.cli('--dir', d, deck=False, school=None)[0]))
        self.assertEqual(len(self.logged_calls(d)), before, 'a page only, a dry run and a call refused before the lock play nothing and log no sitting')

    REBUILD_SENTENCE = ("; THIS PROGRAM ({path}, sha256 {sha12}) IS A REBUILD of that source made on another machine, not the laptop binary, accepted because both self-checks were "
                        "replayed on that machine and equal the committed pin's digests")

    def test_the_registered_engine_text_is_the_pins_and_says_so_when_the_program_is_a_rebuild(self):
        pin = json.loads(read(self.pin_path))
        self.assertNotIn('REBUILD', pin['engine'])
        self.assertEqual(self.build()['engine'], pin['engine'])
        self.assertEqual(self.build(route='pinned', program='/elsewhere/strength')['engine'], pin['engine'], 'the pinned bytes under another path are still the pinned program')
        rebuilt = self.build(route='rebuilt', program='/cloud/strength', program_sha='ab' * 32)
        self.assertEqual(rebuilt['engine'], pin['engine'] + self.REBUILD_SENTENCE.format(path='/cloud/strength', sha12='abababababab'))
        self.assertEqual((rebuilt['program'], rebuilt['program_sha256']), ('/cloud/strength', 'ab' * 32))

    def test_the_block_records_the_engine_tree_the_checkout_has_for_the_pinned_ref_or_nothing(self):
        pin = json.loads(read(self.pin_path))
        block = self.build()['slow_report']
        self.assertIsNone(block['engine_tree_in_checkout'], 'unknown unless the caller found it')
        self.assertEqual((block['engine_ref'], block['engine_tree']), (pin['engine_ref'], pin['engine_tree']))
        self.assertEqual(self.build(engine_tree_checkout='3' * 40)['slow_report']['engine_tree_in_checkout'], '3' * 40)

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


# ---------------------------------------------------------------------------------------------------------- which program ran, and what the self-check text is tied to
HARNESS_FILES = {'rl/strength/src/main.rs': 'fn main() {}\n', 'rl/strength/src/ext.rs': '// external pilots\n', 'rl/strength/Cargo.toml': '[package]\nname = "strength"\n'}
# what build.sh prints as the harness source hash: sha256 of src/*.rs in name order (ext.rs, then main.rs), then Cargo.toml
HARNESS_HASH = hashlib.sha256((HARNESS_FILES['rl/strength/src/ext.rs'] + HARNESS_FILES['rl/strength/src/main.rs'] + HARNESS_FILES['rl/strength/Cargo.toml']).encode()).hexdigest()
ROUTE_LINES = ('program_route', 'pinned_program', 'pinned_program_sha256', 'harness_source_sha256', 'harness_source_checkout_sha256', 'engine_ref', 'engine_tree',
               'engine_tree_in_checkout', 'school_rule', 'school_days')


def slow_report_values(text):
    """{key: value} of the '- key: `value`' lines of the '## Slow report' section of PREREGISTRATION.md, in the order they are printed."""
    section = text.split('## Slow report\n')[1].split('\n## ')[0]
    return dict(m.groups() for m in (re.fullmatch(r'- (\w+): `(.*)`', l) for l in section.splitlines()) if m)


class ProgramRoutes(SelfCheckWorld):
    """What a registration says about the program it will run: PREREGISTRATION.md and the manifest's slow-report block name the route (the pinned binary, or a rebuild given
    with --program), the pinned program and its sha256, the harness source hashes, the engine ref and tree and the school-morning choice; and the self-check text, whichever
    way it was obtained, is tied to the sha256 of the program it was measured on. The fixture lays out a harness source in the temporary repository (HARNESS_FILES) that
    the pin's harness_source_sha256 names, a git commit in it that holds the pinned engine (engine/, whose tree the pin's engine_tree names), and a second copy of the program
    (self.rebuilt, other bytes) with its own digests beside it, as a cloud rebuild would be."""

    def make(self, *a, **kw):
        super().make(*a, **kw)
        for rel, text in HARNESS_FILES.items():
            write(os.path.join(self.repo, *rel.split('/')), text)
        subprocess.run(['git', '-C', self.repo, 'init', '-q'], check=True, capture_output=True)  # a checkout that has the pinned engine commit, as a cloud clone of the branch does
        write(os.path.join(self.repo, 'engine', 'Cargo.lock'), '# the engine of the pinned build\n')
        git(self.repo, 'add', 'engine')
        git(self.repo, 'commit', '-q', '-m', 'the pinned engine')
        pin = json.loads(read(self.pin_path))
        pin['harness_source_sha256'] = HARNESS_HASH
        pin['engine_ref'] = git(self.repo, 'rev-parse', 'HEAD').stdout.strip()
        pin['engine_tree'] = git(self.repo, 'rev-parse', 'HEAD:engine').stdout.strip()
        write(self.pin_path, json.dumps(pin))
        self.pin = pin
        self.cloud = os.path.join(self.tmp, 'cloud')
        self.rebuilt = os.path.join(self.cloud, 'strength')
        write(self.rebuilt, SELFCHECK_PROGRAM + '# built again on another machine: other bytes, the same behaviour\n', mode=0o755)
        write(os.path.join(self.cloud, 'digests.json'), json.dumps({'km3': 'km3pin', 'kx3': 'kx3pin'}))
        return self

    def rebuilt_calls(self):
        return jsonl(os.path.join(self.cloud, 'selfcheck_calls.jsonl'))

    def registered(self, *flags, **kw):
        code, out, err = self.cli('--deals', '1', '--register-only', *flags, **kw)
        self.assertEqual(code, 0, str(code) + out + err)
        d = self.rundir()
        return json.loads(read(os.path.join(d, 'manifest.json'))), json.loads(read(os.path.join(d, 'config.json'))), read(os.path.join(d, 'PREREGISTRATION.md'))

    def assert_route_lines(self, man, text, expected):
        """The block in the manifest and the lines of the document both carry exactly these entries; the document prints them in this order, after the pin."""
        for k, v in expected.items():
            self.assertEqual(man['slow_report'][k], v, k)
        values = slow_report_values(text)
        self.assertEqual({k: values[k] for k in ROUTE_LINES}, expected)
        keys = list(values)
        self.assertEqual(keys[keys.index('pin') + 1:], list(ROUTE_LINES), 'after the pin, once each, in this order')

    def test_the_pinned_binary_is_registered_with_the_pins_text_and_the_route_named(self):
        man, cfg, text = self.registered()
        self.assertEqual((man['program'], man['program_sha256']), (self.program, self.pin['program_sha256']))
        self.assertEqual(self.calls(), [], 'the pinned text is recorded; the 12 games are not replayed')
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'])
        self.assertEqual(man['selfcheck_source'], {'km3': PIN_GIVEN, 'kx3': PIN_GIVEN})
        self.assertEqual(cfg['selfcheck_given_program_sha256'], self.pin['selfcheck_measured_on_sha256'], 'the config says which binary the pinned text was measured on')
        self.assertNotIn('selfcheck_how', cfg)
        self.assert_route_lines(man, text, dict(program_route='pinned', pinned_program=self.program, pinned_program_sha256=self.pin['program_sha256'],
                                                harness_source_sha256=HARNESS_HASH, harness_source_checkout_sha256=HARNESS_HASH, engine_ref=self.pin['engine_ref'],
                                                engine_tree=self.pin['engine_tree'], engine_tree_in_checkout=self.pin['engine_tree'], school_rule='off',
                                                school_days='mon,tue,wed,thu,fri'))
        self.assertEqual(man['engine'], self.pin['engine'], 'the pinned program: the engine text is the pin\'s, word for word')
        self.assertIn(f"engine: {self.pin['engine']}; repository commit", text)
        self.assertNotIn('REBUILD', text.split('## Design')[0])
        line = ' (given in the config, copied from the pin and not replayed: the pin says it was measured on this exact program, whose sha256 is named above)'
        self.assertEqual(text.count(line), 2, 'one line per pilot says so')
        self.assertNotIn('replayed by slow_report.py', text)
        self.assertIn(f"Program: `{self.program}` sha256 `{self.pin['program_sha256']}`", text, 'the sha256 the line points up to')

    def test_a_rebuild_is_registered_with_both_self_checks_replayed_on_it_and_named_as_a_rebuild(self):
        actual = sha(self.rebuilt)
        self.assertNotEqual(actual, self.pin['program_sha256'])
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual((man['program'], man['program_sha256']), (self.rebuilt, actual), 'the program the games will be played with is the rebuild')
        self.assertEqual(sorted(c['argv'][c['argv'].index('--pilot') + 1] for c in self.rebuilt_calls()), ['km3', 'kx3'], 'both pilots are replayed on the rebuild')
        self.assertEqual(self.calls(), [], 'and not on the pinned binary')
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'], 'equal to the committed pin (a difference refuses the registration)')
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED, 'kx3': REPLAYED})
        self.assertEqual((cfg['selfcheck_given_program_sha256'], cfg['selfcheck_how'], cfg['program'], cfg['program_sha256']), (actual, 'replayed', self.rebuilt, actual),
                         'the replayed text carries the sha256 of the program it was just measured on, not the pin\'s')
        self.assert_route_lines(man, text, dict(program_route='rebuilt', pinned_program=self.program, pinned_program_sha256=self.pin['program_sha256'],
                                                harness_source_sha256=HARNESS_HASH, harness_source_checkout_sha256=HARNESS_HASH, engine_ref=self.pin['engine_ref'],
                                                engine_tree=self.pin['engine_tree'], engine_tree_in_checkout=self.pin['engine_tree'], school_rule='off',
                                                school_days='mon,tue,wed,thu,fri'))
        engine = (self.pin['engine'] + f"; THIS PROGRAM ({self.rebuilt}, sha256 {actual[:12]}) IS A REBUILD of that source made on another machine, not the laptop binary, accepted "
                  "because both self-checks were replayed on that machine and equal the committed pin's digests")
        self.assertEqual((man['engine'], cfg['engine']), (engine, engine), 'the registered engine text says this program is a rebuild made elsewhere, and names it')
        self.assertIn(f'engine: {engine}; repository commit', text)
        line = ' (replayed by slow_report.py on this machine just before registration and equal to the committed pin)'
        self.assertEqual(text.count(line), 2, 'one line per pilot says so')
        self.assertNotIn('not replayed', text)
        self.assertIn(f'Program: `{self.rebuilt}` sha256 `{actual}`', text)

    def test_the_route_is_pinned_when_the_program_given_is_the_pinned_binary(self):
        """--program with the pinned binary (the same sha256, here the pin's own path) is not a rebuild: no replay, the pin's text, route `pinned`."""
        man, cfg, text = self.registered('--program', self.program)
        self.assertEqual(self.calls(), [])
        self.assertEqual(man['slow_report']['program_route'], 'pinned')
        self.assertEqual(man['selfcheck_source'], {'km3': PIN_GIVEN, 'kx3': PIN_GIVEN})
        self.assertEqual(cfg['selfcheck_given_program_sha256'], self.pin['selfcheck_measured_on_sha256'])

    def test_a_copy_of_the_pinned_binary_at_another_path_is_the_pinned_binary(self):
        """The route follows the bytes, not the path: the manifest names the copy that will run, and the pin's text (measured on those bytes) is recorded as given."""
        copy = os.path.join(self.tmp, 'copy', 'strength')
        write(copy, read(self.program), mode=0o755)
        self.assertEqual(sha(copy), self.pin['program_sha256'])
        man, cfg, text = self.registered('--program', copy)
        self.assertEqual((man['program'], man['program_sha256']), (copy, self.pin['program_sha256']))
        self.assertEqual(man['slow_report']['program_route'], 'pinned')
        self.assertEqual(man['slow_report']['pinned_program'], self.program, 'the pin\'s path is still the pin\'s')
        self.assertEqual(self.calls(), [])

    def test_the_pinned_route_records_the_checkouts_harness_hash_even_when_it_is_not_the_pins(self):
        """Only a rebuild needs the checkout to hold the pinned source; for the pinned binary the checkout's hash is recorded as a fact the page can point out."""
        write(os.path.join(self.repo, 'rl', 'strength', 'src', 'main.rs'), 'fn main() { println!("changed"); }\n')
        changed = hashlib.sha256((HARNESS_FILES['rl/strength/src/ext.rs'] + 'fn main() { println!("changed"); }\n' + HARNESS_FILES['rl/strength/Cargo.toml']).encode()).hexdigest()
        self.assertNotEqual(changed, HARNESS_HASH)
        man, cfg, text = self.registered()
        self.assertEqual((man['slow_report']['harness_source_sha256'], man['slow_report']['harness_source_checkout_sha256']), (HARNESS_HASH, changed))
        values = slow_report_values(text)
        self.assertEqual((values['harness_source_sha256'], values['harness_source_checkout_sha256']), (HARNESS_HASH, changed))

    def test_a_pin_whose_text_was_measured_on_another_binary_is_refused_naming_both_sha256_values(self):
        """The pin says its texts were measured on one binary (selfcheck_measured_on_sha256); when the program is another one the text is not recorded for it."""
        pin = json.loads(read(self.pin_path))
        pin['selfcheck_measured_on_sha256'] = 'f' * 64
        write(self.pin_path, json.dumps(pin))
        for flags in ((), ('--program', self.program)):
            with self.subTest(flags=flags):
                code, out, err = self.cli('--deals', '1', '--register-only', *flags)
                self.assertNotEqual(code, 0)
                self.assertIn('REFUSED by strength_prereg.py (nothing was written)', str(code))
                self.assertIn(f"measured on a program with sha256 ffffffffffff, but the program at {self.program} has sha256 {sha(self.program)[:12]}", str(code))
                self.assertFalse(os.path.exists(self.out_root), 'nothing is left behind')
                self.assertEqual(self.calls(), [])

    def test_a_replay_does_not_need_the_pins_measured_on_entry_because_it_is_measured_now(self):
        """With --selfcheck the 12 games are played on the program that is there, so the text is tied to that program whatever the pin says about where its own text came from."""
        pin = json.loads(read(self.pin_path))
        pin['selfcheck_measured_on_sha256'] = 'f' * 64
        write(self.pin_path, json.dumps(pin))
        man, cfg, text = self.registered('--selfcheck')
        self.assertEqual(len(self.calls()), 2)
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED, 'kx3': REPLAYED})
        self.assertEqual((cfg['selfcheck_given_program_sha256'], cfg['selfcheck_how']), (sha(self.program), 'replayed'))
        self.assertEqual(slow_report_values(text)['program_route'], 'pinned', 'a replay on the pinned binary is still the pinned route')

    def test_a_rebuild_whose_self_check_differs_from_the_pin_registers_nothing(self):
        write(os.path.join(self.cloud, 'digests.json'), json.dumps({'km3': 'km3pin', 'kx3': 'a-different-digest'}))
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.rebuilt)
        self.assertNotEqual(code, 0)
        self.assertIn('self-check of kx3 does not match the pin', str(code))
        self.assertFalse(os.path.exists(self.out_root), 'nothing is written')

    def edit_pin(self, **kw):
        """Change entries of this world's pin (an entry given as None is removed)."""
        pin = json.loads(read(self.pin_path))
        for k, v in kw.items():
            if v is None:
                pin.pop(k, None)
            else:
                pin[k] = v
        write(self.pin_path, json.dumps(pin))
        self.pin = pin

    def real_tree(self):
        return git(self.repo, 'rev-parse', 'HEAD:engine').stdout.strip()

    def test_the_pinned_route_records_the_engine_tree_the_checkout_has_and_does_not_depend_on_it(self):
        """A checkout is not part of the pinned binary: what it holds for the pinned ref is a fact on the record (the tree id, or null when it cannot say), whatever the pin says."""
        for how, edit, found in (('the pin names another tree', lambda: self.edit_pin(engine_tree='f' * 40), 'the real one'),
                                 ('the pin names no tree', lambda: self.edit_pin(engine_tree=None), 'the real one'),
                                 ('the pin names no ref', lambda: self.edit_pin(engine_ref=None), None),
                                 ('the checkout does not have the pinned commit', lambda: self.edit_pin(engine_ref='0' * 40), None),
                                 ('the checkout is not a git repository', lambda: shutil.rmtree(os.path.join(self.repo, '.git')), None)):
            with self.subTest(case=how):
                self.make()
                edit()
                man, cfg, text = self.registered()
                self.assertEqual(man['slow_report']['program_route'], 'pinned')
                self.assertEqual(man['slow_report']['engine_tree_in_checkout'], self.real_tree() if found else None)
                self.assertEqual(man['slow_report']['engine_tree'], self.pin.get('engine_tree'))
                values = slow_report_values(text)
                self.assertIn('engine_tree_in_checkout', values, 'the document carries the line too')
                self.assertEqual(values['engine_tree_in_checkout'], self.real_tree() if found else 'not found', 'a null entry is said in words, never as the text None')

    def test_a_rebuild_is_refused_when_the_checkouts_engine_is_not_the_pinned_one_before_anything_is_replayed(self):
        real = self.real_tree()
        self.edit_pin(engine_tree='f' * 40)
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.rebuilt)
        self.assertEqual(code, f"[kx3 (d513e37b) v km3] REFUSED: this checkout's {self.pin['engine_ref'][:8]}:engine tree is {real[:12]}, not the pinned ffffffffffff, "
                               'so a build of it is not the pinned engine. Nothing was written.')
        self.assertEqual(self.rebuilt_calls(), [], 'refused before the hours-long replay')
        self.assertEqual(self.calls(), [])
        self.assertFalse(os.path.exists(self.out_root))
        code, out, err = self.cli('--deals', '1', '--dry-run', '--program', self.rebuilt)
        self.assertIn('so a build of it is not the pinned engine', str(code), 'a dry run says so too')
        self.edit_pin(engine_tree=real)
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual(man['slow_report']['program_route'], 'rebuilt', 'and the same rebuild is accepted when the tree is the pinned one')

    def test_a_rebuild_is_accepted_when_the_checkout_cannot_say_what_its_engine_tree_is(self):
        """The tree check is a check when the checkout has the pinned commit; with no git or no such commit it is information only (the self-check replay still has to match)."""
        for how, edit in (('the checkout is not a git repository', lambda: shutil.rmtree(os.path.join(self.repo, '.git'))),
                          ('the checkout does not have the pinned commit', lambda: self.edit_pin(engine_ref='0' * 40)),
                          ('the pin names no tree', lambda: self.edit_pin(engine_tree=None))):
            with self.subTest(case=how):
                self.make()
                edit()
                man, cfg, text = self.registered('--program', self.rebuilt)
                self.assertEqual(man['slow_report']['program_route'], 'rebuilt')
                self.assertEqual(sorted(c['argv'][c['argv'].index('--pilot') + 1] for c in self.rebuilt_calls()), ['km3', 'kx3'])

    def test_a_rebuild_written_over_the_pinned_path_is_refused_and_the_message_says_what_happened(self):
        """Another file at the pin's own path is a frozen binary that was built over (the original cannot be recovered): not a rebuild to accept, whichever way the path is spelled."""
        write(self.program, SELFCHECK_PROGRAM + '# built over the frozen binary\n', mode=0o755)
        link = os.path.join(self.tmp, 'link-to-the-pinned-path')
        os.symlink(self.program, link)
        overwritten = (f"{{path}} is the pinned binary's own path, but the file there has sha256 {sha(self.program)[:12]}, not the pinned {self.pin['program_sha256'][:12]}: the frozen binary has "
                       'been overwritten (do not build over it; build.sh to another path). A rebuild is accepted at any other path, after its self-checks are replayed.')
        for path in (self.program, link, os.path.join(self.tmp, 'rl', '..', os.path.basename(self.program))):
            with self.subTest(program=path):
                code, out, err = self.cli('--deals', '1', '--register-only', '--program', path)
                self.assertEqual(code, '[kx3 (d513e37b) v km3] REFUSED: ' + overwritten.format(path=os.path.abspath(path)))
                self.assertEqual((self.calls(), self.rebuilt_calls()), ([], []), 'refused before the replay')
                self.assertFalse(os.path.exists(self.out_root))
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertIn('is not the pinned build', str(code), 'without --program the pinned path is just not the pinned build, and the message points to --program PATH')
        self.assertIn('--program PATH', str(code))

    def test_the_school_morning_choice_is_registered_in_the_block_the_document_and_the_resume_command(self):
        cases = (('the default: on, on the school days', (), None, 'on', 'mon,tue,wed,thu,fri', ''),
                 ('off', (), 'off', 'off', 'mon,tue,wed,thu,fri', ' --school-rule off'),
                 ('on, on other days', ('--school-days', 'sat,sun'), None, 'on', 'sat,sun', ' --school-days sat,sun'),
                 ('off, with other days named', ('--school-days', 'sat,sun'), 'off', 'off', 'sat,sun', None),
                 ('on, with no school days (a choice, not an unset flag: the rule never pauses)', ('--school-days', ''), None, 'on', '', " --school-days ''"),
                 ('off, with no school days', ('--school-days', ''), 'off', 'off', '', None))
        for how, flags, school, rule, days, tail in cases:
            with self.subTest(choice=how):
                shutil.rmtree(self.out_root, ignore_errors=True)
                man, cfg, text = self.registered(*flags, school=school)
                d = self.rundir()
                self.assertEqual((man['slow_report']['school_rule'], man['slow_report']['school_days']), (rule, days))
                values = slow_report_values(text)
                self.assertEqual((values['school_rule'], values['school_days']), (rule, days))
                run = text.split('## Run')[1]
                if rule == 'on':
                    self.assertIn(f'applies the school-morning rule as registered ({days or "no school days"})', run)
                else:
                    self.assertIn('does NOT apply the school-morning rule (chosen at registration: it never pauses for school mornings)', run)
                if tail is not None:
                    command = f'python3 rl/strength/slow_report.py --dir {shlex.quote(d)}{tail}'
                    self.assertEqual(man['slow_report']['resume_command'], command)
                    self.assertIn(command, text.split('## Run')[1], 'the command the document prints carries the choice')


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

    def reserve(self, base, note='the smoke run of another branch (committed outside the output folder)'):
        pin = json.loads(read(self.pin_path))
        pin['seed_reserved'] = [{'base': base, 'note': note}]
        write(self.pin_path, json.dumps(pin))
        return note

    def test_a_slot_the_pin_reserves_is_skipped_by_a_registration_and_refused_by_number(self):
        """The pin's seed_reserved lists slots used by committed runs that are not in the output folder (the km3 smoke): a registration never takes one, whether the deck's
        own slot is the reserved one or a number is asked for."""
        own = sr.pick_seed_base(sha(self.deck), self.out_root, T.BLOCK, T.STEP)
        note = self.reserve(own)
        code, out, err = self.cli('--deals', '1', '--register-only', '--seed-base', str(own))
        self.assertNotEqual(code, 0)
        self.assertIn(f'--seed-base {own} is a seed slot that is already used ({note})', str(code))
        self.assertFalse(os.path.exists(self.out_root))
        d = self.register()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], own + T.STEP, 'the next free slot')

    def test_a_pin_that_reserves_nothing_leaves_the_deck_its_own_slot(self):
        """seed_reserved says so in words: an empty list. (An entry that is missing is not the same thing, see below.)"""
        own = sr.pick_seed_base(sha(self.deck), self.out_root, T.BLOCK, T.STEP)
        pin = json.loads(read(self.pin_path))
        pin['seed_reserved'] = []
        write(self.pin_path, json.dumps(pin))
        self.assertEqual(json.loads(read(os.path.join(self.register(), 'manifest.json')))['seed_base'], own)

    def test_a_pin_with_no_seed_reserved_entry_is_refused_instead_of_being_read_as_reserving_nothing(self):
        """A missing entry (an older pin, a typo in the key) would hand out the very slots the committed smoke runs used; the pin must say what it reserves, even if that is nothing."""
        pin = json.loads(read(self.pin_path))
        del pin['seed_reserved']
        write(self.pin_path, json.dumps(pin))
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, f"[slow report] the pin {self.pin_path} has no 'seed_reserved'")
        self.assertFalse(os.path.exists(self.out_root))

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
    REQUIRED = ('pilot', 'reference', 'pilot_label', 'reference_label', 'panel_label', 'panel_group', 'program', 'program_sha256', 'selfcheck', 'selfcheck_measured_on_sha256',
                'harness_source_sha256', 'engine', 'pilot_provenance', 'reference_provenance', 'seed_block', 'seed_step', 'games_per_hour', 'scrub_env_prefixes', 'threads',
                'seed_reserved')  # (seed_reserved: a pin must say which slots are taken, even if none; its shape is checked in PinSeedReserved)
    OPTIONAL = ('engine_ref', 'engine_tree')  # recorded when the pin has them; a pin from before them still loads and registers

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

    def test_a_pin_without_the_measured_on_entry_or_the_harness_source_entry_is_refused_before_anything_is_written(self):
        """The two entries the cloud route stands on: without them a self-check text could be recorded for a binary it was not measured on, and a rebuild could not be
        told from the pinned source."""
        for key in ('selfcheck_measured_on_sha256', 'harness_source_sha256'):
            with self.subTest(missing=key):
                self.make()
                pin = json.loads(read(self.pin_path))
                del pin[key]
                write(self.pin_path, json.dumps(pin))
                for flags in (('--register-only',), ('--dry-run',)):
                    code, out, err = self.cli('--deals', '1', *flags)
                    self.assertEqual(str(code), f"[slow report] the pin {self.pin_path} has no {key!r}")
                    self.assertFalse(os.path.exists(self.out_root))
                code, out, err = self.cli('--dir', self.rundir(), '--dry-run', deck=False)
                self.assertIn(f'has no {key!r}', str(code), 'a resume reads the pin too')

    def test_a_malformed_seed_block_or_seed_step_is_a_clean_refusal_not_a_traceback(self):
        """seed_reserved is checked against the block and the step, so those are checked first (a test writer found ZeroDivisionError and TypeError here)."""
        pin = json.loads(read(self.pin_path))
        bad = [('seed_step', 0), ('seed_step', -5), ('seed_step', '100000'), ('seed_step', True), ('seed_step', 1.5), ('seed_step', None),
               ('seed_block', [1]), ('seed_block', [1, 2, 3]), ('seed_block', ['a', 'b']), ('seed_block', [1.5, 3]), ('seed_block', [True, 5]), ('seed_block', [9, 1]),
               ('seed_block', None), ('seed_block', 5), ('seed_block', {'lo': 1, 'hi': 2})]
        for key, value in bad:
            with self.subTest(key=key, value=value):
                broken = os.path.join(self.tmp, 'pin-broken.json')
                write(broken, json.dumps(dict(pin, **{key: value})))
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(broken)
                self.assertEqual(cm.exception.code, f'the pin {broken}: seed_block must be [first seed, last seed] (two whole numbers) and seed_step a whole number of at least 1')
        self.assertEqual(sr.load_pin(self.pin_path)['seed_step'], pin['seed_step'], 'the good pin loads')

    def test_a_pin_without_the_optional_entries_still_loads_and_registers(self):
        pin = json.loads(read(self.pin_path))
        for key in self.OPTIONAL:
            self.assertIn(key, pin, 'the template pin has them')
            del pin[key]
        write(self.pin_path, json.dumps(pin))
        self.assertEqual(sr.load_pin(self.pin_path)['program_sha256'], pin['program_sha256'])
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)

    def test_the_seed_reserved_entry_is_not_one_of_the_optional_ones(self):
        """Without it the pin loads no more: a missing entry is a refusal naming it (an empty list is the way to reserve nothing)."""
        pin = json.loads(read(self.pin_path))
        for key in self.OPTIONAL:
            del pin[key]
        del pin['seed_reserved']
        write(self.pin_path, json.dumps(pin))
        with self.assertRaises(SystemExit) as cm:
            sr.load_pin(self.pin_path)
        self.assertEqual(cm.exception.code, f"the pin {self.pin_path} has no 'seed_reserved'")
        pin['seed_reserved'] = []
        write(self.pin_path, json.dumps(pin))
        self.assertEqual(sr.load_pin(self.pin_path)['seed_reserved'], [])
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)


class PinSeedReserved(T.World):
    """seed_reserved lists the seed slots that committed runs outside the output folder already used (the km3 smoke). A typo there hands out a slot a committed run used, and
    two reports would play the same deals, so load_pin refuses anything but a list of {"base": int, "note": text}, each base the first seed of a slot inside the seed block."""

    LO, HI, STEP = T.BLOCK[0], T.BLOCK[1], T.STEP
    LAST = HI - STEP + 1  # the first seed of the last slot
    NOTE = 'a run that used this slot'

    BAD = {
        'null': None, 'a number': 5, 'text': 'slot 684', 'empty text': '', 'true': True, 'false': False,
        'an object with the keys of an entry': {'base': LO, 'note': NOTE}, 'an empty object': {},
        'an entry that is a number': [5], 'an entry that is text': ['x'], 'an entry that is null': [None], 'an entry that is a pair': [[LO, NOTE]],
        'a good entry then a bad one': [{'base': LO, 'note': NOTE}, 5], 'a bad entry then a good one': [{'base': 'x', 'note': NOTE}, {'base': LO + STEP, 'note': NOTE}],
        'a base that is text': [{'base': str(LO), 'note': NOTE}], 'a base that is a float': [{'base': float(LO), 'note': NOTE}], 'a base that is true': [{'base': True, 'note': NOTE}],
        'a base that is null': [{'base': None, 'note': NOTE}], 'a base that is a list': [{'base': [LO], 'note': NOTE}], 'no base': [{'note': NOTE}],
        'a base below the block': [{'base': LO - STEP, 'note': NOTE}], 'a base one below the block': [{'base': LO - 1, 'note': NOTE}], 'a base of zero': [{'base': 0, 'note': NOTE}],
        'a negative base': [{'base': -LO, 'note': NOTE}], 'the start of the slot after the last': [{'base': LAST + STEP, 'note': NOTE}],
        'a base far above the block': [{'base': HI * 10, 'note': NOTE}],
        'a base inside a slot, not at its start': [{'base': LO + 1, 'note': NOTE}], 'a base half way through a slot': [{'base': LO + STEP // 2, 'note': NOTE}],
        'the last seed of a slot': [{'base': LO + STEP - 1, 'note': NOTE}], 'the start of a slot plus one, late in the block': [{'base': LAST + 1, 'note': NOTE}],
        'no note': [{'base': LO}], 'a note that is a number': [{'base': LO, 'note': 5}], 'a note that is null': [{'base': LO, 'note': None}],
        'a note that is a list': [{'base': LO, 'note': [NOTE]}], 'a note that is true': [{'base': LO, 'note': True}],
    }
    GOOD = {
        'an empty list': [], 'the first slot': [{'base': LO, 'note': 'first'}], 'the last slot': [{'base': LAST, 'note': 'last'}],
        'two slots': [{'base': LO + 684 * STEP, 'note': 'slot 684: a smoke run'}, {'base': LO + 685 * STEP, 'note': 'slot 685: another smoke run'}],
        'slots in any order': [{'base': LAST, 'note': 'last'}, {'base': LO, 'note': 'first'}],
    }

    def message(self, path):
        return (f'the pin {path}: seed_reserved must be a list of {{"base": the first seed of a slot inside the seed block, "note": text}}; '
                'a typo there would hand out a slot a committed run already used')

    def pin_with(self, reserved, name='pin-reserved.json', **more):
        pin = dict(json.loads(read(self.pin_path)), seed_reserved=reserved, **more)
        path = os.path.join(self.tmp, name)
        write(path, json.dumps(pin))
        return path

    def test_every_malformed_shape_is_refused_with_the_clear_message(self):
        for how, reserved in self.BAD.items():
            with self.subTest(seed_reserved=how):
                path = self.pin_with(reserved)
                with self.assertRaises(SystemExit) as cm:
                    sr.load_pin(path)
                self.assertEqual(cm.exception.code, self.message(path))

    def test_a_good_list_is_accepted_as_it_is(self):
        for how, reserved in self.GOOD.items():
            with self.subTest(seed_reserved=how):
                self.assertEqual(sr.load_pin(self.pin_with(reserved))['seed_reserved'], reserved)

    def test_the_committed_pins_own_list_is_a_good_one(self):
        committed = json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))['seed_reserved']
        self.assertTrue(committed)
        self.assertEqual(sr.load_pin(self.pin_with(committed))['seed_reserved'], committed)

    def test_a_bool_is_not_a_base_even_where_it_would_be_a_number_in_the_block(self):
        """True is 1 and False is 0 to arithmetic, so in a block that starts at 0 they pass every range test: only the type check refuses them."""
        for reserved, accepted in (([{'base': 5, 'note': self.NOTE}], True), ([{'base': 0, 'note': self.NOTE}], True), ([{'base': True, 'note': self.NOTE}], False),
                                   ([{'base': False, 'note': self.NOTE}], False)):
            with self.subTest(base=reserved[0]['base']):
                path = self.pin_with(reserved, seed_block=[0, 9], seed_step=1)
                if accepted:
                    self.assertEqual(sr.load_pin(path)['seed_reserved'], reserved)
                else:
                    with self.assertRaises(SystemExit) as cm:
                        sr.load_pin(path)
                    self.assertEqual(cm.exception.code, self.message(path))

    def test_a_slot_that_would_end_past_the_block_is_refused_even_when_its_start_is_inside_it(self):
        """A block that is not a whole number of slots wide: the last, partial slot is not a slot (a base in it would reserve seeds the picker never hands out)."""
        for base, accepted in ((0, True), (100, True), (200, False), (250, False)):
            with self.subTest(base=base):
                path = self.pin_with([{'base': base, 'note': self.NOTE}], seed_block=[0, 250], seed_step=100)
                if accepted:
                    self.assertEqual(sr.load_pin(path)['seed_reserved'][0]['base'], base)
                else:
                    with self.assertRaises(SystemExit) as cm:
                        sr.load_pin(path)
                    self.assertEqual(cm.exception.code, self.message(path))

    def test_the_wrapper_stops_on_a_malformed_list_before_anything_is_written(self):
        for how in ('null', 'a base that is text', 'a base inside a slot, not at its start', 'no note'):
            with self.subTest(seed_reserved=how):
                self.make()
                write(self.pin_path, read(self.pin_with(self.BAD[how])))
                for flags in (('--register-only',), ('--dry-run',)):
                    code, out, err = self.cli('--deals', '1', *flags)
                    self.assertEqual(code, '[slow report] ' + self.message(self.pin_path))
                    self.assertEqual(out, '', 'refused before it printed a plan')
                    self.assertFalse(os.path.exists(self.out_root))

    def test_a_resume_reads_the_pin_too_and_refuses_a_malformed_list(self):
        d = self.register()
        write(self.pin_path, read(self.pin_with(self.BAD['a base inside a slot, not at its start'])))
        for flags in (('--dry-run',), ('--report-only',), ()):
            code, out, err = self.cli('--dir', d, *flags, deck=False)
            self.assertEqual(code, '[slow report] ' + self.message(self.pin_path))
        self.assertFalse(os.path.exists(os.path.join(d, 'games.jsonl')), 'and plays nothing')

    def test_a_good_list_reaches_the_picker_and_a_slot_in_it_is_not_handed_out(self):
        own = sr.pick_seed_base(sha(self.deck), self.out_root, T.BLOCK, T.STEP)
        write(self.pin_path, read(self.pin_with([{'base': own, 'note': 'taken by a committed run'}])))
        d = self.register()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['seed_base'], own + T.STEP)


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


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


class CommittedPin(unittest.TestCase):
    """The committed pin (rl/strength/slow_report_pin.json) and the documents and folders that quote it. These read the real repository on purpose: a failure here means the
    pin, the harness source, START_HERE.md, the README or the smoke folder moved, not that slow_report.py broke."""

    PIN_PATH = os.path.join(HERE, 'slow_report_pin.json')
    PROGRAM_SHA = '5a8f5c83a7915090437e91ae7c644bdd67d1aed713f50a1f7de0bf905802a3d2'
    HARNESS_SHA = 'bf9c5d6814007f1f53b0dc06f1beba02261478ddc40bb5efa3bbc16c0734f86e'
    RESERVED = (24669400000, 24669500000, 24669600000)  # slots 684, 685 and 686: the km3 smoke runs (the third is the cloud-route registration)

    def pin(self):
        def no_repeats(pairs):
            keys = [k for k, _ in pairs]
            repeated = sorted({k for k in keys if keys.count(k) > 1})
            if repeated:
                raise ValueError(f'{repeated} is in the pin twice (a JSON reader keeps the last one without a word)')
            return dict(pairs)
        with open(self.PIN_PATH, encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=no_repeats)

    def test_the_pin_loads_and_is_the_pin_the_wrapper_uses_by_default(self):
        self.assertEqual(sr.load_pin(self.PIN_PATH), self.pin())
        self.assertEqual(os.path.abspath(sr.DEFAULT_PIN), self.PIN_PATH)

    def test_the_entries_the_cloud_route_stands_on_have_their_values(self):
        pin = self.pin()
        self.assertEqual(pin['program_sha256'], self.PROGRAM_SHA)
        self.assertEqual(pin['selfcheck_measured_on_sha256'], self.PROGRAM_SHA, 'the self-check texts were measured on the pinned binary itself')
        self.assertEqual(pin['harness_source_sha256'], self.HARNESS_SHA)
        self.assertEqual(pin['engine_ref'], 'd513e37b473f2819075e1eb2439075a8a1e65c42')
        named = re.search(r'engine tree ([0-9a-f]{12})\b', pin['engine']).group(1)
        self.assertEqual(named, '31dbd2e6e8ec', 'the engine tree the pin\'s own description names')
        self.assertRegex(pin['engine_tree'], r'^[0-9a-f]{40}$')
        self.assertTrue(pin['engine_tree'].startswith(named), f"engine_tree {pin['engine_tree']} is not the tree {named} that the pin's engine text names")
        for where in ('engine', 'pilot_label', 'pilot_provenance'):
            self.assertIn(pin['engine_ref'][:8], pin[where], f'the ref is the commit {where} names')

    def test_the_reserved_seed_slots_are_the_three_smoke_slots_inside_the_block(self):
        pin = self.pin()
        lo, hi = pin['seed_block']
        step = pin['seed_step']
        reserved = sorted(pin['seed_reserved'], key=lambda r: r['base'])
        self.assertEqual([r['base'] for r in reserved], list(self.RESERVED))
        for r, slot in zip(reserved, (684, 685, 686)):
            with self.subTest(slot=slot):
                self.assertEqual(sorted(r), ['base', 'note'])
                self.assertTrue(lo <= r['base'] and r['base'] + step - 1 <= hi and (r['base'] - lo) % step == 0, 'the start of a slot inside the block')
                self.assertEqual((r['base'] - lo) // step, slot)
                self.assertIn(f'slot {slot}', r['note'])

    def test_the_harness_source_in_this_checkout_is_the_source_the_pin_was_made_on(self):
        """A failure means rl/strength/src or Cargo.toml changed since the pin was made: a cloud rebuild from this checkout would be refused, and the pinned binary is no
        longer built from this source. The pin must be re-made, after its own gate (never edit the hash to make this pass)."""
        pin = self.pin()
        self.assertEqual(sr.harness_source_sha256(ROOT), pin['harness_source_sha256'])
        src = os.path.join(HERE, 'src')
        data = b''.join(read_bytes(os.path.join(src, n)) for n in sorted(os.listdir(src)) if n.endswith('.rs')) + read_bytes(os.path.join(HERE, 'Cargo.toml'))
        self.assertEqual(hashlib.sha256(data).hexdigest(), pin['harness_source_sha256'], 'build.sh\'s recipe worked out here, not by the function under test')

    def test_build_sh_prints_the_hash_the_way_the_wrapper_computes_it(self):
        """The recipe in words: src/*.rs then Cargo.toml, no separators, and the file names sorted the C way (the glob is expanded under LC_ALL=C, because the wrapper sorts by
        code point). BuildScript runs it for real, with names that sort differently in the two orders."""
        self.assertIn('echo "harness source sha256: $(LC_ALL=C; cat "$HERE"/src/*.rs "$HERE/Cargo.toml" | sha256sum | cut -d\' \' -f1)"', read(os.path.join(HERE, 'build.sh')))

    def test_start_here_lists_both_reserved_slots_in_the_slow_report_row(self):
        rows = [l for l in read(os.path.join(ROOT, 'START_HERE.md')).splitlines() if l.startswith('|') and '24,601,000,000' in l and 'slow report' in l]
        self.assertEqual(len(rows), 1, 'one row for the slow report\'s seed block')
        for base in self.RESERVED:
            self.assertIn(f'{base:,}', rows[0])
        self.assertIn('slots 684, 685 and 686', rows[0])
        self.assertIn('seed_reserved', rows[0], 'the row says the pin lists them too')

    def test_the_smoke_runs_hold_exactly_the_reserved_seeds(self):
        pin = self.pin()
        smoke = os.path.join(ROOT, 'rl', 'results', 'slow_report_smoke_2026-10-07')
        found = {run: json.loads(read(os.path.join(smoke, run, 'manifest.json'))) for run in sorted(os.listdir(smoke)) if os.path.isfile(os.path.join(smoke, run, 'manifest.json'))}
        self.assertEqual(sorted(found), ['run1_complete_under_nohup', 'run2_sigterm_and_resume', 'run3_cloud_route_rebuilt_registration'])
        self.assertEqual(sorted(m['seed_base'] for m in found.values()), list(self.RESERVED))
        for r in pin['seed_reserved']:
            owner = [run for run, m in found.items() if m['seed_base'] == r['base']]
            self.assertEqual(len(owner), 1, r)
            self.assertIn(owner[0], r['note'], 'the note names the run folder that holds the slot')
        slots = (pin['seed_block'][1] - pin['seed_block'][0] + 1) // pin['seed_step']
        self.assertEqual(int(found['run1_complete_under_nohup']['slow_report']['deck_file_sha256'][:8], 16) % slots, 684, 'the picker chose run 1\'s slot from its deck: the note says so')

    def test_the_picker_skips_the_reserved_slots_of_the_real_pin(self):
        pin = self.pin()
        block, step, reserved = tuple(pin['seed_block']), pin['seed_step'], pin['seed_reserved']
        on_slot = lambda slot: f'{slot:08x}' + '0' * 56  # a deck sha256 whose first 8 hex digits give this slot
        with tempfile.TemporaryDirectory() as empty:
            for slot, picked in ((683, 683), (684, 687), (685, 687), (686, 687), (687, 687)):
                with self.subTest(slot=slot):
                    self.assertEqual(sr.pick_seed_base(on_slot(slot), empty, block, step), block[0] + slot * step, 'without the reserved list a deck lands on its own slot')
                    self.assertEqual(sr.pick_seed_base(on_slot(slot), empty, block, step, reserved=reserved), block[0] + picked * step)
            for base in self.RESERVED:
                with self.subTest(explicit=base):
                    with self.assertRaises(SystemExit) as cm:
                        sr.pick_seed_base(on_slot(0), empty, block, step, explicit=base, reserved=reserved)
                    self.assertIn(f'--seed-base {base} is a seed slot that is already used (', str(cm.exception.code))
                    self.assertIn(next(r['note'] for r in reserved if r['base'] == base), str(cm.exception.code), 'it says which run holds the slot')


def cloud_section():
    """README.md's 'Running on the cloud' section."""
    text = read(os.path.join(HERE, 'README.md'))
    assert '### Running on the cloud' in text, 'README.md has no "Running on the cloud" section'
    return text.split('### Running on the cloud')[1].split('\n## ')[0]


def readme_build_command():
    """(ref, out) of the build.sh command that step 1 of the cloud section gives, out as written ($HOME unexpanded)."""
    m = re.search(r'`rl/strength/build\.sh (\S+) (\S+)`', cloud_section())
    assert m, 'step 1 of the cloud section gives a `rl/strength/build.sh REF OUT` command'
    return m.group(1), m.group(2)


def locale_that_sorts_a_before_B(scratch):
    """(locale name, extra environment) under which bash expands a glob case-insensitively, a.rs before B.rs (the C locale puts B.rs first): an installed locale or, failing
    that, en_US.UTF-8 made now with localedef into `scratch`. None when this machine has none."""
    probe = os.path.join(scratch, 'probe')
    os.makedirs(probe)
    for n in ('B.rs', 'a.rs'):
        write(os.path.join(probe, n), '')
    clean = {k: v for k, v in os.environ.items() if k not in ('LANG', 'LANGUAGE', 'LOCPATH') and not k.startswith('LC_')}

    def sorts(name, extra):
        r = subprocess.run(['bash', '-c', 'cd "$1" && echo *.rs', 'probe', probe], capture_output=True, text=True, env=dict(clean, LC_ALL=name, **extra))
        return r.stdout.split() == ['a.rs', 'B.rs']
    for name in ('en_US.UTF-8', 'en_US.utf8', 'en_GB.UTF-8', 'de_DE.UTF-8'):
        if sorts(name, {}):
            return name, {}
    if shutil.which('localedef'):
        where = os.path.join(scratch, 'locales')
        os.makedirs(where)
        subprocess.run(['localedef', '-i', 'en_US', '-f', 'UTF-8', os.path.join(where, 'en_US.UTF-8')], capture_output=True)
        if sorts('en_US.UTF-8', {'LOCPATH': where}):
            return 'en_US.UTF-8', {'LOCPATH': where}
    return None


class BuildScript(unittest.TestCase):
    """rl/strength/build.sh, run for real on a COPY of itself in a temporary folder: its own src/*.rs, Cargo.toml and a pin beside it, an engine folder for the ref (so no git), a
    stub `cargo` first on the PATH that only writes a file where the real one would leave the program, and HOME, STRENGTH_BUILD_DIR and every output path inside the temporary
    folder. Nothing is built and nothing outside the folder is touched: the 'frozen binary' here is a file of this test's own, at a path of its own. Only the format of the
    committed pin's program line is read from the real repository (build.sh picks it out with sed)."""

    FROZEN = b'the frozen binary: not to be overwritten\n'
    STUB_PROGRAM = b'the stub program\n'

    def setUp(self):
        if not all(shutil.which(x) for x in ('bash', 'sed', 'readlink', 'sha256sum', 'nice', 'find', 'touch', 'cat', 'cut')):
            self.skipTest('needs a Unix userland (bash, GNU readlink and sha256sum)')
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.here = os.path.join(self.tmp, 'rl', 'strength')
        os.makedirs(self.here)
        shutil.copy(os.path.join(HERE, 'build.sh'), os.path.join(self.here, 'build.sh'))
        for n in ('B.rs', 'a.rs', 'Z.rs', 'm.rs'):  # in the C order B, Z, a, m; case-insensitively a, B, m, Z
            write(os.path.join(self.here, 'src', n), f'// {n}\n')
        write(os.path.join(self.here, 'Cargo.toml'), '[package]\nname = "strength"\n')
        self.engine = os.path.join(self.tmp, 'engine')
        write(os.path.join(self.engine, 'Cargo.lock'), '# the engine\'s lock file\n')
        self.stub = os.path.join(self.tmp, 'stub-bin')
        self.log = os.path.join(self.tmp, 'cargo-calls.log')
        write(os.path.join(self.stub, 'cargo'), '#!/bin/bash\necho "$* | target=$CARGO_TARGET_DIR" >> "$STUB_LOG"\nmkdir -p "$CARGO_TARGET_DIR/release"\n'
                                                'printf \'the stub program\\n\' > "$CARGO_TARGET_DIR/release/strength"\n', mode=0o755)
        self.frozen = os.path.join(self.tmp, 'frozen', 'strength')
        write_bytes(self.frozen, self.FROZEN)
        self.lay_out_pin(self.frozen)

    def lay_out_pin(self, program):
        """The pin beside build.sh, laid out like the committed one (one entry to a line): it names `program` as the frozen binary."""
        write(os.path.join(self.here, 'slow_report_pin.json'), json.dumps({'_note': 'a test pin', 'program': program, 'program_sha256': '0' * 64}, indent=1) + '\n')

    def run_build(self, out, ref=None, cwd=None, **env_changes):
        """build.sh REF OUT with a clean environment (no locale, no STRENGTH_* variable), HOME and the build folder inside the temporary folder; env_changes add to it."""
        env = {k: v for k, v in os.environ.items() if k not in ('LANG', 'LANGUAGE', 'LOCPATH') and not k.startswith(('LC_', 'STRENGTH_'))}
        env.update(PATH=self.stub + os.pathsep + env.get('PATH', ''), HOME=os.path.join(self.tmp, 'home'), STRENGTH_BUILD_DIR=os.path.join(self.tmp, 'build'), STUB_LOG=self.log)
        env.update(env_changes)
        self.assertEqual(shutil.which('cargo', path=env['PATH']), os.path.join(self.stub, 'cargo'), 'the stub, never a real cargo, is what build.sh would call')
        self.assertTrue(os.path.realpath(os.path.join(cwd or self.tmp, out)).startswith(self.tmp + os.sep), 'every output path of these tests is inside the temporary folder')
        return subprocess.run(['bash', os.path.join(self.here, 'build.sh'), ref or self.engine, out], capture_output=True, text=True, env=env, cwd=cwd or self.tmp)

    def refusal(self, program):
        return f"build.sh: refusing to overwrite the slow report's pinned program {program} (slow_report_pin.json); build to another path\n"

    def assert_nothing_was_done(self, r, program):
        self.assertEqual((r.returncode, r.stdout, r.stderr), (2, '', self.refusal(program)))
        self.assertEqual(read_bytes(self.frozen), self.FROZEN, 'the frozen binary is as it was')
        self.assertFalse(os.path.exists(self.log), 'cargo was not called')

    def test_building_to_the_pinned_programs_own_path_is_refused_with_exit_2_before_anything_is_done(self):
        marker = os.path.join(self.tmp, 'build', 'tree', 'marker')
        write(marker, 'left by an earlier build: the refusal comes before build.sh clears the build folder')
        for ref in (self.engine, 'no-such-ref', os.path.join(self.tmp, 'no-such-folder')):
            with self.subTest(ref=os.path.basename(ref)):
                self.assert_nothing_was_done(self.run_build(self.frozen, ref=ref), self.frozen)
                self.assertTrue(os.path.exists(marker))
                self.assertEqual(os.listdir(os.path.dirname(self.frozen)), ['strength'])

    def test_every_spelling_of_the_pinned_path_is_refused(self):
        folder_link, file_link = os.path.join(self.tmp, 'folder-link'), os.path.join(self.tmp, 'file-link')
        os.symlink(os.path.dirname(self.frozen), folder_link)
        os.symlink(self.frozen, file_link)
        link_to_link = os.path.join(self.tmp, 'link-to-the-link')
        os.symlink(file_link, link_to_link)
        spellings = {'with a dot dot in it': os.path.join(self.tmp, 'frozen', '..', 'frozen', 'strength'), 'with doubled slashes': self.frozen.replace('/frozen/', '//frozen//'),
                     'relative to the folder it runs in': os.path.join('frozen', 'strength'), 'a link to the file': file_link, 'a link to that link': link_to_link,
                     'in a folder that is a link': os.path.join(folder_link, 'strength')}
        for how, out in spellings.items():
            with self.subTest(spelling=how):
                self.assert_nothing_was_done(self.run_build(out), self.frozen)

    def test_a_hard_link_to_the_frozen_binary_is_refused_because_cp_would_write_through_it(self):
        link = os.path.join(self.tmp, 'hardlink-folder', 'strength')
        os.makedirs(os.path.dirname(link))
        os.link(self.frozen, link)
        self.assertEqual(os.path.realpath(link), link, 'a hard link is a different path to the same file: readlink does not see it')
        self.assert_nothing_was_done(self.run_build(link), self.frozen)
        self.assertEqual(read_bytes(link), self.FROZEN)

    def test_any_other_output_path_builds_and_prints_the_four_lines(self):
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        os.makedirs(os.path.dirname(out))
        r = self.run_build(out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [f'engine: dir:{self.engine}', f'program: {out}', f'program sha256: {hashlib.sha256(self.STUB_PROGRAM).hexdigest()}',
                                                 f'harness source sha256: {sr.harness_source_sha256(self.tmp)}'])
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        self.assertEqual(read_bytes(self.frozen), self.FROZEN)
        self.assertEqual(read(self.log).splitlines(), [f'build --release --offline | target={os.path.join(self.tmp, "build", "target")}'], 'cargo was asked for an offline release build once')

    def test_a_folder_that_does_not_exist_yet_is_a_fine_place_to_build(self):
        """The laptop (the pinned folder is there, the output folder is new) and the cloud: the README's step 1 builds into $HOME/slow_report_kx3, which a fresh machine has not
        made, and there the laptop's folder is not there either. build.sh makes the output folder itself, after the guard."""
        fresh = os.path.join(self.tmp, 'home', 'slow_report_kx3', 'strength')
        for how, program in (('the pinned binary\'s folder is there', self.frozen), ('the pinned binary\'s folder is not there', os.path.join(self.tmp, 'laptop-home', 'kx', 'strength'))):
            with self.subTest(machine=how):
                shutil.rmtree(os.path.dirname(os.path.dirname(fresh)), ignore_errors=True)
                self.lay_out_pin(program)
                r = self.run_build(fresh)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(read_bytes(fresh), self.STUB_PROGRAM, 'built, into a folder it made')
                self.assertEqual(read_bytes(self.frozen), self.FROZEN)

    def test_the_pinned_path_is_refused_where_nothing_is_there_too(self):
        """A pin read on a machine that does not have the binary: building to that very path is still building over the pinned path."""
        absent = os.path.join(self.tmp, 'laptop-home', 'kx', 'strength')
        self.lay_out_pin(absent)
        self.assert_nothing_was_done(self.run_build(absent), absent)
        self.assertFalse(os.path.exists(os.path.dirname(absent)), 'and it made no folder')

    def test_the_path_the_readme_builds_to_is_accepted_on_a_machine_without_the_laptops_folder_and_the_pinned_path_is_not(self):
        ref, written = readme_build_command()
        self.assertTrue(written.startswith('$HOME/'), written)
        out = written.replace('$HOME', os.path.join(self.tmp, 'home'))
        self.lay_out_pin(os.path.join(self.tmp, 'laptop-home', 'kx', 'strength'))  # (the committed pin's /home/<user>/kx/strength, on a machine that has no such folder)
        r = self.run_build(out)
        self.assertEqual((r.returncode, r.stderr), (0, ''), 'step 1 of the README, as written, is not refused by the guard against building over the frozen binary')
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)

    def test_the_guard_finds_the_program_line_of_the_committed_pin_the_way_json_does(self):
        """build.sh cannot run Python, so it picks the pin's program path out with sed: on the committed pin's layout that must be exactly the path the wrapper reads."""
        m = re.search(r"PIN_PROGRAM=\$\(sed -n '([^']*)' \"\$HERE/slow_report_pin\.json\"", read(os.path.join(HERE, 'build.sh')))
        self.assertTrue(m, 'build.sh reads the pin\'s program path with sed')
        committed = os.path.join(HERE, 'slow_report_pin.json')
        r = subprocess.run(['sed', '-n', m.group(1), committed], capture_output=True, text=True)
        self.assertEqual(r.stdout.splitlines(), [json.loads(read(committed))['program']], 'one line, the pinned path (not the program_sha256 line, not the note)')

    def test_the_harness_source_hash_it_prints_is_the_one_the_wrapper_computes_in_any_locale(self):
        found = locale_that_sorts_a_before_B(self.tmp)
        if found is None:
            self.skipTest('no locale on this machine sorts a.rs before B.rs, so a build under it could not tell the two orders apart')
        name, extra = found
        names = ['B.rs', 'a.rs', 'Z.rs', 'm.rs']
        src = os.path.join(self.here, 'src')

        def hash_in(order):
            return hashlib.sha256(b''.join(read_bytes(os.path.join(src, n)) for n in order) + read_bytes(os.path.join(self.here, 'Cargo.toml'))).hexdigest()
        wrapper = sr.harness_source_sha256(self.tmp)
        self.assertEqual(wrapper, hash_in(sorted(names)), 'the wrapper sorts the names by code point')
        self.assertEqual(sorted(names), ['B.rs', 'Z.rs', 'a.rs', 'm.rs'])
        self.assertNotEqual(wrapper, hash_in(['a.rs', 'B.rs', 'm.rs', 'Z.rs']), 'the other order gives another hash: this test can tell them apart')
        for how, env in (('LC_ALL', {'LC_ALL': name}), ('LANG', {'LANG': name}), ('both', {'LC_ALL': name, 'LANG': name})):
            with self.subTest(locale_set_by=how):
                r = self.run_build(os.path.join(self.tmp, 'out-' + how, 'strength'), **env, **extra)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual([l for l in r.stdout.splitlines() if l.startswith('harness source sha256: ')], [f'harness source sha256: {wrapper}'])


class ReadmeCloudRoute(unittest.TestCase):
    """README.md's 'Running on the cloud' section is what a person (or the cloud agent) will follow word for word: what can be checked mechanically is checked against the
    argument parser, the committed pin and the code. (Real README, real pin: a failure means one of them moved.)"""

    FLAGS = ('--program', '--school-rule off', '--register-only', '--max-games', '--dry-run', '--threads', '--deals')

    def readme(self):
        return read(os.path.join(HERE, 'README.md'))

    def section(self):
        return cloud_section()

    def pin(self):
        return json.loads(read(os.path.join(HERE, 'slow_report_pin.json')))

    def script(self, *argv):
        return subprocess.run([sys.executable, '-B', os.path.join(HERE, 'slow_report.py'), *argv], capture_output=True, text=True)

    def test_the_flags_the_section_uses_exist_in_the_parser(self):
        section, helped = self.section(), self.script('--help')
        self.assertEqual(helped.returncode, 0, helped.stderr)
        for flag in self.FLAGS:
            with self.subTest(flag=flag):
                self.assertIn(flag, section)
                self.assertIn(flag.split()[0], helped.stdout)
        self.assertIn('--school-rule {on,off}', helped.stdout, 'the README says `--school-rule off`: off is a choice')

    def test_every_slow_report_command_in_the_section_is_accepted_by_the_parser(self):
        commands = [s for s in re.findall(r'`([^`]+)`', self.section()) if s.startswith('python3 rl/strength/slow_report.py ')]
        self.assertTrue(commands, 'the section gives the registration command')
        with tempfile.TemporaryDirectory() as t:
            for command in commands:
                with self.subTest(command=command):
                    argv = [w.replace('$HOME', t).replace('DECKFILE', os.path.join(t, 'deck.txt')) for w in shlex.split(command)[2:]]
                    r = self.script(*argv, '--pin', os.path.join(t, 'no-such-pin.json'))
                    self.assertNotIn('unrecognized arguments', r.stderr)
                    self.assertNotIn('usage:', r.stderr)
                    self.assertIn('cannot read the pin', r.stderr, 'the parser accepted every word and the script went on to read the pin')

    def test_the_section_quotes_the_values_of_the_committed_pin(self):
        pin, section = self.pin(), self.section()
        self.assertIn(f"rl/strength/build.sh {pin['engine_ref']} ", section, 'the build command names the pinned engine ref in full')
        self.assertEqual(re.search(r'engine tree must be `([0-9a-f]{12})…`', section).group(1), pin['engine_tree'][:12])
        self.assertEqual(re.search(r'harness source hash `([0-9a-f]{8})…`', section).group(1), pin['harness_source_sha256'][:8])
        self.assertEqual(re.search(r"the laptop's `([0-9a-f]{8})…`", section).group(1), pin['program_sha256'][:8])
        for spec in ('kx3', 'km3'):
            digest = re.search(r'digest=(\w+)', pin['selfcheck'][spec]).group(1)
            self.assertIn(f'{spec} `{digest}`', section)
        self.assertIn(f"sha256 `{pin['program_sha256'][:8]}…`", self.readme(), 'the description of the pin')

    def test_build_sh_takes_the_ref_then_the_output_path_and_prints_the_three_values_the_section_checks(self):
        """Step 1 builds with `build.sh <ref> <out>` (offline) and compares the engine tree, the program sha256 and the harness source hash it prints."""
        section, build = self.section(), read(os.path.join(HERE, 'build.sh'))
        self.assertIn('cargo --offline', section)
        self.assertIn('cargo build --release --offline', build)
        self.assertIn('REF=${1:-origin/main}', build)
        self.assertIn('OUT=${2:-', build)
        self.assertIn('ENGINE_ID="$REF engine tree $(git -C "$REPO" rev-parse "$REF:engine")"', build, 'for a git ref it prints the engine tree')
        for printed in ('echo "engine: $ENGINE_ID"', 'echo "program sha256: ', 'echo "harness source sha256: '):
            self.assertIn(printed, build)

    def test_the_section_quotes_the_message_a_slice_ends_with(self):
        self.assertIn('stopped after --max-games N; resume with: <command>', self.section())

    def test_the_readme_does_not_say_the_held_out_guard_compares_energy_types(self):
        """The guard compares the cards (set and number, counts merged); the Energy line is left out because with none the engine derives the types from the cards."""
        text = self.readme()
        bullet = next(l for l in text.splitlines() if l.startswith('- **Stage `use`.**'))
        self.assertIn('the Energy line is left out', bullet)
        self.assertNotIn('Energy', re.sub(r'\([^()]*Energy line is left out[^()]*\)', '', bullet), 'nothing else in the guard\'s description is about Energy')
        self.assertIsNone(re.search(r'(?i)compar\w*[^.;()]*Energy[ -]types?', text))
        self.assertIsNone(re.search(r'(?i)\b(set|number)[^.;()]* and Energy\b', text))

    def test_the_readme_never_speaks_of_energy_types_as_part_of_what_a_deck_is(self):
        """The Energy line is not read when two decks are compared (with none, the engine derives the types from the cards), so 'Energy types' must not appear as something compared."""
        self.assertNotIn('energy types', self.readme().lower())

    def test_every_flag_the_section_writes_is_an_option_of_the_script_except_the_one_it_gives_to_cargo(self):
        flags = set(re.findall(r'(?<![\w-])--[a-z][a-z-]*', self.section()))
        foreign = {'--offline'}
        self.assertTrue(foreign <= flags and len(flags) >= 8, sorted(flags))
        helped = self.script('--help')
        self.assertEqual(helped.returncode, 0, helped.stderr)
        for flag in sorted(flags - foreign):
            with self.subTest(flag=flag):
                self.assertIn(flag, helped.stdout)

    def test_every_flag_the_whole_slow_report_part_of_the_readme_names_is_an_option_of_one_of_its_scripts(self):
        """The cloud section is checked above; this is the rest of the slow report's part (from its heading to 'Files'), which also names the options of slow_report_existing.py."""
        text = self.readme()
        part = text.split('## The slow report (opt-in)')[1].split('\n## Files')[0]
        flags = set(re.findall(r'(?<![\w-])--[a-z][a-z-]*', part))
        options = ''
        for script in ('slow_report.py', 'slow_report_existing.py'):
            helped = subprocess.run([sys.executable, '-B', os.path.join(HERE, script), '--help'], capture_output=True, text=True)
            self.assertEqual(helped.returncode, 0, helped.stderr)
            options += helped.stdout
        self.assertGreaterEqual(len(flags), 12, sorted(flags))
        self.assertEqual([f for f in sorted(flags - {'--offline'}) if f not in options], [])

    def test_step_1_builds_to_a_path_of_its_own_that_step_2_then_uses_and_never_the_pinned_binarys(self):
        pin, section = self.pin(), self.section()
        ref, out = readme_build_command()
        self.assertEqual(ref, pin['engine_ref'])
        self.assertTrue(out.startswith('$HOME/'), out)
        registrations = [c for c in re.findall(r'`([^`]+)`', section) if c.startswith('python3 rl/strength/slow_report.py ') and '--register-only' in c]
        self.assertEqual(len(registrations), 1, 'step 2 gives one registration command')
        words = shlex.split(registrations[0])
        self.assertEqual(words[words.index('--program') + 1], out, 'the registration is given the program step 1 built, at the same path')
        for home in (os.path.dirname(os.path.dirname(pin['program'])), '/root', '/home/agent', '/tmp/a b'):
            with self.subTest(home=home):
                self.assertNotEqual(os.path.normpath(out.replace('$HOME', home)), os.path.normpath(pin['program']))
        self.assertIn(pin['program'], section, 'the section names the pinned binary\'s path, to say it is not the path to build to')
        self.assertIn('never the pinned binary', section)

    def test_step_1_gives_the_branch_to_fetch_and_the_cargo_cache_to_fill_and_they_are_the_pins_and_build_shs(self):
        pin, section, build = self.pin(), self.section(), read(os.path.join(HERE, 'build.sh'))
        branch = pin['engine'].split()[0]
        self.assertEqual(branch, 'claude/playout-pilot', 'the pin\'s own text names the branch the commit is on')
        self.assertIn(f"The commit `{pin['engine_ref']}` is on the branch `origin/{branch}`", section)
        self.assertIn(f'git fetch origin {branch}', section)
        self.assertIn('`cargo fetch` against `engine/Cargo.lock`', section)
        self.assertIn('cp "$W/tree/engine/Cargo.lock" "$W/tree/rl/strength/Cargo.lock"', build, 'the lock file the section says to fetch against is the one build.sh builds with')


class ReadmeCloudRouteBehaviour(T.World):
    """The claims of README.md that need the code to be run, not just its words read: what registration prints, which path a resume needs, and what a machine without the time
    zone database gets. (The README is the real one, the registration is the synthetic World.)"""

    def readme(self):
        return read(os.path.join(HERE, 'README.md'))

    def test_registration_ends_by_printing_the_command_that_plays_the_run(self):
        self.assertIn('Registration ends by printing the command that plays the run (it carries `--school-rule off`)', cloud_section())
        for how, flags, school, tail in (('the rule off', (), 'off', ' --school-rule off'), ('the default rule', (), None, ''),
                                         ('other school days', ('--school-days', 'sat,sun'), None, ' --school-days sat,sun')):
            with self.subTest(choice=how):
                shutil.rmtree(self.out_root, ignore_errors=True)
                code, out, err = self.cli('--deals', '1', '--register-only', *flags, school=school)
                self.assertEqual(code, 0, str(code) + err)
                d = self.rundir()
                command = f'python3 rl/strength/slow_report.py --dir {shlex.quote(d)}{tail}'
                self.assertEqual(out.splitlines()[-1], f'{T.HEADLINE_START}my-list v km3 on the public panel] play it with: {command} (add --max-games N to play in slices)')
                self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command'], command, 'the command registered is the one printed')
                self.assertIn(command, read(os.path.join(d, 'PREREGISTRATION.md')).split('## Run')[1])

    def test_a_registration_that_only_looks_prints_no_play_command(self):
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, str(code) + err)
        self.assertNotIn('play it with', out)

    def test_the_registration_records_the_checkouts_absolute_path_and_a_moved_checkout_cannot_resume(self):
        self.assertIn("check out the pushed folder **at the same absolute path** (the manifest records the checkout's path)", cloud_section())
        d = self.register()
        man = json.loads(read(os.path.join(d, 'manifest.json')))
        self.assertEqual(man['repo_root'], self.repo)
        self.assertTrue(os.path.isabs(man['repo_root']))
        moved = self.repo + '-moved'
        os.rename(self.repo, moved)
        code, out, err = self.cli('--dir', d.replace(self.repo, moved, 1), '--dry-run', deck=False)
        self.assertEqual(code, 0, str(code) + err)
        self.assertIn(f'the repository this run was registered in ({self.repo}) is not there', out)
        self.assertIn('put the checkout back at that path', out)

    TIME_ZONE_SENTENCE = ("The time zone database is needed when the rule is on (a missing one is a clear refusal at registration or resume, not a traceback hours in) and, for the "
                          "run folder's date, with a UTC fallback when it is missing; `--school-rule off` with `--date` never touches it.")

    def test_without_the_time_zone_database_a_run_with_the_rule_on_is_refused_clearly_at_registration_and_at_resume(self):
        self.assertIn(self.TIME_ZONE_SENTENCE, self.readme())
        d = self.register(school='on')
        asked = self.without_tzdata()
        clear = 'REFUSED: the time zone database (America/Chicago) is not available here (ZoneInfoNotFoundError): install tzdata, or turn the school-morning rule off with --school-rule off'
        headline = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['headline']
        code, out, err = self.cli('--deals', '1', '--register-only', '--date', '2026-10-11', date=False, school='on')
        self.assertEqual(code, f'[{headline}] {clear}')
        self.assertEqual(out, '')
        self.assertFalse(os.path.exists(self.rundir('2026-10-11_my-list')))
        code, out, err = self.cli('--dir', d, '--max-games', '2', deck=False, school=None)
        self.assertEqual(code, f'[{headline}] {clear}')
        self.assertFalse(os.path.exists(os.path.join(d, 'fake_calls.jsonl')), 'a resume refused here played nothing')
        self.assertIn('America/Chicago', asked)

    def test_with_the_rule_off_and_a_date_given_the_time_zone_database_is_never_touched(self):
        asked = self.without_tzdata()
        code, out, err = self.cli('--deals', '1', '--date', '2026-10-12', date=False, school='off')
        self.assertEqual(code, 0, str(code) + err)
        self.assertEqual(asked, [])
        self.assertTrue(os.path.exists(os.path.join(self.rundir('2026-10-12_my-list'), 'SLOW_REPORT.md')))

    def test_with_the_rule_off_and_no_date_the_run_folder_is_dated_by_the_utc_day_where_the_database_is_missing(self):
        self.without_tzdata()
        self.clock = T.FakeClock(T.chi(2026, 10, 10, 22, 0))  # 22:00 on Oct 10 in Chicago is already Oct 11 in UTC
        code, out, err = self.cli('--deals', '1', '--register-only', date=False, school='off')
        self.assertEqual(code, 0, str(code) + err)
        self.assertEqual(os.listdir(self.out_root), ['2026-10-11_my-list'])


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
