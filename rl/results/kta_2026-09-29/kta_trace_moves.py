#!/usr/bin/env python3
"""Per-game move records for kta's Rayquaza traces (REGISTRATION.md 5.5, "Scorching Interruption: no prediction", and
3.2's trace seeds), so the reading can tally, over the traces' changed games, the kind of the first decision that
differs between the arms. trace_pilot.py (run beside it on the same seeds, unchanged) gives the per-turn offered/used
counts; its per-game rows carry no moves, which is why this file exists.

    python3 kta_trace_moves.py --deck RAYQUAZA --opp OPP --games 200 --seed S --pilot kta3 --opp-pilot kog3
                               --engine <the kt build's deckgym> --expect-sha SHA --out FILE

The deck sits in seat 0 in every game (as trace_pilot.py plays it), seeds S .. S+games-1 (--seed-stream), one
`deckgym simulate` call through decks/screen/floor.py's run_call (every game completed, printed wins equal the result
files, one trace file per ply). One JSON line per game: seed, won (seat 0's), draw, turns, plies, moves (blake2b over
every chosen move, as kt_ab_play.py computes it; equal = identical games) and decisions, one entry per ply:
[ply, actor, turn, number of legal moves, kind, label, h], where kind is the chosen move's kind (Play, Attack,
AttachTool, UseAbility, Evolve, Place, Retreat, EndTurn, ...), label the card or attack it names when it names one, and
h an 8-hex digest of the chosen move itself (two plies are the same choice only when h is equal).
"""
import argparse, hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "decks", "screen"))
import floor  # noqa: E402  decks/screen/floor.py: run_call, body, card_fields


def label(kind, v, st, actor):
    try:
        if kind == "Play":
            return floor.card_fields(v["trainer_card"]).get("name")
        if kind == "AttachTool":
            return floor.card_fields(v["tool_card"]).get("name")
        if kind == "Attack":
            return v.get("title") if isinstance(v, dict) else str(v)
        if kind == "UseAbility":
            slot = st["in_play_pokemon"][actor][v["in_play_idx"]]
            return floor.card_fields(slot["card"]).get("name") if slot else None
        if kind == "Evolve":
            return floor.card_fields(v["evolution"]).get("name")
        if kind == "Place":
            return floor.card_fields(v[0]).get("name")
    except (KeyError, TypeError, IndexError, AttributeError):
        return None
    return None


def record(result, plies):
    fp = hashlib.blake2b(digest_size=8)
    decisions = []
    for k, p in enumerate(plies):
        text = json.dumps(p["chosen_action"], sort_keys=True).encode()
        fp.update(text)
        kind, v = floor.body(p["chosen_action"])
        decisions.append([k, p["actor"], p["state"]["turn_count"], len(p["playable_actions"]), kind,
                          label(kind, v, p["state"], p["actor"]), hashlib.blake2b(text, digest_size=4).hexdigest()])
    out = result["outcome"]
    return {"seed": result["randomness"]["game_seed"], "won": out == {"Win": 0},
            "draw": out not in ({"Win": 0}, {"Win": 1}), "turns": result["final_turn"], "plies": result["plies"],
            "moves": fp.hexdigest(), "decisions": decisions}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", required=True); ap.add_argument("--opp", required=True)
    ap.add_argument("--games", type=int, required=True); ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--pilot", required=True); ap.add_argument("--opp-pilot", default="kog3")
    ap.add_argument("--engine", required=True); ap.add_argument("--expect-sha", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    for code in (a.pilot, a.opp_pilot):
        if code.lower() == "jev":
            raise SystemExit("the jev bot calls a paid API and is not allowed here")
    engine = os.path.abspath(a.engine)
    sha = hashlib.sha256(open(engine, "rb").read()).hexdigest()
    if not sha.startswith(a.expect_sha):
        raise SystemExit(f"REFUSED: {engine} sha256 {sha[:16]} is not {a.expect_sha}")
    rows = []
    floor.run_call(engine, a.deck, a.opp, f"{a.pilot},{a.opp_pilot}", a.games, a.seed, 0,
                   lambda r, plies: rows.append({**record(r, plies), "pilot": a.pilot, "opp_pilot": a.opp_pilot}))
    with open(a.out, "w", encoding="utf-8") as f:
        for r in sorted(rows, key=lambda r: r["seed"]):
            f.write(json.dumps(r) + "\n")
    print(f"{os.path.basename(a.deck)} (seat 0, {a.pilot}) v {os.path.basename(a.opp)} ({a.opp_pilot}): {len(rows)} games, "
          f"seeds {a.seed}+ (--seed-stream); engine sha256 {sha}")


if __name__ == "__main__":
    main()
