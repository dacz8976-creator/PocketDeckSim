#!/usr/bin/env python3
"""The identity of a freeze: the prompt fingerprint, the hashes of every source file the judge and the baseline depend on, and the executables.

  python3 freeze_identity.py --check          compare the repository (and the built executables, when present) with FROZEN.json; exit 1 on any difference
  python3 freeze_identity.py                  print the current identity (what a new freeze would record)

Source hashes are sha256 of the file bytes as committed. The executables are checked only where they exist (a laptop without them still runs the tests).
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import judge  # noqa: E402

HARNESS = 'rl/results/pause_games_decisions_2026-10-02/harness'
SOURCES = ['rl/ai_judge/judge.py', 'rl/ai_judge/formal.py', 'rl/ai_judge/validate_baseline.py', 'rl/ai_judge/freeze_identity.py', 'rl/ai_judge/plans/src/main.rs', 'rl/ai_judge/plans/Cargo.lock',
           f'{HARNESS}/pgd_patch.py', f'{HARNESS}/dg_patch.py', f'{HARNESS}/pg_pos.rs']
PLANS_BIN = judge.PLANS_BIN
BASELINE_BIN = judge.PG_POS_BIN


def sha(path):
    return judge.file_sha256(path)


def source_hashes():
    return {p: sha(os.path.join(REPO, p)) for p in SOURCES}


def engine_tree():
    return subprocess.run(['git', '-C', REPO, 'rev-parse', 'HEAD:engine'], capture_output=True, text=True, check=True).stdout.strip()


def current():
    return {'fingerprint': judge.fingerprint(), 'settings': judge.FROZEN, 'source_sha256': source_hashes(), 'engine_tree': engine_tree()}


def check(frozen):
    """Returns a list of differences between FROZEN.json and the repository / executables."""
    diffs = []
    cur = current()
    if cur['fingerprint'] != frozen['fingerprint']:
        diffs.append('prompt fingerprint differs')
    if cur['settings'] != frozen['settings']:
        diffs.append('settings differ')
    for p, h in frozen['source_sha256'].items():
        if cur['source_sha256'].get(p) != h:
            diffs.append(f'source changed since the freeze: {p}')
    if cur['engine_tree'] != frozen['baseline']['engine_tree']:
        diffs.append(f"engine tree {cur['engine_tree'][:12]} differs from the frozen baseline's {frozen['baseline']['engine_tree'][:12]}")
    if os.path.exists(PLANS_BIN) and sha(PLANS_BIN) != frozen['plans_binary_sha256']:
        diffs.append('the plan lister executable is not the frozen one')
    if os.path.exists(BASELINE_BIN) and sha(BASELINE_BIN) != frozen['baseline']['binary_sha256']:
        diffs.append('the baseline (pg_pos) executable is not the frozen one')
    return diffs


def main():
    if '--check' in sys.argv:
        frozen = judge.frozen_identity()
        diffs = check(frozen)
        for d in diffs:
            print('DIFFERS:', d)
        print('identity matches FROZEN.json' if not diffs else f'{len(diffs)} difference(s)')
        return 1 if diffs else 0
    print(json.dumps(current(), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
