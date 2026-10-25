#!/usr/bin/env python3
"""REPORT-ONLY (PREREG_RUN3 addendum 8, K19): at the four points whose notes name a third line, the judge's and km3's chosen lines beside his
note, with NO scoring. Descriptive only; nothing here enters any agreement, interval or verdict.

usage: report_only.py EXAM_JSON KM3_JSONL JUDGE_PRIMARY_JSONL... --out OUT.json"""
import json, sys

POINTS = {'LAD-20261022_235420000_SR-t10': 'Q8', 'LAD-20261022_235420000_SR-t4': 'Q9', 'LAD-20261023_005124000_SR-t8': 'Q11',
          'LAD-20261023_204548000_SR-t7': 'Q15'}
NOTE_Q11 = ('the non-ex Buzzwole is not an Ultra Beast in the engine data (the cause of the 3 G1 drops): a line through its Ultra Beast '
            'effects is outside what the engine plays')
args = sys.argv[1:]
out = args[args.index('--out') + 1]
args = args[:args.index('--out')]
exam_path, km3_path, judge_paths = args[0], args[1], args[2:]
exam = {p['id']: p for p in json.load(open(exam_path, encoding='utf-8'))['points']}


def rows(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


km3 = [r for r in rows(km3_path) if r['position'] in POINTS]
judge = [r for p in judge_paths for r in rows(p) if r['position'] in POINTS and r.get('repeat', 0) in (0, None)]
res = []
for pid, q in POINTS.items():
    a = exam[pid]['answer']
    jr = [r for r in judge if r['position'] == pid]
    res.append({'point': pid, 'question': q, 'his_choice': a['dustin_answer']['choice'], 'his_note': a['dustin_answer']['words'],
                'his_move': a['his_move'], 'key': a.get('key_line') or a['his_move'],
                'judge': [{'plan': r.get('plan'), 'plan_number': r.get('plan_number'), 'cut': r.get('cut'), 'reason': r.get('reason'),
                           'state': 'no_choice' if r.get('plan') is None else 'chose'} for r in jr],
                'km3': [{'seed': r.get('seed'), 'plan': r.get('plan'), 'plan_full': r.get('plan_full'), 'cut': r.get('cut')}
                        for r in sorted((r for r in km3 if r['position'] == pid), key=lambda r: r.get('seed') or 0)],
                **({'engine_note': NOTE_Q11} if q == 'Q11' else {})})
json.dump({'what': 'REPORT-ONLY (K19): the judge\'s and km3\'s chosen lines beside his note at Q8, Q9, Q11, Q15; no scoring', 'points': res},
          open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for x in res:
    print(f"{x['question']} {x['point']}: judge {[j['plan'] for j in x['judge']]} | km3 {[k['plan'] for k in x['km3']]}")
