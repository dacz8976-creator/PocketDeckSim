"""Opponent clocks for the setup tester (SPEC.md "Opponent clock").

A clock gives, for each opponent turn j = 1, 2, ..., how many of our Pokémon it knocks out: an int, or None where the
record cannot say (undecided). `timeline(deal, first)` returns the clock's reading for one deal: `ko(j)`, `complete_at`
(the opponent turn after which the recorded game is complete: its third point) and `game` (which recorded game
was drawn, for the bootstrap). Sampling is keyed by the deal alone, so every version meets the same clock.

Sources: C-his (his 12 Kingambit games, positions_all.json), C-bot (the 64 deck-01 rows of replay_b/games.jsonl),
C-fixed (set paces: fast, medium, slow).
"""
import json
import os
import sys

from st_rng import Stream

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'lib'))
import consistency as cl   # noqa: E402  (read_deck, resolve: card facts through lib/card.py's database)

HIS_DIR = os.path.join('rl', 'results', 'pause_games_new_2026-10-13')
HIS_POS = os.path.join(HIS_DIR, 'v2', 'positions_all.json')
HIS_META = os.path.join(HIS_DIR, 'v2', 'games_meta.json')
HIS_DECKS = os.path.join(HIS_DIR, 'decks')
BOT_GAMES = os.path.join('rl', 'results', 'kx3_on_rules2_2026-10', 'replay_b', 'games.jsonl')


def points_of(card):
    """3 for a Mega ex, 2 for an ex, 1 otherwise (SPEC_AMENDMENT_1 P4)."""
    return 3 if card.name.startswith('Mega ') and card.ex else 2 if card.ex else 1


def strongest_of(cards):
    """(HP, points) of the highest-HP Pokémon in `cards` (more points on a tie), or None."""
    best = [(c.hp, points_of(c)) for c in cards if c.kind == 'P']
    return max(best) if best else None


class Timeline:
    """One deal's clock. ko(j) is an int, None (undecided) or, past the record, None unless complete. `strongest` is
    the opponent's strongest Pokémon (HP, points) or None; opp_hand(t) is the recorded opponent hand at the start of
    our own turn t or None."""
    __slots__ = ('kos', 'complete_at', 'game', 'strongest', 'hands')

    def __init__(self, kos, complete_at, game, strongest=None, hands=None):
        self.kos, self.complete_at, self.game = kos, complete_at, game
        self.strongest, self.hands = strongest, hands or {}

    def opp_hand(self, t):
        return self.hands.get(t)

    def ko(self, j):
        if j <= len(self.kos):
            return self.kos[j - 1]
        if self.complete_at is not None and j == self.complete_at:
            return 1
        return 0 if self.complete_at is not None and j > self.complete_at else None


class Fixed:
    """C-fixed: set paces, no sampling. `kos` is a dict {opponent turn: knock-outs} or a function of j."""

    def __init__(self, name, kos, hp=None, pts=None, hand=None):
        self.name, self._kos = name, kos
        self.hp, self.pts, self.hand = hp, pts, hand
        self.games = [{'name': name}]

    @property
    def strongest(self):
        return (self.hp, self.pts) if self.hp is not None else None

    def opp_hand(self, t):
        return self.hand

    def ko(self, j):
        return self._kos(j) if callable(self._kos) else self._kos.get(j, 0)

    def timeline(self, deal, first):
        return self

    @property
    def game(self):
        return 0

    complete_at = None


# Each pace carries an assumed strongest opponent (SPEC_AMENDMENT_1): fast a 180-HP Mega ex (3 points, the Blade needs
# k=3), medium a 150-HP ex (2 points, k=3), slow a 220-HP Mega ex (3 points, k=4). 'ref190' (fast pace, a 190-HP Mega,
# k=4 without Red) is a reference row.
FIXED = {
    'fast': Fixed('C-fixed fast', lambda j: 1 if j >= 2 else 0, 180, 3),   # one knock-out each opponent turn from turn 2
    'medium': Fixed('C-fixed medium', lambda j: 1 if j >= 3 else 0, 150, 2),    # the same from turn 3
    'slow': Fixed('C-fixed slow', lambda j: 1 if j in (3, 5, 7) else 0, 220, 3),
    'ref190': Fixed('C-fixed reference: fast pace, 190-HP Mega ex', lambda j: 1 if j >= 2 else 0, 190, 3),
}


class Sampled:
    """A recorded clock: deal i draws one recorded game by a stream keyed by i alone."""

    def __init__(self, name, games, seat_matched=False):
        self.name, self.games, self.seat_matched = name, games, seat_matched

    def pick(self, deal, first):
        u = Stream(deal, 'clock').unit()
        ids = [i for i, g in enumerate(self.games) if not self.seat_matched or g['first'] == first] \
            or list(range(len(self.games)))
        return ids[int(u * len(ids))]

    def timeline(self, deal, first):
        gi = self.pick(deal, first)
        g = self.games[gi]
        return Timeline(g['ko'], g['complete_at'], gi, g.get('strongest'), g.get('hands'))


