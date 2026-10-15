### SOURCE.json
```json
{
  "filename": "20260921_152812000_iOS.MP4",
  "source_path": "/home/dacz8976/20260921_152812000_iOS.MP4",
  "sha256": "5FEF7F20302FADC695346ED277CEF892E523CCC73DFF67F2907F4448EE10CDB0",
  "bytes": 568299605,
  "duration_seconds": 304.803,
  "review_status": "partial",
  "reviewer_attribution": "Gemini 3.8 Flash API first-pass draft",
  "recording_type": "gameplay",
  "relationships": [],
  "outcome": "win",
  "index_update_performed": false,
  "media_move_performed": false
}
```

### COVERAGE.md
```markdown
# Coverage Ledger

- Matchmaking & Setup: 00:00.000 - 00:20.199
  - Evidence anchors: Player identity `Dacz8976` and opponent `AI Opponent` established at 00:03.200; coin flip "Going second" at 00:06.400; opening hand drawn and Type: Null placed in Active Spot at 00:11.400; opponent flips Active Oricorio at 00:16.200.
  - State delta: Player Active Type: Null (80 HP, 0 Energy); Opponent Active Oricorio (70 HP, 0 Energy). Score: 0-0.

- Turn 1 (Opponent): 00:20.200 - 00:27.199
  - Evidence anchors: "Current turn: 1" at 00:20.200; Professor's Research played at 00:23.200; Dratini benched at 00:26.000.
  - State delta: Opponent benches Dratini (70 HP); hand adjusted; no Energy attached; no attack.

- Turn 2 (Player): 00:27.200 - 00:52.799
  - Evidence anchors: "Current turn: 2" at 00:27.200; Water Energy generated at 00:30.800; Professor's Research played at 00:29.000 / resolved at 00:33.400 drawing Soothing Shore and Hiking Trail; Elegant Cape attached to Type: Null at 00:38.800; Soothing Shore played at 00:44.600; Water Energy attached to Type: Null at 00:47.800.
  - State delta: Type: Null has Elegant Cape and 1 Water Energy; Stadium in play: Soothing Shore. Turn passed without attack.

- Turn 3 (Opponent): 00:52.800 - 01:09.399
  - Evidence anchors: "Current turn: 3" at 00:52.800; Lightning Energy attached to Benched Dratini at 00:55.600; Rare Candy played at 00:56.400 evolving Dratini to Dragonite (160 HP); Copycat played at 01:02.000; Water Energy attached to Dragonite at 01:08.400.
  - State delta: Opponent Benched Dragonite has 1 Lightning Energy, 1 Water Energy; no attack.

- Turn 4 (Player): 01:09.400 - 01:58.999
  - Evidence anchors: "Current turn: 4" at 01:09.400; Water Energy generated; Type: Null evolved to Silvally (Brave Buddies, shiny) at 01:17.000, triggering Elegant Cape HP boost to 140 HP at 01:20.800; Hiking Trail played replacing Soothing Shore at 01:22.600; Copycat played at 01:28.800 drawing 4 cards; shiny Type: Null benched at 01:40.400; Water Energy attached to Active Silvally at 01:43.600 (now 2 Energy); Brave Buddies attack declared at 01:47.000 dealing 100 damage (50 base + 50 Supporter boost) to Oricorio; Oricorio Knocked Out at 01:49.600; Opponent promotes Dragonite at 01:56.400.
  - State delta: Opponent Oricorio Knocked Out; Player score 1-0; Opponent Active Dragonite (160 HP, 1 Water, 1 Lightning); Player Active Silvally (140 HP, 2 Water Energy, Elegant Cape), Bench Type: Null (80 HP).

- Turn 5 (Opponent): 01:59.000 - 02:07.399
  - Evidence anchors: "Current turn: 5" at 01:59.000; Water Energy attached to Active Dragonite at 02:02.000; Professor's Research played at 02:03.400; Dratini benched at 02:06.400; turn ended without attack.
  - State delta: Opponent Active Dragonite has 2 Water Energy, 1 Lightning Energy (3 total); Opponent benches Dratini (70 HP).

- Turn 6 (Player): 02:07.400 - 03:02.399
  - Evidence anchors: "Current turn: 6" at 02:07.400; Water Energy generated; Professor's Research played at 02:12.400; Poké Ball played at 02:19.200 (failed search at 02:21.600); Elegant Cape attached to Benched Type: Null at 02:23.200; Water Energy attached to Benched Type: Null at 02:54.800; Brave Buddies attack declared at 02:57.800 dealing 100 damage to Dragonite (160 -> 60 HP); turn ended.
  - State delta: Opponent Active Dragonite HP 60/160; Player Benched Type: Null has Elegant Cape and 1 Water Energy.

- Turn 7 (Opponent): 03:02.400 - 03:19.799
  - Evidence anchors: Water Energy attached to Active Dragonite at 03:04.600; Irida played at 03:05.400 healing 40 damage from Dragonite (HP 60 -> 100/160); Rare Candy played at 03:09.600 evolving Benched Dratini to Dragonite (160 HP); Poké Ball played at 03:16.400; turn ended without attack.
  - State delta: Opponent Active Dragonite HP 100/160 (3 Water, 1 Lightning Energy); Opponent Benched Dragonite (160 HP, 0 Energy).

- Turn 8 (Player): 03:19.800 - 04:17.599
  - Evidence anchors: "Current turn: 8" at 03:19.800; Water Energy generated; Silvally (Gold Breaker) drawn; Benched Type: Null evolved into Silvally (Gold Breaker) at 03:27.200 (HP 140 via Cape); Team Rocket's Thieving Machine played at 03:32.400 retrieving Poké Ball from opponent discard; Poké Ball played at 03:37.800 (failed search at 03:40.200); Copycat played at 03:43.600; second Poké Ball played at 03:52.800 (failed search at 03:55.200); Water Energy attached to Benched Silvally (Gold Breaker) at 03:57.600; Brave Buddies attack declared at 04:02.200 dealing 100 damage to Active Dragonite; Active Dragonite Knocked Out at 04:04.800; Opponent promotes Benched Dragonite at 04:06.400; Player score reaches 2-0 at 04:08.400.
  - State delta: Opponent first Dragonite Knocked Out; Player score 2-0; Opponent promotes second Dragonite (160 HP, 0 Energy); Player Active Silvally (140 HP, 2 Water Energy, Cape), Bench Silvally (140 HP, 2 Water Energy, Cape).

- Turn 9 (Opponent): 04:17.600 - 04:21.799
  - Evidence anchors: "Current turn: 9" at 04:17.600; Water Energy attached to Active Dragonite at 04:20.800; turn ended without attack.
  - State delta: Opponent Active Dragonite has 1 Water Energy.

- Turn 10 (Player): 04:21.800 - 04:39.199
  - Evidence anchors: "Current turn: 10" at 04:21.800; Water Energy generated; Gladion played at 04:27.400 (failed search at 04:29.600); Water Energy attached to Benched Silvally (Gold Breaker) at 04:32.400 (now 3 Water Energy); Brave Buddies attack declared at 04:35.200 dealing 100 damage to Dragonite (160 -> 60 HP); turn ended.
  - State delta: Opponent Active Dragonite HP 60/160; Player Benched Silvally (Gold Breaker) has 3 Water Energy.

- Turn 11 (Opponent): 04:39.200 - 04:43.199
  - Evidence anchors: "Current turn: 11" at 04:39.200; Lightning Energy attached to Active Dragonite at 04:41.800; turn ended without attack.
  - State delta: Opponent Active Dragonite has 1 Water Energy, 1 Lightning Energy.

- Turn 12 (Player): 04:43.200 - 05:04.803
  - Evidence anchors: "Current turn: 12" at 04:43.200; Water Energy generated in Energy Zone; Active Silvally retreats at 04:52.800 discarding 1 Water Energy (1 remaining); Benched Silvally (Gold Breaker, 3 Water Energy) promoted to Active Spot at 04:53.600; Gold Breaker attack declared at 04:56.400 dealing 60 damage to Dragonite; Dragonite Knocked Out at 04:58.800; opponent board cleared; Player awarded 3rd point at 05:02.400; final score 3-0.
  - State delta: Opponent field wiped; Player score 3-0; victory achieved.

- Terminal sequence: 05:02.400 - 05:04.803
  - Evidence anchors: Point banner "+1 point! 3" animates at 05:02.400; match ends on victory banner at 05:04.803.

- Reviewed coverage items:
  - [x] Matchmaking and control mode (Solo vs AI, manual mode)
  - [x] Coin flip and turn order decision
  - [x] Setup and active placement
  - [x] Turns 1 through 12 complete timeline
  - [x] Knockouts, promotions, point awards, and win condition

- Unresolved intervals: None.

## Required Event Audit
- Deck searches and failed searches:
  - 00:23.200: Opponent plays Professor's Research (draws 2 cards).
  - 00:29.000: Player plays Professor's Research (draws 2 cards).
  - 01:02.000: Opponent plays Copycat (shuffles and draws).
  - 01:28.800: Player plays Copycat (shuffles and draws 4 cards).
  - 02:03.400: Opponent plays Professor's Research (draws 2 cards).
  - 02:12.400: Player plays Professor's Research (draws 2 cards).
  - 02:19.200: Player plays Poké Ball (failed search prompt confirmed at 02:21.600).
  - 03:16.400: Opponent plays Poké Ball.
  - 03:37.800: Player plays Poké Ball (failed search prompt confirmed at 03:40.200).
  - 03:43.600: Player plays Copycat (shuffles and draws cards).
  - 03:52.800: Player plays Poké Ball (failed search prompt confirmed at 03:55.200).
  - 04:27.400: Player plays Gladion (failed search prompt confirmed at 04:29.600).
- Energy attachments and acceleration:
  - Turn 2 (00:47.800): Player attaches generated Water Energy to Active Type: Null.
  - Turn 3 (00:55.600): Opponent attaches Lightning Energy to Benched Dratini.
  - Turn 3 (01:08.400): Opponent attaches Water Energy to Benched Dragonite.
  - Turn 4 (01:43.600): Player attaches generated Water Energy to Active Silvally.
  - Turn 5 (02:02.000): Opponent attaches Water Energy to Active Dragonite.
  - Turn 6 (02:54.800): Player attaches generated Water Energy to Benched Type: Null.
  - Turn 7 (03:04.600): Opponent attaches Water Energy to Active Dragonite.
  - Turn 8 (03:57.600): Player attaches generated Water Energy to Benched Silvally (Gold Breaker).
  - Turn 9 (04:20.800): Opponent attaches Water Energy to Active Dragonite.
  - Turn 10 (04:32.400): Player attaches generated Water Energy to Benched Silvally (Gold Breaker).
  - Turn 11 (04:41.800): Opponent attaches Lightning Energy to Active Dragonite.
  - Turn 12 (04:52.800): Player retreats Active Silvally, discarding 1 Water Energy; Turn 12 generated Water Energy left in Energy Zone.
- Return-to-hand, replay, and exchange events:
  - Turn 4 (01:28.800): Player plays Copycat, returning hand to deck.
  - Turn 8 (03:32.400): Player plays Team Rocket's Thieving Machine, retrieving Poké Ball from opponent's discard pile into player's hand.
  - Turn 8 (03:43.600): Player plays Copycat, returning hand to deck.
- Knockouts and score changes:
  - Turn 4 (01:48.600 - 01:53.200): Oricorio (70 HP) knocked out by Brave Buddies (100 damage). Player awarded 1 point (Score 1-0).
  - Turn 8 (04:03.800 - 04:08.400): Active Dragonite (100 HP remaining) knocked out by Brave Buddies (100 damage). Player awarded 1 point (Score 2-0).
  - Turn 12 (04:57.600 - 05:02.400): Active Dragonite (60 HP remaining) knocked out by Gold Breaker (60 damage). Opponent board cleared. Player awarded 1 point (Score 3-0).
- Switches, retreats, and Bench changes:
  - Setup (00:11.400): Player places Type: Null into Active Spot; Opponent places Oricorio.
  - Turn 1 (00:26.000): Opponent benches Dratini.
  - Turn 3 (00:58.800): Opponent evolves Benched Dratini to Dragonite via Rare Candy.
  - Turn 4 (01:17.000): Player evolves Active Type: Null to Silvally.
  - Turn 4 (01:40.400): Player benches Type: Null (shiny).
  - Turn 4 (01:56.400): Opponent promotes Benched Dragonite to Active Spot following Oricorio KO.
  - Turn 5 (02:06.400): Opponent benches Dratini.
  - Turn 7 (03:12.000): Opponent evolves Benched Dratini to Dragonite via Rare Candy.
  - Turn 8 (03:27.200): Player evolves Benched Type: Null to Silvally (Gold Breaker).
  - Turn 8 (04:06.400): Opponent promotes Benched Dragonite to Active Spot following first Dragonite KO.
  - Turn 12 (04:52.800 - 04:53.600): Player retreats Active Silvally (paying 1 Water Energy) and promotes Benched Silvally (Gold Breaker) to Active Spot.
- Terminal sequence:
  - Turn 12 (04:58.800 - 05:04.803): Final knockout of opponent's Dragonite with empty bench triggers 3rd point award and immediate victory sequence.
```

