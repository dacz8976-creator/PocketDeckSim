// Lunala (C1 066, C1 198, P-C 008) - Wings of the Moone (R8-08e): "Move all Energy from this Pokémon to your Benched
// Pokémon in any way you like." Upstream's two tests (#438, 20d1857: tests/pokemon/c1_attacks/lunala.rs) with the
// helpers of upstream's c1_attacks/mod.rs, as c1_remaining_types_test.rs ports them, and one change: the fork offers the
// Energy in a fixed order (design r808p2 §B.2, coordinator-088 Q2), the lowest Energy type on the Active Pokémon first, one
// Energy per choice, destinations never decreasing within a type. So on [P][P][W] the first choice is the [W] to either
// Benched Pokémon (2 choices; upstream 4), and the script moves the [W] first. Then the fork's tests (the design's
// N1-N15): every end board against brute force (a gapped Bench too), the order and the floor, single-choice frames
// applied without a decision, each move one certain branch with no game randomness, Rocky Helmet and Perish Body after
// the last move, the defender's Knock Out and a winning one after the last move, Carefree Steps leaving the 110 no
// damage target (no reaction frame below the chain), no Energy, Confusion, Mew ex's copy, both seats' revealed
// knowledge, km3 and W at every frame, the 4 [P] / 3 Bench branching pin, the printings' status, and the two smoke
// records of §C.1 (written to the file named by LUNALA_SMOKE_OUT when it is set; legality is all they assert).
use std::{
    cell::RefCell,
    collections::{BTreeMap, BTreeSet},
    fmt::Write as _,
    rc::Rc,
    time::Instant,
};

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{
        Card,
        EnergyType::{self, Lightning, Psychic, Water},
        PlayedCard, StatusCondition,
    },
    observation::canonical_actions,
    players::{create_players, Player, PlayerCode},
    protocol::PublicEvent,
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board, play_trainer, trainer_from_id},
    Deck, Game, State,
};
use rand::{rngs::StdRng, SeedableRng};

/// Damage on a Pokémon, in place of upstream's `public_details().damage`: its full HP (the remaining HP after
/// setting it above the maximum, which clamps to the full HP) less its remaining HP.
trait Taken {
    fn taken(&self) -> u32;
}
impl Taken for PlayedCard {
    fn taken(&self) -> u32 {
        self.clone().with_remaining_hp(u32::MAX).get_remaining_hp() - self.get_remaining_hp()
    }
}

// Upstream's tests/pokemon/c1_attacks/mod.rs.

// Extra HP isolates the attack's damage from knockouts and promotion choices.
fn durable_of(id: CardId) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(id), 0, 1000, vec![], false, vec![])
}
fn durable() -> PlayedCard {
    durable_of(CardId::A1211Snorlax)
}
fn ready(id: CardId, index: usize) -> PlayedCard {
    let Card::Pokemon(p) = get_card_by_enum(id) else {
        panic!("Pokémon required")
    };
    PlayedCard::from_id(id).with_energy(p.attacks[index].energy_required.clone())
}
fn board(ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> Game<'static> {
    get_initialized_game_with_board(0, 0, 3, ours, theirs)
}
fn attack(game: &mut Game<'static>, id: CardId, index: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, index),
        is_stack: false,
    });
}
fn defender_damage(game: &Game<'static>) -> u32 {
    game.get_state_clone().get_active(1).taken()
}

// Upstream's tests/pokemon/c1_attacks/lunala.rs: `move_to`, then its two tests.

fn move_to(game: &mut Game<'static>, energy: EnergyType, to: usize) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let chosen = choices
        .into_iter()
        .find(|choice| {
            matches!(&choice.action, SimpleAction::MoveActiveEnergyToBenchAndReoffer {
                to_in_play_idx, energy_type
            } if *to_in_play_idx == to && *energy_type == energy)
        })
        .expect("a choice moving that Energy to that Pokémon");
    game.apply_action(&chosen);
}

#[test]
fn wings_of_the_moone_moves_every_energy_to_the_bench_in_any_way_on_every_printing() {
    for id in LUNALA {
        let mut game = board(
            vec![
                PlayedCard::from_id(id).with_energy(vec![
                    EnergyType::Psychic,
                    EnergyType::Psychic,
                    EnergyType::Water,
                ]),
                durable(),
                durable(),
            ],
            vec![durable()],
        );
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), 110, "{id:?}");

        // Fork: [W] is the lowest Energy type there, so it moves first, to either of 2 Benched Pokémon (upstream: 2
        // types x 2 targets), and there is no way to stop with Energy left on Lunala.
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        assert_eq!(choices.len(), 2, "{id:?}");
        move_to(&mut game, EnergyType::Water, 1);
        move_to(&mut game, EnergyType::Psychic, 1);
        move_to(&mut game, EnergyType::Psychic, 2);

        let state = game.get_state_clone();
        assert!(state.get_active(0).attached_energy.is_empty(), "{id:?}");
        let attached = |idx: usize| {
            let mut e = state.in_play_pokemon[0][idx]
                .as_ref()
                .unwrap()
                .attached_energy
                .clone();
            e.sort_by_key(|t| format!("{t:?}"));
            e
        };
        assert_eq!(attached(1), vec![EnergyType::Psychic, EnergyType::Water]);
        assert_eq!(attached(2), vec![EnergyType::Psychic]);
    }
}

