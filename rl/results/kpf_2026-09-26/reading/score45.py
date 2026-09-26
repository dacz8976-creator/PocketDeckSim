"""score.py on the 45-cell scoreboard, with score.py's logic untouched.
- The 28 table cells: scoreboard v2's development cells (../../scoreboard_v2_2026-09-25/limitless_v2_dev.json).
- The 17 new cells: the gauntlet's development-half cells (../../gauntlet_runs_2026-09-26/gauntlet_cells.csv,
  dataset "development"; Rayquaza and Altaria/Greninja against the 8 and against each other).
This wrapper only widens deep_table's PAIRS from the 28 to the 45 cells, and hands score.py a 45-cell --limitless file.
Every rule, bootstrap, veto and quarantine is score.py's own.
Usage: python3 score45.py --rules v2 --old-games <table_kp3> <new17_kp3> --new-games <table_kpf3> <new17_kpf3> --old kp3 --new kpf3 [--mixed ...]"""
import csv, json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "..")
sys.path.insert(0, os.path.join(RES, "table_readings_2026-09-24"))
import score as S  # noqa: E402  (imports deep_table as S.D)

NEW = ["rayquaza", "altaria_greninja"]
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
cells = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
assert len(cells) == 28, len(cells)
new17 = [(d, o) for d in NEW for o in PANEL] + [("rayquaza", "altaria_greninja")]
with open(os.path.join(RES, "gauntlet_runs_2026-09-26", "gauntlet_cells.csv"), encoding="utf-8", newline="") as f:
    rows = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(f)}
for a, b in new17:
    r = rows[("development", a, b)]
    assert int(r["n"]) > 0, (a, b)
    cells[f"{a}|{b}"] = [int(r["W"]), int(r["L"]), int(r["T"])]
S.D.PAIRS[:] = list(S.D.PAIRS) + new17
tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
json.dump({"cells": cells, "note": "45 cells: scoreboard v2 dev (28) + gauntlet dev (17)"}, tmp)
tmp.close()
sys.argv = [sys.argv[0], "--limitless", tmp.name] + sys.argv[1:]
print(f"45-cell scoreboard: {len(S.D.PAIRS)} pairs; Limitless development half (v2's 28 + the gauntlet's 17)")
try:
    S.main()
finally:
    os.unlink(tmp.name)
