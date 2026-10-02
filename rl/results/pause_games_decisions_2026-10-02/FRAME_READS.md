# How each hand was fixed (draft A, his turns 1-4)

Source folders: `C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\<stem>_iOS_shark_sol\` (REVIEW.md, COVERAGE.md, `native\` full-size frames, `overview\sample_frames\` one 390 px frame per 4 s, `gap_*\`). Dustin's go-ahead for stills (Oct 2, in chat): his own hand is visible, the opponent's is not; the decks are on the Pause Games log. Frames were read by Sonnet helpers (still images only, no video). The deck lists are the Pause Games `pause_decks` doc for Draft A (`decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt`).

`text` = opening hand + named draws - named plays from the review. `frame` = read from stills. `elimination` = forced by the review's own later plays.

Every position was checked by the harness: every card seen (hand, discard, board, under evolutions, Tools, own Stadium) must fit inside the 20-card list; the cards left over are the unseen deck. All 22 positions passed.

## 143309 (went second, won 3-0): all five of his turns are `text`
Opening hand: Alolan Vulpix (Active), Alolan Ninetales ex x2, Professor's Research, Copycat. T2 draw Cyrus; Research drew Lapras + Irida (turn 2); turn 4 draw Misty; turn 6 draw Research, which drew Poké Ball + Elegant Cape; turn 8 draw Mega Sharpedo ex. Every draw and Research draw is named in the review.

## 115323 (went first, lost 2-3): all seven of his turns are `text`
Opening hand: Lapras (Active), Elegant Cape, Copycat, Misty x2. Draws: turn 1 Poké Ball, turn 3 Irida, turn 5 the second Carvanha (benched), Copycat then drew Mega Sharpedo ex, Alolan Vulpix, Cyrus; turn 7 Irida (Copycat had shuffled it away).

## 143837 (went first, won 2-1 by concession)
- Turn 1 (`frame`): hand Research, Poké Ball, Misty, a Mega Sharpedo ex (HP 190 and Turbo Shark 70 legible on the card), and the drawn Elegant Cape. `overview/sample_frames/00010.jpg`, `00011.jpg` (about 40-44 s). The opening hand is not named in the review.
- Turn 3 (`frame`): Research, the Sharpedo, Elegant Cape, Lucky Ice Pop (drawn). `00022`-`00024` (88-96 s) and `native/t0100.00.jpg` (Research had drawn Alolan Ninetales ex and Copycat).
- Turn 5 (`elimination`): the review has him play a Poké Ball that nothing else could have supplied, so the turn-5 draw is that Poké Ball; hand Sharpedo, Lucky Ice Pop, Copycat, Poké Ball.
- Turn 7 (`elimination`): hand Sharpedo, Lucky Ice Pop, Copycat + the drawn Misty (review).

## 114458 (went second, won 3-2)
- Turn 2 (`text`): opening hand Mega Sharpedo ex, Copycat, Lucky Ice Pop, Alolan Ninetales ex + Vulpix (Active); draw Research. Also seen in `native/t0064.00.jpg`, `00015`, `00016`.
- Turn 4 (`frame`): Mega Sharpedo ex, Copycat, Lucky Ice Pop, Ninetales ex, Irida, Poké Ball (Research's two draws on turn 2), and the drawn second Mega Sharpedo ex; hand count indicator 7 in `00026`. `gap_78_104/sample_frames/00012`, `00013`, `native/t0094.00.jpg`, `t0106.00.jpg`. The leftmost Sharpedo is cut off in the frames; the count of 7 and the arriving second Sharpedo support it. His Copycat then drew Sharpedo, Misty, Lapras, Poké Ball (review).
- Turn 6 (`frame`): Mega Sharpedo ex, Misty, Poké Ball, and the drawn Alolan Ninetales ex (pink art). `gap_154_186/sample_frames/00015`, `00016`, `native/t0174.00.jpg`, `t0204.00.jpg`.
- Turn 8 (`frame`): Mega Sharpedo ex, Alolan Ninetales ex, and the drawn second Misty. Overview `00064`-`00067`, `native/t0268.00.jpg`.
- Opponent hand counts (visual): turn 2: 3, turn 4: 4 (his Copycat drew 4), turn 6: 2, turn 8: 3. They match the bookkeeping.
- Turn 7 (opponent): Slow Sear milled Irida from the top of his deck into his discard; the turn-8 position has it there.

## 132311 (went first, won 2-0 on the opponent's timeout)
- Turn 1 (`text`, also `native/t0030.00.jpg`): opening hand Mega Sharpedo ex, Lucky Ice Pop, Poké Ball, Professor's Research + Carvanha (Active); draw Cyrus.
- Turn 3 (`frame`): Mega Sharpedo ex, Lucky Ice Pop, Cyrus, Alolan Ninetales ex, Misty, Irida (drawn). The turn-1 Research drew the Ninetales ex and Misty (fan goes from 3 to 5 cards at 50-54 s, `sheet_02.jpg`, `00014`-`00016`). `00023`-`00025`, `native/t0101.00.jpg`, `t0119.00.jpg`.
- Turn 5 (`frame`): Lucky Ice Pop, Cyrus, Ninetales ex, Misty, Irida, and the drawn second Mega Sharpedo ex (alternate art; "probable, by card count": four cards remain at the end of the turn, `native/t0190.00.jpg`). `native/t0161.00.jpg`, `00041`-`00043`.
- Turn 7 (`frame`): Cyrus, Ninetales ex, Misty, Irida, and the drawn Professor's Research (alternate art), which drew Poké Ball + Alolan Vulpix; the Poké Ball then fetched a second Vulpix that stayed in hand. `00059`-`00062`, `native/t0246.00.jpg`. (The mid-turn position uses that state.)

## Opponent hand sizes
Bookkeeping from the review (opening 5, draws, named plays), checked against visual counts of card backs by the helpers. They agree except where the opponent went second on his first turn(s): the helpers counted 5 on turn 1 (and 6 on turn 3 of 143837) against 4 and 5 by bookkeeping. The positions use the visual counts there (143837 turns 1 and 3, 132311 turn 1) and 5 for 115323 turn 1 by analogy. A re-run with the bookkeeping counts gives the same first-action counts in all four turns. The opponent's hand only enters km3's search through Copycat's draw count.

## Where the review's order of plays is only a reading
The reviews list actions in prose with 4-second frame labels; the order inside a turn is the reviewer's reading. Where a native frame time or the game's own logic fixes it (Research before the evolution it makes possible; Poké Ball before benching what it finds), I say so in the table notes.
