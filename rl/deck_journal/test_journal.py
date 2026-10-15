#!/usr/bin/env python3
"""Tests for journal.py, the 'Tests to write first' of rl/deck_journal/SPEC.md (standard library only).

Run from anywhere:  python3 rl/deck_journal/test_journal.py
They read the real repository (deck 01, the Kingambit and Haxorus KW lists, the 12 packets) and write only to
temporary folders.
"""
import base64
import copy
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import journal as J  # noqa: E402

ROOT = J.ROOT
DECK01 = "decks/dustin/01-muk-glimmora-kingambit-regigigas.txt"
KW_KING = "rl/results/pause_games_decisions_2026-10-02/harness/test_oct13/KW261013_010837000.txt"
KW_HAX_A = "rl/results/pause_games_decisions_2026-10-02/harness/test_oct13/KW261013_030351000.txt"
KW_HAX_B = "rl/results/pause_games_new_2026-10-13/decks/KW261013_022530000.txt"
PK = "rl/results/battle_log_packets/"
PACKETS = [PK + p for p in (
    "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS", "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS",
    "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS", "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210823000_iOS",
    "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS", "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_010003000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_010837000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_014423000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS",
    "BATCH_2026-10-13_REMAINING_SIX/20261013_015659000_iOS", "BATCH_2026-10-13_REMAINING_SIX/20261013_020824000_iOS")]
REPLAY_B = "rl/results/kx3_on_rules2_2026-10/replay_b"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def kingambit_doc():
    """A journal with deck 01 and his list, built the way the first fill builds it (no commits needed)."""
    doc = J.new_doc("01-muk-glimmora-kingambit-regigigas", "Kingambit")
    J.add_version(doc, ROOT, list_text=read(DECK01), origin="deck file on main", file=DECK01,
                  reason=("not stated", "test", "none"), by="test", commit="c0")
    J.add_version(doc, ROOT, list_text=read(KW_KING), origin="his list (filmed deck code)", origin_source=KW_KING,
                  reason=("not stated", "test", "none"), by="test", commit="c1")
    return doc


class Ids(unittest.TestCase):
    def test_deck01_and_kingambit_and_haxorus_ids(self):
        self.assertEqual(J.list_id(J.lines_of(read(DECK01))), "35d98d0dcaf2")
        self.assertEqual(J.list_id(J.lines_of(read(KW_KING))), "73dfed58d1d6")
        self.assertEqual(J.list_id(J.lines_of(read(KW_HAX_A))), "b59ea966702c")
        self.assertEqual(J.list_id(J.lines_of(read(KW_HAX_B))), "95c08feb018c")

    def test_curly_apostrophe_still_gives_his_id(self):
        text = read(KW_KING).replace("Professor's Research", "Professor’s Research")
        self.assertIn("’", text)
        lines = J.lines_of(text)
        self.assertEqual(J.list_id(lines), "73dfed58d1d6")
        self.assertNotEqual(J.list_id(lines), "672c29a25f6f")
        self.assertTrue(all("’" not in x for x in lines))
        # the tool's own list never carries the curly mark
        doc = kingambit_doc()
        self.assertTrue(all("’" not in x for v in doc["versions"] for x in v["list"]))

    def test_names_come_from_the_card_database_not_the_packet(self):
        text = read(KW_KING).replace("Poké Ball", "Poke Ball Wrong Name")
        with self.assertRaises(J.Refused):
            J.lines_of(text)


class Diff(unittest.TestCase):
    def test_deck01_to_his_list_is_the_four_lines_and_two_printings(self):
        doc = kingambit_doc()
        a, b = doc["versions"]
        self.assertEqual((a["id"], b["id"]), ("35d98d0dcaf2", "73dfed58d1d6"))
        self.assertEqual(b["parent"], "35d98d0dcaf2")
        self.assertTrue(b["parent_basis"].startswith("inferred"))
        self.assertEqual(sorted(b["diff"]), sorted(["-1 Copycat B1 225", "+1 Lucky Ice Pop B2 145",
                                                    "-1 Alolan Grimer B2 096", "+1 Alolan Grimer A3 110"]))
        self.assertEqual(len(b["diff"]), 4)
        self.assertEqual(sorted(b["printing_only"]), sorted(["Poké Ball P-A 005 -> A2b 111",
                                                             "Professor's Research P-A 007 -> A4b 373"]))
        self.assertFalse(any("Poké Ball" in d or "Professor" in d for d in b["diff"]))
        self.assertIsNone(b["plays_same_as"])

    def test_code_cards_are_entities_and_energy(self):
        doc = kingambit_doc()
        cc = doc["versions"][1]["code_cards"]
        self.assertEqual(cc["energy"], [7])
        self.assertEqual(len(cc["cards"]), 20)
        self.assertEqual(cc["cards"], sorted(cc["cards"]))
        self.assertEqual(cc["cards"].count("trainer:000030"), 2 + 0)   # the two Poke Balls


class Binding(unittest.TestCase):
    def payload(self, packet):
        return J.packet_payload(os.path.join(ROOT, packet))

    def test_all_twelve_packets_bind_to_his_list_and_none_to_deck01(self):
        doc = kingambit_doc()
        self.assertEqual(len(PACKETS), 12)
        for p in PACKETS:
            cc = J.decode_payload(self.payload(p))
            self.assertEqual(J.match_versions(doc, cc), ["73dfed58d1d6"], p)
            self.assertNotEqual(cc, doc["versions"][0]["code_cards"])

    def test_re_encoded_in_sorted_order_still_binds(self):
        doc = kingambit_doc()
        cc = doc["versions"][1]["code_cards"]
        by_hand = base64.b64encode(self._encode_sorted(cc)).decode()
        self.assertNotEqual(by_hand, self.payload(PACKETS[0]))           # the strings differ ...
        self.assertEqual(J.match_versions(doc, J.decode_payload(by_hand)), ["73dfed58d1d6"])   # ... the card sets do not

    @staticmethod
    def _encode_sorted(cc):
        tr = sorted(int(c.split(":")[1]) for c in cc["cards"] if c.startswith("trainer"))
        pk = sorted(int(c.split(":")[1]) for c in cc["cards"] if c.startswith("pokemon"))
        out = bytes([len(tr)]) + b"".join((10_000_000 + x).to_bytes(3, "big") for x in tr)
        out += bytes([len(pk)]) + b"".join(x.to_bytes(3, "big") for x in pk)
        return out + bytes([len(cc["energy"])]) + bytes(cc["energy"])


