// Ported from upstream deckgym-core #433 (tests/pokemon/charizard_flame_aura_test.rs, as of e7cc5ce), with fork tests added at the end (a multi-Energy attach from the Energy Zone, an attach from the discard pile, one non-turn Energy Zone attach against both Flame Aura and Darkrai ex's Nightmare Aura, a Flame Aura Knock Out inside its owner's attack against Rally Back, Rescue Scarf, Innards Out, Hala, Dark Vengeance and Lucky Mittens, Assisting Heater's own Knock Out against Flame Aura's finishing blow, and a main-phase Flame Aura Knock Out).
use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{
        attack_action, get_initialized_game_with_board, get_test_game_with_board, play_trainer,
        trainer_from_id,
    },
    Game,
};
use rand::{rngs::StdRng, SeedableRng};

fn attach(energy: EnergyType, in_play_idx: usize) -> Action {
    Action {
        actor: 0,
        action: SimpleAction::Attach {
            attachments: vec![(1, energy, in_play_idx)],
            is_turn_energy: true,
        },
        is_stack: false,
    }
}

#[test]
fn test_charizard_flame_aura_damages_opponent_active_on_fire_attach() {
    // Flame Aura: Whenever you attach a [R] Energy from your Energy Zone to this Pokémon,
    // do 30 damage to your opponent's Active Pokémon.
    for charizard in [CardId::C1018Charizard, CardId::C1136Charizard] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(charizard)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );

        game.apply_action(&attach(EnergyType::Fire, 0));

        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy.len(), 1);
        assert_eq!(state.get_active(1).get_remaining_hp(), 40);
    }
}

#[test]
fn test_charizard_flame_aura_works_from_the_bench() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::C1018Charizard),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&attach(EnergyType::Fire, 1));

    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 40);
}

#[test]
fn test_charizard_flame_aura_ignores_non_fire_energy() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1018Charizard)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );

    game.apply_action(&attach(EnergyType::Water, 0));

    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 70);
}

// ---------------------------------------------------------------------------------------------
// Fork additions.
// ---------------------------------------------------------------------------------------------

/// One branch of an attack whose effect attaches Energy from the Energy Zone to a Benched Pokémon:
/// the attach it queued (none on a branch that attaches nothing), the Energy the Benched Pokémon
/// ends with, and the remaining HP of the opponent's Active, Wailord ex (250 HP).
struct BenchAttachBranch {
    queued: Option<SimpleAction>,
    benched_energy: Vec<EnergyType>,
    opponent_remaining_hp: u32,
}

/// Plays `attacker`'s first attack over every branch of its forecast, with `benched` as the only
/// Benched Pokémon, and resolves the attach the branch queues.
fn bench_attach_branches(attacker: PlayedCard, benched: CardId) -> Vec<BenchAttachBranch> {
    let attacker_id = CardId::from_card_id(&attacker.get_id()).expect("the attacker's printing");
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![attacker, PlayedCard::from_id(benched)],
        vec![PlayedCard::from_id(CardId::B4197WailordEx)],
    );
    let initial = game.get_state_clone();
    let attack = Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    };
    let (_, branches) = try_forecast_action(&initial, &attack)
        .expect("the attack's forecast should be exactly priced")
        .into_branches();
    branches
        .into_iter()
        .map(|branch| {
            let mut state = initial.clone();
            branch(&mut StdRng::seed_from_u64(0), &mut state, &attack);
            let (_, choices) = state.generate_possible_actions();
            let queued = choices.into_iter().find(|choice| {
                matches!(
                    choice.action,
                    SimpleAction::Attach {
                        is_turn_energy: false,
                        ..
                    }
                )
            });
            game.set_state(state);
            if let Some(queued) = &queued {
                game.apply_action(queued);
            }
            let state = game.get_state_clone();
            BenchAttachBranch {
                queued: queued.map(|choice| choice.action),
                benched_energy: state.in_play_pokemon[0][1]
                    .as_ref()
                    .expect("the Benched Pokémon stays in play")
                    .attached_energy
                    .clone(),
                opponent_remaining_hp: state.get_active(1).get_remaining_hp(),
            }
        })
        .collect()
}

