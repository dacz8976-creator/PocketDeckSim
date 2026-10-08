#!/usr/bin/env python3
"""Tests that strength_report.py refuses a run whose registration changed, and that --override writes a report under a REGISTRATION CHANGED banner.

  cd rl/strength && python3 -B -m unittest -v test_strength_report

Every run directory here is built in a temporary folder; no real run is read or written.
"""
import hashlib, json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, 'strength_report.py')


def read(path, mode='r'):
    with open(path, mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def moves(ms):
    return dict(n=len(ms), total_s=sum(ms) / 1000, ms=ms)


def game(arm, winner):
    """One finished game of the single synthetic pair (deck d1, opponent o1, deal 0, seat 0)."""
    return dict(key=f'd1|o1|0|0|{arm}', deck='d1', opp='o1', deal=0, seat=0, arm=arm, first='deck', seed=7, winner=winner,
                points=[3, 1], turns=9, wall_s=0.5, moves_deck=moves([5.0, 6.0]), moves_opp=moves([4.0]),
                pilot_deck='km3' if arm == 'ref' else 'kx', pilot_opp='km3', started_at='2026-10-03T12:00:00Z')


def make_run(d, sha='match', stage='dev', **extra):
    """A minimal registered run in directory d. sha: 'match', 'wrong', 'missing' or 'empty' (what manifest.sha256 holds). Any other keyword is a manifest entry."""
    man = dict(name='refusal_test', pilot='kx', reference='km3', stage=stage, created_at='2026-10-03T11:00:00Z', planned_games=2,
               decks=[dict(name='d1')], opponents=[dict(name='o1')], threads=1)
    man.update(extra)
    mpath = os.path.join(d, 'manifest.json')
    write(mpath, json.dumps(man, indent=1))
    real = hashlib.sha256(read(mpath, 'rb')).hexdigest()
    spath = os.path.join(d, 'manifest.sha256')
    if sha == 'match':
        write(spath, real + '  manifest.json\n')
    elif sha == 'wrong':
        write(spath, hashlib.sha256(b'the manifest as first registered').hexdigest() + '  manifest.json\n')
    elif sha == 'empty':
        write(spath, '')
    write(os.path.join(d, 'games.jsonl'), json.dumps(game('X', 'deck')) + '\n' + json.dumps(game('ref', 'opp')) + '\n')
    return real


def snapshot(d):
    return {n: read(os.path.join(d, n), 'rb') for n in sorted(os.listdir(d))}


def run_report(d, *extra):
    return subprocess.run([sys.executable, '-B', REPORT, '--dir', d, *extra], capture_output=True, text=True)


class RefusesChangedRegistration(unittest.TestCase):
    def check_refused(self, sha):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, sha)
            before = snapshot(d)
            r = run_report(d)
            self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn('REFUSED', r.stderr)
            self.assertIn('--override', r.stderr)
            self.assertNotIn('Traceback', r.stderr)
            self.assertEqual(r.stdout, '', 'a refused run must not print a report')
            self.assertFalse(os.path.exists(os.path.join(d, 'REPORT.md')))
            self.assertFalse(os.path.exists(os.path.join(d, 'report.json')))
            self.assertEqual(snapshot(d), before, 'a refused run must leave the run directory exactly as it was')

    def test_manifest_differs_from_registered_sha(self):
        self.check_refused('wrong')

    def test_manifest_sha256_missing(self):
        self.check_refused('missing')

    def test_manifest_sha256_empty(self):
        self.check_refused('empty')

    def test_refuses_with_out_too(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as o:
            make_run(d, 'wrong')
            out = os.path.join(o, 'elsewhere.md')
            r = run_report(d, '--out', out)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(out))


