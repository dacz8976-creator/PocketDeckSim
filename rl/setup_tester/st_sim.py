"""The setup tester's simulation part (SPEC.md "Simulation part"): our own cards under a fixed, written-down script,
on shared deals. It is not a bot pilot: it plays fixed priorities, looks no turns ahead and never sees the opponent's
board. Card facts come from lib/card.py through lib/consistency.py's database (`cl.db()`).

Engine rules followed, with the engine file and line each comes from (main 70319c3d; engine unchanged since c045ede):
  * the deal: top 5 cards are the hand; no Basic -> one random hand slot swapped for a random Basic of the other 15,
    the 15 reshuffled (deck.rs:129-153)
  * hand limit 10, extra draws skipped and the card stays in the deck (state/mod.rs:811-815 `maybe_draw_card`;
    actions/shared_mutations.rs:173-186 for searches: only as many cards as fit are taken)
  * empty deck, no draw (state/mod.rs:811, `draw` in deck.rs:120)
  * Bench of 3 (Active + 3 Bench: at most 4 Pokémon in play)
  * one Supporter per turn (state/mod.rs:321 `has_played_support`, reset at state/mod.rs:952); allowed on the first
    player's turn 1 (move_generation/move_generation_trainer.rs:52 only blocks the setup phase, turn_count 0)
  * one Stadium per turn (move_generation/move_generation_trainer.rs:403-406, state/mod.rs:326)
  * no evolution on your own first turn (state/mod.rs:1232-1234 `is_users_first_turn`, turn_count <= 2;
    move_generation/mod.rs:210) or on a Pokémon placed this turn (`played_this_turn`, move_generation/mod.rs:210)
  * Rare Candy: not on your own first turn (move_generation_trainer.rs:670); a Stage 2 in hand and a Basic in play not
    placed this turn, matched by the card_logic/rare_candy.rs:94-106 (Basic name, Stage 2 name) table, so any
    Pawniard can become Kingambit with no Bisharp in the deck
  * searches pick uniformly (shared_mutations.rs:165-168: one equally likely branch per combination)
Not yet checked in Pocket (flag the measures they touch): Poké Ball over cards or over names (open question #24;
`poke_ball_over`), Sightseer's missing hand-limit check (it adds Stage 1 cards without checking the cap), Pokémon
Communication's draw order (it swaps with a uniformly random Pokémon of the deck).
"""
import json
import os
import sys

from st_rng import Stream

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), 'lib'))
import consistency as cl   # noqa: E402  (read_deck, classify, opening_exact; db() for card facts)

SEED_BASE = 24_700_000_000
DEFAULT_PLAN = os.path.join(HERE, 'plans', 'kingambit.json')
HAND_LIMIT = 10
BENCH = 3

KIND = {'Poké Ball': 'pokeball', 'Rare Candy': 'candy', 'Pokémon Communication': 'comm', 'Juliana': 'juliana',
        'Lisia': 'lisia', 'Sightseer': 'sightseer', "Professor's Research": 'prof', 'Copycat': 'copycat',
        'Ilima': 'ilima', 'Mesagoza': 'stadium'}


def load_cfg(path=None, **over):
    with open(path or DEFAULT_PLAN, encoding='utf-8') as f:
        cfg = json.load(f)
    cfg.update(over)
    if 'attacker_cost' not in cfg:       # the main attack's Energy cost, from lib/card.py's database
        atk = next(a for a in cl.db()['name'][cfg['main_attacker']].attacks if a['title'] == cfg['attack'])
        cfg['attacker_cost'] = len(atk['cost'])
    return cfg


def blade_damage(k):
    """Overlord's Blade: 60 + 40 per knock-out so far (lib/card.py: 'B3a 043')."""
    return 60 + 40 * k


