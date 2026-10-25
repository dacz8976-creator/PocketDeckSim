#!/usr/bin/env python3
"""Part A's turn list from the first coding (SELCHECK_JOB.md Part A): selcode_in_p<k>/turns.json from inv_out_p<k>/inventory.json.

  make_turns.py EXAM_V2_DIR PART

Mechanical: for every game of inv_in_p<k>/window.json, every one of his turns the usability job listed, as
{"point_id": "LAD-<game>-t<global turn>", "game", "global_turn", "clip"}, and NOTHING else (no *_known, real_choice, usable, kind,
one-line or reason). Stops on: a game of the part missing from the inventory or one not in the part; a turn whose point id isn't
LAD-<game>-t<global turn>; a repeated point id; a field shape it can't read unambiguously; an existing turns.json.
The inventory's field names are the worker's; the accepted spellings are listed below, and anything else stops the run.
"""
import hashlib, json, os, stat, sys

GAME_KEYS = ('game', 'game_id', 'id')
TURNS_KEYS = ('turns', 'his_turns')
PID_KEYS = ('point_id', 'id')
GT_KEYS = ('global_turn', 'global_turn_count', 'source_global_turn')
CLIP_KEYS = ('clip', 'clip_index', 'clip_order')


def one(d, keys, what, required=True):
    found = [k for k in keys if k in d]
    if len(found) > 1 and len({json.dumps(d[k]) for k in found}) > 1:
        sys.exit(f'{what}: two different values under {found}: stop')
    if not found:
        if required:
            sys.exit(f'{what}: none of {keys} in {sorted(d)[:12]}: stop')
        return None
    return d[found[0]]


def clip_no(v, what):
    if v is None:
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s.isdigit():
            return int(s)
        if s.startswith('clip') and s[4:6].isdigit():
            return int(s[4:6])
    sys.exit(f'{what}: clip {v!r} is not a clip number: stop')


def main():
    e2, k = sys.argv[1], int(sys.argv[2])
    out = os.path.join(e2, f'selcode_in_p{k}', 'turns.json')
    if os.path.exists(out):
        sys.exit(f'{out} exists already: stop')
    window = json.load(open(os.path.join(e2, f'inv_in_p{k}', 'window.json'), encoding='utf-8'))
    want = {g['game']: g for g in window['games']}
    inv = json.load(open(os.path.join(e2, f'inv_out_p{k}', 'inventory.json'), encoding='utf-8'))
    games = inv if isinstance(inv, list) else one(inv, ('games',), 'inventory.json')
    if isinstance(games, dict):  # keyed by game id
        games = [dict(v, game=g) if 'game' not in v else v for g, v in games.items()]
    seen_games, turns, ids = set(), [], set()
    for g in games:
        gid = one(g, GAME_KEYS, 'a game')
        if gid not in want:
            sys.exit(f'inventory game {gid} is not a game of part {k}: stop')
        if gid in seen_games:
            sys.exit(f'game {gid} twice in the inventory: stop')
        seen_games.add(gid)
        multi = want[gid]['clips'] > 1
        for t in one(g, TURNS_KEYS, f'game {gid}'):
            pid = one(t, PID_KEYS, f'a turn of {gid}')
            gt = one(t, GT_KEYS, f'turn {pid}')
            if not isinstance(gt, int):
                sys.exit(f'{pid}: global turn {gt!r} is not a whole number: stop')
            if pid != f'LAD-{gid}-t{gt}':
                sys.exit(f'{pid}: not LAD-{gid}-t{gt}: stop')
            if pid in ids:
                sys.exit(f'{pid} twice: stop')
            ids.add(pid)
            c = clip_no(one(t, CLIP_KEYS, f'turn {pid}', required=multi), pid)
            if not multi:
                c = 1 if c in (None, 1) else sys.exit(f'{pid}: clip {c} in a one-clip game: stop')
            elif not 1 <= c <= want[gid]['clips']:
                sys.exit(f'{pid}: clip {c} outside 1..{want[gid]["clips"]}: stop')
            turns.append({'point_id': pid, 'game': gid, 'global_turn': gt, 'clip': c})
    missing = sorted(set(want) - seen_games)
    if missing:
        sys.exit(f'games of part {k} missing from the inventory: {missing}: stop')
    turns.sort(key=lambda t: (t['game'], t['global_turn']))
    for t in turns:
        assert set(t) == {'point_id', 'game', 'global_turn', 'clip'}
    # the staged folder is read-only (stage_jobs.py): open it for this one file, then close it again
    d = os.path.dirname(out)
    mode = os.stat(d).st_mode
    os.chmod(d, mode | stat.S_IWUSR)
    try:
        with open(out, 'w', encoding='utf-8') as f:
            json.dump({'format': 'pds-exam-v2-turns', 'part': k,
                       'what': "his turns as the first coding listed them, every coded field removed (make_turns.py)", 'turns': turns},
                      f, indent=1, ensure_ascii=False)
        os.chmod(out, 0o444)
    finally:
        os.chmod(d, mode)
    rec = os.path.join(e2, f'TURNS_RECORD_p{k}.json')
    with open(rec, 'w', encoding='utf-8') as f:
        json.dump({'turns_json': out, 'sha256': hashlib.sha256(open(out, 'rb').read()).hexdigest(), 'turns': len(turns),
                   'games': len(seen_games), 'from': {'inventory': os.path.join(e2, f'inv_out_p{k}', 'inventory.json'),
                   'sha256': hashlib.sha256(open(os.path.join(e2, f'inv_out_p{k}', 'inventory.json'), 'rb').read()).hexdigest()}}, f, indent=1)
    print(f'part {k}: {len(turns)} turns from {len(seen_games)} games -> {out} (record {rec})')


if __name__ == '__main__':
    main()
