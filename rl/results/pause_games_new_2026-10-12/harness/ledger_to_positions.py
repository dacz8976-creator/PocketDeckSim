#!/usr/bin/env python3
"""Codex TURN_LEDGER.json (pause-games/turn-capture-v1) + DECK_USED.json -> constructed-board positions at the start of every owner turn
(harness schema, as blast_to_positions.py of the Oct 2 set), generic over the game: his card ids come from the game's own DECK_USED.json, the
opponent's from the engine database by name + printed HP (+ the attack title the ledger shows). The opponent's list is unknown, so the position
carries no "filler" key (his hidden cards are cycled from the pilot's own list, as for the Oct 2 Ladder Log games).
A turn is LEFT OUT (and counted, with the reason) when its hand is not fully named, a card cannot be mapped, or points are missing.
usage: ledger_to_positions.py OUT.json REPORT.json GAMEDIR [GAMEDIR ...]   (GAMEDIR = a Recording_QA game folder)"""
import json, os, re, sys, collections

DB = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/engine/database.json'


def nname(n):
    if n is None:
        return None
    n = str(n).strip().replace('Poke Ball', 'Poké Ball').replace('’', "'")
    n = re.sub(r'^Nidoran\s*(?:male|♂)$', 'Nidoran♂', n, flags=re.I)
    n = re.sub(r'^Nidoran\s*(?:female|♀)$', 'Nidoran♀', n, flags=re.I)
    return re.sub(r'\s*[\(\[].*[\)\]]$', '', n)


def load_db():
    db = json.load(open(DB, encoding='utf-8'))
    cards = db if isinstance(db, list) else db.get('cards', list(db.values()))
    out = []
    for c in cards:
        inner = c.get('Pokemon') or c.get('Trainer') or c.get('Energy') or c
        out.append(inner)
    return out


CARDS = load_db()
BYNAME = collections.defaultdict(list)
for c in CARDS:
    BYNAME[nname(c.get('name', ''))].append(c)


def cid(c):
    return f"{nname(c['name'])} {c['id']}"


def opp_card(name, hp_max, variant_text):
    """printing by name + printed HP; the attack title in the ledger's variant text breaks ties; the first listed printing otherwise"""
    if name not in BYNAME:
        key = re.sub(r'[^a-z0-9]', '', str(name).lower().replace('male', '♂') if 'nidoran' in str(name).lower() else str(name).lower())
        alt = [n for n in BYNAME if re.sub(r'[^a-z0-9]', '', n.lower()) == key]
        name = alt[0] if alt else name
    cand = [c for c in BYNAME.get(name, []) if 'hp' in c]
    if not cand:
        cand = BYNAME.get(name, [])
    by_hp = [c for c in cand if hp_max is not None and c.get('hp') == hp_max] or cand
    if len(by_hp) > 1 and variant_text:
        vt = str(variant_text).split(';')[0]
        t = [c for c in by_hp if any(vt.startswith(a.get('title', '~')) for a in c.get('attacks', []))]
        by_hp = t or by_hp
    return cid(by_hp[0]) if by_hp else None


ETYPES = ('Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal', 'Dragon', 'Colorless')


def etype(x):
    """a ledger energy type as the engine spells it, or None"""
    s = str(x or '').strip().capitalize()
    return s if s in ETYPES else None


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
    """the ledgers spell a play's kind many ways: one set of names"""
    k = str(kind or '').strip().lower().replace(' ', '_')
    if k in ('card_play', 'item', 'supporter', 'trainer', 'card_play_attempt'):
        return 'card_play'
    if k in ('energy_attachment', 'energy', 'attach_energy'):
        return 'energy_attachment'
    if k in ('bench', 'bench_basic', 'bench_pokemon'):
        return 'bench'
    if k in ('evolution', 'evolve'):
        return 'evolution'
    if k in ('tool', 'tool_attachment'):
        return 'tool'
    if k in ('stadium', 'item_evolution', 'retreat', 'attack'):
        return k
    if k in ('ability', 'stadium_ability', 'stadium_effect'):
        return 'ability'
    return 'other'


NUMW = {'one': 1, 'two': 2, 'three': 3, 'four': 4}


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


def instances(side):
    out = []
    act = side.get('active')
    if _real(act):
        out.append(act)
    bench = [p for p in (side.get('bench_in_position_order') or []) if _real(p)]
    bench.sort(key=lambda p: (bpos(p) if bpos(p) is not None else 99))
    return out + bench


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


