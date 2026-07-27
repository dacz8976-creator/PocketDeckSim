use serde::{Deserialize, Serialize};

use crate::{
    models::{Card, EnergyType, StatusCondition, TrainerType},
    tools::is_tool_card,
};

/// Which kind of card a "put a random <kind> card from your deck into your hand" Ability looks for.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeckSearchKind {
    Pokemon,
    Tool,
}

/// Which kind of card a "put a <kind> card from your discard pile into your hand" Ability looks
/// for. The discard-pile mirror of [`DeckSearchKind`].
///
/// Derives `Hash`/`Serialize`/`Deserialize` because it is carried by
/// [`crate::actions::SimpleAction::PutRandomCardsFromDiscardToHand`].
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum DiscardSearchKind {
    Supporter,
    Tool,
}

impl DiscardSearchKind {
    /// Whether `card` is eligible for this search. `Tool` defers to [`is_tool_card`], the single
    /// definition of "is a Pokémon Tool" shared with the deck searches.
    pub(crate) fn matches(self, card: &Card) -> bool {
        match self {
            DiscardSearchKind::Supporter => {
                matches!(card, Card::Trainer(trainer) if trainer.trainer_card_type == TrainerType::Supporter)
            }
            DiscardSearchKind::Tool => is_tool_card(card),
        }
    }
}

/// How a "put ... from your discard pile into your hand" on-evolve Ability picks its cards. The
/// wording differs between printings and the difference is mechanical, so it is explicit rather
/// than inferred from the card kind.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DiscardSelection {
    /// "a Supporter card" (Delcatty's Search for Friends) — the *player* picks one, so every
    /// eligible card in the pile becomes an option on the move-generation stack.
    PlayerChoosesOne,
    /// "2 random Pokémon Tool cards" (Galarian Perrserker's Dig Up) — the *engine* picks this many,
    /// so it resolves as a probability branch over the eligible cards and takes whatever is
    /// available when the pile holds fewer.
    RandomCards(u8),
}

/// The card names that satisfy "if you have Arceus or Arceus ex in play". Pokémon ex have their
/// own name in this game, so both spellings have to be listed explicitly.
pub const ARCEUS_NAMES: &[&str] = &["Arceus", "Arceus ex"];

