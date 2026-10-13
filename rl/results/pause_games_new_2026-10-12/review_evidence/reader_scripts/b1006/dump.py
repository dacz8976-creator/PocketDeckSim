import json, sys
B = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/'
P = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/positions_all.json'
g, tn = sys.argv[1], int(sys.argv[2])
what = sys.argv[3] if len(sys.argv) > 3 else 'all'
short = g.replace('_iOS', '')[2:]
pid = f'KW-{short}-t{tn:02d}'
pos = [p for p in json.load(open(P, encoding='utf-8')) if p['id'] == pid]
DROP = {'evidence_ids', 'turn_evidence_ids', 'evidence', 'frame_ids', 'evidence_frame_ids', 'discard_snapshot_ids', 'source_video', 'timing'}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in DROP and not k.endswith('evidence_ids') and not k.endswith('_frames')}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o


if what in ('all', 'pos'):
    print('=== POSITION', pid)
    print(json.dumps(pos[0] if pos else None, ensure_ascii=False, indent=1))
if what in ('all', 'led'):
    led = json.load(open(B + g + '/TURN_LEDGER.json', encoding='utf-8'))
    t = [x for x in led['turns'] if x['turn_number'] == tn][0]
    print('=== LEDGER turn', tn, t.get('who_played'))
    keys = sys.argv[4].split(',') if len(sys.argv) > 4 else None
    for k, v in t.items():
        if keys and k not in keys:
            continue
        if k in DROP:
            continue
        print('--', k)
        print(json.dumps(strip(v), ensure_ascii=False, indent=1))
