#!/usr/bin/env python3
"""Dustin's questions on exam v2 (PREREG_RUN3 addendum 5, G4): one entry per question of the assembled draft, for the coordinator's quiz.

  make_questions.py EXAM_V2_DIR [DRAFT_JSON [OUT_DIR]]

Writes ~/exam_v2/questions/QUESTIONS.json and QUESTIONS.md. Each entry holds:
  - the point id and its labelling part; the question, verbatim from the draft; the points a shared question also covers (also_applies_to);
  - where to watch each turn (video: the file, the turn's start in it from the review's own labels, the clip of a linked battle; video_refs.py);
  - his recorded move and each pending alternative, in plain words, step by step (slots followed through the line; a Pokemon with a twin in
    play is named with its HP or how it got there; a random evolution named from the build's record of the review), plus the raw labels;
  - the position: the turn and who went first, the points, both Energy zones, both Actives and Benches (HP, printed HP and the HP bonuses in
    play, Energy, Tools, conditions, cards underneath, lasting effects), his hand (Trainers tagged with their type), his discard, his deck count
    and the cards left in it, the opponent's hand count and visible discard, the Stadium, how many of each side's Pokemon were knocked out,
    and the build's approximations (the position is reconstructed from his game review).
Nothing about any bot, the judge, run 1 or run 2, or any other point's labels."""
import collections, copy, glob, importlib.util, json, os, re, sys

E2 = sys.argv[1] if len(sys.argv) > 1 else '/home/dacz8976/exam_v2'
DRAFT = sys.argv[2] if len(sys.argv) > 2 else f'{E2}/assembly/exam_v2_draft.json'
QDIR = sys.argv[3] if len(sys.argv) > 3 else f'{E2}/questions'  # another folder: a check run that leaves the live quiz file alone (note 048)
DB = {v['id']: v for e in json.load(open(f'{E2}/bin/frozen_db_b5e68fc8.json', encoding='utf-8')) for v in e.values()}
SET = re.compile(r'\s+((?:P-[AB]|[AB]\d[a-z]?)\s+\d{1,3})$')
HP_BONUS = re.compile(r'\+(\d+)\s*HP|(\d+)\s*more HP|gets \+(\d+) HP', re.I)


def name(card):
    return SET.sub('', card)


def card_of(card):
    m = SET.search(card)
    return DB.get(m.group(1)) if m else None


def hand_item(card):
    c = card_of(card)
    if c and 'hp' not in c:
        return f"{name(card)} ({c.get('trainer_card_type')})"
    return name(card)


def args_of(label):
    if '#' in label:
        try:
            return json.loads(label.split('#', 1)[1])
        except ValueError:
            return {}
    m = re.match(r'^[A-Za-z]+\{(.*)\}$', label)
    if m:
        out = {}
        for part in m.group(1).split(','):
            if ':' in part:
                k, v = part.split(':', 1)
                out[k.strip()] = int(v) if v.strip().lstrip('-').isdigit() else v.strip()
        return out
    return {}


def mon(b, stadium):
    c = card_of(b['card'])
    bonuses = []
    for t in b.get('tools') or []:
        tc = card_of(t)
        if tc and HP_BONUS.search(tc.get('effect') or ''):
            bonuses.append(f"{name(t)}: {tc.get('effect')}")
    if stadium and c and c.get('stage') == 0:
        sc = card_of(stadium['card'])
        if sc and HP_BONUS.search(sc.get('effect') or ''):
            bonuses.append(f"{name(stadium['card'])} (Stadium): {sc.get('effect')}")
    out = {'card': name(b['card']), 'printing': b['card'], 'hp_now': b.get('hp'), 'printed_hp': c.get('hp') if c else None,
           'hp_bonuses_in_play': bonuses, 'energy': b.get('energy') or [], 'tools': [name(t) for t in b.get('tools') or []],
           'conditions': b.get('conditions') or [], 'cards_underneath': [name(x) for x in b.get('behind') or []]}
    eff = []
    for e in b.get('effects') or []:
        x = e.get('effect')
        eff.append(x if isinstance(x, str) else ', '.join(f'{k} {v}' for k, v in (x or {}).items()))
    if eff:
        out['effects'] = eff
    return out


