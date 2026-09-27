"""One line per unexplained game: the first divergence's turn, the deck ending the turn, and every Active on that board
with its HP and status, plus whether a Checkup Knock Out is reachable this turn by the plain rule: an Active that is
Poisoned (10 a Checkup) or Burned (20) with HP at most its Checkup damage + 30 (one attack's worth), or any Active at
30 HP or less while the Poison deck (Team Rocket's Weezing ex / Koffing / Deceptive Needle) is on the board.
Usage: python3 summarize_divergences.py > divergences.txt"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
un = json.load(open(os.path.join(HERE, "unexplained.json")))
LINE = re.compile(r"DUMP (\d+) (\d+) (t\d+ p\d \d) :: (.*?) \|\| (.*) \|\| (.*)$")
ACT = re.compile(r"\[(.+?) (\d+)hp((?: [A-Z]{3})*) \|")


def load(path):
    g = {}
    for line in open(path, encoding="utf-8"):
        m = LINE.match(line.strip())
        if m:
            g.setdefault(int(m.group(1)), []).append(m.groups()[2:])
    return g


total, reachable = 0, 0
for bot in ("k3", "kp3"):
    a, b = (load(os.path.join(HERE, f"dump_{c}_{bot}.txt")) for c in ("5b75bf9", "5bab907"))
    for p, i, seed in un[bot]:
        x, y = a.get(seed, []), b.get(seed, [])
        k = next((n for n in range(min(len(x), len(y))) if x[n][:2] != y[n][:2]), None)
        total += 1
        if k is None:
            print(f"{bot} p{p} d{i}: no divergence in the dumps ({len(x)} v {len(y)} ticks)")
            continue
        who, _, s0, s1 = x[k]
        weezing = "Weezing" in s0 + s1 or "Koffing" in s0 + s1
        acts, why = [], []
        for s in (s0, s1):
            m = ACT.search(s)
            if not m:
                continue
            name, hp, st = m.group(1), int(m.group(2)), m.group(3).split()
            acts.append(f"{name} {hp}{'/' + '+'.join(st) if st else ''}")
            dmg = 10 * ("PSN" in st) + 20 * ("BRN" in st)
            if (dmg and hp <= dmg + 30) or (weezing and hp <= 30):
                why.append(name)
        ok = bool(why)
        reachable += ok
        print(f"{bot} p{p} d{i} {who.split()[0]}: {'; '.join(acts)}{' [Poison deck]' if weezing else ''} -> "
              f"{'Checkup KO reachable (' + ', '.join(why) + ')' if ok else 'NOT obviously reachable'}")
print(f"\n{reachable} of {total} unexplained games have a Checkup Knock Out reachable in the turn where they diverge")
