"""km3's late Trainer play (Oct 5): the rates behind README.md, from events_games.jsonl (the development run's km3 games,
replayed) and events_playouts.jsonl (the continuation study's km3 play-outs at the 8 positions, replayed), and the
development run's own logs for the kx3 arm (labels only). Run from the repository root:
  python3 rl/results/playout_trainer_habits_2026-10-05/analyze.py > rl/results/playout_trainer_habits_2026-10-05/rates.txt
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEV = HERE.parent / "strength_2026-10-03_kx3_dev"
PANEL = {f"t-{n}" for n in ("altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing")}


def load(name):
    return [json.loads(l) for l in open(HERE / name, encoding="utf-8")]


games = load("events_games.jsonl")
plays = load("events_playouts.jsonl")
checks = {n: load(f"events_{n}.jsonl.replay.jsonl") for n in ("games", "playouts")}
n_games = len(checks["games"])
n_playouts = len(checks["playouts"])


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "-"


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else float("nan")


def side(e):
    if e["ctx"]["source"] == "playout":
        return "play-outs (draft A)"
    return "games: panel side" if e["deck"] in PANEL else "games: development deck side"


print("Replay checks:")
for n, c in checks.items():
    print(f"  {n}: {len(c)} replayed, {sum(x['replayed_exactly'] for x in c)} exactly as recorded")
print()

# (1) Copycat
def playable(h):
    return h["playable_now"] + h["playable_next"]


def held(e):
    return playable(e["hand_before"]) >= 2


groups = [("km3's own games (both seats)", [e for e in games if e["kind"] == "copycat"]),
          ("  of which the development decks' side", [e for e in games if e["kind"] == "copycat" and e["deck"] not in PANEL]),
          ("  of which the panel side", [e for e in games if e["kind"] == "copycat" and e["deck"] in PANEL]),
          ("km3 as the play-out policy (8 positions, draft A)", [e for e in plays if e["kind"] == "copycat"])]
print("(1) Copycat")
print(f"  plays per game: games {sum(1 for e in games if e['kind'] == 'copycat') / n_games:.2f} (both seats); "
      f"play-outs {sum(1 for e in plays if e['kind'] == 'copycat') / n_playouts:.2f} (draft A's side)")
for title, ev in groups:
    if not ev:
        continue
    n = len(ev)
    hb = [e["hand_before"] for e in ev]
    ha = [e["hand_after"] for e in ev]
    dist = Counter(min(playable(h), 3) for h in hb)
    print(f"  {title}: {n} plays")
    print(f"    hand shuffled away: size {mean(h['size'] for h in hb):.1f}; playable now {mean(h['playable_now'] for h in hb):.2f}, "
          f"next turn {mean(h['playable_next'] for h in hb):.2f}; Supporters {mean(h['supporters'] for h in hb):.2f}; "
          f"Energy-matching Pokemon {mean(h['energy_matching_pokemon'] for h in hb):.2f}")
    print(f"    playable this or next turn: 0: {pct(dist[0], n)}, 1: {pct(dist[1], n)}, 2: {pct(dist[2], n)}, 3+: {pct(dist[3], n)}")
    print(f"    drew into (the opponent's hand): {mean(e['opp_hand'] for e in ev):.1f} cards; new hand: playable now "
          f"{mean(h['playable_now'] for h in ha):.2f}, next turn {mean(h['playable_next'] for h in ha):.2f}; Supporters "
          f"{mean(h['supporters'] for h in ha):.2f}; Energy-matching Pokemon {mean(h['energy_matching_pokemon'] for h in ha):.2f}")
    worse = sum(1 for e in ev if playable(e["hand_after"]) < playable(e["hand_before"]))
    smaller = sum(1 for e in ev if e["opp_hand"] < e["hand_before"]["size"])
    print(f"    a competent player would have held it (>= 2 playable this or next turn): {sum(held(e) for e in ev)} = {pct(sum(held(e) for e in ev), n)}")
    ready = sum(1 for e in ev if e["hand_before"]["playable_next"] > 0)
    either = sum(1 for e in ev if held(e) or e["hand_before"]["playable_next"] > 0)
    print(f"    shuffled away an evolution ready for a Pokemon in play: {ready} = {pct(ready, n)}; "
          f"held by either test (>= 2 playable, or a ready evolution): {pct(either, n)}")
    print(f"    drew fewer cards than it shuffled away: {pct(smaller, n)}; fewer playable cards after than before: {pct(worse, n)}")
    by_turn = Counter("turns 1-4" if e["turn"] <= 4 else "turns 5-10" if e["turn"] <= 10 else "turns 11+" for e in ev)
    held_by_turn = Counter("turns 1-4" if e["turn"] <= 4 else "turns 5-10" if e["turn"] <= 10 else "turns 11+" for e in ev if held(e))
    print("    by turn: " + "; ".join(f"{k} {by_turn[k]} (held {pct(held_by_turn[k], by_turn[k])})" for k in ("turns 1-4", "turns 5-10", "turns 11+")))
print()
print("  The proposal's net-draw rule (block Copycat unless it draws at least 2 more cards than it shuffles away, and always when an")
print("  evolution ready for a Pokemon in play would go back), and the >= 2 playable rule, as shares of plays they would block:")
for title, ev in (("km3's own games", [e for e in games if e["kind"] == "copycat"]),) + tuple(
        (f"play-outs at {pos}", [e for e in plays if e["kind"] == "copycat" and e["ctx"]["position"] == pos])
        for pos in ("B-214254-t06", "B-214254-t10", "B-205731-t08", "B-205731-t10", "B-210952-t14", "B-210952-t16", "B-210952-t18", "B-205731-t02")):
    if ev:
        block = sum(1 for e in ev if e["opp_hand"] - e["hand_before"]["size"] < 2 or e["hand_before"]["playable_next"] > 0)
        print(f"    {title}: {len(ev)} plays; net-draw rule blocks {pct(block, len(ev))}; >= 2 playable blocks {pct(sum(held(e) for e in ev), len(ev))}; "
              f"hand {mean(e['hand_before']['size'] for e in ev):.1f}, draws {mean(e['opp_hand'] for e in ev):.1f}")
print()

# (2) Tools
def timely(x):
    """Never attacked while carrying the Tool, although it carried it for at least two more of its owner's turns."""
    end = x["ended"]["turn"] if x["ended"] else x["game_end_turn"]
    return x["never_attacked"] and end - x["turn"] >= 4


