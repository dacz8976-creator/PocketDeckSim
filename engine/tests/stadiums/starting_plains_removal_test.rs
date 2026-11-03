//! Starting Plains (B2 154; reprints B4b 235 and B4b 401): "Each Basic Pokémon in play (both yours
//! and your opponent's) gets +20 HP." Four cards take it out of play, and the +20 leaves with it at
//! once, from every Basic in play on both sides (a Stage 1 or Stage 2 Pokémon never had it):
//! - Machop's Shatter (B2 079) and Conkeldurr's Bedrock Breaker (B4 089): "Discard a Stadium in
//!   play." (any Stadium, its own player's too; the only two printings with that text);
//! - Palkia's Spacial Rend (C1 038 / C1 140): "If your opponent has a Stadium in play, discard it."
//!   (only a Stadium the opponent put into play);
//! - Field Blower (B3 147; reprints B4b 202 and B4b 368), an Item: "Discard a Pokémon Tool card
//!   from a Pokémon (yours or your opponent's), or discard a Stadium card in play."
//!
//! A Pokémon whose damage reaches its HP without the +20 is Knocked Out at once. How that Knock
//! Out is scored is the engine's existing reading, not verified against the real game, and every
//! test here that asserts one, its points, its promotion or a win from it says so. Whichever check
//! scores it, the point goes to the owner's opponent (rules/02 §6), and the owner promotes if it
//! was the Active Pokémon.
//!
//! After one of the three attacks (each refreshes the HP bonuses inside its own effect) the engine
//! scores it as the attack's own Knock Out, in the attack's own Knock Out check: when both Active
//! Pokémon go, the attacker promotes first, as after any double Knock Out in an attack (rules/02
//! §7), where the catch-all check after the action would go by seat (player 0 first). A Pokémon of
//! the opponent's Knocked Out this way sets the flag Marshadow's Revenge reads during the next turn
//! ("If any of your Pokémon were Knocked Out by damage from an attack during your opponent's last
//! turn"), even a Benched one the attack did no damage to. Whether a Knock Out from the lost +20 is
//! an attack's Knock Out at all is the open question for Dustin after R8 (the Revenge flag, Rescue
//! Scarf and Iris's extra point all depend on it): read plainly, Revenge's text and rules/04
//! (Poison and Ability Knock Outs don't count for Revenge) make it doubtful, most of all for a
//! Pokémon the attack did not damage.
//!
//! After Field Blower it is the catch-all Knock Out check that follows the Item, and the turn goes
//! on. The labels stay on those tests too, but nothing there is open: the points at once, the
//! promotion, the win and the turn going on match Dustin's ruling on Knock Outs from removing an
//! HP bonus outside an attack (rules/02 §7-§8 and the settled list in rules/05: [DUSTIN], with an
//! Ability Knock Out filmed in 025604), and with no attack there is no Knock Out by an attack.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::{attack_action, get_test_game_with_board, trainer_from_id},
    Game, State,
};

const PLAINS: [CardId; 3] = [
    CardId::B2154StartingPlains,
    CardId::B4b235StartingPlains,
    CardId::B4b401StartingPlains,
];
const PALKIAS: [CardId; 2] = [CardId::C1038Palkia, CardId::C1140Palkia];
const FIELD_BLOWERS: [CardId; 3] = [
    CardId::B3147FieldBlower,
    CardId::B4b202FieldBlower,
    CardId::B4b368FieldBlower,
];

fn bulbasaur() -> PlayedCard {
    // 70 HP, Basic.
    PlayedCard::from_id(CardId::A1001Bulbasaur)
}

fn squirtle() -> PlayedCard {
    // 60 HP, Basic.
    PlayedCard::from_id(CardId::A1053Squirtle)
}

fn seel() -> PlayedCard {
    // 70 HP, Basic.
    PlayedCard::from_id(CardId::C1032Seel)
}

fn snorlax() -> PlayedCard {
    // 150 HP, Basic.
    PlayedCard::from_id(CardId::A1211Snorlax)
}

fn ivysaur() -> PlayedCard {
    // 90 HP, Stage 1: Starting Plains never gives it the +20.
    PlayedCard::from_id(CardId::A1002Ivysaur)
}

fn machop() -> PlayedCard {
    // 70 HP, Basic. Shatter: [C], 10 damage.
    PlayedCard::from_id(CardId::B2079Machop).with_energy(vec![EnergyType::Colorless])
}

fn conkeldurr() -> PlayedCard {
    // 150 HP, Stage 2. Bedrock Breaker: [F][F][C], 100 damage.
    PlayedCard::from_id(CardId::B4089Conkeldurr).with_energy(vec![
        EnergyType::Fighting,
        EnergyType::Fighting,
        EnergyType::Colorless,
    ])
}

fn palkia(printing: CardId) -> PlayedCard {
    // 120 HP, Basic. Spacial Rend: [W][W][C], 70 damage.
    PlayedCard::from_id(printing).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Colorless,
    ])
}

