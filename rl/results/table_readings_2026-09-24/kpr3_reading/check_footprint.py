"""Second reader: the footprint numbers in kpr3_paired_reading.md, section 3 (own code).
A game 'changes' when its move fingerprint ('moves') differs from kp3's on the same deal; its result changes when the
first deck's score differs (also shown: winner seat or points differ)."""
from check_common import PAIRS, NAMES, KP3, KPR3, K3, MIX1, MIX2, load, score

kp3 = load(KP3, ("kp3", "kp3"))
kpr3 = load(KPR3, ("kpr3", "kpr3"))
k3 = load(K3, ("k3", "k3"))
m1 = load(MIX1, ("kpr3", "kp3"))
m2 = load(MIX2, ("kp3", "kpr3"))


def comp(other, keys, base=kp3):
    mv = sc = wp = 0
    n = 0
    for k in keys:
        for i in range(500):
            a, b = base[k][i], other[k][i]
            n += 1
            mv += a["moves"] != b["moves"]
            sc += score(a) != score(b)
            wp += (a["winner_seat"], a["points"]) != (b["winner_seat"], b["points"])
    return n, mv, sc, wp


n, mv, sc, wp = comp(kpr3, PAIRS)
print(f"kpr3 table vs kp3: moves differ {mv:,} of {n:,} ({100 * mv / n:.1f}%); identical {n - mv:,}; "
      f"score differs {sc:,} ({100 * sc / n:.1f}%); winner or points differ {wp:,}")
n, mv, sc, wp = comp(k3, PAIRS)
print(f"k3 table vs kp3: identical {n - mv:,} of {n:,}; moves differ {mv:,}")
per = sorted((comp(kpr3, [k])[1], k) for k in PAIRS)
print(f"least-changed cell {per[0][1]} {per[0][0]} of 500; most-changed {per[-1][1]} {per[-1][0]} of 500")
print(f"  next least {per[1]}, next most {per[-2]}")
print("kpr3 on one deck only (mixed rows), that deck's 3,500 games:")
tot_mv = tot_n = 0
for d in NAMES:
    n = mv = sc = 0
    for k in PAIRS:
        if d not in k:
            continue
        t = m1 if k[0] == d else m2
        a, b, c, _ = comp(t, [k])
        n += a; mv += b; sc += c
    tot_mv += mv; tot_n += n
    print(f"  {d:>9}: moves differ {mv:,} of {n:,} ({100 * mv / n:.1f}%), score differs {sc} ({100 * sc / n:.1f}%)")
print(f"all mixed games: moves differ {tot_mv:,} of {tot_n:,}")