/// Flame Aura fires once for each [R] Energy of a multi-Energy attach from the Energy Zone. Moltres
/// ex's Inferno Dance ("Flip 3 coins. Take an amount of [R] Energy from your Energy Zone equal to the
/// number of heads and attach it to your Benched [R] Pokémon in any way you like.") puts every heads'
/// Energy on the only Benched Charizard in one attach, and each Energy does 30.
#[test]
fn test_charizard_flame_aura_fires_once_per_energy_of_a_multi_energy_zone_attach() {
    let moltres = PlayedCard::from_id(CardId::A1047MoltresEx).with_energy(vec![EnergyType::Fire]);
    let branches = bench_attach_branches(moltres, CardId::C1018Charizard);

    let mut heads: Vec<usize> = branches
        .iter()
        .map(|branch| branch.benched_energy.len())
        .collect();
    heads.sort();
    assert_eq!(heads, [0, 1, 2, 3]);
    for branch in &branches {
        let count = branch.benched_energy.len();
        assert!(branch
            .benched_energy
            .iter()
            .all(|energy| *energy == EnergyType::Fire));
        assert_eq!(
            branch.opponent_remaining_hp,
            250 - 30 * count as u32,
            "{count} [R] Energy attached"
        );
        if count == 3 {
            assert_eq!(
                branch.queued,
                Some(SimpleAction::Attach {
                    attachments: vec![(3, EnergyType::Fire, 1)],
                    is_turn_energy: false,
                }),
                "the three Energy come in a single attach"
            );
        }
    }
}

/// Flame Aura reads "from your Energy Zone": a [R] Energy attached from the discard pile does
/// nothing.
#[test]
fn test_charizard_flame_aura_ignores_an_attach_from_the_discard_pile() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1018Charizard)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let mut state = game.get_state_clone();
    state.discard_energies[0] = vec![EnergyType::Fire];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::AttachTypedFromDiscard {
            in_play_idx: 0,
            energy_type: EnergyType::Fire,
            count: 1,
        },
        is_stack: false,
    });

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Fire]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 70);
}

/// The difference the shared hook keeps, on one attach from the Energy Zone that is not the turn's
/// Energy: Sableye's Jeweled Gift ("Take a random Energy from among [G], [R], [W], [L], [P], [F], [D],
/// and [M] Energy from your Energy Zone and attach it to 1 of your Benched Pokémon."). Flame Aura
/// fires on the [R] branch. Darkrai ex's Nightmare Aura, read as the turn's Energy attach only
/// (only_turn_energy), stays silent on every branch, the [D] one included; its turn's-Energy cases
/// are in darkrai_ex_test.rs.
#[test]
fn test_jeweled_gift_fires_flame_aura_but_not_nightmare_aura() {
    let sableye =
        || PlayedCard::from_id(CardId::B3a040Sableye).with_energy(vec![EnergyType::Colorless]);
    let charizard = bench_attach_branches(sableye(), CardId::C1018Charizard);
    let darkrai = bench_attach_branches(sableye(), CardId::A2110DarkraiEx);

    for branches in [&charizard, &darkrai] {
        assert_eq!(branches.len(), 8, "one branch per printed Energy type");
        assert!(branches
            .iter()
            .all(|branch| branch.benched_energy.len() == 1));
    }
    for branch in &charizard {
        let expected = if branch.benched_energy == [EnergyType::Fire] {
            220
        } else {
            250
        };
        assert_eq!(
            branch.opponent_remaining_hp, expected,
            "Charizard given {:?}",
            branch.benched_energy
        );
    }
    assert!(darkrai
        .iter()
        .any(|branch| branch.benched_energy == [EnergyType::Darkness]));
    for branch in &darkrai {
        assert_eq!(
            branch.opponent_remaining_hp, 250,
            "Darkrai ex given {:?}",
            branch.benched_energy
        );
    }
}

// Flame Aura's 30 is Ability damage, so a Knock Out it causes is not "by damage from an attack", even
// when it fires on an attack's own attach and the attack's Knock Out wave settles it.

fn ready_ceruledge() -> PlayedCard {
    PlayedCard::from_id(CardId::C1028Ceruledge).with_energy(vec![
        EnergyType::Fire,
        EnergyType::Fire,
        EnergyType::Colorless,
    ])
}

/// Player 1's Moltres ex (A1 047), with the [R] Energy that Inferno Dance needs.
fn moltres_ex() -> PlayedCard {
    PlayedCard::from_id(CardId::A1047MoltresEx).with_energy(vec![EnergyType::Fire])
}

