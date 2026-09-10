use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Attacks Regirock (A2 087, a *Basic* whose Ability reads "This Pokémon takes -20 damage from
/// attacks") with a Bulbasaur, optionally with an Alolan Muk on `bench_owner`'s Bench, and returns
/// the damage Regirock ended up with.
fn damage_dealt_to_regirock(muk_bench_owner: Option<usize>) -> u32 {
    let filler = PlayedCard::from_id(CardId::A1033Charmander);
    let muk = PlayedCard::from_id(CardId::B2097AlolanMuk);

    let own_bench = match muk_bench_owner {
        Some(0) => muk.clone(),
        _ => filler.clone(),
    };
    let opponent_bench = match muk_bench_owner {
        Some(1) => muk,
        _ => filler,
    };

    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
            own_bench,
        ],
        vec![PlayedCard::from_id(CardId::A2087Regirock), opponent_bench],
    );

    let regirock_full_hp = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    regirock_full_hp - game.get_state_clone().get_active(1).get_remaining_hp()
}

fn data_scan_offered_with_muk(muk_in_play: bool) -> bool {
    let bench = if muk_in_play {
        PlayedCard::from_id(CardId::B2097AlolanMuk)
    } else {
        PlayedCard::from_id(CardId::A1033Charmander)
    };
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1209Porygon), bench],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseAbility { in_play_idx: 0 }))
}

/// NEGATIVE (baseline): with no Alolan Muk anywhere, Regirock's Basic Ability reduces the damage
/// it takes by 20.
#[test]
fn test_basic_passive_ability_works_without_alolan_muk() {
    let unblocked = damage_dealt_to_regirock(None);
    assert!(unblocked > 0, "Bulbasaur's attack should do some damage");

    // Sanity: the Ability really is worth 20 damage here.
    let suppressed = damage_dealt_to_regirock(Some(0));
    assert_eq!(
        unblocked + 20,
        suppressed,
        "Regirock's -20 Ability should be worth exactly 20 damage"
    );
}

/// Power of Alchemy: "Basic Pokémon in play (both yours and your opponent's) have no Abilities."
/// Regirock is a Basic, so its passive damage reduction stops applying — and note Alolan Muk is
/// the only Ability holder on the board here, which is also what proves it does not switch itself
/// off (it is a Stage 1, so it is not a "Basic Pokémon in play").
#[test]
fn test_power_of_alchemy_suppresses_a_basics_passive_ability() {
    assert_eq!(
        damage_dealt_to_regirock(Some(0)),
        damage_dealt_to_regirock(None) + 20,
        "Regirock's -20 damage Ability must not apply while Power of Alchemy is in play"
    );
}

/// "Both yours and your opponent's": Alolan Muk suppresses the Basic Abilities of the player who
/// controls it, too.
#[test]
fn test_power_of_alchemy_suppresses_its_own_controllers_basics() {
    assert_eq!(
        damage_dealt_to_regirock(Some(1)),
        damage_dealt_to_regirock(None) + 20,
        "Power of Alchemy is symmetric, so Regirock loses its Ability to its own side's Muk"
    );
}

/// The other half of "have no Abilities": an *activated* Ability on a Basic disappears from move
/// generation, so it cannot be used at all.
#[test]
fn test_power_of_alchemy_removes_a_basics_activated_ability_from_move_generation() {
    assert!(
        data_scan_offered_with_muk(false),
        "Porygon's Data Scan should be offered when no Alolan Muk is in play"
    );
    assert!(
        !data_scan_offered_with_muk(true),
        "Porygon is a Basic, so Power of Alchemy must remove Data Scan entirely"
    );
}

/// NEGATIVE: only *Basic* Pokémon lose their Abilities. Cloyster is a Stage 1, so its "-10 damage
/// from attacks" keeps working with Alolan Muk in play.
#[test]
fn test_power_of_alchemy_leaves_evolved_pokemon_alone() {
    let damage_with_muk = damage_dealt_to_cloyster(true);
    let damage_without_muk = damage_dealt_to_cloyster(false);
    assert_eq!(
        damage_with_muk, damage_without_muk,
        "Cloyster is a Stage 1, so Power of Alchemy must not touch its Shell Armor"
    );
}

fn damage_dealt_to_cloyster(muk_in_play: bool) -> u32 {
    let bench = if muk_in_play {
        PlayedCard::from_id(CardId::B2097AlolanMuk)
    } else {
        PlayedCard::from_id(CardId::A1033Charmander)
    };
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
            bench,
        ],
        vec![PlayedCard::from_id(CardId::A1067Cloyster)],
    );

    let full_hp = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    full_hp - game.get_state_clone().get_active(1).get_remaining_hp()
}
