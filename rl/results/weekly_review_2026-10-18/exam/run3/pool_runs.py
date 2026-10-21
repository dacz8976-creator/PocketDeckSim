#!/usr/bin/env python3
"""Exam run 3's PRIMARY (PREREG_RUN3.md section 4): runs 2 + 3 POOLED, Gemini minus km3, prefix agreement, game-clustered.

  pool_runs.py --analysis PATH/analysis.py --run REPORT ELIGIBILITY [--run REPORT ELIGIBILITY ...]
               [--confidence 0.975] [--stratum IDS_FILE] --out OUT.json

It uses frozen-7's analysis.py (refused unless its sha256 is frozen-7's) exactly as the formal compare does for one run's prefix block:
- each run's per-decision values come from its formal report's rows through analysis.decision_values (the judge's one predefined call, repeat 0;
  km3: the mean over its 3 seeds; a failed judge reply scored as a miss arrives with agrees False);
- the decisions are each run's primary_ids; the cluster is the game (each run's eligibility `games`); the runs' games and point ids must not overlap;
- the series are built as analysis._block builds them (one entry per game in sorted game order: per-game sums and counts);
- analysis.game_bootstrap with the level PASSED IN (analysis.RESAMPLES draws, seed analysis.SEED), analysis.sign_flip_p (seed analysis.SEED, Monte Carlo
  beyond 16 games), and analysis.verdict's rule at the same level: a direction needs the interval to exclude 0 AND the sign-flip p < 1 - level, with at least
  analysis.MIN_GAMES games. The interval test is made with a 1e-9 margin, so float noise around an exact 0 never counts as excluding 0.
PASS (section 4) = verdict "judge higher" at --confidence 0.975 (at any other level `pass` is null).
Each run is checked before pooling, or refused:
- its report is complete, formal, with no problems; frozen-7's tag and prompt fingerprint; request bots km3 + judge, 3 km3 seeds, failed replies 'miss',
  analysis.RESAMPLES resamples and analysis.MIN_GAMES; no km3 seed is shared with another run;
- the eligibility file is the one the report was made from (its sha256 = run.inputs.eligibility_sha256); the report's row positions are exactly its
  primary_ids, every row's game is the eligibility's game, and each point has exactly the 3 km3 seed rows and 1 judge repeat-0 row;
- on that run alone at 0.95 this script gives the report's own prefix contrast and rates to the printed digits.
Section 7: the judge models the reports returned (run.judge_models_returned) must be one model, the frozen one (gemini-4-argon, run 2's), and no report
warns about model versions; otherwise pooling is OFF (exit 3) and nothing is computed.
Section 6: the failed judge replies (state 'no_choice', scored as a miss) are counted per run and pooled, with their share and the > 20% flag.
`--stratum`: a file of point ids (a non-empty subset of the pooled primary ids); the same computation restricted to them is reported as a secondary,
descriptive only (no verdict, no PASS).
Test: test_pool_runs.py (on run 2 alone at --confidence 0.95 it gives run 2's report_primary.json prefix contrast to the printed digits; refusals)."""
import argparse, hashlib, importlib.util, json, os, sys

FROZEN7_ANALYSIS_SHA256 = '64f78cbd7f6d1bbf991387f9779b6e41dbf2c6fa8da44e2aad29bbb869f176fa'
FROZEN7_TAG = 'judge-prompt-frozen-7'
FROZEN7_FINGERPRINT = '0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762'
FROZEN_MODEL = 'gemini-4-argon'  # run 2's run.judge_models_returned
PASS_LEVEL = 0.975
FAILED_SHARE_LIMIT = 0.20
EPS = 1e-9
BOTS = ['km3', 'judge']
A_NAME, B_NAME = 'judge', 'km3'


