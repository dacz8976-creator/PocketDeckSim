# Whole source review: 20261004_213625000_iOS

Reviewer: /root/pause_20261004_213625000_iOS. Review date: 2026-10-06T18:11:53.615465+00:00. Worker review complete, pending independent acceptance.

Source 20261004_213625000_iOS.MP4, SHA-256 aa7e935b335a2dfe11e43783f260698997845f7c85de8d6b1db976b7bf794225, 851427995 bytes, 460.651667 seconds. Frozen SOURCE.json unchanged.

One continuous human game in Deluxe Pack: Mega Emblem Event, owner Dacz8976 versus Noytamon. No Auto control is observed. Owner goes first. Outcome is a 2-3 loss, established by terminal point 3 at 450 and Defeat screen 459.

## Opening and deck

At 2 seconds the New deck 24 QR is filmed. QR_DECODE_RECEIPT.json resolves 20 cards and Grass-only Energy; deck screen 4, selection 6 and queue 8 continue into this game. Baseline live log does not include the deck, so DECK_USED.json explicitly preserves the missing-log limit.

At 31 seconds all five cards before Active placement, left to right: Professor's Research, Fragrant Forest, Butterfree, Caterpie, Quick-Grow Extract. Caterpie in slot 4 is selected Active 33-34. No setup redraw or replacement is shown. Opponent sets Exeggcute Active and Combee right Bench.

## Per-turn account

| Turn | Player | Source seconds | Numbered voluntary actions and meaningful results |
|---|---|---|---|
| 1 | owner | 44-81 | 1. Professor's Research: Draw Shelmet, then Caterpie (56 s); 2. Fragrant Forest: Place Fragrant Forest (61 s); 3. Fragrant Forest: Search Shelmet (67 s); 4. Shelmet: Bench first Shelmet (72 s); 5. Caterpie: Bench Caterpie (73 s); 6. Shelmet: Bench second Shelmet (78 s); 7. end turn: End Turn; no current Energy generated on first turn (81 s) |
| 2 | opponent | 82-137 | 1. Professor's Research: Two hidden cards drawn (89 s); 2. Pinsir: Bench Pinsir (97 s); 3. Fragrant Forest: Search result is hidden; subsequently Budew is publicly benched (124 s); 4. Budew: Bench Budew (125 s); 5. energy attachment: Attach one Grass from Energy Zone to Exeggcute Active (126 s); 6. retreat: Pay one Grass; Exeggcute moves left Bench (131 s); 7. Budew: Prickly Powder10; Caterpie40 to30 and loses abilities until it leaves Active (134 s) |
| 3 | owner | 138-181 | 1. Quick-Grow Extract: Find and directly evolve into Metapod; preserve10damage,70/80HP; ability restriction clears on evolution (152 s); 2. Lucky Ice Pop: Heal10 to80; tails, card discarded (159 s); 3. energy attachment: Attach one Grass from Energy Zone to Metapod Active (168 s); 4. Metapod: Ram30 KO; owner point1; opponent promotes Pinsir (171 s) |
| 4 | opponent | 182-198 | 1. Teal Mask Ogerpon ex: Soothing Wind applies to Pokemon with Energy (189 s); 2. energy attachment: Attach one Grass from Energy Zone to Combee right Bench (197 s); 3. end turn: End turn without attack (198 s) |
| 5 | owner | 199-223 | 1. Poke Ball: No effect: no valid Basic Pokemon in deck (209 s); 2. Butterfree: Evolve Butterfree130 (213 s); 3. energy attachment: Attach one Grass from Energy Zone to Shelmet left Bench (217 s); 4. Butterfree: Sunny Wind60; Pinsir90 to30; no damage to heal on Butterfree (221 s) |
| 6 | opponent | 224-240 | 1. Fragrant Forest: One hidden Basic searched (230 s); 2. energy attachment: Attach one Grass from Energy Zone to Combee right Bench (240 s); 3. end turn: End without attack (240 s) |
| 7 | owner | 241-269 | 1. Accelgor: Evolve Accelgor80 (245.5 s); 2. energy attachment: Attach one Grass from Energy Zone to Accelgor left Bench (255 s); 3. Butterfree: Sunny Wind60 KO; owner point2; opponent promotes Combee (259 s) |
| 8 | opponent | 270-331 | 1. Vespiquen ex: Evolve Vespiquen ex140, retain2Grass (276 s); 2. Fragrant Forest: No effect: no valid Basic in deck (282 s); 3. Combee: Bench second Combee (307 s); 4. energy attachment: Attach one Grass from Energy Zone to Teal Mask Ogerpon ex center Bench (309 s); 5. Vespiquen ex: Chase Order140 total KO; opponent point1 (312 s) |
| 9 | owner | 332-359 | 1. Butterfree: Evolve second Butterfree130 (336.5 s); 2. Hiking Trail: Replace Fragrant Forest (341 s); 3. energy attachment: Attach one Grass from Energy Zone to Butterfree Active (346 s); 4. Butterfree: Sunny Wind60,140 to80; Hiking Trail draws three at end (351 s) |
| 10 | opponent | 360-388 | 1. Leaf Cape: Effective maxHP140 to170, current80 to110; preserves60damage (363 s); 2. energy attachment: Attach one Grass from Energy Zone to Teal Mask Ogerpon ex center Bench (371 s); 3. Vespiquen ex: Discard Exeggcute; Chase Order140 KO; opponent point2; owner promotes Accelgor (378 s) |
| 11 | owner | 389-418 | 1. energy attachment: Attach one Grass from Energy Zone to Shelmet right Bench (392.2 s); 2. Accelgor: Evolve right Bench Accelgor80 with1Grass (393.5 s); 3. Poke Ball: No effect: no target in deck (396 s); 4. Professor's Research: Draw only Lucky Ice Pop; last card in deck, no second card drawn (401 s); 5. Accelgor: Deck and Cover50,110 to60; Poison/Paralysis blocked by Soothing Wind; active Accelgor stack shuffled; promote other Accelgor; Hiking Trail draws Accelgor (407 s) |
| 12 | opponent | 419-451 | 1. Exeggcute: Bench second Exeggcute (427 s); 2. energy attachment: Attach one Grass from Energy Zone to Teal Mask Ogerpon ex center Bench (440 s); 3. Vespiquen ex: Discard Teal Mask Ogerpon ex; Chase Order140 KO; opponent point3, owner loses (443 s) |