def random_evolutions(pos, built):
    """[(from name, to name)]: what the build's patch (vpatch, the review's result) evolved at a random evolution (Wallace, Quick-Grow)."""
    vp = (built or {}).get('_vpatch')
    if not vp:
        return []
    v = copy.deepcopy(pos)
    try:
        vp(v)
    except Exception:
        return []
    before = [name(b['card']) for b in pos['me']['board']]
    after = [name(b['card']) for b in v['me']['board']]
    out = []
    for b in v['me']['board']:
        n, c = name(b['card']), card_of(b['card'])
        if c and c.get('evolves_from') and before.count(n) < after.count(n) and (c['evolves_from'], n) not in out:
            out.append((c['evolves_from'], n))
    return out


ORDINAL = ('first', 'second', 'third', 'fourth')


class Board:
    """His side, slot by slot, with how each Pokemon got there this turn. A Pokemon with a same-name twin in play is always named with its
    place (the Active one, or on the Bench) and with what tells it apart from the twins in the same place: how it got there this turn
    ("evolved from Dratini this turn"), else "the older one" when each such twin got there this turn, else its HP when that differs (said
    as "at the start of the turn": a step earlier in the line can heal it, as Irida does), else its place on the Bench counted from the left
    (the build's Bench is compacted). The Active one needs no HP. coordinator-049: quiz Q10's "Dragonair (80 HP, on the Bench)" fitted both
    Dragonair, and "Dragonair (evolved from Dratini this turn)" did not say it was the one on the Bench."""
    def __init__(self, pos):
        self.slots = [{'name': name(b['card']), 'hp': b.get('hp'), 'how': None} for b in pos['me']['board']]

    def say(self, k):
        if not (isinstance(k, int) and 0 <= k < len(self.slots)):
            return f'the Pokémon in slot {k}'
        s = self.slots[k]
        twins = [j for j, x in enumerate(self.slots) if x['name'] == s['name'] and j != k]
        if not twins:
            return f"{'the Active ' if k == 0 else ''}{s['name']}"
        if k == 0:
            return f"the Active {s['name']}" + (f" ({s['how']})" if s['how'] else '')
        bench = [j for j in twins if j != 0]
        if not bench:
            return f"{s['name']} on the Bench" + (f" ({s['how']})" if s['how'] else '')
        if s['how'] and all(self.slots[j]['how'] != s['how'] for j in bench):
            tag = s['how']
        elif not s['how'] and all(self.slots[j]['how'] for j in bench):
            tag = 'the older one'
        elif s['hp'] and all(self.slots[j]['hp'] and self.slots[j]['hp'] != s['hp'] for j in bench):
            tag = f"{s['hp']} HP at the start of the turn"
        else:
            tag = f"{ORDINAL[min(k, 4) - 1]} from the left"
        return f"{s['name']} on the Bench ({tag})"


