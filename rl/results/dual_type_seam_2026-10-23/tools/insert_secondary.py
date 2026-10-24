#!/usr/bin/env python3
"""Add `secondary_energy_type: None,` after every generated `energy_type:` line of engine/src/database.rs,
byte-exact (same indentation, same CRLF ending), the way the updated card_enum_generator emits it.
The night build re-runs the generator and checks the committed file equals its output.
usage: insert_secondary.py PATH_TO_database.rs"""
import re, sys

p = sys.argv[1]
b = open(p, 'rb').read()
if b'secondary_energy_type' in b:
    sys.exit('refusing: the file already has secondary_energy_type lines')
pat = re.compile(rb'^( +)energy_type: EnergyType::[A-Za-z]+,(\r?\n)', re.M)
n = 0


def add(m):
    global n
    n += 1
    return m.group(0) + m.group(1) + b'secondary_energy_type: None,' + m.group(2)


out = pat.sub(add, b)
open(p, 'wb').write(out)
print(f'inserted {n} lines')
