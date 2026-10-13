#!/usr/bin/env python3
"""normalize_ledger.py SRC_GAMEDIR DST_GAMEDIR: copy a game's DECK_USED.json (with the log list's printings under the key the converter reads) and a TURN_LEDGER.json whose plays are written the way the converter reads them.

The ledger of 20261013_020824000 (and a few plays of the others) has no `target` and no `result` on a play: the target is inside a free-text `details` ("Evolve right Alolan Grimer
into Alolan Muk; ...", "Attach Heavy Helmet to Pawniard, not Glimmora") and the Energy's destination is in `energy.destination`. The converter of
../../pause_games_new_2026-10-12/harness reads `target` and `result`, so, without this, it cuts such a turn's plan at the first step it cannot place (turns 3 to 13 of that
game came out with empty or short plans). This copies the ledger with `result` := details and `target` := the part of `details` (or the Energy's destination) that names the
Pokemon the play is on. Only a play with no `target` and some `details` is touched (its `result`, if any, is kept and the details are added after it); the harness itself is not edited."""
import json, os, re, shutil, sys

src, dst = sys.argv[1:3]
os.makedirs(dst, exist_ok=True)
# DECK_USED.json of 20261013_015011000 writes the log list's printings as `variant_as_shown_in_log` (the converter's deckspec reads `variant`): without this its Regigigas and
# Alolan Grimer would stay "name only" (and the Regigigas would be the A2 143 card, not the B3 134 card every other game of this deck has)
deck = json.load(open(os.path.join(src, 'DECK_USED.json'), encoding='utf-8'))
for k, v in list(deck.items()):
    if isinstance(v, list):
        for x in v:
            if isinstance(x, dict) and x.get('variant') is None and x.get('variant_as_shown_in_log'):
                x['variant'] = x['variant_as_shown_in_log']
json.dump(deck, open(os.path.join(dst, 'DECK_USED.json'), 'w', encoding='utf-8'), ensure_ascii=False)
led = json.load(open(os.path.join(src, 'TURN_LEDGER.json'), encoding='utf-8'))


def kind(p):
    return str(p.get('kind') or '').strip().lower().replace(' ', '_')


def target_of(p):
    d = str(p.get('details') or '')
    e = p.get('energy') if isinstance(p.get('energy'), dict) else {}
    k = kind(p)
    if k in ('energy_attachment', 'energy', 'attach_energy'):
        return e.get('destination')
    if k == 'retreat':
        return e.get('destination')                   # the Pokemon that becomes Active
    if k in ('evolution', 'evolve'):
        m = re.search(r'evolve\s+(.+?)\s+(?:into|to)\s', d, re.I)
        return m.group(1) if m else None
    if k in ('tool_attachment', 'tool', 'attach_tool'):
        m = re.search(r'attach\s+.+?\s+to\s+(.+?)(?:\s+not\s|[,;.]|$)', d, re.I)
        return m.group(1) if m else None
    if k in ('card_play', 'bench', 'bench_basic', 'item', 'supporter', 'item_evolution'):
        return d          # a Pokemon benched ("Bench Pawniard in center slot"): the whole text is the best evidence for the slot
    return None


changed = 0
for t in led['turns']:
    for p in t.get('plays_in_order') or []:
        if p.get('target') is None and p.get('details'):
            p['target'] = target_of(p)
            if p.get('result') is None:
                p['result'] = p['details']
            else:
                p['result'] = str(p['result']) + '; ' + str(p['details'])      # the result and the free text both stay readable
            e = p.get('energy')
            if isinstance(e, dict) and e.get('count') is None and e.get('number') is not None:
                e['count'] = e['number']
            changed += 1
json.dump(led, open(os.path.join(dst, 'TURN_LEDGER.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(os.path.basename(src), 'plays normalised:', changed)
