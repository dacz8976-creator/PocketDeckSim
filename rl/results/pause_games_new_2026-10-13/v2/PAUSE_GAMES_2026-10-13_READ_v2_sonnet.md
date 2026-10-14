# The 14 new pause games, read again (v2): Sleep and Poison, the knock-out count, verified deck lists

Redo of `../PAUSE_GAMES_2026-10-13_READ_sonnet.md` by the Sonnet session "Opus agents progress", Oct 13, for Dustin through the laptop, after Astra's review of the first read. Branch `sonnet/pause-games-v2-2026-10-13` (from main 28df6315), this folder only (plus a one-line banner on the first read). No hold file, no kx3 run, nothing on main. The first read stays as it was; where the two disagree, this one is right.

What was redone, and why:

1. **The two harness fixes on main (28df6315).** `ledger_to_positions.py` now writes `conditions` on board entries and `me.knockouts`, and `pg_pos.rs` reads both. The first read ran without them: Sleep and Poison were missing, and Kingambit's Overlord's Blade counted 60 on every turn. All 92 positions were converted again and km3 re-run on `pg_pos_F_cond` (sha256 5c4859949a88a28b: the same engine as `pg_pos_F`, cd20a97a, with main's new `pg_pos.rs` and the same print-only patch), seeds 1-12, forced mode, nice 19.
2. **Verified deck lists for the three games that had none** (010706, 203719, 030351): the 28 positions are now `usable`.

## In short (for Dustin)

- **The deck lists were right.** For the three games whose packets had no 20-card list I built the list from the filmed QR code and checked it against the live log snapshot and against every card the ledger shows. The QR and the snapshot agree in all three (same cards, same counts, each snapshot printing is one the QR card allows, same Energy), and the lists are card for card the ones I had assumed from games of the same named deck. So the 28 positions are on verified lists and nothing in them moved because of the decks. What moved them is the Sleep, the Poison and the knock-out count.
- **Sleep turns (game 030351): the two huge gaps were artefacts, and they are gone.** Your Dragonair (turn 5) and Druddigon (turn 13) were Asleep and were knocked out by Bad Dreams at the checkup. The first read had no Sleep, so km3 attacked with them and scored your line 8,600 and 10,100 lower. With Sleep km3 plays what you played (turn 5 ties; turn 13 it plays Professor's Research as you did). One thing the first read also got wrong in this game: the two checkup knock-outs were missing from your discard, so the position said your deck was empty when it still held 4 cards (turn 15 could not be run). That is fixed, and turn 15 runs now.
- **Kingambit turns (game 010837 and others): the Blade now counts, and it found one new free point.** With the real count (1 to 3 of your Pokémon already knocked out) the Blade is 100, 140 or 180 instead of 60. Two things follow. (a) **203719 turn 17 is new**: Glimmora had 10 HP, you healed it and hit Drampa for 30; with one of your Pokémon already knocked out, Kingambit's Blade is exactly 100, and the Active Drampa had exactly 100 HP. km3 retreats into Kingambit and takes the point (1-1 to 2-1); it scores your line 9,900 below (the first read had 40). (b) In 010837 the picture is as before: turns 3 and 11 (the 30-HP Pichu) are still the two free points, turn 9's gap grows from 340 to 787 now that the Blade is really 140, and in 010706 turn 21 km3 now sees that your Blade wins the game (180 plus 20 weakness on a 130-HP Mega Gardevoir ex), where it saw 80 before.
- **Rules switch 2 is still clean**: km3 plays the same plan on the older engine and on the official one in all 14 flagged turns, all 12 seeds, now with the same position reader on both builds (see the notes: the first comparison used an older reader that does not know the count, and one turn differed for that reason alone).
- **Updated list of turns worth a kx3 look** (not run): 010837 t03, 010837 t11, 203719 t17 (new), 010837 t09, 020824 t11, 014423 t07 with 015659 t05, 210041 t06. Details below.

## What changed from the first read

All 92 positions load, all `usable`. km3's plans differ from the first read in 11 positions, in all 12 seeds of each (10 changed, and 030351 t15 is newly runnable). In three of them (010706 t21, 203719 t17, 010837 t13) the steps are the same and only the end differs: the Blade now knocks out, or wins, so no `EndTurn` follows it. Every other position is plan-for-plan the same as in the first read.

| position | what is new in it | km3: first read → v2 | gap to his line: first read → v2 |
|---|---|---|---|
| 030351 t03 | his Active Dratini Asleep | Place, Stadium, Research → Place, **Evolve (cures the Sleep)**, Research | 12 → 0 (tie) |
| 030351 t05 | Dragonair (20 HP) Asleep, knocked out at the checkup | Evolve, Stadium, Energy, Draconic Whip → Evolve, Stadium, Dragon's Blessing, Energy, promotion at the checkup | 8,558 → 0 |
| 030351 t07 | Haxorus Asleep | Pop, Pop, Stadium, Blessing → Pop, Pop, Blessing, Stadium (order) | 0 → 70 |
| 030351 t13 | Druddigon Asleep, knocked out at the checkup | Retreat, Iris, Energy, Frenzied Blade → **Professor's Research** (as his line) | 10,096 → none |
| 030351 t15 | the two checkup knock-outs back in the discard (could not be run) | — → Energy, Retreat, Iris, Blessing, Frenzied Blade | — → 10,030 (order, see below) |
| 010837 t13 | 3 of his Pokémon knocked out: Blade 180 | Energy, Blade (60) → Energy, Blade (**180: knocks out Raticate ex, 2 points**) | none → none |
| 010837 t15 | the same count | Energy, Blade → **Blade alone: a winning knock-out** (Mega Kangaskhan ex 180 HP at 2-2) | — |
| 010837 t09 | 2 knocked out: Blade 140 | same plan | 340 → **787** |
| 010706 t21 | 3 knocked out: Blade 180 (+20) | same two steps; **the game now ends there (his win)** | 0 → 0 |
| 203719 t17 | 1 knocked out: Blade exactly 100 | same plan, now a knock-out | 40 → **9,935** |
| 203719 t11 | the opponent's Active Drampa Poisoned | Helmet and Energy, Stadium → Energy first, Helmet, Stadium | 10 → 21 |
| 210041 t14 | the opponent's Active Riolu Poisoned; 3 knocked out | Retreat, Energy → Energy, Slash (no plan of his; he conceded; no weight; I did not trace which of the two moved it) | — |

Unchanged on purpose: 010837 t03 (10,628), t11 (9,221), t07 (658) and 210823 t02 (877). In t11 the Blade already knocked out the 30-HP Pichu at 60, so the count changes nothing there.

## The 28 positions now on verified lists

010706 (11 positions), 203719 (9) and 030351 (8). Method (`scripts/normalize_ledger.py`, `deck_from_qr_check.txt`): the filmed QR (`QR_DECODE.json`, `card_slot_count` 20; 15, 15 and 13 distinct cards) and the live log snapshot (`DECK_LOG_SNAPSHOT.json`, `verified_live_log_snapshot`, 20 slots) give the list; the script requires the same cards and counts, each snapshot printing among the printings of the QR card, and the same Energy, and prints `AGREE` or `DISAGREE`. Result: **AGREE in all three.** Then `deck_assumption_check.txt` against every card in the ledgers: none missing, none too many. The three lists equal the lists of the first read card for card (`diff` of the sorted deck files is empty). Nothing disagreed, so nothing is marked otherwise.

## The numbers

| | first read | v2 |
|---|---|---|
| Positions / usable | 92 / 64 | 92 / 92 |
| With a plan of his | 87 | 88 (030351 t15 runs now) |
| km3 first move = his (10 or more of 12 seeds) | 55 of 87 (63%) | 55 of 88 (63%) |
| km3 plays every step of his line (to its first draw card) | 37 | 37 |
| km3 leaves his line at some step, in most seeds | 51 | 51 |
| ...gap: tie / under 50 / 50-500 / 500-5,000 / over 5,000 | 17 / 10 / 18 / 2 / 4 | 18 / 8 / 18 / 3 / 4 |
| Gaps of 500 or more | 010837 t03, t11, t07; 210823 t02; 030351 t05, t13 | 010837 t03 (10,628), 030351 t15 (10,030, order), 203719 t17 (9,935), 010837 t11 (9,221), 210823 t02 (877), 010837 t09 (787), 010837 t07 (658) |
| Positions with the Blade in play | 22 Kingambit turns, count 0 in all | 22 Kingambit turns, 18 with a count above 0; 47 of 92 positions have a count above 0 |
| Positions with a Special Condition | none | 17: his Pokémon Asleep in 4 (030351), the opponent's Poisoned in 13 |
| Rules switch 2 (14 turns) | identical in 14 of 14 | identical in 14 of 14 |

In 11 of the 88 positions with a plan, his line is cut before its first draw card because a later step is not legal in the harness state. A bare `Ability` step is now resolved when exactly one Ability is legal; that freed 030351 t05, t07 and t15, which were cut at the Ability on my first v2 pass.

## The gaps that matter, in order

1. **010837 t03 (10,628), unchanged.** Pichu 30 HP in front, Slash for exactly 30 with the Energy on Pawniard; he retreated it, paying that Energy.
2. **030351 t15 (10,030), new, an order effect.** He used Dragon's Blessing first (a Metal from the discard to the Active Haxorus), retreated paying with it, played Iris and knocked out Igglybuff with Frenzied Blade (2 points). km3 plays the same Retreat, Iris and Frenzied Blade, and the Blessing too, but starts with the Fighting Energy attach. The first-step score of the Blessing is 10,030 below (-18,763 against -8,733). Same cards, a different order; I did not trace why the score gap is that large (the position is lost, 0-2, where scores saturate), so I do not rate it as a different turn.
3. **203719 t17 (9,935), new.** The exact-100 Blade described above. The ledger's damage trail on that Drampa (100, 70, 60 after his turn, 50, then 20 and 10 on turn 19) confirms its 100 HP, and the Blade count of 1 matches the opponent's single point at the time. After his actual turn Glimmora was knocked out (the opponent's second point).
4. **010837 t11 (9,221), unchanged.** Pichu (30 HP) in front with Mega Kangaskhan ex behind; km3 retreats Glimmet and knocks Pichu out with the Blade; he used Hang Down for 20. He may have wanted Glimmet knocked out to charge the Blade (180 at turn 13, which then knocked out Raticate ex).
5. **210823 t02 (877), unchanged.** Research or Copycat on the first turn; a hand-quality judgement.
6. **010837 t09 (787, was 340)** and **t07 (658).** The Blade now really does 140 at t09 (no knock-out on the 180-HP Mega Kangaskhan ex); at t07 it is the Energy on Glimmet or on Kingambit.

The free-point pattern now has three entries: 010837 t03 (Slash), 010837 t11 (Blade on a 30-HP Pichu) and 203719 t17 (Blade for exactly 100).

## Turns worth a kx3 look (for the cloud pilot; not run)

The runner on main now carries the count and the conditions, so the Kingambit turns can be run.

1. `KW-261013_010837000-t03`: Slash for the point, or the retreat.
2. `KW-261013_010837000-t11`: Overlord's Blade on Pichu, or Hang Down (count 2).
3. `KW-261012_203719000-t17` (new): the exact-100 Blade on Drampa after the retreat, or the Pops and Venomous Hit (count 1).
4. `KW-261013_010837000-t09`: the Blade for 140 now, or healing Glimmet (count 2).
5. `KW-261013_020824000-t11`: the Ilima line (km3 under-ranks it only here).
6. `KW-261013_014423000-t07` (and 015659 t05): the Energy on the Bench or on the Pokémon that will be knocked out.
7. `KW-261012_210041000-t06`: the unused Ilima.

Not worth a kx3 run: 030351 t15 (order), the Sleep turns (ties or order now), 010706 t21 (his win, km3 agrees).

## Engine and tool notes (for the laptop)

- **The new reader works.** `scripts/check_state_dump.py` runs `pg_pos_F_cond --dump-state` on all 92 positions and compares the engine state with the position: `own_knockouts_this_game` and every condition on every Pokémon match, 92 of 92 (47 positions with a count above 0, 17 sides with a condition; `state_dump_check.txt`).
- **Rules switch 2, like for like.** The Oct 2 harness build used for the older engine (`/home/dacz8976/pgd/pg_pos`, main-8626a35) has the old `pg_pos.rs`, which ignores `conditions` and `knockouts`. Run as it was, 13 of the 14 flagged turns were identical and 010837 t15 differed in all 12 seeds (it attached before the Blade because it counted 60); that was the reader, not the engine (`runs_km3_older_engine_old_reader/`, kept for the record). I rebuilt the older engine's tree with main's new `pg_pos.rs` (`scripts/build_older_engine_cond.sh`, `/home/dacz8976/pgx/pg_pos_D_cond`, sha256 48772afd4371c53a...): **14 of 14 identical** (`engine_comparison.txt`, `runs_km3_older_engine/`).
- **A shape in the 030351 packet that the converter does not handle.** The owner row of a turn that ended in a checkup knock-out has a `board_after` that is already past the knock-out (the Pokémon and its Energy are gone) and then lists the promotion. The converter reads that board as the end of the turn, so the knocked-out Pokémon never reaches the discard and the deck count is off. `scripts/normalize_ledger.py` puts it back (Dragonair at turn 5, Druddigon at turn 13, each with its two Metal; `deck_from_qr_check.txt`). If more Sleep or Poison games come, main's converter needs the same step.
- **`me.knockouts` only.** The converter writes the count for his side only; the opponent's `knockouts` stays empty (no opponent deck here has a card that uses it).
- **The same converter limits as before**, unchanged: the last attack label after Ilima's promotion is wrong in 203719 t07 and 210823 t08; a turn with an empty hand is dropped (203719 t19, t21); 015659 t11 is left out (the opponent's hand count is missing).
- **A bare `Ability` in his line** is now resolved by `scripts/forced_runs.py` when exactly one Ability is legal (Dragonair's Dragon's Blessing). With two legal Abilities the line is still cut there.
- **Scores saturate in lost positions** (values near ±10,000 to ±22,000, ties at the top, the first in the list wins): 18 of the 51 departures are exact ties.

## What was done

`scripts/run_all.sh` redoes the chain (77 seconds on this machine; I ran it end to end once more before committing and every output file is byte-identical to the one this document was written from; the older-engine build is 3.5 minutes more and is separate, `build_older_engine_cond.sh`): `convert.sh` (normaliser, then main's converter, then the 14 games are split out), `run_km3.sh` (92 positions x 12 seeds), `kw_report.py` of the Oct 12 harness, `forced_runs.py`, the older-engine run and `compare_engines.py`, `check_state_dump.py`, `check_deck_assumption.py`, `position_cards.py`, `make_table.py`. The harness itself is not edited.

## Limits

- The opponent's list is unknown in every game; his hidden cards are filled from the pilot's own list ("approximate", as before).
- km3's plan is cut at its first draw card; coin flips (Mesagoza, Lucky Ice Pop) come from the seeds, not from what happened.
- The gaps are km3's own evaluation at seed 1; very negative numbers mean km3 thinks the game is lost.
- Game 015011 has 3 turns; the opponent never returned. Its Alolan Grimer printing is unsettled between A3 110 and two others (the log list says A3 110 and that is used).
- 020824 turn 11 keeps a plan cut at the final Energy (a Pokémon returned to hand and benched again).
- 210041 t14: I did not find which of the new facts (Poison on the Riolu, the count of 3) changed km3's plan; no plan of his, so no weight.
- Reviews were read as written. 8 of the 92 cards in `position_cards.txt` show no review line (that game's REVIEW.md table has another layout).

## Files

`PAUSE_GAMES_2026-10-13_READ_v2_sonnet.md` (this), `POSITION_TABLE.md` (92 rows, 52 with a reading), `position_cards.txt` (now with the knock-out counts and `COND:` marks), `positions_all.json`, `decks/`, `position_list.tsv/json`, `games_meta.json`, `report_convert.json`, `deck_from_qr_check.txt`, `deck_assumption_check.txt`, `state_dump_check.txt`, `engine_comparison.txt`, `run_ids.txt`, `run_ids_switch2.txt`, `report_out.txt`, `km3_TABLES.md`, `km3_summary.json`, `runs_km3/`, `runs_forced/` (`forced_summary.json`), `runs_km3_older_engine/`, `runs_km3_older_engine_old_reader/`, `scripts/`.
