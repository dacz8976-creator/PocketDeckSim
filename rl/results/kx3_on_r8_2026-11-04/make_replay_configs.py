#!/usr/bin/env python3
"""The slow report's R8 re-pin check (rl/results/kx3_on_r8_2026-11-04/SPEC.md): three strength_prereg.py configs that replay the
development run's frozen-kx3 games on the R8 program (d513e37b's six kx3 files on R8's engine: K8 b5f15351), on the development run's own
seeds. The same slices as the Oct 12, Oct 21 and Oct 29 checks (rl/results/kx3_on_r6_2026-10-29/make_replay_configs.py): Wailord
(deck 03) left out; the six other decks in two slices; deck 10 v t-weezing (Will's row) a third registration with all 5 deals. Run from
the repository root; writes rl/results/kx3_on_r8_2026-11-04/configs/. Only the program, its texts and the names differ from R6's copy."""
import json, os
R = "rl/results"
dev_cfg = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/config.json"))
dev_man = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/manifest.json"))
dev_games = [json.loads(l) for l in open(f"{R}/strength_2026-10-03_kx3_dev/games.jsonl") if l.strip().endswith("}")]
OUT = f"{R}/kx3_on_r8_2026-11-04/configs"
os.makedirs(OUT, exist_ok=True)
decks = [d["name"] for d in dev_man["decks"]]; opps = [o["name"] for o in dev_man["opponents"]]
base, stride = dev_man["seed_base"], dev_man["pair_stride"]
assert decks[3] == "03-wailord-indeedee-wall" and decks[2] == "10-xatu-oricorio-tr-weezing" and opps[7] == "t-weezing"
assert dev_man["pilot"] == "kx3" and dev_man["reference"] == "km3"
SLICES = {
    "a": (decks[0:3], opps, base, 2),
    "b": (decks[4:7], opps, base + 4 * 1000 * stride, 2),
    "c": ([decks[2]], [opps[7]], base + (2 * 1000 + 7) * stride, 5),
}
dev_seed = {(g["deck"], g["opp"], g["deal"], g["seat"], g["arm"]): g["seed"] for g in dev_games}
n = 0
for s, (dl, ol, sb, deals) in SLICES.items():
    for di, d in enumerate(dl):
        for oi, o in enumerate(ol):
            for deal in range(deals):
                for seat in (0, 1):
                    for arm in ("ref", "X"):
                        assert sb + (di * 1000 + oi) * stride + deal == dev_seed[(d, o, deal, seat, arm)], (s, d, o, deal, seat, arm)
                        n += 1
print(f"seeds: all {n} keys get the development run's seed")
PROGRAM, SHA = ("/home/dacz8976/pincand_work/RR_R8_48dec4f5/strength/K8/strength",
                "d4d4e43acebcf7aebad7ba719d32dc2b0a3d347d1a2b53c074788a678ab4e12d")
ENGINE = ("laptop/kx3-on-r8-2026-11-04 b5f15351f3f61f2bfc2fc6c41dfc555e3a3b71b0 engine tree f33d2c49baf432d4bd1e407b96a6c243471fa9b6 "
          "(the frozen kx3's six engine files on R8's lane commit 48dec4f5, whose engine tree is R8's release S8 543dad00's, "
          "014b4371a3b8: five files byte for byte d513e37b's, and players/mod.rs d513e37b's plus R8's 8 protocol-adapter lines, a union "
          "merge), built on the laptop 2026-11-04T06:07:16Z with rl/strength/build.sh (harness c4f7da21, STRENGTH_JOBS=2); self-checks: "
          "kx3 31d638dbc818b0fa measured on this program (Nov 4), km3 81b572198c04d5d1 measured on strength_L (R8's km3 build, the same "
          "engine tree), both equal to the slow-report pin's; each registration replays both on this program")
for s, (dl, ol, sb, deals) in SLICES.items():
    c = {k: dev_cfg[k] for k in dev_cfg if k in ("reference", "seats", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines")}
    c.update({
        "name": f"kx3_replay_r8_2026_11_04_{s}",
        "question": ("THE SLOW REPORT'S R8 RE-PIN CHECK (rl/results/kx3_on_r8_2026-11-04/SPEC.md): do the frozen kx3's development-run "
                     "games replay exactly on R8's engine? SPEC.md section 3 found no R8 change that can act in these games and names no "
                     "row, so any changed game is a stop. "
                     f"This registration: {', '.join(dl)} v {', '.join(ol) if len(ol) < 8 else 'the 8 panel lists'}, "
                     f"deals 0-{deals - 1}, seed_base {sb} (each key the development run's own seed)."),
        "pilot": "kx3", "stage": "dev", "decks": dl, "opponents": ol, "deals": deals, "seed_base": sb,
        "program": PROGRAM, "program_sha256": SHA, "engine": ENGINE,
        "pilot_provenance": ("kx3 (d513e37b's files, on main-543dad0): kx3 from claude/playout-pilot@d513e37b (frozen Oct 4-5), its five "
                             "player, pool and test files byte for byte, players/mod.rs with R8's protocol-adapter lines added, on R8's "
                             "engine"),
        "reference_provenance": "km3 in the same build; its self-check is the pinned km3's (81b572198c04d5d1)",
    })
    p = f"{OUT}/config_replay_{s}.json"
    with open(p, "w") as f:
        json.dump(c, f, indent=1); f.write("\n")
    print("wrote", p, dl, len(ol), "opponents, deals", deals, "seed_base", sb)
