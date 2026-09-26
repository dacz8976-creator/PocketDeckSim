#!/usr/bin/env python3
"""B2c for the Altaria detector network, step 3: group the positions where the network and kp3 choose differently,
and say which choice wins more when kp3 plays on. The Lucario study's analyze.py
(../lucario_network_divergence_2026-09-25/analyze.py) with kp3 in place of k3, a by-game interval beside the
by-position one, and the five named habits fixed in README.md before the run.

    python3 analyze.py [--file decisions.jsonl] [--min 20] [--sub 10]

Reads decisions.jsonl (net_divergence_kp: every network decision with both moves' details and the board, and at
each position where the moves differ beyond move order, 8 paired play-outs of each move with kp3 piloting both decks
afterwards). A position's value is the mean over its paired play-outs of (Altaria's score after the network's move
- after kp3's move), in points of Altaria's score (win 1, tie 0.5).

Intervals, both 95%: "by position" treats positions as independent (the Lucario study's; a little narrow, since
positions from one game are not); "by game" is the same mean with a game-clustered standard error (sandwich, G/(G-1)
correction), printed beside it. A row "clears zero" when its by-position interval excludes zero, the Lucario study's
rule; a row that clears by position but not by game is marked "(position only)". Review, Sept 26 (before any run of
the study): a tested row under 10 positions is not marked, and the pooled row of small pairs is not a tested row.

Rows, fixed before the run (README.md, "Pre-set groupings"):
  A. pairs of move kinds (network, kp3), as the Lucario study's analyze.py; rows with at least --min positions,
     the rest pooled;
  B. the named habits 1-5, headline rows 1a-5b (18 rows), each printed whatever its size; the indented rows under
     a headline are looks inside it (at least --sub positions each, the rest pooled as "other"), not separate tests,
     and are never marked as clearing zero.
Also checked: decisions.jsonl holds exactly the network's recorded moves (--games-file), decision for decision.
Card names: the sleep attacks are the attacks in decks/research/altaria.txt whose text puts the opponent's Active
to sleep, and Stampede is Eevee's attack; both are read from the card database at start (lib/card.py) and checked
against the names used below.
"""
import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SLEEP = {"Sing", "Hypnoblast", "Dark Slumber", "Sleepy Lullaby"}
STAMPEDE = "Stampede"


def check_names():
    """The sleep attacks and Stampede, read from the Altaria list's card texts (lib/card.py's database)."""
    sys.path.insert(0, str(ROOT / "lib"))
    sys.dont_write_bytecode = True   # nothing written into lib/
    import card  # noqa: E402
    db = {v["id"]: v for _, v in card.load()}
    ids = []
    for line in (ROOT / "decks/research/altaria.txt").read_text().splitlines():
        parts = line.split()
        if parts and parts[0].isdigit():
            ids.append(" ".join(parts[1:]))
    attacks = {a["title"]: (a.get("effect") or "") for i in ids for a in db[i].get("attacks", [])}
    sleep = {t for t, e in attacks.items() if "is now asleep" in e.lower()}
    if sleep != SLEEP or STAMPEDE not in attacks:
        sys.exit(f"card names changed: sleep attacks in the list {sorted(sleep)}, expected {sorted(SLEEP)}; "
                 f"Stampede in the list: {STAMPEDE in attacks}")


def check_against_games(rows, path):
    """Every game's network moves in decisions.jsonl are the recorded ones, decision for decision."""
    recorded = {}
    for x in open(path):
        g = json.loads(x)
        if g["row"] == "net|kp3":
            recorded[g["seed"] - 18_200_000_000] = g["moves"]
    by_game = defaultdict(list)
    for r in rows:
        by_game[r["i"]].append((r["decision"], r["net"]))
    bad = [i for i, v in by_game.items() if [k for _, k in sorted(v)] != recorded.get(i)]
    if bad:
        sys.exit(f"decisions.jsonl does not hold the recorded network moves for deals {bad[:10]}")
    return len(by_game)


