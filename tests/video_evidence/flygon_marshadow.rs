//! Integrated regressions for the observed Flygon ex -> Marshadow sequence.
//!
//! This is a constructed mechanics fixture, not a full match replay or a strategy label. The
//! positive case earns Revenge's history through a real Dragon Pulse knockout and carries it
//! through the offered promotion, EndTurn/Pokemon Checkup, turn handoff, turn-Energy attachment,
//! and Revenge. It never writes the KO-history flag directly.
//!
//! Source recording: `20260907_222326000_iOS.MP4`, SHA-256
//! `48ab3d405f4e5c8c243778e49de93aa1779d49c26f075b23a6c2cca5579b499b`.
//! Published review: `Boss Folder/video-mechanics-flygon-sableye-2026-09-07/flygon-video/`
//! `{EVIDENCE.md,SOURCE_BINDINGS.md}`.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

const SEED: u64 = 222_326;

fn unique_action(
    game: &Game<'static>,
    description: &str,
    predicate: impl Fn(&Action) -> bool,
) -> Action {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    let matches: Vec<Action> = actions
        .into_iter()
        .filter(|candidate| predicate(candidate))
        .collect();
    assert_eq!(
        matches.len(),
        1,
        "expected one legal {description} for actor {actor}, got {matches:?}"
    );
    matches.into_iter().next().unwrap()
}

fn legal_attack(game: &Game<'static>, actor: usize, card: CardId, attack_index: usize) -> Action {
    let expected = attack_action(card, attack_index);
    let selected = unique_action(game, "attack", |candidate| candidate.action == expected);
    assert_eq!(selected.actor, actor, "attack offered to the wrong actor");
    assert!(!selected.is_stack, "ordinary attack should not be a stack choice");
    selected
}

fn legal_end_turn(game: &Game<'static>, actor: usize) -> Action {
    let selected = unique_action(game, "EndTurn", |candidate| {
        matches!(&candidate.action, SimpleAction::EndTurn)
    });
    assert_eq!(selected.actor, actor, "EndTurn offered to the wrong actor");
    selected
}

fn settle_single_forced_draw(game: &mut Game<'static>, incoming_actor: usize) {
    // The reduced fixtures intentionally admit exactly one automatic public continuation. Check
    // its identity before allowing Game to select it, so no unexplained multi-action stack can be
    // hidden by play_until_stable.
    let pending = game.get_state_clone();
    assert_eq!(pending.move_generation_stack.len(), 1);
    let (actor, choices) = pending.move_generation_stack.last().unwrap();
    assert_eq!(*actor, incoming_actor);
    assert_eq!(
        choices.as_slice(),
        [SimpleAction::DrawCard { amount: 1 }],
        "the only automatic handoff choice must be DrawCard(1)"
    );
    game.play_until_stable();
    assert!(
        game.get_state_clone().move_generation_stack.is_empty(),
        "constructed handoff should settle all forced public choices"
    );
}

fn finish_public_turn_handoff(game: &mut Game<'static>, outgoing_actor: usize) {
    let end_turn = legal_end_turn(game, outgoing_actor);
    game.apply_action(&end_turn);
    let incoming_actor = 1 - outgoing_actor;
    assert_eq!(game.get_state_clone().current_player, incoming_actor);
    settle_single_forced_draw(game, incoming_actor);
}

