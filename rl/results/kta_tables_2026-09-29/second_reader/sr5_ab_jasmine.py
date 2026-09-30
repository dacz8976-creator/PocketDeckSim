"""Step 5: the fresh Dustin-deck A/B (5.6, reported) and the Jasmine line (5.5): deck 07, Jasmine played on at least 20%
of the turns she was offered, pooled over the kta3 arm's 1,920 games (played summed over offered summed); the guard:
kog3's own rate on the same deals at 20% or more counts as not passed. `plays` = {card: [turns offered, turns played]}
(kta_ab_play.py's docstring). Paired by (opponent, seat, i); seeds 23,004,000,000 + 10,000 x deck + 1,000 x opponent
index (+500 seat 1) + i, i < 120. Writes OUT/sr5_ab_jasmine.txt."""
import sys, math
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kta_tables_2026-09-29/second_reader")
from sr_lib import *

lines = []
p = lines.append
OPP = ["t-" + n for n in sorted(NAMES)]
for deck in (7, 5, 11, 1, 3):
    A = {(r["opp"], r["seat"], r["i"]): r for r in rd(F + f"ab_d{deck:02d}_kog3.jsonl")}
    B = {(r["opp"], r["seat"], r["i"]): r for r in rd(F + f"ab_d{deck:02d}_kta3.jsonl")}
    assert len(A) == len(B) == 1920 and set(A) == set(B)
    for k, r in A.items():
        opp, seat, i = k
        seed = 23004000000 + 10000 * deck + 1000 * OPP.index(opp) + 500 * seat + i
        assert r["seed"] == B[k]["seed"] == seed and i < 120, (deck, k, r["seed"])
        assert (r["pilot"], r["opp_pilot"]) == ("kog3", "kog3") and (B[k]["pilot"], B[k]["opp_pilot"]) == ("kta3", "kog3")
    wa = sum(r["won"] for r in A.values())
    wb = sum(r["won"] for r in B.values())
    d = [100.0 * (int(B[k]["won"]) - int(A[k]["won"])) for k in A]
    m, v = mv(d)
    hw = 1.96 * math.sqrt(v)
    b_only = sum(1 for k in A if B[k]["won"] and not A[k]["won"])
    a_only = sum(1 for k in A if A[k]["won"] and not B[k]["won"])
    mdiff = sum(1 for k in A if A[k]["moves"] != B[k]["moves"])
    p(f"deck {deck:02d}: kog3 {wa}/1920 = {100*wa/1920:.2f}% -> kta3 {wb}/1920 = {100*wb/1920:.2f}%; paired {m:+.2f} ({m-hw:+.2f} to {m+hw:+.2f});"
      f" discordant {b_only} / {a_only}; moves differ {100*mdiff/1920:.1f}% ({mdiff})")
    if deck == 7:
        tot = {}
        for arm, D in (("kog3", A), ("kta3", B)):
            off = sum(r.get("plays", {}).get("Jasmine", [0, 0])[0] for r in D.values())
            pl = sum(r.get("plays", {}).get("Jasmine", [0, 0])[1] for r in D.values())
            tot[arm] = (off, pl)
            p(f"   Jasmine {arm}: played {pl} of {off} offered turns = {100*pl/off:.3f}%")
        off, pl = tot["kta3"]
        goff, gpl = tot["kog3"]
        reaches = 5 * pl >= off
        guard_bites = 5 * gpl >= goff
        p(f"JASMINE LINE: kta3 {100*pl/off:.2f}% {'reaches' if reaches else 'does not reach'} 20%; guard: kog3 {100*gpl/goff:.2f}% "
          f"{'reaches 20% (not passed)' if guard_bites else 'below 20%'} -> {'PASS' if reaches and not guard_bites else 'NOT PASSED'} (gates only in the fallback)")
open(OUT + "/sr5_ab_jasmine.txt", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
