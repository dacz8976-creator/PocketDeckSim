//! The Ultra Beast list (`ULTRA_BEAST_NAMES` in hooks/core.rs) decides what Lusamine, Celesteela's
//! Ultra Thrusters, Beast Wall and Beastite accept. Non-ex Buzzwole (B2 014, B2 159) carries the
//! Ultra Beast tag but was missing from the list, so Lusamine and Ultra Thrusters refused it.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, TrainerCard},
    test_support::get_test_game_with_board,
    Game,
};

fn lusamine() -> TrainerCard {
    get_card_by_enum(CardId::A3a069Lusamine).as_trainer()
}

/// Player 0 to act on turn 3 with `board` in play (the first card Active), Lusamine in hand, two
/// Grass Energy in the discard pile, and the opponent on 1 point (Lusamine's play condition).
fn lusamine_game(board: Vec<PlayedCard>) -> Game<'static> {
    let mut game =
        get_test_game_with_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![Card::Trainer(lusamine())];
    state.discard_energies[0] = vec![EnergyType::Grass, EnergyType::Grass];
    state.points[1] = 1;
    game.set_state(state);
    game
}

fn can_play_lusamine(game: &Game) -> bool {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions.iter().any(|a| {
        matches!(
            &a.action,
            SimpleAction::Play { trainer_card } if trainer_card.name == "Lusamine"
        )
    })
}

fn play_lusamine(game: &mut Game) -> Vec<Action> {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: lusamine(),
        },
        is_stack: false,
    });
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "Lusamine's choice belongs to the player who played it");
    actions
}

/// Lusamine (A3a 069): "Choose 1 of your Ultra Beasts. Attach 2 random Energy from your discard
/// pile to that Pokémon." An Active non-ex Buzzwole must be offered and get both Energy.
#[test]
fn test_lusamine_attaches_to_active_non_ex_buzzwole() {
    let mut game = lusamine_game(vec![PlayedCard::from_id(CardId::B2014Buzzwole)]);
    assert!(
        can_play_lusamine(&game),
        "Buzzwole (B2 014) is an Ultra Beast, so Lusamine must be playable"
    );
    let actions = play_lusamine(&mut game);
    let attach = actions
        .iter()
        .find(|a| {
            matches!(
                a.action,
                SimpleAction::AttachFromDiscard {
                    in_play_idx: 0,
                    num_random_energies: 2
                }
            )
        })
        .unwrap_or_else(|| panic!("Lusamine should offer the Active Buzzwole, got {actions:?}"))
        .clone();
    game.apply_action(&attach);

    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert_eq!(active.get_name(), "Buzzwole");
    assert_eq!(
        active.attached_energy,
        vec![EnergyType::Grass, EnergyType::Grass]
    );
}

#[test]
fn test_lusamine_accepts_both_non_ex_buzzwole_printings() {
    for id in [CardId::B2014Buzzwole, CardId::B2159Buzzwole] {
        let game = lusamine_game(vec![PlayedCard::from_id(id)]);
        assert!(
            can_play_lusamine(&game),
            "{id:?} is an Ultra Beast, so Lusamine must be playable"
        );
    }
}

/// Celesteela (A3a 062), Ultra Thrusters: "Once during your turn, you may switch your Active Ultra
/// Beast with 1 of your Benched Ultra Beasts." Buzzwole Active, Celesteela on the Bench.
#[test]
fn test_ultra_thrusters_switches_an_active_non_ex_buzzwole() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2014Buzzwole),
            PlayedCard::from_id(CardId::A3a062Celesteela),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let use_ability = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::UseAbility { in_play_idx: 1 }))
        .unwrap_or_else(|| panic!("Ultra Thrusters should be usable, got {actions:?}"))
        .clone();
    game.apply_action(&use_ability);
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let activate = actions
        .iter()
        .find(|a| {
            matches!(
                a.action,
                SimpleAction::Activate {
                    player: 0,
                    in_play_idx: 1
                }
            )
        })
        .unwrap_or_else(|| panic!("Celesteela should be offered, got {actions:?}"))
        .clone();
    game.apply_action(&activate);

    assert_eq!(
        game.get_state_clone().get_active(0).get_name(),
        "Celesteela"
    );
}

/// The same ability with Celesteela Active and Buzzwole the Benched Ultra Beast.
#[test]
fn test_ultra_thrusters_brings_up_a_benched_non_ex_buzzwole() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A3a062Celesteela),
            PlayedCard::from_id(CardId::B2159Buzzwole),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let use_ability = actions
        .iter()
        .find(|a| matches!(a.action, SimpleAction::UseAbility { in_play_idx: 0 }))
        .unwrap_or_else(|| panic!("Ultra Thrusters should be usable, got {actions:?}"))
        .clone();
    game.apply_action(&use_ability);
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    let activate = actions
        .iter()
        .find(|a| {
            matches!(
                a.action,
                SimpleAction::Activate {
                    player: 0,
                    in_play_idx: 1
                }
            )
        })
        .unwrap_or_else(|| panic!("the Benched Buzzwole should be offered, got {actions:?}"))
        .clone();
    game.apply_action(&activate);

    assert_eq!(game.get_state_clone().get_active(0).get_name(), "Buzzwole");
}

