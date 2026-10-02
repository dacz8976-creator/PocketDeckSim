"""Classify the first differing decisions in the traced Altaria v Suicune deals (km diagnosis, Sept 30; diagnosis only).

Reads trace_rows.jsonl (km_diag_trace's output) and the committed records, all on table pairing 4's deals:
  kta3 on both sides   ../kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl
  km3 on Suicune only  ../km_tables_2026-09-30/1f6319e_mixed_table_km3_second.jsonl   (Altaria is first-named)
  km3 on Altaria only  ../km_tables_2026-09-30/1f6319e_mixed_table_km3_first.jsonl
  km3 on both sides    ../km_tables_2026-09-30/1f6319e_km3_table.jsonl
First it checks the trace against them: every replay's move fingerprint is kta3's committed one, and a seat has a first
differing decision exactly where the matching km3 record's moves differ from kta3's. Then it counts Suicune's first
differing decision (the one behind km3-on-Suicune's changed games) by kind, by the deal's result change, and by which of
the deciding side's two clocks N2 changes at that moment: "mine" (how soon the opponent wins: Altaria's attacker's
Stadium bonus against Suicune) or "theirs" (how soon Suicune wins: its own attacker's bonus). Prints the tables.
Usage: python3 classify.py"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE.parent


def load(f):
    return {r["i"]: r for r in map(json.loads, open(RES / f)) if r["a"] == "altaria" and r["b"] == "suicune"}


kta3 = load("kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl")
second = load("km_tables_2026-09-30/1f6319e_mixed_table_km3_second.jsonl")
first = load("km_tables_2026-09-30/1f6319e_mixed_table_km3_first.jsonl")
both = load("km_tables_2026-09-30/1f6319e_km3_table.jsonl")
rows = [json.loads(l) for l in open(HERE / "trace_rows.jsonl")]

# The checks against the records.
checks = Counter()
for r in rows:
    i = r["i"]
    checks["replay equals kta3's committed game"] += r["moves"] == kta3[i]["moves"] and r["seed"] == kta3[i]["seed"]
    checks["Suicune differs where km3-on-Suicune's record differs"] += (r["first_diff_suicune"] is not None) == (second[i]["moves"] != kta3[i]["moves"])
    checks["Altaria differs where km3-on-Altaria's record differs"] += (r["first_diff_altaria"] is not None) == (first[i]["moves"] != kta3[i]["moves"])
    either = r["first_diff_suicune"] is not None or r["first_diff_altaria"] is not None
    checks["a first difference where km3-on-both's record differs"] += either == (both[i]["moves"] != kta3[i]["moves"])
print(f"Checks, of {len(rows)} traced deals:")
for k, v in checks.items():
    print(f"  {k}: {v} of {len(rows)}")
assert all(v == len(rows) for v in checks.values()), "a check failed"


def move(a):
    """A short name for a move's kind."""
    if a.startswith("Play { trainer_card:"):
        name = re.sub(r"^Play \{ trainer_card: \S+ \S+ (.*) \}$", r"\1", a)
        return f"play {name}"
    for k, v in [("Attack(", "attack"), ("Retreat(", "retreat"), ("Promote", "promote"), ("Attach {", "attach Energy"),
                 ("Place(", "bench a Basic"), ("Evolve", "evolve"), ("UseAbility", "use an Ability"), ("EndTurn", "end turn"),
                 ("AttachTool", "attach a Tool")]:
        if a.startswith(k):
            return v
    return a.split(" ")[0].split("(")[0]


STADIUMS = ("Soothing Shore", "Training Area")


def kind(d):
    """The request's categories, from km3's move and kta3's."""
    km, kta = move(d["km3"]), move(d["kta3"])
    if any(km == f"play {s}" or kta == f"play {s}" for s in STADIUMS):
        return "Stadium play"
    if "play Field Blower" in (km, kta):
        return "Field Blower"
    if "attack" in (km, kta):
        return "attack choice"
    if {"retreat", "promote"} & {km, kta}:
        return "retreat or promotion"
    return "other"


def group(i):
    a, b = kta3[i]["first_deck_score"], second[i]["first_deck_score"]
    return "to Suicune" if b < a else "to Altaria" if b > a else "same result"


def clock_side(d):
    c = d["clocks"]
    mine, theirs = c["km"]["mine"] != c["kta"]["mine"], c["km"]["theirs"] != c["kta"]["theirs"]
    return "mine and theirs" if mine and theirs else "mine" if mine else "theirs" if theirs else "neither"


def blower_target(d):
    nxt = d.get("km3_next") or ""
    if "DiscardActiveStadium" in nxt:
        return "the Stadium"
    if "DiscardToolFromPokemon" in nxt:
        return "a Tool"
    return nxt or "?"


table = defaultdict(Counter)
detail = Counter()
sides, stadiums, pairs, targets = Counter(), Counter(), Counter(), Counter()
for r in rows:
    d = r["first_diff_suicune"]
    g, k = group(r["i"]), kind(d)
    table[k][g] += 1
    sides[clock_side(d)] += 1
    stadiums[str(d["stadium"])] += 1
    pairs[(move(d["kta3"]), move(d["km3"]))] += 1
    if k == "Field Blower":
        targets[blower_target(d)] += 1
groups = ["to Suicune", "to Altaria", "same result"]
print("\nSuicune's first differing decision (km3 on Suicune, kta3 on Altaria), by kind and by the deal's result change:")
print(f"  {'kind':22s} " + " ".join(f"{g:>12s}" for g in groups) + f" {'all':>6s}")
for k in ["Stadium play", "Field Blower", "attack choice", "retreat or promotion", "other"]:
    print(f"  {k:22s} " + " ".join(f"{table[k][g]:12d}" for g in groups) + f" {sum(table[k].values()):6d}")
print(f"  {'all':22s} " + " ".join(f"{sum(table[k][g] for k in table):12d}" for g in groups) + f" {len(rows):6d}")
print("\nkta3's move -> km3's move at that decision:")
for (a, b), n in pairs.most_common():
    print(f"  {n:3d}  {a} -> {b}")
print("\nField Blower's target (km3's next pick on a copy of the game):", dict(targets))
print("The Stadium in play at that decision:", dict(stadiums))
print("Which of Suicune's clocks N2 changes at that decision (km vs kta, from Suicune's view):", dict(sides))

# For context: the first difference with km3 on Altaria only, and with km3 on both (which seat moved first).
alt = Counter(kind(r["first_diff_altaria"]) for r in rows if r["first_diff_altaria"])
firstseat = Counter()
for r in rows:
    s, a = r["first_diff_suicune"], r["first_diff_altaria"]
    if s and a:
        firstseat["Suicune first" if s["tick"] < a["tick"] else "Altaria first"] += 1
    elif s:
        firstseat["Suicune only"] += 1
    elif a:
        firstseat["Altaria only"] += 1
print("\nContext, the same 40 deals:")
print("  Altaria's first differing decision (km3 on Altaria only), by kind:", dict(alt), f"({sum(alt.values())} deals)")
print("  km3 on both sides, which seat's decision comes first:", dict(firstseat))
