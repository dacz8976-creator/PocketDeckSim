#!/usr/bin/env python3
"""Draft A v the Fire list: the per-game extraction and the results page. Registered in README.md beside this file,
before any game. Not a ranking, not a ladder forecast.

    python3 analyze.py extract --tmp DIR --tag draftA|deck13 --seat 0|1 --seed SEED --num N --coverage FILE --out FILE
        Reads one deckgym call's output (DIR/res: --results-output, DIR/data: --data-output, DIR/stdout.txt: what it
        printed), checks it, and writes one compact record per game (JSON lines, sorted by seed). run.sh calls this
        after each call and then deletes DIR; the traces themselves are not kept (about 2.5 MB a game).
    python3 analyze.py report [--dir DIR] [--allow-partial]
        Reads DIR/games/*.jsonl and DIR/coverage/*.json and writes DIR/RESULTS.md (as RESULTS.md.part, then renamed).
        Refuses an incomplete or duplicated set of games unless --allow-partial (a test run; the page then says PARTIAL).
    python3 analyze.py --self-test

Every definition is the README's (sections 6 and 7). This file applies them; it changes none. It imports
decks/screen/floor.py (sha256 pinned in the README and checked by run.sh) for the trace helpers, the went-first
reading, the coverage flags and the flagged-card counts, so those are read exactly as the floor reads them.
"""
import argparse, glob, json, math, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
for p in (ROOT, os.path.join(ROOT, "lib"), os.path.join(ROOT, "decks", "screen")):
    sys.path.insert(0, p)
import floor  # noqa: E402

SEED_BASE = 23_200_000_000          # README section 4: seed = SEED_BASE + 500 x seat + i, i < 500, the same for both lists
PER_SEAT = 500
PILOT = "km3"
PILOT_PRINTED = "KM { max_depth: 3 }"
LISTS = {"draftA": "decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt",
         "deck13": "decks/dustin/13-a-ninetales-raticate.txt"}
OPPONENT = "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt"
LABEL = {"draftA": "draft A (Shark Tempo)", "deck13": "deck 13 (Alolan Ninetales / Raticate)",
         "opponent": "the Charizard Y / Entei list (h-charizardy_entei)"}
SHARPEDO, TURBO = "Mega Sharpedo ex", "Turbo Shark"
NINETALES, SNOW = "Alolan Ninetales ex", "Binding Snow"
VULPIX, LAPRAS = "Alolan Vulpix", "Lapras"
THREE = (SHARPEDO, NINETALES, LAPRAS)   # README section 6.7: did each of these attack at all, counted separately
Z = 1.96
TURN_COLS = (1, 2, 3, 4, 5, 6, "7+")


# --- intervals (README section 7) --------------------------------------------------------------------------------------

