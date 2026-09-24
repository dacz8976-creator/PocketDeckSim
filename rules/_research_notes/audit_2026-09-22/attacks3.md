# attacks3 — Attack effects group 3 (186 texts, A1–A186)

Read RULES_FOR_AGENTS.md and rules/README.md first. Reviewed every Mechanic variant's handler in
`src/actions/apply_attack_action.rs` (dispatch table + function bodies), cross-checked against
`src/actions/effect_mechanic_map.rs` map entries, and checked each of the 186 texts' parameters
(numbers, energy types, own/opponent, bench/active, "each"/"up to", who chooses, conditions,
failure cases) against its handler. No probes were run — every finding below is VERIFIED-READ with
exact file:line citations; no High/Medium doubt required a probe.

## Findings

### F1 [Medium] `ChargeBench` used instead of `AttachEnergyToBenchedBasic` for Pichu's Crackly Toss — energy can go to a non-Basic Benched Pokémon  (VERIFIED-READ)
- Card(s): A4 066 / A4 171 / B2 213 Pichu — Crackly Toss (entry **A34**, `ChargeBench` group)
- Text (printed card text): "Take a [L] Energy from your Energy Zone and attach it to 1 of your **Benched Basic** Pokémon."
- Engine: `src/actions/effect_mechanic_map.rs:1780-1786` maps this exact text to
  `Mechanic::ChargeBench { energies: vec![EnergyType::Lightning], target_benched_type: None }`.
  Contrast with the otherwise-identical `[R]` and `[W]` texts a few lines away
  (`effect_mechanic_map.rs:1820-1824`, `:1844-1849`), which correctly map to
  `Mechanic::AttachEnergyToBenchedBasic { energy_type: ... }`. The handler for `ChargeBench`,
  `energy_bench_attack` (`apply_attack_action.rs:2311-2337`), filters benched targets only by
  `target_benched_type` (an *energy-type* match) — with `target_benched_type: None` there is no
  filter at all:
  ```rust
  let choices = state.enumerate_bench_pokemon(state.current_player)
      .filter(|(_, played_card)| {
          target_benched_type.is_none_or(|t| state.pokemon_is_type(played_card, t))
      })
      .map(|(in_play_idx, _)| SimpleAction::Attach { ... })
  ```
  There is no stage/`get_stage(pokemon) == 0` check anywhere in this path, unlike
  `attach_energy_to_benched_basic` (`apply_attack_action.rs:4996-5011`), which the `[R]`/`[W]`
  siblings correctly use.
- Example: Pichu is Active with a Benched Eevee (Basic) and a Benched Stage-1 (e.g. evolved
  Raichu) on the bench. Using Crackly Toss, the engine offers "attach to Raichu" as a legal move
  generation option even though the card restricts the target to a Benched *Basic* Pokémon; real
  Pocket would only offer Eevee.
