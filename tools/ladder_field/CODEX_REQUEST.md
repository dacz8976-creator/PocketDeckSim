# Request for Codex: one OPPONENT.json per ranked game

From now on, for every ranked game you review, please write an `OPPONENT.json` next to `REVIEW.md`. It feeds Dustin's Ladder Field dashboard, which tracks the decks, Energy types and plans he faces.

The rule for every field: record only what the video shows. If something isn't shown, write `null` or leave the list empty. Never fill anything in from what that deck "usually" plays.

```json
{
  "recording": "ScreenRecording_10-24-2026 15-36-08_1.mp4",
  "went_first": "dustin | opponent",
  "global_turns": 9,
  "final_score": {"dustin": 1, "opponent": 3},
  "end": "points | no_pokemon | deck_out | concede_dustin | concede_opponent | timeout_dustin | timeout_opponent",
  "opponent_energy_zone": ["Fire", "Lightning"],
  "opponent_energy_attached": [{"turn": 2, "type": "Fire", "to": "Mega Rayquaza ex"}],
  "opponent_pokemon": [
    {"name": "Mega Rayquaza ex", "set_number": "B4 ...", "first_seen_turn": 2, "attacked": true,
     "attacks_used": ["..."], "abilities_used": ["..."], "points_taken": 2}
  ],
  "opponent_trainers": [{"turn": 3, "name": "Cyrus"}],
  "opponent_effects": {"special_conditions": ["Poisoned"], "healed": true, "bench_damage": false},
  "opponent_card_of_the_game": "Mega Rayquaza ex",
  "notes": "short, factual"
}
```

- **`opponent_energy_zone`:** the type or types shown in the opponent's Energy Zone. Read them from the screen even on a turn when nothing gets attached.
- **`name`:** exact card names, keeping "ex", "Mega", "Alolan" and "Team Rocket's". Fill `set_number` only when the card is opened or readable on screen.
- **`points_taken`:** the points this Pokémon scored by Knock Outs.
- **No opponent player name** goes in this file.
- **The Ladder Log entry:** its opponent text should list exactly the Pokémon in `opponent_pokemon`. Two entries didn't match: one listed a Nihilego that never appeared, and one left out a Hisuian Zoroark ex that did most of the damage.
- **Recording names:** give every recording, test clips included, a name with its date and time. A clip named just "T2.MP4" was matched by mistake to every note that mentioned turn 2.
