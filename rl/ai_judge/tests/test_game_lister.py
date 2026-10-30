import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
AIJ = os.path.dirname(HERE)
sys.path.insert(0, AIJ)
REPO = os.path.abspath(os.path.join(AIJ, '..', '..'))
import judge  # noqa: E402

TMP = os.environ['TMPDIR']
T = '/home/dacz8976/gemini_target'
JP = T + '/judge/release/judge_plans'
JP0 = T + '/judge_plans_before'
LS = T + '/judge/release/leak_states'
POS = os.path.join(REPO, 'rl/results/pause_games_new_2026-10-13/v2/positions_all.json')
IDS = os.path.join(REPO, 'rl/results/pause_games_new_2026-10-13/v2/run_ids.txt')
V2DECKS = os.path.join(REPO, 'rl/results/pause_games_new_2026-10-13/v2/decks')
FIXD = os.path.join(HERE, 'fixtures', 'decks')
FIXTURES = [os.path.join(HERE, 'fixtures', n) for n in ('mini_positions.json', 'baseline_positions.json', 'retreat_positions.json')]
LIM = ['--max-plans', '2000', '--max-nodes', '200000', '--max-steps', '30']


def cut(x):
    return str(x)[:300]


def run(argv, check=True):
    p = subprocess.run(argv, capture_output=True, timeout=1700, cwd=REPO)
    if check and p.returncode != 0:
        raise AssertionError('rc=%d %s' % (p.returncode, cut(p.stderr.decode('utf-8', 'replace'))))
    return p


def ids92():
    with open(IDS) as f:
        return [l.strip() for l in f if l.strip()]


def lines_of(p):
    return [json.loads(l) for l in p.stdout.decode('utf-8').splitlines() if l.strip()]


def pos_files():
    """(label, positions file, decks dir, only-ids or None)"""
    out = [(os.path.basename(f), f, FIXD, None) for f in FIXTURES]
    out.append(('92', POS, V2DECKS, ids92()))
    return out


def pos_argv(binary, f, decks, only, extra=()):
    a = [binary, '--positions', f] + judge.deck_args(decks)
    for i in only or []:
        a += ['--only', i]
    return a + list(extra)


_EXPORTS = {}


def exports(label, f, decks, only):
    """positions mode with --export-observations; returns (positions stdout lines bytes, export records)"""
    if label in _EXPORTS:
        return _EXPORTS[label]
    out = os.path.join(TMP, 'exp_%s.jsonl' % label)
    p = run(pos_argv(JP, f, decks, only, ['--export-observations', out]))
    with open(out) as fh:
        recs = [json.loads(l) for l in fh if l.strip()]
    _EXPORTS[label] = (p.stdout, recs)
    return _EXPORTS[label]


def obs_run(recs, name, extra=(), raw=False):
    inp = os.path.join(TMP, name + '_in.jsonl')
    with open(inp, 'w') as fh:
        for r in recs:
            fh.write(json.dumps(r) + '\n')
    p = run([JP, '--observations', inp] + LIM + list(extra))
    if raw:
        return [l for l in p.stdout.splitlines() if l.strip()]
    return lines_of(p)


def by_kind(lines):
    out = {}
    for l in lines:
        out.setdefault(l['kind'], {})[l['id']] = l
    return out