- Impact: Pichu — Crackly Toss only (a 0-cost, 0-damage support attack); low play rate (P3, not in
  Dustin's decks or the meta pool), but any simulated game that plays this exact Pichu with an
  evolved Benched Pokémon present gets an illegal energy-attachment option in its move space.

## Rules questions
None raised by this group — the texts all map to already-settled rules (bench damage, self-choice
vs. random, "for each"/"more" phrasing, discard/heal amounts).

## Checked and OK
(One line per group of entry IDs; every ID A1–A186 is covered by one of these lines or by F1
above. Parameters — numbers, energy types, own/opp scope, bench/active, filters — verified against
each text; "Number-mismatch hint" flags the assignment doc attached to A26, A87, A88, A141, A146,
A168 are all false positives: those numbers are baked into the handler as constants or as `Vec`
length, not passed as a param, and match the text.)

- **A1–A5** `AlsoBenchDamage`: opponent/own flag, per-target damage, and the `must_have_energy`
  filter (A3, "that has any Energy attached") all match; bench targets get flat listed damage with
  no Weakness (handled by the shared damage pipeline, not this code). OK.
- **A6** `AlsoChoiceOwnPokemonDamage` (Mimikyu): player chooses via generated `SimpleAction`
  choices (incl. itself as a legal target, which the text doesn't forbid). OK.
- **A7** `AttachEnergiesAnyWayToBenchedBasic` (Ho-Oh ex): recursively enumerates every
  distribution of R/W/L across Benched Basics (stage==0, fossils count), including stacking
  several types on one Pokémon ("in any way you like"); fizzles safely with damage still applied
  if no Benched Basic exists. OK.
- **A8–A9** `AttachEnergyFromZoneToTwoBenched`: forces choosing exactly 2 Benched Pokémon (or the
  lone one if only 1 exists); correct energy type per entry. OK.
- **A10–A11** `AttachEnergyToBenchedBasic`: correctly Basic-only (`get_stage(pokemon)==0`),
  contrast with F1. OK.
- **A12–A24** `BenchCountDamage`: `include_fixed_damage` correctly distinguishes "X more damage"
  (adds printed base) from plain "X damage for each" (base dropped); `bench_side`
  (YourBench/OpponentBench/BothBenches), `energy_type` (checks the Pokémon's own type, not
  attached energy) and `names` filters (A18 Nidoking, A22 Wishiwashi/Wishiwashi ex) all match
  their texts. A15/A16 (checked0921) confirmed at the variant level only, per instructions. OK.
- **A25** `BlockBasicAttack` (Umbreon): only applies `CannotAttack` when the opponent's Active is
  Basic-stage, gated by `prevents_attack_effects`. OK.
- **A26** `CelebiExPowerfulBloom`: coins = total attached Energy (any type) on the attacker; 50/heads
  hardcoded, matches; 0 energy → 0 damage, no coin flips. OK.
- **A27** `ChangeRandomOpponentActiveEnergyType`: picks uniformly among the 8 basic types (Grass…
  Metal, no Colorless — `BASIC_ENERGY_TYPES` at `apply_attack_action.rs:3822`) crossed with each
  attached-energy index; no-energy case is damage-only. OK.
- **A28–A33, A35–A36** `ChargeBench`: energy list and `target_benched_type` (type filter or none)
  match their texts exactly. OK. (A34 is F1.)
- **A37** `ChooseOpponentHandCardToShuffleIntoDeck` (Purugly): attacker chooses which revealed
  card to shuffle in (player choice, not random). OK.
- **A38** `CoinFlipAlsoChoiceBenchDamage`: heads → player-chosen Benched target takes bundled
  damage; no Benched targets → coin flip is moot, active damage still dealt. OK.
- **A39–A41** `CoinFlipExtraDamageOrSelfDamage`: heads = extra damage, tails = base damage + self
  damage to the attacker; matches "if heads/if tails" framing exactly, amounts per entry. OK.
- **A42–A45** `CoinFlipPerPokemonInPlay`: coin count = attacker's own in-play Pokémon (optionally
  name-filtered, A42 Tandemaus/Maushold); 0 in-play Pokémon → 0 damage, no flips. OK.
- **A46** `CoinFlipSelfChargeActive` (Tepig): heads attaches 2 Fire to itself; tails is damage-only
  (0 fixed damage either way, matches "Stoke"). OK.
- **A47** `CoinFlipStatusOpponentOrSelf` (Psyduck): heads → opponent Confused, tails → self
  Confused, both go through `apply_attack_status_condition` (respects immunities). OK.
- **A48** `CoinFlipTailsCardEffect`: tails-only effect (`CannotAttack`, duration 2 = "your next
  turn"); heads = plain damage. OK.
- **A49–A50** `DamageAllOpponentPokemon`: flat damage to every opponent Pokémon (Active + Bench),
  no Weakness applied since this is a flat spread, matching Bench-damage rule. OK.
- **A51** `DamageAllOpponentPokemonWithNextTurnBonus` (Archeops): initially looked miscoded (Active
  target's raw damage list entry never includes `bonus`), but the shared damage pipeline
  (`hooks/core.rs:1082-1109`, `get_increased_attack_specific_modifiers`) adds the
  `IncreasedDamageForAttack` bonus to Active-to-Active damage automatically when boosted, while
  this handler manually pre-adds the bonus only for Bench targets (which the shared pipeline
  deliberately skips, per the code comment at `apply_attack_action.rs:6208-6210`, to avoid double
  counting). Verified both halves total correctly to `damage+bonus` on every opponent Pokémon when
  boosted. Not a bug. OK.
- **A52** `DamageEqualToSelfDamage` (Phanpy): damage = attacker's own damage counters at time of
  attack. OK.
- **A53** `DiscardEnergyFromOpponentActive`: random discard of 1 Energy from opponent's Active,
  gated by `prevents_attack_effects`. OK.
- **A54–A55** `DiscardHandCards`: mandatory discard of exactly `count` cards (player chooses which,
  via generated combinations); "if you can't" → checked before generating choices, returns
  damage-0/no-effect. OK.
- **A56** `DiscardStadiumInPlay`: discards whichever Stadium is in play (either player's) to its
  owner's discard pile. OK.
- **A57** `DiscardToolsFromHandForDamage`: "up to 2" — optional, choices include discarding 0;
  damage = 50 × cards actually discarded. OK.
- **A58** `DiscardTopSelfDeck`: discards own deck's top card; empty deck is a safe no-op (`draw()`
  returns `None`). OK.
- **A59** `DrawCard`: queues a normal 1-card draw (subject to the shared hand-limit-10 draw logic
  elsewhere, out of this handler's scope). OK.
- **A60** `DrawPerNamedPokemonInPlay` (Poochyena): counts attacker's own in-play Pokémon named
  "Poochyena" (includes itself if Active), draws that many. OK.
- **A61–A63** `ExtraDamageIfAttackUsedDuringOwnLastTurn`: keyed on exact `attack_name` ("Sweets
  Relay") and reads a dedicated "used during own last turn" tracker; amounts per entry. OK.
- **A64–A67** `ExtraDamageIfBothHeads`: flips exactly 2 coins, bonus only on double-heads, amounts
  per entry. OK.
- **A68–A69** `ExtraDamageIfCardInDiscard`: checks own discard pile for the exact named card
  ("Quick-Grow Extract" / "Volbeat"). OK.
- **A70** `ExtraDamageIfCombinedActiveEnergyAtLeast` (checked0921, variant only): sums both
  Actives' attached-energy counts against the threshold. OK.
- **A71** `ExtraDamageIfDamagedByAttackLastTurn` (Wobbuffet): reads a dedicated
  "damaged by attack while Active last turn" flag, matching the "while it was in the Active Spot"
  qualifier. OK.
- **A72–A74** `ExtraDamageIfDefenderStage`: `evolution:false`→Basic-stage check,
  `evolution:true`→stage>Basic; matches "Basic"/"Evolution" wording. OK.
- **A75–A81** `ExtraDamageIfDefenderType`: checks opponent Active's own type against the listed
  `energy_types` (single or, for A80, a 2-type OR-list). OK.
- **A82–A83** `ExtraDamageIfDifferentEnergyTypesAttached`: `all_in_play` correctly switches scope
  between "this Pokémon" (A82) and "your Pokémon in play" (A83); counts distinct energy types. OK.
- **A84–A92** `ExtraDamageIfExtraEnergy`: checks total cost (`attack.energy_required` + the extra
  types) via the shared `contains_energy`/`energy_missing` cost-matching logic, correctly requiring
  N *additional* Energy of that type beyond the printed cost; A87/A88's "3" is the literal length
  of a 3-element `Vec`, not a missing number. OK.
- **A93** `ExtraDamageIfHandSizeEqualsOpponent`: compares hand sizes at time of attack. OK.
- **A94–A103** `ExtraDamageIfHurt`: `opponent`/`benched` flags correctly scope "opponent's
  Active"/"this Pokémon"/"your Benched" damage checks; amounts per entry. OK.
- **A104** `ExtraDamageIfOpponentHasSpecialCondition` (Absol): checks
  `opponent_active.has_status_condition()`. OK.
- **A105–A109** `ExtraDamageIfToolAttached`: `opponent` flag correctly scopes "this
  Pokémon"/"your opponent's Active Pokémon has a Tool attached". OK.
- **A110** `ExtraDamagePerCardInOwnHand`: `include_fixed_damage:false` → total is purely
  `hand_size × 20`, matching "does 20 damage for each card" (no separate base). OK.
- **A111** `ExtraDamagePerOpponentPoint`: reads `state.points[opponent]`. OK.
- **A112** `ExtraDamagePerOpponentPointDuringOwnLastTurn`: reads a dedicated
  `points_gained_during_own_last_turn[opponent]` ledger, not lifetime points. OK.
- **A113** `ExtraDamagePerOwnKnockoutThisGame` (Kingambit): reads a lifetime own-KO counter. OK.
- **A114** `ExtraDamagePerPokemonInDiscard`: counts all `Card::Pokemon` in own discard, any type.
  OK.
- **A115** `ExtraDamagePerPokemonTypeInDiscard`: filters own discard's Pokémon by `energy_type`.
  OK.
- **A116** `ExtraDamagePerSpecificEnergyAllYours`: sums the given energy type across all of the
  attacker's in-play Pokémon's attached Energy ("all of your Pokémon"). OK.
- **A117–A118** `ExtraDamagePerTrainerTypeInDiscard`: filters own discard by `TrainerType`
  (Supporter/Item). OK.
- **A119** `FirstAttackBonusDamageAndStatus` (Iron Bundle ex): gated on a per-Pokémon
  `has_attacked_since_play` flag ("first time…after coming into play"); status only applied on
  that first use, flag set unconditionally after. OK.
- **A120** `FlipCoinsBenchDamagePerHead`: fixed Active damage always applied; 3 coins, bench
  damage = 20×heads split across every opponent Benched Pokémon. OK.
- **A121–A123** `FlipCoinsDiscardOpponentEnergyPerHeads`: `nothing_if_no_heads` correctly
  distinguishes "if both/all tails, this attack does nothing" (A121, A123) from "no such clause"
  (A122, where 0 heads still deals the fixed damage). OK.
- **A124–A128** `FlipUntilTailsDamage`: unbounded flip-until-tails modeled as a saturated geometric
  distribution (capped where extra heads can no longer change the outcome), matching the "flip
  until tails, unbounded" rule without literally simulating infinite coins. OK.
- **A129–A131** `HealEachYourPokemon`: `benched_only`/`basic_only`/`energy_type` filters match
  "Benched Basic"/"[P] Pokémon"/"Benched" scoping; goes through `state.heal_pokemon`. OK.
- **A132** `HealSelfEqualToDamageDealt` (Kabutops): heals the attacker by the *actual post-modifier*
  damage dealt to the opponent's Active (computed via `modify_damage`, not raw attack value). OK.
- **A133–A134** `IncreasedDamageNextTurn`: stored as a player-scoped `TurnEffect`, restricted to
  Active-to-Active damage only (`hooks/core.rs:1015-1017`, `!is_active_to_active → 0`), matching
  "to your opponent's Active Pokémon"; A134's `[F]`-only restriction checks the attacking Pokémon's
  own types. OK.
- **A135–A136** `InflictPoisonWithCustomCheckupDamage`: applies Poison via the immunity-aware path,
  then overrides checkup damage only if the Poison actually stuck. OK.
- **A137** `InflictStatusAndCardEffects` (Roserade): applies Poison via the immunity-aware
  `apply_attack_status_condition` (which already checks `prevents_attack_effects` internally), then
  separately gates the `NoRetreat` card effect behind the same check — no double-application bug.
  OK.
- **A138** `InflictStatusConditionsAndShuffleSelfIntoDeck` (Accelgor): both conditions applied
  unconditionally (mandatory, no "you may"); shuffle skipped only if the attacker was already
  knocked out by then. OK.
- **A139** `LessDamageIfSelfHurt` (Regidrago): `saturating_sub` floors at 0, no negative damage
  underflow. OK.
- **A140** `MagikarpWaterfallEvolution`: picks uniformly at random among matching evolution cards
  in the deck (matches "random", not player choice); no match → just shuffles. OK.
- **A141** `MegaKangaskhanExDoublePunchingFamily`: first hit resolves and knockouts/promotions are
  forced via `handle_knockouts` before the second 40-damage hit is queued (inserted at the bottom
  of the move-generation stack so any opponent promotion choice resolves first), matching "used
  after your opponent chooses a new Active Pokémon." OK.
- **A142** `MoveAllEnergyToBench`: moves all Energy off the attacker to one chosen Benched Pokémon.
  OK.
- **A143** `MoveAllEnergyTypeToBench` (Mismagius): only the specified type; falls back to
  damage-only if the attacker has none of that type or no Bench exists. OK.
- **A144** `MoveEnergyFreelyAmongYourPokemon`: "you may" — offers a Noop choice alongside every
  candidate move (optional). OK.
- **A145** `OminousClaw` (Absol): heads → attacker chooses which revealed Supporter to discard
  (player choice among generated options, not random); no Supporters → no discard. OK.
- **A146** `PalkiaExDimensionalStorm`: hardcoded 150 Active / 20-per-Bench damage and a 3×Water
  discard match the text exactly (all baked-in constants, not params — the "Number-mismatch hint"
  is a false positive). OK.
- **A147** `RecoilIfKo` (Rampardos): KO status checked immediately after damage resolves, before
  discard/promotion, so recoil correctly triggers only on an actual KO. OK.
- **A148** `SearchToHandByEnergy`: filters deck by Pokémon type (any stage, matches "Grass
  Pokémon" with no Basic restriction in this text). OK.
- **A149–A150** `SearchToHandByEvolvesFrom`: filters deck by exact `evolves_from` match, random
  pick. OK.
- **A151–A157** `SelfDamage`: flat self-damage to the attacker, amount per entry, always applied
  regardless of coin flips (no "if" clause in any of these texts). A151/A152 (checked0921)
  confirmed at the variant level only. OK.
- **A158** `SelfDamageAndAllBenchDamage` (Forretress): self-damage plus flat damage to every
  Benched Pokémon on both sides. OK.
- **A159** `SelfDiscardAllEnergyAndInflictStatus` (Galvantula): discards 100% of attached Energy
  (empty-safe), then unconditional Paralysis. OK.
- **A160** `SelfDiscardAllEnergyKnockOutOpponentActive` (Raging Bolt): sets remaining HP to 0
  directly (a true Knock Out, not damage — correctly bypasses Weakness/reductions), gated by
  `prevents_attack_effects`. OK.
- **A161–A172** `SelfDiscardEnergy`: discards the exact listed Energy types/counts from the
  attacker via "best effort" (fails gracefully if the attacker doesn't have them all). OK.
- **A173** `SelfDiscardEnergyAndCardEffect` (Corviknight): discards 2 Metal, then applies
  `ReducedDamage{50}` to self for 1 opponent turn. OK.
- **A174** `SelfDiscardEnergyAndChoiceBenchDamage` (Rapid Strike Urshifu): discards Water, and the
  player chooses which opponent Benched Pokémon takes the bundled 40. OK.
- **A175–A178** `SelfHeal`: flat self-heal, amount per entry. A175 (checked0921) confirmed at the
  variant level only. OK.
- **A179** `ShuffleHandIntoDeckDrawEqualToOpponentHand` (Chatot/Mime Jr.): shuffles own hand into
  deck, draws exactly the opponent's *current* hand size (computed before the shuffle). OK.
- **A180–A181** `ShuffleRandomOpponentHandCardsIntoDeck`: random pick from opponent's hand;
  A181 also unconditionally shuffles the attacker itself into its own deck after. OK.
- **A182–A184** `ShuffleRandomOpponentHandCardsPerHeads`: coin count per entry (1 or 3), random
  card(s) from opponent's hand shuffled in per heads. OK.
- **A185–A186** `SwitchInOpponentBenchedThenDamage`: player chooses which Benched opponent
  Pokémon to switch in (not random); "if you do" correctly skips the follow-up damage when the
  opponent has no Bench; A186's coin-gated, 0-damage version matches Chinchou's text (no damage
  clause at all). OK.

## Coverage note
All 186 texts got a verdict above. No probes were needed — every check above was resolved by
reading the dispatch table, the named handler function, and (for F1) the map file entry directly;
none of the doubts reached High/Medium uncertainty after reading the code.
