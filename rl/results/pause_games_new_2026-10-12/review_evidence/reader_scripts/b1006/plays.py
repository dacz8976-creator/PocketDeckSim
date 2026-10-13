import json, sys
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
g = sys.argv[1]
upto = int(sys.argv[2]) if len(sys.argv) > 2 else 999
led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))


def brief(s):
    out = []
    for p in [s.get('active')] + list(s.get('bench_in_position_order') or []):
        if isinstance(p, dict) and p.get('name'):
            e = (p.get('attached_energy') or {}).get('by_type')
            out.append(f"{p['name']}@{p.get('bench_position')} {p.get('hp_now')}/{p.get('hp_max')} E={json.dumps(e)} T={p.get('tool')}")
    return ' | '.join(out)


for t in led['turns']:
    if t['turn_number'] > upto:
        break
    print(f"--- T{t['turn_number']} {t.get('who_played')}")
    for pl in t.get('plays_in_order') or []:
        e = pl.get('energy') or {}
        print(f"   {pl.get('order')} {pl.get('kind')} card={pl.get('card_name')} tgt={pl.get('target')} E={e.get('type')}x{e.get('count')} pay={e.get('retreat_payment_by_type')} | {str(pl.get('result'))[:200]}")
    for a in t.get('automatic_events_in_order') or []:
        print('   auto', json.dumps(a, ensure_ascii=False)[:200])
    ba = t.get('board_after') or {}
    print('   after owner:', brief(ba.get('owner') or {}), 'pts', (ba.get('owner') or {}).get('points'))
    print('   after opp  :', brief(ba.get('opponent') or {}), 'pts', (ba.get('opponent') or {}).get('points'), 'stadium', json.dumps(ba.get('stadium'), ensure_ascii=False))
