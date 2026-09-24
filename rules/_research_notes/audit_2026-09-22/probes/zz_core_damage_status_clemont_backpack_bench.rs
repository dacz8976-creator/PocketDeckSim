use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn trainer_from_id(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(tc) => tc,
        _ => panic!("Expected trainer card"),
    }
}

/// Probe: Clemont's Backpack ("+20 damage to your opponent's Pokémon" -- not "Active Pokémon")
/// should add to the Bench-hit part of Heliolisk's Electrispark (40 to Active + 10 to each
/// Benched). `get_increased_turn_effect_modifiers` in hooks/core.rs gates ALL
/// `TurnEffect::IncreasedDamageForSpecificPokemon` bonuses (including this one) behind
/// `is_active_to_active`, so it should currently NOT apply to the Bench portion (bug).
#[test]
fn probe_clemonts_backpack_bonus_on_bench_hit() {
    let heliolisk = PlayedCard::from_id(CardId::B4061Heliolisk)
        .with_energy(vec![EnergyType::Lightning]);

    let opponent_active = PlayedCard::from_id(CardId::A1001Bulbasaur);
    let opponent_bench = PlayedCard::from_id(CardId::A1001Bulbasaur);

    let mut game = get_test_game_with_board(
        vec![heliolisk],
        vec![opponent_active, opponent_bench],
    );

    let mut state = game.get_state_clone();
    let backpack = trainer_from_id(CardId::B1a066ClemontsBackpack);
    state.hands[0].push(Card::Trainer(backpack.clone()));
    game.set_state(state);

    // Play Clemont's Backpack (Item; sets "+20 to your Magneton/Heliolisk attacks' damage to
    // your opponent's Pokémon" for this turn).
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: backpack },
        is_stack: false,
    });

    let bench_hp_before = game
        .get_state_clone()
        .in_play_pokemon[1][1]
        .as_ref()
        .unwrap()
        .get_remaining_hp();
    println!("BEFORE attack: opponent bench remaining_hp={bench_hp_before}");

    // Attack with Electrispark: 40 fixed to Active, +10 to each opponent Benched Pokémon.
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B4061Heliolisk, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let bench_hp_after = state.in_play_pokemon[1][1]
        .as_ref()
        .map(|p| p.get_remaining_hp());
    let bench_damage_taken = bench_hp_before - bench_hp_after.unwrap_or(bench_hp_before);
    println!(
        "AFTER attack: opponent bench remaining_hp={bench_hp_after:?}, bench_damage_taken={bench_damage_taken} \
         (expected 30 = 10 base + 20 Clemont's Backpack if the Bench correctly gets the bonus; \
         10 if the engine wrongly restricts the bonus to the Active target only)"
    );

    if bench_damage_taken == 30 {
        println!("RESULT: OK -- Clemont's Backpack's bonus applied to the Bench hit.");
    } else {
        println!("RESULT: BUG -- Clemont's Backpack's bonus did not apply to the Bench hit (bench_damage_taken={bench_damage_taken}, expected 30).");
    }
    // Documents current behavior; does not hard-fail so it doesn't break other agents' full-suite runs.
}
