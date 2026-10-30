import datetime
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import game_kit  # noqa: E402
import game_shadow  # noqa: E402

PB = '/home/dacz8976/gemini_target/engine/release/protocol_bot'
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
TMP = os.environ['TMPDIR']


def fake(body):
    fd, path = tempfile.mkstemp(dir=TMP, suffix='.py')
    with os.fdopen(fd, 'w') as f:
        f.write('#!/usr/bin/env python3\n' + body)
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


class Shadow(unittest.TestCase):
    def mk(self, path, **kw):
        s = game_shadow.Kx3Shadow(path, game_shadow.shadow_env(os.environ), **kw)
        self.addCleanup(s.close)
        return s

    def test_S1_env(self):
        env = {'PATH': '/bin', 'HOME': '/h', 'TMPDIR': '/t', 'RAYON_NUM_THREADS': '2', 'EXTRA': 'x',
               'LANG': 'C', 'LC_ALL': 'C',
               'VERTEX_' + 'API_KEY': 'fake' + '-' * 3, 'VERTEX_' + 'PROJECT': 'fake-p',
               'KX_EXTRA_LISTS': 'a', 'PDL_DB': 'b', 'PG_DUMP': 'c'}
        out = game_shadow.shadow_env(env)
        self.assertEqual(set(out), set(game_kit.SHADOW_ENV_KEEP))
        self.assertEqual(len(out), 6)
        self.assertTrue(set(game_kit.FORBIDDEN_ENV).isdisjoint(out))

    def test_S2_real_handshake(self):
        self.assertTrue(os.path.exists(PB))
        s = self.mk(PB)
        s.start()
        self.assertIsNotNone(s.pid)

    def test_S3_wrong_name(self):
        p = fake("import sys\nsys.stdin.readline()\nprint('{\"name\":\"other\",\"pdl_observation\":true}',flush=True)\nsys.stdin.read()\n")
        with self.assertRaises(game_shadow.ShadowError):
            self.mk(p).start()

    HELLO = "import sys\nsys.stdin.readline()\nprint('{\"name\":\"pdl-kx3\",\"pdl_observation\":true}',flush=True)\n"

    def test_S4_timeout_and_close(self):
        p = fake(self.HELLO + "import time\nwhile True: time.sleep(1)\n")
        s = self.mk(p)
        s.start()
        s.new_game('{"type":"new_game"}')
        s.send_decide('{"type":"decide"}')
        with self.assertRaises(game_shadow.ShadowError):
            s.read_reply(time.monotonic() + 1, 3)
        pid = s.pid
        t0 = time.monotonic()
        s.close()
        self.assertLess(time.monotonic() - t0, 7)
        t0 = time.monotonic()
        while time.monotonic() - t0 < 2:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.05)
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        s.close()

    def test_S5_failures(self):
        for body in ("print('garbage',flush=True)\nimport time\ntime.sleep(5)\n",
                     "print('{\"i\":9}',flush=True)\nimport time\ntime.sleep(5)\n",
                     "sys.exit(0)\n"):
            s = self.mk(fake(self.HELLO + body))
            s.start()
            with self.assertRaises(game_shadow.ShadowError):
                s.ask('{"type":"decide"}', time.monotonic() + 3, 3, 1)
        s = self.mk(fake(self.HELLO + "sys.exit(0)\n"))
        s.start()
        time.sleep(0.5)
        for _ in range(3):
            try:
                s.new_game('x' * 100000)
            except game_shadow.ShadowError:
                break
        with self.assertRaises(game_shadow.ShadowError):
            s.new_game('x' * 100000)
        s._outstanding = False
        with self.assertRaises(game_shadow.ShadowError):
            s.send_decide('x' * 100000)
        with self.assertRaises(game_shadow.ShadowError):
            self.mk(os.path.join(TMP, 'no_such_bot_here')).start()

    def test_S6_S7_forwarding_and_log(self):
        hashes = os.path.join(TMP, 's6_hashes.txt')
        if os.path.exists(hashes):
            os.remove(hashes)
        body = ("import sys,hashlib,json\n"
                "n=0\n"
                "for raw in sys.stdin.buffer:\n"
                "    n+=1\n"
                "    h=hashlib.sha256(raw).hexdigest()\n"
                "    open(%r,'a').write(h+'\\n')\n"
                "    if n==1: out=json.dumps({'name':'pdl-kx3','pdl_observation':True,'h':h})\n"
                "    elif n<=3: out=h\n"
                "    else: out='{\"i\":1}'\n"
                "    sys.stdout.write(out+'\\n'); sys.stdout.flush()\n") % hashes
        p = fake(body)
        log = os.path.join(TMP, 's7_log.jsonl')
        if os.path.exists(log):
            os.remove(log)
        s = self.mk(p, log_path=log, deal_tag='dt')
        s.start()
        ng, dc = '{"type":"new_game","x":"\u00e9 1 \u00e9\u4e2d"}', '{"type":"decide", "ply":4}'
        s.new_game(ng + '\n')
        h_ng = s._readline(time.monotonic() + 5).strip().decode()
        s.send_decide(dc + '\n')
        h_dc = s._readline(time.monotonic() + 5).strip().decode()
        self.assertEqual(h_ng, hashlib.sha256((ng + '\n').encode('utf-8')).hexdigest())
        self.assertEqual(h_dc, hashlib.sha256((dc + '\n').encode('utf-8')).hexdigest())
        s._outstanding = False
        k, secs = s.ask(dc, time.monotonic() + 5, 3, 4)
        self.assertEqual(k, 1)
        sent = open(hashes).read().split()
        hello = hashlib.sha256(b'{"type":"hello","protocol":1}\n').hexdigest()
        self.assertEqual(sent[0], hello)
        rec = json.loads(open(log).read().splitlines()[-1])
        self.assertEqual((rec['new_game'], rec['decide'], rec['shadow_i'], rec['deal_tag'], rec['ply']), (ng, dc, 1, 'dt', 4))


