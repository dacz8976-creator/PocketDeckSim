# Coverage Ledger

- **Setup Interval**: 00:00.000 – 00:20.000
- **Turn 1 (Player)**: 00:20.200 – 00:29.200
  - Evidence anchors: `00:20.200` (turn start), `00:24.200` (Professor's Research played), `00:28.400` (turn end)
  - State delta: Player draws 2 cards via Professor's Research; no energy or attack on first turn.
- **Turn 2 (Opponent)**: 00:29.400 – 01:00.400
  - Evidence anchors: `00:29.400` (turn start), `00:33.200` (Poké Ball), `00:36.600` (Magmar benched), `00:38.400` (Poison Barb attached to Magmar), `00:42.200` (Copycat played), `00:48.800` (Poké Ball), `00:52.400` (Koffing benched), `00:53.200` (Happiny benched), `00:54.600` (Darkness Energy attached to Koffing), `00:56.200` (Reverse Thrust attack, 10 damage to Rattata, switches to Happiny)
  - State delta: Opponent benches Magmar, Koffing, Happiny; attacks with Koffing for 10 damage and switches Happiny to Active.
- **Turn 3 (Player)**: 01:00.600 – 01:32.000
  - Evidence anchors: `01:00.600` (turn start), `01:06.400` (Team Rocket's Researcher played, 4 heads), `01:21.600` (second Rattata benched), `01:23.000` (Raticate ex evolved), `01:26.400` (Drowzee benched), `01:27.800` (Raticate ex free retreats, Comfey promoted), `01:30.800` (Psychic Energy attached to Drowzee)
  - State delta: Player searches 4 Team Rocket cards; evolves Active Rattata to Raticate ex; free retreats Raticate ex to bench and promotes Comfey; benches second Rattata and Drowzee; attaches 1 Psychic energy to Drowzee.
- **Turn 4 (Opponent)**: 01:32.200 – 02:08.200
  - Evidence anchors: `01:32.200` (turn start), `01:34.800` (Fire Energy to Magmar), `01:35.800` (Copycat played), `01:43.200` (Weezing ex evolved on bench, Boiler Smog poisons/burns Comfey), `01:51.200` (Happiny free retreats, Magmar promoted), `01:52.800` (Poison Barb to Happiny), `01:57.600` (Derisive Roasting attack, 110 damage), `02:01.000` (Comfey KO'd), `02:04.000` (Opponent +1 point, score 1-0), `02:07.400` (Drowzee promoted)
  - State delta: Comfey knocked out; opponent scores 1 point; player promotes Drowzee.
- **Turn 5 (Player)**: 02:08.400 – 02:50.400
  - Evidence anchors: `02:08.400` (turn start), `02:14.600` (Hypno evolved), `02:17.600` (Sightseer played, gets Raticate ex), `02:24.800` (Raticate ex evolved on bench, Thieving Incisors steals Fire Energy from Magmar), `02:33.000` (Elegant Cape attached to Hypno, HP 90->120), `02:38.000` (Psychic Energy attached to Hypno), `02:39.600` (Entrap attack, pulls Weezing ex, deals 50 damage)
  - State delta: Hypno evolves, gains Cape and second Psychic energy; bench Raticate ex steals active Magmar's Fire energy; Hypno attacks Weezing ex for 50 damage and traps it active.
- **Turn 6 (Opponent)**: 02:50.600 – 03:32.600
  - Evidence anchors: `02:50.600` (turn start), `02:54.200` (Professor's Research played), `02:58.000` (second Weezing ex evolved on bench, Boiler Smog poisons/burns Hypno), `03:06.800` (X Speed played), `03:10.400` (Weezing ex retreats paying 1 Darkness, Magmar promoted), `03:12.400` (Darkness Energy attached to Magmar), `03:14.000` (Derisive Roasting attack, 110 damage to Hypno), `03:18.000` (Hypno KO'd by Poison in Checkup), `03:26.000` (Opponent +1 point, score 2-0), `03:31.000` (Raticate ex promoted)
  - State delta: Active Hypno survives attack with 10 HP, knocked out during Checkup by Poison; opponent scores 1 point (2-0); player promotes Raticate ex.
- **Turn 7 (Player)**: 03:32.800 – 03:53.400
  - Evidence anchors: `03:32.800` (turn start), `03:34.600` (Poké Ball played, fails/no basic), `03:36.400` (Psychic Energy attached to Raticate ex), `03:39.800` (Boost Dash attack, 70 damage), `03:42.200` (Magmar KO'd), `03:44.800` (Poison Barb poisons Raticate ex), `03:49.400` (Player +1 point, score 2-1), `03:51.400` (Happiny promoted)
  - State delta: Opponent's Active Magmar knocked out; player scores 1 point; Raticate ex takes Poison from Poison Barb; Happiny promoted.
- **Turn 8 (Opponent)**: 03:53.600 – 04:18.800
  - Evidence anchors: `03:53.600` (turn start), `03:56.400` (second Magmar benched), `03:58.400` (Team Rocket's Master Plan played, Confuses Raticate ex and Happiny), `04:06.600` (Happiny free retreats, second Magmar promoted), `04:08.800` (Darkness Energy attached to Magmar), `04:10.400` (Derisive Roasting attack, 110 damage), `04:12.600` (Raticate ex KO'd), `04:17.000` (Opponent +2 points, score 2-1 -> 3-1), `04:18.800` (Defeat screen)
  - State delta: Raticate ex knocked out; opponent awarded 2 points reaching winning condition; battle concludes.
- **Terminal Sequence**: 04:16.000 – 04:18.978
  - Score reaches opponent win threshold; Defeat banner displayed.

## Required Event Audit
- `Deck searches and failed searches:` 00:33.200 (Poké Ball -> Magmar), 00:48.800 (Poké Ball -> Koffing), 01:06.400 (Team Rocket's Researcher -> 4 Rocket cards), 02:17.600 (Sightseer -> Raticate ex), 03:34.600 (Poké Ball -> failed, no basic).
- `Energy attachments and acceleration:` 00:54.600 (Darkness to opp Koffing), 01:30.800 (Psychic to player Drowzee), 01:34.800 (Fire to opp Magmar), 02:28.600 (Thieving Incisors steals Fire from Magmar to Raticate ex), 02:38.000 (Psychic to player Hypno), 03:10.400 (1 Darkness paid to retreat Weezing ex), 03:12.400 (Darkness to opp Magmar), 03:23.400 (Hypno KO discards 2 Psychic), 03:36.400 (Psychic to player Raticate ex), 03:46.400 (Magmar KO discards 1 Darkness), 04:08.800 (Darkness to opp second Magmar), 04:13.400 (Raticate ex KO discards 1 Fire and 1 Psychic).
- `Return-to-hand, replay, and exchange events:` 00:42.200 (Copycat shuffles hand into deck, draws 4), 01:35.800 (Copycat shuffles hand into deck, draws 5).
- `Knockouts and score changes:` 02:01.000 (Comfey KO, opp 1 point, 02:04.000), 03:18.000 (Hypno KO by poison, opp 1 point, 03:26.000), 03:42.200 (Magmar KO, player 1 point, 03:49.400), 04:12.600 (Raticate ex KO, opp 2 points, 04:17.000).
- `Switches, retreats, and Bench changes:` 00:56.200 (Koffing Reverse Thrust switches Happiny in), 01:27.800 (Raticate ex free retreats, Comfey promoted), 01:51.200 (Happiny free retreats, Magmar promoted), 02:44.600 (Hypno Entrap forces Weezing ex in), 03:10.400 (Weezing ex retreats, Magmar promoted), 03:31.000 (Raticate ex promoted after Hypno KO), 03:51.400 (Happiny promoted after Magmar KO), 04:06.600 (Happiny free retreats, second Magmar promoted).
- `Terminal sequence:` 04:17.000 (+2 points awarded to opponent, reaching match limit), 04:18.800 ('Defeat' banner displayed).
