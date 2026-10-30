"""Gate 5: the frozen-8 identity. `record` writes it, `check` recomputes it and lists every difference.
Exit codes of check: 0 GATE5 PASS, 1 GATE5 FAIL, 3 GATE5 DRAFT. record exits 2 on a missing source or binary."""
import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import game_kit  # noqa: E402
import judge  # noqa: E402
import providers  # noqa: E402

DEFAULT_ENGINE_BINS = '/home/dacz8976/gemini_target/engine/release'
DEFAULT_JUDGE_BINS = '/home/dacz8976/gemini_target/judge/release'
ENGINE_BINARIES = ('deckgym', 'protocol_bot')
JUDGE_BINARIES = ('judge_plans', 'kx3_parity', 'kx3_replay', 'leak_states')
EXPECTED_DG = 'e6a8bf768c4fd3cf8592f097773d1faaf9e1f1b15ac0e3030b17382efcaffa75'
EXPECTED_PB = 'd3a976cccc70263fe5d5688b0ac4727a1c33700fe28dafdd39f5ca9d618e6295'
LAPTOP_FIELDS = ('frozen_on', 'supersedes[0].commit', 'kx3.selfcheck_checked')
MAIN_RS_SUFFIX = 'plans/src/main.rs'
SELFCHECK_PIN = 'selfcheck pilot=kx3 games=12 seat0_wins=5 seat1_wins=7 ties=0 turns=138 digest=31d638dbc818b0fa'
VERTEX_FROZEN_EXPECT = {'provider': 'gemini-vertex', 'model': 'gemini-4-argon', 'location': 'global', 'max_tokens': 32768, 'temperature': None, 'thinking_level': 'HIGH'}

