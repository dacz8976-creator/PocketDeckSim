#!/usr/bin/env python3
"""The exam's analysis: a paired comparison of bots with game-clustered uncertainty (formal.compare calls this only for a complete, fully accounted batch).

The contract (FROZEN.md, "Analysis contract"):
  * the SELECTION is explicit: a separate eligibility file names the primary point ids, the full-scope subset of them and every point's game. The references file
    covers ALL points; the comparison FILTERS it to the selection. Nothing outside the selection enters the primary aggregation, the bootstrap or the
    full-scope block: `analyse` is handed only selected rows and checks that;
  * the unit of analysis is the DECISION (point); the unit of resampling is the GAME: points of one game are one cluster, so a game-level bootstrap (whole games
    drawn with replacement) is the only interval reported; a point-level interval would count correlated decisions as independent;
  * PREFIX agreement (the move list agrees with an accepted one up to the plan's own end: the first chance event, the attack or the end of the turn) is reported
    for ALL primary points. FULL-PLAN agreement (a COMPLETE turn: the same listed plan as an accepted move list, order of moves up to the plan's own end not
    mattering, and what follows a chance event equal label by label) is reported only for the full-scope subset, as a
    separate block; a judge plan that stops at a chance event has no complete sequence and is "not comparable" there (counted, never scored, never dropped silently);
  * points outside the primary selection appear only in a separate DIAGNOSTIC block (descriptive counts, no interval, no verdict);
  * ONE predefined judge call per decision is the primary result (repeat 0). Extra judge repeats are a separate SENSITIVITY estimate (the per-decision mean over
    all repeats): they never replace the primary, are never counted as extra samples (a decision counts once), and no "better run" is ever picked.
    A step bot's own randomness is its predefined seeds: its per-decision value is the mean over ALL of its expected seeds (nothing is selected);
  * an interval that includes zero is "inconclusive" and nothing more is claimed; so is a directional result that the exact sign-flip test over games does not
    support, and any block with fewer than MIN_GAMES games with data. The interval is a percentile bootstrap: at 10-17 games its simulated coverage is about
    89-94% (not 95%) and the verdict rule behaves as the sign-flip test (conservative: false directions 2-4% under a true null, low power for small gaps).

Pure Python, no dependencies; the resampling is seeded so a report can be reproduced bit for bit.
"""
import math
import random

SCHEMA = 'ai_judge_clustered_analysis_v2'
ELIGIBILITY_SCHEMA = 'ai_judge_eligibility_v1'
ELIGIBILITY_KEYS = {'schema', 'primary_ids', 'full_scope_ids', 'games', 'excluded_reasons'}
CONFIDENCE = 0.95
RESAMPLES = 20000
MIN_FORMAL_RESAMPLES = 5000  # fewer resamples than this and a report is marked as an experiment
SEED = 20261019
MIN_GAMES = 10
SIGN_FLIP_EXACT_MAX_GAMES = 16  # up to 2**16 sign patterns are enumerated; beyond that a seeded Monte Carlo draw is used
SIGN_FLIP_DRAWS = 100000
PRIMARY_JUDGE_RUN = 0  # the one predefined judge call per decision (repeat index 0)


# ---------------------------------------------------------------------------------------------------------------------------------- selection
def _ids_ok(xs):
    return isinstance(xs, list) and all(isinstance(x, str) and x for x in xs) and len(set(xs)) == len(xs)


