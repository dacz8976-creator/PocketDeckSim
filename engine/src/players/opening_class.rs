//! koa, kob and kor: the B5 candidate "opening Active choice", registered Sept 26
//! (`rl/results/opening_active_census_2026-09-26/REGISTRATION.md`). One players-side classification of every Ability
//! mechanic by where it works, and the setup-evaluation term it feeds. Mirrors `census.py`'s `VARIANT_CLASS` in that
//! folder. Names no card: the classes come from the engine's own mechanic flags and their fields.
//!
//! Who classifies a new variant: the author of the engine change that adds it, in the same commit (a tier-2 change),
//! checked by the phrase test below. No arm is a wildcard, at any level, so a new variant fails to compile until it
//! is classified. The compile error forces a classification, not a correct one; the phrase test is the only check.
#![deny(clippy::wildcard_enum_match_arm)]

use crate::{
    actions::{
        abilities::{
            AbilityMechanic, AttackCostReductionScope, NoRetreatCostCondition, NoRetreatCostTarget,
            RandomEvolutionTrigger,
        },
        get_in_play_ability_mechanic,
    },
    card_logic::get_highest_evolutions,
    models::Card,
    State,
};

/// Switch A's weight: half the Active online score's 500, the kq precedent. Pre-set, not tuned on any table.
pub(crate) const OPENING_FIRST_TURN_ACTIVE_BONUS: f64 = 250.0;
/// Switch B's weight (diagnostic kob only): the same 250, as a penalty.
pub(crate) const OPENING_BENCH_WORKING_PENALTY: f64 = 250.0;
/// Switch R's weight (diagnostic kor only): per Energy of the Active's cheapest own attack.
pub(crate) const OPENING_READINESS_PER_ENERGY: f64 = 100.0;

/// Where an Ability works.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum OpeningPosition {
    /// Only while the holder is in the Active Spot.
    Active,
    /// Only while the holder is on the Bench.
    Bench,
    /// From the Active Spot and the Bench.
    Anywhere,
    /// When the holder is put from the hand onto the Bench.
    BenchEntry,
    /// When the holder is played to evolve (irrelevant to the opening placement).
    Evolve,
}

/// An Ability mechanic's class for the opening: where it works, whether its payoff is confined to the owner's first
/// turn, whether it acts on other Pokémon, the opponent or the owner's draws (`board`) rather than on its holder only,
/// and whether it hurts its holder while Active (`drawback`).
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) struct OpeningAbilityClass {
    pub(crate) position: OpeningPosition,
    pub(crate) first_turn: bool,
    pub(crate) board: bool,
    pub(crate) drawback: bool,
}

impl OpeningAbilityClass {
    /// Class A (switch A, koa): an Ability that works only from the Active Spot and whose payoff is confined to the
    /// owner's first turn (or the turn the holder is played); today exactly `AbilityMechanic::CanEvolveOnFirstTurnIfActive`.
    pub(crate) fn is_first_turn_active_only(&self) -> bool {
        self.position == OpeningPosition::Active && self.first_turn && !self.drawback
    }

    /// Switch B's classes (kob, diagnostic): Bench-only, or working from anywhere in play on other Pokémon, the
    /// opponent or the owner's draws. "Works from the Bench" is not the same as "better there".
    pub(crate) fn is_bench_working(&self) -> bool {
        self.position == OpeningPosition::Bench || (self.position == OpeningPosition::Anywhere && self.board)
    }
}

fn class(position: OpeningPosition, first_turn: bool, board: bool, drawback: bool) -> OpeningAbilityClass {
    OpeningAbilityClass { position, first_turn, board, drawback }
}

