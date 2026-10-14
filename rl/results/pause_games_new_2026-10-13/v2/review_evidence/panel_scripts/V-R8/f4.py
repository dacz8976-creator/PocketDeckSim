import json, re, glob, os, collections
Q = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
games = sorted(glob.glob(Q + "BATCH_2026-10-1[23]_*/2026101*_iOS/TURN_LEDGER.json"))
print(len(games), 'ledgers')
kinds = collections.Counter()
def nk(kind):
    k = str(kind or '').strip().lower().replace(' ', '_')
    if k in ('card_play', 'item', 'supporter', 'trainer'): return 'card_play'
    if k == 'card_play_attempt': return 'attempt'
    if k in ('energy_attachment', 'energy', 'attach_energy'): return 'energy_attachment'
    if k in ('bench', 'bench_basic', 'bench_pokemon'): return 'bench'
    if k in ('evolution', 'evolve'): return 'evolution'
    if k in ('tool', 'tool_attachment'): return 'tool'
    if k in ('stadium', 'item_evolution', 'retreat', 'attack', 'prompt_response'): return k
    if k in ('ability', 'stadium_ability', 'stadium_effect'): return 'ability'
    if k in ('end_turn', 'end_turn_request'): return 'end'
    return 'other'
for g in games:
    led = json.load(open(g, encoding="utf-8"))
    gid = os.path.basename(os.path.dirname(g))
    for t in led['turns']:
        owner = str(t.get('who_played', '')).startswith('owner')
        for i, p in enumerate(t.get('plays_in_order') or []):
            k = str(p.get('kind'))
            if owner:
                kinds[(k, nk(k))] += 1
            if owner and (nk(k) == 'other' or 'Mesagoza' in json.dumps(p, ensure_ascii=False)):
                print(gid, 't', t.get('turn_number'), 'play', i, {kk: p.get(kk) for kk in ('kind', 'card_name', 'target', 'result', 'details')})
print()
for (k, n), c in sorted(kinds.items()):
    print(f'{c:5d}  {k!r} -> {n}')
