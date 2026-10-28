You are checking two independent written records of one recorded Pokémon TCG Pocket ranked game against frames from the video. Dustin recorded the game on his phone; he is "the owner".

## Files (all under <DIR>)
- **Review G, written by Gemini from the video:** `gemini/REVIEW.md`, `gemini/OPPONENT.json` and `gemini/UNCERTAINTIES.md`. Timestamps such as `t=75s` are seconds from the start of the video.
- **Gemini's cheaper opponent sheet:** `gemini_cheap/OPPONENT.json`, from a lower-detail pass.
- **Review X, Codex's review of the same game:** the files in `codex/`.
  - `REVIEW.md` is the main record.
  - Files such as `OPPONENT.json`, `SUMMARY.json`, `LADDER_ENTRY.json`, `VERIFICATION.json`, `FINDINGS.json` or correction notes are part of it.
  - Review X's final word is REVIEW.md as amended by those files.
- **The truth:** `frames/t_SSSS.jpg`, one frame per second at full resolution. SSSS is the second: second 75 is `frames/t_0075.jpg`. Codex's timestamps may be written differently (mm:ss, or frame numbers); convert them.

## Your job
1. **Compare the two reviews turn by turn** on these facts:
   - who went first; the owner's opening hand; each player's Energy Zone type;
   - each turn's cards played, Energy attachments (type and target), evolutions, retreats and Abilities;
   - each attack with its damage, and HP before and after;
   - Special Conditions, Knock Outs, points, the final score and how the game ended;
   - the opponent Pokémon seen.
2. **Settle each disagreement from the frames.** Open the full-resolution frames around both reviews' timestamps. The verdict is `G right`, `X right`, `both wrong` or `unsettled`.
3. **Also list claims only one review makes** that the frames contradict.
4. **Grade every error, for each review separately.**
   - **Major:** it changes the record of what happened. Examples: an attack, damage number, Knock Out, point, score, who went first or end that is wrong or missing; a card said to be played that wasn't, or the reverse; a wrong card name or wrong Pokémon; a wrong Energy type or target; a missing or merged turn.
   - **Minor:** a timestamp off by more than 3 s; a wrong HP in a board-state line where the event itself is right; a small missing detail.
5. **Check the opponent sheets.** Check `gemini/OPPONENT.json`, `gemini_cheap/OPPONENT.json` and, if it exists, `codex/OPPONENT.json`, each against the frames, on these 12 fields:
   - went_first, global_turns, final_score, end;
   - the opponent's Energy Zone type(s);
   - the set of opponent Pokémon names;
   - each opponent attack name;
   - the opponent Trainer names;
   - special_conditions (conditions that appear in the game from the opponent's cards or attacks), healed, bench_damage;
   - the card of the game.

   Where the two reviews agree on a field, take it as right unless something you saw contradicts it. Settle the rest from the frames.

## Rules
- Don't count style, or differences in detail where neither is wrong.
- A timestamp difference of 3 s or less is not an error.
- Open frames only where needed, at most 120 frames in total.
- Never open any other folder.

## Write to `<DIR>/score/` (the files exist with a placeholder line; replace it)
- **SCORE.md:**
  - the disagreement table: turn, item, what G says, what X says, the frames, the verdict;
  - each review's errors with their grades;
  - the opponent-sheet tables;
  - one paragraph: which record a player could rely on more for this game, and why.
- **score.json:**
  `{"G": {"major": 0, "minor": 0}, "X": {"major": 0, "minor": 0}, "verdicts": {"G_right": 0, "X_right": 0, "both_wrong": 0, "unsettled": 0}, "sheets": {"gemini": {"checked": 12, "right": 0}, "gemini_cheap": {"checked": 12, "right": 0}, "codex": {"checked": 12, "right": 0} | null}, "errors": [{"review": "G|X", "turn": "", "item": "", "says": "", "truth": "", "frames": [], "grade": "major|minor"}]}`

When you finish, reply with the counts only.
