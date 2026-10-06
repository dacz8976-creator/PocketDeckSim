#!/usr/bin/env python3
"""Second reader: independent recount of the kx3 exam from games.jsonl."""
import json, math, sys, collections, statistics

BASE = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/"
EXAM = BASE + "strength_2026-10-05_kx3_exam/"
DEV = BASE + "strength_2026-10-03_kx3_dev/"


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def score(w):
    return {"deck": 1.0, "tie": 0.5, "opp": 0.0}[w]


def ci(xs, scale=1.0):
    n = len(xs)
    m = sum(xs) / n
    sd = statistics.stdev(xs) if n > 1 else float("nan")
    h = 1.96 * sd / math.sqrt(n)
    return m * scale, h * scale, sd * scale, n


def fmt(xs, scale=1.0, nd=1):
    m, h, sd, n = ci(xs, scale)
    return f"{m:+.{nd}f} ± {h:.{nd}f} (sd {sd:.{nd+1}f}, n {n})"


def first_attack(g):
    log = g.get("log") or []
    for e in log:
        if str(e.get("a", "")).startswith("Attack:"):
            return e["o"], True
    if not log:
        return EMPTY_LOG_VALUE, False
    return max(e["o"] for e in log), False


EMPTY_LOG_VALUE = 0  # empty log: no own turn logged; counted as own turn 0 (variant reported below)


def last_own(g):
    log = g.get("log") or []
    return max(e["o"] for e in log) if log else None


