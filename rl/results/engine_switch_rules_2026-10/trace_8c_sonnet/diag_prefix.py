#!/usr/bin/env python3
"""The two prefix games: the vs_probe (repair A) and coin_probe at the attack tick (the last tick both games share, where the old game ends), and the
final ticks of both games' records (who wins, with what points). Output goes to stdout."""
import csv, subprocess
from pathlib import Path

W = Path("/home/dacz8976/c8c")
rows = {(r["bot"], int(r["pairing"]), int(r["i"])): r for r in csv.DictReader(open(W / "handoff_8c.tsv", encoding="utf-8"), delimiter="\t") if r["step"] == "8"}
for bot, pairing, deal, tick in [("k3", 31, 81, 71), ("km3", 31, 12, 47)]:
    r = rows[(bot, pairing, deal)]
    print("=" * 100)
    print(f"{bot} p{pairing} i{deal}: {Path(r['held_file']).stem} v {Path(r['panel_file']).stem}; old winner {r['old_winner']} points {r['old_points']}; R winner {r['new_winner']} points {r['new_points']}")
    for name, exe, cwd in (("vs_probe", "bin_new_vs_probe", "new"), ("coin_probe", "bin_probe_coin_probe", "probe")):
        out = subprocess.run(["nice", "-n", "19", str(W / exe), "--a", str(W / "root" / r["held_file"]), "--b", str(W / "root" / r["panel_file"]), "--seed-base", "23100000000",
                              "--pairing", str(pairing), "--bot", bot, "--deal", str(deal), "--tick", str(tick)], cwd=W / cwd / "engine", capture_output=True, text=True)
        print(f"  {name} at tick {tick} (the attack tick):")
        for ln in (out.stdout + out.stderr).splitlines():
            print("    " + ln[:200])