#[test]
fn wings_of_the_moone_keeps_its_energy_without_a_benched_pokemon() {
    let id = CardId::C1066Lunala;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 110);
    assert_eq!(
        game.get_state_clone().get_active(0).attached_energy.len(),
        2
    );
}

// The fork's tests.

const LUNALA: [CardId; 3] = [CardId::C1066Lunala, CardId::C1198Lunala, CardId::PC008Lunala];

fn lunala(energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::from_id(CardId::C1066Lunala).with_energy(energy)
}

fn is_wings_move(action: &SimpleAction) -> bool {
    matches!(action, SimpleAction::MoveActiveEnergyToBenchAndReoffer { .. })
}

/// The Wings of the Moone choices offered now, as (Energy type, Benched Pokémon) in the frame's order; empty when no
/// such choice is on top.
fn wings_offer(state: &State) -> Vec<(EnergyType, usize)> {
    let (_, actions) = state.generate_possible_actions();
    actions
        .iter()
        .filter_map(|action| match action.action {
            SimpleAction::MoveActiveEnergyToBenchAndReoffer {
                to_in_play_idx,
                energy_type,
            } => Some((energy_type, to_in_play_idx)),
            _ => None,
        })
        .collect()
}

/// Whether any frame on the stack still holds a Wings of the Moone choice.
fn wings_frame_left(state: &State) -> bool {
    state
        .move_generation_stack
        .iter()
        .any(|(_, choices)| choices.iter().any(is_wings_move))
}

/// The Energy on `player`'s Pokémon at `in_play_idx`, sorted in `EnergyType`'s order (empty for an empty slot).
fn sorted_energy(state: &State, player: usize, in_play_idx: usize) -> Vec<EnergyType> {
    let mut energy = state.in_play_pokemon[player][in_play_idx]
        .as_ref()
        .map(|pokemon| pokemon.attached_energy.clone())
        .unwrap_or_default();
    energy.sort();
    energy
}

/// Applies the forced `ResolveAttackRetaliation` frame the chain leaves below it: the attack's reactions, then its
/// Knock Outs.
fn resolve_retaliation(game: &mut Game<'static>) {
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    assert!(
        matches!(
            actions.as_slice(),
            [Action {
                action: SimpleAction::ResolveAttackRetaliation { .. },
                ..
            }]
        ),
        "{actions:?}"
    );
    game.apply_action(&actions[0]);
}

/// Player 0's Lunala holding `energy` uses Wings of the Moone (game from `seed`) against a 1000-HP Snorlax, with a
/// 1000-HP Snorlax in each Bench slot of `bench` and the other slots empty.
fn after_wings(seed: u64, energy: Vec<EnergyType>, bench: &[usize]) -> Game<'static> {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![lunala(energy)], vec![durable()]);
    let mut state = game.get_state_clone();
    for &in_play_idx in bench {
        state.in_play_pokemon[0][in_play_idx] = Some(durable());
    }
    game.set_state(state);
    attack(&mut game, CardId::C1066Lunala, 0);
    assert_eq!(defender_damage(&game), 110);
    game
}

/// Every path of the Wings of the Moone chain from `state` (a choice on top), through `Game::apply_action`: counts the
/// decision nodes and those of them with two or more choices, and collects every end state.
fn explore(state: &State, nodes: &mut usize, real: &mut usize, leaves: &mut Vec<State>) {
    let (actor, actions) = state.generate_possible_actions();
    if !actions.iter().any(|action| is_wings_move(&action.action)) {
        leaves.push(state.clone());
        return;
    }
    assert!(actor == 0 && actions.iter().all(|action| is_wings_move(&action.action)));
    *nodes += 1;
    if actions.len() > 1 {
        *real += 1;
    }
    for action in &actions {
        let mut game = Game::from_state(state.clone(), Vec::new(), 0);
        game.apply_action(action);
        explore(&game.get_state_clone(), nodes, real, leaves);
    }
}

type EndBoard = Vec<(usize, Vec<EnergyType>)>;

/// The Energy each Pokémon of `bench` holds at the end, sorted.
fn end_board(state: &State, bench: &[usize]) -> EndBoard {
    bench
        .iter()
        .map(|&in_play_idx| (in_play_idx, sorted_energy(state, 0, in_play_idx)))
        .collect()
}

/// Brute force: every map of each Energy (as an instance) to one Pokémon of `bench`, |bench|^|energy| of them, as end
/// boards.
fn brute_force_boards(energy: &[EnergyType], bench: &[usize]) -> BTreeSet<EndBoard> {
    let mut boards = BTreeSet::new();
    for map in 0..bench.len().pow(energy.len() as u32) {
        let mut board: EndBoard = bench.iter().map(|&in_play_idx| (in_play_idx, Vec::new())).collect();
        let mut rest = map;
        for &e in energy {
            board[rest % bench.len()].1.push(e);
            rest /= bench.len();
        }
        for (_, held) in &mut board {
            held.sort();
        }
        boards.insert(board);
    }
    boards
}

