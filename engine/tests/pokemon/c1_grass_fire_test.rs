// Ported from upstream deckgym-core #433 (tests/pokemon/c1_grass_fire_test.rs, as of e7cc5ce): all its tests, as upstream wrote them: the Sawsbuck, Amoonguss, Volcanion, Ceruledge, Venusaur and two Raboot tests (R8-04a and R8-04b), and the Ribombee and Vespiquen tests (R8-07b). Fork tests are added at the end (Rally Back through real Knock Outs; Jumping Coach on every Rabbit Jumping attacker, switched off, on other titles and sides, and under Victory Star and Will; Honey Gather's rental card played, discarded, retrieved and shuffled in, not offered at 10 cards, once per Ribombee, switched off, seen by the opponent's observation, knowledge, list sampler and bots; Honey Rush by name with a rental copy, at 0 against Weakness, its reveal not recorded; the printings' status).
use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_support::SupportReport,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    observation::{canonical_actions, INFORMATION_MODEL},
    players::{create_players, PlayerCode},
    state::MistySourceRoute,
    test_support::{
        attack_action, get_initialized_game_with_board, get_test_game_with_board, nth_attack,
        play_trainer, trainer_from_id,
    },
    Deck, Game, State,
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

/// Ribombee - Honey Gather: once during your turn, put a Sweet Honey rental card into your hand.
#[test]
fn test_ribombee_honey_gather_puts_sweet_honey_in_hand_once_per_turn() {
    for ribombee in [CardId::C1015Ribombee, CardId::C1135Ribombee] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(ribombee)],
            vec![PlayedCard::from_id(CardId::A1211Snorlax)],
        );
        let hand_before = game.get_state_clone().hands[0].len();
        let deck_before = game.get_state_clone().decks[0].cards.len();

        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });

        let state = game.get_state_clone();
        assert_eq!(state.hands[0].len(), hand_before + 1);
        assert_eq!(state.decks[0].cards.len(), deck_before);
        assert_eq!(
            state.hands[0].last().unwrap().get_name(),
            "Sweet Honey",
            "a Sweet Honey is added to the hand"
        );
        let (_, actions) = state.generate_possible_actions();
        assert!(
            !actions
                .iter()
                .any(|a| matches!(a.action, SimpleAction::UseAbility { .. })),
            "Honey Gather is once per turn"
        );
    }
}

/// Vespiquen - Honey Rush: reveal all of the Sweet Honey in your hand; 50 damage for each.
#[test]
fn test_vespiquen_honey_rush_does_50_per_sweet_honey_in_hand() {
    for (honey_count, expected_damage) in [(0usize, 0u32), (1, 50), (3, 150)] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::C1008Vespiquen)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
            vec![PlayedCard::from_id(CardId::B4197WailordEx)],
        );
        let mut state = game.get_state_clone();
        state.hands[0] = vec![deckgym::database::get_card_by_enum(CardId::A1001Bulbasaur)];
        for _ in 0..honey_count {
            state.hands[0].push(deckgym::database::get_card_by_enum(CardId::C1119SweetHoney));
        }
        game.set_state(state);

        attack(&mut game, CardId::C1008Vespiquen);

        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(1).get_remaining_hp(),
            250 - expected_damage,
            "{honey_count} Sweet Honey in hand"
        );
        assert_eq!(
            state.hands[0].len(),
            honey_count + 1,
            "revealed cards stay in hand"
        );
    }
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

// Ribombee - Honey Gather (C1 015 / C1 135): "Once during your turn, you may use this Ability. Put a Sweet Honey
// rental card into your hand." The rental card is a C1 119 Sweet Honey for every rule; played, it goes to the discard
// pile like any Item (Dustin's clip 11-23-18 at 02:50).

fn use_ability(actor: usize, in_play_idx: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::UseAbility { in_play_idx },
        is_stack: false,
    }
}

fn offered(game: &Game<'static>, action: &Action) -> bool {
    game.get_state_clone().generate_possible_actions().1.contains(action)
}

fn sweet_honey() -> Card {
    get_card_by_enum(CardId::C1119SweetHoney)
}

