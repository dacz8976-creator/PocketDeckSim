"""Tests for skip_positions.py (the km3 check on the current engine). A stub stands in for pg_pos: it prints "free" lines whose plan
starts with the move the test names for each (position, seed), so the keep/drop rule is tested without an engine.

  python3 -m unittest -v test_skip_positions      (from this folder)
Optional end-to-end test: PG_POS=/path/to/pg_pos SKIP_E2E_POSITIONS=positions.json python3 -m unittest -v test_skip_positions.E2E"""
import json, os, stat, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skip_positions as sp

STUB = """#!/usr/bin/env python3
import json, sys
a = sys.argv
pos = json.load(open(a[a.index("--positions") + 1]))
seeds = [int(x) for x in a[a.index("--seeds") + 1].split(",")]
plans = json.load(open(%r))
for p in pos:
    if p["id"] in plans.get("problem", []):
        print(json.dumps({"kind": "position", "id": p["id"], "problems": ["more copies of X seen than the list holds"]}))
        continue
    print(json.dumps({"kind": "position", "id": p["id"], "problems": []}))
    for s in seeds:
        first = plans[p["id"]][(s - 1) %% len(plans[p["id"]])]
        print(json.dumps({"kind": "free", "id": p["id"], "seed": s, "plan": [first, "EndTurn"], "cut": "end of turn"}))
"""


def pos(i, km3):
    return {"id": i, "deck": "d", "filler": "o", "km3_move": km3}


class Rule(unittest.TestCase):
    def run_check(self, positions, plans, **kw):
        with tempfile.TemporaryDirectory() as t:
            pj, plj, stub = f"{t}/p.json", f"{t}/plans.json", f"{t}/pg_pos"
            json.dump(positions, open(pj, "w")); json.dump(plans, open(plj, "w"))
            open(stub, "w").write(STUB % plj); os.chmod(stub, os.stat(stub).st_mode | stat.S_IEXEC)
            return sp.check_positions(positions, {"d": "/x/d.txt", "o": "/x/o.txt"}, stub, **kw)

    def test_kept_when_km3_makes_the_recorded_move_in_most_of_12(self):
        kept, dropped = self.run_check([pos("a", "Attack:Pierce")], {"a": ["Attack:Pierce"] * 7 + ["EndTurn"] * 5})
        self.assertEqual([k["id"] for k in kept], ["a"])
        self.assertEqual(kept[0]["km3_agree"], 7)
        self.assertEqual(dropped, [])

    def test_dropped_and_listed_at_six_of_12(self):
        kept, dropped = self.run_check([pos("a", "Attack:Pierce")], {"a": ["Attack:Pierce"] * 6 + ["EndTurn"] * 6})
        self.assertEqual(kept, [])
        self.assertEqual(dropped[0]["id"], "a")
        self.assertIn("6 of 12", dropped[0]["reason"])

    def test_an_ability_label_matches_across_the_two_label_forms(self):
        self.assertTrue(sp.same_move("Ability:Volt Charge@2", "Ability@2"))
        self.assertFalse(sp.same_move("Ability:Volt Charge@2", "Ability@1"))
        self.assertTrue(sp.same_move("Attach:1Grass@0 zone", "Attach:1Grass@0 zone"))

    def test_a_position_pg_pos_cannot_build_is_dropped_with_its_problem(self):
        kept, dropped = self.run_check([pos("b", "EndTurn")], {"b": ["EndTurn"], "problem": ["b"]})
        self.assertEqual(kept, [])
        self.assertIn("more copies", dropped[0]["reason"])

    def test_a_position_without_a_recorded_move_is_dropped(self):
        kept, dropped = self.run_check([{"id": "c", "deck": "d", "filler": "o", "km3_move": None}], {"c": ["EndTurn"]})
        self.assertEqual(kept, [])
        self.assertIn("no km3_move", dropped[0]["reason"])

    def test_the_seeds_default_to_1_through_12(self):
        self.assertEqual(sp.SEEDS, list(range(1, 13)))


class E2E(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("PG_POS") and os.environ.get("SKIP_E2E_POSITIONS"), "needs PG_POS and SKIP_E2E_POSITIONS")
    def test_an_exported_position_is_built_by_pg_pos_without_problems(self):
        positions = json.load(open(os.environ["SKIP_E2E_POSITIONS"]))
        decks = json.load(open(os.environ["SKIP_E2E_DECKS"]))
        lines = sp.run_pg_pos(os.environ["PG_POS"], positions, decks, [1])
        for p in positions:
            self.assertEqual(lines[p["id"]]["problems"], [], p["id"])
            self.assertTrue(lines[p["id"]]["free"], p["id"])


if __name__ == "__main__":
    unittest.main()
