#!/usr/bin/env python3
"""The judge runs with a HARD spend bound (the formal way to run the frozen-7 Gemini judge on Vertex AI; Astra's exam-run-1 design, ported to a provider-aware wrapper).

judge.py's own scheduling loop (`judge.py judge`) is replaced; every call, prompt, parser and record field is exactly what judge.judge_one makes (the FROZEN settings of the
provider). The bound: before a call is SENT, its worst-case cost is reserved:

    worst case = (UTF-8 bytes of the system + user prompt + OVERHEAD_TOKENS) x input price + max_tokens x output price      (a token covers at least one byte of text)

at the RESERVATION price: for Gemini the higher published price ($4 / $20 per 1M tokens, whatever the date), for Anthropic judge.PRICES. A call is sent only if both
    accrued + reserved + this call's worst case <= the authorized total   (the ledger file, shared by the primary and the repeat run)
    this run's accrued + reserved + this call's worst case <= the run cap
hold. A call that does not fit only because other calls are still in flight WAITS for them to settle; one that could never fit is not sent and its task is reported as not made. When a
call returns, its reservation is released and its actual cost (at the price in force on the day: Gemini $2 / $10 through 2026-11-30, $4 / $20 after) is added; a reply without a usage
block is charged its whole worst case. A call that fails (API error, timeout) is charged its full worst case, because whether it was billed is unknown, and no further call is sent.
A call whose cost passes its reservation stops further calls. The calls in flight are written to the ledger file, so a run that is killed is charged for them when the ledger is next
opened. So accrued + reserved never exceeds the total, whatever the concurrency. The run cap is a cap on this invocation: for the primary run set it equal to the total (the repeat run
only gets what the ledger has left); a call reserves about $0.7 at 32,768 output tokens, so workers x 0.7 of the cap is always in flight.

usage:
  budget_judge.py --positions P --decks D --ids ID... --max-calls N --repeat 1 --workers 4 --tag T --out F --ledger L --total-usd 15 --run-cap-usd 15 --vertex-project PROJECT (--live | --mock)
--mock replaces the API call with a fixed reply (no key read, nothing sent), for dry runs and the tests; its rows carry `mock: true` and formal.py refuses them. Exit 0 = every task made
a usable choice; 2 = some task was not made (the bound or an earlier failure), a call failed, or a call gave no usable choice (the file holds every row that was made); 1 = a usage
error. --provider gemini is the frozen-5 Developer API judge (GEMINI_API_KEY, 8,000 tokens); the default, gemini-vertex, reads VERTEX_API_KEY."""
import argparse, json, math, os, sys, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge, providers  # noqa: E402

OVERHEAD_TOKENS = 2000  # message framing beyond the prompt text: a generous fixed allowance


class BudgetRefused(Exception):
    pass


