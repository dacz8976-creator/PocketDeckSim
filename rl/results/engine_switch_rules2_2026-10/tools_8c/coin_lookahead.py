"""Rules switch 2's copy of the first switch's `../engine_switch_rules_2026-10/coin_lookahead.py` (the cloud, Oct 9; switch-2 PLAN.md
precondition (b)): for each game a smoke run changes, is the change explained? One smoke directory, one pairing, as the original; the
hand-off's many pairings are classify_8c.py's (this folder). Changed only where switch 2 differs, as classify_8c.py's copy is:
  - the rule is this folder's tightened_rule.py (v3): a "length" difference is judged like any other board difference (`board_hits`);
    the original read it as UNEXPLAINED (its line 66);
  - the reach counters are round 2's exact names (`round2_reach` from --instrument, P2's attack_return_weakness among them), the keyed
    ones put together by `reach_row` (coin_queued_by_attack: the later round's eight attacks only), not repair B's three;
  - the probe is coin_probe v2 with round 2's conditions (`parse_probe`, `lookahead_verdict`: inside the search, only at its leaf, and
    the strict reading of a queued choice that may be a first-round site, both printed);
  - the golden check runs at the last explaining tick of each counter the probe has a condition for (`golden_ok`, with the keys that
    fired there: not for coin_queued_by_attack fired only for Double-Punching Family); S3's four hand-traced games were the first
    switch's (--s3, empty by default);
  - the negative controls require that the probe finds nothing at all (`control_clean` is `nothing_found`: no QUEUED, CUT or RETURN,
    none of round 2's kinds, no trapleaf; the laptop's spec for the 8c tools, Oct 10, item 2).
(Oct 10, Sonnet, for the laptop: this copy is in tools_8c/, beside the tightened_rule.py it imports, which is the pinned one with
`control_clean` changed to `nothing_found`; it differs from the copy on P's path only in that controls line, the --instrument
default's path (one folder further up) and this note. Run it from tools_8c/ or the pinned copy imports P's tightened_rule.py.)
"In lookahead" also needs the revert check (precondition (e)), which this script doesn't run.

  python3 coin_lookahead.py --dir SMOKE_DIR --a A.txt --b B.txt --seed-base N --probe PATH/coin_probe_v2 [--bot km3] [--pairing 0]
                            [--instrument PATH] [--s3 deal:tick,...]
SMOKE_DIR holds trace_old_*.jsonl.gz, trace_R.jsonl.gz (vs_trace.rs on the old engine and on the candidate) and watch_R.jsonl (the
watch build's legality_scan rows). --instrument is the watch build's coin script (default: ../../coin_prevention_repair_2026-09-30/
instrument_scan.py: this copy is in tools_8c/). The probe runs in the current directory."""
import argparse, glob, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from tightened_rule import (load_trace, first_difference, counter_hits, board_hits, round2_reach, reach_row, parse_probe,  # noqa: E402
                            nothing_found, control_clean, lookahead_verdict, golden_ok, ROUND2_QUEUED, R2_KINDS)

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True)
ap.add_argument("--a", required=True)
ap.add_argument("--b", required=True)
ap.add_argument("--seed-base", required=True)
ap.add_argument("--probe", required=True)
ap.add_argument("--bot", default="km3")
ap.add_argument("--pairing", default="0")
ap.add_argument("--instrument", default=str(HERE.parent.parent / "coin_prevention_repair_2026-09-30" / "instrument_scan.py"))
ap.add_argument("--s3", default="", help="golden: deal:first differing tick pairs traced by hand, with a queued choice on the table there")
a = ap.parse_args()
D = Path(a.dir)
REACH = round2_reach(Path(a.instrument).read_text(encoding="utf-8"))
RETRY_LIMIT = 600_000
EMPTY = {"queued": None, "cut": None, "free": False, "ret": None, "r2": {k: None for k in R2_KINDS}, "trapleaf": None}
# The cards that use the later coin round's eight attacks (classify_8b.py's list).
ROUND2_ATTACKERS = {"A4 045", "A4 215", "B2 048", "B3 051", "B1a 019", "B1a 020", "B1a 078", "B1a 084", "B4 077", "A4a 018",
                    "B2 127", "B2 189", "B2 202", "B4 231"}
LISTS_REACH_ROUND2 = any(re.search(rf"\b{re.escape(c)}\s*$", Path(p).read_text(encoding="utf-8"), re.M) for p in (a.a, a.b) for c in ROUND2_ATTACKERS)

old, old_done = load_trace(glob.glob(str(D / "trace_old_*.jsonl.gz"))[0])
new, new_done = load_trace(D / "trace_R.jsonl.gz")
raw = {r["i"]: r for r in map(json.loads, open(D / "watch_R.jsonl"))}
watch = {i: reach_row(r) for i, r in raw.items()}
changed = [i for i in sorted(old_done) if old_done[i]["moves"] != new_done[i]["moves"]]
print(f"{len(changed)} changed games of {len(old_done)}: {changed}")
print(f"reach counters: {', '.join(REACH)}")


def probe(deal, tick, limit=None):
    p = subprocess.run([a.probe, "--a", a.a, "--b", a.b, "--seed-base", a.seed_base, "--pairing", a.pairing, "--bot", a.bot,
                        "--deal", str(deal), "--tick", str(tick)] + (["--node-limit", str(limit)] if limit else []),
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"coin_probe_v2 failed for deal {deal} tick {tick}: {p.stderr[-300:]}")
    c = parse_probe(p.stdout)
    if c.get("truncated") and limit is None and nothing_found(c):
        return probe(deal, tick, RETRY_LIMIT) | {"retried": RETRY_LIMIT}
    return c


