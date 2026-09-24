//! Generated-action regressions for continuous recovery when Power of Alchemy leaves play.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard, StatusCondition},
    players::{EndTurnPlayer, Player},
    Deck, Game, State,
};

const SEED: u64 = 318_018;

fn evolved(id: CardId, under: &[CardId], energy: Vec<EnergyType>) -> PlayedCard {
    let mut pokemon = PlayedCard::from_id(id).with_energy(energy);
    pokemon.cards_behind = under.iter().map(|id| get_card_by_enum(*id)).collect();
    pokemon
}

fn muk(energy: Vec<EnergyType>) -> PlayedCard {
    evolved(CardId::B2097AlolanMuk, &[CardId::B2096AlolanGrimer], energy)
}

fn game_from_state(state: State, offset: u64) -> Game<'static> {
    let players: Vec<Box<dyn Player>> = vec![
        Box::new(EndTurnPlayer { deck: state.decks[0].clone() }),
        Box::new(EndTurnPlayer { deck: state.decks[1].clone() }),
    ];
    Game::from_state(state, players, SEED + offset)
}

fn state_with_board(
    current_player: usize,
    player_0: Vec<PlayedCard>,
    player_1: Vec<PlayedCard>,
) -> State {
    let mut state = State::new(&Deck::default(), &Deck::default());
    state.current_player = current_player;
    state.turn_count = 9;
    state.hands = [vec![], vec![]];
    state.energy_zone[0].current = None;
    state.energy_zone[0].next = None;
    state.energy_zone[1].current = None;
    state.energy_zone[1].next = None;
    state.set_board(player_0, player_1);
    state
}

