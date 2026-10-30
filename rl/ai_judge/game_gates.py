"""Gate tools of the Gemini finished-game test: gate1, gate2-positions, gate2-games, seat1 (B2); gate3 and the gate-4 tools are added in B7.
Exit codes: PASS 0, FAIL or STOP 1, REFUSED 2, INCOMPLETE 3."""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_call  # noqa: E402
import game_kit  # noqa: E402
import game_obs  # noqa: E402
import game_shadow  # noqa: E402
import judge  # noqa: E402

LIM = ['--max-plans', '2000', '--max-nodes', '200000', '--max-steps', '30']
EXIT = {'PASS': 0, 'FAIL': 1, 'REFUSED': 2, 'INCOMPLETE': 3}


class Refused(Exception):
    pass


class GateError(Exception):
    pass


def cut(x, n=300):
    return str(x)[:n]


def write_json_fsync(path, obj):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f)
        f.flush()
        os.fsync(f.fileno())


def append_rows_fsync(path, rows, mode='a'):
    with open(path, mode, encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
        f.flush()
        os.fsync(f.fileno())


def read_jsonl(path):
    with open(path, encoding='utf-8') as f:
        return [json.loads(l) for l in f if l.strip()]


def first_diff(a, b, path='$'):
    if type(a) is not type(b):
        return (path, cut(a), cut(b))
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                return (path + '.' + str(k), cut(a.get(k, '<missing>')), cut(b.get(k, '<missing>')))
            d = first_diff(a[k], b[k], path + '.' + str(k))
            if d:
                return d
        return None
    if isinstance(a, list):
        for i in range(min(len(a), len(b))):
            d = first_diff(a[i], b[i], '%s[%d]' % (path, i))
            if d:
                return d
        return None if len(a) == len(b) else (path + '.len', len(a), len(b))
    return None if a == b else (path, cut(a), cut(b))


# ------------------------------------------------------------------------------------------------ running the lister
def run_jp(jp, args, timeout=1750):
    argv = ['prlimit', f'--as={game_kit.LISTER_MEM_BYTES}', '--', jp] + list(args)
    p = subprocess.run(argv, capture_output=True, timeout=timeout, env=game_shadow.shadow_env(os.environ))
    if p.returncode != 0:
        raise GateError('lister rc=%s: %s' % (p.returncode, cut(p.stderr.decode('utf-8', 'replace'))))
    return [json.loads(l) for l in p.stdout.decode('utf-8').splitlines() if l.strip()]


class Obs:
    def __init__(self, lines):
        self.kinds, self.problems, self.stats = {}, {}, []
        for l in lines:
            k = l.get('kind')
            if k == 'problem':
                self.problems[l.get('id')] = l.get('problems')
            elif k == 'stats':
                self.stats.append(l)
                self.kinds.setdefault(k, {})[l.get('id')] = l
            else:
                self.kinds.setdefault(k, {})[l.get('id')] = l


def obs_mode(jp, records, workdir, name, extra=()):
    os.makedirs(workdir, exist_ok=True)
    inp = os.path.join(workdir, name + '_in.jsonl')
    append_rows_fsync(inp, records, 'w')
    return Obs(run_jp(jp, ['--observations', inp] + LIM + list(extra)))


def positions_run(jp, positions, ids, decks_dir, extra=()):
    args = ['--positions', positions] + judge.deck_args(decks_dir)
    for i in ids:
        args += ['--only', i]
    return run_jp(jp, args + list(extra))


def prompt_sha(pos, rec, decks_dir):
    system, user, _shown = judge.render_prompt(pos, rec, 'shuffle-id', decks_dir, 80, 'v1')
    return judge.prompt_hash(system, user)


def prompt_for(pos_like, rec, pid, deck_file):
    decks_dir, key = game_obs.decks_dir_and_key(deck_file)
    system, user, _shown = judge.render_prompt(game_obs.pos_for_prompt(pos_like, pid, key), rec, 'shuffle-id', decks_dir, 80, 'v1')
    return system, user


def keyfree(rec):
    return [{'labels': p['labels'], 'steps': p['steps'], 'end': p['end'], 'final': p['final'], 'result': p['result']} for p in rec['plans']]


# ------------------------------------------------------------------------------------------------ gate 1
def check_reference(path, sha, ids):
    if not sha:
        raise Refused('no --ref-sha256')
    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except OSError:
        raise Refused('the reference file cannot be read')
    if hashlib.sha256(raw).hexdigest() != sha:
        raise Refused('the reference file sha256 differs from the one given')
    recs = {}
    for l in raw.decode('utf-8').splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        if r.get('kind') != 'plans':
            raise Refused('a line that is not a plans line')
        if r['id'] in recs:
            raise Refused('an id twice: ' + cut(r['id'], 60))
        recs[r['id']] = r
    missing, extra = [i for i in ids if i not in recs], [i for i in recs if i not in set(ids)]
    if missing or extra:
        raise Refused('ids missing %d (e.g. %s), extra %d (e.g. %s)' % (len(missing), cut(missing[:1], 60), len(extra), cut(extra[:1], 60)))
    for i, r in recs.items():
        if r.get('world_seed') != 1 or r.get('limits') != game_kit.LISTER_LIMITS:
            raise Refused('world_seed or limits differ for ' + cut(i, 60))
    return recs


def new_path(jp, positions, ids, decks_dir, out):
    exp = os.path.join(out, 'export.jsonl')
    if os.path.exists(exp):
        os.remove(exp)
    pos_lines = positions_run(jp, positions, ids, decks_dir, ['--export-observations', exp])
    pos_recs = {l['id']: l for l in pos_lines if l.get('kind') == 'plans'}
    exported = read_jsonl(exp) if os.path.exists(exp) else []
    obs = obs_mode(jp, exported, out, 'obs')
    res = {}
    for i in ids:
        e = {'pos_rec': pos_recs.get(i)}
        k = obs.kinds
        if i in obs.problems or any(i not in k.get(x, {}) for x in ('plans', 'plan_actions', 'root_check', 'pos_like')) or e['pos_rec'] is None:
            e['problem'] = cut(obs.problems.get(i) or 'missing line for ' + i)
        else:
            e.update(obs_rec=k['plans'][i], plan_actions=k['plan_actions'][i], root_check=k['root_check'][i], pos_like=k['pos_like'][i]['pos'])
        res[i] = e
    return res


def compute_exclusions(ids, by_id, ref, new):
    excl = []
    for i in ids:
        cls = game_obs.declared_classes(by_id[i])
        if cls:
            excl.append({'id': i, 'class': cls[0], 'detail': cls})
            continue
        if ref is not None and new[i].get('pos_rec') is not None:
            a = sorted({p['labels'][0] for p in ref[i]['plans'] if p['labels']})
            b = sorted({p['labels'][0] for p in new[i]['pos_rec']['plans'] if p['labels']})
            if a != b:
                excl.append({'id': i, 'class': 'root_first_step_labels_differ', 'detail': {'ref': cut(a), 'new': cut(b)}})
    return excl


def write_exclusions(path, excl):
    write_json_fsync(path, excl)


def make_row(pid, orig_pos, ref_rec, new, decks_dir, excluded, have_ref):
    row = {'id': pid, 'excluded': excluded, 'compared': excluded is None, 'root_ok': False, 'n_dup_of': 0, 'n_noop': 0, 'keyfree_eq_ref': None, 'prompt_game_eq_ref': False,
           'prompt_pos_eq_ref': None, 'full_sha_eq_ref': None, 'obs_eq_pos': False, 'first_diff': None}
    if new.get('problem'):
        row['first_diff'] = {'problem': new['problem']}
        return row
    rc = new['root_check']
    row['root_ok'] = rc.get('ok') is True
    row['n_dup_of'], row['n_noop'] = rc.get('n_dup_of', 0), rc.get('n_noop', 0)
    obs_rec, pos_rec = new['obs_rec'], new['pos_rec']
    row['obs_eq_pos'] = obs_rec == pos_rec
    gpos = game_obs.pos_for_prompt(new['pos_like'], pid, orig_pos['deck'])
    p_game = prompt_sha(gpos, obs_rec, decks_dir)
    p_posrec = prompt_sha(orig_pos, pos_rec, decks_dir)
    fd = None
    if have_ref:
        row['keyfree_eq_ref'] = keyfree(obs_rec) == keyfree(ref_rec)
        p_ref = prompt_sha(orig_pos, ref_rec, decks_dir)
        row['prompt_pos_eq_ref'] = p_posrec == p_ref
        row['full_sha_eq_ref'] = judge.plan_list_sha256(obs_rec) == judge.plan_list_sha256(ref_rec)
        if not row['keyfree_eq_ref']:
            d = first_diff(keyfree(ref_rec), keyfree(obs_rec))
            fd = {'what': 'keyfree', 'path': d[0], 'ref': d[1], 'new': d[2]} if d else None
    else:
        p_ref = p_posrec
        if not row['obs_eq_pos']:
            d = first_diff(pos_rec, obs_rec)
            fd = {'what': 'obs_v_pos', 'path': d[0], 'pos': d[1], 'obs': d[2]} if d else None
    row['prompt_game_eq_ref'] = p_game == p_ref
    if not row['prompt_game_eq_ref'] and fd is None:
        fd = {'what': 'prompt', 'game': p_game, 'ref': p_ref}
    row['first_diff'] = fd
    return row


def compare_rows(ids, by_id, ref, new, decks_dir, excl_map, have_ref, out):
    rows = [make_row(i, by_id[i], ref[i] if have_ref else None, new[i], decks_dir, excl_map.get(i), have_ref) for i in ids]
    append_rows_fsync(os.path.join(out, 'gate1_rows.jsonl'), rows, 'w')
    return rows


def _counts(rows):
    c = [r for r in rows if r['compared']]
    return {'ids': len(rows), 'compared': len(c), 'root_ok': sum(1 for r in rows if r['root_ok']), 'keyfree': sum(1 for r in c if r['keyfree_eq_ref']),
            'prompt': sum(1 for r in c if r['prompt_game_eq_ref']), 'full_sha': sum(1 for r in c if r['full_sha_eq_ref']), 'obs_eq_pos': sum(1 for r in rows if r['obs_eq_pos']),
            'dup_of': sum(r['n_dup_of'] for r in rows), 'noop': sum(r['n_noop'] for r in rows)}


def gate1_decide(rows, total, have_ref):
    c = _counts(rows)
    n = c['compared']
    if have_ref:
        first = 'PROMPT BYTES: %d/%d equal' % (c['prompt'], n)
    else:
        first = 'PROMPT BYTES: %d/%d equal (game path v positions path; no reference)' % (c['prompt'], n)
    lines = [first]
    by_cls = {}
    for r in rows:
        if r['excluded']:
            by_cls[r['excluded']] = by_cls.get(r['excluded'], 0) + 1
    lines.append('ids %d, compared %d, excluded %s' % (c['ids'], n, json.dumps(by_cls, sort_keys=True)))
    lines.append('root_ok %d/%d, keyfree equal %d/%d, full sha equal %d/%d (information), obs_eq_pos %d/%d' % (c['root_ok'], c['ids'], c['keyfree'], n, c['full_sha'], n, c['obs_eq_pos'], c['ids']))
    lines.append('root actions dup_of %d, noop %d' % (c['dup_of'], c['noop']))
    d14 = [r for r in rows if r['id'] in set(judge.DIAG14)]
    if d14:
        d = _counts(d14)
        lines.append('DIAG14 (information): ids %d, compared %d, root_ok %d, keyfree %d, prompt %d' % (d['ids'], d['compared'], d['root_ok'], d['keyfree'], d['prompt']))
    cmp_rows = [r for r in rows if r['compared']]
    if have_ref:
        bad = any(not r['root_ok'] for r in rows) or any(not (r['keyfree_eq_ref'] and r['prompt_game_eq_ref']) for r in cmp_rows)
    else:
        bad = any(not r['root_ok'] for r in rows) or any(not (r['obs_eq_pos'] and r['prompt_game_eq_ref']) for r in cmp_rows)
    if bad:
        lines.append('GATE1 FAIL ' + json.dumps(c, sort_keys=True))
        return lines, 1
    if not have_ref:
        lines.append('GATE1 INCOMPLETE (no reference)')
        return lines, 3
    need = math.ceil(0.9 * total)
    if n < need:
        lines.append('GATE1 INCOMPLETE (%d of %d compared; %d needed)' % (n, total, need))
        return lines, 3
    lines.append('GATE1 PASS')
    return lines, 0


def load_ids(positions_path, ids_file):
    with open(positions_path, encoding='utf-8') as f:
        plist = json.load(f)
    by_id = {p['id']: p for p in plist}
    if ids_file:
        with open(ids_file) as f:
            ids = [l.strip() for l in f if l.strip()]
    else:
        ids = [p['id'] for p in plist]
    return by_id, ids


def run_gate1(a):
    by_id, ids = load_ids(a.positions, a.ids_file)
    have_ref = bool(a.ref)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    decks_dir = os.path.abspath(a.decks_dir)
    ref = None
    if have_ref:
        try:
            ref = check_reference(a.ref, a.ref_sha256, ids)
        except Refused as e:
            print('GATE1 REFUSED: ' + cut(e))
            return 2
    new = new_path(a.new_bin, os.path.abspath(a.positions), ids, decks_dir, out)
    excl = compute_exclusions(ids, by_id, ref, new)
    write_exclusions(os.path.join(out, 'gate1_excluded.json'), excl)
    rows = compare_rows(ids, by_id, ref, new, decks_dir, {e['id']: e['class'] for e in excl}, have_ref, out)
    lines, rc = gate1_decide(rows, len(ids), have_ref)
    for l in lines:
        print(l)
    if rc == 1:
        bad = [r for r in rows if not r['root_ok'] or (r['compared'] and not (r['prompt_game_eq_ref'] and (r['keyfree_eq_ref'] if have_ref else r['obs_eq_pos'])))]
        print('excluded ids: ' + cut([e['id'] for e in excl], 1000))
        for r in bad[:6]:
            print('failing id %s: %s' % (r['id'], cut(r['first_diff'])))
    return rc


# ------------------------------------------------------------------------------------------------ gate 2a
def run_gate2a(a):
    by_id, ids = load_ids(a.positions, a.ids_file)
    decks_dir = os.path.abspath(a.decks_dir)
    os.makedirs(a.out, exist_ok=True)
    runs = {}
    for ws in (1, 2, 99):
        lines = positions_run(a.bin, os.path.abspath(a.positions), ids, decks_dir, ['--world-seed', str(ws)])
        runs[ws] = {l['id']: l for l in lines if l.get('kind') == 'plans'}
    fails = []
    for i in ids:
        base = dict(runs[1].get(i) or {})
        for ws in (2, 99):
            other = dict(runs[ws].get(i) or {})
            x, y = dict(base), dict(other)
            x.pop('world_seed', None), y.pop('world_seed', None)
            if not base or x != y:
                d = first_diff(x, y)
                fails.append((i, ws, 'plans', d))
                continue
            if prompt_sha(by_id[i], base, decks_dir) != prompt_sha(by_id[i], other, decks_dir):
                fails.append((i, ws, 'prompt', None))
    print('ids %d, world seeds 1,2,99, failures %d' % (len(ids), len(fails)))
    for f in fails[:6]:
        print('failing id %s seed %s %s %s' % (f[0], f[1], f[2], cut(f[3])))
    print('GATE2a ' + ('FAIL' if fails else 'PASS'))
    return 1 if fails else 0


# ------------------------------------------------------------------------------------------------ gate 2b
FILL = {'f2': ['--fill-seed', '2'], 'f99': ['--fill-seed', '99']}
KEYS_NAME = {'f2': 'fill2', 'f99': 'fill99', 'b': 'obs_b', 'c': 'obs_c'}


def _strip_keys(line):
    x = json.loads(json.dumps(line))
    x.pop('plans_hash', None)
    for p in x.get('plans', []):
        p.pop('key', None)
    return json.dumps(x, sort_keys=True)


def compare_record(res, skipped):
    """res: variant -> {'plans','pos_like','prompt','obs'} or {'problem'}. -> (equal, keys_equal, first_diff)"""
    a = res['a']
    keys = {n: None for n in KEYS_NAME.values()}
    equal, fd = True, None

    def fail(v, what, x, y):
        nonlocal equal, fd
        if equal:
            fd = {'variant': v, 'what': what, 'a': cut(x), 'b': cut(y)}
        equal = False
    for v in ('f2', 'f99', 'b', 'c'):
        if skipped and v in ('b', 'c'):
            continue
        r = res.get(v)
        if r is None:
            continue
        if 'problem' in a or 'problem' in r:
            if a.get('problem') != r.get('problem'):
                fail(v, 'problem', a.get('problem'), r.get('problem'))
            continue
        keys[KEYS_NAME[v]] = json.dumps(a['plans'], sort_keys=True) == json.dumps(r['plans'], sort_keys=True)
        if v in ('b', 'c'):
            if not keys[KEYS_NAME[v]]:
                d = first_diff(a['plans'], r['plans'])
                fail(v, 'plans ' + (d[0] if d else ''), d[1] if d else '', d[2] if d else '')
        elif _strip_keys(a['plans']) != _strip_keys(r['plans']):
            d = first_diff(json.loads(_strip_keys(a['plans'])), json.loads(_strip_keys(r['plans'])))
            fail(v, 'plans(key-free) ' + (d[0] if d else ''), d[1] if d else '', d[2] if d else '')
        if json.dumps(a['pos_like'], sort_keys=True) != json.dumps(r['pos_like'], sort_keys=True):
            d = first_diff(a['pos_like'], r['pos_like'])
            fail(v, 'pos_like ' + (d[0] if d else ''), d[1] if d else '', d[2] if d else '')
        if a['prompt'] != r['prompt']:
            fail(v, 'prompt bytes', cut(a['prompt'][1], 80), cut(r['prompt'][1], 80))
    return equal, keys, fd


def gate2b_decide(rows):
    comp = [r for r in rows if not r['skipped']]
    sk = len(rows) - len(comp)
    a0 = sum(1 for r in comp if r['actor'] == 0)
    a1 = sum(1 for r in comp if r['actor'] == 1)
    oc = sum(1 for r in comp if r['has_obs_c'])
    lines = ['records %d (skipped %d)' % (len(rows), sk), 'skipped share %.3f' % (sk / len(rows) if rows else 0.0),
             'compared %d, actor 0: %d, actor 1: %d, with obs_c: %d' % (len(comp), a0, a1, oc)]
    if any(not r['equal'] for r in rows):
        bad = [r for r in rows if not r['equal']]
        for r in bad[:6]:
            lines.append('failing id %s: %s' % (r['id'], cut(r.get('first_diff'))))
        lines.append('GATE2b FAIL')
        return lines, 1
    if len(comp) < 200 or a0 < 50 or a1 < 50 or oc < 50:
        lines.append('GATE2b INCOMPLETE (compared %d/200, actor0 %d/50, actor1 %d/50, obs_c %d/50)' % (len(comp), a0, a1, oc))
        return lines, 3
    lines.append('GATE2b PASS')
    return lines, 0


def _variant_result(obs, rid, deck_file):
    if rid in obs.problems or any(rid not in obs.kinds.get(k, {}) for k in ('plans', 'pos_like')):
        return {'problem': cut(obs.problems.get(rid) or 'missing line')}
    plans, pl = obs.kinds['plans'][rid], obs.kinds['pos_like'][rid]['pos']
    try:
        prompt = prompt_for(pl, plans, rid, deck_file)
    except Exception as e:  # a prompt that cannot be rendered is a difference only when the variants differ
        return {'problem': 'prompt: ' + type(e).__name__}
    return {'plans': plans, 'pos_like': pl, 'prompt': prompt}


def run_gate2b(a):
    out = os.path.abspath(a.out)
    rows_path = os.path.join(out, 'gate2b_rows.jsonl')
    if os.path.exists(rows_path) and not a.append:
        print('GATE2b REFUSED: the rows file exists (use --append)')
        return 2
    os.makedirs(out, exist_ok=True)
    recs = read_jsonl(a.leak)
    tag = hashlib.sha256(a.leak.encode()).hexdigest()[:8]

    def inp(v):
        key = {'a': 'obs_a', 'f2': 'obs_a', 'f99': 'obs_a', 'b': 'obs_b', 'c': 'obs_c'}[v]
        out_l = []
        for r in recs:
            if v in ('b', 'c') and (r.get('skipped') or r.get(key) is None):
                continue
            out_l.append({'id': r['id'], 'pdl_observation': r[key], 'legal_actions': r.get('legal_actions')})
        return out_l
    obs = {}
    stats = []
    for v in ('a', 'f2', 'f99', 'b', 'c'):
        li = inp(v)
        obs[v] = obs_mode(a.bin, li, out, 'g2b_%s_%s' % (tag, v), FILL.get(v, [])) if li else Obs([])
        stats += obs[v].stats
    rows = []
    for r in recs:
        res = {v: _variant_result(obs[v], r['id'], r['deck_file']) for v in ('a', 'f2', 'f99')}
        sk = bool(r.get('skipped'))
        has_c = (not sk) and r.get('obs_c') is not None
        if not sk:
            res['b'] = _variant_result(obs['b'], r['id'], r['deck_file'])
            if has_c:
                res['c'] = _variant_result(obs['c'], r['id'], r['deck_file'])
        eq, keys, fd = compare_record(res, sk)
        same = lambda k: (None if sk or r.get(k) is None else json.dumps(r[k], sort_keys=True) == json.dumps(r['obs_a'], sort_keys=True))
        rows.append({'id': r['id'], 'actor': r['actor'], 'skipped': sk, 'has_obs_c': has_c, 'equal': eq, 'keys_equal': keys, 'first_diff': fd,
                     'obs_bytes_identical': {'obs_b': same('obs_b'), 'obs_c': same('obs_c')}})
    append_rows_fsync(rows_path, rows, 'a' if a.append else 'w')
    allrows = read_jsonl(rows_path)
    secs = [s['secs'] for s in stats if isinstance(s.get('secs'), (int, float))]
    lines, rc = gate2b_decide(allrows)
    for l in lines[:-1]:
        print(l)
    print('OBS_SECS_MEAN %.4f' % (sum(secs) / len(secs) if secs else 0.0))
    print(lines[-1])
    return rc


# ------------------------------------------------------------------------------------------------ seat 1
def seat_fields(v, variant, path=''):
    """Mirror of main.rs rel_seats: every seat value an action JSON holds, as {path: value}."""
    out = {}

    def num(p, x):
        if isinstance(x, int) and not isinstance(x, bool):
            out[p] = x

    def walk(x, p):
        if isinstance(x, dict):
            for k, y in x.items():
                q = p + '.' + k
                if k in ('player', 'source_player', 'target_player'):
                    num(q, y)
                elif k == 'attacking_ref':
                    if isinstance(y, list) and y:
                        num(q + '[0]', y[0])
                elif k in ('prior_knockouts', 'damaged_refs'):
                    if isinstance(y, list):
                        for j, it in enumerate(y):
                            if isinstance(it, list) and it:
                                num('%s[%d][0]' % (q, j), it[0])
                elif k == 'point_denial_flips':
                    if isinstance(y, list):
                        for j, it in enumerate(y):
                            if isinstance(it, list) and it and isinstance(it[0], list) and it[0]:
                                num('%s[%d][0][0]' % (q, j), it[0][0])
                elif k == 'targets' and variant == 'ApplyDamage':
                    if isinstance(y, list):
                        for j, it in enumerate(y):
                            if isinstance(it, list) and len(it) > 1:
                                num('%s[%d][1]' % (q, j), it[1])
                else:
                    walk(y, q)
        elif isinstance(x, list):
            for j, y in enumerate(x):
                walk(y, '%s[%d]' % (p, j))
    walk(v, path)
    return out


def label_numbers(label, action, actor):
    """[(printed, expected, where)] for every player number the label prints; None when the label cannot be parsed against the action."""
    act = action.get('action')
    if not isinstance(act, dict) or len(act) != 1:
        m = re.match(r'^(Promote|Activate):(\d+)@\d+$', label)
        return [] if not m else None
    variant, inner = next(iter(act.items()))
    exp = lambda s: 0 if s == actor else 1
    m = re.match(r'^(Promote|Activate):(\d+)@\d+$', label)
    if m:
        if m.group(1) != variant or not isinstance(inner, dict) or 'player' not in inner:
            return None
        return [(int(m.group(2)), exp(inner['player']), 'player')]
    if '#' in label:
        name, js = label.split('#', 1)
        try:
            printed = seat_fields(json.loads(js), name)
        except ValueError:
            return None
        want = seat_fields(inner, variant)
        if name != variant or sorted(printed) != sorted(want):
            return None
        return [(printed[p], exp(want[p]), p) for p in sorted(want)]
    return []


def seat1_check_state(rid, plans, pa, actor, opp_turn, text):
    row = {'id': rid, 'opponent_turn': opp_turn, 'has_you_line': 'You are the player on the move' in text, 'n_labels': 0, 'n_numbers': 0, 'mismatches': []}
    acts = {p['n']: p['actions'] for p in pa['plans']}
    for p in plans['plans']:
        al = acts.get(p['n'])
        for si, label in enumerate(p['labels']):
            row['n_labels'] += 1
            if al is None or si >= len(al):
                row['mismatches'].append({'plan': p['n'], 'step': si, 'label': cut(label), 'printed': None, 'expected': 'no action'})
                continue
            nums = label_numbers(label, al[si], actor)
            if nums is None:
                row['mismatches'].append({'plan': p['n'], 'step': si, 'label': cut(label), 'printed': 'unparsed', 'expected': None})
                continue
            for printed, expected, where in nums:
                row['n_numbers'] += 1
                if printed != expected:
                    row['mismatches'].append({'plan': p['n'], 'step': si, 'label': cut(label), 'printed': printed, 'expected': expected, 'field': where})
    return row


def run_seat1(a):
    game_call.install_mock()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    recs = []
    for f in a.leak:
        recs += read_jsonl(f)
    use = [r for r in recs if r.get('actor') == 1 and r.get('turn_count', 0) >= 1 and r.get('obs_a') is not None]

    def opp_turn(r):
        cp = r['obs_a'].get('template', {}).get('current_player', r.get('current_player'))
        return cp != r['actor']
    opp = [r for r in use if opp_turn(r)]
    own = [r for r in use if not opp_turn(r)]
    sel = opp[:8]
    sel += own[:max(0, 8 - len(sel))]
    print('selected %d states (%d opponent-turn; available %d opponent-turn)' % (len(sel), sum(1 for r in sel if opp_turn(r)), len(opp)))
    if len(sel) < 8 or len(opp) < 2:
        print('SEAT1 INCOMPLETE (selected %d of 8 needed, opponent-turn %d of 2 needed)' % (len(sel), len(opp)))
        return 3
    obs = obs_mode(a.bin, [{'id': r['id'], 'pdl_observation': r['obs_a'], 'legal_actions': r.get('legal_actions')} for r in sel], out, 'seat1')
    rows = []
    for r in sel:
        rid = r['id']
        k = obs.kinds
        if rid in obs.problems or any(rid not in k.get(x, {}) for x in ('plans', 'plan_actions', 'pos_like')):
            rows.append({'id': rid, 'opponent_turn': opp_turn(r), 'problem': cut(obs.problems.get(rid) or 'missing line'), 'has_you_line': None, 'n_labels': 0, 'n_numbers': 0, 'mismatches': []})
            continue
        system, user = prompt_for(k['pos_like'][rid]['pos'], k['plans'][rid], rid, r['deck_file'])
        rows.append(seat1_check_state(rid, k['plans'][rid], k['plan_actions'][rid], r['actor'], opp_turn(r), system + '\n' + user))
    append_rows_fsync(os.path.join(out, 'seat1_rows.jsonl'), rows, 'w')
    ok = [r for r in rows if 'problem' not in r]
    print('checked %d states, %d with problems, labels %d, numbers %d, opponent-turn %d' % (len(ok), len(rows) - len(ok), sum(r['n_labels'] for r in ok), sum(r['n_numbers'] for r in ok),
                                                                                              sum(1 for r in ok if r['opponent_turn'])))
    if len(ok) < 8 or sum(1 for r in ok if r['opponent_turn']) < 2:
        print('SEAT1 INCOMPLETE (%d states checked after lister problems)' % len(ok))
        return 3
    bad = [r for r in ok if r['mismatches']]
    if bad:
        for r in bad[:6]:
            print('mismatch id %s: %s' % (r['id'], cut(r['mismatches'][:2])))
        print('SEAT1 STOP: label seat')
        return 1
    if any(not r['has_you_line'] for r in ok):
        print("SEAT1 STOP: no 'you' line")
        return 1
    print('SEAT1 PASS')
    return 0


# ------------------------------------------------------------------------------------------------ CLI
def build_parser():
    p = argparse.ArgumentParser(prog='game_gates')
    sub = p.add_subparsers(dest='cmd', required=True)
    g = sub.add_parser('gate1')
    g.add_argument('--positions', required=True)
    g.add_argument('--ids-file')
    g.add_argument('--decks-dir', required=True)
    g.add_argument('--new-bin', required=True)
    g.add_argument('--ref')
    g.add_argument('--ref-sha256')
    g.add_argument('--out', required=True)
    g = sub.add_parser('gate2-positions')
    g.add_argument('--positions', required=True)
    g.add_argument('--ids-file')
    g.add_argument('--decks-dir', required=True)
    g.add_argument('--bin', required=True)
    g.add_argument('--out', required=True)
    g = sub.add_parser('gate2-games')
    g.add_argument('--leak', required=True)
    g.add_argument('--bin', required=True)
    g.add_argument('--out', required=True)
    g.add_argument('--append', action='store_true')
    g = sub.add_parser('seat1')
    g.add_argument('--leak', action='append', required=True)
    g.add_argument('--bin', required=True)
    g.add_argument('--out', required=True)
    return p


HANDLERS = {'gate1': run_gate1, 'gate2-positions': run_gate2a, 'gate2-games': run_gate2b, 'seat1': run_seat1}


def main(argv=None):
    a = build_parser().parse_args(argv)
    try:
        return HANDLERS[a.cmd](a)
    except GateError as e:
        print('STOP: ' + cut(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
