"""Step 8c of the rules switch (the cloud, Oct 1-2): every changed game of step 8's hand-off (main 1ba07d9,
handoff_8c.tsv; step 8b's rows too), traced on the old engine and on R to the first differing tick and classified.

For each row (one changed deal: step, bot, pairing, i):
  1. the deck files' git blob ids must equal the row's held_blob and panel_blob, and the row's files must be pairs_8.tsv's
     for its pairing;
  2. vs_trace (R's, built on each engine; build_8c.sh) replays the deal with the row's own bot on both engines, a
     whole (step, bot, pairing) group per process (tightened_rule.load_trace keys games by i, so one file per group);
     each trace's move fingerprint must equal the row's old_moves and new_moves, or the game is UNTRACED (a tool fault,
     never a verdict; it would be reported at the top);
  3. tightened_rule.py (R's, unchanged) places the first difference: kind, tick k, its turn, the cause tick;
  4. the verdict, as classify_8b.py (early_warning_8b/) gives it, which is R's first_diff.py and coin_lookahead.py on
     both repairs at once:
       ON THE BOARD   a reach counter (sitting2_check.py's REACH: vs_confusion_first_built, vs_confused_choice_offered,
                      vs_confused_choice_chosen, coin_cut_recorded, coin_queued_offered, coin_queued_offered_any; the
                      row's exact_counters, every firing tick) fired at or before k in k's turn, or at the cause tick;
       LOOKAHEAD ONLY, both halves hold
                      no such counter; kind "lookahead" (the same state, the same offered moves, a different choice);
                      both probes run on R at tick k with the row's bot, and one finds a repair's gate inside the 3
                      plies: vs_probe (A: the Confusion-first branch built by an attack within 2 moves) or coin_probe
                      (B: a queued coin-path choice offered, or a finite heads cut recorded), not leaf-only;
       NEEDS A JUDGMENT
                      no counter; lookahead; vs_probe finds nothing, and coin_probe finds the queued choice only at the
                      leaf (ply 3, in a mixed frame), as coin_lookahead.py;
       UNEXPLAINED    anything else: a "movegen" or "state" difference with no counter, a lookahead difference neither
                      probe explains. PLAN.md: a stop. A "length" difference (one game a prefix of the other) is
                      written LENGTH, for a look by hand, as the hand-off asks.
  5. golden probes on games explained on the board (the tool check R's scripts make): the coin probe at the last
     explaining B tick must find the gate on the table (queued after 0 moves or a cut at ply 1), and vs_probe at the last
     vs_confusion_first_built up to the cause must find the branch built after 0 moves. A mismatch is a tool finding,
     reported apart; it never changes a verdict.
Outputs (in the output folder): rows/<step>_<bot>_<pairing>.jsonl (one line per game, every field above), firstdiff/
the same games' two trace rows at k-1 and k (for a cross-check without the full traces), traces/ (the full traces,
gzip), and STOP.txt the moment a game is UNEXPLAINED or UNTRACED. summarize_8c.py reads rows/.
Usage: python3 trace_8c.py <work dir> <output dir> [--jobs 4] [--groups 0-35] [--no-golden]"""
import argparse, gzip, hashlib, json, os, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("work")
ap.add_argument("out")
ap.add_argument("--jobs", type=int, default=4)
ap.add_argument("--pairings", default="0-35")
ap.add_argument("--no-golden", action="store_true")
a = ap.parse_args()
W, O = Path(a.work), Path(a.out)
sys.path.insert(0, str(W / "tools"))
from tightened_rule import load_trace, first_difference, counter_hits  # noqa: E402  (R's, f8cfa9c)

SEED_BASE = "23100000000"
REACH_A = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")
REACH_B = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
REACH = REACH_A + REACH_B
SEARCH_PLIES = 3
lo, hi = map(int, a.pairings.split("-"))
for d in ("rows", "firstdiff", "traces"):
    (O / d).mkdir(parents=True, exist_ok=True)
lock = threading.Lock()


