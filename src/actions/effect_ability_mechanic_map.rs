// This code is initially generated from the database.json by card_enum_generator.rs.
// but needs to be manually filled in with actual implementations.

use std::collections::HashMap;
use std::sync::LazyLock;

use crate::actions::abilities::{
    AbilityMechanic, AttackCostReductionScope, DeckSearchKind, DiscardSearchKind, DiscardSelection,
    KnockoutDamageTarget, NoRetreatCostCondition, NoRetreatCostTarget, RandomEvolutionTrigger,
    ARCEUS_NAMES, REGI_TRIO_NAMES,
};
use crate::effects::CardEffect;
use crate::models::{Card, EnergyType, PlayedCard, StatusCondition};
use crate::State;

/// Map from ability effect text to its AbilityMechanic.
pub static EFFECT_ABILITY_MECHANIC_MAP: LazyLock<HashMap<&'static str, AbilityMechanic>> =
    LazyLock::new(|| {
        let mut map: HashMap<&'static str, AbilityMechanic> = HashMap::new();
        map.insert(
            "Each of your evolved Pokémon can use any attack from its previous Evolutions. (You still need the necessary Energy to use each attack.)",
            AbilityMechanic::TimeRecall,
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, attacks used by your opponent's Active Pokémon cost 1 [C] more.",
            AbilityMechanic::IncreaseAttackCostForOpponentActive { amount: 1 },
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, attacks used by your opponent's Active Pokémon do -20 damage.",
            AbilityMechanic::ReduceOpponentActiveDamage { amount: 20 },
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it.",
            AbilityMechanic::CanEvolveOnFirstTurnIfActive,
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, whenever you attach an Energy from your Energy Zone to it, it is now Asleep.",
            AbilityMechanic::SleepOnZoneAttachToSelfWhileActive,
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, whenever your opponent attaches an Energy from their Energy Zone to 1 of their Pokémon, do 20 damage to that Pokémon.",
            AbilityMechanic::ElectromagneticWall,
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, your opponent can't use any Supporter cards from their hand.",
            AbilityMechanic::NoOpponentSupportInActive,
        );
        map.insert(
            "As long as this Pokémon is in the Active Spot, your opponent can't play any Stadium cards from their hand.",
            AbilityMechanic::NoOpponentStadiumInActive,
        );
        map.insert(
            "As long as this Pokémon is on your Bench, attacks used by your Pokémon that evolve from Poliwhirl do +40 damage to your opponent's Active Pokémon.",
            AbilityMechanic::IncreaseDamageForEvolutionsFromBench {
                evolves_from: "Poliwhirl",
                amount: 40,
            },
        );
        map.insert(
            "As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks.",
            AbilityMechanic::PreventDamageWhileBenched,
        );
        map.insert(
            "As long as this Pokémon is on your Bench, your Active Basic Pokémon's Retreat Cost is 1 less.",
            AbilityMechanic::ReduceRetreatCostOfYourActiveBasicFromBench { amount: 1 },
        );
        map.insert(
            "As often as you like during your turn, you may choose 1 of your Pokémon that has damage on it, and move all of its damage to this Pokémon.",
            AbilityMechanic::MoveDamageFromOneYourPokemonToThisPokemon,
        );
        map.insert(
            "As often as you like during your turn, you may move a [W] Energy from 1 of your Benched [W] Pokémon to your Active [W] Pokémon.",
            AbilityMechanic::MoveTypedEnergyFromBenchToActive {
                energy_type: EnergyType::Water,
            },
        );
        map.insert(
            "At the beginning of your turn, if this Pokémon is in the Active Spot, put a random [P] Pokémon from your deck into your hand.",
            AbilityMechanic::StartTurnRandomPokemonToHand {
                energy_type: EnergyType::Psychic,
            },
        );
        map.insert(
            "At the end of your first turn, take a [L] Energy from your Energy Zone and attach it to this Pokémon.",
            AbilityMechanic::EndFirstTurnAttachEnergyToSelf {
                energy_type: EnergyType::Lightning,
            },
        );
        map.insert(
            "At the end of your turn, if this Pokémon is in the Active Spot, draw a card.",
            AbilityMechanic::EndTurnDrawCardIfActive { amount: 1 },
        );
        map.insert(
            "At the end of your turn, if this Pokémon is in the Active Spot, heal 20 damage from it.",
            AbilityMechanic::EndTurnHealSelfIfActive { amount: 20 },
        );
        map.insert(
            "Attacks used by your [F] Pokémon do +20 damage to your opponent's Active Pokémon.",
            AbilityMechanic::IncreaseDamageForTypeInPlay {
                energy_type: EnergyType::Fighting,
                amount: 20,
            },
        );
        map.insert(
            "Attacks used by your [P] Pokémon and [M] Pokémon do +30 damage to your opponent's Active Pokémon.",
            AbilityMechanic::IncreaseDamageForTwoTypesInPlay {
                energy_type_a: EnergyType::Psychic,
                energy_type_b: EnergyType::Metal,
                amount: 30,
            },
        );
        // map.insert("Basic Pokémon in play (both yours and your opponent's) have no Abilities.", todo_implementation);
        map.insert(
            "During Pokémon Checkup, if this Pokémon is in the Active Spot, do 10 damage to your opponent's Active Pokémon.",
            AbilityMechanic::CheckupDamageToOpponentActive { amount: 10 },
        );
        map.insert(
            "During Pokémon Checkup, heal 10 damage from each of your Pokémon.",
            AbilityMechanic::CheckupHealAllYourPokemon { amount: 10 },
        );
        map.insert(
            "During your first turn, this Pokémon has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::ThisPokemon,
                condition: NoRetreatCostCondition::YourFirstTurn,
            },
        );
        map.insert(
            "Each [G] Energy attached to your [G] Pokémon provides 2 [G] Energy. This effect doesn't stack.",
            AbilityMechanic::DoubleGrassEnergy,
        );
        map.insert(
            "Each of your Pokémon that has any Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions.",
            AbilityMechanic::SoothingWind { energy_type: None },
        );
        map.insert(
            "Each of your Pokémon that has any [P] Energy attached recovers from all Special Conditions and can't be affected by any Special Conditions.",
            AbilityMechanic::SoothingWind {
                energy_type: Some(EnergyType::Psychic),
            },
        );
        map.insert(
            "Each of your [G] Pokémon gets +20 HP.",
            AbilityMechanic::IncreaseHpForTypeInPlay {
                energy_type: EnergyType::Grass,
                amount: 20,
            },
        );
        map.insert(
            "If a Stadium is in play, this Pokémon has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::ThisPokemon,
                condition: NoRetreatCostCondition::StadiumInPlay,
            },
        );
        map.insert(
            "If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage.",
            AbilityMechanic::CoinFlipToPreventDamage,
        );
        map.insert(
            "If any damage is done to this Pokémon by attacks, flip a coin. If heads, this Pokémon takes -100 damage from that attack.",
            AbilityMechanic::CoinFlipToReduceDamage { amount: 100 },
        );
        map.insert(
            "If any damage is done to this Pokémon by attacks, flip a coin. If heads, this Pokémon takes -80 damage from that attack.",
            AbilityMechanic::CoinFlipToReduceDamage { amount: 80 },
        );
        map.insert(
            "If this Pokémon has a Pokémon Tool attached, attacks used by this Pokémon cost 1 less [G] Energy.",
            AbilityMechanic::ReduceAttackCost {
                energy_type: EnergyType::Grass,
                amount: 1,
                scope: AttackCostReductionScope::SelfIfToolAttached,
            },
        );
        map.insert(
            "If this Pokémon has any Energy attached, it has no Retreat Cost.",
            AbilityMechanic::NoRetreatIfHasEnergy,
        );
        map.insert(
            "If this Pokémon has full HP, it takes -40 damage from attacks from your opponent's Pokémon.",
            AbilityMechanic::ReduceDamageAtFullHp { amount: 40 },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 10 damage to each of your opponent's Pokémon.",
            AbilityMechanic::DamageOnKnockoutInActive {
                amount: 10,
                target: KnockoutDamageTarget::EachOpponentPokemon,
            },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 50 damage to the Attacking Pokémon.",
            AbilityMechanic::DamageOnKnockoutInActive {
                amount: 50,
                target: KnockoutDamageTarget::Attacker,
            },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, flip a coin. If heads, the Attacking Pokémon is Knocked Out.",
            AbilityMechanic::CoinFlipToKnockOutAttackerOnKnockout,
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, move all [F] Energy from this Pokémon to 1 of your Benched Pokémon.",
            AbilityMechanic::MoveAllTypedEnergyToBenchOnKnockout {
                energy_type: EnergyType::Fighting,
            },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon.",
            AbilityMechanic::CounterattackDamage { amount: 20 },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, take a [W] Energy from your Energy Zone and attach it to 1 of your Benched Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToBenchOnDamaged {
                energy_type: EnergyType::Water,
            },
        );
        map.insert(
            "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, the Attacking Pokémon is now Poisoned.",
            AbilityMechanic::PoisonAttackerOnDamaged,
        );
        map.insert(
            "If this Pokémon is in the Active Spot, once during your turn, you may switch in 1 of your opponent's Benched Basic Pokémon to the Active Spot.",
            AbilityMechanic::VictreebelFragranceTrap,
        );
        map.insert(
            "If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP becomes 10.",
            AbilityMechanic::CoinFlipToSurviveKnockOut,
        );
        map.insert(
            "If you have Arceus or Arceus ex in play, attacks used by this Pokémon cost 1 less [C] Energy.",
            AbilityMechanic::ReduceAttackCost {
                energy_type: EnergyType::Colorless,
                amount: 1,
                scope: AttackCostReductionScope::SelfIfArceusInPlay,
            },
        );
        map.insert(
            "If you have Arceus or Arceus ex in play, attacks used by this Pokémon do +30 damage to your opponent's Active Pokémon.",
            AbilityMechanic::IncreaseDamageIfArceusInPlay { amount: 30 },
        );
        map.insert(
            "If you have another Falinks in play, this Pokémon's attacks do +20 damage to your opponent's Active Pokémon, and this Pokémon takes -20 damage from attacks from your opponent's Pokémon.",
            AbilityMechanic::CoordinatedUnit {
                pokemon_name: "Falinks",
                damage_bonus: 20,
                damage_reduction: 20,
            },
        );
        map.insert(
            "If you have Arceus or Arceus ex in play, this Pokémon takes -30 damage from attacks.",
            AbilityMechanic::ReduceDamageIfArceusInPlay { amount: 30 },
        );
        map.insert(
            "If you have Arceus or Arceus ex in play, this Pokémon has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::ThisPokemon,
                condition: NoRetreatCostCondition::NamedPokemonInPlay(ARCEUS_NAMES),
            },
        );
        map.insert(
            "If you have Latias in play, this Pokémon has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::ThisPokemon,
                condition: NoRetreatCostCondition::NamedPokemonInPlay(&["Latias"]),
            },
        );
        map.insert(
            "If your opponent's Pokémon is Knocked Out by damage from this Pokémon's attacks, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon.",
            AbilityMechanic::ProtectSelfNextTurnAfterAttackKnockout,
        );
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may heal 30 damage from 1 of your Pokémon.",
            AbilityMechanic::HealOneYourPokemon {
                amount: 30,
                require_active: true,
                require_tool_attached: false,
            },
        );
        map.insert(
            "Once during your turn, if this Pokémon has a Pokémon Tool attached, you may heal 30 damage from 1 of your Pokémon.",
            AbilityMechanic::HealOneYourPokemon {
                amount: 30,
                require_active: false,
                require_tool_attached: true,
            },
        );
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may look at a random Supporter card from your opponent's hand. Use the effect of that card as the effect of this Ability.",
            AbilityMechanic::CopyRandomOpponentHandSupporter,
        );
        map.insert("Once during your turn, if this Pokémon is in the Active Spot, you may make your opponent's Active Pokémon Poisoned.", AbilityMechanic::PoisonOpponentActive);
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may switch in 1 of your opponent's Benched Pokémon that has damage on it to the Active Spot.",
            AbilityMechanic::SwitchDamagedOpponentBenchToActive,
        );
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may take a [G] Energy from your Energy Zone and attach it to 1 of your [G] Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToYourTypedPokemon {
                energy_type: EnergyType::Grass,
            },
        );
        map.insert(
            "Once during your turn, if this Pokémon is on your Bench, you may discard all Pokémon Tools from your opponent's Active Pokémon. If you do, discard this Pokémon.",
            AbilityMechanic::DiscardOpponentActiveToolsAndDiscardSelf,
        );
        map.insert(
            "Once during your turn, if this Pokémon is on your Bench, you may switch it with your Active Pokémon.",
            AbilityMechanic::SwitchThisBenchWithActive,
        );
        map.insert(
            "Once during your turn, if you have Arceus or Arceus ex in play, you may do 30 damage to your opponent's Active Pokémon.",
            AbilityMechanic::DamageOpponentActiveIfArceusInPlay { amount: 30 },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may discard a random Energy from your opponent's Active Pokémon.",
            AbilityMechanic::DiscardRandomEnergyFromOpponentActiveOnEvolve,
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may draw 2 cards.",
            AbilityMechanic::DrawCardsOnEvolve { amount: 2 },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may have your opponent shuffle their hand into their deck. For each remaining point that your opponent needs to win, they draw a card.",
            AbilityMechanic::OpponentShuffleHandAndDrawOnEvolve,
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may heal 60 damage from 1 of your [W] Pokémon.",
            AbilityMechanic::HealTypedPokemonOnEvolve {
                energy_type: EnergyType::Water,
                amount: 60,
            },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may put 2 random Pokémon Tool cards from your discard pile into your hand.",
            AbilityMechanic::PutCardsFromDiscardToHandOnEvolve {
                card_kind: DiscardSearchKind::Tool,
                selection: DiscardSelection::RandomCards(2),
            },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may put a Supporter card from your discard pile into your hand.",
            AbilityMechanic::PutCardsFromDiscardToHandOnEvolve {
                card_kind: DiscardSearchKind::Supporter,
                selection: DiscardSelection::PlayerChoosesOne,
            },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may take a [R] Energy from your Energy Zone and attach it to your Active [R] Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToActiveTypedOnEvolve {
                energy_type: EnergyType::Fire,
            },
        );
        map.insert(
            "Once during your turn, when you put this Pokémon from your hand onto your Bench, you may have your opponent reveal their hand.",
            AbilityMechanic::InfiltratingInspection,
        );
        map.insert(
            "Once during your turn, you may attach a [R] Energy from your discard pile to this Pokémon. If you do, do 20 damage to this Pokémon.",
            AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage {
                energy_type: EnergyType::Fire,
                self_damage: 20,
            },
        );
        map.insert(
            "Once during your turn, you may choose either player. Look at the top card of that player's deck.",
            AbilityMechanic::LookAtTopCardOfDeck {
                either_player: true,
            },
        );
        map.insert(
            "Once during your turn, you may discard the top card of your opponent's deck.",
            AbilityMechanic::DiscardTopCardOpponentDeck,
        );
        map.insert(
            "Once during your turn, you may do 20 damage to 1 of your opponent's Pokémon.",
            AbilityMechanic::DamageOneOpponentPokemon { amount: 20 },
        );
        map.insert(
            "Once during your turn, you may flip a coin. If heads, switch in 1 of your opponent's Benched Pokémon to the Active Spot.",
            AbilityMechanic::CoinFlipSwitchInOpponentBenchToActive,
        );
        map.insert(
            "Once during your turn, you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep.",
            AbilityMechanic::CoinFlipStatusOpponentActive {
                status: StatusCondition::Asleep,
            },
        );
        map.insert(
            "Once during your turn, you may flip a coin. If heads, your opponent's Active Pokémon is now Poisoned.",
            AbilityMechanic::CoinFlipStatusOpponentActive {
                status: StatusCondition::Poisoned,
            },
        );
        map.insert(
            "Once during your turn, you may heal 10 damage from each of your Pokémon.",
            AbilityMechanic::HealAllYourPokemon {
                amount: 10,
                energy_type: None,
            },
        );
        map.insert(
            "Once during your turn, you may heal 20 damage from each of your Pokémon.",
            AbilityMechanic::HealAllYourPokemon {
                amount: 20,
                energy_type: None,
            },
        );
        map.insert(
            "Once during your turn, you may heal 20 damage from your Active Pokémon.",
            AbilityMechanic::HealActiveYourPokemon { amount: 20 },
        );
        map.insert(
            "Once during your turn, you may heal 30 damage from each of your [W] Pokémon.",
            AbilityMechanic::HealAllYourPokemon {
                amount: 30,
                energy_type: Some(EnergyType::Water),
            },
        );
        map.insert(
            "Once during your turn, you may look at the top card of your deck.",
            AbilityMechanic::LookAtTopCardOfDeck {
                either_player: false,
            },
        );
        map.insert(
            "Once during your turn, you may make your opponent's Active Pokémon Burned.",
            AbilityMechanic::BurnOpponentActive,
        );
        map.insert(
            "Once during your turn, you may move all [D] Energy from each of your Pokémon to this Pokémon.",
            AbilityMechanic::MoveAllTypedEnergyFromYourPokemonToSelf {
                energy_type: EnergyType::Darkness,
            },
        );
        map.insert(
            "Once during your turn, you may move all [P] Energy from 1 of your Benched [P] Pokémon to your Active Pokémon.",
            AbilityMechanic::MoveAllTypedEnergyFromBenchToActive {
                energy_type: EnergyType::Psychic,
            },
        );
        map.insert(
            "Once during your turn, you may put a random Pokémon Tool card from your deck into your hand.",
            AbilityMechanic::SearchRandomCardFromDeck {
                card_kind: DeckSearchKind::Tool,
            },
        );
        map.insert(
            "Once during your turn, you may put a random Pokémon from your deck into your hand.",
            AbilityMechanic::SearchRandomCardFromDeck {
                card_kind: DeckSearchKind::Pokemon,
            },
        );
        // Note the non-breaking space before "(Your opponent ...": the database text uses U+00A0
        // there, exactly like the non-Basic printing below, so the key must too.
        map.insert(
            "Once during your turn, you may switch out your opponent's Active Basic Pok\u{e9}mon to the Bench.\u{a0}(Your opponent chooses the new Active Pok\u{e9}mon.)",
            AbilityMechanic::SwitchOutOpponentActiveToBench {
                require_active: false,
                require_opponent_active_basic: true,
            },
        );
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)",
            AbilityMechanic::SwitchOutOpponentActiveToBench {
                require_active: true,
                require_opponent_active_basic: false,
            },
        );
        map.insert(
            "Once during your turn, you may switch out your opponent's Active Pok\u{e9}mon to the Bench.\u{a0}(Your opponent chooses the new Active Pok\u{e9}mon.)",
            AbilityMechanic::SwitchOutOpponentActiveToBench {
                require_active: false,
                require_opponent_active_basic: false,
            },
        );
        map.insert(
            "Once during your turn, you may switch your Active Ultra Beast with 1 of your Benched Ultra Beasts.",
            AbilityMechanic::SwitchActiveUltraBeastWithBench,
        );
        map.insert("Once during your turn, you may switch your Active [W] Pokémon with 1 of your Benched Pokémon.", AbilityMechanic::SwitchActiveTypedWithBench { energy_type: EnergyType::Water });
        map.insert(
            "Once during your turn, you may take 2 [D] Energy from your Energy Zone and attach it to this Pokémon. If you do, do 30 damage to this Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToSelfAndDamage {
                energy_type: EnergyType::Darkness,
                amount: 2,
                self_damage: 30,
            },
        );
        map.insert(
            "Once during your turn, you may take a [L] Energy from your Energy Zone and attach it to this Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToSelf {
                energy_type: EnergyType::Lightning,
                amount: 1,
            },
        );
        map.insert(
            "Once during your turn, you may take a [W] Energy from your Energy Zone and attach it to this Pokémon.",
            AbilityMechanic::AttachEnergyFromZoneToSelf {
                energy_type: EnergyType::Water,
                amount: 1,
            },
        );
        map.insert(
            "Once during your turn, you may take a [P] Energy from your Energy Zone and attach it to the [P] Pokémon in the Active Spot.",
            AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon {
                energy_type: EnergyType::Psychic,
            },
        );
        map.insert(
            "Once during your turn, you may take a [P] Energy from your Energy Zone and attach it to this Pokémon. If you use this Ability, your turn ends.",
            AbilityMechanic::AttachEnergyFromZoneToSelfAndEndTurn {
                energy_type: EnergyType::Psychic,
            },
        );
        map.insert(
            "Pokémon (both yours and your opponent's) can't be healed.",
            AbilityMechanic::PreventAllHealing,
        );
        map.insert(
            "Prevent all damage done to this Pokémon by attacks from your opponent's Pokémon ex.",
            AbilityMechanic::PreventAllDamageFromEx,
        );
        map.insert(
            "Prevent all effects of attacks used by your opponent's Pokémon done to this Pokémon.",
            AbilityMechanic::PreventAttackEffects,
        );
        map.insert(
            "This Ability works if you have any Unown in play with an Ability other than POWER. Attacks used by your Pokémon do +10 damage to your opponent's Active Pokémon.",
            AbilityMechanic::UnownPower { amount: 10 },
        );
        map.insert(
            "This Ability works if you have any Unown in play with an Ability other than GUARD. All of your Pokémon take -10 damage from attacks from your opponent's Pokémon.",
            AbilityMechanic::UnownGuard { amount: 10 },
        );
        map.insert(
            "This Pokémon can evolve into any Pokémon that evolves from Eevee if you play it from your hand onto this Pokémon. (This Pokémon can't evolve during your first turn or the turn you play it.)",
            AbilityMechanic::CanEvolveIntoEeveeEvolution,
        );
        map.insert(
            "This Pokémon can't be Asleep.",
            AbilityMechanic::ImmuneToStatusConditions {
                status: Some(StatusCondition::Asleep),
            },
        );
        map.insert(
            "This Pokémon can't be affected by any Special Conditions.",
            AbilityMechanic::ImmuneToStatusConditions { status: None },
        );
        map.insert(
            "This Pokémon gets +30 HP for each [P] Energy attached to it.",
            AbilityMechanic::IncreaseHpPerAttachedEnergy {
                energy_type: EnergyType::Psychic,
                amount: 30,
            },
        );
        map.insert(
            "This Pokémon takes -10 damage from attacks.",
            AbilityMechanic::ReduceDamageFromAttacks { amount: 10 },
        );
        map.insert(
            "This Pokémon takes -20 damage from attacks from [R] or [W] Pokémon.",
            AbilityMechanic::ReduceDamageFromTypedAttackers {
                energy_types: vec![EnergyType::Fire, EnergyType::Water],
                amount: 20,
            },
        );
        map.insert(
            "This Pokémon takes -20 damage from attacks.",
            AbilityMechanic::ReduceDamageFromAttacks { amount: 20 },
        );
        map.insert(
            "This Pokémon takes -30 damage from attacks from [F] Pokémon.",
            AbilityMechanic::ReduceDamageFromTypedAttackers {
                energy_types: vec![EnergyType::Fighting],
                amount: 30,
            },
        );
        map.insert(
            "This Pokémon takes -30 damage from attacks from [R] or [W] Pokémon.",
            AbilityMechanic::ReduceDamageFromTypedAttackers {
                energy_types: vec![EnergyType::Fire, EnergyType::Water],
                amount: 30,
            },
        );
        // Dusknoir (B1 105) "Fade into Darkness" and Glimmora (B3a 045 / B3a 078)
        // "Shattering Crystal". Point DENIAL, not damage prevention — the Pokémon is still
        // Knocked Out and still leaves play, the opponent simply scores nothing for it on heads.
        map.insert(
            "When this Pokémon is Knocked Out, flip a coin. If heads, your opponent can't get any points for it.",
            AbilityMechanic::CoinFlipToDenyKnockoutPoints,
        );
        map.insert(
            "When this Pokémon is first damaged by an attack after coming into play, prevent that damage.",
            AbilityMechanic::PreventFirstAttack,
        );
        map.insert(
            "Whenever you attach a [D] Energy from your Energy Zone to this Pokémon, do 20 damage to your opponent's Active Pokémon.",
            AbilityMechanic::DamageOpponentActiveOnZoneAttachToSelf {
                energy_type: EnergyType::Darkness,
                amount: 20,
                only_turn_energy: true,
            },
        );
        map.insert(
            "Whenever you attach a [P] Energy from your Energy Zone to this Pokémon, heal 20 damage from this Pokémon.",
            AbilityMechanic::HealSelfOnZoneAttach {
                energy_type: EnergyType::Psychic,
                amount: 20,
            },
        );
        map.insert(
            "Whenever you attach an Energy from your Energy Zone to this Pokémon, put a random card from your deck that evolves from this Pokémon onto this Pokémon to evolve it.",
            AbilityMechanic::RandomEvolutionFromDeck {
                trigger: RandomEvolutionTrigger::OnEnergyZoneAttachToSelf,
            },
        );
        map.insert(
            "You must discard a card from your hand in order to use this Ability. Once during your turn, you may draw a card.",
            AbilityMechanic::DiscardFromHandToDrawCard,
        );
        map.insert(
            "Your Active Dondozo has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::YourActiveNamed("Dondozo"),
                condition: NoRetreatCostCondition::Always,
            },
        );
        map.insert(
            "Your Active Pokémon has no Retreat Cost.",
            AbilityMechanic::NoRetreatCost {
                target: NoRetreatCostTarget::YourActive,
                condition: NoRetreatCostCondition::Always,
            },
        );
        map.insert(
            "Your opponent can't play any Pokémon from their hand to evolve their Active Pokémon.",
            AbilityMechanic::PreventOpponentActiveEvolution,
        );
        map.insert(
            "Your opponent's Active Pokémon takes +10 damage from being Poisoned.",
            AbilityMechanic::IncreasePoisonDamage { amount: 10 },
        );
        map.insert(
            "Your opponent's Active Pokémon's Retreat Cost is 1 more.",
            AbilityMechanic::IncreaseRetreatCostForOpponentActive { amount: 1 },
        );

        // B2 and B2a mechanics
        // NOTE: this effect text carries non-breaking spaces, exactly as printed on B2 097 / B2 173.
        map.insert(
            "Basic Pokémon in play (both yours and your opponent's) have no Abilities.",
            AbilityMechanic::SuppressBasicAbilities,
        );
        map.insert(
            "If this Pokémon's remaining HP is 50 or less, attacks used by this Pokémon do +60 damage to your opponent's Active Pokémon.",
            AbilityMechanic::IncreaseDamageWhenRemainingHpAtMost {
                amount: 60,
                hp_threshold: 50,
            },
        );
        map.insert(
            "Once during your turn, you may discard 1 [R] Energy from this Pokémon in order to use this Ability. During this turn, attacks used by your [R] Pokémon do +50 damage to your opponent's Active Pokémon.",
            AbilityMechanic::DiscardEnergyToIncreaseTypeDamage {
                discard_energy: EnergyType::Fire,
                attack_type: EnergyType::Fire,
                amount: 50,
            },
        );
        map.insert(
            "Once during your turn, you may heal 60 damage from 1 of your Pokémon ex that has any Energy attached. If you do, discard a random Energy from that Pokémon.",
            AbilityMechanic::HealOneYourPokemonExAndDiscardRandomEnergy { amount: 60 },
        );
        // Both "switch out your opponent's Active [Basic] Pokémon to the Bench" texts are
        // mapped further up; the generator emitted duplicates of them here.
        map.insert(
            "Once during your turn, you may take a [W] Energy from your Energy Zone and attach it to the [W] Pokémon in the Active Spot.",
            AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon {
                energy_type: EnergyType::Water,
            },
        );
        map.insert(
            "This Pokémon takes -30 damage from attacks.",
            AbilityMechanic::ReduceDamageFromAttacks { amount: 30 },
        );

        // b2b mechanics
        map.insert(
            "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon.",
            AbilityMechanic::BadDreamsEndOfTurn { amount: 20 },
        );
        map.insert("Once during your turn, you may switch your Active [M] Pokémon with 1 of your Benched Pokémon.", AbilityMechanic::SwitchActiveTypedWithBench { energy_type: EnergyType::Metal });

        // b3a mechanics
        map.insert(
            "Once during your turn, when you put this Pokémon from your hand onto your Bench, you may switch it with your Active Pokémon. If you do, move all of your Energy in play to this Pokémon.",
            AbilityMechanic::LegendaryDrive,
        );
        map.insert(
            "Once during your turn, when you put this Pokémon from your hand onto your Bench, you may switch out your opponent's Active Pokémon to the Bench. (Your opponent chooses the new Active Pokémon.)",
            AbilityMechanic::AncientRoar,
        );
        map.insert(
            "Attacks used by your Future Pokémon cost 1 less [C] Energy.",
            AbilityMechanic::ReduceAttackCost {
                energy_type: EnergyType::Colorless,
                amount: 1,
                scope: AttackCostReductionScope::YourFuturePokemon,
            },
        );

        // b3 mechanics
        map.insert(
            "As long as this Pokémon is in play, it is [F] and [D] type.",
            AbilityMechanic::DualType {
                types: [EnergyType::Fighting, EnergyType::Darkness],
            },
        );
        map.insert(
            "As long as this Pokémon is in play, it is [W] and [F] type.",
            AbilityMechanic::DualType {
                types: [EnergyType::Water, EnergyType::Fighting],
            },
        );
        map.insert(
            "As long as this Pokémon is on your Bench, your Active [D] Pokémon's Retreat Cost is 1 less.",
            AbilityMechanic::ReduceRetreatCostOfYourActiveTypedFromBench {
                energy_type: EnergyType::Darkness,
                amount: 1,
            },
        );
        map.insert(
            "During Pokémon Checkup, if this Pokémon is in the Active Spot, do 10 damage to each of your opponent's Pokémon.",
            AbilityMechanic::CheckupDamageToAllOpponentPokemon { amount: 10 },
        );
        map.insert(
            "If you don't have Regirock, Regice, and Registeel on your Bench, this Pokémon can't attack.",
            AbilityMechanic::CannotAttackWithoutBenchedNames {
                required_bench_names: REGI_TRIO_NAMES,
            },
        );
        // DELIBERATELY UNIMPLEMENTED — Victini's Victory Star (B3 025 / P-B 049).
        //
        // "Once during your turn, after you flip any coins for an attack of 1 of your [R] Pokémon,
        // you may ignore all results of those coin flips and begin flipping those coins again."
        //
        // Every other coin effect in deckgym is resolved at *forecast* time: `Outcomes` enumerates
        // one branch per coin result, `apply_action` samples a branch and immediately runs its
        // mutation. Victory Star needs a player decision *between* those two steps — the player has
        // to see the flips, then choose whether to discard that result and resample from the same
        // distribution. There is no point in the engine where a sampled-but-not-yet-applied outcome
        // is offered to a player, and by the time the `move_generation_stack` could carry the
        // decision the attack has already resolved (damage, knockouts, promotions, end of turn), so
        // there is nothing left to take back.
        //
        // Implementing it faithfully means a new subsystem: splitting outcome resolution into
        // "sample" / "offer" / "commit", retaining the pre-attack state so a re-roll can resample
        // from it, and teaching the search bots to price a decision node nested inside a chance
        // node. The two shortcuts are both wrong and are deliberately not taken: pre-committing to
        // the re-roll before seeing the flips is mathematically identical to flipping once (the
        // Ability would be a silent no-op), and "keep whichever result had more heads" invents a
        // policy the player never chose. Modelled as inert instead.
        //
        // map.insert("Once during your turn, after you flip any coins for an attack of 1 of your [R] Pokémon, you may ignore all results of those coin flips and begin flipping those coins again. You can't use more than 1 Victory Star Ability each turn.", todo_implementation);
        map.insert(
            "Once during your turn, if this Pokémon is in the Active Spot, you may make your opponent's Active Pokémon Confused.",
            AbilityMechanic::ConfuseOpponentActive,
        );
        map.insert(
            "Once during your turn, if this Pokémon is on your Bench, you may move 30 damage that your Active Pokémon has on it to this Pokémon.",
            AbilityMechanic::MoveFixedDamageFromActiveToThisBenched { amount: 30 },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may do 20 damage to your opponent's Active Pokémon.",
            AbilityMechanic::DamageOpponentActiveOnEvolve { amount: 20 },
        );
        map.insert(
            "Once during your turn, when you play this Pokémon from your hand to evolve 1 of your Pokémon, you may do 30 damage to your opponent's Active Pokémon.",
            AbilityMechanic::DamageOpponentActiveOnEvolve { amount: 30 },
        );
        map.insert(
            "Once during your turn, you may remove a random Special Condition from your Active Pokémon.",
            AbilityMechanic::RemoveRandomSpecialConditionFromActive,
        );

        // b3b mechanics
        map.insert(
            "At the end of your opponent's turn, if this Pokémon is in the Active Spot, put a random card from your deck that evolves from this Pokémon onto this Pokémon to evolve it.",
            AbilityMechanic::RandomEvolutionFromDeck {
                trigger: RandomEvolutionTrigger::EndOfOpponentTurnIfActive,
            },
        );
        map
    });

