#!/usr/bin/env python3
"""Plain readout for the Altaria v Lucario pair checks (copy of the Hydreigon readout, Sept 25).

Usage: readout.py INTERFACE_DIR V22_DIR PARITY_DIR

Reads the three output folders and says PASSED only if every check passed AND
each run used the full sizes, the default seeds, the Altaria/Lucario decks
and add-on module 0fee43ce... (a shrunken run or the wrong venv prints FAIL).
The three check scripts are not changed by this; it only reads their files.
"""
import json
import sys
from pathlib import Path

MODULE = '0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101'
ENGINE = 'e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415'
ALT = '435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f'
LUC = '46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3'
CASES = ['altaria-lucario-k2-k3', 'altaria-lucario-k3-k3', 'blaziken-lucario-k2-k3',
         'blaziken-lucario-k3-k3', 'suicune-altaria-k2-k3', 'suicune-altaria-k3-k3',
         'weezing-lucario-k2-k3', 'weezing-lucario-k3-k3']


def load(folder, name):
    return json.loads((Path(folder) / name).read_text(encoding='utf-8'))


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    a, ai = load(sys.argv[1], 'summary.json'), load(sys.argv[1], 'input_identity.json')
    b = load(sys.argv[2], 'summary.json')
    c, ci = load(sys.argv[3], 'summary.json'), load(sys.argv[3], 'input_identity.json')
    checks = [
        ('Interface C1+C2 passed', a['pass'] is True),
        ('C1 ran 100 k3 replays (50 seeds)', a['c1']['k3_replays_expected'] == 100),
        ('C2 ran 100 hidden-card games', a['c2']['games_expected'] == 100),
        ('C1/C2 used seeds 21,101,000,000 / 21,101,100,000',
         (ai['seeds']['c1_start'], ai['seeds']['c2_start']) == (21_101_000_000, 21_101_100_000)),
        ('C1/C2 used v2.2 features', a['features'] == 'v2.2'),
        ('C1/C2 used Altaria + Lucario', (ai['deck_a']['sha256'], ai['deck_b']['sha256']) == (ALT, LUC)),
        ('C1/C2 used add-on module 0fee43ce', ai['module_sha256'] == MODULE),
        ('v2.2 check passed', b['passed'] is True),
        ('v2.2 ran 20 games', b['identity']['games'] == 20),
        ('v2.2 used seed 21,101,200,000', b['identity']['seed'] == 21_101_200_000),
        ('v2.2 used Altaria + Lucario', sorted(b['identity']['decks'].values()) == sorted([ALT, LUC])),
        ('v2.2 used add-on module 0fee43ce', b['identity']['module_sha256'] == MODULE),
        ('CLI/add-on parity passed', c['status'] == 'passed'),
        ('Parity ran all 8 cases', [x['case'] for x in ci['cases']] == CASES),
        ('Parity used seeds 21,101,300,000-001', ci['seeds'] == [21_101_300_000, 21_101_300_001]),
        ('Parity 16 of 16 games matched',
         (c['games_expected'], c['games_recorded'], c['games_matched']) == (16, 16, 16)),
        ('Parity used engine e6593ed8 and module 0fee43ce',
         (ci['engine_sha256'], ci['module_sha256']) == (ENGINE, MODULE)),
    ]
    for label, ok in checks:
        print(('OK    ' if ok else 'FAIL  ') + label)
    bad = sum(not ok for _, ok in checks)
    print(f'PAIR CHECKS PASSED ({len(checks)} of {len(checks)} OK)' if not bad
          else f'FAIL: {bad} of {len(checks)} readout checks failed; the Altaria run stays unread')
    return 1 if bad else 0


if __name__ == '__main__':
    raise SystemExit(main())
