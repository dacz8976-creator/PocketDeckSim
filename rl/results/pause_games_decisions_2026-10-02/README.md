# Pause games vs km3: draft A, his turns 1-7 (Oct 2, 2026)

**One-line answer.** On the 20 turn starts of his turns 1-4 (five Draft A games), km3's first action matches his in 8, splits in 7 (draw-card choices that change with the sampled deck order) and differs in 5; its whole plan up to the first draw matches in 3. On the 12 turn starts of his turns 5-7 it matches in 5 and differs in 7 (these turns have more cards in play and more to choose from), the whole plan in 2. Over all 32 turn starts, where both his line and km3's reach an attack, **km3 uses a different attack in 1 of 22**: 114458 turn 10, where he attacked with the four-Water Lapras (Surf) and km3 retreats it and attacks with the Ninetales ex (Binding Snow). Everything else that differs is the plan around the attack: which Supporter (Irida on 11 turns where he did not), which draw card first (seed noise), healing and retreat/promotion order. On Turbo Shark's Bench Energy km3's scores differ by 10-50 between targets, with ties, and its pick matched his on 2 of 4 real choices. km3 recognised all three immediate wins (143837 t13, 114458 t12, 143309 t10). No turn lets me say who was right by outcome. Nothing here says anything about strength.

**Added later on Oct 2: turns 5-7** (see the section below), the held-out set of positions, and milestone tags on every position; then **deck 03** (three of the five Wailord games, 15 turn starts, from the review text alone: see "Deck 03" below). The page now holds 49 positions.

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
7. Deck 03 (the five Wailord games): three of the five are built (see the section below); the other two name no opening hand and are listed for the Codex agents.

## His turns 5-7 (12 more turn starts), the held-out set and the milestone tags

**Hands.** Bookkeeping from the review (the opening hand, named draws, plays) predicted every hand; five Sonnet helpers then read the start of each of the 12 turns from stills and **all 12 predictions held** (nothing unreadable, nothing different; two cards, the Elegant Cape on 132311 turn 11 and the Ninetales ex on 115323 turn 13, are "probable" because the drawn card is seen zoomed or played, not in the fan). Opponent hand sizes are the helpers' visual counts of card backs. The frames are listed in `FRAME_READS.md`.

**Results (turns 5-7, 12 turn starts).** First action = his in 5 (143837 t13, 114458 t12, 115323 t09, t11, 132311 t13), different in 7; the whole plan to the first draw equal in 2 (114458 t12 and 132311 t13); same first action but a different plan later in 3 (143837 t13, 115323 t09, t11). Details per position in `TABLES.md`. What is new compared with turns 1-4:

- **The three immediate wins**: 143837 t13 (Cyrus brings the damaged Ogerpon ex Active, Binding Snow KOs it for 2 points: 2 -> 4), 114458 t12 (Binding Snow KOs the 20-HP Aerodactyl, the third point) and 143309 t10 (Binding Snow KOs the 10-HP Mewtwo ex, 1 -> 3). km3 takes the win in all three, and in 114458 t12 and 143837 t13 with exactly his first action (Cyrus; the attack). On 143309 t10 it attacks at once, without the Vulpix, Irida and attachment he did first.
- **A different attack, once**: 114458 t10 (milestone: adapting when the plan fails): he put the Cape on the second Ninetales and attacked with the four-Water Lapras (Surf, 70 + 20 Water weakness, KOs the 40-HP Chandelure); km3 retreats Lapras, puts the Cape on, attaches and attacks with the Ninetales ex (Binding Snow, which also blocks the opponent's Active attachment).
- **Same actions, different order, not always neutral**: 115323 t09 (managing a sacrifice): he heals the Mega Sharpedo ex (a 3-point liability) with Irida and two Lucky Ice Pops, then retreats it into Lapras; km3 retreats before the Ice Pops, so the Ice Pops, which heal the Active Pokémon, would heal Lapras instead. The report tags this "same actions, different order", but the order decides which Pokémon is healed.
- **Retreat before evolving**: on 115323 t13 and 132311 t09 km3 retreats first and evolves the Vulpix in the Active Spot (his: evolve on the Bench, then retreat into it), the same end board; on 115323 t13 it also puts the turn's Water on the Carvanha (slot 1) where he put it on the earlier Vulpix.
- **Turbo Shark target, a fourth**: 115323 t11 (he benched a new Vulpix, gave it the turn's Water, then Turbo Shark's Water too): km3's scores for the targets are Carvanha (0 Energy) 483.03, Vulpix 433.03, the new Vulpix 433.03, so it would put Turbo Shark's Water on the Carvanha; his pick scores 50 lower. Over the four real choices (115323 t05, t07, t11; 132311 t07) km3 matched his target on 2 (115323 t05, 132311 t07 by a tie-break), not on 2 (115323 t07 by 10, t11 by 50).
- Irida: km3 plays it on 3 more turns where he did not (143837 t09 and t11, 132311 t09), 11 in all.

**Held-out set.** A quarter of the games, chosen by game and not by turn, by a fixed rule written in `positions_A.py` and `positions_heldout.json`: a game is held out when `int(sha256('pause-heldout-v1|' + game_id), 16) % 4 == 0` (game id = the recording stem, `ladder-<stem>` for the Ladder Log). It is stable as games are added. For these five games that holds out **143309** (its 5 positions); the development games are 114458, 115323, 132311 and 143837 (27 positions with the two mid-turn ones). `run_pilot.sh` skips held-out positions while `positions_heldout.json` says `locked: true`, and `filter_positions.py` refuses `--include-heldout` while it is locked; nobody flips it until the laptop Opus or the coordinator says so. (km3, the reference, was run on everything, and the findings above include 143309: the lock concerns development pilots.)

**Milestone tags** (my reading of what each turn is about; a position can carry several; each row of `TABLES.md` shows them): preparing an attacker (28 of the 49 positions), managing a sacrifice (10), recognising an immediate win (3), adapting when the plan fails (3); 36 positions carry a tag (counts after deck 03 was added). The positions with their tags are in `positions_A.json` (`milestones`).

## Deck 03 (the Wailord / Indeedee wall): 15 more turn starts, text only (Oct 2)

Three games, every one of his turns: **020315** (lost 1-3, second; turns 2, 4, 6, 8, 10), **020920** (won by concession 0-0, second; turns 2, 4, 6, 8) and **023418** (won by concession 0-1, first; turns 1, 3, 5, 7, 9, 11). All 15 hands come from the written reviews (`text`): each names the opening hand and every drawn card; no still frame was opened and no helper was used. The opponent's hand size is bookkeeping, not a count (it only matters for Copycat, the deck's one card that reads it; Copycat was not in his hand in any of these three games). Games 021402 and 022135 name no opening hand, so they are not built (listed for the Codex agents in `CODEX_REQUEST.md`). Held out by the fixed rule: none of the three (the rule held out only 143309 among the eight games).

