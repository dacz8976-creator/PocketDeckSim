use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard},
    test_support::{attack_action, get_initialized_game, get_initialized_game_with_board},
    Game,
};

fn card(id: CardId) -> Card {
    get_card_by_enum(id)
}

fn trainer(id: CardId) -> TrainerCard {
    card(id).as_trainer()
}

fn action(actor: usize, simple: SimpleAction) -> Action {
    Action {
        actor,
        action: simple,
        is_stack: false,
    }
}

fn count_named(cards: &[Card], name: &str) -> usize {
    cards.iter().filter(|card| card.get_name() == name).count()
}

fn set_hand(game: &mut Game<'static>, player: usize, cards: Vec<Card>) {
    let mut state = game.get_state_clone();
    state.hands[player] = cards;
    game.set_state(state);
}

fn play_tool(game: &mut Game<'static>, player: usize, tool_id: CardId, target: usize) {
    let mut state = game.get_state_clone();
    state.current_player = player;
    state.turn_count = state.turn_count.max(3);
    state.hands[player] = vec![card(tool_id)];
    game.set_state(state);

    game.apply_action(&action(
        player,
        SimpleAction::Play {
            trainer_card: trainer(tool_id),
        },
    ));
    let attach = game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::AttachTool { in_play_idx, .. } if in_play_idx == target
            )
        })
        .expect("expected legal Tool attachment target");
    game.apply_action(&attach);
}

fn play_trainer(game: &mut Game<'static>, player: usize, trainer_id: CardId) {
    let mut state = game.get_state_clone();
    state.current_player = player;
    state.turn_count = state.turn_count.max(3);
    state.hands[player] = vec![card(trainer_id)];
    game.set_state(state);
    game.apply_action(&action(
        player,
        SimpleAction::Play {
            trainer_card: trainer(trainer_id),
        },
    ));
}

fn hand_offers_tool(game: &Game<'static>, tool_id: CardId) -> bool {
    let expected = card(tool_id).get_id();
    game.get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|choice| {
            matches!(
                &choice.action,
                SimpleAction::Play { trainer_card } if trainer_card.id == expected
            )
        })
}

fn revavroom(tools: Vec<Card>) -> PlayedCard {
    PlayedCard::from_id(CardId::B4115Revavroom).with_tools(tools)
}

#[test]
fn dual_customization_allows_second_tool_but_not_third() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B4115Revavroom)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    play_tool(&mut game, 0, CardId::A2147GiantCape, 0);
    play_tool(&mut game, 0, CardId::A2148RockyHelmet, 0);
    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_tools.len(),
        2,
        "B4 115 Revavroom should keep both attachments"
    );
    assert_eq!(
        state.get_active(0).attached_tools[0].get_name(),
        "Giant Cape",
        "attachment order should be stable"
    );

    set_hand(&mut game, 0, vec![card(CardId::A2149LumBerry)]);
    assert!(
        !hand_offers_tool(&game, CardId::A2149LumBerry),
        "a third Tool must not be playable onto a full Revavroom"
    );
}

#[test]
fn dual_customization_allows_two_identical_tools_through_legal_play() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::B4115Revavroom)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    play_tool(&mut game, 0, CardId::A2147GiantCape, 0);
    play_tool(&mut game, 0, CardId::A2147GiantCape, 0);

    let holder = game.get_state_clone().get_active(0).clone();
    assert_eq!(holder.attached_tools.len(), 2);
    assert!(holder
        .attached_tools
        .iter()
        .all(|tool| tool.get_name() == "Giant Cape"));
    assert_eq!(holder.get_remaining_hp(), 160);
}

#[test]
fn ordinary_pokemon_and_other_revavroom_printings_still_have_one_slot() {
    for holder in [
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::B2b050Revavroom),
    ] {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![holder],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        play_tool(&mut game, 0, CardId::A2147GiantCape, 0);
        set_hand(&mut game, 0, vec![card(CardId::A2148RockyHelmet)]);
        assert!(
            !hand_offers_tool(&game, CardId::A2148RockyHelmet),
            "only the B4 115 printing should receive a second Tool slot"
        );
        assert_eq!(game.get_state_clone().get_active(0).attached_tools.len(), 1);
    }
}

