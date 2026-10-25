"""Exam v2's builder helpers (PREREG_RUN3; copies of v1.6's ~/exam/build/mk.py and the chance-step rule of its repair/validate scripts, edited for
the new decks). v1.6's files are left as they are.

Changes from v1.6:
- deck keys and Energy come from run3/decks/DECKS.json (8 deck files from the filmed codes) and any deck Dustin confirms (EXTRA_DECKS), not a
  hand-written 3-deck map;
- a deck may have more than one Energy type (v2deck_9633a01781: Water, Lightning, Metal). For such a deck the position must give the Energy the
  game showed: P(..., ez_now='W', ez_next='L'); a one-type deck keeps v1.6's rule (now = next = its type);
- the chance-step rule lives here once (DRAW, cut), for every v2 build, repair and validation script, and it adds the v2 decks' chance actions:
  * Trainers: the v2 lists' draw / search / coin Trainers are Professor's Research, Poké Ball, Copycat and Lucky Ice Pop, all already in v1.6's
    tuple (the tuple is kept whole, so a confirmed list with Lisia, Sightseer or Quick-Grow Extract still cuts); Wallace (B3b 068, in the
    Mega Sharpedo list, Oct 22) works like Quick-Grow Extract in the frozen engine: playing it is not the chance, its
    ChooseRandomEvolutionTarget is (cut there, as v1.6 did for Quick-Grow), and the after-chance check removes both;
  * Abilities: Dustox B4 005's Variety Powder picks a Special Condition at random, so using it is a chance step (the frozen plan lister stops at
    any action whose engine forecast has more than one branch). Its label is 'Ability@<slot>' and names no card, so cut() follows the slots
    through the line (Place, Evolve, Retreat). If a slot move it can't follow comes before an 'Ability@' while a chance-Ability Pokemon could
    be in play, cut() raises Uncertain: that line is never cut by hand; its first segment is frozen-7's lister's (addendum 5, G1 and R1,
    from check_lister_v2.py). The other v2 Abilities that are used (Dragonair's Dragon's Blessing)
    or trigger (Darkrai ex's Nightmare Aura, Team Rocket's Weezing ex's Boiler Smog) are fixed outcomes, not chance.
  The plan-list label check of the formal compare is the safety net: every accepted first segment must be one of the frozen lister's plans.
- game ids: a Drive recording "ScreenRecording_MM-DD-YYYY HH-MM-SS" (Chicago time) becomes game_id(start_utc) = 'YYYYMMDD_HHMMSS000_SR' from
  run3/window.json's UTC start (v1.6's iOS ids are 'YYYYMMDD_HHMMSSmmm_iOS', also UTC), so ids sort by time and say where they came from.
- the candidate view (advisor finding F5, Oct 23; PREREG_RUN3 addendum 5): P() keeps build-only and answer fields on the built position
  (kind, force, _draws, _vpatch, notes, approximate_reason). The v2 assembly (not yet written) must write every exam position as
  candidate_view(built), and validate_v2.py re-checks each exam position against its build record before the freeze. candidate_view keeps
  CANDIDATE_FIELDS, drops ANSWER_FIELDS and refuses any other field; check_candidate() refuses an answer field at any
  depth or the text of his move or of the builder's notes anywhere in the view. v1.6's view kept `notes` and `approximate_reason`; v2's
  does not (`approximate` stays, as a flag).
- cut() follows frozen-7's plan lister (addendum 5, R1): it also ends the first segment at a play after which the opponent chooses
  (Sabrina) and at Team Rocket's Raticate ex's Thieving Incisors. The F2 lister check (../check_lister_v2.py) asserts the agreement on
  every accepted line before the freeze; on v1.6 it now passes all 67 lines (v1.6's own cut differed on 4 points).
- certified_by (addendum 5, F4): only 'dustin' or 'coordinator_decision_from_his_words' (check_certified_by)."""
import copy, json, os, re

EXAM_V2 = os.path.expanduser('~/exam_v2')
DECKS_JSON = os.path.join(EXAM_V2, 'decks', 'DECKS.json')
EXTRA_DECKS = {}  # deck key -> 'Energy: ...' line, for a list matched under PREREG_RUN3 section 1's repository route (addendum 3, D1)

