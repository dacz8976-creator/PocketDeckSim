"""Rules switch 2, step 8b's early-warning rows, classified (the cloud, Oct 9; read with run_8b.sh, which made the inputs).
Oct 1's classify_8b.py (`../../engine_switch_rules_2026-10/early_warning_8b/`, on claude/pensive-ptolemy-spwc0b), adapted to
this switch as the coordinator's decision 14 asks: "classified with probe v2 and the tightened rule v2".

For each bot (km3, k3) the 240 deals (pairings 32-37, i < 40) were played on the old engine (the official one, main-8626a35),
the new one (claude/coin-prevention-round2's final engine) and the watch build. This script:
  1. checks the files: 240 games each, the same deals; the pinned official legality_scan's rows equal the old rows built from
     source on every field; for pairings 32-35 they equal Oct 1's recorded new-engine rows (main's 5a18d31_8b_new_<bot>.jsonl,
     the side the laptop reuses as "old") on every field; the watch rows equal the new rows on every field the new rows
     record; the first seat follows i's parity;
  2. lists the CHANGED games: the new game differs from the old one on any field the old file records;
  3. traces every changed game on both engines (vs_trace.rs) and checks each trace's move fingerprint against its scan row;
  4. classifies each by tightened_rule_v2.py (`../../round2_readiness_2026-10-02/`, unchanged; read its docstring):
       ON THE BOARD  an exact counter of a mechanic this switch changes (the round-2 and P2 counters: instrument_scan.py's
                     EXACT list, the keyed ones with all their keys' ticks together, except that coin_queued_by_attack counts
                     only the later round's eight attacks: its other keys, Chase Order and the first round's helpers such as
                     Tongue Whip and Diving Icicles, build the same choice on both engines) fired in the watch row at or before the
                     first differing tick k in k's turn, or at the cause tick; or, for a "length" difference where the new
                     game is the longer one, at its first extra tick (`extra_tick_hits`). The first round's counters are not
                     explanations here: both engines have the first round;
       LOOKAHEAD ONLY, both halves hold
                     no such counter, the first difference is a "lookahead" one, and coin_probe v2 run on the new engine at
                     tick k finds a gate inside the bot's 3 plies: QUEUED or CUT (the coin rounds; not only at the leaf of a
                     mixed frame) or RETURN (P2: a hit back taking Weakness). The code-gate halves are the ones the probe's
                     docstring and coin_lookahead.py's give (read in the code);
                     QUEUED and CUT can't tell a first-round site from a later-round one, and both engines build the first
                     round's: where the verdict rests on them alone (no RETURN) and the attack the probe's QUEUED path names
                     is not one of the later round's eight (or, with no attack named, neither list holds one of their
                     attackers), the line says so and the game is also counted under the STRICT reading, where
                     it reads UNEXPLAINED (the probe has no condition yet for round 2's plain-hit coin, Will, Trap Territory
                     and the rest: switch-2 PLAN (a), "still to do");
       NEEDS A JUDGMENT  the probe finds the queued choice only at the leaf (ply 3, a mixed frame);
       UNEXPLAINED   anything else: "movegen" or "state" with no counter; "length" with no counter at the extra tick, and
                     every "length" difference where the new game is the shorter one (tightened rule v2 leaves that case
                     open; the exact counters at the new game's last tick are printed beside it); a lookahead difference the
                     probe doesn't explain.
     vs_probe is not run: its gate (repair A's Confusion-first branch) is the first round's, on both engines.
     The probe also runs as a golden check where a game is on the board by a counter the probe looks for: at the last such
     tick, attack_return_weakness must read ret 1 and coin_queued_by_attack queued 0 (or cut 1). As in Oct 1's, it runs as a
     negative control at a mid-game tick of unchanged games (pairings 33-35, no Meowth on the board): nothing may be found.
     A probe that stops at the node limit having found nothing is run again at 600,000 nodes (validate_v2.py's rule).
  5. reports the share of changed games no exact counter explains, and the implied trace load for step 8: the switch-2 plan's
     step 8 is the last switch's 32 pairings (km3 500, k3 250 deals) and the Will rows (3 pairings, km3 500, k3 250): km3
     17,500 and k3 8,750 deals.
Usage: python3 classify_8b.py <work dir>   (writes the traces into the work dir; prints the report and writes
classify_output.txt and summary.json here)"""
import ast, gzip, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = Path(sys.argv[1])
sys.path.insert(0, str(HERE.parents[1] / "round2_readiness_2026-10-02"))
from tightened_rule_v2 import load_trace, first_difference, counter_hits, extra_tick_hits  # noqa: E402

