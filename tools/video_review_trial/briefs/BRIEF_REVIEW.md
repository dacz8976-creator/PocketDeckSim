You are reviewing one recorded ranked game of Pokémon TCG Pocket. The player who recorded it, "the owner", is Dustin, and the game was played on his phone. Your review is the written record of the game. Other people will rely on it without watching the video, so it must be accurate and complete.

## What you have (your working folder)
- `frames/sheets/sheet_from_NNNNs.jpg`: overview contact sheets. Each holds 18 seconds, at one frame per second, 6 across by 3 down. NNNN is the second the sheet starts at.
- `frames/half/t_SSSS.S.jpg`: two frames per second at half resolution. The name is the second.
- `frames/full/t_SSSS.jpg`: one frame per second at full resolution. Use these to read HP, damage numbers, card text and small icons.
- Do not open `source.mp4`. Use the frames.

## How to work
1. Look through the overview sheets first and map the whole game: the deck QR or deck selection, who goes first, where each turn starts and ends, attacks, Knock Outs, points and the result screen.
2. Then go turn by turn. Use the half-resolution frames to follow the actions, and full-resolution frames wherever you need to read a number, a card name or card text.
3. You can't open every frame, and you shouldn't. Open what each claim needs. Read the numbers at the moments that matter: after damage, after a heal, after an Energy attachment, after a Knock Out.

## Rules
- **Only what the frames show.** The opponent's hand and deck are hidden. Never fill them in or guess what they "probably" have. Say "not shown" instead.
- **Every key fact gets a timestamp:** every attack, every damage number, every HP change, every Knock Out and every point award. Use the frame file's second.
- **Exact card names,** keeping "ex", "Mega", "Alolan" and "Team Rocket's". Distinguish two Pokémon with the same name by place (Active or Bench) and by HP.
- **When the frames don't settle something, say so** and add it to `UNCERTAINTIES.md`. A clearly labelled gap is better than a guess.

## Write three files to your output folder
**REVIEW.md** has:
- **A header:** the deck name or QR shown, who went first, the final score, how the game ended (points, no Pokémon left, deck out, concession, timeout), the number of global turns, and the result screen's statistics if it shows them.
- **Opening:** the owner's opening hand (all cards visible), the Active and Bench each player sets up, and each player's Energy Zone type(s) as shown on screen.
- **One section per global turn** ("global 1" is the first turn of the game), titled with whose turn it is and its time range. In order, with timestamps:
  - the owner's draw;
  - every card played: Supporters, Items, Tools, Stadiums, Pokémon benched or evolved;
  - every Energy attached: type, to which Pokémon, and from the Energy Zone or by an effect;
  - retreats, Ability uses, attacks (name, coin flips, damage), HP before → after, Special Conditions, Knock Outs, points and the score after.
  - End each section with a one-line board state: both Actives and Benches with HP, Energy, Tools and conditions.
- **The owner's hand at the start of each of his turns,** when the screen shows it.

**OPPONENT.json:**

```json
{"recording": "...", "went_first": "dustin|opponent", "global_turns": 0, "final_score": {"dustin": 0, "opponent": 0},
 "end": "points|no_pokemon|deck_out|concede_dustin|concede_opponent|timeout_dustin|timeout_opponent",
 "opponent_energy_zone": [], "opponent_energy_attached": [{"turn": 0, "type": "", "to": ""}],
 "opponent_pokemon": [{"name": "", "set_number": null, "first_seen_turn": 0, "attacked": false, "attacks_used": [], "abilities_used": [], "points_taken": 0}],
 "opponent_trainers": [{"turn": 0, "name": ""}], "opponent_effects": {"special_conditions": [], "healed": false, "bench_damage": false},
 "opponent_card_of_the_game": null, "notes": ""}
```

Use `null` or empty lists where something isn't shown. No opponent player name.

**UNCERTAINTIES.md:** each unsettled point, with its turn, its timestamps and what would settle it.

When you finish, reply with one paragraph: the result, the number of turns, and how many uncertainties you listed.
