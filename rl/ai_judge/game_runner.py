"""The game runner: plan, run, status, scan-keys. One DG process per arm, a session kill after every arm, outcome-blind rows."""
import argparse
import datetime
import glob
import hashlib
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_kit  # noqa: E402
import game_shadow  # noqa: E402

KEY_PATTERNS = (r'AIza[0-9A-Za-z_\-]{20,}', r'AQ\.[0-9A-Za-z_\-]{20,}')
DROP_CLASSES = ('engine_error', 'kx3_route')
POLL_S = 5


OUTCOME_LINE_RE = re.compile(r'^(Player [01] won:|Draws:|Ran [\d,]+ simulations)')
OUTCOME_GUARD_RE = re.compile(r'(?i)\bwon\b|winner|draws?:')

class Refuse(Exception):
    pass


class StopRun(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# ------------------------------------------------------------------------------------------------ helpers
def parse_cells(s):
    if s is None:
        return list(range(16))
    out = []
    for part in s.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-')
            out += list(range(int(a), int(b) + 1))
        elif part:
            out.append(int(part))
    if any(not 0 <= c < 16 for c in out):
        raise Refuse('cells must be 0-15')
    return out


def sid_of(pid):
    try:
        with open('/proc/%d/stat' % pid) as f:
            rest = f.read().rpartition(')')[2].split()
        return int(rest[3]), rest[0]
    except (OSError, ValueError, IndexError):
        return None, None


def session_members(sid):
    out = []
    for p in glob.glob('/proc/[0-9]*/stat'):
        try:
            with open(p) as f:
                rest = f.read().rpartition(')')[2].split()
            if int(rest[3]) == sid and rest[0] != 'Z':
                out.append(int(p.split('/')[2]))
        except (OSError, ValueError, IndexError):
            continue
    return out


def kill_session(sid, timeout_s=30):
    """SIGKILL every process in session `sid` (never ours); repeat until none is left, zombies aside. Raises OSError('orphans') if some remain after timeout_s."""
    if sid <= 1 or sid == os.getsid(0) or sid == os.getpgid(0):
        raise ValueError('refusing to kill session %s' % sid)
    me = os.getpid()
    t0 = time.monotonic()
    while True:
        members = [p for p in session_members(sid) if p != me]
        if not members:
            return
        for p in members:
            try:
                os.kill(p, signal.SIGKILL)
            except OSError:
                pass
        if time.monotonic() - t0 > timeout_s:
            if [p for p in session_members(sid) if p != me]:
                raise OSError('orphans')
            return
        time.sleep(0.1)


def append_jsonl(path, obj):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(obj) + '\n')
        f.flush()
        os.fsync(f.fileno())


def write_json(path, obj):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)


def iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def scan_paths(paths, literal=None):
    """[(file, line number)] of lines that match a key pattern, or hold `literal`. Never returns the match."""
    pats = [re.compile(p) for p in KEY_PATTERNS]
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _d, fs in os.walk(p):
                files += [os.path.join(root, f) for f in fs]
        else:
            files.append(p)
    hits = []
    for f in files:
        try:
            with open(f, encoding='utf-8', errors='replace') as fh:
                for n, line in enumerate(fh, 1):
                    if any(r.search(line) for r in pats) or (literal and literal in line):
                        hits.append((f, n))
        except OSError:
            continue
    return hits


# ------------------------------------------------------------------------------------------------ plan
def build_plan(stage, ks, cells):
    k_ok = {'dev': lambda k: k in game_kit.DEV_K, 1: lambda k: k == game_kit.STAGE1_K or k in game_kit.RESTART_K}
    if stage == 2:
        if sorted(ks) != list(range(len(ks))) or not 1 <= len(ks) <= 8:
            raise Refuse('stage 2 needs k = 0..m-1 with m <= 8')
    elif any(not k_ok[stage](k) for k in ks):
        raise Refuse('a k is outside the stage\'s range')
    deals = []
    for k in sorted(ks):
        order = [c for c in game_kit.STAGE1_ORDER if c in cells] if stage == 1 else sorted(cells)
        for cell in order:
            bits = game_kit.cell_bits(cell)
            deals.append({'deal_idx': len(deals), 'k': k, 'cell': cell, 'bits': bits, 'seed': game_kit.seed(cell, k), 'pilot_deck': game_kit.DECKS[bits['deck']],
                          'opp_list': game_kit.LISTS[bits['list']], 'policy': game_kit.POLICIES[bits['policy']], 'seat': bits['seat']})
    return deals


def stage_value(s):
    return {'1': 1, '2': 2, 'dev': 'dev'}[s]


