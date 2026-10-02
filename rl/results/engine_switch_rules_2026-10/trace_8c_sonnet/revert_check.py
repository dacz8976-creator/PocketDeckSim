#!/usr/bin/env python3
"""The revert check over every lookahead-kind game of step 8c (verdicts.tsv, kind == lookahead): at each game's first differing tick, three
programs decide (print-only patched, same state, same search seed): the old engine, R, and R-revert (R with only queued_attack_damage_choice's
coin-target form switched back to the plain ApplyDamage for that one decision). Records the three choices, whether R-revert reproduces the old
choice and the old candidate scores, the bot-faithful gate (PGGATE: the search entered a pure queued attack-damage frame at a coin-Ability target),
and the coin-Ability Pokemon in play at the tick. Read-only; writes <out>/revert_check.tsv.
Usage: revert_check.py [--jobs 12] [--limit N] [--out DIR]"""
import argparse, collections, csv, re, subprocess, sys
import concurrent.futures as cf
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--jobs", type=int, default=12)
ap.add_argument("--limit", type=int, default=0)
ap.add_argument("--out", default="/home/dacz8976/c8c/out")
a = ap.parse_args()
W = Path("/home/dacz8976/c8c")
OUT = Path(a.out)
rows = {(r["step"], r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t")}
ver = [r for r in csv.DictReader(open(OUT / "verdicts.tsv", encoding="utf-8"), delimiter="\t") if r["kind"] == "lookahead"]
if a.limit:
    ver = ver[:a.limit]
print(f"{len(ver)} lookahead-kind games", flush=True)
PROGS = [("old", "old", []), ("R", "new", []), ("revert", "var", ["--revert-queued"])]


def run(binary, flags, v):
    r = rows[(v["step"], v["bot"], int(v["pairing"]), int(v["i"]))]
    p = subprocess.run(["nice", "-n", "19", str(W / "dg" / f"score_dump_{binary}"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                        "--seed-base", "23100000000", "--pairing", v["pairing"], "--bot", v["bot"], "--deal", v["i"], "--tick", v["k"]] + flags,
                       cwd=W / "dg" / binary / "engine", capture_output=True, text=True)
    text = p.stdout + p.stderr
    chosen = next((ln.split("chose ", 1)[1] for ln in text.splitlines() if ln.startswith("deal ") and "chose " in ln), "?")
    board = next((ln for ln in text.splitlines() if ln.startswith("PGBOARD")), "")
    lines = text.splitlines()
    start = max((i for i, ln in enumerate(lines) if ln.startswith("PGTICK") and "asked about" in ln), default=0)
    cands = [(float(m[1]), m[2]) for ln in lines[start:] if (m := re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", ln))]
    gates = [ln for ln in lines[start:] if ln.startswith("PGGATE")]
    return {"chosen": chosen, "cands": cands, "gates": gates, "board": board, "rc": p.returncode}


def job(v):
    return v, {name: run(binary, flags, v) for name, binary, flags in PROGS}


results = []
with cf.ThreadPoolExecutor(a.jobs) as ex:
    futs = [ex.submit(job, v) for v in ver]
    for n, f in enumerate(cf.as_completed(futs), 1):
        results.append(f.result())
        if n % 100 == 0 or n == len(futs):
            print(f"  {n}/{len(futs)} games", flush=True)
results.sort(key=lambda t: (t[0]["bot"], int(t[0]["pairing"]), int(t[0]["i"])))


def same_scores(x, y):
    return len(x) == len(y) and all(abs(p[0] - q[0]) < 1e-9 and p[1] == q[1] for p, q in zip(x, y))


with open(OUT / "revert_check.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tk\tverdict\told_choice\tR_choice\trevert_choice\treplay_ok\treproduced\tscores_old_eq_revert\tscores_old_eq_R\tgate_R\tgate_old\tgate_revert\tcoin_on_board\tprocess_ok\n")
    for v, res in results:
        o, r_, rv = res["old"], res["R"], res["revert"]
        coin = re.findall(r"seat\d=\[([^\]]*)\]", r_["board"])
        coin_on_board = "yes" if any(c.strip() for c in coin) else "no"
        f.write("\t".join(map(str, [v["step"], v["bot"], v["pairing"], v["i"], v["k"], v["verdict"], o["chosen"], r_["chosen"], rv["chosen"],
                                    "yes" if o["chosen"] != r_["chosen"] else "NO", "yes" if rv["chosen"] == o["chosen"] else "no",
                                    "yes" if same_scores(o["cands"], rv["cands"]) else "no", "yes" if same_scores(o["cands"], r_["cands"]) else "no",
                                    len(r_["gates"]), len(o["gates"]), len(rv["gates"]), coin_on_board,
                                    "yes" if o["rc"] == r_["rc"] == rv["rc"] == 0 else "NO"])) + "\n")
print("wrote", OUT / "revert_check.tsv", flush=True)
