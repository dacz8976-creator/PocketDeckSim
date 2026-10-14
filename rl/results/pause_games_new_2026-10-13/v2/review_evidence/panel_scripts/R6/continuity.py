import json, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"

def sig(m):
    if not m or not isinstance(m, dict) or not m.get("name"):
        return None
    e = (m.get("attached_energy") or {}).get("by_type") or {}
    return (m.get("name"), m.get("hp_now"), m.get("hp_max"), tuple(sorted(e.items())), m.get("tool"), tuple(m.get("special_conditions") or []))

def side(s):
    if not s:
        return None
    return (s.get("points"), sig(s.get("active")), tuple(sig(b) for b in s.get("bench_in_position_order") or []))

for g in ["20261013_010837000_iOS", "20261013_014423000_iOS"]:
    d = json.load(open(base + g + "/TURN_LEDGER.json", encoding="utf-8"))
    rows = d["turns"]
    print("=" * 60, g)
    for a, b in zip(rows, rows[1:]):
        for who in ("owner", "opponent"):
            x = side((a.get("board_after") or {}).get(who))
            y = side((b.get("board_at_start") or {}).get(who))
            if x != y:
                print("turn %s after -> turn %s start, %s differ:\n   %s\n   %s" % (a["turn_number"], b["turn_number"], who, x, y))
        sa = (a.get("board_after") or {}).get("stadium")
        sb = (b.get("board_at_start") or {}).get("stadium")
        if sa != sb:
            print("stadium differs", a["turn_number"], sa, sb)
    # hand continuity for owner turns
    own = [r for r in rows if str(r.get("who_played")).startswith("owner")]
    for a, b in zip(own, own[1:]):
        he = [c.get("name") for c in (a.get("owner_hand_end") or {}).get("cards_left_to_right") or []]
        hs = [c.get("name") for c in (b.get("hand_at_start") or {}).get("cards_left_to_right") or []]
        dr = [c.get("name") for ds in b.get("draws_and_searches") or [] if ds.get("kind") == "normal_draw" for c in ds.get("cards_in_reveal_order") or []]
        import collections
        if collections.Counter(he) + collections.Counter(dr) != collections.Counter(hs):
            print("HAND continuity: turn %s end %s + draw %s != turn %s start %s" % (a["turn_number"], he, dr, b["turn_number"], hs))
        else:
            print("hand ok: t%s end %s + %s = t%s start" % (a["turn_number"], he, dr, b["turn_number"]))
