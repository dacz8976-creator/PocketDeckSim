# Frame-level checks of Dustin's Battle Logs videos (Sept 25, evening)

On Sept 25 Dustin allowed looking at the videos themselves when specifics matter, because the written reviews can misread them. Five items were checked frame by frame with ffmpeg (0.1-0.25 s steps around each moment). An independent second agent checked every item, re-extracting its own frames and trying to refute the first reading. All five readings held.
- The frames are in the laptop session's scratchpad (`video_checks/`), not in the repo.
- `video_frame_checks.json` has both agents' full reports, with every timestamp.
- Times below are video seconds.
- Card texts come from `lib/card.py`.

## 1. Rare Candy onto the Active with the opponent's Aerodactyl ex in play: refused (engine bug confirmed)
`Battle Logs/aerodactly_ex_rare_candy_test.MP4` (257.8 s).
- **Aerodactyl ex:** the opponent's. It came onto their Bench about 72 s, and the message "Can't play Pokémon from the hand to evolve Active Pokémon" appeared with a no-entry marker on Dustin's side (74.6-76.8 s). It became their Active about 161 s.
- **The Axew:** put on Dustin's Bench on turn 6 (169.5-171 s), then made Active on turn 8 by retreating Druddigon (233-238 s). A Metal Energy attached on turn 6 identifies it, so it is not the Axew played on turn 8.
- **The attempts:** his hand was Rare Candy, Haxorus and Haxorus. He tried Rare Candy twice (239.0 s and 254.5 s). Each time the game showed "The conditions for using this Item card have not been met". No target was offered, and the card stayed in hand.
- **Why it was refused:** the Active Axew was the only possible target: not the first turn, not put into play this turn, and Haxorus in hand. So the refusal is Primeval Law. The message itself is generic.
- **Not tested:** Rare Candy onto a Benched Basic. No Benched Basic was a legal target here.
- **Side observation:** at 102-103.5 s Dustin evolved a Benched Dratini into Dragonair from hand while Aerodactyl ex was on the opponent's Bench. That was allowed, as Primeval Law's "Active" wording says.
- **Side observation:** at 219-225 s Aerodactyl ex hit Druddigon, which has Rough Skin and a Rocky Helmet. The game showed Rough Skin's 20, then Rocky Helmet's 20 (140 → 120 → 100). This is from 1 fps sheets only. The engine sums both into one 40 (`hooks/counterattack.rs` 13-36): same total, and no rules difference unless something triggers between the two.

## 2. Heavy Helmet reads the current Retreat Cost (engine bug confirmed)
`Battle Logs/heavyhelmet_test.MP4` (118.4 s).
- **The holder:** Team Rocket's Slowking ex (Psychic, printed Retreat Cost 3). It evolved at about 73.5 s from a Slowpoke that had carried Heavy Helmet since about 21-27 s.
- **The Plaza:** Peculiar Plaza was in play from about 25-28 s, with the banner "Retreat Cost of Psychic-type Pokémon is 2 less". The game showed Slowking ex's Retreat Cost as 1 Colorless at 79, 85-88 and 113.5 s, and the Plaza was in play in every frame in between.
- **The attack:** on turn 4 the opponent's Stufful used Ram (printed 40). A "40" damage number showed at 104.0-104.6 s, and HP went 130 → 90 (105.4 s).
- **Nothing else changed the damage:**
  - No Weakness (a Colorless attacker; Slowking ex is weak to Darkness).
  - The opponent played no card that turn (hand 2 → 3 by the draw).
  - The Effects list showed only the Plaza.
- **Conclusion:** the Helmet's −20 did not apply at a displayed cost of 1. The engine reads the printed 3 and would have made it 20.
- **Correction to the first reading:** Goo-zooka was drawn at the start of turn 5 (108.2 s) and never played.

## 3. Legendary Pulse draws before Hiking Trail tops up (engine bug confirmed)
`Battle Logs/pulse_hikingtrail_order.MP4` (62.0 s).
- **Setup:** Dustin went first. On turn 1, Suicune ex was Active, a second Suicune ex was Benched, and his Hiking Trail was in play. His hand was empty when he tapped End Turn (52.25 s).
- **The draws, in order:**
  1. A "Legendary Pulse" banner showed over the Active Suicune ex only (52.7-54.1 s).
  2. Poké Ball was drawn (54.7-55.5 s): hand 0 → 1.
  3. A separate "Hiking Trail" banner showed (56.3-57.6 s).
  4. Cover Fossil and Armor Fossil were drawn (58.5-60.7 s): hand 1 → 3.
