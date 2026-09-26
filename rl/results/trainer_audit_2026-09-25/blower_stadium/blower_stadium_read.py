"""Summarise blower_stadium.py's games.jsonl: Field Blower targets and offers, Stadium plays by situation,
once-a-turn Stadium use. Usage: blower_stadium_read.py GAMES.jsonl"""
import collections
import json
import sys

G = [json.loads(l) for l in open(sys.argv[1])]
decks = sorted({g["deck"] for g in G})
print(f"{len(G)} games, {len(decks)} decks")

# ---- Field Blower
tgt = collections.defaultdict(collections.Counter)
offer = collections.defaultdict(collections.Counter)
own_only_played = collections.Counter()
for g in G:
    d = g["deck"]
    for b in g["blower_turns"]:
        opp_target = bool(b["opp_tools"]) or b["stadium_owner"] == "opp"
        own_target = bool(b["own_tools"]) or b["stadium_owner"] == "own"
        sit = "opp target available" if opp_target else "only own targets" if own_target else "no target?"
        offer[d][sit] += 1
        offer[d][sit + ", played"] += b["played"]
        if b["played"]:
            t = b["target"] or "?"
            kind = t.split(" ")[0] + " " + t.split(" ")[1] if t and not t.startswith("(") else t
            tgt[d][kind] += 1
            tgt["ALL"][kind] += 1
            if t.startswith("own"):
                tgt["ALL own:detail"][t + (" | opp targets were available" if opp_target else " | only own targets")] += 1
            if t.startswith("opp"):
                tgt["ALL opp:detail"][t] += 1
print("\n== Field Blower: turns playable, by what was on the board, and how often played ==")
for d in decks:
    o = offer[d]
    if not sum(v for k, v in o.items() if not k.endswith("played")):
        continue
    a, b = o["opp target available"], o["only own targets"]
    print(f"{d:48s} opp target available: {a:4d} turns, played {o['opp target available, played']:4d} ({100 * o['opp target available, played'] / max(1, a):4.1f}%) | "
          f"only own targets: {b:4d}, played {o['only own targets, played']:3d} | targets: {dict(tgt[d])}")
print("\nall targets:", dict(tgt["ALL"]))
print("own targets in detail:")
for k, n in tgt["ALL own:detail"].most_common(25):
    print(f"  {n:4d}  {k}")
print("opponent targets (top 20):")
for k, n in tgt["ALL opp:detail"].most_common(20):
    print(f"  {n:4d}  {k}")

# ---- Stadiums
st = collections.defaultdict(collections.Counter)
for g in G:
    for s in g["stadium_turns"]:
        k = (g["deck"], s["card"])
        sit = "none" if not s["in_play"] else ("own " + s["in_play"]) if s["in_play_owner"] == "own" else "opp's " + s["in_play"]
        grp = "none" if not s["in_play"] else "own other" if s["in_play_owner"] == "own" else "opponent's"
        st[k][grp] += 1
        st[k][grp + ", played"] += s["played"]
        st[k]["games"] += 0
print("\n== Stadium cards: turns playable by what was in play, and how often played ==")
for (d, c), o in sorted(st.items()):
    parts = []
    for grp in ("none", "own other", "opponent's"):
        if o[grp]:
            parts.append(f"{grp}: {o[grp + ', played']}/{o[grp]} ({100 * o[grp + ', played'] / o[grp]:4.1f}%)")
    print(f"{d:48s} {c:20s} " + " | ".join(parts))

# ---- once-a-turn Stadium use
use = collections.defaultdict(collections.Counter)
for g in G:
    for s, x in g["use_stadium"].items():
        use[(g["deck"], s)]["offered"] += x["offered"]
        use[(g["deck"], s)]["used"] += x["used"]
print("\n== Once-a-turn Stadium effects: turns offered to the deck, turns used ==")
for (d, s), o in sorted(use.items()):
    if o["offered"] >= 20:
        print(f"{d:48s} {s:20s} used {o['used']:4d} of {o['offered']:4d} ({100 * o['used'] / o['offered']:4.1f}%)")