/// The product over the Energy types of C(k + b - 1, b - 1): a type's k Energy as a multiset on b Benched Pokémon.
fn board_count(energy: &[EnergyType], b: usize) -> usize {
    let mut per_type = BTreeMap::new();
    for e in energy {
        *per_type.entry(*e).or_insert(0usize) += 1;
    }
    let choose = |n: usize, k: usize| (0..k).fold(1, |acc, i| acc * (n - i) / (i + 1));
    per_type.values().map(|&k| choose(k + b - 1, b - 1)).product()
}

/// N1 (design §B.2): the chain's end boards are exactly those of brute force, each reached by one path, as many as the
/// product formula says, on [P][P] / Bench 1-2 (3), upstream's [P][P][W] / Bench 1-2 (6), [W][L][P][P] / Bench 1-3 (54)
/// and [P][P][P] on a gapped Bench, slots 1 and 3 (4). Every end state has an empty Active Pokémon and differs from the
/// others in its Energy alone.
#[test]
fn test_wings_of_the_moone_end_boards_equal_brute_force() {
    let cases = [
        (vec![Psychic, Psychic], vec![1, 2], 3),
        (vec![Psychic, Psychic, Water], vec![1, 2], 6),
        (vec![Water, Lightning, Psychic, Psychic], vec![1, 2, 3], 54),
        (vec![Psychic, Psychic, Psychic], vec![1, 3], 4),
    ];
    for (energy, bench, expected) in cases {
        let start = after_wings(0, energy.clone(), &bench).get_state_clone();
        let (mut nodes, mut real, mut leaves) = (0, 0, Vec::new());
        explore(&start, &mut nodes, &mut real, &mut leaves);
        let boards: BTreeSet<EndBoard> = leaves.iter().map(|leaf| end_board(leaf, &bench)).collect();
        assert_eq!(boards, brute_force_boards(&energy, &bench), "{energy:?} to {bench:?}");
        assert_eq!(leaves.len(), boards.len(), "{energy:?}: one path per end board");
        assert_eq!(leaves.len(), board_count(&energy, bench.len()), "{energy:?}");
        assert_eq!(leaves.len(), expected, "{energy:?}");
        let without_energy = |leaf: &State| {
            let mut leaf = leaf.clone();
            for pokemon in leaf.in_play_pokemon[0].iter_mut().flatten() {
                pokemon.attached_energy.clear();
            }
            leaf
        };
        for leaf in &leaves {
            assert!(leaf.get_active(0).attached_energy.is_empty(), "{energy:?}");
            assert!(
                without_energy(leaf) == without_energy(&leaves[0]),
                "{energy:?}: end states differ in more than their Energy"
            );
        }
    }
}

/// N10: a branching pin. Four [P] on three Benched Pokémon: 20 decision nodes, 10 of them with two or more choices,
/// and 15 end boards (upstream's free order: 40 nodes and 81 paths).
#[test]
fn test_wings_of_the_moone_four_psychic_on_three_benched_has_20_nodes_and_15_end_boards() {
    let start = after_wings(0, vec![Psychic; 4], &[1, 2, 3]).get_state_clone();
    let (mut nodes, mut real, mut leaves) = (0, 0, Vec::new());
    explore(&start, &mut nodes, &mut real, &mut leaves);
    assert_eq!((nodes, real, leaves.len()), (20, 10, 15));
}

/// N2: the first choice offers only the lowest Energy type on Lunala ([W] before [L] before [P], whatever the order of
/// attachment), to every Benched Pokémon; a new type starts again from slot 1 (here after the [W] and the [L] went to
/// slot 3); within a type nothing is offered below the last destination. On the gapped Bench (slots 1 and 3) the
/// first choice offers 1 and 3, a move to 1 keeps both, and after a move to 3 only 3 is left.
#[test]
fn test_wings_of_the_moone_offers_the_lowest_type_from_its_last_destination_on() {
    let every = |energy_type| vec![(energy_type, 1), (energy_type, 2), (energy_type, 3)];
    let mut game = after_wings(0, vec![Psychic, Lightning, Water, Psychic], &[1, 2, 3]);
    assert_eq!(wings_offer(&game.get_state_clone()), every(Water));
    move_to(&mut game, Water, 3);
    assert_eq!(wings_offer(&game.get_state_clone()), every(Lightning));
    move_to(&mut game, Lightning, 3);
    assert_eq!(wings_offer(&game.get_state_clone()), every(Psychic));
    move_to(&mut game, Psychic, 2);
    assert_eq!(wings_offer(&game.get_state_clone()), vec![(Psychic, 2), (Psychic, 3)]);
    move_to(&mut game, Psychic, 3);
    let state = game.get_state_clone();
    assert!(wings_offer(&state).is_empty() && !wings_frame_left(&state));
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic]);
    assert_eq!(sorted_energy(&state, 0, 3), vec![Water, Lightning, Psychic]);

    let mut game = after_wings(0, vec![Psychic; 3], &[1, 3]);
    assert_eq!(wings_offer(&game.get_state_clone()), vec![(Psychic, 1), (Psychic, 3)]);
    move_to(&mut game, Psychic, 1);
    assert_eq!(wings_offer(&game.get_state_clone()), vec![(Psychic, 1), (Psychic, 3)]);
    move_to(&mut game, Psychic, 3);
    assert_eq!(wings_offer(&game.get_state_clone()), vec![(Psychic, 3)]);
    move_to(&mut game, Psychic, 3);
    let state = game.get_state_clone();
    assert!(wings_offer(&state).is_empty());
    assert_eq!(sorted_energy(&state, 0, 1), vec![Psychic]);
    assert_eq!(sorted_energy(&state, 0, 3), vec![Psychic, Psychic]);
}