/// Player 0's `own` Pokémon against player 1's `opponent` (the game of seed 0, turn 3), after
/// `stadium_player` has played `plains` from their hand, so every Basic in play has its +20. It is
/// player 0's turn when this returns.
fn after_plains_played_by(
    stadium_player: usize,
    plains: CardId,
    own: Vec<PlayedCard>,
    opponent: Vec<PlayedCard>,
) -> Game<'static> {
    let mut game = get_test_game_with_board(own, opponent);
    let mut state = game.get_state_clone();
    state.current_player = stadium_player;
    state.hands[stadium_player] = vec![get_card_by_enum(plains)];
    game.set_state(state);
    game.apply_action(&Action {
        actor: stadium_player,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(plains),
        },
        is_stack: false,
    });
    let mut state = game.get_state_clone();
    assert_eq!(state.active_stadium, Some(get_card_by_enum(plains)));
    assert_eq!(state.active_stadium_owner, Some(stadium_player));
    state.current_player = 0;
    game.set_state(state);
    game
}

fn set_points(game: &mut Game<'static>, points: [u8; 2]) {
    let mut state = game.get_state_clone();
    state.points = points;
    game.set_state(state);
}

/// `action` as offered to `actor` on the current board: it must be a legal move there.
fn offered(game: &Game<'static>, actor: usize, action: SimpleAction) -> Action {
    let (to_act, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(to_act, actor, "{action:?}");
    actions
        .into_iter()
        .find(|choice| choice.action == action)
        .unwrap_or_else(|| panic!("{action:?} should be offered to player {actor}"))
}

/// Player 0's Active Pokémon `attacker` uses its first attack.
fn attack(game: &mut Game<'static>, attacker: CardId) {
    let attack = offered(game, 0, attack_action(attacker, 0));
    game.apply_action(&attack);
}

/// Player 1's Active Pokémon `attacker` uses its first attack, on a turn of player 1's.
fn attack_as_player_1(game: &mut Game<'static>, attacker: CardId) {
    let mut state = game.get_state_clone();
    state.current_player = 1;
    game.set_state(state);
    let attack = offered(game, 1, attack_action(attacker, 0));
    game.apply_action(&attack);
}

/// Player 0 plays `blower` from their hand and takes its one choice: no Pokémon here has a Tool,
/// so the Stadium in play is the only card it can discard.
fn field_blower_the_stadium(game: &mut Game<'static>, blower: CardId) {
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(blower)];
    game.set_state(state);
    let play = offered(
        game,
        0,
        SimpleAction::Play {
            trainer_card: trainer_from_id(blower),
        },
    );
    game.apply_action(&play);
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "{blower:?}");
    assert_eq!(choices.len(), 1, "{blower:?}: {choices:?}");
    assert!(
        matches!(choices[0].action, SimpleAction::DiscardActiveStadium),
        "{blower:?}: {choices:?}"
    );
    game.apply_action(&choices[0]);
}

/// The Bench slots `player` is asked to promote from, when that is the only thing on offer.
fn promotion_choices(game: &Game<'static>, player: usize) -> Vec<usize> {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, player);
    let mut slots: Vec<usize> = choices
        .iter()
        .map(|choice| match choice.action {
            SimpleAction::Promote {
                player: promoting,
                in_play_idx,
            } if promoting == player => in_play_idx,
            ref other => panic!("expected a promotion for player {player}, got {other:?}"),
        })
        .collect();
    slots.sort();
    slots
}

fn promote(game: &mut Game<'static>, player: usize, slot: usize) {
    let promotion = offered(
        game,
        player,
        SimpleAction::Promote {
            player,
            in_play_idx: slot,
        },
    );
    game.apply_action(&promotion);
}

/// Player 0 ends the turn (the Pokémon Checkup runs inside it); returns the state at the start of
/// player 1's turn.
fn end_turn(game: &mut Game<'static>) -> State {
    let end_turn = offered(game, 0, SimpleAction::EndTurn);
    game.apply_action(&end_turn);
    let state = game.get_state_clone();
    assert_eq!(state.current_player, 1);
    state
}

fn remaining(state: &State, player: usize, slots: &[usize]) -> Vec<u32> {
    slots
        .iter()
        .map(|&idx| state.get_remaining_hp(player, idx))
        .collect()
}

fn knocked_out(state: &State, player: usize, slots: &[usize]) -> bool {
    slots
        .iter()
        .all(|&idx| state.in_play_pokemon[player][idx].is_none())
}

// Machop's Shatter (B2 079): 10 damage. "Discard a Stadium in play."

