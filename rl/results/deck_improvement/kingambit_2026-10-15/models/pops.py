"""Hits to knock out a wall from full HP, with one heal of H between the first and second hit (Lucky Ice Pop plays:
20 per play; on heads the Pop returns and can be played again, so 1 Pop heals 20 x Geometric(1/2) -> 40 on average).
Heavy Helmet: -20 per hit on retreat 3+ (Regigigas, Muk, Kingambit)."""
walls = [('Glimmet', 60, 0), ('Glimmora', 90, 0), ('Alolan Muk', 110, 0), ('Muk+Helmet', 110, 20),
         ('Regigigas', 150, 0), ('Regigigas+Helmet', 150, 20)]
def hits(hp, d, heal, red):
    d = max(0, d - red)
    if d == 0:
        return 99
    k, cur = 0, hp
    while True:
        cur -= d; k += 1
        if cur <= 0:
            return k
        if k == 1:
            cur = min(hp, cur + heal)
for w, hp, red in walls:
    out = []
    for H in (20, 40, 60):
        gains = [d for d in range(30, 160, 10) if hits(hp, d, H, red) > hits(hp, d, 0, red)]
        out.append(f"H={H}: {gains}")
    print(f"{w:18s}", ' | '.join(out))
# probability that 1 Pop / 2 Pops heal at least 40 / 60 in one turn (enough damage to heal assumed)
import itertools
def dist(npops):
    # each Pop: plays until tails; total plays = sum of geometrics
    from collections import Counter
    c = Counter({0: 1.0})
    for _ in range(npops):
        n = Counter()
        for k, p in c.items():
            for g in range(1, 12):
                n[k + g] += p * (0.5 ** g)
        c = n
    return c
for npops in (1, 2):
    c = dist(npops)
    print(npops, 'Pop(s): P(heal>=40)=%.2f P(heal>=60)=%.2f mean heal=%.0f' % (
        sum(p for k, p in c.items() if 20 * k >= 40), sum(p for k, p in c.items() if 20 * k >= 60), sum(20 * k * p for k, p in c.items())))
