# Retrospective opening and first-six-owner-turn hand supplement

Reviewer: sol_retro_wailord_021402. Submitted for independent Sol acceptance October 2, 2026. Main battle status remains Reviewed.

Source: 20261002_021402000_iOS.MP4. SHA256 5b9bcc18507ea541f35741ed451edb58c743300be366db7f8d4fc88856b36759; 795,968,694 bytes; 430.026667 seconds; native1170 x2532. Archived source was hydrated and hashed once, matching the frozen SOURCE.json before extraction. Source path and original bytes were preserved.

Scope: Add the opening five and missing hands for game turns1,3,5,7,9,11 only. Accepted outcomes, boards, points and voluntary plays remain inherited by exact accepted-row provenance. Owner turn13 is not requested. No other Wailord recording, simulator, shared event/index or external artifact was edited.

## Opening

Native18.00s before Active placement reads, left to right: Poké Ball; Pokémon Center Lady; Heavy Helmet; Wailmer; Irida. Native19.00s shows Wailmer selected from original slot4. Accepted setup places it Active with no Bench. All five identities are direct frame observations; no card was filled from the deck list.

## Requested owner hands

| Game turn | Chosen pre-play native seconds | Hand, left to right | Normal draw | Inherited first voluntary play | Ending hand and count | Opponent fan |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 37.50 | Poké Ball; Pokémon Center Lady; Heavy Helmet; Irida; Wailord | Wailord | Heavy Helmet: Attached | Pokémon Center Lady; Irida; Wailord (3) at 50.50s | 3 |
| 3 | 72.30 | Pokémon Center Lady; Irida; Wailord; Cyrus | Cyrus | Wailord: Non-ex Wailord 200 HP | Pokémon Center Lady; Irida; Cyrus (3) at 77.00s | 5 |
| 5 | 100.80 | Pokémon Center Lady; Irida; Cyrus; Wailord ex | Wailord ex | Wailord ex: Wailord ex 250 HP | Pokémon Center Lady; Irida; Cyrus (3) at 108.00s | 7-8, overlap limit |
| 7 | 132.00 | Pokémon Center Lady; Irida; Cyrus; Professor's Research | Professor's Research | Professor's Research: Draws two cards | Pokémon Center Lady; Irida; Cyrus; Copycat (4) at 146.00s | 7-8, overlap limit |
| 9 | 205.00 | Pokémon Center Lady; Irida; Cyrus; Copycat; Lucky Ice Pop | Lucky Ice Pop | Indeedee ex: First Watch Over heals 140 to 160 | Soothing Shore; Lucky Ice Pop (2) at 275.00s | 5 |
| 11 | 316.50 | Soothing Shore; Lucky Ice Pop; Professor's Research | Professor's Research | Indeedee ex: First Watch Over heals 150 to 170 | Soothing Shore; Cyrus (2) at 362.00s | 4 |

Turn5 required dense inspection:100.00s still shows the Wailord ex draw moving down,100.80s shows all four cards in an unzoomed fan, and101.20s already shows evolution. The chosen100.80s frame is the brief pre-play hand; later +offset candidates cannot replace it.

Turn7 Research adds Indeedee ex, then Copycat. Indeedee is directly visible at137.00s, and Copycat is directly readable in the retained hand at139.00s after Indeedee is placed. Ending count reconciles4 - Research1 + draws2 - Indeedee1 =4.

Turn9 Copycat refills five cards in append order: Heavy Helmet; Indeedee ex; Soothing Shore; Lucky Ice Pop; Soothing Shore. Native252.00s displays all five together, including both Shores. Native249.50s shows the first Shore reveal above Helmet and Indeedee; native250.00s shows Ice Pop; native252.00s includes the second Shore. One Shore is played, leaving the other in hand. Native275.00s shows the final two cards, remaining Shore and Ice Pop. The initial Pop is removed after its inherited heads-return/tails-discard sequence; Center Lady, Irida and Cyrus are shuffled by Copycat.

Turn11 normal draw is Research. Its two Research reveals are Cyrus at330.00s and Poké Ball at331.00s. This supplies reveal order to the accepted unordered pair; it does not change the accepted play account. Poké Ball obtains no card, and Pop is later discarded. Native362.00s directly shows the final two cards, Shore and Cyrus. Count reconciles3 - Research1 + draws2 - Poké Ball1 - Pop1 =2.

