#!/usr/bin/env python3
"""Codex TURN_LEDGER.json (pause-games/turn-capture-v1) + DECK_USED.json -> constructed-board positions at the start of every owner turn
(harness schema, as blast_to_positions.py of the Oct 2 set), generic over the game.

Cards are kept by FUNCTION, never by name alone (cardlib.py): two cards that share a name stay two cards. His deck comes from the game's DECK_USED.json
(deckspec.py: the filmed QR list, with the printings the files and the other games give for each entity); the printing of each card on his board is settled by
the attacks, Abilities and HP the ledger shows for it, and the cards in his hand and discard by what is left of the deck. The opponent's list is unknown, so a
position carries no "filler" key (his hidden cards are cycled from the pilot's own list); the opponent's board cards are chosen by name, printed HP and the
attack/Ability titles the ledger shows, and a card that cannot be told from the ledger is listed in the position's `opp_ambiguous`.
A turn is LEFT OUT (and counted, with the reason) when its hand is not fully named, a card cannot be mapped, or points are missing. A position of a game whose
deck version is not verified (DECK_USED says the list is a different version from the game's) is marked `usable: false`.
A Pokemon of his that the CHECKUP knocked out after his turn ended (Poison, Burn, Bad Dreams on a sleeping one) is read from its own row: the ledger's `board_after` of that row is
already past the knock-out, so checkup_knockouts() finds it from the promotion that follows the turn's last end_turn / attack and the row's text, and it reaches his discard (with what
was under it, its Tool and its Energy) and `me.knockouts` like one the opponent's attack made.
usage: ledger_to_positions.py OUT.json REPORT.json GAMEDIR [GAMEDIR ...]   (GAMEDIR = a Recording_QA game folder; DECK_USED.json of every game is read first)"""
import collections, itertools, json, os, re, sys

import cardlib as C
import deckspec as D

nname, etype, ETYPES = C.nname, C.etype, C.ETYPES


def ebt(p):
    """[(energy type, count)] of a Pokemon's attached Energy, from either by_type shape; unreadable types are dropped"""
    v = (p.get('attached_energy') or {}).get('by_type')
    out = collections.Counter()
    if isinstance(v, dict):
        for t, n in v.items():
            if etype(t):
                out[etype(t)] += int(n or 0)
        return list(out.items())
    for x in v or []:
        if isinstance(x, dict):
            t = etype(x.get('type') or x.get('energy_type'))
            if t:
                out[t] += int(x.get('count') or 1)
        elif isinstance(x, str) and etype(x):
            out[etype(x)] += 1
    return list(out.items())


WORDPOS = {'left': 1, 'leftmost': 1, 'center': 2, 'centre': 2, 'middle': 2, 'right': 3, 'rightmost': 3}


def bpos(p):
    """a ledger bench slot ('left'/'center'/'right', '2', 2, 'Bench2') as 1..3, or None"""
    v = p.get('bench_position')
    if isinstance(v, int):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in WORDPOS:
        return WORDPOS[s]
    m = re.search(r'(\d)', s)
    if m:
        return int(m.group(1))
    return next((n for w, n in WORDPOS.items() if w in s), None)


def nk(kind):
    """the ledgers spell a play's kind many ways: one set of names. An attempt that was not carried out ('card_play_attempt') is its own kind."""
    k = str(kind or '').strip().lower().replace(' ', '_')
    if k in ('card_play', 'item', 'supporter', 'trainer'):
        return 'card_play'
    if k == 'card_play_attempt':
        return 'attempt'
    if k in ('energy_attachment', 'energy', 'attach_energy'):
        return 'energy_attachment'
    if k in ('bench', 'bench_basic', 'bench_pokemon'):
        return 'bench'
    if k in ('evolution', 'evolve'):
        return 'evolution'
    if k in ('tool', 'tool_attachment'):
        return 'tool'
    if k in ('stadium', 'item_evolution', 'retreat', 'attack', 'prompt_response'):
        return k
    if k in ('ability', 'stadium_ability', 'stadium_effect', 'stadium_activation'):
        return 'ability'
    if k in ('end_turn', 'end_turn_request'):
        return 'end'
    return 'other'


NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4}

# a Poké Ball (or other search) that found nothing: the ledgers write 'no effect', 'no target', 'no-target', 'No eligible Basic remains', 'No Basic found'
NOTHING_FOUND = re.compile(r'no[\s-]*effect|no[\s-]*target|no eligible|nothing|no card|no\s+basic', re.I)


def pop_returned(result):
    """did a Lucky Ice Pop come back to his hand? Heads brings it back, tails discards it, however the ledger glues the word ('Heads213 returns Pop', 'coinHeads', 'heads at158');
    when it names neither coin (or both), 'return' without 'discard' decides"""
    t = str(result or '').lower()
    heads, tails = 'heads' in t, 'tails' in t
    if heads != tails:
        return heads
    return 'return' in t and 'discard' not in t


def is_stadium_card(name):
    return any('Stadium' in str(c.get('trainer_card_type', '')) for c in C.BYNAME.get(nname(name), []))


def zone_now(trow):
    """the type of the Energy in his zone for one of his turns: the zone's this-turn circle; else the type he attached from it; else the circle the ledger shows as 'next'
    (at a turn start whose own circle has not loaded, 'next' is this turn's Energy: in all 124 turns with a circle it matched what he attached, and in 46 of the 51 without)"""
    z = ((trow.get('board_at_start') or {}).get('owner') or {}).get('energy_zone') or {}
    att = next((etype(p['energy'].get('type')) for p in trow.get('plays_in_order') or []
                if nk(p.get('kind')) == 'energy_attachment' and isinstance(p.get('energy'), dict) and etype(p['energy'].get('type'))), None)
    return etype((z.get('this_turn') or {}).get('type')) or att or etype((z.get('next') or {}).get('type'))


def opp_zone_types(turns):
    """every Energy type the opponent's zone shows anywhere in the game (its circles on any row, the Energy he attached from it)"""
    out = set()
    for r in turns:
        for key in ('board_at_start', 'board_after'):
            z = (((r.get(key) or {}).get('opponent') or {}).get('energy_zone')) or {}
            out |= {etype((z.get(c) or {}).get('type')) for c in ('this_turn', 'next')}
        if not str(r.get('who_played', '')).startswith('owner'):
            out |= {etype(p['energy'].get('type')) for p in r.get('plays_in_order') or [] if nk(p.get('kind')) == 'energy_attachment' and isinstance(p.get('energy'), dict)}
    out.discard(None)
    return out


def opp_energy_next(turns, ti):
    """the type of the Energy the opponent's zone gives him on his next turn, for the position at the row turns[ti] of his: the zone's `next` circle (or this-turn circle) at the turn start, else
    the `next` circle on the same row after his turn, else what his next row shows (its this-turn circle, or the type he attached from the zone), else (the last turn: no later row) the only type
    his zone ever shows in the game. None when the ledger shows none: at his turn start the opponent's zone is often hidden (010706: all 11 positions, 010003: all 6, 203719 t17), and his
    deck's Energy is not his zone's"""
    t = turns[ti]
    z0 = ((t.get('board_at_start') or {}).get('opponent') or {}).get('energy_zone') or {}
    z1 = ((t.get('board_after') or {}).get('opponent') or {}).get('energy_zone') or {}
    got = etype((z0.get('next') or {}).get('type')) or etype((z0.get('this_turn') or {}).get('type')) or etype((z1.get('next') or {}).get('type'))
    if got:
        return got
    for r in turns[ti + 1:]:
        if not str(r.get('who_played', '')).startswith('owner'):
            zr = ((r.get('board_at_start') or {}).get('opponent') or {}).get('energy_zone') or {}
            att = next((etype(p['energy'].get('type')) for p in r.get('plays_in_order') or []
                        if nk(p.get('kind')) == 'energy_attachment' and isinstance(p.get('energy'), dict) and etype(p['energy'].get('type'))), None)
            got = etype((zr.get('this_turn') or {}).get('type')) or att
            if got:
                return got
            break
    seen = opp_zone_types(turns)
    return next(iter(seen)) if len(seen) == 1 else None


def hp_in(text):
    """the printed HP a ledger text names ('..., HP140', '60 HP'), or None"""
    m = re.search(r'\bHP\s*(\d+)|(\d+)\s*HP\b', str(text or ''))
    return int(m.group(1) or m.group(2)) if m else None


def retreat_pay(p):
    """[(type, n)] the ledger says was paid for a retreat"""
    e = p.get('energy')
    if isinstance(e, dict) and isinstance(e.get('retreat_payment_by_type'), dict):
        return [(etype(t), int(n)) for t, n in e['retreat_payment_by_type'].items() if etype(t) and n]
    out = []
    for m in re.finditer(r'pay\w*\s*(\d+|one|two|three|four)\s*([A-Za-z]+)', str(p.get('result') or ''), re.I):
        n = NUMW.get(m.group(1).lower()) or int(m.group(1))
        if etype(m.group(2)):
            out.append((etype(m.group(2)), n))
    return out


def _real(p):
    return bool(p) and isinstance(p, dict) and bool(p.get('name')) and not p.get('empty') and str(p['name']).strip().lower() not in ('none', 'empty', 'null', 'n/a')


def bench_entry(x):
    """a Bench entry as the ledger writes it: the Pokemon itself, or (game 20261013_015011000) {position, pokemon: {...} or null}; the Pokemon then takes the entry's position when it has none"""
    if isinstance(x, dict) and 'pokemon' in x and not x.get('name'):
        inner = x['pokemon']
        if isinstance(inner, dict) and inner.get('bench_position') is None and x.get('position') is not None:
            inner = dict(inner, bench_position=x['position'])
        return inner
    return x


def instances(side):
    out = []
    act = side.get('active')
    if _real(act):
        out.append(act)
    bench = [p for p in (bench_entry(x) for x in (side.get('bench_in_position_order') or [])) if _real(p)]
    bench.sort(key=lambda p: (bpos(p) if bpos(p) is not None else 99))
    return out + bench


def stadium_name(board_):
    """the Stadium in play at one board reading ('Starting Plains'), or None"""
    st = (board_ or {}).get('stadium')
    if isinstance(st, dict):
        st = st.get('name') or st.get('card')
    return nname(st) if st and str(st).strip().lower() not in ('none', 'null', 'empty', 'no stadium') else None


def shown_hp(p, stadium):
    """the HP the ledger shows for one Pokemon with the Tool on it and the Stadium in play, to be compared with printed HP (cardlib.HP); None when it shows none"""
    return C.HP(p.get('hp_max'), tool_of(p), stadium) if p.get('hp_max') is not None else None


