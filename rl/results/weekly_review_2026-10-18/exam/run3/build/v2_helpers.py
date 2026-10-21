"""Exam v2's builder helpers (PREREG_RUN3; copies of v1.6's ~/exam/build/mk.py and the chance-step rule of its repair/validate scripts, edited for
the new decks). v1.6's files are left as they are.

Changes from v1.6:
- deck keys and Energy come from run3/decks/DECKS.json (8 deck files from the filmed codes) and any deck Dustin confirms (EXTRA_DECKS), not a
  hand-written 3-deck map;
- a deck may have more than one Energy type (v2deck_9633a01781: Water, Lightning, Metal). For such a deck the position must give the Energy the
  game showed: P(..., ez_now='W', ez_next='L'); a one-type deck keeps v1.6's rule (now = next = its type);
- the chance-step rule lives here once (DRAW, cut), for every v2 build, repair and validation script, and it adds the v2 decks' chance actions:
  * Trainers: the v2 lists' draw / search / coin Trainers are Professor's Research, Poké Ball, Copycat and Lucky Ice Pop, all already in v1.6's
    tuple (the tuple is kept whole, so a confirmed list with Lisia, Sightseer or Quick-Grow Extract still cuts);
  * Abilities: Dustox B4 005's Variety Powder picks a Special Condition at random, so using it is a chance step (the frozen plan lister stops at
    any action whose engine forecast has more than one branch). Its label is 'Ability@<slot>' and names no card, so cut() follows the slots
    through the line (Place, Evolve, Retreat). If a slot move it can't follow comes before an 'Ability@' while a chance-Ability Pokemon could
    be in play, cut() raises Uncertain: that line is cut by hand and noted. The other v2 Abilities that are used (Dragonair's Dragon's Blessing)
    or trigger (Darkrai ex's Nightmare Aura, Team Rocket's Weezing ex's Boiler Smog) are fixed outcomes, not chance.
  The plan-list label check of the formal compare is the safety net: every accepted first segment must be one of the frozen lister's plans.
- game ids: a Drive recording "ScreenRecording_MM-DD-YYYY HH-MM-SS" (Chicago time) becomes game_id(start_utc) = 'YYYYMMDD_HHMMSS000_SR' from
  run3/window.json's UTC start (v1.6's iOS ids are 'YYYYMMDD_HHMMSSmmm_iOS', also UTC), so ids sort by time and say where they came from."""
import json, os, re

EXAM_V2 = os.path.expanduser('~/exam_v2')
DECKS_JSON = os.path.join(EXAM_V2, 'decks', 'DECKS.json')
EXTRA_DECKS = {}  # deck key -> 'Energy: ...' line, for a list matched under PREREG_RUN3 section 1's repository route (addendum 3, D1)

EN = {'G': 'Grass', 'W': 'Water', 'R': 'Fire', 'L': 'Lightning', 'P': 'Psychic', 'F': 'Fighting', 'D': 'Darkness', 'M': 'Metal', 'N': 'Dragon', 'C': 'Colorless'}
LETTER = {v: k for k, v in EN.items()}

# the chance-step rule (v1.6's DRAW tuple, unchanged, plus the Abilities below)
DRAW = ("Play:Professor's Research", 'Play:Poké Ball', 'Play:Copycat', 'Play:Lisia', 'Play:Sightseer', 'Play:Lucky Ice Pop', 'ChooseRandomEvolutionTarget', 'Play:Quick-Grow')
CUTD = DRAW[:7]  # Quick-Grow itself is not the cut: its ChooseRandomEvolutionTarget is
CHANCE_ABILITY = ('Dustox',)  # Variety Powder: a Special Condition chosen at random


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
    o = {"hand_count": opp["hand_count"], "discard": opp.get("disc", []), "discard_energy": energies(opp.get("dene", "")), "board": opp["board"],
         "energy_next": EN[opp.get("zone", 'C')] if opp.get("zone") else None, "knockouts": opp.get("ko", 0)}
    if o["energy_next"] is None: del o["energy_next"]
    pos = {"id": f"LAD-{game}-t{tc}", "game": game, "his_turn": his, "deck": deck, "turn_count": tc, "points": pts, "me": m, "opp": o,
           "stadium": stadium, "turn_effects": [], "hand_source": "review", "decision_maker": "Dustin", "kind": kind, "force": force,
           "approximate": bool(approx), "approximate_reason": approx, "opp_ambiguous": ambiguous or [], "notes": notes, "heldout": True, "usable": True}
    pos["_draws"] = draws or {}
    pos["_vpatch"] = vpatch
    return pos


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
    """The line up to and including its first chance step (v1.6's rule, plus a chance Ability by the slot it names); the whole line if none."""
    steps = chance_steps(line, position, CUTD, first_only=True)
    return line[:steps[0] + 1] if steps else list(line)


def chance_steps(line, position, labels=DRAW, first_only=False):
    """Indices of every chance step in the line: a label starting with one of `labels`, UseStadium while Mesagoza is the Stadium, or a chance
    Ability by the slot it names. validate's after-chance variant uses all of them (DRAW, with Quick-Grow); cut() uses the first (CUTD)."""
    stadium = position.get('stadium')
    mesa = 'Mesagoza' in json.dumps(stadium or '')
    board = [_base(b['card']) for b in position['me']['board']]
    followed = True
    out = []
    for i, l in enumerate(line):
        if l == 'Play:Mesagoza':
            mesa = True
        if l.startswith(labels) or (l == 'UseStadium' and mesa):
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