def cmd_plan(a):
    try:
        stage = stage_value(a.stage)
        ks = [a.k] if a.k is not None else [int(x) for x in a.k_list.split(',')] if a.k_list else None
        if a.k_range:
            lo, hi = a.k_range.split('-')
            ks = list(range(int(lo), int(hi) + 1))
        if not ks:
            raise Refuse('give --k, --k-list or --k-range')
        deals = build_plan(stage, ks, parse_cells(a.cells))
    except (Refuse, ValueError) as e:
        print('REFUSED: ' + str(e))
        return 2
    write_json(a.out, {'stage': stage, 'deals': deals})
    print('planned %d deals for stage %s' % (len(deals), a.stage))
    return 0


# ------------------------------------------------------------------------------------------------ headroom, classification
def headroom_ok(stage, total, accrued, in_flight, largest_g_charge, stage1_max_game_charge=None):
    left = total - accrued - in_flight
    if stage == 1:
        return left >= 2 + 2 * largest_g_charge
    return left >= 2 * (stage1_max_game_charge or 0)


def went_first_of(rows):
    for r in rows:
        if r.get('schema') == 'gemini_game_decision_v1' and r.get('turn_count', 0) >= 1:
            tc, cp = r['turn_count'], r['current_player']
            return cp if tc % 2 == 1 else 1 - cp
    return None


def judge_block(rows, mock, went_first):
    dec = [r for r in rows if r.get('schema') == 'gemini_game_decision_v1']
    plans = [r for r in rows if r.get('schema') == 'gemini_game_plan_v1']
    inter = [r for r in dec if r.get('mode') == 'intervene']
    by = lambda it: {k: sum(1 for x in it if x == k) for k in sorted(set(it), key=str)}
    jrows = [r['judge'] for r in dec if r.get('judge')]
    tries = [t for r in dec for t in (r.get('tries') or [])]
    fb = [r for r in dec if r.get('fallback')]
    return {'decisions': len(dec), 'setup_decisions': sum(1 for r in dec if r.get('mode') == 'setup'), 'interventions': len(inter),
            'interventions_by_kind': by([r['kind'] for r in inter]), 'fallbacks': len(fb), 'fallbacks_by_reason': by([r['fallback']['reason'] for r in fb]),
            'reasks_by_reason': by([r.get('reask_reason') for r in inter]), 'calls': sum(r.get('n_judge_calls', 0) for r in dec), 'tries': len(tries),
            'calls_by_outcome': by(['choice' if j.get('plan_number') is not None else 'no_choice' for j in jrows]), 'tries_by_outcome': by([t['outcome'] for t in tries]),
            'root_dup_of': sum((r.get('root_check') or {}).get('n_dup_of', 0) for r in dec), 'root_noop': sum((r.get('root_check') or {}).get('n_noop', 0) for r in dec),
            'ledger_charge_usd': sum(r.get('ledger_charge_usd', 0) for r in dec), 'actual_usd': sum(((j.get('cost') or {}).get('usd') or 0) for j in jrows),
            'model_returned': sorted({j['model_returned'] for j in jrows if j.get('model_returned')}), 'vertex_project': sorted({j['vertex_project'] for j in jrows if j.get('vertex_project')}),
            'frozen_all': all(j.get('frozen') for j in jrows) if jrows else None, 'mock': (all(j.get('mock') for j in jrows) if jrows else bool(mock)), 'went_first': went_first,
            'stale': sum(1 for p in plans if p.get('ended') == 'stale'), 'plans_started': len({r['plan']['plan_id'] for r in dec if r.get('plan')}),
            'plans_completed': sum(1 for p in plans if p.get('ended') == 'completed'), 'open_plans_at_end': sum(1 for p in plans if p.get('ended') == 'game_ended')}


def classify(arm, row, seats):
    """-> (failure class or None, detail). seats: {seat: role}; the first match wins (class 5 and 6 here; 1-4 are decided by the caller)."""
    proto = {p['seat']: p for p in row['protocol']}
    fatal_shadow = arm == 'G' and row.get('_fatal_shadow')
    opp_fb = [s for s, role in seats.items() if role == 'opponent' and s in proto and proto[s]['fallbacks'] > 0]
    pilot_fb = [s for s, role in seats.items() if role == 'pilot' and s in proto and proto[s]['fallbacks'] > 0]
    if fatal_shadow:
        return 'kx3_route', 'g_shadow'
    if opp_fb:
        return 'kx3_route', '%s:opponent' % arm
    if arm == 'K' and pilot_fb:
        return 'kx3_route', 'K:pilot'
    if arm == 'G' and pilot_fb:
        return 'pilot_side', 'G:pilot'
    return None, None


