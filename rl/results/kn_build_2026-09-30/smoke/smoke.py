"""kn smoke summary: per scratch deck and opponent (both seats pooled), the card's plays per chance with km3 and with
kn3 as the deck's pilot, the deck's wins, and the games the two arms play differently (same seeds; a game differs when
any move differs). Usage: python3 smoke.py (reads games.jsonl, prints the tables)"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in open(HERE / "games.jsonl")]
name = lambda p: Path(p).stem
by = defaultdict(dict)                       # (deck, opp, seat, seed) -> code -> row
for r in rows:
    by[(name(r["deck"]), name(r["opp"]), r["seat"], r["seed"])][r["codes"][0]] = r
assert all(set(v) == {"km3", "kn3"} for v in by.values()), "every deal has both arms"
table = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))   # (deck, opp) -> code -> [chances, used, wins, games]
differ = defaultdict(int)
for (deck, opp, seat, seed), arms in sorted(by.items()):
    for code, r in arms.items():
        t = table[(deck, opp)][code]
        t[0] += len(r["chances"]); t[1] += len(r["used"]); t[2] += r["winner"] == f"Some(Win({seat}))"; t[3] += 1
        assert set(r["used"]) <= set(r["chances"])
    differ[(deck, opp)] += arms["km3"]["fingerprint"] != arms["kn3"]["fingerprint"]
pct = lambda a, b: f"{100 * a / b:.1f}%" if b else "-"
print("| deck (card) | opponent | km3: plays / chances | kn3: plays / chances | km3 wins | kn3 wins | games that differ |")
print("|---|---|---|---|---|---|---|")
tot = defaultdict(lambda: [0, 0, 0, 0, 0])
for (deck, opp), arms in sorted(table.items(), key=lambda kv: (["goo", "grass_goo", "plaza", "psychic"].index(kv[0][0]), kv[0][1])):
    km, kn = arms["km3"], arms["kn3"]
    card = {"plaza": "Plaza", "psychic": "Cyrus; control"}.get(deck, "Goo-zooka")
    print(f"| {deck} ({card}) | {opp} | {km[1]} / {km[0]} ({pct(km[1], km[0])}) | {kn[1]} / {kn[0]} ({pct(kn[1], kn[0])}) "
          f"| {km[2]} / {km[3]} | {kn[2]} / {kn[3]} | {differ[(deck, opp)]} / {km[3]} |")
    for i, v in enumerate((km[0], km[1], kn[0], kn[1], differ[(deck, opp)])):
        tot[deck][i] += v
print()
for deck, (c0, u0, c1, u1, d) in tot.items():
    print(f"{deck}: km3 {u0} / {c0} ({pct(u0, c0)}), kn3 {u1} / {c1} ({pct(u1, c1)}); games that differ {d} / 600")
