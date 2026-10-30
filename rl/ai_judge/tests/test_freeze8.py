import contextlib
import io
import json
import os
import shutil
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
REAL = os.path.abspath(os.path.join(AIJ, '..', '..'))
sys.path.insert(0, AIJ)
import freeze8  # noqa: E402
import game_kit  # noqa: E402

TMP = os.environ['TMPDIR']
BINS_E = ('deckgym', 'protocol_bot')
BINS_J = ('judge_plans', 'kx3_parity', 'kx3_replay', 'leak_states')

SHADOW_FEED = ('PREREG v3.1 §2 said the shadow is fed every observation and event; it is asked only at setup and fallback points, because kx3 keeps no state between decisions '
               '(gate 4b proves equality) and feeding every decide would roughly double each (G) game\'s compute.')
SETUP_BY_KX3 = ('kx3 makes setup choices (turn_count == 0) in both arms; the judge plays from turn 1. Setup decisions are out of the fallback denominator and are counted separately. '
                'This narrows PREREG v3.1 §3, which listed setup as an intervention point. Reason: neutral between arms; frozen-7\'s lister was never validated on setup states.')
LABEL_SEATS = ('label seat numbers made relative to the actor, to match frozen-7\'s mover-at-0 convention. The actor is 0 and the opponent 1 in Promote, Activate, the English label text and '
               'every player field inside a Name#{json} label, and in that label\'s other seat fields (target_player, source_player, and the seat element of attacking_ref, targets, '
               'prior_knockouts, damaged_refs and point_denial_flips); the action sent to the engine keeps its real seat. With actor 0 the output is byte-identical by construction.')
PLAN_KEYS = ('Plan keys may differ from frozen-7\'s (the State JSON can gain fields); on the 92 they were equal (gate 1: full plan_list_sha256 92/92). '
             'Keys never reach the prompt. Gate 1 compares the key-free projection (labels, steps, ends, finals, results), the prompt bytes, and root_ok on every id; '
             'full plan_list_sha256 equality is for information only.')
REASK = "reask_reason gains a sixth value, 'lister_error', for a re-ask after a lister failure (coordinator-106, decision 5)."
REASK_OPP = ("The Gemini bot no longer asks the judge again on the adapter's opponent-choice counter. That counter comes from the opponent's full legal-action list, "
             "which can depend on hidden cards (Astra's weekly review, Oct 30). An opponent's choice now ends a plan only when the visible board differs from the "
             "plan's expectation (the obs-hash check).")
TURN_EFFECTS_END = ('Kept turn effects print as {"turn", "effect"} items; each effect\'s inner keys print in serde_json\'s sorted order, because observation mode serialises them with '
                    'serde_json::to_value without preserve_order, so no other order can occur there.')


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = freeze8.main(argv)
    return rc, buf.getvalue().splitlines()


