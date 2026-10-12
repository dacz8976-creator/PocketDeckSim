> **SUPERSEDED for 107 of the 125 positions (Oct 12, evening).** The laptop's review (`REVIEW_POSITIONS_laptop.md`) found wrong cards of Dustin's in these positions (two cards
> that share a name had been merged) and plan steps missing. The positions were rebuilt (`CONVERTER_FIX_sonnet.md`). Everything below was measured on the first version of the
> positions: `position_list.tsv`, column `km3_read`, says for each position whether its km3 read `stands` (the position is unchanged: 14), is `superseded` (the position changed:
> 107) or has none (a position the first version did not have: 4). Do not quote the totals below. km3 was not rerun on the old harness: the kx3 position spec re-measures km3 on
> the official engine.

# The new pause games, read against km3 (Oct 12, 2026)

Read by the Sonnet session "Opus agents progress". Branch `sonnet/video-read-2026-10-12` (new folder only; no hold file, nothing on main).
This is the same reading as the Oct 2 set (`rl/results/pause_games_decisions_2026-10-02/`), run on every game Codex has processed since then.
Follow-ups the same day: `MAGNEMITE_CHECK_sonnet.md` (closed, no engine problem) and `position_list.tsv` (the list for a bot comparison, with the rules switch 2 flags).

## What was read

