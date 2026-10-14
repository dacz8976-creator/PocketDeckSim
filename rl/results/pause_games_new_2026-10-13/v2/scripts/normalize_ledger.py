#!/usr/bin/env python3
"""normalize_ledger.py SRC_GAMEDIR DST_GAMEDIR: copy a game's DECK_USED.json (with the log list's printings under the key the converter reads) and a TURN_LEDGER.json whose plays are written the way the converter reads them.

The ledger of 20261013_020824000 (and a few plays of the others) has no `target` and no `result` on a play: the target is inside a free-text `details` ("Evolve right Alolan Grimer
into Alolan Muk; ...", "Attach Heavy Helmet to Pawniard, not Glimmora") and the Energy's destination is in `energy.destination`. The converter of
../../pause_games_new_2026-10-12/harness reads `target` and `result`, so, without this, it cuts such a turn's plan at the first step it cannot place (turns 3 to 13 of that
game came out with empty or short plans). This copies the ledger with `result` := details and `target` := the part of `details` (or the Energy's destination) that names the
Pokemon the play is on. Only a play with no `target` and some `details` is touched (its `result`, if any, is kept and the details are added after it); the harness itself is not edited.

v3 (Oct 14, the laptop's review of the 92 positions, REVIEW_POSITIONS_laptop.md): (1) a Bench entry nested as {position, pokemon} (game 20261013_015011000) is read; (2) a packet whose
DECK_USED.json holds a 20-card list that leaves an entry's printing open (20261013_022530000: a list of names and 'semantic entity N' strings) still gets the QR-plus-snapshot list
when it has both files; (3) the corrections the review settled from the frames (ledger_corrections.json: each with its evidence) are applied to the copy of the ledger and recorded in it
as `corrections`, which the converter puts in the notes of the positions they cover. The source ledger is never edited."""
import json, os, re, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'pause_games_new_2026-10-12', 'harness'))
import deckspec as D  # noqa: E402

CORRECTIONS_FILE = os.path.join(HERE, 'ledger_corrections.json')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def dump(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False)


def deck_from_packet(src, deck):
    """A packet whose DECK_USED.json holds no 20-card list (20261012_010706000, 20261012_203719000, 20261013_030351000) still has the filmed QR (QR_DECODE.json: the 15 or 13 semantic
    cards with their counts and the printings that carry them) and the dated live log snapshot (DECK_LOG_SNAPSHOT.json: the exact printings). The list is built from those two;
    they must agree (same cards, same counts, every snapshot printing among the QR entity's printings, same Energy) or the game keeps the status `conflict` (unverified).
    -> (deck, [lines of the check])"""
    qr = load(os.path.join(src, 'QR_DECODE.json'))
    snap = load(os.path.join(src, 'DECK_LOG_SNAPSHOT.json'))
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


def needs_packet_list(src, deck):
    """should the list be built from the packet's QR and snapshot? When the file holds no 20-card list deckspec can read, or one that leaves the printing of an entry open (a name-only entry
    that stands for several functions: 20261013_022530000 lists 20 names and 'semantic entity N' strings, and its Dratini was settled on an HP tie), and the packet has both files"""
    if not (os.path.exists(os.path.join(src, 'QR_DECODE.json')) and os.path.exists(os.path.join(src, 'DECK_LOG_SNAPSHOT.json'))):
        return False
    spec = D.read_deck(deck, {})
    return spec is None or any(e.ambiguous for e in spec.entries)


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
NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4}
POST = ('promotion', 'replacement', 'forced_replacement', 'forced_promotion', 'mandatory_promotion_choice', 'replacement_choice', 'replacement_selection')


def inst(side):
    """the Pokemon on one side's board: the Active and the Bench entries (a Bench entry may be nested as {position, pokemon: {...} or null}, game 20261013_015011000)"""
    out = []
    for p in [(side or {}).get('active')] + list((side or {}).get('bench_in_position_order') or []):
        if isinstance(p, dict) and 'pokemon' in p and not p.get('name'):
            p = p['pokemon']
        if isinstance(p, dict) and p.get('name') and str(p['name']).strip().lower() not in ('none', 'empty', 'null') and not p.get('empty'):
            out.append(p)
    return out


def ids_of(p):
    return {x for x in (p.get('instance_id'), p.get('physical_instance')) if x}


def normalize_plays(led):
    """give every play without a `target` the one its free text names, resolve the instance-id arrows ('Dratini-1 → Dragonair-1'); -> (changed, {turn number: ids of the Pokemon that evolved in that row})"""
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
    return changed, evolved_by_turn


def restore_checkup_knockouts(led, evolved_by_turn, log):
    """A Pokemon knocked out by the checkup AFTER he ended his turn (game 20261013_030351000: Bad Dreams knocked out his Dragonair, then his Druddigon): the ledger logs the KO and his
    promotion at the end of his own row and its `board_after` is already the board AFTER the knock-out, so the converter (which finds knock-outs between two of his turns by
    comparing the end of one with the start of the next) never sees it: the Pokemon, what is under it, its Tool and its Energy were missing from his discard, and
    `me.knockouts` stayed 0. Here the Pokemon that was on his board at the start of such a row and is gone at its end (by instance id, an evolution this turn is not a knock-out)
    is put back at the end of the row's `board_after`, with the Energy the row's automatic event says left the board. -> the number put back"""
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
            log.append('   put back: turn ' + str(t.get('turn_number')) + ' ' + str(p.get('name')) + ' ' + str(sorted(ids)) + ' | energy ' + str((ko.get('attached_energy') or {}).get('by_type')))
    return restored


