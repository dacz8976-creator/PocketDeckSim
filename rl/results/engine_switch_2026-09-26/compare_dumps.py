"""For each unexplained game, the first tick where 5b75bf9 and 5bab907 choose differently, with the board just before
it (identical in both, up to that point) and each engine's next few choices. Usage: python3 compare_dumps.py"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
un = json.load(open(os.path.join(HERE, "unexplained.json")))
LINE = re.compile(r"DUMP (\d+) (\d+) (t\d+ p\d \d) :: (.*?) \|\| (.*) \|\| (.*)$")


def load(path):
    games = {}
    for line in open(path, encoding="utf-8"):
        m = LINE.match(line.strip())
        if m:
            seed, tick, who, act, s0, s1 = m.groups()
            games.setdefault(int(seed), []).append((who, act, s0, s1))
    return games


for bot in ("k3", "kp3"):
    a, b = (load(os.path.join(HERE, f"dump_{c}_{bot}.txt")) for c in ("5b75bf9", "5bab907"))
    print(f"===== {bot}: {len(un[bot])} games")
    for p, i, seed in un[bot]:
        x, y = a.get(seed, []), b.get(seed, [])
        k = next((n for n in range(min(len(x), len(y))) if x[n][:2] != y[n][:2]), None)
        if k is None:
            print(f"-- pairing {p} deal {i} seed {seed}: no divergence found in the dumps ({len(x)} v {len(y)} ticks)")
            continue
        who, _, s0, s1 = x[k]
        print(f"-- pairing {p} deal {i} seed {seed}: first divergence at tick {k + 1} ({who})")
        print(f"   board: seat0 {s0}")
        print(f"          seat1 {s1}")
        for tag, g in (("before fix", x), ("with fix", y)):
            print(f"   {tag}: " + " -> ".join(f"{g[n][0].split()[0]}/{g[n][0].split()[2]} {g[n][1][:70]}" for n in range(k, min(k + 4, len(g)))))
