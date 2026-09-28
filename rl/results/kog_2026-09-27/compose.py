"""kog's composition checks (the laptop's request of Sept 27; RUN5 "Rules", composing candidates into one pilot).

kog = kp + koa's switch A + kpg's F. Switch A is read only in the setup evaluation, F only after it, so a kog game
should be koa3's where F can't act and kpg3's where A changed nothing. Against the official engine's tables
(../koa_2026-09-26/reading/table_koa3.jsonl, ../kpf_2026-09-26/reading/table_kpg3.jsonl) and kp3's reference
(../rules09_fixes_2026-09-26/af8489f_kp3_500.jsonl), game by game on the table's 14,000 deals:
1. every game in a pairing where neither list has a recovery source for F equals koa3's;
2. every game where koa3's equals kp3's (switch A changed nothing) equals kpg3's;
3. the games that equal neither: both switches act in each. kog and koa3 share the setup evaluator and differ only
   after setup (F); kog and kpg3 differ only in setup (switch A). So in each such game kog's openings must equal
   koa3's and differ from kpg3's, and first_divergence.rs's traces (check3_traces.txt) must put the first
   difference from kpg3 in setup and the first difference from koa3 after it. Listed by seed. For information: in how
   many F also changes kp3's own game (kpg3 != kp3), which it need not, since A has already changed the game.
Also: k3 and kp3 at the kog build against the official references, and koa3 and kpg3 on 40 deals against the tables.
Usage: python3 compose.py <label>   (the build's label in run_identity.sh). Writes composition_check.txt."""
import json, re, sys
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
R = D.parent
L = sys.argv[1]
# The recovery class (../kpf_2026-09-26/BUILD.md), by printing.
RECOVERY = {'B4 117', 'A3b 009', 'A3b 079', 'A3b 087', 'A4b 066', 'B2 225', 'B1 217', 'B1 331', 'B3a 072', 'B3a 087',
            'A3a 069', 'A3a 083', 'A4b 350', 'A4b 351', 'A4b 375', 'A2 153', 'A2 193'}


def load(path, deals=500):
    games = {}
    for line in open(path):
        g = json.loads(line)
        if g['i'] < deals:
            games[(g['pairing'], g['i'])] = g
    return games


def carries(deck):
    lines = (R.parent.parent / 'decks' / 'research' / f'{deck}.txt').read_text().splitlines()
    return any(re.match(r'^\d+ (.+)$', l) and re.match(r'^\d+ (.+)$', l).group(1) in RECOVERY for l in lines)


def clean(path):
    return re.search(r'Findings \(occurrences / games affected\):\s*\n\s*none', Path(path).read_text()) is not None


def same(a, b):
    return all(a[f] == b[f] for f in ('moves', 'decisions', 'openings')) and \
        (a['winner_seat'], a['points']) == (b['winner_seat'], b['points'])


def identity(bot, n, ref, label):
    run, base = load(D / f'{L}_{bot}_{n}.jsonl', n), load(ref, n)
    keys = sorted(base)
    assert sorted(run) == keys, f'{bot}: different games'
    eq = sum(same(run[k], base[k]) for k in keys)
    ok = eq == len(keys) and clean(D / f'{L}_{bot}_{n}.txt')
    return f"{bot} at {L} vs {label}: {eq} of {len(keys)} games equal (moves, decisions, openings, result); " \
           f"clean run {clean(D / f'{L}_{bot}_{n}.txt')} -> {'IDENTICAL' if ok else 'NOT IDENTICAL'}"


out = []
kog = load(D / f'{L}_kog3_500.jsonl')
koa = load(R / 'koa_2026-09-26/reading/table_koa3.jsonl')
kpg = load(R / 'kpf_2026-09-26/reading/table_kpg3.jsonl')
kp = load(R / 'rules09_fixes_2026-09-26/af8489f_kp3_500.jsonl')
keys = sorted(kog)
assert keys == sorted(koa) == sorted(kpg) == sorted(kp) and len(keys) == 14000
out.append(f"kog3 at {L}: {len(keys)} table games, clean run {clean(D / f'{L}_kog3_500.txt')}")
cell = lambda k: f"{kog[k]['a']} v {kog[k]['b']}"
source = {k: carries(kog[k]['a']) or carries(kog[k]['b']) for k in keys}
decks = sorted({kog[k]['a'] for k in keys} | {kog[k]['b'] for k in keys})
out.append(f"lists with a recovery source for F: {[d for d in decks if carries(d)]}")

# 1. No recovery source in either list: kog = koa3.
c1 = [k for k in keys if not source[k]]
c1_eq = sum(same(kog[k], koa[k]) for k in c1)
out.append(f"check 1, pairings with no recovery source ({len({k[0] for k in c1})} pairings): kog3 = koa3 in {c1_eq} of "
           f"{len(c1)} games -> {'PASS' if c1_eq == len(c1) else 'FAIL'}")