/// Picks the Benched Pokémon furthest along at each Wings of the Moone choice, and keeps seat 0's public events.
#[derive(Debug)]
struct Furthest {
    seat: usize,
    events: Rc<RefCell<Vec<PublicEvent>>>,
}

impl Player for Furthest {
    fn get_deck(&self) -> Deck {
        Deck::default()
    }

    fn on_public_event(&mut self, event: &PublicEvent) {
        if self.seat == 0 {
            self.events.borrow_mut().push(*event);
        }
    }

    fn decide_omniscient(&mut self, _: &mut StdRng, _: &State, actions: &[Action]) -> Action {
        actions
            .iter()
            .max_by_key(|action| match action.action {
                SimpleAction::MoveActiveEnergyToBenchAndReoffer { to_in_play_idx, .. } => to_in_play_idx,
                _ => 0,
            })
            .unwrap()
            .clone()
    }
}

/// Plays the rest of the chain through `Game::play_tick` with `Furthest` in both seats: the end state, and each tick's
/// action with its public event.
fn chain_through_play_tick(state: State) -> (State, Vec<(Action, PublicEvent)>) {
    let events = Rc::new(RefCell::new(Vec::new()));
    let players = (0..2)
        .map(|seat| {
            Box::new(Furthest {
                seat,
                events: events.clone(),
            }) as Box<dyn Player>
        })
        .collect();
    let mut game = Game::from_state(state, players, 0);
    let mut ticks = Vec::new();
    while !wings_offer(&game.get_state_clone()).is_empty() {
        let action = game.play_tick();
        let event = *events.borrow().last().expect("seat 0 saw the action");
        ticks.push((action, event));
    }
    (game.get_state_clone(), ticks)
}

/// N2 and N5: four [P] on three Benched Pokémon, always to the furthest: one real decision (to slot 3, of 3 choices),
/// then three frames that offer only slot 3 (the floor), which `play_tick` applies without asking. With one Benched
/// Pokémon there is no decision at all. No move advances the game's random number generator (N6).
#[test]
fn test_wings_of_the_moone_single_choice_frames_are_applied_without_a_decision() {
    let (end, ticks) = chain_through_play_tick(after_wings(0, vec![Psychic; 4], &[1, 2, 3]).get_state_clone());
    let choices: Vec<bool> = ticks.iter().map(|(_, event)| event.was_choice).collect();
    assert_eq!(choices, vec![true, false, false, false]);
    assert!(ticks.iter().all(|(action, event)| is_wings_move(&action.action) && !event.chance));
    assert_eq!(sorted_energy(&end, 0, 3), vec![Psychic; 4]);

    let (end, ticks) = chain_through_play_tick(
        after_wings(0, vec![Psychic, Psychic, Water], &[2]).get_state_clone(),
    );
    assert_eq!(ticks.len(), 3);
    assert!(ticks.iter().all(|(_, event)| !event.was_choice && !event.chance));
    assert!(end.get_active(0).attached_energy.is_empty());
    assert_eq!(sorted_energy(&end, 0, 2), vec![Water, Psychic, Psychic]);
}

/// N6: every offered move, at every step of a [W][L][P][P] chain on three Benched Pokémon, forecasts one branch with
/// probability 1.
#[test]
fn test_wings_of_the_moone_each_move_is_one_certain_branch() {
    let mut game = after_wings(0, vec![Water, Lightning, Psychic, Psychic], &[1, 2, 3]);
    let mut steps = 0;
    while !wings_offer(&game.get_state_clone()).is_empty() {
        let state = game.get_state_clone();
        let (_, actions) = state.generate_possible_actions();
        for action in &actions {
            let (probabilities, _) = try_forecast_action(&state, action).unwrap().into_branches();
            assert_eq!(probabilities, vec![1.0], "{}", action.action);
        }
        game.apply_action(&actions[0]);
        steps += 1;
    }
    assert_eq!(steps, 4);
}