class OverrideWritesBanner(unittest.TestCase):
    def test_override_writes_report_with_banner_first(self):
        for sha in ('wrong', 'missing', 'empty'):
            with self.subTest(sha=sha), tempfile.TemporaryDirectory() as d:
                make_run(d, sha)
                r = run_report(d, '--override')
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertIn('REGISTRATION CHANGED', r.stderr)
                text = read(os.path.join(d, 'REPORT.md'))
                self.assertTrue(text.startswith('# REGISTRATION CHANGED'), text[:200])
                self.assertIn('--override', text.split('# Strength report')[0])
                self.assertIn('# Strength report: refusal_test', text, 'the report itself is still written')
                self.assertTrue(r.stdout.startswith('# REGISTRATION CHANGED'))
                rep = json.loads(read(os.path.join(d, 'report.json')))
                self.assertTrue(rep['registration_changed'])
                self.assertEqual(len(rep['registration_problems']), 1)
                self.assertEqual(rep['paired_games'], 1)

    def test_override_does_not_alter_the_run(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'wrong')
            before = snapshot(d)
            run_report(d, '--override')
            after = snapshot(d)
            for n in before:
                self.assertEqual(after[n], before[n], n)
            self.assertEqual(sorted(set(after) - set(before)), ['REPORT.md', 'report.json'])