class Version:
    """One list. `cards` are cl.Card objects; they take the base's 20 slots (same id first, then same name, then the
    rest in sorted order), so a one-card change alters one slot in every deal (SPEC "Pairing")."""

    def __init__(self, cards, base_cards, label='v'):
        self.label = label
        n = len(base_cards)
        slots = [None] * n
        free = list(range(n))
        rest = []
        for c in cards:                                   # same id first
            hit = next((s for s in free if base_cards[s].id == c.id), None)
            if hit is None:
                rest.append(c)
            else:
                slots[hit] = c
                free.remove(hit)
        rest2 = []
        for c in rest:                                    # then same name
            hit = next((s for s in free if base_cards[s].name == c.name), None)
            if hit is None:
                rest2.append(c)
            else:
                slots[hit] = c
                free.remove(hit)
        for c, s in zip(sorted(rest2, key=lambda c: (c.id, c.name)), free):   # then the rest, sorted
            slots[s] = c
        self.cards = slots
        self.n = n
        self.name = [c.name for c in slots]
        self.id = [c.id for c in slots]
        self.stage = [c.stage if c.kind == 'P' else -1 for c in slots]
        self.is_basic = [c.is_basic for c in slots]
        self.is_pokemon = [c.kind == 'P' for c in slots]
        self.hp = [c.hp for c in slots]
        self.frm = [c.frm for c in slots]
        self.tkind = [KIND.get(c.name, 'other') if c.kind == 'T' else None for c in slots]
        self.root = [cl.line_of(c.name)[0] if c.kind == 'P' else None for c in slots]


def order_for(ver, top_ids):
    """A deck order (slot indices, top card first) whose first cards are the given card ids, the rest in slot order.
    Used by the hand-checked tests."""
    used, out = set(), []
    for cid in top_ids:
        s = next(i for i in range(ver.n) if ver.id[i] == cid and i not in used)
        used.add(s)
        out.append(s)
    return out + [i for i in range(ver.n) if i not in used]


def opening(ver, deal, order=None, seed_base=SEED_BASE, reshuffle=True):
    """The deal (deck.rs:129-153). Returns (hand slots, rest of the deck, top card first)."""
    seed = seed_base + deal
    perm = list(order) if order is not None else list(range(ver.n))
    if order is None:
        Stream(seed, 'shuffle').shuffle(perm)
    if not any(ver.is_basic[s] for s in perm[:5]):
        bidx = [j for j in range(5, ver.n) if ver.is_basic[perm[j]]]
        sw = Stream(seed, 'swap')
        b = bidx[sw.below(len(bidx))]
        h = sw.below(5)
        perm[h], perm[b] = perm[b], perm[h]
        rest = perm[5:]
        Stream(seed, 'reshuffle').shuffle(rest)
        perm[5:] = rest
    return perm[:5], perm[5:]


def deal_cards(ver, deal, order=None, seed_base=SEED_BASE):
    return opening(ver, deal, order, seed_base)


class Mon:
    __slots__ = ('slot', 'name', 'stage', 'placed', 'evolved', 'energy', 'root', 'hp')

    def __init__(self, ver, slot, turn):
        self.slot, self.name, self.stage = slot, ver.name[slot], ver.stage[slot]
        self.placed, self.evolved, self.energy = turn, -1, 0
        self.root, self.hp = ver.root[slot], ver.hp[slot]


