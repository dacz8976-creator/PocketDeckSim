#!/usr/bin/env bash
# cross-check: the harness's km3 replays a slice of the official draft A v fire run (rl/results/draft_A_v_fire_2026-10-02) game for game
set -euo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
X=/home/dacz8976/sh/xc
BIN=/home/dacz8976/strength_build/strength
D=rl/results/draft_A_v_fire_2026-10-02
OPP=rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt
rm -rf "$X" && mkdir -p "$X/tree" "$X/official"
git -C "$REPO" archive origin/main decks "$OPP" 2>/dev/null | tar -x -C "$X/tree" || git -C "$REPO" archive origin/main decks rl/results/b2e_card_check_2026-09-26/decks | tar -x -C "$X/tree"
for tag in draftA deck13; do for seat in 0 1; do
  git -C "$REPO" show origin/main:$D/games/${tag}_s${seat}_c00.jsonl > "$X/official/${tag}_s${seat}_c00.jsonl"
done; done
python3 - <<'EOF'
import json, os
X = '/home/dacz8976/sh/xc'
decks = {'draftA': 'decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt', 'deck13': 'decks/dustin/13-a-ninetales-raticate.txt'}
opp = 'rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt'
for tag, path in decks.items():
    for seat in (0, 1):
        d = f'{X}/run_{tag}_s{seat}'; os.makedirs(d, exist_ok=True)
        m = {'name': f'xc_{tag}_s{seat}', 'repo_root': f'{X}/tree', 'stage': 'dev', 'reference': 'km3', 'pilot': 'km3',
             'decks': [{'name': tag, 'path': path}], 'opponents': [{'name': 'fire', 'path': opp}],
             'deals': 50, 'seats': [seat], 'seed_base': 23200000000 + 500 * seat, 'pair_stride': 10000, 'threads': 2,
             'log_level': 'none', 'heldout_decks': [], 'heldout_locked': True}
        json.dump(m, open(f'{d}/manifest.json', 'w'))
EOF
for tag in draftA deck13; do for seat in 0 1; do
  nice -n 19 "$BIN" run --manifest "$X/run_${tag}_s${seat}/manifest.json" --out "$X/run_${tag}_s${seat}" --threads 2 2>&1 | tail -1
done; done
python3 - <<'EOF'
import json
X = '/home/dacz8976/sh/xc'
tot = dict(games=0, winner=0, points=0, turns=0, plies=0, first=0, all=0)
bad = []
for tag in ('draftA', 'deck13'):
    for seat in (0, 1):
        off = {}
        for l in open(f'{X}/official/{tag}_s{seat}_c00.jsonl'):
            r = json.loads(l); off[r['seed']] = r
        mine = {}
        for l in open(f'{X}/run_{tag}_s{seat}/games.jsonl'):
            g = json.loads(l)
            if g['arm'] == 'ref':
                mine[g['seed']] = g
        assert set(off) == set(mine), (tag, seat, len(off), len(mine))
        for s, o in sorted(off.items()):
            g = mine[s]
            ds = seat
            ow = o['outcome'] == {'Win': ds}
            ot = o['outcome'] not in ({'Win': 0}, {'Win': 1})
            mw = g['winner'] == 'deck'
            mt = g['winner'] == 'tie'
            # official final_points are [seat 0, seat 1]; mine are [deck, opp]
            op = [o['final_points'][ds], o['final_points'][1 - ds]]
            ok = dict(winner=(ow == mw and ot == mt), points=(op == g['points']), turns=(o['final_turn'] == g['turns']),
                      plies=(o['plies'] == g['plies']), first=(o['went_first'] == (g['first'] == 'deck')))
            tot['games'] += 1
            for k, v in ok.items():
                tot[k] += int(v)
            tot['all'] += int(all(ok.values()))
            if not all(ok.values()):
                bad.append((tag, seat, s, {k: v for k, v in ok.items() if not v}, dict(off_w=o['outcome'], off_p=o['final_points'], off_t=o['final_turn'], off_pl=o['plies']), dict(w=g['winner'], p=g['points'], t=g['turns'], pl=g['plies'])))
print(tot)
for b in bad[:12]:
    print(b)
EOF
