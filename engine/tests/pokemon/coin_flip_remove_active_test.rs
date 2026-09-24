use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    State,
};

/// Attacks that remove the opponent's Active Pokémon on a successful coin flip:
///
/// - Bewear (A3a 058) "Superpowered Hug": "Flip 2 coins. If both of them are heads, your
///   opponent's Active Pokémon is Knocked Out." — a real knockout, so it scores points.
/// - Guzzlord (B2 109) "Breakcore": "Flip a coin. If heads, discard your opponent's Active
///   Pokémon." — a discard, so it scores nothing.
/// - Scream Tail (B3a 025) "Shooing Shout": "Flip 2 coins. If both of them are heads, discard your
///   opponent's Active Pokémon."
fn attack_snorlax(seed: u64, card_id: CardId, energy: Vec<EnergyType>) -> State {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(card_id).with_energy(energy)],
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
    );

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });

    // Removing the Active Pokémon leaves the opponent with a promotion to make.
    while !game.get_state_clone().move_generation_stack.is_empty() {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        game.apply_action(&choices[0].clone());
    }

    game.get_state_clone()
}

fn bewear(seed: u64) -> State {
    attack_snorlax(
        seed,
        CardId::A3a058Bewear,
        vec![
            EnergyType::Colorless,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ],
    )
}

fn guzzlord(seed: u64) -> State {
    attack_snorlax(
        seed,
        CardId::B2109Guzzlord,
        vec![
            EnergyType::Darkness,
            EnergyType::Darkness,
            EnergyType::Darkness,
            EnergyType::Colorless,
        ],
    )
}

/// True when the attack removed Snorlax from the Active Spot (its Benched Charmander was promoted
/// in its place by the loop in `attack_snorlax`).
fn active_was_removed(state: &State) -> bool {
    state.get_active(1).get_name() == "Charmander"
}

fn scream_tail(seed: u64) -> State {
    attack_snorlax(
        seed,
        CardId::B3a025ScreamTail,
        vec![EnergyType::Psychic, EnergyType::Psychic],
    )
}

#[test]
fn test_superpowered_hug_knocks_out_on_double_heads_and_scores_the_points() {
    let removed = (0..60)
        .map(bewear)
        .find(active_was_removed)
        .expect("2 heads should come up within 60 seeds");

    assert_eq!(
        removed.points[0], 1,
        "a Knocked Out Snorlax is worth 1 point"
    );
    assert!(
        removed.discard_piles[1]
            .iter()
            .any(|card| card.get_name() == "Snorlax"),
        "the Knocked Out Pokémon should end up in its owner's discard pile"
    );
    assert_eq!(
        removed.get_active(1).get_name(),
        "Charmander",
        "the opponent should have promoted their Benched Pokémon"
    );
}

/// Negative case: on anything short of two heads, nothing happens at all.
#[test]
fn test_superpowered_hug_does_nothing_without_double_heads() {
    let untouched = (0..60)
        .map(bewear)
        .find(|state| !active_was_removed(state))
        .expect("at least one non-heads result should come up within 60 seeds");

    assert_eq!(
        untouched.get_active(1).get_remaining_hp(),
        150,
        "Superpowered Hug does no damage of its own"
    );
    assert_eq!(untouched.points[0], 0, "no knockout, no points");
}

/// Both coins matter: a mechanic that only looked at the first coin would remove the defender in
/// roughly half of all seeds instead of roughly a quarter.
#[test]
fn test_superpowered_hug_needs_both_coins() {
    let removals = (0..200)
        .filter(|seed| active_was_removed(&bewear(*seed)))
        .count();

    assert!(
        (20..=80).contains(&removals),
        "expected roughly 1 in 4 of 200 seeds to knock out, got {removals}"
    );
}

/// "Discard your opponent's Active Pokémon" is not a knockout: the Pokémon leaves play, but the
/// attacker scores nothing for it.
#[test]
fn test_breakcore_discards_without_scoring_points() {
    let discarded = (0..40)
        .map(guzzlord)
        .find(active_was_removed)
        .expect("heads should come up within 40 seeds");

    assert_eq!(
        discarded.points[0], 0,
        "discarding the Active Pokémon must not award any points"
    );
    assert!(
        discarded.discard_piles[1]
            .iter()
            .any(|card| card.get_name() == "Snorlax"),
        "the discarded Pokémon should be in its owner's discard pile"
    );
    assert_eq!(
        discarded.get_active(1).get_name(),
        "Charmander",
        "the opponent should have promoted their Benched Pokémon"
    );
}

#[test]
fn test_breakcore_does_nothing_on_tails() {
    let untouched = (0..40)
        .map(guzzlord)
        .find(|state| !active_was_removed(state))
        .expect("tails should come up within 40 seeds");

    assert_eq!(untouched.get_active(1).get_remaining_hp(), 150);
    assert_eq!(untouched.points[0], 0);
}

#[test]
fn test_shooing_shout_discards_on_double_heads_without_scoring_points() {
    let discarded = (0..60)
        .map(scream_tail)
        .find(active_was_removed)
        .expect("2 heads should come up within 60 seeds");

    assert_eq!(
        discarded.points[0], 0,
        "Shooing Shout discards rather than knocking out, so it scores nothing"
    );
    assert_eq!(discarded.get_active(1).get_name(), "Charmander");
}

#[test]
fn test_shooing_shout_does_nothing_without_double_heads() {
    let untouched = (0..60)
        .map(scream_tail)
        .find(|state| !active_was_removed(state))
        .expect("at least one non-heads result should come up within 60 seeds");

    assert_eq!(untouched.get_active(1).get_remaining_hp(), 150);
}
