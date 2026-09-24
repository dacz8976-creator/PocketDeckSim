"""Is k3 through the add-on the same k3 as in the engine's own loop? Run from the project root:
    python rl/step1b_k3_replay_check.py

For each seed: play k3 vs k3 in the engine's own loop and record one seat's choices. Then
replay the game through the add-on: that seat goes through `step` (the path the network
uses, which skips the engine's per-seat decision counter), and the other seat is k3 run by
the engine. If skipping the counter changed anything about k3, its moves would differ and
the final game state would not match. Done for both seats.
At every replayed decision it also checks that the legal-move list the add-on offers the
network (every move, in order), the game state, and the PlayerObservation are identical to
what the engine's own loop had at that decision. "same_as_next" counts how often a
decision's fingerprint equals the next decision's: a sensitivity check that the
fingerprints actually change as the game moves.
Control: the same replay with k2 on the engine side instead of k3 should NOT match,
showing the check can tell two bots apart.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pdl_env import PocketEnv  # noqa: E402
from pdl_rl_env import engine_play_record  # noqa: E402

ROOT = HERE.parent  # the repo root (on the laptop this file sat two folders down)
DECK = str(ROOT / "decks/brews/brew-03a-arceus-nihilego-toxapex.txt")
N, SEED0 = 50, 18_500_000


def replay(env, seed, seat, rec, bot, prints=None, tally=None):
    """prints/tally: also compare, at every replayed decision, the legal-move list the
    add-on offers the network, the game state, and the PlayerObservation with what the
    engine's own loop had at that same decision."""
    bots = [None, bot] if seat == 0 else [bot, None]
    env.reset(DECK, DECK, seed, bots=bots)
    i = 0
    while not env.done:
        if i >= len(rec) or env.current_player != seat:
            return None  # the game has already gone differently
        if prints is not None:
            fp = env.raw.decision_fingerprint()
            tally["decisions"] += 1
            for k, name in enumerate(("moves", "state", "observation")):
                tally[f"{name}_mismatch"] += fp[k] != prints[i][k]
                if i + 1 < len(prints):  # sensitivity: the next decision should differ
                    tally[f"{name}_same_as_next"] += fp[k] == prints[i + 1][k]
            tally["pairs_vs_next"] += i + 1 < len(prints)
        try:
            env.step(rec[i])
        except IndexError:  # recorded move no longer legal: the game went differently
            return None
        i += 1
    return i == len(rec), env.raw.final_state_hash(), env.result()


def main():
    env = PocketEnv()
    tally = {"decisions": 0, "pairs_vs_next": 0}
    for name in ("moves", "state", "observation"):
        tally[f"{name}_mismatch"] = 0
        tally[f"{name}_same_as_next"] = 0
    out = {"games_per_seat": N, "k3": {"0": 0, "1": 0}, "control_k2_matched": {"0": 0, "1": 0},
           "results": {"seat0_win": 0, "seat1_win": 0, "draw": 0}, "per_decision": tally}
    for i in range(N):
        seed = SEED0 + i
        for seat in (0, 1):
            rec, prints, h_ref, res_ref = engine_play_record(DECK, DECK, seed, ("k3", "k3"), seat)
            r = replay(env, seed, seat, rec, "k3", prints, tally)
            if r is not None and r[0] and r[1] == h_ref and tuple(r[2][:1]) + tuple(r[2][1]) == tuple(res_ref[:1]) + tuple(res_ref[1]):
                out["k3"][str(seat)] += 1
            c = replay(env, seed, seat, rec, "k2")
            if c is not None and c[0] and c[1] == h_ref:
                out["control_k2_matched"][str(seat)] += 1
            if seat == 0:
                w = res_ref[0]
                out["results"]["draw" if w == -1 else f"seat{w}_win"] += 1
    ok = (out["k3"]["0"] == N and out["k3"]["1"] == N and sum(out["control_k2_matched"].values()) < 2 * N
          and tally["decisions"] > 0
          and all(tally[f"{n}_mismatch"] == 0 for n in ("moves", "state", "observation")))
    out["pass"] = ok
    print(json.dumps(out, indent=1))
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/step1b_k3_replay.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
