"""Lucario analyst: load both dumps for the lucario-selected seeds, split repeated seeds into separate games
(a seed selected for two decks was traced twice; games appear in sorted (pairing, config) order), and cache."""
import json, os, re, pickle
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
LINE = re.compile(r"DUMP2 (\d+) (\d+) t(\d+) p(\d) (\d) :: (.*?) \|\| (.*) \|\| (.*)$")
sel = json.load(open(os.path.join(D, "selected.json"), encoding="utf-8"))
want = {g["seed"] for g in sel if g["deck"] == "lucario"}


def load(name):
    g = defaultdict(list)  # seed -> list of games (list of moves)
    last = {}
    for line in open(os.path.join(D, name), encoding="utf-8"):
        if not line.startswith("DUMP2 "):
            continue
        sp = line.split(" ", 2)
        seed = int(sp[1])
        if seed not in want:
            continue
        m = LINE.match(line.rstrip("\n"))
        if not m:
            continue
        seed, tick, turn, tomove, actor, act, s0, s1 = m.groups()
        seed, tick = int(seed), int(tick)
        if seed not in last or tick <= last[seed]:
            g[seed].append([])
        last[seed] = tick
        g[seed][-1].append({"tick": tick, "turn": int(turn), "tomove": int(tomove), "actor": int(actor), "act": act, "s": [s0, s1]})
    return dict(g)


base, kpf = load("dump_base.txt"), load("dump_kpf.txt")
# which occurrence belongs to the lucario record: order of runs = sorted (pairing, config)
order = defaultdict(list)
for g in sel:
    order[g["seed"]].append((g["pairing"], g["config"], g["deck"]))
idx = {}
for s in want:
    runs = sorted(order[s])
    idx[s] = [r[2] for r in runs].index("lucario")
games = {}
for g in sel:
    if g["deck"] != "lucario":
        continue
    s = g["seed"]
    i = idx[s]
    nb, nk = len(base.get(s, [])), len(kpf.get(s, []))
    games[s] = {"meta": g, "base": base[s][min(i, nb - 1)], "kpf": kpf[s][i], "nb": nb, "nk": nk, "occ": i}
print("games", len(games), "multi-run seeds", sum(1 for v in games.values() if v["nk"] > 1),
      "lucario is 2nd run", sum(1 for v in games.values() if v["occ"] == 1))
pickle.dump(games, open(os.path.join(HERE, "luc_games.pkl"), "wb"))
