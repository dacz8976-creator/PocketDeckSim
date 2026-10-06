"""Tool placements in the development run's games (Oct 6), with the Tool-placement rule's verdict on each: km3's own (its
560 games, both seats, replayed exactly) and kx3's at its own decisions (its 560 games, replayed exactly with its logged
moves, the km3 opponent playing itself). From dev_games/*_events.jsonl (engine/examples/trainer_habits.rs, `games` and
`scripted`). Run from the repository root: python3 rl/results/playout_tool_rule_2026-10-06/tool_placements.py
"""
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent / "dev_games"
for title, name, pilot in (("km3 in its own games", "km3_games_events.jsonl", "km3"), ("kx3 at its own decisions (arm X)", "kx3_games_events.jsonl", "kx3")):
    checks = [json.loads(l) for l in open(HERE / f"{name}.replay.jsonl", encoding="utf-8")]
    print(f"== {title}: {len(checks)} games, {sum(c['replayed_exactly'] for c in checks)} replayed exactly")
    rows = defaultdict(lambda: [0, 0, 0, set()])
    for line in open(HERE / name, encoding="utf-8"):
        e = json.loads(line)
        if e["kind"] not in ("tool", "tool_other"):
            continue
        side = f"the deck's side ({pilot})" if e["player"] == e["ctx"]["deck_seat"] else "the panel side (km3)"
        r = rows[(side, e["deck"], e["tool"])]
        r[0] += 1
        r[1] += not e["rule"]["has_effect"]
        r[2] += e["rule"]["rule_would_change"]
        if e["rule"]["rule_would_change"]:
            r[3].add(e["ctx"]["key"])
    print("| side | deck | Tool | placed | no effect where placed | the rule would place it elsewhere | in games |")
    print("|---|---|---|---|---|---|---|")
    for (side, deck, tool), (n, none, change, games) in sorted(rows.items()):
        print(f"| {side} | {deck} | {tool} | {n} | {none} | {change} | {len(games)} |")
    tot = [sum(v[i] for k, v in rows.items() if k[0].startswith("the deck")) for i in range(3)]
    print(f"\nthe deck's side, all Tools: {tot[0]} placed, {tot[1]} with no effect where placed, {tot[2]} the rule would have placed elsewhere\n")
