"""km3 unplayed-Trainer diagnosis (Sept 30): from trainer_diag's rows (rows_<deck>.jsonl.gz), one row per chance turn
(turns.jsonl) and the counts the README quotes. A chance turn is the floor's opportunity: one of the deck's turns on
which playing the card from hand was offered at some decision; for a Supporter (Iris), turns on which the deck played
another Supporter are left out. "Used" means the card was played that turn.
First it checks: every replay ends as the floor's per-game file says (points, turns, winner), at every probed
decision the move km3 played has the best root score (ties between two copies of one move are allowed), and each
game's chance turns and uses equal the floor's own count (its "flagged" field).
Usage: python3 analyze.py   (writes turns.jsonl, prints the summary)"""
import gzip, json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FLOOR = HERE.parent / "floor_dustin_2026-09-30"
DECKS = {"11-archaludon-haxorus-dragonair": "Iris",
         "14-comfey-raticate-hypno": "Team Rocket's Goo-zooka",
         "15-jolteon-oricorio-raticate": "Team Rocket's Goo-zooka"}
GUSTS = ("Cyrus", "Sabrina", "Entrap")          # moves that choose the opponent's new Active this turn


def kind(move):
    """A short name for a move."""
    if move.startswith("Play { trainer_card:"):
        return "play " + move.split("trainer_card: ", 1)[1].split(" ", 2)[2].rstrip(" }")
    if move.startswith("Attack("):
        return "attack " + move.split('title: "', 1)[1].split('"', 1)[0]
    return move.split(" {")[0].split("(")[0]


out, summary = [], {}
for deck, card in DECKS.items():
    rows = [json.loads(l) for l in gzip.open(HERE / f"rows_{deck}.jsonl.gz", "rt")]
    floor = {(r["opponent"], r["seat"], r["seed"]): r for r in map(json.loads, open(FLOOR / f"{deck}_games.jsonl"))}
    done = [r for r in rows if r.get("done")]
    same = sum(1 for d in done if (lambda f: f["points"] == d["points"] and f["turns"] == d["turns"]
                                   and f["won"] == (d["winner"] == f"Some(Win({d['seat']}))"))(floor[(d["opponent"], d["seat"], d["seed"])]))
    probes = [r for r in rows if "moves" in r]
    best_played = sum(1 for r in probes
                      if abs(max(m["score"] for m in r["moves"]) - [m["score"] for m in r["moves"] if m["move"] == r["chosen"]][0]) < 1e-9)
    assert same == len(done) and best_played == len(probes), (deck, same, len(done), best_played, len(probes))

    by_turn = defaultdict(list)
    for r in rows:
        if not r.get("done"):
            by_turn[(r["opponent"], r["seat"], r["seed"], r["turn"])].append(r)
    keys = sorted(by_turn)
    for k in keys:
        rs = by_turn[k]
        own = [r for r in rs if not r.get("opp_move")]
        probes_t = [r for r in own if "moves" in r]
        if not probes_t:
            continue
        is_card = lambda m: m.startswith("Play { trainer_card:") and card in m
        used = any(is_card(r["chosen"]) for r in own)
        other_supporter = any(r.get("chosen_supporter") and not is_card(r["chosen"]) for r in own)
        if card == "Iris" and other_supporter and not used:
            continue
        p = probes_t[0]
        card_score = [m["score"] for m in p["moves"] if is_card(m["move"])][0]
        best = max(m["score"] for m in p["moves"])
        q = probes_t[-1]                        # the last decision of the turn at which the card was offered
        q_card = [m["score"] for m in q["moves"] if is_card(m["move"])][0]
        q_best = max(m["score"] for m in q["moves"])
        seat = k[1]
        attacks = [r for r in own if r["chosen"].startswith("Attack(")]
        ko_attack = [r for r in attacks if r["track"]["points_after"][seat] > r["track"]["points_before"][seat]]
        row = {"deck": deck, "card": card, "opponent": k[0], "seat": seat, "seed": k[2], "turn": k[3], "used": used,
               "first_offer": {"tick": p["tick"], "km3_played": p["chosen"], "card_score": card_score, "best_score": best,
                               "card_minus_best": round(card_score - best, 6),
                               "static_effect": p["static"]["effect"], "win_scored": best >= 100000.0},
               "last_offer": {"tick": q["tick"], "km3_played": q["chosen"], "card_score": q_card, "best_score": q_best,
                              "card_minus_best": round(q_card - q_best, 6), "static_effect": q["static"]["effect"]},
               "offers": len(probes_t),
               "turn_line": [kind(r["chosen"]) for r in own],
               "attacked": [kind(r["chosen"]) for r in attacks],
               "ko_by_attack": bool(ko_attack),
               "points_before_turn": own[0]["track"]["points_before"],
               "own_board": p["own"], "opp_board": p["opp"]}
        if card == "Iris":
            row["haxorus_attacked"] = any("Frenzied Blade" in r["chosen"] for r in attacks)
            row["haxorus_ko"] = any("Frenzied Blade" in r["chosen"] for r in ko_attack)
            # Would the Haxorus knockout have won without Iris's point? (Pocket's game is to 3 points.)
            hk = [r for r in ko_attack if "Frenzied Blade" in r["chosen"]]
            if hk:
                before, after = hk[0]["track"]["points_before"][seat], hk[0]["track"]["points_after"][seat]
                row["haxorus_ko_points"] = {"before": before, "after": after,
                                            "wins_without_iris": before + (after - before) - (1 if used else 0) >= 3}
        else:
            row["gust_this_turn"] = any(any(g in r["chosen"] for g in GUSTS) for r in own)
            # The opponent's next turn: their first retreat, and the Energy on their Active against its printed cost.
            nxt = by_turn.get((k[0], k[1], k[2], k[3] + 1), [])
            retreats = [r for r in nxt if r.get("opp_move") and r["chosen"].startswith("Retreat")]
            if retreats:
                a = retreats[0]["opp_active_before"] or {}
                row["opp_next_turn_retreat"] = {"from": a.get("name"), "energy": a.get("energy"),
                                                "printed_retreat": a.get("printed_retreat")}
            else:
                row["opp_next_turn_retreat"] = None
        out.append(row)
    # The chance turns and uses found here equal the floor's own count in every replayed game.
    for d in done:
        g = (d["opponent"], d["seat"], d["seed"])
        mine = [r for r in out if r["deck"] == deck and (r["opponent"], r["seat"], r["seed"]) == g]
        assert [len(mine), sum(r["used"] for r in mine)] == floor[g]["flagged"][card], (deck, g)

