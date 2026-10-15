# Bounded independent rules check

Reviewer: astra_rules_check. Model/effort: gpt-6-astra/high. Date: 2026-10-01.

Scope: independent examination of three consequential inferences using existing evidence. This is not a second full-video review. Both REVIEW.md files were read for sequence context; both SOURCE.json files were read for source binding. No original was decoded, rehydrated, moved, or independently rehashed. Existing reviews and history remain intact. No simulator, shared register, or Ladder Log was changed.

## Source binding and exact inspection

- `20261001_203626000_iOS.MP4`: SOURCE.json SHA-256 `4e6dd60d8827f7818f028cb29757200061ab9ace7dde2e772a5358d7a0c0c6fa`, 675738932 bytes, 365.95 seconds. Packet: `Recording_QA/20261001_203626000_iOS_rule_sol`.
- `20261001_210403000_iOS.MP4`: SOURCE.json SHA-256 `57dd0af85e1ae6c148dea79e6dcab38cdfdede707f15d25d468b821a1d55c993`, 862523863 bytes, 465.875488 seconds. Packet: `Recording_QA/20261001_210403000_iOS_rule_sol`.

Images opened and semantically inspected:

- 203626: `LEAD_CHECK_2.jpg`; native `evidence/t0210.00.jpg`, `t0340.50.jpg`, `t0346.50.jpg`, `t0347.00.jpg`.
- 210403: `LEAD_CHECK_1.jpg`, `LEAD_CHECK_2.jpg`; native `native/t0102.00.jpg`, `t0385.00.jpg`, `t0386.00.jpg`, `t0388.00.jpg`, `t0389.00.jpg`, `t0404.00.jpg`.

The useful composite panels include 203626 at 327/332/336.30/338/343/345.50 seconds, 210403 at 376/378/380/386/387/389 seconds, and 210403 at 404/406/412/420/424/426/447 seconds. Native files above were opened separately where coin order or printed text was consequential. Other panels visible in those composites were not treated as a new full-battle acceptance.

## 1. Will and Victory Star replacement: supported, with narrower wording

Will is played and its effect confirmed at 327/332. The original Double Smash sequence registers its first Heads at 336.30 and finishes Heads/Tails at 338. Victory Star's prompt and printed replacement text are clear at 340.50. The replacement sequence registers **0 Heads/1 Tail** at 346.50 before finishing **Tails/Heads** at 347. These intermediate counters establish first-coin order; a final one-head total alone would not.

Supported wording: **After Will's original eligible attack coin sequence, the first Victory Star replacement coin was not guaranteed Heads in this test.** Original HT becoming replacement TH also supports replacing both results rather than retaining the original guaranteed Heads.

The existing review's phrase that the guarantee was "consumed" is a reasonable behavioral shorthand, but the footage cannot reveal an internal flag or implementation. Use "not reapplied to this replacement sequence" for the directly observed conclusion. This does not establish every other reroll mechanism, later eligible effect, probability distribution, or interaction with a non-Fire attacker. No factual reversal of the accepted review is required.

## 2. Will and Confusion: supported; no Victory Star after this failure

The actual Will play and effect confirmation at 376/378 precede the attack menu at 380. At 385/386 the game explicitly labels the coin as a Confusion check and resolves Tails. The attack does nothing at 387/388, then the opponent's turn begins at 389. Moltres remains at 110 HP with seven Fire Energy; Bronzong remains at 120 HP. Two Victini are visibly present. This directly contradicts a rule that Will always forces this separate condition check to Heads.

Supported wording: **Will did not force the separate Confusion check to Heads. No Victory Star reroll was offered in the reviewed failed-check sequence, and the turn ended without resolving the attack.** The independently legible Victini text at 102 limits its trigger to coins for an attack by a Fire Pokemon, supporting the distinction between the condition check and attack-effect coins.

The native failure frames plus the reported full sequence support that bounded observation. This check does not establish a universal exclusion for every status condition or every reroll ability. It also does not determine what would happen to an unused Will guarantee in a different subsequent-effect scenario. A Confusion Heads result alone, such as the earlier turn, cannot establish that Will affected the condition coin.

## 3. Bounded Field and Guard Press damage order: discriminating evidence

At 404, Bronzong's printed Guard Press deals 60 and reduces attack damage to itself by 20 during its opponent's next turn. Its Fire Weakness is also legible. The attack resolves at 406. In the next owner turn, Double Smash's text and one-Head result at 420 establish 40 attack damage before modifiers. The game displays 60 Weakness damage at 424, and Bronzong settles from 120 HP to 60 HP at 426, with Bounded Field still in play.

