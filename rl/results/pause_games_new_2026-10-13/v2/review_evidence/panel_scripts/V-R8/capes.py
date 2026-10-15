import sys, json
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/harness")
import cardlib as C
for i, c in C.BYID.items():
    if 'HP' in str(c.get('effect') or '') and c.get('trainer_card_type') in ('Tool', 'Pokemon Tool', 'Pokémon Tool') or ('Cape' in c.get('name', '')):
        print(i, c.get('name'), c.get('trainer_card_type'), '|', c.get('effect'))
print([ (c['id'], c.get('stage'), c.get('hp'), c.get('energy_type')) for c in C.BYNAME.get('Igglybuff', [])])
print(C.BYID.get('A4a 059'))
