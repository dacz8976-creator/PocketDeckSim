"""Gate 6: the pre-registered analysis (PREREG v3.1 section 6). Stage 2 only; it never sees a dev or stage-1 game."""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis  # noqa: E402
import game_kit  # noqa: E402

DROP_CLASSES = ('engine_error', 'kx3_route')
POLICY = {0: 'km3', 1: 'kx3'}


class Refused(Exception):
    pass


def power_line(n):
    return (1.959964 + 0.841621) * math.sqrt(0.5 / n)


def win_for(outcome, seat):
    """GameOutcome's serde form: {"Win": seat} or "Tie". A tie, the turn limit (a tie) and a loss are 0."""
    if isinstance(outcome, dict) and 'Win' in outcome:
        return 1 if outcome['Win'] == seat else 0
    return 0


def resample(rng, cell_values):
    """One bootstrap draw: within each cell (cells in order), resample with replacement keeping the cell's count."""
    return [rng.choices(cell_values[c], k=len(cell_values[c])) for c in sorted(cell_values)]


def bootstrap_ci(cell_values, draws=game_kit.BOOT_DRAWS, seed=game_kit.BOOT_SEED):
    rng = random.Random(seed)
    n = sum(len(v) for v in cell_values.values())
    means = sorted(sum(sum(x) for x in resample(rng, cell_values)) / n for _ in range(draws))
    return analysis.percentile_interval(means, 0.95)


def signflip_p(D, draws=game_kit.FLIP_DRAWS, seed=game_kit.SIGNFLIP_SEED):
    """Two-sided sign-flip test. Pairs in order; one getrandbits(n) per draw, bit i set flips pair i. A hit: |flipped sum| >= |observed sum| (integers, exact)."""
    rng = random.Random(seed)
    n = len(D)
    obs = abs(sum(D))
    nz = [(i, d) for i, d in enumerate(D) if d]
    hits = 0
    for _ in range(draws):
        bits = rng.getrandbits(n)
        s = 0
        for i, d in nz:
            s += -d if (bits >> i) & 1 else d
        if abs(s) >= obs:
            hits += 1
    return (1 + hits) / (draws + 1)


def _mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def _corr(a, b):
    if len(a) < 2:
        return None
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va, vb = sum((x - ma) ** 2 for x in a), sum((y - mb) ** 2 for y in b)
    if va == 0 or vb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(va * vb)


def _add(dst, src):
    for k, v in (src or {}).items():
        dst[k] = dst.get(k, 0) + v


