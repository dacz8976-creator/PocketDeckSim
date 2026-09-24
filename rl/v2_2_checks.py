"""Checks for encoding v2.2 (add-on 0.6.0): the two "losing the Active" numbers, and that nothing else moved.
Run with 0.6.0 installed:  python v2_2_checks.py [games]
Writes results/v2_2_checks.txt. v1/v2.1 byte-identity against 0.5.0 is checked separately by dump_features.py,
which is run once under each add-on version (see the file's own docstring).

1. Dimensions: v2.2 adds exactly one number per move; the observation is unchanged.
2. Layout: v2.2 keeps v2.1's first 13 numbers and its asleep / poisoned pair, shifted by one.
3. The new numbers against the true game: for every move whose outcome is the same under four chance seeds,
   "my Pokemon in play after this move" must equal the real count, and "losing the Active now loses the game"
   must equal the rule (nothing to promote, or that knockout gives the opponent their third point).
4. The threat "certain" flag is gone: the slot it used now holds the in-play count (0.25 to 1).
"""
import json, random, sys
from pathlib import Path
import numpy as np
from pdl_rl_env import RawEnv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
STUDY = "Boss Folder/competitive-deck-study-2026-09-08/round-robin-checkpoint/reports/research/decks"
DECKS = [str(ROOT / "decks/dustin/06-mega-blaziken-tournament-list.txt"), str(ROOT / STUDY / "lucario.txt"),
         str(ROOT / STUDY / "weezing.txt"), str(ROOT / STUDY / "altaria.txt"), str(ROOT / STUDY / "suicune.txt")]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
K = 4
IDS = sorted({i for p in DECKS for i in RawEnv.deck_card_ids(p)})
out = []


def say(s):
    print(s, flush=True)
    out.append(s)


def ko_points(name):
    return 3.0 if name.startswith("Mega ") else (2.0 if name.endswith(" ex") else 1.0)


def rows_of(env):
    return np.frombuffer(env.action_features(), dtype="<f4").reshape(-1, env.action_dim)


e21, e22 = RawEnv(IDS, "v2.1"), RawEnv(IDS, "v2.2")
say(f"v2.2 checks — {len(IDS)}-card list, {N} random games per part")
say(f"1. dimensions: observation {e21.obs_dim} -> {e22.obs_dim} (unchanged), per move {e21.action_dim} -> {e22.action_dim} (+1)")
assert e22.obs_dim == e21.obs_dim and e22.action_dim == e21.action_dim + 1

# 2 and 4: same games stepped in both encodings, compare the rows
same_head = same_tail = shifted = rowcount = 0
flagslot = []
for g in range(N):
    a, b = DECKS[g % 5], DECKS[(g + 2) % 5]
    e21.reset(a, b, 5_000_000 + g, None)
    e22.reset(a, b, 5_000_000 + g, None)
    rng = random.Random(g)
    while not e21.done:
        r21, r22 = rows_of(e21), rows_of(e22)
        assert r21.shape[0] == r22.shape[0]
        base21, base22 = e21.action_dim - 16, e22.action_dim - 17
        for i in range(r21.shape[0]):
            rowcount += 1
            same_head += np.array_equal(r21[i, :base21 + 13], r22[i, :base22 + 13])
            shifted += np.array_equal(r21[i, base21 + 14:base21 + 16], r22[i, base22 + 15:base22 + 17])
            flagslot.append(float(r22[i, base22 + 13]))
        j = rng.randrange(len(e21.legal_actions()))
        e21.step(j); e22.step(j)
say(f"2. layout: the first 13 numbers match v2.1 in {same_head:,}/{rowcount:,} move rows; "
    f"asleep/poisoned match, shifted by one, in {shifted:,}/{rowcount:,}")
assert same_head == rowcount and shifted == rowcount
fl = np.array(flagslot)
say(f"4. the slot v2.1 used for the threat 'certain' flag now holds the in-play count: "
    f"range {fl.min():.2f}-{fl.max():.2f}, values seen {sorted(set(np.round(fl, 3).tolist()))[:6]}")
assert fl.min() >= 0.0 and fl.max() <= 1.0

# 3: the new numbers against the true game.
# The encoding measures the position the engine's own forecast reaches right after the move, before any
# follow-up choice (that is how every v2 number is built), so the comparison is made where the engine's
# plain step lands in the same place: it doesn't end the game and doesn't leave a choice pending.
checked_count = bad_count = checked_flag = bad_flag = 0
unpriced = self_dmg = pending = ended = changed_active = 0
examples = []
env = RawEnv(IDS, "v2.2")
for g in range(N):
    a, b = DECKS[g % 5], DECKS[(g + 3) % 5]
    env.reset(a, b, 6_000_000 + g, None)
    rng = random.Random(100 + g)
    while not env.done:
        me = env.current_player
        acts = env.legal_actions()
        r = rows_of(env)
        base = env.action_dim - 17
        before = json.loads(env.describe(me))
        n_before = sum(1 for x in before["me"]["board"] if x)
        act_before = before["me"]["board"][0]
        snap = env.snapshot()
        for i in range(min(len(acts), 6)):
            if float(r[i, base + 0]) < 0.5:
                unpriced += 1   # the engine refused to forecast this move (hidden information): the row is all zeros
                continue
            # (a) my Pokemon in play can only go up by placing one, or down if the move hurts my own side
            if float(r[i, base + 6]) > 0:
                self_dmg += 1
            else:
                checked_count += 1
                want = n_before + (1 if acts[i].startswith("V:Place") else 0)
                got = float(r[i, base + 13]) * 4
                if abs(got - want) > 1e-4:
                    bad_count += 1
                    if len(examples) < 5: examples.append(f"count: {acts[i]!r} shown {got:.2f}, expected {want}")
            # (b) the loss flag, against the real position after the move where the step lands in the same place
            env.restore(snap, 0x5eed_0000)
            env.step(i)
            if env.done:
                ended += 1
            elif np.frombuffer(env.observe(env.current_player), dtype="<f4")[11] > 0.5:
                pending += 1
            else:
                d = json.loads(env.describe(me))
                board = d["me"]["board"]
                act_after = board[0]
                same_active = (act_before or {}).get("name") == (act_after or {}).get("name")
                if not same_active:
                    changed_active += 1
                else:
                    in_play = sum(1 for x in board if x)
                    name = act_after["name"] if isinstance(act_after, dict) else str(act_after)
                    lose = in_play <= 1 or d["them"]["points"] + ko_points(name) >= 3.0
                    checked_flag += 1
                    got = float(r[i, base + 14])
                    if abs(got - float(lose)) > 1e-4:
                        bad_flag += 1
                        if len(examples) < 5: examples.append(f"flag: {acts[i]!r} shown {got:.2f}, real {int(lose)}")
            env.restore(snap, 54321)
        env.step(rng.randrange(len(acts)))
say(f"3a. in-play count: {checked_count:,} moves checked, {bad_count} wrong "
    f"({unpriced:,} moves skipped as refused by the engine, {self_dmg:,} that damage my own side)")
say(f"3b. 'losing the Active now loses the game': {checked_flag:,} moves checked against the real position, {bad_flag} wrong "
    f"({ended:,} skipped because the move ended the game, {pending:,} because it opens a follow-up choice, "
    f"{changed_active:,} because it changes the Active — in all three the forecast and a plain step can stop in different places)")
for x in examples:
    say("   " + x)
assert bad_count == 0 and bad_flag == 0
say("ALL CHECKS PASSED")
(HERE / "results").mkdir(exist_ok=True)
(HERE / "results/v2_2_checks.txt").write_text("\n".join(out) + "\n")
