#!/usr/bin/env python3
"""The kx3 position study's reading (SPEC.md, "The reading"): Dustin v km3 v frozen kx3 (F) v candidate kx3 (C) on his real turn starts.

PART 1, the 119 study positions (old harness):
- km3 is the committed runs_km3. F and C are the union of the PF1-PF4 and PC1-PC4 worker folders under workers/.
- Per bot, Sonnet's kw_report.py (the Oct 12 read's comparison rules: plans cut after the first draw card or Sabrina, bare Ability labels
  normalised, EndTurn ignored) gives each position's first-move count out of 12 and its modal plan.
- A position agrees when the bot makes his first move in 10 or more of 12 seeds.
- The main table leaves out the 35 rules-switch-2 positions and the 14 Special-Condition positions; each of those gets its own table.
- "Neither" positions: no bot makes his first move in 7 or more of 12 seeds. They are listed for his next quiz.
- Candidate v frozen is paired by position, on the share of seeds that make his first move.

PART 2, Sonnet's 8 Oct 13 positions (new harness): a separate table with km3 (v2/runs_km3), F_cond and C_cond (workers/P8). The three in
game 010837 face the opponent's Mega Kangaskhan ex, which every bot's forecast prices at 80, not 120
(../kangaskhan_pricing_2026-10-13/).

Nothing is decided on this: it describes how the bots play his real positions. Run from the repository root; it writes reading/."""
import collections, csv, glob, json, math, os, shutil, statistics as st, subprocess, sys

Q = "rl/results/pause_positions_kx3_2026-10"
P1 = "rl/results/pause_games_new_2026-10-12"
P2 = "rl/results/pause_games_new_2026-10-13/v2"
KW = f"{P1}/harness/kw_report.py"
OUT = f"{Q}/reading"
os.makedirs(OUT, exist_ok=True)


def gather(dst, workers, sub):
    """one runs folder from several workers' (symlinks; a position played twice is an error)"""
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)
    for w in workers:
        for f in glob.glob(f"{Q}/workers/{w}/{sub}/*_*.jsonl") + glob.glob(f"{Q}/workers/{w}/{sub}/err_*.txt"):
            t = f"{dst}/{os.path.basename(f)}"
            assert not os.path.exists(t), f"played twice: {f}"
            os.symlink(os.path.abspath(f), t)
    return dst


def report(positions, runs, prefix, bot):
    r = subprocess.run([sys.executable, "-B", KW, positions, runs, prefix, bot], capture_output=True, text=True)
    open(prefix + "_report.txt", "w").write(r.stdout + r.stderr)
    assert r.returncode == 0, r.stderr[-2000:]
    return {x["id"]: x for x in json.load(open(prefix + "_summary.json", encoding="utf-8"))}


ids = [l.strip() for l in open(f"{Q}/run_ids.txt") if l.strip()]
pos1 = {p["id"]: p for p in json.load(open(f"{P1}/positions_all.json", encoding="utf-8"))}
rows1 = {r["position_id"]: r for r in csv.DictReader(open(f"{P1}/position_list.tsv", encoding="utf-8"), delimiter="\t")}
COND = {i for i in ids if "no condition field" in json.dumps(pos1[i])}
SW2 = {i for i in ids if (rows1[i].get("switch2_flag") or "").strip() not in ("", "-", "no", "0", "False")}
tmp = f"{OUT}/positions_119.json"
json.dump([pos1[i] for i in ids], open(tmp, "w", encoding="utf-8"), ensure_ascii=False)

runsF = gather(f"{OUT}/runs_F", ["PF1", "PF2", "PF3", "PF4"], "runs_B")
runsC = gather(f"{OUT}/runs_C", ["PC1", "PC2", "PC3", "PC4"], "runs_B")
B = {"km3": report(tmp, f"{Q}/runs_km3", f"{OUT}/km3", "km3"),
     "F": report(tmp, runsF, f"{OUT}/F", "kx3"),
     "C": report(tmp, runsC, f"{OUT}/C", "kx3m64")}
missing = {b: [i for i in ids if i not in B[b]] for b in B}
L = [f"PART 1: {len(ids)} study positions; runs found: " + ", ".join(f"{b} {len(ids) - len(missing[b])}" for b in B)
     + ("; MISSING " + str({b: m[:5] for b, m in missing.items() if m}) if any(missing.values()) else ""), ""]
have = [i for i in ids if all(i in B[b] for b in B)]
comp = [i for i in have if B["km3"][i]["comparable"]]
main = [i for i in comp if i not in COND and i not in SW2]


def share(b, i):
    r = B[b][i]
    return r["same_first"] / r["n"]


def verdict(b, i):
    k = share(b, i)
    return "agree" if k >= 10 / 12 else ("differ" if k <= 2 / 12 else "split")


