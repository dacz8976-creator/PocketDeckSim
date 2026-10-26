You are the independent checker for two first-pass reviews of one recorded Pokémon TCG Pocket ranked game. The owner of the recording is Dustin. Two reviewers worked blind to each other, from the same frames:
- reviewer H: `out_review_haiku/REVIEW.md`, `OPPONENT.json`, `UNCERTAINTIES.md`;
- reviewer S: `out_review_sonnet/REVIEW.md`, `OPPONENT.json`, `UNCERTAINTIES.md`.

The frames:
- `frames/sheets/sheet_from_NNNNs.jpg`: 18-second overview sheets.
- `frames/half/t_SSSS.S.jpg`: two frames per second, half resolution.
- `frames/full/t_SSSS.jpg`: one frame per second, full resolution, for reading numbers and text.

Do not open `source.mp4`.

## Your job
Check both reviews against the frames yourself. Don't trust either one. Where the two agree, still verify the numbers that matter. Where they disagree, the frames decide. Check:
1. **Every attack:** its damage, the HP before and after, every Knock Out, every point award and the final score. Read the numbers in full-resolution frames.
2. **Every Energy attachment** (type and target), every evolution, and every Trainer card played.
3. **The opening:** the opening hand, the first Active and Bench, the Energy Zone types, and who went first.
4. **The board states,** at least at the end of every second turn and at the end of the game.
5. **Anything either review missed:** a play, a draw, an attachment, a heal, a Special Condition.

Rules: only what the frames show, with timestamps. Hidden information stays unknown.

## Write to your output folder
- **REVIEW_FINAL.md:** one corrected review in the review structure. Start from whichever review is more accurate, and mark every changed line with `[checked: corrected]`.
- **OPPONENT_FINAL.json:** the corrected OPPONENT.json.
- **CHECK_NOTES.md:** two lists of corrections, one per reviewer, one line each, in the form `turn | claim in that review | what the frames show | frame file(s)`. Mark each correction **major** or **minor**:
  - major: a wrong attack, damage, HP, Knock Out, point, Energy type or target, card played, or a missed action;
  - minor: a timestamp, wording, or a board detail that changes nothing.

  Also count the facts each reviewer left as "not shown" or uncertain that the frames actually settle. End with this table:

  ```
  reviewer | major | minor | unsettled-but-settleable | missed actions
  ```

When you finish, reply with that table.
