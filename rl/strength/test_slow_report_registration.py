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

Added with the third round of fixes (the cloud route's three medium holes): the pin must be the COMMITTED one (CommittedPinCheck: byte-equal to HEAD's file in a temporary git
repository, the test-only variable SLOW_REPORT_ALLOW_UNCOMMITTED_PIN that every other test sets in World.setUp, and the refusal before anything is trusted), a rebuild is held to
the build record build.sh writes beside it, not to what the checkout holds (BuildRecordChecks; ProgramRoutes), build.sh writes that record (BuildRecordFile), reads the pin as JSON
(BuildPinGuard) and its files are checked against the README's step 1 (ReadmeCloudRoute), and the registration records the pin state, the registering machine and the record in
the manifest, the document and the console. The test of a build that fails after an earlier build left a program in the target folder (test_a_failed_cargo_build_is_not_passed_
off_...) was red on purpose until build.sh kept cargo's exit status; it passes now, and its sibling for a clean failure with no earlier program sits beside it.

Added with the fix round after the fourth review: what the pin state does to the wording (a pin that is not the committed one is never called "the committed pin": the registered
engine text, the self-check sources, the plan line, PREREGISTRATION.md), what git said when the committed pin cannot be read (a stub git that reports a folder as unsafe, CommittedPinCheck),
a build record whose entries have the wrong type (BuildRecordChecks), and build.sh's new behaviour, run for real with stub tools (BuildRecordFile, BuildPinGuard, BuildScript): a folder as
the output is refused, a relative output or folder is made absolute, a pin whose program is not text is refused, one build at a time per build folder (flock), a failed cargo stops the script
with exit 1 and no program, the variables that change what cargo builds are removed from its environment and listed in the record together with the cargo config files that apply, and
git archive converts no line ends. The README sentences that say so are checked against that behaviour (ReadmeCloudRoute, ReadmeCloudRouteBehaviour).

Added with the third batch of fixes after the last adversarial review: a build record entry that is not text is refused as "an entry KEY that is not text", and a missing toolchain is
worded for the sentence it is in ('toolchain not recorded', 'rustc not recorded', 'built with an unrecorded toolchain': BuildRecordChecks, RegistrationRecords); the pin check and the deck
check read git without GIT_DIR and its relatives and the advice for an unsafe folder is shell-quoted (CommittedPinCheck, DeckStateInGit); build.sh keeps a link's name for the record, makes the
build and target folders absolute, locks the target folder too (and hands neither lock to a process cargo leaves running), refuses a null or non-text pin program under PYTHONOPTIMIZE,
records a config file it cannot read, and reads REPO whatever git variables are exported (BuildScript, BuildPinGuard, BuildRecordFile); the Run paragraph says "a rebuild of the pinned
source by its build record" (test_strength_prereg_use.py); and the README sentences for all of these are checked (ReadmeCloudRoute). The tests of the three defects that were documented as
known (a relative build folder, two build folders sharing a target folder, the unquoted safe.directory advice) are plain tests now.

What reads live data, on purpose, and only in LiveRepositoryData, CommittedPin, BuildScript, BuildPinGuard, ReadmeCloudRoute, ReadmeCloudRouteBehaviour and LiveRegistryEndToEnd (which
uses the LiveWorld fixture): START_HERE.md, the committed pin, rl/strength/src and Cargo.toml (the harness source hash), build.sh, README.md, the km3 smoke folder, the real decks.json,
groups.json and heldout.json, the real panel and held-out files, and the real deck validator lib/deck_check.py with its card database. Everything else here is synthetic.
(BuildWorld, the fixture of BuildScript, BuildPinGuard and BuildRecordFile, runs a COPY of build.sh in a temporary folder with a stub cargo, a stub rustc, its own pin and its own
git repository and engine folder: it never builds anything and never touches the real pinned program.)
"""
import contextlib, datetime, hashlib, io, json, os, re, shlex, shutil, signal, socket, subprocess, sys, tempfile, time, unittest
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
REPLAYED = 'replayed by slow_report.py on the registering machine just before registration (equal to the committed pin)'
# what a pin that is not the committed one (every World's hand-made pin, let through by the test-only variable) is called instead
REPLAYED_UNCOMMITTED = ('replayed by slow_report.py on the registering machine just before registration (equal to the pin file in use, which is NOT the committed pin: test use)')
DIGESTS_COMMITTED = "the committed pin's digests"
DIGESTS_UNCOMMITTED = 'the digests of the pin file in use (NOT the committed pin: test use)'
PIN_GIVEN ='given in the config (copied from the pin, which says it was measured on this exact program sha256)'


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
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED_UNCOMMITTED, 'kx3': REPLAYED_UNCOMMITTED}, "this world's pin is not the committed one, and the record says so")
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
        self.assertEqual(text.count('(replayed by slow_report.py on the registering machine just before registration and equal to the pin file in use, which is NOT the committed pin: test use)'), 2,
                         'one line per pilot says so')
        self.assertNotIn('equal to the committed pin', text, 'a pin that is not the committed one is not called that')
        self.assertNotIn('not replayed', text)
        self.assertNotIn('on this machine', text.split('## Design')[0], 'the document is read elsewhere, later: it names the registering machine, not "this" one')

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
                self.assertIn(f'stopped after --max-games 2 (games across both arms, about half of them kx3 games); resume with: '
                              f'python3 rl/strength/slow_report.py --dir {shlex.quote(d)} --school-rule off\n', out)

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
                              (('--max-games', '5'), 'off'), (('--max-games', '6', '--school-days', ''), None), (('--max-games', '7', '--school-days', 'mon,tue,wed,thu,fri'), None),
                              (('--max-games', '8'), 'on')):
            self.assertEqual(self.cli('--dir', d, *extra, deck=False, school=school)[0], 0)
        got = [(e['school_rule'], e['school_days'], e['threads'], e['max_games'], e['school_choice_overridden']) for e in self.logged_calls(d)]
        self.assertEqual(got, [('off', 'mon,tue,wed,thu,fri', 3, 2, False), ('off', 'mon,tue,wed,thu,fri', 1, 3, False), ('off', 'sat,sun', 3, 4, True),
                               ('off', 'mon,tue,wed,thu,fri', 3, 5, False), ('off', '', 3, 6, True), ('off', 'mon,tue,wed,thu,fri', 3, 7, False),
                               ('on', 'mon,tue,wed,thu,fri', 3, 8, True)],
                         'the registered choice and thread count unless the call gave its own; the choice is "overridden" only when the rule or the days differ from the registered ones '
                         '(a school-days list of nothing is a difference; giving the registered rule or days again, which is what the printed resume command does, is not)')
        before = len(self.logged_calls(d))
        self.assertEqual(self.cli('--dir', d, '--report-only', deck=False, school=None)[0], 0)
        self.assertEqual(self.cli('--dir', d, '--dry-run', deck=False, school=None)[0], 0)
        write(self.deck, T.DECK_TEXT.replace('Torchic', 'Treecko'))
        self.assertIn('REFUSED', str(self.cli('--dir', d, deck=False, school=None)[0]))
        self.assertEqual(len(self.logged_calls(d)), before, 'a page only, a dry run and a call refused before the lock play nothing and log no sitting')

    RECORD = dict(schema=1, program='/cloud/strength', program_sha256='ab' * 32, engine_arg='d513e37b', engine='d513e37b engine tree 31dbd2e6e8ec', engine_ref='d' * 40,
                  engine_tree_archived='3' * 40, harness_source_sha256='b' * 64, rustc='rustc 1.99.0 (abc 2026-01-01)\nbinary: rustc\nhost: x86_64-unknown-linux-gnu\n',
                  cargo='cargo 1.99.0 (def 2026-01-01)', machine='Linux 6.1 x86_64', libc='ldd (GNU libc) 2.39', host='cloud-box', home='/home/agent', cargo_home=None,
                  build_dir='/home/agent/b', target_dir='/home/agent/t', jobs='8', built_at='2026-10-09T12:00:00Z', rebuild_command='env HOME=/home/agent bash build.sh REF OUT',
                  record_file='/cloud/strength.build.json', record_sha256='5' * 64)
    REBUILD_SENTENCE = ("; THIS PROGRAM ({path}, sha256 {sha12}) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) says it is a rebuild of that "
                        "source (build record sha256 {rec12}: engine tree as archived {tree12}, harness source {harness12}, {rustc}), accepted because both self-checks were replayed on "
                        "the registering machine and equal {digests}")

    def rebuilt_engine(self, record=None, **kw):
        return self.build(route='rebuilt', program='/cloud/strength', program_sha='ab' * 32, build_record=self.RECORD if record is None else record, **kw)['engine']

    def test_the_registered_engine_text_is_the_pins_and_says_so_when_the_program_is_a_rebuild(self):
        pin = json.loads(read(self.pin_path))
        self.assertNotIn('REBUILD', pin['engine'])
        self.assertEqual(self.build()['engine'], pin['engine'])
        self.assertEqual(self.build(route='pinned', program='/elsewhere/strength')['engine'], pin['engine'], 'the pinned bytes under another path are still the pinned program')
        rebuilt = self.build(route='rebuilt', program='/cloud/strength', program_sha='ab' * 32, build_record=self.RECORD)
        self.assertEqual(rebuilt['engine'], pin['engine'] + self.REBUILD_SENTENCE.format(path='/cloud/strength', sha12='abababababab', rec12='555555555555', tree12='333333333333',
                                                                                         harness12='bbbbbbbbbbbb', rustc='rustc 1.99.0 (abc 2026-01-01)', digests=DIGESTS_COMMITTED),
                         'the record is named by its own sha256, the engine tree it archived, the harness source and the first line of rustc -vV')
        self.assertEqual((rebuilt['program'], rebuilt['program_sha256']), ('/cloud/strength', 'ab' * 32))
        self.assertNotIn('made on another machine', rebuilt['engine'])
        self.assertNotIn('laptop binary', rebuilt['engine'])

    def test_the_registered_engine_text_does_not_claim_more_than_the_unsigned_record_says(self):
        """The record is written by the builder's own script and proves nothing by itself: the text says it is not signed, says what the record SAYS ('says it is a rebuild'), and
        puts the weight on the replayed self-checks. The older claim ('IS A REBUILD') is gone."""
        engine = self.rebuilt_engine()
        for phrase in ('is NOT the pinned binary', 'written by rl/strength/build.sh, not signed', 'says it is a rebuild of that source', 'accepted because both self-checks were replayed'):
            self.assertIn(phrase, engine)
        for gone in ('IS A REBUILD', 'REBUILD of that source', 'built by rl/strength/build.sh ('):
            self.assertNotIn(gone, engine)

    def test_the_registered_engine_text_names_the_pin_by_its_state_and_never_calls_an_uncommitted_pin_the_committed_one(self):
        """pin_state None (unknown) and 'yes' say 'the committed pin's digests'; anything else (here the test-only 'bypassed', and 'no', which a registration never reaches) says what
        the pin in use really is."""
        for how, state, want in (('no state given', None, DIGESTS_COMMITTED), ('committed', {'state': 'yes', 'sha256': 'e' * 64, 'detail': ''}, DIGESTS_COMMITTED),
                                 ('let through by the test variable', {'state': 'bypassed', 'sha256': 'e' * 64, 'detail': 'x'}, DIGESTS_UNCOMMITTED),
                                 ('not committed', {'state': 'no', 'sha256': 'e' * 64, 'detail': 'x'}, DIGESTS_UNCOMMITTED)):
            with self.subTest(pin=how):
                engine = self.rebuilt_engine(pin_state=state)
                self.assertTrue(engine.endswith(f'and equal {want}'), engine)
                self.assertEqual(engine.count('committed pin'), 1, 'the pin is named once')
                self.assertEqual('NOT the committed pin' in engine, want == DIGESTS_UNCOMMITTED)

    def test_the_two_phrases_for_the_pin_in_use_are_chosen_by_its_state_alone(self):
        for state, want in ((None, DIGESTS_COMMITTED), ('yes', DIGESTS_COMMITTED), ('bypassed', DIGESTS_UNCOMMITTED), ('no', DIGESTS_UNCOMMITTED), ('', DIGESTS_UNCOMMITTED),
                            ('maybe', DIGESTS_UNCOMMITTED)):
            with self.subTest(state=state):
                self.assertEqual(sr.pin_digests(state), want)

    def test_a_build_record_entry_is_its_text_or_not_recorded_and_never_the_text_none(self):
        rec = {'rustc': 'rustc 1.99.0', 'empty': '', 'null': None, 'number': 5, 'list': ['x'], 'mapping': {'a': 1}, 'true': True}
        self.assertEqual(sr.record_text(rec, 'rustc'), 'rustc 1.99.0')
        for key in ('empty', 'null', 'number', 'list', 'mapping', 'true', 'not-there'):
            with self.subTest(entry=key):
                self.assertEqual(sr.record_text(rec, key), 'not recorded')

    def test_the_registered_engine_text_of_a_rebuild_says_when_the_record_has_no_toolchain(self):
        """The first line of rustc -vV is what the text quotes; a record without it (no entry, an empty text, null) says 'toolchain not recorded' there, never the text None and never a
        bare ', not recorded)' that reads as if the record itself were missing."""
        for how, rec in (('no rustc entry', {k: v for k, v in self.RECORD.items() if k != 'rustc'}), ('an empty one', dict(self.RECORD, rustc='')), ('a null one', dict(self.RECORD, rustc=None)),
                         ('only blank lines', dict(self.RECORD, rustc='\n  \n\t\n'))):
            with self.subTest(rustc=how):
                engine = self.rebuilt_engine(rec)
                self.assertIn('harness source bbbbbbbbbbbb, toolchain not recorded), accepted because', engine)
                self.assertNotIn('None', engine)
                self.assertNotIn(', not recorded)', engine)

    def test_the_first_non_empty_line_of_the_toolchain_is_what_the_text_and_the_words_for_a_missing_one_are_chosen_by(self):
        """rustc_line(rec, missing): the first line of the record's rustc that is not blank (a leading blank line is skipped, and so is a line of spaces), else the words the caller
        gave, each sentence its own (the registered engine text, the page's record line and the plan line word the missing toolchain differently)."""
        for how, rustc, want in (('the usual text', 'rustc 1.99.0 (abc 2026-01-01)\nbinary: rustc\nhost: x', 'rustc 1.99.0 (abc 2026-01-01)'), ('a leading blank line', '\nrustc 1.98.0\nbinary: rustc', 'rustc 1.98.0'),
                                 ('leading lines of spaces', '  \n \t \nrustc 1.97.0', 'rustc 1.97.0'), ('one line, no line end', 'rustc 1.96.0', 'rustc 1.96.0'),
                                 ('a line with spaces around it is kept as it is', '  rustc 1.95.0  \nx', '  rustc 1.95.0  ')):
            with self.subTest(rustc=how):
                self.assertEqual(sr.rustc_line({'rustc': rustc}, 'WORDS'), want)
        for how, rec in (('no entry', {}), ('null', {'rustc': None}), ('an empty text', {'rustc': ''}), ('blank lines only', {'rustc': ' \n\n  '}), ('a number', {'rustc': 5}),
                         ('a list', {'rustc': ['rustc 1.9']}), ('true', {'rustc': True})):
            with self.subTest(missing=how):
                for words in ('toolchain not recorded', 'rustc not recorded', 'an unrecorded toolchain'):
                    self.assertEqual(sr.rustc_line(rec, words), words)

    def test_the_block_records_the_pin_the_machine_and_the_build_record_and_no_checkout_tree(self):
        """The engine tree the checkout happened to hold is gone from the block (the build record's tree, as archived, is what a rebuild is held to)."""
        pin = json.loads(read(self.pin_path))
        block = self.build()['slow_report']
        self.assertNotIn('engine_tree_in_checkout', block)
        self.assertEqual((block['engine_ref'], block['engine_tree']), (pin['engine_ref'], pin['engine_tree']))
        self.assertEqual((block['pin_committed'], block['pin_committed_detail'], block['registered_on'], block['build_record']), (None, None, None, None), 'unknown unless the caller says')
        state = {'state': 'bypassed', 'sha256': 'e' * 64, 'detail': 'HEAD has no pin; allowed by the test variable'}
        block = self.build(pin_state=state, registered_on='cloud-box', build_record=self.RECORD)['slow_report']
        self.assertEqual((block['pin_committed'], block['pin_committed_detail'], block['registered_on']), ('bypassed', 'HEAD has no pin; allowed by the test variable', 'cloud-box'))
        self.assertEqual(block['build_record'], self.RECORD, 'the whole record, with the record file and its sha256')
        yes = self.build(pin_state={'state': 'yes', 'sha256': 'e' * 64, 'detail': ''})['slow_report']
        self.assertEqual((yes['pin_committed'], yes['pin_committed_detail']), ('yes', None), 'a committed pin has nothing to explain: no detail, not an empty text')

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
               'pin_committed', 'pin_committed_detail', 'registered_on', 'build_record', 'school_rule', 'school_days')
PIN_REL = 'rl/strength/slow_report_pin.json'


def slow_report_values(text):
    """{key: value} of the '- key: `value`' lines of the '## Slow report' section of PREREGISTRATION.md, in the order they are printed."""
    section = text.split('## Slow report\n')[1].split('\n## ')[0]
    return dict(m.groups() for m in (re.fullmatch(r'- (\w+): `(.*)`', l) for l in section.splitlines()) if m)


def shown(value, key=None):
    """How strength_prereg.py prints a block entry: a null in words ('none' for the pin's detail and the build record, which have nothing to say; 'not found' for a fact about the
    checkout that was not there), a mapping as sorted JSON, anything else as it is."""
    if value is None:
        return 'none' if key in ('pin_committed_detail', 'build_record') else 'not found'
    return json.dumps(value, sort_keys=True, ensure_ascii=False) if isinstance(value, dict) else value


def git_said(repo):
    """The first line (200 characters at most) that git prints on stderr when it is asked for the pin at HEAD of `repo`: what pin_commit_state quotes after 'git said:'. Asked of
    git itself, so the words are whatever this machine's git says; '' when it says nothing."""
    env = {k: v for k, v in os.environ.items() if k not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR',
                                                          'GIT_NAMESPACE', 'GIT_PREFIX')}
    r = subprocess.run(['git', '-C', repo, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], capture_output=True, env=dict(env, GIT_OPTIONAL_LOCKS='0'))
    said = r.stderr.decode('utf-8', 'replace').strip()
    return said.splitlines()[0][:200] if said else ''


def not_committed_detail(repo):
    """What pin_commit_state says when HEAD of `repo` has no pin: the old words, then what git said."""
    said = git_said(repo)
    return f'HEAD has no {PIN_REL} in {repo} (not a git repository, no commit, or the file is not committed)' + (f'; git said: {said}' if said else '')


def bypass_detail(repo):
    """What pin_commit_state says when HEAD of `repo` has no pin and the test variable lets it through."""
    return f'{not_committed_detail(repo)}; allowed by {sr.ALLOW_UNCOMMITTED_PIN} (test use)'


class RouteWorld(SelfCheckWorld):
    """The fixture of the program routes: a harness source in the temporary repository (HARNESS_FILES) that the pin's harness_source_sha256 names, a git commit in it that holds
    the pinned engine (engine/, whose tree the pin's engine_tree names), and a second copy of the program (self.rebuilt, other bytes) with its own digests beside it and the build
    record build.sh would have written for it (self.record), as a cloud rebuild would be."""

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
        self.rebuilt_record = self.record(self.rebuilt)
        return self

    def record(self, program, **changes):
        """The build record rl/strength/build.sh writes beside `program` (program + '.build.json'), for this world's pin; a change given as None removes the entry. Returns the dict."""
        rec = dict(schema=1, program=program, program_sha256=sha(program), engine_arg=self.pin['engine_ref'], engine=f"{self.pin['engine_ref']} engine tree {self.pin['engine_tree']}",
                   engine_ref=self.pin['engine_ref'], engine_tree_archived=self.pin['engine_tree'], harness_source_sha256=HARNESS_HASH,
                   rustc='rustc 1.99.0 (abcdef012 2026-01-01)\nbinary: rustc\nhost: x86_64-unknown-linux-gnu\n', cargo='cargo 1.99.0 (abcdef012 2026-01-01)', machine='Linux 6.1.0 x86_64',
                   libc='ldd (GNU libc) 2.39', host='cloud-box-7', home='/home/agent', cargo_home=None, build_dir='/home/agent/slow_report_kx3/build',
                   target_dir='/home/agent/slow_report_kx3/target', jobs='8', built_at='2026-10-09T12:00:00Z',
                   rebuild_command='env HOME=/home/agent bash /home/agent/repo/rl/strength/build.sh ' + self.pin['engine_ref'] + ' ' + program)
        for k, v in changes.items():
            if v is None:
                rec.pop(k, None)
            else:
                rec[k] = v
        write(program + '.build.json', json.dumps(rec, indent=1) + '\n')
        return rec

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
        self.assertEqual({k: values[k] for k in ROUTE_LINES}, {k: shown(v, k) for k, v in expected.items()})
        keys = list(values)
        self.assertEqual(keys[keys.index('pin') + 1:], list(ROUTE_LINES), 'after the pin, once each, in this order')

    def route_expected(self, route, **more):
        """The entries every route test expects, for this world: the bypassed pin (these worlds' pin is not committed in their repository), this machine's name."""
        expected = dict(program_route=route, pinned_program=self.program, pinned_program_sha256=self.pin['program_sha256'], harness_source_sha256=HARNESS_HASH,
                        harness_source_checkout_sha256=HARNESS_HASH, engine_ref=self.pin['engine_ref'], engine_tree=self.pin['engine_tree'], pin_committed='bypassed',
                        pin_committed_detail=bypass_detail(self.repo), registered_on=socket.gethostname(), build_record=None, school_rule='off', school_days='mon,tue,wed,thu,fri')
        expected.update(more)
        return expected


