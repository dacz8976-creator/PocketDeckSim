"""survey of ledger shapes in the 14 packets: keys of rows / board sides / Pokemon, non-empty effects, conditions, stacks, deck counts, kinds of plays"""
import json, os, collections
R8 = '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/R8'
games = [l.strip() for l in open(os.path.join(R8, 'games.txt')) if l.strip()]
rowkeys, sidekeys, pkeys, kinds = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
for g in games:
    nm = os.path.basename(g)[2:15]
    led = json.load(open(os.path.join(g, 'TURN_LEDGER.json'), encoding='utf-8'))
    print('=' * 10, nm, 'top keys', [k for k in led.keys() if k != 'turns'], 'rows', len(led['turns']))
    for t in led['turns']:
        rowkeys.update(t.keys())
        for bk in ('board_at_start', 'board_after'):
            b = t.get(bk) or {}
            for sd in ('owner', 'opponent'):
                s = b.get(sd) or {}
                sidekeys.update(s.keys())
                if s.get('board_effects'):
                    print(f'  t{t["turn_number"]} {t["who_played"][:5]} {bk} {sd} board_effects: {json.dumps(s["board_effects"], ensure_ascii=False)[:300]}')
                for k in ('deck_count', 'deck_size', 'cards_in_deck', 'discard', 'discard_pile', 'discard_count'):
                    if k in s and s[k] not in (None, [], {}):
                        print(f'  t{t["turn_number"]} {bk} {sd} {k}: {json.dumps(s[k], ensure_ascii=False)[:200]}')
                for p in [s.get('active')] + list(s.get('bench_in_position_order') or []):
                    if not isinstance(p, dict):
                        continue
                    pkeys.update(p.keys())
                    if p.get('active_effects'):
                        print(f'  t{t["turn_number"]} {t["who_played"][:5]} {bk} {sd} {p.get("name")} active_effects: {json.dumps(p["active_effects"], ensure_ascii=False)[:300]}')
                    if p.get('special_conditions'):
                        print(f'  t{t["turn_number"]} {t["who_played"][:5]} {bk} {sd} {p.get("name")} conditions: {p["special_conditions"]}')
                    for k in ('evolution_stack', 'evolution_stack_under_top', 'evolution_stack_bottom_to_top'):
                        if p.get(k):
                            pass
            if b.get('shared_effects'):
                print(f'  t{t["turn_number"]} {bk} shared_effects: {json.dumps(b["shared_effects"], ensure_ascii=False)[:300]}')
        for p in t.get('plays_in_order') or []:
            kinds[str(p.get('kind'))] += 1
print('ROW KEYS', dict(rowkeys))
print('SIDE KEYS', dict(sidekeys))
print('POKEMON KEYS', dict(pkeys))
print('PLAY KINDS', dict(kinds))
