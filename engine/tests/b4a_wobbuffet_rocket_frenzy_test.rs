use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
};

fn rocket_frenzy() -> Action {
    Action {
        actor: 0,
        action: attack_action(CardId::PB091TeamRocketsWobbuffet, 0),
        is_stack: false,
    }
}

fn game_with_top(seed: u64, top: &[CardId]) -> deckgym::Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::PB091TeamRocketsWobbuffet)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1004VenusaurEx)],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = top.iter().map(|id| get_card_by_enum(*id)).collect();
    game.set_state(state);
    game
}

fn sorted(mut cards: Vec<Card>) -> Vec<Card> {
    cards.sort_by_key(Card::get_id);
    cards
}

#[test]
fn rocket_frenzy_replaces_printed_damage_and_counts_only_named_pokemon() {
    let mut game = game_with_top(
        7,
        &[
            CardId::PB088TeamRocketsScyther,
            CardId::B4a007TeamRocketsMoltresEx,
            CardId::B4a069TeamRocketsResearcher,
            CardId::A1001Bulbasaur,
            CardId::PB088TeamRocketsScyther,
            CardId::PA001Potion,
        ],
    );
    let original_order = game.get_state_clone().decks[0].cards.clone();
    let before = sorted(original_order.clone());
    game.apply_action(&rocket_frenzy());
    let after = game.get_state_clone();

    assert_eq!(
        after.get_active(1).get_remaining_hp(),
        100,
        "3 × 30, without adding the stored 30"
    );
    assert_eq!(sorted(after.decks[0].cards.clone()), before);
    assert_ne!(
        after.decks[0].cards, original_order,
        "the revealed cards must actually be shuffled"
    );
    assert_eq!(game.public_reveal_history().len(), 1);
    assert_eq!(game.public_reveal_history()[0].cause, "Rocket Frenzy");
    assert_eq!(
        game.public_reveal_history()[0].scope,
        "deck_prefix_then_shuffle"
    );
    assert_eq!(game.public_reveal_history()[0].cards.len(), 6);
}

#[test]
fn zero_qualifiers_reveals_and_shuffles_without_consuming_first_damage_shield() {
    let mut game = game_with_top(
        11,
        &[
            CardId::A1001Bulbasaur,
            CardId::PA001Potion,
            CardId::B4a069TeamRocketsResearcher,
        ],
    );
    let mut state = game.get_state_clone();
    state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::B2073MimikyuEx));
    game.set_state(state);

    game.apply_action(&rocket_frenzy());
    let after = game.get_state_clone();
    assert_eq!(after.get_active(1).get_remaining_hp(), 120);
    assert!(!after.get_active(1).prevent_first_attack_damage_used);
    assert_eq!(
        game.public_reveal_history()[0].cards.len(),
        3,
        "short deck reveals all remaining cards"
    );
}

#[test]
fn public_membership_is_unordered_and_visible_to_the_opponent() {
    let top = [
        CardId::PB088TeamRocketsScyther,
        CardId::B4a007TeamRocketsMoltresEx,
        CardId::PA001Potion,
        CardId::A1001Bulbasaur,
        CardId::B4a069TeamRocketsResearcher,
        CardId::A1033Charmander,
    ];
    let expected = sorted(top.iter().map(|id| get_card_by_enum(*id)).collect());
    let mut game = game_with_top(13, &top);
    game.apply_action(&rocket_frenzy());

    let owner = game.observation(0);
    assert_eq!(sorted(owner.known_own_deck.clone()), expected);
    assert!(owner.revealed.deck_top[0].is_empty());

    let opponent = game.observation(1);
    assert_eq!(opponent.revealed.opponent_deck_membership, expected);
    assert!(opponent.revealed.deck_top[0].is_empty());
    assert!(opponent.visible_state().decks[0]
        .cards
        .iter()
        .all(Card::is_unknown));
    let serialized = serde_json::to_string(&opponent).unwrap();
    assert!(!serialized.contains("public_reveal_events"));
}

#[test]
fn repeated_public_reveal_uses_max_multiplicity_instead_of_adding() {
    let top = [
        CardId::PB088TeamRocketsScyther,
        CardId::PB088TeamRocketsScyther,
        CardId::PA001Potion,
    ];
    let mut game = game_with_top(17, &top);
    game.apply_action(&rocket_frenzy());
    assert_eq!(
        game.observation(1)
            .revealed
            .opponent_deck_membership
            .iter()
            .filter(|card| card.get_id() == "P-B 088")
            .count(),
        2
    );
    // The three-card deck reveals the same physical multiplicities again after every shuffle.
    // Direct application bypasses normal turn legality so this test can isolate knowledge merge.
    game.apply_action(&rocket_frenzy());
    assert_eq!(
        game.observation(1)
            .revealed
            .opponent_deck_membership
            .iter()
            .filter(|card| card.get_id() == "P-B 088")
            .count(),
        2
    );
}

#[test]
fn unknown_draw_conservatively_invalidates_opponent_membership() {
    let top = [
        CardId::PB088TeamRocketsScyther,
        CardId::PA001Potion,
        CardId::A1001Bulbasaur,
    ];
    let mut game = game_with_top(18, &top);
    game.apply_action(&rocket_frenzy());
    assert!(!game
        .observation(1)
        .revealed
        .opponent_deck_membership
        .is_empty());

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::DrawCard { amount: 1 },
        is_stack: false,
    });
    assert!(game
        .observation(1)
        .revealed
        .opponent_deck_membership
        .is_empty());
}

#[test]
fn copied_rocket_frenzy_uses_and_shuffles_the_copiers_deck() {
    let mut game = get_initialized_game_with_board(
        19,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Psychic,
        ])],
        vec![
            PlayedCard::from_id(CardId::PB091TeamRocketsWobbuffet),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    let mut state = game.get_state_clone();
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::PB088TeamRocketsScyther),
        get_card_by_enum(CardId::PB088TeamRocketsScyther),
    ];
    state.decks[1].cards = vec![get_card_by_enum(CardId::PA001Potion)];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1a032MewEx, 1),
        is_stack: false,
    });
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let copied = choices
        .into_iter()
        .find(|action| matches!(&action.action, SimpleAction::Attack(attack) if attack.title == "Rocket Frenzy"))
        .unwrap();
    game.apply_action(&copied);

    let after = game.get_state_clone();
    assert_eq!(
        after.get_active(1).get_remaining_hp(),
        20,
        "copier's two qualifying cards deal 60"
    );
    assert_eq!(after.decks[0].cards.len(), 2);
    assert_eq!(
        after.decks[1].cards,
        vec![get_card_by_enum(CardId::PA001Potion)]
    );
    assert_eq!(game.public_reveal_history()[0].zone_owner, 0);
}

#[test]
fn opponent_rocket_frenzy_stays_unpriced_when_deck_identities_are_unknown() {
    let top = [
        CardId::PB088TeamRocketsScyther,
        CardId::PA001Potion,
        CardId::A1001Bulbasaur,
    ];
    let mut game = game_with_top(23, &top);
    game.apply_action(&rocket_frenzy());

    let observer = game.observation(1);
    assert!(!observer.revealed.opponent_deck_membership.is_empty());
    assert_eq!(
        deckgym::observation::hidden_continuation_reason(
            observer.visible_state(),
            &rocket_frenzy(),
        ),
        Some("effect depends on unknown cards in the acting player's hidden zones"),
        "unordered membership is informational and must not be converted into an invented deck prefix",
    );
}
