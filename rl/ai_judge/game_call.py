"""One judge decision with the frozen-8 retry rule. The retries live here, outside providers.py (frozen-7's judge block stays valid)."""
import http.client
import io
import json
import os
import random
import re
import sys
import time
import urllib.error
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import budget_judge  # noqa: E402
import game_kit  # noqa: E402
import judge  # noqa: E402
import providers  # noqa: E402

KEY_PATTERNS = (r'AIza[0-9A-Za-z_\-]{20,}', r'AQ\.[0-9A-Za-z_\-]{20,}')
_ORIG_CALL = providers.call_vertex
MOCK_MODEL = 'gemini-4-argon-mock'


class LedgerStop(Exception):
    pass


class LedgerBound(LedgerStop):
    """A BOUND CHECK halt: a try cost more than its reserved worst case. It keeps the tries, as CallFailed does."""
    def __init__(self, tries, detail):
        super().__init__(detail)
        self.tries, self.detail = tries, detail


class CallFailed(Exception):
    def __init__(self, tries, detail):
        super().__init__(detail)
        self.tries, self.detail = tries, detail


class CallNotSent(Exception):
    pass


class LiveSetupError(Exception):
    pass


class GameLedger(budget_judge.Ledger):
    def charge_try_failed(self, w, usd):
        """A failed try: release its reservation and charge `usd`. Unlike charge_failed it does not halt (unless usd passes the reserved worst case, as settle does)."""
        with self.cond:
            try:
                self.reserved -= w
                self.accrued += usd
                self.run_accrued += usd
                self.failed_calls += 1
                if usd > w + 1e-9:
                    self.halted = f'a try cost ${usd:.5f}, above its reserved worst case ${w:.5f}: no further call is sent'
                    print('BOUND CHECK: ' + self.halted, file=sys.stderr)
                self._save()
            finally:
                self.cond.notify_all()


def _clean(text):
    text = str(text)
    for pat in KEY_PATTERNS:
        text = re.sub(pat, '[redacted]', text)
    return text[:300]


def open_ledger(path, total):
    try:
        return GameLedger(path, total, label=game_kit.LEDGER_LABEL)
    except SystemExit as e:
        raise LedgerStop(_clean(e))


# ------------------------------------------------------------------------------------------------ recording what was sent
class Recorder:
    def __init__(self):
        self.clear()

    def clear(self):
        self.called, self.body, self.exc = False, None, None


_REC = [None]


def install_recorder():
    """Wrap whatever providers._post_json is now. Idempotent on an already wrapped function."""
    cur = providers._post_json
    if getattr(cur, '_recorder', None) is not None:
        _REC[0] = cur._recorder
        return cur._recorder
    rec = Recorder()

    def wrapped(url, headers, body, timeout):
        rec.called = True
        try:
            out = cur(url, headers, body, timeout)
        except urllib.error.HTTPError as exc:
            try:
                b = exc.read()
            except Exception:
                b = b''
            rec.exc, rec.body = exc, b
            raise urllib.error.HTTPError(exc.url, exc.code, exc.msg, exc.hdrs, io.BytesIO(b))
        except BaseException as exc:
            rec.exc = exc
            raise
        rec.body = out
        return out
    wrapped._recorder = rec
    providers._post_json = wrapped
    _REC[0] = rec
    return rec


def classify(rec):
    if not rec.called:
        return 'not_sent'
    e = rec.exc
    if e is None:
        return 'error:bad_body'
    if isinstance(e, urllib.error.HTTPError):
        return f'http_{e.code}'
    if isinstance(e, (urllib.error.URLError, OSError, http.client.HTTPException)):
        return f'transport:{type(e).__name__}'
    return f'error:{type(e).__name__}'


