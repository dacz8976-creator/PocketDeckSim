#!/usr/bin/env python3
"""Exam v2's assembly, mechanical (PREREG_RUN3 addendum 5, G1/G2/R1; addendum 8, K3; the coordinator's note 044, A-E), with frozen-7's lister
check on every accepted and pending line before any question goes to Dustin.

  assemble_v2.py RUN3_DIR EXAM_V2_DIR JUDGE_DIR OUT_DIR [--relink LABELS.json] [--second LABELS.json ...] [--fixes D_FIXES.json]

1. The labels: label_out_p1..5/labels.json (format pds-exam-v2-labels). With --relink (note 044 A), that file's labels REPLACE the first pass's
   for its points (the three games recorded in two clips); the first pass's labels of those points are not read. Every built point (G1 drops
   left out) is labelled exactly once.
2. His move is the build's `force` (P() ends it at his Attack); the labeller's copy must equal it action by action (reported if not).
3. --second (note 044 C): the UNION of each second-pass file's acceptable lines with the first pass's (a line equal to his move or to a line
   already there is not added); its pending lines and questions are added where the point has no question yet (a point with a question in both
   passes stops the run for the coordinator).
4. --fixes (note 044 B and D): ops applied in order, each one recorded: strip_alternative (B: a labeller-written order variant), move_to_pending
   (D1), add_pending (D2, D4; `same_question_as` shares another point's question), set_question (D3; the old text must match exactly).
5. The chance-first rule (note 044 B, v1.6's draw-first rule extended): his own line with its first chance action moved to the front is
   accepted when that action is Professor's Research, Poké Ball, Lucky Ice Pop, Wallace, Quick-Grow Extract (each with its random-evolution
   step) or UseStadium under Fragrant Forest, is in the root legal list, is not already first, and nothing before it feeds it:
   - Wallace / Quick-Grow: no Place, Evolve or Retreat before it (they change what can evolve);
   - Lucky Ice Pop: no Retreat or switch of his own Active before it (it changes what is healed);
   - Research, Poké Ball, Fragrant Forest: deterministic actions before it do not change the deck (nothing feeds them).
   Copycat, Lusamine and every other card stay out. Deterministic actions moved before a draw stay unaccepted, as in v1.6.
6. Every acceptable and pending line: cut after its first Attack (K3), judge label form. references -> check_lister_v2.py; verdicts applied
   (remove_alternative removes the line, resolved_by_R1 records lister_segments by the FINAL acceptable order, drop on his line drops the
   point). first_segment, status (pending while a pending line remains). A question whose pending lines all failed is withdrawn.
7. The question cap: at most 6 questions per labelling part (addendum 8, K7); a shared question counts once. Over the cap stops the run.
Writes OUT_DIR/exam_v2_draft.json, references.json, references_lister.json, positions.json, lister_report.json, lister_drops/, ASSEMBLY.md.
Refuses to overwrite OUT_DIR."""
import argparse, collections, glob, importlib.util, json, os, re, subprocess, sys

E2 = sys.argv[2]
sys.path.insert(0, os.path.join(E2, 'build'))
import v2_helpers as H  # noqa: E402
from label_adapter import same_action, to_judge  # noqa: E402

CHANCE_FIRST = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Lucky Ice Pop', 'Play:Wallace', 'Play:Quick-Grow')
EVOLVING = ('Play:Wallace', 'Play:Quick-Grow')
FULL_SCOPE_CAVEAT = ['LAD-20261020_033156000_SR-t2', 'LAD-20261023_115617000_SR-t3', 'LAD-20261023_122720000_SR-t1',
                     'LAD-20261021_225620000_SR-t3', 'LAD-20261022_000850000_SR-t8']  # coordinator's ruling (Oct 25): kept; past-chance unverified


def cut_at_attack(line):
    at = next((i for i, l in enumerate(line) if l.startswith('Attack:')), None)
    return list(line) if at is None else list(line[:at + 1])


