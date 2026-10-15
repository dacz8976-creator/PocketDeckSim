# Whole-source review: 20261010_020908000_iOS.MP4

Reviewer: /root/pause_020908, gpt-6.1-sol. Review UTC date: October 10, 2026. Match date: October 9, 2026, 21:09:08 America/Chicago (lead-verified file metadata and filmed clock). Frozen source SHA-256: 6771089aca9afe1e952e047017c07b74964a184011832179c27fe7b7f839bffc. Duration 388.888333 seconds. Native dimensions 1170x2532.

One human battle against Desk (Lv30), owner Dacz8976, in the filmed Deluxe Pack: Mega Emblem Event queue. No Auto control appears. Owner wins after the filmed opponent connection-timeout notice, not a three-point finish. At378 seconds the Error states, "Your opponent did not return within the allowed time." Victory appears at382 seconds. The last gameplay board is1-0. The native388.8s final result confirms went second, seven turns played, points1-0 and140 damage done, with Kingdra ex Card of the Game. The footage does not establish why the opponent disconnected or any intention to quit.

## Setup and source continuity

0-5s: native QR and New deck 13, visible20/20 deck, then matchmaking with no visible intervening deck change. The filmed QR matches the dated live Pause Games deck ID filmed-qr-b649812c0d42. DECK_USED.json saves20 slots and duplicate counts. Exact artwork/rarity is not encoded by that QR.

At27s before Active placement the five cards left to right are Team Rocket's Weezing ex, Team Rocket's Koffing, Team Rocket's Koffing, Soothing Shore, Horsea. Horsea, original slot5, becomes Active at29s. Owner elects no starting Bench cards and goes second. Opponent reveals Nihilego70HP Active and Team Rocket's Magmar70HP at right Bench slot3. Setup ends around47s. No redraw occurs.

## All seven recorded turns

|Turn|Player|Source interval|Observed actions and resulting state|
|---|---|---|---|
|1|Desk|50-70s|Hidden normal draw; Professor's Research draws two hidden cards; Deceptive Needle on Nihilego; ends without attack. Needle10 damage makes Horsea40/50.|
|2|Owner|71-106s|Normal draw Poke Ball. Bench both Koffing in left/middle slots, Poke Ball finds Horsea, bench Horsea right, play Soothing Shore, attach Water Active Horsea, Hook30 into Nihilego. Shore heals Horsea to50. End hand one Weezing.|
|3|Desk|106-169s|Hidden normal draw, Poke Ball finds Koffing, bench Koffing middle, Darkness to right benched Magmar, Hiking Trail replaces Shore, ends without attack. Needle10 makes Horsea40.|
|4|Owner|169-214s|Normal draw Seadra; evolve Active Horsea to Seadra60/70, evolve left Koffing to Weezing140, accept Boiler Smog Yes to Poison/Burn Nihilego, attach second Water Seadra, End Turn with zero cards and no attack. Hiking Trail reveals Poke Ball at200s, Hiking Trail at201s, Rare Candy at202s, in order (native seek frames independently checked). Poison/Burn30 lowers Nihilego40 to10; Burn heads clears Burn, Poison remains.|
|5|Desk|214-252s|Leaf, retreat zero-Energy Nihilego into Magmar (Poison clears), Team Rocket's Master Plan confuses Seadra and tails confuses Magmar too, Lum Berry on Magmar, attempt Derisive Roasting. Confusion tails: The attack did nothing. Lum Berry clears Magmar Confusion and is discarded. Hiking Trail refills opponent fan to3 hidden cards. Seadra stays60/70 and Confused.|
|6|Owner|252-302s|Normal draw Kingdra ex, first play Poke Ball finds no eligible target, evolve Active Seadra to Kingdra160/170 and clear Confusion, Water to bench Horsea, Stormy Prison110 including Water weakness knocks out Magmar. Owner point 1; opponent promotes Nihilego10. Hiking Trail adds Copycat. Owner ending hand Hiking Trail/Rare Candy/Copycat,3 cards.|
|7|Desk|302-378s|Hidden normal draw; Poke Ball no target, Elegant Cape on benched Koffing (Basic remains60HP), Darkness to Koffing. Waiting for opponent to return appears. No attack or normal turn-end resolution before connection timeout.|

Each table row corresponds to TURN_LEDGER.json turn_number. The ledger numbers every voluntary action and separates automatic effects, condition checks and Stadium draws. Boiler Smog prompt187s is explicitly accepted. No unoffered option is labeled declined. No owner Research or Copycat is played in this game; Copycat is a named automatic Stadium draw at the end of turn 6.

## Native hand and board evidence

All retained native frames have full frame, bottom-fifth crop [0,2025,1170,2532] and top crop [0,150,1170,760]. TURN_EVIDENCE.json stores source seek times, draw approximations and candidate suitability. Selected pre-play owner hands are73.4s (turn 2),174.8s (turn 4),255s (turn 6). Turn2 and6 first plays occur too quickly for the scheduled+1/+3/+6 frames, so dense pre-play frames are selected and scheduled post-play candidates retained with explicit labels. Turn4+1/+3 candidates retain both hand cards; +6 is after evolution. Clear before-ending views94s/196s/270s have respective hand sizes1/0/2. Automatic Hiking Trail draws change the final resolved hand counts to1/3/3.

Opponent fans directly count4/3/3 card backs at owner turns2/4/6. These are visual fan counts, separate from transaction arithmetic. Owner Energy is Water; opponent Darkness icons are observed. Both current and small next orb types are captured; future counts are not shown. All board starts/ends, Bench slots, printed/current HP, damage, typed Energy, Tools, conditions, Stadium and points are in the ledger.

## Recording limits and review scope

Neither discard pile is opened. The visible top discard card and play history cannot establish complete pile contents. No hidden hand identities are inferred from the deck. Opponent hidden draws remain unknown. Requested seeks are local source times; exact decoded frame PTS is unmeasured. Notifications briefly cover the top clock/fan around177-184s and370s; neighboring clear frames supply the visible board. The late waiting sequence is inspected through its timeout, then Victory and source end388.8s (final Victory statistics). No second match appears.

The whole-source review is complete at worker level. The Pause Games supplement is complete with recording limits. Independent lead acceptance, external logging and source archival remain lead responsibilities. No shared index, event, external artifact or simulator was modified by this worker.
