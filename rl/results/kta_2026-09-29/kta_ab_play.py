#!/usr/bin/env python3
"""One arm of kta's fresh Dustin-deck A/B on one deck (kta REGISTRATION.md 5.6 and section 4, check 3).

A copy of ../kt_tables_2026-09-28/kt_ab_play.py (committed; kt's A/B tool) with two options added and nothing else
changed: --block (the seed block; default kta's fresh A/B block 23,004,000,000, REGISTRATION.md 3.2) and
--max-opponents (play only the first K of the eight sorted panel lists; default 8; section 4's check 3 replays deck 07's
first matchup, K = 1, at the development block 22,600,000,000). The gate check is kept unchanged: a kt code (kta3
starts with "kt") refuses to play unless the --gate file exists; run_kta_ab.sh passes the existing
../kt_tables_2026-09-28/GATE_koh_b2e_read with --gate (REGISTRATION.md 5.6). The default gate path is this folder's,
where no gate file exists, so without --gate a kt code is refused.

    python3 kta_ab_play.py --deck 07 --pilot kog3 --engine <the kt build's deckgym> --out FILE.jsonl.part
                           [--meta-pilot kog3] [--games 240] [--expect-sha 407976366fa2104e] [--gate FILE]
                           [--block 23004000000] [--max-opponents 8]

The deck (decks/dustin/<NN>-*.txt) is piloted by --pilot on its own seat; the eight lists in decks/screen/opponents
are piloted by --meta-pilot (kog3 in every arm). 240 games per matchup, half with the deck in seat 0 and half in seat 1
(decks/screen/floor.py's split), so 1,920 games per arm. Seeds, --seed-stream:

    BLOCK + 10,000 x deck number + 1,000 x opponent index (+500 for the deck in seat 1) + i,   i < 120

(opponent index = position in sorted order, altaria 0 to weezing 7; deck number as in the file name, 01-15). Every arm
plays the same seeds, so a game in one arm pairs with the same seed in another.

It reuses decks/screen/floor.py's run_call: one `deckgym simulate --seed-stream --data-output ... --results-output ...`
call per (opponent, seat), checked as the floor checks it (every game completed, printed wins equal the result files,
one trace file per ply), traces read one game at a time and deleted. Only the engine differs: floor.py resolves the
official engine, so here run_call is handed the kt build's own deckgym, whose sha256 is printed and checked.

One JSON line per game: deck, opp, seat, i, seed, pilot, won (the deck's), draw, turns, points, plies, a move
fingerprint over every chosen move (both seats; equal fingerprints = identical games), and the measures, read from the
deck's own decisions with the census's definitions (rl/results/tool_turn_effect_census_2026-09-25/README.md):
  plays  {card: [turns offered, turns played]}: the deck's turns on which playing Jasmine / a watched Tool was among
         the legal moves at some decision, and the turns on which it was played (a turn counts once);
  tools  one entry per Metal Core Barrier / Steel Apron / Heavy Helmet attached (the AttachTool that follows the Play):
         [tool, turn, spot, holder, holder type, holder's printed Retreat Cost, holder qualifies]. Qualifies: Barrier and
         Apron need an [M] holder (the card texts); Heavy Helmet needs a holder whose Retreat Cost is 3 or more (printed
         cost of the holder at that moment; none of decks 01 and 03 runs a Retreat-cost Tool).
"""
import argparse, glob, hashlib, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "decks", "screen"))
import floor  # noqa: E402  decks/screen/floor.py: run_call, body, card_fields

FRESH_BLOCK = 23_004_000_000      # kta's fresh A/B sub-block, REGISTRATION.md 3.2 (23,004,000,000 - 23,004,999,999)
WATCH_PLAYS = ("Jasmine", "Metal Core Barrier", "Steel Apron", "Heavy Helmet")
WATCH_TOOLS = ("Metal Core Barrier", "Steel Apron", "Heavy Helmet")
DEFAULT_GATE = os.path.join(HERE, "GATE_koh_b2e_read")


def qualifies(tool, energy_type, retreat):
    if tool == "Heavy Helmet":
        return retreat >= 3
    return energy_type == "Metal"      # Metal Core Barrier, Steel Apron: "The [M] Pokemon this card is attached to"


