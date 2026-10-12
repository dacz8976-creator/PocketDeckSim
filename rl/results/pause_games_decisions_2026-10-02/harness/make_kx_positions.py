#!/usr/bin/env python3
"""The kx-only copy of the positions file (positions_A.json itself is never touched, so km3's recorded tables stay reproducible).
  make_kx_positions.py positions_A.json positions_kx.json
- every position of the comparison recordings (ids B-...) gets "filler": "BL": the opponent's EXACT list (decks/computer/blastoise-wailord-deluxe.txt, run as --deck BL=<file>);
  pg_pos then deals his hidden cards from that list minus what is visible and fills any discard count from his own list (Supporters first, then Items), never from the pilot's.
- every other position has a real opponent whose list is unknown: its hidden cards and any discard count (discard_n > 0) can only be filler from the pilot's own list.
  Where a discard count is filled that way the position is marked "approximate" with a reason (the reconstructed-list positions already are): approximate positions are
  reported but kept out of every total and verdict.
Only these keys are added: filler, approximate, approximate_reason."""
import json, sys

P = json.load(open(sys.argv[1], encoding='utf-8'))
n_bl = n_marked = n_already = 0
for p in P:
    if p['id'].startswith('B-'):
        p['filler'] = 'BL'
        n_bl += 1
        continue
    dn = p['opp'].get('discard_n', 0) or 0
    if dn > 0:
        reason = f"kx: the opponent's list is unknown, so its {dn} discard card(s) (and its hidden cards) are filler from the pilot's own list"
        if p.get('approximate'):
            n_already += 1   # a reconstructed-list position: keeps its own reason (the list)
        else:
            p['approximate'] = True
            p['approximate_reason'] = reason
            n_marked += 1
json.dump(P, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"{len(P)} positions -> {sys.argv[2]}: {n_bl} with filler BL (exact opponent list); {n_marked} newly marked approximate (discard filler from the pilot's list); {n_already} already approximate")