### REVIEW.md
```markdown
# Match Review: Solo Battle vs AI Opponent

- Date: 2026-09-21 (inferred from recording filename `20260921_152812000_iOS.MP4`).
- Mode: Solo Battle (AI Opponent).
- Auto State: Off (manual control throughout match).
- Player: Dacz8976.
- Opponent: AI Opponent.

## Starting Board and Opening Hand

- Player Initial Hand:
  - Copycat
  - Silvally (Brave Buddies, shiny)
  - Silvally (Gold Breaker)
  - Type: Null (Basic, 80 HP)
  - Elegant Cape (Pokémon Tool)
- Active Setup:
  - Player places Type: Null (80 HP, Colorless) in the Active Spot.
  - Opponent reveals Active Oricorio (70 HP, Lightning).

---

## Evidence Ledger

### Turn 1 (Opponent)
- Observed actions:
  - Opponent turn indicator: "Current turn: 1" (00:20.200).
  - Opponent plays Supporter `Professor's Research` (00:23.200), drawing 2 cards.
  - Opponent plays Basic Pokémon `Dratini` (70 HP) to the Bench (00:26.000).
  - Opponent passes without attaching Energy or attacking.
- State delta: Opponent bench: Dratini (70 HP, 0 Energy).
- Evidence anchors: 00:20.200 (turn start), 00:23.200 (Supporter), 00:26.000 (Bench play), 00:27.000 (turn end).