#[test]
fn duplicate_and_different_hp_tools_stack_on_revavroom() {
    let double_cape = revavroom(vec![
        card(CardId::A2147GiantCape),
        card(CardId::A2147GiantCape),
    ]);
    assert_eq!(
        double_cape.get_remaining_hp(),
        160,
        "two identical Giant Capes add 40 to Revavroom's printed 120 HP"
    );

    let mixed = revavroom(vec![
        card(CardId::A2147GiantCape),
        card(CardId::B3b065ElegantCape),
    ]);
    assert_eq!(
        mixed.get_remaining_hp(),
        170,
        "Giant Cape and the Stage-1 Elegant Cape should both apply"
    );
}

#[test]
fn two_steel_aprons_reduce_one_attack_by_twenty() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![revavroom(vec![
            card(CardId::A4153SteelApron),
            card(CardId::A4153SteelApron),
        ])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&action(
        1,
        SimpleAction::ApplyDamage {
            attacking_ref: (1, 0),
            targets: vec![(100, 0, 0)],
            is_from_active_attack: true,
        },
    ));

    assert_eq!(
        game.get_state_clone().get_active(0).get_remaining_hp(),
        40,
        "100 attack damage minus two 10-point Steel Aprons should leave 40 HP"
    );
}

#[test]
fn field_blower_offers_each_tool_and_removes_only_selected_index() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![revavroom(vec![cape.clone(), helmet.clone()])],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    play_trainer(&mut game, 1, CardId::B3147FieldBlower);
    let choices = game.get_state_clone().generate_possible_actions().1;
    let offered: Vec<usize> = choices
        .iter()
        .filter_map(|choice| match choice.action {
            SimpleAction::DiscardToolFromPokemon {
                player: 0,
                in_play_idx: 0,
                tool_idx,
            } => Some(tool_idx),
            _ => None,
        })
        .collect();
    assert_eq!(offered, vec![0, 1], "both attachment indices must be selectable");

    let remove_helmet = choices
        .into_iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::DiscardToolFromPokemon {
                    player: 0,
                    in_play_idx: 0,
                    tool_idx: 1
                }
            )
        })
        .unwrap();
    game.apply_action(&remove_helmet);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_tools, vec![cape]);
    assert!(state.discard_piles[0].contains(&helmet));
}

#[test]
fn field_blower_selected_hp_tool_can_cause_knockout_without_losing_other_tool() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![
            revavroom(vec![cape.clone(), helmet.clone()]).with_damage(120),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );

    play_trainer(&mut game, 1, CardId::B3147FieldBlower);
    let remove_cape = game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::DiscardToolFromPokemon {
                    player: 0,
                    in_play_idx: 0,
                    tool_idx: 0
                }
            )
        })
        .unwrap();
    game.apply_action(&remove_cape);

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[0][0].is_none());
    assert_eq!(state.points[1], 1);
    assert!(state.discard_piles[0].contains(&cape));
    assert!(
        state.discard_piles[0].contains(&helmet),
        "the other Tool must follow its holder to discard on knockout"
    );
}

#[test]
fn guzma_discards_every_tool_from_dual_customization_holder() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
        vec![revavroom(vec![cape.clone(), helmet.clone()])],
    );

    play_trainer(&mut game, 0, CardId::A3151Guzma);

    let state = game.get_state_clone();
    assert!(state.get_active(1).attached_tools.is_empty());
    assert!(state.discard_piles[1].contains(&cape));
    assert!(state.discard_piles[1].contains(&helmet));
}

#[test]
fn elesa_returns_all_tools_to_each_owners_hand() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![revavroom(vec![
            card(CardId::A2147GiantCape),
            card(CardId::A2148RockyHelmet),
        ])],
        vec![revavroom(vec![
            card(CardId::A4153SteelApron),
            card(CardId::A4153SteelApron),
        ])],
    );
    let before_opponent_aprons =
        count_named(&game.get_state_clone().hands[1], "Steel Apron");

    play_trainer(&mut game, 0, CardId::B3b066Elesa);

    let state = game.get_state_clone();
    assert!(state.get_active(0).attached_tools.is_empty());
    assert!(state.get_active(1).attached_tools.is_empty());
    assert_eq!(count_named(&state.hands[0], "Giant Cape"), 1);
    assert_eq!(count_named(&state.hands[0], "Rocky Helmet"), 1);
    assert_eq!(
        count_named(&state.hands[1], "Steel Apron"),
        before_opponent_aprons + 2
    );
}

