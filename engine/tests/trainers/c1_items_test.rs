// Ported from upstream deckgym-core #435 (tests/trainers/c1_items_test.rs, as of b6b769b): its 8 tests (Super Potion, Max Repel, Full Heal, Genome Converter Y) as upstream wrote them, except that the Super Potion heal test also pins this fork's choice, a HealAndDiscardRandomEnergy that names no Energy (upstream offers a HealAndDiscardEnergy carrying an Energy drawn when the card is played; ours is drawn when the choice resolves, after the heal, and two [G] make one branch). Fork tests follow at the end: Dustin's clip boards (shot list c1-items-playable), Super Potion's targets, heal amounts, Energy branches and Heal Block, Max Repel's Stage 2 and Bench conditions and the opponent's choice, Full Heal on every Special Condition, Genome Converter Y's sources (a Benched Mega Mewtwo X ex included), Poké Mart Guy, and the printings' status. Eviolite and Light Ball (upstream's tests/tools/c1_tools_test.rs) are R8-06b.
//! The Items of upstream #435: Super Potion (C1 120), Max Repel (C1 121), Full Heal (C1 122) and
//! Genome Converter Y (P-C 009).

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::{get_test_game_with_board, play_trainer, trainer_from_id},
    State,
};
use rand::{rngs::StdRng, SeedableRng};

fn give_card(game: &mut deckgym::Game<'static>, card_id: CardId) {
    let mut state = game.get_state_clone();
    state.hands[0] = vec![Card::Trainer(trainer_from_id(card_id))];
    game.set_state(state);
}

/// Super Potion: "Heal 40 damage from 1 of your Pokémon that has any Energy attached. If you
/// healed any damage in this way, discard a random Energy from that Pokémon."
#[test]
fn test_super_potion_heals_40_and_discards_an_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_remaining_hp(20)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(10),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::C1120SuperPotion);
    play_trainer(&mut game, 0, trainer_from_id(CardId::C1120SuperPotion));

    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert_eq!(actions.len(), 1, "only the Pokémon with Energy is a target");
    // Ours: the choice names its target only; the Energy is drawn when it resolves.
    assert_eq!(
        actions[0].action,
        SimpleAction::HealAndDiscardRandomEnergy {
            in_play_idx: 0,
            heal_amount: 40
        }
    );
    game.apply_action(&actions[0]);

    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 60);
    assert_eq!(state.get_active(0).attached_energy.len(), 1);
    assert_eq!(state.discard_energies[0].len(), 1);
    assert!(state.hands[0].is_empty());
}

/// No Energy discard when no damage was actually healed.
#[test]
fn test_super_potion_needs_a_damaged_pokemon_with_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1033Charmander).with_remaining_hp(10),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::C1120SuperPotion);
    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert!(!actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::Play { .. })));
}

/// Max Repel: "Switch out your opponent's Active Stage 2 Pokémon to the Bench."
#[test]
fn test_max_repel_switches_out_a_stage_2_active() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1003Venusaur),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    give_card(&mut game, CardId::C1121MaxRepel);
    play_trainer(&mut game, 0, trainer_from_id(CardId::C1121MaxRepel));

    let state = game.get_state_clone();
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 1, "the opponent chooses the new Active");
    game.apply_action(&actions[0]);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Bulbasaur");
}

#[test]
fn test_max_repel_not_playable_against_basic_active_or_empty_bench() {
    for opp in [
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
        vec![PlayedCard::from_id(CardId::A1003Venusaur)],
    ] {
        let mut game =
            get_test_game_with_board(vec![PlayedCard::from_id(CardId::A1033Charmander)], opp);
        give_card(&mut game, CardId::C1121MaxRepel);
        let state = game.get_state_clone();
        let (_, actions) = state.generate_possible_actions();
        assert!(!actions
            .iter()
            .any(|a| matches!(a.action, SimpleAction::Play { .. })));
    }
}

