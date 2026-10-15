# Full source review: 20261013_015011000_iOS.MP4

Reviewer: /root/pause_20261013_015011000_iOS. First pass model: gpt-6.1-sol, high. Review date: October 13, 2026. Source SHA-256: 7394580c71facb269a7c6703e890ff1eb360ffd509875eb09d03343f43b4fe7a. Source duration: 182.693333 seconds, native 1170x2532. All timestamps below are source-local seconds. Independent acceptance remains pending.

One complete human battle is recorded, preceded by its deck QR and matchmaking. Dacz8976 goes first against coke. No Auto option appears. The precise queue/rank label is not shown. The owner wins when coke fails to return within the allowed time, not through damage or a knockout. At 182.30 the result confirms Victory, turns played3, both point totals0, and damage done0.

SOURCE_TIME.json establishes creation at 2026-10-13 01:50:11 UTC, corresponding to October 12 at 20:50:11 in Chicago. The phone clock 8:50 at opening and 8:53 at ending corroborates this conversion. The filename's UTC date stays unchanged. Match date is October 12, 2026.

## Deck and setup, 0.00 to 40.50

At 1.00 the filmed deck QR is visible. QR_DECODE.json decodes all 20 card slots and Darkness Energy. The payload equals the independently decoded first two sources in this batch, but this receipt is bound to this source's own native frame and hash. Continuous footage closes the QR, shows New deck 16, enters matchmaking and starts this game without a deck edit. The exact filmed list is in DECK_USED.json. The own filmed code exactly matches the 20-card historical Pause Games snapshot retrieved 2026-10-13T04:53:35.861Z, deck Glimmora / Alolan Muk / Kingambit / Regigigas. DECK_USED.json preserves that actual20-card list, all log printing labels, source text and historical retrieval time. Fresh live readback is unavailable this turn per root access block. This snapshot is explicitly historical.

At 13.00 coke's profile is shown and at 21.00 the versus screen identifies Dacz8976. The owner goes first. At 27.50 all five initial card faces are visible before placement. The first name label is clipped, but its artwork matches the clearly named Copycat at 43.50. Left to right: Copycat, Poke Ball, Alolan Muk, Pawniard, Alolan Grimer. The literal card is non-ex Alolan Muk, matching QR entity 14630 and its visible 110 HP Power of Alchemy card. Pawniard is selected as Active, then Alolan Grimer is placed on the right Bench. Copycat, Poke Ball and Alolan Muk remain in hand. No setup replacement/redraw is shown. Opponent starts Falinks 70 HP, with four cards remaining after Active placement and no Bench. Opening and both placements are in PAUSE_GAME.json and native 27.50/34.50/37.00 evidence.

## Recorded turns

| Turn and ledger row | Source interval | Draws and numbered voluntary actions | Result and evidence |
|---|---|---|---|
|1 owner, TURN_LEDGER.json turns[0]|40.50 to 71.80|Normal draw Ilima. Play 1 Poke Ball searches Regigigas. Play 2 bench Regigigas center. Play 3 Copycat shuffles Alolan Muk and Ilima and draws four cards. Play 4 End Turn.|Owner Active Pawniard 50; Bench center Regigigas 150/right Alolan Grimer 70. No Energy attached. Native 43.50, 45.00, 47.00, 50.50, 60.50, 66.00, 67.00, 68.00, 68.50, 69.50, 71.50.|
|2 opponent, turns[1]|71.80 to 162.50|One hidden normal draw. Play 1 bench Tyrogue left. Play 2 attach one Fighting Energy to Falinks. There is no observed attack or deliberate End Turn input.|Falinks 70 with one Fighting; Tyrogue 30 left Bench. Both boards and0-0 score unchanged. Opponent fails to return and timer expires. Native 72.30, 75.50, 79.50, 81.50, 107.00, 162.50.|
|3 owner, turns[2]|162.50 to 169.00|Normal draw Glimmora. One Darkness generated. No voluntary card play, Energy attachment or attack.|Owner hand 5; one unused Darkness. Error states opponent did not return; later Victory. Native 164.50, 166.00, 167.00, 167.50, 168.50, 169.00, 172.00, 182.30.|

### Turn 1 detail

Ilima arrives during 42 to 43.20; native 43.50 shows the clear four-card hand before the first move. Poke Ball is already leaving the hand by44.20. The scheduled draw offsets44.20/46.20/49.20 therefore cannot be used as start-hand evidence; the dense43.50 view is retained instead. Opponent fan 4 is directly counted in the top crop.