EN = {'G': 'Grass', 'W': 'Water', 'R': 'Fire', 'L': 'Lightning', 'P': 'Psychic', 'F': 'Fighting', 'D': 'Darkness', 'M': 'Metal', 'N': 'Dragon', 'C': 'Colorless'}
LETTER = {v: k for k, v in EN.items()}

# the chance-step rule (v1.6's DRAW tuple, unchanged, plus the Abilities below)
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget', 'Play:Quick-Grow',
        'Play:Wallace', 'Play:Cabbie')
CUTD = DRAW[:7] + ('Play:Cabbie',)  # Quick-Grow and Wallace themselves are not the cut: their ChooseRandomEvolutionTarget is (the frozen engine's
                 # random_typed_evolution_outcomes: the player picks the visible target, then the evolution card is random)
# Cabbie (Oct 25 build): it searches his deck for a Stadium, a chance action under ADJUDICATION_RULES section 3 ("any other card whose effect
# draws, searches, flips a coin or picks at random"); pg_legal_v14 stops there whenever a Stadium is left in his deck
RANDOM_EVOLUTION_PLAYS = ('Play:Quick-Grow', 'Play:Wallace')
# Stadiums whose use (UseStadium) is a chance step while they are in play: Mesagoza's coin (v1.6), Fragrant Forest's random Basic [G]
# from the deck (Oct 23 lists; the frozen engine searches the deck, which the lister and pg_legal_v14 both stop at)
CHANCE_STADIUMS = ('Mesagoza', 'Fragrant Forest', 'Area Zero')  # Area Zero (Oct 25 build): its use shuffles and draws (pg_legal_v14 stops there)
# Lusamine (Oct 23 lists): playing it is deterministic; its AttachFromDiscard ("2 random Energy from your discard pile") branches in the
# frozen engine's forecast only when the discard holds 3+ Energy of 2+ types (forecast_attach_from_discard); chance_steps judges that
# from the position's discard at the start of the turn (a retreat earlier in the same line is not counted: the label check catches it)
# Dustox: Variety Powder, a Special Condition chosen at random. Team Rocket's Raticate ex (v1.6's 13-A list; in no v2 list today):
# Thieving Incisors moves a random Energy from the opponent's Active; frozen-7's lister stops at its use even when that Active holds one
# Energy (seen in the F2 check's trial on v1.6), so it is a chance step whenever used (addendum 5, R1).
CHANCE_ABILITY = ('Dustox', "Team Rocket's Raticate ex")
# Plays after which the OPPONENT chooses (Sabrina: "Your opponent chooses the new Active Pokemon"): frozen-7's plan lister ends the plan
# there ('opponent_choice'), so cut() ends the first segment there too (PREREG_RUN3 addendum 5, R1; found by the F2 lister check's trial on
# v1.6, where cut() had no such stop). It is not a chance step: chance_steps() leaves it out.
OPPONENT_CHOICE_PLAYS = ('Play:Sabrina',)


class Uncertain(Exception):
    pass


def energies(s):
    return [EN[c] for c in s] if s else []


def _deck_energy_lines():
    with open(DECKS_JSON, encoding='utf-8') as f:
        d = json.load(f)['decks']
    out = {k: v['energy'] for k, v in d.items()}
    out.update(EXTRA_DECKS)
    return out


def deck_energy(deck):
    """The deck's Energy types as letters, in the deck file's order (e.g. ['W', 'L', 'M'])."""
    line = _deck_energy_lines()[deck]
    return [LETTER[x.strip()] for x in line.split(':', 1)[1].split(',')]


def B(card, hp, e='', tool=None, cond=None, behind=None, new=False, effects=None):
    b = {"card": card, "hp": hp}
    if effects: b["effects"] = effects
    if e: b["energy"] = energies(e)
    if tool: b["tools"] = [tool] if isinstance(tool, str) else tool
    if cond: b["conditions"] = cond
    if behind: b["behind"] = behind
    return b