BOTS = ("km3", "k3")
PAIRINGS = (32, 33, 34, 35, 36, 37)
OCT1 = (32, 33, 34, 35)
SEED_BASE = "23100000000"
SEARCH_PLIES = 3
RETRY_LIMIT = 600_000
STEP8_DEALS = {"km3": 17_500, "k3": 8_750}

# The exact counters, from the watch build's own coin script (run_8b.sh copied it from the tools revision).
script = (W / "instrument_coin_prevention_repair_2026-09-30.py").read_text(encoding="utf-8")
names = lambda var: ast.literal_eval(re.search(rf"^{var} = (\[.*?\])", script, re.S | re.M)[1])
REACH_PLAIN = tuple(n for n in names("R2_COUNTERS") if not n.startswith("offgate_") and n != "trap_territory_two_in_play")
REACH_KEYED = tuple(n for n in names("R2_KEYED") if not n.startswith("offgate_"))
REACH = REACH_PLAIN + REACH_KEYED
# The later coin round's sites, by attack title (the card text, lib/card.py): only these change between the two engines.
ROUND2_QUEUED = {"Wild Swing", "Wellspring Dance", "Tornado Shot", "Double Splash", "Triple Bombardment", "Mischievous Ring",
                 "Litter", "Double-Punching Family"}
# The cards that use them (printings), to say whether a pairing's lists can reach a later-round queued choice at all.
ROUND2_ATTACKERS = {"A4 045", "A4 215", "B2 048", "B3 051", "B1a 019", "B1a 020", "B1a 078", "B1a 084", "B4 077", "A4a 018",
                    "B2 127", "B2 189", "B2 202", "B4 231"}

pairs = {}
for line in open(HERE / "pairs_8b.tsv", encoding="utf-8").read().splitlines()[1:]:
    c = line.split("\t")
    pairs[int(c[0])] = (c[2], c[3], c[4], c[5])          # held_key, held_file, opponent, panel_file


def rows(path):
    return {(r["pairing"], r["i"]): r for r in map(json.loads, open(path))}


def reach_row(w):
    """The watch row with every keyed exact counter's ticks put together, in counter_hits' {"ticks"} form
    (coin_queued_by_attack: the later round's attacks only)."""
    out = dict(w)
    for name in REACH_KEYED:
        keep = lambda key: name != "coin_queued_by_attack" or key in ROUND2_QUEUED
        out[name] = {"ticks": sorted({t for key, ticks in w.get(name, {}).items() if keep(key) for t in ticks})}
    return out


def keys_at(w, hits):
    """For the keyed counters among `hits`, the keys that fired at those ticks (for the report)."""
    return {name: {key: [t for t in ticks if t in hits[name]] for key, ticks in w[name].items() if set(ticks) & set(hits[name])}
            for name in REACH_KEYED if name in hits}


def reaches_round2(pairing):
    """Whether either list of the pairing holds one of the later round's attackers."""
    _, held, _, opp = pairs[pairing]
    text = (W / "root" / held).read_text(encoding="utf-8") + (W / "root" / opp).read_text(encoding="utf-8")
    return any(re.search(rf"\b{re.escape(c)}\s*$", text, re.M) for c in ROUND2_ATTACKERS)


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"failed: {' '.join(cmd)}\n{p.stderr[-400:]}")
    return p.stdout


