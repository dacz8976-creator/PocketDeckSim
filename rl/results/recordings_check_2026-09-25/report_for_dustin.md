# Your recorded battles vs. the engine

"Engine" means the simulator's rules code, in its current official version. A "claim" is one rule statement taken from your battle reviews, like "Weakness adds +20."

## 1. What was read

- 93 review files were read. None were missing.
- They cover about 44 recorded battles. That is my count of the separate videos cited. The two-part 220914/221051 video counts as one.
- 10 reader batches pulled out 528 rule observations.
- After merging duplicates, that left 249 separate claims.
- Each claim was checked against the engine code and its tests.

## 2. Results

- Engine matches the recording: **235**
- Engine seemed to disagree: **8**
- The footage can't settle it: **4**
- Screen-only detail the engine doesn't model: **2**

## 3. Confirmed mismatches

**None.**

Eight claims looked like disagreements. Each one went to three skeptics. A skeptic is a second checker whose job is to try to disprove the finding. All eight were thrown out, 3 votes to 0 each time. In every case, the claim had misread the video or said more than it showed. The engine did what the footage shows.

So nothing here affects the 8 table decks, your decks, or today's card work.

## 4. Mismatches that fell apart

- **Dewott, Razor Shell (R18):** The 0 damage came from Heavy Helmet on Wailord (20 − 20). It was not a Tails "miss." The log shows only one use, not two.
- **Eevee, Boosted Evolution (R67):** This is an Ability, not an attack. The review itself says "No attack." The engine lets the Active Eevee evolve early, just as seen.
- **Sightseer (R150):** The card takes every Stage 1 in the top 4 cards. The video showed one card taken and never showed the other three.
- **Poké Ball (R154):** The footage is from your screen, so it can't show what the opponent saw. "Revealed to both" was a guess.
- **Points capped at 3 (R182):** The score track only has 3 circles, and the banner said "+2 points!" So the video can't show a 4. The winner is the same either way.
- **Baxcalibur, Ice Maker (R192):** Every recorded use went to the Active Water Pokémon, as the card says. The one note that hinted at a Bench target is disproved by the review's own frames.
- **Confusion flips (R234):** Flower Shield blocked Hypno. One Tails self-check confused Mewtwo ex. The second flip was Mewtwo's check when it attacked. No one-flip-per-Pokémon rule was shown.
- **Checkup order (R240):** Checkup is the step between turns where Poison, Burn and Sleep happen. The claim's own video shows the Burn flip after Poison took Hypno to 0. The engine does the same.

## 5. Today's work: what the recordings back up

- **Weakness:** Adds a flat +20, seen in four battles (R2). It doubles only under Bounded Field (R4). It is added before Tool reductions (R7).
- **Cyrus:** Pulls up only a damaged Benched Pokémon, with no retreat cost. Seen in 6 battles (R100). There is no engine test for it yet.
- **Soothing Wind:** Blocks conditions on any of your Pokémon that has Energy attached. Whimsicott ex got Confused only after Ogerpon was gone (R197).
- **Boiler Smog:** Triggers when it evolves, gives Poison and Burn, and is optional (R218, R222).
- **Thieving Incisors:** Optional. It moves one random Energy (R194).
- **Darkness Claw:** An attack, not an Ability. It can only discard a Supporter (R206). The 022627 review failed, so we couldn't check which card was discarded.
- **Roar in Unison:** Attaches 2 Darkness Energy and does 30 damage to itself (R59).
- **Hyper Ray:** Does 130 and discards all its Energy (R60). A side finding from reading the code: that Energy never reaches the engine's discard-Energy pile. Worth fixing.
- **Copycat:** Shuffles your hand into the deck, then draws as many cards as the opponent holds (R142, R143). It doesn't discard your hand.
- **Quick Growth:** Caterpie evolved at the end of the other player's turn, as the card says (R199).
- **Chase Order, Solid Shell:** No recording covered them. Solid Shell only has a unit test, which is a small automatic check in the code (20 − 20 = 0).

## 6. What to test next time you play

The footage couldn't settle these (4):
- **Meowth, Carefree Steps (R10):** Get a frame where the coin face is readable, plus Meowth's HP before and after.
- **Thieving Incisors (R45):** When Raticate ex evolves, note whether you tapped yes or no. At 015702 ~03:08 a banner showed but no Energy moved.
- **Two Sitrus Berries (R84):** Record a Revavroom holding two Berries that ends a turn at 31–60 HP (out of 120). The engine says it heals 30 once and keeps one Berry.
- **Heavy Helmet (R87):** Record a Helmet on a Pokémon with retreat cost 3 or more (like Kingambit) taking a hit. Expect the printed damage minus 20.

Screen-only (2, skip): the 3-circle score track (R181) and the "Damage done" stat (R242).

Also worth getting on video:
- **Blessed Salt rescue:** Can Garganacl's heal during Checkup save a Pokémon that Poison took to 0? The engine says yes. It has never been recorded.
- **"Random" Energy picks:** In the engine, Psychic and Unruly Claw take the last-attached Energy, not a random one (R103, R200). At 015702 T5 the game took the first-attached Metal.
- **Rare Candy vs Primeval Law:** The engine lets Rare Candy evolve the Active Pokémon while Aerodactyl ex is in play. The card text seems to forbid that (R189).

## Update: the three code side notes were checked

A separate check read the code and the card texts. All three are real engine mistakes:

- **"Discard all Energy" attacks** (Hyper Ray, Thunderbolt, Luster Purge and others) don't put that Energy in the discard pile. Cards that pull Energy back from the discard pile, like Volkner, Lusamine and Dragonair, would miss it.
- **Crawdaunt's Unruly Claw and the Supporter Psychic** always take the last Energy attached, not a random one. This only matters for a Pokémon with two Energy types.
- **Rare Candy** can evolve the Active Pokémon while the opponent's Aerodactyl ex (Primeval Law) is in play. The card text says it shouldn't.

None of these touches any game the simulator has played for you so far: no deck in the project has the cards that trigger them. They are on the list for the engine fixes.