Poke Ball reveals Regigigas at 47.00. Placing it center leaves hand 3: Copycat, Alolan Muk, Ilima. Regigigas's Seal of Antiquity prohibits attacking while Regirock, Regice and Registeel are absent. The prohibition icon and Can't attack banner at 52 to 53 are automatic restriction feedback, not a performed attack. Inspection/selection does not count as a card play. Regigigas remains undamaged with no Energy or Tool.

Copycat leaves the hand, then the two remaining cards are shuffled into the deck. Four cards arrive in visible reveal order: Professor's Research at 66.00, another Professor's Research at 67.00, Heavy Helmet at 68.00, Lucky Ice Pop at 68.50. These are observed reveal sample anchors, not exact onset times. Native 69.50 shows the settled four-card hand after all arrivals. The Research cards are draws from Copycat, not Research plays; there is no Research two-card effect. Heavy Helmet is highlighted at 70.50, stays in hand, and is never attached. No heal is used. Native 71.50 preserves the final hand 4 immediately before End Turn; 71.80 already shows turn 2 transition. No offered Supporter warning or voluntary decline is visible.

Hand arithmetic: 3 after setup + Ilima 1 - Poke Ball 1 + Regigigas search 1 - Regigigas bench 1 - Copycat 1 - shuffled 2 + Copycat draws 4 = 4. All identities are observed, not derived from deck membership.

### Turn 2 detail

Opponent draw increases the fan 4 to 5, visible at 75.50. One Fighting Energy is generated. Tyrogue 30, Slippy Knuckles 20 version, is placed left at about 78 to 79.50. The fan returns to 4. One Fighting attaches to Falinks by81.50. The small next Energy icon is Fighting; it does not establish a future numeric count. Falinks has Coordinated Unit and Invade 20; no second Falinks is in play, so no additional matching-Falinks bonus is established.

The opponent then takes no visible action. Every overview sample through the prolonged wait was inspected. At 107.00 the UI says Waiting for opponent to return. No retreat, attack, Trainer, damage, knockout or score change occurs. The per-turn countdown reaches zero and at 162.50 the owner turn 3 begins. This transition is system/timer behavior; a deliberate End Turn click is not visible. Owner hand remains the same four named cards throughout.

### Turn 3 and terminal detail

Glimmora arrives during 164.50 to 166.00 and settles as the fifth card. This is the 90 HP Shattering Crystal/Venomous Hit 30 version. It is not evolved or played. Native 167.00 is the +1 candidate and a clear pre-play hand: Research, Research, Heavy Helmet, Lucky Ice Pop, Glimmora. Opponent fan 4 is directly visible. One Darkness becomes available and remains unused; next icon is Darkness with unknown future count.

The +3 candidate 169.00 shows the error modal and the +6 candidate 172.00 shows Victory animation, so those cannot substitute for a hand view. Native 167.50 supplies the last clear hand and both boards as the before-end substitute because no End Turn or attack occurred. Native 168.50 already shows the error modal over a blurred board and hand. At 169.00 the error says Your opponent did not return within the allowed time. The visible OK acknowledgement is a post-terminal interface action, not a battle play. Victory vs coke is shown at 181.50; 182.30 confirms 3 turns, 0-0 and damage 0. The source ends on the result; no battle-log scroll or second game appears.

## Boards, hands and recording limits

TURN_LEDGER.json stores both complete start/after boards for all three turns, positions, HP/maxHP/damage, Energy by type, Tools, conditions, Stadium, points and Energy Zones. Pawniard 50, Grimer 70, Regigigas 150, Falinks 70 and Tyrogue 30 all retain full printed HP; no HP modifier appears. All Tools, Special Conditions and Stadium are absent. Regigigas attack restriction is explicitly recorded. No mixed Energy is attached; Falinks's single Fighting is the only attachment. Owner turn 1 current Energy is unavailable; owner turn 3 Darkness remains unused. Current-zone circles distinguish availability from future-type icons; future numeric counts stay null.

Neither player opens a discard pile anywhere. The side stack visibly displays Poke Ball followed by Copycat for the owner, but that is not a full discard snapshot. Dedicated absent-view records preserve this limit. Opponent hand identities and its normal draw are hidden. Exact artwork is not forced from a QR playable-entity identity. Approximate action onsets are bounded by retained samples; requested seeks are preserved and not falsely described as individually measured decoded presentation timestamps. These are recording/evidence limits, not omitted review intervals.

No strategic win-rate claim is justified by this disconnect victory. The footage does establish a consistent setup, successful Poke Ball search and four-card Copycat resolution. It does not establish how the battle would have played out.
