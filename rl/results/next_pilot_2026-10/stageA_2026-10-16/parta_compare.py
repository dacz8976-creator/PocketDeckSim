"""Stage A part (a): km3 on the blade build must equal v2/runs_km3 plan for plan; then, per arm (kmb3, kmbc3, kmbd3), the positions
and seeds where its plan differs from km3's, with the first move of each."""
import json
import os
import sys

old_dir, out, ids_file = sys.argv[1], sys.argv[2], sys.argv[3]
ids = [l.strip() for l in open(ids_file) if l.strip()]


def plans(path):
    res = {}
    if not os.path.exists(path):
        return None
    for line in open(path):
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("kind") == "free":
            res[j["seed"]] = j.get("plan") or []
    return res


old = {i: plans(f"{old_dir}/out_{i}.jsonl") for i in ids}
km = {i: plans(f"{out}/pos_km3/out_{i}.jsonl") for i in ids}
eq = sum(1 for i in ids for s in (old[i] or {}) if km[i] and km[i].get(s) == old[i][s])
tot = sum(len(old[i] or {}) for i in ids)
bad = [(i, s) for i in ids for s in (old[i] or {}) if not km[i] or km[i].get(s) != old[i][s]]
print(f"km3 re-run v v2/runs_km3: {eq} of {tot} position-seeds equal plan for plan; differing: {len(bad)}")
for i, s in bad[:20]:
    print("  differs:", i, s, "old", (old[i] or {}).get(s, [])[:3], "new", (km[i] or {}).get(s, [])[:3])
for arm in ("kmb3", "kmbc3", "kmbd3"):
    p = {i: plans(f"{out}/pos_{arm}/out_{i}.jsonl") for i in ids}
    moved = {}
    for i in ids:
        for s, plan in (p[i] or {}).items():
            base = (km[i] or {}).get(s)
            if base is not None and plan != base:
                moved.setdefault(i, []).append((s, base[:2], plan[:2]))
    nseeds = sum(len(v) for v in moved.values())
    print(f"\n{arm}: plans differ from km3 at {len(moved)} positions ({nseeds} position-seeds)")
    for i, v in moved.items():
        firsts = sorted({(tuple(b[:1]), tuple(c[:1])) for _, b, c in v})
        print(f"  {i}: {len(v)}/12 seeds; first moves km3 -> {arm}: {firsts}")
