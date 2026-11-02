// Ported from upstream deckgym-core #435 (tests/tools/c1_tools_test.rs, as of b6b769b): its 4 tests (Eviolite on a Basic holder and not on an evolved one; Light Ball +30 for Pikachu ex and nothing for others) as upstream wrote them. Fork tests follow at the end: Eviolite on a Benched Basic, on a Stage 2, against its owner's own attack and an Ability's damage, against Brick Break (as Heavy Helmet), on a Fossil played as a Basic, two copies of each Tool, Light Ball on every Pikachu ex printing (the Active only), not on Pikachu or Raichu, and before Weakness, and the printings' status. The hit back is pinned in rules_repair_hit_back_attack_damage.rs, kd's clock and kt's lasting Tools in hooks/core.rs (persistent_defender_damage_tests, temporary_defender_reduction_tests), and the damage-saturation bound in actions/apply_attack_action.rs.
//! The Tools of upstream #435: Eviolite (C1 123) and Light Ball (C1 124).

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{
        attack_action, get_initialized_game_with_board, get_test_game_with_board, play_trainer,
        trainer_from_id,
    },
};
use strum::IntoEnumIterator;

fn attack(game: &mut deckgym::Game<'static>, card_id: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(card_id, 0),
        is_stack: false,
    });
}

fn hp_lost_by_defender(defender: PlayedCard) -> u32 {
    let full_hp = defender.get_remaining_hp();
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass; 2])],
        vec![defender],
    );
    attack(&mut game, CardId::A1001Bulbasaur);
    full_hp - game.get_state_clone().get_remaining_hp(1, 0)
}

/// Eviolite: "The Basic Pokémon this card is attached to takes -20 damage from attacks from your
/// opponent's Pokémon."
#[test]
fn test_eviolite_reduces_damage_to_a_basic_holder_by_20() {
    let eviolite = get_card_by_enum(CardId::C1123Eviolite);
    let bare = hp_lost_by_defender(PlayedCard::from_id(CardId::A1033Charmander));
    let with_tool =
        hp_lost_by_defender(PlayedCard::from_id(CardId::A1033Charmander).with_tool(eviolite));
    assert!(bare >= 20);
    assert_eq!(with_tool, bare - 20);
}

#[test]
fn test_eviolite_does_nothing_on_an_evolved_holder() {
    let eviolite = get_card_by_enum(CardId::C1123Eviolite);
    let bare = hp_lost_by_defender(PlayedCard::from_id(CardId::A1034Charmeleon));
    let with_tool =
        hp_lost_by_defender(PlayedCard::from_id(CardId::A1034Charmeleon).with_tool(eviolite));
    assert_eq!(with_tool, bare);
}

fn pikachu_ex_damage(tool: bool) -> u32 {
    let mut attacker =
        PlayedCard::from_id(CardId::A1096PikachuEx).with_energy(vec![EnergyType::Lightning; 3]);
    if tool {
        attacker = attacker.with_tool(get_card_by_enum(CardId::C1124LightBall));
    }
    let mut game = get_test_game_with_board(
        vec![attacker, PlayedCard::from_id(CardId::A1094Pikachu)],
        vec![PlayedCard::from_id(CardId::A1202Chansey)],
    );
    attack(&mut game, CardId::A1096PikachuEx);
    120 - game.get_state_clone().get_remaining_hp(1, 0)
}

/// Light Ball: "Attacks used by the Pikachu ex this card is attached to do +30 damage to your
/// opponent's Active Pokémon."
#[test]
fn test_light_ball_adds_30_damage_for_pikachu_ex() {
    assert_eq!(pikachu_ex_damage(true), pikachu_ex_damage(false) + 30);
}

#[test]
fn test_light_ball_does_nothing_for_other_pokemon() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass; 2])
            .with_tool(get_card_by_enum(CardId::C1124LightBall))],
        vec![PlayedCard::from_id(CardId::A1202Chansey)],
    );
    attack(&mut game, CardId::A1001Bulbasaur);
    assert_eq!(120 - game.get_state_clone().get_remaining_hp(1, 0), 40);
}

// Fork tests.

fn eviolite() -> Card {
    get_card_by_enum(CardId::C1123Eviolite)
}

fn light_ball() -> Card {
    get_card_by_enum(CardId::C1124LightBall)
}

