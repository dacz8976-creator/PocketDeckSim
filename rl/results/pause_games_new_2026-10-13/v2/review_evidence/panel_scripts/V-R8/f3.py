import json, re, glob, os
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
games = sorted(glob.glob(Q + "BATCH_2026-10-1[23]_*/2026101*_iOS/TURN_LEDGER.json"))
pat = re.compile(r'Giga Turbo', re.I)
for g in games:
    led = json.load(open(g, encoding="utf-8"))
    gid = os.path.basename(os.path.dirname(g))
    for t in led['turns']:
        if not str(t.get('who_played', '')).startswith('owner'):
            continue
        for p in t.get('plays_in_order') or []:
            s = json.dumps(p, ensure_ascii=False)
            if pat.search(s):
                print(gid, 't', t.get('turn_number'), {k: p.get(k) for k in ('kind', 'card_name', 'target', 'result', 'details', 'energy')})
                for ne in p.get('nested_events_in_order') or []:
                    print('      nested:', json.dumps(ne, ensure_ascii=False)[:400])
        for ev in t.get('automatic_events_in_order') or []:
            s = json.dumps(ev, ensure_ascii=False)
            if re.search(r'Giga Turbo|Colorless', s):
                print(gid, 't', t.get('turn_number'), 'EVENT', s[:400])
        # board_after: Alolan Muk energy
        for p in ([((t.get('board_after') or {}).get('owner') or {}).get('active')] + list(((t.get('board_after') or {}).get('owner') or {}).get('bench_in_position_order') or [])):
            if isinstance(p, dict) and 'Colorless' in json.dumps(p.get('attached_energy'), ensure_ascii=False):
                print(gid, 't', t.get('turn_number'), 'AFTER has Colorless:', p.get('name'), p.get('bench_position'), p.get('attached_energy'))
