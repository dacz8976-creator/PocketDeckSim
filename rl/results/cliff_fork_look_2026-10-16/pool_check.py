"""Which of our decks can the Cliff fork's engine and card pool run?

Read-only check. Needs two files from https://github.com/IncredibleAloeVera/deckgym-core (main, 2026-08-13):
database.json and auxiliaries/card_status.txt, saved in one folder (database.json at its top, card_status.txt in
its auxiliaries/ sub-folder). Point FORK_FILES at that folder and run:  FORK_FILES=/path python3 pool_check.py
(The default is the scratch folder this check was run from; the output of that run is pool_check_output.txt.)
"""
import json, re, glob, os, collections

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.environ.get('FORK_FILES', '/home/dacz8976/upstream_cmp/cliff/files/').rstrip('/') + '/'
R = os.path.abspath(os.path.join(HERE, '..', '..', '..')) + '/'
db = json.load(open(F + 'database.json'))
ids = {}
names = collections.defaultdict(list)
for c in db:
    k = next(iter(c))
    v = c[k]
    ids[v['id']] = (k, v)
    names[v['name']].append(v['id'])
print('fork cards', len(ids))
sets = collections.Counter(i.split(' ')[0] for i in ids)
print('fork sets', dict(sorted(sets.items())))

inc = {}
for line in open(F + 'auxiliaries/card_status.txt', encoding='utf-8'):
    m = re.match(r'^(\S+ \S+)\s+(.+?)\s{2,}(.+)$', line.rstrip('\n'))
    if m and m.group(1) in ids:
        inc[m.group(1)] = (m.group(2), m.group(3))
print('incomplete listed', len(inc))

decks = {
    'dustin 01 kingambit as played': 'decks/dustin/01-kingambit-as-played.txt',
    'dustin 01 muk-glimmora-kingambit-regigigas': 'decks/dustin/01-muk-glimmora-kingambit-regigigas.txt',
    'brew 07': 'decks/brews/brew-07-hoopa-darkrai-sableye.txt',
    'deck 12': 'decks/dustin/12-ariados-whimsicott-ogerpon.txt',
    'deck 13-a': 'decks/dustin/13-a-ninetales-raticate.txt',
    'brew 08': 'decks/brews/brew-08-entei-rainbow-cave.txt',
    'brew 09': 'decks/brews/brew-09-sableye-obstagoon.txt',
    'draft A (wallace)': 'decks/brews/drafts_2026-10-01/draft-A-wallace.txt',
    'draft A shark': 'decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt',
    'draft D': 'decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt',
    'brew 10': 'decks/brews/brew-10-diancie-giratina.txt',
}
for f in sorted(glob.glob(R + 'decks/screen/opponents/t-*.txt')):
    decks['panel ' + os.path.basename(f)[2:-4]] = os.path.relpath(f, R).replace('\\', '/')
pat = re.compile(r'^(\d+)\s+(?:(.*?)\s+)?([A-Za-z0-9\-]+ \d+)\s*$')
total_missing = collections.Counter()
for label, rel in decks.items():
    p = R + rel
    if not os.path.exists(p):
        print('MISSING FILE', label, rel)
        continue
    n = 0
    notin = []
    broken = []
    reprint = []
    for line in open(p, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith(('#', 'Energy')):
            continue
        m = pat.match(line)
        if not m:
            print('  unparsed:', line)
            continue
        cnt = int(m.group(1))
        nm = m.group(2)
        cid = m.group(3)
        n += cnt
        if cid not in ids:
            alt = names.get(nm, [])
            notin.append((cnt, nm, cid, alt))
        else:
            fname = ids[cid][1]['name']
            if cid in inc:
                broken.append((cnt, fname, cid, inc[cid][1]))
    print(f'== {label}: {n} cards; not in fork DB: {len(notin)}; in DB but engine-incomplete: {len(broken)}')
    for x in notin:
        print('   NOT IN DB  ', x)
        total_missing[(x[1], x[2])] += 1
    for x in broken:
        print('   INCOMPLETE ', x)
        total_missing[(x[1], x[2], 'incomplete')] += 1
