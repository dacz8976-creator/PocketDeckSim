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


def make_run(d, sha='match'):
    """A minimal registered run in directory d. sha: 'match', 'wrong', 'missing' or 'empty' (what manifest.sha256 holds)."""
    man = dict(name='refusal_test', pilot='kx', reference='km3', stage='dev', created_at='2026-10-03T11:00:00Z', planned_games=2,
               decks=[dict(name='d1')], opponents=[dict(name='o1')], threads=1)
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


if __name__ == '__main__':
    unittest.main()