/// `actor` plays a C1 119 Sweet Honey from their hand (a rental card is one).
fn play_sweet_honey(actor: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(CardId::C1119SweetHoney),
        },
        is_stack: false,
    }
}

fn sweet_honey_target(actor: usize, in_play_idx: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::ChooseSweetHoneyTarget { in_play_idx },
        is_stack: true,
    }
}

/// `player`'s hand becomes `hand` and their discard pile is emptied.
fn set_hand(game: &mut Game<'static>, player: usize, hand: &[CardId]) {
    let mut state = game.get_state_clone();
    state.hands[player] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
    state.discard_piles[player].clear();
    game.set_state(state);
}

fn remaining_hp(state: &State, player: usize, in_play_idx: usize) -> u32 {
    state.in_play_pokemon[player][in_play_idx]
        .as_ref()
        .unwrap()
        .get_remaining_hp()
}

/// `player`'s hand and deck, the cards an opponent can't see.
fn hidden(state: &State, player: usize) -> impl Iterator<Item = &Card> {
    state.hands[player].iter().chain(&state.decks[player].cards)
}

/// Honey Gather's rental card is a C1 119 Sweet Honey (`get_card_by_enum`, as upstream) that comes from no zone: the
/// deck and discard pile are untouched. It plays exactly as one: the damaged Ribombee is the only target, offered
/// before any coin, with nothing healed until it is chosen; then 20 per heads, up to the damage. Once played it is in
/// the discard pile, like any Item. Both Ribombee printings, 8 seeds each.
#[test]
fn test_honey_gathers_rental_card_plays_as_a_sweet_honey_and_is_discarded() {
    for ribombee in [CardId::C1015Ribombee, CardId::C1135Ribombee] {
        for seed in 0..8 {
            let ctx = format!("{ribombee:?}, seed {seed}");
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                3,
                vec![
                    PlayedCard::from_id(CardId::A1001Bulbasaur),
                    PlayedCard::from_id(ribombee).with_damage(30),
                ],
                vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            );
            set_hand(&mut game, 0, &[]);
            let before = game.get_state_clone();
            assert!(offered(&game, &use_ability(0, 1)), "{ctx}");
            game.apply_action(&use_ability(0, 1));
            let state = game.get_state_clone();
            assert_eq!(state.hands[0], vec![sweet_honey()], "{ctx}");
            assert_eq!(state.decks[0].cards, before.decks[0].cards, "{ctx}");
            assert!(state.discard_piles[0].is_empty(), "{ctx}");

            assert!(offered(&game, &play_sweet_honey(0)), "{ctx}");
            game.apply_action(&play_sweet_honey(0));
            let staged = game.get_state_clone();
            assert!(
                matches!(
                    staged
                        .pending_misty_target_choice
                        .as_ref()
                        .and_then(|pending| pending.route.as_ref()),
                    Some(MistySourceRoute::SweetHoney { .. })
                ),
                "{ctx}"
            );
            assert!(staged.pending_trainer_coin_choice.is_none(), "{ctx}");
            assert_eq!(
                staged.generate_possible_actions().1,
                vec![sweet_honey_target(0, 1)],
                "{ctx}: the undamaged Bulbasaur is not offered"
            );
            assert_eq!(remaining_hp(&staged, 0, 1), 40, "{ctx}");
            assert!(staged.hands[0].is_empty(), "{ctx}");
            assert_eq!(staged.discard_piles[0], vec![sweet_honey()], "{ctx}");

            game.apply_action(&sweet_honey_target(0, 1));
            let state = game.get_state_clone();
            let healed = remaining_hp(&state, 0, 1) - 40;
            assert!([0, 20, 30].contains(&healed), "{ctx}: healed {healed}");
            assert!(state.pending_misty_target_choice.is_none(), "{ctx}");
            assert!(state.move_generation_stack.is_empty(), "{ctx}");
            assert_eq!(state.discard_piles[0], vec![sweet_honey()], "{ctx}");
        }
    }
}

