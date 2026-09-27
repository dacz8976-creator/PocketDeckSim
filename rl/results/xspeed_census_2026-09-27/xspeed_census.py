"""Does kp3 waste X Speed? (Dustin, Sept 27, on quiz 2 Q02's game: X Speed played, then no free retreat into Bonsly
for Teary Attack.) Worth a fix only if it is common.
For the 10 decks that run X Speed (the Trainer audit's list), kp3 on both sides against the 8 panel lists, 15 games per
opponent per seat (240 per deck), official engine (rl/engine-2026-09-27), per-decision traces read one game at a time
and deleted (the Trainer audit's method, trainer_audit.py).
Seeds: 22,800,000,000 + 10,000 x deck index + 1,000 x opponent index (+500 for seat 1).
Per own turn with X Speed played: did the same side retreat later that turn; if not, was a Retreat offered later that
turn (a choice, not blocked); did it attack; and the turn's move kinds for the first examples.
Usage: python3 xspeed_census.py OUTDIR"""
import collections, glob, json, os, shutil, subprocess, sys, tempfile
from multiprocessing import Pool

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
ENGINE = f"{R}/rl/engine-2026-09-27/deckgym"
OPP = sorted(glob.glob(f"{R}/decks/screen/opponents/*.txt"))
DECKS = ["research/lucario", "research/vespiquen", "research/weezing", "dustin/04-absol-hoopa-darkrai",
         "dustin/12-ariados-whimsicott-ogerpon", "brews/brew-02-arceus-tandemaus-persian",
         "brews/brew-03a-arceus-nihilego-toxapex", "brews/brew-04-xatu-slowking", "brews/brew-05-meowstic-hatterene-confusion",
         "brews/brew-07-hoopa-darkrai-sableye"]
PER = 15


def fields(card):
    return next(iter(card.values())) if isinstance(card, dict) and len(card) == 1 and next(iter(card)) in ("Pokemon", "Trainer") else card


def body(a):
    x = a["action"]
    return (x, None) if isinstance(x, str) else next(iter(x.items()))


def played_name(a):
    k, v = body(a)
    return fields(v["trainer_card"]).get("name") if k == "Play" else None


def turns(plies, seat):
    by = collections.OrderedDict()
    for p in plies:
        if p["actor"] == seat and p["state"]["current_player"] == seat:
            by.setdefault(p["state"]["turn_count"], []).append(p)
    out = []
    for t, ps in by.items():
        idx = [n for n, p in enumerate(ps) if played_name(p["chosen_action"]) == "X Speed"]
        if not idx:
            continue
        after = ps[idx[0] + 1:]
        kinds = [body(p["chosen_action"])[0] if body(p["chosen_action"])[0] != "Play" else f"Play {played_name(p['chosen_action'])}"
                 for p in ps]
        out.append({"turn": t, "retreated": any(body(p["chosen_action"])[0] == "Retreat" for p in after),
                    "retreat_offered_after": any(any(body(a)[0] == "Retreat" for a in p["playable_actions"]) for p in after),
                    "attacked": any(body(p["chosen_action"])[0] == "Attack" for p in ps), "kinds": kinds})
    return out


def job(args):
    di, oi, seat = args
    deck = f"{R}/decks/{DECKS[di]}.txt"
    seed = 22_800_000_000 + 10_000 * di + 1_000 * oi + (500 if seat else 0)
    p0, p1 = (deck, OPP[oi]) if seat == 0 else (OPP[oi], deck)
    tmp = tempfile.mkdtemp(prefix="xs_")
    rows = []
    try:
        subprocess.run(["nice", "-n", "10", ENGINE, "simulate", "--num", str(PER), "--players", "kp3,kp3", "--seed", str(seed),
                        "--seed-stream", "-j", "1", "--data-output", f"{tmp}/d", "--results-output", f"{tmp}/r", p0, p1],
                       cwd=R, capture_output=True, text=True, check=True)
        for gdir in sorted(glob.glob(f"{tmp}/d/*")):
            plies = [json.load(open(f)) for f in sorted(glob.glob(f"{gdir}/ply_*.json"))]
            rows.append({"deck": DECKS[di], "opp": os.path.basename(OPP[oi])[:-4], "seat": seat, "seed": seed,
                         "game_id": os.path.basename(gdir), "xspeed_turns": turns(plies, seat)})
        return rows
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    jobs = [(di, oi, seat) for di in range(len(DECKS)) for oi in range(len(OPP)) for seat in (0, 1)]
    with Pool(10) as pool, open(f"{outdir}/games.jsonl", "w") as f:
        for n, rows in enumerate(pool.imap_unordered(job, jobs), 1):
            for r in rows:
                f.write(json.dumps(r) + "\n")
            f.flush()
    tot = collections.defaultdict(collections.Counter)
    ex = []
    for r in map(json.loads, open(f"{outdir}/games.jsonl")):
        c = tot[r["deck"]]
        c["games"] += 1
        for t in r["xspeed_turns"]:
            c["xspeed turns"] += 1
            c["retreated"] += t["retreated"]
            if not t["retreated"]:
                c["no retreat"] += 1
                c["no retreat, retreat offered later"] += t["retreat_offered_after"]
                c["no retreat, attacked"] += t["attacked"]
                if len(ex) < 25:
                    ex.append(f"{r['deck']} v {r['opp']} seed {r['seed']} game {r['game_id']} turn {t['turn']}: {' > '.join(t['kinds'])}")
    with open(f"{outdir}/summary.txt", "w") as f:
        for d, c in tot.items():
            f.write(f"{d}: {c['games']} games, X Speed turns {c['xspeed turns']}, retreated after {c['retreated']}, "
                    f"no retreat {c['no retreat']} (retreat still offered {c['no retreat, retreat offered later']}; "
                    f"attacked {c['no retreat, attacked']})\n")
        a = sum(tot.values(), collections.Counter())
        f.write(f"ALL: {a['games']} games, X Speed turns {a['xspeed turns']}, retreated after {a['retreated']}, no retreat "
                f"{a['no retreat']} (retreat still offered {a['no retreat, retreat offered later']}; attacked {a['no retreat, attacked']})\n")
        f.write("\nfirst examples of X Speed without a retreat (the turn's moves):\n" + "\n".join(ex) + "\n")
    print(open(f"{outdir}/summary.txt").read())
