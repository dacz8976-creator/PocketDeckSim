You are writing the review of one recorded Pokémon TCG Pocket ranked game. Dustin recorded it. Transcribers have gone through the recording in short pieces. Each piece is in `out_segments/PART_NN.md` and ends with a STATE line describing the board at that moment. Read ALL the parts, in order.

You also have the frames (`frames/full/t_SSSS.jpg`, one per second; `frames/half/t_SSSS.S.jpg`). Open frames ONLY to settle:
- a line marked unreadable;
- a gap between pieces;
- two pieces that disagree, for example a STATE line that doesn't match the next piece's opening;
- arithmetic that doesn't add up.

Open at most 40 frames. Do not open `source.mp4`.

Before writing, check the arithmetic, and fix what doesn't add up from the frames:
- Damage must match the HP changes.
- Points must add up to the final score.
- The result screen's damage total, if shown, must equal the sum of Dustin's attacks.
- Each turn should have one Energy attachment from the Energy Zone, plus any made by effects.
- Each Pokémon's Energy count must follow from its attachments, discards and retreats.

Then write three files to your output folder.

**REVIEW.md:**
- **A header:** the deck name or QR shown, who went first, the final score, how the game ended, the number of global turns, and the result screen's statistics.
- **Opening:** Dustin's opening hand, each side's first Active and Bench, and each player's Energy Zone type(s).
- **One section per global turn** (global 1 is the first turn of the game), titled with whose turn it is and its time range. In order, with timestamps:
  - Dustin's draw;
  - every card played;
  - every Energy attached (type, target, and from the Energy Zone or by an effect);
  - retreats, Ability uses, attacks (name, coin flips, damage), HP before → after, Special Conditions, Knock Outs, points and the score.
  - End each section with a one-line board state: both Actives and Benches with HP, Energy, Tools and conditions.
- **Dustin's hand at the start of each of his turns,** when shown.

**OPPONENT.json:**

```json
{"recording": "...", "went_first": "dustin|opponent", "global_turns": 0, "final_score": {"dustin": 0, "opponent": 0},
 "end": "points|no_pokemon|deck_out|concede_dustin|concede_opponent|timeout_dustin|timeout_opponent",
 "opponent_energy_zone": [], "opponent_energy_attached": [{"turn": 0, "type": "", "to": ""}],
 "opponent_pokemon": [{"name": "", "set_number": null, "first_seen_turn": 0, "attacked": false, "attacks_used": [], "abilities_used": [], "points_taken": 0}],
 "opponent_trainers": [{"turn": 0, "name": ""}], "opponent_effects": {"special_conditions": [], "healed": false, "bench_damage": false},
 "opponent_card_of_the_game": null, "notes": ""}
```

No opponent player name.

**UNCERTAINTIES.md:** whatever is still unsettled.

When you finish, reply with one paragraph: the result, the number of turns, how many piece lines you corrected, and how many frames you opened.
