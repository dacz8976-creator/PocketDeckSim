# abilities — Ability effects (156 unique texts)

Scope: all 156 unique Ability texts in `database.json`, the map entries in
`src/actions/effect_ability_mechanic_map.rs` (→ `AbilityMechanic` in `src/actions/abilities/mechanic.rs`),
activated-ability gating/resolution in `src/move_generation/move_generation_abilities.rs` +
`src/actions/apply_abilities_action.rs`, and passive/triggered hooks in `src/hooks/core.rs`,
`src/hooks/counterattack.rs`, `src/actions/apply_action_helpers.rs`, `src/state/*.rs`.

Method: read `mechanic.rs` (734 lines, every variant documented) in full; read
`move_generation_abilities.rs` (536 lines) and most of `apply_abilities_action.rs` (1312 lines) in full —
these two files are the complete gating/resolution logic for every *activated* Ability, so every
activated-ability text got at least this pass. Passive/triggered mechanics were checked by grepping
their variant name into `hooks/core.rs`, `hooks/counterattack.rs`, `apply_action_helpers.rs`, `state/*.rs`
and reading the call site. All 18 P1-dustin and all 14 P2-meta abilities got a full read of their
resolution code; P2-checked0921 (12) got the shared-mechanic confirmation the brief asks for; the
remaining P3 abilities got the same move-generation-file read plus a targeted grep of their resolution
site. No probes were run — every finding below is VERIFIED-READ and didn't need one.

## Findings

### F1 [Medium] Dusknoir/Glimmora's point-denial coin only fires on attack-caused knockouts (confidence: VERIFIED-READ)
- Ability: B25, `CoinFlipToDenyKnockoutPoints`.
- Card(s): B1 105 Dusknoir — Fade into Darkness; B3a 045/078 Glimmora — Shattering Crystal.
- Text (database.json, [OFFICIAL]): "When this Pokémon is Knocked Out, flip a coin. If heads, your
  opponent can't get any points for it." — **no** "by damage from an attack" qualifier, unlike the sibling
  mechanics `DamageOnKnockoutInActive` / `MoveAllTypedEnergyToBenchOnKnockout` / `CoinFlipToKnockOutAttackerOnKnockout`,
  which all print that restriction explicitly.
- Engine: the coin is only flipped in `apply_attack_action.rs:254` `apply_defender_point_denial_if_needed`,
  called once at `apply_attack_action.rs:175`, inside the attack-forecast path only. The
  `CardEffect::DenyKnockoutPoints` flag it sets is the *only* thing `handle_knockouts`
  (`apply_action_helpers.rs:650-704`) checks when awarding points — it never flips a coin itself, it only
  reads a flag that nothing sets outside an attack.
