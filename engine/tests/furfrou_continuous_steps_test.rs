use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Attack, Card, EnergyType, PlayedCard, TrainerCard},
    test_support::get_initialized_game_with_board,
    Game,
};

fn continuous_steps() -> Attack {
    match get_card_by_enum(CardId::B4a064Furfrou) {
        Card::Pokemon(card) => card.attacks[0].clone(),
        _ => panic!("Furfrou must be a Pokemon"),
    }
}

fn copied_continuous_steps() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Attack(continuous_steps()),
        is_stack: true,
    }
}

fn keep() -> Action {
    Action {
        actor: 0,
        action: SimpleAction::KeepAttackCoinResults,
        is_stack: true,
    }
}

fn reroll(source: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::RerollAttackCoins {
            victory_star_in_play_idx: source,
        },
        is_stack: true,
    }
}

fn trainer(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(card) => card,
        _ => panic!("expected Trainer card"),
    }
}

fn game(seed: u64, defender_hp: u32) -> Game<'static> {
    let fire_attacker =
        PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Colorless]);
    let victini = PlayedCard::from_id(CardId::B3025Victini);
    let defender = PlayedCard::new(
        get_card_by_enum(CardId::PB024MegaLatiosEx),
        0,
        defender_hp,
        vec![],
        false,
        vec![],
    );
    get_initialized_game_with_board(seed, 0, 3, vec![fire_attacker, victini], vec![defender])
}

#[test]
fn victory_star_samples_real_unbounded_batch_then_commits_continuous_steps_once() {
    let mut found_long_tail = false;
    for seed in 0..128 {
        let mut game = game(seed, 70);
        game.apply_action(&copied_continuous_steps());
        let paused = game.get_state_clone();
        let pending = paused
            .pending_attack_coin_choice
            .as_ref()
            .expect("a Fire Pokemon's copied Continuous Steps should pause for Victory Star");
        assert_eq!(paused.get_active(1).get_remaining_hp(), 70);
        assert_eq!(pending.flips.last(), Some(&false));
        let heads = pending.flips.iter().filter(|face| **face).count();
        if heads > 3 {
            found_long_tail = true;
            game.apply_action(&keep());
            let committed = game.get_state_clone();
            assert!(committed.pending_attack_coin_choice.is_none());
            assert!(committed.in_play_pokemon[1][0].is_none());
            break;
        }
    }
    assert!(
        found_long_tail,
        "symbolic saturation must sample concrete batches beyond its 3-head boundary"
    );
}

#[test]
fn will_forces_only_the_first_continuous_steps_batch_before_victini_reroll() {
    let mut saw_immediate_tails_replacement = false;
    for seed in 0..256 {
        let mut game = game(seed, 200);
        let will = trainer(CardId::A4156Will);
        let mut state = game.get_state_clone();
        state.hands[0].push(Card::Trainer(will.clone()));
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Play { trainer_card: will },
            is_stack: false,
        });
        game.apply_action(&copied_continuous_steps());
        let pending = game
            .get_state_clone()
            .pending_attack_coin_choice
            .expect("Victory Star should pause the Will-forced batch");
        assert_eq!(pending.flips.first(), Some(&true));
        game.apply_action(&reroll(pending.victory_star_in_play_idx));
        saw_immediate_tails_replacement |=
            game.get_state_clone().get_active(1).get_remaining_hp() == 200;
        if saw_immediate_tails_replacement {
            break;
        }
    }
    assert!(
        saw_immediate_tails_replacement,
        "Will must be consumed by the first batch so a Victory Star replacement can start tails"
    );
}
