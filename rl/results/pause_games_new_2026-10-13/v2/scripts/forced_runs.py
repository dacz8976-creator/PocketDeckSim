#!/usr/bin/env python3
"""forced_runs.py POSITIONS.json DECKS_DIR OUT_DIR: step by step through HIS line, what km3 (pg_pos_F_cond, the official engine with main's Oct 13 reader) would play at each step.

The free run of km3 is cut at its first draw card, so a difference of ORDER (he uses Mesagoza first, km3 plays Professor's Research first) looks like a different turn. The harness
has a "forced" mode (pg_pos.rs of the Oct 2 harness): the position's `force` line is played as he played it, and at every step km3, on a fresh game from the same state, says what it
would play. This writes, per position and seed, his line cut at (and including) its first draw card, with km3's answer at each step, and summarises the first step at which km3's
answer differs from his in most seeds. A `Place:X` step is resolved to the engine's label (`Place:X@slot`) from the legal actions the harness lists.
Refuses when a DECKGYM_ variable is set or the binary is not pg_pos_F_cond (sha256 5c4859949a88a28b...).
v2 change: a bare `Ability` step is resolved to `Ability@slot` when exactly one Ability is legal."""
import collections, json, os, re, subprocess, sys

pos_f, decks_dir, out_dir = sys.argv[1:4]
BIN = os.environ.get('BIN', '/home/dacz8976/pgx/pg_pos_F_cond')
SEEDS = '1,2,3,4,5,6,7,8,9,10,11,12'
if any(k.startswith('DECKGYM_') for k in os.environ):
    sys.exit('a DECKGYM_ variable is set; refusing')
sha = subprocess.run(['sha256sum', BIN], capture_output=True, text=True).stdout
if not sha.startswith('5c4859949a88a28b'):
    sys.exit(f'{BIN} is not pg_pos_F_cond; refusing')
os.makedirs(out_dir, exist_ok=True)
POS = json.load(open(pos_f, encoding='utf-8'))
DECKARGS = []
for f in sorted(os.listdir(decks_dir)):
    if f.startswith('KW') and f.endswith('.txt'):
        DECKARGS += ['--deck', f'{f[:-4]}={os.path.join(decks_dir, f)}']

DRAW = ("Play:Professor's Research", "Play:Copycat", "Play:Lisia", "Play:Clemont", "Play:Sightseer", "Play:Order Pad", "Play:Team Rocket's Researcher", "Play:Quick-Grow Extract")


def is_draw(l):
    return l in DRAW or l.startswith('Play:Poké Ball') or l.startswith('Play:Poke Ball') or l == 'Play:Sabrina'


def his_force(plan):
    out = []
    for l in plan:
        if l == 'EndTurn':
            continue
        out.append(l)
        if is_draw(l):
            break
    return out


def run(p, force, seeds):
    q = dict(p)
    q['force'] = force
    tmp = os.path.join(out_dir, '_one.json')
    json.dump([q], open(tmp, 'w', encoding='utf-8'), ensure_ascii=False)
    r = subprocess.run(['nice', '-n', '19', BIN, '--positions', tmp, *DECKARGS, '--seeds', seeds, '--bot', 'km3', '--only', p['id']], capture_output=True, text=True)
    run.stderr = r.stderr
    return [json.loads(l) for l in r.stdout.split('\n') if l.strip().startswith('{')]


def step_scores(err, pid, seed):
    """{step: [(score, label)]} of km3's candidates at each forced step of one seed (the PGDUMP blocks of the harness)"""
    out, cur = {}, None
    for line in err.split('\n'):
        m = re.match(r'PGSTEP (\S+) seed (\d+) forced (\d+)', line)
        if m:
            cur = int(m.group(3)) if (m.group(1) == pid and int(m.group(2)) == seed) else None
            if cur is not None:
                out[cur] = []
            continue
        if cur is not None and line.startswith('PGDUMP') and 'candidates=' not in line:
            m = re.match(r'PGDUMP\s+(-?[\d.]+)\s+(.*)$', line)
            if m:
                out[cur].append((float(m.group(1)), m.group(2).strip()))
    return out


