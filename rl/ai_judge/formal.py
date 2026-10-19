#!/usr/bin/env python3
"""The formal paired comparison: every expected row accounted for, every row proven to be the choice it claims, or the whole comparison stops.

  python3 judge.py compare --results a.jsonl b.jsonl --bots km3,kx3,judge --seeds 1,2,3 --judge-repeats 1 --references refs.json --eligibility meta.json
                           --ids ... | --set ... --out report.json [--on-problem fail|inconclusive]

Why this exists (Astra's source reviews, Oct 19): a bot's move list is replayed into the plan list; an ambiguous or unfollowable list used to become a row
with a `match_error` that a later step quietly left out of its denominator, and a row with ANY non-null `plan_number` was scored as if that number were a
listed plan. Here nothing is left out and no number is taken on trust:

  * the EXPECTED rows are fixed first: (point, bot, run) for every point of the batch, every bot and every seed (km3/kx3) or repeat (judge); points, bots and
    seeds must each be named once (a repeated name would double a denominator); a row's run is its whole-number `seed` (step bot, no `repeat`) or its
    whole-number `repeat` (judge, no `seed`);
  * a row is a problem when it is missing, appears twice, was not expected, has no listed plan (an unfollowable or AMBIGUOUS move list, a parse failure), is not
    an object with a text `position` and `bot`, or (judge) is not exactly `dry_run: false` / `frozen: true`, was made with another model, token cap or
    temperature than the freeze, or used a capped (incomplete) plan list;
  * a row with a plan number is checked against the CURRENT plan list, not believed:
      - the number must be a whole number inside the list (bool, float, text and 0 are not numbers; 999 in a two-plan list is a problem);
      - a row that carries a plan number AND a match_error or parse_error contradicts itself;
      - the row must carry the identity hash of the plan list it was made from (`plan_list_sha256`, the lister's whole record: start state, limits, world
        seed, every plan with its key, labels and end) and it must equal the hash of the list used now; the plan's `plan_key` must be the numbered plan's key;
      - step bots: the recorded full move list (`plan_full`) is replayed through the engine again and must reach exactly that numbered plan;
      - judge: the answer's number as printed in the prompt must map to that plan in the prompt re-rendered under the frozen settings, the row's
        `prompt_sha256` must equal the re-rendered prompt's hash, the recorded labels must be the listed plan's labels, and the stored reply (`raw`) must say
        the number the row records;
  * the SELECTION is explicit (analysis.py): the eligibility file names the primary points, the full-scope subset and every point's game. The references file
    covers all points and is FILTERED to the batch: only the references of selected points are validated or used; unselected points never reach the primary
    aggregation, the bootstrap or the full-scope block. Points of the batch outside the primary selection are reported apart, as a descriptive diagnostic block,
    and their problems never stop the primary comparison;
  * the accepted moves of every primary point are mapped to listed plans the same way; one that cannot be mapped to exactly one plan is a problem;
  * with any problem the comparison has no numbers at all: `--on-problem fail` (the default) stops with exit code 2, `--on-problem inconclusive`
    writes a report with status "inconclusive", every expected primary row listed with its state, and exits with code 3. Only a clean batch exits 0 and carries
    the game-clustered analysis (analysis.py). Exit code 3 means a DATA problem; a clean batch whose interval includes 0 exits 0 with the verdict "inconclusive".

The references file is the generic mapping {"POSITION": [{"id": "recorded", "labels": ["Play:Field Blower", "DiscardToolFromPokemon#{...}"]}, ...]} covering all
points (labels in the canonical Name#JSON form or the legacy Name{k:v} form; a bare name is accepted only when it fits exactly one listed plan).
The eligibility file (analysis.ELIGIBILITY_SCHEMA): {"schema": "ai_judge_eligibility_v1", "primary_ids": [...], "full_scope_ids": [...], "games": {"POSITION": "game"},
"excluded_reasons": {"POSITION": "why it is not primary"} (optional)}.
"""
import hashlib
import json
import sys

