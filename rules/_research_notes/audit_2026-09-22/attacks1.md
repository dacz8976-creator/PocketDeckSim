# attacks1 — Attack effects group 1 (187 texts, A1–A187)

Scope: `/home/claude/work/assign/attacks_group1.md`. Reviewed every distinct `Mechanic` variant's handler
(mostly `src/actions/apply_attack_action.rs`, dispatch table starting ~line 341; a few in
`src/move_generation/attacks.rs`, `src/actions/apply_action.rs`, `src/actions/apply_action_helpers.rs`,
`src/card_logic/rare_candy.rs`) and checked every text against it: numbers/types/counts, whose choice it is
(player/random/opponent), conditions and timing, Pocket-specific rules, and failure cases (empty Bench, no
Energy, no target). No probes were run — all findings are code-read only (VERIFIED-READ / PROBABLE), since
none of the doubts reached a level where a probe changed the confidence materially. All work read-only;
nothing under `src/` was modified.

## Findings

### F1 [Medium] Politoed's Raid grants its bonus even when evolved via Rare Candy, not from Poliwhirl (VERIFIED-READ)
- Card/rule: B3 035 Politoed — Raid. Text (A108): "If this Pokémon evolved from Poliwhirl during this turn, this attack does 50 more damage."
- Engine: `src/actions/effect_mechanic_map.rs:3268` → `Mechanic::ExtraDamageIfEvolvedThisTurn { extra_damage: 50 }`. The variant (`src/actions/attacks/mechanic.rs:672-674`) carries no "evolved-from" name field. Handler `extra_damage_if_evolved_this_turn_attack` (`apply_attack_action.rs:4937-4952`) only reads `p.played_this_turn` — true for *any* evolution this turn, not specifically "from Poliwhirl":
  ```
  let evolved = state.in_play_pokemon[state.current_player][0].as_ref().map(|p| p.played_this_turn)...
  ```
- Example: Politoed is Stage 2 (Poliwag→Poliwhirl→Politoed). Rare Candy legally evolves Poliwag straight to Politoed, skipping Poliwhirl (`src/card_logic/rare_candy.rs` builds an explicit Basic→Stage2 lookup for this). `apply_evolve` (`apply_action.rs:1460-1498`) sets `played_this_turn = true` and records the true lineage in `cards_behind` — data the mechanic has available but doesn't use. So a Politoed fielded by Rare Candy this turn (evolved from Poliwag, not Poliwhirl) still gets +50, which the printed text forbids.
- Impact: any Politoed (Raid) deck running Rare Candy — a normal Stage-2 pattern. Low play rate (P3) but the overstatement is deterministic (not a coin flip) whenever it happens. A107 (Jolteon, generic "evolved during this turn," no source restriction) and A109 (Weavile, Stage 1, only one possible source: Sneasel) are unaffected — see Checked and OK.

### F2 [Medium] KO-promotion counts as "moved from the Bench to the Active Spot this turn" (VERIFIED-READ)
- Cards/rule: A118 Golisopod (First Impression), A118/A120 Crobat/Basculin (Surprise Strike), A119 Scizor/Mega Scizor ex (Gale Thrust/Bullet Slugger) — "If this Pokémon moved from your Bench to the Active Spot this turn, this attack does N more damage." A163 Flutter Mane (Hexing Flight) — "If this Pokémon didn't move from the Bench to the Active Spot this turn, this attack does nothing." Rule [OFFICIAL, Scizor FAQ], `rules/04_actions_cards_effects.md` §3 and `rules/02_damage_knockouts_points.md` §7: "A Pokémon promoted after a Knock Out did **not** 'move from the Bench to the Active Spot this turn.'"
- Engine: `src/actions/apply_action.rs:773-780` routes both `SimpleAction::Activate` (a genuine switch/retreat) *and* `SimpleAction::Promote` (forced promotion after a Knock Out) through the identical `apply_retreat(*player, state, *in_play_idx, true)` call, which calls `apply_activate` (`apply_action_helpers.rs:895-904`):
  ```
  if let Some(pokemon) = state.in_play_pokemon[player][0].as_mut() {
      pokemon.moved_to_active_this_turn = true;
  }
  ```
  unconditionally, with no way to tell a KO-promotion from an actual Bench→Active move. The two mechanic handlers read exactly that flag (`extra_damage_if_moved_from_bench_attack`, `apply_attack_action.rs:4920-4935`; `no_damage_unless_moved_from_bench`, `apply_attack_action.rs:4870-4880`).