def block(title, sel):
    L.append(f"== {title}: {len(sel)} positions with his recorded plan")
    if not sel:
        return
    for b in B:
        c = collections.Counter(verdict(b, i) for i in sel)
        mean = 100 * st.mean(share(b, i) for i in sel)
        plan = sum(1 for i in sel if B[b][i]["same_plan"] / B[b][i]["n"] >= 10 / 12)
        L.append(f"  {b:<4}: makes his first move in {mean:.1f}% of seeds; agree {c['agree']}, split {c['split']}, differ {c['differ']}; "
                 f"his whole plan in 10+ of 12 seeds: {plan}")
    for a, b in (("C", "F"), ("F", "km3"), ("C", "km3")):
        d = [share(a, i) - share(b, i) for i in sel]
        m, h = 100 * st.mean(d), (100 * 1.96 * st.stdev(d) / math.sqrt(len(d)) if len(d) > 1 else 0.0)
        L.append(f"  {a} - {b}, paired by position (share of seeds with his first move): {m:+.1f} +- {h:.1f} points; "
                 f"{a} higher in {sum(x > 0 for x in d)}, lower in {sum(x < 0 for x in d)}, equal in {sum(x == 0 for x in d)}")


block("MAIN (no switch-2 flag, no Special Condition)", main)
block("RULES SWITCH 2 flagged (engines differ by design)", [i for i in comp if i in SW2])
block("SPECIAL CONDITION not represented (read apart)", [i for i in comp if i in COND])
L.append("")
neither = [i for i in comp if all(B[b][i]["same_first"] < 7 for b in B)]
L.append(f"NEITHER: no bot makes his first move in 7 or more of 12 seeds: {len(neither)} positions (for his next quiz)")
for i in neither:
    r = B["km3"][i]
    L.append(f"  {i} ({rows1[i]['deck_name'][:40]}){' [switch 2]' if i in SW2 else ''}{' [condition]' if i in COND else ''}: his {r['his'][0] if r['his'] else '-'}; "
             + "; ".join(f"{b} {max(B[b][i]['first'].items(), key=lambda kv: kv[1])[0]} x{max(B[b][i]['first'].values())}" for b in B))
L.append("")
L.append("BY DECK (main set): mean share of seeds with his first move, km3 / F / C")
fam = collections.defaultdict(list)
for i in main:
    fam[rows1[i]["deck_name"]].append(i)
for f, v in sorted(fam.items(), key=lambda kv: -len(kv[1])):
    L.append(f"  {f[:60]:<60} n {len(v):>2}: " + " / ".join(f"{100 * st.mean(share(b, i) for i in v):.0f}%" for b in B))
L.append("")
L.append("WHAT DIFFERS (main set, each bot's modal plan v his, first category):")
for b in B:
    c = collections.Counter(B[b][i]["cat"] for i in main)
    L.append(f"  {b}: " + "; ".join(f"{k} {v}" for k, v in c.most_common()))
L.append("")
L.append("WHERE THE CANDIDATE AND THE FROZEN kx3 PART (main set, |C - F| >= 4 of 12 seeds on his first move):")
for i in main:
    if abs(B["C"][i]["same_first"] - B["F"][i]["same_first"]) >= 4:
        L.append(f"  {i}: his {B['km3'][i]['his'][0] if B['km3'][i]['his'] else '-'}; km3 {B['km3'][i]['same_first']}/12, F {B['F'][i]['same_first']}/12, "
                 f"C {B['C'][i]['same_first']}/12; C modal {' -> '.join(B['C'][i]['modal'][:4])}; F modal {' -> '.join(B['F'][i]['modal'][:4])}")

# PART 2
L.append("")
eight = [l.strip() for l in open(f"{Q}/shards/S8.txt") if l.strip()]
pos2 = {p["id"]: p for p in json.load(open(f"{P2}/positions_all.json", encoding="utf-8"))}
tmp2 = f"{OUT}/positions_8.json"
json.dump([pos2[i] for i in eight], open(tmp2, "w", encoding="utf-8"), ensure_ascii=False)
if os.path.isdir(f"{Q}/workers/P8/runs_B") and os.path.isdir(f"{Q}/workers/P8/runs_C"):
    B2 = {"km3": report(tmp2, f"{P2}/runs_km3", f"{OUT}/p2_km3", "km3"),
          "F": report(tmp2, f"{Q}/workers/P8/runs_B", f"{OUT}/p2_F", "kx3"),
          "C": report(tmp2, f"{Q}/workers/P8/runs_C", f"{OUT}/p2_C", "kx3m64")}
    L.append("PART 2: Sonnet's 8 Oct 13 positions (new harness: Special Conditions and the knock-out count); first move his in n of 12 seeds")
    for i in eight:
        r = B2["km3"][i]
        kang = " [opponent's Mega Kangaskhan ex: every bot's forecast prices its attack at 80, not 120]" if "010837" in i else ""
        L.append(f"  {i}: his {' -> '.join(r['his'][:4]) if r['his'] else '-'}; " + "; ".join(
            f"{b} {B2[b][i]['same_first']}/12 (modal {' -> '.join(B2[b][i]['modal'][:3])})" for b in B2) + kang)
print("\n".join(L))