import analysis

SCHEMA = 'ai_judge_paired_comparison_v2'


class BatchFailed(SystemExit):
    """Raised for `--on-problem fail`: carries the process exit code 2 and the problem list."""

    def __init__(self, problems):
        super().__init__(2)
        self.problems = problems


def plan_list_sha256(rec):
    """The identity of one plan list: sha256 of the lister's whole record for the position (id, start state, world seed, limits, counts, every plan with its
    key, labels, steps and end). Rows record it when they are made; the formal path recomputes it from the list used now."""
    return hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def _no_duplicate_keys(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f'duplicate key {k!r} in a JSON object (the later value would silently replace the earlier one)')
        out[k] = v
    return out


def load_json(path):
    """A JSON file whose objects may not repeat a key. Raises OSError / ValueError (incl. json.JSONDecodeError) with the path in the message."""
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f, object_pairs_hook=_no_duplicate_keys)
    except OSError:
        raise
    except ValueError as e:
        raise ValueError(f'{path}: {e}') from None


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def row_run(row):
    """(run id, error text). A judge row's run is its whole-number `repeat` (and it carries no `seed`); a step bot's is its whole-number `seed` (and it carries no
    `repeat`). bool, float, text and a mixture are refused: the run decides which call is the primary one."""
    seed, repeat = row.get('seed'), row.get('repeat')
    if row.get('bot') == 'judge':
        if seed is not None:
            return None, f'a judge row must not carry a seed (got {seed!r})'
        if not _is_int(repeat):
            return None, f'a judge row needs a whole-number `repeat`, got {repeat!r}'
        return repeat, None
    if not _is_int(seed):
        return None, f'a step-bot row needs a whole-number `seed`, got {seed!r}'
    if repeat is not None:
        return None, f'a step-bot row must not carry a `repeat` (got {repeat!r})'
    return seed, None


def expected_rows(ids, bots, seeds, judge_repeats):
    """The fixed list of (point, bot, run) the batch must contain, exactly once each."""
    out = []
    for pid in ids:
        for bot in bots:
            runs = list(range(judge_repeats)) if bot == 'judge' else list(seeds)
            out += [(pid, bot, r) for r in runs]
    return out


def _prob(kind, detail, position=None, bot=None, run=None):
    return {'kind': kind, 'position': position, 'bot': bot, 'run': run, 'detail': detail}


def request_problems(ids, bots, seeds, judge_repeats, contrasts=None, min_games=analysis.MIN_GAMES, resamples=analysis.RESAMPLES):
    """A request that would double or empty a denominator, or name a contrast nobody asked for, is refused before any row is read."""
    out = []
    for name, xs in (('points', ids), ('bots', bots), ('seeds', seeds)):
        dup = sorted({str(x) for x in xs if list(xs).count(x) > 1})
        if dup:
            out.append(_prob('bad_request', f'{name} named more than once: {dup[:5]} (a repeated name would count its rows twice)'))
    if not ids:
        out.append(_prob('bad_request', 'no points'))
    if not bots or not all(isinstance(b, str) and b for b in bots):
        out.append(_prob('bad_request', 'no bots, or a bot name that is not text'))
    if any(b != 'judge' for b in bots) and not seeds:
        out.append(_prob('bad_request', 'step bots need at least one seed'))
    if not all(_is_int(s) for s in seeds):
        out.append(_prob('bad_request', f'seeds must be whole numbers: {list(seeds)[:5]}'))
    if 'judge' in bots and not (_is_int(judge_repeats) and judge_repeats >= 1):
        out.append(_prob('bad_request', f'--judge-repeats must be a whole number >= 1, got {judge_repeats!r}'))
    if contrasts is not None:
        seen = set()
        for c in contrasts:
            ok = isinstance(c, (tuple, list)) and len(c) == 2 and all(isinstance(x, str) for x in c)
            if not ok or c[0] not in bots or c[1] not in bots or c[0] == c[1]:
                out.append(_prob('bad_request', f'contrast {c!r} must be two different bots of {list(bots)} written a:b'))
            elif tuple(c) in seen:
                out.append(_prob('bad_request', f'contrast {c!r} named twice'))
            else:
                seen.add(tuple(c))
    if not _is_int(min_games) or min_games < 1:
        out.append(_prob('bad_request', f'--min-games must be a whole number >= 1, got {min_games!r}'))
    if not _is_int(resamples) or resamples < 1:
        out.append(_prob('bad_request', f'--resamples must be a whole number >= 1, got {resamples!r}'))
    return out