def wilson(w, n):
    """95% Wilson score interval for w wins in n games: (low, high), as fractions."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = w / n
    den = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / den
    half = Z / den * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (max(0.0, centre - half), min(1.0, centre + half))


def paired(diffs):
    """Mean of the per-deal differences and its 95% normal interval: mean +- 1.96 x sd / sqrt(n), sd with n - 1."""
    n = len(diffs)
    if n < 2:
        return (sum(diffs) / n if n else float("nan"), float("nan"), float("nan"), float("nan"))
    m = sum(diffs) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in diffs) / (n - 1))
    h = Z * sd / math.sqrt(n)
    return (m, m - h, m + h, sd)


def own_turn(t, went_first):
    """The list's own turn number for game turn t (turn 1 is the first player's first turn)."""
    return (t + 1) // 2 if went_first else t // 2


# --- reading one game's traces (README section 6) ----------------------------------------------------------------------

def deck_ids(path):
    ids = []
    for line in open(os.path.join(ROOT, path), encoding="utf-8-sig"):
        p = line.split()
        if len(p) >= 3 and p[0].isdigit():
            ids += [f"{p[-2]} {p[-1]}"] * int(p[0])
    return sorted(ids)


def deck_names(path):
    """The card names in a list file ("2 Carvanha B4 034" -> "Carvanha")."""
    out = set()
    for line in open(os.path.join(ROOT, path), encoding="utf-8-sig"):
        p = line.split()
        if len(p) >= 4 and p[0].isdigit():
            out.add(" ".join(p[1:-2]))
    return out


def base_id(slot):
    """The first card of an in-play Pokemon (the Basic under any evolution): identifies it across Evolve."""
    behind = slot.get("cards_behind") or []
    return floor.card_fields(behind[0] if behind else slot["card"]).get("id")


def slot_name(slot):
    return floor.card_fields(slot["card"]).get("name") if slot else None


def game_extract(result, plies, seat, flagged):
    """The compact record of one game for the list in `seat` (README section 6)."""
    rec0, off, cho, kept, sup = floor.game_record(result, plies, seat, flagged, set())
    wf = rec0["went_first"]
    attacks, evolves, sharks, arms = [], [], [], []
    tracked = defaultdict(list)     # the list's in-play index -> arm events on the Pokemon there
    pending = None                  # the Turbo Shark whose Bench attach has not come yet
    max_own, mismatches, multi = 0, 0, 0
    per_turn = Counter()

    def close(shark, ended):
        if shark["result"] is None:
            shark["result"] = ("no Benched Water Pokemon" if shark["bench_water"] == 0
                               else "game ended before the attach" if ended else "no attach (other)")

    def swap(a, b):
        ea, eb = tracked.pop(a, []), tracked.pop(b, [])
        if eb:
            tracked[a] = eb
        if ea:
            tracked[b] = ea

    for k, p in enumerate(plies):
        st, actor = p["state"], p["actor"]
        t = st["turn_count"]
        if t >= 1 and st["current_player"] == seat:
            max_own = max(max_own, own_turn(t, wf))
        if pending is not None and t != pending["t"]:
            close(pending, False)
            pending = None
        # 1. each tracked Pokemon must still be where the tracking says (same first card); an empty spot = it left play
        for idx in list(tracked):
            slot = st["in_play_pokemon"][seat][idx]
            if slot is None:
                for e in tracked.pop(idx):
                    e["left_play"] = own_turn(t, wf)
            elif any(base_id(slot) != e["base"] for e in tracked[idx]):
                for e in tracked.pop(idx):
                    e["lost_track"] = True
                    mismatches += 1
        kind, v = floor.body(p["chosen_action"])
        if actor == seat and kind == "Attack":
            ot, name, title = own_turn(t, wf), floor.active_name(st, seat), v.get("title")
            attacks.append([ot, t, name, title])
            per_turn[ot] += 1
            for e in tracked.get(0, []):
                if e["attacked"] is None:
                    e["attacked"] = [ot, name, title]
            if name == SHARPEDO and title == TURBO:
                if pending is not None:
                    close(pending, False)
                bench_water = sum(1 for s in st["in_play_pokemon"][seat][1:]
                                  if s and floor.card_fields(s["card"]).get("energy_type") == "Water")
                pending = dict(own=ot, t=t, bench_water=bench_water, result=None, target=None, energy=None)
                sharks.append(pending)
        elif (actor == seat and kind == "Attach" and not v.get("is_turn_energy") and pending is not None
              and t == pending["t"]):
            amount, energy, idx = v["attachments"][0]
            slot = st["in_play_pokemon"][seat][idx]
            pending.update(result="armed", target=slot_name(slot), energy=energy, idx=idx,
                           offered=sum(1 for a in p["playable_actions"] if floor.body(a)[0] == "Attach"))
            ev = dict(own=pending["own"], target=slot_name(slot), base=base_id(slot), attacked=None, evolved=None,
                      left_play=None, lost_track=False)
            arms.append(ev)
            if idx >= 1:
                tracked[idx].append(ev)
            pending = None
        elif actor == seat and kind == "EndTurn" and pending is not None:
            close(pending, False)
            pending = None
        elif actor == seat and kind == "Evolve":
            ot, into = own_turn(t, wf), floor.card_fields(v["evolution"]).get("name")
            evolves.append([ot, t, into, v["in_play_idx"]])
            for e in tracked.get(v["in_play_idx"], []):     # an armed Pokemon evolving: its first evolution is kept
                e["evolved"] = e["evolved"] or [ot, into]
        # 2. moves of the list's own Pokemon: a retreat (paid at once, or by the ChooseRetreatEnergy that follows it)
        #    swaps the Active and that Bench spot; a promotion moves that Bench spot to the Active Spot; a switch by a
        #    card effect (Activate, either player's choice) swaps the Active and that Bench spot (the engine's
        #    apply_activate, which also applies a promotion)
        if actor == seat and kind == "Retreat":
            nxt = plies[k + 1] if k + 1 < len(plies) else None
            deferred = (nxt is not None and nxt["actor"] == seat
                        and floor.body(nxt["chosen_action"])[0] == "ChooseRetreatEnergy")
            if not deferred:
                swap(0, v)
        elif actor == seat and kind == "ChooseRetreatEnergy":
            swap(0, v["to_in_play_idx"])
        elif kind == "Promote" and v["player"] == seat:
            for e in tracked.pop(0, []):        # not expected: a promotion fills an empty Active Spot (step 1 cleared it)
                e["left_play"] = own_turn(t, wf)
            moved = tracked.pop(v["in_play_idx"], [])
            if moved:
                tracked[0] = moved
        elif kind == "Activate" and v["player"] == seat:
            swap(0, v["in_play_idx"])
    if pending is not None:
        close(pending, True)
    multi = sum(1 for c in per_turn.values() if c > 1)
    for e in arms:
        e.pop("base", None)
    seed = result["randomness"]["game_seed"]
    return dict(seat=seat, seed=seed, game_id=result["game_id"], outcome=result["outcome"],
                won=result["outcome"] == {"Win": seat}, draw=result["outcome"] not in ({"Win": 0}, {"Win": 1}),
                final_points=result["final_points"], final_turn=result["final_turn"], plies=result["plies"],
                lifecycle_errors=result.get("lifecycle_errors"), went_first=wf, max_own_turn=max_own,
                attacks=attacks, evolves=evolves,
                sharks=[{k_: s[k_] for k_ in ("own", "t", "bench_water", "result", "target", "energy")} for s in sharks],
                arms=arms, tracking_mismatches=mismatches, turns_with_two_attacks=multi,
                flag_off={n: {tg: sorted(ts) for tg, ts in off[n].items()} for n in off},
                flag_cho={n: {tg: sorted(ts) for tg, ts in cho[n].items()} for n in cho},
                flag_kept={n: sorted(ts) for n, ts in kept.items()},
                supporter_of={str(t_): i for t_, i in sup.items()})


def extract(a):
    def refuse(msg):
        raise SystemExit(f"REFUSED (extract {a.tag} seat {a.seat} seed {a.seed}): {msg}")
    if a.tag not in LISTS or a.seat not in (0, 1):
        refuse("unknown list or seat")
    if not a.smoke:
        lo = SEED_BASE + PER_SEAT * a.seat
        if not (lo <= a.seed and a.seed + a.num <= lo + PER_SEAT):
            refuse(f"seeds {a.seed}..{a.seed + a.num - 1} are outside seat {a.seat}'s registered range")
    text = open(os.path.join(a.tmp, "stdout.txt"), encoding="utf-8", errors="replace").read()
    if "Player 0 won" not in text:
        refuse("the engine printed no result:\n" + text[-400:])
    printed = tuple(int(re.search(pat, text)[1]) for pat in (r"Player 0 won: (\d+)", r"Player 1 won: (\d+)", r"Draws: (\d+)"))
    results = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(a.tmp, "res", "*.json")))]
    if len(results) != a.num or any(r.get("completion") != "completed" for r in results):
        refuse(f"{len(results)} result files for {a.num} games, or a game not completed")
    seeds = sorted(r["randomness"]["game_seed"] for r in results)
    if seeds != list(range(a.seed, a.seed + a.num)):
        refuse("the games' seeds are not seed .. seed + num - 1")
    want = {a.seat: deck_ids(LISTS[a.tag]), 1 - a.seat: deck_ids(OPPONENT)}
    for r in results:
        decks = r["matchup"]["decks"]
        if any(sorted(decks[s]["card_ids"]) != want[s] for s in (0, 1)):
            refuse(f"game {r['game_id']}: the lists in the seats are not the registered ones")
        if r["matchup"]["player_codes"] != [PILOT_PRINTED, PILOT_PRINTED]:
            refuse(f"game {r['game_id']}: pilots {r['matchup']['player_codes']}, not km3 on both sides")
    wins = [sum(1 for r in results if r["outcome"] == {"Win": s}) for s in (0, 1)]
    if (printed[0], printed[1]) != tuple(wins) or sum(printed) != a.num:
        refuse(f"printed {printed} disagree with the result files {wins}")
    flagged = floor.flagged_cards(json.load(open(a.coverage, encoding="utf-8")), PILOT, floor.database())
    lines = []
    for r in sorted(results, key=lambda r: r["randomness"]["game_seed"]):
        files = sorted(glob.glob(os.path.join(a.tmp, "data", r["game_id"], "ply_*.json")))
        if len(files) != r["plies"]:
            refuse(f"game {r['game_id']}: {len(files)} trace files for {r['plies']} plies")
        rec = game_extract(r, [json.load(open(f, encoding="utf-8")) for f in files], a.seat, flagged)
        rec.update(tag=a.tag, chunk=os.path.basename(a.out).split(".")[0], smoke=bool(a.smoke))
        lines.append(json.dumps(rec, sort_keys=True))
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"extract {a.tag} seat {a.seat} seeds {a.seed}..{a.seed + a.num - 1}: {a.num} games, printed {printed}")


# --- the page -----------------------------------------------------------------------------------------------------------

def pct(x):
    return "n/a" if x != x else f"{100 * x:.1f}%"


def ci(lo_hi):
    lo, hi = lo_hi
    return "n/a" if lo != lo else f"{100 * lo:.1f}-{100 * hi:.1f}%"


def rate(w, n):
    return f"{w}/{n} = {pct(w / n) if n else 'n/a'} ({ci(wilson(w, n))})"


def col(ot):
    return ot if ot <= 6 else "7+"


def line_steps(r):
    """README section 6.5's steps for one draft A game record, each True or False."""
    ev, at = r["evolves"], r["attacks"]
    s1 = any(o <= 2 and n == SHARPEDO for o, t, n, i in ev)
    s2 = any(o == 2 and n == SHARPEDO and ti == TURBO for o, t, n, ti in at)
    s3 = any(s["own"] == 2 and s["result"] == "armed" for s in r["sharks"])
    s4 = any(o <= 3 and n == NINETALES for o, t, n, i in ev)
    s5 = any(o == 3 and ((n, ti) in ((NINETALES, SNOW), (SHARPEDO, TURBO))) for o, t, n, ti in at)
    v2 = [e for e in r["arms"] if e["own"] == 2 and e["target"] == VULPIX]   # own turn 2's arms of a Benched Vulpix
    s3v = bool(v2)
    s4v = any(e["evolved"] and e["evolved"][0] <= 3 and e["evolved"][1] == NINETALES for e in v2)
    return dict(L1=s1, L2=s2, L3=s3, L3v=s3v, L4=s4, L4v=s4v, L5=s5, line2=s2 and s3, line3=s2 and s3 and s4 and s5,
                plan=s2 and s4v and s5)


