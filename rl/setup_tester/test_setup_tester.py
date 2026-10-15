#!/usr/bin/env python3
"""Tests for the setup tester, written before the code (SPEC.md "Tests to write first", items 1-7).

    python3 rl/setup_tester/test_setup_tester.py            full sizes (400k-deal checks; a few minutes)
    ST_FAST=1 python3 rl/setup_tester/test_setup_tester.py  small sizes, for quick runs while editing

Standard library only. No engine program is used.
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import consistency as cl          # noqa: E402  (read_deck, resolve, classify, opening_exact only)
import st_exact as ex             # noqa: E402
import st_sim as sim              # noqa: E402
import st_clock as clk            # noqa: E402
import setup_tester as st         # noqa: E402

FAST = bool(os.environ.get('ST_FAST'))
BIG = 20_000 if FAST else 400_000       # spec test 1 and 3: 400k deals
MID = 5_000 if FAST else 20_000
HIS = os.path.join(ROOT, 'rl', 'results', 'pause_games_new_2026-10-13', 'decks', 'KW261012_203719000.txt')
D01 = os.path.join(ROOT, 'decks', 'dustin', '01-muk-glimmora-kingambit-regigigas.txt')
CFG = sim.load_cfg()


def deck(path):
    return cl.read_deck(path)[1]


def version(diff=None, path=HIS, label='v'):
    base = deck(HIS)
    if diff is None and path == HIS:
        return sim.Version(base, base, label)
    return sim.Version(st.build_cards(path, diff or []), base, label)


def hand_deck(top_ids, first, cfg=None, clock=None, **over):
    """Play one deal on his list with the top of the deck fixed by card id (hand = the first five)."""
    ver = version()
    order = sim.order_for(ver, top_ids)
    c = dict(CFG, **over)
    return ver, sim.play_deal(ver, 0, first, c, clock=clock, order=order)


PAWN, KING, BISH = 'B3a 041', 'B3a 043', 'B3a 042'
CANDY, JULI, LISIA, POP = 'A3 144', 'B3a 071', 'B1 226', 'B2 145'
HELM, ILIMA, PROF, COPY = 'B1 219', 'A3 149', 'A4b 373', 'B1 225'
GLIMMET, GLIMMORA, GRIMER, MUK, REGI, MESA = 'B3a 044', 'B3a 045', 'A3 110', 'B2 097', 'B3 134', 'B2a 093'


class T1Exact(unittest.TestCase):
    """Test 1: the formulas against the SPEC anchors (5 decimals); simulation against them within 4 SE."""

    def setUp(self):
        self.cards = deck(HIS)
        self.d01 = deck(D01)

    def anchors(self, cards):
        by = {c.id: c for c in cards}
        a = {}
        a['p0'] = ex.p0(5)
        a['pawn'] = ex.in_hand(cards, 'Pawniard')
        a['king'] = ex.in_hand(cards, 'Kingambit')
        a['candy'] = ex.in_hand(cards, 'Rare Candy')
        a['seen7'] = ex.seen_prob(cards, ['Pawniard', 'Kingambit', 'Rare Candy'], 7)
        a['seen8'] = ex.seen_prob(cards, ['Pawniard', 'Kingambit', 'Rare Candy'], 8)
        a['only'] = ex.forced_active(cards)['Pawniard']
        return a

    def test_anchors_both_lists(self):
        want = dict(p0=0.19369, pawn=0.28874, king=0.23709, candy=0.23709, seen7=0.03373, seen8=0.05246,
                    only=0.12678)
        for cards in (self.cards, self.d01):
            got = self.anchors(cards)
            for k, v in want.items():
                self.assertAlmostEqual(got[k], v, places=5, msg=k)

    def test_closed_forms(self):
        from math import comb
        b = 5
        self.assertAlmostEqual(ex.p0(b), comb(20 - b, 5) / comb(20, 5), places=12)
        self.assertAlmostEqual(ex.in_hand_basic1(b), 5 / 20 + ex.p0(b) / b, places=12)
        self.assertAlmostEqual(ex.in_hand_nonbasic1(b), 5 / 20 - comb(19 - b, 4) / comb(20, 5) / 5, places=12)

    def test_against_consistency_opening_exact(self):
        """The helper in lib/consistency.py already does single cards; the two must agree."""
        plan = cl.Plan(HIS, ['Darkness'], self.cards, main='Kingambit')
        oe = cl.opening_exact(plan)
        self.assertAlmostEqual(ex.in_hand(self.cards, 'Pawniard'), oe['present']['Pawniard'], places=9)
        self.assertAlmostEqual(ex.in_hand(self.cards, 'Kingambit'), oe['present']['Kingambit'], places=9)
        self.assertAlmostEqual(ex.forced_active(self.cards)['Pawniard'], oe['only']['Pawniard'], places=9)

    def test_basics_in_hand_sums_to_one(self):
        d = ex.basics_in_hand(self.cards)
        self.assertAlmostEqual(sum(d.values()), 1.0, places=12)
        self.assertEqual(d[0], 0.0)
        self.assertAlmostEqual(d[1] + 0, ex.opening_basics(self.cards)[1], places=12)

    def test_natural_draw_facts(self):
        self.assertEqual([ex.cards_seen(n) for n in (1, 2, 5)], [6, 7, 10])
        self.assertEqual([ex.energy_by_turn(n, True) for n in (1, 2, 3)], [0, 1, 2])
        self.assertEqual([ex.energy_by_turn(n, False) for n in (1, 2, 3)], [1, 2, 3])
        self.assertEqual(ex.earliest_kingambit_attack(first=True, via='candy'), 3)
        self.assertEqual(ex.earliest_kingambit_attack(first=False, via='candy'), 2)
        self.assertEqual(ex.earliest_kingambit_attack(first=True, via='bisharp'), 3)
        self.assertEqual(ex.earliest_kingambit_attack(first=False, via='bisharp'), 3)

    def test_deal_cards_match_exact(self):
        """The deal (shuffle, swap-in, reshuffle) against the exact numbers, within 4 standard errors."""
        ver = version()
        n = BIG
        names = [c.name for c in ver.cards]
        hit_hand = hit7 = hit8 = hits0 = 0
        for i in range(n):
            hand, deck_top_first = sim.deal_cards(ver, i)
            hn = [names[s] for s in hand]
            if 'Pawniard' in hn:
                hit_hand += 1
            seq = hn + [names[s] for s in deck_top_first]
            for k, need in ((7, 'a'), (8, 'b')):
                seen = set(seq[:k])
                if {'Pawniard', 'Kingambit', 'Rare Candy'} <= seen:
                    if k == 7:
                        hit7 += 1
                    else:
                        hit8 += 1
        for got, want in ((hit_hand, 0.28874), (hit7, 0.03373), (hit8, 0.05246)):
            se = (want * (1 - want) / n) ** 0.5
            self.assertLess(abs(got / n - want), 4 * se)

    def test_play_with_natural_draws_only_matches_exact(self):
        """The full play loop, with every search and trainer switched off, sees exactly the natural draws."""
        ver = version()
        c = dict(CFG, natural_only=True)
        n = BIG
        got = {2: 0, 3: 0}
        for i in range(n):
            tr = sim.play_deal(ver, i, i % 2 == 0, c)
            for t in (2, 3):
                if {'Pawniard', 'Kingambit', 'Rare Candy'} <= set(tr['turns'][t - 1]['seen_names']):
                    got[t] += 1
        for t, k in ((2, 7), (3, 8)):
            want = ex.seen_prob(self.cards, ['Pawniard', 'Kingambit', 'Rare Candy'], k)
            se = (want * (1 - want) / n) ** 0.5
            self.assertLess(abs(got[t] / n - want), 4 * se, msg=f'turn {t}')


class T2Hand(unittest.TestCase):
    """Test 2: hand-checked, fixed-order decks."""

    def in_play(self, tr, t):
        return tr['turns'][t - 1]['in_play']

    def test_candy_refused_turn1_and_on_a_pawniard_placed_that_turn(self):
        # Pawniard the only Basic (so Active); Kingambit and Rare Candy in hand. Going second.
        top = [PAWN, KING, CANDY, POP, HELM, ILIMA, POP]
        _, tr = hand_deck(top, first=False)
        self.assertNotIn('Kingambit', self.in_play(tr, 1))          # refused on own turn 1
        self.assertIn('Kingambit', self.in_play(tr, 2))             # played on own turn 2
        # Going first, Glimmet is the Active; Pawniard is drawn on own turn 2 and so is placed that turn.
        top = [GLIMMET, KING, CANDY, POP, HELM, ILIMA, PAWN]
        _, tr = hand_deck(top, first=True)
        self.assertNotIn('Pawniard', self.in_play(tr, 1))
        self.assertIn('Pawniard', self.in_play(tr, 2))
        self.assertNotIn('Kingambit', self.in_play(tr, 2))          # refused on a Pawniard placed this turn
        self.assertIn('Kingambit', self.in_play(tr, 3))

    def test_first_attack_turn_pawniard_only_basic(self):
        top = [PAWN, KING, CANDY, POP, HELM, ILIMA, POP]
        _, tr = hand_deck(top, first=False)
        self.assertEqual(tr['first_attack_turn'], 2)
        _, tr = hand_deck(top, first=True)
        self.assertEqual(tr['first_attack_turn'], 3)

    def test_bisharp_juliana_candy_on_turn_two(self):
        # hand: Pawniard, Bisharp, Rare Candy, 2 blanks; turn-1 draw blank; turn-2 draw Juliana.
        top = [PAWN, BISH, CANDY, POP, HELM, ILIMA, JULI]
        for first in (True, False):
            ver = version(['-1 Lucky Ice Pop B2 145', '+1 Bisharp B3a 042', '-1 Copycat B1 225',
                           '+1 Juliana B3a 071'])
            order = sim.order_for(ver, top)
            tr = sim.play_deal(ver, 0, first, dict(CFG, mesagoza_coin='tails'), order=order)
            if first:
                self.assertNotIn('Kingambit', self.in_play(tr, 1))
                self.assertIn('Kingambit', self.in_play(tr, 2))
            else:
                # going second the turn-1 draw is Ilima: Juliana arrives with the turn-2 draw too
                self.assertIn('Kingambit', self.in_play(tr, 2))

    def test_pawniard_always_finds_a_bench_slot(self):
        # four non-Pawniard Basics in hand; Pawniard is the next card drawn
        top = [REGI, GLIMMET, GLIMMET, GRIMER, HELM, PAWN]
        _, tr = hand_deck(top, first=True)
        self.assertIn('Pawniard', self.in_play(tr, 1))
        self.assertLessEqual(len(self.in_play(tr, 1)), 4)

    def test_bench_cap_three(self):
        top = [REGI, GLIMMET, GLIMMET, GRIMER, HELM, PAWN, GLIMMORA]
        _, tr = hand_deck(top, first=True)
        for t in tr['turns']:
            self.assertLessEqual(len(t['in_play']), 4)

    def test_one_supporter_per_turn(self):
        top = [PAWN, PROF, PROF, COPY, ILIMA, POP, HELM, POP]
        _, tr = hand_deck(top, first=True)
        for t in tr['turns']:
            self.assertLessEqual(len(t['supporters']), 1)
        self.assertEqual(len(tr['turns'][0]['supporters']), 1)       # allowed on the first player's turn 1
        self.assertEqual(len(tr['turns'][1]['supporters']), 1)

    def test_hand_cap_ten(self):
        g = sim.Game(version(), 0, True, CFG, order=sim.order_for(version(), [PAWN]))
        g.hand = list(range(10))
        before = len(g.deck)
        g.draw(3)
        self.assertEqual(len(g.hand), 10)
        self.assertEqual(len(g.deck), before)                       # skipped draws stay in the deck

    def test_empty_deck_no_draw(self):
        g = sim.Game(version(), 0, True, CFG, order=sim.order_for(version(), [PAWN]))
        g.deck = []
        g.hand = [0]
        g.draw(2)
        self.assertEqual(len(g.hand), 1)

    def test_energy_n_minus_one_going_first(self):
        top = [REGI, GLIMMET, HELM, ILIMA, POP, POP]
        for first in (True, False):
            _, tr = hand_deck(top, first=first, natural_only=True)
            for n in range(1, 6):
                got = tr['turns'][n - 1]['energy_total']
                self.assertEqual(got, ex.energy_by_turn(n, first), msg=f'first={first} turn {n}')

    def test_blade_damage(self):
        self.assertEqual([sim.blade_damage(k) for k in range(4)], [60, 100, 140, 180])

    def test_blade_in_play_uses_knockouts_so_far(self):
        top = [PAWN, KING, CANDY, POP, HELM, ILIMA, POP]
        fixed = clk.Fixed('t', {1: 0, 2: 0, 3: 0, 4: 0, 5: 0})
        _, tr = hand_deck(top, first=False, clock=fixed)
        self.assertEqual(tr['blades'][0]['damage'], 60)
        # every recorded Blade equals 60 + 40 k, with k the knock-outs counted at that moment
        for _ in range(0, 1):
            for i in range(300):
                ver = version()
                t = sim.play_deal(ver, i, i % 2 == 0, CFG, clock=clk.FIXED['fast'])
                for b in t['blades']:
                    self.assertEqual(b['damage'], 60 + 40 * b['k'])

    def test_glimmora_heads_gives_no_point_tails_one(self):
        # Glimmet Active, Glimmora drawn turn 1 (Glimmet evolves turn 2); one knock-out on opponent turn 2
        top = [GLIMMET, GLIMMORA, HELM, ILIMA, POP, POP]
        one = clk.Fixed('t', {2: 1})
        _, heads = hand_deck(top, first=True, clock=one, glimmora_coin='heads')
        _, tails = hand_deck(top, first=True, clock=one, glimmora_coin='tails')
        self.assertEqual((heads['ko'], heads['opp_points']), (1, 0))
        self.assertEqual((tails['ko'], tails['opp_points']), (1, 1))

    def test_losing_the_last_pokemon_ends_the_deal(self):
        top = [PAWN, KING, HELM, ILIMA, POP, POP]        # one Basic, no Bench
        _, tr = hand_deck(top, first=True, clock=clk.Fixed('t', {1: 1}), natural_only=True)
        self.assertEqual(tr['ended'], 'wiped')
        self.assertEqual(len(tr['turns']), 1)

    def test_three_points_end_the_deal(self):
        top = [REGI, GLIMMET, GLIMMET, GRIMER, HELM, ILIMA, POP, POP]
        _, tr = hand_deck(top, first=True, clock=clk.Fixed('t', {1: 1, 2: 1, 3: 1, 4: 1}), natural_only=True,
                          glimmora_coin='tails')
        self.assertEqual(tr['ended'], 'points')
        self.assertEqual(tr['opp_points'], 3)


class T3Repro(unittest.TestCase):
    """Test 3: reproducibility and pairing."""

    N = 400 if FAST else 1500

    def run_versions(self, order):
        vf = {'base': HIS, 'versions': {k: v for k, v in VERSIONS.items()}, 'plan': st.default_plan_path()}
        return st.run_versions(vf, n_deals=self.N, clock_deals=0, clocks=[], workers=1, order=order,
                               base_path=HIS)

    def test_same_seed_byte_identical(self):
        a = st.run_one(HIS, [], self.N, seed_base=24_700_000_000, clocks=[], clock_deals=0)
        b = st.run_one(HIS, [], self.N, seed_base=24_700_000_000, clocks=[], clock_deals=0)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_reordering_versions_changes_nothing(self):
        r1 = self.run_versions(list(VERSIONS))
        r2 = self.run_versions(list(reversed(list(VERSIONS))))
        for k in VERSIONS:
            self.assertEqual(json.dumps(r1['versions'][k]['measures'], sort_keys=True),
                             json.dumps(r2['versions'][k]['measures'], sort_keys=True))

    def test_printing_only_version_is_identical(self):
        base = st.run_one(HIS, [], self.N, clocks=[], clock_deals=0, keep_vectors=True)
        pr = st.run_one(HIS, ['-1 Poké Ball A2b 111', '+1 Poké Ball P-A 005'], self.N, clocks=[], clock_deals=0,
                        keep_vectors=True)
        self.assertEqual(base['vectors'], pr['vectors'])

    def test_swapping_never_played_cards_is_identical_per_deal(self):
        base = st.run_one(HIS, [], self.N, clocks=[], clock_deals=0, keep_vectors=True)
        sw = st.run_one(HIS, ['-1 Lucky Ice Pop B2 145', '+1 Heavy Helmet B1 219'], self.N, clocks=[],
                        clock_deals=0, keep_vectors=True)
        self.assertEqual(base['vectors'], sw['vectors'])

    def test_a_one_card_change_alters_one_slot(self):
        base = version()
        v = version(['-1 Copycat B1 225', '+1 Juliana B3a 071'])
        diff = [i for i in range(20) if base.cards[i].id != v.cards[i].id]
        self.assertEqual(len(diff), 1)

    def test_search_without_reshuffle_matches_explicit_reshuffle(self):
        ver = version()
        n = BIG if not FAST else 4000
        n = min(n, 40_000)                      # the full play loop is the slow part; see REPORT.md
        a = b = 0
        for i in range(n):
            ta = sim.play_deal(ver, i, i % 2 == 0, CFG)
            tb = sim.play_deal(ver, i, i % 2 == 0, dict(CFG, reshuffle_after_search=True))
            a += 'Kingambit' in ta['turns'][3]['in_play']
            b += 'Kingambit' in tb['turns'][3]['in_play']
        p = (a + b) / (2 * n)
        se = (2 * p * (1 - p) / n) ** 0.5
        self.assertLess(abs(a - b) / n, 4 * se + 1e-9)

    def test_illegal_version_is_rejected(self):
        with self.assertRaises(SystemExit):
            st.build_cards(HIS, ['+1 Pawniard B3a 041', '-1 Copycat B1 225'])   # 2 of one id is fine ...
            st.build_cards(HIS, ['+1 Pawniard B3a 041', '-1 Copycat B1 225', '+1 Pawniard B3a 041',
                                 '-1 Ilima A3 149'])                                # ... 3 Pawniards are not


VERSIONS = {'copy_juli': ['-1 Copycat B1 225', '+1 Juliana B3a 071'],
            'lisia': ['-1 Lucky Ice Pop B2 145', '+1 Lisia B1 226'],
            'bisharp': ['-1 Lucky Ice Pop B2 145', '+1 Bisharp B3a 042']}


class T4Direction(unittest.TestCase):
    """Test 4: direction, on his list."""

    N = 3000 if FAST else 20000

    @classmethod
    def setUpClass(cls):
        kw = dict(clocks=[], clock_deals=0, keep_vectors=True)
        cls.base = st.run_one(HIS, [], cls.N, **kw)
        cls.juli = st.run_one(HIS, VERSIONS['copy_juli'], cls.N, **kw)
        cls.nocandy = st.run_one(HIS, ['-1 Rare Candy A3 144', '+1 Heavy Helmet B1 219'], cls.N, **kw)
        cls.bish = st.run_one(HIS, VERSIONS['bisharp'], cls.N, **kw)
        cls.lisia = st.run_one(HIS, VERSIONS['lisia'], cls.N, **kw)

    def rate(self, r, m):
        return st.rate(r, m)

    def test_juliana_for_copycat_raises_k2_turns_2_and_3(self):
        for t in (2, 3):
            self.assertGreater(self.rate(self.juli, f'K2.t{t}'), self.rate(self.base, f'K2.t{t}'), msg=t)

    def test_no_candy_no_bisharp_gives_zero_k2(self):
        for t in range(2, 7):
            self.assertEqual(self.rate(self.nocandy, f'K2.t{t}'), 0.0)

    def test_bisharp_raises_k2_at_turn_3(self):
        self.assertGreater(self.rate(self.bish, 'K2.t3'), self.rate(self.base, 'K2.t3'))

    def test_bisharp_turn_two_identical_deal_by_deal_with_mesagoza_tails(self):
        kw = dict(clocks=[], clock_deals=0, keep_vectors=True, cfg_over={'mesagoza_coin': 'tails'})
        a = st.run_one(HIS, [], 4000, **kw)
        b = st.run_one(HIS, VERSIONS['bisharp'], 4000, **kw)
        self.assertEqual(a['vectors']['K2.t2'], b['vectors']['K2.t2'])

    def test_lisia_raises_k1_turns_1_to_3(self):
        for t in (1, 2, 3):
            self.assertGreater(self.rate(self.lisia, f'K1.t{t}'), self.rate(self.base, f'K1.t{t}'), msg=t)


class T5Clock(unittest.TestCase):
    """Test 5: the recorded clock reproduces me.knockouts; Copycat draws 4 under every clock."""

    def test_his_clock_reproduces_recorded_knockouts(self):
        c = clk.load_his(ROOT)
        self.assertEqual(len(c.games), 12)
        self.assertEqual(sum(1 for g in c.games if g['first']), 9)
        self.assertEqual(sum(1 for g in c.games if not g['first']), 3)
        for g in c.games:
            for turn, recorded in g['recorded_k']:
                self.assertEqual(clk.k_at_own_turn(g, turn), recorded, msg=(g['name'], turn))

    def test_bot_clock_has_64_games(self):
        c = clk.load_bot(ROOT)
        self.assertEqual(len(c.games), 64)
        self.assertEqual(sum(1 for g in c.games if g['first']), 42)

    def test_copycat_draws_four_under_every_clock(self):
        ver = version()
        for name, c in [('none', None), ('fast', clk.FIXED['fast']), ('medium', clk.FIXED['medium']),
                        ('slow', clk.FIXED['slow']), ('his', clk.load_his(ROOT)), ('bot', clk.load_bot(ROOT))]:
            for i in range(300):
                tr = sim.play_deal(ver, i, i % 2 == 0, CFG, clock=c)
                for d in tr['copycat_draws']:
                    self.assertEqual(d, 4, msg=name)

    def test_fixed_clock_paces(self):
        f, m, s = (clk.FIXED[k] for k in ('fast', 'medium', 'slow'))
        self.assertEqual([f.ko(j) for j in range(1, 5)], [0, 1, 1, 1])
        self.assertEqual([m.ko(j) for j in range(1, 5)], [0, 0, 1, 1])
        self.assertEqual([s.ko(j) for j in range(1, 8)], [0, 0, 1, 0, 1, 0, 1])

    def test_sampling_is_keyed_by_deal_alone(self):
        c = clk.load_his(ROOT)
        self.assertEqual(c.pick(17, True), c.pick(17, True))
        self.assertEqual(c.pick(17, False), c.pick(17, False))


class T6Consistency(unittest.TestCase):
    """Test 6: against lib/consistency.py on deck 01. Gaps are printed and explained, never failures."""

    def test_comparison_runs_and_explains_every_gap(self):
        rows = st.compare_consistency(D01, 2000 if FAST else 20000)
        self.assertEqual([r['turn'] for r in rows], [2, 3, 4, 5])
        for r in rows:
            self.assertIn('explained', r)
            self.assertTrue(r['explained'])


class T7Bots(unittest.TestCase):
    """Test 7: K3 beside the first Overlord's Blade turn in the 64 games. A gap is printed, not a failure."""

    def test_bot_blade_turns(self):
        rows = st.compare_bots(ROOT, 1000 if FAST else 20000)
        self.assertEqual(rows['games'], 64)
        self.assertIn('bot_first_blade', rows)
        self.assertIn('sim_k3', rows)


if __name__ == '__main__':
    unittest.main(verbosity=1)
