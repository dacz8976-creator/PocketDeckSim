// Ported from upstream deckgym-core #437 (tests/pokemon/c1_water_test.rs, as of 3c7bdab): the Dewgong and Palkia tests (2 + 3), without the 2 Frogadier tests (R8-05c), with fork tests added at the end (both printings; only [W] Energy discarded; the one choice with fewer than 3 opposing Pokémon; a chosen target with a coin-flip damage Ability, through the queued choice and its coin; Lorelei's +30 on each target; Spacial Rend v Starting Plains, the opponent's, the attacker's own and one with no recorded owner; no Stadium; the printings' status).
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{
        attack_action, get_initialized_game_with_board, get_test_game_with_board, trainer_from_id,
    },
    Game, State,
};

/// Dewgong - Dual Blizzard: discard 2 [W] Energy from this Pokémon, and this attack does 60
/// damage to 2 of your opponent's Pokémon.
#[test]
fn test_dewgong_dual_blizzard_hits_two_chosen_pokemon_and_discards_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1033Dewgong).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
        ])],
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax),
            PlayedCard::from_id(CardId::A1129MewtwoEx),
            PlayedCard::from_id(CardId::B4197WailordEx),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::C1033Dewgong, 0),
        is_stack: false,
    });

    // Any pair out of the 3 opposing Pokémon can be picked.
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    assert_eq!(choices.len(), 3);

    // Pick the pair of the two Benched Pokémon.
    let pick = choices
        .iter()
        .find(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => {
                targets.iter().all(|(_, _, idx)| *idx != 0)
            }
            _ => false,
        })
        .expect("a pair of Benched targets should be offered")
        .clone();
    game.apply_action(&pick);
    game.play_until_stable();

    let state = game.get_state_clone();
    let hp = |idx: usize| {
        state.in_play_pokemon[1][idx]
            .as_ref()
            .unwrap()
            .get_remaining_hp()
    };
    assert_eq!(hp(0), 150);
    assert_eq!(hp(1), 150 - 60);
    assert_eq!(hp(2), 250 - 60);
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Water, EnergyType::Water]
    );
    assert_eq!(state.discard_energies[0], vec![EnergyType::Water; 2]);
}

/// With only the Active Pokémon in play, Dual Blizzard can only hit that one.
#[test]
fn test_dewgong_dual_blizzard_with_lone_target_hits_it_once() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1033Dewgong).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
        ])],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::C1033Dewgong, 0),
        is_stack: false,
    });
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 250 - 60);
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Water]);
}

fn palkia_attacks_with_stadium(stadium_owner: usize) -> deckgym::State {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1038Palkia).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Colorless,
        ])],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    let mut state = game.get_state_clone();
    state.set_active_stadium_for_player(stadium_owner, get_card_by_enum(CardId::B4a072Arcade));
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::C1038Palkia, 0),
        is_stack: false,
    });
    game.play_until_stable();
    game.get_state_clone()
}

/// Palkia - Spacial Rend: 70 damage, and if the opponent has a Stadium in play, discard it.
#[test]
fn test_palkia_spacial_rend_discards_the_opponents_stadium() {
    let state = palkia_attacks_with_stadium(1);
    assert_eq!(state.get_active(1).get_remaining_hp(), 250 - 70);
    assert!(state.active_stadium.is_none());
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| *card == get_card_by_enum(CardId::B4a072Arcade)));
}

/// Palkia leaves its own player's Stadium in play.
#[test]
fn test_palkia_spacial_rend_keeps_your_own_stadium() {
    let state = palkia_attacks_with_stadium(0);
    assert_eq!(state.get_active(1).get_remaining_hp(), 250 - 70);
    assert_eq!(
        state.active_stadium,
        Some(get_card_by_enum(CardId::B4a072Arcade))
    );
}

/// Palkia deals its damage normally when there is no Stadium to discard.
#[test]
fn test_palkia_spacial_rend_without_stadium_just_damages() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1038Palkia).with_energy(vec![
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Colorless,
        ])],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::C1038Palkia, 0),
        is_stack: false,
    });
    game.play_until_stable();
    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        250 - 70
    );
}

// Fork tests.

const DEWGONGS: [CardId; 2] = [CardId::C1033Dewgong, CardId::C1193Dewgong];
const PALKIAS: [CardId; 2] = [CardId::C1038Palkia, CardId::C1140Palkia];

fn snorlax() -> PlayedCard {
    // 150 HP, Basic, weak to [F].
    PlayedCard::from_id(CardId::A1211Snorlax)
}

