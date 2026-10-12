# The new pause games, read against km3 (Oct 12, 2026)

Read by the Sonnet session "Opus agents progress". Branch `sonnet/video-read-2026-10-12` (new folder only; no hold file, nothing on main).
This is the same reading as the Oct 2 set (`rl/results/pause_games_decisions_2026-10-02/`), run on every game Codex has processed since then.

## What was read

- **28 games** with a Codex TURN_LEDGER (batches Oct 6, Oct 9, Oct 11; the three newest, 20261012_003458/004128/004435, included): **138 of Dustin's turns**.
- **121 of those turns became positions** (23 games): the board at the start of his turn, his hand as Codex read it from the video, points, Stadium, the opponent's board and hand size, and his actual plan for the turn from the ledger.
- **Not read:** 4 games with no deck list anywhere in the recording (20261004_214518, 20261004_214731, 20261005_034229, 20261006_012140; 11 turns), 1 game whose filmed list does not contain the cards its ledger shows (20261004_215749; 3 turns), and 3 single turns whose hand or board could not be built (20261006_020518 turn 13, 20261010_014541 turns 9 and 11). All are in `report_convert.json`.
- **km3**, 12 seeds per position, first action and plan, with the Oct 2 rules: a plan is cut after its first draw card (Professor's Research, Copycat, Poké Ball) and after Sabrina (the opponent then chooses); bare Ability labels do not name the user; EndTurn is ignored; draw order is noise.
- **Engine named:** the Oct 2 harness (`pg_pos`, engine main-8626a35). It is not the official engine main-c045ede; a rerun on c045ede needs `pg_pos` rebuilt against it (not done).
- **kx3 not run.** One position at 12 seeds kept all 16 cores busy for over 6 minutes before I stopped it, so the 121 positions would take about half a day. It can be run on a chosen subset.
- 6 of the 121 turns have no recorded plan (the game ended on a concession before he played anything). They are in the tables but not counted.

## Result (115 turns with a recorded plan)

| | turns |
|---|---|
| km3's first move is his first move (10 or more of 12 seeds) | 55 |
| split (3 to 9 of 12) | 6 |
| km3 almost never makes his first move (0 to 2 of 12) | 54 |
| km3's most common whole plan equals his | 34 |
| ... the same plan in 10 or more of 12 seeds | 31 |

### Where the plans part, by what km3 does there (81 turns whose plans differ)

| km3 does this at the first difference | turns | typical case |
|---|---|---|
| plays an Item or Supporter (or a different one, or earlier) | 31 | Lucky Ice Pop, Rare Candy, Steel Apron, Fragrant Forest before what he did. (Across the 54 turns where km3 almost never makes his first move, his own first move is Poké Ball in 11, Professor's Research in 4.) |
| evolves (another target, or earlier / later) | 12 | evolves a benched Pokémon he left, or the other target |
| attaches Energy (another target, or earlier) | 11 | mostly Fighting/Metal decks: to the Active where he chose a bench Pokémon, or before an Item |
| retreats | 10 | Seadra to Horsea (003458 turn 5); Retreat before an Evolve |
| benches a Basic | 8 | Darkrai ex, Honedge, Mega Sableye ex first |
| attacks | 5 | goes to the attack where he finished the build first |
| something else (tool target, ability, ends turn) | 4 | |

### Attack (55 turns where both plans run to the end of the turn; in 60 a plan is cut by a draw card or Sabrina, so it cannot be compared)

| | turns |
|---|---|
| same attack | 24 |
| a different attack | 5 |
| km3 attacks, he does not (he builds, or the ledger shows him declining an attack) | 7 |
| he attacks, km3 does not | 6 |
| neither attacks | 13 |

The "he attacks, km3 does not" turns need a card check before anyone trusts them: three are in the Aegislash / Melmetal ex / Magnezone game (20261005_034953), where the filmed deck lists a printing of Magnemite whose attack cost may not match the card he used.

### Examples from the three newest games (Kingdra ex / Team Rocket's Weezing ex)

- 003458 turn 3: he evolves the Active Horsea to Seadra, then attaches; km3 evolves the *benched* Horsea first (12/12).
- 003458 turn 5: he starts with Poké Ball (and ends the turn with Kingdra ex's Stormy Prison, which KOs Pichu); km3 retreats the Active Seadra into the benched Horsea before the Poké Ball (12/12).
- 003458 turns 7 and 9: he attacks (Stormy Prison on Dragonite); km3 plays Sabrina first (12/12) and the plan stops there because the opponent chooses the new Active.
- 003458 turn 11 (the opponent conceded before he played anything): km3 would attack with Stormy Prison (12/12).
- 004128 turn 4: same plan (Rare Candy, Kingdra ex, Stormy Prison for the win). Turn 2: km3 draws first (Professor's Research or Copycat) where he put down Soothing Shore first.
- 004435 turn 4: same first move (bench Horsea), then km3 retreats into the Weezing ex evolution, uses its ability and attacks with Hook, where he evolved, attached and played Hiking Trail without attacking.

## How far to trust it

- The audit: a helper compared the converted positions with the ledgers. Hand, points, Stadium and its owner, opponent hand size, both boards (cards, HP, Energy by type, Tools) match in all 121 after the fixes below; the id-to-game mapping is right. What it found, and what I changed: plan steps dropped for unrecognised ledger wording (fixed: 12 spellings now mapped), bench slots 'left/center/right' sorted alphabetically (fixed), a replaced Stadium and retreat payments missing from the discard (fixed), Rare Candy logged as "item_evolution" (fixed). Open: two Kingdra ex on one board (20261010_021629) can have their Seadra/Horsea stacks swapped; opponent discard is not tracked (0).
- **The opponent's list is unknown in every game.** His hidden cards are cycled from the pilot's own list, so km3 plays against a deck that is not the real one. Every row is marked approximate for that reason. The Oct 2 set had exact opponent lists for only its 65 computer-deck positions.
- **Status conditions are not represented** (the harness has no field): 15 positions have a Poisoned/Burned/Asleep Pokémon (noted per position). They matter for attack and retreat legality.
- Some evolution stacks are taken from the printed line (a Rare Candy may have skipped a stage); positions where the deck list holds too few copies were rebalanced and noted.
- One printing per card name (the filmed QR is semantic); card text can differ between printings of a name.
- His plan is as Codex wrote it. Where an ephemeral prompt or a target could not be read, the plan stops at that step (`plan_truncated_at`); 4 positions.
- A difference is a difference, not a mistake by either side: the Oct 2 reading found the same pattern (km3 chooses Supporter/Item order and retreat differently, rarely the attack).

## Files

- `PAUSE_GAMES_NEW_READ_sonnet.md` is this file; `km3_TABLES.md` the table per game (his plan, km3's first actions over 12 seeds, modal plan, category, what differs); `km3_summary.json` the same as data; `report_out.txt` the totals.
- `positions_all.json` the 121 positions; `decks/` the 23 deck files (`pg_pos --deck KEY=file`); `report_convert.json` what was left out and why; `games_meta.json` the captions as Codex's PAUSE_GAME.json gives them (some are inconsistent there).
- `harness/ledger_to_positions.py` (ledger + DECK_USED.json → positions, generic over the game), `harness/kw_report.py` (the comparison and tables), `harness/run_all.sh` (km3 on every position; uses `/home/dacz8976/pgd/pg_pos`, the Oct 2 harness binary), `harness/games_meta.py`.
- Rerun: `python3 harness/ledger_to_positions.py positions_all.json report_convert.json <game folders>`, then `harness/run_all.sh km3`, then `python3 harness/kw_report.py positions_all.json runs_km3 km3 km3 games_meta.json`.
