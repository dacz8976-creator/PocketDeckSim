import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
G = {"203719": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_203719000_iOS/",
     "225319": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_225319000_iOS/"}
OUT = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R2/"


def poke(x):
    if not isinstance(x, dict):
        return str(x)
    e = (x.get("attached_energy") or {}).get("by_type") or {}
    s = f"{x.get('name')}[{x.get('variant')}] hp {x.get('hp_now')}/{x.get('hp_max')} dmg {x.get('damage')}"
    if e:
        s += " E" + json.dumps(e)
    if x.get("tool") not in (None, "none"):
        s += f" tool={x.get('tool')}"
    if x.get("special_conditions"):
        s += f" COND={x.get('special_conditions')}"
    if x.get("active_effects"):
        s += f" EFF={x.get('active_effects')}"
    if x.get("status") not in ("observed", None):
        s += f" status={x.get('status')}"
    if x.get("limit_reason"):
        s += f" LIMIT={x.get('limit_reason')}"
    if x.get("hp_max_basis") and x.get("hp_max_basis") not in ("Visible card and HP display",):
        s += f" hpbasis={x.get('hp_max_basis')}"
    return s


def side(S):
    if not S:
        return "  (none)"
    out = []
    out.append(f"   ACT: {poke(S.get('active'))}")
    for b in S.get("bench_in_position_order") or []:
        out.append(f"   BEN: {poke(b)}")
    ez = S.get("energy_zone") or {}
    if ez:
        out.append(f"   EZ: now={json.dumps(ez.get('this_turn'))} next={json.dumps(ez.get('next'))}")
    out.append(f"   points={S.get('points')} board_effects={S.get('board_effects')} status={S.get('status')} limit={S.get('limit_reason')}")
    return "\n".join(out)


def board(B, label):
    if not B:
        return f"  {label}: none"
    return (f"  {label}: displayed={B.get('turn_number_displayed')} phase={B.get('phase')} stadium={B.get('stadium')} shared={B.get('shared_effects')}\n"
            f"  OWNER\n{side(B.get('owner'))}\n  OPP\n{side(B.get('opponent'))}")


def hand(H):
    if not H:
        return "None"
    c = H.get("cards_left_to_right")
    if c is None:
        return f"hidden count={H.get('count')} status={H.get('status')}"
    return f"{len(c)}: " + ", ".join(f"{x.get('name')}" + (f"[{x.get('variant')}]" if x.get('variant') else "") + (f"(LIM:{x.get('limit_reason')})" if x.get('limit_reason') else "") for x in c) + (f" count={H.get('count')}" if H.get('count') is not None else "")


for g, p in G.items():
    L = json.load(open(p + "TURN_LEDGER.json"))
    lines = []
    for t in L["turns"]:
        lines.append("=" * 100)
        lines.append(f"TURN {t['turn_number']} who={t['who_played']} timing={json.dumps(t.get('timing'))}")
        lines.append(f" hand_at_start: {hand(t.get('hand_at_start'))}")
        lines.append(f" owner_hand_start: {hand(t.get('owner_hand_start'))}")
        lines.append(f" opp_hand_at_owner_start: {json.dumps(t.get('opponent_hand_at_owner_turn_start'), ensure_ascii=False)}")
        for d in t.get("draws_and_searches") or []:
            cards = [c.get("name") for c in d.get("cards_in_reveal_order") or []]
            dd = {k: v for k, v in d.items() if k not in ("cards_in_reveal_order",)}
            lines.append(f" DRAW: {cards} {json.dumps(dd, ensure_ascii=False)}")
        for pl in t.get("plays_in_order") or []:
            pp = {k: v for k, v in pl.items() if k not in ("evidence_ids", "source_video", "basis")}
            lines.append(f" PLAY: {json.dumps(pp, ensure_ascii=False)}")
        for ev in t.get("automatic_events_in_order") or []:
            lines.append(f" AUTO: {json.dumps(ev, ensure_ascii=False)}")
        lines.append(board(t.get("board_at_start"), "BOARD_START"))
        lines.append(board(t.get("board_after"), "BOARD_AFTER"))
        lines.append(f" owner_hand_end: {hand(t.get('owner_hand_end'))}")
        if t.get("owner_hand_before_end_action"):
            lines.append(f" owner_hand_before_end_action: {hand(t.get('owner_hand_before_end_action'))}")
        lines.append(f" discard_snapshot_ids={t.get('discard_snapshot_ids')}")
        lines.append(f" limits={json.dumps(t.get('limits'), ensure_ascii=False)}")
        if t.get("hand_reconciliation"):
            lines.append(f" hand_recon={json.dumps(t.get('hand_reconciliation'), ensure_ascii=False)}")
    open(OUT + f"ledger_{g}.txt", "w").write("\n".join(lines))
    print(g, len(lines))
