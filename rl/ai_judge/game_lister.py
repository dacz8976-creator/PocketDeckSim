"""Wrapper around the lister binary's observation mode: one subprocess per call, no shell, under a memory limit and a hang guard."""
import json
import os
import subprocess
import sys
import tempfile
import time
from collections import namedtuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import game_kit  # noqa: E402
import game_shadow  # noqa: E402

ListResult = namedtuple('ListResult', 'ok reason detail rec actions root pos_like stats secs rc stderr_tail')
LIMIT_ARGS = ['--max-plans', '2000', '--max-nodes', '200000', '--max-steps', '30']
REQUIRED = ('plans', 'plan_actions', 'root_check', 'stats', 'pos_like')


class ListerError(Exception):
    pass


class Lister:
    def __init__(self, bin_path, tmpdir, mem_bytes=game_kit.LISTER_MEM_BYTES, hang_s=game_kit.LISTER_HANG_S):
        if mem_bytes is None:
            raise ListerError('LISTER_MEM_BYTES is not set')
        self.bin_path, self.tmpdir, self.mem_bytes, self.hang_s = bin_path, tmpdir, mem_bytes, hang_s

    def _call(self, records, mode_args):
        fd, path = tempfile.mkstemp(dir=self.tmpdir, suffix='.jsonl')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                for r in records:
                    f.write(json.dumps(r) + '\n')
            argv = ['prlimit', f'--as={self.mem_bytes}', '--', self.bin_path, mode_args[0], path] + mode_args[1:]
            t0 = time.monotonic()
            try:
                p = subprocess.run(argv, capture_output=True, timeout=self.hang_s, env=game_shadow.shadow_env(os.environ))
            except subprocess.TimeoutExpired:
                return None, time.monotonic() - t0
            return p, time.monotonic() - t0
        finally:
            try:
                os.remove(path)
            except OSError:
                pass

    @staticmethod
    def _lines(p):
        out = []
        for l in p.stdout.decode('utf-8', 'replace').splitlines():
            if l.strip():
                try:
                    out.append(json.loads(l))
                except ValueError:
                    out.append({'kind': 'garbage'})
        return out

    def list(self, pid, obs, legal):
        p, secs = self._call([{'id': pid, 'pdl_observation': obs, 'legal_actions': legal}], ['--observations'] + LIMIT_ARGS)

        def res(ok, reason, detail='', rec=None, actions=None, root=None, pos_like=None, stats=None, rc=None, tail=''):
            return ListResult(ok, reason, detail, rec, actions or {}, root, pos_like, stats, secs, rc, tail)

        if p is None:
            return res(False, ('a', 'hang_guard_600s'))
        tail = p.stderr.decode('utf-8', 'replace')[-2000:]
        if p.returncode < 0 or 'memory allocation' in p.stderr.decode('utf-8', 'replace'):
            return res(False, ('b', 'memory_cap'), 'rc=%s' % p.returncode, rc=p.returncode, tail=tail)
        lines = self._lines(p)
        kinds = {}
        for l in lines:
            kinds.setdefault(l.get('kind'), l)
        if p.returncode != 0:
            return res(False, ('a', 'lister_error'), 'rc=%s' % p.returncode, rc=p.returncode, tail=tail)
        if 'problem' in kinds:
            return res(False, ('a', 'lister_error'), str(kinds['problem'].get('problems'))[:300], rc=p.returncode, tail=tail)
        missing = [k for k in REQUIRED if k not in kinds]
        if missing:
            return res(False, ('a', 'lister_error'), 'missing ' + ','.join(missing), rc=p.returncode, tail=tail)
        rec = kinds['plans']
        actions = {pa['n']: (pa['actions'], pa['forced']) for pa in kinds['plan_actions']['plans']}
        base = dict(rec=rec, actions=actions, root=kinds['root_check'], pos_like=kinds['pos_like']['pos'], stats=kinds['stats'], rc=p.returncode, tail=tail)
        if rec['capped']:
            lim = rec['limits']
            if rec['total_found'] > rec['n_plans']:
                why = 'plans_over_2000'
            elif rec['nodes'] > lim['max_nodes']:
                why = 'node_cap'
            elif rec['paths_cut_at_max_steps'] > 0:
                why = 'step_cap'
            else:
                why = 'node_cap'
            return res(False, ('b', why), **base)
        if rec['n_plans'] == 0:
            return res(False, ('a', 'empty'), **base)
        if kinds['root_check']['ok'] is False:
            return res(False, ('a', 'root_mismatch'), **base)
        return res(True, None, **base)

    def trace(self, pid, obs, actions):
        p, _ = self._call([{'id': pid, 'pdl_observation': obs, 'actions': actions}], ['--trace'])
        if p is None:
            return {'ok': False, 'error': 'hang_guard_600s', 'steps': []}
        lines = [l for l in self._lines(p) if l.get('kind') == 'trace']
        if p.returncode != 0 or not lines:
            return {'ok': False, 'error': 'lister_error rc=%s' % p.returncode, 'steps': []}
        return lines[0]

    def obs_hash(self, pid, obs):
        p, _ = self._call([{'id': pid, 'pdl_observation': obs}], ['--obs-hash'])
        if p is None:
            raise ListerError('hang_guard_600s')
        lines = [l for l in self._lines(p) if l.get('kind') == 'obs_hash']
        if p.returncode != 0 or not lines:
            raise ListerError('lister_error rc=%s' % p.returncode)
        return lines[0]['hash']