def list_integrity_problems(recs, ids):
    """The plan list itself must be what a number can point into: plans numbered 1..N in order, each key once."""
    out = []
    for pid in ids:
        rec = recs.get(pid)
        if rec is None or not isinstance(rec.get('plans'), list):
            out.append(_prob('list_integrity', 'no plan list for this position', pid))
            continue
        plans = rec['plans']
        if [p.get('n') for p in plans] != list(range(1, len(plans) + 1)):
            out.append(_prob('list_integrity', 'the plans are not numbered 1..N in order', pid))
        elif len({p.get('key') for p in plans}) != len(plans):
            out.append(_prob('list_integrity', 'two plans share a key', pid))
    return out


def check_chosen_plan(row, bot, rec, list_hash, expect_judge, require_frozen):
    """The row claims plan `plan_number` of `rec`: returns [(kind, detail)] for everything that does not hold."""
    out = []
    n = row['plan_number']
    if not _is_int(n) or not 1 <= n <= len(rec['plans']):
        return [('bad_number', f'plan_number {n!r} is not a whole number from 1 to {len(rec["plans"])}, the size of the current plan list')]
    if row.get('match_error') or row.get('parse_error'):
        out.append(('contradictory', f'the row names plan {n} but also carries an error: {row.get("match_error") or row.get("parse_error")}'))
    plan = rec['plans'][n - 1]
    if row.get('plan_list_sha256') is None and row.get('plan_key') is None:
        out.append(('predates_identity', 'the row carries no plan-list identity (`plan_list_sha256`, `plan_key`): it was written before those fields existed; regenerate it with the frozen-4 writers'))
    else:
        if row.get('plan_list_sha256') is None:
            out.append(('list_mismatch', 'the row carries no plan-list identity (`plan_list_sha256`): it cannot be tied to the list used now'))
        elif row['plan_list_sha256'] != list_hash:
            out.append(('list_mismatch', f"the row was made from a different plan list (identity {str(row['plan_list_sha256'])[:12]}, current {list_hash[:12]})"))
        if row.get('plan_key') != plan['key']:
            out.append(('key_mismatch', f"the row's plan key {str(row.get('plan_key'))[:16]!r} is not the key of plan {n} in the current list ({plan['key'][:16]!r})"))
    if bot == 'judge':
        exp = expect_judge(row['position'], row) if expect_judge is not None else {'error': 'no expectation of the prompt was supplied, so the judge row cannot be checked'}
        if exp.get('error'):
            out.append(('prompt_mismatch', f"the prompt cannot be re-rendered: {exp['error']}"))
        else:
            sn = row.get('shown_number')
            shown = exp['shown'].get(sn) if _is_int(sn) else None
            if shown != n:
                out.append(('shown_mismatch', f'the answer {sn!r} is plan {shown} in the prompt as re-rendered, not plan {n}'))
            if row.get('prompt_sha256') != exp['prompt_sha256']:
                out.append(('prompt_mismatch', f"the row's prompt hash {str(row.get('prompt_sha256'))[:12]} is not the hash of the prompt re-rendered now ({exp['prompt_sha256'][:12]})"))
            if exp.get('parse') is not None:
                raw = row.get('raw')
                if not isinstance(raw, str):
                    out.append(('reply_mismatch', 'the row carries no stored reply (`raw`), so its choice cannot be re-derived'))
                else:
                    got = exp['parse'](raw)
                    if got != sn:
                        out.append(('reply_mismatch', f'the stored reply says plan {got!r} but the row records {sn!r}'))
            if require_frozen:
                for k, v in (exp.get('settings') or {}).items():
                    if row.get(k) != v:
                        out.append(('not_frozen', f'the row records {k}={row.get(k)!r}, the freeze says {v!r}'))
        if row.get('plan') != plan['labels']:
            out.append(('labels_mismatch', f"the row's moves {row.get('plan')!r} are not the labels of plan {n}"))
    else:
        pf = row.get('plan_full')
        if not isinstance(pf, list) or not pf or not all(isinstance(x, str) for x in pf):
            out.append(('no_move_list', 'a step-bot row needs its full recorded move list (`plan_full`, a list of text labels) so it can be replayed'))
    return out


