"""Quiz 4, item 2: kx3's own plays that could do nothing by their text, in the development run's kx3 games, decided again
with the no-effect tie-break on (redecide.jsonl, from trainer_habits scripted --noeffect-scan
kx3_r16_c12_z2_real_t0_poolmeta: every game replayed exactly; at each such play, km3 asked with the game's own
randomness, and where km3 had proposed that very move, kx3 with `_noeffect` deciding again from the same randomness).
Run from the repository root:
  python3 rl/results/playout_quiz4_items_2026-10-06/no_effect/redecide.py [redecide.jsonl]"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "redecide.jsonl"
rs = [json.loads(l) for l in open(path, encoding="utf-8")]
print(f"kx3's plays that could do nothing now, at real decisions: {len(rs)} (every game replayed exactly: "
      f"{all(r['replayed_exactly'] for r in rs)})")
own = [r for r in rs if not r["km_proposed_it"]]
kept = [r for r in rs if r["km_proposed_it"]]
print(f"  kx3 switched to it from km3's move (a lead past the bar): {len(own)}; km3 proposed it and kx3 kept it: {len(kept)}")


APPLIED, LEADS, NOTHING, FRESH = ("the tie-break plays another move", "kept: km3's move leads the other beyond the noise",
                                  "kept: no other move does something", "not reproduced: a fresh kx3 switches anyway")


def outcome(r):
    k = r["kx3"]
    if k["tie_break"]:
        return APPLIED
    if "can do nothing now by its text, but its play-outs lead" in k["reason"]:
        return LEADS
    if not k["others_do_something"]:
        return NOTHING
    if not k["plays_the_logged_move"]:
        return FRESH
    return "kept: other"


out = Counter(outcome(r) for r in kept)
for o, n in out.most_common():
    print(f"    {o}: {n}")
print()
print("Per card, where km3 proposed it:")
per = defaultdict(Counter)
for r in kept:
    per[r["card"]][outcome(r)] += 1
print()
print("| card | plays of it | the tie-break plays another move | kept by km3's play-outs | nothing else does something | not reproduced |")
print("|---|---|---|---|---|---|")
for card, c in sorted(per.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"| {card} | {sum(c.values())} | {c[APPLIED]} | {c[LEADS]} | {c[NOTHING]} | {c[FRESH]} |")
print()
inst = Counter(r["kx3"]["chosen"].split(":")[0].split("@")[0] for r in kept if r["kx3"]["tie_break"])
print("What the tie-break plays instead (by kind):", dict(inst.most_common()))
lead = [float(r["kx3"]["reason"].rsplit("(", 1)[1].split(" v km")[0]) for r in kept if r["kx3"]["tie_break"]]
if lead:
    lead.sort()
    print(f"Its play-out score against km3's no-effect move: median {lead[len(lead) // 2]:+.3f}, "
          f"from {lead[0]:+.3f} to {lead[-1]:+.3f}; at or above 0 in {sum(x >= 0 for x in lead)} of {len(lead)}")
print()
print("kx3's own switches to a move that can do nothing (per card):", dict(Counter(r["card"] for r in own).most_common()))
