You are reading seven turns from Dustin's Kingambit games, one at a time, and judging each on its own board. Work only from the four files
in this folder: turns.json, cards.md, PLAN.md and his_list.txt. Do not open any other file or folder (nothing outside this folder, no
repository, no other notes), and do not search for other readings of these turns.

For each turn T1-T7 in turns.json you have:
- `position`: both boards (HP is remaining HP; energy attached; tools; the cards behind each Pokémon), his hand, both discards, the
  points, the Energy Zone, the Stadium and the turn;
- `his_plan`: the moves he actually made that turn, in order;
- `km3_plans_12_seeds`: what a bot (km3) chose to do from the same position at 12 different seeds. A plan may stop early ("cut").

**Your job for each turn:**
1. Say in one line what km3 does (its usual line across the 12 seeds, and any seed that differs). Say in one line what he did.
2. Work out what each line leads to on THIS board:
   - the damage and knockouts each line makes;
   - the opponent's visible threats next turn (their Active and Bench, their attached Energy and the turn's Energy; their hand is
     hidden, so never rely on a card they might hold);
   - what each line keeps or loses for his plan in PLAN.md. Show the HP arithmetic from cards.md.
3. Classify the turn as one of:
   - **his line at least as good:** on this board his choice is as good as km3's or better, for a reason you can show from the files;
   - **unclear:** both are defensible, or the board does not settle it;
   - **km3 better:** km3's line is better.
   Give your confidence (low, medium or high) and the single fact the verdict rests on. If you find an error in the data or a rule you
   can't settle from cards.md, say so.

Take the time you need; a careful reading matters more than speed. Write your answers to `READ.md` in this folder: a table (turn,
km3's line, his line, class, confidence, the deciding fact), then one paragraph per turn with the arithmetic. Then stop.