pub fn ability_mechanic_from_effect(effect: &str) -> Option<&'static AbilityMechanic> {
    EFFECT_ABILITY_MECHANIC_MAP.get(effect)
}

pub fn get_ability_mechanic(card: &Card) -> Option<&'static AbilityMechanic> {
    let Card::Pokemon(pokemon) = card else {
        return None;
    };

    if let Some(ability) = &pokemon.ability {
        let mechanic = ability_mechanic_from_effect(&ability.effect);
        if let Some(mechanic) = mechanic {
            Some(mechanic)
        } else {
            None
        }
    } else {
        None
    }
}

pub fn has_ability_mechanic(card: &Card, mechanic: &AbilityMechanic) -> bool {
    get_ability_mechanic(card) == Some(mechanic)
}

/// The Ability a Pokémon **in play** actually has right now, i.e. after board-wide Ability
/// suppression (Power of Alchemy, Alolan Muk B2 097 / B2 173: "Basic Pokémon in play — both yours
/// and your opponent's — have no Abilities").
///
/// This is the single chokepoint for that question. Every read of an in-play Pokémon's Ability —
/// move generation, the passive hooks, retreat costs, the abilities-as-effects derivation in
/// `PlayedCard::get_effective_card_effects` — goes through here rather than through
/// [`get_ability_mechanic`], so suppression can never be half-applied. `get_ability_mechanic`
/// remains the *raw* printed lookup and is correct only for cards that are not in play yet (a card
/// still in hand being placed or evolved into) or that can never be Basic.
pub(crate) fn get_in_play_ability_mechanic(
    state: &State,
    pokemon: &PlayedCard,
) -> Option<&'static AbilityMechanic> {
    if abilities_switched_off(state, pokemon) {
        return None;
    }
    get_ability_mechanic(&pokemon.card)
}

