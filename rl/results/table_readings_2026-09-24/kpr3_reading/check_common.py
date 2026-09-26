"""Second reader's loaders for the kpr3 reading checks (Sept 26). Written from scratch; shares no code with
analysis.py / recompute.py. Only the Limitless W-L-T data are taken from deep_table.py (Sept 23) and the v2 JSON."""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))            # rl/results
sys.path.insert(0, os.path.join(RES, "deep_search_table"))
import deep_table as DT  # noqa: E402  (data only: NAMES, PAIRS, LIMITLESS)

NAMES = list(DT.NAMES)
PAIRS = list(DT.PAIRS)
QUAR = ("altaria", "sceptile")
SP = os.environ.get("KPR_SCRATCH", r"C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects"
                    r"\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\branch")

KP3 = [os.path.join(RES, "public_pricing_2026-09-25", f) for f in ("kp3_500_worst5.jsonl", "kp3_500_rest.jsonl")]
KPR3 = [os.path.join(SP, "kpr3_500.jsonl")]
K3 = [os.path.join(RES, "per_game_table_2026-09-25", "k3_500.jsonl")]
MIX1 = [os.path.join(RES, "kpr_mixed_rows_2026-09-26", "mixed_kpr3_first.jsonl")]
MIX2 = [os.path.join(RES, "kpr_mixed_rows_2026-09-26", "mixed_kpr3_second.jsonl")]
V2 = os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json")
V2E = os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev_events.json")


def load(paths, want_bots=None):
    """{(a, b): {i: record}}; checks every line's pairing/seed/seat against the table's deal rule."""
    out = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                k = (r["a"], r["b"])
                pi = PAIRS.index(k)
                assert r["pairing"] == pi, (p, r)
                assert r["seed"] == 72_000_000 + pi * 10_000 + r["i"], (p, r)
                assert r["first_seat"] == r["i"] % 2, (p, r)
                if want_bots:
                    assert (r["bot_a"], r["bot_b"]) == want_bots, (p, r["bot_a"], r["bot_b"])
                c = out.setdefault(k, {})
                assert r["i"] not in c, (p, k, r["i"])
                c[r["i"]] = r
    return out


def score(r):
    return float(r["first_deck_score"])


def lim_v2():
    d = json.load(open(V2, encoding="utf-8"))["cells"]
    return {tuple(k.split("|")): tuple(v) for k, v in d.items()}


def lim_s23():
    return {k: tuple(v) for k, v in DT.LIMITLESS.items()}


def events_v2():
    d = json.load(open(V2E, encoding="utf-8"))["events"]
    return [{tuple(k.split("|")): tuple(v) for k, v in e["cells"].items()} for e in d]


def frac(wlt):
    w, l, t = wlt
    n = w + l + t
    return (w + 0.5 * t) / n, n
