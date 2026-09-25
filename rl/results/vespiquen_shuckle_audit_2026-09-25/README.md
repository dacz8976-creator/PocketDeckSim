# Vespiquen's Chase Order: Shuckle, Ogerpon and Cyrus (Sept 25)

**What prompted this:** Dustin's read of the Chase Order count (`../chase_order_2026-09-25/`), which found kq3 keeps Shuckle ex more and discards Teal Mask Ogerpon ex more than kp3. In real play, he says:
- Shuckle ex takes the hits while Vespiquen ex sets up;
- then you discard Shuckle to Chase Order;
- Ogerpon protects you from Special Conditions;
- and an injured benched Pokémon is exposed to Cyrus.

**Short answer:**
- **What the code shows** (checked by two rounds of skeptics, three per claim; the claims below are the versions that survived):
  - the bots price neither of Dustin's two reasons, the Cyrus exposure of a damaged benched Pokémon or the value of status protection;
  - kq3's bench bonus leans toward keeping Shuckle. That is the opposite of his pattern, and it is the likely reason for kq3's measured shift.
- **Not shown:** whether this costs Vespiquen win rate. The existing counts can't answer it.
- Diagnostic only. Nothing here changes a bot.

## The cards (card database, `lib/deckgym-database.json`)

- **Vespiquen ex, Chase Order [G][G] 70:** "You may discard 1 of your Benched Basic [G] Pokémon. If you do, this attack does 70 more damage." In the Vespiquen list, the Basics that can be discarded are Combee, Shuckle ex and Teal Mask Ogerpon ex.
- **Shuckle ex:** 120 HP. Solid Shell: "This Pokémon takes −20 damage from attacks." Triple Slap costs [G].
- **Teal Mask Ogerpon ex, Soothing Wind:** "Each of your Pokémon that has any Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions." Energized Leaves costs [G][G].
- **Cyrus:** "Switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot." It can be played only if such a target exists.
- **Vespiquen's seven research opponents:**
  - **Cyrus:** Blaziken, Hydreigon, Lucario and Sceptile run one each; Weezing runs two. Altaria has only Sabrina, where the Vespiquen player picks the new Active. Suicune has neither.
  - **Special Conditions:**
    - Altaria: Asleep (Sing, Hypnoblast, Dark Slumber, Sleepy Lullaby);
    - Blaziken: Burned (Mega Burning);
    - Sceptile: Poisoned (Terminating Tail);
    - Weezing: Poisoned and Burned (Boiler Smog) and Confused (Confusion Gas);
    - none in Hydreigon, Lucario or Suicune.

## What the bots price (claims that survived three skeptics, in their wording)

**C1, 3 of 3: the clock ignores gusts.**
- The damage-aware clock counts the Active first. It then counts benched victims in the order the victim's owner would prefer (`engine/src/players/value_functions.rs` 903–950, key at 924–930):
  - the most HP left per knockout point;
  - or the most HP left when one point is still needed.
- So a damaged benched Pokémon is counted later, not first.
- No term lets the attacker pick a damaged benched Pokémon first, as Cyrus does. The same holds for k3, kp3, kq3 and kd3; under kd, the order still uses raw HP.

**C2, 2 of 3, corrected wording: no opponent's turn.**
- k3, kp3, kq3 and kd3 have no opponent ply (`players/mod.rs` 424–432, 502–536), so their search never plays out the opponent's turn.
- The one exception is a narrow check at the turn boundary. It resolves the opponent's plain attacks from the Active and scores a line as a certain loss if one wins outright. It looks only at attacks and refuses any board with a Special Condition.
- So an opponent's Cyrus play or Special-Condition attack is never simulated. It can matter only through the evaluator, and C1 and C3 say the evaluator doesn't price it.

**C3, 3 of 3: status protection is unpriced.** No evaluator term reads Soothing Wind, or status immunity at all. The ability acts only through the game rules during play, so its value against the opponent's future Special Conditions isn't priced.

**C4, 2 of 3, sharpened: kq3's bench term leans toward Shuckle.**
- kq's bench term is 250 × the best benched attacker's readiness (`value_functions.rs` 527–532, 1745–1781).
- Readiness is the share of that Pokémon's attack cost that is paid, so it favors the cheaper attack: Shuckle ex's [G] over Ogerpon ex's [G][G].
  - At one [G] each, it keeps Shuckle by 125 points.
  - It keeps Ogerpon only when Shuckle has no [G] and Ogerpon has some.
- This fits kq3's measured shift (keeps Shuckle 36.8% vs 41.6% discarded; discards Ogerpon 17.4% vs 12.9%), which runs opposite to Dustin's pattern. The mechanism is shown in the code; the shift itself was not traced choice by choice.

## What the existing counts can and can't say

- A recount from the raw per-game files matches the cloud's numbers exactly (kp3 3,510 choices, kq3 3,135).
- The apparent splits between Cyrus decks and the rest, and between status decks and the rest, come from which decks fall in each class, not from Cyrus or status. For example:
  - Sceptile (Cyrus) and Suicune (no Cyrus) both clear the Bench about 88% of the time;
  - kq3's status split rests on Sceptile alone.
- The counter didn't record the Bench at each choice.
- So the existing data is no evidence for or against the pattern.

## A test, ready to register (not run)

- **Instrumentation:** extend legality_scan's Chase Order counter. At each choice, record:
  - the turn and the points;
  - each benched Pokémon's HP left, damage and Energy;
  - what was chosen;
  - the opponent's Cyrus copies not yet used.
  
  Per game, also record each opponent Cyrus play, its target, and whether the target was knocked out.
- **Gate:** kp3 and kq3 must still replay their 3,500 table games move for move.
- **Rule for an expert-consistent choice** (first that applies):
  - **R1:** if a damaged Shuckle ex can be discarded, discard it.
  - **R2:** otherwise, against a status deck, with Ogerpon and another option on the Bench, keep Ogerpon.
  - Choices where the attack wins the game are excluded.
- **Report:** rates per bot with game-resampled ranges. Fewer than 100 scored choices reads "too few".
- **What it can show:** misplay, not its cost in win rate. Measuring the cost needs a forced-choice run.
- **What it would motivate:** two card-agnostic evaluator features, each registered before its table and read on scoreboard v2 by the adoption rule:
  - gust risk in the clock, where the attacker picks a damaged benched victim when the opponent can gust;
  - the value of status protection against the Special Conditions the opponent can inflict.
  
  Both touch every deck, not only Vespiquen.

## Files

- The two workflow runs (first audit with 16 agents; second-round verification with 13) are in this session's transcript directory. This README carries their surviving claims and file:line evidence.
- The recount script is in the scratchpad (not in the repo); it reproduces the cloud's `tally_chase_order.py` numbers.