def P(game, tc, his, pts, me, opp, force, deck, kind, stadium=None, approx=None, ambiguous=None, notes="", gid=None, draws=None, vpatch=None,
      ez_now=None, ez_next=None):
    """me/opp: dict(hand=[..]|hand_count=n, disc=[..], dene='GG', board=[B..], ko=n, zone='G'); force: list of labels; draws: {force index: [cards drawn]}
    (for the verify variant only); ez_now / ez_next: the Energy the game showed, required for a deck with more than one Energy type."""
    types = deck_energy(deck)
    if len(types) == 1:
        if (ez_now or types[0]) != types[0] or (ez_next or types[0]) != types[0]:
            raise ValueError(f'{deck} has only {EN[types[0]]} Energy')
        now = nxt = types[0]
    else:
        if ez_now not in types or ez_next not in types:
            raise ValueError(f'{deck} has {", ".join(EN[t] for t in types)} Energy: give ez_now and ez_next as the game showed them (got {ez_now}, {ez_next})')
        now, nxt = ez_now, ez_next
    m = {"hand": me["hand"], "discard": me.get("disc", []), "discard_energy": energies(me.get("dene", "")), "board": me["board"],
         "energy_now": EN[now], "energy_next": EN[nxt], "knockouts": me.get("ko", 0)}
    if tc == 1:
        m["energy_now"] = None  # the first player gets no Energy on the game's first turn (Oct 25 build: the engine listed a zone attach there)
    # his move ends at his attack: frozen-7's plans end at the Attack, and what follows (a target, a pending fx attach, ApplyQueuedAttackDamage,
    # a new Active) is the engine's bookkeeping there (judge.py normalize_full / full_match); the build's notes keep what the review shows
    at = next((i for i, l in enumerate(force) if l.startswith('Attack:')), None)
    if at is not None:
        force = list(force[:at + 1])
    o = {"hand_count": opp["hand_count"], "discard": opp.get("disc", []), "discard_energy": energies(opp.get("dene", "")), "board": opp["board"],
         "energy_next": EN[opp.get("zone", 'C')] if opp.get("zone") else None, "knockouts": opp.get("ko", 0)}
    if o["energy_next"] is None: del o["energy_next"]
    pos = {"id": f"LAD-{game}-t{tc}", "game": game, "his_turn": his, "deck": deck, "turn_count": tc, "points": pts, "me": m, "opp": o,
           "stadium": stadium, "turn_effects": [], "hand_source": "review", "decision_maker": "Dustin", "kind": kind, "force": force,
           "approximate": bool(approx), "approximate_reason": approx, "opp_ambiguous": ambiguous or [], "notes": notes, "heldout": True, "usable": True}
    pos["_draws"] = draws or {}
    pos["_vpatch"] = vpatch
    return pos


# the fields of a built position (P) that a candidate may see, and the ones it may never see
CANDIDATE_FIELDS = ('id', 'game', 'his_turn', 'deck', 'turn_count', 'points', 'me', 'opp', 'stadium', 'turn_effects', 'hand_source',
                    'decision_maker', 'approximate', 'opp_ambiguous', 'heldout', 'usable')
ANSWER_FIELDS = ('kind', 'force', '_draws', '_vpatch', 'notes', 'approximate_reason')
# run 1's and run 2's prep_inputs.py refused these keys at input time, and the answer file's own field names are added; check_candidate refuses
# them at any depth
LEAK_KEYS = frozenset({'force', 'his_plan', 'his_plan_ended', 'answer', 'answer_kind', 'kind', 'milestones', 'build_notes'} | set(ANSWER_FIELDS)
                      | {'his_move', 'key_line', 'first_segment', 'acceptable', 'rejected_alternatives', 'pending_alternatives', 'why_his',
                         'recorded_move_acceptable', 'segment_scope', 'dustin_answer', 'ambiguous', 'references', 'lister_segments'})


class AnswerLeak(Exception):
    pass


# The position's free-text fields (coordinator-038, decision 6): game FACTS only, in the builder's words. They may not carry an
# evaluative or advisory word; card names are taken out first ("Team Rocket's Master Plan", "Safeguard" are names, not advice).
FREE_TEXT_FIELDS = ('opp_ambiguous', 'turn_effects', 'stadium')  # and every board Pokemon's 'effects'
BANNED_WORDS = ('should', 'better', 'best', 'mistake', 'misplay', 'threat', 'lethal', 'plan', 'intend', 'want', 'correct', 'wrong',
                'risky', 'safe', 'good', 'bad', 'optimal', 'ideal', 'blunder', 'must', 'needs to', 'ought')
