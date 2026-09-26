"""Attribution for the B2e Manectric and Raticate archetype pairings (descriptive only).
Per pairing and pooled per held deck, the held deck's score (first_deck_score; the held deck is the first-named 'a'):
  own side  = (kp3 held | k3 panel) - (k3 | k3)      what kp3 piloting the held deck adds
  opponents = (k3 held | kp3 panel) - (k3 | k3)      what kp3 piloting its opponents takes (negative = they got better)
  both      = (kp3 | kp3) - (k3 | k3)                the B2e table change
  interaction = both - own - opponents
Paired by deal (seed); 95% = 1.96 x sd of per-deal differences / sqrt(n); pooled per deck = mean over its 8 cells
(equal weight), sd combined as sqrt(sum var)/8."""
import json, math, os, collections
E = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/b2e_rows_2026-09-26"
D = os.path.dirname(os.path.abspath(__file__))


def load(path, pairs):
    out = {}
    for line in open(path):
        g = json.loads(line)
        if g["pairing"] in pairs:
            out[(g["pairing"], g["seed"])] = g
    return out


PAIRS = set(range(16))
kk = load(f"{E}/b2e_k3_arch.jsonl", PAIRS)
pp = load(f"{E}/b2e_kp3_arch.jsonl", PAIRS)
pk = load(f"{D}/mixed_first.jsonl", PAIRS)
kp = load(f"{D}/mixed_second.jsonl", PAIRS)
for name, d in (("k3|k3", kk), ("kp3|kp3", pp), ("kp3|k3", pk), ("k3|kp3", kp)):
    assert len(d) == 16 * 500, (name, len(d))
for g in pk.values():
    assert g["bot_a"] == "kp3" and g["bot_b"] == "k3", g
for g in kp.values():
    assert g["bot_a"] == "k3" and g["bot_b"] == "kp3", g
keys = sorted(kk)
assert set(keys) == set(pp) == set(pk) == set(kp)
sc = lambda g: float(g["first_deck_score"])


def stat(diffs):
    n = len(diffs); m = sum(diffs) / n
    var = sum((x - m) ** 2 for x in diffs) / (n - 1)
    return 100 * m, var / n


rows = collections.defaultdict(dict)
names = {}
for p in range(16):
    ks = [k for k in keys if k[0] == p]
    names[p] = (kk[ks[0]]["a"], kk[ks[0]]["b"])
    for lab, other in (("own", pk), ("opp", kp), ("both", pp)):
        rows[p][lab] = stat([sc(other[k]) - sc(kk[k]) for k in ks])
    rows[p]["inter"] = stat([sc(pp[k]) - sc(pk[k]) - sc(kp[k]) + sc(kk[k]) for k in ks])
    rows[p]["base"] = 100 * sum(sc(kk[k]) for k in ks) / len(ks)
print(__doc__)
print(f"{'pairing':>7} {'held':>12} {'panel':>10} {'k3|k3':>6} {'own (kp3 on held)':>20} {'opponents (kp3 on panel)':>26} {'both':>16} {'interaction':>16}")
fmt = lambda t: f"{t[0]:+6.1f} ± {100 * 1.96 * math.sqrt(t[1]):4.1f}"
for p in range(16):
    r = rows[p]
    print(f"{p:>7} {names[p][0]:>12} {names[p][1]:>10} {r['base']:6.1f} {fmt(r['own']):>20} {fmt(r['opp']):>26} {fmt(r['both']):>16} {fmt(r['inter']):>16}")
print("\nPooled per held deck (equal weight over its 8 cells):")
for deck, ps in (("manectric", range(0, 8)), ("raticate", range(8, 16))):
    line = f"  {deck:10s}"
    for lab in ("own", "opp", "both", "inter"):
        m = sum(rows[p][lab][0] for p in ps) / 8
        half = 100 * 1.96 * math.sqrt(sum(rows[p][lab][1] for p in ps)) / 8
        line += f"  {lab} {m:+5.1f} ± {half:3.1f}"
    print(line)
