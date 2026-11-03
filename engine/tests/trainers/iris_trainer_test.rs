use deckgym::{
    actions::SimpleAction,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::{get_initialized_game, get_test_game_with_board, trainer_from_id},
    State,
};
use strum::IntoEnumIterator;

#[test]
fn test_iris_haxorus_ko_ex_pokemon_wins_game() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 1;

    // Haxorus with energy for Frenzied Blade; Mewtwo ex with only 10 HP remaining
    state.set_board(
        vec![PlayedCard::from_id(CardId::B2b056Haxorus).with_energy(vec![
            EnergyType::Fighting,
            EnergyType::Metal,
            EnergyType::Colorless,
        ])],
        vec![PlayedCard::from_id(CardId::A1129MewtwoEx).with_remaining_hp(10)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B2b067Iris)];
    game.set_state(state);

    // Play Iris
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let play_iris = actions
        .iter()
        .find(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Iris"))
        .expect("Iris should be playable");
    game.apply_action(play_iris);

    // Attack with Haxorus (Frenzied Blade)
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let attack = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::Attack(_)))
        .expect("Haxorus should be able to attack");
    game.apply_action(attack);

    // Haxorus KOs ex: 2 pts (ex KO) + 1 pt (Iris bonus) = 3 pts = win
    assert_eq!(
        game.get_state_clone().winner,
        Some(GameOutcome::Win(0)),
        "Player 0 should win after Haxorus KOs opponent's Mewtwo ex with Iris active"
    );
}

/// Iris (B2b 067, B2b 081, B4b 212, B4b 378, B4b 421): "During this turn, if your opponent's Active
/// Pokémon is Knocked Out by damage from an attack used by your Haxorus, you get 1 more point."
const IRIS_PRINTINGS: [CardId; 5] = [
    CardId::B2b067Iris,
    CardId::B2b081Iris,
    CardId::B4b212Iris,
    CardId::B4b378Iris,
    CardId::B4b421Iris,
];

/// "your Haxorus": every printing named "Haxorus". B2b 056, B2b 110 and P-B 045 were counted before
/// R8-10c, which added B4b 176 and B4b 348. Each has only Frenzied Blade ([F][M][C], 50: "This
/// attack does 20 more damage for each Benched Pokémon (both yours and your opponent's).").
const HAXORUS_PRINTINGS: [CardId; 5] = [
    CardId::B2b056Haxorus,
    CardId::B2b110Haxorus,
    CardId::B4b176Haxorus,
    CardId::B4b348Haxorus,
    CardId::PB045Haxorus,
];

/// Every Pokémon in the database whose name holds "Haxorus", in card-id order.
fn haxorus_printings() -> Vec<CardId> {
    CardId::iter()
        .filter(|id| {
            let card = get_card_by_enum(*id);
            matches!(card, Card::Pokemon(_)) && card.get_name().contains("Haxorus")
        })
        .collect()
}

/// Player 1's Active Bulbasaur (A1 001, 70 HP) and a Benched Bulbasaur: Frenzied Blade does
/// 50 + 20 = 70 and Knocks the Active Out, and the game goes on.
fn active_and_benched_bulbasaur() -> Vec<PlayedCard> {
    vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    ]
}

/// Player 0's Active `attacker` with [F][M][C] against `opponent` on turn 3, with only `iris` in
/// hand. Plays that Iris from the legal actions when there is one, then takes the attacker's attack
/// from the legal actions, and returns the state after it.
fn attack_after_iris(attacker: CardId, opponent: Vec<PlayedCard>, iris: Option<CardId>) -> State {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(attacker).with_energy(vec![
            EnergyType::Fighting,
            EnergyType::Metal,
            EnergyType::Colorless,
        ])],
        opponent,
    );
    let mut state = game.get_state_clone();
    state.hands[0] = iris.into_iter().map(get_card_by_enum).collect();
    game.set_state(state);
    assert_eq!(game.get_state_clone().points, [0, 0]);

    if let Some(iris) = iris {
        let iris_id = trainer_from_id(iris).id;
        let (actor, actions) = game.get_state_clone().generate_possible_actions();
        assert_eq!(actor, 0);
        let play_iris = actions
            .iter()
            .find(|a| {
                matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.id == iris_id)
            })
            .unwrap_or_else(|| panic!("{iris:?} should be playable"));
        game.apply_action(play_iris);
        assert!(
            game.get_state_clone().hands[0].is_empty(),
            "{iris:?} should have left the hand"
        );
    }

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let attack = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::Attack(_)))
        .unwrap_or_else(|| panic!("{attacker:?} should be able to attack"));
    game.apply_action(attack);
    game.get_state_clone()
}

