"""Synthetic tests for rules switch 2's tightened rule (`tightened_rule.py`, this folder): PLAN.md precondition (b), "the classifier's
prefix fix" (the cloud, Oct 9). The rows are made here, not traced: each is what `vs_trace.rs` prints for a tick (the chosen move, the
offered moves, their number n, the turn and a hash of the state). A game is a list of such rows; "old" is the official engine's game,
"new" the candidate's.
Also (Oct 9, later): the probe's three RESULT lines read together, the lookahead verdict with round 2's kinds, the golden check, and a
hand-off row's counters as a watch row, which the switch-2 copies of classify_8c.py and coin_lookahead.py (this folder) share.
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


# coin_probe v2's output at step 8b's km3 pairing 35, deal 2, tick 89 (early_warning_8b_ticks_r2.txt), its lines cut short.
PROBE_OUT = """deal 2, tick 89:
  mover seat 0, turn 13; Active Mega Sharpedo ex; 12 offered moves
  QUEUED: a queued coin-path choice is offered after 3 move(s): INSIDE THE SEARCH (at the leaf, but a pure frame: resolved without a ply)
    after [Retreat(2) ; Attack(Attack { energy_required: [Water, Water], title: "Wild Swing", fixed_damage: 20,... ; DiscardOwnBenchedThenDamage { in_play_idxs: [], damage: 20 }] offers ApplyQueuedAttackDamage { attack: Attack { title: "Wild Swing" } }
RESULT queued=3 cut=none free=true
RESULT_P2 ret=none
RESULT_R2 will=none vs=none trap=none own=none guts=none plain=none perish=none trapleaf=none
"""
NONE_R2 = {"will": None, "vs": None, "trap": None, "own": None, "guts": None, "plain": None, "perish": None}


def probe(queued=None, cut=None, free=False, ret=None, trapleaf=None, **r2):
    return {"queued": queued, "cut": cut, "free": free, "ret": ret, "r2": dict(NONE_R2, **r2), "trapleaf": trapleaf}


class ProbeOutput(unittest.TestCase):
    """coin_probe v2's three RESULT lines, read together: QUEUED and CUT (the coin rounds), RETURN (P2) and round 2's kinds."""

    def test_the_three_result_lines_and_the_attack_on_the_queued_path(self):
        c = tr.parse_probe(PROBE_OUT)
        self.assertEqual((c["queued"], c["cut"], c["free"], c["ret"], c["trapleaf"]), (3, None, True, None, None))
        self.assertEqual(c["r2"], NONE_R2)
        self.assertEqual(c["queued_attacks"], ["Wild Swing"])
        self.assertNotIn("truncated", c)

    def test_round_two_fields_and_a_stopped_search(self):
        out = PROBE_OUT.replace("will=none", "will=2").replace("trapleaf=none", "trapleaf=3") + "  (the search stopped at 200000 nodes)\n"
        c = tr.parse_probe(out)
        self.assertEqual((c["r2"]["will"], c["trapleaf"], c["truncated"]), (2, 3, True))

    def test_a_probe_without_round_two_s_line_is_refused(self):
        # An older probe build (before precondition (a)) would read as "nothing found" in every round-2 field.
        with self.assertRaises(ValueError):
            tr.parse_probe(PROBE_OUT.replace(PROBE_OUT.splitlines()[-1], ""))

    def test_nothing_found(self):
        self.assertTrue(tr.nothing_found(probe()))
        self.assertFalse(tr.nothing_found(probe(trapleaf=2)))
        self.assertFalse(tr.nothing_found(probe(perish=4)))
        self.assertFalse(tr.nothing_found(probe(cut=2)))


class LookaheadVerdict(unittest.TestCase):
    """A lookahead difference with no counter: (the verdict, the verdict under the strict reading). The strict reading doesn't count a
    queued coin-path choice or cut that may be a first-round site, which both engines build (`round2_queued` False)."""

    def v(self, c, round2_queued=False):
        return tr.lookahead_verdict(c, round2_queued)

    def test_nothing_found_is_unexplained(self):
        self.assertEqual(self.v(probe()), ("UNEXPLAINED", "UNEXPLAINED"))

    def test_a_return_ply_explains_it(self):
        self.assertEqual(self.v(probe(ret=2)), (tr.BOTH_HALVES, tr.BOTH_HALVES))

    def test_a_round_two_kind_inside_the_search_explains_it(self):
        for kind in NONE_R2:
            self.assertEqual(self.v(probe(**{kind: 3})), (tr.BOTH_HALVES, tr.BOTH_HALVES), kind)

    def test_a_round_two_kind_only_beyond_the_search_needs_a_judgment(self):
        self.assertEqual(self.v(probe(trap=4)), (tr.JUDGMENT, tr.JUDGMENT))

    def test_trapleaf_alone_needs_a_judgment(self):
        self.assertEqual(self.v(probe(trapleaf=3)), (tr.JUDGMENT, tr.JUDGMENT))

    def test_a_queued_choice_at_a_later_round_site_explains_it(self):
        self.assertEqual(self.v(probe(queued=1), round2_queued=True), (tr.BOTH_HALVES, tr.BOTH_HALVES))

    def test_a_queued_choice_that_may_be_a_first_round_site_is_unexplained_under_the_strict_reading(self):
        self.assertEqual(self.v(probe(queued=1)), (tr.BOTH_HALVES, "UNEXPLAINED"))
        self.assertEqual(self.v(probe(cut=2)), (tr.BOTH_HALVES, "UNEXPLAINED"))

    def test_a_queued_choice_only_at_the_leaf_of_a_mixed_frame_needs_a_judgment(self):
        self.assertEqual(self.v(probe(queued=3), round2_queued=True), (tr.JUDGMENT, tr.JUDGMENT))
        self.assertEqual(self.v(probe(queued=3)), (tr.JUDGMENT, "UNEXPLAINED"))

    def test_a_queued_choice_at_the_leaf_of_a_pure_frame_explains_it(self):
        self.assertEqual(self.v(probe(queued=3, free=True), round2_queued=True), (tr.BOTH_HALVES, tr.BOTH_HALVES))

    def test_the_strongest_finding_decides(self):
        self.assertEqual(self.v(probe(queued=3, trapleaf=2, will=1)), (tr.BOTH_HALVES, tr.BOTH_HALVES))


class Golden(unittest.TestCase):
    """At the last tick of an exact counter that explains a game on the board, the probe must find that counter's kind on the table."""

    def test_each_round_two_counter_needs_its_kind_at_ply_one(self):
        for name, kind in tr.R2_COUNTER_KIND.items():
            self.assertTrue(tr.golden_ok(name, probe(**{kind: 1})), name)
            self.assertFalse(tr.golden_ok(name, probe(**{kind: 2})), name)
            self.assertFalse(tr.golden_ok(name, probe()), name)

    def test_return_and_queued(self):
        self.assertTrue(tr.golden_ok("attack_return_weakness", probe(ret=1)))
        self.assertFalse(tr.golden_ok("attack_return_weakness", probe(ret=2)))
        self.assertTrue(tr.golden_ok("coin_queued_by_attack", probe(queued=0)))
        self.assertTrue(tr.golden_ok("coin_queued_by_attack", probe(cut=1)))
        self.assertFalse(tr.golden_ok("coin_queued_by_attack", probe(queued=1)))

    def test_a_counter_the_probe_has_no_condition_for_has_no_golden_check(self):
        for name in ("luxury_coin_opp_stadium", "fossil_item_lock"):
            self.assertIsNone(tr.golden_ok(name, probe()))

    def test_every_exact_name_but_those_two_has_a_golden_check(self):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "coin_prevention_repair_2026-09-30", "instrument_scan.py")) as f:
            text = f.read()
        missing = [n for n in tr.round2_reach(text) if tr.golden_ok(n, probe()) is None]
        self.assertEqual(missing, ["luxury_coin_opp_stadium", "fossil_item_lock"])


