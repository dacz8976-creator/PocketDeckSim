import json, collections, math
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/altaria_network_divergence_2026-09-26/decisions.jsonl"
rows = [json.loads(l) for l in open(D)]
setup = [r for r in rows if (r.get("net_detail") or {}).get("setup") or (r.get("kp3_detail") or {}).get("setup")]
print("setup decisions:", len(setup), "differ:", sum(bool(r.get("differs")) for r in setup))
# opening Active choice: both moves place into the active slot at setup
op = [r for r in setup if (r.get("net_detail") or {}).get("slot") == "active" and (r.get("kp3_detail") or {}).get("slot") == "active"]
print("opening-Active decisions:", len(op), "differ:", sum(bool(r.get("differs")) for r in op))
c = collections.Counter((r["net_detail"]["name"], r["kp3_detail"]["name"]) for r in op)
print("opening Active (network, kp3) counts:", c.most_common(12))
dif = [r for r in op if r.get("differs") and r.get("net_minus_kp3") is not None]
by = collections.defaultdict(list)
for r in dif:
    by[(r["net_detail"]["name"], r["kp3_detail"]["name"])].append(r["net_minus_kp3"])
def ci(x):
    n = len(x); m = sum(x) / n
    sd = math.sqrt(sum((a - m) ** 2 for a in x) / (n - 1)) if n > 1 else 0
    return 100 * m, 100 * 1.96 * sd / math.sqrt(n) if n > 1 else float('nan')
allv = [r["net_minus_kp3"] for r in dif]
print("all differing opening choices: n=%d, net-kp3 %+.1f +- %.1f points" % ((len(allv),) + ci(allv)))
for k, x in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print("  net %-16s kp3 %-16s n=%3d  %+.1f +- %.1f" % (k[0], k[1], len(x), *ci(x)))
kd = [r["net_minus_kp3"] for r in dif if r["kp3_detail"]["name"] == "Darkrai"]
print("kp3 opens Darkrai, network doesn't: n=%d, %+.1f +- %.1f" % ((len(kd),) + ci(kd)))
# how often each opens Darkrai among all opening decisions
print("network opens Darkrai:", sum(r["net_detail"]["name"] == "Darkrai" for r in op), "of", len(op),
      "| kp3 opens Darkrai:", sum(r["kp3_detail"]["name"] == "Darkrai" for r in op), "of", len(op))
print("total/game from differing opening choices: %+.2f points" % (100 * sum(allv) / 400))
