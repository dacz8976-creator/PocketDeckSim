use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
    State,
};

fn attack_with(card: PlayedCard, own_bench: Vec<PlayedCard>, opponent: Vec<PlayedCard>) -> State {
    let card_id = card_id_of(&card);
    let mut own_board = vec![card];
    own_board.extend(own_bench);

    let mut game = get_test_game_with_board(own_board, opponent);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

fn card_id_of(card: &PlayedCard) -> CardId {
    CardId::from_card_id(card.get_id().as_str()).expect("test cards should be known card ids")
}

// =================================================================================================
// Toxtricity ex (B2 055 / B2 184 / B2 198) "Damaging Spark": 90 damage, and "This attack also does
// 30 damage to each of your opponent's Benched Pokémon that has damage on it."
// =================================================================================================

#[test]
fn test_damaging_spark_only_hits_benched_pokemon_that_already_have_damage() {
    let state = attack_with(
        PlayedCard::from_id(CardId::B2055ToxtricityEx).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Lightning,
            EnergyType::Colorless,
        ]),
        vec![],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander).with_damage(10),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        90,
        "the Active Pokémon takes the printed 90"
    );
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        20,
        "the damaged Charmander (60 HP, 10 damage) should take another 30"
    );
    assert_eq!(
        state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        70,
        "the undamaged Bulbasaur should be untouched"
    );
}

/// Negative case: with a completely healthy Bench, Damaging Spark is just its printed damage.
#[test]
fn test_damaging_spark_leaves_an_undamaged_bench_alone() {
    let state = attack_with(
        PlayedCard::from_id(CardId::B2184ToxtricityEx).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Lightning,
            EnergyType::Colorless,
        ]),
        vec![],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );

    assert_eq!(state.get_active(1).get_remaining_hp(), 90);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        60,
        "the undamaged Charmander should stay at its full 60 HP"
    );
    assert_eq!(
        state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        70,
        "the undamaged Bulbasaur should stay at its full 70 HP"
    );
}

// =================================================================================================
// Minun (B2 053 / B2 165) "Buddy Spark" and Magmortar (B2b 013) "Thundering Volcano": bench spread
// that only happens when a specific buddy is on your own Bench.
// =================================================================================================

fn opponent_with_full_bench() -> Vec<PlayedCard> {
    vec![
        PlayedCard::from_id(CardId::PB024MegaLatiosEx),
        PlayedCard::from_id(CardId::A1033Charmander),
        PlayedCard::from_id(CardId::A1001Bulbasaur),
    ]
}

#[test]
fn test_buddy_spark_hits_the_bench_when_plusle_is_benched() {
    let state = attack_with(
        PlayedCard::from_id(CardId::B2053Minun).with_energy(vec![EnergyType::Lightning]),
        vec![PlayedCard::from_id(CardId::B2052Plusle)],
        opponent_with_full_bench(),
    );

    assert_eq!(state.get_active(1).get_remaining_hp(), 150, "180 - 30");
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50,
        "Charmander should take the 10 bench damage"
    );
    assert_eq!(
        state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        60,
        "Bulbasaur should take the 10 bench damage"
    );
}

/// Negative case: without Plusle on the Bench, Buddy Spark is only its printed damage.
#[test]
fn test_buddy_spark_does_nothing_extra_without_plusle() {
    let state = attack_with(
        PlayedCard::from_id(CardId::B2165Minun).with_energy(vec![EnergyType::Lightning]),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        opponent_with_full_bench(),
    );

    assert_eq!(state.get_active(1).get_remaining_hp(), 150);
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        60,
        "Charmander should be untouched without Plusle"
    );
    assert_eq!(
        state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        70,
        "Bulbasaur should be untouched without Plusle"
    );
}

/// The buddy has to be on the *Bench* — a Plusle in the Active Spot cannot be there, but a
/// completely different Pokémon named something else must not count either.
#[test]
fn test_thundering_volcano_needs_electivire_on_the_bench() {
    let with_buddy = attack_with(
        PlayedCard::from_id(CardId::B2b013Magmortar).with_energy(vec![
            EnergyType::Fire,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ]),
        vec![PlayedCard::from_id(CardId::A2057Electivire)],
        opponent_with_full_bench(),
    );
    assert_eq!(
        with_buddy.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        40,
        "Charmander should take 20 bench damage when Electivire is benched"
    );

    let without_buddy = attack_with(
        PlayedCard::from_id(CardId::B2b013Magmortar).with_energy(vec![
            EnergyType::Fire,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ]),
        vec![PlayedCard::from_id(CardId::A2056Electabuzz)],
        opponent_with_full_bench(),
    );
    assert_eq!(
        without_buddy.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        60,
        "Electabuzz is not Electivire, so the bench should be untouched"
    );
}

