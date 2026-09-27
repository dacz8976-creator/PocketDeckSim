# Does kp3 waste X Speed? (Sept 27)

**Why:** Dustin, on quiz 2 Q02's game: the bot played X Speed, never retreated, and swung Stretch Kick at an empty Bench, when a free retreat into Bonsly for Teary Attack was there. Worth a fix only if it is common.

**How:** `xspeed_census.py`. The 10 decks that run X Speed; kp3 on both sides against the 8 panel lists; 240 games per deck; official engine; seeds 22,800,000,000+ (START_HERE).

**Result (`summary` in `census.log`):**
- 944 turns with X Speed played. In **723 (77%)** the same side retreated later that turn.
- In **221 (23%)** it didn't. In 156 of those a retreat was still on offer later that turn, so it was a choice, not a block. In 159 the side attacked anyway.
- That is about one wasted X Speed every 11 games.
- By deck it ranges from 4 of 74 (brew 02) to **75 of 143 in Dustin's deck 12** (Ariados/Whimsicott/Ogerpon, 52%). The three panel decks are 22-25%.
- **The common shapes** (the first examples in the log): X Speed played just before Copycat (the hand gets shuffled away anyway), or just before attacking with the Pokémon already in front.

**Reading:**
- It is a real habit, but mostly it burns one thin Item card.
- Q02's miss is a bigger one: a free retreat into a free attacker, which is the "attack with a cheap Basic" habit B2c found.
- Recommendation: no separate candidate. This goes in with the Trainer pricing class already queued in RUN5 (B5), with deck 12 as the deck to check it on.
