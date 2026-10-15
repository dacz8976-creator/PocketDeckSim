# Battle Coverage

## Setup Interval
- **00:00.000 - 00:14.000**: Match intro against AI "Opponent". Coin flip determines player goes first. Player places Gible (player-1) into the Active Spot. Opponent places Deino (opp-1) into the Active Spot.

## Turn Timeline
- **Turn 1 (Player)** [00:14.000 - 00:25.400]
  - *Evidence anchors*: 00:14.200 (Turn 1 start), 00:18.400 (Poké Ball played), 00:20.400 (Munchlax drawn), 00:24.400 (Munchlax benched), 00:25.400 (Turn end).
  - *State delta*: Munchlax placed on Bench. No Energy attached (going first rule).
- **Turn 2 (Opponent)** [00:25.400 - 00:37.000]
  - *Evidence anchors*: 00:25.600 (Turn 2 start), 00:29.400 (Rocky Helmet attached to Deino), 00:32.600 (Darkness Energy attached to Deino), 00:33.800 (Headbutt declared), 00:36.000 (Gible takes 20 damage, HP 40/60).
  - *State delta*: Deino attached Rocky Helmet and 1 Darkness Energy; dealt 20 damage to Gible.
- **Turn 3 (Player)** [00:37.000 - 00:57.200]
  - *Evidence anchors*: 00:37.000 (Turn 3 start), 00:42.600 (Fighting Energy attached to Gible), 00:45.400 (Gible switched/retreated, Munchlax promoted), 00:47.400 (Gible evolved to Gabite on Bench), 00:48.400 (Munchlax uses Hungrily Draw), 00:49.800 (Deino takes 10 damage, HP 50/60; Munchlax takes 20 damage from Rocky Helmet, HP 30/50).
  - *State delta*: Gible retreated/switched, Gabite evolved on Bench, Munchlax attacks Deino for 10, Munchlax takes 20 recoil from Rocky Helmet.
- **Turn 4 (Opponent)** [00:57.200 - 01:38.200]
  - *Evidence anchors*: 00:57.400 (Turn 4 start), 01:01.000 (Rare Candy played), 01:03.000 (Deino evolves directly into Hydreigon), 01:05.400 (Copycat played), 01:11.400 (Bombirdier benched), 01:13.400 (Hydreigon uses Roar in Unison), 01:17.600 (Hydreigon takes 30 damage from ability, HP 110/140), 01:19.400 (Poké Ball played), 01:23.600 (Mega Sableye ex benched), 01:28.000 (Hyper Ray declared), 01:30.000 (Munchlax takes 130 damage, knocked out), 01:34.000 (Opponent awarded 1st point).
  - *State delta*: Deino evolves to Hydreigon via Rare Candy; Bombirdier and Mega Sableye ex benched; Munchlax KO'd; Opponent score: 1.
- **Turn 5 (Player)** [01:38.200 - 02:02.000]
  - *Evidence anchors*: 01:38.400 (Gabite promoted, Turn 5 start), 01:46.400 (Lucky Ice Pop played, heals 20, coin flip Heads), 01:53.600 (Gabite evolves into Garchomp), 01:56.200 (Mesagoza Stadium played), 02:01.000 (Mesagoza coin flip Tails).
  - *State delta*: Gabite healed to 80/80, evolves to Garchomp (150 HP), Mesagoza enters play, turn passed without attack.
- **Turn 6 (Opponent)** [02:02.000 - 02:15.800]
  - *Evidence anchors*: 02:02.200 (Turn 6 start), 02:05.200 (Hydreigon uses Roar in Unison, takes 30 damage, HP 80/140), 02:12.000 (Hyper Ray attack), 02:14.400 (Garchomp takes 130 damage, HP 20/150).
  - *State delta*: Hydreigon damages itself to 80 HP, hits Garchomp for 130 damage.
- **Turn 7 (Player)** [02:15.800 - 02:58.200]
  - *Evidence anchors*: 02:16.000 (Turn 7 start), 02:28.600 (Gible benched), 02:30.000 (Fighting Energy to benched Gible), 02:32.000 (Rainbow Cave replaces Mesagoza), 02:36.400 (Lucky Ice Pop played, heals Garchomp 20, coin flip Heads), 02:44.200 (Lucky Ice Pop played again, heals Garchomp 20, coin flip Heads), 02:52.000 (Lucky Ice Pop played 3rd time, heals Garchomp 20 to 80 HP, coin flip Tails).
  - *State delta*: Second Gible benched with 1 Energy; Garchomp healed from 20 to 80 HP; Stadium replaced with Rainbow Cave.
