#!/usr/bin/env python3
"""Tests for the resume and record checks in run_calibration.py and calibrate.py (Sept 29).

Synthetic data only: every deck, list, engine "binary" and CSV here is invented in a temporary folder, the engine is
never started (run_calibration.run is replaced by a stub), and nothing under the repo is written.

Run them in WSL (or any Linux), from the repo root:

    cd '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/decks/screen/panel_ladder_2026-09-26'
    python3 -B -m unittest -v test_calibration_safety      (standard library only; about a second)

The runner is Linux-only (folder lock, symlinks, POSIX permissions and paths), so on Windows this file skips itself with
a note instead of reporting failures that say nothing about the runner.

What they pin down (Dustin, Sept 29): an identical resume works; changed inputs and conflicting records fail clearly
BEFORE anything is appended or scored; valid records keep exactly the scores the original calibrate.py gave.
"""
import contextlib
import csv
import io
import json
import os
import shutil
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

linux_only = unittest.skipUnless(sys.platform.startswith("linux"),
                                 "run these tests in WSL or Linux: the runner they test is Linux-only "
                                 "(python3 -B -m unittest -v test_calibration_safety, from decks/screen/panel_ladder_2026-09-26)")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import calibrate  # noqa: E402
import run_calibration as rc  # noqa: E402

# Written out here, not read from the code under test, so a change to the runner's columns or to the fields it calls
# provenance shows up as a failing test instead of the tests silently following it.
FIELDS = ["deck_file", "opponent_file", "pilot", "games", "wins", "draws", "seat",
          "slot0_games", "slot0_wins", "slot0_draws", "slot1_games", "slot1_wins", "slot1_draws",
          "seed_slot0", "seed_slot1", "deck_pilot", "meta_pilot", "engine", "engine_sha256", "seconds",
          "schema", "deck_sha256", "opponent_sha256"]
REQUIRED = ("engine_sha256", "deck_sha256", "opponent_sha256", "deck_pilot", "meta_pilot", "seed_slot0", "seed_slot1",
            "slot0_games", "slot1_games", "slot0_wins", "slot1_wins", "slot0_draws", "slot1_draws")
ENGINE_A, ENGINE_B = "a" * 64, "b" * 64


