#!/usr/bin/env python3
"""The combined run's reading (fixed before any game): the candidate kx3 against the frozen kx3, paired on the
development run's own deals.

  python3 -P pair_combined.py RUN_DIR      (from the repository root)

RUN_DIR is the combined strength run (pilot = the candidate, reference km3) whose manifest reproduces the development
run's deals (rl/results/strength_2026-10-03_kx3_dev, "the dev run"). Its X arm is the candidate; the dev run's X arm on
the same key (deck, opponent, deal, seat) is the frozen kx3 (d513e37b, pilot "kx3").

1. Build check: every reference game (km3 v km3) must equal the dev run's game for game and decision for decision
   (timings aside). If one differs, the pairing is void and nothing below is read.
2. Primary: candidate - frozen in game score (win 1, tie 1/2, loss 0) on the same key, mean +- 1.96 sd / sqrt(n),
   pooled over every pair, and every deck weighted equally; then per group (the dev run's own groups: fast 09, 06, 10;
   setup 03, 01, 05; draft A in the middle) and per deck, with how many pairs differ at all (any logged decision) and
   which decks are worse beyond noise (interval entirely below zero; REPORTED, not a veto).
3. Pace, paired the same way: turns per game and the deck's first-attack own turn (no attack: its last own turn).
4. Context: candidate - km3 and frozen - km3 on the same keys.
5. Time: kx3 games only (wall seconds per game, both arms' kx3 games, per deck), and the run's kx3 games v its total
   games.
With fewer games than planned the output says "PARTIAL: information only" at the top; the decision is read only on
the complete run.
"""
import json, math, os, sys, statistics as st
from collections import defaultdict

DEV = "rl/results/strength_2026-10-03_kx3_dev/games.jsonl"
GROUPS = {"09-mega-manectric-heliolisk": "fast", "06-mega-blaziken-tournament-list": "fast", "10-xatu-oricorio-tr-weezing": "fast",
          "03-wailord-indeedee-wall": "setup", "01-muk-glimmora-kingambit-regigigas": "setup", "05-indeedee-stoutland": "setup"}
SC = {"deck": 1.0, "tie": 0.5, "opp": 0.0}


def load(p):
    return {x["key"]: x for x in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip())}


def facts(x):
    return (x["seed"], x["first"], x["winner"], x["points"], x["turns"], x["plies"], x["moves_deck"]["n"], x["moves_opp"]["n"],
            [{k: v for k, v in d.items() if k != "ms"} for d in (x.get("log") or [])])


def first_attack(g):
    log = g.get("log") or []
    own = [d.get("o", 0) for d in log]
    att = [d.get("o", 0) for d in log if str(d.get("a", "")).startswith("Attack:")]
    return min(att) if att else (max(own) if own else 0)


def ci(v, scale=100.0, fmt="{:+.1f} +- {:.1f}"):
    n = len(v)
    if n == 0:
        return "n 0"
    m = st.mean(v)
    h = 1.96 * st.stdev(v) / math.sqrt(n) if n > 1 else float("nan")
    return fmt.format(scale * m, scale * h) + f" (n {n})"


def below_zero(v):
    if len(v) < 2:
        return False
    return st.mean(v) + 1.96 * st.stdev(v) / math.sqrt(len(v)) < 0


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run = sys.argv[1]
    man = json.load(open(os.path.join(run, "manifest.json"), encoding="utf-8"))
    dev = load(DEV)
    games = load(os.path.join(run, "games.jsonl"))
    planned = man.get("planned_games")
    if planned and len(games) < planned:
        print(f"PARTIAL: information only ({len(games)} of {planned} games; the decision is read on the complete run)\n")
    same = diff = 0
    for k, g in sorted(games.items()):
        if k not in dev:
            print("NOT A DEV-RUN DEAL:", k)
            diff += 1
        elif g["arm"] == "ref":
            if facts(g) == facts(dev[k]):
                same += 1
            else:
                diff += 1
                print("DIFFERS FROM THE DEV RUN:", k)
    print(f"build check: {same} reference games replay the dev run exactly, {diff} differ")
    if diff:
        print("THE PAIRING IS VOID: this build does not replay the dev run; candidate - frozen can't be read against it")
        return
    rows = defaultdict(lambda: defaultdict(list))
    secs = defaultdict(lambda: {"cand": [], "frozen": []})
    for k, g in sorted(games.items()):
        if g["arm"] != "X":
            continue
        f, kr = dev[k], k[: -len("X")] + "ref"
        d = g["deck"]
        for grp in ("all", GROUPS.get(d, "middle"), d):
            r = rows[grp]
            r["s"].append(SC[g["winner"]] - SC[f["winner"]])
            r["t"].append(g["turns"] - f["turns"])
            r["fa"].append(first_attack(g) - first_attack(f))
            r["differ"].append(facts(g) != facts(f))
            if kr in games:
                r["ck"].append(SC[g["winner"]] - SC[games[kr]["winner"]])
            r["fk"].append(SC[f["winner"]] - SC[dev[kr]["winner"]])
        secs[d]["cand"].append(g["wall_s"])
        secs[d]["frozen"].append(f["wall_s"])
    decks = [d for d in rows if d not in ("all", "fast", "setup", "middle")]
    eq = [st.mean(rows[d]["s"]) for d in decks]
    print(f"\nPRIMARY, pooled: candidate - frozen {ci(rows['all']['s'])} points; every deck weighted equally "
          f"{100 * st.mean(eq):+.1f} points over {len(eq)} decks")
    for grp in ["all", "fast", "setup", "middle"] + sorted(decks):
        if grp not in rows:
            continue
        r = rows[grp]
        label = grp if grp in ("all", "fast", "setup", "middle") else f"{grp} ({GROUPS.get(grp, 'middle')})"
        print(f"\n{label}: candidate - frozen {ci(r['s'])} points; pairs that differ at all {sum(r['differ'])} of {len(r['differ'])}"
              + ("  WORSE BEYOND NOISE (reported, not a veto)" if grp in decks and below_zero(r["s"]) else ""))
        print(f"  pace: turns per game {ci(r['t'], 1.0, '{:+.2f} +- {:.2f}')}; first-attack own turn {ci(r['fa'], 1.0, '{:+.2f} +- {:.2f}')}")
        print(f"  context: candidate - km3 {ci(r['ck'])}; frozen - km3 {ci(r['fk'])}")
    print("\nTime, kx3 games only (wall seconds per game on the laptop, 2 games at a time):")
    tc = tf = 0.0
    for d in decks:
        c, f = secs[d]["cand"], secs[d]["frozen"]
        tc += sum(c); tf += sum(f)
        print(f"  {d}: candidate {st.mean(c):.0f} s, frozen {st.mean(f):.0f} s, x{st.mean(c) / st.mean(f):.2f} ({len(c)} kx3 games)")
    nx = sum(1 for g in games.values() if g["arm"] == "X")
    print(f"  all: candidate x{tc / tf:.2f} the frozen kx3's time; this run: {nx} kx3 games + {len(games) - nx} km3 games = {len(games)} games")


if __name__ == "__main__":
    main()