class SamePlays(unittest.TestCase):
    def test_a_printing_only_version_plays_same_and_shares_one_block(self):
        doc = kingambit_doc()
        text = read(KW_KING).replace("2 Poké Ball A2b 111", "2 Poké Ball P-A 005")
        v = J.add_version(doc, ROOT, list_text=text, origin="agent proposal", parent="73dfed58d1d6",
                          reason=("printing check", "test", "none"), by="test", commit="c2")
        self.assertNotEqual(v["id"], "73dfed58d1d6")
        self.assertEqual(v["plays_same_as"], "73dfed58d1d6")
        self.assertEqual(v["diff"], [])
        self.assertEqual(len(v["printing_only"]), 1)
        view = J.render(doc)
        self.assertEqual(view.count("73dfed58d1d6"), 1)   # the merged block names the root once, in its heading
        blocks = [b for b in view.split("\n") if b.startswith(("NOW PLAYING", "OLDER", "NEWEST", "LISTED"))]
        self.assertEqual(len(blocks), 2)                       # deck 01 and one merged block for his list
        self.assertIn(v["id"], view)
        self.assertNotIn("A2b 111", view)                      # printing-only differences are never shown


class AppendOnly(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.doc = kingambit_doc()
        self.path = os.path.join(self.tmp, "k.json")
        J.save(self.path, self.doc, ROOT, ref=None)

    def played(self, i):
        return J.add_played(self.doc, ROOT, PACKETS[i], by="test", commit_check=True)

    def test_editing_or_deleting_an_earlier_result_is_refused(self):
        self.played(0)
        J.save(self.path, self.doc, ROOT, ref=None)
        for edit in ("change", "delete", "version-gone", "field"):
            new = copy.deepcopy(self.doc)
            v = [x for x in new["versions"] if x["id"] == "73dfed58d1d6"][0]
            if edit == "change":
                v["results"][0]["binding"] = "his note, unconfirmed"
            elif edit == "delete":
                v["results"].pop()
            elif edit == "version-gone":
                new["versions"].pop(0)
            else:
                v["reason"]["text"] = "rewritten"
            with self.assertRaises(J.Refused, msg=edit):
                J.save(self.path, new, ROOT, ref=None)

    def test_the_same_result_twice_is_refused(self):
        self.played(0)
        with self.assertRaises(J.Refused):
            self.played(0)
        self.assertEqual(len(self.doc["versions"][1]["results"]), 1)

    def test_adding_a_new_result_is_allowed(self):
        self.played(0)
        J.save(self.path, self.doc, ROOT, ref=None)
        self.played(1)
        J.save(self.path, self.doc, ROOT, ref=None)
        self.assertEqual(len(J.load(self.path)["versions"][1]["results"]), 2)


class Bots(unittest.TestCase):
    def test_a_bot_result_whose_source_played_another_list_is_refused(self):
        doc = kingambit_doc()
        # replay_b played deck 01's file, never his list
        with self.assertRaises(J.Refused):
            J.add_bot(doc, ROOT, "73dfed58d1d6", REPLAY_B, by="test")
        # a version with a deck file that is not the one in the run is refused too
        other = J.new_doc("02-arceus-crobat", "Arceus")
        J.add_version(other, ROOT, list_text=read("decks/dustin/02-arceus-crobat.txt"), origin="deck file on main",
                      file="decks/dustin/02-arceus-crobat.txt", reason=("not stated", "test", "none"), by="test", commit="c0")
        with self.assertRaises(J.Refused):
            J.add_bot(other, ROOT, other["versions"][0]["id"], REPLAY_B, by="test")

    def test_replay_b_files_under_deck01_with_both_bots_on_the_current_engine(self):
        doc = kingambit_doc()
        res = J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
        self.assertEqual(len(res), 2)
        self.assertEqual(sorted(r["pilot"] for r in res), ["km3", "kx3"])
        self.assertTrue(all(r["current_engine"] and r["n"] == 32 for r in res))
        self.assertEqual(doc["versions"][1]["results"], [])


class Ladder(unittest.TestCase):
    GAMES = {"d01": [{"id": "g1", "ts": 1792000000000, "note": "1st | 20261013_010837000_iOS.MP4 | Victory.", "opp": "Mega Altaria ex", "result": "W"},
                     {"id": "g2", "ts": 1792003000000, "note": "2nd | Defeat.", "opp": "Hydreigon", "result": "L"},
                     {"id": "g3", "ts": 1792006000000, "note": "1st | Win 0-0 by opponent concession at 01:10.", "opp": "Magikarp", "result": "W"},
                     {"id": "g4", "ts": 1792009000000, "note": "1st | Victory.", "opp": "Weezing ex", "result": "W"}]}
    NOTES = {"games": {"d01/g1": {"version": "73dfed58d1d6", "status": "confirmed", "evidence": "x"},
                       "d01/g2": {"version": "73dfed58d1d6", "status": "confirmed", "evidence": "x"},
                       "d01/g3": {"version": "73dfed58d1d6", "status": "confirmed", "evidence": "x"},
                       "d01/g4": {"version": "35d98d0dcaf2", "status": "confirmed", "evidence": "x"}}}

    def test_games_named_by_a_note_for_a_version_without_predictions_are_feedback(self):
        doc = kingambit_doc()
        r = J.ladder_from_notes(doc, "73dfed58d1d6", self.GAMES, self.NOTES, source=KW_KING, by="test", commit="c")
        self.assertEqual(r["kind"], "ladder")
        self.assertEqual(r["basis"], "version notes (no predictions file)")
        self.assertEqual(r["test"], {"wins": 0, "losses": 0})
        self.assertEqual(r["feedback"], {"wins": 2, "losses": 1})
        self.assertEqual(r["concession_wins"], 1)
        self.assertEqual({g["class"] for g in r["games"]}, {"feedback"})
        self.assertEqual(len(r["games"]), 3)                  # g4 is another version's game


class Extras(unittest.TestCase):
    """Beyond the spec's list: a counting reading's rows."""

    def test_ladder_from_a_reading_splits_test_and_feedback_and_counts_concession_wins(self):
        doc = kingambit_doc()
        rows = [{"key": "d01/a", "doc": "d01", "result": "W", "opp": "x", "class": "test", "tie": "assumed",
                 "concession": True, "cards": "checked"},
                {"key": "d01/b", "doc": "d01", "result": "L", "opp": "y", "class": "feedback", "tie": "assumed",
                 "concession": False, "cards": None}]
        r = J.ladder_from_reading(doc, "35d98d0dcaf2", {"groups": {"01-x@35d98d0dcaf2": {"rows": rows}}},
                                  source=DECK01, by="test", commit="c")
        self.assertEqual((r["test"], r["feedback"], r["concession_wins"]),
                         ({"wins": 1, "losses": 0}, {"wins": 0, "losses": 1}, 1))
        self.assertIn("test 1-0", J.render(doc))


class View(unittest.TestCase):
    def test_deck01_bot_numbers_never_appear_under_his_list_and_the_view_is_repeatable(self):
        doc = kingambit_doc()
        J.add_bot(doc, ROOT, "35d98d0dcaf2", REPLAY_B, by="test")
        for p in PACKETS[:2]:
            J.add_played(doc, ROOT, p, by="test", commit_check=True)
        v1, v2 = J.render(doc), J.render(copy.deepcopy(doc))
        self.assertEqual(v1, v2)
        now_block = v1.split("OLDER")[0]
        self.assertIn("73dfed58d1d6", now_block)
        self.assertIn("Bots: none on this list yet", now_block)
        self.assertNotIn("kx3", now_block)
        older = "OLDER" + v1.split("OLDER", 1)[1]
        self.assertIn("kx3", older)
        self.assertIn("current engine", older)
        self.assertNotIn("(exam", older)                       # the stage is "dev" (the manifest), never "exam"
        self.assertIn("in 2 of your games", now_block)
        self.assertLessEqual(max(len(b.splitlines()) for b in v1.split("\n\n")), 12)


# ====================================================================== INTEGRATION_BRIEF Parts B-E
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

FIX = "rl/deck_journal/testdata/setup_run_small"
HIS_FILE = "decks/dustin/01-kingambit-as-played.txt"
STEM = "01-muk-glimmora-kingambit-regigigas"
A_ID, D01_ID, B_ID, C_ID = "73dfed58d1d6", "35d98d0dcaf2", "78b2ba4b7e24", "74075f8030e0"
AMEND1 = "rl/setup_tester/runs/2026-10-15_kingambit_amendment1_run"
NEEDS = ("P2.any", "P2.both", "P2.g1", "P2.g2", "P3.pawn_lead", "P3.pawn_promo", "P3.grimer_muk", "P4.ko", "P4.win",
         "P4.late1", "P4.late2p", "P4.never", "P4.nomoment", "P5.ko", "P5.win")
SEATS = ("first", "second", "pooled")


def fixture_results():
    with open(os.path.join(ROOT, FIX, "results.json"), encoding="utf-8") as fh:
        return json.load(fh)


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", root] + list(args),
                          check=True, capture_output=True).stdout.decode()


