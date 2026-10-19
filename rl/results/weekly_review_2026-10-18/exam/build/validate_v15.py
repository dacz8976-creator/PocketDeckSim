"""v1.5 legality checks with the rebuilt legal-only tool (no bot is ever built or asked).
Lines: his recorded move (a 'record' where his key was overridden), the key line where Dustin overrode it, and every acceptable line.
(1) shipped: each line forced on the candidate position; every action up to the first chance action must be legal, and the tool must
    stop exactly there (= the line's first segment).
(2) after the chance: a verification variant per line, with the build's recorded draws put in the hand up front, the chance actions
    removed and coin results applied (the build's own _draws/_vpatch); every remaining action must match.
Writes build/vlines_v15.jsonl and build/VALIDATION_v15.json."""
import json, sys, glob, copy, subprocess, importlib.util, collections
sys.path.insert(0, '/home/dacz8976/exam/repair'); sys.path.insert(0, '/home/dacz8976/exam/build')
from label_adapter import to_engine
E = '/home/dacz8976/exam'
BIN = f'{E}/bin/pg_legal_v14'
ARGS = open(f'{E}/bin/decks.args').read().split()
d = json.load(open(f'{E}/commit/exam_2026-10-19.json'))
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget', 'Play:Quick-Grow')
CUTD = DRAW[:7]
def cut(line, stadium):
    mesa = 'Mesagoza' in json.dumps(stadium or '')
    for i, l in enumerate(line):
        if l == 'Play:Mesagoza':
            mesa = True
        if l.startswith(CUTD) or (l == 'UseStadium' and mesa):
            return line[:i + 1]
    return list(line)

build = {}
for f in sorted(glob.glob(f'{E}/build/g/*.py')):
    sp = importlib.util.spec_from_file_location('m', f); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    for q in getattr(m, 'POS', []):
        build[q['id']] = q
def run(qs):
    json.dump(qs, open('/tmp/v15_in.json', 'w'), ensure_ascii=False)
    r = subprocess.run([BIN, '--positions', '/tmp/v15_in.json', '--legal-only'] + ARGS, capture_output=True, text=True)
    assert 'PGDUMP' not in r.stderr, 'a search ran!'
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)
    out = {}
    for line in r.stdout.splitlines():
        j = json.loads(line)
        out.setdefault(j['id'], {})[j['kind']] = j
    return out, r.stderr.count('PGDUMP')

lines = []
for p in d['points']:
    a = p['answer']; st0 = p['position'].get('stadium')
    assert not a.get('pending_alternatives') and a['status'] == 'final'
    L = [('his', a['his_move'], cut(a['his_move'], st0), 'record' if a.get('key_line') else 'accepted')]
    if a.get('key_line'):
        assert a['first_segment'] == cut(a['key_line'], st0)
        L += [('key', a['key_line'], cut(a['key_line'], st0), 'accepted')]
    else:
        assert a['first_segment'] == cut(a['his_move'], st0)
    L += [(f'alt{i}', x['line'], cut(x['line'], st0), 'accepted') for i, x in enumerate(a['acceptable'])]
    for tag, line, seg, kind in L:
        lines.append(dict(pid=p['id'], tag=tag, kind=kind, line=line, seg=seg, eng=[to_engine(l) for l in line], pos=p['position']))
print('lines', len(lines), collections.Counter(x['tag'][:3] for x in lines))

qs = []
for x in lines:
    q = copy.deepcopy(x['pos']); q['id'] = f"{x['pid']}|{x['tag']}"; q['force'] = x['eng']; qs.append(q)
out1, pg1 = run(qs)
res = []
for x in lines:
    o = out1[f"{x['pid']}|{x['tag']}"]
    probs = o['position']['problems']
    steps = o['legal']['steps']; stopped = o['legal']['stopped']
    matched = [s for s in steps if s.get('forced') is not None and s.get('matched') is not None]
    unmatched = [s for s in steps if s.get('forced') is not None and s.get('matched') is None]
    chance_stop = stopped.startswith('hidden')
    n = len(matched)
    seg_ok = (n == len(x['seg'])) if chance_stop else (n == len(x['eng']) or (n == len(x['eng']) - 1 and x['eng'][-1] == 'EndTurn'))
    res.append(dict(pid=x['pid'], tag=x['tag'], kind=x['kind'], problems=probs, matched=n, of=len(x['eng']), seg=len(x['seg']),
                    stopped=stopped, unmatched=bool(unmatched), stop_equals_segment=seg_ok, after_chance=None))

