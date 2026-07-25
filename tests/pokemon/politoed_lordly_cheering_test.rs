use deckgym::{
    actions::Action,
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
};

/// Mega Latios ex (180 HP, no Weakness) is the damage sponge, so the +40 stays visible and no
/// knockout caps the observed HP difference.
fn latios_hp_after_attack(attacker_board: Vec<PlayedCard>, attacker: CardId) -> u32 {
    let mut game = get_test_game_with_board(
        attacker_board,
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker, 0),
        is_stack: false,
    });
    game.get_state_clone().get_active(1).get_remaining_hp()
}

/// Poliwrath's Mega Punch: 80 damage for [W][C][C]. Poliwrath evolves from Poliwhirl.
fn poliwrath() -> PlayedCard {
    PlayedCard::from_id(CardId::A1061Poliwrath).with_energy(vec![
        EnergyType::Water,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ])
}

/// Politoed's Hyper Voice: 60 damage for [W][C]. Politoed also evolves from Poliwhirl.
fn politoed() -> PlayedCard {
    PlayedCard::from_id(CardId::A4040Politoed)
        .with_energy(vec![EnergyType::Water, EnergyType::Colorless])
}

/// Politoed's Lordly Cheering (A4 040): "As long as this Pokémon is on your Bench, attacks used by
/// your Pokémon that evolve from Poliwhirl do +40 damage to your opponent's Active Pokémon."
#[test]
fn test_lordly_cheering_boosts_poliwhirl_evolution_from_bench() {
    let hp = latios_hp_after_attack(
        vec![poliwrath(), PlayedCard::from_id(CardId::A4040Politoed)],
        CardId::A1061Poliwrath,
    );
    assert_eq!(
        hp, 60,
        "A Benched Politoed should add 40 to Poliwrath's 80 damage Mega Punch"
    );
}

/// NEGATIVE: without a Benched Politoed the attack does its printed damage.
#[test]
fn test_poliwrath_does_printed_damage_without_politoed() {
    let hp = latios_hp_after_attack(vec![poliwrath()], CardId::A1061Poliwrath);
    assert_eq!(hp, 100, "Poliwrath's Mega Punch alone should do 80 damage");
}

/// NEGATIVE: "as long as this Pokémon is on your Bench" — an Active Politoed does not boost its
/// own attack.
#[test]
fn test_lordly_cheering_does_not_boost_itself_from_the_active_spot() {
    let hp = latios_hp_after_attack(vec![politoed()], CardId::A4040Politoed);
    assert_eq!(
        hp, 120,
        "Politoed in the Active Spot should only do its printed 60 damage"
    );
}

/// A Benched Politoed does boost an *Active* Politoed, which also evolves from Poliwhirl.
#[test]
fn test_lordly_cheering_boosts_another_politoed_from_bench() {
    let hp = latios_hp_after_attack(
        vec![politoed(), PlayedCard::from_id(CardId::A4040Politoed)],
        CardId::A4040Politoed,
    );
    assert_eq!(
        hp, 80,
        "Only the Benched Politoed grants the bonus, so the Active Politoed does 60 + 40"
    );
}

/// NEGATIVE: the attacker has to evolve from Poliwhirl. Lunatone does not.
#[test]
fn test_lordly_cheering_does_not_boost_unrelated_attacker() {
    let hp = latios_hp_after_attack(
        vec![
            PlayedCard::from_id(CardId::A3073Lunatone)
                .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A4040Politoed),
        ],
        CardId::A3073Lunatone,
    );
    assert_eq!(
        hp, 130,
        "Lunatone does not evolve from Poliwhirl, so Lordly Cheering should not apply"
    );
}