print("(2) Tools")
for title, ev in (("km3's own games (both seats)", [e for e in games if e["kind"] == "tool"]),
                  ("km3 as the play-out policy (8 positions, draft A)", [e for e in plays if e["kind"] == "tool"])):
    by_tool = defaultdict(list)
    for e in ev:
        by_tool[e["tool"]].append(e)
    print(f"  {title}: {len(ev)} attached")
    for tool, xs in sorted(by_tool.items()):
        n = len(xs)
        c = [x["carrier"] for x in xs]
        print(f"    {tool}: {n}; on the Active {pct(sum(x['slot'] == 0 for x in c), n)}, on an ex {pct(sum(x['ex'] for x in c), n)}, "
              f"Stage 1 {pct(sum(x['stage'] == 1 for x in c), n)}; able to attack when it got it {pct(sum(x['can_attack_now'] for x in c), n)}; "
              f"attacked within two turns {pct(sum(x['attacked_within_2'] for x in xs), n)}; knocked out within two turns "
              f"{pct(sum(x['knocked_out_within_2'] for x in xs), n)}; never attacked while carrying it {pct(sum(x['never_attacked'] for x in xs), n)}, "
              f"of which with two more own turns to do it {pct(sum(timely(x) for x in xs), n)}")
        how = Counter(x["ended"]["how"] if x["ended"] else "carried to the end" for x in xs)
        print("      how its time on the board ended: " + ", ".join(f"{k} {pct(v, n)}" for k, v in how.most_common()))
        carriers = Counter(x["carrier"]["name"] for x in xs)
        never = Counter(x["carrier"]["name"] for x in xs if x["never_attacked"])
        print("      carriers: " + ", ".join(f"{k} {v} (never attacked {never[k]})" for k, v in carriers.most_common(8)))
        if tool == "Elegant Cape":
            useless = sum(1 for x in xs if x["carrier"]["stage"] != 1)
            print(f"      Elegant Cape on a Pokemon that isn't Stage 1 (no HP from it): {useless}")
    if ev:
        n = len(ev)
        print(f"    all Tools: on a Pokemon that never attacks {pct(sum(x['never_attacked'] for x in ev), n)} (with two more own turns to "
              f"do it {pct(sum(timely(x) for x in ev), n)}); neither attacked nor was knocked out within two turns "
              f"{pct(sum(not x['attacked_within_2'] and not x['knocked_out_within_2'] for x in ev), n)}")
print()

# (3) heal Supporters
print("(3) Heal Supporters (healed = damage actually removed; little = 20 or less)")
for title, ev in (("km3's own games (both seats)", [e for e in games if e["kind"] == "heal"]),
                  ("km3 as the play-out policy (8 positions, draft A)", [e for e in plays if e["kind"] == "heal"])):
    by_card = defaultdict(list)
    for e in ev:
        by_card[e["card"]].append(e)
    print(f"  {title}: {len(ev)} played")
    for card, xs in sorted(by_card.items()):
        n = len(xs)
        little = sum(1 for x in xs if x["healed"] <= 20)
        zero = sum(1 for x in xs if x["healed"] == 0)
        cured = sum(1 for x in xs if x["conditions"])
        other = sum(1 for x in xs if x["hand_before"]["supporters"] > 0)
        misty = sum(1 for x in xs if any(c["card"] == "Misty" and c["now"] for c in x["hand_before"]["cards"]))
        print(f"    {card}: {n}; healed {mean(x['healed'] for x in xs):.0f} on average (could heal {mean(x['potential'] for x in xs):.0f}; "
              f"board damage {mean(x['board_damage'] for x in xs):.0f}); healed 20 or less {pct(little, n)}, nothing {pct(zero, n)}; "
              f"a Special Condition to cure {pct(cured, n)}; another Supporter in hand {pct(other, n)} (Misty playable instead {pct(misty, n)})")
print()

# The kx3 arm (labels only): plays per game by the deck's side, kx3 (arm X) v km3 (arm ref), the same deals.
print("The development run's own logs, the deck's side only (labels): plays per game, kx3 (arm X) v km3 (arm ref) on the same deals")
recs = [json.loads(l) for l in open(DEV / "games.jsonl", encoding="utf-8")]
kinds = {"Copycat": lambda a: a == "Play:Copycat",
         "a Tool (the four)": lambda a: a.startswith("Tool:") and any(t in a for t in ("Elegant Cape", "Giant Cape", "Rocky Helmet", "Protective Poncho")),
         "a heal Supporter (the three)": lambda a: a in ("Play:Irida", "Play:Pokémon Center Lady", "Play:Erika")}
for k, f in kinds.items():
    row = []
    for arm in ("X", "ref"):
        gs = [g for g in recs if g["arm"] == arm]
        row.append(sum(sum(1 for e in g["log"] if f(e["a"])) for g in gs) / len(gs))
    print(f"  {k}: kx3 {row[0]:.2f}, km3 {row[1]:.2f}")
