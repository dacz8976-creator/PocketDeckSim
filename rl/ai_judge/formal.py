#!/usr/bin/env python3
"""The formal paired comparison: every expected row accounted for, every row proven to be the choice it claims, or the whole comparison stops.

  python3 judge.py compare --results a.jsonl b.jsonl --bots km3,kx3,judge --seeds 1,2,3 --judge-repeats 1 --references refs.json --set diag14 --out report.json
                           [--on-problem fail|inconclusive]

Why this exists (Astra's source reviews, Oct 19): a bot's move list is replayed into the plan list; an ambiguous or unfollowable list used to become a row
with a `match_error` that a later step quietly left out of its denominator, and a row with ANY non-null `plan_number` was scored as if that number were a
listed plan. Here nothing is left out and no number is taken on trust:

  * the EXPECTED rows are fixed first: (position, bot, run) for every position, every bot and every seed (km3/kx3) or repeat (judge); positions, bots and
    seeds must each be named once (a repeated name would double a denominator);
  * a row is a problem when it is missing, appears twice, was not expected, has no listed plan (an unfollowable or AMBIGUOUS move list, a parse failure),
    or (judge) was a dry run, was not run under the frozen settings, or used a capped (incomplete) plan list;
  * a row with a plan number is checked against the CURRENT plan list, not believed:
      - the number must be a whole number inside the list (bool, float, text and 0 are not numbers; 999 in a two-plan list is a problem);
      - a row that carries a plan number AND a match_error or parse_error contradicts itself;
      - the row must carry the identity hash of the plan list it was made from (`plan_list_sha256`, the lister's whole record: start state, limits, world
        seed, every plan with its key, labels and end) and it must equal the hash of the list used now; the plan's `plan_key` must be the key of that numbered plan;
      - step bots: the recorded full move list (`plan_full`) is replayed through the engine again and must reach exactly that numbered plan;
      - judge: the answer's number as printed in the prompt must map to that plan in the prompt re-rendered under the frozen settings, the row's
        `prompt_sha256` must equal the re-rendered prompt's hash, and the recorded labels must be the listed plan's labels;
  * the accepted moves in the references file are mapped to listed plans the same way; one that cannot be mapped to exactly one plan is a problem;
  * the population is the references' eligibility list (analysis.py): every position's game must be eligible or excluded with a reason;
  * with any problem the comparison has no numbers at all: `--on-problem fail` (the default) stops with exit code 2, `--on-problem inconclusive`
    writes a report with status "inconclusive", every expected row listed with its state, and exits with code 3. Only a clean batch exits 0 and carries
    the game-clustered analysis (analysis.py).

The references file:  {"schema": "ai_judge_references_v1",
                       "references": {"POSITION": [{"id": "recorded", "labels": ["Play:Field Blower", "DiscardToolFromPokemon#{...}"]}, ...]},
                       "eligible_games": ["game-a", ...], "excluded_games": [{"game": "game-b", "reason": "..."}]}
(labels in the canonical Name#JSON form or the legacy Name{k:v} form; a bare name is accepted only when it fits exactly one listed plan).
A file without "references" is read as the bare {position: [...]} mapping and has no eligibility list: the comparison then fails with `no_eligibility`.
"""
import hashlib
import json
import sys

import analysis

SCHEMA = 'ai_judge_paired_comparison_v1'
REFERENCES_SCHEMA = 'ai_judge_references_v1'


class BatchFailed(SystemExit):
    """Raised for `--on-problem fail`: carries the process exit code 2 and the problem list."""

    def __init__(self, problems):
        super().__init__(2)
        self.problems = problems