/// Honey Gather's own gate doesn't look at damage, but its card does: with no damaged Pokémon the rental card sits in
/// the hand unplayable, as a Sweet Honey would (rules/05 #28).
#[test]
fn test_a_rental_card_needs_a_damaged_pokemon() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1015Ribombee)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    set_hand(&mut game, 0, &[]);
    assert!(offered(&game, &use_ability(0, 0)));
    game.apply_action(&use_ability(0, 0));
    assert_eq!(game.get_state_clone().hands[0], vec![sweet_honey()]);
    assert!(!offered(&game, &play_sweet_honey(0)));
}

/// Not offered while the hand holds 10 cards (Dustin: "fairly confident" it won't work there; not filmed, so it is in
/// Ribombee's limitation line). The fork's hand limit is 10: draws and deck searches stop there (`maybe_draw_card`,
/// `card_search_outcomes_with_filter_multiple`), and a draw Ability stays offered and skips the draw, but this one is
/// not offered. At 9 both Ribombee offer it, and the first fills the hand to 10, which takes the second's offer away; at
/// 10, or at 11 after an uncapped transfer (a discard retrieval, Team Rocket's Researcher), neither does. Applied at 10
/// anyway, it adds nothing, as a draw does.
#[test]
fn test_honey_gather_is_not_offered_at_10_cards_in_hand() {
    let with_hand = |cards: usize| {
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::C1015Ribombee),
                PlayedCard::from_id(CardId::C1135Ribombee),
            ],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        set_hand(&mut game, 0, &vec![CardId::PA001Potion; cards]);
        game
    };
    let mut game = with_hand(9);
    assert!(offered(&game, &use_ability(0, 0)) && offered(&game, &use_ability(0, 1)));
    game.apply_action(&use_ability(0, 0));
    assert_eq!(game.get_state_clone().hands[0].len(), 10);
    assert!(!offered(&game, &use_ability(0, 1)), "the 10th card takes the offer away");

    for cards in [10, 11] {
        let game = with_hand(cards);
        assert!(!offered(&game, &use_ability(0, 0)), "{cards} cards");
        assert!(!offered(&game, &use_ability(0, 1)), "{cards} cards");
    }

    let mut game = with_hand(10);
    game.apply_action(&use_ability(0, 0));
    assert_eq!(
        game.get_state_clone().hands[0],
        vec![get_card_by_enum(CardId::PA001Potion); 10]
    );
}

/// "Once during your turn", per Ribombee: one of each printing put two rental cards into the hand in one turn, neither
/// offers it twice, and both offer it again on their owner's next turn.
#[test]
fn test_each_ribombee_gathers_once_per_turn() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::C1015Ribombee),
            PlayedCard::from_id(CardId::C1135Ribombee),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    set_hand(&mut game, 0, &[]);
    game.apply_action(&use_ability(0, 0));
    assert!(!offered(&game, &use_ability(0, 0)));
    assert!(offered(&game, &use_ability(0, 1)));
    game.apply_action(&use_ability(0, 1));
    assert_eq!(game.get_state_clone().hands[0], vec![sweet_honey(), sweet_honey()]);
    assert!(!offered(&game, &use_ability(0, 0)) && !offered(&game, &use_ability(0, 1)));

    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    assert_eq!(game.get_state_clone().current_player, 0);
    assert!(offered(&game, &use_ability(0, 0)) && offered(&game, &use_ability(0, 1)));
}

/// Switched off like every activated Ability (`abilities_switched_off`): a Ribombee with Prickly Powder's
/// `NoAbilities` doesn't offer it, while a Benched Ribombee does. Alolan Muk's Power of Alchemy (B2 097) reaches Basic
/// Pokémon only, and Ribombee is a Stage 1, so it still offers it there.
#[test]
fn test_honey_gather_is_switched_off_by_no_abilities() {
    let mut powdered = PlayedCard::from_id(CardId::C1015Ribombee);
    powdered.add_effect(CardEffect::NoAbilities, 1);
    let mut game = get_test_game_with_board(
        vec![powdered, PlayedCard::from_id(CardId::C1135Ribombee)],
        vec![PlayedCard::from_id(CardId::B2097AlolanMuk)],
    );
    set_hand(&mut game, 0, &[]);
    assert!(!offered(&game, &use_ability(0, 0)));
    assert!(offered(&game, &use_ability(0, 1)));
}

