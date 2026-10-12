"""skip_exact.py (the cloud, Oct 12): the exact attack-skipping comparison of the combined run, from skip_replay's decision lines.

Inputs (each made by `skip_replay`, an identity replay of the recorded games on the program that played them; see README.md):
  candidate: this run's arm X (kx3 with _tools _zs3 _m64), replayed on 172cbe9c (engine tree 69a5a441);
  frozen:    the development run's arm X (the frozen kx3, rl/results/strength_2026-10-03_kx3_dev), replayed on d513e37b (31dbd2e6);
  km3:       this run's arm ref (km3 on both sides; it equals the development run's game for game), replayed on 172cbe9c.
Every game of each must have replayed exactly, or nothing is computed.

Definitions (at the deck side's decisions: the points where its pilot was asked, i.e. had two or more legal moves):
  - an attack chance: a decision with an attack among the legal moves;
  - a skip (decision level): an attack chance where the move taken was not an attack (it may still attack later that turn);
  - a skip turn: a game turn of the deck with at least one attack chance, and no attack taken at any of its decisions that turn
    (the pre-registration's "no attack followed that turn").
Shares are pooled over games (the sum of the counts over the sum of the chances); the interval is +- 1.96 SE of the ratio estimator
over games, and a paired difference uses each key's two games (the same deck, opponent, deal and seat), as SKIP_ATTACK.md does.

  python3 skip_exact.py <dir with decisions_<bot>.jsonl and check_<bot>.jsonl for bot in candidate, frozen, km3>
Writes exact_summary.txt, skip_turns.tsv and skip_decisions.tsv in that folder.
"""
import json, os, sys
from collections import defaultdict

BOTS = ("candidate", "frozen", "km3")
GROUPS = {"fast": ("09-", "06-", "10-"), "setup": ("03-", "01-", "05-"), "middle": ("draft-A",)}
DECKS = ["09-mega-manectric-heliolisk", "06-mega-blaziken-tournament-list", "10-xatu-oricorio-tr-weezing", "03-wailord-indeedee-wall",
         "01-muk-glimmora-kingambit-regigigas", "05-indeedee-stoutland", "draft-A-shark-tempo"]
EXPECTED = 560


def pair_key(key):
    return key.rsplit("|", 1)[0]


def group(deck):
    for g, prefixes in GROUPS.items():
        if deck.startswith(prefixes):
            return g
    raise ValueError(deck)


def require_exact(checks, bot, expected):
    bad = [c["key"] for c in checks if not c.get("replayed_exactly")]
    if len(checks) != expected or bad:
        sys.exit(f"STOP: {bot}: {len(checks)} games checked (expected {expected}), {len(bad)} not replayed exactly: {bad[:5]}")


def per_game(rows):
    """Counts for one game's deck-side decisions (in decision order)."""
    rows = sorted(rows, key=lambda r: r["decision"])
    points = sum(r["attack_legal"] for r in rows)
    skips = sum(r["attack_legal"] and not r["taken_attack"] for r in rows)
    by_turn = defaultdict(list)
    for r in rows:
        by_turn[r["turn"]].append(r)
    turns, skip_turns = 0, []
    for t in sorted(by_turn):
        rs = by_turn[t]
        if any(r["attack_legal"] for r in rs):
            turns += 1
            if not any(r["taken_attack"] for r in rs):
                skip_turns.append({"turn": t, "decisions": [r["decision"] for r in rs], "attacks": sorted({a for r in rs for a in r["attacks"]}),
                                   "taken": [r["taken"] for r in rs]})
    skip_decisions = [r for r in rows if r["attack_legal"] and not r["taken_attack"]]
    return {"points": points, "skips": skips, "turns": turns, "skip_turns": len(skip_turns), "skip_turn_list": skip_turns,
            "skip_decisions": skip_decisions}


def ratio(pairs):
    """(share, half-width) of sum(count)/sum(denominator) over games, +- 1.96 SE of the ratio estimator; (None, None) if no denominator."""
    n = len(pairs)
    tot = sum(d for _, d in pairs)
    if tot == 0 or n < 2:
        return None, None
    share = sum(c for c, _ in pairs) / tot
    mean = tot / n
    r = [(c - share * d) / mean for c, d in pairs]
    return share, 1.96 * (sum(x * x for x in r) / (n * (n - 1))) ** 0.5


