#!/usr/bin/env python3
"""K21: a step bot's rows on positions, made exactly as frozen-7's judge.run_pg_pos makes km3's (rl/ai_judge/judge.py at tag judge-prompt-frozen-7,
lines 595-628), with only its k<number>/km<number> name check lifted, so that K21's kx3 executable can play kx3. Every helper is frozen-7's own,
imported from the tag checkout: list_plans, match_plans, canonical_plan, record, plan_list_sha256, deck_args, file_sha256.

The one difference in how it calls the executable: one seed per call (pg_pos plays each seed from its own freshly built state, so a seed's line does not
depend on the other seeds of the call), so that rows are written one (seed, position) at a time and a night can stop and the next resume.
Gate (c) checks the rows equal `judge.py run`'s field for field.

usage: kx3_rows.py --judge-dir J --bin BIN --bot BOT --positions P --decks D --ids FILE --seeds s1[,s2,...] --out-dir OUT [--stop-at-utc HH:MM]
                   [--hard-stop-at-utc HH:MM] [--pause-file F]
Writes OUT/rows_<seed>.jsonl (one row per position, in the ids' order; seed-major) and OUT/timing.tsv. Exit 0: all done; 10: stopped at --stop-at-utc
(no position is started after it) or at --hard-stop-at-utc (the position in play is killed and leaves no row; the next night plays it again).
While --pause-file exists (Dustin needs the laptop), no position is started."""
import argparse, datetime, json, os, subprocess, sys, time

ap = argparse.ArgumentParser()
for k in ('--judge-dir', '--bin', '--bot', '--positions', '--decks', '--ids', '--seeds', '--out-dir'):
    ap.add_argument(k, required=True)
ap.add_argument('--stop-at-utc')
ap.add_argument('--hard-stop-at-utc')
ap.add_argument('--pause-file')
a = ap.parse_args()
if os.environ.get('KX_EXTRA_LISTS'):
    sys.exit('KX_EXTRA_LISTS is set: kx3 must run without extra lists (K21): stop')
sys.path.insert(0, a.judge_dir)
import judge  # noqa: E402  (frozen-7's, from the tag checkout)

ids = open(a.ids).read().split()
seeds = [int(s) for s in a.seeds.split(',')]
os.makedirs(a.out_dir, exist_ok=True)
pg_sha = judge.file_sha256(a.bin)
t0 = time.time()
recs = judge.list_plans(ids, a.positions, a.decks)
print(f'plan lists: {len(recs)} positions in {time.time() - t0:.0f}s', flush=True)


def done_in(path):
    out = set()
    if os.path.exists(path):
        for line in open(path):
            if line.strip():
                out.add(json.loads(line)['position'])
    return out


def at_utc(hhmm):
    """Today's HH:MM UTC as a datetime (the night window lies inside one UTC day)."""
    hh, mm = (int(x) for x in hhmm.split(':'))
    return datetime.datetime.now(datetime.timezone.utc).replace(hour=hh, minute=mm, second=0, microsecond=0)


def stop_now():
    return bool(a.stop_at_utc) and datetime.datetime.now(datetime.timezone.utc) >= at_utc(a.stop_at_utc)


for seed in seeds:
    path = os.path.join(a.out_dir, f'rows_{seed}.jsonl')
    have = done_in(path)
    for pid in ids:
        if pid in have:
            continue
        while a.pause_file and os.path.exists(a.pause_file) and not stop_now():
            print(f'{datetime.datetime.now(datetime.timezone.utc):%H:%M}Z paused ({a.pause_file} exists) before seed {seed} {pid}', flush=True)
            time.sleep(60)
        if stop_now():
            print(f'stopped at {a.stop_at_utc}Z before seed {seed} {pid}', flush=True)
            sys.exit(10)
        s = time.time()
        cmd = [a.bin, '--positions', a.positions] + judge.deck_args(a.decks) + ['--seeds', str(seed), '--bot', a.bot, '--only', pid]
        limit = (at_utc(a.hard_stop_at_utc) - datetime.datetime.now(datetime.timezone.utc)).total_seconds() if a.hard_stop_at_utc else None
        try:
            r = subprocess.run(['nice', '-n', '19'] + cmd, capture_output=True, text=True, timeout=limit)
        except subprocess.TimeoutExpired:  # subprocess.run kills the child (nice execs the binary, so the binary itself)
            print(f'hard stop at {a.hard_stop_at_utc}Z: seed {seed} {pid} killed after {time.time() - s:.0f}s, no row written', flush=True)
            sys.exit(10)
        if r.returncode:
            sys.exit(f'{a.bin} failed on {pid} seed {seed} (exit {r.returncode}): {r.stderr[-800:]}')
        got = [json.loads(line) for line in r.stdout.splitlines()]
        problems = [j for j in got if j.get('problems')]
        if problems:
            sys.exit(f'{a.bin} reports a problem with position {pid}: {problems[0].get("problems")}')
        free = [j for j in got if j.get('kind') == 'free' and j.get('id') == pid]
        if sorted(j['seed'] for j in free) != [seed]:
            sys.exit(f'{a.bot} on {pid}: expected exactly one free-play row for seed {seed}, got {[j["seed"] for j in free]}')
        j = free[0]
        matched = judge.match_plans([(pid, f"{pid}|{j['seed']}", j['plan'])], recs, a.positions, a.decks)
        n, err = matched[f"{pid}|{j['seed']}"]
        plan = judge.canonical_plan(j['plan'], recs[pid])
        end = recs[pid]['plans'][n - 1]['end'] if n else None
        rec = judge.record(pid, a.bot, plan, end, plan_number=n, match_error=err, plan_full=j['plan'], pg_pos_cut=j['cut'], pg_pos_sha256=pg_sha, cost=None,
                           dry_run=False, plan_key=(recs[pid]['plans'][n - 1]['key'] if n else None), plan_list_sha256=judge.plan_list_sha256(recs[pid]))
        rec['seed'] = j['seed']
        with open(path, 'a') as f:
            f.write(json.dumps(rec) + '\n')
        with open(os.path.join(a.out_dir, 'timing.tsv'), 'a') as f:
            f.write(f'{seed}\t{pid}\t{time.time() - s:.1f}\t{n}\t{err or ""}\n')
        print(f'seed {seed} {pid}: plan {n} {"(" + str(err) + ")" if err else ""} {time.time() - s:.0f}s', flush=True)
print('all done', flush=True)
