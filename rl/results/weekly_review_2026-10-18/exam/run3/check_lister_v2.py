#!/usr/bin/env python3
"""Exam v2 (run 3): the frozen-lister check BEFORE the freeze (advisor finding F2, Oct 23; PREREG_RUN3 addendum 5, G2 and R1).

usage: check_lister_v2.py JUDGE_DIR POSITIONS DECKS_DIR REFERENCES --out REPORT.json [--drops-out DIR]

JUDGE_DIR is a checkout of the tag judge-prompt-frozen-7. Before frozen-7's rl/ai_judge/judge.py is imported, its freeze_identity.py --check must
pass; after it, the identity gate requires: the checkout's HEAD is the tag's commit, FROZEN.json names the tag and the prompt fingerprint
pool_runs.FROZEN7_FINGERPRINT, and the plan lister binary judge.py runs (PLANS_BIN) has the sha256 FROZEN.json records (the same test the formal
compare makes). POSITIONS is the candidate view (a JSON list; each point's v2_helpers.candidate_view, with its id), DECKS_DIR the deck files the
positions name, REFERENCES the exam's {point id: [{"id": ..., "labels": [...]}]}: every accepted line, the key included.

It runs frozen-7's own plan lister on EVERY point and maps every accepted line, and every prefix of it, with frozen-7's own replay matching
(judge.match_plans, the function the formal compare uses). For each line:
  - the line must reach exactly ONE listed plan n, from a list that is not capped (else: no_plan / ambiguous / unreadable / capped);
  - the lister's segment is the first k steps of the line, where step k is plan n's last step (labels compared as the lister compares them;
    a step the engine forces may stand in the plan without being named in the line: then the shortest prefix that reaches n is used, and the
    forced step is noted);
  - cut(line), the builder's first segment (build/v2_helpers.py), must equal the lister's segment: when plan n stops inside the turn (a chance
    event, or an opponent's choice such as Sabrina or a knockout's promotion) cut() must stop at the same step; when plan n ends the turn,
    cut() must keep the whole line. A difference is `cut_differs`; a line cut() cannot follow (v2_helpers.Uncertain) is `uncertain_cut`.
Under addendum 5's R1 (proposed; in force once the coordinator accepts it) the scored first segment IS the lister's segment, so a cut_differs
or uncertain_cut row is resolved by that rule, with this row as the record (if R1 is not accepted, those rows are G1 drop evidence).
A no_plan / ambiguous / unreadable row on the KEY line (reference id in KEY_REF_IDS), or a capped list, drops the point (G1); on an
alternative it removes that alternative, with this row as its record.
Exit 0: every line agrees. Exit 2: only rows that R1 or an alternative's removal settles. Exit 1: a point to drop, or a point whose
references hold no key line.
The report holds accepted lines (answer material): it is kept with the frozen references and never staged to a worker. --drops-out writes,
for each point with a problem, a file with the problem types and step counts only (no labels), for the selection check."""
import argparse, hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'build'))
sys.path.insert(0, HERE)
import v2_helpers as H  # noqa: E402

TAG = 'judge-prompt-frozen-7'
NEEDS_DROP = ('no_plan', 'ambiguous', 'unreadable', 'capped')
R1_RESOLVES = ('cut_differs', 'uncertain_cut')
# the reference ids of a point's KEY line (his recorded move when it is the key, or Dustin's key_line): a failure there drops the point;
# on any other (alternative) line it removes that alternative (addendum 5, G1). v1.6's references call his move 'recorded'.
KEY_REF_IDS = ('recorded', 'key', 'his')


def sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def label_fits(J, engine, want):
    """The lister's own rule (plans/src/main.rs label_matches): equal in canonical form, or `want` is a bare name (no #) of `engine`'s action, or a
    Place / Ability label without its slot."""
    try:
        e, w = J.concrete_label(engine), J.concrete_label(want)
    except ValueError:
        return False
    return e == w or ('#' not in w and e.split('#')[0] == w) or (w.startswith(('Place:', 'Ability')) and '@' not in w and e.split('@')[0] == w)


def problem_type(err):
    e = str(err or '')
    if e.startswith('ambiguous'):
        return 'ambiguous'
    if e.startswith('unreadable'):
        return 'unreadable'
    return 'no_plan'