**Results (15 turn starts, 12 seeds each).** km3's first action equals his in 13 of 15 and its whole plan to the first draw in 6. The two where the first action differs: 020920 t02 (he opens with the Poké Ball; km3 puts the Heavy Helmet on first in 9 of 12 seeds and Research in 3 of 12, an order difference) and 020920 t04. Details per position in `TABLES.md`. The differences that are about a choice and not an order:

- **Evolution target (020920 t04).** With the damaged Wailmer (80/100) Active and both a Wailord and a Wailord ex in hand, he evolves into the Wailord (200 HP) and keeps the Wailord ex for the Wailmer he benches later; km3 evolves into the Wailord ex (250 HP) in 12 of 12 seeds, after two Watch Overs.
- **Pokémon Center Lady is used by km3, held by him (020315 t08 and t10; 023418 t09).** Two Watch Overs heal 20 each; he kept Lady in hand through all three games, km3 plays it for the rest of the damage on those turns (on 023418 t09 it plays Lady in 7 of 12 seeds and fewer Lucky Ice Pops than the four heads he flipped: the Ice Pop's coin flips are why the plans differ in length).
- **A Stadium km3 never plays (023418 t03).** He plays Soothing Shore the turn he evolves; km3 does not in any of the 12 seeds (I did not look into why).
- **A point on the table (023418 t11).** Wailord (five Water, a -30 from Bonsly's Teary Attack in force) can Whale Pump the 30-HP Bonsly Active for a knockout, 1 point; km3 does that in 12 of 12 seeds. He healed, attached and used Cyrus to bring the damaged Mega Lucario ex (110 HP) Active, and the opponent conceded before his attack (80 damage would have left it on 30). Not a verdict either way: the review says the Cyrus line was not shown lethal, and what he had planned after Cyrus is not recorded.
- **Benching order (023418 t01).** He benches the Indeedee ex before Research; km3's plan reaches Research with no bench move before it (the grading stops at the first draw card, so what it does after is not compared).

**A rule added to the report for this deck.** Watch Over heals 20 from the Active and the engine offers it at full HP, where it does nothing; km3 sometimes uses it then. On a turn where none of his Pokémon is damaged (`noop_ability` in `positions_A.json`: 020315 t02, t04, t06; 020920 t02, t06; 023418 t01, t03, t05, t07), bare Ability steps are dropped from both plans, so a no-op does not count as a difference. The draft A rows are unchanged by it (all 34 compared). Which of two identical Indeedee ex uses Watch Over is not compared either.

Milestones: preparing an attacker (020920 t04, t06, t08; 023418 t03, t05, t07, t09; 020315 t06), adapting when the plan fails (020315 t08), managing a sacrifice (020315 t10). 023418 t11 carries none. One decision of his own (Sabrina's forced switch on game turn 6 of 023418, where he chose the unenergised Wailmer) falls on the opponent's turn and is not built.

New harness support: a Pokémon in a position may carry effects (`effects` on a board entry; used for Bonsly's -30 on 023418 t11) in `pg_pos.rs`; `pg_pos.rs` and the report script are updated in `harness/`.

## The positions as a test set for any pilot

`harness/run_pilot.sh BOT [SEEDS] [PG_POS_BINARY]` runs every position with the pilot code BOT (any code `parse_player_code` knows) at nice 19 and writes `runs_<BOT>/` (raw) and `report_<BOT>/` (the tables above, for that pilot) in about four seconds. For an experimental pilot, build the harness against the engine tree that contains it: `PGD_ENGINE=<engine dir> PGD_TARGET=<target dir> PGD_BIN=<binary> harness/pgd_build.sh 8` (it applies the print-only patch, which asserts its anchors are found exactly once, then builds `pg_pos.rs` as an example). Pilots built on `ExpectiMiniMaxPlayer` also print their root scores; others record only their choices. To add positions, extend `positions_A.py` (a position names a deck key; `--deck KEY=file` supplies the list) and rerun. Check: `kta3` gives exactly the same tables as `km3` on these 22 positions, as it should (km differs from kta only by the Training Area / Arena bonus, which changes no choice here).

## Files

`TABLES.md` (a table per game), `TURBO_SHARK.md`, `summary.json`, `totals.json`, `positions_A.json` and `positions_A.py` (the positions with their notes), `FRAME_READS.md` (how each hand was fixed), `raw/` (stdout JSON lines and the PGSTEP/PGDUMP root scores for every position and seed), `harness/` (the example, the print-only patch, the run and report scripts), `BUILD.txt` (hashes).
