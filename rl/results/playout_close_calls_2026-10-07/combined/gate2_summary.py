"""Gate 2 of the fix round (Oct 7): the combined code at the gate positions, _tools_zs3 at R = 16 against _tools_zs3_m64.
- gate2/extension.jsonl (playout_tool_rule --extension --combined, at ec283c53): the 8 continuation positions and the 12
  development positions as stored, and the 12 advanced to their Tool placement; 2 decision seeds each (the position's
  seed and + 10,000); LAB, cap 12, z 2, the Tool rule, the skip bar 3. Times are wall times on the cloud's 4 cores, one
  decision at a time.
- ../gate2/extension.jsonl: the same 64 decisions with the first version (7d3639d0), plain R = 16 against _m64, for
  comparison.
Run from the repository root:
  python3 rl/results/playout_close_calls_2026-10-07/combined/gate2_summary.py"""
import json
from pathlib import Path
from statistics import median

HERE = Path(__file__).resolve().parent
rows = [json.loads(l) for l in open(HERE / "gate2" / "extension.jsonl", encoding="utf-8")]
first = {r["decision"]: r for r in map(json.loads, open(HERE.parent / "gate2" / "extension.jsonl", encoding="utf-8"))}
print(f"codes: {rows[0]['code_r16']} against {rows[0]['code_ext']}; {len(rows)} decisions")


def group(r):
    if r["id"].startswith("dev"):
        return "development, the Tool placement" if r["at"] == "placement" else "development, as stored"
    return "continuation"


print()
print("| set | decisions | with a close call (extended to 64) | choice changed | time, R = 16 | time, with _m64 | ratio | median per decision |")
print("|---|---|---|---|---|---|---|---|")
for g in ["continuation", "development, as stored", "development, the Tool placement", "all"]:
    rs = [r for r in rows if g == "all" or group(r) == g]
    a = sum(r["ms_r16"] for r in rs) / 1000
    b = sum(r["ms_ext"] for r in rs) / 1000
    print(f"| {g} | {len(rs)} | {sum(r['rounds_ext'] > 16 for r in rs)} | {sum(r['changed'] for r in rs)} | {a:,.0f} s | {b:,.0f} s | "
          f"{b / a:.2f} | {median(r['ms_r16'] for r in rs) / 1000:.1f} s / {median(r['ms_ext'] for r in rs) / 1000:.1f} s |")
ext = [r for r in rows if r["rounds_ext"] > 16]
print()
print(f"Rounds where extended: {sorted(set(r['rounds_ext'] for r in ext))}; candidates extended (km3's move included): median "
      f"{median(r['extended'] for r in ext)}, from {min(r['extended'] for r in ext)} to {max(r['extended'] for r in ext)}; "
      f"failed rounds: {sum(sum(r['failed_rounds']) for r in rows)}")
both = [r for r in rows if r["decision"] in first]
f_ext = sum(first[r["decision"]]["rounds_ext"] > 16 for r in both)
print(f"The first version on the same {len(both)} decisions: {f_ext} extended, {sum(first[r['decision']]['changed'] for r in both)} changed, "
      f"{sum(first[r['decision']]['ms_ext'] for r in both) / 1000:,.0f} s with _m64")
same_r16 = sum(r["chosen_r16"] == first[r["decision"]]["chosen_r16"] for r in both)
same_ext = sum(r["chosen_ext"] == first[r["decision"]]["chosen_ext"] for r in both)
print(f"  same choice as the first version: at R = 16 {same_r16} of {len(both)} (_tools_zs3 v plain); with the extension {same_ext} of {len(both)}")
print()
# The Tool tie-break after the extension.
tb16 = [r for r in rows if r["reason_r16"].startswith("tie-break: Tool effect")]
tbx = [r for r in rows if r["reason_ext"].startswith("tie-break: Tool effect")]
print(f"The Tool tie-break plays the placement: {len(tb16)} decisions at R = 16, {len(tbx)} with the extension")
for r in tbx:
    c = next(c for c in r["ext"] if c["move"] == r["chosen_ext"])
    note = "a placement left at 16 rounds, not extended" if c["rounds"] == 16 and r["rounds_ext"] > 16 else f"{c['rounds']} rounds"
    print(f"- {r['decision']}: {r['chosen_ext'][:70]} ({note}; {c['diff']:+.3f} v km3's)")
print()
print("## The decisions that changed")
for r in rows:
    if not r["changed"]:
        continue
    sc16 = {c["move"]: c for c in r["r16"]}
    scx = {c["move"]: c for c in r["ext"]}
    def show(label):
        a, b = sc16[label], scx[label]
        return f"{label[:70]}: {a['score']:.3f} at 16, {b['score']:.3f} at {b['rounds']}"
    print(f"- {r['decision']}:")
    print(f"  - km3's move {show(r['km_move'])}")
    if r["chosen_r16"] != r["km_move"]:
        print(f"  - R = 16 played {show(r['chosen_r16'])}")
    if r["chosen_ext"] != r["km_move"] and r["chosen_ext"] != r["chosen_r16"]:
        print(f"  - with _m64: {show(r['chosen_ext'])}")
    print(f"  - R = 16: {r['reason_r16']}")
    print(f"  - _m64: {r['reason_ext']}")
print()
print("## All decisions")
print()
print("| decision | candidates | R = 16 | with _m64 | rounds | extended | ms R = 16 | ms _m64 | the first version's _m64 |")
print("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    f = first.get(r["decision"])
    print(f"| {r['decision']} | {r['candidates']} | {r['chosen_r16'][:40]} | {r['chosen_ext'][:40]}{' (changed)' if r['changed'] else ''} | "
          f"{r['rounds_ext']} | {r['extended']} | {r['ms_r16']:.0f} | {r['ms_ext']:.0f} | "
          f"{(f['chosen_ext'][:40] + ' (' + str(f['rounds_ext']) + ')') if f else '-'} |")