class Lister(unittest.TestCase):
    def test_L1_positions_identity(self):
        for label, f, decks, only in pos_files():
            a = run(pos_argv(JP, f, decks, only)).stdout
            b = run(pos_argv(JP0, f, decks, only)).stdout
            if a != b:
                la, lb = a.splitlines(), b.splitlines()
                for i, (x, y) in enumerate(zip(la, lb)):
                    if x != y:
                        self.fail('%s line %d: %s | %s' % (label, i, cut(x), cut(y)))
                self.fail('%s: length differs %d %d' % (label, len(la), len(lb)))
            print('L1', label, len(a.splitlines()), 'lines identical')

    def test_L2_roundtrip(self):
        vmhwm = vmpeak = 0
        for label, f, decks, only in pos_files():
            pos_out, recs = exports(label, f, decks, only)
            pos_lines = {json.loads(l)['id']: l for l in pos_out.splitlines() if l.strip() and json.loads(l)['kind'] == 'plans'}
            null_legal = sum(1 for r in recs if r['legal_actions'] is None)
            print('NULL_LEGAL', label, null_legal)
            self.assertEqual(null_legal, 0)
            raw = obs_run(recs, 'l2_' + label, raw=True)
            parsed = [json.loads(l) for l in raw]
            kinds = by_kind(parsed)
            self.assertEqual(len(kinds['plans']), len(recs))
            for l, d in zip(raw, parsed):
                if d['kind'] == 'plans':
                    want = pos_lines[d['id']]
                    if l != want:
                        self.fail('%s: id %s plans line differs: %s | %s' % (label, d['id'], cut(l), cut(want)))
                    self.assertEqual(d, json.loads(want))
                if d['kind'] == 'root_check':
                    self.assertTrue(d['ok'] is True, '%s root_check not ok: %s' % (d['id'], cut(d['missing_in_lister']) + cut(d['extra_in_lister'])))
            for d in kinds['stats'].values():
                vmhwm = max(vmhwm, d['vmhwm_kb'])
                vmpeak = max(vmpeak, d['vmpeak_kb'])
        print('VMHWM_MAX', vmhwm)
        print('VMPEAK_MAX', vmpeak)

    def test_L3_root_classes(self):
        for label, f, decks, only in pos_files():
            if label == '92':
                continue
            _, recs = exports(label, f, decks, only)
            kinds = by_kind(obs_run(recs, 'l3_' + label))
            for i, d in kinds['root_check'].items():
                for e in d['root']:
                    self.assertIn(e['class'], ('plan', 'noop', 'dup_of', 'no_plan'))
                    self.assertNotEqual(e['class'], 'no_plan', '%s %s' % (i, cut(e['action'])))
                self.assertEqual(d['n_plan'] + d['n_noop'] + d['n_dup_of'] + d['n_no_plan'], d['n_root'])

    def test_L4_plan_actions_trace(self):
        n_checked = 0
        for label in ('mini_positions.json', 'baseline_positions.json'):
            f = [x for x in FIXTURES if x.endswith(label)][0]
            _, recs = exports(label, f, FIXD, None)
            recs = recs[:3]
            kinds = by_kind(obs_run(recs, 'l4a_' + label))
            tr_in = []
            expect = {}
            for r in recs:
                plans = {p['n']: p for p in kinds['plans'][r['id']]['plans']}
                for pa in kinds['plan_actions'][r['id']]['plans']:
                    p = plans[pa['n']]
                    self.assertEqual(len(pa['actions']), p['n_steps'], r['id'])
                    tid = '%s|%d' % (r['id'], pa['n'])
                    tr_in.append({'id': tid, 'pdl_observation': r['pdl_observation'], 'actions': pa['actions']})
                    expect[tid] = (p['n_steps'], p['end'])
            inp = os.path.join(TMP, 'l4_trace_in.jsonl')
            with open(inp, 'w') as fh:
                for t in tr_in:
                    fh.write(json.dumps(t) + '\n')
            res = lines_of(run([JP, '--trace', inp]))
            self.assertEqual(len(res), len(tr_in))
            for t in res:
                n_steps, end = expect[t['id']]
                self.assertTrue(t['ok'], '%s %s' % (t['id'], cut(t.get('error'))))
                self.assertEqual(len(t['steps']), n_steps, t['id'])
                self.assertEqual(t['steps'][-1]['end'], end, t['id'])
                n_checked += 1
        print('L4 plans traced', n_checked)
        self.assertGreater(n_checked, 5)

    def test_L5_obs_hash_stable(self):
        _, recs = exports('mini_positions.json', FIXTURES[0], FIXD, None)
        hs = []
        for k in range(2):
            inp = os.path.join(TMP, 'l5_in.jsonl')
            with open(inp, 'w') as fh:
                for r in recs:
                    fh.write(json.dumps({'id': r['id'], 'pdl_observation': r['pdl_observation']}) + '\n')
            hs.append([d['hash'] for d in lines_of(run([JP, '--obs-hash', inp]))])
        self.assertEqual(hs[0], hs[1])
        self.assertGreater(len(set(hs[0])), 1)

    def test_L7_bad_information_model(self):
        _, recs = exports('mini_positions.json', FIXTURES[0], FIXD, None)
        bad = json.loads(json.dumps(recs[0]))
        bad['pdl_observation']['information_model'] = 'open-v0'
        inp = os.path.join(TMP, 'l7_in.jsonl')
        with open(inp, 'w') as fh:
            fh.write(json.dumps(bad) + '\n')
        p = run([JP, '--observations', inp] + LIM)
        self.assertEqual(p.returncode, 0)
        ls = lines_of(p)
        self.assertEqual([l['kind'] for l in ls], ['problem'])


if __name__ == '__main__':
    unittest.main()
