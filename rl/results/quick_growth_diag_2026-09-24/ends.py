import re, subprocess, sys, collections
eng = str(__import__("pathlib").Path(__file__).resolve().parents[3] / "engine/target/release/deckgym")
def run(d0, d1, n, seed):
    p = subprocess.run([eng, "simulate", "--num", str(n), "--seed", str(seed), "--seed-stream", "--players", "k3,k3",
                        d0, d1, "-vvv"], capture_output=True, text=True)
    games, cur = [], None
    for line in (p.stdout + p.stderr).splitlines():
        if line.startswith("Playing game with seed"):
            cur = {"kos": [], "pts": [0, 0]}; games.append(cur)
        elif (m := re.match(r"Pokemon (.+?)\(\d+hp,\d+\) fainted\. Player (\d) won (\d) points for a total of (\d)", line)):
            cur["kos"].append((m[1], int(m[2]), int(m[3]))); cur["pts"][int(m[2])] = int(m[4])
        elif (m := re.search(r"Winner is Some\(Win\((\d)\)\)", line)):
            cur["winner"] = int(m[1])
        elif "Winner is" in line:
            cur["winner"] = None
        elif (m := re.search(r"Average number of turns", line)):
            pass
    return games
A, B = sys.argv[1], sys.argv[2]; n = int(sys.argv[3])
names = {A: A.split("/")[-1][:-4], B: B.split("/")[-1][:-4]}
tally = collections.Counter(); kos = collections.Counter(); n_games = 0
for d0, d1, seed in ((A, B, 72230000), (B, A, 72230500)):
    for g in run(d0, d1, n, seed):
        n_games += 1
        seat = {0: names[d0], 1: names[d1]}
        w = g.get("winner")
        if w is None: tally["draw/none"] += 1; continue
        how = "3+ points" if g["pts"][w] >= 3 else "opponent out of Pokemon"
        tally[(seat[w], how)] += 1
        for poke, taker, p in g["kos"]:
            kos[(seat[1 - taker], poke)] += 1
print(f"{n_games} games")
for k, v in sorted(tally.items(), key=lambda x: -x[1]): print(f"  {v:4d}  {k}")
print("Knockouts suffered (deck, Pokemon): count")
for k, v in sorted(kos.items(), key=lambda x: -x[1]): print(f"  {v:4d}  {k}")