summary = []
for p in POS:
    force = his_force(p['his_plan'])
    note = ''
    for _ in range(len(force) + 2):
        recs = [r for r in run(p, force, '1') if r.get('kind') == 'forced']
        if not recs:
            note = 'no forced record'
            break
        rec = recs[0]
        bad = next((s for s in rec['steps'] if s.get('error')), None)
        if bad is None:
            break
        k, w = bad['step'], bad['forced']
        if w.startswith('AttachTypedFromDiscard:'):
            # v3: Dragon's Blessing's choice of an Energy type. The harness (rl/strength/src/main.rs label()) names the choices 'AttachTypedFromDiscard' without the type, so the one he made cannot be
            # told from the others when the discard holds several types (it would need the label 'AttachTypedFromDiscard:<Type>@<slot>'); with one type the engine takes it by itself
            if 'AttachTypedFromDiscard' in bad.get('legal', []):
                note = f"his step {k} ({w}) is a choice among Energy types the harness labels without the type: line cut there"
                force = force[:k]
                if not force:
                    break
                continue
            note = (note + '; ' if note else '') + f'his step {k} ({w}) was taken by the engine itself (one Energy type in the discard)'
            force.pop(k)
            continue
        alts = [l for l in bad.get('legal', []) if l.startswith(w + '@')] if w.startswith(('Place:', 'Evolve:', 'Tool:')) and '@' not in w else []
        if w == 'Ability':
            # the ledger names no Pokemon for an Ability; take it when exactly one Ability is legal (Dragonair's Dragon's Blessing in 030351), else cut the line there
            alts = [l for l in bad.get('legal', []) if l.startswith('Ability@')]
            alts = alts if len(alts) == 1 else []
        if alts:
            force[k] = alts[0]
            continue
        note = f"his step {k} ({w}) is not a legal action in the harness' state: line cut there"
        force = force[:k]
        if not force:
            break
    recs = [r for r in run(p, force, SEEDS) if r.get('kind') == 'forced'] if force else []
    gaps = step_scores(run.stderr, p['id'], 1) if force else {}
    json.dump(recs, open(os.path.join(out_dir, f"forced_{p['id']}.json"), 'w', encoding='utf-8'), ensure_ascii=False)
    # per step: how many seeds km3 plays the step he played
    steps = collections.defaultdict(lambda: collections.Counter())
    nxt = collections.Counter()
    for rec in recs:
        for s in rec['steps']:
            if 'forced' in s and 'error' not in s:
                steps[s['step']][s['km3'] == s['forced']] += 1
                steps[s['step']]['km3:' + s['km3']] += 1
            if 'next_choice_km3' in s:
                nxt[s['next_choice_km3']] += 1
    rows = []
    for k in sorted(steps):
        agree = steps[k][True]
        alts = {x[4:]: n for x, n in steps[k].items() if isinstance(x, str) and x.startswith('km3:')}
        gap = None
        if k in gaps and gaps[k] and k < len(force):
            top = max(v for v, _ in gaps[k])
            mine = [v for v, lab in gaps[k] if lab == force[k]]
            gap = round(top - max(mine), 1) if mine else None      # km3's top score minus the score of the step he played (seed 1)
        rows.append({'step': k, 'his': force[k] if k < len(force) else None, 'km3_agrees_in': agree, 'of': agree + steps[k][False], 'km3_plays': alts, 'gap_seed1': gap})
    first_dev = next((r for r in rows if r['km3_agrees_in'] <= r['of'] // 2), None)
    summary.append({'id': p['id'], 'force': force, 'note': note, 'rows': rows, 'first_deviation': first_dev, 'next_choice_km3': dict(nxt)})
json.dump(summary, open(os.path.join(out_dir, 'forced_summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
os.remove(os.path.join(out_dir, '_one.json'))
n_dev = sum(1 for s in summary if s['first_deviation'])
print(f'{len(summary)} positions; km3 deviates from his line (in most seeds) at some step in {n_dev}')
