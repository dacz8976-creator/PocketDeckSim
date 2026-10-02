"""Step 8c (the cloud): the summary of trace_8c.py's rows (rows/*.jsonl), rebuilt from whatever groups are done, so it
can be pushed as pairings finish. Writes, in this folder:
  results.tsv      one line per traced game: the first difference, the verdict, the counters and probes behind it;
  condition3.tsv   the CONDITION 3 games (handoff_8c.tsv's full_prevention_only = yes), one line each, with its probe;
  judgment.md      a short description of every NEEDS A JUDGMENT game, for Dustin;
  summary.txt      the totals: per step and bot, per pairing, CONDITION 3 by verdict, tool checks, the stops.
Usage: python3 summarize_8c.py [--expect 3813]"""
import argparse, gzip, json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--expect", type=int, default=3813)
a = ap.parse_args()
HERE = Path(__file__).resolve().parent
HELD = ("garchomp_meowth", "togekiss_meowth", "hisuian_goodra", "houndoom_victini")
PANEL = ("t-altaria", "t-blaziken", "t-hydreigon", "t-lucario", "t-sceptile", "t-suicune", "t-vespiquen", "t-weezing")  # pairs_8.tsv
B8 = {32: "fire_victini v psychic_confuse", 33: "fire_heatmor v meowth_carefree", 34: "t-vespiquen v meowth_carefree",
      35: "l-sharpedo v meowth_carefree"}
VERDICTS = ("ON THE BOARD", "LOOKAHEAD ONLY, both halves hold", "NEEDS A JUDGMENT", "UNEXPLAINED", "LENGTH", "UNTRACED",
            "PROBE ERROR")


def name(p):
    return B8[p] if p in B8 else f"{HELD[p // 8]} v {PANEL[p % 8]}"


games = []
for f in sorted((HERE / "rows").glob("*.jsonl")):
    games += [json.loads(l) for l in open(f, encoding="utf-8")]
fd = {}
for f in sorted((HERE / "firstdiff").glob("*.jsonl.gz")):
    for l in gzip.open(f, "rt"):
        r = json.loads(l)
        fd[(r["step"], r["bot"], r["pairing"], r["i"])] = r
games.sort(key=lambda g: (g["step"] != "8", g["pairing"], g["bot"] != "km3", g["i"]))


def pc(g):
    c = g.get("probe_coin")
    return "" if c is None else ("error" if "error" in c else f"queued={c['queued']} cut={c['cut']} free={str(c['free']).lower()}")


def pv(g):
    v = g.get("probe_vs")
    return "" if v is None else ("error" if "error" in v else f"built={v['built']}")


def cj(x):
    return json.dumps(x, separators=(",", ":"), sort_keys=True) if x else ""


cols = ("step", "bot", "pairing", "lists", "i", "seed", "verdict", "kind", "k", "turn", "cause", "counters_explaining",
        "counters_after", "probe_coin", "probe_vs", "golden_ok", "no_reach_counter", "condition3", "old_ticks", "new_ticks")
out = ["\t".join(cols)]
for g in games:
    gold = g.get("golden") or {}
    gok = "" if not gold else ("yes" if all(x["ok"] for x in gold.values()) else "NO")
    out.append("\t".join(str(x) for x in (g["step"], g["bot"], g["pairing"], name(g["pairing"]), g["i"], g["seed"],
                                           g["verdict"], g.get("kind", ""), g.get("k", ""), g.get("turn", ""),
                                           g.get("cause", ""), cj(g.get("counters_explaining")), cj(g.get("counters_after")),
                                           pc(g), pv(g), gok, g["no_reach_counter"], g["condition3"], g["old_ticks"],
                                           g["new_ticks"])))
(HERE / "results.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")

c3 = [g for g in games if g["condition3"] == "yes"]
c3cols = ("step", "bot", "pairing", "lists", "i", "seed", "verdict", "kind", "k", "turn", "probe_coin", "probe_vs",
          "counters_after", "coin_full_prevention_ticks")
lines = ["\t".join(c3cols)]
for g in c3:
    lines.append("\t".join(str(x) for x in (g["step"], g["bot"], g["pairing"], name(g["pairing"]), g["i"], g["seed"],
                                             g["verdict"], g.get("kind", ""), g.get("k", ""), g.get("turn", ""), pc(g), pv(g),
                                             cj(g.get("counters_after")),
                                             cj(g["exact_counters"].get("coin_full_prevention")))))