- Example: your own Active is Knocked Out mid-turn (recoil, self-damage, an Ability) before you've attacked; you promote a Benched Mega Scizor ex/Golisopod/Crobat/Basculin and attack the same turn — the engine wrongly grants the "moved from Bench" bonus, or wrongly lets Flutter Mane deal full damage, when the official ruling says that promotion doesn't count.
- Impact: Mega Scizor ex (Bullet Slugger) is an actually-played card (this batch tags it P3, but it's a real B2b ex); the rest are niche. Only the specific same-turn KO→promote→attack line triggers it, but the result is deterministic once it does. Not on the "already known" list in AGENT_BRIEF.md.

### F3 [Low/Medium] Walking Wake's unqualified "Discard an Energy" is resolved at random instead of by player choice (PROBABLE)
- Card/rule: B3a 053 Walking Wake — Sweeping Billow (A183). Text confirmed verbatim from `database.json`: "Discard an Energy from this Pokémon, and this attack also does 20 damage to each of your opponent's Benched Pokémon." — no "random" qualifier anywhere. Rule analogy [OFFICIAL/INFERRED], `rules/04_actions_cards_effects.md` §2 (retreat): "Discard 1 Energy... The discarded Energy can be of any type... The player also picks which Energy when there is a choice (the game opens a 'Discard' Energy picker)." Pocket's established convention is that an unqualified "discard an Energy" is a player choice; cards that want randomness say so explicitly (compare A94/A96/A97/A99, all of which do say "random").
- Engine: `effect_mechanic_map.rs:3388` maps this exact text to `Mechanic::SelfDiscardRandomEnergyAndBenchDamage { count: 1, bench_damage: 20 }`. The handler (`self_discard_random_energy_and_bench_damage`, `apply_attack_action.rs:3766-3793`) discards via `random_active_energy_multisets`, weighted by the attacker's current energy mix. No player-choice equivalent exists anywhere in the codebase for an unqualified "discard an Energy from this Pokémon."
- Example: Walking Wake's cost is `[Fire, Water]`; with exactly 1 Fire + 1 Water attached (the minimum to attack), the engine effectively coin-flips which type is discarded instead of letting the player pick.
- Impact: single niche card (P3), but the effect is wrong on every use of the attack, not just a rare corner.

### Number-mismatch hints checked (false positives, not bugs)
- A21 (Mega Blastoise ex, `required_extra_energy: 3`): the tool's "number seen in text vs map entry" check missed the number because it's written as three `EnergyType::Water` list entries rather than a literal digit; the field does encode 3. Checked and OK.
- A161 (Moltres ex Inferno Dance, `Mechanic::MoltresExInfernoDance` — no fields): the "3" (3 coins) is hardcoded inside `moltres_inferno_dance()` (`apply_attack_action.rs:2104`, `AttackOutcomes::binomial_by_heads(3, ...)`), correct for the one printing that uses this mechanic. Checked and OK.

## Rules questions
None beyond what the rules folder already lists as open. F3's severity rests on an analogy (retreat-cost Energy discard) rather than a direct ruling for attack-effect Energy discards; if Dustin/Astra want a firmer source before treating it as a bug, it should move here instead.

## Checked and OK
(Grouped by shared `Mechanic` variant/handler; parameters, chooser, timing and failure cases all verified to match text unless noted above.)

- A1 `AlsoBenchDamageIfDamaged`: deterministic "each…that has damage" bench hit, no Weakness issue (bench). OK.
- A2, A3 `AlsoBenchDamageIfPokemonOnBench` (Plusle/Electivire): condition on named Bench-mate checked correctly; deterministic "each" to all opposing Bench. OK.
- A4 `AlsoChoiceBenchDamageFiltered`: player picks among damaged Bench targets only; empty choice ⇒ still does the attack's own damage. OK.
- A5 `AlsoRandomBenchDamage`: uniform random pick among Bench slots (matches "chosen at random", not a player choice). OK.
- A6 `AlternativeCostIfDamaged`: move-gen (`move_generation/attacks.rs:113-143`) gates the reduced cost on `active_pokemon.is_damaged()` and still requires the reduced cost be payable. OK (PROBABLE — didn't verify the printed-cost path stays offered in parallel).
- A7 `AttachEnergyFromZoneToPokemonNamed` (Mesprit/Azelf): choices restricted to those two names on the player's own side; empty ⇒ damage only, no attach. OK.
- A8 `ChangeOpponentNextGeneratedEnergyType`: uniform random among the 8 basic types, matches "at random". OK.
- A9 `CoinFlipChargeBench`: on heads, both Fire Energy go to the *same* chosen Benched Pokémon (matches "attach it… to 1 of your Benched Pokémon"); tails/no-Bench ⇒ just damage. OK.
- A10 `CoinFlipNoDamageOrDamageAndCardEffect`: tails ⇒ 0 damage/no effect ("does nothing"); heads ⇒ damage + self `PreventAllDamageAndEffects` for 1 (opponent's next turn). OK.
- A11 `CoinFlipNoDamageOrDamageAndStatus`: tails ⇒ nothing; heads ⇒ damage + Paralyze. OK.
- A12, A13 `CoinFlipPerSpecificEnergyType` (Metal/Fire): coins = count of that Energy type on self; `include_fixed_damage` correctly distinguishes "does X for each heads" (A12) vs "does X *more* for each heads" (A13). OK.
- A14 `CoinFlipReturnOpponentActiveToHand`: heads returns card+evolution-chain to opponent's hand, discards its Energy/Tools, no points scored, triggers normal promotion. OK.
- A15–A18 `CoinFlipSelfDamage` (20/30/50/60): heads = damage only, tails = damage + self-damage, matches "if tails" wording; independent 50/50 flip. OK.
- A19 `CoinFlipSelfHeal`: damage always applied; heads additionally heals. OK.
- A20, A21 `ConditionalBenchDamage` (Blastoise/Mega Blastoise ex): extra-Energy gate via `contains_energy` on cost+required extra; num_bench_targets 1 vs 2 correctly generates single-choice vs exactly-2-distinct-target combinations; insufficient Bench ⇒ active damage only. OK.
- A22–A26 `CopyAttack` variants (Ditto/Mew ex/Mimikyu/Clefairy): source scoping (opponent active/in-play/own-Bench-non-ex/opponent hand+deck), energy-match requirement, and coin-gated vs unconditional copy all match; copied attack always resolves against the copier's own board (Energy/Bench), matching the Genome Hacking ruling. OK.
- A27, A28, A43 `DamageAndCardEffect`/`ReducedDamage` (−20/−30/−50, self, opponent's next turn): OK.
- A29 `DamageAndCardEffect`/`ReducedDamage` −30 on Defending Pokémon (checked0921 — mechanic only): OK.
- A30 `DamageAndCardEffect`/`CannotAttack` coin-gated on Defending Pokémon: heads-only application via `prevents_attack_effects` check, tails = damage only. OK.
- A31 `DamageAndCardEffect`/`ReducedDamage` −20 (self): OK.
- A32 `DamageAndCardEffect`/`NoRetreat` on Defending Pokémon: OK.
- A33 `DamageAndCardEffect`/`CannotAttack` duration 2 ("your next turn"): duration convention (1 = opponent's next turn, 2 = your next turn) consistent throughout the file. OK.
- A34 `DamageAndCardEffect`/`IncreasedVulnerability` +20 (self — Lucario's own drawback): OK.
- A35 `DamageAndCardEffect`/`CannotAttack` on Defending Pokémon (unconditional): OK.
- A36 `DamageAndCardEffect`/`PreventAllDamageAndEffects` coin-gated (self): OK.
- A37–A40, A42, A48, A58, A68, A71 `DamageAndCardEffect`/`IncreasedDamageForAttack` and `CannotUseAttack` (named-attack buffs/locks, duration 2): attack-name string matches the card's own attack; OK.
- A41, A46, A55, A60 `DamageAndCardEffect`/`Counterattack` (40/30/20/80): OK.
- A44 `DamageAndCardEffect`/`IncreasedVulnerability` +30 (self): OK.
- A45, A54, A66 `DamageAndCardEffect`/`CannotUseAttack` (Big Beat/Sacred Sword/Gigaton Hammer): OK.
- A47 `DamageAndCardEffect`/`CoinFlipToBlockAttack`, duration `UNTIL_LEAVES_ACTIVE_SPOT`: effect application matches text; per-attack coin-flip enforcement lives outside this handler (not reviewed here) — flagged only if a doubt arose, none did. OK.
- A49 `DamageAndCardEffect`/`PreventAllDamageAndEffects` coin-gated (self, "by attacks" only — narrower prevention wording than A36/A10, matches `PreventAllDamageAndEffects` reuse since the card text distinction "damage… by attacks" vs "damage from—and effects of—attacks" is a documented case where the engine doesn't carry a separate variant; not re-flagged, same class as already-known item 10's family). OK.
- A50, A65 `DamageAndCardEffect`/`IncreasedAttackCost` (+1/+2 opponent): OK.
- A51 `DamageAndCardEffect`/`DelayedDamage` 90 (Mismagius): OK.
- A52, A62 `DamageAndCardEffect`/`IncreasedDamageForAttack`, duration `UNTIL_LEAVES_ACTIVE_SPOT`, "stacks": OK.
- A53 `DamageAndCardEffect`/`PreventDamageIfLessOrEqual` 40: OK.
- A56 `DamageAndCardEffect`/`PreventDamageFromBasic`: OK.
- A57 `DamageAndCardEffect`/`AsleepIfEnergyAttached` on Defending Pokémon: OK.
- A59 `DamageAndCardEffect`/`NoWeakness` (self): OK.
- A61 `DamageAndCardEffect`/`ReducedDamage` 100 coin-gated: OK.
- A63 `DamageAndCardEffect`/`DamageNewActiveOnRetreat` 40: effect application correct; retreat-triggered payoff lives elsewhere, not reviewed. OK.
- A64 `DamageAndCardEffect`/`ReducedDamageFromEx` 80: OK.
- A67 `DamageAndCardEffect`/`NoAbilities`, `UNTIL_LEAVES_ACTIVE_SPOT`: OK.
- A69 `DamageAndCardEffect`/`IncreasedVulnerability` +50 duration 2 (opponent, "During your next turn, the Defending Pokémon..."): OK.
- A70 `DamageAndCardEffect`/`IncreasedVulnerability` +50 duration 1 (self): OK.
- A72, A74 `DamageAndMultipleCardEffects` (attack-cost + retreat-cost stacks, opponent): OK.
- A73 `DamageAndMultipleCardEffects` (`ReducedDamage`+`NoWeakness`, self): OK.
- A75 `DamageAndTurnEffect`/`NoEnergyFromZoneToActive`: OK.
- A76 `DamageAndTurnEffect`/`NoItemCards`: OK.
- A77 `DamageAndTurnEffect`/`NoSupportCards`: OK.
- A78 `DamageAndTurnEffect`/`NoTrainerCards`: OK.
- A79 `DamageAndTurnEffect`/`NoEvolutionFromHand`: OK.
- A80, A81 `DamagePerEnergyAll` (opponent side, 20/turn 20-more): sums Energy over the *whole* opposing side (Active+Bench), matches "attached to all of your opponent's Pokémon." OK.
- A82 `DamagePerOwnPokemonWithAttackName` (Puppy Pile): counts in-play + in-hand copies by exact attack name. OK.
- A83, A84 `DamagePerOwnToolAttached` (40/30 per Tool): sums Tools across the whole own side. OK.
- A85 `DamageReducedBySelfDamage`: `saturating_sub`, floors at 0. OK.
- A86 `DamageToAnyOpponentPerTargetEnergy`: per-target damage computed from *that* target's own Energy count, player picks the target. OK.
- A87, A88 `DamageUnaffectedByWeakness`: fixed damage passthrough; Weakness/step-4 skip is handled in the shared damage pipeline (hooks/core.rs), not this mechanic. OK.
- A89 `DarknessClaw` (checked0921): player chooses among revealed Supporters in opponent's hand; empty ⇒ no discard. OK.
- A90 `DelayedSpotDamage`: player chooses a spot (Active or any Bench slot) on the opponent's side; delayed via `ScheduleDelayedSpotDamage`. OK.
- A91 `DirectDamageAndSelfCardEffect`: self `CannotAttack` always applied; player picks 1 of opponent's Pokémon (Active or Bench, `bench_only:false`) for the 140. OK.
- A92 `DiscardOpponentActiveEnergyIfEvolvedThisTurn` (Dudunsparce, Stage 1, only evolves from Dunsparce — no Rare-Candy-skip ambiguity unlike F1): generic played-this-turn check is safe here. OK.
- A93 `DiscardOwnBenchedTypeForDamage`: all-subset choice (including discarding none) of own Benched Water Pokémon, matches "may discard any number." OK.
- A94 `DiscardRandomEnergyFromBothActive`: independent random discard from each side's Active, respects opponent's `prevents_attack_effects`. OK.
- A95–A97 `DiscardRandomGlobalEnergy` (1/2, own-only vs both sides): exact hypergeometric enumeration over all attached Energy in scope, respects per-Pokémon `prevents_attack_effects` on non-attacker targets. OK.
- A98–A101 `DiscardRandomOpponentHandCards` (Item/Tool/Any, coin-gated or not): uniform random among matching hand cards; correct kind filters. OK.
- A102 `DiscardTopSelfDeckExtraDamageIfTrainerType` (Item): checks the concrete top card (deck order is fixed in state at forecast time) then discards it. OK.
- A103 `EvolutionBenchCountDamage`: counts Bench Pokémon with `stage > 0` (any Evolution, not type-restricted, matches text). OK.
- A104 `ExtraDamageForEachHeadsToolBoostedCoins` (Lucky Mittens): coin count conditioned on the named Tool being attached to self. OK.
- A105 `ExtraDamageIfDefenderNameContains` ("Team Rocket"): substring match on opponent Active's name. OK.
- A106 `ExtraDamageIfDefenderNamed` (Zangoose): exact name match. OK.
- A107 `ExtraDamageIfEvolvedThisTurn` (Jolteon, generic, no source restriction in the text): OK.
- A109 `ExtraDamageIfEvolvedThisTurn` (Weavile ← Sneasel, Stage 1, single possible source): OK — unlike A108/F1, no Rare-Candy ambiguity is possible.
- A110, A111, A115 `ExtraDamageIfKnockedOutLastTurn` (60/40/50, no type filter, no status): reads `knocked_out_by_opponent_attack_last_turn`. OK.
- A112 `ExtraDamageIfKnockedOutLastTurn` (0 extra damage, Paralyze only): OK.
- A113 `ExtraDamageIfKnockedOutLastTurn` (60 extra + Paralyze): OK.
- A114 `ExtraDamageIfKnockedOutLastTurn` (80 extra, Darkness-type filter): reads `knocked_out_types_by_opponent_attack_last_turn`. OK (PROBABLE — didn't trace where that set is populated).
- A116, A117 `ExtraDamageIfMoreEnergyThanDefender`: strict `own > opponent`, uses effective Energy counts. OK.
- A121 `ExtraDamageIfOpponentActiveHasAbility`: uses the shared `has_any_in_play_ability` helper (Ability-negation aware). OK (PROBABLE).
- A122 `ExtraDamageIfOpponentHpLessThanSelf`: strict `<`. OK.
- A123, A124 `ExtraDamageIfOpponentHpMoreThanSelf`: strict `>`. OK.
- A125 `ExtraDamageIfOpponentPointsExactly` (==1): exact match. OK.
- A126 `ExtraDamageIfOwnPointsExactly` (==0): exact match. OK.
- A127–A131 `ExtraDamageIfPokemonOnBench` (Passimian/Latios/Durant×2/Magmortar): named-Bench-mate check. OK.
- A132–A134 `ExtraDamageIfStadiumInPlay` (40/70/20): `active_stadium.is_some()`. OK.
- A135 `ExtraDamageIfStage2OnBench`: `get_stage(p) == 2` over own Bench. OK.
- A136–A140 `ExtraDamagePerEnergy` (opponent Active 20/30/40, self 20, "for each"/"more for each" via `include_fixed_damage`): OK.
- A141 `ExtraDamagePerOpponentSpecialCondition`: counts distinct condition types on the opponent's Active (5-condition list). OK — any over/under-count from co-existing Sleep/Paralysis/Confusion is a consequence of already-known bug #7, not re-reported.
- A142 `ExtraDamagePerOwnPoint`: `state.points[current_player]`. OK.
- A143 `FirstAttackBonusTurnEffect` (Flutter Mane ex): `has_attacked_since_play` flag, set false on a fresh `PlayedCard` (new object each evolution), matching "first time…after coming into play." OK.
- A144, A145 `FlipUntilTailsBonusDamage` (30/40 per heads): unbounded flip-until-tails via `geometric_until_tails_saturated`, matches "no cap" rule. OK.
- A146 `FlipUntilTailsDiscardOpponentDeck`: same unbounded-flip construction, saturated at the opponent's actual deck size. OK.
- A147, A148 `HealOneYourBenchedPokemon` (50/30): choice restricted to damaged Bench Pokémon; none damaged ⇒ no-op. OK.
- A149–A152, A154, A156 `InflictStatusConditions` (opponent Active — Poison/Confuse/Asleep/Burn/Poison+Burn/Poison+Asleep): straightforward application; A151 checked0921. OK.
- A153, A155 `InflictStatusConditions` (self — Asleep/Confused): OK.
- A157, A158 `InflictStatusConditionsOnBothActive` (Asleep/Confused): applies to both Actives. OK.
- A159 `KnockBackOpponentActive`: switch choice is pushed for the **opponent** to resolve (`state.move_generation_stack.push((opponent, choices))`), matching "(Your opponent chooses the new Active Pokémon.)"; empty Bench ⇒ no-op. OK.
- A160 `MaySwitchSelfWithBench`: adds a `Noop` choice alongside switch options, matching "you may." OK.
- A161 `MoltresExInfernoDance`: 3 coins hardcoded; distributes exactly `heads` Energy among Fire Benched Pokémon "in any way you like" (any split, including stacking); heads=0 or no Fire Bench ⇒ no attach. OK (see number-mismatch note above).
- A162 `NoDamageIfSelfHpAtMost` (60): `<=` threshold. OK.
- A163 `NoDamageUnlessMovedFromBench`: see **F2** — shares the KO-promotion bug.
- A164–A171 `RandomSpreadDamage` (various times/damage, include_own_bench flag): confirmed *with-replacement* random target sequence (same Pokémon can be hit more than once across N picks, matching "chosen at random N times"), correct target pool per `include_own_bench`. OK.
- A172 `RevealTopDeckDamagePerHeavyPokemon`: reads the concrete top 3 of the (already-shuffled, forecast-fixed) deck, filters Pokémon with retreat cost ≥3 (Trainers correctly excluded via `get_retreat_cost() == None`), then shuffles. OK.
- A173 `SearchToBenchBasic`: shared `search_and_bench_basic`/`search_and_bench_with_filter` infra (used by many other search effects outside this batch); uniform random Basic, no-match ⇒ shuffle only. OK (PROBABLE, shared infra not re-audited here).
- A174 `SelfAsleepAndHeal`: applies Asleep then heals; order doesn't affect outcome. OK.
- A175 `SelfCureStatusConditions` (Wailord ex): clears all conditions on self. OK.
- A176 `SelfDiscardAllEnergy` (checked0921): clears attacker's Energy; damage always applied first. OK.
- A177 `SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon` (Water, checked0921 — mechanic only): OK.
- A178 `SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon` (Lightning): discards *all* matching-type Energy (recomputed live, not a fixed count), then player picks 1 opponent Pokémon (Active or Bench) for the fixed damage. OK.
- A179, A180 `SelfDiscardEnergyAndInflictStatus` (Fire→Burn, Grass→Poison, both checked0921): best-effort discard (won't under/over-discard) then always applies the status; cost guarantees the Energy is present. OK.
- A181 `SelfDiscardEnergyAndInflictStatus` (Water×2→Paralyze): same shape, full check. OK.
- A182 `SelfDiscardEnergyThenDamageAnyOpponentPokemon` (Fire×2→80 to any opponent Pokémon): best-effort discard, then player picks target. OK.
- A183 `SelfDiscardRandomEnergyAndBenchDamage` (Walking Wake): see **F3**.
- A184 `SelfHealAndCardEffect` (Cradily): self-heal + `NoRetreat` on Defending Pokémon. OK.
- A185 `SelfHealIfStadiumInPlay` (20): gated on `active_stadium.is_some()`. OK.
- A186 `ShuffleOpponentActiveIntoDeck`: heads shuffles the opponent's Active + its evolution chain into their deck, discards its Energy, triggers promotion/win-check, no points scored (matches "removal without a KO gives no points"). OK.
- A187 `ShuffleOpponentToolsIntoDeckBeforeDamage` (Hoopa): strips Tools from every opposing in-play Pokémon and shuffles them in *before* queuing the attack's damage (matches "Before doing damage…"); max-HP recompute is dynamic (`get_effective_total_hp` reads `attached_tools` live), so no separate "refresh" call is needed for a correct KO check once damage resolves. OK.
