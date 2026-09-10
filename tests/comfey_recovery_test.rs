//! Generated-action regressions for continuous Soothing Wind / Flower Shield recovery.
//!
//! Each afflicted fixture carries one legal Special Condition at a time. Poison additionally uses
//! a serialized 30-damage Checkup override to prove that recovery clears its severity metadata.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    players::{EndTurnPlayer, Player},
    Deck, Game, State,
};

const SEED: u64 = 317_017;

fn empty_state(current_player: usize) -> State {
    let own = Deck::default();
    let opponent = Deck::default();
    let mut state = State::new(&own, &opponent);
    state.current_player = current_player;
    state.turn_count = 5;
    state.hands = [vec![], vec![]];
    state.energy_zone[0].current = None;
    state.energy_zone[0].next = None;
    state.energy_zone[1].current = None;
    state.energy_zone[1].next = None;
    state
}

fn game_from_state(state: State, offset: u64) -> Game<'static> {
    let players: Vec<Box<dyn Player>> = vec![
        Box::new(EndTurnPlayer {
            deck: state.decks[0].clone(),
        }),
        Box::new(EndTurnPlayer {
            deck: state.decks[1].clone(),
        }),
    ];
    Game::from_state(state, players, SEED + offset)
}

fn generated_action(
    game: &Game<'_>,
    actor: usize,
    description: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) -> Action {
    let (offered_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(offered_actor, actor, "{description} offered to wrong actor");
    let matches: Vec<_> = actions
        .into_iter()
        .filter(|candidate| predicate(&candidate.action))
        .collect();
    assert_eq!(
        matches.len(),
        1,
        "expected exactly one legal {description}, found {matches:?}"
    );
    matches.into_iter().next().unwrap()
}

fn apply_generated(
    game: &mut Game<'_>,
    actor: usize,
    description: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) {
    let action = generated_action(game, actor, description, predicate);
    game.apply_action(&action);
}

fn afflicted(id: CardId, condition: StatusCondition, poison_damage: Option<u32>) -> PlayedCard {
    let card = PlayedCard::from_id(id).with_status_condition(condition);
    if let Some(amount) = poison_damage {
        assert_eq!(condition, StatusCondition::Poisoned);
        let mut encoded = serde_json::to_value(card).unwrap();
        encoded["poison_checkup_damage"] = serde_json::json!(amount);
        let card: PlayedCard = serde_json::from_value(encoded).unwrap();
        assert_eq!(
            serde_json::to_value(&card).unwrap().get("poison_checkup_damage"),
            Some(&serde_json::json!(amount))
        );
        card
    } else {
        card
    }
}

fn assert_cured(state: &State, player: usize, slot: usize) {
    let pokemon = state.in_play_pokemon[player][slot]
        .as_ref()
        .expect("status target must remain in play");
    for condition in [
        StatusCondition::Poisoned,
        StatusCondition::Paralyzed,
        StatusCondition::Asleep,
        StatusCondition::Burned,
        StatusCondition::Confused,
    ] {
        assert!(
            !pokemon.has_status(condition),
            "{condition:?} should have been cured"
        );
    }
    let encoded = serde_json::to_value(pokemon).unwrap();
    assert_eq!(
        encoded.get("poison_checkup_damage"),
        Some(&serde_json::Value::Null),
        "recovery must clear a modified Poison Checkup amount"
    );
}

fn attach_from_zone(game: &mut Game<'_>, actor: usize, energy: EnergyType, slot: usize) {
    apply_generated(game, actor, "turn Energy attachment", |action| {
        matches!(action, SimpleAction::Attach { attachments, is_turn_energy: true }
            if attachments == &vec![(1, energy, slot)])
    });
}

#[test]
fn psychic_turn_attachment_cures_each_special_condition_and_modified_poison() {
    let cases = [
        (StatusCondition::Poisoned, Some(30)),
        (StatusCondition::Paralyzed, None),
        (StatusCondition::Asleep, None),
        (StatusCondition::Burned, None),
        (StatusCondition::Confused, None),
    ];
    for (case, (condition, poison_damage)) in cases.into_iter().enumerate() {
        let mut state = empty_state(0);
        state.set_board(
            vec![
                afflicted(CardId::A1001Bulbasaur, condition, poison_damage),
                PlayedCard::from_id(CardId::A3080Comfey),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        state.energy_zone[0].current = Some(EnergyType::Psychic);
        let mut game = game_from_state(state, case as u64);

        attach_from_zone(&mut game, 0, EnergyType::Psychic, 0);

        let settled = game.get_state_clone();
        assert_eq!(
            settled.get_active(0).attached_energy,
            vec![EnergyType::Psychic]
        );
        assert_cured(&settled, 0, 0);
    }
}

#[test]
fn dawn_scalar_move_cures_newly_matching_active() {
    let mut state = empty_state(0);
    state.set_board(
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Burned, None),
            PlayedCard::from_id(CardId::A1005Caterpie)
                .with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::A2154Dawn)];
    let mut game = game_from_state(state, 10);

    apply_generated(&mut game, 0, "Dawn", |action| {
        matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Dawn")
    });
    apply_generated(&mut game, 0, "Dawn Psychic move", |action| {
        matches!(action, SimpleAction::MoveEnergy {
            from_in_play_idx: 1,
            to_in_play_idx: 0,
            energy_type: EnergyType::Psychic,
            amount: 1,
        })
    });

    let settled = game.get_state_clone();
    assert_eq!(
        settled.get_active(0).attached_energy,
        vec![EnergyType::Psychic]
    );
    assert!(
        settled.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .attached_energy
            .is_empty(),
        "Dawn must remove the moved Energy from its source"
    );
    assert_cured(&settled, 0, 0);
}

#[test]
fn mixed_energy_move_cures_newly_matching_bench_target() {
    // Special Conditions normally occur only in the Active Spot and are cleared on switching.
    // The pre-afflicted Bench target is therefore a deliberately synthetic handler-state control;
    // the Feathery Cyclone and MoveEnergies actions themselves are generated legally.
    let mut state = empty_state(0);
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A4063Swanna)
                .with_energy(vec![EnergyType::Water, EnergyType::Psychic]),
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Paralyzed, None),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    let mut game = game_from_state(state, 11);

    apply_generated(&mut game, 0, "Feathery Cyclone", |action| {
        matches!(action, SimpleAction::Attack(attack) if attack.title == "Feathery Cyclone")
    });
    apply_generated(&mut game, 0, "mixed Energy move to afflicted Bench", |action| {
        matches!(action, SimpleAction::MoveEnergies {
            from_in_play_idx: 0,
            to_in_play_idx: 1,
            energies,
        } if energies.len() == 2
            && energies.contains(&EnergyType::Water)
            && energies.contains(&EnergyType::Psychic))
    });

    let settled = game.get_state_clone();
    assert!(
        settled.get_active(0).attached_energy.is_empty(),
        "Feathery Cyclone must remove the complete mixed set from Swanna"
    );
    let target = settled.in_play_pokemon[0][1].as_ref().unwrap();
    let mut received = target.attached_energy.clone();
    received.sort();
    let mut expected = vec![EnergyType::Water, EnergyType::Psychic];
    expected.sort();
    assert_eq!(received, expected, "the exact mixed Energy set must move");
    assert_cured(&settled, 0, 1);
}