def eligibility_shape_problems(e):
    """The shape of the eligibility file: {"schema": "ai_judge_eligibility_v1", "primary_ids": [...], "full_scope_ids": [...], "games": {id: game},
    "excluded_reasons": {id: text} (optional)}. Returns a list of problem texts (empty = well formed)."""
    if not isinstance(e, dict):
        return ['the eligibility file is not an object']
    out = []
    unknown = sorted(set(e) - ELIGIBILITY_KEYS)
    if unknown:
        out.append(f'unknown key(s) {unknown[:5]} (a misspelt key would silently drop part of the selection); allowed: {sorted(ELIGIBILITY_KEYS)}')
    if 'schema' in e and e['schema'] != ELIGIBILITY_SCHEMA:
        out.append(f'"schema" must be {ELIGIBILITY_SCHEMA!r}, got {e["schema"]!r}')
    if 'full_scope_ids' not in e:
        out.append('"full_scope_ids" must be present (an empty list when no point has a full-plan comparison)')
    prim, full, games = e.get('primary_ids'), e.get('full_scope_ids', []), e.get('games')
    if not _ids_ok(prim) or not prim:
        out.append('"primary_ids" must be a non-empty list of distinct point ids')
        prim = []
    if not _ids_ok(full):
        out.append('"full_scope_ids" must be a list of distinct point ids')
        full = []
    if sorted(set(full) - set(prim)):
        out.append(f'"full_scope_ids" must be a subset of "primary_ids": {sorted(set(full) - set(prim))[:5]}')
    if not isinstance(games, dict) or not all(isinstance(k, str) and isinstance(v, str) and v for k, v in games.items()):
        out.append('"games" must map point ids to non-empty game ids')
    else:
        odd = sorted(v for v in set(games.values()) if v != v.strip() or not v.isprintable())
        if odd:
            out.append(f'game ids may not have leading / trailing space or non-printable characters: {odd[:3]!r}')
        names = {}
        for v in set(games.values()):
            names.setdefault(v.strip().casefold(), set()).add(v)
        clash = sorted(sorted(s) for s in names.values() if len(s) > 1)
        if clash:
            out.append(f'game ids that differ only in case or spacing would be counted as different games: {clash[:3]}')
    reasons = e.get('excluded_reasons', {})
    if not isinstance(reasons, dict) or not all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in reasons.items()):
        out.append('"excluded_reasons" must map point ids to non-empty reason texts')
    elif sorted(set(reasons) & set(prim)):
        out.append(f'a point cannot be both primary and excluded: {sorted(set(reasons) & set(prim))[:5]}')
    return out


def eligibility_problems(ids, references, e, min_games=MIN_GAMES):
    """Problems that stop the primary comparison (dicts like formal's). `ids` = the points of the batch, `references` = the references file (ALL points)."""
    def prob(kind, detail, position=None):
        return {'kind': kind, 'position': position, 'bot': None, 'run': None, 'detail': detail}

    if e is None:
        return [prob('no_eligibility', 'no eligibility selection was given: the comparison needs the primary point ids, the full-scope subset and every point\'s game '
                                       '(--eligibility FILE: {"primary_ids": [...], "full_scope_ids": [...], "games": {id: game}})')]
    shape = eligibility_shape_problems(e)
    if shape:
        return [prob('eligibility_malformed', s) for s in shape]
    out = []
    batch = set(ids)
    games = e['games']
    for pid in e['primary_ids']:
        if pid not in batch:
            out.append(prob('primary_not_in_batch', 'the eligibility file selects this point but it is not in this batch', pid))
            continue
        if not games.get(pid):
            out.append(prob('no_game', 'a selected point has no game in the eligibility file, so it cannot be placed in a cluster', pid))
        refs = references.get(pid) if isinstance(references, dict) else None
        if not refs:
            out.append(prob('reference_missing', 'a selected point has no accepted move list in the references file', pid))
    distinct = {games[p] for p in e['primary_ids'] if games.get(p)}
    if len(distinct) < min_games and not out:
        out.append(prob('too_few_games', f'{len(distinct)} game(s) among the selected points < {min_games}: a game-level bootstrap on so few clusters is not trustworthy'))
    return out


# ---------------------------------------------------------------------------------------------------------------------------------- statistics
def percentile_interval(sorted_draws, confidence=CONFIDENCE):
    b = len(sorted_draws)
    if b == 0:
        raise ValueError('percentile_interval: no draws')
    tail = (1.0 - confidence) / 2.0
    lo = sorted_draws[int(math.floor(round(tail * b, 9)))]  # round: 0.975 * 20000 must not become 19500.000000000004 and shift an index
    hi = sorted_draws[min(b - 1, int(math.ceil(round((1.0 - tail) * b, 9))) - 1)]
    return lo, hi


