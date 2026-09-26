"""Second reader: run score.py (unchanged) three times on the same inputs as run_score.sh and compare its output with the
writer's kpr3_vs_*.txt files line by line, ignoring only the Source line (the path of the kpr3 copy differs).
Also compares the no-mixed runs with Fable's score_v2 / score_sept23 outputs."""
import os, subprocess, sys
from check_common import RES, KPR3, HERE

S = os.path.join(RES, "table_readings_2026-09-24", "score.py")
KP3 = ["public_pricing_2026-09-25/kp3_500_worst5.jsonl", "public_pricing_2026-09-25/kp3_500_rest.jsonl"]
MIX = ["kpr_mixed_rows_2026-09-26/mixed_kpr3_first.jsonl", "kpr_mixed_rows_2026-09-26/mixed_kpr3_second.jsonl"]
V2 = ["--limitless", "scoreboard_v2_2026-09-25/limitless_v2_dev.json",
      "--limitless-events", "scoreboard_v2_2026-09-25/limitless_v2_dev_events.json"]
runs = {
    "kpr3_vs_kp3_v2": ["--rules", "v2", "--old", "kp3", "--new", "kpr3", "--old-games", *KP3, "--new-games", KPR3[0],
                       "--mixed", *MIX, *V2],
    "kpr3_vs_kp3_sept23": ["--rules", "v2", "--old", "kp3", "--new", "kpr3", "--old-games", *KP3, "--new-games", KPR3[0],
                           "--mixed", *MIX],
    "kpr3_vs_k3_v2": ["--rules", "v2", "--old", "k3", "--new", "kpr3", "--old-games",
                      "per_game_table_2026-09-25/k3_500.jsonl", "--new-games", KPR3[0], *V2],
    "fable_v2_nomixed": ["--rules", "v2", "--old", "kp3", "--new", "kpr3", "--old-games", *KP3, "--new-games", KPR3[0], *V2],
    "fable_sept23_nomixed": ["--rules", "v2", "--old", "kp3", "--new", "kpr3", "--old-games", *KP3, "--new-games", KPR3[0]],
}
refs = {
    "kpr3_vs_kp3_v2": os.path.join(HERE, "kpr3_vs_kp3_v2.txt"),
    "kpr3_vs_kp3_sept23": os.path.join(HERE, "kpr3_vs_kp3_sept23.txt"),
    "kpr3_vs_k3_v2": os.path.join(HERE, "kpr3_vs_k3_v2.txt"),
    "fable_v2_nomixed": os.path.join(RES, "fable_reviews_2026-09-26", "score_v2_kpr3_vs_kp3.txt"),
    "fable_sept23_nomixed": os.path.join(RES, "fable_reviews_2026-09-26", "score_sept23_kpr3_vs_kp3.txt"),
}
print(f"python {sys.version.split()[0]}")
for name, args in runs.items():
    out = subprocess.run([sys.executable, S, *args], cwd=RES, capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        print(name, "FAILED", out.stderr[-500:])
        continue
    mine = out.stdout.splitlines()
    with open(os.path.join(HERE, f"check_score_{name}.txt"), "w", encoding="utf-8") as f:
        f.write(out.stdout)
    theirs = open(refs[name], encoding="utf-8").read().splitlines()
    keep = lambda ls: [l for l in ls if not l.startswith("Source:")]  # noqa: E731
    a, b = keep(mine), keep(theirs)
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    print(f"{name}: mine {len(a)} lines, reference {len(b)} lines, {len(diff)} differing lines"
          + ("" if len(a) == len(b) else " (LENGTHS DIFFER)"))
    for i, x, y in diff[:6]:
        print(f"   mine : {x}\n   ref  : {y}")