def stack_under(p):
    es = p.get('evolution_stack')
    if isinstance(es, dict) and es.get('cards_bottom_to_top'):
        names = [nname(x if isinstance(x, str) else x.get('name')) for x in es['cards_bottom_to_top']]
        return names[:-1] if names and names[-1] == nname(p.get('name')) else names
    for k in ('evolution_stack_under_top', 'evolution_stack_bottom_to_top'):
        v = p.get(k)
        if isinstance(v, list):
            names = [nname(x.get('name') if isinstance(x, dict) else x) for x in v]
            return names[:-1] if names and names[-1] == nname(p.get('name')) else names
    return None


def chain_names(name):
    """names below a Pokemon by the printed evolution line (no Rare Candy assumed), for any printing of the name"""
    cs = [c for c in C.BYNAME.get(name, []) if C.is_pokemon(c)]
    return C.chain_down(cs[0]['id']) if cs else []


def pids(p):
    """the instance ids a ledger gives a Pokemon ('A', 'W1'; instance_id / physical_instance)"""
    return {x for x in (p.get('instance_id'), p.get('physical_instance')) if x}


def tool_of(p):
    """the Tool name on a Pokemon; None when there is none (or the ledger says nothing)"""
    t = p.get('tool')
    return None if t is None or str(t).strip().lower() in ('none', 'null', '') else nname(t)


def pair_cost(a, n):
    """how unlike two readings of one Pokemon are (before and after the opponent's turn): the Energy on it, its Tool, then its bench slot"""
    ea, en = collections.Counter(dict(ebt(a))), collections.Counter(dict(ebt(n)))
    return sum(((ea - en) + (en - ea)).values()) + 0.5 * (tool_of(a) != tool_of(n)) + 0.05 * (bpos(a) != bpos(n))


def evolves_into(below, above):
    """is `above` an evolution of `below`, by the printed line? An Eevee ex counts as an Eevee (the ledger shows Eevee ex becoming Glaceon ex)"""
    line = chain_names(above)
    return below in line or (below.endswith(' ex') and below[:-3] in line)


def match_boards(after, now):
    """-> (pairs [(Pokemon after his turn, the same Pokemon at his next turn start)], knocked_out [the after-Pokemon with no counterpart]).
    The same Pokemon is told by its instance id when the ledger gives one; else by being its evolution; else, among Pokemon of one name, by what is on
    it (Energy, Tool, slot): never by which of them comes first"""
    ua, un, pairs = set(range(len(after))), set(range(len(now))), []

    def link(i, j):
        pairs.append((after[i], now[j]))
        ua.discard(i)
        un.discard(j)
    for i in sorted(ua):
        ids = pids(after[i])
        for j in sorted(un):
            if ids and ids & pids(now[j]):
                link(i, j)
                break
    for nm in sorted({nname(after[i]['name']) for i in ua}):
        ia = sorted(i for i in ua if nname(after[i]['name']) == nm)
        jn = sorted(j for j in un if nname(now[j]['name']) == nm)
        k = min(len(ia), len(jn))
        if k:
            best = min(((sum(pair_cost(after[i], now[j]) for i, j in zip(sub, perm)), sub, perm)
                        for sub in itertools.combinations(ia, k) for perm in itertools.permutations(jn, k)), key=lambda x: x[0])
            for i, j in zip(best[1], best[2]):
                link(i, j)
    # what is left: a Pokemon that is now its own evolution (a name that is gone because it evolved is not a knock-out)
    evo = sorted((pair_cost(after[i], now[j]), i, j) for i in ua for j in un if evolves_into(nname(after[i]['name']), nname(now[j]['name'])))
    for _, i, j in evo:
        if i in ua and j in un:
            link(i, j)
    return pairs, [after[i] for i in sorted(ua)]


# ---------------------------------------------------------------------------------------------------------------- knocked out after his turn ended

POST_KO_KIND = re.compile(r'promot|replac', re.I)            # a play of kind promotion / replacement / forced_replacement ...: he had to put a new Active in front
KO_WORDS = re.compile(r"knock\w*[\s-]*out|\bKO\b|\bKO'?d\b|leaves?\s+(?:the\s+)?board|(?:is|are)\s+discarded", re.I)
RETURNED = re.compile(r"return\w*\s+(?:\w+\s+){0,6}?(?:to|into)\s+(?:the\s+|his\s+|owner\s+)*(?:hand|deck)|back\s+to\s+(?:the\s+|his\s+|owner\s+)*hand|shuffl", re.I)
ENERGY_COUNT = re.compile(r'\b(\d+|one|two|three|four)\s+([A-Za-z]+)')


def _norm(s):
    return str(s or '').replace('’', "'").lower()


def _id_in(text, ids):
    """does a ledger target text name one of these instance ids as a word ('Dratini-2 → Dragonair-2' names Dratini-2 and Dragonair-2, not Dragonair-22)?"""
    return any(re.search(r'(?<![A-Za-z0-9\-])' + re.escape(i) + r'(?![A-Za-z0-9\-])', str(text or '')) for i in ids)


def _is_evolution_play(p):
    """an evolution: a Stage 1 or 2 played from the hand, or a Rare Candy / Quick-Grow Extract (not an Ability or an attack, whose card_name is the Pokemon using it)"""
    k, card = nk(p.get('kind')), nname(p.get('card_name'))
    if k in ('evolution', 'item_evolution'):
        return True
    return k == 'card_play' and (card in ('Rare Candy', 'Quick-Grow Extract') or any(C.is_pokemon(c) and c.get('stage', 0) >= 1 for c in C.BYNAME.get(card, [])))


def checkup_knockouts(row):
    """-> (the Pokemon of his that were knocked out AFTER his turn ended, each as it stood when the turn ended; notes) for one row of his.
    The checkup after his turn (Poison, Burn, Bad Dreams on a sleeping Pokemon) can knock out his Active. The ledgers log the knock-out and his promotion at the end of his own row, and
    that row's `board_after` is already past it, so the comparison of the end of one of his rows with the start of his next (which finds what the OPPONENT's turn knocked out) never sees it:
    the Pokemon, what is under it, its Tool and its Energy were missing from his discard and the knock-out from `me.knockouts`.
    A Pokemon is one of these when (1) a promotion/replacement play comes after the last play that ended his turn (an end_turn, or an attack), (2) it was on his board at the start of
    the row and is gone at its end (by instance id; without ids, by the number of its name), (3) it did not evolve in the row (an evolved Pokemon is a new instance), and (4) the row's
    automatic events or the promotion's text say it was knocked out / left the board / was discarded, and say nothing of it going back to his hand or deck (a bounce also ends in a
    promotion). Exactly one Pokemon must fit: with two, none is taken and a note says so. Its Energy is what it had at the start plus what the row attached to it, unless the ledger's text
    gives a count (then the text's); its Tool the one it had, or one the row attached"""
    plays = row.get('plays_in_order') or []
    ends = [i for i, p in enumerate(plays) if nk(p.get('kind')) in ('end', 'attack')]
    after_end = plays[ends[-1] + 1:] if ends else []
    if not any(POST_KO_KIND.search(str(p.get('kind') or '')) for p in after_end):
        return [], []
    pre = instances((row.get('board_at_start') or {}).get('owner') or {})
    post = instances((row.get('board_after') or {}).get('owner') or {})
    post_ids = set().union(*[pids(p) for p in post]) if post else set()
    texts = [str(ev.get('event') or ev.get('description') or '') if isinstance(ev, dict) else str(ev) for ev in row.get('automatic_events_in_order') or []]
    texts += [str(p.get(x) or '') for p in after_end if POST_KO_KIND.search(str(p.get('kind') or '')) for x in ('result', 'details')]
    texts = [t for t in texts if t]
    evo_targets = [str(p.get('target') or '') for p in plays if _is_evolution_play(p)]
    cands = []
    for i, p in enumerate(pre):
        ids, nm = pids(p), nname(p['name'])
        if ids:
            gone = not (ids & post_ids) and not any(_id_in(t, ids) for t in evo_targets)
        else:
            # no ids: the Active at the start, when fewer of its name are left and no evolution of its name was played
            gone = (i == 0 and sum(1 for q in pre if nname(q['name']) == nm) > sum(1 for q in post if nname(q['name']) == nm)
                    and not any(evolves_into(nm, nname(q.get('card_name'))) for q in plays if _is_evolution_play(q)))
        if not gone:
            continue
        said = [t for t in texts if _norm(nm) in _norm(t)]
        if any(KO_WORDS.search(t) for t in said) and not any(RETURNED.search(t) for t in said):
            cands.append((p, said))
    if len(cands) != 1:
        if len(cands) > 1:
            return [], [f'a Pokémon of his was knocked out after his turn ended, but the ledger does not tell which of {" / ".join(sorted(nname(c[0]["name"]) for c in cands))}: none is put in his discard']
        return [], []
    p, said = cands[0]
    ids = pids(p)
    by = collections.Counter(dict(ebt(p)))
    for q in plays:
        e = q.get('energy')
        if isinstance(e, dict) and etype(e.get('type')) and e.get('count') and ids and _id_in(e.get('destination') or q.get('target'), ids):
            by[etype(e['type'])] += int(e['count'])
    told = collections.Counter()
    nm_ = _norm(nname(p['name']))
    for t in said:
        # only the clause that says it was knocked out / left the board / was discarded and names it ("Druddigon, Rocky Helmet and 3 Metal are discarded."): the next one often
        # says what he promoted, with ITS Energy ("Owner promotes second Haxorus 150 HP with 1 Fighting.")
        for clause in re.split(r'(?<=[.;])\s+|;', t):
            if nm_ in _norm(clause) and KO_WORDS.search(clause):
                for m in ENERGY_COUNT.finditer(clause):
                    if etype(m.group(2)):
                        told[etype(m.group(2))] += int(m.group(1)) if m.group(1).isdigit() else NUMW[m.group(1).lower()]
    notes = []
    if told and sum(told.values()) != sum(by.values()):
        notes.append(f'the Energy of the knocked-out {nname(p["name"])} is the count in the ledger\'s text ({sum(told.values())}), not the one the plays add up to ({sum(by.values())})')
        by = told
    ko = json.loads(json.dumps(p))
    ko['hp_now'] = 0
    ko['attached_energy'] = {'total': sum(by.values()), 'by_type': dict(by)}
    for q in plays:
        card = nname(q.get('card_name'))
        if card and ids and any('Tool' in str(c.get('trainer_card_type', '')) for c in C.BYNAME.get(card, [])) and _id_in(q.get('target'), ids) and nk(q.get('kind')) != 'attempt':
            ko['tool'] = card
    return [ko], notes


