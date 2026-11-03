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
//! A Pokémon whose damage reaches its HP without the +20 is Knocked Out at once. Whichever check
//! scores it, the point goes to the owner's opponent (rules/02 §6), and the owner promotes if it
//! was the Active Pokémon.
//!
//! After one of the three attacks, the attack's damage comes first, with the +20 still in place,
//! and then the Stadium is discarded (the card texts give no order). Each attack refreshes the HP
//! bonuses inside its own effect, so the attack's own Knock Out check scores every Knock Out. A
//! Pokémon the attack's damage Knocks Out at its HP with the +20 is the attack's Knock Out. One
//! still in play after the damage that the lost +20 then Knocks Out is not: the defender left with
//! damage at least its printed HP but below HP + 20, and any Benched Basic, on either side. Its
//! point still counts and its owner still promotes, but nothing that reads "Knocked Out by damage
//! from an attack" fires for it: the flag Marshadow's Revenge reads ("If any of your Pokémon were
//! Knocked Out by damage from an attack during your opponent's last turn"), Zarude's Dark
//! Vengeance type tally, Rescue Scarf, and the attack's on-Knock-Out hooks such as Lucky Egg,
//! Innards Out and the attacker's Lucky Mittens (Iris's extra point needs a Haxorus attacker, which
//! none of these attacks has). Every test here that asserts how such a Knock Out is scored, its
//! points or a win from it says so. All of this is
//! Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game (rules/02 §8,
//! rules/08 T15).
//!
//! When both Active Pokémon go, the attacker promotes first, as after any double Knock Out in an
//! attack (rules/02 §7), where the catch-all check after the action would go by seat (player 0
//! first). That order is the existing reading, not verified (question 2, asked Nov 3).
//!
//! After Field Blower it is the catch-all Knock Out check that follows the Item, and the turn goes
//! on. The points at once, the promotion, the win and the turn going on are
//! Dustin's ruling (rules/02 §7-§8; Nov 3: not an attack), on Knock Outs from removing an HP
//! bonus outside an attack (with an Ability Knock Out filmed in 025604, and the settled list in
//! rules/05), and with no attack there is no Knock Out by an attack.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
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
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game: both survived
/// Shatter's damage and fell to the lost +20, so the attack's own Knock Out check scores them but
/// neither is the attack's Knock Out: at the start of the opponent's turn the engine does not count
/// their Pokémon as Knocked Out by damage from an attack during the last turn (the flag Marshadow's
/// Revenge reads).
#[test]
fn shatter_knocks_out_the_opponents_damaged_basics_at_once_but_not_as_the_attacks_knock_outs() {
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
            !state.get_knocked_out_by_opponent_attack_last_turn(),
            "{plains:?}: not Knocked Out by the attack"
        );
    }
}

/// Shatter discards a Stadium its own player put into play just the same, and the +20 leaves the
/// attacker's side too: Machop itself (70 damage, 20 left) and the Benched Squirtle (60 damage on 60
/// HP) are Knocked Out at once, the opponent scores both, and Machop's player promotes Bulbasaur (30
/// damage, 60 → 40). The opponent's Ivysaur takes the 10 (90 → 80) and Seel loses the +20 (90 → 70).
/// The Knock Outs are scored by the attack's own Knock Out check (the double Knock Out test from
/// player 1's seat below pins it), and are not the attack's Knock Outs, nor Knock Outs by the
/// opponent's attack:
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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
/// Machop's player still has a Pokémon in play. The win (the point still counts):
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game: both Knock
/// Outs are scored, and neither is the attack's Knock Out. The order of the promotions is the
/// existing reading, not verified (question 2, asked Nov 3): both are scored together by the
/// attack's own Knock Out check, so Machop's player promotes first, as after any double Knock Out
/// in an attack (rules/02 §7). The catch-all check after the action goes by seat and would ask
/// player 0 first, so only an attacker in player 1's seat tells the two checks apart. A Knock Out by
/// the attack's damage would not either: the discard that follows it refreshes the HP bonuses and
/// pulls the lost +20's Knock Outs into the attack's check.
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
/// damage, now 20) or Ivysaur.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game: both survived
/// Bedrock Breaker's damage and fell to the lost +20, so the attack's own Knock Out check scores
/// them but neither is the attack's Knock Out: at the start of the opponent's turn the engine does
/// not count their Pokémon as Knocked Out by damage from an attack during the last turn (the flag
/// Marshadow's Revenge reads).
#[test]
fn bedrock_breaker_knocks_out_the_opponents_damaged_basics_but_not_as_the_attacks_knock_outs() {
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
            !state.get_knocked_out_by_opponent_attack_last_turn(),
            "{plains:?}: not Knocked Out by the attack"
        );
    }
}

