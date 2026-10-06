"""Quiz 4, item 1: where kx3 left an attack km3 proposed, in the development run's kx3 games (attack_scan.jsonl, from
trainer_habits scripted --attack-scan with the run's kx3, kx3_r16_c12_z2_real_t0_poolmeta), and what the attack bar does
there: worked out from each decision's lead and standard error, and checked against kx3 deciding again with the bar on
(attack_scan_za3.jsonl, the same scan with kx3_r16_c12_z2_real_t0_poolmeta_za3). Run from the repository root:
  python3 rl/results/playout_quiz4_items_2026-10-06/attack_bar/attack_scan.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rs = [json.loads(l) for l in open(HERE / "attack_scan.jsonl", encoding="utf-8")]
za3 = {(r["key"], r["decision"]): r for r in map(json.loads, open(HERE / "attack_scan_za3.jsonl", encoding="utf-8"))}
assert set(za3) == {(r["key"], r["decision"]) for r in rs} and all(r["replayed_exactly"] for r in za3.values())
games = {}
for l in open("rl/results/strength_2026-10-03_kx3_dev/games.jsonl", encoding="utf-8"):
    g = json.loads(l)
    games[g["key"]] = g
key = json.load(open("rl/results/blind_quiz4_2026-10-06/answer_key_q4.json", encoding="utf-8"))
quiz = {}
for q, v in key.items():
    if q.startswith("Q"):
        quiz[(f"{v['deck']}|{v['opponent']}|{(v['seed'] - 24400000000) % 10000}|{v['seat']}|X", v["decision"])] = q

left = [r for r in rs if not r["played_an_attack"]]
print(f"kx3's games: {len(games) // 2} deals x seats; decisions where km3 (asked with the game's own search randomness) proposes an attack: {len(rs)}"
      f" (every game replayed exactly: {all(r['replayed_exactly'] for r in rs)})")
print(f"kx3 played an attack there: {len(rs) - len(left)}; something else: {len(left)} ({100 * len(left) / len(rs):.1f}%)")
rows = []
for r in left:
    g = games[r["key"]]
    log, k = g["log"], r["decision"]
    t = log[k]["t"]
    later = any(e["a"].startswith("Attack:") for e in log[k + 1:] if e["t"] == t)
    kx = r["kx3"]
    sd = kx["lead"] / kx["se"] if kx["se"] > 0 else float("inf")
    stopped = kx["chosen_equals_played"] and sd <= 3.0
    ref = games[r["key"][:-1] + "ref"]
    # With the bar on, kx3 decides again from the same randomness: it keeps km3's attack exactly where worked out.
    on = za3[(r["key"], k)]["kx3"]
    if kx["chosen_equals_played"]:
        assert (not on["chosen_equals_played"]) == stopped and on["reason"].startswith("the attack bar") == stopped, (r["key"], k, on["reason"])
    rows.append((r, t, later, kx, sd, stopped, g["winner"], ref["winner"], quiz.get((r["key"], k), "")))
print(f"  of those, kx3 attacked later in the same turn: {sum(x[2] for x in rows)}; no attack that turn: {sum(not x[2] for x in rows)}")
print(f"  a fresh kx3 at that decision plays what the log says: {sum(x[3]['chosen_equals_played'] for x in rows)} of {len(rows)}")
print(f"  with the attack bar at 3 standard errors, the attack would be kept: {sum(x[5] for x in rows)}; the switch would stand: "
      f"{sum(x[3]['chosen_equals_played'] and not x[5] for x in rows)}")
print("  kx3 deciding again with the bar on (attack_scan_za3.jsonl) agrees at every one of them")
skip = [x for x in rows if not x[2]]
print(f"  of the {len(skip)} with no attack that turn: kept by the bar {sum(x[5] for x in skip)}")
later = [x for x in rows if x[2] and x[5]]
print(f"  of the {sum(x[5] for x in rows)} the bar keeps, {len(later)} are a move before the attack (kx3 attacked later that turn): "
      + ", ".join(sorted({x[0]['played'].split(':')[0] + (':' + x[0]['played'].split(':')[1] if x[0]['played'].startswith('Play:') else '') for x in later})))
for name, group in (("no attack that turn", skip), ("attacked later that turn", [x for x in rows if x[2]])):
    gs = {x[0]["key"]: x for x in group}
    print(f"  games with a switch {name}: {len(gs)}; kx3 won {sum(x[6] == 'deck' for x in gs.values())}, "
          f"km3 won the same deal {sum(x[7] == 'deck' for x in gs.values())}")
print()
print("| game (deck, opponent, deal, seat) | turn | km3's attack | kx3's move | attacked later this turn | kx3's lead (SE) | with `_za3` | kx3's game | km3's game | quiz |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r, t, later, kx, sd, stopped, xw, rw, q in sorted(rows, key=lambda x: (x[2], x[4])):
    verdict = "attack kept" if stopped else ("switch stands" if kx["chosen_equals_played"] else "(not reproduced)")
    sds = f"{sd:.1f}" if sd != float("inf") else "-"
    print(f"| {r['key'][:-2].replace('|', ', ')} | {t} | {r['km'].split(':', 1)[1]} | {r['played']} | {'yes' if later else 'no'} | {kx['lead']:+.3f} ({sds}) | {verdict} | {xw} | {rw} | {q} |")
