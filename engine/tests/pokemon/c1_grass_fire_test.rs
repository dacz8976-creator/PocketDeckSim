// Ported from upstream deckgym-core #433 (tests/pokemon/c1_grass_fire_test.rs, as of e7cc5ce): the Sawsbuck, Amoonguss, Volcanion, Ceruledge, Venusaur and two Raboot tests (R8-04a and R8-04b), without the Ribombee and Vespiquen tests (later R8 commits), with fork tests added at the end (Rally Back through real Knock Outs; Jumping Coach on every Rabbit Jumping attacker, switched off, on other titles and sides, and under Victory Star and Will; the printings' status).
use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::{
        attack_action, get_initialized_game_with_board, get_test_game_with_board, nth_attack,
        play_trainer, trainer_from_id,
    },
    Game,
};
use rand::{rngs::StdRng, SeedableRng};

fn attack(game: &mut deckgym::Game<'static>, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

/// Sawsbuck - Leaf Litter Tackle: 100 damage, then discard a [G] Energy from this Pokémon.
#[test]
fn test_sawsbuck_leaf_litter_tackle_discards_a_grass_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1010Sawsbuck).with_energy(vec![
            EnergyType::Grass,
            EnergyType::Fire,
            EnergyType::Fire,
        ])],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    attack(&mut game, CardId::C1010Sawsbuck);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 150);
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Fire, EnergyType::Fire]
    );
    assert_eq!(state.discard_energies[0], vec![EnergyType::Grass]);
}
/// Amoonguss - Astonish: a random card from the opponent's hand is shuffled into their deck.
#[test]
fn test_amoonguss_astonish_shuffles_a_random_hand_card_back() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1012Amoonguss)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    let state = game.get_state_clone();
    let hand_before = state.hands[1].len();
    let deck_before = state.decks[1].cards.len();

    attack(&mut game, CardId::C1012Amoonguss);

    let state = game.get_state_clone();
    assert_eq!(state.hands[1].len(), hand_before - 1);
    assert_eq!(state.decks[1].cards.len(), deck_before + 1);
}
/// Volcanion - Dynamite Steam: flip 2 coins, 110 damage for each heads.
#[test]
fn test_volcanion_dynamite_steam_damage_scales_with_heads() {
    let mut seen = std::collections::BTreeSet::new();
    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::C1019Volcanion).with_energy(vec![
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Colorless,
                ]),
            ],
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        attack(&mut game, CardId::C1019Volcanion);
        let state = game.get_state_clone();
        seen.insert(250 - state.get_active(1).get_remaining_hp());
    }
    assert_eq!(seen, [0, 110, 220].into_iter().collect());
}
/// Ceruledge - Rally Back: +70 damage if one of our Pokémon was Knocked Out by an attack last turn.
#[test]
fn test_ceruledge_rally_back_adds_damage_after_a_knockout_last_turn() {
    for (knocked_out, expected_damage) in [(true, 140), (false, 70)] {
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::C1028Ceruledge).with_energy(vec![
                    EnergyType::Fire,
                    EnergyType::Fire,
                    EnergyType::Colorless,
                ]),
            ],
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        let mut state = game.get_state_clone();
        state.set_knocked_out_by_opponent_attack_last_turn(knocked_out);
        game.set_state(state);
        attack(&mut game, CardId::C1028Ceruledge);

        let state = game.get_state_clone();
        assert_eq!(
            250 - state.get_active(1).get_remaining_hp(),
            expected_damage
        );
    }
}

/// Venusaur - Sunny Heal: once during your turn, you may heal 30 damage from your Active Pokémon.
#[test]
fn test_venusaur_sunny_heal_heals_active_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50),
            PlayedCard::from_id(CardId::C1003Venusaur),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let ability = Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 1 },
        is_stack: false,
    };
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .contains(&ability));
    game.apply_action(&ability);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 70 - 50 + 30);
    assert!(!state.generate_possible_actions().1.contains(&ability));
}

