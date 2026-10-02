#!/usr/bin/env python3
"""The finite-cut question. Among the lookahead-kind games whose decks hold a finite-cut Pokemon (Bastiodon A2 114, Hisuian Goodra B3b 050), run the
decision at the first differing tick on old and on VAR2 with (full) --revert-queued --revert-cut, (cut-only) --revert-cut, and (queued-only)
--revert-queued, and count which reproduce the old choice and candidate scores. Writes <out>/revert_check_cut.tsv.
Usage: rc_cut.py [--jobs 12] [--out DIR]"""
import argparse, csv, re, subprocess
import concurrent.futures as cf
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--jobs", type=int, default=12)
ap.add_argument("--out", default="/home/dacz8976/c8c/out")
a = ap.parse_args()
W = Path("/home/dacz8976/c8c")
OUT = Path(a.out)
rows = {(r["step"], r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t")}
FINITE = ("A2 114", "B3b 050")


def has_finite(path):
    t = (W / "root" / path).read_text(encoding="utf-8", errors="replace")
    return any(i in t for i in FINITE)


sel = []
for v in csv.DictReader(open(OUT / "verdicts.tsv", encoding="utf-8"), delimiter="\t"):
    if v["kind"] != "lookahead":
        continue
    r = rows[(v["step"], v["bot"], int(v["pairing"]), int(v["i"]))]
    if has_finite(r["held_file"]) or has_finite(r["panel_file"]):
        sel.append((v, r))
print(f"{len(sel)} lookahead-kind games with a finite-cut Pokemon (A2 114 / B3b 050) in a deck", flush=True)
PROGS = [("old", "old", []), ("full", "var2", ["--revert-queued", "--revert-cut"]), ("cut_only", "var2", ["--revert-cut"]), ("queued_only", "var2", ["--revert-queued"])]


def run(binary, flags, v, r):
    p = subprocess.run(["nice", "-n", "19", str(W / "dg" / f"score_dump_{binary}"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                        "--seed-base", "23100000000", "--pairing", v["pairing"], "--bot", v["bot"], "--deal", v["i"], "--tick", v["k"]] + flags,
                       cwd=W / "dg" / binary.replace("var2", "var2") / "engine", capture_output=True, text=True)
    text = p.stdout + p.stderr
    chosen = next((ln.split("chose ", 1)[1] for ln in text.splitlines() if ln.startswith("deal ") and "chose " in ln), "?")
    board = next((ln for ln in text.splitlines() if ln.startswith("PGBOARD")), "")
    lines = text.splitlines()
    start = max((i for i, ln in enumerate(lines) if ln.startswith("PGTICK") and "asked about" in ln), default=0)
    cands = [(float(m[1]), m[2]) for ln in lines[start:] if (m := re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", ln))]
    return {"chosen": chosen, "cands": cands, "board": board}


def job(item):
    v, r = item
    return v, {n: run(b, f, v, r) for n, b, f in PROGS}


res = []
with cf.ThreadPoolExecutor(a.jobs) as ex:
    for n, f in enumerate(cf.as_completed([ex.submit(job, s) for s in sel]), 1):
        res.append(f.result())
        if n % 100 == 0 or n == len(sel):
            print(f"  {n}/{len(sel)}", flush=True)
res.sort(key=lambda t: (t[0]["bot"], int(t[0]["pairing"]), int(t[0]["i"])))
same = lambda x, y: len(x) == len(y) and all(abs(p[0] - q[0]) < 1e-9 and p[1] == q[1] for p, q in zip(x, y))
with open(OUT / "revert_check_cut.tsv", "w", encoding="utf-8") as f:
    f.write("step\tbot\tpairing\ti\tk\tverdict\tfinite_on_board\told_choice\tfull_choice\tcut_only_choice\tqueued_only_choice\tfull_ok\tcut_only_ok\tqueued_only_ok\n")
    for v, rr in res:
        o = rr["old"]
        fin = "yes" if re.findall(r"A2 114|B3b 050", rr["old"]["board"]) else "no"
        ok = lambda n: "yes" if rr[n]["chosen"] == o["chosen"] and same(o["cands"], rr[n]["cands"]) else "no"
        f.write("\t".join([v["step"], v["bot"], v["pairing"], v["i"], v["k"], v["verdict"], fin, o["chosen"], rr["full"]["chosen"], rr["cut_only"]["chosen"], rr["queued_only"]["chosen"],
                           ok("full"), ok("cut_only"), ok("queued_only")]) + "\n")
print("wrote", OUT / "revert_check_cut.tsv", flush=True)
