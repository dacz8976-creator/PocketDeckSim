"""Round-2 readiness, job 3 (the cloud, Oct 2): coin_probe v2 and tightened_rule v2, validated on the Oct 1 hand-off (main,
rl/results/engine_switch_rules_2026-10/handoff_8c.tsv): every one of its 3,813 changed games, as step 8c classified them
(`../engine_switch_rules_2026-10/trace_8c_cloud/`, on the cloud branch: rows/ with every game's first difference, counters and
probe results, and traces/ with both engines' full traces).

For every game, from the stored traces: the first difference again (tightened_rule v2), checked against step 8c's (the same kind
and tick); then the verdict again, by step 8c's rule with the two changes:
  - "length": ON THE BOARD when an exact counter fires at R's first extra tick (tightened_rule v2's extra_tick_hits);
  - "lookahead": coin_probe v2 at the first differing tick (run again here, on the official engine main-8626a35, whose engine is
    R's); vs_probe is unchanged, so its stored result is used.
  - ON THE BOARD by the counters is unchanged; coin_probe v2 also runs as the golden check at the last explaining coin tick (the
    gate must be on the table: queued 0 or cut 1).
And the 12 negative controls of step 8c (controls.txt's coin-probe deals and ticks): v2 must find nothing.
A probe that stops at v1's node limit (60,000) having found nothing is run again with RETRY_LIMIT nodes, and that run is used.
The bar (the coordinator, Oct 2): the 5 promotion games and km3 4/106 found by the probe, the 2 pairing-31 games on the board, and
the other 3,805 verdicts unchanged.
Usage: python3 validate_v2.py <trace_8c_cloud dir> <8c work dir: root/ and pairs_8.tsv> <coin_probe_v2 binary> <its engine dir>
Writes v2_verdicts.tsv and v2_summary.txt here."""
import gzip, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
C8, W, BIN, CWD = (Path(x) for x in sys.argv[1:5])
sys.path.insert(0, str(HERE))
from tightened_rule_v2 import load_trace, first_difference, counter_hits, extra_tick_hits  # noqa: E402