/// Scorbunny's Rabbit Jumping: damage dealt over many seeds, with `raboots` benched.
fn rabbit_jumping_damages(raboots: Vec<CardId>) -> std::collections::BTreeSet<u32> {
    let mut seen = std::collections::BTreeSet::new();
    for seed in 0..300 {
        let mut board =
            vec![PlayedCard::from_id(CardId::C1022Scorbunny)
                .with_energy(vec![EnergyType::Colorless])];
        board.extend(raboots.iter().map(|id| PlayedCard::from_id(*id)));
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            board,
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        attack(&mut game, CardId::C1022Scorbunny);
        let state = game.get_state_clone();
        seen.insert(250 - state.get_active(1).get_remaining_hp());
    }
    seen
}

/// Raboot - Jumping Coach: Rabbit Jumping flips 3 more coins while a Raboot is in play.
#[test]
fn test_raboot_jumping_coach_adds_three_coins_to_rabbit_jumping() {
    assert_eq!(
        rabbit_jumping_damages(vec![]),
        [0, 20, 40].into_iter().collect()
    );
    // 5 coins, 20 damage per heads.
    assert_eq!(
        rabbit_jumping_damages(vec![CardId::C1023Raboot]),
        (0..=5).map(|heads| heads * 20).collect()
    );
}

/// Raboot - Jumping Coach: each Raboot in play adds 3 more coins (printings stack).
#[test]
fn test_two_raboots_stack_jumping_coach() {
    // 2 + 3 + 3 = 8 coins.
    let seen = rabbit_jumping_damages(vec![CardId::C1023Raboot, CardId::C1137Raboot]);
    assert!(seen.iter().all(|damage| damage % 20 == 0));
    assert!(seen.iter().max().unwrap() > &100);
    assert!(seen.iter().max().unwrap() <= &160);
}

// ---------------------------------------------------------------------------------------------
// Fork additions.
// ---------------------------------------------------------------------------------------------

fn ready_ceruledge() -> PlayedCard {
    PlayedCard::from_id(CardId::C1028Ceruledge).with_energy(vec![
        EnergyType::Fire,
        EnergyType::Fire,
        EnergyType::Colorless,
    ])
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    // The Pokémon Checkup, any promotion, and the next player's draw.
    game.play_until_stable();
}

/// Full flow for Rally Back, with no flag set by hand: the opponent (player 1) Knocks Out player 0's
/// Active Snorlax with Mega Latios ex's Sonic Impulse (160), player 0 promotes their only Benched
/// Pokémon, a ready Ceruledge, and player 1 ends the turn, so the Pokémon Checkup shifts the
/// knockout flag.
fn ceruledge_after_a_knock_out_by_an_attack() -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![PlayedCard::from_id(CardId::A1211Snorlax), ready_ceruledge()],
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![
                EnergyType::Water,
                EnergyType::Water,
                EnergyType::Psychic,
            ]),
        ],
    );
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::PB024MegaLatiosEx, 0),
        is_stack: false,
    });

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0, "player 0 should be promoting after the knockout");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);

    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 1, "player 1 should be ending their turn");
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);
    game.play_until_stable();

    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");
    game
}

/// Ceruledge - Rally Back: "If any of your Pokémon were Knocked Out by damage from an attack during
/// your opponent's last turn, this attack does 70 more damage." After a real Knock Out by the
/// opponent's attack: 70 + 70.
#[test]
fn test_ceruledge_rally_back_after_a_knock_out_by_the_opponents_attack() {
    let mut game = ceruledge_after_a_knock_out_by_an_attack();
    attack(&mut game, CardId::C1028Ceruledge);

    // Mega Latios ex (180 HP, no Weakness): 180 - 140 = 40.
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 40);
}

/// Rally Back reads only the opponent's last turn: Ceruledge waits a turn after the Knock Out, the
/// opponent's next turn knocks out nothing, and Rally Back does its printed 70.
#[test]
fn test_ceruledge_rally_back_ignores_a_knock_out_two_turns_ago() {
    let mut game = ceruledge_after_a_knock_out_by_an_attack();
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    assert_eq!(game.get_state_clone().current_player, 0);

    attack(&mut game, CardId::C1028Ceruledge);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 110);
}

/// A Knock Out that is not by damage from an attack does not count: player 0's Poisoned Snorlax
/// (10 HP left) is Knocked Out at the Pokémon Checkup that ends player 1's turn, and Rally Back
/// does its printed 70.
#[test]
fn test_ceruledge_rally_back_ignores_a_knock_out_by_poison() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax)
                .with_remaining_hp(10)
                .with_status_condition(StatusCondition::Poisoned),
            ready_ceruledge(),
        ],
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
    );
    end_turn(&mut game, 1);

    let state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    assert_eq!(state.points, [0, 1], "the Poison Knock Out scored for player 1");
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");

    attack(&mut game, CardId::C1028Ceruledge);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 110);
}