/// The opponent's Starting Plains goes to its owner's discard pile, and the +20 leaves every Basic
/// in play on both sides at once: Machop 90 → 70 and the attacker's Squirtle (30 damage) 50 → 30;
/// the opponent's Bulbasaur 90 - 10 → 60 and Seel (50 damage) 40 → 20. Neither Ivysaur (Stage 1)
/// ever had it: 90 before and after. Each printing of Starting Plains.
#[test]
fn shatter_takes_the_plus_20_off_every_basic_in_play_and_leaves_the_stage_1s_alone() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![machop(), squirtle().with_damage(30), ivysaur()],
            vec![bulbasaur(), seel().with_damage(50), ivysaur()],
        );
        let state = game.get_state_clone();
        assert_eq!(remaining(&state, 0, &[0, 1, 2]), vec![90, 50, 90], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1, 2]), vec![90, 40, 90], "{plains:?}");

        attack(&mut game, CardId::B2079Machop);
        let state = game.get_state_clone();
        assert!(
            state.active_stadium.is_none() && state.active_stadium_owner.is_none(),
            "{plains:?}"
        );
        assert_eq!(state.discard_piles[1], vec![get_card_by_enum(plains)], "{plains:?}");
        assert_eq!(remaining(&state, 0, &[0, 1, 2]), vec![70, 30, 90], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1, 2]), vec![60, 20, 90], "{plains:?}");
        assert_eq!(state.points, [0, 0], "{plains:?}");
    }
}

/// Shatter against the opponent's Starting Plains: their Bulbasaur (60 damage, 30 left) takes the
/// 10 and is at 20, then its 70 damage is its printed 70 HP; their Benched Squirtle has 70 damage on
/// 60 HP (10 left with the +20). Both are Knocked Out at once: 2 points, and the opponent promotes
/// Seel (50 damage, now 20) or Ivysaur (90). The attacker's Machop and Bulbasaur are at 70.
/// The Knock Outs are the existing reading, not verified: the attack's own, scored by the attack's
/// own Knock Out check, so at the start of the opponent's turn the engine counts their Pokémon as
/// Knocked Out by damage from an attack during the last turn (the flag Marshadow's Revenge reads),
/// though the Benched Squirtle took no damage from Shatter: doubtful, see the module doc.
#[test]
fn shatter_knocks_out_the_opponents_damaged_basics_at_once_as_the_attacks_knock_outs() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![machop(), bulbasaur()],
            vec![
                bulbasaur().with_damage(60),
                squirtle().with_damage(70),
                seel().with_damage(50),
                ivysaur(),
            ],
        );
        attack(&mut game, CardId::B2079Machop);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none(), "{plains:?}");
        assert!(state.discard_piles[1].contains(&get_card_by_enum(plains)), "{plains:?}");
        assert!(knocked_out(&state, 1, &[0, 1]), "{plains:?}: Bulbasaur and Squirtle");
        assert_eq!(remaining(&state, 1, &[2, 3]), vec![20, 90], "{plains:?}");
        assert_eq!(remaining(&state, 0, &[0, 1]), vec![70, 70], "{plains:?}");
        assert_eq!(state.points, [2, 0], "{plains:?}: both points at once");
        assert_eq!(state.winner, None, "{plains:?}");
        assert_eq!(promotion_choices(&game, 1), vec![2, 3], "{plains:?}");

        promote(&mut game, 1, 2);
        let state = end_turn(&mut game);
        assert!(
            state.get_knocked_out_by_opponent_attack_last_turn(),
            "{plains:?}: Knocked Out by the attack"
        );
    }
}

/// Shatter discards a Stadium its own player put into play just the same, and the +20 leaves the
/// attacker's side too: Machop itself (70 damage, 20 left) and the Benched Squirtle (60 damage on 60
/// HP) are Knocked Out at once, the opponent scores both, and Machop's player promotes Bulbasaur (30
/// damage, 60 → 40). The opponent's Ivysaur takes the 10 (90 → 80) and Seel loses the +20 (90 → 70).
/// The Knock Outs are the existing reading, not verified: scored by the attack's own Knock Out
/// check (the double Knock Out test from player 1's seat below pins it), and not Knock Outs by the
/// opponent's attack.
#[test]
fn shatter_knocks_out_machop_itself_and_its_own_damaged_benched_basic() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            0,
            plains,
            vec![
                machop().with_damage(70),
                squirtle().with_damage(60),
                bulbasaur().with_damage(30),
            ],
            vec![ivysaur(), seel()],
        );
        attack(&mut game, CardId::B2079Machop);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none(), "{plains:?}");
        assert!(state.discard_piles[0].contains(&get_card_by_enum(plains)), "{plains:?}");
        assert!(knocked_out(&state, 0, &[0, 1]), "{plains:?}: Machop and Squirtle");
        assert_eq!(remaining(&state, 0, &[2]), vec![40], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1]), vec![80, 70], "{plains:?}");
        assert_eq!(state.points, [0, 2], "{plains:?}: the opponent scores both");
        assert_eq!(state.winner, None, "{plains:?}");
        assert_eq!(promotion_choices(&game, 0), vec![2], "{plains:?}");

        promote(&mut game, 0, 2);
        let state = end_turn(&mut game);
        assert!(!state.get_knocked_out_by_opponent_attack_last_turn(), "{plains:?}");
    }
}

