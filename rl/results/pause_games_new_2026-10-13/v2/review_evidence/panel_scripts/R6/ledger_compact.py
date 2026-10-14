import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
g = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 else base + g + "/TURN_LEDGER.json"
d = json.load(open(path, encoding="utf-8"))

def mon(m):
    if not m:
        return "None"
    if isinstance(m, str):
        return m
    s = "%s[%s] %s/%s dmg=%s" % (m.get("name"), m.get("variant"), m.get("hp_now"), m.get("hp_max"), m.get("damage"))
    e = m.get("attached_energy") or {}
    if e:
        s += " E%s:%s" % (e.get("total"), json.dumps(e.get("by_type"), ensure_ascii=False))
    if m.get("tool") not in (None, "none"):
        s += " TOOL=%s" % m.get("tool")
    if m.get("special_conditions"):
        s += " COND=%s" % json.dumps(m.get("special_conditions"), ensure_ascii=False)
    if m.get("active_effects"):
        s += " EFF=%s" % json.dumps([x.get("name") if isinstance(x, dict) else x for x in m.get("active_effects")], ensure_ascii=False)
    for k in m:
        if k not in ("name", "variant", "bench_position", "hp_now", "hp_max", "damage", "hp_max_basis", "attached_energy", "tool", "special_conditions", "active_effects", "status", "limit_reason", "evidence_ids"):
            s += " %s=%s" % (k, json.dumps(m[k], ensure_ascii=False))
    if m.get("limit_reason"):
        s += " LIMIT=%s" % m.get("limit_reason")
    return s

def side(sd, label):
    if not sd:
        print("   ", label, "None")
        return
    print("   ", label, "points=%s" % sd.get("points"))
    print("      A:", mon(sd.get("active")))
    for b in sd.get("bench_in_position_order") or []:
        print("      B%s:" % (b.get("bench_position") if isinstance(b, dict) else "?"), mon(b))
    ez = sd.get("energy_zone")
    if ez:
        print("      EZ now=%s next=%s" % ((ez.get("this_turn") or {}).get("type"), (ez.get("next") or {}).get("type")))
    if sd.get("board_effects"):
        print("      board_effects:", json.dumps(sd.get("board_effects"), ensure_ascii=False))
    for k in sd:
        if k not in ("active", "bench_in_position_order", "points", "energy_zone", "board_effects", "evidence_ids", "status", "limit_reason"):
            print("      %s: %s" % (k, json.dumps(sd[k], ensure_ascii=False)[:600]))
    if sd.get("limit_reason"):
        print("      LIMIT:", sd.get("limit_reason"))

def board(b, label):
    if not b:
        print("  ", label, "None")
        return
    print("  ", label, "turn_disp=%s phase=%s stadium=%s" % (b.get("turn_number_displayed"), b.get("phase"), json.dumps(b.get("stadium"), ensure_ascii=False)))
    side(b.get("owner"), "OWNER")
    side(b.get("opponent"), "OPP")
    if b.get("shared_effects"):
        print("    shared_effects:", json.dumps(b.get("shared_effects"), ensure_ascii=False))
    for k in b:
        if k not in ("turn_number_displayed", "phase", "stadium", "owner", "opponent", "shared_effects", "evidence_ids"):
            print("    %s: %s" % (k, json.dumps(b[k], ensure_ascii=False)[:800]))

def hand(h):
    if not h:
        return "None"
    if isinstance(h, dict):
        cs = h.get("cards_left_to_right") or h.get("cards") or []
        names = []
        for c in cs:
            if isinstance(c, dict):
                n = c.get("name")
                if c.get("variant"):
                    n += "[%s]" % c.get("variant")
                names.append(n)
            else:
                names.append(str(c))
        extra = {k: v for k, v in h.items() if k not in ("cards_left_to_right", "cards", "evidence_ids", "basis")}
        return "%s | %s" % (names, json.dumps(extra, ensure_ascii=False)[:500])
    return json.dumps(h, ensure_ascii=False)[:500]

for r in d["turns"]:
    print("=" * 110)
    print("TURN %s who=%s" % (r["turn_number"], r["who_played"]))
    for hk in ("hand_at_start", "owner_hand_start", "owner_hand_before_end_action", "owner_hand_end"):
        if hk in r:
            print("  %s: %s" % (hk, hand(r.get(hk))))
    print("  opp_hand_at_owner_turn_start:", json.dumps(r.get("opponent_hand_at_owner_turn_start"), ensure_ascii=False)[:400])
    for ds in r.get("draws_and_searches") or []:
        print("  DRAW kind=%s by=%s linked=%s cards=%s returned=%s limit=%s" % (ds.get("kind"), ds.get("caused_by"), ds.get("linked_play_order"), [c.get("name") for c in ds.get("cards_in_reveal_order") or []], ds.get("returned_or_discarded_cards"), ds.get("limit_reason")))
    for p in r.get("plays_in_order") or []:
        s = "  PLAY %s %s card=%s target=%s result=%s" % (p.get("order"), p.get("kind"), p.get("card_name"), p.get("target"), p.get("result"))
        if p.get("energy"):
            s += " energy=%s" % json.dumps(p.get("energy"), ensure_ascii=False)
        if p.get("nested_events_in_order"):
            s += " nested=%s" % json.dumps(p.get("nested_events_in_order"), ensure_ascii=False)
        if p.get("prompt_text") or p.get("response"):
            s += " prompt=%s resp=%s" % (p.get("prompt_text"), p.get("response"))
        for k in p:
            if k not in ("order", "kind", "card_name", "target", "result", "energy", "nested_events_in_order", "prompt_text", "response", "source_video", "timestamp_seconds", "evidence_ids", "basis", "limit_reason", "hand_count_after", "timing_basis"):
                s += " %s=%s" % (k, json.dumps(p[k], ensure_ascii=False))
        if p.get("hand_count_after") is not None:
            s += " hca=%s" % p.get("hand_count_after")
        if p.get("limit_reason"):
            s += " LIMIT=%s" % p.get("limit_reason")
        print(s)
    for a in r.get("automatic_events_in_order") or []:
        print("  AUTO", json.dumps({k: v for k, v in a.items() if k not in ("evidence_ids", "source_video")}, ensure_ascii=False))
    board(r.get("board_at_start"), "BOARD_AT_START")
    board(r.get("board_after"), "BOARD_AFTER")
    if r.get("limits"):
        print("  LIMITS:", json.dumps(r.get("limits"), ensure_ascii=False)[:1500])
    if r.get("hand_reconciliation"):
        print("  HAND_RECON:", json.dumps(r.get("hand_reconciliation"), ensure_ascii=False)[:1500])
    if r.get("discard_snapshot_ids"):
        print("  discard_snapshot_ids:", r.get("discard_snapshot_ids"))
print("GAME LIMITS:", json.dumps(d.get("limits"), ensure_ascii=False, indent=1))