def stub_result(n, seed):
    """What the stubbed engine reports for n games from seed: (player 0 wins, player 1 wins, draws). Deliberately lopsided,
    and with a draw count that differs between a pair's two slots (their seeds are 5,000 apart), so a run that swaps the two
    players, the two slots or the draws records visibly different numbers."""
    a = min(n // 3 + seed % 5, n)
    b = min(n // 4 + 1 + (seed // 5000) % 3, n - a)
    return a, b, n - a - b


def read_rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path, rows, fields=FIELDS):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


class Repo:
    """A throwaway repo root with decks, a fake screen folder, a fake engine file and a stubbed engine call."""

    def __init__(self, tc, npairs=2, working="kog3"):
        self.tmp = Path(tempfile.mkdtemp(prefix="cal_test_"))
        tc.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "repo"
        (self.root / "decks").mkdir(parents=True)
        self.screen = self.tmp / "screen"
        self.screen.mkdir()
        self.set_working(working)
        self.pairs = [self.add_pair(i) for i in range(npairs)]
        self.engine = self.tmp / "engine_bin"
        self.engine.write_bytes(b"engine-A")
        self.games_csv = self.tmp / "calibration_games.csv"
        self.write_games(self.pairs)
        self.out = self.tmp / "sim_results.csv"
        self.calls = []
        self.hook = None          # called with the number of engine calls so far, from inside the stubbed engine call
        fake = types.ModuleType("current_engine")
        fake.resolve = lambda project=None, override=None: self.engine
        for p in (mock.patch.object(calibrate, "SCREEN_DIR", str(self.screen)), mock.patch.object(rc, "ROOT", str(self.root)),
                  mock.patch.object(rc, "run", self._fake_run), mock.patch.dict(sys.modules, {"current_engine": fake}),
                  mock.patch.object(sys, "path", list(sys.path))):
            p.start()
            tc.addCleanup(p.stop)

    def set_working(self, pilot, meta=None, floor=None):
        (self.screen / "run_screen.py").write_text(
            f"ap.add_argument('--pilot', default='{pilot}', help='x')\nap.add_argument('--meta-pilot', default='{meta or pilot}', help='y')\n")
        (self.screen / "floor.py").write_text(f'FLOOR_PILOT = "{floor or pilot}"   # the working pilot\n')

    def add_pair(self, i, deck=None, opp=None):
        d, o = deck or f"decks/d{i}.txt", opp or f"decks/o{i}.txt"
        (self.root / d).write_text(f"20-card list {d}\n")
        (self.root / o).write_text(f"20-card list {o}\n")
        return d, o

    def write_games(self, pairs):
        with open(self.games_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["game_id", "deck_file", "opponent_file", "result", "usable"])
            for k, (d, o) in enumerate(pairs):
                w.writerow([f"g{k}", d, o, "W" if k % 2 == 0 else "L", 1])

    def _fake_run(self, engine, p0, p1, players, n, seed):
        self.calls.append((os.path.basename(p0), os.path.basename(p1), players, n, seed))
        if self.hook:
            self.hook(len(self.calls))
        return stub_result(n, seed)

    def call(self, *args):
        """Run the runner's main; returns (stdout, refusal message or None, engine calls made)."""
        self.calls.clear()
        argv = ["--games-csv", str(self.games_csv), "--out", str(self.out), "--games", "100", *args]
        buf, msg = io.StringIO(), None
        with contextlib.redirect_stdout(buf):
            try:
                rc.main(argv)
            except SystemExit as e:
                msg = str(e.code)
        return buf.getvalue(), msg, len(self.calls)

    def raw(self):
        return self.out.read_bytes()

    def rows(self):
        return read_rows(self.out)


@linux_only
class RunnerResume(unittest.TestCase):
    def setUp(self):
        self.w = Repo(self)

    def first_run(self):
        out, msg, calls = self.w.call()
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 4)   # 2 pairs x 2 slots
        return self.w.raw()

    def assertRefusedUntouched(self, msg, calls, before, *needles):
        self.assertIsNotNone(msg)
        self.assertTrue(msg.startswith("REFUSED"), msg)
        for n in needles:
            self.assertIn(n, msg)
        self.assertEqual(calls, 0, "the engine must not be started")
        self.assertEqual(self.w.raw(), before, "nothing may be appended or changed")

    def test_first_run_records_full_provenance(self):
        self.first_run()
        for r in self.w.rows():
            self.assertEqual(r["schema"], calibrate.PROVENANCE_SCHEMA)
            self.assertEqual(r["deck_pilot"], "kog3")
            self.assertEqual(r["meta_pilot"], "kog3")
            self.assertEqual(r["deck_sha256"], calibrate.file_sha256(self.w.root / r["deck_file"]))
            self.assertEqual(r["opponent_sha256"], calibrate.file_sha256(self.w.root / r["opponent_file"]))
            self.assertEqual(len(r["engine_sha256"]), 64)

    def test_identical_resume_reuses_everything_and_changes_nothing(self):
        before = self.first_run()
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 0)
        self.assertEqual(self.w.raw(), before)
        self.assertEqual(out.count("verified against this run's engine"), 2)

    def test_resume_plays_only_the_missing_pair_with_the_planned_seeds(self):
        before = self.first_run()
        full = self.w.rows()
        lines = before.decode().splitlines(True)
        self.w.out.write_text("".join(lines[:2]))                   # header + pair 0 only: an interrupted run
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 2)
        self.assertEqual([c[4] for c in self.w.calls], [21_107_010_000, 21_107_015_000])
        got = self.w.rows()
        self.assertEqual(len(got), 2)
        for a, b in zip(got, full):
            self.assertEqual({k: v for k, v in a.items() if k != "seconds"}, {k: v for k, v in b.items() if k != "seconds"})
        self.assertEqual(self.w.raw().decode().splitlines(True)[:2], lines[:2], "the finished row is kept byte for byte")

    def test_changed_engine_is_refused(self):
        before = self.first_run()
        self.w.engine.write_bytes(b"engine-B, a different build")
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "engine_sha256", "pair 0", "pair 1")

    def test_edited_deck_is_refused(self):
        before = self.first_run()
        (self.w.root / "decks/d0.txt").write_text("20-card list D0, two cards swapped\n")
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "deck_sha256", "pair 0")
        self.assertNotIn("pair 1", msg)

    def test_edited_opponent_is_refused(self):
        before = self.first_run()
        (self.w.root / "decks/o1.txt").write_text("20-card list O1 EDITED\n")
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "opponent_sha256", "pair 1")

    def test_line_endings_alone_do_not_count_as_a_change(self):
        before = self.first_run()
        (self.w.root / "decks/d0.txt").write_bytes(b"20-card list decks/d0.txt\r\n")   # the same list, Windows line endings
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual((calls, self.w.raw()), (0, before))

    def test_changed_game_count_is_refused(self):
        before = self.first_run()
        out, msg, calls = self.w.call("--resume", "--games", "200")
        self.assertRefusedUntouched(msg, calls, before, "games is 100 in the file, this run would use 200", "slot0_games")

    def test_changed_seed_block_is_refused(self):
        before = self.first_run()
        out, msg, calls = self.w.call("--resume", "--seed", "21107500000")
        self.assertRefusedUntouched(msg, calls, before, "seed_slot0")

    def test_a_pair_inserted_before_the_others_shifts_every_seed_and_is_refused(self):
        before = self.first_run()
        new = self.w.add_pair(9, "decks/a9.txt", "decks/b9.txt")     # sorts first, so it takes index 0 and the rest move down
        self.w.write_games([new] + self.w.pairs)
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "seed_slot0", "overlap seeds already used by line")
        self.assertIn("pair 1 (d0.txt vs o0.txt)", msg)              # the old pair 0 is now pair 1 and its seeds differ

    def test_other_pilots_never_reuse_a_row_and_leave_it_alone(self):
        before = self.first_run()
        out, msg, calls = self.w.call("--resume", "--pilot", "kp3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 4, "a pair finished under kog3 is not a finished pair under kp3")
        self.assertTrue(self.w.raw().startswith(before), "the kog3 rows are untouched")
        self.assertEqual([r["pilot"] for r in self.w.rows()], ["kog3", "kog3", "kp3", "kp3"])
        # same seeds under another pilot are a paired comparison, not a collision, and a later resume accepts both
        out, msg, calls = self.w.call("--resume", "--pilot", "kp3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 0)

    def test_one_side_on_another_pilot_is_its_own_label(self):
        before = self.first_run()
        out, msg, calls = self.w.call("--resume", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertEqual([r["pilot"] for r in self.w.rows()][2:], ["kog3|kp3", "kog3|kp3"])
        self.assertTrue(self.w.raw().startswith(before))

    def test_pilot_column_that_contradicts_the_recorded_pilots_is_refused(self):
        self.first_run()
        rows = self.w.rows()
        rows[0]["deck_pilot"] = "k3"                                 # label says kog3, the row says k3 played Dustin's deck
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "the pilot column says 'kog3' but deck_pilot is 'k3'", "deck_pilot")

    def test_one_bad_pair_stops_everything_before_any_engine_call_or_append(self):
        self.first_run()
        rows = self.w.rows()
        rows[1]["deck_sha256"] = "c" * 64                            # pair 1 was played with another deck; pair 0 is fine
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "pair 1", "deck_sha256")
        self.assertNotIn("pair 0 (", msg)

    def test_every_problem_is_listed_not_just_the_first(self):
        before = self.first_run()
        (self.w.root / "decks/d0.txt").write_text("edited\n")
        self.w.engine.write_bytes(b"engine-B")
        out, msg, calls = self.w.call("--resume", "--games", "200")
        self.assertRefusedUntouched(msg, calls, before, "deck_sha256", "engine_sha256", "games is 100", "slot1_games")

    def test_second_row_for_one_pair_is_refused(self):
        self.first_run()
        rows = self.w.rows()
        write_rows(self.w.out, rows + [dict(rows[1])])              # the same pair twice, same seeds
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "2 rows", "share simulated seeds")

    def test_overlapping_seeds_between_pairs_are_refused(self):
        self.first_run()
        rows = self.w.rows()
        rows[1]["seed_slot0"], rows[1]["seed_slot1"] = rows[0]["seed_slot0"], rows[0]["seed_slot1"]
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "seed_slot0")

    def test_rows_from_two_engines_in_one_file_are_refused(self):
        self.first_run()
        rows = self.w.rows()
        rows[1]["engine_sha256"] = "d" * 64
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "engine_sha256")

    def test_planned_seeds_used_by_another_pair_are_refused(self):
        out, msg, calls = self.w.call("--only", "1")                 # pair d0/o0 recorded at the first seed block
        self.assertIsNone(msg, out)
        new = self.w.add_pair(9, "decks/a9.txt", "decks/b9.txt")     # a different pair now sorts first and would take those seeds
        self.w.write_games([new] + self.w.pairs)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--only", "1")
        self.assertRefusedUntouched(msg, calls, before, "overlap seeds already used by line", "pair 0 (a9.txt vs b9.txt)")

    def test_existing_output_without_resume_is_not_appended_to(self):
        before = self.first_run()
        out, msg, calls = self.w.call()
        self.assertRefusedUntouched(msg, calls, before, "already holds 2 rows", "--resume")

    def test_older_header_is_refused_with_and_without_resume(self):
        old = FIELDS[:20]
        self.w.out.write_text(",".join(old) + "\n" + ",".join(["decks/d0.txt", "decks/o0.txt", "kog3", "100", "50", "0", "any"] + [""] * 13) + "\n")
        before = self.w.raw()
        for extra in ((), ("--resume",)):
            out, msg, calls = self.w.call(*extra)
            self.assertRefusedUntouched(msg, calls, before, "older or different header", "misaligned")

    def test_rows_without_provenance_are_not_reused_unless_accepted(self):
        self.first_run()
        rows = self.w.rows()
        for c in ("schema", "deck_sha256", "opponent_sha256"):
            rows[0][c] = ""
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "no full provenance", "--accept-unverified-resume", "schema")
        out, msg, calls = self.w.call("--resume", "--accept-unverified-resume")
        self.assertIsNone(msg, out)
        self.assertEqual((calls, self.w.raw()), (0, before))
        self.assertIn("UNVERIFIED", out)
        self.assertIn("WARNING", out)

    def test_accepting_unverified_still_checks_what_can_be_checked(self):
        self.first_run()
        rows = self.w.rows()
        for c in ("schema", "deck_sha256", "opponent_sha256"):
            rows[0][c] = ""
        rows[0]["engine_sha256"] = "e" * 64                          # and the engine it names is not this one
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--accept-unverified-resume")
        self.assertRefusedUntouched(msg, calls, before, "engine_sha256")

    def test_first_run_needs_no_flags_and_an_empty_file_is_a_new_file(self):
        self.w.out.write_text("")
        before, msg, calls = self.w.call()
        self.assertIsNone(msg, before)
        self.assertEqual(self.w.out.read_text().splitlines()[0], ",".join(FIELDS))

    # ---- found by the adversarial review of Sept 29; each was reproduced on the first version of this runner
    def test_a_last_row_or_header_without_a_final_newline_is_refused_not_glued(self):
        before = self.first_run()
        self.w.out.write_bytes(b"\n".join(before.rstrip(b"\n").split(b"\n")[:2]))       # header + pair 0, final newline trimmed
        raw = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, raw, "does not end with a newline", "glue")
        self.w.out.write_bytes(",".join(FIELDS).encode())                               # a header only, no newline
        raw = self.w.raw()
        out, msg, calls = self.w.call()
        self.assertRefusedUntouched(msg, calls, raw, "does not end with a newline")

    def test_one_pair_under_two_spellings_is_refused_before_any_game(self):
        d, o = self.w.pairs[0]
        for spelling in ("./" + d, d.upper(), d.replace("/", "//"), "decks/x/../d0.txt"):
            with open(self.w.games_csv, "a", newline="") as f:
                csv.writer(f).writerow(["gx", spelling, o, "W", 1])
            out, msg, calls = self.w.call()
            self.assertIn("names one pair under different spellings", msg, spelling)
            self.assertEqual(calls, 0)
            self.assertFalse(self.w.out.exists())
            self.w.write_games(self.w.pairs)

    def test_a_row_for_another_pair_from_another_engine_is_refused(self):
        out, msg, calls = self.w.call("--only", "1", "--seed", "22900000000")
        self.assertIsNone(msg, out)
        self.w.write_games([self.w.pairs[1]])                        # a different pair now, in a fresh seed block, on another engine
        self.w.engine.write_bytes(b"engine-B")
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--seed", "22900100000")
        self.assertRefusedUntouched(msg, calls, before, "a row for another pair was played with engine")

    def test_a_row_for_another_pair_that_records_a_file_as_it_was_is_refused(self):
        """The round-two blocker: a stray same-pilot row recorded d0 before it was edited; appending a new pair beside it
        would leave one file with two contents in the scored set."""
        for victim, kind in (("decks/d0.txt", "deck"), ("decks/o0.txt", "opponent")):
            w = Repo(self)
            w.add_pair(5, "decks/e5.txt", "decks/f5.txt")
            out, msg, calls = w.call("--only", "1", "--seed", "22900000000")            # pair (d0, o0) recorded with both files as they were
            self.assertIsNone(msg, out)
            (w.root / victim).write_text("edited after the row was written\n")
            # the next run plays a different pair that uses the edited file, into a fresh seed block
            w.write_games([("decks/d0.txt", "decks/f5.txt")] if kind == "deck" else [("decks/e5.txt", "decks/o0.txt")])
            before = w.raw()
            out, msg, calls = w.call("--resume", "--seed", "22900100000")
            self.assertIn(f"records the {kind} file {victim}", msg or out)
            self.assertIn("one file with two contents cannot share one scored set", msg or "")
            self.assertEqual((calls, w.raw()), (0, before))

    def test_an_unverified_row_for_another_pair_is_named_and_needs_the_flag_before_anything_is_appended_beside_it(self):
        out, msg, calls = self.w.call("--only", "1", "--seed", "22900000000")
        self.assertIsNone(msg, out)
        rows = self.w.rows()
        for c in ("schema", "deck_sha256", "opponent_sha256"):
            rows[0][c] = ""
        write_rows(self.w.out, rows)
        self.w.write_games([self.w.pairs[1]])
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--seed", "22900100000")
        self.assertRefusedUntouched(msg, calls, before, "line 2 (a pair not in this run) has no full provenance",
                                    "the scorer would refuse the whole file", "--accept-unverified-resume")
        out, msg, calls = self.w.call("--resume", "--seed", "22900100000", "--accept-unverified-resume")
        self.assertIsNone(msg, out)
        self.assertIn("kept as UNVERIFIED", out)

    def test_a_block_that_partly_overlaps_the_reserved_one_is_refused(self):
        for seed in ("21107100000", "21107000050", "21106995000"):
            out, msg, calls = self.w.call("--seed", seed)
            self.assertIn("overlaps part of the reserved block", msg, seed)
            self.assertEqual(calls, 0)
            self.assertFalse(self.w.out.exists())
        out, msg, calls = self.w.call("--seed", "21107000000")              # the block itself is fine
        self.assertIsNone(msg, out)

    def test_pilot_names_must_be_plain(self):
        for bad in (" kp3", "kp3 ", "kp3,x", "k|p", ""):
            out, msg, calls = self.w.call("--pilot", bad, "--meta-pilot", bad, "--allow-pilot-mismatch")
            self.assertIn("is not a pilot name", msg, repr(bad))
            self.assertEqual(calls, 0)
            self.assertFalse(self.w.out.exists())

    def test_seeds_the_engine_cannot_take_are_refused_and_a_custom_block_is_announced(self):
        for seed in ("-5000", str(2 ** 64 - 6000)):
            out, msg, calls = self.w.call("--seed", seed)
            self.assertIn("outside what the engine takes", msg, seed)
            self.assertEqual(calls, 0)
            self.assertFalse(self.w.out.exists())
        edge = 2 ** 64 - 20000                                       # two pairs need 20,000 seeds: this is exactly the last block
        out, msg, calls = self.w.call("--seed", str(edge))
        self.assertIsNone(msg, out)
        self.assertIn("are not the reserved block", out)
        self.assertEqual(max(c[4] for c in self.w.calls), edge + 15_000)

    def test_only_must_be_at_least_one(self):
        for bad in ("0", "-1"):
            with contextlib.redirect_stderr(io.StringIO()):
                out, msg, calls = self.w.call("--only", bad)
            self.assertEqual((msg, calls), ("2", 0))                 # argparse's usage error
            self.assertFalse(self.w.out.exists())

    def test_a_file_or_engine_changed_while_a_pair_plays_is_not_recorded_under_the_old_hash(self):
        self.w.hook = lambda n: (self.w.root / "decks/d0.txt").write_text("edited mid-run\n") if n == 1 else None
        out, msg, calls = self.w.call()
        self.assertIn("decks/d0.txt changed", msg)
        self.assertIn("while pair 0 was played", msg)
        self.assertEqual(self.w.out.read_text().splitlines(), [",".join(FIELDS)], "no row for the pair whose input moved")
        self.w.out.unlink()
        (self.w.root / "decks/d0.txt").write_text("20-card list decks/d0.txt\n")
        self.w.hook = lambda n: self.w.engine.write_bytes(b"engine replaced") if n == 1 else None
        out, msg, calls = self.w.call()
        self.assertIn("the engine binary changed", msg)
        self.assertEqual(self.w.out.read_text().splitlines(), [",".join(FIELDS)])

    def test_a_file_edited_before_a_later_pair_is_caught_and_earlier_pairs_are_kept(self):
        self.w.hook = lambda n: (self.w.root / "decks/d1.txt").write_text("edited\n") if n == 3 else None   # while pair 1 is played
        out, msg, calls = self.w.call()
        self.assertIn("while pair 1 was played", msg)
        self.assertEqual(len(self.w.rows()), 1, "pair 0 was finished and stays recorded")

    def test_a_second_run_cannot_start_while_one_holds_the_folder(self):
        seen = {}

        def hook(n):
            if n == 1:
                try:
                    rc.main(["--games-csv", str(self.w.games_csv), "--out", str(self.w.out), "--games", "100", "--resume"])
                except SystemExit as e:
                    seen["msg"] = str(e.code)
        self.w.hook = hook
        out, msg, calls = self.w.call()
        self.assertIsNone(msg, out)
        self.assertIn("another calibration run holds the folder", seen["msg"])
        self.assertEqual(len(self.w.rows()), 2, "each pair recorded exactly once")
        out, msg, calls = self.w.call("--resume")                   # and the lock is released afterwards
        self.assertIsNone(msg, out)

    def test_a_pooled_row_edited_to_a_seat_is_refused(self):
        self.first_run()
        rows = self.w.rows()
        rows[0]["seat"] = "first"
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "seat is 'first'", "only pooled")

    def test_an_identical_resume_of_a_read_only_finished_file_needs_no_write_access(self):
        before = self.first_run()
        mtime = os.stat(self.w.out).st_mtime_ns
        os.chmod(self.w.out, 0o444)
        self.addCleanup(os.chmod, self.w.out, 0o644)
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual((calls, self.w.raw(), os.stat(self.w.out).st_mtime_ns), (0, before, mtime))

    def test_a_byte_order_mark_header_is_named_in_the_refusal(self):
        before = self.first_run()
        self.w.out.write_bytes(b"\xef\xbb\xbf" + before)
        raw = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, raw, "byte-order mark", "older or different header")

    def test_a_games_file_without_the_usable_column_is_refused_cleanly(self):
        self.w.games_csv.write_text("game_id,deck_file,opponent_file,result\ng0,decks/d0.txt,decks/o0.txt,W\n")
        out, msg, calls = self.w.call()
        self.assertIn("is missing columns ['usable']", msg)
        self.assertEqual(calls, 0)

    def test_a_hash_that_was_cut_short_shows_as_cut(self):
        self.first_run()
        rows = self.w.rows()
        rows[0]["opponent_sha256"] = rows[0]["opponent_sha256"][:40]
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, before, "opponent_sha256", "(40 characters)")

    # ---- gaps the mutation review found in the first 60 tests: every guard must be pinned by a test that fails without it
    def test_every_recorded_field_is_verified_on_resume(self):
        self.first_run()
        base = self.w.rows()
        changes = {"engine_sha256": "e" * 64, "deck_sha256": "c" * 64, "opponent_sha256": "d" * 64, "deck_pilot": "k3",
                   "meta_pilot": "k3", "games": "102", "slot0_games": "51", "slot1_games": "49",
                   "seed_slot0": str(int(base[0]["seed_slot0"]) + 1), "seed_slot1": str(int(base[0]["seed_slot1"]) + 1)}
        for field, value in changes.items():
            rows = [dict(r) for r in base]
            rows[0][field] = value
            write_rows(self.w.out, rows)
            before = self.w.raw()
            out, msg, calls = self.w.call("--resume")
            if field in ("games", "slot0_games", "slot1_games", "seed_slot0", "seed_slot1"):     # numbers are shown with commas
                needle = f"{field} is {int(value):,} in the file, this run would use {int(base[0][field]):,}"
            elif len(value) <= 16:
                needle = f"{field} is {value} in the file, this run would use {base[0][field]}"
            else:                                                                                 # a hash is shown cut, with its length
                needle = f"{field} is {value[:16]}...(64 characters) in the file, this run would use {base[0][field][:16]}...(64 characters)"
            self.assertRefusedUntouched(msg, calls, before, needle)
            self.assertIn("pair 0", msg, field)

    def test_results_land_on_the_right_side_slot_and_pilot_with_odd_game_counts(self):
        out, msg, calls = self.w.call("--games", "101", "--pilot", "kog3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        s0, s1 = 21_107_000_000, 21_107_005_000
        self.assertEqual(self.w.calls[:2], [("d0.txt", "o0.txt", "kog3,kp3", 50, s0), ("o0.txt", "d0.txt", "kp3,kog3", 51, s1)])
        (a1, b1, d1), (a2, b2, d2) = stub_result(50, s0), stub_result(51, s1)
        self.assertNotEqual(d1, d2, "the stub must give the two slots different draw counts, or a swap of them goes unseen")
        r = self.w.rows()[0]
        # slot 0: Dustin's deck is player 0 (his wins are a1). slot 1: he is player 1 (his wins are b2). Draws add up.
        self.assertEqual((int(r["slot0_wins"]), int(r["slot1_wins"]), int(r["wins"])), (a1, b2, a1 + b2))
        self.assertEqual((int(r["slot0_draws"]), int(r["slot1_draws"]), int(r["draws"])), (d1, d2, d1 + d2))
        self.assertEqual((int(r["slot0_games"]), int(r["slot1_games"]), int(r["games"])), (50, 51, 101))
        self.assertEqual((r["seat"], r["pilot"], r["deck_pilot"], r["meta_pilot"], r["seed_slot1"]), ("any", "kog3|kp3", "kog3", "kp3", str(s1)))
        self.assertEqual(r["engine"], "../engine_bin")            # the engine path is recorded relative to the repo root
        self.assertEqual(self.w.rows()[0]["schema"], calibrate.PROVENANCE_SCHEMA)

    def test_a_crash_after_one_pair_keeps_that_pair_and_the_resume_finishes_identically(self):
        def boom(n):
            if n == 3:
                raise RuntimeError("the machine went away")
        self.w.hook = boom
        with self.assertRaises(RuntimeError):
            self.w.call()
        self.assertEqual(len(self.w.rows()), 1, "the finished pair was flushed at once")
        self.assertTrue(self.w.raw().endswith(b"\n"))
        self.w.hook = None
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 2)
        crashed = [{k: v for k, v in r.items() if k != "seconds"} for r in self.w.rows()]
        fresh = Repo(self)
        out, msg, calls = fresh.call()
        self.assertEqual(crashed, [{k: v for k, v in r.items() if k != "seconds"} for r in fresh.rows()])

    def test_a_missing_input_file_is_refused_before_anything_is_created(self):
        (self.w.root / "decks/o1.txt").unlink()
        out, msg, calls = self.w.call()
        self.assertIn("pair 1: cannot read decks/o1.txt", msg)
        self.assertEqual(calls, 0)
        self.assertFalse(self.w.out.exists())

    def test_an_engine_that_cannot_be_resolved_is_refused_before_anything_is_created(self):
        def refuse(project=None, override=None):
            raise ValueError("engine differs from available_release")
        sys.modules["current_engine"].resolve = refuse
        out, msg, calls = self.w.call()
        self.assertIn("this runs only the manifest's available release", msg)
        self.assertFalse(self.w.out.exists())

    def test_fewer_than_two_games_is_refused(self):
        out, msg, calls = self.w.call("--games", "1")
        self.assertIn("--games must be at least 2", msg)
        self.assertEqual(calls, 0)

    def test_a_header_only_file_with_its_newline_is_a_new_file_and_gets_one_header(self):
        self.w.out.write_text(",".join(FIELDS) + "\n")
        out, msg, calls = self.w.call()
        self.assertIsNone(msg, out)
        self.assertEqual(self.w.out.read_text().count(",".join(FIELDS)), 1)
        self.assertEqual(len(self.w.rows()), 2)

    def test_blocks_that_touch_are_not_an_overlap_but_one_shared_seed_is(self):
        base = 22_900_000_000                                                    # outside the reserved block, so any seed is allowed
        out, msg, calls = self.w.call("--only", "1", "--games", "100", "--seed", str(base))   # pair d0/o0: [B, B+50) and [B+5000, B+5050)
        self.assertIsNone(msg, out)
        self.w.write_games([self.w.add_pair(9, "decks/a9.txt", "decks/b9.txt")])
        out, msg, calls = self.w.call("--resume", "--seed", str(base + 50))      # starts exactly where the first block ends
        self.assertIsNone(msg, out)
        self.assertEqual(len(self.w.rows()), 2)
        self.w.out.unlink()
        self.w.write_games([self.w.pairs[0]])
        self.w.call("--only", "1", "--games", "100", "--seed", str(base))
        self.w.write_games([self.w.add_pair(8, "decks/a8.txt", "decks/b8.txt")])
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--seed", str(base + 49))      # one seed inside the first block
        self.assertRefusedUntouched(msg, calls, before, "overlap seeds already used by line 2")
        self.w.out.unlink()
        self.w.write_games([self.w.pairs[0]])
        self.w.call("--only", "1", "--games", "100", "--seed", str(base))
        self.w.write_games([self.w.add_pair(7, "decks/a7.txt", "decks/b7.txt")])
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume", "--seed", str(base - 5000 + 10))   # only ITS slot 1 range lands inside the first block
        self.assertRefusedUntouched(msg, calls, before, "planned slot 1 seeds 22,900,000,010..22,900,000,059", "line 2")
        self.assertNotIn("planned slot 0", msg)

    def test_rows_of_pairs_that_are_not_in_this_run_are_left_alone_and_said_so(self):
        out, msg, calls = self.w.call("--only", "1", "--seed", "22900000000")
        self.assertIsNone(msg, out)
        before = self.w.raw()
        self.w.write_games([self.w.pairs[1]])
        out, msg, calls = self.w.call("--resume", "--seed", "22900100000")
        self.assertIsNone(msg, out)
        self.assertIn("WARNING: 1 row in sim_results.csv belong to pairs or pilots not in this run", out)
        self.assertTrue(self.w.raw().startswith(before), "the other pair's row is untouched")

    def test_an_accepted_unverified_pair_is_announced_as_unverified_and_never_as_verified(self):
        self.first_run()
        rows = self.w.rows()
        for c in ("schema", "deck_sha256", "opponent_sha256"):
            rows[0][c] = ""
        write_rows(self.w.out, rows)
        out, msg, calls = self.w.call("--resume", "--accept-unverified-resume")
        self.assertIsNone(msg, out)
        line0 = [l for l in out.splitlines() if l.startswith("pair 0:")][0]
        line1 = [l for l in out.splitlines() if l.startswith("pair 1:")][0]
        self.assertIn("UNVERIFIED (accepted)", line0)
        self.assertNotIn("verified against", line0)
        self.assertIn("verified against this run's engine, deck and opponent contents", line1)

    def test_a_working_pilot_that_cannot_be_read_needs_both_pilots_named(self):
        (self.w.screen / "run_screen.py").unlink()
        for args in (("--pilot", "kog3"), ("--meta-pilot", "kog3"), ()):
            out, msg, calls = self.w.call(*args, "--allow-pilot-mismatch")
            self.assertIn("cannot be verified", msg, args)

    def test_a_maximal_ten_thousand_game_run_resumes_when_the_next_pair_touches_it(self):
        out, msg, calls = self.w.call("--games", "10000", "--only", "1")
        self.assertIsNone(msg, out)
        out, msg, calls = self.w.call("--games", "10000", "--resume")             # pair 1's block starts exactly where pair 0's ends
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 2)
        out, msg, calls = self.w.call("--games", "10000", "--resume")
        self.assertEqual((msg, calls), (None, 0))

    def test_an_identical_resume_of_an_odd_game_count_works(self):
        out, msg, calls = self.w.call("--games", "101")
        self.assertIsNone(msg, out)
        before = self.w.raw()
        out, msg, calls = self.w.call("--games", "101", "--resume")
        self.assertEqual((msg, calls, self.w.raw()), (None, 0, before))

    def test_a_pilot_field_that_contradicts_an_unverified_row_is_not_accepted_with_it(self):
        for blank, keep in (("deck_pilot", "meta_pilot"), ("meta_pilot", "deck_pilot")):
            w = Repo(self)
            w.call()
            rows = w.rows()
            for c in ("schema", blank):
                rows[0][c] = ""
            rows[0][keep] = "kp3"                                # the label says kog3 on both sides; this row says otherwise
            write_rows(w.out, rows)
            before = w.raw()
            out, msg, calls = w.call("--resume", "--accept-unverified-resume")
            self.assertIn(keep, msg or "")
            self.assertEqual((calls, w.raw()), (0, before))

    def test_rows_of_another_pilot_from_another_engine_do_not_block_a_resume(self):
        self.w.call()
        self.w.call("--resume", "--pilot", "kp3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        rows = self.w.rows()
        for r in rows:
            if r["pilot"] == "kp3":
                r["engine_sha256"] = "e" * 64
        write_rows(self.w.out, rows)
        before = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual((calls, self.w.raw()), (0, before))

    def test_a_missing_deck_or_opponent_file_is_refused_for_a_new_run_and_for_a_resume(self):
        before = self.first_run()
        for victim in ("decks/d1.txt", "decks/o0.txt"):
            (self.w.root / victim).rename(self.w.root / (victim + ".gone"))
            out, msg, calls = self.w.call("--resume")
            self.assertRefusedUntouched(msg, calls, before, f"cannot read {victim}")
            (self.w.root / (victim + ".gone")).rename(self.w.root / victim)

    # ---- round two of the review: files that cannot be read or written end in a refusal, never a traceback
    def test_files_that_cannot_be_read_or_written_end_in_a_refusal_that_says_what_was_kept(self):
        tail = "nothing was run and nothing was appended"
        self.w.out.write_bytes((",".join(FIELDS) + "\n").encode("utf-16"))               # what PowerShell's > writes
        out, msg, calls = self.w.call("--resume")
        self.assertIn("could not read or write a file (UnicodeDecodeError", msg)
        self.assertIn(tail, msg)
        self.assertEqual(calls, 0)
        self.w.out.unlink()
        out, msg, calls = self.w.call("--games-csv", str(self.w.tmp / "nope.csv"))
        self.assertIn("could not read or write a file (FileNotFoundError", msg)
        self.w.out = self.w.tmp / "no_such_folder" / "sim_results.csv"
        out, msg, calls = self.w.call()
        self.assertIn("could not read or write a file (FileNotFoundError", msg)
        self.assertEqual(calls, 0)
        self.w.out = self.w.tmp / "a_folder"
        self.w.out.mkdir()
        out, msg, calls = self.w.call()
        self.assertIn("could not read or write a file (IsADirectoryError", msg)
        self.assertEqual(calls, 0)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can write to a read-only file")
    def test_a_failed_write_says_a_row_may_be_cut_and_a_closed_output_is_not_blamed_on_a_file(self):
        real = csv.DictWriter

        class FullDisk(real):                                       # the Nth write fails, as a full disk's would
            fail_on, seen = 1, 0

            def writerow(me, row):
                FullDisk.seen += 1
                if FullDisk.seen == FullDisk.fail_on:
                    raise OSError(28, "No space left on device")
                return super().writerow(row)

        for fail_on, kept in ((1, 0), (3, 1)):                     # the header itself, then the second pair's row
            FullDisk.fail_on, FullDisk.seen = fail_on, 0
            if self.w.out.exists():
                self.w.out.unlink()
            with mock.patch.object(csv, "DictWriter", FullDisk):
                out, msg, calls = self.w.call()
            self.assertIn("could not read or write a file (OSError", msg)
            self.assertIn(f"a row may have been written only in part (the {kept} pair(s) before it are complete)", msg)
            self.assertIn("use a new --out", msg)
            self.assertNotIn("nothing was run and nothing was appended", msg)
            self.assertNotIn("nothing further was appended", msg)
        self.w.out.unlink()
        w = self.w
        w.calls.clear()

        class Gone(io.StringIO):                                    # stdout closed after the first pair ran (a pipe into head)
            def write(me, text):
                if len(w.calls) >= 2:
                    raise BrokenPipeError(32, "Broken pipe")
                return super().write(text)
        argv = ["--games-csv", str(w.games_csv), "--out", str(w.out), "--games", "100"]
        with contextlib.redirect_stdout(Gone()), self.assertRaises(SystemExit) as cm:
            rc.main(argv)
        msg = str(cm.exception.code)
        self.assertIn("STOPPED: the output was closed", msg)
        self.assertIn("not a file problem", msg)
        self.assertIn("--resume continues from there", msg)
        self.assertNotIn("REFUSED", msg)
        self.assertTrue(w.raw().endswith(b"\n"))
        kept_rows = len(w.rows())
        self.assertLess(kept_rows, 2)                               # the second pair never ran
        out, msg, calls = w.call("--resume")
        self.assertIsNone(msg, out)
        self.assertEqual([r["deck_file"] for r in w.rows()], ["decks/d0.txt", "decks/d1.txt"])
        self.assertEqual(calls, 2 * (2 - kept_rows))                # only what was missing was played

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root can write to a read-only file")
    def test_a_read_only_output_with_a_pair_still_to_play_is_refused_and_keeps_what_it_has(self):
        out, msg, calls = self.w.call("--only", "1")
        self.assertIsNone(msg, out)
        before = self.w.raw()
        os.chmod(self.w.out, 0o444)
        self.addCleanup(os.chmod, self.w.out, 0o644)
        out, msg, calls = self.w.call("--resume")
        self.assertIn("could not read or write a file (PermissionError", msg)
        self.assertIn("nothing was run and nothing was appended", msg)
        self.assertEqual((calls, self.w.raw()), (0, before))

    def test_a_resume_of_a_missing_empty_or_header_only_file_is_refused_and_a_fresh_start_is_a_run_without_resume(self):
        for name, content in (("missing", None), ("empty", b""), ("header only", (",".join(FIELDS) + "\n").encode())):
            if self.w.out.exists():
                self.w.out.unlink()
            if content is not None:
                self.w.out.write_bytes(content)
            out, msg, calls = self.w.call("--resume")
            self.assertIn("--resume was given but sim_results.csv", msg, name)
            self.assertIn("nothing to resume", msg, name)
            self.assertIn("leave out --resume", msg, name)
            self.assertIn("nothing was run and nothing was appended", msg, name)
            self.assertEqual(calls, 0, name)
            self.assertEqual(self.w.out.read_bytes() if content is not None else self.w.out.exists(),
                             content if content is not None else False, name)
        self.w.out.unlink()
        out, msg, calls = self.w.call()                                       # a fresh start needs no --resume
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 4)
        out, msg, calls = self.w.call("--resume")                             # and an identical resume of it writes nothing
        self.assertIn("nothing written: every pair (2) was already in sim_results.csv, the file is unchanged", out)
        self.assertNotIn("wrote ", out)

    def test_an_empty_plan_is_refused(self):
        self.w.games_csv.write_text("game_id,deck_file,opponent_file,result,usable\n")
        out, msg, calls = self.w.call()
        self.assertIn("no usable pairs in calibration_games.csv", msg)
        self.assertEqual(calls, 0)
        self.assertFalse(self.w.out.exists())

    def test_the_folder_lock_follows_the_real_folder_not_the_spelling_of_it(self):
        real = self.w.tmp / "realdir"
        real.mkdir()
        (self.w.tmp / "linkdir").symlink_to(real)
        self.w.out = self.w.tmp / "linkdir" / "sim_results.csv"
        seen = {}

        def hook(n):
            if n == 1:
                try:
                    rc.main(["--games-csv", str(self.w.games_csv), "--out", str(real / "sim_results.csv"), "--games", "100", "--resume"])
                except SystemExit as e:
                    seen["msg"] = str(e.code)
        self.w.hook = hook
        out, msg, calls = self.w.call()
        self.assertIsNone(msg, out)
        self.assertIn("another calibration run holds the folder", seen["msg"])
        self.assertEqual(len(self.w.rows()), 2)

    def test_a_different_header_names_the_column_and_a_repeated_header_line_is_recognised(self):
        before = self.first_run()
        swapped = list(FIELDS)
        swapped[0], swapped[1] = swapped[1], swapped[0]
        text = before.decode().splitlines(True)
        self.w.out.write_text(",".join(swapped) + "\n" + "".join(text[1:]))
        raw = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, raw, "column 1 is 'opponent_file' where this runner writes 'deck_file'")
        self.w.out.write_bytes(before + before)                                            # two copies joined end to end
        raw = self.w.raw()
        out, msg, calls = self.w.call("--resume")
        self.assertRefusedUntouched(msg, calls, raw, "this line repeats the header", "nothing was run and nothing was appended")