def game_bootstrap(series, resamples=RESAMPLES, seed=SEED, confidence=CONFIDENCE):
    """series[name] = (per-game sums, per-game counts), one entry per game in a common order. The estimate of a series is sum(sums)/sum(counts) (every decision
    weighs the same). Whole games are drawn with replacement; ONE draw serves every series, so rates and differences are coherent. A draw whose games carry no
    decision of a series is skipped for that series. Returns {name: (point, low, high) or (point, None, None) if fewer than half of the draws were usable}."""
    if not isinstance(resamples, int) or isinstance(resamples, bool) or resamples < 1:
        raise ValueError(f'resamples must be a whole number >= 1, got {resamples!r}')
    names = list(series)
    g = len(next(iter(series.values()))[1]) if series else 0
    rng = random.Random(seed)
    draws = {n: [] for n in names}
    for _ in range(resamples):
        idx = [int(rng.random() * g) for _ in range(g)]
        for name in names:
            sums, counts = series[name]
            n = sum(counts[j] for j in idx)
            if n:
                draws[name].append(sum(sums[j] for j in idx) / n)
    out = {}
    for name in names:
        sums, counts = series[name]
        total = sum(counts)
        point = (sum(sums) / total) if total else None
        d = sorted(draws[name])
        if point is None or len(d) < resamples / 2.0:
            out[name] = (point, None, None)
        else:
            lo, hi = percentile_interval(d, confidence)
            out[name] = (point, lo, hi)
    return out


def sign_flip_p(game_sums, seed=SEED):
    """Two-sided randomisation test over GAMES: under 'no difference' each game's summed difference is as likely to be negative as positive. Exact for up to
    SIGN_FLIP_EXACT_MAX_GAMES games, a seeded Monte Carlo draw beyond. Returns (p, how)."""
    g = len(game_sums)
    obs = abs(sum(game_sums))
    eps = 1e-9
    if g <= SIGN_FLIP_EXACT_MAX_GAMES:
        hits = 0
        for mask in range(1 << g):
            s = 0.0
            for j in range(g):
                s += game_sums[j] if (mask >> j) & 1 else -game_sums[j]
            if abs(s) >= obs - eps:
                hits += 1
        return hits / float(1 << g), 'exact'
    rng = random.Random(seed + 1)
    hits = 0
    for _ in range(SIGN_FLIP_DRAWS):
        s = sum(x if rng.random() < 0.5 else -x for x in game_sums)
        if abs(s) >= obs - eps:
            hits += 1
    return (hits + 1) / float(SIGN_FLIP_DRAWS + 1), 'monte-carlo'


def verdict(a, b, point, lo, hi, p_flip, n_games, min_games=MIN_GAMES, all_games_equal=False):
    """('a higher' | 'b higher' | 'inconclusive', reason). Only an interval that excludes zero AND is supported by the sign-flip test is a direction."""
    if n_games < min_games:
        return 'inconclusive', f'{n_games} games < {min_games}'
    if point is None or lo is None or hi is None:
        return 'inconclusive', 'no usable interval (too few comparable decisions)'
    if lo > 0:
        direction = f'{a} higher'
    elif hi < 0:
        direction = f'{b} higher'
    else:
        return 'inconclusive', 'the interval includes 0'
    if p_flip >= 1.0 - CONFIDENCE:
        return 'inconclusive', f'the interval excludes 0 but the sign-flip test over games does not support it (p = {p_flip:.3f})'
    return direction, 'the interval excludes 0 and the sign-flip test over games agrees' + (' (every game gave the same difference)' if all_games_equal else '')


