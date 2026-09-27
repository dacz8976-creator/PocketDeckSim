import pickle, re
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
rows = pickle.load(open(D + "workflow_scratch/sk_alt_rows.pkl", "rb"))


def short(a):
    a = re.sub(r"Attack\(Attack \{.*title: \"([^\"]+)\".*", r"ATK \1", a)
    a = re.sub(r"Attach \{ attachments: \[\((\d+), (\w+), (\d+)\)\], is_turn_energy: true \}", r"ZONE->\3", a)
    a = re.sub(r"Play \{ trainer_card: \S+ \S+ (.+?) \}", r"PLAY \1", a)
    a = re.sub(r"Pokemon\(\S+ \S+ (.+?)\)", r"\1", a)
    a = re.sub(r"DrawCard \{ amount: 1 \}", "Draw", a)
    a = re.sub(r"Evolve \{ evolution: (.+?), in_play_idx: (\d+), from_deck: \w+ \}", r"Evolve \1@\2", a)
    return a


n = 0
for r in rows:
    if not r["own_turn"]:
        continue
    a3, af = r["kp3"], r["kpf"]
    if (a3["dest_attach"], af["dest_attach"]) != (a3["dest_end"], af["dest_end"]):
        n += 1
        if n <= 40:
            print(r["seed"], r["kind"], r["opp"], "t", r["turn"], "| attach:", a3["dest_attach"], af["dest_attach"], "end:", a3["dest_end"], af["dest_end"])
            print("   board:", a3["div_board"])
            print("   kp3:", " ; ".join(short(x) for x in a3["acts"]))
            print("   kpf:", " ; ".join(short(x) for x in af["acts"]))
print("total differing", n)
