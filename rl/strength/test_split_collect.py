"""Tests for split_collect.py, the split-run collector (the cloud, Oct 9; rl/results/split_runs_2026-10-09/README.md).
Run: python3 -m unittest test_split_collect   (from rl/strength/)"""
import hashlib, json, os, subprocess, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import split_collect as sc  # noqa: E402

PROGRAM_SHA = "ab" * 32
STAMPED = "2026-10-09T21:00:00Z"   # before every record's started_at
SEALED = "2026-10-11T00:00:00Z"    # after them


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


def reseal(w):
    """Seals a worker folder again after a test changed its files during 'play'."""
    with open(os.path.join(w, "worker_seal.json")) as f:
        seal = json.load(f)
    seal["games_sha256"] = sc.sha256_file(os.path.join(w, "games.jsonl"))
    errs = os.path.join(w, "errors.jsonl")
    seal["errors_sha256"] = sc.sha256_file(errs) if os.path.isfile(errs) else None
    with open(os.path.join(w, "worker_seal.json"), "w") as f:
        json.dump(seal, f)


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

    def worker(self, name, mpath, records, only=(), program_sha256=PROGRAM_SHA, manifest_sha256=None, tail="", selfcheck=None, engine_tree="38af8b0",
               stamped_at=STAMPED, decks=None, build_sha=None, seal=True, seal_changes=None):
        """A worker folder as the recipe leaves it: stamped before play (worker.json), played (games.jsonl), sealed after (worker_seal.json)."""
        w = os.path.join(self.d, name)
        os.makedirs(w)
        with open(os.path.join(w, "games.jsonl"), "w") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            f.write(tail)
        with open(mpath) as f:
            m = json.load(f)
        if decks is None:
            decks = {d["name"]: d["sha256"] for d in m["decks"] + m["opponents"]}
        stamp = {"worker": name, "manifest_sha256": manifest_sha256 or sc.sha256_file(mpath), "program_sha256": program_sha256,
                 "only_deck": list(only), "engine_tree": engine_tree, "stamped_at": stamped_at, "decks_sha256": decks,
                 "build_record_program_sha256": build_sha or program_sha256}
        if stamped_at is None:
            del stamp["stamped_at"]
        if selfcheck is not None:
            stamp["selfcheck"] = selfcheck
        with open(os.path.join(w, "worker.json"), "w") as f:
            json.dump(stamp, f)
        if seal:
            sealed = {"worker": name, "sealed_at": SEALED, "games_sha256": sc.sha256_file(os.path.join(w, "games.jsonl")), "errors_sha256": None,
                      "manifest_sha256": stamp["manifest_sha256"], "program_sha256": program_sha256, "decks_sha256": dict(decks)}
            sealed.update(seal_changes or {})
            with open(os.path.join(w, "worker_seal.json"), "w") as f:
                json.dump(sealed, f)
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
        self.assertEqual({p["kind"] for p in res["problems"]}, {"outside slice", "missing"})
        self.assertEqual(len([p for p in res["problems"] if p["kind"] == "outside slice"]), 8)
        # F1: a game a worker played outside its slice is not merged
        self.assertEqual(len([p for p in res["problems"] if p["kind"] == "missing"]), 8)
        self.assertEqual(len(res["lines"]), 16)

    def test_a_worker_on_another_registration_or_program_is_flagged(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), manifest_sha256="cd" * 32)
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32)
        res = sc.collect(self.mpath, [w1, w2])
        kinds = sorted((p["kind"], p.get("worker")) for p in res["problems"] if p["kind"] != "missing")
        self.assertEqual(kinds, [("manifest", "w1"), ("program", "w2")])
        self.assertEqual(res["lines"], [])   # F1: neither worker's games are merged
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
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"] if p["kind"] != "missing"], [("program", "w2")])
        self.assertIn("k3", res["problems"][0]["detail"])
        self.assertEqual(len(res["lines"]), 16)   # F1: w2's 8 games are not merged

    def test_a_rebuilt_program_missing_a_pilots_self_check_is_a_problem(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32, selfcheck={"km3": SELF["km3"]})
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"] if p["kind"] != "missing"], [("program", "w2")])

    def test_a_worker_on_another_engine_tree_is_flagged(self):
        w1 = self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), engine_tree="1234567abcdef")
        w2 = self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(self.mpath, [w1, w2])
        self.assertEqual([(p["kind"], p["worker"]) for p in res["problems"] if p["kind"] != "missing"], [("engine", "w1")])

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
        reseal(workers[1])   # the errors file is written during play, before the seal
        res = sc.collect(self.mpath, workers)
        self.assertEqual([(p["kind"], p["key"]) for p in res["problems"]], [("error", self.by_deck["d2"][0]["key"])])


