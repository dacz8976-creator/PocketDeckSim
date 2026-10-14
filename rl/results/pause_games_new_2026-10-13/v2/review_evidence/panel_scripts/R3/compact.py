import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "210041": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
 "230258": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
}
g = sys.argv[1]
d = json.load(open(paths[g], encoding='utf-8'))

STD = {"name", "variant", "hp_now", "hp_max", "hp_max_basis", "damage", "attached_energy", "tool", "status", "bench_position",
       "evidence_ids", "basis", "limit_reason"}
allkeys = {}

def mon(p):
    if not isinstance(p, dict):
        return repr(p)
    for k in p:
        allkeys[k] = allkeys.get(k, 0) + 1
    e = p.get("attached_energy") or {}
    en = e.get("by_type") or ({} if not e.get("total") else {"?": e.get("total")})
    s = f"{p.get('name')}"
    if p.get('variant'):
        s += f" [{p.get('variant')}]"
    s += f" hp {p.get('hp_now')}/{p.get('hp_max')} dmg {p.get('damage')} E{dict(en)} tool={p.get('tool')}"
    if p.get('bench_position') is not None:
        s += f" pos{p.get('bench_position')}"
    extra = {}
    for k, v in p.items():
        if k in STD:
            continue
        if k == 'special_conditions' and not v:
            continue
        if k == 'active_effects':
            v = [(x.get('name') if isinstance(x, dict) else x) for x in (v or [])]
            if not v:
                continue
        extra[k] = v
    if extra:
        s += " EXTRA " + json.dumps(extra, ensure_ascii=False)
    if p.get('limit_reason'):
        s += " LIMIT: " + str(p.get('limit_reason'))
    if p.get('status') not in (None, 'observed'):
        s += f" status={p.get('status')}"
    return s

def ez(z):
    z = z or {}
    out = []
    for k in ('this_turn', 'next'):
        x = z.get(k) or {}
        out.append(f"{k}={x.get('type')}:{x.get('count')}:{x.get('available')}")
    return ' '.join(out)

def side(sd, label):
    out = []
    if not isinstance(sd, dict):
        return [f"  {label}: {sd!r}"]
    out.append(f"  {label}: points={sd.get('points')} ez {ez(sd.get('energy_zone'))}")
    out.append("    A: " + mon(sd.get('active')))
    for b in sd.get('bench_in_position_order') or []:
        out.append("    B: " + mon(b))
    extra = {}
    for k, v in sd.items():
        if k in ('points', 'energy_zone', 'active', 'bench_in_position_order', 'status', 'evidence_ids'):
            continue
        if k == 'board_effects':
            v = [(x.get('name') if isinstance(x, dict) else x) for x in (v or [])]
        if v in (None, [], {}, ''):
            continue
        extra[k] = v
    if extra:
        out.append("    side-extra: " + json.dumps(extra, ensure_ascii=False))
    return out

def board(b, label):
    print(f" {label}: phase={b.get('phase')} stadium={b.get('stadium')}")
    for l in side(b.get('owner'), 'OWNER'):
        print(l)
    for l in side(b.get('opponent'), 'OPP'):
        print(l)
    extra = {}
    for k, v in b.items():
        if k in ('phase', 'stadium', 'owner', 'opponent', 'associated_ledger_turn_number', 'turn_number_limit', 'evidence_ids'):
            continue
        if k == 'shared_effects':
            v = [(x.get('name') if isinstance(x, dict) else x) for x in (v or [])]
        if v in (None, [], {}, ''):
            continue
        extra[k] = v
    if extra:
        print("   board-extra: " + json.dumps(extra, ensure_ascii=False))

def hand(h):
    if not isinstance(h, dict):
        return repr(h)
    cs = h.get('cards_left_to_right')
    names = [(str(c.get('name')) + (f"[{c.get('variant')}]" if c.get('variant') else '')) for c in cs] if cs else cs
    return f"count={h.get('count')} status={h.get('status')} {names}" + (f" LIMIT {h.get('limit_reason')}" if h.get('limit_reason') else '')

for t in d['turns']:
    print("=" * 40, "TURN", t['turn_number'], t['who_played'])
    own = str(t['who_played']).startswith('owner')
    if own:
        print(" hand_at_start:", hand(t.get('hand_at_start')))
        print(" owner_hand_start:", hand(t.get('owner_hand_start')))
        o = t.get('opponent_hand_at_owner_turn_start') or {}
        print(" opp_hand_at_owner_start:", o.get('count'), o.get('supported_range'), o.get('limit_reason') or '')
    for ds in t.get('draws_and_searches') or []:
        names = [c.get('name') for c in ds.get('cards_in_reveal_order') or []]
        print(f" DRAW {ds.get('kind')} by={ds.get('caused_by')} link={ds.get('linked_play_order')} names={names} {ds.get('hand_count_before')}->{ds.get('hand_count_after')} ret={ds.get('returned_or_discarded_cards')}")
    for p in t.get('plays_in_order') or []:
        q = {k: v for k, v in p.items() if k not in ('evidence_ids', 'source_video', 'timestamp_seconds', 'basis', 'limit_reason') and v not in (None, [], {}, '')}
        if isinstance(q.get('energy'), dict):
            q['energy'] = {k: v for k, v in q['energy'].items() if v is not None}
            if not q['energy']:
                q.pop('energy')
        print(" PLAY", json.dumps(q, ensure_ascii=False))
    for a in t.get('automatic_events_in_order') or []:
        if isinstance(a, dict):
            q = {k: v for k, v in a.items() if k not in ('evidence_ids', 'source_video', 'timestamp_seconds', 'basis') and v not in (None, [], {}, '')}
        else:
            q = a
        print(" AUTO", json.dumps(q, ensure_ascii=False))
    board(t.get('board_at_start') or {}, 'START')
    board(t.get('board_after') or {}, 'AFTER')
    if own:
        print(" hand_before_end:", hand(t.get('owner_hand_before_end_action')))
        print(" hand_end:", hand(t.get('owner_hand_end')))
    for l in t.get('limits') or []:
        print(" LIMIT:", l)
print("ALLKEYS", allkeys)
