#!/usr/bin/env python3
"""Writes the positions a pilot may be run on to stdout: every position outside the held-out games, and the held-out ones only when the lock file
says `locked: false` AND --include-heldout is given. usage: filter_positions.py POSITIONS.json LOCK.json [--include-heldout]"""
import json, sys

positions = json.load(open(sys.argv[1], encoding='utf-8'))
lock = json.load(open(sys.argv[2], encoding='utf-8'))
include = '--include-heldout' in sys.argv
if include and lock.get('locked', True):
    sys.exit('REFUSED: the held-out positions are locked (positions_heldout.json says locked: true). No development pilot is run on them until the laptop Opus or the coordinator says so.')
out = [p for p in positions if include or not p.get('heldout')]
sys.stderr.write(f"{len(out)} of {len(positions)} positions ({len(positions) - len(out)} held out, lock {'on' if lock.get('locked', True) else 'off'})\n")
json.dump(out, sys.stdout, ensure_ascii=False)