def resolve(items, text):
    """index in the board list (the engine's slot) from a ledger target text ('owner Active', 'owner Bench 3', 'Seadra', 'Horsea Bench 1', 'Weezing ex Bench 3'); a slot Ilima emptied (None) is skipped"""
    if text is None:
        return None
    t = str(text).replace('’', "'")
    tl = t.lower()
    cand = [i for i, x in enumerate(items) if x is not None]
    # an instance id the ledger gives its Pokemon ('A', 'B', 'W1' ...): the whole target text, a short text containing it as a word, or a text that begins with it ('B on bench2')
    hits = [i for i in cand for tok in items[i].get('ids', ()) if t.strip() == tok or (len(t) <= 8 and re.search(r'(?<![A-Za-z0-9])' + re.escape(tok) + r'(?![A-Za-z0-9])', t))
            or re.match(re.escape(tok) + r'\s+(?:on|at|in)\b', t.strip())]
    if len(set(hits)) == 1:
        return hits[0]
    m = re.search(r'bench\s*(?:position\s*|slot\s*)?(\d)', tl)
    if m:
        k = int(m.group(1))
        pos = [i for i in cand if items[i].get('bench_position') == k]
        if len(pos) == 1:
            return pos[0]
    if 'active' in tl and 0 in cand and not m:
        return 0
    nm = [i for i in cand if items[i]['name'].lower() in tl or tl in items[i]['name'].lower()]
    if len(nm) == 0:
        # a distinctive word of the name ('owner benched Koffing' for Team Rocket's Koffing)
        nm = [i for i in cand if any(w in tl for w in re.findall(r"[a-z0-9']+", items[i]['name'].lower()) if len(w) >= 4 and w not in ("team", "rocket's"))]
    if len(nm) == 1:
        return nm[0]
    for word, k in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)):
        if word in tl:
            pos = [i for i in cand if items[i].get('bench_position') == k]
            if len(pos) == 1:
                return pos[0]
    if len(cand) == 1:
        return cand[0]
    return None


# ---------------------------------------------------------------------------------------------------------------- his deck

def evidence_texts(led, name):
    """(variant text, printed max HP) of every appearance of one of HIS Pokemon of this name anywhere in the ledger"""
    out = []
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        stad = stadium_name(t.get('board_at_start'))
        for key in ('board_at_start', 'board_after'):
            for p in instances((t.get(key) or {}).get('owner') or {}):
                if nname(p.get('name')) == name:
                    out.append((str(p.get('variant') or ''), shown_hp(p, stad)))
    return out


def settle_deck(spec, led):
    """give every entry of the deck one printing (`rid`): the first the files name, or, for an entry that stands for several functions, the one the ledger's
    attacks / Abilities / HP for his Pokemon of that name point to (distinct functions for distinct entries of one name); `flag` says when it is a guess"""
    by_name = collections.OrderedDict()
    for e in spec.entries:
        by_name.setdefault(e.name, []).append(e)
    for name, es in by_name.items():
        taken = {C.SIG[e.ids[0] if e.ids else e.cands[0]] for e in es if not e.ambiguous and (e.ids or e.cands)}
        ev = None
        for e in es:
            e.flag = None
            if not e.ambiguous:
                e.rid = e.ids[0] if e.ids else e.cands[0]
                continue
            ev = ev if ev is not None else evidence_texts(led, name)
            pool = [i for i in e.cands if C.SIG[i] not in taken] or e.cands
            scored = sorted(((sum(C.score_text(C.BYID[i], t, hp) for t, hp in ev), -n, i) for n, i in enumerate(pool)), reverse=True)
            top = scored[0][0]
            tied = {C.SIG[i] for s, _, i in scored if s == top}
            e.rid = scored[0][2]
            if top <= 0 or len(tied) > 1:
                e.flag = f'{name}: the ledger does not tell which of {", ".join(pool)} it is; {e.rid} used'
            taken.add(C.SIG[e.rid])
    return spec


class Alloc:
    """the cards of his deck not yet placed in one position: a name is given a printing from what is left, a Pokemon on the board by what the ledger shows of it"""

    def __init__(self, spec):
        self.entries = spec.entries
        self.left = {id(e): e.count for e in spec.entries}
        self.flags = []

    def entries_named(self, name):
        return [e for e in self.entries if e.name == name]

    def has(self, name):
        return bool(self.entries_named(name))

    def take(self, name, text=None, hp=None, certain=False):
        """-> printing id; None when the deck has no card of that name"""
        es = self.entries_named(name)
        if not es:
            return None
        funcs = {C.SIG[e.rid] for e in es}
        if len(funcs) > 1:
            # several functions under one name: a Pokemon with evidence picks by it, a card of the hand takes what is left
            pool = [e for e in es if self.left[id(e)] > 0] or es
            if text is not None or hp is not None:
                sc = [(C.score_text(C.BYID[e.rid], text or '', hp), -n, e) for n, e in enumerate(pool)]
                top = max(s for s, _, _ in sc)
                best = [e for s, _, e in sc if s == top]
                if (len({C.SIG[e.rid] for e in best}) > 1 or top <= 0) and not certain:
                    self.flags.append(f'{name}: which of {", ".join(sorted({e.rid for e in best}))} it is is not told by the ledger')
                e = max(sc)[2] if len(best) == 1 else best[0]
            else:
                e = pool[0]
                if len({C.SIG[x.rid] for x in pool}) > 1 and not certain:
                    self.flags.append(f'{name}: which of {", ".join(sorted({x.rid for x in pool}))} it is is not told by the ledger')
        else:
            pool = [e for e in es if self.left[id(e)] > 0] or es
            e = pool[0]
        self.left[id(e)] -= 1
        return e.rid

    def evidence(self, name, text, hp):
        """how strongly a ledger text points to one function of a name that stands for several in the deck (0 for a name with one)"""
        es = self.entries_named(name)
        if len({C.SIG[e.rid] for e in es}) < 2 or (text is None and hp is None):
            return 0
        return max(C.score_text(C.BYID[e.rid], text or '', hp) for e in es)

    def available(self, name):
        return sum(self.left[id(e)] for e in self.entries_named(name))


# ---------------------------------------------------------------------------------------------------------------- the opponent's cards

PRINTED_HP = re.compile(r'printed\s+(?:HP\s*)?(\d+)\s*(?:HP)?', re.I)


def opp_pick(name, hp_max, texts, tool=None, stadium=None):
    """-> (printing id, [other printings of other functions that fit equally]) among the database's cards of this name: the HP the ledger shows (a card fits when its printed HP plus what the Tool on
    it and the Stadium in play add is that HP; else when its printed HP is that HP although they would have added to it), the printed HP the ledger's text states ('printed 100 HP'), then the attack /
    Ability titles the ledger shows for it. `hp_max` is the HP shown, or a cardlib.HP that carries its own Tool and Stadium (030351: Darkrai at 120 under Starting Plains is the 100-HP card)"""
    cands = [c['id'] for c in C.BYNAME.get(name, []) if C.is_pokemon(c)] or [c['id'] for c in C.BYNAME.get(name, [])]
    if not cands:
        return None, []
    hpc = hp_max if isinstance(hp_max, C.HP) else (C.HP(hp_max, tool, stadium) if hp_max is not None else None)
    by_hp = cands
    if hpc is not None:
        by_hp = [i for i in cands if hpc.score(C.BYID[i]) == 2] or [i for i in cands if hpc.score(C.BYID[i]) >= 1] or cands
    printed = {int(m) for t_ in texts for m in PRINTED_HP.findall(str(t_ or ''))}
    by_hp = [i for i in by_hp if C.BYID[i].get('hp') in printed] or by_hp if printed else by_hp
    text = ' | '.join(texts)
    sc = sorted(((C.score_text(C.BYID[i], text, None), -n, i) for n, i in enumerate(by_hp)), reverse=True)
    top = sc[0][0]
    firsts = collections.OrderedDict()
    for s, _, i in sc:
        if s == top:
            firsts.setdefault(C.SIG[i], i)
    chosen = list(firsts.values())
    return chosen[0], chosen[1:]


def opp_texts(led):
    """name -> the ledger's descriptions of the opponent's Pokemon of that name (variant text of every appearance, and the attack titles it used)"""
    out = collections.defaultdict(list)
    for t in led['turns']:
        for key in ('board_at_start', 'board_after'):
            for p in instances((t.get(key) or {}).get('opponent') or {}):
                v = str(p.get('variant') or '')
                if v and v not in out[nname(p['name'])]:
                    out[nname(p['name'])].append(v)
        if not str(t.get('who_played', '')).startswith('owner'):
            for p in t.get('plays_in_order') or []:
                if nk(p.get('kind')) == 'attack':
                    cn = str(p.get('card_name') or '')
                    att, _ = attacker_of(t, cn)
                    out[att].append(cn + ' ' + str(p.get('result') or ''))
    return out


# ---------------------------------------------------------------------------------------------------------------- effects carried from the opponent's last turn

EFFECT_TEXTS = {
    # attack effect text in the database -> (whose Pokemon, [(CardEffect as the engine serialises it, turns)])
    "During your opponent's next turn, this Pokémon takes -20 damage from attacks.": ('attacker', [({'ReducedDamage': {'amount': 20}}, 1)]),
    "During your opponent's next turn, attacks used by the Defending Pokémon cost 2 [C] more, and its Retreat Cost is 2 [C] more.":
        ('defender', [({'IncreasedAttackCost': {'amount': 2}}, 1), ({'IncreasedRetreatCost': {'amount': 2}}, 1)]),
    # Budew's Prickly Powder: no Abilities until the Defending Pokemon leaves the Active Spot (the engine's UNTIL_LEAVES_ACTIVE_SPOT is 255 turns)
    'The Defending Pokémon loses all Abilities. This effect lasts until the Defending Pokémon leaves the Active Spot.': ('defender', [('NoAbilities', 255)]),
}


TURN_EFFECT_TEXTS = {
    # attack effect text -> the engine's TurnEffect for the player whose attack it was (the engine's `turn_effects`: [{turn, effect}])
    "During your next turn, attacks used by your Pokémon do +20 damage to your opponent's Active Pokémon.":
        lambda player: {'IncreasedDamageForPlayer': {'amount': 20, 'player': player, 'energy_type': None}},      # Happiny's Chubby Cheer
}
LASTING = re.compile(r'during your next turn|until this pok', re.I)      # an attack effect that is still there at the attacker's next turn


def attacker_of(row, cn, side='opponent'):
    """(Pokemon name, attack title) of an attack play of one side (the OPPONENT's by default): the ledger writes 'Stakataka: Brass Rock', or just 'Land Crush'; then the
    attacker is that side's Active Pokemon of that turn that has such an attack"""
    if ':' in cn:
        return nname(cn.split(':')[0]), cn.split(':', 1)[1].strip()
    name = nname(cn)
    if any(C.is_pokemon(c) for c in C.BYNAME.get(name, [])):
        return name, None
    for key in ('board_after', 'board_at_start'):
        act = (((row or {}).get(key) or {}).get(side) or {}).get('active')
        if _real(act) and any(cn.strip() in C.attack_titles(c) for c in C.BYNAME.get(nname(act['name']), []) if C.is_pokemon(c)):
            return nname(act['name']), cn.strip()
    return name, None