def record(result, plies, seat, deck_no, opp, oi, seed0):
    """The per-game row (see the module docstring)."""
    out = result["outcome"]
    seed = result["randomness"]["game_seed"]
    offered = {n: set() for n in WATCH_PLAYS}
    played = {n: set() for n in WATCH_PLAYS}
    tools = []
    fp = hashlib.blake2b(digest_size=8)
    for p in plies:
        fp.update(json.dumps(p["chosen_action"], sort_keys=True).encode())
        if p["actor"] != seat:
            continue
        st, t = p["state"], p["state"]["turn_count"]
        for a in p["playable_actions"]:
            kind, v = floor.body(a)
            if kind == "Play":
                name = floor.card_fields(v["trainer_card"]).get("name")
                if name in offered:
                    offered[name].add(t)
        kind, v = floor.body(p["chosen_action"])
        if kind == "Play":
            name = floor.card_fields(v["trainer_card"]).get("name")
            if name in played:
                played[name].add(t)
        elif kind == "AttachTool":
            name = floor.card_fields(v["tool_card"]).get("name")
            if name in WATCH_TOOLS:
                idx = v["in_play_idx"]
                slot = floor.card_fields(st["in_play_pokemon"][seat][idx]["card"])
                retreat = len(slot.get("retreat_cost") or [])
                tools.append([name, t, "Active" if idx == 0 else "Bench", slot.get("name"), slot.get("energy_type"),
                              retreat, qualifies(name, slot.get("energy_type"), retreat)])
    return {"deck": deck_no, "opp": opp, "seat": seat, "i": seed - seed0, "seed": seed,
            "won": out == {"Win": seat}, "draw": out not in ({"Win": 0}, {"Win": 1}),
            "turns": result["final_turn"], "points": result["final_points"], "plies": result["plies"],
            "moves": fp.hexdigest(),
            "plays": {n: [len(offered[n]), len(played[n] & offered[n])] for n in WATCH_PLAYS if offered[n] or played[n]},
            "tools": tools}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", required=True, help="Dustin's deck number, e.g. 07 (decks/dustin/07-*.txt)")
    ap.add_argument("--pilot", required=True, help="the deck's bot: kog3 or kta3")
    ap.add_argument("--meta-pilot", default="kog3", help="the opponent lists' bot (kog3 in every arm)")
    ap.add_argument("--engine", required=True, help="the kt build's deckgym")
    ap.add_argument("--expect-sha", default=None, help="refuse unless the engine's sha256 starts with this")
    ap.add_argument("--out", required=True)
    ap.add_argument("--games", type=int, default=240, help="games per matchup (240 as registered; half per seat)")
    ap.add_argument("--gate", default=DEFAULT_GATE, help="a kt code plays only once this file exists")
    ap.add_argument("--opponents", default=os.path.join(ROOT, "decks", "screen", "opponents"))
    ap.add_argument("--block", type=int, default=FRESH_BLOCK, help="the seed block (default kta's fresh 23,004,000,000)")
    ap.add_argument("--max-opponents", type=int, default=8, help="play only the first K sorted panel lists (default 8)")
    a = ap.parse_args()
    if a.games < 2:
        raise SystemExit("--games must be at least 2 (half the games are played in each seat)")
    if not 1 <= a.max_opponents <= 8:
        raise SystemExit("--max-opponents must be 1 to 8")
    for code in (a.pilot, a.meta_pilot):
        if code.lower().startswith("kt") and not os.path.exists(a.gate):
            raise SystemExit(f"REFUSED: {code} is a kt code and the gate file {a.gate} does not exist (no kt game before it)")
        if code.lower() == "jev":
            raise SystemExit("the jev bot calls a paid API and is not allowed here")
    engine = os.path.abspath(a.engine)
    sha = hashlib.sha256(open(engine, "rb").read()).hexdigest()
    if a.expect_sha and not sha.startswith(a.expect_sha):
        raise SystemExit(f"REFUSED: {engine} sha256 {sha[:16]} is not {a.expect_sha}")
    files = sorted(glob.glob(os.path.join(ROOT, "decks", "dustin", f"{a.deck}-*.txt")))
    if len(files) != 1:
        raise SystemExit(f"deck {a.deck}: {len(files)} files match decks/dustin/{a.deck}-*.txt")
    deck, deck_no = files[0], int(a.deck)
    opps = sorted(glob.glob(os.path.join(a.opponents, "*.txt")))
    if len(opps) != 8:
        raise SystemExit(f"expected the 8 panel lists in {a.opponents}, found {len(opps)}")
    opps = opps[:a.max_opponents]       # the index oi below stays the position among all eight
    t0, n_games, wins = time.time(), 0, 0
    print(f"kta Dustin-deck A/B: {os.path.relpath(deck, ROOT)} piloted by {a.pilot} on its own seat, "
          f"{a.meta_pilot} on {len(opps)} of the 8 lists in {os.path.relpath(a.opponents, ROOT)}; {a.games} games per matchup")
    print(f"engine {engine} sha256 {sha}")
    print(f"seeds {a.block} + 10,000 x {deck_no} + 1,000 x opponent index (+500 seat 1) + i, --seed-stream")
    with open(a.out, "w", encoding="utf-8") as f:
        for oi, opp in enumerate(opps):
            oname = os.path.splitext(os.path.basename(opp))[0]
            h, cell_wins, cell_n = a.games // 2, 0, 0
            for seat, n in ((0, h), (1, a.games - h)):
                seed0 = a.block + 10_000 * deck_no + 1_000 * oi + (500 if seat else 0)
                p0, p1 = (deck, opp) if seat == 0 else (opp, deck)
                players = f"{a.pilot},{a.meta_pilot}" if seat == 0 else f"{a.meta_pilot},{a.pilot}"
                rows = []
                floor.run_call(engine, p0, p1, players, n, seed0, seat,
                               lambda r, plies, seat=seat, seed0=seed0: rows.append(
                                   {**record(r, plies, seat, deck_no, oname, oi, seed0), "pilot": a.pilot,
                                    "opp_pilot": a.meta_pilot}))
                for r in sorted(rows, key=lambda r: r["seed"]):
                    f.write(json.dumps(r) + "\n")
                f.flush()
                cell_wins += sum(r["won"] for r in rows)
                cell_n += len(rows)
            wins, n_games = wins + cell_wins, n_games + cell_n
            print(f"  {oname:14s} {cell_wins:3d}/{cell_n} = {100 * cell_wins / cell_n:5.1f}%", flush=True)
    print(f"{os.path.basename(deck)}: {wins}/{n_games} = {100 * wins / n_games:.2f}% ({a.pilot} on the deck), "
          f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
