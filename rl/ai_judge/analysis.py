#!/usr/bin/env python3
"""The exam's analysis: a paired comparison of bots with game-clustered uncertainty (formal.compare calls this only for a complete, fully accounted batch).

The contract (FROZEN.md, "Analysis contract"):
  * the unit of analysis is the DECISION (position); the unit of resampling is the GAME: positions of one game are one cluster, so a game-level bootstrap
    (whole games drawn with replacement) is the only interval reported; a position-level interval would count correlated decisions as independent;
  * ONE predefined judge call per decision is the primary result (repeat 0). Extra judge repeats are a separate SENSITIVITY estimate (the per-decision mean over
    all repeats): they never replace the primary, are never counted as extra samples (a decision counts once), and no "better run" is ever picked.
    A step bot's own randomness is its predefined seeds: its per-decision value is the mean agreement over ALL of its expected seeds (nothing is selected);
  * the population is the references' eligibility list: the primary comparison covers exactly the eligible games; an excluded game (for example one affected by
    developer exposure) is named with its reason and left out; a game that is neither eligible nor excluded is a problem, never silently dropped;
  * an interval that includes zero is "inconclusive" and nothing more is claimed; so is a batch with fewer than MIN_GAMES games (a game bootstrap on a handful
    of clusters is not trustworthy) and a directional result that the exact sign-flip test over games does not support.

Pure Python, no dependencies; the resampling is seeded so a report can be reproduced bit for bit.
"""
import math
import random

SCHEMA = 'ai_judge_clustered_analysis_v1'
CONFIDENCE = 0.95
RESAMPLES = 20000
SEED = 20261019
MIN_GAMES = 10
SIGN_FLIP_EXACT_MAX_GAMES = 16  # up to 2**16 sign patterns are enumerated; beyond that a seeded Monte Carlo draw is used
SIGN_FLIP_DRAWS = 100000
PRIMARY_JUDGE_RUN = 0  # the one predefined judge call per decision (repeat index 0)


# ---------------------------------------------------------------------------------------------------------------------------------- population
def check_eligibility(eligibility):
    """The shape of the references' eligibility block: {"eligible_games": [game ids], "excluded_games": [{"game": id, "reason": text}]}.
    Returns a list of problem texts (empty = well formed)."""
    if not isinstance(eligibility, dict):
        return ['the eligibility block is not an object']
    out = []
    eligible = eligibility.get('eligible_games')
    if not isinstance(eligible, list) or not eligible or not all(isinstance(g, str) and g for g in eligible):
        out.append('"eligible_games" must be a non-empty list of game ids')
        eligible = []
    if len(set(eligible)) != len(eligible):
        out.append('"eligible_games" names a game twice')
    excluded = eligibility.get('excluded_games', [])
    names = []
    if not isinstance(excluded, list):
        out.append('"excluded_games" must be a list of {"game", "reason"}')
        excluded = []
    for x in excluded:
        if not isinstance(x, dict) or not isinstance(x.get('game'), str) or not x.get('game') or not isinstance(x.get('reason'), str) or not x.get('reason').strip():
            out.append(f'an excluded game needs a "game" id and a non-empty "reason": {x!r}')
            continue
        names.append(x['game'])
    if len(set(names)) != len(names):
        out.append('"excluded_games" names a game twice')
    both = sorted(set(eligible) & set(names))
    if both:
        out.append(f'a game cannot be both eligible and excluded: {both[:5]}')
    return out


