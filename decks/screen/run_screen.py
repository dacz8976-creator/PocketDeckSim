#!/usr/bin/env python3
"""Quick screen: the k3 bot pilots a deck against the opponent panel (decks/screen/opponents/).

Purpose: catch decks that are clearly bad before Dustin spends ladder games on them. Not a ranking.
See decks/README.md for the pass bar and how to read the result.

usage: run_screen.py DECK.txt [DECK2.txt ...] --engine PATH/TO/deckgym [--games 60] [--seed 7100]
Each matchup is played half with the deck in seat 0 and half in seat 1, on fixed seeds, so
different decks face the same shuffles. Needs a Linux with glibc 2.39+ (WSL or the Cowork cloud).
"""
import argparse, os, re, subprocess, glob

here = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('decks', nargs='+')
ap.add_argument('--engine', required=True)
ap.add_argument('--games', type=int, default=60, help='games per matchup (split across seats)')
ap.add_argument('--seed', type=int, default=7100)
ap.add_argument('--opponents', default=os.path.join(here, 'opponents'))
a = ap.parse_args()
opps = sorted(glob.glob(os.path.join(a.opponents, '*.txt')))

def run(p0, p1, n, seed):
    out = subprocess.run([a.engine, 'simulate', '--num', str(n), '--players', 'k3,k3', '--seed', str(seed),
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
        w0, l0, d0 = run(deck, o, h, s)          # deck in seat 0
        l1, w1, d1 = run(o, deck, a.games - h, s + 500)   # deck in seat 1
        w, g = w0 + w1, a.games
        tw += w; tg += g
        rows.append((oname, w, g - w - d0 - d1, d0 + d1))
    print(f'\n== {name}: {tw}/{tg} = {100*tw/tg:.0f}% vs the panel  (k3 bot both sides, {a.games} games per matchup)')
    for oname, w, l, d in sorted(rows, key=lambda r: r[1]):
        print(f'   {oname:14s} {w:3d}-{l:<3d}' + (f' ({d} draws)' if d else '') + f'  {100*w/a.games:3.0f}%')