def lasting_turn_effects(prev_opp_row, prev_own_row, tn):
    """-> ([{turn, effect}], notes): what an attack left for a LATER turn, as the engine's `turn_effects` (a player-wide effect), and notes on lasting effects that are not modelled.
    The opponent's attack on turn tn-1 reaches its owner's next turn tn+1 (the engine files it under tn too, where it counts only for the player it names); an attack of his
    on his previous turn reaches tn"""
    tfx, notes, seen = [], [], set()
    for row, side, player, turns in ((prev_opp_row, 'opponent', 1, (tn, tn + 1)), (prev_own_row, 'owner', 0, (tn,))):
        for p in (row or {}).get('plays_in_order') or []:
            if nk(p.get('kind')) != 'attack':
                continue
            cn, res = str(p.get('card_name') or ''), str(p.get('result') or '')
            att_name, title = attacker_of(row, cn, side)
            for c in (c for c in C.BYNAME.get(att_name, []) if C.is_pokemon(c)):
                for a in c.get('attacks') or []:
                    if not ((title and a.get('title') == title) or (not title and a.get('title') and C.norm_text(a['title']) in C.norm_text(cn + res))):
                        continue
                    eff = a.get('effect') or ''
                    if eff in TURN_EFFECT_TEXTS:
                        for tk in turns:
                            x = {'turn': tk, 'effect': TURN_EFFECT_TEXTS[eff](player)}
                            if json.dumps(x, sort_keys=True) not in seen:
                                seen.add(json.dumps(x, sort_keys=True))
                                tfx.append(x)
                    elif eff not in EFFECT_TEXTS and LASTING.search(eff):
                        notes.append(f'{att_name} {a.get("title")}: "{eff}" is not carried into the position')
    return tfx, notes


def carried_effects(prev_opp_row, prev_owner_active, my_active_name, opp_active_name, my_lost_pokemon):
    """effects the opponent's last turn left on the board for his turn: [(side 'me'|'opp', pokemon name, effect, turns)] and notes about ones not modelled"""
    out, notes, seen = [], [], set()
    if not prev_opp_row:
        return out, notes
    for p in prev_opp_row.get('plays_in_order') or []:
        if nk(p.get('kind')) != 'attack':
            continue
        cn = str(p.get('card_name') or '')
        res = str(p.get('result') or '')
        att_name, title = attacker_of(prev_opp_row, cn)
        cards = [c for c in C.BYNAME.get(att_name, []) if C.is_pokemon(c)]
        for c in cards:
            for a in c.get('attacks') or []:
                if (title and a.get('title') == title) or (not title and a.get('title') and C.norm_text(a['title']) in C.norm_text(cn + res)):
                    eff = a.get('effect') or ''
                    if eff in EFFECT_TEXTS:
                        who, effs = EFFECT_TEXTS[eff]
                        if who == 'attacker':
                            new = [('opp', att_name, e, n) for e, n in effs]
                        elif not prev_owner_active or prev_owner_active == my_active_name:
                            # (no earlier turn of his: the Pokemon the attack hit is the one on the board now)
                            new = [('me', my_active_name, e, n) for e, n in effs]
                        else:
                            new = []
                        out += [x for x in new if json.dumps(x, sort_keys=True) not in seen and not seen.add(json.dumps(x, sort_keys=True))]
                    elif eff.startswith("During your opponent's next turn") or 'lasts until' in eff:
                        notes.append(f'{att_name} {a.get("title")}: "{eff}" is not carried into the position')
            ab = C.ability_title(c)
            if ab == 'Mach Stealth' and my_lost_pokemon:
                x = ('opp', att_name, 'PreventAllDamageAndEffects', 1)
                if json.dumps(x, sort_keys=True) not in seen:
                    seen.add(json.dumps(x, sort_keys=True))
                    out.append(x)
        # the same effect also carries on a Pokemon whose name the ledger gives only in the result text
    return out, notes


# ---------------------------------------------------------------------------------------------------------------- the opponent's discard, as the ledger names it

STAGE2 = {n for n, cs in C.BYNAME.items() if any(C.is_pokemon(c) and c.get('stage') == 2 for c in cs)}
EMPTY_DECK = re.compile(r'empty deck|deck (?:is )?empty|no cards? (?:left )?in (?:the |his |her |their )?deck', re.I)
TOP_PILE = re.compile(r'top pile (?:preview )?(?:is|shows?) ([^.;,]+?)\s*(?:[.;,]|$)', re.I)
GONE = ('none', 'null', 'empty', 'no stadium', '')


def stage2_in(text):
    """the Stage 2 Pokemon a ledger text names ('... directly into Dragonite'): the longest such name, or None"""
    t = str(text or '').lower()
    hits = [n for n in STAGE2 if n.lower() in t]
    return max(hits, key=len) if hits else None


def rc_count(counter, name):
    """how many Rare Candy evolutions the ledger gave for a Pokemon of this name: under its own name, or under the bare name the ledger wrote ('Tinkaton' for "Team Rocket's Tinkaton")"""
    return sum(n for k, n in counter.items() if n > 0 and (k == name or name.endswith(' ' + k)))


def rc_take(counter, name):
    """one of those evolutions is used up (the Pokemon it made left the board)"""
    k = next((k for k, n in counter.items() if n > 0 and (k == name or name.endswith(' ' + k))), None)
    if k is not None:
        counter[k] -= 1


def is_trainer_item(name):
    """a Trainer card that goes to the discard when played (not a Tool, which stays attached, nor a Stadium, which stays in play)"""
    cs = C.BYNAME.get(name)
    return bool(cs) and not any(C.is_pokemon(c) for c in cs) and not any(('Tool' in str(c.get('trainer_card_type', ''))) or ('Stadium' in str(c.get('trainer_card_type', ''))) for c in cs)


def opp_history(led):
    """-> {turn_number: what the ledger says of the OPPONENT's discard and deck BEFORE that row}: {'cards': [(name, variant text, printed HP)], 'energy': [types], 'hidden': n cards
    whose identity the ledger says is not readable, 'deck_empty': bool, 'rc_ids', 'rc_names': Pokemon of his a Rare Candy evolved (no Stage 1 under them)}.
    Taken from: his Pokemon that left the board (knocked out: with the cards under it, its Tool and its Energy), the Items and Supporters he played, his Stadium when another one
    replaced it, Energy he paid to retreat or that an attack of mine discarded off a Pokemon that is still there, a Tool of his that left a Pokemon that is still there, the
    cards the ledger names as discarded to pay an attack ('attack_cost_discard', "New top pile preview is X"), and a deck the ledger says is empty"""
    st = {'cards': [], 'energy': [], 'hidden': 0, 'deck_empty': False, 'rc_ids': set(), 'rc_names': collections.Counter(), 'ko_points': 0}
    out, prev_stad, stad_by = {}, None, {}
    for r in led['turns']:
        is_owner = str(r.get('who_played', '')).startswith('owner')
        b0, b1 = r.get('board_at_start') or {}, r.get('board_after') or {}
        # the Stadium: one of his that is gone from play by this row went to his discard
        sd = b0.get('stadium')
        played_by = str(sd.get('played_by') or '').lower() if isinstance(sd, dict) else ''
        sname = sd.get('name') if isinstance(sd, dict) else sd
        cur = nname(sname) if sname and str(sname).strip().lower() not in GONE else None
        if prev_stad and prev_stad[0] != cur and prev_stad[1] and C.BYNAME.get(prev_stad[0]):
            st['cards'].append((prev_stad[0], None, None))
        by = ('opp' if 'opp' in played_by else 'own') if played_by else stad_by.get(cur)
        prev_stad = (cur, by == 'opp') if cur else None
        # (the Stadium change above happened before this row: it is part of the state a position at this row starts from)
        out[r['turn_number']] = {'cards': list(st['cards']), 'energy': list(st['energy']), 'hidden': st['hidden'], 'deck_empty': st['deck_empty'],
                                 'rc_ids': set(st['rc_ids']), 'rc_names': collections.Counter(st['rc_names']), 'ko_points': st['ko_points']}
        if not is_owner:
            for p in r.get('plays_in_order') or []:
                kind = nk(re.sub(r'^opponent[_ ]', '', str(p.get('kind') or ''), flags=re.I))
                card, res = nname(p.get('card_name')), str(p.get('result') or '')
                if kind == 'attempt':
                    continue
                if kind == 'stadium' and card:
                    stad_by[card] = 'opp'
                if kind == 'attack':
                    for ev in p.get('nested_events_in_order') or []:
                        if isinstance(ev, dict) and re.search(r'discard', str(ev.get('kind') or ''), re.I) and 'mill' not in str(ev.get('kind')).lower():
                            nm = nname(ev.get('card_name')) if ev.get('card_name') else None
                            if nm and C.BYNAME.get(nm):
                                st['cards'].append((nm, None, None))
                            else:
                                st['hidden'] += 1
                elif kind == 'retreat':
                    st['energy'] += [t_ for t_, n_ in retreat_pay(p) for _ in range(n_)]
                elif 'rare candy' in str(p.get('card_name') or '').lower():
                    # (the ledger also writes it as "Rare Candy + Mega Gardevoir ex", as an evolution row)
                    st['cards'].append(('Rare Candy', None, None))
                    tg_ = str(p.get('target') or '').strip()
                    if tg_ and len(tg_) <= 3:
                        st['rc_ids'].add(tg_)
                    else:
                        evo = stage2_in(str(p.get('card_name') or '') + ' ' + tg_ + ' ' + res)
                        if evo:
                            st['rc_names'][evo] += 1
                elif kind in ('card_play', 'item_evolution') and is_trainer_item(card) and not (card == 'Lucky Ice Pop' and pop_returned(res)):
                    st['cards'].append((card, None, None))
            for ev in r.get('automatic_events_in_order') or []:
                txt = str(ev.get('event') or ev.get('description') or '') if isinstance(ev, dict) else str(ev)
                m = TOP_PILE.search(txt)
                if m and 'opponent' in txt.lower():
                    nm = nname(m.group(1))
                    if C.BYNAME.get(nm):
                        st['cards'].append((nm, None, None))
            if any(isinstance(d, dict) and EMPTY_DECK.search(json.dumps(d, ensure_ascii=False)) for d in r.get('draws_and_searches') or []):
                st['deck_empty'] = True
        # what left his board during this row
        if (b1.get('opponent') or {}) and (b0.get('opponent') or {}):
            start, after = instances(b0['opponent']), instances(b1['opponent'])
            pairs, kos = match_boards(start, after)
            for p in kos:
                nm = nname(p['name'])
                stk = stack_under(p)
                if stk is None:
                    stk = chain_names(nm)
                    ids = pids(p)
                    n_named = sum(1 for q in start if nname(q['name']) == nm)
                    if stk and ((ids and ids & st['rc_ids']) or (not ids and rc_count(st['rc_names'], nm) > 0 and n_named <= rc_count(st['rc_names'], nm))):
                        stk = stk[:1]
                if not pids(p):
                    rc_take(st['rc_names'], nm)
                st['cards'] += [(nm, str(p.get('variant') or ''), shown_hp(p, stadium_name(b0)))] + [(s, None, None) for s in stk]
                st['ko_points'] += 3 if (nm.startswith('Mega ') and nm.endswith(' ex')) else (2 if nm.endswith(' ex') else 1)      # what knocking it out scores (used to check the list)
                if tool_of(p) and C.BYNAME.get(tool_of(p)):
                    st['cards'].append((tool_of(p), None, None))
                st['energy'] += [t_ for t_, n_ in ebt(p) for _ in range(int(n_ or 0))]
            if is_owner:
                for a, n in pairs:
                    st['energy'] += list((collections.Counter(dict(ebt(a))) - collections.Counter(dict(ebt(n)))).elements())
                    ta = tool_of(a)
                    if ta and n.get('tool') is not None and tool_of(n) != ta and C.BYNAME.get(ta):
                        st['cards'].append((ta, None, None))
    return out


