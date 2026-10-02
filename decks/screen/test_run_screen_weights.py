#!/usr/bin/env python3
"""run_screen.py --weights (Sept 30): the ladder-weighted readout is off by default, and when it is off nothing changes.

run_screen.py plays games on the manifest's engine, which current_engine.resolve() insists on by hash. These tests therefore
copy the script into a scratch tree with a stand-in current_engine.py and a stand-in engine/deckgym whose results are a fixed
function of its arguments. No real engine runs and no game is played; the stand-in prints the three lines the script parses
("Player 0 won", "Player 1 won", "Draws") and logs the arguments it was given.

GOLDEN_OFF and GOLDEN_CALLS are what the script printed, and the engine calls it made, on that same scratch tree BEFORE the
option was added (decks/screen/run_screen.py at 654d139). The test holds today's script, run without --weights, to them byte
for byte; `python3 test_run_screen_weights.py --golden OLD_RUN_SCREEN.py` regenerates them from an unmodified copy.

    python3 -B -m unittest -v test_run_screen_weights          (Linux: WSL or the cloud; from decks/screen)
"""
import csv, os, re, shutil, stat, subprocess, sys, tempfile, unittest
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(HERE, "run_screen.py")
WEIGHTS = os.path.join(HERE, "panel_ladder_2026-09-26", "panel_weights.csv")
EIGHT = ("t-altaria", "t-blaziken", "t-hydreigon", "t-lucario", "t-sceptile", "t-suicune", "t-vespiquen", "t-weezing")
OFF_PANEL = ("g-dragonair_mega_rayquaza", "h-charizardy_entei", "l-sharpedo")
ELEVEN = EIGHT + OFF_PANEL
ARGS = ["decks/alpha.txt", "decks/beta.txt", "--games", "9", "--seed", "123"]          # 2 decks, an odd game count
ADDED = ("   ladder-weighted:", "   not played, no cells:", "   played but not weighted, left out:",
         "   not a ranking: the ranking hold stands")
linux_only = unittest.skipUnless(sys.platform.startswith("linux"), "needs Linux (the stand-in engine is an executable script)")

