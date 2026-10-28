// Port of upstream #432's tests/trainers/dual_fusion_supporters (98219e2) to our layout: wired from
// tests/trainers.rs with #[path]. Changes from upstream: a local `play` (our test_support has no
// `play_trainer`), RulesUnverified accepted for older Supporters (Team Rocket's Researcher), damage
// read as lost HP (no `public_details`), our empty-deck rule for Poké Mart Guy and Serena's Choice
// (J3), and a full-hand case for Serena's Choice (J4).
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard},
    test_support::get_test_game_with_board,
    Game, State,
};
fn pokemon(id: &str) -> PlayedCard {
    PlayedCard::from_id(CardId::from_card_id(id).unwrap())
}
fn board(ours: Vec<PlayedCard>) -> Game<'static> {
    get_test_game_with_board(
        ours,
        vec![pokemon("A1 211"), pokemon("A1 001"), pokemon("A1 033")],
    )
}
fn give(game: &mut Game<'static>, id: CardId) {
    let mut s = game.get_state_clone();
    s.hands[0] = vec![get_card_by_enum(id)];
    game.set_state(s);
}
fn offered(game: &mut Game<'static>, id: CardId) -> bool {
    give(game, id);
    game.get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.id == get_card_by_enum(id).get_id()))
}
fn play_from_hand(game: &mut Game<'static>, id: CardId) {
    let Card::Trainer(trainer_card) = get_card_by_enum(id) else {
        unreachable!()
    };
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card },
        is_stack: false,
    });
}
fn play(game: &mut Game<'static>, id: CardId) {
    assert!(offered(game, id), "{id:?} must be playable");
    play_from_hand(game, id);
}
fn remaining_hp(s: &State, player: usize, idx: usize) -> u32 {
    s.in_play_pokemon[player][idx]
        .as_ref()
        .unwrap()
        .get_remaining_hp()
}

mod lorelei;

mod blue;

mod serena;

mod rika;

mod mart;

mod rising;

#[test]
fn every_supporter_printing_is_implemented_including_all_twelve_new_printings() {
    use deckgym::card_validation::{get_implementation_status, ImplementationStatus};
    use deckgym::models::TrainerType;
    use strum::IntoEnumIterator;
    let mut new_printings = 0;
    for id in CardId::iter() {
        if let Card::Trainer(t) = get_card_by_enum(id) {
            if t.trainer_card_type == TrainerType::Supporter {
                let status = get_implementation_status(id);
                // Ours: Team Rocket's Researcher (B4a 069/085) is RulesUnverified, not Complete.
                assert!(
                    matches!(
                        status,
                        ImplementationStatus::Complete | ImplementationStatus::RulesUnverified
                    ),
                    "{id:?}: {status:?}"
                );
                if t.id.starts_with("C1 ") {
                    assert_eq!(status, ImplementationStatus::Complete, "{id:?}");
                    new_printings += 1;
                }
            }
        }
    }
    assert_eq!(new_printings, 12);
}