def population_problems(ids, games, eligibility, min_games=MIN_GAMES):
    """Problems that stop the analysis (each is a dict like formal's): positions without a game id, games that are neither eligible nor excluded, eligible
    games with no position in the batch, a malformed or missing eligibility list, too few eligible games."""
    def prob(kind, detail, position=None):
        return {'kind': kind, 'position': position, 'bot': None, 'run': None, 'detail': detail}

    if eligibility is None:
        return [prob('no_eligibility', 'the references carry no eligibility list: the primary comparison needs the games it is over (references file: '
                                       '{"references": {...}, "eligible_games": [...], "excluded_games": [{"game", "reason"}]})')]
    shape = check_eligibility(eligibility)
    if shape:
        return [prob('eligibility_malformed', s) for s in shape]
    out = []
    eligible = set(eligibility['eligible_games'])
    excluded = {x['game'] for x in eligibility.get('excluded_games', [])}
    seen = set()
    for pid in ids:
        g = (games or {}).get(pid)
        if not g:
            out.append(prob('no_game', 'the position has no game id, so it cannot be placed in a cluster', pid))
        elif g not in eligible and g not in excluded:
            out.append(prob('game_not_listed', f'game {g} is neither in "eligible_games" nor in "excluded_games": nothing is dropped silently', pid))
        else:
            seen.add(g)
    for g in sorted(eligible - seen):
        out.append(prob('eligible_game_uncovered', f'eligible game {g} has no position in this batch: the comparison is not over the planned population'))
    covered = len(eligible & seen)
    if covered < min_games and not out:
        out.append(prob('too_few_games', f'{covered} eligible game(s) < {min_games}: a game-level bootstrap on so few clusters is not trustworthy'))
    return out


# ---------------------------------------------------------------------------------------------------------------------------------- statistics
def percentile_interval(sorted_draws, confidence=CONFIDENCE):
    b = len(sorted_draws)
    tail = (1.0 - confidence) / 2.0
    lo = sorted_draws[int(math.floor(round(tail * b, 9)))]  # round: 0.975 * 20000 must not become 19500.000000000004 and shift an index
    hi = sorted_draws[min(b - 1, int(math.ceil(round((1.0 - tail) * b, 9))) - 1)]
    return lo, hi


def game_bootstrap(sums, counts, names, resamples=RESAMPLES, seed=SEED, confidence=CONFIDENCE):
    """sums[name] = per-game sum of the series' per-decision values, counts = decisions per game (same order). The estimate of a series is sum(sums)/sum(counts)
    (every decision weighs the same). Whole games are drawn with replacement; ONE draw serves every series, so rates and differences are coherent.
    Returns {name: (point, low, high)}."""
    g = len(counts)
    rng = random.Random(seed)
    draws = {n: [] for n in names}
    for _ in range(resamples):
        idx = [int(rng.random() * g) for _ in range(g)]
        n = sum(counts[j] for j in idx)
        for name in names:
            s = sums[name]
            draws[name].append(sum(s[j] for j in idx) / n)
    total = sum(counts)
    out = {}
    for name in names:
        d = sorted(draws[name])
        lo, hi = percentile_interval(d, confidence)
        out[name] = (sum(sums[name]) / total, lo, hi)
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


def verdict(a, b, point, lo, hi, p_flip, n_games, min_games=MIN_GAMES):
    """('a higher' | 'b higher' | 'inconclusive', reason). Only an interval that excludes zero AND is supported by the sign-flip test is a direction."""
    if n_games < min_games:
        return 'inconclusive', f'{n_games} games < {min_games}'
    if lo > 0:
        direction = f'{a} higher'
    elif hi < 0:
        direction = f'{b} higher'
    else:
        return 'inconclusive', 'the interval includes 0'
    if p_flip >= 1.0 - CONFIDENCE:
        return 'inconclusive', f'the interval excludes 0 but the sign-flip test over games does not support it (p = {p_flip:.3f})'
    same = ' (every game gave the same difference)' if hi - lo <= 1e-12 else ''
    return direction, 'the interval excludes 0 and the sign-flip test over games agrees' + same


