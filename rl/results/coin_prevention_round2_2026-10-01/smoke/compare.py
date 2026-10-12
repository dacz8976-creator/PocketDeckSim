"""The later round's smoke check (Oct 1): compares the three scans' game files in this folder (run_smoke.sh).
games_r_plain.jsonl        R (1abdbe8), plain scan
games_round2_plain.jsonl   this branch's engine, plain scan
games_round2_watch.jsonl   this branch's engine, with the coin counters (instrument_scan.py)
km3 on both sides, 40 games a pairing, seeds 20,980,000,000 + pairing x 10,000 + i. Pairing 0 is water_round2 v
meowth_carefree (Carefree Steps in play, so the repaired code can run); pairing 1 is water_round2 v fire_heatmor (no
coin-flip damage Ability in play, so every game must be identical).
Usage: python3 compare.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
load = lambda v: {(r["pairing"], r["i"]): r for r in map(json.loads, open(HERE / f"games_{v}.jsonl"))}
old, plain, watch = load("r_plain"), load("round2_plain"), load("round2_watch")
EXACT = ["coin_cut_recorded", "coin_full_prevention", "coin_queued_offered", "offgate_helper_choice",
         "offgate_discard_then_damage"]
count = lambda v: v["n"] if isinstance(v, dict) else v

same = sum(plain[k]["moves"] == watch[k]["moves"] for k in plain)
print(f"this branch, plain v watch scan (the counters change no play): same moves in {same} of {len(plain)}")
for p, name in [(0, "water_round2 v meowth_carefree"), (1, "water_round2 v fire_heatmor")]:
    keys = sorted(k for k in old if k[0] == p)
    changed = [k[1] for k in keys if old[k]["moves"] != plain[k]["moves"]]
    print(f"\npairing {p}, {name}: games whose moves this round changes, R v this branch: {len(changed)} of {len(keys)}"
          + (f": {changed}" if changed else ""))
    for c in EXACT + ["coin_defender_attack"]:
        n = [count(watch[k][c]) for k in keys]
        print(f"  {c}: fires in {sum(x > 0 for x in n)} games ({sum(n)} ticks)")
    offered = [k[1] for k in keys if count(watch[k]["coin_queued_offered"]) > 0]
    print(f"  changed games with no queued coin-path choice offered on the board (lookahead only; to trace): "
          f"{[i for i in changed if i not in offered]}")
    print(f"  games with one offered that did not change (the coin went the old way, or the bot chose another): "
          f"{[i for i in offered if i not in changed]}")