### Turn 2 (Player)
- Observed actions:
  - Player turn indicator: "Current turn: 2" (00:27.200).
  - Energy Zone generates Water Energy (00:30.800).
  - Player plays Supporter `Professor's Research` (00:29.000 - 00:33.400), drawing `Soothing Shore` (Stadium) and `Hiking Trail` (Stadium).
  - Player attaches Pokémon Tool `Elegant Cape` to Active Type: Null (00:38.800 - 00:41.400). Note: Tool specifies Stage 1 Pokémon; Type: Null remains at 80/80 HP.
  - Player plays Stadium card `Soothing Shore` (00:44.600 - 00:46.400).
  - Player attaches Water Energy from Energy Zone to Active Type: Null (00:47.800).
  - Player inspects Silvally cards in hand; ends turn without attacking (00:52.400).
- State delta: Player Active Type: Null has Elegant Cape and 1 Water Energy; Stadium is Soothing Shore.
- Evidence anchors: 00:27.200 (turn start), 00:33.400 (Research draw), 00:41.400 (Tool attach), 00:46.400 (Stadium), 00:48.000 (Energy attach), 00:52.400 (turn end).

### Turn 3 (Opponent)
- Observed actions:
  - Opponent turn indicator: "Current turn: 3" (00:52.800).
  - Opponent attaches Lightning Energy to Benched Dratini (00:55.600).
  - Opponent plays Item `Rare Candy` (00:56.400 - 00:57.200), evolving Benched Dratini directly into Stage 2 `Dragonite` (160 HP) (00:58.800 - 01:00.400).
  - Opponent plays Supporter `Copycat` (01:02.000 - 01:04.600), shuffling hand and drawing cards.
  - Opponent attaches Water Energy to Benched Dragonite (01:08.400). Dragonite now has 1 Lightning, 1 Water Energy.
  - Opponent ends turn without attacking.
