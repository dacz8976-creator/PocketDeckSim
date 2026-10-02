#!/usr/bin/env python3
"""Turbo Shark turns: his line replayed step by step on km3, and the Bench-target scores. Writes TURBO_SHARK.md into OUTDIR."""
import json, os, re, sys, collections, statistics

D = os.environ.get('PGD_DIR', '/home/dacz8976/pgd')
RUNS = os.environ.get('PGD_RUNS', f'{D}/runs')  # where the pg_pos output of the pilot being reported lives
OUT = sys.argv[1]
POS = {p['id']: p for p in json.load(open(os.environ.get('PGD_POSITIONS', f'{D}/positions_A.json'), encoding='utf-8'))}


def blocks(pid):
    out, cur = {}, None
    for line in open(f'{RUNS}/err_{pid}.txt', encoding='utf-8', errors='replace'):
        if line.startswith('PGSTEP'):
            m = re.match(r'PGSTEP (\S+) seed (\d+) (free|forced) (\d+)', line)
            cur = (int(m.group(2)), m.group(3), int(m.group(4)))
            out[cur] = {}
        elif line.startswith('PGDUMP') and cur and not line.startswith('PGDUMP actor='):
            m = re.match(r'PGDUMP\s+(-?[\d.]+) (.*)$', line.rstrip('\n'))
            if m:
                out[cur][m.group(2)] = float(m.group(1))
    return out


md = ["# Turbo Shark turns: km3's scores, step by step along his line\n",
      "Each row replays his own line from the position and, at every step, asks km3 (on a fresh game from the same state, 12 seeds) what it would play and how its search scores his action against its own best at that step. "
      "Scores are the search's root values (the same print as the Step 8c dump), averaged over 12 seeds; a gap of 0 means his action was km3's top-scoring candidate. "
      "The last step of each block is the Bench Energy target of Turbo Shark: every legal target and its root score.\n"]
rows = []
for pid in ('A-132311-t03', 'A-115323-t05b', 'A-115323-t07', 'A-115323-t11', 'A-132311-t07b'):
    if pid not in POS or not os.path.exists(f'{RUNS}/out_{pid}.jsonl'):
        continue  # not in this run (held out, or not built)
    p = POS[pid]
    lines = [json.loads(l) for l in open(f'{RUNS}/out_{pid}.jsonl', encoding='utf-8') if l.strip()]
    forced = [l for l in lines if l['kind'] == 'forced']
    bl = blocks(pid)
    md.append(f"## {pid}: game {p['game']}, his turn {p['his_turn']} (game turn {p['turn_count']})" + (' (mid-turn position)' if pid.endswith('b') else '') + '\n')
    md.append(f"His line: {' → '.join(l for l in p['his_plan'] if not l.startswith('('))}. {p['notes']}\n")
    md.append('| step | his action | km3 picks (12 seeds) | km3 score for his action | km3 best at this step | gap |')
    md.append('|---|---|---|---|---|---|')
    target_rows = None
    for k in range(max(len(r['steps']) for r in forced)):
        sts = [(r['seed'], r['steps'][k]) for r in forced if k < len(r['steps'])]
        s0 = sts[0][1]
        if 'forced' in s0:
            w = s0['forced']
            picks = collections.Counter(s['km3'] for _, s in sts)
            have = [bl[(sd, 'forced', k)] for sd, s in sts if (sd, 'forced', k) in bl and w in bl[(sd, 'forced', k)]]
            if have:
                mine = statistics.mean(h[w] for h in have)
                best = statistics.mean(max(h.values()) for h in have)
                md.append(f"| {k} | {w} | {', '.join(f'{a} ×{b}' for a, b in picks.most_common())} | {mine:.1f} | {best:.1f} | {best - mine:.1f} |")
            else:
                md.append(f"| {k} | {w} | {', '.join(f'{a} ×{b}' for a, b in picks.most_common())} | (only legal action) | | |")
        elif 'next_choice_km3' in s0:
            picks = collections.Counter(s['next_choice_km3'] for _, s in sts)
            target_rows = (k, s0['legal'], picks, [bl.get((sd, 'forced', k), {}) for sd, _ in sts])
    md.append('')
    if target_rows:
        k, legal, picks, bs = target_rows
        md.append(f"Bench target after Turbo Shark (step {k}); km3 picks: {', '.join(f'{a} ×{b}' for a, b in picks.most_common())}. His pick: {[l for l in p['his_plan'] if l.endswith(' fx')]}\n")
        md.append('| target (slot) | km3 root score (mean of 12 seeds) | min | max |')
        md.append('|---|---|---|---|')
        for lab in legal:
            vals = [b[lab] for b in bs if lab in b]
            if vals:
                md.append(f"| {lab} | {statistics.mean(vals):.2f} | {min(vals):.2f} | {max(vals):.2f} |")
        md.append('')
    else:
        md.append('There is no Bench target choice here (only one Water Pokémon on the Bench, so the engine places the Energy without asking).\n')
open(f'{OUT}/TURBO_SHARK.md', 'w', encoding='utf-8').write('\n'.join(md))
print('\n'.join(md))
