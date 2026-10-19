"""v1.4 (live laptop, Oct 19): the coordinator's scope rule. A point's scope is set by its SHORTEST accepted segment:
'full' only if every accepted line's first segment contains all of that line's strategic actions; 'none' if his own segment
has none of his; otherwise 'partial' (prefix agreement only). No bot output used."""
import json, collections, os, shutil
F = '/home/dacz8976/exam/commit/exam_2026-10-19.json'
SNAP = '/home/dacz8976/exam/commit/exam_2026-10-19.v13_4b72704f.json'
if not os.path.exists(SNAP):
    shutil.copy(F, SNAP)
d = json.load(open(SNAP))
assert d['format'] == 'pds-exam-v1.3', d['format']
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget')
def strategic(line):
    return [l for l in line if not (l.startswith(DRAW) or l in ('EndTurn', 'UseStadium') or l.startswith('Play:Quick-Grow'))]
def scope(line, seg):
    s = strategic(line)
    if all(l in seg for l in s):
        return 'full'
    return 'none' if not any(l in seg for l in s) else 'partial'
changed = []
for p in d['points']:
    a = p['answer']
    by = {'his': scope(a['his_move'], a['first_segment'])}
    for i, x in enumerate(a['acceptable']):
        by[f'alt{i}'] = scope(x['line'], x['first_segment'])
    point = 'full' if all(v == 'full' for v in by.values()) else ('none' if by['his'] == 'none' else 'partial')
    a['segment_scope_v13'] = a['segment_scope']
    a['segment_scope_his'] = by['his']
    a['segment_scope_by_line'] = by
    a['segment_scope'] = point
    if point != a['segment_scope_v13']:
        changed.append((p['id'], a['segment_scope_v13'], point, {k: v for k, v in by.items() if v != 'full'}))
d['format'] = 'pds-exam-v1.4'
d['scope_rule'] = ("A point's segment_scope is set by its shortest accepted segment (coordinator, Oct 19): 'full' only if every accepted line's "
                   "first segment (his and each acceptable line; pending alternatives don't count) contains all of that line's strategic actions; "
                   "'none' if his own first segment contains none of his strategic actions; otherwise 'partial'. Plan-segment agreement uses 'full' "
                   "points only; 'partial' and 'none' points count for prefix agreement only. segment_scope_by_line and segment_scope_his show the parts; "
                   "segment_scope_v13 keeps the old value.")
json.dump(d, open(F, 'w'), indent=1, ensure_ascii=False)
sc = lambda pts: collections.Counter(p['answer']['segment_scope'] for p in pts)
scored = [p for p in d['points'] if p['answer'].get('status') != 'pending_dustin']
print('changed:', len(changed))
for c in changed:
    print('  ', c)
print('all 51:', sc(d['points']), '| v1.3 all:', collections.Counter(p['answer']['segment_scope_v13'] for p in d['points']))
print('scored (not pending):', len(scored), sc(scored), '| v1.3 scored:', collections.Counter(p['answer']['segment_scope_v13'] for p in scored))
print('full scored by deck:', collections.Counter(p['deck'] for p in scored if p['answer']['segment_scope'] == 'full'))
print('full scored by kind:', collections.Counter(p['answer_kind'] for p in scored if p['answer']['segment_scope'] == 'full'))
print('scoring field:', d['scoring'][:1500])
