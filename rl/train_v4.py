"""Run 4: ONE NETWORK PER PILOTED DECK for a five-deck pool (encoding v2.2), judged per matchup against k3.

Run 3 with one thing changed, plus the two benching numbers. See FEASIBILITY.md "Run 4 design" (Fable,
Sept 20, signed off):
  - five networks, one per pool deck; each pilots only its own deck. A training game draws one of the 10
    cross pairings (evenly) and each seat is piloted by that deck's own network, so every game trains two
    networks, each only on its own side's decisions. The card list is still all five decks.
  - encoding v2.2 (add-on 0.6.0): two numbers per move — how many Pokemon I'd have in play after it, and
    whether losing the Active right then would lose the game — in place of the threat "certain" flag.
  - the bars first: k3 piloting both sides of every pairing, 1,000 games each on the confirmation seeds
  - checkpoints every 500,000 games; each network plays its four matchups against k3, 1,000 games each,
    on seeds the confirmation never uses. A network's score is its AVERAGE MARGIN over those four.
  - leveled off, per network: 3 checkpoints in a row within 3 points of each other, and the newest winning
    no more than 55% of the games it and its predecessor decide differently (the eval seeds are fixed, so
    that is a paired comparison; no mirror match needed). The run ends when every network has leveled off,
    or at the 6M-game cap. No time budget.
  - floors, per network, from run 3's own curve (insurance, not a judgement)
  - then each network's best checkpoint (plus its runner-up within 2 points) replays its matchups on the
    bars' own seeds; the pass rules are fixed in the settings before the run: Blaziken vs Lucario at least
    +10, at or above k3 where the headroom test says there is room, and nothing more than 5 under k3.

Start or resume (inside WSL), from anywhere:
    python train_v4.py --run runs/<name>
Running the same command again after an interruption resumes from the last save. run_training_v4.sh runs
this and then every report step. Everything a person needs is in <run>/STATUS.txt.

--smoke runs a scaled-down copy of every step (for testing the program, not the bot).
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import collections  # noqa: E402
import fcntl  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import uuid  # noqa: E402
import json  # noqa: E402
import multiprocessing as mp  # noqa: E402
import queue as queue_mod  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from model import MLP  # noqa: E402
from pdl_env import PocketEnv  # noqa: E402

ROOT = HERE.parent.parent
HIDDEN = (512, 256)
STUDY = "Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks"
DECKS = {}  # {"paths": {name: absolute path}, "features": name}; set once from the run's settings in every process

POOL = {  # name -> path from the project root; the order is fixed and used everywhere
    "blaziken": "decks/dustin/06-mega-blaziken-tournament-list.txt",
    "lucario": f"{STUDY}/lucario.txt",
    "weezing": f"{STUDY}/weezing.txt",
    "altaria": f"{STUDY}/altaria.txt",
    "suicune": f"{STUDY}/suicune.txt",
}
LIMITLESS_SHARE = {"lucario": 8.58, "altaria": 5.11, "suicune": 4.8, "weezing": 4.17}


def default_weights(pool, share):
    """Half the games: Blaziken vs each other deck, by Limitless share. Half: the other pairings, evenly."""
    names = list(pool)
    pairs = [f"{a}|{b}" for i, a in enumerate(names) for b in names[i + 1:]]
    bl = [p for p in pairs if "blaziken" in p.split("|")]
    rest = [p for p in pairs if p not in bl]
    tot = sum(share[p.replace("blaziken", "").strip("|")] for p in bl)
    w = {p: 0.5 * share[p.replace("blaziken", "").strip("|")] / tot for p in bl}
    w.update({p: 0.5 / len(rest) for p in rest})
    return w


# Run 3's shared network, average margin per piloted deck at 1M and 2M games: the floors are set from this
# curve (Fable), not from run 2's. A run 4 network well below run 3's shared network is broken, not slow.
RUN3_CURVE = {1_000_000: {"blaziken": 0.007, "lucario": -0.004, "weezing": -0.191, "altaria": -0.096, "suicune": -0.288},
              2_000_000: {"blaziken": 0.007, "lucario": 0.036, "weezing": -0.208, "altaria": -0.097, "suicune": -0.355}}

SETTINGS = dict(
    workers=8, budget=6_000_000, features="v2.2", pool=POOL,
    pairing_weights={f"{a}|{b}": 0.1 for a, b in [(x, y) for i, x in enumerate(POOL) for y in list(POOL)[i + 1:]]},
    checkpoints=list(range(500_000, 6_000_001, 500_000)),
    draw_gate_at=250_000, draw_window=20_000, draw_gate_max=0.10, shaping_off_below=0.05,
    eps_early=0.10, eps_late=0.05, eps_switch=1_000_000, past_share=0.20,
    lr=1e-4, batch=512, buffer=40_000, min_buffer=4_000, uses_target=2.0, publish_every=50,
    gamma=0.97,
    eval_k3_per_matchup=1000, eval_random=500, confirm_per_matchup=1000, bar_per_pairing=1000,
    # floors (insurance), per network: its average margin must stay within `below_run3` of run 3's shared
    # network at the same game count, and it must beat random moves at least `random` of the time
    floors=[(1_000_000, {"random": 0.90, "below_run3": 0.10}), (2_000_000, {"below_run3": 0.05})],
    level_window=3, level_spread=0.03, level_prev_max=0.55, runner_up_gap=0.02,
    # the pass rules, fixed before the run (Fable, Sept 20), judged per matchup on the paired confirmation
    # of each network's best confirmed checkpoint. "at_least_k3" is the list of matchups where the headroom
    # test (results/run3_checks/k2_headroom_pool.json) says deeper search barely pays, so beating k3 is on.
    criteria={"hold": {"blaziken>lucario": 0.10},
              "at_least_k3": ["blaziken>weezing", "altaria>blaziken", "altaria>lucario", "altaria>suicune"],
              "no_matchup_below": -0.05},
    # a report line, not a rule: checkup deaths with a retreat on offer that turn, counted separately in
    # positions the network still rated winnable (its score for the move it chose above winnable_q)
    checkup_report={"winnable_q": -0.5},
    held_out={"ninetales": "decks/dustin/13-a-ninetales-raticate.txt",
              "manectric": "decks/dustin/09-mega-manectric-heliolisk.txt"},
    transfer_per_row=1000,
    record_selfplay_every=1000, queue_max=4000,
)
SMOKE = dict(
    workers=2, budget=12_000, checkpoints=[3_000, 6_000, 9_000, 12_000], draw_gate_at=3_000,
    draw_window=1_000, eps_switch=6_000, buffer=4_000, min_buffer=400, draw_gate_max=0.60,
    eval_k3_per_matchup=4, eval_random=8, confirm_per_matchup=4, bar_per_pairing=4,
    floors=[(6_000, {"random": 0.10, "below_run3": 0.9})], level_spread=0.9, level_prev_max=1.0, runner_up_gap=1.0,
    transfer_per_row=4, record_selfplay_every=100,
)
SEEDS = {"train": 3_000_000_000, "k3": 80_000_000, "random": 81_000_000,
         "confirm": 90_000_000, "transfer": 95_000_000}
# Training game seeds: SEEDS["train"] + resume_epoch * EPOCH_SPAN + the game's own number (unique across workers,
# because every game number is claimed once under a lock). Needs budget < EPOCH_SPAN, checked at start (Astra's review).
EPOCH_SPAN = 100_000_000


# ---------------------------------------------------------------- network helpers
def params(net):
    return net.W + net.b


def flatten(net):
    return np.concatenate([p.ravel() for p in params(net)])


def unflatten_into(net, flat):
    o = 0
    for p in params(net):
        p[...] = flat[o:o + p.size].reshape(p.shape)
        o += p.size


def save_net(path, net, with_optimizer=True):
    arrays = {f"p{i}": p for i, p in enumerate(params(net))}
    if with_optimizer:
        arrays.update({f"m{i}": m for i, m in enumerate(net.m)})
        arrays.update({f"v{i}": v for i, v in enumerate(net.v)})
        arrays["t"] = np.array([net.t])
    tmp = Path(str(path) + ".tmp")
    with open(tmp, "wb") as f:
        np.savez(f, **arrays)
    os.replace(tmp, path)


def ckpt_path(run_dir, name, deck):
    """One file per network: ckpt_1000k_blaziken.npz and so on."""
    return run_dir / f"{name}_{deck}.npz"


def ckpt_paths(run_dir, name, S):
    return {deck: str(ckpt_path(run_dir, name, deck)) for deck in S["pool"]}


def load_net(path, dim, lr=1e-4):
    net = MLP(dim, HIDDEN, seed=0, lr=lr)
    z = np.load(path)
    for i, p in enumerate(params(net)):
        p[...] = z[f"p{i}"]
    if "t" in z:
        for i in range(len(net.m)):
            net.m[i][...] = z[f"m{i}"]
            net.v[i][...] = z[f"v{i}"]
        net.t = int(z["t"][0])
    return net


# Networks that only play (past opponents in training games, and every network in evaluation) are
# cached by the processes that use them. In run 4 both caches grew without limit, five networks per
# worker per checkpoint, and each copy carried optimizer state it never uses; at 3.5M games WSL ran out
# of memory during an evaluation (results/astra-review/V4_MEMORY_FAILURE_REVIEW_20260921.md).
# Both caches are now capped, and hold weights only. Every past checkpoint is still an eligible opponent:
# a network that was dropped is simply read again from its file, with exactly the same weights.
PAST_CACHE_CAP = 40   # per training worker: 40 x 2.7 MB; run 4 reaches 60 (checkpoint, deck) pairs by 6M
EVAL_CACHE_CAP = 10   # per evaluation worker: one evaluation needs at most five networks


def load_scorer(path, dim):
    """The same weights as load_net, bit for bit, without the optimizer state (a third of the memory)."""
    net = MLP(dim, HIDDEN, seed=0)
    z = np.load(path)
    for i, p in enumerate(params(net)):
        p[...] = z[f"p{i}"]
    net.m = net.v = None  # playing never trains
    return net


class NetCache:
    """At most `cap` networks; the least recently used one is dropped first."""

    def __init__(self, cap):
        self.cap, self.nets = cap, collections.OrderedDict()

    def get(self, key, load):
        if key in self.nets:
            self.nets.move_to_end(key)
            return self.nets[key]
        net = self.nets[key] = load()
        if len(self.nets) > self.cap:
            self.nets.popitem(last=False)
        return net

    def __len__(self):
        return len(self.nets)


def pick(q, rng):
    if not np.isfinite(q).all():
        raise RuntimeError("Network produced non-finite move scores")
    best = np.flatnonzero(q == q.max())
    return int(best[0]) if len(best) == 1 else int(rng.choice(best))


def set_decks(S):
    DECKS["paths"] = {name: str(ROOT / rel) for name, rel in S["pool"].items()}
    DECKS["held_out"] = {name: str(ROOT / rel) for name, rel in S["held_out"].items()}
    DECKS["features"] = S["features"]


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def addon_path():
    return Path(importlib.util.find_spec("pdl_rl_env.pdl_rl_env").origin)


def check_decks_unchanged(run_dir, S, held_out=False):
    """Report steps use the run's own deck bytes: refuse if a deck file changed since the run started."""
    saved = json.loads((run_dir / "identity.json").read_text())["sha256"]
    decks = {f"deck: {n}": rel for n, rel in S["pool"].items()}
    if held_out:
        decks.update({f"held-out: {n}": rel for n, rel in S["held_out"].items()})
    changed = [role for role, rel in decks.items() if saved.get(role) != sha_file(ROOT / rel)]
    if changed:
        raise SystemExit(f"{', '.join(changed)}: the file differs from the one this run used (identity.json). "
                         f"Restore it to rerun this report step.")