def k_at_own_turn(game, turn):
    """Our knock-outs counted at the start of own turn `turn`: opponent turns 1..turn-1 if we went first, 1..turn if
    second. None if a turn in between is undecided."""
    upto = turn - 1 if game['first'] else turn
    kos = game['ko'][:upto]
    if len(kos) < upto or any(x is None for x in kos):
        return None
    return sum(kos)


def _his_game(name, positions, outcome_complete, strongest=None, hands=None):
    positions = sorted(positions, key=lambda p: p['his_turn'])
    first = positions[0]['turn_count'] == 1
    s = 1 if first else 0                       # k at his turn t covers opponent turns 1..t-s
    kos = []
    prev_t, prev_k = None, 0
    if not first:                               # going second: opponent turn 1 comes before his turn 1
        pass
    known = []                                  # (his_turn, k)
    for p in positions:
        known.append((p['his_turn'], p['me']['knockouts']))
    # opponent turns up to the first known position
    t0, k0 = known[0]
    upto0 = t0 - s
    if upto0 >= 1:
        kos += [k0] + [0] * (upto0 - 1)         # nothing recorded earlier than his turn 1 (k0 = 0 in practice)
    for (ta, ka), (tb, kb) in zip(known, known[1:]):
        n = tb - ta
        r = kb - ka
        if n == 1:
            kos.append(r)
        elif r == 0:
            kos += [0] * n
        else:
            kos += [None] * n                   # a rise across a missing turn: undecided for those turns
    last = known[-1][0] - s
    complete_at = len(kos) + 1 if outcome_complete else None
    return {'name': name, 'first': first, 'ko': kos, 'complete_at': complete_at,
            'recorded_k': known, 'n_known': last, 'strongest': strongest, 'hands': hands or {}}


def load_his(root, seat_matched=False):
    with open(os.path.join(root, HIS_POS), encoding='utf-8') as f:
        pos = json.load(f)
    with open(os.path.join(root, HIS_META), encoding='utf-8') as f:
        meta = json.load(f)
    by = {}
    for p in pos:
        by.setdefault(p['deck'], []).append(p)
    games = []
    for deck, ps in sorted(by.items()):
        with open(os.path.join(root, HIS_DECKS, deck + '.txt'), encoding='utf-8') as f:
            txt = f.read()
        if 'B3a 043' not in txt:                # Kingambit games only (the two Haxorus lists are left out)
            continue
        title = meta[deck.lower().replace('kw', 'kw-')]['title'].lower() if deck.lower().replace('kw', 'kw-') in meta \
            else ''
        complete = 'loss' in title and 'concession' not in title
        seen = [cl.resolve(' '.join(b['card'].split()[-2:])) for p in ps for b in p['opp']['board']]
        hands = {p['his_turn']: p['opp']['hand_count'] for p in ps if p['opp'].get('hand_count') is not None}
        games.append(_his_game(deck, ps, complete, strongest_of([c for c in seen if c]), hands))
    return Sampled('C-his (seat-matched)' if seat_matched else 'C-his', games, seat_matched)


def own_turn(t, deck_first):
    return (t + 1) // 2 if deck_first else t // 2


def _bot_game(r, strongest=None):
    first = r['first'] == 'deck'
    log = r['log']
    last = r['turns'] // 2 if first else (r['turns'] + 1) // 2
    kos, cum = [], 0
    for j in range(1, last + 1):
        T = 2 * j if first else 2 * j - 1
        promotes = sum(1 for e in log if e['t'] <= T and e['a'].startswith('Promote') and e['act'] == '')
        nxt = next((e['p'][1] for e in log if e['t'] > T), r['points'][1])
        new = max(promotes, nxt, cum)
        kos.append(new - cum)
        cum = new
    complete = r['winner'] == 'opp'
    return {'name': r['key'], 'first': first, 'ko': kos, 'complete_at': last if complete else None,
            'recorded_k': [], 'strongest': strongest, 'strongest_flag': 'the panel list\'s biggest Pokémon (the '
            'logs do not show the opponent\'s HP)'}


def _bot_rows(root):
    with open(os.path.join(root, BOT_GAMES), encoding='utf-8') as f:
        return [json.loads(l) for l in f]


def load_bot(root):
    rows = _bot_rows(root)
    rows = [r for r in rows if r['deck'].startswith('01')]
    lists = {}
    for r in rows:
        if r['opp'] not in lists:
            _, cards = cl.read_deck(os.path.join(root, 'decks', 'screen', 'opponents', r['opp'] + '.txt'))
            lists[r['opp']] = strongest_of(cards)
    return Sampled('C-bot', [_bot_game(r, lists[r['opp']]) for r in rows])


def bot_first_blade_turns(root):
    """The own turn of each deck-01 game's first Overlord's Blade in the 64 games (None if it never used it)."""
    rows = _bot_rows(root)
    out = []
    for r in rows:
        if not r['deck'].startswith('01'):
            continue
        first = r['first'] == 'deck'
        t = next((e['t'] for e in r['log'] if e['a'].startswith("Attack:Overlord")), None)
        out.append(None if t is None else own_turn(t, first))
    return out