- **28 games** with a Codex TURN_LEDGER (batches Oct 6, Oct 9, Oct 11; the three newest, 20261012_003458/004128/004435, included): **138 of Dustin's turns**.
- **121 of those turns became positions** (23 games): the board at the start of his turn, his hand as Codex read it from the video, points, Stadium, the opponent's board and hand size, and his actual plan for the turn from the ledger.
- **Not read:** 4 games with no deck list anywhere in the recording (20261004_214518, 20261004_214731, 20261005_034229, 20261006_012140; 11 turns), 1 game whose filmed list does not contain the cards its ledger shows (20261004_215749; 3 turns), and 3 single turns whose hand or board could not be built (20261006_020518 turn 13, 20261010_014541 turns 9 and 11). All are in `report_convert.json`.
- **km3**, 12 seeds per position, first action and plan, with the Oct 2 rules: a plan is cut after its first draw card (Professor's Research, Copycat, Poké Ball) and after Sabrina (the opponent then chooses); bare Ability labels do not name the user; EndTurn is ignored; draw order is noise.
- **Engine named:** the Oct 2 harness (`pg_pos`, engine main-8626a35). It is not the official engine main-c045ede; a rerun on c045ede needs `pg_pos` rebuilt against it (not done). `position_list.tsv` says which positions need that.
- **kx3 not run.** One position at 12 seeds kept all 16 cores busy for over 6 minutes before I stopped it, so the 121 positions would take about half a day. It can be run on a chosen subset.
- 6 of the 121 turns have no recorded plan (the game ended on a concession before he played anything). They are in the tables but not counted.
- Printings: his deck cards use the filmed list's printing, and where the ledger itself names the printing of a Pokémon on his board ("A2a 053; Tackle20, HP60") that printing wins. This was fixed after the Magnemite check, see `MAGNEMITE_CHECK_sonnet.md`.

## Result (115 turns with a recorded plan)

| | turns |
|---|---|
| km3's first move is his first move (10 or more of 12 seeds) | 55 |
| split (3 to 9 of 12) | 8 |
| km3 almost never makes his first move (0 to 2 of 12) | 52 |
| km3's most common whole plan equals his | 36 |
| ... the same plan in 10 or more of 12 seeds | 32 |

### Where the plans part, by what km3 does there (79 turns whose plans differ)

| km3 does this at the first difference | turns | typical case |
|---|---|---|
| plays an Item or Supporter (or a different one, or earlier) | 28 | Lucky Ice Pop, Rare Candy, Steel Apron, Fragrant Forest before what he did. (Across the 52 turns where km3 almost never makes his first move, his own first move is Poké Ball in 11.) |
| evolves (another target, or earlier / later) | 13 | evolves a benched Pokémon he left, or the other target |
| attaches Energy (another target, or earlier) | 10 | mostly Fighting/Metal decks: to the Active where he chose a bench Pokémon, or before an Item |
| retreats | 10 | Seadra to Horsea (003458 turn 5); Retreat before an Evolve |
| benches a Basic | 8 | Darkrai ex, Honedge, Mega Sableye ex first |
| attacks | 6 | goes to the attack where he finished the build first |
| something else (tool target, ability, ends turn) | 4 | |

### Attack (55 turns where both plans run to the end of the turn; in 60 a plan is cut by a draw card or Sabrina, so it cannot be compared)

| | turns |
|---|---|
| same attack | 27 |
| a different attack | 5 |
| km3 attacks, he does not (he builds, or the ledger shows him declining an attack) | 7 |
| he attacks, km3 does not | 3 |
| neither attacks | 13 |

### Rules switch 2 flags (`position_list.tsv`)

35 of the 121 positions are flagged: his deck, the opponent's cards seen in the game, or a card on the table at that turn is on the switch's list (`rl/engine-2026-10-12/README.md`, `PLAN.md` section 0). A flagged position should be read on the official engine main-c045ede; the other 86 hold no card the switch changed.

| game | positions flagged | why |
|---|---|---|
| 20261005_031138 | 3 of 3 | Togekiss in his deck (coin ability) |
| 20261005_183108 | 5 of 5 | Mega Sableye ex on both sides (Cursed Jewel, return damage takes Weakness) |
| 20261006_012927 | 5 of 5 | Meowth in his deck (coin ability) |
| 20261006_020518 | 8 of 8 | Conkeldurr in his deck (Guts); the opponent's Togedemaru (Bristling Spikes) |
| 20261010_012303 | 6 of 6 | Conkeldurr (Guts) |
| 20261010_013009 | 8 of 8 | Conkeldurr (Guts) |

None of the 23 games has a Will, a Fossil, an Ariados (deck 12 / Trap Territory) or Luxury Coin in his deck or seen on the opponent's side. "Seen" is a lower bound: the opponent's hidden cards are unknown, so an unflagged game can still meet one.

### Examples from the three newest games (Kingdra ex / Team Rocket's Weezing ex)

- 003458 turn 3: he evolves the Active Horsea to Seadra, then attaches; km3 evolves the *benched* Horsea first (12/12).
- 003458 turn 5: he starts with Poké Ball (and ends the turn with Kingdra ex's Stormy Prison, which KOs Pichu); km3 retreats the Active Seadra into the benched Horsea before the Poké Ball (12/12).
- 003458 turns 7 and 9: he attacks (Stormy Prison on Dragonite); km3 plays Sabrina first (12/12) and the plan stops there because the opponent chooses the new Active.
- 003458 turn 11 (the opponent conceded before he played anything): km3 would attack with Stormy Prison (12/12).
- 004128 turn 4: same plan (Rare Candy, Kingdra ex, Stormy Prison for the win). Turn 2: km3 draws first (Professor's Research or Copycat) where he put down Soothing Shore first.
- 004435 turn 4: same first move (bench Horsea), then km3 retreats into the Weezing ex evolution, uses its ability and attacks with Hook, where he evolved, attached and played Hiking Trail without attacking.

## How far to trust it

- The audit: a helper compared the converted positions with the ledgers. Hand, points, Stadium and its owner, opponent hand size, both boards (cards, HP, Energy by type, Tools) match in all 121; the id-to-game mapping is right. It found, and I fixed: plan steps dropped for other spellings of a play's kind, bench slots 'left/center/right' sorted alphabetically, a replaced Stadium and retreat payments missing from the discard, Rare Candy logged as "item_evolution". The Magnemite check then found one more (a QR variant with two printings fell back to the database's first printing); fixed and everything redone. Open: two Kingdra ex on one board (20261010_021629) can have their Seadra/Horsea stacks swapped; opponent discard is not tracked (0).
- **The opponent's list is unknown in every game.** His hidden cards are cycled from the pilot's own list, so km3 plays against a deck that is not the real one. Every row is marked approximate for that reason. The Oct 2 set had exact opponent lists for only its 65 computer-deck positions.
- **Status conditions are not represented** (the harness has no field): 15 positions have a Poisoned/Burned/Asleep Pokémon (noted per position). They matter for attack and retreat legality.
- Some evolution stacks are taken from the printed line (a Rare Candy may have skipped a stage); positions where the deck list holds too few copies were rebalanced and noted.
- His plan is as Codex wrote it. Where a prompt or a target could not be read, the plan stops at that step (`plan_truncated_at`); 4 positions.
- A difference is a difference, not a mistake by either side: the Oct 2 reading found the same pattern (km3 chooses Supporter/Item order and retreat differently, rarely the attack).

## Files

- `PAUSE_GAMES_NEW_READ_sonnet.md` is this file; `km3_TABLES.md` the table per game (his plan, km3's first actions over 12 seeds, modal plan, category, what differs); `km3_summary.json` the same as data; `report_out.txt` the totals.
- `MAGNEMITE_CHECK_sonnet.md`: the Magnemite A1 097 card check (card text, the engine's cost check, the video), closed.
- `position_list.tsv` / `position_list.json`: one row per position for a bot comparison (nothing was run for it): game, turn, his move, km3's first move and whether they match, deck and opponent names, and the rules switch 2 flag with the cards behind it. Details at the top of `harness/position_list.py`.
- `positions_all.json` the 121 positions; `decks/` the 24 deck files (`pg_pos --deck KEY=file`); `report_convert.json` what was left out and why; `games_meta.json` the captions as Codex's PAUSE_GAME.json gives them (some are inconsistent there).
- `harness/ledger_to_positions.py` (ledger + DECK_USED.json → positions, generic over the game), `harness/kw_report.py` (the comparison and tables), `harness/position_list.py`, `harness/run_all.sh` (km3 on every position; uses `/home/dacz8976/pgd/pg_pos`, the Oct 2 harness binary), `harness/games_meta.py`.
- Rerun: `python3 harness/ledger_to_positions.py positions_all.json report_convert.json <game folders>`, then `bash harness/run_all.sh km3`, then `python3 harness/kw_report.py positions_all.json runs_km3 km3 km3 games_meta.json`.
