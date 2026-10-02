"""PLAN.md step 8c, the second independent run (Sonnet, on the laptop's cores, beside the cloud's): every changed game of the hand-off
(`handoff_8c.tsv`) traced on the old engine and on R to its first differing tick and classified by `tightened_rule.py` (R's, unchanged),
exactly as the cloud's `early_warning_8b/classify_8b.py` did for 8b, generalised from 8b's four pairings to every pairing of step 8.

For each changed row (step, bot, pairing, i):
  1. vs_trace on the old engine and on R for that deal, with the row's own bot; each trace's move fingerprint must equal the row's
     old_moves / new_moves (a trace that does not reproduce its game explains nothing; any mismatch is a PROBLEM and is listed);
  2. first_difference(old trace, new trace) gives the kind (movegen / lookahead / state / length), the first differing tick k and the
     cause tick; counter_hits(row's exact counters, ...) says whether a reach counter fired at or before k in k's turn or at the cause tick;
  3. ON THE BOARD: such a counter fired. LOOKAHEAD ONLY, both halves: no such counter, a "lookahead" first difference, and a probe
     (vs_probe.rs for repair A, coin_probe.rs for repair B, both run on R at tick k with the row's bot) finds a repair's gate inside the
     bot's 3 plies. NEEDS A JUDGMENT: the coin probe finds the queued choice only at the leaf (ply 3, a mixed frame). UNEXPLAINED: anything
     else (a board difference or a prefix with no counter; a lookahead difference no probe explains). UNEXPLAINED stops the switch.
  4. Both probes are run on every lookahead-only game (the coordinator's instruction), as a golden check on the games explained on the
     board (the gate must be on the table at the last explaining tick; --no-golden skips it) and as a negative control at a mid-game tick
     of a few unchanged games (nothing may be found).
The reach counters are the hand-off's: A = vs_confusion_first_built, vs_confused_choice_offered, vs_confused_choice_chosen; B =
coin_cut_recorded, coin_queued_offered, coin_queued_offered_any. coin_full_prevention, vs_confused_choice and the superset counters never
explain a game. The CONDITION 3 rows (changed, coin_full_prevention fired, no reach counter) are listed one by one in condition3.tsv.

Usage: python3 classify_8c.py --work W --tsv handoff_8c.tsv --out OUT [--steps 8] [--jobs 12] [--limit N] [--no-golden]
       [--controls-from DIR_WITH_THE_SCAN_JSONL]
W holds root/ (decks, as the hand-off's paths name them), tools/ (tightened_rule.py), old/, new/, probe/ (engine copies the programs were
built in) and bin_old_vs_trace, bin_new_vs_trace, bin_new_vs_probe, bin_probe_coin_probe (run_8c.sh makes them). Only the first differing
rows and each game's turn list are kept in memory, never a whole trace."""
import argparse, collections, concurrent.futures as cf, csv, gzip, hashlib, json, re, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--tsv", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--steps", default="8")
ap.add_argument("--jobs", type=int, default=12)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--no-golden", action="store_true")
ap.add_argument("--controls-from", default=None)
ap.add_argument("--chunk", type=int, default=20, help="deals per vs_trace call")
a = ap.parse_args()
W, OUT = Path(a.work), Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
(W / "traces").mkdir(exist_ok=True)
sys.path.insert(0, str(W / "tools"))
from tightened_rule import load_trace, first_difference, counter_hits  # noqa: E402

SEED_BASE = "23100000000"
REACH_A = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")
REACH_B = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
REACH = REACH_A + REACH_B
SEARCH_PLIES = 3
NICE = ["nice", "-n", "19"]

rows = [r for r in csv.DictReader(open(a.tsv, encoding="utf-8"), delimiter="\t") if r["step"] in a.steps.split(",")]
for r in rows:
    r["pairing"], r["i"] = int(r["pairing"]), int(r["i"])
rows.sort(key=lambda r: (r["bot"], r["pairing"], r["i"]))
if a.limit:
    rows = rows[:a.limit]
by_key = {(r["bot"], r["pairing"], r["i"]): r for r in rows}
problems = []


def run(cmd, cwd):
    p = subprocess.run(NICE + cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"failed: {' '.join(cmd)[:200]}\n{p.stderr[-300:]}")
    return p.stdout


# ---- the deck files are the ones the hand-off's rows were played with (git blob ids) ----
def blob_id(path):
    if not path.exists():
        return "MISSING"
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


files = {}
for r in rows:
    files[r["held_file"]] = r["held_blob"]
    files[r["panel_file"]] = r["panel_blob"]
bad_blobs = [f for f, want in files.items() if blob_id(W / "root" / f) != want]
if bad_blobs:
    sys.exit(f"deck files differ from the hand-off's blobs: {bad_blobs}")


