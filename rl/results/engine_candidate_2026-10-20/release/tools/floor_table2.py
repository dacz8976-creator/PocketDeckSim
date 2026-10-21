#!/usr/bin/env python3
"""The floor re-check sort for the release notes, both builds: one row per piece with the recorded verdict (main-c045ede),
the Oct 20 build's (lane A, $W/floor2) and the final build's ($W/floor2F), each build compared with the recorded page, and
the final build compared with the Oct 20 build where it differs from the recorded page. Prints the markdown table, then a
JSON line {short, sort, ...}. Sorting rule (PLAN addendum): final differs where the Oct 20 build doesn't -> item 8 (a, if
a holder meets a brought-in card in that row, else c); both differ -> the Oct 20 attribution (Growl, t-lucario)."""
import importlib.util, json, re, sys
from pathlib import Path

W = Path('/home/dacz8976/pincand_work')
spec = importlib.util.spec_from_file_location('floor2', W / 'floor2.py')
F2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F2)
VERD = re.compile(r'^\*\*Verdict: (.+?)\*\* (\d+) wins in (\d+) games', re.M)


def verdict(md):
    if not Path(md).exists():
        return '?'
    t = Path(md).read_text(encoding='utf-8')
    m = VERD.search(t)
    if m:
        return f'{m.group(1).rstrip(".")}, {int(m.group(2)):,} of {int(m.group(3)):,}'
    m = re.search(r'(\d+) wins in (\d+) games', t)
    return f'{int(m.group(1)):,} of {int(m.group(2)):,} wins' if m else '?'


def summ(folder):
    p = W / folder / 'summary.tsv'
    return {l.split('\t')[0]: (l.rstrip('\n').split('\t') + [''] * 5)[:5] for l in p.read_text().splitlines() if l} if p.exists() else {}


C, F = summ('floor2'), summ('floor2F')
rows, out = [], dict(c_same=[], f_same=[], f_only=[], both=[], other=[])
for piece, (kind, deck, extra, ref, name) in F2.PIECES.items():
    c, f = C.get(piece), F.get(piece)
    cv, fv = (c[3] if c else 'not run'), (f[3] if f else 'not run')
    if kind == 'screen':
        old = 'run_screen, 20 lines'
        cw = cv
        fw = fv
    else:
        refmd = (F2.REF / 'pages' / ref.split(':', 1)[1] / f'{name}.md') if isinstance(ref, str) and ref.startswith('STRIP:') else Path(ref) / f'{name}.md'
        old = verdict(refmd)
        cw = f'{cv}: {verdict(W / "floor2" / piece / f"{name}.md")}'
        fw = f'{fv}: {verdict(W / "floor2F" / piece / f"{name}.md")}'
    if cv == 'SAME':
        out['c_same'].append(piece)
    if fv == 'SAME':
        out['f_same'].append(piece)
    elif fv == 'DIFFERS' and cv == 'SAME':
        out['f_only'].append(piece)
    elif fv == 'DIFFERS' and cv == 'DIFFERS':
        out['both'].append(piece)
    else:
        out['other'].append(piece)
    det = (f[4] if f else '')[:160].replace('|', '/')
    rows.append(f'| {piece} | {old} | {cw} | {fw} | {det} |')
print('| Piece (1,920 games; run_screen 3,840) | Recorded on main-c045ede | Oct 20 build (245e11e8) v recorded | Final build v recorded | Final build: detail |')
print('|---|---|---|---|---|')
print('\n'.join(rows))
n = len(F2.PIECES)
games = sum(int(F[p][1] or 0) for p in F if p in F2.PIECES)
out['games_final'] = games
out['short'] = (f'all {n} pieces equal to the recorded pages ({games:,} games)' if len(out['f_same']) == n else
                f"{len(out['f_same'])} of {n} pieces equal to the recorded pages; different: {', '.join(out['f_only'] + out['both'] + out['other'])}")
print(json.dumps(out))