# ------------------------------------------------------------------------------------------------ the runner
class Runner:
    def __init__(self, a, environ=None, mono=time.monotonic, wall=time.time, sleep=time.sleep, utcnow=utc_now):
        self.a, self.env = a, dict(os.environ if environ is None else environ)
        self.mono, self.wall, self.sleep, self.utcnow = mono, wall, sleep, utcnow
        self.D = os.path.abspath(a.run_dir)
        self.repo = os.path.abspath(a.repo)
        self.stage = stage_value(a.stage)
        self.mock = a.mock_judge is not None
        self.live = not self.mock
        self.live_dg = None
        self.stop_reason = None
        self.model_ref = a.expect_model_version
        self.call_cap = a.call_cap

    # ---- paths and commands
    def p(self, *x):
        return os.path.join(self.D, *x)

    def deal_dir(self, deal):
        return self.p('deals', '%04d-k%d-c%02d' % (deal['deal_idx'], deal['k'], deal['cell']))

    def tag(self, deal, attempt, arm):
        return '%04d-k%d-c%02d-a%d-%s' % (deal['deal_idx'], deal['k'], deal['cell'], attempt, arm)

    def kx3_cmd(self):
        return 'env -u VERTEX_API_KEY -u VERTEX_PROJECT %s --bot kx3' % shlex.quote(os.path.join(self.a.engine_bins, 'protocol_bot'))

    def bot_cmd(self, deal, tag, arm_dir):
        a = self.a
        parts = ['python3', '-I', '-B', os.path.join(self.repo, 'rl', 'ai_judge', 'game_bot.py'), '--deck-file', os.path.join(self.repo, deal['pilot_deck']),
                 '--plans-bin', os.path.join(a.judge_bins, 'judge_plans'), '--protocol-bot', os.path.join(a.engine_bins, 'protocol_bot'),
                 '--pid-prefix', game_kit.pid_prefix(deal['seed'], deal['cell'], 'G'), '--deal-tag', tag, '--rows', os.path.join(arm_dir, 'rows.jsonl'),
                 '--shadow-log', os.path.join(arm_dir, 'shadow.jsonl'), '--ledger', os.path.abspath(a.ledger), '--ledger-total-usd', str(a.ledger_total_usd),
                 '--call-cap', str(self.call_cap), '--stop-file', self.p('STOP'), '--bot-timeout-s', '2700']
        if self.mock:
            parts += ['--mock-judge', a.mock_judge, '--mock-seed', str(a.mock_seed)]
            if a.force_fallback_every:
                parts += ['--force-fallback-every', str(a.force_fallback_every)]
        return ' '.join(shlex.quote(x) for x in parts)

    def arm_argv(self, deal, arm, tag, arm_dir):
        """-> (argv, {seat: role}, [proto seats in seat order])"""
        seat = deal['seat']
        opp = 1 - seat
        codes, cmds = {}, {}
        codes[seat] = 'proto'
        cmds[seat] = self.bot_cmd(deal, tag, arm_dir) if arm == 'G' else self.kx3_cmd()
        if deal['policy'] == 'kx3':
            codes[opp], cmds[opp] = 'proto', self.kx3_cmd()
        else:
            codes[opp] = 'km3'
        pilot_deck, opp_deck = os.path.join(self.repo, deal['pilot_deck']), os.path.join(self.repo, deal['opp_list'])
        deck_a, deck_b = (pilot_deck, opp_deck) if seat == 0 else (opp_deck, pilot_deck)
        argv = ['nice', '-n', '19', os.path.join(self.a.engine_bins, 'deckgym'), 'simulate', deck_a, deck_b, '--players', '%s,%s' % (codes[0], codes[1])]
        for s, flag in ((0, '--bot-a'), (1, '--bot-b')):
            if s in cmds:
                argv += [flag, cmds[s]]
        argv += ['--bot-timeout-ms', str(game_kit.BOT_TIMEOUT_MS), '--bot-log', os.path.join(arm_dir, 'protolog'), '--results-output', os.path.join(arm_dir, 'result'), '--num', '1',
                 '--seed', str(deal['seed'])]
        seats = {seat: 'pilot', opp: 'opponent'}
        return argv, seats, sorted(cmds)

    def dg_env(self, arm):
        env = {k: self.env[k] for k in game_kit.SHADOW_ENV_KEEP if k in self.env}
        if arm == 'G' and self.live:
            env.update({k: v for k, v in self.env.items() if k.startswith('VERTEX_')})
        return env

    def ledger_accrued(self):
        try:
            with open(self.a.ledger) as f:
                return float(json.load(f)['accrued_usd'])
        except (OSError, ValueError, KeyError):
            return None

    # ---- one arm
    def kill_dg(self, proc):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            pass
        kill_session(proc.pid)

    def run_arm(self, deal, arm, attempt):
        a = self.a
        tag = self.tag(deal, attempt, arm)
        arm_dir = os.path.join(self.deal_dir(deal), 'a%d' % attempt, arm)
        os.makedirs(arm_dir, exist_ok=True)
        argv, seats, proto_seats = self.arm_argv(deal, arm, tag, arm_dir)
        before = self.ledger_accrued()
        started = iso(self.utcnow())
        out, err = open(os.path.join(arm_dir, 'stdout.txt'), 'w'), open(os.path.join(arm_dir, 'stderr.txt'), 'w')
        t_start = self.mono()
        proc = subprocess.Popen(argv, stdout=out, stderr=err, stdin=subprocess.DEVNULL, env=self.dg_env(arm), start_new_session=True)
        self.live_dg = proc
        infra, killed_for_stop, orphan = None, False, False
        prev_m, prev_w, max_gap = self.mono(), self.wall(), 0.0
        try:
            while proc.poll() is None:
                self.sleep(POLL_S)
                now_m, now_w = self.mono(), self.wall()
                gap = max(now_m - prev_m, now_w - prev_w) - POLL_S
                prev_m, prev_w = now_m, now_w
                max_gap = max(max_gap, gap)
                if os.path.exists(self.p('STOP')):
                    killed_for_stop = True
                elif now_m - t_start > a.game_wall_s:
                    infra = 'wall_limit'
                elif gap > game_kit.PAUSE_GAP_S:
                    infra = 'pause_gap (%.0f s)' % gap
                elif os.path.exists(self.p('PAUSE')):
                    infra = 'pause_marker'
                if infra or killed_for_stop:
                    try:
                        self.kill_dg(proc)
                    except OSError:
                        orphan = True
                    break
            rc = proc.wait()
            if not orphan:
                try:
                    kill_session(proc.pid)
                except OSError:
                    orphan = True
        finally:
            self.live_dg = None
            out.close()
            err.close()
        lock = os.path.abspath(a.ledger) + '.lock'
        lock_removed = False
        if os.path.exists(lock):
            if not orphan:
                os.remove(lock)
                lock_removed = True
        rows = read_jsonl(os.path.join(arm_dir, 'rows.jsonl')) if arm == 'G' else []
        if arm == 'G':
            started_ids = {r['plan']['plan_id']: r['plan'] for r in rows if r.get('schema') == 'gemini_game_decision_v1' and r.get('plan')}
            ended_ids = {r['plan_id'] for r in rows if r.get('schema') == 'gemini_game_plan_v1'}
            for pid, pl in started_ids.items():
                if pid not in ended_ids:
                    append_jsonl(os.path.join(arm_dir, 'rows.jsonl'), {'schema': 'gemini_game_plan_v1', 'deal_tag': tag, 'plan_id': pid, 'n_steps': pl.get('n_steps'),
                                                                       'steps_played': sum(1 for r in rows if (r.get('follow') or {}).get('plan_id') == pid and r.get('mode') == 'follow') + 1,
                                                                       'ended': 'game_ended'})
            rows = read_jsonl(os.path.join(arm_dir, 'rows.jsonl'))
        # the result file: completion, lifecycle_errors, plies, final_turn only
        res_files = sorted(glob.glob(os.path.join(arm_dir, 'result', 'game_*.json')))
        completion = lifecycle = plies = final_turn = result_file = result_sha = None
        if res_files:
            with open(res_files[0], 'rb') as f:
                raw = f.read()
            result_sha = hashlib.sha256(raw).hexdigest()
            j = json.loads(raw)
            completion, lifecycle, plies, final_turn = j.get('completion'), j.get('lifecycle_errors'), j.get('plies'), j.get('final_turn')
            result_file = os.path.relpath(res_files[0], self.D)
        protocol = self.read_protocol(arm_dir, seats, proto_seats)
        row = {'schema': 'gemini_game_arm_v1', 'stage': self.stage, 'k': deal['k'], 'cell': deal['cell'], 'bits': deal['bits'], 'seed': deal['seed'], 'arm': arm, 'attempt': attempt,
               'deal_tag': tag, 'started_utc': started, 'finished_utc': iso(self.utcnow()), 'seconds': self.mono() - t_start, 'exit_code': rc,
               'rayon_threads': self.env.get('RAYON_NUM_THREADS'), 'result_file': result_file, 'result_sha256': result_sha, 'completion': completion, 'lifecycle_errors': lifecycle,
               'plies': plies, 'final_turn': final_turn, 'protocol': protocol, 'max_gap_s': max_gap, 'ledger_before_usd': before, 'ledger_after_usd': self.ledger_accrued(),
               'ledger_lock_removed': lock_removed, 'failure': None, 'failure_detail': None}
        if arm == 'G':
            row['judge'] = judge_block(rows, self.mock, went_first_of(rows))
            row['_fatal_shadow'] = any(r.get('fatal') == 'shadow' for r in rows)
        stop = None
        if os.path.exists(self.p('STOP')):
            try:
                with open(self.p('STOP')) as f:
                    stop = json.load(f).get('reason')
            except ValueError:
                stop = 'unreadable'
        if infra or (rc is not None and rc < 0 and not killed_for_stop):
            row['failure'], row['failure_detail'] = 'infra', infra or 'signal %d' % (-rc)
        elif rc == 2:
            row['failure'], row['failure_detail'] = 'config', 'dg exit 2'
        elif stop:
            row['failure'], row['failure_detail'] = 'stop:' + stop, stop
        elif rc == 101 or completion != 'completed' or rc != 0:
            row['failure'], row['failure_detail'] = 'engine_error', 'exit %s completion %s' % (rc, completion)
        else:
            row['failure'], row['failure_detail'] = classify(arm, row, seats)
        if row['failure'] is None and arm == 'G' and row['_fatal_shadow']:
            row['failure'], row['failure_detail'] = 'kx3_route', 'g_shadow'
        row.pop('_fatal_shadow', None)
        if row['failure'] in ('engine_error', 'kx3_route', 'pilot_side', 'infra', 'config') or (row['failure'] or '').startswith('stop:'):
            try:
                with open(os.path.join(arm_dir, 'stderr.txt'), errors='replace') as f:
                    raw_err = f.read()
                kept = ''.join(l for l in raw_err.splitlines(True) if not OUTCOME_LINE_RE.match(l))
                tail = self.scrub(kept)[-2000:]
                row['stderr_tail'] = '[withheld: outcome-like text]' if OUTCOME_GUARD_RE.search(tail) else tail
            except OSError:
                pass
        append_jsonl(self.p('games.jsonl'), row)
        if orphan:
            raise StopRun('orphans')
        return row

    def scrub(self, text):
        for p in KEY_PATTERNS:
            text = re.sub(p, '[redacted]', text)
        key = self.env.get('VERTEX_API_KEY')
        return text.replace(key, '***') if key else text

    def read_protocol(self, arm_dir, seats, proto_seats):
        files = sorted(glob.glob(os.path.join(arm_dir, 'protolog', 'protocol_*.jsonl')), key=lambda f: int(re.search(r'_(\d+)\.jsonl$', f).group(1)) if re.search(r'_(\d+)\.jsonl$', f) else 0)
        out = []
        for seat, f in zip(proto_seats, files):
            lines = read_jsonl(f)
            dec = [l for l in lines if not l.get('summary')]
            summ = next((l for l in lines if l.get('summary')), {})
            secs = [l.get('secs') or 0 for l in dec]
            out.append({'seat': seat, 'role': seats[seat], 'decisions': summ.get('decisions', len(dec)), 'fallbacks': summ.get('fallbacks', sum(1 for l in dec if l.get('fallback'))),
                        'errors': summ.get('errors', sum(1 for l in dec if l.get('error'))), 'startup_secs': max([l.get('startup_secs') or 0 for l in dec] or [0]),
                        'decide_secs_sum': sum(secs), 'decide_secs_max': max(secs or [0])})
        return out

    # ---- deals
    def deal_rows(self):
        return read_jsonl(self.p('deals.jsonl'))

    def rows_of_record(self):
        best = {}
        for r in self.deal_rows():
            if r['complete'] and (r['deal_idx'] not in best or r['attempt'] > best[r['deal_idx']]['attempt']):
                best[r['deal_idx']] = r
        return best

    def play_deal(self, deal, attempt0):
        attempt, infra_n = attempt0, 0
        while True:
            rows = {}
            result = 'done'
            for arm in self.arms:
                row = self.run_arm(deal, arm, attempt)
                rows[arm] = row
                f = row['failure']
                if f == 'infra':
                    result = 'infra'
                    break
                if f == 'config':
                    result = 'config'
                    break
                if f and f.startswith('stop:'):
                    result = f
                    break
            g, k = rows.get('G'), rows.get('K')
            drop = next(({'arm': arm, 'class': r['failure']} for arm, r in (('G', g), ('K', k)) if r and r['failure'] in DROP_CLASSES), None)
            deal_row = {'schema': 'gemini_game_deal_v1', 'stage': self.stage, 'deal_idx': deal['deal_idx'], 'k': deal['k'], 'cell': deal['cell'], 'bits': deal['bits'], 'seed': deal['seed'],
                        'attempt': attempt, 'complete': result == 'done', 'g_deal_tag': g['deal_tag'] if g else None, 'k_deal_tag': k['deal_tag'] if k else None,
                        'g_failure': g['failure'] if g else None, 'k_failure': k['failure'] if k else None, 'dropped': drop is not None and result == 'done', 'drop_reason': drop if result == 'done' else None}
            append_jsonl(self.p('deals.jsonl'), deal_row)
            if result == 'infra':
                infra_n += 1
                if infra_n >= 3:
                    raise StopRun('infra_repeat')
                attempt += 1
                continue
            if result == 'config':
                raise StopRun('config')
            if result.startswith('stop:'):
                raise StopRun(result)
            return deal_row, rows

    def check_model(self, rows):
        g = rows.get('G')
        if not g:
            return
        vals = g['judge']['model_returned']
        if self.model_ref is None and vals:
            self.model_ref = vals[0]
        if self.model_ref is not None and any(v != self.model_ref for v in vals):
            raise StopRun('model_version')

    def pooled_rate(self):
        arms = {r['deal_tag']: r for r in read_jsonl(self.p('games.jsonl'))}
        iv = fb = 0
        for d in self.rows_of_record().values():
            g = arms.get(d['g_deal_tag'])
            if g and g.get('judge'):
                iv += g['judge']['interventions']
                fb += g['judge']['fallbacks']
        return fb / iv if iv else 0.0

    def after_deal(self, deal_row, rows, deals):
        self.check_model(rows)
        best = self.rows_of_record()
        if self.stage == 2:
            ks = {}
            for r in best.values():
                ks.setdefault(r['k'], set()).add(r['cell'])
            if ks.get(deal_row['k']) == set(range(16)) and self.pooled_rate() > game_kit.FALLBACK_LIMIT:
                raise StopRun('fallback_rate')
        if self.stage == 1 and sum(1 for r in best.values() if r['dropped']) > game_kit.STAGE1_MAX_DROPS:
            raise StopRun('drops')

    def stop_file_reason(self):
        if os.path.exists(self.p('STOP')):
            try:
                with open(self.p('STOP')) as f:
                    return 'stop:' + str(json.load(f).get('reason'))
            except ValueError:
                return 'stop:unreadable'
        return None

    def headroom_check(self):
        if not self.live:
            return
        try:
            with open(self.a.ledger) as f:
                d = json.load(f)
        except OSError:
            return
        arms = [r for r in read_jsonl(self.p('games.jsonl')) if r['arm'] == 'G' and r.get('judge')]
        largest = max([r['judge']['ledger_charge_usd'] for r in arms] or [0.0])
        if not headroom_ok(self.stage, float(d['total_usd']), float(d['accrued_usd']), float(d.get('in_flight_usd') or 0), largest, self.a.stage1_max_game_charge):
            raise StopRun('ledger_headroom')

    def run(self, deals):
        a = self.a
        self.arms = a.arms.split(',')
        os.makedirs(self.D, exist_ok=True)
        write_json(self.p('run_start.json'), {'stage': self.stage, 'plan': os.path.abspath(a.plan), 'ledger': os.path.abspath(a.ledger), 'ledger_total_usd': a.ledger_total_usd,
                                              'started_utc': iso(self.utcnow())})
        if self.model_ref is None and a.resume:
            for r in read_jsonl(self.p('games.jsonl')):
                if r['arm'] == 'G' and r.get('judge') and r['judge']['model_returned']:
                    self.model_ref = r['judge']['model_returned'][0]
                    break
        stop = None
        try:
            for deal in deals:
                best = self.rows_of_record()
                if deal['deal_idx'] in best:
                    continue
                while os.path.exists(self.p('PAUSE')):
                    self.sleep(POLL_S)
                s = self.stop_file_reason()
                if s:
                    raise StopRun(s)
                if self.utcnow() >= datetime.datetime.strptime(game_kit.STOP_AT_UTC, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=datetime.timezone.utc):
                    raise StopRun('stop_date')
                self.headroom_check()
                prior = [r['attempt'] for r in self.deal_rows() if r['deal_idx'] == deal['deal_idx']]
                for d in glob.glob(os.path.join(self.deal_dir(deal), 'a[0-9]*')):
                    m = re.fullmatch(r'a(\d+)', os.path.basename(d))
                    if m:
                        prior.append(int(m.group(1)))
                deal_row, rows = self.play_deal(deal, max(prior or [0]) + 1)
                self.after_deal(deal_row, rows, deals)
        except StopRun as s:
            stop = s.reason
        self.stop_reason = stop
        return self.finish(deals)

    def finish(self, deals, signalled=False):
        best = self.rows_of_record()
        write_json(self.p('run_end.json'), {'stage': self.stage, 'planned_deals': len(deals), 'complete_deals': len(best), 'stopped_early': self.stop_reason is not None,
                                            'stop_reason': self.stop_reason, 'finished_utc': iso(self.utcnow()), 'model_returned': self.model_ref})
        print('run_end: complete %d of %d, stop_reason %s' % (len(best), len(deals), self.stop_reason))
        return 0 if self.stop_reason is None else 1