def plan_list_sha256(rec):
    """The identity of one plan list: sha256 of the lister's whole record for the position (id, start state, world seed, limits, counts, every plan with its
    key, labels, steps and end). Rows record it when they are made; the formal path recomputes it from the list used now."""
    return hashlib.sha256(json.dumps(rec, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')).hexdigest()


def load_references(path):
    """-> (references {position: [{id, labels}]}, eligibility {eligible_games, excluded_games} or None)."""
    with open(path, encoding='utf-8') as f:
        j = json.load(f)
    if isinstance(j, dict) and 'references' in j:
        elig = {k: j[k] for k in ('eligible_games', 'excluded_games') if k in j}
        return j['references'], (elig or None)
    return j, None


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def run_id(row):
    """What distinguishes the runs of one bot at one position: the seed of a step bot (km3, kx3), the repeat index of the judge."""
    if row.get('seed') is not None:
        return row['seed']
    return row.get('repeat', 0)


def expected_rows(ids, bots, seeds, judge_repeats):
    """The fixed list of (position, bot, run) the batch must contain, exactly once each."""
    out = []
    for pid in ids:
        for bot in bots:
            runs = list(range(judge_repeats)) if bot == 'judge' else list(seeds)
            out += [(pid, bot, r) for r in runs]
    return out


def request_problems(ids, bots, seeds, judge_repeats):
    """A request that would double or empty a denominator is refused before any row is read."""
    def prob(detail, position=None):
        return {'kind': 'bad_request', 'position': position, 'bot': None, 'run': None, 'detail': detail}

    out = []
    for name, xs in (('positions', ids), ('bots', bots), ('seeds', seeds)):
        dup = sorted({str(x) for x in xs if list(xs).count(x) > 1})
        if dup:
            out.append(prob(f'{name} named more than once: {dup[:5]} (a repeated name would count its rows twice)'))
    if not ids:
        out.append(prob('no positions'))
    if any(b != 'judge' for b in bots) and not seeds:
        out.append(prob('step bots need at least one seed'))
    if 'judge' in bots and not (_is_int(judge_repeats) and judge_repeats >= 1):
        out.append(prob(f'--judge-repeats must be a whole number >= 1, got {judge_repeats!r}'))
    return out


def list_integrity_problems(recs, ids):
    """The plan list itself must be what a number can point into: plans numbered 1..N in order, each key once."""
    out = []
    for pid in ids:
        rec = recs.get(pid)
        if rec is None or not isinstance(rec.get('plans'), list):
            out.append({'kind': 'list_integrity', 'position': pid, 'bot': None, 'run': None, 'detail': 'no plan list for this position'})
            continue
        plans = rec['plans']
        if [p.get('n') for p in plans] != list(range(1, len(plans) + 1)):
            out.append({'kind': 'list_integrity', 'position': pid, 'bot': None, 'run': None, 'detail': 'the plans are not numbered 1..N in order'})
        elif len({p.get('key') for p in plans}) != len(plans):
            out.append({'kind': 'list_integrity', 'position': pid, 'bot': None, 'run': None, 'detail': 'two plans share a key'})
    return out


def check_chosen_plan(row, bot, rec, list_hash, expect_judge):
    """The row claims plan `plan_number` of `rec`: returns [(kind, detail)] for everything that does not hold."""
    out = []
    n = row['plan_number']
    if not _is_int(n) or not 1 <= n <= len(rec['plans']):
        return [('bad_number', f'plan_number {n!r} is not a whole number from 1 to {len(rec["plans"])}, the size of the current plan list')]
    if row.get('match_error') or row.get('parse_error'):
        out.append(('contradictory', f'the row names plan {n} but also carries an error: {row.get("match_error") or row.get("parse_error")}'))
    plan = rec['plans'][n - 1]
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
        if row.get('plan') != plan['labels']:
            out.append(('labels_mismatch', f"the row's moves {row.get('plan')!r} are not the labels of plan {n}"))
    else:
        if not isinstance(row.get('plan_full'), list) or not row['plan_full']:
            out.append(('no_move_list', 'a step-bot row needs its full recorded move list (`plan_full`) so it can be replayed'))
    return out


def check_rows(rows, expected, recs, require_frozen=True, baseline_sha256=None, expect_judge=None):
    """Returns (by_key, problems): by_key maps each expected key to its single row (or None), problems is a list of dicts {kind, position, bot, run, detail}."""
    problems = []
    seen = {}
    exp = set(expected)
    hashes = {pid: plan_list_sha256(rec) for pid, rec in recs.items()}
    for r in rows:
        key = (r['position'], r['bot'], run_id(r))
        seen.setdefault(key, []).append(r)
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
            for kind, detail in check_chosen_plan(row, bot, recs[pid], hashes[pid], expect_judge):
                problems.append({**base, 'kind': kind, 'detail': detail})
        else:
            problems.append({**base, 'kind': 'list_integrity', 'detail': 'there is no plan list for this position to check the row against'})
        if bot != 'judge' and baseline_sha256 is not None and row.get('pg_pos_sha256') != baseline_sha256:
            problems.append({**base, 'kind': 'baseline_binary', 'detail': f"the row was not played by the frozen baseline executable (its sha256 {str(row.get('pg_pos_sha256'))[:16]})"})
        if bot == 'judge':
            if row.get('dry_run'):
                problems.append({**base, 'kind': 'dry_run', 'detail': 'a dry-run record has no choice'})
            if require_frozen and not row.get('frozen'):
                problems.append({**base, 'kind': 'not_frozen', 'detail': 'the judge row was not produced under the frozen settings'})
        if row.get('capped'):
            problems.append({**base, 'kind': 'capped', 'detail': 'the plan list was capped: not every legal choice'})
    for key in seen:
        if key not in exp:
            problems.append({'kind': 'unexpected', 'position': key[0], 'bot': key[1], 'run': key[2], 'detail': 'a row nobody expected'})
    for pid, rec in recs.items():
        if rec.get('capped'):
            problems.append({'kind': 'capped_list', 'position': pid, 'bot': None, 'run': None, 'detail': 'the plan list of this position is capped'})
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
            out.append({'kind': 'replay_mismatch', 'position': pid, 'bot': key[1], 'run': key[2], 'detail': f'the recorded moves replay to {where}, not to the numbered plan {claimed}'})
    return out


def map_references(references, recs, match, ids=None):
    """references: {position: [{id, labels}]} -> ({position: {ref id: plan number}}, problems). `match` is judge.match_plans (or a stand-in): it must give
    (plan number or None, error text or None) for every item, with ambiguity reported as an error starting with 'ambiguous'.
    With `ids`, a reference for a position that is not in the batch is a problem (the batch must be the planned population), and so is a malformed entry."""
    problems = []
    clean = {}
    for pid, refs in references.items():
        if ids is not None and pid not in ids:
            problems.append({'kind': 'reference_unused', 'position': pid, 'bot': None, 'run': None, 'detail': 'the references name a position that is not in this batch'})
            continue
        ok = isinstance(refs, list) and all(isinstance(r, dict) and isinstance(r.get('id'), str) and isinstance(r.get('labels'), list) and r['labels']
                                            and all(isinstance(l, str) for l in r['labels']) for r in refs)
        if ok and len({r['id'] for r in refs}) != len(refs):
            ok = False
        if not ok:
            problems.append({'kind': 'reference_malformed', 'position': pid, 'bot': None, 'run': None,
                             'detail': 'accepted moves must be a list of {"id": text, "labels": [text, ...]} with each id once'})
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
                problems.append({'kind': kind, 'position': pid, 'bot': None, 'run': ref['id'], 'detail': str(err or 'reaches no listed plan')})
            else:
                out[pid][ref['id']] = n
    return out, problems


def paired_report(ids, expected, by_key, accepted, problems, games=None, on_problem='fail'):
    """The report. With any problem: no agreement numbers; status 'failed' or 'inconclusive'; every expected row listed with its state."""
    status = 'complete' if not problems else ('inconclusive' if on_problem == 'inconclusive' else 'failed')
    bad = {(p['position'], p['bot'], p['run']) for p in problems if p.get('bot')}
    rows = []
    for key in expected:
        pid, bot, run = key
        row = by_key.get(key)
        n = None if row is None else row.get('plan_number')
        state = 'missing' if row is None else ('unresolved' if key in bad else 'ok')
        acc = [rid for rid, num in accepted.get(pid, {}).items() if state == 'ok' and num == n]
        rows.append({'position': pid, 'game': (games or {}).get(pid), 'bot': bot, 'run': run, 'state': state, 'plan_number': n, 'accepted': acc,
                     'agrees': (bool(acc) if state == 'ok' else None)})
    report = {'schema': SCHEMA, 'status': status, 'n_expected_rows': len(expected), 'n_present_rows': sum(1 for k in expected if by_key.get(k) is not None),
              'n_resolved_rows': sum(1 for r in rows if r['state'] == 'ok'), 'problems': problems, 'rows': rows, 'agreement': None, 'analysis': None}
    if status == 'complete':
        agg = {}
        for r in rows:
            a = agg.setdefault(r['bot'], {'rows': 0, 'agree': 0})
            a['rows'] += 1
            a['agree'] += bool(r['agrees'])
        report['agreement'] = agg
    return report


def compare(rows, ids, bots, seeds, judge_repeats, references, recs, match, games=None, on_problem='fail', require_frozen=True, baseline_sha256=None,
            eligibility=None, expect_judge=None, contrasts=None, min_games=analysis.MIN_GAMES, resamples=analysis.RESAMPLES):
    """The whole path. Returns the report; raises BatchFailed (exit code 2) for on_problem='fail' when anything is unresolved.
    expect_judge(position, row) -> {'prompt_sha256', 'shown': {number printed in the prompt: plan number}} (or {'error': text}) is required whenever the judge is a bot:
    it is how a judge row is tied to the prompt it was answered from."""
    if 'judge' in bots and expect_judge is None:
        raise ValueError('compare: the judge rows can only be checked with expect_judge (the prompt re-rendered under the frozen settings)')
    problems = request_problems(ids, bots, seeds, judge_repeats)
    if problems:
        err = BatchFailed(problems)
        err.report = {'schema': SCHEMA, 'status': 'failed' if on_problem != 'inconclusive' else 'inconclusive', 'n_expected_rows': 0, 'n_present_rows': 0, 'n_resolved_rows': 0,
                      'problems': problems, 'rows': [], 'agreement': None, 'analysis': None}
        if on_problem == 'inconclusive':
            return err.report
        raise err
    expected = expected_rows(ids, bots, seeds, judge_repeats)
    problems += list_integrity_problems(recs, ids)
    by_key, row_problems = check_rows(rows, expected, recs, require_frozen, baseline_sha256, expect_judge)
    problems += row_problems
    bad = {(p['position'], p['bot'], p['run']) for p in problems if p.get('bot')}
    if not any(p['kind'] == 'list_integrity' for p in problems):
        problems += replay_problems(by_key, recs, match, bad)
    accepted, ref_problems = map_references(references, recs, match, ids)
    problems += ref_problems
    missing_refs = [pid for pid in ids if not references.get(pid)]
    problems += [{'kind': 'reference_missing', 'position': pid, 'bot': None, 'run': None, 'detail': 'no accepted move list for this position'} for pid in missing_refs]
    problems += analysis.population_problems(ids, games, eligibility, min_games)
    report = paired_report(ids, expected, by_key, accepted, problems, games, on_problem)
    if report['status'] == 'complete':
        report['analysis'] = analysis.analyse(report['rows'], games, eligibility, bots, judge_repeats, contrasts, resamples, min_games=min_games)
    if problems and on_problem != 'inconclusive':
        err = BatchFailed(problems)
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
