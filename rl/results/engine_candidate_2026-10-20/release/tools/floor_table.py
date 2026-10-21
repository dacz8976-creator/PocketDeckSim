#!/usr/bin/env python3
"""The floor re-check sort for the release notes: one markdown row per piece (recorded page v the candidate's), from
/home/dacz8976/pincand_work/floor2/summary.tsv and the pages. Prints the table, then a JSON line {short, sort}."""
import importlib.util, json, re, sys
from pathlib import Path

W = Path('/home/dacz8976/pincand_work')
spec = importlib.util.spec_from_file_location('floor2', W / 'floor2.py')
F = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F)
VERD = re.compile(r'^\*\*Verdict: (.+?)\*\* (\d+) wins in (\d+) games', re.M)


def verdict(md):
    t = Path(md).read_text(encoding='utf-8')
    m = VERD.search(t)
    if m:
        return f'{m.group(1).rstrip(".")}, {int(m.group(2)):,} of {int(m.group(3)):,}'
    m = re.search(r'(\d+) wins in (\d+) games', t)
    return f'{int(m.group(1)):,} of {int(m.group(2)):,} wins' if m else '?'


rows, same, differ, err = [], [], [], []
summ = {l.split('\t')[0]: l.rstrip('\n').split('\t') for l in (W / 'floor2/summary.tsv').read_text().splitlines() if l}
for piece, (kind, deck, extra, ref, name) in F.PIECES.items():
    s = summ.get(piece)
    if not s:
        rows.append(f'| {piece} | | not run | |'); err.append(piece); continue
    _, games, secs, v, detail = (s + [''] * 5)[:5]
    if kind == 'screen':
        old, new = 'run_screen, 20 lines', 'run_screen, 20 lines'
        cmpw = 'all 20 lines equal' if v == 'SAME' else detail
    else:
        refmd = (F.REF / 'pages' / ref.split(':', 1)[1] / f'{name}.md') if isinstance(ref, str) and ref.startswith('STRIP:') else Path(ref) / f'{name}.md'
        old = verdict(refmd)
        newmd = W / 'floor2' / piece / f'{name}.md'
        new = verdict(newmd) if newmd.exists() else '?'
        cmpw = ('every game equal (14 summary fields), coverage byte-equal, page equal but for the program path' if v == 'SAME' else detail)
    (same if v == 'SAME' else differ if v == 'DIFFERS' else err).append(piece)
    rows.append(f'| {piece} ({int(games or 0):,} games) | {old} | {new} | {v}: {cmpw} |')
print('| Piece | Recorded on main-c045ede | On the candidate | Comparison |')
print('|---|---|---|---|')
print('\n'.join(rows))
n = len(F.PIECES)
games = sum(int(summ[p][1]) for p in summ if p in F.PIECES)
short = (f'all {n} pieces equal to the recorded pages ({games:,} games)' if len(same) == n
         else f'{len(same)} of {n} equal, {len(differ)} differ ({", ".join(differ)}), {len(err)} not compared ({", ".join(err)})')
sort = ('Sort: (a) rule fix 0, (b) upstream change 0, (c) unexplained 0. Every page keeps its recorded verdict and wins.'
        if len(same) == n else 'Sort: see the per-page notes below.')
print(json.dumps(dict(short=short, sort=sort, same=same, differ=differ, err=err, games=games)))