/// N3 (divergence D8): Rocky Helmet (A2 148) on the defender, Lunala at 20 HP. The Helmet's 20 waits for the last
/// move, so every Energy reaches the Bench and only then is Lunala Knocked Out (upstream skips the move once the
/// attacker is Knocked Out). The opponent takes the point and player 0 promotes.
#[test]
fn test_wings_of_the_moone_moves_every_energy_before_rocky_helmet_knocks_lunala_out() {
    let mut game = board(
        vec![
            lunala(vec![Psychic, Psychic, Water]).with_remaining_hp(20),
            durable(),
            durable(),
        ],
        vec![durable().with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
    );
    attack(&mut game, CardId::C1066Lunala, 0);
    assert_eq!(defender_damage(&game), 110);
    for (energy, to) in [(Water, 1), (Psychic, 1), (Psychic, 2)] {
        assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 20);
        move_to(&mut game, energy, to);
    }
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 20, "the Helmet waits for the reaction frame");
    assert_eq!(state.points, [0, 0]);
    resolve_retaliation(&mut game);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[0][0].is_none(), "the Helmet's 20 Knocks Lunala Out");
    assert_eq!(state.points, [0, 1]);
    assert_eq!(sorted_energy(&state, 0, 1), vec![Water, Psychic]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic]);
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(actions
        .iter()
        .all(|action| matches!(action.action, SimpleAction::Promote { player: 0, .. })));
}

/// N4: the 110 Knocks Out the defender (Bulbasaur, 70 HP). Its Knock Out, the point and the opponent's promotion all
/// come after the last move: no catch-all Knock Out check removes it in between.
#[test]
fn test_wings_of_the_moone_knock_out_resolves_after_the_last_move() {
    let mut game = board(
        vec![lunala(vec![Psychic, Psychic]), durable(), durable()],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), durable(), durable()],
    );
    attack(&mut game, CardId::C1066Lunala, 0);
    for to in [1, 2] {
        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[1][0].is_some(), "the Knocked Out Bulbasaur is still in play");
        assert_eq!(state.points, [0, 0]);
        move_to(&mut game, Psychic, to);
    }
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_some());
    assert_eq!(state.points, [0, 0]);
    resolve_retaliation(&mut game);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points, [1, 0]);
    assert_eq!(sorted_energy(&state, 0, 1), vec![Psychic]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic]);
    let (actor, actions) = state.generate_possible_actions();
    assert_eq!(actor, 1, "the opponent promotes");
    assert_eq!(actions.len(), 2);
    assert!(actions
        .iter()
        .all(|action| matches!(action.action, SimpleAction::Promote { player: 1, .. })));
}

/// N14: Lunala's 110 takes the last point. Every move is still offered and applied first (the game is not over while
/// a choice is offered), then the Knock Out, the third point and the win; no Wings of the Moone frame is left once the
/// game is over.
#[test]
fn test_wings_of_the_moone_winning_knock_out_comes_after_the_last_move() {
    let mut game = board(
        vec![lunala(vec![Psychic, Psychic, Water]), durable(), durable()],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), durable()],
    );
    let mut state = game.get_state_clone();
    state.points = [2, 0];
    game.set_state(state);
    attack(&mut game, CardId::C1066Lunala, 0);
    for (energy, to) in [(Water, 2), (Psychic, 1), (Psychic, 1)] {
        assert!(!game.is_game_over());
        assert_eq!(game.get_state_clone().points, [2, 0]);
        move_to(&mut game, energy, to);
    }
    assert!(!game.is_game_over(), "the Knock Out waits for the reaction frame");
    resolve_retaliation(&mut game);
    let state = game.get_state_clone();
    assert!(game.is_game_over());
    assert!(matches!(state.winner, Some(GameOutcome::Win(0))));
    assert_eq!(state.points[0], 3);
    assert!(state.get_active(0).attached_energy.is_empty());
    assert_eq!(sorted_energy(&state, 0, 1), vec![Psychic, Psychic]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Water]);
    assert!(!wings_frame_left(&state));
}

/// N15 (divergence D8): Galarian Cursola (A4a 035) at 20 HP is Knocked Out by the 110, and on a seed whose Perish Body
/// coin is heads (recorded in the reaction frame) every Energy still reaches the Bench before Lunala is Knocked Out.
/// Each player takes a point.
#[test]
fn test_wings_of_the_moone_moves_every_energy_before_perish_body_knocks_lunala_out() {
    let mut game = (0..40)
        .find_map(|seed| {
            let mut game = get_initialized_game_with_board(
                seed,
                0,
                3,
                vec![lunala(vec![Psychic, Psychic, Water]), durable(), durable()],
                vec![
                    PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(20),
                    durable(),
                ],
            );
            attack(&mut game, CardId::C1066Lunala, 0);
            let heads = game.get_state_clone().move_generation_stack.iter().any(|(_, choices)| {
                choices.iter().any(|choice| {
                    matches!(choice, SimpleAction::ResolveAttackRetaliation { perish_body_heads: true, .. })
                })
            });
            heads.then_some(game)
        })
        .expect("some seed flips Perish Body heads");
    for (energy, to) in [(Water, 1), (Psychic, 2), (Psychic, 2)] {
        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[0][0].is_some() && state.in_play_pokemon[1][0].is_some());
        move_to(&mut game, energy, to);
    }
    resolve_retaliation(&mut game);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[0][0].is_none(), "Perish Body Knocks Lunala Out");
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points, [1, 1]);
    assert_eq!(sorted_energy(&state, 0, 1), vec![Water]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic, Psychic]);
}

