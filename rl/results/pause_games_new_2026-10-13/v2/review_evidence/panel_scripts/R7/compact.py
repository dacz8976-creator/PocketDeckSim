import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX"
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R7"
d = sys.argv[1]
L = json.load(open(QA + "/" + d + "/TURN_LEDGER.json"))


def pk(p):
    if p is None:
        return "None"
    if not isinstance(p, dict):
        return json.dumps(p, ensure_ascii=False)
    e = p.get("attached_energy") or {}
    s = "%s [%s] hp %s/%s dmg %s E%s tool=%s cond=%s" % (
        p.get("name"), p.get("variant"), p.get("hp_now"), p.get("hp_max"), p.get("damage"),
        json.dumps(e.get("by_type"), ensure_ascii=False) + "(%s)" % e.get("total"), p.get("tool"), p.get("special_conditions"))
    extra = {k: v for k, v in p.items() if k not in ("name", "variant", "hp_now", "hp_max", "damage", "attached_energy", "tool", "special_conditions", "hp_max_basis", "status", "limit_reason", "bench_position")}
    if extra.get("active_effects") == []:
        extra.pop("active_effects")
    if extra:
        s += " EXTRA " + json.dumps(extra, ensure_ascii=False)
    if p.get("limit_reason"):
        s += " LIMIT " + str(p.get("limit_reason"))
    if p.get("bench_position") is not None:
        s = "b%s " % p.get("bench_position") + s
    return s


def side(sd, label):
    lines = []
    if sd is None:
        return ["  %s: None" % label]
    lines.append("  %s points=%s board_effects=%s" % (label, sd.get("points"), json.dumps(sd.get("board_effects"), ensure_ascii=False)))
    lines.append("    A: " + pk(sd.get("active")))
    for b in sd.get("bench_in_position_order") or []:
        lines.append("    B: " + pk(b))
    ez = sd.get("energy_zone") or {}
    lines.append("    EZ: now=%s next=%s" % (json.dumps(ez.get("this_turn")), json.dumps(ez.get("next"))))
    other = {k: v for k, v in sd.items() if k not in ("points", "board_effects", "active", "bench_in_position_order", "energy_zone", "status", "evidence_ids")}
    if other:
        lines.append("    OTHER " + json.dumps(other, ensure_ascii=False))
    return lines


def board(b, label):
    if b is None:
        return ["%s: None" % label]
    lines = ["%s: turn_disp=%s phase=%s stadium=%s shared=%s" % (label, b.get("turn_number_displayed"), b.get("phase"), json.dumps(b.get("stadium"), ensure_ascii=False), json.dumps(b.get("shared_effects"), ensure_ascii=False))]
    lines += side(b.get("owner"), "OWNER")
    lines += side(b.get("opponent"), "OPP")
    other = {k: v for k, v in b.items() if k not in ("turn_number_displayed", "phase", "stadium", "shared_effects", "owner", "opponent", "evidence_ids")}
    if other:
        lines.append("  OTHERB " + json.dumps(other, ensure_ascii=False))
    return lines


def hand(h):
    if h is None:
        return "None"
    if not isinstance(h, dict):
        return json.dumps(h, ensure_ascii=False)
    cards = h.get("cards_left_to_right")
    names = None
    if cards:
        names = [(c.get("name"), c.get("variant")) if c.get("variant") else c.get("name") for c in cards]
    return "count=%s status=%s cards=%s limit=%s" % (h.get("count"), h.get("status"), json.dumps(names, ensure_ascii=False), h.get("limit_reason"))


out = open(OUT + "/compact_" + d + ".txt", "w")
for i, t in enumerate(L["turns"]):
    w = out.write
    w("=" * 110 + "\n")
    w("ROW %d turn %s who=%s\n" % (i, t.get("turn_number"), t.get("who_played")))
    w("hand_at_start: " + hand(t.get("hand_at_start")) + "\n")
    w("opp_hand_at_owner_start: " + json.dumps(t.get("opponent_hand_at_owner_turn_start"), ensure_ascii=False) + "\n")
    for ds in t.get("draws_and_searches") or []:
        w("DRAW: kind=%s caused_by=%s cards=%s lim=%s\n" % (ds.get("kind"), ds.get("caused_by"), json.dumps([c.get("name") for c in ds.get("cards_in_reveal_order") or []], ensure_ascii=False), ds.get("limit_reason")))
    for p in t.get("plays_in_order") or []:
        extra = {k: v for k, v in p.items() if k not in ("kind", "card_name", "target", "result", "energy", "nested_events_in_order", "source_video", "timestamp_seconds", "evidence_ids", "basis", "order", "limit_reason")}
        w("PLAY %s: %s | card=%s | target=%s | result=%s | energy=%s | nested=%s | lim=%s | t=%s %s\n" % (
            p.get("order"), p.get("kind"), p.get("card_name"), p.get("target"), p.get("result"),
            json.dumps(p.get("energy"), ensure_ascii=False), json.dumps(p.get("nested_events_in_order"), ensure_ascii=False), p.get("limit_reason"), p.get("timestamp_seconds"),
            ("EXTRA " + json.dumps(extra, ensure_ascii=False)) if extra else ""))
    for a in t.get("automatic_events_in_order") or []:
        w("AUTO: " + json.dumps(a, ensure_ascii=False) + "\n")
    for l in board(t.get("board_at_start"), "BOARD_START"):
        w(l + "\n")
    for l in board(t.get("board_after"), "BOARD_AFTER"):
        w(l + "\n")
    w("hand_end: " + hand(t.get("owner_hand_end")) + "\n")
    w("hand_before_end: " + hand(t.get("owner_hand_before_end_action")) + "\n")
    w("arith: " + json.dumps(t.get("hand_arithmetic"), ensure_ascii=False) + "\n")
    w("discard_snapshot_ids: " + json.dumps(t.get("discard_snapshot_ids"), ensure_ascii=False) + "\n")
    w("limits: " + json.dumps(t.get("limits"), ensure_ascii=False) + "\n")
    other = {k: v for k, v in t.items() if k not in ("turn_number", "who_played", "source_video", "timing", "hand_at_start", "owner_hand_start", "opponent_hand_at_owner_turn_start", "draws_and_searches", "plays_in_order", "automatic_events_in_order", "board_at_start", "board_after", "owner_hand_end", "owner_hand_before_end_action", "hand_arithmetic", "discard_snapshot_ids", "turn_evidence_ids", "limits")}
    if other:
        w("OTHER: " + json.dumps(other, ensure_ascii=False) + "\n")
    if t.get("owner_hand_start") != t.get("hand_at_start") and t.get("who_played") == "owner":
        w("owner_hand_start DIFFERS: " + hand(t.get("owner_hand_start")) + "\n")
out.close()
