"""Tests for split_collect.py, the split-run collector (the cloud, Oct 9; rl/results/split_runs_2026-10-09/README.md).
Run: python3 -m unittest test_split_collect   (from rl/strength/)"""
import hashlib, json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import split_collect as sc  # noqa: E402

PROGRAM_SHA = "ab" * 32


SELF = {"km3": "selfcheck pilot=km3 games=12 seat0_wins=8 seat1_wins=4 ties=0 turns=127 digest=81b572198c04d5d1",
        "k3": "selfcheck pilot=k3 games=12 seat0_wins=7 seat1_wins=5 ties=0 turns=130 digest=0123456789abcdef"}


def manifest(decks=("d1", "d2", "d3"), opps=("o1",), deals=2, seats=(0, 1), pilot="km3", reference="k3", program_sha256=PROGRAM_SHA):
    return {"name": "t", "pilot": pilot, "reference": reference,
            "decks": [{"name": d, "path": f"decks/{d}.txt", "sha256": "0" * 64} for d in decks],
            "opponents": [{"name": o, "path": f"decks/{o}.txt", "sha256": "0" * 64} for o in opps],
            "deals": deals, "seats": list(seats), "seed_base": 21_000_000_000, "pair_stride": 10_000,
            "program_sha256": program_sha256, "engine": "main-8626a35, engine tree 38af8b0cc4f3", "planned_games": None,
            "selfcheck": dict(SELF)}


