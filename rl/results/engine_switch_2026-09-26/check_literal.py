"""The literal check for the engine switch (see run_watch.sh). Reads the cloud's per-repair replays from its branch
and the laptop's instrumented 5b75bf9 games; prints one verdict line per check. Usage: python3 check_literal.py"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
BR = "origin/claude/pensive-ptolemy-spwc0b"
FIX = "rl/results/rules09_fixes_2026-09-26"


def load_lines(lines):
    return {(g["pairing"], g["i"]): g for g in map(json.loads, (l for l in lines if l.strip()))}


def cloud(commit, bot):
    out = subprocess.run(["git", "show", f"{BR}:{FIX}/{commit}_{bot}_500.jsonl"], cwd=HERE, capture_output=True,
                         text=True, check=True).stdout
    return load_lines(out.splitlines())


ok = True
for bot in ("k3", "kp3"):
    pre, pulse, promo = cloud("3102c9e", bot), cloud("5b75bf9", bot), cloud("5bab907", bot)
    watch = load_lines(open(os.path.join(HERE, f"watch_5b75bf9_{bot}_500.jsonl"), encoding="utf-8"))
    same = sum(watch[k]["moves"] == pulse[k]["moves"] for k in pulse)
    print(f"{bot}: instrumented 5b75bf9 equals the cloud's 5b75bf9 in {same} of {len(pulse)} games (moves)")
    ok &= same == len(pulse) == 14000
    for name, a, b, flag in (("Legendary Pulse (5b75bf9 v 3102c9e)", pre, pulse, "pulse"),
                             ("promotion timing (5bab907 v 5b75bf9)", pulse, promo, "eot_ko")):
        changed = [k for k in b if a[k]["moves"] != b[k]["moves"]]
        results = [k for k in changed if (a[k]["winner_seat"], a[k]["points"]) != (b[k]["winner_seat"], b[k]["points"])]
        unexplained = [k for k in changed if watch[k][flag] == 0]
        fired = sum(1 for k in watch if watch[k][flag] > 0)
        print(f"  {name}: {len(changed)} games changed ({len(results)} results); mechanic fired in "
              f"{len(changed) - len(unexplained)} of them; games where it fired at all: {fired}")
        if unexplained:
            ok = False
            print(f"    NOT REACHING THE MECHANIC: {len(unexplained)}, e.g. " +
                  ", ".join(f"pairing {p} deal {i} seed {b[(p, i)]['seed']}" for p, i in unexplained[:8]))
print("LITERAL CHECK PASS" if ok else "LITERAL CHECK FAIL")
sys.exit(0 if ok else 1)
