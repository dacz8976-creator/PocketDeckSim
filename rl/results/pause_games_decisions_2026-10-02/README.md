# Pause games vs km3: draft A, his first four turns (Oct 2, 2026)

**One-line answer.** On the 20 turn starts (his turns 1-4 in the five Draft A games), km3's first action matches his in 8, splits in 7 (draw-card choices that change with the sampled deck order) and differs in 5; its whole plan up to the first draw matches in 3. Where the plans differ it is almost always a Supporter choice (Irida, or which draw card), then retreat/promotion (3 turns); the attack is never different. On Turbo Shark's Bench Energy km3's scores differ by 10-50 between targets, and one tie. No turn lets me say who was right by outcome. Nothing here says anything about strength.

## What was done

- **Positions.** Each turn is rebuilt as a constructed board at the start of his turn, after his draw: his hand, both boards (Pokémon, HP, Energy, Tools, evolutions underneath), Stadium, points, turn number, discard piles, the turn effects (Item lock, Flower Trick's mark) and the cards left in his deck (the 20-card list minus everything seen; the harness refuses a position that over-counts a card). 20 turn starts plus 2 mid-turn positions (115323 turn 5 after the Copycat; 132311 turn 7 after Research and Poké Ball) for the Turbo Shark question. `positions_A.json`, built by `positions_A.py` with a note per position.
- **Hands.** 10 turns from the written reviews alone (`text`), 8 read from still frames (`frame`), 2 forced by the review's own later plays (`elimination`). Marked in every table row; the frame files are in `FRAME_READS.md`. Dustin allowed stills (Oct 2); Sonnet helpers read them, no video was opened.
- **km3.** The official engine, main-8626a35 (`rl/engine-2026-10-02`), km3 = `PublicPricingPlayer` over depth-3 expectiminimax with the km value function. A scratch harness (`harness/pg_pos.rs`) in a copy of that source, outside the repo's `engine/`, with the print-only score-dump patch from Step 8c (`harness/dg_patch.py`, `pgd_patch.py`). km3 sees only its own hand and the public board; the opponent's hidden cards are filler of the right count.
- **12 seeds per position.** The seed fixes the search's sample of his unseen cards' order and the real draws, so a first action that changes with the seed is a split, not a preference.
- **Grading as the quizzes do:** only the part of the turn up to and including the first draw card (Research, Poké Ball, Copycat); a turn with no draw card is graded whole. Place-slot numbers and the final EndTurn are ignored.

## Results (tables per game: `TABLES.md`; raw search scores: `raw/`)

| | turns |
|---|---|
| km3's first action = his, in at least 10 of 12 seeds | 8: 143309 t04, t08; 115323 t07; 143837 t07; 114458 t04, t06, t08; 132311 t03 |
| split (3-8 of 12) | 7: 143309 t02; 115323 t01; 143837 t01, t03, t05; 114458 t02; 132311 t01 |
| differs (0 of 12) | 5: 143309 t06; 115323 t03, t05; 132311 t05, t07 |
| whole plan to the first draw = his, in at least 10 of 12 seeds | 3: 143837 t07, 114458 t06, 132311 t03 |
| first action agrees but the plan differs later | 5: 143309 t04, t08; 115323 t07; 114458 t04, t08 |

All 7 splits are choices among draw cards at the turn start (Research / Poké Ball / Copycat; on 143837 t03 Research first 8 of 12, Elegant Cape first 4 of 12). The root scores of those candidates move with the sampled deck order, so km3 has no stable preference there.

**By the categories asked for (a turn can carry several):**

- **Supporter/Item choice or order: 17 of 20.** Ten involve a draw card (which of Research, Poké Ball or Copycat first; Research versus Irida; Misty versus Copycat). **Irida:** km3 plays it on 8 turns where he did not (143309 t04, t06, t08; 115323 t05, t07; 114458 t04; 132311 t05, t07). On 5 of them he spent his Supporter on another card that turn (Misty, Research, Copycat); on 3 he left the Supporter slot unused with Irida in hand and a damaged Pokémon on the board (143309 t08, 115323 t07, 132311 t05, the turn he used Lucky Ice Pop twice). On 115323 t03 km3 never plays Misty (Copycat 7 of 12, or a Water to Carvanha); he played Misty (one head) and put the Water on Lapras.
- **Retreat/promotion: 3** (132311 t05 and t07, 114458 t08). On 132311 t05 km3 retreats the damaged Mega Sharpedo ex first, heals with Irida, evolves the Carvanha now in the Active Spot and attacks; he evolved the benched Carvanha, healed with Lucky Ice Pop twice and attacked from the same Mega. On 132311 t07 both lines retreat the damaged Mega into the fresh one; he plays Research first and km3 never does. On 114458 t08 km3 retreats the 50-HP Alolan Ninetales ex for the fresh one (150 HP) and attacks with it; he kept the damaged one Active and attacked.
- **Evolution timing: 1** (132311 t05: km3 evolves the Carvanha after retreating into it).
- **Energy attachment target: 1** (114458 t08, follows from the retreat).
- **Attack choice: none.** Wherever both lines attack, they use the same attack. (Four rows are tagged "attack vs another action" only because his graded plan ends at a draw card and km3's goes on to the attack.)
- **Tool placement: none** (143837 t03: in 4 of 12 seeds km3 plays Elegant Cape before Research; the placement is the same).
- **Order of independent actions:** 115323 t05 (mid-turn position) is the same set of actions in a different order (km3 evolves before benching the Vulpix).

## Turbo Shark (`TURBO_SHARK.md`)

Turbo Shark was available to him on six of the twenty turns (115323 t05 once the Copycat had drawn the Sharpedo, and t07; 132311 t03, t05, t07; 143837 t07 after the Copycat) and he used it every time. km3's own line also ends in Turbo Shark on 115323 t07 and 132311 t03, t05, t07 and, from the mid-turn position, on 115323 t05; from the start of 115323 t05 its own line is Irida, bench the Carvanha, Surf with Lapras. Only three of the turns offer a real Bench target (115323 t05, t07; 132311 t07): the others have one Water Pokémon on the Bench and the engine places the Energy without asking.

| position | Bench targets and km3's root scores (mean of 12 seeds; the scores did not move with the seed) | his pick | km3's pick |
|---|---|---|---|
| 115323 t05, after retreat | Lapras (0 Energy) 765.1; second Carvanha 775.1; Vulpix 785.1 | Vulpix | Vulpix |
| 115323 t07 | Lapras (1 Water) 669.5; Carvanha 679.5; Vulpix (1 Water) 629.5 | Lapras | Carvanha |
| 132311 t07 | damaged Mega (2 Water) 11,618.63; Vulpix (new) 11,618.63 | Vulpix | tie, goes to Vulpix |

Reading it: the target pick moves km3's score by 10-50 (and ties once), where a different first action moves it by 100-1,400 (for example 109 for Irida before the attack on 115323 t07). The one target where km3 ranks differently from him is by 10. That fits the laptop's code read (bench Energy priced through HP x Energy against the Benched Pokémon's own priciest attack, 3-5x low), and the ranking of the three targets changes between two positions (Vulpix ranks first on 115323 t05, last on t07). When Turbo Shark is the next action, its root score equals the best target's score (679.5 on 115323 t07, 785.1 on t05), so the target frame is priced when it is one ply away; I did not test it as a later action in a line (the depth question in the code read), which the root dump of any turn start can show.

**Wallace-type lines:** none appear in these twenty turns (Draft A has no Wallace); nothing to record.

## Who was right

Not unambiguous on any turn. The narrowest fact: on 114458 t08 his Ninetales ex (50 HP) was Knocked Out by Heat Blast on the opponent's next turn (2 points to them); km3's line would have met the same attack with a 150-HP Ninetales. He still won that game 3-2, and the opponent's reply would not have been the same on a different board, so I do not call it.

## Assumptions and limits

1. The order of his plays inside a turn is the reviewer's prose order (frame labels are 4-second midpoints). Where logic fixes it (Research before the evolution it makes possible), it is noted in the position.
2. His unseen cards are the list minus the seen ones, in random order (12 seeds). Two hands are `elimination`, and the turn-5 Mega Sharpedo ex on 132311 is "probable" (card count).
3. The opponent's hand size is bookkeeping checked by visual counts of the card backs; a re-run with the bookkeeping counts for the four early turns where they differ by one gives the same first-action counts (`raw_bookkeeping_hand_counts/`).
4. Misty's target is not preserved in the review on 114458 t08 (treated as a wildcard). Coin outcomes never matter at a decision point.
5. km3 is a depth-3 search; its choice among draw cards and the root scores depend on the sampled deck order. A score is a root value of the search, not a probability.
6. Five games and twenty turns: no claim about strength, either way.
7. Deck 03 (the five Wailord games) is not done; it waits for the coordinator.

## The positions as a test set for any pilot

`harness/run_pilot.sh BOT [SEEDS] [PG_POS_BINARY]` runs every position with the pilot code BOT (any code `parse_player_code` knows) at nice 19 and writes `runs_<BOT>/` (raw) and `report_<BOT>/` (the tables above, for that pilot) in about four seconds. For an experimental pilot, build the harness against the engine tree that contains it: `PGD_ENGINE=<engine dir> PGD_TARGET=<target dir> PGD_BIN=<binary> harness/pgd_build.sh 8` (it applies the print-only patch, which asserts its anchors are found exactly once, then builds `pg_pos.rs` as an example). Pilots built on `ExpectiMiniMaxPlayer` also print their root scores; others record only their choices. To add positions, extend `positions_A.py` (a position names a deck key; `--deck KEY=file` supplies the list) and rerun. Check: `kta3` gives exactly the same tables as `km3` on these 22 positions, as it should (km differs from kta only by the Training Area / Arena bonus, which changes no choice here).

## Files

`TABLES.md` (a table per game), `TURBO_SHARK.md`, `summary.json`, `totals.json`, `positions_A.json` and `positions_A.py` (the positions with their notes), `FRAME_READS.md` (how each hand was fixed), `raw/` (stdout JSON lines and the PGSTEP/PGDUMP root scores for every position and seed), `harness/` (the example, the print-only patch, the run and report scripts), `BUILD.txt` (hashes).