// =================================================================================================
// Ampharos (B1 084 / B3b 096) "Zapping Bullet": 90 damage, and "1 of your opponent's Benched
// Pokémon is chosen at random. This attack also does 20 damage to it."
// =================================================================================================

fn zapping_bullet(seed: u64, opponent: Vec<PlayedCard>) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B1084Ampharos).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Lightning,
            EnergyType::Colorless,
        ])],
        opponent,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B1084Ampharos, 0),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn test_zapping_bullet_hits_exactly_one_random_benched_pokemon() {
    let mut hit_slot_one = 0;
    let mut hit_slot_two = 0;

    for seed in 0..40 {
        let state = zapping_bullet(
            seed,
            vec![
                PlayedCard::from_id(CardId::PB024MegaLatiosEx),
                PlayedCard::from_id(CardId::A1033Charmander),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
        );
        assert_eq!(state.get_active(1).get_remaining_hp(), 90);

        // Charmander (60 HP) in slot 1, Bulbasaur (70 HP) in slot 2.
        let slot_one_hp = state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp();
        let slot_two_hp = state.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp();
        match (slot_one_hp, slot_two_hp) {
            (40, 70) => hit_slot_one += 1,
            (60, 50) => hit_slot_two += 1,
            other => {
                panic!("seed {seed}: exactly one benched Pokémon should take 20, got {other:?}")
            }
        }
    }

    assert!(
        hit_slot_one > 0 && hit_slot_two > 0,
        "the choice is not random"
    );
}

/// Negative case: with an empty Bench there is nothing to choose, so only the Active takes damage.
#[test]
fn test_zapping_bullet_with_an_empty_bench_is_just_its_printed_damage() {
    let state = zapping_bullet(0, vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 90);
}

// =================================================================================================
// Forretress (B2b 046 / B2b 104) "Enormous Explosion": 100 damage, and "This Pokémon also does 100
// damage to itself and 50 damage to all Benched Pokémon (both yours and your opponent's)."
// =================================================================================================

#[test]
fn test_enormous_explosion_hits_both_benches_and_itself() {
    let state = attack_with(
        PlayedCard::from_id(CardId::B2b046Forretress).with_energy(vec![
            EnergyType::Metal,
            EnergyType::Metal,
            EnergyType::Metal,
        ]),
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
    );

    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        80,
        "the opponent's Active Pokémon takes the printed 100"
    );
    assert_eq!(
        state.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        100,
        "the opponent's Benched Snorlax takes 50"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        100,
        "your own Benched Snorlax takes 50 too"
    );
    assert!(
        state.in_play_pokemon[0][0].is_none()
            || state.in_play_pokemon[0][0].as_ref().unwrap().get_name() == "Snorlax",
        "Forretress (100 HP) should knock itself out with its own 100 damage"
    );
    assert_eq!(
        state.points[1], 1,
        "the opponent scores the point for Forretress knocking itself out"
    );
}

// =================================================================================================
// Mimikyu (A3 083 / P-A 066) "Shadow Hit": 60 damage, and "This attack also does 20 damage to 1 of
// your Pokémon."
// =================================================================================================

#[test]
fn test_shadow_hit_lets_you_pick_any_of_your_own_pokemon() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3083Mimikyu)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1211Snorlax),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A3083Mimikyu, 0),
        is_stack: false,
    });

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "the attacking player chooses the target");
    assert_eq!(
        choices.len(),
        2,
        "both the Attacking Pokémon and its Benched partner are legal targets"
    );
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::ApplyDamage { .. })));

    // Pick the Benched Snorlax (in_play_idx 1).
    let bench_choice = choices
        .iter()
        .find(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => targets[0].2 == 1,
            _ => false,
        })
        .expect("the Bench should be a legal target")
        .clone();
    game.apply_action(&bench_choice);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(1).get_remaining_hp(),
        120,
        "Mega Latios ex takes the printed 60"
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        130,
        "your Benched Snorlax takes the 20"
    );
    assert_eq!(
        state.get_active(0).get_remaining_hp(),
        70,
        "Mimikyu itself should be untouched when the Bench was chosen"
    );
}

#[test]
fn test_shadow_hit_can_target_the_attacking_pokemon_itself() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::PA066Mimikyu)
            .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::PA066Mimikyu, 0),
        is_stack: false,
    });

    let (_, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(choices.len(), 1, "only Mimikyu itself is in play");
    game.apply_action(&choices[0].clone());

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        50,
        "Mimikyu (70 HP) should take its own 20"
    );
}