def kind(d):
    """The Lucario study's move kind, unchanged."""
    k = d["kind"]
    if k == "play":
        return f"play {d['trainer']}"
    if k in ("energy", "tool", "evolve", "ability"):
        return f"{k} to {d['target']}" if k in ("energy", "tool") else f"{k} ({d['target']})"
    if k == "attack":
        return "attack (knocks out)" if d.get("printed_ko") else "attack"
    return k


def is_attack(d, names=None):
    return d["kind"] == "attack" and (names is None or d["name"] in names)


def benches(d):
    return d["kind"] == "place" and d["slot"] == "bench"


def short(d):
    """A move in a few words, with names, for the looks inside a habit."""
    k = d["kind"]
    if k == "attack":
        return f"attack {d['name']}" + (" (sure KO)" if d.get("sure_ko") else "")
    if k == "place":
        return f"bench {d['name']}" if d["slot"] == "bench" else f"place {d['name']} (active)"
    if k == "energy":
        return f"energy to {d['target']} {d['name']}"
    if k in ("retreat", "promote", "activate"):
        return f"{k} to {d['name']}"
    if k == "evolve":
        return f"evolve {d['from']} into {d['name']}"
    if k == "play":
        return f"play {d['card']}"
    if k == "tool":
        return f"tool {d['card']} to {d['target']}"
    return k


def stats(rows):
    """n, mean, half-width by position, half-width by game (clustered)."""
    v = [r["net_minus_kp3"] for r in rows]
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / max(n - 1, 1))
    h_pos = 1.96 * sd / math.sqrt(n) if n > 1 else float("nan")
    by_game = defaultdict(float)
    for r in rows:
        by_game[r["i"]] += r["net_minus_kp3"] - m
    g = len(by_game)
    h_game = (1.96 * math.sqrt(g / (g - 1) * sum(s * s for s in by_game.values())) / n) if g > 1 else float("nan")
    return n, m, h_pos, h_game


MIN_MARK = 10   # review, Sept 26: a row under 10 positions is printed but never marked (two positions of +12.5 each
#                have an interval of zero width and would "clear zero"); the same size as the smallest look (--sub)


def line(label, rows, games, width=70, mark=True):
    if not rows:
        return f"{label:<{width}} {0:>9}"
    n, m, hp, hg = stats(rows)
    clear = ""
    if mark and n >= MIN_MARK and (m - hp > 0 or m + hp < 0):
        clear = "  *" if (m - hg > 0 or m + hg < 0) else "  * (position only)"
    elif mark and n < MIN_MARK:
        clear = "  (too few to mark)"
    total = 100 * sum(r["net_minus_kp3"] for r in rows) / games

    def ci(h):  # no interval from one position (by position) or one game (by game)
        return f"({100 * (m - h):+6.1f}, {100 * (m + h):+6.1f})" if not math.isnan(h) else f"({'-':>6}, {'-':>6})"
    return f"{label:<{width}} {n:>9} {100 * m:+8.1f} {ci(hp)} {ci(hg)} {total:+9.2f}{clear}"


def header(width=70):
    return (f"{'':<{width}} {'positions':>9} {'net-kp3':>8} {'95% by position':>16} {'95% by game':>16} "
            f"{'total/game':>9}")


