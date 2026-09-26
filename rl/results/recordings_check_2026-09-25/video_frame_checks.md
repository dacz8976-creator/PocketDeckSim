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