# 2. Switch A changed nothing (koa3 = kp3): kog = kpg3.
c2 = [k for k in keys if same(koa[k], kp[k])]
c2_eq = sum(same(kog[k], kpg[k]) for k in c2)
out.append(f"check 2, games where koa3 = kp3 ({len(c2)} of {len(keys)}): kog3 = kpg3 in {c2_eq} of {len(c2)} games -> "
           f"{'PASS' if c2_eq == len(c2) else 'FAIL'}")
# The same with the looser reading "koa3's openings = kp3's", for information.
c2b = [k for k in keys if koa[k]['openings'] == kp[k]['openings']]
out.append(f"  (for information: games where koa3's openings = kp3's: {len(c2b)}; kog3 = kpg3 in "
           f"{sum(same(kog[k], kpg[k]) for k in c2b)})")

# 3. Games equal to neither: both switches must act.
neither = [k for k in keys if not same(kog[k], koa[k]) and not same(kog[k], kpg[k])]
a_acts = [k for k in neither if kog[k]['openings'] == koa[k]['openings'] != kpg[k]['openings']]
traces = (D / 'check3_traces.txt').read_text() if (D / 'check3_traces.txt').exists() else ''
blocks = [b for b in traces.split('\n\n') if b.strip()]
replayed = sum('(table: true), ' in b and b.split('\n')[0].endswith('(table: true)') for b in blocks)
vs_kpg = [b for b in blocks if ' kpg3 moves ' in b.split('\n')[0]]
vs_koa = [b for b in blocks if ' koa3 moves ' in b.split('\n')[0]]
setup_kpg = sum('(setup)' in b for b in vs_kpg)
play_koa = sum('(play)' in b for b in vs_koa)
strict = [k for k in neither if not same(koa[k], kp[k]) and not same(kpg[k], kp[k])]
ok3 = len(a_acts) == len(neither) and len(vs_kpg) == len(vs_koa) == len(neither) and setup_kpg == play_koa == len(neither) \
    and replayed == len(blocks)
out.append(f"check 3, games equal to neither koa3 nor kpg3: {len(neither)}. Switch A acts in each (kog3's openings = koa3's "
           f"!= kpg3's): {len(a_acts)}. Traces replaying the table games exactly: {replayed} of {len(blocks)}; first "
           f"difference from kpg3 in setup: {setup_kpg} of {len(vs_kpg)}; first difference from koa3 after setup (F): "
           f"{play_koa} of {len(vs_koa)} -> {'PASS' if ok3 else 'FAIL'}")
out.append(f"  (for information: F also changes kp3's own game, kpg3 != kp3, in {len(strict)} of them)")
for c, n in sorted(Counter(cell(k) for k in neither).items()):
    seeds = [str(kog[k]['seed']) for k in neither if cell(k) == c]
    same_open = sum(kog[k]['openings'] == koa[k]['openings'] for k in neither if cell(k) == c)
    out.append(f"  {c}: {n} games (kog3's openings = koa3's in {same_open}); seeds {', '.join(seeds)}")

# Where each game lands, by cell.
out.append("by cell: games equal to koa3 / equal to kpg3 / equal to both / neither")
for c in sorted({cell(k) for k in keys}):
    ks = [k for k in keys if cell(k) == c]
    a = sum(same(kog[k], koa[k]) for k in ks)
    g = sum(same(kog[k], kpg[k]) for k in ks)
    b = sum(same(kog[k], koa[k]) and same(kog[k], kpg[k]) for k in ks)
    out.append(f"  {c:22s} {a:4d} {g:4d} {b:4d} {sum(1 for k in ks if k in set(neither)):4d}")

# 4. k3 and kp3 unchanged; koa3 and kpg3 at the build on 40 deals.
for bot, n, ref, label in [
    ('k3', 500, R / 'rules09_fixes_2026-09-26/af8489f_k3_500.jsonl', 'af8489f_k3_500 (official reference)'),
    ('kp3', 500, R / 'rules09_fixes_2026-09-26/af8489f_kp3_500.jsonl', 'af8489f_kp3_500 (official reference)'),
    ('koa3', 40, R / 'koa_2026-09-26/reading/table_koa3.jsonl', 'table_koa3 (first 40 deals)'),
    ('kpg3', 40, R / 'kpf_2026-09-26/reading/table_kpg3.jsonl', 'table_kpg3 (first 40 deals)'),
]:
    if (D / f'{L}_{bot}_{n}.jsonl').exists():
        out.append(identity(bot, n, ref, label))
(D / 'composition_check.txt').write_text('\n'.join(out) + '\n')
print('\n'.join(out))
