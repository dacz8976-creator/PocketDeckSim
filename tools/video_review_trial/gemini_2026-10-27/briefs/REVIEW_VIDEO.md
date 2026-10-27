You are reviewing one recorded ranked game of Pokémon TCG Pocket. The video above is a screen recording of the whole game. The player who recorded it, "the owner", is Dustin, and the game was played on his phone. Your review is the written record of the game. Other people will rely on it without watching the video, so it must be accurate and complete.

## How to work
1. First map the whole game: the deck QR or deck selection, who goes first, where each turn starts and ends, attacks, Knock Outs, points and the result screen.
2. Then go turn by turn. Read the numbers at the moments that matter: after damage, after a heal, after an Energy attachment, after a Knock Out.

## Rules
- **Only what the video shows.** The opponent's hand and deck are hidden. Never fill them in or guess what they "probably" have. Say "not shown" instead.
- **Every key fact gets a timestamp,** in whole seconds from the start of the video, written like `t=75s`. That covers every attack, every damage number, every HP change, every Knock Out and every point award.
- **Exact card names,** keeping "ex", "Mega", "Alolan" and "Team Rocket's". Distinguish two Pokémon with the same name by place (Active or Bench) and by HP.
- **When the video doesn't settle something, say so,** and list it under UNCERTAINTIES. A clearly labelled gap is better than a guess.

## Your answer: three sections, each starting with its marker line exactly as shown

`=== REVIEW.md ===`
- **A header:** the deck name or QR shown, who went first, the final score, how the game ended (points, no Pokémon left, deck out, concession, timeout), the number of global turns, and the result screen's statistics if it shows them.
- **Opening:** the owner's opening hand (all cards visible), the Active and Bench each player sets up, and each player's Energy Zone type(s) as shown on screen.
- **One section per global turn** ("global 1" is the first turn of the game), titled with whose turn it is and its time range. In order, with timestamps:
  - the owner's draw;
  - every card played: Supporters, Items, Tools, Stadiums, Pokémon benched or evolved;
  - every Energy attached: type, to which Pokémon, and from the Energy Zone or by an effect;
  - retreats, Ability uses, attacks (name, coin flips, damage), HP before → after, Special Conditions, Knock Outs, points and the score after.
  - End each section with a one-line board state: both Actives and Benches with HP, Energy, Tools and conditions.
- **The owner's hand at the start of each of his turns,** when the screen shows it.

`=== OPPONENT.json ===`
Only the JSON object, in this shape:
```json
{"recording": "<RECORDING>", "went_first": "dustin|opponent", "global_turns": 0, "final_score": {"dustin": 0, "opponent": 0},
 "end": "points|no_pokemon|deck_out|concede_dustin|concede_opponent|timeout_dustin|timeout_opponent",
 "opponent_energy_zone": [], "opponent_energy_attached": [{"turn": 0, "type": "", "to": ""}],
 "opponent_pokemon": [{"name": "", "set_number": null, "first_seen_turn": 0, "attacked": false, "attacks_used": [], "abilities_used": [], "points_taken": 0}],
 "opponent_trainers": [{"turn": 0, "name": ""}], "opponent_effects": {"special_conditions": [], "healed": false, "bench_damage": false},
 "opponent_card_of_the_game": null, "notes": ""}
```
Use `null` or empty lists where something isn't shown. Leave out the opponent's player name.

`=== UNCERTAINTIES.md ===`
Each unsettled point, with its turn, its timestamps and what would settle it.