/// The Bench Regigigas' Seal of Antiquity demands. Every printing of these three counts — the
/// Ability names Pokémon, not specific cards.
pub const REGI_TRIO_NAMES: &[&str] = &["Regirock", "Regice", "Registeel"];

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
    /// "Once during your turn, you may heal `amount` damage from each of your [type] Pokémon."
    ///
    /// `energy_type: None` heals every Pokémon you have in play (Shaymin's Fragrant Flower
    /// Garden, Butterfree's Powder Heal); `Some(t)` restricts it to that type (Primarina's
    /// Melodious Healing, `[W]`). Mirrors how `SoothingWind` parameterises its type filter.
    HealAllYourPokemon {
        amount: u32,
        energy_type: Option<EnergyType>,
    },
    /// "Once during your turn, [condition,] you may heal `amount` damage from 1 of your Pokémon."
    ///
    /// The heal itself is identical across printings; only the usage condition differs, so it is
    /// parameterised rather than duplicated:
    /// - `require_active`: Espeon ex's Psychic Healing ("if this Pokémon is in the Active Spot").
    /// - `require_tool_attached`: Sylveon's Soothing Ribbon ("if this Pokémon has a Pokémon Tool
    ///   attached"). Any Pokémon Tool qualifies — the card does not name a specific one.
    HealOneYourPokemon {
        amount: u32,
        require_active: bool,
        require_tool_attached: bool,
    },
    /// Alolan Muk's Power of Alchemy (B2 097 / B2 173): "Basic Pokémon in play (both yours and
    /// your opponent's) have no Abilities."
    ///
    /// Passive and symmetric. Resolved at the single accessor
    /// `get_in_play_ability_mechanic`, which every read of an *in-play* Pokémon's Ability goes
    /// through, so the suppression cannot be applied to move generation but missed by some passive
    /// hook. Alolan Muk is a Stage 1, so it does not switch itself off.
    SuppressBasicAbilities,
    /// Claydol's Heal Block (A3a 031): "Pokémon (both yours and your opponent's) can't be healed."
    ///
    /// Passive and symmetric: while any Pokémon with this Ability is in play, *no* Pokémon on
    /// either side can be healed, whatever the source (Ability, attack, Trainer, Tool/berry,
    /// Pokémon Checkup). Resolved at the single healing gate `State::heal_pokemon` /
    /// `State::heal_each_pokemon` rather than at each healing site, so a healing effect added later
    /// is blocked by construction. Moving damage counters between Pokémon is not healing and is
    /// deliberately not blocked.
    PreventAllHealing,
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
    /// Rillaboom's Captivating Rhythm: "Once during your turn, you may flip a coin. If heads,
    /// switch in 1 of your opponent's Benched Pokémon to the Active Spot."
    ///
    /// Distinct from `SwitchOutOpponentActiveToBench`: there the *opponent* picks the replacement,
    /// here the ability's controller does, so on heads the follow-up choice is offered to the
    /// acting player even though it targets the opponent's board.
    CoinFlipSwitchInOpponentBenchToActive,
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
    /// Tyranitar's Energy Plunder: "Once during your turn, you may move all [energy_type] Energy
    /// from each of your Pokémon to this Pokémon."
    ///
    /// Differs from `MoveAllTypedEnergyFromBenchToActive` on both ends: the source is *every* one
    /// of your Pokémon rather than a single chosen Benched one (so there is no player choice and
    /// no `move_generation_stack` push), and the destination is the ability holder itself, which
    /// may be Benched, rather than the Active Spot. Moving from the holder to itself is a no-op.
    MoveAllTypedEnergyFromYourPokemonToSelf {
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
    /// "Once during your turn, you may put a random <kind> card from your deck into your hand."
    /// Pokémon (Pidgeot's Quick Search) and Pokémon Tool (Ambipom's Catching Tail) printings differ
    /// only by which cards are eligible, so the search kind is a parameter.
    SearchRandomCardFromDeck {
        card_kind: DeckSearchKind,
    },
    /// Data Scan (Porygon A1 209 / A1 249): "Once during your turn, you may look at the top card
    /// of your deck." and CHECK (Unown A2a 034 / A2a 078): "Once during your turn, you may choose
    /// either player. Look at the top card of that player's deck."
    ///
    /// Information-only. deckgym's players have no hidden-information model — they already
    /// forecast over the whole deck — so peeking at a top card cannot change any decision they
    /// make. It is therefore implemented honestly as an Ability that is legally usable once per
    /// turn and mutates nothing but its own once-per-turn flag; it is deliberately *not* faked as
    /// a draw or a deck manipulation, which would give the card power it does not have.
    ///
    /// `either_player` is the one part of the wording with a mechanical consequence: CHECK may look
    /// at the opponent's deck, so it stays usable while only the opponent still has a top card.
    LookAtTopCardOfDeck {
        either_player: bool,
    },
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
    /// Galarian Cursola's Perish Body (A4a 035): "If this Pokémon is in the Active Spot and is
    /// Knocked Out by damage from an attack from your opponent's Pokémon, flip a coin. If heads,
    /// the Attacking Pokémon is Knocked Out."
    ///
    /// The coin-flip sibling of `DamageOnKnockoutInActive { target: Attacker }`, but it cannot ride
    /// the same `on_knockout` hook: there is no RNG there, and folding the flip in would hide it
    /// from the search. So, exactly like `CoinFlipToDenyKnockoutPoints`, it is a probability split
    /// at forecast time (see `AttackOutcomes::split_with_attacker_knockout`) — on heads the branch
    /// zeroes the attacker's HP right after damage lands, and the single `handle_knockouts` pass
    /// that follows resolves the double knockout, awarding each player their point.
    CoinFlipToKnockOutAttackerOnKnockout,
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
    /// Garganacl's Blessed Salt (B3a 033): "During Pokémon Checkup, heal `amount` damage from each
    /// of your Pokémon."
    ///
    /// The healing counterpart of the `Checkup*Damage*` mechanics above, with one difference worth
    /// noting: those print "if this Pokémon is in the Active Spot", Blessed Salt does not, so the
    /// holder heals the board from the Bench too. Passive; resolved in the Pokémon Checkup step.
    CheckupHealAllYourPokemon {
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
    /// "Once during your turn, you may switch out your opponent's Active [Basic] Pokémon to the
    /// Bench. (Your opponent chooses the new Active Pokémon.)"
    ///
    /// - `require_active`: the ability holder must itself be in the Active Spot.
    /// - `require_opponent_active_basic`: only Swellow's Repelling Wind (B2 133) prints the
    ///   "Active *Basic* Pokémon" restriction; the other printings can repel anything.
    SwitchOutOpponentActiveToBench {
        require_active: bool,
        require_opponent_active_basic: bool,
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
    /// Hypno's Sleep Pendulum and Grafaiai's Poison Coating: "Once during your turn, you may flip
    /// a coin. If heads, your opponent's Active Pokémon is now <condition>." One parameterised
    /// mechanic covers every Special Condition printed on this template.
    CoinFlipStatusOpponentActive {
        status: StatusCondition,
    },
    DiscardFromHandToDrawCard,
    /// Fabled Luster (Arceus ex) "can't be affected by any Special Conditions" and Insomnia
    /// (Hoothoot A4 140 / A4 182) "can't be Asleep".
    ///
    /// `status: None` is the blanket immunity; `Some(s)` immunises against that one condition only,
    /// mirroring how `SoothingWind` parameterises its Energy filter. Passive; enforced in
    /// `State::apply_status_condition`, the single authoritative path for setting conditions.
    ImmuneToStatusConditions {
        status: Option<StatusCondition>,
    },
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
    /// Polteageist's Refreshing Tea (B2 075): "Once during your turn, when you play this Pokémon
    /// from your hand to evolve 1 of your Pokémon, you may have your opponent shuffle their hand
    /// into their deck. For each remaining point that your opponent needs to win, they draw a
    /// card."
    ///
    /// The payload is exactly Mars' Supporter effect, so it rides the same implementation; the
    /// Ability only changes when it happens. Passive: it is an on-evolve trigger, so it is offered
    /// from the `on_evolve` hook (with a `Noop`, because it is a "may") rather than as a
    /// `UseAbility` action.
    OpponentShuffleHandAndDrawOnEvolve,
    /// "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your
    /// Pokémon, you may put <selection> `card_kind` card(s) from your discard pile into your hand."
    ///
    /// The discard-pile mirror of `SearchRandomCardFromDeck`, riding the same on-evolve trigger as
    /// `DrawCardsOnEvolve` & co. Two printings, differing on both axes:
    /// - Delcatty's Search for Friends (B1 194 / B1 248):
    ///   `{ Supporter, PlayerChoosesOne }` — "a Supporter card", the player picks.
    /// - Galarian Perrserker's Dig Up (B2 111 / B2 177):
    ///   `{ Tool, RandomCards(2) }` — "2 *random* Pokémon Tool cards", the engine picks.
    ///
    /// Either way it is a "may", so the offer always carries a `Noop`.
    PutCardsFromDiscardToHandOnEvolve {
        card_kind: DiscardSearchKind,
        selection: DiscardSelection,
    },
    CanEvolveIntoEeveeEvolution,
    CanEvolveOnFirstTurnIfActive,
    CounterattackDamage {
        amount: u32,
    },
    PoisonAttackerOnDamaged,
    /// Jellicent's Bouncy Body (B1 069 / B1 234 / B3 210): "If this Pokémon is in the Active Spot
    /// and is damaged by an attack from your opponent's Pokémon, take a [`energy_type`] Energy from
    /// your Energy Zone and attach it to 1 of your Benched Pokémon."
    ///
    /// Passive, and an on-*damaged* trigger rather than an on-knockout one: it fires from the same
    /// place as Poison Barb and the counterattack abilities, so it also fires on the hit that
    /// Knocks Jellicent Out (the Bench is still intact at that point). The destination is the
    /// holder's controller's choice, so it pushes onto the `move_generation_stack` — and with an
    /// empty Bench there is no legal target and nothing happens.
    AttachEnergyFromZoneToBenchOnDamaged {
        energy_type: EnergyType,
    },
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
    /// Regigigas' Seal of Antiquity (B3 134): "If you don't have Regirock, Regice, and Registeel on
    /// your Bench, this Pokémon can't attack."
    ///
    /// A restriction on the holder's *own* attacks, so — unlike the `CardEffect::CannotAttack` that
    /// attacks inflict on the defender — it is expressed at move generation time in
    /// `generate_attack_actions`: while the Active Pokémon has this Ability and its Bench is
    /// missing any of `required_bench_names`, it is offered no attacks at all. Passive.
    CannotAttackWithoutBenchedNames {
        required_bench_names: &'static [&'static str],
    },
    /// Double Type (Rapid Strike Urshifu B3 051: "As long as this Pokémon is in play, it is [W]
    /// and [F] type."; Single Strike Urshifu B3 113: "... it is [F] and [D] type.").
    ///
    /// Replaces the holder's printed type with `types` — for both printings the printed type is
    /// one of the two, so in practice it *adds* the second. Passive, and read through the single
    /// accessor `State::pokemon_energy_types` / `State::pokemon_is_type`, which every
    /// "what type is this Pokémon in play" question goes through (Weakness, the type damage
    /// boosts, "each of your [X] Pokémon" filters, Retreat-cost discounts). Going through the
    /// in-play Ability chokepoint means Prickly Powder's `NoAbilities` turns it back off.
    DualType {
        types: [EnergyType; 2],
    },
    /// Celebi's Time Recall: "Each of your evolved Pokémon can use any attack from its previous
    /// Evolutions. (You still need the necessary Energy to use each attack.)"
    /// Passive: while a Pokémon with this ability is in play, attack generation also offers the
    /// active evolved Pokémon the attacks from its previous evolutions (its under-cards).
    TimeRecall,
    /// "... put a random card from your deck that evolves from this Pokémon onto this Pokémon to
    /// evolve it." Two printings share the effect and differ only in what sets it off, so the
    /// trigger is a parameter:
    /// - Caterpie's Quick Growth (B3b 001 / B3b 091): `EndOfOpponentTurnIfActive`.
    /// - Porygon2's Buggy Evolution (A4 136): `OnEnergyZoneAttachToSelf`.
    ///
    /// Passive either way — there is no `UseAbility` action for it.
    RandomEvolutionFromDeck {
        trigger: RandomEvolutionTrigger,
    },
}

/// What sets off a [`AbilityMechanic::RandomEvolutionFromDeck`] ability.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum RandomEvolutionTrigger {
    /// "At the end of your opponent's turn, if this Pokémon is in the Active Spot" — resolved in
    /// the start-of-turn ability outcomes, alongside the other end-of-turn triggers.
    EndOfOpponentTurnIfActive,
    /// "Whenever you attach an Energy from your Energy Zone to this Pokémon" — resolved when the
    /// `Attach` action is forecast, so the random evolution shows up as real probability branches
    /// instead of being hidden inside the state mutation.
    OnEnergyZoneAttachToSelf,
}