_BANNED = re.compile(r'\b(?:' + '|'.join(re.escape(w) for w in BANNED_WORDS) + r')(?:s|d|ed|ing|ly|er|est|ned|ning)?\b', re.I)
_CARD_NAMES = None


def card_names():
    """Every card name, Ability name and attack name in the card database (longest first), to take out of a free text before the
    banned-word check ("Safeguard" is an Ability, "Team Rocket's Master Plan" a card)."""
    global _CARD_NAMES
    if _CARD_NAMES is None:
        here = os.path.dirname(os.path.abspath(__file__))
        for p in (os.path.join(here, *(['..'] * 6), 'lib', 'deckgym-database.json'), os.path.expanduser('~/pincand/lib/deckgym-database.json')):
            if os.path.exists(p):
                with open(p, encoding='utf-8') as f:
                    names = set()
                    for e in json.load(f):
                        v = next(iter(e.values()))
                        names.add(v['name'])
                        if v.get('ability'):
                            names.add(v['ability']['title'])
                        names.update(a['title'] for a in v.get('attacks') or [])
                    _CARD_NAMES = sorted((n for n in names if n), key=len, reverse=True)
                break
        else:
            raise FileNotFoundError('lib/deckgym-database.json not found: the free-text check needs the card names')
    return _CARD_NAMES


def free_text_problems(view):
    """[(field path, the banned word, the text)] for every evaluative or advisory word in the position's free-text fields."""
    texts = []
    for f in FREE_TEXT_FIELDS:
        texts += [(f, s) for s in _strings(view.get(f))]
    for side in ('me', 'opp'):
        for k, b in enumerate((view.get(side) or {}).get('board') or []):
            texts += [(f'{side}.board[{k}].effects', s) for s in _strings(b.get('effects') if isinstance(b, dict) else None)]
    out = []
    names = card_names()
    for path, s in texts:
        bare = s
        for n in names:
            if n in bare:
                bare = bare.replace(n, ' ')
        for m in _BANNED.finditer(bare):
            out.append((path, m.group(0), s))
    return out


def _key_paths(x, path=''):
    if isinstance(x, dict):
        for k, v in x.items():
            p = f'{path}.{k}' if path else k
            yield p, k
            yield from _key_paths(v, p)
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from _key_paths(v, f'{path}[{i}]')


def _strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from _strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _strings(v)


def check_candidate(view, built=None, allowed=CANDIDATE_FIELDS):
    """Raise AnswerLeak when the candidate view holds an answer key at any depth or a field outside `allowed`, or, given the built position,
    any of his move's labels or the builder's notes / approximate_reason text in any of its texts. The view is checked as it will be written
    (a JSON round trip, so a tuple counts as a list); a label with no ':', '@' or '#' (EndTurn, UseStadium) must equal a whole text to count."""
    view = json.loads(json.dumps(view, ensure_ascii=False))
    bad = sorted(p for p, k in _key_paths(view) if k in LEAK_KEYS)
    if bad:
        raise AnswerLeak(f'{view.get("id")}: answer fields in the candidate view: {bad}')
    extra = sorted(set(view) - set(allowed))
    if extra:
        raise AnswerLeak(f'{view.get("id")}: fields outside the allowed fields in the candidate view: {extra}')
    banned = free_text_problems(view)
    if banned:
        raise AnswerLeak(f'{view.get("id")}: evaluative or advisory words in the position\'s free-text facts: {banned[:5]}')
    if built is not None:
        texts = list(_strings(view))
        for label in built.get('force') or []:
            if not label:
                continue
            bare = not any(ch in label for ch in ':@#')
            if any((t == label) if bare else (label in t) for t in texts):
                raise AnswerLeak(f'{view.get("id")}: his move\'s label {label!r} appears in the candidate view')
        for field in ('notes', 'approximate_reason'):
            s = built.get(field)
            if isinstance(s, str) and s.strip() and any(s in t for t in texts):
                raise AnswerLeak(f'{view.get("id")}: the built position\'s {field} text appears in the candidate view')


# who may certify a rejected alternative or a pending one (advisor finding F4; PREREG_RUN3 addendum 5): Dustin himself, or the coordinator
# deciding from his recorded words. v1.6's `coordinator_interpretation` is not allowed in v2.
CERTIFIED_BY = ('dustin', 'coordinator_decision_from_his_words')


