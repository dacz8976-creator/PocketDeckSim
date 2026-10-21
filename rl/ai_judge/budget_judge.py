#!/usr/bin/env python3
"""The judge runs with a HARD spend bound (the formal way to run the frozen-5 Gemini judge; Astra's exam-run-1 design, ported to a provider-aware wrapper).

judge.py's own scheduling loop (`judge.py judge`) is replaced; every call, prompt, parser and record field is exactly what judge.judge_one makes (the FROZEN settings of the
provider). The bound: before a call is SENT, its worst-case cost is reserved:

    worst case = (UTF-8 bytes of the system + user prompt + OVERHEAD_TOKENS) x input price + max_tokens x output price      (a token covers at least one byte of text)

at the RESERVATION price: for Gemini the higher published price ($4 / $20 per 1M tokens, whatever the date), for Anthropic judge.PRICES. A call is sent only if both
    accrued + reserved + this call's worst case <= the authorized total   (the ledger file, shared by the primary and the repeat run)
    this run's accrued + reserved + this call's worst case <= the run cap
hold; otherwise it is not sent and its task is reported as not made. When a call returns, its reservation is released and its actual cost (at the price in force on the day:
Gemini $2 / $10 through 2026-11-30, $4 / $20 after) is added; a reply without a usage block is charged its whole worst case. A call that fails (API error, timeout) is charged
its full worst case, because whether it was billed is unknown, and no further call is sent. A call whose cost passes its reservation stops further calls. So accrued +
reserved never exceeds the total, whatever the concurrency.

usage:
  budget_judge.py --positions P --decks D --ids ID... --max-calls N --repeat 1 --workers 4 --tag T --out F --ledger L --total-usd 15 --run-cap-usd 8 (--live | --mock) [--provider gemini]
--mock replaces the API call with a fixed reply (no key read, nothing sent), for dry runs and the tests. Exit 0 = every task made a usable choice; 2 = some task was not made
(the bound) or gave no usable choice (the file holds every row that was made); 1 = a usage error."""
import argparse, json, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge, providers  # noqa: E402

OVERHEAD_TOKENS = 2000  # message framing beyond the prompt text: a generous fixed allowance


class BudgetRefused(Exception):
    pass


class Ledger:
    """Under one lock: accrued + reserved <= total and run_accrued + reserved <= run_cap. `accrued` is persisted (atomic replace) so the second invocation continues from the
    first; a lock file refuses two invocations on one ledger at once; the ledger remembers its provider and model and refuses another."""

    def __init__(self, path, total, run_cap=None, label=None):
        self.path, self.total, self.lock, self.label = path, float(total), threading.Lock(), label
        self.run_cap = float(run_cap) if run_cap is not None else float(total)
        try:
            os.close(os.open(path + '.lock', os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            sys.exit(f'{path}.lock exists: another run holds this ledger (remove the lock only if no run is going)')
        self.accrued = 0.0
        if os.path.exists(path):
            with open(path) as f:
                d = json.load(f)
            if float(d['total_usd']) != self.total:
                self.close()
                sys.exit(f"the ledger's total is ${d['total_usd']}, not ${self.total}")
            if label is not None and d.get('label') not in (None, label):
                self.close()
                sys.exit(f"the ledger was opened for {d.get('label')!r}, not {label!r}")
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
        """A returned call: release its reservation, add its actual cost. A cost above the worst case would mean the bound's arithmetic is wrong: stop sending (the cost is
        still counted)."""
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
            json.dump({'accrued_usd': round(self.accrued, 6), 'total_usd': self.total, 'label': self.label,
                       'note': 'judge calls: actual cost of returned calls (at the price in force) + the worst case of failed calls and of replies without usage'}, f)
        os.replace(tmp, self.path)

    def close(self):
        try:
            os.remove(self.path + '.lock')
        except FileNotFoundError:
            pass


def reservation_price(provider, model):
    """(input, output) USD per 1M tokens a call's worst case is reserved at."""
    if provider == 'gemini':
        return providers.gemini_reserve_price()
    return judge.PRICES.get(model, judge.PRICES[judge.MODEL])


def worst_case_usd(system, user, provider, model, max_tokens):
    pin, pout = reservation_price(provider, model)
    in_ub = len(system.encode('utf-8')) + len(user.encode('utf-8')) + OVERHEAD_TOKENS
    return in_ub * pin / 1e6 + max_tokens * pout / 1e6


def actual_usd(provider, out, worst):
    """The cost to settle a returned call: the price in force on its usage; a Gemini reply without usage is charged its whole worst case."""
    text, usage, secs, model_used, extra = out
    if provider == 'gemini':
        if extra.get('usage_missing') or usage.get('input_tokens') is None:
            return worst
        pin, pout = providers.gemini_price()
        return usage['input_tokens'] * pin / 1e6 + usage.get('output_tokens', 0) * pout / 1e6
    return judge.cost_of(model_used, usage)['usd']


def mock_call(provider):
    """A fixed reply in the shape of the provider's call (no key, no network)."""
    def call(system, user, model=None, max_tokens=judge.MAX_TOKENS, temperature=None, thinking=None, timeout=300):
        if provider == 'gemini':
            usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 900, 'thought_tokens': 700, 'answer_tokens': 200, 'cached_tokens': 0}
            return ('PLAN: 1\nREASON: MOCK reply (no API call was made).', usage, 0.0, model,
                    {'stop_reason': 'end_turn', 'content_types': ['model_output'], 'status': 'completed', 'usage_missing': False})
        usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 900}
        return 'PLAN: 1\nREASON: MOCK reply (no API call was made).', usage, 0.0, model, {'stop_reason': 'end_turn', 'content_types': ['text']}
    return call


