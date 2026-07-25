use crate::models::EnergyType;

/// The card names that satisfy "if you have Arceus or Arceus ex in play". Pokémon ex have their
/// own name in this game, so both spellings have to be listed explicitly.
pub const ARCEUS_NAMES: &[&str] = &["Arceus", "Arceus ex"];

/// Which Pokémon a [`AbilityMechanic::NoRetreatCost`] ability frees from its Retreat Cost.
#[derive(Debug, Clone, PartialEq)]
pub enum NoRetreatCostTarget {
    /// "this Pokémon has no Retreat Cost" — only the Pokémon that has the Ability.
    ThisPokemon,
    /// "your Active Pokémon has no Retreat Cost" — whichever Pokémon is Active, while the Pokémon
    /// with the Ability is anywhere in play (Active or Benched).
    YourActive,
    /// "your Active <name> has no Retreat Cost" — as [`Self::YourActive`], but only when the Active
    /// Pokémon has this exact name.
    YourActiveNamed(&'static str),
}

/// Extra condition that must hold for a [`AbilityMechanic::NoRetreatCost`] ability to apply.
#[derive(Debug, Clone, PartialEq)]
pub enum NoRetreatCostCondition {
    /// Unconditional.
    Always,
    /// You have a Pokémon with one of these exact names in play.
    NamedPokemonInPlay(&'static [&'static str]),
    /// Any Stadium card is in play (Stadiums are shared, so either player's counts).
    StadiumInPlay,
    /// It is your first turn.
    YourFirstTurn,
}

/// Who the retaliation damage of [`AbilityMechanic::DamageOnKnockoutInActive`] hits.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum KnockoutDamageTarget {
    /// Only the Pokémon whose attack caused the knockout (Pyukumuku's Innards Out).
    Attacker,
    /// Every one of the opponent's in-play Pokémon, Active and Benched (Spiritomb's Final Scream).
    EachOpponentPokemon,
}

/// Who benefits from an [`AbilityMechanic::ReduceAttackCost`] ability, and what has to be true for
/// it to work. Every one of these discounts the *Active* attacker's attack; they differ in where
/// the granting Pokémon sits and in the enabling condition.
#[derive(Debug, Clone, PartialEq)]
pub enum AttackCostReductionScope {
    /// Future System: the ability holder may be anywhere in play, and the discount applies while
    /// your Active Pokémon is a Future Pokémon.
    YourFuturePokemon,
    /// Vigor Link (Abomasnow A2a 021): the ability holder itself, while you have Arceus or
    /// Arceus ex in play.
    SelfIfArceusInPlay,
    /// En-fruits-iastic (Cherubi A4 023 / A4b 025 / A4b 026): the ability holder itself, while it
    /// has a Pokémon Tool attached.
    SelfIfToolAttached,
}

