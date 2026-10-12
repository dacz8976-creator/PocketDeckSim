#!/usr/bin/env python3
"""Writes the thinking-time test's four strength_prereg.py configs (two settings x two seed slices) from the combined run's config, and
checks that every planned (deck, opponent, deal, seat) key gets the development run's own seed. Run from the repository root."""
import json, sys, os

R = "rl/results"
comb = json.load(open(f"{R}/strength_2026-10-08_kx3_combined/config.json"))
dev_man = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/manifest.json"))
dev_games = [json.loads(l) for l in open(f"{R}/strength_2026-10-03_kx3_dev/games.jsonl") if l.strip().endswith("}")]
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

decks = comb["decks"] if isinstance(comb["decks"], list) else json.loads(comb["decks"].replace("'", '"'))
dev_decks = [d["name"] for d in dev_man["decks"]]
assert decks == dev_decks, (decks, dev_decks)
assert dev_decks[3] == "03-wailord-indeedee-wall"
opps = comb["opponents"]
assert [o["name"] for o in dev_man["opponents"]] == opps
base, stride = dev_man["seed_base"], dev_man["pair_stride"]
assert (base, stride, dev_man["deals"]) == (24400000000, 10000, 5), (base, stride)
print("frozen pilot (the dev run's):", dev_man["pilot"])

SLICES = {"a": (dev_decks[0:3], base), "b": (dev_decks[4:7], base + 4 * 1000 * stride)}
ARMS = {"m32": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32", "m16": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3"}

# the dev run's seed per key, and the seed each slice's manifest would give it (rl/strength/src/main.rs: seed_base + (di*1000 + oi)*stride + deal)
dev_seed = {(g["deck"], g["opp"], g["deal"], g["seat"], g["arm"]): g["seed"] for g in dev_games}
checked = 0
for s, (dl, sb) in SLICES.items():
    for di, d in enumerate(dl):
        for oi, o in enumerate(opps):
            for deal in range(5):
                for seat in (0, 1):
                    for arm in ("ref", "X"):
                        want = dev_seed[(d, o, deal, seat, arm)]
                        got = sb + (di * 1000 + oi) * stride + deal
                        assert got == want, (s, d, o, deal, seat, arm, got, want)
                        checked += 1
print(f"seeds: {checked} of {checked} keys get the dev run's seed (480 kx3 + 480 km3 per setting)")

for an, pilot in ARMS.items():
    for s, (dl, sb) in SLICES.items():
        c = {k: comb[k] for k in ("reference", "deals", "seats", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines",
                                  "program", "program_sha256", "engine", "reference_provenance")}
        c.update({
            "name": f"kx3_think_{an}_{s}",
            "question": (f"THE THINKING-TIME TEST, setting {an}, slice {s} (coordinator, Oct 11; PLAN.md in rl/results/thinking_time_2026-10/). "
                         f"How much of the combined candidate's gain over the frozen kx3 does kx3 with `_tools _zs3` and "
                         + ("close calls extended to 32 play-outs (`_m32`, not 64)" if an == "m32" else "no close-call extension (16 play-outs)")
                         + f" keep, on the development decks without Wailord (Dustin, Oct 10)? This slice: {', '.join(dl)}, seed_base {sb} "
                         "(each key gets the development run's own seed). PRIMARY and the reading are fixed in PLAN.md before any game."),
            "pilot": pilot, "stage": "dev", "decks": dl, "opponents": opps, "seed_base": sb,
            "pilot_provenance": (f"{pilot} from claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219: the combined candidate's code "
                                 f"(_tools _zs3) with " + ("R_max 32" if an == "m32" else "no _m (no extension)")
                                 + "; the same program as the combined run (the suffixes are the pilot code's parameters)"),
        })
        p = f"{OUT}/config_{an}_{s}.json"
        json.dump(c, open(p, "w"), indent=1)
        open(p, "a").write("\n")
        print("wrote", p, pilot, sb, dl)
