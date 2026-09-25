#!/usr/bin/env python3
"""Quick screen: a bot pilots a deck against the opponent panel (decks/screen/opponents/).

Purpose: catch decks that are clearly bad before Dustin spends ladder games on them. Not a ranking.
See decks/README.md for the pass bar and how to read the result.

usage: run_screen.py DECK.txt [DECK2.txt ...] [--engine PATH/TO/deckgym] [--pilot kp3] [--meta-pilot kp3]
                     [--games 60] [--seed 7100]
Each matchup is played half with the deck in seat 0 and half in seat 1, on fixed seeds, so
different decks face the same shuffles. Needs Linux (WSL or the cloud).

Engine: by default the manifest's available release (project_manifest.json, checked by current_engine.py, which
refuses a binary whose hash differs). Pilots: kp3 on both sides by default (the plan revised Sept 25, approved by
Dustin); --pilot k3 --meta-pilot k3 reproduces the Sept 24 screen.
"""
import argparse, glob, os, re, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, root)
from current_engine import resolve  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('decks', nargs='+')
ap.add_argument('--engine', default=None, help="default: the manifest's available release")
ap.add_argument('--pilot', default='kp3', help="the screened deck's bot (default kp3)")
ap.add_argument('--meta-pilot', default='kp3', help="the panel decks' bot (default kp3)")
ap.add_argument('--games', type=int, default=60, help='games per matchup (split across seats)')
ap.add_argument('--seed', type=int, default=7100)
ap.add_argument('--opponents', default=os.path.join(here, 'opponents'))
a = ap.parse_args()
try:
    engine = str(resolve(project=root, override=a.engine))
except (OSError, ValueError) as e:
    raise SystemExit(f'REFUSED: {e} (the screen runs only the manifest\'s available release)')
opps = sorted(glob.glob(os.path.join(a.opponents, '*.txt')))

def run(p0, p1, players, n, seed):
    out = subprocess.run([engine, 'simulate', '--num', str(n), '--players', players, '--seed', str(seed),
                          '--seed-stream', '-p', p0, p1], capture_output=True, text=True)
    out = out.stdout + out.stderr
    if 'Player 0 won' not in out:
        raise SystemExit(f'engine refused {p0} vs {p1}:\n' + out[-400:] + '\n(deck files must not contain # comment lines)')
    w0 = int(re.search(r'Player 0 won: (\d+)', out)[1]); w1 = int(re.search(r'Player 1 won: (\d+)', out)[1])
    d = int(re.search(r'Draws: (\d+)', out)[1])
    return w0, w1, d

for deck in a.decks:
    name = os.path.splitext(os.path.basename(deck))[0]
    tw = tg = 0; rows = []
    for i, o in enumerate(opps):
        oname = os.path.splitext(os.path.basename(o))[0]
        h = a.games // 2; s = a.seed + 1000 * i
        w0, l0, d0 = run(deck, o, f'{a.pilot},{a.meta_pilot}', h, s)             # deck in seat 0
        l1, w1, d1 = run(o, deck, f'{a.meta_pilot},{a.pilot}', a.games - h, s + 500)   # deck in seat 1
        w, g = w0 + w1, a.games
        tw += w; tg += g
        rows.append((oname, w, g - w - d0 - d1, d0 + d1))
    print(f'\n== {name}: {tw}/{tg} = {100*tw/tg:.0f}% vs the panel  ({a.pilot} on the deck, {a.meta_pilot} on the panel, '
          f'{a.games} games per matchup; engine {os.path.relpath(engine, root)})')
    for oname, w, l, d in sorted(rows, key=lambda r: r[1]):
        print(f'   {oname:14s} {w:3d}-{l:<3d}' + (f' ({d} draws)' if d else '') + f'  {100*w/a.games:3.0f}%')
