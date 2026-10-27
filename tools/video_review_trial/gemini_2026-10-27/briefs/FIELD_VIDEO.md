You are filling in a short fact sheet about the OPPONENT in one recorded Pokémon TCG Pocket ranked game. The video above is the screen recording; Dustin recorded it on his phone. This is a quick pass: the sheet feeds a tracker of which decks Dustin meets. You are not writing a full review.

## What to find
- who goes first;
- the opponent's Energy Zone type icon;
- each opponent Pokémon when it first appears, by name;
- every attack the opponent makes: the attack name and damage;
- every Knock Out and point award;
- the result screen: Victory or Defeat, points, and any statistics or card of the game;
- the Energy types the opponent attaches, and the Trainer cards they play when the card is shown full-screen.

## Rules
- Only what the video shows. The opponent's hand is face down, so never guess it.
- Use exact card names, keeping "ex", "Mega", "Alolan" and "Team Rocket's".
- Use `null` or empty lists for anything not shown.

## Your answer
Only this JSON object, filled in, with no other text:
```json
{"recording": "<RECORDING>", "went_first": "dustin|opponent", "global_turns": 0, "final_score": {"dustin": 0, "opponent": 0},
 "end": "points|no_pokemon|deck_out|concede_dustin|concede_opponent|timeout_dustin|timeout_opponent",
 "opponent_energy_zone": [], "opponent_energy_attached": [{"turn": 0, "type": "", "to": ""}],
 "opponent_pokemon": [{"name": "", "set_number": null, "first_seen_turn": 0, "attacked": false, "attacks_used": [], "abilities_used": [], "points_taken": 0}],
 "opponent_trainers": [{"turn": 0, "name": ""}], "opponent_effects": {"special_conditions": [], "healed": false, "bench_damage": false},
 "opponent_card_of_the_game": null, "notes": ""}
```
Leave out the opponent's player name.
