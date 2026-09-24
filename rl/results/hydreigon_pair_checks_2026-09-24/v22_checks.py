#!/usr/bin/env python3
"""Chosen-matchup v2.2 audit, with explicit skip counts and reproducible feature rows.

Extends the historical v2_2_checks coverage to every offered action and four
chance streams. This is a sampled count/loss-flag audit, not proof of all point,
win, or chance forecasts. Focused Rust fixtures check delayed knockout scoring.
The main game never restores snapshots, so probes do not alter its chance stream.

PocketDeckSim copy (Sept 24) of Astra's Sept 22 script, for Hydreigon v Lucario.
Changed only: default decks (repo root = folder holding project_manifest.json),
default --seed 21,000,200,000 (was 6,000,000) and a default new output folder.
Checks and the pass criterion are unchanged.
"""
from __future__ import annotations
import argparse
import collections
import gzip
import hashlib
import importlib.metadata
import json
import random
import struct
import sys
import time
from pathlib import Path
import pdl_rl_env
from pdl_rl_env import RawEnv

SEED0 = 21_000_200_000
DECK_A = ('decks/research/hydreigon.txt', '6ea0042236b4844458a1b2d0f0e6cefb4c50ce0148a38aded1162f4d27e935e9')
DECK_B = ('decks/research/lucario.txt', '46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3')
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def find_root():
    for parent in HERE.parents:
        if (parent / 'project_manifest.json').is_file() and (parent / 'lib' / 'deckgym-database.json').is_file():
            return parent
    raise RuntimeError('could not locate project root')