This is a discriminating case: **40 x 2 - 20 = 60**, while reduction before doubling gives **(40 - 20) x 2 = 40**, and omitting reduction gives **40 x 2 = 80**. The visible 60 and settled HP support doubling before this Guard Press reduction. Netherwing's later displayed 260 at 447 supports the Stadium's doubling behavior after the reported protection interval, but is corroboration rather than the decisive ordering test.

Scope clarification from the legible Bounded Field text at 203626/210: its Mega Evolution Pokemon ex exception qualifies the **attacking Pokemon whose attack is used**, not the defending Pokemon receiving damage. Both tested attackers are outside that exception. No Mega attacker or Mega defender appears in this bounded test. Do not generalize this observation into a complete ordering rule for every damage modifier, bench damage, zero damage, or a Mega interaction.

## Disposition

All three requested findings are supported within the stated scope. The additive clarifications above sharpen "consumed" into observable non-reapplication and identify the attacker-side Mega exception. No contradiction requiring withdrawal of the prior battle acceptance was found. The original whole-video coverage, finalization, and archival remain the lead review's responsibility.

## Addendum: second Misty target in 213822

Reviewer: astra_rules_check, gpt-6-astra/high. Date: 2026-10-01. This follow-up is limited to the supplied 117-129 second sequence.

Source binding read from `Recording_QA/20261001_213822000_iOS_rule_sol/SOURCE.json`: `20261001_213822000_iOS.MP4`, SHA-256 `3017f3abbf17846d9041177e3fce268560c4ca7ed68277b2a2972b8a90f8399b`, 387819155 bytes, 217.453333 seconds. The relevant REVIEW.md passages and UNCERTAINTIES.json were read for context. No original was opened, decoded, rehydrated, or rehashed.

Exact images independently opened: `native/t0117.00.jpg`, `t0120.00.jpg`, `t0122.00.jpg`, `t0123.00.jpg`, `t0126.00.jpg`, `t0128.00.jpg`, and `t0129.00.jpg` in that packet.

**Conclusion: keep the second Misty target unknown.** At 120, the selection instruction remains visible and all three eligible Water Pokemon are outlined. Misty's card overlaps the benched Mega Gyarados ex and its area is brighter, but that single transient appearance does not securely distinguish hover/drag highlighting from a committed target. At 122 Misty's generic play animation is centered over the Active area; this also does not identify the selected Pokemon. At 123 the large Trainer animation obscures the board. The coin interface at 126/128 names no target. At 129 Mega Sharpedo ex's attack/retreat menu is open after the coin resolution, which does not retroactively establish Misty's target.

**Supported outcome:** 128 explicitly shows zero Heads and one Tail. Misty's printed instruction at 117/122 provides Energy for Heads, so this use supplies no Energy regardless of which eligible target was chosen. The pre-use board shows ordinary Gyarados with three Water, Mega Sharpedo with one, and Mega Gyarados with none; there is no resulting attachment that could disambiguate the choice. No accepted coverage, result, or zero-Energy finding needs correction. Only the exact selected target remains observationally unresolved.

## Addendum: lethal Destructive Inferno and Energy removal in 214736

Reviewer: astra_rules_check, gpt-6-astra/high. Date: 2026-10-01. This is a bounded consequential-evidence check, not completion acceptance or a duplicate full pass.

Source binding read from `Recording_QA/20261001_214736000_iOS_rule_sol/SOURCE.json`: `20261001_214736000_iOS.MP4`, SHA-256 `fed3727e102145e326fd09847e5062ae37321f45310e885333ddfb6b2cd2d02a`, 674613872 bytes, 363.465 seconds. REVIEW.md did not yet exist at the time of this check. The lead's supplied sequence context was compared with the retained evidence. No original was opened, decoded, rehydrated, or rehashed.

Exact images inspected: `LEAD_LETHAL_CHECK.jpg`, whose labeled panels are 170/177/180/182/188/188.90/189.30/194 seconds; and separately `native/t0170.00.jpg`, `t0188.90.jpg`, `t0189.30.jpg`, `t0238.00.jpg`, `t0240.00.jpg`, `t0246.00.jpg`, `t0248.00.jpg`, `t0251.00.jpg`.

**Directly supported:** Typhlosion ex's printed Destructive Inferno at 170 deals 110 and instructs a flip-until-tails sequence, discarding a random Energy from the opponent's Active Pokemon for each Heads. Gabite is visibly at 0 HP with Water and Fighting Energy still attached at 177. The original attack-effect coin sequence finishes 0 Heads/1 Tail at 180, Victory Star activates at 182, and the replacement finishes 2 Heads/1 Tail at 188. Gabite still displays both Energy at 188.90. At 189.30 the same 0-HP Gabite card remains visibly on the board, its Energy icons have disappeared, and two outbound streaks are visible. The opponent's first point is displayed at 194.

