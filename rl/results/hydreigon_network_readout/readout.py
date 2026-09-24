"""Readout for the Hydreigon network run (RUN5.md, "The plan, revised Sept 24", item 2). Run it after the run's own
report steps (audit_v5.py, REPORT.txt). Inside WSL, from the rl folder:
    python results/hydreigon_network_readout/readout.py --run runs/diag-hydreigon-lucario [--games 2000] [--workers 8]

What it does, on the run's own confirmation deals (seed = the settings' confirmation base + i, the bars' seats):
  1. reads the confirmed Hydreigon and Lucario checkpoints from state.json (verdict "picks", which finish() in
     train_v5.py records) and checks REPORT.txt names the same ones;
  2. plays network v network (the two confirmed networks) on those deals, and prints Hydreigon's result in all four
     conditions: k3 v k3 (the bars), network H v k3 L and k3 H v network L (the confirmation rows), network v network,
     each paired with k3 v k3 on the same deals;
  3. counts Hyper Ray (and Roar in Unison) for the Hydreigon network: in its confirmation games, replayed from the
     recorded moves as audit_v5.py does, and live in the network v network games;
  4. applies RUN5's pre-set reading to those numbers;
  5. prints the text and writes it to readout.txt here (never overwritten: a taken name gets a time suffix), with
     the network v network games beside it (<same name>_nvn_games.jsonl).
No new seeds: reusing the confirmation deals is deliberate (that block is reserved for this run's evaluation), so
all four rows are paired. --deck and --attack-name exist for the smoke test on other decks.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
RL = HERE.parents[1]
sys.path.insert(0, str(RL))
import train_v5 as T  # noqa: E402

# Limitless score of the first deck, % and its 95% range (results/limitless_check_2026-09-23.md)
LIMITLESS = {"hydreigon>lucario": (54.4, 8.0), "weezing>lucario": (43.4, 8.3)}
# Hydreigon (B1 157, lib/card.py): "Roar in Unison ... do 30 damage to this Pokemon". Healthy = more than 30 HP left.
ROAR_OWNER, ROAR_SELF = "Hydreigon", 30
LOAD_CHECK_GAMES = 50   # the other network's confirmation games replayed only to prove its weights load
# k3 reference counts, not recomputed (see-everything file: used / passed per Hydreigon turn)
K3_NOKO_RATE, SEARCHED_NOKO_RATE = 0.03, 0.82
REFERENCE = [
    "  k3 v k3, first 500 table seeds (see_everything_2026-09-24.md):  KOs 366 / 4;  doesn't KO 8 / 225 (3%);  "
    "Roar used when healthy 630 / 776",
    "  k3 v k3, all 1,000 table games (hydreigon_v_lucario_k3_transcripts_2026-09-24.md):  KOs 732 / 8 (99%);  "
    "doesn't KO 12 / 434 (3%);  17 other;  Roar on 83% of the turns it was usable without knocking Hydreigon out",
    "  searched bots kr3 (see-everything): sees everything  KOs 312 / 15;  doesn't KO 74 / 16 (82%);  "
    "guesses from the list  304 / 21;  66 / 13 (84%)",
]
KEYS = ("ko_used", "ko_passed", "noko_used", "noko_passed", "other", "roar_turns", "roar_used", "roar_self_ko")

_W = {}


def _init(S, nets, focus, attack):
    T.set_decks(S)
    env = T.make_env()
    dim = env.obs_dim + env.action_dim
    _W.update(env=env, nets={d: T.load_scorer(p, dim) for d, p in nets.items()}, focus=focus, attack=attack)


def look(env, p, mv):
    """One decision of the focus deck: was the attack / Roar on offer, was it chosen, would the attack KO."""
    acts = [json.loads(a) for a in env.raw.legal_actions_json()]
    view = json.loads(env.raw.describe(p))
    me, opp = view["me"]["board"], view["them"]["board"][0]
    hr = [i for i, a in enumerate(acts) if isinstance(a, dict) and a.get("Attack", {}).get("title") == _W["attack"]]
    roar = [i for i, a in enumerate(acts) if isinstance(a, dict) and "UseAbility" in a
            and (me[a["UseAbility"]["in_play_idx"]] or {}).get("name") == ROAR_OWNER]
    hp = lambda i: me[acts[i]["UseAbility"]["in_play_idx"]]["hp_left"]  # noqa: E731
    dmg = acts[hr[0]]["Attack"]["fixed_damage"] if hr else None
    return {"turn": view["turn"], "hr": bool(hr), "chose_hr": mv in hr, "end": acts[mv] == "EndTurn",
            "ko": bool(hr) and opp is not None and opp["hp_left"] <= dmg,
            "roar_ok": any(hp(i) > ROAR_SELF for i in roar), "chose_roar": mv in roar,
            "roar_self_ko": mv in roar and hp(mv) <= ROAR_SELF}


def tally(recs):
    """Per turn of the focus deck, as the transcripts file counted k3: the attack used (classified at the decision
    where it was used), passed (the turn ended with EndTurn while it was on offer; classified there), or offered
    earlier in the turn but not when the turn ended ("other")."""
    c = dict.fromkeys(KEYS, 0)
    turns = {}
    for r in recs:
        turns.setdefault(r["turn"], []).append(r)
    for ds in turns.values():
        used = [r for r in ds if r["chose_hr"]]
        passed = [r for r in ds if r["hr"] and r["end"]]
        if used:
            c["ko_used" if used[0]["ko"] else "noko_used"] += 1
        elif passed:
            c["ko_passed" if passed[0]["ko"] else "noko_passed"] += 1
        elif any(r["hr"] for r in ds):
            c["other"] += 1
        if any(r["roar_ok"] for r in ds):
            c["roar_turns"] += 1
            c["roar_used"] += any(r["chose_roar"] for r in ds)
        c["roar_self_ko"] += sum(r["roar_self_ko"] for r in ds)
    return c


def play(task):
    """("nvn", game): both seats played by their own network, live. ("replay", row): a recorded confirmation game
    (a network in one seat, k3 in the other) replayed from its moves; the network also re-chooses each move, which
    proves the weights file is the one that played."""
    kind, g = task
    env, nets, focus = _W["env"], _W["nets"], _W["focus"]
    d0, d1 = g["decks"]
    fseat = g["decks"].index(focus)
    rng = np.random.default_rng(g["seed"])  # tie-breaks, exactly as eval_chunk
    moves = None
    if kind == "nvn":
        env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"])
    else:
        seat = g["bot_seat"]
        env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"], bots=[None, "k3"] if seat == 0 else ["k3", None])
        moves = g["moves"]
    recs, played, same = [], [], 0
    while not env.done:
        p = env.current_player
        obs, feats = env.observe(p), env.action_features()
        i = T.pick(nets[g["decks"][p]].score_actions(obs, feats), rng)
        if moves is not None:
            if len(played) >= len(moves):
                break   # more decisions than were recorded: not an exact replay
            same += i == moves[len(played)]
            i = moves[len(played)]
        if p == fseat:
            recs.append(look(env, p, i))
        played.append(i)
        env.step(i)
    res = env.result() if env.done else None
    out = {"kind": kind, "seed": g["seed"], "decks": g["decks"], "count": tally(recs), "decisions": len(played),
           "same": same}
    if kind == "nvn":
        out.update(winner=res[0], points=list(res[1]), turns=res[2], moves=played, ok=True)
    else:
        out.update(deck=g["deck"], ok=res is not None and len(played) == len(moves) and res[0] == g["winner"]
                   and res[2] == g["turns"])
    return out


def score(g, focus):
    s = g["decks"].index(focus)
    return 1.0 if g["winner"] == s else (0.5 if g["winner"] == -1 else 0.0)


def paired_line(label, games, bars, focus, width):
    """Focus deck's result in one condition, paired with k3 v k3 on the same seeds."""
    seeds = sorted(s for s in games if s in bars)
    n = len(seeds)
    if not n:
        return f"  {label:<{width}}     0   (no games)", float("nan"), float("nan")
    won =[float(games[s]["winner"] == games[s]["decks"].index(focus)) for s in seeds]
    base = [float(bars[s]["winner"] == bars[s]["decks"].index(focus)) for s in seeds]
    sc = [score(games[s], focus) for s in seeds]
    draws = sum(games[s]["winner"] == -1 for s in seeds)
    d = np.array(won) - np.array(base)
    half = 1.96 * d.std(ddof=1) / math.sqrt(n) if n > 1 else float("nan")
    only_here = int(sum(a > b for a, b in zip(won, base)))
    only_bar = int(sum(b > a for a, b in zip(won, base)))
    return (f"  {label:<{width}}{n:>6}{100 * np.mean(won):>8.1f}{draws:>7}{100 * np.mean(sc):>9.1f}"
            f"{100 * d.mean():>+10.1f} ±{100 * half:<5.1f}{only_here:>9} / {only_bar:<5}"), 100 * np.mean(sc), 100 * d.mean()