def check(J, positions_path, decks_dir, refs):
    """-> report dict. J is frozen-7's judge module (or a stand-in with list_plans / match_plans / concrete_label for the tests)."""
    with open(positions_path, encoding='utf-8') as f:
        plist = json.load(f)
    ids = [p['id'] for p in plist]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f'positions named more than once: {dup[:5]}: stop')
    positions = {p['id']: p for p in plist}
    ids = sorted(ids)
    if sorted(refs) != ids:
        raise SystemExit(f'the references and the positions name different points: only in references {sorted(set(refs) - set(ids))[:5]}, '
                         f'only in positions {sorted(set(ids) - set(refs))[:5]}: stop')
    for pid in ids:
        if not refs[pid]:
            raise SystemExit(f'{pid}: no accepted line in the references (the key must be there): stop')
        for r in refs[pid]:
            if not r.get('labels'):
                raise SystemExit(f"{pid}: reference {r.get('id')!r} has no labels: stop")
        H.check_candidate(positions[pid])  # the lister sees the candidate view only
    recs = J.list_plans(ids, positions_path, decks_dir)
    items, plan = [], {}
    for pid in ids:
        pos = positions[pid]
        for r in refs[pid]:
            line = list(r['labels'])
            tag = f"{pid}|{r['id']}"
            try:
                c = H.cut(line, pos)
                ch = H.chance_steps(line[:len(c)], pos, H.CUTD, first_only=True)
                stop = 'chance' if ch and ch[0] == len(c) - 1 else ('opponent_choice' if len(c) < len(line) else None)
            except H.Uncertain as e:
                c, stop = None, f'uncertain: {e}'
            plan[tag] = {'point': pid, 'ref': r['id'], 'line': line, 'cut': c, 'cut_stop': stop}
            items += [(pid, f'{tag}|{k}', line[:k]) for k in range(1, len(line) + 1)]
    m = J.match_plans(items, recs, positions_path, decks_dir)
    rows = []
    for tag, p in plan.items():
        rec = recs[p['point']]
        line, c = p['line'], p['cut']
        n, err = m[f'{tag}|{len(line)}']
        problems, forced = [], None
        if rec.get('capped'):
            problems.append(('capped', 'the plan list is capped'))
        if not n:
            problems.append((problem_type(err), f'the accepted line reaches no single listed plan: {err}'))
        end = rec['plans'][n - 1]['end'] if n else None
        k = None
        if n:
            last = (rec['plans'][n - 1].get('labels') or [None])[-1]
            k = next((j for j in range(1, len(line) + 1) if m[f'{tag}|{j}'][0] == n and last is not None and label_fits(J, last, line[j - 1])), None)
            if k is None:  # the plan's last step is not named in the line (the engine forced it)
                k = next((j for j in range(1, len(line) + 1) if m[f'{tag}|{j}'][0] == n), None)
                forced = last
            if c is None:
                problems.append(('uncertain_cut', f"cut() cannot follow the line ({p['cut_stop']}); the lister's segment is {k} steps"))
            elif end in ('chance', 'opponent_choice'):
                if k != len(c):
                    problems.append(('cut_differs', f"plan {n} stops inside the turn ('{end}') after {k} of the line's {len(line)} steps; cut() keeps {len(c)}"))
            elif p['cut_stop'] or len(c) != len(line):
                problems.append(('cut_differs', f"plan {n} ends the turn ('{end}'), but cut() stops ({p['cut_stop']}) after {len(c)} of {len(line)} steps"))
        types = [t for t, _ in problems]
        is_key = p['ref'] in KEY_REF_IDS
        if 'capped' in types or (is_key and any(t in NEEDS_DROP for t in types)):
            verdict = 'drop'
        elif any(t in NEEDS_DROP for t in types):
            verdict = 'remove_alternative'
        else:
            verdict = 'resolved_by_R1' if types else 'pass'
        rows.append({'point': p['point'], 'ref': p['ref'], 'key_line': is_key, 'plan': n, 'plan_end': end, 'n_plans': len(rec['plans']), 'line_steps': len(line),
                     'cut_steps': None if c is None else len(c), 'cut_stop': p['cut_stop'], 'lister_steps': k, 'forced_last_step': forced,
                     'lister_segment': line[:k] if k else None, 'problems': [{'type': t, 'detail': d} for t, d in problems], 'verdict': verdict,
                     'match': {str(j): m[f'{tag}|{j}'] for j in range(1, len(line) + 1)}})
    by = lambda v: sorted({r['point'] for r in rows if r['verdict'] == v})
    return {'what': "exam v2: every accepted line against frozen-7's plan lister (PREREG_RUN3 addendum 5, G2 and R1)",
            'positions_sha256': sha(positions_path), 'points': len(ids), 'lines': len(rows),
            'lines_by_verdict': {v: sum(r['verdict'] == v for r in rows) for v in ('pass', 'resolved_by_R1', 'remove_alternative', 'drop')},
            'points_needing_drop': by('drop'), 'points_with_alternatives_to_remove': by('remove_alternative'),
            'points_resolved_by_R1': by('resolved_by_R1'),
            'points_without_key_line': sorted(pid for pid in ids if not any(r['id'] in KEY_REF_IDS for r in refs[pid])),
            'plans_per_point': {pid: len(recs[pid]['plans']) for pid in ids}, 'rows': rows}


