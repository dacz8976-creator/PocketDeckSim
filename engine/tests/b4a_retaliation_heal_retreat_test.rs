use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
fn pokemon(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id)
}
fn attack(game: &mut Game<'static>, id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, 0),
        is_stack: false,
    });
}
fn dark_attacker(id: CardId) -> PlayedCard {
    pokemon(id).with_energy(vec![
        EnergyType::Darkness,
        EnergyType::Darkness,
        EnergyType::Colorless,
    ])
}
fn arbok_game(own_support: Option<CardId>, defender_support: Option<CardId>) -> Game<'static> {
    let mut own = vec![dark_attacker(CardId::B4a039TeamRocketsArbok)];
    own.extend(own_support.map(pokemon));
    let mut other = vec![pokemon(CardId::A1211Snorlax)];
    other.extend(defender_support.map(pokemon));
    get_initialized_game_with_board(4, 0, 3, own, other)
}
#[test]
fn arbok_measures_the_defenders_retreat_support_on_the_correct_side() {
    for (own, other, damage) in [
        (None, None, 110),
        (Some(CardId::A2a069Shaymin), None, 110),
        (None, Some(CardId::A2a069Shaymin), 100),
        (Some(CardId::B1a006Ariados), None, 120),
        (None, Some(CardId::B1a006Ariados), 110),
    ] {
        let mut game = arbok_game(own, other);
        let hp = game.get_state_clone().get_active(1).get_remaining_hp();
        attack(&mut game, CardId::B4a039TeamRocketsArbok);
        assert_eq!(
            hp - game.get_state_clone().get_active(1).get_remaining_hp(),
            damage,
            "wrong retreat-cost owner: own={own:?}, defender={other:?}"
        );
    }
}
#[test]
fn attacking_players_leaf_does_not_reduce_shadow_seeker_damage() {
    let mut game = arbok_game(None, None);
    let leaf = get_card_by_enum(CardId::A1a068Leaf);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![leaf.clone()];
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: leaf.as_trainer(),
        },
        is_stack: false,
    });
    let hp = game.get_state_clone().get_active(1).get_remaining_hp();
    attack(&mut game, CardId::B4a039TeamRocketsArbok);
    assert_eq!(
        hp - game.get_state_clone().get_active(1).get_remaining_hp(),
        110
    );
}
#[test]
fn muk_heals_only_if_defender_was_poisoned_and_heal_block_still_applies() {
    for (poisoned, blocked, expected_hp) in
        [(false, false, 50), (true, false, 110), (true, true, 50)]
    {
        let mut defender = pokemon(CardId::A1211Snorlax);
        if poisoned {
            defender = defender.with_status_condition(StatusCondition::Poisoned);
        }
        let mut board = vec![defender];
        if blocked {
            board.push(pokemon(CardId::A3a031Claydol));
        }
        let mut game = get_initialized_game_with_board(
            5,
            0,
            3,
            vec![dark_attacker(CardId::B4a041TeamRocketsMuk).with_damage(70)],
            board,
        );
        attack(&mut game, CardId::B4a041TeamRocketsMuk);
        assert_eq!(
            game.get_state_clone().get_active(0).get_remaining_hp(),
            expected_hp
        );
    }
}
fn ninetales() -> PlayedCard {
    pokemon(CardId::A1038Ninetales).with_energy(vec![EnergyType::Fire, EnergyType::Fire])
}
#[test]
fn electrode_active_knockout_retaliates_for_seventy_once() {
    let mut game = get_initialized_game_with_board(
        8,
        0,
        3,
        vec![ninetales()],
        vec![
            pokemon(CardId::B4a020TeamRocketsElectrode),
            pokemon(CardId::A1001Bulbasaur),
        ],
    );
    attack(&mut game, CardId::A1038Ninetales);
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 20);
    assert_eq!(game.get_state_clone().points, [1, 0]);
}
#[test]
fn electrode_does_not_retaliate_without_a_knockout() {
    let mut game = get_initialized_game_with_board(
        8,
        0,
        3,
        vec![pokemon(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![pokemon(CardId::B4a020TeamRocketsElectrode)],
    );
    attack(&mut game, CardId::A1001Bulbasaur);
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 70);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 30);
}
#[test]
fn electrode_poison_knockout_does_not_trigger_attack_retaliation() {
    let mut game = get_initialized_game_with_board(
        8,
        0,
        3,
        vec![ninetales()],
        vec![
            pokemon(CardId::B4a020TeamRocketsElectrode)
                .with_damage(60)
                .with_status_condition(StatusCondition::Poisoned),
            pokemon(CardId::A1001Bulbasaur),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 90);
    assert_eq!(game.get_state_clone().points, [1, 0]);
}
