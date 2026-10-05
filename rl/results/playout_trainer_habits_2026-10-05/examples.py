"""The 20 hand-picked examples of README.md, chosen by fixed criteria (the first event in file order that meets each),
so the list is reproducible: python3 rl/results/playout_trainer_habits_2026-10-05/examples.py > .../examples.md
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
games = [json.loads(l) for l in open(HERE / "events_games.jsonl", encoding="utf-8")]
plays = [json.loads(l) for l in open(HERE / "events_playouts.jsonl", encoding="utf-8")]
PANEL = {f"t-{n}" for n in ("altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing")}


def where(e):
    c = e["ctx"]
    if c["source"] == "game":
        return f"km3's own game `{c['key']}` (seed {c['seed']})"
    return f"play-out: {c['position']}, after the {'plan' if c['first'] == 'plans_first_move' else 'rival'}'s first move, round {c['round']}"


def hand(h):
    def mark(c):
        return c["card"] + (" (now)" if c["now"] else " (next turn)" if c["next"] else "")
    return ", ".join(mark(c) for c in h["cards"]) or "nothing else"


def board(b):
    return ", ".join(f"{p['name']}{' [Active]' if p['slot'] == 0 else ''} {p['hp']} HP {p['energy']}E" for p in b)


def show(e):
    who = f"{e['deck']}, turn {e['turn']}, points {e['points'][0]}-{e['points'][1]}, {e['deck_left']} cards in deck; result: {e['winner']}"
    if e["kind"] == "copycat":
        hb, ha = e["hand_before"], e["hand_after"]
        n = hb["playable_now"] + hb["playable_next"]
        verdict = "hold (>= 2 playable)" if n >= 2 else "play (fewer than 2 playable)"
        ready = " A ready evolution went back into the deck." if hb["playable_next"] else ""
        return (f"Copycat. {where(e)}; {who}. Board: {board(e['board'])}. Hand shuffled away: {hand(hb)}. Drew {e['opp_hand']} "
                f"into: {hand(ha)}. The rule says {verdict}.{ready}")
    if e["kind"] == "tool":
        c = e["carrier"]
        fate = (f"attacked on turns {e['attacks']}" if e["attacks"] else "never attacked while carrying it") + (
            f"; {e['ended']['how']} on turn {e['ended']['turn']}" if e["ended"] else "; carried it to the end")
        return (f"{e['tool']} on {'the Active' if c['slot'] == 0 else 'a Benched'} {c['name']} ({c['hp']} HP, {c['energy']} Energy, "
                f"{'able' if c['can_attack_now'] else 'not able'} to attack). {where(e)}; {who}. Then: {fate}; the game ended on turn {e['game_end_turn']}.")
    return (f"{e['card']}: healed {e['healed']} (could heal {e['potential']}; {e['board_damage']} damage on the board"
            f"{'; a Special Condition to cure' if e['conditions'] else ''}). {where(e)}; {who}. Board: {board(e['board'])}. Hand: {hand(e['hand_before'])}.")


used = set()


def first(events, pred):
    """The first event meeting `pred` that no earlier pick took."""
    e = next(e for e in events if pred(e) and id(e) not in used)
    used.add(id(e))
    return e


cc_g = [e for e in games if e["kind"] == "copycat"]
cc_p = [e for e in plays if e["kind"] == "copycat"]
tl_g = [e for e in games if e["kind"] == "tool"]
tl_p = [e for e in plays if e["kind"] == "tool"]
he_g = [e for e in games if e["kind"] == "heal"]
he_p = [e for e in plays if e["kind"] == "heal"]
pl = lambda h: h["playable_now"] + h["playable_next"]
picks = [
    ("Copycat throws away a ready evolution on turn 2 (the continuation study's position 8)",
     first(cc_p, lambda e: e["ctx"]["position"] == "B-205731-t02" and e["turn"] == 2 and e["hand_before"]["playable_next"] > 0)),
    ("the same, another world", first(cc_p, lambda e: e["ctx"]["position"] == "B-205731-t02" and e["turn"] == 2 and e["hand_before"]["playable_next"] > 0 and e["ctx"]["round"] > 10)),
    ("Copycat throws away a ready evolution, a development deck in its own game", first(cc_g, lambda e: e["deck"] not in PANEL and e["hand_before"]["playable_next"] > 0)),
    ("the same, the panel side", first(cc_g, lambda e: e["deck"] in PANEL and e["hand_before"]["playable_next"] > 0)),
    ("Copycat with 3 or more playable cards, drawing fewer than it shuffles away", first(cc_g, lambda e: pl(e["hand_before"]) >= 3 and e["opp_hand"] < e["hand_before"]["size"])),
    ("the same, another deck", first(cc_g, lambda e: pl(e["hand_before"]) >= 3 and e["opp_hand"] < e["hand_before"]["size"] and not e["deck"].startswith("09-"))),
    ("Copycat with 2 playable cards on turn 1 or 2", first(cc_g, lambda e: e["turn"] <= 2 and pl(e["hand_before"]) >= 2)),
    ("Copycat late (turn 11+) into a small opponent's hand", first(cc_g, lambda e: e["turn"] >= 11 and e["opp_hand"] <= 2)),
    ("Copycat in a play-out at position 4, turn 12 (where withholding Copycat helped)", first(cc_p, lambda e: e["ctx"]["position"] == "B-205731-t10" and e["turn"] == 12)),
    ("Copycat with an empty deck, late in a play-out", first(cc_p, lambda e: e["turn"] >= 30 and e["deck_left"] == 0)),
    ("a Copycat the rule calls fine: nothing playable, a big draw", first(cc_g, lambda e: pl(e["hand_before"]) == 0 and e["opp_hand"] >= 5)),
    ("Elegant Cape on a Basic that never attacks while carrying it, with time to", first(tl_g, lambda e: e["tool"] == "Elegant Cape" and e["carrier"]["stage"] == 0 and e["never_attacked"] and ((e["ended"]["turn"] if e["ended"] else e["game_end_turn"]) - e["turn"]) >= 4)),
    ("Elegant Cape on a damaged Basic (it adds no HP to a Basic)",
     first(tl_g, lambda e: e["tool"] == "Elegant Cape" and e["carrier"]["stage"] == 0 and e["carrier"]["hp"] <= 30)),
    ("Elegant Cape on the Active Ninetales ex at position 6 (the continuation study's hiding case)",
     first(tl_p, lambda e: e["ctx"]["position"] == "B-210952-t16" and e["ctx"]["first"] == "plans_first_move")),
    ("Elegant Cape on a Benched Mega Sharpedo ex that never attacks while carrying it, with time to",
     first(tl_p, lambda e: e["carrier"]["name"] == "Mega Sharpedo ex" and e["carrier"]["slot"] != 0 and e["never_attacked"] and ((e["ended"]["turn"] if e["ended"] else e["game_end_turn"]) - e["turn"]) >= 4)),
    ("Protective Poncho on the Active (it protects only on the Bench)", first(tl_g, lambda e: e["tool"] == "Protective Poncho" and e["carrier"]["slot"] == 0 and e["never_attacked"] and not e["ended"])),
    ("Giant Cape on a Suicune ex that never attacks while carrying it, with time to",
     first(tl_g, lambda e: e["tool"] == "Giant Cape" and e["carrier"]["name"] == "Suicune ex" and e["never_attacked"] and ((e["ended"]["turn"] if e["ended"] else e["game_end_turn"]) - e["turn"]) >= 4)),
    ("Pokémon Center Lady healing 20 or less", first(he_g, lambda e: e["card"] == "Pokémon Center Lady" and e["healed"] <= 20 and not e["conditions"])),
    ("Irida healing 20 or less in km3's own game", first(he_g, lambda e: e["card"] == "Irida" and e["healed"] <= 20)),
    ("Irida with Misty playable, in a play-out", first(he_p, lambda e: any(c["card"] == "Misty" and c["now"] for c in e["hand_before"]["cards"]) and e["healed"] == 40)),
]
print("# The 20 examples (generated by examples.py from the event files; each is the first event in file order that meets its criterion)\n")
for i, (title, e) in enumerate(picks, 1):
    print(f"{i}. **{title}.** {show(e)}\n")