def load_analysis(path):
    with open(path, 'rb') as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    if sha != FROZEN7_ANALYSIS_SHA256:
        sys.exit(f'{path}: sha256 {sha[:12]} is not frozen-7 analysis.py ({FROZEN7_ANALYSIS_SHA256[:12]}): refused')
    spec = importlib.util.spec_from_file_location('analysis_frozen7', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gkey(g):
    return g.strip().casefold()


def load_run(A, label, report_path, elig_path):
    """The run's report and eligibility, checked against each other and against the freeze (refused otherwise)."""
    with open(report_path, encoding='utf-8') as f:
        rep = json.load(f)
    with open(elig_path, 'rb') as f:
        elig_bytes = f.read()
    e = json.loads(elig_bytes.decode('utf-8'))
    bad = lambda why: sys.exit(f'{label} ({report_path}): {why}: refused')
    if rep.get('status') != 'complete' or rep.get('formal') is not True or rep.get('problems'):
        bad('not a complete formal report with no problems')
    run = rep.get('run') or {}
    fr, rq = run.get('freeze') or {}, run.get('request') or {}
    if fr.get('tag') != FROZEN7_TAG or fr.get('fingerprint_now') != FROZEN7_FINGERPRINT or fr.get('fingerprint_frozen') != FROZEN7_FINGERPRINT:
        bad(f"not made under {FROZEN7_TAG} (tag {fr.get('tag')}, fingerprint {str(fr.get('fingerprint_now'))[:12]})")
    bots = set(str(rq.get('bots', '')).split(','))
    seeds = rq.get('seeds') or []
    if not set(BOTS) <= bots or len(seeds) != 3 or len(set(seeds)) != 3 or rq.get('failed_judge_rows') != 'miss' \
            or rq.get('resamples') != A.RESAMPLES or rq.get('min_games') != A.MIN_GAMES:
        bad(f'the request is not section 6\'s (bots {rq.get("bots")}, seeds {seeds}, failed rows {rq.get("failed_judge_rows")}, '
            f'resamples {rq.get("resamples")}, min games {rq.get("min_games")})')
    if hashlib.sha256(elig_bytes).hexdigest() != (run.get('inputs') or {}).get('eligibility_sha256'):
        bad(f'{elig_path} is not the eligibility file the report was made from (sha256 differs from run.inputs.eligibility_sha256)')
    prim = list(e['primary_ids'])
    if len(set(prim)) != len(prim):
        bad('a primary id is listed twice')
    rows = rep['rows']
    if {r['position'] for r in rows} != set(prim):
        bad("the report's row positions are not exactly the eligibility's primary_ids")
    per = {p: {'km3': [], 'judge': []} for p in prim}
    for r in rows:
        if r['game'] != e['games'].get(r['position']):
            bad(f"row {r['position']}: game {r['game']} is not the eligibility's {e['games'].get(r['position'])}")
        if r['bot'] in per[r['position']]:
            per[r['position']][r['bot']].append(r['run'])
    for p, d in per.items():
        if sorted(d['km3']) != sorted(seeds) or d['judge'].count(A.PRIMARY_JUDGE_RUN) != 1:
            bad(f'point {p}: km3 seed rows {sorted(d["km3"])}, judge repeat-{A.PRIMARY_JUDGE_RUN} rows {d["judge"].count(A.PRIMARY_JUDGE_RUN)} '
                f'(want the 3 seeds and 1)')
    return rep, e, prim, seeds


def run_values(A, label, rep, e, prim):
    v = A.decision_values(rep['rows'], BOTS, 1)
    vals, games = {b: {} for b in BOTS}, {}
    for p in prim:
        games[p] = e['games'][p]
        for b in BOTS:
            if p not in v[b]:
                sys.exit(f'{label}: no {b} value for primary point {p}')
            vals[b][p] = v[b][p]
    return vals, games


def failed_replies(rep, prim, A):
    n = sum(1 for r in rep['rows'] if r['bot'] == 'judge' and r['run'] == A.PRIMARY_JUDGE_RUN and r['state'] == 'no_choice' and r['position'] in set(prim))
    return n


def contrast(A, vals, games, pids, confidence, verdict=True):
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
        if not verdict:
            pass
        elif n_games < A.MIN_GAMES:
            out['verdict'], out['reason'] = 'inconclusive', f'{n_games} games < {A.MIN_GAMES}'
        elif lo is None or hi is None:
            out['verdict'], out['reason'] = 'inconclusive', 'no usable interval'
        elif lo <= EPS and hi >= -EPS:
            out['verdict'], out['reason'] = 'inconclusive', 'the interval includes 0'
        elif p_flip >= 1.0 - confidence:
            out['verdict'], out['reason'] = 'inconclusive', f'the interval excludes 0 but the sign-flip p = {p_flip:.6f} is not < {1.0 - confidence:.3f}'
        else:
            out['verdict'] = f'{A_NAME} higher' if lo > EPS else f'{B_NAME} higher'
            out['reason'] = 'the interval excludes 0 and the sign-flip test agrees' + (
                ' (every game gave the same difference)' if max(gsums) - min(gsums) <= 1e-12 and len(set(gcounts)) == 1 else '')
    elif verdict:
        out['verdict'], out['reason'] = 'inconclusive', 'no decision is comparable for both bots'
    return {'rates': {b: block(f'rate:{b}') for b in BOTS}, 'contrast': out,
            'population': {'n_decisions': len(pids), 'n_games': len(game_list)}}


def self_check(A, label, rep, vals, games, prim):
    """On this run alone at 0.95, the script must give the report's own prefix contrast and rates to the printed digits."""
    got = contrast(A, vals, games, prim, 0.95)
    want = rep['analysis']['prefix']
    wc = want['contrasts'][0]
    if (wc.get('a'), wc.get('b')) != (A_NAME, B_NAME):
        sys.exit(f'{label}: the report\'s first prefix contrast is {wc.get("a")} - {wc.get("b")}, not {A_NAME} - {B_NAME}: refused')
    keys = ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games', 'sign_flip_p', 'sign_flip')
    diff = [k for k in keys if got['contrast'].get(k) != wc.get(k)]
    diff += [f'{b}.{k}' for b in BOTS for k in ('estimate', 'ci_low', 'ci_high', 'n_decisions', 'n_games') if got['rates'][b][k] != want['rates'][b][k]]
    if diff:
        sys.exit(f'{label}: alone at 0.95 this script does not give the report\'s own numbers ({", ".join(diff)}): refused')
    return {k: wc.get(k) for k in keys + ('verdict',)}


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--analysis', required=True)
    p.add_argument('--run', nargs=2, action='append', required=True, metavar=('REPORT', 'ELIGIBILITY'))
    p.add_argument('--confidence', type=float, default=PASS_LEVEL)
    p.add_argument('--stratum')
    p.add_argument('--out', required=True)
    a = p.parse_args(argv)
    if not 0.5 < a.confidence < 1.0:
        sys.exit(f'--confidence {a.confidence} is outside (0.5, 1): refused')
    A = load_analysis(a.analysis)
    labels = [os.path.basename(os.path.dirname(os.path.abspath(r))) or r for r, _ in a.run]
    labels = [f'{l} (#{i + 1})' for i, l in enumerate(labels)]
    res = {'schema': 'exam_pooled_primary_v2', 'confidence': a.confidence,
           'runs': [{'label': l, 'report': r, 'eligibility': e} for l, (r, e) in zip(labels, a.run)],
           'method': {'resamples': A.RESAMPLES, 'bootstrap_seed': A.SEED, 'sign_flip_seed': A.SEED + 1, 'sign_flip_draws': A.SIGN_FLIP_DRAWS,
                      'exact_up_to_games': A.SIGN_FLIP_EXACT_MAX_GAMES, 'min_games': A.MIN_GAMES, 'analysis_sha256': FROZEN7_ANALYSIS_SHA256,
                      'zero_margin': EPS, 'pass_level': PASS_LEVEL}}
    loaded = []
    for l, (r, e) in zip(labels, a.run):
        loaded.append((l, *load_run(A, l, r, e)))
    models, warn = set(), []
    for l, rep, *_ in loaded:
        ms = rep['run'].get('judge_models_returned')
        models.update(ms if isinstance(ms, list) and ms else [None])
        warn += [f'{l}: {w}' for w in rep['run'].get('warnings') or [] if 'model' in str(w).lower()]
    res['judge_models'] = sorted(models, key=str)
    if models != {FROZEN_MODEL} or warn:
        res['pooling'] = ('OFF: the runs\' judge replies name ' + (f'models {res["judge_models"]}, not only {FROZEN_MODEL}' if models != {FROZEN_MODEL}
                                                                    else 'one model, but a report warns about model versions')
                          + ' (PREREG_RUN3 section 7)')
        res['model_warnings'] = warn
        with open(a.out, 'w') as f:
            json.dump(res, f, indent=1)
        print(res['pooling'])
        return 3
    seen_seed = {}
    for l, rep, e, prim, seeds in loaded:
        for s in seeds:
            if s in seen_seed:
                sys.exit(f'km3 seed {s} appears in two runs ({seen_seed[s]} and {l}): each run needs its own seeds')
            seen_seed[s] = l
    vals, games, pids, seen_games, per_run = {b: {} for b in BOTS}, {}, [], {}, []
    for l, rep, e, prim, seeds in loaded:
        v, g = run_values(A, l, rep, e, prim)
        own = self_check(A, l, rep, v, g, prim)
        n_failed = failed_replies(rep, prim, A)
        if n_failed != (rep.get('failed_judge_rows') or {}).get('n_primary_decisions', n_failed):
            sys.exit(f'{l}: {n_failed} failed primary judge replies in the rows, the report says {rep["failed_judge_rows"]["n_primary_decisions"]}: refused')
        for pt in prim:
            if pt in games:
                sys.exit(f'point {pt} appears in two runs')
            k = gkey(g[pt])
            if k in seen_games and seen_games[k] != l:
                sys.exit(f'game {g[pt]} appears in runs {seen_games[k]} and {l}: the runs must be different games')
            seen_games[k] = l
            games[pt] = g[pt]
            for b in BOTS:
                vals[b][pt] = v[b][pt]
            pids.append(pt)
        per_run.append({'label': l, 'n_decisions': len(prim), 'n_games': len({g[x] for x in prim}), 'km3_seeds': seeds,
                        'failed_replies': {'n': n_failed, 'share': round(n_failed / len(prim), 6), 'over_20pct': n_failed / len(prim) > FAILED_SHARE_LIMIT},
                        'alone_at_0.95_equals_its_report': own})
    res['per_run'] = per_run
    res['primary'] = contrast(A, vals, games, pids, a.confidence)
    n_failed = sum(r['failed_replies']['n'] for r in per_run)
    res['primary']['failed_replies'] = {'n': n_failed, 'share': round(n_failed / len(pids), 6), 'over_20pct': n_failed / len(pids) > FAILED_SHARE_LIMIT}
    res['primary']['pass'] = (res['primary']['contrast']['verdict'] == f'{A_NAME} higher') if a.confidence == PASS_LEVEL else None
    if a.stratum:
        with open(a.stratum) as f:
            ids = [x.strip() for x in f if x.strip()]
        missing = sorted(set(ids) - set(pids))
        if not ids or missing:
            sys.exit(f'{a.stratum}: the stratum must be a non-empty subset of the pooled primary ids ({len(missing)} not among them, e.g. {missing[:3]}): refused')
        sp = [x for x in pids if x in set(ids)]
        by_run = {r['label']: 0 for r in per_run}
        for l, rep, e, prim, seeds in loaded:
            by_run[l] = sum(1 for x in prim if x in set(ids))
        res['stratum'] = {'file': a.stratum, 'what': 'secondary, descriptive only: no verdict, no PASS', 'n_by_run': by_run,
                          **contrast(A, vals, games, sp, a.confidence, verdict=False)}
    with open(a.out, 'w') as f:
        json.dump(res, f, indent=1)
    c, fr = res['primary']['contrast'], res['primary']['failed_replies']
    print(f"pooled at {a.confidence}: {res['primary']['population']}; judge - km3 {c['estimate']} [{c['ci_low']}, {c['ci_high']}], "
          f"sign-flip p {c.get('sign_flip_p')} ({c.get('sign_flip')}); verdict {c['verdict']} ({c['reason']}); PASS {res['primary']['pass']}; "
          f"failed replies {fr['n']} ({fr['share']:.1%}{', OVER 20%' if fr['over_20pct'] else ''})")
    return 0


if __name__ == '__main__':
    sys.exit(main())