/// When Machop's own Knock Out is the opponent's third point, the opponent wins at once, though
/// Machop's player still has a Pokémon in play. The win is the existing reading, not verified.
#[test]
fn shatter_that_knocks_out_machop_itself_can_give_the_opponent_the_game() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            0,
            plains,
            vec![machop().with_damage(70), bulbasaur()],
            vec![ivysaur()],
        );
        set_points(&mut game, [0, 2]);
        attack(&mut game, CardId::B2079Machop);
        let state = game.get_state_clone();
        assert!(knocked_out(&state, 0, &[0]), "{plains:?}");
        assert_eq!(state.get_remaining_hp(1, 0), 80, "{plains:?}");
        assert_eq!(state.points, [0, 3], "{plains:?}");
        assert_eq!(state.winner, Some(GameOutcome::Win(1)), "{plains:?}");
    }
}

/// Shatter from player 1's seat knocks out both Active Pokémon with the lost +20 alone: player 0's
/// Bulbasaur (60 damage) takes the 10 and is at 20, then its 70 damage is its printed 70 HP, and
/// Machop's own 70 damage is its printed 70 HP once its player's Starting Plains goes. One point
/// each; player 0's Seel 90 → 70, player 1's Benched Squirtle 80 → 60.
/// The Knock Outs and the order of the promotions are the existing reading, not verified: both are
/// the attack's own, scored together by the attack's own Knock Out check, so Machop's player
/// promotes first, as after any double Knock Out in an attack (rules/02 §7). The catch-all check
/// after the action goes by seat and would ask player 0 first, so only an attacker in player 1's
/// seat tells the two checks apart. A Knock Out by the attack's damage would not either: the
/// discard that follows it refreshes the HP bonuses and pulls the lost +20's Knock Outs into the
/// attack's check.
#[test]
fn shatter_from_player_1s_seat_that_knocks_out_both_actives_lets_player_1_promote_first() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![bulbasaur().with_damage(60), seel()],
            vec![machop().with_damage(70), squirtle()],
        );
        attack_as_player_1(&mut game, CardId::B2079Machop);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none(), "{plains:?}");
        assert!(state.discard_piles[1].contains(&get_card_by_enum(plains)), "{plains:?}");
        assert!(
            knocked_out(&state, 0, &[0]) && knocked_out(&state, 1, &[0]),
            "{plains:?}: Bulbasaur and Machop"
        );
        assert_eq!(remaining(&state, 0, &[1]), vec![70], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[1]), vec![60], "{plains:?}");
        assert_eq!(state.points, [1, 1], "{plains:?}");
        assert_eq!(state.winner, None, "{plains:?}");
        assert_eq!(promotion_choices(&game, 1), vec![1], "{plains:?}: the attacker first");

        promote(&mut game, 1, 1);
        assert_eq!(promotion_choices(&game, 0), vec![1], "{plains:?}: then player 0");
        promote(&mut game, 0, 1);
    }
}

// Conkeldurr's Bedrock Breaker (B4 089, Stage 2): 100 damage. "Discard a Stadium in play."

/// The opponent's Starting Plains goes to its owner's discard pile, and the +20 leaves every Basic
/// in play: Palkia (120 + 20) takes 100 and is at 40, then 20; the opponent's Seel 90 → 70; the
/// attacker's Squirtle (30 damage) 50 → 30. Conkeldurr (Stage 2) and both Ivysaur (Stage 1) never
/// had it.
#[test]
fn bedrock_breaker_takes_the_plus_20_off_every_basic_in_play_and_leaves_the_others_alone() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![conkeldurr(), squirtle().with_damage(30), ivysaur()],
            vec![palkia(CardId::C1038Palkia), seel(), ivysaur()],
        );
        let state = game.get_state_clone();
        assert_eq!(remaining(&state, 0, &[0, 1, 2]), vec![150, 50, 90], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1, 2]), vec![140, 90, 90], "{plains:?}");

        attack(&mut game, CardId::B4089Conkeldurr);
        let state = game.get_state_clone();
        assert!(
            state.active_stadium.is_none() && state.active_stadium_owner.is_none(),
            "{plains:?}"
        );
        assert_eq!(state.discard_piles[1], vec![get_card_by_enum(plains)], "{plains:?}");
        assert_eq!(remaining(&state, 0, &[0, 1, 2]), vec![150, 30, 90], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1, 2]), vec![20, 70, 90], "{plains:?}");
        assert_eq!(state.points, [0, 0], "{plains:?}");
    }
}