def main():
    man = json.load(open(EXAM + "manifest.json", encoding="utf-8"))
    games = load(EXAM + "games.jsonl")
    decks = [d["name"] for d in man["decks"]]
    opps = [o["name"] for o in man["opponents"]]
    print("== 1. completeness ==")
    print("records", len(games), "planned", man["planned_games"])
    print("winner values", collections.Counter(g["winner"] for g in games))
    print("arm values", collections.Counter(g["arm"] for g in games))
    keys = collections.Counter((g["deck"], g["opp"], g["seed"], g["seat"], g["arm"]) for g in games)
    dups = [k for k, c in keys.items() if c > 1]
    print("duplicate (deck,opp,seed,seat,arm):", len(dups))
    kfield = collections.Counter(g.get("key") for g in games)
    print("duplicate key field:", sum(1 for c in kfield.values() if c > 1))
    # planned set
    planned = set()
    for di, d in enumerate(decks):
        for oi, o in enumerate(opps):
            p = di * 1000 + oi
            for i in range(man["deals"]):
                for s in man["seats"]:
                    for arm in ("X", "ref"):
                        planned.add((d, o, man["seed_base"] + p * man["pair_stride"] + i, s, arm))
    actual = set(keys)
    print("planned", len(planned), "missing", len(planned - actual), "extra", len(actual - planned))
    # deal field vs seed
    bad_deal = 0
    for g in games:
        di, oi = decks.index(g["deck"]), opps.index(g["opp"])
        exp = man["seed_base"] + (di * 1000 + oi) * man["pair_stride"] + g["deal"]
        if exp != g["seed"]:
            bad_deal += 1
    print("seed != base + p*stride + deal:", bad_deal)
    # pairs
    by = {}
    for g in games:
        by[(g["deck"], g["opp"], g["seed"], g["seat"], g["arm"])] = g
    pairs = []
    for (d, o, sd, st, arm), g in by.items():
        if arm != "X":
            continue
        r = by.get((d, o, sd, st, "ref"))
        if r is not None:
            pairs.append((g, r))
    print("complete pairs", len(pairs))
    # same deal checks
    diff_first = sum(1 for x, r in pairs if x["first"] != r["first"])
    diff_deal = sum(1 for x, r in pairs if x["deal"] != r["deal"])
    # first decision: number of options at first logged decision (depends on opening hand only)
    def first_n(g):
        log = g.get("log") or []
        return (log[0].get("n"), log[0].get("o"), log[0].get("t")) if log else None
    diff_n = sum(1 for x, r in pairs if first_n(x) != first_n(r))
    print("pairs with different first player:", diff_first, "| deal idx:", diff_deal,
          "| first decision (n options, o, t):", diff_n)
    # setup decisions identical up to first choice? compare set of o=0 Place labels count
    print("first player counts (X arm):", collections.Counter(x["first"] for x, r in pairs))

    print("\n== 4. sanity ==")
    print("pilot_deck by arm:", collections.Counter((g["arm"], g["pilot_deck"]) for g in games))
    print("pilot_opp by arm:", collections.Counter((g["arm"], g["pilot_opp"]) for g in games))
    print("decks in games == manifest:", sorted(set(g["deck"] for g in games)) == sorted(decks),
          "| opps:", sorted(set(g["opp"] for g in games)) == sorted(opps))
    print("games per deck:", collections.Counter(g["deck"] for g in games).most_common(1),
          min(collections.Counter(g["deck"] for g in games).values()))
    print("seats:", collections.Counter(g["seat"] for g in games), "deals:", collections.Counter(g["deal"] for g in games))
    print("seed range", min(g["seed"] for g in games), max(g["seed"] for g in games))
    nolog = [g for g in games if not g.get("log")]
    print("games with empty log:", len(nolog))
    for g in nolog:
        print("   ", {k: g[k] for k in ("arm", "deck", "opp", "seed", "seat", "first", "winner", "turns", "plies", "points")},
              "moves_deck n", g["moves_deck"]["n"], "moves_opp n", g["moves_opp"]["n"])
        other = by.get((g["deck"], g["opp"], g["seed"], g["seat"], "ref" if g["arm"] == "X" else "X"))
        print("     partner:", {k: other[k] for k in ("arm", "winner", "turns", "first")}, "log len", len(other["log"]),
              "first atk", first_attack(other))
    # o vs t consistency: own turn o at global t
    bad_ot = 0
    for g in games:
        for e in g.get("log") or []:
            if e["o"] == 0:
                continue
            exp_t = 2 * e["o"] - 1 if g["first"] == "deck" else 2 * e["o"]
            if e["t"] != exp_t:
                bad_ot += 1
    print("log entries where t != own-turn mapping:", bad_ot)

    print("\n== 2. score ==")
    D = [score(x["winner"]) - score(r["winner"]) for x, r in pairs]
    print("pooled d (points):", fmt(D, 100))
    print("diff counts", collections.Counter(D))
    winX = [score(x["winner"]) for x, r in pairs]
    winR = [score(r["winner"]) for x, r in pairs]
    print(f"score rate X {100*sum(winX)/len(winX):.2f}  ref {100*sum(winR)/len(winR):.2f}")
    print("winner counts X", collections.Counter(x["winner"] for x, r in pairs),
          "ref", collections.Counter(r["winner"] for x, r in pairs))
    perdeck = collections.defaultdict(list)
    for (x, r), dd in zip(pairs, D):
        perdeck[x["deck"]].append(dd)
    means = [sum(v) / len(v) for v in perdeck.values()]
    eq = sum(means) / len(means)
    # interval variants for equal-weight
    se_a = math.sqrt(sum(statistics.variance(v) / len(v) for v in perdeck.values())) / len(perdeck)
    se_b = statistics.stdev(means) / math.sqrt(len(means))
    print(f"equal-deck-weight: {100*eq:+.2f}  (±{196*se_a:.2f} from per-deck var; ±{196*se_b:.2f} from sd of deck means)")
    for d in decks:
        v = perdeck[d]
        sX = sum(score(x["winner"]) for x, r in pairs if x["deck"] == d) / len(v)
        sR = sum(score(r["winner"]) for x, r in pairs if x["deck"] == d) / len(v)
        print(f"  {d:34s} {fmt(v, 100)}  X {100*sX:.1f}% ref {100*sR:.1f}%")
    print("by first player:")
    for who in ("deck", "opp"):
        v = [dd for (x, r), dd in zip(pairs, D) if x["first"] == who]
        print(f"  deck {'first' if who=='deck' else 'second'}: {fmt(v, 100)}")
    print("by seat:")
    for s in (0, 1):
        v = [dd for (x, r), dd in zip(pairs, D) if x["seat"] == s]
        print(f"  seat {s}: {fmt(v, 100)}")
    m, h, sdv, n = ci(D)
    for target in (0.03, 0.05):
        need = (1.96 * sdv / target) ** 2
        print(f"  pairs needed for ±{target*100:.0f}: {need:.0f} total (≈{need-n:.0f} more pairs, {(need-n)/(len(decks)*len(opps)*2):.1f} more deals per pair)")
    # wall time / decisions per game per arm (deck player)
    for arm in ("X", "ref"):
        gs = [g for g in games if g["arm"] == arm]
        print(f"  arm {arm}: wall_s mean {statistics.mean(g['wall_s'] for g in gs):.2f}, "
              f"deck decisions/game {statistics.mean(len(g['log']) for g in gs):.1f}, "
              f"moves_deck.total_s mean {statistics.mean(g['moves_deck']['total_s'] for g in gs):.3f}")

    print("\n== 3. groups ==")
    ref_turns = collections.defaultdict(list)
    for x, r in pairs:
        ref_turns[r["deck"]].append(r["turns"])
    rank = sorted(decks, key=lambda d: statistics.mean(ref_turns[d]))
    for i, d in enumerate(rank):
        print(f"  rank {i+1:2d} {d:34s} ref mean turns {statistics.mean(ref_turns[d]):.3f}")
    fast = rank[:4]
    setup = rank[-4:]
    if "07-skarmory-stall" not in setup:
        # deck 07 forced in; the next-longest (shortest member of the would-be setup group) moves to the middle
        setup_sorted = sorted(setup, key=lambda d: statistics.mean(ref_turns[d]))
        dropped = setup_sorted[0]
        setup = [d for d in setup if d != dropped] + ["07-skarmory-stall"]
        if "07-skarmory-stall" in fast:
            fast = [d for d in fast if d != "07-skarmory-stall"]
            print("  NOTE: 07 was in the fast group; fast group now has", len(fast))
        print("  07 forced into setup; moved to middle:", dropped)
    middle = [d for d in decks if d not in fast and d not in setup]
    groups = {"fast": fast, "middle": middle, "setup": setup}
    for gname, members in groups.items():
        print(f"  {gname}: {members}")

    def metrics(sel_pairs):
        sc = [score(x["winner"]) - score(r["winner"]) for x, r in sel_pairs]
        tu = [x["turns"] - r["turns"] for x, r in sel_pairs]
        fa = [first_attack(x)[0] - first_attack(r)[0] for x, r in sel_pairs]
        return sc, tu, fa

    for gname, members in list(groups.items()) + [("all", decks)]:
        sp = [(x, r) for x, r in pairs if x["deck"] in members]
        sc, tu, fa = metrics(sp)
        noatkX = sum(1 for x, r in sp if not first_attack(x)[1])
        noatkR = sum(1 for x, r in sp if not first_attack(r)[1])
        print(f"  {gname:6s} score {fmt(sc, 100)}")
        print(f"         turns {fmt(tu, 1, 2)}   [X {statistics.mean(x['turns'] for x,r in sp):.2f} ref {statistics.mean(r['turns'] for x,r in sp):.2f}]")
        print(f"         first-attack own turn {fmt(fa, 1, 2)}   [X {statistics.mean(first_attack(x)[0] for x,r in sp):.2f} ref {statistics.mean(first_attack(r)[0] for x,r in sp):.2f}; no-attack games X {noatkX} ref {noatkR}]")
    print("  per deck:")
    for d in rank:
        sp = [(x, r) for x, r in pairs if x["deck"] == d]
        sc, tu, fa = metrics(sp)
        print(f"   {d:34s} score {fmt(sc,100)} | turns {fmt(tu,1,2)} | 1st atk {fmt(fa,1,2)}")

    # extras for the line-by-line comparison
    print("\n== extras ==")
    atk_bad = 0
    atk_n = 0
    kinds = collections.Counter()
    for g in games:
        for e in g.get("log") or []:
            if e["o"] == 0:
                continue
            exp_t = 2 * e["o"] - 1 if g["first"] == "deck" else 2 * e["o"]
            if e["t"] != exp_t:
                kinds[str(e["a"]).split(":")[0]] += 1
            if str(e["a"]).startswith("Attack:"):
                atk_n += 1
                if e["t"] != exp_t:
                    atk_bad += 1
    print("Attack entries", atk_n, "with t off the own-turn mapping:", atk_bad, "| off-mapping kinds:", kinds.most_common(6))
    print("per deck, by who went first (deck first / deck second):")
    for d in decks:
        a = [dd for (x, r), dd in zip(pairs, D) if x["deck"] == d and x["first"] == "deck"]
        b = [dd for (x, r), dd in zip(pairs, D) if x["deck"] == d and x["first"] == "opp"]
        print(f"   {d:34s} {fmt(a,100)} | {fmt(b,100)}")
    MYPAIRS = {}
    print("per pair rows: compared with REPORT.md table below")
    for d in decks:
        for o in opps:
            sp = [(x, r) for x, r in pairs if x["deck"] == d and x["opp"] == o]
            v = [score(x["winner"]) - score(r["winner"]) for x, r in sp]
            m, h, _, n = ci(v, 100)
            sX = 100 * sum(score(x["winner"]) for x, r in sp) / n
            sR = 100 * sum(score(r["winner"]) for x, r in sp) / n
            mine = f"| {d} | {o} | {n} | {sX:.1f}% | {sR:.1f}% | {m:+.1f} ± {h:.1f} |"
            MYPAIRS[(d, o)] = mine
    for arm in ("X", "ref"):
        gs = sorted(g["wall_s"] for g in games if g["arm"] == arm)
        n = len(gs)
        ms = sorted(x for g in games if g["arm"] == arm for x in g["moves_deck"]["ms"])
        mo = sorted(x for g in games if g["arm"] == arm for x in g["moves_opp"]["ms"])
        print(f"  arm {arm}: wall mean {statistics.mean(gs):.2f} median {statistics.median(gs):.2f} max {gs[-1]:.2f}; "
              f"deck ms/decision mean {statistics.mean(ms):.1f} median {statistics.median(ms):.1f} max {ms[-1]:.1f}; "
              f"opp decisions/game {statistics.mean(g['moves_opp']['n'] for g in games if g['arm']==arm):.1f}, "
              f"opp ms mean {statistics.mean(mo):.1f}")
    rep = open(EXAM + "REPORT.md", encoding="utf-8").read().splitlines()
    theirs = {}
    for line in rep:
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) == 6 and parts[1].startswith("t-") and parts[2] == "6":
            theirs[(parts[0], parts[1])] = "| " + " | ".join(parts) + " |"
    mism = [(k, MYPAIRS[k], theirs.get(k)) for k in MYPAIRS if MYPAIRS[k] != theirs.get(k)]
    print(f"  pair rows: mine {len(MYPAIRS)}, REPORT {len(theirs)}, differing {len(mism)}")
    for k, a, b in mism:
        print("    MINE ", a, "\n    THEIRS", b)
    ti = collections.defaultdict(lambda: [0, 0])
    for g in games:
        if any("Thieving Incisors" in str(e.get("a", "")) for e in g.get("log") or []):
            ti[(g["deck"], g["arm"])][0] += 1
        ti[(g["deck"], g["arm"])][1] += 1
    print("  games with a 'Thieving Incisors' label:",
          {k: f"{v[0]}/{v[1]}" for k, v in sorted(ti.items()) if v[0]})

    # dev run comparison
    print("\n== dev run comparison ==")
    try:
        dg = load(DEV + "games.jsonl")
    except Exception as e:
        print("dev games not readable:", e)
        return
    dby = {}
    for g in dg:
        dby[(g["deck"], g["opp"], g["seed"], g["seat"], g["arm"])] = g
    dpairs = [(g, dby[(k[0], k[1], k[2], k[3], "ref")]) for k, g in dby.items()
              if k[4] == "X" and (k[0], k[1], k[2], k[3], "ref") in dby]
    print("dev records", len(dg), "pairs", len(dpairs), "decks", sorted(set(g["deck"] for g in dg)))
    dd = sorted(set(g["deck"] for g in dg))
    def pick(prefixes):
        return [d for d in dd if any(d.startswith(p) for p in prefixes)]
    dgroups = {"aggro": pick(["09", "06", "10"]), "setup": pick(["03", "01", "05"]),
               "draftA": [d for d in dd if "draft-A" in d]}
    for gname, members in dgroups.items():
        sp = [(x, r) for x, r in dpairs if x["deck"] in members]
        if not sp:
            print(" ", gname, "none", members)
            continue
        sc, tu, fa = metrics(sp)
        print(f"  {gname} {members}")
        print(f"     score {fmt(sc,100)} | turns {fmt(tu,1,2)} | 1st atk {fmt(fa,1,2)}")
    sc, tu, fa = metrics(dpairs)
    print(f"  all dev: score {fmt(sc,100)} | turns {fmt(tu,1,2)} | 1st atk {fmt(fa,1,2)}")
    for d in dd:
        sp = [(x, r) for x, r in dpairs if x["deck"] == d]
        sc, tu, fa = metrics(sp)
        print(f"   {d:36s} score {fmt(sc,100)} | turns {fmt(tu,1,2)} | 1st atk {fmt(fa,1,2)}")
    print("  dev pilots:", collections.Counter((g["arm"], g["pilot_deck"], g["pilot_opp"]) for g in dg))


if __name__ == "__main__":
    main()
