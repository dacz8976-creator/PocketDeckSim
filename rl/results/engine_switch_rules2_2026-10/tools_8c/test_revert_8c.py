"""Tests for revert_8c.py, the step 8c revert-check driver (rules switch 2; the laptop's spec, Oct 10), with fakes: no program, no deck
and no game of the real run is used. A fake runner stands in for the two score dumps and prints what score_dump_round2.rs prints (the
`PGTICK ... asked about` line, the `PGDUMP score text` lines and `deal i, tick t: chose X`); the decks, programs, hand-off and
lookahead.tsv are made in a temporary folder. counters.tsv is the real one, one folder up.
Run: python3 -m unittest test_revert_8c   (from this folder)"""
import contextlib, hashlib, json, os, stat, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
COUNTERS_TSV = HERE.parent / "counters.tsv"          # the folder's own counters.tsv, one level up
import revert_8c as rv  # noqa: E402

SEED_BASE = 23100000000
NONE_R2 = {k: None for k in rv.R2_KINDS}
CHOSEN_A, CHOSEN_B = "Place(Pokemon(B2b 040 Darkrai), 1)", "EndTurn"
SCORES_A = [("-10503.366666666666788", "EndTurn"), ("-9644.366666666666788", "Place(Pokemon(B2b 040 Darkrai), 1)")]
SCORES_B = [("-10503.366666666666788", "EndTurn"), ("-9744.366666666666788", "Place(Pokemon(B2b 040 Darkrai), 1)")]


def probe(queued=None, cut=None, free=False, ret=None, trapleaf=None, tick=None, **r2):
    p = {"queued": queued, "cut": cut, "free": free, "ret": ret, "r2": dict(NONE_R2, **r2), "trapleaf": trapleaf}
    if tick is not None:
        p["tick"] = tick
    return p


def dump_out(chosen, cands, rc=0, stray=True):
    """What the score dump prints: stdout `deal ...: chose X`; stderr the board, the PGTICK line (a stray PGDUMP line before it, from a
    replayed tick, is not part of the decision asked about) and the dump."""
    err = ["PGBOARD coin seat0=[] seat1=[]"]
    if stray:
        err.append("PGDUMP        -1.000000000000000000 STRAY replayed tick")
    err.append("PGTICK 89 (the decision asked about; gates off for it: [])")
    err.append(f"PGDUMP actor=1 candidates={len(cands)}")
    err += [f"PGDUMP {score:>26} {text}" for score, text in cands]
    return rc, (f"deal 2, tick 89: chose {chosen}\n" if chosen is not None else ""), "\n".join(err) + "\n"


class FakeRunner:
    """A PASS game by default: the official engine chooses A, P with every gate on chooses B (the difference replays), P with the game's
    gates off and P with all gates off choose A with the official scores. `over` replaces one of "official", "p", "gate_off", "all_off"
    with a (rc, chosen, cands) tuple, for every game, or `over_deal[deal]` for one game."""

    def __init__(self, over=None, over_deal=None):
        self.over, self.over_deal, self.calls = over or {}, over_deal or {}, []

    def __call__(self, program, args, env):
        revert = args[args.index("--revert") + 1] if "--revert" in args else None
        deal = int(args[args.index("--deal") + 1])
        name = "official" if program.label == "official" else "p" if revert is None else "all_off" if revert == "all" else "gate_off"
        self.calls.append({"name": name, "program": program.label, "path": program.path, "cwd": program.cwd, "args": list(args), "revert": revert,
                           "deal": deal, "env": env})
        base = {"official": (0, CHOSEN_A, SCORES_A), "p": (0, CHOSEN_B, SCORES_B), "gate_off": (0, CHOSEN_A, SCORES_A),
                "all_off": (0, CHOSEN_A, SCORES_A)}
        rc, chosen, cands = {**base, **self.over, **self.over_deal.get(deal, {})}[name]
        return dump_out(chosen, cands, rc)


