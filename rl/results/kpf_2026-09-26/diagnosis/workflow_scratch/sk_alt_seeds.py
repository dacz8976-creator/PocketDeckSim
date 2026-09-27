import re, pickle, sys
D = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/kpf_2026-09-26/diagnosis/"
base, kpf = pickle.load(open(D + "workflow_scratch/sk_alt_games.pkl", "rb"))
alt = pickle.load(open(D + "workflow_scratch/sk_alt_recs.pkl", "rb"))
R = {r["seed"]: r for r in alt}


def short(a):
    a = re.sub(r"Attack\(Attack \{.*title: \"([^\"]+)\".*", r"ATK \1", a)
    a = re.sub(r"Attach \{ attachments: \[\((\d+), (\w+), (\d+)\)\], is_turn_energy: true \}", r"ZONE->\3", a)
    a = re.sub(r"Play \{ trainer_card: \S+ \S+ (.+?) \}", r"PLAY \1", a)
    a = re.sub(r"Pokemon\(\S+ \S+ (.+?)\)", r"\1", a)
    a = re.sub(r"DrawCard \{ amount: 1 \}", "Draw", a)
    a = re.sub(r"Evolve \{ evolution: (.+?), in_play_idx: (\d+), from_deck: \w+ \}", r"Evolve \1@\2", a)
    return a


def show(seed, turns, which=("kp3", "kpf")):
    r = R[seed]
    seat = r["kpf_seat"]
    print(f"=== {seed} {r['kind']} v {r['b']} (altaria seat {seat}), divergence turn {r['turn']} change {r['change']}")
    for w in which:
        g = (base if w == "kp3" else kpf)[seed][0]
        for t in turns:
            L = [ln for ln in g if ln["turn"] == t and ln["actor"] == seat and ln["tomove"] == seat]
            if not L:
                continue
            print(f"  {w} t{t} start: {L[0]['s'][seat]}")
            print(f"        opp: {L[0]['s'][1 - seat]}")
            print(f"        acts: {' ; '.join(short(ln['act']) for ln in L)}")
            print(f"        end: {L[-1]['s'][seat]}")


for arg in sys.argv[1:]:
    seed, ts = arg.split(":")
    show(int(seed), [int(x) for x in ts.split(",")])