SEED_BASE = "23100000000"
SEARCH_PLIES = 3
REACH_A = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")
REACH_B = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
REACH = REACH_A + REACH_B
pairs = {}
for l in open(W / "pairs_8.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = l.split("\t")
    pairs[int(c[0])] = (c[3], c[5])


RETRY_LIMIT = 600_000


def probe(bot, pairing, deal, tick, limit=None):
    held, opp = pairs[pairing]
    p = subprocess.run([str(BIN), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base", SEED_BASE,
                        "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)]
                       + (["--node-limit", str(limit)] if limit else []),
                       cwd=CWD, capture_output=True, text=True)
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", p.stdout, re.M)
    if p.returncode != 0 or not m:
        return {"error": p.stderr[-300:]}
    parse = lambda s: None if s == "none" else int(s)
    path = re.search(r"^    after \[(.*)\] offers", p.stdout, re.M)
    return {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true", "truncated": "stopped at" in p.stdout,
            "path": path[1][:240] if path else ""} | ({"limit": limit} if limit else {})


def stopped_empty(r):
    return r.get("truncated") and r.get("queued") is None and r.get("cut") is None


def lookahead_verdict(c, v):
    coin_found = c["queued"] is not None or c["cut"] is not None
    leaf_only = coin_found and c["queued"] == SEARCH_PLIES and not c["free"] and (c["cut"] is None or c["cut"] > SEARCH_PLIES)
    if v["built"] is not None or (coin_found and not leaf_only):
        return "LOOKAHEAD ONLY, both halves hold"
    return "NEEDS A JUDGMENT" if leaf_only else "UNEXPLAINED"


games = []
for f in sorted((C8 / "rows").glob("*.jsonl")):
    games += [json.loads(l) for l in open(f, encoding="utf-8")]
games.sort(key=lambda g: (g["step"] != "8", g["pairing"], g["bot"] != "km3", g["i"]))
trace_cache = {}


def traces(g):
    key = (g["step"], g["bot"], g["pairing"])
    if key not in trace_cache:
        name = f"{g['step']}_{g['bot']}_{g['pairing']:02d}.jsonl.gz"
        trace_cache[key] = (load_trace(C8 / "traces" / f"trace_old_{name}")[0], load_trace(C8 / "traces" / f"trace_new_{name}")[0])
    old, new = trace_cache[key]
    return old[g["i"]], new[g["i"]]


plans, problems = [], []
for g in games:
    a, b = traces(g)
    d = first_difference(a, b)
    if d["kind"] != g["kind"] or d["k"] != g["k"]:
        problems.append(f"{g['step']} {g['bot']} {g['pairing']} {g['i']}: first difference {d['kind']} {d['k']} v 8c's {g['kind']} {g['k']}")
    watch = {n: {"ticks": g["exact_counters"].get(n, [])} for n in REACH}
    plan = {"g": g, "d": d, "rows": b}
    if d["kind"] == "length":
        plan["hits"] = extra_tick_hits(watch, REACH, d)
    else:
        strict = counter_hits(watch, REACH, b, d)
        plan["hits"] = strict
        if strict:
            b_ticks = [t for n in REACH_B for t in strict.get(n, [])]
            if b_ticks:
                plan["golden_tick"] = max(b_ticks)
        elif d["kind"] == "lookahead":
            plan["probe_tick"] = d["k"]
    plans.append(plan)

jobs = [(i, "golden", p["golden_tick"]) for i, p in enumerate(plans) if "golden_tick" in p] + \
       [(i, "probe", p["probe_tick"]) for i, p in enumerate(plans) if "probe_tick" in p]
controls = []
for l in (C8 / "controls.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"coin probe, (\w+), pairing (\d+), deal (\d+), tick (\d+)", l)
    if m:
        controls.append((m[1], int(m[2]), int(m[3]), int(m[4])))
with ThreadPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(lambda j: probe(plans[j[0]]["g"]["bot"], plans[j[0]]["g"]["pairing"], plans[j[0]]["g"]["i"], j[2]), jobs))
    control_results = list(pool.map(lambda c: probe(*c), controls))
    retry = [n for n, r in enumerate(results) if stopped_empty(r)]
    for n, r in zip(retry, pool.map(lambda n: probe(plans[jobs[n][0]]["g"]["bot"], plans[jobs[n][0]]["g"]["pairing"],
                                                     plans[jobs[n][0]]["g"]["i"], jobs[n][2], RETRY_LIMIT), retry)):
        results[n] = r
    retry_c = [n for n, r in enumerate(control_results) if stopped_empty(r)]
    for n, r in zip(retry_c, pool.map(lambda n: probe(*controls[n], RETRY_LIMIT), retry_c)):
        control_results[n] = r
for (i, kind, _), r in zip(jobs, results):
    plans[i][kind] = r

out = ["\t".join(("step", "bot", "pairing", "i", "kind", "k", "verdict_8c", "verdict_v2", "changed", "coin_v1", "coin_v2", "vs",
                  "counters", "v2_path"))]
tally, changes, golden_bad, coin_cmp = {}, [], [], {"same": 0, "smaller": 0, "larger": 0, "v2 only": 0, "v1 only": 0, "neither": 0}
for p in plans:
    g, d = p["g"], p["d"]
    if d["kind"] == "length":
        v2 = "ON THE BOARD" if p["hits"] else "UNEXPLAINED"
    elif p["hits"]:
        v2 = "ON THE BOARD"
        gold = p.get("golden")
        if gold is not None and ("error" in gold or not (gold["queued"] == 0 or gold["cut"] == 1)):
            golden_bad.append(f"{g['step']} {g['bot']} {g['pairing']} {g['i']} tick {p['golden_tick']}: {gold}")
    elif d["kind"] == "lookahead":
        c = p["probe"]
        if "error" in c:
            v2 = "PROBE ERROR"
            problems.append(f"{g['step']} {g['bot']} {g['pairing']} {g['i']}: {c['error']}")
        else:
            v2 = lookahead_verdict(c, g["probe_vs"])
            c1 = g["probe_coin"]
            l1 = min((x for x in (c1["queued"], c1["cut"]) if x is not None), default=None)
            l2 = min((x for x in (c["queued"], c["cut"]) if x is not None), default=None)
            coin_cmp["neither" if l1 is None and l2 is None else "v2 only" if l1 is None else "v1 only" if l2 is None
                     else "same" if l1 == l2 else "smaller" if l2 < l1 else "larger"] += 1
    else:
        v2 = "UNEXPLAINED"
    tally[v2] = tally.get(v2, 0) + 1
    changed = v2 != g["verdict"]
    if changed:
        changes.append(p)
    coin_v2 = p.get("probe", {})
    out.append("\t".join(str(x) for x in (g["step"], g["bot"], g["pairing"], g["i"], d["kind"], d["k"], g["verdict"], v2,
                                           "yes" if changed else "no",
                                           json.dumps(g.get("probe_coin"), sort_keys=True) if g.get("probe_coin") else "",
                                           json.dumps({k: v for k, v in coin_v2.items() if k != "path"}, sort_keys=True) if coin_v2 else "",
                                           json.dumps(g.get("probe_vs"), sort_keys=True) if g.get("probe_vs") else "",
                                           json.dumps(p["hits"], sort_keys=True), coin_v2.get("path", ""))))
(HERE / "v2_verdicts.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")

expected = {("8", "km3", 1, 399), ("8", "k3", 4, 7), ("8", "km3", 4, 7), ("8", "km3", 4, 360), ("8", "km3", 21, 310),
            ("8", "km3", 4, 106), ("8", "km3", 31, 12), ("8", "k3", 31, 81)}
got = {(p["g"]["step"], p["g"]["bot"], p["g"]["pairing"], p["g"]["i"]) for p in changes}
control_bad = [f"{c}: {r}" for c, r in zip(controls, control_results) if "error" in r or r["queued"] is not None or r["cut"] is not None]
truncated = sum(1 for p in plans if p.get("probe", {}).get("truncated"))
retried = [p for p in plans if p.get("probe", {}).get("limit")]
s = [f"games: {len(plans)}; first differences equal to step 8c's: {len(plans) - sum(1 for x in problems if 'first difference' in x)}",
     f"verdicts v2: {json.dumps(dict(sorted(tally.items())))}",
     f"verdicts 8c: {json.dumps(dict(sorted((v, sum(1 for p in plans if p['g']['verdict'] == v)) for v in {p['g']['verdict'] for p in plans})))}",
     f"changed verdicts: {len(changes)}; the expected 8 (the 5 promotion games, km3 4/106, the 2 pairing-31 games): "
     f"{'exactly these' if got == expected else 'DIFFERENT: ' + str(sorted(got ^ expected))}",
     f"unchanged verdicts: {len(plans) - len(changes)}"]
for p in changes:
    g = p["g"]
    s.append(f"  {g['step']} {g['bot']} pairing {g['pairing']} i {g['i']} ({p['d']['kind']} at {p['d']['k']}): {g['verdict']} -> "
             + ("ON THE BOARD" if p["d"]["kind"] == "length" or p["hits"] else lookahead_verdict(p['probe'], g['probe_vs']))
             + (f"; counters at the extra tick {p['hits']}" if p["d"]["kind"] == "length" else
                f"; coin v1 {g['probe_coin']}, v2 { {k: v for k, v in p['probe'].items() if k != 'path'} }; path [{p['probe'].get('path', '')[:200]}]"))
s += [f"coin probe v2 against v1 on the {sum(coin_cmp.values())} lookahead games (the smallest ply found): {coin_cmp}",
      f"lookahead probes that stopped at 60,000 nodes having found nothing, run again at {RETRY_LIMIT:,}: {len(retried)} "
      f"({sum(1 for p in retried if not stopped_empty(p['probe']))} found, {sum(1 for p in retried if stopped_empty(p['probe']))} "
      f"still stopped); controls run again: {len(retry_c)}",
      f"lookahead probes whose final run stopped at its node limit (anything found is still found): {truncated}",
      f"golden checks (v2 at the last explaining coin tick; the gate on the table): {sum(1 for p in plans if 'golden' in p) - len(golden_bad)} "
      f"of {sum(1 for p in plans if 'golden' in p)} on the table" + (f"; NOT: {golden_bad[:10]}" if golden_bad else ""),
      f"negative controls (step 8c's {len(controls)} coin-probe controls, unchanged deals): {len(controls) - len(control_bad)} found nothing"
      + (f"; FOUND: {control_bad}" if control_bad else ""),
      f"problems: {problems[:20] or 'none'}"]
(HERE / "v2_summary.txt").write_text("\n".join(s) + "\n", encoding="utf-8")
print("\n".join(s))