class TempRepo:
    """A throwaway git repository with a branch called main; the real checkout is never written."""

    def __init__(self, folder="runs/fix"):
        self.root = tempfile.mkdtemp()
        self.folder = folder
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "commit", "-q", "--allow-empty", "-m", "start")

    def put(self, rel, data):
        p = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(data if isinstance(data, str) else json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    def commit(self, msg="c"):
        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "-m", msg)
        return git(self.root, "rev-parse", "HEAD").strip()

    def run(self, results=None, md=None, extra=None):
        """Commit a copy of the fixture run (results.json edited if given) and return the commit."""
        res = results if results is not None else fixture_results()
        self.put(self.folder + "/results.json", res)
        self.put(self.folder + "/RESULTS.md", md if md is not None else read(FIX + "/RESULTS.md"))
        for k, v in (extra or {}).items():
            self.put(self.folder + "/" + k, v)
        return self.commit()


def reviewed_file(res=None, tester_commit=None):
    res = res or fixture_results()
    p = os.path.join(tempfile.mkdtemp(), "reviewed_testers.json")
    with open(p, "w") as fh:
        json.dump({res["run"]["code_sha256"]: {"tester_commit": tester_commit or res["run"]["tester_commit"],
                                               "reviewed_by": "test", "review_ref": "test"}}, fh)
    return p


def run_doc(which=("A", "B", "C"), deck01=True):
    """Deck 01, his list A (file on main), and the fixture's B (parent A) and C (parent B)."""
    res = fixture_results()["versions"]
    doc = J.new_doc(STEM, "Kingambit")
    why = ("not stated", "test", "none")
    if deck01:
        J.add_version(doc, ROOT, list_text=read(DECK01), origin="deck file on main", file=DECK01, reason=why, by="test",
                      commit="c0")
    J.add_version(doc, ROOT, list_text=read(HIS_FILE), origin="his list (filmed deck code)", file=HIS_FILE, reason=why,
                  by="test", commit="c1")
    if "B" in which:
        J.add_version(doc, ROOT, list_text="\n".join(res["B"]["list"]), origin="agent proposal", parent=A_ID,
                      reason=("test", "test", "none"), by="test", commit="c2")
    if "C" in which:
        J.add_version(doc, ROOT, list_text="\n".join(res["C"]["list"]), origin="agent proposal", parent=B_ID,
                      reason=("test", "test", "none"), by="test", commit="c3")
    return doc


def file_fixture(doc, **kw):
    kw.setdefault("main_ref", "HEAD")
    kw.setdefault("reviewed", reviewed_file())
    return J.add_setup_run(doc, ROOT, FIX, by="test", **kw)


def setups(doc, vid):
    return [r for v in doc["versions"] if v["id"] == vid for r in v["results"] if r["kind"] == "setup"]


def snap(doc):
    return json.dumps(doc, sort_keys=True)


