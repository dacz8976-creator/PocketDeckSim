"""Synthetic tests for rules switch 2's tightened rule (`tightened_rule.py`, this folder): PLAN.md precondition (b), "the classifier's
prefix fix" (the cloud, Oct 9). The rows are made here, not traced: each is what `vs_trace.rs` prints for a tick (the chosen move, the
offered moves, their number n, the turn and a hash of the state). A game is a list of such rows; "old" is the official engine's game,
"new" the candidate's.
Run: python3 -m unittest test_tightened_rule   (from this folder)"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tightened_rule as tr  # noqa: E402


def game(turns, prefix="s"):
    """One row per tick: `turns` gives each tick's turn; every tick offers two moves and the first is chosen."""
    return [{"chosen": f"m{t}", "offered": [f"m{t}", f"alt{t}"], "n": 2, "turn": turn, "state": f"{prefix}{t}"} for t, turn in enumerate(turns)]


def watch(**ticks):
    """A watch row: {counter: {"n", "first", "ticks"}}, as legality_scan's watch build writes an unkeyed counter."""
    return {name: {"n": len(t), "first": t[0] if t else None, "ticks": t} for name, t in ticks.items()}


TURNS = [1, 1, 2, 2, 3, 3, 3, 4, 4, 5]


class FirstDifference(unittest.TestCase):
    def test_lookahead_movegen_and_state_are_as_before(self):
        old = game(TURNS)
        new = game(TURNS)
        new[4] = dict(new[4], chosen="alt4")
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"]), ("lookahead", 4, 4))
        new = game(TURNS)
        new[4] = dict(new[4], offered=["m4", "alt4", "new4"], n=3)
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"]), ("movegen", 4, 4))
        new = game(TURNS)
        new[4] = dict(new[4], state="other")
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"]), ("state", 4, 3))

    def test_the_new_game_longer_k_is_its_first_extra_tick_and_the_cause_the_tick_before(self):
        old, new = game(TURNS[:6]), game(TURNS[:8])
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"], d["longer"]), ("length", 6, 5, "new"))
        self.assertEqual(d["y"], new[6])
        self.assertIsNone(d["x"])

    def test_the_new_game_shorter_k_is_the_old_games_first_extra_tick_and_the_cause_the_new_games_last(self):
        old, new = game(TURNS[:8]), game(TURNS[:6])
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"], d["longer"]), ("length", 6, 5, "old"))
        self.assertEqual(d["x"], old[6])
        self.assertIsNone(d["y"])

    def test_the_same_length_the_cause_is_the_last_tick(self):
        old, new = game(TURNS[:6]), game(TURNS[:6])
        d = tr.first_difference(old, new)
        self.assertEqual((d["kind"], d["k"], d["cause"], d["longer"]), ("length", 6, 5, None))