class ProgramRoutes(RouteWorld):
    """What a registration says about the program it will run: PREREGISTRATION.md and the manifest's slow-report block name the route (the pinned binary, or a rebuild given
    with --program), the pinned program and its sha256, the harness source hashes, the engine ref and tree, whether the pin was the committed one and on which machine the run was
    registered, the build record of a rebuild and the school-morning choice; and the self-check text, whichever way it was obtained, is tied to the sha256 of the program it was
    measured on."""

    def test_the_pinned_binary_is_registered_with_the_pins_text_and_the_route_named(self):
        man, cfg, text = self.registered()
        self.assertEqual((man['program'], man['program_sha256']), (self.program, self.pin['program_sha256']))
        self.assertEqual(self.calls(), [], 'the pinned text is recorded; the 12 games are not replayed')
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'])
        self.assertEqual(man['selfcheck_source'], {'km3': PIN_GIVEN, 'kx3': PIN_GIVEN})
        self.assertEqual(cfg['selfcheck_given_program_sha256'], self.pin['selfcheck_measured_on_sha256'], 'the config says which binary the pinned text was measured on')
        self.assertNotIn('selfcheck_how', cfg)
        self.assert_route_lines(man, text, self.route_expected('pinned'))
        self.assertNotIn('engine_tree_in_checkout', man['slow_report'], 'what the checkout happens to hold is no longer recorded: a rebuild is held to its build record')
        self.assertNotIn('engine_tree_in_checkout', text)
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
        self.assertEqual(man['selfcheck'], self.pin['selfcheck'], 'equal to the pin in use (a difference refuses the registration)')
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED_UNCOMMITTED, 'kx3': REPLAYED_UNCOMMITTED}, "this world's pin is not the committed one: the record says what it is")
        self.assertEqual((cfg['selfcheck_given_program_sha256'], cfg['selfcheck_how'], cfg['program'], cfg['program_sha256']), (actual, 'replayed', self.rebuilt, actual),
                         'the replayed text carries the sha256 of the program it was just measured on, not the pin\'s')
        record_file = self.rebuilt + '.build.json'
        record = dict(self.rebuilt_record, record_file=record_file, record_sha256=sha(record_file))
        self.assert_route_lines(man, text, self.route_expected('rebuilt', build_record=record))
        self.assertEqual(man['slow_report']['build_record'], cfg['slow_report']['build_record'], 'the config the registration was made from carries the same record')
        rustc = self.rebuilt_record['rustc'].splitlines()[0]
        engine = (self.pin['engine'] + f"; THIS PROGRAM ({self.rebuilt}, sha256 {actual[:12]}) is NOT the pinned binary: its build record (written by rl/strength/build.sh, not signed) "
                  f"says it is a rebuild of that source (build record sha256 {record['record_sha256'][:12]}: engine tree as archived {self.pin['engine_tree'][:12]}, harness source "
                  f"{HARNESS_HASH[:12]}, {rustc}), accepted because both self-checks were replayed on the registering machine and equal {DIGESTS_UNCOMMITTED}")
        self.assertEqual((man['engine'], cfg['engine']), (engine, engine), 'the registered engine text says this program is not the pinned binary, names it and the record it came with')
        self.assertIn(f'engine: {engine}; repository commit', text)
        line = ' (replayed by slow_report.py on the registering machine just before registration and equal to the pin file in use, which is NOT the committed pin: test use)'
        self.assertEqual(text.count(line), 2, 'one line per pilot says so')
        self.assertNotIn('equal to the committed pin', text, 'a pin that is not the committed one is not called that')
        self.assertNotIn("the committed pin's digests", text)
        self.assertNotIn('not replayed', text)
        self.assertIn(f'Program: `{self.rebuilt}` sha256 `{actual}`', text)
        self.assertIn('a rebuild of the pinned source by its build record (accepted after both self-checks were replayed on the registering machine;', text.split('## Run')[1],
                      'the Run paragraph says so too')
        self.assertNotIn('REBUILD', text.split('## Run')[1], 'in the words of a record that says it, not as a fact (the record is not signed)')

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
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED_UNCOMMITTED, 'kx3': REPLAYED_UNCOMMITTED})
        self.assertEqual((cfg['selfcheck_given_program_sha256'], cfg['selfcheck_how']), (sha(self.program), 'replayed'))
        self.assertEqual(slow_report_values(text)['program_route'], 'pinned', 'a replay on the pinned binary is still the pinned route')

    def test_a_rebuild_whose_self_check_differs_from_the_pin_registers_nothing(self):
        write(os.path.join(self.cloud, 'digests.json'), json.dumps({'km3': 'km3pin', 'kx3': 'a-different-digest'}))
        code, out, err = self.cli('--deals', '1', '--register-only', '--program', self.rebuilt)
        self.assertNotEqual(code, 0)
        self.assertIn('self-check of kx3 does not match the pin', str(code))
        self.assertFalse(os.path.exists(self.out_root), 'nothing is written')

    def test_the_pinned_route_does_not_depend_on_what_the_checkout_or_the_pins_tree_say(self):
        """A checkout is not part of the pinned binary: the pinned route registers whatever the checkout holds for the pinned ref (a pin that names another tree, or none, a missing
        commit, no repository at all), and has no build record."""
        for how, edit in (('the pin names another tree', lambda: self.edit_pin(engine_tree='f' * 40)), ('the pin names no tree', lambda: self.edit_pin(engine_tree=None)),
                          ('the pin names no ref', lambda: self.edit_pin(engine_ref=None)), ('the checkout does not have the pinned commit', lambda: self.edit_pin(engine_ref='0' * 40)),
                          ('the checkout is not a git repository', lambda: shutil.rmtree(os.path.join(self.repo, '.git')))):
            with self.subTest(case=how):
                self.make()
                edit()
                man, cfg, text = self.registered()
                self.assertEqual(man['slow_report']['program_route'], 'pinned')
                self.assertEqual(man['slow_report']['engine_tree'], self.pin.get('engine_tree'))
                self.assertIsNone(man['slow_report']['build_record'])
                self.assertEqual(slow_report_values(text)['build_record'], 'none', 'the pinned binary has no build record: said in words, never as the text None, and not as "not found"')

    def test_a_rebuild_is_held_to_its_build_record_and_not_to_what_the_checkout_holds(self):
        """The old check read the engine tree back from the checkout's git objects, which a cloud clone may not have and which says nothing about what was compiled. The tree
        that counts is the one build.sh archived and recorded: the pin and the record agree, the checkout is not asked."""
        for how, edit in (('the checkout is not a git repository', lambda: shutil.rmtree(os.path.join(self.repo, '.git'))),
                          ('the checkout does not have the pinned commit', lambda: (self.edit_pin(engine_ref='0' * 40), self.record(self.rebuilt, engine_ref='0' * 40))),
                          ('the pin names a tree the checkout does not have', lambda: (self.edit_pin(engine_tree='f' * 40), self.record(self.rebuilt, engine_tree_archived='f' * 40)))):
            with self.subTest(case=how):
                self.make()
                edit()
                man, cfg, text = self.registered('--program', self.rebuilt)
                self.assertEqual(man['slow_report']['program_route'], 'rebuilt')
                self.assertEqual(man['slow_report']['build_record']['engine_tree_archived'], self.pin['engine_tree'])
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
        plan_lines = {('on', True): 'on school days ({days}) the run pauses from 5:15 am to 5 pm Chicago time (the school-morning rule), so the calendar time is longer',
                      ('on', False): 'school-morning rule: on, but with no school days set it never pauses the run',
                      ('off', True): 'school-morning rule: OFF for this run (it never pauses for school mornings; the choice is recorded in the registration and carried by the resume command)',
                      ('off', False): 'school-morning rule: OFF for this run (it never pauses for school mornings; the choice is recorded in the registration and carried by the resume command)'}
        for how, flags, school, rule, days, tail in cases:
            with self.subTest(choice=how):
                shutil.rmtree(self.out_root, ignore_errors=True)
                code, out, err = self.cli('--deals', '1', '--dry-run', *flags, school=school)  # (before the registration: a dry run refuses a folder that is already there)
                self.assertEqual(code, 0, str(code) + err)
                wanted = plan_lines[(rule, bool(days))].format(days=days)
                self.assertEqual([l for l in out.splitlines() if 'school' in l], [f'{T.HEADLINE_START}my-list v km3 on the public panel] {wanted}'], 'the plan says what the rule will do, once')
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


class BuildRecordChecks(RouteWorld):
    """A program whose sha256 is not the pinned one is a rebuild, and is accepted only with the record rl/strength/build.sh writes beside it (PROGRAM.build.json): for exactly that
    file (its program sha256), with the engine tree build.sh ARCHIVED and the harness source it compiled equal to the pin's, and the engine ref equal to the pin's when both have one.
    The record is read right after the program check and before anything is replayed or written."""

    HINT = 'rl/strength/build.sh writes it beside the program it builds (build with it, to the path you pass here)'
    TAG = '[kx3 (d513e37b) v km3] '

    def refusal(self, *flags):
        """A registration (or a dry run) of the rebuilt program must be refused before the hours-long replay and before anything is written; returns the refusal."""
        code, out, err = self.cli('--deals', '1', *flags, '--program', self.rebuilt)
        self.assertIsInstance(code, str, out + err)
        self.assertTrue(code.startswith(self.TAG + 'REFUSED: '), code)
        self.assertTrue(code.endswith(' Nothing was written.'), code)
        self.assertEqual((self.calls(), self.rebuilt_calls()), ([], []), 'refused before the hours-long replay')
        self.assertFalse(os.path.exists(self.out_root), 'nothing is written')
        return code

    def test_a_rebuild_with_no_build_record_is_refused_before_anything_is_replayed_and_a_dry_run_says_so_too(self):
        record = self.rebuilt + '.build.json'
        os.remove(record)
        want = f'{self.TAG}REFUSED: {self.rebuilt} has no build record ({record}); {self.HINT}. Nothing was written.'
        for flags in (('--register-only',), ('--dry-run',), ('--register-only', '--selfcheck')):
            with self.subTest(flags=flags):
                self.assertEqual(self.refusal(*flags), want)
        os.mkdir(record)  # a folder of that name is no record either
        self.assertEqual(self.refusal('--register-only'), want)

    def test_a_record_that_cannot_be_read_or_is_not_a_schema_1_record_is_refused(self):
        record = self.rebuilt + '.build.json'
        good = json.loads(read(record))
        for how, data in (('not JSON', b'{not json'), ('empty', b''), ('cut off', json.dumps(good).encode()[:40]), ('not text at all', b'\xff\xfe\x00\x01')):
            with self.subTest(unreadable=how):
                write_bytes(record, data)
                code = self.refusal('--register-only')
                self.assertTrue(code.startswith(f'{self.TAG}REFUSED: the build record {record} cannot be read ('), code)
                self.assertTrue(code.endswith(f'); {self.HINT}. Nothing was written.'), code)
        for how, rec in (('a list', [good]), ('null', None), ('a number', 7), ('text', 'schema 1'), ('schema 2', dict(good, schema=2)), ('schema as text', dict(good, schema='1')),
                         ('schema 1.5', dict(good, schema=1.5)), ('schema null', dict(good, schema=None)), ('no schema entry', {k: v for k, v in good.items() if k != 'schema'}),
                         ('schema true (python counts True as 1)', dict(good, schema=True)), ('schema 1.0 (python counts 1.0 as 1)', dict(good, schema=1.0)),
                         ('schema as a list', dict(good, schema=[1])), ('schema 0', dict(good, schema=0)), ('schema false (python counts False as 0)', dict(good, schema=False))):
            with self.subTest(not_a_schema_1_record=how):
                write(record, json.dumps(rec))
                self.assertEqual(self.refusal('--register-only'), f'{self.TAG}REFUSED: the build record {record} is not a schema 1 record; {self.HINT}. Nothing was written.')
        write(record, json.dumps(good))
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual(man['slow_report']['build_record']['schema'], 1, 'and the integer 1 is accepted')

    TEXT_KEYS = ('program_sha256', 'engine_arg', 'engine', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'rustc', 'cargo', 'machine', 'host', 'built_at', 'rebuild_command')

    def test_the_entries_of_a_record_that_the_page_prints_as_text_must_be_text_when_they_are_there(self):
        """A record whose rustc is a number or a list is damaged (or made by hand): the page and the plan would print it, so it is refused, naming the entry, before anything is
        replayed or written. A null entry, or no entry at all, is not an error here (the record then says 'not recorded' where it is printed); the entries the check itself needs
        (program sha256, engine tree, harness source) are refused when null by their own checks."""
        self.assertEqual(sr.BUILD_RECORD_TEXT_KEYS, self.TEXT_KEYS, 'the entries that are held to being text')
        for key in self.TEXT_KEYS:
            for how, value in (('a number', 5), ('true', True), ('a list', ['x']), ('a mapping', {'x': 1}), ('a float', 1.5)):
                with self.subTest(entry=key, record=how):
                    self.make()
                    self.record(self.rebuilt, **{key: value})
                    self.assertEqual(self.refusal('--register-only'), f'{self.TAG}REFUSED: the build record {self.rebuilt}.build.json has an entry {key} that is not text; {self.HINT}. Nothing was written.')
        for key in set(self.TEXT_KEYS) - {'program_sha256', 'engine_tree_archived', 'harness_source_sha256'}:
            for how, gone in (('null', lambda r: r.update({key: None})), ('no entry', lambda r: r.pop(key, None))):
                with self.subTest(entry=key, accepted=how):
                    self.make()
                    self.rewrite_record(gone)
                    got = sr.read_build_record(self.rebuilt, self.pin)
                    self.assertEqual(got.get(key), None)
                    man, cfg, text = self.registered('--program', self.rebuilt)
                    self.assertEqual(man['slow_report']['program_route'], 'rebuilt')
                    self.assertNotIn('None', man['engine'])
        for key in ('program_sha256', 'engine_tree_archived', 'harness_source_sha256'):
            with self.subTest(entry=key, empty_text='is text, and is refused by the check that needs it'):
                self.make()
                self.record(self.rebuilt, **{key: ''})
                self.assertNotIn('is not text', self.refusal('--register-only'))

    def test_a_record_is_checked_for_text_before_the_program_and_the_pin_it_is_held_to(self):
        """The type check comes first: a program sha256 of 7 is damage, not 'a record for another program', and a tree of 5 is not 'another tree'."""
        self.record(self.rebuilt, program_sha256=7, engine_tree_archived=5, harness_source_sha256='f' * 64)
        self.assertIn('has an entry program_sha256 that is not text', self.refusal('--register-only'))
        self.rewrite_record(lambda r: r.update(program_sha256=sha(self.rebuilt)))
        self.assertIn('has an entry engine_tree_archived that is not text', self.refusal('--register-only'))

    def test_a_record_written_for_another_program_is_refused_naming_both_sha256_values(self):
        for how, kw in (('the record of another build', lambda: dict(program_sha256='c' * 64)), ('the record of the pinned binary', lambda: dict(program_sha256=self.pin['program_sha256'])),
                        ('no program sha256 in it', lambda: dict(program_sha256=None)), ('an empty text for it', lambda: dict(program_sha256=''))):
            with self.subTest(record=how):
                self.make()
                self.record(self.rebuilt, **kw())
                recorded = str(json.loads(read(self.rebuilt + '.build.json')).get('program_sha256'))[:12]
                self.assertEqual(self.refusal('--register-only'), f'{self.TAG}REFUSED: the build record {self.rebuilt}.build.json is for a program with sha256 {recorded}, but {self.rebuilt} has sha256 '
                                                                   f'{sha(self.rebuilt)[:12]}: the record belongs to the file it was written for. Nothing was written.')
        self.make()
        built = sha(self.rebuilt)
        write(self.rebuilt, read(self.rebuilt) + '# edited after it was built\n', mode=0o755)
        self.assertNotEqual(sha(self.rebuilt), built)
        self.assertIn(f'is for a program with sha256 {built[:12]}, but {self.rebuilt} has sha256 {sha(self.rebuilt)[:12]}', self.refusal('--register-only'), 'a program changed after its record was written')

    def test_a_record_with_another_engine_tree_or_harness_source_than_the_pins_is_refused_naming_both(self):
        for key, what, pinned in (('engine_tree_archived', 'engine tree', lambda: self.pin['engine_tree']), ('harness_source_sha256', 'harness source', lambda: HARNESS_HASH)):
            for how, value in (('another one', 'e' * 40), ('none', None), ('an empty text', ''), ('the pinned one in capitals', 'PINNED')):
                with self.subTest(entry=key, record=how):
                    self.make()
                    want = pinned()
                    value = want.upper() if value == 'PINNED' else value
                    self.record(self.rebuilt, **{key: value})
                    self.assertEqual(self.refusal('--register-only'), f'{self.TAG}REFUSED: the build record says the {what} that went into {self.rebuilt} is {str(value)[:12]}, '
                                                                       f'not the pinned {want[:12]}, so it is not a build of the pinned source. Nothing was written.')

    def test_the_engine_ref_of_the_record_is_held_to_the_pins_when_both_have_one(self):
        self.record(self.rebuilt, engine_ref='e' * 40)
        self.assertEqual(self.refusal('--register-only'), f"{self.TAG}REFUSED: the build record says the engine ref was {'e' * 12}, not the pinned {self.pin['engine_ref'][:12]}. Nothing was written.")

        def pin_names_none():
            self.edit_pin(engine_ref=None)
            self.rewrite_record(lambda r: r.update(engine_ref='e' * 40))
        for how, edit in (('a build from a folder has no ref (null)', lambda: self.rewrite_record(lambda r: r.update(engine_ref=None))),
                          ('no ref entry', lambda: self.rewrite_record(lambda r: r.pop('engine_ref'))), ('the pin names none', pin_names_none)):
            with self.subTest(accepted=how):
                self.make()
                edit()
                man, cfg, text = self.registered('--program', self.rebuilt)
                self.assertEqual(man['slow_report']['program_route'], 'rebuilt')

    def rewrite_record(self, change):
        path = self.rebuilt + '.build.json'
        rec = json.loads(read(path))
        change(rec)
        write(path, json.dumps(rec))

    def test_a_pin_without_an_engine_tree_or_a_harness_hash_cannot_check_a_rebuild_and_refuses_it(self):
        self.edit_pin(engine_tree=None)
        self.assertEqual(self.refusal('--register-only'), f'{self.TAG}REFUSED: the pin has no engine_tree, so a rebuild cannot be checked against it. Nothing was written.')
        pin = {k: v for k, v in self.pin.items() if k != 'harness_source_sha256'}  # (load_pin refuses such a pin, so only the function itself can be asked)
        pin['engine_tree'] = self.rebuilt_record['engine_tree_archived']
        with self.assertRaises(SystemExit) as cm:
            sr.read_build_record(self.rebuilt, pin)
        self.assertEqual(cm.exception.code, 'REFUSED: the pin has no harness_source_sha256, so a rebuild cannot be checked against it. Nothing was written.')

    def test_the_checks_run_in_a_fixed_order_so_the_first_wrong_thing_is_the_one_named(self):
        self.record(self.rebuilt, program_sha256='c' * 64, engine_tree_archived='e' * 40, harness_source_sha256='f' * 64, engine_ref='9' * 40)
        for fixed, phrase in ((None, 'is for a program with sha256 cccccccccccc'), (dict(program_sha256=sha(self.rebuilt)), 'the build record says the engine tree that went into'),
                              (dict(engine_tree_archived=self.pin['engine_tree']), 'the build record says the harness source that went into'),
                              (dict(harness_source_sha256=HARNESS_HASH), f"the build record says the engine ref was {'9' * 12}")):
            if fixed:
                self.rewrite_record(lambda r: r.update(fixed))
            self.assertIn(phrase, self.refusal('--register-only'))
        self.rewrite_record(lambda r: r.update(engine_ref=self.pin['engine_ref']))
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual(man['slow_report']['program_route'], 'rebuilt')

    def test_an_accepted_record_comes_back_whole_with_its_file_and_its_sha256_and_is_left_as_it_was(self):
        path = self.rebuilt + '.build.json'
        before = read_bytes(path)
        got = sr.read_build_record(self.rebuilt, self.pin)
        self.assertEqual(got, dict(self.rebuilt_record, record_file=path, record_sha256=hashlib.sha256(before).hexdigest()))
        self.assertEqual(read_bytes(path), before)
        moved = os.path.join(self.tmp, 'moved', 'program')  # the pair copied elsewhere: the record belongs to the bytes of the file, not to its path
        write(moved, read(self.rebuilt), mode=0o755)
        write(moved + '.build.json', read(path))
        again = sr.read_build_record(moved, self.pin)
        self.assertEqual((again['record_file'], again['program'], again['program_sha256']), (moved + '.build.json', self.rebuilt, sha(moved)))

    def test_a_record_with_only_the_entries_the_check_needs_is_accepted_and_every_text_it_lacks_is_said_as_not_recorded(self):
        """Only the program sha256, the engine tree and the harness source are needed. Every other entry the page and the plan print is 'not recorded' when the record has none
        (never the text None): the toolchain in the plan and the engine text, here; the page's own line is checked with the page."""
        write(self.rebuilt + '.build.json', json.dumps(dict(schema=1, program_sha256=sha(self.rebuilt), engine_tree_archived=self.pin['engine_tree'], harness_source_sha256=HARNESS_HASH)))
        code, out, err = self.cli('--deals', '1', '--dry-run', '--program', self.rebuilt)
        self.assertEqual(code, 0, str(code) + err)
        self.assertIn(f"harness source {HARNESS_HASH[:12]}, built with an unrecorded toolchain); both self-checks will be replayed on this machine", out)
        self.assertNotIn('None', out)
        self.assertNotIn('built with not recorded', out, 'a sentence that cannot be read: the plan words a missing toolchain for its own sentence')
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual(man['slow_report']['build_record']['engine_tree_archived'], self.pin['engine_tree'])
        self.assertIn(f'harness source {HARNESS_HASH[:12]}, toolchain not recorded), accepted because both self-checks were replayed on the registering machine', man['engine'])
        self.assertNotIn('None', man['engine'])
        self.assertNotIn(', not recorded)', man['engine'], 'and the registered text words it for its own sentence too')

    def plan_lines(self, out):
        return [l.split('] ', 1)[1] for l in out.splitlines()]

    def test_the_plan_names_the_pin_the_build_record_and_the_replay_still_to_come_and_a_dry_run_replays_nothing(self):
        code, out, err = self.cli('--deals', '1', '--dry-run', '--program', self.rebuilt)
        self.assertEqual(code, 0, str(code) + err)
        record = self.rebuilt + '.build.json'
        pin12 = self.pin['program_sha256'][:12]
        self.assertIn(f"pin committed: bypassed ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; {bypass_detail(self.repo)})", self.plan_lines(out))
        self.assertIn(f"program {self.rebuilt} (sha256 {sha(self.rebuilt)[:12]}) is NOT the pinned binary (sha256 {pin12}): its build record (strength.build.json, sha256 "
                      f"{sha(record)[:12]}) says it is a rebuild of the pinned source (engine tree as archived {self.pin['engine_tree'][:12]}, harness source {HARNESS_HASH[:12]}, built with "
                      f"rustc 1.99.0 (abcdef012 2026-01-01)); both self-checks will be replayed on this machine against {DIGESTS_UNCOMMITTED} before anything is registered "
                      "(hours for kx3), and the checkout's harness source equals the pinned build's", self.plan_lines(out))
        self.assertNotIn('IS A REBUILD', out)
        self.assertNotIn('is a REBUILD', out)
        self.assertIn(f"(rebuilt, sha256 {sha(self.rebuilt)[:12]}), with the comparison with km3 on the same deals in the page", out)
        self.assertEqual((self.calls(), self.rebuilt_calls()), ([], []))
        self.assertFalse(os.path.exists(self.out_root))
        code, out, err = self.cli('--deals', '1', '--dry-run')
        self.assertEqual(code, 0, str(code) + err)
        self.assertIn(f"pin committed: bypassed ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; ", out)
        self.assertNotIn('REBUILD', out, 'the pinned binary has no build record to speak of')
        self.assertNotIn('NOT the pinned binary', out)
        self.assertIn('(pinned, sha256 ', out)

    def test_the_pinned_route_never_reads_a_build_record(self):
        copy = os.path.join(self.tmp, 'copy', 'strength')
        write(copy, read(self.program), mode=0o755)
        write(copy + '.build.json', '{not json: a record the pinned route must not look at')
        man, cfg, text = self.registered('--program', copy)
        self.assertEqual((man['slow_report']['program_route'], man['slow_report']['build_record']), ('pinned', None))


