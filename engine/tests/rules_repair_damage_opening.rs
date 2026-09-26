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

/// rules/09 (confirmed in-game 2026-09-25, `heavyhelmet_test.MP4`): Heavy Helmet reads the holder's current
/// Retreat Cost where it sits, not the printed one. Returns the damage a 40-damage opponent attack does to
/// player 0's Pokémon at `target_idx`.
fn helmet_hit(player0: Vec<PlayedCard>, player1: Vec<PlayedCard>, plaza: bool, target_idx: usize) -> u32 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(player0, player1);
    if plaza {
        state.active_stadium = Some(get_card_by_enum(CardId::B2155PeculiarPlaza));
    }
    game.set_state(state);
    let before = game.get_state_clone().in_play_pokemon[0][target_idx].as_ref().unwrap().get_remaining_hp();
    game.apply_action(&Action {
        actor: 1,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (1, 0),
            targets: vec![(40, 0, target_idx)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    before - game.get_state_clone().in_play_pokemon[0][target_idx].as_ref().unwrap().get_remaining_hp()
}

/// rules/09 (laptop's Altaria card check, Sept 26): Disguise prevents the first attack that damages Mimikyu ex. Sing
/// does no damage, so it leaves Disguise in place for the next hit.
#[test]
fn sing_does_not_use_up_disguise() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1196Swablu).with_energy(vec![EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::B2073MimikyuEx)],
    );
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B1196Swablu, 0), is_stack: false });
    let state = game.get_state_clone();
    assert!(state.get_active(1).is_asleep(), "Sing still puts it to sleep");
    assert!(!state.get_active(1).prevent_first_attack_damage_used, "no damage was done, so Disguise is unused");
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage { attacking_ref: (0, 0), targets: vec![(30, 1, 0)], is_from_active_attack: true },
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 120, "the first damaging hit is the one Disguise prevents");
    assert!(state.get_active(1).prevent_first_attack_damage_used);
}

/// rules/09 (laptop recordings check, 2026-09-25): "Discard all Energy from this Pokémon" puts the Energy in the
/// discard pile, where Volkner, Flame Patch, Dragon's Blessing and the rest read it.
#[test]
fn hyper_ray_puts_the_discarded_energy_in_the_discard_pile() {
    let energy = vec![EnergyType::Darkness, EnergyType::Darkness, EnergyType::Darkness, EnergyType::Colorless];
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1157Hydreigon).with_energy(energy.clone())],
        vec![PlayedCard::from_id(CardId::A1055Blastoise)],
    );
    let mut state = game.get_state_clone();
    state.discard_energies[0].clear();
    game.set_state(state);
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B1157Hydreigon, 0), is_stack: false });
    let state = game.get_state_clone();
    assert!(state.get_active(0).attached_energy.is_empty());
    assert_eq!(state.get_active(1).get_remaining_hp(), 20, "Hyper Ray still does 130");
    let mut discarded = state.discard_energies[0].clone();
    discarded.sort_by_key(|e| format!("{e:?}"));
    let mut expected = energy;
    expected.sort_by_key(|e| format!("{e:?}"));
    assert_eq!(discarded, expected);
}

#[test]
fn heavy_helmet_reads_the_current_retreat_cost_where_the_holder_sits() {
    let helmet = |id| PlayedCard::from_id(id).with_tool(get_card_by_enum(CardId::B1219HeavyHelmet));
    let bulbasaur = || PlayedCard::from_id(CardId::A1001Bulbasaur);
    // Golett: Psychic, printed Retreat Cost 3. Peculiar Plaza makes it 1, so the Helmet cuts nothing (the recording).
    assert_eq!(helmet_hit(vec![helmet(CardId::A1135Golett)], vec![bulbasaur()], false, 0), 20);
    assert_eq!(helmet_hit(vec![helmet(CardId::A1135Golett)], vec![bulbasaur()], true, 0), 40);
    // Ivysaur: printed 2. The opponent's Ariados (Trap Territory) makes the Active's cost 3, so the Helmet cuts 20;
    // on the Bench Trap Territory doesn't reach it, so it stays 2 and the Helmet cuts nothing.
    let ariados = || PlayedCard::from_id(CardId::B1a006Ariados);
    assert_eq!(helmet_hit(vec![helmet(CardId::A1002Ivysaur)], vec![bulbasaur()], false, 0), 40);
    assert_eq!(helmet_hit(vec![helmet(CardId::A1002Ivysaur)], vec![bulbasaur(), ariados()], false, 0), 20);
    assert_eq!(
        helmet_hit(vec![bulbasaur(), helmet(CardId::A1002Ivysaur)], vec![bulbasaur(), ariados()], false, 1),
        40
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

/// rules/09 (laptop's Raticate/Manectric card check, Sept 26): the hand holds 10 cards. Clemont played from a 10-card
/// hand leaves room for one of its two random cards; the other stays in the deck, as a draw past 10 does.
#[test]
fn clemont_from_a_ten_card_hand_stops_at_ten() {
    let clemont = trainer_from_id(CardId::B1a068Clemont);
    let targets = [CardId::A1098Magneton, CardId::B4061Heliolisk];
    for seed in 20_000_000_010..20_000_000_030u64 {
        let mut game = get_initialized_game(seed);
        let mut state = game.get_state_clone();
        state.set_board(vec![PlayedCard::from_id(CardId::A1001Bulbasaur)], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
        state.current_player = 0;
        state.turn_count = 3;
        state.hands[0] = vec![Card::Trainer(clemont.clone())];
        state.hands[0].extend((0..9).map(|_| get_card_by_enum(CardId::PA001Potion)));
        state.decks[0].cards = targets.iter().map(|id| get_card_by_enum(*id)).collect();
        state.decks[0].cards.extend((0..4).map(|_| get_card_by_enum(CardId::PA001Potion)));
        game.set_state(state);
        game.apply_action(&Action { actor: 0, action: SimpleAction::Play { trainer_card: clemont.clone() }, is_stack: false });
        let state = game.get_state_clone();
        assert_eq!(state.hands[0].len(), 10);
        let in_hand = |id: CardId| state.hands[0].contains(&get_card_by_enum(id));
        assert!(in_hand(targets[0]) != in_hand(targets[1]), "exactly one of the two fits");
        assert_eq!(state.decks[0].cards.len(), 5, "the other stays in the deck");
    }
}

/// rules/09 (laptop's Raticate/Manectric card check, Sept 26): the Backpack's +20 is for attacks used by Magneton or
/// Heliolisk against the opponent's Pokémon. A Poisoned Heliolisk takes the plain 10 at Checkup the turn it is played.
#[test]
fn clemonts_backpack_does_not_add_to_checkup_damage_on_its_own_heliolisk() {
    let heliolisk = PlayedCard::from_id(CardId::B4061Heliolisk).with_status_condition(StatusCondition::Poisoned);
    let mut game = get_test_game_with_board(vec![heliolisk], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let trainer = trainer_from_id(CardId::B1a066ClemontsBackpack);
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(trainer.clone()));
    game.set_state(state);
    let before = game.get_state_clone().get_active(0).get_remaining_hp();
    game.apply_action(&Action { actor: 0, action: SimpleAction::Play { trainer_card: trainer }, is_stack: false });
    game.apply_action(&Action { actor: 0, action: SimpleAction::EndTurn, is_stack: false });
    assert_eq!(before - game.get_state_clone().get_active(0).get_remaining_hp(), 10);
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