fn generated_action(
    game: &Game<'_>,
    actor: usize,
    label: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) -> Action {
    let (offered_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(offered_actor, actor, "{label} offered to wrong actor");
    let matches: Vec<_> = actions
        .into_iter()
        .filter(|candidate| predicate(&candidate.action))
        .collect();
    assert_eq!(matches.len(), 1, "expected one legal {label}: {matches:?}");
    matches.into_iter().next().unwrap()
}

fn apply_generated(
    game: &mut Game<'_>,
    actor: usize,
    label: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) {
    let action = generated_action(game, actor, label, predicate);
    game.apply_action(&action);
}

fn apply_attack(game: &mut Game<'_>, actor: usize, title: &str) {
    apply_generated(game, actor, title, |action| {
        matches!(action, SimpleAction::Attack(attack) if attack.title == title)
    });
}

fn poison_while_basic_protector_is_suppressed(state: &mut State, player: usize) {
    state.apply_status_condition(player, 0, StatusCondition::Poisoned);
    assert!(
        state.get_active(player).has_status(StatusCondition::Poisoned),
        "Power of Alchemy must suppress the Basic protection source before the transition"
    );
}

fn mewtwo_with_comfey(energy: Vec<EnergyType>) -> Vec<PlayedCard> {
    vec![
        PlayedCard::from_id(CardId::A1129MewtwoEx).with_energy(energy),
        PlayedCard::from_id(CardId::A3080Comfey),
    ]
}

#[test]
fn lethal_attack_removing_last_muk_restores_and_reconciles_flower_shield() {
    let mut state = state_with_board(
        0,
        mewtwo_with_comfey(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Water,
        ]),
        vec![muk(vec![]), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 0);
    let mut game = game_from_state(state, 0);

    apply_attack(&mut game, 0, "Psydrive");

    let after_ko = game.get_state_clone();
    assert!(after_ko.in_play_pokemon[1][0].is_none());
    assert_eq!(after_ko.points, [1, 0]);
    assert_eq!(
        after_ko
            .get_active(0)
            .attached_energy
            .iter()
            .filter(|energy| **energy == EnergyType::Psychic)
            .count(),
        1
    );
    assert!(
        !after_ko.get_active(0).has_status(StatusCondition::Poisoned),
        "Flower Shield must cure immediately after the last suppressor is removed"
    );
    let (_, choices) = after_ko.generate_possible_actions();
    assert_eq!(choices.len(), 1);
    assert!(matches!(
        choices[0].action,
        SimpleAction::Promote { player: 1, in_play_idx: 1 }
    ));
}

#[test]
fn removing_muk_does_not_cure_a_wrong_energy_recipient() {
    let machamp = evolved(
        CardId::A1146MachampEx,
        &[CardId::A1143Machop, CardId::A1144Machoke],
        vec![
            EnergyType::Fighting,
            EnergyType::Fighting,
            EnergyType::Fighting,
        ],
    );
    let mut state = state_with_board(
        0,
        vec![machamp, PlayedCard::from_id(CardId::A3080Comfey)],
        vec![muk(vec![]), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 0);
    let mut game = game_from_state(state, 1);

    apply_attack(&mut game, 0, "Mega Punch");

    let after_ko = game.get_state_clone();
    assert!(after_ko.in_play_pokemon[1][0].is_none());
    assert!(after_ko.get_active(0).has_status(StatusCondition::Poisoned));
}

#[test]
fn removing_last_muk_restores_ogerpons_any_energy_soothing_wind() {
    let machamp = evolved(
        CardId::A1146MachampEx,
        &[CardId::A1143Machop, CardId::A1144Machoke],
        vec![
            EnergyType::Fighting,
            EnergyType::Fighting,
            EnergyType::Fighting,
        ],
    );
    let mut state = state_with_board(
        0,
        vec![
            machamp,
            PlayedCard::from_id(CardId::B2017TealMaskOgerponEx),
        ],
        vec![muk(vec![]), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 0);
    let mut game = game_from_state(state, 11);

    apply_attack(&mut game, 0, "Mega Punch");

    let after_ko = game.get_state_clone();
    assert!(after_ko.in_play_pokemon[1][0].is_none());
    assert!(
        !after_ko.get_active(0).has_status(StatusCondition::Poisoned),
        "Ogerpon's untyped Soothing Wind must accept the remaining Fighting Energy"
    );
}

#[test]
fn knocking_out_one_muk_does_not_restore_abilities_while_a_second_remains() {
    let mut state = state_with_board(
        0,
        mewtwo_with_comfey(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Water,
        ]),
        vec![
            muk(vec![]),
            muk(vec![]),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 0);
    let mut game = game_from_state(state, 2);

    apply_attack(&mut game, 0, "Psydrive");

    let after_ko = game.get_state_clone();
    assert!(after_ko.in_play_pokemon[1][0].is_none());
    assert_eq!(after_ko.in_play_pokemon[1][1].as_ref().unwrap().get_id(), "B2 097");
    assert!(after_ko.get_active(0).has_status(StatusCondition::Poisoned));
    let mut fresh_status = after_ko;
    fresh_status.apply_status_condition(0, 0, StatusCondition::Burned);
    assert!(fresh_status.get_active(0).has_status(StatusCondition::Burned));
}

#[test]
fn temporal_leaves_devolving_last_active_muk_uses_the_same_restoration_boundary() {
    let mut state = state_with_board(
        0,
        vec![
            PlayedCard::from_id(CardId::A4a006Celebi).with_energy(vec![
                EnergyType::Grass,
                EnergyType::Grass,
                EnergyType::Psychic,
            ]),
            PlayedCard::from_id(CardId::A3080Comfey),
        ],
        vec![muk(vec![]), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 0);
    let mut game = game_from_state(state, 3);

    apply_attack(&mut game, 0, "Temporal Leaves");

    let after_devolution = game.get_state_clone();
    assert_eq!(after_devolution.get_active(1).get_id(), "B2 096");
    assert_eq!(after_devolution.get_active(1).get_remaining_hp(), 40);
    assert_eq!(after_devolution.points, [0, 0]);
    assert!(after_devolution.hands[1]
        .iter()
        .any(|card| card.get_name() == "Alolan Muk"));
    assert!(
        !after_devolution
            .get_active(0)
            .has_status(StatusCondition::Poisoned),
        "devolving the last Muk must restore and reconcile Flower Shield"
    );
}

#[test]
fn removing_the_protector_with_the_suppressor_does_not_create_recovery() {
    let lurantis = evolved(
        CardId::A3015Lurantis,
        &[CardId::A3014Fomantis],
        vec![EnergyType::Grass],
    );
    let mut state = state_with_board(
        0,
        vec![lurantis],
        vec![
            PlayedCard::from_id(CardId::A1129MewtwoEx)
                .with_energy(vec![EnergyType::Psychic]),
            muk(vec![]).with_remaining_hp(20),
            PlayedCard::from_id(CardId::A3080Comfey).with_remaining_hp(20),
        ],
    );
    poison_while_basic_protector_is_suppressed(&mut state, 1);
    let mut game = game_from_state(state, 4);

    apply_attack(&mut game, 0, "Petal Blizzard");

    let settled = game.get_state_clone();
    assert_eq!(settled.points, [2, 0]);
    assert!(settled.in_play_pokemon[1][1].is_none());
    assert!(settled.in_play_pokemon[1][2].is_none());
    assert_eq!(settled.get_active(1).get_remaining_hp(), 130);
    assert!(
        settled.get_active(1).has_status(StatusCondition::Poisoned),
        "a departed Comfey cannot cure after the same knockout wave removes Muk"
    );
    let mut fresh_status = settled;
    fresh_status.apply_status_condition(1, 0, StatusCondition::Burned);
    assert!(fresh_status.get_active(1).has_status(StatusCondition::Burned));
}
