"""PLAN item (a)'s open test: coin_probe v2 (Oct 2, 57c6586) at each lookahead game's first differing tick, with two added
lines: every ply where it saw a pure queued frame (PURE_PLIES), and R's PGGATE frame (GATE_PLIES: a pure queued frame of any
mover with a coin Pokemon of either side among its targets). WALK=1 sets GATE_WALK: the walk goes on past a queued frame. Usage: run_open_test.py <revert_check.tsv> <W: root/, pairs_8.tsv> <probe> <out.tsv>"""
import csv, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
RC, W, BIN, OUT = (Path(x) for x in sys.argv[1:5])
pairs = {int(c[0]): (c[3], c[5]) for c in (l.split("\t") for l in open(W / "pairs_8.tsv").read().splitlines()[1:])}
ENV = dict(os.environ, GATE_WALK="1") if os.environ.get("WALK") else dict(os.environ)
rows = list(csv.DictReader(open(RC), delimiter="\t"))
def run(r, limit=None):
    held, opp = pairs[int(r["pairing"])]
    p = subprocess.run([str(BIN), "--a", str(W / "root" / held), "--b", str(W / "root" / opp), "--seed-base", "23100000000",
                        "--pairing", r["pairing"], "--bot", r["bot"], "--deal", r["i"], "--tick", r["k"]]
                       + (["--node-limit", str(limit)] if limit else []), cwd=W / "root", capture_output=True, text=True, env=ENV)
    m = re.search(r"^RESULT queued=(\S+) cut=(\S+) free=(true|false)$", p.stdout, re.M)
    pure = re.findall(r"PURE_PLIES \{([^}]*)\}", p.stdout)
    gate = re.findall(r"GATE_PLIES \{([^}]*)\}", p.stdout)
    if p.returncode or not m or not pure:
        return {"error": p.stderr[-200:]}
    return {"queued": m[1], "cut": m[2], "free": m[3], "pure_plies": pure[-1].replace(" ", ""), "gate_plies": gate[-1].replace(" ", "") if gate else "",
            "stopped": "stopped at" in p.stdout, "limit": limit or 60000}
def one(r):
    x = run(r)
    if x.get("stopped") and x.get("queued") == "none" and x.get("cut") == "none":
        x = run(r, 600_000)
    return r, x
with ThreadPoolExecutor(4) as ex, open(OUT, "w") as f:
    f.write("step\tbot\tpairing\ti\tk\tgate_R\tqueued\tfree\tpure_plies\tgate_plies\tnode_limit\tstopped\terror\n")
    for r, x in ex.map(one, rows):
        f.write("\t".join([r["step"], r["bot"], r["pairing"], r["i"], r["k"], r["gate_R"], x.get("queued", ""), x.get("free", ""),
                           x.get("pure_plies", ""), x.get("gate_plies", ""), str(x.get("limit", "")), str(x.get("stopped", "")), x.get("error", "").replace("\n", " ")]) + "\n")
