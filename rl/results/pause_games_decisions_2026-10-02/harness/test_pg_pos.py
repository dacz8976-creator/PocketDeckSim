"""Tests for pg_pos.rs (the cloud, Oct 13; Fable via Sonnet's read of the Oct 13 games): the position runner carries a side's
knock-out count (Kingambit's Overlord's Blade) and the Special Conditions of each Pokemon into the engine state before the bot moves,
and its normal output is unchanged.

  PG_POS=/path/to/pg_pos python3 -m unittest -v test_pg_pos      (from this folder)

The positions are two of Sonnet's real ones (010837 turn 11 with Kingambit; 030351 turn 5 with Dragonair Asleep), in test_oct13/."""
import json, os, subprocess, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "test_oct13")
BIN = os.environ.get("PG_POS", "pg_pos")
DECKS = ["--deck", f"KW261013_010837000={T}/KW261013_010837000.txt", "--deck", f"KW261013_030351000={T}/KW261013_030351000.txt"]


def run(*extra, positions=None):
    p = subprocess.run([BIN, "--positions", positions or f"{T}/positions.json", *DECKS, "--seeds", "1", *extra],
                       capture_output=True, text=True, timeout=600)
    assert p.returncode == 0, p.stderr[-2000:]
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]


class State(unittest.TestCase):
    """--dump-state prints, per position, what the built engine state holds (a line of its own; nothing else changes)."""

    @classmethod
    def setUpClass(cls):
        cls.lines = run("--dump-state")
        cls.state = {l["id"]: l for l in cls.lines if l.get("kind") == "state"}

    def test_the_knockout_count_is_set_from_the_position(self):
        self.assertEqual(self.state["oct13-kingambit-knockouts"]["knockouts"], [2, 0])

    def test_a_position_without_the_count_keeps_zero(self):
        self.assertEqual(self.state["oct13-kingambit-no-count"]["knockouts"], [0, 0])

    def test_sleep_is_set_on_the_pokemon_that_carries_it(self):
        s = self.state["oct13-dragonair-asleep"]["conditions"]
        self.assertEqual(s["me"], {"0": ["Asleep"]})
        self.assertEqual(s["opp"], {"0": ["Poisoned"]})

    def test_a_position_without_conditions_has_none(self):
        self.assertEqual(self.state["oct13-dragonair-awake"]["conditions"], {"me": {}, "opp": {}})

    def test_paralysis_and_confusion_are_carried_the_same_way(self):
        self.assertEqual(self.state["oct13-dragonair-paralyzed"]["conditions"]["me"], {"0": ["Paralyzed"]})
        self.assertEqual(self.state["oct13-dragonair-confused"]["conditions"]["me"], {"0": ["Confused"]})


class Play(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.free = {l["id"]: l for l in run() if l.get("kind") == "free"}

    def test_a_sleeping_active_neither_attacks_nor_retreats(self):
        plan = self.free["oct13-dragonair-asleep"]["plan"]
        self.assertFalse([m for m in plan if m.startswith("Attack:") or m.startswith("Retreat:")], plan)

    def test_a_paralyzed_active_neither_attacks_nor_retreats(self):
        plan = self.free["oct13-dragonair-paralyzed"]["plan"]
        self.assertFalse([m for m in plan if m.startswith("Attack:") or m.startswith("Retreat:")], plan)


class Format(unittest.TestCase):
    """The laptop's reading scripts read these lines: without --dump-state the output has the same kinds and keys as before."""

    def test_the_normal_output_is_unchanged(self):
        lines = run()
        self.assertEqual({l["kind"] for l in lines}, {"position", "free"})
        for l in lines:
            keys = {"position": {"kind", "id", "summary", "problems"}, "free": {"kind", "id", "seed", "plan", "cut"}}[l["kind"]]
            self.assertEqual(set(l), keys)
            if l["kind"] == "position":
                self.assertEqual(set(l["summary"]), {"turn_count", "points", "me", "opp", "stadium"})

    def test_an_unknown_condition_is_a_position_problem(self):
        bad = json.load(open(f"{T}/positions.json"))[3]
        bad = json.loads(json.dumps(bad))
        bad["id"] = "bad-condition"
        bad["me"]["board"][0]["conditions"] = ["Sleepy"]
        path = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pg_pos_bad_condition.json")
        json.dump([bad], open(path, "w"))
        pos = [l for l in run(positions=path) if l["kind"] == "position"][0]
        self.assertTrue(any("Sleepy" in p for p in pos["problems"]), pos["problems"])


if __name__ == "__main__":
    unittest.main()