/// When the lost +20 gives the attacker its third point, the attacker wins at once: the opponent's
/// Benched Squirtle (60 damage on 60 HP) is Knocked Out, while their Palkia survives at 20. The win
/// (the point still counts):
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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
/// The Knock Outs are scored by the attack's own Knock Out check (Bedrock Breaker refreshes the HP
/// bonuses where Shatter does, and Shatter's double Knock Out test from player 1's seat pins it),
/// and are not the attack's Knock Outs, nor Knock Outs by the opponent's attack:
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game: Spacial Rend
/// did no damage to the Benched Squirtle, which fell to the lost +20, so the attack's own Knock Out
/// check scores it but it is not the attack's Knock Out: at the start of the opponent's turn the
/// engine does not count their Pokémon as Knocked Out by damage from an attack during the last turn
/// (the flag Marshadow's Revenge reads).
#[test]
fn spacial_rend_knocks_out_the_opponents_damaged_benched_basic_but_not_as_the_attacks_knock_out() {
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
                !state.get_knocked_out_by_opponent_attack_last_turn(),
                "{printing:?} {plains:?}: not Knocked Out by the attack"
            );
        }
    }
}

/// The +20 leaves the attacker's side too when Spacial Rend discards the opponent's Starting
/// Plains: Palkia itself (130 damage, 10 left) and the Benched Squirtle (60 damage on 60 HP) are
/// Knocked Out at once, the opponent scores both, and Palkia's player promotes Bulbasaur (30 damage,
/// 60 → 40). The opponent's Snorlax takes the 70 (170 → 100 → 80) and Seel loses the +20 (90 → 70).
/// The Knock Outs are scored by the attack's own Knock Out check (the double Knock Out test from
/// player 1's seat below pins it), and are not the attack's Knock Outs, nor Knock Outs by the
/// opponent's attack:
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game: both Knock
/// Outs are scored, and neither is the attack's Knock Out. The order of the promotions is the
/// existing reading, not verified (question 2, asked Nov 3): both are scored together by the
/// attack's own Knock Out check, so Palkia's player promotes first, as after any double Knock Out in
/// an attack (rules/02 §7). The catch-all check after the action goes by seat and would ask player
/// 0 first (see the Shatter test above).
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
/// Benched Squirtle (60 damage on 60 HP) is Knocked Out, while Snorlax survives at 80. The win (the
/// point still counts):
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
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

// Knocked Out by the attack's damage, or by the lost +20 after it.
// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game (rules/02 §8):
// the attack's damage comes first, with the +20 still in place, and a Pokémon it Knocks Out is the
// attack's Knock Out; one it leaves in play that the lost +20 then Knocks Out is not, though its
// point still counts. Each test runs every attack that discards a Stadium (Spacial Rend from both
// printings) against each printing of the opponent's Starting Plains. In each contrast test the
// attack's damage alone Knocks the Pokémon Out, at its HP + 20: the attack's Knock Out, before
// R8-10e and after.

/// One of the three attacks that discard a Stadium, used by player 0's Active Pokémon.
struct StadiumDiscard {
    /// The attacker, with the Energy its attack needs.
    attacker: PlayedCard,
    printing: CardId,
    /// The attack's damage to the opponent's Active Pokémon: no defender below is Weak to it.
    damage: u32,
    /// The attacker's HP once Starting Plains is gone.
    hp: u32,
}