class Case(unittest.TestCase):
    """A temporary folder with two decks, two program files, a hand-off and lookahead.tsv; `go` runs the driver on them."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        (self.tmp / "root" / "decks").mkdir(parents=True)
        self.held, self.panel = b"2 Eevee\n", b"2 Darkrai\n"
        (self.tmp / "root" / "decks" / "held.txt").write_bytes(self.held)
        (self.tmp / "root" / "decks" / "panel.txt").write_bytes(self.panel)
        self.progs = {}
        for label in ("official", "p"):
            (self.tmp / label / "engine").mkdir(parents=True)
            exe = self.tmp / label / f"{label}-dump"
            exe.write_bytes(f"binary of {label}\n".encode())
            self.progs[label] = (exe, self.tmp / label / "engine", hashlib.sha256(exe.read_bytes()).hexdigest())
        self.games = []
        self.out = self.tmp / "out"

    def add(self, pairing=35, i=2, bot="km3", k=89, pr=None, verdict=rv.BOTH_HALVES, step="8", seed=None):
        self.games.append({"step": step, "bot": bot, "pairing": pairing, "i": i, "k": k, "probe": pr if pr is not None else probe(queued=2, tick=k),
                           "verdict": verdict, "seed": SEED_BASE + pairing * 10_000 + i if seed is None else seed})

    def files(self, handoff_edit=None, held_blob=None):
        blob = lambda b: rv.hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
        with open(self.tmp / "lookahead.tsv", "w", encoding="utf-8", newline="\n") as f:
            f.write("\t".join(rv.LOOKAHEAD_HEADER) + "\n")
            for g in self.games:
                f.write("\t".join(map(str, [g["step"], g["bot"], g["pairing"], g["i"], g["seed"], g["k"], 13, g["verdict"], g["verdict"],
                                            json.dumps(g["probe"], sort_keys=True)])) + "\n")
        rows = [{"step": g["step"], "bot": g["bot"], "pairing": g["pairing"], "i": g["i"], "seed": g["seed"], "old_moves": "12", "new_moves": "13",
                 "held_file": "decks/held.txt", "panel_file": "decks/panel.txt", "held_blob": held_blob or blob(self.held),
                 "panel_blob": blob(self.panel), "exact_counters": "{}"} for g in self.games]
        if handoff_edit:
            rows = handoff_edit(rows)
        cols = ["step", "bot", "pairing", "i", "seed", "old_moves", "new_moves", "held_file", "panel_file", "held_blob", "panel_blob", "exact_counters"]
        with open(self.tmp / "handoff_8c.tsv", "w", encoding="utf-8", newline="\n") as f:
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(str(r[c]) for c in cols) + "\n")

    def go(self, runner=None, environ=None, jobs=1, p_sha=None, official_sha=None, seed_bases=(SEED_BASE,), counters=None, write=True):
        if write:
            self.files()
        runner = runner or FakeRunner()
        logs = []
        argv = ["--lookahead", str(self.tmp / "lookahead.tsv"), "--counters", str(counters or COUNTERS_TSV),
                "--handoff", str(self.tmp / "handoff_8c.tsv"), "--root", str(self.tmp / "root"),
                "--p-program", str(self.progs["p"][0]), "--p-cwd", str(self.progs["p"][1]), "--p-sha256", p_sha or self.progs["p"][2],
                "--official-program", str(self.progs["official"][0]), "--official-cwd", str(self.progs["official"][1]),
                "--official-sha256", official_sha or self.progs["official"][2], "--out", str(self.out), "--jobs", str(jobs)]
        for b in seed_bases:
            argv += ["--seed-base", str(b)]
        code = rv.run(argv, environ={"PATH": "/usr/bin", "HOME": "/home/x"} if environ is None else environ, runner=runner,
                      log=lambda *a, **k: logs.append(" ".join(str(x) for x in a)))
        self.logs = "\n".join(logs)
        return code, runner

    def rows(self):
        lines = (self.out / "revert_8c.tsv").read_text(encoding="utf-8").splitlines()
        return [dict(zip(lines[0].split("\t"), ln.split("\t"))) for ln in lines[1:]]

    def summary(self):
        return (self.out / "revert_8c_summary.txt").read_text(encoding="utf-8")

    def assertRefused(self, runner, **kw):
        code, _ = self.go(runner=runner, **kw)
        self.assertEqual(code, 2, self.logs)
        self.assertIn("REFUSED", self.logs)
        self.assertEqual(runner.calls, [], "a refusal runs nothing")
        self.assertFalse(self.out.exists(), "a refusal writes nothing")


class Reproduced(Case):
    def test_a_game_whose_gate_off_run_is_the_official_one_passes(self):
        self.add()
        code, runner = self.go()
        self.assertEqual(code, 0, self.logs)
        self.assertEqual(self.summary(), "revert 1 of 1 reproduced\n")
        (row,) = self.rows()
        self.assertEqual((row["result"], row["reason"], row["kind"], row["gates"], row["tokens"]),
                         ("PASS", "", "queued", "DECKGYM_NO_PLAIN_HIT_COIN,DECKGYM_PLAIN_QUEUED_SITES", "g1,g2"))
        self.assertEqual((row["official_move"], row["p_move"], row["gate_off_move"], row["all_off_move"]), (CHOSEN_A, CHOSEN_B, CHOSEN_A, CHOSEN_A))
        self.assertEqual([row[c] for c in ("replay_ok", "move_equal", "scores_equal", "all_off_equal", "process_ok")], ["yes"] * 5)

    def test_the_four_runs_are_asked_as_specified(self):
        self.add(pairing=35, i=2, bot="km3", k=89)
        _, runner = self.go()
        self.assertEqual([c["name"] for c in runner.calls], ["official", "p", "gate_off", "all_off"])
        by = {c["name"]: c for c in runner.calls}
        base = ["--a", str(self.tmp / "root/decks/held.txt"), "--b", str(self.tmp / "root/decks/panel.txt"), "--seed-base", str(SEED_BASE),
                "--pairing", "35", "--bot", "km3", "--deal", "2", "--tick", "89"]
        self.assertEqual(by["official"]["args"], base)                     # the official dump: no gate
        self.assertEqual(by["p"]["args"], base)                            # P as it is: every gate on
        self.assertEqual(by["gate_off"]["args"], base + ["--revert", "g1,g2"])
        self.assertEqual(by["all_off"]["args"], base + ["--revert", "all"])
        self.assertEqual((by["official"]["path"], by["official"]["cwd"]), (str(self.progs["official"][0]), str(self.progs["official"][1])))
        for n in ("p", "gate_off", "all_off"):
            self.assertEqual((by[n]["path"], by[n]["cwd"]), (str(self.progs["p"][0]), str(self.progs["p"][1])))

    def test_a_mixed_frame_gets_the_union_of_its_findings_gates(self):
        # Reader one's N5: a frame with a queued choice and a Will condition and Guts at once.
        self.add(pr=probe(queued=2, will=2, guts=3, tick=89))
        _, runner = self.go()
        self.assertEqual(next(c for c in runner.calls if c["name"] == "gate_off")["revert"], "g1,g2,g4,g7")
        (row,) = self.rows()
        self.assertEqual((row["kind"], row["result"]), ("queued+will+guts", "PASS"))

    def test_a_return_ply_turns_p2_off_and_the_all_off_run_is_always_made(self):
        self.add(pr=probe(ret=1, tick=89))
        _, runner = self.go()
        self.assertEqual([c["revert"] for c in runner.calls], [None, None, "p2", "all"])

    def test_several_games_are_counted_and_listed_in_order(self):
        self.add(bot="kp3", pairing=7, i=5, pr=probe(will=2, tick=89))
        self.add(bot="km3", pairing=35, i=2)
        self.add(bot="km3", pairing=4, i=9, pr=probe(trapleaf=1, tick=89))
        code, runner = self.go(jobs=3)
        self.assertEqual(code, 0, self.logs)
        self.assertEqual(self.summary(), "revert 3 of 3 reproduced\n")
        self.assertEqual([(r["bot"], r["pairing"], r["i"], r["tokens"]) for r in self.rows()],
                         [("km3", "4", "9", "g6"), ("km3", "35", "2", "g1,g2"), ("kp3", "7", "5", "g4")])
        self.assertEqual(len(runner.calls), 12)

    def test_the_provenance_file_names_the_inputs_the_programs_and_the_driver(self):
        self.add()
        self.go()
        info = json.loads((self.out / "revert_8c.json").read_text(encoding="utf-8"))
        self.assertEqual((info["summary"], info["games"], info["passed"], info["failed"]), ("revert 1 of 1 reproduced", 1, 1, []))
        self.assertEqual(info["inputs"]["lookahead"]["sha256"], hashlib.sha256((self.tmp / "lookahead.tsv").read_bytes()).hexdigest())
        self.assertEqual(info["inputs"]["counters"]["sha256"], hashlib.sha256((COUNTERS_TSV).read_bytes()).hexdigest())
        self.assertEqual(info["programs"]["p"]["sha256"], self.progs["p"][2])
        self.assertEqual(info["programs"]["official"]["sha256"], self.progs["official"][2])
        self.assertEqual(info["driver_sha256"], hashlib.sha256((HERE / "revert_8c.py").read_bytes()).hexdigest())
        self.assertEqual(info["inputs"]["seed_bases"], [SEED_BASE])


class Failures(Case):
    def failed(self, over=None, over_deal=None, reason=None):
        self.add()
        code, _ = self.go(runner=FakeRunner(over, over_deal))
        self.assertEqual(code, 1, self.logs)
        self.assertEqual(self.summary(), "revert 0 of 1 reproduced\n")
        (row,) = self.rows()
        self.assertEqual(row["result"], "FAIL")
        if reason is not None:
            self.assertEqual(row["reason"], reason)
        self.assertIn("STOP", self.logs)
        self.assertTrue((self.out / "raw" / "8_km3_35_2.txt").is_file(), "the raw dumps of a failed game are kept")
        return row

    def test_fail_when_the_gate_off_move_is_not_the_official_move(self):
        row = self.failed({"gate_off": (0, CHOSEN_B, SCORES_B)})
        self.assertIn("move", row["reason"].split(","))
        self.assertEqual((row["move_equal"], row["gate_off_move"]), ("NO", CHOSEN_B))

    def test_fail_on_the_scores_alone(self):
        # The same move, one candidate's score a millionth off: the move matches, the scores do not.
        close = [SCORES_A[0], (str(float(SCORES_A[1][0]) + 1e-6), SCORES_A[1][1])]
        row = self.failed({"gate_off": (0, CHOSEN_A, close)}, reason="scores")
        self.assertEqual((row["move_equal"], row["scores_equal"], row["all_off_equal"]), ("yes", "NO", "yes"))

    def test_fail_when_a_candidate_text_or_the_candidate_count_differs(self):
        self.failed({"gate_off": (0, CHOSEN_A, [SCORES_A[0], (SCORES_A[1][0], "Place(Pokemon(B2b 040 Darkrai), 2)")])}, reason="scores")
        self._tmp.cleanup(), self.setUp()
        self.failed({"gate_off": (0, CHOSEN_A, SCORES_A[:1])}, reason="scores")

    def test_a_score_within_a_billionth_is_the_same_score(self):
        near = [SCORES_A[0], (str(float(SCORES_A[1][0]) + 1e-10), SCORES_A[1][1])]
        self.add()
        code, _ = self.go(runner=FakeRunner({"gate_off": (0, CHOSEN_A, near)}))
        self.assertEqual(code, 0, self.logs)

    def test_fail_on_the_all_off_run_alone(self):
        row = self.failed({"all_off": (0, CHOSEN_B, SCORES_B)}, reason="all_off")
        self.assertEqual((row["move_equal"], row["scores_equal"], row["all_off_equal"]), ("yes", "yes", "NO"))
        self._tmp.cleanup(), self.setUp()
        row = self.failed({"all_off": (0, CHOSEN_A, SCORES_B)}, reason="all_off")       # the move matches, the scores do not
        self.assertEqual(row["all_off_move"], CHOSEN_A)

    def test_fail_when_the_difference_does_not_replay(self):
        # P with every gate on chooses what the official engine chose: the game's difference was not reproduced, so the check says nothing.
        row = self.failed({"p": (0, CHOSEN_A, SCORES_A)}, reason="replay")
        self.assertEqual(row["replay_ok"], "NO")

    def test_fail_when_a_program_fails_or_prints_no_choice_or_no_scores(self):
        for name, bad in (("official", (1, CHOSEN_A, SCORES_A)), ("gate_off", (0, None, SCORES_A)), ("all_off", (0, CHOSEN_A, [])),
                          ("p", (101, CHOSEN_B, SCORES_B))):
            self._tmp.cleanup(), self.setUp()
            row = self.failed({name: bad})
            self.assertEqual(row["process_ok"], "NO", name)
            self.assertIn("process", row["reason"].split(","), name)

    def test_one_failed_game_among_three(self):
        for i in (2, 3, 4):
            self.add(i=i)
        code, _ = self.go(runner=FakeRunner(over_deal={3: {"gate_off": (0, CHOSEN_B, SCORES_B)}}))
        self.assertEqual(code, 1)
        self.assertEqual(self.summary(), "revert 2 of 3 reproduced\n")
        self.assertEqual([(r["i"], r["result"]) for r in self.rows()], [("2", "PASS"), ("3", "FAIL"), ("4", "PASS")])
        self.assertIn("FAIL ('8', 'km3', 35, 3)", self.logs)
        self.assertTrue((self.out / "raw" / "8_km3_35_3.txt").is_file())
        self.assertFalse((self.out / "raw" / "8_km3_35_2.txt").exists())


def with_root(text, only=None):
    """`over` for the FakeRunner: the four runs as usual (a PASS game), each with one more root candidate, `text`."""
    base = {"official": (0, CHOSEN_A, SCORES_A), "p": (0, CHOSEN_B, SCORES_B), "gate_off": (0, CHOSEN_A, SCORES_A), "all_off": (0, CHOSEN_A, SCORES_A)}
    return {n: (rc, chosen, cands + [("-9700.5", text)]) for n, (rc, chosen, cands) in base.items() if only is None or n in only}


class RootGuard(Case):
    """Reader one's N3 (the laptop's addition, Oct 10): a root that holds a pending attack continuation (a queued hit or punch frame, a
    pending attack coin choice) is neither PASS nor FAIL: ROOT_CONTINUATION, not reproduced, and a stop that goes to Dustin."""
    KINDS = {"ApplyQueuedAttackDamage": 'ApplyQueuedAttackDamage { attack: Attack { title: "Wild Swing" } }',
             "ApplyDamage": "ApplyDamage { targets: [(20, 1, 1)] }",
             "KeepAttackCoinResults": "KeepAttackCoinResults",
             "RerollAttackCoins": "RerollAttackCoins { victory_star_in_play_idx: 0 }"}

    def test_each_continuation_kind_among_the_roots_candidates_is_not_a_pass(self):
        for kind, text in self.KINDS.items():
            self._tmp.cleanup(), self.setUp()
            self.add()
            code, _ = self.go(runner=FakeRunner(with_root(text)))
            self.assertEqual(code, 1, (kind, self.logs))
            (row,) = self.rows()
            self.assertEqual((row["result"], row["root_holds"], row["reason"]), ("ROOT_CONTINUATION", kind, f"root holds {kind}"), kind)
            self.assertEqual((row["move_equal"], row["scores_equal"], row["all_off_equal"]), ("yes", "yes", "yes"), "the comparison is kept")
            self.assertEqual(self.summary(), "revert 0 of 1 reproduced\n")
            self.assertTrue((self.out / "raw" / "8_km3_35_2.txt").is_file())
            self.assertIn("ROOT_CONTINUATION", self.logs)
            self.assertIn("STOP", self.logs)

    def test_it_is_not_a_fail_either_when_the_comparison_would_have_failed(self):
        over = with_root(self.KINDS["ApplyQueuedAttackDamage"])
        over["gate_off"] = (0, CHOSEN_B, over["gate_off"][2])
        self.add()
        code, _ = self.go(runner=FakeRunner(over))
        self.assertEqual(code, 1)
        (row,) = self.rows()
        self.assertEqual((row["result"], row["move_equal"]), ("ROOT_CONTINUATION", "NO"))

    def test_a_continuation_in_one_run_only_is_enough(self):
        for only in ("official", "p", "gate_off", "all_off"):
            self._tmp.cleanup(), self.setUp()
            self.add()
            code, _ = self.go(runner=FakeRunner(with_root(self.KINDS["KeepAttackCoinResults"], only=(only,))))
            self.assertEqual((code, self.rows()[0]["result"]), (1, "ROOT_CONTINUATION"), only)

    def test_several_kinds_are_all_named(self):
        over = with_root("RerollAttackCoins { victory_star_in_play_idx: 0 }")
        over = {n: (rc, ch, cands + [("-9701.5", "KeepAttackCoinResults")]) for n, (rc, ch, cands) in over.items()}
        self.add()
        self.go(runner=FakeRunner(over))
        self.assertEqual(self.rows()[0]["root_holds"], "KeepAttackCoinResults,RerollAttackCoins")

    def test_an_ordinary_root_is_not_touched(self):
        # Turn menus (Attach, Play, Place, EndTurn), and an action that only begins with a continuation kind's name, are ordinary.
        extra = [("-9800.0", "Attach { attachments: [(1, Psychic, 0)], is_turn_energy: true }"), ("-9801.0", "Play { trainer_card: A1 225 Sabrina }"),
                 ("-9802.0", "ApplyDamageLater { targets: [] }"), ("-9803.0", "Retreat(2)")]
        over = {n: (rc, ch, cands + extra) for n, (rc, ch, cands) in with_root("EndTurn").items()}
        self.add()
        code, _ = self.go(runner=FakeRunner(over))
        self.assertEqual(code, 0, self.logs)
        (row,) = self.rows()
        self.assertEqual((row["result"], row["root_holds"]), ("PASS", ""))

    def test_a_program_that_failed_did_not_show_its_root_and_is_a_fail(self):
        over = with_root(self.KINDS["ApplyDamage"])
        over["official"] = (1, CHOSEN_A, over["official"][2])
        self.add()
        self.go(runner=FakeRunner(over))
        (row,) = self.rows()
        self.assertEqual((row["result"], row["reason"].split(",")[0]), ("FAIL", "process"))

    def test_among_several_games_only_the_passes_are_counted(self):
        for i in (2, 3, 4):
            self.add(i=i)
        runner = FakeRunner(over_deal={3: with_root(self.KINDS["RerollAttackCoins"]), 4: {"gate_off": (0, CHOSEN_B, SCORES_B)}})
        code, _ = self.go(runner=runner)
        self.assertEqual(code, 1)
        self.assertEqual(self.summary(), "revert 1 of 3 reproduced\n")
        self.assertEqual([(r["i"], r["result"]) for r in self.rows()], [("2", "PASS"), ("3", "ROOT_CONTINUATION"), ("4", "FAIL")])
        self.assertIn("1 game(s) failed the revert check and 1 are a ROOT_CONTINUATION", self.logs)
        info = json.loads((self.out / "revert_8c.json").read_text(encoding="utf-8"))
        self.assertEqual([k[:4] for k in info["root_continuation"]], [["8", "km3", 35, 3]])
        self.assertEqual([k[:4] for k in info["failed"]], [["8", "km3", 35, 4]])
        self.assertTrue((self.out / "raw" / "8_km3_35_3.txt").is_file() and (self.out / "raw" / "8_km3_35_4.txt").is_file())
        self.assertFalse((self.out / "raw" / "8_km3_35_2.txt").exists())


class Refusals(Case):
    def test_an_unknown_round_two_kind_in_the_probe_is_refused(self):
        self.add(pr=dict(probe(queued=2, tick=89), r2=dict(NONE_R2, mystery=2)))
        self.assertRefused(FakeRunner())

    def test_a_probe_without_a_round_two_kind_or_with_an_unknown_field_is_refused(self):
        bad = probe(queued=2, tick=89)
        del bad["r2"]["perish"]
        self.add(pr=bad)
        self.assertRefused(FakeRunner())
        self._tmp.cleanup(), self.setUp()
        self.add(pr=dict(probe(queued=2, tick=89), mystery=1))
        self.assertRefused(FakeRunner())
        self._tmp.cleanup(), self.setUp()
        extra = dict(probe(queued=2, tick=89), queued_attacks=["Wild Swing"], truncated=True, retried=600000)   # classify_8c.py's own extras
        self.add(pr=extra)
        code, _ = self.go()
        self.assertEqual(code, 0, self.logs)

    def test_a_probe_that_found_nothing_is_refused(self):
        self.add(pr=probe(tick=89))
        self.assertRefused(FakeRunner())

    def test_a_ply_that_is_not_a_number_is_refused(self):
        for bad in ("2", True, -1, 1.5):
            self._tmp.cleanup(), self.setUp()
            self.add(pr=probe(queued=bad, tick=89))
            self.assertRefused(FakeRunner())

    def test_a_probe_run_at_another_tick_than_k_is_refused(self):
        self.add(k=89, pr=probe(queued=2, tick=88))
        self.assertRefused(FakeRunner())

    def test_a_verdict_that_is_not_a_lookahead_verdict_is_refused(self):
        self.add(verdict="ON THE BOARD")
        self.assertRefused(FakeRunner())

    def test_a_counter_the_table_does_not_know_a_switch_it_does_not_know_or_none_is_refused(self):
        real = (COUNTERS_TSV).read_text(encoding="utf-8")
        queued_row = next(ln for ln in real.splitlines() if ln.startswith("coin_queued_by_attack\t"))
        edits = {"an unknown switch": real.replace(queued_row, queued_row.replace("DECKGYM_PLAIN_QUEUED_SITES", "DECKGYM_SOMETHING_ELSE")),
                 "no switch": real.replace(queued_row, queued_row.rsplit("\t", 1)[0] + "\t-"),
                 "the master switch as a counter's switch": real.replace(queued_row, queued_row.rsplit("\t", 1)[0] + "\tDECKGYM_ROUND2_OFF"),
                 "no such counter": "\n".join(ln for ln in real.splitlines() if not ln.startswith("coin_queued_by_attack\t")) + "\n"}
        for why, text in edits.items():
            self._tmp.cleanup(), self.setUp()
            self.add()
            path = self.tmp / "counters.tsv"
            path.write_text(text, encoding="utf-8", newline="\n")
            self.assertRefused(FakeRunner(), counters=path)

    def test_two_counters_of_one_kind_naming_different_switches_are_refused(self):
        real = (COUNTERS_TSV).read_text(encoding="utf-8")
        row = next(ln for ln in real.splitlines() if ln.startswith("will_block_coin_attack\t"))
        self.add(pr=probe(will=2, tick=89))
        path = self.tmp / "counters.tsv"
        path.write_text(real.replace(row, row.rsplit("\t", 1)[0] + "\tDECKGYM_NO_OWN_SIDE_COIN"), encoding="utf-8", newline="\n")
        self.assertRefused(FakeRunner(), counters=path)

    def test_a_deckgym_variable_in_the_callers_environment_is_refused(self):
        for var in ("DECKGYM_ROUND2_OFF", "DECKGYM_NO_PLAIN_HIT_COIN", "PDL_EQUIV_DEALS", "GOLDFISH_TRACE", "PG_DUMP"):
            self._tmp.cleanup(), self.setUp()
            self.add()
            self.assertRefused(FakeRunner(), environ={"PATH": "/usr/bin", var: "1"})
            self.assertIn(var, self.logs)

    def test_the_programs_must_be_the_files_named(self):
        self.add()
        self.assertRefused(FakeRunner(), p_sha="0" * 64)
        self.assertIn("not the", self.logs)
        self.assertRefused(FakeRunner(), official_sha="1" * 64)
        self.assertRefused(FakeRunner(), p_sha="ABC")
        self.assertRefused(FakeRunner(), p_sha=self.progs["p"][2].upper())
        self.progs["p"][0].unlink()
        self.assertRefused(FakeRunner())
        self.assertIn("no program", self.logs)

    def test_the_seed_must_belong_to_a_seed_base_the_caller_gave(self):
        self.add(pairing=35, i=2)
        self.assertRefused(FakeRunner(), seed_bases=(SEED_BASE + 1,))
        self.assertRefused(FakeRunner(), seed_bases=(SEED_BASE + 1, SEED_BASE + 2))
        self._tmp.cleanup(), self.setUp()
        self.add(pairing=35, i=2, seed=SEED_BASE + 35 * 10_000 + 3)            # the seed of deal 3, not deal 2
        self.assertRefused(FakeRunner())
        self._tmp.cleanup(), self.setUp()
        self.add(pairing=35, i=2)
        code, runner = self.go(seed_bases=(5, SEED_BASE))                        # two bases allowed: the row's is found
        self.assertEqual(code, 0, self.logs)
        self.assertEqual(runner.calls[0]["args"][runner.calls[0]["args"].index("--seed-base") + 1], str(SEED_BASE))

    def test_the_hand_off_must_agree_with_lookahead_tsv(self):
        self.add()
        self.files(handoff_edit=lambda rows: [dict(r, seed=int(r["seed"]) + 1) for r in rows])
        self.assertRefused(FakeRunner(), write=False)
        self._tmp.cleanup(), self.setUp()
        self.add()
        self.files(handoff_edit=lambda rows: [])
        self.assertRefused(FakeRunner(), write=False)
        self.assertIn("not in the hand-off", self.logs)

    def test_the_deck_files_must_be_the_hand_offs_blobs(self):
        self.add()
        self.files(held_blob="0" * 40)
        self.assertRefused(FakeRunner(), write=False)
        self.assertIn("blob", self.logs)
        self._tmp.cleanup(), self.setUp()
        self.add()
        self.files()
        (self.tmp / "root" / "decks" / "panel.txt").unlink()
        self.assertRefused(FakeRunner(), write=False)

    def test_a_game_twice_in_lookahead_tsv_is_refused(self):
        self.add()
        self.add()
        self.assertRefused(FakeRunner())
        self.assertIn("twice", self.logs)

    def test_a_missing_or_misshapen_file_is_refused(self):
        self.add()
        self.files()
        (self.tmp / "lookahead.tsv").write_text("step\tbot\n8\tkm3\n", encoding="utf-8")
        self.assertRefused(FakeRunner(), write=False)
        self._tmp.cleanup(), self.setUp()
        self.add()
        self.files()
        (self.tmp / "handoff_8c.tsv").unlink()
        self.assertRefused(FakeRunner(), write=False)


class Environment(Case):
    def test_each_program_gets_a_clean_copy_and_the_callers_environment_is_left_alone(self):
        self.add()
        caller = {"PATH": "/usr/bin", "HOME": "/home/x"}
        before = dict(caller)
        os_before = {k: v for k, v in os.environ.items() if k.startswith("DECKGYM_")}

        class Meddler(FakeRunner):
            def __call__(self, program, args, env):
                assert "DECKGYM_SCRATCH" not in env, "one program's environment leaked into the next one's"
                env["DECKGYM_SCRATCH"] = "1"                      # a program's copy may be changed; nothing flows back
                return super().__call__(program, args, env)

        _, runner = self.go(runner=Meddler(), environ=caller)
        self.assertEqual(caller, before)
        self.assertEqual({k: v for k, v in os.environ.items() if k.startswith("DECKGYM_")}, os_before)
        self.assertEqual(os_before, {}, "the tests themselves run with no DECKGYM_* variable")
        for c in runner.calls:
            self.assertEqual({k: v for k, v in c["env"].items() if k != "DECKGYM_SCRATCH"}, before)

    def test_the_gates_are_never_set_through_the_environment(self):
        self.add(pr=probe(queued=2, ret=1, will=2, tick=89))
        _, runner = self.go()
        for c in runner.calls:
            self.assertFalse([k for k in c["env"] if k.startswith("DECKGYM_")], c["name"])

    @unittest.skipIf(os.name == "nt", "the fake programs are shell scripts")
    def test_a_real_subprocess_runs_in_its_working_directory_with_a_clean_environment(self):
        self.add()
        script = """#!/bin/sh