class SetupRoundTrip(unittest.TestCase):
    def test_ids_of_the_fixture(self):
        res = fixture_results()
        self.assertEqual(res["schema"], "setup-tester results v2")
        self.assertEqual({k: v["list_id"] for k, v in res["versions"].items()},
                         {"base": A_ID, "deck01": D01_ID, "B": B_ID, "C": C_ID})

    def test_round_trip_every_stored_number_equals_results_json(self):
        res = fixture_results()
        run = res["run"]
        doc = run_doc()
        out = file_fixture(doc)
        self.assertEqual(len(out), 4)
        for name, v in res["versions"].items():
            (r,) = setups(doc, v["list_id"])
            self.assertEqual(r["run_version"], name)
            self.assertEqual(r["run_base"], {"name": "base", "id": A_ID})
            self.assertEqual(r["source"], FIX)
            self.assertEqual(r["tester"], {"code_sha256": run["code_sha256"], "tester_commit": run["tester_commit"],
                                           "plan_path": run["plan_path"], "plan_sha256": run["plan_sha256"]})
            self.assertEqual(r["seeds"], {"seed_base": 24700000000, "deal_rule": run["deal_rule"]})
            self.assertEqual(r["deals"], {"no_knockout": 2000, "per_clock": 1000})
            self.assertEqual(r["config"]["all"], run["config"])
            self.assertEqual(r["config"]["pawniard_bench"], "first_ko")
            self.assertEqual(r["config"]["setup_bench"], {"trigger": "at_once", "reserved": False})
            self.assertEqual(r["config"]["copycat"]["rule"], "valuation")
            self.assertEqual(r["config"]["copycat"]["label"], "his rule, approximated")
            self.assertEqual(r["config"]["copycat"]["value_table"], run["copycat"]["value_table"])
            self.assertEqual(r["config"]["copycat"]["disagreement"], run["copycat"]["disagreement"][name])
            self.assertNotIn("N=2", json.dumps(r["config"]))
            self.assertEqual(r["p1"], {"pokemon": "Regigigas", "exact": v["p1_exact"], "simulated": v["setup"]["P1"]})
            self.assertEqual(r["rulings"], run["rulings"])
            self.assertEqual(r["held"], [])
            self.assertEqual(r["undecided_rule"], run["undecided_rule"])
            self.assertEqual(r["not_valued"], {"not_played_by_script": run["not_played_by_script"],
                                               "acts_on_damage": run["acts_on_damage"]})
            for c, ci in run["clocks"].items():
                self.assertEqual(r["clocks"][c]["label"], ci["label"])
                self.assertEqual(r["clocks"][c]["strongest"], ci["strongest"])
                self.assertEqual(r["clocks"][c]["strongest_source"], ci["strongest_source"])
                self.assertEqual(r["clocks"][c]["zero_by_construction"], ci["zero_by_construction"])
                self.assertEqual(r["clocks"][c]["source_sha256"], ci["source_sha256"])
                for m in NEEDS:
                    for s in SEATS:
                        cell, got = v["clock"][c][m][s], r["plan_lines"][c][m][s]
                        self.assertEqual((got["x_no"], got["x_yes"], got["n"]), (cell["x_no"], cell["x_yes"], cell["n"]))
                        self.assertEqual(got["range"], cell["boot"] if ci["kind"] == "recorded" else cell["wilson"])
            ds = r["descriptive"]["setup"]
            self.assertEqual(len(ds), 67)
            for m, cells in ds.items():
                self.assertEqual(cells, {s: {"x": v["setup"][m][s]["x"], "n": v["setup"][m][s]["n"],
                                             "wilson": v["setup"][m][s]["wilson"]} for s in SEATS})
            self.assertEqual(r["descriptive"]["setup_mean"]["G5.n5"], v["setup"]["G5.n5"])
            self.assertEqual(r["descriptive"]["exact"], v["exact"])
        self.assertEqual(setups(doc, B_ID)[0]["commit"], git(ROOT, "log", "-1", "--format=%H", "--", FIX).strip())
        self.assertEqual(len(setups(doc, B_ID)[0]["files_sha256"]), 2)
        self.assertTrue(setups(doc, B_ID)[0]["main_commit"])

    def test_save_load_render_check(self):
        doc = run_doc()
        file_fixture(doc)
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, STEM + ".json")
        J.save(path, doc, ROOT, ref=None)
        self.assertEqual(J.load(path), doc)
        self.assertEqual(J.render(doc), J.render(J.load(path)))
        J._write_view(doc, path)
        self.assertEqual(J.main(["check", "--deck", STEM, "--dir", tmp]), 0)


class SetupVersionsAndRepeats(unittest.TestCase):
    def test_a_version_not_in_the_journal_is_refused_then_filed_after_add_version(self):
        doc = run_doc(which=())
        before = snap(doc)
        with self.assertRaises(J.Refused) as cm:
            file_fixture(doc)
        self.assertEqual(snap(doc), before)
        self.assertIn(B_ID, str(cm.exception))
        self.assertIn(C_ID, str(cm.exception))
        self.assertIn("add-version", str(cm.exception))
        self.assertIn('--origin "agent proposal" --parent', str(cm.exception))
        # a tester run never creates a version: B is added by hand, then it files (C still missing -> refused)
        J.add_version(doc, ROOT, list_text="\n".join(fixture_results()["versions"]["B"]["list"]),
                      origin="agent proposal", parent=A_ID, reason=("t", "t", "none"), by="test", commit="c")
        with self.assertRaises(J.Refused):
            file_fixture(doc)
        out = file_fixture(doc, only=[A_ID, D01_ID, B_ID])
        self.assertEqual(len(out), 3)

    def test_only_files_some_versions_and_records_also_in_run(self):
        doc = run_doc(which=())
        out = file_fixture(doc, only=[A_ID, D01_ID])
        self.assertEqual(sorted(r["run_version"] for r in out), ["base", "deck01"])
        for r in out:
            self.assertEqual(sorted(x["id"] for x in r["also_in_run"]), sorted([B_ID, C_ID]))
        self.assertEqual(setups(doc, B_ID), [])

    def test_only_naming_a_version_the_journal_lacks_is_refused(self):
        doc = run_doc(which=())
        with self.assertRaises(J.Refused) as cm:
            file_fixture(doc, only=[A_ID, B_ID])
        self.assertIn(B_ID, str(cm.exception))

    def test_the_same_run_twice_and_a_recommitted_run(self):
        repo = TempRepo()
        c1 = repo.run()
        rev = reviewed_file()
        doc = run_doc()
        J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main", reviewed=rev)
        before = snap(doc)
        with self.assertRaises(J.Refused):
            J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main", reviewed=rev)
        self.assertEqual(snap(doc), before)
        # the same folder re-committed with one changed number
        res = fixture_results()
        old = res["versions"]["base"]["clock"]["his"]["P4.ko"]["first"]["x_no"]
        res["versions"]["base"]["clock"]["his"]["P4.ko"]["first"]["x_no"] = old - 1
        c2 = repo.run(results=res)
        self.assertNotEqual(c1, c2)
        with self.assertRaises(J.Refused) as cm:
            J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main", reviewed=rev)
        self.assertIn("corrects", str(cm.exception))
        self.assertEqual(snap(doc), before)
        J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main", reviewed=rev, only=[A_ID],
                        corrects="%s@%s" % (repo.folder, c1))
        view = J.render(doc)
        self.assertIn("%.1f%%" % (100 * (old - 1) / 500), view)
        self.assertNotIn("%.1f%%" % (100 * old / 500), view)
        self.assertIn("corrected", view)
        self.assertEqual(len(setups(doc, A_ID)), 2)          # the earlier result stays; the view hides it