- **End state:** 3 cards at "Opponent's turn / Current turn: 2" (61.0 s).
- **The Benched Suicune ex didn't fire,** as "if this Pokémon is in the Active Spot" requires.
- **Engine:** does Hiking Trail first and ends on 4.

## 4. The unlabeled 5:41 pm video: an ordinary solo battle, not a test
`Battle Logs/20260925_224120000_iOS.MP4` (365.7 s).
- **What it is:** a solo battle against "Aerodactyl ex & Marowak ex Deck (Mythical Island)". Defeat.
  - Dustin played Zubat, Crobat, Arceus ex, Munchlax, Absol, Rare Candy and Starting Plains.
  - Aerodactyl ex never came into play, so it tests nothing about Primeval Law.
  - It is likely a first attempt at test 1, forty minutes earlier (inferred).
- **What it shows, all matching `RULES_FOR_AGENTS.md`:**
  - Growl's −20 made Venomous Fang do 0, and it still Poisoned.
  - Evolving cured Poison and kept the damage.
  - Weakness is +20 after other boosts.
  - Starting Plains gives +20 HP to Basics on both sides, not to Stage 1, and stacks with Giant Cape.
  - Lucky Egg draws on a Knock Out, before the opponent's point and the promotion.
  - An empty deck only skips draws.
  - Munchlax's Hungrily Draw and Copycat can be used with an empty deck.
  - Lisia can be played with no legal target in the deck.
  - Revenge's +60 comes on after a Knock Out.

## 5. Burn and Blessed Salt at the Checkup: the game uses the engine's order (settled; no bug)
`Battle Logs/Reviewed/20260922_010316000_iOS.MP4` (414.4 s). This answers the shot list's "Burn before or after Blessed Salt" item from existing footage.
- **Turn 15 Checkup:** Passimian ex was Active, Poisoned, Burned and Confused, with Garganacl, Machop and Garganacl on the Bench.
  1. Poison: 70 → 60 (popup 232.0 s).
  2. Burn: 60 → 40 (popup 233.0 s).
  3. Burn coin: Heads at 236.6 s; "Passimian ex recovered from being Burned" at 237.4 s.
  4. Blessed Salt from the left Garganacl: 40 → 50 (241.2 s).
  5. Blessed Salt from the right Garganacl: 50 → 60 (245.4 s).
  - So Poison comes first, then Burn's 20 and its coin, then the heals, one Garganacl at a time, left before right. That is exactly the engine's order.
- **Turns 16 and 18:** Poison comes first and the heals after it.
  - On turn 16 only one Blessed Salt banner showed, because the first heal already brought him to full HP. The written review's "two heals" there is not what the footage shows; the end state is the same.
- **Also seen:**
  - Confusion has no Checkup step.
  - Blessed Salt heals only its owner's Pokémon.
  - Checkup damage shows as popups; only the Burn coin gets a banner.
- **Still open:** whether Blessed Salt can save a Pokémon that Poison or Burn takes to 0. No footage has that case (shot list item "Blessed Salt when Poison takes a Pokémon to 0").

## 7. Rainbow Cave can't be used after the turn's Energy is attached (Sept 27; the engine is right)
`Battle Logs/Reviewed/20260927_170847000_iOS.MP4` (406 s), Dustin's proof video (one match against the AI). A locator, a checker and an independent verifier each extracted their own frames. Both readings agree with Dustin and with the engine.
- **Turn 2 (the test):**
  - Rainbow Cave is played at about 41-43 s.
  - At 67.1 s the glowing Stadium is tapped and the prompt "Use the effect of Rainbow Cave?" appears. It is dismissed without use: no banner, and the Zone is unchanged at 68.75 s.
  - At 69-70.5 s the Zone's Water is attached to the active Rattata, which empties the Zone (only the Fire "next" icon is left). The Stadium's glow goes off and stays off for the rest of the turn.
  - At 70.6 s the Stadium is tapped again: the same press animation as at 67.1 s; no finger shows in a screen recording.
  - At 71.0-73.0 s the red message "The conditions for using the effect of this Stadium card have not been met" appears. It is the only time this message appears in the video (a 2 fps scan of the whole video).
- **Contrast:** all 7 other prompts (116.5, 171.0, 177.5, 217.5, 250.0, 297.5 and 348.0 s) come while the Zone still holds an Energy not yet attached, and every accepted use works.
  - Each works the same way: banner, the current Energy bursts, the next Energy becomes current, and "Next Energy generated" shows a new next.
  - On turn 6 a declined prompt (171-173 s) did not use up the turn's use: accepted again at 177.5 s.
- **Caveat:** one after-attach attempt, on one client version.

