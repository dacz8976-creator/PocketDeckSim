"""koa's reading, in the registration's order (../../opening_active_census_2026-09-26/REGISTRATION.md section 7), on the
official engine (main-83e17ae). kp3's references at this engine are kpf's reading runs (identical to the official build's
own table replay, ../../engine_switch_2026-09-26/pin_identity.txt).
  0. koa3 at the official build replays the cloud's koa3 identity games at 9af40c8 (../identity_koa3_40.jsonl), since
     kpf's refactor of value_functions.rs came between the two builds.
  1. The footprint: the share of the 14,000 paired table games whose moves differ from kp3's. Under 15% -> the reserve
     route; 15% or more -> the ordinary adoption rule. Fixed before anything else is read.
  2. (b) No harm: score.py on the 28 table cells, rules v2, with koa's mixed rows: the tau margin (kp3 minus koa) 90%
     lower bound at -1.0 or above, and no veto counting. Altaria's seven Limitless cells reported before and after.
  3. (c) Mixed rows: Altaria's own side (koa on Altaria, its 7 rows) not worse beyond paired noise; the seven opponents'
     rows with koa on them are identities (exactly 0).
  4. (d) Altaria's own side, pooled over its 7 rows, above zero beyond paired noise (predicted up; Altaria v Lucario +5.5).
  5. Held-out (B2e 0-47): no archetype more than 2 further from Limitless pooled.
  6. Diagnostics, reported after the decision: kob3 and kor3's own-side Altaria change.
Usage: python3 read_koa.py   (writes nothing; print to READING_numbers.txt)"""
import csv, json, math, os, subprocess, sys
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(RES, "table_readings_2026-09-24"))
import score as S  # noqa: E402
KPF = os.path.join(RES, "kpf_2026-09-26", "reading")
PAIRS = S.D.PAIRS[:28]
ALT = [p for p, (a, b) in enumerate(PAIRS) if "altaria" in (a, b)]


def load(path):
    return {(g["pairing"], g["i"]): g for g in map(json.loads, open(path, encoding="utf-8"))}


kp3, koa = load(os.path.join(KPF, "table_kp3.jsonl")), load(os.path.join(HERE, "table_koa3.jsonl"))
# 0. identity against the cloud's koa3 at 9af40c8
cloud = load(os.path.join(RES, "koa_2026-09-26", "identity_koa3_40.jsonl"))
f0 = [f for f in ("moves", "winner_seat", "points", "seed") if all(f in g for g in cloud.values())]
same0 = sum(all(koa[k][f] == cloud[k][f] for f in f0) for k in cloud)
print(f"0. koa3 at the official build v the cloud's koa3 at 9af40c8: {same0} of {len(cloud)} games equal on {f0}")
# 1. footprint
diff = [k for k in kp3 if koa[k]["moves"] != kp3[k]["moves"]]
by_p = defaultdict(int)
for p, _ in diff:
    by_p[p] += 1
fp = 100 * len(diff) / len(kp3)
print(f"1. footprint: {len(diff)} of {len(kp3)} table games differ from kp3 = {fp:.1f}% (predicted 6.0%); "
      f"route: {'RESERVE (under 15%)' if fp < 15 else 'ORDINARY adoption rule (15% or more)'}")
print("   per pairing with any difference: " + ", ".join(f"{PAIRS[p][0]} v {PAIRS[p][1]} {n}" for p, n in sorted(by_p.items())))
outside = [p for p in by_p if p not in ALT]
print(f"   pairings without Altaria that differ: {len(outside)} (registration section 4: they are identities)")
# Section 8's leak test: a changed game with both openings unchanged refutes koa (stop before reading anything else).
leaks = [k for k in diff if koa[k]["openings"] == kp3[k]["openings"]]
print(f"   LEAK TEST (section 8): changed games with both openings unchanged: {len(leaks)}"
      + (f" -> REFUTED, e.g. {leaks[:5]}" if leaks else " -> none"))
trans = defaultdict(int)
for k in diff:
    # "openings" lists the first-named deck's opening Active, then the second's (by deck, not by seat); Altaria is the
    # first-named deck in all its pairings.
    trans[(kp3[k]["openings"][0], koa[k]["openings"][0])] += 1
print("   Altaria's opening transitions in changed games (kp3 -> koa3): " +
      ", ".join(f"{a}->{b} {n}" for (a, b), n in sorted(trans.items(), key=lambda x: -x[1])))
# 2. (b) score.py on the 28 cells, rules v2, with the mixed rows
mix = [os.path.join(HERE, f"mixed_koa3_{s}.jsonl") for s in ("first", "second")]
cmd = [sys.executable, os.path.join(RES, "table_readings_2026-09-24", "score.py"), "--rules", "v2",
       "--limitless", os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"),
       "--limitless-events", os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev_events.json"),
       "--old-games", os.path.join(KPF, "table_kp3.jsonl"), "--new-games", os.path.join(HERE, "table_koa3.jsonl"),
       "--old", "kp3", "--new", "koa3", "--mixed"] + mix
out = subprocess.run(cmd, capture_output=True, text=True).stdout
open(os.path.join(HERE, "score28_koa3_vs_kp3.txt"), "w", encoding="utf-8").write(out)
print("2. (b) score.py, 28 table cells, rules v2 (full output: score28_koa3_vs_kp3.txt):")
for line in out.splitlines():
    if any(t in line for t in ("real error, current minus new", "dMSE", "cell veto", "deck veto", "ADOPTION", "koa3: real error", "kp3: real error")):
        print("   " + line.strip()[:240])