fn bulbasaur() -> PlayedCard {
    // 70 HP, Basic, weak to [R].
    PlayedCard::from_id(CardId::A1001Bulbasaur)
}

fn squirtle() -> PlayedCard {
    // 60 HP, Basic, weak to [L].
    PlayedCard::from_id(CardId::A1053Squirtle)
}

/// Player 0's `dewgong` with `energy` uses Dual Blizzard on `defender` (the game of `seed`): the
/// target choice is then on the stack.
fn dual_blizzard(
    seed: u64,
    dewgong: CardId,
    energy: Vec<EnergyType>,
    defender: Vec<PlayedCard>,
) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        5,
        vec![PlayedCard::from_id(dewgong).with_energy(energy)],
        defender,
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(dewgong, 0),
        is_stack: false,
    });
    game
}

/// The queued target choices, sorted: whether each is queued as the attack's own damage
/// (`ApplyQueuedAttackDamage`, the coin path) rather than as `ApplyDamage`, and the damage and
/// in-play index of each of the opponent's Pokémon it hits.
fn queued_picks(game: &Game<'static>) -> Vec<(bool, Vec<(u32, usize)>)> {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let mut picks: Vec<(bool, Vec<(u32, usize)>)> = choices
        .iter()
        .map(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => {
                assert!(targets.iter().all(|(_, player, _)| *player == 1));
                (false, targets.iter().map(|&(damage, _, idx)| (damage, idx)).collect())
            }
            SimpleAction::ApplyQueuedAttackDamage { targets, .. } => {
                assert!(targets.iter().all(|(_, opponent, _)| *opponent));
                (true, targets.iter().map(|&(damage, _, idx)| (damage, idx)).collect())
            }
            other => panic!("not a Dual Blizzard target choice: {other:?}"),
        })
        .collect();
    picks.sort();
    picks
}

/// "Discard 2 [W] Energy from this Pokémon": both printings discard 2 [W] and nothing else; the
/// [L] and the third [W] stay attached.
#[test]
fn test_dual_blizzard_discards_two_water_energy_only() {
    for dewgong in DEWGONGS {
        let energy = vec![
            EnergyType::Lightning,
            EnergyType::Water,
            EnergyType::Water,
            EnergyType::Water,
        ];
        let mut game = dual_blizzard(0, dewgong, energy, vec![snorlax()]);
        game.play_until_stable();
        let state = game.get_state_clone();
        let left = &state.get_active(0).attached_energy;
        let count = |energy_type: EnergyType| left.iter().filter(|e| **e == energy_type).count();
        assert_eq!(
            (left.len(), count(EnergyType::Water), count(EnergyType::Lightning)),
            (2, 1, 1),
            "{dewgong:?}"
        );
        assert_eq!(state.discard_energies[0], vec![EnergyType::Water; 2], "{dewgong:?}");
        assert_eq!(state.get_active(1).get_remaining_hp(), 150 - 60, "{dewgong:?}");
    }
}

/// "2 of your opponent's Pokémon" with fewer than 3 in play: the one choice hits each of them, the
/// pair with 2 and the lone Active with 1 (rules/04: an effect does as much as it can, as Oceanic
/// Gift does with one Benched Pokémon).
#[test]
fn test_dual_blizzard_with_fewer_than_three_opposing_pokemon_has_one_choice() {
    for dewgong in DEWGONGS {
        let mut game = dual_blizzard(0, dewgong, vec![EnergyType::Water; 3], vec![snorlax(), bulbasaur()]);
        assert_eq!(queued_picks(&game), vec![(false, vec![(60, 0), (60, 1)])], "{dewgong:?}");
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        game.apply_action(&choices[0]);
        let state = game.get_state_clone();
        assert_eq!(
            (state.get_remaining_hp(1, 0), state.get_remaining_hp(1, 1)),
            (150 - 60, 70 - 60),
            "{dewgong:?}"
        );

        let game = dual_blizzard(0, dewgong, vec![EnergyType::Water; 3], vec![snorlax()]);
        assert_eq!(queued_picks(&game), vec![(false, vec![(60, 0)])], "{dewgong:?}");
    }
}

