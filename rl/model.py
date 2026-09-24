"""Small action-scoring network (numpy only, no torch needed).

Q(obs, action) = MLP([obs ; action_features]) -> one number, trained by mean-squared
error toward the final game outcome (+1/-1/0). This is the Deep Monte-Carlo (DMC) idea
from DouZero / RLCard's dmc_agent, minus the LSTM history and the GPU learner.
"""
import numpy as np


class MLP:
    def __init__(self, in_dim, hidden=(512, 256), seed=0, lr=1e-3, zero_last=False):
        rng = np.random.default_rng(seed)
        dims = [in_dim, *hidden, 1]
        self.W = [(rng.standard_normal((a, b)) * np.sqrt(2.0 / a)).astype(np.float32) for a, b in zip(dims[:-1], dims[1:])]
        self.b = [np.zeros(b, dtype=np.float32) for b in dims[1:]]
        if zero_last:  # untrained net scores every action the same: no built-in preference
            self.W[-1][:] = 0.0
        self.lr = lr
        self.t = 0
        self.m = [np.zeros_like(p) for p in self.W + self.b]
        self.v = [np.zeros_like(p) for p in self.W + self.b]

    @property
    def n_params(self):
        return int(sum(p.size for p in self.W + self.b))

    def forward(self, x):
        h = x
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            h = h @ W + b
            if i < len(self.W) - 1:
                np.maximum(h, 0, out=h)
        return h[:, 0]

    def score_actions(self, obs, act_feats):
        """Q for every legal action of one decision."""
        x = np.empty((act_feats.shape[0], obs.shape[0] + act_feats.shape[1]), dtype=np.float32)
        x[:, : obs.shape[0]] = obs
        x[:, obs.shape[0]:] = act_feats
        return self.forward(x)

    def train_step(self, x, y):
        """One Adam step on mean-squared error. Returns the loss."""
        acts = [x]
        h = x
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            h = h @ W + b
            if i < len(self.W) - 1:
                h = np.maximum(h, 0)
            acts.append(h)
        pred = h[:, 0]
        err = pred - y
        loss = float(np.mean(err ** 2))
        g = (2.0 / len(y)) * err[:, None].astype(np.float32)
        gW, gb = [None] * len(self.W), [None] * len(self.b)
        for i in reversed(range(len(self.W))):
            gW[i] = acts[i].T @ g
            gb[i] = g.sum(0)
            if i > 0:
                g = (g @ self.W[i].T) * (acts[i] > 0)
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for j, (p, gp) in enumerate(zip(self.W + self.b, gW + gb)):
            self.m[j] = b1 * self.m[j] + (1 - b1) * gp
            self.v[j] = b2 * self.v[j] + (1 - b2) * gp * gp
            mh = self.m[j] / (1 - b1 ** self.t)
            vh = self.v[j] / (1 - b2 ** self.t)
            p -= (self.lr * mh / (np.sqrt(vh) + eps)).astype(np.float32)
        return loss
