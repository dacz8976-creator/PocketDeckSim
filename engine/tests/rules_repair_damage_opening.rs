use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    test_support::{attack_action, get_initialized_game, get_test_game_with_board},
    Deck,
};
use rand::{rngs::StdRng, SeedableRng};

fn two_basic_deck() -> Deck {
    Deck::from_string("Pokémon: 2\n2 Bulbasaur A1 001\n\nTrainer: 18\n18 Potion P-A 001\n").unwrap()
}

fn trainer_from_id(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(card) => card,
        _ => panic!("expected Trainer card"),
    }
}

#[test]
fn initial_shuffle_preserves_a_random_five_that_already_has_a_basic() {
    let source = two_basic_deck();
    let mut checked = 0;

    for seed in 0..512 {
        let mut ordinary = source.clone();
        ordinary.shuffle(false, &mut StdRng::seed_from_u64(seed));
        if ordinary.cards[..5].iter().any(Card::is_basic) {
            let mut initial = source.clone();
            initial.shuffle(true, &mut StdRng::seed_from_u64(seed));
            assert_eq!(initial.cards, ordinary.cards, "seed {seed}");
            checked += 1;
        }
    }

    assert!(checked > 100, "expected many already-valid random hands");
}

#[test]
fn initial_shuffle_repairs_only_a_zero_basic_hand() {
    let source = two_basic_deck();
    let seed = (0..512)
        .find(|seed| {
            let mut ordinary = source.clone();
            ordinary.shuffle(false, &mut StdRng::seed_from_u64(*seed));
            ordinary.cards[..5].iter().all(|card| !card.is_basic())
        })
        .expect("a zero-Basic random hand");

    let mut repaired = source;
    repaired.shuffle(true, &mut StdRng::seed_from_u64(seed));
    assert_eq!(repaired.cards.len(), 20);
    assert_eq!(
        repaired.cards.iter().filter(|card| card.is_basic()).count(),
        2
    );
    assert_eq!(
        repaired.cards[..5]
            .iter()
            .filter(|card| card.is_basic())
            .count(),
        1
    );
}

#[test]
fn heavy_helmet_reduces_only_opponent_attack_damage() {
    let helmet_holder = PlayedCard::from_id(CardId::A1055Blastoise)
        .with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), helmet_holder],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(30, 0, 1)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        120,
        "Heavy Helmet must not reduce its owner's attack damage"
    );

    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (1, 0),
            targets: vec![(30, 0, 1)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        110,
        "Heavy Helmet should reduce an opponent's attack by 20"
    );
}

#[test]
fn heavy_helmet_does_not_reduce_poison_damage() {
    let poisoned = PlayedCard::from_id(CardId::A1055Blastoise)
        .with_status_condition(StatusCondition::Poisoned)
        .with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));
    let mut game = get_test_game_with_board(
        vec![poisoned],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 140);
}

#[test]
fn clemonts_backpack_boosts_bench_damage_but_giovanni_does_not() {
    fn bench_damage(trainer_id: CardId) -> u32 {
        let heliolisk =
            PlayedCard::from_id(CardId::B4061Heliolisk).with_energy(vec![EnergyType::Lightning]);
        let mut game = get_test_game_with_board(
            vec![heliolisk],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
        );
        let trainer = trainer_from_id(trainer_id);
        let mut state = game.get_state_clone();
        state.hands[0].push(Card::Trainer(trainer.clone()));
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: trainer,
            },
            is_stack: false,
        });
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B4061Heliolisk, 0),
            is_stack: false,
        });
        70 - game.get_state_clone().in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp()
    }

    assert_eq!(bench_damage(CardId::B1a066ClemontsBackpack), 30);
    assert_eq!(bench_damage(CardId::A1223Giovanni), 10);
}

#[test]
fn weakness_precedes_reductions_and_damage_clamps_after_defender_stage() {
    fn damage_taken(base_damage: u32, bounded_field: bool) -> u32 {
        let mut game = get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![PlayedCard::from_id(CardId::A1038Ninetales)],
            vec![PlayedCard::from_id(CardId::A4124SkarmoryEx)
                .with_tool(get_card_by_enum(CardId::B2148MetalCoreBarrier))],
        );
        if bounded_field {
            state.active_stadium = Some(get_card_by_enum(CardId::B3155BoundedField));
            state.active_stadium_owner = Some(0);
        }
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::ApplyDamage {
                attacking_ref: (0, 0),
                targets: vec![(base_damage, 1, 0)],
                is_from_active_attack: true,
            },
            is_stack: false,
        });
        140 - game.get_state_clone().get_active(1).get_remaining_hp()
    }

    assert_eq!(damage_taken(60, true), 70);
    assert_eq!(damage_taken(10, false), 0);
    assert_eq!(damage_taken(0, true), 0);
}

#[test]
fn intimidating_fang_reduces_attacker_damage_before_double_weakness() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1143Machop)],
        vec![PlayedCard::from_id(CardId::A3a015Luxray)],
    );
    state.active_stadium = Some(get_card_by_enum(CardId::B3155BoundedField));
    state.active_stadium_owner = Some(0);
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(60, 1, 0)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        50,
        "Intimidating Fang should reduce 60 to 40 before Bounded Field doubles it to 80"
    );
}

#[test]
fn protective_poncho_does_not_block_owners_attack() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho)),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(20, 0, 1)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    assert_eq!(
        game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        50
    );
}

fn lum_bad_dreams_result(lum_owner_ends_turn: bool) -> (u32, bool) {
    let sleeping_lum_holder = PlayedCard::from_id(CardId::A1001Bulbasaur)
        .with_status_condition(StatusCondition::Asleep)
        .with_tool(get_card_by_enum(CardId::A2149LumBerry));
    let darkrai = PlayedCard::from_id(CardId::B2b040Darkrai);
    let (player, opponent) = if lum_owner_ends_turn {
        (sleeping_lum_holder, darkrai)
    } else {
        (darkrai, sleeping_lum_holder)
    };
    let mut game = get_test_game_with_board(vec![player], vec![opponent]);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    let state = game.get_state_clone();
    let holder_player = if lum_owner_ends_turn { 0 } else { 1 };
    let holder = state.get_active(holder_player);
    (holder.get_remaining_hp(), holder.is_asleep())
}

#[test]
fn lum_berry_and_bad_dreams_follow_turn_owner_order() {
    assert_eq!(lum_bad_dreams_result(false), (50, false));
    assert_eq!(lum_bad_dreams_result(true), (70, false));
}