def install_gate(ledger, real_call, provider):
    """judge.judge_one calls providers.call_gemini (or judge.call_claude): reserve first, refuse if a bound would be passed, settle or charge afterwards."""

    def gated(system, user, model=None, max_tokens=judge.MAX_TOKENS, temperature=None, *rest, **kw):
        w = worst_case_usd(system, user, provider, model, max_tokens)
        if not ledger.reserve(w):
            raise BudgetRefused(ledger.halted or f'its worst case ${w:.4f} would pass the bound')
        try:
            out = real_call(system, user, model, max_tokens, temperature, *rest, **kw)
        except BaseException:
            ledger.charge_failed(w)
            raise
        ledger.settle(w, actual_usd(provider, out, w))
        return out

    if provider == 'gemini':
        providers.call_gemini = gated
    else:
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
    p.add_argument('--provider', choices=['gemini', 'anthropic'], default='gemini')
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--live', action='store_true')
    mode.add_argument('--mock', action='store_true')
    a = p.parse_args(argv)
    if os.path.exists(a.out):
        sys.exit(f'{a.out} exists: use a fresh --out per run')
    F = judge.FROZEN
    S = judge.judge_settings(a.provider)  # the frozen judge settings of the provider
    positions = judge.load_positions(a.positions)
    ids = list(a.ids)
    if len(set(ids)) != len(ids) or any(i not in positions for i in ids):
        sys.exit('ids must be known position ids, each once')
    tasks = [(i, k) for i in ids for k in range(a.repeat)]
    if len(tasks) > a.max_calls:
        sys.exit(f'{len(tasks)} calls asked for but --max-calls is {a.max_calls}: raise it on purpose')
    recs = judge.list_plans(ids, a.positions, a.decks, F['plan_world_seed'], None)
    if a.live:  # a missing key stops the run HERE (the message names the variable, never a value), before any ledger or reservation exists
        (providers.load_key if a.provider == 'gemini' else judge.load_key)()
    ledger = Ledger(a.ledger, a.total_usd, a.run_cap_usd, label=f"{a.provider}:{S['model']}")
    done = []
    try:
        if a.mock:
            def no_key(*_a, **_k):
                raise SystemExit('mock: the key must never be read')
            judge.load_key = no_key
            providers.load_key = no_key
            install_gate(ledger, mock_call(a.provider), a.provider)
        else:
            install_gate(ledger, providers.call_gemini if a.provider == 'gemini' else judge.call_claude, a.provider)
        out_f, lock = open(a.out, 'a', encoding='utf-8'), threading.Lock()

        def one(task):
            i, k = task
            try:
                r, _, _ = judge.judge_one(i, positions, recs, F['order'], True, S['model'], S['temperature'], a.decks, F['compact_above'], S['max_tokens'], F['prompt_version'], False,
                                          a.provider, S.get('thinking_level'))
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
        note = providers.GEMINI_PRICE_NOTE if a.provider == 'gemini' else judge.PRICE_NOTE
        print(f'{ledger.calls} call(s) returned, {ledger.failed_calls} failed; this run ${ledger.run_accrued:.4f} (cap ${ledger.run_cap}); ledger '
              f'${ledger.accrued:.4f} of ${ledger.total} (peak accrued+reserved ${ledger.peak:.4f}); {ledger.refused} refused by the bound ({note})', file=sys.stderr)
        ledger.close()
    skipped = sum(r is None for r in done)
    failed = [r for r in done if r is not None and r['plan_number'] is None]
    if skipped or failed:
        print(f'INCOMPLETE BATCH: {skipped} call(s) not made (the spend bound) and {len(failed)} without a usable choice; the file has every row that was made', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