def paired(a, b):
    """(share_a - share_b, half-width) over keys, each key's two games' residuals differenced."""
    n = len(a)
    ta, tb = sum(d for _, d in a), sum(d for _, d in b)
    if n < 2 or ta == 0 or tb == 0:
        return None, None
    sa, sb = sum(c for c, _ in a) / ta, sum(c for c, _ in b) / tb
    ma, mb = ta / n, tb / n
    dd = [(ca - sa * da) / ma - (cb - sb * db) / mb for (ca, da), (cb, db) in zip(a, b)]
    return sa - sb, 1.96 * (sum(x * x for x in dd) / (n * (n - 1))) ** 0.5


def load(folder, bot):
    with open(os.path.join(folder, f"check_{bot}.jsonl")) as f:
        checks = [json.loads(l) for l in f if l.strip()]
    require_exact(checks, bot, EXPECTED)
    rows = defaultdict(list)
    with open(os.path.join(folder, f"decisions_{bot}.jsonl")) as f:
        for l in f:
            r = json.loads(l)
            rows[pair_key(r["key"])].append(r)
    games = {}
    for c in checks:
        k = pair_key(c["key"])
        g = per_game(rows.get(k, []))
        g["key"], g["deck"] = c["key"], c["key"].split("|")[0]
        games[k] = g
    return games


def pct(x, h):
    return "-" if x is None else f"{100 * x:.1f} ± {100 * h:.1f}"


def main(folder):
    data = {b: load(folder, b) for b in BOTS}
    keys = sorted(data["candidate"])
    assert all(sorted(data[b]) == keys for b in BOTS), "the three bots' games are not on the same keys"
    out = []
    subsets = [("all", keys)] + [(f"group {g}", [k for k in keys if group(k.split("|")[0]) == g]) for g in GROUPS] + \
              [(f"deck {d}", [k for k in keys if k.startswith(d + "|")]) for d in DECKS]
    for level, (cnt, den) in (("decision", ("skips", "points")), ("turn", ("skip_turns", "turns"))):
        what = ("attack chances (decisions with an attack legal) and the share where the move taken was not an attack" if level == "decision"
                else "turns with an attack chance and the share with no attack taken that turn (skip turns)")
        out += [f"## {level} level: {what}", "",
                "| rows | games | " + " | ".join(f"{b} {den} / {cnt} / share %" for b in BOTS) + " | cand − frozen | cand − km3 | frozen − km3 |",
                "|---|---:|" + "---|" * (len(BOTS) + 3)]
        for name, ks in subsets:
            cells = []
            for b in BOTS:
                p = [(data[b][k][cnt], data[b][k][den]) for k in ks]
                s, h = ratio(p)
                cells.append(f"{sum(x for _, x in p)} / {sum(x for x, _ in p)} / {pct(s, h)}")
            diffs = []
            for a, b in (("candidate", "frozen"), ("candidate", "km3"), ("frozen", "km3")):
                dv, h = paired([(data[a][k][cnt], data[a][k][den]) for k in ks], [(data[b][k][cnt], data[b][k][den]) for k in ks])
                diffs.append("-" if dv is None else f"{100 * dv:+.1f} ± {100 * h:.1f}")
            out.append(f"| {name} | {len(ks)} | " + " | ".join(cells) + " | " + " | ".join(diffs) + " |")
        out.append("")
    for b in BOTS:
        games_with = sum(1 for k in keys if data[b][k]["skip_turns"] > 0)
        out.append(f"- {b}: games with one or more skip turns {games_with} of {len(keys)}; skip turns per game "
                   f"{sum(data[b][k]['skip_turns'] for k in keys) / len(keys):.3f}")
    with open(os.path.join(folder, "exact_summary.txt"), "w") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(folder, "skip_turns.tsv"), "w") as f:
        f.write("bot\tkey\tturn\tdecisions\tlegal_attacks\tmoves_taken_that_turn\n")
        for b in BOTS:
            for k in keys:
                g = data[b][k]
                for s in g["skip_turn_list"]:
                    f.write(f"{b}\t{g['key']}\t{s['turn']}\t{','.join(map(str, s['decisions']))}\t{'; '.join(s['attacks'])}\t{' > '.join(s['taken'])}\n")
    with open(os.path.join(folder, "skip_decisions.tsv"), "w") as f:
        f.write("bot\tkey\tturn\tdecision\tlegal_attacks\ttaken\tattack_later_that_turn\n")
        for b in BOTS:
            for k in keys:
                g = data[b][k]
                skip_turns = {s["turn"] for s in g["skip_turn_list"]}
                for r in g["skip_decisions"]:
                    f.write(f"{b}\t{g['key']}\t{r['turn']}\t{r['decision']}\t{'; '.join(r['attacks'])}\t{r['taken']}\t"
                            f"{'no' if r['turn'] in skip_turns else 'yes'}\n")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