def floats(blob):
    return struct.unpack('<' + 'f' * (len(blob) // 4), blob)


def action_kind(raw):
    value = json.loads(raw)
    return value if isinstance(value, str) else next(iter(value))


def ko_points(name):
    return 3 if name.startswith('Mega ') else 2 if name.endswith(' ex') else 1


def main():
    root = find_root()
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    ap = argparse.ArgumentParser()
    ap.add_argument('--deck-a', type=Path, default=root / DECK_A[0])
    ap.add_argument('--deck-b', type=Path, default=root / DECK_B[0])
    ap.add_argument('--output', type=Path, default=HERE / f'hydreigon-lucario-v22-072-{stamp}')
    ap.add_argument('--games', type=int, default=20)
    ap.add_argument('--seed', type=int, default=SEED0)
    args = ap.parse_args()
    if args.games < 1:
        ap.error('--games must be positive')
    for path, (rel, expected) in ((args.deck_a, DECK_A), (args.deck_b, DECK_B)):
        if path.resolve() == (root / rel).resolve() and sha(path) != expected:
            ap.error(f'{rel} has changed: its SHA-256 is no longer {expected}')
    args.output.mkdir(parents=True, exist_ok=False)
    decks = [args.deck_a.resolve(), args.deck_b.resolve()]
    print(f'v2.2 seeds: {args.seed:,} to {args.seed + args.games - 1:,}; decks '
          + ', '.join(f'{p.name} {sha(p)[:16]}' for p in decks) + f'. Output: {args.output}', flush=True)
    ids = sorted({i for p in decks for i in RawEnv.deck_card_ids(str(p))})
    env, old, trial = RawEnv(ids, 'v2.2'), RawEnv(ids, 'v2.1'), RawEnv(ids, 'v2.2')
    assert env.obs_dim == old.obs_dim and env.action_dim == old.action_dim + 1
    module = Path(pdl_rl_env.__file__).resolve()
    extensions = [module] if module.suffix == '.so' else sorted(module.parent.glob('*.so'))
    identity = {'schema': 1, 'addon_version': importlib.metadata.version('pdl_rl_env'),
                'python': sys.executable, 'module': str(module), 'module_sha256': sha(module),
                'extensions': {str(p): sha(p) for p in extensions},
                'decks': {str(p): sha(p) for p in decks}, 'script_sha256': sha(__file__),
                'vocab': ids, 'games': args.games, 'seed': args.seed,
                'observation_dim': env.obs_dim, 'action_dim': env.action_dim,
                'chance_seeds_per_action': [0x5eed_0000 + i for i in range(4)],
                'diagnostics_available': hasattr(env, 'forecast_diagnostics')}
    (args.output / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    totals, by_kind, errors = collections.Counter(), collections.defaultdict(collections.Counter), []
    started = time.monotonic()
    def count(kind, reason):
        totals[reason] += 1
        by_kind[kind][reason] += 1
    def fail(kind, reason, evidence):
        count(kind, reason)
        if len(errors) < 30:
            errors.append(evidence)
    with gzip.open(args.output / 'features.jsonl.gz', 'wt', encoding='utf-8') as features, (args.output / 'games.jsonl').open('w') as games:
        for g in range(args.games):
            order = decks if g % 2 == 0 else decks[::-1]
            for e in (env, old, trial):
                e.reset(str(order[0]), str(order[1]), args.seed + g, None)
            chooser = random.Random(100 + g)
            decision = 0
            while not env.done:
                assert not old.done and env.decision_fingerprint() == old.decision_fingerprint()
                me = env.current_player
                acts = env.legal_actions_json()
                assert acts == old.legal_actions_json()
                blob, b21 = env.action_features(), old.action_features()
                obs_blob = env.observe(me)
                assert obs_blob == old.observe(me)
                rr, r21 = floats(blob), floats(b21)
                base, base21 = env.action_dim - 17, old.action_dim - 16
                assert base == base21 and len(rr) == len(acts) * env.action_dim
                before = json.loads(env.describe(me))
                board_before = before['me']['board']
                n_before = sum(x is not None for x in board_before)
                active_before = board_before[0]
                snapshot = env.snapshot()
                diagnostics = None
                if hasattr(env, 'forecast_diagnostics'):
                    diagnostics = env.forecast_diagnostics()
                    if isinstance(diagnostics, str):
                        diagnostics = json.loads(diagnostics)
                    elif isinstance(diagnostics, list):
                        diagnostics = [json.loads(d) if isinstance(d, str) else d for d in diagnostics]
                features.write(json.dumps({'game': g, 'seed': args.seed + g, 'decision': decision,
                    'fingerprint': list(env.decision_fingerprint()), 'actor': me, 'actions': acts,
                    'observe_hex': obs_blob.hex(), 'features_hex': blob.hex(), 'diagnostics': diagnostics}, sort_keys=True) + '\n')
                for i, raw in enumerate(acts):
                    kind = action_kind(raw)
                    row = rr[i * env.action_dim:(i + 1) * env.action_dim]
                    previous = r21[i * old.action_dim:(i + 1) * old.action_dim]
                    count(kind, 'offered')
                    if row[:base + 13] != previous[:base21 + 13] or row[base + 15:base + 17] != previous[base21 + 14:base21 + 16]:
                        fail(kind, 'layout_wrong', {'game': g, 'decision': decision, 'action': raw})
                    else:
                        count(kind, 'layout_checked')
                    if row[base] < 0.5:
                        count(kind, 'count_skip_unpriced')
                        count(kind, 'flag_skip_unpriced')
                        continue
                    if row[base + 6] > 0:
                        count(kind, 'count_skip_self_damage')
                    else:
                        want = n_before + int(kind == 'Place')
                        count(kind, 'count_checked')
                        if abs(row[base + 13] * 4 - want) > 1e-4:
                            fail(kind, 'count_wrong', {'game': g, 'decision': decision, 'action': raw,
                                'got': row[base + 13] * 4, 'expected': want})
                    outcomes = []
                    for chance in range(4):
                        trial.restore(snapshot, 0x5eed_0000 + chance)
                        assert trial.legal_actions_json() == acts
                        trial.step(i)
                        if trial.done:
                            outcomes.append(('ended', None))
                        elif floats(trial.observe(trial.current_player))[11] > 0.5:
                            outcomes.append(('pending_choice', None))
                        else:
                            after = json.loads(trial.describe(me))
                            board = after['me']['board']
                            active = board[0]
                            if (active_before or {}).get('name') != (active or {}).get('name'):
                                outcomes.append(('changed_active', None))
                            else:
                                in_play = sum(x is not None for x in board)
                                lose = in_play <= 1 or after['them']['points'] + ko_points(active['name']) >= 3
                                outcomes.append(('eligible', int(lose)))
                    reasons = {x[0] for x in outcomes}
                    if reasons != {'eligible'}:
                        reason = next(iter(reasons)) if len(reasons) == 1 else 'mixed_chance_boundaries'
                        count(kind, 'flag_skip_' + reason)
                    elif len({x[1] for x in outcomes}) != 1:
                        count(kind, 'flag_skip_chance_variation')
                    else:
                        count(kind, 'flag_checked')
                        if abs(row[base + 14] - outcomes[0][1]) > 1e-4:
                            fail(kind, 'flag_wrong', {'game': g, 'decision': decision, 'action': raw,
                                'got': row[base + 14], 'expected': outcomes[0][1]})
                chosen = chooser.randrange(len(acts))
                env.step(chosen)
                old.step(chosen)
                decision += 1
                if decision > 2000:
                    raise RuntimeError('unexpected decision count')
            assert old.done and env.final_state_hash() == old.final_state_hash() and env.result() == old.result()
            games.write(json.dumps({'game': g, 'seed': args.seed + g, 'decks': [str(p) for p in order],
                                   'decisions': decision, 'result': env.result(), 'final_state_hash': env.final_state_hash()}) + '\n')
            games.flush()
            print(f'v2.2: {g + 1}/{args.games} games, {totals["offered"]} rows, {len(errors)} retained errors', flush=True)
    assert all(sha(p) == h for p, h in identity['decks'].items())
    summary = {'identity': identity, 'elapsed_seconds': time.monotonic() - started,
               'totals': dict(totals), 'by_action_kind': {k: dict(v) for k, v in sorted(by_kind.items())},
               'examples': errors, 'passed': not errors,
               'scope': 'All offered moves; four sampled chance streams for eligible loss flags. Terminal, pending, changed-active and stochastic boundaries explicitly skipped. This audit does not validate every points/win forecast.'}
    (args.output / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'passed': summary['passed'], 'totals': dict(totals)}), flush=True)
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
