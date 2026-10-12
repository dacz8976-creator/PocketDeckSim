#!/usr/bin/env python3
"""Run decks/screen/floor.py, unchanged, on a named deckgym instead of the manifest's release (sitting1.sh step 7c).

usage: floor_with.py DECKGYM SHA256 FLOOR.py [floor.py arguments ...]

floor.py takes its program from current_engine.resolve(), which returns only the manifest's release. Before the pin, the
new program is not in the manifest and the manifest is not touched. So, as ../engine_switch_2026-09-30/screen_with.py
does for run_screen.py, this wrapper checks DECKGYM's sha256 against SHA256 (the pin sitting1.sh recorded in step 5),
puts a stand-in current_engine module whose resolve() returns DECKGYM in sys.modules, and runs floor.py as __main__:
floor.py's own call (deckgym simulate --seed-stream, its seeds, seats, pilots, panel, traces and records), with the new
program. Everything else floor.py reads is its own: the manifest's goldfish for the coverage, the opponents, the
database. Its page names the program it ran in the "- Engine:" line; that line is the only one that differs by design.
"""
import hashlib, os, runpy, sys, types
from pathlib import Path

if len(sys.argv) < 4:
    sys.exit(__doc__)
gym, pin, script = sys.argv[1], sys.argv[2], sys.argv[3]
path = Path(gym).resolve(strict=True)
got = hashlib.sha256(path.read_bytes()).hexdigest()
if got != pin or not os.access(path, os.X_OK):
    sys.exit(f"REFUSED: {path} has sha256 {got}, not the pin {pin} (or is not executable)")
if any(a == "--goldfish" or a.startswith("--goldfish=") for a in sys.argv[4:]):
    sys.exit("REFUSED: floor_with.py replays floor.py's own call; it takes no --goldfish")


def resolve(project=None, override=None):
    if override is not None:
        raise ValueError("floor_with.py names the program itself; no override")
    return path


stand_in = types.ModuleType("current_engine")
stand_in.resolve = resolve
sys.modules["current_engine"] = stand_in
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
