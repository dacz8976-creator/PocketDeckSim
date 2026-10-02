#!/usr/bin/env python3
"""Runs the score dump (print-only patched bots, --tree) for the 5 unexplained lookahead games and the judgment game on three programs, all at
the first differing tick: the old engine; R; and R with the queued attack-damage choice at a coin target reverted to the plain ApplyDamage for
that one decision (--revert-queued, the VAR build). Writes out/dump_<bot>_p<pairing>_i<deal>_<program>.txt and prints, per game, the candidates'
scores on the three programs, the gate lines (PGGATE: the bot's own search entered a pure queued attack-damage frame at a coin Pokemon) per
candidate, and the principal line under the candidate whose score differs."""
import csv, re, subprocess, sys
from pathlib import Path

W = Path("/home/dacz8976/c8c")
OUT = W / "out"
rows = {(r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t") if r["step"] == "8"}
GAMES = [("k3", 4, 7, 95), ("km3", 1, 399, 81), ("km3", 4, 7, 84), ("km3", 4, 360, 57), ("km3", 21, 310, 87), ("km3", 4, 106, 82)]
PROGS = [("old", "old", []), ("R", "new", []), ("R-revert", "var", ["--revert-queued"])]
only = [a for a in sys.argv[1:] if not a.startswith("--")]
if only:
    GAMES = [g for g in GAMES if f"{g[0]}:{g[1]}:{g[2]}" in only]


def dump(prog, binary, flags, bot, pairing, deal, tick):
    r = rows[(bot, pairing, deal)]
    p = subprocess.run(["nice", "-n", "19", str(W / "dg" / f"score_dump_{binary}"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                        "--seed-base", "23100000000", "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick), "--tree"] + flags,
                       cwd=W / "dg" / binary / "engine", capture_output=True, text=True)
    text = p.stdout + p.stderr
    (OUT / f"dump_{bot}_p{pairing}_i{deal}_{prog}.txt").write_text(text, encoding="utf-8")
    return text


def parse(text):
    """The asked decision's candidates [(score, action)], the gate lines per candidate action, the principal line per candidate, the chosen line."""
    lines = text.splitlines()
    chosen = next((ln for ln in lines if ln.startswith("deal ")), "")      # stdout comes first in the joined text
    start = max((i for i, ln in enumerate(lines) if ln.startswith("PGTICK") and "asked about" in ln), default=0)
    lines = lines[start:]
    cands, gates, cur = [], {}, None
    trees, tcur = {}, None
    for ln in lines:
        if ln.startswith("PGCAND "):
            cur = ln[7:]
            gates.setdefault(cur, [])
        elif ln.startswith("PGGATE") and cur is not None:
            gates[cur].append(ln[7:])
        elif re.match(r"PGDUMP\s+(-?[\d.eE+-]+) ", ln):
            m = re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", ln)
            cands.append((float(m[1]), m[2]))
        elif ln.startswith("PGTREE candidate "):
            tcur = int(ln.split()[-1])
            trees[tcur] = []
        elif ln.startswith("PGTREE") and tcur is not None:
            trees[tcur].append(ln[7:])
    return cands, gates, trees, chosen


for bot, pairing, deal, tick in GAMES:
    res = {prog: parse(dump(prog, binary, flags, bot, pairing, deal, tick)) for prog, binary, flags in PROGS}
    print("=" * 112)
    print(f"{bot} pairing {pairing} deal {deal} tick {tick}: {Path(rows[(bot, pairing, deal)]['held_file']).stem} v {Path(rows[(bot, pairing, deal)]['panel_file']).stem}")
    for prog, _, _ in PROGS:
        print(f"  {prog:9} {res[prog][3]}")
    o, n, v = res["old"][0], res["R"][0], res["R-revert"][0]
    print(f"  R-revert scores equal old's: {len(o) == len(v) and all(abs(a[0] - b[0]) < 1e-9 for a, b in zip(o, v))};   R's equal old's: {len(o) == len(n) and all(abs(a[0] - b[0]) < 1e-9 for a, b in zip(o, n))}")
    for i, ((so, a), (sn, _), (sv, _)) in enumerate(zip(o, n, v)):
        flag = "" if abs(so - sn) < 1e-9 else "   <-- R differs from old"
        print(f"    old {so:>15.4f}   R {sn:>15.4f}   R-revert {sv:>15.4f}   {a[:84]}{flag}")
        for prog in ("old", "R", "R-revert"):
            g = res[prog][1].get(a, [])
            if g:
                print(f"        gate in {prog}: {len(g)} x, e.g. {g[0][:170]}")
    for i, ((so, a), (sn, _)) in enumerate(zip(o, n)):
        if abs(so - sn) >= 1e-9:
            for prog in ("old", "R"):
                print(f"  --- principal line under '{a[:60]}' in {prog}:")
                for ln in res[prog][2].get(i, [])[:26]:
                    print("     " + ln[:190])