- State delta: Opponent Benched Dragonite (160 HP, 1 Water, 1 Lightning Energy).
- Evidence anchors: 00:52.800 (turn start), 00:55.600 (Lightning attach), 00:58.800 (Rare Candy evolution), 01:02.000 (Copycat), 01:08.400 (Water attach), 01:09.200 (turn end).

### Turn 4 (Player)
- Observed actions:
  - Player turn indicator: "Current turn: 4" (01:09.400).
  - Water Energy generated in Energy Zone.
  - Player draws Item `Team Rocket's Thieving Machine` (01:11.400).
  - Player checks opponent's discard pile (01:13.400 - 01:14.200).
  - Player evolves Active Type: Null into `Silvally` (Brave Buddies, shiny) (01:17.000 - 01:20.600).
  - `Elegant Cape` activates on Stage 1 evolution: Max HP increases from 110 to 140 (01:20.800).
  - Player plays Stadium `Hiking Trail` (01:22.600 - 01:25.200), discarding Soothing Shore.
  - Player plays Supporter `Copycat` (01:28.800 - 01:31.200), shuffling hand and drawing 4 cards: `Professor's Research`, `Lucky Ice Pop`, `Team Rocket's Thieving Machine`, and `Type: Null` (shiny).
  - Player benches `Type: Null` (shiny, 80 HP) (01:40.400).
  - Player attaches Water Energy from Energy Zone to Active Silvally (01:43.600), bringing attached Energy to 2.
  - Player declares attack `Brave Buddies` (01:47.000). Attack deals 50 base + 50 bonus damage due to playing Supporter Copycat this turn = 100 damage.
  - 100 damage dealt to Oricorio (70 HP) (01:48.600). Oricorio is Knocked Out (01:49.600).
  - Opponent promotes Dragonite (160 HP) to Active Spot (01:56.400 - 01:58.400).
  - Player awarded 1st point (Score 1-0) (01:53.200).
  - Hiking Trail effect checks: player already has 3 cards in hand, draws 0.