# ---- traces: old and R, per (bot, pairing, deck pair), in chunks, in parallel; each chunk is reduced to compact records at once ----
def trace_file(engine, bot, pairing, held, panel, deals):
    path = W / "traces" / f"{engine}_{bot}_{pairing}_{deals[0]}_{deals[-1]}.jsonl.gz"
    if not path.exists():
        out = run([str(W / f"bin_{engine}_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / panel), "--seed-base", SEED_BASE,
                   "--pairing", str(pairing), "--bot", bot, "--deals", ",".join(map(str, deals))], W / engine / "engine")
        tmp = path.with_suffix(".tmp")
        with gzip.open(tmp, "wt") as f:
            f.write(out)
        tmp.rename(path)
    return path


def analyse_chunk(bot, pairing, held, panel, deals):
    old_games, old_done = load_trace(trace_file("old", bot, pairing, held, panel, deals))
    new_games, new_done = load_trace(trace_file("new", bot, pairing, held, panel, deals))
    out = []
    for i in deals:
        d = first_difference(old_games[i], new_games[i])
        out.append({"key": (bot, pairing, i), "d": d, "turns": [x["turn"] for x in new_games[i]], "ticks": (len(old_games[i]), len(new_games[i])),
                    "old_moves": old_done[i]["moves"], "new_moves": new_done[i]["moves"]})
    return out


groups = collections.defaultdict(list)
for r in rows:
    groups[(r["bot"], r["pairing"], r["held_file"], r["panel_file"])].append(r["i"])
chunks = []
for (bot, pairing, held, panel), deals in groups.items():
    deals = sorted(deals)
    for s in range(0, len(deals), a.chunk):
        chunks.append((bot, pairing, held, panel, deals[s:s + a.chunk]))

print(f"{len(rows)} changed rows, {len(chunks)} chunks x 2 engines, {a.jobs} jobs", flush=True)
analysed = {}
with cf.ThreadPoolExecutor(a.jobs) as ex:
    futs = [ex.submit(analyse_chunk, *c) for c in chunks]
    for n, f in enumerate(cf.as_completed(futs), 1):
        for rec in f.result():
            analysed[rec["key"]] = rec
        if n % 10 == 0 or n == len(futs):
            print(f"  traced and compared {n}/{len(futs)} chunks", flush=True)


# ---- probes ----
def probe(kind, bot, pairing, held, panel, deal, tick):
    exe = W / ("bin_new_vs_probe" if kind == "vs" else "bin_probe_coin_probe")
    cwd = W / ("new" if kind == "vs" else "probe") / "engine"
    out = run([str(exe), "--a", str(W / "root" / held), "--b", str(W / "root" / panel), "--seed-base", SEED_BASE, "--pairing", str(pairing),
               "--bot", bot, "--deal", str(deal), "--tick", str(tick)], cwd)
    if kind == "vs":
        m = re.search(r"^RESULT built=(\S+)$", out, re.M)
        return {"built": None if m[1] == "none" else int(m[1])}
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", out, re.M)
    parse = lambda s: None if s == "none" else int(s)
    return {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true"}


def watch_of(row):
    ex = json.loads(row["exact_counters"] or "{}")
    return {n: {"ticks": ex.get(n, [])} for n in REACH + ("coin_full_prevention",)}


# ---- first differences and counters ----
recs = []
for r in rows:
    key = (r["bot"], r["pairing"], r["i"])
    an = analysed[key]
    fp_ok = an["old_moves"] == r["old_moves"] and an["new_moves"] == r["new_moves"]
    if not fp_ok:
        problems.append(f"{key}: a trace's move fingerprint differs from the hand-off row (old {an['old_moves']} v {r['old_moves']}, "
                        f"new {an['new_moves']} v {r['new_moves']})")
    d, w = an["d"], watch_of(r)
    turns = [{"turn": t} for t in an["turns"]]          # counter_hits reads rows[t]["turn"] only
    rec = {"row": r, "key": key, "fp_ok": fp_ok, "d": d, "turns": turns, "w": w, "probes": {}, "verdict": None, "note": ""}
    if d["kind"] == "length":
        rec["verdict"], rec["note"] = "UNEXPLAINED", d["detail"]
    else:
        rec["strict"] = counter_hits(w, REACH, turns, d)
        rec["later"] = counter_hits(w, REACH, turns, d, after=True)
        if rec["strict"]:
            rec["verdict"] = "ON THE BOARD"
        elif d["kind"] == "lookahead":
            rec["verdict"] = "?"            # decided after the probes
        else:
            rec["verdict"], rec["note"] = "UNEXPLAINED", f"{d['kind']}: {d['detail']}, no reach counter"
    recs.append(rec)

# ---- probe jobs: both probes on every lookahead game; golden probes on the games explained on the board ----
jobs = []
for rec in recs:
    d = rec["d"]
    if rec["verdict"] == "?":
        jobs += [(rec, "coin", d["k"]), (rec, "vs", d["k"])]
    elif rec["verdict"] == "ON THE BOARD" and not a.no_golden:
        b_ticks = [t for n in REACH_B for t in rec["strict"].get(n, [])]
        a_ticks = [t for t in rec["strict"].get("vs_confusion_first_built", []) if t <= d["cause"]]
        if b_ticks:
            jobs.append((rec, "coin_golden", max(b_ticks)))
        if a_ticks:
            jobs.append((rec, "vs_golden", max(a_ticks)))
print(f"{len(jobs)} probe runs", flush=True)


def do_probe(job):
    rec, kind, tick = job
    r = rec["row"]
    res = probe("coin" if kind.startswith("coin") else "vs", r["bot"], r["pairing"], r["held_file"], r["panel_file"], r["i"], tick)
    return rec, kind, tick, res


with cf.ThreadPoolExecutor(a.jobs) as ex:
    futs = [ex.submit(do_probe, j) for j in jobs]
    for n, f in enumerate(cf.as_completed(futs), 1):
        rec, kind, tick, res = f.result()
        rec["probes"][kind] = {"tick": tick, **res}
        if n % 100 == 0 or n == len(futs):
            print(f"  probed {n}/{len(futs)}", flush=True)

golden_bad = []
for rec in recs:
    p = rec["probes"]
    if rec["verdict"] == "?":
        c, v = p["coin"], p["vs"]
        coin_found = c["queued"] is not None or c["cut"] is not None
        leaf_only = coin_found and c["queued"] == SEARCH_PLIES and not c["free"] and (c["cut"] is None or c["cut"] > SEARCH_PLIES)
        if v["built"] is not None or (coin_found and not leaf_only):
            rec["verdict"] = "LOOKAHEAD ONLY, both halves hold"
        elif leaf_only:
            rec["verdict"] = "NEEDS A JUDGMENT"
        else:
            rec["verdict"], rec["note"] = "UNEXPLAINED", "a lookahead difference no probe explains"
    if "coin_golden" in p and not (p["coin_golden"]["queued"] == 0 or p["coin_golden"]["cut"] == 1):
        golden_bad.append((rec["key"], "coin", p["coin_golden"]))
    if "vs_golden" in p and p["vs_golden"]["built"] != 0:
        golden_bad.append((rec["key"], "vs", p["vs_golden"]))

# ---- negative controls: unchanged games, a mid-game tick, nothing may be found ----
controls = []
if a.controls_from:
    for bot in sorted({r["bot"] for r in rows}):
        old = {(g["pairing"], g["i"]): g for g in map(json.loads, open(Path(a.controls_from) / f"5a18d31_8_old_{bot}.jsonl"))}
        new = {(g["pairing"], g["i"]): g for g in map(json.loads, open(Path(a.controls_from) / f"5a18d31_8_new_{bot}.jsonl"))}
        pair_files = {r["pairing"]: (r["held_file"], r["panel_file"]) for r in rows if r["bot"] == bot}
        for kind in ("vs", "coin"):
            found = 0
            for (p, i), g in sorted(old.items()):
                if found == 2:
                    break
                if p not in pair_files or (bot, p, i) in by_key or new[(p, i)]["moves"] != g["moves"]:
                    continue
                held, panel = pair_files[p]
                games, _ = load_trace(trace_file("old", bot, p, held, panel, [i]))
                tick = next((t for t, x in enumerate(games[i][:60]) if t >= 8 and x["n"] > 1
                             and (kind == "vs" or "Meowth" not in json.dumps(x["board"]))), None)
                if tick is None:
                    continue
                res = probe(kind, bot, p, held, panel, i, tick)
                nothing = (res["built"] is None) if kind == "vs" else (res["queued"] is None and res["cut"] is None)
                controls.append({"bot": bot, "kind": kind, "pairing": p, "i": i, "tick": tick, "result": res, "nothing": nothing})
                found += 1
control_bad = [c for c in controls if not c["nothing"]]

# ---- the outputs ----
tally = collections.Counter(rec["verdict"] for rec in recs)
by = collections.defaultdict(collections.Counter)
for rec in recs:
    by[(rec["key"][0], rec["key"][1])][rec["verdict"]] += 1
kinds = collections.Counter((rec["d"]["kind"], rec["verdict"]) for rec in recs)


def turn_at(rec, k):
    return rec["turns"][k]["turn"] if rec["d"]["kind"] != "length" and k < len(rec["turns"]) else ""


def line(rec):
    r, d = rec["row"], rec["d"]
    head = f"{r['step']} {r['bot']} pairing {r['pairing']} i {r['i']}: "
    if d["kind"] == "length":
        return head + f"{d['detail']} => {rec['verdict']}"
    s = (f"first difference at tick {d['k']} (turn {turn_at(rec, d['k'])}; {d['kind']}: {d['detail']}; cause tick {d['cause']}); reach counters "
         f"at or before it in its turn or at the cause tick: {rec['strict'] or 'none'}")
    if rec["later"]:
        s += f"; same turn after it (never an explanation): {rec['later']}"
    if rec["probes"]:
        s += "; probes: " + json.dumps(rec["probes"], sort_keys=True)
    return head + s + f" => {rec['verdict']}" + ("" if rec["fp_ok"] else "; TRACE FINGERPRINT MISMATCH")


with open(OUT / "verdicts.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tseed\tkind\tk\tturn\tcause\treach_counters_that_explain\tverdict\tcoin_probe\tvs_probe\tcondition3\tno_reach\tfingerprints_ok\n")
    for rec in recs:
        r, d = rec["row"], rec["d"]
        f.write("\t".join(map(str, [r["step"], r["bot"], r["pairing"], r["i"], r["seed"], d["kind"], d["k"], turn_at(rec, d["k"]), d["cause"],
                                    json.dumps(rec.get("strict", {}), sort_keys=True), rec["verdict"],
                                    json.dumps(rec["probes"].get("coin", {}), sort_keys=True), json.dumps(rec["probes"].get("vs", {}), sort_keys=True),
                                    r["full_prevention_only"], r["no_reach_counter"], "yes" if rec["fp_ok"] else "NO"])) + "\n")
with open(OUT / "report.txt", "w", encoding="utf-8") as f:
    for rec in recs:
        f.write(line(rec) + "\n")
c3 = [rec for rec in recs if rec["row"]["full_prevention_only"] == "yes"]
with open(OUT / "condition3.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tkind\tk\tturn\tcoin_probe\tvs_probe\tverdict\tcoin_full_prevention_ticks\n")
    for rec in c3:
        r, d = rec["row"], rec["d"]
        f.write("\t".join(map(str, [r["step"], r["bot"], r["pairing"], r["i"], d["kind"], d["k"], turn_at(rec, d["k"]),
                                    json.dumps(rec["probes"].get("coin", {}), sort_keys=True), json.dumps(rec["probes"].get("vs", {}), sort_keys=True),
                                    rec["verdict"], json.dumps(rec["w"]["coin_full_prevention"]["ticks"])])) + "\n")
judg = [rec for rec in recs if rec["verdict"] == "NEEDS A JUDGMENT"]
with open(OUT / "judgment.md", "w", encoding="utf-8") as f:
    f.write(f"# Games that need a judgment ({len(judg)})\n\nFor Dustin, in plain words. The coin probe finds the queued coin-path choice (repair B) only at the "
            f"leaf of the bot's search: offered at ply 3 in a frame that mixes it with plain moves, so the bot sees it offered but never plays it.\n\n")
    for rec in judg:
        r, d = rec["row"], rec["d"]
        x, y = d["x"], d["y"]
        f.write(f"- **{r['bot']}, pairing {r['pairing']}, deal {r['i']}** (held {Path(r['held_file']).stem} v {Path(r['panel_file']).stem}), turn {y['turn']}, tick {d['k']}: "
                f"the old engine chose `{x['chosen'][:110]}` and R chose `{y['chosen'][:110]}` from the same position. Coin probe: {rec['probes']['coin']}.\n")
unexpl = [rec for rec in recs if rec["verdict"] == "UNEXPLAINED"]
if unexpl:
    with open(OUT / "UNEXPLAINED.md", "w", encoding="utf-8") as f:
        f.write(f"# STOP: {len(unexpl)} unexplained games\n\n" + "\n".join("- " + line(rec) for rec in unexpl) + "\n")
summary = {"rows": len(recs), "steps": a.steps, "tally": dict(tally), "by_bot_pairing": {f"{k[0]}/{k[1]}": dict(v) for k, v in sorted(by.items())},
           "kind_by_verdict": {f"{k[0]} / {k[1]}": v for k, v in sorted(kinds.items())}, "condition3": len(c3),
           "condition3_verdicts": dict(collections.Counter(rec["verdict"] for rec in c3)), "golden_mismatches": len(golden_bad),
           "controls": controls, "control_failures": len(control_bad), "problems": problems}
json.dump(summary, open(OUT / "summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k not in ("by_bot_pairing", "controls")}, indent=1))
print(f"\nCONDITION 3 rows: {len(c3)}; verdicts {summary['condition3_verdicts']}")
if golden_bad:
    print("golden mismatches:", golden_bad[:10])
if control_bad:
    print("negative controls that found something:", control_bad)
if unexpl:
    print(f"STOP: {len(unexpl)} UNEXPLAINED games (see UNEXPLAINED.md)")
sys.exit(1 if (unexpl or problems or golden_bad or control_bad) else 0)
