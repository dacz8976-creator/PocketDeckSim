import json, sys
P = sys.argv[1]
d = json.load(open(P + "/TURN_LEDGER.json"))

def poke(p):
    if p is None:
        return "-"
    e = p.get("attached_energy") or {}
    bt = {k: v for k, v in (e.get("by_type") or {}).items() if v}
    s = "%s[%s] %s/%s dmg=%s E=%s(tot %s) tool=%s" % (p.get("name"), p.get("variant"), p.get("hp_now"), p.get("hp_max"), p.get("damage"), bt, e.get("total"), p.get("tool"))
    if p.get("special_conditions"):
        s += " COND=%s" % p["special_conditions"]
    if p.get("active_effects"):
        s += " EFF=%s" % json.dumps(p["active_effects"], ensure_ascii=False)
    extra = {k: v for k, v in p.items() if k not in ("name", "variant", "bench_position", "hp_now", "hp_max", "hp_max_basis", "damage", "attached_energy", "tool", "special_conditions", "active_effects", "evidence_ids", "status", "limit_reason")}
    if extra:
        s += " EXTRA=%s" % json.dumps(extra, ensure_ascii=False)
    if p.get("status") != "observed":
        s += " STATUS=%s" % p.get("status")
    if p.get("limit_reason"):
        s += " LIMIT=%s" % p.get("limit_reason")
    if p.get("hp_max_basis") and "no HP modifier" not in p.get("hp_max_basis"):
        s += " HPBASIS=%s" % p.get("hp_max_basis")
    return s

def side(name, s):
    out = []
    if s is None:
        return ["  %s: None" % name]
    out.append("  %s: points=%s" % (name, s.get("points")))
    out.append("    A: " + poke(s.get("active")))
    for i, b in enumerate(s.get("bench_in_position_order") or []):
        if b is not None:
            out.append("    B%d: %s" % (i + 1, poke(b)))
    ez = s.get("energy_zone") or {}
    out.append("    EZ now=%s next=%s" % (json.dumps(ez.get("this_turn")), json.dumps(ez.get("next"))))
    if s.get("board_effects"):
        out.append("    board_effects=%s" % json.dumps(s["board_effects"], ensure_ascii=False))
    extra = {k: v for k, v in s.items() if k not in ("active", "bench_in_position_order", "points", "board_effects", "energy_zone", "evidence_ids", "status", "limit_reason")}
    if extra:
        out.append("    EXTRA=%s" % json.dumps(extra, ensure_ascii=False))
    return out

def board(label, b):
    print(" %s: stadium=%s phase=%s" % (label, b.get("stadium"), b.get("phase")))
    for k in ("owner", "opponent"):
        for l in side(k, b.get(k)):
            print(l)
    if b.get("shared_effects"):
        print("  shared_effects=%s" % json.dumps(b["shared_effects"], ensure_ascii=False))
    extra = {k: v for k, v in b.items() if k not in ("turn_number_displayed", "phase", "stadium", "owner", "opponent", "shared_effects", "evidence_ids", "source_seconds")}
    if extra:
        print("  EXTRA=%s" % json.dumps(extra, ensure_ascii=False))

for r in d["turns"]:
    print("=" * 110)
    print("TURN %s who=%s time=%s" % (r["turn_number"], r["who_played"], r.get("source_time_range_seconds")))
    for hk in ("hand_at_start", "owner_hand_start", "owner_hand_end", "opponent_hand_at_owner_turn_start"):
        h = r.get(hk)
        if h:
            print(" %s: %s" % (hk, json.dumps({k: v for k, v in h.items() if k not in ("evidence_ids",)}, ensure_ascii=False)))
    print(" DRAWS:")
    for ds in r.get("draws_and_searches") or []:
        cards = [c.get("name") for c in ds.get("cards_in_reveal_order") or []]
        x = {k: v for k, v in ds.items() if k not in ("cards_in_reveal_order",)}
        print("   %s cards=%s" % (json.dumps(x, ensure_ascii=False), cards))
    print(" PLAYS:")
    for p in r.get("plays_in_order") or []:
        x = {k: v for k, v in p.items() if k not in ("source_video", "evidence_ids", "basis") and v not in (None, [], {})}
        print("   " + json.dumps(x, ensure_ascii=False))
    print(" AUTO:")
    for a in r.get("automatic_events_in_order") or []:
        if isinstance(a, dict):
            x = {k: v for k, v in a.items() if k not in ("source_video", "evidence_ids") and v not in (None, [], {})}
        else:
            x = a
        print("   " + json.dumps(x, ensure_ascii=False))
    board("BOARD_AT_START", r["board_at_start"])
    board("BOARD_AFTER", r["board_after"])
    print(" discard_snapshot_ids=%s" % r.get("discard_snapshot_ids"))
    print(" limits=%s" % json.dumps(r.get("limits"), ensure_ascii=False))
    extra = {k: v for k, v in r.items() if k not in ("turn_number", "who_played", "source_video", "source_sha256", "source_time_range_seconds", "timing", "draws_and_searches", "plays_in_order", "automatic_events_in_order", "board_at_start", "board_after", "discard_snapshot_ids", "turn_evidence_ids", "limits", "hand_at_start", "owner_hand_start", "owner_hand_end", "opponent_hand_at_owner_turn_start")}
    if extra:
        print(" ROW EXTRA=%s" % json.dumps(extra, ensure_ascii=False))
print("TOP-LEVEL limits:", json.dumps(d.get("limits"), ensure_ascii=False, indent=1))
for k, v in d.items():
    if k not in ("turns", "limits"):
        print(k, json.dumps(v, ensure_ascii=False)[:2000])
