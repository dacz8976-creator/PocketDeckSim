# The six new pause games (Oct 13), read against km3: what is interesting

Read by the Sonnet session "Opus agents progress", Oct 13, for Dustin through the laptop. Branch `sonnet/pause-games-2026-10-13`, this folder only. Nothing on main, no hold file, no kx3 run.

## In short (for Dustin)

Six games with the Glimmora / Alolan Muk / Regigigas / Kingambit deck: three wins (two because the opponent stopped playing, one concession) and three losses (two on points, one he conceded). 34 of his turn starts could be rebuilt (one more was left out). On each, km3 (our bot, on the official engine) played the turn 12 times with different dice.

- **First moves.** km3's first move is his in 15 of the 32 turns that have a plan of his: 47%, the same as on the 24 games of Oct 12 (55 of 115, 48%). That is not the interesting part. Most of the "differences" are ties or order: in 8 turns km3's scores for his move and its own are exactly equal, and in 9 more they are within a few hundred points of numbers that run to ±20,000. Only 3 turns have a real gap, all in one game.
- **The one that looks like a miss of his (game 010837, his 2nd turn).** The opponent's Active was Pichu with 30 HP. Pawniard's Slash does 30, and he had put the Energy on Pawniard. He retreated Pawniard (paying that Energy) instead of attacking, so he missed a point on turn 3. km3 attacks with Slash in 4 of 12 seeds and scores his retreat 10,600 below its best. It would have cost him little: the opponent put Mega Kangaskhan ex in front by retreating Pichu for free the next turn anyway.
- **The same thing again, four of his turns later (same game, game turn 11).** Pichu again in front at 30 HP. He healed and used Glimmet's Hang Down (20), leaving Pichu at 10. km3 retreats Glimmet and knocks Pichu out with Kingambit's Overlord's Blade (Kingambit already had its two Energy). km3 scores his line 9,200 below its own, the biggest gap of the six games. His reason may be the plan he followed: Glimmet was knocked out on the opponent's turn, which raised the Blade to 180 for turn 13, where it knocked out Raticate ex.
- **Where he looks right and km3 does not.** In 014423 (turn 7) and 015659 (turn 5) he puts the Energy on a Pokémon on the Bench, km3 puts it on the Active Pokémon that the opponent's attack will knock out next turn (Regigigas, 50 HP against 100 damage; Regigigas, 30 HP against Mega Lucario ex). km3 does not look at the opponent's next attack when it chooses where the Energy goes.
- **A clever line km3 misses.** 020824, turn 11: he plays Ilima to put the damaged Regigigas back in his hand, benches it at 150 HP and retreats into it, instead of chaining Lucky Ice Pops. km3 puts Ilima 270 points below its Pop chain.
- **A weakness of the deck, not a play.** In 015659 (lost, he conceded at 0-2) almost everything he plays (Regigigas, Glimmet, Glimmora, Alolan Muk, Alolan Grimer) has a Fighting weakness, and the opponent's Mega Lucario ex is Fighting: every attack on them does 20 more.
- **What our tools do not know.** (1) Kingambit's Overlord's Blade does 60 plus 40 per Pokémon of yours already knocked out; the position runner does not carry that count, so km3 saw 60 where the real damage was 140 (turns 9 and 11) and 180 (turns 13 and 15). That makes km3's choices in the 5 Kingambit turns understated, not wrong. (2) Poison and other conditions are not represented (3 turns). (3) km3 spends actions on a Stadium that cannot help it (Fragrant Forest, no Grass Basic in his deck).
- **Rules switch 2.** Eight turns (all of game 010837) hold Mega Kangaskhan ex, whose second punch the switch changed. km3's plan is identical on the older and on the official engine in all 8 turns, all 12 seeds.

## What was done