def attacked_at_all(recs, name):
    """README section 6.7: (games in which `name` made at least one of the list's attacks, its attacks in all)."""
    return (sum(1 for r in recs if any(n == name for o, t, n, ti in r["attacks"])),
            sum(1 for r in recs for o, t, n, ti in r["attacks"] if n == name))


def flagged_use(recs, flagged, deck_path):
    """Floor's flagged-card counts over these games: {name: (opportunities, used, role)} (floor.py's roles)."""
    rel = deck_path.replace(os.sep, "/")
    out = {}
    for name, card in flagged.items():
        ability_offered = any(r["flag_off"].get(name, {}).get("ability") for r in recs)
        role = floor.ROLES.get(rel, {}).get(name) or floor.default_role(card, ability_offered)
        o_n = u_n = 0
        for r in recs:
            off = defaultdict(set, {tg: set(ts) for tg, ts in r["flag_off"].get(name, {}).items()})
            cho = defaultdict(set, {tg: set(ts) for tg, ts in r["flag_cho"].get(name, {}).items()})
            sup = {int(t): i for t, i in r["supporter_of"].items()}
            o_, u_ = floor.role_sets(role, card, off, cho, set(r["flag_kept"].get(name, [])), sup)
            o_n += len(o_)
            u_n += sum(1 for t in u_ if t in o_)
        out[name] = (o_n, u_n, role)
    return out


