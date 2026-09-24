"""Diagnostic: first deck's win % over paired seeds, both seats. Not for any ranking."""
import os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
REPO = str(__import__("pathlib").Path(__file__).resolve().parents[3])  # the repo root
def run(eng, d0, d1, n, seed, env):
    p = subprocess.run([eng, "simulate", "--num", str(n), "--seed", str(seed), "--seed-stream", "--players", "k3,k3",
                        f"{REPO}/decks/research/{d0}.txt", f"{REPO}/decks/research/{d1}.txt"],
                       capture_output=True, text=True, env={**os.environ, **env})
    o = p.stdout + p.stderr
    return int(re.search(r"Player 0 won: (\d+)", o)[1]), int(re.search(r"Player 1 won: (\d+)", o)[1]), int(re.search(r"Draws: (\d+)", o)[1])
def cell(eng, a, b, n, base, env):
    h = n // 2
    w0, l0, d0 = run(eng, a, b, h, base, env)          # a in seat 0
    l1, w1, d1 = run(eng, b, a, n - h, base + 5000, env)  # a in seat 1
    return 100 * (w0 + w1 + 0.5 * (d0 + d1)) / n
if __name__ == "__main__":
    eng, n, envs = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    env = dict(kv.split("=") for kv in envs.split(",") if kv)
    pairs = [p.split(":") for p in sys.argv[4:]]
    with ThreadPoolExecutor(4) as ex:
        res = list(ex.map(lambda ab: cell(eng, ab[0], ab[1], n, 81_000_000 + 10_000 * pairs.index(ab), env), pairs))
    for (a, b), r in zip(pairs, res): print(f"{a} v {b}: {r:.1f}")
