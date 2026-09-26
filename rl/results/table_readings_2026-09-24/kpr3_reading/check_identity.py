"""Second reader: the identity statements in kpr3_paired_reading.md, section 6 (own code).
Each replay file is compared with its reference table game by game on every field the reference carries except the
bot names (hyper_ray included where both carry it)."""
import hashlib, os
from check_common import RES, SP, KP3, KPR3, K3, load

REF = {"k3": K3, "kp3": KP3, "kq3": [os.path.join(RES, "kq_2026-09-25", "kq3_500.jsonl")],
       "kd3": [os.path.join(SP, "kd3_500.jsonl")], "kpr3": KPR3}
refs = {b: load(p, (b, b)) for b, p in REF.items()}
FIELDS = ("a", "b", "pairing", "i", "seed", "first_seat", "moves", "winner_seat", "points", "turns", "first_deck_score")


def compare(path, bot):
    t = load([path], (bot, bot))
    ref = refs[bot]
    n = same = 0
    extra = {}
    for k, c in t.items():
        for i, r in c.items():
            n += 1
            b = ref[k][i]
            ok = all(r[f] == b[f] for f in FIELDS)
            for f in ("hyper_ray", "chase_order"):   # counters: compared where both files carry them
                if f in r and f in b:
                    e = extra.setdefault(f"{f} (both carry)", [0, 0])
                    e[0] += 1
                    e[1] += r[f] == b[f]
                    ok = ok and r[f] == b[f]
                elif f in r or f in b:
                    key = f"{f} only in {'replay' if f in r else 'reference'}"
                    extra[key] = extra.get(key, 0) + 1
            same += ok
    deals = sorted({i for c in t.values() for i in c})
    return n, same, len(t), (deals[0], deals[-1]), extra


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


print("reference tables:", {b: f"{sum(len(c) for c in r.values()):,} games" for b, r in refs.items()})
cloud = [("identity_k3_500.jsonl", "k3"), ("identity_kp3_500.jsonl", "kp3"), ("identity_kq3_500.jsonl", "kq3"),
         ("identity_kd3_40.jsonl", "kd3"), ("table_commit_identity_k3_40.jsonl", "k3"),
         ("table_commit_identity_kp3_40.jsonl", "kp3"), ("table_commit_identity_kq3_40.jsonl", "kq3")]
for f, b in cloud:
    n, s, cells, dr, ex = compare(os.path.join(SP, f), b)
    print(f"  cloud {f:<36} {s:,} of {n:,} identical to the {b} table ({cells} pairings, deals {dr[0]}-{dr[1]}; also "
          f"compared: {ex or 'none'})")
mix = os.path.join(RES, "kpr_mixed_rows_2026-09-26")
for f, b in (("spot_kp3_p0-2.jsonl", "kp3"), ("kpr3_replay_p1.jsonl", "kpr3")):
    n, s, cells, dr, ex = compare(os.path.join(mix, f), b)
    print(f"  laptop {f:<35} {s:,} of {n:,} identical to the {b} table ({cells} pairings; also compared: {ex or 'none'})")
print("  byte-identical? cloud identity_kp3_500.jsonl vs engine_identity_2026-09-25/kp3_500.jsonl:",
      sha(os.path.join(SP, "identity_kp3_500.jsonl")) == sha(os.path.join(RES, "engine_identity_2026-09-25", "kp3_500.jsonl"))
      if os.path.exists(os.path.join(RES, "engine_identity_2026-09-25", "kp3_500.jsonl")) else "no such file")
print("  laptop scan identity.txt:", open(os.path.join(mix, "identity.txt"), encoding="utf-8").read().strip())
print("  kpr3 table sha256:", sha(KPR3[0]))
