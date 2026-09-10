use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

/// A Regigigas holding exactly the Energy Giga Turbo costs.
fn powered_regigigas() -> PlayedCard {
    PlayedCard::from_id(CardId::B3134Regigigas).with_energy(vec![
        EnergyType::Colorless,
        EnergyType::Colorless,
        EnergyType::Colorless,
    ])
}

/// Puts Regigigas (fully powered for Giga Turbo) in the Active Spot behind `bench` and reports
/// whether the engine offers it an attack.
fn regigigas_can_attack(bench: [CardId; 3]) -> bool {
    regigigas_can_attack_against(bench, [CardId::A1001Bulbasaur].as_slice())
}

/// Same as [`regigigas_can_attack`], but with the opponent's whole board spelled out (their Active
/// Spot first) so tests can put cards on the *other* side of the table.
fn regigigas_can_attack_against(bench: [CardId; 3], opponent_board: &[CardId]) -> bool {
    let mut board = vec![powered_regigigas()];
    board.extend(bench.into_iter().map(PlayedCard::from_id));

    let game = get_test_game_with_board(
        board,
        opponent_board
            .iter()
            .copied()
            .map(PlayedCard::from_id)
            .collect(),
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Attack(_)))
}

/// Regigigas (B3 134) "Seal of Antiquity": "If you don't have Regirock, Regice, and Registeel on
/// your Bench, this Pokémon can't attack."
#[test]
fn test_seal_of_antiquity_allows_attacking_with_the_full_regi_bench() {
    assert!(
        regigigas_can_attack([
            CardId::B3077Regirock,
            CardId::B3045Regice,
            CardId::B3116Registeel,
        ]),
        "with all three Regis on the Bench, Giga Turbo should be offered"
    );
}

/// Negative test: the condition is an *and*, so dropping any single Regi seals the attack away.
/// Bench order should not matter either, hence the swapped positions here.
#[test]
fn test_seal_of_antiquity_blocks_attacking_when_a_regi_is_missing() {
    assert!(
        !regigigas_can_attack([
            CardId::B3116Registeel,
            CardId::B3077Regirock,
            CardId::A1001Bulbasaur,
        ]),
        "without Regice on the Bench, Regigigas must not be offered an attack"
    );
    assert!(
        !regigigas_can_attack([
            CardId::B3045Regice,
            CardId::B3116Registeel,
            CardId::A1001Bulbasaur,
        ]),
        "without Regirock on the Bench, Regigigas must not be offered an attack"
    );
    assert!(
        !regigigas_can_attack([
            CardId::B3077Regirock,
            CardId::B3045Regice,
            CardId::A1001Bulbasaur,
        ]),
        "without Registeel on the Bench, Regigigas must not be offered an attack"
    );
}

/// The restriction is scoped to the Ability's holder: a Regigigas *on the Bench* does not stop the
/// Active Pokémon from attacking, and the Active Pokémon's own attacks are unaffected.
#[test]
fn test_seal_of_antiquity_only_restricts_its_own_holder() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1094Pikachu).with_energy(vec![EnergyType::Lightning]),
            PlayedCard::from_id(CardId::B3134Regigigas),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(
        choices
            .iter()
            .any(|choice| matches!(choice.action, SimpleAction::Attack(_))),
        "a Benched Regigigas must not seal the Active Pokémon's attacks"
    );
}

/// "on your Bench": the requirement is scoped to the Ability holder's own side, so the opponent
/// parading all three Regis does nothing for a sealed Regigigas.
#[test]
fn test_seal_of_antiquity_ignores_the_opponents_regis() {
    assert!(
        !regigigas_can_attack_against(
            [
                CardId::A1001Bulbasaur,
                CardId::A1033Charmander,
                CardId::A1094Pikachu,
            ],
            &[
                CardId::A1001Bulbasaur,
                CardId::B3077Regirock,
                CardId::B3045Regice,
                CardId::B3116Registeel,
            ],
        ),
        "only your own Bench satisfies Seal of Antiquity"
    );
}

/// Alolan Muk (B2 097) "Power of Alchemy": "Basic Pokémon in play (both yours and your opponent's)
/// have no Abilities." Regigigas is a Basic, so its own Seal of Antiquity is switched off — the
/// deliberate combo that lets Regigigas attack without the three Regis on the Bench.
#[test]
fn test_power_of_alchemy_unseals_regigigas() {
    let incomplete_bench = [
        CardId::B3077Regirock,
        CardId::B3045Regice,
        CardId::A1001Bulbasaur,
    ];
    assert!(
        !regigigas_can_attack(incomplete_bench),
        "baseline: without Alolan Muk the missing Registeel must still seal Giga Turbo"
    );

    assert!(
        regigigas_can_attack([
            CardId::B3077Regirock,
            CardId::B3045Regice,
            CardId::B2097AlolanMuk,
        ]),
        "Power of Alchemy switches off Seal of Antiquity, so Regigigas can attack anyway"
    );
}

/// Power of Alchemy is symmetric, so the *opponent's* Alolan Muk unseals your Regigigas too.
#[test]
fn test_opponents_power_of_alchemy_unseals_regigigas() {
    assert!(
        regigigas_can_attack_against(
            [
                CardId::A1001Bulbasaur,
                CardId::A1033Charmander,
                CardId::A1094Pikachu,
            ],
            &[CardId::A1001Bulbasaur, CardId::B2097AlolanMuk],
        ),
        "an opponent's Alolan Muk suppresses your Basics' Abilities as well, freeing Regigigas"
    );
}

/// The other half of Ability suppression: Budew's Prickly Powder applies `CardEffect::NoAbilities`
/// to the Defending Pokémon, which must lift the seal on a Defending Regigigas just the same.
fn regigigas_can_attack_after_prickly_powder(apply_prickly_powder: bool) -> bool {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3013Budew)],
        vec![
            powered_regigigas(),
            PlayedCard::from_id(CardId::B3077Regirock),
            PlayedCard::from_id(CardId::B3045Regice),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );

    if apply_prickly_powder {
        game.apply_action(&Action {
            actor: 0,
            action: attack_action(CardId::B3013Budew, 0),
            is_stack: false,
        });
    }

    end_turn(&mut game, 0);

    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1);
    choices
        .iter()
        .any(|choice| matches!(choice.action, SimpleAction::Attack(_)))
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

#[test]
fn test_prickly_powder_unseals_regigigas() {
    assert!(
        !regigigas_can_attack_after_prickly_powder(false),
        "baseline: with Registeel missing, Regigigas cannot attack"
    );
    assert!(
        regigigas_can_attack_after_prickly_powder(true),
        "losing all Abilities to Prickly Powder also loses Seal of Antiquity"
    );
}
