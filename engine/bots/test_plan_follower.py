import importlib.util
import os
import unittest

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan_follower_bot.py")
_SPEC = importlib.util.spec_from_file_location("plan_follower_bot", _PATH)
bot = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(bot)

ZERO = {"opponent_choices": 0, "chance_events": 0, "cards_left_deck_mine": 0, "cards_left_deck_opponent": 0}


def msg(ply, actions, **since):
    s = dict(ZERO)
    s.update(since)
    return {"ply": ply, "actions": [{"i": i, "text": str(a), "action": a} for i, a in enumerate(actions)],
            "pdl_since_last": s}


class ScriptedSource(bot.PlanSource):
    def __init__(self, plans):
        self.plans = list(plans)
        self.calls = 0

    def propose(self, m):
        self.calls += 1
        return list(self.plans.pop(0))


class PlanFollowerTests(unittest.TestCase):
    def test_p1_plan_played_in_order(self):
        src = ScriptedSource([["c", "a", "b"]])
        f = bot.PlanFollower(src)
        acts = ["a", "b", "c"]
        out = [f.decide(msg(p, acts)) for p in (1, 2, 3)]
        self.assertEqual([o[0] for o in out], [2, 0, 1])
        self.assertEqual(src.calls, 1)
        self.assertEqual([o[1]["played_from_saved_plan"] for o in out], [False, True, True])

    def _reask(self, **since):
        src = ScriptedSource([["a", "b"], ["b", "a"]])
        f = bot.PlanFollower(src)
        f.decide(msg(1, ["a", "b"]))
        i, rec = f.decide(msg(2, ["a", "b"], **since))
        self.assertEqual(src.calls, 2)
        self.assertEqual(i, 1)
        self.assertFalse(rec["played_from_saved_plan"])
        return rec

    def test_p2_draw_mine(self):
        self.assertEqual(self._reask(cards_left_deck_mine=1)["reask_reason"], "draw_mine")

    def test_p3_chance(self):
        self.assertEqual(self._reask(chance_events=2)["reask_reason"], "chance")

    def test_p4_opponent_choice(self):
        self.assertEqual(self._reask(opponent_choices=1)["reask_reason"], "opponent_choice")

    def test_p5_stale_step_never_played(self):
        src = ScriptedSource([["a", "x"], ["b", "c"]])
        f = bot.PlanFollower(src)
        f.decide(msg(1, ["a", "b", "c"]))
        i, rec = f.decide(msg(2, ["b", "c"]))
        self.assertEqual(rec["reask_reason"], "stale")
        self.assertEqual(i, 0)
        self.assertEqual(src.calls, 2)

    def test_p6_exhausted_plan_reproposes(self):
        src = ScriptedSource([["a"], ["b"]])
        f = bot.PlanFollower(src)
        f.decide(msg(1, ["a", "b"]))
        i, rec = f.decide(msg(2, ["a", "b"]))
        self.assertEqual(src.calls, 2)
        self.assertEqual(i, 1)
        self.assertIsNone(rec["reask_reason"])

    def test_p7_dummy_source_deterministic(self):
        m = msg(5, list("abcdefgh"))
        a = bot.DummyPlanSource(3).propose(m)
        b = bot.DummyPlanSource(3).propose(m)
        self.assertEqual(a, b)
        self.assertEqual(sorted(a), sorted(list("abcdefgh")))


if __name__ == "__main__":
    unittest.main()