/// A pair that includes a Pokémon with a coin-flip damage Ability (Togekiss A4 080's Celestial
/// Blessing, Meowth B2 124's Carefree Steps) is queued as the attack's own damage
/// (`ApplyQueuedAttackDamage`, rules/09's Sept 30 repair, as for Volcanic Ash); the pair without
/// one is queued as `ApplyDamage`.
#[test]
fn test_dual_blizzard_queues_a_pair_with_a_coin_ability_as_the_attacks_own_damage() {
    for coin in [CardId::A4080Togekiss, CardId::B2124Meowth] {
        for dewgong in DEWGONGS {
            let game = dual_blizzard(
                0,
                dewgong,
                vec![EnergyType::Water; 3],
                vec![snorlax(), bulbasaur(), PlayedCard::from_id(coin)],
            );
            assert_eq!(
                queued_picks(&game),
                vec![
                    (false, vec![(60, 0), (60, 1)]),
                    (true, vec![(60, 0), (60, 2)]),
                    (true, vec![(60, 1), (60, 2)]),
                ],
                "{coin:?}, {dewgong:?}"
            );
        }
    }
}

/// Through the queued choice the chosen target's coin flips: over 60 seeds Togekiss (140 HP) is
/// sometimes untouched and sometimes at 80, Meowth (50 HP) sometimes untouched and sometimes Knocked
/// Out, while Snorlax beside it takes the 60 every time.
#[test]
fn test_dual_blizzard_flips_the_coin_of_a_chosen_target() {
    for (coin, hp) in [(CardId::A4080Togekiss, 140), (CardId::B2124Meowth, 50)] {
        let (mut prevented, mut hit) = (0, 0);
        for seed in 0..60u64 {
            let mut game = dual_blizzard(
                seed,
                CardId::C1033Dewgong,
                vec![EnergyType::Water; 3],
                vec![snorlax(), PlayedCard::from_id(coin)],
            );
            let (_, choices) = game.get_state_clone().generate_possible_actions();
            assert_eq!(choices.len(), 1);
            assert!(matches!(choices[0].action, SimpleAction::ApplyQueuedAttackDamage { .. }));
            game.apply_action(&choices[0]);
            // The attack's reactions settle before its Knock Out wave.
            game.play_until_stable();
            let state = game.get_state_clone();
            assert_eq!(state.get_remaining_hp(1, 0), 150 - 60, "seed {seed}: Snorlax");
            match state.in_play_pokemon[1][1].as_ref().map(|p| p.get_remaining_hp()) {
                Some(left) if left == hp => prevented += 1,
                Some(left) if left + 60 == hp => hit += 1,
                None if hp <= 60 => hit += 1,
                other => panic!("seed {seed}: {coin:?} at {other:?}"),
            }
        }
        assert!(prevented > 10 && hit > 10, "{coin:?}: {prevented} prevented, {hit} hit: the coin must flip");
    }
}

/// Player 0 plays Lorelei (C1 125), then Dewgong uses Dual Blizzard on `defender`.
fn lorelei_then_dual_blizzard(seed: u64, dewgong: CardId, defender: Vec<PlayedCard>) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        seed,
        0,
        5,
        vec![PlayedCard::from_id(dewgong).with_energy(vec![EnergyType::Water; 3])],
        defender,
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::C1125Lorelei)];
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(CardId::C1125Lorelei),
        },
        is_stack: false,
    });
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(dewgong, 0),
        is_stack: false,
    });
    game
}

/// Lorelei: "During this turn, attacks used by your Dewgong, Cloyster, or Lapras do +30 damage to
/// your opponent's Pokémon." Each of the 2 targets of every pair takes 90, Active or Benched, and the
/// third Pokémon nothing; through the coin path too, where Togekiss takes 0 or 90.
#[test]
fn test_lorelei_adds_30_to_each_dual_blizzard_target() {
    let full = [150, 150, 250];
    for dewgong in DEWGONGS {
        for pick in 0..3 {
            let mut game = lorelei_then_dual_blizzard(
                0,
                dewgong,
                vec![
                    snorlax(),
                    PlayedCard::from_id(CardId::A1129MewtwoEx),
                    PlayedCard::from_id(CardId::B4197WailordEx),
                ],
            );
            let (_, choices) = game.get_state_clone().generate_possible_actions();
            assert_eq!(choices.len(), 3);
            let hit: Vec<usize> = match &choices[pick].action {
                SimpleAction::ApplyDamage { targets, .. } => targets.iter().map(|&(_, _, idx)| idx).collect(),
                other => panic!("not a Dual Blizzard target choice: {other:?}"),
            };
            game.apply_action(&choices[pick]);
            let state = game.get_state_clone();
            for (idx, hp) in full.into_iter().enumerate() {
                let expected = if hit.contains(&idx) { 90 } else { 0 };
                assert_eq!(hp - state.get_remaining_hp(1, idx), expected, "{dewgong:?}, pick {hit:?}, slot {idx}");
            }
        }
    }

    let mut seen = std::collections::BTreeSet::new();
    for seed in 0..60u64 {
        let mut game = lorelei_then_dual_blizzard(
            seed,
            CardId::C1033Dewgong,
            vec![snorlax(), PlayedCard::from_id(CardId::A4080Togekiss)],
        );
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        assert!(matches!(
            choices.as_slice(),
            [Action { action: SimpleAction::ApplyQueuedAttackDamage { .. }, .. }]
        ));
        game.apply_action(&choices[0]);
        let state = game.get_state_clone();
        assert_eq!(state.get_remaining_hp(1, 0), 150 - 90, "seed {seed}: Snorlax");
        seen.insert(140 - state.get_remaining_hp(1, 1));
    }
    assert_eq!(seen, [0, 90].into_iter().collect(), "Togekiss: prevented, or 60 + 30");
}

