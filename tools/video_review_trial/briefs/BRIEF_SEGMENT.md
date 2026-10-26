You are transcribing ONE short piece of a screen recording of a Pokémon TCG Pocket game: seconds <FROM> to <TO>. Dustin recorded it on his phone. Other people are transcribing the other pieces, so do your piece completely and nothing else.

## Your files (these exact names; you don't need to list any folder)
- Overview sheets for your piece: <SHEETS>. Each sheet holds 18 frames, one per second, 6 across and 3 down, read left to right, top to bottom. The first frame is the second in the sheet's name.
- Full-resolution frames: `frames/full/t_SSSS.jpg`, one per second, four digits. For example, second 75 is `frames/full/t_0075.jpg`.
- Half-resolution frames: `frames/half/t_SSSS.S.jpg`, two per second. For example `frames/half/t_0075.5.jpg`.
- Do not open `source.mp4`.

## Procedure
1. Open each of your sheets in order.
2. For EVERY second from <FROM> to <TO> where the screen shows something new, write one line. Something new means:
   - a card played or shown, or a card drawn (Dustin's draw shows face up at the bottom);
   - a Pokémon placed, evolved or retreated;
   - an Energy attached (watch the Energy icons on each Pokémon change);
   - an attack, a damage number, an HP change, a heal, a Special Condition, a coin flip;
   - a Knock Out, a point award, a turn change, a Stadium change, or a result screen.
3. For every line with a number or a card name, open the full-resolution frame for that second and copy the exact number or name. If that frame is mid-animation, try the next second or the half-resolution frames.
4. At the end of your piece, open the full-resolution frame `frames/full/t_<TO4>.jpg` and write a STATE line:
   - both Active Pokémon with HP, Energy icons (type and count), Tools and conditions;
   - both Benches the same way;
   - the score, if shown.
5. <EXTRA>

## Line format
`SSSS s | Dustin / opponent / screen | what happened | exact names and numbers | frame you read`

## Rules
- Only what is on screen. If you can't read something, write "unreadable" and the frame. Never guess.
- Dustin's side is the bottom half of the screen; the opponent's is the top. The opponent's hand is face down, so never name cards in it.
- Keep exact card names, including "ex", "Mega", "Alolan" and "Team Rocket's".
- Turn changes: write `--- TURN CHANGE at SSSS s ---` when the screen shows whose turn it is.

## Output
Your output file `PART_<PART>.md` ALREADY EXISTS in your output folder, holding one placeholder line: `PLACEHOLDER - replace me`. Replace that line with your transcript using the Edit tool (old_string = that placeholder line). You can also add more text with further Edits. Save as you go, at least after each sheet, so nothing is lost. In the finished file, Its first line is `PIECE <FROM>-<TO> s`. Its last line is `COVERED <FROM>-<TO> s, UNREADABLE <n>`.

Reply with the number of lines you wrote.