def trace(engine, bot, pairing, deals, tag=None):
    """vs_trace on one engine for some deals of one pairing; cached as a gzip file in the work dir."""
    path = W / f"trace_{tag or engine}_{bot}_{pairing}.jsonl.gz"
    if not path.exists():
        _, held, _, opp = pairs[pairing]
        out = run([str(W / f"bin_{engine}_vs_trace"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
                   "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot,
                   "--deals", ",".join(map(str, deals))], W / engine / "engine")
        with gzip.open(path, "wt") as f:
            f.write(out)
    return load_trace(path)


def probe(bot, pairing, deal, tick, limit=None):
    _, held, _, opp = pairs[pairing]
    out = run([str(W / "bin_probe_coin_probe_v2"), "--a", str(W / "root" / held), "--b", str(W / "root" / opp),
               "--seed-base", SEED_BASE, "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)]
              + (["--node-limit", str(limit)] if limit else []), W / "probe" / "engine")
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", out, re.M)
    r2 = re.search(r"^RESULT_P2 ret=(\S+)$", out, re.M)
    parse = lambda s: None if s == "none" else int(s)
    r = {"queued": parse(m[1]), "cut": parse(m[2]), "free": m[3] == "true", "ret": parse(r2[1])}
    # The attacks named on the shortest QUEUED paths (the attack chosen on the way, read from the path's own move list).
    block = re.search(r"^ *QUEUED: .*\n((?: {4}after .*\n?)+)", out, re.M)
    titles = sorted({t for line in (block[1].splitlines() if block else []) for t in re.findall(r'title: "([^"]+)"', line.split("] offers")[0])})
    if titles:
        r["queued_attacks"] = titles
    if "search stopped at" in out:
        r["truncated"] = True
        if limit is None and r["queued"] is None and r["cut"] is None and r["ret"] is None:
            return probe(bot, pairing, deal, tick, RETRY_LIMIT) | {"retried": RETRY_LIMIT}
    return r


def lookahead_verdict(c):
    """validate_v2.py's, with P2's RETURN beside the coin conditions (vs_probe not run)."""
    coin_found = c["queued"] is not None or c["cut"] is not None
    leaf_only = coin_found and c["queued"] == SEARCH_PLIES and not c["free"] and (c["cut"] is None or c["cut"] > SEARCH_PLIES)
    if c["ret"] is not None or (coin_found and not leaf_only):
        return "LOOKAHEAD ONLY, both halves hold"
    return "NEEDS A JUDGMENT" if leaf_only else "UNEXPLAINED"


report, summary, problems = [], {}, []
say = report.append
say(f"exact counters (REACH): {', '.join(REACH)}")
for bot in BOTS:
    old, new, watch, pinned = (rows(W / f"8b_{v}_{bot}.jsonl") for v in ("old", "new", "watch", "pinned"))
    oct1 = {k: r for k, r in rows(W / f"oct1_8b_new_{bot}.jsonl").items() if k[0] in OCT1}
    keys = sorted(old)
    want = [(p, i) for p in PAIRINGS for i in range(40)]
    for name, d in (("old", old), ("new", new), ("watch", watch), ("pinned", pinned)):
        if sorted(d) != want:
            problems.append(f"{bot} {name}: not exactly the 240 deals")
    pin_same = sum(pinned[k] == old[k] for k in keys)
    oct1_same = sum(oct1.get(k) == pinned[k] for k in keys if k[0] in OCT1)
    watch_same = sum(all(watch[k].get(f) == v for f, v in new[k].items()) for k in keys)
    seat_ok = sum(old[k]["first_seat"] == (0 if k[1] % 2 == 0 else 1) for k in keys)
    say(f"\n=== {bot}")
    say(f"checks: pinned official legality_scan v old built from source, every field: {pin_same} of {len(keys)} equal; "
        f"pinned v Oct 1's recorded rows (main's 5a18d31_8b_new_{bot}.jsonl), pairings 32-35, every field: {oct1_same} of "
        f"{len(oct1)} equal; watch v new on every field new records: {watch_same} of {len(keys)} equal; first seat by i's "
        f"parity: {seat_ok} of {len(keys)}")
    if pin_same != len(keys) or oct1_same != len(oct1) or len(oct1) != 160 or watch_same != len(keys) or seat_ok != len(keys):
        problems.append(f"{bot}: a file check failed")
    changed = [k for k in keys if any(new[k].get(f) != v for f, v in old[k].items())]
    moves_differ = [k for k in keys if new[k]["moves"] != old[k]["moves"]]
    say(f"changed games (new v old on any field old records): {len(changed)} of {len(keys)}; moves differ in {len(moves_differ)}")
    by_pairing = {p: [k[1] for k in changed if k[0] == p] for p in PAIRINGS}
    traces = {p: {e: trace(e, bot, p, by_pairing[p]) for e in ("old", "new")} for p in PAIRINGS if by_pairing[p]}
    verdicts, strict_only = {}, []
    for p in PAIRINGS:
        held_key, _, opp_key, _ = pairs[p]
        say(f"\npairing {p}, {held_key} v {opp_key}: {len(by_pairing[p])} changed of 40"
            + (f": {by_pairing[p]}" if by_pairing[p] else ""))
        for i in by_pairing[p]:
            (to, to_done), (tn, tn_done) = traces[p]["old"], traces[p]["new"]
            fp_ok = to_done[i]["moves"] == old[(p, i)]["moves"] and tn_done[i]["moves"] == new[(p, i)]["moves"]
            if not fp_ok:
                problems.append(f"{bot} pairing {p} i {i}: a trace's move fingerprint differs from its scan")
            a, b, w = to[i], tn[i], reach_row(watch[(p, i)])
            d = first_difference(a, b)
            mark = "" if fp_ok else "; TRACE FINGERPRINT MISMATCH"
            if d["kind"] == "length":
                hits = extra_tick_hits(w, REACH, d)
                if hits:
                    verdict, note = "ON THE BOARD", f"; exact counters at the new game's first extra tick {d['k']}: {hits}"
                elif d.get("longer") in ("old", None):
                    last = len(b) - 1
                    at_last = {n: [last] for n in REACH if last in w[n]["ticks"]}
                    verdict = "UNEXPLAINED"
                    what = ("the new game is the shorter one (the open case of tightened rule v2)" if d.get("longer") == "old"
                            else "the two traces are the same, tick for tick, and as long: only the last move's effect differs")
                    note = f"; {what}; exact counters at the new game's last tick {last} (turn {b[last]['turn']}): {at_last or 'none'}"
                else:
                    verdict, note = "UNEXPLAINED", "; no exact counter at the new game's first extra tick"
                say(f"  i = {i:2d}: {d['detail']}, longer: {d.get('longer')}{note}{mark} => {verdict}")
                verdicts[(p, i)] = (verdict, d)
                continue
            k, cause = d["k"], d["cause"]
            strict = counter_hits(w, REACH, b, d)
            later = counter_hits(w, REACH, b, d, after=True)
            keyed = keys_at(watch[(p, i)], strict)
            head = (f"  i = {i:2d}: first difference at tick {k} (turn {b[k]['turn']}; {d['kind']}: {d['detail']}; cause tick "
                    f"{cause}); exact counters at or before it in its turn, or at the cause tick: {strict or 'none'}"
                    + (f" (by key: {keyed})" if keyed else "")
                    + (f"; same turn after it (never an explanation): {later}" if later else "") + mark)
            if strict:
                verdict, gold = "ON THE BOARD", ""
                for name, ok_if in (("attack_return_weakness", lambda g: g["ret"] == 1),
                                    ("coin_queued_by_attack", lambda g: g["queued"] == 0 or g["cut"] == 1)):
                    if name in strict:
                        t = max(strict[name])
                        g = probe(bot, p, i, t)
                        ok = ok_if(g)
                        gold += f"; golden probe for {name} at tick {t}: {g} ({'on the table' if ok else 'NOT ON THE TABLE'})"
                        problems += [] if ok else [f"{bot} pairing {p} i {i}: golden probe for {name} not on the table"]
                say(f"{head}{gold} => {verdict}")
            elif d["kind"] == "lookahead":
                c = probe(bot, p, i, k)
                verdict = lookahead_verdict(c)
                caveat = ""
                named = set(c.get("queued_attacks", []))
                round2 = bool(named & ROUND2_QUEUED) if named else reaches_round2(p)
                if verdict.startswith("LOOKAHEAD") and c["ret"] is None and not round2:
                    strict_only.append((p, i))
                    caveat = ("; CAVEAT: only QUEUED/CUT, and the coin choice found is a first-round site both engines build "
                              f"({'the path names ' + ', '.join(sorted(named)) if named else 'neither list holds a later-round attacker'}): "
                              "under the strict reading, UNEXPLAINED")
                say(f"{head}; coin_probe v2 at tick {k}: {c}{caveat} => {verdict}")
            else:
                verdict = "UNEXPLAINED"
                say(f"{head} => {verdict}")
            verdicts[(p, i)] = (verdict, d)
    # Negative controls, as Oct 1's: in unchanged games of pairings 33-35, the first tick from 8 on with two or more offered
    # moves and no Meowth in play on either side; nothing may be found there (QUEUED, CUT or RETURN). Two per bot.
    unchanged = [k for k in keys if k not in changed]
    controls, found = 0, 0
    for (p, i) in unchanged:
        if found == 2 or p not in (33, 34, 35):
            continue
        tr, _ = trace("old", bot, p, [i], tag=f"control_{i}")
        tick = next((t for t, r in enumerate(tr[i][:60]) if t >= 8 and r["n"] > 1 and "Meowth" not in json.dumps(r["board"])), None)
        if tick is None:
            continue
        g = probe(bot, p, i, tick)
        nothing = g["queued"] is None and g["cut"] is None and g["ret"] is None
        say(f"control (coin_probe v2), pairing {p} i {i} tick {tick}, an unchanged game: {g} "
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
    say(f"\n{bot} verdicts: {json.dumps(tally)}; of the lookahead ones, resting only on a first-round coin site (UNEXPLAINED "
        f"under the strict reading): {len(strict_only)}; controls that found something: {controls}")
    summary[bot] = {"games": len(keys), "changed": len(changed), "no_counter": len(no_counter), "hand": len(hand),
                    "hand_strict": len(hand) + len(strict_only), "strict_only_games": strict_only,
                    "tally": tally, "no_counter_games": no_counter, "hand_games": hand,
                    "per_pairing": {p: {"changed": len(by_pairing[p]),
                                        "no_counter": sum(1 for k in no_counter if k[0] == p),
                                        "hand": sum(1 for k in hand if k[0] == p)} for p in PAIRINGS}}

say("\n=== the share and the implied trace load for step 8")
tot_g = sum(s["games"] for s in summary.values())
tot_c = sum(s["changed"] for s in summary.values())
tot_n = sum(s["no_counter"] for s in summary.values())
tot_h = sum(s["hand"] for s in summary.values())
say(f"deals: {tot_g} (old v new; {tot_g * 3} games over the three builds, and the pinned check); changed: {tot_c}; no exact "
    f"counter explains on the board: {tot_n}; of those, settled by the probe (lookahead only, both halves): {tot_n - tot_h}; "
    f"needing a hand trace or a judgment (UNEXPLAINED or NEEDS A JUDGMENT): {tot_h}")
load_n = sum(summary[b]["no_counter"] / summary[b]["games"] * STEP8_DEALS[b] for b in BOTS)
load_h = sum(summary[b]["hand"] / summary[b]["games"] * STEP8_DEALS[b] for b in BOTS)
load_s = sum(summary[b]["hand_strict"] / summary[b]["games"] * STEP8_DEALS[b] for b in BOTS)
say("per bot: " + "; ".join(f"{b}: changed {summary[b]['changed']}/{summary[b]['games']}, no counter {summary[b]['no_counter']}, "
                             f"hand {summary[b]['hand']}" for b in BOTS))
say(f"implied for step 8 (km3 17,500 and k3 8,750 deals; each bot's share of its 240 deals times its step 8 deals):")
say(f"  changed games no exact counter explains: {load_n:.0f}")
say(f"  of them needing a hand trace or a judgment after the probe: {load_h:.0f}; under the strict reading (a first-round coin "
    f"site doesn't explain a change): {load_s:.0f}")
say(f"TRACE LOAD {load_h:.0f}   (the line for trace_load.txt, with the commit of these results; strict reading {load_s:.0f})")
say(f"\nproblems: {problems or 'none'}")
print("\n".join(report))
(HERE / "classify_output.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
json.dump(summary, open(HERE / "summary.json", "w"), indent=1, default=str)
sys.exit(1 if problems else 0)
