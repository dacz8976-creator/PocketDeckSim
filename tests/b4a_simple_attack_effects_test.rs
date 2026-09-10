use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board},
};

const SPONGE_HP: u32 = 250;

fn sponge() -> PlayedCard {
    PlayedCard::new(
        get_card_by_enum(CardId::PB024MegaLatiosEx),
        0,
        SPONGE_HP,
        vec![],
        false,
        vec![],
    )
}

fn attacker(id: CardId, energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(energy)
}

fn attack_damage(
    seed: u64,
    attacker_id: CardId,
    attacker: PlayedCard,
    attacker_bench: Vec<PlayedCard>,
    defender: PlayedCard,
    defender_bench: Vec<PlayedCard>,
    discard: Vec<Card>,
) -> (u32, deckgym::State) {
    let mut player_board = vec![attacker];
    player_board.extend(attacker_bench);
    let mut opponent_board = vec![defender];
    opponent_board.extend(defender_bench);
    let initial_hp = opponent_board[0].get_remaining_hp();
    let mut game = get_initialized_game_with_board(seed, 0, 3, player_board, opponent_board);
    let mut state = game.get_state_clone();
    state.discard_piles[0] = discard;
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    let remaining = state
        .in_play_pokemon[1][0]
        .as_ref()
        .map_or(0, PlayedCard::get_remaining_hp);
    (initial_hp - remaining, state)
}

#[test]
fn illumise_ire_fly_requires_volbeat_in_own_discard() {
    let illuminise = || {
        attacker(
            CardId::B4a002Illumise,
            vec![EnergyType::Grass, EnergyType::Colorless],
        )
    };
    let (base, _) = attack_damage(
        0,
        CardId::B4a002Illumise,
        illuminise(),
        vec![],
        sponge(),
        vec![],
        vec![],
    );
    let (boosted, _) = attack_damage(
        0,
        CardId::B4a002Illumise,
        illuminise(),
        vec![],
        sponge(),
        vec![],
        vec![get_card_by_enum(CardId::B4a001Volbeat)],
    );
    assert_eq!(base, 30);
    assert_eq!(boosted, 90);
}

#[test]
fn illumise_does_not_count_opponents_discard_or_a_different_pokemon() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![attacker(
            CardId::B4a002Illumise,
            vec![EnergyType::Grass, EnergyType::Colorless],
        )],
        vec![sponge()],
    );
    let mut state = game.get_state_clone();
    state.discard_piles[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.discard_piles[1] = vec![get_card_by_enum(CardId::B4a001Volbeat)];
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B4a002Illumise, 0),
        is_stack: false,
    });
    assert_eq!(
        SPONGE_HP - game.get_state_clone().get_active(1).get_remaining_hp(),
        30
    );
}

#[test]
fn magmar_counts_each_simultaneous_special_condition() {
    let magmar = || attacker(CardId::B4a006TeamRocketsMagmar, vec![EnergyType::Colorless]);
    let (none, _) = attack_damage(
        0,
        CardId::B4a006TeamRocketsMagmar,
        magmar(),
        vec![],
        sponge(),
        vec![],
        vec![],
    );
    let (three, _) = attack_damage(
        0,
        CardId::B4a006TeamRocketsMagmar,
        magmar(),
        vec![],
        sponge()
            .with_status_condition(StatusCondition::Poisoned)
            .with_status_condition(StatusCondition::Burned)
            .with_status_condition(StatusCondition::Confused),
        vec![],
        vec![],
    );
    assert_eq!(none, 10);
    assert_eq!(three, 160);
}

#[test]
fn houndoom_inflicts_poison_and_burn_after_damage() {
    let (damage, state) = attack_damage(
        0,
        CardId::B4a009TeamRocketsHoundoom,
        attacker(CardId::B4a009TeamRocketsHoundoom, vec![EnergyType::Fire]),
        vec![],
        sponge(),
        vec![],
        vec![],
    );
    assert_eq!(damage, 20);
    assert!(state.get_active(1).is_poisoned());
    assert!(state.get_active(1).is_burned());
}