class CommittedPinCheck(RouteWorld):
    """The pin is trusted for what the program is (its sha256, its self-check texts, what a rebuild must replay), so a pin that is not the one committed at HEAD of the repository the run
    is made from is refused: a hand-edited pin, an old copy, a pin in a folder that is not a checkout. Every other test sets the test-only variable
    SLOW_REPORT_ALLOW_UNCOMMITTED_PIN for its hand-made pin; these run with it unset, in a temporary git repository whose HEAD does or does not hold the very bytes of the pin."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop(sr.ALLOW_UNCOMMITTED_PIN, None)

    def commit_pin(self, data=None, repo=None, subdir=''):
        """Commit `data` (default: the bytes of this world's pin) as rl/strength/slow_report_pin.json in `repo` (under `subdir`); returns the path."""
        repo = repo or self.repo
        rel = os.path.join(subdir, *PIN_REL.split('/'))
        path = os.path.join(repo, rel)
        write_bytes(path, read_bytes(self.pin_path) if data is None else data)
        git(repo, 'add', rel)
        git(repo, 'commit', '-q', '-m', 'the pin')
        return path

    def no_detail(self, repo=None):
        return not_committed_detail(repo or self.repo)

    def refused(self, detail):
        return (f'REFUSED: the pin is not the committed one: {detail}. A slow report trusts the pin for what the program is, so it uses only {PIN_REL} as committed at HEAD '
                '(commit the pin, in the repository you run from; a hand-edited or copied pin is refused). Nothing was written.')

    def test_a_pin_with_the_very_bytes_committed_at_head_is_the_committed_pin_wherever_the_file_is(self):
        in_repo = self.commit_pin()
        elsewhere = os.path.join(self.tmp, 'copy', 'pin.json')  # a copy, byte for byte, in another folder: the bytes decide, not the path
        write_bytes(elsewhere, read_bytes(self.pin_path))
        for path in (in_repo, self.pin_path, elsewhere):
            with self.subTest(pin=path):
                st = sr.pin_commit_state(self.repo, path)
                self.assertEqual(st, {'state': 'yes', 'sha256': sha(self.pin_path), 'detail': ''})
                self.assertEqual(sr.require_committed_pin(self.repo, path), st)

    def test_a_pin_that_differs_in_any_byte_from_the_committed_one_is_not_the_committed_pin(self):
        self.commit_pin()
        original = read_bytes(self.pin_path)
        pin = json.loads(original)
        for how, data in (('one newline more', original + b'\n'), ('one space less', original.replace(b' ', b'', 1)), ('a CRLF at the end', original + b'\r\n'),
                          ('the same JSON in another layout', json.dumps(pin, indent=4).encode()), ('the same JSON indented by one', json.dumps(pin, indent=1).encode()),
                          ('the program hash changed', original.replace(pin['program_sha256'].encode(), b'f' * 64, 1)), ('empty', b'')):
            with self.subTest(pin=how):
                self.assertNotEqual(data, original)
                path = os.path.join(self.tmp, 'edited.json')
                write_bytes(path, data)
                st = sr.pin_commit_state(self.repo, path)
                self.assertEqual(st, {'state': 'no', 'sha256': hashlib.sha256(data).hexdigest(),
                                      'detail': f'the pin file (sha256 {hashlib.sha256(data).hexdigest()[:12]}) differs from the {PIN_REL} committed at HEAD '
                                                f'(sha256 {hashlib.sha256(original).hexdigest()[:12]})'})
                with self.assertRaises(SystemExit) as cm:
                    sr.require_committed_pin(self.repo, path)
                self.assertEqual(cm.exception.code, self.refused(st['detail']))

    def test_only_what_is_committed_at_head_counts_not_the_work_tree_nor_the_index_nor_an_older_commit(self):
        path = self.commit_pin()
        original = read_bytes(path)
        write_bytes(path, original + b'\n')  # edited in the work tree
        self.assertEqual(sr.pin_commit_state(self.repo, path)['state'], 'no')
        git(self.repo, 'add', PIN_REL)  # staged
        self.assertEqual(sr.pin_commit_state(self.repo, path)['state'], 'no')
        git(self.repo, 'commit', '-q', '-m', 'the edited pin')  # committed: it is HEAD's now
        self.assertEqual(sr.pin_commit_state(self.repo, path)['state'], 'yes')
        write_bytes(path, original)  # the older commit's bytes are not HEAD's
        self.assertEqual(sr.pin_commit_state(self.repo, path)['state'], 'no')

    def test_a_pin_that_is_not_committed_at_all_is_not_the_committed_pin_and_the_detail_says_why(self):
        plain = os.path.join(self.tmp, 'plain')
        os.makedirs(plain)
        fresh = os.path.join(self.tmp, 'fresh')
        os.makedirs(fresh)
        subprocess.run(['git', '-C', fresh, 'init', '-q'], check=True, capture_output=True)
        for how, repo in (('commits but not the pin', self.repo), ('a repository with no commit', fresh), ('not a git repository', plain)):
            with self.subTest(repo=how):
                st = sr.pin_commit_state(repo, self.pin_path)
                self.assertEqual(st, {'state': 'no', 'sha256': sha(self.pin_path), 'detail': self.no_detail(repo)})
                self.assertTrue(st['detail'].startswith(f'HEAD has no {PIN_REL} in {repo} (not a git repository, no commit, or the file is not committed); git said: '), st['detail'])
                self.assertEqual(st['detail'].count('git said:'), 1)
                self.assertNotIn('safe.directory', st['detail'], 'none of these is a folder that git refuses as unsafe')
        empty_bin = os.path.join(self.tmp, 'empty-bin')
        os.makedirs(empty_bin)
        with mock.patch.dict(os.environ, {'PATH': empty_bin}):
            st = sr.pin_commit_state(self.repo, self.pin_path)
        self.assertEqual(st, {'state': 'no', 'sha256': sha(self.pin_path), 'detail': 'git is not available, so the committed pin cannot be read'})

    def test_the_committed_file_is_the_one_in_the_folder_the_run_is_made_from(self):
        big = os.path.join(self.tmp, 'big')
        subprocess.run(['git', '-C', self.tmp, 'init', '-q', big], check=True, capture_output=True)
        self.commit_pin(repo=big, subdir='sub')
        inner = os.path.join(big, 'sub')
        self.assertEqual(sr.pin_commit_state(inner, self.pin_path)['state'], 'yes', 'the run is made from sub/: its rl/strength/slow_report_pin.json is the committed one')
        self.assertEqual(sr.pin_commit_state(big, self.pin_path)['state'], 'no', 'the folder above has no such file at its root')

    def test_the_test_only_variable_turns_no_into_bypassed_with_the_reason_kept_and_an_empty_value_is_not_set(self):
        self.assertEqual(sr.ALLOW_UNCOMMITTED_PIN, 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN')
        for value in ('1', 'yes', '0', 'false', ' '):
            with self.subTest(value=value), mock.patch.dict(os.environ, {sr.ALLOW_UNCOMMITTED_PIN: value}):
                st = sr.pin_commit_state(self.repo, self.pin_path)
                self.assertEqual(st, {'state': 'bypassed', 'sha256': sha(self.pin_path), 'detail': f'{self.no_detail()}; allowed by SLOW_REPORT_ALLOW_UNCOMMITTED_PIN (test use)'})
                self.assertEqual(sr.require_committed_pin(self.repo, self.pin_path), st, 'and nothing is refused')
        with mock.patch.dict(os.environ, {sr.ALLOW_UNCOMMITTED_PIN: ''}):
            self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path)['state'], 'no')
        self.commit_pin()
        with mock.patch.dict(os.environ, {sr.ALLOW_UNCOMMITTED_PIN: '1'}):
            self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path), {'state': 'yes', 'sha256': sha(self.pin_path), 'detail': ''}, 'a committed pin is committed, not bypassed')

    def test_a_new_registration_or_dry_run_with_a_pin_that_is_not_the_committed_one_is_refused_before_anything_is_trusted(self):
        want = f'{BuildRecordChecks.TAG}' + self.refused(self.no_detail())
        for flags in (('--register-only',), ('--dry-run',), ('--register-only', '--selfcheck')):
            with self.subTest(flags=flags):
                code, out, err = self.cli('--deals', '1', *flags)
                self.assertEqual(code, want)
                self.assertEqual(out, '', 'refused before it printed a plan')
                self.assertFalse(os.path.exists(self.out_root))
                self.assertEqual((self.calls(), self.rebuilt_calls()), ([], []))
        # before the program is looked at, so a program that is not the pinned build, or is not there, is not what the refusal is about
        write(self.program, read(self.program) + '# other bytes\n', mode=0o755)
        os.remove(self.rebuilt + '.build.json')  # (and a rebuild with no record)
        for program in (None, self.rebuilt, os.path.join(self.tmp, 'no-such-program')):
            with self.subTest(program=program):
                code, out, err = self.cli('--deals', '1', '--register-only', *(('--program', program) if program else ()))
                self.assertEqual(code, want)
        self.assertFalse(os.path.exists(self.out_root))

    def test_a_committed_pin_registers_and_the_registration_says_so_on_the_console_in_the_block_and_in_the_document(self):
        self.commit_pin()
        with mock.patch.object(sr.socket, 'gethostname', return_value='registering-box'):
            code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        block = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']
        self.assertEqual((block['pin_committed'], block['pin_committed_detail'], block['registered_on']), ('yes', None, 'registering-box'))
        self.assertIn(f'pin committed: yes ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; byte-equal to HEAD)\n', out)
        values = slow_report_values(read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertEqual((values['pin_committed'], values['pin_committed_detail'], values['registered_on']), ('yes', 'none', 'registering-box'),
                         'a committed pin has nothing to explain: "none", not "not found" and not the text None')
        self.assertEqual(values['build_record'], 'none', 'and the pinned binary has no build record')

    def test_the_test_only_variable_lets_a_hand_made_pin_register_and_the_registration_records_that_it_did(self):
        with mock.patch.dict(os.environ, {sr.ALLOW_UNCOMMITTED_PIN: '1'}), mock.patch.object(sr.socket, 'gethostname', return_value='test-box'):
            code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        detail = bypass_detail(self.repo)
        block = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']
        self.assertEqual((block['pin_committed'], block['pin_committed_detail'], block['registered_on']), ('bypassed', detail, 'test-box'))
        self.assertIn(f'pin committed: bypassed ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; {detail})\n', out)
        values = slow_report_values(read(os.path.join(d, 'PREREGISTRATION.md')))
        self.assertEqual((values['pin_committed'], values['pin_committed_detail'], values['registered_on']), ('bypassed', detail, 'test-box'))

    def test_a_rebuild_registered_with_the_committed_pin_says_the_committed_pins_digests_in_every_place_that_names_the_pin(self):
        """The wording follows the state of the pin: with the pin committed, the plan, the registered engine text, the self-check sources and the document all say 'the committed pin'
        (with a hand-made pin they say what it is instead: ProgramRoutes, BuildRecordChecks)."""
        self.commit_pin()
        code, out, err = self.cli('--deals', '1', '--dry-run', '--program', self.rebuilt)
        self.assertEqual(code, 0, str(code) + err)
        self.assertIn(f'both self-checks will be replayed on this machine against {DIGESTS_COMMITTED} before anything is registered (hours for kx3)', out)
        self.assertIn(f'pin committed: yes ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; byte-equal to HEAD)', out)
        for gone in ('NOT the committed pin', 'test use', 'pin file in use'):
            self.assertNotIn(gone, out)
        man, cfg, text = self.registered('--program', self.rebuilt)
        self.assertEqual(man['slow_report']['pin_committed'], 'yes')
        self.assertEqual(man['selfcheck_source'], {'km3': REPLAYED, 'kx3': REPLAYED})
        self.assertTrue(man['engine'].endswith(f'and equal {DIGESTS_COMMITTED}'), man['engine'])
        self.assertEqual(text.count(' (replayed by slow_report.py on the registering machine just before registration and equal to the committed pin)'), 2)
        for gone in ('NOT the committed pin', 'test use', 'pin file in use'):
            self.assertNotIn(gone, text)
            self.assertNotIn(gone, json.dumps(man))

    # ------------------------------------------------------------------------------------ what git said
    UNSAFE = ("fatal: detected dubious ownership in repository at '{repo}'\nTo add an exception for this directory, call:\n\n\tgit config --global --add safe.directory {repo}\n")

    def stub_git(self, stderr=b'', exit_code=128, stdout=b''):
        """A `git` first on the PATH that prints `stdout` and `stderr` as given and exits with `exit_code`, whatever it is asked, and logs how it was called (stub-git-calls.jsonl)."""
        bin_dir = os.path.join(self.tmp, 'stub-git-bin')
        write_bytes(os.path.join(self.tmp, 'stub-git-stderr'), stderr)
        write_bytes(os.path.join(self.tmp, 'stub-git-stdout'), stdout)
        write(os.path.join(bin_dir, 'git'), f'#!{sys.executable}\nimport json, os, sys\nd = {self.tmp!r}\n'
                                            "named = ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX']\n"
                                            "open(os.path.join(d, 'stub-git-calls.jsonl'), 'a').write(json.dumps({'argv': sys.argv[1:], 'locks': os.environ.get('GIT_OPTIONAL_LOCKS'), "
                                            "'repo_vars': [k for k in named if k in os.environ], 'marker': os.environ.get('STUB_GIT_MARKER')}) + '\\n')\n"
                                            "sys.stdout.buffer.write(open(os.path.join(d, 'stub-git-stdout'), 'rb').read())\n"
                                            "sys.stderr.buffer.write(open(os.path.join(d, 'stub-git-stderr'), 'rb').read())\n"
                                            f'sys.exit({exit_code})\n', mode=0o755)
        patcher = mock.patch.dict(os.environ, {'PATH': bin_dir + os.pathsep + os.environ.get('PATH', '')})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.assertEqual(shutil.which('git'), os.path.join(bin_dir, 'git'), 'the stub, not the real git, is what the code under test would call')

    def stub_git_calls(self):
        return jsonl(os.path.join(self.tmp, 'stub-git-calls.jsonl'))

    NO_PIN = 'HEAD has no {rel} in {repo} (not a git repository, no commit, or the file is not committed)'

    def test_a_folder_git_refuses_as_unsafe_is_said_to_be_that_and_not_only_uncommitted(self):
        """A clone made by another user (a root container) gives 'detected dubious ownership' and exit 128: the pin may well be committed. The refusal quotes git's first line and the
        command that fixes it, the same line the README quotes."""
        self.stub_git(stderr=self.UNSAFE.format(repo=self.repo).encode())
        want = (self.NO_PIN.format(rel=PIN_REL, repo=self.repo) + f"; git said: fatal: detected dubious ownership in repository at '{self.repo}' (git refuses this folder as unsafe, "
                f'which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory {self.repo})')
        st = sr.pin_commit_state(self.repo, self.pin_path)
        self.assertEqual(st, {'state': 'no', 'sha256': sha(self.pin_path), 'detail': want})
        self.assertEqual(self.stub_git_calls(), [{'argv': ['-C', self.repo, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], 'locks': '0', 'repo_vars': [], 'marker': None}],
                         'it asked for the pin at HEAD, without taking git locks')
        with self.assertRaises(SystemExit) as cm:
            sr.require_committed_pin(self.repo, self.pin_path)
        self.assertEqual(cm.exception.code, self.refused(want))
        readme_line = 'git config --global --add safe.directory <folder>'
        self.assertIn(f'`{readme_line}`', cloud_section(), 'the README quotes the command the refusal gives')
        self.assertIn(readme_line.replace('<folder>', self.repo), want)
        self.assertIn('"detected dubious ownership"', cloud_section())
        with mock.patch.dict(os.environ, {sr.ALLOW_UNCOMMITTED_PIN: '1'}):
            self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path), {'state': 'bypassed', 'sha256': sha(self.pin_path),
                                                                              'detail': f'{want}; allowed by {sr.ALLOW_UNCOMMITTED_PIN} (test use)'}, 'the reason is kept when the test variable lets it through')

    def test_a_registration_in_a_folder_git_refuses_is_refused_with_git_s_own_words_before_anything_is_written(self):
        self.stub_git(stderr=self.UNSAFE.format(repo=self.repo).encode())
        code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertIsInstance(code, str, out + err)
        self.assertTrue(code.startswith(f"{BuildRecordChecks.TAG}REFUSED: the pin is not the committed one: HEAD has no {PIN_REL} in {self.repo} (not a git repository, no commit, or the file is "
                                        f"not committed); git said: fatal: detected dubious ownership in repository at '{self.repo}' (git refuses this folder as unsafe"), code)
        self.assertIn(f'if you trust it: git config --global --add safe.directory {self.repo}). A slow report trusts the pin', code)
        self.assertEqual(out, '')
        self.assertFalse(os.path.exists(self.out_root))

    def test_the_command_that_fixes_an_unsafe_folder_is_quoted_for_a_shell_when_the_folder_has_a_space(self):
        """The advice is pasted into a shell: a folder with a space in its name must be one word there (it was once built with the folder as it is, and git refused the command)."""
        spaced = os.path.join(self.tmp, 'my checkout')
        os.makedirs(spaced)
        self.stub_git(stderr=self.UNSAFE.format(repo=spaced).encode())
        detail = sr.pin_commit_state(spaced, self.pin_path)['detail']
        self.assertIn(f"git config --global --add safe.directory '{spaced}')", detail, 'quoted, and the closing bracket of the sentence is outside the quotes')
        self.assertTrue(detail.endswith(f"if you trust it: git config --global --add safe.directory '{spaced}')"), detail)
        advice = detail.rsplit('if you trust it: ', 1)[1][:-1]
        self.assertEqual(shlex.split(advice), ['git', 'config', '--global', '--add', 'safe.directory', spaced], 'a shell reads the advice as git config --global --add safe.directory <the folder>')

    def test_the_command_that_fixes_an_unsafe_folder_quotes_what_a_shell_would_split_or_expand_and_leaves_a_plain_path_alone(self):
        for how, name in (('a space', 'my checkout'), ('an apostrophe', "it's a checkout"), ('a dollar sign', 'costs $HOME'), ('a semicolon and brackets', 'a; (b)'),
                          ('a backslash', 'back\\slash'), ('a plain name', 'plain-name_1.2')):
            with self.subTest(folder=how):
                folder = os.path.join(self.tmp, name)
                os.makedirs(folder)
                self.stub_git(stderr=self.UNSAFE.format(repo=folder).encode())
                detail = sr.pin_commit_state(folder, self.pin_path)['detail']
                advice = detail.rsplit('if you trust it: ', 1)[1][:-1]
                self.assertEqual(shlex.split(advice), ['git', 'config', '--global', '--add', 'safe.directory', folder])
                self.assertEqual(advice == f'git config --global --add safe.directory {folder}', how == 'a plain name', 'only a path with nothing to quote is left bare')
                self.assertTrue(detail.startswith(self.NO_PIN.format(rel=PIN_REL, repo=folder)), 'the first part names the folder as it is, not quoted')

    # ------------------------------------------------------------------------------------ git is asked about the repository it was told about
    NAMED_BY_GIT = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX')

    def test_the_variables_that_make_git_read_another_repository_are_not_in_the_environment_of_the_git_the_pin_check_runs(self):
        """A git hook or `git rebase --exec` exports GIT_DIR and its relatives: with them set, `git -C repo ...` reads THAT repository whatever -C says. The check runs git
        without them (and with the optional locks off), and leaves the rest of the environment as it is."""
        self.assertEqual(sr.GIT_REPO_VARS, self.NAMED_BY_GIT, 'the variables the code removes')
        self.stub_git(stderr=b'fatal: bad object HEAD\n')
        exported = {name: os.path.join(self.tmp, 'elsewhere', name) for name in self.NAMED_BY_GIT}
        with mock.patch.dict(os.environ, dict(exported, STUB_GIT_MARKER='kept', GIT_OPTIONAL_LOCKS='1')):
            before = dict(os.environ)
            sr.pin_commit_state(self.repo, self.pin_path)
            self.assertEqual(dict(os.environ), before, 'the check does not change the environment of this process')
        self.assertEqual(self.stub_git_calls(), [{'argv': ['-C', self.repo, 'cat-file', 'blob', f'HEAD:./{PIN_REL}'], 'locks': '0', 'repo_vars': [], 'marker': 'kept'}],
                         'none of the eight reached git, the locks are off whatever the caller had, and the other variables are as they were')
        for name in self.NAMED_BY_GIT:
            with self.subTest(only=name):
                os.remove(os.path.join(self.tmp, 'stub-git-calls.jsonl'))
                with mock.patch.dict(os.environ, {name: exported[name]}):
                    sr.pin_commit_state(self.repo, self.pin_path)
                self.assertEqual([c['repo_vars'] for c in self.stub_git_calls()], [[]], f'{name} did not reach git')

    def test_the_variables_that_make_git_read_another_repository_are_not_in_the_environment_of_any_of_the_git_calls_that_judge_the_deck_file(self):
        self.stub_git(stderr=b'', exit_code=0, stdout=b'true\n')
        with mock.patch.dict(os.environ, dict({name: os.path.join(self.tmp, 'elsewhere', name) for name in self.NAMED_BY_GIT}, GIT_OPTIONAL_LOCKS='1', STUB_GIT_MARKER='kept')):
            sr.deck_state(self.repo, 'decks/events/my-list.txt')
        calls = self.stub_git_calls()
        self.assertGreaterEqual(len(calls), 3, 'it asked git several things about the deck file')
        self.assertEqual([c['argv'][:3] for c in calls][:2], [['-C', self.repo, 'rev-parse'], ['-C', self.repo, 'ls-files']])
        for call in calls:
            with self.subTest(git=' '.join(call['argv'][2:4])):
                self.assertEqual((call['repo_vars'], call['locks'], call['marker']), ([], '0', 'kept'))

    def other_repository(self, name='other'):
        """A second repository with a commit and with a pin of other bytes committed (the one a leaked GIT_DIR would point to)."""
        other = os.path.join(self.tmp, name)
        os.makedirs(other)
        subprocess.run(['git', '-C', other, 'init', '-q'], check=True, capture_output=True)
        self.commit_pin(data=b'{"another": "pin"}\n', repo=other)
        return other

    def test_a_git_dir_exported_to_another_repository_does_not_change_which_repository_judges_the_pin(self):
        """The repository given is judged by its own HEAD: the committed pin is 'yes' and an uncommitted one 'no' with GIT_DIR (or its relatives) set to a repository that holds
        other bytes at that path, and the detail names the folder that was given."""
        self.commit_pin()
        other = self.other_repository()
        pointing = {'GIT_DIR': os.path.join(other, '.git'), 'GIT_COMMON_DIR': os.path.join(other, '.git'), 'GIT_OBJECT_DIRECTORY': os.path.join(self.tmp, 'no-objects-here'),
                    'GIT_NAMESPACE': 'someone-elses', 'GIT_WORK_TREE': other, 'GIT_PREFIX': 'rl/strength/', 'GIT_INDEX_FILE': os.path.join(other, '.git', 'index')}
        os.makedirs(pointing['GIT_OBJECT_DIRECTORY'])
        for name in self.NAMED_BY_GIT:
            if name not in pointing:
                pointing[name] = os.path.join(other, '.git', 'objects')
        edited = os.path.join(self.tmp, 'edited.json')
        write_bytes(edited, read_bytes(self.pin_path) + b'\n')
        for name, value in pointing.items():
            with self.subTest(exported=name), mock.patch.dict(os.environ, {name: value}):
                self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path), {'state': 'yes', 'sha256': sha(self.pin_path), 'detail': ''})
                self.assertEqual(sr.pin_commit_state(self.repo, edited)['state'], 'no')
                self.assertIn('differs from the', sr.pin_commit_state(self.repo, edited)['detail'], 'judged against the pin committed in the folder given')
                self.assertEqual(sr.require_committed_pin(self.repo, self.pin_path)['state'], 'yes')
        with mock.patch.dict(os.environ, pointing):
            self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path)['state'], 'yes', 'all of them at once')
        outside = os.path.join(self.tmp, 'a-plain-folder')
        os.makedirs(outside)
        with mock.patch.dict(os.environ, {'GIT_DIR': os.path.join(other, '.git')}):
            st = sr.pin_commit_state(outside, self.pin_path)
        self.assertEqual(st['state'], 'no', "a folder that is not a repository is not rescued by another one's pin: the other repository does not hold this pin either")
        self.assertTrue(st['detail'].startswith(f'HEAD has no {PIN_REL} in {outside} '), st['detail'])

    def test_a_registration_made_with_a_git_dir_exported_to_another_repository_still_reads_the_pin_of_the_checkout_it_runs_from(self):
        self.commit_pin()
        other = self.other_repository()
        with mock.patch.dict(os.environ, {'GIT_DIR': os.path.join(other, '.git'), 'GIT_WORK_TREE': other}), mock.patch.object(sr.socket, 'gethostname', return_value='registering-box'):
            code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        block = json.loads(read(os.path.join(self.rundir(), 'manifest.json')))['slow_report']
        self.assertEqual((block['pin_committed'], block['pin_committed_detail']), ('yes', None))
        self.assertIn(f'pin committed: yes ({PIN_REL} sha256 {sha(self.pin_path)[:12]}; byte-equal to HEAD)\n', out)

    def test_the_repository_commit_a_registration_records_is_the_checkouts_even_when_a_git_dir_is_exported_to_another_repository(self):
        """strength_prereg.py reads the commit it records ("repository commit" in manifest.json, PREREGISTRATION.md and the page) with git run without GIT_DIR and its relatives
        (GIT_REPO_VARS), like the pin check and the deck check: with GIT_DIR exported (a git hook, `rebase --exec`) the commit recorded is this checkout's, not the OTHER repository's."""
        self.commit_pin()
        head = git(self.repo, 'rev-parse', 'HEAD').stdout.strip()
        other = self.other_repository()
        self.assertNotEqual(git(other, 'rev-parse', 'HEAD').stdout.strip(), head)
        with mock.patch.dict(os.environ, {'GIT_DIR': os.path.join(other, '.git')}):
            code, out, err = self.cli('--deals', '1', '--register-only')
        self.assertEqual(code, 0, str(code) + err)
        d = self.rundir()
        self.assertEqual(json.loads(read(os.path.join(d, 'manifest.json')))['repo_commit'], head)
        self.assertIn(f'repository commit: `{head}`', read(os.path.join(d, 'PREREGISTRATION.md')))

    def test_only_the_first_line_git_prints_is_quoted_cut_at_200_characters_and_what_git_does_not_say_is_not_invented(self):
        folder = self.repo
        base = self.NO_PIN.format(rel=PIN_REL, repo=folder)
        unsafe_tail = f' (git refuses this folder as unsafe, which is not the same as the pin being uncommitted; if you trust it: git config --global --add safe.directory {folder})'
        for how, stderr, said, unsafe in (
                ('one line, not about safety', b'fatal: bad object HEAD\n', 'fatal: bad object HEAD', False),
                ('several lines: the first only', b'error: first\nerror: second\nerror: third\n', 'error: first', False),
                ('blank lines and spaces before the first line', b'\n\n  fatal: late\nmore\n', 'fatal: late', False),
                ('a long first line is cut at 200', b'x' * 300 + b'\nsecond\n', 'x' * 200, False),
                ('safe.directory on the first line', b'fatal: not allowed by safe.directory setting\n', 'fatal: not allowed by safe.directory setting', True),
                ('safe.directory only on a later line', b'fatal: first\nadd it to safe.directory please\n', 'fatal: first', True),
                ('not UTF-8: replaced, never a crash', b'fatal: caf\xe9 \xff\n', 'fatal: caf\ufffd \ufffd', False),
                ('Windows line ends', b'fatal: one\r\nfatal: two\r\n', 'fatal: one', False)):
            with self.subTest(stderr=how):
                self.stub_git(stderr=stderr)
                got = sr.pin_commit_state(folder, self.pin_path)
                self.assertEqual(got['state'], 'no')
                self.assertEqual(got['detail'], f'{base}; git said: {said}' + (unsafe_tail if unsafe else ''))
        for how, stderr in (('nothing', b''), ('only white space', b' \n\t\n  \n')):
            with self.subTest(stderr=how):
                self.stub_git(stderr=stderr)
                self.assertEqual(sr.pin_commit_state(folder, self.pin_path)['detail'], base, 'git said nothing: the old words, no "git said:"')

    def test_what_git_prints_on_success_or_for_a_different_pin_is_not_added_to_the_detail(self):
        """Only a failing git has something to say: a successful read with noise on stderr (a warning) is a committed pin, and a pin that differs says how it differs."""
        original = read_bytes(self.pin_path)
        self.stub_git(stderr=b'warning: something harmless\n', exit_code=0, stdout=original)
        self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path), {'state': 'yes', 'sha256': sha(self.pin_path), 'detail': ''})
        self.stub_git(stderr=b'warning: something harmless\n', exit_code=0, stdout=original + b'\n')
        got = sr.pin_commit_state(self.repo, self.pin_path)
        self.assertEqual(got['state'], 'no')
        self.assertTrue(got['detail'].startswith('the pin file (sha256 '), got['detail'])
        self.assertNotIn('git said', got['detail'])
        self.assertNotIn('harmless', got['detail'])

    def test_git_that_is_missing_is_still_said_to_be_missing_and_not_as_a_failure_of_git(self):
        empty_bin = os.path.join(self.tmp, 'empty-bin')
        os.makedirs(empty_bin)
        with mock.patch.dict(os.environ, {'PATH': empty_bin}):
            self.assertEqual(sr.pin_commit_state(self.repo, self.pin_path), {'state': 'no', 'sha256': sha(self.pin_path), 'detail': 'git is not available, so the committed pin cannot be read'})


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

    def test_a_git_dir_exported_to_another_repository_does_not_change_what_git_says_about_the_deck_file(self):
        """A git hook (or `git rebase --exec`) exports GIT_DIR and its relatives; the deck file is judged by the repository the run is made from, not by that one."""
        repo = self.repo_with_a_commit()
        write(os.path.join(repo, 'decks', 'new.txt'), 'x\n')
        git(repo, 'add', 'decks/new.txt')
        git(repo, 'commit', '-q', '-m', 'deck')
        write(os.path.join(repo, 'decks', 'edited.txt'), 'x\n')
        git(repo, 'add', 'decks/edited.txt')
        git(repo, 'commit', '-q', '-m', 'another deck')
        write(os.path.join(repo, 'decks', 'edited.txt'), 'y\n')
        write(os.path.join(repo, 'decks', 'untracked.txt'), 'z\n')
        other = os.path.join(self.tmp, 'other')
        write(os.path.join(other, 'unrelated.txt'), 'x\n')
        subprocess.run(['git', '-C', other, 'init', '-q'], check=True)
        git(other, 'add', 'unrelated.txt')
        git(other, 'commit', '-q', '-m', 'elsewhere')
        plain = os.path.join(self.tmp, 'plain')
        write(os.path.join(plain, 'a.txt'), 'x\n')
        pointing = {'GIT_DIR': os.path.join(other, '.git'), 'GIT_WORK_TREE': other, 'GIT_INDEX_FILE': os.path.join(other, '.git', 'index'), 'GIT_COMMON_DIR': os.path.join(other, '.git'),
                    'GIT_OBJECT_DIRECTORY': os.path.join(other, '.git', 'objects'), 'GIT_PREFIX': ''}
        for name, value in list(pointing.items()) + [('all of them', None)]:
            with self.subTest(exported=name), mock.patch.dict(os.environ, pointing if value is None else {name: value}):
                self.assertEqual(sr.deck_state(repo, 'decks/new.txt'), 'committed')
                self.assertEqual(sr.deck_state(repo, 'decks/edited.txt'), 'not committed')
                self.assertEqual(sr.deck_state(repo, 'decks/untracked.txt'), 'not committed')
                self.assertEqual(sr.deck_state(plain, 'a.txt'), 'unknown (not a git repository)', "a folder that is not a repository is not taken to be the exported one's work tree")

    def test_the_manifest_and_the_plan_say_what_git_says_about_the_deck_file(self):
        subprocess.run(['git', '-C', self.repo, 'init', '-q'], check=True)
        plan = self.cli('--deals', '1', '--dry-run')[1]
        self.assertEqual(plan.count(f'plan: my-list ({self.deck_rel}, not committed), 1 deal x 2 seats'), 1, 'a deck git has not seen (the pin line has its own "committed" word, about the pin)')
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
        build = read(os.path.join(HERE, 'build.sh'))
        self.assertIn('HARNESS_SHA=$(LC_ALL=C; cat "$HERE"/src/*.rs "$HERE/Cargo.toml" | sha256sum | cut -d\' \' -f1)', build)
        self.assertIn('echo "harness source sha256: $HARNESS_SHA"', build, 'printed')
        self.assertIn('BR_HARNESS="$HARNESS_SHA"', build, 'and the very same value goes into the build record')

    def test_the_pin_carries_what_a_rebuild_is_checked_against_and_a_record_made_from_it_passes_the_check_and_one_entry_off_does_not(self):
        pin = self.pin()
        self.assertRegex(pin['engine_ref'], r'^[0-9a-f]{40}$')
        self.assertRegex(pin['engine_tree'], r'^[0-9a-f]{40}$')
        self.assertRegex(pin['harness_source_sha256'], r'^[0-9a-f]{64}$')
        with tempfile.TemporaryDirectory() as t:
            program = os.path.join(t, 'strength')
            write(program, 'a program that is not the pinned binary\n')
            rec = dict(schema=1, program_sha256=sha(program), engine_ref=pin['engine_ref'], engine_tree_archived=pin['engine_tree'], harness_source_sha256=pin['harness_source_sha256'])
            write(program + '.build.json', json.dumps(rec))
            got = sr.read_build_record(program, pin)
            self.assertEqual({k: got[k] for k in rec}, rec)
            for key in ('program_sha256', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256'):
                with self.subTest(off=key):
                    write(program + '.build.json', json.dumps(dict(rec, **{key: ('0' if rec[key][0] != '0' else '1') + rec[key][1:]})))
                    with self.assertRaises(SystemExit) as cm:
                        sr.read_build_record(program, pin)
                    self.assertIn('REFUSED: ', str(cm.exception.code))
                    self.assertTrue(str(cm.exception.code).endswith(' Nothing was written.'), cm.exception.code)

    def test_the_cloud_route_smoke_run_recorded_a_rebuild_with_a_build_record_of_the_pinned_source(self):
        """Run 3 of the committed smoke folder is the cloud route as it was run for real with a rebuilt copy of the pinned binary: it took the rebuilt route, its build record has
        the pin's engine tree and harness hash, it used the test-only variable for the pin (the hand-made km3 pin of the smoke is not the committed one), and the program it ran is
        the one whose sha256 games.sha256 records. When the run was resumed with another rebuild, its program_changed event is held to the same. Skipped while the folder is the
        one made before the build record existed."""
        pin = self.pin()
        smoke = os.path.join(ROOT, 'rl', 'results', 'slow_report_smoke_2026-10-07')
        run3 = next((d for d in (sorted(os.listdir(smoke)) if os.path.isdir(smoke) else []) if d.startswith('run3_cloud_route') and os.path.isfile(os.path.join(smoke, d, 'manifest.json'))), None)
        if run3 is None:
            self.skipTest(f'{smoke} has no run3_cloud_route* run: the smoke folder is not this checkout\'s')
        man = json.loads(read(os.path.join(smoke, run3, 'manifest.json')))
        block = man['slow_report']
        if not block.get('build_record'):
            self.skipTest('the smoke folder is still the one made before the build record existed (run 3 has no build_record): run smoke.sh again to refresh it')
        rec = block['build_record']
        recorded = read(os.path.join(smoke, 'games.sha256'))
        self.assertEqual(block['program_route'], 'rebuilt')
        self.assertEqual(rec['engine_tree_archived'], pin['engine_tree'])
        self.assertEqual(rec['harness_source_sha256'], pin['harness_source_sha256'])
        self.assertEqual(rec['program_sha256'], man['program_sha256'], 'the record is of the program the run was registered with')
        self.assertNotEqual(man['program_sha256'], pin['program_sha256'], 'a rebuild, not the pinned binary')
        self.assertEqual(block['pin_committed'], 'bypassed', 'the smoke used the test-only variable for its hand-made pin')
        self.assertIn(sr.ALLOW_UNCOMMITTED_PIN, block['pin_committed_detail'])
        self.assertTrue(block.get('registered_on'))
        self.assertIn(rec['program_sha256'], recorded, 'games.sha256 records the sha256 of the rebuilt copy run 3 used')
        for event in (e for e in jsonl(os.path.join(smoke, run3, 'slow_report_log.jsonl')) if e['event'] == 'program_changed'):
            self.assertEqual(event['old_sha256'], man['program_sha256'], 'the program the run was registered with')
            self.assertIn(event['new_sha256'], recorded, 'games.sha256 records the sha256 of the second rebuild too')
            self.assertEqual(event['build_record']['program_sha256'], event['new_sha256'])
            self.assertEqual((event['build_record']['engine_tree_archived'], event['build_record']['harness_source_sha256']), (pin['engine_tree'], pin['harness_source_sha256']))
            self.assertEqual(event['pin_committed'], 'bypassed')

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
        self.assertEqual(sorted(found)[:2], ['run1_complete_under_nohup', 'run2_sigterm_and_resume'])
        self.assertEqual(len(found), 3, sorted(found))
        self.assertEqual(sorted(found)[2], 'run3_cloud_route_real_rebuild_and_restart', f'the third run is the cloud route\'s, in the folder of its real rebuild and restart (it was first called run3_cloud_route_rebuilt_registration): {sorted(found)}')
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


# the assignments build.sh writes, in this order, into the rebuild command of its record (README step 1 gives the first four)
REBUILD_ENV = ('HOME', 'CARGO_HOME', 'STRENGTH_BUILD_DIR', 'STRENGTH_TARGET_DIR', 'STRENGTH_JOBS', 'STRENGTH_REPO')
RECORD_FIELDS = ('schema', 'program', 'program_sha256', 'engine_arg', 'engine', 'engine_ref', 'engine_tree_archived', 'harness_source_sha256', 'rustc', 'cargo', 'machine', 'libc', 'host',
                 'home', 'cargo_home', 'build_dir', 'target_dir', 'jobs', 'build_env_unset', 'cargo_config_files', 'built_at', 'rebuild_command')
LIST_FIELDS = ('build_env_unset', 'cargo_config_files')  # the two that are lists (of names, and of {path, sha256}); every other field but schema, engine_ref and cargo_home is text


def readme_build_command():
    """(env, ref, out) of the build.sh command that step 1 of the cloud section gives, `env NAME=value ... bash rl/strength/build.sh REF OUT`: the assignments as a dict, the ref and
    the output path, all as written ($HOME unexpanded)."""
    m = re.search(r'`(env [^`]*\bbash rl/strength/build\.sh [^`]*)`', cloud_section())
    assert m, 'step 1 of the cloud section gives an `env NAME=value ... bash rl/strength/build.sh REF OUT` command'
    words = shlex.split(m.group(1))
    at = words.index('bash')
    assert words[0] == 'env' and words[at + 1] == 'rl/strength/build.sh' and len(words) == at + 4, words
    return dict(w.split('=', 1) for w in words[1:at]), words[at + 2], words[at + 3]


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


class BuildWorld(unittest.TestCase):
    """rl/strength/build.sh, run for real on a COPY of itself in a temporary folder: its own src/*.rs, Cargo.toml and a pin beside it, an engine folder (or, for a git ref, the
    temporary folder itself as the repository, which is where build.sh looks for refs: two folders above the script), a stub `cargo` and a stub `rustc` first on the PATH
    (the cargo only writes a file where the real one would leave the program, and answers -V), and HOME, STRENGTH_BUILD_DIR and every output path inside the temporary folder. Git
    runs with no global or system configuration, so the machine's own settings cannot change what the tests expect. Nothing is built and nothing outside the folder is touched:
    the 'frozen binary' here is a file of this test's own, at a path of its own. Only the format of the committed pin's program line is read from the real repository."""

    FROZEN = b'the frozen binary: not to be overwritten\n'
    STUB_PROGRAM = b'the stub program\n'
    RUSTC = 'rustc 1.99.0 (stub 2026-01-01)\nbinary: rustc\nhost: x86_64-unknown-linux-gnu'
    CARGO = 'cargo 1.99.0 (stub 2026-01-01)'

    def setUp(self):
        if not all(shutil.which(x) for x in ('bash', 'readlink', 'sha256sum', 'nice', 'find', 'touch', 'cat', 'cut', 'git', 'tar', 'python3', 'uname')):
            self.skipTest('needs a Unix userland (bash, GNU readlink and sha256sum, git, tar, python3)')
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
        write(os.path.join(self.stub, 'cargo'), '#!/bin/bash\nif [ "$1" = "-V" ]; then echo "$STUB_CARGO_V"; exit 0; fi\necho "$* | target=$CARGO_TARGET_DIR" >> "$STUB_LOG"\n'
                                                'if [ -n "${STUB_CARGO_FAILS:-}" ]; then echo "error: could not compile the stub"; exit 101; fi\nmkdir -p "$CARGO_TARGET_DIR/release"\n'
                                                'printf \'%s\\n\' "${STUB_PROGRAM_TEXT:-the stub program}" > "$CARGO_TARGET_DIR/release/strength"\n', mode=0o755)
        write(os.path.join(self.stub, 'rustc'), '#!/bin/bash\nif [ "$1" = "-vV" ]; then echo "$STUB_RUSTC_VV"; fi\n', mode=0o755)
        self.frozen = os.path.join(self.tmp, 'frozen', 'strength')
        write_bytes(self.frozen, self.FROZEN)
        self.lay_out_pin(self.frozen)

    def lay_out_pin(self, program):
        """The pin beside build.sh, laid out like the committed one (one entry to a line): it names `program` as the frozen binary."""
        write(os.path.join(self.here, 'slow_report_pin.json'), json.dumps({'_note': 'a test pin', 'program': program, 'program_sha256': '0' * 64}, indent=1) + '\n')

    def env(self, **changes):
        """A clean environment (no locale, no STRENGTH_* or STUB_* or git variable, nothing of cargo's or rustc's: no CARGO_* and no RUST*, which the build would remove and list), the
        stubs first on the PATH, HOME and the build folder inside the temporary folder, git without any configuration of the machine; `changes` add to it (a value of None removes
        the variable)."""
        env = {k: v for k, v in os.environ.items() if k not in ('LANG', 'LANGUAGE', 'LOCPATH', 'GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE')
               and not k.startswith(('LC_', 'STRENGTH_', 'STUB_', 'GIT_CONFIG', 'CARGO_', 'RUST'))}
        env.update(PATH=self.stub + os.pathsep + env.get('PATH', ''), HOME=os.path.join(self.tmp, 'home'), STRENGTH_BUILD_DIR=os.path.join(self.tmp, 'build'), STUB_LOG=self.log,
                   STUB_CARGO_V=self.CARGO, STUB_RUSTC_VV=self.RUSTC, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        env.update(changes)
        return {k: v for k, v in env.items() if v is not None}

    def run_build(self, out, ref=None, cwd=None, **env_changes):
        """build.sh REF OUT (REF: the engine folder unless given) in the clean environment; env_changes add to it."""
        env = self.env(**env_changes)
        for tool in ('cargo', 'rustc'):
            self.assertEqual(shutil.which(tool, path=env['PATH']), os.path.join(self.stub, tool), f'the stub, never a real {tool}, is what build.sh would call')
        self.assertTrue(os.path.realpath(os.path.join(cwd or self.tmp, out)).startswith(self.tmp + os.sep), 'every output path of these tests is inside the temporary folder')
        return subprocess.run(['bash', os.path.join(self.here, 'build.sh'), ref or self.engine, out], capture_output=True, text=True, env=env, cwd=cwd or self.tmp)

    def refusal(self, program):
        return f"build.sh: refusing to overwrite the slow report's pinned program {program} (slow_report_pin.json); build to another path\n"

    def git(self, *args):
        return subprocess.run(['git', '-C', self.tmp, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false', *args], check=True, capture_output=True, text=True,
                              env=self.env())

    def commit_engine(self, message='the engine'):
        """Commit engine/ (every file, ignored ones too) in the temporary folder, the repository build.sh reads refs from; returns (commit, tree of engine/)."""
        if not os.path.isdir(os.path.join(self.tmp, '.git')):
            self.git('init', '-q')
            self.git('symbolic-ref', 'HEAD', 'refs/heads/main')  # (the branch is named here, not by the machine's init.defaultBranch; `init -b` needs a newer git)
        self.git('add', '-A', '-f', 'engine')
        self.git('commit', '-q', '--allow-empty', '-m', message)
        return self.git('rev-parse', 'HEAD').stdout.strip(), self.git('rev-parse', 'HEAD:engine').stdout.strip()

    def write_stub(self, name, body):
        """Replace the stub `name` (cargo, rustc, tar, ...) in the stub folder by this bash script."""
        write(os.path.join(self.stub, name), '#!/bin/bash\n' + body, mode=0o755)

    # the default stub cargo, in pieces, for the stubs that do something more: answer -V, note the call, and (BUILDS) leave the program where the real cargo would
    CARGO_V = 'if [ "$1" = "-V" ]; then echo "$STUB_CARGO_V"; exit 0; fi\n'
    CARGO_NOTES = 'echo "$* | target=$CARGO_TARGET_DIR" >> "$STUB_LOG"\n'
    CARGO_BUILDS = 'mkdir -p "$CARGO_TARGET_DIR/release"\nprintf \'%s\\n\' "${STUB_PROGRAM_TEXT:-the stub program}" > "$CARGO_TARGET_DIR/release/strength"\n'


class BuildScript(BuildWorld):
    """The guard against building over the frozen binary, and what a build prints."""

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

    def test_any_other_output_path_builds_and_prints_the_six_lines_in_order(self):
        """The four lines of before (the engine, the program, its sha256, the harness source hash, in that order) and the two the build record added: the engine tree as archived
        after the engine line, and the record's own path last."""
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        os.makedirs(os.path.dirname(out))
        commit, tree = self.commit_engine()
        r = self.run_build(out)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [f'engine: dir:{self.engine}', f'engine tree as archived: {tree}', f'program: {out}', f'program sha256: {hashlib.sha256(self.STUB_PROGRAM).hexdigest()}',
                                                 f'harness source sha256: {sr.harness_source_sha256(self.tmp)}', f'build record: {out}.build.json'])
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        self.assertEqual(read_bytes(self.frozen), self.FROZEN)
        self.assertEqual(read(self.log).splitlines(), [f'build --release --offline | target={os.path.join(self.tmp, "build", "target")}'], 'cargo was asked for an offline release build once')
        self.assertEqual(sorted(os.listdir(os.path.dirname(out))), ['strength', 'strength.build.json'], 'the program and its record, nothing else')

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
                self.assertTrue(os.path.isfile(fresh + '.build.json'), 'and the record beside it')
                self.assertEqual(read_bytes(self.frozen), self.FROZEN)

    def test_the_pinned_path_is_refused_where_nothing_is_there_too(self):
        """A pin read on a machine that does not have the binary: building to that very path is still building over the pinned path."""
        absent = os.path.join(self.tmp, 'laptop-home', 'kx', 'strength')
        self.lay_out_pin(absent)
        self.assert_nothing_was_done(self.run_build(absent), absent)
        self.assertFalse(os.path.exists(os.path.dirname(absent)), 'and it made no folder')

    def test_step_1_of_the_readme_as_written_is_accepted_on_a_machine_without_the_laptops_folder_and_the_pinned_path_is_not(self):
        env, ref, written = readme_build_command()
        home = os.path.join(self.tmp, 'home')
        here = lambda v: v.replace('$HOME', home)
        self.assertTrue(written.startswith('$HOME/'), written)
        commit, tree = self.commit_engine()
        self.lay_out_pin(os.path.join(self.tmp, 'laptop-home', 'kx', 'strength'))  # (the committed pin's /home/<user>/kx/strength, on a machine that has no such folder)
        out = here(written)
        r = self.run_build(out, ref=commit, **{k: here(v) for k, v in env.items()})
        self.assertEqual((r.returncode, r.stderr), (0, ''), 'step 1 of the README, as written, is not refused by the guard against building over the frozen binary')
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        rec = json.loads(read(out + '.build.json'))
        assignments = dict(w.split('=', 1) for w in shlex.split(rec['rebuild_command'])[1:shlex.split(rec['rebuild_command']).index('bash')])
        for name, value in env.items():
            self.assertEqual(assignments[name], here(value), f'{name} in the README is what the record would repeat')
        self.assertEqual(rec['engine_tree_archived'], tree)

    def test_the_guard_reads_the_committed_pins_program_line_the_way_json_does(self):
        """build.sh picks the pin's program path out with python3's json module: on the committed pin's layout that must be exactly the path the wrapper reads, and the whole
        script, given the committed pin's text with the program entry pointed at this test's frozen binary, must refuse that path and accept another."""
        m = re.search(r"PIN_PROGRAM=\$\(python3 -c '([^']*)' \"\$HERE/slow_report_pin\.json\" 2>/dev/null\)", read(os.path.join(HERE, 'build.sh')))
        self.assertTrue(m, 'build.sh reads the pin\'s program path with python3 (its own complaint hidden: the guard says why it refuses)')
        committed = os.path.join(HERE, 'slow_report_pin.json')
        r = subprocess.run(['python3', '-c', m.group(1), committed], capture_output=True, text=True)
        self.assertEqual(r.stdout.splitlines(), [json.loads(read(committed))['program']], 'one line, the pinned path (not the program_sha256 line, not the note)')
        text, real = read(committed), json.loads(read(committed))['program']
        self.assertEqual(text.count(json.dumps(real)), 1, 'the pinned path is written once')
        write(os.path.join(self.here, 'slow_report_pin.json'), text.replace(json.dumps(real), json.dumps(self.frozen)))
        self.assert_nothing_was_done(self.run_build(self.frozen), self.frozen)
        other = os.path.join(self.tmp, 'elsewhere', 'strength')
        self.assertEqual(self.run_build(other).returncode, 0, 'and the committed layout does not make it refuse everything')

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
                out = os.path.join(self.tmp, 'out-' + how, 'strength')
                r = self.run_build(out, **env, **extra)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual([l for l in r.stdout.splitlines() if l.startswith('harness source sha256: ')], [f'harness source sha256: {wrapper}'])
                self.assertEqual(json.loads(read(out + '.build.json'))['harness_source_sha256'], wrapper, 'the record carries the same hash')

    # ------------------------------------------------------------------------------------------------------ the output path and the engine folder
    def test_a_folder_as_the_output_is_refused_with_exit_2_before_anything_is_done(self):
        """OUT_BINARY is the program's FILE path. Given a folder, cp would put the program inside it under cargo's name and the record would sit beside the folder, named for it."""
        folder = os.path.join(self.tmp, 'a-folder')
        os.makedirs(folder)
        link = os.path.join(self.tmp, 'link-to-a-folder')
        os.symlink(folder, link)
        for how, out in (('a folder', folder), ('a folder given relative to the folder it runs in', 'a-folder'), ('a link to a folder', link), ('a folder with a slash after it', folder + '/'),
                         ("the pinned binary's own folder", os.path.dirname(self.frozen))):
            with self.subTest(output=how):
                r = self.run_build(out)
                self.assertEqual((r.returncode, r.stdout), (2, ''))
                self.assertEqual(r.stderr, f'build.sh: OUT_BINARY {out} is a directory; give the path of the program file to write (for example {out}/strength)\n')
                self.assertEqual(os.listdir(folder), [], 'nothing was put into the folder')
                self.assertFalse(os.path.exists(self.log), 'cargo was not called')
                self.assertFalse(os.path.exists(os.path.join(self.tmp, 'build')), 'and the build folder was not touched')
                self.assertEqual(os.listdir(os.path.dirname(self.frozen)), ['strength'])
        self.assertEqual(sorted(n for n in os.listdir(self.tmp) if n.startswith(('a-folder', 'link-to'))), ['a-folder', 'link-to-a-folder'], 'and no record was written beside any of them')
        again = self.run_build(os.path.join(folder, 'strength'))
        self.assertEqual(again.returncode, 0, 'a file in that folder is a fine output')
        self.assertEqual(sorted(os.listdir(folder)), ['strength', 'strength.build.json'])

    def test_a_relative_output_and_a_relative_engine_folder_are_made_absolute_so_the_program_and_the_record_land_where_they_were_asked_for(self):
        """The script changes folder to build; a relative OUT would then mean another place, and the record and the rebuild command would carry a path that means nothing elsewhere."""
        work = os.path.join(self.tmp, 'work')
        for how, out, made in (('a path', os.path.join('rel', 'out', 'strength'), ['rel']), ('a path with a dot dot in a folder that is not there', os.path.join('nope', '..', 'rel2', 'strength'), ['rel2']),
                               ('just a file name', 'strength', ['strength', 'strength.build.json'])):
            with self.subTest(output=how):
                shutil.rmtree(work, ignore_errors=True)
                os.makedirs(work)
                r = self.run_build(out, ref=os.path.join('..', 'engine'), cwd=work)
                absolute = os.path.normpath(os.path.join(work, out))
                self.assertEqual(r.returncode, 0, r.stderr)
                lines = r.stdout.splitlines()
                self.assertEqual((lines[0], lines[2], lines[5]), (f'engine: dir:{self.engine}', f'program: {absolute}', f'build record: {absolute}.build.json'), 'what it prints is absolute too')
                self.assertEqual(read_bytes(absolute), self.STUB_PROGRAM)
                rec = json.loads(read(absolute + '.build.json'))
                self.assertEqual((rec['program'], rec['engine_arg'], rec['engine']), (absolute, self.engine, f'dir:{self.engine}'))
                words = shlex.split(rec['rebuild_command'])
                self.assertEqual(words[-2:], [self.engine, absolute], 'the command repeats the build from anywhere: the engine folder and the output, both absolute')
                self.assertEqual(sorted(os.listdir(work)), made, 'under the folder it ran in, only what was asked for')
                os.remove(absolute)
                os.remove(absolute + '.build.json')
                again = subprocess.run(words, capture_output=True, text=True, env=self.env(STRENGTH_BUILD_DIR=None, HOME='/nonexistent-home'), cwd='/')
                self.assertEqual(again.returncode, 0, again.stderr)
                repeated = json.loads(read(absolute + '.build.json'))
                self.assertEqual(repeated['cargo_home'], os.path.join(self.tmp, 'home', '.cargo'), 'the command spells out the CARGO_HOME the first build used (cargo\'s default)')
                self.assertEqual({k: v for k, v in repeated.items() if k not in ('built_at', 'cargo_home')}, {k: v for k, v in rec.items() if k not in ('built_at', 'cargo_home')},
                                 'repeated from the root folder it makes the same record')

    def test_a_relative_engine_folder_is_recorded_as_the_absolute_folder_it_was(self):
        copy = os.path.join(self.tmp, 'engine copy')
        shutil.copytree(self.engine, copy)
        r = self.run_build(os.path.join(self.tmp, 'out', 'strength'), ref='engine copy')
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(read(os.path.join(self.tmp, 'out', 'strength.build.json')))
        self.assertEqual((rec['engine_arg'], rec['engine']), (copy, f'dir:{copy}'))
        self.assertEqual(r.stdout.splitlines()[0], f'engine: dir:{copy}')
        self.assertEqual(shlex.split(rec['rebuild_command'])[-2], copy)

    # ------------------------------------------------------------------------------------------------------ a link as the output: the record sits beside the NAME
    def test_a_link_named_as_the_output_gets_its_record_beside_the_link_and_the_program_is_written_through_the_link(self):
        """OUT's folder part is resolved but its file name is kept as given: slow_report.py --program looks for PROGRAM.build.json beside the name it is given, and cp writes the program
        through a link into the file the link names (resolving the whole path would have put the record beside the target, where nobody looks)."""
        real = os.path.join(self.tmp, 'real-place', 'the-real-file')
        write_bytes(real, b'an older program\n')
        link = os.path.join(self.tmp, 'linked', 'strength')
        os.makedirs(os.path.dirname(link))
        os.symlink(real, link)
        r = self.run_build(link)
        self.assertEqual((r.returncode, r.stderr), (0, ''))
        self.assertTrue(os.path.islink(link), 'the link is still a link: cp wrote through it')
        self.assertEqual((read_bytes(link), read_bytes(real)), (self.STUB_PROGRAM, self.STUB_PROGRAM))
        self.assertEqual(sorted(os.listdir(os.path.dirname(link))), ['strength', 'strength.build.json'], 'the record is beside the link')
        self.assertEqual(os.listdir(os.path.dirname(real)), ['the-real-file'], 'and not beside the file the link names')
        rec = json.loads(read(link + '.build.json'))
        self.assertEqual((rec['program'], rec['program_sha256']), (link, hashlib.sha256(self.STUB_PROGRAM).hexdigest()), 'the record names the link, and the sha256 of what is behind it')
        lines = r.stdout.splitlines()
        self.assertEqual((lines[2], lines[5]), (f'program: {link}', f'build record: {link}.build.json'))
        self.assertEqual(shlex.split(rec['rebuild_command'])[-1], link, 'and the rebuild command names the link')

    def test_a_dangling_link_named_as_the_output_either_works_through_the_link_or_is_refused_before_cargo_runs(self):
        """With OUT's file name kept as given, a link to a place where nothing is there yet would be handed to cp, which will not write through a dangling link ("cp: not writing through
        dangling symlink"): build.sh would end with exit 1 AFTER the compile, with no program and no record. It refuses (exit 2, 'a symbolic link to nothing') before cargo is called."""
        link, target = os.path.join(self.tmp, 'linked', 'strength'), os.path.join(self.tmp, 'later', 'strength-file')
        os.makedirs(os.path.dirname(link))
        os.makedirs(os.path.dirname(target))
        os.symlink(target, link)
        r = self.run_build(link)
        if r.returncode == 0:
            self.assertEqual(read_bytes(target), self.STUB_PROGRAM)
            self.assertTrue(os.path.isfile(link + '.build.json'))
        else:
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertFalse(os.path.exists(self.log), 'refused before cargo was called')

    def test_a_link_in_a_relative_output_keeps_its_name_and_a_link_in_the_folder_part_is_resolved(self):
        work, real_folder = os.path.join(self.tmp, 'work'), os.path.join(self.tmp, 'real-folder')
        for how, out, record_beside in (('a relative link to a file, given by its name', 'file-link', os.path.join('work', 'file-link')),
                                        ('the same with ./ before it', os.path.join('.', 'file-link'), os.path.join('work', 'file-link')),
                                        ('the same behind a dot dot through a folder that is not there', os.path.join('nope', '..', 'file-link'), os.path.join('work', 'file-link')),
                                        ('a file in a relative link to a folder', os.path.join('folder-link', 'strength'), os.path.join('real-folder', 'strength')),
                                        ('a link to a file inside a link to a folder', os.path.join('folder-link', 'inner-link'), os.path.join('real-folder', 'inner-link'))):
            with self.subTest(output=how):
                for folder in (work, real_folder):
                    shutil.rmtree(folder, ignore_errors=True)
                    os.makedirs(folder)
                write_bytes(os.path.join(real_folder, 'target-file'), b'an older program\n')
                os.symlink(os.path.join('..', 'real-folder', 'target-file'), os.path.join(work, 'file-link'))
                os.symlink(os.path.join('..', 'real-folder'), os.path.join(work, 'folder-link'))
                os.symlink('target-file', os.path.join(real_folder, 'inner-link'))
                r = self.run_build(out, cwd=work)
                self.assertEqual((r.returncode, r.stderr), (0, ''))
                beside = os.path.join(self.tmp, record_beside)
                self.assertTrue(os.path.isfile(beside + '.build.json'), f'the record is beside {record_beside}')
                self.assertEqual(sorted(n for n in os.listdir(work) if n.endswith('.build.json')) + sorted(n for n in os.listdir(real_folder) if n.endswith('.build.json')),
                                 [os.path.basename(beside) + '.build.json'], 'and there is no other record')
                rec = json.loads(read(beside + '.build.json'))
                self.assertEqual(rec['program'], beside, 'the record names the path with its folder resolved and its name kept')
                self.assertEqual(rec['program_sha256'], hashlib.sha256(self.STUB_PROGRAM).hexdigest())
                if 'link' in os.path.basename(beside):
                    self.assertTrue(os.path.islink(beside))
                    self.assertEqual(read_bytes(os.path.join(real_folder, 'target-file')), self.STUB_PROGRAM, 'the program went through the link into the file it names')

    def test_a_link_to_the_pinned_binary_is_refused_however_the_path_to_the_link_is_written(self):
        """The guard compares the path with every link in it resolved (also where nothing is there: a laptop's pin on another machine) and the file itself (a hard link)."""
        work = os.path.join(self.tmp, 'work')
        os.makedirs(work)
        absent = os.path.join(self.tmp, 'laptop-home', 'kx', 'strength')
        os.symlink(os.path.join('..', 'frozen', 'strength'), os.path.join(work, 'relative-link'))
        os.symlink(self.frozen, os.path.join(work, 'absolute-link'))
        os.symlink('relative-link', os.path.join(work, 'link-to-link'))
        os.symlink(os.path.join('..', 'frozen'), os.path.join(work, 'folder-link'))
        os.symlink(absent, os.path.join(work, 'link-to-absent'))
        os.link(self.frozen, os.path.join(work, 'hard-link'))
        for how, out, pinned in (('a relative link, by its name', 'relative-link', self.frozen), ('an absolute link', 'absolute-link', self.frozen),
                                 ('a link to a link', 'link-to-link', self.frozen), ('a link with ./ before it', os.path.join('.', 'relative-link'), self.frozen),
                                 ('a link behind a dot dot through a folder that is not there', os.path.join('nope', '..', 'relative-link'), self.frozen),
                                 ('a file in a link to the pinned folder', os.path.join('folder-link', 'strength'), self.frozen), ('a hard link', 'hard-link', self.frozen),
                                 ('a link to a pinned path where nothing is', 'link-to-absent', absent)):
            with self.subTest(output=how):
                self.lay_out_pin(pinned)
                self.assert_nothing_was_done(self.run_build(out, cwd=work), pinned)
                self.assertEqual(read_bytes(os.path.join(work, 'hard-link')), self.FROZEN)
        self.lay_out_pin(self.frozen)
        os.symlink(os.path.join('..', 'elsewhere', 'a-new-file'), os.path.join(work, 'link-elsewhere'))
        os.makedirs(os.path.join(self.tmp, 'elsewhere'))
        write_bytes(os.path.join(self.tmp, 'elsewhere', 'a-new-file'), b'x\n')
        self.assertEqual(self.run_build('link-elsewhere', cwd=work).returncode, 0, 'and a link to any other file is fine')
        self.assertEqual(read_bytes(self.frozen), self.FROZEN)

    def test_a_relative_build_folder_builds_like_a_relative_output(self):
        """OUT and a folder REF are made absolute at the top, and so are STRENGTH_BUILD_DIR and STRENGTH_TARGET_DIR: the script changes folder before cargo's output is redirected to
        "$W/cargo.log", so a relative build folder used to make that redirection fail (cargo never ran, and the script said 'cargo build failed', exit 1), and the record's build_dir and
        the rebuild command would have carried a relative path. (A known defect until the folders were made absolute like OUT.)"""
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        r = self.run_build(out, STRENGTH_BUILD_DIR='relative-build-folder')
        self.assertEqual((r.returncode, r.stderr), (0, ''))
        rec = json.loads(read(out + '.build.json'))
        self.assertEqual((rec['build_dir'], rec['target_dir']), (os.path.join(self.tmp, 'relative-build-folder'), os.path.join(self.tmp, 'relative-build-folder', 'target')))

    def test_relative_build_and_target_folders_are_made_absolute_from_any_working_folder_and_the_record_and_the_rebuild_command_carry_them_absolute(self):
        work = os.path.join(self.tmp, 'work')
        absolute_build, absolute_target = os.path.join(self.tmp, 'build'), os.path.join(work, 'rel-target')
        for n, (how, env, want_build, want_target) in enumerate((
                ('a relative build folder', dict(STRENGTH_BUILD_DIR='rel-build'), os.path.join(work, 'rel-build'), os.path.join(work, 'rel-build', 'target')),
                ('a relative target folder', dict(STRENGTH_TARGET_DIR='rel-target'), absolute_build, absolute_target),
                ('both relative, the target in a folder that is not there yet', dict(STRENGTH_BUILD_DIR='rel-build', STRENGTH_TARGET_DIR=os.path.join('not', 'yet', 'rel-target')),
                 os.path.join(work, 'rel-build'), os.path.join(work, 'not', 'yet', 'rel-target')),
                ('a dot dot through a folder that is not there', dict(STRENGTH_BUILD_DIR=os.path.join('nope', '..', 'rel-build'), STRENGTH_TARGET_DIR=os.path.join('nope', '..', 'rel-target')),
                 os.path.join(work, 'rel-build'), absolute_target),
                ('a dot and a trailing slash', dict(STRENGTH_BUILD_DIR='./rel-build/', STRENGTH_TARGET_DIR='./rel-target/'), os.path.join(work, 'rel-build'), absolute_target))):
            with self.subTest(folders=how):
                shutil.rmtree(work, ignore_errors=True)
                os.makedirs(work)
                shutil.rmtree(absolute_build, ignore_errors=True)
                if os.path.exists(self.log):
                    os.remove(self.log)
                out = os.path.join(self.tmp, f'elsewhere-{n}', 'strength')
                r = self.run_build(out, cwd=work, **env)
                self.assertEqual((r.returncode, r.stderr), (0, ''), r.stdout)
                self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
                rec = json.loads(read(out + '.build.json'))
                self.assertEqual((rec['build_dir'], rec['target_dir']), (want_build, want_target), 'absolute, whatever folder the script was started from')
                self.assertEqual(read(self.log).splitlines(), [f'build --release --offline | target={want_target}'], 'cargo built into the absolute target folder')
                self.assertTrue(os.path.isfile(os.path.join(want_build, 'cargo.log')), "cargo's output went to the build folder asked for, not to a path relative to where the script moved to")
                self.assertTrue(os.path.isfile(os.path.join(want_target, 'release', 'strength')))
                assignments = dict(w.split('=', 1) for w in shlex.split(rec['rebuild_command'])[1:shlex.split(rec['rebuild_command']).index('bash')])
                self.assertEqual((assignments['STRENGTH_BUILD_DIR'], assignments['STRENGTH_TARGET_DIR']), (want_build, want_target), 'the rebuild command carries them absolute')
                words = shlex.split(rec['rebuild_command'])
                os.remove(out)
                os.remove(out + '.build.json')
                again = subprocess.run(words, capture_output=True, text=True, env=self.env(STRENGTH_BUILD_DIR=None, HOME='/nonexistent-home'), cwd='/')
                self.assertEqual(again.returncode, 0, again.stderr)
                repeated = json.loads(read(out + '.build.json'))
                self.assertEqual({k: v for k, v in repeated.items() if k not in ('built_at', 'cargo_home')}, {k: v for k, v in rec.items() if k not in ('built_at', 'cargo_home')},
                                 'repeated from the root folder it makes the same record')

    def test_two_builds_in_different_build_folders_that_share_a_target_folder_do_not_swap_programs(self):
        """The lock was on the build folder only, but cargo's program is taken from the target folder, which STRENGTH_TARGET_DIR can make the same for two build folders. The second
        build used to delete the first one's program from it (rm -f) and write its own; the first then copied the second's program as its own, with a record of its own engine tree
        and harness. Now the second build is refused (a lock on the target folder too). (A known defect until the target folder had its own lock.)"""
        started, release = os.path.join(self.tmp, 'started'), os.path.join(self.tmp, 'release')
        shared = os.path.join(self.tmp, 'shared-target')
        self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + self.CARGO_BUILDS + ': > "$STUB_STARTED"\nfor i in $(seq 1 300); do [ -e "$STUB_RELEASE" ] && break; sleep 0.1; done\n')
        first_out = os.path.join(self.tmp, 'first', 'strength')
        first = subprocess.Popen(['bash', os.path.join(self.here, 'build.sh'), self.engine, first_out], cwd=self.tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env=self.env(STUB_STARTED=started, STUB_RELEASE=release, STUB_PROGRAM_TEXT='the program of the first build', STRENGTH_TARGET_DIR=shared))
        self.addCleanup(self.release_and_wait, first, release)
        deadline = time.time() + 30
        while not os.path.exists(started):
            self.assertIsNone(first.poll(), 'the first build ended before cargo finished')
            self.assertLess(time.time(), deadline)
            time.sleep(0.05)
        second = self.run_build(os.path.join(self.tmp, 'second', 'strength'), STRENGTH_BUILD_DIR=os.path.join(self.tmp, 'build-two'), STRENGTH_TARGET_DIR=shared,
                                STUB_STARTED=os.path.join(self.tmp, 'started-two'), STUB_RELEASE=started, STUB_PROGRAM_TEXT='the program of the second build')
        write(release, '')
        first.communicate(timeout=60)
        self.assertIn(second.returncode, (0, 2))
        self.assertEqual(read_bytes(first_out), b'the program of the first build\n')

    # ------------------------------------------------------------------------------------------------------ one build at a time per build folder
    def stuck_cargo(self):
        """A stub cargo that says it has started (it creates $STUB_STARTED), waits until $STUB_RELEASE exists (60 s at most), and then builds like the default one."""
        self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + ': > "$STUB_STARTED"\nfor i in $(seq 1 600); do [ -e "$STUB_RELEASE" ] && break; sleep 0.1; done\n' + self.CARGO_BUILDS)

    def release_and_wait(self, proc, release):
        if proc.poll() is None:  # a test that failed with the build still waiting: open its gate, so it ends
            write(release, '')
            try:
                proc.communicate(timeout=60)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()

    def test_a_second_build_in_the_same_build_folder_is_refused_while_the_first_runs_and_one_in_another_folder_or_after_it_is_fine(self):
        """Every build empties $W/tree first: a second build in the same folder would delete the first one's source while it compiles. The lock is flock on $W/build.lock, taken without
        waiting; the second build says so and exits 2 before it touches anything."""
        self.stuck_cargo()
        started, release, open_gate = (os.path.join(self.tmp, n) for n in ('started', 'release', 'open-gate'))
        write(open_gate, '')
        w = os.path.join(self.tmp, 'build')
        first_out = os.path.join(self.tmp, 'first', 'strength')
        first = subprocess.Popen(['bash', os.path.join(self.here, 'build.sh'), self.engine, first_out], cwd=self.tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env=self.env(STUB_STARTED=started, STUB_RELEASE=release))
        self.addCleanup(self.release_and_wait, first, release)
        deadline = time.time() + 30
        while not os.path.exists(started):
            self.assertIsNone(first.poll(), 'the first build ended before its cargo started')
            self.assertLess(time.time(), deadline, 'the first build never got to cargo')
            time.sleep(0.05)
        marker = os.path.join(w, 'tree', 'marker')
        write(marker, "the first build's source: a second build would delete it")
        self.assertTrue(os.path.isfile(os.path.join(w, 'build.lock')))
        second_out = os.path.join(self.tmp, 'second', 'strength')
        try:
            second = subprocess.run(['bash', os.path.join(self.here, 'build.sh'), self.engine, second_out], cwd=self.tmp, text=True, capture_output=True, timeout=20,
                                    env=self.env(STUB_STARTED=started, STUB_RELEASE=open_gate))
        except subprocess.TimeoutExpired:
            self.fail('the second build waited for the lock instead of refusing at once')
        self.assertEqual((second.returncode, second.stdout), (2, ''))
        self.assertEqual(second.stderr, f"build.sh: another build is using {w} (STRENGTH_BUILD_DIR); wait for it or use another folder (a second build would delete the first one's source while it compiles)\n")
        self.assertFalse(os.path.exists(second_out) or os.path.exists(second_out + '.build.json') or os.path.exists(os.path.dirname(second_out)), 'the refused build made nothing')
        self.assertTrue(os.path.isfile(marker), "and deleted nothing of the first build's")
        self.assertIsNone(first.poll(), 'the first build is still running')
        other = self.run_build(os.path.join(self.tmp, 'other', 'strength'), STRENGTH_BUILD_DIR=os.path.join(self.tmp, 'build-two'), STUB_STARTED=started, STUB_RELEASE=open_gate)
        self.assertEqual((other.returncode, other.stderr), (0, ''), 'a build in another build folder does not wait for the first and is not refused')
        self.assertEqual(read_bytes(os.path.join(self.tmp, 'other', 'strength')), self.STUB_PROGRAM)
        self.assertIsNone(first.poll())
        write(release, '')
        stdout, stderr = first.communicate(timeout=60)
        self.assertEqual((first.returncode, stderr), (0, ''), stdout)
        self.assertEqual(read_bytes(first_out), self.STUB_PROGRAM)
        self.assertTrue(os.path.isfile(first_out + '.build.json'))
        self.assertTrue(os.path.isfile(marker), "the first build did not lose its source either")
        third = self.run_build(os.path.join(self.tmp, 'third', 'strength'), STUB_STARTED=started, STUB_RELEASE=open_gate)
        self.assertEqual((third.returncode, third.stderr), (0, ''), 'once the first has ended the folder is free again')

    # ------------------------------------------------------------------------------------------------------ one build at a time per target folder too
    def start_stuck_build(self, out, started, release, **env_changes):
        """A build whose stub cargo has started and waits for $STUB_RELEASE (stuck_cargo); returns the running process, which the test's cleanup lets go."""
        first = subprocess.Popen(['bash', os.path.join(self.here, 'build.sh'), self.engine, out], cwd=self.tmp, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 env=self.env(STUB_STARTED=started, STUB_RELEASE=release, **env_changes))
        self.addCleanup(self.release_and_wait, first, release)
        deadline = time.time() + 30
        while not os.path.exists(started):
            self.assertIsNone(first.poll(), 'the first build ended before its cargo started')
            self.assertLess(time.time(), deadline, 'the first build never got to cargo')
            time.sleep(0.05)
        return first

    def run_build_at_once(self, out, **env_changes):
        """run_build, failing the test when the build waits for a lock instead of answering (20 s)."""
        try:
            return subprocess.run(['bash', os.path.join(self.here, 'build.sh'), self.engine, out], cwd=self.tmp, text=True, capture_output=True, timeout=20, env=self.env(**env_changes))
        except subprocess.TimeoutExpired:
            self.fail('the build waited for a lock instead of answering at once')

    def target_message(self, target):
        return f'build.sh: another build is using the target folder {target} (STRENGTH_TARGET_DIR); wait for it or use another target folder (two builds would swap programs)\n'

    def test_a_second_build_that_shares_the_target_folder_is_refused_naming_it_while_the_first_runs_and_another_target_folder_or_a_later_time_is_fine(self):
        """Two build folders can name one target folder, and cargo's program is taken from it: a second flock, on $TARGET.lock, taken without waiting, keeps the builds apart."""
        self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + self.CARGO_BUILDS + ': > "$STUB_STARTED"\nfor i in $(seq 1 600); do [ -e "$STUB_RELEASE" ] && break; sleep 0.1; done\n')  # (builds, then waits)
        started, release, open_gate = (os.path.join(self.tmp, n) for n in ('started', 'release', 'open-gate'))
        write(open_gate, '')
        shared, two = os.path.join(self.tmp, 'shared-target'), os.path.join(self.tmp, 'build-two')
        first_out = os.path.join(self.tmp, 'first', 'strength')
        first = self.start_stuck_build(first_out, started, release, STUB_PROGRAM_TEXT='the program of the first build', STRENGTH_TARGET_DIR=shared)
        self.assertTrue(os.path.isfile(shared + '.lock'), 'the lock file is beside the target folder')
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, 'build', 'build.lock')), 'and the build folder has its own')
        second_out = os.path.join(self.tmp, 'second', 'strength')
        second = self.run_build_at_once(second_out, STRENGTH_BUILD_DIR=two, STRENGTH_TARGET_DIR=shared, STUB_STARTED=started, STUB_RELEASE=open_gate)
        self.assertEqual((second.returncode, second.stdout), (2, ''))
        self.assertEqual(second.stderr, self.target_message(shared))
        self.assertFalse(os.path.exists(second_out) or os.path.exists(second_out + '.build.json') or os.path.exists(os.path.dirname(second_out)), 'the refused build made nothing')
        self.assertFalse(os.path.exists(os.path.join(two, 'tree')), 'and cleared nothing in its own build folder')
        self.assertEqual(read_bytes(os.path.join(shared, 'release', 'strength')), b'the program of the first build\n', "and did not take the first build's program out of the target folder")
        self.assertIsNone(first.poll(), 'the first build is still running')
        same_folder = self.run_build_at_once(second_out, STRENGTH_TARGET_DIR=shared, STUB_STARTED=started, STUB_RELEASE=open_gate)
        self.assertEqual((same_folder.returncode, same_folder.stdout), (2, ''))
        self.assertIn('another build is using ' + os.path.join(self.tmp, 'build'), same_folder.stderr, 'the same build folder is still the build folder message, which is the first check')
        other = self.run_build_at_once(os.path.join(self.tmp, 'other', 'strength'), STRENGTH_BUILD_DIR=two, STRENGTH_TARGET_DIR=os.path.join(self.tmp, 'other-target'), STUB_STARTED=started,
                                       STUB_RELEASE=open_gate)
        self.assertEqual((other.returncode, other.stderr), (0, ''), 'another build folder and another target folder do not wait for the first and are not refused (and the refused build gave its own folder back)')
        self.assertEqual(read_bytes(os.path.join(self.tmp, 'other', 'strength')), self.STUB_PROGRAM)
        self.assertIsNone(first.poll())
        write(release, '')
        stdout, stderr = first.communicate(timeout=60)
        self.assertEqual((first.returncode, stderr), (0, ''), stdout)
        self.assertEqual(read_bytes(first_out), b'the program of the first build\n', "the first build's output is its own program")
        third = self.run_build_at_once(os.path.join(self.tmp, 'third', 'strength'), STRENGTH_BUILD_DIR=two, STRENGTH_TARGET_DIR=shared, STUB_STARTED=started, STUB_RELEASE=open_gate)
        self.assertEqual((third.returncode, third.stderr), (0, ''), 'once the first has ended the target folder is free again')
        self.assertEqual(read_bytes(os.path.join(self.tmp, 'third', 'strength')), self.STUB_PROGRAM)

    def test_a_build_that_fails_gives_the_target_folder_back_too(self):
        failed = self.run_build(os.path.join(self.tmp, 'first', 'strength'), STUB_CARGO_FAILS='1', STRENGTH_TARGET_DIR=os.path.join(self.tmp, 'target-dir'))
        self.assertEqual(failed.returncode, 1)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, 'target-dir.lock')))
        after = self.run_build(os.path.join(self.tmp, 'second', 'strength'), STRENGTH_BUILD_DIR=os.path.join(self.tmp, 'build-two'), STRENGTH_TARGET_DIR=os.path.join(self.tmp, 'target-dir'))
        self.assertEqual((after.returncode, after.stderr), (0, ''))

    def test_a_process_cargo_leaves_running_does_not_keep_either_lock_after_the_build_has_ended(self):
        """cargo runs with the two lock descriptors closed (9>&- 8>&-): whatever it leaves behind (a build server, a daemon) must not hold the build folder or the target folder
        for as long as it lives, or the next build would be refused for hours by a lock nobody is using."""
        pids = os.path.join(self.tmp, 'sleeper-pids')
        self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + self.CARGO_BUILDS + 'sleep 20 &\necho $! >> "$STUB_PIDS"\n')  # (the test stops every one it started)
        self.addCleanup(lambda: [self.stop(int(p)) for p in (read(pids).split() if os.path.exists(pids) else [])])
        target, two = os.path.join(self.tmp, 'build', 'target'), os.path.join(self.tmp, 'build-two')
        first = self.run_build_at_once(os.path.join(self.tmp, 'first', 'strength'), STUB_PIDS=pids)
        self.assertEqual((first.returncode, first.stderr), (0, ''))
        sleeper = int(read(pids).split()[0])
        for n, (how, env) in enumerate((('the same build folder and the same target folder', {}),
                                        ('the same build folder, another target folder', dict(STRENGTH_TARGET_DIR=os.path.join(self.tmp, 'target-two'))),
                                        ('another build folder, the same target folder', dict(STRENGTH_BUILD_DIR=two, STRENGTH_TARGET_DIR=target)))):
            with self.subTest(next_build=how):
                os.kill(sleeper, 0)  # (still running: it was left behind, so an inherited lock would still be held)
                r = self.run_build_at_once(os.path.join(self.tmp, f'next-{n}', 'strength'), STUB_PIDS=pids, **env)
                self.assertEqual((r.returncode, r.stderr), (0, ''), 'the process left running by the first build holds neither lock')

    @staticmethod
    def stop(pid):
        """Stop a process this test started (by its number), if it is still there."""
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            pass

    def test_a_build_that_fails_gives_the_build_folder_back(self):
        failed = self.run_build(os.path.join(self.tmp, 'first', 'strength'), STUB_CARGO_FAILS='1')
        self.assertEqual(failed.returncode, 1)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, 'build', 'build.lock')))
        after = self.run_build(os.path.join(self.tmp, 'second', 'strength'))
        self.assertEqual((after.returncode, after.stderr), (0, ''))

    def test_without_flock_the_build_goes_on_and_says_it_cannot_keep_two_builds_apart(self):
        """flock is part of util-linux: a machine without it still builds, with a warning on stderr instead of the lock."""
        farm = os.path.join(self.tmp, 'tools-without-flock')
        os.makedirs(farm)
        for tool in ('bash', 'env', 'readlink', 'dirname', 'basename', 'mkdir', 'rm', 'cp', 'find', 'touch', 'cat', 'cut', 'grep', 'head', 'tr', 'sha256sum', 'nice', 'git', 'tar', 'python3',
                     'uname', 'ldd', 'hostname', 'sort', 'sed', 'awk', 'ls', 'sleep', 'seq'):
            if shutil.which(tool):
                os.symlink(shutil.which(tool), os.path.join(farm, tool))
        self.assertIsNone(shutil.which('flock', path=self.stub + os.pathsep + farm), 'this PATH has no flock')
        self.assertTrue(os.path.islink(os.path.join(farm, 'basename')), 'the output path is split with dirname and basename: both are on this PATH')
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        r = self.run_build(out, PATH=self.stub + os.pathsep + farm)
        w = os.path.join(self.tmp, 'build')
        self.assertEqual((r.returncode, r.stderr), (0, f'build.sh: warning: flock is not installed, so two builds in {w} at the same time are not prevented\n'),
                         'one warning, naming the build folder; the target folder has no second one')
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        self.assertTrue(os.path.isfile(out + '.build.json'))
        self.assertFalse(os.path.exists(os.path.join(w, 'build.lock')) or os.path.exists(os.path.join(w, 'target.lock')), 'and no lock file was made')
        with_flock = self.run_build(os.path.join(self.tmp, 'with-flock', 'strength'))
        self.assertEqual((with_flock.returncode, with_flock.stderr), (0, ''), 'and with flock on the PATH there is no warning')


