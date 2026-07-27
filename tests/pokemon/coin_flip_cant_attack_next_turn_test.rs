use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Origin Forme Dialga (A2a 060) "Time Mash": 100 damage. Flip a coin; if tails, during your next
/// turn this Pokémon can't attack. (Same template as Hippowdon's Crashing Fangs and Oinkologne's
/// Leg Stomp.)
fn dialga_game(seed: u64) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A2a060OriginFormeDialga).with_energy(vec![
            EnergyType::Metal,
            EnergyType::Metal,
            EnergyType::Colorless,
        ])],
        vec![
            // Mega Latios ex: 180 HP, no weakness — survives the 100 so damage is readable.
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    )
}

fn play_will(game: &mut Game<'static>) {
    let will = match get_card_by_enum(CardId::A4156Will) {
        Card::Trainer(trainer_card) => trainer_card,
        _ => panic!("Will should be a Trainer card"),
    };
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(will.clone()));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: will },
        is_stack: false,
    });
}

/// Apply the pending EndTurn for whoever's turn it is, then resolve forced actions (draws).
fn end_turn(game: &mut Game<'static>) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    let end = choices
        .iter()
        .find(|choice| matches!(choice.action, SimpleAction::EndTurn))
        .unwrap_or_else(|| panic!("EndTurn should be available for player {actor}"))
        .clone();
    game.apply_action(&end);
    game.play_until_stable();
}

/// Attack with Time Mash, cycle through the opponent's turn, and report whether Time Mash is
/// offered again on player 0's next turn.
fn time_mash_offered_next_turn(game: &mut Game<'static>) -> bool {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A2a060OriginFormeDialga, 0),
        is_stack: false,
    });

    // Damage is dealt regardless of the coin.
    let state = game.get_state_clone();
    assert_eq!(
        180 - state.get_active(1).get_remaining_hp(),
        100,
        "Time Mash always does 100"
    );

    end_turn(game); // player 0's turn ends
    end_turn(game); // opponent's turn ends

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "it should be player 0's turn again");
    choices.iter().any(
        |choice| matches!(&choice.action, SimpleAction::Attack(attack) if attack.title == "Time Mash"),
    )
}

#[test]
fn test_time_mash_heads_can_attack_next_turn() {
    for seed in 0..10 {
        let mut game = dialga_game(seed);
        play_will(&mut game);
        assert!(
            time_mash_offered_next_turn(&mut game),
            "seed {seed}: after forced heads, Dialga must be able to attack next turn"
        );
    }
}

#[test]
fn test_time_mash_tails_blocks_attack_next_turn() {
    let (mut saw_blocked, mut saw_allowed) = (false, false);
    for seed in 0..40 {
        let mut game = dialga_game(seed);
        if time_mash_offered_next_turn(&mut game) {
            saw_allowed = true;
        } else {
            saw_blocked = true;
        }
        if saw_blocked && saw_allowed {
            break;
        }
    }
    assert!(saw_blocked, "some seed must land tails and block the attack");
    assert!(saw_allowed, "some seed must land heads and allow the attack");
}