def plain(line, pos, evos=()):
    evos = list(evos)
    bd = Board(pos)
    stadium = name(pos['stadium']['card']) if pos.get('stadium') else None
    opp = [name(b['card']) for b in pos['opp']['board']]
    out = []
    for l in line:
        base, a = l.split('#', 1)[0].split('{')[0], args_of(l)
        if base.startswith('Place:'):
            n = base[len('Place:'):].split('@')[0]
            out.append(f'Bench {n} from your hand')
            bd.slots.append({'name': n, 'hp': None, 'how': 'the one just benched from the hand'})
        elif base.startswith('Evolve:'):
            n, at = base[len('Evolve:'):].rsplit('@', 1)
            k = int(re.match(r'\d+', at).group(0))
            out.append(f'Evolve {bd.say(k)} into {n}')
            if k < len(bd.slots):
                bd.slots[k] = {'name': n, 'hp': None, 'how': f"evolved from {bd.slots[k]['name']} this turn"}
        elif base.startswith('Attach:'):
            m = re.match(r'Attach:(\d+)(\w+)@(\d+)\s*(\w*)', base)
            out.append(f"Attach {m.group(2)} Energy{' from the Energy Zone' if m.group(4) == 'zone' else ''} to {bd.say(int(m.group(3)))}"
                       if m else f'[{l}]')
        elif base.startswith('Play:'):
            out.append(f"Play {base[len('Play:'):]}")
            pc = DB.get(next((c for c in DB if DB[c]['name'] == base[len('Play:'):] and DB[c].get('trainer_card_type') == 'Stadium'), ''), None)
            if pc:
                stadium = pc['name']
        elif base.startswith('Tool:'):
            t, at = base[len('Tool:'):].rsplit('@', 1)
            out.append(f'  (attach {t} to {bd.say(int(at))})')
        elif base.startswith('Retreat:'):
            k = int(re.match(r'\d+', base[len('Retreat:'):]).group(0))
            if k < len(bd.slots):
                out.append(f'Retreat {bd.say(0)}, bringing {bd.say(k)} into the Active Spot')
                bd.slots[0], bd.slots[k] = bd.slots[k], bd.slots[0]
            else:
                out.append(f'[{l}]')
        elif base.startswith('Attack:'):
            out.append(f"Attack with {bd.say(0)}: {base[len('Attack:'):]}")
        elif base.startswith('Ability'):
            m = re.match(r'Ability@(\d+)', base)
            k = int(m.group(1)) if m else 0
            nm = bd.slots[k]['name'] if k < len(bd.slots) else None
            c = next((card_of(b['card']) for b in pos['me']['board'] if name(b['card']) == nm), None)
            title = (c.get('ability') or {}).get('title') if c else None
            out.append(f"Use {bd.say(k)}'s Ability" + (f' ({title})' if title else ''))
        elif re.fullmatch(r'Activate:\d+@\d+', base):
            pl, k = (int(x) for x in base[len('Activate:'):].split('@'))  # Activate:<player>@<Bench slot> (v1.6 BUILD.md: 'Activate:1@1')
            if pl == 0 and k < len(bd.slots):
                out.append(f'  ({bd.say(k)} comes into the Active Spot, {bd.say(0)} goes to the Bench)')
                bd.slots[0], bd.slots[k] = bd.slots[k], bd.slots[0]
            elif pl == 1 and k < len(opp):
                out.append(f"  (the opponent's {opp[k]} comes into the Active Spot)")
                opp[0], opp[k] = opp[k], opp[0]
            else:
                out.append(f'[{l}]')
        elif base == 'EndTurn':
            out.append('End the turn')
        elif base == 'UseStadium':
            out.append(f"Use the Stadium{f' ({stadium})' if stadium else ''}")
        elif base == 'Noop':
            out.append('  (decline the optional effect)')
        elif base.startswith('ChooseRandomEvolutionTarget'):
            k = a.get('in_play_idx')
            names = [s['name'] for s in bd.slots]
            ev = next(((x, y) for x, y in evos if (isinstance(k, int) and k < len(names) and names[k] == x) or (k is None and x in names)), None)
            if ev:
                evos.remove(ev)
                j = k if isinstance(k, int) else names.index(ev[0])
                out.append(f'  (random evolution: {bd.say(j)} became {ev[1]})')
                bd.slots[j] = {'name': ev[1], 'hp': None, 'how': 'the one the random evolution just made'}
            else:
                out.append(f"  (choose {bd.say(k) if isinstance(k, int) else 'the Pokémon'} for the random evolution)")
        elif base.startswith('MistyTarget@'):
            out.append(f"  (Misty's target: {bd.say(int(base.split('@')[1]))})")
        elif base.startswith('AttachTypedFromDiscard:'):
            t, at = base[len('AttachTypedFromDiscard:'):].rsplit('@', 1)
            out.append(f'  (attach {t} Energy from the discard pile to {bd.say(int(at))})')
        elif base.startswith('AttachFromDiscard'):
            out.append('  (attach Energy from the discard pile)')
        elif base.startswith('DiscardToolFromPokemon'):
            pl, k, ti = a.get('player'), a.get('in_play_idx'), a.get('tool_idx', 0)
            side = pos['opp']['board'] if pl == 1 else pos['me']['board']
            try:
                tool = name(side[k]['tools'][ti])
                who = (f"the opponent's {'Active ' if k == 0 else ''}{opp[k]}" if pl == 1 else bd.say(k))
                out.append(f'  (discard {tool} from {who})')
            except (IndexError, KeyError, TypeError):
                out.append('  (discard a Tool)')
        elif base == 'DiscardActiveStadium':
            out.append('  (discard the Stadium in play)')
        elif base.startswith('ReturnPokemonToHand'):
            out.append(f"  (return {bd.say(a.get('in_play_idx'))} to the hand)")
        else:
            out.append(f'[{l}]')
    return out


def deck_left(pos):
    path = f"{E2}/decks/{pos['deck']}.txt"
    deck = collections.Counter()
    for line in open(path, encoding='utf-8'):
        if line[:1].isdigit():
            n, card = line.split(None, 1)
            deck[card.strip()] += int(n)
    seen = collections.Counter(pos['me']['hand'] + (pos['me'].get('discard') or []))
    for b in pos['me']['board']:
        seen[b['card']] += 1
        for x in (b.get('behind') or []) + (b.get('tools') or []):
            seen[x] += 1
    if pos.get('stadium') and pos['stadium'].get('owner') == 0:
        seen[pos['stadium']['card']] += 1
    left = deck - seen
    return sum(left.values()), sorted(f'{n} {name(c)}' for c, n in left.items())