def live_start_checks(r):
    for k in ('VERTEX_API_KEY', 'VERTEX_PROJECT'):
        if not r.env.get(k):
            raise Refuse('a live run needs %s set' % k)
    p = subprocess.run(['python3', '-I', '-B', os.path.join(r.repo, 'rl', 'ai_judge', 'freeze8.py'), 'check', '--frozen', os.path.join(r.repo, 'rl', 'ai_judge', 'FROZEN8.json'),
                        '--engine-bins', r.a.engine_bins, '--judge-bins', r.a.judge_bins, '--repo', r.repo], capture_output=True, timeout=1700, env=game_shadow.shadow_env(os.environ))
    if p.returncode != 0:
        raise Refuse('freeze8 check did not pass (exit %d)' % p.returncode)


def cmd_run(a, **inject):
    with open(a.plan) as f:
        plan = json.load(f)
    r = Runner(a, **inject)
    try:
        if stage_value(a.stage) != plan.get('stage'):
            raise Refuse('--stage differs from the plan\'s stage')
        if r.stage in (1, 2) and (a.mock_judge or a.force_fallback_every):
            raise Refuse('stage 1 and 2 take no mock flags')
        if r.stage in (1, 2) and a.arms != 'G,K':
            raise Refuse('stage 1 and 2 run both arms')
        if r.live and r.stage == 2 and (not a.call_cap_given or a.stage1_max_game_charge is None or not a.expect_model_version):
            raise Refuse('a live stage 2 needs --call-cap, --stage1-max-game-charge and --expect-model-version')
        if r.live and a.force_fallback_every:
            raise Refuse('--force-fallback-every is refused in live mode')
        for n in game_kit.FORBIDDEN_ENV:
            if n in r.env:
                raise Refuse('a forbidden environment name is set: ' + n)
        if os.path.exists(os.path.join(r.D, 'STOP')):
            raise Refuse('the STOP file exists: the laptop clears it before a resume')
        if os.path.exists(os.path.join(r.D, 'deals.jsonl')) and not a.resume:
            raise Refuse('the run folder has deals: use --resume')
        if r.live:
            live_start_checks(r)
    except Refuse as e:
        print('REFUSED: ' + str(e))
        return 2
    deals = plan['deals'][:a.max_deals] if a.max_deals else plan['deals']

    def on_signal(signum, frame):
        if r.live_dg is not None:
            try:
                os.killpg(r.live_dg.pid, signal.SIGKILL)
            except OSError:
                pass
            try:
                kill_session(r.live_dg.pid)
                lock = os.path.abspath(a.ledger) + '.lock'
                if os.path.exists(lock):
                    os.remove(lock)
            except (OSError, ValueError):
                pass
        r.stop_reason = 'signal'
        r.finish(deals)
        os._exit(130)
    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
        signal.signal(s, on_signal)
    return r.run(deals)