DEVIATIONS = [
    ('lister_rebuild', 'frozen-7, PREREG v3.1 §2 (i)', 'PREREG v3.1',
     '''The plan lister is rebuilt on engine tree e36452d3 plus kx3's files (tree 34fef9e5): a seat parameter, steps that keep their actions, root classification, obs_hash, and the observation, trace and obs-hash modes. Positions-mode output stays byte-identical to the pre-edit build. Reason: the game path lists plans from the adapter's observation, for either seat.'''),
    ('converter', 'frozen-7, PREREG v3.1 §2 (ii)', 'PREREG v3.1',
     '''A converter turns the adapter's pdl_observation into the lister's input and the prompt's position fields. Reason: game prompts are built from the observation only.'''),
    ('plan_keys', 'frozen-7', 'coordinator-103, wording coordinator-108',
     '''Plan keys may differ from frozen-7's (the State JSON can gain fields); on the 92 they were equal (gate 1: full plan_list_sha256 92/92). Keys never reach the prompt. Gate 1 compares the key-free projection (labels, steps, ends, finals, results), the prompt bytes, and root_ok on every id; full plan_list_sha256 equality is for information only.'''),
    ('label_seats', 'frozen-7', 'coordinator-104',
     '''label seat numbers made relative to the actor, to match frozen-7's mover-at-0 convention. The actor is 0 and the opponent 1 in Promote, Activate, the English label text and every player field inside a Name#{json} label, and in that label's other seat fields (target_player, source_player, and the seat element of attacking_ref, targets, prior_knockouts, damaged_refs and point_denial_flips); the action sent to the engine keeps its real seat. With actor 0 the output is byte-identical by construction.'''),
    ('turn_effects', 'frozen-7', 'laptop fact (Oct 30 engine read: add_turn_effect is never pruned)',
     '''Game prompts show the turn effects with turn equal to turn_count, in State order, as {turn, effect} dicts, with every player, source_player and target_player value made relative to the actor (actor 0, opponent 1), on the line for effects active this turn. Frozen-7's 92 positions never had a non-empty list, so this line is new content in game prompts. Reason: the engine writes entries for later turns and never prunes them; only the current turn's entries are active. Kept turn effects print as {"turn", "effect"} items; each effect's inner keys print in serde_json's sorted order, because observation mode serialises them with serde_json::to_value without preserve_order, so no other order can occur there.'''),
    ('retries_and_charges', 'frozen-7, PREREG v3.1 §3 and §5', 'coordinator-103',
     '''A returned call is never re-sent. HTTP 429 and transport errors are retried, 3 tries within 10 minutes, outside providers.py; HTTP 5xx goes to fallback (c) at once. A try is charged its usage when the response carries usage metadata; a 429 with no usage metadata is charged $0; any other failed try with no usage is charged frozen-7's worst case. Reason: PREREG v3.1 §3 has 429 and transport errors wait and retry, while frozen-7 sent one request with no retry, so the retry sits outside providers.py and frozen-7's judge block and identity test stay valid; the charges and the 5xx rule are coordinator-103's.'''),
    ('call_cap', 'PREREG v3.1 §3', 'coordinator-103',
     '''CALL_CAP = 75 counts judge decisions per game, not tries; fallback (d) fires at the 76th decision point. Reason: retries do not use up the cap.'''),
    ('shadow_feed', 'PREREG v3.1 §2', 'coordinator-103, wording coordinator-105',
     '''PREREG v3.1 §2 said the shadow is fed every observation and event; it is asked only at setup and fallback points, because kx3 keeps no state between decisions (gate 4b proves equality) and feeding every decide would roughly double each (G) game's compute.'''),
    ('setup_by_kx3', 'PREREG v3.1 §3', 'coordinator-103',
     '''kx3 makes setup choices (turn_count == 0) in both arms; the judge plays from turn 1. Setup decisions are out of the fallback denominator and are counted separately. This narrows PREREG v3.1 §3, which listed setup as an intervention point. Reason: neutral between arms; frozen-7's lister was never validated on setup states.'''),
    ('gate1_rule', 'PREREG v3.1 §2 gate 1', 'coordinator-103',
     '''Gate 1 reads 'root legal sets differ' as 'root first-step label sets differ', because frozen-7's binary emits no legal set. Excluded ids are listed before comparing, root_ok must hold on every id, and fewer than 83 of the 92 compared is INCOMPLETE. A position in one of the converter's declared classes (none occurs in the 92) is also excluded and listed before comparing.'''),
    ('kx3_route_drop', 'PREREG v3.1 §6', 'coordinator-103',
     '''A fallback in a (K) pilot seat or in any kx3 opponent seat, or a failure of the (G) arm's kx3 shadow, drops the pair (both arms), reported like an engine error and counted by arm and reason; the not-testable label (more than 5% of pairs dropped) applies. Stage 1 stops when more than 2 of its deals drop, for any cause, and its report lists the drops by cause. Reason: such a game was not played by the registered programs, and treating both arms alike keeps the drop symmetric.'''),
    ('gate2_fill_seed', 'PREREG v3.1 §2 gate 2', 'brief v2 review',
     '''Under a changed fill-in seed, gate 2 compares the key-free plan list and the prompt bytes, because plan keys hash the filled world's own-deck order; keys never reach the prompt.'''),
    ('gate2_revealed', 'PREREG v3.1 §2 gate 2', 'brief v2 review',
     '''On states where cards were revealed, gate 2 does not swap the opponent's hand or deck (it would contradict what was revealed); it still varies the fill-in seed, and the skipped share is reported.'''),
    ('root_dup_noop', 'PREREG v3.1 §2 judge bot step 2', 'coordinator-103',
     '''A legal root action whose child state equals the root's (noop) or the child of an earlier root action (dup_of) is accepted though no plan starts with it; it is counted, not a fallback. Reason: the lister de-duplicates children through seen, so such an action can never head a plan, and the judge still sees every distinct outcome. It is a pure no-op: accepting such an action changes no output byte (plan lines, prompts, rows other than its counters).'''),
    ('reask_lister_error', 'PREREG v3.1 §2 judge bot', 'coordinator-106, decision 5; coordinator-108',
     '''reask_reason gains a sixth value, 'lister_error', for a re-ask after a lister failure (coordinator-106, decision 5).'''),
]