/// The printings R8-04a maps, the alt-art Venusaur and Ceruledge and Charizard's two
/// (charizard_flame_aura_test.rs) included: each is Complete, with no known limitation.
#[test]
fn test_mapped_c1_printings_report_complete() {
    for id in [
        CardId::C1003Venusaur,
        CardId::C1132Venusaur,
        CardId::C1010Sawsbuck,
        CardId::C1012Amoonguss,
        CardId::C1018Charizard,
        CardId::C1136Charizard,
        CardId::C1019Volcanion,
        CardId::C1028Ceruledge,
        CardId::C1138Ceruledge,
    ] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}

// Raboot - Jumping Coach: "As long as this Pokémon is in play, flip 3 more coins for the Rabbit
// Jumping attack used by your Pokémon." The exact forecast shows the coin count: a heads-count
// attack of N coins is N + 1 branches, one per number of heads, with the binomial probabilities.

/// A Wailord ex with 500 HP, so no number of heads Knocks it Out and the damage is 500 minus its HP.
fn coin_sponge() -> PlayedCard {
    PlayedCard::new(get_card_by_enum(CardId::B4197WailordEx), 0, 500, vec![], false, vec![])
}

/// The exact forecast of `action` in `state`, which must offer it: each branch's probability and the
/// damage it does to player 1's Active (`coin_sponge()`), sorted by damage.
fn branches_from(state: &deckgym::State, action: &Action) -> Vec<(f64, u32)> {
    assert!(
        state.generate_possible_actions().1.contains(action),
        "{:?} should be offered",
        action.action
    );
    let (probabilities, mutations) = try_forecast_action(state, action)
        .expect("the forecast should be exactly priced")
        .into_branches();
    let mut branches: Vec<(f64, u32)> = probabilities
        .into_iter()
        .zip(mutations)
        .map(|(probability, mutation)| {
            let mut next = state.clone();
            mutation(&mut StdRng::seed_from_u64(0), &mut next, action);
            (probability, 500 - next.get_active(1).get_remaining_hp())
        })
        .collect();
    branches.sort_by_key(|(_, damage)| *damage);
    branches
}

/// Player 0's Active uses `attack` on `board` (the attacker first), against `coin_sponge()` with
/// `opponent_bench` behind it: `branches_from` the start of the turn.
fn attack_branches(
    board: Vec<PlayedCard>,
    opponent_bench: Vec<PlayedCard>,
    attack: SimpleAction,
) -> Vec<(f64, u32)> {
    let mut opponent_board = vec![coin_sponge()];
    opponent_board.extend(opponent_bench);
    let game = get_initialized_game_with_board(0, 0, 3, board, opponent_board);
    let action = Action {
        actor: 0,
        action: attack,
        is_stack: false,
    };
    branches_from(&game.get_state_clone(), &action)
}

/// `branches` are `coins` coins for `per_head` damage each heads, the first `forced_heads` of them
/// heads (Will): one branch per number of heads, with its binomial probability.
fn assert_coins(branches: &[(f64, u32)], coins: u32, forced_heads: u32, per_head: u32) {
    let free = coins - forced_heads;
    let expected: Vec<(f64, u32)> = (0..=free)
        .map(|heads| {
            let ways = (0..heads).fold(1.0, |ways, i| ways * f64::from(free - i) / f64::from(i + 1));
            (ways / 2f64.powi(free as i32), (forced_heads + heads) * per_head)
        })
        .collect();
    assert_eq!(branches.len(), expected.len(), "{coins} coins: {branches:?}");
    for (&(probability, damage), &(expected_probability, expected_damage)) in
        branches.iter().zip(&expected)
    {
        assert_eq!(damage, expected_damage, "{coins} coins: {branches:?}");
        assert!(
            (probability - expected_probability).abs() < 1e-9,
            "{coins} coins: {branches:?}"
        );
    }
}

