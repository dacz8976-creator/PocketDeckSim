"""What kp3 does with Field Blower and Stadiums, in every deck that carries them.

For each deck with Field Blower or a Stadium (from the Trainer audit): kp3 on both sides against the 8 lists in
decks/screen/opponents, 15 games per opponent per seat, official engine, one thread per call at the lowest priority
(the Altaria training shares the machine). Per-decision traces are read one game at a time and deleted.
Seeds: 21,105,000,000 + 10,000 x deck index + 1,000 x opponent index (+500 for seat 1).

Recorded for the deck's seat, per game:
- blower_turns: each turn Field Blower was playable, with what was on the board then (Tools on each side by name,
  the Stadium and whose it is) and, if it was played, the target chosen (own/opponent Tool by name, or the Stadium).
- stadium_turns: each turn a Stadium card could be played, with the Stadium already in play (none / own / opponent's)
  and whether the bot played it.
- use_stadium: turns a Stadium's once-a-turn effect was offered and turns it was used, by Stadium.
Usage: blower_stadium.py OUTDIR [--smoke]
"""
import glob, json, os, shutil, subprocess, sys, tempfile
from multiprocessing import Pool

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
ENGINE = f"{R}/rl/engine-2026-09-25/deckgym"
OPP = sorted(glob.glob(f"{R}/decks/screen/opponents/*.txt"))
AUDIT = f"{R}/rl/results/trainer_audit_2026-09-25/audit_trainers.tsv"
PER = 15


def decks_with_cards():
    out = set()
    for line in list(open(AUDIT, encoding="utf-8"))[1:]:
        deck, card, kind = line.split("\t")[:3]
        if card == "Field Blower" or kind == "Stadium":
            out.add(deck)
    return sorted(out)


DECKS = decks_with_cards()


def fields(card):
    return next(iter(card.values())) if isinstance(card, dict) and len(card) == 1 and next(iter(card)) in ("Pokemon", "Trainer") else card


def body(a):
    x = a["action"]
    return (x, None) if isinstance(x, str) else next(iter(x.items()))


def board(st, seat):
    tools = {"own": [], "opp": []}
    for p in (0, 1):
        for k, slot in enumerate(st["in_play_pokemon"][p]):
            if slot:
                for t in slot.get("attached_tools") or []:
                    tools["own" if p == seat else "opp"].append(
                        f"{fields(t).get('name')}@{'Active' if k == 0 else 'Bench'}:{fields(slot['card']).get('name')}")
    stad = st.get("active_stadium")
    owner = st.get("active_stadium_owner")
    return tools, (fields(stad).get("name") if stad else None), (None if not stad else "own" if owner == seat else "opp")


def analyse(plies, seat):
    blower, stadium, use = {}, {}, {}
    pending_blower = None
    for p in plies:
        if p["actor"] != seat:
            continue
        st = p["state"]
        t = st["turn_count"]
        kind, v = body(p["chosen_action"])
        if pending_blower is not None:  # the target choice right after playing Field Blower
            if kind == "DiscardToolFromPokemon":
                who = "own" if v["player"] == seat else "opp"
                slot = st["in_play_pokemon"][v["player"]][v["in_play_idx"]]
                tl = slot.get("attached_tools") or []
                ti = v.get("tool_idx", 0) or 0
                name = fields(tl[ti]).get("name") if ti < len(tl) else "?"
                blower[pending_blower]["target"] = f"{who} Tool {name}@{'Active' if v['in_play_idx'] == 0 else 'Bench'}"
            elif kind == "DiscardActiveStadium":
                _, sname, sown = board(st, seat)
                blower[pending_blower]["target"] = f"{sown} Stadium {sname}"
            else:
                blower[pending_blower]["target"] = f"(no choice: {kind})"
            pending_blower = None
        offered_play = {}
        uses = set()
        for a in p["playable_actions"]:
            k, av = body(a)
            if k == "Play":
                c = fields(av["trainer_card"])
                offered_play[c.get("name")] = c.get("trainer_card_type")
            elif k == "UseStadium":
                uses.add(True)
        tools, sname, sown = board(st, seat)
        if "Field Blower" in offered_play and t not in blower:
            blower[t] = {"turn": t, "own_tools": tools["own"], "opp_tools": tools["opp"], "stadium": sname,
                         "stadium_owner": sown, "played": False, "target": None}
        for name, tt in offered_play.items():
            if tt == "Stadium" and (t, name) not in stadium:
                stadium[(t, name)] = {"turn": t, "card": name, "in_play": sname, "in_play_owner": sown, "played": False}
        if uses and sname:
            use.setdefault(sname, {"offered_turns": set(), "used_turns": set()})["offered_turns"].add(t)
        if kind == "Play":
            c = fields(v["trainer_card"])
            if c.get("name") == "Field Blower":
                # the board when it was played (earlier moves this turn, e.g. a gust, may have changed it)
                blower[t] = {"turn": t, "own_tools": tools["own"], "opp_tools": tools["opp"], "stadium": sname,
                             "stadium_owner": sown, "played": True, "target": None}
                pending_blower = t
            if c.get("trainer_card_type") == "Stadium" and (t, c.get("name")) in stadium:
                stadium[(t, c.get("name"))]["played"] = True
        elif kind == "UseStadium" and sname:
            use.setdefault(sname, {"offered_turns": set(), "used_turns": set()})["used_turns"].add(t)
    return {"blower_turns": list(blower.values()), "stadium_turns": list(stadium.values()),
            "use_stadium": {k: {"offered": len(x["offered_turns"]), "used": len(x["used_turns"])} for k, x in use.items()}}


def job(args):
    di, oi, seat, per = args
    deck = f"{R}/decks/{DECKS[di]}.txt"
    seed = 21_105_000_000 + 10_000 * di + 1_000 * oi + (500 if seat else 0)
    p0, p1 = (deck, OPP[oi]) if seat == 0 else (OPP[oi], deck)
    tmp = tempfile.mkdtemp(prefix="bs_")
    rows = []
    try:
        subprocess.run(["nice", "-n", "19", ENGINE, "simulate", "--num", str(per), "--players", "kp3,kp3", "--seed", str(seed),
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
                         "game_id": os.path.basename(gdir), "won": res.get("outcome") == {"Win": seat}, **analyse(plies, seat)})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    if "--smoke" in sys.argv:
        di = DECKS.index("research/lucario") if "research/lucario" in DECKS else 0
        for r in job((di, 0, 0, 2)) + job((di, 1, 1, 2)):
            print(json.dumps(r)[:1500])
        print("decks:", len(DECKS), DECKS)
        sys.exit(0)
    json.dump({"decks": DECKS, "opponents": [os.path.basename(o) for o in OPP], "per_call": PER},
              open(f"{outdir}/plan.json", "w"), indent=1)
    jobs = [(di, oi, seat, PER) for di in range(len(DECKS)) for oi in range(len(OPP)) for seat in (0, 1)]
    with Pool(3) as pool, open(f"{outdir}/games.jsonl", "w") as f:
        for n, rows in enumerate(pool.imap_unordered(job, jobs), 1):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            f.flush()
            if n % 16 == 0:
                print(f"{n}/{len(jobs)} calls", flush=True)
    print("done", flush=True)