## 8. Professor Sada: one Energy of each type in the discard pile, up to 3 (Sept 27; the engine is right)
Same video, same three agents. Both readings agree with Dustin's rule (`rules/04`).
- **First Sada (turn 4, 122-127.5 s), with two types.** Walking Wake is the only Ancient Pokémon in play. Worked out from events: the discard holds exactly Fire 1 (Rainbow Cave at 119 s) and Water 1 (the KO'd Rattata's, 102 s), since the only other Energy Dustin had generated was still in his Zone.
  - Sada attaches automatically, with no picker (one possible target), and exactly 2 Energy land: one Fire, one Water (127.5-129 s).
  - So Sada is playable with fewer than 3 types.
- **Second Sada (turn 14, 352-366 s), with duplicates.** The discard held about Fire 4, Water 2, Lightning 3: the 273.5 s view showed Fire 3, Water 1, Lightning 1, plus the later discards.
  - The picker "Please attach 3 Energy to Ancient Pokemon in any way you like" offered exactly three: one Fire, one Water, one Lightning, none twice.
  - Lightning and Water went to Raging Bolt ex, Fire to the benched Walking Wake.
  - The 378 s discard view shows Fire 3, Water 1, Lightning 2: exactly one of each removed.
- **Not shown:** the 1-type case (→ 1) and the 4+-type case (→ 3). They are neither shown nor contradicted.
- **Caveat:** the pile's contents before each Sada are worked out from events and the two on-screen views, not from a view opened just before either play.

## 6. Rainbow Cave's discarded Energy goes to the discard pile (added Sept 26; the engine is right)
`Battle Logs/Reviewed/20260908_015702000_iOS.MP4` (Dustin's deck 11, Archaludon/Haxorus/Dragonair, Fighting and Metal). This answers the gauntlet card check's questions R1 and R4 (`decks/gauntlet_2026-09-26/card_check.md`). The laptop session read it, and an independent agent re-extracted its own frames (0.25 s steps, 03:39.9-04:22.8) and tried to refute it. Both readings held.
- **The counter.** Dragonair's Dragon's Blessing picker ("Please choose an Energy") shows the discard pile's Energy by type.
  - **Turn 16:** Fighting 5, Metal 3 at 03:43.7-03:43.9. A Metal is picked, leaving 2.
  - **Turn 18:** Fighting 5, Metal 4 at 04:18.5-04:18.8.
  - All digits are clearly readable in both pickers.
- **Between the pickers:**
  - Turn 16:
    - The Blessing Metal lands on Haxorus (03:45.2-03:45.4).
    - With the Energy Zone showing current Metal and next Metal, the "Rainbow Cave" banner runs 03:46.4-03:47.4, the current Metal is discarded, and the next Metal moves up. "Next Energy generated" shows Fighting at 03:49.2-03:49.7.
    - The zone's Metal is then attached to Haxorus (03:50.2-03:51.0), leaving 2 Metal.
  - Turn 17:
    - Crawdaunt's Unruly Claw removes one Metal (03:58.2-03:58.5), so Haxorus goes from 2 Metal to 1.
    - Team Rocket Grunt's first flip is tails, so it removes nothing.
    - Icicle does 20 damage. Nothing else touches Energy.
- **So:** the pile goes from 2 Metal, +1 from Rainbow Cave, +1 from Unruly Claw, to 4. If Rainbow Cave's Energy vanished, it would be 3, and nothing else between the pickers could add a Metal.
  - The Energy that Rainbow Cave throws away goes to the discard pile, as the engine does it (`actions/apply_stadium_action.rs` 84-87).
  - So Dragon's Blessing, Flame Patch and the like can reuse it. This does not flatter Rayquaza or Charizard Y.
- **R4 (Rainbow Cave after the turn's attachment):** not shown.
  - On turn 16, Rainbow Cave came before the only attachment from the zone.
  - The written review's "manual attach at 03:45.5-03:46, then Rainbow Cave" misread the Blessing Metal as that attachment.
  - On turns 4 (00:23-00:28) and 12 (02:16-02:20), Rainbow Cave also came before the attachment.
  - The engine's before-the-attachment offer is not contradicted by any footage seen so far, and not confirmed either.
- **Also seen:** Rainbow Cave discards the current Energy, and the queued one becomes current, even when both are Metal. This matches the Sept 25 second-pass claim.
- **Caveat:** the discard itself is never shown arriving in the pile. It is inferred from the two counts.
  - The written review's Energy history for the earlier turns doesn't add up under either reading. It is off by one Energy under this one, and by two or more if the Energy vanished. So the review probably miscounts one Energy somewhere before turn 16.
  - The turn 16-18 check depends only on the frames between the two pickers.
