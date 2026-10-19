"""Follow-up repairs (Astra 20261019T1122Z): stadium chance rule, Mesagoza lines, illegal Pop-first alternative, judge label form."""
import json, sys
sys.path.insert(0, '/home/dacz8976/exam/repair')
from label_adapter import to_judge, to_engine
F = '/home/dacz8976/exam/commit/exam_2026-10-19.json'
d = json.load(open('/home/dacz8976/exam/commit/exam_2026-10-19.v12_fa6c9b7e.json'))
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget')
def cut(line, stadium):
    mesa = 'Mesagoza' in json.dumps(stadium or '')
    for i, l in enumerate(line):
        if l == 'Play:Mesagoza':
            mesa = True
        elif l.startswith('Play:') and l not in DRAW and 'Stadium' in l:
            pass
        if l.startswith(DRAW) or (l == 'UseStadium' and mesa):   # UseStadium is a coin only on Mesagoza; Rainbow Cave etc. are deterministic
            return line[:i + 1]
    return list(line)
log = []
for p in d['points']:
    a, pid, st = p['answer'], p['id'], p['position'].get('stadium')
    if pid == 'LAD-20261016_024253000_iOS-t1':          # review row 28: plays Mesagoza and uses its coin (tails)
        hm = a['his_move']; hm.insert(hm.index('Play:Mesagoza') + 1, 'UseStadium'); log.append(f'{pid}: UseStadium added after Play:Mesagoza (tails, per review)')
    if pid == 'LAD-20261015_210617000_iOS-t6':          # the alternative's reason is the free coin, so its line must flip
        for x in a['acceptable']:
            if x['line'][:1] == ['Play:Mesagoza'] and 'UseStadium' not in x['line']:
                x['line'].insert(1, 'UseStadium'); log.append(f'{pid}: alternative now {x["line"]}')
    if pid == 'LAD-20261016_015753000_iOS-t5':          # Pop is not legal at the start of this turn (absent from legal_root)
        a['acceptable'] = [x for x in a['acceptable'] if not x['line'][0].startswith('Play:Lucky Ice Pop')]
        a['draw_first'] = {'accepted': False, 'reason': 'Lucky Ice Pop is not playable at the start of this turn (not in legal_root); it becomes legal only after his earlier actions'}
        log.append(f'{pid}: illegal Pop-first alternative removed')
    # one label form everywhere in the answer key and the candidate's legal list: the judge's target-preserving Name#JSON
    J = lambda L: [to_judge(l) for l in L]
    a['his_move'] = J(a['his_move'])
    for x in a['acceptable'] + a.get('pending_alternatives', []):
        x['line'] = J(x['line'])
    p['legal_root'] = J(p['legal_root'])
    a['first_segment'] = cut(a['his_move'], st)
    for x in a['acceptable'] + a.get('pending_alternatives', []):
        x['first_segment'] = cut(x['line'], st)
    strat = [l for l in a['his_move'] if not (l.startswith(DRAW) or l in ('EndTurn', 'UseStadium') or l.startswith('Play:Quick-Grow'))]
    seg = a['first_segment']
    a['segment_scope'] = 'full' if all(l in seg for l in strat) else ('none' if not any(l in seg for l in strat) else 'partial')
    a['strategic_actions_after_segment'] = [l for l in strat if l not in seg]
d['format'] = 'pds-exam-v1.3'
d['label_format'] = ("Answer key and legal_root use the AI judge's target-preserving labels: plain labels as before, and actions with arguments as "
  "Name#{json} with sorted keys (e.g. a Field Blower Tool discard keeps player, Pokemon and Tool index). build/label_adapter.py converts to and from the "
  "legal-moves tool's Name{k:v} form losslessly; compare with same_action() (parsed arguments), never by name alone. answer.legal_steps keeps the tool's raw form.")
json.dump(d, open(F, 'w'), indent=1, ensure_ascii=False)
import collections
print('\n'.join(log)); print('scope', collections.Counter(p['answer']['segment_scope'] for p in d['points']))
# validation positions: every accepted and pending line, forced in engine form, for the existing legal-only binary
V = []
for p in d['points']:
    a = p['answer']
    lines = [('his', a['his_move'])] + [(f'alt{i}', x['line']) for i, x in enumerate(a['acceptable'])] + [(f'pend{i}', x['line']) for i, x in enumerate(a.get('pending_alternatives', []))]
    for tag, L in lines:
        q = dict(p['position']); q['id'] = p['id'] + '|' + tag; q['force'] = [to_engine(l) for l in L]; V.append(q)
json.dump(V, open('/home/dacz8976/exam/repair/validate_lines.json', 'w'))
print('lines to validate', len(V))
