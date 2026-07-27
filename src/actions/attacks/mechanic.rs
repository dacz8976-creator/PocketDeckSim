use crate::{
    effects::{CardEffect, TurnEffect},
    models::{EnergyType, StatusCondition},
};

#[derive(Debug, Clone, PartialEq)]
pub enum BenchSide {
    YourBench,
    OpponentBench,
    BothBenches,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CopyAttackSource {
    OpponentActive,
    OpponentInPlay,
    OwnBenchNonEx,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Mechanic {
    SelfHeal {
        amount: u32,
    },
    HealOneYourPokemon {
        amount: u32,
    },
    HealOneYourBenchedPokemon {
        amount: u32,
    },
    HealAllYourPokemon {
        amount: u32,
    },
    CoinFlipSelfHeal {
        amount: u32,
    },
    SearchToHandByEnergy {
        energy_type: EnergyType,
    },
    SearchToBenchByName {
        name: String,
    },
    SearchToBenchBasic,
    SearchRandomPokemonToHand,
    SearchToHandByEvolvesFrom {
        name: String,
    },
    SearchToHandSupporterCard,
    InflictStatusConditions {
        conditions: Vec<StatusCondition>,
        target_opponent: bool,
    },
    InflictStatusConditionsOnBothActive {
        conditions: Vec<StatusCondition>,
    },
    ChanceStatusAttack {
        condition: StatusCondition,
    },
    /// Deal damage, then let the player choose one of these Special Conditions to
    /// inflict on the opponent's Active Pokémon (e.g. Dustox's Select Powder).
    ChooseStatusToInflict {
        options: Vec<StatusCondition>,
    },
    DamageAllOpponentPokemon {
        damage: u32,
    },
    DiscardRandomGlobalEnergy {
        count: usize,
    },
    RandomDamageToOpponentPokemonPerSelfEnergy {
        energy_type: EnergyType,
        damage_per_hit: u32,
    },
    DiscardEnergyFromOpponentActive,
    CoinFlipDiscardEnergyFromOpponentActive,
    DiscardOpponentActiveToolsBeforeDamage,
    ExtraDamageIfEx {
        extra_damage: u32,
    },
    /// Extra damage if the opponent's Active Pokémon is one of the listed types
    /// (e.g. Hawlucha's "is a [D] Pokémon", Scovillain's "is a [G] or [M] Pokémon").
    ExtraDamageIfDefenderType {
        energy_types: Vec<EnergyType>,
        extra_damage: u32,
    },
    /// Extra damage depending on the opponent's Active Pokémon's stage:
    /// `evolution: false` → "is a Basic Pokémon" (fossils count as Basic),
    /// `evolution: true` → "is an Evolution Pokémon".
    ExtraDamageIfDefenderStage {
        evolution: bool,
        extra_damage: u32,
    },
    /// Seviper's Fateful Fang: extra damage if the opponent's Active Pokémon has this exact name.
    ExtraDamageIfDefenderNamed {
        name: String,
        extra_damage: u32,
    },
    ExtraDamageIfOpponentHasSpecialCondition {
        extra_damage: u32,
    },
    ExtraDamageIfSupportPlayedThisTurn {
        extra_damage: u32,
    },
    SelfDamage {
        amount: u32,
    },
    CoinFlipExtraDamage {
        extra_damage: u32,
    },
    CoinFlipExtraDamageOrSelfDamage {
        extra_damage: u32,
        self_damage: u32,
    },
    CoinFlipSelfDamage {
        self_damage: u32,
    },
    ExtraDamageForEachHeads {
        include_fixed_damage: bool,
        damage_per_head: u32,
        num_coins: usize,
    },
    DiscardSelfEnergyPerHeadsExtraDamage {
        num_coins: usize,
        energy_type: EnergyType,
        damage_per_discarded_energy: u32,
    },
    CoinFlipNoEffect,
    SelfDiscardEnergy {
        energies: Vec<EnergyType>,
    },
    SelfDiscardEnergyAndInflictStatus {
        energies: Vec<EnergyType>,
        conditions: Vec<StatusCondition>,
    },
    SelfDiscardEnergyAndCardEffect {
        energies: Vec<EnergyType>,
        effect: CardEffect,
        duration: u8,
    },
    ExtraDamageIfExtraEnergy {
        required_extra_energy: Vec<EnergyType>,
        extra_damage: u32,
    },
    /// Extra damage if enough different Energy types are attached. `all_in_play: false` checks
    /// only this Pokémon's attached Energy; `true` checks all of your Pokémon in play
    /// (Grafaiai's Colorful Attack).
    ExtraDamageIfDifferentEnergyTypesAttached {
        minimum_types: usize,
        extra_damage: u32,
        all_in_play: bool,
    },
    ExtraDamageIfTypeEnergyInPlay {
        energy_type: EnergyType,
        minimum_count: usize,
        extra_damage: u32,
    },
    /// Medicham's "Psykick" / Mega Medicham ex's "Chakra Fist": extra damage if the attacking
    /// Pokémon has any Energy of `energy_type` attached. (Chakra Fist additionally shares Sawk's
    /// "isn't affected by any effects on your opponent's Active Pokémon" clause, which is detected
    /// separately from the attack's effect text in `hooks::modify_damage`.)
    ExtraDamageIfSelfHasTypeEnergy {
        energy_type: EnergyType,
        extra_damage: u32,
    },
    ExtraDamageIfStadiumInPlay {
        extra_damage: u32,
    },
    ExtraDamageIfBothHeads {
        extra_damage: u32,
    },
    DirectDamage {
        damage: u32,
        bench_only: bool,
    },
    DamageAndTurnEffect {
        effect: TurnEffect,
        duration: u8,
    },
    SelfChargeActive {
        energies: Vec<EnergyType>,
    },
    CoinFlipSelfChargeActive {
        energies: Vec<EnergyType>,
    },
    ChargeYourTypeAnyWay {
        energy_type: EnergyType,
        count: usize,
    },
    // Fairly unique mechanics
    /// Manaphy's Oceanic Gift / Carbink's Glittering Gift: choose 2 of your Benched Pokémon and
    /// attach an Energy of the given type to each.
    AttachEnergyFromZoneToTwoBenched {
        energy_type: EnergyType,
    },
    PalkiaExDimensionalStorm,
    MegaKangaskhanExDoublePunchingFamily,
    MoltresExInfernoDance,
    CelebiExPowerfulBloom,
    CoinFlipPerSpecificEnergyType {
        energy_type: EnergyType,
        include_fixed_damage: bool,
        damage_per_heads: u32,
    },
    MagikarpWaterfallEvolution,
    CoinFlipToBlockAttackNextTurn,
    MoveAllEnergyTypeToBench {
        energy_type: EnergyType,
    },
    MoveFixedEnergyTypeToBench {
        energy_type: EnergyType,
        amount: u32,
    },
    ChargeBench {
        energies: Vec<EnergyType>,
        target_benched_type: Option<EnergyType>,
    },
    /// Ho-Oh ex's Phoenix Turbo: deal `fixed_damage`, then attach each of these Energies to your
    /// Benched Basic Pokémon "in any way you like" (each Energy is placed independently, so all on
    /// one Pokémon is allowed). Fossils count as Basic. If there is no Benched Basic Pokémon the
    /// Energy simply fizzles; the damage is still dealt.
    AttachEnergiesAnyWayToBenchedBasic {
        energies: Vec<EnergyType>,
    },
    VaporeonHyperWhirlpool,
    ConditionalBenchDamage {
        required_extra_energy: Vec<EnergyType>,
        bench_damage: u32,
        num_bench_targets: usize,
        opponent: bool,
    },
    ExtraDamageForEachHeadsWithStatus {
        include_fixed_damage: bool,
        damage_per_head: u32,
        num_coins: usize,
        status: StatusCondition,
    },
    DamageAndMultipleCardEffects {
        opponent: bool,
        effects: Vec<CardEffect>,
        duration: u8,
    },
    DamageReducedBySelfDamage,
    ExtraDamagePerTrainerInOpponentDeck {
        damage_per_trainer: u32,
    },
    ExtraDamagePerSupporterInDiscard {
        damage_per_supporter: u32,
    },
    ExtraDamagePerPokemonTypeInDiscard {
        energy_type: EnergyType,
        damage_per_pokemon: u32,
    },
    ExtraDamagePerPokemonInDiscard {
        damage_per_pokemon: u32,
    },
    ExtraDamagePerOwnPoint {
        damage_per_point: u32,
    },
    ExtraDamageIfCardInDiscard {
        card_name: String,
        extra_damage: u32,
    },
    DamageUnaffectedByWeakness,
    /// Sawk's Brick Break: fixed damage whose value "isn't affected by any effects on your
    /// opponent's Active Pokémon." The bypass itself is handled in `hooks::modify_damage` and the
    /// defender-prevention path via the attack's effect text; this variant just routes the attack
    /// as ordinary active damage (like `DamageUnaffectedByWeakness`).
    DamageUnaffectedByOpponentActiveEffects,
    DelayedSpotDamage {
        amount: u32,
    },
    // End Unique mechanics
    DamageAndCardEffect {
        opponent: bool,
        effect: CardEffect,
        duration: u8,
        coin_flip: bool, // false = always apply, true = apply on heads
    },
    CoinFlipNoDamageOrDamageAndCardEffect {
        opponent: bool,
        effect: CardEffect,
        duration: u8,
    },
    DrawCard {
        amount: u8,
    },
    SelfDiscardAllEnergy,
    SelfDiscardAllTypeEnergy {
        energy_type: EnergyType,
    },
    SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon {
        energy_type: EnergyType,
        damage: u32,
    },
    SelfDiscardRandomEnergy,
    AlsoBenchDamage {
        opponent: bool,
        damage: u32,
        must_have_energy: bool,
    },
    AlsoChoiceBenchDamage {
        opponent: bool,
        damage: u32,
    },
    /// Extra damage if a Pokémon has damage on it. `benched: false` checks the chosen side's
    /// Active Pokémon; `benched: true` checks whether ANY of that side's Benched Pokémon are
    /// damaged (Drampa's Berserk).
    ExtraDamageIfHurt {
        extra_damage: u32,
        opponent: bool,
        benched: bool,
    },
    ExtraDamageIfUndamaged {
        extra_damage: u32,
    },
    ExtraDamageIfStage2OnBench {
        extra_damage: u32,
    },
    ExtraDamageIfPokemonOnBench {
        pokemon_name: String,
        extra_damage: u32,
    },
    DamageEqualToSelfDamage,
    ExtraDamageEqualToSelfDamage,
    /// "If any of your (\[type\]) Pokémon were Knocked Out by damage from an attack during your
    /// opponent's last turn, ..." — the vengeance family. `energy_type` filters which knockouts
    /// qualify (Zarude's Dark Vengeance counts only [D] Pokémon); `conditions` are Special
    /// Conditions inflicted on the opponent's Active Pokémon when the condition holds (Lapras's
    /// Raging Freeze / Toxtricity's Vengeful Shock Paralyze; may be combined with extra damage).
    ExtraDamageIfKnockedOutLastTurn {
        extra_damage: u32,
        energy_type: Option<EnergyType>,
        conditions: Vec<StatusCondition>,
    },
    ExtraDamageIfAttackUsedDuringOwnLastTurn {
        attack_name: String,
        extra_damage: u32,
    },
    DamagePerAttackUsedThisGame {
        attack_name: String,
        damage_per_use: u32,
    },
    ExtraDamageIfMovedFromBench {
        extra_damage: u32,
    },
    ExtraDamageIfEvolvedThisTurn {
        extra_damage: u32,
    },
    /// Damage scaling with the number of Benched Pokémon on `bench_side`, optionally filtered by
    /// `energy_type` and/or by exact Pokémon `names` (Wishiwashi ex's School Storm counts benched
    /// "Wishiwashi" and "Wishiwashi ex"; Nidoqueen's Lovestrike counts benched "Nidoking").
    BenchCountDamage {
        include_fixed_damage: bool,
        damage_per: u32,
        energy_type: Option<EnergyType>,
        names: Option<Vec<String>>,
        bench_side: BenchSide,
    },
    EvolutionBenchCountDamage {
        include_fixed_damage: bool,
        damage_per: u32,
    },
    ExtraDamagePerEnergy {
        include_fixed_damage: bool,
        opponent: bool,
        damage_per_energy: u32,
    },
    ExtraDamagePerEnergyType {
        damage_per_type: u32,
    },
    ExtraDamagePerRetreatCost {
        damage_per_energy: u32,
    },
    DamagePerEnergyAll {
        opponent: bool,
        damage_per_energy: u32,
    },
    /// Choose 1 of the opponent's Pokémon; deal damage_per_energy × (energy on that Pokémon).
    DamageToAnyOpponentPerTargetEnergy {
        damage_per_energy: u32,
    },
    DiscardHandCards {
        count: usize,
    },
    ExtraDamagePerSpecificEnergy {
        energy_type: EnergyType,
        damage_per_energy: u32,
    },
    ExtraDamagePerSpecificEnergyAllYours {
        energy_type: EnergyType,
        damage_per_energy: u32,
    },
    /// Extra damage if a Pokémon Tool is attached: to this Pokémon (`opponent: false`) or to the
    /// opponent's Active Pokémon (`opponent: true`, Rotom's Assault Laser).
    ExtraDamageIfToolAttached {
        extra_damage: u32,
        opponent: bool,
    },
    RecoilIfKo {
        self_damage: u32,
    },
    ShuffleOpponentActiveIntoDeck,
    KnockBackOpponentActive,
    /// Random spread damage attack (e.g., Draco Meteor, Spurt Fire)
    /// Always targets opponent's active + bench. Optionally includes own bench.
    RandomSpreadDamage {
        times: usize,
        damage_per_hit: u32,
        include_own_bench: bool,
    },
    FlipUntilTailsDamage {
        damage_per_heads: u32,
    },
    /// Like `FlipUntilTailsDamage`, but the attack's `fixed_damage` is dealt as a base and each
    /// heads adds `damage_per_heads` on top (e.g. "does 30 more damage for each heads").
    FlipUntilTailsBonusDamage {
        damage_per_heads: u32,
    },
    DirectDamageIfDamaged {
        damage: u32,
    },
    /// Kingambit's Overlord's Blade: the attack's `fixed_damage` plus `damage_per_ko` for each
    /// time the attacking player's own Pokémon have been Knocked Out this game. A comeback
    /// mechanic — it scales with how badly you are losing on board, not with points scored.
    ExtraDamagePerOwnKnockoutThisGame {
        damage_per_ko: u32,
    },
    AttachEnergyToBenchedBasic {
        energy_type: EnergyType,
    },
    DamageAndDiscardOpponentDeck {
        discard_count: usize,
    },
    MegaAmpharosExLightningLancer,
    OminousClaw,
    DarknessClaw,
    BlockBasicAttack,
    SwitchSelfWithBench,
    MaySwitchSelfWithBench,
    SelfHealIfStadiumInPlay {
        amount: u32,
    },
    InflictStatusIfStadiumInPlay {
        status: StatusCondition,
    },
    CopyAttack {
        source: CopyAttackSource,
        require_attacker_energy_match: bool,
    },
    SelfAsleepAndHeal {
        amount: u32,
    },
    FlipCoinsBenchDamagePerHead {
        num_coins: usize,
        bench_damage_per_head: u32,
    },
    ExtraDamageIfSelfHpAtMost {
        threshold: u32,
        extra_damage: u32,
    },
    ExtraDamageIfOpponentHpMoreThanSelf {
        extra_damage: u32,
    },
    ExtraDamageIfOpponentActiveHasAbility {
        extra_damage: u32,
    },
    /// Honchkrow – Evil Admonition: extra damage for each of the opponent's
    /// Pokémon in play (active and bench) that has an Ability.
    ExtraDamagePerOpponentPokemonWithAbility {
        damage_per: u32,
    },
    CoinFlipShuffleRandomOpponentHandCardIntoDeck,
    /// Teal Mask Ogerpon ex – Energized Leaves:
    /// If total energy on both Active Pokémon ≥ threshold, deal extra_damage more.
    ExtraDamageIfCombinedActiveEnergyAtLeast {
        threshold: usize,
        extra_damage: u32,
    },
    /// Hearthflame Mask Ogerpon – Hearthflame Dance:
    /// Flip a coin. If heads, take `count` energy of `energy_type` from your Energy Zone
    /// and attach them to 1 of your Benched Pokémon.
    CoinFlipChargeBench {
        energies: Vec<EnergyType>,
        target_benched_type: Option<EnergyType>,
    },
    /// Wellspring Mask Ogerpon – Wellspring Dance:
    /// Flip a coin. If heads, this attack also does `damage` to 1 of the chosen player's
    /// Benched Pokémon (opponent = true → opponent's bench).
    CoinFlipAlsoChoiceBenchDamage {
        opponent: bool,
        damage: u32,
    },
    /// Extra damage if the opponent's Active Pokémon is affected by the given Special Condition
    /// (Venoshock's Poisoned, Hatterene's Confused, Breloom's Asleep, Heatmor's Burned).
    ExtraDamageIfDefenderStatus {
        status: StatusCondition,
        extra_damage: u32,
    },
    /// Discard the top card of the attacker's own deck after dealing damage.
    DiscardTopSelfDeck,
    /// Tiered coin flip damage: flip `num_coins` coins and deal fixed_damage +
    /// extra_damage_by_heads[heads_count] total damage.
    TieredCoinFlipDamage {
        num_coins: usize,
        extra_damage_by_heads: Vec<u32>,
    },
    /// First attack after coming into play: conditionally apply a turn effect (e.g. Flutter Mane).
    FirstAttackBonusTurnEffect {
        effect: TurnEffect,
        duration: u8,
    },
    /// First attack after coming into play: conditionally deal extra damage and inflict status (e.g. Iron Bundle).
    FirstAttackBonusDamageAndStatus {
        extra_damage: u32,
        conditions: Vec<StatusCondition>,
    },
    /// Growlithe – Puppy Pile: deal damage_per × (number of own Pokémon in play and hand
    /// that have an attack named `attack_name`).
    DamagePerOwnPokemonWithAttackName {
        attack_name: String,
        damage_per: u32,
    },
    /// Emolga (Windup Thunder) / Dedenne ex (Dede-Circuit):
    /// deal `damage_per` damage for each Pokémon Tool attached to any of your
    /// Pokémon in play (active + bench).
    DamagePerOwnToolAttached {
        damage_per: u32,
    },
    /// Ludicolo / Luvdisc / Grumpig: extra damage if the hand size of the chosen player
    /// (`opponent: true` → your opponent's hand) is exactly one of `counts`.
    ExtraDamageIfHandSizeIn {
        counts: Vec<u32>,
        opponent: bool,
        extra_damage: u32,
    },
    /// Tyrantrum's Tyrannical Fang: extra damage if you have fewer Pokémon in play than your
    /// opponent.
    ExtraDamageIfFewerPokemonInPlay {
        extra_damage: u32,
    },
    /// Buzzwole's Ground Beat: extra damage if your opponent has gotten exactly `points` points.
    ExtraDamageIfOpponentPointsExactly {
        points: u8,
        extra_damage: u32,
    },
    /// Scrafty's Crush the Weak: extra damage if this Pokémon has more Energy attached than the
    /// opponent's Active Pokémon.
    ExtraDamageIfMoreEnergyThanDefender {
        extra_damage: u32,
    },
    /// Enamorus's Smitten Strike: extra damage if this Pokémon and the opponent's Active Pokémon
    /// each have at least `minimum_each` Energy of one common type attached.
    ExtraDamageIfSharedEnergyType {
        minimum_each: usize,
        extra_damage: u32,
    },
    /// Ting-Lu's Arrogant Impact: "If this Pokémon's remaining HP is N or less, this attack does
    /// nothing."
    NoDamageIfSelfHpAtMost {
        threshold: u32,
    },
    /// Flutter Mane's Hexing Flight: "If this Pokémon didn't move from the Bench to the Active
    /// Spot this turn, this attack does nothing."
    NoDamageUnlessMovedFromBench,
    /// Bronzong's Psychic Resonance: extra damage if the opponent has any Pokémon of this type in
    /// play (Active or Bench).
    ExtraDamageIfOpponentHasTypeInPlay {
        energy_type: EnergyType,
        extra_damage: u32,
    },
    /// Wobbuffet's Reply Strongly: extra damage if this Pokémon was damaged by an attack during
    /// the opponent's last turn while it was in the Active Spot.
    ExtraDamageIfDamagedByAttackLastTurn {
        extra_damage: u32,
    },
}
