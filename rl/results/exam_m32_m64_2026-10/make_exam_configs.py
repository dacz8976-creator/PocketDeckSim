#!/usr/bin/env python3
"""Writes the held-out exam's two strength_prereg.py configs (m32 and m64, PLAN.md) and checks, before any game, that they replay the Oct 5
exam's deals: the same 11 held-out decks in the same order, the same 8 opponents in the same order, every deck and opponent file unchanged
(sha256 against the Oct 5 manifest), and every planned (deck, opponent, deal, seat, arm) key given the Oct 5 exam's own seed by the harness's
formula (rl/strength/src/main.rs: seed_base + (deck index x 1000 + opponent index) x stride + deal). Run from the repository root."""
import hashlib, json, os, sys

R = "rl/results"
exam_cfg = json.load(open(f"{R}/strength_2026-10-05_kx3_exam/config.json"))
exam_man = json.load(open(f"{R}/strength_2026-10-05_kx3_exam/manifest.json"))
exam_games = [json.loads(l) for l in open(f"{R}/strength_2026-10-05_kx3_exam/games.jsonl") if l.strip().endswith("}")]
comb = json.load(open(f"{R}/strength_2026-10-08_kx3_combined/config.json"))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


decks = [d["name"] for d in exam_man["decks"]]
opps = [o["name"] for o in exam_man["opponents"]]
assert decks == exam_cfg["decks"] and len(decks) == 11, decks
assert len(opps) == 8, opps
held = json.load(open("rl/strength/heldout.json"))["decks"]
assert sorted(decks) == sorted(held), (decks, held)
for e in exam_man["decks"] + exam_man["opponents"]:
    now = sha256_file(e["path"])
    assert now == e["sha256"], (e["name"], e["path"], now[:12], e["sha256"][:12])
print(f"deck files: {len(exam_man['decks'])} held-out decks and {len(exam_man['opponents'])} opponents unchanged since the Oct 5 exam (sha256)")

base, stride, deals = exam_man["seed_base"], exam_man["pair_stride"], exam_man["deals"]
assert (base, stride, deals, exam_man["seats"]) == (24500000000, 10000, 3, [0, 1]), (base, stride, deals)
exam_seed = {g["key"]: g["seed"] for g in exam_games}
assert len(exam_seed) == 1056, len(exam_seed)
checked = 0
for di, d in enumerate(decks):
    for oi, o in enumerate(opps):
        for deal in range(deals):
            for seat in (0, 1):
                for arm in ("ref", "X"):
                    key = f"{d}|{o}|{deal}|{seat}|{arm}"
                    got = base + (di * 1000 + oi) * stride + deal
                    assert got == exam_seed[key], (key, got, exam_seed[key])
                    checked += 1
print(f"seeds: {checked} of {checked} keys get the Oct 5 exam's seed (528 kx3 + 528 km3 per setting)")

ARMS = {"m32": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m32", "m64": "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64"}
assert comb["pilot"] == ARMS["m64"], comb["pilot"]
for an, pilot in ARMS.items():
    c = {k: exam_cfg[k] for k in ("deals", "seats", "seed_base", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines")}
    c.update({k: comb[k] for k in ("reference", "program", "program_sha256", "engine")})
    c["engine"] += ("; this program predates rules switch 2 (the official program since Oct 12 is rl/engine-2026-10-12): the exam runs on "
                    "the Oct 5 exam's rules on purpose, so that its games pair with the frozen kx3's (PLAN.md)")
    c.update({
        "name": f"kx3_exam_{an}",
        "question": (f"THE HELD-OUT EXAM OF m32 AND m64, setting {an} (Dustin, Oct 13, with Astra's conditions; PLAN.md in "
                     "rl/results/exam_m32_m64_2026-10/). Does kx3 with `_tools _zs3` and close calls extended to "
                     + ("32 play-outs (`_m32`)" if an == "m32" else "64 play-outs (`_m64`, the combined candidate)")
                     + " play Dustin's 11 held-out decks better than the frozen kx3, on the Oct 5 exam's own deals (seed_base 24500000000, "
                     "3 deals, both seats, the 8 panel lists), and is m64's extra time bought with better play than m32's? Both settings play the "
                     "same deals; each game pairs by key with the other setting's, the frozen kx3's and km3's Oct 5 exam games. PRIMARY and the "
                     "selection rule are fixed in PLAN.md before any game."),
        "pilot": pilot, "stage": "heldout", "decks": decks, "opponents": opps,
        "pilot_provenance": (f"{pilot} from claude/playout-pilot 172cbe9ce0f2cb7946b489422b56d3fce5ca6219: the combined candidate's code "
                             "(_tools _zs3) with R_max " + an[1:] + "; the same program as the combined run and the thinking-time test "
                             "(the suffixes are the pilot code's parameters)"),
        "reference_provenance": ("km3 in the same build; it must equal the pinned km3 (self-check 81b572198c04d5d1) and replay the Oct 5 "
                                 "exam's ref games"),
    })
    p = f"{OUT}/config_{an}.json"
    with open(p, "w") as f:
        json.dump(c, f, indent=1)
        f.write("\n")
    print("wrote", p, pilot)