/// Player 1, to act, uses `attacker`'s first attack, whose effect attaches [R] Energy from the Energy
/// Zone to player 1's lone Benched Charizard, on the first branch that queues that attach (for
/// Inferno Dance, a branch with heads). The attach fires Flame Aura. Then the attack's Knock Out wave
/// and player 0's promotion are settled. Returns the remaining HP of player 0's Active when the attach
/// is applied, after the attack's own damage and before Flame Aura's.
///
/// It first checks that the attack's `ResolveAttackRetaliation` choice is still pending on the stack
/// when the queued attach is applied, so Flame Aura fires inside the attack and any Knock Out it
/// causes waits for the attack's wave (the path this file's inside-an-attack tests are about).
fn attack_attaching_to_benched_charizard(game: &mut Game<'static>, attacker: CardId) -> u32 {
    let initial = game.get_state_clone();
    let attack = Action {
        actor: 1,
        action: attack_action(attacker, 0),
        is_stack: false,
    };
    let (_, branches) = try_forecast_action(&initial, &attack)
        .expect("the attack's forecast should be exactly priced")
        .into_branches();
    let (state, queued) = branches
        .into_iter()
        .find_map(|branch| {
            let mut state = initial.clone();
            branch(&mut StdRng::seed_from_u64(0), &mut state, &attack);
            let (_, choices) = state.generate_possible_actions();
            let queued = choices.into_iter().find(|choice| {
                matches!(
                    choice.action,
                    SimpleAction::Attach {
                        is_turn_energy: false,
                        ..
                    }
                )
            })?;
            Some((state, queued))
        })
        .expect("a branch queues an attach");
    let before_flame_aura = state.get_active(0).get_remaining_hp();
    game.set_state(state);
    assert!(
        game.get_state_clone()
            .move_generation_stack
            .iter()
            .any(|(_, choices)| choices
                .iter()
                .any(|choice| matches!(choice, SimpleAction::ResolveAttackRetaliation { .. }))),
        "the attack's ResolveAttackRetaliation choice is pending when its attach is applied"
    );
    game.apply_action(&queued);
    // The attack's Knock Out wave, then player 0's promotion.
    game.play_until_stable();
    before_flame_aura
}

