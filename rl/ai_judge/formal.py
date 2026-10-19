#!/usr/bin/env python3
"""The formal paired comparison: every expected row accounted for, every move list resolved to ONE listed plan, or the whole comparison stops.

  python3 judge.py compare --results a.jsonl b.jsonl --bots km3,kx3,judge --seeds 1,2,3 --judge-repeats 1 --references refs.json --set diag14 --out report.json
                           [--on-problem fail|inconclusive]

Why this exists (Astra's source review, Oct 19): a bot's move list is replayed into the plan list; an ambiguous or unfollowable list used to become a row
with a `match_error` that a later step quietly left out of its denominator. Here nothing is left out:

  * the EXPECTED rows are fixed first: (position, bot, run) for every position, every bot and every seed (km3/kx3) or repeat (judge);
  * a row is a problem when it is missing, appears twice, was not expected, has no listed plan (an unfollowable or AMBIGUOUS move list, a parse failure),
    or (judge) was a dry run, was not run under the frozen settings, or used a capped (incomplete) plan list;
  * the accepted moves in the references file are mapped to listed plans the same way; one that cannot be mapped to exactly one plan is a problem;
  * with any problem the comparison has no numbers at all: `--on-problem fail` (the default) stops with exit code 2, `--on-problem inconclusive`
    writes a report with status "inconclusive", every expected row listed with its state, and exits with code 3. Only a clean batch exits 0.

The references file maps a position id to its accepted move lists:  {"POSITION": [{"id": "recorded", "labels": ["Play:Field Blower", "DiscardToolFromPokemon#{...}"]}, ...]}
(labels in the canonical Name#JSON form or the legacy Name{k:v} form; a bare name is accepted only when it fits exactly one listed plan).
"""
import json
import sys

SCHEMA = 'ai_judge_paired_comparison_v1'


class BatchFailed(SystemExit):
    """Raised for `--on-problem fail`: carries the process exit code 2 and the problem list."""

    def __init__(self, problems):
        super().__init__(2)
        self.problems = problems


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


def check_rows(rows, expected, recs, require_frozen=True):
    """Returns (by_key, problems): by_key maps each expected key to its single row (or None), problems is a list of dicts {kind, position, bot, run, detail}."""
    problems = []
    seen = {}
    exp = set(expected)
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


def map_references(references, recs, match):
    """references: {position: [{id, labels}]} -> ({position: {ref id: plan number}}, problems). `match` is judge.match_plans (or a stand-in): it must give
    (plan number or None, error text or None) for every item, with ambiguity reported as an error starting with 'ambiguous'."""
    items = [(pid, f'{pid}|{ref["id"]}', ref['labels']) for pid, refs in references.items() for ref in refs]
    got = match(items, recs) if items else {}
    out, problems = {}, []
    for pid, refs in references.items():
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
        acc = [rid for rid, num in accepted.get(pid, {}).items() if n is not None and num == n]
        rows.append({'position': pid, 'game': (games or {}).get(pid), 'bot': bot, 'run': run, 'state': state, 'plan_number': n, 'accepted': acc,
                     'agrees': (bool(acc) if state == 'ok' else None)})
    report = {'schema': SCHEMA, 'status': status, 'n_expected_rows': len(expected), 'n_present_rows': sum(1 for k in expected if by_key.get(k) is not None),
              'n_resolved_rows': sum(1 for r in rows if r['state'] == 'ok'), 'problems': problems, 'rows': rows, 'agreement': None}
    if status == 'complete':
        agg = {}
        for r in rows:
            a = agg.setdefault(r['bot'], {'rows': 0, 'agree': 0})
            a['rows'] += 1
            a['agree'] += bool(r['agrees'])
        report['agreement'] = agg
    return report


def compare(rows, ids, bots, seeds, judge_repeats, references, recs, match, games=None, on_problem='fail', require_frozen=True):
    """The whole path. Returns the report; raises BatchFailed (exit code 2) for on_problem='fail' when anything is unresolved."""
    expected = expected_rows(ids, bots, seeds, judge_repeats)
    by_key, problems = check_rows(rows, expected, recs, require_frozen)
    accepted, ref_problems = map_references(references, recs, match)
    problems += ref_problems
    missing_refs = [pid for pid in ids if not references.get(pid)]
    problems += [{'kind': 'reference_missing', 'position': pid, 'bot': None, 'run': None, 'detail': 'no accepted move list for this position'} for pid in missing_refs]
    report = paired_report(ids, expected, by_key, accepted, problems, games, on_problem)
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
