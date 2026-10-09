"""Rules switch 2, step 8c's classifier (the cloud, Oct 9; switch-2 PLAN.md precondition (b), "copies of tightened_rule.py,
classify_8c.py and coin_lookahead.py go in this folder"). A copy of the first switch's `../engine_switch_rules_2026-10/trace_8c_sonnet/
classify_8c.py` (Sonnet's, Oct 1), changed only where switch 2 differs:
  - the rule is this folder's tightened_rule.py (v3): a "length" difference (the new game shorter, longer or as long) is judged like
    any other board difference (PLAN.md's mechanic check, change 2; Dustin's "1-3 sure", Oct 9), by `board_hits`: an exact counter at
    or before k in k's turn or at the cause tick, or, when the new game is the longer one, at its first extra tick. The first switch's
    copy read every "length" difference as UNEXPLAINED (its line 162);
  - the reach counters are round 2's exact names (`round2_reach`, from instrument_scan.py's R2_COUNTERS and R2_KEYED less the off-gate
    and superset ones; P2's attack_return_weakness among them), the keyed ones ({key: [ticks]}) read through `watch_from_counters`
    (coin_queued_by_attack counts only the later round's eight attacks). Round 1's counters are not explanations: both engines have
    round 1;
  - the probe is coin_probe v2 (`../round2_readiness_2026-10-02/coin_probe_v2.rs`, built on the candidate engine with precondition
    (a)'s round-2 conditions): QUEUED, CUT, RETURN and RESULT_R2's seven kinds and trapleaf, read by `parse_probe` and judged by
    `lookahead_verdict` (read its docstring: what is inside the search, what is only at its leaf, and the strict reading of a queued
    choice that may be a first-round site). A probe that stops at the node limit having found nothing is run again at 600,000 nodes
    (validate_v2.py's rule). vs_probe is not run: its gate (repair A's Confusion-first branch) is the first round's, on both engines;
  - the golden check runs at the last explaining tick of every exact counter the probe has a condition for (`golden_ok`: the counter's
    kind at ply 1, RETURN at ply 1, a queued choice after 0 moves or a cut at ply 1); luxury_coin_opp_stadium and fossil_item_lock
    have none and are listed as such, and so has coin_queued_by_attack at a tick where it fired only for Mega Kangaskhan ex's
    Double-Punching Family (the keys that fired there, from the row's raw exact counters; `golden_ok`'s docstring says why);
  - CONDITION 3 rows are the changed rows where no reach counter fired anywhere in the game and an off-gate counter did (the hand-off's
    offgate_counters column), listed in condition3.tsv as before;
  - the negative controls require no queued coin-path choice, cut or return ply (`control_clean`, step 8b's requirement);
  - "In lookahead" also needs the revert check (PLAN.md's change 3, precondition (e)): this script doesn't run it; every lookahead
    verdict is listed in lookahead.tsv for it.
For each changed row (step, bot, pairing, i) of the hand-off: vs_trace on both engines (each trace's move fingerprint must equal the
row's), first_difference, then ON THE BOARD (board_hits), else for a "lookahead" difference the probe at k (LOOKAHEAD ONLY, both halves
hold / NEEDS A JUDGMENT / UNEXPLAINED), else UNEXPLAINED. UNEXPLAINED stops the switch; so does it under the strict reading, which is
reported beside the verdict (STRICT column, summary's strict_tally), as step 8b's classify_8b.py did.

Usage: python3 classify_8c.py --work W --tsv HANDOFF.tsv --out OUT [--steps 8] [--jobs 12] [--limit N] [--no-golden]
       [--controls-from DIR --controls-tag TAG] [--seed-base 23100000000] [--instrument PATH]
W holds root/ (decks, as the hand-off's paths name them), old/engine, new/engine and probe/engine (the engine copies the programs were
built in: their working directories), and bin_old_vs_trace, bin_new_vs_trace and bin_probe_coin_probe_v2. The hand-off's
exact_counters column holds {name: [ticks]}, a keyed counter {name: {key: [ticks]}}. --controls-from DIR reads DIR/TAG_old_<bot>.jsonl
and DIR/TAG_new_<bot>.jsonl (legality_scan rows) for the negative controls. --instrument is the watch build's coin script
(default: ../coin_prevention_repair_2026-09-30/instrument_scan.py beside this folder). Only the first differing rows and each game's
turn list are kept in memory, never a whole trace."""
import argparse, collections, concurrent.futures as cf, csv, gzip, hashlib, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from tightened_rule import (load_trace, first_difference, counter_hits, board_hits, round2_reach, watch_from_counters,  # noqa: E402
                            parse_probe, nothing_found, control_clean, lookahead_verdict, golden_ok, ROUND2_QUEUED, R2_KINDS, BOTH_HALVES, JUDGMENT)