v2 = json.load(open(os.path.join(RES, "scoreboard_v2_2026-09-25", "limitless_v2_dev.json"), encoding="utf-8"))["cells"]
print("   Altaria's seven Limitless cells, before (kp3) and after (koa3), v2 development half:")
for p in ALT:
    a, b = PAIRS[p]
    s_kp = 100 * sum(kp3[(p, i)]["first_deck_score"] for i in range(500)) / 500
    s_ko = 100 * sum(koa[(p, i)]["first_deck_score"] for i in range(500)) / 500
    w, l, t = v2[f"{a}|{b}"]
    print(f"     {a} v {b}: kp3 {s_kp:.1f} -> koa3 {s_ko:.1f}; Limitless {100 * (w + 0.5 * t) / (w + l + t):.1f} (n {w + l + t})")


# 3-4. (c) and (d): the mixed rows against kp3's table games, same deals
def side(rows_file, flip_opponent):
    rows = load(rows_file)
    parts, per = [], {}
    for p in ALT:
        a, b = PAIRS[p]
        base = {i: {"s": kp3[(p, i)]["first_deck_score"], "seed": kp3[(p, i)]["seed"]} for i in range(500)}
        other = {i: {"s": rows[(p, i)]["first_deck_score"], "seed": rows[(p, i)]["seed"]} for i in range(500)}
        # Altaria is always the first-named deck in its pairings (alphabetical); the side read is Altaria's for the
        # "first" rows and the opponent's for the "second" rows.
        d = S.diffs(base, other, flip_opponent)
        parts.append(d)
        per[f"{a} v {b}"] = S.mean_var(d)
    return S.side_change(parts), per


(own_m, own_h, own_n), own_per = side(mix[0], False)
(opp_m, opp_h, opp_n), opp_per = side(mix[1], True)
second = load(mix[1])
ident = sum(second[(p, i)]["moves"] == kp3[(p, i)]["moves"] for p in ALT for i in range(500))
print(f"3. (c) Altaria's own side (koa on Altaria, 7 rows, {own_n} deals): {own_m:+.2f} +/- {own_h:.2f} points "
      f"({'NOT worse beyond noise' if own_m + own_h >= 0 else 'WORSE beyond noise'})")
print(f"   opponents' rows (koa on the opponent): change {opp_m:+.2f} +/- {opp_h:.2f}; games identical to kp3's: {ident} of {7 * 500}")
print(f"4. (d) Altaria's own side above zero beyond paired noise: {'YES' if own_m - own_h > 0 else 'NO'} ({own_m:+.2f} +/- {own_h:.2f})")
for c, (m, v) in own_per.items():
    print(f"     {c}: {m:+.2f} +/- {1.96 * math.sqrt(v):.2f}{'   (refutation check: predicted +5.5)' if 'lucario' in c else ''}")
# 5. held-out
tsv = {int(r["pairing"]): r for r in csv.DictReader(open(os.path.join(RES, "b2e_card_check_2026-09-26", "b2e_pairings.tsv"), encoding="utf-8"), delimiter="\t")}
lim = defaultdict(dict)
for r in csv.DictReader(open(os.path.join(RES, "b2e_card_check_2026-09-26", "limitless_cells.csv"), encoding="utf-8")):
    if int(r["n"]):
        lim[r["dataset"]][(r["archetype"], r["opponent"])] = float(r["score_pct"])


def panel(path):
    by = defaultdict(list)
    for g in map(json.loads, open(path, encoding="utf-8")):
        if g["pairing"] < 48:
            r = tsv[g["pairing"]]
            by[(r["held_key"], r["opponent"])].append(g["first_deck_score"])
    out = defaultdict(dict)
    for (k, o), s in by.items():
        out[k][o] = 100 * sum(s) / len(s)
    return out


if not os.path.exists(os.path.join(HERE, "b2e_koa3.jsonl")):
    print("5. held-out: b2e_koa3.jsonl not in yet")
    a5 = {}
else:
    a5, b5 = panel(os.path.join(KPF, "b2e_kp3.jsonl")), panel(os.path.join(HERE, "b2e_koa3.jsonl"))
    print("5. held-out (B2e archetypes, Limitless pooled):")
names = sorted({k for k, _ in lim["pooled"]})
for k in sorted(a5):
    arch = next((n for n in names if n == k), None) or next((n for n in names if n.startswith(k)), None)
    cells = [o for o in a5[k] if (arch, o) in lim["pooled"]]
    L = sum(lim["pooled"][(arch, o)] for o in cells) / len(cells)
    x, y = sum(a5[k].values()) / len(a5[k]), sum(b5[k].values()) / len(b5[k])
    fur = abs(y - L) - abs(x - L)
    print(f"     {k}: kp3 {x:.1f} -> koa3 {y:.1f}; L {L:.1f}; further by {fur:+.1f}{'  VETO FIRES (awaits mixed rows)' if fur > 2 else ''}")
# 6. diagnostics
for dname in ("kob3", "kor3"):
    try:
        (m, h, n), _ = side(os.path.join(HERE, f"mixed_{dname}_first.jsonl"), False)
        print(f"6. diagnostic {dname}: Altaria's own side {m:+.2f} +/- {h:.2f} ({n} deals)")
    except FileNotFoundError:
        print(f"6. diagnostic {dname}: not run")