/// Player 0's Heatmor (B1 044) uses Tongue Whip ("This attack does 30 damage to 1 of your
/// opponent's Benched Pokémon.") on the Benched Pokémon at `target` of player 1's `board`: the HP
/// it has left.
fn hp_after_tongue_whip(board: Vec<PlayedCard>, target: usize) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B1044Heatmor).with_energy(vec![EnergyType::Fire])],
        board,
    );
    attack(&mut game, CardId::B1044Heatmor);
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let snipe = choices
        .into_iter()
        .find(|choice| match &choice.action {
            SimpleAction::ApplyDamage { targets, .. } => targets[0].2 == target,
            SimpleAction::ApplyQueuedAttackDamage { targets, .. } => targets[0].2 == target,
            _ => false,
        })
        .expect("Tongue Whip can target every Benched Pokémon");
    game.apply_action(&snipe);
    game.get_state_clone().get_remaining_hp(1, target)
}

/// On the Bench too: Tongue Whip's 30 does 10 to a Benched Squirtle (60 HP) holding Eviolite, and
/// 30 to the Squirtle beside it without one.
#[test]
fn test_eviolite_cuts_an_opponents_attack_on_a_benched_basic() {
    let board = || {
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1053Squirtle).with_tool(eviolite()),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ]
    };
    assert_eq!(hp_after_tongue_whip(board(), 1), 50, "30 - 20 = 10");
    assert_eq!(hp_after_tongue_whip(board(), 2), 30, "no Eviolite: the full 30");
}

/// "The Basic Pokémon": nothing on a Stage 2 either (Venusaur A1 003 takes Vine Whip's full 40).
#[test]
fn test_eviolite_does_nothing_on_a_stage_2_holder() {
    let bare = hp_lost_by_defender(PlayedCard::from_id(CardId::A1003Venusaur));
    let with_tool = hp_lost_by_defender(PlayedCard::from_id(CardId::A1003Venusaur).with_tool(eviolite()));
    assert_eq!((bare, with_tool), (40, 40));
}

/// Only attacks from the opponent's Pokémon: Diggersby's Earthquake (B2 140, 70, "This attack also
/// does 10 damage to each of your Benched Pokémon.") does its full 10 to its owner's Benched
/// Bulbasaur holding Eviolite, as to the Squirtle beside it.
#[test]
fn test_eviolite_does_not_cut_damage_from_its_owners_own_attack() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B2140Diggersby)
                .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless]),
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_tool(eviolite()),
            PlayedCard::from_id(CardId::A1053Squirtle),
        ],
        vec![PlayedCard::from_id(CardId::A1211Snorlax)],
    );
    attack(&mut game, CardId::B2140Diggersby);
    let state = game.get_state_clone();
    assert_eq!(state.get_remaining_hp(0, 1), 60, "Bulbasaur with Eviolite: the full 10");
    assert_eq!(state.get_remaining_hp(0, 2), 50, "Squirtle: the full 10");
    assert_eq!(state.get_active(1).get_remaining_hp(), 80, "Snorlax took Earthquake's 70");
}

/// "from attacks": Greninja's Water Shuriken (A1 089, "Once during your turn, you may do 20 damage
/// to 1 of your opponent's Pokémon.") is an Ability's damage, so it does its full 20 to an Active
/// Bulbasaur (70 HP) and a Benched Squirtle (60 HP), each holding Eviolite.
#[test]
fn test_eviolite_does_not_cut_damage_from_an_ability() {
    for (target, hp) in [(0, 50), (1, 40)] {
        let mut game = get_initialized_game_with_board(
            0,
            0,
            5,
            vec![PlayedCard::from_id(CardId::A1089Greninja)],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur).with_tool(eviolite()),
                PlayedCard::from_id(CardId::A1053Squirtle).with_tool(eviolite()),
            ],
        );
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::UseAbility { in_play_idx: 0 },
            is_stack: false,
        });
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        let shuriken = choices
            .into_iter()
            .find(|choice| {
                matches!(&choice.action, SimpleAction::ApplyDamage { targets, .. } if targets[0].2 == target)
            })
            .expect("Water Shuriken can target either Pokémon");
        assert!(matches!(
            &shuriken.action,
            SimpleAction::ApplyDamage { targets, is_from_active_attack: false, .. }
                if targets[..] == [(20, 1, target)]
        ));
        game.apply_action(&shuriken);
        assert_eq!(game.get_state_clone().get_remaining_hp(1, target), hp, "target {target}");
    }
}

