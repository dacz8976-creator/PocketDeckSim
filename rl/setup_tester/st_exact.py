"""The setup tester's exact part (SPEC.md "Exact part"). No simulation, no randomness.

The deal (engine/src/deck.rs, `Deck::shuffle` with `initial_shuffle`, lines 129-153): the top 5 cards are the hand.
If none is a Basic, one random hand slot is swapped for a random Basic from the other 15, and those 15 are
reshuffled. No mulligan. After that the 15 cards left are in uniform order, so natural draws are hypergeometric.
"""
import itertools
from collections import Counter
from math import comb

HAND = 5
_CACHE = {}


def p0(b, n=20):
    """Chance the raw 5 cards hold no Basic, with b Basics in n cards."""
    return comb(n - b, HAND) / comb(n, HAND)


def in_hand_basic1(b, n=20):
    """A 1-copy Basic is in the final hand: 5/20 + P0/b."""
    return HAND / n + p0(b, n) / b


def in_hand_nonbasic1(b, n=20):
    """A 1-copy non-Basic is in the final hand: 5/20 - [C(19-b,4)/C(20,5)]/5."""
    return HAND / n - comb(n - 1 - b, HAND - 1) / comb(n, HAND) / HAND


def cards_seen(turn):
    """Cards seen by own turn N through natural draws: 5 + N in both seats (the first player draws on turn 1)."""
    return HAND + turn


def energy_by_turn(turn, first):
    """Energy attached by own turn N: N-1 going first (no Energy on the first player's first turn), N going second."""
    return turn - 1 if first else turn


def earliest_kingambit_attack(first, via):
    """Earliest own turn a Kingambit can attack: Rare Candy skips the Stage 1; Bisharp needs a turn of its own.
    Energy [DD] limits the first player to own turn 3 either way."""
    if via == 'candy':
        return 3 if first else 2
    if via == 'bisharp':
        return 3
    raise ValueError(via)


def _names(cards):
    return sorted({c.name for c in cards})


def hand_dist(cards):
    """The final opening hand's distribution, aggregated by how many cards of each name it holds:
    returns (names, [(probability, count-vector-in-hand)]). Exact: every 5-card subset of the 20, and for a
    hand without a Basic every (hand slot, Basic) swap."""
    key = tuple((c.id, c.name, c.is_basic) for c in cards)
    if key in _CACHE:
        return _CACHE[key]
    names = _names(cards)
    ix = {nm: i for i, nm in enumerate(names)}
    nm_of = [ix[c.name] for c in cards]
    basic = [c.is_basic for c in cards]
    basics = [i for i in range(len(cards)) if basic[i]]
    total = comb(len(cards), HAND)
    agg = Counter()
    for sub in itertools.combinations(range(len(cards)), HAND):
        if any(basic[i] for i in sub):
            v = [0] * len(names)
            for i in sub:
                v[nm_of[i]] += 1
            agg[tuple(v)] += 1.0 / total
        else:
            # swap one random hand slot for one random Basic of the other 15 (all Basics are among them)
            w = 1.0 / total / (HAND * len(basics))
            for s in sub:
                for j in basics:
                    v = [0] * len(names)
                    for i in sub:
                        if i != s:
                            v[nm_of[i]] += 1
                    v[nm_of[j]] += 1
                    agg[tuple(v)] += w
    out = (names, sorted(agg.items()))
    out = (names, [(p, v) for v, p in out[1]])
    _CACHE[key] = out
    return out


def seen_prob(cards, needs, n):
    """P(at least one copy of every name in `needs` is among the first n cards seen by natural draws)."""
    names, dist = hand_dist(cards)
    ix = {nm: i for i, nm in enumerate(names)}
    total = Counter(c.name for c in cards)
    d = n - HAND
    rest = len(cards) - HAND
    denom = comb(rest, d)
    need_ix = [ix[x] for x in needs]
    out = 0.0
    for p, v in dist:
        unmet = [i for i in need_ix if v[i] == 0]
        s = 0.0
        for r in range(len(unmet) + 1):
            for sub in itertools.combinations(unmet, r):
                cs = sum(total[names[i]] for i in sub)
                s += (-1) ** r * (comb(rest - cs, d) / denom if rest - cs >= d else 0.0)
        out += p * s
    return out


def in_hand(cards, name):
    """P(a card of this name is in the final opening hand)."""
    return seen_prob(cards, [name], HAND)


def basics_in_hand(cards):
    """P(the final hand holds exactly k Basics), k = 0..5 (k = 0 never happens)."""
    names, dist = hand_dist(cards)
    isb = {c.name for c in cards if c.is_basic}
    out = {k: 0.0 for k in range(HAND + 1)}
    for p, v in dist:
        out[sum(x for nm, x in zip(names, v) if nm in isb)] += p
    return out


opening_basics = basics_in_hand


def forced_active(cards):
    """For each Basic name: P(it is the only Basic name in the final hand), so it is the Active."""
    names, dist = hand_dist(cards)
    isb = {c.name for c in cards if c.is_basic}
    out = {nm: 0.0 for nm in names if nm in isb}
    for p, v in dist:
        held = [(nm, x) for nm, x in zip(names, v) if nm in isb and x]
        if len(held) == 1:
            out[held[0][0]] += p
    return out
