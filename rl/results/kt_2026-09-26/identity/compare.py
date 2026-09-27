"""kt's identity checks (run_identity.sh), written to identity_check.txt.

Each identity run is compared game by game with its reference: moves (a hash of every step), decisions (a hash of the
moves picked from two or more options), openings and results. Each smoke (kt3, kta3, ktb3, ktc3) is checked for a clean
run (no rule findings) and compared with kp3 on the same 40 deals: the games whose choices differ, by cell.
Usage: python3 compare.py <label>   (the build's label in run_identity.sh, e.g. ed81c8b)."""
import json, re, sys
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
R = D / '../../rules09_fixes_2026-09-26'
L = sys.argv[1]


def load(path, deals=500):
    games = {}
    for line in open(path):
        g = json.loads(line)
        if g['i'] < deals:
            games[(g['pairing'], g['i'])] = g
    return games


def clean(bot, n):
    text = (D / f'{L}_{bot}_{n}.txt').read_text()
    return re.search(r'Findings \(occurrences / games affected\):\s*\n\s*none', text) is not None


def identity(bot, n, ref, ref_label):
    run, base = load(D / f'{L}_{bot}_{n}.jsonl'), load(ref, n)
    keys = sorted(base)
    assert sorted(run) == keys, f'{bot}: the run and the reference hold different games'
    eq = {f: sum(run[k][f] == base[k][f] for k in keys) for f in ('moves', 'decisions', 'openings')}
    results = sum((run[k]['winner_seat'], run[k]['points']) == (base[k]['winner_seat'], base[k]['points']) for k in keys)
    ok = all(v == len(keys) for v in eq.values()) and results == len(keys) and clean(bot, n)
    return (f"{bot} at {L} vs {ref_label}: {len(keys)} games; moves equal {eq['moves']}, decisions equal "
            f"{eq['decisions']}, openings equal {eq['openings']}, results equal {results}; clean run {clean(bot, n)}"
            f" -> {'IDENTICAL' if ok else 'NOT IDENTICAL'}")


def smoke(bot):
    run, base = load(D / f'{L}_{bot}_40.jsonl'), load(D / f'{L}_kp3_40.jsonl')
    differ = [k for k in sorted(run) if run[k]['decisions'] != base[k]['decisions']]
    cells = Counter(f"{run[k]['a']} v {run[k]['b']}" for k in differ)
    return (f"{bot} smoke ({len(run):,} games, clean run {clean(bot, 40)}): choices differ from kp3 in {len(differ)} "
            f"({100 * len(differ) / len(run):.1f}%); by cell: {dict(sorted(cells.items()))}")


lines = []
for bot, n, ref, label in [
    ('k3', 500, R / 'af8489f_k3_500.jsonl', 'af8489f_k3_500'),
    ('kp3', 500, R / 'af8489f_kp3_500.jsonl', 'af8489f_kp3_500'),
    ('kq3', 500, D / 'official_kq3_500.jsonl', 'official_kq3_500 (rl/engine-2026-09-27 legality_scan e6ab9a9d)'),
    ('kd3', 40, R / 'af8489f_kd3_40.jsonl', 'af8489f_kd3_40'),
    ('kpr3', 40, R / 'af8489f_kpr3_40.jsonl', 'af8489f_kpr3_40'),
    ('kp3', 40, R / 'af8489f_kp3_500.jsonl', 'af8489f_kp3_500 (first 40 deals)'),
]:
    if (D / f'{L}_{bot}_{n}.jsonl').exists():
        lines.append(identity(bot, n, ref, label))
for bot in ('kt3', 'kta3', 'ktb3', 'ktc3'):
    if (D / f'{L}_{bot}_40.jsonl').exists():
        lines.append(smoke(bot))
(D / 'identity_check.txt').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
