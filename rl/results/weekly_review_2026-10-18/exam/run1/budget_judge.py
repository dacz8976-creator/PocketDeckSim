#!/usr/bin/env python3
"""The judge runs of exam run 1 with a HARD spend bound (Astra's pre-run correction 3). judge.py is frozen and is not edited: this replaces only its
scheduling loop (judge.py lines 1170-1204: one judge_one call per (position, repeat) task, `repeat` and `tag` stamped on the row, one JSON line per row)
and keeps every call, prompt, parser and record field exactly as judge.py makes them (judge.judge_one with the FROZEN settings; test_budget.py checks
that the rows are the same as judge.py's own loop makes).

The bound: before a call is SENT, its worst-case cost is reserved:
    worst case = (UTF-8 bytes of the system + user prompt + OVERHEAD_TOKENS) x input list price + max_tokens x output list price
(a token covers at least one byte of text, so the bytes bound the input tokens; the output can't exceed max_tokens). A call is sent only if both
    accrued + reserved + this call's worst case <= the authorized total   (the ledger file, shared by the primary and the repeat run)
    this run's accrued + reserved + this call's worst case <= the run cap
hold; otherwise it is not sent and its task is reported as not made. When a call returns, its reservation is released and its actual cost
(judge.cost_of on the returned usage) is added. A call that fails (API error, timeout) is charged its full worst case, because whether it was billed is
unknown, and no further call is sent. So accrued + reserved never exceeds the total, whatever the concurrency. Prices are judge.PRICES (the harness's
assumed list price; verify in the console).

usage (from rl/ai_judge of the frozen tag):
  budget_judge.py --positions P --decks D --ids ID... --max-calls N --repeat 1 --workers 4 --tag T --out F --ledger L --total-usd 25 --run-cap-usd 12
                  (--live | --mock)
--mock replaces the API call with a fixed reply (no key read, nothing sent), for dry runs and the tests. Exit 0 = every task made a usable choice;
2 = some task was not made (the bound) or gave no usable choice (the file holds every row that was made); 1 = a usage error or a failed call."""
import argparse, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.getcwd())
import judge  # noqa: E402

OVERHEAD_TOKENS = 2000  # message framing beyond the prompt text: a generous fixed allowance


class BudgetRefused(Exception):
    pass