/// Full Heal: "Your Active Pokémon recovers from all Special Conditions."
#[test]
fn test_full_heal_cures_all_special_conditions_on_the_active() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1033Charmander),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let mut state = game.get_state_clone();
    state.apply_status_condition(0, 0, StatusCondition::Poisoned);
    state.apply_status_condition(0, 0, StatusCondition::Burned);
    state.apply_status_condition(0, 0, StatusCondition::Asleep);
    game.set_state(state);
    give_card(&mut game, CardId::C1122FullHeal);
    play_trainer(&mut game, 0, trainer_from_id(CardId::C1122FullHeal));

    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert!(!active.is_poisoned() && !active.is_burned() && !active.is_asleep());
    assert!(state.hands[0].is_empty());
}

#[test]
fn test_full_heal_not_playable_without_a_special_condition() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::C1122FullHeal);
    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert!(!actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::Play { .. })));
}

/// Genome Converter Y: "Move all [P] Energy from 1 of your Benched [P] Pokémon to your Mega
/// Mewtwo Y ex in the Active Spot."
#[test]
fn test_genome_converter_y_moves_all_psychic_energy_to_mega_mewtwo() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::PC002MegaMewtwoYEx),
            PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![
                EnergyType::Psychic,
                EnergyType::Psychic,
                EnergyType::Fire,
            ]),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::PC009GenomeConverterY);
    play_trainer(&mut game, 0, trainer_from_id(CardId::PC009GenomeConverterY));

    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert_eq!(actions.len(), 1);
    game.apply_action(&actions[0]);

    let state = game.get_state_clone();
    assert_eq!(
        state.get_active(0).attached_energy,
        vec![EnergyType::Psychic; 2]
    );
    assert_eq!(
        state.in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .attached_energy,
        vec![EnergyType::Fire]
    );
}

#[test]
fn test_genome_converter_y_requires_mega_mewtwo_y_ex_active() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1115Abra),
            PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Psychic]),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::PC009GenomeConverterY);
    let state = game.get_state_clone();
    let (_, actions) = state.generate_possible_actions();
    assert!(!actions
        .iter()
        .any(|a| matches!(a.action, SimpleAction::Play { .. })));
}

// Fork tests.

/// With `card_id` the only card in hand: whether it is offered as a play.
fn offered(game: &mut deckgym::Game<'static>, card_id: CardId) -> bool {
    give_card(game, card_id);
    let id = trainer_from_id(card_id).id;
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    actions
        .iter()
        .any(|a| matches!(&a.action, SimpleAction::Play { trainer_card } if trainer_card.id == id))
}

/// Plays `card_id` from hand (it must be offered); who chooses next, and what they are offered.
fn play_and_choices(game: &mut deckgym::Game<'static>, card_id: CardId) -> (usize, Vec<Action>) {
    assert!(offered(game, card_id), "{card_id:?} should be playable");
    play_trainer(game, 0, trainer_from_id(card_id));
    game.get_state_clone().generate_possible_actions()
}

fn kinds(actions: &[Action]) -> Vec<SimpleAction> {
    actions.iter().map(|a| a.action.clone()).collect()
}

/// `initial` after branch `branch` of `action`'s exact forecast, its mutation run with `seed`.
fn apply_branch(initial: &State, action: &Action, branch: usize, seed: u64) -> State {
    let (_, mut mutations) = try_forecast_action(initial, action)
        .expect("the forecast should be exactly priced")
        .into_branches();
    let mutation = mutations.remove(branch);
    let mut next = initial.clone();
    mutation(&mut StdRng::seed_from_u64(seed), &mut next, action);
    next
}

/// An Energy list in a fixed order, to compare multisets.
fn sorted(mut energies: Vec<EnergyType>) -> Vec<EnergyType> {
    energies.sort_by_key(|energy| format!("{energy:?}"));
    energies
}