class Provenance(Scratch):
    """Reader one's collector findings (SECOND_READ_reader1_opus.md, appendix), Oct 11: F2 the stamp and the records, F1 a flagged worker's
    games, F3 the engine tree, F4 the decks."""

    def setUp(self):
        super().setUp()
        self.m = manifest()
        self.mpath = self.write_manifest(self.m)
        self.jobs = sc.expected_jobs(self.m)
        self.by_deck = {d: [j for j in self.jobs if j["deck"] == d] for d in ("d1", "d2", "d3")}

    def clean_w2(self):
        return self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))

    def w1(self, **kw):
        return self.worker("w1", self.mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"), **kw)

    def kinds(self, res):
        return sorted({(p["kind"], p.get("worker")) for p in res["problems"] if p["kind"] != "missing"})

    # F2: the stamp comes before play and is bound to the records by a seal after play
    def test_f2_a_stamp_later_than_a_game_is_refused_and_its_games_are_not_merged(self):
        res = sc.collect(self.mpath, [self.w1(stamped_at="2026-10-09T22:30:00Z"), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("stamp after play", "w1")])
        self.assertEqual(len(res["lines"]), 8)
        self.assertFalse(res["complete"])

    def test_f2_a_stamp_later_than_the_runs_first_start_is_refused(self):
        w1 = self.w1()
        with open(os.path.join(w1, "run_log.jsonl"), "w") as f:
            f.write(json.dumps({"event": "start", "at": "2026-10-09T20:00:00Z"}) + "\n")
        res = sc.collect(self.mpath, [w1, self.clean_w2()])
        self.assertEqual(self.kinds(res), [("stamp after play", "w1")])

    def test_f2_a_stamp_without_its_time_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(stamped_at=None), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("stamp after play", "w1")])

    def test_f2_a_worker_without_a_seal_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(seal=False), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("seal", "w1")])
        self.assertEqual(len(res["lines"]), 8)

    def test_f2_records_changed_after_the_seal_are_refused(self):
        w1 = self.w1()
        with open(os.path.join(w1, "games.jsonl"), "a") as f:
            f.write("\n")
        res = sc.collect(self.mpath, [w1, self.clean_w2()])
        self.assertEqual(self.kinds(res), [("seal", "w1")])

    def test_f2_a_program_changed_between_stamp_and_seal_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(seal_changes={"program_sha256": "ef" * 32}), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("seal", "w1")])

    def test_f2_a_seal_older_than_the_last_game_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(seal_changes={"sealed_at": "2026-10-09T21:30:00Z"}), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("seal", "w1")])

    def test_f2_the_stamp_command_refuses_a_folder_already_played(self):
        mpath, prog = self.mpath, os.path.join(self.d, "strength")
        with open(prog, "wb") as f:
            f.write(b"binary")
        out = os.path.join(self.d, "played")
        os.makedirs(out)
        with open(os.path.join(out, "games.jsonl"), "w") as f:
            f.write(json.dumps(record(self.jobs[0])) + "\n")
        self.assertEqual(sc.main(["stamp", "--manifest", mpath, "--program", prog, "--worker", "w", "--out", out, "--no-selfcheck"]), 2)
        self.assertFalse(os.path.exists(os.path.join(out, "worker.json")))

    def test_f2_stamp_then_seal_binds_the_records_to_the_program_and_manifest(self):
        root = os.path.join(self.d, "repo")
        for d in ("d1", "d2", "d3", "o1"):
            os.makedirs(os.path.join(root, "decks"), exist_ok=True)
            with open(os.path.join(root, "decks", f"{d}.txt"), "w") as f:
                f.write(f"list {d}\n")
        m = dict(self.m, repo_root=root)
        for d in m["decks"] + m["opponents"]:
            d["sha256"] = sc.sha256_file(os.path.join(root, d["path"]))
        mpath = self.write_manifest(m)
        prog = os.path.join(self.d, "strength")
        with open(prog, "wb") as f:
            f.write(b"binary")
        out = os.path.join(self.d, "w1")
        self.assertEqual(sc.main(["stamp", "--manifest", mpath, "--program", prog, "--worker", "w1", "--out", out, "--no-selfcheck"]), 0)
        with open(os.path.join(out, "worker.json")) as f:
            stamp = json.load(f)
        self.assertTrue(stamp["stamped_at"].endswith("Z"))
        self.assertEqual(stamp["decks_sha256"], {d["name"]: d["sha256"] for d in m["decks"] + m["opponents"]})
        with open(os.path.join(out, "games.jsonl"), "w") as f:
            f.write(json.dumps(record(self.jobs[0], started="2099-01-01T00:00:00Z")) + "\n")
        self.assertEqual(sc.main(["seal", "--manifest", mpath, "--program", prog, "--out", out]), 0)
        with open(os.path.join(out, "worker_seal.json")) as f:
            seal = json.load(f)
        self.assertEqual(seal["games_sha256"], sc.sha256_file(os.path.join(out, "games.jsonl")))
        self.assertEqual((seal["program_sha256"], seal["manifest_sha256"]), (stamp["program_sha256"], stamp["manifest_sha256"]))
        self.assertEqual(seal["decks_sha256"], stamp["decks_sha256"])

    def test_f2_the_seal_command_refuses_an_unstamped_folder(self):
        prog = os.path.join(self.d, "strength")
        with open(prog, "wb") as f:
            f.write(b"binary")
        out = os.path.join(self.d, "w")
        os.makedirs(out)
        self.assertEqual(sc.main(["seal", "--manifest", self.mpath, "--program", prog, "--out", out]), 2)

    # F1: a flagged worker's games are not merged, and an incomplete merge writes no games.jsonl
    def test_f1_a_worker_on_another_program_contributes_no_games(self):
        res = sc.collect(self.mpath, [self.w1(), self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",),
                                                              program_sha256="ef" * 32)])
        self.assertEqual(self.kinds(res), [("program", "w2")])
        self.assertEqual(len(res["lines"]), 16)
        self.assertEqual(len([p for p in res["problems"] if p["kind"] == "missing"]), 8)

    def test_f1_an_incomplete_merge_writes_no_games_jsonl(self):
        out = os.path.join(self.d, "merged")
        code = sc.main(["merge", "--manifest", self.mpath, "--out", out, "--worker", self.w1()])
        self.assertEqual(code, 1)
        self.assertFalse(os.path.exists(os.path.join(out, "games.jsonl")))
        self.assertTrue(os.path.exists(os.path.join(out, "games_INCOMPLETE.jsonl")))
        with open(os.path.join(out, "MERGE_RECORD.md")) as f:
            self.assertIn("INCOMPLETE", f.read())

    def test_f1_merge_never_overwrites_a_games_jsonl(self):
        out = os.path.join(self.d, "merged")
        os.makedirs(out)
        with open(os.path.join(out, "games.jsonl"), "w") as f:
            f.write("keep me\n")
        code = sc.main(["merge", "--manifest", self.mpath, "--out", out, "--worker", self.w1(), "--worker", self.clean_w2()])
        self.assertEqual(code, 2)
        with open(os.path.join(out, "games.jsonl")) as f:
            self.assertEqual(f.read(), "keep me\n")

    # F3: the engine tree fails closed; the build record belongs to the program
    def test_f3_a_manifest_naming_no_engine_tree_fails_closed(self):
        m = dict(self.m, engine="claude/playout-pilot b96296a5 (fix round 2) engine tree, built on the laptop Oct 3-4")
        mpath = self.write_manifest(m)
        w1 = self.worker("w1", mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(mpath, [w1, w2])
        self.assertEqual(self.kinds(res), [("engine", None)])
        self.assertFalse(res["complete"])
        self.assertEqual(res["lines"], [])

    def test_f3_the_tree_named_on_the_merge_command_is_used_and_recorded(self):
        m = dict(self.m, engine="claude/playout-pilot b96296a5 (fix round 2) engine tree, built on the laptop Oct 3-4")
        mpath = self.write_manifest(m)
        w1 = self.worker("w1", mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",))
        res = sc.collect(mpath, [w1, w2], engine_tree="38af8b0cc4f35fdc")
        self.assertTrue(res["complete"])
        self.assertIn("named on the merge command", sc.merge_record(res))
        res = sc.collect(mpath, [w1, w2], engine_tree="1234567")
        self.assertEqual(self.kinds(res), [("engine", "w1"), ("engine", "w2")])

    def test_f3_a_manifest_engine_tree_field_is_read(self):
        m = dict(self.m, engine="free text, no tree", engine_tree="38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5")
        self.assertEqual(sc.registered_tree(m), "38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5")
        m = dict(self.m, engine="free text", slow_report={"engine_tree": "31dbd2e6e8ecd39f"})
        self.assertEqual(sc.registered_tree(m), "31dbd2e6e8ecd39f")

    def test_f3_a_worker_whose_stamp_names_no_engine_tree_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(engine_tree=None), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("engine", "w1")])
        self.assertEqual(len(res["lines"]), 8)

    def test_f3_a_build_record_for_another_program_is_refused(self):
        res = sc.collect(self.mpath, [self.w1(build_sha="ef" * 32), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("program", "w1")])

    def test_f3_a_rebuild_must_be_of_the_registered_harness_source(self):
        m = dict(self.m, slow_report={"harness_source_sha256": "aa" * 32})
        mpath = self.write_manifest(m)
        w1 = self.worker("w1", mpath, [record(j) for j in self.by_deck["d1"] + self.by_deck["d3"]], only=("d1", "d3"))
        w2 = self.worker("w2", mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), program_sha256="ef" * 32, selfcheck=dict(SELF))
        with open(os.path.join(w2, "worker.json")) as f:
            stamp = json.load(f)
        stamp["harness_source_sha256"] = "bb" * 32
        with open(os.path.join(w2, "worker.json"), "w") as f:
            json.dump(stamp, f)
        res = sc.collect(mpath, [w1, w2])
        self.assertEqual(self.kinds(res), [("program", "w2")])
        self.assertIn("harness source", [p for p in res["problems"] if p["kind"] == "program"][0]["detail"])

    # F4: the deck files a worker loads are the manifest's, by sha256
    def test_f4_an_edited_deck_under_the_same_name_is_refused(self):
        decks = {d["name"]: d["sha256"] for d in self.m["decks"] + self.m["opponents"]}
        decks["d3"] = "9" * 64
        res = sc.collect(self.mpath, [self.w1(decks=decks), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("decks", "w1")])
        self.assertIn("d3", [p for p in res["problems"] if p["kind"] == "decks"][0]["detail"])
        self.assertEqual(len(res["lines"]), 8)

    def test_f4_an_opponent_list_edited_is_refused(self):
        decks = {d["name"]: d["sha256"] for d in self.m["decks"] + self.m["opponents"]}
        decks["o1"] = "9" * 64
        res = sc.collect(self.mpath, [self.w1(), self.worker("w2", self.mpath, [record(j) for j in self.by_deck["d2"]], only=("d2",), decks=decks)])
        self.assertEqual(self.kinds(res), [("decks", "w2")])

    def test_f4_a_stamp_without_deck_hashes_is_refused(self):
        w1 = self.w1()
        with open(os.path.join(w1, "worker.json")) as f:
            stamp = json.load(f)
        del stamp["decks_sha256"]
        with open(os.path.join(w1, "worker.json"), "w") as f:
            json.dump(stamp, f)
        res = sc.collect(self.mpath, [w1, self.clean_w2()])
        self.assertEqual(self.kinds(res), [("decks", "w1")])

    def test_f4_decks_changed_between_stamp_and_seal_are_refused(self):
        decks = {d["name"]: d["sha256"] for d in self.m["decks"] + self.m["opponents"]}
        decks["d1"] = "9" * 64
        res = sc.collect(self.mpath, [self.w1(seal_changes={"decks_sha256": decks}), self.clean_w2()])
        self.assertEqual(self.kinds(res), [("seal", "w1")])


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

    def test_the_same_games_in_another_order_are_equal(self):
        # a straight run with several threads writes its games as they finish, the merge in the job list's order
        a, b = self.files()
        with open(b) as f:
            lines = f.readlines()
        lines[6], lines[7] = lines[7], lines[6]
        with open(b, "w") as f:
            f.writelines(lines)
        self.assertEqual(sc.main(["compare", a, b]), 0)

    def test_a_game_missing_from_one_side_fails(self):
        a, b = self.files()
        with open(b) as f:
            lines = f.readlines()
        with open(b, "w") as f:
            f.writelines(lines[:-1] + [lines[0]])
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