class SetupRefusals(unittest.TestCase):
    def refused(self, mutate=None, *, repo=None, results=None, extra=None, rev=None, text=None, md=None, **kw):
        res = results or fixture_results()
        if mutate:
            mutate(res)
        repo = repo or TempRepo()
        repo.run(results=res, extra=extra, md=md)
        doc = run_doc()
        before = snap(doc)
        with self.assertRaises(J.Refused) as cm:
            J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main",
                            reviewed=rev or reviewed_file(), **kw)
        self.assertEqual(snap(doc), before)
        if text:
            self.assertIn(text, str(cm.exception))
        return str(cm.exception)

    def test_amendment1_folder_is_not_on_main(self):
        doc = run_doc()
        before = snap(doc)
        with self.assertRaises(J.Refused) as cm:
            J.add_setup_run(doc, ROOT, AMEND1, by="test", main_ref="origin/main", reviewed=reviewed_file())
        self.assertIn("not on main", str(cm.exception))
        self.assertEqual(snap(doc), before)

    def test_v1_results_json_is_refused_by_schema(self):
        try:
            v1 = json.loads(git(ROOT, "show", "eeaf54c5:%s/results.json" % AMEND1))
        except subprocess.CalledProcessError:
            self.skipTest("eeaf54c5 is not in this clone")
        self.assertNotEqual(v1.get("schema"), "setup-tester results v2")
        self.refused(results=v1, text="schema")

    def test_code_shas_not_reviewed(self):
        for pre in ("6fc5b64c8588", "d67307200c3c"):
            self.refused(lambda r, pre=pre: r["run"].__setitem__("code_sha256", pre + "0" * 52), text="not reviewed")

    def test_tester_commit_must_match_the_reviewed_one(self):
        self.refused(rev=reviewed_file(tester_commit="0" * 40), text="tester_commit")

    def test_tree_not_clean(self):
        self.refused(lambda r: r["run"].__setitem__("tree_clean", False), text="tree_clean")

    def test_untracked_file_in_the_run_folder(self):
        repo = TempRepo()
        repo.run()
        repo.put(repo.folder + "/notes.txt", "x")
        doc = run_doc()
        with self.assertRaises(J.Refused) as cm:
            J.add_setup_run(doc, repo.root, repo.folder, by="test", main_ref="main", reviewed=reviewed_file())
        self.assertIn("uncommitted", str(cm.exception))

    def test_superseded(self):
        self.refused(extra={"SUPERSEDED.md": "old"}, text="SUPERSEDED")

    def test_a_missing_field(self):
        self.refused(lambda r: r["run"].pop("seed_base"), text="seed_base")

    def test_list_edited_so_the_id_disagrees(self):
        def edit(r):
            r["versions"]["B"]["list"] = [x.replace("2 Rare Candy", "1 Rare Candy") for x in r["versions"]["B"]["list"]]
        self.refused(edit, text="disagree")

    def test_missing_setup_p1(self):
        self.refused(lambda r: r["versions"]["base"]["setup"].pop("P1"), text="P1")

    def test_missing_p1_exact(self):
        self.refused(lambda r: r["versions"]["base"].pop("p1_exact"), text="p1_exact")

    def test_two_versions_with_one_id(self):
        def dup(r):
            for k in ("list", "list_id", "card_list_sha256"):
                r["versions"]["C"][k] = r["versions"]["B"][k]
        self.refused(dup, text="share")

    def test_x_yes_below_x_no(self):
        def bad(r):
            c = r["versions"]["base"]["clock"]["his"]["P4.ko"]["first"]
            c["x_yes"] = c["x_no"] - 1
        self.refused(bad, text="x_no")

    def test_impossible_counts(self):
        def n_wrong(r):
            r["versions"]["base"]["setup"]["P1"]["first"]["n"] = 999
        self.refused(n_wrong, text="n")

        def x_over(r):
            r["versions"]["base"]["setup"]["P1"]["first"]["x"] = 5000
        self.refused(x_over, text="x")

        def range_bad(r):
            r["versions"]["base"]["clock"]["fast"]["P4.ko"]["first"]["wilson"] = [0.9, 0.1]
        self.refused(range_bad, text="range")