/// Dustin's clip (shot list c1-items-playable, 01:04-01:09): his Active Alolan Diglett (A3 117,
/// 50 HP) at 20 HP with no Energy and an empty Bench, against an Active Wobbuffet at 90/90 with one
/// [P] Energy. Super Potion and Full Heal were each refused ("conditions not met"). The capture
/// names no printings: these fit its HP, and C1 061 Wobbuffet (Headbutt Bounce, [P], 30) fits its
/// one Energy and 30-damage hit, where A4 086's Reply Strongly costs [P][C]. The clip's Diglett
/// also holds Eviolite, left off here (R8-06b). With one [M] Energy on the same Diglett, Super
/// Potion is offered.
#[test]
fn test_super_potion_and_full_heal_refused_on_the_clips_damaged_diglett_with_no_energy() {
    let board = |energy: Vec<EnergyType>| {
        get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A3117AlolanDiglett)
                .with_remaining_hp(20)
                .with_energy(energy)],
            vec![PlayedCard::from_id(CardId::C1061Wobbuffet).with_energy(vec![EnergyType::Psychic])],
        )
    };
    let mut game = board(vec![]);
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 20);
    assert!(!offered(&mut game, CardId::C1120SuperPotion), "damaged, but no Energy");
    assert!(!offered(&mut game, CardId::C1122FullHeal), "no Special Condition");
    assert!(offered(&mut board(vec![EnergyType::Metal]), CardId::C1120SuperPotion));
}

/// Not on undamaged Pokémon, Energy or not (rules/05 #28): a full-HP Bulbasaur with [G] and a
/// full-HP Charmander with [R].
#[test]
fn test_super_potion_refused_with_only_undamaged_pokemon_with_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![EnergyType::Fire]),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    assert!(!offered(&mut game, CardId::C1120SuperPotion));
}

/// Only a damaged Pokémon with Energy is a target: of an Active Bulbasaur (damaged, [G]), a Benched
/// Charmander (damaged, no Energy), a Benched Squirtle (undamaged, [W]) and a Benched Ivysaur
/// (damaged, [G][R]), the Bulbasaur and the Ivysaur. The choices name no Energy.
#[test]
fn test_super_potion_offers_only_damaged_pokemon_with_energy() {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_damage(30)
                .with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1033Charmander).with_damage(30),
            PlayedCard::from_id(CardId::A1053Squirtle).with_energy(vec![EnergyType::Water]),
            PlayedCard::from_id(CardId::A1002Ivysaur)
                .with_damage(50)
                .with_energy(vec![EnergyType::Grass, EnergyType::Fire]),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    let (actor, choices) = play_and_choices(&mut game, CardId::C1120SuperPotion);
    assert_eq!(actor, 0);
    assert_eq!(
        kinds(&choices),
        vec![
            SimpleAction::HealAndDiscardRandomEnergy {
                in_play_idx: 0,
                heal_amount: 40
            },
            SimpleAction::HealAndDiscardRandomEnergy {
                in_play_idx: 3,
                heal_amount: 40
            },
        ]
    );
}

/// "Heal 40 damage": 40 off a Bulbasaur (70 HP) with 50 damage, and only the 10 there is off one
/// with 10 (to full HP). Either heal removed damage, so either discards one Energy.
#[test]
fn test_super_potion_heals_40_or_up_to_full_hp() {
    for (damage, healed) in [(50, 40), (10, 10)] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_damage(damage)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        let (_, choices) = play_and_choices(&mut game, CardId::C1120SuperPotion);
        game.apply_action(&choices[0]);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).get_remaining_hp(), 70 - damage + healed, "{damage} damage");
        assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Grass]);
        assert_eq!(state.discard_energies[0], vec![EnergyType::Grass]);
    }
}

