"""The skip bar (`_zs3`, Oct 7) at the 26 development-run decisions where kx3 left an attack km3 proposed (quiz 4 item 1's
scan). Both runs are trainer_habits scripted --attack-scan on the development run's kx3 games (every game replayed
exactly): attack_scan_poolmeta.jsonl with the run's code (kx3_r16_c12_z2_real_t0_poolmeta), which now also gives every
candidate's count of play-outs that attack before the turn ends; attack_scan_poolmeta_zs3.jsonl with the skip bar on.
"In the game" is what kx3 itself did after the switch (from the run's log); "in the play-outs" is the candidate's own line
(km3 continuing), which is what the bar reads. Run from the repository root:
  python3 rl/results/playout_attack_skip_2026-10-07/skip_scan.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
plain = {(r["key"], r["decision"]): r for r in map(json.loads, open(HERE / "attack_scan_poolmeta.jsonl", encoding="utf-8"))}
zs = {(r["key"], r["decision"]): r for r in map(json.loads, open(HERE / "attack_scan_poolmeta_zs3.jsonl", encoding="utf-8"))}
assert set(plain) == set(zs) and all(r["replayed_exactly"] for r in list(plain.values()) + list(zs.values()))
games = {}
for l in open("rl/results/strength_2026-10-03_kx3_dev/games.jsonl", encoding="utf-8"):
    g = json.loads(l)
    games[g["key"]] = g
left = sorted((k for k, r in plain.items() if not r["played_an_attack"]), key=lambda k: k)
print(f"decisions where km3 proposed an attack: {len(plain)}; kx3 played something else: {len(left)}")
rows = []
for k in left:
    p, z = plain[k], zs[k]
    log = games[k[0]]["log"]
    t = log[k[1]]["t"]
    later = any(e["a"].startswith("Attack:") for e in log[k[1] + 1:] if e["t"] == t)
    kp, kz = p["kx3"], z["kx3"]
    reproduced = kp["chosen_equals_played"]
    attacks = kp["chosen_attacks_this_turn"]
    rounds = kp["rounds"]
    keeps = reproduced and not kz["chosen_equals_played"]
    rows.append(dict(key=k[0][:-2].replace("|", ", "), turn=t, km=p["km"].split(":", 1)[1], played=p["played"], later=later,
                     attacks=attacks, rounds=rounds, reproduced=reproduced, keeps=keeps, lead=kp["lead"], se=kp["se"],
                     reason=kz["reason"]))
skips = [r for r in rows if not r["later"]]
lates = [r for r in rows if r["later"]]
print(f"  in the game, no attack that turn (the 9 true skips): {len(skips)}; an attack later that turn: {len(lates)}")
for name, group in (("true skips", skips), ("attacked later in the game", lates)):
    print(f"  {name}: the skip bar keeps km3's attack at {sum(r['keeps'] for r in group)}; "
          f"the line attacks this turn in most play-outs at {sum(r['attacks'] * 2 >= r['rounds'] for r in group if r['reproduced'])} "
          f"(of {sum(r['reproduced'] for r in group)} that reproduce)")
print()
print("| game (deck, opponent, deal, seat) | turn | km3's attack | kx3's move | attacked later in the game | its line attacks this turn (play-outs) | lead (SE) | with `_zs3` |")
print("|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r: (r["later"], -r["keeps"], r["key"])):
    sd = f"{r['lead'] / r['se']:.1f}" if r["se"] > 0 else "-"
    verdict = "(not reproduced)" if not r["reproduced"] else ("attack kept" if r["keeps"] else "switch stands")
    print(f"| {r['key']} | {r['turn']} | {r['km']} | {r['played']} | {'yes' if r['later'] else 'no'} | "
          f"{r['attacks']} of {r['rounds']} | {r['lead']:+.3f} ({sd}) | {verdict} |")
print()
print("The skip bar's reasons where it decided differently, or the line skipped the attack:")
for r in rows:
    if r["keeps"] or (r["reproduced"] and r["attacks"] * 2 < r["rounds"]):
        print(f"- {r['key']} t{r['turn']}: {r['reason']}")