- Example: Dusknoir/Glimmora at 10 remaining HP takes 10 Poison damage at Checkup (or is finished off by
  an opposing Ability like Greninja's Water Shuriken, or its own controller's self-damage Ability such as
  Flareon ex's Combust) and is Knocked Out. The engine awards the opponent's point unconditionally; the
  card text says it should still get the 50/50 coin.
- Impact: any Dusknoir/Glimmora game where the KO comes from Poison/Burn Checkup, an opposing Ability, or
  self-damage rather than an attack — situational but a clean text/engine mismatch, not cosmetic.

### F2 [Medium] Iron Jugulis (B3a 046) and one Dragalge ex printing (B3 231) never trigger their on-damaged Ability (confidence: VERIFIED-READ)
- Abilities: B34 `CounterattackDamage` (Iron Jugulis's "Automated Combat"); B104 `PoisonAttackerOnDamaged`
  (Dragalge ex's "Poison Point").
- Text: "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon,
  do 20 damage to the Attacking Pokémon." / "...the Attacking Pokémon is now Poisoned."
- Engine: unlike every other on-damaged/on-knockout mechanic in the file (which dispatch off
  `get_in_play_ability_mechanic`), these two effects are resolved in `hooks/counterattack.rs` by a
  **hardcoded match on `CardId`** — `get_counterattack_damage` (lines 28-39) and `should_poison_attacker`
  (lines 118-131) — rather than off the `AbilityMechanic` the card actually maps to. Cross-checking
  `database.json` against those match arms:
  - `CounterattackDamage` text is printed on 8 cards (A1 061, A1a 056, A2b 028, A3a 052, A4a 065,
    B1 297, **B3a 046 Iron Jugulis**, P-A 054); `get_counterattack_damage` only matches 7 — B3a 046 is
    absent.
  - `PoisonAttackerOnDamaged` text is printed on 4 Dragalge ex (B1 160, B1 263, B1 281, **B3 231**);
    `should_poison_attacker` only matches 3 — B3 231 is absent.
  - `CardId::B3a046IronJugulis` and `CardId::B3231DragalgeEx` both exist and are wired into the card
    database (`card_ids.rs:3165`/`3116`, `database.rs:70275`), so this isn't an unimplemented-card panic —
    the Ability is silently a no-op for exactly these two printings.
- Example: B3a 046 Iron Jugulis (Ability "Automated Combat") sits Active, takes an opponent's attack —
  no counter-damage is ever dealt. B3 231 Dragalge ex sits Active, takes an opponent's attack — the
  attacker is never Poisoned (unless it also happens to hold Poison Barb, a separate check).
- Impact: complete, silent loss of the Ability for these two specific printings only; every other
  printing of the same text works correctly. Root cause is systemic: these two functions must be
  hand-updated whenever a new printing of either text is added, and the last two additions were missed —
  worth checking again after any future set import.

### F3 [Medium] Vaporeon's Wash Out ("as often as you like") is capped to once per turn by default
- Ability: B92, `MoveTypedEnergyFromBenchToActive` (Vaporeon — Wash Out, A1a 019 / A4b 099-100).
- Text: "**As often as you like** during your turn, you may move a [W] Energy from 1 of your Benched
  [W] Pokémon to your Active [W] Pokémon." — of the two Ability texts in the whole 156-text set that print
  "as often as you like" (the other is Dusknoir's Shadow Void, B89, which is correctly unbounded — no
  `ability_used` check in `can_use_dusknoir_shadow_void`), this one is deliberately bounded.
- Engine: `move_generation_abilities.rs:477-482` `can_use_vaporeon_wash_out` gates on `card.ability_used`
  unless the env var `DECKGYM_UNBOUNDED_ENERGY_MOVES=1` is set (`energy_moves.rs:44,59-61`); this is a
  documented, intentional simplification for search-bot performance (ablation note in the same file: the
  literal unbounded version was a 9.5× cost outlier on `milotic-vaporeon`), not an oversight — but it is a
  real behavior difference from the printed card, and it removes a genuine piece of Vaporeon-deck play
  (rearranging Water Energy more than once per turn, e.g. to power up a bigger attack from a pool spread
  across the Bench). Flagging because the brief asks to check "once during your turn"-vs-unrestricted
  wording specifically; this is the one ability in the set where the two diverge on purpose.
- Impact: Vaporeon (plain, not ex) decks that lean on repeated Wash Out activations in one turn; low
  priority to actually change given the documented performance rationale and the escape hatch, but worth
  the project knowing this one card is intentionally not-per-text by default.

### F4 [Low] Garchomp's Reckless Shearing can be activated on an empty deck, discarding a hand card for nothing
- Ability: B44 (P2-meta), `DiscardFromHandToDrawCard` (A2 123/175 Garchomp — Reckless Shearing).
- Text: "You must discard a card from your hand in order to use this Ability. Once during your turn, you
  may draw a card."
- Engine: `move_generation_abilities.rs:197-199` gates only on `!state.hands[current_player].is_empty()`
  — no check that the deck has a card left to draw. Compare `DrawCardsOncePerTurn` (Team Rocket's
  Slowking ex, B50), which correctly adds `!state.decks[state.current_player].cards.is_empty()`
  (`move_generation_abilities.rs:256-260`). `state.maybe_draw_card` silently no-ops on an empty deck
  (`state/mod.rs:806-813`, matches the real "no deck-out loss" rule), so using Reckless Shearing with an
  empty deck discards a real hand card for zero benefit — a move a bot could still pick since it's legal
  and cheap to search.
- Impact: only matters in the rare case a Garchomp deck's own deck is empty (late game); low severity,
  included because it's the same "blocked only when it visibly can't work" family the brief calls out
  (known issue #4) and this is a case the project hasn't listed yet.

## Rules questions
None new. Two already-known items surfaced again during this pass and are **not** re-reported per the
brief: #13 (Darkrai ex Nightmare Aura only fires on manual Zone attachment) — contrasted directly against
Jolteon ex's Electromagnetic Wall (B53, P1-dustin), which correctly fires on *any* Zone-sourced
attachment (no `only_turn_energy` restriction) and is therefore itself fine; and #5/#8/#9 (Eevee Boosted
Evolution, Lum Berry vs. Bad Dreams order, Caterpie Quick Growth timing), all confirmed present but
unchanged in scope.

## Checked and OK

All verdicts below are VERIFIED-READ against `move_generation_abilities.rs`, `apply_abilities_action.rs`,
and the relevant hook, unless noted. IDs match `assign/abilities.md`.

**P1-dustin (18/18, deep read of each)**
- B2 `AttachEnergyFromDiscardToActiveTypedFromBench` (Dragonair): bench-only gate, one branch per
  distinct discard-pile Energy type, always attaches to Active idx 0 — matches text.
- B17 `CannotAttackWithoutBenchedNames` (Regigigas): self-scoped attack block in `move_generation/attacks.rs`,
  reads Bench only, suppression-aware (Power of Alchemy correctly frees it) — matches.
- B25 `CoinFlipToDenyKnockoutPoints` — **see F1**.
- B31 `ConfuseOpponentActive` (Meowstic): requires holder Active, unconditional apply to opponent's Active — matches.
- B39 `DamageOpponentActiveIfArceusInPlay` (Crobat): Arceus/Arceus ex name check correct, damages opponent Active
  with `is_from_active_attack:false` (no Weakness) — matches.
- B50 `DrawCardsOncePerTurn` (T.R. Slowking ex): `require_active` honored, gated on non-empty deck — matches.
- B53 `ElectromagneticWall` (Jolteon ex): fires on any Zone-sourced attach to the wall-holder's opponent
  while the wall is Active, hardcoded 20 dmg via `handle_damage_only` (no Weakness) — matches; correctly
  broader than Nightmare Aura (see Rules questions).
- B58 `HealActiveYourPokemon` (Wigglytuff/Indeedee ex/…): heals own Active (idx 0) — matches.
- B67 `ImmuneToStatusConditions{status:None}` (Arceus ex): blanket immunity enforced in the single
  `apply_status_condition` chokepoint — matches.
- B69 `IncreaseAttackCostForOpponentActive` (Stoutland/Goomy): +1 colorless only when holder is opponent's
  Active — matches.
- B78 `IncreasePoisonDamage` (Nihilego): +10 per Nihilego, opponent-Active-only, stacks (unit-tested in
  `apply_action_helpers.rs`) — matches.
- B79 `IncreaseRetreatCostForOpponentActive` (Ariados): +1 colorless added to the Active being retreated
  when the opponent has the ability; `get_retreat_cost` is only ever called on the true Active — matches.
- B91 `MoveRandomEnergyFromOpponentActiveToSelfOnEvolve` (T.R. Raticate ex): weighted-by-count random branch
  over opponent Active's attached Energy, triggered only `on_evolve(..., from_hand=true)` — matches.
- B107 `PreventAllDamageFromEx` (Oricorio Safeguard): gated on `is_from_active_attack` and attacker `is_ex()`
  in `modify_damage`, so Ability/Poison/Burn damage still lands — matches "Ability damage isn't attack damage."
- B113 `ProtectSelfNextTurnAfterAttackKnockout` (Zoroark/Garchomp): `on_attack_knockout` requires
  `is_from_active_attack` and a genuine opponent KO before granting `PreventAllDamageAndEffects` (dur. 1) — matches.
- B139 `SoothingWind{Some(Psychic)}` (Comfey): checked at every `apply_status_condition` call plus on
  Energy-attach and suppressor-removal reconciliation — matches.
- B142 `SuppressBasicAbilities` (Alolan Muk): symmetric (`basic_abilities_suppressed` scans both sides),
  routed through the single `get_in_play_ability_mechanic` chokepoint so nothing bypasses it — matches.
- B151 `TimeRecall` (Celebi): grants Active's `cards_behind` attacks as extra offered attacks, still
  filtered by the normal Energy-cost check afterward — matches "still need the Energy."

**P2-meta (14/14, full read)**
- B8 `AttachEnergyFromZoneToSelf{Water,1}` (Milotic ex): no location restriction printed, none enforced — matches.
- B15 `CanEvolveIntoEeveeEvolution` (Eevee ex): `can_evolve_into` extends the normal evolve check to any
  card with `evolves_from == "Eevee"`, suppression-aware — matches.
- B35 `DamageOnKnockoutInActive{70,Attacker}` (T.R. Electrode ex): shares `apply_knockout_retaliation`,
  gated on Active-idx + genuine opponent-attack KO — matches (see B36/B37 below, same gate).
- B38 `DamageOneOpponentPokemon` (Greninja Water Shuriken): targets any one of opponent's in-play Pokémon
  (Active or Bench), ability-damage path (no Weakness) — matches.
- B44 `DiscardFromHandToDrawCard` (Garchomp) — **see F4**.
- B59 `HealAllYourPokemon{20,None}` (Butterfree): heals every own Pokémon in play — matches.
- B62 `HealOneYourPokemon{30,require_active:true}` (Espeon ex): requires holder Active + a damaged target
  exists — matches.
- B66 `HealTypedPokemonOnEvolve{Water,60}` (Milotic): on-evolve, filtered to damaged [W] Pokémon — matches.
- B81 `LegendaryDrive` (Miraidon ex/Koraidon ex): bench-from-hand-only trigger, switches in then gathers
  Energy from every other in-play slot (including the just-displaced old Active) onto itself — matches
  "move all of your Energy in play."
- B84 `LookAtTopCardsPutTrainerTypeToHandOnEvolve{4,Item}` (Raticate): takes matching Items, returns the
  rest to the top in original order (functionally equivalent to "shuffle back" since nothing observed the
  order) — matches.
- B95 `NoRetreatCost{YourActive,Always}` (Jumpluff): `grants_active_no_retreat_cost` scans the holder's
  whole board, so it works from the Bench too — matches.
- B105 `PoisonOpponentActive` (Weezing): requires holder Active (`_in_play_index==0`) — matches.
- B129 `ReduceDamageIfArceusInPlay{30}` (Raichu/Magnezone): reduction keyed on the *receiver's own*
  controller having Arceus — matches.
- B143 `SwitchActiveTypedWithBench{Water}` (Greninja ex): requires Active is [W] and a Bench target exists — matches.

**P2-checked0921 (12/12, shared-mechanic confirmation only, per brief)**
- B5/B6 `AttachEnergyFromZoneToActiveTypedPokemon` (Baxcalibur W / Gardevoir P): mechanic gates on
  Active being the right type and Zone-attach availability — OK.
- B10 `AttachEnergyFromZoneToSelfAndDamage{Darkness,2,30}` (Hydreigon): self-damage only applied "if you
  do" (i.e. if Energy actually attached), no Weakness on the self-hit — OK.
- B13 `BadDreamsEndOfTurn{20}` (Darkrai): fires per-Darkrai (either player), targets opponent's Active
  only if Asleep — OK (Lum Berry ordering is the already-known #8, not re-reported).
- B16 `CanEvolveOnFirstTurnIfActive` (Eevee — Boosted Evolution): mechanic itself maps correctly; the
  known board-wide-scope bug (#5) is unchanged, not re-reported.
- B42 `DamageOpponentActiveOnZoneAttachToSelf{Darkness,20,only_turn_energy:true}` (Darkrai ex): matches
  its own map entry; the known scope gap vs. the official ruling (#13) is unchanged, not re-reported.
- B55 `EndTurnDrawCardIfActive{1}` (Entei/Suicune/Raikou ex — Legendary Pulse): mandatory (not "may"),
  queued unconditionally in `on_end_turn` while Active; empty-deck case correctly no-ops via
  `maybe_draw_card` rather than wasting anything — OK.
- B72 `IncreaseDamageForTypeInPlay{Fighting,20}` (Lucario): board bonus only applied when
  `is_active_to_active` (not to Bench-damage moves) — OK.
- B103 `PoisonAndBurnOpponentActiveOnEvolve` (T.R. Weezing ex): applies both conditions to opponent's
  Active on evolve — OK.
- B116 `RandomEvolutionFromDeck{EndOfOpponentTurnIfActive}` (Caterpie): mechanic wiring correct; the
  known Checkup-vs-end-of-turn ordering bug (#9) is unchanged, not re-reported.
- B123/B124/B125 `ReduceDamageFromAttacks` (Melmetal/Regirock/… 20; Cloyster/Dwebble 10; Armarouge ex 30):
  modeled as `CardEffect`, and `get_ability_damage_reduction` explicitly zeroes it when
  `!is_from_active_attack` — confirms Ability/Poison/Burn damage correctly ignores it — OK.
- B133 `ReduceRetreatCostOfYourActiveTypedFromBench{Darkness,1}` (Bombirdier): scans Bench for the ability,
  applies to Active only if type matches — OK.
- B140 `SoothingWind{None}` (Ogerpon ex): same chokepoint as B139 above — OK.

**P3 (remaining ~112, one-liners; all read via the full `move_generation_abilities.rs` /
`apply_abilities_action.rs` pass plus a targeted hook check)**
- B1 `AncientRoar` / B81-sibling trigger family: bench-from-hand-only (`on_bench_from_hand`), requires an
  opponent Bench target — OK.
- B3 `AttachEnergyFromDiscardToSelfAndDamage{Fire,20}` (Flareon ex): self-damage only "if you do" — OK.
- B4 `AttachEnergyFromZoneToActiveTypedOnEvolve{Fire}` (Charmeleon): on-evolve offer, `[Attach,Noop]` — OK.
- B7 `AttachEnergyFromZoneToBenchOnDamaged{Water}` (Jellicent): on-damaged, Active-only, player picks
  Bench destination, no-op on empty Bench — OK.
- B9 `AttachEnergyFromZoneToSelf{Lightning,1}` (Magneton) — OK, same as B8.
- B11 `AttachEnergyFromZoneToSelfAndEndTurn{Psychic}` (Giratina ex): only ends turn if Energy actually
  attached and holder not KO'd — OK.
- B12 `AttachEnergyFromZoneToYourTypedPokemon{Grass}` (Leafeon ex): requires holder Active, offers any own
  [G] Pokémon as target — OK.
- B14 `BurnOpponentActive` (Typhlosion): no location restriction printed, none enforced — OK.
- B18/B19/B20 Checkup family (Flygon ex/Glaceon ex/Garganacl): damage variants require holder Active,
  heal variant (Blessed Salt) correctly does not; heal resolved after checkup damage so it can't rescue a
  Pokémon already at 0 — OK, matches official Checkup ordering.
- B21 `CoinFlipParalyzeOpponentActiveOnEvolve` (Raichu): binary-coin on-evolve offer — OK.
- B22/B23 `CoinFlipStatusOpponentActive` (Hypno Asleep / Grafaiai Poisoned): plain once-per-turn coin — OK.
- B24 `CoinFlipSwitchInOpponentBenchToActive` (Rillaboom): requires opponent Bench target — OK.
- B26 `CoinFlipToKnockOutAttackerOnKnockout` (Galarian Cursola): forecast-time split, Active-KO'd-by-opponent-attack
  gate shared with the B35/36/37 family — OK.
- B27/B28/B29 `CoinFlipToPreventDamage` / `CoinFlipToReduceDamage` (Togekiss/Meowth; Bastiodon; Hisuian
  Goodra): passive, resolved via the abilities-as-effects path, same "attacks only" gating as
  `ReduceDamageFromAttacks` — OK.
- B30 `CoinFlipToSurviveKnockOut` (Conkeldurr/Ursaluna): `guts_would_flip` checks post-modifier lethal
  damage; survival sets remaining HP to 10 (hardcoded, matches text; map has no numeric field for this one
  since only one value is printed) — OK.
- B32 `CoordinatedUnit` (Falinks): both the damage bonus and the reduction require a second same-named
  Falinks in play — OK.
- B33 `CopyRandomOpponentHandSupporter` (Smeargle): requires holder Active, folds opponent's hand
  Supporters into one weighted outcome without removing the card from hand — OK.
- B36/B37 — see B35 above (same shared gate).
- B40/B41 `DamageOpponentActiveOnEvolve{20/30}` (Drizzile/Inteleon): on-evolve offer to opponent's Active — OK.
- B43 `DiscardEnergyToIncreaseTypeDamage` (Skeledirge): discards own attached [R] Energy, then a
  same-turn +50 bonus for [R] attacks — OK.
- B45 `DiscardOpponentActiveToolsAndDiscardSelf` (Klefki): requires opponent Active holding a Tool;
  discards Tools, resolves any resulting KO from lost Tool-HP, then discards Klefki itself (not scored as
  a KO) — OK.
- B46 `DiscardRandomEnergyFromOpponentActiveOnEvolve` (Crawdaunt): on-evolve, random from opponent Active — OK.
- B47 `DiscardTopCardOpponentDeck` (Chandelure) — OK.
- B48 `DoubleGrassEnergy` (Serperior — Jungle Totem): resolved through the type/energy-counting chokepoint;
  "doesn't stack" is enforced by the accessor treating presence as boolean, not summing multiple
  Serperior — OK (interacts with the already-known #14 Ogerpon ex question, not re-reported).
- B49 `DrawCardsOnEvolve{2}` (Sylveon ex): on-evolve `[DrawCard,Noop]` — OK.
- B51/B52 `DualType` (Rapid Strike/Single Strike Urshifu): read through the single
  `pokemon_energy_types`/`pokemon_is_type` chokepoint used by Weakness/type-boost/retreat checks — OK.
- B54 `EndFirstTurnAttachEnergyToSelf{Lightning}` (Zeraora) — OK.
- B56 `EndTurnHealSelfIfActive{20}` (Snorlax ex) — OK, same `on_end_turn` slot as B55.
- B57 `HealActiveTypedOnBenchFromHand{Grass,20}` (Poltchageist): bench-from-hand trigger, only offered
  when the Active is damaged and the right type — OK.
- B60/B61 — see B59 above (same mechanic, different amount/type filter).
- B63 `HealOneYourPokemon{30,require_tool_attached:true}` (Sylveon) — OK, same as B62.
- B64 `HealOneYourPokemonExAndDiscardRandomEnergy{60}` (Arboliva): filtered to damaged ex holding Energy — OK.
- B65 `HealSelfOnZoneAttach{Psychic,20}` (Cresselia ex) — OK.
- B68 `ImmuneToStatusConditions{Some(Asleep)}` (Hoothoot) — OK, same chokepoint as B67.
- B70 `IncreaseDamageForEvolutionsFromBench{Poliwhirl,40}` (Politoed): Bench-only, keyed on the target's
  `evolves_from` — OK.
- B71 `IncreaseDamageForTwoTypesInPlay{Psychic,Metal,30}` (Aegislash): active-to-active only — OK.
- B73 `IncreaseDamageIfArceusInPlay{30}` (Carnivine/Tyranitar): active-to-active only, Arceus check on
  attacker's own side — OK.
- B74 `IncreaseDamageWhenRemainingHpAtMost{60,50}` (Quaquaval): re-evaluated per hit off current HP — OK.
- B75 `IncreaseHpForTypeInPlay{Grass,20}` (Lilligant): materialized via `refresh_hp_bonuses_all`, removed
  immediately if the source leaves play (documented and relied on by the wave-based knockout loop) — OK.
- B76/B77 `IncreaseHpPerAttachedEnergy` (Reuniclus P; Serperior G) — OK.
- B80 `InfiltratingInspection` (Misdreavus): bench-from-hand trigger; reveal is a no-op for the
  full-information search bots by the same deliberate design as B82/83 — OK.
- B82/B83 `LookAtTopCardOfDeck` (Porygon; Unown CHECK): deliberately empty mutation (info-only, engine has
  no hidden-info model), `either_player` correctly widens the "is there a top card" gate — OK.
- B85 `LuxuryCoin` / B155 `VictoryStar` (Gholdengo; Victini): both explicitly cap at 1 use **per player per
  turn**, matching the card text's own "can't use more than 1 ... Ability each turn" override of the
  general per-Pokémon rule; tracked in dedicated per-player arrays, reset each turn — OK, correctly an
  intentional exception to "once per turn is per Pokémon."
- B86 `MoveAllTypedEnergyFromBenchToActive{Psychic}` (Lunala ex): requires a Benched [P] Pokémon holding
  [P] Energy — OK.
- B87 `MoveAllTypedEnergyFromYourPokemonToSelf{Darkness}` (Tyranitar): requires *another* Pokémon holding
  the Energy (self-move would be a no-op) — OK.
- B88 `MoveAllTypedEnergyToBenchOnKnockout{Fighting}` (Passimian ex) — OK, same gate as B35/36/37.
- B89 `MoveDamageFromOneYourPokemonToThisPokemon` (Dusknoir — Shadow Void): correctly **not** bounded to
  once/turn (matches "as often as you like"), contrast with B92 (F3) — OK.
- B90 `MoveFixedDamageFromActiveToThisBenched{30}` (Brambleghast): Bench-only, requires Active has ≥30
  damage, moves counters (not a heal, so it isn't blocked by Heal Block) — OK.
- B93 `NoOpponentStadiumInActive` (Snorlax — Massive Body) / B94 `NoOpponentSupportInActive` (Gengar ex):
  both read through the standard ability-mechanic check at the Stadium/Supporter play site — OK.
- B96-B100 `NoRetreatCost` variants (Heatran/Rotom Arceus-gated; Tatsugiri→Dondozo; Wimpod first-turn;
  Latios Latias-gated; Alolan Raichu Stadium-gated): all resolved through the same
  `has_no_retreat_cost_ability`/condition-holds pair — OK.
- B101 `NoRetreatIfHasEnergy` (Giratina): zero cost while any Energy attached — OK.
- B102 `OpponentShuffleHandAndDrawOnEvolve` (Polteageist): reuses the Mars Supporter effect, on-evolve — OK.
- B106 `PreventAllDamageAndEffectsOnEvolve{1}` (Samurott): on-evolve, adds the same
  `CardEffect::PreventAllDamageAndEffects` used elsewhere for 1-turn protections — OK.
- B108 `PreventAllHealing` (Claydol): single chokepoint (`heal_pokemon`/`heal_each_pokemon`), symmetric — OK.
- B109 `PreventAttackEffects` (Regice): resolved at `prevents_attack_effects`, damage itself untouched,
  only attack *effects* — OK.
- B110 `PreventDamageWhileBenched` (Wartortle): gated on `is_from_active_attack` so Ability/Poison damage
  still lands on the Bench — OK.
- B111 `PreventFirstAttack` (Mimikyu ex — Disguise): one-shot `prevent_first_attack_damage_used` flag — OK.
- B112 `PreventOpponentActiveEvolution` (Aerodactyl ex): checked at the evolve-generation site — OK.
- B114/B115 `PutCardsFromDiscardToHandOnEvolve` (Delcatty PlayerChoosesOne; Galarian Perrserker
  RandomCards(2)): on-evolve, matches each printing's exact wording (player choice vs. random) — OK.
- B117 `RandomEvolutionFromDeck{OnEnergyZoneAttachToSelf}` (Porygon2): resolved when the `Attach` action
  is forecast, so it's a visible branch rather than a hidden mutation — OK.
- B118 `RandomStatusConditionToOpponentActive` (Dustox): draws only from conditions not already on the
  target — OK.
- B119-B121 `ReduceAttackCost` (Abomasnow Arceus-gated; Cherubi Tool-gated; Iron Valiant Future-Pokémon):
  all resolved in `get_attack_cost` per their distinct `scope` — OK.
- B122 `ReduceDamageAtFullHp{40}` (Eiscue): re-checked per hit against current vs. max HP, opponent-only — OK.
- B126-B128 `ReduceDamageFromTypedAttackers` (Piloswine/Mamoswine/Azumarill vs Fire/Water; Staraptor vs
  Fighting): gated on the attacker's own type(s) — OK.
- B130 `ReduceOpponentActiveDamage{20}` (Luxray): requires holder Active — OK.
- B131 `ReduceOwnRetreatCostIfAnotherSameNameInPlay{2}` (Beldum): keyed on the holder's own name, requires
  a second copy in play — OK.
- B132 `ReduceRetreatCostOfYourActiveBasicFromBench{1}` (Shaymin): Bench-only, Basic-Active-only — OK.
- B134 `RemoveRandomSpecialConditionFromActive` (Blissey): requires the Active actually have a condition — OK.
- B135 `RevealRandomOpponentHandCard` (T.R. Kecleon): requires non-empty opponent hand — OK.
- B136/B137 `SearchRandomCardFromDeck` (Shiinotic Pokémon; Ambipom Tool): gated on a matching card existing
  in the deck (`deck_has_searchable_card`) — matches the "blocked only when visibly impossible" rule; no
  new blocking-rule gap found here.
- B138 `SleepOnZoneAttachToSelfWhileActive` (Komala/Slaking): only while holder Active, on Zone-attach to
  itself — OK.
- B141 `StartTurnRandomPokemonToHand{Psychic}` (Meloetta): start-of-turn, Active-only — OK.
- B144 `SwitchActiveTypedWithBench{Metal}` (Revavroom) — OK, same as B143.
- B145 `SwitchActiveUltraBeastWithBench` (Celesteela): both source and a Benched target must be Ultra
  Beasts — OK.
- B146 `SwitchDamagedOpponentBenchToActive` (Umbreon ex — Dark Chase): requires holder Active and a
  damaged opponent Bench target — OK.
- B147-B149 `SwitchOutOpponentActiveToBench` (Pidgeot any; Swellow Basic-only; Vaporeon ex Active-only):
  all three printed variants correctly distinguished by `require_active`/`require_opponent_active_basic` — OK.
- B150 `SwitchThisBenchWithActive` (Solgaleo ex — Rising Road): Bench-only — OK.
- B152 `ToolCapacity{2}` (Revavroom — Dual Customization): read through the single Tool-attach-limit
  accessor in `tools.rs` — OK.
- B153/B154 `UnownGuard`/`UnownPower`: self-referential "another Unown with a different title" gate
  correctly excludes two GUARD (or two POWER) Unown from enabling each other; board-wide sum stacks
  multiple holders — OK.
- B156 `VictreebelFragranceTrap` (Victreebel): requires holder Active and an opponent Benched **Basic** — OK.
