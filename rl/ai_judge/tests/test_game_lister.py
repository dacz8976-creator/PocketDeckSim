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


def jdiff(a, b, path='$'):
    """first differing JSON path of a and b as (path, a_value, b_value), or None"""
    if type(a) is not type(b):
        return (path, a, b)
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return (path + '.' + str(k), a.get(k, '<missing>'), b.get(k, '<missing>'))
            d = jdiff(a[k], b[k], path + '.' + str(k))
            if d:
                return d
        return None
    if isinstance(a, list):
        for i in range(min(len(a), len(b))):
            d = jdiff(a[i], b[i], '%s[%d]' % (path, i))
            if d:
                return d
        if len(a) != len(b):
            return (path + '.len', len(a), len(b))
        return None
    return None if a == b else (path, a, b)


def jdiff_msg(label, id_, x, y):
    try:
        d = jdiff(json.loads(x), json.loads(y))
    except ValueError:
        d = ('<not json>', x, y)
    return '%s id %s path %s: %s | %s' % (label, id_, d[0] if d else '?', cut(d[1] if d else x), cut(d[2] if d else y))


def pos_count(f, only):
    if only:
        return len(only)
    with open(f) as fh:
        return len(json.load(fh))


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


def ls_dump(name, cell_deck, cell_list, seat, seeds, every, dump_only=True):
    out = os.path.join(TMP, name + '.jsonl')
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        import game_kit
        run([LS, '--pilot-deck', game_kit.DECKS[cell_deck], '--opp-deck', game_kit.LISTS[cell_list], '--seat', str(seat),
             '--seeds', ','.join(str(x) for x in seeds), '--every', str(every)] + (['--dump-only'] if dump_only else []) + ['--out', out])
    with open(out) as fh:
        return [json.loads(l) for l in fh if l.strip()]


_SEAT1 = {}


def seat1_inputs():
    """Observations of the two seat-1 dumps (A v list 1 at cell 1, B v list 2 at cell 13): every opponent-turn state, plus the first 20 own-turn states of each dump."""
    if 'v' in _SEAT1:
        return _SEAT1['v']
    import game_kit
    cells = ((0, 0, 1), (1, 1, 13))
    ks = [90]
    while True:
        recs = {}
        for deck, lst, cell in cells:
            seeds = [game_kit.seed(cell, k) for k in ks]
            name = 's1dump_%d_%s' % (cell, '_'.join(str(k) for k in ks))
            recs[cell] = [r for r in ls_dump(name, deck, lst, 1, seeds, 1) if r['actor'] == 1 and r['turn_count'] >= 1]
        opp_turn = [r for c in recs.values() for r in c if r['current_player'] != r['actor']]
        if len(opp_turn) >= 2 or ks[-1] >= 99:
            break
        ks.append(ks[-1] + 1)
    chosen = []
    for c in recs.values():
        own = [r for r in c if r['current_player'] == r['actor']][:20]
        chosen += own + [r for r in c if r['current_player'] != r['actor']]
    inputs = [{'id': r['id'], 'pdl_observation': r['obs_a'], 'legal_actions': r['legal_actions']} for r in chosen]
    meta = {r['id']: r for r in chosen}
    lines = by_kind(obs_run(inputs, 'seat1_obs'))
    _SEAT1['v'] = (inputs, meta, lines)
    return _SEAT1['v']


