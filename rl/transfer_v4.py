"""Run 4 report step: the two held-out decks, faced (Fable).
Run after train_v4.py (run_training_v4.sh does it):  python transfer_v4.py --run runs/<name>

For each held-out deck H (never trained on) and each pool deck P, on the same seeds and seats:
  bar   k3 piloting P against k3 piloting H
  (a)   P's own network piloting P against k3 piloting H  -> does it handle an opponent it never met?
Piloting a held-out deck is no longer meaningful: in run 4 each network has one deck, and nothing was trained
to pilot H. Each row is compared with k3 piloting the same deck in the bar games (paired). The card list stays
the run's own; the held-out decks' cards read as "other card". A report line, not a pass rule.
Uses each network's best confirmed checkpoint (the ones the verdict used). A finished result is reused only if
its inputs are unchanged (checkpoints, all seven decks, settings, code, add-on); otherwise it's redone and the
old file kept. The decks must still be the ones the run recorded at its start (Astra's review).
"""
import argparse
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import train_v4 as T  # noqa: E402


def specs(S):
    bars, bot = [], []
    names = list(S["pool"])
    for h_i, h in enumerate(S["held_out"]):
        for p_i, p in enumerate(names):
            q = h_i * len(names) + p_i
            for i in range(S["transfer_per_row"]):
                seed = T.SEEDS["transfer"] + q * 100_000 + i
                d = (p, h) if i % 2 == 0 else (h, p)
                bars.append((seed, *d, "k3k3", None, f"{p}|{h}"))
                bot.append((seed, *d, "k3", d.index(p), f"{p}>{h}"))
    return bars, bot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--ckpt", default="")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--redo", action="store_true")
    a = ap.parse_args()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    st = json.loads((run_dir / "state.json").read_text())
    if not st.get("verdict"):
        print("No confirmed networks (the run stopped before leveling off); held-out test skipped.")
        return
    picks = st["verdict"]["picks"]          # deck -> its best confirmed checkpoint
    name = "+".join(sorted(set(picks.values())))
    out = HERE / f"results/transfer_v4_{run_dir.name}_{name}.json"
    T.check_decks_unchanged(run_dir, S, held_out=True)
    inputs = T.report_inputs("transfer", run_dir, S, sorted(picks.items())[0][1], ["transfer_v4.py"], nets=picks)
    inputs["picks"] = picks
    if out.exists():
        old = json.loads(out.read_text())
        if old.get("inputs") == inputs and not a.redo:
            print(f"{out.name} exists with the same inputs; skipped (--redo to rerun)")
            return
        kept = out.with_name(f"{out.stem}.superseded-{time.strftime('%Y%m%d-%H%M%S')}.json")
        out.replace(kept)
        print(f"{out.name}: redoing ({'--redo' if a.redo else 'its inputs changed'}); the old result is kept as {kept.name}")
    T.set_decks(S)
    dim = T.env_dims()
    bars, bot = specs(S)
    nets = {d: str(T.ckpt_path(run_dir, picks[d], d)) for d in S["pool"]}
    with mp.get_context("spawn").Pool(a.workers, initializer=T._eval_init, initargs=(dim, S)) as pool:
        bar_games = T.run_games(pool, None, bars, a.workers)
        bot_games = T.run_games(pool, nets, bot, a.workers)
    bar = T.bar_rates(bar_games)
    rates = T.by_tag(bot_games)
    pr = T.paired(bot_games, bar_games)
    rows = {t: {"bot": rates[t]["win_rate"], "k3": bar[t]["win_rate"], "margin": rates[t]["win_rate"] - bar[t]["win_rate"],
                **pr[t]} for t in rates}
    n = S["transfer_per_row"]
    lines = [f"Held-out test (run 4) — {run_dir.name}, each network's best confirmed checkpoint "
             f"({', '.join(f'{d} {c}' for d, c in sorted(picks.items()))}): {n:,} games per row, paired with k3 "
             f"on the same seeds", "",
             f"  {'network pilots':<14}{'against (k3)':<14}{'network':>9}{'k3, same deck':>15}{'margin':>9}{'games won only by':>28}"]
    for h in S["held_out"]:
        lines.append(f"  facing {h}, a deck none of them ever met:")
        for p in S["pool"]:
            r = rows[f"{p}>{h}"]
            lines.append(f"  {p:<14}{h:<14}{r['bot']:>9.1%}{r['k3']:>15.1%}{100 * r['margin']:>+8.1f}"
                         f"   network {r['bot_only']:>4} / k3 {r['k3_only']:>4} (p {r['p']:.2g})")
    text = "\n".join(lines)
    print(text)
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"summary": text, "rows": rows, "checkpoints": picks, "games_per_row": n,
                               "inputs": inputs}, indent=1))


if __name__ == "__main__":
    main()