class BuildPinGuard(BuildWorld):
    """The guard reads the pin as JSON (python3), whatever its layout, and refuses with exit 2 and a message when it cannot tell which path is the pinned one."""

    def missing_message(self):
        return ("build.sh: cannot find slow_report_pin.json beside this script, so it cannot tell whether OUT is the slow report's pinned program; "
                "refusing (set STRENGTH_SKIP_PIN_GUARD=1 to build anyway)\n")

    def unreadable_message(self):
        return (f'build.sh: cannot read the "program" entry of {self.here}/slow_report_pin.json, so it cannot tell whether OUT is the pinned program; '
                'refusing (set STRENGTH_SKIP_PIN_GUARD=1 to build anyway)\n')

    def assert_refused(self, r, message):
        """Exit 2, nothing on stdout and the message, and only the message, on stderr (python3's own complaint about the pin, a traceback, is hidden: the message says why)."""
        self.assertEqual((r.returncode, r.stdout), (2, ''))
        self.assertEqual(r.stderr, message)
        self.assertNotIn('Traceback', r.stderr)
        self.assertFalse(os.path.exists(self.log), 'cargo was not called')
        self.assertFalse(os.path.exists(os.path.join(self.tmp, 'build')), 'the build folder was not touched')

    def test_a_missing_pin_is_exit_2_with_a_clear_message_and_nothing_is_done(self):
        os.remove(os.path.join(self.here, 'slow_report_pin.json'))
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        self.assert_refused(self.run_build(out), self.missing_message())
        self.assertFalse(os.path.exists(os.path.dirname(out)), 'and it made no folder')
        os.mkdir(os.path.join(self.here, 'slow_report_pin.json'))  # a folder of that name is no pin either
        self.assert_refused(self.run_build(out), self.missing_message())

    def test_a_pin_that_gives_no_program_entry_is_exit_2_with_a_clear_message_and_nothing_is_done(self):
        for how, data in (('no program entry', json.dumps({'_note': 'x', 'program_sha256': '0' * 64}).encode()), ('cut off', b'{"program": '), ('empty', b''), ('a list', b'[1, 2]'),
                          ('a string', b'"/x/y"'), ('a number', b'7'), ('null', b'null'), ('not text', b'\xff\xfe\x00{'), ('program_sha256 only', b'{"program_sha256": "' + b'0' * 64 + b'"}'),
                          ('the program entry is null', b'{"program": null, "program_sha256": "' + b'0' * 64 + b'"}'), ('the program entry is an empty text', b'{"program": ""}'),
                          ('the program entry is a number', b'{"program": 5}'), ('the program entry is true', b'{"program": true}'),
                          ('the program entry is a list of paths', b'{"program": ["/x/y"]}'), ('the program entry is a mapping', b'{"program": {"path": "/x/y"}}'),
                          ('the program entry is there twice, the last one null', b'{"program": "/x/y", "program": null}')):
            with self.subTest(pin=how):
                write_bytes(os.path.join(self.here, 'slow_report_pin.json'), data)
                out = os.path.join(self.tmp, 'elsewhere', 'strength')
                self.assert_refused(self.run_build(out), self.unreadable_message())
                self.assertFalse(os.path.exists(os.path.dirname(out)))

    def test_the_guard_does_not_rely_on_an_assert_so_python_without_assertions_still_refuses_a_program_entry_that_is_not_a_path(self):
        """PYTHONOPTIMIZE=1 (or 2) strips assert statements: a guard that tested the pin's program entry with one would print 'None', '' or '5' as if it were a path, find that it is
        not the output path, and build anyway (over a binary it could not name). The test is an `if` and an exit."""
        guard = re.search(r"PIN_PROGRAM=\$\(python3 -c '([^']*)'", read(os.path.join(HERE, 'build.sh'))).group(1)
        self.assertNotIn('assert', guard, 'the guard has no assert statement')
        stripped = subprocess.run([shutil.which('python3'), '-c', 'assert False\nprint("assertions are stripped")'], capture_output=True, text=True, env=dict(os.environ, PYTHONOPTIMIZE='1'))
        self.assertEqual(stripped.stdout.strip(), 'assertions are stripped', 'PYTHONOPTIMIZE=1 does strip them on the python3 build.sh calls: this test can tell')
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        for optimize in ('1', '2'):
            for how, data in (('null', b'{"program": null}'), ('an empty text', b'{"program": ""}'), ('a number', b'{"program": 5}'), ('true', b'{"program": true}'),
                              ('a list of paths', b'{"program": ["/x/y"]}'), ('a mapping', b'{"program": {"path": "/x/y"}}'), ('no program entry', b'{"program_sha256": "00"}'),
                              ('cut off', b'{"program": '), ('not a mapping', b'[1, 2]')):
                with self.subTest(PYTHONOPTIMIZE=optimize, program=how):
                    write_bytes(os.path.join(self.here, 'slow_report_pin.json'), data)
                    self.assert_refused(self.run_build(out, PYTHONOPTIMIZE=optimize), self.unreadable_message())
                    self.assertFalse(os.path.exists(os.path.dirname(out)))
        self.lay_out_pin(self.frozen)
        for optimize in ('1', '2'):
            with self.subTest(PYTHONOPTIMIZE=optimize, pin='a good one'):
                self.assertEqual(self.run_build(self.frozen, PYTHONOPTIMIZE=optimize).stderr, self.refusal(self.frozen), 'a good pin still guards the pinned path')
                r = self.run_build(out, PYTHONOPTIMIZE=optimize)
                self.assertEqual((r.returncode, r.stderr), (0, ''), 'and any other path is built')
        self.assertEqual(read_bytes(self.frozen), self.FROZEN)

    def test_a_reformatted_pin_still_guards_the_pinned_path_because_it_is_read_as_json(self):
        pin = {'_note': 'a test pin', 'program': self.frozen, 'program_sha256': '0' * 64}
        escaped = ''.join(f'\\u{ord(c):04x}' for c in self.frozen)
        layouts = {'compact, on one line': json.dumps(pin, separators=(',', ':')), 'compact, the program entry last': json.dumps(dict(reversed(list(pin.items()))), separators=(',', ':')),
                   'the program entry first': json.dumps(dict(program=self.frozen, **{k: v for k, v in pin.items() if k != 'program'}), indent=1),
                   'indented by four': json.dumps(pin, indent=4), 'indented with tabs': json.dumps(pin, indent='\t'), 'CRLF line ends': json.dumps(pin, indent=1).replace('\n', '\r\n'),
                   'blank lines and trailing spaces': json.dumps(pin, indent=1).replace('\n', '  \n\n'), 'the path written with \\u escapes': '{"program": "' + escaped + '"}',
                   'no space after the colon, the key not first on its line': '{"_note":"a test pin","x":1,\n  "program"  :  "' + self.frozen + '"}'}
        for how, text in layouts.items():
            with self.subTest(layout=how):
                shutil.rmtree(os.path.join(self.tmp, 'build'), ignore_errors=True)
                if os.path.exists(self.log):
                    os.remove(self.log)
                write_bytes(os.path.join(self.here, 'slow_report_pin.json'), text.encode())
                r = self.run_build(self.frozen)
                self.assertEqual((r.returncode, r.stdout, r.stderr), (2, '', self.refusal(self.frozen)), 'the pinned path is found, so the message is the refusal of that path')
                self.assertEqual(read_bytes(self.frozen), self.FROZEN)
                self.assertFalse(os.path.exists(self.log))
                self.assertEqual(self.run_build(os.path.join(self.tmp, 'elsewhere', 'strength')).returncode, 0, 'and any other path is fine')

    def test_skipping_the_guard_builds_anyway(self):
        """STRENGTH_SKIP_PIN_GUARD=1 (any non-empty value) turns the guard off, for a pin that is missing or unreadable and for the pinned path itself; empty is not set."""
        pin = os.path.join(self.here, 'slow_report_pin.json')
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        for how, prepare in (('no pin', lambda: os.remove(pin)), ('an unreadable pin', lambda: write(pin, '{not json')), ('a pin that names no program', lambda: write(pin, '{}')),
                             ('a pin whose program is null', lambda: write(pin, '{"program": null}')), ('a pin whose program is an empty text', lambda: write(pin, '{"program": ""}')),
                             ('a pin whose program is a number', lambda: write(pin, '{"program": 5}'))):
            with self.subTest(pin=how):
                self.lay_out_pin(self.frozen)
                prepare()
                shutil.rmtree(os.path.dirname(out), ignore_errors=True)
                self.assertEqual(self.run_build(out).returncode, 2, 'the guard is on without the variable')
                r = self.run_build(out, STRENGTH_SKIP_PIN_GUARD='1')
                self.assertEqual((r.returncode, r.stderr), (0, ''))
                self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        self.lay_out_pin(self.frozen)
        self.assertEqual(self.run_build(self.frozen, STRENGTH_SKIP_PIN_GUARD='').returncode, 2, 'an empty value does not turn it off')
        self.assertEqual(read_bytes(self.frozen), self.FROZEN)
        r = self.run_build(self.frozen, STRENGTH_SKIP_PIN_GUARD='yes')
        self.assertEqual((r.returncode, r.stderr), (0, ''))
        self.assertEqual(read_bytes(self.frozen), self.STUB_PROGRAM, 'switched off on purpose, it builds over the path the pin names (here a file of this test\'s own)')


