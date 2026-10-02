"""The coin-flip prevention repair's smoke check (Sept 30): compares the three scans' game files in this folder.
games_legacy_instr.jsonl  the engine without the repair (d21511a), instrumented scan
games_fixed_plain.jsonl   the repaired engine (5942d1a's content), plain scan
games_fixed_instr.jsonl   the repaired engine, instrumented scan
All three: kog3 on both sides, 40 games, the scratch decks fire_heatmor.txt v meowth_carefree.txt, seeds 20,950,000,000 + i.
Usage: python3 compare.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
load = lambda v: {r["i"]: r for r in map(json.loads, open(HERE / f"games_{v}.jsonl"))}
old, plain, new = load("legacy_instr"), load("fixed_plain"), load("fixed_instr")
print(f"repaired engine, plain v instrumented scan: same moves in {sum(plain[i]['moves'] == new[i]['moves'] for i in plain)} of {len(plain)}")
for name, d in [("without the repair", old), ("with the repair", new)]:
    a = [r["coin_defender_attack"] for r in d.values()]
    q = [r["coin_queued_attack_damage"] for r in d.values()]
    print(f"{name}: coin_defender_attack in {sum(x > 0 for x in a)} games ({sum(a)} moves); "
          f"coin_queued_attack_damage in {sum(x > 0 for x in q)} games ({sum(q)} moves)")
changed = [i for i in old if old[i]["moves"] != new[i]["moves"]]
onboard = [i for i in changed if new[i]["coin_queued_attack_damage"] > 0]
print(f"games whose moves the repair changes: {len(changed)} of {len(old)}: {changed}")
print(f"  with a snipe at Meowth redirected on the board: {len(onboard)}: {onboard}")
print(f"  without one (not traced): {[i for i in changed if i not in onboard]}")
print(f"games with a redirected snipe that did not change: {[i for i in new if new[i]['coin_queued_attack_damage'] > 0 and i not in changed]}")