case "$*" in *--revert*) c=A;; *) if [ "$(basename "$0")" = "p-dump" ]; then c=B; else c=A; fi;; esac
echo "deal 2, tick 89: chose $c"
echo "PGTICK 89 (the decision asked about)" >&2
echo "PGDUMP -1.5 $c" >&2
pwd >> "$PWD/seen.txt"
env | grep -c '^DECKGYM_' >> "$PWD/seen.txt"
exit 0
"""
        for label in ("official", "p"):
            exe = self.progs[label][0]
            exe.write_text(script, encoding="utf-8", newline="\n")
            exe.chmod(exe.stat().st_mode | stat.S_IXUSR)
            self.progs[label] = (exe, self.progs[label][1], hashlib.sha256(exe.read_bytes()).hexdigest())
        # P's default run chooses B and prints "-1.5 B", so the candidate lists differ between P and the official engine only there.
        code, _ = self.go(runner=rv.run_program)
        self.assertEqual(code, 0, self.logs)
        (row,) = self.rows()
        self.assertEqual((row["official_move"], row["p_move"], row["gate_off_move"], row["all_off_move"]), ("A", "B", "A", "A"))
        for label in ("official", "p"):
            seen = (self.progs[label][1] / "seen.txt").read_text().split()
            self.assertTrue(all(seen[j] == str(self.progs[label][1].resolve()) or seen[j] == str(self.progs[label][1]) for j in range(0, len(seen), 2)))
            self.assertTrue(all(seen[j] == "0" for j in range(1, len(seen), 2)))


class GatesFromCountersTsv(unittest.TestCase):
    """The real counters.tsv, beside this file: each finding's gate is what its revert_switch column names."""
    counters = rv.read_counters(COUNTERS_TSV)

    def test_each_finding_picks_its_gate(self):
        expected = {"queued": ["g1", "g2"], "cut": ["g1", "g2"], "return": ["p2"], "will": ["g4"], "vs": ["g5"], "trap": ["g6"],
                    "trapleaf": ["g6"], "own": ["g3"], "guts": ["g7"], "plain": ["g1"], "perish": ["g8"]}
        for label, tokens in expected.items():
            self.assertEqual(rv.gates_for([label], self.counters)[1], tokens, label)
        self.assertEqual(rv.gates_for(["queued"], self.counters)[0], ["DECKGYM_NO_PLAIN_HIT_COIN", "DECKGYM_PLAIN_QUEUED_SITES"])
        self.assertEqual(rv.gates_for(["return"], self.counters)[0], ["DECKGYM_FLAT_RETURN_DAMAGE"])

    def test_the_seven_site_gate_is_g1_and_g2_together_never_g2_alone(self):
        self.assertEqual(rv.gates_for(["queued"], self.counters)[1], ["g1", "g2"])
        self.assertEqual(rv.gates_for(["cut"], self.counters)[1], ["g1", "g2"])

    def test_every_finding_label_the_driver_can_produce_has_a_gate(self):
        labels = rv.findings(probe(queued=1, cut=1, ret=1, trapleaf=1, **{k: 1 for k in rv.R2_KINDS}))
        self.assertEqual(sorted(labels), sorted(["queued", "cut", "return", "trapleaf", *rv.R2_KINDS]))
        for label in labels:
            self.assertTrue(rv.gates_for([label], self.counters)[1], label)

    def test_a_union_is_sorted_and_has_each_gate_once(self):
        self.assertEqual(rv.gates_for(["will", "queued", "plain", "guts", "return"], self.counters)[1], ["p2", "g1", "g2", "g4", "g7"])

    def test_every_switch_counters_tsv_names_is_known_and_the_table_is_one_to_one(self):
        names = {env for cell in self.counters.values() if cell != "-" for env in cell.split("+")}
        self.assertTrue(names <= set(rv.ENV_TO_TOKEN), sorted(names - set(rv.ENV_TO_TOKEN)))
        self.assertEqual(len(set(rv.ENV_TO_TOKEN.values())), len(rv.ENV_TO_TOKEN))
        self.assertEqual(set(rv.ENV_TO_TOKEN.values()), set(rv.TOKEN_ORDER) - {"all"})
        self.assertNotIn("DECKGYM_ROUND2_OFF", rv.ENV_TO_TOKEN)

    def test_the_vocabulary_copies_are_the_classifiers(self):
        try:
            import tightened_rule as tr
        except ImportError:
            self.skipTest("tightened_rule.py is not in this folder (it is on the round-2 branch until it is merged): run again where it is")
        self.assertEqual(rv.R2_KINDS, tr.R2_KINDS)
        self.assertEqual(rv.R2_COUNTER_KIND, tr.R2_COUNTER_KIND)
        self.assertEqual((rv.BOTH_HALVES, rv.JUDGMENT), (tr.BOTH_HALVES, tr.JUDGMENT))


