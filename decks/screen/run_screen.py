#!/usr/bin/env python3
"""Quick screen: a bot pilots a deck against the opponent panel (decks/screen/opponents/).

Purpose: catch decks that are clearly bad before Dustin spends ladder games on them. Not a ranking.
The quick screen's percentages are not a verdict and not a ranking (RUN5); the one approved bar is the floor check's (decks/screen/floor.py, RUN5 A2).

usage: run_screen.py DECK.txt [DECK2.txt ...] [--engine PATH/TO/deckgym] [--pilot km3] [--meta-pilot km3]
                     [--games 60] [--seed 7100] [--weights FILE]
Each matchup is played half with the deck in seat 0 and half in seat 1, on fixed seeds, so
different decks face the same shuffles. Needs Linux (WSL or the cloud).

--weights FILE (off by default; Sept 30): also print a ladder-weighted line under each deck's usual one, from a table of
`list,weight` (decks/screen/panel_ladder_2026-09-26/panel_weights.csv, README section 9). It is a readout of the lists
played, renormalised over their weights, and says what share of the ladder weight those lists carry (68% with opponents/
alone; --opponents can point at a readout-only folder holding all eleven). It is not a ranking: the ranking hold stands.
Nothing else changes, and without the option the output is exactly what it was.

Engine: by default the manifest's available release (project_manifest.json, checked by current_engine.py, which
refuses a binary whose hash differs). Pilots: km3 on both sides by default, the working pilot since the Sept 30
engine switch (kog3 from Sept 28, kp3 before it, from the plan revised Sept 25); --pilot kog3 --meta-pilot kog3
reproduces the Sept 28-30 screen, --pilot kp3 --meta-pilot kp3 the Sept 25-27 one, and --pilot k3 --meta-pilot k3
the Sept 24 one. Since Sept 30, kt3, kta3, ktb3 and ktc3 in the official engine are the kog-based presets (kta3 is
the adopted one; kt3, ktb3 and ktc3 are diagnostic); the older kp-based ones are only in rl/engine-2026-09-28/.
"""
import argparse, csv, glob, os, re, subprocess, sys

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(os.path.dirname(here))
sys.path.insert(0, root)
from current_engine import resolve  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('decks', nargs='+')
ap.add_argument('--engine', default=None, help="default: the manifest's available release")
ap.add_argument('--pilot', default='km3', help="the screened deck's bot (default km3)")
ap.add_argument('--meta-pilot', default='km3', help="the panel decks' bot (default km3)")
ap.add_argument('--games', type=int, default=60, help='games per matchup (split across seats)')
ap.add_argument('--seed', type=int, default=7100)
ap.add_argument('--opponents', default=os.path.join(here, 'opponents'))
ap.add_argument('--weights', default=None, metavar='FILE',
                help='also print a ladder-weighted line per deck, from a list,weight table; readout only, not a ranking')
a = ap.parse_args()
try:
    engine = str(resolve(project=root, override=a.engine))
except (OSError, ValueError) as e:
    raise SystemExit(f'REFUSED: {e} (the screen runs only the manifest\'s available release)')
opps = sorted(glob.glob(os.path.join(a.opponents, '*.txt')))

def read_weights(path):
    """list name -> weight (percent) from a `list,weight` CSV (other columns and `#` lines are ignored). Refuses a file that
    is unreadable, lacks either column, repeats a list, has a weight that is not a positive number, or does not total 100."""
    try:
        with open(path, encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(line for line in f if not line.startswith('#')))
    except (OSError, UnicodeDecodeError) as e:
        raise SystemExit(f'REFUSED: cannot read the weights file {path}: {e}')
    if not rows or not {'list', 'weight'} <= set(rows[0]):
        raise SystemExit(f'REFUSED: {path} needs a header with the columns list and weight, and at least one row')
    weights = {}
    for r in rows:
        name = (r['list'] or '').strip()
        try:
            w = float(r['weight'])
        except (TypeError, ValueError):
            w = float('nan')
        if not name or name in weights or not 0 < w < float('inf'):
            raise SystemExit(f'REFUSED: {path} has a blank or repeated list, or a weight that is not a positive number: {r}')
        weights[name] = w
    if abs(sum(weights.values()) - 100) > 0.5:
        raise SystemExit(f'REFUSED: the weights in {path} total {sum(weights.values()):.1f}, not 100')
    return weights

weights = read_weights(a.weights) if a.weights else None
if weights is not None and not any(os.path.splitext(os.path.basename(o))[0] in weights for o in opps):
    raise SystemExit(f'REFUSED: none of the {len(opps)} opponent lists in {a.opponents} has a weight in {a.weights}')

def weighted_lines(rows, games, weights, path):
    """The readout lines under a deck's usual one: the weighted win rate over the lists played that have a weight, the
    share of the ladder weight they carry, the lists with a weight that were not played, and the lists played without one."""
    played = {o: w for o, w, _, _ in rows}
    used = {o: w for o, w in played.items() if o in weights}
    carried = sum(weights[o] for o in used)
    pct = 100 * sum(weights[o] * w / games for o, w in used.items()) / carried
    lines = [f'   ladder-weighted: {pct:.1f}%  (weights from {os.path.basename(path)}; {len(used)} of {len(weights)} weighted '
             f'lists played, carrying {100 * carried / sum(weights.values()):.0f}% of the ladder weight)']
    missing = sorted(n for n in weights if n not in played)
    if missing:
        lines.append('   not played, no cells: ' + ', '.join(missing))
    unweighted = sorted(o for o in played if o not in weights)
    if unweighted:
        lines.append('   played but not weighted, left out: ' + ', '.join(unweighted))
    lines.append('   not a ranking: the ranking hold stands')
    return lines

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
    if weights is not None:
        print('\n'.join(weighted_lines(rows, a.games, weights, a.weights)))
    for oname, w, l, d in sorted(rows, key=lambda r: r[1]):
        print(f'   {oname:14s} {w:3d}-{l:<3d}' + (f' ({d} draws)' if d else '') + f'  {100*w/a.games:3.0f}%')