def check_rows(rows, expected, recs, require_frozen=True, baseline_sha256=None, expect_judge=None):
    """Returns (by_key, problems): by_key maps each expected key to its single row (or None), problems is a list of dicts {kind, position, bot, run, detail}."""
    problems = []
    seen = {}
    exp = set(expected)
    hashes = {pid: plan_list_sha256(rec) for pid, rec in recs.items()}
    for i, r in enumerate(rows):
        if not isinstance(r, dict) or not isinstance(r.get('position'), str) or not isinstance(r.get('bot'), str):
            problems.append(_prob('bad_row', f'row {i} is not an object with a text `position` and a text `bot`'))
            continue
        run, err = row_run(r)
        if err:
            problems.append(_prob('bad_run_id', err, r['position'], r['bot']))
            continue
        seen.setdefault((r['position'], r['bot'], run), []).append(r)
    by_key = {}
    for key in expected:
        got = seen.get(key, [])
        pid, bot, run = key
        base = {'position': pid, 'bot': bot, 'run': run}
        if not got:
            problems.append({**base, 'kind': 'missing', 'detail': 'no row for this expected (position, bot, run)'})
            by_key[key] = None
            continue
        if len(got) > 1:
            problems.append({**base, 'kind': 'duplicate', 'detail': f'{len(got)} rows for this key'})
            by_key[key] = None
            continue
        row = got[0]
        by_key[key] = row
        if row.get('plan_number') is None:
            why = row.get('match_error') or row.get('parse_error') or 'no listed plan'
            kind = 'ambiguous' if str(why).startswith('ambiguous') else 'unresolved'
            problems.append({**base, 'kind': kind, 'detail': str(why)})
        elif pid in recs and isinstance(recs[pid].get('plans'), list):
            for kind, detail in check_chosen_plan(row, bot, recs[pid], hashes[pid], expect_judge, require_frozen):
                problems.append({**base, 'kind': kind, 'detail': detail})
        else:
            problems.append({**base, 'kind': 'list_integrity', 'detail': 'there is no plan list for this position to check the row against'})
        if row.get('dry_run') is not False:
            problems.append({**base, 'kind': 'dry_run', 'detail': f"`dry_run` must be exactly false (a dry-run record has no choice), got {row.get('dry_run')!r}"})
        if bot != 'judge' and baseline_sha256 is not None and row.get('pg_pos_sha256') != baseline_sha256:
            problems.append({**base, 'kind': 'baseline_binary', 'detail': f"the row was not played by the frozen baseline executable (its sha256 {str(row.get('pg_pos_sha256'))[:16]})"})
        if bot == 'judge' and require_frozen and row.get('frozen') is not True:
            problems.append({**base, 'kind': 'not_frozen', 'detail': f"the judge row was not produced under the frozen settings (`frozen` is {row.get('frozen')!r}, not true)"})
        if row.get('capped'):
            problems.append({**base, 'kind': 'capped', 'detail': 'the plan list was capped: not every legal choice'})
    for key in seen:
        if key not in exp:
            problems.append({**_prob('unexpected', 'a row nobody expected', key[0], key[1], key[2])})
    for pid, rec in recs.items():
        if rec.get('capped'):
            problems.append(_prob('capped_list', 'the plan list of this position is capped', pid))
    return by_key, problems


