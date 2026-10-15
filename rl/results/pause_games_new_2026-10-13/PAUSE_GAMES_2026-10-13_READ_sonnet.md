> **Redone as v2, with Sleep and Poison, Kingambit's knock-out count and verified deck lists: see [v2/PAUSE_GAMES_2026-10-13_READ_v2_sonnet.md](v2/PAUSE_GAMES_2026-10-13_READ_v2_sonnet.md). Where the two disagree, v2 is right.**

# The 14 new pause games (Oct 12-13), read against km3: what is interesting

Read by the Sonnet session "Opus agents progress", Oct 13, for Dustin through the laptop. Branch `sonnet/pause-games-2026-10-13`, this folder only. Nothing on main, no hold file, no kx3 run. The import files of the batch folders were not read or used.

The first version of this read had the six games of BATCH_2026-10-13_REMAINING_SIX; the laptop then asked for all 14 new games (the other eight: BATCH_2026-10-12_NEW_LONG_VIDEOS 010706, 203719, 210041, 210823; BATCH_2026-10-12_ADDITIONAL_TWO 225319, 230258; BATCH_2026-10-13_NEWEST_TWO 022530, 030351).

## In short (for Dustin)

Fourteen games, seven wins and seven losses: 12 with the Glimmora / Alolan Muk / Regigigas (/ Kingambit) deck and 2 with the Haxorus / Dragonair / Druddigon deck. 92 of your turn starts could be rebuilt; km3 (our bot, on the official engine) played each 12 times with different dice. Three of the games (010706, 203719, 030351) have no deck list in their packet; I gave them the list of a game of the same named deck and marked their 28 turns "unverified" (every card the ledgers show fits those lists).