# ---------------------------------------------------------------------------------------------------------------------------------- per-decision values
def decision_values(rows, bots, judge_repeats, key='agrees'):
    """{bot: {position: (primary, sensitivity, [plan numbers by run])}} from the report rows (all state 'ok' in a complete batch); `key` is the row field that holds
    the agreement flag (True / False / None = not comparable). judge: primary = repeat 0 only; sensitivity = mean over all repeats (None if any is not comparable
    or there is a single call). step bots: primary = mean over all expected seeds. A primary of None means 'no comparable value for this decision'."""
    by = {}
    for r in rows:
        by.setdefault((r['bot'], r['position']), []).append(r)
    out = {b: {} for b in bots}
    for (bot, pid), rs in by.items():
        if bot not in out:
            continue
        rs = sorted(rs, key=lambda r: r['run'])
        vals = [None if r.get(key) is None else (1.0 if r[key] else 0.0) for r in rs]
        nums = [r['plan_number'] for r in rs]
        mean = (lambda xs: None if (not xs or any(x is None for x in xs)) else sum(xs) / len(xs))
        if bot == 'judge':
            prim = [v for r, v in zip(rs, vals) if r['run'] == PRIMARY_JUDGE_RUN]
            if len(prim) != 1:
                raise ValueError(f'judge decision {pid}: expected exactly one primary call (repeat {PRIMARY_JUDGE_RUN}), found {len(prim)}')
            out[bot][pid] = (prim[0], mean(vals) if judge_repeats > 1 else None, nums)
        else:
            out[bot][pid] = (mean(vals), None, nums)
    return out