def game_path():
    k = game_kit
    return {
        'resend': 'A call that returned is never sent again, whatever its stop_reason.',
        'retries': 'Only HTTP 429 and transport errors are retried: %d tries within %d s (waits %s s), outside providers.py. HTTP 5xx goes to fallback (c) at once.' % (k.MAX_TRIES, k.RETRY_WINDOW_S, list(k.RETRY_WAITS_S)),
        'charges': ('A try is charged its usage when the response carries usage metadata. A 429 with no usage metadata is charged $0. Any other failed try with no usage is charged frozen-7\'s worst case. '
                    'A try that never reached _post_json is settled at $0 and the run stops (STOP not_sent).'),
        'call_cap': 'CALL_CAP = %d judge decisions per game, not tries. Fallback (d) fires at the first intervention point after the %dth judge decision; earlier fallbacks do not count toward the %d.' % (k.CALL_CAP, k.CALL_CAP, k.CALL_CAP),
        'bar': 'More than 2,000 plans, the node cap, or the step cap (the max-steps cut) is fallback (b).',
        'hang_guard': 'LISTER_HANG_S = %d s is a hang guard only, and is fallback (a).' % k.LISTER_HANG_S,
        'memory_cap': ('The lister runs as argv [\'prlimit\', f\'--as={LISTER_MEM_BYTES}\', \'--\', JP, ...] and a breach is fallback (b). LISTER_MEM_BYTES = min(3 GiB, max(1 GiB, 3 x the largest VmHWM measured on the 92 and the LS dumps)) = %d.' % k.LISTER_MEM_BYTES),
        'timeouts': ('BOT_TIMEOUT_MS = %d per read; a decide\'s deadline is its start + 2,700 s - DECIDE_MARGIN_S (%d s); a judge try starts only with VERTEX_TIMEOUT_S (%d s) + SHADOW_RESERVE_S (%d s) left; GAME_WALL_S = %d s per game.'
                     % (k.BOT_TIMEOUT_MS, k.DECIDE_MARGIN_S, k.VERTEX_TIMEOUT_S, k.SHADOW_RESERVE_S, k.GAME_WALL_S)),
        'shadow': 'Every kx3 seat runs protocol_bot --bot kx3, with its env from shadow_env. The G arm\'s shadow is asked only at fallback points and at setup decisions; it is never fed otherwise (SHADOW_FEED = fallback).',
        'setup': 'kx3 makes setup choices (turn_count == 0) in both arms. The judge plays from turn 1.',
        'search_seed': 'The lister fills the world with 0x5EED_0001. It never uses pdl_search_seed.',
        'obs_hash': 'A2\'s scheme: sorted known_own_deck, canonical template, DefaultHasher.',
        'pid': 'pid_prefix(seed, cell, arm) + -p{ply}.',
        'root_check': 'dup_of and noop root actions are accepted and counted. Any other mismatch is fallback (a).',
        'label_seats': 'Label player numbers are relative to the actor (actor 0, opponent 1), including every seat field of A2.6 inside a Name#{json} label. The action sent to the engine keeps its real seat.',
        'turn_effects': ('Only the State\'s entries with turn == turn_count, in State order, as {turn, effect} dicts, with every player, source_player and target_player value made relative to the actor (actor 0, opponent 1).'),
        'stops': ('No new deal starts after STOP_AT_UTC. A heartbeat gap over PAUSE_GAP_S inside an arm, or the GAME_WALL_S kill, classes the arm infra, and it is replayed. A ledger refusal stops the run. It is never a fallback.'),
    }


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def git_tree(repo, path):
    p = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD:' + path], capture_output=True, timeout=60)
    return p.stdout.decode().strip() if p.returncode == 0 else None


def load_frozen7(repo):
    with open(os.path.join(repo, 'rl', 'ai_judge', 'FROZEN.json'), encoding='utf-8') as f:
        return json.load(f)


def is_outside(key):
    return key.startswith('rl/') and not key.startswith('rl/ai_judge/')


def resolve(repo, key):
    """A FROZEN.json key resolves from REPO first, then from REPO/rl/ai_judge. -> repo-relative path, or None."""
    for base in ('', os.path.join('rl', 'ai_judge')):
        rel = os.path.normpath(os.path.join(base, key))
        if os.path.isfile(os.path.join(repo, rel)):
            return rel
    return None


def sources8(repo):
    """-> (repo-relative paths of SOURCES8 that exist, {outside-clone key: FROZEN.json value}, [paths that are missing])"""
    fz = load_frozen7(repo)
    paths, outside, missing = [], {}, []

    def add(rel):
        if rel not in paths:
            paths.append(rel)

    for key, val in fz['source_sha256'].items():
        if is_outside(key):
            outside[key] = val
            continue
        rel = resolve(repo, key)
        if rel is None:
            missing.append(key)
        else:
            add(rel)
    ai = os.path.join('rl', 'ai_judge')
    here = lambda *p: os.path.join(ai, *p)
    wanted = [here(n) for n in ('judge.py', 'formal.py', 'analysis.py', 'providers.py', 'budget_judge.py', 'freeze_identity.py', 'FROZEN.json')]
    wanted += sorted(os.path.relpath(p, repo) for p in glob.glob(os.path.join(repo, ai, 'game_*.py')))
    wanted += [here('shadow_check.py'), here('freeze8.py'), here('plans', 'Cargo.toml'), here('plans', 'Cargo.lock')]
    for root, _dirs, files in os.walk(os.path.join(repo, ai, 'plans', 'src')):
        wanted += sorted(os.path.relpath(os.path.join(root, f), repo) for f in files if f.endswith('.rs'))
    wanted += sorted(os.path.relpath(p, repo) for p in glob.glob(os.path.join(repo, ai, 'tests', 'test_game_*.py')))
    wanted += [here('tests', 'test_freeze8.py')]
    wanted += list(game_kit.DECKS.values()) + list(game_kit.LISTS.values())
    for rel in wanted:
        if os.path.isfile(os.path.join(repo, rel)):
            add(rel)
        else:
            missing.append(rel)
    return paths, outside, missing