/// Machop's Shatter (10 damage), Conkeldurr's Bedrock Breaker (100) and Palkia's Spacial Rend (70)
/// from both printings.
fn stadium_discards() -> Vec<StadiumDiscard> {
    let mut discards = vec![
        StadiumDiscard {
            attacker: machop(),
            printing: CardId::B2079Machop,
            damage: 10,
            hp: 70,
        },
        StadiumDiscard {
            attacker: conkeldurr(),
            printing: CardId::B4089Conkeldurr,
            damage: 100,
            hp: 150,
        },
    ];
    discards.extend(PALKIAS.map(|printing| StadiumDiscard {
        attacker: palkia(printing),
        printing,
        damage: 70,
        hp: 120,
    }));
    discards
}

/// `basic`, a Basic Pokémon of `hp` printed HP, with the damage that leaves it `left` HP (with
/// Starting Plains' +20) after an attack's `damage`. At 0 the attack's damage Knocks it Out, at its
/// HP + 20. At 10 or 20 the attack's damage is at least its printed HP but less than HP + 20: it
/// survives the damage, and the lost +20 Knocks it Out.
fn left_after_the_damage(basic: PlayedCard, hp: u32, damage: u32, left: u32) -> PlayedCard {
    basic.with_damage(hp + 20 - damage - left)
}

fn palkia_defender() -> PlayedCard {
    // 120 HP, Basic, Weakness [L].
    PlayedCard::from_id(CardId::C1038Palkia)
}

/// Zarude (B3 114): 90 HP, Basic, [D], Weakness [G], with the Energy for Dark Vengeance ([D][D], 40
/// damage): "If any of your [D] Pokémon were Knocked Out by damage from an attack during your
/// opponent's last turn, this attack does 80 more damage."
fn zarude() -> PlayedCard {
    PlayedCard::from_id(CardId::B3114Zarude)
        .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])
}

/// Pyukumuku (A3 054): 60 HP, Basic, Weakness [L]. Innards Out: "If this Pokémon is in the Active
/// Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, do 50 damage to
/// the Attacking Pokémon."
fn pyukumuku() -> PlayedCard {
    PlayedCard::from_id(CardId::A3054Pyukumuku)
}

/// Rescue Scarf (A4 155): "If the Pokémon this card is attached to is Knocked Out by damage from an
/// attack from your opponent's Pokémon, put it into your hand instead of the discard pile."
fn with_rescue_scarf(pokemon: PlayedCard) -> PlayedCard {
    pokemon.with_tool(get_card_by_enum(CardId::A4155RescueScarf))
}

/// Lucky Mittens (B1 220): "Whenever your opponent's Pokémon is Knocked Out by damage from an
/// attack used by the Pokémon this card is attached to, draw a card."
fn with_lucky_mittens(pokemon: PlayedCard) -> PlayedCard {
    pokemon.with_tool(get_card_by_enum(CardId::B1220LuckyMittens))
}

fn holds(cards: &[Card], name: &str) -> bool {
    cards.iter().any(|card| card.get_name() == name)
}

/// The remaining HP of `player`'s Active Pokémon, or 0 once it is Knocked Out (the spot is empty).
fn active_remaining_hp(state: &State, player: usize) -> u32 {
    state.in_play_pokemon[player][0]
        .as_ref()
        .map_or(0, |active| active.get_remaining_hp())
}

/// Player 0 ends the turn, and after player 1's draw their Active Zarude uses Dark Vengeance on
/// player 0's Active. Returns the state at the start of player 1's turn, as `end_turn` does.
fn end_turn_and_dark_vengeance(game: &mut Game<'static>) -> State {
    let start_of_turn = end_turn(game);
    // Player 1's draw.
    game.play_until_stable();
    let dark_vengeance = offered(game, 1, attack_action(CardId::B3114Zarude, 0));
    game.apply_action(&dark_vengeance);
    start_of_turn
}