/// The two ways an in-play Pokémon can lose its printed Ability: board-wide suppression of Basic
/// Pokémon (Alolan Muk's Power of Alchemy) and a per-Pokémon `CardEffect::NoAbilities` applied by
/// an attack (Budew's Prickly Powder). Kept together here so both chokepoint accessors — and
/// therefore every Ability read in the engine — apply them identically.
pub(crate) fn abilities_switched_off(state: &State, pokemon: &PlayedCard) -> bool {
    if pokemon.card.is_basic() && basic_abilities_suppressed(state) {
        return true;
    }
    // `get_active_effects` (the raw stored list) rather than `get_effective_card_effects`, which
    // derives effects *from* abilities and would recurse back into this function.
    pokemon
        .get_active_effects()
        .iter()
        .any(|effect| matches!(effect, CardEffect::NoAbilities))
}

/// The suppression-aware lookup for a card that is *entering* play — being placed onto the Bench
/// or evolved into — where there is no `PlayedCard` yet. Same gate as
/// [`get_in_play_ability_mechanic`]; it exists only because the trigger hooks run against the
/// `Card` that was just played.
pub(crate) fn get_entering_play_ability_mechanic(
    state: &State,
    card: &Card,
) -> Option<&'static AbilityMechanic> {
    if card.is_basic() && basic_abilities_suppressed(state) {
        return None;
    }
    get_ability_mechanic(card)
}

