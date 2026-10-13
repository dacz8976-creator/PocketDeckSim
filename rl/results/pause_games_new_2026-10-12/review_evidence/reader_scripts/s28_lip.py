import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
nk, nname = C['nk'], C['nname']
for g in GAMES:
    if short_of(g) not in {p['game'][3:] for p in POS}:
        continue
    for t in led(g)['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for pl in t.get('plays_in_order') or []:
            if nname(pl.get('card_name')) != 'Lucky Ice Pop':
                continue
            res = str(pl.get('result') or '')
            returns = bool(re.search(r'return\w*\b[^.;]*\bhand|back (?:to|into) (?:his |the )?hand', res, re.I) and re.search(r'heads', res, re.I))
            print(short_of(g), 't%02d' % t['turn_number'], pl.get('kind'), '| converter returns-to-hand:', returns, '|', res[:160])
# discard rebalancing notes
print()
for p in POS:
    for m in re.findall(r'one ([^;.]+?) taken out of the discard guess', p['notes']):
        print(p['id'], 'rebalanced discard:', m)
