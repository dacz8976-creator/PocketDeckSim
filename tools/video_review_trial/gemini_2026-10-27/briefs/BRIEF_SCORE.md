You are checking an AI's written record of one recorded Pokémon TCG Pocket ranked game. You check it against a reference record and against frames from the video. Dustin recorded the game on his phone; he is "the owner".

## Files (all under <DIR>)
- **Review G, written by Gemini from the video:** `gemini/REVIEW.md`, `gemini/OPPONENT_review.json` and `gemini/UNCERTAINTIES.md`. Its timestamps such as `t=75s` are seconds from the start of the video.
- **Gemini's quick opponent sheet:** `gemini/OPPONENT_field.json`, a separate, cheaper pass.
- **Review C, an earlier review that a careful checker corrected against the frames:** `ref/REVIEW_FINAL.md` and `ref/OPPONENT_FINAL.json`.
  - `ref/CHECK_NOTES.md` lists that checker's corrections.
  - `ref/compare.json` lists facts already settled from the frames when Review C was compared with a third review.
  - Review C is very likely right, but not certain. The frames decide.
- **The truth:** `frames/t_SSSS.jpg`, one frame per second at full resolution. SSSS is the second: second 75 is `frames/t_0075.jpg`.

## Your job
1. **Compare the two reviews turn by turn** on these facts:
   - who went first; the owner's opening hand; each player's Energy Zone type;
   - each turn's cards played, Energy attachments (type and target), evolutions, retreats and Abilities;
   - each attack with its damage, and HP before and after;
   - Special Conditions, Knock Outs, points, the final score and how the game ended;
   - the opponent Pokémon seen.
2. **Settle each fact where they disagree.** If `ref/compare.json` or `ref/CHECK_NOTES.md` already settled it from the frames, use that and say so. Otherwise open the full-resolution frames around both reviews' timestamps and settle it. The verdict is `G right`, `C right`, `both wrong` or `unsettled`.
3. **Also list:**
   - facts Review C records, confirmed by the frames, that Review G is missing;
   - claims in Review G that the frames contradict while Review C is silent;
   - Review G's uncertainty items, and whether each was a real gap.
4. **Grade every Review G error.**
   - **Major:** it changes the record of what happened. Examples: an attack, damage number, Knock Out, point, score, who went first or end that is wrong or missing; a card said to be played that wasn't, or the reverse; a wrong card name or wrong Pokémon; a wrong Energy type or target; a missing or merged turn.
   - **Minor:** a timestamp off by more than 3 s; a wrong HP in a board-state line where the event itself is right; a small missing detail, such as an incomplete hand list.
5. **Check both opponent sheets.** Compare `gemini/OPPONENT_field.json` and `gemini/OPPONENT_review.json` separately against `ref/OPPONENT_FINAL.json` on these fields:
   - went_first, global_turns, final_score, end;
   - opponent_energy_zone;
   - the set of opponent Pokémon names;
   - each opponent attack (name and damage);
   - the opponent Trainer names;
   - special_conditions, healed, bench_damage;
   - the card of the game.

   A field matches if the facts match; ignore wording, key order, set numbers and the notes field. Settle mismatches from the frames the same way.

## Rules
- Don't count style.
- A timestamp difference of 3 s or less is not an error.
- Open frames only where a disagreement needs them, at most 120 frames in total.
- Do not open any other folder.

## Write to `<DIR>/score/` (the files exist with a placeholder line; replace it)
- **SCORE.md:**
  - a table of every Review G error: turn, item, what G says, the truth, the frames, major or minor, and how it was settled;
  - the missed facts;
  - the two opponent-sheet tables;
  - one paragraph on whether a player could rely on Review G for this game.
- **score.json:**
  `{"major": 0, "minor": 0, "missed": 0, "g_right_over_c": 0, "unsettled": 0, "errors": [{"turn": "", "item": "", "g": "", "truth": "", "frames": [], "grade": "major|minor", "settled_by": "frames|compare.json|CHECK_NOTES"}], "field_sheet": {"fields_checked": 0, "matched": 0, "mismatches": []}, "review_sheet": {"fields_checked": 0, "matched": 0, "mismatches": []}}`

When you finish, reply with the counts only.
