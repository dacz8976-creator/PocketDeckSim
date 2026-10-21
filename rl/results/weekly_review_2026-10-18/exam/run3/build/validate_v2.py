"""Exam v2's legality checks: v1.6's validate_v15.py (~/exam/commit/build/), copied and edited only where v2 differs. No bot is ever built or asked.
  validate_v2.py EXAM_JSON OUT_DIR
Edits from v15: the chance-step rule is v2_helpers' (one place for every v2 script: v1.6's tuple plus Dustox's Variety Powder by slot), the
decks are ~/exam_v2/bin/decks.args (the v2 deck files), the build records are ~/exam_v2/build/g/*.py, and the inputs/outputs are arguments.
The tool is v1.6's frozen pg_legal_v14 (~/exam/bin, read only), whose database equals frozen-7's (b5e68fc8).
Lines: his recorded move (a 'record' where his key was overridden), the key line where Dustin overrode it, and every acceptable line.
(1) shipped: each line forced on the candidate position; every action up to the first chance action must be legal, and the tool must
    stop exactly there (= the line's first segment) when it stops at a hidden draw or coin.
(2) after the chance: a verification variant per line, with the build's recorded draws put in the hand up front, the chance actions
    removed and coin results applied (the build's own _draws/_vpatch); every remaining action must match.
Writes OUT_DIR/vlines_v2.jsonl and OUT_DIR/VALIDATION_v2.json."""
import json, os, sys, glob, copy, subprocess, importlib.util, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from label_adapter import to_engine
from v2_helpers import DRAW, cut, chance_steps, Uncertain
E2 = os.path.expanduser('~/exam_v2')
BIN = os.path.expanduser('~/exam/bin/pg_legal_v14')
with open(f'{E2}/bin/decks.args') as f:
    ARGS = f.read().split()


def run(qs, tmp):
    with open(tmp, 'w') as f:
        json.dump(qs, f, ensure_ascii=False)
    r = subprocess.run([BIN, '--positions', tmp, '--legal-only'] + ARGS, capture_output=True, text=True)
    assert 'PGDUMP' not in r.stderr, 'a search ran!'
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)
    out = {}
    for line in r.stdout.splitlines():
        j = json.loads(line)
        out.setdefault(j['id'], {})[j['kind']] = j
    return out, r.stderr.count('PGDUMP')


def main(exam_json, out_dir):
    with open(exam_json, encoding='utf-8') as f:
        d = json.load(f)
    build = {}
    for fn in sorted(glob.glob(f'{E2}/build/g/*.py')):
        sp = importlib.util.spec_from_file_location('m', fn); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        for q in getattr(m, 'POS', []):
            build[q['id']] = q
    lines, uncertain = [], []
    for p in d['points']:
        a = p['answer']; pos = p['position']
        assert not a.get('pending_alternatives') and a['status'] == 'final'
        try:
            L = [('his', a['his_move'], cut(a['his_move'], pos), 'record' if a.get('key_line') else 'accepted')]
            if a.get('key_line'):
                assert a['first_segment'] == cut(a['key_line'], pos)
                L += [('key', a['key_line'], cut(a['key_line'], pos), 'accepted')]
            else:
                assert a['first_segment'] == cut(a['his_move'], pos)
            L += [(f'alt{i}', x['line'], cut(x['line'], pos), 'accepted') for i, x in enumerate(a['acceptable'])]
        except Uncertain as e:
            uncertain.append(str(e)); continue
        for tag, line, seg, kind in L:
            lines.append(dict(pid=p['id'], tag=tag, kind=kind, line=line, seg=seg, eng=[to_engine(l) for l in line], pos=pos))
    print('lines', len(lines), collections.Counter(x['tag'][:3] for x in lines), 'uncertain cuts', len(uncertain))

    qs = []
    for x in lines:
        q = copy.deepcopy(x['pos']); q['id'] = f"{x['pid']}|{x['tag']}"; q['force'] = x['eng']; qs.append(q)
    out1, pg1 = run(qs, os.path.join(out_dir, 'v2_in.json'))
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
        # v2: a chance Ability (Dustox) is a cut the tool does not stop at; the segment is then checked by the line matching in full
        res.append(dict(pid=x['pid'], tag=x['tag'], kind=x['kind'], problems=probs, matched=n, of=len(x['eng']), seg=len(x['seg']),
                        stopped=stopped, unmatched=bool(unmatched), stop_equals_segment=seg_ok, after_chance=None,
                        cut_by_ability=len(x['seg']) < len(x['line']) and x['seg'][-1].startswith('Ability')))

    qs2, meta = [], {}
    for x, r in zip(lines, res):
        ch = set(chance_steps(x['eng'], x['pos']))
        if not ch:
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
        for k, lab in enumerate(x['eng']):
            if k not in ch:
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
    out2, pg2 = run(qs2, os.path.join(out_dir, 'v2_in2.json')) if qs2 else ({}, 0)
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
    with open(os.path.join(out_dir, 'vlines_v2.jsonl'), 'w') as f:
        for r in res:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    summ = {
        'lines': len(res),
        'by_tag': dict(collections.Counter(r['tag'][:3] for r in res)),
        'uncertain_cuts': uncertain,
        'pgdump_lines': pg1 + pg2,
        'shipped_position_problems': sum(1 for r in res if r['problems']),
        'shipped_unmatched': [(r['pid'], r['tag'], r['stopped']) for r in res if r['unmatched']],
        'stop_equals_first_segment': sum(1 for r in res if r['stop_equals_segment']),
        'stop_differs': [(r['pid'], r['tag'], r['matched'], r['seg'], r['stopped']) for r in res if not r['stop_equals_segment']],
        'cut_by_chance_ability': [(r['pid'], r['tag'], r['seg']) for r in res if r['cut_by_ability']],
        'after_chance': dict(collections.Counter(r['after_chance'].split(' (')[0].split(':')[0] for r in res)),
        'after_chance_detail': [(r['pid'], r['tag'], r['after_chance']) for r in res if not r['after_chance'].startswith(('validated', 'n/a'))],
    }
    with open(os.path.join(out_dir, 'VALIDATION_v2.json'), 'w') as f:
        json.dump(summ, f, indent=1, ensure_ascii=False)
    print(json.dumps(summ, indent=1, ensure_ascii=False)[:7000])
    return summ


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('usage: validate_v2.py EXAM_JSON OUT_DIR')
    main(sys.argv[1], sys.argv[2])