/// The random Energy is drawn after the choice. Playing Super Potion draws nothing: one branch,
/// queuing the same choice whatever the seed. The chosen heal then has one chance branch per Energy
/// type, weighted by count: a Benched Abra (60 HP) with 30 damage and [P][P][R] loses a [P] with
/// 2/3 and the [R] with 1/3, healed to full in both, the same on every seed.
#[test]
fn test_super_potion_draws_the_energy_after_the_choice_as_weighted_branches() {
    use EnergyType::{Fire, Psychic};
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1115Abra)
                .with_damage(30)
                .with_energy(vec![Psychic, Psychic, Fire]),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    give_card(&mut game, CardId::C1120SuperPotion);
    let before = game.get_state_clone();
    let play = Action {
        actor: 0,
        action: SimpleAction::Play {
            trainer_card: trainer_from_id(CardId::C1120SuperPotion),
        },
        is_stack: false,
    };
    let (probabilities, _) = try_forecast_action(&before, &play).unwrap().into_branches();
    assert_eq!(probabilities, vec![1.0], "playing it draws nothing");
    let choice = SimpleAction::HealAndDiscardRandomEnergy {
        in_play_idx: 1,
        heal_amount: 40,
    };
    for seed in [1, 9_999] {
        let played = apply_branch(&before, &play, 0, seed);
        assert_eq!(played.move_generation_stack, vec![(0, vec![choice.clone()])], "seed {seed}");
    }

    let played = apply_branch(&before, &play, 0, 1);
    let heal = Action {
        actor: 0,
        action: choice,
        is_stack: true,
    };
    let (probabilities, _) = try_forecast_action(&played, &heal).unwrap().into_branches();
    assert_eq!(probabilities, vec![2.0 / 3.0, 1.0 / 3.0]);
    for (branch, discarded, left) in [(0, Psychic, vec![Psychic, Fire]), (1, Fire, vec![Psychic, Psychic])] {
        for seed in [1, 9_999] {
            let next = apply_branch(&played, &heal, branch, seed);
            let abra = next.in_play_pokemon[0][1].as_ref().unwrap();
            assert_eq!(abra.get_remaining_hp(), 60, "branch {branch}: healed to full");
            assert_eq!(sorted(abra.attached_energy.clone()), sorted(left.clone()), "branch {branch}");
            assert_eq!(next.discard_energies[0], vec![discarded], "branch {branch}");
            assert!(next.move_generation_stack.is_empty(), "branch {branch}");
        }
    }
}

/// Under Heal Block (Claydol A3a 031, "Pokémon (both yours and your opponent's) can't be healed."),
/// on either side, Super Potion is still played on a damaged Pokémon with Energy, as Potion is, but
/// it heals 0, so its "if you healed any damage" clause discards nothing, and the heal has no chance
/// branch.
#[test]
fn test_super_potion_under_heal_block_heals_nothing_and_discards_nothing() {
    use EnergyType::{Fire, Psychic};
    for claydol_side in [0, 1] {
        let mut boards = [
            vec![PlayedCard::from_id(CardId::A1115Abra)
                .with_damage(30)
                .with_energy(vec![Psychic, Fire])],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        ];
        boards[claydol_side].push(PlayedCard::from_id(CardId::A3a031Claydol));
        let [ours, theirs] = boards;
        let mut game = get_test_game_with_board(ours, theirs);
        let (_, choices) = play_and_choices(&mut game, CardId::C1120SuperPotion);
        assert_eq!(choices.len(), 1, "Claydol {claydol_side}: only the Abra is damaged");
        let (probabilities, _) = try_forecast_action(&game.get_state_clone(), &choices[0])
            .unwrap()
            .into_branches();
        assert_eq!(probabilities, vec![1.0], "Claydol {claydol_side}");
        game.apply_action(&choices[0]);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).get_remaining_hp(), 30, "Claydol {claydol_side}");
        assert_eq!(state.get_active(0).attached_energy, vec![Psychic, Fire]);
        assert!(state.discard_energies[0].is_empty(), "Claydol {claydol_side}");
    }
}

