#!/usr/bin/env python3
"""Independent point estimates of tau, dMSE, cell and deck vetoes (no import of score.py), plus kob/kor identity decks."""
import json, math, random
from collections import Counter, defaultdict

R = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
RD = f"{R}/rl/results/koa_2026-09-26/reading"
KPF = f"{R}/rl/results/kpf_2026-09-26/reading"
L = {tuple(k.split("|")): v for k, v in json.load(open(f"{R}/rl/results/scoreboard_v2_2026-09-25/limitless_v2_dev.json"))["cells"].items()}


def load(p):
    return {(g["pairing"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}


O, N = load(f"{KPF}/table_kp3.jsonl"), load(f"{RD}/table_koa3.jsonl")
cells = defaultdict(list)
for k in O:
    cells[(O[k]["a"], O[k]["b"])].append(k)
missing = [c for c in cells if c not in L]
print("table cells without a Limitless cell:", missing)


def stats(keys, T):
    S = {c: sum(T[k]["first_deck_score"] for k in cells[c]) / len(cells[c]) for c in keys}
    return S


def lim(c):
    w, l, t = L[c]; n = w + l + t
    return (w + 0.5 * t) / n, n


def tau(S, keys):
    acc = 0
    for c in keys:
        l, nl = lim(c); s = S[c]; ns = len(cells[c])
        acc += (s - l) ** 2 - l * (1 - l) / nl - s * (1 - s) / ns
    return 100 * math.sqrt(max(0, acc / len(keys)))


def mse(S, keys):
    return sum((100 * (S[c] - lim(c)[0])) ** 2 for c in keys) / len(keys)


for label, keys in (("all 28", sorted(cells)), ("decision 27", [c for c in sorted(cells) if c != ("altaria", "sceptile")])):
    So, Sn = stats(keys, O), stats(keys, N)
    to, tn = tau(So, keys), tau(Sn, keys)
    print(f"{label}: tau kp3 {to:.3f}, koa3 {tn:.3f}, margin (kp3 - koa3) {to - tn:+.3f}; dMSE {mse(Sn, keys) - mse(So, keys):+.2f}")
    cv = [(c, 100 * (abs(Sn[c] - lim(c)[0]) - abs(So[c] - lim(c)[0]))) for c in keys]
    print("   largest cell miss growth:", max(cv, key=lambda x: x[1]), "-> cell veto" if max(x[1] for x in cv) > 6 else "-> none > 6")
    dk = defaultdict(lambda: [[], [], []])
    for c in keys:
        a, b = c; l = lim(c)[0]
        for d, s0, s1, ll in ((a, So[c], Sn[c], l), (b, 1 - So[c], 1 - Sn[c], 1 - l)):
            dk[d][0].append(s0); dk[d][1].append(s1); dk[d][2].append(ll)
    gg = {d: 100 * (abs(sum(v[1]) / len(v[1]) - sum(v[2]) / len(v[2])) - abs(sum(v[0]) / len(v[0]) - sum(v[2]) / len(v[2]))) for d, v in dk.items()}
    print("   deck gap growth:", {d: round(x, 2) for d, x in sorted(gg.items())}, "-> deck veto" if max(gg.values()) > 2 else "-> none > 2")
    # own paired bootstrap of the tau margin (sim side by deal, Limitless side binomial), 2000 reps, own seed
    rng = random.Random(20000000001)
    marg = []
    for _ in range(2000):
        acc_o = acc_n = 0
        for c in keys:
            ks = cells[c]; n = len(ks)
            idx = [ks[rng.randrange(n)] for _ in range(n)]
            so = sum(O[k]["first_deck_score"] for k in idx) / n
            sn = sum(N[k]["first_deck_score"] for k in idx) / n
            l0, nl = lim(c)
            lb = sum(1 for _ in range(nl) if rng.random() < l0) / nl
            for which, s in (("o", so), ("n", sn)):
                v = (s - lb) ** 2 - lb * (1 - lb) / nl - s * (1 - s) / n
                if which == "o":
                    acc_o += v
                else:
                    acc_n += v
        marg.append(100 * (math.sqrt(max(0, acc_o / len(keys))) - math.sqrt(max(0, acc_n / len(keys)))))
    marg.sort()
    print(f"   own bootstrap of the tau margin (2000 reps, ties counted half in the table scores; Limitless W/L/T drawn as a binomial on the score): 90% {marg[100]:+.2f} to {marg[1899]:+.2f}")

# kob/kor diagnostics: identity decks
for b, idd in (("kob3", {"blaziken", "lucario", "sceptile", "suicune"}), ("kor3", {"blaziken", "lucario", "sceptile", "hydreigon"})):
    Y = load(f"{RD}/mixed_{b}_second.jsonl")
    diff = [k for k in Y if Y[k]["moves"] != O[k]["moves"]]
    by = Counter(Y[k]["b"] for k in diff)
    opch = Counter(Y[k]["b"] for k in diff if Y[k]["openings"][1] != O[k]["openings"][1])
    leak = [k for k in diff if Y[k]["openings"] == O[k]["openings"]]
    print(f"{b} on Altaria's opponents: differing games by opponent {dict(by)}; with the opponent's opening changed {dict(opch)}; leaks {len(leak)}; identity decks touched: {sorted(set(by) & idd)}")
