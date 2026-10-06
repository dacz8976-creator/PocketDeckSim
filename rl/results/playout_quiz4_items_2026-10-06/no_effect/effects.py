"""Quiz 4, item 2: how often each bot spends an action whose printed effect can do nothing at the time, in the
development run (strength_2026-10-03_kx3_dev). The events are trainer_habits' "effect" lines: every Item or Supporter
played, Ability or Stadium used and Tool played, with the no-effect reader's verdict (playout_effects.rs `effect_now`):
true (it can do something), false (by its text it can do nothing now) or null (a text the reader doesn't read).
  effects_km3_arm.jsonl: the reference arm, km3 on both sides (games mode, every game replayed exactly).
  effects_kx3_arm.jsonl: arm X, kx3 on the deck side, km3 on the panel side (scripted replay, every game exactly).
Only real decisions count (more than one legal move); a forced move isn't the bot's choice. Run from the repository root:
  python3 rl/results/playout_quiz4_items_2026-10-06/no_effect/effects.py"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    out = []
    for l in open(HERE / name, encoding="utf-8"):
        e = json.loads(l)
        if e["decision"]:
            e["side"] = "deck" if e["player"] == e["ctx"]["deck_seat"] else "panel"
            out.append(e)
    return out


arms = {"km3 (reference arm)": load("effects_km3_arm.jsonl"), "kx3 (arm X)": load("effects_kx3_arm.jsonl")}
print("Moves with a card text that were real decisions, and how many of them could do nothing by the text (no effect):")
print()
print("| who | moves with a card text | no effect | share | text not read |")
print("|---|---|---|---|---|")
for arm, es in arms.items():
    for side, who in (("deck", arm.split(" ")[0] + ", the deck side"), ("panel", "km3, the panel side (" + arm.split(" ")[0] + "'s games)")):
        s = [e for e in es if e["side"] == side]
        n0 = sum(e["does_something"] is False for e in s)
        print(f"| {who} | {len(s)} | {n0} | {100 * n0 / len(s):.1f}% | {sum(e['does_something'] is None for e in s)} |")
print()
print("Per card, the deck side (no effect / played; the same 280 deals and 2 seats, so the arms differ only by the pilot):")
print()
print("| card | km3 | kx3 |")
print("|---|---|---|")
per = defaultdict(lambda: {a: [0, 0] for a in arms})
for arm, es in arms.items():
    for e in es:
        if e["side"] == "deck":
            c = per[e["card"]][arm]
            c[1] += 1
            c[0] += e["does_something"] is False
rows = sorted(per.items(), key=lambda kv: -sum(v[0] for v in kv[1].values()))
for card, v in rows:
    if sum(x[0] for x in v.values()) == 0:
        continue
    print(f"| {card} | " + " | ".join(f"{v[a][0]} / {v[a][1]}" for a in arms) + " |")
never = [card for card, v in rows if sum(x[0] for x in v.values()) == 0]
# The reader's verdict on each text (effect_readings.jsonl, from playout_tool_rule --list-effects): a text read as
# "always" can never be flagged, so it says nothing about how the bots play it.
readings = {}
for l in open(HERE / "effect_readings.jsonl", encoding="utf-8"):
    r = json.loads(l)
    readings.setdefault(r["card"], r["reading"])
# A Tool (not in the listing: the Tool rule reads it) or a text with needs could have been flagged; a text read as
# "always", or one the reader doesn't read (a Stadium that works by itself, which is only ever played), could not.
could = sorted(c for c in never if c not in readings or isinstance(readings[c], list))
print()
print(f"Cards the deck side played only where they could do something ({len(could)}): " + ", ".join(could))
print(f"Cards never flagged because the reader can't flag them (read as always doing something, or a Stadium that works "
      f"by itself) ({len(never) - len(could)}): " + ", ".join(sorted(c for c in never if c not in could)))
print()
print("Per deck, the deck side's no-effect moves (km3 / kx3):")
print()
print("| deck | km3 | kx3 |")
print("|---|---|---|")
dk = defaultdict(lambda: Counter())
for arm, es in arms.items():
    for e in es:
        if e["side"] == "deck" and e["does_something"] is False:
            dk[e["deck"]][arm] += 1
for d in sorted(dk):
    print(f"| {d} | " + " | ".join(str(dk[d][a]) for a in arms) + " |")
print()
print("Panel side (km3 in both arms), per card, no effect / played, summed over both arms:")
pc = defaultdict(lambda: [0, 0])
for es in arms.values():
    for e in es:
        if e["side"] == "panel":
            pc[e["card"]][1] += 1
            pc[e["card"]][0] += e["does_something"] is False
print(", ".join(f"{c} {v[0]}/{v[1]}" for c, v in sorted(pc.items(), key=lambda kv: -kv[1][0]) if v[0]))
print()
unread = Counter(e["card"] for es in arms.values() for e in es if e["does_something"] is None)
print("Texts not read (null), all sides:", dict(unread) or "none")