/// Dustin's clip (shot list c1-items-playable, 01:43 and 02:51): Max Repel refused against a Basic
/// Active with a Bench, Wobbuffet (C1 061, as in the Super Potion clip test) with Eevee (A1 206)
/// and Cosmog (A3 085) Benched, and Zangoose (A4a 065) with Eevee and Cosmoem (A3 086) Benched. His
/// side: an Active Alolan Dugtrio ex (A3a 047) at 90 / 100 HP with one [M] Energy and an empty
/// Bench (its Eviolite, R8-06b's, is left off). The capture names no printings; these fit its HP.
/// Repel (A3a 064), for a Basic Active, is offered on the same boards.
#[test]
fn test_max_repel_refused_on_the_clips_basic_actives_with_a_bench() {
    for (hp_left, opponent) in [
        (90, [CardId::C1061Wobbuffet, CardId::A1206Eevee, CardId::A3085Cosmog]),
        (100, [CardId::A4a065Zangoose, CardId::A1206Eevee, CardId::A3086Cosmoem]),
    ] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A3a047AlolanDugtrioEx)
                .with_remaining_hp(hp_left)
                .with_energy(vec![EnergyType::Metal])],
            opponent.iter().map(|id| PlayedCard::from_id(*id)).collect(),
        );
        assert!(!offered(&mut game, CardId::C1121MaxRepel), "{:?}", opponent[0]);
        assert!(offered(&mut game, CardId::A3a064Repel), "{:?}", opponent[0]);
    }
}

/// Not against a Stage 2 Active with nothing on its Bench to switch in: the opponent's Venusaur
/// alone. The player's own Bench (a Bulbasaur behind the player's own Venusaur) doesn't count.
#[test]
fn test_max_repel_refused_against_a_stage_2_active_with_an_empty_bench() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1003Venusaur), PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1003Venusaur)],
    );
    assert!(!offered(&mut game, CardId::C1121MaxRepel));
}

/// Only a Stage 2 Active: a Stage 1 Ivysaur with a Bench is refused. Against a Stage 2 Venusaur with
/// two Benched Pokémon it is played, and the opponent chooses either of them as the new Active; the
/// Venusaur goes to that Bench spot and the turn goes on.
#[test]
fn test_max_repel_needs_a_stage_2_active_and_the_opponent_chooses_the_new_active() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
        vec![
            PlayedCard::from_id(CardId::A1002Ivysaur),
            PlayedCard::from_id(CardId::A1001Bulbasaur),
        ],
    );
    assert!(!offered(&mut game, CardId::C1121MaxRepel), "a Stage 1 Active");
    for (chosen, name) in [(1, "Bulbasaur"), (2, "Charmander")] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
            vec![
                PlayedCard::from_id(CardId::A1003Venusaur),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        let (actor, choices) = play_and_choices(&mut game, CardId::C1121MaxRepel);
        assert_eq!(actor, 1, "the opponent chooses the new Active");
        assert_eq!(
            kinds(&choices),
            vec![
                SimpleAction::Activate {
                    player: 1,
                    in_play_idx: 1
                },
                SimpleAction::Activate {
                    player: 1,
                    in_play_idx: 2
                },
            ]
        );
        game.apply_action(&choices[chosen - 1]);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).get_name(), name);
        assert_eq!(state.in_play_pokemon[1][chosen].as_ref().unwrap().get_name(), "Venusaur");
        assert_eq!(state.generate_possible_actions().0, 0, "the turn goes on");
    }
}

/// A Bulbasaur Poisoned with a modified Checkup amount (20, as Toxic-style attacks leave it), built
/// as `comfey_recovery_test.rs` builds one.
fn poisoned_with_checkup_20() -> PlayedCard {
    let card =
        PlayedCard::from_id(CardId::A1001Bulbasaur).with_status_condition(StatusCondition::Poisoned);
    let mut encoded = serde_json::to_value(card).unwrap();
    encoded["poison_checkup_damage"] = serde_json::json!(20);
    serde_json::from_value(encoded).unwrap()
}

