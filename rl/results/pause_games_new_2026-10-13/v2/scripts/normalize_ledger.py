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
deck = json.load(open(os.path.join(src, 'DECK_USED.json'), encoding='utf-8'))


def deck_from_packet(src, deck):
    """A packet whose DECK_USED.json holds no 20-card list (20261012_010706000, 20261012_203719000, 20261013_030351000) still has the filmed QR (QR_DECODE.json: the 15 or 13 semantic
    cards with their counts and the printings that carry them) and the dated live log snapshot (DECK_LOG_SNAPSHOT.json: the exact printings). The list is built from those two;
    they must agree (same cards, same counts, every snapshot printing among the QR entity's printings, same Energy) or the game keeps the status `conflict` (unverified).
    -> (deck, [lines of the check])"""
    qr = json.load(open(os.path.join(src, 'QR_DECODE.json'), encoding='utf-8'))
    snap = json.load(open(os.path.join(src, 'DECK_LOG_SNAPSHOT.json'), encoding='utf-8'))
    qr_cards = [{'name': c['name'], 'entity_kind': c['entity_kind'], 'entity_id': c['entity_id'], 'count': c['count'], 'printing_aliases': c.get('printing_aliases') or []} for c in qr['cards']]
    if isinstance(snap.get('cards_in_log_order'), list) and len(snap['cards_in_log_order']) == 20:
        log = [{'name': x['name'], 'variant': x['variant']} for x in snap['cards_in_log_order']]
    else:                                   # 030351: rows {n, name, kind, id}
        log = [{'name': x['name'], 'variant': x['id']} for x in snap['cards'] for _ in range(int(x['n']))]
    lines, ok = [], True
    qn = {}
    for c in qr_cards:
        qn[c['name']] = qn.get(c['name'], 0) + c['count']
    ln = {}
    for x in log:
        ln[x['name']] = ln.get(x['name'], 0) + 1
    if sum(qn.values()) != 20 or len(log) != 20:
        ok = False
        lines.append(f'  the QR holds {sum(qn.values())} cards, the snapshot {len(log)}')
    if qn != ln:
        ok = False
        lines.append(f'  the cards differ: only in the QR {sorted(set(qn.items()) - set(ln.items()))}, only in the snapshot {sorted(set(ln.items()) - set(qn.items()))}')
    alias = {c['name']: set(c['printing_aliases']) for c in qr_cards}
    for x in log:
        if alias.get(x['name']) and x['variant'] not in alias[x['name']]:
            ok = False
            lines.append(f"  snapshot printing {x['name']} {x['variant']} is not among the QR entity's printings {sorted(alias[x['name']])}")
    qe = sorted(e['name'] for e in qr['decoded']['energy'])
    se = sorted(re.split(r'\s*\+\s*|\s*,\s*', str(snap.get('energy') or '')))
    if qe != se:
        ok = False
        lines.append(f'  Energy: QR {qe}, snapshot {se}')
    counts = {}
    for x in log:
        counts[(x['name'], x['variant'])] = counts.get((x['name'], x['variant']), 0) + 1
    out = dict(deck)
    out.update({'filmed_qr_cards': qr_cards, 'cards_in_log_order': log, 'counts_by_name_and_variant': [{'name': n, 'variant': v, 'count': k} for (n, v), k in counts.items()],
                'filmed_energy': qe, 'energy_configuration_from_log': ' + '.join(se), 'game_id': os.path.basename(src.rstrip('/')),
                'exact_list_status': 'verified_filmed_QR_and_live_log_snapshot_agree' if ok else 'filmed_QR_and_log_snapshot_conflict'})
    return out, [('AGREE' if ok else 'DISAGREE') + f' {os.path.basename(src.rstrip("/"))}: QR {sum(qn.values())} cards, snapshot {len(log)} cards, retrieved {snap.get("retrieved_utc")}'] + lines