def check_certified_by(points):
    """points: {point id: answer dict}. Raise ValueError naming every rejected or pending alternative whose certified_by is not allowed."""
    bad = []
    for pid, a in points.items():
        for field in ('rejected_alternatives', 'pending_alternatives'):
            for k, alt in enumerate(a.get(field) or []):
                if 'certified_by' in alt and alt['certified_by'] not in CERTIFIED_BY:
                    bad.append(f"{pid} {field}[{k}]: {alt['certified_by']!r}")
                elif field == 'rejected_alternatives' and 'certified_by' not in alt:
                    bad.append(f'{pid} {field}[{k}]: no certified_by')
    if bad:
        raise ValueError(f'certified_by must be one of {CERTIFIED_BY}: {bad}')


def candidate_view(built):
    """What a candidate (the judge, km3, the plan lister) may see of a built position: CANDIDATE_FIELDS only. Refuses a field that is in
    neither CANDIDATE_FIELDS nor ANSWER_FIELDS (a new field must be classified before it can be built), then checks the view."""
    unknown = sorted(set(built) - set(CANDIDATE_FIELDS) - set(ANSWER_FIELDS))
    if unknown:
        raise AnswerLeak(f'{built.get("id")}: unclassified fields {unknown}: add each to CANDIDATE_FIELDS or ANSWER_FIELDS first')
    view = {k: copy.deepcopy(v) for k, v in built.items() if k in CANDIDATE_FIELDS}
    check_candidate(view, built)
    return view


def label_view(built):
    """What the labelling job sees of a built position (addendum 5, G5): the candidate view plus `his_move` (the built position's `force`, his
    recorded whole turn). Never the builder's `notes`, `approximate_reason` or `kind`: the builder (the laptop session) has seen run 2's
    per-point results."""
    view = candidate_view(built)
    out = dict(view, his_move=list(built.get('force') or []))
    for k in ('notes', 'approximate_reason', 'kind', '_draws', '_vpatch'):
        assert k not in out
    return out


def game_id(start_utc):
    """'2026-10-19T22:12:18Z' (run3/window.json) -> '20261019_221218000_SR'."""
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z', start_utc)
    if not m:
        raise ValueError(start_utc)
    return '{}{}{}_{}{}{}000_SR'.format(*m.groups())


def _base(card):
    """'Dustox B4 005' or 'Dustox' -> 'Dustox' (a Place/Evolve label names the card without its set)."""
    return re.sub(r'\s+(?:P-[AB]|[AB]\d[a-z]?)\s+\d{1,3}$', '', card)


def is_chance_ability(card):
    return _base(card) in CHANCE_ABILITY


def cut(line, position):
    """The line up to and including its first chance step (v1.6's rule, plus a chance Ability by the slot it names) or its first play after
    which the opponent chooses (addendum 5, R1), whichever comes first; the whole line if neither."""
    stop = next((i for i, l in enumerate(line) if l.startswith(OPPONENT_CHOICE_PLAYS)), None)
    head = list(line) if stop is None else list(line[:stop + 1])  # nothing after the opponent's choice is scanned (its slots need no following)
    steps = chance_steps(head, position, CUTD, first_only=True)
    return head[:steps[0] + 1] if steps else head


def tool_stop_agrees(line, seg, position, matched, tool_stopped_at_chance, unmatched, from_lister=False):
    """validate_v2's shipped check: does pg_legal's stop agree with the first segment `seg`? `seg` is cut(line), or, under R1, frozen-7's
    lister's segment recorded by the assembly (`from_lister`). `matched` actions were matched before the tool stopped (at a hidden draw or coin
    when `tool_stopped_at_chance`). The tool stops exactly at the segment's end, or the segment ends EARLIER, at an opponent's choice or a
    chance Ability the tool does not stop at (any earlier stop, for a lister segment), and the tool then stops at a later chance step of the
    same line with nothing unmatched. With no chance stop, the whole line (or all of it but a closing EndTurn) must match."""
    if not tool_stopped_at_chance:
        return matched == len(line) or (matched == len(line) - 1 and line[-1] == 'EndTurn')
    if matched == len(seg):
        return True
    if unmatched or not 0 < matched <= len(line):
        return False
    # pg_legal stops only at a hidden draw or coin, never at an Ability, so its stop is judged by its label alone (no slot following,
    # which could raise Uncertain): a draw / search / coin Trainer, a random evolution, or UseStadium on a chance Stadium
    stop = line[matched - 1]
    stadium_named = any(s in json.dumps(position.get('stadium') or '') for s in CHANCE_STADIUMS) or \
        any(l in tuple(f'Play:{s}' for s in CHANCE_STADIUMS) for l in line[:matched - 1])
    tool_stop_is_chance = stop.startswith(CUTD) or (stop == 'UseStadium' and stadium_named)
    if matched > len(seg):
        early = len(seg) < len(line) and (from_lister or seg[-1].startswith(OPPONENT_CHOICE_PLAYS) or seg[-1].startswith('Ability'))
        return early and tool_stop_is_chance
    # matched < len(seg): only a lister segment (R1) may run past the tool's stop, at a draw the lister does not count as a chance step;
    # the after-chance variant then checks the rest of the line
    return from_lister and tool_stop_is_chance


