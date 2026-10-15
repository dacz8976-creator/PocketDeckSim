#!/usr/bin/env python3
"""m64's replay check on the current engine (rl/results/m64_on_rules2_2026-10/SPEC.md section 3): three strength_prereg.py configs that
replay the combined run's m64 games (rl/results/strength_2026-10-08_kx3_combined, arm X) on the new program (172cbe9c's players on
main-c045ede's engine, laptop/kx3cand-on-rules2 9a0bc5ac), on the combined run's own seeds. As in step 4: Wailord (deck 03) is left out
(Dustin, Oct 10), the six other decks are two slices with deals 0-1, and deck 10 v t-weezing (Will's row) is a third with all 5 deals.
Usage, from the repository root: make_replay_configs.py PROGRAM; it reads PROGRAM.build.json (build.sh's record) for the program sha256,
the archived engine tree and the harness source, and checks them; writes rl/results/m64_on_rules2_2026-10/configs/."""
import hashlib, json, os, sys
R = "rl/results"
SRC = f"{R}/strength_2026-10-08_kx3_combined"
PROGRAM = sys.argv[1]
rec = json.load(open(PROGRAM + ".build.json"))
SHA = hashlib.sha256(open(PROGRAM, "rb").read()).hexdigest()
assert rec.get("program_sha256") == SHA, ("the build record is for another program", rec.get("program_sha256"), SHA)
TREE = rec.get("engine_tree_archived") or rec.get("engine_tree")
assert TREE and TREE.startswith("5d557d350b6d"), ("engine tree", TREE)
assert str(rec.get("engine_ref", "")).startswith("9a0bc5ac"), ("engine ref", rec.get("engine_ref"))
HARNESS = str(rec.get("harness_source_sha256"))[:16]
assert HARNESS == "bf9c5d6814007f1f", ("harness source", HARNESS)
cfg = json.load(open(f"{SRC}/config.json"))
man = json.load(open(f"{SRC}/manifest.json"))
games = [json.loads(l) for l in open(f"{SRC}/games.jsonl") if l.strip().endswith("}")]
OUT = f"{R}/m64_on_rules2_2026-10/configs"
os.makedirs(OUT, exist_ok=True)
PILOT = "kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64"
decks = [d["name"] for d in man["decks"]]; opps = [o["name"] for o in man["opponents"]]
base, stride = man["seed_base"], man["pair_stride"]
assert man["pilot"] == PILOT and man["reference"] == "km3", (man["pilot"], man["reference"])
assert decks[3] == "03-wailord-indeedee-wall" and decks[2] == "10-xatu-oricorio-tr-weezing" and opps[7] == "t-weezing"
assert base == 24400000000 and stride == 10000
SLICES = {
    "a": (decks[0:3], opps, base, 2),
    "b": (decks[4:7], opps, base + 4 * 1000 * stride, 2),
    "c": ([decks[2]], [opps[7]], base + (2 * 1000 + 7) * stride, 5),
}
src_seed = {(g["deck"], g["opp"], g["deal"], g["seat"], g["arm"]): g["seed"] for g in games}
n = 0
for s, (dl, ol, sb, deals) in SLICES.items():
    for di, d in enumerate(dl):
        for oi, o in enumerate(ol):
            for deal in range(deals):
                for seat in (0, 1):
                    for arm in ("ref", "X"):
                        assert sb + (di * 1000 + oi) * stride + deal == src_seed[(d, o, deal, seat, arm)], (s, d, o, deal, seat, arm)
                        n += 1
print(f"seeds: all {n} keys get the combined run's seed")
ENGINE = ("laptop/kx3cand-on-rules2 9a0bc5ac28ccf421044c3c68dc2779123b607bca engine tree 5d557d350b6d (the candidate kx3's players, "
          "claude/playout-pilot 172cbe9c byte for byte, on main-c045ede's engine, rules switch 2), built on the laptop Oct 14 with "
          f"rl/strength/build.sh (harness {HARNESS})")
for s, (dl, ol, sb, deals) in SLICES.items():
    c = {k: cfg[k] for k in cfg if k in ("reference", "seats", "pair_stride", "threads", "log_level", "ext_timeout_s", "intended_lines")}
    c.update({
        "name": f"m64_replay_rules2_{s}",
        "question": ("m64's REPLAY CHECK on the current engine (rl/results/m64_on_rules2_2026-10/SPEC.md section 3): do the combined run's m64 "
                     "games replay exactly on the rules-switch-2 engine, except deck 10 against t-weezing, where each changed game must show "
                     f"Will's new rule acting? This registration: {', '.join(dl)} v {', '.join(ol) if len(ol) < 8 else 'the 8 panel lists'}, "
                     f"deals 0-{deals - 1}, seed_base {sb} (each key the combined run's own seed)."),
        "pilot": PILOT, "stage": "dev", "decks": dl, "opponents": ol, "deals": deals, "seed_base": sb,
        "program": PROGRAM, "program_sha256": SHA, "engine": ENGINE,
        "pilot_provenance": f"{PILOT} from claude/playout-pilot@172cbe9c (the combined run's and the held-out exam's m64), its players byte for byte on main-c045ede's engine",
        "reference_provenance": "km3 in the same build; its self-check must be the pinned km3's (81b572198c04d5d1)",
    })
    p = f"{OUT}/config_replay_{s}.json"
    with open(p, "w") as f:
        json.dump(c, f, indent=1); f.write("\n")
    print("wrote", p, dl, len(ol), "opponents, deals", deals, "seed_base", sb)