def _usage_of_record(rec, w, model):
    """(usd, seen): the charge of the recorded body's usageMetadata, or (None, False)."""
    body = rec.body
    try:
        if isinstance(body, (bytes, bytearray)):
            body = json.loads(body.decode('utf-8', 'replace'))
        if not isinstance(body, dict) or not isinstance(body.get('usageMetadata'), dict):
            return None, False
        text, usage, model_used, extra = providers.parse_generate_content(body, model)
        if extra.get('usage_missing'):
            return None, False
        return budget_judge.actual_usd('gemini-vertex', (text, usage, 0.0, model_used, extra), w), True
    except Exception:
        return None, False


class GatedVertex:
    def __init__(self, ledger_path, ledger_total, deadline, clock=time.monotonic, sleep=time.sleep):
        self.ledger_path, self.ledger_total, self.deadline, self.clock, self.sleep = ledger_path, ledger_total, deadline, clock, sleep
        self.tries, self.waits = [], []

    def __call__(self, system, user, model='gemini-4-argon', max_tokens=32768, temperature=None, thinking=None, timeout=game_kit.VERTEX_TIMEOUT_S):
        rec = _REC[0]
        if rec is None:
            raise RuntimeError('install_recorder() was not called')
        w = budget_judge.worst_case_usd(system, user, 'gemini-vertex', 'gemini-4-argon', 32768)
        self.tries, self.waits = [], []
        t_first = None
        detail = 'no_time'
        for t in range(1, game_kit.MAX_TRIES + 1):
            if t > 1:
                wait = game_kit.RETRY_WAITS_S[t - 2]
                if self.clock() - t_first + wait > game_kit.RETRY_WINDOW_S:
                    detail = self.tries[-1]['outcome']
                    break
                self.waits.append(wait)
                self.sleep(wait)
                if self.clock() - t_first > game_kit.RETRY_WINDOW_S:
                    detail = self.tries[-1]['outcome']
                    break
            if self.deadline - self.clock() < game_kit.VERTEX_TIMEOUT_S + game_kit.SHADOW_RESERVE_S:
                detail = 'no_time'
                break
            t_start = self.clock()
            if t_first is None:
                t_first = t_start
            led = open_ledger(self.ledger_path, self.ledger_total)
            try:
                if not led.reserve(w, block=False):
                    raise LedgerStop(str(led.halted or 'the worst case does not fit the ledger')[:300])
                rec.clear()
                try:
                    out = _ORIG_CALL(system, user, model, max_tokens=max_tokens, temperature=temperature, thinking=thinking, timeout=timeout)
                except (SystemExit, Exception) as e:
                    secs = self.clock() - t_start
                    cls = classify(rec)
                    if cls == 'not_sent':
                        led.settle(w, 0.0)
                        self.tries.append({'t_start': t_start, 'secs': secs, 'outcome': 'not_sent', 'http_status': None, 'charged_usd': 0.0, 'usage_seen': False})
                        raise CallNotSent(type(e).__name__)
                    status = rec.exc.code if isinstance(rec.exc, urllib.error.HTTPError) else None
                    if isinstance(e, SystemExit):
                        usd, seen = _usage_of_record(rec, w, model)
                        if usd is None:
                            usd = 0.0 if cls == 'http_429' else w
                    else:
                        usd, seen = w, False
                    led.charge_try_failed(w, usd)
                    self.tries.append({'t_start': t_start, 'secs': secs, 'outcome': cls, 'http_status': status, 'charged_usd': usd, 'usage_seen': seen})
                    detail = cls
                    if usd > w + 1e-9:
                        raise LedgerBound(self.tries, _clean(led.halted))
                    if isinstance(e, SystemExit) and (cls == 'http_429' or cls.startswith('transport:')):
                        continue
                    raise CallFailed(self.tries, cls)
                usd = budget_judge.actual_usd('gemini-vertex', out, w)
                led.settle(w, usd)
                self.tries.append({'t_start': t_start, 'secs': self.clock() - t_start, 'outcome': 'ok', 'http_status': 200, 'charged_usd': usd,
                                   'usage_seen': not out[4].get('usage_missing')})
                if usd > w + 1e-9:
                    raise LedgerBound(self.tries, _clean(led.halted))
                return out
            finally:
                led.close()
        raise CallFailed(self.tries, detail)