def record(job, winner="deck", wall=1.25, started="2026-10-09T22:00:00Z", ms=(3.5, 4.0)):
    """A game record as the harness writes it (rl/strength/src/main.rs), with its timing fields."""
    return {"key": job["key"], "deck": job["deck"], "opp": job["opp"], "deal": job["deal"], "seat": job["seat"], "arm": job["arm"],
            "seed": job["seed"], "pilot_deck": job["pilot_deck"], "pilot_opp": job["pilot_opp"], "first": "deck", "winner": winner,
            "points": [3, 1], "turns": 14, "plies": 120, "wall_s": wall,
            "moves_deck": {"n": len(ms), "total_s": round(sum(ms) / 1000, 3), "ms": list(ms)},
            "moves_opp": {"n": 1, "total_s": 0.002, "ms": [2.0]}, "started_at": started,
            "log": [{"t": 1, "o": 1, "a": "EndTurn", "n": 1, "ms": ms[0], "p": [0, 0], "act": "", "b": 0}]}


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write_manifest(self, m):
        path = os.path.join(self.d, "manifest.json")
        with open(path, "w") as f:
            json.dump(m, f, indent=1)
        return path

    def worker(self, name, mpath, records, only=(), program_sha256=PROGRAM_SHA, manifest_sha256=None, tail="", selfcheck=None, engine_tree="38af8b0"):
        w = os.path.join(self.d, name)
        os.makedirs(w)
        with open(os.path.join(w, "games.jsonl"), "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            f.write(tail)
        stamp = {"worker": name, "manifest_sha256": manifest_sha256 or sc.sha256_file(mpath), "program_sha256": program_sha256,
                 "only_deck": list(only), "engine_tree": engine_tree}
        if selfcheck is not None:
            stamp["selfcheck"] = selfcheck
        with open(os.path.join(w, "worker.json"), "w") as f:
            json.dump(stamp, f)
        return w


class ExpectedGames(unittest.TestCase):
    def test_the_job_list_is_the_harnesss_order_keys_seeds_and_pilots(self):
        m = manifest(decks=("a", "b"), opps=("b", "c"), deals=2, seats=(0, 1))
        jobs = sc.expected_jobs(m)
        # a v b, a v c, then b v c (b v b skipped); deal, then seat, then arm ref before X
        self.assertEqual(len(jobs), 3 * 2 * 2 * 2)
        self.assertEqual([j["key"] for j in jobs[:4]], ["a|b|0|0|ref", "a|b|0|0|X", "a|b|0|1|ref", "a|b|0|1|X"])
        self.assertEqual(jobs[-1]["key"], "b|c|1|1|X")
        # seed = seed_base + (deck index * 1000 + opponent index) * pair_stride + deal, with the manifests' indexes
        self.assertEqual(jobs[0]["seed"], 21_000_000_000)
        self.assertEqual([j for j in jobs if j["key"] == "b|c|1|0|ref"][0]["seed"], 21_000_000_000 + (1 * 1000 + 1) * 10_000 + 1)
        x, ref = jobs[1], jobs[0]
        self.assertEqual((x["pilot_deck"], x["pilot_opp"]), ("km3", "k3"))
        self.assertEqual((ref["pilot_deck"], ref["pilot_opp"]), ("k3", "k3"))

    def test_a_missing_pair_stride_is_the_harnesss_default(self):
        m = manifest(decks=("a",), opps=("c",), deals=1, seats=(0,))
        del m["pair_stride"]
        m["seed_base"] = 5
        self.assertEqual(sc.expected_jobs(m)[0]["seed"], 5)
        m2 = manifest(decks=("z", "a"), opps=("c",), deals=1, seats=(0,))
        del m2["pair_stride"]
        m2["seed_base"] = 5
        self.assertEqual(sc.expected_jobs(m2)[2]["seed"], 5 + 1000 * 10_000)


class Content(unittest.TestCase):
    def test_timing_fields_are_left_out(self):
        job = sc.expected_jobs(manifest())[0]
        a = record(job, wall=1.0, started="2026-10-09T22:00:00Z", ms=(1.0, 2.0))
        b = record(job, wall=9.0, started="2026-10-10T01:00:00Z", ms=(7.0, 8.0))
        self.assertEqual(sc.content(a), sc.content(b))
        self.assertNotIn("wall_s", sc.content(a))
        self.assertEqual(sc.content(a)["moves_deck"], {"n": 2})

    def test_a_different_result_is_different_content(self):
        job = sc.expected_jobs(manifest())[0]
        self.assertNotEqual(sc.content(record(job, winner="deck")), sc.content(record(job, winner="opp")))

    def test_a_different_number_of_decisions_is_different_content(self):
        job = sc.expected_jobs(manifest())[0]
        self.assertNotEqual(sc.content(record(job, ms=(1.0, 2.0))), sc.content(record(job, ms=(1.0, 2.0, 3.0))))


class Merge(Scratch):
    def setUp(self):
        super().setUp()
        self.m = manifest()
        self.mpath = self.write_manifest(self.m)
        self.jobs = sc.expected_jobs(self.m)
        self.by_deck = {d: [j for j in self.jobs if j["deck"] == d] for d in ("d1", "d2", "d3")}

    def two_workers(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in reversed(self.by_deck["d1"] + self.by_deck["d3"])], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        return [w1, w2]

    def test_a_clean_split_merges_complete_in_the_canonical_order(self):
        res = sc.collect(self.mpath, self.two_workers())
        self.assertTrue(res["complete"])
        self.assertEqual(res["problems"], [])
        self.assertEqual([json.loads(l)["key"] for l in res["lines"]], [j["key"] for j in self.jobs])
        self.assertEqual({w["worker"]: w["games"] for w in res["workers"]}, {"w1": 16, "w2": 8})

    def test_the_merged_lines_are_the_workers_lines_byte_for_byte(self):
        workers = self.two_workers()
        res = sc.collect(self.mpath, workers)
        source = set()
        for w in workers:
            with open(os.path.join(w, "games.jsonl")) as f:
                source |= set(f.read().splitlines())
        self.assertEqual(set(res["lines"]), source)

    def test_the_outputs_are_written_and_the_exit_status_says_complete(self):
        workers = self.two_workers()
        out = os.path.join(self.d, "merged")
        code = sc.main(["merge", "--manifest", self.mpath, "--out", out] + sum((["--worker", w] for w in workers), []))
        self.assertEqual(code, 0)
        with open(os.path.join(out, "games.jsonl")) as f:
            self.assertEqual(len(f.read().splitlines()), 24)
        with open(os.path.join(out, "MERGE_RECORD.md")) as f:
            text = f.read()
        self.assertIn("COMPLETE", text)
        self.assertIn("w1", text)
        self.assertIn(PROGRAM_SHA, text)

    def test_a_missing_game_is_flagged_and_the_merge_is_incomplete(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"][1:]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertFalse(res["complete"])
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("missing", self.by_deck["d3"][0]["key"])])
        self.assertEqual(len(res["lines"]), 23)
        out = os.path.join(self.d, "merged")
        self.assertEqual(sc.main(["merge", "--manifest", self.mpath, "--out", out, "--worker", w1, "--worker", w2]), 1)
        with open(os.path.join(out, "MERGE_RECORD.md")) as f:
            text = f.read()
        self.assertIn("INCOMPLETE", text)
        self.assertIn(self.by_deck["d3"][0]["key"], text)

    def test_a_duplicate_with_the_same_content_is_flagged_and_kept_once(self):
        workers = self.two_workers()
        extra = self.worker("w3", self.mpath, [record(self.by_deck["d2"][0], wall=7.0, started="2026-10-10T00:00:00Z")], only=("d2",))
        res = sc.collect(self.mpath, workers + [extra])
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("duplicate", self.by_deck["d2"][0]["key"])])
        self.assertIn("same content", res["problems"][0]["detail"])
        self.assertFalse(res["complete"])
        self.assertEqual(len(res["lines"]), 24)
        self.assertEqual(json.loads(res["lines"][[j["key"] for j in self.jobs].index(self.by_deck["d2"][0]["key"])])["wall_s"], 1.25)

    def test_a_duplicate_with_different_content_is_a_conflict_and_neither_is_kept(self):
        workers = self.two_workers()
        extra = self.worker("w3", self.mpath, [record(self.by_deck["d2"][0], winner="opp")], only=("d2",))
        res = sc.collect(self.mpath, workers + [extra])
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("conflict", self.by_deck["d2"][0]["key"])])
        self.assertEqual(len(res["lines"]), 23)

    def test_a_duplicate_inside_one_worker_is_flagged(self):
        recs = [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]]
        w1 = self.worker("w1", self.mpath, recs + [recs[0]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([p["kind"] for p in res["problems"]], ["duplicate"])

    def test_a_game_with_other_inputs_is_flagged_and_left_out(self):
        bad = record(self.by_deck["d2"][1])
        bad["seed"] += 1
        bad2 = record(self.by_deck["d2"][2])
        bad2["pilot_deck"] = "kog3"
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(self.by_deck["d2"][0]), bad, bad2] + [record(j) for j in self.by_deck["d2"][3:]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        kinds = sorted((p["kind"], p["key"]) for p in res["problems"])
        self.assertIn(("mismatch", bad["key"]), kinds)
        self.assertIn(("mismatch", bad2["key"]), kinds)
        self.assertIn(("missing", bad["key"]), kinds)
        self.assertIn("seed", [p for p in res["problems"] if p["kind"] == "mismatch" and p["key"] == bad["key"]][0]["detail"])
        self.assertEqual(len(res["lines"]), 22)

    def test_a_game_not_in_the_registration_is_flagged(self):
        stray = record(self.jobs[0])
        stray["key"] = "d9|o1|0|0|X"
        stray["deck"] = "d9"
        workers = self.two_workers()
        extra = self.worker("w3", self.mpath, [stray], only=("d9",))
        res = sc.collect(self.mpath, workers + [extra])
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("unexpected", "d9|o1|0|0|X")])

    def test_a_game_outside_the_workers_slice_is_flagged(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1",))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual({p["kind"] for p in res["problems"]}, {"outside slice"})
        self.assertEqual(len([p for p in res["problems"] if p["kind"] == "outside slice"]), 8)

    def test_a_worker_on_another_registration_or_program_is_flagged(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), manifest_sha256="cd" * 32)
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32)
        res = sc.collect(self.mpath, [w1, w2])
        kinds = sorted((p["kind"], p.get("worker")) for p in res["problems"])
        self.assertEqual(kinds, [("manifest", "w1"), ("program", "w2")])
        self.assertFalse(res["complete"])

    def test_a_rebuilt_program_with_the_registrations_self_checks_is_a_note_not_a_problem(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32, selfcheck=dict(SELF))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual(res["problems"], [])
        self.assertTrue(res["complete"])
        self.assertEqual([(n["kind"], n["worker"]) for n in res["notes"]], [("rebuilt", "w2")])
        self.assertIn("rebuilt", sc.merge_record(res))

    def test_a_rebuilt_program_with_another_self_check_is_a_problem(self):
        other = dict(SELF, k3=SELF["k3"].replace("0123456789abcdef", "fedcba9876543210"))
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32, selfcheck=other)
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"]], [("program", "w2")])
        self.assertIn("k3", res["problems"][0]["detail"])

    def test_a_rebuilt_program_missing_a_pilots_self_check_is_a_problem(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32, selfcheck={"km3": SELF["km3"]})
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"]], [("program", "w2")])

    def test_a_worker_on_another_engine_tree_is_flagged(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), engine_tree="1234567abcdef")
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"]], [("engine", "w1")])

    def test_with_no_program_in_the_manifest_the_workers_must_agree(self):
        m = manifest(program_sha256=None)
        mpath = self.write_manifest(m)
        jobs = sc.expected_jobs(m)
        w1 = self.worker("w1", mpath, [record(j) for j in jobs if j["deck"] != "d2"], only=("d1", "d3"), program_sha256="11" * 32)
        w2 = self.worker("w2", mpath, [record(j) for j in jobs if j["deck"] == "d2"], only=("d2",), program_sha256="22" * 32)
        res = sc.collect(mpath, [w1, w2])
        self.assertEqual([p["kind"] for p in res["problems"]], ["program"])

    def test_a_worker_without_its_stamp_is_flagged(self):
        workers = self.two_workers()
        os.remove(os.path.join(workers[1], "worker.json"))
        res = sc.collect(self.mpath, workers)
        self.assertEqual([(p["kind"], p.get("worker")) for p in res["problems"]], [("stamp", "w2")])

    def test_an_unreadable_last_line_is_reported(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), tail='{"key": "d1|o1|0')
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p.get("worker")) for p in res["problems"]], [("unreadable", "w1")])
        self.assertEqual(len(res["lines"]), 24)

    def test_errored_games_are_listed(self):
        workers = self.two_workers()
        with open(os.path.join(workers[1], "errors.jsonl"), "w") as f:
            f.write(json.dumps({"key": self.by_deck["d2"][0]["key"], "error": "boom", "at": "x"}) + "\n")
        res = sc.collect(self.mpath, workers)
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("error", self.by_deck["d2"][0]["key"])])