def position(p, built):
    pos = p['position']
    tc, his = pos['turn_count'], pos['his_turn']
    me, op = pos['me'], pos['opp']
    n_left, left = deck_left(pos)
    return {
        'turn': tc, 'his_turn': his, 'went_first': 'Dustin' if tc == 2 * his - 1 else 'the opponent',
        'points': {'dustin': pos['points'][0], 'opponent': pos['points'][1]},
        'energy_zone': {'dustin_this_turn': me.get('energy_now'), 'dustin_next_turn': me.get('energy_next'),
                        'opponent_next_turn': op.get('energy_next')},
        'dustin': {'active': mon(me['board'][0], pos.get('stadium')), 'bench': [mon(b, pos.get('stadium')) for b in me['board'][1:]],
                   'hand': [hand_item(c) for c in me['hand']], 'discard': [name(c) for c in me.get('discard') or []],
                   'discarded_energy': me.get('discard_energy') or [], 'deck_count': n_left, 'cards_left_in_deck': left,
                   'his_pokemon_knocked_out_so_far': me.get('knockouts', 0)},
        'opponent': {'active': mon(op['board'][0], pos.get('stadium')), 'bench': [mon(b, pos.get('stadium')) for b in op['board'][1:]],
                     'hand_count': op['hand_count'], 'discard_seen': [name(c) for c in op.get('discard') or []],
                     'discarded_energy': op.get('discard_energy') or [], 'opponent_pokemon_knocked_out_so_far': op.get('knockouts', 0)},
        'stadium': ({'card': name(pos['stadium']['card']), 'owner': 'Dustin' if pos['stadium'].get('owner') == 0 else 'the opponent'}
                    if pos.get('stadium') else None),
        'note': 'Reconstructed from your game review, as it stood at the start of this turn; a few details (for example the opponent\'s '
                'hand size or a card\'s exact printing) may be estimates.',
    }  # the builder's approximation and uncertain-reading texts are left out: they can cite later turns (note 045: no hindsight)


ANSWER_OPTIONS = ['The alternative was better (my play was a mistake)', 'Both were fine', 'My play was better', 'Not sure']
MAPPING = {
    'The alternative was better (my play was a mistake)':
        "The alternative becomes the key (key_line); recorded_move_acceptable is false; his recorded move becomes a rejected alternative with his "
        "words (rejected_because) and certified_by 'dustin'. This is v1.6's precedent (LAD-20261016_031512000_iOS-t2, 'Not attacking was a mistake').",
    'Both were fine':
        "The alternative is accepted (acceptable), with his words and certified_by 'dustin'; his recorded move stays the key.",
    'My play was better':
        "The alternative becomes a rejected alternative with his words (rejected_because) and certified_by 'dustin', and never counts; his recorded "
        "move stays the key. This is v1.6's precedent (e.g. LAD-20261014_161324000_iOS-t5).",
    'Not sure':
        "The alternative is left out: it is not accepted and never counts (it is recorded with his answer); his recorded move stays the key.",
    'his note': "His optional note (his thinking in the moment) is stored verbatim with the point (dustin_answer.words), whatever option he picks.",
    'a shared question': "One answer applies to each point the question covers (also_applies_to), each to its own pending line.",
    'no answer': "A question not answered by the freeze leaves its point pending and unscored (PREREG_RUN3 addendum 5, G10).",
}


def video(pid):
    """Where to watch the turn: the recording as Dustin knows it (its name in his review index), the time the turn starts in that file from the
    review's own turn labels (null if the review gives none), and the clip of a linked battle (null for a one-recording game)."""
    import video_refs
    v, in_index, _, _ = video_refs.ref(pid)
    if not in_index:
        raise SystemExit(f'{pid}: {v["file"]} is not in the review index')
    return v


def lines_of(p, built):
    a, pos = p['answer'], p['position']
    evos = random_evolutions(pos, built)
    return ({'steps': plain(a['his_move'], pos, evos), 'labels': a['his_move']},
            [{'steps': plain(x['line'], pos, evos), 'labels': x['line']} for x in a['pending_alternatives']])


