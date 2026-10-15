"""Dry runs of the two 13-A variants against the base folder (no game is played, nothing is written)."""
import contextlib, io, json, os, subprocess, sys
from unittest import mock
REPO = '/home/dacz8976/pgfix'
sys.path.insert(0, f'{REPO}/rl/strength')
import slow_report as sr
BASE = 'rl/results/slow_reports/2026-10-12_13-a-ninetales-raticate'
base_sha = json.load(open(f'{REPO}/{BASE}/manifest.json'))['program_sha256']
os.chdir(REPO)
def dry(variant, patch_program):
    argv = ['--paired-with', BASE, '--deck', f'decks/variants-2026-10-15/{variant}.txt', '--dry-run', '--date', '2026-10-16']
    out = io.StringIO()
    code = None
    cm = mock.patch.object(sr, 'check_program', lambda pin, program=None, repo=None: ('pinned', base_sha)) if patch_program else contextlib.nullcontext()
    with cm, contextlib.redirect_stdout(out):
        try:
            code = sr.main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue()
for patched in (False, True):
    print('=' * 100)
    print('ON THIS LAPTOP (the pinned program 76df495b is the only one here)' if not patched else
          'AS ON THE CLOUD RUNNER (the program check answered with the base report\'s own program, 5011e227cf63, by a throwaway patch of check_program; every other check is real)')
    for v in ('13-a-giant-cape', '13-a-big-malasada'):
        code, out = dry(v, patched)
        print('-' * 100)
        print(f'$ python3 rl/strength/slow_report.py --paired-with {BASE} --deck decks/variants-2026-10-15/{v}.txt --dry-run')
        print(out.rstrip())
        print(f'exit: {code if isinstance(code, int) else "REFUSED"}')
        if not isinstance(code, int) and code:
            print(str(code))
