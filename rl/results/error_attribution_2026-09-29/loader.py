"""Loader for the error-attribution job (Sept 29). Read-only on the repo; writes nothing.
Mirrors the eval-power loader (rl/results/eval_power_2026-09-29/analyst/common.py) for the 45 development cells,
and adds the other pilots' 45-cell tables, the variation check's game files and the frozen-half counts.
Run with python3 -B (no bytecode written)."""
import csv, json, math, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(RES, "table_readings_2026-09-24"))
import score as S  # noqa: E402  (score.py; imports deep_table as S.D)
D = S.D

NEW = ["rayquaza", "altaria_greninja"]
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
KPF = os.path.join(RES, "kpf_2026-09-26", "reading")
KOG = os.path.join(RES, "kog_composition_2026-09-27")
KT = os.path.join(RES, "kt_tables_2026-09-28")
KOHC = "/tmp/koh_cloud"   # koh3's tables (the cloud's copy, not in the repo); the per-cell rates are cached in cells.csv
GAUNT = os.path.join(RES, "gauntlet_runs_2026-09-26")

# pilot -> (table file, new-17 file)
PILOTS = {
    "k3":   (KPF + "/table_k3.jsonl",  KPF + "/new17_k3.jsonl"),
    "kp3":  (KPF + "/table_kp3.jsonl", KPF + "/new17_kp3.jsonl"),
    "kpf3": (KPF + "/table_kpf3.jsonl", KPF + "/new17_kpf3.jsonl"),
    "kpr3": (KPF + "/table_kpr3.jsonl", KPF + "/new17_kpr3.jsonl"),
    "kpg3": (KPF + "/table_kpg3.jsonl", KPF + "/new17_kpg3.jsonl"),
    "kog3": (KOG + "/table_kog3.jsonl", KOG + "/new17_kog3.jsonl"),
    "koh3": (KOHC + "/table_koh3.jsonl", KOHC + "/new17_koh3.jsonl"),
    "kt3":  (KT + "/ec7e1a8_kt3_table.jsonl", KT + "/ec7e1a8_kt3_new17.jsonl"),
    "kta3": (KT + "/ec7e1a8_kta3_table.jsonl", KT + "/ec7e1a8_kta3_new17.jsonl"),
    "ktb3": (KT + "/ec7e1a8_ktb3_table.jsonl", KT + "/ec7e1a8_ktb3_new17.jsonl"),
    "ktc3": (KT + "/ec7e1a8_ktc3_table.jsonl", KT + "/ec7e1a8_ktc3_new17.jsonl"),
}


def load_limitless():
    cells = json.load(open(RES + "/scoreboard_v2_2026-09-25/limitless_v2_dev.json", encoding="utf-8"))["cells"]
    new17 = [(d, o) for d in NEW for o in PANEL] + [("rayquaza", "altaria_greninja")]
    with open(GAUNT + "/gauntlet_cells.csv", encoding="utf-8", newline="") as f:
        rows = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(f)}
    for a, b in new17:
        r = rows[("development", a, b)]
        cells[f"{a}|{b}"] = [int(r["W"]), int(r["L"]), int(r["T"])]
    pairs = list(D.PAIRS) + new17
    lim = {tuple(k.split("|")): tuple(v) for k, v in cells.items()}
    assert set(lim) == set(pairs) and len(pairs) == 45
    return pairs, lim


def load_pilot(name, pairs):
    """{cell: [first-deck score per deal, in deal order i=0..499]} and the seeds, for the 45 cells."""
    g = S.load_games(list(PILOTS[name]))
    out, seeds = {}, {}
    for k in pairs:
        c = g[k]
        idx = sorted(c)
        assert idx == list(range(len(idx))) and len(idx) == 500, (name, k, len(idx))
        out[k] = [c[i]["s"] for i in idx]
        seeds[k] = [c[i].get("seed") for i in idx]
    return out, seeds


def load_frozen():
    """frozen_cells.csv: dev and pooled Limitless with n; returns {cell: dict}."""
    out = {}
    with open(RES + "/scoreboard_v3_2026-09-27/frozen_cells.csv", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            out[(r["a"], r["b"])] = dict(dev=float(r["limitless_dev"]) / 100, n_dev=int(r["n_dev"]),
                                          pooled=float(r["limitless_pooled"]) / 100, n_pooled=int(r["n_pooled"]),
                                          k3=float(r["k3"]), kp3=float(r["kp3"]))
    return out


def jl(path):
    """{(pairing, i): record} from a per-game file."""
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line:
            r = json.loads(line)
            out[(r["pairing"], r["i"])] = r
    return out