class Ledger:
    """Under one lock: accrued + reserved <= total and run_accrued + reserved <= run_cap. `accrued` and the calls in flight are persisted (atomic replace) so the second invocation
    continues from the first, and a run that was killed with calls out is charged those calls' worst cases when the ledger is next opened; a lock file refuses two invocations on one
    ledger at once; the ledger remembers its provider and model and refuses another. A call that does not fit only because other calls are still in flight WAITS for them; one that could
    never fit is refused."""

    def __init__(self, path, total, run_cap=None, label=None):
        self.cond = threading.Condition()
        self.path, self.total, self.lock, self.label = path, float(total), self.cond, label
        self.run_cap = float(run_cap) if run_cap is not None else float(total)
        if not (math.isfinite(self.total) and self.total > 0 and math.isfinite(self.run_cap) and self.run_cap > 0):  # nan or inf would remove the bound (every comparison false / true)
            sys.exit(f'--total-usd and --run-cap-usd must be finite positive numbers, not {total!r} and {run_cap!r}')
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
            in_flight = float(d.get('in_flight_usd') or 0)
            if in_flight > 0:  # the last run did not finish: its calls in flight may have been billed, so they are charged at their worst case
                self.accrued += in_flight
                print(f'NOTICE: the ledger showed ${in_flight:.4f} of calls in flight from a run that did not finish: charged as spent', file=sys.stderr)
        self.run_accrued = self.reserved = 0.0
        self.peak = self.accrued
        self.refused = self.calls = self.failed_calls = 0
        self.halted = None
        if not self._save():
            self.close()
            sys.exit(f'the ledger file {path} cannot be written')

    def reserve(self, w, block=True):
        """True: `w` is reserved and the call may be sent. False: it can never fit (halted, or the total or the run cap would be passed even with nothing in flight), or, with
        block=False, it does not fit right now. With block=True a call that fits once the calls in flight have settled waits for them; with nothing in flight it never waits."""
        with self.cond:
            while True:
                if (self.halted or self.accrued + w > self.total + 1e-12 or self.run_accrued + w > self.run_cap + 1e-12):
                    self.refused += 1
                    return False
                if self.accrued + self.reserved + w <= self.total + 1e-12 and self.run_accrued + self.reserved + w <= self.run_cap + 1e-12:
                    self.reserved += w
                    self.peak = max(self.peak, self.accrued + self.reserved)
                    if not self._save():  # the file cannot be written: the call is not sent, the reservation is given back and the run stops (halted)
                        self.reserved -= w
                        self.refused += 1
                        self.cond.notify_all()
                        return False
                    return True
                if not block or self.reserved <= 1e-9:  # nothing in flight to wait for: it will never fit (this also stops a nan from waiting for ever)
                    self.refused += 1
                    return False
                self.cond.wait()  # calls are in flight: it fits once they settle (each settles or is charged, and either wakes every waiter)

    def settle(self, w, actual):
        """A returned call: release its reservation, add its actual cost. A cost above the worst case would mean the bound's arithmetic is wrong: stop sending (the cost is
        still counted)."""
        with self.cond:
            try:
                self.reserved -= w
                self.accrued += actual
                self.run_accrued += actual
                self.calls += 1
                if actual > w + 1e-9:
                    self.halted = f'a call cost ${actual:.5f}, above its reserved worst case ${w:.5f}: no further call is sent'
                    print('BOUND CHECK: ' + self.halted, file=sys.stderr)
                self._save()
            finally:
                self.cond.notify_all()  # whatever happened above, a waiter must re-check

    def charge_failed(self, w):
        """A call that raised: charge its whole worst case (it may have been billed) and send nothing more."""
        with self.cond:
            try:
                self.reserved -= w
                self.accrued += w
                self.run_accrued += w
                self.failed_calls += 1
                self.halted = self.halted or 'a call failed: no further call is sent'
                self._save()
            finally:
                self.cond.notify_all()

    def _save(self):
        """Writes the ledger file (atomic replace). True when written. A failed write (disk full, a locked file) does not raise: it halts the run (no further call is sent, and the
        calls out are still settled in memory) and returns False, so that nothing waits for ever on a state change that did not get its wake-up."""
        tmp = self.path + '.tmp'
        try:
            with open(tmp, 'w') as f:
                json.dump({'accrued_usd': round(self.accrued, 6), 'in_flight_usd': round(max(self.reserved, 0.0), 6), 'total_usd': self.total, 'label': self.label,
                           'note': 'judge calls: actual cost of returned calls (at the price in force) + the worst case of failed calls and of replies without usage; in_flight_usd = calls out '
                                   'right now (charged at their worst case if the run is killed)'}, f)
            os.replace(tmp, self.path)
            return True
        except OSError as e:
            if not self.halted or 'cannot be written' not in self.halted:
                print(f'LEDGER: the file {self.path} cannot be written ({type(e).__name__}): no further call is sent', file=sys.stderr)
            self.halted = self.halted or f'the ledger file cannot be written ({type(e).__name__}): no further call is sent'
            return False

    def close(self):
        try:
            os.remove(self.path + '.lock')
        except FileNotFoundError:
            pass


def reservation_price(provider, model):
    """(input, output) USD per 1M tokens a call's worst case is reserved at."""
    if provider in providers.GEMINI_PROVIDERS:
        return providers.gemini_reserve_price()
    return judge.PRICES.get(model, judge.PRICES[judge.MODEL])


def worst_case_usd(system, user, provider, model, max_tokens):
    pin, pout = reservation_price(provider, model)
    in_ub = len(system.encode('utf-8')) + len(user.encode('utf-8')) + OVERHEAD_TOKENS
    return in_ub * pin / 1e6 + max_tokens * pout / 1e6


def actual_usd(provider, out, worst):
    """The cost to settle a returned call: the price in force on its usage; a Gemini reply without usage is charged its whole worst case."""
    text, usage, secs, model_used, extra = out
    if provider in providers.GEMINI_PROVIDERS:
        if extra.get('usage_missing') or usage.get('input_tokens') is None:
            return worst
        pin, pout = providers.gemini_price()
        return usage['input_tokens'] * pin / 1e6 + usage.get('output_tokens', 0) * pout / 1e6
    return judge.cost_of(model_used, usage)['usd']