This securely establishes that **the attack-effect coin procedure and Victory Star reroll continue after lethal damage is displayed, before the knockout's point award.** It also securely establishes the visual disappearance of both Energy after the replacement result and before the Pokemon card visibly leaves the board.

**Causal attribution remains unresolved:** this sequence alone does not discriminate Destructive Inferno's actual discard operation from the Energy-removal phase of normal knockout cleanup. Two Heads with exactly two attached Energy and cleanup of those same two Energy produce the same visible final state. The fact that Energy disappears before the Pokemon card disappears is suggestive of the attack effect, but is not decisive without an independently established difference in those animations or an explicit event record attributing the discard. Treat the two streaks as observed removal animation, not proof of which rule invoked it. Random selection among Energy types is also untested because both available Energy disappear.

The Froakie control shows original 0 Heads/1 Tail at 238, Victory Star at 240, replacement 2 Heads/1 Tail at 246, a "No Energy attached" message at 248, and the opponent's second point at 251. This supports continued presentation of the secondary-effect procedure even though no Energy can be discarded. However, Froakie's Active spot is already visibly empty at 248. Do not describe that frame as proving the game checks an intact 0-HP Froakie before knockout cleanup, or use it to assign Gabite's removal to the attack. The reported later nonlethal zero-Head case was not independently inspected here; even if confirmed, zero Heads with retained Energy would not distinguish the competing explanations for the lethal two-Energy removal.

Recommended narrow wording: **"After Destructive Inferno reduced Gabite to 0 HP, its effect coins still resolved and Victory Star replaced T with HHT. Both attached Energy then disappeared before the point award. Because the reroll's two Heads match all two attached Energy, this footage does not independently distinguish effect-driven discard from knockout cleanup."**

A future positive-Heads removal from a surviving target would establish actual effect-driven discard without knockout interference, but would not by itself resolve the lethal ordering. For that lethal question, a target with more attached Energy than Heads and an independently visible partial removal before the remainder is cleaned up would be more discriminating. No further test was run or requested by this check. No shared index/events, acceptance, media location, simulator, or training data was changed.

## Addendum: Gabite's 50 damage does not test Weakness bypass

Reviewer: astra_rules_check, gpt-6-astra/high. Date: 2026-10-01. Source is the same SHA-bound 214736 packet identified above. Independently inspected only `native/t0144.00.jpg`, `t0148.00.jpg`, `t0165.00.jpg`, plus the retained Gabite evolution/version views `t0069.00.jpg` and `t0205.00.jpg`. Read the short REVIEW.md passages for printed versions, owner turn 5, and the ability/selected-target claim. The current report already contains the appropriate Dragon-type limitation.

**The observed 50 is not a discriminating Weakness-bypass test.** Gabite is the Dragon-type Linear Attack version; the Water and Fighting symbols beside the attack specify its Energy requirement, not a matching Water-type attacker. Quilava's printed Weakness is Water +20. Frame 148 shows Quilava at 80 HP, and 165 shows it at 30 HP with Gabite's Water and Fighting attached. These observations establish the 50 damage, but do not separate normal nonmatching-type damage from any proposed special rule for selected-target attack damage. The 205 view independently shows the same printed Gabite version with its type symbol unobscured by the combat HP overlay.

For primary-source context, Pokemon's official [Pocket Fighting-type Fury strategy](https://www.pokemon.com/uk/features/pokemon-tcg-pocket-strategy-fighting-type-fury) describes Pikachu ex's Weakness to Fighting-type Pokemon, and its official [Sudowoodo and Lucario strategy](https://www.pokemon.com/uk/features/pokemon-tcg-pocket-sudowoodo-and-lucario-deck-list-strategy) connects Fighting-type attackers with an opponent's Fighting-type Weakness. These support the attacker-type comparison; neither is evidence for a special Linear Attack bypass rule. No forum claims or tabletop-specific rule were used as authority.

Supported wording: **"Dragon-type Gabite's Linear Attack dealt 50 to Active Quilava, reducing it from 80 to 30 HP. This was not a matching-Weakness attack, so it does not establish that selected-target attacks ignore Weakness."** Greninja's separate Water Shuriken use is an Ability against a benched target and cannot serve as the missing matching-type Active attack comparison. Do not infer a general targeted-attack Weakness rule from either event. Only this additive clarification was written.