def report_inputs(step, run_dir, S, ckpt, code, records=None, nets=None):
    """Everything a cached report result depends on. A cached result is reused only when this matches exactly
    (Astra's review); otherwise it is regenerated and the old file kept as prior evidence.
    `nets`: {deck: checkpoint name} for the networks the result was made from (default: `ckpt` for all)."""
    decks = dict(S["pool"], **(S["held_out"] if step == "transfer" else {}))
    nets = nets or {d: ckpt for d in S["pool"]}
    keys = ("pool", "held_out", "features", "checkup_report", "transfer_per_row") if step == "transfer" else \
        ("pool", "features", "checkup_report")
    out = {"step": step, "checkpoint": ckpt,
           "checkpoint sha256": {d: sha_file(ckpt_path(run_dir, n, d)) for d, n in nets.items()},
           "decks": {n: sha_file(ROOT / rel) for n, rel in decks.items()},
           "settings": {k: S.get(k) for k in keys},
           "code": {n: sha_file(HERE / n) for n in sorted(set(code) | {"train_v4.py", "model.py", "pdl_env.py"})},
           "add-on": sha_file(addon_path())}
    if records is not None:
        out["records sha256"] = hashlib.sha256("\n".join(records).encode()).hexdigest()
    return out


def pairings(S):
    """The 10 cross pairings as (A, B) in pool order; A is placed in seat i % 2 in bar/confirmation game i."""
    names = list(S["pool"])
    return [(a, b) for i, a in enumerate(names) for b in names[i + 1:]]


def directed(S):
    """The 20 directed matchups (bot's deck, k3's deck)."""
    return [m for a, b in pairings(S) for m in ((a, b), (b, a))]


def make_env():
    """Card list = all five pool decks; the network was built for exactly this list."""
    paths = list(DECKS["paths"].values())
    env = PocketEnv(vocab_deck_paths=paths, features=DECKS["features"])
    env.reset(paths[0], paths[1], 1)
    return env


def turn_of(obs):
    return int(round(float(obs[0]) * 30))  # encoding scalar 0 is turn_count / 30


def env_dims():
    env = make_env()
    return env.obs_dim + env.action_dim


