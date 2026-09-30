#!/usr/bin/env python3
"""Run decks/screen/run_screen.py, unchanged, on a named deckgym instead of the manifest's release (prepare.sh step 7).

usage: screen_with.py DECKGYM SHA256 RUN_SCREEN.py [run_screen arguments ...]

run_screen.py takes its program from current_engine.resolve(), which returns only the manifest's release (an --engine
override must have the release's hash, and the release is what runs). Before the pin, the new program is not in the
manifest and the manifest is not touched. So this wrapper checks DECKGYM's sha256 against SHA256 (the pin prepare.sh
recorded in step 1), puts a stand-in current_engine module whose resolve() returns DECKGYM in sys.modules, and runs
run_screen.py as __main__: the screen's own code (seeds, seats, pilots, panel, printing), with the new program.
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


def resolve(project=None, override=None):
    if override is not None:
        raise ValueError("screen_with.py names the program itself; do not pass --engine")
    return path


stand_in = types.ModuleType("current_engine")
stand_in.resolve = resolve
sys.modules["current_engine"] = stand_in
sys.argv = [script] + sys.argv[4:]
runpy.run_path(script, run_name="__main__")
