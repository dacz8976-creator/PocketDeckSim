"""How kp3 uses every Trainer card, in every deck: offered turns, played turns (Supporters: turns with another
Supporter played are counted separately), and, for Tools, where they were attached and whether they ever did anything.

For each of the 36 decks (research, dustin, brews): kp3 on both sides against the 8 lists in decks/screen/opponents,
15 games per opponent per seat (240 games per deck), official engine, one thread per call at the lowest priority (the
Altaria training shares the machine), per-decision traces read one game at a time and deleted.
Seeds: 21,104,000,000 + 10,000 x deck index + 1,000 x opponent index (+500 for seat 1).

Tool episodes (checked against the card texts and the engine by two independent checkers, Sept 25):
- one episode per physical Tool, followed across evolution (keyed on the Basic at the bottom of the holder's stack);
- 'eligible' = the Tool's type/stage/retreat condition holds for the holder (ignoring position);
- the window in which a Tool acts: the opponent's turn (current_player != seat) for HP and defensive Tools, the
  opponent's Attack decisions for damage-reaction Tools, the owner's end of turn for Deceptive Needle, and the
  owner's Retreat decisions for Small Balloon and Inflatable Boat;
- episodes with no window at all (attached as the game ended) are kept but flagged, not counted as wasted.
Usage: trainer_audit.py OUTDIR
"""
import glob, json, os, shutil, subprocess, sys, tempfile
from multiprocessing import Pool

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
ENGINE = f"{R}/rl/engine-2026-09-25/deckgym"
OPP = sorted(glob.glob(f"{R}/decks/screen/opponents/*.txt"))
DECKS = sorted(os.path.relpath(p, f"{R}/decks")[:-4] for p in
               glob.glob(f"{R}/decks/research/*.txt") + glob.glob(f"{R}/decks/dustin/*.txt") + glob.glob(f"{R}/decks/brews/*.txt"))
PER = 15
HP_TOOLS = {"Leaf Cape", "Elegant Cape", "Giant Cape"}
DEFENSIVE = {"Metal Core Barrier", "Steel Apron", "Heavy Helmet", "Protective Poncho", "Rocky Helmet", "Poison Barb", "Lucky Egg"}
RETREAT_TOOLS = {"Small Balloon", "Inflatable Boat"}


def fields(card):
    return next(iter(card.values())) if isinstance(card, dict) and len(card) == 1 and next(iter(card)) in ("Pokemon", "Trainer") else card


def body(a):
    x = a["action"]
    return (x, None) if isinstance(x, str) else next(iter(x.items()))


def eligible(tool, mon):
    """The Tool's own condition on the holder, ignoring position."""
    t, stage, retreat = mon.get("energy_type"), mon.get("stage"), len(mon.get("retreat_cost") or [])
    return {"Leaf Cape": t == "Grass", "Elegant Cape": stage == 1, "Small Balloon": stage == 0 and retreat >= 1,
            "Inflatable Boat": t == "Water" and retreat >= 1, "Metal Core Barrier": t == "Metal", "Steel Apron": t == "Metal",
            "Heavy Helmet": retreat >= 3, "Deceptive Needle": t == "Darkness"}.get(tool, True)


def position_ok(tool, pos):
    if tool == "Protective Poncho":
        return pos == "Bench"
    if tool in ("Rocky Helmet", "Poison Barb", "Deceptive Needle", "Small Balloon", "Inflatable Boat"):
        return pos == "Active"
    return True


def tools_on_board(state, seat):
    """[(base id, tool name, holder fields, pos)]; the base id is the Basic at the bottom of the holder's stack."""
    out = []
    for k, slot in enumerate(state["in_play_pokemon"][seat]):
        if not slot:
            continue
        mon = fields(slot["card"])
        behind = slot.get("cards_behind") or []
        base = fields(behind[0]).get("id") if behind else mon.get("id")
        for t in slot.get("attached_tools") or []:
            out.append((base, fields(t).get("name"), mon, "Active" if k == 0 else "Bench"))
    return out