class Ledger:
    """Under one lock: accrued + reserved <= total and run_accrued + reserved <= run_cap. `accrued` is persisted (atomic replace) so the second
    invocation continues from the first; a lock file refuses two invocations on one ledger at once."""

    def __init__(self, path, total, run_cap=None):
        self.path, self.total, self.lock = path, float(total), threading.Lock()
        self.run_cap = float(run_cap) if run_cap is not None else float(total)
        try:
            os.close(os.open(path + '.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            sys.exit(f'{path}.lock exists: another run holds this ledger (remove the lock only if no run is going)')
        self.accrued = 0.0
        if os.path.exists(path):
            d = json.load(open(path))
            if float(d['total_usd']) != self.total:
                self.close()
                sys.exit(f"the ledger's total is ${d['total_usd']}, not ${self.total}")
            self.accrued = float(d['accrued_usd'])
        self.run_accrued = self.reserved = 0.0
        self.peak = self.accrued
        self.refused = self.calls = self.failed_calls = 0
        self.halted = None
        self._save()

    def reserve(self, w):
        with self.lock:
            if (self.halted or self.accrued + self.reserved + w > self.total + 1e-12
                    or self.run_accrued + self.reserved + w > self.run_cap + 1e-12):
                self.refused += 1
                return False
            self.reserved += w
            self.peak = max(self.peak, self.accrued + self.reserved)
            return True

    def settle(self, w, actual):
        """A returned call: release its reservation, add its actual cost. A cost above the worst case would mean the bound's arithmetic is wrong:
        stop sending (the cost is still counted)."""
        with self.lock:
            self.reserved -= w
            self.accrued += actual
            self.run_accrued += actual
            self.calls += 1
            if actual > w + 1e-9:
                self.halted = f'a call cost ${actual:.5f}, above its reserved worst case ${w:.5f}: no further call is sent'
                print('BOUND CHECK: ' + self.halted, file=sys.stderr)
            self._save()

    def charge_failed(self, w):
        """A call that raised: charge its whole worst case (it may have been billed) and send nothing more."""
        with self.lock:
            self.reserved -= w
            self.accrued += w
            self.run_accrued += w
            self.failed_calls += 1
            self.halted = self.halted or 'a call failed: no further call is sent'
            self._save()

    def _save(self):
        tmp = self.path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump({'accrued_usd': round(self.accrued, 6), 'total_usd': self.total,
                       'note': 'judge calls of exam run 1: actual cost of returned calls + the worst case of failed calls, at judge.PRICES'}, f)
        os.replace(tmp, self.path)

    def close(self):
        try:
            os.remove(self.path + '.lock')
        except FileNotFoundError:
            pass


def worst_case_usd(system, user, model, max_tokens):
    pin, pout = judge.PRICES.get(model, judge.PRICES[judge.MODEL])
    in_ub = len(system.encode('utf-8')) + len(user.encode('utf-8')) + OVERHEAD_TOKENS
    return in_ub * pin / 1e6 + max_tokens * pout / 1e6


def mock_call(system, user, model=judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None, timeout=300):
    usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 900}
    return 'PLAN: 1\nREASON: MOCK reply (no API call was made).', usage, 0.0, model, {'stop_reason': 'end_turn', 'content_types': ['text']}


def install_gate(ledger, real_call):
    """judge.judge_one calls judge.call_claude(system, user, model, max_tokens=..., temperature=...): reserve first, refuse if a bound would be passed."""

    def gated(system, user, model=judge.MODEL, max_tokens=judge.MAX_TOKENS, temperature=None, timeout=300):
        w = worst_case_usd(system, user, model, max_tokens)
        if not ledger.reserve(w):
            raise BudgetRefused(ledger.halted or f'its worst case ${w:.4f} would pass the bound')
        try:
            out = real_call(system, user, model, max_tokens, temperature, timeout)
        except BaseException:
            ledger.charge_failed(w)
            raise
        ledger.settle(w, judge.cost_of(out[3], out[1])['usd'])
        return out

    judge.call_claude = gated


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--positions', required=True)
    p.add_argument('--decks', required=True)
    p.add_argument('--ids', nargs='+', required=True)
    p.add_argument('--max-calls', type=int, required=True)
    p.add_argument('--repeat', type=int, default=1)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--tag', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--ledger', required=True)
    p.add_argument('--total-usd', type=float, required=True)
    p.add_argument('--run-cap-usd', type=float, required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--live', action='store_true')
    mode.add_argument('--mock', action='store_true')
    a = p.parse_args(argv)
    if os.path.exists(a.out):
        sys.exit(f'{a.out} exists: use a fresh --out per run')
    F = judge.FROZEN
    positions = judge.load_positions(a.positions)
    ids = list(a.ids)
    if len(set(ids)) != len(ids) or any(i not in positions for i in ids):
        sys.exit('ids must be known position ids, each once')
    tasks = [(i, k) for i in ids for k in range(a.repeat)]
    if len(tasks) > a.max_calls:
        sys.exit(f'{len(tasks)} calls asked for but --max-calls is {a.max_calls}: raise it on purpose')
    recs = judge.list_plans(ids, a.positions, a.decks, F['plan_world_seed'], None)
    ledger = Ledger(a.ledger, a.total_usd, a.run_cap_usd)
    try:
        if a.mock:
            def no_key():
                raise SystemExit('mock: the key must never be read')
            judge.load_key = no_key
            install_gate(ledger, mock_call)
        else:
            install_gate(ledger, judge.call_claude)
        out_f, lock = open(a.out, 'a', encoding='utf-8'), threading.Lock()

        def one(task):
            i, k = task
            try:
                r, _, _ = judge.judge_one(i, positions, recs, F['order'], True, F['model'], F['temperature'], a.decks, F['compact_above'],
                                          F['max_tokens'], F['prompt_version'], False)
            except BudgetRefused as e:
                print(f'NOT SENT {i} repeat {k}: {e}', file=sys.stderr)
                return None
            r['repeat'] = k
            r['tag'] = a.tag
            with lock:
                out_f.write(json.dumps(r, ensure_ascii=False) + '\n')
                out_f.flush()
                print(f"{r['position']} judge plan {r.get('plan_number')} -> {r['plan']}")
            return r

        with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
            done = list(ex.map(one, tasks))
        out_f.close()
    finally:
        print(f'{ledger.calls} call(s) returned, {ledger.failed_calls} failed; this run ${ledger.run_accrued:.4f} (cap ${ledger.run_cap}); ledger '
              f'${ledger.accrued:.4f} of ${ledger.total} (peak accrued+reserved ${ledger.peak:.4f}); {ledger.refused} refused by the bound '
              f'({judge.PRICE_NOTE})', file=sys.stderr)
        ledger.close()
    skipped = sum(r is None for r in done)
    failed = [r for r in done if r is not None and r['plan_number'] is None]
    if skipped or failed:
        print(f'INCOMPLETE BATCH: {skipped} call(s) not made (the spend bound) and {len(failed)} without a usable choice; the file has every row '
              'that was made', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
