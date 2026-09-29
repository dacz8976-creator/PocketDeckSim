"""Shared loader for the power analysis. Read-only on the repo. Mirrors score45.py's setup exactly:
45 cells = scoreboard v2's 28 development cells + the gauntlet's 17 development cells; Limitless W-L-T per cell;
per-event cells from limitless_45_dev_events.json; per-deal game files loaded with score.py's own load_games.
Run with python3 -B (no bytecode written in the repo)."""
import csv, json, math, os, random, sys
sys.dont_write_bytecode = True
REPO = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
RES = REPO + "/rl/results"
sys.path.insert(0, RES + "/table_readings_2026-09-24")
import score as S  # noqa: E402  (score.py; imports deep_table as S.D)
D = S.D

NEW = ["rayquaza", "altaria_greninja"]
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]


def load_limitless():
    cells = json.load(open(RES + "/scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]
    assert len(cells) == 28
    new17 = [(d, o) for d in NEW for o in PANEL] + [("rayquaza", "altaria_greninja")]
    with open(RES + "/gauntlet_runs_2026-09-26/gauntlet_cells.csv", encoding="utf-8", newline="") as f:
        rows = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(f)}
    for a, b in new17:
        r = rows[("development", a, b)]
        cells[f"{a}|{b}"] = [int(r["W"]), int(r["L"]), int(r["T"])]
    pairs = list(D.PAIRS) + new17
    lim = {tuple(k.split("|")): tuple(v) for k, v in cells.items()}
    assert set(lim) == set(pairs) and len(pairs) == 45
    return pairs, lim


def load_events(pairs, lim):
    ev = json.load(open(RES + "/scoreboard_v3_2026-09-27/limitless_45_dev_events.json", encoding="utf-8"))["events"]
    events = [{tuple(k.split("|")): tuple(v) for k, v in e["cells"].items()} for e in ev]
    for k in pairs:
        tot = tuple(sum(e.get(k, (0, 0, 0))[j] for e in events) for j in range(3))
        assert tot == tuple(lim[k]), (k, tot, lim[k])
    return events


def load_reading(old_paths, new_paths, pairs):
    """Per cell: sorted list of (o, n) per-deal score pairs (first deck's score, 0/0.5/1) on common deals."""
    Ogr, Ngr = S.load_games(old_paths), S.load_games(new_paths)
    out = {}
    for k in pairs:
        common = sorted(set(Ogr[k]) & set(Ngr[k]))
        for i in common:
            assert S.same_deal(Ogr[k][i], Ngr[k][i]), (k, i)
        out[k] = [(Ogr[k][i]["s"], Ngr[k][i]["s"]) for i in common]
    return out


def cell_stats(pairs, lim, deals):
    """Numbers per cell (rates as fractions)."""
    O, N, L, nL, n = {}, {}, {}, {}, {}
    for k in pairs:
        d = deals[k]
        n[k] = len(d)
        O[k] = sum(o for o, _ in d) / n[k]
        N[k] = sum(x for _, x in d) / n[k]
        w, l, t = lim[k]
        nL[k] = w + l + t
        L[k] = (w + 0.5 * t) / nL[k]
    return O, N, L, nL, n


def dmse_point(pairs, O, N, L):
    return sum((N[k] - L[k]) ** 2 - (O[k] - L[k]) ** 2 for k in pairs) / len(pairs) * 1e4


# reading registry: label -> (old paths, new paths, current-pilot name, new-pilot name, printed score45 numbers)
KPF = RES + "/kpf_2026-09-26/reading/"
KOG = RES + "/kog_composition_2026-09-27/"
KOHC = "/tmp/koh_cloud/"


def readings():
    return {
        "koh3_vs_kog3": ([KOG + "table_kog3.jsonl", KOG + "new17_kog3.jsonl"], [KOHC + "table_koh3.jsonl", KOHC + "new17_koh3.jsonl"], "kog3", "koh3"),
        "kog3_vs_kp3": ([KPF + "table_kp3.jsonl", KPF + "new17_kp3.jsonl"], [KOG + "table_kog3.jsonl", KOG + "new17_kog3.jsonl"], "kp3", "kog3"),
        "kpf3_vs_kp3": ([KPF + "table_kp3.jsonl", KPF + "new17_kp3.jsonl"], [KPF + "table_kpf3.jsonl", KPF + "new17_kpf3.jsonl"], "kp3", "kpf3"),
        "kpr3_vs_kp3": ([KPF + "table_kp3.jsonl", KPF + "new17_kp3.jsonl"], [KPF + "table_kpr3.jsonl", KPF + "new17_kpr3.jsonl"], "kp3", "kpr3"),
        "kpg3_vs_kp3": ([KPF + "table_kp3.jsonl", KPF + "new17_kp3.jsonl"], [KPF + "table_kpg3.jsonl", KPF + "new17_kpg3.jsonl"], "kp3", "kpg3"),
        "kog3_vs_kpg3": ([KPF + "table_kpg3.jsonl", KPF + "new17_kpg3.jsonl"], [KOG + "table_kog3.jsonl", KOG + "new17_kog3.jsonl"], "kpg3", "kog3"),
    }