class Lister(unittest.TestCase):
    def test_L1_positions_identity(self):
        for label, f, decks, only in pos_files():
            a = run(pos_argv(JP, f, decks, only)).stdout
            b = run(pos_argv(JP0, f, decks, only)).stdout
            if a != b:
                la, lb = a.splitlines(), b.splitlines()
                for i, (x, y) in enumerate(zip(la, lb)):
                    if x != y:
                        try:
                            id_ = json.loads(x).get('id')
                        except ValueError:
                            id_ = '?'
                        self.fail('%s line %d: %s' % (label, i, jdiff_msg('L1', id_, x, y)))
                self.fail('%s: length differs %d %d' % (label, len(la), len(lb)))
            print('L1', label, len(a.splitlines()), 'lines identical')

    def test_L2_roundtrip(self):
        a_, b_ = {'id': 'x', 'v': [1, {'k': 'p'}]}, {'id': 'x', 'v': [1, {'k': 'q'}]}
        self.assertEqual(jdiff(a_, b_), ('$.v[1].k', 'p', 'q'))
        vmhwm = vmpeak = 0
        fx_hwm = fx_peak = 0
        for label, f, decks, only in pos_files():
            pos_out, recs = exports(label, f, decks, only)
            pos_lines = {json.loads(l)['id']: l for l in pos_out.splitlines() if l.strip() and json.loads(l)['kind'] == 'plans'}
            self.assertEqual(len(recs), pos_count(f, only), label)
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
                        self.fail(jdiff_msg('L2 ' + label, d['id'], l, want))
                    self.assertEqual(d, json.loads(want))
                if d['kind'] == 'root_check':
                    self.assertTrue(d['ok'] is True, '%s root_check not ok: %s' % (d['id'], cut(d['missing_in_lister']) + cut(d['extra_in_lister'])))
            for d in kinds['stats'].values():
                if label == '92':
                    vmhwm = max(vmhwm, d['vmhwm_kb'])
                    vmpeak = max(vmpeak, d['vmpeak_kb'])
                else:
                    fx_hwm = max(fx_hwm, d['vmhwm_kb'])
                    fx_peak = max(fx_peak, d['vmpeak_kb'])
        print('FIXTURES_VMHWM_MAX', fx_hwm, 'FIXTURES_VMPEAK_MAX', fx_peak)
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

    def test_L6_leak_states_obs(self):
        import game_kit
        recs = []
        for deck, lst, seat, cell in ((0, 0, 0, 0), (0, 0, 1, 1)):
            recs += ls_dump('l6_c%d' % cell, deck, lst, seat, [game_kit.seed(cell, 90)], 3)
        inputs = [{'id': r['id'], 'pdl_observation': r['obs_a'], 'legal_actions': r['legal_actions']} for r in recs]
        lines = obs_run(inputs, 'l6_obs')
        kinds = by_kind(lines)
        setup = [0, 0, 0]
        rest_ok = rest_n = 0
        for r in recs:
            rc = kinds.get('root_check', {}).get(r['id'])
            pr = kinds.get('problem', {}).get(r['id'])
            if r['turn_count'] == 0:
                setup[2 if pr else (0 if rc and rc['ok'] else 1)] += 1
                continue
            rest_n += 1
            if rc and rc['ok'] is True:
                rest_ok += 1
            else:
                print('L6 FAIL', r['id'], cut(pr or (rc['missing_in_lister'], rc['extra_in_lister'])))
        print('L6 setup (ok, not ok, problem)', setup)
        print('L6 root_check ok share', rest_ok, '/', rest_n)
        self.assertGreaterEqual(rest_ok, 0.95 * rest_n)
        n_seat1 = 0
        pool = [(r['id'], r['obs_a'], kinds['plans'][r['id']]['start']) for r in recs if r['actor'] == 1 and r['turn_count'] >= 1]
        s_inputs, _, s_kinds = seat1_inputs()
        pool += [(x['id'], x['pdl_observation'], s_kinds['plans'][x['id']]['start']) for x in s_inputs]
        for rid, ob, st in pool:
            tpl = ob['template']
            a = ob['actor']
            self.assertEqual(st['points'], [tpl['points'][a], tpl['points'][1 - a]], rid)
            self.assertEqual(st['me']['deck_size'], len(ob['known_own_deck']), rid)
            ez = tpl['energy_zone'][a]
            self.assertEqual(st['energy_zone'], [ez['current'], ez['next']], rid)
            n_seat1 += 1
        print('L6 seat-1 observations checked', n_seat1)
        self.assertGreaterEqual(n_seat1, 10)
        print('VMHWM_MAX', max(d['vmhwm_kb'] for d in kinds['stats'].values()))
        print('VMPEAK_MAX', max(d['vmpeak_kb'] for d in kinds['stats'].values()))

    def test_L9_seat1_attack_diffs(self):
        import re
        inputs, meta, kinds = seat1_inputs()
        n_plans, obs_used = 0, set()
        n_opp = n_you = n_pts = 0
        for rec in inputs:
            m = meta[rec['id']]
            if m['current_player'] != m['actor']:
                continue
            tpl = rec['pdl_observation']['template']
            boards = [json.dumps(tpl['in_play_pokemon'][side]) for side in (0, 1)]
            for p in kinds['plans'][rec['id']]['plans']:
                if p['end'] != 'attack':
                    continue
                n_plans += 1
                obs_used.add(rec['id'])
                for o in p['final'].get('outcomes', []):
                    for line in o['lines']:
                        mm = re.match(r'^(Opponent|You): (.+?) (\(Active\)|\(Bench \d\)|takes the)', line)
                        if mm:
                            if mm.group(1) == 'Opponent':
                                n_opp += 1
                            else:
                                n_you += 1
                            side = 0 if mm.group(1) == 'Opponent' else 1
                            self.assertIn(mm.group(2), boards[side], '%s: %s' % (rec['id'], cut(line)))
                        if line.startswith('Points:'):
                            pm = re.match(r'^Points: you (\d+) -> (\d+), opponent (\d+) -> (\d+)$', line)
                            self.assertIsNotNone(pm, line)
                            n_pts += 1
                            self.assertEqual(int(pm.group(1)), tpl['points'][1], line)
                            self.assertEqual(int(pm.group(3)), tpl['points'][0], line)
        print('L9 attack plans', n_plans, 'observations', len(obs_used))
        print('L9 matched lines: Opponent', n_opp, 'You', n_you, 'Points', n_pts)
        self.assertGreaterEqual(n_opp, 1)
        self.assertGreaterEqual(n_you, 1)
        self.assertGreaterEqual(n_pts, 1)
        self.assertGreaterEqual(n_plans, 3)
        self.assertGreaterEqual(len(obs_used), 2)

    def test_L10_relative_seats(self):
        import re
        inputs, meta, kinds = seat1_inputs()
        total = 0
        per_opp_state = {}

        def seat_pairs(lab, act, path, out, variant):
            if isinstance(lab, dict) and isinstance(act, dict):
                for k in lab:
                    if k in ('player', 'target_player', 'source_player') and isinstance(lab[k], int):
                        out.append((lab[k], act[k]))
                    elif k == 'attacking_ref':
                        out.append((lab[k][0], act[k][0]))
                    elif k in ('prior_knockouts', 'damaged_refs'):
                        out.extend((x[0], y[0]) for x, y in zip(lab[k], act[k]))
                    elif k == 'point_denial_flips':
                        out.extend((x[0][0], y[0][0]) for x, y in zip(lab[k], act[k]))
                    elif k == 'targets' and variant == 'ApplyDamage':
                        out.extend((x[1], y[1]) for x, y in zip(lab[k], act[k]))
                    else:
                        seat_pairs(lab[k], act[k], path + [k], out, variant)
            elif isinstance(lab, list) and isinstance(act, list):
                for x, y in zip(lab, act):
                    seat_pairs(x, y, path, out, variant)

        for rec in inputs:
            rid = rec['id']
            actor = rec['pdl_observation']['actor']
            acts = {pa['n']: pa['actions'] for pa in kinds['plan_actions'][rid]['plans']}
            n_here = 0
            for p in kinds['plans'][rid]['plans']:
                for lab, act in zip(p['labels'], acts[p['n']]):
                    pairs = []
                    mm = re.match(r'^(Promote|Activate):(\d+)@(\d+)$', lab)
                    if mm:
                        pairs.append((int(mm.group(2)), list(act['action'].values())[0]['player']))
                    elif '#' in lab and re.match(r'^[A-Za-z0-9_]+#', lab):
                        name, js = lab.split('#', 1)
                        variant = list(act['action'].keys())[0] if isinstance(act['action'], dict) else None
                        if variant != name:
                            continue
                        seat_pairs(json.loads(js), list(act['action'].values())[0], [], pairs, variant)
                    for labn, real in pairs:
                        want = 0 if real == actor else 1
                        self.assertEqual(labn, want, '%s label %s action seat %s actor %s' % (rid, cut(lab), real, actor))
                        n_here += 1
            total += n_here
            if meta[rid]['current_player'] != meta[rid]['actor']:
                per_opp_state[rid] = n_here
        print('L10 numbers checked', total, 'opponent-turn states with a number', sum(1 for v in per_opp_state.values() if v >= 1), 'of', len(per_opp_state))
        self.assertGreaterEqual(sum(1 for v in per_opp_state.values() if v >= 1), 2)
        self.assertGreaterEqual(total, 20)

    def test_L11_wrapper(self):
        import game_kit
        import game_lister
        import game_shadow
        from unittest import mock
        rec0 = exports('mini_positions.json', FIXTURES[0], FIXD, None)[1][0]
        tmpd = os.path.join(TMP, 'l11_tmp')
        os.makedirs(tmpd, exist_ok=True)
        before = set(os.listdir(tmpd))
        # recorded call
        calls = []

        def fake_run(argv, **kw):
            calls.append((argv, kw))
            raise subprocess.TimeoutExpired(argv, 1)
        L = game_lister.Lister('/bin/none', tmpd, mem_bytes=123456789, hang_s=1)
        with mock.patch('subprocess.run', fake_run):
            r = L.list('x', rec0['pdl_observation'], rec0['legal_actions'])
        self.assertEqual(r.reason, ('a', 'hang_guard_600s'))
        argv, kw = calls[0]
        self.assertEqual(argv[:4], ['prlimit', '--as=123456789', '--', '/bin/none'])
        self.assertNotIn('shell', kw)
        self.assertNotIn('preexec_fn', kw)
        self.assertIn('env', kw)
        self.assertEqual(kw['env'], game_shadow.shadow_env(os.environ))
        self.assertTrue(set(kw['env']) <= set(game_kit.SHADOW_ENV_KEEP))
        for k in kw['env']:
            self.assertFalse(k.startswith('VERTEX_') or k in game_kit.FORBIDDEN_ENV)
        # fake bins
        good = {'plans': {'kind': 'plans', 'id': 'x', 'capped': False, 'n_plans': 1, 'total_found': 1, 'nodes': 5, 'paths_cut_at_max_steps': 0,
                          'limits': game_kit.LISTER_LIMITS, 'plans': [{'n': 1}], 'start': {}},
                'plan_actions': {'kind': 'plan_actions', 'id': 'x', 'plans': [{'n': 1, 'key': 'k', 'actions': [], 'forced': []}]},
                'root_check': {'kind': 'root_check', 'id': 'x', 'ok': True},
                'pos_like': {'kind': 'pos_like', 'id': 'x', 'pos': {'turn_count': 1}},
                'stats': {'kind': 'stats', 'id': 'x', 'secs': 0.1, 'vmhwm_kb': 1, 'vmpeak_kb': 2, 'fill_seed': 1}}

        def fake_bin(name, lines=None, rc=0, pre='', post=''):
            lines = good if lines is None else lines
            path = os.path.join(TMP, 'fake_lister_%s.py' % name)
            with open(path, 'w') as f:
                f.write('#!/usr/bin/env python3\nimport sys, os, json, time\n' + pre + 'for d in %r:\n    print(json.dumps(d))\n' % list(lines.values()) + post + 'sys.exit(%d)\n' % rc)
            os.chmod(path, 0o755)
            return path

        def classify(path, hang=30):
            return game_lister.Lister(path, tmpd, hang_s=hang).list('x', rec0['pdl_observation'], rec0['legal_actions'])

        def mod(**over):
            d = json.loads(json.dumps(good))
            for k, v in over.items():
                d[k].update(v)
            return d
        self.assertEqual(classify(fake_bin('good')).ok, True)
        self.assertEqual(classify(fake_bin('sleep', pre='time.sleep(30)\n'), hang=1).reason, ('a', 'hang_guard_600s'))
        self.assertEqual(classify(fake_bin('mem', pre="sys.stderr.write('memory allocation of 8 bytes failed\\n')\nsys.stderr.flush()\nos.abort()\n")).reason, ('b', 'memory_cap'))
        self.assertEqual(classify(fake_bin('rc1', rc=1)).reason, ('a', 'lister_error'))
        self.assertEqual(classify(fake_bin('prob', lines={'problem': {'kind': 'problem', 'id': 'x', 'problems': ['m']}})).reason, ('a', 'lister_error'))
        noplans = {k: v for k, v in good.items() if k != 'plans'}
        self.assertEqual(classify(fake_bin('noplans', lines=noplans)).reason, ('a', 'lister_error'))
        nopos = {k: v for k, v in good.items() if k != 'pos_like'}
        self.assertEqual(classify(fake_bin('nopos', lines=nopos)).reason, ('a', 'lister_error'))
        self.assertEqual(classify(fake_bin('c1', lines=mod(plans={'capped': True, 'total_found': 5, 'n_plans': 2}))).reason, ('b', 'plans_over_2000'))
        self.assertEqual(classify(fake_bin('c2', lines=mod(plans={'capped': True, 'nodes': 200001}))).reason, ('b', 'node_cap'))
        self.assertEqual(classify(fake_bin('c3', lines=mod(plans={'capped': True, 'paths_cut_at_max_steps': 2}))).reason, ('b', 'step_cap'))
        self.assertEqual(classify(fake_bin('empty', lines=mod(plans={'n_plans': 0, 'total_found': 0}))).reason, ('a', 'empty'))
        self.assertEqual(classify(fake_bin('rootbad', lines=mod(root_check={'ok': False}))).reason, ('a', 'root_mismatch'))
        # the real binary
        real = game_lister.Lister(JP, tmpd).list(rec0['id'], rec0['pdl_observation'], rec0['legal_actions'])
        self.assertTrue(real.ok, str(real.reason) + cut(real.detail))
        self.assertEqual(real.rc, 0)
        self.assertEqual(set(real.pos_like), {"turn_count", "stadium", "turn_effects", "me", "opp"})
        self.assertEqual(set(os.listdir(tmpd)), before)


if __name__ == '__main__':
    unittest.main()