- State delta: Opponent Oricorio KO'd; Player score: 1-0; Opponent Active: Dragonite (160 HP, 1 Water, 1 Lightning Energy); Player Active: Silvally (140 HP, 2 Water Energy, Elegant Cape), Bench: Type: Null (80 HP).
- Evidence anchors: 01:09.400 (turn start), 01:20.800 (evolution & Cape activation), 01:25.200 (Hiking Trail), 01:31.200 (Copycat draw), 01:40.400 (Type: Null benched), 01:43.600 (Energy attach), 01:48.600 (attack & KO), 01:53.200 (point award), 01:58.400 (Dragonite promoted).

### Turn 5 (Opponent)
- Observed actions:
  - Opponent turn indicator: "Current turn: 5" (01:59.000).
  - Water Energy generated and attached to Active Dragonite (02:02.000), bringing Dragonite to 3 Energy (2 Water, 1 Lightning).
  - Opponent plays Supporter `Professor's Research` (02:03.400), drawing 2 cards.
  - Opponent benches `Dratini` (70 HP) (02:06.400).
  - Dragonite Draco Meteor requires 4 Energy; opponent passes turn without attacking.
- State delta: Opponent Active Dragonite has 3 Energy; Opponent Benched Dratini (70 HP).
- Evidence anchors: 01:59.000 (turn start), 02:02.000 (Energy attach), 02:03.400 (Research), 02:06.400 (Dratini benched), 02:07.200 (turn end).

