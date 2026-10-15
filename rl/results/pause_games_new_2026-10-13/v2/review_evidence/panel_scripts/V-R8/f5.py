import json, re, glob, os
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
want = {"20261012_210823000_iOS": 8, "20261013_020824000_iOS": 11, "20261012_203719000_iOS": 7}
def brd(side):
    out = []
    for p in [side.get('active')] + list(side.get('bench_in_position_order') or []):
        if isinstance(p, dict):
            out.append((p.get('name'), p.get('bench_position'), p.get('instance_id') or p.get('physical_instance'), p.get('hp_now'), (p.get('attached_energy') or {}).get('by_type')))
    return out
for g in sorted(glob.glob(Q + "BATCH_2026-10-1[23]_*/2026101*_iOS/TURN_LEDGER.json")):
    gid = os.path.basename(os.path.dirname(g))
    if gid not in want:
        continue
    led = json.load(open(g, encoding="utf-8"))
    for t in led['turns']:
        if t.get('turn_number') != want[gid]:
            continue
        print('=====', gid, 't', t.get('turn_number'), t.get('who_played'))
        print('START', brd(((t.get('board_at_start') or {}).get('owner') or {})))
        for i, p in enumerate(t.get('plays_in_order') or []):
            print(' ', i, {k: p.get(k) for k in ('kind', 'card_name', 'target', 'result', 'details', 'prompt_text', 'response')}, 'energy', p.get('energy'))
            for ne in p.get('nested_events_in_order') or []:
                print('       nested', json.dumps(ne, ensure_ascii=False)[:300])
        for ev in t.get('automatic_events_in_order') or []:
            print('  EV', json.dumps(ev, ensure_ascii=False)[:300])
        print('AFTER', brd(((t.get('board_after') or {}).get('owner') or {})))