#[test]
fn psychic_supporter_cross_player_move_uses_recipients_flower_shield() {
    let mut state = empty_state(0);
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1117Alakazam)],
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Confused, None),
            PlayedCard::from_id(CardId::A1005Caterpie)
                .with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B4150Psychic)];
    let mut game = game_from_state(state, 12);

    apply_generated(&mut game, 0, "Psychic Supporter", |action| {
        matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Psychic")
    });
    apply_generated(&mut game, 0, "opponent Energy theft", |action| {
        matches!(action, SimpleAction::MoveRandomOpponentEnergyToActive {
            from_in_play_idx: 1
        })
    });

    let settled = game.get_state_clone();
    assert_eq!(
        settled.get_active(1).attached_energy,
        vec![EnergyType::Psychic]
    );
    assert!(
        settled.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .attached_energy
            .is_empty(),
        "Psychic must remove the stolen Energy from the selected Bench source"
    );
    assert_cured(&settled, 1, 0);
}

#[test]
fn energy_plunder_direct_transfer_triggers_any_energy_soothing_wind() {
    let mut state = empty_state(0);
    state.set_board(
        vec![
            afflicted(CardId::A4119Tyranitar, StatusCondition::Burned, None),
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Grass]),
            PlayedCard::from_id(CardId::B2017TealMaskOgerponEx),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut game = game_from_state(state, 13);

    apply_generated(&mut game, 0, "Energy Plunder", |action| {
        matches!(action, SimpleAction::UseAbility { in_play_idx: 0 })
    });

    let settled = game.get_state_clone();
    assert_eq!(
        settled.get_active(0).attached_energy,
        vec![EnergyType::Darkness],
        "Energy Plunder must move only Darkness Energy to Tyranitar"
    );
    assert_eq!(
        settled.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .attached_energy,
        vec![EnergyType::Grass],
        "the source must retain its non-Darkness Energy"
    );
    assert_cured(&settled, 0, 0);
}

