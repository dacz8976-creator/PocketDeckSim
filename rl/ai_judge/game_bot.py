"""The Gemini pilot: a protocol bot. kx3 (the shadow) decides at setup and fallback points; the judge plays from turn 1 by listing plans and following the chosen one."""
import argparse
import datetime
import json
import os
import re
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_call  # noqa: E402
import game_kit  # noqa: E402
import game_lister  # noqa: E402
import game_obs  # noqa: E402
import game_shadow  # noqa: E402
import judge  # noqa: E402
import providers  # noqa: E402

KEY_RES = [re.compile(p) for p in game_call.KEY_PATTERNS]
COUNTERS = (('opponent_choice', 'opponent_choices'), ('chance', 'chance_events'), ('draw_mine', 'cards_left_deck_mine'), ('draw_opponent', 'cards_left_deck_opponent'))


def counter_reason(since):
    for name, key in COUNTERS:
        if (since or {}).get(key, 0) > 0:
            return name
    return None


def scrub_str(s, key):
    s = providers.scrub(s, key)
    for r in KEY_RES:
        s = r.sub('[redacted]', s)
    return s


def scrub_row(x, key):
    if isinstance(x, str):
        return scrub_str(x, key)
    if isinstance(x, dict):
        return {k: scrub_row(v, key) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [scrub_row(v, key) for v in x]
    return x


def jkey(a):
    return json.dumps(a, sort_keys=True)


class Fatal(Exception):
    def __init__(self, code):
        self.code = code


class Bot:
    def __init__(self, a, stdin, stdout, stderr, environ, lister, shadow_factory, clock, sleep, mock_mode):
        self.a, self.stdin, self.stdout, self.stderr, self.env = a, stdin, stdout, stderr, environ
        self.lister, self.shadow_factory, self.clock, self.sleep, self.mock_mode = lister, shadow_factory, clock, sleep, mock_mode
        self.mock = a.mock_judge is not None
        self.key = 'MOCK-KEY' if self.mock else self.env.get('VERTEX_API_KEY')
        self.shadow = None
        self.plan = None
        self.n_points = self.n_judge = self.n_tries = 0
        self.prev_fallback = False
        self.rows_f = None
        self.tmp = self.env.get('TMPDIR') or os.environ.get('TMPDIR') or '.'

    # ---- output
    def write_row(self, obj):
        if self.rows_f is None:
            self.rows_f = open(self.a.rows, 'a', encoding='utf-8')
        self.rows_f.write(json.dumps(scrub_row(obj, self.key)) + '\n')
        self.rows_f.flush()
        os.fsync(self.rows_f.fileno())

    def write_stop(self, reason, detail):
        obj = scrub_row({'reason': reason, 'detail': str(detail)[:300], 'deal_tag': self.a.deal_tag,
                         'utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}, self.key)
        with open(self.a.stop_file, 'w', encoding='utf-8') as f:
            json.dump(obj, f)
            f.flush()
            os.fsync(f.fileno())

    def reply(self, k):
        self.stdout.write(json.dumps({'i': k}) + '\n')
        self.stdout.flush()

    def err(self, text):
        self.stderr.write(scrub_str(text, self.key) + '\n')
        self.stderr.flush()

    # ---- start-up
    def startup(self):
        for n in game_kit.FORBIDDEN_ENV:
            if n in self.env:
                self.write_stop('env', 'a forbidden environment name is set: ' + n)
                raise Fatal(2)
        if self.mock:
            bad = sorted(k for k in self.env if k.startswith('VERTEX_'))
            if bad:
                self.write_stop('env', 'a VERTEX_ name is set in mock mode: ' + bad[0])
                raise Fatal(2)
            game_call.install_mock(self.mock_mode or 'random', self.a.mock_seed or 0)
            assert providers.load_key('VERTEX_API_KEY') == 'MOCK-KEY'
            assert isinstance(providers._OPENER, game_call._BlockedOpener)
        else:
            if self.a.force_fallback_every:
                self.err('--force-fallback-every is refused in live mode')
                raise Fatal(2)
            try:
                game_call.install_live()
            except game_call.LiveSetupError as e:
                self.write_stop('no_key_env', str(e))
                raise Fatal(2)
        game_call.install_recorder()

    # ---- plans
    def end_plan(self, ended):
        p = self.plan
        if p is None:
            return
        self.plan = None
        n = len(p['actions'])
        self.write_row({'schema': 'gemini_game_plan_v1', 'deal_tag': self.a.deal_tag, 'plan_id': p['plan_id'], 'n_steps': n, 'steps_played': n if ended == 'completed' else p['cursor'], 'ended': ended})

    def tail_forced(self, p, after):
        return all(p['forced'][i] for i in range(after + 1, len(p['actions'])))

    # ---- messages
    def hello(self):
        self.shadow = self.shadow_factory(self.a.protocol_bot, game_shadow.shadow_env(self.env), self.a.shadow_log, self.a.deal_tag)
        self.shadow.start()
        self.stdout.write(json.dumps({'type': 'hello', 'name': 'gemini-judge-f8', 'pdl_observation': True, 'pdl_events': True}) + '\n')
        self.stdout.flush()

    def new_game(self, msg, line):
        got, want = Counter(msg.get('deck') or []), game_obs.deck_counter(self.a.deck_file)
        if got != want:
            diff = next((c for c in sorted(set(got) | set(want)) if got.get(c, 0) != want.get(c, 0)), '?')
            self.write_stop('deck', 'first differing id %s: game %s, file %s' % (diff, got.get(diff, 0), want.get(diff, 0)))
            raise Fatal(6)
        self.shadow.new_game(line)

    def decide(self, msg, line):
        a = self.a
        t0 = self.clock()
        deadline = t0 + a.bot_timeout_s - game_kit.DECIDE_MARGIN_S
        actions, legal, obs, ply = msg['actions'], msg['legal_actions'], msg['pdl_observation'], msg['ply']
        me = msg['actor']
        tpl = obs['template']
        tc, cp = tpl['turn_count'], tpl['current_player']
        since = msg.get('pdl_since_last') or {}
        pid = f'{a.pid_prefix}-p{ply}'
        row = {'schema': 'gemini_game_decision_v1', 'deal_tag': a.deal_tag, 'ply': ply, 'actor': me, 'turn_count': tc, 'current_player': cp,
               'kind': 'setup' if tc == 0 else ('own_turn' if cp == me else 'opponent_turn'), 'n_legal': len(legal), 'since': since, 'mode': None, 'follow': None,
               'reask_reason': None, 'lister': None, 'root_check': None, 'judge': None, 'tries': [], 'n_list_runs': 0, 'n_judge_calls': 0, 'calls_this_game': self.n_judge,
               'tries_this_game': self.n_tries, 'ledger_charge_usd': 0.0, 'plan': None, 'fallback': None, 'shadow_secs': None, 'reply_i': None, 'secs_total': None, 'mock': self.mock}
        legal_json = [jkey(x) for x in legal]

        def finish(k, shadow_secs=None):
            row['reply_i'], row['shadow_secs'], row['secs_total'] = k, shadow_secs, self.clock() - t0
            row['calls_this_game'], row['tries_this_game'] = self.n_judge, self.n_tries
            self.write_row(row)
            self.reply(k)

        if tc == 0:
            k, secs = self.shadow.ask(line, deadline, len(actions), ply)
            row['mode'] = 'setup'
            finish(k, secs)
            return
        counter = counter_reason(since)
        reask = counter
        lister_err = False
        if self.plan and counter:
            self.end_plan('reask:' + counter)
        p = self.plan
        if p:
            c = p['cursor']
            n = len(p['actions'])
            cprime = next((i for i in range(c, n) if not p['forced'][i]), None)
            if cprime is None:
                self.end_plan('completed')
            else:
                try:
                    h = self.lister.obs_hash(pid, obs)
                except game_lister.ListerError:
                    lister_err = True
                    self.end_plan('reask:lister_error')
                    reask = reask or 'lister_error'
                else:
                    ok = h == p['hash_after'][cprime - 1]
                    legal_ok = jkey(p['actions'][cprime]) in legal_json
                    row['follow'] = {'plan_id': p['plan_id'], 'step': cprime, 'skipped_forced': cprime - c, 'hash_ok': ok}
                    if ok and legal_ok:
                        p['cursor'] = cprime + 1
                        row['mode'] = 'follow'
                        k = legal_json.index(jkey(p['actions'][cprime]))
                        if self.tail_forced(p, cprime):
                            self.end_plan('completed')
                        finish(k)
                        return
                    if self.mock:
                        with open(os.path.join(self.tmp, 'stale_%s_%s.json' % (a.deal_tag, ply)), 'w') as f:
                            json.dump({'decide': line.rstrip('\n'), 'plan_id': p['plan_id'], 'c': c, 'cprime': cprime}, f)
                    self.end_plan('stale')
                    reask = reask or 'stale'
        # an intervention point
        row['mode'] = 'intervene'
        row['reask_reason'] = reask or ('after_fallback' if self.prev_fallback else 'first' if self.n_points == 0 else 'plan_done')
        self.n_points += 1
        fb = None
        r = None
        tries = []
        if lister_err:
            fb = ('a', 'lister_error')
        elif self.n_judge >= a.call_cap:
            fb = ('d', 'call_cap')
        elif self.mock and a.force_fallback_every and self.n_points % a.force_fallback_every == 0:
            fb = ('dev', 'forced_dev')
        if fb is None:
            row['n_list_runs'] = 1
            r = self.lister.list(pid, obs, legal)
            rec = r.rec
            row['lister'] = {'secs': r.secs, 'rc': r.rc, 'n_plans': rec['n_plans'] if rec else None, 'total_found': rec['total_found'] if rec else None, 'capped': rec['capped'] if rec else None,
                             'nodes': rec['nodes'] if rec else None, 'paths_cut_at_max_steps': rec['paths_cut_at_max_steps'] if rec else None,
                             'vmhwm_kb': (r.stats or {}).get('vmhwm_kb'), 'plan_list_sha256': judge.plan_list_sha256(rec) if rec else None,
                             'failure': None if r.ok else '%s:%s' % (r.reason[0], r.reason[1])}
            if r.root:
                rc = r.root
                row['root_check'] = {'ok': rc.get('ok'), 'n_legal': rc.get('n_legal'), 'n_root': rc.get('n_root'), 'n_dup_of': rc.get('n_dup_of', 0), 'n_noop': rc.get('n_noop', 0),
                                     'missing': json.dumps(rc.get('missing_in_lister'))[:300], 'extra': json.dumps(rc.get('extra_in_lister'))[:300]}
            if not r.ok:
                fb = (r.reason[0], r.reason[1])
        if fb is None:
            decks_dir, key = game_obs.decks_dir_and_key(a.deck_file)
            pos = game_obs.pos_for_prompt(r.pos_like, pid, key)
            self.n_judge += 1
            row['n_judge_calls'] = 1
            gv = game_call.GatedVertex(a.ledger, a.ledger_total_usd, deadline, clock=self.clock, sleep=self.sleep)
            try:
                jrow = game_call.judge_decision(pid, pos, r.rec, decks_dir, gv, self.mock)
            except game_call.CallFailed as e:
                tries = e.tries
                fb = ('c', e.detail)
            else:
                tries = gv.tries
                row['judge'] = jrow
                if jrow.get('plan_number') is None:
                    fb = ('c', 'no_usable_answer')
            row['tries'] = tries
            self.n_tries += len(tries)
            row['ledger_charge_usd'] = sum(t['charged_usd'] for t in tries)
        if fb is None:
            matches = [q for q in r.rec['plans'] if q['key'] == jrow['plan_key']]
            if len(matches) != 1 or matches[0]['n'] != jrow['plan_number'] or matches[0]['n'] not in r.actions:
                fb = ('a', 'plan_key_missing')
            else:
                plan_n = matches[0]['n']
                plan_acts, forced = r.actions[plan_n]
                tr = self.lister.trace(pid, obs, plan_acts)
                if not tr.get('ok') or len(tr.get('steps') or []) != len(plan_acts):
                    fb = ('a', 'trace_error')
                elif jkey(plan_acts[0]) not in legal_json:
                    fb = ('a', 'first_step_illegal')
        if fb is None:
            hash_after = [s.get('hash_after') for s in tr['steps']]
            self.plan = {'plan_id': pid, 'n': plan_n, 'key': jrow['plan_key'], 'actions': plan_acts, 'forced': forced, 'hash_after': hash_after, 'cursor': 1}
            row['plan'] = {'plan_id': pid, 'n': plan_n, 'key': jrow['plan_key'], 'n_steps': len(plan_acts), 'end': matches[0].get('end')}
            if self.mock:
                with open(os.path.join(self.tmp, 'plan_%s_%s.json' % (a.deal_tag, pid)), 'w') as f:
                    json.dump({'decide': line.rstrip('\n'), 'plan_acts': plan_acts, 'hash_after': hash_after}, f)
            self.prev_fallback = False
            if self.tail_forced(self.plan, 0):
                self.end_plan('completed')
            finish(legal_json.index(jkey(plan_acts[0])))
            return
        self.plan = None
        k, secs = self.shadow.ask(line, deadline, len(actions), ply)
        row['fallback'] = {'reason': fb[0], 'detail': fb[1], 'shadow_i': k, 'shadow_secs': secs}
        self.prev_fallback = True
        finish(k, secs)

    # ---- the loop
    def run(self):
        try:
            self.startup()
            for line in self.stdin:
                if not line.strip():
                    continue
                try:
                    msg = json.loads(line)
                except ValueError:
                    continue
                t = msg.get('type') if isinstance(msg, dict) else None
                if t == 'hello':
                    self.hello()
                elif t == 'new_game':
                    self.new_game(msg, line)
                elif t == 'decide':
                    self.decide(msg, line)
            return 0
        except Fatal as f:
            return f.code
        except game_call.LedgerStop as e:
            self.write_stop('ledger', e)
            return 3
        except game_shadow.ShadowError as e:
            self.write_row({'fatal': 'shadow', 'detail': str(e)[:300]})
            return 4
        except game_call.CallNotSent as e:
            self.write_row({'fatal': 'CallNotSent'})
            self.write_stop('not_sent', 'the judge call was never sent')
            return 5
        except Exception as e:
            self.write_row({'fatal': type(e).__name__, 'detail': str(e)[:300]})
            self.err('fatal %s: %s' % (type(e).__name__, str(e)[:300]))
            return 5
        finally:
            if self.shadow is not None:
                try:
                    self.shadow.close()
                except Exception:
                    pass
            if self.rows_f is not None:
                self.rows_f.close()


def build_parser():
    p = argparse.ArgumentParser(prog='game_bot')
    for name in ('deck-file', 'plans-bin', 'protocol-bot', 'pid-prefix', 'deal-tag', 'rows', 'shadow-log', 'ledger', 'stop-file'):
        p.add_argument('--' + name, required=True)
    p.add_argument('--ledger-total-usd', type=float, required=True)
    p.add_argument('--call-cap', type=int, default=game_kit.CALL_CAP)
    p.add_argument('--bot-timeout-s', type=float, default=2700)
    p.add_argument('--mock-judge', choices=['random'])
    p.add_argument('--mock-seed', type=int, default=0)
    p.add_argument('--force-fallback-every', type=int)
    return p


def main(argv=None, stdin=None, stdout=None, stderr=None, environ=None, lister=None, shadow_factory=None, clock=None, sleep=None, mock_mode=None):
    a = build_parser().parse_args(argv)
    environ = os.environ if environ is None else environ
    if lister is None:
        lister = game_lister.Lister(a.plans_bin, environ.get('TMPDIR') or '.')
    bot = Bot(a, stdin or sys.stdin, stdout or sys.stdout, stderr or sys.stderr, environ, lister, shadow_factory or game_shadow.Kx3Shadow, clock or time.monotonic, sleep or time.sleep, mock_mode)
    return bot.run()


if __name__ == '__main__':
    sys.exit(main())