## Hands, draws and checkups

TURN_LEDGER.json contains one row per actual turn with both full boards, Energy Zones, points and hand transactions. Owner normal draws in turns 1/3/5/7/9/11 are Lucky Ice Pop, Butterfree, Poke Ball, Accelgor, Hiking Trail and Quick-Grow Extract. Research turn 1 reveals Shelmet then Caterpie. Fragrant Forest finds second Shelmet. Extract turn 3 evolves active Caterpie directly with Metapod. Research turn 11 draws only Lucky Ice Pop; no second card is added because the deck is exhausted. Hiking Trail turn 9 draws Accelgor, Research, Poke Ball, in that order. Turn 11 Trail draws the shuffled Accelgor.

Owner ending hand counts, including Stadium draws: turn 1=3,3=2,5=1,7=1,9=3,11=3. Turn 9 has 0 before attack and Trail adds 3. Turn 11 has 2 before attack and Trail adds 1. Opponent fan counts at owner starts are 3, 3, 3, 5, 4, 4 respectively; these are card-back observations, not hidden names.

## Consequential mechanics

Budew Prickly Powder deals 10 and prevents the defending Caterpie from using its Quick Growth ability. Owner uses Quick-Grow Extract instead, evolves Metapod and heals the remaining 10 with Lucky Ice Pop. The coin is tails, so Ice Pop is discarded.

Native 189 shows Ogerpon Soothing Wind: Pokemon with any Energy recover from and are immune to all Special Conditions. The blue upper-right icon is the board-effect badge; both Energy Zones stay Grass. Deck and Cover 50 still resolves on turn 11, but the UI explicitly says Vespiquen ex did not become Poisoned or Paralyzed at 410.

Leaf Cape on turn 10 adds 30 to maximum and current HP, preserving 60 damage: Vespiquen 80/140 becomes 110/170. This is not healing. Chase Order discards one benched Basic to add 70 to its base 70; the three attacks discard Combee, Exeggcute and then Ogerpon. Each boosted attack totals 140. Owner Butterfree 130 is knocked out on turns 8 and 10; owner Accelgor 80 is knocked out on turn 12.

## Limits and acceptance

No pile is opened anywhere, so requested periodic discard views are not shown. Face-up pile tops and public discards are retained without claiming full pile contents. Opponent searched/drawn identities remain hidden unless subsequently played. Requested seek times are retained, actual decoded PTS was not measured. Connection-unstable/app-view interruptions 75-77 do not change the board or indicate a recording cut. All recorded gameplay is covered. The supplemental capture is complete with these recording limits; live deck provenance still needs root new-entry/readback. Independent acceptance and registration remain the lead responsibility.