#[test]
fn observed_composite_chain() {
    // Central cards, HP, attached Energy, and score reproduce the public video state. The two
    // noncentral opponent Bench Pokemon use the readable standard prints from that board. Decks,
    // hands, and their ordering come from the test helper and are synthetic because the recording
    // does not reveal those private zones. Rainbow Cave is irrelevant to this chain and is
    // omitted. The video shows a mechanically
    // standard 80-HP/Razor Wing Dartrix surviving on the Bench; A3 011 supplies that exact card
    // behavior, while the physical reprint identity is not needed by the test.
    let recorder_board = vec![
        PlayedCard::from_id(CardId::B3126FlygonEx)
            .with_remaining_hp(100)
            .with_energy(vec![
                EnergyType::Grass,
                EnergyType::Grass,
                EnergyType::Fighting,
            ]),
        PlayedCard::from_id(CardId::A3011Dartrix).with_remaining_hp(80),
    ];
    let opponent_board = vec![
        PlayedCard::from_id(CardId::A1a046AerodactylEx)
            .with_remaining_hp(130)
            .with_energy(vec![EnergyType::Fighting, EnergyType::Fighting]),
        PlayedCard::from_id(CardId::A1155Hitmonchan).with_remaining_hp(50),
        PlayedCard::from_id(CardId::A1153MarowakEx).with_remaining_hp(130),
        PlayedCard::from_id(CardId::A1a047Marshadow)
            .with_remaining_hp(70)
            .with_energy(vec![EnergyType::Fighting]),
    ];
    let mut game = get_initialized_game_with_board(
        SEED,
        0,
        8,
        recorder_board,
        opponent_board,
    );
    let mut state = game.get_state_clone();
    state.points = [0, 1];
    state.active_stadium = None;
    state.active_stadium_owner = None;
    state.energy_zone[0].current = None;
    state.energy_zone[1].current = None;
    // Declared public turn-Energy scaffolding: the video shows Fighting become available and get
    // attached, but does not reveal the private deck construction used to generate it.
    state.energy_zone[1].next = Some(EnergyType::Fighting);
    game.set_state(state);

    let before = game.get_state_clone();
    let recorder_deck_before = before.decks[0].cards.len();
    let recorder_discard_before = before.discard_piles[0].len();
    let opponent_discard_before = before.discard_piles[1].len();
    assert!(
        recorder_deck_before > 0,
        "synthetic Dragon Pulse deck must contain a card to discard"
    );
    assert_eq!(before.points, [0, 1]);
    assert_eq!(before.get_active(0).get_remaining_hp(), 100);
    assert_eq!(before.get_active(1).get_remaining_hp(), 130);
    assert!(!before.get_knocked_out_by_opponent_attack_last_turn());

    let dragon_pulse = legal_attack(&game, 0, CardId::B3126FlygonEx, 0);
    game.apply_action(&dragon_pulse);

    let after_dragon_pulse = game.get_state_clone();
    assert_eq!(after_dragon_pulse.points, [2, 1]);
    assert!(after_dragon_pulse.in_play_pokemon[1][0].is_none());
    assert_eq!(
        after_dragon_pulse.decks[0].cards.len(),
        recorder_deck_before - 1,
        "Dragon Pulse must discard exactly one card from the user's synthetic deck"
    );
    assert_eq!(
        after_dragon_pulse.discard_piles[0].len(),
        recorder_discard_before + 1
    );
    assert_eq!(
        after_dragon_pulse.discard_piles[1].len(),
        opponent_discard_before + 1,
        "Aerodactyl ex must enter the opponent discard"
    );

    let (promotion_actor, promotion_set) = after_dragon_pulse.generate_possible_actions();
    assert_eq!(promotion_actor, 1);
    let mut offered_slots: Vec<usize> = promotion_set
        .iter()
        .filter_map(|candidate| match &candidate.action {
            SimpleAction::Promote { player: 1, in_play_idx } => Some(*in_play_idx),
            _ => None,
        })
        .collect();
    offered_slots.sort_unstable();
    assert_eq!(
        offered_slots,
        vec![1, 2, 3],
        "the forced promotion must offer the full surviving Bench"
    );
    let promote_marshadow = unique_action(&game, "Marshadow promotion", |candidate| {
        matches!(
            &candidate.action,
            SimpleAction::Promote {
                player: 1,
                in_play_idx: 3
            }
        )
    });
    assert!(promote_marshadow.is_stack);
    game.apply_action(&promote_marshadow);
    assert_eq!(game.get_state_clone().get_active(1).get_id(), "A1a 047");
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 70);

    // Checkup occurs while applying the offered EndTurn. Record all three victims immediately
    // after that action and before consuming the incoming turn's automatic DrawCard.
    let end_turn = legal_end_turn(&game, 0);
    game.apply_action(&end_turn);
    let after_checkup = game.get_state_clone();
    assert_eq!(after_checkup.current_player, 1);
    assert_eq!(after_checkup.turn_count, 9);
    assert_eq!(after_checkup.get_active(1).get_remaining_hp(), 60);
    assert_eq!(
        after_checkup.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        40
    );
    assert_eq!(
        after_checkup.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        120
    );
    assert!(
        after_checkup.get_knocked_out_by_opponent_attack_last_turn(),
        "the real Aerodactyl ex attack KO must rotate into Revenge's last-turn history"
    );
    settle_single_forced_draw(&mut game, 1);

    let attach_fighting = unique_action(&game, "turn Fighting attachment to Marshadow", |candidate| {
        matches!(
            &candidate.action,
            SimpleAction::Attach {
                attachments,
                is_turn_energy: true
            } if attachments == &vec![(1, EnergyType::Fighting, 0)]
        )
    });
    assert_eq!(attach_fighting.actor, 1);
    game.apply_action(&attach_fighting);
    assert_eq!(
        game.get_state_clone().get_active(1).attached_energy,
        vec![EnergyType::Fighting, EnergyType::Fighting]
    );

    let revenge = legal_attack(&game, 1, CardId::A1a047Marshadow, 0);
    game.apply_action(&revenge);
    let final_state = game.get_state_clone();
    assert!(final_state.in_play_pokemon[0][0].is_none());
    assert_eq!(
        final_state.in_play_pokemon[0][1]
            .as_ref()
            .expect("the observed Dartrix must survive the terminal attack")
            .get_remaining_hp(),
        80
    );
    assert_eq!(final_state.points, [2, 3]);
    assert_eq!(final_state.winner, Some(GameOutcome::Win(1)));
    assert!(
        final_state.move_generation_stack.iter().all(|(_, choices)| {
            choices
                .iter()
                .all(|choice| !matches!(choice, SimpleAction::Promote { player: 0, .. }))
        }),
        "three points must end the game without asking the recorder to promote Dartrix"
    );

    println!(
        "PASS observed composite: Dragon Pulse KO/+2 -> full promotion -> Sand Slammer all three -> attach Fighting -> Revenge 100 KO/+2 -> [2,3] Win(1)"
    );
}