class Game:
    def __init__(self, ver, deal, first, cfg, order=None, seed_base=SEED_BASE):
        self.ver, self.cfg, self.first, self.deal = ver, cfg, first, deal
        self.seed = seed_base + deal
        self.streams = {}
        hand, rest = opening(ver, deal, order, seed_base)
        self.hand = list(hand)
        self.deck = rest[::-1]                    # the end of the list is the top card
        self.play = []                            # [Active, Bench...]
        self.discard = []
        self.stadium = None
        self.t = 0
        self.ko = 0
        self.opp_points = 0
        self.ended = None
        self.und_j = None                         # first opponent turn the clock could not read
        self.seen = list(hand)
        self.turns = []
        self.blades = []
        self.copycat_draws = []
        self.pawniard_lost_j = None
        self.first_attack_turn = None
        self.hold = {tuple(x) for x in cfg['hold_evolutions']}
        self.cost = cfg['attacker_cost']
        self.cur = {}
        self.setup()

    # ---- helpers ----
    def stream(self, purpose):
        s = self.streams.get(purpose)
        if s is None:
            s = self.streams[purpose] = Stream(self.seed, purpose)
        return s

    def draw(self, n):
        for _ in range(n):
            if not self.deck or len(self.hand) >= HAND_LIMIT:
                return
            c = self.deck.pop()
            self.hand.append(c)
            self.seen.append(c)

    def take(self, slot):
        """A search takes `slot` out of the deck into the hand if the hand has room; the rest of the deck stays in place
        (the same odds as the engine's reshuffle, because the order was already random)."""
        if len(self.hand) >= HAND_LIMIT:
            return False
        self.deck.remove(slot)
        self.hand.append(slot)
        self.seen.append(slot)
        if self.cfg.get('reshuffle_after_search'):
            self.stream('reshuffle').shuffle(self.deck)
        return True

    def pick(self, cands):
        return cands[self.stream('search').below(len(cands))]

    def insert_random(self, slot):
        self.deck.insert(self.stream('return').below(len(self.deck) + 1), slot)

    def room(self):
        return len(self.play) < BENCH + 1

    def in_play_names(self):
        return [m.name for m in self.play]

    def has_in_hand(self, kind):
        v = self.ver.tkind
        return next((s for s in self.hand if v[s] == kind), None)

    def discard_trainer(self, slot):
        self.hand.remove(slot)
        self.discard.append(slot)

    # ---- placing ----
    def place(self, slot):
        self.hand.remove(slot)
        self.play.append(Mon(self.ver, slot, self.t))
        if self.t > 0:
            self.cur['placed'] += 1

    def lead_rank(self, slot):
        lead = self.cfg['lead_order']
        n = self.ver.name[slot]
        return lead.index(n) if n in lead else len(lead)

    def place_basics(self):
        v, did = self.ver, False
        reserve = self.cfg['bench_reserved_for']
        while len(self.play) < BENCH + 1:
            cands = [s for s in self.hand if v.is_basic[s]]
            if not cands:
                break
            pr = [s for s in cands if v.name[s] == reserve]
            if pr:
                self.place(pr[0])
            else:
                # keep one Bench slot free while the plan Basic is still in the deck
                if len(self.play) >= BENCH and any(v.name[s] == reserve for s in self.deck):
                    break
                self.place(min(cands, key=self.lead_rank))
            did = True
        return did

    def setup(self):
        v = self.ver
        basics = [s for s in self.hand if v.is_basic[s]]
        self.place(min(basics, key=self.lead_rank))       # the Active: the first Basic by the lead order
        self.place_basics()
        self.t = 0

    # ---- one own turn ----
    def own_turn(self):
        self.t += 1
        t = self.t
        self.cur = {'placed': 0, 'evolved': 0, 'drawsearch': False, 'supporters': [], 'stadium': False,
                    'mesagoza': False}
        cfg = self.cfg
        self.draw(1)                                       # the first player's turn 1 included
        natural = cfg.get('natural_only')
        while True:
            changed = False
            if not natural:
                changed |= self.items()
                changed |= self.use_stadium()
            changed |= self.place_basics()
            changed |= self.evolve()
            if not natural:
                changed |= self.supporter()
            if not changed:
                break
        self.end_evolve()
        self.energy()
        self.attack()
        self.record()

    def items(self):
        v, did = self.ver, False
        cfg = self.cfg
        pieces = cfg['plan_pieces']
        while True:
            s = self.has_in_hand('pokeball')
            if s is not None and any(v.is_basic[c] for c in self.deck):
                self.discard_trainer(s)
                basics = [c for c in self.deck if v.is_basic[c]]
                if cfg.get('poke_ball_over') == 'names':
                    names = sorted({v.name[c] for c in basics})
                    nm = names[self.stream('search').below(len(names))]
                    got = next(c for c in basics if v.name[c] == nm)
                else:
                    got = self.pick(basics)
                self.take(got)
                self.cur['drawsearch'] = True
                did = True
                continue
            if self.candy():
                did = True
                continue
            s = self.has_in_hand('comm')
            if s is not None and any(v.name[c] in pieces for c in self.deck):
                cand = [h for h in self.hand if v.is_pokemon[h] and v.name[h] not in pieces]
                if cand:
                    prom = cfg['promote_order']
                    give = min(cand, key=lambda h: prom.index(v.name[h]) if v.name[h] in prom else len(prom))
                    mons = [c for c in self.deck if v.is_pokemon[c]]
                    got = mons[self.stream('comm').below(len(mons))]
                    self.discard_trainer(s)
                    self.hand.remove(give)
                    self.hand.append(got)
                    self.seen.append(got)
                    self.deck[self.deck.index(got)] = give
                    self.cur['drawsearch'] = True
                    did = True
                    continue
            return did

    def candy(self):
        """Rare Candy when legal (move_generation_trainer.rs:670-688, card_logic/rare_candy.rs:94-106)."""
        if self.t == 1:
            return False
        v = self.ver
        s = self.has_in_hand('candy')
        if s is None:
            return False
        for h in self.hand:
            if v.stage[h] != 2:
                continue
            root = v.root[h]
            for m in self.play:
                if m.stage == 0 and m.placed < self.t and m.name == root:
                    self.discard_trainer(s)
                    self.hand.remove(h)
                    m.slot, m.name, m.stage, m.evolved, m.hp = h, v.name[h], 2, self.t, v.hp[h]
                    self.cur['evolved'] += 1
                    return True
        return False

    def use_stadium(self):
        did = False
        v = self.ver
        s = self.has_in_hand('stadium')
        if self.stadium is None and s is not None and not self.cur['stadium']:
            self.discard_trainer(s)
            self.stadium = 'Mesagoza'
            self.cur['stadium'] = True
            did = True
        if self.stadium == 'Mesagoza' and not self.cur['mesagoza']:
            mons = [c for c in self.deck if v.is_pokemon[c]]
            if mons:
                self.cur['mesagoza'] = True
                self.cur['drawsearch'] = True
                mode = self.cfg.get('mesagoza_coin', 'random')
                heads = mode == 'heads' or (mode == 'random' and self.stream('mesagoza').below(2) == 1)
                if heads:
                    self.take(self.pick(mons))
                did = True
        return did

    def evolve(self):
        if self.t == 1:
            return False
        v, did = self.ver, False
        for m in self.play:
            if m.placed == self.t or m.evolved == self.t:
                continue
            for h in self.hand:
                if v.stage[h] > 0 and v.frm[h] == m.name and (m.name, v.name[h]) not in self.hold:
                    self.hand.remove(h)
                    m.slot, m.name, m.stage, m.evolved, m.hp = h, v.name[h], v.stage[h], self.t, v.hp[h]
                    self.cur['evolved'] += 1
                    did = True
                    break
        return did

    def end_evolve(self):
        """Step 4: a Pawniard still in play evolves into Bisharp if one is in hand (after the rest of the turn)."""
        if self.t == 1:
            return
        v = self.ver
        for m in self.play:
            if m.placed == self.t or m.evolved == self.t:
                continue
            for h in self.hand:
                if v.stage[h] > 0 and v.frm[h] == m.name and (m.name, v.name[h]) in self.hold:
                    self.hand.remove(h)
                    m.slot, m.name, m.stage, m.evolved, m.hp = h, v.name[h], v.stage[h], self.t, v.hp[h]
                    self.cur['evolved'] += 1
                    break

    def supporter(self):
        if self.cur['supporters']:
            return False
        v, cfg = self.ver, self.cfg
        main = cfg['main_attacker']
        s = self.has_in_hand('juliana')
        if s is not None:
            c2 = [c for c in self.deck if v.stage[c] == 2]
            if any(v.name[c] == main for c in self.deck):
                self.discard_trainer(s)
                self.take(self.pick(c2))
                return self.played('juliana')
        s = self.has_in_hand('lisia')
        if s is not None and self.room():
            c = [c for c in self.deck if v.is_basic[c] and v.hp[c] <= 50]
            if c:
                self.discard_trainer(s)
                for _ in range(min(2, len(c))):
                    g = self.pick(c)
                    c.remove(g)
                    self.take(g)
                return self.played('lisia')
        s = self.has_in_hand('sightseer')
        if s is not None and any(v.stage[c] == 1 for c in self.deck):
            self.discard_trainer(s)
            top = [self.deck.pop() for _ in range(min(4, len(self.deck)))]
            for c in top:
                if v.stage[c] == 1:
                    self.hand.append(c)               # no hand-limit check (flagged, SIM docstring)
                    self.seen.append(c)
                else:
                    self.insert_random(c)
            return self.played('sightseer')
        s = self.has_in_hand('prof')
        if s is not None and len(self.hand) <= 8:
            self.discard_trainer(s)
            self.draw(2)
            return self.played('prof')
        s = self.has_in_hand('copycat')
        if s is not None:
            main_in_hand = any(v.name[h] == main or v.tkind[h] == 'candy' for h in self.hand)
            smaller = len(self.hand) - 1 < cfg['opp_hand']
            if not main_in_hand and (smaller or cfg.get('copycat_rule') == 'always'):
                self.discard_trainer(s)
                for h in list(self.hand):
                    self.hand.remove(h)
                    self.insert_random(h)
                self.copycat_draws.append(cfg['opp_hand'])
                self.draw(cfg['opp_hand'])
                return self.played('copycat')
        return False

    def played(self, kind):
        self.cur['supporters'].append(kind)
        self.cur['drawsearch'] = True
        return True

    def energy(self):
        if self.first and self.t == 1:
            return                                     # no Energy on the first player's first turn
        cfg = self.cfg
        main = cfg['main_attacker']
        play = self.play
        pick = next((m for m in play if m.name == main and m.energy < self.cost), None)
        if pick is None:
            for nm in cfg['energy_line']:             # Bisharp, then Pawniard: fewer than 2
                pick = next((m for m in play if m.name == nm and m.energy < 2), None)
                if pick:
                    break
        if pick is None and any(m.name == cfg['muk'] for m in play):
            pick = next((m for m in play if m.name == cfg['muk_partner']), None)
        if pick is None:
            pick = play[0]
        pick.energy += 1

    def attack(self):
        a = self.play[0] if self.play else None
        if a is None or self.first and self.t == 1:
            return
        if a.name == self.cfg['main_attacker'] and a.energy >= self.cost:
            self.blades.append({'turn': self.t, 'damage': blade_damage(self.ko), 'k': self.ko,
                                'opp_points': self.opp_points})
            if self.first_attack_turn is None:
                self.first_attack_turn = self.t

    def record(self):
        play, cfg = self.play, self.cfg
        main = cfg['main_attacker']
        names = [m.name for m in play]
        rec = {'in_play': names, 'roots': [m.root for m in play], 'stages': [m.stage for m in play],
               'energy_total': sum(m.energy for m in play),
               'kg_energy': max((m.energy for m in play if m.name == main), default=-1),
               'supporters': list(self.cur['supporters']), 'placed': self.cur['placed'],
               'evolved': self.cur['evolved'], 'hand': len(self.hand),
               'empty': not (self.cur['placed'] or self.cur['evolved'] or self.cur['drawsearch'])}
        if cfg.get('natural_only') or cfg.get('detail'):
            rec['seen_names'] = [self.ver.name[s] for s in self.seen]
        self.turns.append(rec)

    # ---- the opponent's turn ----
    def promote(self):
        v, cfg = self.ver, self.cfg
        if not self.play:
            return
        main = cfg['main_attacker']
        ready = [m for m in self.play if m.name == main and m.energy >= self.cost]
        if ready and self.ko >= cfg['blade_target']:
            pick = ready[0]
        else:
            prom = cfg['promote_order']
            pick = min(self.play, key=lambda m: prom.index(m.name) if m.name in prom else len(prom))
        self.play.remove(pick)
        self.play.insert(0, pick)

    def knock_out(self, j):
        if not self.play:
            return
        dead = self.play.pop(0)
        self.ko += 1
        if dead.name == self.cfg['pawniard'] and self.pawniard_lost_j is None:
            self.pawniard_lost_j = j
        gain = 1
        if dead.name == self.cfg['coin_pokemon']:
            mode = self.cfg.get('glimmora_coin', 'random')
            heads = mode == 'heads' or (mode == 'random' and self.stream('glimmora').below(2) == 1)
            if heads:
                gain = 0
        self.opp_points += gain
        if self.opp_points >= 3:
            self.ended = 'points'
        elif not self.play:
            self.ended = 'wiped'
        else:
            self.promote()

    def opp_turn(self, tl, j):
        kos = tl.ko(j)
        if kos is None:
            if self.und_j is None:
                self.und_j = j
            kos = 0
        for _ in range(kos):
            if self.ended:
                break
            self.knock_out(j)
        if not self.ended and tl.complete_at == j:
            self.ended = 'record'