/// Player 0 attacks the opponent's Active Palkia, which the attack's damage leaves with 20 or 10 HP
/// (its damage at least its printed 120 HP), and then the lost +20 Knocks it Out. It is scored and
/// its owner promotes Ivysaur, but it is not the attack's Knock Out: at the start of the opponent's
/// turn the engine does not count their Pokémon as Knocked Out by damage from an attack during the
/// last turn (the flag Marshadow's Revenge reads).
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn a_defender_the_damage_leaves_in_play_falls_to_the_lost_plus_20_not_to_the_attack() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            for left in [20, 10] {
                let mut game = after_plains_played_by(
                    1,
                    plains,
                    vec![discard.attacker.clone()],
                    vec![
                        left_after_the_damage(palkia_defender(), 120, discard.damage, left),
                        ivysaur(),
                    ],
                );
                attack(&mut game, printing);
                let state = game.get_state_clone();
                assert!(state.active_stadium.is_none(), "{printing:?} {plains:?} {left}");
                assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?} {left}");
                assert_eq!(state.points, [1, 0], "{printing:?} {plains:?} {left}: scored");
                assert_eq!(promotion_choices(&game, 1), vec![1], "{printing:?} {plains:?} {left}");

                promote(&mut game, 1, 1);
                let state = end_turn(&mut game);
                assert!(
                    !state.get_knocked_out_by_opponent_attack_last_turn(),
                    "{printing:?} {plains:?} {left}: not Knocked Out by the attack"
                );
            }
        }
    }
}

/// The contrast: the attack's damage alone takes the opponent's Active Palkia to its 120 HP + 20.
/// That is the attack's Knock Out, and the flag Marshadow's Revenge reads is set.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn a_defender_the_damage_knocks_out_at_hp_plus_20_is_the_attacks_knock_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    left_after_the_damage(palkia_defender(), 120, discard.damage, 0),
                    ivysaur(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(state.active_stadium.is_none(), "{printing:?} {plains:?}");
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert_eq!(promotion_choices(&game, 1), vec![1], "{printing:?} {plains:?}");

            promote(&mut game, 1, 1);
            let state = end_turn(&mut game);
            assert!(
                state.get_knocked_out_by_opponent_attack_last_turn(),
                "{printing:?} {plains:?}: Knocked Out by the attack"
            );
        }
    }
}

/// Rescue Scarf on the opponent's Active Palkia, which the attack's damage leaves with 10 HP and
/// the lost +20 then Knocks Out: not by damage from an attack, so Palkia goes to its owner's
/// discard pile, not the hand. The point still counts.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn rescue_scarf_does_not_save_a_defender_the_lost_plus_20_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    with_rescue_scarf(left_after_the_damage(
                        palkia_defender(),
                        120,
                        discard.damage,
                        10,
                    )),
                    ivysaur(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert!(
                !holds(&state.hands[1], "Palkia"),
                "{printing:?} {plains:?}: not to the hand"
            );
            assert!(
                holds(&state.discard_piles[1], "Palkia"),
                "{printing:?} {plains:?}: to the discard pile"
            );
        }
    }
}

/// The contrast: the attack's damage Knocks Out the opponent's Active Palkia at 120 HP + 20, and
/// Rescue Scarf puts it into its owner's hand instead of the discard pile.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn rescue_scarf_saves_a_defender_the_attacks_damage_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    with_rescue_scarf(left_after_the_damage(
                        palkia_defender(),
                        120,
                        discard.damage,
                        0,
                    )),
                    ivysaur(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert!(
                holds(&state.hands[1], "Palkia"),
                "{printing:?} {plains:?}: to the hand"
            );
            assert!(
                !holds(&state.discard_piles[1], "Palkia"),
                "{printing:?} {plains:?}: not to the discard pile"
            );
        }
    }
}

/// The opponent's Active Zarude ([D]) is left with 10 HP by the attack's damage, and the lost +20
/// Knocks it Out; they promote their second Zarude. Next turn its Dark Vengeance does its printed
/// 40: no [D] Pokémon of theirs was Knocked Out by damage from an attack.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn dark_vengeance_does_not_count_a_dark_pokemon_the_lost_plus_20_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    left_after_the_damage(zarude(), 90, discard.damage, 10),
                    zarude(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            promote(&mut game, 1, 1);

            end_turn_and_dark_vengeance(&mut game);
            assert_eq!(
                active_remaining_hp(&game.get_state_clone(), 0),
                discard.hp - 40,
                "{printing:?} {plains:?}: Dark Vengeance's 40"
            );
        }
    }
}