@linux_only
class EngineOutput(unittest.TestCase):
    """rc.run() parses the engine's text; tested with subprocess.run replaced, so no engine is ever started."""

    def patched(self, text, code=0):
        return mock.patch.object(rc.subprocess, "run", return_value=types.SimpleNamespace(stdout=text, stderr="", returncode=code))

    def test_the_three_counts_are_parsed_and_the_command_line_is_exact(self):
        with self.patched("noise\nPlayer 0 won: 3\nPlayer 1 won: 5\nDraws: 2\n") as m:
            self.assertEqual(rc.run("eng", "a.txt", "b.txt", "kog3,kp3", 10, 77), (3, 5, 2))
        self.assertEqual(m.call_args[0][0], ["eng", "simulate", "--num", "10", "--players", "kog3,kp3", "--seed", "77",
                                             "--seed-stream", "-p", "a.txt", "b.txt"])

    def test_a_count_that_does_not_add_up_or_a_refusal_is_not_recorded(self):
        with self.patched("Player 0 won: 3\nPlayer 1 won: 5\nDraws: 2\n"), self.assertRaises(SystemExit) as cm:
            rc.run("eng", "a", "b", "x,y", 11, 1)
        self.assertIn("engine reported 3+5+2 results for 11 games", str(cm.exception.code))
        with self.patched("error: unknown player kxx", code=2), self.assertRaises(SystemExit) as cm:
            rc.run("eng", "a", "b", "x,y", 10, 1)
        self.assertIn("engine refused a vs b (exit 2)", str(cm.exception.code))

    def test_the_engine_runs_from_the_repo_root_and_counts_printed_on_stderr_are_read_too(self):
        with self.patched("Player 0 won: 1\nPlayer 1 won: 1\nDraws: 0\n") as m:
            rc.run("eng", "a", "b", "x,y", 2, 1)
        self.assertEqual((m.call_args[1]["cwd"], m.call_args[1]["capture_output"], m.call_args[1]["text"]), (rc.ROOT, True, True))
        only_stderr = types.SimpleNamespace(stdout="", stderr="Player 0 won: 3\nPlayer 1 won: 5\nDraws: 2\n", returncode=0)
        with mock.patch.object(rc.subprocess, "run", return_value=only_stderr):
            self.assertEqual(rc.run("eng", "a", "b", "x,y", 10, 1), (3, 5, 2))

    def test_output_missing_one_count_line_is_a_clear_refusal_not_a_traceback(self):
        for text in ("Player 0 won: 3\nPlayer 1 won: 1\n", "Player 0 won: 3\nDraws: 0\n", "Player 0 won: 3\n"):
            with self.patched(text), self.assertRaises(SystemExit) as cm:
                rc.run("eng", "a.txt", "b.txt", "x,y", 4, 1)
            msg = str(cm.exception.code)
            self.assertIn("engine output could not be read (a count is missing) for a.txt vs b.txt", msg)
            self.assertIn("Player 0 won: 3", msg)                   # the tail of what the engine printed is shown


