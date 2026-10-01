"""PLAN.md step 8b's early-warning rows, classified (the cloud, Oct 1; read with run_8b.sh, which made the inputs).

For each bot (km3, k3) the 160 deals (pairings 32-35, i < 40) were played on the old engine, the new one (R) and the watch
build. This script:
  1. checks the files: 160 games each, the same deals; the pinned old legality_scan's rows equal the old rows built from
     source on every field; the watch rows equal the new rows on every field the new rows record (watch must equal plain);
  2. lists the CHANGED games: the new game differs from the old one on any field the old file records (sitting2_check.py
     touched's definition);
  3. traces every changed game on both engines (vs_trace.rs, R's version, built on each) and checks each trace's move
     fingerprint against its scan row;
  4. classifies each by tightened_rule.py (R's, unchanged; read its docstring), the rule R's first_diff.py and
     coin_lookahead.py apply, here to both repairs at once:
       ON THE BOARD  a reach counter fired in the watch row at or before the first differing tick k in k's turn, or at the
                     cause tick: repair A's vs_confusion_first_built, vs_confused_choice_offered, vs_confused_choice_chosen;
                     repair B's coin_cut_recorded, coin_queued_offered, coin_queued_offered_any (sitting2_check.py's REACH);
       LOOKAHEAD ONLY, both halves hold
                     no such counter, the first difference is a "lookahead" one (the same state, the same offered moves, a
                     different choice), and a probe run on R at tick k finds a repair's gate inside the bot's 3 plies:
                     vs_probe.rs (repair A: the Confusion-first branch built by an attack within 2 moves) or coin_probe.rs
                     (repair B: a queued coin-path choice offered, or a finite heads cut recorded); the code-gate half is
                     the one read in the code, as R's scripts' docstrings give it;
       NEEDS A JUDGMENT  coin_probe finds the queued choice only at the leaf (ply 3, a mixed frame), as coin_lookahead.py;
       UNEXPLAINED   anything else ("movegen", "state" or "length" with no counter; or a lookahead difference neither probe
                     explains). PLAN.md: that stops the switch.
     As in R's scripts, the probe also runs as a golden check on the games explained on the board (the gate must be on the
     table at the last explaining tick), and as a negative control at a mid-game tick of unchanged games.
  5. reports the share of changed games no exact counter explains, and the implied trace load for step 8.
Usage: python3 classify_8b.py <work dir>   (writes the traces into the work dir; prints the report)"""
import gzip, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path(sys.argv[1])
sys.path.insert(0, str(W / "tools"))       # run_8b.sh put R's tightened_rule.py there (f8cfa9c)
from tightened_rule import load_trace, first_difference, counter_hits  # noqa: E402

BOTS = ("km3", "k3")
PAIRINGS = (32, 33, 34, 35)
SEED_BASE = "23100000000"
REACH_A = ("vs_confusion_first_built", "vs_confused_choice_offered", "vs_confused_choice_chosen")
REACH_B = ("coin_cut_recorded", "coin_queued_offered", "coin_queued_offered_any")
REACH = REACH_A + REACH_B
SEARCH_PLIES = 3
STEP8_DEALS = {"km3": 16_000, "k3": 8_000}   # step 8: 32 pairings x km3 500 and k3 250 (72,000 games = 24,000 deals x 3)

pairs = {}
for line in open(HERE / "pairs_8.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = line.split("\t")
    pairs[int(c[0])] = (c[2], c[3], c[4], c[5])          # held_key, held_file, opponent, panel_file


def rows(v, bot):
    return {(r["pairing"], r["i"]): r for r in map(json.loads, open(W / f"8b_{v}_{bot}.jsonl"))}


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"failed: {' '.join(cmd)}\n{p.stderr[-400:]}")
    return p.stdout


