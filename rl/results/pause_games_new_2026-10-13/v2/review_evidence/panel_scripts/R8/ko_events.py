"""per game: every row's automatic events and attack results that mention a knock-out / Shattering Crystal / points, plus point totals at each row start; and the owner Pokemon that leave the board between rows (by name multiset)"""
import json, os, re, sys, collections
REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
sys.path.insert(0, REPO + '/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
sel = sys.argv[1] if len(sys.argv) > 1 else ''
KO = re.compile(r'knock|\bKO|Shattering|point', re.I)


def names(side):
    side = side or {}
    out = []
    for p in [side.get('active')] + list(side.get('bench_in_position_order') or []):
        if isinstance(p, dict) and p.get('name') and str(p['name']).lower() not in ('none', 'empty', 'null'):
            out.append(C.nname(p['name']))
    return collections.Counter(out)


for g in games:
    if sel not in g:
        continue
    print('=' * 20, os.path.basename(g))
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    prev_after = None
    for t in led['turns']:
        b0, b1 = t.get('board_at_start') or {}, t.get('board_after') or {}
        pts0 = ((b0.get('owner') or {}).get('points'), (b0.get('opponent') or {}).get('points'))
        pts1 = ((b1.get('owner') or {}).get('points'), (b1.get('opponent') or {}).get('points'))
        texts = []
        for p in t.get('plays_in_order') or []:
            s = str(p.get('result') or p.get('details') or '')
            if KO.search(s):
                texts.append(f'[{p.get("kind")}] {s[:200]}')
        for e in t.get('automatic_events_in_order') or []:
            s = e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
            if KO.search(s):
                texts.append('AUTO ' + s[:250])
        gone_mine = names(b0.get('owner')) - names(b1.get('owner'))
        between = (prev_after - names(b0.get('owner'))) if prev_after is not None else collections.Counter()
        print(f" t{t['turn_number']} {t['who_played'][:5]} pts {pts0}->{pts1} | his gone in row {dict(gone_mine)} | gone between rows {dict(between)}")
        for x in texts:
            print('      ' + x)
        prev_after = names(b1.get('owner'))