class Env:
    """A temporary repo with a made-up FROZEN.json, and two bins folders with small fake binaries."""

    def __init__(self, name):
        self.root = os.path.join(TMP, 'z_' + name)
        shutil.rmtree(self.root, ignore_errors=True)
        self.repo = os.path.join(self.root, 'repo')
        for rel in freeze8.sources8(REAL)[0]:
            dst = os.path.join(self.repo, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(os.path.join(REAL, rel), dst)
        ai = os.path.join(self.repo, 'rl', 'ai_judge')
        with open(os.path.join(ai, 'zz_rel.py'), 'w') as f:
            f.write('x = 1\n')
        with open(os.path.join(ai, 'pinned.py'), 'w') as f:
            f.write('y = 2\n')
        with open(os.path.join(REAL, 'rl', 'ai_judge', 'FROZEN.json')) as f:
            fz = json.load(f)
        h = freeze8.sha256_file
        fz['source_sha256'] = {'rl/ai_judge/plans/src/main.rs': 'f' * 64, 'rl/ai_judge/pinned.py': h(os.path.join(ai, 'pinned.py')), 'zz_rel.py': h(os.path.join(ai, 'zz_rel.py')),
                               'rl/zz_outside/x.py': 'ab' * 32}
        with open(os.path.join(ai, 'FROZEN.json'), 'w') as f:
            json.dump(fz, f)
        self.eb, self.jb = os.path.join(self.root, 'eb'), os.path.join(self.root, 'jb')
        for d, names in ((self.eb, BINS_E), (self.jb, BINS_J)):
            os.makedirs(d)
            for n in names:
                with open(os.path.join(d, n), 'wb') as f:
                    f.write(n.encode() * 10)
        self.out = os.path.join(self.root, 'draft.json')
        self.args = ['--engine-bins', self.eb, '--judge-bins', self.jb, '--repo', self.repo]

    def record(self, extra=()):
        return run(['record', '--out', self.out] + list(extra) + self.args)

    def check(self, frozen=None):
        return run(['check', '--frozen', frozen or self.out] + self.args)

    def git_tree_fake(self):
        return lambda repo, path: {'engine': game_kit_trees()['engine'], 'lib': game_kit_trees()['lib']}[path]

    def patch(self):
        return mock.patch.multiple(freeze8, git_tree=self.git_tree_fake(), EXPECTED_DG=freeze8.sha256_file(os.path.join(self.eb, 'deckgym')),
                                   EXPECTED_PB=freeze8.sha256_file(os.path.join(self.eb, 'protocol_bot')))

    def flip(self, path):
        with open(path, 'rb') as f:
            b = bytearray(f.read())
        b[0] ^= 1
        with open(path, 'wb') as f:
            f.write(bytes(b))


def game_kit_trees():
    return {'engine': '34fef9e536e9ff6c1cc6ba2ae440e5b17941b858', 'lib': '65058095aaafdbcbddf67a0f4da4276d1d594c14'}


class Freeze8(unittest.TestCase):
    def test_Z1_draft_then_final(self):
        e = Env('z1')
        with e.patch():
            rc, out = e.record(['--draft'])
            self.assertEqual(rc, 0, out)
            rc, out = e.check()
            self.assertEqual((rc, out[-1]), (3, 'GATE5 DRAFT'), out)
            self.assertFalse([l for l in out if l.startswith('  diff')], out)
            with open(e.out) as f:
                d = json.load(f)
            d['draft'] = False
            d['frozen_on'] = '2026-11-01'
            d['supersedes'][0]['commit'] = 'abc'
            d['kx3']['selfcheck_checked'] = '2026-11-01T00:00:00Z equal'
            fin = os.path.join(e.root, 'final.json')
            with open(fin, 'w') as f:
                json.dump(d, f)
            rc, out = e.check(fin)
            self.assertEqual((rc, out[-1]), (0, 'GATE5 PASS'), out)

    def test_Z2_changed_sources8_file(self):
        e = Env('z2')
        with e.patch():
            e.record(['--draft'])
            e.flip(os.path.join(e.repo, 'rl', 'ai_judge', 'game_kit.py'))
            rc, out = e.check()
            self.assertEqual((rc, out[-1]), (1, 'GATE5 FAIL'), out)
            self.assertTrue(any('game_kit.py' in l for l in out), out)

    def test_Z3_frozen7_sources(self):
        e = Env('z3')
        ai = os.path.join(e.repo, 'rl', 'ai_judge')
        with e.patch():
            e.record(['--draft'])
            rc, out = e.check()
            self.assertIn('FROZEN7 SOURCES: 2/2 equal', out)
            self.assertTrue(any(l.startswith('outside clone: 1 keys') for l in out), out)
            self.assertTrue(any(l.startswith('skipped: rl/ai_judge/plans/src/main.rs') for l in out), out)
            self.assertEqual(rc, 3)
            # main.rs differs from its pin by design: skipped, not a difference
            self.assertFalse(any('main.rs recorded' in l for l in out))
            e.flip(os.path.join(ai, 'zz_rel.py'))
            rc, out = e.check()
            self.assertEqual(rc, 1)
            self.assertIn('FROZEN7 SOURCES: 1/2 equal', out)
            self.assertTrue(any(l.startswith('  zz_rel.py') for l in out), out)
            self.assertFalse(any('zz_outside' in l and 'recorded' in l for l in out))
            e.flip(os.path.join(ai, 'zz_rel.py'))
            e.flip(os.path.join(ai, 'pinned.py'))
            rc, out = e.check()
            self.assertEqual(rc, 1)
            self.assertTrue(any(l.startswith('  rl/ai_judge/pinned.py') for l in out), out)
            e.flip(os.path.join(ai, 'pinned.py'))
            os.remove(os.path.join(ai, 'pinned.py'))
            rc, out = e.check()
            self.assertEqual(rc, 1)
            self.assertTrue(any('pinned.py' in l and 'MISSING' in l for l in out), out)

    def test_Z4_draft_exit3(self):
        e = Env('z4')
        with e.patch():
            e.record(['--draft'])
            rc, out = e.check()
            self.assertEqual((rc, out[-1]), (3, 'GATE5 DRAFT'))

    def test_Z5_deviations(self):
        e = Env('z5')
        with e.patch():
            e.record(['--draft'])
        with open(e.out) as f:
            d = json.load(f)
        ids = [x['id'] for x in d['deviations']]
        self.assertEqual(ids, ['lister_rebuild', 'converter', 'plan_keys', 'label_seats', 'turn_effects', 'retries_and_charges', 'call_cap', 'shadow_feed', 'setup_by_kx3',
                               'gate1_rule', 'kx3_route_drop', 'gate2_fill_seed', 'gate2_revealed', 'root_dup_noop', 'reask_lister_error',
                               'reask_opponent_choice'])
        by = {x['id']: x for x in d['deviations']}
        self.assertEqual(by['shadow_feed']['text'], SHADOW_FEED)
        self.assertEqual(by['setup_by_kx3']['text'], SETUP_BY_KX3)
        self.assertEqual(by['label_seats']['text'], LABEL_SEATS)
        self.assertTrue(by['turn_effects']['text'].endswith(TURN_EFFECTS_END))
        self.assertEqual(by['plan_keys']['text'], PLAN_KEYS)
        self.assertEqual(by['plan_keys']['source'], 'coordinator-103, wording coordinator-108')
        self.assertEqual(by['reask_lister_error'], {'id': 'reask_lister_error', 'from': 'PREREG v3.1 §2 judge bot', 'source': 'coordinator-106, decision 5; coordinator-108', 'text': REASK})
        self.assertEqual(by['reask_opponent_choice'], {'id': 'reask_opponent_choice', 'from': 'PREREG v3.1 §2 judge bot step 5', 'source': 'coordinator-110, decisions 1 and 3',
                                                       'text': REASK_OPP})
        for x in d['deviations']:
            self.assertEqual(sorted(x), ['from', 'id', 'source', 'text'])
        self.assertEqual(d['tag'], 'judge-prompt-frozen-8')
        self.assertTrue(d['draft'])
        self.assertIsNone(d['frozen_on'])
        self.assertEqual(d['kx3']['selfcheck_pin'], 'selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa')
        self.assertIn('outside_clone', d)

    def test_Z8_binaries_enforced(self):
        e = Env('z8')
        dg, pb = os.path.join(e.eb, 'deckgym'), os.path.join(e.eb, 'protocol_bot')
        with mock.patch.object(freeze8, 'git_tree', e.git_tree_fake()):
            rc, out = e.record(['--draft'])
            self.assertEqual(rc, 2, out)
            self.assertTrue(any(dg in l for l in out), out)
            self.assertFalse(os.path.exists(e.out))
        with mock.patch.multiple(freeze8, git_tree=e.git_tree_fake(), EXPECTED_DG=freeze8.sha256_file(dg)):
            rc, out = e.record(['--draft'])
            self.assertEqual(rc, 2, out)
            self.assertTrue(any(pb in l for l in out), out)
            self.assertFalse(any(dg in l for l in out), out)
        with e.patch():
            rc, out = e.record(['--draft'])
            self.assertEqual(rc, 0, out)
        with mock.patch.object(freeze8, 'git_tree', e.git_tree_fake()):
            rc, out = e.check()
            self.assertEqual((rc, out[-1]), (1, 'GATE5 FAIL'), out)
            self.assertTrue(any(dg in l for l in out), out)

    def test_Z6_forbidden_env(self):
        e = Env('z6')
        with e.patch():
            e.record(['--draft'])
            with mock.patch.dict(os.environ, {'PDL_DB': 'made-up'}):
                rc, out = e.check()
            self.assertEqual((rc, out[-1]), (1, 'GATE5 FAIL'), out)

    def test_Z7_changed_binary(self):
        for which in ('eb', 'jb'):
            e = Env('z7' + which)
            with e.patch():
                e.record(['--draft'])
                d = getattr(e, which)
                e.flip(os.path.join(d, sorted(os.listdir(d))[0]))
                rc, out = e.check()
                self.assertEqual((rc, out[-1]), (1, 'GATE5 FAIL'), out)


if __name__ == '__main__':
    unittest.main()
