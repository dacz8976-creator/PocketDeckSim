"""The kx3 shadow: a protocol_bot --bot kx3 child, asked only at setup and fallback points."""
import json
import os
import queue
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_kit  # noqa: E402


def shadow_env(environ):
    return {k: environ[k] for k in game_kit.SHADOW_ENV_KEEP if k in environ}


class ShadowError(Exception):
    pass


class Kx3Shadow:
    def __init__(self, protocol_bot, env, log_path=None, deal_tag=''):
        self.protocol_bot = protocol_bot
        self.env = env
        self.log_path = log_path
        self.deal_tag = deal_tag
        self.pid = None
        self.proc = None
        self.q = queue.Queue()
        self._new_game = None
        self._closed = False
        self._outstanding = False

    def _reader(self, out):
        try:
            for line in out:
                self.q.put(line)
        except (OSError, ValueError):
            pass
        self.q.put(None)

    def _readline(self, deadline):
        left = deadline - time.monotonic()
        try:
            line = self.q.get(timeout=max(0.0, left))
        except queue.Empty:
            raise ShadowError('timeout')
        if line is None:
            self.q.put(None)
            raise ShadowError('eof')
        return line

    def _write(self, text):
        try:
            self.proc.stdin.write(text.encode('utf-8'))
            self.proc.stdin.flush()
        except (OSError, ValueError) as e:
            raise ShadowError('write failed: ' + type(e).__name__)

    def start(self, hello_timeout_s=60):
        try:
            self.proc = subprocess.Popen([self.protocol_bot, '--bot', 'kx3'], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=None, env=self.env)
        except OSError as e:
            raise ShadowError('spawn failed: ' + type(e).__name__)
        self.pid = self.proc.pid
        threading.Thread(target=self._reader, args=(self.proc.stdout,), daemon=True).start()
        try:
            self._write('{"type":"hello","protocol":1}\n')
            line = self._readline(time.monotonic() + hello_timeout_s)
            obj = json.loads(line)
        except ShadowError:
            self.close()
            raise
        except ValueError:
            self.close()
            raise ShadowError('hello not json')
        if not isinstance(obj, dict) or obj.get('name') != 'pdl-kx3' or obj.get('pdl_observation') is not True:
            self.close()
            raise ShadowError('bad hello')

    @staticmethod
    def _nl(raw):
        return raw if raw.endswith('\n') else raw + '\n'

    def new_game(self, raw_line):
        self._new_game = raw_line.rstrip('\n')
        self._write(self._nl(raw_line))

    def send_decide(self, raw_line):
        if self._outstanding:
            raise ShadowError('decide already outstanding')
        self._write(self._nl(raw_line))
        self._outstanding = True

    def read_reply(self, deadline, n_actions):
        try:
            line = self._readline(deadline)
        finally:
            pass
        self._outstanding = False
        try:
            obj = json.loads(line)
        except ValueError:
            raise ShadowError('garbage reply')
        k = obj.get('i') if isinstance(obj, dict) else None
        if not isinstance(k, int) or isinstance(k, bool) or not 0 <= k < n_actions:
            raise ShadowError('bad index')
        return k

    def ask(self, raw_line, deadline, n_actions, ply):
        t0 = time.monotonic()
        self.send_decide(raw_line)
        k = self.read_reply(deadline, n_actions)
        secs = time.monotonic() - t0
        if self.log_path:
            rec = {'deal_tag': self.deal_tag, 'ply': ply, 'new_game': self._new_game,
                   'decide': raw_line.rstrip('\n'), 'shadow_i': k, 'secs': secs}
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec) + '\n')
                f.flush()
                os.fsync(f.fileno())
        return k, secs

    def close(self):
        if self._closed or self.proc is None:
            self._closed = True
            return
        self._closed = True
        try:
            self.proc.stdin.close()
        except (OSError, ValueError):
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.proc.wait()