class SetupPaired(unittest.TestCase):
    def setUp(self):
        self.doc = run_doc()
        file_fixture(self.doc)
        self.res = fixture_results()["versions"]

    def comp(self, vid, against):
        (r,) = setups(self.doc, vid)
        return [c for c in r["comparisons"] if c["against"] == against]

    def test_a_against_deck01_is_the_deck01_against_base_inverted(self):
        (inv,) = self.comp(A_ID, D01_ID)
        self.assertEqual(inv["how"], "inverted")
        (dir_,) = self.comp(D01_ID, A_ID)
        self.assertEqual(dir_["how"], "direct")
        for m, seats in dir_["setup"].items():
            for s, (d, lo, hi) in seats.items():
                self.assertEqual(inv["setup"][m][s], [-d, -hi, -lo])
        raw = self.res["deck01"]["paired_vs_base"]["G3.Alolan Grimer.t1"]["first"]
        self.assertEqual(dir_["setup"]["G3.Alolan Grimer.t1"]["first"], raw)
        for c, ms in dir_["clock"].items():
            for m, cell in ms.items():
                d, lo, hi = cell["diff"]
                self.assertEqual(inv["clock"][c][m]["diff"], [-d, -hi, -lo])

    def test_b_against_a_is_direct_and_c_against_b_is_absent(self):
        (b_a,) = self.comp(B_ID, A_ID)
        self.assertEqual(b_a["how"], "direct")
        self.assertEqual(b_a["clock"]["his"]["P4.ko"]["diff"], self.res["B"]["clock"]["his"]["P4.ko"]["diff"]["pooled"])
        self.assertEqual(self.comp(C_ID, B_ID), [])
        self.assertEqual(len(self.comp(C_ID, A_ID)), 1)
        d, lo, hi = b_a["clock"]["fast"]["P4.ko"]["diff"]
        self.assertEqual(b_a["clock"]["fast"]["P4.ko"]["flag"], (lo > 0 or hi < 0) and abs(d) >= 0.01)


class SetupShapes(unittest.TestCase):
    def test_g5_is_a_mean_without_a_range_and_x_over_n_is_accepted_for_it_only(self):
        doc = run_doc()
        file_fixture(doc)
        (r,) = setups(doc, A_ID)
        g5 = r["descriptive"]["setup_mean"]["G5.n5"]
        self.assertTrue(all("wilson" not in g5[s] and "range" not in g5[s] for s in SEATS))
        res = fixture_results()
        res["versions"]["base"]["setup"]["G5.n5"]["first"]["x"] = 5000          # empty turns: a count that can exceed n
        repo = TempRepo()
        repo.run(results=res)
        out = J.add_setup_run(run_doc(), repo.root, repo.folder, by="t", main_ref="main", reviewed=reviewed_file())
        self.assertEqual(len(out), 4)

    def test_recorded_clocks_store_boot_and_fixed_clocks_wilson(self):
        doc = run_doc()
        file_fixture(doc)
        (r,) = setups(doc, A_ID)
        for c in ("his", "his_seat", "bot"):
            self.assertEqual(r["plan_lines"][c]["P4.ko"]["first"]["range_method"], "boot")
        for c in ("fast", "medium", "slow", "ref190", "ref220"):
            self.assertEqual(r["plan_lines"][c]["P4.ko"]["first"]["range_method"], "wilson")
        self.assertEqual(r["clocks"]["his"]["kind"], "recorded")
        self.assertEqual(r["clocks"]["slow"]["kind"], "fixed")


class SetupView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = run_doc()
        J.add_played(cls.doc, ROOT, PACKETS[0], by="test", commit_check=True)           # A is NOW PLAYING
        file_fixture(cls.doc, only=[A_ID, B_ID, C_ID])
        cls.view = J.render(cls.doc)
        cls.blocks = {}
        for b in cls.view.split("\n\n")[1:]:
            cls.blocks[re.search(r"\s([0-9a-f]{12})", b.splitlines()[0])[1]] = b

    def line(self, vid, start):
        (x,) = [l for l in self.blocks[vid].splitlines() if l.lstrip().startswith(start)]
        return x

    def test_p_lines_come_in_order_before_the_speed_line_and_every_p4_line_has_both_columns(self):
        b = self.blocks[A_ID].splitlines()
        idx = [next(i for i, l in enumerate(b) if l.lstrip().startswith(s)) for s in
               ("Setup odds", "P1", "P3", "P4-P5", "P4, set paces", "Against", "Not valued", "Speed")]
        self.assertEqual(idx, sorted(idx))
        for l in b:
            if l.lstrip().startswith(("P4-P5", "P4, set paces")):
                self.assertIn("knocks out", l)
                self.assertIn("wins outright", l)
        self.assertIn("P2", self.line(A_ID, "P1"))
        self.assertRegex(self.line(A_ID, "P3"), r"\d+\.\d%")             # P3 by cause, with numbers (R2 is recorded)

    def test_header_copycat_wording_and_no_placeholder(self):
        h = self.line(A_ID, "Setup odds")
        self.assertIn("Copycat played by your valuation, approximated (value table in the run's RESULTS.md)", h)
        self.assertNotIn("N=2", self.view)
        self.assertNotIn("placeholder", self.view)

    def test_not_valued_lines_name_the_changed_cards(self):
        self.assertIn("2 Lucky Ice Pop out", self.line(B_ID, "Not valued"))
        c = self.line(C_ID, "Not valued")
        for s in ("2 Lucky Ice Pop out", "1 Ilima out", "1 Red in"):
            self.assertIn(s, c)
        self.assertIn("1 Lucky Ice Pop in", self.line(A_ID, "Not valued"))
        self.assertIn("act on damage", self.line(A_ID, "Not valued"))

    def test_speed_line_is_descriptive_and_names_the_bench_policy(self):
        s = self.line(A_ID, "Speed")
        self.assertIn("descriptive", s)
        self.assertIn("benched at once", s)

    def test_zero_by_construction_is_printed_for_the_lines_the_run_lists(self):
        paces = self.line(A_ID, "P4, set paces")
        self.assertIn("zero by construction", paces)
        medium = [x for x in paces.split(";") if "medium" in x][0]
        self.assertIn("zero by construction", medium)
        slow = [x for x in paces.split(";") if "slow" in x][0]
        self.assertIn("180-HP", slow)
        self.assertNotIn("220", paces)
        self.assertNotIn("zero by construction", slow)

    def test_no_setup_number_appears_under_deck01_and_blocks_are_short_and_repeatable(self):
        self.assertNotIn("Setup odds (", self.blocks[D01_ID])
        self.assertIn("Setup odds: not computed yet", self.blocks[D01_ID])
        for b in self.blocks.values():
            self.assertLessEqual(len(b.splitlines()), 16)
        self.assertEqual(self.view, J.render(copy.deepcopy(self.doc)))

    def test_changed_and_against_lines_use_now_playing_for_agent_proposals(self):
        self.assertIn(A_ID, self.line(C_ID, "Against"))       # C's parent is B; the reference is what he plays
        self.assertIn(D01_ID, self.line(A_ID, "Against"))     # his list's reference is its parent
        self.assertIn(A_ID, self.line(C_ID, "Changed"))
        self.assertIn("built on %s" % B_ID, self.line(C_ID, "Changed"))

    def test_zero_digits_in_held_lines(self):
        repo = TempRepo()
        res = fixture_results()
        res["run"]["rulings"] = {}
        repo.run(results=res)
        doc = run_doc()
        J.add_setup_run(doc, repo.root, repo.folder, by="t", main_ref="main", reviewed=reviewed_file(), only=[A_ID])
        (r,) = setups(doc, A_ID)
        self.assertEqual(sorted(r["held"]), ["P2", "P3"])
        view = J.render(doc)
        held = [l for l in view.splitlines() if "held until a rule is settled" in l]
        self.assertEqual(len(held), 1)
        self.assertNotRegex(re.sub(r"P\d", "", held[0]), r"\d")


