import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
DROP = {"evidence_ids", "source_video", "source_sha256", "turn_evidence_ids", "basis", "count_method"}

def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if k not in DROP and v not in (None, [], {}, "")}
    if isinstance(o, list):
        return [clean(x) for x in o]
    return o

def poke(x):
    return json.dumps(clean(x), ensure_ascii=False)

for t in d["turns"]:
    print("#" * 110)
    print("ROW turn", t["turn_number"], t["who_played"], "timing", t.get("timing"))
    for k in ("hand_at_start", "owner_hand_start", "opponent_hand_at_owner_turn_start", "owner_hand_before_end_action", "owner_hand_end"):
        if k in t:
            print(f"  {k}: {poke(t[k])}")
    print("  draws_and_searches:")
    for x in t.get("draws_and_searches", []):
        print("    ", poke(x))
    print("  plays:")
    for x in t.get("plays_in_order", []):
        print("    ", poke(x))
    print("  automatic:")
    for x in t.get("automatic_events_in_order", []):
        print("    ", poke(x))
    for bk in ("board_at_start", "board_after"):
        b = t.get(bk)
        if not b:
            continue
        print(f"  {bk}: turn_disp={b.get('turn_number_displayed')} phase={b.get('phase')} stadium={b.get('stadium')} shared={poke(b.get('shared_effects'))}")
        for side in ("owner", "opponent"):
            s = b.get(side, {})
            print(f"    {side}: points={s.get('points')} zone={poke(s.get('energy_zone'))} effects={poke(s.get('board_effects'))} status={s.get('status')}")
            print(f"      ACTIVE {poke(s.get('active'))}")
            for i, bb in enumerate(s.get("bench_in_position_order", []) or []):
                print(f"      BENCH{i} {poke(bb)}")
            for k in s:
                if k not in ("points", "energy_zone", "board_effects", "status", "active", "bench_in_position_order", "evidence_ids"):
                    print(f"      {k}: {poke(s[k])}")
        for k in b:
            if k not in ("turn_number_displayed", "phase", "stadium", "shared_effects", "owner", "opponent", "evidence_ids"):
                print(f"    {k}: {poke(b[k])}")
    for k in t:
        if k not in ("turn_number", "who_played", "timing", "hand_at_start", "owner_hand_start", "opponent_hand_at_owner_turn_start", "owner_hand_before_end_action", "owner_hand_end", "draws_and_searches", "plays_in_order", "automatic_events_in_order", "board_at_start", "board_after") and k not in DROP:
            print(f"  {k}: {poke(t[k])}")
print("TOP limits", poke(d.get("limits")))
for k in d:
    if k not in ("turns", "limits", "sources"):
        print("TOP", k, poke(d[k])[:300])
