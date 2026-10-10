"""Tests for handoff_for_classify.py, the adapter between sitting2_check.py's hand-off and classify_8c.py (rules switch 2, step 8c; the
laptop's spec, Oct 10, item 2). The rows are made here: one is the shape sitting2_check.py writes (its HEADER, compact-JSON counters),
one the cloud's classify_check_8b/handoff_8b.tsv shape (the 13 columns classify_8c.py reads; one real row's values, cut short).
Run: python3 -m unittest test_handoff_for_classify   (from this folder)"""
import ast, json, os, re, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import handoff_for_classify as hf  # noqa: E402
import tightened_rule as tr  # noqa: E402

SITTING2 = list(hf.SITTING2)
CLASSIFY = list(hf.CLASSIFY)
ROW = {
    "step": "8", "bot": "km3", "pairing": "35", "i": "2", "seed": "23100350002",
    "held_file": "decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt", "held_blob": "34c28791effe9036451cd4901f97d517052ffc48",
    "panel_file": "rl/results/engine_switch_rules_2026-10/scratch_8b/meowth_carefree.txt", "panel_blob": "26815670db336f3d49c642d0ddaf2abf7c00bc64",
    "old_moves": "2b5ba65a790dbe34", "new_moves": "681155c48abbaa7c", "moves_differ": "yes", "differing_fields": "moves,points",
    "old_winner": "0", "new_winner": "1", "old_points": "[3,1]", "new_points": "[1,3]", "category": "reach",
    "reach2_counters": '{"attack_return_weakness":[67],"coin_queued_by_attack":{"Wild Swing":[93]}}',
    "offgate2_counters": '{"offgate_by_attack":{"Diving Icicles":[39],"Wild Swing":[104]},"offgate_plain_attack_damage":[39,104]}',
    "round1_counters": '{"coin_full_prevention":[93],"coin_queued_by_attack (round-1 keys)":{"Diving Icicles":[39]}}',
    "superset_counters": '{"coin_defender_attack":3}',
    "revert_switches": "DECKGYM_FLAT_RETURN_DAMAGE,DECKGYM_NO_PLAIN_HIT_COIN,DECKGYM_PLAIN_QUEUED_SITES",
}
ROW_8B = {
    "step": "8b", "bot": "km3", "pairing": "35", "i": "2", "seed": "23100350002",
    "held_file": ROW["held_file"], "held_blob": ROW["held_blob"], "panel_file": ROW["panel_file"], "panel_blob": ROW["panel_blob"],
    "old_moves": "2b5ba65a790dbe34", "new_moves": "681155c48abbaa7c",
    "exact_counters": '{"attack_return_weakness": [], "chase_order": {"discarded": 2, "names": {"Mantyke": 1}, "offered": 2}, '
                      '"coin_full_prevention": [93], "coin_queued_by_attack": {"Diving Icicles": [39], "Wild Swing": [93]}, '
                      '"discard_attacks": {"Diving Icicles": [1, 0, 0, 0]}}',
    "offgate_counters": '{"offgate_by_attack": {"Diving Icicles": [39], "Wild Swing": [104]}, "offgate_return_by_source": {"Rocky Helmet": [67]}}',
}
REACH = ("will_confused_attack", "coin_own_side_split", "trap_territory_offer_changed", "attack_return_weakness",
         "coin_queued_by_attack", "coin_plain_damage_by_attack")


def row2(**over):
    return {**ROW, **over}


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.src, self.dst = self.tmp / "handoff_8c.tsv", self.tmp / "handoff_for_classify.tsv"

    def write(self, header, rows, path=None):
        (path or self.src).write_text("\t".join(header) + "\n" + "".join("\t".join(r[c] for c in header) + "\n" for r in rows), encoding="utf-8", newline="\n")

    def read(self, path=None):
        lines = (path or self.dst).read_text(encoding="utf-8").split("\n")
        header = lines[0].split("\t")
        return header, [dict(zip(header, ln.split("\t"))) for ln in lines[1:] if ln]

    def refused(self, why=None):
        self.assertFalse(self.dst.exists())
        with self.assertRaises(hf.Refuse) as cm:
            hf.convert(self.src, self.dst)
        self.assertFalse(self.dst.exists(), "a refusal writes nothing")
        if why:
            self.assertIn(why, str(cm.exception))
        logs = []
        self.assertEqual(hf.main(["--in", str(self.src), "--out", str(self.dst)], log=lambda *a, **k: logs.append(" ".join(map(str, a)))), 2)
        self.assertTrue(logs[-1].startswith("REFUSED"), logs)
        self.assertFalse(self.dst.exists())