def judge_decision(pid, pos, rec, decks_dir, gv, mock):
    providers.call_vertex = gv
    try:
        row, _system, _user = judge.judge_one(pid, {pid: pos}, {pid: rec}, 'shuffle-id', True, 'gemini-4-argon', None, decks_dir, 80, 32768, 'v1', False, 'gemini-vertex', 'HIGH')
    finally:
        providers.call_vertex = _ORIG_CALL
    row['mock'] = bool(mock)
    if mock and row.get('model_returned') != MOCK_MODEL:
        raise RuntimeError('mock mode but the reply was not the mock')
    return row


# ------------------------------------------------------------------------------------------------ mock
def _resp(text, finish, prompt_tokens, model=MOCK_MODEL):
    r = {'candidates': [{'content': {'parts': [{'text': text}]}, 'finishReason': finish}],
         'usageMetadata': {'promptTokenCount': prompt_tokens, 'candidatesTokenCount': 200, 'thoughtsTokenCount': 700, 'totalTokenCount': prompt_tokens + 900},
         'modelVersion': model}
    return r


def _http(code, with_usage):
    body = {'error': {'code': code, 'message': 'mock'}}
    if with_usage:
        body['usageMetadata'] = {'promptTokenCount': 100, 'candidatesTokenCount': 0, 'totalTokenCount': 100}
    return urllib.error.HTTPError('https://mock.invalid/', code, 'mock', None, io.BytesIO(json.dumps(body).encode()))


class MockPost:
    def __init__(self, mode='random', seed=0):
        self.mode, self.seed = mode, seed
        self.items = mode[4:].split(',') if mode.startswith('seq:') else None
        self.calls = 0
        self.hook = None
        self.last_headers = None

    def __call__(self, url, headers, body, timeout):
        self.calls += 1
        self.last_headers = dict(headers)
        if self.hook:
            self.hook()
        system = body['systemInstruction']['parts'][0]['text']
        user = body['contents'][0]['parts'][0]['text']
        ptok = (len(system) + len(user)) // 3
        item = 'ok'
        if self.items is not None:
            if self.calls > len(self.items):
                raise AssertionError('mock sequence exhausted')
            item = self.items[self.calls - 1]
        if item == '429':
            raise _http(429, False)
        if item == '429u':
            raise _http(429, True)
        if item == '500':
            raise _http(500, False)
        if item == '500u':
            raise _http(500, True)
        if item == 'timeout':
            raise TimeoutError('mock timeout')
        if item == 'max_tokens':
            return _resp('PLAN: 1\nREASON: MOCK', 'MAX_TOKENS', ptok)
        if item == 'noplan':
            return _resp('no plan line here', 'STOP', ptok)
        m = re.search(r'PLANS \((\d+) legal', user)
        n = int(m.group(1)) if m else 1
        k = random.Random(self.seed ^ zlib.crc32(user.encode())).randint(1, n)
        return _resp(f'PLAN: {k}\nREASON: MOCK', 'STOP', ptok)


class _BlockedOpener:
    def open(self, *a, **k):
        raise RuntimeError('NETWORK_BLOCKED')


def install_mock(mode='random', seed=0):
    providers._OPENER = _BlockedOpener()
    providers.load_key = lambda name, *a, **k: 'MOCK-KEY'
    providers.set_vertex_project('mock-project-0')
    mp = MockPost(mode, seed)
    providers._post_json = mp
    return mp


def install_live():
    """Live set-up: the key is read only from the environment (never the shell rc file), and both settings are checked once."""
    def load_key(name, *a, **k):
        return os.environ.get(name, '')
    providers.load_key = load_key
    key = os.environ.get('VERTEX_API_KEY', '')
    if not any(re.fullmatch(p, key) for p in KEY_PATTERNS):
        raise LiveSetupError('VERTEX_API_KEY is missing or does not look like a key')
    try:
        providers.vertex_project(required=True, strict=True)
    except SystemExit:
        raise LiveSetupError('VERTEX_PROJECT is missing or not a project id')
