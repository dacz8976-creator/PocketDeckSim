"""Python face of the training interface (wraps the Rust module pdl_rl_env).

reset(deck_a_path, deck_b_path, seed) -> new game
observe(player) -> fixed-length float32 vector built only from PlayerObservation
legal_actions() -> readable list; action_features() -> (n_actions, action_dim) float32
step(action_index) -> True when the game ended; illegal index raises IndexError
reward(player) -> +1 win / -1 loss / 0 draw (raises if the game is not over)

Forced moves (exactly one legal option) are played automatically, the same way the
engine's own loop does, so every decision the caller sees has at least two options.
"""
import numpy as np
from pdl_rl_env import RawEnv, Snapshot, engine_play  # noqa: F401


class PocketEnv:
    def __init__(self, vocab_deck_paths=None, features="v1"):
        """features: "v1" (run 1's encoding) or "v2" (adds consequence and threat features;
        needs add-on 0.4.0 or later)."""
        self._vocab_paths = list(vocab_deck_paths) if vocab_deck_paths else None
        self._features = features
        self.raw = None

    def _ensure(self, paths):
        if self.raw is None:
            ids = sorted({i for p in (self._vocab_paths or paths) for i in RawEnv.deck_card_ids(p)})
            # v1 is called the old way so this file still works with the 0.1.0 add-on
            self.raw = RawEnv(ids) if self._features == "v1" else RawEnv(ids, self._features)

    def reset(self, deck_a_path, deck_b_path, seed, bots=None):
        self._ensure([deck_a_path, deck_b_path])
        self.raw.reset(deck_a_path, deck_b_path, int(seed), bots)
        return self

    @property
    def obs_dim(self):
        return self.raw.obs_dim

    @property
    def action_dim(self):
        return self.raw.action_dim

    @property
    def current_player(self):
        return self.raw.current_player

    @property
    def done(self):
        return self.raw.done

    def observe(self, player):
        return np.frombuffer(self.raw.observe(player), dtype="<f4")

    def legal_actions(self):
        return self.raw.legal_actions()

    def num_actions(self):
        return self.raw.num_actions()

    def action_features(self):
        n = self.raw.num_actions()
        return np.frombuffer(self.raw.action_features(), dtype="<f4").reshape(n, self.raw.action_dim)

    def step(self, action_index):
        if isinstance(action_index, bool) or int(action_index) != action_index:
            raise TypeError(f"action index must be an integer, got {action_index!r}")
        return self.raw.step(int(action_index))

    def reward(self, player):
        return self.raw.reward(player)

    def result(self):
        return self.raw.result()