#[derive(Debug, Clone, PartialEq)]
pub enum AbilityMechanic {
    VictreebelFragranceTrap,
    HealAllYourPokemon {
        amount: u32,
    },
    HealOneYourPokemon {
        amount: u32,
    },
    HealOneYourPokemonExAndDiscardRandomEnergy {
        amount: u32,
    },
    DamageOneOpponentPokemon {
        amount: u32,
    },
    IncreaseDamageIfArceusInPlay {
        amount: u32,
    },
    DamageOpponentActiveIfArceusInPlay {
        amount: u32,
    },
    SwitchDamagedOpponentBenchToActive,
    SwitchThisBenchWithActive,
    SwitchActiveTypedWithBench {
        energy_type: EnergyType,
    },
    SwitchActiveUltraBeastWithBench,
    MoveTypedEnergyFromBenchToActive {
        energy_type: EnergyType,
    },
    /// Lunala ex's Psychic Connect: "Once during your turn, you may move all [energy_type] Energy
    /// from 1 of your Benched [energy_type] Pokémon to your Active Pokémon." Unlike
    /// `MoveTypedEnergyFromBenchToActive`, all of the chosen Pokémon's matching Energy moves at
    /// once, it is once per turn, and the Active Pokémon may be any type.
    MoveAllTypedEnergyFromBenchToActive {
        energy_type: EnergyType,
    },
    AttachEnergyFromZoneToActiveTypedPokemon {
        energy_type: EnergyType,
    },
    AttachEnergyFromZoneToYourTypedPokemon {
        energy_type: EnergyType,
    },
    AttachEnergyFromZoneToSelf {
        energy_type: EnergyType,
        amount: u32,
    },
    AttachEnergyFromZoneToSelfAndEndTurn {
        energy_type: EnergyType,
    },
    AttachEnergyFromZoneToSelfAndDamage {
        energy_type: EnergyType,
        amount: u32,
        self_damage: u32,
    },
    DamageOpponentActiveOnZoneAttachToSelf {
        energy_type: EnergyType,
        amount: u32,
        only_turn_energy: bool,
    },
    AttachEnergyFromDiscardToSelfAndDamage {
        energy_type: EnergyType,
        self_damage: u32,
    },
    ReduceDamageFromAttacks {
        amount: u32,
    },
    ReduceOpponentActiveDamage {
        amount: u32,
    },
    /// Thick Fat (Mamoswine, Piloswine, Azumarill) and Defensive Whirlwind (Staraptor):
    /// "This Pokémon takes -`amount` damage from attacks from [X] (or [Y]) Pokémon."
    ///
    /// Parameterised on both the amount (Thick Fat prints at -30 and -20) and the list of
    /// attacker Energy types (Thick Fat is `[R]`/`[W]`, Defensive Whirlwind is `[F]`), so a single
    /// variant covers the whole family. Passive: unlike `ReduceDamageFromAttacks` this cannot be
    /// expressed as a context-free `CardEffect`, because whether it applies depends on the
    /// *attacker*, so it is resolved in `modify_damage`.
    ReduceDamageFromTypedAttackers {
        energy_types: Vec<EnergyType>,
        amount: u32,
    },
    /// Resilience Link (Raichu, Magnezone): "If you have Arceus or Arceus ex in play, this Pokémon
    /// takes -`amount` damage from attacks." The defensive mirror of
    /// `IncreaseDamageIfArceusInPlay`; both share the `has_arceus_in_play` board check. Passive.
    ReduceDamageIfArceusInPlay {
        amount: u32,
    },
    /// Ice Face (Eiscue): "If this Pokémon has full HP, it takes -`amount` damage from attacks from
    /// your opponent's Pokémon." Passive; the condition is re-evaluated per hit, so the shield is
    /// gone as soon as any damage sticks.
    ReduceDamageAtFullHp {
        amount: u32,
    },
    /// GUARD (Unown A4 084): "This Ability works if you have any Unown in play with an Ability
    /// other than GUARD. All of your Pokémon take -`amount` damage from attacks from your
    /// opponent's Pokémon."
    ///
    /// Board-wide rather than self-scoped, and self-referential: the enabling condition is another
    /// in-play Unown whose printed Ability *title* is something other than GUARD (CHECK on A2a 034
    /// / A2a 078, POWER on A4 085). Two GUARD Unown therefore do not enable each other.
    UnownGuard {
        amount: u32,
    },
    IncreaseDamageWhenRemainingHpAtMost {
        amount: u32,
        hp_threshold: u32,
    },
    IncreaseDamageForTypeInPlay {
        energy_type: EnergyType,
        amount: u32,
    },
    IncreaseDamageForTwoTypesInPlay {
        energy_type_a: EnergyType,
        energy_type_b: EnergyType,
        amount: u32,
    },
    /// POWER (Unown A4 085): "This Ability works if you have any Unown in play with an Ability
    /// other than POWER. Attacks used by your Pokémon do +`amount` damage to your opponent's
    /// Active Pokémon."
    ///
    /// Board-wide rather than self-scoped, and self-referential: the enabling condition is an
    /// in-play Unown whose printed Ability *title* is something other than POWER (CHECK on
    /// A2a 034 / A2a 078, GUARD on A4 084). Two POWER Unown therefore do not enable each other.
    UnownPower {
        amount: u32,
    },
    /// Politoed's Lordly Cheering (A4 040): "As long as this Pokémon is on your Bench, attacks
    /// used by your Pokémon that evolve from `evolves_from` do +`amount` damage to your
    /// opponent's Active Pokémon." Only counts while the ability holder is Benched.
    IncreaseDamageForEvolutionsFromBench {
        evolves_from: &'static str,
        amount: u32,
    },
    /// Falinks' Coordinated Unit (B2 092 / B2 172): "If you have another Falinks in play, this
    /// Pokémon's attacks do +`damage_bonus` damage to your opponent's Active Pokémon, and this
    /// Pokémon takes -`damage_reduction` damage from attacks from your opponent's Pokémon."
    ///
    /// One ability with two self-scoped effects, both gated on the holder's controller having a
    /// *second* Pokémon with the same name in play.
    CoordinatedUnit {
        pokemon_name: &'static str,
        damage_bonus: u32,
        damage_reduction: u32,
    },
    StartTurnRandomPokemonToHand {
        energy_type: EnergyType,
    },
    SearchRandomPokemonFromDeck,
    MoveDamageFromOneYourPokemonToThisPokemon,
    DiscardOpponentActiveToolsAndDiscardSelf,
    PreventFirstAttack,
    ElectromagneticWall,
    InfiltratingInspection,
    DiscardTopCardOpponentDeck,
    CoinFlipToPreventDamage,
    /// Bastiodon's Guarded Grill / Hisuian Goodra's Securely Sheltered: if any damage is done to
    /// this Pokémon by attacks, flip a coin. If heads, this Pokémon takes `amount` less damage
    /// from that attack. Passive; handled like `CoinFlipToPreventDamage` via the
    /// abilities-as-effects pathway.
    CoinFlipToReduceDamage {
        amount: u32,
    },
    /// Ursaluna's Guts: if this Pokémon would be Knocked Out by damage from an attack, flip a
    /// coin. If heads, it is not Knocked Out and its remaining HP becomes 10.
    CoinFlipToSurviveKnockOut,
    /// Dusknoir's Fade into Darkness / Glimmora's Shattering Crystal: when this Pokémon is Knocked
    /// Out, flip a coin. If heads, the opponent gets no points for it.
    ///
    /// Distinct from `CoinFlipToSurviveKnockOut`: the Pokémon still dies and still leaves play,
    /// so on-knockout triggers, promotions and discards all resolve normally — only the point
    /// award is suppressed. Modelled as a probability split at forecast time (see
    /// `AttackOutcomes::split_with_point_denial`) so the search bots price the coin correctly
    /// rather than seeing an expected value; on heads the branch tags the doomed Pokémon with
    /// `CardEffect::DenyKnockoutPoints`, which `handle_knockouts` consumes.
    CoinFlipToDenyKnockoutPoints,
    /// Passimian ex's Offload Pass: if this Pokémon is in the Active Spot and is Knocked Out by
    /// damage from an opponent's attack, move all of its `energy_type` Energy to 1 of your Benched
    /// Pokémon (your choice). Passive; handled in the `on_knockout` hook.
    MoveAllTypedEnergyToBenchOnKnockout {
        energy_type: EnergyType,
    },
    /// Pyukumuku's Innards Out (`Attacker`, 50) and Spiritomb's Final Scream
    /// (`EachOpponentPokemon`, 10): "If this Pokémon is in the Active Spot and is Knocked Out by
    /// damage from an attack from your opponent's Pokémon, do `amount` damage to <target>."
    ///
    /// Passive; handled in the `on_knockout` hook. The retaliation is ability damage rather than
    /// attack damage, so it ignores Weakness and does not itself provoke counterattacks.
    DamageOnKnockoutInActive {
        amount: u32,
        target: KnockoutDamageTarget,
    },
    CheckupDamageToOpponentActive {
        amount: u32,
    },
    CheckupDamageToAllOpponentPokemon {
        amount: u32,
    },
    DiscardEnergyToIncreaseTypeDamage {
        discard_energy: EnergyType,
        attack_type: EnergyType,
        amount: u32,
    },
    PoisonOpponentActive,
    ConfuseOpponentActive,
    BurnOpponentActive,
    RemoveRandomSpecialConditionFromActive,
    HealActiveYourPokemon {
        amount: u32,
    },
    SwitchOutOpponentActiveToBench {
        require_active: bool,
    },
    BadDreamsEndOfTurn {
        amount: u32,
    },
    EndTurnDrawCardIfActive {
        amount: u32,
    },
    EndTurnHealSelfIfActive {
        amount: u32,
    },
    CoinFlipSleepOpponentActive,
    DiscardFromHandToDrawCard,
    ImmuneToStatusConditions,
    /// Passive ability shared by Teal Mask Ogerpon ex (Soothing Wind) and Comfey (Flower Shield):
    /// Each of your Pokémon that has the required Energy attached recovers from all Special
    /// Conditions and can't be affected by any Special Conditions.
    ///   - `energy_type: None`  → any energy (Ogerpon ex – Soothing Wind)
    ///   - `energy_type: Some(t)` → only the specified type (Comfey – Flower Shield, `[P]`)
    SoothingWind {
        energy_type: Option<EnergyType>,
    },
    NoOpponentSupportInActive,
    /// Snorlax's Massive Body: as long as this Pokémon is in the Active Spot, the opponent
    /// can't play any Stadium cards from their hand.
    NoOpponentStadiumInActive,
    DoubleGrassEnergy,
    PreventOpponentActiveEvolution,
    ReduceRetreatCostOfYourActiveBasicFromBench {
        amount: u32,
    },
    ReduceRetreatCostOfYourActiveTypedFromBench {
        energy_type: EnergyType,
        amount: u32,
    },
    NoRetreatIfHasEnergy,
    /// The passive "no Retreat Cost" family: Speed Link (Arceus in play), Fantastical Floating
    /// (Latias in play), Surge Surfer (a Stadium in play), Wimp Out (your first turn), Fluffy
    /// Flight (your Active Pokémon, unconditionally) and Retreat Directive (your Active Dondozo).
    ///
    /// Passive, so it is resolved in `hooks::retreat::get_retreat_cost`;
    /// `forecast_ability_by_mechanic` panics and `can_use_ability_by_mechanic` returns false.
    NoRetreatCost {
        target: NoRetreatCostTarget,
        condition: NoRetreatCostCondition,
    },
    PreventAllDamageFromEx,
    SleepOnZoneAttachToSelfWhileActive,
    IncreasePoisonDamage {
        amount: u32,
    },
    DrawCardsOnEvolve {
        amount: u32,
    },
    HealTypedPokemonOnEvolve {
        energy_type: EnergyType,
        amount: u32,
    },
    AttachEnergyFromZoneToActiveTypedOnEvolve {
        energy_type: EnergyType,
    },
    DamageOpponentActiveOnEvolve {
        amount: u32,
    },
    DiscardRandomEnergyFromOpponentActiveOnEvolve,
    CanEvolveIntoEeveeEvolution,
    CanEvolveOnFirstTurnIfActive,
    CounterattackDamage {
        amount: u32,
    },
    PoisonAttackerOnDamaged,
    IncreaseAttackCostForOpponentActive {
        amount: u32,
    },
    IncreaseRetreatCostForOpponentActive {
        amount: u32,
    },
    PreventDamageWhileBenched,
    IncreaseHpPerAttachedEnergy {
        energy_type: EnergyType,
        amount: u32,
    },
    /// Lilligant's Toughness Aroma (B1 018 / B1 329): "Each of your [`energy_type`] Pokémon gets
    /// +`amount` HP." Board-conditional, so — like Starting Plains' +20 HP for Basic Pokémon — it
    /// is materialised onto each Pokémon as a stored bonus by `State::refresh_hp_bonuses_all` and
    /// read back by `PlayedCard::get_effective_total_hp`.
    IncreaseHpForTypeInPlay {
        energy_type: EnergyType,
        amount: u32,
    },
    HealSelfOnZoneAttach {
        energy_type: EnergyType,
        amount: u32,
    },
    EndFirstTurnAttachEnergyToSelf {
        energy_type: EnergyType,
    },
    ProtectSelfNextTurnAfterAttackKnockout,
    MoveFixedDamageFromActiveToThisBenched {
        amount: u32,
    },
    /// "Once during your turn, when you put this Pokémon from your hand onto your Bench,
    /// you may switch it with your Active Pokémon. If you do, move all of your Energy
    /// in play to this Pokémon."
    LegendaryDrive,
    /// "Once during your turn, when you put this Pokémon from your hand onto your Bench,
    /// you may switch out your opponent's Active Pokémon to the Bench.
    /// (Your opponent chooses the new Active Pokémon.)"
    AncientRoar,
    /// "Attacks used by <someone> cost `amount` less [`energy_type`] Energy": Future System,
    /// Vigor Link (Abomasnow A2a 021) and En-fruits-iastic (Cherubi A4 023 / A4b 025 / A4b 026).
    /// `scope` says who is discounted and under what condition. Passive; resolved in
    /// `hooks::core::get_attack_cost`.
    ReduceAttackCost {
        energy_type: EnergyType,
        amount: u32,
        scope: AttackCostReductionScope,
    },
    /// Celebi's Time Recall: "Each of your evolved Pokémon can use any attack from its previous
    /// Evolutions. (You still need the necessary Energy to use each attack.)"
    /// Passive: while a Pokémon with this ability is in play, attack generation also offers the
    /// active evolved Pokémon the attacks from its previous evolutions (its under-cards).
    TimeRecall,
    /// Caterpie's Quick Growth: "At the end of your opponent's turn, if this Pokémon is in the
    /// Active Spot, put a random card from your deck that evolves from this Pokémon onto this
    /// Pokémon to evolve it."
    QuickGrowth,
}