(HERE / "condition3.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def short(s, n=140):
    return s if len(s) <= n else s[:n - 3] + "..."


jm = ["# Step 8c: the games that need a judgment (Dustin's)", "",
      "Each is a lookahead difference (the same state and the same offered moves on both engines, a different choice) with no "
      "reach counter in its window, where vs_probe finds nothing and coin_probe finds repair B's queued coin-path choice only "
      "at the leaf: offered after 3 of the mover's moves, in a mixed frame (plain ApplyDamage choices beside it), which the bot "
      "never applies at ply 3. So the repaired code is in the tree only as an unpriced leaf; whether that counts as the "
      "mechanic acting is the judgment (coin_lookahead.py's NEEDS A JUDGMENT).", ""]
jg = [g for g in games if g["verdict"] == "NEEDS A JUDGMENT"]
for g in jg:
    r = fd.get((g["step"], g["bot"], g["pairing"], g["i"]))
    old_k = r["old"][-1] if r else None
    new_k = r["new"][-1] if r else None
    jm.append(f"- **{g['step']} {g['bot']}, pairing {g['pairing']} ({name(g['pairing'])}), deal {g['i']} (seed {g['seed']:,})"
              f"{', CONDITION 3' if g['condition3'] == 'yes' else ''}.** First difference at tick {g['k']} (turn {g['turn']}), "
              f"{old_k['n'] if old_k else '?'} moves offered. Old engine chose `{short(old_k['chosen']) if old_k else '?'}`; "
              f"R chose `{short(new_k['chosen']) if new_k else '?'}`. coin_probe: {pc(g)}; vs_probe: {pv(g)}. "
              f"Counters later in the turn (never an explanation): {cj(g.get('counters_after')) or 'none'}.")
if not jg:
    jm.append("None.")
(HERE / "judgment.md").write_text("\n".join(jm) + "\n", encoding="utf-8")

s = []
tally = lambda gs: {v: sum(1 for g in gs if g["verdict"] == v) for v in VERDICTS}
fmt = lambda t: ", ".join(f"{k} {n}" for k, n in t.items() if n)
s.append(f"Step 8c, the cloud's traces (trace_8c.py on the hand-off at main 1ba07d9): {len(games)} of {a.expect} changed games "
         f"traced{' (ALL)' if len(games) == a.expect else ' (partial: more groups to come)'}.")
s.append(f"verdicts, all traced games: {fmt(tally(games))}")
for step in ("8", "8b"):
    for bot in ("km3", "k3"):
        gs = [g for g in games if g["step"] == step and g["bot"] == bot]
        if gs:
            s.append(f"  step {step} {bot}: {len(gs)} games: {fmt(tally(gs))}")
s.append("")
s.append("per pairing (step, pairing, lists: games, verdicts):")
for key in sorted({(g["step"], g["pairing"]) for g in games}, key=lambda k: (k[0] != "8", k[1])):
    gs = [g for g in games if (g["step"], g["pairing"]) == key]
    s.append(f"  {key[0]} {key[1]:2d} {name(key[1])}: {len(gs)}: {fmt(tally(gs))}")
s.append("")
s.append(f"CONDITION 3 (handoff_8c.tsv's full_prevention_only = yes): {len(c3)} games traced: {fmt(tally(c3))}; "
         f"listed one by one in condition3.tsv")
nr = [g for g in games if g["no_reach_counter"] == "yes"]
s.append(f"no reach counter anywhere in the game: {len(nr)} games: {fmt(tally(nr))}")
kinds = {}
for g in games:
    kinds[g.get("kind", "-")] = kinds.get(g.get("kind", "-"), 0) + 1
s.append(f"kinds of first difference: {json.dumps(kinds, sort_keys=True)}")
s.append("")
gold = [g for g in games if g.get("golden")]
bad_gold = [g for g in gold if not all(x["ok"] for x in g["golden"].values())]
s.append(f"tool checks: every traced game's two fingerprints equal its row's: "
         f"{sum(1 for g in games if g['fingerprints']['old'] and g['fingerprints']['new'])} of {len(games)}; golden probes "
         f"run on {len(gold)} games explained on the board, gate on the table in {len(gold) - len(bad_gold)}"
         + (f"; NOT in: {[(g['step'], g['bot'], g['pairing'], g['i']) for g in bad_gold]}" if bad_gold else ""))
stops = [g for g in games if g["verdict"] in ("UNEXPLAINED", "LENGTH", "UNTRACED", "PROBE ERROR")]
s.append(f"STOPS (unexplained, length, untraced, probe error): {len(stops)}"
         + "".join(f"\n  {g['step']} {g['bot']} pairing {g['pairing']} ({name(g['pairing'])}) i {g['i']}: {g['verdict']}"
                   f" ({g.get('kind', '')} at tick {g.get('k', '')})" for g in stops))
s.append(f"needs a judgment: {len(jg)} (judgment.md)")
la = [g for g in games if g["verdict"] == "LOOKAHEAD ONLY, both halves hold"]
dist = {}
for g in la:
    c, v = g["probe_coin"], g["probe_vs"]
    parts = []
    if c["queued"] is not None:
        parts.append(f"queued after {c['queued']}" + (" (pure frame)" if c["free"] else ""))
    if c["cut"] is not None:
        parts.append(f"cut at ply {c['cut']}")
    if v["built"] is not None:
        parts.append(f"Confusion-first built after {v['built']}")
    key = "; ".join(parts)
    dist[key] = dist.get(key, 0) + 1
s.append(f"what the probes found in the {len(la)} lookahead games (moves of the mover's own before the gate):")
s += [f"  {n:4d}  {k}" for k, n in sorted(dist.items(), key=lambda x: -x[1])]
ctl = HERE / "controls.txt"
if ctl.exists():
    s.append("negative controls (controls_8c.py): " + ctl.read_text(encoding="utf-8").strip().splitlines()[-1])
(HERE / "summary.txt").write_text("\n".join(s) + "\n", encoding="utf-8")
print("\n".join(s))