def chain_from_db(name):
    """names below a Pokemon by the printed evolution line (no Rare Candy assumed)"""
    out, cur = [], name
    for _ in range(3):
        cs = [c for c in BYNAME.get(cur, []) if c.get('evolves_from')]
        if not cs:
            break
        cur = nname(cs[0]['evolves_from'])
        out.insert(0, cur)
    return out


def tokens_of(p):
    return {t for t in (p.get('instance_id'), p.get('physical_instance')) if t}


def resolve(items, text, name_hint=None):
    """index in the compact board list from a ledger target text ('owner Active', 'owner Bench 3', 'Seadra', 'Horsea Bench 1', 'Weezing ex Bench 3')"""
    if text is None:
        return None
    t = str(text).replace('’', "'")
    tl = t.lower()
    cand = list(range(len(items)))
    # an instance id the ledger gives its Pokemon ('A', 'B', 'W1' ...): the whole target text, or a short text containing it as a word
    hits = [i for i in cand for tok in items[i].get('ids', ()) if t.strip() == tok or (len(t) <= 8 and re.search(r'(?<![A-Za-z0-9])' + re.escape(tok) + r'(?![A-Za-z0-9])', t))]
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


def _card_entries(v):
    """a list of 20 slot entries, or of per-name entries whose counts add to 20 -> [(name, 'SET NNN' or None)]"""
    if not (isinstance(v, list) and v and all(isinstance(x, (dict, str)) for x in v)):
        return None
    out = []
    for x in v:
        if isinstance(x, str):
            out.append((nname(x), None))
        elif x.get('name'):
            var = x.get('variant')
            # a QR entity can carry two printings ('A2a 053 / A2a 080'): the first one
            alts = [a.strip() for a in str(var).split('/')] if isinstance(var, str) else []
            var = next((a for a in alts if re.fullmatch(r'[A-Za-z0-9\-]+ \d{3}', a)), None)
            out += [(nname(x['name']), var if var else None)] * (int(x['count']) if isinstance(x.get('count'), int) and 'position' not in x else 1)
        else:
            return None
    return out if len(out) == 20 else None


def load_deck(d):
    """the game's exact 20 cards: [(name, 'SET NNN' or None)] and the Energy line; None when no 20-card list is in the file"""
    cards, src = None, None
    cand = []
    for k, v in d.items():
        if isinstance(v, list) and ('card' in k.lower() or 'slot' in k.lower() or k.startswith('counts_by')):
            cand.append((k, v))
        elif isinstance(v, dict) and ('qr' in k.lower() or 'card' in k.lower()):
            for k2, v2 in v.items():
                if isinstance(v2, list) and ('card' in k2.lower() or 'slot' in k2.lower() or k2.startswith('counts_by')):
                    cand.append((k + '.' + k2, v2))
    cand.sort(key=lambda kv: (kv[0] != 'cards_in_log_order', kv[0] != 'counts_by_name_and_variant'))
    for k, v in cand:
        e = _card_entries(v)
        if e:
            cards, src = e, k
            break
    energy = None
    flat = dict(d)
    for k, v in d.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                flat[k + '.' + k2] = v2
    for k in ['energy_configuration_from_log'] + [k for k in flat if 'energy' in k.lower() and k != 'energy_configuration_from_log']:
        v = flat.get(k)
        if isinstance(v, str) and v.strip():
            energy = v.strip()
            break
        if isinstance(v, list) and v and all(isinstance(x, str) for x in v):
            energy = ', '.join(v)
            break
    return cards, energy, src


def printing_for(name):
    cs = [c for c in BYNAME.get(name, [])]
    return str(cs[0]['id']) if cs else None


