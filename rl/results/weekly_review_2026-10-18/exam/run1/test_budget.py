#!/usr/bin/env python3
"""Tests of budget_judge.py's spend bound, with mocks only: no key is read and no API call is made. Run from rl/ai_judge of the judge tag:
    cd <clone>/rl/ai_judge && python3 <run1>/test_budget.py
Old fixtures only (tests/fixtures/mini_positions.json), never the exam."""
import json, os, random, subprocess, sys, tempfile, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.getcwd())
import judge  # noqa: E402
import budget_judge as bj  # noqa: E402

FIX = os.path.join(os.getcwd(), 'tests', 'fixtures')
MINI, DECKS = os.path.join(FIX, 'mini_positions.json'), os.path.join(FIX, 'decks')
REAL_CALL = judge.call_claude
results = []


def check(name, cond, detail=''):
    results.append((name, bool(cond)))
    print(f"{'PASS' if cond else 'FAIL'} {name}{': ' + detail if detail else ''}")


def tmpledger():
    return os.path.join(tempfile.mkdtemp(prefix='budget_test_'), 'ledger.json')


def test_ledger_stress():
    """32 threads reserve random worst cases and settle random actual costs; an independent sampler watches accrued + reserved under the lock."""
    L = bj.Ledger(tmpledger(), total=1.0, run_cap=1.0)
    worst, stop = [0.0], threading.Event()

    def sampler():
        while not stop.is_set():
            with L.lock:
                worst[0] = max(worst[0], L.accrued + L.reserved)
            time.sleep(0)

    def worker(seed):
        rnd = random.Random(seed)
        for _ in range(300):
            w = rnd.uniform(0.005, 0.15)
            if L.reserve(w):
                time.sleep(rnd.uniform(0, 0.002))
                L.settle(w, rnd.uniform(0, w))
    s = threading.Thread(target=sampler)
    s.start()
    ts = [threading.Thread(target=worker, args=(i,)) for i in range(32)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    stop.set()
    s.join()
    L.close()
    check('stress: accrued + reserved never above the total (sampled)', worst[0] <= 1.0 + 1e-9, f'max seen ${worst[0]:.4f}')
    check('stress: peak at each reservation never above the total', L.peak <= 1.0 + 1e-9, f'peak ${L.peak:.4f}')
    check('stress: final accrued within the total, nothing left reserved', L.accrued <= 1.0 + 1e-9 and abs(L.reserved) < 1e-9,
          f'accrued ${L.accrued:.4f}, {L.calls} calls, {L.refused} refused')
    check('stress: the bound was actually exercised (refusals happened)', L.refused > 0)


def test_gate_adversarial():
    """Every call costs exactly its worst case (input tokens = bytes + overhead, output = max_tokens), 4 calls in flight at once."""
    L = bj.Ledger(tmpledger(), total=2.0, run_cap=2.0)

    def worst_call(system, user, model, max_tokens, temperature, timeout):
        time.sleep(0.01)
        n_in = len(system.encode('utf-8')) + len(user.encode('utf-8')) + bj.OVERHEAD_TOKENS
        return 'PLAN: 1', {'input_tokens': n_in, 'output_tokens': max_tokens}, 0.01, model, {'stop_reason': 'end_turn'}
    bj.install_gate(L, worst_call)
    system, user = 'S' * 5000, 'U' * 40000
    sent = refused = 0
    lock = threading.Lock()

    def worker():
        nonlocal sent, refused
        for _ in range(10):
            try:
                judge.call_claude(system, user, judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None)
                with lock:
                    sent += 1
            except bj.BudgetRefused:
                with lock:
                    refused += 1
    ts = [threading.Thread(target=worker) for _ in range(4)]
    [t.start() for t in ts]
    [t.join() for t in ts]
    judge.call_claude = REAL_CALL
    L.close()
    w = bj.worst_case_usd(system, user, judge.MODEL, judge.MAX_TOKENS)
    check('worst-case calls: total spend within the bound', L.accrued <= 2.0 + 1e-9, f'${L.accrued:.4f} for {sent} calls of ${w:.4f}; {refused} refused')
    check('worst-case calls: as many calls as fit were sent, no more', sent == int(2.0 // w) and not L.halted, f'{sent} sent, {int(2.0 // w)} fit')


def test_failed_call():
    L = bj.Ledger(tmpledger(), total=5.0, run_cap=5.0)

    def boom(*a):
        raise RuntimeError('simulated timeout')
    bj.install_gate(L, boom)
    try:
        judge.call_claude('s', 'u', judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None)
        raised = False
    except RuntimeError:
        raised = True
    w = bj.worst_case_usd('s', 'u', judge.MODEL, judge.MAX_TOKENS)
    try:
        judge.call_claude('s', 'u', judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None)
        refused = False
    except bj.BudgetRefused:
        refused = True
    judge.call_claude = REAL_CALL
    L.close()
    check('failed call: the error is passed on', raised)
    check('failed call: charged its whole worst case', abs(L.accrued - w) < 1e-9, f'${L.accrued:.5f} vs worst ${w:.5f}')
    check('failed call: no further call is sent', refused and L.halted)


def test_ledger_persists_and_locks():
    path = tmpledger()
    L1 = bj.Ledger(path, total=1.0, run_cap=0.6)
    ok1 = L1.reserve(0.5)
    L1.settle(0.5, 0.5)
    over_run_cap = not L1.reserve(0.2)  # 0.5 + 0.2 > the run cap 0.6, though within the total
    try:
        bj.Ledger(path, total=1.0, run_cap=0.6)
        second_refused = False
    except SystemExit:
        second_refused = True
    L1.close()
    L2 = bj.Ledger(path, total=1.0, run_cap=0.6)
    carried = abs(L2.accrued - 0.5) < 1e-9
    fits = L2.reserve(0.45)
    over_total = not L2.reserve(0.1)  # 0.5 accrued + 0.45 reserved + 0.1 > 1.0
    L2.close()
    try:
        bj.Ledger(path, total=30.0)
        total_changed_refused = False
    except SystemExit:
        total_changed_refused = True
    check('run cap: a reservation past the run cap is refused', ok1 and over_run_cap)
    check('ledger: a second run on the same ledger at once is refused', second_refused)
    check('ledger: the next run continues from the accrued total', carried and fits and over_total)
    check('ledger: a different total on an existing ledger is refused', total_changed_refused)


def run_cmd(args, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k != 'ANTHROPIC_API_KEY'}
    env.update(env_extra or {})
    return subprocess.run(args, capture_output=True, text=True, env=env, cwd=os.getcwd())


def rows(path):
    return sorted((json.loads(l) for l in open(path, encoding='utf-8')), key=lambda r: (r['position'], r['repeat']))


def test_orchestrator_mock():
    ids = [p['id'] for p in json.load(open(MINI, encoding='utf-8'))]
    d = tempfile.mkdtemp(prefix='budget_orch_')
    base = [sys.executable, os.path.join(HERE, 'budget_judge.py'), '--positions', MINI, '--decks', DECKS, '--ids', *ids, '--max-calls', str(2 * len(ids)),
            '--repeat', '2', '--workers', '4', '--mock']
    # (a) a full mocked run
    a = run_cmd(base + ['--tag', 'T', '--out', f'{d}/a.jsonl', '--ledger', f'{d}/a_ledger.json', '--total-usd', '25', '--run-cap-usd', '12'])
    ra = rows(f'{d}/a.jsonl') if os.path.exists(f'{d}/a.jsonl') else []
    led = json.load(open(f'{d}/a_ledger.json'))
    check('mock run: exit 0 and one row per task', a.returncode == 0 and len(ra) == 2 * len(ids), f'exit {a.returncode}, {len(ra)} rows; {a.stderr.strip()[-300:]}')
    check('mock run: every row is frozen, tagged, with its repeat', all(r['frozen'] and r['tag'] == 'T' for r in ra)
          and sorted(r['repeat'] for r in ra) == sorted([0, 1] * len(ids)))
    check('mock run: ledger = the rows\' summed cost', abs(led['accrued_usd'] - sum(r['cost']['usd'] for r in ra)) < 1e-4,
          f"ledger ${led['accrued_usd']}, rows ${sum(r['cost']['usd'] for r in ra):.5f}")
    check('mock run: the lock is released', not os.path.exists(f'{d}/a_ledger.json.lock'))
    # (b) judge.py's own frozen loop with the same mock: the rows must be the same
    code = ('import sys; sys.path.insert(0, %r); import judge, budget_judge as bj; judge.call_claude = bj.mock_call; '
            'judge.load_key = lambda: (_ for _ in ()).throw(SystemExit("key read")); sys.exit(judge.main(sys.argv[1:]))') % HERE
    b = run_cmd([sys.executable, '-c', code, 'run', '--bot', 'judge', '--positions', MINI, '--decks', DECKS, '--ids', *ids, '--live', '--max-calls',
                 str(2 * len(ids)), '--repeat', '2', '--workers', '4', '--tag', 'T', '--out', f'{d}/b.jsonl'])
    rb = rows(f'{d}/b.jsonl') if os.path.exists(f'{d}/b.jsonl') else []
    same = len(ra) == len(rb) and all(x == y for x, y in zip(ra, rb))
    diff = '' if same else str([(k, x.get(k), y.get(k)) for x, y in zip(ra, rb) for k in set(x) | set(y) if x.get(k) != y.get(k)][:4])
    check("parity: the same rows as judge.py's own loop (every field)", b.returncode == 0 and same, f'judge.py exit {b.returncode}; {diff}')
    # (c) a total that fits only a few calls: exit 2, the rest not sent, the spend within the total
    # room for the largest call's worst case plus 30% of what the 12 mock calls really cost: the first call fits, all 12 can't
    w = max(r['cost']['usd'] for r in ra)
    max_in = max(r['cost']['input_tokens'] for r in ra)  # the mock bills (characters // 3) input tokens
    max_w = (3 * max_in + 3) * 1.2 * 3.0 / 1e6 + bj.OVERHEAD_TOKENS * 3.0 / 1e6 + judge.MAX_TOKENS * 15.0 / 1e6
    tight = round(max_w + 0.3 * sum(r['cost']['usd'] for r in ra), 4)
    c = run_cmd(base + ['--tag', 'T', '--out', f'{d}/c.jsonl', '--ledger', f'{d}/c_ledger.json', '--total-usd', str(tight), '--run-cap-usd', str(tight)])
    rc_ = rows(f'{d}/c.jsonl') if os.path.exists(f'{d}/c.jsonl') else []
    ledc = json.load(open(f'{d}/c_ledger.json'))
    check('tight total: exit 2, some calls not sent', c.returncode == 2 and 0 < len(rc_) < 2 * len(ids) and 'NOT SENT' in c.stderr,
          f'exit {c.returncode}, {len(rc_)} rows of {2 * len(ids)}, total ${tight}')
    check('tight total: spend within the total', ledc['accrued_usd'] <= tight + 1e-9, f"${ledc['accrued_usd']} of ${tight} (largest mock call ${w})")
    # (d) a second invocation on ledger (a) continues from its accrued amount
    e = run_cmd(base + ['--tag', 'T2', '--out', f'{d}/e.jsonl', '--ledger', f'{d}/a_ledger.json', '--total-usd', '25', '--run-cap-usd', '12'])
    lede = json.load(open(f'{d}/a_ledger.json'))
    check('shared ledger: the second run adds to the first', e.returncode == 0 and abs(lede['accrued_usd'] - 2 * led['accrued_usd']) < 1e-4,
          f"${led['accrued_usd']} -> ${lede['accrued_usd']}")


if __name__ == '__main__':
    test_ledger_stress()
    test_gate_adversarial()
    test_failed_call()
    test_ledger_persists_and_locks()
    test_orchestrator_mock()
    bad = [n for n, ok in results if not ok]
    print(f'{len(results) - len(bad)}/{len(results)} passed' + (f'; FAILED: {bad}' if bad else ''))
    sys.exit(1 if bad else 0)