def play_deal(ver, deal, first, cfg, clock=None, order=None, seed_base=SEED_BASE):
    """One deal: the opening, then `horizon` own turns (`setup_horizon` with no clock). Returns the trace."""
    g = Game(ver, deal, first, cfg, order, seed_base)
    tl = clock.timeline(deal, first) if clock is not None else None
    horizon = cfg['horizon'] if clock is not None else cfg['setup_horizon']
    setup = {'in_play': g.in_play_names(), 'roots': [m.root for m in g.play]}
    for t in range(1, horizon + 1):
        if tl is not None and not first:
            g.opp_turn(tl, t)
            if g.ended:
                break
        g.own_turn()
        if tl is not None and first:
            g.opp_turn(tl, t)
            if g.ended:
                break
    und_own = None
    if g.und_j is not None:
        und_own = g.und_j + (1 if first else 0)
    return {'setup': setup, 'turns': g.turns, 'first_attack_turn': g.first_attack_turn, 'blades': g.blades,
            'ko': g.ko, 'opp_points': g.opp_points, 'ended': g.ended, 'und_j': g.und_j, 'und_own': und_own,
            'pawniard_lost_j': g.pawniard_lost_j, 'copycat_draws': g.copycat_draws,
            'game': tl.game if tl is not None else None, 'horizon': horizon, 'first': first}