/// A played rental card is in the discard pile as an ordinary Item: Team Rocket's Slowpoke's Scavenge ("Put a random
/// Item card from your discard pile into your hand.") takes it back, a Sweet Honey like any other.
#[test]
fn test_a_played_rental_card_is_retrieved_like_any_item() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B4a025TeamRocketsSlowpoke)
                .with_energy(vec![EnergyType::Psychic]),
            PlayedCard::from_id(CardId::C1015Ribombee).with_damage(30),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    set_hand(&mut game, 0, &[]);
    game.apply_action(&use_ability(0, 1));
    game.apply_action(&play_sweet_honey(0));
    game.apply_action(&sweet_honey_target(0, 1));
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.discard_piles[0], vec![sweet_honey()]);

    attack(&mut game, CardId::B4a025TeamRocketsSlowpoke);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![sweet_honey()]);
    assert!(state.discard_piles[0].is_empty());
}

/// A rental card shuffled into a deck by another effect stays there as an ordinary Sweet Honey and can be drawn again
/// (upstream's reading; not filmed, so it is in Ribombee's limitation line). Player 1's Honey Gather puts it into an
/// otherwise empty hand, so player 0's Amoonguss's Astonish ("Look at a random card from your opponent's hand and
/// shuffle it into their deck.") can only take that card; with player 1's deck empty before, their next draw is that
/// Sweet Honey, which then plays as one on the Ribombee Astonish damaged.
#[test]
fn test_a_rental_card_shuffled_into_the_deck_stays_a_sweet_honey() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![PlayedCard::from_id(CardId::C1012Amoonguss)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::C1015Ribombee)],
    );
    let mut state = game.get_state_clone();
    state.hands[1].clear();
    state.decks[1].cards.clear();
    game.set_state(state);
    game.apply_action(&use_ability(1, 0));
    assert_eq!(game.get_state_clone().hands[1], vec![sweet_honey()]);
    end_turn(&mut game, 1);

    attack(&mut game, CardId::C1012Amoonguss);
    let state = game.get_state_clone();
    assert!(state.hands[1].is_empty());
    assert_eq!(state.decks[1].cards, vec![sweet_honey()]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 20);

    end_turn(&mut game, 0);
    let state = game.get_state_clone();
    assert_eq!(state.current_player, 1);
    assert_eq!(state.hands[1], vec![sweet_honey()], "drawn again");
    assert!(state.decks[1].cards.is_empty());
    assert!(offered(&game, &play_sweet_honey(1)));
    game.apply_action(&play_sweet_honey(1));
    assert_eq!(
        game.get_state_clone().generate_possible_actions().1,
        vec![sweet_honey_target(1, 0)]
    );
    game.apply_action(&sweet_honey_target(1, 0));
    assert_eq!(game.get_state_clone().discard_piles[1], vec![sweet_honey()]);
}