#[test]
fn houndoom_status_rider_respects_attack_effect_immunity() {
    let protected = sponge().with_tool(get_card_by_enum(CardId::B4149ClearVeil));
    let (damage, state) = attack_damage(
        0,
        CardId::B4a009TeamRocketsHoundoom,
        attacker(CardId::B4a009TeamRocketsHoundoom, vec![EnergyType::Fire]),
        vec![],
        protected,
        vec![],
        vec![],
    );
    assert_eq!(damage, 20);
    assert!(!state.get_active(1).is_poisoned());
    assert!(!state.get_active(1).is_burned());
}

#[test]
fn lapras_requires_strictly_more_attached_energy() {
    let lapras = || {
        attacker(
            CardId::B4a013TeamRocketsLapras,
            vec![EnergyType::Water, EnergyType::Colorless],
        )
    };
    let (more, _) = attack_damage(
        0,
        CardId::B4a013TeamRocketsLapras,
        lapras(),
        vec![],
        sponge().with_energy(vec![EnergyType::Colorless]),
        vec![],
        vec![],
    );
    let (equal, _) = attack_damage(
        0,
        CardId::B4a013TeamRocketsLapras,
        lapras(),
        vec![],
        sponge().with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]),
        vec![],
        vec![],
    );
    assert_eq!(more, 80);
    assert_eq!(equal, 40);
}

#[test]
fn marowak_matches_team_rocket_as_a_name_substring() {
    let marowak = || {
        attacker(
            CardId::B4a036Marowak,
            vec![EnergyType::Fighting, EnergyType::Colorless],
        )
    };
    let (boosted, _) = attack_damage(
        0,
        CardId::B4a036Marowak,
        marowak(),
        vec![],
        PlayedCard::new(
            get_card_by_enum(CardId::B4a009TeamRocketsHoundoom),
            0,
            SPONGE_HP,
            vec![],
            false,
            vec![],
        ),
        vec![],
        vec![],
    );
    let (base, _) = attack_damage(
        0,
        CardId::B4a036Marowak,
        marowak(),
        vec![],
        sponge(),
        vec![],
        vec![],
    );
    assert_eq!(boosted, 120);
    assert_eq!(base, 50);
}

#[test]
fn sneasel_flips_once_per_own_pokemon_in_play() {
    let sneasel = || {
        attacker(
            CardId::B4a044TeamRocketsSneasel,
            vec![EnergyType::Darkness, EnergyType::Colorless],
        )
    };
    let mut solo_max = 0;
    let mut three_max = 0;
    for seed in 0..120 {
        let (solo, _) = attack_damage(
            seed,
            CardId::B4a044TeamRocketsSneasel,
            sneasel(),
            vec![],
            sponge(),
            vec![],
            vec![],
        );
        assert!(matches!(solo, 0 | 30));
        solo_max = solo_max.max(solo);

        let (three, _) = attack_damage(
            seed,
            CardId::B4a044TeamRocketsSneasel,
            sneasel(),
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            sponge(),
            vec![],
            vec![],
        );
        assert!(three % 30 == 0 && three <= 90);
        three_max = three_max.max(three);
    }
    assert_eq!(solo_max, 30);
    assert_eq!(three_max, 90);
}

#[test]
fn persian_counts_only_opponents_occupied_bench_slots() {
    let persian = || {
        attacker(
            CardId::B4a061TeamRocketsPersian,
            vec![EnergyType::Colorless, EnergyType::Colorless],
        )
    };
    let (empty, _) = attack_damage(
        0,
        CardId::B4a061TeamRocketsPersian,
        persian(),
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        sponge(),
        vec![],
        vec![],
    );
    let (two, _) = attack_damage(
        0,
        CardId::B4a061TeamRocketsPersian,
        persian(),
        vec![],
        sponge(),
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![],
    );
    assert_eq!(empty, 10);
    assert_eq!(two, 90);
}