/// Bedrock Breaker against the opponent's Starting Plains: their Palkia (30 damage) takes the 100
/// and is at 10, then its 130 damage is above its printed 120 HP; their Benched Squirtle has 60
/// damage on 60 HP. Both are Knocked Out at once: 2 points, and the opponent promotes Seel (50
/// damage, now 20) or Ivysaur. The Knock Outs are the existing reading, not verified: the attack's
/// own, scored by the attack's own Knock Out check, so at the start of the opponent's turn the
/// engine counts their Pokémon as Knocked Out by damage from an attack during the last turn (the
/// flag Marshadow's Revenge reads), though Bedrock Breaker did no damage to the Benched Squirtle:
/// doubtful, see the module doc.
#[test]
fn bedrock_breaker_knocks_out_the_opponents_damaged_basics_at_once_as_the_attacks_knock_outs() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![conkeldurr(), bulbasaur()],
            vec![
                palkia(CardId::C1140Palkia).with_damage(30),
                squirtle().with_damage(60),
                seel().with_damage(50),
                ivysaur(),
            ],
        );
        attack(&mut game, CardId::B4089Conkeldurr);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none(), "{plains:?}");
        assert!(state.discard_piles[1].contains(&get_card_by_enum(plains)), "{plains:?}");
        assert!(knocked_out(&state, 1, &[0, 1]), "{plains:?}: Palkia and Squirtle");
        assert_eq!(remaining(&state, 1, &[2, 3]), vec![20, 90], "{plains:?}");
        assert_eq!(remaining(&state, 0, &[0, 1]), vec![150, 70], "{plains:?}");
        assert_eq!(state.points, [2, 0], "{plains:?}: both points at once");
        assert_eq!(state.winner, None, "{plains:?}");
        assert_eq!(promotion_choices(&game, 1), vec![2, 3], "{plains:?}");

        promote(&mut game, 1, 3);
        let state = end_turn(&mut game);
        assert!(
            state.get_knocked_out_by_opponent_attack_last_turn(),
            "{plains:?}: Knocked Out by the attack"
        );
    }
}

/// When the lost +20 gives the attacker its third point, the attacker wins at once: the opponent's
/// Benched Squirtle (60 damage on 60 HP) is Knocked Out, while their Palkia survives at 20. The win
/// is the existing reading, not verified.
#[test]
fn bedrock_breaker_wins_the_game_on_a_third_point_from_the_lost_plus_20() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            1,
            plains,
            vec![conkeldurr()],
            vec![palkia(CardId::C1038Palkia), squirtle().with_damage(60)],
        );
        set_points(&mut game, [2, 0]);
        attack(&mut game, CardId::B4089Conkeldurr);
        let state = game.get_state_clone();
        assert!(knocked_out(&state, 1, &[1]), "{plains:?}");
        assert_eq!(state.get_remaining_hp(1, 0), 20, "{plains:?}");
        assert_eq!(state.points, [3, 0], "{plains:?}");
        assert_eq!(state.winner, Some(GameOutcome::Win(0)), "{plains:?}");
    }
}

/// Bedrock Breaker discards its own player's Starting Plains too, and the attacker's own damaged
/// Benched Basics go: Squirtle (70 damage on 60 HP) and Bulbasaur (70 on 70) are Knocked Out at once
/// and the opponent scores both, while Seel (50 damage) stays at 20. Both were on the Bench, so
/// nobody promotes and Conkeldurr stays Active.
/// The Knock Outs are the existing reading, not verified: scored by the attack's own Knock Out
/// check (Bedrock Breaker refreshes the HP bonuses where Shatter does, and Shatter's double Knock
/// Out test from player 1's seat pins it), and not Knock Outs by the opponent's attack.
#[test]
fn bedrock_breaker_knocks_out_the_attackers_own_damaged_benched_basics() {
    for plains in PLAINS {
        let mut game = after_plains_played_by(
            0,
            plains,
            vec![
                conkeldurr(),
                squirtle().with_damage(70),
                bulbasaur().with_damage(70),
                seel().with_damage(50),
            ],
            vec![palkia(CardId::C1038Palkia), ivysaur()],
        );
        attack(&mut game, CardId::B4089Conkeldurr);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none(), "{plains:?}");
        assert!(state.discard_piles[0].contains(&get_card_by_enum(plains)), "{plains:?}");
        assert!(knocked_out(&state, 0, &[1, 2]), "{plains:?}: Squirtle and Bulbasaur");
        assert_eq!(remaining(&state, 0, &[0, 3]), vec![150, 20], "{plains:?}");
        assert_eq!(remaining(&state, 1, &[0, 1]), vec![20, 90], "{plains:?}");
        assert_eq!(state.points, [0, 2], "{plains:?}: the opponent scores both");

        // Nothing to promote: the only move left is to end the turn.
        let state = end_turn(&mut game);
        assert!(!state.get_knocked_out_by_opponent_attack_last_turn(), "{plains:?}");
    }
}

// Palkia's Spacial Rend (C1 038 / C1 140): 70 damage. "If your opponent has a Stadium in play,
// discard it." (c1_water_test.rs pins the opponent's B2 154 with an undamaged Active Knocked Out,
// the attacker's own B2 154 and a Stadium with no recorded owner.)