def hr_line(label, c, width):
    return (f"  {label:<{width}}{c['ko_used']:>6} / {c['ko_passed']:<5}{'(' + c_pct(c, True) + ')':<8}"
            f"{c['noko_used']:>8} / {c['noko_passed']:<5}{'(' + c_pct(c, False) + ')':<8}{c['other']:>6}")


def c_pct(c, ko):
    u, p = (c["ko_used"], c["ko_passed"]) if ko else (c["noko_used"], c["noko_passed"])
    return f"{100 * u / (u + p):.0f}%" if u + p else "—"


def total(results):
    c = dict.fromkeys(KEYS, 0)
    for r in results:
        for k in KEYS:
            c[k] += r["count"][k]
    return c


def free_name(path):
    """Never overwrite: a taken name gets a time suffix."""
    if not path.exists():
        return path
    alt = path.with_name(f"{path.stem}_{time.strftime('%Y%m%d-%H%M%S')}{path.suffix}")
    if alt.exists():
        raise SystemExit(f"{alt} exists; wait a second and rerun")
    return alt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder (relative paths are taken from the rl folder)")
    ap.add_argument("--games", type=int, default=2000, help="first N confirmation deals (default 2000 = all)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--deck", default="hydreigon", help="the deck whose attack is counted (smoke tests only)")
    ap.add_argument("--attack-name", default="Hyper Ray", help="Hydreigon's attack (lib/card.py)")
    ap.add_argument("--out", default=str(HERE / "readout.txt"))
    a = ap.parse_args()
    t0 = time.time()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    st = json.loads((run_dir / "state.json").read_text())
    focus = a.deck
    names = list(S["pool"])
    if focus not in names or len(names) != 2:
        raise SystemExit(f"--deck {focus}: the run's pool is {names}; this readout needs a two-deck pool containing it")
    opp = [d for d in names if d != focus][0]
    T.check_decks_unchanged(run_dir, S)   # the recorded games were played with the run's own deck files

    # 1. the confirmed checkpoints, as finish() records them
    picks = (st.get("verdict") or {}).get("picks")
    if not picks or set(picks) != set(names):
        raise SystemExit("state.json has no confirmed checkpoint per network yet (verdict 'picks'); "
                         "run this after the run has finished its confirmations")
    cf = {d: next(c for c in st["confirmations"] if c["deck"] == d and c["name"] == picks[d]) for d in names}
    rep = run_dir / "REPORT.txt"
    rep_text = rep.read_text() if rep.exists() else None
    rep_ok = {d: rep_text is not None and f"Confirmation of the {d} network's {picks[d]} (used for the verdict)" in rep_text
              for d in names}
    nets = {d: str(T.ckpt_path(run_dir, picks[d], d)) for d in names}

    # the deals: the bars' own rows, checked against the settings' formula (bar_games in train_v5.py)
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines()
            if '"kind": "bar"' in x or '"kind": "confirmation"' in x]
    pair = sorted([focus, opp])
    bars = {g["seed"]: g for g in rows if g["kind"] == "bar" and sorted(g["decks"]) == pair}
    formula = {s: [d0, d1] for s, d0, d1, *_ in T.bar_games(S) if sorted([d0, d1]) == pair}
    off = [s for s, g in bars.items() if formula.get(s) != g["decks"]]
    if off:
        raise SystemExit(f"{len(off)} bar rows don't match the settings' seed/seat formula (first: seed {off[0]})")
    seeds = sorted(bars)[:a.games]
    keep = set(seeds)
    bars = {s: bars[s] for s in seeds}
    conf = {d: {g["seed"]: g for g in rows if g["kind"] == "confirmation" and g.get("ckpt") == picks[d]
                and g.get("deck") == d and g["seed"] in keep} for d in names}
    bad_deal = [s for d in names for s, g in conf[d].items() if g["decks"] != bars[s]["decks"]]
    if bad_deal:
        raise SystemExit(f"{len(bad_deal)} confirmation rows sit on a different deal than the bar with the same seed")

    # 2 + 3. play network v network, replay the focus network's confirmation games, and a load check of the other
    tasks = [("nvn", {"seed": s, "decks": bars[s]["decks"]}) for s in seeds]
    tasks += [("replay", conf[focus][s]) for s in sorted(conf[focus])]
    tasks += [("replay", conf[opp][s]) for s in sorted(conf[opp])[:LOAD_CHECK_GAMES]]
    init = (S, nets, focus, a.attack_name)
    if a.workers == 1:
        _init(*init)
        results = [play(t) for t in tasks]
    else:
        with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=init) as pool:
            results = pool.map(play, tasks, chunksize=4)
    nvn = {r["seed"]: r for r in results if r["kind"] == "nvn"}
    rep_f = [r for r in results if r["kind"] == "replay" and r["deck"] == focus]
    rep_o = [r for r in results if r["kind"] == "replay" and r["deck"] == opp]
    good_f = [r for r in rep_f if r["ok"]]

    # the text
    F, O = focus.capitalize(), opp.capitalize()
    base = S["seeds"]["confirm"]
    ident = json.loads((run_dir / "identity.json").read_text())["sha256"]
    addon_ok = ident.get("add-on") in (None, T.sha_file(T.addon_path()))
    L = [f"Hydreigon network run readout — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Confirmed checkpoints (state.json verdict picks, recorded by finish() in train_v5.py): "
         + ", ".join(f"{d} {picks[d]} ({100 * cf[d]['margin']:+.1f} over k3)" for d in names) + ".",
         "  REPORT.txt names the same ones as 'used for the verdict': "
         + ("not written yet" if rep_text is None else ", ".join(f"{d} {'yes' if rep_ok[d] else 'NO'}" for d in names)),
         "  Weights: " + ", ".join(f"{Path(p).name} {T.sha_file(p)[:12]}" for p in nets.values())
         + f". Add-on {T.sha_file(T.addon_path())[:12]} " + ("(the run's own)" if addon_ok else "(DIFFERENT from the run's identity.json)"),
         "",
         f"Deals: the run's own confirmation deals, {len(seeds):,} of them: seed {base:,} + i for i = "
         f"{seeds[0] - base} to {seeds[-1] - base} (settings 'confirm' base), {names[0]} in seat 0 on even i and "
         f"seat 1 on odd i, as in the bars; the engine's coin decides who goes first.",
         "  No new seeds. Reusing this block is deliberate: it is reserved for this run's evaluation, and it makes the",
         "  four rows below paired. Network v network starts from the same deal as the bar; later draws can differ",
         "  once the play differs.", "",
         f"1. {F}'s result on those deals (row = who pilots each side). 'change' = won % minus k3 v k3's on the same",
         "   deals, with a paired 95% interval (1.96 x standard deviation of the per-deal difference / sqrt n).",
         f"   'won only' = deals {F} won here and not in k3 v k3 / the reverse. Score counts a draw as half (Limitless's way).", ""]
    w = 38
    L.append(f"  {'condition':<{w}}{'n':>6}{'won %':>8}{'draws':>7}{'score %':>9}{'change':>10}{'':>7}{'won only here / in bar':>24}")
    bar_line = paired_line(f"k3 {F} v k3 {O} (the bars)", bars, bars, focus, w)
    rows_out = [bar_line,
                paired_line(f"network {F} v k3 {O}", conf[focus], bars, focus, w),
                paired_line(f"k3 {F} v network {O}", conf[opp], bars, focus, w),
                paired_line(f"network v network (new)", nvn, bars, focus, w)]
    L += [r[0] for r in rows_out]
    full = len(seeds) == len(conf[focus]) == S["confirm_per_matchup"]
    if full:
        t = f"{focus}>{opp}"
        mine = rows_out[1][2]
        L.append(f"  Check: the run's own confirmed margin for {F} is {100 * cf[focus]['margin']:+.1f}; this table's "
                 f"{mine:+.1f} ({'same' if abs(mine - 100 * cf[focus]['margin']) < 0.05 else 'DIFFERENT'}); "
                 f"bars {100 * st['bars'][t]['win_rate']:.1f}% in state.json.")
    L.append("")

    # Hyper Ray and Roar in Unison
    c_rep, c_nvn = total(good_f), total(nvn.values())
    same_f, dec_f = sum(r["same"] for r in rep_f), sum(r["decisions"] for r in rep_f)
    same_o, dec_o = sum(r["same"] for r in rep_o), sum(r["decisions"] for r in rep_o)
    w2 = 42
    L += [f"2. {a.attack_name}, per turn of the {F} network where it was on offer: used / passed (use %).",
          f"   'KOs' = {O}'s Active had no more HP left than {a.attack_name}'s damage (the attack's own fixed_damage in",
          "   the legal move; 130 for Hyper Ray), the transcripts file's definition. Passed = the turn ended with EndTurn",
          "   while it was on offer (classified there); 'other' = offered earlier in the turn, not when it ended.", "",
          "  " + " " * w2 + "   KOs: used / passed    doesn't KO: used / passed   other",
          hr_line(f"network {F} v k3 {O} (replayed)", c_rep, w2),
          hr_line("network v network (live)", c_nvn, w2),
          "  k3 reference numbers (not recomputed; Hyper Ray, other seeds):"] + REFERENCE
    for label, c in ((f"network {F} v k3 {O}", c_rep), ("network v network", c_nvn)):
        L.append(f"  Roar in Unison, {label}: used on {c['roar_used']} of the {c['roar_turns']} turns it was usable on a "
                 f"{ROAR_OWNER} with more than {ROAR_SELF} HP left"
                 + (f" ({100 * c['roar_used'] / c['roar_turns']:.0f}%)" if c["roar_turns"] else "")
                 + f"; uses that knocked out its own {ROAR_OWNER}: {c['roar_self_ko']}.")
    L += [f"  Replays: {len(good_f):,} of {len(rep_f):,} {F} confirmation games replayed exactly (winner and turns); the "
          f"{F} network re-chose the recorded move at {same_f:,} of {dec_f:,} decisions, the {O} network at {same_o:,} "
          f"of {dec_o:,} (first {len(rep_o)} of its confirmation games). All equal = the right weights were loaded.", ""]
    if len(good_f) < len(rep_f):
        L.insert(0, f"INCOMPLETE: {len(rep_f) - len(good_f)} confirmation games did not replay exactly; they are left "
                    f"out of the {a.attack_name} count.")
    bad_o = [r for r in rep_o if not r["ok"]]
    weights_bad = same_f != dec_f or same_o != dec_o or bad_o or not rep_f or not rep_o
    if weights_bad:
        L.insert(0, f"INCOMPLETE: weights check failed ({F} re-chose {same_f}/{dec_f}, {O} {same_o}/{dec_o}, "
                    f"{len(bad_o)} {O} replays not exact); the network v network row and the READING are not trustworthy.")

    # 4. the reading
    gain = 100 * cf[focus]["margin"]
    noko = c_rep["noko_used"] + c_rep["noko_passed"]
    rate = c_rep["noko_used"] / noko if noko else None
    if rate is None:
        chips, why = None, "no turn offered it without a KO, so there is nothing to read"
    elif rate <= K3_NOKO_RATE:
        chips, why = False, f"{100 * rate:.0f}% is no more than k3's 3%"
    elif rate >= SEARCHED_NOKO_RATE:
        chips, why = True, f"{100 * rate:.0f}% is at the searched bots' level (82-84%)"
    else:
        chips, why = None, (f"{100 * rate:.0f}% is between k3's 3% and the searched bots' 82-84%; RUN5 gives no number "
                            f"for 'chips', so both branches are shown")
    case = {(True, True): "chips with Hyper Ray and gains 10+ over k3 -> learning finds the play k3 misses",
            (True, False): "chips but lands near k3 -> check its benching before concluding",
            (False, True): "gains without chipping -> the gain is elsewhere",
            (False, False): "neither -> ambiguous, and only then is a forced-Hyper-Ray k3 build worth it"}
    g10 = gain >= 10
    L += ["3. READING (RUN5.md's reading, set before the run, applied as written; no new thresholds)"]
    if weights_bad:
        L.append("  NOT TRUSTWORTHY: the weights check failed (see the top line); don't act on this reading.")
    L += [f"  Gain over k3: the {F} network's confirmed margin is {gain:+.1f} points (the run's own number, "
          f"{S['confirm_per_matchup']:,} paired deals; its paired 95% interval is in table 1). RUN5's line is 10+: "
          f"{'yes' if g10 else 'no'}.",
          f"  Chips with Hyper Ray: it used {a.attack_name} on {c_rep['noko_used']} of {noko} turns where it was on offer "
          f"and wouldn't KO"
          + (f" ({100 * rate:.0f}%)" if rate is not None else "")
          + f" in its games against k3 ({c_pct(c_nvn, False)} against the {O} network). k3: 3%. Searched bots: 82-84%.",
          f"  RUN5 sets no number for 'chips'. Read here only against those two references: {why}.",
          "  The see-everything file's guide: near ~80% = the network learned the same fix as the searched bot; wins more",
          "  with Hyper Ray still low = it found something else."]
    branches = [chips] if chips is not None else [True, False]
    for b in branches:
        pre = "  -> " if chips is not None else f"  If this {'counts' if b else 'does not count'} as chipping: "
        L.append(pre + case[(b, g10)] + ".")
    if not g10 and (chips is None or chips):
        L.append("     RUN5 doesn't define 'near k3'; any confirmed gain under +10 is read as this branch here.")
        au = T.HERE / f"results/ko_audit/v5_{run_dir.name}_{focus}_{picks[focus]}.json"
        if au.exists():
            r = json.loads(au.read_text())
            b_, k_ = r["stats"].get(f"bot|{focus}>{opp}"), r["stats"].get(f"k3|{focus}>{opp}")
            pct = lambda s, k: f"{s[k + '_made'] / s[k + '_turns']:.0%}" if s and s[k + "_turns"] else "—"  # noqa: E731
            L.append(f"     Benching (knockout audit, {au.name}{'' if r.get('complete') else ', INCOMPLETE'}): the network "
                     f"benched {pct(b_, 'bench')} of the turns it could (k3 {pct(k_, 'bench')}); attacked "
                     f"{pct(b_, 'attack')} (k3 {pct(k_, 'attack')}).")
        else:
            L.append(f"     Benching: the knockout audit file isn't there ({au.name}); see REPORT.txt.")
    lim = LIMITLESS.get(f"{focus}>{opp}")
    if lim:
        mid, pm = lim
        miss = lambda x: abs(x - mid)  # noqa: E731
        k3s, nvs = rows_out[0][1], rows_out[3][1]
        L += [f"  Toward Limitless ({F} {mid} ± {pm}, results/limitless_check_2026-09-23.md), scores with draws as half:",
              f"    k3 v k3 {k3s:.1f} (off by {miss(k3s):.1f}); network v network {nvs:.1f} (off by {miss(nvs):.1f}): "
              f"{'moved toward' if miss(nvs) < miss(k3s) else 'did not move toward'} Limitless; "
              f"{'inside' if miss(nvs) <= pm else 'outside'} Limitless's 95% range.",
              f"    One side only: network {F} v k3 {O} {rows_out[1][1]:.1f} (off by {miss(rows_out[1][1]):.1f}); "
              f"k3 {F} v network {O} {rows_out[2][1]:.1f} (off by {miss(rows_out[2][1]):.1f}).",
              "    RUN5's warning: a bot can gain over k3 and still take the matchup further from reality."]
    L += ["  Before any of this is read: RUN5 says the result isn't read until the auditor's pair checks pass. This",
          "  readout does not run them.", "",
          f"Took {time.time() - t0:.0f} s with {a.workers} worker{'s' if a.workers != 1 else ''}. "
          f"Games played here: {len(nvn):,} network v network, {len(rep_f) + len(rep_o):,} confirmation replays."]
    text = "\n".join(L) + "\n"
    print(text)
    out = free_name(Path(a.out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    games_path = free_name(out.with_name(out.stem + "_nvn_games.jsonl"))
    with open(games_path, "w") as f:
        for s in seeds:
            r = nvn[s]
            f.write(json.dumps({"kind": "nvn", "seed": s, "decks": r["decks"], "nets": picks, "winner": r["winner"],
                                "points": r["points"], "turns": r["turns"], "moves": r["moves"]}) + "\n")
    print(f"Written: {out}\n         {games_path}")


if __name__ == "__main__":
    main()