#[test]
fn dismantling_keys_discards_both_tools_before_discarding_klefki() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let klefki = card(CardId::B1120Klefki);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::B1120Klefki),
        ],
        vec![revavroom(vec![cape.clone(), helmet.clone()])],
    );

    let ability = game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|choice| {
            matches!(
                choice.action,
                SimpleAction::UseAbility { in_play_idx: 1 }
            )
        })
        .expect("Klefki should be usable from the Bench");
    game.apply_action(&ability);

    let state = game.get_state_clone();
    assert!(state.get_active(1).attached_tools.is_empty());
    assert!(state.discard_piles[1].contains(&cape));
    assert!(state.discard_piles[1].contains(&helmet));
    assert!(state.discard_piles[0].contains(&klefki));
}

#[test]
fn ordinary_knockout_discards_both_tools() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            revavroom(vec![cape.clone(), helmet.clone()]),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );

    game.apply_action(&action(
        0,
        SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(300, 1, 0)],
            is_from_active_attack: true,
        },
    ));

    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert!(state.discard_piles[1].contains(&cape));
    assert!(state.discard_piles[1].contains(&helmet));
}

#[test]
fn rescue_scarf_returns_only_pokemon_and_discards_both_tools() {
    let scarf = card(CardId::A4155RescueScarf);
    let cape = card(CardId::A2147GiantCape);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            revavroom(vec![scarf.clone(), cape.clone()]),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
    );
    let hand_before = game.get_state_clone().hands[1].len();

    game.apply_action(&action(
        0,
        SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(300, 1, 0)],
            is_from_active_attack: true,
        },
    ));

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), hand_before + 1);
    assert!(state.hands[1].iter().any(|card| card.get_id() == "B4 115"));
    assert!(state.discard_piles[1].contains(&scarf));
    assert!(state.discard_piles[1].contains(&cape));
    assert!(!state.discard_piles[1].iter().any(|card| card.get_id() == "B4 115"));
}

#[test]
fn return_and_shuffle_actions_conserve_tools_and_energy() {
    for shuffle in [false, true] {
        let cape = card(CardId::A2147GiantCape);
        let helmet = card(CardId::A2148RockyHelmet);
        let mut game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                revavroom(vec![cape.clone(), helmet.clone()])
                    .with_energy(vec![EnergyType::Metal]),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );

        let movement = if shuffle {
            SimpleAction::ShuffleInPlayPokemonIntoDeck { in_play_idx: 1 }
        } else {
            SimpleAction::ReturnPokemonToHand { in_play_idx: 1 }
        };
        game.apply_action(&action(0, movement));

        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[0][1].is_none());
        assert!(state.discard_piles[0].contains(&cape));
        assert!(state.discard_piles[0].contains(&helmet));
        assert_eq!(state.discard_energies[0], vec![EnergyType::Metal]);
        if shuffle {
            assert!(state.decks[0].cards.iter().any(|card| card.get_id() == "B4 115"));
        } else {
            assert!(state.hands[0].iter().any(|card| card.get_id() == "B4 115"));
        }
    }
}

#[test]
fn legacy_single_tool_and_new_tool_vector_both_deserialize() {
    let cape = card(CardId::A2147GiantCape);
    let helmet = card(CardId::A2148RockyHelmet);

    let current = revavroom(vec![cape.clone(), helmet.clone()]);
    let encoded = serde_json::to_value(&current).unwrap();
    assert_eq!(encoded["attached_tools"].as_array().unwrap().len(), 2);
    assert!(encoded.get("attached_tool").is_none());
    let round_trip: PlayedCard = serde_json::from_value(encoded).unwrap();
    assert_eq!(round_trip.attached_tools, vec![cape.clone(), helmet]);

    let mut legacy = serde_json::to_value(PlayedCard::from_id(CardId::B4115Revavroom)).unwrap();
    let object = legacy.as_object_mut().unwrap();
    object.remove("attached_tools");
    object.insert("attached_tool".into(), serde_json::to_value(cape.clone()).unwrap());
    let restored: PlayedCard = serde_json::from_value(legacy).unwrap();
    assert_eq!(restored.attached_tools, vec![cape]);

    let mut legacy_none =
        serde_json::to_value(PlayedCard::from_id(CardId::B4115Revavroom)).unwrap();
    let object = legacy_none.as_object_mut().unwrap();
    object.remove("attached_tools");
    object.insert("attached_tool".into(), serde_json::Value::Null);
    let restored_none: PlayedCard = serde_json::from_value(legacy_none).unwrap();
    assert!(restored_none.attached_tools.is_empty());
}