/// Every Ability mechanic's class for the opening Active choice (`census.py`'s `VARIANT_CLASS`). Class A: an Ability
/// that works only from the Active Spot and whose payoff is confined to the owner's first turn (or the turn the holder
/// is played); today exactly `AbilityMechanic::CanEvolveOnFirstTurnIfActive`.
pub(crate) fn opening_ability_class(mechanic: &AbilityMechanic) -> OpeningAbilityClass {
    match mechanic {
        AbilityMechanic::CanEvolveOnFirstTurnIfActive => class(OpeningPosition::Active, true, false, false),
        AbilityMechanic::AttachEnergyFromZoneToBenchOnDamaged { .. }
        | AbilityMechanic::AttachEnergyFromZoneToYourTypedPokemon { .. }
        | AbilityMechanic::CheckupDamageToAllOpponentPokemon { .. }
        | AbilityMechanic::CheckupDamageToOpponentActive { .. }
        | AbilityMechanic::CoinFlipToKnockOutAttackerOnKnockout
        | AbilityMechanic::ConfuseOpponentActive
        | AbilityMechanic::CopyRandomOpponentHandSupporter
        | AbilityMechanic::CounterattackDamage { .. }
        | AbilityMechanic::DamageOnKnockoutInActive { .. }
        | AbilityMechanic::ElectromagneticWall
        | AbilityMechanic::EndTurnDrawCardIfActive { .. }
        | AbilityMechanic::IncreaseAttackCostForOpponentActive { .. }
        | AbilityMechanic::MoveAllTypedEnergyToBenchOnKnockout { .. }
        | AbilityMechanic::NoOpponentStadiumInActive
        | AbilityMechanic::NoOpponentSupportInActive
        | AbilityMechanic::PoisonAttackerOnDamaged
        | AbilityMechanic::PoisonOpponentActive
        | AbilityMechanic::ReduceOpponentActiveDamage { .. }
        | AbilityMechanic::StartTurnRandomPokemonToHand { .. }
        | AbilityMechanic::SwitchDamagedOpponentBenchToActive
        | AbilityMechanic::VictreebelFragranceTrap => class(OpeningPosition::Active, false, true, false),
        AbilityMechanic::EndTurnHealSelfIfActive { .. } => class(OpeningPosition::Active, false, false, false),
        AbilityMechanic::CannotAttackWithoutBenchedNames { .. }
        | AbilityMechanic::SleepOnZoneAttachToSelfWhileActive => class(OpeningPosition::Active, false, false, true),
        AbilityMechanic::AttachEnergyFromDiscardToActiveTypedFromBench { .. }
        | AbilityMechanic::DiscardOpponentActiveToolsAndDiscardSelf
        | AbilityMechanic::IncreaseDamageForEvolutionsFromBench { .. }
        | AbilityMechanic::MoveFixedDamageFromActiveToThisBenched { .. }
        | AbilityMechanic::ReduceRetreatCostOfYourActiveBasicFromBench { .. }
        | AbilityMechanic::ReduceRetreatCostOfYourActiveTypedFromBench { .. } => class(OpeningPosition::Bench, false, true, false),
        AbilityMechanic::PreventDamageWhileBenched
        | AbilityMechanic::SwitchThisBenchWithActive => class(OpeningPosition::Bench, false, false, false),
        AbilityMechanic::EndFirstTurnAttachEnergyToSelf { .. } => class(OpeningPosition::Anywhere, true, false, false),
        AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { .. }
        | AbilityMechanic::BurnOpponentActive
        | AbilityMechanic::CheckupHealAllYourPokemon { .. }
        | AbilityMechanic::CoinFlipStatusOpponentActive { .. }
        | AbilityMechanic::CoinFlipSwitchInOpponentBenchToActive
        | AbilityMechanic::DamageOneOpponentPokemon { .. }
        | AbilityMechanic::DamageOpponentActiveIfArceusInPlay { .. }
        | AbilityMechanic::DiscardEnergyToIncreaseTypeDamage { .. }
        | AbilityMechanic::DiscardFromHandToDrawCard
        | AbilityMechanic::DiscardTopCardOpponentDeck
        | AbilityMechanic::DoubleGrassEnergy
        | AbilityMechanic::HealAllYourPokemon { .. }
        | AbilityMechanic::HealOneYourPokemonExAndDiscardRandomEnergy { .. }
        | AbilityMechanic::IncreaseDamageForTwoTypesInPlay { .. }
        | AbilityMechanic::IncreaseDamageForTypeInPlay { .. }
        | AbilityMechanic::IncreaseHpForTypeInPlay { .. }
        | AbilityMechanic::IncreaseRetreatCostForOpponentActive { .. }
        | AbilityMechanic::LookAtTopCardOfDeck { .. }
        | AbilityMechanic::LuxuryCoin
        | AbilityMechanic::MoveAllTypedEnergyFromBenchToActive { .. }
        | AbilityMechanic::MoveDamageFromOneYourPokemonToThisPokemon
        | AbilityMechanic::MoveTypedEnergyFromBenchToActive { .. }
        | AbilityMechanic::PreventAllHealing
        | AbilityMechanic::PreventOpponentActiveEvolution
        | AbilityMechanic::RandomStatusConditionToOpponentActive { .. }
        | AbilityMechanic::RemoveRandomSpecialConditionFromActive
        | AbilityMechanic::RevealRandomOpponentHandCard
        | AbilityMechanic::SearchRandomCardFromDeck { .. }
        | AbilityMechanic::SuppressBasicAbilities
        | AbilityMechanic::SwitchActiveTypedWithBench { .. }
        | AbilityMechanic::SwitchActiveUltraBeastWithBench
        | AbilityMechanic::UnownGuard { .. }
        | AbilityMechanic::UnownPower { .. }
        | AbilityMechanic::VictoryStar => class(OpeningPosition::Anywhere, false, true, false),
        AbilityMechanic::AttachEnergyFromDiscardToSelfAndDamage { .. }
        | AbilityMechanic::AttachEnergyFromZoneToSelf { .. }
        | AbilityMechanic::AttachEnergyFromZoneToSelfAndDamage { .. }
        | AbilityMechanic::AttachEnergyFromZoneToSelfAndEndTurn { .. }
        | AbilityMechanic::CanEvolveIntoEeveeEvolution
        | AbilityMechanic::CoinFlipToDenyKnockoutPoints
        | AbilityMechanic::CoinFlipToPreventDamage
        | AbilityMechanic::CoinFlipToReduceDamage { .. }
        | AbilityMechanic::CoinFlipToSurviveKnockOut
        | AbilityMechanic::CoordinatedUnit { .. }
        | AbilityMechanic::DualType { .. }
        | AbilityMechanic::HealSelfOnZoneAttach { .. }
        | AbilityMechanic::ImmuneToStatusConditions { .. }
        | AbilityMechanic::IncreaseDamageIfArceusInPlay { .. }
        | AbilityMechanic::IncreaseDamageWhenRemainingHpAtMost { .. }
        | AbilityMechanic::IncreaseHpPerAttachedEnergy { .. }
        | AbilityMechanic::MoveAllTypedEnergyFromYourPokemonToSelf { .. }
        | AbilityMechanic::NoRetreatIfHasEnergy
        | AbilityMechanic::PreventAllDamageFromEx
        | AbilityMechanic::PreventAttackEffects
        | AbilityMechanic::PreventFirstAttack
        | AbilityMechanic::ProtectSelfNextTurnAfterAttackKnockout
        | AbilityMechanic::ReduceDamageAtFullHp { .. }
        | AbilityMechanic::ReduceDamageFromAttacks { .. }
        | AbilityMechanic::ReduceDamageFromTypedAttackers { .. }
        | AbilityMechanic::ReduceDamageIfArceusInPlay { .. }
        | AbilityMechanic::ReduceOwnRetreatCostIfAnotherSameNameInPlay { .. }
        | AbilityMechanic::ToolCapacity { .. } => class(OpeningPosition::Anywhere, false, false, false),
        AbilityMechanic::AncientRoar
        | AbilityMechanic::HealActiveTypedOnBenchFromHand { .. }
        | AbilityMechanic::InfiltratingInspection
        | AbilityMechanic::LegendaryDrive => class(OpeningPosition::BenchEntry, false, true, false),
        AbilityMechanic::AttachEnergyFromZoneToActiveTypedOnEvolve { .. }
        | AbilityMechanic::CoinFlipParalyzeOpponentActiveOnEvolve
        | AbilityMechanic::DamageOpponentActiveOnEvolve { .. }
        | AbilityMechanic::DiscardRandomEnergyFromOpponentActiveOnEvolve
        | AbilityMechanic::DrawCardsOnEvolve { .. }
        | AbilityMechanic::HealTypedPokemonOnEvolve { .. }
        | AbilityMechanic::LookAtTopCardsPutTrainerTypeToHandOnEvolve { .. }
        | AbilityMechanic::MoveRandomEnergyFromOpponentActiveToSelfOnEvolve
        | AbilityMechanic::OpponentShuffleHandAndDrawOnEvolve
        | AbilityMechanic::PoisonAndBurnOpponentActiveOnEvolve
        | AbilityMechanic::PutCardsFromDiscardToHandOnEvolve { .. } => class(OpeningPosition::Evolve, false, true, false),
        AbilityMechanic::PreventAllDamageAndEffectsOnEvolve { .. } => class(OpeningPosition::Evolve, false, false, false),
        // Classed by its hook (hooks/core.rs 620 (`apply_bad_dreams_damage_for_owner` collects every in-play holder)): no position phrase in its text.
        AbilityMechanic::BadDreamsEndOfTurn { .. } => class(OpeningPosition::Anywhere, false, true, false),
        // Classed by its hook (state/energy.rs 153 (any slot)): no position phrase in its text.
        AbilityMechanic::DamageOpponentActiveOnZoneAttachToSelf { .. } => class(OpeningPosition::Anywhere, false, true, false),
        // Classed by its hook (move_generation/move_generation_abilities.rs 193 (the gate is only `!card.ability_used`)): no position phrase in its text.
        AbilityMechanic::HealActiveYourPokemon { .. } => class(OpeningPosition::Anywhere, false, true, false),
        // Classed by its hook (actions/apply_action_helpers.rs 253 (counts every in-play holder)): no position phrase in its text.
        AbilityMechanic::IncreasePoisonDamage { .. } => class(OpeningPosition::Anywhere, false, true, false),
        // Classed by its hook (state/mod.rs 1165 (any of the player's Pokémon)): no position phrase in its text.
        AbilityMechanic::SoothingWind { .. } => class(OpeningPosition::Anywhere, false, true, false),
        // Classed by its hook (move_generation/attacks.rs 182 (`has_in_play_ability_mechanic`, any slot)): no position phrase in its text.
        AbilityMechanic::TimeRecall => class(OpeningPosition::Anywhere, false, true, false),
        // Field-dependent: each class is read from the variant's own fields.
        AbilityMechanic::DrawCardsOncePerTurn { amount: _, require_active }
        | AbilityMechanic::HealOneYourPokemon { amount: _, require_active, require_tool_attached: _ }
        | AbilityMechanic::SwitchOutOpponentActiveToBench { require_active, require_opponent_active_basic: _ } => {
            let position = if *require_active { OpeningPosition::Active } else { OpeningPosition::Anywhere };
            class(position, false, true, false)
        }
        AbilityMechanic::NoRetreatCost { target, condition } => {
            let board = match target {
                NoRetreatCostTarget::ThisPokemon => false,
                NoRetreatCostTarget::YourActive | NoRetreatCostTarget::YourActiveNamed(_) => true,
            };
            let first_turn = match condition {
                NoRetreatCostCondition::YourFirstTurn => true,
                NoRetreatCostCondition::Always
                | NoRetreatCostCondition::NamedPokemonInPlay(_)
                | NoRetreatCostCondition::StadiumInPlay => false,
            };
            class(OpeningPosition::Anywhere, first_turn, board, false)
        }
        AbilityMechanic::RandomEvolutionFromDeck { trigger } => {
            let position = match trigger {
                RandomEvolutionTrigger::EndOfOpponentTurnIfActive => OpeningPosition::Active,
                RandomEvolutionTrigger::OnEnergyZoneAttachToSelf => OpeningPosition::Anywhere,
            };
            class(position, false, false, false)
        }
        AbilityMechanic::ReduceAttackCost { energy_type: _, amount: _, scope } => {
            let board = match scope {
                AttackCostReductionScope::YourFuturePokemon => true,
                AttackCostReductionScope::SelfIfArceusInPlay | AttackCostReductionScope::SelfIfToolAttached => false,
            };
            class(OpeningPosition::Anywhere, false, board, false)
        }
    }
}

