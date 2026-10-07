"""The 26 development-run decisions where kx3 left an attack km3 proposed (quiz 4 item 1's scan, the skip bar's 26), decided
again with the combined code (Oct 7, the fix round): kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64, and with
kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3 (no extension) to tell the extension's part from the Tool rule's. Both are
trainer_habits scripted --attack-scan on the development run's kx3 games (every game replayed exactly), from the game's
own observation and randomness. The game's own code (kx3_r16_c12_z2_real_t0_poolmeta) is the skip bar's scan,
../../playout_attack_skip_2026-10-07/attack_scan_poolmeta.jsonl, and the skip bar alone (_zs3) is its
attack_scan_poolmeta_zs3.jsonl.
- The 9 true skips: kx3 didn't attack later that turn in the game. "Kept" = the code plays km3's attack.
- The 17 attack-later moves: kx3 attacked later that turn in the game. "Touched" = the code plays something other than the
  game's move (km3's attack, or another move).
Run from the repository root:
  python3 rl/results/playout_close_calls_2026-10-07/combined/combined_scan.py"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP = HERE.parent.parent / "playout_attack_skip_2026-10-07"


def load(path):
    return {(r["key"], r["decision"]): r for r in map(json.loads, open(path, encoding="utf-8"))}


game = load(SKIP / "attack_scan_poolmeta.jsonl")
zs = load(SKIP / "attack_scan_poolmeta_zs3.jsonl")
tz = load(HERE / "attack_scan_poolmeta_tools_zs3.jsonl")
cm = load(HERE / "attack_scan_poolmeta_tools_zs3_m64.jsonl")
assert set(game) == set(zs) == set(tz) == set(cm), "the same decisions in every scan"
assert all(r["replayed_exactly"] for d in (game, zs, tz, cm) for r in d.values()), "every game replayed exactly"
games = {}
for l in open("rl/results/strength_2026-10-03_kx3_dev/games.jsonl", encoding="utf-8"):
    g = json.loads(l)
    games[g["key"]] = g
left = sorted(k for k, r in game.items() if not r["played_an_attack"])
print(f"decisions where km3 proposed an attack: {len(game)}; kx3 played something else: {len(left)}")


def choice(rec):
    """What the code played: 'game' (the game's move), 'attack' (km3's attack) or 'other' (another move)."""
    k = rec["kx3"]
    if k["chosen_equals_played"]:
        return "game"
    switched = k["reason"].startswith("play-outs:") or k["reason"].startswith("tie-break")
    assert switched or k["lead"] == 0, k["reason"]
    return "other" if switched else "attack"


def sd(k):
    return f"{k['lead'] / k['se']:.1f}" if k["se"] > 0 else "-"


def best(k):
    """The best candidate among those with the most rounds: label, lead over km3's attack, its SE ratio, rounds."""
    top = max(c[5] if len(c) > 5 else k["rounds"] for c in k["candidates"])
    live = [c for c in k["candidates"] if (c[5] if len(c) > 5 else k["rounds"]) == top]
    b = max(live, key=lambda c: c[1])  # ties: the first, km3's attack first
    return b[0], b[2], (f"{b[2] / b[3]:.1f}" if b[3] > 0 else "-"), top


rows = []
for key in left:
    log = games[key[0]]["log"]
    t = log[key[1]]["t"]
    later = any(e["a"].startswith("Attack:") for e in log[key[1] + 1:] if e["t"] == t)
    g, z, a, c = game[key]["kx3"], zs[key]["kx3"], tz[key]["kx3"], cm[key]["kx3"]
    extended = sum(1 for x in c["candidates"] if len(x) > 5 and x[5] > 16)
    rows.append(dict(
        key=key[0][:-2].replace("|", ", "), turn=t, km=game[key]["km"].split(":", 1)[1], played=game[key]["played"], later=later,
        reproduced=g["chosen_equals_played"], attacks=g["chosen_attacks_this_turn"], rounds=g["rounds"], lead=g["lead"], sd=sd(g),
        zs=choice(zs[key]), tz=choice(tz[key]), cm=choice(cm[key]), cm_rounds=c["rounds"], cm_extended=extended,
        cm_best=best(c), tz_best=best(a), cm_reason=c["reason"], tz_reason=a["reason"], cm_ms=c.get("ms"), tz_ms=a.get("ms"),
    ))
skips = [r for r in rows if not r["later"]]
lates = [r for r in rows if r["later"]]
print(f"  the 9 true skips (no attack later that turn in the game): {len(skips)}; the 17 attack-later moves: {len(lates)}")
for name, col in (("_zs3 (the skip bar's scan)", "zs"), ("_tools_zs3", "tz"), ("_tools_zs3_m64 (the combined code)", "cm")):
    kept = sum(r[col] == "attack" for r in skips)
    touched = [r for r in lates if r[col] != "game"]
    print(f"  {name}: true skips, km3's attack kept at {kept} of {len(skips)} "
          f"(the game's move at {sum(r[col] == 'game' for r in skips)}, another move at {sum(r[col] == 'other' for r in skips)}); "
          f"attack-later moves touched at {len(touched)} of {len(lates)} "
          f"(km3's attack at {sum(r[col] == 'attack' for r in touched)}, another move at {sum(r[col] == 'other' for r in touched)})")
ext = [r for r in rows if r["cm_rounds"] > 16]
print(f"  the combined code extended {len(ext)} of the 26 decisions to {sorted(set(r['cm_rounds'] for r in ext))} rounds; "
      f"time {sum(r['cm_ms'] for r in rows) / 1000:.0f} s, against {sum(r['tz_ms'] for r in rows) / 1000:.0f} s without the extension")
print()
name = {"game": "the game's move", "attack": "**km3's attack**", "other": "**another move**"}
print("| game (deck, opponent, deal, seat) | turn | km3's attack | kx3's move in the game | attacked later | its line attacks this turn | the game's lead (SE) | `_zs3` | `_tools_zs3` | `_tools_zs3_m64` | rounds (extended) | best at the end, lead (SE) |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in sorted(rows, key=lambda r: (r["later"], r["key"], r["turn"])):
    b = r["cm_best"]
    print(f"| {r['key']} | {r['turn']} | {r['km']} | {r['played']} | {'yes' if r['later'] else 'no'} | {r['attacks']} of {r['rounds']} | "
          f"{r['lead']:+.3f} ({r['sd']}){'' if r['reproduced'] else ', not reproduced'} | {name[r['zs']]} | {name[r['tz']]} | {name[r['cm']]} | "
          f"{r['cm_rounds']} ({r['cm_extended']}) | {b[0]} {b[1]:+.3f} ({b[2]}) |")
print()
print("The combined code's reasons, where it decided otherwise than the game or than _tools_zs3:")
for r in rows:
    if r["cm"] != "game" or r["cm"] != r["tz"]:
        print(f"- {r['key']} t{r['turn']} ({'attacked later' if r['later'] else 'true skip'}):")
        print(f"  - _tools_zs3: {r['tz_reason']}")
        print(f"  - _tools_zs3_m64: {r['cm_reason']}")
