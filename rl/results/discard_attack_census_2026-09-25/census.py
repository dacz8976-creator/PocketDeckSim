"""Does k3 decline Energy-discard attacks elsewhere, as it declines Hyper Ray? The census Fable asked for before a
projected-readiness evaluation feature is registered (docs/REVIEW_2026-09-24_direction.md, section 8). Inside WSL,
from the rl folder, with the run5 venv (the verified 0.7.2 add-on; k3 only):
    python results/discard_attack_census_2026-09-25/census.py [--deals 200] [--workers 8]

For every deck among the table's eight whose list has an attack that discards Energy from the attacker (read from
lib/card.py: Mega Blaziken ex's Mega Burning, Hydreigon's Hyper Ray, Mega Sceptile ex's Terminating Tail, Chien-Pao
ex's Diving Icicles), k3 v k3 in each of that deck's seven pairings: the engine's own loop plays the game and records
that deck's choices (engine_play_record, as step1b_k3_replay_check.py); the game is replayed through the add-on and
each of its decisions is classified. A replay counts only if it equals the engine loop's game (winner and turns).

Per turn of that deck where the attack was on offer, as readout.py counts Hyper Ray: used; passed (the turn ended
with EndTurn while it was on offer); another attack (a different attack was chosen while it was on offer); other
(offered earlier in the turn, not at the end). Classified at the decision where it was used or passed. 'KOs' = the
attack's printed damage is at least the target's HP left (the opponent's Active; for Diving Icicles, which hits any
opponent's Pokemon for 130, the lowest-HP one). Weakness and damage changes are not counted, as in readout.py.

Seeds: 21,020,000,000 + pairing x 100,000 + i (pairings in the table's alphabetical order, the table's own numbering),
i < --deals, the first-named deck in seat 0 on even i. A new Claude Code diagnostics block, above tonight's others.

READING, written before any census game was played (Sept 25, about 05:50 CDT; Fable and the laptop session):
  - Descriptive only; no threshold decides anything. It says where a projected-readiness term (the Active's Energy
    at its next attack, counting the turn's attach of the visible Zone type and abilities that attach to it) would
    bite, as a list per attack, before that term is registered.
  - "k3 declines it" means a low use % on no-KO turns, read against Hyper Ray's 3% (k3) and 99% (the network) on the
    Hydreigon run's own deals, and against the searched bots' 82-84% (see-everything file).
  - Caution, set now: the sim already overrates Suicune (52.9 against 48.2 on the table). If k3 declines Diving
    Icicles and the readiness fix makes Suicune use it, Suicune moves further from Limitless and the deck veto may
    fire. That is the rule working: a fix that is right by the rules and moves a deck away from reality points to a
    blind spot on the other side of those matchups (or to the population), not to reverting the fix.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
RL = HERE.parents[1]
ROOT = RL.parent
sys.path.insert(0, str(RL))
from pdl_env import PocketEnv  # noqa: E402
from pdl_rl_env import engine_play_record  # noqa: E402

DECKS = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
PAIRS = list(itertools.combinations(DECKS, 2))   # the table's order: pairing index p
SEED0 = 21_020_000_000
# deck -> (attack title, damage it does, whether it may target any opponent's Pokemon)
ATTACKS = {"blaziken": ("Mega Burning", 120, False), "hydreigon": ("Hyper Ray", 130, False),
           "sceptile": ("Terminating Tail", 130, False), "suicune": ("Diving Icicles", 130, True)}
KEYS = ("ko_used", "ko_passed", "ko_other_attack", "noko_used", "noko_passed", "noko_other_attack", "other")
_W = {}


def path(d):
    return str(ROOT / "decks/research" / f"{d}.txt")


def _init():
    env = PocketEnv(vocab_deck_paths=[path(d) for d in DECKS], features="v2.2")
    env.reset(path(DECKS[0]), path(DECKS[1]), 1)
    _W["env"] = env


def look(env, p, mv, title, dmg, any_target):
    acts = [json.loads(a) for a in env.raw.legal_actions_json()]
    view = json.loads(env.raw.describe(p))
    them = [x for x in view["them"]["board"] if x]
    offered = [i for i, a in enumerate(acts) if isinstance(a, dict) and a.get("Attack", {}).get("title") == title]
    targets = them if any_target else [view["them"]["board"][0]] if view["them"]["board"][0] else []
    return {"turn": view["turn"], "on": bool(offered), "used": mv in offered,
            "other_attack": bool(offered) and isinstance(acts[mv], dict) and "Attack" in acts[mv] and mv not in offered,
            "end": acts[mv] == "EndTurn", "ko": any(t["hp_left"] <= dmg for t in targets)}


def tally(recs):
    c = dict.fromkeys(KEYS, 0)
    turns = {}
    for r in recs:
        turns.setdefault(r["turn"], []).append(r)
    for ds in turns.values():
        hit = next((r for r in ds if r["used"] or (r["on"] and (r["end"] or r["other_attack"]))), None)
        if hit is None:
            c["other"] += any(r["on"] for r in ds)
            continue
        kind = "used" if hit["used"] else ("passed" if hit["end"] else "other_attack")
        c[("ko_" if hit["ko"] else "noko_") + kind] += 1
    return c


def play(task):
    deck, p, i = task
    a, b = PAIRS[p]
    d0, d1 = (a, b) if i % 2 == 0 else (b, a)
    seed = SEED0 + p * 100_000 + i
    seat = (d0, d1).index(deck)
    title, dmg, anyt = ATTACKS[deck]
    rec, _prints, _h, res = engine_play_record(path(d0), path(d1), seed, ("k3", "k3"), seat)
    env = _W["env"]
    env.reset(path(d0), path(d1), seed, bots=[None, "k3"] if seat == 0 else ["k3", None])
    recs, n = [], 0
    while not env.done:
        if n >= len(rec) or env.current_player != seat:
            return {"deck": deck, "p": p, "ok": False}
        recs.append(look(env, seat, rec[n], title, dmg, anyt))
        env.step(rec[n])
        n += 1
    w, _pts, turns = env.result()
    won = w == seat
    return {"deck": deck, "p": p, "ok": n == len(rec) and (w, turns) == (res[0], res[2]), "won": won,
            "count": tally(recs)}


def pct(u, p):
    return f"{100 * u / (u + p):.0f}%" if u + p else "—"


def line(label, c, won=None):
    s = (f"  {label:<30}{c['ko_used']:>6} / {c['ko_passed']:<5}/ {c['ko_other_attack']:<4}{pct(c['ko_used'], c['ko_passed'] + c['ko_other_attack']):>6}"
         f"{c['noko_used']:>9} / {c['noko_passed']:<5}/ {c['noko_other_attack']:<4}{pct(c['noko_used'], c['noko_passed'] + c['noko_other_attack']):>6}"
         f"{c['other']:>8}")
    return s + (f"{won:>9.1f}" if won is not None else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deals", type=int, default=200)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", default=str(HERE / "census.txt"))
    a = ap.parse_args()
    t0 = time.time()
    tasks = [(deck, p, i) for deck in ATTACKS for p, pr in enumerate(PAIRS) if deck in pr for i in range(a.deals)]
    with mp.get_context("spawn").Pool(a.workers, initializer=_init) as pool:
        res = pool.map(play, tasks, chunksize=4)
    good = [r for r in res if r["ok"]]
    L = [f"Energy-discard attack census, k3 v k3   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"{a.deals} deals per pairing, seeds {SEED0:,} + pairing x 100,000 + i. Replayed exactly (winner and turns equal "
         f"the engine loop's game): {len(good):,} of {len(res):,}; only those are counted.", "",
         "Per turn of the deck where the attack was on offer: used / passed / another attack chosen (use %), split by",
         "whether it would knock out; 'other' = offered earlier in the turn, not at the end. 'won %' = the deck's k3 wins.", "",
         f"  {'':<30}{'KOs: used / passed / other atk':>31}{'no KO: used / passed / other atk':>35}{'other':>8}{'won %':>9}"]
    for deck, (title, dmg, anyt) in ATTACKS.items():
        rows = [r for r in good if r["deck"] == deck]
        tot = dict.fromkeys(KEYS, 0)
        L.append(f"{deck.capitalize()}: {title} ({dmg}{', any target' if anyt else ''})")
        for p, pr in enumerate(PAIRS):
            if deck not in pr:
                continue
            opp = pr[1] if pr[0] == deck else pr[0]
            rs = [r for r in rows if r["p"] == p]
            c = dict.fromkeys(KEYS, 0)
            for r in rs:
                for k in KEYS:
                    c[k] += r["count"][k]
                    tot[k] += r["count"][k]
            L.append(line(f"v {opp}", c, 100 * sum(r["won"] for r in rs) / len(rs) if rs else float("nan")))
        L += [line("all seven", tot, 100 * sum(r["won"] for r in rows) / len(rows) if rows else float("nan")), ""]
    if len(good) < len(res):
        L.insert(0, f"INCOMPLETE: {len(res) - len(good)} games did not replay exactly; they are left out.")
    L.append(f"Took {time.time() - t0:.0f} s with {a.workers} workers; {len(res):,} games.")
    text = "\n".join(L) + "\n"
    print(text)
    out = Path(a.out)
    if out.exists():
        out = out.with_name(f"{out.stem}_{time.strftime('%Y%m%d-%H%M%S')}{out.suffix}")
    out.write_text(text)
    print(f"Written: {out}")


if __name__ == "__main__":
    main()
