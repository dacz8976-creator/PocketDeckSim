#!/usr/bin/env python3
"""Reads kt's Dustin-deck A/B (run_kt_ab.sh) into a plain table per deck.

    python3 read_kt_ab.py [--dir DIR] [--build ec7e1a8] [--decks 07,05,11,01,03] [--arms kog3,kt3,kta3] [--by-opponent]

Reads DIR/<build>_ab_d<deck>_<arm>.jsonl (one line per game, written by kt_ab_play.py). For each deck:
  - win rate by arm (the deck's wins; a draw is not a win), and for every arm but the first (kog3, the comparator) the
    paired difference against kog3 on the same deals (same seed, same seat): mean of (win in this arm - win in kog3's),
    in points, with its 95% interval (normal approximation on the per-deal differences, 1.96 x sd / sqrt(n)), and
    McNemar's exact test on the discordant deals (the registration: "with McNemar beside the paired difference");
  - "moves differ": the share of paired games whose move fingerprint differs from kog3's (the arm's footprint on
    these deals);
  - Jasmine: turns on which she was a legal play ("offered", the census's denominator), turns played, the rate;
  - Metal Core Barrier, Steel Apron, Heavy Helmet: turns offered / played, and where they were attached: on a
    qualifying holder or not (Barrier and Apron need an [M] holder, Heavy Helmet a holder with Retreat Cost 3 or more),
    and how many on the Active.
Then all decks together (paired differences over every game). Nothing here is a verdict; it reads what the games show.
"""
import argparse, json, math, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = ("Metal Core Barrier", "Steel Apron", "Heavy Helmet")
Z = 1.96


def mcnemar_exact(b, c):
    """Two-sided exact p for b arm-only wins against c comparator-only wins (b + c discordant deals)."""
    n = b + c
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, j) for j in range(min(b, c) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def load(path):
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    return {(r["opp"], r["seat"], r["seed"]): r for r in rows}


def paired(base, arm):
    """The arm against the comparator on the deals both played, or None when they share none."""
    keys = sorted(set(base) & set(arm))
    d = [int(arm[k]["won"]) - int(base[k]["won"]) for k in keys]
    n = len(d)
    if n == 0:
        return None
    mean = sum(d) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in d) / (n - 1)) if n > 1 else float("nan")
    return dict(n=n, b=sum(x == 1 for x in d), c=sum(x == -1 for x in d), mean=mean,
                half=Z * sd / math.sqrt(n) if n > 1 else float("nan"),
                differ=sum(base[k]["moves"] != arm[k]["moves"] for k in keys), unpaired=len(set(base) ^ set(arm)))


def pct(x, d=1):
    return f"{100 * x:.{d}f}%"


def wins_of(rows):
    return sum(r["won"] for r in rows.values())


def offered_played(data, name):
    """Turns the card was a legal play / turns it was played, summed over the arm's games."""
    off = pl = 0
    for r in data.values():
        o, p = r["plays"].get(name, (0, 0))
        off, pl = off + o, pl + p
    return off, pl


def placements(data, tool):
    """(attached, on a qualifying holder, on the Active, qualifying and on the Active)."""
    rows = [t for r in data.values() for t in r["tools"] if t[0] == tool]
    return (len(rows), sum(bool(t[6]) for t in rows), sum(t[2] == "Active" for t in rows),
            sum(bool(t[6]) and t[2] == "Active" for t in rows))


def diff_text(pr):
    lo, hi = pr["mean"] - pr["half"], pr["mean"] + pr["half"]
    return f"{100 * pr['mean']:+.1f} points ({100 * lo:+.1f} to {100 * hi:+.1f})"