def main():
    d = json.load(open(DRAFT, encoding='utf-8'))
    sys.path.insert(0, f'{E2}/build')
    built = {}
    for fn in sorted(glob.glob(f'{E2}/build/g/g*.py')):
        sp = importlib.util.spec_from_file_location('g', fn); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        for q in m.POS:
            built[q['id']] = q
    pts = {p['id']: p for p in d['points']}
    qs = []
    for p in d['points']:
        a = p['answer']
        if not a.get('ambiguous') or a.get('same_question_as') or a.get('status') != 'pending':
            continue
        his, alts = lines_of(p, built.get(p['id']))
        also = []
        for q in d['points']:
            if q['answer'].get('same_question_as') == p['id']:
                h2, a2 = lines_of(q, built.get(q['id']))
                also.append({'point_id': q['id'], 'video': video(q['id']), 'his_move': h2, 'alternatives': a2,
                             'position': position(q, built.get(q['id']))})
        qs.append({'point_id': p['id'], 'part': a['part'], 'question': a['ambiguous'], 'video': video(p['id']), 'his_move': his, 'alternatives': alts,
                   'position': position(p, built.get(p['id'])), **({'also_applies_to': also} if also else {})})
    os.makedirs(QDIR, exist_ok=True)
    with open(f'{QDIR}/QUESTIONS.json', 'w', encoding='utf-8') as f:
        json.dump({'what': "Questions for Dustin about his own ranked turns: for each, his move and the other line asked about, with the position "
                   'as reconstructed from his game review at the start of that turn. His answers are recorded in his own words.',
                   'answer_options': ANSWER_OPTIONS, 'optional_note': 'Your thinking in the moment (optional)',
                   'mapping_for_the_record': MAPPING, 'n': len(qs), 'questions': qs},
                  f, indent=1, ensure_ascii=False)
    md = ['# Questions for Dustin', '']

    def side(s):
        def one(x):
            t = f"{x['card']} {x['hp_now']} HP" + (f" (printed {x['printed_hp']})" if x['printed_hp'] != x['hp_now'] else '')
            t += f", Energy {''.join(e[0] for e in x['energy']) or 'none'}"
            for k in ('tools', 'conditions', 'effects'):
                if x.get(k):
                    t += f", {k} {', '.join(x[k])}"
            return t
        return f"Active {one(s['active'])}; Bench: {'; '.join(one(b) for b in s['bench']) or 'none'}"

    def block(qid, pz, his, alts):
        out = [f"Turn {pz['turn']} (his turn {pz['his_turn']}; {pz['went_first']} went first). Points: Dustin {pz['points']['dustin']}, "
               f"opponent {pz['points']['opponent']}. Stadium: {pz['stadium']['card'] + ' (' + pz['stadium']['owner'] + ')' if pz['stadium'] else 'none'}.",
               '', f"- **Dustin:** {side(pz['dustin'])}", f"- **His hand:** {', '.join(pz['dustin']['hand'])} (deck: {pz['dustin']['deck_count']} cards)",
               f"- **Opponent:** {side(pz['opponent'])}; hand {pz['opponent']['hand_count']} cards", '',
               '**His move:** ' + '; '.join(s.strip() for s in his['steps'])]
        out += [f'**Alternative {j}:** ' + '; '.join(s.strip() for s in alt['steps']) for j, alt in enumerate(alts, 1)]
        return out

    def watch(v):
        return (f"**Video:** {v['file']}" + (f", clip {v['clip']}" if v['clip'] else '') +
                (f", from {v['at']}" if v['at'] else ' (the review gives no time for this turn)'))

    for i, q in enumerate(qs, 1):
        md += [f"## {i}. {q['point_id']} (part {q['part']})", '', f"**Question:** {q['question']}", '', watch(q['video']), '']
        md += block(q['point_id'], q['position'], q['his_move'], q['alternatives']) + ['']
        for x in q.get('also_applies_to') or []:
            md += [f"**The same question at {x['point_id']}:**", '', watch(x['video']), ''] + block(x['point_id'], x['position'], x['his_move'], x['alternatives']) + ['']
    with open(f'{QDIR}/QUESTIONS.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')
    unknown = sum(1 for q in qs for s in [*q['his_move']['steps'], *[x for a in q['alternatives'] for x in a['steps']]] if s.startswith('['))
    print(f"{len(qs)} questions ({sum(len(q.get('also_applies_to') or []) for q in qs)} shared points); steps not in plain words: {unknown}")


if __name__ == '__main__':
    main()