qs2, meta = [], {}
for x, r in zip(lines, res):
    if not r['stopped'].startswith('hidden'):
        r['after_chance'] = 'n/a (no chance action in the line)'
        continue
    b = build.get(x['pid'])
    if not b:
        r['after_chance'] = 'unvalidated: no build record'; continue
    draws, vp = b.get('_draws') or {}, b.get('_vpatch')
    orig = b['force']
    pool = []
    for i in sorted(draws, key=int):
        lab = orig[int(i)]
        base = 'UseStadium' if lab == 'Play:Mesagoza' else lab
        pool.append([base, draws[i], False])
    v = copy.deepcopy(x['pos']); hand = list(v['me']['hand']); keep = []; note = []
    ok = True
    for lab in x['eng']:
        is_ch = lab.startswith(DRAW) or (lab == 'UseStadium' and ('Mesagoza' in json.dumps(v.get('stadium')) or 'Play:Mesagoza' in keep))
        if not is_ch:
            keep.append(lab); continue
        base = lab.split('{')[0]
        hit = next((e for e in pool if not e[2] and (e[0] == lab or e[0] == base or (base.startswith('ChooseRandom') and e[0].startswith('Play:Quick-Grow')))), None)
        if lab.startswith('ChooseRandom'):
            continue
        if hit is None:
            if lab == 'UseStadium':
                note.append('Mesagoza coin assumed tails (no record)'); continue
            ok = False; note.append(f'no draw record for {lab}'); break
        hit[2] = True
        if lab.startswith('Play:'):
            name = lab.split(':', 1)[1]
            h = next((c for c in hand if c.startswith(name)), None)
            if h: hand.remove(h)
        for c in hit[1]:
            if c.startswith('-'):
                if c[1:] in hand: hand.remove(c[1:])
            else:
                hand.append(c)
    if not ok:
        r['after_chance'] = 'unvalidated: ' + '; '.join(note); continue
    v['me']['hand'] = hand; v['force'] = keep; v['id'] = f"{x['pid']}|{x['tag']}|v"
    if vp:
        try:
            vp(v)
        except Exception as e:
            r['after_chance'] = f'unvalidated: coin patch failed ({e})'; continue
    qs2.append(v); meta[v['id']] = (r, note, len(keep))
out2, pg2 = run(qs2) if qs2 else ({}, 0)
for vid, (r, note, n) in meta.items():
    o = out2[vid]
    probs = o['position']['problems']; st = o['legal']['stopped']; steps = o['legal']['steps']
    um = [s for s in steps if s.get('forced') is not None and s.get('matched') is None]
    m = len([s for s in steps if s.get('matched') is not None])
    if probs:
        r['after_chance'] = f'variant position problems: {probs}'
    elif um or st.startswith('unmatched'):
        r['after_chance'] = f'FAILED: {st}'
    elif st.startswith('hidden'):
        r['after_chance'] = f'partly: stops again at {st} after {m}/{n}'
    else:
        r['after_chance'] = f'validated ({m}/{n} actions, {st})' + (f"; {'; '.join(note)}" if note else '')
with open(f'{E}/commit/build/vlines_v15.jsonl', 'w') as f:
    for r in res:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
summ = {
    'lines': len(res),
    'by_tag': dict(collections.Counter(r['tag'][:3] for r in res)),
    'pgdump_lines': pg1 + pg2,
    'shipped_position_problems': sum(1 for r in res if r['problems']),
    'shipped_unmatched': [(r['pid'], r['tag'], r['stopped']) for r in res if r['unmatched']],
    'stop_equals_first_segment': sum(1 for r in res if r['stop_equals_segment']),
    'stop_differs': [(r['pid'], r['tag'], r['matched'], r['seg'], r['stopped']) for r in res if not r['stop_equals_segment']],
    'after_chance': dict(collections.Counter(r['after_chance'].split(' (')[0].split(':')[0] for r in res)),
    'after_chance_detail': [(r['pid'], r['tag'], r['after_chance']) for r in res if not r['after_chance'].startswith(('validated', 'n/a'))],
    'new_or_changed_lines': [(r['pid'], r['tag'], r['matched'], r['of'], r['stopped'], r['after_chance']) for r in res
                             if r['pid'] in ('LAD-20261014_161324000_iOS-t5', 'LAD-20261016_031512000_iOS-t2', 'LAD-20261016_031512000_iOS-t8', 'LAD-20261014_215114000_iOS-t10', 'LAD-20261014_225451000_iOS-t4')],
}
json.dump(summ, open(f'{E}/commit/build/VALIDATION_v15.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(summ, indent=1, ensure_ascii=False)[:7000])