def replay_problems(by_key, recs, match, already_bad):
    """Step-bot rows: the recorded full move list is replayed through the engine again; it must reach exactly the numbered plan."""
    items = []
    for key, row in by_key.items():
        if row is None or key in already_bad or key[1] == 'judge' or row.get('plan_number') is None:
            continue
        items.append((key[0], f'{key[0]}|{key[1]}|{key[2]}', row['plan_full'], key))
    if not items:
        return []
    got = match([(pid, tag, labels) for pid, tag, labels, _ in items], recs)
    out = []
    for pid, tag, _, key in items:
        n, err = got.get(tag, (None, 'no answer from the matcher'))
        claimed = by_key[key]['plan_number']
        if n != claimed:
            where = f'plan {n}' if n else f'no single plan ({err})'
            out.append(_prob('replay_mismatch', f'the recorded moves replay to {where}, not to the numbered plan {claimed}', pid, key[1], key[2]))
    return out


def map_references(references, recs, match, ids):
    """FILTERS the references file (which covers ALL points) to the batch `ids`, validates and maps only those: -> ({position: {ref id: plan number}}, problems,
    n_ignored). References of points outside the batch are neither read nor validated. `match` is judge.match_plans (or a stand-in): it must give
    (plan number or None, error text or None) for every item, with ambiguity reported as an error starting with 'ambiguous'."""
    problems = []
    clean = {}
    wanted = [pid for pid in ids if pid in references]
    for pid in wanted:
        refs = references[pid]
        ok = isinstance(refs, list) and all(isinstance(r, dict) and isinstance(r.get('id'), str) and isinstance(r.get('labels'), list) and r['labels']
                                            and all(isinstance(l, str) for l in r['labels']) for r in refs)
        if ok and len({r['id'] for r in refs}) != len(refs):
            ok = False
        if not ok:
            problems.append(_prob('reference_malformed', 'accepted moves must be a list of {"id": text, "labels": [text, ...]} with each id once', pid))
            continue
        clean[pid] = refs
    items = [(pid, f'{pid}|{ref["id"]}', ref['labels']) for pid, refs in clean.items() for ref in refs]
    got = match(items, recs) if items else {}
    out = {}
    for pid, refs in clean.items():
        out[pid] = {}
        for ref in refs:
            n, err = got.get(f'{pid}|{ref["id"]}', (None, 'no answer from the matcher'))
            if n is None:
                kind = 'reference_ambiguous' if str(err).startswith('ambiguous') else 'reference_unresolved'
                problems.append(_prob(kind, str(err or 'reaches no listed plan'), pid, None, ref['id']))
            else:
                out[pid][ref['id']] = n
    return out, problems, len([p for p in references if p not in set(ids)])


def row_full_labels(row, bot):
    """The complete move sequence a row stands for, or None when it has none (a judge plan that stops at a chance event or for an opponent's choice)."""
    if bot == 'judge':
        return row.get('plan') if row.get('cut') in ('attack', 'end_turn') else None
    pf = row.get('plan_full')
    return pf if isinstance(pf, list) else None


def full_plan_agreement(row, bot, refs, normalize):
    """-> (True | False | None, error text or None). Full-plan agreement: the row's complete move sequence equals an accepted complete sequence (compared after
    `normalize`, the canonical label form without the trailing End the turn). None = the row has no complete sequence (not comparable)."""
    labels = row_full_labels(row, bot)
    if labels is None:
        return None, None
    try:
        got = normalize(labels)
        return any(normalize(ref['labels']) == got for ref in refs), None
    except (ValueError, TypeError, AttributeError) as e:
        return None, f'a move label cannot be read: {e}'


