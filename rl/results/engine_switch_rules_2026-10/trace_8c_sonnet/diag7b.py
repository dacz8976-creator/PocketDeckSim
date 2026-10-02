#!/usr/bin/env python3
"""For the 5 unexplained lookahead games and the judgment game: the board at the first differing tick (names, HP, Energy of both sides, with the
coin Ability Pokemon marked) and the existing coin_probe's own output (its printed paths), to see how it counted plies."""
import csv, gzip, json, subprocess, sys, tempfile
from pathlib import Path

W = Path("/home/dacz8976/c8c")
sys.path.insert(0, str(W / "tools"))
from tightened_rule import load_trace  # noqa: E402

GAMES = [("k3", 4, 7, 95), ("km3", 1, 399, 81), ("km3", 4, 7, 84), ("km3", 4, 360, 57), ("km3", 21, 310, 87), ("km3", 4, 106, 82)]
COIN = ("Bastiodon", "Hisuian Goodra", "Togekiss", "Meowth")
rows = {(r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t") if r["step"] == "8"}

for bot, pairing, deal, tick in GAMES:
    r = rows[(bot, pairing, deal)]
    out = subprocess.run(["nice", "-n", "19", str(W / "bin_new_vs_trace"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                          "--seed-base", "23100000000", "--pairing", str(pairing), "--bot", bot, "--deals", str(deal)],
                         cwd=W / "new" / "engine", capture_output=True, text=True, check=True).stdout
    p = Path(tempfile.mkdtemp()) / "t.jsonl.gz"
    with gzip.open(p, "wt") as f:
        f.write(out)
    games, _ = load_trace(p)
    rec = games[deal][tick]
    first_seat = 0 if deal % 2 == 0 else 1
    names = {0: Path(r["held_file"] if first_seat == 0 else r["panel_file"]).stem, 1: Path(r["panel_file"] if first_seat == 0 else r["held_file"]).stem}
    print("=" * 100)
    print(f"{bot} p{pairing} i{deal} tick {tick}: seat 0 = {names[0]}, seat 1 = {names[1]}; mover seat {rec['actor']}, turn {rec['turn']}; facts {rec['facts']}")
    for seat in (0, 1):
        mons = rec["board"][f"p{seat}"]
        marked = [m + ("   <== coin Ability" if any(c in m for c in COIN) else "") for m in mons]
        print(f"  seat {seat} ({names[seat]}): " + " | ".join(marked))
    cp = subprocess.run(["nice", "-n", "19", str(W / "bin_probe_coin_probe"), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]),
                         "--seed-base", "23100000000", "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)],
                        cwd=W / "probe" / "engine", capture_output=True, text=True)
    print("  coin_probe says:")
    for ln in (cp.stdout + cp.stderr).splitlines():
        print("    " + ln[:230])