def _group_mean(scored, keyfn):
    g = {}
    for d in scored:
        g.setdefault(keyfn(d), []).append(d['D'])
    return {str(k): {'n': len(v), 'mean': _mean(v)} for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


def analyse(deals, planned_deals, stopped_early):
    deals = sorted((dict(d) for d in deals), key=lambda d: d['deal_idx'])
    if stopped_early:
        by_k = {}
        for d in deals:
            by_k.setdefault(d['k'], set()).add(d['cell'])
        whole = {k for k, cells in by_k.items() if cells == set(range(16))}
        deals = [d for d in deals if d['k'] in whole]
    scored, dropped, dropped_by = [], [], {}
    for d in deals:
        causes = [(arm, d.get(arm.lower() + '_failure')) for arm in ('G', 'K')]
        causes = [(a, c) for a, c in causes if c in DROP_CLASSES]
        if causes:
            dropped.append(d)
            for a, c in causes:
                dropped_by['%s:%s' % (a, c)] = dropped_by.get('%s:%s' % (a, c), 0) + 1
            continue
        g = 0 if d.get('g_failure') == 'pilot_side' else d['g_win']
        d['D'] = g - d['k_win']
        d['g_eff'] = g
        scored.append(d)
    n_s, n_d = len(scored), len(dropped)
    D = [d['D'] for d in scored]
    interventions = sum(d.get('g_interventions', 0) for d in deals)
    fallbacks = sum(d.get('g_fallbacks', 0) for d in deals)
    rate = fallbacks / interventions if interventions else 0.0
    cells = {}
    for d in scored:
        cells.setdefault(d['cell'], []).append(d['D'])
    mean_d = sum(D) / n_s if n_s else None
    ci = list(bootstrap_ci(cells)) if n_s else None
    p = signflip_p(D) if n_s else None
    pol = {}
    for code, name in POLICY.items():
        pol[name] = _mean(d['D'] for d in scored if (d['cell'] >> 1) & 1 == code)
    if (n_d / (n_s + n_d) if (n_s + n_d) else 0) > game_kit.DROP_LIMIT or (stopped_early and len(deals) < game_kit.MIN_PAIRS):
        label = 'not testable'
    elif rate > game_kit.FALLBACK_LIMIT:
        label = 'pilot not tested'
    elif n_s < game_kit.MIN_PAIRS:
        label = 'too few deals'
    elif ci[0] > 0 and p < 0.05 and all(v is not None and v > 0 for v in pol.values()):
        label = 'PASS / judge higher'
    elif ci[1] < 0 and p < 0.05:
        label = 'kx3 higher'
    else:
        label = 'inconclusive'
    g_w = [d['g_eff'] for d in scored]
    k_w = [d['k_win'] for d in scored]
    by_reason, reasks, setup, by_seat = {}, {}, 0, {}
    per_game = []
    for d in deals:
        _add(by_reason, d.get('g_fallbacks_by_reason'))
        _add(reasks, d.get('g_reasks_by_reason'))
        setup += d.get('setup_decisions', 0)
        seat = d['cell'] & 1
        s = by_seat.setdefault(str(seat), {'decisions': 0, 'interventions': 0, 'fallbacks': 0})
        s['decisions'] += d.get('decisions', 0)
        s['interventions'] += d.get('g_interventions', 0)
        s['fallbacks'] += d.get('g_fallbacks', 0)
        iv = d.get('g_interventions', 0)
        per_game.append({'deal_idx': d['deal_idx'], 'cell': d['cell'], 'interventions': iv, 'fallbacks': d.get('g_fallbacks', 0),
                         'rate': d.get('g_fallbacks', 0) / iv if iv else 0.0, 'by_reason': d.get('g_fallbacks_by_reason') or {}})
    opt = lambda key: _mean(d[key] for d in scored if d.get(key) is not None)
    desc = {'by_deck': _group_mean(scored, lambda d: (d['cell'] >> 3) & 1), 'by_policy': _group_mean(scored, lambda d: POLICY[(d['cell'] >> 1) & 1]),
            'by_seat': _group_mean(scored, lambda d: d['cell'] & 1), 'by_went_first': _group_mean([d for d in scored if d.get('went_first') is not None], lambda d: d['went_first']),
            'concordance': _mean(1 if a == b else 0 for a, b in zip(g_w, k_w)), 'pair_correlation': _corr(g_w, k_w),
            'game_length': {'plies_mean': opt('plies'), 'final_turn_mean': opt('final_turn')},
            'per_game_means': {'calls': opt('calls'), 'tries': opt('tries'), 'g_seconds': opt('g_seconds'), 'k_seconds': opt('k_seconds'), 'actual_usd': opt('actual_usd'),
                               'ledger_charge_usd': opt('ledger_charge_usd')},
            'fallbacks_by_reason': by_reason, 'reasks_by_reason': reasks, 'fallbacks_per_game': per_game, 'by_pilot_seat': by_seat, 'setup_decisions': setup,
            'dropped_by_arm_reason': dropped_by}
    return {'label': label, 'scored': n_s, 'dropped': n_d, 'planned': planned_deals, 'stopped_early': bool(stopped_early), 'mean_d': mean_d, 'ci': ci, 'p': p,
            'policy_means': pol, 'fallback_rate': rate, 'dropped_by': dropped_by,
            'power_line': {'planned': power_line(planned_deals) if planned_deals else None, 'scored': power_line(n_s) if n_s else None}, 'descriptive': desc}


# ------------------------------------------------------------------------------------------------ run-dir reader
def _read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def read_run_dir(d):
    end_path = os.path.join(d, 'run_end.json')
    if not os.path.exists(end_path):
        raise Refused('no run_end.json: the run has not ended (no interim looks)')
    with open(end_path) as f:
        end = json.load(f)
    st = end.get('stage')
    if not (isinstance(st, int) and not isinstance(st, bool) and st == 2):
        raise Refused('the run_end stage is %r, not 2' % (st,))
    rows = _read_jsonl(os.path.join(d, 'deals.jsonl'))
    arms = {r['deal_tag']: r for r in _read_jsonl(os.path.join(d, 'games.jsonl'))}
    best = {}
    for r in rows:
        if r.get('complete') and (r['deal_idx'] not in best or r['attempt'] > best[r['deal_idx']]['attempt']):
            best[r['deal_idx']] = r
    out = []
    for idx in sorted(best):
        r = best[idx]
        if not 0 <= r['k'] <= 7:
            raise Refused('a deal at k=%s is outside 0-7' % r['k'])
        g, k = arms.get(r['g_deal_tag']), arms.get(r['k_deal_tag'])
        if g is None or k is None:
            raise Refused('a deal row names an arm row that is missing')
        if (g.get('judge') or {}).get('mock'):
            raise Refused('a G arm row has judge.mock true')
        seat = r['bits']['seat']

        def win(arm):
            rf = arm.get('result_file')
            if not rf:
                return 0, None
            path = rf if os.path.isabs(rf) else os.path.join(d, rf)
            if not os.path.exists(path):
                return 0, None
            with open(path) as f:
                res = json.load(f)
            return win_for(res.get('outcome'), seat), res
        gw, gres = win(g)
        kw, _ = win(k)
        j = g.get('judge') or {}
        out.append({'deal_idx': idx, 'k': r['k'], 'cell': r['cell'], 'g_win': gw, 'k_win': kw, 'g_failure': r.get('g_failure'), 'k_failure': r.get('k_failure'),
                    'g_interventions': j.get('interventions', 0), 'g_fallbacks': j.get('fallbacks', 0), 'setup_decisions': j.get('setup_decisions', 0), 'decisions': j.get('decisions', 0),
                    'went_first': j.get('went_first'), 'calls': j.get('calls'), 'tries': j.get('tries'), 'g_seconds': g.get('seconds'), 'k_seconds': k.get('seconds'),
                    'actual_usd': j.get('actual_usd'), 'ledger_charge_usd': j.get('ledger_charge_usd'), 'plies': g.get('plies', (gres or {}).get('plies')),
                    'final_turn': g.get('final_turn', (gres or {}).get('final_turn')), 'g_fallbacks_by_reason': j.get('fallbacks_by_reason'), 'g_reasks_by_reason': j.get('reasks_by_reason')})
    return out, end.get('planned_deals', len(rows)), bool(end.get('stopped_early'))


# ------------------------------------------------------------------------------------------------ the gate 6 data sets
def _set(f, n_k=5, **kw):
    out = []
    for k in range(n_k):
        for cell in range(16):
            D = f(k, cell)
            g, kk = (1, 0) if D == 1 else (0, 1) if D == -1 else (0, 0)
            d = {'deal_idx': 16 * k + cell, 'k': k, 'cell': cell, 'g_win': g, 'k_win': kk, 'g_failure': None, 'k_failure': None, 'g_interventions': 20, 'g_fallbacks': 0}
            d.update(kw)
            out.append(d)
    return out


_EVEN = [1, 1, 1, -1, 0]
_ODD = [1, 1, -1, 0, 0]
_NULL_EVEN = [1, 1, -1, -1, 0]
_NULL_ODD = [1, -1, 0, 0, 0]


def self_test_sets():
    """name -> (deals, planned_deals, stopped_early, expected label)"""
    plus = lambda k, c: _EVEN[k] if c % 2 == 0 else _ODD[k]
    null = lambda k, c: _NULL_EVEN[k] if c % 2 == 0 else _NULL_ODD[k]
    sets = {'Y1': (_set(lambda k, c: 1), 80, False, 'PASS / judge higher'), 'Y2': (_set(lambda k, c: 0), 80, False, 'inconclusive'),
            'Y3': (_set(lambda k, c: -1), 80, False, 'kx3 higher'), 'Y4': (_set(lambda k, c: 1 if (c >> 1) & 1 == 0 else 0), 80, False, 'inconclusive')}

    def with_drops(n_eng, n_route):
        ds = _set(lambda k, c: 1)
        for i in range(n_eng):
            ds[i]['g_failure'] = 'engine_error'
        for i in range(n_route):
            ds[n_eng + i]['k_failure'] = 'kx3_route'
        return ds
    sets['Y5a'] = (with_drops(3, 2), 80, False, 'not testable')
    sets['Y5b'] = (with_drops(2, 2), 80, False, 'PASS / judge higher')
    sets['Y6'] = (_set(lambda k, c: 1, g_interventions=100, g_fallbacks=11), 80, False, 'pilot not tested')
    sets['Y7a'] = (_set(lambda k, c: 1, n_k=3), 48, False, 'too few deals')
    sets['Y7b'] = (_set(lambda k, c: 1, n_k=3), 80, True, 'not testable')
    sets['Y12'] = (with_drops(8, 0), 80, False, 'not testable')
    sets['Y14'] = (_set(lambda k, c: 1, g_failure='pilot_side'), 80, False, 'inconclusive')
    sets['Y15'] = (_set(plus), 80, False, 'PASS / judge higher')
    sets['Y16'] = (_set(null), 80, False, 'inconclusive')
    sets['Y17'] = (_set(lambda k, c: -plus(k, c)), 80, False, 'kx3 higher')
    sets['Y18'] = (_set(lambda k, c: 1, g_interventions=100, g_fallbacks=9, setup_decisions=5), 80, False, 'PASS / judge higher')
    return sets


def self_test():
    ok = True
    for name, (deals, planned, stopped, expect) in self_test_sets().items():
        label = analyse(deals, planned, stopped)['label']
        good = label == expect
        ok = ok and good
        print('%s: %s %s' % (name, label, 'OK' if good else 'MISMATCH (expected %s)' % expect))
    for n, want in ((80, 0.22148), (96, 0.20219), (128, 0.17510)):
        good = abs(power_line(n) - want) < 0.0001
        ok = ok and good
        print('Y11 power_line(%d): %.5f %s' % (n, power_line(n), 'OK' if good else 'MISMATCH'))
    f = analyse(*self_test_sets()['Y15'][:3])
    n = analyse(*self_test_sets()['Y17'][:3])
    z = analyse(*self_test_sets()['Y16'][:3])
    checks = {'Y15 mean 0.3': f['mean_d'] == 0.3, 'Y16 p 1.0': z['p'] == 1.0 and z['mean_d'] == 0, 'Y17 p equals Y15 p': n['p'] == f['p']}
    for k, v in checks.items():
        ok = ok and v
        print('%s: %s' % (k, 'OK' if v else 'MISMATCH'))
    print('GATE6 PASS' if ok else 'GATE6 FAIL')
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(prog='game_analysis')
    p.add_argument('--run-dir')
    p.add_argument('--mock-data')
    p.add_argument('--out')
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args(argv)
    if a.self_test:
        return self_test()
    try:
        if a.run_dir:
            deals, planned, stopped = read_run_dir(a.run_dir)
        elif a.mock_data:
            with open(a.mock_data) as f:
                m = json.load(f)
            deals, planned, stopped = m['deals'], m['planned_deals'], m['stopped_early']
        else:
            print('REFUSED: give --run-dir, --mock-data or --self-test')
            return 2
    except Refused as e:
        print('REFUSED: ' + str(e)[:300])
        return 2
    if not a.out:
        print('REFUSED: --out is required')
        return 2
    r = analyse(deals, planned, stopped)
    with open(a.out, 'w') as f:
        json.dump(r, f, indent=1, sort_keys=True)
    print('scored %d, dropped %d, planned %s, mean D %s, CI %s, p %s' % (r['scored'], r['dropped'], r['planned'], r['mean_d'], r['ci'], r['p']))
    print('LABEL: ' + r['label'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
