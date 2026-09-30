"""km3 unplayed-Trainer diagnosis (Sept 30): which floor games to replay, by a fixed rule, before any replay.
From the floor's per-game files (../floor_dustin_2026-09-30/<deck>_games.jsonl), a game qualifies when the card had at
least one chance it didn't take (flagged[card] = [opportunities, used] with opportunities > used). Per deck, for each
of the eight panel opponents in turn, it takes qualifying games alternating seat 0 and seat 1, in the file's seed
order, until the deck's quota is met: 40 games of deck 11 for Iris; 20 of deck 14 and 20 of deck 15 for Goo-zooka
(at most 40 per card). Prints one line per deck, "--games" for trainer_diag: opponent:seat:seed, comma-separated.
Usage: python3 select_deals.py > deals.txt"""
import json
from collections import defaultdict
from pathlib import Path

FLOOR = Path(__file__).resolve().parent.parent / "floor_dustin_2026-09-30"
PLAN = [("11-archaludon-haxorus-dragonair", "Iris", 40),
        ("14-comfey-raticate-hypno", "Team Rocket's Goo-zooka", 20),
        ("15-jolteon-oricorio-raticate", "Team Rocket's Goo-zooka", 20)]

for deck, card, quota in PLAN:
    rows = [json.loads(l) for l in open(FLOOR / f"{deck}_games.jsonl")]
    by = defaultdict(lambda: defaultdict(list))            # opponent -> seat -> qualifying seeds, in file order
    for r in rows:
        o, u = r["flagged"][card]
        if o > u:
            by[r["opponent"]][r["seat"]].append(r["seed"])
    opponents = sorted(by)
    picked, round_ = [], 0
    while len(picked) < quota:
        added = False
        for opp in opponents:                              # one per opponent per pass, seats alternating by pass
            seat = round_ % 2
            k = round_ // 2
            if k < len(by[opp][seat]) and len(picked) < quota:
                picked.append(f"{opp}:{seat}:{by[opp][seat][k]}")
                added = True
        round_ += 1
        if not added and round_ > 200:
            break
    total = sum(len(s) for o in by.values() for s in o.values())
    print(f"{deck}\t{card}\t{len(picked)} of {total} qualifying games\t{','.join(picked)}")