class Compare(Scratch):
    def files(self, change=None):
        m = manifest()
        jobs = sc.expected_jobs(m)
        a = os.path.join(self.d, "a.jsonl")
        b = os.path.join(self.d, "b.jsonl")
        with open(a, "w") as f:
            for j in jobs:
                f.write(json.dumps(record(j)) + "\n")
        with open(b, "w") as f:
            for i, j in enumerate(jobs):
                r = record(j, wall=3.0, started="2026-10-11T00:00:00Z", ms=(9.0, 9.5))
                if change == i:
                    r["turns"] += 1
                f.write(json.dumps(r) + "\n")
        return a, b

    def test_equal_content_game_for_game(self):
        a, b = self.files()
        self.assertEqual(sc.main(["compare", a, b]), 0)

    def test_one_different_game_fails(self):
        a, b = self.files(change=5)
        self.assertEqual(sc.main(["compare", a, b]), 1)


class Stamp(Scratch):
    def test_the_stamp_records_the_manifest_and_program_sha256(self):
        mpath = self.write_manifest(manifest())
        prog = os.path.join(self.d, "strength")
        with open(prog, "wb") as f:
            f.write(b"binary")
        out = os.path.join(self.d, "w1")
        self.assertEqual(sc.main(["stamp", "--manifest", mpath, "--program", prog, "--worker", "w1", "--out", out,
                                  "--only-deck", "d1", "--only-deck", "d3"]), 0)
        with open(os.path.join(out, "worker.json")) as f:
            s = json.load(f)
        self.assertEqual(s["manifest_sha256"], sc.sha256_file(mpath))
        self.assertEqual(s["program_sha256"], hashlib.sha256(b"binary").hexdigest())
        self.assertEqual(s["only_deck"], ["d1", "d3"])
        self.assertEqual(s["worker"], "w1")

    def test_the_stamp_refuses_a_deck_not_in_the_registration(self):
        mpath = self.write_manifest(manifest())
        prog = os.path.join(self.d, "strength")
        with open(prog, "wb") as f:
            f.write(b"binary")
        self.assertEqual(sc.main(["stamp", "--manifest", mpath, "--program", prog, "--worker", "w1", "--out", os.path.join(self.d, "w"),
                                  "--only-deck", "nope"]), 2)


class CommandLine(unittest.TestCase):
    def test_the_script_runs_as_a_program(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "split_collect.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr.lower())


if __name__ == "__main__":
    unittest.main()