with open(HERE / "turns.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")

for deck, card in DECKS.items():
    rs = [r for r in out if r["deck"] == deck]
    un = [r for r in rs if not r["used"]]
    band = lambda g: "0 (a tie)" if g == 0 else "-1 (the card leaving the hand)" if g == -1 else "-2 to -20" if g >= -20 else "below -20"
    gap = Counter(band(r["first_offer"]["card_minus_best"]) for r in un)
    gap_last = Counter(band(r["last_offer"]["card_minus_best"]) for r in un)
    print(f"\n== {deck} ({card}): {len(rs)} chance turns in these games, used on {len(rs) - len(un)}")
    print("  static effect (score after playing minus after only discarding), all chance turns:",
          dict(Counter(r["first_offer"]["static_effect"] for r in rs)))
    print("  static effect at the last offer, all chance turns:", dict(Counter(r["last_offer"]["static_effect"] for r in rs)))
    print("  unplayed, card score minus best at the first offer:", dict(gap))
    print("  unplayed, card score minus best at the last offer:", dict(gap_last))
    print("  unplayed, km3's move at the last offer:", dict(Counter(kind(r["last_offer"]["km3_played"]).split(" ")[0] for r in un).most_common()))
    print("  unplayed, km3's move at the first offer:", dict(Counter(kind(r["first_offer"]["km3_played"]).split(" ")[0] + (" " + kind(r["first_offer"]["km3_played"]).split(" ", 1)[1] if kind(r["first_offer"]["km3_played"]).startswith("play") else "") for r in un).most_common()))
    print("  unplayed, the turn attacked:", sum(1 for r in un if r["attacked"]), "| knocked out:", sum(1 for r in un if r["ko_by_attack"]))
    if card == "Iris":
        for used in (True, False):
            g = [r for r in rs if r["used"] is used]
            print(f"  {'used' if used else 'unplayed'}: Haxorus attacked {sum(r['haxorus_attacked'] for r in g)}, "
                  f"Haxorus knocked out {sum(r['haxorus_ko'] for r in g)} "
                  f"(of which the knockout won the game: {sum(1 for r in g if r['haxorus_ko'] and r['first_offer']['win_scored'])}; "
                  f"would have won without Iris's point: {sum(1 for r in g if r['haxorus_ko'] and r['haxorus_ko_points']['wins_without_iris'])})")
            print(f"    {[(r['opponent'], r['seed'], r['turn'], r['haxorus_ko_points']) for r in g if r['haxorus_ko']]}")
    else:
        print("  unplayed, a gust that turn (Cyrus, Sabrina or Entrap):", sum(1 for r in un if r["gust_this_turn"]))
        rt = [r for r in un if r["opp_next_turn_retreat"]]
        exact = [r for r in rt if r["opp_next_turn_retreat"]["energy"] == r["opp_next_turn_retreat"]["printed_retreat"]]
        print(f"  unplayed, the opponent retreated on its next turn: {len(rt)}; "
              f"with exactly its printed Retreat Cost in Energy on the Active: {len(exact)}")
        print("  used turns:", [(r["opponent"], r["seed"], r["turn"], r["first_offer"]["card_minus_best"], r["turn_line"]) for r in rs if r["used"]])