/// The defender is Meowth (B2 124), whose Carefree Steps reads "If any damage is done to this Pokémon by attacks, flip a
/// coin. If heads, prevent that damage." On heads the 110 has no damage target left, so no `ResolveAttackRetaliation`
/// frame is put below the chain and every move runs under the end-of-action Knock Out check. Nothing was damaged, so the
/// chain still moves every Energy and leaves only the turn's end to offer. On tails the frame is there and Meowth's Knock
/// Out waits for it. Both happen over 40 seeds.
#[test]
fn test_wings_of_the_moone_runs_without_a_reaction_frame_when_carefree_steps_prevents_the_damage() {
    let (mut prevented, mut damaged) = (0, 0);
    for seed in 0..40 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![lunala(vec![Psychic, Psychic, Water]), durable(), durable()],
            vec![PlayedCard::from_id(CardId::B2124Meowth), durable()],
        );
        attack(&mut game, CardId::C1066Lunala, 0);
        let state = game.get_state_clone();
        let reaction_frame = state.move_generation_stack.iter().any(|(_, choices)| {
            choices
                .iter()
                .any(|choice| matches!(choice, SimpleAction::ResolveAttackRetaliation { .. }))
        });
        assert_eq!(wings_offer(&state), vec![(Water, 1), (Water, 2)], "seed {seed}");
        if defender_damage(&game) > 0 {
            damaged += 1;
            assert!(reaction_frame, "seed {seed}");
            assert!(state.in_play_pokemon[1][0].is_some(), "seed {seed}: the Knock Out waits for the reaction frame");
            continue;
        }
        prevented += 1;
        assert!(!reaction_frame, "seed {seed}");
        for (energy, to) in [(Water, 1), (Psychic, 1), (Psychic, 2)] {
            move_to(&mut game, energy, to);
        }
        let state = game.get_state_clone();
        assert!(state.get_active(0).attached_energy.is_empty(), "seed {seed}");
        assert_eq!(sorted_energy(&state, 0, 1), vec![Water, Psychic], "seed {seed}");
        assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic], "seed {seed}");
        assert!(state.move_generation_stack.is_empty(), "seed {seed}: {:?}", state.move_generation_stack);
        assert_eq!((state.get_active(1).taken(), state.points), (0, [0, 0]), "seed {seed}");
        let (_, actions) = state.generate_possible_actions();
        assert!(
            matches!(actions.as_slice(), [Action { action: SimpleAction::EndTurn, .. }]),
            "seed {seed}: {actions:?}"
        );
    }
    assert!(prevented > 0 && damaged > 0, "{prevented} prevented, {damaged} damaged");
}

/// N11 and N5: Lunala cannot attack with no Energy in play (the cost is [P][P]); applied directly, the attack does its
/// 110 and offers nothing. With Energy but no Benched Pokémon nothing is offered either and the Energy stays. Either
/// way no frame is left behind: the reactions resolve at once and the turn's end is all that is offered. The helper's
/// own test is in attack_helpers.rs.
#[test]
fn test_wings_of_the_moone_with_no_energy_or_no_bench_offers_nothing() {
    for (ours, energy_left) in [
        (vec![lunala(vec![]), durable(), durable()], 0),
        (vec![lunala(vec![Psychic, Psychic, Water])], 3),
    ] {
        let mut game = board(ours, vec![durable()]);
        attack(&mut game, CardId::C1066Lunala, 0);
        assert_eq!(defender_damage(&game), 110);
        let state = game.get_state_clone();
        assert!(state.move_generation_stack.is_empty(), "{:?}", state.move_generation_stack);
        assert_eq!(state.get_active(0).attached_energy.len(), energy_left);
        let (_, actions) = state.generate_possible_actions();
        assert!(
            matches!(actions.as_slice(), [Action { action: SimpleAction::EndTurn, .. }]),
            "{actions:?}"
        );
    }
}

/// N12: a Confused Lunala. On tails the attack does nothing: no damage, no choice, and the Energy stays. On heads the
/// chain runs as usual. Both happen over 20 seeds.
#[test]
fn test_confused_lunala_moves_its_energy_only_when_the_attack_goes_ahead() {
    let (mut failed, mut used) = (0, 0);
    for seed in 0..20 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                lunala(vec![Psychic, Psychic, Water]).with_status_condition(StatusCondition::Confused),
                durable(),
                durable(),
            ],
            vec![durable()],
        );
        attack(&mut game, CardId::C1066Lunala, 0);
        let state = game.get_state_clone();
        if defender_damage(&game) == 0 {
            failed += 1;
            assert!(!wings_frame_left(&state), "seed {seed}");
            assert_eq!(state.get_active(0).attached_energy.len(), 3, "seed {seed}");
        } else {
            used += 1;
            assert_eq!(defender_damage(&game), 110, "seed {seed}");
            assert_eq!(wings_offer(&state), vec![(Water, 1), (Water, 2)], "seed {seed}");
        }
    }
    assert!(failed > 0 && used > 0, "{failed} failed, {used} went ahead");
}