## All recorded game turns as inherited context

Each row below is copied from the accepted REVIEW.md and bound by accepted_review_sha256 c6e361d1f95db21cf3b2d500d8d6d3f7db0b0d059aae500a22a677b466abe044. The inherited account is retained verbatim. TURN_LEDGER.json contains all fourteen rows, both board reference objects, numbered inherited action units, and source provenance. Only the six target owner hands are newly observed.

| Supplied phase | Accepted meaningful actions and state, inherited | Original evidence, inherited |
| --- | --- | --- |
| Turn 1, about 35-52s, owner | Heavy Helmet attaches to Active Wailmer. Poké Ball obtains the second Wailmer, which is benched. No Energy attachment or attack occurs. | overview 02; native 48.00s |
| Turn 2, about 52-72s, opponent | Meloetta's Strange Singing adds a hidden random Psychic Pokémon to the opponent's hand. Giratina ex uses Broken-Space Bellow and gains Psychic Energy, ending the turn. Giratina's early buildup includes normal Energy attachment; no attack or HP change occurs. | overview 02, native 92.00s for subsequent three-Energy state |
| Turn 3, about 72-82s, owner | Active Wailmer evolves into non-ex Wailord 200 HP. Owner attaches first Water to that Active. No attack with one Energy. | overview 03 |
| Turn 4, about 82-98s, opponent | Strange Singing triggers. Psychic attaches to Meloetta. Giratina ex uses Broken-Space Bellow again, building its Energy. No damage. | overview 03; native 92.00s |
| Turn 5, about 98-112s, owner | Benched Wailmer evolves into Wailord ex 250 HP. Second Water attaches to Active non-ex Wailord. Owner passes without attacking. | overview 03-04 |
| Turn 6, about 112-130s, opponent | Strange Singing triggers. Ralts 60 HP is benched and receives Psychic Energy. Giratina ex uses Broken-Space Bellow again. No attack. | overview 04; native 122.00s, 124.00s and 160.00s |
| Turn 7, about 130-148s, owner | Professor's Research draws two cards. Indeedee ex 130 HP is benched. Third Water attaches to non-ex Wailord. It still needs four Energy for Whale Pump, so no attack occurs. | overview 04-05 |
| Turn 8, about 148-204s, opponent | Strange Singing triggers. Rare Candy evolves Ralts into Mega Gardevoir ex. Mega Diancie ex is benched. Peculiar Plaza reduces Psychic Pokémon retreat cost by two. Sabrina forces an owner replacement; owner selects zero-Energy Wailord ex, benching the three-Water non-ex Wailord. Opponent retreats Meloetta and promotes Mega Gardevoir ex, supplies its second Psychic, then attacks with Fantasia Force. Wailord ex takes 110, 250 to 140. The attack adds three Psychic from the Energy Zone, visibly allocated into the Mega Gardevoir/Diancie board. | native 160.00s, 165.00s, 171.00s, 177.00s, 180.00s, 188.00s, 193.00s, 199.00s, 205.00s |
| Turn 9, about 204-280s, owner | First Indeedee's Watch Over heals Active ex 140 to 160. Owner inspects Mega Diancie: expected Brilliant Storm damage is 240 at that moment, not a played attack. Lucky Ice Pop heals 160 to 180; heads returns it to hand. Reused Pop heals 180 to 200; tails discards it. Copycat shuffles the remaining hand and draws to opponent hand count. Soothing Shore replaces Peculiar Plaza. Second Indeedee ex is benched and its Watch Over heals 200 to 220. Heavy Helmet attaches to Active ex. Water attaches to Active ex, enabling Shore's end-of-turn heal 220 to 240. No attack. Non-ex Wailord remains benched with three Water. | native 205.00s, 211.00s, 232.00s, 236.00s, 241.00s, 249.00s, 254.00s, 263.00s, 265.00s, 268.00s, 272.00s; overview 08 |
| Turn 10, about 280-314s, opponent | Protective Poncho attaches to benched Mega Diancie, protecting it from damage while benched. May is played but the interface says no cards in deck can be the effect's target. Psychic attaches to Mega Gardevoir. Fantasia Force hits Active ex for 90 after Heavy Helmet, 240 to 150. Three more Psychic are distributed; stable post-turn board shows Giratina four, Meloetta two, Mega Diancie four and Mega Gardevoir four. Score remains zero-zero. | native 291.00s, 296.00s, 300.00s, 309.00s, 336.00s; overview 09 |
| Turn 11, about 314-366s, owner | Both Watch Over abilities heal 150 to 170 to 190. Professor's Research draws Poké Ball and Cyrus. Poké Ball is played with no remaining Basic target, confirmed by on-screen message. Water is attached to benched non-ex Wailord, bringing it to four, while ex remains Active with one. Lucky Ice Pop heals ex 190 to 210; tails discards it. Shore heals ex to 230 at turn end. Owner does not attack. | native 331.00s, 336.00s, 350.00s, 360.00s; overview 09-11 |
| Turn 12, about 366-396s, opponent | Opponent plays Poké Ball with no deck target. Psychic attaches to Mega Diancie, which now has five. Mega Gardevoir retreats, discarding one Psychic, and Mega Diancie promotes. The resulting visible opponent board has fourteen Psychic in total. Brilliant Storm hits for displayed 300 after the owner's Helmet, knocking out 230-HP Wailord ex. Opponent gains two points. Owner is prompted to replace it. | native 373.00s, 383.00s, 386.00s, 392.00s; overview 11 |
| Turn 13, about 396-408s, owner | Non-ex Wailord promotes at full 200 HP. Owner draws Irida and inspects it; Irida remains in hand, so it is not treated as played. Fifth Water attaches to Wailord. Whale Pump displays 110 and is used, reducing Active Mega Diancie from 170 to stable 60 HP. This is the owner's only recorded attack. No owner point is earned. | native 402.00s, 410.00s; overview 12 |
| Turn 14, about 408-424s, opponent | Mega Diancie remains Active with stable 60 HP, then uses Brilliant Storm again. Displayed 300 damage knocks out 200-HP non-ex Wailord despite Heavy Helmet. Opponent gains one point and reaches three. | native 410.00s, 416.00s, 422.00s |

