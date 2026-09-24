use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Mew (B2b 030 / 085 / 086) "Miraculous Memory": "1 attack from among the Pokémon in your
/// opponent's hand and deck is chosen at random, and you use the chosen attack as this attack."
fn game_with_opponent_library(seed: u64, hand: Vec<Card>, deck: Vec<Card>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B2b030Mew)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        // Mega Latios ex: 180 HP and no Weakness, so the copied attack's damage is readable
        // straight off the remaining HP.
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut state = game.get_state_clone();
    state.hands[1] = hand;
    state.decks[1].cards = deck;
    game.set_state(state);
    game
}

fn use_miraculous_memory(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B2b030Mew, 0),
        is_stack: false,
    });
    // The copied attack is queued as a single (already randomly chosen) option; resolve it.
    game.play_until_stable();
}

#[test]
fn test_mew_miraculous_memory_uses_an_attack_from_the_opponents_deck() {
    let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
    let mut game = game_with_opponent_library(0, vec![], vec![bulbasaur; 6]);

    use_miraculous_memory(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        140,
        "Vine Whip is the only attack in the opponent's library, so Mew must deal its 40 damage"
    );
}

#[test]
fn test_mew_miraculous_memory_also_reaches_the_opponents_hand() {
    // Nothing to copy in the deck; the only Pokémon is sitting in the opponent's hand.
    let ivysaur = get_card_by_enum(CardId::A1002Ivysaur);
    let erika = get_card_by_enum(CardId::A1219Erika);
    let mut game = game_with_opponent_library(0, vec![ivysaur], vec![erika; 6]);

    use_miraculous_memory(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        120,
        "Razor Leaf (60) from the Ivysaur in the opponent's hand should be the copied attack"
    );
}

/// Negative case: with no Pokémon at all in the opponent's hand or deck there is nothing to copy,
/// and Miraculous Memory (0 printed damage) does nothing.
#[test]
fn test_mew_miraculous_memory_does_nothing_without_any_pokemon_to_copy() {
    let erika = get_card_by_enum(CardId::A1219Erika);
    let mut game = game_with_opponent_library(0, vec![], vec![erika; 6]);

    use_miraculous_memory(&mut game);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "no Pokémon in the opponent's hand or deck means no attack to copy, so no damage"
    );
}

/// The choice is made by the engine, not offered to the player: exactly one attack is picked, and
/// across seeds each of the two candidates is picked at least once.
#[test]
fn test_mew_miraculous_memory_picks_one_attack_at_random() {
    let mut vine_whip = 0;
    let mut razor_leaf = 0;

    for seed in 0..40 {
        let mut game = game_with_opponent_library(
            seed,
            vec![],
            vec![
                get_card_by_enum(CardId::A1001Bulbasaur),
                get_card_by_enum(CardId::A1002Ivysaur),
            ],
        );

        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B2b030Mew, 0),
            is_stack: false,
        });

        let (actor, choices) = game.get_state_clone().generate_possible_actions();
        assert_eq!(actor, 0);
        assert_eq!(
            choices.len(),
            1,
            "seed {seed}: Miraculous Memory chooses the attack itself, so only one option is left"
        );
        let SimpleAction::Attack(attack) = &choices[0].action else {
            panic!(
                "seed {seed}: expected the copied attack, got {:?}",
                choices[0]
            );
        };
        match attack.title.as_str() {
            "Vine Whip" => vine_whip += 1,
            "Razor Leaf" => razor_leaf += 1,
            other => panic!("seed {seed}: unexpected copied attack {other}"),
        }
    }

    assert!(vine_whip > 0, "Vine Whip was never chosen in 40 seeds");
    assert!(razor_leaf > 0, "Razor Leaf was never chosen in 40 seeds");
}
