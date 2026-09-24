use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

fn sponge() -> PlayedCard {
    // Mega Latios ex: 180 HP, no weakness — a safe damage sponge.
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

#[test]
fn test_volcarona_volcanic_ash_discards_fire_then_damages_chosen_pokemon() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1a014Volcarona).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Fire,
                EnergyType::Colorless,
            ]),
        ],
        vec![sponge(), sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1a014Volcarona, 0),
        is_stack: false,
    });

    // The 2 [R] are discarded and the player chooses which opponent Pokémon takes 80.
    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Colorless],
        "Volcanic Ash should discard 2 [R] Energy first"
    );

    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 2, "Active and 1 Benched target");
    assert!(choices
        .iter()
        .all(|c| matches!(c.action, SimpleAction::ApplyDamage { .. })));

    // Choose the benched target.
    let bench_choice = choices
        .iter()
        .find(|c| match &c.action {
            SimpleAction::ApplyDamage { targets, .. } => targets[0].2 == 1,
            _ => false,
        })
        .expect("Bench target should be offered")
        .clone();
    game.apply_action(&bench_choice);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        180,
        "Active takes no damage when the bench is chosen"
    );
    let bench = state.in_play_pokemon[1][1].as_ref().unwrap();
    assert_eq!(bench.get_remaining_hp(), 180 - 80);
}

#[test]
fn test_rapid_strike_urshifu_tornado_shot_discards_water_and_snipes_bench() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu)
            .with_energy(vec![EnergyType::Water, EnergyType::Colorless])],
        vec![sponge(), sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3051RapidStrikeUrshifu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Colorless],
        "Tornado Shot should discard the [W] Energy"
    );

    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 1, "One choice per benched Pokémon");
    game.apply_action(&choices[0]);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 40);
    let bench = state.in_play_pokemon[1][1].as_ref().unwrap();
    assert_eq!(bench.get_remaining_hp(), 180 - 40);
}

#[test]
fn test_rapid_strike_urshifu_tornado_shot_without_bench_still_discards_and_damages() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu)
            .with_energy(vec![EnergyType::Water, EnergyType::Colorless])],
        vec![sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3051RapidStrikeUrshifu, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Colorless]
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 40);
    let (_, choices) = state.generate_possible_actions();
    assert!(
        choices
            .iter()
            .all(|c| !matches!(c.action, SimpleAction::ApplyDamage { .. })),
        "No bench snipe choice without a benched target"
    );
}

#[test]
fn test_walking_wake_sweeping_billow_discards_energy_and_splashes_bench() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a053WalkingWake)
            .with_energy(vec![EnergyType::Fire, EnergyType::Water])],
        vec![sponge(), sponge(), sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a053WalkingWake, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy,
        vec![EnergyType::Fire, EnergyType::Water],
        "Damage resolves before the Energy selection");
    let (_, choices) = state.generate_possible_actions();
    assert_eq!(choices.len(), 2);
    let water = choices.into_iter().find(|choice| matches!(
        &choice.action,
        SimpleAction::ChooseAttackEnergyDiscard { energies, .. }
            if energies == &vec![EnergyType::Water]
    )).expect("Water should be selectable");
    game.apply_action(&water);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
    for idx in 1..=2 {
        let bench = state.in_play_pokemon[1][idx].as_ref().unwrap();
        assert_eq!(
            bench.get_remaining_hp(),
            180 - 20,
            "Each benched Pokémon takes 20"
        );
    }
}

#[test]
fn test_gouging_fire_scorching_interruption_discards_two_and_reduces_damage() {
    let charmander = PlayedCard::new(
        get_card_by_enum(CardId::A1033Charmander),
        0,
        150, // extra HP so it survives the 100 damage
        vec![EnergyType::Fire, EnergyType::Fire],
        false,
        vec![],
    );
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3a054GougingFire).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Lightning,
                EnergyType::Colorless,
            ]),
        ],
        vec![charmander],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a054GougingFire, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy.len(), 3,
        "Damage resolves before the Energy selection");
    let (_, choices) = state.generate_possible_actions();
    assert_eq!(choices.len(), 3);
    let keep_fire = choices.into_iter().find(|choice| matches!(
        &choice.action,
        SimpleAction::ChooseAttackEnergyDiscard { energies, .. }
            if energies == &vec![EnergyType::Lightning, EnergyType::Colorless]
    )).expect("Lightning and Colorless should be selectable");
    game.apply_action(&keep_fire);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 150 - 100);

    let (_, reaction) = game.get_state_clone().generate_possible_actions();
    assert!(matches!(reaction[0].action, SimpleAction::ResolveAttackRetaliation { .. }));
    game.apply_action(&reaction[0]);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });

    // Charmander's Ember (30) is reduced to 0 by the -30 effect.
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::A1033Charmander, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        110,
        "Gouging Fire takes -30 damage during the opponent's next turn (30 - 30 = 0)"
    );
}

#[test]
fn test_raging_bolt_baneful_boom_discards_all_and_knocks_out() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B3a055RagingBolt).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Colorless,
            ]),
        ],
        // A full-HP sponge on the bench; the Active (full 70 HP, undamaged) is KO'd outright.
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), sponge()],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a055RagingBolt, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert!(
        state.get_active(0).attached_energy.is_empty(),
        "Baneful Boom should discard all Energy from the attacker"
    );
    assert_eq!(state.points[0], 1, "The knockout awards its normal points");
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 1, "Opponent must promote a new Active");
    assert!(choices
        .iter()
        .all(|c| matches!(c.action, SimpleAction::Promote { player: 1, .. })));
}

#[test]
fn test_dudunsparce_sudden_drilling_discards_when_evolved_this_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a059Dunsparce)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![sponge().with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Psychic,
        ])],
    );
    let mut state = game.get_state_clone();
    state.hands[0].push(get_card_by_enum(CardId::B3a060Dudunsparce));
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Evolve {
            evolution: get_card_by_enum(CardId::B3a060Dudunsparce),
            in_play_idx: 0,
            from_deck: false,
        },
        is_stack: false,
    });
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a060Dudunsparce, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).attached_energy.len(),
        1,
        "Having evolved this turn, Sudden Drilling discards 2 random opponent Energy"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
}

#[test]
fn test_dudunsparce_sudden_drilling_no_discard_without_evolving_this_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3a060Dudunsparce)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![sponge().with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Psychic,
        ])],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B3a060Dudunsparce, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).attached_energy.len(),
        3,
        "Without evolving this turn no Energy is discarded"
    );
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 60);
}
