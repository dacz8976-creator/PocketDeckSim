You are filling in a short fact sheet about the OPPONENT in one recorded Pokémon TCG Pocket ranked game. Dustin recorded it on his phone. This is a quick pass: the sheet feeds a tracker of which decks Dustin meets. You are not writing a full review.

## Your files
- Overview sheets: `frames/sheets/sheet_from_0000s.jpg`,`frames/sheets/sheet_from_0018s.jpg`,`frames/sheets/sheet_from_0036s.jpg`,`frames/sheets/sheet_from_0054s.jpg`,`frames/sheets/sheet_from_0072s.jpg`,`frames/sheets/sheet_from_0090s.jpg`,`frames/sheets/sheet_from_0108s.jpg`,`frames/sheets/sheet_from_0126s.jpg`,`frames/sheets/sheet_from_0144s.jpg`,`frames/sheets/sheet_from_0162s.jpg`,`frames/sheets/sheet_from_0180s.jpg`,`frames/sheets/sheet_from_0198s.jpg`,`frames/sheets/sheet_from_0216s.jpg`,`frames/sheets/sheet_from_0234s.jpg`. Each holds 18 frames, one per second, 6 across and 3 down, read left to right, top to bottom. The first frame is the second in the sheet's name.
- Full-resolution frames: `frames/full/t_SSSS.jpg`, one per second, four digits. Second 75 is `frames/full/t_0075.jpg`.
- Do not open `source.mp4`, and do not open any other folder.

## Procedure
1. Open every overview sheet once, in order.
2. Find these moments, then open the full-resolution frame at each one to read names and numbers. Open 30 full-resolution frames at most.
   - who goes first;
   - the opponent's Energy Zone type icon;
   - each opponent Pokémon when it first appears: read its name;
   - every attack the opponent makes: read the attack name and damage;
   - every Knock Out and point award;
   - the result screen: Victory or Defeat, points, and any statistics or card of the game.
3. Watch the opponent's Pokémon for the Energy icons they attach (type), and note which Trainer cards they play when the card is shown full-screen.

## Rules
- Only what the frames show. The opponent's hand is face down, so never guess it.
- Use exact card names, keeping "ex", "Mega", "Alolan" and "Team Rocket's".
- Use `null` or empty lists for anything not shown.

## Output
Your output file `OPPONENT.json` already exists in your output folder with a placeholder line. Replace that line, using Edit, with:

```json
{"recording": "ScreenRecording_10-24-2026 12-51-31_1.mp4", "went_first": "dustin|opponent", "global_turns": 0, "final_score": {"dustin": 0, "opponent": 0},
 "end": "points|no_pokemon|deck_out|concede_dustin|concede_opponent|timeout_dustin|timeout_opponent",
 "opponent_energy_zone": [], "opponent_energy_attached": [{"turn": 0, "type": "", "to": ""}],
 "opponent_pokemon": [{"name": "", "set_number": null, "first_seen_turn": 0, "attacked": false, "attacks_used": [], "abilities_used": [], "points_taken": 0}],
 "opponent_trainers": [{"turn": 0, "name": ""}], "opponent_effects": {"special_conditions": [], "healed": false, "bench_damage": false},
 "opponent_card_of_the_game": null, "notes": ""}
```

Don't include the opponent's player name. Reply with the number of full-resolution frames you opened.