# ------------------------------------------------------------------------------------------------ status, scan
def stat(xs):
    xs = sorted(xs)
    return (min(xs), xs[len(xs) // 2], max(xs)) if xs else None


def cmd_status(a):
    D = a.run_dir
    start = {}
    if os.path.exists(os.path.join(D, 'run_start.json')):
        with open(os.path.join(D, 'run_start.json')) as f:
            start = json.load(f)
    deals = read_jsonl(os.path.join(D, 'deals.jsonl'))
    games = read_jsonl(os.path.join(D, 'games.jsonl'))
    best = {}
    for r in deals:
        if r['complete'] and (r['deal_idx'] not in best or r['attempt'] > best[r['deal_idx']]['attempt']):
            best[r['deal_idx']] = r
    planned = None
    if start.get('plan') and os.path.exists(start['plan']):
        with open(start['plan']) as f:
            planned = len(json.load(f)['deals'])
    print('deals complete %d of %s' % (len(best), planned))
    print('games by arm: G %d, K %d' % (sum(1 for g in games if g['arm'] == 'G'), sum(1 for g in games if g['arm'] == 'K')))
    if start.get('ledger') and os.path.exists(start['ledger']):
        with open(start['ledger']) as f:
            l = json.load(f)
        print('ledger accrued %.4f of total %.4f' % (l['accrued_usd'], start.get('ledger_total_usd', l['total_usd'])))
    secs = {arm: [g['seconds'] for g in games if g['arm'] == arm] for arm in ('G', 'K')}
    print('seconds: sum %.1f, mean G %.1f, mean K %.1f' % (sum(secs['G']) + sum(secs['K']), sum(secs['G']) / len(secs['G']) if secs['G'] else 0, sum(secs['K']) / len(secs['K']) if secs['K'] else 0))
    rec_tags = {d['g_deal_tag'] for d in best.values()}
    gg = [g for g in games if g['arm'] == 'G' and g.get('judge') and g['deal_tag'] in rec_tags]
    if gg:
        ch, au, dc = [g['judge']['ledger_charge_usd'] for g in gg], [g['judge']['actual_usd'] for g in gg], [g['judge']['calls'] for g in gg]
        print('per G game: ledger charge mean %.4f max %.4f; actual_usd mean %.4f max %.4f; judge decisions mean %.1f max %d' % (sum(ch) / len(ch), max(ch), sum(au) / len(au), max(au), sum(dc) / len(dc), max(dc)))
        iv, fb = sum(g['judge']['interventions'] for g in gg), sum(g['judge']['fallbacks'] for g in gg)
        print('pooled G fallback rate (setup excluded): %.4f (%d of %d)' % (fb / iv if iv else 0.0, fb, iv))
        rates = [g['judge']['fallbacks'] / g['judge']['interventions'] if g['judge']['interventions'] else 0.0 for g in gg]
        print('per-game fallback rate min/median/max: %s' % (stat(rates),))
        worst = max(gg, key=lambda g: g['judge']['fallbacks'] / g['judge']['interventions'] if g['judge']['interventions'] else 0.0)
        print('worst game %s reasons %s' % (worst['deal_tag'], json.dumps(worst['judge']['fallbacks_by_reason'])))
        print('setup decisions: %d' % sum(g['judge']['setup_decisions'] for g in gg))
        for seat in (0, 1):
            s = [g for g in gg if g['bits']['seat'] == seat]
            print('pilot seat %d: decisions %d, fallbacks %d' % (seat, sum(g['judge']['decisions'] for g in s), sum(g['judge']['fallbacks'] for g in s)))
    fails = {}
    for g in games:
        if g.get('failure'):
            key = g['failure'] if g['failure'] != 'kx3_route' else 'kx3_route (%s)' % g.get('failure_detail')
            fails[key] = fails.get(key, 0) + 1
    print('failures by class: %s' % json.dumps(fails, sort_keys=True))
    dropped = [d for d in best.values() if d['dropped']]
    print('dropped deals %d (limit %d)' % (len(dropped), game_kit.STAGE1_MAX_DROPS))
    by_tag = {g['deal_tag']: g for g in games}
    for d in dropped:
        arm = d['drop_reason']['arm']
        tag = d['g_deal_tag'] if arm == 'G' else d['k_deal_tag']
        print('  dropped %s: %s (%s)' % (tag, d['drop_reason']['class'], (by_tag.get(tag) or {}).get('failure_detail')))
    infra = {}
    for g in games:
        if g.get('failure') == 'infra':
            infra[g['failure_detail']] = infra.get(g['failure_detail'], 0) + 1
    print('infra attempts by reason: %s' % json.dumps(infra, sort_keys=True))
    return 0


def cmd_scan(a):
    hits = scan_paths(a.paths, os.environ.get('VERTEX_API_KEY') or None)
    counts = {}
    for f, n in hits:
        counts.setdefault(f, []).append(n)
    for f, ns in counts.items():
        print('%s:%s (%d)' % (f, ','.join(map(str, ns)), len(ns)))
    print('SCAN %s (%d matching lines)' % ('FOUND' if hits else 'CLEAN', len(hits)))
    return 1 if hits else 0


def build_parser():
    p = argparse.ArgumentParser(prog='game_runner')
    sub = p.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('plan')
    s.add_argument('--stage', required=True, choices=['1', '2', 'dev'])
    s.add_argument('--k', type=int)
    s.add_argument('--k-list')
    s.add_argument('--k-range')
    s.add_argument('--cells')
    s.add_argument('--out', required=True)
    s = sub.add_parser('run')
    for n in ('plan', 'run-dir', 'repo', 'engine-bins', 'judge-bins', 'ledger'):
        s.add_argument('--' + n, required=True)
    s.add_argument('--ledger-total-usd', type=float, required=True)
    s.add_argument('--stage', required=True, choices=['1', '2', 'dev'])
    s.add_argument('--arms', default='G,K')
    s.add_argument('--call-cap', type=int, default=None)
    s.add_argument('--stage1-max-game-charge', type=float)
    s.add_argument('--expect-model-version')
    s.add_argument('--mock-judge', choices=['random'])
    s.add_argument('--mock-seed', type=int, default=0)
    s.add_argument('--force-fallback-every', type=int)
    s.add_argument('--resume', action='store_true')
    s.add_argument('--max-deals', type=int)
    s.add_argument('--game-wall-s', type=float, default=game_kit.GAME_WALL_S)
    s = sub.add_parser('status')
    s.add_argument('--run-dir', required=True)
    s = sub.add_parser('scan-keys')
    s.add_argument('paths', nargs='+')
    return p


def main(argv=None, **inject):
    a = build_parser().parse_args(argv)
    if a.cmd == 'plan':
        return cmd_plan(a)
    if a.cmd == 'run':
        a.call_cap_given = a.call_cap is not None
        if a.call_cap is None:
            a.call_cap = game_kit.CALL_CAP
        return cmd_run(a, **inject)
    if a.cmd == 'status':
        return cmd_status(a)
    return cmd_scan(a)


if __name__ == '__main__':
    sys.exit(main())
