import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "010706": base + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_010706000_iOS/TURN_LEDGER.json",
 "015011": base + "BATCH_2026-10-13_REMAINING_SIX/20261013_015011000_iOS/TURN_LEDGER.json",
}
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R1/"
k = sys.argv[1]
d = json.load(open(paths[k], encoding="utf-8"))
J = lambda x: json.dumps(x, ensure_ascii=False)

def pk(p):
    if not isinstance(p, dict):
        return str(p)
    if "pokemon" in p and "name" not in p:
        if p["pokemon"] is None:
            return "[pos%s empty]" % p.get("position")
        p = p["pokemon"]
    if not p.get("name"):
        return "[empty %s]" % J(p)[:80]
    e = p.get("attached_energy") or {}
    extra = {kk: v for kk, v in p.items() if kk not in ("name", "variant", "hp_now", "hp_max", "damage", "attached_energy", "tool", "special_conditions", "active_effects", "evidence_ids", "status", "limit_reason", "hp_max_basis", "bench_position")}
    s = "%s {%s} bp=%s hp=%s/%s dmg=%s E=%s tool=%s cond=%s eff=%s" % (p.get("name"), p.get("variant"), p.get("bench_position"), p.get("hp_now"), p.get("hp_max"), p.get("damage"), J(e.get("by_type")), p.get("tool"), J(p.get("special_conditions")), J(p.get("active_effects")))
    if extra:
        s += " EXTRA=" + J(extra)
    if p.get("limit_reason"):
        s += " LIM=" + str(p.get("limit_reason"))[:150]
    return s

def side(sd, label):
    out = []
    if not sd:
        return ["  %s: none" % label]
    out.append("  %s ACTIVE: %s" % (label, pk(sd.get("active"))))
    for b in sd.get("bench_in_position_order") or []:
        out.append("  %s BENCH: %s" % (label, pk(b)))
    ez = sd.get("energy_zone")
    out.append("  %s points=%s EZ=%s board_effects=%s" % (label, sd.get("points"), J(ez)[:300] if ez else None, J(sd.get("board_effects"))))
    extra = {kk: v for kk, v in sd.items() if kk not in ("active", "bench_in_position_order", "energy_zone", "points", "board_effects", "evidence_ids", "status", "limit_reason")}
    if extra:
        out.append("  %s EXTRA: %s" % (label, J(extra)[:1500]))
    return out

def board(b, label):
    out = [" %s: stadium=%s shared=%s phase=%s" % (label, J(b.get("stadium")), J(b.get("shared_effects")), b.get("phase"))]
    extra = {kk: v for kk, v in b.items() if kk not in ("owner", "opponent", "stadium", "shared_effects", "phase", "evidence_ids", "turn_number_displayed")}
    if extra:
        out.append("  BOARD EXTRA: " + J(extra)[:1500])
    out += side(b.get("owner"), "OWN")
    out += side(b.get("opponent"), "OPP")
    return out

def hand(h):
    if not h:
        return "None"
    cs = h.get("cards_left_to_right")
    names = [ (c.get("name") + ("(" + c["variant"] + ")" if c.get("variant") else "")) if isinstance(c, dict) else str(c) for c in (cs or [])]
    return "count=%s %s status=%s lim=%s" % (h.get("count"), names, h.get("status"), h.get("limit_reason"))

lines = []
for t in d["turns"]:
    lines.append("=" * 100)
    lines.append("TURN %s %s timing=%s" % (t["turn_number"], t["who_played"], J(t.get("timing"))))
    lines.append(" hand_at_start: " + hand(t.get("hand_at_start")))
    lines.append(" owner_hand_start: " + hand(t.get("owner_hand_start")))
    lines.append(" owner_hand_end: " + hand(t.get("owner_hand_end")))
    lines.append(" opp_hand_at_owner_turn_start: " + J(t.get("opponent_hand_at_owner_turn_start")))
    for kk in t:
        if kk not in ("turn_number", "who_played", "source_video", "timing", "plays_in_order", "automatic_events_in_order", "board_at_start", "board_after", "discard_snapshot_ids", "turn_evidence_ids", "limits", "draws_and_searches", "hand_at_start", "owner_hand_start", "owner_hand_end", "opponent_hand_at_owner_turn_start"):
            lines.append(" OTHER %s: %s" % (kk, J(t[kk])[:2000]))
    lines += board(t.get("board_at_start") or {}, "BOARD_AT_START")
    for ds in t.get("draws_and_searches") or []:
        cards = [c.get("name") for c in ds.get("cards_in_reveal_order") or []]
        lines.append(" DRAW %s by=%s cards=%s before=%s after=%s returned=%s lim=%s" % (ds.get("kind"), ds.get("caused_by"), cards, ds.get("hand_count_before"), ds.get("hand_count_after"), J(ds.get("returned_or_discarded_cards")), ds.get("limit_reason")))
    for p in t.get("plays_in_order") or []:
        extra = {kk: v for kk, v in p.items() if kk not in ("order", "kind", "card_name", "target", "energy", "result", "prompt_text", "response", "nested_events_in_order", "hand_count_after", "source_video", "timestamp_seconds", "evidence_ids", "basis", "limit_reason")}
        lines.append(" PLAY %s [%s] card=%s target=%s energy=%s @%s" % (p.get("order"), p.get("kind"), p.get("card_name"), p.get("target"), J(p.get("energy")), p.get("timestamp_seconds")))
        lines.append("     result=%s" % p.get("result"))
        if p.get("prompt_text") or p.get("response"):
            lines.append("     prompt=%s response=%s" % (p.get("prompt_text"), p.get("response")))
        if p.get("nested_events_in_order"):
            lines.append("     nested=%s" % J(p.get("nested_events_in_order")))
        if p.get("limit_reason"):
            lines.append("     lim=%s" % p.get("limit_reason"))
        lines.append("     hand_after=%s basis=%s" % (p.get("hand_count_after"), p.get("basis")))
        if extra:
            lines.append("     EXTRA=%s" % J(extra))
    for ev in t.get("automatic_events_in_order") or []:
        lines.append(" AUTO " + J(ev))
    lines += board(t.get("board_after") or {}, "BOARD_AFTER")
    lines.append(" discard_snapshot_ids=" + J(t.get("discard_snapshot_ids")))
    for l in t.get("limits") or []:
        lines.append(" LIMIT " + str(l))
open(OUT + "summ_" + k + ".txt", "w", encoding="utf-8").write("\n".join(lines))
print("ok", len(lines))
