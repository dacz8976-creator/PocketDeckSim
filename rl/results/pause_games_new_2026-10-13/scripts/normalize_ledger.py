#!/usr/bin/env python3
"""normalize_ledger.py SRC_GAMEDIR DST_GAMEDIR: copy a game's DECK_USED.json (with the log list's printings under the key the converter reads) and a TURN_LEDGER.json whose plays are written the way the converter reads them.

The ledger of 20261013_020824000 (and a few plays of the others) has no `target` and no `result` on a play: the target is inside a free-text `details` ("Evolve right Alolan Grimer
into Alolan Muk; ...", "Attach Heavy Helmet to Pawniard, not Glimmora") and the Energy's destination is in `energy.destination`. The converter of
../../pause_games_new_2026-10-12/harness reads `target` and `result`, so, without this, it cuts such a turn's plan at the first step it cannot place (turns 3 to 13 of that
game came out with empty or short plans). This copies the ledger with `result` := details and `target` := the part of `details` (or the Energy's destination) that names the
Pokemon the play is on. Only a play with no `target` and some `details` is touched (its `result`, if any, is kept and the details are added after it); the harness itself is not edited."""
import json, os, re, shutil, sys

src, dst = sys.argv[1:3]
donor = sys.argv[3] if len(sys.argv) > 3 else None       # a game folder whose DECK_USED.json is used when this packet has no 20-card list
os.makedirs(dst, exist_ok=True)
# DECK_USED.json of 20261013_015011000 writes the log list's printings as `variant_as_shown_in_log` (the converter's deckspec reads `variant`): without this its Regigigas and
# Alolan Grimer would stay "name only" (and the Regigigas would be the A2 143 card, not the B3 134 card every other game of this deck has)
deck = json.load(open(os.path.join(src, 'DECK_USED.json'), encoding='utf-8'))
if donor and not any(isinstance(v, list) and len(v) == 20 for v in deck.values()):
    # no 20-card list in the packet (20261012_010706000, 20261012_203719000, 20261013_030351000): the list of a game of the SAME named deck stands in, marked unverified
    # (the converter then marks every position of the game `usable: false`); check_deck_assumption.py compares it with every card the ledger shows
    deck = json.load(open(os.path.join(donor, 'DECK_USED.json'), encoding='utf-8'))
    deck['exact_list_status'] = 'assumed_from_' + os.path.basename(donor.rstrip('/')) + '_deck_list_not_in_this_packet_unverified'
    deck['game_id'] = os.path.basename(src.rstrip('/'))
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
    """what the converter reads as `target`, from the free text the packet gives instead (`details`, or `result` when it is the only text)"""
    d = str(p.get('details') or p.get('result') or '')
    e = p.get('energy') if isinstance(p.get('energy'), dict) else {}
    k = kind(p)
    if k in ('energy_attachment', 'energy', 'attach_energy'):
        return e.get('destination') or None
    if k == 'retreat':
        return e.get('destination') or d                   # the Pokemon that becomes Active, or the text ("promotes Regigigas")
    if k in ('evolution', 'evolve'):
        m = re.search(r'evolves?\s+(.+?)\s+(?:into|to|using)\s', d, re.I)
        return m.group(1) if m else d
    if k in ('tool_attachment', 'tool', 'attach_tool'):
        m = re.search(r'attach(?:es)?\s+.+?\s+to\s+(.+?)(?:\s+not\s|[,;.]|$)', d, re.I)
        return m.group(1) if m else d
    if k in ('card_play', 'bench', 'bench_basic', 'item', 'supporter', 'item_evolution'):
        return d          # a Pokemon benched ("Bench Pawniard in center slot"): the whole text is the best evidence for the slot
    return None


def nname_is_rare_candy(p):
    return 'rare candy' in str(p.get('card_name') or '').lower()


ARROW = re.compile(r'^\s*(.+?-\d+)\s*(?:→|->)\s*(.+?)-(\d+)\s*$')
changed = 0
for t in led['turns']:
    alias = {}        # an instance id made this turn by an evolution ('Dragonair-1') -> the id the Pokemon had at the start of the turn ('Dratini-1')
    for p in t.get('plays_in_order') or []:
        tg = p.get('target')
        m = ARROW.match(tg) if isinstance(tg, str) and kind(p) not in ('retreat', 'promotion') else None      # (a retreat's arrow is "retreats → becomes Active", the converter reads it as it is)
        if m:
            # "Dratini-1 → Dragonair-1" (game 20261013_030351000 names its Pokemon by instance): the evolved one is the old one for the rest of the turn
            alias[m.group(2) + '-' + m.group(3)] = m.group(1)
            p['target'] = m.group(1) if kind(p) in ('evolution', 'evolve', 'card_play') and nname_is_rare_candy(p) is False else m.group(1) + ' -> ' + m.group(2)
            changed += 1
        elif isinstance(tg, str) and tg.strip() in alias:
            p['target'] = alias[tg.strip()]
            changed += 1
        if p.get('target') is None and (p.get('details') or p.get('result')):
            p['target'] = target_of(p)
            if p.get('details'):
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
