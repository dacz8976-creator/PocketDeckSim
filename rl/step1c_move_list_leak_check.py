"""Can the legal-move list leak hidden cards? Run from the project root:
    python "Boss Folder/rl-feasibility-2026-09-18/step1c_move_list_leak_check.py"

At every decision, rebuild the position with the opponent's hidden cards (hand + deck)
reshuffled and our own deck reordered, and ask the engine for the legal moves again.
If the list changes, the moves we're offered depend on something we can't see: a card in
the opponent's hand, or where a card sits in a deck. That's a leak the network could learn
to exploit. Card-by-card name checks can't tell the difference in a mirror match (both
decks hold the same cards), so this reshuffle test is the stronger version.
Covers 200 random-vs-random games and 100 games against k3 (50 per seat).
Control: reshuffling OUR OWN hand with our deck must change the list at least sometimes,
which shows the test notices when the list does change.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pdl_env import PocketEnv  # noqa: E402

ROOT = HERE.parent.parent
DECK = str(ROOT / "decks/brews/brew-03a-arceus-nihilego-toxapex.txt")


def main():
    env = PocketEnv()
    out = {"decisions_checked": 0, "move_list_changed": 0, "examples": [],
           "control_checked": 0, "control_changed": 0,
           "games": {"random_vs_random": 200, "vs_k3": 100}}
    rng = np.random.default_rng(7)
    for g in range(300):
        bots = None if g < 200 else (["k3", None] if g % 2 else [None, "k3"])
        env.reset(DECK, DECK, 19_000_000 + g, bots=bots)
        while not env.done:
            same = env.raw.hidden_move_probe(int(rng.integers(1 << 30)))
            if same is not None:
                out["decisions_checked"] += 1
                if not same:
                    out["move_list_changed"] += 1
                    if len(out["examples"]) < 5:
                        out["examples"].append({"seed": 19_000_000 + g, "moves": env.legal_actions()})
                c = env.raw.hidden_move_probe(int(rng.integers(1 << 30)), True)
                out["control_checked"] += 1
                out["control_changed"] += (c is False)
            env.step(int(rng.integers(env.num_actions())))
    out["pass"] = (out["decisions_checked"] > 0 and out["move_list_changed"] == 0
                   and out["control_changed"] > 0)
    print(json.dumps(out, indent=1))
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/step1c_move_list_leak.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