def write_drops(rep, out_dir):
    """For the selection check: per point with a problem, the problem types and step counts, never a label."""
    os.makedirs(out_dir, exist_ok=True)
    for pid in sorted({r['point'] for r in rep['rows'] if r['verdict'] != 'pass'}):
        mine = [r for r in rep['rows'] if r['point'] == pid and r['verdict'] != 'pass']
        with open(os.path.join(out_dir, f'{pid}.txt'), 'w', encoding='utf-8') as f:
            f.write(f'{pid}: frozen-7 lister check (check_lister_v2.py), {len(mine)} accepted line(s) with a problem\n')
            for r in mine:
                f.write(f"  line {r['ref']}: verdict {r['verdict']}; problems {[x['type'] for x in r['problems']]}; plan end {r['plan_end']}; "
                        f"steps: line {r['line_steps']}, cut {r['cut_steps']}, lister {r['lister_steps']}\n")


def identity_gate(J, judge_dir, frozen_fingerprint):
    """The checkout is the tag's commit, FROZEN.json is frozen-7's, and the lister binary judge.py will run is the frozen one. -> record dict."""
    head = subprocess.run(['git', '-C', judge_dir, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    tag = subprocess.run(['git', '-C', judge_dir, 'rev-parse', f'{TAG}^{{commit}}'], capture_output=True, text=True).stdout.strip()
    ident = J.frozen_identity()
    bin_sha = J.file_sha256(J.PLANS_BIN)
    bad = []
    if not head or head != tag:
        bad.append(f'the checkout is {head[:12]}, not {TAG} ({tag[:12]})')
    if ident.get('tag') != TAG:
        bad.append(f"FROZEN.json names {ident.get('tag')!r}, not {TAG}")
    if ident.get('fingerprint') != frozen_fingerprint:
        bad.append(f"FROZEN.json's prompt fingerprint {str(ident.get('fingerprint'))[:12]} is not frozen-7's {frozen_fingerprint[:12]}")
    if bin_sha != ident.get('plans_binary_sha256'):
        bad.append(f"the plan lister {J.PLANS_BIN} has sha256 {bin_sha[:16]}, not the frozen {str(ident.get('plans_binary_sha256'))[:16]}")
    if bad:
        raise SystemExit('identity gate: ' + '; '.join(bad) + ': stop')
    return {'tag': TAG, 'commit': head, 'fingerprint': ident.get('fingerprint'), 'plans_bin': J.PLANS_BIN, 'plans_bin_sha256': bin_sha}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('judge_dir'); ap.add_argument('positions'); ap.add_argument('decks'); ap.add_argument('references')
    ap.add_argument('--out', required=True)
    ap.add_argument('--drops-out')
    a = ap.parse_args()
    aj = os.path.join(a.judge_dir, 'rl', 'ai_judge')
    fc = subprocess.run([sys.executable, 'freeze_identity.py', '--check'], cwd=aj, capture_output=True, text=True)
    if fc.returncode:
        sys.exit(f'freeze_identity.py --check failed in {aj}: {(fc.stdout + fc.stderr)[-1500:]}')
    sys.path.insert(0, aj)
    import judge as J  # frozen-7's own code
    import pool_runs
    gate = identity_gate(J, a.judge_dir, pool_runs.FROZEN7_FINGERPRINT)
    with open(a.references, encoding='utf-8') as f:
        refs = json.load(f)
    rep = check(J, a.positions, a.decks, refs)
    rep['identity'] = dict(gate, freeze_identity_check=(fc.stdout.strip().splitlines() or [''])[-1])
    rep['inputs'] = {'references_sha256': sha(a.references)}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    if a.drops_out:
        write_drops(rep, a.drops_out)
    v = rep['lines_by_verdict']
    code = 1 if (v['drop'] or rep['points_without_key_line']) else (2 if v['resolved_by_R1'] or v['remove_alternative'] else 0)
    print(f"lister check: {rep['points']} points, {rep['lines']} accepted lines: {v['pass']} pass, {v['resolved_by_R1']} differ from cut() "
          f"(R1: the lister's segment), {v['remove_alternative']} alternatives to remove, {v['drop']} key lines failing "
          f"({len(rep['points_needing_drop'])} points to drop); points without a key line: {len(rep['points_without_key_line'])}; report {a.out}")
    sys.exit(code)


if __name__ == '__main__':
    main()