/// Negative cases: a Pokémon without the Ultra Beast tag is still refused. Necrozma (A3 088) has
/// no tag, unlike its Dawn Wings, Dusk Mane and Ultra forms.
#[test]
fn test_non_ultra_beasts_are_still_refused() {
    for id in [CardId::A1001Bulbasaur, CardId::A3088Necrozma] {
        let game = lusamine_game(vec![PlayedCard::from_id(id)]);
        assert!(
            !can_play_lusamine(&game),
            "{id:?} is not an Ultra Beast, so Lusamine must not be playable"
        );
    }

    // Lusamine with a non-Ultra Beast Active and Buzzwole on the Bench offers only Buzzwole.
    let mut game = lusamine_game(vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::B2014Buzzwole),
    ]);
    let actions = play_lusamine(&mut game);
    let targets: Vec<usize> = actions
        .iter()
        .filter_map(|a| match a.action {
            SimpleAction::AttachFromDiscard { in_play_idx, .. } => Some(in_play_idx),
            _ => None,
        })
        .collect();
    assert_eq!(targets, vec![1], "only the Benched Buzzwole is an Ultra Beast");

    // Ultra Thrusters needs an Active Ultra Beast: with Bulbasaur Active it is not offered.
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A3a062Celesteela),
            PlayedCard::from_id(CardId::B2014Buzzwole),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        !actions
            .iter()
            .any(|a| matches!(a.action, SimpleAction::UseAbility { in_play_idx: 1 })),
        "Ultra Thrusters must not be offered with a non-Ultra Beast Active"
    );
}

/// Every printing that carries the Ultra Beast tag, as Serebii's Ultra Beast list shows it
/// (read Oct 26: 50 printings, all in our card data; no other printing shares their names).
/// The card data has no tag field, so this list is the record of the printed tag.
const TAGGED_ULTRA_BEASTS: [CardId; 50] = [
    CardId::A3a006BuzzwoleEx,
    CardId::A3a007Pheromosa,
    CardId::A3a008Kartana,
    CardId::A3a009Blacephalon,
    CardId::A3a020Xurkitree,
    CardId::A3a042Nihilego,
    CardId::A3a043GuzzlordEx,
    CardId::A3a044Poipole,
    CardId::A3a045Naganadel,
    CardId::A3a053Stakataka,
    CardId::A3a062Celesteela,
    CardId::A3a071Pheromosa,
    CardId::A3a072Blacephalon,
    CardId::A3a075Celesteela,
    CardId::A3a076BuzzwoleEx,
    CardId::A3a079GuzzlordEx,
    CardId::A3a086GuzzlordEx,
    CardId::A3a088BuzzwoleEx,
    CardId::A3a103Nihilego,
    CardId::A4b044BuzzwoleEx,
    CardId::A4b045Pheromosa,
    CardId::A4b046Pheromosa,
    CardId::A4b047Kartana,
    CardId::A4b048Kartana,
    CardId::A4b246Nihilego,
    CardId::A4b247Nihilego,
    CardId::A4b248GuzzlordEx,
    CardId::A4b304Celesteela,
    CardId::A4b305Celesteela,
    CardId::A4b360BuzzwoleEx,
    CardId::PA075Kartana,
    CardId::PA076Blacephalon,
    CardId::PA077Xurkitree,
    CardId::PA078DawnWingsNecrozma,
    CardId::PA079DuskManeNecrozma,
    CardId::PA080Stakataka,
    CardId::PA081UltraNecrozmaEx,
    CardId::PA082Poipole,
    CardId::B1a098BuzzwoleEx,
    CardId::B1a100GuzzlordEx,
    CardId::B2014Buzzwole,
    CardId::B2023BlacephalonEx,
    CardId::B2109Guzzlord,
    CardId::B2159Buzzwole,
    CardId::B2181BlacephalonEx,
    CardId::B2195BlacephalonEx,
    CardId::B2b048Kartana,
    CardId::B4016Pheromosa,
    CardId::B4224BlacephalonEx,
    CardId::B4b045BlacephalonEx,
];

/// Blacephalon ex, Guzzlord and Ultra Necrozma ex were missing too (the list named "Ultra
/// Necrozma", which no card is called), so Lusamine refused them.
#[test]
fn test_lusamine_accepts_every_tagged_ultra_beast_printing() {
    for id in TAGGED_ULTRA_BEASTS {
        let game = lusamine_game(vec![PlayedCard::from_id(id)]);
        assert!(
            can_play_lusamine(&game),
            "{id:?} carries the Ultra Beast tag, so Lusamine must be playable"
        );
    }
}
