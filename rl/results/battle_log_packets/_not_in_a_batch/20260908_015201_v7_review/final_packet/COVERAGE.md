# Battle Recording Coverage

## Setup Interval
- **00:00.000 - 00:05.400**: Loading and match introduction. Matchup: Opponent vs. Dacz8976. An AI badge is visible but is not material to the battle review.
- **00:05.600 - 00:08.200**: Coin flip. Result is black coin / "Going second" for player.
- **00:08.800 - 00:17.000**: Initial setup. Both players draw 5 cards. Player puts Duraludon in Active Spot. Opponent places 1 Active and 2 Benched cards face down.
- **00:19.200 - 00:22.800**: Cards revealed:
  - Opponent Active: Team Rocket's Rattata (HP 40).
  - Opponent Bench: Corphish (HP 60), Team Rocket's Rattata (HP 40).
  - Player Active: Duraludon (HP 100).

## Turn-by-Turn Phases
- **Turn 1 (Opponent)** [00:23.400 - 00:29.200]:
  - Evidence anchors: `00:23.400` (turn banner), `00:27.000` (Chien-Pao ex played to Bench), `00:29.000` (turn end).
  - State delta: Opponent plays Chien-Pao ex onto Bench. No Energy attached. No attack. Score: 0-0.
- **Turn 2 (Player)** [00:29.400 - 01:06.400]:
  - Evidence anchors: `00:29.400` (turn banner), `00:31.200` (draws Dratini), `00:33.800` (Dratini played to Bench), `00:39.400` (plays Professor's Research), `00:41.800` (draws Poké Ball and Axew), `00:46.400` (plays Poké Ball), `00:48.000` (finds Axew), `00:51.400` (Axew played to Bench), `00:56.200` (plays Rainbow Cave Stadium), `01:00.000` (uses Rainbow Cave effect: discards Fighting Energy, then the Stadium causes the next Energy to be generated, which is Metal), `01:04.000` (attaches Metal Energy to Duraludon), `01:06.200` (taps End Turn).
  - State delta: Hand updated; Bench gains Dratini and Axew; Rainbow Cave in play; Duraludon gains 1 Metal Energy. Score: 0-0.
- **Turn 3 (Opponent)** [01:06.600 - 01:08.000]:
  - Evidence anchors: `01:06.600` (Opponent's turn 3 banner), `01:08.000` (video truncates).
  - State delta: Turn 3 begins; video cuts off. Score: 0-0.

## Terminal Sequence
- This file ends at `01:08.000`, so its clip-specific outcome is unknown. Confirmed continuation `20260908_015702000_iOS.MP4` completes the linked battle as a player win, 3-2.

## Reviewed Items
- [x] Setup and starting hands/positions
- [x] Turn 1 full execution
- [x] Turn 2 full execution and card sequencing
- [x] Truncated Turn 3 start

## Unresolved Intervals
- `01:08.000 - end of match`: Recording ends mid-turn during Opponent Turn 3. What is the terminal outcome and final score? (Tracked in U1).

## Required Event Audit
- `Deck searches and failed searches:` 00:46.400 - 00:48.200 (Poké Ball successfully searches deck and puts Basic Pokémon Axew into hand).
- `Energy attachments and acceleration:` 01:00.000 - 01:03.000 (Rainbow Cave discards generated Fighting Energy and causes the next Energy to be generated, which is Metal); 01:03.800 - 01:05.000 (manual attachment: 1 Metal Energy from the Energy Zone to the player's Active Duraludon).
- `Return-to-hand, replay, and exchange events:` none observed.
- `Knockouts and score changes:` none observed (Score remains 0-0).
- `Switches, retreats, and Bench changes:` 00:27.000 (Opponent benches Chien-Pao ex); 00:33.800 (Player benches Dratini); 00:51.400 (Player benches Axew).
- `Terminal sequence in this file:` unknown (U1; video cuts off at 01:08.000). `Linked terminal sequence:` verified in `20260908_015702000_iOS.MP4`, player win 3-2.