def _states(expected, by_key, problems):
    """{key: state}: missing / duplicate / unresolved (a problem names the row) / ok."""
    st = {}
    pos_bad = {p['position'] for p in problems if p.get('position') and not p.get('bot')}
    kinds = {}
    for p in problems:
        if p.get('position') is not None and p.get('bot') is not None:
            kinds.setdefault((p['position'], p['bot'], p['run']), []).append(p['kind'])
    for key in expected:
        k = kinds.get(key, [])
        if 'duplicate' in k:
            st[key] = 'duplicate'
        elif by_key.get(key) is None:
            st[key] = 'missing'
        elif k or key[0] in pos_bad:
            st[key] = 'unresolved'
        else:
            st[key] = 'ok'
    return st


def _rows(scope_ids, expected, by_key, states, accepted, games, full_scope, full_agree, complete):
    rows = []
    for key in expected:
        pid, bot, run = key
        if pid not in scope_ids:
            continue
        row = by_key.get(key)
        n = None if row is None else row.get('plan_number')
        acc = [rid for rid, num in accepted.get(pid, {}).items() if complete and states[key] == 'ok' and num == n]
        rows.append({'position': pid, 'game': (games or {}).get(pid), 'bot': bot, 'run': run, 'state': states[key], 'plan_number': n, 'accepted': acc,
                     'agrees': (bool(acc) if (complete and states[key] == 'ok') else None), 'full_scope': pid in full_scope,
                     'full_agrees': (full_agree.get(key) if (complete and states[key] == 'ok' and pid in full_scope) else None)})
    return rows


def early_failure(problems, on_problem, run_info=None):
    """The report of a request that cannot even start (bad request, malformed selection): raises BatchFailed, or returns the inconclusive report."""
    report = {'schema': SCHEMA, 'status': 'inconclusive' if on_problem == 'inconclusive' else 'failed', 'n_expected_rows': 0, 'n_present_rows': 0, 'n_resolved_rows': 0,
              'problems': problems, 'rows': [], 'row_account': None, 'analysis': None, 'selection': None, 'diagnostic_excluded': None}
    if run_info is not None:
        report['run'] = run_info
    if on_problem == 'inconclusive':
        return report
    err = BatchFailed(problems)
    err.report = report
    raise err