/// N13: Mew ex (A1a 032) copies an opposing Lunala's Wings of the Moone with Genome Hacking ("Choose 1 of your
/// opponent's Active Pokémon's attacks and use it as this attack."). "This Pokémon" is Mew ex, so Mew ex's own Energy
/// goes to Mew ex's own Bench, and the opposing Lunala keeps its Energy.
#[test]
fn test_wings_of_the_moone_copied_by_mew_ex_moves_mew_exs_own_energy() {
    let mew = CardId::A1a032MewEx;
    let mut game = board(
        vec![PlayedCard::from_id(mew).with_energy(vec![Psychic; 3]), durable(), durable()],
        vec![durable_of(CardId::C1066Lunala).with_energy(vec![Psychic, Psychic])],
    );
    attack(&mut game, mew, 1);
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    let wings = actions
        .into_iter()
        .find(|action| matches!(&action.action, SimpleAction::Attack(copied) if copied.title == "Wings of the Moone"))
        .expect("Genome Hacking offers Wings of the Moone");
    game.apply_action(&wings);
    assert_eq!(defender_damage(&game), 110);
    assert_eq!(wings_offer(&game.get_state_clone()), vec![(Psychic, 1), (Psychic, 2)]);
    for to in [1, 2, 2] {
        move_to(&mut game, Psychic, to);
    }
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_id(), "A1a 032");
    assert!(state.get_active(0).attached_energy.is_empty());
    assert_eq!(sorted_energy(&state, 0, 1), vec![Psychic]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic, Psychic]);
    assert_eq!(sorted_energy(&state, 1, 0), vec![Psychic, Psychic]);
}

/// N7: player 0 knows the opponent's hand (Hand Scope, P-A 003) and its own top 3 cards (Pokédex, P-A 004). Neither
/// seat's revealed knowledge changes through the attack and every move: the moves' names contain "hand"
/// (`MoveActiveEnergyToBenchAndReoffer`), which the knowledge update must not read as a hand change.
#[test]
fn test_wings_of_the_moone_leaves_both_seats_revealed_knowledge_alone() {
    let mut game = board(
        vec![
            lunala(vec![Water, Lightning, Psychic, Psychic]),
            durable(),
            durable(),
            durable(),
        ],
        vec![durable()],
    );
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::PA003HandScope),
        get_card_by_enum(CardId::PA004PokedEx),
    ];
    state.hands[1] = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1225Sabrina),
    ];
    game.set_state(state);
    play_trainer(&mut game, 0, trainer_from_id(CardId::PA003HandScope));
    play_trainer(&mut game, 0, trainer_from_id(CardId::PA004PokedEx));
    let known = [game.observation(0).revealed, game.observation(1).revealed];
    assert_eq!(known[0].opponent_hand.len(), 2);
    assert_eq!(known[0].deck_top[0].len(), 3);
    attack(&mut game, CardId::C1066Lunala, 0);
    let mut steps = 0;
    loop {
        assert_eq!([game.observation(0).revealed, game.observation(1).revealed], known, "step {steps}");
        let (_, actions) = game.get_state_clone().generate_possible_actions();
        if !actions.iter().any(|action| is_wings_move(&action.action)) {
            break;
        }
        game.apply_action(actions.last().unwrap());
        steps += 1;
    }
    assert_eq!(steps, 4);
}

/// N9 (smoke): km3 and WeightedRandomPlayer pick an offered move at every frame of a [W][L][P][P] chain on three
/// Benched Pokémon, through `decision_fn` with each frame's observation.
#[test]
fn test_km3_and_weighted_random_pick_an_offered_move_at_every_frame() {
    for code in [PlayerCode::KM { max_depth: 3 }, PlayerCode::W] {
        let mut game = after_wings(0, vec![Water, Lightning, Psychic, Psychic], &[1, 2, 3]);
        let mut players = create_players(Deck::default(), Deck::default(), vec![code.clone(), code.clone()]);
        let mut steps = 0;
        loop {
            let (actor, mut actions) = game.get_state_clone().generate_possible_actions();
            if !actions.iter().any(|action| is_wings_move(&action.action)) {
                break;
            }
            canonical_actions(&mut actions);
            let observation = game.observation(actor);
            let chosen = players[actor].decision_fn(&mut StdRng::seed_from_u64(steps), &observation, &actions);
            assert!(actions.contains(&chosen), "{code:?} picked {chosen:?}");
            game.apply_action(&chosen);
            steps += 1;
        }
        assert_eq!(steps, 4, "{code:?}");
        assert!(game.get_state_clone().get_active(0).attached_energy.is_empty(), "{code:?}");
    }
}