ap = argparse.ArgumentParser()
ap.add_argument("--work", required=True)
ap.add_argument("--tsv", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--steps", default="8")
ap.add_argument("--jobs", type=int, default=12)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--no-golden", action="store_true")
ap.add_argument("--controls-from", default=None)
ap.add_argument("--controls-tag", default=None)
ap.add_argument("--seed-base", default="23100000000")
ap.add_argument("--instrument", default=str(HERE.parent / "coin_prevention_repair_2026-09-30" / "instrument_scan.py"))
ap.add_argument("--chunk", type=int, default=20, help="deals per vs_trace call")
a = ap.parse_args()
if a.controls_from and not a.controls_tag:
    sys.exit("--controls-from needs --controls-tag")
W, OUT = Path(a.work).resolve(), Path(a.out)
OUT.mkdir(parents=True, exist_ok=True)
(W / "traces").mkdir(exist_ok=True)

SEED_BASE = a.seed_base
REACH = round2_reach(Path(a.instrument).read_text(encoding="utf-8"))
RETRY_LIMIT = 600_000
EMPTY = {"queued": None, "cut": None, "free": False, "ret": None, "r2": {k: None for k in R2_KINDS}, "trapleaf": None}
NICE = ["nice", "-n", "19"]
# The cards that use the later coin round's eight attacks (printings), to say whether a pairing's lists can reach a later-round queued
# choice at all when the probe's QUEUED path names no attack (step 8b's classify_8b.py).
ROUND2_ATTACKERS = {"A4 045", "A4 215", "B2 048", "B3 051", "B1a 019", "B1a 020", "B1a 078", "B1a 084", "B4 077", "A4a 018",
                    "B2 127", "B2 189", "B2 202", "B4 231"}

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


def reaches_round2(held, panel):
    """Whether either list holds one of the later round's attackers."""
    text = (W / "root" / held).read_text(encoding="utf-8") + (W / "root" / panel).read_text(encoding="utf-8")
    return any(re.search(rf"\b{re.escape(c)}\s*$", text, re.M) for c in ROUND2_ATTACKERS)


# ---- traces: old and new, per (bot, pairing, deck pair), in chunks, in parallel; each chunk is reduced to compact records at once ----
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

print(f"{len(rows)} changed rows, {len(chunks)} chunks x 2 engines, {a.jobs} jobs; reach counters: {', '.join(REACH)}", flush=True)
analysed = {}
with cf.ThreadPoolExecutor(a.jobs) as ex:
    futs = [ex.submit(analyse_chunk, *c) for c in chunks]
    for n, f in enumerate(cf.as_completed(futs), 1):
        for rec in f.result():
            analysed[rec["key"]] = rec
        if n % 10 == 0 or n == len(futs):
            print(f"  traced and compared {n}/{len(futs)} chunks", flush=True)


# ---- the probe ----
def probe(bot, pairing, held, panel, deal, tick, limit=None):
    out = run([str(W / "bin_probe_coin_probe_v2"), "--a", str(W / "root" / held), "--b", str(W / "root" / panel), "--seed-base", SEED_BASE,
               "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)]
              + (["--node-limit", str(limit)] if limit else []), W / "probe" / "engine")
    c = parse_probe(out)
    if c.get("truncated") and limit is None and nothing_found(c):
        return probe(bot, pairing, held, panel, deal, tick, RETRY_LIMIT) | {"retried": RETRY_LIMIT}
    return c


def watch_of(row):
    return watch_from_counters(json.loads(row["exact_counters"] or "{}"), REACH)


def fired_keys(row, name, tick):
    """The round-2 keys a keyed exact counter fired for at `tick`, from the hand-off row's raw exact counters (() for a plain one)."""
    v = json.loads(row["exact_counters"] or "{}").get(name)
    if not isinstance(v, dict):
        return ()
    return tuple(sorted(k for k, ticks in v.items() if tick in ticks and (name != "coin_queued_by_attack" or k in ROUND2_QUEUED)))


def has_offgate(row):
    try:
        v = json.loads(row.get("offgate_counters") or "{}")
    except json.JSONDecodeError:
        return bool(row.get("offgate_counters"))
    return any(bool(x) for x in (v.values() if isinstance(v, dict) else v))


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
    rec = {"row": r, "key": key, "fp_ok": fp_ok, "d": d, "turns": turns, "w": w, "probes": {}, "verdict": None, "strict": None, "note": ""}
    rec["hits"] = board_hits(w, REACH, turns, d)
    rec["later"] = counter_hits(w, REACH, turns, d, after=True)
    if rec["hits"]:
        rec["verdict"] = rec["strict"] = "ON THE BOARD"
    elif d["kind"] == "lookahead":
        rec["verdict"] = "?"            # decided after the probe
    else:
        rec["verdict"] = rec["strict"] = "UNEXPLAINED"
        rec["note"] = f"{d['kind']}: {d['detail']}, no reach counter"
    rec["condition3"] = not any(v["ticks"] for v in w.values()) and has_offgate(r)
    recs.append(rec)

# ---- probe jobs: every lookahead game at k; golden probes at the last explaining tick of each counter the probe has a condition for ----
jobs = []
for rec in recs:
    d = rec["d"]
    if rec["verdict"] == "?":
        jobs.append((rec, "probe", d["k"]))
    elif rec["verdict"] == "ON THE BOARD" and not a.no_golden:
        for tick in sorted({max(ticks) for name, ticks in rec["hits"].items() if golden_ok(name, EMPTY) is not None}):
            jobs.append((rec, f"golden_{tick}", tick))
print(f"{len(jobs)} probe runs", flush=True)


def do_probe(job):
    rec, kind, tick = job
    r = rec["row"]
    return rec, kind, tick, probe(r["bot"], r["pairing"], r["held_file"], r["panel_file"], r["i"], tick)


with cf.ThreadPoolExecutor(a.jobs) as ex:
    futs = [ex.submit(do_probe, j) for j in jobs]
    for n, f in enumerate(cf.as_completed(futs), 1):
        rec, kind, tick, res = f.result()
        rec["probes"][kind] = {"tick": tick, **res}
        if n % 100 == 0 or n == len(futs):
            print(f"  probed {n}/{len(futs)}", flush=True)

golden_bad, no_golden = [], collections.Counter()
for rec in recs:
    p, r = rec["probes"], rec["row"]
    if rec["verdict"] == "?":
        c = p["probe"]
        named = set(c.get("queued_attacks", []))
        round2_queued = bool(named & ROUND2_QUEUED) if named else reaches_round2(r["held_file"], r["panel_file"])
        rec["verdict"], rec["strict"] = lookahead_verdict(c, round2_queued)
        if rec["verdict"] == "UNEXPLAINED":
            rec["note"] = "a lookahead difference the probe doesn't explain"
        elif rec["strict"] != rec["verdict"]:
            rec["note"] = ("only a queued choice or cut the probe can't tell from a first-round site, which both engines build ("
                           + (f"the path names {', '.join(sorted(named))}" if named else "neither list holds a later-round attacker") + ")")
    if rec["verdict"] == "ON THE BOARD":
        for name, ticks in rec["hits"].items():
            g = p.get(f"golden_{max(ticks)}")
            ok = golden_ok(name, g, fired_keys(r, name, max(ticks))) if g else None
            if ok is None:
                no_golden[name] += 1
            elif not ok:
                golden_bad.append((rec["key"], name, g))

# ---- negative controls: unchanged games, a mid-game tick, no queued coin-path choice, cut or return ply (control_clean) ----
controls = []
if a.controls_from:
    for bot in sorted({r["bot"] for r in rows}):
        old = {(g["pairing"], g["i"]): g for g in map(json.loads, open(Path(a.controls_from) / f"{a.controls_tag}_old_{bot}.jsonl"))}
        new = {(g["pairing"], g["i"]): g for g in map(json.loads, open(Path(a.controls_from) / f"{a.controls_tag}_new_{bot}.jsonl"))}
        pair_files = {r["pairing"]: (r["held_file"], r["panel_file"]) for r in rows if r["bot"] == bot}
        found = 0
        for (pg, i), g in sorted(old.items()):
            if found == 4:
                break
            if pg not in pair_files or (bot, pg, i) in by_key or new[(pg, i)]["moves"] != g["moves"]:
                continue
            held, panel = pair_files[pg]
            games, _ = load_trace(trace_file("old", bot, pg, held, panel, [i]))
            tick = next((t for t, x in enumerate(games[i][:60]) if t >= 8 and x["n"] > 1 and "Meowth" not in json.dumps(x["board"])), None)
            if tick is None:
                continue
            res = probe(bot, pg, held, panel, i, tick)
            controls.append({"bot": bot, "pairing": pg, "i": i, "tick": tick, "result": res, "nothing": control_clean(res)})
            found += 1
control_bad = [c for c in controls if not c["nothing"]]

# ---- the outputs ----
tally = collections.Counter(rec["verdict"] for rec in recs)
strict_tally = collections.Counter(rec["strict"] for rec in recs)
by = collections.defaultdict(collections.Counter)
for rec in recs:
    by[(rec["key"][0], rec["key"][1])][rec["verdict"]] += 1
kinds = collections.Counter((rec["d"]["kind"] + ("" if rec["d"]["kind"] != "length" else f" ({rec['d'].get('longer') or 'as long'})"),
                             rec["verdict"]) for rec in recs)


def turn_at(rec, k):
    t = rec["turns"]
    if k < len(t):
        return t[k]["turn"]
    row = rec["d"].get("x") or rec["d"].get("y")
    return row["turn"] if row else (t[-1]["turn"] if t else "")


def line(rec):
    r, d = rec["row"], rec["d"]
    head = f"{r['step']} {r['bot']} pairing {r['pairing']} i {r['i']}: "
    s = (f"first difference at tick {d['k']} (turn {turn_at(rec, d['k'])}; {d['kind']}: {d['detail']}"
         + (f", the longer game: {d.get('longer')}" if d["kind"] == "length" else "")
         + f"; cause tick {d['cause']}); reach counters at or before it in its turn, at the cause tick"
         + (" or at the new game's first extra tick" if d["kind"] == "length" and d.get("longer") == "new" else "")
         + f": {rec['hits'] or 'none'}")
    if rec["later"]:
        s += f"; same turn after it (never an explanation): {rec['later']}"
    if rec["probes"]:
        s += "; probes: " + json.dumps(rec["probes"], sort_keys=True)
    s += f" => {rec['verdict']}" + ("" if rec["strict"] == rec["verdict"] else f" (STRICT: {rec['strict']})")
    if rec["note"]:
        s += f" [{rec['note']}]"
    return head + s + ("" if rec["fp_ok"] else "; TRACE FINGERPRINT MISMATCH")


with open(OUT / "verdicts.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tseed\tkind\tlonger\tk\tturn\tcause\treach_counters_that_explain\tverdict\tstrict\tprobe\tcondition3\tfingerprints_ok\n")
    for rec in recs:
        r, d = rec["row"], rec["d"]
        f.write("\t".join(map(str, [r["step"], r["bot"], r["pairing"], r["i"], r["seed"], d["kind"], d.get("longer") or "", d["k"],
                                    turn_at(rec, d["k"]), d["cause"], json.dumps(rec["hits"], sort_keys=True), rec["verdict"], rec["strict"],
                                    json.dumps(rec["probes"].get("probe", {}), sort_keys=True), "yes" if rec["condition3"] else "",
                                    "yes" if rec["fp_ok"] else "NO"])) + "\n")
with open(OUT / "report.txt", "w", encoding="utf-8") as f:
    for rec in recs:
        f.write(line(rec) + "\n")
look = [rec for rec in recs if rec["verdict"] in (BOTH_HALVES, JUDGMENT)]
with open(OUT / "lookahead.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tseed\tk\tturn\tverdict\tstrict\tprobe\n")
    for rec in look:
        r, d = rec["row"], rec["d"]
        f.write("\t".join(map(str, [r["step"], r["bot"], r["pairing"], r["i"], r["seed"], d["k"], turn_at(rec, d["k"]), rec["verdict"],
                                    rec["strict"], json.dumps(rec["probes"].get("probe", {}), sort_keys=True)])) + "\n")
c3 = [rec for rec in recs if rec["condition3"]]
with open(OUT / "condition3.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tkind\tk\tturn\tprobe\tverdict\tstrict\toffgate_counters\n")
    for rec in c3:
        r, d = rec["row"], rec["d"]
        f.write("\t".join(map(str, [r["step"], r["bot"], r["pairing"], r["i"], d["kind"], d["k"], turn_at(rec, d["k"]),
                                    json.dumps(rec["probes"].get("probe", {}), sort_keys=True), rec["verdict"], rec["strict"],
                                    r.get("offgate_counters", "")])) + "\n")
judg = [rec for rec in recs if rec["verdict"] == JUDGMENT or rec["strict"] == JUDGMENT]
with open(OUT / "judgment.md", "w", encoding="utf-8") as f:
    f.write(f"# Games that need a judgment ({len(judg)})\n\nFor Dustin, in plain words. The probe finds what the new rules changed only at "
            f"the edge of the bot's search: a queued coin choice offered at its last step beside plain moves, a round-2 condition offered "
            f"just past it, or a position at its last step where Trap Territory raised a Retreat Cost. The bot sees it there but never "
            f"plays it out, so the switch's revert check decides.\n\n")
    for rec in judg:
        r, d = rec["row"], rec["d"]
        x, y = d["x"], d["y"]
        f.write(f"- **{r['bot']}, pairing {r['pairing']}, deal {r['i']}** (held {Path(r['held_file']).stem} v {Path(r['panel_file']).stem}), "
                f"turn {y['turn']}, tick {d['k']}: the old engine chose `{x['chosen'][:110]}` and the new one chose `{y['chosen'][:110]}` "
                f"from the same position. Probe: {rec['probes'].get('probe')}.\n")
unexpl = [rec for rec in recs if rec["verdict"] == "UNEXPLAINED" or rec["strict"] == "UNEXPLAINED"]
(OUT / "UNEXPLAINED.md").unlink(missing_ok=True)
if unexpl:
    with open(OUT / "UNEXPLAINED.md", "w", encoding="utf-8") as f:
        f.write(f"# STOP: {len(unexpl)} unexplained games (the strict reading included)\n\n" + "\n".join("- " + line(rec) for rec in unexpl) + "\n")
summary = {"rows": len(recs), "steps": a.steps, "reach": list(REACH), "tally": dict(tally), "strict_tally": dict(strict_tally),
           "by_bot_pairing": {f"{k[0]}/{k[1]}": dict(v) for k, v in sorted(by.items())},
           "kind_by_verdict": {f"{k[0]} / {k[1]}": v for k, v in sorted(kinds.items())}, "condition3": len(c3),
           "condition3_verdicts": dict(collections.Counter(rec["verdict"] for rec in c3)), "golden_mismatches": len(golden_bad),
           "explaining_counters_without_a_golden_check": dict(no_golden), "lookahead_for_the_revert_check": len(look),
           "controls": controls, "control_failures": len(control_bad), "problems": problems,
           "tightened_rule_sha256": hashlib.sha256((HERE / "tightened_rule.py").read_bytes()).hexdigest()}
json.dump(summary, open(OUT / "summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in summary.items() if k not in ("by_bot_pairing", "controls")}, indent=1))
print(f"\nCONDITION 3 rows: {len(c3)}; verdicts {summary['condition3_verdicts']}")
if golden_bad:
    print("golden mismatches:", golden_bad[:10])
if control_bad:
    print("negative controls that found something:", control_bad)
if unexpl:
    print(f"STOP: {len(unexpl)} UNEXPLAINED games, the strict reading included (see UNEXPLAINED.md)")
sys.exit(1 if (unexpl or problems or golden_bad or control_bad) else 0)
