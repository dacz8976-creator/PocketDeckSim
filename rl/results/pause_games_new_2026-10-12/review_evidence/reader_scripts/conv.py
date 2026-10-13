# load the converter's functions without importing it as a module (no __pycache__ written in the repo)
import sys
sys.dont_write_bytecode = True
SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py'
C = {'__name__': 'conv_review'}
exec(compile(open(SRC, encoding='utf-8').read(), SRC, 'exec'), C)