- **Turn 8 (Opponent)** [02:58.200 - 03:22.400]
  - *Evidence anchors*: 02:58.400 (Turn 8 start), 03:02.000 (Professor's Research played), 03:05.000 (Roar in Unison used, Hydreigon takes 30 damage, HP 50/140), 03:12.000 (Hyper Ray attack), 03:13.800 (Garchomp knocked out), 03:18.000 (Opponent awarded 2nd point).
  - *State delta*: Hydreigon damages itself to 50 HP; Garchomp KO'd; Opponent score: 2.
- **Turn 9 (Player)** [03:22.400 - 03:48.200]
  - *Evidence anchors*: 03:22.400 (Gible promoted, Turn 9 start), 03:25.400 (Celebi benched), 03:28.400 (Gible evolves into Gabite), 03:29.600 (Water Energy attached to Gabite), 03:32.000 (Linear Attack declared against Hydreigon), 03:34.200 (Hydreigon takes 50 damage, HP 0/140, KO'd), 03:36.600 (Rocky Helmet deals 20 recoil to Gabite, HP 60/80), 03:41.400 (Player awarded 1st point).
  - *State delta*: Celebi benched; Gabite attacks and KOs Hydreigon; Gabite takes 20 recoil; Player score: 1.
- **Turn 10 (Opponent)** [03:48.200 - 04:02.800]
  - *Evidence anchors*: 03:46.000 (Mega Sableye ex promoted), 03:48.400 (Turn 10 start), 03:51.400 (Darkness Energy attached to Mega Sableye ex), 03:53.000 (Cursed Jewel declared), 03:55.600 (Gabite takes 80 damage, knocked out), 04:00.400 (Opponent awarded 3rd point).
  - *State delta*: Gabite knocked out by Mega Sableye ex; Opponent score: 3.

## Terminal Sequence
- **04:00.400 - 04:09.600**: Opponent reaches 3 points, triggering match end. Defeat banner displayed at 04:03.000, followed by defeat screen at 04:08.200.

## Required Event Audit
- `Deck searches and failed searches:` Turn 1 Poké Ball at 00:18.400 (draws Munchlax); Turn 4 Poké Ball at 01:19.400 (opponent draws Mega Sableye ex); Turn 5 Mesagoza at 01:58.800 (coin flip Tails, no search).
- `Energy attachments and acceleration:` Turn 2 manual Darkness to Deino (00:32.600); Turn 3 manual Fighting to Gible (00:42.600); Turn 4 manual Darkness to Hydreigon (01:00.600) & Roar in Unison +2 Darkness (01:13.600); Turn 6 Roar in Unison (02:05.200); Turn 7 manual Fighting to benched Gible (02:30.000); Turn 8 manual Darkness to Hydreigon (03:01.000) & Roar in Unison (03:05.000); Turn 9 manual Water to Gabite (03:29.600); Turn 10 manual Darkness to Mega Sableye ex (03:51.400).
- `Return-to-hand, replay, and exchange events:` Turn 4 Copycat shuffles opponent hand and redraws (01:05.400); Turn 5 Lucky Ice Pop returned to hand on Heads (01:50.000); Turn 7 Lucky Ice Pop replayed and returned on Heads twice (02:41.600, 02:49.400), then discarded on Tails (02:57.000).
- `Knockouts and score changes:` Turn 4 Munchlax KO'd (01:30.000), opponent score 0 -> 1 (01:34.000); Turn 8 Garchomp KO'd (03:13.800), opponent score 1 -> 2 (03:18.000); Turn 9 Hydreigon KO'd (03:34.200), player score 0 -> 1 (03:41.400); Turn 10 Gabite KO'd (03:55.600), opponent score 2 -> 3 (04:00.400).
- `Switches, retreats, and Bench changes:` Turn 3 Gible retreats/switches, Munchlax promoted (00:45.400); Turn 5 Gabite promoted after Munchlax KO (01:38.400); Turn 9 Gible promoted after Garchomp KO (03:22.400); Turn 10 Mega Sableye ex promoted after Hydreigon KO (03:46.000).
- `Terminal sequence:` Opponent scores 3rd point at 04:00.400, "Defeat" banner displayed at 04:03.000.
