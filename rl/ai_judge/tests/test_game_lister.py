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


def obs_run(recs, name, extra=()):
    inp = os.path.join(TMP, name + '_in.jsonl')
    with open(inp, 'w') as fh:
        for r in recs:
            fh.write(json.dumps(r) + '\n')
    p = run([JP, '--observations', inp] + LIM + list(extra))
    return lines_of(p)


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


if __name__ == '__main__':
    unittest.main()
