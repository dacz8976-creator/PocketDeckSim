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
        self.assertEqual(view.count("73dfed58d1d6"), view.count("73dfed58d1d6"))
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
        self.assertTrue(all(r["in_bot_comparison"] and r["n"] == 32 for r in res))
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
        self.assertIn("in 2 of your games", now_block)
        self.assertLessEqual(max(len(b.splitlines()) for b in v1.split("\n\n")), 12)


if __name__ == "__main__":
    unittest.main(verbosity=1)