/// Jumping Coach adds its coins to every Rabbit Jumping on this fork's database, not only upstream's
/// Scorbunny: each printing flips 2 coins alone, 5 with one Raboot and 8 with two, whether those are
/// both printings or two copies of the same one (the coins are counted per Raboot in play).
#[test]
fn test_jumping_coach_adds_coins_to_every_rabbit_jumping_attacker() {
    let attackers = [
        (CardId::C1022Scorbunny, vec![EnergyType::Colorless], 20),
        (
            CardId::C1059Azumarill,
            vec![EnergyType::Psychic, EnergyType::Colorless],
            60,
        ),
        (CardId::C1115Buneary, vec![EnergyType::Colorless], 20),
        (CardId::C1116Lopunny, vec![EnergyType::Colorless], 40),
    ];
    for (attacker, energy, per_head) in attackers {
        assert_eq!(nth_attack(attacker, 0).title, "Rabbit Jumping");
        for (raboots, coins) in [
            (vec![], 2),
            (vec![CardId::C1023Raboot], 5),
            (vec![CardId::C1023Raboot, CardId::C1137Raboot], 8),
            (vec![CardId::C1023Raboot, CardId::C1023Raboot], 8),
        ] {
            let mut board = vec![PlayedCard::from_id(attacker).with_energy(energy.clone())];
            board.extend(raboots.iter().map(|id| PlayedCard::from_id(*id)));
            let branches = attack_branches(board, vec![], attack_action(attacker, 0));
            assert_coins(&branches, coins, 0, per_head);
        }
    }
}

/// Raboot over Scorbunny, as if it evolved in play, so Celebi's Time Recall ("Each of your evolved
/// Pokémon can use any attack from its previous Evolutions.") offers it Scorbunny's Rabbit Jumping.
fn raboot_over_scorbunny() -> PlayedCard {
    let mut raboot = PlayedCard::from_id(CardId::C1023Raboot).with_energy(vec![EnergyType::Fire]);
    raboot.cards_behind = vec![get_card_by_enum(CardId::C1022Scorbunny)];
    raboot
}

/// A Raboot whose Ability is switched off adds no coins. Prickly Powder's `NoAbilities` lands only on
/// the Defending Pokémon and lasts while it stays Active, so the route in play is an Active Raboot
/// using Scorbunny's Rabbit Jumping through Celebi's Time Recall. Its own Jumping Coach counts (it is
/// one of "your Pokémon") until it is switched off; a Benched Raboot still adds its 3.
#[test]
fn test_jumping_coach_switched_off_adds_no_coins() {
    let celebi = || PlayedCard::from_id(CardId::B3004Celebi);
    let powdered = || {
        let mut raboot = raboot_over_scorbunny();
        raboot.add_effect(CardEffect::NoAbilities, 1);
        raboot
    };
    for (board, coins) in [
        (vec![raboot_over_scorbunny(), celebi()], 5),
        (vec![powdered(), celebi()], 2),
        (
            vec![powdered(), celebi(), PlayedCard::from_id(CardId::C1137Raboot)],
            5,
        ),
    ] {
        let branches = attack_branches(board, vec![], attack_action(CardId::C1022Scorbunny, 0));
        assert_coins(&branches, coins, 0, 20);
    }
}

/// Jumping Coach is keyed on the attack's title, not its text: Buneary B1a 062's Double Kick prints
/// Rabbit Jumping's exact effect and still flips 2 coins with a Raboot in play. No Rabbit Jumping
/// reaches the Lucky Mittens path (`ExtraDamageForEachHeadsToolBoostedCoins`, only Ambipom B1 186's
/// Excited Tail), and a Raboot leaves Excited Tail at 2 coins, or 4 with Lucky Mittens.
#[test]
fn test_jumping_coach_ignores_attacks_with_other_titles() {
    let double_kick = nth_attack(CardId::B1a062Buneary, 0);
    assert_eq!(double_kick.title, "Double Kick");
    assert_eq!(
        double_kick.effect,
        nth_attack(CardId::C1115Buneary, 0).effect
    );
    let branches = attack_branches(
        vec![
            PlayedCard::from_id(CardId::B1a062Buneary).with_energy(vec![EnergyType::Colorless]),
            PlayedCard::from_id(CardId::C1023Raboot),
        ],
        vec![],
        attack_action(CardId::B1a062Buneary, 0),
    );
    assert_coins(&branches, 2, 0, 20);

    let ambipom =
        || PlayedCard::from_id(CardId::B1186Ambipom).with_energy(vec![EnergyType::Colorless]);
    for (attacker, coins) in [
        (ambipom(), 2),
        (
            ambipom().with_tool(get_card_by_enum(CardId::B1220LuckyMittens)),
            4,
        ),
    ] {
        let branches = attack_branches(
            vec![attacker, PlayedCard::from_id(CardId::C1023Raboot)],
            vec![],
            attack_action(CardId::B1186Ambipom, 0),
        );
        assert_coins(&branches, coins, 0, 30);
    }
}

