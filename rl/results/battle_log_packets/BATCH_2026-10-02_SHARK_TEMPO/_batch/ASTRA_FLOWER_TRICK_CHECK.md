# Astra targeted check: Flower Trick delayed damage

Reviewed October 2, 2026. Scope: only native frames at 150, 188, 194 and 197 seconds from 20261002_143837000_iOS_shark_sol. Optional 164/166/168/170-second frames were not present in the packet when checked. No whole-battle review or external rules lookup was performed.

**Judgment:** Describe Lapras's 110-to-40 HP change as delayed Flower Trick damage. It is an effect of Meowscarada ex's earlier attack, not Surf recoil or an Ability.

## Printed text and timing

The Flower Trick text is legible in the original-resolution [150-second frame](../20261002_143837000_iOS_shark_sol/native/t0150.00.jpg):

> Choose a spot from among your opponent's Active Spot and Bench. At the end of your opponent's next turn, do 70 damage to the Pokémon in the spot you chose.

The attack selects a **spot**, with damage scheduled for the end of the defending player's next turn. In this game the defending player is the owner. Thus the relevant boundary is after the owner's intervening turn, including Surf, rather than during the Meowscarada player's later turn. The wording targets the Pokemon occupying the chosen spot when the delayed effect resolves; do not paraphrase it as permanently marking Lapras regardless of movement.

## Observations and inference

- [188 seconds](../20261002_143837000_iOS_shark_sol/native/t0188.00.jpg): Active Lapras remains at 110 HP and carries a blue star effect icon. Opposing Meowscarada ex is at 190 HP. The icon alone does not identify the exact effect.
- [194 seconds](../20261002_143837000_iOS_shark_sol/native/t0194.00.jpg): Surf's 70-damage animation is over Meowscarada ex; Lapras still displays 110 HP. Lapras's visible Surf text contains no self-damage clause.
- [197 seconds](../20261002_143837000_iOS_shark_sol/native/t0197.00.jpg): Meowscarada ex is at 120 HP and Lapras at 40 HP. These are separate 70-damage changes, consistent with Surf resolving first and the previously scheduled Flower Trick effect then resolving at the end of the owner's turn.

The printed attack timing and the before/after states strongly support this interpretation. These sampled frames do not independently show the initial choice of Active Spot or every intervening animation, and do not establish an exact subsecond timestamp. Attribution of the blue star icon specifically to Flower Trick is an inference supported by the matching printed timing and 70 damage.

Recommended review wording: "Lapras used Surf for 70, taking Meowscarada ex from 190 to 120 HP. At the end of the owner's turn, the earlier Flower Trick effect dealt its delayed 70 damage to the chosen Active Spot, taking Lapras from 110 to 40 HP."