/// The opponent's view of a rental card, which R8 adds no knowledge for (INFORMATION_MODEL stays v8). Player 1 holds
/// Ribombee; player 0 sees one more Unknown hand card after Honey Gather. Player 0's list-sampled search state
/// (`search_state_with_opponent_list`, b-tier's) takes the visible cards out of the list, fills the hand before the
/// deck, and leaves Unknown what the list can't fill. Counted over player 1's hand and deck together, from a state
/// whose hidden cards are exactly the list's: with a list holding no Sweet Honey, 0 Unknown before Honey Gather, 1 with
/// the rental card in hand, and 0 once it is played (the discarded card matches nothing in the list); with a list
/// holding one C1 119, and that card in the deck, 0, 1 and 1, and after the play no Sweet Honey among the sampled
/// cards, since the discarded rental card took the list's copy: the real one is under-counted. No panic.
#[test]
fn test_the_opponents_list_sampler_with_a_rental_card() {
    let hand = [CardId::A1001Bulbasaur, CardId::PA001Potion];
    for list_has_sweet_honey in [false, true] {
        let mut deck = vec![
            CardId::A1033Charmander,
            CardId::A1053Squirtle,
            CardId::A1001Bulbasaur,
            CardId::PA001Potion,
        ];
        if list_has_sweet_honey {
            deck.push(CardId::C1119SweetHoney);
        }
        let mut list = Deck::default();
        list.cards = std::iter::once(CardId::C1015Ribombee)
            .chain(hand)
            .chain(deck.iter().copied())
            .map(get_card_by_enum)
            .collect();
        let mut game = get_initialized_game_with_board(
            0,
            1,
            4,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::C1015Ribombee).with_damage(30)],
        );
        let mut state = game.get_state_clone();
        state.hands[1] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        state.decks[1].cards = deck.iter().map(|id| get_card_by_enum(*id)).collect();
        state.discard_piles[1].clear();
        game.set_state(state);

        let check = |game: &Game<'static>, unknown: usize, step: &str| {
            let ctx = format!("list has Sweet Honey {list_has_sweet_honey}, {step}");
            let observation = game.observation(0);
            for seed in 0..8 {
                let sampled = observation
                    .search_state_with_opponent_list(&mut StdRng::seed_from_u64(seed), &list);
                let unknowns = hidden(&sampled, 1).filter(|card| **card == Card::Unknown).count();
                assert_eq!(unknowns, unknown, "{ctx}, seed {seed}");
                if step == "played" {
                    let honey = hidden(&sampled, 1).filter(|card| card.get_name() == "Sweet Honey").count();
                    assert_eq!(honey, 0, "{ctx}, seed {seed}");
                }
            }
        };
        check(&game, 0, "before");
        game.apply_action(&use_ability(1, 0));
        assert_eq!(
            game.observation(0).visible_state().hands[1],
            vec![Card::Unknown; 3]
        );
        check(&game, 1, "in hand");
        game.apply_action(&play_sweet_honey(1));
        game.apply_action(&sweet_honey_target(1, 0));
        assert_eq!(game.get_state_clone().discard_piles[1], vec![sweet_honey()]);
        check(&game, usize::from(list_has_sweet_honey), "played");
    }
}

/// The bots with a rental card in a hand, without panic, each picking an offered action: km3 and WeightedRandomPlayer
/// for the holder at the main phase (Sweet Honey playable on the damaged Ribombee) and at its target; then, with the
/// holder's turn ended and the card still in hand, km3 and the list-aware b3 (sampling the holder's hidden cards from
/// their list) for the opponent.
#[test]
fn test_bots_decide_with_a_rental_card_in_a_hand() {
    let hand = [CardId::A1001Bulbasaur, CardId::PA001Potion];
    let deck = [
        CardId::A1033Charmander,
        CardId::A1053Squirtle,
        CardId::A1001Bulbasaur,
        CardId::PA001Potion,
    ];
    let mut list = Deck::default();
    list.cards = std::iter::once(CardId::C1015Ribombee)
        .chain(hand)
        .chain(deck)
        .map(get_card_by_enum)
        .collect();
    let holder_after_gather = || {
        let mut game = get_initialized_game_with_board(
            3,
            1,
            4,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![PlayedCard::from_id(CardId::C1015Ribombee).with_damage(30)],
        );
        let mut state = game.get_state_clone();
        state.hands[1] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        state.decks[1].cards = deck.iter().map(|id| get_card_by_enum(*id)).collect();
        game.set_state(state);
        game.apply_action(&use_ability(1, 0));
        game
    };
    // Player 0's opponent list is player 1's (`create_players` gives each player the other's deck).
    let decide = |game: &Game<'static>, code: &PlayerCode| {
        let (actor, mut actions) = game.get_state_clone().generate_possible_actions();
        canonical_actions(&mut actions);
        let mut players = create_players(Deck::default(), list.clone(), vec![code.clone(), code.clone()]);
        let chosen = players[actor].decision_fn(
            &mut StdRng::seed_from_u64(7),
            &game.observation(actor),
            &actions,
        );
        assert!(actions.contains(&chosen), "{code:?} chose {chosen:?}");
        (actor, chosen)
    };
    for code in [PlayerCode::KM { max_depth: 3 }, PlayerCode::W] {
        let mut game = holder_after_gather();
        assert_eq!(decide(&game, &code).0, 1);
        game.apply_action(&play_sweet_honey(1));
        let (actor, chosen) = decide(&game, &code);
        assert_eq!((actor, chosen), (1, sweet_honey_target(1, 0)), "{code:?}");
    }
    for code in [
        PlayerCode::KM { max_depth: 3 },
        PlayerCode::B {
            max_depth: 3,
            opponent_ply: 0,
            samples: 1,
        },
    ] {
        let mut game = holder_after_gather();
        end_turn(&mut game, 1);
        let state = game.get_state_clone();
        assert_eq!(state.current_player, 0);
        assert!(state.hands[1].contains(&sweet_honey()), "{code:?}");
        assert_eq!(decide(&game, &code).0, 0, "{code:?}");
    }
}

