"""Cross-check the converted boards against the readable guide-supplement tables (independent fresh reads by another worker) where a game has one."""
import json, re, os
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD/'
P = json.load(open('/home/dacz8976/pgd/bd_positions.json', encoding='utf-8'))
by = {p['id']: p for p in P}
cell_re = re.compile(r'^(?P<name>.+?) (?P<hp>\d+)/(?P<mx>\d+) HP, W(?P<w>\d+)(?P<cape> \+ Cape)?$')
bad = checked = 0
for g in sorted(os.listdir(B)):
    if not g.startswith('2026100') or not os.path.isdir(B + g):
        continue
    md = B + g + '/GUIDE_UPDATE_SUPPLEMENT.md'
    txt = open(md, encoding='utf-8').read()
    rows = [l for l in txt.splitlines() if re.match(r'^\|\s*\d+\s*\|\s*[\d.]+\s*\|', l)]
    if not rows:
        continue
    short = g[9:15]
    for r in rows:
        cells = [c.strip() for c in r.strip().strip('|').split('|')]
        tn = int(cells[0])
        pid = f'B-{short}-t{tn:02d}'
        p = by.get(pid)
        if not p:
            print(pid, 'MISSING position'); bad += 1; continue
        for side, cell, key in (('me', cells[2], 'me'), ('opp', cells[3], 'opp')):
            parts = [x.strip() for x in re.split(r';| / ', cell)]
            parts = [x for x in parts if x and x != 'empty']
            want = []
            for x in parts:
                m = cell_re.match(x)
                if not m:
                    want.append(('?', x)); continue
                want.append((m['name'], int(m['hp']), int(m['w'])))
            have = []
            for b in p[key]['board']:
                nm = b['card'].rsplit(' ', 2)[0]
                have.append((nm, b['hp'], len(b.get('energy', []))))
            checked += 1
            if want != have:
                bad += 1
                print(pid, side, 'DIFF\n   supplement:', want, '\n   position  :', have)
        pts = cells[4]
        m = re.match(r'(\d+)-(\d+)', pts)
        if m and [int(m[1]), int(m[2])] != p['points']:
            bad += 1; print(pid, 'POINTS', pts, p['points'])
print('sides checked', checked, 'differences', bad)