/// As Heavy Helmet (sawk_test.rs, test_sawk_bypasses_heavy_helmet_and_ability): Sawk's Brick Break
/// (B3 086, 30, "This attack's damage isn't affected by any effects on your opponent's Active
/// Pokémon.") ignores Eviolite and does its full 30 to an Active Squirtle (60 HP) holding it. The
/// control, Charmander's Ember (30), does 10 to the same Squirtle.
#[test]
fn test_brick_break_ignores_eviolite_like_heavy_helmet() {
    let squirtle = || PlayedCard::from_id(CardId::A1053Squirtle).with_tool(eviolite());
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3086Sawk).with_energy(vec![EnergyType::Fighting])],
        vec![squirtle()],
    );
    attack(&mut game, CardId::B3086Sawk);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 30);

    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Fire])],
        vec![squirtle()],
    );
    attack(&mut game, CardId::A1033Charmander);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 50);
}

/// A Fossil is played "as if it were a 40-HP Basic [C] Pokémon" (Helix Fossil, A1 216): in play it
/// has 40 HP and this fork's `get_stage` makes it Basic, so Eviolite cuts the damage it takes
/// (coordinator-088: the card text, no rule row; upstream's `card.is_basic()` is false for a
/// Fossil). The fork offers a Tool for any Pokémon in play, a Fossil included. Charmander's Ember
/// (30) leaves it at 30 HP with Eviolite and at 10 without.
#[test]
fn test_eviolite_cuts_damage_to_a_fossil_played_as_a_basic() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1216HelixFossil),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![eviolite()];
    game.set_state(state);
    play_trainer(&mut game, 0, trainer_from_id(CardId::C1123Eviolite));
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    let on_fossil = choices
        .into_iter()
        .find(|choice| matches!(&choice.action, SimpleAction::AttachTool { in_play_idx: 0, .. }))
        .expect("Eviolite can be attached to the Fossil");
    game.apply_action(&on_fossil);
    let fossil = game.get_state_clone().in_play_pokemon[0][0].clone().unwrap();
    assert_eq!(fossil.attached_tools, vec![eviolite()]);
    assert_eq!(fossil.get_remaining_hp(), 40);

    let ember = |fossil: PlayedCard| {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Fire])],
            vec![fossil, PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        attack(&mut game, CardId::A1033Charmander);
        game.get_state_clone().get_remaining_hp(1, 0)
    };
    assert_eq!(ember(fossil), 30, "30 - 20 = 10 on 40 HP");
    assert_eq!(ember(PlayedCard::from_id(CardId::A1216HelixFossil)), 10);
}

/// The fork's per-Tool convention (Heavy Helmet, Steel Apron, Beastite): each copy counts, -20 or
/// +30 per Tool. A fixture: only Dual Customization (Revavroom B4 115, a Stage 1 and not a Pikachu
/// ex) holds two Tools, and neither Tool does anything on it. Snorlax's Rollout (70) on Chansey
/// (120 HP): 70, 50, 30; Pikachu ex's Pika Punch (C1 043, 30) on Chansey: 30, 60, 90.
#[test]
fn test_two_copies_of_each_tool_count_twice() {
    let rollout = |tools: Vec<Card>| {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1211Snorlax).with_energy(vec![EnergyType::Colorless; 4])],
            vec![PlayedCard::from_id(CardId::A1202Chansey).with_tools(tools)],
        );
        attack(&mut game, CardId::A1211Snorlax);
        120 - game.get_state_clone().get_remaining_hp(1, 0)
    };
    assert_eq!(rollout(vec![]), 70);
    assert_eq!(rollout(vec![eviolite()]), 50);
    assert_eq!(rollout(vec![eviolite(), eviolite()]), 30);

    let pika_punch = |tools: Vec<Card>| {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::C1043PikachuEx)
                .with_energy(vec![EnergyType::Lightning])
                .with_tools(tools)],
            vec![PlayedCard::from_id(CardId::A1202Chansey)],
        );
        attack(&mut game, CardId::C1043PikachuEx);
        120 - game.get_state_clone().get_remaining_hp(1, 0)
    };
    assert_eq!(pika_punch(vec![]), 30);
    assert_eq!(pika_punch(vec![light_ball()]), 60);
    assert_eq!(pika_punch(vec![light_ball(), light_ball()]), 90);
}

