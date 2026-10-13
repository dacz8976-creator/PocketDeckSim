import json, os, glob, sys
Q = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
R = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/'
GAMES = sorted(glob.glob(Q + 'BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*_iOS'))


def short_of(g):
    return os.path.basename(g.rstrip('/')).replace('_iOS', '')[2:]


def led(g):
    return json.load(open(g + '/TURN_LEDGER.json', encoding='utf-8'))


def deck(g):
    return json.load(open(g + '/DECK_USED.json', encoding='utf-8'))


POS = json.load(open(R + 'positions_all.json', encoding='utf-8'))
POSBY = {p['id']: p for p in POS}
GBY = {short_of(g): g for g in GAMES}