/// The setup evaluation's opening term for `myself`'s own Active (0 before it is placed), read through the
/// suppression-aware `get_in_play_ability_mechanic`. Switch A (koa): +250 when the Active's Ability is in class A and
/// its highest evolution is in the owner's deck or hand. Switch B (kob): -250 when it is Bench-working. Switch R (kor):
/// -100 per Energy of the Active's cheapest own attack (0 with no attack). Only reached while the opponent's setup is
/// masked (turn 0), so nothing after the opening placement changes.
pub(crate) fn opening_active_term(
    state: &State,
    myself: usize,
    first_turn_active: bool,
    bench_working: bool,
    readiness: bool,
) -> f64 {
    let Some(active) = state.maybe_get_active(myself) else {
        return 0.0;
    };
    let mut term = 0.0;
    if let Some(mechanic) = get_in_play_ability_mechanic(state, active) {
        let class = opening_ability_class(mechanic);
        if first_turn_active && class.is_first_turn_active_only() {
            let own: Vec<Card> =
                state.decks[myself].cards.iter().chain(state.hands[myself].iter()).cloned().collect();
            if !get_highest_evolutions(&active.card, &own).is_empty() {
                term += OPENING_FIRST_TURN_ACTIVE_BONUS;
            }
        }
        if bench_working && class.is_bench_working() {
            term -= OPENING_BENCH_WORKING_PENALTY;
        }
    }
    if readiness {
        let cheapest = active.card.get_attacks().iter().map(|attack| attack.energy_required.len()).min().unwrap_or(0);
        term -= OPENING_READINESS_PER_ENERGY * cheapest as f64;
    }
    term
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        actions::{SimpleAction, EFFECT_ABILITY_MECHANIC_MAP},
        card_ids::CardId,
        database::get_card_by_enum,
        observation::{canonical_actions, PlayerObservation, RevealedKnowledge},
        players::{get_player, PlayerCode},
        Deck,
    };
    use rand::{rngs::StdRng, SeedableRng};
    use std::collections::BTreeMap;

    fn variant_name(mechanic: &AbilityMechanic) -> String {
        format!("{mechanic:?}").split([' ', '(', '{']).next().unwrap().to_string()
    }

    /// Section 4's phrase test. Every map entry's class agrees with its printed condition phrases, both ways:
    /// Active exactly when the text says "this Pokémon is in the Active Spot", Bench exactly when it says "this
    /// Pokémon is on your Bench", first-turn exactly when it says "first turn". The two known exceptions are
    /// `CanEvolveIntoEeveeEvolution` (its "first turn" forbids evolving then) and `CannotAttackWithoutBenchedNames`
    /// (a drawback classed Active because only the Active attacks; its "on your Bench" names other Pokémon). The six
    /// phrase-less flags are classed by their hook (see the arms), which this test cannot check.
    #[test]
    fn every_class_agrees_with_its_printed_position_phrases() {
        let mut exceptions: Vec<String> = Vec::new();
        for (text, mechanic) in EFFECT_ABILITY_MECHANIC_MAP.iter() {
            let class = opening_ability_class(mechanic);
            let agrees = text.contains("this Pokémon is in the Active Spot") == (class.position == OpeningPosition::Active)
                && text.contains("this Pokémon is on your Bench") == (class.position == OpeningPosition::Bench)
                && text.contains("first turn") == class.first_turn;
            if !agrees {
                exceptions.push(variant_name(mechanic));
            }
        }
        exceptions.sort();
        assert_eq!(exceptions, ["CanEvolveIntoEeveeEvolution", "CannotAttackWithoutBenchedNames"]);
    }

    /// The class counts `census.py` and its README (section 3) report, counted as flag settings over the map (a
    /// variant whose own fields change its class counts once per setting): 130 over 124 variants, 156 entries.
    #[test]
    fn the_classes_count_as_the_census_does() {
        let mut settings: BTreeMap<(String, String), ()> = BTreeMap::new();
        for mechanic in EFFECT_ABILITY_MECHANIC_MAP.values() {
            settings.insert((variant_name(mechanic), format!("{:?}", opening_ability_class(mechanic))), ());
        }
        let mut counts: BTreeMap<&str, usize> = BTreeMap::new();
        for (_, class_text) in settings.keys() {
            let class = EFFECT_ABILITY_MECHANIC_MAP
                .values()
                .map(opening_ability_class)
                .find(|c| format!("{c:?}") == *class_text)
                .unwrap();
            let key = match (class.position, class.first_turn, class.board, class.drawback) {
                (_, _, _, true) => "active drawback",
                (OpeningPosition::Active, true, _, _) => "active first turn",
                (OpeningPosition::Active, false, _, _) => "active any time",
                (OpeningPosition::Bench, _, _, _) => "bench only",
                (OpeningPosition::Anywhere, false, true, _) => "anywhere board",
                (OpeningPosition::Anywhere, false, false, _) => "anywhere self",
                (OpeningPosition::Anywhere, true, _, _) => "anywhere first turn",
                (OpeningPosition::Evolve, _, _, _) => "on evolve",
                (OpeningPosition::BenchEntry, _, _, _) => "on bench entry",
            };
            *counts.entry(key).or_default() += 1;
        }
        let expected: BTreeMap<&str, usize> = [
            ("active first turn", 1),
            ("active any time", 26),
            ("active drawback", 2),
            ("bench only", 8),
            ("anywhere board", 44),
            ("anywhere self", 31),
            ("on evolve", 12),
            ("on bench entry", 4),
            ("anywhere first turn", 2),
        ]
        .into_iter()
        .collect();
        assert_eq!(counts, expected);
        assert_eq!(settings.len(), 130);
    }

    const ALTARIA: &str = "Energy: Psychic\n2 B1 196\n1 B1 102\n2 B1 184\n2 B3a 020\n2 B2b 040\n1 A4a 059\n2 P-A 007\n2 B1 225\n1 A1 225\n2 P-A 005\n1 B3 147\n1 B3b 064\n1 B2 153\n";

    /// The opening Active `code` places from `hand` (Basics of the table's Altaria list; the rest of the list is the
    /// deck), decided through `decision_fn` on `PlayerObservation::from_state` at turn 0, where the setup branch runs.
    /// Without `espeon`, the deck's two Espeon B3a 020 are replaced by Potions.
    fn opening(code: PlayerCode, hand: &[CardId], espeon: bool) -> String {
        let mut deck = Deck::from_string(ALTARIA).unwrap().cards;
        for id in hand {
            let card = get_card_by_enum(*id);
            let at = deck.iter().position(|c| *c == card).expect("the hand's Basics are in the list");
            deck.remove(at);
        }
        if !espeon {
            let espeon = get_card_by_enum(CardId::B3a020Espeon);
            deck.iter_mut().filter(|c| **c == espeon).for_each(|c| *c = get_card_by_enum(CardId::PA001Potion));
        }
        let mut game = crate::test_support::get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(vec![], vec![]);
        state.turn_count = 0;
        state.current_player = 0;
        state.move_generation_stack.clear();
        state.hands[0] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        state.decks[0].cards = deck;
        game.set_state(state);
        let real = game.get_state_clone();
        let (actor, mut actions) = real.generate_possible_actions();
        assert_eq!(actor, 0);
        canonical_actions(&mut actions);
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        assert!(observation.visible_state().setup_opponent_hidden);
        let mut player = get_player(Deck::default(), &Deck::default(), &code);
        let chosen = player.decision_fn(&mut StdRng::seed_from_u64(20_000_000_040), &observation, &actions).action;
        let SimpleAction::Place(card, 0) = &chosen else {
            panic!("expected the opening placement, got {chosen:?}");
        };
        card.get_name()
    }

    /// Section 4's hand table (Altaria list; A = koa, B = kob). {Swablu, Eevee} under kob and kp3 is a tie that
    /// goes to the id that sorts last as a string: Swablu B1 196 after Eevee B1 184.
    #[test]
    fn the_registered_setup_hands_open_as_the_table_says() {
        let (darkrai, eevee, igglybuff, swablu) =
            (CardId::B2b040Darkrai, CardId::B1184Eevee, CardId::A4a059Igglybuff, CardId::B1196Swablu);
        let (koa, kob, kp3) =
            (PlayerCode::KOA { max_depth: 3 }, PlayerCode::KOB { max_depth: 3 }, PlayerCode::KP { max_depth: 3 });
        let rows = [
            ([darkrai, eevee], ["Eevee", "Eevee", "Darkrai"]),
            ([igglybuff, eevee], ["Igglybuff", "Igglybuff", "Igglybuff"]),
            ([darkrai, swablu], ["Darkrai", "Swablu", "Darkrai"]),
            ([swablu, eevee], ["Eevee", "Swablu", "Swablu"]),
        ];
        for (hand, expected) in rows {
            let got = [opening(koa.clone(), &hand, true), opening(kob.clone(), &hand, true), opening(kp3.clone(), &hand, true)];
            assert_eq!(got, expected, "hand {hand:?}: koa, kob, kp3");
        }
    }

    /// With no Espeon in the deck or hand, Eevee has no evolution to reach, so switch A does not fire.
    #[test]
    fn switch_a_needs_the_evolution_in_the_deck_or_hand() {
        let hand = [CardId::B2b040Darkrai, CardId::B1184Eevee];
        assert_eq!(opening(PlayerCode::KOA { max_depth: 3 }, &hand, true), "Eevee");
        assert_eq!(opening(PlayerCode::KOA { max_depth: 3 }, &hand, false), "Darkrai");
    }
}
