#!/usr/bin/env python3
"""split_new.py TMP OUT QA: keep the positions, the report and the games_meta of the 14 new games (BATCH_2026-10-12_NEW_LONG_VIDEOS, _ADDITIONAL_TWO, 2026-10-13_NEWEST_TWO, _REMAINING_SIX) out of a conversion of all 38 games."""
import glob, json, os, sys

tmp, out, qa = sys.argv[1:4]
BATCHES = ('BATCH_2026-10-12_NEW_LONG_VIDEOS', 'BATCH_2026-10-12_ADDITIONAL_TWO', 'BATCH_2026-10-13_NEWEST_TWO', 'BATCH_2026-10-13_REMAINING_SIX')
NEW = {os.path.basename(d).replace('_iOS', '')[2:] for b in BATCHES for d in glob.glob(os.path.join(qa, b, '2026*'))}      # '261013_010003000'
pos = [p for p in json.load(open(os.path.join(tmp, 'positions_all.json'), encoding='utf-8')) if p['id'][3:].rsplit('-t', 1)[0] in NEW]
json.dump(pos, open(os.path.join(out, 'positions_all.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
rep = json.load(open(os.path.join(tmp, 'report_convert.json'), encoding='utf-8'))
new = {'positions': len(pos),
       'left_out': [s for s in rep['left_out'] if str(s.get('game')).replace('_iOS', '')[2:] in NEW or str(s.get('game')) in NEW],
       'plans_with_unresolved_targets': [s for s in rep['plans_with_unresolved_targets'] if str(s.get('game')).replace('_iOS', '')[2:] in NEW or str(s.get('game')) in NEW],
       'decks': {g: d for g, d in rep['decks'].items() if g in NEW}}
json.dump(new, open(os.path.join(out, 'report_convert.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

meta = {}
for batch, d in sorted((b, d) for b in BATCHES for d in glob.glob(os.path.join(qa, b, '2026*'))):
    name = os.path.basename(d)
    short = 'kw-' + name.replace('_iOS', '')[2:]
    try:
        pg = json.load(open(d + '/PAUSE_GAME.json', encoding='utf-8'))
    except Exception:
        pg = {}
    oc = pg.get('outcome') or {}
    oc = oc if isinstance(oc, dict) else {'result': str(oc)}
    res = oc.get('result') or pg.get('result')
    meth = oc.get('method') or oc.get('reason') or pg.get('result_method')
    opp = oc.get('opponent') if isinstance(oc.get('opponent'), str) else (pg.get('opponent') if isinstance(pg.get('opponent'), str) else None)
    deck = pg.get('deck_name') or 'deck not named in the packet'
    meta[short] = {'title': f"{deck}; {res or 'result not recorded'}{(' (' + meth + ')') if meth else ''}; opponent {opp}", 'folder': batch + '/' + name,
                   'has_ledger': os.path.exists(d + '/TURN_LEDGER.json')}
json.dump(meta, open(os.path.join(out, 'games_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(pos), 'positions in', len(meta), 'games')