#[test]
fn juggler_gather_cures_active_and_conserves_every_bench_energy() {
    let mut state = empty_state(0);
    state.set_board(
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Burned, None),
            PlayedCard::from_id(CardId::A1005Caterpie)
                .with_energy(vec![
                    EnergyType::Psychic,
                    EnergyType::Grass,
                    EnergyType::Fire,
                ]),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B2151Juggler)];
    let mut game = game_from_state(state, 14);

    apply_generated(&mut game, 0, "Juggler", |action| {
        matches!(action, SimpleAction::Play { trainer_card } if trainer_card.name == "Juggler")
    });

    let settled = game.get_state_clone();
    assert_eq!(
        settled.get_active(0).attached_energy,
        vec![
            EnergyType::Psychic,
            EnergyType::Grass,
            EnergyType::Fire,
        ],
        "Juggler must gather the exact ordered Energy set"
    );
    for slot in [1, 2] {
        assert!(
            settled.in_play_pokemon[0][slot]
                .as_ref()
                .unwrap()
                .attached_energy
                .is_empty(),
            "Juggler must empty every Bench source"
        );
    }
    assert_cured(&settled, 0, 0);
}

#[test]
fn typed_flower_shield_respects_wrong_energy_side_and_suppression() {
    // Wrong Energy on the Comfey owner's side.
    let mut wrong = empty_state(0);
    wrong.set_board(
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Poisoned, None),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    wrong.energy_zone[0].current = Some(EnergyType::Grass);
    let mut wrong_game = game_from_state(wrong, 20);
    attach_from_zone(&mut wrong_game, 0, EnergyType::Grass, 0);
    assert!(wrong_game.get_state_clone().get_active(0).is_poisoned());

    // Psychic Energy on the other side cannot use this side's Comfey.
    let mut other_side = empty_state(1);
    other_side.set_board(
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![afflicted(
            CardId::A1001Bulbasaur,
            StatusCondition::Poisoned,
            None,
        )],
    );
    other_side.energy_zone[1].current = Some(EnergyType::Psychic);
    let mut other_game = game_from_state(other_side, 21);
    attach_from_zone(&mut other_game, 1, EnergyType::Psychic, 0);
    assert!(other_game.get_state_clone().get_active(1).is_poisoned());

    // Power of Alchemy suppresses the Basic Comfey before Energy arrives.
    let mut suppressed = empty_state(0);
    suppressed.set_board(
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Poisoned, None),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![PlayedCard::from_id(CardId::B2097AlolanMuk)],
    );
    suppressed.energy_zone[0].current = Some(EnergyType::Psychic);
    let mut suppressed_game = game_from_state(suppressed, 22);
    attach_from_zone(&mut suppressed_game, 0, EnergyType::Psychic, 0);
    assert!(
        suppressed_game
            .get_state_clone()
            .get_active(0)
            .is_poisoned(),
        "suppressed Flower Shield must not cure on attachment"
    );
}

#[test]
fn ogerpon_soothing_wind_cures_after_any_energy_type_arrives() {
    let mut state = empty_state(0);
    state.set_board(
        vec![
            afflicted(CardId::A1001Bulbasaur, StatusCondition::Asleep, None),
            PlayedCard::from_id(CardId::B2017TealMaskOgerponEx),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.energy_zone[0].current = Some(EnergyType::Fire);
    let mut game = game_from_state(state, 30);

    attach_from_zone(&mut game, 0, EnergyType::Fire, 0);

    let settled = game.get_state_clone();
    assert_eq!(settled.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_cured(&settled, 0, 0);
}