# ---------------------------------------------------------------------------------------------------------------------------------- the analysis
def decision_values(rows, bots, judge_repeats):
    """{bot: {position: (primary value, sensitivity value or None, [plan numbers by run])}} from the report rows (all state 'ok' in a complete batch).
    judge: primary = repeat 0; sensitivity = mean over all repeats. step bots: primary = mean over all expected seeds, no sensitivity of its own."""
    by = {}
    for r in rows:
        by.setdefault((r['bot'], r['position']), []).append(r)
    out = {b: {} for b in bots}
    for (bot, pid), rs in by.items():
        if bot not in out:
            continue
        rs = sorted(rs, key=lambda r: r['run'])
        vals = [1.0 if r['agrees'] else 0.0 for r in rs]
        nums = [r['plan_number'] for r in rs]
        if bot == 'judge':
            prim = [1.0 if r['agrees'] else 0.0 for r in rs if r['run'] == PRIMARY_JUDGE_RUN]
            if len(prim) != 1:
                raise ValueError(f'judge decision {pid}: expected exactly one primary call (repeat {PRIMARY_JUDGE_RUN}), found {len(prim)}')
            out[bot][pid] = (prim[0], (sum(vals) / len(vals)) if judge_repeats > 1 else None, nums)
        else:
            out[bot][pid] = (sum(vals) / len(vals), None, nums)
    return out


