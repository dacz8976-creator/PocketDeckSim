"""Follow-up to integrity_check.py: (1) do G and K differ only in player_codes, with identical decks? (2) what are the
player codes per arm and policy? (3) does each played 20-card list equal its registered deck file, card for card?
Usage: python3 -I integrity2.py <run_dir> <repo>"""
import collections
import json
import os
import re
import sys

run_dir, repo = sys.argv[1], sys.argv[2]
arms = {}
for l in open(os.path.join(run_dir, 'games.jsonl')):
    if l.strip():
        a = json.loads(l)
        arms[a['deal_tag']] = a
deals = [json.loads(l) for l in open(os.path.join(run_dir, 'deals.jsonl')) if l.strip()]


def res(a):
    return json.load(open(os.path.join(run_dir, a['result_file'])))


diff_keys = collections.Counter()
codes = collections.Counter()
for dl in deals:
    g, k = arms[dl['g_deal_tag']], arms[dl['k_deal_tag']]
    rg, rk = res(g), res(k)
    for key in sorted(set(rg['matchup']) | set(rk['matchup'])):
        if rg['matchup'].get(key) != rk['matchup'].get(key):
            diff_keys[key] += 1
    b = dl['bits']
    for arm, r in (('G', rg), ('K', rk)):
        pc = r['matchup'].get('player_codes')
        pilot = pc[b['seat']] if isinstance(pc, list) else pc
        opp = pc[1 - b['seat']] if isinstance(pc, list) else None
        codes[(arm, 'km3' if b['policy'] == 0 else 'kx3', 'pilot=' + str(pilot)[:120], 'opp=' + str(opp)[:120])] += 1
print('matchup keys that differ between G and K, deals:', dict(diff_keys))
print('player codes (arm, opponent policy, pilot seat code, opponent seat code): count')
for key, n in sorted(codes.items()):
    print('  ', key, n)

CARD = re.compile(r'^(\d+)\s+(.+?)\s+([A-Za-z0-9-]+)\s+(\d+)$')


def file_ids(path):
    ids = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or line.lower().startswith('energy'):
            continue
        m = CARD.match(line)
        if not m:
            raise SystemExit('unparsed deck line in %s: %r' % (path, line))
        ids += ['%s %s' % (m.group(3), m.group(4))] * int(m.group(1))
    return collections.Counter(ids)


files = {('deck', 0): 'decks/dustin/09-mega-manectric-heliolisk.txt', ('deck', 1): 'decks/dustin/11-archaludon-haxorus-dragonair.txt',
         ('list', 0): 'decks/screen/opponents/t-lucario.txt', ('list', 1): 'decks/screen/opponents/t-suicune.txt'}
want = {key: file_ids(os.path.join(repo, p)) for key, p in files.items()}
bad = 0
for a in arms.values():
    b = a['bits']
    decks = res(a)['matchup']['decks']
    for key, seat in ((('deck', b['deck']), b['seat']), (('list', b['list']), 1 - b['seat'])):
        if collections.Counter(decks[seat]['card_ids']) != want[key]:
            bad += 1
            if bad <= 3:
                print('MISMATCH', a['deal_tag'], key, 'seat', seat)
for key in sorted(want):
    print('%s=%d: %s, %d cards' % (key[0], key[1], files[key], sum(want[key].values())))
print('played lists that differ from their file: %d of %d checks' % (bad, 2 * len(arms)))
print('INTEGRITY2 %s' % ('OK' if bad == 0 and set(diff_keys) <= {'player_codes'} else 'PROBLEMS'))