# ---------------------------------------------------------------------------------------------------------------- one game

# the ledger's wordings of a Special Condition -> the engine's name (StatusCondition in engine/src/models/card.rs)
CONDITIONS = {'asleep': 'Asleep', 'sleep': 'Asleep', 'paralyzed': 'Paralyzed', 'paralysed': 'Paralyzed', 'paralysis': 'Paralyzed',
              'confused': 'Confused', 'confusion': 'Confused', 'poisoned': 'Poisoned', 'poison': 'Poisoned', 'burned': 'Burned', 'burn': 'Burned'}


def condition_key(x):
    return str(x).strip().lower()


def convert_game(gdir, global_entities):
    gname = os.path.basename(gdir.rstrip('/'))
    short = gname.replace('_iOS', '')[2:]
    led = load_json(os.path.join(gdir, 'TURN_LEDGER.json'))
    deckj = load_json(os.path.join(gdir, 'DECK_USED.json'))
    spec = D.read_deck(deckj, global_entities)
    if spec is None:
        raise ValueError('no 20-card list in DECK_USED.json')
    settle_deck(spec, led)
    game_notes = list(spec.notes) + [e.flag for e in spec.entries if getattr(e, 'flag', None)]
    deck_ids = collections.Counter()
    for e in spec.entries:
        deck_ids[e.rid] += e.count
    energy = spec.energy or ['Water']
    deck_info = {'energy': energy, 'cards': [{'name': C.nname(C.BYID[i]['name']), 'id': i, 'count': n} for i, n in deck_ids.items()],
                 'source': spec.source, 'notes': game_notes, 'version_unverified': spec.version_unverified, 'status': spec.status}
    names_in_deck = {e.name for e in spec.entries}
    ispoke = {n: any(C.is_pokemon(c) for c in C.BYNAME.get(n, [])) for n in names_in_deck}
    isbasic = {n: ispoke[n] and all(c.get('stage', 0) == 0 for c in C.BYNAME[n] if C.is_pokemon(c)) for n in names_in_deck}
    trainer_type = {n: str((C.BYNAME[n][0] or {}).get('trainer_card_type', '')) for n in names_in_deck if not ispoke[n]}
    TOOLS = {n for n, t in trainer_type.items() if 'Tool' in t}
    STADIUMS = {n for n, t in trainer_type.items() if 'Stadium' in t}
    TRAINER_DISCARD = set(trainer_type)
    opp_ev = opp_texts(led)
    opp_hist = opp_history(led)
    turns = led['turns']
    owner_idx =[i for i, t in enumerate(turns) if str(t.get('who_played', '')).startswith('owner')]
    if not owner_idx:
        return [], [], deck_info
    first_player = turns[owner_idx[0]]['turn_number'] == 1
    decks_energy = energy[0]
    positions, skipped = [], []
    disc, disc_energy = [], []                      # names of his discarded cards, and Energy
    stad_owner_by_card = {}
    my_stad = None
    rc_ids = set()      # instance ids of Pokemon of his that a Rare Candy evolved: they have no Stage 1 under them
    rc_names = collections.Counter()      # the same for a Rare Candy whose target the ledger gives no id for: the name it evolved into
    mill_total = 0
    me_deck_empty = False
    ev_cache = {}

    def ev_for(name):
        """(text, HP) the ledger shows for his Pokemon of this name anywhere in the game: the evidence for which printing a stack card of that name is"""
        if name not in ev_cache:
            ev = evidence_texts(led, name)
            ev_cache[name] = (' | '.join(t for t, _ in ev), next((hp for _, hp in ev if hp), None))
        return ev_cache[name]

    def take_stack(alloc_, u):
        """a card under one of his Pokemon: the printing the ledger's earlier readings of that Pokemon point to"""
        txt, hp_ = ev_for(u)
        return alloc_.take(u, text=txt or None, hp=hp_)

    def evolved_into(text):
        """the Stage 1 / 2 Pokemon of his deck a ledger text names ('... directly into Guts Conkeldurr150HP'): the longest such name"""
        names_ = [n for n in names_in_deck if ispoke[n] and chain_names(n) and n.lower() in str(text).lower()]
        return max(names_, key=len) if names_ else None

    def rc_flag(p, name, n_named):
        """did a Rare Candy evolve this Pokemon of his (so no Stage 1 is under it)? By instance id when it has one, else by the name it evolved into"""
        ids = pids(p)
        if ids:
            return bool(ids & rc_ids)
        return rc_names[name] > 0 and n_named <= rc_names[name]
    knockouts = 0      # his own Pokemon knocked out so far this game (Kingambit's Overlord's Blade; pg_pos.rs reads me.knockouts), Oct 13
    for k, ti in enumerate(owner_idx):
        t = turns[ti]
        tn = t['turn_number']
        notes = []
        for cor in led.get('corrections') or []:      # what normalize_ledger.py corrected in this ledger from the frames (recorded overrides)
            if not cor.get('turns') or tn in cor['turns']:
                notes.append('ledger corrected from the frames: ' + str(cor.get('note') or cor.get('id')))
        b = t['board_at_start']
        own_inst, opp_inst = instances(b['owner']), instances(b['opponent'])
        pt = turns[owner_idx[k - 1]] if k > 0 else None
        lost_mine = False
        milled_named = []      # cards of his the opponent's last attack milled that the ledger shows
        if any(isinstance(d, dict) and EMPTY_DECK.search(json.dumps(d, ensure_ascii=False)) for d in t.get('draws_and_searches') or []):
            me_deck_empty = True
        if pt is not None:
            for p in pt.get('plays_in_order') or []:
                card = nname(p.get('card_name'))
                res_ = str(p.get('result') or '')
                if card == 'Rare Candy' and nk(p.get('kind')) != 'attempt':
                    tg_ = str(p.get('target') or '').strip()
                    if tg_ and len(tg_) <= 3:
                        rc_ids.add(tg_)
                    else:
                        evo_ = evolved_into(tg_ + ' ' + res_)
                        if evo_:
                            rc_names[evo_] += 1
                returns = card == 'Lucky Ice Pop' and pop_returned(res_)
                nothing = NOTHING_FOUND.search(res_) and card == 'Poké Ball'
                if nk(p.get('kind')) in ('card_play', 'item_evolution') and card in TRAINER_DISCARD and card not in TOOLS and card not in STADIUMS and not returns:
                    disc.append((card, None, None))
                if card in STADIUMS and nk(p.get('kind')) in ('stadium', 'card_play'):
                    if my_stad and my_stad != card:
                        disc.append((my_stad, None, None))
                    stad_owner_by_card[card] = 0
                    my_stad = card
                if nk(p.get('kind')) == 'retreat':
                    for tt, n_ in retreat_pay(p):
                        disc_energy += [tt] * n_
            cur_st = b.get('stadium')
            cur_st = cur_st.get('name') if isinstance(cur_st, dict) else cur_st
            cur_name = nname(cur_st) if cur_st and str(cur_st).strip().lower() not in ('none', 'null', 'empty', 'no stadium') else None
            if my_stad and cur_name != my_stad:
                disc.append((my_stad, None, None))   # his Stadium was replaced by the opponent's
                my_stad = None
            after = instances(pt.get('board_after', {}).get('owner') or {})
            # which of his Pokemon the opponent's turn knocked out (by instance id, evolution, or what is on it: not by name alone), and what left the others
            pairs, kos = match_boards(after, own_inst)
            # and what the checkup after his own previous turn knocked out: that row's `board_after` is already past it (Oct 13)
            ckos, cnotes = checkup_knockouts(pt)
            notes += cnotes
            ck_ids = {id(x) for x in ckos}
            kos = kos + ckos
            between = [x for x in turns[owner_idx[k - 1] + 1:ti] if not str(x.get('who_played', '')).startswith('owner')]
            moved = []      # Energy the opponent MOVED off one of his Pokemon (Thieving Incisors): it is on the opponent's Pokemon, not in his discard
            for x in between:
                for p in x.get('plays_in_order') or []:
                    mv = re.search(r'moves?\s+(?:one|1|an?|\d+)\s+(\w+)\s+(?:Energy\s+)?from\s+(?:the\s+|owner\s+|your\s+|Active\s+|Benched?\s+)*(.+?)\s+to\s', str(p.get('result') or ''), re.I)
                    if mv and etype(mv.group(1)):
                        moved.append((etype(mv.group(1)), nname(mv.group(2))))
            for p in kos:
                nm = nname(p['name'])
                if nm not in names_in_deck:
                    continue
                at_checkup = id(p) in ck_ids      # knocked out after his own turn ended, not by the opponent's attack: no Mach Stealth, and nothing of it was moved by the opponent
                lost_mine = lost_mine or not at_checkup
                knockouts += 1
                st = stack_under(p)
                if st is None:
                    st = chain_names(nm)
                    if st and rc_flag(p, nm, sum(1 for q in after + ckos if nname(q['name']) == nm)):
                        st = st[:1]
                if not pids(p) and rc_names[nm] > 0:
                    rc_names[nm] -= 1
                disc += [(nm, str(p.get('variant') or ''), shown_hp(p, stadium_name(pt.get('board_at_start'))))] + [(s, None, None) for s in st if s in names_in_deck]
                tool = tool_of(p)
                if tool and tool in names_in_deck:
                    disc.append((tool, None, None))
                en_ = [tt for tt, n in ebt(p) for _ in range(int(n or 0))]
                for mvd in ([] if at_checkup else list(moved)):
                    if mvd[1] == nm and mvd[0] in en_:
                        en_.remove(mvd[0])
                        moved.remove(mvd)
                disc_energy += en_
                notes.append(f'knocked out at the checkup after his turn ended: {nm}' if at_checkup else f'knocked out between turns: {nm}')
            for x in between:
                for p in x.get('plays_in_order') or []:
                    for ev in p.get('nested_events_in_order') or []:
                        if isinstance(ev, dict) and str(ev.get('kind') or '').lower() == 'deck_mill' and 'owner' in str(ev.get('destination') or 'owner').lower():
                            shown = [c.get('name') if isinstance(c, dict) else c for c in ev.get('cards_in_reveal_order') or []] + [ev.get('visible_final_discard_top')]
                            for nm in dict.fromkeys(nname(c) for c in shown if c):
                                milled_named.append(nm)
                                if nm in names_in_deck:
                                    disc.append((nm, None, None))
            for a_, n_ in pairs:
                # a Tool that was on a Pokemon of his when his turn ended and is gone from the Pokemon that is still there (Field Blower, a Tool that discards itself)
                ta = tool_of(a_)
                if ta and n_.get('tool') is not None and tool_of(n_) != ta and ta in names_in_deck:
                    disc.append((ta, None, None))
                    notes.append(f'{ta} left {nname(a_["name"])} between the turns (discarded)')
        # hand
        hs = t.get('hand_at_start') or {}
        raw = hs.get('cards_left_to_right') or []
        names = [nname(c.get('name') if isinstance(c, dict) else c) for c in raw]
        # what the ledger reads on a card of the hand: its variant ('B1 172; Superb Shield 80, HP140') and what is written after its name ("Aegislash (Cursed Metal / Slicing Blade)",
        # "Conkeldurr [A3 096 Guts / Mega Punch]")
        hvars = []
        for c in raw:
            nm_raw = str(c.get('name') if isinstance(c, dict) else c)
            paren = re.search(r'[\(\[](.*)[\)\]]\s*$', nm_raw)
            hvars.append(' '.join(x for x in (str(c.get('variant') or '') if isinstance(c, dict) else '', paren.group(1) if paren else '') if x))
        if not raw or any(n is None or n not in names_in_deck for n in names) or (hs.get('count') is not None and hs['count'] != len(names)):
            skipped.append({'game': short, 'turn': tn, 'reason': f'hand not fully named or unmapped: {names} count={hs.get("count")}'})
            continue
        alloc = Alloc(spec)
        opp_alts = []
        ohist = opp_hist.get(tn) or {'cards': [], 'energy': [], 'hidden': 0, 'deck_empty': False, 'rc_ids': set(), 'rc_names': collections.Counter()}

        def opp_rc_flag(p, name, n_named):
            ids = pids(p)
            if ids:
                return bool(ids & ohist['rc_ids'])
            return rc_count(ohist['rc_names'], name) > 0 and n_named <= rc_count(ohist['rc_names'], name)
        try:
            stad_now = stadium_name(b)

            def mk(p, mine):
                name = nname(p['name'])
                text = ' | '.join([str(p.get('variant') or '')] + ([] if mine else opp_ev.get(name, [])))
                if mine:
                    cid_ = alloc.take(name, text=str(p.get('variant') or ''), hp=shown_hp(p, stad_now))
                else:
                    cid_, alts = opp_pick(name, shown_hp(p, stad_now), [str(p.get('variant') or '')] + opp_ev.get(name, []))
                    if alts:
                        opp_alts.append({'name': name, 'used': cid_, 'could_also_be': alts})
                if cid_ is None:
                    raise KeyError(f'no card id for {name} ({p.get("hp_max")})')
                d = {'card': f'{name} {cid_}', 'hp': p['hp_now']}
                en = []
                for tt, n in ebt(p):
                    en += [tt] * int(n or 0)
                if en:
                    d['energy'] = en
                tool = p.get('tool')
                if tool and str(tool).lower() not in ('none', 'null'):
                    tn_ = nname(tool)
                    tid = alloc.take(tn_) if mine else (C.BYNAME[tn_][0]['id'] if C.BYNAME.get(tn_) else None)
                    if tid is None:
                        raise KeyError(f'unknown tool {tool}')
                    d['tools'] = [f'{tn_} {tid}']
                under = stack_under(p)
                derived = under is None
                if derived:
                    under = chain_names(name)
                    if under and mine and rc_flag(p, name, sum(1 for q in own_inst if nname(q['name']) == name)):
                        under = under[:1]    # a Rare Candy took it from the Basic to its Stage 2
                        notes.append(f'{name}: a Rare Candy evolved it, so no Stage 1 is under it')
                    elif under and not mine and opp_rc_flag(p, name, sum(1 for q in opp_inst if nname(q['name']) == name)):
                        under = under[:1]    # the opponent's Rare Candy: the Stage 1 was skipped
                        notes.append(f'the opponent\'s {name}: a Rare Candy evolved it, so no Stage 1 is under it')
                    elif under:
                        notes.append(f'{name} stack taken from the printed evolution line (the ledger gives none)')
                if under and mine and derived:
                    d['_under'] = list(under)     # placed last, from what the hand and the discard leave (a Rare Candy may have skipped a stage)
                elif under:
                    behind = []
                    for u in reversed(under):
                        if mine:
                            uid = take_stack(alloc, u)
                            if uid is None:
                                continue
                            behind.append(f'{u} {uid}')
                        else:
                            uid, alts_u = opp_pick(u, None, opp_ev.get(u, []))
                            if uid is None:
                                continue
                            if alts_u:
                                opp_alts.append({'name': u, 'used': uid, 'could_also_be': alts_u, 'under': name})
                            behind.append(f'{u} {uid}')
                    d['behind'] = list(reversed(behind))
                # Special Conditions (Oct 13): the engine's names, which pg_pos.rs sets on the Pokemon; a condition the engine has no name for
                # stays a note
                conds = p.get('special_conditions') or []
                known = [CONDITIONS[c] for c in (condition_key(x) for x in conds) if c in CONDITIONS]
                if known:
                    d['conditions'] = list(dict.fromkeys(known))
                unknown = [x for x in conds if condition_key(x) not in CONDITIONS]
                if unknown:
                    notes.append(f'{name} is {"/".join(map(str, unknown))} (not represented: the engine has no such condition)')
                d['_name'] = name
                return d
            me_board = [mk(p, True) for p in own_inst]
            opp_board = [mk(p, False) for p in opp_inst]
        except KeyError as e:
            skipped.append({'game': short, 'turn': tn, 'reason': f'board: {e}'})
            continue
        pts_me, pts_opp = b['owner'].get('points'), b['opponent'].get('points')
        if pts_me is None or pts_opp is None:
            skipped.append({'game': short, 'turn': tn, 'reason': f'points missing ({pts_me},{pts_opp})'})
            continue
        oh = t.get('opponent_hand_at_owner_turn_start') or {}
        opp_hand = oh.get('count')
        if opp_hand is None and oh.get('supported_range'):
            opp_hand = oh['supported_range'][0]
            notes.append(f"opponent hand range {oh['supported_range']}: the lower end is used")
        if opp_hand is None:
            skipped.append({'game': short, 'turn': tn, 'reason': 'opponent hand count missing'})
            continue
        st = b.get('stadium')
        st_by = None
        if isinstance(st, dict):
            st_by = str(st.get('played_by') or '').lower()
            st = st.get('name') or st.get('card')
        stadium = None
        if st and str(st).strip().lower() not in ('none', 'null', 'empty', 'no stadium'):
            sn = nname(st)
            if sn in names_in_deck and st_by != 'opponent':
                owner0 = stad_owner_by_card.get(sn) == 0
                stadium = {'card': f'{sn} {alloc.take(sn) if owner0 else C.BYNAME[sn][0]["id"]}', 'owner': 0 if owner0 else 1}
            else:
                cs = C.BYNAME.get(sn)
                if cs:
                    stadium = {'card': f'{sn} {cs[0]["id"]}', 'owner': 1}
                else:
                    skipped.append({'game': short, 'turn': tn, 'reason': f'stadium {st} unmapped'})
                    continue
        # hand and discard: what is left of the deck (the Pokemon on the board, their stacks, Tools and the Stadium were placed first)
        turn_text = ' | '.join(str(p.get(x) or '') for p in (t.get('plays_in_order') or []) for x in ('card_name', 'target', 'result'))
        reqs = [('hand', i, n, (hvars[i] + ' | ' if hvars[i] else '') + turn_text, hp_in(hvars[i])) for i, n in enumerate(names)] + [('disc', i, n, tx, hp) for i, (n, tx, hp) in enumerate(disc)]
        reqs.sort(key=lambda r: -alloc.evidence(r[2], r[3], r[4]))
        got = {}
        extra_disc = []
        asked = collections.Counter(r[2] for r in reqs)
        kinds_asked = collections.defaultdict(set)
        for r in reqs:
            kinds_asked[r[2]].add(r[0])
        for kind_, i, n, tx, hp in reqs:
            if kind_ == 'disc' and alloc.available(n) <= 0:
                extra_disc.append(n)
                continue
            # every copy that is left is asked for, all as the same kind of card: which printing goes where cannot matter
            certain = len(kinds_asked[n]) == 1 and asked[n] >= alloc.available(n)
            got[(kind_, i)] = f'{n} {alloc.take(n, text=tx, hp=hp, certain=certain)}'
            asked[n] -= 1
        hand = [got[('hand', i)] for i in range(len(names))]
        pdisc = [got[('disc', i)] for i in range(len(disc)) if ('disc', i) in got]
        for n in extra_disc:
            notes.append(f'one {n} taken out of the discard guess (the list holds too few)')
        # the stacks the ledger does not give: the printed evolution line, from what is left of the deck (a stage the deck has no copy left of was skipped by a Rare Candy)
        for pk in me_board:
            under = pk.pop('_under', None)
            if under:
                behind = []
                for u in reversed(under):
                    if alloc.available(u) > 0:
                        behind.append(f'{u} {take_stack(alloc, u)}')
                    else:
                        notes.append(f'{pk["_name"]}: no {u} is left in the list, so the stack leaves it out (Rare Candy)')
                if behind:
                    pk['behind'] = list(reversed(behind))
        notes += alloc.flags
        # ---- carried effects of the opponent's last turn
        prev_opp = next((x for x in turns if x.get('turn_number') == tn - 1 and not str(x.get('who_played', '')).startswith('owner')), None)
        prev_owner_active = nname(((pt or {}).get('board_after') or {}).get('owner', {}).get('active', {}).get('name')) if pt else None
        my_active_name = me_board[0]['_name'] if me_board else None
        opp_active_name = opp_board[0]['_name'] if opp_board else None
        eff, eff_notes = carried_effects(prev_opp, prev_owner_active, my_active_name, opp_active_name, lost_mine)
        notes += eff_notes
        turn_fx, turn_fx_notes = lasting_turn_effects(prev_opp, pt, tn)
        notes += turn_fx_notes
        for p in (prev_opp or {}).get('plays_in_order') or []:
            mm = re.search(r'discards?\s+(?:the\s+)?top\s*(\d+)[^.;]*(?:owner|your)\s*deck', str(p.get('result') or ''), re.I)
            if mm:
                named_here = list(dict.fromkeys(milled_named))
                if named_here:
                    unlisted = [x for x in named_here if x not in names_in_deck]
                    notes.append(f'the opponent\'s attack discarded the top {mm.group(1)} cards of his deck: {", ".join(named_here)} named by the ledger'
                                 + (f' ({", ".join(unlisted)} not in his list: left out)' if unlisted else ' and put in his discard')
                                 + f'; the other {max(0, int(mm.group(1)) - len(named_here))} are not known (they stay in the deck here)')
                else:
                    notes.append(f'the opponent\'s attack discarded the top {mm.group(1)} cards of his deck (which ones is not known: they stay in the deck here)')
        for side, nm_, e_, turns_n in eff:
            board = me_board if side == 'me' else opp_board
            tgt = next((pk for pk in board[:1] if pk['_name'] == nm_), None) or next((pk for pk in board if pk['_name'] == nm_), None)
            if tgt is not None:
                tgt.setdefault('effects', []).append({'effect': e_, 'turns': turns_n})
        for pk in me_board + opp_board:
            pk.pop('_name', None)
        # ---- his plan, with indices resolved against the board as it changes during the turn
        plan, unresolved = [], []
        # (the engine's slots: [Active, Bench 1..3]. A slot Ilima emptied is None until a Pokemon is benched into it or promoted out of another one)
        items = [{'name': nname(p['name']), 'bench_position': bpos(p), 'ids': {x for x in (p.get('instance_id'), p.get('physical_instance')) if x}} for p in own_inst]
        ended = False
        pending_promote = False      # Ilima put his Active into his hand and the ledger has not yet said which Pokemon he promoted
        plays = list(t.get('plays_in_order') or [])

        def place(new):
            """a Pokemon he benches goes to the first empty Bench slot (the engine's choice; Ilima leaves one open)"""
            for si_ in range(1, len(items)):
                if items[si_] is None:
                    items[si_] = new
                    return si_
            items.append(new)
            return len(items) - 1

        def promote(j):
            plan.append(f'Promote:0@{j}')
            items[0], items[j] = items[j], None
            items[0]['bench_position'] = None

        def promoted_in(txt, whole):
            """the Benched Pokemon a text says he promoted: the one named after the word 'promotes' (the whole text of a promotion row), else the only one on the Bench; None when it is not told"""
            rest = txt
            if not whole:
                m_ = re.search(r'promot', txt, re.I)
                if not m_:
                    live_ = [i_ for i_ in range(1, len(items)) if items[i_] is not None]
                    return live_[0] if len(live_) == 1 else None
                rest = txt[m_.start():]
            hits_ = [i_ for i_ in range(1, len(items)) if items[i_] is not None and items[i_]['name'].lower() in rest.lower()]
            return hits_[0] if len(hits_) == 1 else None

        def ilima_returned(txt):
            """the slot of the Pokemon Ilima put into his hand: his Active when the text names it, else the one Pokemon it names"""
            named_ = [i_ for i_, x in enumerate(items) if x is not None and x['name'].lower() in txt.lower()]
            if 0 in named_:
                return 0
            return named_[0] if len(named_) == 1 else None
        for p in plays:
            kind, card, res, tg = nk(p.get('kind')), nname(p.get('card_name')), str(p.get('result') or ''), p.get('target')
            resp = str(p.get('response') or '')
            ptxt = ' '.join(str(x or '') for x in (p.get('prompt_text'), p.get('response'), tg, res))
            if pending_promote and kind != 'attempt':
                if re.search(r'promot|replace', str(p.get('kind') or ''), re.I) or (kind == 'prompt_response' and re.search(r'replacement|promot', ptxt, re.I)):
                    j_ = promoted_in(ptxt, True)
                    if j_ is None:
                        plan.append('Promote:0@?')
                        unresolved.append(f'promotion after Ilima {ptxt!r}')
                    else:
                        promote(j_)
                    pending_promote = False
                    continue
                plan.append('Promote:0@?')      # something else came first: the ledger does not say which Pokemon he promoted
                unresolved.append('Ilima: the Pokemon he promoted is not told')
                pending_promote = False
            if kind in ('end',):
                ended = True
            elif kind == 'attempt':
                continue   # an attempt that was not carried out (a cancelled Wally)
            elif kind == 'prompt_response':
                if re.search(r'boiler smog', ptxt, re.I) and re.search(r'\b(yes|ok|accept)', ptxt, re.I) and not re.search(r'cancel|declin', ptxt, re.I):
                    plan.append('Ability')
                continue
            elif kind in ('card_play', 'bench') and card in names_in_deck and ispoke[card] and isbasic[card]:
                plan.append(f'Place:{card}')
                mm = re.search(r'bench\s*(?:position\s*)?(\d)', str(tg).lower())
                bp = int(mm.group(1)) if mm else next((k2 for w, k2 in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)) if w in str(tg).lower()), None)
                new_id = re.search(r'\bPlace\s+([A-Za-z]\d?)\b', res)
                place({'name': card, 'bench_position': bp, 'ids': {new_id.group(1)} if new_id else set()})
            elif kind == 'card_play' and card == 'Ilima' and card in names_in_deck:
                plan.append('Play:Ilima')
                itxt = ' '.join(str(x or '') for x in (tg, res, p.get('details')))
                ri = ilima_returned(itxt)
                if ri is None:
                    plan.append('Promote:0@?')
                    unresolved.append(f'Ilima: the Pokemon that went back to his hand is not told ({itxt!r})')
                else:
                    items[ri] = None
                    if ri == 0:
                        j_ = promoted_in(itxt, False)
                        if j_ is None:
                            pending_promote = True
                        else:
                            promote(j_)
            elif kind in ('card_play', 'item_evolution', 'stadium') and card == 'Rare Candy':
                mm = re.search(r'(.*?)\s*->\s*(.+)$', str(tg or ''))
                plan.append('Play:Rare Candy')
                if mm and nname(mm.group(2)) in names_in_deck:
                    i = resolve(items, mm.group(1))
                    plan.append(f'Evolve:{nname(mm.group(2))}@{i if i is not None else "?"}')
                    if i is None:
                        unresolved.append(f'Rare Candy target {tg!r}')
                    else:
                        items[i]['name'] = nname(mm.group(2))
                else:
                    i = resolve(items, tg) if tg else resolve(items, res)
                    s2 = []
                    if i is not None:
                        base = items[i]['name']
                        s2 = [n for n in dict.fromkeys(names) if n in names_in_deck and ispoke.get(n) and chain_names(n)[:1] == [base] and any(c.get('stage') == 2 for c in C.BYNAME[n])]
                        if len(s2) != 1:
                            s2 = [n for n in s2 if n in (res + ' ' + str(tg))] or s2
                    if i is not None and len(s2) == 1:
                        plan.append(f'Evolve:{s2[0]}@{i}')
                        items[i]['name'] = s2[0]
                    else:
                        plan.append('Evolve:?@?')
                        unresolved.append(f'Rare Candy target {tg!r}')
            elif kind == 'card_play' and card in names_in_deck and ispoke[card]:
                i = resolve(items, tg)
                plan.append(f'Evolve:{card}@{i if i is not None else "?"}')
                if i is None:
                    unresolved.append(f'evolution target {tg!r}')
                else:
                    items[i]['name'] = card
                if re.search(r'use boiler smog', resp, re.I):
                    plan.append('Ability')
            elif kind == 'card_play' and card == 'Poké Ball' and NOTHING_FOUND.search(res):
                notes.append('a Poké Ball that found nothing is left out of his plan (the engine does not offer it)')
            elif kind in ('card_play', 'stadium') and card in names_in_deck and card not in TOOLS:
                plan.append(f'Play:{card}')
                if card == 'Quick-Grow Extract':
                    # it evolves the Pokemon at once: what it became is the one whose attack he can then use
                    evo_, i_qg = evolved_into(res), resolve(items, tg)
                    if evo_ and i_qg is not None:
                        items[i_qg]['name'] = evo_
                if card == 'Wally':
                    i = resolve(items, tg if tg and tg != 'None' else res)
                    if i is None:
                        i = resolve(items, res)
                    plan.append(f'Attach:1Colorless@{i if i is not None else "?"} fx')
                    if i is None:
                        unresolved.append(f'Wally target {tg!r} / {res!r}')
            elif kind == 'tool' or (kind == 'card_play' and card in TOOLS):
                plan.append(f'Play:{card}')
                i = resolve(items, tg)
                plan.append(f'Tool:{card}@{i}' if i is not None else f'Tool:{card}@?')
                if i is None:
                    unresolved.append(f'tool target {tg!r}')
            elif kind == 'evolution':
                i = resolve(items, tg)
                plan.append(f'Evolve:{card}@{i}' if i is not None else f'Evolve:{card}@?')
                if i is None:
                    unresolved.append(f'evolution target {tg!r}')
                else:
                    items[i]['name'] = card
                if re.search(r'boiler smog', res + ' ' + resp, re.I) and not re.search(r'offered|decline', res, re.I):
                    plan.append('Ability')
            elif kind == 'energy_attachment':
                i = resolve(items, tg)
                plan.append(f'Attach:1{etype((p.get("energy") or {}).get("type")) or decks_energy}@{i if i is not None else "?"} zone')
                if i is None:
                    unresolved.append(f'attach target {tg!r}')
            elif kind == 'retreat':
                i = None
                arrow = re.split(r'→|->', str(tg))
                for cand_text in ([arrow[-1].strip()] if len(arrow) > 1 else []) + [str(tg), res]:
                    i2 = resolve(items, cand_text)
                    if i2 is not None and i2 != 0:
                        i = i2
                        break
                if i is None:
                    hits = [j for j in range(1, len(items)) if items[j] is not None and re.search(r'(?:promot\w*|becomes?|new)\s+(?:the\s+)?(?:Active\s+)?' + re.escape(items[j]['name']) + r'|' + re.escape(items[j]['name']) + r'\s+(?:is\s+)?(?:promoted|becomes Active|Active|to Active)', res + ' ' + str(tg), re.I)]
                    if len(hits) == 1:
                        i = hits[0]
                plan.append(f'Retreat:{i}' if i is not None else 'Retreat:?')
                if i is None:
                    unresolved.append(f'retreat target {tg!r} / {res!r}')
                else:
                    # the two swap places, slot and all (a later "B on bench2" must find the one that retreated there)
                    items[0], items[i] = items[i], items[0]
                    items[0]['bench_position'], items[i]['bench_position'] = items[i].get('bench_position'), items[0].get('bench_position')
            elif kind == 'ability' and (card in STADIUMS or is_stadium_card(card) or 'stadium' in str(p.get('kind')).lower()):
                plan.append('UseStadium')
            elif kind == 'ability':
                if not (plan and plan[-1] == 'Ability' and re.search(r'boiler smog', card + ' ' + res, re.I)):
                    plan.append('Ability')
                # an Ability that takes an Energy of a chosen type from his discard (Dragon's Blessing): the engine asks which type, and the choice is a step of its own
                e_ = p.get('energy') if isinstance(p.get('energy'), dict) else {}
                if etype(e_.get('type')) and re.search(r'discard', res + ' ' + str(p.get('details') or ''), re.I):
                    i = resolve(items, e_.get('destination') or tg)
                    plan.append(f'AttachTypedFromDiscard:{etype(e_["type"])}@{i if i is not None else "?"}')
                    if i is None:
                        unresolved.append(f'Energy target of the Ability {e_.get("destination") or tg!r}')
            elif kind in ('card_play', 'stadium', 'tool', 'bench', 'evolution') and card and card not in names_in_deck:
                notes.append(f'a play of {card!r}, which is not in the deck list, is left out of his plan')
            elif kind == 'attack':
                act = items[0]['name'] if items and items[0] is not None else None
                act_cards = [C.BYID[e.rid] for e in spec.entries if e.name == act]
                tl = list(dict.fromkeys(a.get('title') for c in act_cards for a in (c.get('attacks') or []) if a.get('title')))
                named = str(p.get('card_name') or '').replace('’', "'")
                after_c = named.split(':', 1)[1].strip() if ':' in named else ''
                hit = [x for x in tl if x and (x.lower() == after_c.lower() or C.norm_text(x) in C.norm_text(res + ' ' + named))]
                plan.append(f'Attack:{hit[0] if hit else (tl[-1] if tl else act)}')
                if not hit:
                    notes.append(f'attack title of {act} not named in the ledger: the last printed attack is used')
                # an attack that takes an Energy from the zone and attaches it to a Benched Pokemon (Turbo Shark, Giga Turbo): the engine asks where, and the choice is a step of its own
                fx_m = None
                for c_ in (act_cards if hit else []):
                    for a_ in c_.get('attacks') or []:
                        if a_.get('title') == hit[0]:
                            fx_m = fx_m or re.search(r'Take an? \[(\w)\] Energy from your Energy Zone and attach it to 1 of your Benched', a_.get('effect') or '')
                if fx_m:
                    tail = re.split(r'attach', res, maxsplit=1, flags=re.I)
                    tail = tail[1] if len(tail) > 1 else res
                    sel = re.search(r'select\w*\s+([^,;]+)', res, re.I)     # "... prompt selects Wailord Bench2, attach1 Water resolved ..."
                    j = None
                    for txt_ in ([sel.group(1)] if sel else []) + [tail]:
                        j = resolve(items, txt_)
                        if j in (None, 0):
                            names_hit = [x for x in range(1, len(items)) if items[x] is not None and items[x]['name'].lower() in txt_.lower()]
                            j = names_hit[0] if len(names_hit) == 1 else None
                        if j not in (None, 0):
                            break
                    if j == 0:
                        j = None     # it goes to a Benched Pokemon
                    en = C.TYPE_LETTERS.get(fx_m.group(1)) or etype(next(iter(re.findall(r'\b(' + '|'.join(ETYPES) + r')\b', res)), None)) or 'Water'
                    plan.append(f'Attach:1{en}@{j if j is not None else "?"} fx')
                    if j is None:
                        unresolved.append(f'{hit[0]} Energy target in {res!r}')
                ended = True
        if pending_promote:
            plan.append('Promote:0@?')
            unresolved.append('Ilima: the Pokemon he promoted is not told')
        known_prefix = None
        for si, s_ in enumerate(plan):
            if '?' in s_:
                known_prefix = si
                break
        if known_prefix is not None:
            plan = plan[:known_prefix]
        e_zone = b['owner'].get('energy_zone') or {}
        this = (e_zone.get('this_turn') or {})
        nxt = (e_zone.get('next') or {})
        # the Energy of this turn, and of the next one: the next one is what the zone shows after his turn (the "next" circle at a turn start can be this turn's)
        a_zone = ((t.get('board_after') or {}).get('owner') or {}).get('energy_zone') or {}
        my_now = zone_now(t)
        my_next = etype((a_zone.get('next') or {}).get('type')) or (zone_now(turns[owner_idx[k + 1]]) if k + 1 < len(owner_idx) else None) or (etype(nxt.get('type')) if etype(this.get('type')) else None)
        o_next = opp_energy_next(turns, ti)
        if o_next is None:
            o_next = decks_energy
            notes.append(f"the opponent's next Energy is not told by the ledger: his deck's Energy ({decks_energy}) is used")
        # the opponent's discard: the cards the ledger names (his Pokemon that left the board with what was under them, the Items and Supporters he played, ...)
        opp_disc = []
        for nm_, tx_, hp_ in ohist['cards']:
            cs_ = C.BYNAME.get(nm_) or []
            if any(C.is_pokemon(c) for c in cs_):
                cid_, alts_ = opp_pick(nm_, hp_, ([tx_] if tx_ else []) + opp_ev.get(nm_, []))
                if alts_:
                    opp_alts.append({'name': nm_, 'used': cid_, 'could_also_be': alts_, 'where': 'discard'})
                opp_disc.append(f'{nm_} {cid_}')
            elif cs_:
                opp_disc.append(f'{nm_} {cs_[0]["id"]}')
        if ohist['hidden']:
            notes.append(f'the opponent\'s discard also holds {ohist["hidden"]} card(s) whose identity the ledger says is not readable: not in the list, so the count is a lower bound')
        pid = f'KW-{short}-t{tn:02d}'
        me_side = {'hand': hand, 'discard': pdisc, 'discard_energy': list(disc_energy), 'board': me_board,
                   # the zone Energy is there every turn except the first player's first (the ledger's `available` flag is unreliable at the turn boundary)
                   'energy_now': None if (first_player and tn == 1) else (my_now or decks_energy),
                   'energy_next': my_next or decks_energy}
        opp_side = {'hand_count': opp_hand, 'discard': opp_disc, 'discard_energy': list(ohist['energy']), 'board': opp_board, 'energy_next': o_next}
        me_side['knockouts'] = knockouts
        if me_deck_empty:
            me_side['deck_count'] = 0      # the ledger says his deck is empty: the position runner checks this against the list minus what it shows
        if ohist['deck_empty']:
            opp_side['deck_count'] = 0
        if ohist['hidden']:
            opp_side['discard_hidden'] = ohist['hidden']
        pos = {
            'id': pid, 'game': 'kw-' + short, 'his_turn': k + 1, 'deck': 'KW' + short, 'turn_count': tn, 'points': [pts_me, pts_opp],
            'me': me_side,
            'opp': opp_side,
            'stadium': stadium, 'turn_effects': turn_fx, 'his_plan': plan, 'his_plan_ended': bool(ended), 'hand_source': 'codex', 'decision_maker': 'Dustin',
            'exact_list': False, 'milestones': [], 'unresolved': unresolved,
            'notes': ('; '.join(sorted(set(notes))) + '. ' if notes else '') + "The opponent's list is unknown (his hidden cards are filled from the pilot's own list); his discard is what the ledger names (Pokémon that left the board, Items and Supporters played, Energy paid or discarded), so cards the ledger does not show are missing from it.",
            'approximate': True, 'approximate_reason': "opponent's list unknown" + ('; part of his discard is hidden in the ledger' if ohist['hidden'] else ''), 'heldout': False, 'plan_truncated_at': known_prefix,
            'opp_ambiguous': opp_alts, 'usable': not spec.version_unverified,
            'usable_reason': None if not spec.version_unverified else f"DECK_USED says the deck list is not this game's version ({spec.status})",
        }
        positions.append(pos)
    return positions, skipped, deck_info


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def read_decks(gdirs):
    out = {}
    for g in gdirs:
        try:
            out[g] = load_json(os.path.join(g, 'DECK_USED.json'))
        except (OSError, ValueError):
            pass
    return out


