You are comparing two independent written reviews of the same recorded Pokémon TCG Pocket ranked game against the frames themselves. The owner of the recording is Dustin.

- **Review C:** `<C_DIR>/REVIEW_FINAL.md` and `<C_DIR>/OPPONENT_FINAL.json`, written by a Claude reviewer and checker.
- **Review X:** the files in `codex/`, written by a different review team. `REVIEW.md` is their first pass. Files such as `VERIFICATION.json`, `FINDINGS.json`, `LEAD_ACCEPTANCE.json` or correction notes record their checks and accepted changes. Review X's final word is REVIEW.md as amended by those files.
- **The frames:** `frames/full/t_SSSS.jpg` (1 per second, full resolution), `frames/half/t_SSSS.S.jpg` (2 per second) and `frames/sheets/` (overview). Do not open `source.mp4`.

## Your job
1. Go turn by turn through both reviews. Compare these facts:
   - who went first; the owner's opening hand; Energy Zone types;
   - each turn's cards played and their order;
   - each Energy attachment (type and target); evolutions; retreats; Abilities;
   - each attack, its damage, and the HP before and after;
   - Special Conditions, Knock Outs, points, and the final score and end;
   - the opponent Pokémon seen.
2. **Settle every disagreement from the frames.** Open full-resolution frames where numbers or text decide it. For each one, record the turn, the item, what C says, what X says, what the frames show, the frame file(s), and the verdict: `C right`, `X right`, `both wrong` or `unsettled`.
3. **Also list facts only one review records** that the frames confirm (`only C`, `only X`), and any claim in either review that the frames contradict while the other review is silent.
4. **Don't count style.** Wording, timestamp differences under 2 seconds and different levels of detail aren't disagreements unless a fact differs.

## Write to your output folder
- **COMPARE.md:** a readable table of every disagreement and its verdict, then the only-C and only-X lists, then a short paragraph on which review a player could rely on more for this game, and why.
- **compare.json:**

  ```json
  {"disagreements": [{"turn": "", "item": "", "C": "", "X": "", "frames_show": "", "frames": [], "verdict": ""}],
   "only_C": [], "only_X": [], "counts": {"C_right": 0, "X_right": 0, "both_wrong": 0, "unsettled": 0, "only_C": 0, "only_X": 0}}
  ```

When you finish, reply with the counts.
