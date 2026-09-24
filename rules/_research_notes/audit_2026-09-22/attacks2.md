# attacks2 — Attack effects group 2 (187 texts, ~80 Mechanic variants)

Method: grouped by `Mechanic` variant per the assignment; read each variant's handler once in
`src/actions/apply_attack_action.rs` (dispatch table + implementation function), plus
`src/move_generation/attacks.rs` for the two "usable only if" gates, then checked every text/card
list in the group against it. All confidence VERIFIED-READ unless noted.

## Findings

### F1 [Medium] `SelfDiscardRandomEnergyAndCardEffect` discards a random Energy where the card text names no type and never says "random"  (VERIFIED-READ)
- Card/rule: B3a 054 Gouging Fire — Scorching Interruption `['Fire','Lightning','Colorless']` 100 (A181)
- Text: "Discard 2 Energy from this Pokémon. During your opponent's next turn, this Pokémon takes -30 damage from attacks." — no "random", no `[X]` type.
- Engine: `src/actions/attacks/mechanic.rs` ~258, doc comment on the variant itself: "discard `count` (**untyped, so randomly chosen**) Energy from the attacker" — an assumption, not a sourced rule. `apply_attack_action.rs:3699` `self_discard_random_energy_and_card_effect` picks the discard via `random_active_energy_multisets` (probability-weighted branches), never offering the player a choice.
- Contrast: the project's own texts distinguish this elsewhere — "Discard 2 **random** Energy from this Pokémon." (A179) and "Discard a **random** Energy from this Pokémon." (A180) explicitly say "random" and are mapped to the same style of random-discard code; A181 has neither "random" nor a type letter, yet gets the same random treatment. `rules/04_actions_cards_effects.md` §Energy (retreat-cost discard, a different action but the only sourced statement on this pattern): "The player also picks *which* Energy when there is a choice (the game opens a 'Discard' Energy picker)." — the general Pocket UI default for discarding your own mixed Energy is a player-chosen picker, not a random pick, absent the word "random" on the card.
- Example: Gouging Fire's attack costs `[Fire, Lightning, Colorless]`, so using it guarantees at least one of each type attached — discarding 2 of those 3 is a real, meaningful choice every single use (e.g. keep the Fire to re-attack next turn vs. keep the Lightning). The engine instead spreads probability across the discard combinations, so a search bot/AI cannot express "keep the Lightning" at all, and a real game (which very likely lets the player pick) would let them.
- Impact: every use of Gouging Fire's Scorching Interruption (only card using this Mechanic in the whole database, per `effect_mechanic_map.rs`). `SelfDiscardRandomEnergyAndBenchDamage` (Walking Wake's Sweeping Billow, not in this batch's assignment but sharing the exact same "untyped, so randomly chosen" comment/pattern) likely has the identical issue and is worth a quick look by whoever owns that Mechanic.

## Rules questions (real rule unknown or ambiguous)

- **A137 `HalveOpponentActiveRemainingHp` (Bidoof — Super Fang).** Text: "Halve your opponent's Active Pokémon's remaining HP, rounded down." Engine (`apply_attack_action.rs:5992`) computes `remaining_hp / 2 / 10 * 10` — i.e. rounds down to the nearest **10**, not just to the nearest whole number (130 HP → 65 → 60, not 65). The code's own comment argues this must be right because Pocket damage counters only come in 10s and cites the physical card's "rounded up to the nearest 10" wording, but nothing in the rules folder confirms Pocket's own text implies the extra /10 rounding rather than a literal "rounded down" to 65. Low impact (only matters when remaining HP isn't a multiple of 20); flagging for someone to confirm against an in-game example rather than treating as settled.
- **A28 `CoinFlipSetOpponentActiveRemainingHp` (Xatu — Life Drain, P1-dustin).** Engine clamps so the effect can only *lower* remaining HP (`target.get_remaining_hp().min(remaining_hp)`), reasoning in a comment that it "must not act as a backdoor heal." Text is "your opponent's Active Pokémon's remaining HP is now 10" with no heal-guard language; unclear whether Pocket's actual ruling sets the HP unconditionally (which could raise it back up from e.g. 5) or only ever lowers it. Low impact — only matters if the target's remaining HP was already below the stated value, a narrow case — but it's the one P1-dustin item in this batch with an unverified interpretive call, so noting it explicitly.