def write_deck_file(path, info):
    lines = ['Energy: ' + ', '.join(info['energy'])]
    for c in info['cards']:
        lines.append(f"{c['count']} {c['name']} {c['id']}")
    open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')


def main():
    out, rep, gdirs = sys.argv[1], sys.argv[2], sys.argv[3:]
    gm = D.global_entity_map(read_decks(gdirs).values())
    allpos, allskip, decks = [], [], {}
    for g in gdirs:
        try:
            pos, skip, deck = convert_game(g, gm)
        except Exception as e:
            import traceback
            print('GAME FAILED', os.path.basename(g), repr(e), traceback.format_exc().splitlines()[-3:])
            allskip.append({'game': os.path.basename(g), 'turn': None, 'reason': f'game not converted: {e!r}'})
            continue
        short = os.path.basename(g.rstrip('/')).replace('_iOS', '')[2:]
        decks[short] = deck
        for p in pos:
            if p['unresolved']:
                allskip.append({'game': short, 'turn': p['turn_count'], 'reason': 'unresolved plan targets (plan kept)', 'detail': p['unresolved']})
            p.pop('unresolved', None)
        allpos += pos
        allskip += skip
        print(os.path.basename(g), 'positions', len(pos), 'skipped', len(skip), '| deck notes:', len(deck['notes']))
    json.dump(allpos, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'positions': len(allpos), 'left_out': [s for s in allskip if 'unresolved' not in s['reason']], 'plans_with_unresolved_targets': [s for s in allskip if 'unresolved' in s['reason']],
               'decks': {g: {'source': d['source'], 'energy': d['energy'], 'notes': d['notes'], 'version_unverified': d['version_unverified'], 'status': d['status']} for g, d in decks.items()}},
              open(rep, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    base = os.path.dirname(out)
    for short, deck in decks.items():
        write_deck_file(os.path.join(base, f'KW{short}.txt'), deck)
    print('total', len(allpos), 'positions;', sum(1 for s in allskip if 'unresolved' not in s['reason']), 'left out;', sum(1 for s in allskip if 'unresolved' in s['reason']), 'with unresolved targets')


if __name__ == '__main__':
    main()
