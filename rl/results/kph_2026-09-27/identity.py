"""kph's identity checks (run_identity.sh), written to identity_check.txt: each run against its official reference,
game by game on moves, choices, openings and results, and the smokes' clean runs.
Usage: python3 identity.py <label>."""
import json, re, sys
from pathlib import Path

D = Path(__file__).resolve().parent
R = D.parent
L = sys.argv[1]


def load(path, deals=40):
    games = {}
    for line in open(path):
        g = json.loads(line)
        if g['i'] < deals:
            games[(g['pairing'], g['i'])] = g
    return games


def clean(bot):
    text = (D / f'{L}_{bot}_40.txt').read_text()
    return re.search(r'Findings \(occurrences / games affected\):\s*\n\s*none', text) is not None


out = []
for bot, ref in [('kp3', R / 'rules09_fixes_2026-09-26/af8489f_kp3_500.jsonl'),
                 ('k3', R / 'rules09_fixes_2026-09-26/af8489f_k3_500.jsonl'),
                 ('kpg3', R / 'kpf_2026-09-26/reading/table_kpg3.jsonl'),
                 ('kpf3', R / 'kpf_2026-09-26/reading/table_kpf3.jsonl')]:
    run, base = load(D / f'{L}_{bot}_40.jsonl'), load(ref)
    keys = sorted(base)
    assert sorted(run) == keys, bot
    eq = {f: sum(run[k][f] == base[k][f] for k in keys) for f in ('moves', 'decisions', 'openings')}
    res = sum((run[k]['winner_seat'], run[k]['points']) == (base[k]['winner_seat'], base[k]['points']) for k in keys)
    ok = all(v == len(keys) for v in eq.values()) and res == len(keys) and clean(bot)
    out.append(f"{bot} at {L} vs {ref.relative_to(R)} (first 40 deals): {len(keys)} games; moves equal {eq['moves']}, "
               f"decisions equal {eq['decisions']}, openings equal {eq['openings']}, results equal {res}; clean run "
               f"{clean(bot)} -> {'IDENTICAL' if ok else 'NOT IDENTICAL'}")
for bot in ('kph3', 'kpha3', 'kphb3'):
    run = load(D / f'{L}_{bot}_40.jsonl')
    out.append(f"{bot} smoke: {len(run)} games, clean run {clean(bot)}")
(D / 'identity_check.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