# ---------------------------------------------------------------------------------------------------------------- corrections from the frames
def pokemon_slots(board_side):
    """every Pokemon dict of one side's board reading, the Bench entries unwrapped (the dicts themselves, so they can be edited)"""
    out = []
    for p in [(board_side or {}).get('active')] + list((board_side or {}).get('bench_in_position_order') or []):
        if isinstance(p, dict) and 'pokemon' in p and not p.get('name'):
            p = p['pokemon']
        if isinstance(p, dict) and p.get('name'):
            out.append(p)
    return out


def apply_corrections(led, ops, game=''):
    """apply the recorded corrections to a ledger (in place) and record them in `led['corrections']`. Each op is {id, op, note, evidence, ...}; one that changes nothing is an error, so a ledger
    that no longer looks like the one the correction was written for does not pass silently. -> the list of lines to print"""
    lines, rec = [], []
    for c in ops:
        n = 0
        op = c['op']
        if op == 'rename_pokemon':
            side = 'opponent' if c.get('side', 'opponent') == 'opponent' else 'owner'
            for t in led['turns']:
                for key in ('board_at_start', 'board_after'):
                    for p in pokemon_slots((t.get(key) or {}).get(side)):
                        if p.get('name') == c['name']:
                            p['name'] = c['to']
                            if c.get('variant') is not None:
                                p['variant'] = c['variant']
                            n += 1
                for p in t.get('plays_in_order') or []:
                    if p.get('card_name') == c['name'] and (t.get('who_played', '').startswith('opponent') == (side == 'opponent')):
                        p['card_name'] = c['to']
                        n += 1
        elif op == 'rename_tool':
            side = 'opponent' if c.get('side', 'opponent') == 'opponent' else 'owner'
            for t in led['turns']:
                if c.get('from_turn', 0) <= t['turn_number'] <= c.get('to_turn', 10 ** 6):
                    for key in ('board_at_start', 'board_after'):
                        for p in pokemon_slots((t.get(key) or {}).get(side)):
                            if p.get('tool') == c['name']:
                                p['tool'] = c['to']
                                n += 1
        elif op == 'set_opponent_hand':
            for t in led['turns']:
                v = c['counts'].get(str(t['turn_number']))
                if v is not None and str(t.get('who_played', '')).startswith('owner'):
                    old = t.get('opponent_hand_at_owner_turn_start') or {}
                    said = old.get('count') if old.get('count') is not None else old.get('supported_range')
                    if 'was' in c and c['was'].get(str(t['turn_number'])) != said:
                        raise SystemExit(f'correction {c["id"]}: the ledger says {said!r} for the opponent hand at turn {t["turn_number"]}, the correction was written for {c["was"].get(str(t["turn_number"]))!r}')
                    t['opponent_hand_at_owner_turn_start'] = {'count': v, 'supported_range': None, 'basis': 'frames (recorded correction ' + c['id'] + ')', 'ledger_said': said}
                    n += 1
        elif op == 'replace_play':
            for t in led['turns']:
                if t['turn_number'] == c['turn']:
                    for p in t.get('plays_in_order') or []:
                        if p.get('order') == c['order'] and all(p.get(k) == v for k, v in c.get('expect', {}).items()):
                            p['replaced_by_correction'] = {k: p.get(k) for k in c['set']}
                            p.update(c['set'])
                            n += 1
        else:
            raise SystemExit(f'correction {c.get("id")}: unknown op {op!r}')
        if not n:
            raise SystemExit(f'correction {c.get("id")} ({op}) changed nothing: the ledger is not the one it was written for')
        lines.append(f'{game} corrected from the frames: {c["id"]} ({op}, {n} change{"s" if n != 1 else ""})')
        rec.append({'id': c['id'], 'op': op, 'turns': c.get('turns'), 'note': c.get('note'), 'evidence': c.get('evidence')})
    if rec:
        led['corrections'] = rec
    return lines


def load_corrections(game_id, path=CORRECTIONS_FILE):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return json.load(f).get(game_id) or []


def normalize(src, dst, corrections=None):
    """write DST/DECK_USED.json and DST/TURN_LEDGER.json from the packet SRC; -> the lines the check prints (the deck check first). `corrections` defaults to ledger_corrections.json's entry for the packet"""
    src = src.rstrip('/')
    os.makedirs(dst, exist_ok=True)
    lines = []
    deck = load(os.path.join(src, 'DECK_USED.json'))
    if needs_packet_list(src, deck) or (not any(isinstance(v, list) and len(v) == 20 for v in deck.values()) and os.path.exists(os.path.join(src, 'QR_DECODE.json'))):
        deck, report = deck_from_packet(src, deck)
        lines += report
    for k, v in list(deck.items()):
        if isinstance(v, list):
            for x in v:
                if isinstance(x, dict) and x.get('variant') is None and x.get('variant_as_shown_in_log'):
                    x['variant'] = x['variant_as_shown_in_log']
    dump(deck, os.path.join(dst, 'DECK_USED.json'))
    led = load(os.path.join(src, 'TURN_LEDGER.json'))
    changed, evolved_by_turn = normalize_plays(led)
    restored = restore_checkup_knockouts(led, evolved_by_turn, lines)
    lines.append(f'{os.path.basename(src)} knock-outs after the end of his turn put back: {restored}')
    ops = load_corrections(os.path.basename(src)) if corrections is None else corrections
    lines += apply_corrections(led, ops, os.path.basename(src))
    dump(led, os.path.join(dst, 'TURN_LEDGER.json'))
    lines.append(f'{os.path.basename(src)} plays normalised: {changed}')
    return lines


if __name__ == '__main__':
    for line in normalize(*sys.argv[1:3]):
        print(line)