/// Knowledge around Honey Gather, which R8 leaves as it was (observation.rs `update_knowledge`): the card goes into
/// its holder's hand, so the opponent's knowledge of that hand (player 1's Hand Scope) is cleared, as for any change to
/// it, while deck tops known from Pokédex (player 1's own; player 0's own, before a second Honey Gather) are kept, since
/// no deck changes and the Ability's text has no "shuffle".
#[test]
fn test_honey_gather_clears_the_opponents_hand_knowledge_and_keeps_deck_tops() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::C1015Ribombee),
            PlayedCard::from_id(CardId::C1135Ribombee),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::PA004PokedEx)];
    state.hands[1] = vec![
        get_card_by_enum(CardId::PA004PokedEx),
        get_card_by_enum(CardId::PA003HandScope),
    ];
    game.set_state(state);
    play_trainer(&mut game, 1, trainer_from_id(CardId::PA004PokedEx));
    play_trainer(&mut game, 1, trainer_from_id(CardId::PA003HandScope));
    end_turn(&mut game, 1);
    let known = game.observation(1).revealed;
    assert_eq!(known.opponent_hand, vec![get_card_by_enum(CardId::PA004PokedEx)]);
    assert_eq!(known.deck_top[1].len(), 3);

    game.apply_action(&use_ability(0, 0));
    let after = game.observation(1).revealed;
    assert!(after.opponent_hand.is_empty(), "the hand changed");
    assert_eq!(after.deck_top, known.deck_top);
    assert_eq!(after.opponent_deck_membership, known.opponent_deck_membership);

    play_trainer(&mut game, 0, trainer_from_id(CardId::PA004PokedEx));
    let own_top = game.observation(0).revealed.deck_top[0].clone();
    assert_eq!(own_top.len(), 3);
    game.apply_action(&use_ability(0, 1));
    assert_eq!(game.observation(0).revealed.deck_top[0], own_top);
}

// Vespiquen - Honey Rush (C1 008): "Reveal all of the Sweet Honey in your hand, and this attack does 50 damage for
// each card you revealed in this way."

fn honey_rush() -> Action {
    Action {
        actor: 0,
        action: attack_action(CardId::C1008Vespiquen, 0),
        is_stack: false,
    }
}

fn ready_vespiquen() -> PlayedCard {
    PlayedCard::from_id(CardId::C1008Vespiquen).with_energy(vec![EnergyType::Grass, EnergyType::Grass])
}

/// Honey Rush counts by name: both printings and a rental copy from a Benched Ribombee's Honey Gather each count 50,
/// other cards (a Potion, a Misty) don't, and the printed 50 is not added on top. The forecast is one exact branch, and
/// the revealed cards stay in hand.
#[test]
fn test_honey_rush_counts_every_sweet_honey_in_hand_by_name() {
    for (hand, damage) in [
        (vec![CardId::PA001Potion, CardId::A1220Misty], 50),
        (vec![CardId::C1119SweetHoney, CardId::PA001Potion], 100),
        (vec![CardId::C1119SweetHoney, CardId::C1152SweetHoney], 150),
    ] {
        let mut game = get_test_game_with_board(
            vec![ready_vespiquen(), PlayedCard::from_id(CardId::C1015Ribombee)],
            vec![coin_sponge()],
        );
        set_hand(&mut game, 0, &hand);
        game.apply_action(&use_ability(0, 1));
        let state = game.get_state_clone();
        assert_eq!(branches_from(&state, &honey_rush()), vec![(1.0, damage)], "{hand:?}");

        attack(&mut game, CardId::C1008Vespiquen);
        let after = game.get_state_clone();
        assert_eq!(500 - after.get_active(1).get_remaining_hp(), damage, "{hand:?}");
        assert_eq!(after.hands[0], state.hands[0], "{hand:?}: the revealed cards stay in hand");
    }
}