/// "Used by your Pokémon": Raboot on the opponent's Bench add no coins to player 0's Rabbit Jumping.
#[test]
fn test_an_opponents_raboot_adds_no_coins() {
    let branches = attack_branches(
        vec![PlayedCard::from_id(CardId::C1022Scorbunny).with_energy(vec![EnergyType::Colorless])],
        vec![
            PlayedCard::from_id(CardId::C1023Raboot),
            PlayedCard::from_id(CardId::C1137Raboot),
        ],
        attack_action(CardId::C1022Scorbunny, 0),
    );
    assert_coins(&branches, 2, 0, 20);
}

/// Victini's Victory Star ("after you flip any coins for an attack of 1 of your [R] Pokémon, you may
/// ignore all results of those coin flips and begin flipping those coins again") sees Jumping Coach's
/// coins: Scorbunny's Rabbit Jumping with a Raboot in play pauses on a 5-coin batch, Reroll flips 5
/// coins again, and Keep commits 20 damage for each heads of the batch.
#[test]
fn test_victory_star_replaces_rabbit_jumpings_five_coins() {
    let rabbit_jumping = Action {
        actor: 0,
        action: attack_action(CardId::C1022Scorbunny, 0),
        is_stack: false,
    };
    let reroll = Action {
        actor: 0,
        action: SimpleAction::RerollAttackCoins {
            victory_star_in_play_idx: 1,
        },
        is_stack: true,
    };
    let keep = Action {
        actor: 0,
        action: SimpleAction::KeepAttackCoinResults,
        is_stack: true,
    };
    for seed in 0..10 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::C1022Scorbunny)
                    .with_energy(vec![EnergyType::Colorless]),
                PlayedCard::from_id(CardId::B3025Victini),
                PlayedCard::from_id(CardId::C1023Raboot),
            ],
            vec![coin_sponge()],
        );
        game.apply_action(&rabbit_jumping);
        let paused = game.get_state_clone();
        let pending = paused
            .pending_attack_coin_choice
            .clone()
            .expect("Victory Star should pause Rabbit Jumping");
        assert_eq!(pending.flips.len(), 5, "seed {seed}");
        assert_eq!(pending.victory_star_in_play_idx, 1);
        assert_coins(&branches_from(&paused, &reroll), 5, 0, 20);

        game.apply_action(&keep);
        let heads = pending.flips.iter().filter(|heads| **heads).count() as u32;
        assert_eq!(
            500 - game.get_state_clone().get_active(1).get_remaining_hp(),
            20 * heads,
            "seed {seed}"
        );
    }
}

/// Will ("the first coin flip will definitely be heads") sees Jumping Coach's coins too: with a Raboot
/// in play, Rabbit Jumping flips 5 coins and the first of them is heads.
#[test]
fn test_will_forces_the_first_of_rabbit_jumpings_five_coins() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::C1022Scorbunny).with_energy(vec![EnergyType::Colorless]),
            PlayedCard::from_id(CardId::C1023Raboot),
        ],
        vec![coin_sponge()],
    );
    let will = trainer_from_id(CardId::A4156Will);
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(will.clone()));
    game.set_state(state);
    play_trainer(&mut game, 0, will);

    let rabbit_jumping = Action {
        actor: 0,
        action: attack_action(CardId::C1022Scorbunny, 0),
        is_stack: false,
    };
    assert_coins(
        &branches_from(&game.get_state_clone(), &rabbit_jumping),
        5,
        1,
        20,
    );
}

/// Both Raboot printings are Complete, with no known limitation.
#[test]
fn test_raboot_printings_report_complete() {
    for id in [CardId::C1023Raboot, CardId::C1137Raboot] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