# ---------------------------------------------------------------- actor (plays training games)
def actor(wid, sh, q, run_dir, S, seed_base, rng_key, dim):
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ctrl+C is handled once, by the main process
    parent = os.getppid()
    q.cancel_join_thread()  # if the main process is gone, exit without waiting to flush games nobody will read
    try:
        set_decks(S)
        env = make_env()
        names = list(S["pool"])
        pair_names = list(S["pairing_weights"])
        pair_p = np.array([S["pairing_weights"][k] for k in pair_names], dtype=float)
        pair_p /= pair_p.sum()
        nets = {d: MLP(dim, HIDDEN, seed=0) for d in names}
        weights = {d: np.frombuffer(sh["weights"][d], dtype=np.float32) for d in names}
        my_ver = {d: -1 for d in names}
        pool_ver, pool_names, past = -1, [], NetCache(PAST_CACHE_CAP)
        rng = np.random.default_rng(rng_key)  # this worker's own stream for exploration, pairing and seat draws
        pause_seen = 0
        while not sh["stop"].value:
            if sh["pause"].value:
                pause_id = sh["pause"].value
                if pause_seen != pause_id:
                    while not sh["stop"].value:
                        try:
                            q.put((None, {"paused": wid, "pause_id": pause_id}), timeout=1.0)
                            pause_seen = pause_id
                            break
                        except queue_mod.Full:
                            if os.getppid() != parent:
                                return
                if os.getppid() != parent:
                    return
                time.sleep(0.01)
                continue
            with sh["claim_lock"]:
                game_no = sh["issued"].value  # this game's own number; no other worker can get it
                can_play = game_no < sh["limit"].value
                if can_play:
                    sh["issued"].value += 1
            if not can_play:
                time.sleep(0.002)
                continue
            if sh["pool_version"].value != pool_ver:
                pool_ver = sh["pool_version"].value
                pool_names = json.loads((run_dir / "pool.json").read_text())
            eps = sh["eps"].value
            seed = seed_base + game_no
            pairing = pair_names[int(rng.choice(len(pair_names), p=pair_p))]  # which two pool decks
            d = pairing.split("|")
            if rng.integers(2):
                d = d[::-1]  # either deck in either seat
            # 20% of games: one seat is that deck's own earlier checkpoint, the other is its current network
            past_seat, past_name, past_net = None, None, None
            if pool_names and rng.random() < S["past_share"]:
                past_seat = int(rng.integers(2))
                past_name = pool_names[int(rng.integers(len(pool_names)))]
                past_path = ckpt_path(run_dir, past_name, d[past_seat])
                past_net = past.get((past_name, d[past_seat]), lambda: load_scorer(past_path, dim))
            for x in set(d):  # copy in only the two networks this game needs, and only if they changed
                if sh["version"][x].value != my_ver[x]:
                    with sh["lock"]:
                        unflatten_into(nets[x], weights[x])
                        my_ver[x] = sh["version"][x].value
            env.reset(DECKS["paths"][d[0]], DECKS["paths"][d[1]], seed)
            rows = ([], [])
            turns_at = ([], [])
            moves = []
            while not env.done:
                p = env.current_player
                obs, feats = env.observe(p), env.action_features()
                model = past_net if p == past_seat else nets[d[p]]
                if rng.random() < eps:
                    i = int(rng.integers(len(feats)))
                else:
                    i = pick(model.score_actions(obs, feats), rng)
                if p != past_seat:
                    rows[p].append(np.concatenate([obs, feats[i]]))
                    turns_at[p].append(turn_of(obs))
                moves.append(i)
                env.step(i)
            winner, pts, turns = env.result()
            cap = turns > 30
            sides = []  # (deck, rows, targets) for every seat piloted by a current network
            for p in (0, 1):
                if p == past_seat or not rows[p]:
                    continue
                if winner == -1:
                    r = min(0.5, max(-0.5, 0.25 * (pts[p] - pts[1 - p]))) if (cap and sh["shaping"].value) else 0.0
                else:
                    r = 1.0 if winner == p else -1.0
                # a result reached sooner counts for more: GAMMA per game turn between move and end
                y = [r * S["gamma"] ** max(0, turns - t) for t in turns_at[p]]
                sides.append((d[p], np.asarray(rows[p], dtype=np.float32), np.asarray(y, dtype=np.float32)))
            meta = {"type": "past" if past_seat is not None else "self", "cap_draw": cap, "turns": turns,
                    "winner": winner, "decisions": len(moves), "decks": d}
            if past_seat is not None:
                meta["net_seat"] = 1 - past_seat
                meta["net_won"] = winner == 1 - past_seat
                meta["opp"] = past_name
            if (game_no + 1) % S["record_selfplay_every"] == 0:
                meta["record"] = {"seed": seed, "moves": moves, "type": meta["type"], "decks": d,
                                  "past_seat": past_seat, "past": past_name,
                                  "weights_version": {x: my_ver[x] for x in d}}
            item = (sides, meta)
            while True:  # never hang forever if the main process is gone
                try:
                    q.put(item, timeout=1.0)
                    break
                except queue_mod.Full:
                    if sh["stop"].value or os.getppid() != parent:
                        return
            if os.getppid() != parent:
                return
    except Exception:
        import traceback
        (run_dir / f"actor{wid}_error.txt").write_text(traceback.format_exc())
        raise


# ---------------------------------------------------------------- evaluation (greedy, no shaping)
_E = {}