@linux_only
class RunnerLayout(unittest.TestCase):
    def test_games_beyond_the_slot_spacing_are_refused_even_for_a_plan_only_run(self):
        w = Repo(self)
        for extra in ((), ("--pairs-only",)):
            out, msg, calls = w.call(*extra, "--games", "10001")
            self.assertIn("overflows the reserved seed spacing", msg)
            self.assertEqual(calls, 0)
            self.assertFalse(w.out.exists())
        out, msg, calls = w.call("--games", "12000", "--pairs-only")
        self.assertIn("overflows the reserved seed spacing", msg)

    def test_exactly_ten_thousand_games_fit(self):
        w = Repo(self, npairs=1)
        out, msg, calls = w.call("--games", "10000")
        self.assertIsNone(msg, out)
        self.assertEqual([c[4] for c in w.calls], [21_107_000_000, 21_107_005_000])
        self.assertEqual([c[3] for c in w.calls], [5000, 5000])

    def test_more_pairs_than_the_reserved_block_are_refused(self):
        w = Repo(self, npairs=21)
        out, msg, calls = w.call("--games", "2", "--pairs-only")
        self.assertIn("21 pairs need 210,000 seeds", msg)
        self.assertIn("20 pairs", msg)
        out, msg, calls = w.call("--games", "2", "--only", "20")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 40)
        self.assertEqual(max(c[4] for c in w.calls), 21_107_195_000)   # stays inside 21,107,199,999