- **First moves.** km3's first move is yours in 55 of the 87 turns that have a plan of yours (63%); on the 60 turns with a verified deck, 35 (58%). Most of the differences are ties or order: among the 51 turns where km3 would leave your line at some step, the score for your step is exactly equal to km3's best in 17, within 50 points in 10 more, within 500 in 18. **Only 4 turns in the verified games have a real gap**, and 3 of them are in one game (010837). (The Oct 12 read had 48% first-move agreement; this deck and its openings are simpler.)
- **Two free points he did not take (game 010837).** The opponent's Active was Pichu, 30 HP. Turn 3 (his 2nd): Pawniard's Slash does exactly 30 and the Energy was on Pawniard; he retreated it, paying that Energy, instead. Turn 11: Kingambit had its two Energy; he healed Glimmet and used Hang Down (20), leaving Pichu at 10. km3 takes the knock-out both times (turn 3: Slash in 4 of 12 seeds, Copycat first in the other 8; turn 11: it retreats and uses Overlord's Blade) and scores your lines 10,600 and 9,200 below its own. At turn 3 it would have cost little: the opponent put Mega Kangaskhan ex in front for free by retreating Pichu the next turn anyway. At turn 11 he may have had a reason: Glimmet was knocked out on the opponent's turn, which raised the Blade to 180 for turn 13, where it knocked out Raticate ex.
- **A habit worth knowing.** You often attach the turn's Energy to the Active Pokémon and retreat it at once, paying with that Energy (010837 turn 3, 225319 turn 6, 020824 turn 7). It is a free retreat from the zone Energy. In 010837 turn 3 it cost the point above.
- **Where you look right and km3 does not.** 014423 turn 7 and 015659 turn 5: you put the Energy on a benched Pokémon; km3 puts it on the Active, which the opponent's attack knocks out next turn (Regigigas, 50 HP against 100 damage; Regigigas, 30 HP against Mega Lucario ex). km3 does not look at the opponent's next attack when it picks where the Energy goes.
- **Ilima.** In 203719 turn 7 and 210823 turn 8 (where you played it) and in 210041 turn 6 (where you did not) km3 plays the Ilima reset (damaged Regigigas back to hand, benched at 150 HP) in 12 of 12 seeds, so km3 knows the trick. It misses it only in 020824 turn 11 (it ranks Ilima 270 below a Lucky Ice Pop chain), where you played it. In 210041 turn 6 you kept the Ilima while your 40-HP Regigigas faced Mega Lucario ex's lethal Fighting hit (Regigigas is weak to Fighting); the game even warned you that a Supporter was still playable. Regigigas was knocked out next turn. km3's scores for the two lines tie, so I cannot call it a mistake, only an unused chance.
- **A weakness of the deck, not a play.** In 015659 and 210041 the opponent's Mega Lucario ex is a Fighting Pokémon; Regigigas, Glimmet, Glimmora, Alolan Muk and Alolan Grimer are all weak to Fighting (every hit on them does 20 more).
- **What our tools do not know.** (1) Kingambit's Overlord's Blade does 60 plus 40 per Pokémon of yours already knocked out; the position runner does not carry that count, so km3 saw 60 where the real damage was 140 to 200 (22 of the 92 turns have a Kingambit on your board, 14 of them after you had already lost a Pokémon). In 010706 turn 21 you won with it: 180 +20 weakness on a 130-HP Mega Gardevoir ex for 3 points; km3 would see 80. (2) Sleep is not represented: in the unverified game 030351 your Pokémon was Asleep in 4 turns, which produced the two biggest gaps of the read (8,600 and 10,100) and are not real disagreements. Poison on the opponent's Pokémon is also not represented (13 turns). (3) km3 spends actions on a Stadium that cannot help it (Fragrant Forest, no Grass Basic in your deck).
- **Rules switch 2.** 14 turns hold a card the switch changed: all 8 of 010837 (the opponent's Mega Kangaskhan ex) and all 6 of 210823 (the opponent's Meowth with Carefree Steps). km3's plan is identical on the older and the official engine in all 14, all 12 seeds each.

## What was done

- **Positions.** The 14 games went through the converter of main (`../pause_games_new_2026-10-12/harness/`, the version verified by the laptop's two panels), unchanged. Some packets needed a copy of the file first (`scripts/normalize_ledger.py`; the harness itself is not edited): 020824 writes each play's target in a free-text `details` field; 210041 and 210823 write targets only in `result`; 030351 names Pokémon by instance ("Dratini-1 → Dragonair-1"); 015011 writes the log list's printings under `variant_as_shown_in_log`; three packets (010706, 203719, 030351) have no 20-card list (see above; `deck_assumption_check.txt` compares each list with every card the ledgers show: none missing, none too many; the control on verified games is quiet). 92 positions; left out: 203719 turns 19 and 21 (his hand is empty, the converter cannot take an empty hand) and 015659 turn 11 (the opponent's hand count is missing). 030351 turn 15 could not be run (the position says his deck is empty, the assumed list leaves 4 cards).
- **km3.** `pg_pos_F`, sha256 129b96a7 (the pinned build of `../pause_positions_kx3_2026-10/builds/builds.txt`, official engine main-c045ede), seeds 1 to 12, one position at a time at nice 19, as in the kx3 spec. Before the new positions I ran it on 3 positions of the Oct 12 set and the 12-seed plans are identical to the laptop's committed km3 runs. 91 positions load with no problem; the 1,092 runs took under two minutes.
- **Comparison.** `report_out.txt` / `km3_TABLES.md` are the Oct 12 report script (plans cut at the first draw card, as there). Because a cut plan makes an ordering difference look like a different turn, I also ran the harness's forced mode (`scripts/forced_runs.py`, `runs_forced/`): his line is played as he played it, cut at its first draw card, and at each step km3 says what it would play and how far its score for his step is from its best.
- **The older engine** (`runs_km3_older_engine/`, the Oct 2 harness build, main-8626a35) for the 14 turns flagged for rules switch 2.
- **Cost.** About 6 minutes of one machine for everything (`scripts/run_all.sh` redoes the chain).

## The numbers

| | all 92 | 64 verified |
|---|---|---|
| Positions / games | 92 / 14 | 64 / 11 |
| With a plan of his | 87 | 60 |
| km3 first move = his (10 or more of 12 seeds) | 55 of 87 (63%) | 35 of 60 (58%) |
| km3 plays every step of his line (to its first draw card) | 37 | |
| km3 leaves his line at some step, in most seeds | 51 | |
| ...its best score minus the score of his step: tie / under 50 / 50-500 / 500-5,000 / over 5,000 | 17 / 10 / 18 / 2 / 4 | |
| ...of the 6 gaps of 500 or more | 010837 t03, t11, t07; 210823 t02 (Copycat or Research first, 877); 030351 t05, t13 (Sleep, unverified) | the first four |
| Turns that touch rules switch 2 | 14, km3 identical on both engines in 14 of 14 | |

`POSITION_TABLE.md` has one row per position (his line, km3's, the step where they part, and a reading of 48 turns that need one). `position_cards.txt` has the boards. The game turn numbers are the games' (1 is his first).

## The gaps that are real, in order

1. **010837, turn 3 (gap 10,600).** Pichu in front at 30 HP, Slash for exactly 30 with the Energy already on Pawniard; the only thing he gave up by attacking was the retreat into Glimmora.
2. **010837, turn 11 (gap 9,200).** The opponent had Mega Kangaskhan ex (180 HP, two Energy) on the Bench behind Pichu. km3's line takes a point now and puts Kingambit in front with a Heavy Helmet (-20 per hit); his line keeps Glimmet in front and lets the opponent's Raticate ex knock it out for the second point. At turn 13 he got 2 points from the Blade; the game then ended 2-2 with the opponent timing out. I cannot say his line was worse, only that km3 sees it as much worse and that the Pichu knock-out was free.
3. **210823, turn 2 (gap 877).** His first turn: Research (draw 2) or Copycat (the opponent held 5 cards: draw 5). km3 prefers Copycat; his hand had Alolan Muk and Mesagoza that Copycat would have shuffled away. A hand-quality judgement, not a clear miss.
4. **010837, turn 7 (gap 658).** After Rare Candy Kingambit he puts the Energy on Glimmet, km3 on Kingambit. His later turns show he used Glimmet as the piece that gets knocked out to charge the Blade.

Two of the four are about **taking a free point early**: with the opponent's 30-HP Pichu in front, km3 takes the knock-out each time, and he did not.

## Engine and tool notes (for the laptop)

- **Kingambit's Overlord's Blade and the position runner.** The engine counts "own Pokémon knocked out this game" per player (`own_knockouts_this_game`, state/mod.rs); `pg_pos.rs` (sha 790ae7b1b91e18f4, the pinned build's) builds a fresh state and never sets it, so it is 0 in every position. In 010837 it should be 2 at turns 9 and 11 and 3 at turns 13 and 15 (his Glimmora, Regigigas, then Glimmet; the opponent's points, 1, 1, 2, 2, are lower because Glimmora's Shattering Crystal flipped heads). If kx3 is run on any Kingambit turn the runner needs a `me.knockouts` field (a one-line State patch); otherwise read those turns knowing the Blade is 60.
- **Sleep and the other conditions.** Sleep is not represented: 4 of his turns in 030351, all unverified. A sleeping Pokémon cannot attack or retreat; km3 does both there. Poison on the opponent's Pokémon is not represented in 13 turns.
- **The converter and Ilima.** The converter does not follow Ilima's return-and-promote: the last attack label of the plans of 203719 t07 and 210823 t08 ("Attack:Giga Turbo") is wrong (the reviews say Glimmora's Venomous Hit); only those two comparisons are affected.
- **Empty hand.** The converter drops a turn whose hand is empty (203719 t19, t21); an empty hand is a legal position.
- **Every card the games show is in the engine.** All attack and Ability texts of the cards seen on the boards of the first six games are in the engine's text map, all Trainers have their own code (Arena of Antiquity, Soothing Shore, Protective Poncho, Electrical Cord, Rocky Helmet, Small Balloon, Leaf Cape, Fragrant Forest, Mesagoza). Whether each is right was not checked card by card; the eight added games were not checked this way.
- **Stadium use that cannot do anything.** At 020824 turns 9, 11 and 13 km3 adds `UseStadium` for the opponent's Fragrant Forest (a random Grass Basic from the deck) to its plan, with no Grass Basic in his deck. It costs nothing in the harness.
- **Lucky Ice Pop loops.** km3 replays a Pop after each heads, up to seven times in a turn (020824 turn 13); the seeds draw the coins, so it is not a sign of a plan.
- **Scores saturate.** In lost positions km3's best and second-best scores often tie (values near ±10,000 to ±22,000), and the choice is then the first on the list: 17 of the 51 departures from his line are exact ties, e.g. 014423 turn 9 (km3 attacks without the free Energy attach).

## Turns worth a kx3 look (for the cloud pilot; not run)

1. `KW-261013_010837000-t03`: Slash for the point, or the retreat.
2. `KW-261013_010837000-t11`: Overlord's Blade on Pichu, or Hang Down (needs the knock-out count first).
3. `KW-261013_010837000-t09`: the Blade for 140 on Mega Kangaskhan ex now, or healing Glimmet (same).
4. `KW-261013_020824000-t11`: the Ilima line (km3 under-ranks it only here).
5. `KW-261013_014423000-t07` (and 015659 t05): the Energy on the Bench or on the Pokémon that will be knocked out.
6. `KW-261012_210041000-t06`: the unused Ilima.

## Limits

- The opponent's list is unknown in every game; his hidden cards are filled from the pilot's own list ("approximate", as on Oct 12). The opponent's discard is what the ledger names (none of these games has unreadable discards).
- km3's plan is cut at its first draw card; Mesagoza's coin and Lucky Ice Pop's coins come from the seeds, not from what happened.
- 28 positions (010706, 203719, 030351) rest on an assumed deck list and are `usable: false`; I read them but the numbers above are given both ways.
- Game 015011 has 3 turns; the opponent never returned. Its Alolan Grimer printing is unsettled between A3 110 and two others (the log list says A3 110 and that is used).
- 020824 turn 11 keeps a plan cut at the final Energy (a Pokémon returned to hand and benched again).
- Reviews were read as written. 8 of the 92 cards in `position_cards.txt` show no review line (that game's REVIEW.md table has another layout).

## Files

`PAUSE_GAMES_2026-10-13_READ_sonnet.md` (this), `POSITION_TABLE.md`, `position_cards.txt`, `positions_all.json`, `decks/`, `position_list.tsv/json` (flags by function), `games_meta.json`, `report_convert.json`, `deck_assumption_check.txt`, `run_ids.txt`, `report_out.txt`, `km3_TABLES.md`, `km3_summary.json`, `runs_km3/`, `runs_forced/` (`forced_summary.json`), `runs_km3_older_engine/`, `scripts/`.