# ---------------------------------------------------------------------------------------------------------------------------------- blocks
def _block(pids, games, vals, bots, judge_repeats, contrasts, resamples, seed, min_games, sensitivity=True, verdicts=True):
    """The clustered comparison of one scope (`pids`, all with a game). vals = decision_values output restricted to the scope."""
    game_list = sorted({games[p] for p in pids})
    pos_by_game = {g: [p for p in pids if games[p] == g] for g in game_list}

    def get(bot, p, which):
        v = vals[bot].get(p)
        if v is None:
            return None
        prim, sens, _ = v
        return prim if which == 0 else (sens if sens is not None else prim)

    series, defined = {}, {}

    def add(name, fn):
        sums, counts = [], []
        for g in game_list:
            xs = [fn(p) for p in pos_by_game[g]]
            xs = [x for x in xs if x is not None]
            sums.append(sum(xs))
            counts.append(len(xs))
        series[name] = (sums, counts)
        defined[name] = sum(counts)

    for b in bots:
        add(f'rate:{b}', lambda p, b=b: get(b, p, 0))
    for a, b in contrasts:
        add(f'diff:{a}-{b}', lambda p, a=a, b=b: (None if get(a, p, 0) is None or get(b, p, 0) is None else get(a, p, 0) - get(b, p, 0)))
    do_sens = sensitivity and judge_repeats > 1 and 'judge' in bots
    if do_sens:
        add('sens_rate:judge', lambda p: get('judge', p, 1))
        for a, b in contrasts:
            if a == 'judge' or b == 'judge':
                add(f'sens:{a}-{b}', lambda p, a=a, b=b: (None if get(a, p, 1 if a == 'judge' else 0) is None or get(b, p, 1 if b == 'judge' else 0) is None
                                                       else get(a, p, 1 if a == 'judge' else 0) - get(b, p, 1 if b == 'judge' else 0)))
    est = game_bootstrap(series, resamples, seed)

    def interval(name):
        point, lo, hi = est[name]
        r = lambda x: None if x is None else round(x, 6)
        n_games = sum(1 for c in series[name][1] if c)
        if n_games < 2:  # an interval from resampling ONE game has no width and says nothing
            lo = hi = None
        return {'estimate': r(point), 'ci_low': r(lo), 'ci_high': r(hi), 'n_decisions': defined[name], 'n_games': n_games}

    def contrast_block(a, b, prefix, with_verdict):
        name = f'{prefix}:{a}-{b}'
        point, lo, hi = est[name]
        sums, counts = series[name]
        gsums = [s for s, c in zip(sums, counts) if c]
        gcounts = [c for c in counts if c]
        n_games = len(gsums)
        blk = {'a': a, 'b': b, **interval(name), 'n_pairs_dropped': len(pids) - defined[name]}
        if gsums and point is not None:
            p_flip, how = sign_flip_p(gsums, seed)
            blk['sign_flip_p'], blk['sign_flip'] = round(p_flip, 6), how
            if with_verdict:
                blk['verdict'], blk['reason'] = verdict(a, b, point, lo, hi, p_flip, n_games, min_games, max(gsums) - min(gsums) <= 1e-12 and len(set(gcounts)) == 1)
        elif with_verdict:
            blk['verdict'], blk['reason'] = 'inconclusive', 'no decision is comparable for both bots'
        if prefix == 'diff':
            pa = [get(a, p, 0) for p in pids]
            pb = [get(b, p, 0) for p in pids]
            pairs = [(x, y) for x, y in zip(pa, pb) if x is not None and y is not None]
            if blk['n_pairs_dropped'] and pairs:
                # the contrast is over the decisions comparable for BOTH bots: say so, and show each bot's rate on exactly those decisions (its own rate above may
                # cover other decisions), because dropping non-comparable pairs is conditional on the outcome when a plan is not comparable more often when it fails
                blk['matched_rates'] = {a: round(sum(x for x, _ in pairs) / len(pairs), 6), b: round(sum(y for _, y in pairs) / len(pairs), 6)}
                if with_verdict and 'reason' in blk:
                    blk['reason'] += f"; computed on {len(pairs)} of {len(pids)} decisions, {blk['n_pairs_dropped']} not comparable for both bots (dropped, not scored)"
            if pairs and all(x in (0.0, 1.0) and y in (0.0, 1.0) for x, y in pairs):
                blk['discordant'] = {'both': sum(1 for x, y in pairs if x == 1 and y == 1), f'{a}_only': sum(1 for x, y in pairs if x == 1 and y == 0),
                                     f'{b}_only': sum(1 for x, y in pairs if x == 0 and y == 1), 'neither': sum(1 for x, y in pairs if x == 0 and y == 0)}
        return blk

    out = {'population': {'n_games': len(game_list), 'n_decisions': len(pids), 'decisions_per_game': {g: len(pos_by_game[g]) for g in game_list}},
           'rates': {b: interval(f'rate:{b}') for b in bots}, 'contrasts': [contrast_block(a, b, 'diff', verdicts) for a, b in contrasts], 'sensitivity': None}
    if do_sens:
        same_all = pairwise = pairs = 0
        for p in pids:
            nums = vals['judge'][p][2]
            if len(set(nums)) == 1:
                same_all += 1
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    pairs += 1
                    pairwise += nums[i] == nums[j]
        out['sensitivity'] = {
            'what': 'the judge\'s per-decision mean over all its repeats against the same other bots (no verdict is drawn from it); the primary result is the one predefined call. '
                    'Repeats are not extra samples and no run is chosen.',
            'judge_rate': interval('sens_rate:judge'),
            'contrasts': [contrast_block(a, b, 'sens', False) for a, b in contrasts if a == 'judge' or b == 'judge'],
            'repeat_consistency': {'repeats': judge_repeats, 'decisions_with_the_same_plan_in_every_repeat': same_all, 'of_decisions': len(pids),
                                   'pairwise_same_plan': (round(pairwise / pairs, 6) if pairs else None)}}
    return out


