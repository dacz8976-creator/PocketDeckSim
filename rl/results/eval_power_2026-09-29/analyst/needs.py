"""What sizes would a reading of a given true effect need? Plug-in variances from decompose.py's JSON (candidate moving cells as the reading's candidate did).
Power = Phi((|t| - 1.96 sd)/sd). Also: the post-freeze and pooled Limitless options at their sizes (x0.5, x1.5, x2.13 = dev + spent holdout, sizes only)."""
import json, math
A = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_power/analyst/"
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
dec = {n: json.load(open(A + f"decomp_{n}.json"))["analytic"] for n in ("koh3_vs_kog3", "kog3_vs_kp3", "kog3_vs_kpg3")}
TAU0 = 14.05


def sd(v, ms, mL):
    return math.sqrt(v["var_sim"] / ms + v["var_lim"] / mL + v["var_cross"] / (ms * mL))


CF = [("now", 1, 1), ("sim x4", 4, 1), ("Limitless x1.5 (dev + post-freeze read)", 1, 1.5), ("Limitless x2.13 (dev + spent holdout, 4,712)", 1, 2.13),
      ("Limitless x0.5 (post-freeze read alone)", 1, 0.5), ("sim x4 + Limitless x2.13", 4, 2.13), ("sim x4 + Limitless x1.5", 4, 1.5)]
for name, effects in (("koh3_vs_kog3", (-45.1, -27.6, -55.0)), ("kog3_vs_kp3", (-17.0, -27.6, -43.1)), ("kog3_vs_kpg3", (-5.0, -10.0))):
    v = dec[name]
    print(f"== plug-in from {name} (var sim {v['var_sim']:.1f}, Limitless {v['var_lim']:.1f}, cross {v['var_cross']:.1f})")
    for e in effects:
        tau_new = math.sqrt(TAU0 ** 2 + e)
        print(f"  true dMSE {e:+.1f} (real error 14.05 -> {tau_new:.2f}, i.e. {14.05 - tau_new:.2f} better): power " +
              " | ".join(f"{lab.split(' (')[0]} {100 * Phi((-e - 1.96 * sd(v, ms, mL)) / sd(v, ms, mL)):.0f}%" for lab, ms, mL in CF))
    # sizes for 80% power at each effect: with sim x4 fixed, and with sim fixed
    for e in effects[:1]:
        target = -e / 2.8016
        best = None
        for ms in (1, 2, 4, 8):
            # solve mL: var_sim/ms + (var_lim + var_cross/ms)/mL = target^2
            rest = target ** 2 - v["var_sim"] / ms
            if rest <= 0:
                print(f"  80% power at {e:+.1f} with sim x{ms}: impossible even with unlimited Limitless data")
                continue
            mL = (v["var_lim"] + v["var_cross"] / ms) / rest
            print(f"  80% power at {e:+.1f} with sim x{ms}: needs Limitless x{mL:.2f} = {mL * 2214:,.0f} matches")