@linux_only
class RunnerPilot(unittest.TestCase):
    def test_default_is_the_working_pilot_on_both_sides_and_says_so(self):
        w = Repo(self, npairs=1)
        out, msg, calls = w.call()
        self.assertIsNone(msg, out)
        self.assertEqual({(r["deck_pilot"], r["meta_pilot"], r["pilot"]) for r in w.rows()}, {("kog3", "kog3", "kog3")})
        self.assertIn("pilot check: kog3 on both sides, the project's working pilot", out)
        self.assertEqual(w.calls[0][2], "kog3,kog3")
        self.assertEqual(w.calls[1][2], "kog3,kog3")

    def test_a_different_pilot_is_refused_unless_deliberate(self):
        w = Repo(self, npairs=1)
        for args in (("--pilot", "kp3", "--meta-pilot", "kp3"), ("--pilot", "kp3"), ("--meta-pilot", "kp3")):
            out, msg, calls = w.call(*args)
            self.assertIn("differ from the project's working pilot kog3", msg)
            self.assertIn("--allow-pilot-mismatch", msg)
            self.assertEqual(calls, 0)
            self.assertFalse(w.out.exists())
        out, msg, calls = w.call("--pairs-only", "--pilot", "kp3", "--meta-pilot", "kp3")
        self.assertIn("differ from the project's working pilot", msg, "a plan-only run must not print a plan for the wrong bot")

    def test_a_deliberate_mismatch_runs_and_is_recorded_and_announced(self):
        w = Repo(self, npairs=1)
        out, msg, calls = w.call("--pilot", "kp3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertIn("NOTE (pilot mismatch, allowed)", out)
        self.assertEqual({r["pilot"] for r in w.rows()}, {"kp3"})

    def test_screen_and_floor_disagreeing_is_refused(self):
        w = Repo(self, npairs=1)
        w.set_working("kog3", floor="kp3")
        out, msg, calls = w.call()
        self.assertIn("cannot be verified", msg)
        self.assertIn("disagree", msg)
        self.assertEqual(calls, 0)

    def test_unreadable_working_pilot_is_refused_unless_both_pilots_are_named_deliberately(self):
        w = Repo(self, npairs=1)
        (w.screen / "run_screen.py").unlink()
        out, msg, calls = w.call()
        self.assertIn("cannot be verified", msg)
        out, msg, calls = w.call("--pilot", "kog3", "--meta-pilot", "kog3")
        self.assertIn("cannot be verified", msg)
        out, msg, calls = w.call("--pilot", "kog3", "--meta-pilot", "kog3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertIn("could not be verified", out)

    def test_a_meta_pilot_default_that_differs_from_the_pilot_or_the_floor_is_refused(self):
        w = Repo(self, npairs=1)
        for pilot, meta, floor in (("kog3", "kp3", "kog3"), ("kp3", "kog3", "kog3"), ("kog3", "kog3", "kp3")):
            w.set_working(pilot, meta=meta, floor=floor)
            out, msg, calls = w.call()
            self.assertIn("disagree on the working pilot", msg, (pilot, meta, floor))
            self.assertEqual(calls, 0)
            self.assertFalse(w.out.exists())


GAMES = [("d0", "o0", "W", "1"), ("d0", "o0", "L", "0"), ("d0", "o0", "W", ""), ("d1", "o1", "L", "1"), ("d1", "o1", "L", "0"),
         ("d2", "o2", "W", ""), ("d2", "o2", "W", "1"), ("d2", "o2", "L", ""), ("d2", "o2", "W", "0")]
# Computed with the ORIGINAL calibrate.py (git HEAD before Sept 29) on the fixture below: draws "half", boot 300, seed 7.
GOLD = {"n": 9, "wins": 5, "base_rate": 0.5555555555555556, "mean_sim_chance": 0.5211111111111112, "brier_sim": 0.19469999999999998,
        "brier_base": 0.2469135802469136, "brier_base_loo": 0.3125, "skill_vs_base": 0.21146500000000013,
        "skill_vs_base_loo": 0.3769600000000001, "loglik_sim": -5.192204895153763, "loglik_base": -6.18265418937591,
        "llr_bits": 1.4289162850262653, "llr_bits_loo": 3.1693817435976417, "brier_diff_base_minus_sim": 0.052213580246913596}
GOLD_BOOT = {"boot_brier_diff": (-0.0037877006172839078, 0.11327708333333335, 0.94),
             "boot_llr_bits": (-0.060979026934224426, 3.0657796297139734, 0.94),
             "boot_brier_diff_loo": (0.06166777777777782, 0.1817040277777778, 1.0),
             "boot_llr_bits_loo": (1.6762761889812268, 4.904439066111886, 1.0),
             "boot_brier_sim": (0.13503055555555557, 0.24495319444444444, 1.0)}
GOLD_P = [0.7, 0.56, 0.56, 0.3, 0.3, 0.605, 0.605, 0.605, 0.455]
# (deck, opponent, games, wins, draws, seat)
SIM = [("d0", "o0", 200, 110, 4, "any"), ("d1", "o1", 200, 60, 0, "any"), ("d2", "o2", 200, 120, 2, "any"),
       ("d0", "o0", 100, 70, 0, "first"), ("d2", "o2", 100, 45, 1, "second")]


@linux_only
class ScoringBase(unittest.TestCase):
    """The fixtures the scorer's tests share (no tests of its own)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cal_score_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.root = self.tmp / "repo"
        (self.root / "decks").mkdir(parents=True)
        for n in ("d0", "o0", "d1", "o1", "d2", "o2"):
            (self.root / "decks" / f"{n}.txt").write_text(f"20-card list {n}\n")
        self.screen = self.tmp / "screen"
        self.screen.mkdir()
        (self.screen / "run_screen.py").write_text("ap.add_argument('--pilot', default='kog3')\nap.add_argument('--meta-pilot', default='kog3')\n")
        (self.screen / "floor.py").write_text('FLOOR_PILOT = "kog3"\n')
        p = mock.patch.object(calibrate, "SCREEN_DIR", str(self.screen))
        p.start()
        self.addCleanup(p.stop)
        self.games = self.tmp / "g.csv"
        with open(self.games, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["game_id", "date", "deck_file", "opponent_file", "opponent_key", "list_match", "went_first", "result", "usable"])
            for k, (d, o, r, wf) in enumerate(GAMES):
                w.writerow([f"g{k}", f"2026-09-2{k % 9}", f"decks/{d}.txt", f"decks/{o}.txt", o, "exact", wf, r, 1])
        self.sim = self.tmp / "sim.csv"

    # -- fixtures
    def row(self, d="d0", o="o0", games=200, wins=110, draws=4, seat="any", pilot="kog3", seed=21_107_000_000, engine=ENGINE_A, **over):
        h0, h1 = games // 2, games - games // 2
        r = dict(deck_file=f"decks/{d}.txt", opponent_file=f"decks/{o}.txt", pilot=pilot, games=games, wins=wins, draws=draws, seat=seat,
                 slot0_games=h0, slot0_wins=wins // 2, slot0_draws=draws // 2, slot1_games=h1, slot1_wins=wins - wins // 2,
                 slot1_draws=draws - draws // 2, seed_slot0=seed, seed_slot1=seed + 5000, deck_pilot=pilot.split("|")[0],
                 meta_pilot=pilot.split("|")[-1], engine="engine_bin", engine_sha256=engine, seconds="1.0",
                 schema=calibrate.PROVENANCE_SCHEMA, deck_sha256=calibrate.file_sha256(self.root / "decks" / f"{d}.txt"),
                 opponent_sha256=calibrate.file_sha256(self.root / "decks" / f"{o}.txt"))
        r.update(over)
        return r

    def full_fixture(self):
        return [self.row(d, o, g, w, dr, seat, seed=21_107_000_000 + 10_000 * i) for i, (d, o, g, w, dr, seat) in enumerate(SIM)]

    def write(self, rows, fields=FIELDS):
        write_rows(self.sim, rows, fields)

    def write_minimal(self):
        rows = [dict(deck_file=f"decks/{d}.txt", opponent_file=f"decks/{o}.txt", pilot="kog3", games=g, wins=w, draws=dr, seat=s)
                for d, o, g, w, dr, s in SIM]
        write_rows(self.sim, rows, ["deck_file", "opponent_file", "pilot", "games", "wins", "draws", "seat"])

    def argv(self, *args, boot=300, seed=7, repo_root=True):
        argv = ["--sim", str(self.sim), "--games", str(self.games), "--draws", "half", "--boot", str(boot), "--seed", str(seed)]
        if repo_root:
            argv += ["--repo-root", str(self.root)]
        return argv + list(args)

    def score(self, *args, **kw):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = calibrate.main(self.argv(*args, **kw))
        return res, buf.getvalue()

    def refused(self, *args, **kw):
        """Run the scorer expecting a refusal; the capture is around calibrate.main itself, so anything printed before the
        refusal would be seen here."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            calibrate.main(self.argv(*args, **kw))
        self.assertEqual(buf.getvalue(), "", "a refusal must come before any score is printed")
        msg = str(cm.exception.code)
        self.assertTrue(msg and msg != "None", "a refusal must say why")
        return msg

    def assertGold(self, res):
        for k, v in GOLD.items():
            self.assertAlmostEqual(res[k], v, places=12, msg=k)
        for k, (lo, hi, share) in GOLD_BOOT.items():
            self.assertAlmostEqual(res[k]["p05"], lo, places=12, msg=k)
            self.assertAlmostEqual(res[k]["p95"], hi, places=12, msg=k)
            self.assertAlmostEqual(res[k]["share_positive"], share, places=12, msg=k)
        self.assertEqual([round(m["p"], 15) for m in res["games_scored"]], GOLD_P)

class Scoring(ScoringBase):
    # -- valid records keep their scores
    def test_verified_records_score_exactly_as_the_original_scorer_did(self):
        self.write(self.full_fixture())
        res, out = self.score()
        self.assertGold(res)
        self.assertEqual(res["provenance"]["level"], "verified")
        self.assertEqual(res["provenance"]["content_files_rechecked"], 6)
        self.assertIn("PROVENANCE: verified", out)

    def test_hand_made_file_scores_the_same_only_when_accepted_and_is_labelled(self):
        self.write_minimal()
        msg = self.refused()
        self.assertIn("no verifiable provenance", msg)
        self.assertIn("--accept-unverified", msg)
        res, out = self.score("--accept-unverified")
        self.assertGold(res)
        self.assertEqual(res["provenance"]["level"], "unverified")
        self.assertTrue(res["provenance"]["accepted_unverified"])
        self.assertIn("PROVENANCE: NOT VERIFIED", out)
        self.assertIn("Treat these scores as unverified", out)
        self.assertTrue(all(m["sim_verified"] is False for m in res["games_scored"]))

    def test_quiet_line_and_json_carry_the_provenance_label(self):
        self.write_minimal()
        res, out = self.score("--accept-unverified", "--quiet")
        line = json.loads(out.strip().splitlines()[-1])
        self.assertEqual(line["provenance"], "unverified")
        self.write(self.full_fixture())
        res, out = self.score("--quiet")
        self.assertEqual(json.loads(out.strip().splitlines()[-1])["provenance"], "verified")

    def test_disjoint_chunks_add_up_to_the_same_score_as_one_row(self):
        rows = self.full_fixture()
        a, b = self.row("d0", "o0", 100, 55, 2, seed=21_108_000_000), self.row("d0", "o0", 100, 55, 2, seed=21_108_010_000)
        self.write([a, b] + rows[1:3] + rows[3:])
        res, _ = self.score()
        one = self.row("d0", "o0", 200, 110, 4)
        self.write([one] + rows[1:3] + rows[3:])
        res1, _ = self.score()
        for k in ("brier_sim", "llr_bits", "mean_sim_chance"):
            self.assertEqual(res[k], res1[k])
        # game 0 has went_first known, so it reads the "first" seat row (100 games); games 1 and 2 read the pooled row (200)
        self.assertEqual([m["sim_games"] for m in res["games_scored"]][:3], [100, 200, 200])

    # -- duplicates, overlaps, incompatible runs
    def test_the_same_games_twice_are_refused(self):
        rows = self.full_fixture()
        self.write(rows + [dict(rows[1])])
        msg = self.refused()
        self.assertIn("share simulated seeds", msg)
        self.assertIn("counted twice", msg)

    def test_partly_overlapping_chunks_are_refused(self):
        rows = self.full_fixture()
        self.write(rows + [self.row("d1", "o1", 200, 60, 0, seed=21_107_010_000 + 50)])   # 50 seeds into the first row's slot
        self.assertIn("share simulated seeds 21,107,010,050 to 21,107,010,099", self.refused())

    def test_several_rows_without_seeds_cannot_be_told_from_repeats(self):
        self.write_minimal()
        rows = read_rows(self.sim)
        fields = list(rows[0].keys())
        chunk = dict(rows[1], games="100", wins="30", draws="0")      # a second, different-looking chunk of d1/o1, no seeds
        write_rows(self.sim, rows + [chunk], fields)
        msg = self.refused()
        self.assertIn("carry no seeds", msg)
        self.assertIn("double counting", msg)
        res, out = self.score("--accept-unverified")                  # accepted knowingly: summed as before, and said so
        self.assertEqual(len(res["provenance"]["unseeded_repeats"]), 1)
        self.assertIn("several rows without seeds", out)

    def test_an_exact_repeat_of_a_row_without_seeds_is_refused_even_when_unverified_rows_are_accepted(self):
        self.write_minimal()
        rows = read_rows(self.sim)
        write_rows(self.sim, rows + [dict(rows[1])], list(rows[0].keys()))
        msg = self.refused("--accept-unverified")
        self.assertIn("are identical and carry no seeds", msg)
        self.assertIn("counted twice", msg)

    def test_two_engines_in_one_file_are_refused(self):
        rows = self.full_fixture()
        rows[1]["engine_sha256"] = ENGINE_B
        self.write(rows)
        msg = self.refused()
        self.assertIn("2 different engine builds", msg)

    def test_rows_of_one_pair_that_disagree_are_refused(self):
        rows = self.full_fixture()
        other = self.row("d0", "o0", 100, 50, 0, seed=21_109_000_000, engine=ENGINE_B, deck_sha256="9" * 64)
        self.write(rows + [other])
        msg = self.refused()
        self.assertIn("disagree on engine_sha256", msg)
        self.assertIn("disagree on deck_sha256", msg)

    def test_a_field_recorded_in_some_rows_and_blank_in_others_is_refused(self):
        rows = self.full_fixture()
        other = self.row("d0", "o0", 100, 50, 0, seed=21_109_000_000, deck_sha256="")
        self.write(rows + [other])
        self.assertIn("recorded in some rows and blank in others", self.refused("--accept-unverified"))

    def test_pilot_column_against_recorded_pilots_is_refused(self):
        rows = self.full_fixture()
        rows[0]["meta_pilot"] = "kp3"
        self.write(rows)
        self.assertIn("the pilot column says 'kog3' but deck_pilot is 'kog3' and meta_pilot 'kp3'", self.refused())

    def test_slot_counts_that_do_not_add_up_are_refused(self):
        rows = self.full_fixture()
        rows[0]["slot1_games"] = int(rows[0]["slot1_games"]) + 1
        self.write(rows)
        self.assertIn("do not add up to games", self.refused())

    def test_a_slot_that_ran_into_the_next_slots_seeds_is_refused(self):
        rows = self.full_fixture()
        rows[0].update(games=12000, slot0_games=6000, slot1_games=6000, slot0_wins=0, slot1_wins=0, wins=0, draws=0,
                       slot0_draws=0, slot1_draws=0)
        self.write(rows)
        self.assertIn("run into slot 1 seeds", self.refused())

    # -- provenance against the files
    def test_a_deck_changed_since_the_row_was_written_is_refused(self):
        self.write(self.full_fixture())
        (self.root / "decks/d1.txt").write_text("20-card list d1, edited\n")
        msg = self.refused()
        self.assertIn("the deck file decks/d1.txt has changed since this row was written", msg)

    def test_a_changed_opponent_is_refused_and_missing_files_are_only_reported(self):
        self.write(self.full_fixture())
        (self.root / "decks/o2.txt").write_text("edited\n")
        self.assertIn("the opponent file decks/o2.txt has changed", self.refused())
        (self.root / "decks/o2.txt").unlink()
        res, out = self.score()
        self.assertEqual(res["provenance"]["content_not_rechecked"], ["decks/o2.txt"])
        self.assertIn("not present here to re-check", out)
        res, out = self.score("--repo-root", str(self.tmp / "nowhere"), repo_root=False)    # a checkout that holds none of them
        self.assertEqual(res["provenance"]["content_files_rechecked"], 0)

    def test_older_runner_rows_have_engine_and_seeds_but_are_still_unverified(self):
        rows = [{k: v for k, v in r.items() if k not in ("schema", "deck_sha256", "opponent_sha256")} for r in self.full_fixture()]
        self.write(rows, FIELDS[:20])
        msg = self.refused()
        self.assertIn("no provenance schema", msg)
        self.assertIn("missing deck_sha256, opponent_sha256", msg)
        res, out = self.score("--accept-unverified")
        self.assertGold(res)
        self.assertEqual(res["provenance"]["unverified_rows"], 5)

    # -- input handling
    def test_numbers_that_are_not_whole_are_refused_cleanly(self):
        for bad in ("12.7", "inf", "nan", "1e400x", ""):
            rows = self.full_fixture()
            rows[0]["games"] = bad
            self.write(rows)
            msg = self.refused()
            self.assertIn("column games", msg, bad)
            self.assertNotIn("Traceback", msg)
        rows = self.full_fixture()
        rows[0]["seed_slot0"] = "21107000000.5"
        self.write(rows)
        self.assertIn("column seed_slot0 is not a whole number", self.refused())

    def test_a_whole_number_written_as_a_float_is_accepted(self):
        rows = self.full_fixture()
        for r in rows:
            r["games"], r["wins"] = f"{r['games']}.0", f"{r['wins']}.0"
        self.write(rows)
        res, _ = self.score()
        self.assertGold(res)

    def test_ragged_rows_are_refused(self):
        self.write(self.full_fixture())
        text = self.sim.read_text().splitlines()
        self.sim.write_text("\n".join(text[:2] + [text[2] + ",extra"] + text[3:]) + "\n")
        self.assertIn("fields under a header of", self.refused())
        self.sim.write_text("\n".join(text[:2] + [",".join(text[2].split(",")[:9])] + text[3:]) + "\n")
        self.assertIn("fewer fields", self.refused())

    def test_an_empty_sim_file_is_refused(self):
        write_rows(self.sim, [], FIELDS)
        self.assertIn("no rows", self.refused())

    # -- the pilot report
    def test_the_report_says_when_the_rows_are_not_the_working_pilot(self):
        rows = [dict(r, pilot="kp3", deck_pilot="kp3", meta_pilot="kp3") for r in self.full_fixture()]
        self.write(rows)
        res, out = self.score()
        self.assertIs(res["pilot_is_working_pilot"], False)
        self.assertEqual(res["working_pilot"], "kog3")
        self.assertIn("PILOT MISMATCH: these sim rows were played with kp3, but the project's working pilot is kog3", out)
        self.assertGold(res)                                        # a mismatch is reported, not a reason to change the score

    def test_the_report_confirms_the_working_pilot_and_tolerates_an_unreadable_one(self):
        self.write(self.full_fixture())
        res, out = self.score()
        self.assertIs(res["pilot_is_working_pilot"], True)
        self.assertIn("PILOT: kog3 on both sides", out)
        (self.screen / "floor.py").unlink()
        res, out = self.score()
        self.assertIsNone(res["pilot_is_working_pilot"])
        self.assertIn("PILOT: not checked", out)

    def test_a_refusal_prints_nothing_and_writes_no_json(self):
        rows = self.full_fixture()
        self.write(rows + [dict(rows[0])])
        js = self.tmp / "report.json"
        self.refused("--json", str(js))
        self.assertFalse(js.exists())


class ScoringHardening(ScoringBase):
    """Each of these was reproduced on the first version of the scorer by the Sept 29 adversarial review."""

    # ---- the content re-check and provenance can not be walked around
    def test_a_path_spelled_in_another_case_still_gets_the_content_recheck(self):
        rows = self.full_fixture()
        rows[0]["deck_file"] = "Decks/D0.txt"                 # the sim row spells the path in another case
        rows[1]["deck_file"] = "decks\\D1.txt"                # backslash and case
        rows[2]["opponent_file"] = "./decks//O2.txt"          # './', '//' and case
        self.write(rows)
        (self.root / "decks/d0.txt").write_text("20-card list d0, two cards swapped after the sim ran\n")
        msg = self.refused()
        self.assertIn("has changed since this row was written", msg)
        (self.root / "decks/d0.txt").write_text("20-card list d0\n")                          # restored: now it passes, and says so
        res, out = self.score()
        self.assertEqual(res["provenance"]["content_not_rechecked"], [])
        self.assertGold(res)

    def test_two_files_that_differ_only_in_case_are_not_guessed_between(self):
        (self.root / "decks/Dx.txt").write_text("one\n")
        if (self.root / "decks/dx.txt").exists():
            self.skipTest("this file system ignores case")
        (self.root / "decks/dx.txt").write_text("two\n")
        rows = self.full_fixture()
        rows[0]["deck_file"] = "DECKS/DX.TXT"
        rows[0]["deck_sha256"] = calibrate.file_sha256(self.root / "decks/dx.txt")
        self.write(rows)
        self.assertIn("matches two files that differ only in case", self.refused())

    def test_placeholder_text_in_the_provenance_columns_is_not_provenance(self):
        rows = self.full_fixture()
        for r in rows:
            r.update(engine_sha256="TBD", deck_sha256="n/a", opponent_sha256="x")
        self.write(rows)
        msg = self.refused()
        self.assertIn("is not a 64-character sha256", msg)
        res, out = self.score("--accept-unverified")
        self.assertEqual(res["provenance"]["level"], "unverified")
        self.assertIn("PROVENANCE: NOT VERIFIED", out)
        rows = [dict(r, pilot="kog 3", deck_pilot="kog 3", meta_pilot="kog 3") for r in self.full_fixture()]
        self.write(rows)
        self.assertIn("is not a pilot name", self.refused())
        rows = self.full_fixture()
        rows[0]["seed_slot0"] = str(2 ** 64)
        self.write(rows)
        self.assertIn("largest seed the engine takes", self.refused())
        rows = self.full_fixture()
        rows[0]["seed_slot0"] = "1e30"
        self.write(rows)
        self.assertIn("seed_slot0", self.refused())

    def test_upper_case_hashes_are_the_same_hashes(self):
        rows = self.full_fixture()
        rows[0]["deck_sha256"] = rows[0]["deck_sha256"].upper()                   # as PowerShell's Get-FileHash prints it
        rows[1]["engine_sha256"] = ENGINE_A.upper()
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")
        self.assertGold(res)

    def test_one_file_recorded_with_two_contents_is_refused_even_when_the_files_are_not_here(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        rows = self.full_fixture()
        other_seat = self.row("d0", "o0", 100, 70, 0, "first", seed=21_108_000_000, deck_sha256="9" * 64, opponent_sha256="8" * 64)
        self.write(rows[:3] + [other_seat])
        msg = self.refused("--repo-root", str(empty), repo_root=False)
        self.assertIn("is recorded with 2 different contents", msg)
        other_pair = self.row("d0", "o1", 100, 60, 0, seed=21_109_000_000, deck_sha256="7" * 64)     # the same deck file, another pair
        self.write(rows[:3] + [other_pair])
        msg = self.refused("--repo-root", str(empty), repo_root=False)
        self.assertIn("decks/d0.txt is recorded with 2 different contents", msg)

    def test_verified_rows_are_never_joined_to_another_folders_deck_by_file_name(self):
        for sub in ("old", "new"):
            (self.root / "decks" / sub).mkdir()
            (self.root / "decks" / sub / "d0.txt").write_text(f"20-card list d0 in {sub}\n")
            (self.root / "decks" / sub / "o0.txt").write_text(f"20-card list o0 in {sub}\n")
        with open(self.games, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["game_id", "date", "deck_file", "opponent_file", "opponent_key", "list_match", "went_first", "result", "usable"])
            for k, r in enumerate("WLW"):
                w.writerow([f"g{k}", "2026-09-27", "decks/new/d0.txt", "decks/new/o0.txt", "o0", "exact", "", r, 1])
        old = self.row("d0", "o0", 200, 110, 4, deck_file="decks/old/d0.txt", opponent_file="decks/old/o0.txt",
                       deck_sha256=calibrate.file_sha256(self.root / "decks/old/d0.txt"),
                       opponent_sha256=calibrate.file_sha256(self.root / "decks/old/o0.txt"))
        self.write([old])
        self.assertIn("no game could be joined", self.refused())
        minimal = [dict(deck_file="decks/old/d0.txt", opponent_file="decks/old/o0.txt", pilot="kog3", games=200, wins=110, draws=4, seat="any")]
        write_rows(self.sim, minimal, list(minimal[0].keys()))                     # a hand-made file may still match by file name
        res, out = self.score("--accept-unverified")
        self.assertEqual(res["n"], 3)
        self.assertIn("matched decks/new/d0.txt vs decks/new/o0.txt by file name", out)

    def test_spelling_variants_of_one_pair_are_one_pair(self):
        rows = self.full_fixture()
        dup = dict(rows[0], deck_file="decks/./d0.txt")
        self.write(rows + [dup])
        self.assertIn("share simulated seeds", self.refused())
        a, b = self.row("d0", "o0", 100, 55, 2, seed=21_108_000_000), self.row("d0", "o0", 100, 55, 2, seed=21_108_010_000, deck_file="decks//d0.txt")
        self.write([a, b] + rows[1:])
        res, _ = self.score()
        self.assertEqual([m["sim_games"] for m in res["games_scored"]][1], 200, "both spellings were summed as one pair")

    def test_a_sim_row_that_no_game_used_is_reported_not_silently_dropped(self):
        rows = self.full_fixture()
        self.write(rows + [self.row("d1", "o2", 100, 40, 0, seed=21_110_000_000)])
        res, out = self.score()
        self.assertEqual(res["unused_sim_pairs"], ["decks/d1.txt vs decks/o2.txt"])
        self.assertIn("joined to no game and did not count", out)
        self.assertGold(res)

    def test_the_banner_says_other_pilots_rows_were_not_checked(self):
        rows = self.full_fixture()
        bad = self.row("d0", "o0", 100, 50, 0, pilot="kp3", seed=21_111_000_000, engine=ENGINE_B)
        self.write(rows + [bad, dict(bad)])                                        # a duplicate hiding in the other pilot's rows
        res, out = self.score("--pilot", "kog3")
        self.assertEqual(res["provenance"]["other_pilot_rows"], 2)
        self.assertIn("(2 rows of other pilots were not checked or scored)", out)
        self.assertIn("share simulated seeds", self.refused("--pilot", "kp3"))

    def test_the_quiet_line_says_how_many_files_were_rechecked(self):
        self.write(self.full_fixture())
        res, out = self.score("--quiet")
        line = json.loads(out.strip().splitlines()[-1])
        self.assertEqual((line["content_files_rechecked"], line["content_files_not_rechecked"]), (6, 0))
        res, out = self.score("--quiet", "--repo-root", str(self.tmp / "nowhere"), repo_root=False)
        line = json.loads(out.strip().splitlines()[-1])
        self.assertEqual((line["content_files_rechecked"], line["content_files_not_rechecked"]), (0, 6))
        res, out = self.score("--repo-root", str(self.tmp / "nowhere"), repo_root=False)
        self.assertIn("NOTE: no deck or opponent file could be re-checked here", out)

    def test_the_pilot_line_for_unverified_rows_says_it_is_a_label(self):
        self.write_minimal()
        res, out = self.score("--accept-unverified")
        self.assertIn("PILOT (label only): the pilot column says kog3", out)
        self.assertIn("not verified", out)

    # ---- slot and layout checks
    def test_a_row_must_split_its_games_the_way_the_runner_does(self):
        for games, first in ((100, 1), (5000, 4999), (100, 0), (100, 100), (101, 51)):
            rows = self.full_fixture()
            wins, draws = rows[0]["wins"], rows[0]["draws"]
            rows[0].update(games=games, slot0_games=first, slot1_games=games - first, slot0_wins=0, slot0_draws=0,
                           slot1_wins=min(wins, games - first), slot1_draws=0, wins=min(wins, games - first), draws=0)
            self.write(rows)
            needle = f"the slots hold {first:,} and {games - first:,} games, but the runner splits {games:,} games as " \
                     f"{games // 2:,} and {games - games // 2:,}"
            self.assertIn(needle, self.refused(), (games, first))
        rows = self.full_fixture()                                   # what the runner writes for an odd count: 50 and 51
        rows[0].update(games=101, slot0_games=50, slot1_games=51, slot0_wins=20, slot0_draws=0, slot1_wins=21, slot1_draws=1,
                       wins=41, draws=1)
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")
        rows[0].update(slot0_games=51, slot1_games=50)               # the odd game belongs to slot 1, not slot 0
        self.write(rows)
        self.assertIn("the slots hold 51 and 50 games", self.refused())

    def test_impossible_slot_counts_are_refused(self):
        rows = self.full_fixture()
        rows[0].update(slot0_wins=105, slot1_wins=5)                               # totals still add up to 110
        self.write(rows)
        self.assertIn("slot 0 shows 105 wins and 2 draws in 100 games", self.refused())
        rows = self.full_fixture()
        for c in ("slot0_wins", "slot1_wins", "slot0_draws", "slot1_draws"):
            rows[0][c] = ""
        self.write(rows)
        self.assertIn("missing slot0_wins, slot1_wins, slot0_draws, slot1_draws", self.refused())

    def test_a_row_the_runner_wrote_keeps_to_its_seed_layout(self):
        rows = self.full_fixture()
        rows[0].update(games=10_000, slot0_games=4000, slot1_games=6000, wins=0, draws=0, slot0_wins=0, slot1_wins=0,
                       slot0_draws=0, slot1_draws=0)                              # slot 1 runs 6,000 seeds from +5,000: into the next pair
        self.write(rows)
        msg = self.refused()
        self.assertIn("slot 1 played 6,000 games, more than the 5,000 seeds reserved per slot", msg)
        self.assertIn("slot 1 seeds run past the pair's 10,000-seed block", msg)

    # ---- malformed input is refused cleanly, quickly, and before anything is printed
    def test_hostile_numbers_and_bytes_are_refused_not_crashed_on(self):
        import time as _t
        for bad, needle in (("1e10000000", "too large"), ("9" * 5000, "too long"), ("1e400", "too large")):
            rows = self.full_fixture()
            rows[0]["games"] = bad
            self.write(rows)
            t0 = _t.time()
            self.assertIn(needle, self.refused(), bad[:12])
            self.assertLess(_t.time() - t0, 2.0, "refused at once, not after computing a huge integer")
        self.sim.write_bytes(b"deck_file,opponent_file,pilot,games,wins\n\xff\xfe\x00bad,x,y,1,1\n")
        self.assertIn("could not read or write a file", self.refused())
        self.sim.write_text("deck_file,opponent_file,pilot,games,wins\n" + "x" * 200_000 + ",b,c,1,1\n")
        self.assertIn("could not read or write a file", self.refused())
        self.assertIn("--boot must be at least 1", self._boot_refusal())
        self.sim.unlink()
        self.assertIn("could not read or write a file", self.refused())

    def _boot_refusal(self):
        self.write(self.full_fixture())
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            calibrate.main(["--sim", str(self.sim), "--games", str(self.games), "--boot", "0"])
        return str(cm.exception.code)

    def test_json_never_overwrites_the_inputs_and_is_valid_when_a_score_is_undefined(self):
        self.write(self.full_fixture())
        before = self.sim.read_bytes()
        self.assertIn("would overwrite the evidence", self.refused("--json", str(self.sim)))
        self.assertIn("would overwrite the evidence", self.refused("--json", str(self.games)))
        self.assertEqual(self.sim.read_bytes(), before)
        self.assertIn("folder for --json", self.refused("--json", str(self.tmp / "no" / "such" / "dir" / "r.json")))
        with open(self.games, "w", newline="") as f:                             # every game a win: skill against the base rate is undefined
            w = csv.writer(f)
            w.writerow(["game_id", "date", "deck_file", "opponent_file", "opponent_key", "list_match", "went_first", "result", "usable"])
            for k in range(3):
                w.writerow([f"g{k}", "2026-09-27", "decks/d0.txt", "decks/o0.txt", "o0", "exact", "", "W", 1])
        js = self.tmp / "r.json"
        res, out = self.score("--json", str(js))
        text = js.read_text()
        self.assertNotIn("NaN", text)
        json.loads(text, parse_constant=lambda c: self.fail(f"invalid JSON constant {c}"))

    def test_a_result_other_than_w_or_l_is_refused_not_scored_as_a_loss(self):
        self.write(self.full_fixture())
        for bad in ("", "Win", "won", "D"):
            with open(self.games, newline="") as gf:
                rows = list(csv.reader(gf))
            rows[1][7] = bad
            with open(self.games, "w", newline="") as f:
                csv.writer(f).writerows(rows)
            self.assertIn("not W or L", self.refused(), repr(bad))
            rows[1][7] = "W"
            with open(self.games, "w", newline="") as f:
                csv.writer(f).writerows(rows)

    def test_byte_order_marks_and_short_games_rows_are_handled(self):
        self.write(self.full_fixture())
        self.sim.write_bytes(b"\xef\xbb\xbf" + self.sim.read_bytes())
        self.games.write_bytes(b"\xef\xbb\xbf" + self.games.read_bytes())
        res, _ = self.score()
        self.assertGold(res)
        lines = self.games.read_text(encoding="utf-8-sig").splitlines()
        self.games.write_text("\n".join(lines[:3] + [",".join(lines[3].split(",")[:4])] + lines[4:]) + "\n")
        self.assertIn("different number of fields", self.refused())

    def test_a_blank_pilot_column_is_refused_even_with_accept_unverified(self):
        rows = [dict(deck_file=f"decks/{d}.txt", opponent_file=f"decks/{o}.txt", pilot="", games=g, wins=w, draws=dr, seat=s)
                for d, o, g, w, dr, s in SIM]
        write_rows(self.sim, rows, list(rows[0].keys()))
        self.assertIn("the pilot column is empty", self.refused("--accept-unverified"))

    def test_line_numbers_are_the_real_lines_when_the_file_has_blank_lines(self):
        self.write(self.full_fixture())
        text = self.sim.read_text().splitlines()
        dup = text[2]                                                              # the second data row, repeated further down
        self.sim.write_text("\n".join([text[0], "", text[1], "", text[2], dup] + text[3:]) + "\n")
        self.assertIn("lines 5 and 6 share simulated seeds", self.refused())

    # ---- round two of the review
    def test_json_does_not_overwrite_a_hard_link_of_an_input_or_a_file_that_is_not_a_report(self):
        self.write(self.full_fixture())
        hard = self.tmp / "hard.json"
        os.link(self.sim, hard)
        before = self.sim.read_bytes()
        self.assertIn("would overwrite the evidence", self.refused("--json", str(hard)))
        self.assertEqual(self.sim.read_bytes(), before)
        self.assertIn("is not a JSON report", self.refused("--json", str(self.root / "decks/d0.txt")))
        self.assertEqual((self.root / "decks/d0.txt").read_text(), "20-card list d0\n")
        report = self.tmp / "report.json"
        self.score("--json", str(report))
        self.score("--json", str(report))                                               # an earlier report may be replaced
        self.assertEqual(json.loads(report.read_text())["n"], 9)
        folder = self.tmp / "afolder"
        folder.mkdir()
        self.assertIn("is a folder", self.refused("--json", str(folder)))

    def test_a_row_the_runner_wrote_starts_slot_1_five_thousand_after_slot_0_and_inside_the_engines_range(self):
        for over, needle in ((dict(seed_slot1=21_107_000_100), "slot 1 seeds start at 21,107,000,100, not 5,000 after slot 0's"),
                             (dict(seed_slot1=0), "slot 1 seeds start at 0"),
                             (dict(seed_slot0=2 ** 64 - 1, seed_slot1=2 ** 64 - 1 + 5000), "largest seed the engine takes")):
            rows = self.full_fixture()
            rows[0].update(over)
            self.write(rows)
            self.assertIn(needle, self.refused(), over)
        rows = self.full_fixture()
        rows[0].update(seed_slot0=2 ** 64 - 10_000, seed_slot1=2 ** 64 - 5_000)          # the very last block: 100 games fit
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")

    def test_the_quiet_line_counts_games_that_found_no_sim_row(self):
        self.write([r for r in self.full_fixture() if "d2" not in r["deck_file"]])
        res, out = self.score("--quiet")
        line = json.loads(out.strip().splitlines()[-1])
        self.assertEqual((line["missing_games"], line["missing_pairs"], line["n"]), (4, 1, 5))

    def test_a_games_file_with_only_a_header_is_no_usable_games_not_missing_columns(self):
        self.write(self.full_fixture())
        self.games.write_text("game_id,date,deck_file,opponent_file,opponent_key,list_match,went_first,result,usable\n")
        self.assertIn("no usable games", self.refused())

    def test_a_repeated_header_line_in_the_sim_file_is_named(self):
        self.write(self.full_fixture())
        text = self.sim.read_text().splitlines()
        self.sim.write_text("\n".join(text + [text[0]]) + "\n")
        self.assertIn("this line repeats the header", self.refused())

    def test_a_closed_stdout_ends_quietly_not_as_a_false_refusal(self):
        class Gone(io.StringIO):
            def write(self, s):
                raise BrokenPipeError(32, "Broken pipe")
        self.write(self.full_fixture())
        with contextlib.redirect_stdout(Gone()), self.assertRaises(SystemExit) as cm:
            calibrate.main(self.argv())
        self.assertEqual(cm.exception.code, 1)                                           # no 'REFUSED ... nothing was scored' text


class ScoringGuards(ScoringBase):
    """Guards the mutation review showed nothing was pinning: each test here fails if its check is removed."""

    def nowhere(self):
        return ("--repo-root", str(self.tmp / "nowhere"))

    def test_a_maximal_valid_record_is_accepted_and_a_one_seed_overlap_is_not(self):
        rows = self.full_fixture()
        rows[0] = self.row("d0", "o0", 10_000, 5500, 40)          # slot 0: 5,000 games, slot 1: 5,000, touching but disjoint
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")
        rows[0] = self.row("d0", "o0", 10_001, 5500, 40, slot0_games=5001, slot1_games=5000, slot0_wins=2750, slot1_wins=2750,
                           slot0_draws=20, slot1_draws=20)
        self.write(rows)
        self.assertIn("run into slot 1 seeds", self.refused())

    def test_chunks_that_touch_are_fine_and_one_shared_seed_in_either_slot_is_not(self):
        rows = self.full_fixture()
        base = 21_108_000_000
        a = self.row("d0", "o0", 100, 55, 2, seed=base)                              # slot 0 [B, B+50), slot 1 [B+5000, B+5050)
        for name, over, needle in (("touching, both slots", dict(seed=base + 50), None),
                                   ("one seed shared in slot 0", dict(seed=base + 49), f"{base + 49:,} to {base + 49:,}"),
                                   ("one seed shared in slot 1 only", dict(seed=base + 50, seed_slot1=base + 5049),
                                    f"{base + 5049:,} to {base + 5049:,}")):
            b = self.row("d0", "o0", 100, 55, 2, **over)
            self.write([a, b] + rows[1:])
            if needle is None:
                res, _ = self.score()
                self.assertEqual([m["sim_games"] for m in res["games_scored"]][1], 200, name)
            else:
                self.assertIn(needle, self.refused(), name)

    def test_the_first_and_third_of_three_chunks_overlapping_is_found(self):
        rows = self.full_fixture()
        b = self.row("d1", "o1", 200, 60, 0, seed=21_108_000_000)
        c = self.row("d1", "o1", 200, 60, 0, seed=21_107_010_050)    # overlaps the first d1 row, with a clean chunk between them
        self.write(rows + [b, c])
        self.assertIn("share simulated seeds", self.refused())

    def test_chunks_of_one_pair_that_disagree_on_any_recorded_field_are_refused(self):
        rows = self.full_fixture()
        for field, value in (("opponent_sha256", "9" * 64), ("deck_sha256", "8" * 64), ("engine_sha256", ENGINE_B),
                             ("deck_pilot", "kp3"), ("meta_pilot", "kp3")):
            other = self.row("d0", "o0", 100, 50, 0, seed=21_109_000_000, **{field: value})
            self.write(rows[:3] + [other])
            self.assertIn(f"disagree on {field}", self.refused(*self.nowhere(), repo_root=False), field)

    def test_every_required_field_left_blank_makes_a_row_unverified(self):
        self.assertEqual(sorted(calibrate.REQUIRED_PROVENANCE), sorted(REQUIRED), "the list of fields that make a row verified changed")
        self.assertEqual(len(REQUIRED), 13)
        for field in REQUIRED:
            rows = self.full_fixture()
            rows[0][field] = ""
            self.write(rows)
            self.assertIn(f"missing {field}", self.refused(), field)
            res, out = self.score("--accept-unverified")
            self.assertEqual(res["provenance"]["level"], "unverified", field)
        rows = self.full_fixture()
        rows[0]["schema"] = "2"
        self.write(rows)
        self.assertIn("unknown provenance schema '2'", self.refused())

    def test_slot_wins_and_draws_must_add_up_to_the_row(self):
        for col, word in (("slot0_wins", "wins"), ("slot0_draws", "draws"), ("slot1_games", "games")):
            rows = self.full_fixture()
            rows[0][col] = int(rows[0][col]) + 1
            self.write(rows)
            self.assertIn(f"do not add up to {word}", self.refused(), col)

    def test_a_mixed_pilot_label_must_match_its_two_pilots(self):
        rows = [dict(r, pilot="kog3|kp3", deck_pilot="kog3", meta_pilot="kp3") for r in self.full_fixture()]
        self.write(rows)
        res, out = self.score()
        self.assertEqual((res["pilot"], res["pilot_is_working_pilot"]), ("kog3|kp3", False))
        self.assertIn("PILOT MISMATCH", out)
        self.write([dict(r, pilot="kp3|kog3") for r in rows])                           # the label reversed against the recorded pilots
        self.assertIn("the pilot column says 'kp3|kog3'", self.refused())

    def test_the_three_draw_modes_give_the_original_scorers_values_and_drop_refuses_all_draws(self):
        self.write(self.full_fixture())
        for mode, expected in (("loss", 110 / 200), ("half", 112 / 200), ("drop", 110 / 196)):
            res, _ = self.score("--draws", mode)
            self.assertAlmostEqual(res["games_scored"][1]["p"], expected, places=12, msg=mode)   # game 1 reads the pooled d0/o0 row
        rows = self.full_fixture()
        rows[1] = self.row("d1", "o1", 200, 0, 200)
        self.write(rows)
        with self.assertRaises(SystemExit) as cm:
            self.score("--draws", "drop")
        self.assertIn("every game was a draw", str(cm.exception.code))

    def test_several_pilots_in_one_file_need_a_choice_and_only_the_chosen_ones_rows_count(self):
        a = self.full_fixture()
        b = [dict(r, pilot="kp3", deck_pilot="kp3", meta_pilot="kp3", engine_sha256=ENGINE_B, wins=r["games"], slot0_wins=r["slot0_games"],
                  slot1_wins=r["slot1_games"], slot0_draws=0, slot1_draws=0, draws=0) for r in a]      # kp3 wins everything, from another engine
        self.write(a + b)
        self.assertIn("several pilots", self.refused())
        self.assertIn("'zzz' is not in the sim file", self.refused("--pilot", "zzz"))
        res, _ = self.score("--pilot", "kog3")
        self.assertGold(res)                                                           # the kp3 rows changed nothing
        self.assertEqual((res["pilot"], res["provenance"]["level"]), ("kog3", "verified"))
        res, _ = self.score("--pilot", "kp3")
        self.assertEqual(res["provenance"]["engine_sha256"], [ENGINE_B])

    def test_the_json_report_is_written_and_carries_the_provenance(self):
        self.write(self.full_fixture())
        js = self.tmp / "report.json"
        self.score("--json", str(js))
        got = json.loads(js.read_text())
        self.assertEqual((got["n"], got["provenance"]["level"], got["provenance"]["accepted_unverified"]), (9, "verified", False))
        self.assertEqual(got["pilot"], "kog3")
        self.write_minimal()
        self.score("--accept-unverified", "--json", str(js))
        got = json.loads(js.read_text())
        self.assertEqual((got["provenance"]["level"], got["provenance"]["accepted_unverified"]), ("unverified", True))
        self.assertEqual(len(got["provenance"]["unverified_lines"]), 5)

    def test_impossible_rows_are_refused_with_their_line(self):
        cases = [("games", "0", "do not make sense"), ("games", "-4", "do not make sense"), ("wins", "-1", "do not make sense"),
                 ("draws", "-1", "do not make sense"), ("wins", "199", "do not make sense"), ("seat", "sideways", "seat must be"),
                 ("slot0_games", "-5", "is negative")]
        for col, bad, needle in cases:
            rows = self.full_fixture()
            rows[0][col] = bad
            self.write(rows)
            self.assertIn(needle, self.refused(), (col, bad))
            self.assertIn("line 2", self.refused(), (col, bad))

    def test_the_pooled_seat_is_another_name_for_any_and_missing_columns_are_named(self):
        rows = [dict(r, seat="pooled") if r["seat"] == "any" else r for r in self.full_fixture()]
        self.write(rows)
        res, _ = self.score()
        self.assertGold(res)
        self.write([{k: v for k, v in r.items() if k != "wins"} for r in self.full_fixture()], [f for f in FIELDS if f != "wins"])
        self.assertIn("missing columns ['wins']", self.refused())
        self.write(self.full_fixture())
        with open(self.games, "w", newline="") as f:
            f.write("game_id,deck_file,opponent_file,usable\ng0,decks/d0.txt,decks/o0.txt,1\n")
        self.assertIn("missing columns ['result']", self.refused())

    def test_the_scorers_own_guards(self):
        self.write(self.full_fixture())
        self.assertIn("--clip must be between 0 and 0.5", self.refused("--clip", "0.5"))
        self.assertIn("missing sim rows for: decks/d2.txt vs decks/o2.txt", self._strict_refusal())
        self.write([r for r in self.full_fixture() if "d1" in r["deck_file"]])          # no sim row for any pair the games use except d1
        res, _ = self.score()
        self.assertEqual(res["n"], 2)
        self.write([self.row("d2", "o0", 100, 50, 0)])
        self.assertIn("no game could be joined", self.refused())
        with open(self.games, "w", newline="") as f:
            f.write("game_id,deck_file,opponent_file,result,usable\ng0,decks/d0.txt,decks/o0.txt,W,0\ng1,,decks/o0.txt,W,1\n")
        self.write(self.full_fixture())
        self.assertIn("no usable games", self.refused())

    def _strict_refusal(self):
        self.write([r for r in self.full_fixture() if "d2" not in r["deck_file"]])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
            calibrate.main(self.argv("--strict"))
        return str(cm.exception.code)

    def test_two_hand_made_rows_that_share_a_file_name_are_not_guessed_between(self):
        rows = [dict(deck_file=f"{sub}/d0.txt", opponent_file="x/o0.txt", pilot="kog3", games=200, wins=w, draws=0, seat="any")
                for sub, w in (("a", 100), ("b", 120))]
        write_rows(self.sim, rows, list(rows[0].keys()))
        msg = self.refused("--accept-unverified")
        self.assertIn("ambiguous sim rows", msg)
        self.assertIn("several rows share this file name", msg)


class ScoringBoundaries(ScoringBase):
    """Scorer checks that the round-3 mutation review found nothing pinning: every hash column, the seed ceiling, spellings of
    the opponent path, files with only the old basic columns."""

    def quiet_line(self, *args):
        res, out = self.score("--quiet", *args)
        return json.loads(out.strip().splitlines()[-1])

    def test_a_bad_hash_in_any_of_the_three_hash_columns_is_not_provenance(self):
        for field in ("engine_sha256", "deck_sha256", "opponent_sha256"):
            for bad in ("a" * 63, "a" * 65, "g" * 64, "TBD"):
                rows = [dict(r, **{field: bad}) for r in self.full_fixture()]
                self.write(rows)
                self.assertIn(f"{field} {bad.lower()[:16]!r} is not a 64-character sha256", self.refused(), (field, bad))
                res, _ = self.score("--accept-unverified")
                self.assertEqual(res["provenance"]["level"], "unverified", (field, bad))
        rows = self.full_fixture()
        rows[0]["opponent_sha256"] = rows[0]["opponent_sha256"].upper()         # as PowerShell's Get-FileHash prints it
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")
        self.assertGold(res)

    def test_one_opponent_or_one_differently_spelled_deck_recorded_with_two_contents_is_refused(self):
        empty = self.tmp / "empty"
        empty.mkdir()
        rows = self.full_fixture()
        other_opp = self.row("d1", "o0", 100, 60, 0, seed=21_109_000_000, opponent_sha256="7" * 64)          # the same opponent file, another deck
        self.write(rows[:3] + [other_opp])
        self.assertIn("decks/o0.txt is recorded with 2 different contents", self.refused("--repo-root", str(empty), repo_root=False))
        other_spelling = self.row("d0", "o1", 100, 60, 0, seed=21_109_000_000, deck_file="Decks/D0.txt", deck_sha256="7" * 64)
        self.write(rows[:3] + [other_spelling])                                                          # the same deck file, spelled another way
        self.assertIn("decks/d0.txt is recorded with 2 different contents", self.refused("--repo-root", str(empty), repo_root=False))

    def test_one_pair_with_its_opponent_spelled_two_ways_is_one_pair(self):
        rows = self.full_fixture()
        for spelling in ("decks/./o0.txt", "decks\\o0.txt", "DECKS/O0.TXT", "decks//o0.txt"):
            self.write(rows + [dict(rows[0], opponent_file=spelling)])
            self.assertIn("share simulated seeds", self.refused(), spelling)
        a = self.row("d0", "o0", 100, 55, 2, seed=21_108_000_000)
        b = self.row("d0", "o0", 100, 55, 2, seed=21_108_010_000, opponent_file="DECKS//O0.txt")
        self.write([a, b] + rows[1:])
        res, _ = self.score()
        self.assertEqual([m["sim_games"] for m in res["games_scored"]][1], 200, "both spellings were summed as one pair")

    def test_seeds_up_to_the_largest_the_engine_takes_are_accepted_and_one_more_is_not(self):
        top = 2 ** 64 - 1
        rows = self.full_fixture()
        rows[0] = self.row("d0", "o0", 100, 55, 2, seed=top - 5049)            # slot 1 is [top-49, top]: its last seed is the largest one
        self.write(rows)
        res, _ = self.score()
        self.assertEqual(res["provenance"]["level"], "verified")
        rows[0] = self.row("d0", "o0", 100, 55, 2, seed=top - 5048)            # one seed higher runs past it
        self.write(rows)
        self.assertIn(f"slot 1 seeds run past {top:,}", self.refused())
        rows[0] = self.row("d0", "o0", 2, 1, 0, seed=top, schema="", seed_slot1="", slot1_games="", slot1_wins="", slot1_draws="")
        self.write(rows)                                                       # a hand-made row whose only seed is the largest one
        res, _ = self.score("--accept-unverified")
        self.assertEqual(res["provenance"]["unverified_rows"], 1)
        rows[0]["seed_slot0"] = top + 1
        self.write(rows)
        self.assertIn("largest seed the engine takes", self.refused("--accept-unverified"))

    def test_the_quiet_line_says_whether_the_rows_are_the_working_pilots(self):
        self.write(self.full_fixture())
        self.assertIs(self.quiet_line()["pilot_is_working_pilot"], True)
        self.write([dict(r, pilot="kog3|kp3", deck_pilot="kog3", meta_pilot="kp3") for r in self.full_fixture()])
        self.assertIs(self.quiet_line()["pilot_is_working_pilot"], False)
        (self.screen / "run_screen.py").unlink()                               # the working pilot cannot be read: neither yes nor no
        self.assertIsNone(self.quiet_line()["pilot_is_working_pilot"])

    def test_an_older_file_with_only_the_basic_columns_scores_when_accepted_and_a_missing_pilot_column_is_named(self):
        rows = [dict(deck_file=f"decks/{d}.txt", opponent_file=f"decks/{o}.txt", pilot="kog3", games=200, wins=w)
                for d, o, w in (("d0", "o0", 110), ("d1", "o1", 100), ("d2", "o2", 90))]
        write_rows(self.sim, rows, ["deck_file", "opponent_file", "pilot", "games", "wins"])              # no seat, no draws, nothing else
        self.assertIn("no verifiable provenance", self.refused())
        res, out = self.score("--accept-unverified")
        self.assertEqual((res["n"], res["provenance"]["level"]), (9, "unverified"))
        self.assertAlmostEqual(res["games_scored"][0]["p"], 110 / 200, places=12)
        write_rows(self.sim, [{k: v for k, v in r.items() if k != "pilot"} for r in rows], ["deck_file", "opponent_file", "games", "wins"])
        self.assertIn("missing columns ['pilot']", self.refused("--accept-unverified"))

    def test_touching_chunks_are_fine_in_either_line_order(self):
        rows = self.full_fixture()
        a = self.row("d0", "o0", 100, 55, 2, seed=21_108_000_000)
        b = self.row("d0", "o0", 100, 55, 2, seed=21_108_000_050)
        for order in ([a, b], [b, a]):
            self.write(order + rows[1:])
            res, _ = self.score()
            self.assertEqual([m["sim_games"] for m in res["games_scored"]][1], 200)

    def test_a_row_of_zero_games_or_with_more_wins_and_draws_than_games_is_refused(self):
        rows = self.full_fixture()
        rows[0].update(games=0, wins=0, draws=0, slot0_games=0, slot1_games=0, slot0_wins=0, slot1_wins=0, slot0_draws=0, slot1_draws=0)
        self.write(rows)
        self.assertIn("games=0 wins=0 draws=0 do not make sense", self.refused())
        rows = self.full_fixture()
        rows[0].update(wins=200, draws=1)
        self.write(rows)
        self.assertIn("games=200 wins=200 draws=1 do not make sense", self.refused())


@linux_only
class RunnerBoundaries(unittest.TestCase):
    """Runner behaviour the round-3 mutation review found nothing pinning: the edges of the reserved block, plan-only runs,
    an edited opponent, rows without seeds, pilot defaults, and the shape of the games file."""

    def test_the_columns_the_runner_writes_are_exactly_these_and_a_first_run_says_it_wrote(self):
        self.assertEqual(rc.FIELDS, FIELDS)
        w = Repo(self, npairs=1)
        out, msg, calls = w.call()
        self.assertIsNone(msg, out)
        self.assertEqual(w.out.read_text().splitlines()[0], ",".join(FIELDS))
        self.assertIn("wrote ", out)
        self.assertNotIn("nothing written", out)

    def test_the_reserved_block_edges_to_the_seed(self):
        lo = 21_107_000_000
        hi = lo + 199_999
        for seed, refused in ((lo - 10_000, False), (lo - 9_999, True), (lo, False), (hi, True), (hi + 1, False)):
            errs = rc.layout_errors(1, 100, seed)
            self.assertEqual([("overlaps part of the reserved block" in e) for e in errs], [True] if refused else [], seed)
        w = Repo(self, npairs=1)
        for seed, refused in ((hi, True), (hi + 1, False)):
            out, msg, calls = w.call("--seed", str(seed))
            self.assertEqual("overlaps part of the reserved block" in (msg or ""), refused, (seed, msg))
            self.assertEqual(calls == 0, refused, seed)
            if w.out.exists():
                w.out.unlink()

    def test_pairs_only_prints_every_pair_and_seed_and_touches_no_engine_and_no_file(self):
        w = Repo(self)
        out, msg, calls = w.call("--pairs-only")
        self.assertIsNone(msg, out)
        self.assertEqual(calls, 0)
        self.assertFalse(w.out.exists())
        self.assertIn("pair  0: decks/d0.txt vs decks/o0.txt  (1 ladder game)  seeds 21,107,000,000+g and 21,107,005,000+g", out)
        self.assertIn("pair  1: decks/d1.txt vs decks/o1.txt  (1 ladder game)  seeds 21,107,010,000+g and 21,107,015,000+g", out)
        w.out.write_text("not a results file\n")                   # an existing file is neither read nor locked nor changed
        out, msg, calls = w.call("--pairs-only", "--resume")
        self.assertEqual((msg, calls, w.out.read_text()), (None, 0, "not a results file\n"))

    def test_an_opponent_edited_while_a_pair_plays_is_not_recorded_and_one_edited_before_a_pair_stops_it_starting(self):
        w = Repo(self)
        w.hook = lambda n: (w.root / "decks/o0.txt").write_text("edited mid-run\n") if n == 1 else None
        out, msg, calls = w.call()
        self.assertIn("decks/o0.txt changed", msg)
        self.assertIn("while pair 0 was played", msg)
        self.assertEqual(w.out.read_text().splitlines(), [",".join(FIELDS)], "no row for the pair whose opponent moved")
        w2 = Repo(self)
        w2.hook = lambda n: (w2.root / "decks/o1.txt").write_text("edited while pair 0 played\n") if n == 2 else None
        out, msg, calls = w2.call()
        self.assertIn("decks/o1.txt changed", msg)
        self.assertIn("before pair 1 was played", msg)
        self.assertEqual((calls, len(w2.rows())), (2, 1), "pair 0 is kept; the engine was never started for pair 1")

    def test_rows_without_seeds_or_counts_resume_only_with_the_flag_and_stay_as_they_are(self):
        w = Repo(self)
        out, msg, calls = w.call()
        self.assertIsNone(msg, out)
        rows = w.rows()
        for c in ("schema", "engine_sha256", "deck_sha256", "opponent_sha256", "deck_pilot", "meta_pilot", "seed_slot0", "seed_slot1",
                  "slot0_games", "slot1_games", "slot0_wins", "slot1_wins", "slot0_draws", "slot1_draws"):
            rows[0][c] = ""
        write_rows(w.out, rows)
        before = w.raw()
        out, msg, calls = w.call("--resume")
        self.assertIn("no full provenance", msg)
        self.assertIn("--accept-unverified-resume", msg)
        self.assertEqual((calls, w.raw()), (0, before))
        out, msg, calls = w.call("--resume", "--accept-unverified-resume")
        self.assertIsNone(msg, out)
        self.assertIn("UNVERIFIED (accepted)", [l for l in out.splitlines() if l.startswith("pair 0:")][0])
        self.assertEqual((calls, w.raw()), (0, before))

    def test_a_mixed_pilot_run_resumes_identically_and_one_named_pilot_leaves_the_other_at_the_working_pilot(self):
        w = Repo(self)
        args = ("--pilot", "kog3", "--meta-pilot", "kp3", "--allow-pilot-mismatch")
        out, msg, calls = w.call(*args)
        self.assertIsNone(msg, out)
        before = w.raw()
        out, msg, calls = w.call("--resume", *args)
        self.assertEqual((msg, calls, w.raw()), (None, 0, before))
        w2 = Repo(self, npairs=1)
        out, msg, calls = w2.call("--pilot", "kp3", "--allow-pilot-mismatch")
        self.assertIsNone(msg, out)
        self.assertEqual({(r["pilot"], r["deck_pilot"], r["meta_pilot"]) for r in w2.rows()}, {("kp3|kog3", "kp3", "kog3")})
        self.assertEqual(w2.calls[0][2], "kp3,kog3")

    def test_planned_seeds_that_end_where_used_ones_begin_are_fine_and_one_shared_seed_at_the_end_of_slot_0_is_not(self):
        base = 22_900_000_000
        for seed, needle in ((base - 50, None), (base - 49, "planned slot 0 seeds")):
            w = Repo(self)
            out, msg, calls = w.call("--only", "1", "--seed", str(base))
            self.assertIsNone(msg, out)
            w.write_games([w.add_pair(9, "decks/a9.txt", "decks/b9.txt")])
            before = w.raw()
            out, msg, calls = w.call("--resume", "--seed", str(seed))
            if needle is None:
                self.assertIsNone(msg, out)
                self.assertEqual((calls, len(w.rows())), (2, 2))
            else:
                self.assertIn(needle, msg)
                self.assertIn("overlap seeds already used by line 2", msg)
                self.assertEqual((calls, w.raw()), (0, before))

    def test_a_pair_with_its_opponent_under_two_spellings_is_refused_before_any_game(self):
        w = Repo(self)
        d, o = w.pairs[0]
        for spelling in ("./" + o, o.upper(), o.replace("/", "//"), "decks/x/../o0.txt"):
            with open(w.games_csv, "a", newline="") as f:
                csv.writer(f).writerow(["gx", d, spelling, "W", 1])
            out, msg, calls = w.call()
            self.assertIn("names one pair under different spellings", msg, spelling)
            self.assertEqual(calls, 0)
            self.assertFalse(w.out.exists())
            w.write_games(w.pairs)

    def test_unusable_rows_and_the_order_of_the_games_file_do_not_change_the_plan_and_a_ragged_row_is_refused(self):
        w = Repo(self)
        plan, msg, calls = w.call("--pairs-only")
        with open(w.games_csv, "a", newline="") as f:
            csv.writer(f).writerow(["gx", "decks/z9.txt", "decks/y9.txt", "W", 0])           # usable = 0: never played
        again, msg, calls = w.call("--pairs-only")
        self.assertEqual(plan, again)
        w.write_games(list(reversed(w.pairs)))
        reordered, msg, calls = w.call("--pairs-only")
        self.assertEqual(plan, reordered, "the order of the games file must not move any pair's seeds")
        with open(w.games_csv, "a", newline="") as f:
            f.write("gy,decks/d0.txt\n")
        out, msg, calls = w.call("--pairs-only")
        self.assertIn("has a different number of fields than the header", msg)

    def test_the_engine_option_reaches_the_engine_resolver(self):
        w = Repo(self, npairs=1)
        seen = []

        def resolve(project=None, override=None):
            seen.append((project, override))
            return w.engine
        sys.modules["current_engine"].resolve = resolve
        out, msg, calls = w.call("--engine", "/some/engine")
        self.assertIsNone(msg, out)
        w.out.unlink()
        out, msg, calls = w.call()
        self.assertIsNone(msg, out)
        self.assertEqual(seen, [(str(w.root), "/some/engine"), (str(w.root), None)])


@linux_only
class HelperUnits(unittest.TestCase):
    def test_strict_int(self):
        self.assertEqual(calibrate.strict_int(" 500 ", "x"), 500)
        self.assertEqual(calibrate.strict_int("500.0", "x"), 500)
        self.assertEqual(calibrate.strict_int("21107000000", "x"), 21_107_000_000)
        for bad in ("12.7", "inf", "-inf", "nan", "", "  ", "1,000", "ten"):
            with self.assertRaises(ValueError):
                calibrate.strict_int(bad, "x")

    def test_file_sha256_ignores_line_endings_but_not_content(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "a").write_bytes(b"1 Pikachu\n2 Raichu\n")
        (d / "b").write_bytes(b"1 Pikachu\r\n2 Raichu\r\n")
        (d / "c").write_bytes(b"1 Pikachu\n3 Raichu\n")
        self.assertEqual(calibrate.file_sha256(d / "a"), calibrate.file_sha256(d / "b"))
        self.assertNotEqual(calibrate.file_sha256(d / "a"), calibrate.file_sha256(d / "c"))

    def test_working_pilot_reads_the_live_code_not_the_text(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        screen = ('"""Example: ap.add_argument(\'--pilot\', default=\'kp3\')"""\n# ap.add_argument(\'--pilot\', default=\'kp3\')\n'
                  "ap.add_argument('--pilot', type=str, default=('kog3'), help='x')\n"
                  'ap.add_argument("--meta-pilot", help="y", default="kog3")\n')
        floor = 'FLOOR_PILOT = "kp3"\n"""FLOOR_PILOT = "kp3" in a docstring"""\nFLOOR_PILOT: str = "kog3"   # the live one, annotated\n'
        (d / "run_screen.py").write_text(screen)
        (d / "floor.py").write_text("﻿" + floor, encoding="utf-8")                  # a byte-order mark is fine
        pilot, sources = calibrate.working_pilot(str(d))
        self.assertEqual((pilot, set(sources.values())), ("kog3", {"kog3"}))
        (d / "floor.py").write_text("FLOOR_PILOT = = 3\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("cannot parse floor.py", str(cm.exception))
        (d / "floor.py").write_text(floor)
        (d / "run_screen.py").write_text(screen + "ap.add_argument('--pilot', default='kp3')\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("gives --pilot several different defaults", str(cm.exception))
        (d / "run_screen.py").write_text("ap.add_argument('--pilot', default='kog-3')\nap.add_argument('--meta-pilot', default='kog-3')\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("is not a plain pilot name", str(cm.exception))

    def test_working_pilot_fails_closed_on_a_floor_pilot_it_cannot_read_and_accepts_harmless_forms(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        both = "ap.add_argument('--pilot', default='kog3')\nap.add_argument('--meta-pilot', default='kog3')\n"
        (d / "run_screen.py").write_text(both)
        for tail, needle in (('FLOOR_PILOT = os.environ.get("P")\n', "a value that is not a plain string"),
                             ('FLOOR_PILOT = FLOOR_PILOT.replace("3", "4")\n', "a value that is not a plain string"),
                             ('FLOOR_PILOT += "x"\n', "an augmented assignment or a delete"),
                             ("del FLOOR_PILOT\n", "an augmented assignment or a delete")):
            (d / "floor.py").write_text('FLOOR_PILOT = "kog3"\n' + tail)
            with self.assertRaises(ValueError) as cm:
                calibrate.working_pilot(str(d))
            self.assertIn("cannot be read without running it", str(cm.exception), tail)
            self.assertIn(needle, str(cm.exception), tail)
        (d / "floor.py").write_text('FLOOR_PILOT = os.environ.get("P")\nFLOOR_PILOT = "kog3"\n')      # a later plain string settles it
        self.assertEqual(calibrate.working_pilot(str(d))[0], "kog3")
        (d / "run_screen.py").write_text("PIL = 'kog3'\nap.add_argument('-p', '--pilot', default=PIL)\nap.add_argument('--meta-pilot', default=PIL)\n")
        pilot, sources = calibrate.working_pilot(str(d))
        self.assertEqual((pilot, set(sources.values())), ("kog3", {"kog3"}))
        (d / "run_screen.py").write_text("ap.add_argument('-p', '--pilot', default=os.environ.get('P'))\nap.add_argument('--meta-pilot', default='kog3')\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("run_screen.py has no default for --pilot", str(cm.exception))

    def test_working_pilot_ignores_other_calls_no_default_and_assignments_inside_functions(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        both = "ap.add_argument('--pilot', default='kog3')\nap.add_argument('--meta-pilot', default='kog3')\n"
        (d / "run_screen.py").write_text("print('--pilot', default='kp3')\n" + both)                      # not an add_argument call
        (d / "floor.py").write_text('FLOOR_PILOT = "kog3"\ndef helper():\n    FLOOR_PILOT = "kp3"\n')   # a local name, not the module's
        self.assertEqual(calibrate.working_pilot(str(d))[0], "kog3")
        (d / "run_screen.py").write_text("ap.add_argument('--pilot', default=None)\nap.add_argument('--meta-pilot', default='kog3')\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("run_screen.py has no default for --pilot", str(cm.exception))

    def test_norm_path_unifies_every_spelling_of_one_path(self):
        for spelling in ("decks/d0.txt", "Decks\\D0.TXT", "./decks/d0.txt", "decks//d0.txt", "decks/./d0.txt", "decks/x/../d0.txt",
                         "decks/d0.txt/", "  decks/d0.txt  "):
            self.assertEqual(calibrate.norm_path(spelling), "decks/d0.txt", spelling)
        self.assertEqual(calibrate.norm_path(""), "")
        self.assertNotEqual(calibrate.norm_path("decks/d0.txt"), calibrate.norm_path("decks/d1.txt"))

    def test_working_pilot_names_what_is_missing_and_reads_all_three_sources(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        both = "ap.add_argument('--pilot', default='kog3')\nap.add_argument('--meta-pilot', default='kog3')\n"
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("cannot read run_screen.py", str(cm.exception))
        (d / "floor.py").write_text('FLOOR_PILOT = "kog3"\n')
        (d / "run_screen.py").write_text("ap.add_argument('--pilot', default='kog3')\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("run_screen.py has no default for --meta-pilot", str(cm.exception))
        (d / "run_screen.py").write_text(both)
        (d / "floor.py").unlink()
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("cannot read floor.py", str(cm.exception))
        (d / "floor.py").write_text("PILOT = 'kog3'\n")
        with self.assertRaises(ValueError) as cm:
            calibrate.working_pilot(str(d))
        self.assertIn("floor.py has no FLOOR_PILOT", str(cm.exception))
        (d / "floor.py").write_text('FLOOR_PILOT = "kog3"\n')
        pilot, sources = calibrate.working_pilot(str(d))
        self.assertEqual((pilot, len(sources)), ("kog3", 3))

    def test_read_games_skips_unusable_rows_and_names_missing_columns(self):
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "g.csv").write_text("game_id,deck_file,opponent_file,result,usable\ng0,decks/d0.txt,decks/o0.txt,W,1\n"
                                 "g1,decks/d0.txt,decks/o0.txt,L,0\ng2,,decks/o0.txt,W,1\n")
        games, skipped = calibrate.read_games(str(d / "g.csv"))
        self.assertEqual(([g["game_id"] for g in games], len(skipped)), (["g0"], 2))
        (d / "h.csv").write_text("game_id,deck_file,result,usable\ng0,decks/d0.txt,W,1\n")
        with self.assertRaises(SystemExit) as cm:
            calibrate.read_games(str(d / "h.csv"))
        self.assertIn("missing columns ['opponent_file']", str(cm.exception.code))

    def test_the_layout_constants_are_the_ones_in_the_seed_table(self):
        self.assertEqual((calibrate.PAIR_SPACING, calibrate.SLOT_SPACING, calibrate.RESERVED_SEEDS), (10_000, 5_000, 200_000))
        self.assertEqual(rc.layout_errors(20, 10_000), [])
        self.assertEqual(len(rc.layout_errors(21, 10_001)), 2)


if __name__ == "__main__":
    unittest.main()