class CounterHits(unittest.TestCase):
    """A length difference is a board difference: the move at the cause tick had a different effect on the two engines."""

    def hits(self, old, new, w, **kw):
        d = tr.first_difference(old, new)
        return tr.counter_hits(w, list(w), new, d, **kw)

    def test_the_new_game_shorter_a_counter_at_its_last_tick_explains_it(self):
        # P2's case: a +20 hit back Knocks Out the last Pokemon, so the new game ends at the attack's tick (5) and the old one goes on.
        old, new = game(TURNS[:8]), game(TURNS[:6])
        self.assertEqual(self.hits(old, new, watch(attack_return_weakness=[5])), {"attack_return_weakness": [5]})

    def test_the_new_game_shorter_a_counter_earlier_in_the_same_turn_explains_it(self):
        old, new = game(TURNS[:8]), game(TURNS[:6])
        self.assertEqual(self.hits(old, new, watch(trap_territory_offer_changed=[4])), {"trap_territory_offer_changed": [4]})

    def test_the_new_game_shorter_with_no_counter_nothing_explains_it(self):
        old, new = game(TURNS[:8]), game(TURNS[:6])
        self.assertEqual(self.hits(old, new, watch(attack_return_weakness=[])), {})

    def test_a_counter_in_an_earlier_turn_never_explains_it(self):
        # k = 6 and the cause 5 are in turn 3; ticks 2 and 3 are in turn 2.
        old, new = game(TURNS[:8]), game(TURNS[:6])
        self.assertEqual(self.hits(old, new, watch(will_confused_attack=[2, 3])), {})

    def test_the_new_game_longer_a_counter_at_the_extra_tick_explains_it_as_in_v2(self):
        # The two pairing-31 games of step 8c: the Victory Star choice offered at the new game's first extra tick.
        old, new = game(TURNS[:6]), game(TURNS[:8])
        w = watch(vs_confused_choice_offered=[6], vs_confused_choice_chosen=[6])
        self.assertEqual(self.hits(old, new, w), {"vs_confused_choice_offered": [6], "vs_confused_choice_chosen": [6]})
        self.assertEqual(tr.extra_tick_hits(w, list(w), tr.first_difference(old, new)),
                         {"vs_confused_choice_offered": [6], "vs_confused_choice_chosen": [6]})

    def test_the_new_game_longer_a_counter_at_the_cause_tick_explains_it(self):
        old, new = game(TURNS[:6]), game(TURNS[:8])
        self.assertEqual(self.hits(old, new, watch(coin_own_side_split=[5])), {"coin_own_side_split": [5]})

    def test_the_same_length_a_counter_at_the_last_tick_explains_it(self):
        old, new = game(TURNS[:6]), game(TURNS[:6])
        self.assertEqual(self.hits(old, new, watch(attack_return_weakness=[5])), {"attack_return_weakness": [5]})

    def test_counters_after_the_first_difference_are_reported_apart(self):
        old, new = game(TURNS), game(TURNS)
        new[4] = dict(new[4], chosen="alt4")
        w = watch(perish_plain_hit_chosen=[5], guts_own_side_split=[4])
        self.assertEqual(self.hits(old, new, w), {"guts_own_side_split": [4]})
        self.assertEqual(self.hits(old, new, w, after=True), {"perish_plain_hit_chosen": [5]})

    def test_counter_hits_reads_the_turn_from_a_list_of_turns_only(self):
        # classify_8c.py keeps only the new game's turns ([{"turn": t}, ...]); k past them is read from the old game's row in d.
        old, new = game(TURNS[:8]), game(TURNS[:6])
        d = tr.first_difference(old, new)
        turns = [{"turn": r["turn"]} for r in new]
        self.assertEqual(tr.counter_hits(watch(attack_return_weakness=[5]), ["attack_return_weakness"], turns, d), {"attack_return_weakness": [5]})


INSTRUMENT_TEXT = '''
R2_COUNTERS = ["will_confused_attack", "coin_own_side_split", "trap_territory_offer_changed",
               "offgate_plain_attack_damage", "trap_territory_two_in_play", "attack_return_weakness"]
R2_KEYED = ["coin_queued_by_attack", "coin_plain_damage_by_attack", "offgate_by_attack", "offgate_return_by_source"]
'''


class Round2Reach(unittest.TestCase):
    """Round 2's exact counter names, keyed ones included ({attack: [ticks]}), as validate_v2.py's REACH was round 1's."""

    def test_the_exact_names_leave_out_the_off_gate_and_superset_counters(self):
        self.assertEqual(tr.round2_reach(INSTRUMENT_TEXT),
                         ("will_confused_attack", "coin_own_side_split", "trap_territory_offer_changed", "attack_return_weakness",
                          "coin_queued_by_attack", "coin_plain_damage_by_attack"))

    def test_a_keyed_counter_is_flattened_and_a_first_round_coin_site_is_left_out(self):
        row = {"will_confused_attack": {"n": 1, "first": 3, "ticks": [3]},
               "coin_queued_by_attack": {"Wild Swing": [7, 9], "Chase Order": [4], "Diving Icicles": [5]},
               "coin_plain_damage_by_attack": {"Earthquake": [2], "Tongue Whip": [6]}}
        flat = tr.reach_row(row)
        self.assertEqual(flat["coin_queued_by_attack"], {"ticks": [7, 9]})
        self.assertEqual(flat["coin_plain_damage_by_attack"], {"ticks": [2, 6]})
        self.assertEqual(flat["will_confused_attack"], row["will_confused_attack"])

    def test_a_keyed_counter_missing_from_the_row_is_empty(self):
        self.assertEqual(tr.reach_row({})["coin_queued_by_attack"], {"ticks": []})


if __name__ == "__main__":
    unittest.main()