### Turn 6 (Player)
- Observed actions:
  - Player turn indicator: "Current turn: 6" (02:07.400).
  - Water Energy generated in Energy Zone.
  - Player draws `Elegant Cape` (02:09.200).
  - Player plays Supporter `Professor's Research` (02:12.400 - 02:13.600), drawing `Copycat` and `Poké Ball`.
  - Player plays Item `Poké Ball` (02:19.200 - 02:21.000). Deck search fails: "There are no cards in the deck that can be the target of the effect" (02:21.600).
  - Player attaches `Elegant Cape` to Benched Type: Null (02:23.200 - 02:25.400).
  - Player checks opponent's discard pile (02:26.200 - 02:50.000).
  - Player attaches Water Energy from Energy Zone to Benched Type: Null (02:54.800).
  - Player declares attack `Brave Buddies` with Active Silvally (02:57.800). Damage: 50 + 50 (Supporter played this turn) = 100 damage.
  - 100 damage dealt to Active Dragonite (160 HP -> 60 HP remaining) (02:59.400).
  - Turn ends; Hiking Trail checks hand (3 cards, draws 0).
- State delta: Opponent Active Dragonite HP reduced to 60/160; Player Benched Type: Null has Elegant Cape and 1 Water Energy.
- Evidence anchors: 02:07.400 (turn start), 02:13.600 (Research), 02:21.600 (Poké Ball failed search), 02:25.400 (Cape attached), 02:54.800 (Energy attached), 02:59.400 (attack damage), 03:02.000 (turn end).

### Turn 7 (Opponent)
- Observed actions:
  - Opponent turn starts (03:02.400).
  - Water Energy attached to Active Dragonite (03:04.600), bringing it to 4 Energy (3 Water, 1 Lightning).
  - Opponent plays Supporter `Irida` (03:05.400 - 03:06.200), healing 40 damage from each Pokémon with Water Energy attached. Dragonite heals 40 HP (HP 60 -> 100/160) (03:07.600).
  - Opponent plays Item `Rare Candy` (03:09.600 - 03:10.600), evolving Benched Dratini into second `Dragonite` (160 HP) (03:12.000 - 03:13.200).
  - Opponent plays Item `Poké Ball` (03:16.400).
  - Opponent passes without attacking despite Dragonite having 4 Energy.
- State delta: Opponent Active Dragonite HP 100/160 (4 Energy); Opponent Benched Dragonite (160 HP, 0 Energy).
- Evidence anchors: 03:02.400 (turn start), 03:04.600 (Energy attach), 03:07.600 (Irida heal), 03:13.200 (Rare Candy evolution), 03:16.400 (Poké Ball), 03:19.400 (turn end).

### Turn 8 (Player)
- Observed actions:
  - Player turn indicator: "Current turn: 8" (03:19.800).
  - Water Energy generated in Energy Zone.
  - Player draws `Silvally` (Gold Breaker) (03:21.600).
  - Player evolves Benched Type: Null into `Silvally` (Gold Breaker) (03:27.200 - 03:29.400). Elegant Cape increases max HP to 140.
  - Player plays Item `Team Rocket's Thieving Machine` (03:32.400 - 03:34.600), randomly taking `Poké Ball` from opponent's discard pile into hand (03:35.800).
  - Player plays Item `Poké Ball` (03:37.800 - 03:39.400). Prompt: "There are no cards in the deck that can be the target of the effect" (03:40.200).
  - Player plays Supporter `Copycat` (03:43.600 - 03:45.200), shuffling hand and drawing cards.
  - Player plays Item `Poké Ball` from new hand (03:52.800 - 03:54.400). Prompt: "There are no cards in the deck that can be the target of the effect" (03:55.200).
  - Player attaches Water Energy from Energy Zone to Benched Silvally (Gold Breaker) (03:57.600), bringing it to 2 Water Energy.
  - Player declares attack `Brave Buddies` with Active Silvally (04:02.200). Damage: 50 + 50 (Supporter Copycat played) = 100 damage.
  - 100 damage dealt to Active Dragonite (100 -> 0 HP) (04:03.800). Dragonite is Knocked Out (04:04.800).
  - Opponent promotes second Dragonite (160 HP) to Active Spot (04:06.400).
  - Player awarded 2nd point (Score 2-0) (