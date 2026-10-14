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


REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T14 = os.path.join(HERE, "test_oct14")


def decks_of(folder):
    return sum((["--deck", f"{f[:-4]}={os.path.join(folder, f)}"] for f in sorted(os.listdir(folder)) if f.endswith(".txt")), [])


def run_set(positions, deck_folder, *extra):
    p = subprocess.run([BIN, "--positions", positions, *decks_of(deck_folder), "--seeds", "1", *extra], capture_output=True, text=True,
                       timeout=1800)
    assert p.returncode == 0, p.stderr[-2000:]
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()]


def recorded_hp(pos):
    return {side: {str(i): b["hp"] for i, b in enumerate(pos[side]["board"]) if "hp" in b} for side in ("me", "opp")}


class StartingPlains(unittest.TestCase):
    """Oct 14 (the laptop's review of the Oct 12-13 positions, REVIEW_POSITIONS_laptop.md on main 373b41a6): pg_pos built each Pokemon's
    damage with no Stadium bonus and set the Stadium after the board, so under Starting Plains (+20 HP to every Basic) a damaged Basic
    gained 20 HP once the engine refreshed its bonuses. The state line's "hp" is each Pokemon's HP after the engine's own refresh."""

    def test_every_pokemon_under_starting_plains_has_its_recorded_hp(self):
        positions = json.load(open(f"{T14}/positions_plains.json"))
        state = {l["id"]: l for l in run_set(f"{T14}/positions_plains.json", T14, "--dump-state") if l["kind"] == "state"}
        for pos in positions:
            self.assertEqual(state[pos["id"]]["hp"], recorded_hp(pos), pos["id"])

    def test_the_damaged_druddigon_of_030351_t11_is_90_not_110(self):
        state = {l["id"]: l for l in run_set(f"{T14}/positions_plains.json", T14, "--dump-state") if l["kind"] == "state"}
        self.assertEqual(state["KW-261013_030351000-t11"]["hp"]["me"]["0"], 90)
        self.assertEqual(state["KW-261013_030351000-t11"]["hp"]["opp"]["0"], 10)     # the opponent's damaged Igglybuff, not 30


class PositionSets(unittest.TestCase):
    """The Oct 12 set (the 119 of ../../pause_positions_kx3_2026-10/run_ids.txt) and the Oct 13 v2 set (92) load with no problems, every
    Pokemon at its recorded HP."""

    def check(self, positions_path, deck_folder, ids_path, unreachable=()):
        """`unreachable`: (position id, side, slot) whose recorded HP is above the most the card can have in the engine (a data finding,
        not a runner one); there the engine's maximum is expected instead."""
        ids = set(open(ids_path).read().split())
        positions = [p for p in json.load(open(positions_path)) if p["id"] in ids]
        self.assertEqual(len(positions), len(ids))
        tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "pg_pos_set_" + os.path.basename(os.path.dirname(positions_path)) + ".json")
        json.dump(positions, open(tmp, "w"))
        lines = run_set(tmp, deck_folder, "--dump-state")
        pos_lines = [l for l in lines if l["kind"] == "position"]
        self.assertEqual(len(pos_lines), len(ids))
        self.assertEqual([(l["id"], l["problems"]) for l in pos_lines if l["problems"]], [])
        state = {l["id"]: l for l in lines if l["kind"] == "state"}
        wrong = []
        for p in positions:
            want = recorded_hp(p)
            for pid, side, slot, top in unreachable:
                if pid == p["id"]:
                    want[side][slot] = top
            if state[p["id"]]["hp"] != want:
                wrong.append((p["id"], state[p["id"]]["hp"], want))
        self.assertEqual(wrong, [])

    def test_the_oct12_set_of_119(self):
        d = os.path.join(REPO, "rl/results/pause_games_new_2026-10-12")
        self.check(f"{d}/positions_all.json", f"{d}/decks", os.path.join(REPO, "rl/results/pause_positions_kx3_2026-10/run_ids.txt"))

    def test_the_oct13_v2_set_of_92(self):
        d = os.path.join(REPO, "rl/results/pause_games_new_2026-10-13/v2")
        # 022530 t05 and t07: the opponent's Mega Scizor ex (printed 200 HP) with Giant Cape (+20) is recorded at 230; it can have at most 220
        self.check(f"{d}/positions_all.json", f"{d}/decks", f"{d}/run_ids.txt",
                   unreachable=[("KW-261013_022530000-t05", "opp", "3", 220), ("KW-261013_022530000-t07", "opp", "2", 220)])


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