fn poison_checkup_damage(pokemon: &PlayedCard) -> serde_json::Value {
    serde_json::to_value(pokemon).unwrap()["poison_checkup_damage"].clone()
}

const SPECIAL_CONDITIONS: [StatusCondition; 5] = [
    StatusCondition::Poisoned,
    StatusCondition::Burned,
    StatusCondition::Asleep,
    StatusCondition::Paralyzed,
    StatusCondition::Confused,
];

/// Full Heal clears every Special Condition on the Active at once: Poison (and its modified Checkup
/// amount), Burn, and whichever of Sleep, Paralysis and Confusion it has (each replaces the others,
/// so one at a time).
#[test]
fn test_full_heal_clears_every_special_condition_and_a_modified_poison() {
    for third in [
        StatusCondition::Asleep,
        StatusCondition::Paralyzed,
        StatusCondition::Confused,
    ] {
        let mut game = get_test_game_with_board(
            vec![
                poisoned_with_checkup_20()
                    .with_status_condition(StatusCondition::Burned)
                    .with_status_condition(third),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        let before = game.get_state_clone();
        let active = before.get_active(0);
        assert!(active.is_poisoned() && active.is_burned() && active.has_status(third));
        assert_eq!(poison_checkup_damage(active), serde_json::json!(20));
        play_and_choices(&mut game, CardId::C1122FullHeal);
        let state = game.get_state_clone();
        let active = state.get_active(0);
        for condition in SPECIAL_CONDITIONS {
            assert!(!active.has_status(condition), "{third:?}: {condition:?} left");
        }
        assert_eq!(poison_checkup_damage(active), serde_json::Value::Null, "{third:?}");
        assert!(state.hands[0].is_empty());
    }
}

/// Any one Special Condition on the Active is enough.
#[test]
fn test_full_heal_is_offered_with_any_one_special_condition() {
    for condition in SPECIAL_CONDITIONS {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_status_condition(condition)],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        assert!(offered(&mut game, CardId::C1122FullHeal), "{condition:?}");
    }
}

/// Not without a Mega Mewtwo Y ex in the Active Spot: with one on the Bench and a Mewtwo ex (A1 129)
/// Active it is refused; with it Active it is offered, a Benched Abra holding [P][P] either way.
#[test]
fn test_genome_converter_y_refused_unless_mega_mewtwo_y_ex_is_active() {
    let abra = || PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Psychic; 2]);
    let opponent = || vec![PlayedCard::from_id(CardId::A1033Charmander)];
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1129MewtwoEx),
            abra(),
            PlayedCard::from_id(CardId::PC002MegaMewtwoYEx),
        ],
        opponent(),
    );
    assert!(!offered(&mut game, CardId::PC009GenomeConverterY));
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::PC002MegaMewtwoYEx), abra()],
        opponent(),
    );
    assert!(offered(&mut game, CardId::PC009GenomeConverterY));
}

/// Not without a Benched [P] Pokémon holding [P] Energy (upstream's condition: no source): an Active
/// Mega Mewtwo Y ex with [P] and no Bench; with a Benched Abra holding only [R]; with a Benched
/// Bulbasaur ([G]) holding [P][P].
#[test]
fn test_genome_converter_y_refused_without_a_benched_psychic_source() {
    for bench in [
        vec![],
        vec![PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Fire])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Psychic; 2])],
    ] {
        let mut ours = vec![
            PlayedCard::from_id(CardId::PC002MegaMewtwoYEx).with_energy(vec![EnergyType::Psychic])
        ];
        ours.extend(bench);
        let names: Vec<String> = ours.iter().map(|pokemon| pokemon.get_name()).collect();
        let mut game =
            get_test_game_with_board(ours, vec![PlayedCard::from_id(CardId::A1033Charmander)]);
        assert!(!offered(&mut game, CardId::PC009GenomeConverterY), "{names:?}");
    }
}

