"""Run 2 transfer test: does the specialist carry over to matchups it never trained on?
Run from the project root, inside WSL, after training has finished:
    python rl/matchup_test_v2.py --run runs/<run 2 folder>

The bot always pilots the run's own deck (Dustin's); k3 always pilots the opponent deck.
Three rows per opponent, on the same seeds, half from each seat (draws count as non-wins):
  ceiling  k3 piloting Dustin's deck      -> how well k3 itself does in this matchup
  floor    untrained network (ckpt_0)     -> what knowing nothing scores here
  bot      best checkpoint                -> where it lands between floor and ceiling
The training matchup is included as the reference, on the same method.

The card list is the run's own (Dustin's deck + the training opponent); cards the bot has never
met read as "other card". The v2 consequence and threat numbers don't depend on the card list.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pdl_env import PocketEnv, engine_play  # noqa: E402
from train_v2 import load_net  # noqa: E402

ROOT = HERE.parent  # the repo root (on the laptop this file sat two folders down)
STUDY = ROOT / "decks/research"
SEED0 = 41_000_000  # separate from every training and evaluation seed range (run 1's test used 40M)

_W = {}
MINE = {}


def make_env():
    env = PocketEnv(vocab_deck_paths=[MINE["deck"], MINE["opp"]], features=MINE["features"])
    env.reset(MINE["deck"], MINE["opp"], 1)
    return env


def _init(ckpts, deck, opp, features):
    MINE.update(deck=deck, opp=opp, features=features)
    _W["env"] = make_env()
    dim = _W["env"].obs_dim + _W["env"].action_dim
    _W["nets"] = {name: load_net(path, dim) for name, path in ckpts.items()}


def pick(q, rng):
    if not np.isfinite(q).all():
        raise RuntimeError("network produced non-finite move scores")
    best = np.flatnonzero(q == q.max())
    return int(best[0]) if len(best) == 1 else int(rng.choice(best))


def play(task):
    row, opp_deck, seed, seat = task  # seat = where Dustin's deck sits
    DECK = MINE["deck"]
    if row == "ceiling":
        decks = (DECK, opp_deck) if seat == 0 else (opp_deck, DECK)
        winner, pts, turns = engine_play(decks[0], decks[1], seed, ("k3", "k3"))
    else:
        env, net = _W["env"], _W["nets"][row]
        rng = np.random.default_rng(seed)
        if seat == 0:
            env.reset(DECK, opp_deck, seed, bots=[None, "k3"])
        else:
            env.reset(opp_deck, DECK, seed, bots=["k3", None])
        while not env.done:
            p = env.current_player
            assert p == seat, "only the network's seat should be asked to move"
            env.step(pick(net.score_actions(env.observe(p), env.action_features()), rng))
        winner, pts, turns = env.result()
    return {"row": row, "opp": opp_deck, "seed": seed, "seat": seat, "winner": winner,
            "points": list(pts), "turns": turns}


def summarize(games):
    out = {"games": len(games)}
    for s in (0, 1):
        g = [x for x in games if x["seat"] == s]
        w = sum(x["winner"] == s for x in g)
        d = sum(x["winner"] == -1 for x in g)
        out[f"seat{s}"] = {"wins": w, "losses": len(g) - w - d, "draws": d, "win_rate": w / max(1, len(g))}
    out["win_rate"] = (out["seat0"]["wins"] + out["seat1"]["wins"]) / max(1, len(games))
    out["draw_rate"] = (out["seat0"]["draws"] + out["seat1"]["draws"]) / max(1, len(games))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run 2 folder")
    ap.add_argument("--opponents", default="altaria,suicune",
                    help="Limitless study decks to test on, besides the training opponent (file names)")
    ap.add_argument("--ckpt", default="", help="checkpoint to test (default: best against k3)")
    ap.add_argument("--games", type=int, default=400, help="games per row per opponent (half per seat)")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--allow-running", action="store_true", help="run even while training is still going")
    a = ap.parse_args()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    st = json.loads((run_dir / "state.json").read_text())
    if st["status"] == "RUNNING" and not a.allow_running:
        raise SystemExit("Training is still running; this test would slow it down. Run it after the run ends.")
    best = max((c for c in st["checkpoints"] if c["name"] != "ckpt_0"), key=lambda c: c["eval"]["k3"]["win_rate"])
    name = a.ckpt or best["name"]
    ckpts = {"floor": str(run_dir / "ckpt_0.npz"), "bot": str(run_dir / f"{name}.npz")}
    S = json.loads((run_dir / "settings.json").read_text())
    # the encoding the run was trained with: no key = "v2" (add-on 0.4.0, the Sept 18 pilot)
    MINE.update(deck=str(ROOT / S["deck"]), opp=str(ROOT / S["opp"]), features=S.get("features", "v2"))
    OPPONENTS = {f"{Path(S['opp']).stem} (trained on)": MINE["opp"]}
    for o in a.opponents.split(","):
        if o.strip():
            OPPONENTS[o.strip()] = str(STUDY / f"{o.strip()}.txt")

    # Guard against the silent-misread trap: same card list and input size as training.
    env = make_env()
    from pdl_rl_env import RawEnv
    if env.raw.vocab != sorted(set(RawEnv.deck_card_ids(MINE["deck"])) | set(RawEnv.deck_card_ids(MINE["opp"]))):
        raise SystemExit("Card list isn't the run's own; refusing to run.")
    for path in ckpts.values():
        if np.load(path)["p0"].shape[0] != env.obs_dim + env.action_dim:
            raise SystemExit(f"{path} was built for a different input size; refusing to run.")

    tasks = []
    for opp in OPPONENTS.values():
        for row in ("ceiling", "floor", "bot"):
            tasks += [(row, opp, SEED0 + i, i % 2) for i in range(a.games)]
    t0 = time.time()
    with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=(ckpts, MINE["deck"], MINE["opp"], MINE["features"])) as pool:
        games = pool.map(play, tasks, chunksize=20)
    results = {"run": run_dir.name, "checkpoint": name,
               "checkpoint_k3_score_during_training": best["eval"]["k3"]["win_rate"] if not a.ckpt else None,
               "games_per_row": a.games, "seconds": round(time.time() - t0), "opponents": {}}
    lines = [f"Matchup test — {run_dir.name}, checkpoint {name} (bot always pilots {Path(S['deck']).stem}; "
             "k3 pilots the opponent)",
             "Win rates, draws count as non-wins. Position = where the bot lands from floor (0%) to k3's own score (100%).",
             "", f"  {'opponent':<52} {'k3 itself':>9} {'untrained':>9} {'bot':>6} {'position':>9}"]
    for label, opp in OPPONENTS.items():
        rows = {r: summarize([g for g in games if g["opp"] == opp and g["row"] == r])
                for r in ("ceiling", "floor", "bot")}
        c, f, b = rows["ceiling"]["win_rate"], rows["floor"]["win_rate"], rows["bot"]["win_rate"]
        pos = (b - f) / (c - f) if c - f > 0.05 else None
        results["opponents"][label] = dict(rows, deck=opp, position=pos)
        lines.append(f"  {label:<52} {c:>9.0%} {f:>9.0%} {b:>6.0%} "
                     + (f"{pos:>9.0%}" if pos is not None else f"{'n/a':>9}"))
        lines.append(f"  {'':<52} bot by seat: {rows['bot']['seat0']['win_rate']:.0%} / "
                     f"{rows['bot']['seat1']['win_rate']:.0%} · bot draws {rows['bot']['draw_rate']:.0%}")
    margin = 100 * 1.96 * (0.25 / a.games) ** 0.5
    lines += ["", f"{a.games} games per row ({a.games // 2} per seat): about ±{margin:.0f} points on each win rate. "
              "Position is n/a when k3 barely beats the untrained network, since there's no room to measure."]
    text = "\n".join(lines)
    print(text)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / f"results/matchup_test_{run_dir.name}_{name}.json").write_text(json.dumps(dict(results, summary=text), indent=1))


if __name__ == "__main__":
    main()