if not any(isinstance(v, list) and len(v) == 20 for v in deck.values()) and os.path.exists(os.path.join(src, 'QR_DECODE.json')):
    deck, report = deck_from_packet(src, deck)
    print('\n'.join(report))
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
evolved_by_turn = {}      # turn number -> instance ids of Pokemon that evolved in that row ("Dratini-1 → Dragonair-1": Dratini-1)
for t in led['turns']:
    alias = {}        # an instance id made this turn by an evolution ('Dragonair-1') -> the id the Pokemon had at the start of the turn ('Dratini-1')
    for p in t.get('plays_in_order') or []:
        tg = p.get('target')
        m = ARROW.match(tg) if isinstance(tg, str) and kind(p) not in ('retreat', 'promotion') else None      # (a retreat's arrow is "retreats → becomes Active", the converter reads it as it is)
        if m:
            # "Dratini-1 → Dragonair-1" (game 20261013_030351000 names its Pokemon by instance): the evolved one is the old one for the rest of the turn
            alias[m.group(2) + '-' + m.group(3)] = m.group(1)
            evolved_by_turn.setdefault(t.get('turn_number'), set()).add(m.group(1))
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

# ---- a Pokemon knocked out by the checkup AFTER he ended his turn (game 20261013_030351000: Bad Dreams knocked out his Dragonair, then his Druddigon): the ledger logs the KO and his
# promotion at the end of his own row and its `board_after` is already the board AFTER the knock-out, so the converter (which finds knock-outs between two of his turns by
# comparing the end of one with the start of the next) never sees it: the Pokemon, what is under it, its Tool and its Energy were missing from his discard, and
# `me.knockouts` stayed 0. Here the Pokemon that was on his board at the start of such a row and is gone at its end (by instance id, an evolution this turn is not a knock-out)
# is put back at the end of the row's `board_after`, with the Energy the row's automatic event says left the board.
NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
POST = ('promotion', 'replacement', 'forced_replacement', 'forced_promotion', 'mandatory_promotion_choice', 'replacement_choice', 'replacement_selection')


def inst(side):
    out = []
    for p in [(side or {}).get('active')] + list((side or {}).get('bench_in_position_order') or []):
        if isinstance(p, dict) and p.get('name') and str(p['name']).strip().lower() not in ('none', 'empty', 'null') and not p.get('empty'):
            out.append(p)
    return out


def ids_of(p):
    return {x for x in (p.get('instance_id'), p.get('physical_instance')) if x}


restored = 0
for t in led['turns']:
    if not str(t.get('who_played', '')).startswith('owner'):
        continue
    plays = t.get('plays_in_order') or []
    ends = [i for i, p in enumerate(plays) if kind(p) in ('end_turn', 'end_turn_request')]
    if not ends or not any(kind(p) in POST for p in plays[ends[-1] + 1:]):
        continue
    pre, post = inst((t.get('board_at_start') or {}).get('owner')), inst((t.get('board_after') or {}).get('owner'))
    post_ids = set().union(*[ids_of(p) for p in post]) if post else set()
    evolved = evolved_by_turn.get(t.get('turn_number'), set())
    for p in pre:
        ids = ids_of(p)
        if not ids or ids & post_ids or ids & evolved:
            continue
        ko = json.loads(json.dumps(p))
        ko['hp_now'] = 0
        for ev in t.get('automatic_events_in_order') or []:
            txt = str(ev.get('event') or ev.get('description') or '') if isinstance(ev, dict) else str(ev)
            m = re.search(r'leave board', txt, re.I)
            mm = re.search(r'(\d|one|two|three|four)\s+([A-Z][a-z]+)\s+Energy', txt) if m else None
            if mm and mm.group(1) and (str(p['name']) in txt):
                n = int(mm.group(1)) if mm.group(1).isdigit() else NUMW[mm.group(1)]
                ko['attached_energy'] = {'total': n, 'by_type': {mm.group(2): n}}
        t.setdefault('board_after', {}).setdefault('owner', {}).setdefault('bench_in_position_order', []).append(ko)
        restored += 1
        print('   put back: turn', t.get('turn_number'), p.get('name'), sorted(ids), '| energy', (ko.get('attached_energy') or {}).get('by_type'))
print(os.path.basename(src.rstrip('/')), 'knock-outs after the end of his turn put back:', restored)
json.dump(led, open(os.path.join(dst, 'TURN_LEDGER.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(os.path.basename(src), 'plays normalised:', changed)
