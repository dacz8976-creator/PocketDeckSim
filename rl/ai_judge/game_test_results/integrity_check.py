"""Stage 2 integrity check over all 256 arm rows (after stage 2 ended): is the pilot really at bits.seat, with the right deck,
the right opponent list and policy, the same seed and decks in both arms, the real model, and an outcome equal to state_winner?
Usage: python3 -I integrity_check.py <run_dir> <repo>"""
import collections
import json
import os
import sys

run_dir, repo = sys.argv[1], sys.argv[2]
arms = [json.loads(l) for l in open(os.path.join(run_dir, 'games.jsonl')) if l.strip()]
deals = {json.loads(l)['deal_idx']: json.loads(l) for l in open(os.path.join(run_dir, 'deals.jsonl')) if l.strip()}
plan = json.load(open('/home/dacz8976/relplan/gemini/stage2/stage2.plan.json'))

first = arms[1]
print('protocol entries of one arm:')
for p in first['protocol']:
    print('  ', json.dumps({k: v for k, v in p.items() if not k.endswith('_secs_sum') and not k.endswith('_secs_max')})[:300])
rf = first['result_file']
r = json.load(open(os.path.join(run_dir, rf)))
print('matchup keys:', sorted(r['matchup']), '; deck entry keys:', sorted(r['matchup']['decks'][0]))
for i, dk in enumerate(r['matchup']['decks']):
    print('  deck %d:' % i, json.dumps({k: v for k, v in dk.items() if k != 'card_ids'})[:300], 'cards', len(dk['card_ids']))
print('plan keys:', sorted(plan) if isinstance(plan, dict) else type(plan).__name__)


def deck_cards(path):
    out = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        out.append(line)
    return out


print('--- checks over all arms')
bad = collections.Counter()
examples = {}
seen_decks = collections.defaultdict(set)   # (bit name, value) -> card multisets seen at that seat
opp_bots = collections.defaultdict(set)
models = collections.Counter()
for a in arms:
    tag = a['deal_tag']
    b = a['bits']
    seat = b['seat']
    r = json.load(open(os.path.join(run_dir, a['result_file'])))
    pilot = [p for p in a['protocol'] if p.get('role') == 'pilot']
    others = [p for p in a['protocol'] if p.get('role') != 'pilot']

    def flag(name, detail):
        bad[name] += 1
        examples.setdefault(name, '%s: %s' % (tag, detail))
    if len(pilot) != 1 or pilot[0].get('seat') != seat:
        flag('pilot seat != bits.seat', json.dumps(pilot)[:200])
    if r.get('outcome') != r.get('state_winner'):
        flag('outcome != state_winner', '%s v %s' % (r.get('outcome'), r.get('state_winner')))
    if r['randomness']['game_seed'] != a['seed']:
        flag('game_seed != arm seed', '%s v %s' % (r['randomness']['game_seed'], a['seed']))
    if a['seed'] != 25103000000 + 100 * a['cell'] + a['k']:
        flag('seed != registered formula', a['seed'])
    if a['cell'] != 8 * b['deck'] + 4 * b['list'] + 2 * b['policy'] + b['seat']:
        flag('cell != bits', a['cell'])
    if r.get('completion') != 'completed' or a.get('completion') != 'completed':
        flag('not completed', '%s/%s' % (r.get('completion'), a.get('completion')))
    decks = r['matchup']['decks']
    seen_decks[('deck', b['deck'])].add(tuple(sorted(decks[seat]['card_ids'])))
    seen_decks[('list', b['list'])].add(tuple(sorted(decks[1 - seat]['card_ids'])))
    for p in others:
        opp_bots[b['policy']].add(json.dumps({k: v for k, v in p.items() if k in ('role', 'bot', 'name', 'policy', 'kind')}, sort_keys=True))
    if a['arm'] == 'G':
        j = a['judge']
        models[json.dumps(j.get('model_returned'))] += 1
        if j.get('mock'):
            flag('G mock', 'mock true')
        if not j.get('calls'):
            flag('G with 0 calls', j.get('calls'))
    if a['arm'] == 'K' and a.get('judge'):
        flag('K arm has a judge block', '')

# the paired arms of each deal: same seed, same decks, same seats
for idx, dl in deals.items():
    g = next(a for a in arms if a['deal_tag'] == dl['g_deal_tag'])
    k = next(a for a in arms if a['deal_tag'] == dl['k_deal_tag'])
    rg = json.load(open(os.path.join(run_dir, g['result_file'])))
    rk = json.load(open(os.path.join(run_dir, k['result_file'])))
    if rg['matchup'] != rk['matchup']:
        bad['G and K matchup differ'] += 1
        examples.setdefault('G and K matchup differ', str(idx))
    if rg['randomness']['game_seed'] != rk['randomness']['game_seed']:
        bad['G and K game seed differ'] += 1

print('model_returned over G rows:', dict(models))
for key in sorted(seen_decks):
    print('distinct card lists at %s=%d: %d' % (key[0], key[1], len(seen_decks[key])))
print('opponent protocol entries by policy bit:', {k: sorted(v) for k, v in opp_bots.items()})

# compare the pilot decks and opponent lists with the files named in the registration
files = {('deck', 0): 'decks/dustin/09-mega-manectric-heliolisk', ('deck', 1): 'decks/dustin/11-archaludon-haxorus-dragonair',
         ('list', 0): 'decks/screen/opponents/t-lucario', ('list', 1): 'decks/screen/opponents/t-suicune'}
for key, stem in files.items():
    cands = [stem + ext for ext in ('.txt', '', '.deck')]
    path = next((os.path.join(repo, c) for c in cands if os.path.isfile(os.path.join(repo, c))), None)
    if path is None:
        print('%s=%d: file %s.* not in the clone, not compared' % (key[0], key[1], stem))
        continue
    raw = deck_cards(path)
    print('%s=%d: %s has %d non-comment lines; first lines %s' % (key[0], key[1], os.path.relpath(path, repo), len(raw), raw[:3]))
    lists = seen_decks[key]
    if len(lists) == 1:
        played = list(next(iter(lists)))
        print('   played list (%d cards), first %s' % (len(played), played[:4]))

print('PROBLEMS: %s' % (dict(bad) if bad else 'none'))
for name, ex in examples.items():
    print('  e.g. %s -> %s' % (name, ex))
print('INTEGRITY %s' % ('OK' if not bad else 'PROBLEMS'))
