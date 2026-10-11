"""Tests for skip_attack.py (the combined run's skip-attack comparison): made-up games, no run data.
Run: python3 -m unittest test_skip_attack   (from this folder)"""
import math, sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skip_attack as sa  # noqa: E402


def d(t, a, act, n=3):
    return {"t": t, "a": a, "act": act, "n": n, "o": (t + 1) // 2, "ms": 1.0, "p": [0, 0], "b": 1}


GAME_A = {"first": "deck", "turns": 9, "log": [
    d(1, "Place:Elec@3", "Elec"), d(1, "EndTurn", "Elec", 2),                                  # t1: E
    d(3, "Evolve:Heli@0", "Elec"), d(3, "Attack:Zap", "Heli"),                                  # t3: A (attacker Heli)
    d(4, "Promote:0@3", ""),                                                                    # the opponent's turn: ignored
    d(5, "Attach:1L@0 zone", "Heli"), d(5, "Attack:Zap", "Heli"),                               # t5: A, R
    d(7, "Retreat:2", "Heli"), d(7, "Attach:1L@0 zone", "Mega"),                                # t7: no attack, a Retreat, forced end: F, R, R2
    d(9, "Play:Cyrus", "Mega"), d(9, "EndTurn", "Mega", 3)]}                                    # t9: E, not R (t7 did not attack)
GAME_B = {"first": "opp", "turns": 6, "log": [d(2, "Attack:Zap", "Heli"), d(6, "Attack:Zap", "Heli")]}   # t4: no decision at all


class Turns(unittest.TestCase):
    def test_every_own_turn_is_one_of_a_e_f(self):
        r = sa.turn_records(GAME_A)
        self.assertEqual({t: x["out"] for t, x in r.items()}, {1: "E", 3: "A", 5: "A", 7: "F", 9: "E"})
        self.assertEqual((r[3]["attacker"], r[3]["attack"], r[7]["retreat"], r[5]["retreat"]), ("Heli", "Zap", True, False))
        rb = sa.turn_records(GAME_B)
        self.assertEqual({t: x["out"] for t, x in rb.items()}, {2: "A", 4: "F", 6: "A"})
        self.assertIsNone(rb[4]["act0"])

    def test_the_cohorts(self):
        c = sa.cohorts(GAME_A)
        self.assertEqual((c["own"]["n"], c["own"]["A"], c["own"]["E"], c["own"]["F"]), (5, 2, 2, 1))
        self.assertEqual((c["after"]["n"], c["after"]["A"], c["after"]["E"], c["after"]["F"]), (3, 1, 1, 1))     # t5, t7, t9
        self.assertEqual((c["R"]["n"], c["R"]["A"], c["R"]["na"], c["R"]["ret"], c["R"]["eo"], c["R"]["fo"]), (2, 1, 1, 1, 0, 0))   # t5, t7
        self.assertEqual((c["R2"]["n"], c["R2"]["na"], c["R2"]["ret"]), (1, 1, 1))                              # t7 only
        self.assertEqual(c["R"]["prev:Zap"], 1)
        cb = sa.cohorts(GAME_B)
        self.assertEqual((cb["after"]["n"], cb["after"]["A"], cb["after"]["F"]), (2, 1, 1))
        self.assertEqual(cb["R"]["n"], 0)                         # t6 follows a turn with no attack; t4 has no decision

    def test_a_different_pokemon_in_front_is_not_a_repeat_attacker(self):
        g = {"first": "deck", "turns": 5, "log": [d(1, "Attack:Zap", "Heli"), d(3, "Attack:Zap", "Mega")]}
        self.assertEqual(sa.cohorts(g)["R"]["n"], 0)

    def test_the_opponents_turn_decisions_are_not_the_decks_turn(self):
        g = {"first": "deck", "turns": 4, "log": [d(1, "EndTurn", "Heli", 2), d(2, "Promote:0@1", ""), d(3, "Attack:Zap", "Heli")]}
        self.assertEqual({t: x["out"] for t, x in sa.turn_records(g).items()}, {1: "E", 3: "A"})


class Intervals(unittest.TestCase):
    def test_a_known_ratio_and_half_width(self):
        r, h = sa.ratio_diff([(1, 2), (0, 2), (1, 2)])
        self.assertAlmostEqual(r, 1 / 3)
        self.assertAlmostEqual(h, 1.96 / 6)

    def test_a_bot_against_itself_differs_by_exactly_zero(self):
        v = [(1, 2), (0, 3), (2, 2), (0, 1)]
        self.assertEqual(sa.ratio_diff(v, list(v)), (0.0, 0.0))

    def test_a_paired_difference_is_the_difference_of_the_shares(self):
        v1, v2 = [(1, 2), (0, 2), (1, 2), (2, 2)], [(0, 2), (0, 2), (1, 2), (1, 2)]
        r, h = sa.ratio_diff(v1, v2)
        self.assertAlmostEqual(r, 4 / 8 - 2 / 8)
        self.assertGreater(h, 0)

    def test_nothing_to_divide_is_not_a_number(self):
        self.assertIsNone(sa.ratio_diff([(0, 0), (0, 0)]))
        self.assertIsNone(sa.ratio_diff([(1, 2)]))


if __name__ == "__main__":
    unittest.main()