/// The contrast: the attack's damage Knocks Out the opponent's Active Zarude at 90 HP + 20, and
/// next turn their second Zarude's Dark Vengeance does 40 + 80 = 120: Machop (70) and Palkia (120)
/// are Knocked Out, and Conkeldurr is left with 30.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn dark_vengeance_counts_a_dark_pokemon_the_attacks_damage_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    left_after_the_damage(zarude(), 90, discard.damage, 0),
                    zarude(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            promote(&mut game, 1, 1);

            end_turn_and_dark_vengeance(&mut game);
            assert_eq!(
                active_remaining_hp(&game.get_state_clone(), 0),
                discard.hp.saturating_sub(120),
                "{printing:?} {plains:?}: Dark Vengeance's 120"
            );
        }
    }
}

/// Innards Out on the opponent's Active Pyukumuku, which the attack's damage leaves with 10 HP and
/// the lost +20 then Knocks Out: not by damage from an attack, so it does not fire and the attacker
/// keeps its HP. Bedrock Breaker's 100 is more than Pyukumuku's 60 + 20, so only Shatter and
/// Spacial Rend can leave it in play.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn innards_out_does_not_fire_for_a_pyukumuku_the_lost_plus_20_knocks_out() {
    for discard in stadium_discards()
        .into_iter()
        .filter(|discard| discard.printing != CardId::B4089Conkeldurr)
    {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    left_after_the_damage(pyukumuku(), 60, discard.damage, 10),
                    ivysaur(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert_eq!(
                state.get_remaining_hp(0, 0),
                discard.hp,
                "{printing:?} {plains:?}: no Innards Out"
            );
        }
    }
}

/// The contrast: the attack's damage Knocks Out the opponent's Active Pyukumuku at 60 HP + 20, and
/// Innards Out does its 50 to the attacker: Machop 70 → 20, Palkia 120 → 70.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn innards_out_fires_for_a_pyukumuku_the_attacks_damage_knocks_out() {
    for discard in stadium_discards()
        .into_iter()
        .filter(|discard| discard.printing != CardId::B4089Conkeldurr)
    {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![discard.attacker.clone()],
                vec![
                    left_after_the_damage(pyukumuku(), 60, discard.damage, 0),
                    ivysaur(),
                ],
            );
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert_eq!(
                state.get_remaining_hp(0, 0),
                discard.hp - 50,
                "{printing:?} {plains:?}: Innards Out's 50"
            );
        }
    }
}

/// Lucky Mittens on the attacker: the opponent's Active Palkia, left with 10 HP by the attack's
/// damage, falls to the lost +20, which is not a Knock Out by damage from the attack, so the
/// attacker's player draws nothing.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn lucky_mittens_draws_nothing_for_a_defender_the_lost_plus_20_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![with_lucky_mittens(discard.attacker.clone())],
                vec![
                    left_after_the_damage(palkia_defender(), 120, discard.damage, 10),
                    ivysaur(),
                ],
            );
            let hand_before = game.get_state_clone().hands[0].len();
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert_eq!(
                state.hands[0].len(),
                hand_before,
                "{printing:?} {plains:?}: no Lucky Mittens draw"
            );
        }
    }
}

/// The contrast: the attack's damage Knocks Out the opponent's Active Palkia at 120 HP + 20, and
/// Lucky Mittens draws 1 card.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn lucky_mittens_draws_for_a_defender_the_attacks_damage_knocks_out() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![with_lucky_mittens(discard.attacker.clone())],
                vec![
                    left_after_the_damage(palkia_defender(), 120, discard.damage, 0),
                    ivysaur(),
                ],
            );
            let hand_before = game.get_state_clone().hands[0].len();
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(knocked_out(&state, 1, &[0]), "{printing:?} {plains:?}");
            assert_eq!(state.points, [1, 0], "{printing:?} {plains:?}");
            assert_eq!(
                state.hands[0].len(),
                hand_before + 1,
                "{printing:?} {plains:?}: one Lucky Mittens draw"
            );
        }
    }
}