/// Spacial Rend against the opponent's Starting Plains, from either printing: their Snorlax (150 +
/// 20) takes 70 and is at 100, then 80; their Benched Squirtle (70 damage on 60 HP) is Knocked Out
/// at once, Seel (50 damage) stays at 20 and Ivysaur at 90; the attacker's Palkia and Bulbasaur lose
/// the +20 too (140 → 120, 90 → 70), and its Ivysaur (Stage 1) stays at 90. One point, and no
/// promotion: the Active survived.
/// The Knock Out is the existing reading, not verified: the attack's own, scored by the attack's
/// own Knock Out check, so at the start of the opponent's turn the engine counts their Pokémon as
/// Knocked Out by damage from an attack during the last turn (the flag Marshadow's Revenge reads),
/// though Spacial Rend did no damage to the Benched Squirtle: doubtful, see the module doc.
#[test]
fn spacial_rend_knocks_out_the_opponents_damaged_benched_basic_as_the_attacks_knock_out() {
    for printing in PALKIAS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![palkia(printing), bulbasaur(), ivysaur()],
                vec![
                    snorlax(),
                    squirtle().with_damage(70),
                    seel().with_damage(50),
                    ivysaur(),
                ],
            );
            let state = game.get_state_clone();
            assert_eq!(
                remaining(&state, 0, &[0, 1, 2]),
                vec![140, 90, 90],
                "{printing:?} {plains:?}"
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(
                state.active_stadium.is_none() && state.active_stadium_owner.is_none(),
                "{printing:?} {plains:?}"
            );
            assert!(
                state.discard_piles[1].contains(&get_card_by_enum(plains)),
                "{printing:?} {plains:?}"
            );
            assert!(knocked_out(&state, 1, &[1]), "{printing:?} {plains:?}: Squirtle");
            assert_eq!(remaining(&state, 1, &[0, 2, 3]), vec![80, 20, 90], "{printing:?} {plains:?}");
            assert_eq!(
                remaining(&state, 0, &[0, 1, 2]),
                vec![120, 70, 90],
                "{printing:?} {plains:?}"
            );
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");

            let state = end_turn(&mut game);
            assert!(
                state.get_knocked_out_by_opponent_attack_last_turn(),
                "{printing:?} {plains:?}: Knocked Out by the attack"
            );
        }
    }
}

/// The +20 leaves the attacker's side too when Spacial Rend discards the opponent's Starting
/// Plains: Palkia itself (130 damage, 10 left) and the Benched Squirtle (60 damage on 60 HP) are
/// Knocked Out at once, the opponent scores both, and Palkia's player promotes Bulbasaur (30 damage,
/// 60 → 40). The opponent's Snorlax takes the 70 (170 → 100 → 80) and Seel loses the +20 (90 → 70).
/// The Knock Outs are the existing reading, not verified: scored by the attack's own Knock Out
/// check (the double Knock Out test from player 1's seat below pins it), and not Knock Outs by the
/// opponent's attack.
#[test]
fn spacial_rend_knocks_out_palkia_itself_and_its_own_damaged_benched_basic() {
    for printing in PALKIAS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![
                    palkia(printing).with_damage(130),
                    squirtle().with_damage(60),
                    bulbasaur().with_damage(30),
                ],
                vec![snorlax(), seel()],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(state.active_stadium.is_none(), "{printing:?} {plains:?}");
            assert!(
                knocked_out(&state, 0, &[0, 1]),
                "{printing:?} {plains:?}: Palkia and Squirtle"
            );
            assert_eq!(remaining(&state, 0, &[2]), vec![40], "{printing:?} {plains:?}");
            assert_eq!(remaining(&state, 1, &[0, 1]), vec![80, 70], "{printing:?} {plains:?}");
            assert_eq!(state.points, [0, 2], "{printing:?} {plains:?}");
            assert_eq!(state.winner, None, "{printing:?} {plains:?}");
            assert_eq!(promotion_choices(&game, 0), vec![2], "{printing:?} {plains:?}");

            promote(&mut game, 0, 2);
            let state = end_turn(&mut game);
            assert!(
                !state.get_knocked_out_by_opponent_attack_last_turn(),
                "{printing:?} {plains:?}"
            );
        }
    }
}

/// Spacial Rend from player 1's seat knocks out both Active Pokémon with the lost +20 alone, from
/// either printing: player 0's Bulbasaur takes the 70 and is at 20, then its 70 damage is its
/// printed 70 HP, and Palkia's own 130 damage is above its printed 120 HP once player 0's Starting
/// Plains goes. One point each; player 0's Seel 90 → 70, player 1's Benched Squirtle 80 → 60.
/// The Knock Outs and the order of the promotions are the existing reading, not verified: both are
/// the attack's own, scored together by the attack's own Knock Out check, so Palkia's player
/// promotes first, as after any double Knock Out in an attack (rules/02 §7). The catch-all check
/// after the action goes by seat and would ask player 0 first (see the Shatter test above).
#[test]
fn spacial_rend_from_player_1s_seat_that_knocks_out_both_actives_lets_player_1_promote_first() {
    for printing in PALKIAS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                0,
                plains,
                vec![bulbasaur(), seel()],
                vec![palkia(printing).with_damage(130), squirtle()],
            );
            attack_as_player_1(&mut game, printing);
            let state = game.get_state_clone();
            assert!(state.active_stadium.is_none(), "{printing:?} {plains:?}");
            assert!(
                state.discard_piles[0].contains(&get_card_by_enum(plains)),
                "{printing:?} {plains:?}"
            );
            assert!(
                knocked_out(&state, 0, &[0]) && knocked_out(&state, 1, &[0]),
                "{printing:?} {plains:?}: Bulbasaur and Palkia"
            );
            assert_eq!(remaining(&state, 0, &[1]), vec![70], "{printing:?} {plains:?}");
            assert_eq!(remaining(&state, 1, &[1]), vec![60], "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 1], "{printing:?} {plains:?}");
            assert_eq!(state.winner, None, "{printing:?} {plains:?}");
            assert_eq!(
                promotion_choices(&game, 1),
                vec![1],
                "{printing:?} {plains:?}: the attacker first"
            );

            promote(&mut game, 1, 1);
            assert_eq!(
                promotion_choices(&game, 0),
                vec![1],
                "{printing:?} {plains:?}: then player 0"
            );
            promote(&mut game, 0, 1);
        }
    }
}

