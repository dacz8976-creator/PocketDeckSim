"""Summarise /home/dacz8976/trainer_audit/games.jsonl (kp3 on both sides, 36 decks x 8 opponents x 2 seats x 15).

Writes audit_trainers.tsv (per deck and Trainer card: offered turns, played turns, rate) and audit_tools.tsv (per deck
and Tool: attachments, attached to a holder that never met the Tool's condition, never had a window, never worked),
and prints the headline tables.
Usage: analyze_audit.py GAMES.jsonl OUTDIR
"""
import collections
import json
import os
import sys

games, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
tr = collections.defaultdict(lambda: collections.Counter())
tools = collections.defaultdict(lambda: collections.Counter())
holders = collections.defaultdict(collections.Counter)  # (deck, tool) -> holder names where the condition never held
n_games = collections.Counter()
for line in open(games):
    g = json.loads(line)
    d = g["deck"]
    n_games[d] += 1
    for name, t in g["trainers"].items():
        c = tr[(d, name)]
        c["kind:" + str(t["kind"])] = 1
        c["games_offered"] += t["offered"] > 0
        c["offered"] += t["offered"]
        c["offered_free"] += t["offered_no_other_supporter"]
        c["played"] += t["played"]
        c["games_played"] += t["played"] > 0
    for e in g["tool_episodes"]:
        c = tools[(d, e["tool"])]
        c["attached"] += 1
        c["inelig_at_attach"] += not e["eligible_at_attach"]
        c["never_eligible"] += not e["ever_eligible"]
        c["no_window"] += e["windows"] == 0
        c["never_worked"] += e["windows"] > 0 and e["worked"] == 0
        c["worked_some"] += e["worked"] > 0
        if not e["ever_eligible"]:
            holders[(d, e["tool"])][e["holder"] + ("->" + "/".join(e["evolved_into"]) if e["evolved_into"] else "")] += 1

with open(os.path.join(outdir, "audit_trainers.tsv"), "w") as f:
    f.write("deck\tcard\tkind\tgames\tgames_offered\tgames_played\toffered_turns\toffered_turns_free\tplayed_turns\tplay_rate\n")
    for (d, name), c in sorted(tr.items()):
        kind = next((k[5:] for k in c if k.startswith("kind:")), "")
        denom = c["offered_free"] if kind == "Supporter" else c["offered"]
        rate = c["played"] / denom if denom else 0
        f.write(f"{d}\t{name}\t{kind}\t{n_games[d]}\t{c['games_offered']}\t{c['games_played']}\t{c['offered']}\t"
                f"{c['offered_free']}\t{c['played']}\t{rate:.3f}\n")
with open(os.path.join(outdir, "audit_tools.tsv"), "w") as f:
    f.write("deck\ttool\tattached\tinelig_at_attach\tnever_eligible\tno_window\tnever_worked\tworked_some\tnever_eligible_holders\n")
    for (d, t), c in sorted(tools.items()):
        hs = ", ".join(f"{h} x{n}" for h, n in holders[(d, t)].most_common(6))
        f.write(f"{d}\t{t}\t{c['attached']}\t{c['inelig_at_attach']}\t{c['never_eligible']}\t{c['no_window']}\t"
                f"{c['never_worked']}\t{c['worked_some']}\t{hs}\n")

print("games per deck:", min(n_games.values()), "-", max(n_games.values()), "| decks:", len(n_games))
print("\n== Tools: attachments whose holder never met the Tool's condition (wasted), by deck ==")
rows = sorted(tools.items(), key=lambda kv: -kv[1]["never_eligible"] / max(1, kv[1]["attached"]))
for (d, t), c in rows:
    if c["attached"] >= 5:
        print(f"{d:48s} {t:20s} attached {c['attached']:5d}  never-eligible {c['never_eligible']:5d} "
              f"({100 * c['never_eligible'] / c['attached']:5.1f}%)  never worked w/ window {c['never_worked']:5d}  "
              f"| {', '.join(f'{h} x{n}' for h, n in holders[(d, t)].most_common(4))}")
print("\n== Trainers offered in >=30 games but played on <15% of offered turns ==")
for (d, name), c in sorted(tr.items()):
    kind = next((k[5:] for k in c if k.startswith("kind:")), "")
    denom = c["offered_free"] if kind == "Supporter" else c["offered"]
    if c["games_offered"] >= 30 and denom and c["played"] / denom < 0.15:
        print(f"{d:48s} {name:24s} {kind:10s} offered in {c['games_offered']:4d} games, {denom:5d} turns; "
              f"played {c['played']:4d} ({100 * c['played'] / denom:4.1f}%)")
