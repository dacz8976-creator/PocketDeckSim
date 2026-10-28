# Add up the 10-game Gemini v Codex check from each game's score/score.json, against the rules set before the check.
import json, pathlib, sys, re

root = pathlib.Path(sys.argv[1])
rows, tot = [], {'Gmaj': 0, 'Gmin': 0, 'Xmaj': 0, 'Xmin': 0, 'Gr': 0, 'Xr': 0, 'bw': 0, 'un': 0}
sheets = {'gemini': [0, 0], 'gemini_cheap': [0, 0], 'codex': [0, 0]}
flags = []
KEY = re.compile(r'result|winner|final.?score|concede|concession|end of game|how the game ended|opponent pok[eé]mon|main attacker|wrong pok[eé]mon|card name', re.I)
for d in sorted(p for p in root.iterdir() if p.is_dir()):
    j = json.loads((d / 'score' / 'score.json').read_text(encoding='utf-8'))
    g, x, v = j['G'], j['X'], j['verdicts']
    tot['Gmaj'] += g['major']; tot['Gmin'] += g['minor']; tot['Xmaj'] += x['major']; tot['Xmin'] += x['minor']
    tot['Gr'] += v['G_right']; tot['Xr'] += v['X_right']; tot['bw'] += v['both_wrong']; tot['un'] += v['unsettled']
    for k in sheets:
        s = j['sheets'].get(k)
        if s:
            sheets[k][0] += s['right']; sheets[k][1] += s['checked']
    for e in j.get('errors', []):
        if e.get('grade') == 'major' and KEY.search(' '.join(str(e.get(f, '')) for f in ('item', 'says', 'truth'))):
            flags.append(f"{d.name[16:]} [{e['review']}] {e.get('turn','')} {e.get('item','')}: says {e.get('says','')} / truth {e.get('truth','')}")
    rows.append(f"{d.name[16:]:<24} G {g['major']}/{g['minor']}  X {x['major']}/{x['minor']}  verdicts G{v['G_right']} X{v['X_right']} bw{v['both_wrong']} un{v['unsettled']}")
print('\n'.join(rows))
print(f"\nTOTAL majors G {tot['Gmaj']} v X {tot['Xmaj']}; minors G {tot['Gmin']} v X {tot['Xmin']}")
print(f"verdicts: G right {tot['Gr']}, X right {tot['Xr']}, both wrong {tot['bw']}, unsettled {tot['un']}")
for k, (r, c) in sheets.items():
    print(f"sheet {k}: {r}/{c} = {100 * r / c:.1f}%")
print(f"\nrule 1 (G majors <= X majors): {'PASS' if tot['Gmaj'] <= tot['Xmaj'] else 'FAIL'}")
r, c = sheets['gemini_cheap']
print(f"rule 2 (cheap sheet >= 95%): {'cheap sheet' if r / c >= 0.95 else 'full sheet'} ({100 * r / c:.1f}%)")
print('\nmajor errors that mention the result or an opponent Pokemon (check by hand):')
print('\n'.join(flags) or '(none)')