def trace(engine, bot, pairing, deals):
    """vs_trace on one engine for some deals of one pairing; cached as a gzip file in the work dir."""
    path = W / f"trace_{engine}_{bot}_{pairing}.jsonl.gz"
    if not path.exists():
        _, held, _, opp = pairs[pairing]
        out = run([str(W / f"bin_{engine}_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
                   "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot,
                   "--deals", ",".join(map(str, deals))], W / engine / "engine")
        with gzip.open(path, "wt") as f:
            f.write(out)
    return load_trace(path)


def load_trace_one(bot, pairing, deal):
    """One unchanged game's trace on the old engine (for the negative controls)."""
    path = W / f"trace_control_{bot}_{pairing}_{deal}.jsonl.gz"
    if not path.exists():
        _, held, _, opp = pairs[pairing]
        out = run([str(W / "bin_old_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
                   "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot, "--deals", str(deal)], W / "old" / "engine")
        with gzip.open(path, "wt") as f:
            f.write(out)
    games, _ = load_trace(path)
    return games[deal], None


def probe(kind, bot, pairing, deal, tick):
    _, held, _, opp = pairs[pairing]
    exe = W / ("bin_new_vs_probe" if kind == "vs" else "bin_probe_coin_probe")
    cwd = W / ("new" if kind == "vs" else "probe") / "engine"
    out = run([str(exe), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base", SEED_BASE,
               "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)], cwd)
    import re
    if kind == "vs":
        m = re.search(r"^RESULT built=(\S+)$", out, re.M)
        return {"built": None if m[1] == "none" else int(m[1])}
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", out, re.M)
    parse = lambda s: None if s == "none" else int(s)
    return {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true"}


report, summary, problems = [], {}, []
say = report.append
for bot in BOTS:
    old, new, watch, pinned = rows("old", bot), rows("new", bot), rows("watch", bot), rows("pinned", bot)
    keys = sorted(old)
    want = [(p, i) for p in PAIRINGS for i in range(40)]
    for name, d in (("old", old), ("new", new), ("watch", watch), ("pinned", pinned)):
        if sorted(d) != want:
            problems.append(f"{bot} {name}: not exactly the 160 deals")
    pin_same = sum(pinned[k] == old[k] for k in keys)
    watch_same = sum(all(watch[k].get(f) == v for f, v in new[k].items()) for k in keys)
    seat_ok = sum(old[k]["first_seat"] == (0 if k[1] % 2 == 0 else 1) for k in keys)
    say(f"\n=== {bot}")
    say(f"checks: pinned old legality_scan v old built from source, every field: {pin_same} of {len(keys)} equal; "
        f"watch v new on every field new records: {watch_same} of {len(keys)} equal; first seat by i's parity (vs_trace's "
        f"setup): {seat_ok} of {len(keys)}")
    if pin_same != len(keys) or watch_same != len(keys) or seat_ok != len(keys):
        problems.append(f"{bot}: a file check failed")
    changed = [k for k in keys if any(new[k].get(f) != v for f, v in old[k].items())]
    moves_differ = [k for k in keys if new[k]["moves"] != old[k]["moves"]]
    say(f"changed games (new v old on any field old records): {len(changed)} of {len(keys)}; moves differ in {len(moves_differ)}")
    by_pairing = {p: [k[1] for k in changed if k[0] == p] for p in PAIRINGS}
    traces = {}
    for p in PAIRINGS:
        if by_pairing[p]:
            traces[p] = {e: trace(e, bot, p, by_pairing[p]) for e in ("old", "new")}
    verdicts = {}
    for p in PAIRINGS:
        held_key, _, opp_key, _ = pairs[p]
        say(f"\npairing {p}, {held_key} v {opp_key}: {len(by_pairing[p])} changed of 40"
            + (f": {by_pairing[p]}" if by_pairing[p] else ""))
        for i in by_pairing[p]:
            (to, to_done), (tn, tn_done) = traces[p]["old"], traces[p]["new"]
            fp_ok = to_done[i]["moves"] == old[(p, i)]["moves"] and tn_done[i]["moves"] == new[(p, i)]["moves"]
            if not fp_ok:
                problems.append(f"{bot} pairing {p} i {i}: a trace's move fingerprint differs from its scan")
            a, b, w = to[i], tn[i], watch[(p, i)]
            d = first_difference(a, b)
            if d["kind"] == "length":
                verdicts[(p, i)] = ("UNEXPLAINED", d)
                say(f"  i = {i:2d}: {d['detail']} => UNEXPLAINED")
                continue
            k, cause = d["k"], d["cause"]
            strict = counter_hits(w, REACH, b, d)
            later = counter_hits(w, REACH, b, d, after=True)
            head = (f"  i = {i:2d}: first difference at tick {k} (turn {b[k]['turn']}; {d['kind']}: {d['detail']}; cause tick "
                    f"{cause}); reach counters at or before it in its turn, or at the cause tick: {strict or 'none'}"
                    + (f"; same turn after it (never an explanation): {later}" if later else "")
                    + ("" if fp_ok else "; TRACE FINGERPRINT MISMATCH"))
            if strict:
                verdict, gold = "ON THE BOARD", ""
                b_ticks = [t for n in REACH_B for t in strict.get(n, [])]
                a_ticks = [t for t in strict.get("vs_confusion_first_built", []) if t <= cause]
                if b_ticks:
                    g = probe("coin", bot, p, i, max(b_ticks))
                    ok = g["queued"] == 0 or g["cut"] == 1
                    gold += f"; golden coin probe at tick {max(b_ticks)}: {g} ({'on the table' if ok else 'NOT ON THE TABLE'})"
                    problems += [] if ok else [f"{bot} pairing {p} i {i}: golden coin probe not on the table"]
                if a_ticks:
                    g = probe("vs", bot, p, i, max(a_ticks))
                    ok = g["built"] == 0
                    gold += f"; golden vs probe at tick {max(a_ticks)}: {g} ({'match' if ok else 'DIFFERENT, it must be 0'})"
                    problems += [] if ok else [f"{bot} pairing {p} i {i}: golden vs probe not built after 0 moves"]
                say(f"{head}{gold} => {verdict}")
            elif d["kind"] == "lookahead":
                c, v = probe("coin", bot, p, i, k), probe("vs", bot, p, i, k)
                coin_found = c["queued"] is not None or c["cut"] is not None
                leaf_only = coin_found and c["queued"] == SEARCH_PLIES and not c["free"] and (c["cut"] is None or c["cut"] > SEARCH_PLIES)
                if v["built"] is not None or (coin_found and not leaf_only):
                    verdict = "LOOKAHEAD ONLY, both halves hold"
                elif leaf_only:
                    verdict = "NEEDS A JUDGMENT"
                else:
                    verdict = "UNEXPLAINED"
                say(f"{head}; probes at tick {k}: coin {c}, vs {v} => {verdict}")
            else:
                verdict = "UNEXPLAINED"
                say(f"{head} => {verdict}")
            verdicts[(p, i)] = (verdict, d)
    # Negative controls, as R's scripts pick them: in unchanged games, the first tick from 8 on with two or more offered
    # moves (for the coin probe also with no Meowth in play on either side); nothing may be found there. Up to two per
    # probe, from the pairings where its repair can act (32 for A; 33-35 for B).
    unchanged = [k for k in keys if k not in changed]
    controls = 0
    for kind, ps in (("vs", (32,)), ("coin", (33, 34, 35))):
        found = 0
        for (p, i) in unchanged:
            if found == 2 or p not in ps:
                continue
            tr, _ = load_trace_one(bot, p, i)
            tick = next((t for t, r in enumerate(tr[:60]) if t >= 8 and r["n"] > 1
                         and (kind == "vs" or "Meowth" not in json.dumps(r["board"]))), None)
            if tick is None:
                continue
            g = probe(kind, bot, p, i, tick)
            nothing = (g.get("built") is None) if kind == "vs" else (g["queued"] is None and g["cut"] is None)
            say(f"control ({kind} probe), pairing {p} i {i} tick {tick}, an unchanged game: {g} "
                f"({'nothing found' if nothing else 'FOUND SOMETHING'})")
            controls += 0 if nothing else 1
            found += 1
    if controls:
        problems.append(f"{bot}: {controls} negative controls found something")
    tally = {}
    for v, _ in verdicts.values():
        tally[v] = tally.get(v, 0) + 1
    no_counter = [k for k, (v, _) in verdicts.items() if v != "ON THE BOARD"]
    hand = [k for k, (v, _) in verdicts.items() if v in ("UNEXPLAINED", "NEEDS A JUDGMENT")]
    say(f"\n{bot} verdicts: {json.dumps(tally)}; controls that found something: {controls}")
    summary[bot] = {"games": len(keys), "changed": len(changed), "no_counter": len(no_counter), "hand": len(hand),
                    "tally": tally, "no_counter_games": no_counter, "hand_games": hand,
                    "per_pairing": {p: {"changed": len(by_pairing[p]),
                                        "no_counter": sum(1 for k in no_counter if k[0] == p),
                                        "hand": sum(1 for k in hand if k[0] == p)} for p in PAIRINGS}}

say("\n=== the share and the implied trace load for step 8")
tot_g = sum(s["games"] for s in summary.values())
tot_c = sum(s["changed"] for s in summary.values())
tot_n = sum(s["no_counter"] for s in summary.values())
tot_h = sum(s["hand"] for s in summary.values())
say(f"deals: {tot_g} (old v new; 960 games over the three builds); changed: {tot_c}; no exact counter explains on the board: "
    f"{tot_n}; of those, settled by a probe (lookahead only, both halves): {tot_n - tot_h}; needing a hand trace or a judgment "
    f"(UNEXPLAINED or NEEDS A JUDGMENT): {tot_h}")
load_n = sum(summary[b]["no_counter"] / summary[b]["games"] * STEP8_DEALS[b] for b in BOTS)
load_h = sum(summary[b]["hand"] / summary[b]["games"] * STEP8_DEALS[b] for b in BOTS)
say(f"per bot: " + "; ".join(f"{b}: changed {summary[b]['changed']}/{summary[b]['games']}, no counter {summary[b]['no_counter']}, "
                              f"hand {summary[b]['hand']}" for b in BOTS))
say(f"implied for step 8 (24,000 deals: km3 16,000, k3 8,000; each bot's share of its 160 deals times its step 8 deals):")
say(f"  changed games no exact counter explains: {load_n:.0f}")
say(f"  of them needing a hand trace or a judgment after the probes: {load_h:.0f}")
say(f"(plain proportion, all 320 deals: {tot_n / tot_g * 24_000:.0f} and {tot_h / tot_g * 24_000:.0f})")
say(f"\nproblems: {problems or 'none'}")
print("\n".join(report))
json.dump(summary, open(W / "summary.json", "w"), indent=1, default=str)
sys.exit(1 if problems else 0)
