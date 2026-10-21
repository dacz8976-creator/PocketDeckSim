#!/usr/bin/env python3
"""Exam run 3's PRIMARY (PREREG_RUN3.md section 4): runs 2 + 3 POOLED, Gemini minus km3, prefix agreement, game-clustered.

  pool_runs.py --analysis PATH/analysis.py --run REPORT ELIGIBILITY [--run REPORT ELIGIBILITY ...]
               [--confidence 0.975] [--judge-rows FILE ...] [--stratum IDS_FILE] --out OUT.json

It uses frozen-7's analysis.py (refused unless its sha256 is frozen-7's) exactly as the formal compare does for one run's prefix block:
- each run's per-decision values come from its formal report's rows through analysis.decision_values (the judge's one predefined call, repeat 0;
  km3: the mean over its 3 seeds; a failed judge reply scored as a miss arrives with agrees False);
- the decisions are each run's primary_ids; the cluster is the game (each run's eligibility `games`); the runs' games and point ids must not overlap;
- the series are built as analysis._block builds them (one entry per game in sorted game order: per-game sums and counts);
- analysis.game_bootstrap with the level PASSED IN (analysis.RESAMPLES draws, seed analysis.SEED), analysis.sign_flip_p (seed analysis.SEED, Monte Carlo
  beyond 16 games), and analysis.verdict's rule at the same level: a direction needs the interval to exclude 0 AND the sign-flip p < 1 - level, with at least
  analysis.MIN_GAMES games.
PASS (section 4) = verdict "judge higher" at --confidence 0.975.
`--judge-rows`: every judge rows file of the runs; the model a reply names must be the same everywhere, or pooling is off (section 7) and nothing is computed.
`--stratum`: a file of point ids; the same computation restricted to them is reported as a secondary (no PASS from it).
Test: on run 2 alone at --confidence 0.95 it must give run 2's report_primary.json prefix contrast to the printed digits (test_pool_runs.py)."""
import argparse, hashlib, importlib.util, json, sys

FROZEN7_ANALYSIS_SHA256 = '64f78cbd7f6d1bbf991387f9779b6e41dbf2c6fa8da44e2aad29bbb869f176fa'
BOTS = ['km3', 'judge']
A_NAME, B_NAME = 'judge', 'km3'


