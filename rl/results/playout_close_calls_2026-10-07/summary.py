"""The close-call extension (`_m64`, Oct 7): its time cost and the decisions it changes against R = 16.
- gate2/extension.jsonl (playout_tool_rule --extension): the 8 continuation positions and the 12 development positions
  as stored, and the 12 advanced to their Tool placement; 2 decision seeds each (the position's seed and + 10,000); LAB,
  cap 12, z 2; R = 16 against _m64. Times are wall times on the cloud's 4 cores, one decision at a time.
- quiz/index_poolmeta*.json (trainer_habits positions --kx3): quiz 4's 12 positions, kx3 deciding from the game's own
  observation and randomness, as the development run did (kx3_r16_c12_z2_real_t0_poolmeta), and with _m64.
Run from the repository root:
  python3 rl/results/playout_close_calls_2026-10-07/summary.py"""
import json
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in open(HERE / "gate2" / "extension.jsonl", encoding="utf-8")]


def group(r):
    if r["id"].startswith("dev"):
        return "development, the Tool placement" if r["at"] == "placement" else "development, as stored"
    return "continuation"


print("## The gate positions (R = 16 against _m64)")
print()
print("| set | decisions | with a close call (extended) | choice changed | time, R = 16 | time, _m64 | ratio | median per decision, R = 16 / _m64 |")
print("|---|---|---|---|---|---|---|---|")
groups = ["continuation", "development, as stored", "development, the Tool placement"]
for g in groups + ["all"]:
    rs = [r for r in rows if g == "all" or group(r) == g]
    if not rs:
        continue
    a = sum(r["ms_r16"] for r in rs) / 1000
    b = sum(r["ms_ext"] for r in rs) / 1000
    print(f"| {g} | {len(rs)} | {sum(r['rounds_ext'] > 16 for r in rs)} | {sum(r['changed'] for r in rs)} | {a:.0f} s | {b:.0f} s | "
          f"{b / a:.2f} | {median(r['ms_r16'] for r in rs) / 1000:.1f} s / {median(r['ms_ext'] for r in rs) / 1000:.1f} s |")
print()
ext = [r for r in rows if r["rounds_ext"] > 16]
print(f"Rounds played where extended: " + ", ".join(f"{n} rounds: {sum(r['rounds_ext'] == n for r in ext)}" for n in (32, 48, 64)))
print(f"Candidates extended (km3's move included): median {median(r['extended'] for r in ext) if ext else 0}, "
      f"from {min((r['extended'] for r in ext), default=0)} to {max((r['extended'] for r in ext), default=0)}")
print(f"Failed rounds: {sum(sum(r['failed_rounds']) for r in rows)}")
print()


def kind(r):
    km = r["km_move"]
    a, b = r["chosen_r16"], r["chosen_ext"]
    if a == km:
        return "R = 16 kept km3's move; _m64 switches"
    if b == km:
        return "R = 16 switched; _m64 keeps km3's move"
    return "both switch, to different moves"


changed = [r for r in rows if r["changed"]]
print("## The decisions that changed")
print()
for r in changed:
    sc16 = {c["move"]: c for c in r["r16"]}
    scx = {c["move"]: c for c in r["ext"]}
    def show(label):
        a, b = sc16[label], scx[label]
        return f"{label[:70]}: {a['score']:.3f} at 16, {b['score']:.3f} at {b['rounds']}"
    print(f"- {r['decision']} ({kind(r)}):")
    print(f"  - km3's move {show(r['km_move'])}")
    if r["chosen_r16"] != r["km_move"]:
        print(f"  - R = 16 played {show(r['chosen_r16'])}")
    if r["chosen_ext"] != r["km_move"] and r["chosen_ext"] != r["chosen_r16"]:
        print(f"  - _m64 plays {show(r['chosen_ext'])}")
    elif r["chosen_ext"] != r["km_move"]:
        pass
    print(f"  - R = 16: {r['reason_r16']}")
    print(f"  - _m64: {r['reason_ext']}")
print()
print("All decisions:")
print()
print("| decision | candidates | R = 16 | _m64 | rounds | extended | ms R = 16 | ms _m64 |")
print("|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['decision']} | {r['candidates']} | {r['chosen_r16'][:40]} | {r['chosen_ext'][:40]}{' (changed)' if r['changed'] else ''} | "
          f"{r['rounds_ext']} | {r['extended']} | {r['ms_r16']:.0f} | {r['ms_ext']:.0f} |")

# The quiz positions, from the game's own randomness.
qa, qb = HERE / "quiz" / "index_poolmeta.json", HERE / "quiz" / "index_poolmeta_m64.json"
if qa.exists() and qb.exists():
    a = {e["id"]: e for e in json.load(open(qa, encoding="utf-8"))}
    b = {e["id"]: e for e in json.load(open(qb, encoding="utf-8"))}
    print()
    print("## Quiz 4's 12 positions, kx3 from the game's own randomness (REALISTIC, the meta pool)")
    print()
    print("| Q | km3's move | kx3 at R = 16 (its arm's log) | kx3 with _m64 | rounds | ms R = 16 / _m64 |")
    print("|---|---|---|---|---|---|")
    for q in sorted(a):
        x, y = a[q]["kx3_in_the_game"], b[q]["kx3_in_the_game"]
        assert x["plays_what_the_log_says"], q
        rx, ry = x["report"], y["report"]
        print(f"| {q} | {rx['km']} | {x['chosen']} | {y['chosen']}{' (changed)' if y['chosen'] != x['chosen'] else ''} | {ry['rounds']} | "
              f"{rx['ms']:.0f} / {ry['ms']:.0f} |")
    print()
    for q in sorted(a):
        y = b[q]["kx3_in_the_game"]["report"]
        if y["rounds"] > 16:
            print(f"- {q} with _m64: {y['reason']}")
            for c in y["candidates"]:
                print(f"    {c['move']}: {c['score']:.3f} ({c['diff']:+.3f}) over {c['rounds']} rounds")
