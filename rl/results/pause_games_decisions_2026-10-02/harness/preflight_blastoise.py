"""Preflight for the draft A v Blastoise/Wailord batch: (1) OWNER_DECK_SNAPSHOT.json == the repo's draft A list, card for card; (2) every card of the opponent's list (and his) is
Complete in the pinned engine's card_status inventory (checked for every printing of the name, since the opponent's printings are not known)."""
import json, collections, sys, re

B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD/'
REPO = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/'

snap = json.load(open(B + 'OWNER_DECK_SNAPSHOT.json', encoding='utf-8'))
mine = collections.Counter((c['name'], c['variant']) for c in snap['cards_in_log_order'])
repo = collections.Counter()
for line in open(REPO + 'decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('Energy'):
        continue
    p = line.split()
    repo[(' '.join(p[1:-2]), ' '.join(p[-2:]))] += int(p[0])
print('1. owner snapshot == repo draft A list:', mine == repo, '| snapshot total', sum(mine.values()), '| repo total', sum(repo.values()), '| energy', snap['energy_configuration'])
if mine != repo:
    print('   only in snapshot:', dict(mine - repo)); print('   only in repo:', dict(repo - mine))

st = json.load(open('/home/dacz8976/pgd/card_status.json', encoding='utf-8'))['cards']
byname = collections.defaultdict(list)
for c in st:
    byname[c['name']].append(c)
opp = json.load(open(B + 'OPPONENT_DECK.json', encoding='utf-8'))
print('2. opponent list:', opp['counts_by_name'], '| total', opp['total_card_slots'])
bad = []
names = list(opp['counts_by_name']) + sorted({n for n, _ in mine})
for n in names:
    rows = byname.get(n, [])
    if not rows:
        print(f'   {n}: NOT IN THE ENGINE DATABASE'); bad.append(n); continue
    stat = collections.Counter(r['status'] if isinstance(r['status'], str) else json.dumps(r['status']) for r in rows)
    lim = sorted({l for r in rows for l in r['limitations']})
    flag = '' if set(stat) == {'Complete'} else '   <-- NOT ALL COMPLETE'
    if flag:
        bad.append(n)
    who = 'opp' if n in opp['counts_by_name'] else 'mine'
    print(f"   [{who}] {n}: {len(rows)} printings {dict(stat)}{flag}")
    for l in lim:
        print('        limitation:', l)
    if flag:
        for r in rows:
            if r['status'] != 'Complete':
                print('        ', r['id'], r['status'])
print('NOT FULLY COMPLETE / MISSING:', bad)