class PartB(unittest.TestCase):
    def test_a_bot_deck_path_resolves_to_the_list_it_holds(self):
        doc = kingambit_doc()
        v = J.find(doc, A_ID)
        kw = "rl/results/pause_games_new_2026-10-13/v2/decks/KW261012_203719000.txt"
        info = J.bot_deck_info(v, ROOT, J.mp.Git(ROOT), "HEAD", deck_path=kw)
        self.assertEqual(info["version_id"], A_ID)
        self.assertEqual(info["name"], "KW261012_203719000")
        self.assertEqual(info["deck_path"], kw)
        self.assertEqual(info["card_list_sha256"][:12], A_ID)
        self.assertTrue(info["file_sha256"])
        with self.assertRaises(J.Refused):                               # another list
            J.bot_deck_info(v, ROOT, J.mp.Git(ROOT), "HEAD", deck_path=KW_HAX_A)
        with self.assertRaises(J.Refused):                               # not committed on main
            J.bot_deck_info(v, ROOT, J.mp.Git(ROOT), "HEAD", deck_path="rl/deck_journal/testdata/nothing.txt")

    def test_tie_breaks_to_now_playing_then_newest_and_a_proposal_needs_a_parent(self):
        doc = kingambit_doc()
        d01, his = doc["versions"]
        self.assertEqual(J.choose_parent(doc, [d01, his])["id"], his["id"])          # nothing played: the newest
        d01["results"].append({"kind": "played", "video": "20261013_020824000_iOS.MP4", "date": "2026-10-12"})
        self.assertEqual(J.now_playing_id(doc), D01_ID)
        self.assertEqual(J.choose_parent(doc, [d01, his])["id"], D01_ID)             # NOW PLAYING, not the newest
        with self.assertRaises(J.Refused):
            J.add_version(doc, ROOT, list_text=read(KW_HAX_A), origin="agent proposal",
                          reason=("t", "t", "none"), by="t", commit="c")

    def test_the_twelve_outcomes_dates_and_the_five_named_results(self):
        doc = kingambit_doc()
        for p in PACKETS:
            J.add_played(doc, ROOT, p, by="test", commit_check=True)
        rs = [r for r in doc["versions"][1]["results"] if r["kind"] == "played"]
        self.assertEqual(len(rs), 12)
        self.assertTrue(all(r["result"] in ("win", "loss", "draw") for r in rs))
        by = {r["video"][:15]: r for r in rs}
        for k, want in (("20261012_010706", "win"), ("20261012_210823", "win"), ("20261012_203719", "win"),
                        ("20261012_210041", "loss"), ("20261012_225319", "loss")):
            self.assertEqual(by[k]["result"], want, k)
            self.assertIn("result_raw", by[k])
            self.assertIn("result_key", by[k])
        self.assertTrue(all(r["date"] in ("2026-10-11", "2026-10-12") for r in rs))
        self.assertIn("Oct 11-12", J.render(doc))

    def test_utc_video_names_convert_to_chicago(self):
        self.assertEqual(J.local_date_of_video("20261013_020824000_iOS.MP4"), "2026-10-12")
        self.assertEqual(J.local_date_of_video("20261012_010706000_iOS.MP4"), "2026-10-11")
        self.assertEqual(J.local_date_of_video("20261012_210041000_iOS.MP4"), "2026-10-12")

    def test_bot_lines_group_by_game_set_and_carry_the_kx3_caveat(self):
        doc = J.load(os.path.join(J.JOURNALS, STEM + ".json"))
        bots = [r for v in doc["versions"] if v["id"] == D01_ID for r in v["results"] if r["kind"] == "bot"]
        self.assertEqual(len(bots), 19)
        self.assertEqual(sum(r["current_engine"] for r in bots), 2)
        self.assertEqual(sum(r["run_kind"] == "floor" for r in bots), 1)
        old = [r for r in bots if not r["current_engine"]]
        sets = len({r["games_sha256"] for r in old})
        self.assertEqual((len(old), sets), (17, 11))
        view = J.render(doc)
        self.assertIn("17 results on 11 game sets", view)
        self.assertNotIn("from 9 runs", view)
        self.assertIn("counts wins only", view)
        self.assertIn("optimistic end", view)
        self.assertRegex(view, r"kx3 games 32 of \d+")
        self.assertNotIn("(exam", view)
        self.assertTrue(all("knows_the_panel_lists" in r and "stage" in r and "games_in_run" in r for r in bots))
        self.assertTrue(all(r["stage"] in ("dev", None) for r in bots))

    def test_the_energy_alias_with_a_file_is_refused(self):
        repo = TempRepo()
        text = read(KW_KING)
        alias = re.sub(r"(?im)^energy:.*$", "Energy: Dark", text)
        self.assertNotEqual(alias, text)
        repo.put("decks/x.txt", alias)
        repo.commit()
        doc = J.new_doc("x", "x")
        with self.assertRaises(J.Refused):
            J.add_version(doc, repo.root, list_text=alias, origin="deck file on main", file="decks/x.txt",
                          reason=("t", "t", "none"), by="t", commit="c", main_ref="main")
        repo.put("decks/y.txt", text)
        repo.commit()
        v = J.add_version(doc, repo.root, list_text=text, origin="deck file on main", file="decks/y.txt",
                          reason=("t", "t", "none"), by="t", commit="c", main_ref="main")
        self.assertEqual(v["id"], A_ID)

    def test_each_bot_line_in_a_merged_block_names_its_own_version(self):
        doc = kingambit_doc()
        text = read(KW_KING).replace("2 Poké Ball A2b 111", "2 Poké Ball P-A 005")
        v = J.add_version(doc, ROOT, list_text=text, origin="agent proposal", parent=A_ID,
                          reason=("t", "t", "none"), by="t", commit="c2")
        mk = lambda label, n, pct: {"kind": "bot", "at": "x", "by": "t", "source": "s/" + label, "commit": "c",
                                    "bot": label, "label": label, "run_kind": "exam", "arm": "X", "pilot": "km3",
                                    "engine": {"label": "e", "key": "k"}, "current_engine": True, "counts": "c",
                                    "n": n, "wins": 1, "ties": 0, "losses": 0, "number_pct": pct,
                                    "ci95_wilson": [1.0, 2.0], "games_sha256": label, "tested": "t", "note": None,
                                    "stage": "dev", "games_in_run": n, "knows_the_panel_lists": False,
                                    "run_name": label, "main_commit": "m", "deck_path": None}
        doc["versions"][1]["results"].append(mk("kmA", 8, 10.0))
        v["results"].append(mk("kmB", 9, 20.0))
        view = J.render(doc)
        la = [l for l in view.splitlines() if "10.0%" in l]
        lb = [l for l in view.splitlines() if "20.0%" in l]
        self.assertTrue(la and lb)
        self.assertTrue(all(A_ID in l and v["id"] not in l for l in la))
        self.assertTrue(all(v["id"] in l and (A_ID not in l) for l in lb))

    def test_a_branch_only_commit_is_refused(self):
        repo = TempRepo()
        repo.put("decks/x.txt", read(KW_KING))
        repo.commit()
        git(repo.root, "checkout", "-q", "-b", "side")
        repo.put("decks/z.txt", read(KW_KING) + "\n")
        repo.commit()
        self.assertEqual(J.committed(repo.root, "decks/x.txt", main_ref="main"),
                         git(repo.root, "log", "-1", "--format=%H", "--", "decks/x.txt").strip())
        with self.assertRaises(J.Refused) as cm:
            J.committed(repo.root, "decks/z.txt", main_ref="main")
        self.assertIn("main", str(cm.exception))

    def test_a_changed_title_and_a_new_key_are_detected(self):
        doc = kingambit_doc()
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "k.json")
        J.save(path, doc, ROOT, ref=None)
        new = copy.deepcopy(doc)
        new["title"] = "Another title"
        with self.assertRaises(J.Refused):
            J.save(path, new, ROOT, ref=None)
        new = copy.deepcopy(doc)
        new["versions"][0]["sneaky"] = 1
        with self.assertRaises(J.Refused):
            J.save(path, new, ROOT, ref=None)

    def test_save_checks_the_copy_on_main_too(self):
        repo = TempRepo()
        doc = kingambit_doc()
        path = os.path.join(repo.root, "journals", "k.json")
        os.makedirs(os.path.dirname(path))
        J.save(path, doc, repo.root, ref=None)
        repo.commit()
        new = copy.deepcopy(doc)
        new["title"] = "changed"
        os.remove(path)                                         # the disk copy is gone; main still holds the old one
        with self.assertRaises(J.Refused):
            J.save(path, new, repo.root, ref="main")

    def test_a_correcting_result_replaces_the_earlier_one_in_the_view(self):
        doc = kingambit_doc()
        old = {"kind": "note", "at": "2026-10-15T10:00:00Z", "by": "t", "source": "s", "commit": "c1", "text": "old note",
               "basis": "old"}
        new = {"kind": "note", "at": "2026-10-16T10:00:00Z", "by": "t", "source": "s", "commit": "c2", "text": "new note",
               "basis": "new", "corrects": {"kind": "note", "source": "s", "commit": "c1", "version": A_ID}}
        v = J.find(doc, A_ID)
        v["results"] += [old, new]
        view = J.render(doc)
        self.assertIn("new note", view)
        self.assertNotIn("old note", view)
        self.assertIn("(corrected Oct 16)", view)
        self.assertEqual(len(v["results"]), 2)

    def test_the_first_fill_holds_the_proposals_and_withdrawn_lists(self):
        doc = J.load(os.path.join(J.JOURNALS, STEM + ".json"))
        by = {v["id"]: v for v in doc["versions"]}
        a = by[A_ID]
        self.assertEqual(a["file"], HIS_FILE)
        props = [v for v in doc["versions"] if v["origin"] == "agent proposal"]
        self.assertEqual(len(props), 5)
        withdrawn = [v for v in props if v["reason"]["text"].startswith("WITHDRAWN Oct 15: cuts cards his plan uses")]
        self.assertEqual(sorted(v["id"] for v in withdrawn), sorted([B_ID, C_ID, "a76361f7ffbc"]))
        self.assertEqual(by[B_ID]["parent"], A_ID)
        self.assertEqual(by[C_ID]["parent"], B_ID)
        self.assertEqual(by["a76361f7ffbc"]["parent"], B_ID)
        current = [v for v in props if v not in withdrawn]
        self.assertEqual(len(current), 2)
        for v in current:
            self.assertEqual(v["parent"], A_ID)
            self.assertEqual(v["origin_source"], "laptop review + Astra's review, Oct 15 (tester fix brief section D)")
        self.assertEqual(sorted(sorted(v["diff"]) for v in current),
                         sorted([sorted(["-1 Lucky Ice Pop B2 145", "+1 Rare Candy A3 144"]),
                                 sorted(["-1 Lucky Ice Pop B2 145", "-1 Professor's Research A4b 373",
                                         "+1 Rare Candy A3 144", "+1 Juliana B3a 071"])]))
        self.assertTrue(all(v["origin_source"].endswith("DELIVERABLE.md") for v in withdrawn))
        played = [r for r in a["results"] if r["kind"] == "played"]
        self.assertEqual(len(played), 12)
        self.assertTrue(all(r["result"] for r in played))
        self.assertNotIn("setup", {r["kind"] for v in doc["versions"] for r in v["results"]})
        self.assertIn("Setup odds: not computed yet", J.render(doc))


if __name__ == "__main__":
    unittest.main(verbosity=1)
