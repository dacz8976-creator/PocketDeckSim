You are transcribing a screen recording of one Pokémon TCG Pocket game into a plain, time-ordered list of what happens on screen. Dustin recorded it on his phone. You are not reviewing, judging or summarizing. You write down what each frame shows.

## Your files
- `frames/sheets/sheet_from_NNNNs.jpg`: contact sheets. Each holds 18 frames, one per second, 6 across and 3 down, read left to right, top to bottom. The first frame is second NNNN, the next NNNN+1, and so on.
- `frames/full/t_SSSS.jpg`: full-resolution frames, one per second. SSSS is the second.
- `frames/half/t_SSSS.S.jpg`: half-resolution frames, two per second.
- Do not open `source.mp4`.

## The procedure. Follow it exactly and do not skip steps.
1. List all the sheets in `frames/sheets/`. You will process EVERY sheet, in order, from the first to the last. Do not stop early. Stopping before the last sheet is the one mistake that makes your work useless.
2. For each sheet, open it, then:
   a. Write one line for each second where the screen shows something new: a card played or shown, a Pokémon placed, evolved or retreated, an Energy attached, an attack, a damage number, an HP change, a Knock Out, a point award, a turn change, a coin flip, a Special Condition, or a result screen.
   b. For every line that involves a number or a card name, open the full-resolution frame `frames/full/t_SSSS.jpg` for that second and copy the exact number or name from it. If that frame is mid-animation, try the next second, or the half-resolution frames around it.
   c. Before moving to the next sheet, append the lines to TRANSCRIPT.md. Don't wait until the end.
3. At the very start of the game, open full-resolution frames to record:
   - the deck name or QR;
   - who goes first (the coin or "first"/"second" text);
   - each player's Energy Zone type icon;
   - Dustin's opening hand: his cards are at the bottom of the screen; name every card;
   - each side's first Active and Bench.
4. At the very end, open full-resolution frames to record:
   - the result screen (Victory or Defeat, both players' points);
   - any statistics shown (turns, damage done, card of the game);
   - any rank change.
5. Whenever a new turn starts (the screen says whose turn it is, or the Energy Zone refreshes), write a line `--- TURN CHANGE at SSSS s ---`.

## How to write each line
`SSSS s | who (Dustin / opponent / screen) | what happened | exact names and numbers | frame you read`

For example: `0072 s | Dustin | attack Turbo Shark | 70 damage, opponent Buneary 60 -> 0 | full/t_0073`

## Rules
- Write only what is on screen. If you can't read something, write "unreadable" and give the frame. Never guess.
- Dustin's cards are at the bottom of the screen, the opponent's at the top.
- The opponent's hand is face down. Never name cards in it.
- Keep exact card names, including "ex", "Mega", "Alolan" and "Team Rocket's".

## Output
Write TRANSCRIPT.md to your output folder. Its last lines must be:
- `SHEETS COVERED: <list of every sheet file name>`
- `UNREADABLE: <count>`

Then reply with the number of sheets covered out of the total, and the number of lines written.