# Filled by `--golden` from the script as it was before --weights existed.
GOLDEN_OFF = (
    '\n'
    '== alpha: 29/72 = 40% vs the panel  (km3 on the deck, km3 on the panel, 9 games per matchup; engine engine/deckgym)\n'
    '   t-lucario        1-8     11%\n'
    '   t-altaria        2-6   (1 draws)   22%\n'
    '   t-sceptile       3-5   (1 draws)   33%\n'
    '   t-hydreigon      4-4   (1 draws)   44%\n'
    '   t-vespiquen      4-4   (1 draws)   44%\n'
    '   t-weezing        4-5     44%\n'
    '   t-suicune        5-3   (1 draws)   56%\n'
    '   t-blaziken       6-3     67%\n'
    '\n'
    '== beta: 33/72 = 46% vs the panel  (km3 on the deck, km3 on the panel, 9 games per matchup; engine engine/deckgym)\n'
    '   t-weezing        2-6   (1 draws)   22%\n'
    '   t-altaria        3-6     33%\n'
    '   t-suicune        3-4   (2 draws)   33%\n'
    '   t-vespiquen      4-5     44%\n'
    '   t-blaziken       5-4     56%\n'
    '   t-lucario        5-4     56%\n'
    '   t-sceptile       5-3   (1 draws)   56%\n'
    '   t-hydreigon      6-3     67%\n'
)
GOLDEN_CALLS = [
    'simulate --num 4 --players km3,km3 --seed 123 --seed-stream -p alpha.txt t-altaria.txt',
    'simulate --num 5 --players km3,km3 --seed 623 --seed-stream -p t-altaria.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 1123 --seed-stream -p alpha.txt t-blaziken.txt',
    'simulate --num 5 --players km3,km3 --seed 1623 --seed-stream -p t-blaziken.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 2123 --seed-stream -p alpha.txt t-hydreigon.txt',
    'simulate --num 5 --players km3,km3 --seed 2623 --seed-stream -p t-hydreigon.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 3123 --seed-stream -p alpha.txt t-lucario.txt',
    'simulate --num 5 --players km3,km3 --seed 3623 --seed-stream -p t-lucario.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 4123 --seed-stream -p alpha.txt t-sceptile.txt',
    'simulate --num 5 --players km3,km3 --seed 4623 --seed-stream -p t-sceptile.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 5123 --seed-stream -p alpha.txt t-suicune.txt',
    'simulate --num 5 --players km3,km3 --seed 5623 --seed-stream -p t-suicune.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 6123 --seed-stream -p alpha.txt t-vespiquen.txt',
    'simulate --num 5 --players km3,km3 --seed 6623 --seed-stream -p t-vespiquen.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 7123 --seed-stream -p alpha.txt t-weezing.txt',
    'simulate --num 5 --players km3,km3 --seed 7623 --seed-stream -p t-weezing.txt alpha.txt',
    'simulate --num 4 --players km3,km3 --seed 123 --seed-stream -p beta.txt t-altaria.txt',
    'simulate --num 5 --players km3,km3 --seed 623 --seed-stream -p t-altaria.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 1123 --seed-stream -p beta.txt t-blaziken.txt',
    'simulate --num 5 --players km3,km3 --seed 1623 --seed-stream -p t-blaziken.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 2123 --seed-stream -p beta.txt t-hydreigon.txt',
    'simulate --num 5 --players km3,km3 --seed 2623 --seed-stream -p t-hydreigon.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 3123 --seed-stream -p beta.txt t-lucario.txt',
    'simulate --num 5 --players km3,km3 --seed 3623 --seed-stream -p t-lucario.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 4123 --seed-stream -p beta.txt t-sceptile.txt',
    'simulate --num 5 --players km3,km3 --seed 4623 --seed-stream -p t-sceptile.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 5123 --seed-stream -p beta.txt t-suicune.txt',
    'simulate --num 5 --players km3,km3 --seed 5623 --seed-stream -p t-suicune.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 6123 --seed-stream -p beta.txt t-vespiquen.txt',
    'simulate --num 5 --players km3,km3 --seed 6623 --seed-stream -p t-vespiquen.txt beta.txt',
    'simulate --num 4 --players km3,km3 --seed 7123 --seed-stream -p beta.txt t-weezing.txt',
    'simulate --num 5 --players km3,km3 --seed 7623 --seed-stream -p t-weezing.txt beta.txt',
]

STUB_RESOLVE = ("from pathlib import Path\n"
                "def resolve(project=None, override=None):\n"
                "    return Path(project) / 'engine' / 'deckgym'\n")
STUB_ENGINE = """#!{py}
import os, sys, zlib
a = sys.argv[1:]
num = int(a[a.index('--num') + 1]); seed = int(a[a.index('--seed') + 1]); players = a[a.index('--players') + 1]
i = a.index('-p'); a[i + 1], a[i + 2] = os.path.basename(a[i + 1]), os.path.basename(a[i + 2])
if os.environ.get('STUB_LOG'):
    with open(os.environ['STUB_LOG'], 'a') as f:
        f.write(' '.join(a) + '\\n')
h = zlib.crc32('|'.join([a[i + 1], a[i + 2], players, str(num), str(seed)]).encode())
w0 = h % (num + 1)
d = 1 if (h >> 8) % 3 == 0 and w0 < num else 0
print('Player 0 won: %d' % w0); print('Player 1 won: %d' % (num - w0 - d)); print('Draws: %d' % d)
"""


