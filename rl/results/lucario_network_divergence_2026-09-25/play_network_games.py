"""B2c step 1: the run 5 stage 1 Lucario network (ckpt_1800k_avg_lucario.npz, add-on 0.7.2) pilots Lucario
against k3 piloting Weezing, and every move is recorded so engine/examples/net_divergence.rs can replay the
games and ask k3 what it would have played at each of the network's decisions.

    <venv with numpy and the 0.7.2 wheel>/bin/python play_network_games.py --games 400 --out games.jsonl

Seeds are new: 22,300,000,000 + i, Lucario in seat i % 2. The network picks as in train_v5.eval_chunk
(highest score, ties broken by numpy's default_rng(seed)). Checks before playing: the installed add-on
library, both deck files and the weights file match rl/checkpoints/run5-stage1-weezing-lucario/identity.json
and project_manifest.json.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "rl"))
import train_v5 as T  # noqa: E402

CKPT_DIR = ROOT / "rl/checkpoints/run5-stage1-weezing-lucario"
SEED_BASE = 22_300_000_000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=400)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--out", default=str(HERE / "games.jsonl.gz"))
    a = ap.parse_args()

    ident = json.load(open(CKPT_DIR / "identity.json"))["sha256"]
    decks = {"weezing": ROOT / "decks/research/weezing.txt", "lucario": ROOT / "decks/research/lucario.txt"}
    checks = {"add-on": sha(T.addon_path()), "deck: weezing": sha(decks["weezing"]),
              "deck: lucario": sha(decks["lucario"])}
    for k, v in checks.items():
        if v != ident[k]:
            sys.exit(f"{k} does not match the checkpoint's identity.json: {v}")
    weights = CKPT_DIR / "ckpt_1800k_avg_lucario.npz"
    manifest = json.load(open(ROOT / "project_manifest.json"))
    listed = json.dumps(manifest)
    if sha(weights) not in listed:
        print(f"note: weights hash {sha(weights)} is not listed in project_manifest.json", file=sys.stderr)

    S = json.load(open(CKPT_DIR / "settings.json"))
    S["pool"] = {k: str(v.relative_to(ROOT)) for k, v in decks.items()}  # same files, hashes checked above
    T.set_decks(S)
    env = T.make_env()
    net = T.load_scorer(str(weights), env.obs_dim + env.action_dim)
    env.raw.set_recording(True)
    L, W = str(decks["lucario"]), str(decks["weezing"])
    with gzip.open(a.out, "wt") as f:
        for i in range(a.start, a.start + a.games):
            seed = SEED_BASE + i
            seat = i % 2
            d0, d1 = (L, W) if seat == 0 else (W, L)
            env.reset(d0, d1, seed, bots=[None, "k3"] if seat == 0 else ["k3", None])
            rng = np.random.default_rng(seed)
            net_moves = []
            while not env.done:
                p = env.current_player
                assert p == seat
                q = net.score_actions(env.observe(p), env.action_features())
                k = T.pick(q, rng)
                net_moves.append({"chosen": k, "q": [round(float(x), 5) for x in q]})
                env.step(k)
            w, pts, turns = env.result()
            moves = [[p, kind, js] for p, kind, js, _view in env.raw.history()]
            f.write(json.dumps({"i": i, "seed": seed, "lucario_seat": seat,
                                "decks": ["lucario", "weezing"] if seat == 0 else ["weezing", "lucario"],
                                "winner": w, "points": list(pts), "turns": turns,
                                "moves": moves, "net": net_moves}) + "\n")
            if (i + 1) % 50 == 0:
                print(f"{i + 1} games", flush=True)
    print(json.dumps({"checks": checks, "weights": sha(weights)}))


if __name__ == "__main__":
    main()