/// Player 0's `palkia` (with [W][W][C]) and `own_bench` against `defender`, after
/// `stadium_player` has played Starting Plains (B2 154) from their hand, so every Basic in play
/// has its +20. It is player 0's turn when this returns.
fn after_starting_plains_played_by(
    stadium_player: usize,
    palkia: CardId,
    own_bench: Vec<PlayedCard>,
    defender: Vec<PlayedCard>,
) -> Game<'static> {
    let mut attacker = vec![PlayedCard::from_id(palkia).with_energy(vec![
        EnergyType::Water,
        EnergyType::Water,
        EnergyType::Colorless,
    ])];
    attacker.extend(own_bench);
    let mut game = get_test_game_with_board(attacker, defender);
    let mut state = game.get_state_clone();
    state.current_player = stadium_player;
    state.hands[stadium_player] = vec![get_card_by_enum(CardId::B2154StartingPlains)];
    game.set_state(state);
    game.apply_action(&Action {
        actor: stadium_player,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(CardId::B2154StartingPlains),
        },
        is_stack: false,
    });
    let mut state = game.get_state_clone();
    state.current_player = 0;
    game.set_state(state);
    game
}

fn spacial_rend(game: &mut Game<'static>, palkia: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(palkia, 0),
        is_stack: false,
    });
}

fn remaining(state: &State, player: usize, slots: &[usize]) -> Vec<u32> {
    slots.iter().map(|&idx| state.get_remaining_hp(player, idx)).collect()
}

/// Against the opponent's Starting Plains: the Stadium goes to the opponent's discard pile and every
/// Basic in play, on both sides, loses its +20 at once. The opponent's Bulbasaur (70 damage from
/// Spacial Rend on 70 HP) and Benched Squirtle (60 on 60) are Knocked Out and both points scored at
/// once; the Active was Knocked Out, so its owner is asked to promote (rules/02: removing an HP bonus).
#[test]
fn test_spacial_rend_discards_the_opponents_starting_plains_and_its_bonus_at_once() {
    let plains = get_card_by_enum(CardId::B2154StartingPlains);
    for palkia in PALKIAS {
        let mut game = after_starting_plains_played_by(
            1,
            palkia,
            vec![squirtle()],
            vec![
                bulbasaur(),
                squirtle().with_damage(60),
                PlayedCard::from_id(CardId::A1002Ivysaur),
                PlayedCard::from_id(CardId::C1032Seel),
            ],
        );
        let state = game.get_state_clone();
        assert_eq!(state.active_stadium_owner, Some(1));
        assert_eq!(remaining(&state, 0, &[0, 1]), vec![140, 80], "{palkia:?}: the attacker's Basics have the +20");
        assert_eq!(remaining(&state, 1, &[0, 1, 2, 3]), vec![90, 20, 90, 90], "{palkia:?}: Ivysaur is a Stage 1");

        spacial_rend(&mut game, palkia);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none() && state.active_stadium_owner.is_none(), "{palkia:?}");
        assert!(state.discard_piles[1].contains(&plains), "{palkia:?}: to the opponent's discard pile");
        assert!(!state.discard_piles[0].contains(&plains), "{palkia:?}");
        assert_eq!(remaining(&state, 0, &[0, 1]), vec![120, 60], "{palkia:?}: Palkia and Squirtle lose the +20");
        assert!(
            state.in_play_pokemon[1][0].is_none() && state.in_play_pokemon[1][1].is_none(),
            "{palkia:?}: Bulbasaur and the Benched Squirtle are Knocked Out"
        );
        assert_eq!(remaining(&state, 1, &[2, 3]), vec![90, 70], "{palkia:?}: Ivysaur keeps 90, Seel loses the +20");
        assert_eq!(state.points, [2, 0], "{palkia:?}: both points at once");

        let (actor, choices) = state.generate_possible_actions();
        assert_eq!(actor, 1, "{palkia:?}");
        let mut promotions: Vec<usize> = choices
            .iter()
            .map(|choice| match choice.action {
                SimpleAction::Promote { player: 1, in_play_idx } => in_play_idx,
                ref other => panic!("{palkia:?}: expected a promotion, got {other:?}"),
            })
            .collect();
        promotions.sort();
        assert_eq!(promotions, vec![2, 3], "{palkia:?}");
    }
}