/// Whether an in-play Pokémon has *any* Ability at all right now — the question asked by the cards
/// that care about the presence of an Ability rather than which one it is (Team, and the attacks
/// that do more damage "if your opponent's Active Pokémon has an Ability").
///
/// Keyed on the *printed* Ability rather than on whether deckgym implements it, so an
/// unimplemented Ability still counts as an Ability; the only thing that takes it away is
/// board-wide suppression.
pub(crate) fn has_any_in_play_ability(state: &State, pokemon: &PlayedCard) -> bool {
    pokemon.card.get_ability().is_some() && !abilities_switched_off(state, pokemon)
}

/// [`get_in_play_ability_mechanic`] + equality, the suppression-aware counterpart of
/// [`has_ability_mechanic`].
pub(crate) fn has_in_play_ability_mechanic(
    state: &State,
    pokemon: &PlayedCard,
    mechanic: &AbilityMechanic,
) -> bool {
    get_in_play_ability_mechanic(state, pokemon) == Some(mechanic)
}

/// Whether any Pokémon in play (either side — the Ability is symmetric) is switching off the
/// Abilities of Basic Pokémon.
///
/// Uses the *raw* lookup deliberately: asking the suppression-aware accessor here would be
/// self-referential, and a Basic printing of this Ability would have to decide whether it turns
/// itself off. The question does not arise in practice — every printing of Power of Alchemy is on
/// a Stage 1 Alolan Muk, which is not a "Basic Pokémon in play" and therefore never suppresses
/// itself (see `test_power_of_alchemy_suppresses_a_basics_passive_ability`, where Muk is the only
/// Ability holder on the board).
pub(crate) fn basic_abilities_suppressed(state: &State) -> bool {
    (0..2).any(|player| {
        state.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
            has_ability_mechanic(&pokemon.card, &AbilityMechanic::SuppressBasicAbilities)
        })
    })
}