/// `ender` ends the turn. After the Pokémon Checkup and the other player's draw, that player's
/// Active `attacker` uses its first attack.
fn end_turn_and_attack_back(game: &mut Game<'static>, ender: usize, attacker: CardId) {
    game.apply_action(&Action {
        actor: ender,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    // The Pokémon Checkup and the other player's draw.
    game.play_until_stable();
    let avenger = (ender + 1) % 2;
    assert_eq!(game.get_state_clone().current_player, avenger);

    game.apply_action(&Action {
        actor: avenger,
        action: attack_action(attacker, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

/// Player 1's Moltres ex uses Inferno Dance with a lone Benched Charizard, on a branch with heads,
/// against player 0's `defender` with 30 HP left and a ready Ceruledge behind it. The attach the attack
/// queues fires Flame Aura, whose first 30 Knocks the defender Out; the attack's Knock Out wave scores
/// it, and player 0 promotes Ceruledge.
fn flame_aura_knock_out_inside_inferno_dance(defender: PlayedCard) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![defender.with_remaining_hp(30), ready_ceruledge()],
        vec![moltres_ex(), PlayedCard::from_id(CardId::C1018Charizard)],
    );
    attack_attaching_to_benched_charizard(&mut game, CardId::A1047MoltresEx);

    let state = game.get_state_clone();
    assert_eq!(state.points, [0, 1], "the Knock Out still scores");
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");
    game
}

/// Ceruledge's Rally Back ("If any of your Pokémon were Knocked Out by damage from an attack during
/// your opponent's last turn, this attack does 70 more damage.") does its printed 70 the next turn.
#[test]
fn test_a_flame_aura_knock_out_inside_an_attack_does_not_count_for_rally_back() {
    let mut game =
        flame_aura_knock_out_inside_inferno_dance(PlayedCard::from_id(CardId::A1211Snorlax));
    end_turn_and_attack_back(&mut game, 1, CardId::C1028Ceruledge);
    // Moltres ex (140 HP, Weakness [L]): 140 - 70 = 70.
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 70);
}

/// Rescue Scarf ("If the Pokémon this card is attached to is Knocked Out by damage from an attack
/// from your opponent's Pokémon, put it into your hand instead of the discard pile.") does not return
/// the Knocked Out Snorlax to the hand.
#[test]
fn test_a_flame_aura_knock_out_inside_an_attack_ignores_rescue_scarf() {
    let game = flame_aura_knock_out_inside_inferno_dance(
        PlayedCard::from_id(CardId::A1211Snorlax)
            .with_tool(get_card_by_enum(CardId::A4155RescueScarf)),
    );

    let state = game.get_state_clone();
    assert!(!state.hands[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
    assert!(state.discard_piles[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
}

/// Pyukumuku's Innards Out ("If this Pokémon is in the Active Spot and is Knocked Out by damage from an
/// attack from your opponent's Pokémon, do 50 damage to the Attacking Pokémon.") does not fire: Moltres
/// ex keeps its 140 HP.
#[test]
fn test_a_flame_aura_knock_out_inside_an_attack_ignores_innards_out() {
    let game =
        flame_aura_knock_out_inside_inferno_dance(PlayedCard::from_id(CardId::A3054Pyukumuku));

    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 140);
}

/// Hala (B1 222: "During your opponent's next turn, if your Hariyama or Crabominable would be Knocked
/// Out by damage from an attack, it is not Knocked Out and its remaining HP becomes 10.") does not
/// cover a Flame Aura Knock Out inside Inferno Dance: player 0 plays Hala, and on player 1's turn the
/// Hariyama (B1 127) with 30 HP left is Knocked Out, and the Knock Out scores.
#[test]
fn test_hala_does_not_save_hariyama_from_a_flame_aura_knock_out_inside_an_attack() {
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![
            PlayedCard::from_id(CardId::B1127Hariyama).with_remaining_hp(30),
            ready_ceruledge(),
        ],
        vec![moltres_ex(), PlayedCard::from_id(CardId::C1018Charizard)],
    );
    let mut state = game.get_state_clone();
    state.hands[0].push(get_card_by_enum(CardId::B1222Hala));
    game.set_state(state);
    play_trainer(&mut game, 0, trainer_from_id(CardId::B1222Hala));
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    // The Pokémon Checkup and player 1's draw.
    game.play_until_stable();
    assert_eq!(game.get_state_clone().current_player, 1);

    attack_attaching_to_benched_charizard(&mut game, CardId::A1047MoltresEx);

    let state = game.get_state_clone();
    assert_eq!(state.points, [0, 1], "Hariyama is Knocked Out and the Knock Out scores");
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");
    assert!(state.discard_piles[0]
        .iter()
        .any(|card| card.get_name() == "Hariyama"));
}

/// Zarude's Dark Vengeance (B3 114, 40 damage: "If any of your [D] Pokémon were Knocked Out by damage
/// from an attack during your opponent's last turn, this attack does 80 more damage.") does its base
/// 40 the turn after Flame Aura Knocks Out a [D] Seviper (A4a 048) inside Inferno Dance.
#[test]
fn test_a_flame_aura_knock_out_inside_an_attack_does_not_count_for_dark_vengeance() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::A4a048Seviper).with_remaining_hp(30),
            PlayedCard::from_id(CardId::B3114Zarude)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]),
        ],
        vec![moltres_ex(), PlayedCard::from_id(CardId::C1018Charizard)],
    );
    attack_attaching_to_benched_charizard(&mut game, CardId::A1047MoltresEx);
    let state = game.get_state_clone();
    assert_eq!(state.points, [0, 1], "the Knock Out still scores");
    assert_eq!(state.get_active(0).get_name(), "Zarude");

    end_turn_and_attack_back(&mut game, 1, CardId::B3114Zarude);
    // Moltres ex (140 HP, Weakness [L]): 140 - 40 = 100.
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 100);
}

/// Lucky Mittens (B1 220: "Whenever your opponent's Pokémon is Knocked Out by damage from an attack
/// used by the Pokémon this card is attached to, draw a card.") on the attacking Moltres ex draws
/// nothing for a Flame Aura Knock Out inside Inferno Dance.
#[test]
fn test_a_flame_aura_knock_out_inside_an_attack_gives_no_lucky_mittens_draw() {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax).with_remaining_hp(30),
            ready_ceruledge(),
        ],
        vec![
            moltres_ex().with_tool(get_card_by_enum(CardId::B1220LuckyMittens)),
            PlayedCard::from_id(CardId::C1018Charizard),
        ],
    );
    let hand_before = game.get_state_clone().hands[1].len();
    attack_attaching_to_benched_charizard(&mut game, CardId::A1047MoltresEx);

    let state = game.get_state_clone();
    assert_eq!(state.points, [0, 1], "the Knock Out still scores");
    assert_eq!(state.hands[1].len(), hand_before, "no Lucky Mittens draw");
}

