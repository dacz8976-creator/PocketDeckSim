#!/usr/bin/env python3
"""R8 Lane N identity replays: replay one recorded rules-switch-2 reference with the lane's programs, compare it with the
reference (as R6 did) and with R6 S's committed outputs (in place of R6's "v f", coordinator-148 §2.5).

PROVENANCE: a copy of R6's replay3.py (rl/results/dual_type_seam_2026-10-23/r6_release/tools/replay3.py, sha256
47f79ac7bd7952889a77de0316136452bbb209437ec136ebe75631798b30dbef, TOOLS.txt:10). CHANGES:
  1. Inputs come from the LANE WORKTREE (LANE_WT, default /home/dacz8976/lane_r8_w; coordinator-148 §3, first option), not
     ~/pincand's working tree: the decks, the 4 pairs files, run_screen.py, screen_with.py, the goldfish deck and panel, and the
     references in rl/results/engine_switch_rules2_2026-10 (all tracked; equal to ~/pincand's files and unchanged since
     b78c8997: checked before the lane commit, and again by night_r8.sh's preflight). The Windows path of the .run records maps
     to LANE_WT instead of /home/dacz8976/pincand.
  2. One side only, r = the lane's programs (LANE_OUT/programs) and archive (LANE_OUT/RR); the floor:<page> mode and sides
     old/new/u/f/d/p are removed (not used by R8's 18 replays).
  3. Outputs under LANE_OUT (/home/dacz8976/pincand_work/RR_R8_<commit>): games/r/<NAME>.*, games/summary.tsv.
  4. "v f" (games/f, deleted Nov 1) is replaced by "v S", R6 S's committed outputs (r6_release/logs/replays_S in the worktree):
     the 11 game files' sha256 against replays_S/outputs.sha256; each game row's diff.tsv byte-equal to S's; the 5 CLI outputs
     equal to replays_S/<NAME>.txt ("Ran " lines aside); run_screen v its S file (switch_check.py screen); the goldfish page
     equal to S's (the deck path's folder mapped: LANE_WT -> /home/dacz8976/pincand) and its coverage sha256 against
     outputs.sha256. A difference only in a line that names the engine or its version is listed ("version-only"), not failed.
  5. `replay_r8.py verify` (new): the prediction check of LANE_N_PREDICTION.md over the lane's logs and the 18 rows; writes
     LANE_OUT/verify/VERIFY.txt and prints "VERIFY PASS" or "VERIFY FAIL: <reasons>" last.

  replay_r8.py r NAME      NAME = a reference base name in rl/results/engine_switch_rules2_2026-10/ (e.g. 08a9b3a_table_k3)
  replay_r8.py verify
Summary line (as R6): side name games seconds verdict(SAME|DIFFERS|ERROR) detail; the detail ends with " | v S: ...".
legality_scan runs with RAYON_NUM_THREADS (default 8; games are matched by (pairing, i), so the thread count changes no game);
the CLI, run_screen and goldfish run as recorded, without RAYON_NUM_THREADS. Everything runs at nice 19 / ionice -c3."""
import hashlib, json, os, re, shlex, subprocess, sys, time
from pathlib import Path

W = Path(os.environ.get('LANE_OUT', ''))
R = Path(os.environ.get('LANE_WT', '/home/dacz8976/lane_r8_w'))
if not str(W).startswith('/home/dacz8976/pincand_work/RR_R8_'):
    sys.exit('replay_r8.py: LANE_OUT must be /home/dacz8976/pincand_work/RR_R8_<commit>')