class SittingTwoShape(Case):
    def test_reach2_becomes_exact_and_offgate2_becomes_offgate_in_their_places(self):
        rows = [ROW, row2(i="3", reach2_counters="{}", offgate2_counters="{}", category="none")]
        self.write(SITTING2, rows)
        self.assertEqual(hf.main(["--in", str(self.src), "--out", str(self.dst)], log=lambda *a, **k: None), 0)
        header, out = self.read()
        self.assertEqual(header, [hf.RENAME.get(c, c) for c in SITTING2])
        self.assertEqual(len(out), 2)
        for got, want in zip(out, rows):
            self.assertEqual(got["exact_counters"], want["reach2_counters"])
            self.assertEqual(got["offgate_counters"], want["offgate2_counters"])
            for c in SITTING2:
                if c not in hf.RENAME:
                    self.assertEqual(got[c], want[c], c)                  # every other column, round1 and superset included, unchanged

    def test_the_output_has_every_column_classify_8c_reads(self):
        src = (HERE / "classify_8c.py").read_text(encoding="utf-8")
        used = set(re.findall(r'\b(?:r|row)\["(\w+)"\]', src)) | set(re.findall(r'\brow\.get\("(\w+)"\)', src))
        used -= {"turn"}          # turn_at()'s `row` is a trace row, not a hand-off row
        self.assertTrue({"step", "bot", "pairing", "i", "seed", "held_file", "panel_file", "held_blob", "panel_blob", "old_moves", "new_moves",
                         "exact_counters", "offgate_counters"} <= used, used)
        self.write(SITTING2, [ROW])
        hf.convert(self.src, self.dst)
        header, _ = self.read()
        self.assertEqual(sorted(used - set(header)), [], "classify_8c.py reads a hand-off column the adapter's output lacks")

    def test_the_counters_go_through_the_classifiers_own_reading(self):
        self.write(SITTING2, [ROW, row2(i="3", reach2_counters="{}", offgate2_counters="{}")])
        hf.convert(self.src, self.dst)
        _, out = self.read()
        w = tr.watch_from_counters(json.loads(out[0]["exact_counters"]), REACH)        # what classify_8c.py's watch_of() does
        self.assertEqual(w["attack_return_weakness"], {"ticks": [67]})
        self.assertEqual(w["coin_queued_by_attack"], {"ticks": [93]})
        self.assertEqual(w["will_confused_attack"], {"ticks": []})
        self.assertEqual(tr.watch_from_counters(json.loads(out[1]["exact_counters"]), REACH)["coin_queued_by_attack"], {"ticks": []})
        has_offgate = lambda cell: any(bool(x) for x in json.loads(cell).values())     # classify_8c.py's has_offgate()
        self.assertTrue(has_offgate(out[0]["offgate_counters"]))
        self.assertFalse(has_offgate(out[1]["offgate_counters"]))

    def test_running_it_on_its_own_output_changes_nothing(self):
        self.write(SITTING2, [ROW, row2(i="3")])
        hf.convert(self.src, self.dst)
        again = self.tmp / "again.tsv"
        hf.convert(self.dst, again)
        self.assertEqual(again.read_bytes(), self.dst.read_bytes())

    def test_columns_in_another_order_and_a_file_with_no_rows(self):
        self.write(list(reversed(SITTING2)), [ROW])
        hf.convert(self.src, self.dst)
        header, out = self.read()
        self.assertEqual(header, [hf.RENAME.get(c, c) for c in reversed(SITTING2)])
        self.assertEqual(out[0]["exact_counters"], ROW["reach2_counters"])
        self.dst.unlink()
        self.write(SITTING2, [])
        hf.convert(self.src, self.dst)
        self.assertEqual(self.read()[1], [])

    def test_the_header_is_sitting2_checks_own(self):
        tree = ast.parse((HERE.parent / "sitting2_check.py").read_text(encoding="utf-8"))
        header = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "HEADER" for t in n.targets))
        self.assertEqual(tuple(header), hf.SITTING2)


class ClassifyShape(Case):
    def test_the_clouds_8b_shape_is_copied_unchanged(self):
        self.write(CLASSIFY, [ROW_8B, {**ROW_8B, "i": "3"}])
        before = self.src.read_bytes()
        self.assertEqual(hf.main(["--in", str(self.src), "--out", str(self.dst)], log=lambda *a, **k: None), 0)
        self.assertEqual(self.dst.read_bytes(), before)

    def test_its_counters_need_only_be_json_objects(self):
        # exact_counters also holds counters of other shapes (chase_order's numbers and names): not the tick lists the compact form has.
        self.write(CLASSIFY, [ROW_8B])
        hf.convert(self.src, self.dst)
        self.dst.unlink()
        self.write(CLASSIFY, [{**ROW_8B, "exact_counters": '["not", "an", "object"]'}])
        self.refused("not a JSON object")


