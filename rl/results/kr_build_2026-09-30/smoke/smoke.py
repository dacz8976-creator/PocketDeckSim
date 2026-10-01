"""kr smoke summary: kn's smoke tables for three arms (km3, kr3, kro3 as the deck's pilot; km3 the opponent's), with
kn3's from kn's smoke beside them (same decks, seeds and opponent). Checks first that this run's km3 games equal kn's
smoke's km3 games, deal by deal (the km3 code path is unchanged). A game differs when any move differs.
Usage: python3 smoke.py (reads games.jsonl and ../../kn_build_2026-09-30/smoke/games.jsonl, prints the tables)"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KN = HERE.parents[1] / "kn_build_2026-09-30" / "smoke" / "games.jsonl"
DECKS = ["goo", "grass_goo", "plaza", "psychic"]
CARD = {"goo": "Goo-zooka", "grass_goo": "Goo-zooka", "plaza": "Plaza", "psychic": "Cyrus; control"}
name = lambda p: Path(p).stem
by = defaultdict(dict)                       # (deck, opp, seat, seed) -> code -> row
for path in (HERE / "games.jsonl", KN):
    for r in map(json.loads, open(path)):
        key = (name(r["deck"]), name(r["opp"]), r["seat"], r["seed"])
        code = r["codes"][0]
        if path == KN and code == "km3":
            by[key]["km3 (kn smoke)"] = r
        elif path == KN or code != "kn3":
            by[key][code] = r
assert all({"km3", "kr3", "kro3", "kn3", "km3 (kn smoke)"} <= set(v) for v in by.values()), "every deal has every arm"
same = sum(v["km3"]["fingerprint"] == v["km3 (kn smoke)"]["fingerprint"] for v in by.values())
print(f"km3 games equal to kn's smoke's km3 games: {same} of {len(by)}")
assert same == len(by)
CODES = ["km3", "kr3", "kro3", "kn3"]
pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "-"
order = lambda kv: (DECKS.index(kv[0][0]), kv[0][1])
cells = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))   # (deck, opp) -> code -> [chances, used, wins, games]
differ = defaultdict(lambda: defaultdict(int))                    # (deck, opp) -> code -> games differing from km3
for (deck, opp, seat, seed), arms in by.items():
    for code in CODES:
        r = arms[code]
        c = cells[(deck, opp)][code]
        c[0] += len(r["chances"]); c[1] += len(r["used"]); c[2] += r["winner"] == f"Some(Win({seat}))"; c[3] += 1
        differ[(deck, opp)][code] += r["fingerprint"] != arms["km3"]["fingerprint"]

print("\n| deck (card) | opponent | " + " | ".join(f"{c}: plays / chances" for c in CODES) + " | " + " | ".join(f"{c} wins" for c in CODES) + " | " + " | ".join(f"{c}: games that differ" for c in CODES[1:]) + " |")
print("|---|---|" + "---|" * (3 * len(CODES) - 1))
for (deck, opp), arms in sorted(cells.items(), key=order):
    print(f"| {deck} ({CARD[deck]}) | {opp} | " + " | ".join(f"{arms[c][1]} / {arms[c][0]} ({pct(arms[c][1], arms[c][0])})" for c in CODES)
          + " | " + " | ".join(f"{arms[c][2]} / {arms[c][3]}" for c in CODES)
          + " | " + " | ".join(f"{differ[(deck, opp)][c]} / {arms[c][3]}" for c in CODES[1:]) + " |")

print("\nPer deck, all opponents and seats (600 games a code):")
for deck in DECKS:
    line = []
    for code in CODES:
        ch = sum(cells[(deck, o)][code][0] for (d, o) in cells if d == deck)
        u = sum(cells[(deck, o)][code][1] for (d, o) in cells if d == deck)
        df = sum(differ[(deck, o)][code] for (d, o) in cells if d == deck)
        line.append(f"{code} {u} / {ch} ({pct(u, ch)})" + (f", differ {df}" if code != "km3" else ""))
    print(f"  {deck}: " + "; ".join(line))

print("\n| deck | code | games with a chance | games with a play | median turn of the first play | plays on the game's first chance turn |")
print("|---|---|---|---|---|---|")
for deck in DECKS:
    for code in CODES:
        rs = [arms[code] for (d, _, _, _), arms in by.items() if d == deck]
        played = [r for r in rs if r["used"]]
        first = sorted(min(r["used"]) for r in played)
        on_first = sum(1 for r in rs for t in r["used"] if t == min(r["chances"]))
        print(f"| {deck} | {code} | {sum(1 for r in rs if r['chances'])} / {len(rs)} | {len(played)} | {first[len(first) // 2] if first else '-'} | {on_first} |")

print("\n| grass_goo | Goo-zooka plays | followed by Grass Knot that turn | Grass Knots in all |")
print("|---|---|---|---|")
for code in CODES:
    rs = [arms[code] for (d, _, _, _), arms in by.items() if d == "grass_goo"]
    plays = [(r, t) for r in rs for t in r["used"]]
    if "attacks" not in rs[0]:
        print(f"| {code} | {len(plays)} | (not recorded) | |"); continue
    knot = sum(1 for r, t in plays if [t, "Grass Knot"] in r["attacks"])
    print(f"| {code} | {len(plays)} | {knot} | {sum(1 for r in rs for a in r['attacks'] if a[1] == 'Grass Knot')} |")

print("\nPaired results against km3 on the same deals (won with km3 only / won with the code only):")
print("| deck | opponent | kr3 | kro3 | kn3 |")
print("|---|---|---|---|---|")
pairs = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for (deck, opp, seat, seed), arms in by.items():
    w = {c: arms[c]["winner"] == f"Some(Win({seat}))" for c in CODES}
    for c in CODES[1:]:
        pairs[(deck, opp)][c][0] += w["km3"] and not w[c]
        pairs[(deck, opp)][c][1] += w[c] and not w["km3"]
for (deck, opp), v in sorted(pairs.items(), key=order):
    print(f"| {deck} | {opp} | " + " | ".join(f"{v[c][0]} / {v[c][1]}" for c in CODES[1:]) + " |")
