"""for every QR entity's printing_aliases in the 14 packets: do the aliases share one function (cardlib SIG)? and does the deck file's printing belong to it?"""
import json, os, re, sys, collections
REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
sys.path.insert(0, REPO + '/rl/results/pause_games_new_2026-10-12/harness')
import cardlib as C
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
V2 = REPO + '/rl/results/pause_games_new_2026-10-13/v2'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
ent_alias = {}
for g in games:
    p = os.path.join(g, 'QR_DECODE.json')
    j = json.load(open(p, encoding='utf-8'))
    for c in j.get('cards') or []:
        if c.get('printing_aliases'):
            ent_alias[(C.nname(c['name']), c['entity_id'])] = c['printing_aliases']
print('entities with aliases:')
for (nm, e), al in sorted(ent_alias.items(), key=str):
    sigs = collections.OrderedDict()
    for a in al:
        sigs.setdefault(C.SIG.get(a), []).append(a)
    print(f'  {nm} ent={e}: {al} -> {len(sigs)} function(s)', '' if len(sigs) == 1 else ' <-- SEVERAL: ' + str(list(sigs.values())))
# deck files: each printing in one of the entity alias lists of its name
print('deck files v QR aliases:')
for g in games:
    short = os.path.basename(g).replace('_iOS', '')[2:]
    lines = open(os.path.join(V2, 'decks', f'KW{short}.txt'), encoding='utf-8').read().splitlines()
    for l in lines[1:]:
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})$', l.strip())
        nm, pid = C.nname(m.group(2)), m.group(3)
        als = [al for (n, e), al in ent_alias.items() if n == nm]
        if not als:
            print(f'  {short}: {nm} {pid}: no alias list known')
            continue
        ok = any(pid in al for al in als)
        same = any(any(C.same_function(pid, a) for a in al) for al in als)
        if not ok:
            print(f'  {short}: {nm} {pid} NOT among aliases {als}; same function as one: {same}')
# all functions of each name in the decks
print('functions per name:')
names = set()
for g in games:
    short = os.path.basename(g).replace('_iOS', '')[2:]
    for l in open(os.path.join(V2, 'decks', f'KW{short}.txt'), encoding='utf-8').read().splitlines()[1:]:
        m = re.match(r'(\d+) (.+) ([A-Za-z0-9\-]+ \d{3})$', l.strip())
        names.add(C.nname(m.group(2)))
for n in sorted(names):
    print(f'  {n}: {C.functions(n)}')
