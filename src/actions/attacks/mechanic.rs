use crate::{
    effects::{CardEffect, TurnEffect},
    models::{EnergyType, StatusCondition, TrainerType},
};

#[derive(Debug, Clone, PartialEq)]
pub enum BenchSide {
    YourBench,
    OpponentBench,
    BothBenches,
}

/// Restriction applied when an attack asks its user to choose one Benched Pokémon for damage.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum BenchDamageFilter {
    Any,
    Damaged,
}

/// Which cards a hand-disruption attack is allowed to pick from the opponent's hand.
/// `Any` is the unrestricted "a random card" wording; the others restrict by Trainer type.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HandCardKind {
    Any,
    Item,
    Tool,
}

#[derive(Debug, Clone, PartialEq)]
pub enum CopyAttackSource {
    OpponentActive,
    OpponentInPlay,
    OwnBenchNonEx,
    /// Mew's Miraculous Memory: every attack printed on a Pokémon in the opponent's hand *or*
    /// deck. Unlike the other sources the attacker does not choose — one candidate is picked at
    /// random (see [`CopyAttackSource::is_random`]).
    OpponentHandAndDeck,
}

impl CopyAttackSource {
    /// Whether the copied attack is chosen at random rather than by the attacking player.
    pub(crate) fn is_random(&self) -> bool {
        matches!(self, CopyAttackSource::OpponentHandAndDeck)
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum Mechanic {
    SelfHeal {
        amount: u32,
    },
    /// The defender's condition is checked when the attack resolves, before its damage.
    SelfHealIfDefenderHasStatus {
        condition: StatusCondition,
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
    /// Cradily's Stick and Absorb: deal damage, heal `heal_amount` from the attacking Pokémon, then
    /// apply a `CardEffect` to an Active Pokémon (`opponent: true` → the Defending Pokémon).
    /// `SelfHeal` plus `DamageAndCardEffect` in one attack.
    SelfHealAndCardEffect {
        heal_amount: u32,
        opponent: bool,
        effect: CardEffect,
        duration: u8,
    },
    SearchToHandByEnergy {
        energy_type: EnergyType,
    },
    SearchToBenchByName {
        name: String,
    },
    SearchToBenchBasic,
    SearchRandomPokemonToHand,
    /// Team Rocket's Slowpoke - Scavenge: put one random Trainer card of the requested kind
    /// from the attacker's discard pile into their hand.
    SearchRandomTrainerTypeFromDiscardToHand {
        trainer_type: TrainerType,
    },
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
    /// Flip a coin; on heads apply `heads_conditions` to the opponent's Active Pokémon, on tails
    /// apply `tails_conditions` (usually empty). Damage is dealt on either branch.
    ChanceStatusAttack {
        heads_conditions: Vec<StatusCondition>,
        tails_conditions: Vec<StatusCondition>,
    },
    /// Flip a coin. If tails, this attack does nothing. If heads, deal damage and apply
    /// `conditions` to the opponent's Active Pokémon (e.g. Drampa's Dragon Breath).
    CoinFlipNoDamageOrDamageAndStatus {
        conditions: Vec<StatusCondition>,
    },
    /// One Special Condition from `options` is chosen at random (uniformly) and applied to the
    /// opponent's Active Pokémon, excluding conditions already affecting it (Alolan Muk ex's
    /// Chemical Panic). If every option is already present, only the damage is dealt.
    RandomStatusFromEligible {
        options: Vec<StatusCondition>,
    },
    /// Apply `conditions` plus lingering `effects` (for `duration` turns) to the opponent's
    /// Active Pokémon (e.g. Roserade's Poison Ring: Poisoned + can't retreat).
    InflictStatusAndCardEffects {
        conditions: Vec<StatusCondition>,
        effects: Vec<CardEffect>,
        duration: u8,
    },
    /// The opponent's Active Pokémon is now Poisoned, and its Pokémon Checkup poison damage is
    /// `checkup_damage` instead of the usual 10 (Toxicroak's Toxic, Toxapex's Severe Poison).
    InflictPoisonWithCustomCheckupDamage {
        checkup_damage: u32,
    },
    /// Deal damage, then let the player choose one of these Special Conditions to
    /// inflict on the opponent's Active Pokémon (e.g. Dustox's Select Powder).
    ChooseStatusToInflict {
        options: Vec<StatusCondition>,
    },
    DamageAllOpponentPokemon {
        damage: u32,
    },
    /// Discard `count` random Energy from among the Energy attached to in-play Pokémon.
    /// `own_side_only` restricts the pool to the attacker's own Pokémon (Groudon's Gaia
    /// Blast); otherwise both sides' Pokémon are in the pool (Lunala ex-style).
    DiscardRandomGlobalEnergy {
        count: usize,
        own_side_only: bool,
    },
    RandomDamageToOpponentPokemonPerSelfEnergy {
        energy_type: EnergyType,
        damage_per_hit: u32,
    },
    DiscardEnergyFromOpponentActive,
    /// Discard one Energy of a specific type from the opponent's Active Pokémon (e.g. Dedenne's
    /// Electric Nibbling discards a [L], Surskit's Firefighting discards a [R]).
    DiscardTypeEnergyFromOpponentActive {
        energy_type: EnergyType,
    },
    /// Oricorio's Kindle / Yveltal's Evil Crash: discard a random Energy from each Active
    /// Pokémon (the attacker's own Active and the opponent's Active).
    DiscardRandomEnergyFromBothActive,
    /// Dudunsparce's Sudden Drilling: if this Pokémon evolved (was played) this turn, discard
    /// `count` random Energy from the opponent's Active Pokémon.
    DiscardOpponentActiveEnergyIfEvolvedThisTurn {
        count: usize,
    },
    /// Maushold's Triple Gnawing / Pidgeot's Twister: flip `num_coins` coins and discard one
    /// random Energy from the opponent's Active Pokémon per heads. When `nothing_if_no_heads`
    /// is set ("If all of them are tails, this attack does nothing."), the zero-heads branch
    /// deals no damage at all.
    FlipCoinsDiscardOpponentEnergyPerHeads {
        num_coins: usize,
        nothing_if_no_heads: bool,
    },
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
    /// Extra damage when the defender's name contains the supplied text.
    ExtraDamageIfDefenderNameContains {
        substring: String,
        extra_damage: u32,
    },
    ExtraDamageIfOpponentHasSpecialCondition {
        extra_damage: u32,
    },
    /// Extra damage for every simultaneous Special Condition on the opponent's Active Pokémon.
    ExtraDamagePerOpponentSpecialCondition {
        damage_per_condition: u32,
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
    /// Flip `num_coins` coins; if ALL of them are tails the attack does nothing, otherwise the
    /// printed damage is dealt unchanged.
    CoinFlipNoEffect {
        num_coins: usize,
    },
    /// Flip a coin; if TAILS, add `effect` to the Active Pokémon (own or opponent's) for
    /// `duration` turns. Damage is dealt on either branch (e.g. "If tails, during your next
    /// turn, this Pokémon can't attack").
    CoinFlipTailsCardEffect {
        opponent: bool,
        effect: CardEffect,
        duration: u8,
    },
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
    /// Gouging Fire's Scorching Interruption: discard `count` (untyped, so randomly chosen)
    /// Energy from the attacker, then give the attacker a card effect.
    SelfDiscardRandomEnergyAndCardEffect {
        count: usize,
        effect: CardEffect,
        duration: u8,
    },
    /// Rapid Strike Urshifu's Tornado Shot: discard the listed Energy from the attacker, and
    /// the attack also does `bench_damage` to 1 of the opponent's Benched Pokémon (chosen).
    SelfDiscardEnergyAndChoiceBenchDamage {
        energies: Vec<EnergyType>,
        bench_damage: u32,
    },
    /// Walking Wake's Sweeping Billow: discard `count` (untyped, so randomly chosen) Energy
    /// from the attacker, and the attack also does `bench_damage` to each of the opponent's
    /// Benched Pokémon.
    SelfDiscardRandomEnergyAndBenchDamage {
        count: usize,
        bench_damage: u32,
    },
    /// Volcarona's Volcanic Ash: discard the listed Energy from the attacker, then deal
    /// `damage` to 1 of the opponent's Pokémon (chosen, Active or Benched).
    SelfDiscardEnergyThenDamageAnyOpponentPokemon {
        energies: Vec<EnergyType>,
        damage: u32,
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
    /// Gigalith ex's Megaton Cannon: `DirectDamage` that additionally leaves a `CardEffect` on the
    /// attacking Pokémon (e.g. "During your next turn, this Pokémon can't attack.").
    DirectDamageAndSelfCardEffect {
        damage: u32,
        bench_only: bool,
        effect: CardEffect,
        duration: u8,
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
    /// Team Rocket's Moltres ex - Heat Charged: attach one produced Energy of `energy_type`
    /// to the attacker for each heads in a fixed coin batch.
    FlipCoinsSelfChargeActivePerHeads {
        num_coins: usize,
        energy_type: EnergyType,
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
    /// Swanna's Feathery Cyclone: move all Energy (of any types) from the attacker to 1 of
    /// your Benched Pokémon (chosen).
    MoveAllEnergyToBench,
    /// Regice's Reflect Energy: move `count` random Energy from the attacker to 1 of your
    /// Benched Pokémon (chosen).
    MoveRandomEnergyToBench {
        count: usize,
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
    /// Flip `num_coins` coins for `damage_per_head` damage per heads, and inflict `status` when at
    /// least `min_heads_for_status` heads were flipped (0 = always). `status_on_self` targets the
    /// attacker instead of the opponent's Active (Bellossom's Petal Dance).
    ExtraDamageForEachHeadsWithStatus {
        include_fixed_damage: bool,
        damage_per_head: u32,
        num_coins: usize,
        status: StatusCondition,
        min_heads_for_status: usize,
        status_on_self: bool,
    },
    /// Flip `num_coins` coins for `damage_per_head` damage per heads — but flip
    /// `boosted_num_coins` instead if the attacker has the tool named `tool_name` attached
    /// (Ambipom's Excited Tail + Lucky Mittens).
    ExtraDamageForEachHeadsToolBoostedCoins {
        damage_per_head: u32,
        num_coins: usize,
        boosted_num_coins: usize,
        tool_name: String,
    },
    /// Flip a coin for each of the attacker's Pokémon in play (optionally only those whose name
    /// is in `name_filter`); the attack does `damage_per_heads` damage for each heads, REPLACING
    /// the printed damage (Group Beatdown, Family Beatdown).
    CoinFlipPerPokemonInPlay {
        damage_per_heads: u32,
        name_filter: Option<Vec<String>>,
    },
    /// Flip a coin: heads → `damage` to the opponent's Active Pokémon; tails → heal `heal`
    /// damage FROM the opponent's Active Pokémon (Delibird's Box of Surprises).
    CoinFlipDamageOrHealOpponent {
        damage: u32,
        heal: u32,
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
    /// Extra damage for each card of a given Trainer kind in your discard pile (e.g. Chandelure's
    /// Past Friends counts Supporters, Rotom ex's Junk Spark counts Items).
    ExtraDamagePerTrainerTypeInDiscard {
        trainer_type: TrainerType,
        damage_per_card: u32,
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

    // ---------------------------------------------------------------------------------------
    // §47 — B4 completion, wave 2. Each of these is the mirror image, or a one-field variant,
    // of a mechanic that already existed. They are separate variants rather than extra fields
    // on the originals so that no currently-working map entry had to be touched.
    // ---------------------------------------------------------------------------------------
    /// Luxray's Revenge Blast: "+N damage for each point your OPPONENT has gotten." The mirror of
    /// [`Mechanic::ExtraDamagePerOwnPoint`] — it rewards being behind rather than ahead.
    ExtraDamagePerOpponentPoint {
        damage_per_point: u32,
    },
    /// Hisuian Basculegion's Soul Counter: count only points the opponent received during their
    /// most recently completed own turn, not their lifetime score or points gained on your turn.
    ExtraDamagePerOpponentPointDuringOwnLastTurn {
        damage_per_point: u32,
    },
    /// Pheromosa's Prelude: "If you haven't gotten any points, this attack does +N damage."
    /// The own-side mirror of [`Mechanic::ExtraDamageIfOpponentPointsExactly`].
    ExtraDamageIfOwnPointsExactly {
        points: u8,
        extra_damage: u32,
    },
    /// Swalot's Swallow Up: extra damage if the opponent's Active has LESS remaining HP than this
    /// Pokémon. The mirror of [`Mechanic::ExtraDamageIfOpponentHpMoreThanSelf`] — a finisher
    /// rather than a giant-killer.
    ExtraDamageIfOpponentHpLessThanSelf {
        extra_damage: u32,
    },
    /// Mr. Mime's Synchro Dance: extra damage if this Pokémon and the opponent's Active have the
    /// SAME amount of Energy attached. Equality, where
    /// [`Mechanic::ExtraDamageIfMoreEnergyThanDefender`] is strict inequality.
    ExtraDamageIfEqualEnergyToDefender {
        extra_damage: u32,
    },
    /// Chimecho's Extrasensory: extra damage if you have the same number of cards in hand as your
    /// opponent. [`Mechanic::ExtraDamageIfHandSizeIn`] tests one hand against a fixed list; this
    /// compares the two hands to each other.
    ExtraDamageIfHandSizeEqualsOpponent {
        extra_damage: u32,
    },
    /// Damage scaling with the number of cards in the attacker's hand.
    ExtraDamagePerCardInOwnHand {
        damage_per_card: u32,
        include_fixed_damage: bool,
    },
    /// Poochyena's Team Hunt: "Draw a card for each <name> you have in play." Count is resolved at
    /// forecast time, so search bots see the true draw count rather than a fixed one.
    DrawPerNamedPokemonInPlay {
        name: String,
    },
    /// Teal Mask Ogerpon's Ogre's Whip: "This attack does damage equal to this Pokémon's remaining
    /// HP." Printed `fixed_damage` is 0; the whole attack is the attacker's current HP, so it hits
    /// hardest when untouched and fades as the Pokémon takes damage.
    DamageEqualToSelfRemainingHp,
    /// Pachirisu's Crackling Snap: "Discard the top card of your deck, and if that card is an Item,
    /// this attack does +N damage." The Trainer-type counterpart of
    /// [`Mechanic::DiscardTopSelfDeckExtraDamageIfType`], which tests an Energy type.
    DiscardTopSelfDeckExtraDamageIfTrainerType {
        trainer_type: TrainerType,
        extra_damage: u32,
    },
    /// Kyogre's Tidal Blast: "Discard N [type] Energy from this Pokémon, and this attack does
    /// `damage` to EACH of your opponent's Pokémon."
    SelfDiscardTypedEnergyAndDamageAllOpponent {
        energy_type: EnergyType,
        count: usize,
        damage: u32,
    },
    /// Psyduck's Migraine: "Flip a coin. If heads, your opponent's Active Pokémon is now
    /// `condition`. If tails, THIS Pokémon is." Both branches deal the attack's damage; only the
    /// recipient of the Special Condition differs.
    CoinFlipStatusOpponentOrSelf {
        condition: StatusCondition,
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
    /// Galvantula's Electric Shock: discard all Energy from the attacker and inflict the
    /// listed Special Conditions on the opponent's Active Pokémon.
    SelfDiscardAllEnergyAndInflictStatus {
        conditions: Vec<StatusCondition>,
    },
    /// Raging Bolt's Baneful Boom: discard all Energy from the attacker, then Knock Out the
    /// opponent's Active Pokémon outright (not damage, so damage modifiers don't apply).
    SelfDiscardAllEnergyKnockOutOpponentActive,
    /// Mesprit's Supreme Blast: usable only with the named Pokémon on the attacker's Bench
    /// (gated at move generation); on use, discard all Energy from the attacker.
    RequiresBenchedNamesSelfDiscardAllEnergy {
        required_bench_names: Vec<String>,
    },
    /// Boltund's Defiant Spark: if the attacker has damage on it, the attack can instead be
    /// paid with `cost`. Wired into move generation; the attack itself is plain damage.
    AlternativeCostIfDamaged {
        cost: Vec<EnergyType>,
    },
    /// Veluza's Shedding Spiral: if the attacker's deck is empty, the attack can instead be
    /// paid with `cost`. Wired into move generation; the attack itself is plain damage.
    AlternativeCostIfDeckEmpty {
        cost: Vec<EnergyType>,
    },
    SelfDiscardAllTypeEnergy {
        energy_type: EnergyType,
    },
    /// Mega Rayquaza ex's Mega Burst: discard every Energy of the listed types from the attacking
    /// Pokémon, dealing `damage_per_energy` for each Energy discarded in this way (the attack's
    /// `fixed_damage` is the per-Energy amount, so it is not added as a base).
    SelfDiscardAllTypesEnergyDamagePerDiscarded {
        energy_types: Vec<EnergyType>,
        damage_per_energy: u32,
    },
    SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon {
        energy_type: EnergyType,
        damage: u32,
    },
    SelfDiscardRandomEnergy {
        count: usize,
    },
    /// Entei's Strong Flare: flip a coin; if tails, discard `count` random Energy from the
    /// attacker.
    CoinFlipTailsSelfDiscardRandomEnergy {
        count: usize,
    },
    AlsoBenchDamage {
        opponent: bool,
        damage: u32,
        must_have_energy: bool,
    },
    AlsoChoiceBenchDamage {
        opponent: bool,
        damage: u32,
    },
    /// A filtered counterpart to `AlsoChoiceBenchDamage`. Kept separate so existing effect-map
    /// entries retain their stable debug representation.
    AlsoChoiceBenchDamageFiltered {
        opponent: bool,
        damage: u32,
        filter: BenchDamageFilter,
    },
    /// Extra damage if a Pokémon has damage on it. `benched: false` checks the chosen side's
    /// Active Pokémon; `benched: true` checks whether ANY of that side's Benched Pokémon are
    /// damaged (Drampa's Berserk).
    ExtraDamageIfHurt {
        extra_damage: u32,
        opponent: bool,
        benched: bool,
    },
    /// Regidrago - Draconic Slam: reduce printed damage when the attacker is damaged.
    LessDamageIfSelfHurt {
        reduction: u32,
    },
    ExtraDamageIfUndamaged {
        extra_damage: u32,
    },
    /// Vespiquen ex's Chase Order: "You may discard 1 of your Benched Basic [G] Pokémon. If you
    /// do, this attack does 70 more damage." The attacker chooses between the plain damage and
    /// discarding one eligible Benched Basic Pokémon for the boosted damage.
    OptionalDiscardBenchedBasicForExtraDamage {
        energy_type: EnergyType,
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
    /// `include_fixed_damage: false` — "This attack does N damage for each Energy attached to all
    /// of your opponent's Pokémon" (the count IS the whole attack).
    /// `include_fixed_damage: true` — "…does N MORE damage for each…" (added on top of the printed
    /// damage, e.g. Eelektross' Energy Crush at B4 058).
    DamagePerEnergyAll {
        opponent: bool,
        damage_per_energy: u32,
        include_fixed_damage: bool,
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
    /// Sableye's Jeweled Gift: take a random Energy from among the 8 basic types from your
    /// Energy Zone and attach it to 1 of your Benched Pokémon (chosen).
    AttachRandomBasicEnergyFromZoneToBench,
    /// Uxie's Mind Boost: take an Energy of `energy_type` from your Energy Zone and attach it
    /// to 1 of your in-play Pokémon with one of the listed names (chosen).
    AttachEnergyFromZoneToPokemonNamed {
        energy_type: EnergyType,
        names: Vec<String>,
    },
    /// Smeargle's Splatter Coating: change the type of a random Energy attached to the
    /// opponent's Active Pokémon to a random one of the 8 basic types.
    ChangeRandomOpponentActiveEnergyType,
    /// Porygon-Z's Buggy Beam: change the type of the next Energy that will be generated for
    /// the opponent to a random one of the 8 basic types.
    ChangeOpponentNextGeneratedEnergyType,
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
    /// Use one of the attacks reachable from `source` as this attack. When `coin_flip` is set the
    /// copy only happens on heads (Mimikyu's Try to Imitate); when `source.is_random()` the engine
    /// picks the copied attack instead of offering the choice (Mew's Miraculous Memory).
    CopyAttack {
        source: CopyAttackSource,
        require_attacker_energy_match: bool,
        coin_flip: bool,
    },
    SelfAsleepAndHeal {
        amount: u32,
    },
    /// Wailord ex's Wondrous Waves: after dealing damage, the attacking Pokémon recovers from
    /// all Special Conditions.
    SelfCureStatusConditions,
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
    /// "Flip N coins. For each heads, a card is chosen at random from your opponent's hand …
    /// and shuffles it into their deck." With `num_coins: 1` this is the single-coin printing
    /// ("Flip a coin. If heads, your opponent reveals a random card …" / Purrloin's Whiny Voice).
    ShuffleRandomOpponentHandCardsPerHeads {
        num_coins: usize,
    },
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
    // ---------------------------------------------------------------------------------------------
    // Bench / spread, switching and board-manipulation family.
    // ---------------------------------------------------------------------------------------------
    /// Bidoof's Super Fang: "Halve your opponent's Active Pokémon's remaining HP, rounded down."
    /// This is not damage — no weakness, no damage modifiers, no counterattacks. Since every HP and
    /// damage value in the game sits on a 10s grid, "rounded down" can only mean rounded down to
    /// the nearest 10 (90 HP left becomes 40, matching the physical card's "half its remaining HP,
    /// rounded up to the nearest 10" damage wording).
    HalveOpponentActiveRemainingHp,
    /// Xatu's Life Drain: "Flip a coin. If heads, your opponent's Active Pokémon's remaining HP is
    /// now N." Only ever *lowers* the remaining HP — a Pokémon already below `remaining_hp` (e.g.
    /// one left at 10 by Ursaluna's Guts) is not healed back up to it.
    CoinFlipSetOpponentActiveRemainingHp {
        remaining_hp: u32,
    },
    /// Bewear's Superpowered Hug (`knocked_out: true`, points are scored) and Guzzlord's Breakcore /
    /// Scream Tail's Shooing Shout (`knocked_out: false`, the Pokémon is *discarded*, so no points).
    /// The effect only fires when every one of `num_coins` coins comes up heads.
    FlipCoinsRemoveOpponentActive {
        num_coins: usize,
        knocked_out: bool,
    },
    /// Kabutops' Leech Life: "Heal from this Pokémon the same amount of damage you did to your
    /// opponent's Active Pokémon." The heal is the *modified* damage (weakness, Giovanni, …), and
    /// it goes through `State::heal_pokemon` so Claydol's Heal Block still stops it.
    HealSelfEqualToDamageDealt,
    /// Toxtricity ex's Damaging Spark: "This attack also does N damage to each of your opponent's
    /// Benched Pokémon that has damage on it."
    AlsoBenchDamageIfDamaged {
        damage: u32,
    },
    /// Minun's Buddy Spark / Magmortar's Thundering Volcano: "If <name> is on your Bench, this
    /// attack also does N damage to each of your opponent's Benched Pokémon."
    AlsoBenchDamageIfPokemonOnBench {
        pokemon_name: String,
        damage: u32,
    },
    /// Ampharos' Zapping Bullet: "1 of your opponent's Benched Pokémon is chosen at random. This
    /// attack also does N damage to it." One equally likely branch per benched Pokémon, so the
    /// search bots price the spread instead of averaging it.
    AlsoRandomBenchDamage {
        damage: u32,
    },
    /// Mimikyu's Shadow Hit: "This attack also does N damage to 1 of your Pokémon." The attacking
    /// player chooses the target, which may be the Attacking Pokémon itself.
    AlsoChoiceOwnPokemonDamage {
        damage: u32,
    },
    /// Forretress' Enormous Explosion: "This Pokémon also does N damage to itself and M damage to
    /// all Benched Pokémon (both yours and your opponent's)."
    SelfDamageAndAllBenchDamage {
        self_damage: u32,
        bench_damage: u32,
    },
    /// Archeops' Wild Spin: "This attack does N damage to each of your opponent's Pokémon. During
    /// your next turn, this Pokémon's <attack_name> attack does +M damage to each of your
    /// opponent's Pokémon."
    ///
    /// The bonus is carried by an ordinary `CardEffect::IncreasedDamageForAttack`, which
    /// `hooks::modify_damage` already applies to the *Active*-to-Active portion. Because that hook
    /// deliberately ignores bench targets, this mechanic adds the same bonus to the benched targets
    /// itself — hence `bonus` appearing both here and in the effect.
    DamageAllOpponentPokemonWithNextTurnBonus {
        damage: u32,
        bonus: u32,
        attack_name: String,
    },
    /// Gyarados' Wild Swing: "You may discard any number of your Benched [energy_type] Pokémon.
    /// This attack does `damage_per` more damage for each Benched Pokémon you discarded in this
    /// way." Offers the attacking player one choice per subset of eligible Benched Pokémon.
    DiscardOwnBenchedTypeForDamage {
        energy_type: EnergyType,
        damage_per: u32,
    },
    /// Eldegoss' Float Up / Dunsparce's Bop 'n' Burrow: "You may shuffle this Pokémon and all
    /// attached cards into your deck." Declined with `SimpleAction::Noop`.
    MayShuffleSelfIntoDeck,

    // ---------------------------------------------------------------------------------------
    // §47 — B4 completion, wave 3.
    // ---------------------------------------------------------------------------------------
    /// Accelgor's Deck and Cover (B4 014 / B4 159): inflict `conditions` on the opponent's Active,
    /// then shuffle THIS Pokémon and everything attached back into the deck.
    ///
    /// Unlike [`Mechanic::MayShuffleSelfIntoDeck`] the shuffle is mandatory — there is no "you
    /// may" — so no `Noop` branch is offered.
    InflictStatusConditionsAndShuffleSelfIntoDeck {
        conditions: Vec<StatusCondition>,
    },
    /// Hoopa's Mischievous Ring (B4 077): "Before doing damage, shuffle all Pokémon Tools from
    /// each of your opponent's Pokémon into their deck."
    ///
    /// "Before doing damage" matters: a Tool that would have reduced the incoming damage (Heavy
    /// Helmet, Protective Poncho, …) is already gone when the damage is calculated, so the removal
    /// is applied as a pre-damage mutation rather than an after-effect.
    ShuffleOpponentToolsIntoDeckBeforeDamage,
    /// Armaldo's Abyssal Drop (B4 082): "Discard all Energy from this Pokémon. Choose a spot from
    /// among your opponent's Active Spot and Bench. At the end of your opponent's next turn, Knock
    /// Out the Pokémon in the spot you chose."
    ///
    /// Targets a BOARD POSITION, not a Pokémon — whatever is standing in that spot when the timer
    /// expires is knocked out, so switching the threatened Pokémon out saves it. Modelled on the
    /// existing delayed-spot-damage plumbing with `knock_out: true`, which makes the damage equal
    /// to the occupant's remaining HP at trigger time rather than a fixed number.
    SelfDiscardAllEnergyAndDelayedSpotKnockOut,
    /// Delcatty's Energy Blender (B4 135): "You may move any amount of Energy from your Pokémon in
    /// play to your other Pokémon in any way you like."
    ///
    /// ⚠ The literal text is the full Energy-redistribution lattice. This is generated by
    /// `actions::energy_moves::bounded_energy_move_candidates`, which offers only purposeful
    /// redistributions — see that module for the deviation and why it is taken.
    MoveEnergyFreelyAmongYourPokemon,

    /// Tapu Koko's Volt Switch: "Switch this Pokémon with 1 of your Benched [energy_type] Pokémon."
    /// The typed sibling of `SwitchSelfWithBench`.
    SwitchSelfWithBenchOfType {
        energy_type: EnergyType,
    },
    /// Fan Rotom's Spin Storm: "Flip a coin. If heads, put your opponent's Active Pokémon into
    /// their hand." The Pokémon and everything it evolved from go back to hand; its Energy is lost.
    CoinFlipReturnOpponentActiveToHand,
    /// Chinchou's Luring Glow (`coin_flip: true`, `damage: 0`) and Sandy Shocks' Pull In and Pound
    /// (`coin_flip: false`, `damage: 50`): "Switch in 1 of your opponent's Benched Pokémon to the
    /// Active Spot." The *attacking* player picks, exactly like Lana/Cyrus. When `damage > 0` the
    /// damage lands on the newly promoted Active Pokémon, and only if the switch happened.
    SwitchInOpponentBenchedThenDamage {
        damage: u32,
        coin_flip: bool,
    },
    /// Ho-Oh's Blessed Burn (`benched_only`, `basic_only`) and Diancie's Diamond Storm
    /// (`energy_type`): "Heal N damage from each of your <subset> Pokémon." The filtered
    /// counterpart of `HealAllYourPokemon`, routed through `State::heal_each_pokemon` so Heal Block
    /// still applies.
    HealEachYourPokemon {
        amount: u32,
        benched_only: bool,
        basic_only: bool,
        energy_type: Option<EnergyType>,
    },
    /// Wishiwashi's Call for Family (`count: 1`) and Tandemaus' Flock (`count: 3`): "Put N random
    /// cards from among <names> from your deck onto your Bench." The multi-name, multi-card
    /// generalization of `SearchToBenchByName`.
    SearchToBenchByNames {
        names: Vec<String>,
        count: usize,
    },
    /// Celebi's Temporal Leaves: "If your opponent's Active Pokémon is an evolved Pokémon, devolve
    /// it by putting the highest Stage Evolution card on it into your opponent's hand." Damage
    /// counters, Energy and any attached Tool stay on the Pokémon that is left behind.
    DevolveOpponentActive,

    // ===== Opponent hand / deck disruption =====
    /// "Discard a random [Item/Pokémon Tool] card from your opponent's hand", optionally gated
    /// behind a coin flip ("Flip a coin. If heads, discard a random card from your opponent's
    /// hand."). Discards fewer cards than `count` — possibly none — when the opponent's hand
    /// holds fewer matching cards.
    DiscardRandomOpponentHandCards {
        kind: HandCardKind,
        count: usize,
        coin_flip: bool,
    },
    /// "Your opponent reveals their hand." Both players already see the whole state in this
    /// engine, so revealing carries no mechanical consequence — the attack is plain damage.
    /// Modelled explicitly (rather than left unimplemented) so the printings validate as done.
    RevealOpponentHand,
    /// "Discard the top N cards of your deck" / "of each player's deck". Either count may be 0
    /// for the one-sided printings.
    DiscardTopDeck {
        own_count: usize,
        opponent_count: usize,
    },
    /// Dugtrio's Cliff Crumbler: discard the top card of your own deck; if it is a Pokémon of
    /// `energy_type`, the attack does `extra_damage` more.
    DiscardTopSelfDeckExtraDamageIfType {
        energy_type: EnergyType,
        extra_damage: u32,
    },
    /// Slowking's Litter: "Discard up to `max_cards` Pokémon Tool cards from your hand. This
    /// attack does `damage_per_card` damage for each card you discarded in this way." The
    /// printed damage is replaced, not added to, so discarding nothing deals nothing.
    DiscardToolsFromHandForDamage {
        max_cards: usize,
        damage_per_card: u32,
    },
    /// Aipom's Imitate: draw until your hand holds as many cards as your opponent's. Never
    /// discards when your hand is already the bigger one.
    DrawUntilHandMatchesOpponent,
    /// Coalossal's Mountain Crush: flip a coin until tails, discarding the top card of your
    /// opponent's deck for each heads.
    FlipUntilTailsDiscardOpponentDeck,
    /// Golurk's Heavy Rocket: reveal the top `reveal_count` cards of your deck, deal
    /// `damage_per` for each Pokémon there with a Retreat Cost of `min_retreat_cost` or more,
    /// then shuffle your deck. The printed damage is replaced by the computed total.
    RevealTopDeckDamagePerHeavyPokemon {
        reveal_count: usize,
        min_retreat_cost: usize,
        damage_per: u32,
    },
    /// Reveal a deck prefix, deal replacement damage for each Pokémon whose printed name contains
    /// `name_fragment`, then shuffle. The reveal is public and survives only as unordered deck
    /// membership knowledge after the shuffle.
    RevealTopDeckDamagePerPokemonName {
        reveal_count: usize,
        name_fragment: String,
        damage_per: u32,
    },
    /// Chatot's Mimic: shuffle your hand into your deck, then draw one card for each card in
    /// your opponent's hand.
    ShuffleHandIntoDeckDrawEqualToOpponentHand,
    /// "Your opponent reveals a random card from their hand and shuffles it into their deck",
    /// optionally followed by "Shuffle this Pokémon into your deck" (Liepard's Snatch and Flee).
    ShuffleRandomOpponentHandCardsIntoDeck {
        count: usize,
        shuffle_self_into_deck: bool,
    },
    /// Purugly's Interrupt: the opponent reveals their hand and the attacker chooses any one
    /// card there to shuffle into the opponent's deck.
    ChooseOpponentHandCardToShuffleIntoDeck,
    /// Oricorio's / Meloetta's Inspiring Dance: "During your next turn, attacks used by your
    /// [`energy_type`] Pokémon do +`amount` damage to your opponent's Active Pokémon."
    /// `energy_type: None` covers all of the attacker's Pokémon. Adds a
    /// `TurnEffect::IncreasedDamageForPlayer` bound to the attacking player, which is why this
    /// cannot be expressed as a plain `DamageAndTurnEffect` map entry.
    IncreasedDamageNextTurn {
        amount: u32,
        energy_type: Option<EnergyType>,
    },
    /// Machop's Shatter: discard whichever Stadium is in play (it goes to its owner's discard
    /// pile). Does nothing extra when there is no Stadium.
    DiscardStadiumInPlay,
    /// Quagsire's Amnesia: pick one of the opponent's Active Pokémon's attacks at random and lock
    /// it out for `duration` turns via `CardEffect::CannotUseAttack`.
    DisableRandomOpponentActiveAttack {
        duration: u8,
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