/// Player 0's Active `attacker` does 30 to player 1's Active Chansey and 30 to the Benched Chansey
/// behind it in one attack (the engine's `ApplyDamage` from the Active, as an attack's damage): the
/// damage each takes.
fn damage_to_active_and_bench(attacker: PlayedCard) -> (u32, u32) {
    let mut game = get_test_game_with_board(
        vec![attacker],
        vec![
            PlayedCard::from_id(CardId::A1202Chansey),
            PlayedCard::from_id(CardId::A1202Chansey),
        ],
    );
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(30, 1, 0), (30, 1, 1)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    let state = game.get_state_clone();
    (120 - state.get_remaining_hp(1, 0), 120 - state.get_remaining_hp(1, 1))
}

/// Every printing named "Pikachu ex" (17) gets the +30, to the opponent's Active only. No printed
/// Pikachu ex attack damages the Bench, so the Benched target is the engine's own attack damage.
#[test]
fn test_light_ball_adds_30_to_the_active_only_for_every_pikachu_ex_printing() {
    let printings: Vec<CardId> = CardId::iter()
        .filter(|id| {
            let card = get_card_by_enum(*id);
            matches!(card, Card::Pokemon(_)) && card.get_name() == "Pikachu ex"
        })
        .collect();
    assert_eq!(printings.len(), 17);
    for id in printings {
        let holder = PlayedCard::from_id(id).with_tool(light_ball());
        assert_eq!(damage_to_active_and_bench(holder), (60, 30), "{id:?}");
        assert_eq!(damage_to_active_and_bench(PlayedCard::from_id(id)), (30, 30), "{id:?}");
    }
}

/// "the Pikachu ex": a plain Pikachu (A1 094) or a Raichu (A1 095) holding Light Ball gets nothing,
/// through Pikachu's own Gnaw (20) too.
#[test]
fn test_light_ball_does_nothing_for_pikachu_or_raichu() {
    for id in [CardId::A1094Pikachu, CardId::A1095Raichu] {
        let holder = PlayedCard::from_id(id).with_tool(light_ball());
        assert_eq!(damage_to_active_and_bench(holder), (30, 30), "{id:?}");
    }
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1094Pikachu)
            .with_energy(vec![EnergyType::Lightning])
            .with_tool(light_ball())],
        vec![PlayedCard::from_id(CardId::A1202Chansey)],
    );
    attack(&mut game, CardId::A1094Pikachu);
    assert_eq!(120 - game.get_state_clone().get_remaining_hp(1, 0), 20);
}

/// The +30 comes before Weakness, with the attacker's other bonuses. Pikachu ex's Pika Punch (C1
/// 043, 30) on the Lightning-weak Articuno ex (A1 084, 140 HP): 30 + 20 = 50, and 30 + 30 + 20 = 80
/// with Light Ball. Under Bounded Field (Weakness as x2) the order shows: 30 x 2 = 60, and
/// (30 + 30) x 2 = 120 with Light Ball (it would be 90 if the +30 came after Weakness).
#[test]
fn test_light_ball_comes_before_weakness() {
    let pika_punch = |light: bool, bounded: bool| {
        let mut pikachu =
            PlayedCard::from_id(CardId::C1043PikachuEx).with_energy(vec![EnergyType::Lightning]);
        if light {
            pikachu = pikachu.with_tool(light_ball());
        }
        let mut game = get_test_game_with_board(
            vec![pikachu],
            vec![PlayedCard::from_id(CardId::A1084ArticunoEx)],
        );
        if bounded {
            let mut state = game.get_state_clone();
            state.active_stadium = Some(get_card_by_enum(CardId::B3155BoundedField));
            game.set_state(state);
        }
        attack(&mut game, CardId::C1043PikachuEx);
        140 - game.get_state_clone().get_remaining_hp(1, 0)
    };
    assert_eq!(pika_punch(false, false), 50);
    assert_eq!(pika_punch(true, false), 80);
    assert_eq!(pika_punch(false, true), 60);
    assert_eq!(pika_punch(true, true), 120);
}

/// Both Tools are Complete, with no known limitation.
#[test]
fn test_c1_tools_printings_report_complete() {
    for id in [CardId::C1123Eviolite, CardId::C1124LightBall] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