def _eval_init(dim, S, parent_pid=None):
    if parent_pid is not None:
        # Pool workers otherwise can outlive a SIGKILL of the trainer on Linux/WSL.
        import ctypes
        import signal
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(1, signal.SIGTERM, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
            raise OSError(ctypes.get_errno(), "Cannot bind evaluation worker lifetime to trainer")
        if os.getppid() != parent_pid:
            os._exit(1)
    set_decks(S)
    _E["env"] = make_env()
    _E["dim"] = dim
    _E["nets"] = NetCache(EVAL_CACHE_CAP)
    _E["extra"] = dict(S.get("held_out", {}))  # held-out decks (transfer test) can be named in a game spec too


def _net(path):
    return _E["nets"].get(path, lambda: load_scorer(path, _E["dim"]))


def deck_path(name):
    if name in DECKS["paths"]:
        return DECKS["paths"][name]
    return str(ROOT / _E["extra"][name])


def eval_chunk(args):
    """Each game spec is (seed, deck in seat 0, deck in seat 1, mode, bot_seat, tag):
    mode "k3" = the deck's own network at bot_seat, k3 in the other seat; "k3k3" = k3 in both seats (a bar
    game); "random" = the network against uniformly random moves. `nets` maps a deck to its weights file."""
    nets, games, keep_moves = args
    env = _E["env"]
    out = []
    for seed, d0, d1, mode, seat, tag in games:
        rng = np.random.default_rng(seed)
        bots = None
        if mode == "k3":
            bots = [None, "k3"] if seat == 0 else ["k3", None]
        elif mode == "k3k3":
            bots = ["k3", "k3"]
        net = _net(nets[(d0, d1)[seat]]) if nets else None
        env.reset(deck_path(d0), deck_path(d1), seed, bots=bots)
        moves, opp_moves = [], []
        while not env.done:
            p = env.current_player
            obs, feats = env.observe(p), env.action_features()
            if p == seat:
                i = pick(net.score_actions(obs, feats), rng)
                moves.append(i)
            else:
                i = int(rng.integers(len(feats)))  # "random" mode: the other seat plays at random
                opp_moves.append(i)
            env.step(i)
        w, pts, turns = env.result()
        g = {"seed": seed, "decks": [d0, d1], "mode": mode, "bot_seat": seat, "tag": tag, "winner": w,
             "points": list(pts), "turns": turns}
        if keep_moves:
            g.update(moves=moves, opp_moves=opp_moves)
        out.append(g)
    return out


def run_games(pool, nets, games, workers, keep_moves=False):
    """`nets`: {deck: weights file} for the network side, or None for bar games (k3 vs k3)."""
    n = max(1, len(games) // (workers * 4))
    chunks = [games[i:i + n] for i in range(0, len(games), n)]
    out = []
    for part in pool.imap_unordered(eval_chunk, [(nets, c, keep_moves) for c in chunks]):
        out.extend(part)
    return out


def bar_games(S):
    """k3 pilots both sides; pairing (A, B), game i: A in seat i % 2. These seeds are the confirmation's too."""
    return [(SEEDS["confirm"] + p * 100_000 + i, *((a, b) if i % 2 == 0 else (b, a)), "k3k3", None, f"{a}|{b}")
            for p, (a, b) in enumerate(pairings(S)) for i in range(S["bar_per_pairing"])]


def confirm_games(S, deck=None):
    """The bar's seeds and placement, a network in one seat and k3 in the other. With `deck`, only that
    network's four matchups (run 4 confirms one network at a time)."""
    out = []
    for p, (a, b) in enumerate(pairings(S)):
        for i in range(S["confirm_per_matchup"]):
            seed, d = SEEDS["confirm"] + p * 100_000 + i, ((a, b) if i % 2 == 0 else (b, a))
            if deck in (None, a):
                out.append((seed, *d, "k3", d.index(a), f"{a}>{b}"))
            if deck in (None, b):
                out.append((seed, *d, "k3", d.index(b), f"{b}>{a}"))
    return out


def checkpoint_k3_games(S):
    """Fixed evaluation seeds the confirmation never uses; the network alternates seats."""
    out = []
    for p, (a, b) in enumerate(pairings(S)):
        for k, (x, y) in enumerate(((a, b), (b, a))):
            for i in range(S["eval_k3_per_matchup"]):
                d = (x, y) if i % 2 == 0 else (y, x)
                out.append((SEEDS["k3"] + p * 100_000 + k * 50_000 + i, *d, "k3", d.index(x), f"{x}>{y}"))
    return out


def random_games(S):
    """Each network against uniformly random moves, spread over its own four matchups."""
    out = []
    for p, (a, b) in enumerate(pairings(S)):
        for k, (x, y) in enumerate(((a, b), (b, a))):
            for i in range(max(1, S["eval_random"] // 4)):
                d = (x, y) if i % 2 == 0 else (y, x)
                out.append((SEEDS["random"] + p * 10_000 + k * 5_000 + i, *d, "random", d.index(x), f"{x}>{y}"))
    return out


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def deck_of(tag):
    return tag.split(">")[0]


def paired_share(new_games, old_games):
    """Of the games the two checkpoints decided differently, the share the newer one won.
    50% = no change; the evaluation seeds are fixed, so this is a paired comparison (no mirror needed)."""
    old = {(g["seed"], g["tag"]): g for g in old_games}
    only_new = only_old = 0
    for g in new_games:
        o = old.get((g["seed"], g["tag"]))
        if o is None:
            continue
        a, b = g["winner"] == g["bot_seat"], o["winner"] == o["bot_seat"]
        only_new += a and not b
        only_old += b and not a
    n = only_new + only_old
    return {"share": (only_new / n) if n else 0.5, "only_new": only_new, "only_old": only_old}


def win_rate_of(games):
    n = len(games)
    wins = sum(g["winner"] == g["bot_seat"] for g in games)
    seat = {s: [g for g in games if g["bot_seat"] == s] for s in (0, 1)}
    return {"games": n, "win_rate": wins / max(1, n), "draws": sum(g["winner"] == -1 for g in games),
            "seat0": sum(g["winner"] == 0 for g in seat[0]) / max(1, len(seat[0])),
            "seat1": sum(g["winner"] == 1 for g in seat[1]) / max(1, len(seat[1]))}


def by_tag(games):
    tags = sorted({g["tag"] for g in games})
    return {t: win_rate_of([g for g in games if g["tag"] == t]) for t in tags}


def bar_rates(games):
    """From the k3-vs-k3 bar games: k3's own win rate piloting each deck, per directed matchup."""
    out = {}
    for tag in sorted({g["tag"] for g in games}):
        a, b = tag.split("|")
        gs = [g for g in games if g["tag"] == tag]
        for x, y in ((a, b), (b, a)):
            as_bot = [dict(g, bot_seat=g["decks"].index(x)) for g in gs]  # k3 "piloting x" sits where x is
            out[f"{x}>{y}"] = win_rate_of(as_bot)
    return out


def exact_p(a, c):
    """Two-sided exact sign test on the discordant pairs."""
    from math import comb
    n = a + c
    if n == 0:
        return 1.0
    tail = sum(comb(n, i) for i in range(max(a, c), n + 1))
    return min(1.0, 2 * tail / 2 ** n)


def paired(conf_games, bar_games_):
    """Per directed matchup: the network vs k3 piloting the same deck on the same seed and seats."""
    bar = {g["seed"]: g for g in bar_games_}
    out = {}
    for tag in sorted({g["tag"] for g in conf_games}):
        x = tag.split(">")[0]
        a = c = 0
        for g in conf_games:
            if g["tag"] != tag:
                continue
            b = bar[g["seed"]]
            bot_won = g["winner"] == g["bot_seat"]
            k3_won = b["winner"] == b["decks"].index(x)
            a += bot_won and not k3_won
            c += k3_won and not bot_won
        out[tag] = {"bot_only": a, "k3_only": c, "p": exact_p(a, c)}
    return out



def grid(names, values, fmt, scale=1):
    """Rows = the deck the network (or k3, for bars) pilots; columns = the opposing deck."""
    w = max(len(n) for n in names) + 2
    rows = ["  " + " " * w + "".join(f"{n:>{w}}" for n in names)]
    for x in names:
        cells = []
        for y in names:
            v = values.get(f"{x}>{y}")
            cells.append(f"{'—':>{w}}" if v is None else f"{fmt.format(v * scale):>{w}}")
        rows.append(f"  {x:<{w}}" + "".join(cells))
    return rows


# ---------------------------------------------------------------- the run
class Run:
    def __init__(self, run_dir, S):
        self.dir, self.S = run_dir, S
        self.state_path = run_dir / "state.json"

    def fresh_state(self):
        return {"status": "RUNNING", "reason": "", "games": 0, "selfplay_games": 0, "resume_epoch": 0,
                "inserted": 0, "trained": 0, "window_inserted": 0, "window_trained": 0,
                "draw_window": [], "draw_start": None, "shaping": True, "low_draw_checks": 0,
                "draw_gate": None, "checkpoints": [], "confirmations": [], "confirmed": [], "bars": None,
                "elapsed_eval_s": 0.0, "draw_checked_at": None, "last_draw_rate": None,
                "leveled": [], "verdict": None, "flags": [], "past_games": 0, "past_wins": 0,
                "rate_games_per_sec": None, "elapsed_train_s": 0.0, "started": time.strftime("%Y-%m-%d %H:%M")}

    def save_state(self, st):
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=1))
        os.replace(tmp, self.state_path)

    def commit(self, st, nets):
        # Never overwrite the weights referenced by the previous committed state.
        stamp = uuid.uuid4().hex
        for deck, net in nets.items():
            save_net(self.dir / f"resume_{stamp}_{deck}.npz", net)
        st["resume_stamp"] = stamp
        st["log_sizes"] = {log: (self.dir / log).stat().st_size if (self.dir / log).exists() else 0
                           for log in ("eval_games.jsonl", "selfplay_samples.jsonl")}
        self.save_state(st)
        # the new state is on disk, so older resume files are no longer referenced (keeps the folder small)
        for old in self.dir.glob("resume_*.npz"):
            if not old.name.startswith(f"resume_{stamp}_"):
                old.unlink(missing_ok=True)

    def recover(self, st):
        # Keep interrupted output separately; only committed checkpoints enter the pool.
        recovery = self.dir / f"interrupted_attempt_{st['resume_epoch']}"
        for name, length in st["log_sizes"].items():
            path = self.dir / name
            if path.exists() and path.stat().st_size > length:
                recovery.mkdir(exist_ok=True)
                with path.open("rb+") as f:
                    f.seek(length)
                    (recovery / name).write_bytes(f.read())
                    f.truncate(length)
        committed = {c["name"] for c in st["checkpoints"]} | {"ckpt_0"}
        for path in self.dir.glob("ckpt_*.npz"):
            if path.name.rsplit("_", 1)[0] not in committed:
                recovery.mkdir(exist_ok=True)
                path.replace(recovery / path.name)
        (self.dir / "pool.json").write_text(json.dumps(sorted(committed)))

    def write_status(self, st):
        S = self.S
        g = st["games"]
        names = list(S["pool"])
        lines = [f"Run 4 (one network per deck, encoding {S['features']}) — {self.dir.name}   "
                 f"(updated {time.strftime('%Y-%m-%d %H:%M')})",
                 f"Networks: {', '.join(names)} · each pilots only its own deck · the {plural(len(names) * (len(names) - 1) // 2, 'pairing')} between them, evenly",
                 f"State: {st['status']}" + (f" — {st['reason']}" if st["reason"] else ""), ""]
        if st.get("bars"):
            lines += ["The bars: k3's own win rate piloting the row deck against k3 piloting the column deck",
                      f"({S['bar_per_pairing']:,} games per pairing, on the confirmation seeds):"]
            lines += grid(names, {t: v["win_rate"] for t, v in st["bars"].items()}, "{:.0%}")
            lines.append("")
        rate_ = st.get("rate_games_per_sec")
        hours = st["elapsed_train_s"] / 3600
        spent = f"{hours:.1f} h" if hours >= 1 else f"{hours * 60:.0f} min"
        evalh = st.get("elapsed_eval_s", 0.0) / 3600
        lines.append(f"Games played: {g:,} (safety cap {S['budget']:,}) · {spent} of training + {evalh:.1f} h of evaluation"
                     + (f" · {rate_:.0f} games/sec lately" if rate_ else ""))
        uses_all = st["trained"] / max(1, st["inserted"])
        uses_win = st["uses_lately"] if "uses_lately" in st else st["window_trained"] / max(1, st["window_inserted"])
        lines.append(f"Trainer: each recorded move trained on {uses_win:.1f} times lately ({uses_all:.1f} overall); "
                     f"target {S['uses_target']:.0f}. Under 1 means the trainer is falling behind (try fewer workers).")
        dw = st["draw_window"]
        if dw:
            now = sum(dw) / len(dw)
            start = st["draw_start"]
            lines.append(f"Turn-limit draws in training, last {len(dw):,} games: {now:.1%}"
                         + (f" (started at {start:.0%})" if start is not None else "")
                         + f". Tiebreak shaping: {'on' if st['shaping'] else 'off'}.")
        if st["draw_gate"]:
            dg = st["draw_gate"]
            lines.append(f"Draw gate at {S['draw_gate_at']:,} games: {'passed' if dg['passed'] else 'FAILED'} "
                         f"({dg['rate']:.1%}; needed under {S['draw_gate_max']:.0%} and below the start)")
        if st["past_games"]:
            lines.append(f"Training games vs earlier checkpoints: the current networks won "
                         f"{st['past_wins'] / st['past_games']:.0%} of {st['past_games']:,}")
        cps = [c for c in st["checkpoints"] if c.get("decks")]
        if cps:
            lines += ["", "Checkpoints. Each network's margin = its win rate minus k3's own result in the same matchup,",
                      f"averaged over its {plural(len(names) - 1, 'matchup')} ({S['eval_k3_per_matchup']:,} games each, seeds the confirmation never uses).",
                      "'vs previous' = of the games this checkpoint and the one before it decided differently, the share this one",
                      "won (50% = no change). 'vs random' = against uniformly random moves.", ""]
            lines.append(f"  {'checkpoint':<12}" + "".join(f"{n:>22}" for n in names))
            lines.append(f"  {'':<12}" + "".join(f"{'margin  prev random':>22}" for _ in names))
            for c in cps:
                row = f"  {c['name']:<12}"
                for n in names:
                    d = c["decks"][n]
                    row += f"{100 * d['margin']:>+9.1f}{d['vs_prev']['share']:>7.0%}{d['random']:>6.0%}"
                lines.append(row)
            last = cps[-1]
            all_m = {t: m for n in names for t, m in last["decks"][n]["margins"].items()}
            lines += ["", f"Margin by matchup at {last['name']} (points; row = the deck's own network, column = k3's deck):"]
            lines += grid(names, all_m, "{:+.0f}", scale=100)
            lines.append("Best checkpoint per network: " + ", ".join(
                f"{n} {max(cps, key=lambda c: c['decks'][n]['margin'])['name']} "
                f"({100 * max(c['decks'][n]['margin'] for c in cps):+.1f})" for n in names))
            lines.append(f"Leveled off (per network) = {S['level_window']} checkpoints in a row within "
                         f"{100 * S['level_spread']:.0f} points of each other, with the newest winning no more than "
                         f"{S['level_prev_max']:.0%} of the games it and the one before it decided differently. "
                         f"It is re-read at every checkpoint and is not sticky: the run ends when every network "
                         f"is leveled off at the same checkpoint, or at the cap.")
            if st.get("leveled"):
                lines.append("Leveled off so far: " + (", ".join(st["leveled"]) or "none"))
        for cf in st["confirmations"]:
            lines += ["", f"Confirmation of {cf['deck']}'s {cf['name']} (paired with the bars): margin "
                      f"{100 * cf['margin']:+.1f} points over its {plural(len(names) - 1, 'matchup')}; "
                      f"lowest {cf['lowest'][0].replace('>', ' vs ')} {100 * cf['lowest'][1]:+.1f}."]
            lines += [f"    {t.replace('>', ' vs '):<22}{100 * m:>+7.1f}" for t, m in cf["margins"].items()]
        if st.get("verdict"):
            lines += ["", "The pass rules, on each network's best confirmed checkpoint ("
                      + ", ".join(f"{d} {n}" for d, n in st["verdict"]["picks"].items()) + "):"]
            for v in st["verdict"]["criteria"]:
                lines.append(f"  - {v['text']} → {'yes' if v['ok'] else 'NO'}")
            lines.append(f"  → {'PASS' if st['verdict']['pass'] else 'not a pass'}. "
                         f"The audit and held-out results follow in REPORT.txt.")
        if st["flags"]:
            lines += ["", "Flags:"] + [f"  - {f}" for f in st["flags"]]
        nxt = [e for e in self.events() if e[0] > g]
        if st["status"] == "RUNNING" and nxt:
            lines += ["", f"Next: {nxt[0][1]} at {nxt[0][0]:,} games."]
        (self.dir / "STATUS.txt").write_text("\n".join(lines) + "\n")

    def events(self):
        S = self.S
        ev = [(S["draw_gate_at"], "draw gate")] + [(c, "checkpoint") for c in S["checkpoints"]]
        return sorted(ev)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True, help="run folder (created if missing)")
    ap.add_argument("--smoke", action="store_true", help="scaled-down test of every step")
    ap.add_argument("--workers", type=int, default=0, help="number of game-playing processes (default 8)")
    ap.add_argument("--override", default="{}", help="JSON of settings to override (testing only)")
    ap.add_argument("--stop-after", type=int, default=0, help="testing: exit abruptly after N games")
    a = ap.parse_args()
    S = dict(SETTINGS)
    if a.smoke:
        S.update(SMOKE)
    S.update(json.loads(a.override))
    if a.workers:
        S["workers"] = a.workers
    if max([S["budget"]] + S["checkpoints"]) >= EPOCH_SPAN:
        raise SystemExit(f"The game cap must stay under {EPOCH_SPAN:,} so training seeds can't repeat")
    run_dir = Path(a.run)
    if not run_dir.is_absolute():
        run_dir = HERE / run_dir
    for name, rel in list(S["pool"].items()) + list(S["held_out"].items()):
        if not (ROOT / rel).exists():
            raise SystemExit(f"Deck {name}: no such file under the project root: {rel}")
    set_decks(S)
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "run.lock").open("a") as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("This run is already active; no second trainer was started.")
        try:
            execute_run(a, S, run_dir)
        except BaseException:
            state_path = run_dir / "state.json"
            if state_path.exists():
                saved = json.loads(state_path.read_text())
                saved["status"] = "INTERRUPTED"
                saved["reason"] = "run interrupted; rerun the same command to resume the last committed save"
                Run(run_dir, S).write_status(saved)
            raise