/// "Move all [P] Energy": every [P] on the chosen source moves to the Active, on top of what it
/// holds, and none of the source's other Energy. One choice per source, each with that source's own
/// count. A Benched Mega Mewtwo X ex (C1 056, printed [P] and [F]) is a [P] Pokémon in play.
#[test]
fn test_genome_converter_y_moves_all_and_only_psychic_and_counts_mega_mewtwo_x_ex() {
    use EnergyType::{Fighting, Grass, Psychic};
    let abra_energy = vec![Psychic, Grass, Psychic, Fighting, Psychic];
    let mewtwo_x_energy = vec![Fighting, Psychic];
    let board = || {
        get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::PC002MegaMewtwoYEx).with_energy(vec![Psychic]),
                PlayedCard::from_id(CardId::A1115Abra).with_energy(abra_energy.clone()),
                PlayedCard::from_id(CardId::C1056MegaMewtwoXEx).with_energy(mewtwo_x_energy.clone()),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        )
    };
    let (actor, choices) = play_and_choices(&mut board(), CardId::PC009GenomeConverterY);
    assert_eq!(actor, 0);
    assert_eq!(
        kinds(&choices),
        vec![
            SimpleAction::MoveEnergy {
                from_in_play_idx: 1,
                to_in_play_idx: 0,
                energy_type: Psychic,
                amount: 3
            },
            SimpleAction::MoveEnergy {
                from_in_play_idx: 2,
                to_in_play_idx: 0,
                energy_type: Psychic,
                amount: 1
            },
        ]
    );
    for (chosen, moved, left, other) in [
        (1, 3, vec![Grass, Fighting], mewtwo_x_energy.clone()),
        (2, 1, vec![Fighting], abra_energy.clone()),
    ] {
        let mut game = board();
        let (_, choices) = play_and_choices(&mut game, CardId::PC009GenomeConverterY);
        game.apply_action(&choices[chosen - 1]);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy, vec![Psychic; 1 + moved], "source {chosen}");
        let source = state.in_play_pokemon[0][chosen].as_ref().unwrap();
        assert_eq!(sorted(source.attached_energy.clone()), sorted(left), "source {chosen}");
        let untouched = state.in_play_pokemon[0][3 - chosen].as_ref().unwrap();
        assert_eq!(untouched.attached_energy, other, "source {chosen}");
    }
}

/// Poké Mart Guy (C1 129 / C1 169) searches by name for "Super Potion", "Max Repel" or "Full Heal";
/// a Super Potion it finds can now be played.
#[test]
fn test_poke_mart_guy_finds_a_super_potion_that_can_be_played() {
    for mart_guy in [CardId::C1129PokeMartGuy, CardId::C1169PokeMartGuy] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_damage(30)
                .with_energy(vec![EnergyType::Grass])],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(mart_guy)];
        state.decks[0].cards = vec![get_card_by_enum(CardId::C1120SuperPotion)];
        game.set_state(state);
        play_trainer(&mut game, 0, trainer_from_id(mart_guy));
        let state = game.get_state_clone();
        assert_eq!(state.hands[0], vec![get_card_by_enum(CardId::C1120SuperPotion)], "{mart_guy:?}");
        let (_, actions) = state.generate_possible_actions();
        assert!(
            actions.iter().any(|a| matches!(&a.action,
                SimpleAction::Play { trainer_card } if trainer_card.id == "C1 120")),
            "{mart_guy:?}"
        );
    }
}

/// The four Items are Complete, with no known limitation.
#[test]
fn test_c1_items_printings_report_complete() {
    for id in [
        CardId::C1120SuperPotion,
        CardId::C1121MaxRepel,
        CardId::C1122FullHeal,
        CardId::PC009GenomeConverterY,
    ] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}
