"""Tests for skip_exact.py (the cloud, Oct 12). Run: python3 -m unittest test_skip_exact   (from this folder)"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skip_exact as se  # noqa: E402


def d(key, turn, attack_legal, taken_attack, decision=0, deck="09-mega-manectric-heliolisk", legal=None, taken=None):
    return {"key": key, "turn": turn, "decision": decision, "deck": deck, "attack_legal": attack_legal, "taken_attack": taken_attack,
            "attacks": ["Attack:Bite"] if attack_legal else [], "legal": legal or ["EndTurn"], "taken": taken or ("Attack:Bite" if taken_attack else "EndTurn")}


class PerGame(unittest.TestCase):
    def test_decision_points_and_skips(self):
        rows = [d("k", 3, True, False, 0), d("k", 3, True, True, 1), d("k", 5, False, False, 2), d("k", 7, True, False, 3)]
        g = se.per_game(rows)
        self.assertEqual((g["points"], g["skips"]), (3, 2))       # 3 decisions with an attack legal; 2 of them not an attack

    def test_a_turn_with_an_attack_later_is_not_a_skip_turn(self):
        rows = [d("k", 3, True, False, 0), d("k", 3, True, True, 1)]
        g = se.per_game(rows)
        self.assertEqual((g["turns"], g["skip_turns"]), (1, 0))

    def test_a_turn_with_a_legal_attack_and_none_taken_is_a_skip_turn(self):
        rows = [d("k", 3, True, False, 0), d("k", 3, False, False, 1), d("k", 5, True, False, 2), d("k", 5, True, True, 3)]
        g = se.per_game(rows)
        self.assertEqual((g["turns"], g["skip_turns"]), (2, 1))
        self.assertEqual([s["turn"] for s in g["skip_turn_list"]], [3])

    def test_a_turn_without_a_legal_attack_counts_nowhere(self):
        g = se.per_game([d("k", 3, False, False, 0), d("k", 3, False, False, 1)])
        self.assertEqual((g["points"], g["skips"], g["turns"], g["skip_turns"]), (0, 0, 0, 0))


def k(key, turn, attack_legal, taken_attack, km3_attacked, decision=0, km3_move=None):
    r = d(key, turn, attack_legal, taken_attack, decision)
    r["km3_attacked"] = km3_attacked
    r["km3_move"] = km3_move or ("Attack:Bite" if km3_attacked else "EndTurn")
    return r


class PreRegistered(unittest.TestCase):
    """Oct 12, the second follow-up: the pre-registration's own measure, a turn where km3 proposed an attack and the bot played
    something else, with no attack that turn."""

    def test_a_turn_where_km3_proposed_an_attack_and_none_was_played_is_a_preregistered_skip(self):
        rows = [k("k", 3, True, False, True, 0), k("k", 3, True, False, False, 1)]
        g = se.per_game(rows)
        self.assertEqual((g["km3_turns"], g["km3_skip_turns"]), (1, 1))

    def test_a_turn_where_km3_never_proposed_an_attack_is_not_counted(self):
        rows = [k("k", 3, True, False, False, 0), k("k", 3, True, False, False, 1)]
        g = se.per_game(rows)
        self.assertEqual((g["km3_turns"], g["km3_skip_turns"]), (0, 0))
        self.assertEqual((g["turns"], g["skip_turns"]), (1, 1))   # still a legal-attack skip turn

    def test_an_attack_later_that_turn_is_not_a_preregistered_skip(self):
        rows = [k("k", 3, True, False, True, 0), k("k", 3, True, True, True, 1)]
        g = se.per_game(rows)
        self.assertEqual((g["km3_turns"], g["km3_skip_turns"]), (1, 0))

    def test_the_skip_turn_list_carries_km3s_moves(self):
        rows = [k("k", 3, True, False, True, 0, km3_move="Attack:Bite"), k("k", 3, True, False, False, 1, km3_move="Retreat:1")]
        s = se.per_game(rows)["skip_turn_list"][0]
        self.assertEqual(s["km3_moves"], ["Attack:Bite", "Retreat:1"])
        self.assertTrue(s["km3_attacked"])

    def test_rows_without_a_km3_proposal_are_not_counted_as_proposals(self):
        r = d("k", 3, False, False, 0)
        r["km3_attacked"], r["km3_move"] = None, None
        g = se.per_game([r])
        self.assertEqual(g["km3_turns"], 0)


class Km3Identity(unittest.TestCase):
    def test_km3s_own_games_must_show_its_proposal_equal_to_its_move(self):
        rows = [k("k", 3, True, True, True, 0, km3_move="Attack:Bite"), k("k", 5, False, False, False, 1, km3_move="EndTurn")]
        self.assertEqual(se.km3_identity(rows), (2, 0))

    def test_a_disagreement_is_counted(self):
        rows = [k("k", 3, True, False, True, 0, km3_move="Attack:Bite")]
        self.assertEqual(se.km3_identity(rows), (1, 1))


class Ratio(unittest.TestCase):
    def test_pooled_share_and_interval(self):
        # two games: 1 of 2 and 3 of 4 -> 4/6; residuals (1 - 2*4/6)/3 and (3 - 4*4/6)/3
        share, half = se.ratio([(1, 2), (3, 4)])
        self.assertAlmostEqual(share, 4 / 6)
        r = [(1 - 2 * 4 / 6) / 3, (3 - 4 * 4 / 6) / 3]
        self.assertAlmostEqual(half, 1.96 * (sum(x * x for x in r) / (2 * 1)) ** 0.5)

    def test_no_points_is_none(self):
        self.assertEqual(se.ratio([(0, 0), (0, 0)]), (None, None))

    def test_paired_difference_uses_each_keys_two_games(self):
        a, b = [(1, 2), (3, 4), (0, 2)], [(0, 2), (1, 4), (0, 2)]
        diff, half = se.paired(a, b)
        sa, sb = 4 / 8, 1 / 8
        self.assertAlmostEqual(diff, sa - sb)
        m = 8 / 3
        ra = [(x - sa * n) / m for x, n in a]
        rb = [(x - sb * n) / m for x, n in b]
        dd = [p - q for p, q in zip(ra, rb)]
        self.assertAlmostEqual(half, 1.96 * (sum(x * x for x in dd) / (3 * 2)) ** 0.5)


class Keys(unittest.TestCase):
    def test_the_pair_key_drops_the_arm(self):
        self.assertEqual(se.pair_key("09-x|t-altaria|3|1|X"), "09-x|t-altaria|3|1")
        self.assertEqual(se.pair_key("09-x|t-altaria|3|1|ref"), "09-x|t-altaria|3|1")

    def test_groups_are_the_preregistrations(self):
        self.assertEqual(se.group("09-mega-manectric-heliolisk"), "fast")
        self.assertEqual(se.group("06-mega-blaziken-tournament-list"), "fast")
        self.assertEqual(se.group("10-xatu-oricorio-tr-weezing"), "fast")
        self.assertEqual(se.group("03-wailord-indeedee-wall"), "setup")
        self.assertEqual(se.group("01-muk-glimmora-kingambit-regigigas"), "setup")
        self.assertEqual(se.group("05-indeedee-stoutland"), "setup")
        self.assertEqual(se.group("draft-A-shark-tempo"), "middle")


class Gate(unittest.TestCase):
    def test_a_game_not_replayed_exactly_stops_the_comparison(self):
        checks = [{"key": "a|b|0|0|X", "replayed_exactly": True}, {"key": "a|b|0|1|X", "replayed_exactly": False}]
        with self.assertRaises(SystemExit):
            se.require_exact(checks, "candidate", 2)

    def test_a_missing_game_stops_the_comparison(self):
        with self.assertRaises(SystemExit):
            se.require_exact([{"key": "a|b|0|0|X", "replayed_exactly": True}], "candidate", 2)


if __name__ == "__main__":
    unittest.main()