/// The set: every Pokémon whose name holds "Haxorus" is named exactly "Haxorus" (no "Haxorus ex"
/// exists) and is one of the 5 printings. A new printing fails here, and is played in the tests
/// below, which read the printings from the database.
#[test]
fn test_every_haxorus_in_the_database_is_one_of_the_five_printings() {
    let printings = haxorus_printings();
    for id in &printings {
        assert_eq!(get_card_by_enum(*id).get_name(), "Haxorus", "{id:?}");
    }
    assert_eq!(printings, HAXORUS_PRINTINGS);
}

/// Every Haxorus printing, after each Iris printing is played this turn, gets 1 more point for
/// Knocking Out the opponent's Active Bulbasaur with Frenzied Blade: 1 + 1.
#[test]
fn test_iris_gives_the_extra_point_to_every_haxorus_printing() {
    for haxorus in haxorus_printings() {
        for iris in IRIS_PRINTINGS {
            let state = attack_after_iris(haxorus, active_and_benched_bulbasaur(), Some(iris));
            assert!(
                state.in_play_pokemon[1][0].is_none(),
                "{haxorus:?} with {iris:?}: the Active Bulbasaur should be Knocked Out"
            );
            assert_eq!(
                state.points,
                [2, 0],
                "{haxorus:?} with {iris:?}: 1 point for the Knock Out and 1 for Iris"
            );
            assert_eq!(state.winner, None, "{haxorus:?} with {iris:?}");
        }
    }
}

/// No Iris this turn: the same Knock Out scores only its own point, for every Haxorus printing.
#[test]
fn test_no_extra_point_for_haxorus_without_iris() {
    for haxorus in haxorus_printings() {
        let state = attack_after_iris(haxorus, active_and_benched_bulbasaur(), None);
        assert!(
            state.in_play_pokemon[1][0].is_none(),
            "{haxorus:?}: the Active Bulbasaur should be Knocked Out"
        );
        assert_eq!(state.points, [1, 0], "{haxorus:?}: no Iris, no extra point");
    }
}

/// "your Haxorus": Fraxure (B2b 055; Dragon Claw, [F][M], 60) Knocking Out the opponent's Active
/// after Iris is played gets no extra point, for every Iris printing.
#[test]
fn test_iris_gives_no_extra_point_to_a_pokemon_that_is_not_haxorus() {
    for iris in IRIS_PRINTINGS {
        let state = attack_after_iris(
            CardId::B2b055Fraxure,
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(10),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            Some(iris),
        );
        assert!(
            state.in_play_pokemon[1][0].is_none(),
            "{iris:?}: the Active Bulbasaur should be Knocked Out"
        );
        assert_eq!(state.points, [1, 0], "{iris:?}: Fraxure is not Haxorus");
    }
}

/// "your opponent's Active Pokémon": a Benched Pokémon Knocked Out by the same attack gets no extra
/// point. Player 1's Active Lilligant (B1 018, 80 + 20 HP under its own Toughness Aroma) carries 70
/// damage, and Frenzied Blade does 50 + 2 x 20 = 90. The Benched Bulbasaur, alive at 10 only through
/// the +20, is Knocked Out in the next wave. 1 + 1 (Iris) for Lilligant and 1 for Bulbasaur: 3, not 4.
#[test]
fn test_iris_gives_no_extra_point_for_a_benched_knock_out() {
    for haxorus in haxorus_printings() {
        let state = attack_after_iris(
            haxorus,
            vec![
                PlayedCard::from_id(CardId::B1018Lilligant).with_damage(70),
                PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(80),
                PlayedCard::from_id(CardId::A1094Pikachu),
            ],
            Some(CardId::B2b067Iris),
        );
        assert!(
            state.in_play_pokemon[1][0].is_none(),
            "{haxorus:?}: the Active Lilligant should be Knocked Out"
        );
        assert!(
            state.in_play_pokemon[1][1].is_none(),
            "{haxorus:?}: the Benched Bulbasaur should be Knocked Out"
        );
        assert_eq!(
            state.points,
            [3, 0],
            "{haxorus:?}: the extra point is for the Active's Knock Out only"
        );
        assert_eq!(state.winner, Some(GameOutcome::Win(0)), "{haxorus:?}");
    }
}