/// N8: each printing is Complete, with no known limitation.
#[test]
fn test_lunala_printings_report_complete() {
    for id in LUNALA {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}

fn label(action: &Action) -> String {
    format!("{}|{}|{}", action.actor, action.is_stack, action.action)
}

/// Plays `state` with `code` in both seats through `Game::play_tick` until turn `until_turn` begins or the game is
/// over (at most 80 ticks), writing each tick's turn, actor, number of offered actions, pick and decision time.
fn smoke_game(out: &mut String, state: State, code: &PlayerCode, until_turn: u8) {
    let players = create_players(Deck::default(), Deck::default(), vec![code.clone(), code.clone()]);
    let mut game = Game::from_state(state, players, 0);
    for _ in 0..80 {
        let state = game.get_state_clone();
        if game.is_game_over() || state.turn_count >= until_turn {
            break;
        }
        let (actor, mut actions) = state.generate_possible_actions();
        canonical_actions(&mut actions);
        let started = Instant::now();
        let action = game.play_tick();
        let elapsed = started.elapsed().as_millis();
        assert!(actions.contains(&action), "{code:?} played an action it was not offered: {action:?}");
        let _ = writeln!(
            out,
            "  turn {} p{actor} of {}: {} ({elapsed} ms)",
            state.turn_count,
            actions.len(),
            label(&action)
        );
    }
    let state = game.get_state_clone();
    let _ = writeln!(
        out,
        "  end: turn {}, winner {:?}, points {:?}, player 0 Active {:?} with {:?}",
        state.turn_count,
        state.winner,
        state.points,
        state.in_play_pokemon[0][0].as_ref().map(|pokemon| pokemon.get_name()),
        state.in_play_pokemon[0][0].as_ref().map(|pokemon| pokemon.attached_energy.clone()),
    );
}

/// The two smoke records of design §C.1, recorded and not asserted beyond legality.
/// - R6: player 0 at 2 points, its Lunala holding `energy` with one Benched Pokémon, against a 70-HP Bulbasaur whose
///   Knock Out wins: does each searcher attack? With 3 Energy the chain is cut by km3's horizon at the attack root, so
///   the 110's Knock Out and the win are not priced there (risk R6); 2 Energy is recorded beside it.
/// - R6b: player 0's Bulbasaur (70 HP, [G]) faces player 1's ready Lunala at 2 points, with a Snorlax at its printed
///   150 HP (which survives the 110) on its Bench: what does each searcher do on its own turn, and how does player 1's
///   turn end (risk R6b)? The control row is the same board with Lunala holding no Energy, so it cannot attack on turn
///   4. A searcher that sees the lethal 110 can show it only as a difference between the two rows; the same pick in
///   both is no evidence either way (km3 searches no opponent ply at all). The no-Bench row is the ready Lunala with no
///   Benched Pokémon to take its Energy: its 110 Knocks Out at once, with no choice after the damage, so it shows
///   whether a searcher sees a lethal attack on this board at all.
/// Player 0's Energy Zone is spent for the turn in all of them, so the choice is only to attack, retreat or end the turn.
#[test]
fn smoke_record_searchers_at_and_against_a_lethal_wings_of_the_moone() {
    let mut out = String::new();
    let searchers = [
        ("km3", PlayerCode::KM { max_depth: 3 }),
        ("y3", PlayerCode::Y { max_depth: 3, opponent_ply: 3 }),
        ("x3", PlayerCode::X { max_depth: 3, opponent_ply: 3 }),
    ];
    for energy in [vec![Psychic; 3], vec![Psychic; 2]] {
        let game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![lunala(energy.clone()), PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        let mut state = game.get_state_clone();
        state.points = [2, 0];
        state.hands = [Vec::new(), Vec::new()];
        state.energy_zone[0].current = None;
        for (name, code) in &searchers {
            let _ = writeln!(
                out,
                "R6 {name}: player 0's Lunala {energy:?}, 1 Benched Bulbasaur, 2 points; player 1's Bulbasaur (70 HP) Active"
            );
            smoke_game(&mut out, state.clone(), code, 4);
        }
    }
    for (row, energy, benched) in [
        ("ready", vec![Psychic, Psychic], true),
        ("control", vec![], true),
        ("no-Bench", vec![Psychic, Psychic], false),
    ] {
        let mut theirs = vec![lunala(energy.clone())];
        if benched {
            theirs.push(durable());
        }
        let game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![
                PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
                PlayedCard::from_id(CardId::A1211Snorlax),
            ],
            theirs,
        );
        let mut state = game.get_state_clone();
        state.points = [0, 2];
        state.hands = [Vec::new(), Vec::new()];
        state.energy_zone[0].current = None;
        for (name, code) in &searchers {
            let _ = writeln!(
                out,
                "R6b {row} {name}: player 0's Bulbasaur [G] (70 HP) with a 150-HP Snorlax Benched; player 1's Lunala {energy:?}, {} Benched, 2 points",
                usize::from(benched)
            );
            smoke_game(&mut out, state.clone(), code, 5);
        }
    }
    print!("{out}");
    if let Ok(path) = std::env::var("LUNALA_SMOKE_OUT") {
        std::fs::write(path, &out).expect("the smoke record is written");
    }
}