SW2 = R / 'rl/results/engine_switch_rules2_2026-10'
S_DIR = R / 'rl/results/dual_type_seam_2026-10-23/r6_release/logs/replays_S'
S_ROOT = '/home/dacz8976/pincand'   # what S's own outputs name as the deck folder
OLD_CWD = '/home/dacz8976/engine-rules2-08a9b3a/engine'
WIN = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim'
ARCHIVE, PROGS = W / 'RR', W / 'programs'
THREADS = os.environ.get('SCAN_THREADS', '8')
GENTLE = ['nice', '-n', '19', 'ionice', '-c3']
VERSION_LINE = re.compile(r'^PDL decision-integrity candidate \S+:')   # names the engine version (deckgym main.rs)
REPLAYS = ('08a9b3a_10_cli_k3 08a9b3a_10_cli_kp3 08a9b3a_10_cli_kog3 08a9b3a_10_cli_kta3 08a9b3a_10_cli_km3 08a9b3a_10_goldfish '
           '08a9b3a_table_k3 08a9b3a_table_kp3 08a9b3a_table_kog3 08a9b3a_dev_km3_table 08a9b3a_dev_kta3_table 08a9b3a_10_run_screen '
           '08a9b3a_new17_k3 08a9b3a_dev_km3_new17 08a9b3a_8b_cloud_new_k3 08a9b3a_8b_cloud_new_km3 08a9b3a_8_new_km3 '
           '08a9b3a_cov_b2e_km3').split()
KNOWN_DIFFERS = {'08a9b3a_new17_k3': '8 differing deals of 8500;', '08a9b3a_dev_km3_new17': '7 differing deals of 8500;',
                 '08a9b3a_8_new_km3': '1 differing deals of 16000;'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def s_sums():
    out = {}
    for l in (S_DIR / 'outputs.sha256').read_text().splitlines():
        if l.strip():
            h, n = l.split(None, 1)
            out[n.strip()] = h
    return out


def read_run(name):
    lines = (SW2 / f'{name}.run').read_text().splitlines()
    prog, _, psha = lines[0].split(' ', 2)
    psha = psha.replace('sha256 ', '').strip()
    cwd = next(l[4:] for l in lines if l.startswith('cwd '))
    args = shlex.split(next(l[5:] for l in lines if l.startswith('args ')))
    return prog, psha, cwd, args


def mapped(s, archive):
    return s.replace(OLD_CWD, str(archive / 'engine')).replace(WIN, str(R))


def summary(side, name, games, secs, verdict, detail):
    with open(W / 'games/summary.tsv', 'a') as f:
        f.write(f'{side}\t{name}\t{games}\t{secs}\t{verdict}\t{detail}\n')
    print(f'{side} {name}: {verdict} ({games} games, {secs} s) {detail}', flush=True)


def diff_jsonl(new, ref, out_tsv):
    def load(p):
        d = {}
        for l in open(p):
            g = json.loads(l)
            d[(g['pairing'], g['i'])] = g
        return d
    a, b = load(new), load(ref)
    rows = []
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k), b.get(k)
        if x is None or y is None:
            rows.append((k, 'MISSING_IN_' + ('NEW' if x is None else 'REF'), '', '', '', ''))
            continue
        fields = sorted(f for f in set(x) | set(y) if x.get(f, '<absent>') != y.get(f, '<absent>'))
        if fields:
            rows.append((k, ','.join(fields), x.get('a', ''), x.get('b', ''), x.get('winner_seat'), y.get('winner_seat')))
    with open(out_tsv, 'w') as f:
        f.write('pairing\ti\tfields\ta\tb\twinner_new\twinner_ref\n')
        for (p, i), fl, da, db, wn, wr in rows:
            f.write(f'{p}\t{i}\t{fl}\t{da}\t{db}\t{wn}\t{wr}\n')
    return len(rows), len(a), len(b)


def line_diff(new_lines, s_lines):
    """Differing lines (S's, ours), and whether every one of them is a version/engine-name line."""
    pairs = [(a, b) for a, b in zip(s_lines, new_lines) if a != b]
    if len(s_lines) != len(new_lines):
        pairs.append((f'<{len(s_lines)} lines>', f'<{len(new_lines)} lines>'))
    version_only = bool(pairs) and all(VERSION_LINE.match(a) and VERSION_LINE.match(b) for a, b in pairs)
    return pairs, version_only