def looks(rows, key, games, sub, indent="    "):
    """Rows inside a headline, split by key(r); groups under `sub` positions pooled as 'other'."""
    split = defaultdict(list)
    for r in rows:
        split[key(r)].append(r)
    out, other = [], []
    for k, rs in sorted(split.items(), key=lambda kv: -len(kv[1])):
        if len(rs) >= sub:
            out.append(line(indent + k, rs, games, mark=False))
        else:
            other += rs
    if other and out:
        out.append(line(indent + "other", other, games, mark=False))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(HERE / "decisions.jsonl"))
    ap.add_argument("--min", type=int, default=20, help="smallest move-kind pair listed on its own (A)")
    ap.add_argument("--sub", type=int, default=10, help="smallest look inside a named habit (B)")
    ap.add_argument("--games-file", default=str(ROOT / "rl/results/altaria_network_readout/kp3_rows_games.jsonl"))
    a = ap.parse_args()
    check_names()
    rows = [json.loads(x) for x in open(a.file) if x.strip()]
    games = len({r["i"] for r in rows})
    checked = check_against_games(rows, a.games_file)
    print(f"Check: in all {checked} games, decisions.jsonl holds exactly the network's recorded moves "
          "(kp3_rows_games.jsonl, row net|kp3), decision for decision.")
    n_dec = len(rows)
    same = sum(1 for r in rows if not r["differs"])
    order = sum(1 for r in rows if r["differs"] and r["order_only"])
    rolled = [r for r in rows if "net_minus_kp3" in r]
    selfagree = sum(1 for r in rows if r["kp3_agrees_with_itself"])
    memory = sum(1 for r in rolled if any(r.get("revealed_memory", [])))
    print(f"{games} games, {n_dec} network decisions: same move as kp3 {same} ({100 * same / n_dec:.0f}%), "
          f"differs only in move order {order} ({100 * order / n_dec:.0f}%), differs {len(rolled)} "
          f"({100 * len(rolled) / n_dec:.0f}%). kp3 chose the same move under all 3 probe seeds at "
          f"{100 * selfagree / n_dec:.0f}% of decisions.")
    print(f"Positions played out where either player had revealed-card memory (it starts empty in a play-out): "
          f"{memory} of {len(rolled)}.")
    if not rolled:
        sys.exit("no position was played out")
    n, m, hp, hg = stats(rolled)
    print(f"Overall: over the {n} differing positions, the network's move scores {100 * m:+.1f} points "
          f"(95% by position ± {100 * hp:.1f}, by game ± {100 * hg:.1f}) for Altaria against kp3's move, with kp3 "
          "piloting both decks afterwards.\n")
    print("'*' = the 95% interval by position excludes zero (the Lucario study's rule); '(position only)' = not by "
          "game. Marked on\ntested rows only (A's pairs and B's headlines), never on the looks inside a headline or "
          f"the pooled row;\na tested row under {MIN_MARK} positions is printed but not marked ('too few to mark').\n"
          "'total/game' = the row's summed difference per game, in points of Altaria's score: a rough size of "
          "what kp3 would\ngain by making the network's move in that kind of position (gains don't simply add).\n")

    # A. pairs of move kinds
    print("A. Pairs of move kinds (network move, kp3 move)")
    print(header())
    groups = defaultdict(list)
    for r in rolled:
        groups[(kind(r["net_detail"]), kind(r["kp3_detail"]))].append(r)
    listed = 0
    for (nk, kk), rs in sorted(groups.items(), key=lambda kv: -sum(r["net_minus_kp3"] for r in kv[1])):
        if len(rs) >= a.min:
            print(line(f"{nk} / {kk}", rs, games))
            listed += 1
    small = [r for rs in groups.values() if len(rs) < a.min for r in rs]
    if small:   # a mixture of pairs, not a tested row: never marked (review, Sept 26)
        print(line("(smaller groups, pooled; not tested)", small, games, mark=False))
    print(f"  {listed} pairs listed on their own, {sum(1 for rs in groups.values() if len(rs) < a.min)} pooled.\n")

    # B. the named habits
    N, K = "net_detail", "kp3_detail"
    print("B. The named habits (fixed before the run)")
    print(header())
    heads = []

    def head(tag, label, rs, key=None):
        """A headline row (a test; tags as in README.md), and the looks inside it (not tests) split by key."""
        heads.append(tag)
        print(line(f"  {tag} {label}", rs, games))
        if key is not None:
            for x in looks(rs, key, games, a.sub, indent="       "):
                print(x)

    print("1. Benching a Basic")
    for (ta, tb), lab, setup in ((("1a", "1b"), "in play (turn 1 on)", False), (("1c", "1d"), "at setup (turn 0)", True)):
        inn = [r for r in rolled if (r["turn"] == 0) == setup]
        head(ta, f"network benches a Basic, kp3 doesn't, {lab}",
             [r for r in inn if benches(r[N]) and not benches(r[K])],
             lambda r: f"network benches {r[N]['name']}; kp3: {short(r[K])}")
        head(tb, f"kp3 benches a Basic, network doesn't, {lab}",
             [r for r in inn if benches(r[K]) and not benches(r[N])],
             lambda r: f"kp3 benches {r[K]['name']}; network: {short(r[N])}")

    print("2. Stampede without a knockout (sure-knockout rule)")
    stamp = lambda d: is_attack(d, {STAMPEDE}) and not d.get("sure_ko")  # noqa: E731
    head("2a", "kp3 Stampedes without a KO, network does something else",
         [r for r in rolled if stamp(r[K]) and not is_attack(r[N], {STAMPEDE})], lambda r: f"network: {short(r[N])}")
    head("2b", "network Stampedes without a KO, kp3 does something else",
         [r for r in rolled if stamp(r[N]) and not is_attack(r[K], {STAMPEDE})], lambda r: f"kp3: {short(r[K])}")

    print("3. Sleep: which sleep attack, and who is Active")
    head("3a", "network uses a sleep attack, kp3 doesn't",
         [r for r in rolled if is_attack(r[N], SLEEP) and not is_attack(r[K], SLEEP)],
         lambda r: f"network {r[N]['name']} ({r[N]['attacker']}); kp3: {short(r[K])}")
    head("3b", "kp3 uses a sleep attack, network doesn't",
         [r for r in rolled if is_attack(r[K], SLEEP) and not is_attack(r[N], SLEEP)],
         lambda r: f"kp3 {r[K]['name']} ({r[K]['attacker']}); network: {short(r[N])}")
    who = [r for r in rolled if r[N].get("active_after") != r[K].get("active_after")]
    after = lambda r, s: r[s].get("active_after")  # noqa: E731
    head("3c", "the two moves leave different Pokemon Active", who,
         lambda r: ("(3d or 3e)" if "Darkrai" in (after(r, N), after(r, K))
                    else f"Active after: network {after(r, N)}, kp3 {after(r, K)}"))
    head("3d", "Darkrai Active after the network's move, not kp3's",
         [r for r in who if after(r, N) == "Darkrai"], lambda r: f"kp3: {short(r[K])}")
    head("3e", "Darkrai Active after kp3's move, not the network's",
         [r for r in who if after(r, K) == "Darkrai"], lambda r: f"network: {short(r[N])}")

    print("4. Energy target")
    en = lambda d, t: d["kind"] == "energy" and d["target"] == t  # noqa: E731
    head("4a", "network energy to the Bench, kp3 to the Active",
         [r for r in rolled if en(r[N], "bench") and en(r[K], "active")],
         lambda r: f"network to {r[N]['name']}; kp3 to {r[K]['name']}")
    head("4b", "network energy to the Active, kp3 to the Bench",
         [r for r in rolled if en(r[N], "active") and en(r[K], "bench")],
         lambda r: f"network to {r[N]['name']}; kp3 to {r[K]['name']}")
    head("4c", "both to the Bench, different Pokemon",
         [r for r in rolled if en(r[N], "bench") and en(r[K], "bench")],
         lambda r: f"network to {r[N]['name']}; kp3 to {r[K]['name']}")
    head("4d", "network energy to the Bench, kp3 no energy",
         [r for r in rolled if en(r[N], "bench") and r[K]["kind"] != "energy"], lambda r: f"kp3: {short(r[K])}")
    head("4e", "kp3 energy to the Bench, network no energy",
         [r for r in rolled if en(r[K], "bench") and r[N]["kind"] != "energy"], lambda r: f"network: {short(r[N])}")

    print("5. Retreat vs attack")
    head("5a", "network retreats, kp3 attacks",
         [r for r in rolled if r[N]["kind"] == "retreat" and is_attack(r[K])],
         lambda r: f"network to {r[N]['name']}; kp3 {short(r[K])}")
    head("5b", "network attacks, kp3 retreats",
         [r for r in rolled if is_attack(r[N]) and r[K]["kind"] == "retreat"],
         lambda r: f"network {short(r[N])}; kp3 to {r[K]['name']}")

    print(f"\n{listed + len(heads)} rows were tested ({listed} move-kind pairs listed on their own and {len(heads)} "
          "named headline rows), so one or two\nof the smaller ones may clear zero by chance. The indented rows under "
          "a headline are looks inside it, not separate tests.")


if __name__ == "__main__":
    main()