/// Against its own player's Starting Plains: nothing is discarded and every Basic keeps its +20,
/// so the opponent's Bulbasaur survives Spacial Rend at 20 and the damaged Squirtle stays at 20.
#[test]
fn test_spacial_rend_keeps_your_own_starting_plains_and_its_bonus() {
    let plains = get_card_by_enum(CardId::B2154StartingPlains);
    for palkia in PALKIAS {
        let mut game =
            after_starting_plains_played_by(0, palkia, vec![], vec![bulbasaur(), squirtle().with_damage(60)]);
        assert_eq!(game.get_state_clone().active_stadium_owner, Some(0));
        spacial_rend(&mut game, palkia);
        let state = game.get_state_clone();
        assert_eq!(state.active_stadium, Some(plains.clone()), "{palkia:?}");
        assert_eq!(state.active_stadium_owner, Some(0), "{palkia:?}");
        assert!(!state.discard_piles[0].contains(&plains) && !state.discard_piles[1].contains(&plains));
        assert_eq!(remaining(&state, 0, &[0]), vec![140], "{palkia:?}");
        assert_eq!(remaining(&state, 1, &[0, 1]), vec![20, 20], "{palkia:?}");
        assert_eq!(state.points, [0, 0], "{palkia:?}");
    }
}

/// A Stadium with no recorded owner (as a legacy saved state reads it: `active_stadium_owner` is
/// `#[serde(default)]`) is not known to be the opponent's, so Spacial Rend leaves it, and Starting
/// Plains' +20 with it.
#[test]
fn test_spacial_rend_keeps_a_stadium_with_no_recorded_owner() {
    let plains = get_card_by_enum(CardId::B2154StartingPlains);
    for palkia in PALKIAS {
        let mut game =
            after_starting_plains_played_by(1, palkia, vec![], vec![bulbasaur(), squirtle().with_damage(60)]);
        let mut state = game.get_state_clone();
        state.active_stadium_owner = None;
        game.set_state(state);
        spacial_rend(&mut game, palkia);
        let state = game.get_state_clone();
        assert_eq!(state.active_stadium, Some(plains.clone()), "{palkia:?}");
        assert_eq!(state.active_stadium_owner, None, "{palkia:?}");
        assert!(!state.discard_piles[0].contains(&plains) && !state.discard_piles[1].contains(&plains));
        assert_eq!(remaining(&state, 0, &[0]), vec![140], "{palkia:?}");
        assert_eq!(remaining(&state, 1, &[0, 1]), vec![20, 20], "{palkia:?}");
        assert_eq!(state.points, [0, 0], "{palkia:?}");
    }
}

/// With no Stadium in play, Spacial Rend from either printing is just its 70: nothing is discarded.
#[test]
fn test_spacial_rend_without_a_stadium_from_either_printing_is_just_its_damage() {
    for palkia in PALKIAS {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(palkia).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Colorless,
            ])],
            vec![snorlax(), squirtle()],
        );
        spacial_rend(&mut game, palkia);
        let state = game.get_state_clone();
        assert!(state.active_stadium.is_none() && state.active_stadium_owner.is_none(), "{palkia:?}");
        assert!(state.discard_piles[0].is_empty() && state.discard_piles[1].is_empty(), "{palkia:?}");
        assert_eq!(remaining(&state, 1, &[0, 1]), vec![150 - 70, 60], "{palkia:?}");
    }
}

/// Both Dewgong and both Palkia printings are Complete, with no known limitation.
#[test]
fn test_dewgong_and_palkia_printings_report_complete() {
    for id in DEWGONGS.into_iter().chain(PALKIAS) {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