/// When the lost +20 gives Palkia's player their third point, they win at once: the opponent's
/// Benched Squirtle (60 damage on 60 HP) is Knocked Out, while Snorlax survives at 80. The win is the
/// existing reading, not verified.
#[test]
fn spacial_rend_wins_the_game_on_a_third_point_from_the_lost_plus_20() {
    for printing in PALKIAS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![palkia(printing)],
                vec![snorlax(), squirtle().with_damage(60)],
            );
            set_points(&mut game, [2, 0]);
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[1]), "{printing:?} {plains:?}");
            assert_eq!(state.get_remaining_hp(1, 0), 80, "{printing:?} {plains:?}");
            assert_eq!(state.points, [3, 0], "{printing:?} {plains:?}");
            assert_eq!(state.winner, Some(GameOutcome::Win(0)), "{printing:?} {plains:?}");
        }
    }
}

/// Spacial Rend leaves its own player's Starting Plains in play, from either printing and with
/// each printing of the Stadium, and every +20 stays: the opponent's Bulbasaur takes the 70 and is
/// at 20, and the two Squirtles with 70 damage (one on each side, 10 left) stay in play.
#[test]
fn spacial_rend_leaves_its_own_players_starting_plains_and_every_plus_20() {
    for printing in PALKIAS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                0,
                plains,
                vec![palkia(printing), squirtle().with_damage(70)],
                vec![bulbasaur(), squirtle().with_damage(70)],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert_eq!(
                state.active_stadium,
                Some(get_card_by_enum(plains)),
                "{printing:?} {plains:?}"
            );
            assert_eq!(state.active_stadium_owner, Some(0), "{printing:?} {plains:?}");
            assert!(
                state.discard_piles[0].is_empty() && state.discard_piles[1].is_empty(),
                "{printing:?} {plains:?}"
            );
            assert_eq!(remaining(&state, 0, &[0, 1]), vec![140, 10], "{printing:?} {plains:?}");
            assert_eq!(remaining(&state, 1, &[0, 1]), vec![20, 10], "{printing:?} {plains:?}");
            assert_eq!(state.points, [0, 0], "{printing:?} {plains:?}");
        }
    }
}

// Field Blower (B3 147; reprints B4b 202 and B4b 368), an Item: "Discard a Pokémon Tool card from
// a Pokémon (yours or your opponent's), or discard a Stadium card in play."

/// Each printing of Field Blower against each printing of the opponent's Starting Plains: the
/// Stadium goes to its owner's discard pile and the +20 leaves every Basic in play: the user's
/// Bulbasaur 90 → 70 and Squirtle (30 damage) 50 → 30; the opponent's Seel (50 damage) 40 → 20 and
/// Bulbasaur 90 → 70. Both Ivysaur (Stage 1) stay at 90.
#[test]
fn field_blower_takes_the_plus_20_off_every_basic_in_play_and_leaves_the_stage_1s_alone() {
    for blower in FIELD_BLOWERS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![bulbasaur(), squirtle().with_damage(30), ivysaur()],
                vec![seel().with_damage(50), bulbasaur(), ivysaur()],
            );
            field_blower_the_stadium(&mut game, blower);
            let state = game.get_state_clone();
            assert!(
                state.active_stadium.is_none() && state.active_stadium_owner.is_none(),
                "{blower:?} {plains:?}"
            );
            assert_eq!(state.discard_piles[1], vec![get_card_by_enum(plains)], "{blower:?} {plains:?}");
            assert_eq!(state.discard_piles[0], vec![get_card_by_enum(blower)], "{blower:?} {plains:?}");
            assert_eq!(remaining(&state, 0, &[0, 1, 2]), vec![70, 30, 90], "{blower:?} {plains:?}");
            assert_eq!(remaining(&state, 1, &[0, 1, 2]), vec![20, 70, 90], "{blower:?} {plains:?}");
            assert_eq!(state.points, [0, 0], "{blower:?} {plains:?}");
        }
    }
}