def analyse(rows, games, eligibility, bots, judge_repeats, contrasts=None, resamples=RESAMPLES, seed=SEED, min_games=MIN_GAMES):
    """The clustered comparison over a complete batch. rows = the report's rows; games = {position: game}; eligibility = the references' block
    ({"eligible_games", "excluded_games"}); contrasts = [(a, b)] (default: the judge against every other bot). Returns the analysis block of the report."""
    eligible = set(eligibility['eligible_games'])
    excluded = {x['game']: x['reason'] for x in eligibility.get('excluded_games', [])}
    vals = decision_values(rows, bots, judge_repeats)
    pids = sorted({pid for b in bots for pid in vals[b]})
    for b in bots:
        absent = [p for p in pids if p not in vals[b]]
        if absent:
            raise ValueError(f'bot {b} has no decision at {absent[:3]}: the analysis only runs on a fully accounted batch')
    in_pop = [p for p in pids if games[p] in eligible]
    out_pop = {}
    for p in pids:
        if games[p] in excluded:
            out_pop.setdefault(games[p], []).append(p)
    game_list = sorted({games[p] for p in in_pop})
    counts = [sum(1 for p in in_pop if games[p] == g) for g in game_list]
    pos_by_game = {g: [p for p in in_pop if games[p] == g] for g in game_list}
    if contrasts is None:
        contrasts = [('judge', b) for b in bots if b != 'judge'] if 'judge' in bots else []

    def per_game_sums(fn):
        return [sum(fn(p) for p in pos_by_game[g]) for g in game_list]

    def v(bot, p, which=0):
        prim, sens, _ = vals[bot][p]
        return prim if which == 0 else (sens if sens is not None else prim)

    names, sums = [], {}
    for b in bots:
        names.append(f'rate:{b}')
        sums[f'rate:{b}'] = per_game_sums(lambda p, b=b: v(b, p))
    for a, b in contrasts:
        names.append(f'diff:{a}-{b}')
        sums[f'diff:{a}-{b}'] = per_game_sums(lambda p, a=a, b=b: v(a, p) - v(b, p))
    est = game_bootstrap(sums, counts, names, resamples, seed)

    def interval(name):
        point, lo, hi = est[name]
        return {'estimate': round(point, 6), 'ci_low': round(lo, 6), 'ci_high': round(hi, 6)}

    result = {'schema': SCHEMA, 'status': 'complete',
              'method': {'unit': 'decision (position)', 'cluster': 'game', 'interval': f'{int(CONFIDENCE * 100)}% percentile interval of a game-level bootstrap (whole games drawn with replacement)',
                         'resamples': resamples, 'seed': seed, 'estimator': 'sum of per-decision values / number of decisions (every decision weighs the same)',
                         'primary': f'judge: the one call per decision (repeat {PRIMARY_JUDGE_RUN}); step bots: mean over all predefined seeds',
                         'sign_flip': f'exact test over games up to {SIGN_FLIP_EXACT_MAX_GAMES} games, seeded Monte Carlo ({SIGN_FLIP_DRAWS} draws) beyond; a direction needs p < {1.0 - CONFIDENCE:.2f} as well',
                         'min_games': min_games, 'multiplicity': 'no adjustment for several contrasts'},
              'population': {'eligible_games': game_list, 'n_games': len(game_list), 'n_decisions': len(in_pop), 'decisions_per_game': dict(zip(game_list, counts)),
                             'excluded_games': [{'game': g, 'reason': excluded[g], 'n_decisions': len(ps)} for g, ps in sorted(out_pop.items())]},
              'rates': {b: interval(f'rate:{b}') for b in bots}, 'contrasts': [], 'sensitivity': None}

    def contrast_block(a, b, which):
        name = f'diff:{a}-{b}' if which == 0 else f'sens:{a}-{b}'
        point, lo, hi = est[name]
        gs = sums[name]
        p_flip, how = sign_flip_p(gs, seed)
        verd, why = verdict(a, b, point, lo, hi, p_flip, len(game_list), min_games)
        blk = {'a': a, 'b': b, 'estimate': round(point, 6), 'ci_low': round(lo, 6), 'ci_high': round(hi, 6), 'sign_flip_p': round(p_flip, 6), 'sign_flip': how,
               'n_games': len(game_list), 'n_decisions': len(in_pop), 'verdict': verd, 'reason': why}
        pa = [v(a, p, which) for p in in_pop]
        pb = [v(b, p, which) for p in in_pop]
        if all(x in (0.0, 1.0) for x in pa + pb):
            blk['discordant'] = {'both': sum(1 for x, y in zip(pa, pb) if x == 1 and y == 1), f'{a}_only': sum(1 for x, y in zip(pa, pb) if x == 1 and y == 0),
                                 f'{b}_only': sum(1 for x, y in zip(pa, pb) if x == 0 and y == 1), 'neither': sum(1 for x, y in zip(pa, pb) if x == 0 and y == 0)}
        return blk

    result['contrasts'] = [contrast_block(a, b, 0) for a, b in contrasts]

    if judge_repeats > 1 and 'judge' in bots:
        # SENSITIVITY: the judge's per-decision mean over all its repeats against the same other bots; reported apart, never in place of the primary
        s_names, s_sums = [], {}
        s_names.append('sens_rate:judge')
        s_sums['sens_rate:judge'] = per_game_sums(lambda p: v('judge', p, 1))
        for a, b in contrasts:
            if a == 'judge':
                s_names.append(f'sens:{a}-{b}')
                s_sums[f'sens:{a}-{b}'] = per_game_sums(lambda p, a=a, b=b: v(a, p, 1) - v(b, p))
        s_est = game_bootstrap(s_sums, counts, s_names, resamples, seed)
        est.update(s_est)
        sums.update(s_sums)
        same_all = sum(1 for p in in_pop if len(set(vals['judge'][p][2])) == 1)
        pairs = agree_pairs = 0
        for p in in_pop:
            nums = vals['judge'][p][2]
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    pairs += 1
                    agree_pairs += nums[i] == nums[j]
        point, lo, hi = est['sens_rate:judge']
        result['sensitivity'] = {
            'what': 'the judge\'s per-decision mean over all its repeats; the primary result above is the one predefined call. Repeats are not extra samples and no run is chosen.',
            'judge_rate': {'estimate': round(point, 6), 'ci_low': round(lo, 6), 'ci_high': round(hi, 6)},
            'contrasts': [contrast_block(a, b, 1) for a, b in contrasts if a == 'judge'],
            'repeat_consistency': {'repeats': judge_repeats, 'decisions_with_the_same_plan_in_every_repeat': same_all, 'of_decisions': len(in_pop),
                                   'pairwise_same_plan': (round(agree_pairs / pairs, 6) if pairs else None)}}
    return result