def fired_keys(i, name, tick):
    v = raw[i].get(name)
    if not isinstance(v, dict) or "ticks" in v:
        return ()
    return tuple(sorted(k for k, ticks in v.items() if tick in ticks and (name != "coin_queued_by_attack" or k in ROUND2_QUEUED)))


def show(c):
    r2 = " ".join(f"{k}={v}" for k, v in c["r2"].items() if v is not None)
    return (f"queued {c['queued']}{' (a pure frame)' if c['free'] else ''}, cut {c['cut']}, ret {c['ret']}"
            + (f", round 2: {r2}" if r2 else "") + (f", trapleaf {c['trapleaf']}" if c["trapleaf"] is not None else "")
            + (f", the queued path names {c['queued_attacks']}" if c.get("queued_attacks") else "")
            + (f" (retried at {c['retried']} nodes)" if c.get("retried") else ""))


verdicts, stricts, golden, kinds = {}, {}, {}, {}
bad = 0
for i in changed:
    x, y = old[i], new[i]
    d = first_difference(x, y)
    kinds[i] = d["kind"] + (f" ({d.get('longer') or 'as long'})" if d["kind"] == "length" else "")
    k, cause = d["k"], d["cause"]
    hits = board_hits(watch[i], REACH, y, d)
    literal = counter_hits(watch[i], REACH, y, d, literal=True)
    later = counter_hits(watch[i], REACH, y, d, after=True)
    turn = (y[k] if k < len(y) else d.get("x") or d.get("y") or y[-1])["turn"]
    counters = f"counters at or before tick {k} in its turn, at the cause tick or at the new game's first extra tick: {hits or 'none'}" \
        + ("" if literal == hits else f" (only the first clause: {literal or 'none'})") \
        + (f"; same turn after tick {k}: {later}" if later else "")
    head = f"i = {i:2d}: first difference at tick {k:3d} (turn {turn}; {kinds[i]}: {d['detail']}; cause tick {cause}); {counters}"
    golden[i] = (k, None)
    if hits:
        verdict = strict = "ON THE BOARD"
        gold = []
        for tick in sorted({max(t) for n, t in hits.items() if golden_ok(n, EMPTY) is not None}):
            c = probe(i, tick)
            names = [n for n, t in hits.items() if max(t) == tick and golden_ok(n, EMPTY) is not None]
            ok = all(golden_ok(n, c, fired_keys(i, n, tick)) is not False for n in names)
            bad += not ok
            gold.append(f"golden probe at tick {tick} for {names}: {show(c)} ({'on the table' if ok else 'NOT ON THE TABLE'})")
            golden[i] = (k, c)
        print(f"{head}; {'; '.join(gold) or 'no golden check (no counter the probe has a condition for)'} => {verdict}")
    elif d["kind"] == "lookahead":
        c = probe(i, k)
        named = set(c.get("queued_attacks", []))
        verdict, strict = lookahead_verdict(c, bool(named & ROUND2_QUEUED) if named else LISTS_REACH_ROUND2)
        print(f"{head}; probe at tick {k}: {show(c)} => {verdict}" + ("" if strict == verdict else f" (STRICT: {strict})"))
        golden[i] = (k, c)
    else:
        verdict = strict = "UNEXPLAINED"
        print(f"{head} => {verdict}")
    verdicts[i], stricts[i] = verdict, strict

if a.s3:
    print("\nS3's games (the first difference must be at the traced tick, with the queued coin-path choice on the table there):")
    for pair in a.s3.split(","):
        i, tick = map(int, pair.split(":"))
        k, c = golden.get(i, (None, None))
        ok = k == tick and c is not None and c["queued"] == 0 and verdicts.get(i) == "ON THE BOARD"
        bad += not ok
        print(f"  i = {i}: traced tick {tick}; first difference here {k}; verdict {verdicts.get(i)}  ({'match' if ok else 'DIFFERENT'})")

print("\nnegative control (unchanged games, a mid-game tick with no Meowth in play on either side: no queued choice, cut or return ply):")
controls = []
for i in sorted(set(old) - set(changed)):
    for t, r in enumerate(old[i][:60]):
        if t >= 8 and r["n"] > 1 and "Meowth" not in json.dumps(r["board"]):
            controls.append((i, t))
            break
    if len(controls) == 3:
        break
for i, t in controls:
    c = probe(i, t)
    ok = control_clean(c)
    bad += not ok
    print(f"  i = {i}, tick {t}: {show(c)}  ({'clean, as it must be' if ok else 'FOUND SOMETHING'})")

tally, strict_tally = {}, {}
for i in verdicts:
    tally[verdicts[i]] = tally.get(verdicts[i], 0) + 1
    strict_tally[stricts[i]] = strict_tally.get(stricts[i], 0) + 1
print(f"\nkinds of first difference: { {k_: [i for i in kinds if kinds[i] == k_] for k_ in sorted(set(kinds.values()))} }")
print("verdicts:", json.dumps(tally), "; under the strict reading:", json.dumps(strict_tally))
print("games by verdict:", json.dumps({v: [i for i in verdicts if verdicts[i] == v] for v in tally}))
unexplained = [i for i in verdicts if "UNEXPLAINED" in (verdicts[i], stricts[i])]
judgment = [i for i in verdicts if "NEEDS A JUDGMENT" in (verdicts[i], stricts[i])]
print(f"unexplained (the strict reading included): {unexplained or 'none'}; needing a judgment: {judgment or 'none'}; "
      f"golden and control mismatches: {bad}")
sys.exit(1 if unexplained or bad else 0)