#[test]
fn no_prior_attack_ko_revenge_control() {
    // Derived public control. It deliberately starts at the next-turn attack board with fresh
    // history instead of manufacturing the preceding KO flag.
    let recorder_board = vec![
        PlayedCard::from_id(CardId::B3126FlygonEx).with_remaining_hp(100),
    ];
    let opponent_board = vec![PlayedCard::from_id(CardId::A1a047Marshadow)
        .with_remaining_hp(60)
        .with_energy(vec![EnergyType::Fighting, EnergyType::Fighting])];
    let mut game = get_initialized_game_with_board(
        SEED + 1,
        1,
        9,
        recorder_board,
        opponent_board,
    );
    let mut state = game.get_state_clone();
    state.points = [2, 1];
    state.active_stadium = None;
    state.active_stadium_owner = None;
    game.set_state(state);
    assert!(!game
        .get_state_clone()
        .get_knocked_out_by_opponent_attack_last_turn());

    let revenge = legal_attack(&game, 1, CardId::A1a047Marshadow, 0);
    game.apply_action(&revenge);
    let final_state = game.get_state_clone();
    assert_eq!(final_state.get_active(0).get_remaining_hp(), 60);
    assert_eq!(final_state.points, [2, 1]);
    assert_eq!(final_state.winner, None);
    println!("PASS no-prior-KO control: Revenge remains 40 and Flygon ex 100->60");
}

#[test]
fn inactive_flygon_checkup_control() {
    // Derived positional control. The effect-inert Active and all private zones are synthetic;
    // only Flygon's move from Active to Bench is meant to change the Sand Slammer condition.
    let recorder_board = vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::B3126FlygonEx),
    ];
    let opponent_board = vec![
        PlayedCard::from_id(CardId::A1a047Marshadow).with_remaining_hp(70),
        PlayedCard::from_id(CardId::A1155Hitmonchan).with_remaining_hp(50),
        PlayedCard::from_id(CardId::A1153MarowakEx).with_remaining_hp(130),
    ];
    let mut game = get_initialized_game_with_board(
        SEED + 2,
        0,
        8,
        recorder_board,
        opponent_board,
    );
    let mut state = game.get_state_clone();
    state.active_stadium = None;
    state.active_stadium_owner = None;
    state.energy_zone[1].next = Some(EnergyType::Fighting);
    game.set_state(state);

    let before = game.get_state_clone();
    let before_hp = [
        before.in_play_pokemon[1][0]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        before.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        before.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
    ];
    finish_public_turn_handoff(&mut game, 0);
    let after = game.get_state_clone();
    let after_hp = [
        after.in_play_pokemon[1][0]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        after.in_play_pokemon[1][1]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
        after.in_play_pokemon[1][2]
            .as_ref()
            .unwrap()
            .get_remaining_hp(),
    ];
    assert_eq!(before_hp, [70, 50, 130]);
    assert_eq!(after_hp, before_hp);
    println!("PASS inactive-Flygon control: Checkup leaves all three opponent Pokemon unchanged");
}