def rustc_version():
    try:
        return subprocess.run(['rustc', '--version'], capture_output=True, timeout=60).stdout.decode().strip()
    except OSError:
        return None


def compute(repo, engine_bins, judge_bins, draft):
    """-> (the frozen-8 record, [problems: missing files, identity mismatches])"""
    problems = []
    fz = load_frozen7(repo)
    if fz['fingerprint'] != judge.fingerprint():
        problems.append('FROZEN.json fingerprint differs from judge.fingerprint()')
    if json.loads(json.dumps(fz['settings'])) != json.loads(json.dumps(judge.FROZEN)):
        problems.append('FROZEN.json settings differ from judge.FROZEN')
    if json.loads(json.dumps(fz['judge'])) != json.loads(json.dumps(judge.frozen_judge_block())):
        problems.append('FROZEN.json judge block differs from judge.frozen_judge_block()')
    paths, outside, missing = sources8(repo)
    problems += ['missing source: ' + m for m in missing]
    src = {rel: sha256_file(os.path.join(repo, rel)) for rel in paths}
    src.update(outside)
    bins = {}
    for folder, names in ((engine_bins, ENGINE_BINARIES), (judge_bins, JUDGE_BINARIES)):
        for n in names:
            p = os.path.join(folder, n)
            if os.path.isfile(p):
                bins[n] = sha256_file(p)
                want = {'deckgym': EXPECTED_DG, 'protocol_bot': EXPECTED_PB}.get(n) if folder == engine_bins else None
                if want is not None and bins[n] != want:
                    problems.append('binary differs from EXPECTED_%s: %s' % ('DG' if n == 'deckgym' else 'PB', p))
            else:
                problems.append('missing binary: ' + p)
    kit = json.loads(json.dumps({n: getattr(game_kit, n) for n in sorted(dir(game_kit)) if n.isupper()}, default=list))
    rec = {
        'tag': 'judge-prompt-frozen-8', 'draft': bool(draft), 'frozen_on': None,
        'supersedes': [{'tag': 'judge-prompt-frozen-7', 'commit': None, 'fingerprint': fz['fingerprint']}],
        'fingerprint': fz['fingerprint'], 'settings': fz['settings'], 'judge': fz['judge'],
        'base': {'adapter_tip': '2639a261', 'engine_tree_base': 'e36452d3', 'kx3_files': 'e3ddc014', 'harness_tag_commit': '712593a1',
                 'harness_subtree': '636ccfd4b98588b9dccfd9c631d3aa734163a738', 'c1': '30ac8703604a4d6db3d2540aea0cfa4a0f244ff7', 'c2': '07f8aa8d31b4b53a338d4332dc095a45ed189367',
                 'c3': '9fbd8cadba08767558280862441f94d5518e2b6f', 'kx_tree': '34fef9e536e9ff6c1cc6ba2ae440e5b17941b858', 'lib_tree': '65058095aaafdbcbddf67a0f4da4276d1d594c14'},
        'engine_tree': git_tree(repo, 'engine'), 'lib_tree': git_tree(repo, 'lib'), 'rustc': rustc_version(), 'information_model': 'closed-counts-unpriced-v8',
        'game_path': game_path(), 'deviations': [{'id': i, 'from': f, 'text': t, 'source': s} for i, f, s, t in DEVIATIONS], 'kit': kit,
        'kx3': {'code': game_kit.KX3_CODE, 'canonical': game_kit.KX3_CANONICAL, 'pool_sha256': game_kit.POOL_SHA256,
                'kx_params': "code kx3_r16_c12_z2_real_t0; knowledge REALISTIC with the pool's 8 meta lists; extra_lists []",
                'record_program': '23d8a9b5: kx3\'s six files on main-affe56e\'s engine, engine tree cd970db6', 'selfcheck_pin': SELFCHECK_PIN, 'selfcheck_checked': None,
                'rayon_threads': {'laptop_runs': 8, 'build_job': 2},
                'thread_identity': ('Oct 30: the same game at 2 and at 8 threads chose identical moves (24/24); the thread count changes speed, not choices. '
                                    'Gate 4a runs the protocol side at 8 threads and the in-engine side at 2.')},
        'source_sha256': src, 'outside_clone': sorted(outside), 'binaries_sha256': bins,
    }
    return rec, problems


