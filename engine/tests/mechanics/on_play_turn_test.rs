// Ported from upstream deckgym-core #385 (tests/regressions/on_play_turn_test.rs), adapted to this fork.
//
// Legendary Drive (Miraidon ex) and Ancient Roar (Roaring Moon) read "Once during your turn, when
// you put this Pokémon from your hand onto your Bench". Setup comes before any turn, and a player
// whose Pokémon is benched during the other player's turn (Team Rocket's Boss) never gets them.
// The fork's guard is in engine/src/hooks/core.rs `on_bench_from_hand`.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, PlayedCard, TrainerCard},
    test_support::get_test_game_with_board,
    Game, State,
};

fn place_on_bench(card: CardId, turn: u8, actor: usize) -> State {
    let mut state = State::default();
    state.turn_count = turn;
    state.current_player = 0;
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B1a024Magnemite),
            PlayedCard::from_id(CardId::B1a024Magnemite),
        ],
        vec![
            PlayedCard::from_id(CardId::A4032Magby),
            PlayedCard::from_id(CardId::A4032Magby),
        ],
    );
    let card = get_card_by_enum(card);
    state.hands[actor] = vec![card.clone()];
    let mut game = Game::from_state(state, vec![], 42);
    game.apply_action(&Action {
        actor,
        action: SimpleAction::Place(card, 2),
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn on_play_abilities_do_not_create_setup_or_opponent_turn_prompts() {
    for card in [CardId::B3a019MiraidonEx, CardId::B3a047RoaringMoon] {
        for actor in 0..2 {
            let state = place_on_bench(card, 0, actor);
            assert!(
                state.move_generation_stack.is_empty(),
                "setup must not trigger on-play abilities"
            );
        }
        let state = place_on_bench(card, 1, 1);
        assert!(
            state.move_generation_stack.is_empty(),
            "ability requires the owner's turn"
        );
    }
}

#[test]
fn on_play_abilities_still_offer_the_correct_owner_choice_during_their_turn() {
    for card in [CardId::B3a019MiraidonEx, CardId::B3a047RoaringMoon] {
        let state = place_on_bench(card, 1, 0);
        assert_eq!(
            state.move_generation_stack,
            vec![(
                0,
                vec![
                    SimpleAction::UseAbility { in_play_idx: 2 },
                    SimpleAction::Noop
                ]
            )]
        );
    }
}

// Not in upstream's file: the fork's own case for the third branch of the guard. Team Rocket's
// Boss ("put any number of Basic Pokémon you find there onto your opponent's Bench") puts the
// opponent's Miraidon ex / Roaring Moon from THEIR hand onto THEIR Bench during OUR turn, so the
// opponent must not be offered Legendary Drive or Ancient Roar.
fn trainer(card_id: CardId) -> TrainerCard {
    let Card::Trainer(card) = get_card_by_enum(card_id) else {
        panic!("expected a Trainer card");
    };
    card
}

#[test]
fn team_rockets_boss_benching_the_opponents_on_play_pokemon_queues_no_ability() {
    for card_id in [CardId::B3a019MiraidonEx, CardId::B3a047RoaringMoon] {
        let card = get_card_by_enum(card_id);
        let boss = trainer(CardId::B4a071TeamRocketsBoss);
        // Both players have an Active and one Benched Pokémon, so each Ability would have
        // something to do (an Active to switch with, a Bench to switch the opponent's Active to).
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::B1a024Magnemite),
                PlayedCard::from_id(CardId::B1a024Magnemite),
            ],
            vec![
                PlayedCard::from_id(CardId::A4032Magby),
                PlayedCard::from_id(CardId::A4032Magby),
            ],
        );
        let mut state = game.get_state_clone();
        state.current_player = 0;
        state.hands[0] = vec![Card::Trainer(boss.clone())];
        state.hands[1] = vec![card.clone()];
        game.set_state(state);

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card: boss },
            is_stack: false,
        });
        let (_actor, choices) = game.get_state_clone().generate_possible_actions();
        let bench_it = choices
            .into_iter()
            .find(|choice| {
                matches!(
                    &choice.action,
                    SimpleAction::BenchOpponentHandBasics { cards } if *cards == vec![card.clone()]
                )
            })
            .expect("Team Rocket's Boss should offer to bench the opponent's Basic");
        game.apply_action(&bench_it);

        let state = game.get_state_clone();
        assert_eq!(
            state.in_play_pokemon[1][2]
                .as_ref()
                .map(|pokemon| pokemon.card.clone()),
            Some(card.clone()),
            "Team Rocket's Boss should put the card onto the opponent's first free Bench spot"
        );
        assert!(
            state.move_generation_stack.is_empty(),
            "{} was benched on its owner's opponent's turn, so its Ability must not be offered",
            card.get_name()
        );
    }
}
