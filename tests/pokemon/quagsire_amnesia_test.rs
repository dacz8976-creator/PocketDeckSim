use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Quagsire (B3b 037) "Amnesia": "1 of your opponent's Active Pokémon's attacks is chosen at
/// random. During your opponent's next turn, that Pokémon can't use the chosen attack."
fn quagsire() -> PlayedCard {
    PlayedCard::from_id(CardId::B3b037Quagsire).with_energy(vec![
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Colorless,
    ])
}

fn amnesia(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3b037Quagsire, 0),
        is_stack: false,
    });
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn offered_attack_titles(game: &Game<'static>) -> Vec<String> {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "it should be the opponent's turn");
    choices
        .iter()
        .filter_map(|choice| match &choice.action {
            SimpleAction::Attack(attack) => Some(attack.title.clone()),
            _ => None,
        })
        .collect()
}

/// A single-attack Defending Pokémon: the random pick can only land on that one attack, so the
/// lock is fully deterministic.
fn game_with_single_attack_defender(seed: u64) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![quagsire()],
        vec![PlayedCard::new(
            get_card_by_enum(CardId::A1001Bulbasaur),
            0,
            300,
            vec![EnergyType::Grass, EnergyType::Colorless],
            false,
            vec![],
        )],
    )
}

#[test]
fn test_quagsire_amnesia_locks_out_the_defenders_attack() {
    let mut game = game_with_single_attack_defender(0);

    amnesia(&mut game);
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        240,
        "Amnesia does its printed 60 damage"
    );

    end_turn(&mut game, 0);

    assert!(
        offered_attack_titles(&game).is_empty(),
        "Bulbasaur's only attack should be locked out"
    );
}

/// Negative: without Amnesia the same Bulbasaur can attack.
#[test]
fn test_defender_can_attack_without_amnesia() {
    let mut game = game_with_single_attack_defender(0);
    end_turn(&mut game, 0);

    assert_eq!(
        offered_attack_titles(&game),
        vec!["Vine Whip".to_string()],
        "with no Amnesia applied, Vine Whip should be available"
    );
}

/// Negative: the lock covers exactly the opponent's next turn.
#[test]
fn test_quagsire_amnesia_expires_after_one_turn() {
    let mut game = game_with_single_attack_defender(0);

    amnesia(&mut game);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    end_turn(&mut game, 0);

    assert_eq!(
        offered_attack_titles(&game),
        vec!["Vine Whip".to_string()],
        "the attack lock should have expired"
    );
}

/// Exactly one attack is locked, and across seeds both of a two-attack Defending Pokémon's attacks
/// get picked.
#[test]
fn test_quagsire_amnesia_picks_the_locked_attack_at_random() {
    let mut pierce_locked = 0;
    let mut razor_locked = 0;

    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![quagsire()],
            // Decidueye ex: "Pierce the Pain" ([C][C]) and "Razor Leaf" ([G][G]), 170 HP.
            vec![PlayedCard::from_id(CardId::A3012DecidueyeEx)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        );

        amnesia(&mut game);
        end_turn(&mut game, 0);

        let titles = offered_attack_titles(&game);
        assert_eq!(
            titles.len(),
            1,
            "seed {seed}: exactly one of the two attacks should be locked, got {titles:?}"
        );
        match titles[0].as_str() {
            "Razor Leaf" => pierce_locked += 1,
            "Pierce the Pain" => razor_locked += 1,
            other => panic!("seed {seed}: unexpected remaining attack {other}"),
        }
    }

    assert!(
        pierce_locked > 0,
        "\"Pierce the Pain\" was never the locked attack in 40 seeds"
    );
    assert!(
        razor_locked > 0,
        "\"Razor Leaf\" was never the locked attack in 40 seeds"
    );
}