def same_line(a, b):
    return len(a) == len(b) and all(same_action(to_judge(x), to_judge(y)) for x, y in zip(a, b))


def _as_set(line):
    """A line as a multiset of actions (ADJUDICATION_RULES s.2: 'a line is a set of actions'): judge form, a Place without its slot (the lister's
    own rule), a random evolution without its arguments."""
    out = []
    for l in line:
        j = to_judge(l)
        if j.startswith('Place:'):
            j = j.split('@')[0]
        if j.startswith('ChooseRandomEvolutionTarget'):
            j = 'ChooseRandomEvolutionTarget'
        out.append(j)
    return sorted(out)


def same_set(a, b):
    return _as_set(a) == _as_set(b)


def chance_first_variant(his, pos, root_legal):
    """(variant line or None, reason)."""
    stadium = json.dumps(pos.get('stadium') or '')
    try:
        ch = H.chance_steps(his, pos)  # every chance step of the line, by the machinery's own rule (v2_helpers.DRAW and the rest)
    except H.Uncertain as e:
        return None, f'the chance steps cannot be followed ({e})'
    if not ch:
        return None, 'no chance action in his line'
    idx = min(ch)
    l = his[idx]
    if not (l.startswith(CHANCE_FIRST) or (l == 'UseStadium' and 'Fragrant Forest' in stadium)):
        return None, f'its first chance action ({l.split("#")[0]}) is not one the rule covers'
    if idx == 0:
        return None, 'the chance action is already first'
    lab = his[idx]
    span = 2 if lab.startswith(EVOLVING) and idx + 1 < len(his) and his[idx + 1].startswith('ChooseRandomEvolutionTarget') else 1
    before = his[:idx]
    if lab.startswith(EVOLVING) and any(x.startswith(('Place:', 'Evolve:', 'Retreat:', 'Play:Rare Candy')) for x in before):
        return None, f'{lab}: a Place, Evolve or Retreat before it feeds the random evolution'
    if lab.startswith('Play:Lucky Ice Pop') and any(x.startswith(('Retreat:', 'Promote', 'Play:Ilima', 'Play:Koga')) or 'Switch' in x for x in before):
        return None, 'Lucky Ice Pop: his Active changes before it'
    if not any(l == lab or l.split('#')[0] == lab.split('#')[0] for l in root_legal):
        return None, f'{lab} is not in the root legal list'
    return his[idx:idx + span] + before + his[idx + span:], f'{lab.split("#")[0]} moved first (nothing before it feeds it; legal at the root)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run3'); ap.add_argument('e2'); ap.add_argument('judge'); ap.add_argument('out')
    ap.add_argument('--relink'); ap.add_argument('--second', nargs='*', default=[]); ap.add_argument('--fixes')
    a = ap.parse_args()
    run3, e2, judge, out = a.run3, a.e2, a.judge, a.out
    if os.path.exists(out):
        sys.exit(f'{out} exists already: stop')
    built = {}
    for fn in sorted(glob.glob(f'{e2}/build/g/g*.py')):
        sp = importlib.util.spec_from_file_location('g', fn); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        for q in m.POS:
            built[q['id']] = q
    drops = {os.path.basename(p)[:-4] for p in glob.glob(f'{e2}/build/drops/*.txt')}
    staging = json.load(open(f'{e2}/LABEL_STAGING.json', encoding='utf-8'))
    part_of = {pid: p['part'] for p in staging['parts'] for pid in p['points']}
    relink = {}
    if a.relink:
        R = json.load(open(a.relink, encoding='utf-8'))
        if R.get('format') != 'pds-exam-v2-labels':
            sys.exit('relink labels: wrong format: stop')
        relink = R['points']
    labels, deck_kinds, problems, record = {}, {}, collections.defaultdict(list), collections.defaultdict(list)
    for k in range(1, 6):
        L = json.load(open(f'{e2}/label_out_p{k}/labels.json', encoding='utf-8'))
        if L.get('format') != 'pds-exam-v2-labels':
            sys.exit(f'part {k}: format {L.get("format")!r}: stop')
        for pid in L['points']:
            if pid in labels:
                sys.exit(f'{pid} labelled twice: stop')
            if part_of.get(pid) != k:
                sys.exit(f'{pid} labelled in part {k}, staged in part {part_of.get(pid)}: stop')
            if pid in relink:
                labels[pid] = relink[pid]  # note 044 A: the first pass's labels of these points are not read
                record['relabelled'].append(pid)
            else:
                labels[pid] = L['points'][pid]
        for d, v in (L.get('decks') or {}).items():
            if d in deck_kinds:
                sys.exit(f'deck {d} given deck_kinds twice: stop')
            deck_kinds[d] = v
    if set(relink) - set(labels):
        sys.exit(f'relink labels for points not staged: {sorted(set(relink) - set(labels))[:5]}: stop')
    want = set(part_of)
    if set(labels) != want or want & drops or set(built) - drops != want:
        sys.exit('the labelled points are not the built points minus the G1 drops: stop')
    answers = {}
    c = collections.Counter()

    def norm_line(raw, pid, field, reason):
        line = cut_at_attack(raw)
        if len(line) < len(raw):
            c[f'{field}_cut_after_attack'] += 1
        try:
            return [to_judge(l) for l in line]
        except Exception as e:
            sys.exit(f'{pid}: an unreadable label in a {field} line ({e}): the coordinator decides: stop')

    for pid in sorted(want):
        b, lab = built[pid], labels[pid]
        his = list(b['force'])
        theirs = cut_at_attack(lab.get('his_move') or [])
        if not same_line(theirs, his):
            problems['his_move_copy_differs'].append(pid)
        answers[pid] = {'status': None, 'his_move': [to_judge(l) for l in his], 'acceptable': [], 'pending_alternatives': [], 'removed_alternatives': [],
                        'answer_kind': lab.get('answer_kind'), 'ambiguous': lab.get('ambiguous'), 'why_his': lab.get('why_his'), 'part': part_of[pid],
                        **({'relabelled': 'note 044 A: re-labelled from the merged clip reviews'} if pid in relink else {})}
        for field in ('acceptable', 'pending_alternatives'):
            for x in lab.get(field) or []:
                line = norm_line(list(x.get('line') or []), pid, field, x.get('reason'))
                if line is None:
                    continue
                if not line:
                    answers[pid]['removed_alternatives'].append({'from': field, 'line': x.get('line'), 'reason': x.get('reason'), 'why': 'empty line'})
                    continue
                if same_line(line, answers[pid]['his_move']):
                    problems[f'{field}_equal_to_his_move'].append(pid)
                answers[pid][field].append(dict(x, line=line))
    F = json.load(open(a.fixes, encoding='utf-8')) if a.fixes else {'ops': []}
    to_pending = {f['point']: f for f in F['ops'] if f['op'] == 'second_to_pending'}  # the coordinator's note of Oct 25 (A/C outputs), point 1
    # note 044 C: the second pass, unioned (lines compared as sets of actions)
    for fn in a.second:
        S = json.load(open(fn, encoding='utf-8'))
        if S.get('format') != 'pds-exam-v2-labels':
            sys.exit(f'{fn}: wrong format: stop')
        for pid, x in S['points'].items():
            if pid not in answers:
                sys.exit(f'{fn}: {pid} is not a point: stop')
            if pid in relink:
                record['second_pass_skipped_relinked'].append(pid)
                continue
            ans = answers[pid]
            for y in x.get('acceptable') or []:
                line = norm_line(list(y.get('line') or []), pid, 'acceptable', y.get('reason'))
                if not line:
                    continue
                if any(same_set(line, z['line']) for z in ans['pending_alternatives']):
                    record['second_pass_acceptable_equal_to_a_pending_line_stays_pending'].append(pid)
                    continue
                if same_set(line, ans['his_move']):
                    ans['removed_alternatives'].append({'from': 'acceptable (second pass)', 'line': line, 'reason': y.get('reason'),
                                                        'why': "an order variant of his own move: orders are decided by note 044 B's rule"})
                    record['order_variant_stripped'].append(pid)
                    continue
                if any(same_set(line, z['line']) for z in ans['acceptable']):
                    c['second_pass_acceptable_already_accepted'] += 1
                    continue
                if pid in to_pending:
                    f = to_pending[pid]
                    if ans['ambiguous']:
                        sys.exit(f'{pid}: second_to_pending, but the point has a question already: stop')
                    ans['pending_alternatives'].append(dict(y, line=line, source='second pass (note 044 C), made pending', why=f['why']))
                    ans['ambiguous'] = f['question']
                    record['second_pass_stronger_made_pending'].append(pid)
                    continue
                ans['acceptable'].append(dict(y, line=line, source='second pass (note 044 C)'))
                record['second_pass_added_acceptable'].append(pid)
            pend = [p for p in (x.get('pending_alternatives') or [])]
            new = []
            for y in pend:
                line = norm_line(list(y.get('line') or []), pid, 'pending_alternatives', y.get('reason'))
                if line and any(same_set(line, z['line']) for z in ans['pending_alternatives']):
                    record['second_pass_question_merged_with_the_first'].append(pid)
                elif line:
                    new.append(dict(y, line=line, source='second pass (note 044 C)'))
            if new:
                if ans['ambiguous']:
                    sys.exit(f'{pid}: a new pending line from the second pass, but the point has a question already: stop')
                ans['pending_alternatives'] += new
                ans['ambiguous'] = x.get('ambiguous')
                record['second_pass_added_question'].append(pid)
    # note 044 B and D: the fixes file
    if F['ops']:
        for f in F['ops']:
            if f['op'] == 'second_to_pending':
                continue
            pid, op = f['point'], f['op']
            ans = answers[pid]
            if op == 'strip_alternative':
                i = next((i for i, z in enumerate(ans['acceptable']) if same_line(z['line'], f['line'])), None)
                if i is None:
                    sys.exit(f'{pid}: strip_alternative: the line is not accepted there: stop')
                z = ans['acceptable'].pop(i)
                ans['removed_alternatives'].append({'from': 'acceptable', 'line': z['line'], 'reason': z.get('reason'), 'why': f['why']})
            elif op == 'move_to_pending':
                i = next((i for i, z in enumerate(ans['acceptable']) if same_line(z['line'], f['line'])), None)
                if i is None or ans['ambiguous']:
                    sys.exit(f'{pid}: move_to_pending: the line is not accepted there, or the point has a question: stop')
                z = ans['acceptable'].pop(i)
                ans['pending_alternatives'].append(dict(z, moved_from='acceptable', why=f['why']))
                ans['ambiguous'] = f['question']
            elif op == 'add_pending':
                line = [to_judge(l) for l in cut_at_attack(f['line'])]
                if any(same_line(line, z['line']) for z in ans['acceptable'] + ans['pending_alternatives']) or same_line(line, ans['his_move']):
                    sys.exit(f'{pid}: add_pending: the line is already there: stop')
                ans['pending_alternatives'].append({'line': line, 'reason': f['why'], 'source': f['source']})
                if f.get('same_question_as'):
                    ans['ambiguous'] = answers[f['same_question_as']]['ambiguous']
                    ans['same_question_as'] = f['same_question_as']
                else:
                    if ans['ambiguous']:
                        sys.exit(f'{pid}: add_pending: the point has a question already: stop')
                    ans['ambiguous'] = f['question']
            elif op == 'set_question':
                if ans['ambiguous'] != f['from']:
                    sys.exit(f'{pid}: set_question: the question text is not the expected one: stop')
                ans['ambiguous'] = f['to']
                ans['question_edited'] = f['why']
            else:
                sys.exit(f'unknown op {op}: stop')
            record[f'fix_{op}'].append(pid)
    # note 044 B: every labeller-written order variant of his own move (the same set of actions in another order) is stripped; the orders
    # are decided by the chance-first rule below (the two named in note 044 are among them)
    for pid, ans in answers.items():
        keep = []
        for z in ans['acceptable']:
            if same_set(z['line'], ans['his_move']):
                ans['removed_alternatives'].append({'from': 'acceptable', 'line': z['line'], 'reason': z.get('reason'),
                                                    'why': "an order variant of his own move: orders are decided by note 044 B's rule"})
                record['order_variant_stripped'].append(pid)
            else:
                keep.append(z)
        ans['acceptable'] = keep
    # note 044 B: the chance-first rule (his own line)
    roots = {}
    for k in range(1, 6):
        for l in open(f'{e2}/label_in_p{k}/legal.jsonl', encoding='utf-8'):
            j = json.loads(l)
            roots[j['id']] = j['steps'][0]['legal'] if j['steps'] else []
    views = {pid: H.candidate_view(built[pid]) for pid in sorted(want)}
    for pid in sorted(want):
        ans = answers[pid]
        v, why = chance_first_variant(ans['his_move'], views[pid], [to_judge(x) for x in roots.get(pid, [])])
        ans['chance_first'] = {'accepted': v is not None, 'reason': why}
        if v is not None:
            if any(same_line(v, z['line']) for z in ans['acceptable']):
                record['chance_first_already_accepted'].append(pid)
            else:
                ans['acceptable'].append({'line': v, 'reason': 'chance-first order of his own line (note 044 B; settled before any candidate output)',
                                          'source': 'chance-first rule'})
                record['chance_first_added'].append(pid)
    refs = {pid: [{'id': 'his', 'labels': ans['his_move']}] + [{'id': f'alt{i}', 'labels': x['line']} for i, x in enumerate(ans['acceptable'])]
            + [{'id': f'pend{i}', 'labels': x['line']} for i, x in enumerate(ans['pending_alternatives'])] for pid, ans in answers.items()}
    os.makedirs(out)
    json.dump([views[pid] for pid in sorted(want)], open(f'{out}/positions.json', 'w'), ensure_ascii=False)
    json.dump(refs, open(f'{out}/references_lister.json', 'w'), ensure_ascii=False)
    r = subprocess.run([sys.executable, '-B', f'{run3}/check_lister_v2.py', judge, f'{out}/positions.json', f'{e2}/decks', f'{out}/references_lister.json',
                        '--out', f'{out}/lister_report.json', '--drops-out', f'{out}/lister_drops'], capture_output=True, text=True)
    if not os.path.exists(f'{out}/lister_report.json'):
        sys.exit('check_lister_v2.py failed: ' + (r.stdout + r.stderr)[-2000:])
    print('lister:', (r.stdout.strip().splitlines() or [''])[-1])
    rep = json.load(open(f'{out}/lister_report.json', encoding='utf-8'))
    rows = {(x['point'], x['ref']): x for x in rep['rows']}
    exam_points, g1_drops, withdrawn = [], [], []
    for pid in sorted(want):
        ans = answers[pid]
        if rows[(pid, 'his')]['verdict'] == 'drop':
            g1_drops.append(pid)
            continue
        keep = {'acceptable': [], 'pending_alternatives': []}
        for field, tag in (('acceptable', 'alt'), ('pending_alternatives', 'pend')):
            for i, x in enumerate(ans[field]):
                row = rows[(pid, f'{tag}{i}')]
                if row['verdict'] in ('remove_alternative', 'drop'):
                    ans['removed_alternatives'].append({'from': field, 'line': x['line'], 'reason': x.get('reason'),
                                                        'why': f"frozen-7 lister check: {[p['type'] for p in row['problems']]} (G1)"})
                    c[f'{field}_removed_by_lister'] += 1
                    continue
                keep[field].append((x, row))
        ans['acceptable'] = [x for x, _ in keep['acceptable']]
        ans['pending_alternatives'] = [x for x, _ in keep['pending_alternatives']]
        segs = {}
        if rows[(pid, 'his')]['verdict'] == 'resolved_by_R1':
            segs['his'] = rows[(pid, 'his')]['lister_segment']
        for j, (x, row) in enumerate(keep['acceptable']):
            if row['verdict'] == 'resolved_by_R1':
                segs[f'alt{j}'] = row['lister_segment']
        if segs:
            ans['lister_segments'] = segs
        ans['first_segment'] = segs.get('his') or H.cut(ans['his_move'], views[pid])
        if ans['ambiguous'] and not ans['pending_alternatives']:
            withdrawn.append(pid)
            ans['ambiguous_withdrawn'] = ans['ambiguous']
            ans['ambiguous'] = None
        ans['status'] = 'pending' if ans['pending_alternatives'] else 'final'
        b = built[pid]
        exam_points.append({'id': pid, 'game': b['game'], 'deck': b['deck'], 'part': ans['part'], 'position': views[pid], 'answer': ans})
    # the question cap per part (a shared question counts once)
    qpart = collections.Counter()
    for p in exam_points:
        if p['answer']['status'] == 'pending' and not p['answer'].get('same_question_as'):
            if not p['answer']['ambiguous']:
                sys.exit(f"{p['id']}: pending lines but no question: stop")
            qpart[p['part']] += 1
        elif p['answer']['ambiguous'] and p['answer']['status'] != 'pending':
            sys.exit(f"{p['id']}: a question but no pending line: stop")
    over = {k: n for k, n in qpart.items() if n > 6}
    if over:
        sys.exit(f'questions over the cap of 6 per part: {over}: stop')
    exam = {'format': 'pds-exam-v2-draft', 'what': 'exam v2 (run 3) draft: the labels merged mechanically, the note 044 fixes applied, every '
            'line checked by the frozen lister (assemble_v2.py); not frozen', 'deck_kinds': deck_kinds, 'points': exam_points,
            'g1_drops_build': sorted(drops), 'g1_drops_lister': g1_drops,
            'full_scope_caveat': {'points': FULL_SCOPE_CAVEAT, 'why': "the coordinator's ruling (Oct 25): these accepted alternatives are kept; "
                                  'their remainder past the chance step depends on draws that never happened and is unverified in the full-scope reading'},
            'record': {k: sorted(set(v)) for k, v in record.items()}}
    json.dump(exam, open(f'{out}/exam_v2_draft.json', 'w'), indent=1, ensure_ascii=False)
    json.dump({p['id']: [{'id': 'his', 'labels': p['answer']['his_move']}] +
               [{'id': f'alt{i}', 'labels': x['line']} for i, x in enumerate(p['answer']['acceptable'])] for p in exam_points},
              open(f'{out}/references.json', 'w'), ensure_ascii=False)
    st = collections.Counter(p['answer']['status'] for p in exam_points)
    lines = ['# Exam v2 assembly (assemble_v2.py): counts only', '',
             f"- points: {len(exam_points)} (built {len(built)}; G1 drops at build {len(drops)}; by the lister check {len(g1_drops)})",
             f"- status: {dict(st)}; questions per part: {dict(sorted(qpart.items()))}; shared questions: "
             f"{sum(1 for p in exam_points if p['answer'].get('same_question_as'))}; withdrawn: {len(withdrawn)} {withdrawn}",
             f"- lister check lines by verdict: {rep['lines_by_verdict']}; points resolved by R1: {len(rep['points_resolved_by_R1'])}",
             f"- lines: acceptable {sum(len(p['answer']['acceptable']) for p in exam_points)}, pending {sum(len(p['answer']['pending_alternatives']) for p in exam_points)}, "
             f"removed {sum(len(p['answer']['removed_alternatives']) for p in exam_points)}",
             f"- counters: {dict(c)}",
             f"- answer kinds: {dict(collections.Counter(p['answer']['answer_kind'] for p in exam_points))}"]
    for k, v in sorted(record.items()):
        lines.append(f'- {k}: {len(set(v))} {sorted(set(v))[:30]}')
    for k, v in problems.items():
        lines.append(f'- {k}: {len(v)} {v[:20]}')
    open(f'{out}/ASSEMBLY.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