class BuildRecordFile(BuildWorld):
    """OUT.build.json, the record build.sh writes beside the program and slow_report.py --program requires: what was archived and compiled (git's tree id of the files that were
    actually extracted, computed from them and not read back from the ref), the harness source, the program's sha256, the toolchain and the build paths, and the command that
    repeats the build."""

    def build(self, ref=None, out=None, **env):
        """A build that must work: (the program's path, its record, the lines it printed); what it wrote on stderr is kept in self.last_stderr."""
        out = out or os.path.join(self.tmp, 'elsewhere', 'strength')
        r = self.run_build(out, ref=ref, **env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.last_stderr = r.stderr
        return out, json.loads(read(out + '.build.json')), r.stdout.splitlines()

    def shell(self, command):
        return subprocess.run(command, shell=True, capture_output=True, text=True).stdout.rstrip('\n')

    def test_the_record_has_every_field_with_its_type_and_the_values_of_the_build(self):
        commit, tree = self.commit_engine()
        cargo_home, target = os.path.join(self.tmp, 'cargo-home'), os.path.join(self.tmp, 'target-dir')
        t0 = datetime.datetime.now(UTC).replace(microsecond=0)
        out, rec, printed = self.build(CARGO_HOME=cargo_home, STRENGTH_JOBS='3', STRENGTH_TARGET_DIR=target)
        t1 = datetime.datetime.now(UTC)
        self.assertEqual(sorted(rec), sorted(RECORD_FIELDS), 'every field and no other')
        self.assertIs(type(rec['schema']), int)
        self.assertEqual(rec['schema'], 1)
        for key in set(RECORD_FIELDS) - {'schema', 'engine_ref', 'cargo_home'} - set(LIST_FIELDS):
            self.assertIsInstance(rec[key], str, key)
        self.assertEqual(rec['build_env_unset'], [], 'nothing was removed from the environment')
        self.assertEqual([c for c in rec['cargo_config_files'] if c['path'].startswith(self.tmp + os.sep)], [], 'and no cargo config file of this world applies (the machine may have its own above the temporary folder)')
        self.assertEqual((rec['program'], rec['engine_arg'], rec['engine'], rec['engine_ref']), (out, self.engine, f'dir:{self.engine}', None), 'a folder has no commit')
        self.assertEqual(rec['program_sha256'], hashlib.sha256(self.STUB_PROGRAM).hexdigest())
        self.assertEqual(rec['program_sha256'], sha(out), 'the sha256 of the file the record sits beside')
        self.assertIn(f'program sha256: {rec["program_sha256"]}', printed, 'and the one build.sh prints')
        self.assertEqual(rec['engine_tree_archived'], tree, 'the tree of the files that were compiled: the same files, committed, have this id')
        self.assertIn(f'engine tree as archived: {tree}', printed)
        self.assertEqual(rec['harness_source_sha256'], sr.harness_source_sha256(self.tmp))
        self.assertIn(f'harness source sha256: {rec["harness_source_sha256"]}', printed)
        self.assertEqual((rec['rustc'], rec['cargo']), (self.RUSTC, self.CARGO), 'rustc -vV and cargo -V, without the final line end')
        self.assertEqual(rec['machine'], self.shell('uname -srm'))
        self.assertEqual(rec['libc'], self.shell('(ldd --version 2>&1 || true) | head -1'))
        self.assertEqual(rec['host'], self.shell('hostname 2>/dev/null || true'))
        self.assertEqual((rec['home'], rec['cargo_home'], rec['build_dir'], rec['target_dir'], rec['jobs']),
                         (os.path.join(self.tmp, 'home'), cargo_home, os.path.join(self.tmp, 'build'), target, '3'))
        self.assertRegex(rec['built_at'], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')
        built = datetime.datetime.strptime(rec['built_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=UTC)
        self.assertTrue(t0 <= built <= t1 + datetime.timedelta(seconds=1), f'{rec["built_at"]} is not the current UTC time ({t0} .. {t1})')
        text = read_bytes(out + '.build.json')
        self.assertTrue(text.startswith(b'{\n "schema": 1,\n'), text[:30])
        self.assertTrue(text.endswith(b'}\n'))
        self.assertNotIn(b'\r', text)
        self.assertFalse(text.startswith(b'\xef\xbb\xbf'))

    def test_the_defaults_when_nothing_is_set_are_recorded_as_what_the_build_used(self):
        """No CARGO_HOME (cargo's own default is HOME/.cargo, but the record says nothing was set), no STRENGTH_JOBS (8), no STRENGTH_TARGET_DIR (under the build folder)."""
        out, rec, printed = self.build()
        self.assertEqual((rec['cargo_home'], rec['jobs'], rec['target_dir'], rec['build_dir']), (None, '8', os.path.join(self.tmp, 'build', 'target'), os.path.join(self.tmp, 'build')))
        out, rec, printed = self.build(STRENGTH_BUILD_DIR=None, out=os.path.join(self.tmp, 'out2', 'strength'))
        home = os.path.join(self.tmp, 'home')
        self.assertEqual((rec['build_dir'], rec['target_dir']), (os.path.join(home, 'strength_build'), os.path.join(home, 'strength_build', 'target')), 'the default build folder is under HOME')

    def test_a_second_build_replaces_the_record_beside_the_same_program(self):
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        commit1, tree1 = self.commit_engine()
        _, first, _ = self.build(ref=commit1, out=out, STUB_PROGRAM_TEXT='the first program')
        write(os.path.join(self.engine, 'Cargo.lock'), '# another engine\n')
        commit2, tree2 = self.commit_engine('another engine')
        _, second, _ = self.build(ref=commit2, out=out, STUB_PROGRAM_TEXT='the second program')
        self.assertEqual(read_bytes(out), b'the second program\n')
        self.assertNotEqual((first['program_sha256'], first['engine_tree_archived'], first['engine_ref']), (second['program_sha256'], second['engine_tree_archived'], second['engine_ref']))
        self.assertEqual((second['program_sha256'], second['engine_tree_archived'], second['engine_ref']), (sha(out), tree2, commit2), 'the record is of the build that made the file')

    def test_for_a_git_ref_the_archived_tree_is_the_ids_of_the_ref_and_the_commit_is_resolved(self):
        commit, tree = self.commit_engine()
        self.git('tag', '-a', 'v1', '-m', 'an annotated tag')
        write(os.path.join(self.engine, 'Cargo.lock'), '# a later engine\n')
        later, later_tree = self.commit_engine('a later engine')
        self.assertNotEqual(tree, later_tree)
        for ref, want_commit, want_tree in ((commit, commit, tree), ('v1', commit, tree), ('HEAD~1', commit, tree), ('main', later, later_tree), ('HEAD', later, later_tree), (later[:10], later, later_tree)):
            with self.subTest(ref=ref):
                out, rec, printed = self.build(ref=ref, out=os.path.join(self.tmp, 'out-' + ref.replace('~', '-'), 'strength'))
                self.assertEqual(rec['engine_arg'], ref)
                self.assertEqual(rec['engine_ref'], want_commit, 'the commit the ref resolved to, in full (an annotated tag is peeled)')
                self.assertEqual(rec['engine_tree_archived'], want_tree, 'git rev-parse REF:engine, for an archive that is what the ref says')
                self.assertEqual(rec['engine'], f'{ref} engine tree {want_tree}')
                self.assertEqual(printed[:2], [f'engine: {ref} engine tree {want_tree}', f'engine tree as archived: {want_tree}'])

    def test_the_same_files_as_a_folder_have_the_same_tree_as_the_ref_and_no_commit(self):
        commit, tree = self.commit_engine()
        _, by_ref, _ = self.build(ref=commit, out=os.path.join(self.tmp, 'by-ref', 'strength'))
        _, by_folder, _ = self.build(ref=self.engine, out=os.path.join(self.tmp, 'by-folder', 'strength'))
        self.assertEqual(by_ref['engine_tree_archived'], by_folder['engine_tree_archived'])
        self.assertEqual((by_ref['engine_ref'], by_folder['engine_ref']), (commit, None))
        self.assertEqual(by_folder['engine'], f'dir:{self.engine}')
        copy = os.path.join(self.tmp, 'copy of the engine')  # a folder of another name and place, the same files
        shutil.copytree(self.engine, copy)
        _, by_copy, _ = self.build(ref=copy, out=os.path.join(self.tmp, 'by-copy', 'strength'))
        self.assertEqual((by_copy['engine_tree_archived'], by_copy['engine_arg']), (tree, copy), 'the tree is of the files, not of where the folder is')

    def test_other_files_or_an_executable_bit_make_another_tree_and_each_is_the_trees_id_of_those_files(self):
        seen = []
        def step(how):
            commit, tree = self.commit_engine(how)
            _, rec, _ = self.build(ref=self.engine, out=os.path.join(self.tmp, f'out-{len(seen)}', 'strength'))
            self.assertEqual(rec['engine_tree_archived'], tree, how)
            self.assertNotIn(tree, seen, f'{how} is a tree no earlier step had')
            seen.append(tree)
        step('the engine')
        write(os.path.join(self.engine, 'tool.sh'), '#!/bin/sh\n', mode=0o644)
        step('a new file')
        os.chmod(os.path.join(self.engine, 'tool.sh'), 0o755)
        step('the same file, executable')
        write(os.path.join(self.engine, 'tool.sh'), '#!/bin/sh\n# changed\n', mode=0o755)
        step('the executable file, one line more')
        write_bytes(os.path.join(self.engine, 'crlf.txt'), b'a\r\nb\r\n')
        step('a file with CRLF line ends')

    def test_the_tree_is_worked_out_from_the_files_that_were_extracted_not_read_back_from_the_ref(self):
        """A stub tar that changes a file after the real one has extracted the archive: what is compiled is not what the ref says, and the record must say so (its tree is of the
        changed files), while the engine text still names the ref's tree."""
        commit, tree = self.commit_engine()
        real_tar = shutil.which('tar')
        write(os.path.join(self.stub, 'tar'), f'#!/bin/bash\n{shlex.quote(real_tar)} "$@" || exit $?\necho "changed after extraction" >> "$STRENGTH_BUILD_DIR/tree/engine/Cargo.lock"\n', mode=0o755)
        out, rec, printed = self.build(ref=commit)
        with open(os.path.join(self.engine, 'Cargo.lock'), 'a', encoding='utf-8') as f:
            f.write('changed after extraction\n')
        _, changed_tree = self.commit_engine('the engine as compiled')
        self.assertNotEqual(tree, changed_tree)
        self.assertEqual(rec['engine_tree_archived'], changed_tree)
        self.assertEqual(rec['engine'], f'{commit} engine tree {tree}', 'the engine text is the ref\'s; the archived tree is a separate fact')
        self.assertEqual(rec['engine_ref'], commit)

    def test_ignored_files_and_a_machines_git_settings_do_not_change_the_tree(self):
        """The extracted files are added with -f (a .gitignore or a global ignore file must not hide one), with no line-end conversion and with the executable bit as the file
        system has it, whatever the machine's own git configuration says (here: ignore everything, convert CRLF to LF on add, do not trust the file mode)."""
        write(os.path.join(self.engine, '.gitignore'), 'generated.rs\n*.log\n')
        write(os.path.join(self.engine, 'generated.rs'), '// ignored by the engine\'s own .gitignore\n')
        write(os.path.join(self.engine, 'build.log'), 'a log\n')
        write_bytes(os.path.join(self.engine, 'crlf.txt'), b'a\r\nb\r\n')
        write(os.path.join(self.engine, 'tool.sh'), '#!/bin/sh\n', mode=0o755)
        commit, tree = self.commit_engine()
        listed = self.git('ls-tree', '-r', '--name-only', 'HEAD:engine').stdout.split()
        self.assertEqual(sorted(listed), ['.gitignore', 'Cargo.lock', 'build.log', 'crlf.txt', 'generated.rs', 'tool.sh'], 'the reference tree holds the ignored files too')
        ignore_all = os.path.join(self.tmp, 'ignore-everything')
        write(ignore_all, '*\n')
        hostile = dict(GIT_CONFIG_COUNT='3', GIT_CONFIG_KEY_0='core.autocrlf', GIT_CONFIG_VALUE_0='input', GIT_CONFIG_KEY_1='core.fileMode', GIT_CONFIG_VALUE_1='false',
                       GIT_CONFIG_KEY_2='core.excludesFile', GIT_CONFIG_VALUE_2=ignore_all)
        for ref in (commit, self.engine):
            with self.subTest(ref='a folder' if ref == self.engine else 'a ref'):
                out, rec, printed = self.build(ref=ref, out=os.path.join(self.tmp, 'out-' + ('f' if ref == self.engine else 'r'), 'strength'), **hostile)
                self.assertEqual(rec['engine_tree_archived'], tree)

    GIT_VARIABLES = ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES', 'GIT_COMMON_DIR', 'GIT_NAMESPACE', 'GIT_PREFIX')

    def another_repository(self):
        """A second repository (the one a hook's exported GIT_DIR would name) whose HEAD, main and engine/ are other things than this world's; returns (folder, its engine tree)."""
        other = os.path.join(self.tmp, 'other-repo')
        write(os.path.join(other, 'engine', 'Cargo.lock'), "# another repository's engine\n")
        base = ['git', '-C', other, '-c', 'user.name=t', '-c', 'user.email=t@t', '-c', 'commit.gpgsign=false']
        subprocess.run(base + ['init', '-q'], check=True, capture_output=True, env=self.env())
        subprocess.run(base + ['symbolic-ref', 'HEAD', 'refs/heads/main'], check=True, capture_output=True, env=self.env())
        subprocess.run(base + ['add', '-A', '-f', 'engine'], check=True, capture_output=True, env=self.env())
        subprocess.run(base + ['commit', '-q', '-m', 'the other engine'], check=True, capture_output=True, env=self.env())
        return other, subprocess.run(base + ['rev-parse', 'HEAD:engine'], check=True, capture_output=True, text=True, env=self.env()).stdout.strip()

    def test_git_variables_exported_to_another_repository_do_not_change_what_build_sh_archives_or_the_tree_it_records(self):
        """A git hook (or `rebase --exec`) exports GIT_DIR and its relatives: with them set the script's `git -C REPO archive REF` would read THAT repository (HEAD and main are other
        commits there), and the scratch repository that computes the archived tree would be pointed at it. The script removes them before its first git read."""
        commit, tree = self.commit_engine()
        other, other_tree = self.another_repository()
        self.assertNotEqual(tree, other_tree)
        plain_out, plain, _ = self.build(ref='HEAD', out=os.path.join(self.tmp, 'plain', 'strength'))
        self.assertEqual((plain['engine_ref'], plain['engine_tree_archived'], plain['engine']), (commit, tree, f'HEAD engine tree {tree}'))

        def same_but_for_the_time_and_the_path(rec, out):
            return {k: (v.replace(out, 'OUT') if isinstance(v, str) else v) for k, v in rec.items() if k != 'built_at'}
        pointing = {'GIT_DIR': os.path.join(other, '.git'), 'GIT_WORK_TREE': other, 'GIT_INDEX_FILE': os.path.join(other, '.git', 'index'), 'GIT_COMMON_DIR': os.path.join(other, '.git'),
                    'GIT_OBJECT_DIRECTORY': os.path.join(other, '.git', 'objects'), 'GIT_ALTERNATE_OBJECT_DIRECTORIES': os.path.join(other, '.git', 'objects'), 'GIT_NAMESPACE': 'someone-elses',
                    'GIT_PREFIX': 'engine/'}
        self.assertEqual(sorted(pointing), sorted(self.GIT_VARIABLES), 'all eight')
        for n, (name, value) in enumerate(list(pointing.items()) + [('all of them', None)]):
            with self.subTest(exported=name):
                out, rec, printed = self.build(ref='HEAD', out=os.path.join(self.tmp, f'pointing-{n}', 'strength'), **(pointing if value is None else {name: value}))
                self.assertEqual(same_but_for_the_time_and_the_path(rec, out), same_but_for_the_time_and_the_path(plain, plain_out), "the same record as without them: the archive is of REPO's HEAD")
                self.assertEqual(printed[:2], [f'engine: HEAD engine tree {tree}', f'engine tree as archived: {tree}'])

    def test_none_of_the_git_variables_reaches_any_git_build_sh_runs(self):
        """Whatever the effect of each one, the script's git calls (the archive, the commit and tree ids, the scratch repository) run without all eight."""
        log = os.path.join(self.tmp, 'git-variables.log')
        calls = log + '.calls'
        commit, tree = self.commit_engine()
        other, _ = self.another_repository()
        pointing = {name: os.path.join(other, '.git') for name in self.GIT_VARIABLES}
        real_git = shutil.which('git')
        self.write_stub('git', f'for v in {" ".join(self.GIT_VARIABLES)}; do if [ -n "${{!v+x}}" ]; then echo "$v" >> "$STUB_GIT_LOG"; fi; done\n'
                               f'echo "$*" >> "$STUB_GIT_LOG.calls"\nexec {shlex.quote(real_git)} "$@"\n')  # (the stub is first on the PATH from here on: no git of this test after it)
        control = subprocess.run([os.path.join(self.stub, 'git'), '--version'], capture_output=True, text=True, env=dict(os.environ, STUB_GIT_LOG=log, **pointing))
        self.assertEqual(control.returncode, 0, control.stderr)
        self.assertEqual(read(log).split(), list(self.GIT_VARIABLES), 'the stub does report every one of the eight when it is given them')
        os.remove(log)
        os.remove(calls)
        out, rec, _ = self.build(ref=commit, STUB_GIT_LOG=log, **pointing)
        self.assertGreaterEqual(len(read(calls).splitlines()), 5, 'the script ran git several times (archive, rev-parse, init, add, write-tree)')
        self.assertFalse(os.path.exists(log), 'and none of the eight was in the environment of any of those calls: ' + (read(log) if os.path.exists(log) else ''))
        self.assertEqual((rec['engine_ref'], rec['engine_tree_archived']), (commit, tree))

    def test_the_rebuild_command_repeats_the_build_and_names_every_value_the_build_depended_on(self):
        commit, tree = self.commit_engine()
        dirs = {n: os.path.join(self.tmp, f"it's a {n} dir") for n in ('build', 'target', 'cargo')}  # a space and an apostrophe: the command has to quote them
        out = os.path.join(self.tmp, 'out dir', 'strength')
        _, rec, _ = self.build(ref=commit, out=out, STRENGTH_BUILD_DIR=dirs['build'], STRENGTH_TARGET_DIR=dirs['target'], CARGO_HOME=dirs['cargo'], STRENGTH_JOBS='2')
        words = shlex.split(rec['rebuild_command'])
        at = words.index('bash')
        assignments = [w.split('=', 1) for w in words[1:at]]
        self.assertEqual(words[0], 'env')
        self.assertEqual([k for k, _ in assignments], list(REBUILD_ENV), 'the same names, in this order')
        self.assertEqual(dict(assignments), {'HOME': os.path.join(self.tmp, 'home'), 'CARGO_HOME': dirs['cargo'], 'STRENGTH_BUILD_DIR': dirs['build'], 'STRENGTH_TARGET_DIR': dirs['target'],
                                             'STRENGTH_JOBS': '2', 'STRENGTH_REPO': self.tmp})
        self.assertEqual(words[at:], ['bash', os.path.join(self.tmp, 'rl', 'strength', 'build.sh'), commit, out], 'then the script, the ref as given and the output path')
        # repeated from nowhere in particular, with none of the variables set, it makes the same program and the same record (the time apart)
        first_program = read_bytes(out)
        os.remove(out)
        os.remove(out + '.build.json')
        env = self.env(STRENGTH_BUILD_DIR=None, HOME='/nonexistent-home')
        r = subprocess.run(words, capture_output=True, text=True, env=env, cwd='/')
        self.assertEqual(r.returncode, 0, r.stderr)
        again = json.loads(read(out + '.build.json'))
        self.assertEqual(read_bytes(out), first_program)
        self.assertEqual({k: v for k, v in again.items() if k != 'built_at'}, {k: v for k, v in rec.items() if k != 'built_at'}, 'the same record, the time apart')

    def test_the_rebuild_command_quotes_a_ref_that_is_a_folder_with_odd_characters(self):
        folder = os.path.join(self.tmp, "it's an engine; (copy) $HOME")
        shutil.copytree(self.engine, folder)
        out = os.path.join(self.tmp, 'out', 'strength')
        _, rec, _ = self.build(ref=folder, out=out)
        words = shlex.split(rec['rebuild_command'])
        self.assertEqual(words[-2:], [folder, out], 'the ref as given, one word')
        os.remove(out)
        os.remove(out + '.build.json')
        r = subprocess.run(words, capture_output=True, text=True, env=self.env(STRENGTH_BUILD_DIR=None), cwd='/')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(read(out + '.build.json'))['engine_arg'], folder)

    def test_the_record_for_a_cargo_home_that_is_not_set_is_repeated_with_the_default_one(self):
        out, rec, _ = self.build()
        words = shlex.split(rec['rebuild_command'])
        self.assertIsNone(rec['cargo_home'])
        self.assertEqual(dict(w.split('=', 1) for w in words[1:words.index('bash')])['CARGO_HOME'], os.path.join(self.tmp, 'home', '.cargo'))

    def test_a_ref_that_is_not_there_makes_no_program_and_no_record(self):
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        self.commit_engine()
        r = self.run_build(out, ref='no-such-ref')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(out) or os.path.exists(out + '.build.json'))
        self.assertFalse(os.path.exists(self.log), 'cargo was not called')

    def test_a_first_build_that_fails_makes_no_program_and_no_record(self):
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        r = self.run_build(out, STUB_CARGO_FAILS='1')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(out) or os.path.exists(out + '.build.json'))

    def test_a_failed_cargo_build_is_not_passed_off_with_the_program_of_an_earlier_build(self):
        """The target folder keeps the program an earlier build left there. After a build that fails (an offline build that lacks a crate, a source error) that old program must not
        be copied out with a record that says it was built from the new engine tree and harness: a program that is not the pinned source, with a record that says it is. (Until
        build.sh kept cargo's exit status this test was red; it is the first of the tests of what a failed build leaves behind.)"""
        commit1, tree1 = self.commit_engine()
        self.build(ref=commit1, out=os.path.join(self.tmp, 'first', 'strength'), STUB_PROGRAM_TEXT='the program of the first engine')
        write(os.path.join(self.engine, 'Cargo.lock'), '# the engine this build is about\n')
        commit2, tree2 = self.commit_engine('another engine')
        out = os.path.join(self.tmp, 'second', 'strength')
        r = self.run_build(out, ref=commit2, STUB_CARGO_FAILS='1')
        self.assertNotEqual(r.returncode, 0, 'a build that did not compile is not a build')
        self.assertFalse(os.path.exists(out), 'and no program is left')
        self.assertFalse(os.path.exists(out + '.build.json'), 'and no record that claims one')

    # a stub cargo that complains the way cargo does: lines the script's filter keeps (error..., --> ..., | ..., warning: unused...) among lines it drops, one of them on stderr
    COMPLAINTS = ['   Compiling strength v0.1.0', 'error[E0425]: cannot find value `x` in this scope', ' --> src/main.rs:3:5', '  |', '3 |     x', '  |     ^ not found',
                  'warning: unused variable: `y`', 'note: some other line', 'warning: function is never used']
    KEPT_COMPLAINTS = ['error[E0425]: cannot find value `x` in this scope', ' --> src/main.rs:3:5', '  |', '  |     ^ not found', 'warning: unused variable: `y`', 'error: and one on stderr']

    def complaining_cargo(self, then):
        lines = ' '.join(shlex.quote(l) for l in self.COMPLAINTS)
        self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + f'printf "%s\\n" {lines}\necho "error: and one on stderr" >&2\n' + then)

    def test_a_cargo_that_fails_stops_the_script_with_exit_1_and_says_so_and_leaves_no_program_and_no_record_and_the_older_ones_are_as_they_were(self):
        for how, own_target in (('the default target folder', False), ('a target folder of its own', True)):
            with self.subTest(target=how):
                self.make_fresh_build_world()
                target = os.path.join(self.tmp, 'their', 'target') if own_target else None
                env = {} if target is None else dict(STRENGTH_TARGET_DIR=target)
                stale = os.path.join(target or os.path.join(self.tmp, 'build', 'target'), 'release', 'strength')
                commit1, tree1 = self.commit_engine()
                out = os.path.join(self.tmp, 'elsewhere', 'strength')
                self.build(ref=commit1, out=out, STUB_PROGRAM_TEXT='the program of the first build', **env)
                self.assertTrue(os.path.isfile(stale), 'the first build left its program in the target folder')
                before = {p: (read_bytes(p), os.stat(p).st_mtime_ns) for p in (out, out + '.build.json')}
                write(os.path.join(self.engine, 'Cargo.lock'), '# a changed engine\n')
                commit2, tree2 = self.commit_engine('changed')
                self.complaining_cargo('exit 101\n')
                r = self.run_build(out, ref=commit2, **env)
                log = os.path.join(self.tmp, 'build', 'cargo.log')
                self.assertEqual(r.returncode, 1, "build.sh's own status for a failed build, not cargo's 101")
                self.assertEqual(r.stdout.splitlines(), self.KEPT_COMPLAINTS, 'the lines of cargo that matter, as before')
                self.assertEqual(r.stderr, f'build.sh: cargo build failed (its whole output is in {log}); no program was copied and no build record was written\n')
                self.assertEqual(read(log).splitlines(), self.COMPLAINTS + ['error: and one on stderr'], "the whole of cargo's output, both streams, is in the log")
                self.assertFalse(os.path.exists(stale), 'the program of the earlier build was taken out of the target folder before this one began')
                self.assertEqual({p: (read_bytes(p), os.stat(p).st_mtime_ns) for p in before}, before, 'the older program and its record are as they were')
                self.assertEqual(sorted(os.listdir(os.path.dirname(out))), ['strength', 'strength.build.json'])

    def make_fresh_build_world(self):
        """A new temporary folder for the next case of a test that tries several (the stub tools and the pin are laid out again)."""
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.setUp()

    def test_a_cargo_that_succeeds_and_leaves_no_program_is_a_failed_build_and_an_earlier_program_is_not_taken_for_it(self):
        for how, own_target in (('the default target folder', False), ('a target folder of its own', True)):
            with self.subTest(target=how):
                self.make_fresh_build_world()
                target = os.path.join(self.tmp, 'their', 'target') if own_target else None
                env = {} if target is None else dict(STRENGTH_TARGET_DIR=target)
                stale = os.path.join(target or os.path.join(self.tmp, 'build', 'target'), 'release', 'strength')
                self.build(out=os.path.join(self.tmp, 'first', 'strength'), STUB_PROGRAM_TEXT='the program of the first build', **env)
                self.assertTrue(os.path.isfile(stale))
                self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + 'exit 0\n')
                out = os.path.join(self.tmp, 'second', 'strength')
                r = self.run_build(out, **env)
                self.assertNotEqual(r.returncode, 0, 'no program, no build')
                self.assertEqual(r.stdout, '', 'and none of the lines that say there is one')
                self.assertFalse(os.path.exists(out) or os.path.exists(out + '.build.json'), 'the earlier build\'s program was not copied as this build\'s')
                self.assertFalse(os.path.exists(stale))

    def test_what_cargo_complained_about_is_printed_before_the_six_lines_when_it_builds_too(self):
        self.complaining_cargo(self.CARGO_BUILDS)
        out = os.path.join(self.tmp, 'elsewhere', 'strength')
        r = self.run_build(out)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[:len(self.KEPT_COMPLAINTS)], self.KEPT_COMPLAINTS)
        self.assertEqual([l.split(':')[0] for l in lines[len(self.KEPT_COMPLAINTS):]], ['engine', 'engine tree as archived', 'program', 'program sha256', 'harness source sha256', 'build record'])
        self.assertEqual(r.stderr, '')
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)

    def test_at_most_60_lines_of_cargos_complaints_are_printed_and_a_huge_output_does_not_end_the_script_early(self):
        """The filter is `grep ... | head -60`: with a long output grep is stopped by a broken pipe, which must not be taken for a failure of the script (pipefail)."""
        many = 'i=0; while [ $i -lt 20000 ]; do echo "error: complaint number $i of a very long list, padded so that the whole output is much bigger than a pipe holds"; i=$((i+1)); done\n'
        want = [f'error: complaint number {i} of a very long list, padded so that the whole output is much bigger than a pipe holds' for i in range(60)]
        for how, tail, code in (('a build that fails', 'exit 101\n', 1), ('a build that works', self.CARGO_BUILDS, 0)):
            with self.subTest(cargo=how):
                self.write_stub('cargo', self.CARGO_V + self.CARGO_NOTES + many + tail)
                out = os.path.join(self.tmp, f'elsewhere-{code}', 'strength')
                r = self.run_build(out)
                self.assertEqual(r.returncode, code, r.stderr)
                self.assertEqual([l for l in r.stdout.splitlines() if l.startswith('error: complaint')], want, 'sixty lines, the first sixty')
                if code:
                    self.assertTrue(r.stderr.startswith('build.sh: cargo build failed (its whole output is in '), r.stderr)
                else:
                    self.assertIn(f'build record: {out}.build.json', r.stdout.splitlines())

    # ------------------------------------------------------------------------------------------------------ what changes what cargo builds is taken out of its environment
    SCRUBBED = {'RUSTFLAGS': '-C target-cpu=native', 'RUSTDOCFLAGS': '', 'RUSTC': '/somewhere/rustc', 'RUSTC_WRAPPER': 'sccache', 'RUSTC_BOOTSTRAP': '1', 'RUSTUP_TOOLCHAIN': 'nightly',
                'CARGO_BUILD_TARGET': 'x86_64-unknown-linux-musl', 'CARGO_BUILD_RUSTFLAGS': '-C opt-level=0', 'CARGO_ENCODED_RUSTFLAGS': '-Ccodegen-units=1',
                'CARGO_PROFILE_RELEASE_OPT_LEVEL': '0', 'CARGO_PROFILE_RELEASE_LTO': 'off', 'CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER': '/somewhere/ld', 'CARGO_INCREMENTAL': '1',
                'CARGO_UNSTABLE_BUILD_STD': 'true', 'CARGO_PATCH_CRATES_IO': 'x'}
    # names that look like them and stay: they change nothing about the program (or are cargo's own folders), or are the two the script sets itself
    KEPT = {'RUSTUP_HOME': '/their/rustup', 'CARGO_NET_OFFLINE': 'true', 'RUSTFLAGS_EXTRA': 'keep', 'MY_RUSTFLAGS': 'keep', 'CARGO_PROFILE': 'keep', 'CARGO_REGISTRY_TOKEN': 'keep',
            'CARGO_BUILD_JOBS': '99', 'CARGO_TARGET_DIR': '/their/target'}

    def env_logging_tools(self):
        """A stub cargo and rustc that write every call, with the whole environment it was made in, to $STUB_ENVLOG; returns that file's path."""
        self.write_stub('cargo', '{ echo "== cargo $*"; env; } >> "$STUB_ENVLOG"\n' + self.CARGO_V + self.CARGO_NOTES + self.CARGO_BUILDS)
        self.write_stub('rustc', '{ echo "== rustc $*"; env; } >> "$STUB_ENVLOG"\nif [ "$1" = "-vV" ]; then echo "$STUB_RUSTC_VV"; fi\n')
        return os.path.join(self.tmp, 'env.log')

    @staticmethod
    def env_calls(log):
        """{call: {name: value}} from the file the logging stubs write: one block per call, introduced by '== <tool> <arguments>'."""
        calls, current = {}, None
        for line in read(log).splitlines():
            if line.startswith('== '):
                current = calls[line[3:]] = {}
            elif current is not None and '=' in line:
                name, value = line.split('=', 1)
                current[name] = value
        return calls

    def test_the_variables_that_change_what_cargo_builds_are_not_in_the_environment_of_cargo_or_of_the_two_version_commands_and_the_record_lists_them(self):
        log = self.env_logging_tools()
        cargo_home, target = os.path.join(self.tmp, 'cargo-home'), os.path.join(self.tmp, 'target-dir')
        out, rec, printed = self.build(ref=self.engine, out=os.path.join(self.tmp, 'elsewhere', 'strength'), STUB_ENVLOG=log, CARGO_HOME=cargo_home, STRENGTH_TARGET_DIR=target,
                                       **self.SCRUBBED, **self.KEPT)
        calls = self.env_calls(log)
        self.assertEqual(sorted(calls), ['cargo -V', 'cargo build --release --offline', 'rustc -vV'], "the build, and the two commands the record's toolchain lines come from")
        for call, seen in calls.items():
            for name in self.SCRUBBED:
                self.assertNotIn(name, seen, f'{name} reached `{call}`')
            self.assertEqual((seen['HOME'], seen['CARGO_HOME']), (os.path.join(self.tmp, 'home'), cargo_home), f'HOME and CARGO_HOME are as they were for `{call}`')
            for name in ('RUSTUP_HOME', 'CARGO_NET_OFFLINE', 'RUSTFLAGS_EXTRA', 'MY_RUSTFLAGS', 'CARGO_PROFILE', 'CARGO_REGISTRY_TOKEN'):
                self.assertEqual(seen.get(name), self.KEPT[name], f'{name} is not one of the variables that change the build, so `{call}` still sees it')
        build, version_commands = calls['cargo build --release --offline'], [calls['cargo -V'], calls['rustc -vV']]
        self.assertEqual((build['CARGO_TARGET_DIR'], build['CARGO_BUILD_JOBS']), (target, '8'), "what the script sets for cargo itself (the machine's own values do not reach the build)")
        for seen in version_commands:
            self.assertEqual((seen['CARGO_TARGET_DIR'], seen['CARGO_BUILD_JOBS']), ('/their/target', '99'), 'those two are not removed: the version commands see them as they were')
        self.assertEqual(rec['build_env_unset'], sorted(self.SCRUBBED), 'the record lists the names that were removed, sorted')
        self.assertNotIn('CARGO_TARGET_DIR', rec['build_env_unset'])
        self.assertNotIn('CARGO_BUILD_JOBS', rec['build_env_unset'])
        said = [l for l in self.last_stderr.splitlines()]
        self.assertEqual(len(said), 1, self.last_stderr)
        prefix = 'build.sh: removed from the build environment (they change what cargo builds): '
        self.assertTrue(said[0].startswith(prefix), said[0])
        self.assertEqual(sorted(said[0][len(prefix):].split()), sorted(self.SCRUBBED), 'the same names, each once')
        for value in ('native', 'sccache', 'nightly', 'musl'):
            self.assertNotIn(value, rec['rebuild_command'], 'the removed values are not baked into the rebuild command: the script removes them again wherever it runs')

    def test_a_build_with_none_of_them_set_says_nothing_and_lists_nothing(self):
        r = self.run_build(os.path.join(self.tmp, 'elsewhere', 'strength'), RUSTFLAGS_EXTRA='x', CARGO_NET_OFFLINE='true', CARGO_TARGET_DIR='/their/target', CARGO_BUILD_JOBS='99')
        self.assertEqual((r.returncode, r.stderr), (0, ''))
        self.assertEqual(json.loads(read(os.path.join(self.tmp, 'elsewhere', 'strength.build.json')))['build_env_unset'], [])

    def test_every_variable_the_readme_names_as_removed_is_removed_from_cargos_environment(self):
        sentence = re.search(r"takes the variables that change what cargo builds out of cargo's environment \(([^)]*)\)", cloud_section())
        self.assertTrue(sentence, 'the README says which variables build.sh takes out of the environment')
        named = re.findall(r'`([A-Z_]+\*?)`', sentence.group(1))
        self.assertGreaterEqual(len(named), 4, named)
        concrete = {name: (name[:-1] + 'RELEASE_LTO' if name.endswith('*') else name) for name in named}
        log = self.env_logging_tools()
        out, rec, _ = self.build(STUB_ENVLOG=log, **{v: 'x' for v in concrete.values()})
        for call, seen in self.env_calls(log).items():
            for name in named:
                self.assertNotIn(concrete[name], seen, f'the README says {name} is removed; it reached `{call}`')
        self.assertEqual(rec['build_env_unset'], sorted(concrete.values()))
        header = read(os.path.join(HERE, 'build.sh')).split('set -euo pipefail')[0]
        for name in ('RUSTFLAGS', 'CARGO_PROFILE_*', 'RUSTC_WRAPPER'):
            self.assertIn(name, named, 'the README names it')
            self.assertIn(name, header, f'and build.sh says in its own header that {name} is removed')

    # ------------------------------------------------------------------------------------------------------ the cargo config files that still apply
    def digest(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def listed_here(self, rec):
        """The record's cargo config files that are inside the temporary folder (a machine may have others above it), as (path, sha256)."""
        return [(c['path'], c['sha256']) for c in rec['cargo_config_files'] if c['path'].startswith(self.tmp + os.sep)]

    def test_the_cargo_config_files_that_still_apply_are_listed_with_their_sha256_innermost_folder_first_then_cargo_home(self):
        cargo_home = os.path.join(self.tmp, 'cargo-home')
        files = [(os.path.join(self.tmp, 'build', '.cargo', 'config.toml'), '[build]\njobs = 1\n'), (os.path.join(self.tmp, 'build', '.cargo', 'config'), '# the old name\n'),
                 (os.path.join(self.tmp, '.cargo', 'config.toml'), '[net]\noffline = true\n'), (os.path.join(cargo_home, 'config.toml'), '[term]\nverbose = true\n'),
                 (os.path.join(cargo_home, 'config'), '# the old name, in cargo home\n')]
        for path, text in files:
            write(path, text)
        os.makedirs(os.path.join(self.tmp, '.cargo', 'config'))  # a folder with a config's name is no config file
        write(os.path.join(self.tmp, 'not-an-ancestor', '.cargo', 'config.toml'), '# beside the build, not above it\n')
        out, rec, _ = self.build(CARGO_HOME=cargo_home)
        self.assertEqual(self.listed_here(rec), [(p, self.digest(t)) for p, t in files], 'the build folder (both names), the folder above it, then cargo home (both names); nothing else')
        for entry in rec['cargo_config_files']:
            self.assertEqual(sorted(entry), ['path', 'sha256'])
            self.assertEqual(entry['sha256'], hashlib.sha256(read_bytes(entry['path'])).hexdigest())

    def test_a_config_file_found_twice_is_listed_once_and_the_default_cargo_home_is_home_slash_dot_cargo(self):
        write(os.path.join(self.tmp, '.cargo', 'config.toml'), '[net]\noffline = true\n')
        alias = os.path.join(self.tmp, 'cargo-alias')
        os.symlink(os.path.join(self.tmp, '.cargo'), alias)
        for how, home_env in (('cargo home is the folder above the build', os.path.join(self.tmp, '.cargo')), ('cargo home is a link to it', alias)):
            with self.subTest(cargo_home=how):
                out, rec, _ = self.build(CARGO_HOME=home_env, out=os.path.join(self.tmp, f'out-{os.path.basename(home_env)}', 'strength'))
                self.assertEqual(self.listed_here(rec), [(os.path.join(self.tmp, '.cargo', 'config.toml'), self.digest('[net]\noffline = true\n'))], 'one file, listed once under the first spelling')
        write(os.path.join(self.tmp, 'home', '.cargo', 'config.toml'), '[term]\nquiet = true\n')
        out, rec, _ = self.build(out=os.path.join(self.tmp, 'out-default', 'strength'))
        self.assertEqual(self.listed_here(rec), [(os.path.join(self.tmp, '.cargo', 'config.toml'), self.digest('[net]\noffline = true\n')),
                                                 (os.path.join(self.tmp, 'home', '.cargo', 'config.toml'), self.digest('[term]\nquiet = true\n'))],
                         'with CARGO_HOME unset, cargo reads $HOME/.cargo')

    def test_without_any_cargo_config_file_the_list_is_empty_in_this_world(self):
        out, rec, _ = self.build()
        self.assertIsInstance(rec['cargo_config_files'], list)
        self.assertEqual(self.listed_here(rec), [])

    def test_a_cargo_config_file_that_cannot_be_read_is_listed_with_the_error_and_no_sha256_and_the_record_is_still_written(self):
        """A file cargo may not be able to read either: the record says so (path, sha256 null, the error) instead of the script ending in a traceback after the build, with no record."""
        readable, locked = os.path.join(self.tmp, 'build', '.cargo', 'config.toml'), os.path.join(self.tmp, 'cargo-home', 'config.toml')
        write(readable, '[build]\njobs = 1\n')
        write(locked, '[term]\nverbose = true\n')
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, 0o644)
        try:
            open(locked, 'rb').close()
        except OSError:
            pass
        else:
            self.skipTest('this user can read a file whose mode is 000 (root, or a file system that ignores modes), so a cargo config file cannot be made unreadable here')
        out, rec, _ = self.build(CARGO_HOME=os.path.join(self.tmp, 'cargo-home'))
        self.assertEqual(self.last_stderr, '', 'no traceback, no complaint')
        listed = [c for c in rec['cargo_config_files'] if c['path'].startswith(self.tmp + os.sep)]
        self.assertEqual([c['path'] for c in listed], [readable, locked], 'both are listed, in the usual order')
        self.assertEqual(listed[0], {'path': readable, 'sha256': self.digest('[build]\njobs = 1\n')}, 'the readable one as before')
        self.assertEqual(sorted(listed[1]), ['error', 'path', 'sha256'])
        self.assertIsNone(listed[1]['sha256'])
        self.assertIsInstance(listed[1]['error'], str)
        self.assertIn(locked, listed[1]['error'], 'the error names the file')
        self.assertEqual(read_bytes(out), self.STUB_PROGRAM)
        self.assertEqual(rec['program_sha256'], sha(out), 'and the program and its record are there')
        os.chmod(locked, 0o644)
        out2, rec2, _ = self.build(CARGO_HOME=os.path.join(self.tmp, 'cargo-home'), out=os.path.join(self.tmp, 'again', 'strength'))
        self.assertEqual([c for c in rec2['cargo_config_files'] if c['path'] == locked], [{'path': locked, 'sha256': self.digest('[term]\nverbose = true\n')}], 'readable again: the usual entry')

    # ------------------------------------------------------------------------------------------------------ git archive converts nothing
    def test_a_machines_line_end_settings_do_not_change_what_git_archive_extracts_and_so_not_the_tree(self):
        """With core.autocrlf=true (a Windows habit) in the user's ~/.gitconfig, or core.eol=crlf with a file marked text, git archive writes CRLF into the files it extracts: what is
        compiled would not be the ref's files, and the record's tree (computed from the extracted files) would be another one than `git rev-parse REF:engine` on every machine
        that has such a setting. The archive is made with those settings overridden."""
        write(os.path.join(self.engine, 'Cargo.lock'), '# the engine\n# two lines\n')
        write(os.path.join(self.engine, 'src', 'lib.rs'), 'fn main() {\n}\n')
        write(os.path.join(self.engine, '.gitattributes'), '*.rs text\n')
        commit, tree = self.commit_engine()
        committed = {n: self.git('cat-file', 'blob', f'HEAD:engine/{n}').stdout for n in ('Cargo.lock', 'src/lib.rs')}
        self.assertTrue(all('\r' not in t for t in committed.values()), 'the files in the commit have LF line ends')
        for how, config in (('core.autocrlf=true', '[core]\n\tautocrlf = true\n'), ('core.eol=crlf for files marked text', '[core]\n\teol = crlf\n'),
                            ('both', '[core]\n\tautocrlf = true\n\teol = crlf\n')):
            with self.subTest(gitconfig=how):
                write(os.path.join(self.tmp, 'home', '.gitconfig'), config)
                out, rec, printed = self.build(ref=commit, out=os.path.join(self.tmp, 'out-' + how.split('=')[0].replace(' ', '-'), 'strength'), GIT_CONFIG_GLOBAL=None)
                self.assertEqual(rec['engine_tree_archived'], tree, 'the tree of the files compiled is the ref\'s tree')
                self.assertEqual(rec['engine'], f'{commit} engine tree {tree}')
                extracted = os.path.join(self.tmp, 'build', 'tree', 'engine')
                for name, text in committed.items():
                    self.assertEqual(read_bytes(os.path.join(extracted, name)), text.encode(), f'{name} as extracted is the committed file, byte for byte')


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

    @staticmethod
    def slow_report_commands(section):
        """The arguments (after `python3 rl/strength/slow_report.py`) of every command in backticks in the section that runs the slow report, as the section writes them: a
        leading `nohup`, a redirection (`> register.log 2>&1`) and a trailing `&` belong to the shell and are not the script's."""
        found = []
        for span in re.findall(r'`([^`]+)`', section):
            if 'rl/strength/slow_report.py ' not in span:
                continue
            words = shlex.split(span)
            if words[:1] == ['nohup']:
                words = words[1:]
            assert words[:2] == ['python3', 'rl/strength/slow_report.py'], words
            args = words[2:]
            cut = next((i for i, w in enumerate(args) if w == '&' or re.match(r'^\d*>', w)), len(args))
            found.append(args[:cut])
        return found

    def test_every_slow_report_command_in_the_section_is_accepted_by_the_parser(self):
        commands = self.slow_report_commands(self.section())
        self.assertTrue(commands, 'the section gives the registration command')
        with tempfile.TemporaryDirectory() as t:
            for command in commands:
                with self.subTest(command=command):
                    argv = [w.replace('$HOME', t).replace('DECKFILE', os.path.join(t, 'deck.txt')) for w in command]
                    r = self.script(*argv, '--pin', os.path.join(t, 'no-such-pin.json'))
                    self.assertNotIn('unrecognized arguments', r.stderr)
                    self.assertNotIn('usage:', r.stderr)
                    self.assertIn('cannot read the pin', r.stderr, 'the parser accepted every word and the script went on to read the pin')

    def test_the_registration_is_given_in_the_nohup_form_with_register_only_and_a_log_to_follow(self):
        """The replay of the kx3 self-check takes hours, so the registration is started under nohup, in the background, with its output in a file that `tail -f` follows."""
        section = self.section()
        spans = [s for s in re.findall(r'`([^`]+)`', section) if '--register-only' in s]
        self.assertEqual(len(spans), 1, 'one registration command')
        self.assertTrue(spans[0].startswith('nohup python3 rl/strength/slow_report.py DECKFILE '), spans[0])
        self.assertTrue(spans[0].endswith(' > register.log 2>&1 &'), spans[0])
        self.assertIn('tail -f register.log', section)
        args = self.slow_report_commands(section)[0]
        for flag in ('--program', '--deals', '--threads', '--school-rule', '--register-only'):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index('--school-rule') + 1], 'off')
        self.assertEqual(args[:1], ['DECKFILE'])

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

    def test_build_sh_takes_the_ref_then_the_output_path_and_prints_the_values_the_section_checks(self):
        """Step 1 builds with `build.sh <ref> <out>` (offline) and compares the engine tree as archived, the program sha256 and the harness source hash it prints."""
        section, build = self.section(), read(os.path.join(HERE, 'build.sh'))
        self.assertIn('cargo --offline', section)
        self.assertIn('cargo build --release --offline', build)
        self.assertIn('REF=${1:-origin/main}', build)
        self.assertIn('OUT=${2:-', build)
        self.assertIn('ENGINE_ID="$REF engine tree $(git -C "$REPO" rev-parse "$REF:engine")"', build, 'for a git ref it prints the engine tree of the ref')
        for printed in ('echo "engine: $ENGINE_ID"', 'echo "engine tree as archived: $ENGINE_TREE_ARCHIVED"', 'echo "program sha256: $PROGRAM_SHA"', 'echo "harness source sha256: $HARNESS_SHA"'):
            self.assertIn(printed, build)
        self.assertIn('engine tree **as archived**', section, 'the section says which of the printed trees is the one to compare')

    SLICE_MESSAGE = 'stopped after --max-games N (games across both arms, about half of them kx3 games); resume with: <command>'

    def test_the_section_quotes_the_message_a_slice_ends_with(self):
        section = self.section()
        self.assertIn(f'prints "{self.SLICE_MESSAGE}"', section, 'the whole message, the count explained (the behaviour test below prints the real one)')
        self.assertNotIn('stopped after --max-games N; resume with', section, 'the short form it replaced is gone')

    def test_the_section_says_the_pin_must_be_the_committed_one_and_names_the_test_only_variable_the_code_checks(self):
        section, code = self.section(), read(os.path.join(HERE, 'slow_report.py'))
        for phrase in ('must be the committed one', 'byte-equal', '`rl/strength/slow_report_pin.json` committed at HEAD', 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN', '"bypassed"', 'pin committed: yes'):
            self.assertIn(phrase, section)
        self.assertEqual(sr.ALLOW_UNCOMMITTED_PIN, 'SLOW_REPORT_ALLOW_UNCOMMITTED_PIN', 'the variable the README names is the one the code reads')
        self.assertIn('test-only', section)
        self.assertIn('ALLOW_UNCOMMITTED_PIN', code)

    def test_the_section_describes_the_build_record_and_the_rebuild_command_build_sh_writes(self):
        env, ref, out = readme_build_command()
        section, build = self.section(), read(os.path.join(HERE, 'build.sh'))
        self.assertIn(f'`{os.path.basename(out)}.build.json`', section, 'the record sits beside the program, named for it')
        self.assertIn('OUT_BINARY.build.json', build.split('set -euo pipefail')[0], 'build.sh says so in its own header')
        for phrase in ('rebuild_command', '`rustc -vV`', '`cargo -V`', 'engine tree **as archived**', 'not from the checkout', 'registered `rebuild_command`'):
            self.assertIn(phrase, section)
        self.assertIn('rebuild_command=', build, 'the field the section names is one build.sh writes')

    def test_the_section_states_the_rule_for_a_program_that_changed_on_a_resume_and_the_code_logs_that_event_and_shows_it_on_the_page(self):
        section, code = self.section(), read(os.path.join(HERE, 'slow_report.py'))
        for phrase in ('`program_changed`', 'The program changed mid-run', 'registered on the rebuilt route', 'same engine tree as archived', 'same harness hash', 'replayed again',
                       'equal the committed pin', 'Anything else is refused, naming both sha256 values'):
            self.assertIn(phrase, section)
        self.assertIn("'program_changed'", code, 'the event the section names is the one the wrapper logs')
        self.assertIn('The program changed mid-run', code, 'and the words the page shows')

    def test_the_rules_the_section_gives_for_a_changed_program_are_the_ones_the_code_states(self):
        """Each sentence of step 5 about a program that changed on a resume is tied to the words of the code that carries it out (the behaviour is tested with the resume, in
        test_slow_report.py); a README that promises more than the code says, or the other way round, fails here."""
        section, code = self.section(), read(os.path.join(HERE, 'slow_report.py'))
        ties = (('only if the pin in use is the pin the run was registered under (same engine tree, harness hash, engine ref and self-check texts)',
                 ['the pin in use is not the pin this run was registered under', "for key in ('engine_tree', 'harness_source_sha256', 'engine_ref')"]),
                ('and is the committed one', ['st = require_committed_pin(repo, pin_path)']),
                ("the new program's build record has the same engine tree as archived and the same harness hash as the pin", ['rec = read_build_record(man[\'program\'], pin)']),
                ('both self-checks are replayed again (hours for kx3) and equal the committed pin', ['texts = {spec: run_selfcheck(pin_run, repo, spec']),
                ('(old and new sha256: the program the previous sitting ran with)', ['old_sha256=program_in_use_before(rundir, man)']),
                ('`--dir RUN --dry-run` makes the same checks before it says a resume would replay and go on (or "it would be refused: ...")',
                 ["check_program_change(man, pin, a.pin, repo, school_rule, school_days, now)", "status = 'it would be refused: ' + re.sub(r'^REFUSED: ', '', str(e.code))"]),
                ('A run with every game played is not replayed for a changed program (the page is written from the games).',
                 ['so nothing is run: the program at', '(no self-check is replayed and no program change is logged)']),
                ('A run registered on the pinned route needs the same program byte for byte.', ['this run was registered on the pinned route, which has no build record and no rebuild']),
                ('Anything else is refused, naming both sha256 values', ['{PROGRAM_PROBLEM} {str(man.get("program_sha256"))[:12]}']),
                ('The `program_changed` lines of `slow_report_log.jsonl` are checked against the registration (rebuilt route, build record with the registered engine tree and harness hash, the registered '
                 'self-check texts), so a stray or foreign line is neither honoured nor shown on the page',
                 ["(man.get('slow_report') or {}).get('program_route') == 'rebuilt' and program_change_valid(e, man)", "rec.get('engine_tree_archived') == sr.get('engine_tree')",
                  "rec.get('harness_source_sha256') == sr.get('harness_source_sha256')", "e.get('selfcheck') == man.get('selfcheck')"]),
                ('that is a consistency check, not authentication (whoever can write the run folder can rewrite `manifest.json` and `manifest.sha256` as well): the pushed commit of the registration '
                 'is the tamper evidence', ['it is NOT authentication', 'whoever can write to the run folder can also rewrite manifest.json and manifest.sha256 (the pushed commit of the registration is the tamper evidence)']))
        for sentence, in_code in ties:
            with self.subTest(sentence=sentence[:70]):
                self.assertIn(sentence, section)
                for words in in_code:
                    self.assertIn(words, code, 'the code the sentence describes')

    def test_the_section_says_what_build_sh_does_with_a_folder_the_environment_a_lock_and_a_failed_cargo_and_build_sh_says_it_too(self):
        section, header = self.section(), re.sub(r'\s*\n#\s*', ' ', read(os.path.join(HERE, 'build.sh')).split('set -euo pipefail')[0])  # (the comment's lines joined into one text)
        for phrase in ('The output path is a file, not a folder (a folder is refused); the build folders and the output path may be given relative, the record and the rebuild command carry them absolute.',
                       'lists the cargo config files that still apply with their sha256', 'allows one build at a time per build folder and per target folder (locks held by the script alone)',
                       'stops with exit 1, no program and no record when cargo fails (it never hands out the program of an earlier build)', 'is **not signed**',
                       'the record lists the ones that were set, so the printed rebuild command does not depend on them', 'what stands behind the program are the replayed self-checks in step 2'):
            with self.subTest(readme=phrase[:60]):
                self.assertIn(phrase, section)
        for phrase in ('a directory is refused', 'is not signed', 'the record lists the ones that were set', 'cargo\'s config files that would still apply are listed in the record with their sha256',
                       'One build at a time per STRENGTH_BUILD_DIR and per target folder (locks, held by this script only)', 'a failed cargo build stops the script with no program and no record'):
            with self.subTest(build_sh=phrase[:60]):
                self.assertIn(phrase, header)
        for gone in ('repeats the build anywhere', 'any machine', 'allows one build at a time per build folder (a lock)', 'a lock in it'):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, section, 'the README no longer promises that the printed command repeats the build anywhere, nor one lock only')
                self.assertNotIn(gone, header, 'and neither does build.sh')

    def test_the_section_says_what_the_build_does_not_pin_in_the_words_build_sh_uses_and_that_a_rebuild_is_not_a_guarantee(self):
        section, header = self.section(), re.sub(r'\s*\n#\s*', ' ', read(os.path.join(HERE, 'build.sh')).split('set -euo pipefail')[0])
        self.assertIn("It does not pin the C toolchain (`CC`, `CFLAGS`), the system libraries or the toolchain behind rustup's default, so the same bytes need the same machine setup, which is why "
                      'step 5 is not a guarantee.', section)
        self.assertIn("the toolchain beyond the rustup default (`rustc -vV` is recorded), C toolchain variables such as CC and CFLAGS, and the system libraries: the same bytes need the same machine setup",
                      header)
        self.assertIn('the replay in step 2 is the check', section, 'and what the README relies on instead')

    def test_the_section_says_what_the_pin_check_reads_when_git_variables_are_exported_and_what_the_refusal_quotes_of_gits_message(self):
        section = self.section()
        self.assertIn("the refusal quotes the first line of git's own message and the `git config --global --add safe.directory <folder>` line that fixes it", section)
        self.assertIn('The check reads the repository it is told about even when `GIT_DIR` and its relatives are exported (a git hook, `rebase --exec`).', section)
        body = read(os.path.join(HERE, 'build.sh')).split('set -euo pipefail')[1]
        unset = next(l for l in body.splitlines() if l.startswith('unset '))
        self.assertEqual(unset.split()[1:], list(sr.GIT_REPO_VARS), 'build.sh removes the very variables slow_report.py removes')
        self.assertLess(body.index(unset), min(body.index('git -C'), body.index('git --git-dir')), 'and before its first git read')

    def test_the_section_keeps_its_six_steps_in_order_and_the_new_sentences_sit_in_the_steps_that_own_them(self):
        section = self.section()
        positions = [section.index(f'\n{n}. **{title}') for n, title in ((1, 'Build the pinned source.'), (2, 'Register only**'), (3, 'Commit and push the registered folder**'), (4, 'Play in slices**'),
                                                                          (5, 'After a container restart**'), (6, 'Finish**'))]
        self.assertEqual(positions, sorted(positions))
        steps = {n: section[a:b] for n, (a, b) in enumerate(zip(positions, positions[1:] + [len(section)]), 1)}
        self.assertIn('allows one build at a time per build folder and per target folder (locks held by the script alone)', steps[1])
        self.assertIn('`strength.build.json`', steps[1])
        self.assertIn('prints "stopped after --max-games N (games across both arms, about half of them kx3 games); resume with: <command>"', steps[4])
        self.assertIn('A run with every game played is not replayed for a changed program', steps[5])
        self.assertIn('detected dubious ownership', section.split('\n1. **')[0], 'the git remedy is in the opening paragraph, with the committed-pin rule it belongs to')

    def test_the_section_says_a_slice_is_counted_across_both_arms_and_the_help_and_the_message_say_it_too(self):
        section = self.section()
        self.assertIn('across both arms', section)
        self.assertIn('about N/2 of them kx3 games', section)
        helped = ' '.join(self.script('--help').stdout.split())
        self.assertIn('--max-games MAX_GAMES play at most this many games in this call (counted across both arms: about half of them kx3 games)', helped)

    def test_the_date_option_says_the_run_folder_is_dated_in_chicago_with_the_utc_fallback(self):
        helped = ' '.join(self.script('--help').stdout.split())
        self.assertIn('--date DATE YYYY-MM-DD for the run directory name (default: today in Chicago, or the UTC date on a machine without the time zone database)', helped)

    def test_the_build_command_has_the_environment_assignments_that_make_it_repeatable_and_is_not_the_pinned_path(self):
        pin = self.pin()
        env, ref, out = readme_build_command()
        self.assertEqual(sorted(env), ['CARGO_HOME', 'HOME', 'STRENGTH_BUILD_DIR', 'STRENGTH_TARGET_DIR'])
        self.assertTrue(set(env) <= set(REBUILD_ENV), 'every name is one the build record repeats in its rebuild command')
        build = read(os.path.join(HERE, 'build.sh'))
        for name in ('STRENGTH_BUILD_DIR', 'STRENGTH_TARGET_DIR'):
            self.assertIn(name, build, 'and build.sh reads it')
        self.assertEqual(env['HOME'], '$HOME')
        for name, value in env.items():
            self.assertTrue(value.startswith('$HOME'), f'{name}={value}: under the home folder')
        self.assertEqual(ref, pin['engine_ref'])
        pinned, pinned_folder = os.path.normpath(pin['program']), os.path.dirname(pin['program'])
        for home in (os.path.dirname(os.path.dirname(pin['program'])), '/root', '/home/agent', '/tmp/a b'):
            for what, value in [('OUT', out)] + list(env.items()):
                with self.subTest(home=home, what=what):
                    path = os.path.normpath(value.replace('$HOME', home))
                    self.assertNotEqual(path, pinned)
                    self.assertFalse(path.startswith(pinned_folder + os.sep), f'{path} is inside the pinned binary\'s folder')

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

    # the options the sections write that belong to another program: cargo's, and git's in the one command that fixes a folder git refuses as unsafe
    FOREIGN = {'--offline': 'cargo --offline', '--global': 'git config --global --add safe.directory', '--add': 'git config --global --add safe.directory', '--exec': '`rebase --exec`'}

    def test_every_flag_the_section_writes_is_an_option_of_the_script_except_the_ones_it_gives_to_cargo_and_to_git(self):
        section = self.section()
        flags = set(re.findall(r'(?<![\w-])--[a-z][a-z-]*', section))
        self.assertTrue(set(self.FOREIGN) <= flags and len(flags) >= 8, sorted(flags))
        helped = self.script('--help')
        self.assertEqual(helped.returncode, 0, helped.stderr)
        for flag in sorted(flags - set(self.FOREIGN)):
            with self.subTest(flag=flag):
                self.assertIn(flag, helped.stdout)
        for flag, command in self.FOREIGN.items():
            self.assertIn(command, section, f'{flag} is written inside the command it belongs to')
        self.assertIn('`git config --global --add safe.directory <folder>`', section, "--global and --add are git's, in the one command the section gives")
        self.assertIn('cargo build --release --offline', read(os.path.join(HERE, 'build.sh')), "and --offline is what build.sh gives cargo")

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
        self.assertEqual([f for f in sorted(flags - set(self.FOREIGN)) if f not in options], [], 'every option is one of the scripts (cargo\'s and git\'s own are left out)')
        for flag in self.FOREIGN:
            self.assertIn(flag, flags)

    def test_step_1_builds_to_a_path_of_its_own_that_step_2_then_uses_and_never_the_pinned_binarys(self):
        pin, section = self.pin(), self.section()
        env, ref, out = readme_build_command()
        self.assertEqual(ref, pin['engine_ref'])
        self.assertTrue(out.startswith('$HOME/'), out)
        registrations = [args for args in self.slow_report_commands(section) if '--register-only' in args]
        self.assertEqual(len(registrations), 1, 'step 2 gives one registration command')
        words = registrations[0]
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

    def test_a_slice_counts_its_games_across_both_arms_and_ends_with_the_message_that_says_so(self):
        """--max-games N plays N games in all (about half of them kx3 games, the other half the cheap km3 baseline) and stops with the message the README quotes, the count explained."""
        d = self.register()
        code, out, err = self.cli('--dir', d, '--max-games', '4', deck=False)
        self.assertEqual(code, 0, str(code) + err)
        lines = [l for l in out.splitlines() if 'stopped after --max-games' in l]
        self.assertEqual(len(lines), 1, out)
        command = json.loads(read(os.path.join(d, 'manifest.json')))['slow_report']['resume_command']
        self.assertEqual(lines[0].split('] ', 1)[1], f'stopped after --max-games 4 (games across both arms, about half of them kx3 games); resume with: {command}')
        for quoted in ('stopped after --max-games ', '; resume with: '):
            self.assertIn(quoted.strip('; '), lines[0], 'the words the README quotes are in it')
        readme_quote = re.search(r'prints "(stopped after --max-games N [^"]*)"', cloud_section()).group(1)
        self.assertEqual(readme_quote.replace('N', '4', 1).replace('<command>', command), lines[0].split('] ', 1)[1], 'the README quotes the very message, with N and <command> filled in')
        games = jsonl(os.path.join(d, 'games.jsonl'))
        self.assertEqual(sorted(g['arm'] for g in games), ['X', 'X', 'ref', 'ref'], '4 games across both arms: 2 kx3 games and 2 km3 baseline games')

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