def tool_episodes(plies, seat):
    live, done = {}, []
    for p in plies:
        st = p["state"]
        cur = {}
        for base, tool, mon, pos in tools_on_board(st, seat):
            cur.setdefault((base, tool), []).append((mon, pos))
        kind, _ = body(p["chosen_action"])
        opp_turn = st["current_player"] != seat
        for key, lst in cur.items():
            for n, (mon, pos) in enumerate(lst):
                ek = (key, n)
                if ek not in live:
                    live[ek] = {"tool": key[1], "holder": mon.get("name"), "holder_type": mon.get("energy_type"),
                                "holder_stage": mon.get("stage"), "pos_at_attach": pos, "turn": st["turn_count"],
                                "eligible_at_attach": eligible(key[1], mon), "ever_eligible": False, "windows": 0,
                                "worked": 0, "evolved_into": []}
                e = live[ek]
                if mon.get("name") != e["holder"] and mon.get("name") not in e["evolved_into"]:
                    e["evolved_into"].append(mon.get("name"))
                ok = eligible(key[1], mon) and position_ok(key[1], pos)
                e["ever_eligible"] |= eligible(key[1], mon)
                tool = key[1]
                if tool in RETREAT_TOOLS:
                    window = p["actor"] == seat and kind == "Retreat" and pos == "Active"
                elif tool == "Deceptive Needle":
                    window = p["actor"] == seat and not opp_turn and kind in ("EndTurn", "Attack") and pos == "Active"
                elif tool in ("Rocky Helmet", "Poison Barb"):
                    window = opp_turn and p["actor"] != seat and kind == "Attack"
                else:
                    window = opp_turn
                if window:
                    e["windows"] += 1
                    e["worked"] += int(ok)
        for ek in [k for k in live if k[0] not in cur or k[1] >= len(cur[k[0]])]:
            done.append(live.pop(ek))
    done.extend(live.values())
    return done


def trainer_counts(plies, seat):
    offered, played, sup_turns, kinds = {}, {}, {}, {}
    for p in plies:
        if p["actor"] != seat:
            continue
        t = p["state"]["turn_count"]
        for a in p["playable_actions"]:
            k, v = body(a)
            if k == "Play":
                c = fields(v["trainer_card"]); n = c.get("name")
                kinds[n] = c.get("trainer_card_type")
                offered.setdefault(n, set()).add(t)
        k, v = body(p["chosen_action"])
        if k == "Play":
            c = fields(v["trainer_card"]); n = c.get("name")
            kinds[n] = c.get("trainer_card_type")
            played.setdefault(n, set()).add(t)
            if c.get("trainer_card_type") == "Supporter":
                sup_turns[t] = n
    out = {}
    for n in set(offered) | set(played):
        off = offered.get(n, set())
        other = {t for t in off if sup_turns.get(t) not in (None, n)} if kinds.get(n) == "Supporter" else set()
        out[n] = {"kind": kinds.get(n), "offered": len(off), "offered_no_other_supporter": len(off - other),
                  "played": len(played.get(n, set()))}
    return out


def job(args):
    di, oi, seat = args
    deck = f"{R}/decks/{DECKS[di]}.txt"
    seed = 21_104_000_000 + 10_000 * di + 1_000 * oi + (500 if seat else 0)
    p0, p1 = (deck, OPP[oi]) if seat == 0 else (OPP[oi], deck)
    tmp = tempfile.mkdtemp(prefix="ta_")
    rows = []
    try:
        subprocess.run(["nice", "-n", "19", ENGINE, "simulate", "--num", str(PER), "--players", "kp3,kp3", "--seed", str(seed),
                        "--seed-stream", "-j", "1", "--data-output", f"{tmp}/d", "--results-output", f"{tmp}/r", p0, p1],
                       cwd=R, capture_output=True, text=True, check=True)
        results = {}
        for f in glob.glob(f"{tmp}/r/*.json"):
            r = json.load(open(f))
            results[r["game_id"]] = r
        for gdir in sorted(glob.glob(f"{tmp}/d/*")):
            plies = [json.load(open(f)) for f in sorted(glob.glob(f"{gdir}/ply_*.json"))]
            res = results.get(os.path.basename(gdir), {})
            rows.append({"deck": DECKS[di], "opp": os.path.basename(OPP[oi])[:-4], "seat": seat, "seed": seed,
                         "game_id": os.path.basename(gdir), "won": res.get("outcome") == {"Win": seat},
                         "trainers": trainer_counts(plies, seat), "tool_episodes": tool_episodes(plies, seat)})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    json.dump({"decks": DECKS, "opponents": [os.path.basename(o) for o in OPP], "per_call": PER}, open(f"{outdir}/plan.json", "w"), indent=1)
    jobs = [(di, oi, seat) for di in range(len(DECKS)) for oi in range(len(OPP)) for seat in (0, 1)]
    with Pool(3) as pool, open(f"{outdir}/games.jsonl", "w") as f:
        for n, rows in enumerate(pool.imap_unordered(job, jobs), 1):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            f.flush()
            if n % 16 == 0:
                print(f"{n}/{len(jobs)} calls", flush=True)
    print("done", flush=True)