def v_s_text(new_lines, s_lines, out_file):
    pairs, vo = line_diff(new_lines, s_lines)
    if not pairs:
        return 'SAME'
    out_file.write_text(''.join(f'S:   {a}\nnew: {b}\n' for a, b in pairs))
    return f'version-only ({len(pairs)} line(s), listed in {out_file.name})' if vo else f'DIFFERS ({len(pairs)} line(s), see {out_file.name})'


def run_one(side, name):
    archive, progs = ARCHIVE, PROGS
    out = W / 'games' / side
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    for k in list(env):
        if k.startswith('DECKGYM_'):
            sys.exit(f'refusing: {k} is set')
    for k in ('RAYON_NUM_THREADS', 'PDL_DB', 'TEST_CARD_SUPPORT_MISSING_ATTACK', 'LANE_OUT', 'LANE_WT'):
        env.pop(k, None)
    t0 = time.time()
    prog, psha, cwd, args = read_run(name)
    exe = progs / prog
    cwd = mapped(cwd, archive)
    args = [mapped(a, archive) for a in args]
    if prog == 'legality_scan':
        env['RAYON_NUM_THREADS'] = THREADS
        part = out / f'{name}.jsonl'
        cmd = GENTLE + [str(exe)] + args + ['--games-out', str(part)]
    elif prog == 'deckgym' and args and args[0] == 'simulate':
        cmd = GENTLE + [str(exe)] + args
    elif prog == 'goldfish':
        cov = out / f'{name}_coverage.json'
        args = [str(cov) if a.endswith('_coverage.json') else a for a in args]
        cmd = GENTLE + [str(exe)] + args
    elif prog == 'deckgym' and args and args[0].startswith('run_screen.py='):
        rest = args[2:]
        cmd = GENTLE + ['python3', str(R / 'rl/results/engine_switch_2026-09-30/screen_with.py'), str(exe), sha(exe), str(R / 'decks/screen/run_screen.py')] + rest
    else:
        sys.exit(f'unknown run kind: {prog} {args[:2]}')
    (out / f'{name}.cmd').write_text(f'cwd {cwd}\n' + ' '.join(shlex.quote(c) for c in cmd) + f'\nprogram sha256 {sha(exe)}\n')
    with open(out / f'{name}.txt', 'w') as log:
        rc = subprocess.run(cmd, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
    secs = int(time.time() - t0)
    if rc != 0:
        return summary(side, name, 0, secs, 'ERROR', f'exit {rc}; see {name}.txt')

    ck = SW2 / 'switch_check.py'
    sums = s_sums()
    if prog == 'legality_scan':
        ref = SW2 / f'{name}.jsonl'
        nref = sum(1 for _ in open(ref))
        chk = subprocess.run(['python3', str(ck), 'same', str(part), '--ref', str(ref), '--expect', str(nref), '--label', f'{side} {name}'],
                             capture_output=True, text=True)
        (out / f'{name}.cmp').write_text(chk.stdout + chk.stderr)
        rules = subprocess.run(['python3', str(ck), 'rules', str(out / f'{name}.txt')], capture_output=True, text=True)
        ndiff, na, nb = diff_jsonl(part, ref, out / f'{name}.diff.tsv')
        verdict = 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR')
        want = sums.get(f'{name}.jsonl')
        sha_s = 'SAME' if want and sha(part) == want else ('NO S SUM' if not want else 'DIFFERS')
        dt_s = '=' if (out / f'{name}.diff.tsv').read_bytes() == (S_DIR / f'{name}.diff.tsv').read_bytes() else '!='
        vs = f' | v S: sha {sha_s}, diff.tsv {dt_s}'
        return summary(side, name, na, secs, verdict, f'{ndiff} differing deals of {nb}; rules page: {rules.stdout.strip()[:120]}{vs}')
    if prog == 'deckgym' and args[0] == 'simulate':
        strip = lambda t: [l for l in t.splitlines() if not l.startswith('Ran ')]
        new_t, ref_t = (out / f'{name}.txt').read_text(), (SW2 / f'{name}.txt').read_text()
        same = strip(new_t) == strip(ref_t)
        wins = ' | '.join(l for l in new_t.splitlines() if 'won' in l or 'Draws' in l)
        wins += ' | v S: ' + v_s_text(strip(new_t), strip((S_DIR / f'{name}.txt').read_text()), out / f'{name}.v_S.txt')
        return summary(side, name, 240, secs, 'SAME' if same else 'DIFFERS', wins)
    if prog == 'goldfish':
        norm = lambda t: t.replace(str(R), WIN)
        page = (out / f'{name}.txt').read_text()
        same_t = norm(page) == (SW2 / f'{name}.txt').read_text()
        same_c = norm(cov.read_text()) == (SW2 / f'{name}_coverage.json').read_text()
        pv = v_s_text(page.replace(str(R), S_ROOT).splitlines(), (S_DIR / f'{name}.txt').read_text().splitlines(), out / f'{name}.v_S.txt')
        want = sums.get(f'{name}_coverage.json')
        cv = 'SAME' if want and sha(cov) == want else 'DIFFERS'
        return summary(side, name, 0, secs, 'SAME' if (same_t and same_c) else 'DIFFERS',
                       f'page {"=" if same_t else "!="}, coverage {"=" if same_c else "!="} | v S: page {pv}, coverage sha {cv}')
    chk = subprocess.run(['python3', str(ck), 'screen', str(out / f'{name}.txt'), str(SW2 / f'{name}.txt')], capture_output=True, text=True)
    (out / f'{name}.cmp').write_text(chk.stdout + chk.stderr)
    detail = chk.stdout.strip()[:300]
    chk2 = subprocess.run(['python3', str(ck), 'screen', str(out / f'{name}.txt'), str(S_DIR / f'{name}.txt')], capture_output=True, text=True)
    (out / f'{name}.v_S.cmp').write_text(chk2.stdout + chk2.stderr)
    detail += ' | v S: ' + ('SAME' if chk2.returncode == 0 else ('DIFFERS' if chk2.returncode == 1 else 'ERROR')) + ' (' + chk2.stdout.strip()[-120:] + ')'
    return summary(side, name, 3840, secs, 'SAME' if chk.returncode == 0 else ('DIFFERS' if chk.returncode == 1 else 'ERROR'), detail)


def verify():
    """The prediction check (LANE_N_PREDICTION.md items 1-5) over the lane's own logs and summary rows."""
    P = W / 'prep'
    why, notes, rows_out = [], [], []
    rd = lambda p: (P / p).read_text(errors='replace') if (P / p).exists() else ''
    lane = rd('lane_r.log')
    for s in ('build_R', 'gen_R', 'status_R', 'suite_R', 'goldfish_R', 'replays_R'):
        if not (P / f'{s}.done').exists():
            why.append(f'{s} not done')
        if (P / f'{s}.FAILED').exists():
            why.append(f'{s} FAILED')
    if not re.search(r'gen_R ids: SAME .*generated secondary_energy_type None lines: 0$', lane, re.M):
        why.append('gen_R ids line not as predicted')
    if not re.search(r'gen_R database: SAME .*generated secondary_energy_type None lines: 4154$', lane, re.M):
        why.append('gen_R database line not as predicted')
    st = rd('status_R.txt')
    for want in ("card_status: all 4577 | new C1/SP1/P-C: 260 {'Complete': 256, 'RulesUnverified': 4}",
                 "   C1 217 {'Complete': 213, 'RulesUnverified': 4}", "   SP1 30 {'Complete': 30}", "   P-C 13 {'Complete': 13}",
                 'older cards neither Complete nor RulesUnverified: 0 []',
                 'Trainers with a new or B4b printing (same name and text) whose printings differ in status: 0',
                 "incomplete new ids: [('C1 015', 'RulesUnverified'), ('C1 051', 'RulesUnverified'), ('C1 135', 'RulesUnverified'), ('C1 184', 'RulesUnverified')]",
                 "all by status: {'Complete': 4565, 'RulesUnverified': 12}", 'STATUS_CHECK OK'):
        if want not in st.splitlines():
            why.append(f'status line missing: {want[:70]}')
    if not re.search(r'suite_R rc=0 in \d+ s: passed 2633 failed 0 ignored 0 compile_errors 0 failing \[\]$', lane, re.M):
        why.append('suite not "passed 2633 failed 0 ignored 0"')
    if 'goldfish_R strings TEST_CARD_SUPPORT_MISSING_ATTACK: programs/deckgym 0, programs/goldfish 0, rebuilt plain goldfish 0' not in lane:
        why.append('strings counts not 0/0/0')
    if not re.search(r'goldfish_R plain test rc=0: test result: ok\. 1 passed; 0 failed', lane):
        why.append('goldfish_card_support_test not "1 passed"')
    for g in ('build_R: guard OK', 'goldfish_plain: guard OK', 'goldfish_test_utils: guard OK'):
        if g not in lane:
            why.append(f'missing "{g}"')
    summ = W / 'games/summary.tsv'
    rows = [l.rstrip('\n').split('\t') for l in summ.read_text().splitlines() if l.startswith('r\t')] if summ.exists() else []
    by = {}
    for r in rows:
        if r[1] in by:
            why.append(f'row {r[1]} twice')
        by[r[1]] = r
    if sorted(by) != sorted(REPLAYS):
        why.append(f'replay rows: {len(by)} of 18 (missing {sorted(set(REPLAYS) - set(by))})')
    n_rules, n_vs = 0, 0
    for name in REPLAYS:
        r = by.get(name)
        if not r:
            continue
        verdict, detail = r[4], r[5]
        ref_ok = (verdict == 'SAME' and name not in KNOWN_DIFFERS) or (verdict == 'DIFFERS' and detail.startswith(KNOWN_DIFFERS.get(name, '\0')))
        if not ref_ok:
            why.append(f'{name}: v reference {verdict} ({detail[:60]}) not as predicted')
        vs = detail.split(' | v S: ', 1)[1] if ' | v S: ' in detail else ''
        if name.startswith('08a9b3a_10_cli_'):
            vs_ok = vs == 'SAME' or vs.startswith('version-only')
            if vs.startswith('version-only'):
                notes.append(f'{name}: v S version-only difference (listed, not a failure): {vs}')
        elif name == '08a9b3a_10_goldfish':
            vs_ok = vs in ('page SAME, coverage sha SAME',) or (vs.startswith('page version-only') and vs.endswith('coverage sha SAME'))
        elif name == '08a9b3a_10_run_screen':
            vs_ok = vs.startswith('SAME')
        else:
            vs_ok = vs == 'sha SAME, diff.tsv ='
            if vs.startswith('sha DIFFERS, diff.tsv ='):
                notes.append(f'{name}: sha differs from S but the deals v the reference are S\'s: a format change? (STOP: nothing to diff; 148 §2.5)')
            if re.search(r'rules page: .*: no RULE finding', detail):
                n_rules += 1
            else:
                why.append(f'{name}: rules page not "no RULE finding"')
        if not vs_ok:
            why.append(f'{name}: v S "{vs}"')
        else:
            n_vs += 1
        rows_out.append(f'{name}\t{verdict}\t{r[2]} games\t{r[3]} s\tv S: {vs}')
    if n_rules != 11:
        why.append(f'clean rules pages {n_rules} of 11')
    (W / 'verify').mkdir(exist_ok=True)
    text = ('R8 Lane N verify (replay_r8.py verify) ' + time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\n'
            + '\n'.join(rows_out) + '\n' + ''.join(f'note: {n}\n' for n in notes)
            + (f'v S as predicted: {n_vs} of 18; clean rules pages: {n_rules} of 11\n')
            + ('VERIFY PASS' if not why else 'VERIFY FAIL: ' + '; '.join(why)) + '\n')
    (W / 'verify' / 'VERIFY.txt').write_text(text)
    print(text, end='')
    return 0 if not why else 1


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'verify':
        sys.exit(verify())
    if len(sys.argv) != 3 or sys.argv[1] != 'r':
        sys.exit(__doc__)
    run_one(sys.argv[1], sys.argv[2])