def load_analysis(path):
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    if sha != FROZEN7_ANALYSIS_SHA256:
        sys.exit(f'{path}: sha256 {sha[:12]} is not frozen-7 analysis.py ({FROZEN7_ANALYSIS_SHA256[:12]}): refused')
    spec = importlib.util.spec_from_file_location('analysis_frozen7', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pooled_values(A, runs):
    """(vals {bot: {pid: (primary, sens, nums)}}, games {pid: game}, pids [primary ids of every run])."""
    vals, games, pids, seen_games = {b: {} for b in BOTS}, {}, [], {}
    for label, report_path, elig_path in runs:
        rep = json.load(open(report_path, encoding='utf-8'))
        if rep.get('status') != 'complete' or rep.get('formal') is not True or rep.get('problems'):
            sys.exit(f'{report_path}: not a complete formal report with no problems: refused')
        e = json.load(open(elig_path, encoding='utf-8'))
        prim = list(e['primary_ids'])
        v = A.decision_values(rep['rows'], BOTS, 1)
        for p in prim:
            if p in games:
                sys.exit(f'point {p} appears in two runs')
            g = e['games'][p]
            if g in seen_games and seen_games[g] != label:
                sys.exit(f'game {g} appears in runs {seen_games[g]} and {label}: the runs must be different games')
            seen_games[g] = label
            games[p] = g
            for b in BOTS:
                if p not in v[b]:
                    sys.exit(f'{label}: no {b} value for primary point {p}')
                vals[b][p] = v[b][p]
            pids.append(p)
    return vals, games, pids


def contrast(A, vals, games, pids, confidence):
    game_list = sorted({games[p] for p in pids})
    pos_by_game = {g: [p for p in pids if games[p] == g] for g in game_list}
    get = lambda b, p: vals[b][p][0]
    series = {}

    def add(name, fn):
        sums, counts = [], []
        for g in game_list:
            xs = [x for x in (fn(p) for p in pos_by_game[g]) if x is not None]
            sums.append(sum(xs))
            counts.append(len(xs))
        series[name] = (sums, counts)

    for b in BOTS:
        add(f'rate:{b}', lambda p, b=b: get(b, p))
    add(f'diff:{A_NAME}-{B_NAME}', lambda p: None if get(A_NAME, p) is None or get(B_NAME, p) is None else get(A_NAME, p) - get(B_NAME, p))
    est = A.game_bootstrap(series, A.RESAMPLES, A.SEED, confidence)
    r6 = lambda x: None if x is None else round(x, 6)

    def block(name):
        point, lo, hi = est[name]
        counts = series[name][1]
        n_games = sum(1 for c in counts if c)
        if n_games < 2:
            lo = hi = None
        return {'estimate': r6(point), 'ci_low': r6(lo), 'ci_high': r6(hi), 'n_decisions': sum(counts), 'n_games': n_games}

    name = f'diff:{A_NAME}-{B_NAME}'
    out = {'a': A_NAME, 'b': B_NAME, **block(name), 'n_pairs_dropped': len(pids) - sum(series[name][1])}
    sums, counts = series[name]
    gsums = [s for s, c in zip(sums, counts) if c]
    gcounts = [c for c in counts if c]
    point, lo, hi = est[name]
    n_games = len(gsums)
    if gsums and point is not None:
        p_flip, how = A.sign_flip_p(gsums, A.SEED)
        out['sign_flip_p'], out['sign_flip'] = round(p_flip, 6), how
        if n_games < A.MIN_GAMES:
            out['verdict'], out['reason'] = 'inconclusive', f'{n_games} games < {A.MIN_GAMES}'
        elif lo is None or hi is None:
            out['verdict'], out['reason'] = 'inconclusive', 'no usable interval'
        elif lo <= 0 <= hi:
            out['verdict'], out['reason'] = 'inconclusive', 'the interval includes 0'
        elif p_flip >= 1.0 - confidence:
            out['verdict'], out['reason'] = 'inconclusive', f'the interval excludes 0 but the sign-flip p = {p_flip:.6f} is not < {1.0 - confidence:.3f}'
        else:
            out['verdict'] = f'{A_NAME} higher' if lo > 0 else f'{B_NAME} higher'
            out['reason'] = 'the interval excludes 0 and the sign-flip test agrees' + (
                ' (every game gave the same difference)' if max(gsums) - min(gsums) <= 1e-12 and len(set(gcounts)) == 1 else '')
    else:
        out['verdict'], out['reason'] = 'inconclusive', 'no decision is comparable for both bots'
    return {'rates': {b: block(f'rate:{b}') for b in BOTS}, 'contrast': out,
            'population': {'n_decisions': len(pids), 'n_games': len(game_list)}}


def model_check(files):
    models = {}
    for f in files:
        for line in open(f, encoding='utf-8'):
            if line.strip():
                r = json.loads(line)
                m = r.get('model_returned') or r.get('model')
                models.setdefault(m, 0)
                models[m] += 1
    return models


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--analysis', required=True)
    p.add_argument('--run', nargs=2, action='append', required=True, metavar=('REPORT', 'ELIGIBILITY'))
    p.add_argument('--confidence', type=float, default=0.975)
    p.add_argument('--judge-rows', nargs='*', default=[])
    p.add_argument('--stratum')
    p.add_argument('--out', required=True)
    a = p.parse_args(argv)
    A = load_analysis(a.analysis)
    res = {'schema': 'exam_pooled_primary_v1', 'confidence': a.confidence, 'runs': [{'report': r, 'eligibility': e} for r, e in a.run],
           'method': {'resamples': A.RESAMPLES, 'bootstrap_seed': A.SEED, 'sign_flip_seed': A.SEED + 1, 'sign_flip_draws': A.SIGN_FLIP_DRAWS,
                      'exact_up_to_games': A.SIGN_FLIP_EXACT_MAX_GAMES, 'min_games': A.MIN_GAMES, 'analysis_sha256': FROZEN7_ANALYSIS_SHA256}}
    if a.judge_rows:
        models = model_check(a.judge_rows)
        res['judge_models'] = models
        if len(models) != 1:
            res['pooling'] = 'OFF: the judge rows name more than one model (PREREG_RUN3 section 7)'
            json.dump(res, open(a.out, 'w'), indent=1)
            print(res['pooling'], models)
            return 3
    runs = [(f'run{i + 1}', r, e) for i, (r, e) in enumerate(a.run)]
    vals, games, pids = pooled_values(A, runs)
    res['primary'] = contrast(A, vals, games, pids, a.confidence)
    res['primary']['pass'] = res['primary']['contrast']['verdict'] == f'{A_NAME} higher'
    if a.stratum:
        ids = {l.strip() for l in open(a.stratum) if l.strip()}
        sp = [x for x in pids if x in ids]
        res['stratum'] = {'file': a.stratum, 'what': 'secondary, no PASS from it', **contrast(A, vals, games, sp, a.confidence)}
    json.dump(res, open(a.out, 'w'), indent=1)
    c = res['primary']['contrast']
    print(f"pooled at {a.confidence}: {res['primary']['population']}; judge - km3 {c['estimate']} [{c['ci_low']}, {c['ci_high']}], "
          f"sign-flip p {c.get('sign_flip_p')} ({c.get('sign_flip')}); verdict {c['verdict']} ({c['reason']}); PASS {res['primary']['pass']}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