def tool_steps(steps, stopped):
    """(matched steps, unmatched steps) of a pg_legal_v14 legal line. At a random evolution the tool stops with 'hidden random choice (...)' and
    leaves the forced ChooseRandomEvolutionTarget unmatched although that step's own legal list holds it (bare, or with its arguments): that
    step IS the chance step, so it counts as matched (Oct 25 build; it was the only tool reading that blocked every Wallace line)."""
    matched = [s for s in steps if s.get('forced') is not None and s.get('matched') is not None]
    unmatched = [s for s in steps if s.get('forced') is not None and s.get('matched') is None]
    if stopped.startswith('hidden random choice') and len(unmatched) == 1 and unmatched[0] is steps[-1]:
        f, legal = unmatched[0]['forced'], unmatched[0].get('legal') or []
        if f.startswith('ChooseRandomEvolutionTarget') and any(l == f or l.startswith(f) or f.startswith(l) for l in legal
                                                                if l.startswith('ChooseRandomEvolutionTarget')):
            return matched + unmatched, []
    return matched, unmatched


def chance_steps(line, position, labels=DRAW, first_only=False):
    """Indices of every chance step in the line: a label starting with one of `labels`, UseStadium while Mesagoza is the Stadium, or a chance
    Ability by the slot it names. validate's after-chance variant uses all of them (DRAW, with Quick-Grow); cut() uses the first (CUTD)."""
    stadium = position.get('stadium')
    mesa = any(s in json.dumps(stadium or '') for s in CHANCE_STADIUMS)
    board = [_base(b['card']) for b in position['me']['board']]
    discard_energy = list(position['me'].get('discard_energy') or [])
    followed = True
    out = []
    for i, l in enumerate(line):
        if l in tuple(f'Play:{s}' for s in CHANCE_STADIUMS):
            mesa = True
        random_attach = l == 'AttachFromDiscard' and len(discard_energy) > 2 and len(set(discard_energy)) > 1
        if l.startswith(labels) or (l == 'UseStadium' and mesa) or random_attach:
            out.append(i)
            if first_only:
                return out
            continue
        if l == 'Ability' or l.startswith('Ability@'):
            m = re.fullmatch(r'Ability@(\d+)', l)
            idx = int(m.group(1)) if m else None
            if followed and idx is not None and idx < len(board):
                if is_chance_ability(board[idx]):
                    out.append(i)
                    if first_only:
                        return out
            elif any(is_chance_ability(c) for c in board) or not followed:
                raise Uncertain(f'{position.get("id")}: {l} at step {i}: the slot is not followed, and a chance-Ability Pokemon may be in play')
            continue
        if l.startswith('Place:'):
            board.append(_base(l[len('Place:'):]))
        elif l.startswith('Evolve:'):
            name, at = l[len('Evolve:'):].rsplit('@', 1)
            idx = int(at.split('{')[0])
            if idx < len(board):
                board[idx] = _base(name)
            else:
                followed = False
        elif l.startswith('Retreat:'):
            j = int(l.split(':', 1)[1].split('{')[0])
            if j < len(board):
                board[0], board[j] = board[j], board[0]
            else:
                followed = False
        elif l.startswith(('Promote', 'Play:Ilima', 'Play:Koga')) or 'Switch' in l:
            followed = False  # a move of his own Pokemon between slots that this follower does not model
    return out
