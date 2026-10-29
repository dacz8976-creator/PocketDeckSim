#!/usr/bin/env python3
"""The slow report's R6 re-pin check (rl/results/kx3_on_r6_2026-10-29/SPEC.md): three strength_prereg.py configs that replay the
development run's frozen-kx3 games on the R6 program (d513e37b's six kx3 files on R6's engine, S affe56e8), on the development run's own
seeds. The same slices as the Oct 12 and Oct 21 checks (rl/results/kx3_on_engine_2026-10-21/make_replay_configs.py): Wailord (deck 03)
left out; the six other decks in two slices; deck 10 v t-weezing (Will's row) a third registration with all 5 deals. Run from the
repository root; writes rl/results/kx3_on_r6_2026-10-29/configs/."""
import json, os
R = "rl/results"
dev_cfg = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/config.json"))
dev_man = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/manifest.json"))
dev_games = [json.loads(l) for l in open(f"{R}/strength_2026-10-03_kx3_dev/games.jsonl") if l.strip().endswith("}")]
OUT = f"{R}/kx3_on_r6_2026-10-29/configs"
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
PROGRAM, SHA = "/home/dacz8976/kx_r4/strength", "23d8a9b5a2e70f06abc4b6989c6662e73c5ebc33baecbe9727e1af1c4f413378"
ENGINE = ("laptop/kx3-on-r6-2026-10-29 e3ddc0149bb9d35fda1becbb17ab5f71d9461609 engine tree cd970db60aa5df7e9db9d7479e88f87190dab2c3 (the frozen kx3's six "
          "engine files, d513e37b's blobs, laid onto R6's release commit S affe56e88985e2997a66beb85efaca0c487617bd: main ffe97adb, the "
          "card-support refusal and the tests-only fold), built on the laptop 2026-10-29T04:13:47Z with rl/strength/build.sh (harness c4f7da21, "
          "STRENGTH_JOBS=2); self-checks measured on this program in the R6 night: km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa, equal "
          "to the slow-report pin's")
for s, (dl, ol, sb, deals) in SLICES.items():
    c = {k: dev_cfg[k] for k in dev_cfg if k in ("reference", "seats", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines")}
    c.update({
        "name": f"kx3_replay_r6_2026_10_29_{s}",
        "question": ("THE SLOW REPORT'S R6 RE-PIN CHECK (rl/results/kx3_on_r6_2026-10-29/SPEC.md): do the frozen kx3's development-run "
                     "games replay exactly on R6's engine? SPEC.md section 3 found no R6 change that can act in these games and names no "
                     "row, so any changed game is a stop. "
                     f"This registration: {', '.join(dl)} v {', '.join(ol) if len(ol) < 8 else 'the 8 panel lists'}, "
                     f"deals 0-{deals - 1}, seed_base {sb} (each key the development run's own seed)."),
        "pilot": "kx3", "stage": "dev", "decks": dl, "opponents": ol, "deals": deals, "seed_base": sb,
        "program": PROGRAM, "program_sha256": SHA, "engine": ENGINE,
        "pilot_provenance": ("kx3 (d513e37b's files, on main-affe56e): kx3 from claude/playout-pilot@d513e37b (frozen Oct 4-5), its six "
                             "engine files byte for byte on R6's engine, whose km3 player files changed (fuel_credit.rs, value_functions.rs, "
                             "public_pricing_player.rs, weighted_random_player.rs)"),
        "reference_provenance": "km3 in the same build; its self-check is the pinned km3's (81b572198c04d5d1)",
    })
    p = f"{OUT}/config_replay_{s}.json"
    with open(p, "w") as f:
        json.dump(c, f, indent=1); f.write("\n")
    print("wrote", p, dl, len(ol), "opponents, deals", deals, "seed_base", sb)