def mock_call(provider):
    """A fixed reply in the shape of the provider's call (no key, no network)."""
    def call(system, user, model=None, max_tokens=judge.MAX_TOKENS, temperature=None, thinking=None, timeout=300):
        if provider in providers.GEMINI_PROVIDERS:
            usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 900, 'thought_tokens': 700, 'answer_tokens': 200, 'cached_tokens': 0}
            extra = ({'stop_reason': 'end_turn', 'content_types': ['text'], 'finish_reason': 'STOP', 'usage_missing': False, 'n_candidates': 1} if provider == 'gemini-vertex'
                     else {'stop_reason': 'end_turn', 'content_types': ['model_output'], 'status': 'completed', 'usage_missing': False})
            return 'PLAN: 1\nREASON: MOCK reply (no API call was made).', usage, 0.0, model, extra
        usage = {'input_tokens': (len(system) + len(user)) // 3, 'output_tokens': 900}
        return 'PLAN: 1\nREASON: MOCK reply (no API call was made).', usage, 0.0, model, {'stop_reason': 'end_turn', 'content_types': ['text']}
    return call


def install_gate(ledger, real_call, provider):
    """judge.judge_one calls providers.call_vertex / call_gemini (or judge.call_claude): reserve first (waiting for calls in flight when it only fits after they settle, refusing when it
    can never fit), settle or charge afterwards. judge_one always passes max_tokens; the default is the provider's frozen cap, never a smaller one."""
    default_max_tokens = judge.judge_settings(provider)['max_tokens']

    def gated(system, user, model=None, max_tokens=default_max_tokens, temperature=None, *rest, **kw):
        w = worst_case_usd(system, user, provider, model, max_tokens)
        if not ledger.reserve(w):
            raise BudgetRefused(ledger.halted or f'its worst case ${w:.4f} would pass the bound')
        try:
            out = real_call(system, user, model, max_tokens, temperature, *rest, **kw)
            actual = actual_usd(provider, out, w)  # inside the try: a reply the costing cannot read (an absurd count) is charged at its worst case, never left reserved
        except BaseException:
            ledger.charge_failed(w)
            raise
        ledger.settle(w, actual)
        return out

    if provider == 'gemini':
        providers.call_gemini = gated
    elif provider == 'gemini-vertex':
        providers.call_vertex = gated
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
    p.add_argument('--provider', choices=['gemini-vertex', 'gemini', 'anthropic'], default='gemini-vertex', help='the judge of the current freeze (frozen-7) is gemini-vertex')
    p.add_argument('--vertex-project', help='gemini-vertex: the Google Cloud project id or number the key bills to (default: the VERTEX_PROJECT environment variable; not a secret)')
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
    if a.vertex_project is not None:
        if a.provider != 'gemini-vertex':
            sys.exit('--vertex-project is a gemini-vertex setting')
        providers.set_vertex_project(a.vertex_project)
    if a.live:  # a missing key (or, for Vertex, project) stops the run HERE (the message names the variable, never a value), before any ledger or reservation exists
        if a.provider == 'gemini-vertex':
            providers.load_key(providers.VERTEX_KEY_VAR)
            providers.vertex_project()
        else:
            (providers.load_key if a.provider == 'gemini' else judge.load_key)()
    ledger = Ledger(a.ledger, a.total_usd, a.run_cap_usd, label=f"{a.provider}:{S['model']}")
    done = []
    out_f = None
    try:
        if a.mock:
            def no_key(*_a, **_k):
                raise SystemExit('mock: the key must never be read')
            judge.load_key = no_key
            providers.load_key = no_key
            install_gate(ledger, mock_call(a.provider), a.provider)
        else:
            install_gate(ledger, {'gemini-vertex': providers.call_vertex, 'gemini': providers.call_gemini, 'anthropic': judge.call_claude}[a.provider], a.provider)
        out_f, lock = open(a.out, 'a', encoding='utf-8'), threading.Lock()

        def one(task):
            i, k = task
            try:
                r, _, _ = judge.judge_one(i, positions, recs, F['order'], True, S['model'], S['temperature'], a.decks, F['compact_above'], S['max_tokens'], F['prompt_version'], False,
                                          a.provider, S.get('thinking_level'))
            except BudgetRefused as e:
                print(f'NOT SENT {i} repeat {k}: {e}', file=sys.stderr)
                return None
            except SystemExit as e:  # a call that failed (the gate has charged it at its worst case and halted the run; the message is already scrubbed of the key) or a refusal of judge_one itself (a capped plan list: nothing was sent, nothing charged)
                print(f'TASK FAILED {i} repeat {k}: {e.code}', file=sys.stderr)
                return {'failed': True, 'position': i, 'plan_number': None}
            except Exception as e:  # anything else out of a call or of the row's making (the gate has already charged a failed call); only the type is shown
                print(f'TASK FAILED {i} repeat {k}: {type(e).__name__}', file=sys.stderr)
                return {'failed': True, 'position': i, 'plan_number': None}
            r['repeat'] = k
            r['tag'] = a.tag
            if a.mock:
                r['mock'] = True  # a mock row is never a result: formal.py refuses it
            with lock:
                out_f.write(json.dumps(r, ensure_ascii=False) + '\n')
                out_f.flush()
                print(f"{r['position']} judge plan {r.get('plan_number')} -> {r['plan']}")
            return r

        with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
            done = list(ex.map(one, tasks))
    finally:
        if out_f is not None:
            out_f.close()
        note = judge.provider_price_note(a.provider)
        print(f'{ledger.calls} call(s) returned, {ledger.failed_calls} failed; this run ${ledger.run_accrued:.4f} (cap ${ledger.run_cap}); ledger '
              f'${ledger.accrued:.4f} of ${ledger.total} (peak accrued+reserved ${ledger.peak:.4f}); {ledger.refused} refused by the bound ({note})', file=sys.stderr)
        ledger.close()
    skipped = sum(r is None for r in done)
    crashed = [r for r in done if r is not None and r.get('failed')]
    failed = [r for r in done if r is not None and not r.get('failed') and r['plan_number'] is None]
    if skipped or crashed or failed:
        print(f'INCOMPLETE BATCH: {skipped} call(s) not made (the spend bound or an earlier failure), {len(crashed)} task(s) failed or refused and {len(failed)} without a usable choice; '
              'the file has every row that was made', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