class WatchFromCounters(unittest.TestCase):
    """A hand-off row's exact counters ({name: [ticks]}, a keyed one {name: {key: [ticks]}}) as the watch row counter_hits reads."""

    def test_plain_and_keyed_counters(self):
        ex = {"will_confused_attack": [3], "coin_queued_by_attack": {"Wild Swing": [7], "Chase Order": [4]}}
        w = tr.watch_from_counters(ex, ("will_confused_attack", "coin_own_side_split", "coin_queued_by_attack", "coin_plain_damage_by_attack"))
        self.assertEqual(w, {"will_confused_attack": {"ticks": [3]}, "coin_own_side_split": {"ticks": []},
                             "coin_queued_by_attack": {"ticks": [7]}, "coin_plain_damage_by_attack": {"ticks": []}})

    def test_a_keyed_counter_given_as_a_list_is_refused(self):
        # Its first-round keys could not be left out.
        with self.assertRaises(ValueError):
            tr.watch_from_counters({"coin_queued_by_attack": [4, 7]}, ("coin_queued_by_attack",))


class BoardHits(unittest.TestCase):
    """counter_hits and extra_tick_hits together: what explains a game on the board, whatever its kind."""

    def test_the_new_game_shorter(self):
        old, new = game(TURNS[:8]), game(TURNS[:6])
        d = tr.first_difference(old, new)
        self.assertEqual(tr.board_hits(watch(attack_return_weakness=[5]), ["attack_return_weakness"], new, d), {"attack_return_weakness": [5]})

    def test_the_new_game_longer_at_the_extra_tick(self):
        old, new = game(TURNS[:6]), game(TURNS[:7])
        d = tr.first_difference(old, new)
        # tick 6 is turn 3 here, as k is: counter_hits and extra_tick_hits both read it, and it is listed once
        self.assertEqual(tr.board_hits(watch(vs_block_coin_built=[6]), ["vs_block_coin_built"], new, d), {"vs_block_coin_built": [6]})

    def test_a_counter_in_an_earlier_turn_never_explains_it(self):
        old, new = game(TURNS[:8]), game(TURNS[:6])
        d = tr.first_difference(old, new)
        self.assertEqual(tr.board_hits(watch(guts_own_side_split=[1]), ["guts_own_side_split"], new, d), {})


if __name__ == "__main__":
    unittest.main()