/// Field Blower on the opponent's Starting Plains: their Bulbasaur (70 damage on 70 HP) and
/// Benched Squirtle (70 damage on 60 HP) are Knocked Out at once and both points scored; they promote
/// Seel (50 damage, now 20) or Ivysaur, and the user's turn goes on: their Bulbasaur can still
/// attack. The Knock Outs are the existing reading, not verified: scored by the catch-all Knock Out
/// check after the Item, so they are not Knock Outs by an attack. The points at once, the promotion
/// and the turn going on match Dustin's ruling in rules/02 §7-§8: nothing here is open.
#[test]
fn field_blower_knocks_out_the_opponents_damaged_basics_at_once_and_the_turn_goes_on() {
    for blower in FIELD_BLOWERS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![bulbasaur().with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
                vec![
                    bulbasaur().with_damage(70),
                    squirtle().with_damage(70),
                    seel().with_damage(50),
                    ivysaur(),
                ],
            );
            field_blower_the_stadium(&mut game, blower);
            let state = game.get_state_clone();
            assert!(state.active_stadium.is_none(), "{blower:?} {plains:?}");
            assert!(
                state.discard_piles[1].contains(&get_card_by_enum(plains)),
                "{blower:?} {plains:?}"
            );
            assert!(
                knocked_out(&state, 1, &[0, 1]),
                "{blower:?} {plains:?}: Bulbasaur and Squirtle"
            );
            assert_eq!(remaining(&state, 1, &[2, 3]), vec![20, 90], "{blower:?} {plains:?}");
            assert_eq!(remaining(&state, 0, &[0]), vec![70], "{blower:?} {plains:?}");
            assert_eq!(state.points, [2, 0], "{blower:?} {plains:?}: both points at once");
            assert_eq!(state.winner, None, "{blower:?} {plains:?}");
            assert_eq!(promotion_choices(&game, 1), vec![2, 3], "{blower:?} {plains:?}");

            promote(&mut game, 1, 2);
            offered(&game, 0, attack_action(CardId::A1001Bulbasaur, 0));
            let state = end_turn(&mut game);
            assert!(
                !state.get_knocked_out_by_opponent_attack_last_turn(),
                "{blower:?} {plains:?}"
            );
        }
    }
}

/// Field Blower on its own player's Starting Plains: the user's Bulbasaur (70 damage on 70 HP) and
/// Benched Squirtle (60 on 60) are Knocked Out at once and the opponent scores both; the user
/// promotes Seel (30 damage, 60 → 40) and the turn goes on. The opponent's Bulbasaur 90 → 70, their
/// Ivysaur (Stage 1) stays at 90. The Knock Outs are the existing reading, not verified: scored by
/// the catch-all Knock Out check after the Item. The opponent scoring them (rules/02 §6), the
/// promotion and the turn going on match rules/02 §7-§8 (nothing open; see the module doc).
#[test]
fn field_blower_on_its_own_starting_plains_knocks_out_the_users_damaged_basics() {
    for blower in FIELD_BLOWERS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                0,
                plains,
                vec![
                    bulbasaur().with_damage(70),
                    squirtle().with_damage(60),
                    seel().with_damage(30),
                ],
                vec![ivysaur(), bulbasaur()],
            );
            field_blower_the_stadium(&mut game, blower);
            let state = game.get_state_clone();
            assert!(state.active_stadium.is_none(), "{blower:?} {plains:?}");
            assert!(
                state.discard_piles[0].contains(&get_card_by_enum(plains)),
                "{blower:?} {plains:?}: its own discard pile"
            );
            assert!(
                knocked_out(&state, 0, &[0, 1]),
                "{blower:?} {plains:?}: Bulbasaur and Squirtle"
            );
            assert_eq!(remaining(&state, 0, &[2]), vec![40], "{blower:?} {plains:?}");
            assert_eq!(remaining(&state, 1, &[0, 1]), vec![90, 70], "{blower:?} {plains:?}");
            assert_eq!(state.points, [0, 2], "{blower:?} {plains:?}: the opponent scores both");
            assert_eq!(state.winner, None, "{blower:?} {plains:?}");
            assert_eq!(promotion_choices(&game, 0), vec![2], "{blower:?} {plains:?}");

            promote(&mut game, 0, 2);
            let (actor, _) = game.get_state_clone().generate_possible_actions();
            assert_eq!(actor, 0, "{blower:?} {plains:?}: the turn goes on");
        }
    }
}

/// When the lost +20 gives the user their third point, they win at once: the opponent's Benched
/// Squirtle (60 damage on 60 HP) is Knocked Out. The win is the existing reading, not verified; it
/// matches rules/02 §7-§8 ("the game ends there if it's the winning point"; see the module doc).
#[test]
fn field_blower_wins_the_game_on_a_third_point_from_the_lost_plus_20() {
    for blower in FIELD_BLOWERS {
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![bulbasaur()],
                vec![ivysaur(), squirtle().with_damage(60)],
            );
            set_points(&mut game, [2, 0]);
            field_blower_the_stadium(&mut game, blower);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[1]), "{blower:?} {plains:?}");
            assert_eq!(state.points, [3, 0], "{blower:?} {plains:?}");
            assert_eq!(state.winner, Some(GameOutcome::Win(0)), "{blower:?} {plains:?}");
        }
    }
}
