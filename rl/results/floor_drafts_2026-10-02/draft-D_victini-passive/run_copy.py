"""Run the private copy of floor.py as if it sat where the committed one does.

    python3 run_copy.py COPY.py REPO/decks/screen/floor.py <floor.py's arguments>

floor.py finds the repository (ROOT), the panel (decks/screen/opponents) and lib/ from its own __file__. The copy lives
outside the repository, so this runs the copy's code with __file__ set to the committed file's path. Nothing else changes:
the code that runs is the copy's, byte for byte.
"""
import sys

copy, real = sys.argv[1], sys.argv[2]
sys.argv = [real] + sys.argv[3:]
code = compile(open(copy, encoding="utf-8").read(), copy, "exec")
exec(code, {"__name__": "__main__", "__file__": real, "__builtins__": __builtins__})