/// Player 1's Flareon (A3b 008) uses Assisting Heater (40 damage: "Take a [R] Energy from your Energy
/// Zone and attach it to 1 of your Benched Pokémon.") with a lone Benched Charizard, against player
/// 0's Snorlax holding Rescue Scarf (A4 155) with `remaining_hp` left and a ready Ceruledge behind it.
/// The attack's 40 comes first; the attach then fires Flame Aura on the Snorlax. Either way the Knock
/// Out scores, and player 0 promotes Ceruledge.
fn assisting_heater_onto_benched_charizard(remaining_hp: u32) -> Game<'static> {
    let mut game = get_initialized_game_with_board(
        0,
        1,
        4,
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax)
                .with_remaining_hp(remaining_hp)
                .with_tool(get_card_by_enum(CardId::A4155RescueScarf)),
            ready_ceruledge(),
        ],
        vec![
            PlayedCard::from_id(CardId::A3b008Flareon)
                .with_energy(vec![EnergyType::Fire, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::C1018Charizard),
        ],
    );
    let before_flame_aura = attack_attaching_to_benched_charizard(&mut game, CardId::A3b008Flareon);
    assert_eq!(before_flame_aura, remaining_hp.saturating_sub(40));

    let state = game.get_state_clone();
    assert_eq!(state.points, [0, 1], "the Knock Out scores");
    assert_eq!(state.get_active(0).get_name(), "Ceruledge");
    game
}

/// Assisting Heater's own 40 Knocks Out a Snorlax with 40 HP left, so Flame Aura's 30 then hits an
/// Active already at 0: the Knock Out stays by damage from an attack. Rescue Scarf puts Snorlax into
/// the hand, and the next turn Rally Back does 70 + 70 = 140, which Knocks Out Flareon (110 HP).
#[test]
fn test_an_assisting_heater_knock_out_stays_an_attack_knock_out_when_flame_aura_also_hits() {
    let mut game = assisting_heater_onto_benched_charizard(40);
    let state = game.get_state_clone();
    assert!(state.hands[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
    assert!(!state.discard_piles[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));

    end_turn_and_attack_back(&mut game, 1, CardId::C1028Ceruledge);
    // Flareon (110 HP, Weakness [W]) is Knocked Out by 140, where 70 would leave it 40 HP.
    let state = game.get_state_clone();
    assert_eq!(state.points, [1, 1], "Rally Back's 140 Knocks Out Flareon");
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_name() == "Flareon"));
}

/// Assisting Heater's own 40 leaves a Snorlax with 60 HP left at 20, and Flame Aura's 30 Knocks it
/// Out: an Ability Knock Out, which still scores. Rescue Scarf does not put Snorlax into the hand, and
/// the next turn Rally Back does its printed 70.
#[test]
fn test_flame_aura_finishing_an_assisting_heater_target_is_an_ability_knock_out() {
    let mut game = assisting_heater_onto_benched_charizard(60);
    let state = game.get_state_clone();
    assert!(!state.hands[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
    assert!(state.discard_piles[0]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));

    end_turn_and_attack_back(&mut game, 1, CardId::C1028Ceruledge);
    // Flareon (110 HP, Weakness [W]): 110 - 70 = 40.
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 40);
}

/// Outside an attack: the turn's [R] Energy, attached in the main phase to player 0's Active Charizard,
/// fires Flame Aura, whose 30 Knocks Out player 1's Snorlax (30 HP left, holding Rescue Scarf). The
/// Knock Out is settled at once (player 0 scores, and player 1 must promote) and is not by damage
/// from an attack: Rescue Scarf does not put Snorlax into the hand, and the next turn Ceruledge's
/// Rally Back does its printed 70.
#[test]
fn test_a_main_phase_flame_aura_knock_out_is_settled_at_once_and_is_not_from_an_attack() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::C1018Charizard)],
        vec![
            PlayedCard::from_id(CardId::A1211Snorlax)
                .with_remaining_hp(30)
                .with_tool(get_card_by_enum(CardId::A4155RescueScarf)),
            ready_ceruledge(),
        ],
    );
    game.apply_action(&attach(EnergyType::Fire, 0));

    let state = game.get_state_clone();
    assert_eq!(state.points, [1, 0], "the Knock Out scores at once");
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.generate_possible_actions().0, 1, "player 1 promotes");
    assert!(!state.hands[1]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
    assert!(state.discard_piles[1]
        .iter()
        .any(|card| card.get_name() == "Snorlax"));
    game.play_until_stable();
    assert_eq!(game.get_state_clone().get_active(1).get_name(), "Ceruledge");

    end_turn_and_attack_back(&mut game, 0, CardId::C1028Ceruledge);
    // Charizard (150 HP, Weakness [W]): 150 - 70 = 80.
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 80);
}