def blob_id(path):
    data = open(path, "rb").read()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def stop(msg):
    with lock:
        with open(O / "STOP.txt", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
        print("STOP: " + msg, flush=True)


lines = open(W / "handoff_8c.tsv", encoding="utf-8").read().splitlines()
head = lines[0].split("\t")
rows = [dict(zip(head, l.split("\t"))) for l in lines[1:]]
pairs = {}
for l in open(W / "pairs_8.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = l.split("\t")
    pairs[int(c[0])] = (c[3], c[5])
blobs = {}
for r in rows:
    for f, b in ((r["held_file"], r["held_blob"]), (r["panel_file"], r["panel_blob"])):
        if f not in blobs:
            blobs[f] = blob_id(W / "root" / f)
        if blobs[f] != b:
            sys.exit(f"blob mismatch: {f} is {blobs[f]} on disk, the row says {b}")
    if pairs[int(r["pairing"])] != (r["held_file"], r["panel_file"]):
        sys.exit(f"row {r['step']} {r['bot']} {r['pairing']} {r['i']}: files differ from pairs_8.tsv")
groups = {}
for r in rows:
    groups.setdefault((r["step"], r["bot"], int(r["pairing"])), []).append(r)
order = sorted((k for k in groups if lo <= k[2] <= hi), key=lambda k: (k[2], k[1] != "km3", k[0]))
print(f"{len(rows)} rows, {len(groups)} groups; blobs checked for {len(blobs)} deck files; running {len(order)} groups "
      f"(pairings {lo}-{hi}), {a.jobs} at a time", flush=True)


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def trace(engine, step, bot, pairing, deals):
    path = O / "traces" / f"trace_{engine}_{step}_{bot}_{pairing:02d}.jsonl.gz"
    if not path.exists():
        held, opp = pairs[pairing]
        rc, out, err = run([str(W / f"bin_{engine}_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
                            "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot,
                            "--deals", ",".join(map(str, deals))], W / engine / "engine")
        if rc != 0:
            raise RuntimeError(f"vs_trace {engine} {step} {bot} {pairing} failed: {err[-300:]}")
        tmp = path.with_suffix(".tmp")
        with gzip.open(tmp, "wt") as f:
            f.write(out)
        os.replace(tmp, path)
    return load_trace(path)


def probe(kind, bot, pairing, deal, tick):
    held, opp = pairs[pairing]
    exe = W / ("bin_new_vs_probe" if kind == "vs" else "bin_probe_coin_probe")
    cwd = W / ("new" if kind == "vs" else "probe") / "engine"
    rc, out, err = run([str(exe), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base", SEED_BASE,
                        "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)], cwd)
    if rc != 0:
        return {"error": err[-200:].strip()}
    if kind == "vs":
        m = re.search(r"^RESULT built=(\S+)$", out, re.M)
        return {"built": None if m[1] == "none" else int(m[1])} if m else {"error": "no RESULT line"}
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", out, re.M)
    if not m:
        return {"error": "no RESULT line"}
    parse = lambda s: None if s == "none" else int(s)
    return {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true"}


def compact(row):
    return None if row is None else {k: row[k] for k in ("tick", "turn", "actor", "n", "chosen", "offered", "state", "board")}


def do_group(key):
    step, bot, pairing = key
    grows = sorted(groups[key], key=lambda r: int(r["i"]))
    deals = [int(r["i"]) for r in grows]
    (to, to_done), (tn, tn_done) = trace("old", step, bot, pairing, deals), trace("new", step, bot, pairing, deals)
    out, fd = [], []
    for r in grows:
        i = int(r["i"])
        exact = json.loads(r["exact_counters"])
        watch = {n: {"ticks": exact.get(n, [])} for n in REACH}
        res = {"step": step, "bot": bot, "pairing": pairing, "i": i, "seed": int(r["seed"]),
               "no_reach_counter": r["no_reach_counter"], "condition3": r["full_prevention_only"],
               "exact_counters": exact, "old_ticks": len(to.get(i, [])), "new_ticks": len(tn.get(i, []))}
        fp_old = to_done.get(i, {}).get("moves") == r["old_moves"]
        fp_new = tn_done.get(i, {}).get("moves") == r["new_moves"]
        res["fingerprints"] = {"old": fp_old, "new": fp_new}
        if not (fp_old and fp_new):
            res["verdict"] = "UNTRACED"
            stop(f"{step} {bot} pairing {pairing} i {i}: a trace does not reproduce its game (old {fp_old}, new {fp_new})")
            out.append(res)
            continue
        d = first_difference(to[i], tn[i])
        res.update(kind=d["kind"], detail=d["detail"], k=d["k"], cause=d["cause"])
        if d["kind"] == "length":
            res["verdict"] = "LENGTH"
            stop(f"{step} {bot} pairing {pairing} i {i}: one game is a prefix of the other ({d['detail']}); to look at by hand")
            out.append(res)
            continue
        k, cause = d["k"], d["cause"]
        res["turn"] = tn[i][k]["turn"]
        strict = counter_hits(watch, REACH, tn[i], d)
        res["counters_explaining"] = strict
        res["counters_literal"] = counter_hits(watch, REACH, tn[i], d, literal=True)
        res["counters_after"] = counter_hits(watch, REACH, tn[i], d, after=True)
        fd.append({"step": step, "bot": bot, "pairing": pairing, "i": i, "k": k, "kind": d["kind"],
                   "old": [compact(to[i][t]) if t < len(to[i]) else None for t in (k - 1, k) if t >= 0],
                   "new": [compact(tn[i][t]) if t < len(tn[i]) else None for t in (k - 1, k) if t >= 0]})
        if strict:
            res["verdict"] = "ON THE BOARD"
            if not a.no_golden:
                b_ticks = [t for n in REACH_B for t in strict.get(n, [])]
                a_ticks = [t for t in strict.get("vs_confusion_first_built", []) if t <= cause]
                gold = {}
                if b_ticks:
                    g = probe("coin", bot, pairing, i, max(b_ticks))
                    gold["coin"] = dict(g, tick=max(b_ticks), ok=("error" not in g and (g["queued"] == 0 or g["cut"] == 1)))
                if a_ticks:
                    g = probe("vs", bot, pairing, i, max(a_ticks))
                    gold["vs"] = dict(g, tick=max(a_ticks), ok=("error" not in g and g["built"] == 0))
                res["golden"] = gold
        elif d["kind"] == "lookahead":
            c, v = probe("coin", bot, pairing, i, k), probe("vs", bot, pairing, i, k)
            res["probe_coin"], res["probe_vs"] = c, v
            if "error" in c or "error" in v:
                res["verdict"] = "PROBE ERROR"
                stop(f"{step} {bot} pairing {pairing} i {i}: a probe failed at tick {k}: coin {c}, vs {v}")
            else:
                coin_found = c["queued"] is not None or c["cut"] is not None
                leaf_only = (coin_found and c["queued"] == SEARCH_PLIES and not c["free"]
                             and (c["cut"] is None or c["cut"] > SEARCH_PLIES))
                if v["built"] is not None or (coin_found and not leaf_only):
                    res["verdict"] = "LOOKAHEAD ONLY, both halves hold"
                elif leaf_only:
                    res["verdict"] = "NEEDS A JUDGMENT"
                else:
                    res["verdict"] = "UNEXPLAINED"
        else:
            res["verdict"] = "UNEXPLAINED"
        if res["verdict"] == "UNEXPLAINED":
            stop(f"{step} {bot} pairing {pairing} i {i}: UNEXPLAINED ({d['kind']} at tick {k}, turn {res['turn']}; "
                 f"counters after k: {res['counters_after'] or 'none'})")
        out.append(res)
    tmp = O / "rows" / f"{step}_{bot}_{pairing:02d}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(x, sort_keys=True) + "\n" for x in out))
    os.replace(tmp, O / "rows" / f"{step}_{bot}_{pairing:02d}.jsonl")
    with gzip.open(O / "firstdiff" / f"{step}_{bot}_{pairing:02d}.jsonl.gz", "wt") as f:
        f.write("".join(json.dumps(x, sort_keys=True) + "\n" for x in fd))
    tally = {}
    for x in out:
        tally[x["verdict"]] = tally.get(x["verdict"], 0) + 1
    return key, tally


todo = [k for k in order if not (O / "rows" / f"{k[0]}_{k[1]}_{k[2]:02d}.jsonl").exists()]
print(f"{len(order) - len(todo)} groups already done; {len(todo)} to run", flush=True)
with ThreadPoolExecutor(max_workers=a.jobs) as pool:
    futs = {pool.submit(do_group, k): k for k in todo}
    for f in as_completed(futs):
        try:
            key, tally = f.result()
            print(f"done {key[0]} {key[1]} pairing {key[2]}: {len(groups[key])} games, {json.dumps(tally, sort_keys=True)}", flush=True)
        except Exception as e:  # noqa: BLE001
            stop(f"group {futs[f]} failed: {e}")
print("ALL GROUPS DONE", flush=True)
