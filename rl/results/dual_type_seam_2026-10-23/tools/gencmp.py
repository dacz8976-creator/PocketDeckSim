#!/usr/bin/env python3
"""Compare a committed generated file with card_enum_generator's raw output, modulo what `cargo fmt` changes.

usage: gencmp.py COMMITTED GENERATED [--drop-secondary]

No rustfmt on this laptop, so the generator's raw text is compared after the same normalisation on both sides:
CR and all whitespace removed, a comma right before a closing ] ) } removed (rustfmt drops trailing commas on one-line
lists), and the `use` lines compared as a sorted set (rustfmt sorts them). --drop-secondary also removes every
`secondary_energy_type:None,` from both sides, to compare the cards themselves with main's file.
Prints SAME or the first difference with context."""
import re, sys

def norm(path, drop_secondary):
    text = open(path, encoding='utf-8').read().replace('\r', '')
    uses = sorted(l.strip() for l in text.split('\n') if l.startswith('use '))
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('use '))
    body = re.sub(r'\s+', '', body)
    body = re.sub(r',(?=[\]\)\}])', '', body)
    if drop_secondary:
        body = body.replace('secondary_energy_type:None,', '')
    return uses, body

a_path, b_path = sys.argv[1], sys.argv[2]
drop = '--drop-secondary' in sys.argv
(ua, a), (ub, b) = norm(a_path, drop), norm(b_path, drop)
ok = True
if ua != ub:
    ok = False
    print('use lines differ:', sorted(set(ua) ^ set(ub)))
if a != b:
    ok = False
    i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
    print(f'body differs at char {i} (lengths {len(a)} v {len(b)}):\n  committed: ...{a[max(0, i - 80):i + 80]}\n  generated: ...{b[max(0, i - 80):i + 80]}')
n = open(b_path, encoding='utf-8').read().count('secondary_energy_type: None,')
print(('SAME' if ok else 'DIFFERS') + f' ({a_path} v {b_path}{", secondary lines dropped" if drop else ""}); generated secondary_energy_type None lines: {n}')
