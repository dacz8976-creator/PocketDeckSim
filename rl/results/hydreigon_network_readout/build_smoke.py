"""Smoke test only (tests the program, not the bot): builds a tiny fake run folder for readout.py the way
train_v5.py writes one (settings.json, identity.json, state.json, eval_games.jsonl with bar and confirmation rows
from train_v5's own eval_chunk, checkpoint files, a REPORT.txt line). One process, a handful of games.
    python build_smoke.py --kind weezing     stage 1's confirmed networks (ckpt_1800k_avg, weezing + lucario)
    python build_smoke.py --kind hydreigon   untrained networks on Hydreigon v Lucario, to exercise the Hyper Ray
                                             and Roar in Unison code on the real card
Folders: /tmp/hyd-readout-smoke/<kind>-lucario. Seeds (Claude Code's sub-block for this readout, 21,001,000,000 -
21,001,999,999): weezing 21,001,000,000 + i, hydreigon 21,001,010,000 + i.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
RL = HERE.parents[1]
sys.path.insert(0, str(RL))
import train_v5 as T  # noqa: E402
from model import MLP  # noqa: E402

SEED = {"weezing": 21_001_000_000, "hydreigon": 21_001_010_000}
STAGE1 = RL / "checkpoints/run5-stage1-weezing-lucario"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=list(SEED), required=True)
    ap.add_argument("--games", type=int, default=4)
    ap.add_argument("--out", default="/tmp/hyd-readout-smoke")
    a = ap.parse_args()
    run_dir = Path(a.out) / f"{a.kind}-lucario"
    if run_dir.exists():
        if not (run_dir / "SMOKE").exists():
            raise SystemExit(f"{run_dir} exists and isn't a smoke folder; not touching it")
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True)
    (run_dir / "SMOKE").write_text("fake run folder for readout.py's smoke test\n")
    base = SEED[a.kind]
    S = dict(T.SETTINGS)
    S.update(pool={a.kind: f"decks/research/{a.kind}.txt", "lucario": "decks/research/lucario.txt"},
             pairing_weights={f"{a.kind}|lucario": 1.0}, held_out={}, criteria=None, avg_half_life_games=100_000,
             bar_per_pairing=a.games, confirm_per_matchup=a.games, workers=1,
             seeds={"train": base + 100_000, "k3": base + 200_000, "random": base + 300_000, "confirm": base,
                    "transfer": base + 400_000})
    T.set_decks(S)
    (run_dir / "settings.json").write_text(json.dumps(S, indent=1))
    ident = {"sha256": {f"deck: {n}": T.sha_file(T.ROOT / rel) for n, rel in S["pool"].items()}}
    ident["sha256"]["add-on"] = T.sha_file(T.addon_path())
    (run_dir / "identity.json").write_text(json.dumps(ident, indent=1))
    env = T.make_env()
    dim = env.obs_dim + env.action_dim
    name = "ckpt_1800k_avg" if a.kind == "weezing" else "ckpt_untrained"
    for k, d in enumerate(S["pool"]):
        if a.kind == "weezing":
            shutil.copyfile(STAGE1 / f"ckpt_1800k_avg_{d}.npz", T.ckpt_path(run_dir, name, d))
        else:
            T.save_net(T.ckpt_path(run_dir, name, d), MLP(dim, T.HIDDEN, seed=k), with_optimizer=False)
    T._eval_init(dim, S)
    bars = T.eval_chunk((None, T.bar_games(S), False))
    lines = [json.dumps(dict(g, kind="bar", ckpt=None)) for g in bars]
    st = {"status": "FINISHED", "reason": "smoke test folder", "bars": T.bar_rates(bars), "confirmations": [],
          "flags": [], "checkpoints": []}
    for d in S["pool"]:
        games = T.eval_chunk((T.ckpt_paths(run_dir, name, S), T.confirm_games(S, d), True))
        lines += [json.dumps(dict(g, kind="confirmation", ckpt=name, deck=d)) for g in games]
        rates = T.by_tag(games)
        mg = {t: rates[t]["win_rate"] - st["bars"][t]["win_rate"] for t in rates}
        st["confirmations"].append({"deck": d, "name": name, "rates": rates, "margins": mg,
                                    "margin": sum(mg.values()) / len(mg), "paired": T.paired(games, bars)})
    st["verdict"] = {"picks": {d: name for d in S["pool"]}, "criteria": [], "pass": None}
    (run_dir / "eval_games.jsonl").write_text("\n".join(lines) + "\n")
    (run_dir / "state.json").write_text(json.dumps(st, indent=1))
    (run_dir / "REPORT.txt").write_text("".join(f"Confirmation of the {d} network's {name} (used for the verdict): smoke\n"
                                                for d in S["pool"]))
    print(f"Smoke run folder {run_dir}: input dim {dim}, {len(bars)} bar games, {len(lines) - len(bars)} confirmation "
          f"games, seeds {base:,} + i (i < {a.games}); confirmed {name} for {', '.join(S['pool'])}")


if __name__ == "__main__":
    main()
