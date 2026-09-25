# Discard-attack census: does k3 decline Energy-discard attacks elsewhere? (Sept 25)

**Short answer: only Hyper Ray, the attack that discards all of a three-Energy cost.**
- k3 plays the two attacks that discard one Energy of two almost every time they are offered without a knockout: Mega Burning 92%, Terminating Tail 95%.
- Diving Icicles almost never comes up without a knockout (7 turns, all spent on Icicle instead), so it can't be read here.

The reading was written into `census.py` before any census game was played (file saved 05:46:51, first game 05:50:16). It is descriptive, with no threshold.

**Games:**
- k3 v k3 on 200 deals in each of the seven pairings of Blaziken, Hydreigon, Sceptile and Suicune.
- Seeds: 21,020,000,000 + pairing × 100,000 + i.
- The verified 0.7.2 add-on. 5,600 of 5,600 games replayed exactly against the engine's own loop.

| attack (deck) | Energy discarded | used when it knocks out | used without a knockout |
|---|---|---|---|
| Mega Burning (Blaziken) | 1 [R] of [RR] | 1,127 / 1,130 (100%) | 837 / 909 (**92%**) |
| Terminating Tail (Sceptile) | 1 [G] of [GG] | 609 / 610 (100%) | 283 / 297 (**95%**) |
| Hyper Ray (Hydreigon) | all, of [DDD] | 1,084 / 1,113 (97%) | 138 / 718 (**19%**) |
| Diving Icicles (Suicune's Chien-Pao ex) | all [W], of [WWW] | 151 / 160 (94%) | 0 of 7 (all 7 spent on Icicle) |

**Hyper Ray without a knockout, by opponent:**
- Altaria 4%, Blaziken 2%, Lucario 3%, Sceptile 2%, Vespiquen 10%, Suicune 34%, Weezing 31%.
- The Hydreigon run's own deals gave 3% against Lucario.
- Against Vespiquen, 24 turns counted as "would knock out" were passed. The count takes the printed 130 against HP left and ignores Shuckle ex's −20 (as the file header says), so some of those were not knockouts.

**What it means:**
- **The pattern fits a readiness cost that grows with what the attack throws away.** Losing one Energy of two (−250 in k's Active online term) is outweighed by 120–130 damage; losing all three (−500) is not. This fits the code, but it was not traced decision by decision; the clock's missing-Energy turns may add to it.
- **So a projected-readiness term would, on this table, mainly change Hydreigon,** plus Chien-Pao if the no-knockout case ever arises.
  - Hydreigon's deck average is already above Limitless under kp3 (47.4 against 42.5), so that term would very likely trip the deck veto.
  - Under the reading set with Fable, that points at the opponents' blind spots against Hydreigon, not at reverting a fix that is right by the rules.
- **Of Dustin's 15 decks, only 06 (Mega Blaziken) has an Energy-discard attack, and k3 already plays it.** So the term would change little for his current brews.
- **This is why kd goes first, and "kpr" (projected readiness) second:**
  - kd = kp plus the defender's Weakness and damage reductions in the clock, and it touches every deck.
  - kpr's registration should carry this list of where it bites.
