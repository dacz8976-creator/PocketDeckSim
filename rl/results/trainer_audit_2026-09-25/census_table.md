| card | kind | what kp3's score reads | lands after its own turn | meta decks where it was playable | fix sketch |
|---|---|---|---|---|---|
| Heavy Helmet | Tool | not read | yes | - | price persistent_defender_damage (kd's path) for the holder in the clock, and give no Tool bonus when the holder's condition fails |
| Lucky Egg | Tool | not read | yes | - | credit (5 - hand size) cards x the hand weight when the holder is the clock's next KO victim |
| Metal Core Barrier | Tool | not read | yes | - | price one-turn damage reductions (this Tool, or turn effects like Jasmine) on the clock's first hit against the holder |
| Poison Barb | Tool | not read | yes | - | credit the expected Poison damage to the attacker (per checkup until it leaves) in the own-side KO clock while the holder is Active |
| Rocky Helmet | Tool | not read | yes | blaziken | credit the counterattack damage (get_counterattack_damage) against the opponent threat's HP in the own-side KO clock while the holder is Active |
| Deceptive Needle | Tool | partly read | yes | hydreigon, weezing | credit the per-turn chip damage in the own-side KO clock while a qualifying holder is Active, so the repeat hits count |
| Elegant Cape | Tool | partly read | yes | - | price the Tool only through what it changes for this holder: 0 on a Basic unless an evolution is available, then discounted the way evolution_potential discounts it |
| Inflatable Boat | Tool | partly read | yes | suicune | no flat bonus; keep the retreat-cost term |
| Small Balloon | Tool | partly read | yes | altaria | no flat bonus; the existing retreat-cost term already prices the eligible case (optionally weighted by the chance of a retreat) |
| Steel Apron | Tool | partly read | yes | - | persistent_defender_damage in the clock (it already covers Steel Apron for kd), with no Tool bonus off a [M] holder |
| Giant Cape | Tool | read | no | suicune | none needed for its own effect; only the flat +10 on top is spurious |
| Leaf Cape | Tool | read | no | sceptile, vespiquen | none needed for the HP; drop or gate the flat +10 so an ineligible holder scores 0 |
| Protective Poncho | Tool | read wrongly | yes | lucario | drop the flat +10; price Bench damage prevention against the opponent's Bench-hitting attacks and Abilities (0 while Active) |
| Cheren | Supporter | not read | yes | - | The clock should price the threat's first attack through live defender TurnEffects (ReducedDamageForTarget covering the opponent's next turn), the same way kd prices tools and abilities. |
| Jasmine | Supporter | not read | yes | - | Same as Cheren: price live defender TurnEffects into the threat's first attack in the clock. |
| Team Rocket's Boss | Supporter | not read | no | suicune | Give Unknown opponent-hand cards an expected identity from public information (or a list sample, as the b tier does) so hand-reading effects can find likely Basics. |
| Clemont | Supporter | read (the search plays it out) | no | - | none needed |
| Copycat | Supporter | read (the search plays it out) | no | altaria, blaziken, hydreigon, lucario, sceptile, suicune, vespiquen, weezing | none needed (optionally average the redraw over several deck samples) |
| Cynthia | Supporter | read (the search plays it out) | no | - | none needed |
| Cyrus | Supporter | read (the search plays it out) | no | blaziken, hydreigon, lucario, sceptile, vespiquen, weezing | none needed (optionally read the opposing Active's retreat cost) |
| Gladion | Supporter | read (the search plays it out) | no | - | none needed |
| Iris | Supporter | read (the search plays it out) | no | - | none needed |
| Korrina | Supporter | read (the search plays it out) | no | lucario | none needed |
| Lisia | Supporter | read (the search plays it out) | no | - | none needed |
| Professor's Research | Supporter | read (the search plays it out) | no | altaria, blaziken, hydreigon, lucario, sceptile, suicune, vespiquen, weezing | none needed (optionally average draws over several deck samples) |
| Psychic | Supporter | read (the search plays it out) | no | - | none needed |
| Red | Supporter | read (the search plays it out) | no | - | none needed |
| Sabrina | Supporter | read (the search plays it out) | no | altaria, hydreigon, sceptile, vespiquen | none needed (optionally read the opposing Active's retreat cost) |
| Sightseer | Supporter | read (the search plays it out) | no | - | none needed |
| Team Rocket's Researcher | Supporter | read (the search plays it out) | no | - | none needed |
| Will | Supporter | read (the search plays it out) | no | - | none needed |
| Guzma | Supporter | partly read | yes | - | Replace the flat Active-Tool bonus with per-Tool pricing of what each Tool does to the clock (HP, damage cut, retreat) on any slot. This is the same fix the Tool rows need. |
| Ilima | Supporter | partly read | yes | - | Price a returned Pokemon at its replay value, and add a points-at-risk term for the knockout it denies. |
| Mars | Supporter | partly read | yes | weezing | Either accept the hand-count proxy, or add a term for the opponent's resources on their next turn. |
| Pokémon Center Lady | Supporter | partly read | yes | lucario, suicune | Add a status term for each side's Active: checkup damage per turn, and a missed attack for Paralyzed, Asleep or Confused. |
| Team Rocket's Master Plan | Supporter | partly read | yes | - | Add a status term to the clock (a Confused threat's next attack fails 50% of the time), and have the estimator price ExtraDamageIfDefenderStatus against the defender's current condition. |
| Erika | Supporter | read | no | sceptile | none needed |
| Irida | Supporter | read | no | - | none needed |
| Lillie | Supporter | read | no | - | none needed |
| Wally | Supporter | read | no | - | none needed |
| Clemont's Backpack | Item | read (the search plays it out) | no | - | none needed |
| Poké Ball | Item | read (the search plays it out) | no | altaria, blaziken, hydreigon, lucario, suicune, weezing | none needed |
| X Speed | Item | read (the search plays it out) | no | lucario, vespiquen, weezing | none needed |
| Field Blower | Item | partly read | yes | altaria, blaziken, lucario, suicune, vespiquen, weezing | Replace the flat 10 for any Tool on the Active with each Tool's effect priced where it acts: HP, damage reduction through the existing persistent_defender_damage, and retreat cost for both sides. |
| Pokémon Flute | Item | partly read | yes | - | Have the attacker's clock pick the cheapest prize it can reach (lowest HP per point), not the tankiest benched Pokémon. |
| Repel | Item | partly read | yes | - | In the threat clock, charge a benched threat its Active's retreat cost (or a turn) before it can attack. |
| Team Rocket's Goo-zooka | Item | partly read | yes | - | Score the opponent's Active retreat cost, which is already computed, or search one public opponent reply. |
| Flame Patch | Item | read | no | blaziken | none needed |
| Lucky Ice Pop | Item | read | no | hydreigon | none needed |
| Quick-Grow Extract | Item | read | no | sceptile | none needed |
| Rare Candy | Item | read | no | blaziken, hydreigon, suicune | Scoring: none needed. Rules: skip the Active as a Rare Candy target while has_opponent_aerodactyl_ex_primeval_law holds, in both can_play_rare_candy and rare_candy_effect. |
| Arcade | Stadium | partly read | yes | - | Price an in-play Stadium's once-a-turn effect as expected value per future turn, for both players. |
| Arena of Antiquity | Stadium | partly read | yes | lucario | Add Stadium and board damage modifiers to the clock's damage estimate, for both sides. |
| Fragrant Forest | Stadium | partly read | yes | sceptile, vespiquen | Same as Arcade: expected value per future turn for both players. |
| Hiking Trail | Stadium | partly read | yes | blaziken | Apply both players' end-of-turn Stadium effects at the leaf, or price the refill for both sides per turn. |
| Mesagoza | Stadium | partly read | yes | - | Same as Arcade: expected value per future turn for both players. |
| Peculiar Plaza | Stadium | partly read | yes | - | Score the opponent's Active retreat cost too. |
| Rainbow Cave | Stadium | partly read | yes | - | Price how well the Energy Zone's current type fits, discard Energy that the bot's own recyclers (Items included) can reach, and the Stadium's per-turn option. |
| Soothing Shore | Stadium | partly read | yes | suicune | Apply end-of-turn Stadium effects for both players at the leaf, or price them per turn. |
| Training Area | Stadium | partly read | yes | altaria | Same as Arena of Antiquity: add Stadium damage modifiers to the clock's damage estimate, for both sides. |
| Starting Plains | Stadium | read | no | - | none needed |