def flat(x, prefix=''):
    out = {}
    if isinstance(x, dict):
        for k, v in x.items():
            out.update(flat(v, prefix + '.' + str(k) if prefix else str(k)))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out.update(flat(v, '%s[%d]' % (prefix, i)))
    else:
        out[prefix] = x
    return out


def cmd_record(a):
    rec, problems = compute(a.repo, a.engine_bins, a.judge_bins, a.draft)
    if problems:
        for p in problems:
            print('RECORD: ' + p)
        return 2
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(rec, f, indent=1, sort_keys=True)
        f.write('\n')
    print('recorded %s (draft=%s), %d sources' % (a.out, rec['draft'], len(rec['source_sha256'])))
    return 0


def cmd_check(a):
    repo = a.repo
    path = a.frozen or os.path.join(repo, 'rl', 'ai_judge', 'FROZEN8.json')
    with open(path, encoding='utf-8') as f:
        old = json.load(f)
    diffs = []
    fz = load_frozen7(repo)
    keys = [k for k in fz['source_sha256'] if not k.endswith(MAIN_RS_SUFFIX)]
    outside = [k for k in keys if is_outside(k)]
    inside = [k for k in keys if not is_outside(k)]
    print('outside clone: %d keys (laptop-checked)' % len(outside))
    bad, ok = [], 0
    for k in inside:
        rel = resolve(repo, k)
        if rel is None:
            bad.append('  %s MISSING' % k)
            continue
        now = sha256_file(os.path.join(repo, rel))
        if now == fz['source_sha256'][k]:
            ok += 1
        else:
            bad.append('  %s recorded %s now %s' % (k, fz['source_sha256'][k][:16], now[:16]))
    print('FROZEN7 SOURCES: %d/%d equal' % (ok, len(inside)))
    for b in bad:
        print(b)
    diffs += bad
    for k in fz['source_sha256']:
        if k.endswith(MAIN_RS_SUFFIX):
            print('skipped: %s (expected to change)' % k)
    new, problems = compute(repo, a.engine_bins, a.judge_bins, bool(old.get('draft')))
    for p in problems:
        print('  diff problem: ' + p)
        diffs.append(p)
    new['frozen_on'] = old.get('frozen_on')
    try:
        new['supersedes'][0]['commit'] = old['supersedes'][0].get('commit')
    except (KeyError, IndexError, TypeError):
        pass
    new['kx3']['selfcheck_checked'] = old.get('kx3', {}).get('selfcheck_checked')
    fo, fn = flat(old), flat(new)
    for k in sorted(set(fo) | set(fn)):
        if fo.get(k, '<absent>') != fn.get(k, '<absent>'):
            line = '  diff %s: recorded %s | now %s' % (k, str(fo.get(k, '<absent>'))[:80], str(fn.get(k, '<absent>'))[:80])
            print(line)
            diffs.append(line)
    extra = []
    if new['engine_tree'] != new['base']['kx_tree']:
        extra.append('engine_tree %s != base.kx_tree' % new['engine_tree'])
    if new['lib_tree'] != new['base']['lib_tree']:
        extra.append('lib_tree %s != base.lib_tree' % new['lib_tree'])
    if providers.VERTEX_FROZEN != VERTEX_FROZEN_EXPECT:
        extra.append('providers.VERTEX_FROZEN differs')
    if judge.COMPACT_ABOVE != 80:
        extra.append('judge.COMPACT_ABOVE is not 80')
    for n in game_kit.FORBIDDEN_ENV:
        if n in os.environ:
            extra.append('forbidden environment name set: ' + n)
    for e in extra:
        print('  check: ' + e)
    diffs += extra
    laptop_null = old.get('frozen_on') is None or (old.get('supersedes') or [{}])[0].get('commit') is None or old.get('kx3', {}).get('selfcheck_checked') is None
    if diffs:
        print('GATE5 FAIL')
        return 1
    if old.get('draft') or laptop_null:
        print('GATE5 DRAFT')
        return 3
    print('GATE5 PASS')
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(prog='freeze8')
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('record', 'check'):
        s = sub.add_parser(name)
        if name == 'record':
            s.add_argument('--out', required=True)
            s.add_argument('--draft', action='store_true')
        else:
            s.add_argument('--frozen')
        s.add_argument('--engine-bins', default=DEFAULT_ENGINE_BINS)
        s.add_argument('--judge-bins', default=DEFAULT_JUDGE_BINS)
        s.add_argument('--repo', default=os.path.abspath(os.path.join(HERE, '..', '..')))
    a = p.parse_args(argv)
    return cmd_record(a) if a.cmd == 'record' else cmd_check(a)


if __name__ == '__main__':
    sys.exit(main())