/// With no Sweet Honey in hand Honey Rush does 0, and a Grass-weak defender takes no +20 (rules/05 #11, settled: an
/// attack whose own damage is 0 does 0); with one it does 50 + 20. Sandslash A1 138, 100 HP, weak to [G].
#[test]
fn test_honey_rush_with_no_sweet_honey_does_nothing_even_against_weakness() {
    for (hand, remaining) in [
        (vec![CardId::PA001Potion], 100),
        (vec![CardId::C1119SweetHoney], 30),
    ] {
        let mut game = get_test_game_with_board(
            vec![ready_vespiquen()],
            vec![PlayedCard::from_id(CardId::A1138Sandslash)],
        );
        set_hand(&mut game, 0, &hand);
        attack(&mut game, CardId::C1008Vespiquen);
        assert_eq!(
            game.get_state_clone().get_active(1).get_remaining_hp(),
            remaining,
            "{hand:?}"
        );
    }
}

/// The reveal is not recorded: recording it would be a knowledge-model change, and R8 keeps INFORMATION_MODEL at v8.
/// After Honey Rush there is no private or public reveal record, the opponent's knowledge is what it was (nothing of the
/// attacker's hand) and its view of that hand is all Unknown, as after Puppy Pile's reveal.
#[test]
fn test_honey_rushs_reveal_is_not_recorded() {
    let mut game = get_test_game_with_board(vec![ready_vespiquen()], vec![coin_sponge()]);
    set_hand(
        &mut game,
        0,
        &[CardId::C1119SweetHoney, CardId::C1152SweetHoney, CardId::PA001Potion],
    );
    let before = game.observation(1).revealed;
    attack(&mut game, CardId::C1008Vespiquen);
    assert_eq!(500 - game.get_state_clone().get_active(1).get_remaining_hp(), 100);
    assert!(game.private_reveal_history().is_empty());
    assert!(game.public_reveal_history().is_empty());
    let observation = game.observation(1);
    assert_eq!(observation.revealed, before);
    assert!(observation.revealed.opponent_hand.is_empty());
    assert_eq!(observation.visible_state().hands[0], vec![Card::Unknown; 3]);
    assert_eq!(observation.information_model, "closed-counts-unpriced-v8");
    assert_eq!(INFORMATION_MODEL, "closed-counts-unpriced-v8");
}

/// Vespiquen C1 008 is Complete. Both Ribombee printings are RulesUnverified with the same single limitation line, which
/// names the two unfilmed cases (the 10-card hand, a rental card shuffled into a deck), and the card-support preflight
/// allows them, as it allows every RulesUnverified card.
#[test]
fn test_vespiquen_and_ribombee_printings_status() {
    assert_eq!(
        get_implementation_status(CardId::C1008Vespiquen),
        ImplementationStatus::Complete
    );
    assert!(implementation_limitations(CardId::C1008Vespiquen).is_empty());
    let lines = implementation_limitations(CardId::C1015Ribombee);
    assert_eq!(lines.len(), 1);
    assert!(lines[0].contains("not offered while the hand holds 10 cards"), "{}", lines[0]);
    assert!(lines[0].contains("shuffled into a deck"), "{}", lines[0]);
    for id in [CardId::C1015Ribombee, CardId::C1135Ribombee] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::RulesUnverified,
            "{id:?}"
        );
        assert_eq!(implementation_limitations(id), lines, "{id:?}");
        let mut report = SupportReport::default();
        report.inspect_card_id("Ribombee test", id);
        assert!(report.enforce("this test").is_ok(), "{id:?}");
    }
}
