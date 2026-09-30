"""The Victory Star repair's smoke check (Sept 30): compares the three scans' game files in this folder.
games_legacy_instr.jsonl  the engine without the repair (265ce95), instrumented scan
games_fixed_plain.jsonl   the repaired engine (6415e39's content), plain scan
games_fixed_instr.jsonl   the repaired engine, instrumented scan
All three: kog3 on both sides, 40 games, the scratch decks fire_victini.txt v psychic_confuse.txt, seeds 20,930,000,000 + i.
Usage: python3 compare.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
load = lambda v: {r["i"]: r for r in map(json.loads, open(HERE / f"games_{v}.jsonl"))}
old, plain, new = load("legacy_instr"), load("fixed_plain"), load("fixed_instr")
print(f"repaired engine, plain v instrumented scan: same moves in {sum(plain[i]['moves'] == new[i]['moves'] for i in plain)} of {len(plain)}")
for name, d in [("without the repair", old), ("with the repair", new)]:
    a = [r["vs_confused_attack"] for r in d.values()]
    c = [r["vs_confused_choice"] for r in d.values()]
    print(f"{name}: vs_confused_attack in {sum(x > 0 for x in a)} games ({sum(a)} attacks); "
          f"vs_confused_choice in {sum(x > 0 for x in c)} games ({sum(c)} choices)")
changed = [i for i in old if old[i]["moves"] != new[i]["moves"]]
print(f"games whose moves the repair changes: {len(changed)} of {len(old)}; "
      f"of them, with vs_confused_attack > 0 without the repair: {sum(old[i]['vs_confused_attack'] > 0 for i in changed)}")