class Kit(unittest.TestCase):
    def test_K1_kit(self):
        import judge
        self.assertEqual(game_kit.seed(15, 99), 25_103_001_599)
        for bad in ((16, 0), (0, 100), (-1, 0)):
            with self.assertRaises(AssertionError):
                game_kit.seed(*bad)
        for c in range(16):
            b = game_kit.cell_bits(c)
            self.assertEqual(game_kit.cell_of(b['deck'], b['list'], b['policy'], b['seat']), c)
        o = game_kit.STAGE1_ORDER
        self.assertEqual(sorted(o), list(range(16)))
        bits = [game_kit.cell_bits(c) for c in o[:6]]
        for key in ('deck', 'list', 'policy', 'seat'):
            self.assertEqual({b[key] for b in bits}, {0, 1})
        for key in ('deck', 'list'):
            for v in (0, 1):
                self.assertGreaterEqual(sum(b[key] == v for b in bits), 2)
        self.assertEqual(game_kit.SHADOW_FEED, 'fallback')
        datetime.datetime.strptime(game_kit.STOP_AT_UTC, '%Y-%m-%dT%H:%M:%SZ')
        files = list(game_kit.DECKS.values()) + list(game_kit.LISTS.values())
        ids = set()
        for rel in files:
            path = os.path.join(REPO, rel)
            d, key = os.path.dirname(path), os.path.basename(path)[:-4]
            pos = {'me': {'hand': [], 'discard': [], 'board': []}, 'opp': {'board': [], 'discard': []},
                   'stadium': None, 'deck': key}
            judge.card_texts(pos, d)
            for i in judge._deck_ids(key, d):
                ids.add(i)
        self.assertIsNotNone(judge._DB)
        missing = [i for i in ids if i not in judge._DB]
        print('K1_CARD_IDS', len(ids))
        self.assertEqual(missing, [])


if __name__ == '__main__':
    unittest.main()