- **Positions.** The six games went through the converter of main (`../pause_games_new_2026-10-12/harness/`, the version verified by the laptop's two panels), unchanged. Two things about these packets needed a copy of the file first (`scripts/normalize_ledger.py`, the harness itself is not edited): game 020824 writes each play's target and result in a free-text `details` field and no `target` (without this its turns 3 to 13 came out with empty or short plans), and game 015011 writes the log list's printings under `variant_as_shown_in_log` (without this its Regigigas became the A2 143 card; the other five games, the same 20 cards, have B3 134). 34 positions in 6 games; 015659's turn 11 is left out (the opponent's hand count is missing); 020824's turn 11 keeps a plan cut at the final Energy (a Pokémon returned to hand and benched again). The six decks are the same 20 cards.
- **km3.** `pg_pos_F`, sha256 129b96a7 (the pinned build of `../pause_positions_kx3_2026-10/builds/builds.txt`, official engine main-c045ede), seeds 1 to 12, one position at a time at nice 19, as in the kx3 spec. Before the new positions I ran it on 3 positions of the Oct 12 set and the 12-seed plans are identical to the laptop's committed km3 runs (3 of 3). All 34 positions load with no problem. The 408 runs took 12 to 33 seconds.
- **Comparison.** `report_out.txt` / `km3_TABLES.md` are the Oct 12 report script (plans cut at the first draw card, as there). Because a cut plan makes an ordering difference look like a different turn, I also ran the harness's forced mode (`scripts/forced_runs.py`, `runs_forced/`): his line is played as he played it, cut at its first draw card, and at each step km3 says what it would play and how far its score for his step is from its best.
- **The older engine** (`runs_km3_older_engine/`, the Oct 2 harness build, main-8626a35) for the 8 turns flagged for rules switch 2.
- **Cost.** Under 4 minutes of one machine for everything (`scripts/run_all.sh` redoes the chain).

## The numbers

| | |
|---|---|
| Positions / games | 34 / 6 (1 more turn left out) |
| With a plan of his | 32 (2 are turns where the opponent never returned) |
| km3 first move = his (10 or more of 12 seeds) | 15 of 32 (47%); split 4, differ 13 (`report_out.txt`) |
| Whole plan the same in 10 or more of 12 seeds | 7 of 32 |
| km3 plays every step of his line (to its first draw card) | 12 of 34 |
| km3 leaves his line at some step, in most seeds | 20 of 34 |
| ...gap between km3's best score and the score of his step: tie / under 50 / 50-500 / 500-5,000 / over 5,000 | 8 / 1 / 8 / 1 / 2 |
| Turns that touch rules switch 2 | 8 (game 010837), km3 identical on both engines in 8 of 8 |
| Opponent cards the ledger cannot settle | 6 positions (a Combee in game 020824), no effect on the plans |

`POSITION_TABLE.md` has one row per position (his line, km3's, the step where they part, and a reading of the 31 turns that need one). `position_cards.txt` has the boards. The game turn numbers are the games' (1 is his first).

## The three real gaps, in order

1. **010837, turn 3 (gap 10,600).** The Slash case: Pichu in front at 30 HP, Slash for exactly 30 with the Energy already on Pawniard, and the only thing he gave up by attacking was the retreat into Glimmora.
2. **010837, turn 11 (gap 9,200).** The case above. The opponent had Mega Kangaskhan ex (180 HP, two Energy) on the Bench behind Pichu. km3's line takes a point now and puts Kingambit in front with a Heavy Helmet (-20 per hit); his line keeps Glimmet in front and lets the opponent's Raticate ex knock it out for the second point. At turn 13 he got 2 points from the Blade; the game then ended 2-2 with the opponent timing out. I cannot say his line was worse, only that km3 sees it as much worse and that the Pichu knock-out was free.
3. **010837, turn 7 (gap 658).** After Rare Candy Kingambit he puts the Energy on Glimmet, km3 on Kingambit. Not a mistake either way: his later turns show he used Glimmet as the piece that gets knocked out to charge the Blade.

All three are in game 010837. Two are about the same pattern, **taking a free point early**: with the opponent's 30-HP Pichu in front, km3 takes the knock-out each time, and he did not.

## Engine and tool notes (for the laptop)

- **Kingambit's Overlord's Blade and the position runner.** The engine counts "own Pokémon knocked out this game" per player (`own_knockouts_this_game`, state/mod.rs); `pg_pos.rs` (sha 790ae7b1b91e18f4, the pinned build's) builds a fresh state and never sets it, so it is 0 in every position. In this set the count should be 2 at 010837 turns 9 and 11 and 3 at turns 13 and 15 (his Glimmora, Regigigas, then Glimmet were knocked out; the opponent's points, 1, 1, 2, 2, are lower because Glimmora's Shattering Crystal flipped heads). Any Kingambit position of the Oct 12 set has the same gap. If kx3 is run on 010837's later turns, the runner needs a `me.knockouts` field (a one-line State patch); otherwise read those turns knowing the Blade is 60.
- **Every card the six games show is in the engine.** The 46 cards seen on the boards: all attack and Ability texts are in the engine's text map, all Trainers have their own code (Arena of Antiquity, Soothing Shore, Protective Poncho, Electrical Cord, Rocky Helmet, Small Balloon, Leaf Cape, Fragrant Forest and Mesagoza included). Whether each is right was not checked card by card.
- **Conditions.** Poison is not represented in 3 turns (010003 turn 7, 015659 turn 13, 020824 turn 5).
- **Stadium use that cannot do anything.** At 020824 turns 9, 11 and 13 km3 adds `UseStadium` for the opponent's Fragrant Forest (a random Grass Basic from the deck) to its plan, with no Grass Basic in his deck. It costs nothing in the harness; it shows that km3 does not check that a use can succeed.
- **Lucky Ice Pop loops.** km3 replays a Pop after each heads, up to seven times in a turn (020824 turn 13); the seeds draw the coins, so it is not a sign of a plan.
- **Scores saturate.** In lost positions km3's best and second-best scores often tie (values near ±10,000 to ±22,000), and the choice is then the first on the list: 8 of the 20 departures from his line are exact ties, e.g. 014423 turn 9 (km3 attacks without the free Energy attach).

## Turns worth a kx3 look (for the cloud pilot; not run)

1. `KW-261013_010837000-t03`: Slash for the point, or the retreat.
2. `KW-261013_010837000-t11`: Overlord's Blade on Pichu, or Hang Down (needs the knock-out count first).
3. `KW-261013_010837000-t09`: the Blade for 140 on Mega Kangaskhan ex now, or healing Glimmet (same).
4. `KW-261013_020824000-t11`: the Ilima line.
5. `KW-261013_014423000-t07` (and 015659 t05): the Energy on the Bench or on the Pokémon that will be knocked out.

## Limits

- The opponent's list is unknown in every game; his hidden cards are filled from the pilot's own list ("approximate", as on Oct 12). The opponent's discard is what the ledger names, plus the count of unreadable ones (none in these six games).
- km3's plan is cut at its first draw card; Mesagoza's coin and Lucky Ice Pop's coins come from the seeds, not from what happened.
- Game 015011 has 3 turns; the opponent never returned, so its turn 3 has no plan of his. Its deck's Alolan Grimer printing is still unsettled between A3 110 and two others (the log list says A3 110 and that is used).
- Reviews were read as written; the Pause Games import files in the batch folder were not read or used.

## Files

`PAUSE_GAMES_2026-10-13_READ_sonnet.md` (this), `POSITION_TABLE.md`, `position_cards.txt`, `positions_all.json`, `decks/`, `position_list.tsv/json` (flags by function), `games_meta.json`, `report_convert.json`, `run_ids.txt`, `report_out.txt`, `km3_TABLES.md`, `km3_summary.json`, `runs_km3/`, `runs_forced/` (`forced_summary.json`), `runs_km3_older_engine/`, `scripts/`.