def report(a):
    d = os.path.abspath(a.dir)
    recs = []
    for f in sorted(glob.glob(os.path.join(d, "games", "*.jsonl"))):
        recs += [json.loads(line) for line in open(f, encoding="utf-8") if line.strip()]
    by = defaultdict(list)
    for r in recs:
        by[r["tag"]].append(r)
    keys = Counter((r["tag"], r["seat"], r["seed"]) for r in recs)
    dup = sorted(k for k, c in keys.items() if c > 1)
    want = {(tag, s, SEED_BASE + PER_SEAT * s + i) for tag in LISTS for s in (0, 1) for i in range(PER_SEAT)}
    missing, extra = want - set(keys), set(keys) - want
    complete = not dup and not missing and not extra
    if not complete and not a.allow_partial:
        raise SystemExit(f"REFUSED: {len(recs)} games; {len(missing)} registered deals missing, {len(extra)} outside "
                         f"the registered seeds, {len(dup)} duplicated. No page (use --allow-partial only for a test).")
    db = floor.database()
    L = ["# Draft A v the Fire list: results", ""]
    if not complete:
        L += [f"**PARTIAL: {len(recs)} games, not the registered 2,000 ({len(missing)} registered deals missing, "
              f"{len(extra)} outside the registered seeds, {len(dup)} duplicated). A test page, not the result.**", ""]
    L += ["Written by `analyze.py report` from `games/*.jsonl` and `coverage/*.json`. Every definition is the README's "
          "(sections 6 to 8). **Not a ranking and not a ladder forecast**: one list against one saved opponent list, "
          "both sides played by the km3 bot.", ""]

    # win rates
    W = {}
    for tag in LISTS:
        g = by.get(tag, [])
        W[tag] = (sum(r["won"] for r in g), len(g), sum(r["draw"] for r in g))
    # paired difference
    idx = {tag: {(r["seat"], r["seed"]): r for r in by.get(tag, [])} for tag in LISTS}
    deals = sorted(set(idx["draftA"]) & set(idx["deck13"]))
    diffs = [int(idx["draftA"][k]["won"]) - int(idx["deck13"][k]["won"]) for k in deals]
    m, lo, hi, sd = paired(diffs)
    if lo != lo:
        reading = "no reading (fewer than two paired deals)"
    elif lo > 0:
        reading = ("the premise holds in this test: draft A beat the Fire list more often than deck 13 did on the "
                   "same deals, by more than the paired interval")
    elif hi < 0:
        reading = ("the premise does not hold in this test (reversed): deck 13 beat the Fire list more often than "
                   "draft A did on the same deals, by more than the paired interval")
    else:
        reading = ("the premise does not hold in this test (no difference seen): the paired interval includes "
                   "zero, so this test cannot tell draft A from deck 13 against the Fire list")
    line = f"**Reading (README section 8): {reading}.**"
    if lo == lo:
        line += (f" Paired difference, draft A minus deck 13: {100 * m:+.1f} points (95% interval {100 * lo:+.1f} to "
                 f"{100 * hi:+.1f}).")
        if abs(m) < 0.05:
            line += (" The point difference is under 5 points, the size START_HERE calls noise for two versions of one "
                     "shell (said for scale only; the reading above is the registered one).")
    L.append(line)
    wA, nA, _ = W["draftA"]
    if nA:
        lA, hA = wilson(wA, nA)
        side = ("above" if lA > 0.5 else "below" if hA < 0.5 else "not distinguishable from")
        L += ["", f"Secondary, descriptive (README section 8): draft A's win rate against this list is {side} 50% "
              f"({pct(wA / nA)}, {ci((lA, hA))})."]
    L += ["", "## Win rates (draws are not wins)", "", "| list | games | wins | draws | win rate | 95% interval (Wilson) |",
          "|---|---|---|---|---|---|"]
    for tag in LISTS:
        w, n, dr = W[tag]
        L.append(f"| {LABEL[tag]} | {n} | {w} | {dr} | {pct(w / n) if n else 'n/a'} | {ci(wilson(w, n))} |")
    both = sum(1 for k in deals if idx["draftA"][k]["won"] and idx["deck13"][k]["won"])
    a_only = sum(1 for x in diffs if x == 1)
    b_only = sum(1 for x in diffs if x == -1)
    L += ["", "## Paired difference (per deal: same seed, same seat)", "",
          f"- Deals played by both lists: {len(deals)}. Difference per deal = (draft A won) - (deck 13 won), each 1 or 0.",
          f"- Mean: {100 * m:+.2f} points; standard deviation of the per-deal differences {sd:.4f}; "
          f"95% interval {100 * lo:+.2f} to {100 * hi:+.2f} points (mean +- 1.96 x sd / sqrt(n))." if lo == lo else
          f"- Mean: {100 * m:+.2f} points; no interval (fewer than two deals).",
          f"- Both won: {both}. Draft A won and deck 13 did not: {a_only}. Deck 13 won and draft A did not: {b_only}. "
          f"Neither won: {len(deals) - both - a_only - b_only}."]
    for s in (0, 1):
        ds = [int(idx["draftA"][k]["won"]) - int(idx["deck13"][k]["won"]) for k in deals if k[0] == s]
        if not ds:
            L.append(f"- Seat {s} only: no deals.")
            continue
        ms, ls, hs, _ = paired(ds)
        L.append(f"- Seat {s} only ({len(ds)} deals, descriptive): {100 * ms:+.1f} points" +
                 (f" ({100 * ls:+.1f} to {100 * hs:+.1f})" if ls == ls else "") + ".")
    differ = sum(1 for k in deals if idx["draftA"][k]["went_first"] != idx["deck13"][k]["went_first"])
    L.append(f"- Deals on which the two lists did not both go first or both go second: {differ} of {len(deals)} "
             "(the same seed decides the opening coin for both, if the engine draws it the same way).")

    # went first / second, seat
    L += ["", "## Went first / went second, and seat", "",
          "| list | went first | went second | seat 0 | seat 1 |", "|---|---|---|---|---|"]
    for tag in LISTS:
        g = by.get(tag, [])
        cells = []
        for sel in (lambda r: r["went_first"] is True, lambda r: r["went_first"] is False,
                    lambda r: r["seat"] == 0, lambda r: r["seat"] == 1):
            h = [r for r in g if sel(r)]
            cells.append(rate(sum(r["won"] for r in h), len(h)))
        L.append(f"| {LABEL[tag]} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("Each cell: wins/games = win rate (95% Wilson interval).")

    # attacks by own turn
    L += ["", "## Attacks by own turn, attacker and attack (the list's own attacks)", ""]
    for tag in LISTS:
        g = by.get(tag, [])
        tab = defaultdict(Counter)
        for r in g:
            for ot, t, name, title in r["attacks"]:
                tab[(name, title)][col(ot)] += 1
        reach = Counter()
        for r in g:
            for c in TURN_COLS:
                if r["max_own_turn"] >= (7 if c == "7+" else c):
                    reach[c] += 1
        L += [f"**{LABEL[tag]}** ({len(g)} games). Each cell: number of attacks (one attack at most per turn, so also "
              "games). Own turn 1 is the list's first turn.", "",
              "| attacker | attack | " + " | ".join(f"turn {c}" for c in TURN_COLS) + " | total |",
              "|---|---|" + "---|" * (len(TURN_COLS) + 1)]
        for (name, title), cnt in sorted(tab.items(), key=lambda x: -sum(x[1].values())):
            L.append(f"| {name} | {title} | " + " | ".join(str(cnt[c]) for c in TURN_COLS) + f" | {sum(cnt.values())} |")
        L.append("| games that reached this own turn | | " + " | ".join(str(reach[c]) for c in TURN_COLS) + " | |")
        L.append("")

    # did each of the three attack at all
    L += ["## Did Mega Sharpedo ex, Alolan Ninetales ex and Lapras attack at all? (README section 6.7)", "",
          "Each row is one Pokemon in one list, counted on its own: a game counts in every row whose Pokemon made at "
          "least one of the list's attacks in it (any of its attacks).", "",
          "| list | Pokemon | games in which it attacked at least once | its attacks, all games |", "|---|---|---|---|"]
    for tag in LISTS:
        g = by.get(tag, [])
        here = deck_names(LISTS[tag])
        for name in THREE:
            if name not in here:
                L.append(f"| {LABEL[tag]} | {name} | not in the list | not in the list |")
                continue
            games, n_att = attacked_at_all(g, name)
            L.append(f"| {LABEL[tag]} | {name} | {games} of {len(g)}" + (f" ({pct(games / len(g))})" if g else "") +
                     f" | {n_att} |")
    L.append("")

    # Sharpedo's line
    g = by.get("draftA", [])
    L += ["## Sharpedo's line (draft A; README section 6.5)", ""]
    if g:
        names = [("L1", "Mega Sharpedo ex evolved by own turn 2"), ("L2", "Turbo Shark was the attack of own turn 2"),
                 ("L3", "that Turbo Shark armed a Benched Pokemon (any Water Pokemon)"),
                 ("L3v", "that Turbo Shark armed a Benched Alolan Vulpix"),
                 ("L4", "Alolan Ninetales ex evolved by own turn 3 (any Vulpix)"),
                 ("L4v", "that armed Alolan Vulpix evolved into Alolan Ninetales ex by own turn 3"),
                 ("L5", "own turn 3's attack was Binding Snow or Turbo Shark"),
                 ("line2", "the line through turn 2 (L2 and L3)"), ("line3", "the line through turn 3 (L2 to L5)"),
                 ("plan", "the plan's line (L2, L4v and L5)")]
        groups = [("all games", g), ("went first", [r for r in g if r["went_first"] is True]),
                  ("went second", [r for r in g if r["went_first"] is False])]
        st_ = {id(r): line_steps(r) for r in g}
        L += ["| step | " + " | ".join(f"{lab} ({len(h)})" for lab, h in groups) + " |", "|---|---|---|---|"]
        for key, lab in names:
            L.append(f"| {key}: {lab} | " + " | ".join(
                (f"{sum(st_[id(r)][key] for r in h)} = {pct(sum(st_[id(r)][key] for r in h) / len(h))}" if h else "n/a")
                for _, h in groups) + " |")
        L.append("| games that reached own turn 2 / 3 | " + " | ".join(
            f"{sum(r['max_own_turn'] >= 2 for r in h)} / {sum(r['max_own_turn'] >= 3 for r in h)}" for _, h in groups) + " |")

        def t2(r):      # own turn 2's Turbo Shark: the arm's target, or why there was no arm (one attack a turn)
            s = [s_ for s_ in r["sharks"] if s_["own"] == 2]
            return (None if not s else f"armed: {s[0]['target']}" if s[0]["result"] == "armed"
                    else f"not armed: {s[0]['result']}")
        cnt = {lab: Counter(t2(r) for r in h) for lab, h in groups}
        rows = sorted((k_ for k_ in cnt["all games"] if k_), key=lambda k_: (not k_.startswith("armed"), -cnt["all games"][k_], k_))
        L += ["", "**Own turn 2's Turbo Shark, by where its Energy went** (games): the arm's target (the Pokemon on that "
              "Bench spot), or why there was no arm.", "",
              "| own turn 2 | " + " | ".join(f"{lab} ({len(h)})" for lab, h in groups) + " |", "|---|---|---|---|"]
        for k_ in rows + [None]:
            L.append(f"| {k_ or 'no Turbo Shark on own turn 2'} | " + " | ".join(str(cnt[lab][k_]) for lab, _ in groups) + " |")
        firsts = {}
        for lab, h in groups:
            firsts[lab] = Counter()
            for r in h:
                ts = [s["own"] for s in r["sharks"]]
                firsts[lab]["never" if not ts else (min(ts) if min(ts) <= 5 else "6+")] += 1
        cols = [k_ for k_ in (1, 2, 3, 4, 5, "6+") if k_ != 1 or firsts["all games"][1]] + ["never"]
        L += ["", "**First Turbo Shark, by own turn** (games). README 6.5 reads the plan as own turn 2 going first and "
              "going second; turn 3 is shown beside it.", "",
              "| games | " + " | ".join(k_ if k_ == "never" else f"turn {k_}" for k_ in cols) + " |", "|---|" + "---|" * len(cols)]
        for lab, h in groups:
            L.append(f"| {lab} ({len(h)}) | " + " | ".join(
                f"{firsts[lab][k_]}" + (f" ({pct(firsts[lab][k_] / len(h))})" if h else "") for k_ in cols) + " |")
        L.append("")
        for key in ("line2",):
            yes = [r for r in g if st_[id(r)][key]]
            no = [r for r in g if not st_[id(r)][key]]
            L.append(f"Win rate when the line through turn 2 happened: {rate(sum(r['won'] for r in yes), len(yes))}; "
                     f"when it did not: {rate(sum(r['won'] for r in no), len(no))}. Descriptive only, not cause and "
                     "effect: games where the bot can play the line are also games with good draws.")
        sharks = [s for r in g for s in r["sharks"]]
        res = Counter(s["result"] for s in sharks)
        L += ["", f"**Turbo Shark and the Bench-arming count.** Turbo Sharks: {len(sharks)} "
              f"({len(sharks) / len(g):.2f} a game; {sum(1 for r in g if r['sharks'])} games with at least one). "
              "Outcome of each: " + ", ".join(f"{k_}: {c}" for k_, c in sorted(res.items())) + "."]
        arms = [e for r in g for e in r["arms"]]
        tgt = Counter(e["target"] for e in arms)
        by_turn = Counter(col(e["own"]) for e in arms)
        L.append(f"Bench-arming count (Turbo Shark Energy attached to a Benched Water Pokemon): {len(arms)} "
                 f"({len(arms) / len(g):.2f} a game; {pct(len(arms) / len(sharks)) if sharks else 'n/a'} of Turbo Sharks). "
                 "By target at the time: " + (", ".join(f"{k_}: {c}" for k_, c in tgt.most_common()) or "none") +
                 ". By own turn: " + ", ".join(f"turn {c}: {by_turn[c]}" for c in TURN_COLS) + ".")
        att = [e for e in arms if e["attacked"]]
        lost = [e for e in arms if not e["attacked"] and e["lost_track"]]
        left = [e for e in arms if not e["attacked"] and not e["lost_track"] and e["left_play"] is not None]
        rest = len(arms) - len(att) - len(left) - len(lost)
        how = Counter((e["attacked"][1], e["attacked"][2]) for e in att)
        L.append(f"After the arming: the armed Pokemon later attacked from the Active Spot in {len(att)} cases "
                 f"({pct(len(att) / len(arms)) if arms else 'n/a'}; first attack: " +
                 (", ".join(f"{n} {t}: {c}" for (n, t), c in how.most_common()) or "none") +
                 f"); left play before attacking in {len(left)}; still in play at the end without attacking in {rest}; "
                 f"tracking lost in {len(lost)} (expected 0; README 6.5).")
        evo = Counter(e["evolved"][1] for e in arms if e["evolved"])
        L.append(f"The armed Pokemon evolved after the arming (its first evolution) in {sum(evo.values())} cases: " +
                 (", ".join(f"into {n}: {c}" for n, c in evo.most_common()) or "none") + ".")
    else:
        L.append("No draft A games.")

    # coverage flags
    L += ["", "## Coverage flags (official goldfish `--coverage`, read as floor.py reads them, pilot km3)", ""]
    for key, path in (("draftA", LISTS["draftA"]), ("deck13", LISTS["deck13"]), ("opponent", OPPONENT)):
        cp = os.path.join(d, "coverage", f"{key}_coverage.json")
        if not os.path.isfile(cp):
            L.append(f"- {LABEL[key]}: no coverage file ({os.path.relpath(cp, d)})")
            continue
        fl = floor.flagged_cards(json.load(open(cp, encoding="utf-8")), PILOT, db)
        if not fl:
            L.append(f"- {LABEL[key]} (`{path}`): no flagged card.")
            continue
        L.append(f"- {LABEL[key]} (`{path}`): " + "; ".join(
            f"{n} ({', '.join(sorted(c['ids']))}): {'; '.join(c['reasons'])}" for n, c in sorted(fl.items())) + ".")
        if key in LISTS and by.get(key):
            use = flagged_use(by[key], fl, path)
            L.append("  - In these games, as the floor counts them: " + "; ".join(
                f"{n} as {role}: used on {us} of {op} opportunities" + (f" ({pct(us / op)})" if op else "")
                for n, (op, us, role) in sorted(use.items())) + ".")

    # checks
    lc = sum(1 for r in recs if r.get("lifecycle_errors"))
    tm = sum(r["tracking_mismatches"] for r in recs)
    two = sum(r["turns_with_two_attacks"] for r in recs)
    smoke = sum(1 for r in recs if r.get("smoke"))
    L += ["", "## For a second reader", "",
          f"- Games read: {len(recs)} ({', '.join(f'{LABEL[t]}: {len(by.get(t, []))}' for t in LISTS)}); every game "
          "completed, its seed, lists and pilots checked against the registration, and the engine's printed wins "
          "checked against the result files, at extraction (`run.log`).",
          f"- Games with lifecycle errors: {lc}. Arm-tracking mismatches: {tm}. Own turns with two attacks: {two}. "
          f"Smoke records: {smoke}. All four are expected to be 0.",
          "- Engine, programs and lists: sha256 in `provenance.txt` (written by run.sh before the first game).",
          "- Per-game records: `games/*.jsonl` (one line per game; README section 5 lists the fields)."]
    out = os.path.join(d, "RESULTS.md")
    with open(out + ".part", "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    os.replace(out + ".part", out)
    print(f"Written: {out}")


def _fake_game():
    """A made-up game for the self-test (not an engine game): draft A in seat 0 goes first; on own turn 2 Turbo Shark
    arms the Benched Alolan Vulpix (spot 1); a switch by a card effect (Activate) brings it to the Active Spot; on own
    turn 3 it evolves there into Alolan Ninetales ex and uses Binding Snow."""
    def mon(cid, name, stage=0):
        return {"Pokemon": {"id": cid, "name": name, "energy_type": "Water", "stage": stage}}
    carv, shark, vul, nine, lap = (mon("B4 034", "Carvanha"), mon("B4 035", SHARPEDO, 1), mon("B2 028", VULPIX),
                                   mon("B2 029", NINETALES, 1), mon("A3 044", LAPRAS))

    def slot(card, behind=()):
        return {"card": card, "cards_behind": list(behind)}

    def ply(t, cur, board, action, playable=None):
        return {"state": {"turn_count": t, "current_player": cur, "hands": [[], []], "points": [0, 0],
                          "in_play_pokemon": [board, [None] * 4]},
                "actor": 0, "chosen_action": {"action": action},
                "playable_actions": [{"action": x} for x in (playable or [action])]}
    b2 = [slot(shark, [carv]), slot(vul), slot(lap), None]          # own turn 2 (game turn 3)
    b3 = [slot(vul), slot(shark, [carv]), slot(lap), None]          # after the switch
    b4 = [slot(nine, [vul]), slot(shark, [carv]), slot(lap), None]  # after the evolution
    arm = [{"Attach": {"attachments": [[1, "Water", i]], "is_turn_energy": False}} for i in (1, 2)]
    plies = [ply(1, 0, [slot(carv), slot(vul), None, None], "EndTurn"),
             ply(3, 0, b2, {"Attack": {"title": TURBO}}),
             ply(3, 0, b2, arm[0], arm),
             ply(4, 1, b2, {"Activate": {"player": 0, "in_play_idx": 1}}),
             ply(5, 0, b3, {"Evolve": {"evolution": nine, "in_play_idx": 0}}),
             ply(5, 0, b4, {"Attack": {"title": SNOW}})]
    result = {"randomness": {"game_seed": 1}, "game_id": "fake", "outcome": {"Win": 0}, "final_points": [2, 0],
              "final_turn": 5, "plies": len(plies)}
    return game_extract(result, plies, 0, {})


def self_test():
    g = _fake_game()
    assert g["went_first"] is True and g["max_own_turn"] == 3 and g["tracking_mismatches"] == 0, g
    assert g["arms"] == [dict(own=2, target=VULPIX, attacked=[3, NINETALES, SNOW], evolved=[3, NINETALES],
                              left_play=None, lost_track=False)], g["arms"]
    assert g["sharks"][0]["result"] == "armed" and g["sharks"][0]["bench_water"] == 2, g["sharks"]
    s = line_steps(g)
    assert s == dict(L1=False, L2=True, L3=True, L3v=True, L4=True, L4v=True, L5=True, line2=True, line3=True,
                     plan=True), s
    g2 = json.loads(json.dumps(g))
    g2["arms"][0]["target"] = LAPRAS                                 # armed, but not the Vulpix: loose line only
    s = line_steps(g2)
    assert s["L3"] and s["line3"] and not (s["L3v"] or s["L4v"] or s["plan"]), s
    assert attacked_at_all([g, g2], NINETALES) == (2, 2) and attacked_at_all([g], LAPRAS) == (0, 0)
    assert set(THREE) <= deck_names(LISTS["draftA"]) and deck_names(LISTS["deck13"]) & set(THREE) == {NINETALES}
    lo, hi = wilson(50, 100)
    assert abs(lo - 0.4038) < 1e-4 and abs(hi - 0.5962) < 1e-4, (lo, hi)
    lo, hi = wilson(0, 10)
    assert lo == 0.0 and abs(hi - 0.2775) < 1e-4, hi
    m, lo, hi, sd = paired([1, 0, -1, 1])
    assert abs(m - 0.25) < 1e-12 and abs(sd - math.sqrt(2.75 / 3)) < 1e-12
    assert abs(hi - lo - 2 * Z * sd / 2) < 1e-12
    assert [own_turn(t, True) for t in (1, 3, 5)] == [1, 2, 3] and [own_turn(t, False) for t in (2, 4, 6)] == [1, 2, 3]
    assert len(deck_ids(LISTS["draftA"])) == 20 and len(deck_ids(LISTS["deck13"])) == 20 and len(deck_ids(OPPONENT)) == 20
    print("self-test passed: Wilson 50/100 = 40.38-59.62%, 0/10 = 0-27.75%; paired mean and sd; own turns; lists of 20; "
          "a made-up game: arm of the Benched Vulpix followed through a switch (Activate) and its evolution, "
          "steps L1-L5, L3v, L4v and the plan's line; attacked-at-all counts; card names in the lists")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", nargs="?", choices=("extract", "report"))
    ap.add_argument("--tmp")
    ap.add_argument("--tag")
    ap.add_argument("--seat", type=int)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--num", type=int)
    ap.add_argument("--coverage")
    ap.add_argument("--out")
    ap.add_argument("--smoke", action="store_true", help="extract only: seeds outside the registered range (a test)")
    ap.add_argument("--dir", default=HERE)
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    self_test()
    if a.self_test:
        return
    if a.mode == "extract":
        if None in (a.tmp, a.tag, a.seat, a.seed, a.num, a.coverage, a.out):
            raise SystemExit("extract needs --tmp --tag --seat --seed --num --coverage --out")
        extract(a)
    elif a.mode == "report":
        report(a)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