class DumpOutput(unittest.TestCase):
    def test_chosen_and_candidates_after_the_last_asked_about_line(self):
        d = rv.parse_dump(*dump_out(CHOSEN_A, SCORES_A))
        self.assertEqual((d["ok"], d["chosen"]), (True, CHOSEN_A))
        self.assertEqual(d["cands"], [(float(s), t) for s, t in SCORES_A])          # the stray PGDUMP line before PGTICK is not one

    def test_not_ok_without_a_choice_without_candidates_or_with_a_bad_return_code(self):
        self.assertFalse(rv.parse_dump(*dump_out(None, SCORES_A))["ok"])
        self.assertFalse(rv.parse_dump(*dump_out(CHOSEN_A, []))["ok"])
        self.assertFalse(rv.parse_dump(*dump_out(CHOSEN_A, SCORES_A, rc=3))["ok"])

    def test_candidates_printed_to_stdout_are_found_too(self):
        rc, out, err = dump_out(CHOSEN_A, SCORES_A)
        self.assertEqual(rv.parse_dump(rc, err + out, "")["cands"], [(float(s), t) for s, t in SCORES_A])

    def test_same_scores_is_oct_1s_rule(self):
        x = [(1.0, "a"), (2.0, "b")]
        self.assertTrue(rv.same_scores(x, [(1.0 + 1e-10, "a"), (2.0, "b")]))
        self.assertFalse(rv.same_scores(x, [(1.0 + 1e-8, "a"), (2.0, "b")]))
        self.assertFalse(rv.same_scores(x, [(1.0, "a"), (2.0, "c")]))
        self.assertFalse(rv.same_scores(x, x[:1]))


if __name__ == "__main__":
    unittest.main()