#[test]
fn public_observation_preserves_both_tool_identities_and_order() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.current_player = 0;
    state.turn_count = 3;
    state.set_board(
        vec![revavroom(vec![
            card(CardId::A2147GiantCape),
            card(CardId::A2148RockyHelmet),
        ])],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    game.set_state(state);

    let visible = game.observation(0);
    let names: Vec<String> = visible
        .visible_state()
        .get_active(0)
        .attached_tools
        .iter()
        .map(Card::get_name)
        .collect();
    assert_eq!(names, vec!["Giant Cape", "Rocky Helmet"]);
}

#[test]
fn named_tool_in_second_slot_still_triggers() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![revavroom(vec![
            card(CardId::A2147GiantCape),
            card(CardId::A2148RockyHelmet),
        ])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&action(
        1,
        SimpleAction::ApplyDamage {
            attacking_ref: (1, 0),
            targets: vec![(10, 0, 0)],
            is_from_active_attack: true,
        },
    ));

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        50,
        "Rocky Helmet in slot 2 should counterattack for 20"
    );
}

#[test]
fn per_tool_attack_counts_two_tools_on_one_revavroom() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B3b023Emolga)
                .with_energy(vec![EnergyType::Lightning, EnergyType::Lightning]),
            revavroom(vec![
                card(CardId::A2147GiantCape),
                card(CardId::A2148RockyHelmet),
            ]),
        ],
        vec![PlayedCard::from_id(CardId::A1004VenusaurEx)],
    );

    game.apply_action(&action(0, attack_action(CardId::B3b023Emolga, 0)));

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        130,
        "Windup Thunder should count two Tool cards on one holder: 190 - 60"
    );
}

#[test]
fn second_slot_sitrus_consumes_only_itself_and_preserves_cape() {
    let cape = card(CardId::A2147GiantCape);
    let sitrus = card(CardId::B1218SitrusBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            revavroom(vec![cape.clone(), sitrus.clone()]).with_damage(70),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&action(0, SimpleAction::EndTurn));

    let state = game.get_state_clone();
    let holder = state.in_play_pokemon[0][0].as_ref().unwrap();
    assert_eq!(holder.get_remaining_hp(), 100);
    assert_eq!(holder.attached_tools, vec![cape]);
    assert!(state.discard_piles[0].contains(&sitrus));
}

#[test]
fn heal_block_prevents_sitrus_heal_and_consumption_in_second_slot() {
    let cape = card(CardId::A2147GiantCape);
    let sitrus = card(CardId::B1218SitrusBerry);
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            revavroom(vec![cape.clone(), sitrus.clone()]).with_damage(70),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A3a031Claydol)],
    );

    game.apply_action(&action(0, SimpleAction::EndTurn));

    let state = game.get_state_clone();
    let holder = state.in_play_pokemon[0][0].as_ref().unwrap();
    assert_eq!(holder.get_remaining_hp(), 70, "Heal Block should prevent healing");
    assert_eq!(
        holder.attached_tools,
        vec![cape, sitrus],
        "Sitrus says 'If you do'; it must remain when Heal Block prevents the heal"
    );
}

#[test]
fn two_metal_core_barriers_both_expire_at_end_of_opponents_turn() {
    let barrier_a = card(CardId::B2148MetalCoreBarrier);
    let barrier_b = card(CardId::B2b117MetalCoreBarrier);
    let mut game = get_initialized_game_with_board(
        0,
        1,
        3,
        vec![revavroom(vec![barrier_a.clone(), barrier_b.clone()])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&action(1, SimpleAction::EndTurn));

    let state = game.get_state_clone();
    assert!(state.get_active(0).attached_tools.is_empty());
    assert!(state.discard_piles[0].contains(&barrier_a));
    assert!(state.discard_piles[0].contains(&barrier_b));
}
