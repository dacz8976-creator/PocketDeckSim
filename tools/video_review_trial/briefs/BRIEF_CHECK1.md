You are the independent checker for a review of one recorded Pokémon TCG Pocket ranked game. Dustin recorded it. The review is in `<REVIEW_DIR>/`: REVIEW.md, OPPONENT.json and UNCERTAINTIES.md. It was written from the frames in `frames/`.

The frames:
- `frames/sheets/sheet_from_NNNNs.jpg`: 18-second overview sheets.
- `frames/half/t_SSSS.S.jpg`: two frames per second, half resolution.
- `frames/full/t_SSSS.jpg`: one frame per second, full resolution, for reading numbers and text.

Do not open `source.mp4`. Ignore any other folder.

## Your job
Check the review against the frames yourself. Don't trust it. Check:
1. **Every attack:** its damage, the HP before and after, every Knock Out, every point award and the final score. Read the numbers in full-resolution frames.
2. **Every Energy attachment** (type and target), every evolution, and every Trainer card played.
3. **The opening:** the opening hand, the first Active and Bench, the Energy Zone types, and who went first.
4. **The board states,** at least at the end of every second turn and at the end of the game.
5. **The uncertainties:** resolve the ones the frames can settle.
6. **Anything the review missed:** a play, a draw, an attachment, a heal, a Special Condition.

Rules: only what the frames show, with timestamps. Hidden information stays unknown.

## Write to your output folder
- **REVIEW_FINAL.md:** the corrected review, in the same structure. Mark every changed line with `[checked: corrected]`.
- **OPPONENT_FINAL.json:** the corrected OPPONENT.json.
- **CHECK_NOTES.md:** one line per correction, in the form `turn | claim in the review | what the frames show | frame file(s)`. Mark each correction **major** or **minor**:
  - major: a wrong attack, damage, HP, Knock Out, point, Energy type or target, card played, or a missed action;
  - minor: a timestamp, wording, or a board detail that changes nothing.

  End with this table:

  ```
  major | minor | unsettled-but-settleable | missed actions
  ```

When you finish, reply with that table.