## Capture and evidence limits

HAND_SUPPLEMENT.json capture_status is complete_with_recording_limits for the opening and six specified hands. It does not claim a fresh full-battle capture. No target hand identity remains unresolved, so no Astra question is requested. Independent Sol acceptance remains pending.

All full frames are original-resolution1170 x2532, either newly retained or referenced in the accepted packet. Each registered frame has a native bottom crop [0,2025,1170,2532] and top crop [0,0,1170,550]. Full original frames remain linked, so crops are not replacements. Actual decoded-frame PTS was not measured; requested seek time is explicitly separate. Source times stay local to this recording.

Draw-end times are bounded estimates from the retained animation/fan frames. Candidates were chosen around expected +1,+3,+6 and dense pre-play windows; those nominal offsets are not claimed exact after boundary refinement. Later candidates commonly follow quick first plays, and their suitability is explicitly flagged. The readable pre-play fan, reveal and ending evidence governs each hand.

Opponent fans are directly counted as3,5,range7-8,range7-8,5,4 for the target turns. Tight overlap prevents an exact count at turns5/7. No bookkeeping count is substituted. Hidden identities stay unknown. No opened discard-pile window is seen in retained target/reveal evidence, and this bounded task did not freshly inspect all intervening footage for pile views. Both start/end boards and their Energy Zones are inherited references or explicitly outside the requested addition, with no fabricated fresh values.

DECK_USED.json is the lead-supplied verified current20-slot live snapshot. Historical-version uncertainty and variant labels were preserved, and it was never used to identify hidden cards.

## Metrics

New full native frames: 48 of cap48, 21,886,671 bytes. Existing native frames referenced: 16. Retained native crops: 128, 18,420,244 bytes. One successful source hash/read hydrated the original; three extraction passes of38,8,2 frames. Initial sandbox reads/extraction were denied, then authorized escalated reads completed. Wall time at submission about 12.2 minutes, including approximately6.5 minutes waiting for source hydration. Token and dollar usage were unavailable, not estimated.

This packet is submitted to the lead for separate Sol source checks. The lead alone accepts and restores the source to online-only.