def input_identity():
    # keyed by role, so two inputs with the same file name can't hide each other (Astra's review)
    files = {"trainer": Path(__file__).resolve(), "model": HERE / "model.py", "env wrapper": HERE / "pdl_env.py",
             "add-on": addon_path()}
    files.update({f"deck: {n}": Path(p) for n, p in DECKS["paths"].items()})
    files.update({f"held-out: {n}": Path(p) for n, p in DECKS["held_out"].items()})  # used by the report steps
    return {"sha256": {role: hashlib.sha256(p.read_bytes()).hexdigest() for role, p in files.items()},
            "python": sys.version, "numpy": np.__version__}


def execute_run(a, S, run_dir):
    R = Run(run_dir, S)
    identity = input_identity()
    dim = env_dims()
    ctx = mp.get_context("spawn")
    names = list(S["pool"])

    if R.state_path.exists():
        st = json.loads(R.state_path.read_text())
        if st["status"] != "RUNNING":
            print(f"This run already ended: {st['status']} — {st['reason']}. To train again, use a new --run folder.")
            return
        if "resume_stamp" not in st:
            raise RuntimeError("Legacy save lacks a matching weights reference; use a new run folder")
        saved_settings = json.loads((run_dir / "settings.json").read_text())
        changed = [k for k in set(S) | set(saved_settings) if k != "workers"
                   and json.dumps(S.get(k), sort_keys=True) != json.dumps(saved_settings.get(k), sort_keys=True)]
        if changed:
            raise RuntimeError(f"Resume settings changed: {changed}; use the original settings")
        if json.loads((run_dir / "identity.json").read_text()) != identity:
            raise RuntimeError("Run inputs changed; restore the saved inputs before resuming")
        nets = {d: load_net(run_dir / f"resume_{st['resume_stamp']}_{d}.npz", dim, S["lr"]) for d in names}
        st["resume_epoch"] += 1
        R.recover(st)
        st["flags"].append(f"resumed at {st['games']:,} games from the last save ({time.strftime('%Y-%m-%d %H:%M')}); "
                           f"games after that save were lost")
        # Reserve this seed epoch before any actor can start, including repeated crashes.
        R.save_state(st)
        print(f"Resuming at {st['games']:,} games", flush=True)
    else:
        st = R.fresh_state()
        (run_dir / "settings.json").write_text(json.dumps(S, indent=1))
        (run_dir / "identity.json").write_text(json.dumps(identity, indent=1))
        # ordinary starting weights, a different draw per deck, not the zeroed start
        nets = {d: MLP(dim, HIDDEN, seed=k, lr=S["lr"]) for k, d in enumerate(names)}
        for d in names:
            save_net(ckpt_path(run_dir, "ckpt_0", d), nets[d])
        (run_dir / "pool.json").write_text(json.dumps(["ckpt_0"]))
        R.commit(st, nets)
    with ctx.Pool(S["workers"], initializer=_eval_init, initargs=(dim, S, os.getpid())) as eval_pool:

        def log(games, **fields):
            with open(run_dir / "eval_games.jsonl", "a") as f:
                for g in games:
                    f.write(json.dumps(dict(g, **fields)) + "\n")

        def logged(kind, ckpt):
            path = run_dir / "eval_games.jsonl"
            if not path.exists():
                return []
            want = f'"kind": "{kind}"'
            return [g for g in (json.loads(x) for x in path.read_text().splitlines()
                                if want in x and (ckpt is None or f'"ckpt": "{ckpt}"' in x))
                    if g.get("ckpt") == ckpt]

        def margins_of(rates):
            return {t: rates[t]["win_rate"] - st["bars"][t]["win_rate"] for t in rates}

        def tags_of(deck):
            return [f"{deck}>{b}" for a, b in directed(S) if a == deck]

        def evaluate(name):
            """Each network plays its four matchups against k3 on the fixed evaluation seeds, and some games
            against random moves. Improvement is measured against the previous checkpoint on the same seeds."""
            for d in names:
                save_net(ckpt_path(run_dir, name, d), nets[d])
            paths = ckpt_paths(run_dir, name, S)
            rnd = run_games(eval_pool, paths, random_games(S), S["workers"])
            by_deck_random = {d: win_rate_of([g for g in rnd if deck_of(g["tag"]) == d])["win_rate"] for d in names}
            entry = {"name": name, "games": st["games"], "decks": None, "random": by_deck_random}
            if name == "ckpt_0":
                return entry  # the untrained networks aren't scored against k3 (they lose everything)
            k3_games = run_games(eval_pool, paths, checkpoint_k3_games(S), S["workers"])
            log(k3_games, kind="checkpoint", ckpt=name)
            rates = by_tag(k3_games)
            mg = margins_of(rates)
            done = [c for c in st["checkpoints"] if c.get("decks")]
            prev_games = logged("checkpoint", done[-1]["name"]) if done else []
            decks = {}
            for d in names:
                tags = tags_of(d)
                decks[d] = {"margin": sum(mg[t] for t in tags) / len(tags),
                            "margins": {t: mg[t] for t in tags},
                            "rates": {t: rates[t]["win_rate"] for t in tags},
                            "random": by_deck_random[d],
                            "vs_prev": paired_share([g for g in k3_games if deck_of(g["tag"]) == d],
                                                    [g for g in prev_games if deck_of(g["tag"]) == d])}
            entry["decks"] = decks
            entry["avg_margin"] = sum(decks[d]["margin"] for d in names) / len(names)
            return entry

        def scored():
            return [c for c in st["checkpoints"] if c.get("decks")]

        def leveled_off(deck):
            cps = scored()[-S["level_window"]:]
            if len(cps) < S["level_window"]:
                return False
            m = [c["decks"][deck]["margin"] for c in cps]
            # the design: three margins within the spread, and the NEWEST checkpoint beating the one
            # before it on no more than level_prev_max of the games they decide differently (Astra's P2)
            return (max(m) - min(m) <= S["level_spread"] + 1e-9
                    and cps[-1]["decks"][deck]["vs_prev"]["share"] <= S["level_prev_max"] + 1e-9)

        def confirm(deck, name):
            """That network's four matchups on the bars' own seeds, paired with the bar games."""
            games = run_games(eval_pool, ckpt_paths(run_dir, name, S),
                              confirm_games(S, deck), S["workers"], keep_moves=True)
            log(games, kind="confirmation", ckpt=name, deck=deck)
            rates = by_tag(games)
            mg = margins_of(rates)
            bars = logged("bar", None)
            return {"deck": deck, "name": name, "rates": rates, "margins": mg,
                    "margin": sum(mg.values()) / len(mg), "lowest": min(mg.items(), key=lambda kv: kv[1]),
                    "paired": paired(games, bars)}

        def judge(margins):
            """The pass rules, fixed before the run (Fable, Sept 20), judged per matchup."""
            C = S["criteria"]
            out = []
            for tag, need in C["hold"].items():
                m = margins.get(tag)
                out.append({"ok": m is not None and m >= need - 1e-9,
                            "text": f"{tag.replace('>', ' vs ')}: {100 * m:+.1f} points over k3 (needed {100 * need:+.0f})"})
            for tag in C["at_least_k3"]:
                m = margins.get(tag)
                out.append({"ok": m is not None and m >= -1e-9,
                            "text": f"{tag.replace('>', ' vs ')}: {100 * m:+.1f} points over k3 "
                                    f"(needed +0 or better; deeper search barely pays here)"})
            low = min(margins.items(), key=lambda kv: kv[1])
            out.append({"ok": low[1] >= C["no_matchup_below"] - 1e-9,
                        "text": f"every matchup, no more than {-100 * C['no_matchup_below']:.0f} points under k3: "
                                f"lowest is {low[0].replace('>', ' vs ')} at {100 * low[1]:+.1f}"})
            return out

        if st["bars"] is None:
            # k3 piloting both sides of every pairing: the bar for each matchup, on the confirmation seeds
            games = run_games(eval_pool, None, bar_games(S), S["workers"])
            log(games, kind="bar", ckpt=None)
            st["bars"] = bar_rates(games)
            R.commit(st, nets)
            R.write_status(st)
            print("Bars measured: k3 vs k3 in every pairing", flush=True)

        if not st["checkpoints"]:
            st["checkpoints"].append(evaluate("ckpt_0"))
            R.commit(st, nets)
            R.write_status(st)
            print("Checkpoint 0 (the starting networks) evaluated", flush=True)

        events = [e for e in R.events() if e[0] > st["games"]]
        # shared objects for the actors: one weight block and version counter per network
        n_params = flatten(nets[names[0]]).size
        sh = {"weights": {d: ctx.RawArray("f", n_params) for d in names},
              "version": {d: ctx.Value("i", 0, lock=False) for d in names},
              "lock": ctx.Lock(), "pause": ctx.Value("i", 0, lock=False), "stop": ctx.Value("i", 0, lock=False),
              "eps": ctx.Value("d", S["eps_early"] if st["games"] < S["eps_switch"] else S["eps_late"], lock=False),
              "shaping": ctx.Value("i", 1 if st["shaping"] else 0, lock=False),
              "pool_version": ctx.Value("i", 0, lock=False), "claim_lock": ctx.Lock(),
              "issued": ctx.Value("q", st["games"], lock=False),
              "limit": ctx.Value("q", events[0][0] if events else st["games"], lock=False)}
        wbuf = {d: np.frombuffer(sh["weights"][d], dtype=np.float32) for d in names}

        def publish(which=None):
            with sh["lock"]:
                for d in (which or names):
                    wbuf[d][:] = flatten(nets[d])
                    sh["version"][d].value += 1

        publish()
        q = ctx.Queue(maxsize=S["queue_max"])
        actors = []
        base = SEEDS["train"] + st["resume_epoch"] * EPOCH_SPAN
        for w in range(S["workers"]):
            p = ctx.Process(target=actor, args=(w, sh, q, run_dir, S, base, [SEEDS["train"], st["resume_epoch"], w], dim),
                            daemon=True)
            p.start()
            actors.append(p)

        # one replay buffer per network; together they hold as much as run 3's single buffer
        X = {d: np.zeros((S["buffer"], dim), dtype=np.float32) for d in names}
        Y = {d: np.zeros(S["buffer"], dtype=np.float32) for d in names}
        pos = {d: 0 for d in names}
        filled = {d: 0 for d in names}
        credit = {d: 0.0 for d in names}  # buffers are empty after a resume: never repay debt for discarded rows
        pause_epoch = 0
        paused_workers = set()
        rng = np.random.default_rng(12345 + st["resume_epoch"])
        draw_window = collections.deque(st["draw_window"], maxlen=S["draw_window"])
        records = []
        steps = {d: 0 for d in names}   # per network: a global counter published only whichever deck trained on that step (Astra's P1)
        events = [e for e in R.events() if e[0] > st["games"]]
        t_mark, g_mark = time.time(), st["games"]

        def check_actors():
            dead = [p.pid for p in actors if not p.is_alive()]
            if dead:
                raise RuntimeError(f"Training workers exited: {dead}; see actor*_error.txt. Resume the last save.")

        def pause_actors():
            nonlocal pause_epoch
            pause_epoch += 1
            paused_workers.clear()
            sh["pause"].value = pause_epoch
            deadline = time.monotonic() + 120
            while len(paused_workers) != S["workers"]:
                check_actors()
                drain(64)
                if time.monotonic() > deadline:
                    raise RuntimeError("Workers did not finish pausing within 120 seconds")
                time.sleep(0.01)

        def drain(limit):
            got = 0
            while got < limit:
                try:
                    sides, meta = q.get_nowait()
                except queue_mod.Empty:
                    break
                if "paused" in meta:
                    if meta["pause_id"] == pause_epoch:
                        paused_workers.add(meta["paused"])
                    continue
                got += 1
                for deck, Xg, yg in sides:
                    n = len(yg)
                    if not n:
                        continue
                    idx = (np.arange(n) + pos[deck]) % S["buffer"]
                    X[deck][idx], Y[deck][idx] = Xg, yg
                    pos[deck] = (pos[deck] + n) % S["buffer"]
                    filled[deck] = min(S["buffer"], filled[deck] + n)
                    credit[deck] = min(credit[deck] + n * S["uses_target"], filled[deck] * S["uses_target"])
                    st["inserted"] += n
                    st["window_inserted"] += n
                st["games"] += 1
                if meta["type"] == "self":
                    st["selfplay_games"] += 1
                    draw_window.append(1 if meta["cap_draw"] else 0)
                    if st["draw_start"] is None and len(draw_window) == S["draw_window"]:
                        st["draw_start"] = sum(draw_window) / len(draw_window)
                else:
                    st["past_games"] += 1
                    st["past_wins"] += int(meta["net_won"])
                if "record" in meta:
                    records.append(dict(meta["record"], winner=meta["winner"], turns=meta["turns"]))
            return got

        def stop(status, reason):
            st["status"], st["reason"] = status, reason

        def check_draws():
            # at most once per game count: two events at the same boundary share one check (Astra's review)
            if st["draw_checked_at"] == st["games"]:
                return st["last_draw_rate"]
            st["draw_checked_at"] = st["games"]
            rate = sum(draw_window) / max(1, len(draw_window))
            st["last_draw_rate"] = rate
            if rate < S["shaping_off_below"]:
                st["low_draw_checks"] += 1
            else:
                st["low_draw_checks"] = 0
            if st["shaping"] and st["low_draw_checks"] >= 2:
                st["shaping"] = False
                sh["shaping"].value = 0
                st["flags"].append(f"tiebreak shaping switched off at {st['games']:,} games (turn-limit draws under "
                                   f"{S['shaping_off_below']:.0%} at two checks in a row)")
            return rate

        def cap_reached(at):
            return f"safety cap of {S['budget']:,} games reached" if at >= S["budget"] else None

        def finish(why, at):
            """Every network's best checkpoint (and its runner-up within the gap) replays its matchups on the
            bars' seeds; then the pass rules are judged on each network's best confirmed checkpoint."""
            cps = scored()
            picks = {}
            for d in names:
                ranked = sorted(cps, key=lambda c: -c["decks"][d]["margin"])
                top = ranked[0]["decks"][d]["margin"]
                for c in ranked[:2]:
                    if top - c["decks"][d]["margin"] <= S["runner_up_gap"] + 1e-9:
                        st["confirmations"].append(confirm(d, c["name"]))
                        R.write_status(st)
                mine = [cf for cf in st["confirmations"] if cf["deck"] == d]
                best = max(mine, key=lambda cf: cf["margin"])
                picks[d] = best["name"]
            st["confirmed"] = sorted({cf["name"] for cf in st["confirmations"]})
            chosen = {d: next(cf for cf in st["confirmations"] if cf["deck"] == d and cf["name"] == picks[d])
                      for d in names}
            all_margins = {t: m for d in names for t, m in chosen[d]["margins"].items()}
            criteria = judge(all_margins)
            won = all(v["ok"] for v in criteria)
            st["verdict"] = {"picks": picks, "criteria": criteria, "pass": won,
                             "margins": all_margins,
                             "avg_margin": sum(all_margins.values()) / len(all_margins)}
            stop("PASSED" if won else "FINISHED",
                 f"{why} at {at:,} games; best checkpoint per network " +
                 ", ".join(f"{d} {picks[d]} ({100 * chosen[d]['margin']:+.1f})" for d in names) +
                 ("" if won else " — not a pass") +
                 ". The report steps (audit, held-out test, REPORT.txt) run next, automatically")

        try:
            while events and st["status"] == "RUNNING":
                check_actors()
                got = drain(64)
                trained_now = 0
                while trained_now < 8:
                    ready = [d for d in names if filled[d] >= S["min_buffer"] and credit[d] >= S["batch"]]
                    if not ready:
                        break
                    d = max(ready, key=lambda d: credit[d])
                    idx = rng.integers(filled[d], size=S["batch"])
                    loss = nets[d].train_step(X[d][idx], Y[d][idx])
                    if not np.isfinite(loss):
                        raise RuntimeError(f"Non-finite training loss ({d}); resume from the last save")
                    credit[d] -= S["batch"]
                    st["trained"] += S["batch"]
                    st["window_trained"] += S["batch"]
                    trained_now += 1
                    steps[d] += 1
                    if steps[d] % S["publish_every"] == 0:
                        publish([d])   # this network's own interval, so every network that trains reaches the workers
                if not got and not trained_now:
                    time.sleep(0.002)
                if st["games"] >= S["eps_switch"] and sh["eps"].value != S["eps_late"]:
                    sh["eps"].value = S["eps_late"]
                if a.stop_after and st["games"] >= a.stop_after:  # simulates a crash: nothing saved
                    print("test: abrupt exit", flush=True)
                    sh["stop"].value = 1
                    eval_pool.terminate()
                    os._exit(3)
                if st["games"] < events[0][0]:
                    continue
                # Every event at this game count is handled together and saved in ONE commit, so an
                # interruption can't leave one of them done and the other skipped on resume (Astra's review).
                at = events[0][0]
                batch = sorted((k for g_, k in events if g_ == at), key=lambda k: k != "draw gate")
                events = [e for e in events if e[0] != at]
                pause_actors()
                now = time.time()
                st["elapsed_train_s"] += now - t_mark
                st["rate_games_per_sec"] = (st["games"] - g_mark) / max(1e-9, now - t_mark)
                st["draw_window"] = list(draw_window)
                for kind in batch:
                    if st["status"] != "RUNNING":
                        break
                    if kind == "draw gate":
                        rate = check_draws()
                        start = st["draw_start"] if st["draw_start"] is not None else 1.0
                        ok = rate < S["draw_gate_max"] and rate < start
                        st["draw_gate"] = {"games": st["games"], "rate": rate, "passed": ok}
                        if not ok:
                            stop("STOPPED", f"draw gate failed at {st['games']:,} games: turn-limit draws {rate:.0%} "
                                            f"(needed under {S['draw_gate_max']:.0%} and below the start)")
                    else:
                        publish()
                        name = f"ckpt_{at // 1000}k"
                        entry = evaluate(name)
                        st["checkpoints"].append(entry)
                        check_draws()
                        # floors, per network, from run 3's own curve (insurance, not a judgement)
                        for at_games, floor in S["floors"]:
                            if at != at_games:
                                continue
                            curve = RUN3_CURVE.get(at_games) or RUN3_CURVE[min(RUN3_CURVE)]
                            low = []
                            for d in names:
                                got_m, got_r = entry["decks"][d]["margin"], entry["decks"][d]["random"]
                                if "below_run3" in floor and got_m < curve[d] - floor["below_run3"] - 1e-9:
                                    low.append(f"{d} {100 * got_m:+.1f} (run 3 had {100 * curve[d]:+.1f}, "
                                               f"floor {100 * (curve[d] - floor['below_run3']):+.1f})")
                                if "random" in floor and got_r < floor["random"] - 1e-9:
                                    low.append(f"{d} vs random {got_r:.0%} (needed {floor['random']:.0%})")
                            if low:
                                stop("STOPPED", f"floor missed at {at:,} games: " + "; ".join(low))
                        if st["status"] == "RUNNING":
                            st["leveled"] = [d for d in names if leveled_off(d)]
                            why = "every network leveled off" if len(st["leveled"]) == len(names) else cap_reached(at)
                            if why:
                                finish(why, at)
                        pool_names = [c["name"] for c in st["checkpoints"]]
                        (run_dir / "pool.json").write_text(json.dumps(pool_names))
                        sh["pool_version"].value += 1
                st["elapsed_eval_s"] += time.time() - now
                st["uses_lately"] = st["window_trained"] / max(1, st["window_inserted"])
                st["window_inserted"] = st["window_trained"] = 0
                if records:
                    with open(run_dir / "selfplay_samples.jsonl", "a") as f:
                        for r in records:
                            f.write(json.dumps(r) + "\n")
                    records.clear()
                R.commit(st, nets)
                R.write_status(st)
                print(f"{' + '.join(batch)} at {st['games']:,} games — {st['status']}", flush=True)
                t_mark, g_mark = time.time(), st["games"]
                with sh["claim_lock"]:
                    sh["limit"].value = events[0][0] if events and st["status"] == "RUNNING" else st["games"]
                sh["pause"].value = 0
        finally:
            sh["stop"].value = 1
            sh["pause"].value = 0
            for p in actors:
                p.join(timeout=5)
                if p.is_alive():
                    p.terminate()
                    p.join(timeout=5)
            q.close()
            eval_pool.terminate()
            eval_pool.join()
        print((run_dir / "STATUS.txt").read_text())


if __name__ == "__main__":
    main()