/// Translate a *self-scoped defensive* passive ability mechanic into the `CardEffect` it presents
/// as while the holder is in play. This is the core of the "abilities-as-effects" model: rather
/// than scanning the board for these abilities, damage code reads a Pokémon's effect list (see
/// `PlayedCard::get_effective_card_effects`), which merges stored effects with the effects derived
/// here. Returns `None` for mechanics that are not effects-on-this-Pokémon (activated abilities,
/// opponent-restrictions like Gengar/Snorlax, auras like Serperior, lifecycle triggers, etc.).
pub fn card_effect_from_ability_mechanic(mechanic: &AbilityMechanic) -> Option<CardEffect> {
    match mechanic {
        AbilityMechanic::ReduceDamageFromAttacks { amount } => {
            Some(CardEffect::ReduceDamageFromAttacks { amount: *amount })
        }
        AbilityMechanic::ReduceOpponentActiveDamage { amount } => {
            Some(CardEffect::ReduceOpponentActiveDamage { amount: *amount })
        }
        AbilityMechanic::PreventAllDamageFromEx => Some(CardEffect::PreventAllDamageFromEx),
        AbilityMechanic::PreventDamageWhileBenched => Some(CardEffect::PreventDamageWhileBenched),
        AbilityMechanic::CoinFlipToPreventDamage => {
            Some(CardEffect::CoinFlipToPreventIncomingDamage)
        }
        AbilityMechanic::CoinFlipToReduceDamage { amount } => {
            Some(CardEffect::CoinFlipToReduceIncomingDamage { amount: *amount })
        }
        _ => None,
    }
}