/// One wave with both kinds of Knock Out, and one on the attacker's own side. The attack's damage
/// Knocks Out the opponent's Active Palkia at 120 HP + 20. Their Benched Zarude (90 damage on 90 HP)
/// and the attacker's own Benched Squirtle (60 on 60), which the attack did not damage, fall to the
/// lost +20. Each of the three holds Rescue Scarf, and all three are scored: 2 points to the
/// attacker, 1 to the opponent, who promotes their second Zarude. Only Palkia is the attack's Knock
/// Out: Rescue Scarf puts it into its owner's hand but sends the Benched Zarude and the attacker's
/// own Squirtle to the discard pile; the attacker's Lucky Mittens draws 1 card, not 2; the flag
/// Marshadow's Revenge reads is set, by Palkia; and next turn Dark Vengeance does its printed 40, as
/// no [D] Pokémon was Knocked Out by damage from the attack.
/// Dustin's expected reading, Nov 3 (damage, then discard); to be confirmed in game.
#[test]
fn one_wave_holds_the_attacks_knock_out_and_the_lost_plus_20s_on_both_sides() {
    for discard in stadium_discards() {
        let printing = discard.printing;
        for plains in PLAINS {
            let mut game = after_plains_played_by(
                1,
                plains,
                vec![
                    with_lucky_mittens(discard.attacker.clone()),
                    with_rescue_scarf(squirtle().with_damage(60)),
                ],
                vec![
                    with_rescue_scarf(left_after_the_damage(
                        palkia_defender(),
                        120,
                        discard.damage,
                        0,
                    )),
                    with_rescue_scarf(PlayedCard::from_id(CardId::B3114Zarude).with_damage(90)),
                    zarude(),
                ],
            );
            let hand_before = game.get_state_clone().hands[0].len();
            attack(&mut game, printing);
            let state = game.get_state_clone();
            assert!(
                knocked_out(&state, 1, &[0, 1]) && knocked_out(&state, 0, &[1]),
                "{printing:?} {plains:?}: Palkia, the Benched Zarude and Squirtle"
            );
            assert_eq!(state.points, [2, 1], "{printing:?} {plains:?}: all three scored");
            assert!(
                holds(&state.hands[1], "Palkia") && !holds(&state.discard_piles[1], "Palkia"),
                "{printing:?} {plains:?}: Rescue Scarf saves the attack's Knock Out"
            );
            assert!(
                holds(&state.discard_piles[1], "Zarude") && !holds(&state.hands[1], "Zarude"),
                "{printing:?} {plains:?}: but not the Benched Zarude"
            );
            assert!(
                holds(&state.discard_piles[0], "Squirtle") && !holds(&state.hands[0], "Squirtle"),
                "{printing:?} {plains:?}: nor the attacker's own Squirtle"
            );
            assert_eq!(
                state.hands[0].len(),
                hand_before + 1,
                "{printing:?} {plains:?}: one Lucky Mittens draw, for Palkia"
            );
            assert_eq!(promotion_choices(&game, 1), vec![2], "{printing:?} {plains:?}");

            promote(&mut game, 1, 2);
            let start_of_turn = end_turn_and_dark_vengeance(&mut game);
            assert!(
                start_of_turn.get_knocked_out_by_opponent_attack_last_turn(),
                "{printing:?} {plains:?}: Knocked Out by the attack, Palkia"
            );
            assert_eq!(
                active_remaining_hp(&game.get_state_clone(), 0),
                discard.hp - 40,
                "{printing:?} {plains:?}: Dark Vengeance's 40"
            );
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
/// attack. The Knock Outs are Dustin's ruling (rules/02 §7-§8; Nov 3: not an attack): scored by the
/// catch-all Knock Out check after the Item, so they are not Knock Outs by an attack, with the
/// points at once, the promotion and the turn going on. Nothing here is open.
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
/// Ivysaur (Stage 1) stays at 90. The Knock Outs are Dustin's ruling (rules/02 §7-§8; Nov 3: not
/// an attack): scored by the catch-all Knock Out check after the Item, with the opponent scoring
/// them (rules/02 §6), the promotion and the turn going on (nothing open; see the module doc).
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
/// Squirtle (60 damage on 60 HP) is Knocked Out. The win is Dustin's ruling (rules/02 §7-§8; Nov
/// 3: not an attack): "the game ends there if it's the winning point" (see the module doc).
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