class Refusals(Case):
    def test_an_unknown_column(self):
        self.write(SITTING2 + ["mystery"], [{**ROW, "mystery": "x"}])
        self.refused("unknown column mystery")
        self.write(CLASSIFY + ["mystery"], [{**ROW_8B, "mystery": "x"}])
        self.refused("unknown column mystery")

    def test_a_missing_column(self):
        header = [c for c in SITTING2 if c != "category"]
        self.write(header, [ROW])
        self.refused("without category")
        self.write([c for c in CLASSIFY if c != "seed"], [ROW_8B])
        self.refused("without seed")

    def test_the_old_and_new_names_together(self):
        self.write(SITTING2 + ["exact_counters"], [{**ROW, "exact_counters": "{}"}])
        self.refused("none of the three shapes")
        self.write(SITTING2 + ["exact_counters", "offgate_counters"], [{**ROW, "exact_counters": "{}", "offgate_counters": "{}"}])
        self.refused("both the sitting-2 names")

    def test_a_column_twice(self):
        self.write(SITTING2 + ["step"], [{**ROW}])
        self.refused("a column twice")

    def test_an_empty_file_a_missing_file_and_a_header_with_a_bom(self):
        self.src.write_text("", encoding="utf-8")
        self.refused("empty")
        self.src.unlink()
        self.refused()
        self.src.write_text("﻿" + "\t".join(SITTING2) + "\n", encoding="utf-8")
        self.refused("unknown column")

    def test_a_row_of_another_width(self):
        self.write(SITTING2, [ROW])
        self.src.write_text(self.src.read_text(encoding="utf-8") + "8\tkm3\t35\n", encoding="utf-8")
        self.refused("3 cells")

    def test_a_counter_cell_that_is_not_json_or_not_an_object(self):
        for bad, why in (("", "not JSON"), ("{1:2}", "not JSON"), ("[1,2]", "not a JSON object"), ("3", "not a JSON object")):
            self.write(SITTING2, [row2(reach2_counters=bad)])
            self.refused(why)
        self.write(SITTING2, [row2(offgate2_counters="nope")])
        self.refused("offgate2_counters")
        self.write(SITTING2, [row2(round1_counters="[]")])
        self.refused("round1_counters")
        self.write(SITTING2, [row2(superset_counters="")])
        self.refused("superset_counters")

    def test_a_counter_cell_of_the_wrong_compact_shape(self):
        for bad in ('{"attack_return_weakness":"67"}', '{"attack_return_weakness":[67,"x"]}', '{"attack_return_weakness":[true]}',
                    '{"coin_queued_by_attack":{"Wild Swing":93}}', '{"coin_queued_by_attack":{"Wild Swing":[1.5]}}', '{"x":5}'):
            self.write(SITTING2, [row2(reach2_counters=bad)])
            self.refused("not a list of ticks")

    def test_a_pairing_or_deal_that_is_not_a_number(self):
        self.write(SITTING2, [row2(pairing="x")])
        self.refused("pairing")
        self.write(SITTING2, [row2(i="")])
        self.refused("i is")

    def test_a_cell_beginning_with_a_double_quote(self):
        self.write(SITTING2, [row2(held_file='"decks/a.txt"')])
        self.refused("double quote")

    def test_the_output_is_never_over_an_existing_file_or_the_input(self):
        self.write(SITTING2, [ROW])
        self.dst.write_text("keep me", encoding="utf-8")
        with self.assertRaises(hf.Refuse):
            hf.convert(self.src, self.dst)
        self.assertEqual(self.dst.read_text(encoding="utf-8"), "keep me")
        with self.assertRaises(hf.Refuse) as cm:
            hf.convert(self.src, self.src)
        self.assertIn("--out is --in", str(cm.exception))
        self.assertEqual(self.src.read_text(encoding="utf-8").split("\n")[0], "\t".join(SITTING2))

    def test_the_second_of_two_rows_being_bad_writes_nothing_of_the_first(self):
        self.write(SITTING2, [ROW, row2(i="3", reach2_counters="nope")])
        self.refused("line 3")


if __name__ == "__main__":
    unittest.main()