def compare(rows, ids, bots, seeds, judge_repeats, references, recs, match, eligibility, on_problem='fail', require_frozen=True, baseline_sha256=None,
            expect_judge=None, contrasts=None, min_games=analysis.MIN_GAMES, resamples=analysis.RESAMPLES, normalize=None, run_info=None, extra_problems=(),
            read_problems=()):
    """The whole path. Returns the report; raises BatchFailed (exit code 2) for on_problem='fail' when anything is unresolved.
    expect_judge(point, row) -> {'prompt_sha256', 'shown': {number printed in the prompt: plan number}, 'parse': reply text -> number or None,
    'settings': {model, max_tokens, temperature}} (or {'error': text}) is required whenever the judge is a bot: it is how a judge row is tied to the prompt and
    reply it was answered from. `normalize(labels)` -> canonical comparable label list is required for the full-plan agreement of the full-scope points."""
    if 'judge' in bots and expect_judge is None:
        raise ValueError('compare: the judge rows can only be checked with expect_judge (the prompt re-rendered under the frozen settings)')
    problems = list(extra_problems) + request_problems(ids, bots, seeds, judge_repeats, contrasts, min_games, resamples)
    if not isinstance(references, dict):
        problems.append(_prob('reference_malformed', 'the references must be an object {point: [{"id", "labels"}]}'))
    problems += analysis.eligibility_problems(ids, references, eligibility, min_games) if not problems else []
    if problems:
        return early_failure(problems, on_problem, run_info)
    primary = list(eligibility['primary_ids'])
    pset, full_scope = set(primary), set(eligibility.get('full_scope_ids', []))
    if full_scope and normalize is None:
        raise ValueError('compare: the full-scope points need `normalize` (the canonical form of a move list)')
    diag_ids = [i for i in ids if i not in pset]
    dset = set(diag_ids)
    games = eligibility['games']
    expected = expected_rows(ids, bots, seeds, judge_repeats)
    problems = list_integrity_problems(recs, ids)
    by_key, row_problems = check_rows(rows, expected, recs, require_frozen, baseline_sha256, expect_judge)
    problems += row_problems
    problems += list(read_problems)  # lines of the results files that did not parse: the batch fails, with every expected row still accounted for
    bad = {(p['position'], p['bot'], p['run']) for p in problems if p.get('bot')}
    if not any(p['kind'] == 'list_integrity' for p in problems):
        problems += replay_problems(by_key, recs, match, bad)
    accepted, ref_problems, n_ignored = map_references(references, recs, match, ids)
    problems += ref_problems
    problems += [_prob('reference_missing', 'no accepted move list for this point', pid) for pid in diag_ids if not references.get(pid)]
    # full-plan agreement (full-scope points only)
    full_agree = {}
    for key in expected:
        pid, bot, run = key
        row = by_key.get(key)
        if pid in full_scope and row is not None and row.get('plan_number') is not None and pid in accepted:
            val, err = full_plan_agreement(row, bot, references[pid], normalize)
            full_agree[key] = val
            if err:
                problems.append(_prob('full_plan_unreadable', err, pid, bot, run))
    batch_problems = [p for p in problems if p.get('position') not in dset]
    diag_problems = [p for p in problems if p.get('position') in dset]
    complete = not batch_problems
    status = 'complete' if complete else ('inconclusive' if on_problem == 'inconclusive' else 'failed')
    states = _states(expected, by_key, problems)
    prim_expected = [k for k in expected if k[0] in pset]
    report_rows = _rows(pset, expected, by_key, states, accepted, games, full_scope, full_agree, complete)
    account = {}
    for r in report_rows:
        a = account.setdefault(r['bot'], {})
        a[r['state']] = a.get(r['state'], 0) + 1
    diag_rows = _rows(dset, expected, by_key, states, accepted, games, set(), {}, True)
    reasons = eligibility.get('excluded_reasons', {})
    report = {'schema': SCHEMA, 'status': status, 'n_expected_rows': len(prim_expected), 'n_present_rows': sum(1 for k in prim_expected if by_key.get(k) is not None),
              'n_resolved_rows': sum(1 for r in report_rows if r['state'] == 'ok'), 'problems': batch_problems, 'rows': report_rows,
              'row_account': {'what': 'row accounting only (primary points; every repeat and seed is a row): not an agreement figure', 'per_bot_state_counts': account},
              'selection': {'primary_ids': len(primary), 'full_scope_ids': len(full_scope), 'diagnostic_ids': list(diag_ids), 'references_in_file': len(references),
                            'references_used': len([p for p in ids if p in references]), 'references_ignored': n_ignored},
              'analysis': None,
              'diagnostic_excluded': {**analysis.diagnostic_block(diag_rows, diag_ids, reasons, bots, judge_repeats), 'problems': diag_problems,
                                      'n_expected_rows': len([k for k in expected if k[0] in dset]), 'rows': diag_rows} if diag_ids else None}
    if run_info is not None:
        report['run'] = run_info
    if complete:
        report['analysis'] = analysis.analyse(report_rows, eligibility, bots, judge_repeats, contrasts, resamples, min_games=min_games)
    if batch_problems and on_problem != 'inconclusive':
        err = BatchFailed(batch_problems)
        err.report = report
        raise err
    return report


def exit_code(report):
    return {'complete': 0, 'inconclusive': 3}.get(report['status'], 2)


def print_problems(problems, file=None):
    file = file or sys.stderr  # looked up when called, so a redirected stderr is honoured
    for p in problems[:50]:
        print(f"  {p['kind']}: {p.get('position')} {p.get('bot')} {p.get('run')}: {p.get('detail')}", file=file)
    if len(problems) > 50:
        print(f'  ... and {len(problems) - 50} more', file=file)