class IntactRegistration(unittest.TestCase):
    def test_no_banner_and_no_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match')
            r = run_report(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            text = read(os.path.join(d, 'REPORT.md'))
            self.assertNotIn('REGISTRATION CHANGED', text)
            self.assertIn('(matches the pre-registration)', text)
            self.assertEqual(r.stderr, '')
            rep = json.loads(read(os.path.join(d, 'report.json')))
            self.assertFalse(rep['registration_changed'])
            self.assertEqual(rep['registration_problems'], [])

    def test_override_on_an_intact_registration_adds_no_banner(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match')
            r = run_report(d, '--override')
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn('REGISTRATION CHANGED', read(os.path.join(d, 'REPORT.md')))
            self.assertEqual(r.stderr, '')


class UseStageNote(unittest.TestCase):
    """A report on a `use` run (the slow report) says up front that it is not development evidence; a development run's report does not."""

    def test_use_report_says_it_is_not_development_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match', stage='use')
            r = run_report(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            text = read(os.path.join(d, 'REPORT.md'))
            self.assertIn('not development evidence', text)
            self.assertIn('stage `use`', text)
            self.assertLess(text.index('not development evidence'), text.index('## Result'))
            self.assertEqual(json.loads(read(os.path.join(d, 'report.json')))['stage'], 'use')

    def test_dev_report_has_no_such_note(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match', stage='dev')
            run_report(d)
            self.assertNotIn('not development evidence', read(os.path.join(d, 'REPORT.md')))

    def test_the_use_note_says_which_numbers_to_quote_and_that_the_lock_is_not_lifted(self):
        """The whole note is the rule: it keeps the engineering report's intervals from being quoted in place of the slow report page's."""
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match', stage='use')
            self.assertEqual(run_report(d).returncode, 0)
            text = read(os.path.join(d, 'REPORT.md'))
            self.assertIn("**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. "
                          "This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, "
                          "and is the one to quote.", text)
            self.assertEqual(text.count('not development evidence'), 1)


class SelfCheckSourceAnnotation(unittest.TestCase):
    """The report prints the self-check digests the registration recorded, each with where the text came from (copied from the pin, replayed, run at registration)."""

    def report_of(self, **extra):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match', **extra)
            self.assertEqual(run_report(d).returncode, 0)
            return read(os.path.join(d, 'REPORT.md'))

    PIN_SOURCE = 'given in the config (copied from the pin, which says it was measured on this exact program sha256)'  # what strength_prereg.py records for a pinned text

    def test_each_digest_is_followed_by_its_source(self):
        text = self.report_of(selfcheck={'km3': 'selfcheck pilot=km3 digest=aaaa', 'kx': 'selfcheck pilot=kx digest=bbbb'},
                              selfcheck_source={'km3': self.PIN_SOURCE, 'kx': 'run by strength_prereg.py'})
        self.assertIn(f'Self-check digests recorded at registration: `selfcheck pilot=km3 digest=aaaa` ({self.PIN_SOURCE}); '
                      '`selfcheck pilot=kx digest=bbbb` (run by strength_prereg.py)', text)

    def test_a_digest_with_no_recorded_source_is_printed_plainly_and_no_digest_means_no_line(self):
        text = self.report_of(selfcheck={'km3': 'selfcheck pilot=km3 digest=aaaa', 'kx': 'selfcheck pilot=kx digest=bbbb'}, selfcheck_source={'kx': 'run by strength_prereg.py'})
        self.assertIn('registration: `selfcheck pilot=km3 digest=aaaa`; `selfcheck pilot=kx digest=bbbb` (run by strength_prereg.py)', text)
        self.assertNotIn('Self-check digests', self.report_of())
        self.assertNotIn('Self-check digests', self.report_of(selfcheck={}))

    def test_a_replayed_digest_says_so(self):
        replayed = 'replayed by slow_report.py on this machine just before registration (equal to the committed pin)'
        text = self.report_of(selfcheck={'km3': 'selfcheck pilot=km3 digest=aaaa', 'kx': 'selfcheck pilot=kx digest=bbbb'}, selfcheck_source={'km3': replayed, 'kx': replayed})
        self.assertIn(f'registration: `selfcheck pilot=km3 digest=aaaa` ({replayed}); `selfcheck pilot=kx digest=bbbb` ({replayed})', text)

    def test_a_manifest_that_records_digests_but_no_sources_is_still_reported(self):
        """An older registration (before the source was recorded) has the digests only: no key, an empty mapping, a null and an empty text all print the digest plainly."""
        plain = 'registration: `selfcheck pilot=km3 digest=aaaa`; `selfcheck pilot=kx digest=bbbb`\n'
        digests = {'km3': 'selfcheck pilot=km3 digest=aaaa', 'kx': 'selfcheck pilot=kx digest=bbbb'}
        for how, extra in {'no selfcheck_source key': {}, 'an empty mapping': dict(selfcheck_source={}), 'a null': dict(selfcheck_source=None),
                           'an empty text for each': dict(selfcheck_source={'km3': '', 'kx': ''})}.items():
            with self.subTest(how=how):
                text = self.report_of(selfcheck=digests, **extra)
                self.assertIn(plain, text)
                self.assertNotIn('()', text.split('Self-check digests')[1].split('\n')[0])


class PilotsAndErrors(unittest.TestCase):
    """report.json names both pilots; a game that errored counts once, and not at all once it was played on a later try."""

    def test_report_json_names_both_pilots(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match', stage='use')
            self.assertEqual(run_report(d).returncode, 0)
            rep = json.loads(read(os.path.join(d, 'report.json')))
            self.assertEqual((rep['pilot'], rep['reference']), ('kx', 'km3'))

    def test_errors_are_counted_by_game_not_by_line_and_a_game_played_later_is_not_one(self):
        with tempfile.TemporaryDirectory() as d:
            make_run(d, 'match')
            err = lambda k, m: json.dumps(dict(key=k, error=m, at='2026-10-03T12:30:00Z')) + '\n'
            # one game that panicked on three tries, one that panicked once and was then played (its key is in games.jsonl)
            write(os.path.join(d, 'errors.jsonl'), err('d1|o1|1|0|X', 'boom') * 3 + err('d1|o1|0|0|X', 'flaky'))
            r = run_report(d)
            self.assertEqual(r.returncode, 0, r.stderr)
            text = read(os.path.join(d, 'REPORT.md'))
            self.assertIn('errors 1', text.split('## Result')[0])
            self.assertIn('1 game failed', text)
            self.assertIn('d1|o1|1|0|X', text)
            self.assertNotIn('flaky', text)


if __name__ == '__main__':
    unittest.main()
