#!/usr/bin/env python3
"""The slow report's re-pin check (rl/results/kx3_on_engine_2026-10-21/SPEC.md): three strength_prereg.py configs that replay the
development run's frozen-kx3 games on the re-pin program (d513e37b's players on main-4d48844's engine), on the development run's own
seeds. The same slices as the Oct 12 check (rl/results/kx3_on_rules2_2026-10/make_replay_configs.py): Wailord (deck 03) left out; the
six other decks in two slices; deck 10 v t-weezing (Will's row) a third registration with all 5 deals. Run from the repository root;
writes rl/results/kx3_on_engine_2026-10-21/configs/."""
import json, os
R = "rl/results"
dev_cfg = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/config.json"))
dev_man = json.load(open(f"{R}/strength_2026-10-03_kx3_dev/manifest.json"))
dev_games = [json.loads(l) for l in open(f"{R}/strength_2026-10-03_kx3_dev/games.jsonl") if l.strip().endswith("}")]
OUT = f"{R}/kx3_on_engine_2026-10-21/configs"
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
PROGRAM, SHA = "/home/dacz8976/kx_r3/strength", "7d046b6f9c1dcd9a9a834c2995bad256bc784e804ea08d351878e035cb24d319"
ENGINE = ("laptop/kx3-on-engine-candidate-2026-10-20 87a7f3404263e1bfe76e8765ba8dd94695e19cfe engine tree "
          "64de03e2c3c25b8371e9b87c5727d1f93ec70c30 (the frozen kx3's players, d513e37b, on main-4d48844's engine: built commit "
          "4d4884492aa85496acf9bafdae18b22739f56647), built on the laptop Oct 21 with rl/strength/build.sh (harness bf9c5d68, "
          "STRENGTH_JOBS=2); self-checks measured on this program Oct 21: km3 81b572198c04d5d1 and kx3 31d638dbc818b0fa, equal to the "
          "slow-report pin's")
for s, (dl, ol, sb, deals) in SLICES.items():
    c = {k: dev_cfg[k] for k in dev_cfg if k in ("reference", "seats", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines")}
    c.update({
        "name": f"kx3_replay_engine_2026_10_21_{s}",
        "question": ("THE SLOW REPORT'S RE-PIN CHECK after main-4d48844's pin (rl/results/kx3_on_engine_2026-10-21/SPEC.md): do the frozen "
                     "kx3's development-run games replay exactly on the new engine, except where one of main-4d48844's six changes acts "
                     "(SPEC.md section 3 names the rows), and does every changed game show that change acting? "
                     f"This registration: {', '.join(dl)} v {', '.join(ol) if len(ol) < 8 else 'the 8 panel lists'}, "
                     f"deals 0-{deals - 1}, seed_base {sb} (each key the development run's own seed)."),
        "pilot": "kx3", "stage": "dev", "decks": dl, "opponents": ol, "deals": deals, "seed_base": sb,
        "program": PROGRAM, "program_sha256": SHA, "engine": ENGINE,
        "pilot_provenance": "kx3 from claude/playout-pilot@d513e37b (frozen Oct 4-5), its players byte for byte on main-4d48844's engine",
        "reference_provenance": "km3 in the same build; its self-check is the pinned km3's (81b572198c04d5d1)",
    })
    p = f"{OUT}/config_replay_{s}.json"
    with open(p, "w") as f:
        json.dump(c, f, indent=1); f.write("\n")
    print("wrote", p, dl, len(ol), "opponents, deals", deals, "seed_base", sb)