class Tree:
    """A scratch repo: decks/screen/run_screen.py (the script under test), the stand-in current_engine.py and engine/deckgym,
    eight panel lists in decks/screen/opponents/, and two decks to screen."""

    def __init__(self, tmp, script=SCRIPT):
        self.root = Path(tmp)
        screen = self.root / "decks" / "screen"
        (screen / "opponents").mkdir(parents=True)
        (self.root / "engine").mkdir()
        shutil.copy(script, screen / "run_screen.py")
        (self.root / "current_engine.py").write_text(STUB_RESOLVE)
        engine = self.root / "engine" / "deckgym"
        engine.write_text(STUB_ENGINE.format(py=sys.executable))
        engine.chmod(engine.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        for n in EIGHT:
            (screen / "opponents" / f"{n}.txt").write_text("Pokemon: stand-in\n")
        for n in ("alpha", "beta"):
            (self.root / "decks" / f"{n}.txt").write_text("Pokemon: stand-in\n")
        self.log = self.root / "engine_calls.log"

    def folder(self, names, where="readout_only"):
        d = self.root / where
        d.mkdir(exist_ok=True)
        for n in names:
            (d / f"{n}.txt").write_text("Pokemon: stand-in\n")
        return str(d)

    def weights_file(self, text, name="weights.csv", encoding="utf-8"):
        p = self.root / name
        p.write_bytes(text.encode(encoding))
        return str(p)

    def run(self, *args):
        """(completed process, the engine calls it made, one line each). Output is text, exactly as written."""
        if self.log.exists():
            self.log.unlink()
        env = dict(os.environ, STUB_LOG=str(self.log), PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run([sys.executable, "-B", "decks/screen/run_screen.py", *args], cwd=self.root, env=env,
                              capture_output=True, text=True)
        calls = self.log.read_text().splitlines() if self.log.exists() else []
        return proc, calls


def strip_added(text):
    return "".join(line for line in text.splitlines(keepends=True) if not line.startswith(ADDED))


def cell_wins(text):
    """{deck: {list: wins}} from the usual per-list rows of a run's output."""
    out, deck = {}, None
    for line in text.splitlines():
        m = re.match(r"== (\S+): ", line)
        if m:
            deck = out.setdefault(m.group(1), {})
            continue
        m = re.match(r"   (\S+)\s+(\d+)-\d+", line)
        if m and deck is not None and not line.startswith(ADDED):
            deck[m.group(1)] = int(m.group(2))
    return out


def read_table(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(line for line in f if not line.startswith("#")))


@linux_only
class RunWithStandInEngine(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tree = Tree(self._tmp.name)

    def test_without_the_option_the_output_and_the_engine_calls_are_what_they_were(self):
        proc, calls = self.tree.run(*ARGS)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(proc.stdout, GOLDEN_OFF)
        self.assertEqual(calls, GOLDEN_CALLS)
        self.assertTrue(GOLDEN_OFF.startswith("\n== alpha: ") and len(GOLDEN_CALLS) == 2 * 8 * 2, "golden is not filled in")

    def test_with_the_option_only_lines_are_added_and_the_same_games_are_played(self):
        proc, calls = self.tree.run(*ARGS, "--weights", WEIGHTS)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertNotEqual(proc.stdout, GOLDEN_OFF)
        self.assertEqual(strip_added(proc.stdout), GOLDEN_OFF)
        self.assertEqual(calls, GOLDEN_CALLS)

    def test_the_weighted_lines_sit_right_under_each_decks_usual_line(self):
        proc, _ = self.tree.run(*ARGS, "--weights", WEIGHTS)
        lines = proc.stdout.splitlines()
        heads = [i for i, l in enumerate(lines) if l.startswith("== ")]
        self.assertEqual(len(heads), 2)
        for i in heads:
            self.assertTrue(lines[i + 1].startswith("   ladder-weighted: "), lines[i + 1])

    def test_every_weighted_readout_says_it_is_not_a_ranking(self):
        proc, _ = self.tree.run(*ARGS, "--weights", WEIGHTS)
        self.assertEqual(proc.stdout.count("   not a ranking: the ranking hold stands\n"), 2)
        self.assertEqual(GOLDEN_OFF.count("not a ranking"), 0)

    def test_the_weighted_value_is_the_weights_times_the_win_rates_over_the_lists_played(self):
        weights = self.tree.weights_file("list,weight\nt-lucario,50\nt-altaria,30\nt-weezing,20\n")
        proc, _ = self.tree.run(*ARGS, "--weights", weights)
        wins = cell_wins(proc.stdout)
        self.assertEqual(set(wins), {"alpha", "beta"})
        for deck, w in wins.items():
            expect = (50 * w["t-lucario"] + 30 * w["t-altaria"] + 20 * w["t-weezing"]) / 9      # weights sum to 100
            self.assertIn(f"== {deck}: ", proc.stdout)
            block = proc.stdout.split(f"== {deck}: ")[1].split("\n\n")[0]
            self.assertIn(f"   ladder-weighted: {expect:.1f}%  (weights from weights.csv; 3 of 3 weighted lists played = "
                          f"100% of the three-list weights)", block)

    def test_the_committed_table_covers_68_percent_of_its_weights_and_says_how_little_of_the_ladder(self):
        proc, _ = self.tree.run(*ARGS, "--weights", WEIGHTS)
        self.assertEqual(proc.stdout.count(
            "8 of 11 weighted lists played = 68% of the eleven-list weights; those eleven lists cover about 42% of the "
            "saved ladder games, 23 of 55, README section 9)\n"), 2)
        self.assertNotIn("of the ladder weight", proc.stdout)
        self.assertEqual(proc.stdout.count("   not played, no cells: g-dragonair_mega_rayquaza, h-charizardy_entei, "
                                           "l-sharpedo\n"), 2)
        self.assertNotIn("played but not weighted", proc.stdout)

    def test_a_readout_only_folder_holding_all_eleven_gives_the_full_weight_line(self):
        folder = self.tree.folder(ELEVEN)
        proc, calls = self.tree.run(*ARGS, "--weights", WEIGHTS, "--opponents", folder)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(len(calls), 2 * 11 * 2)
        self.assertEqual(proc.stdout.count(
            "11 of 11 weighted lists played = 100% of the eleven-list weights; those eleven lists cover about 42% of the "
            "saved ladder games, 23 of 55, README section 9)\n"), 2)
        self.assertNotIn("not played", proc.stdout)
        self.assertEqual(sorted(cell_wins(proc.stdout)["alpha"]), sorted(ELEVEN))
        self.assertEqual(sorted(os.listdir(self.tree.root / "decks" / "screen" / "opponents")),
                         sorted(f"{n}.txt" for n in EIGHT), "the panel folder itself is untouched")

    def test_a_played_list_without_a_weight_is_named_and_left_out_of_the_value(self):
        weights = self.tree.weights_file("list,weight\nt-lucario,60\nt-altaria,40\n")
        proc, _ = self.tree.run(*ARGS, "--weights", weights)
        left_out = ", ".join(sorted(set(EIGHT) - {"t-lucario", "t-altaria"}))
        self.assertEqual(proc.stdout.count(f"   played but not weighted, left out: {left_out}\n"), 2)
        self.assertEqual(proc.stdout.count("2 of 2 weighted lists played = 100% of the two-list weights)"), 2)
        wins = cell_wins(proc.stdout)["alpha"]
        expect = (60 * wins["t-lucario"] + 40 * wins["t-altaria"]) / 9
        self.assertIn(f"   ladder-weighted: {expect:.1f}%  (", proc.stdout)

    def test_the_value_is_renormalised_over_the_weight_the_played_lists_carry(self):
        # Lucario, Altaria and Weezing are played and weighted (80 of the 100 points); Sharpedo is weighted but not played.
        weights = self.tree.weights_file("list,weight\nt-lucario,40\nt-altaria,30\nt-weezing,10\nl-sharpedo,20\n")
        proc, _ = self.tree.run(*ARGS, "--weights", weights)
        for deck, w in cell_wins(proc.stdout).items():
            expect = (40 * w["t-lucario"] + 30 * w["t-altaria"] + 10 * w["t-weezing"]) / 80 / 9 * 100
            block = proc.stdout.split(f"== {deck}: ")[1].split("\n\n")[0]
            self.assertIn(f"   ladder-weighted: {expect:.1f}%  (weights from weights.csv; 3 of 4 weighted lists played = "
                          f"80% of the four-list weights)\n   not played, no cells: l-sharpedo\n", block)

    def test_the_ladder_coverage_comes_from_the_table_itself(self):
        # 6 + 4 games on the two lists, 50 saved: the whole table covers 20% of the saved ladder games.
        weights = self.tree.weights_file("# logged_games: 50\nlist,weight,ladder_games\nt-lucario,60,6\nt-altaria,40,4\n")
        proc, _ = self.tree.run(*ARGS, "--weights", weights)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(proc.stdout.count("2 of 2 weighted lists played = 100% of the two-list weights; those two lists "
                                           "cover about 20% of the saved ladder games, 10 of 50, README section 9)\n"), 2)

    def test_no_coverage_sentence_unless_the_table_gives_both_numbers_and_they_make_sense(self):
        cases = {
            "no logged_games line": "list,weight,ladder_games\nt-lucario,60,6\nt-altaria,40,4\n",
            "no ladder_games column": "# logged_games: 50\nlist,weight\nt-lucario,60\nt-altaria,40\n",
            "logged_games 0": "# logged_games: 0\nlist,weight,ladder_games\nt-lucario,60,6\nt-altaria,40,4\n",
            "more games on the lists than saved": "# logged_games: 8\nlist,weight,ladder_games\nt-lucario,60,6\nt-altaria,40,4\n",
            "a ladder_games cell that is not a number": "# logged_games: 50\nlist,weight,ladder_games\nt-lucario,60,x\nt-altaria,40,4\n",
        }
        for what, text in cases.items():
            with self.subTest(what):
                proc, _ = self.tree.run(*ARGS, "--weights", self.tree.weights_file(text))
                self.assertEqual((proc.returncode, proc.stderr), (0, ""), what)
                self.assertEqual(proc.stdout.count("2 of 2 weighted lists played = 100% of the two-list weights)\n"), 2, what)
                self.assertNotIn("saved ladder games", proc.stdout)

    def test_the_committed_table_value_is_renormalised_over_the_68_percent_played(self):
        table = {r["list"]: float(r["weight"]) for r in read_table(WEIGHTS)}
        proc, _ = self.tree.run(*ARGS, "--weights", WEIGHTS)
        carried = sum(table[n] for n in EIGHT)
        self.assertAlmostEqual(carried, 68.0)
        for deck, w in cell_wins(proc.stdout).items():
            expect = sum(table[n] * w[n] for n in EIGHT) / carried / 9 * 100
            block = proc.stdout.split(f"== {deck}: ")[1].split("\n\n")[0]
            self.assertIn(f"   ladder-weighted: {expect:.1f}%  (", block)

    def test_extra_columns_comments_a_bom_and_windows_line_endings_are_fine(self):
        text = "# a comment\r\nlist,weight,note\r\nt-lucario,50,x\r\nt-altaria,50,y\r\n"
        weights = self.tree.weights_file(text, encoding="utf-8-sig")
        proc, _ = self.tree.run(*ARGS, "--weights", weights)
        self.assertEqual((proc.returncode, proc.stderr), (0, ""))
        self.assertEqual(proc.stdout.count("2 of 2 weighted lists played"), 2)

    def test_a_bad_weights_file_is_refused_before_any_game(self):
        bad = {
            "missing file": os.path.join(self._tmp.name, "nope.csv"),
            "no weight column": self.tree.weights_file("list,pct\nt-lucario,100\n", "a.csv"),
            "no rows": self.tree.weights_file("# only a comment\nlist,weight\n", "b.csv"),
            "empty file": self.tree.weights_file("", "c.csv"),
            "repeated list": self.tree.weights_file("list,weight\nt-lucario,50\nt-lucario,50\n", "d.csv"),
            "blank list": self.tree.weights_file("list,weight\n,50\nt-lucario,50\n", "e.csv"),
            "text weight": self.tree.weights_file("list,weight\nt-lucario,abc\nt-altaria,100\n", "f.csv"),
            "zero weight": self.tree.weights_file("list,weight\nt-lucario,0\nt-altaria,100\n", "g.csv"),
            "negative weight": self.tree.weights_file("list,weight\nt-lucario,-5\nt-altaria,105\n", "h.csv"),
            "nan weight": self.tree.weights_file("list,weight\nt-lucario,nan\nt-altaria,100\n", "i.csv"),
            "inf weight": self.tree.weights_file("list,weight\nt-lucario,inf\nt-altaria,100\n", "j.csv"),
            "missing weight cell": self.tree.weights_file("list,weight\nt-lucario\nt-altaria,100\n", "k.csv"),
            "total 90": self.tree.weights_file("list,weight\nt-lucario,50\nt-altaria,40\n", "l.csv"),
            "total 101": self.tree.weights_file("list,weight\nt-lucario,50\nt-altaria,51\n", "m.csv"),
            "no played list has a weight": self.tree.weights_file("list,weight\nt-nothing,50\nt-else,50\n", "n.csv"),
        }
        for what, path in bad.items():
            with self.subTest(what):
                proc, calls = self.tree.run(*ARGS, "--weights", path)
                self.assertEqual(proc.returncode, 1)
                self.assertIn("REFUSED", proc.stderr)
                self.assertEqual(proc.stdout, "")
                self.assertEqual(calls, [], "no game may be played before the weights are accepted")

    def test_a_total_within_half_a_point_of_100_is_accepted(self):
        for total in ("99.6", "100.4"):
            with self.subTest(total):
                weights = self.tree.weights_file(f"list,weight\nt-lucario,50\nt-altaria,{float(total) - 50}\n")
                proc, calls = self.tree.run(*ARGS, "--weights", weights)
                self.assertEqual((proc.returncode, proc.stderr), (0, ""))
                self.assertEqual(len(calls), 32)

    def test_help_names_the_option_and_says_it_is_off_by_default(self):
        proc, _ = self.tree.run("--help")
        self.assertEqual(proc.returncode, 0)
        text = " ".join(proc.stdout.split())                               # argparse wraps its help text
        self.assertIn("--weights FILE", text)
        self.assertIn("not a ranking", text)


class CommittedTable(unittest.TestCase):
    """panel_weights.csv is README section 9's eleven-list table, and it agrees with the repo it sits in."""

    def test_the_table_is_the_eleven_lists_and_totals_100(self):
        rows = read_table(WEIGHTS)
        self.assertEqual(sorted(r["list"] for r in rows), sorted(ELEVEN))
        self.assertEqual(sum(float(r["weight"]) for r in rows), 100.0)

    def test_each_weight_is_its_counted_games_out_of_the_total(self):
        rows = read_table(WEIGHTS)
        total = sum(int(r["counted_as"]) for r in rows)
        self.assertEqual(total, 25)                                      # 23 ladder games plus one floor game each: Sceptile, Weezing
        self.assertEqual(sum(int(r["ladder_games"]) for r in rows), 23)
        for r in rows:
            self.assertEqual(float(r["weight"]), round(100 * int(r["counted_as"]) / total, 1), r["list"])
        floored = {r["list"] for r in rows if int(r["ladder_games"]) == 0}
        self.assertEqual(floored, {"t-sceptile", "t-weezing"})           # P2: only the zero-game lists get the one-game floor
        for r in rows:
            if r["list"] not in floored:
                self.assertEqual(r["counted_as"], r["ladder_games"], r["list"])

    def test_the_eight_panel_lists_are_the_opponents_folder_and_every_file_exists(self):
        rows = read_table(WEIGHTS)
        opp_dir = os.path.join(HERE, "opponents")
        self.assertEqual(sorted(os.path.splitext(f)[0] for f in os.listdir(opp_dir) if f.endswith(".txt")), sorted(EIGHT))
        for r in rows:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, r["file"])), r["file"])
            self.assertEqual(os.path.splitext(os.path.basename(r["file"]))[0], r["list"])
            in_panel = r["file"].startswith("decks/screen/opponents/")
            self.assertEqual(in_panel, r["list"] in EIGHT, r["list"])
        files = {r["list"]: r["file"] for r in rows}
        self.assertEqual(files["h-charizardy_entei"], "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt")   # P5

    def test_the_file_says_what_it_is_and_what_it_is_not(self):
        with open(WEIGHTS, encoding="utf-8") as f:
            head = "".join(l for l in f if l.startswith("#"))
        for must in ("section 9", "run_screen.py --weights", "not a ranking: the ranking hold stands"):
            self.assertIn(must, head)

    def test_the_saved_ladder_total_is_named_and_the_coverage_rounds_to_42_percent(self):
        with open(WEIGHTS, encoding="utf-8") as f:
            logged = [int(m.group(1)) for m in (re.match(r"#\s*logged_games:\s*(\d+)\b", l) for l in f) if m]
        self.assertEqual(logged, [55])                                   # the Ladder Log's games at the Sept 28 night refresh
        on_lists = sum(int(r["ladder_games"]) for r in read_table(WEIGHTS))
        self.assertEqual((on_lists, round(100 * on_lists / logged[0])), (23, 42))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--golden":
        with tempfile.TemporaryDirectory() as tmp:
            proc, calls = Tree(tmp, script=sys.argv[2]).run(*ARGS)
            assert proc.returncode == 0 and proc.stderr == "", (proc.returncode, proc.stderr)
            print("GOLDEN_OFF = " + repr(proc.stdout))
            print("GOLDEN_CALLS = " + repr(calls))
    else:
        unittest.main(verbosity=2)