def analyse(rows, eligibility, bots, judge_repeats, contrasts=None, resamples=RESAMPLES, seed=SEED, min_games=MIN_GAMES):
    """The clustered comparison over a complete batch. `rows` = the report rows of the PRIMARY points only (fields: position, bot, run, state, plan_number, agrees,
    full_agrees); `eligibility` = the parsed eligibility file; contrasts = [(a, b)] (default: the judge against every other bot). Returns the analysis block:
    {'method', 'prefix': <block over all primary points>, 'full_scope': <block over the full-scope subset> or None}."""
    primary = sorted(eligibility['primary_ids'])
    full = sorted(eligibility.get('full_scope_ids', []))
    games = eligibility['games']
    leaked = sorted({r['position'] for r in rows} - set(primary))
    if leaked:
        raise ValueError(f'analyse was handed rows of points outside the primary selection: {leaked[:5]}')
    if contrasts is None:
        contrasts = [('judge', b) for b in bots if b != 'judge'] if 'judge' in bots else []
    for a, b in contrasts:
        if a not in bots or b not in bots or a == b:
            raise ValueError(f'contrast {a}:{b} must name two different bots of {bots}')
    pv = decision_values(rows, bots, judge_repeats, 'agrees')
    for b in bots:
        absent = [p for p in primary if p not in pv[b]]
        if absent:
            raise ValueError(f'bot {b} has no decision at {absent[:3]}: the analysis only runs on a fully accounted batch')
    result = {'schema': SCHEMA, 'status': 'complete',
              'method': {'unit': 'decision (point)', 'cluster': 'game', 'bots': list(bots), 'judge_repeats': judge_repeats,
                         'interval': f'{int(CONFIDENCE * 100)}% nominal percentile interval of a game-level bootstrap (whole games drawn with replacement); simulated coverage is about 89-94% at 10-17 games',
                         'resamples': resamples, 'seed': seed, 'estimator': 'sum of per-decision values / number of decisions (every decision weighs the same)',
                         'primary': f'judge: the one call per decision (repeat {PRIMARY_JUDGE_RUN}); step bots: mean over all predefined seeds',
                         'agreement': {'prefix': 'all primary points: the move list agrees with an accepted one up to the plan\'s own end (first chance event, attack or end of turn)',
                                       'full_plan': 'full-scope points only, complete turns only: the same listed plan as an accepted move list AND what follows a chance event equal label by label; '
                                                    'a judge plan that stops at a chance event, and a step-bot turn pg_pos cut at a draw card, are not comparable'},
                         'sign_flip': f'exact test over games up to {SIGN_FLIP_EXACT_MAX_GAMES} games, seeded Monte Carlo ({SIGN_FLIP_DRAWS} draws) beyond; a direction needs p < {1.0 - CONFIDENCE:.2f} as well',
                         'min_games': min_games, 'contrasts': [f'{a}:{b}' for a, b in contrasts],
                         'multiplicity': 'no adjustment for several contrasts (with the two default contrasts the chance of at least one false direction is about 5%)'}}
    result['prefix'] = _block(primary, games, pv, bots, judge_repeats, contrasts, resamples, seed, min_games)
    if full:
        fv = decision_values(rows, bots, judge_repeats, 'full_agrees')
        fb = _block(full, games, fv, bots, judge_repeats, contrasts, resamples, seed, min_games, sensitivity=False)
        fb['not_comparable'] = {b: sorted(p for p in full if fv[b][p][0] is None) for b in bots}
        result['full_scope'] = fb
    else:
        result['full_scope'] = None
    return result


def diagnostic_block(rows, ids, reasons, bots, judge_repeats):
    """Points outside the primary selection: DESCRIPTIVE only (per bot: decisions with an agreeing prediction out of the decisions with a resolved row; no interval,
    no verdict, never pooled into anything). `rows` = report rows of those points."""
    per_bot = {}
    for b in bots:
        vs = []
        for p in ids:
            rs = [r for r in rows if r['position'] == p and r['bot'] == b and r['state'] == 'ok' and r.get('agrees') is not None
                  and (b != 'judge' or r['run'] == PRIMARY_JUDGE_RUN)]  # the judge's one predefined call; a step bot's seeds averaged
            if rs:
                vs.append(sum(1.0 if r['agrees'] else 0.0 for r in rs) / len(rs))
        per_bot[b] = {'decisions_resolved': len(vs), 'agreement_sum': round(sum(vs), 6)}
    return {'what': 'points outside the primary selection: descriptive counts only, no interval, no verdict, not part of any primary or full-scope number',
            'points': [{'position': p, 'reason': (reasons or {}).get(p)} for p in ids], 'per_bot': per_bot}