def convert_game(gdir):
    gname = os.path.basename(gdir.rstrip('/'))
    short = gname.replace('_iOS', '')[2:]
    led = json.load(open(os.path.join(gdir, 'TURN_LEDGER.json'), encoding='utf-8'))
    deckj = json.load(open(os.path.join(gdir, 'DECK_USED.json'), encoding='utf-8'))
    dcards, denergy, dsrc = load_deck(deckj)
    if dcards is None:
        raise ValueError('no 20-card list in DECK_USED.json')
    lines_by = collections.Counter()
    notes_deck = []
    for n, v in dcards:
        if v is None:
            v = printing_for(n)
            if v is None:
                raise ValueError(f'card {n!r} not in the database')
            notes_deck.append(n)
        lines_by[(n, v)] += 1
    # one printing per name (the QR is semantic: two printings of a name are the same card to the engine's list), counts added up
    MINE, by_name = {}, collections.Counter()
    for (n, v), c in lines_by.items():
        MINE.setdefault(n, f'{n} {v}')
        by_name[n] += c
    # the ledger often names the exact printing of his own Pokemon ('A2a 053; Tackle20, HP60'): it beats a guessed or name-matched printing
    seen_ids = collections.defaultdict(collections.Counter)
    for t_ in led['turns']:
        if not str(t_.get('who_played', '')).startswith('owner'):
            continue
        for key_ in ('board_at_start', 'board_after'):
            for p_ in instances((t_.get(key_) or {}).get('owner') or {}):
                m_ = re.match(r'\s*([A-Za-z0-9\-]+ \d{3})\b', str(p_.get('variant') or ''))
                if m_:
                    seen_ids[nname(p_['name'])][m_.group(1)] += 1
    for n_, c_ in seen_ids.items():
        pid_ = c_.most_common(1)[0][0]
        if n_ in MINE and MINE[n_] != f'{n_} {pid_}' and any(cid(x_) == f'{n_} {pid_}' for x_ in BYNAME.get(n_, [])):
            notes_deck.append(f'{n_}: printing {MINE[n_][len(n_) + 1:]} -> {pid_} (named in the ledger)')
            MINE[n_] = f'{n_} {pid_}'
    deck = {'energy_configuration_from_log': denergy or 'Water',
            'counts_by_name_and_variant': [{'name': n, 'variant': MINE[n][len(n) + 1:], 'count': c} for n, c in by_name.items()],
            'source_key': dsrc, 'printing_guessed_for': sorted(set(notes_deck))}
    DECKCOUNT = {MINE[n]: c for n, c in by_name.items()}
    isbasic = {}
    for n in MINE:
        cs = [c for c in BYNAME.get(n, []) if 'hp' in c]
        isbasic[n] = bool(cs) and all(c.get('stage', 0) == 0 for c in cs)
    ispoke = {n: any('hp' in c for c in BYNAME.get(n, [])) for n in MINE}
    TRAINER_DISCARD = {n for n in MINE if not ispoke[n]}
    TOOLS = {n for n in TRAINER_DISCARD if any(('Tool' in str(c.get('trainer_card_type', ''))) for c in BYNAME.get(n, []))}
    STADIUMS = {n for n in TRAINER_DISCARD if any(('Stadium' in str(c.get('trainer_card_type', ''))) for c in BYNAME.get(n, []))}
    turns = led['turns']
    owner_idx = [i for i, t in enumerate(turns) if str(t.get('who_played', '')).startswith('owner')]
    first_player = turns[owner_idx[0]]['turn_number'] == 1
    decks_energy = (deck.get('energy_configuration_from_log') or 'Water').split(',')[0].strip()
    positions, skipped = [], []
    disc, disc_energy = [], []
    stad_owner_by_card = {}
    my_stad = None
    for k, ti in enumerate(owner_idx):
        t = turns[ti]
        tn = t['turn_number']
        notes = []
        b = t['board_at_start']
        own_inst, opp_inst = instances(b['owner']), instances(b['opponent'])
        if k > 0:
            pt = turns[owner_idx[k - 1]]
            for p in pt.get('plays_in_order') or []:
                card = nname(p.get('card_name'))
                returns = re.search(r'return\w*\b[^.;]*\bhand|back (?:to|into) (?:his |the )?hand', str(p.get('result') or ''), re.I) and re.search(r'heads', str(p.get('result') or ''), re.I)
                if nk(p.get('kind')) in ('card_play', 'item_evolution') and card in TRAINER_DISCARD and card not in TOOLS and card not in STADIUMS and not returns:
                    disc.append(MINE[card])
                if card in STADIUMS and card in MINE and nk(p.get('kind')) in ('stadium', 'card_play'):
                    stad_owner_by_card[card] = 0
                    my_stad = card
                if nk(p.get('kind')) == 'retreat':
                    for tt, n_ in retreat_pay(p):
                        disc_energy += [tt] * n_
            cur_st = b.get('stadium')
            cur_st = cur_st.get('name') if isinstance(cur_st, dict) else cur_st
            cur_name = nname(cur_st) if cur_st and str(cur_st).strip().lower() not in ('none', 'null', 'empty', 'no stadium') else None
            if my_stad and cur_name != my_stad:
                disc.append(MINE[my_stad])   # his Stadium was replaced by the opponent's
                my_stad = None
            after = instances(pt.get('board_after', {}).get('owner') or {})
            now_names = collections.Counter(nname(p['name']) for p in own_inst)
            # a Pokemon of his present after his previous turn and gone now was knocked out in between (matched by name and bench count)
            gone = collections.Counter(nname(p['name']) for p in after) - now_names
            for p in after:
                nm = nname(p['name'])
                if gone.get(nm, 0) > 0 and nm in MINE:
                    gone[nm] -= 1
                    st = stack_under(p)
                    if st is None:
                        st = chain_from_db(nm)
                    disc += [MINE[nm]] + [MINE[s] for s in st if s in MINE]
                    tool = p.get('tool')
                    if tool and str(tool).lower() not in ('none', 'null') and nname(tool) in MINE:
                        disc.append(MINE[nname(tool)])
                    for tt, n in ebt(p):
                        disc_energy += [tt] * int(n or 0)
                    notes.append(f'knocked out between turns: {nm}')
        # hand
        hs = t.get('hand_at_start') or {}
        raw = hs.get('cards_left_to_right') or []
        names = [nname(c.get('name') if isinstance(c, dict) else c) for c in raw]
        if not raw or any(n is None or n not in MINE for n in names) or (hs.get('count') is not None and hs['count'] != len(names)):
            skipped.append({'game': short, 'turn': tn, 'reason': f'hand not fully named or unmapped: {names} count={hs.get("count")}'})
            continue
        hand = [MINE[n] for n in names]
        hand_source = 'codex'
        # boards
        try:
            def mk(p, mine):
                name = nname(p['name'])
                c = MINE.get(name) if mine else opp_card(name, p.get('hp_max'), p.get('variant'))
                if c is None:
                    raise KeyError(f'no card id for {name} ({p.get("hp_max")})')
                d = {'card': c, 'hp': p['hp_now']}
                en = []
                for tt, n in ebt(p):
                    en += [tt] * int(n or 0)
                if en:
                    d['energy'] = en
                tool = p.get('tool')
                if tool and str(tool).lower() not in ('none', 'null'):
                    tn_ = nname(tool)
                    tid = MINE.get(tn_) if mine else (cid(BYNAME[tn_][0]) if BYNAME.get(tn_) else None)
                    if tid is None:
                        raise KeyError(f'unknown tool {tool}')
                    d['tools'] = [tid]
                under = stack_under(p)
                if under is None:
                    under = chain_from_db(name)
                    if under:
                        notes.append(f'{name} stack taken from the printed evolution line (the ledger gives none)')
                        d['_derived'] = True
                if under:
                    if mine:
                        d['behind'] = [MINE[u] for u in under]
                    else:
                        d['behind'] = [opp_card(u, None, None) for u in under]
                conds = p.get('special_conditions') or []
                if conds:
                    notes.append(f'{name} is {"/".join(map(str, conds))} (not represented: the harness has no condition field)')
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
            if sn in MINE and st_by != 'opponent':
                stadium = {'card': MINE[sn], 'owner': 0 if stad_owner_by_card.get(sn) == 0 else 1}
            else:
                cs = BYNAME.get(sn)
                if cs:
                    stadium = {'card': cid(cs[0]), 'owner': 1}
                else:
                    skipped.append({'game': short, 'turn': tn, 'reason': f'stadium {st} unmapped'})
                    continue
        # a card seen more often than the list holds comes from an evolution stack derived from the printed line (Rare Candy skipped a stage) or
        # from a discard guess: take it out there, with a note
        pdisc = list(disc)
        seen = collections.Counter(hand) + collections.Counter(pdisc)
        for pk_ in me_board:
            seen[pk_['card']] += 1
            for x in pk_.get('behind', []) + pk_.get('tools', []):
                seen[x] += 1
        if stadium and stadium['owner'] == 0:
            seen[stadium['card']] += 1
        for cardid, n_seen in list(seen.items()):
            over = n_seen - DECKCOUNT.get(cardid, 99)
            while over > 0:
                owner_pk = next((pk_ for pk_ in me_board if pk_.get('_derived') and cardid in pk_.get('behind', [])), None)
                if owner_pk is not None:
                    owner_pk['behind'].remove(cardid)
                    notes.append(f'{cardid.rsplit(" ", 2)[0]} left out of a derived evolution stack (the list holds too few: Rare Candy skipped it)')
                elif cardid in pdisc:
                    pdisc.remove(cardid)
                    notes.append(f'one {cardid.rsplit(" ", 2)[0]} taken out of the discard guess (the list holds too few)')
                else:
                    break
                over -= 1
        for pk_ in me_board + opp_board:
            pk_.pop('_derived', None)
        plan, unresolved = [], []
        items = [{'name': nname(p['name']), 'bench_position': bpos(p), 'ids': {x for x in (p.get('instance_id'), p.get('physical_instance')) if x}} for p in own_inst]
        for p in t.get('plays_in_order') or []:
            kind, card, res, tg = nk(p.get('kind')), nname(p.get('card_name')), str(p.get('result') or ''), p.get('target')
            if kind in ('card_play', 'bench') and card in MINE and ispoke[card] and isbasic[card]:
                plan.append(f'Place:{card}')
                mm = re.search(r'bench\s*(?:position\s*)?(\d)', str(tg).lower())
                bp = int(mm.group(1)) if mm else next((k2 for w, k2 in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)) if w in str(tg).lower()), None)
                items.append({'name': card, 'bench_position': bp})
            elif kind in ('card_play', 'item_evolution', 'stadium') and card == 'Rare Candy':
                # target text 'owner Active Horsea -> Kingdra ex': the evolution the engine prints for a Rare Candy play
                mm = re.search(r'(.*?)\s*->\s*(.+)$', str(tg or ''))
                plan.append('Play:Rare Candy')
                if mm and nname(mm.group(2)) in MINE:
                    i = resolve(items, mm.group(1))
                    plan.append(f'Evolve:{nname(mm.group(2))}@{i if i is not None else "?"}')
                    if i is None:
                        unresolved.append(f'Rare Candy target {tg!r}')
                    else:
                        items[i]['name'] = nname(mm.group(2))
                else:
                    # no '->' in the target: the target Pokemon, and the Stage 2 in hand whose printed line starts at it
                    i = resolve(items, tg) if tg else resolve(items, res)
                    s2 = []
                    if i is not None:
                        base = items[i]['name']
                        s2 = [n for n in dict.fromkeys(names) if n in MINE and ispoke.get(n) and chain_from_db(n)[:1] == [base]]
                        if len(s2) != 1:
                            s2 = [n for n in s2 if n in (res + ' ' + str(tg))] or s2
                    if i is not None and len(s2) == 1:
                        plan.append(f'Evolve:{s2[0]}@{i}')
                        items[i]['name'] = s2[0]
                    else:
                        plan.append('Evolve:?@?')
                        unresolved.append(f'Rare Candy target {tg!r}')
            elif kind == 'card_play' and card in MINE and ispoke[card]:
                # a Stage 1 / Stage 2 played from the hand: the evolution
                i = resolve(items, tg)
                plan.append(f'Evolve:{card}@{i if i is not None else "?"}')
                if i is None:
                    unresolved.append(f'evolution target {tg!r}')
                else:
                    items[i]['name'] = card
            elif kind in ('card_play', 'stadium') and card in MINE and card not in TOOLS:
                plan.append(f'Play:{card}')
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
            elif kind == 'energy_attachment':
                i = resolve(items, tg)
                plan.append(f'Attach:1{etype((p.get("energy") or {}).get("type")) or decks_energy}@{i if i is not None else "?"} zone')
                if i is None:
                    unresolved.append(f'attach target {tg!r}')
            elif kind == 'retreat':
                i = None
                for cand_text in (str(tg), res):
                    i2 = resolve(items, cand_text)
                    if i2 is not None and i2 != 0:
                        i = i2
                        break
                if i is None:
                    # a bench Pokemon named next to 'promoted' / 'becomes Active' / 'Active' in the result text
                    hits = [j for j in range(1, len(items)) if re.search(r'(?:promot\w*|becomes?|new)\s+(?:the\s+)?(?:Active\s+)?' + re.escape(items[j]['name']) + r'|' + re.escape(items[j]['name']) + r'\s+(?:is\s+)?(?:promoted|becomes Active|Active|to Active)', res + ' ' + str(tg), re.I)]
                    if len(hits) == 1:
                        i = hits[0]
                plan.append(f'Retreat:{i}' if i is not None else 'Retreat:?')
                if i is None:
                    unresolved.append(f'retreat target {tg!r} / {res!r}')
                else:
                    items[0], items[i] = items[i], items[0]
            elif kind == 'ability' and card in STADIUMS:
                plan.append('UseStadium')
            elif kind == 'ability':
                i = resolve(items, card)
                if i is None:
                    # card_name is the ability's title: the one Pokemon on his board that has it
                    users = [j for j, it in enumerate(items) if any(isinstance(c.get('ability'), dict) and nname(c['ability'].get('title')) == card for c in BYNAME.get(it['name'], []))]
                    if len(users) == 1:
                        i = users[0]
                # the comparison ignores which Pokemon used the ability (Ability labels are bare), so an unresolved user does not cut the plan
                plan.append(f'Ability:{res[:40]}@{i if i is not None else 0}')
            elif kind == 'attack':
                act = items[0]['name'] if items else None
                exact = [c for c in BYNAME.get(act, []) if act in MINE and cid(c) == MINE[act]] or BYNAME.get(act, [])
                titles = list(dict.fromkeys(a.get('title') for c in exact for a in c.get('attacks', []) if a.get('title')))
                named = str(p.get('card_name') or '').replace('’', "'")
                after = named.split(':', 1)[1].strip() if ':' in named else ''
                hit = [x for x in titles if x and (x.lower() == after.lower() or x.lower() in (res + ' ' + named).lower().replace('’', "'"))]
                plan.append(f'Attack:{hit[0] if hit else (titles[-1] if titles else act)}')
                if not hit:
                    notes.append(f'attack title of {act} not named in the ledger: the last printed attack is used')
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
        o_zone = b['opponent'].get('energy_zone') or {}
        o_next = etype((o_zone.get('next') or {}).get('type')) or etype((o_zone.get('this_turn') or {}).get('type')) or decks_energy
        pid = f'KW-{short}-t{tn:02d}'
        pos = {
            'id': pid, 'game': 'kw-' + short, 'his_turn': k + 1, 'deck': 'KW' + short, 'turn_count': tn, 'points': [pts_me, pts_opp],
            'me': {'hand': hand, 'discard': pdisc, 'discard_energy': list(disc_energy), 'board': me_board,
                   # the zone Energy is there every turn except the first player's first (the ledger's `available` flag is unreliable at the turn boundary)
                   'energy_now': None if (first_player and tn == 1) else (etype(this.get('type')) or next((re.match(r'Attach:1(\w+)@', s_).group(1) for s_ in plan if re.match(r'Attach:1(\w+)@\d+ zone', s_)), None) or decks_energy),
                   'energy_next': etype(nxt.get('type')) or decks_energy},
            'opp': {'hand_count': opp_hand, 'discard_n': 0, 'discard_energy': [], 'board': opp_board, 'energy_next': o_next},
            'stadium': stadium, 'turn_effects': [], 'his_plan': plan, 'hand_source': hand_source, 'decision_maker': 'Dustin',
            'exact_list': False, 'milestones': [], 'unresolved': unresolved,
            'notes': ('; '.join(sorted(set(notes))) + '. ' if notes else '') + "The opponent's list is unknown (his hidden cards are filled from the pilot's own list); his discard is not tracked (0); printings chosen by the HP shown.",
            'approximate': True, 'approximate_reason': "opponent's list unknown", 'heldout': False, 'plan_truncated_at': known_prefix,
        }
        positions.append(pos)
    return positions, skipped, deck


def main():
    out, rep, gdirs = sys.argv[1], sys.argv[2], sys.argv[3:]
    allpos, allskip, decks = [], [], {}
    for g in gdirs:
        try:
            pos, skip, deck = convert_game(g)
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
        print(os.path.basename(g), 'positions', len(pos), 'skipped', len(skip))
    json.dump(allpos, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump({'positions': len(allpos), 'left_out': [s for s in allskip if 'unresolved' not in s['reason']], 'plans_with_unresolved_targets': [s for s in allskip if 'unresolved' in s['reason']]},
              open(rep, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # deck files (pg_pos --deck KEY=file format: 'Energy: Water' then 'N Name SET NUM')
    base = os.path.dirname(out)
    for short, deck in decks.items():
        lines = [f"Energy: {deck.get('energy_configuration_from_log') or 'Water'}"]
        for c in deck['counts_by_name_and_variant']:
            lines.append(f"{c['count']} {nname(c['name'])} {c['variant']}")
        open(os.path.join(base, f'KW{short}.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('total', len(allpos), 'positions;', sum(1 for s in allskip if 'unresolved' not in s['reason']), 'left out;', sum(1 for s in allskip if 'unresolved' in s['reason']), 'with unresolved targets')


if __name__ == '__main__':
    main()