def deck_report(deck, arms, files, by_opp, out):
    loaded = {a: load(p) for a, p in files.items() if os.path.exists(p)}
    if not loaded:
        out += [f"== Deck {deck}: no outputs yet", ""]
        return {}
    base_arm = arms[0]
    base = loaded.get(base_arm)
    any_rows = next(iter(loaded.values()))
    opps = sorted({k[0] for k in any_rows})
    out.append(f"== Deck {deck}: against the {len(opps)} panel lists ({next(iter(any_rows.values()))['opp_pilot']} on the lists)")
    out.append(f"{'arm':6} {'games':>5} {'wins':>5} {'win rate':>8}   {'paired vs ' + base_arm + ' (95% interval)':<40}"
               f"{'McNemar p':>10}  {'arm-only / ' + base_arm + '-only':>18}  {'moves differ':>12}")
    for a in arms:
        if a not in loaded:
            out.append(f"{a:6} not run yet")
            continue
        d = loaded[a]
        line = f"{a:6} {len(d):5d} {wins_of(d):5d} {pct(wins_of(d) / len(d)):>8}   "
        if a == base_arm:
            line += "(comparator)"
        elif base is None:
            line += f"(no {base_arm} file to pair with)"
        elif (pr := paired(base, d)) is None:
            line += f"no games in common with {base_arm}"
        else:
            line += (f"{diff_text(pr):<40}{mcnemar_exact(pr['b'], pr['c']):10.3f}  {str(pr['b']) + ' / ' + str(pr['c']):>18}  "
                     f"{pct(pr['differ'] / pr['n']):>12}" + (f"  [{pr['unpaired']} games unpaired]" if pr["unpaired"] else ""))
        out.append(line)
    out.append("")
    out.append("Jasmine and the damage-cut Tools (turns the deck could play the card / turns it did; where each Tool was attached):")
    lines = []
    for name in ("Jasmine",) + TOOLS:
        for a in arms:
            if a not in loaded:
                continue
            off, pl = offered_played(loaded[a], name)
            att, qual, active, qa = placements(loaded[a], name)
            if not (off or att):
                continue
            rate = f"{pl} ({pct(pl / off)})" if off else f"{pl}"
            if name == "Jasmine":
                lines.append(f"    {a:6} Jasmine: offered {off} turns, played {rate}")
            else:
                lines.append(f"    {a:6} {name}: offered {off} turns, played {rate}; attached {att}: on a qualifying holder "
                             f"{qual}" + (f" ({pct(qual / att, 0)})" if att else "") + f", on the Active {active}, qualifying and Active {qa}")
    out.extend(lines or ["    (this deck plays none of them)"])
    if by_opp:
        out += ["", f"    win rate by opponent and arm", f"    {'opponent':14}" + "".join(f"{a:>9}" for a in arms if a in loaded)]
        for o in opps:
            cells = []
            for a in arms:
                if a in loaded:
                    rs = [r for k, r in loaded[a].items() if k[0] == o]
                    cells.append(f"{pct(sum(r['won'] for r in rs) / len(rs)) if rs else '-':>9}")
            out.append(f"    {o:14}" + "".join(cells))
    out.append("")
    return loaded


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default=HERE)
    ap.add_argument("--build", default="ec7e1a8", help="the kt build's short commit (the output files' prefix)")
    ap.add_argument("--decks", default="07,05,11,01,03")
    ap.add_argument("--arms", default="kog3,kt3,kta3", help="comparator first")
    ap.add_argument("--by-opponent", action="store_true")
    a = ap.parse_args()
    arms, decks = a.arms.split(","), a.decks.split(",")
    out = [f"kt Dustin-deck A/B, kt build {a.build}; files {a.dir}/{a.build}_ab_d<deck>_<arm>.jsonl",
           "Deck win rate by arm. Differences are paired with kog3's games on the same deals (same seed, same seat), kog3 on "
           "the opponent's seat in every arm. A draw is not a win.", ""]
    everything = defaultdict(dict)
    for deck in decks:
        files = {arm: os.path.join(a.dir, f"{a.build}_ab_d{deck}_{arm}.jsonl") for arm in arms}
        for arm, d in deck_report(deck, arms, files, a.by_opponent, out).items():
            everything[arm].update({(deck,) + k: v for k, v in d.items()})
    if len(decks) > 1 and everything:
        out.append("== All decks together (paired over every game)")
        base = everything.get(arms[0])
        for arm in arms:
            d = everything.get(arm)
            if not d:
                continue
            line = f"  {arm:6} {len(d):5d} games, {wins_of(d):5d} wins ({pct(wins_of(d) / len(d))})"
            pr = paired(base, d) if base and arm != arms[0] else None
            if pr:
                line += (f"; vs {arms[0]} {diff_text(pr)}, McNemar p {mcnemar_exact(pr['b'], pr['c']):.3f}, "
                         f"moves differ {pct(pr['differ'] / pr['n'])}")
            out.append(line)
        out.append("")
    out.append("For scale (registration): the flat +10 took Jasmine to 82.4% of the turns she was offered on the 240-seed"
               " causal block; the deck-seat-only Jasmine pricing gave +5.7 points on a separate fresh 1,920-game block.")
    print("\n".join(out))


if __name__ == "__main__":
    main()