## Checked and OK

- **AlsoChoiceBenchDamage** (A1–A7, opponent/own bench, 10/20/30/50 dmg): `also_choice_bench_damage` offers every eligible Bench Pokémon as a player-chosen `SimpleAction`, bundles it with the Active-target damage in one outcome (so it still fires after lethal damage to the Active), falls back to Active-only damage when the Bench is empty, and never applies Weakness to the bench target (`target_idx != 0`). All 7 texts' `opponent`/`damage` params match the printed text.
- **AlternativeCostIfDeckEmpty** (A8): gated at move-gen (`move_generation/attacks.rs:138`) on `deck.cards.is_empty()`; cost `[Water]` matches Veluza's text.
- **AttachRandomBasicEnergyFromZoneToBench** (A9): energy type uniform-random over the 8 basics (matches "random"), Bench target is a player choice; falls back to damage-only with an empty Bench.
- **ChanceStatusAttack** (A10–A14): `damage_chance_status_attack` applies `heads_conditions`/`tails_conditions` on the respective coin branch; all 5 texts' condition lists match (Paralyzed-only, Confused-only, Paralyzed/Confused split, Poisoned+Paralyzed, Burned-only).
- **ChargeYourTypeAnyWay** (A15): player chooses the distribution among own [P] Pokémon (`energy_any_way_choices`); no-op if none in play.
- **ChooseStatusToInflict** (A16): genuine player choice via `move_generation_stack` (`ApplyStatusToOpponentActive` per option) — matches "Choose either…".
- **CoinFlipDamageOrHealOpponent** (A17): heads = damage only, tails = heal opponent's Active only (no damage that branch) — matches text exactly, including the odd "heal the opponent" effect.
- **CoinFlipDiscardEnergyFromOpponentActive** (A18): heads → random discard of 1 from opponent's Active (matches "a random Energy"), handles 0-energy/prevented targets.
- **CoinFlipExtraDamage** (A19–A25, +20/30/40/50/60/70/80): plain binary-coin add-on, all extra_damage values match text.
- **CoinFlipNoEffect** (A26 num_coins 1, A27 num_coins 2): only the all-tails branch zeroes damage; any single head still deals full printed damage, matching "does nothing" (not scaled) wording for both.
- **CoinFlipSetOpponentActiveRemainingHp** (A28): see Rules questions.
- **CoinFlipTailsSelfDiscardRandomEnergy** (A29, count 2): heads = damage only, tails = damage + random discard of 2 — matches Entei's text.
- **CoinFlipToBlockAttackNextTurn** (A30): sets `CardEffect::CoinFlipToBlockAttack` duration 1 on opponent's Active; consumed as a 50%-block gate on *that Pokémon's own next attack attempt* (`apply_attack_action.rs` ~108–130) — matches "your opponent flips a coin, if tails that attack doesn't happen."
- **DamageAndDiscardOpponentDeck** (A31 count 1, A32 count 3): mills opponent's deck top N, stops early if the deck runs out — no crash, matches.
- **DamageEqualToSelfRemainingHp** (A33): damage = attacker's own remaining HP, matches Ogerpon's text.
- **DamagePerAttackUsedThisGame** (A34): counts uses of the named prior attack ("Sweets Relay") this game across the player's Pokémon, ×40 — matches Alcremie's text.
- **DamageUnaffectedByOpponentActiveEffects** (A35): resolved via exact-string match on the attack's own effect text in `hooks/core.rs` (`DAMAGE_UNAFFECTED_BY_OPPONENT_ACTIVE_EFFECTS_EFFECT`), which is character-for-character A35's text; the Mechanic dispatch itself is a plain pass-through by design.
- **DevolveOpponentActive** (A36): checked `cards_behind` non-empty (i.e. evolved) and not KO'd; puts current (highest-stage) card into opponent's hand, restores the prior stage with damage/energy/tools carried over — matches text.
- **DirectDamage** (A37–A48, 10/20/30/40/50/60/70/80 dmg, bench_only true/false): all values/flags match; target chosen by player among eligible slots (Active excluded when `bench_only`); Weakness gated correctly by target index (only applies if the chosen target is the opponent's Active); fizzles safely (0 damage — matches the printed 0 base damage on every one of these attacks) when no eligible targets exist.
- **DirectDamageIfDamaged** (A49 dmg 100, A50 dmg 60): filters to `is_damaged()` targets only; fizzles safely with no damaged target.
- **DisableRandomOpponentActiveAttack** (A51, duration 1): "chosen at random" implemented as a uniform pick over the defender's attack titles; duration 1 turn matches "during your opponent's next turn."
- **DiscardOpponentActiveToolsBeforeDamage** (A52, A53): discard resolved *before* damage is computed (`effect_then_damage`), so damage-reducing Tools are already gone — matches the "before doing damage" clause on A52; A53 has 0 base damage so order is moot.
- **DiscardSelfEnergyPerHeadsExtraDamage** (A54, 3 coins, [R], +30/discarded): discard count capped by actually-available [R] Energy, damage scales only with what was actually discarded — matches "for each Energy you discarded in this way."
- **DiscardTopDeck** (A55 own 3/opp 0, A56 own 5/opp 5): straightforward, stops early on an empty deck.
- **DiscardTopSelfDeckExtraDamageIfType** (A57, Fighting, +60): top card checked before it's discarded (deck order fixed at forecast) — matches Dugtrio's text.
- **DiscardTypeEnergyFromOpponentActive** (A58 Lightning, A59 Fire): discards one of the named type if present, no-op otherwise.
- **DrawUntilHandMatchesOpponent** (A60): draws `opponent_hand − own_hand` (floored at 0, so never discards) — matches Aipom's text.
- **ExtraDamageEqualToSelfDamage** (A61): adds attacker's own damage counters as bonus — matches all 5 printings' text.
- **ExtraDamageForEachHeads** (A62–A84, 23 texts, 2–9 coins, 10–100 dmg/head, include_fixed_damage true/false): plain binomial-by-heads scaling; every (num_coins, damage_per_head, include_fixed_damage) triple matches its text's flip count and "damage for each heads" vs. "more damage for each heads" wording.
- **ExtraDamageForEachHeadsWithStatus** (A85–A88): status only applied at/above `min_heads_for_status` (2, 1, 0-self, 0-opponent respectively) — all 4 match their "if at least N are heads" / unconditional wording.
- **ExtraDamageIfDefenderStatus** (A89–A96, Poisoned/Confused/Burned/Asleep, +40–70): reads the opponent Active's *current* status before this attack's own damage — all 8 status/extra_damage pairs match.
- **ExtraDamageIfEqualEnergyToDefender** (A97, +40): compares own vs. opponent Active effective Energy counts — matches.
- **ExtraDamageIfEx** (A98–A102, +30/40/70/80/90): checks `is_ex()` on opponent's Active — matches.
- **ExtraDamageIfFewerPokemonInPlay** (A103, +80): strict own-count < opponent-count over all in-play — matches.
- **ExtraDamageIfHandSizeIn** (A104–A106, {1,3,5}/{2,4,6} own or opponent): matches.
- **ExtraDamageIfOpponentHasTypeInPlay** (A107, Psychic, +50): checks any opponent in-play (Active+Bench) of that type — matches.
- **ExtraDamageIfSelfHasTypeEnergy** (A108–A111, Water/Psychic/Fighting/Psychic, +40/50/60/40): checks attacker's own attached Energy — matches, including the combined text on A111 (Mega Medicham ex, which also carries the DamageUnaffectedByOpponentActiveEffects clause, itself confirmed above).
- **ExtraDamageIfSelfHpAtMost** (A112 ≤110 +80, A113 ≤30 +60): `<=` threshold — matches "or less."
- **ExtraDamageIfSharedEnergyType** (A114, A115, min_each 1, +60/+30): both own and opponent's Active need ≥1 of a common type — matches "1 or more of the same type."
- **ExtraDamageIfSupportPlayedThisTurn** (A116 +50, A117 +60): reads `state.has_played_support` — matches "played a Supporter card from your hand during this turn."
- **ExtraDamageIfTypeEnergyInPlay** (A118 Psychic ≥5 +60, A119 Lightning ≥4 +70): sums the type across all own in-play Pokémon (not just Active) — matches "in play."
- **ExtraDamageIfUndamaged** (A120 +40, A121 +30): bonus only when attacker has zero damage counters — matches.
- **ExtraDamagePerEnergyType** (A122, +20/distinct type): counts distinct Energy *types* (not count) on the attacker — matches "for each type of Energy."
- **ExtraDamagePerOpponentPokemonWithAbility** (A123, +40): counts opponent in-play (Active+Bench) Pokémon with an Ability — matches.
- **ExtraDamagePerRetreatCost** (A124 +30, A125 +40, A126 +10): reads opponent Active's actual (possibly modified) retreat cost length — matches all 3.
- **ExtraDamagePerSpecificEnergy** (A127 Water +10, A128 Lightning +20, A129 Grass +20, A130 Metal +20, A131 Metal +10): counts that type on the attacker's own attached Energy — matches all 5.
- **ExtraDamagePerTrainerInOpponentDeck** (A132, +20/trainer): counts Trainer cards remaining in the opponent's deck server-side (a legitimate hidden-zone count effect, not a leak of specific cards to the opposing player) — matches.
- **FlipCoinsRemoveOpponentActive** (A133 KO on 2/2 heads, A134 discard on 1/1 heads, A135 discard on 2/2 heads): "Knocked Out" branch sets remaining HP to 0 and lets the shared KO pass award the point/promote; "discard" branch removes the Pokémon with no point and no promotion scoring — correctly distinguishes the two wordings; any non-all-heads result only deals the (0) base damage.
- **FlipCoinsSelfChargeActivePerHeads** (A136, 3 coins, Fire): attaches one Fire per head, stopping early only if the Active itself gets KO'd mid-loop — matches.
- **HalveOpponentActiveRemainingHp** (A137): see Rules questions.
- **HealAllYourPokemon** (A138 +20, A139 +10, A140 +30): heals every own in-play Pokémon by the flat amount — matches.
- **HealOneYourPokemon** (A141 +20, A142 +30): offers a choice among own damaged Pokémon only (healing an undamaged one is a no-op anyway) — matches.
- **InflictStatusIfStadiumInPlay** (A143 Burned, A144 Asleep): checks `state.active_stadium.is_some()` at resolution time, unconditional status if true — matches both.
- **MayShuffleSelfIntoDeck** (A145): offers both the shuffle and a no-op choice — matches "you may."
- **MegaAmpharosExLightningLancer** (A146): base 100 + 3 independent at-random Bench picks (with-replacement, so repeats stack) at 20 each, all hardcoded in the single-purpose handler rather than parameterized — verified this Mechanic has exactly one user in the whole database (the 4 Mega Ampharos ex Lightning Lancer printings, all with matching numbers), so the hardcoding isn't a live bug; falls back to Active-only damage with an empty Bench.
- **MoveFixedEnergyTypeToBench** (A147, Darkness, amount 2): moves exactly 2 Darkness to a player-chosen Bench Pokémon, no-op (damage only) if fewer than 2 are attached or Bench is empty — the attack's own cost (2 Darkness) guarantees the amount is available in practice.
- **MoveRandomEnergyToBench** (A148, count 2): the 2 moved Energy are chosen at random (matches "2 random Energy"), Bench target is a player choice.
- **OptionalDiscardBenchedBasicForExtraDamage** (A149, Grass, +70): offers "don't discard" alongside one choice per eligible Benched Basic [G] Pokémon — matches "you may… if you do."
- **RandomDamageToOpponentPokemonPerSelfEnergy** (A150, Metal, 40/hit): independent at-random picks among all opponent in-play Pokémon, one per Metal Energy attached, repeats stack — matches "chosen at random… for each time chosen;" 0 Metal Energy → 0 damage (Gholdengo's own base damage is 0).
- **RandomStatusFromEligible** (A151): uniform random among the 5 listed conditions, excluding ones already active on the opponent's Active — matches, including the "will not be chosen" exclusion.
- **RequiresBenchedNamesSelfDiscardAllEnergy** (A152): gated at move-gen on both named Pokémon being present on the Bench; resolution discards all of the attacker's Energy — matches.
- **RevealOpponentHand** (A153): resolves as plain damage with no state mutation — reasonable, since this solitary-simulator engine already has full information internally and there's no hidden-info-driven decision logic for it to affect.
- **RevealTopDeckDamagePerPokemonName** (A154, reveal 6, "Team Rocket", 30/match): counts matches in the deterministic top-N deck prefix, deals damage, then shuffles the revealed cards back — matches order and numbers.
- **SearchRandomPokemonToHand** (A155): uniform random over eligible deck Pokémon — matches "a random Pokémon."
- **SearchRandomTrainerTypeFromDiscardToHand** (A156, Item): uniform random over Item cards in the discard pile — matches "a random Item card."
- **SearchToBenchByName** (A157–A161, Nidoran♂/Koffing/Weedle/Poliwag/Starly, count 1 each): random pick among matches, Bench-space-limited — matches "1 random."
- **SearchToBenchByNames** (A162 Tandemaus/Maushold count 3, A163 Wishiwashi/Wishiwashi ex count 1, A164 Silcoon/Cascoon count 3): random unordered combinations, clamped to available cards and open Bench slots — matches.
- **SearchToHandSupporterCard** (A165): uniform random over deck Supporters — matches.
- **SelfChargeActive** (A166–A175, 10 texts, 1–3 Energy of a given type or mixed): deterministic attach of the exact listed Energy list to the Active from the Zone (not the once-per-turn manual attachment) — matches every combination including the mixed Water+Lightning (A167) and the 3×Fire multi-attach (A166).
- **SelfDiscardAllEnergyAndDelayedSpotKnockOut** (A176): discards 100% of attached Energy, then offers a player choice of spot (opponent Active or any Bench slot) for the delayed KO — matches "choose a spot."
- **SelfDiscardAllTypeEnergy** (A177, Fire): discards every Fire Energy on the attacker — matches.
- **SelfDiscardAllTypesEnergyDamagePerDiscarded** (A178, Fire+Lightning, 50/discarded): damage computed from the actual pre-discard count of matching Energy, same set is what gets discarded — matches.
- **SelfDiscardRandomEnergy** (A179 count 2, A180 count 1): both texts explicitly say "random" and are implemented as random — correct (contrast with F1).
- **SelfDiscardRandomEnergyAndCardEffect** (A181): see Finding F1.
- **SelfDiscardTypedEnergyAndDamageAllOpponent** (A182, Water count 3, 50 dmg): damages the opponent's Active *and every Bench slot* ("each of your opponent's Pokémon"), discards up to 3 Water Energy (capped safely, though the attack's own 4-Water cost guarantees enough) — matches.
- **SelfHealIfDefenderHasStatus** (A183, Poisoned, +60 heal): checks opponent Active's current status, heals the attacker if true — matches.
- **SwitchSelfWithBench** (A184): mandatory (no "you may" in text, `optional: false`), player-chosen Bench target, skipped if the attacker was KO'd by counter-damage first, no-op with an empty Bench — matches.
- **SwitchSelfWithBenchOfType** (A185, Lightning): same as above but filtered to Benched Lightning Pokémon — matches.
- **TieredCoinFlipDamage** (A186, 3 coins, tiers 0/20/50/120): exclusive per-heads-count bonus (not cumulative) — matches "if 1…, if 2…, if all…" phrasing.
- **VaporeonHyperWhirlpool** (A187): unbounded "flip until tails," each head discards one random Energy from the opponent's Active, saturated at the opponent's actual attached-Energy count so extra heads past that point change nothing — matches "flip until tails" being unbounded and the Pocket rule that it's not capped at a fixed number of coins.

Everything in the already-known-bugs list (damage order, status stacking, etc.) that also touches this batch's mechanics (e.g. status-inflicting variants, Bench-damage weakness) was left un-repeated per the brief.
