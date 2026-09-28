"""koh's identity checks (run_identity.sh), written to identity_check.txt: each run against its reference, game by game
on moves, choices, openings and results, and the smoke's clean run. Usage: python3 identity.py <label>."""
import json, re, sys
from pathlib import Path

D = Path(__file__).resolve().parent
R = D.parent
L = sys.argv[1]


def load(path, deals):
    games = {}
    for line in open(path):
        g = json.loads(line)
        if g['i'] < deals:
            games[(g['pairing'], g['i'])] = g
    return games


def clean(bot, n):
    text = (D / f'{L}_{bot}_{n}.txt').read_text()
    return re.search(r'Findings \(occurrences / games affected\):\s*\n\s*none', text) is not None


out = []
for bot, n, ref in [('k3', 40, R / 'rules09_fixes_2026-09-26/af8489f_k3_500.jsonl'),
                    ('kp3', 40, R / 'rules09_fixes_2026-09-26/af8489f_kp3_500.jsonl'),
                    ('kog3', 500, R / 'kog_2026-09-27/a823b6d_kog3_500.jsonl')]:
    if not (D / f'{L}_{bot}_{n}.jsonl').exists():
        continue
    run, base = load(D / f'{L}_{bot}_{n}.jsonl', n), load(ref, n)
    keys = sorted(base)
    assert sorted(run) == keys, bot
    eq = {f: sum(run[k][f] == base[k][f] for k in keys) for f in ('moves', 'decisions', 'openings')}
    res = sum((run[k]['winner_seat'], run[k]['points']) == (base[k]['winner_seat'], base[k]['points']) for k in keys)
    ok = all(v == len(keys) for v in eq.values()) and res == len(keys) and clean(bot, n)
    out.append(f"{bot} at {L} vs {ref.relative_to(R)} ({n} deals): {len(keys)} games; moves equal {eq['moves']}, "
               f"decisions equal {eq['decisions']}, openings equal {eq['openings']}, results equal {res}; clean run "
               f"{clean(bot, n)} -> {'IDENTICAL' if ok else 'NOT IDENTICAL'}")
if (D / f'{L}_koh3_40.jsonl').exists():
    out.append(f"koh3 smoke: {len(load(D / f'{L}_koh3_40.jsonl', 40))} games, clean run {clean('koh3', 40)}")
(D / 'identity_check.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
