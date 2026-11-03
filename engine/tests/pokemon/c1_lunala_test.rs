// Lunala (C1 066, C1 198, P-C 008) - Wings of the Moone (R8-08e, reshaped in R8-08h): "Move all Energy from this
// Pokémon to your Benched Pokémon in any way you like." Upstream's two tests (#438, 20d1857:
// tests/pokemon/c1_attacks/lunala.rs) with the helpers of upstream's c1_attacks/mod.rs, as c1_remaining_types_test.rs
// ports them, and one change: the fork offers whole distributions (coordinator-131 option (a), coordinator-132 shape 3,
// design r808lun), not one Energy per choice. With at most 256 final boards one choice offers every final board;
// otherwise there is one choice per Energy type, lowest first, each offering every split of that type, the shape decided
// once when the attack resolves. So on [P][P][W] the first choice offers the 6 final boards (upstream: 4 one-Energy
// choices) and the script picks one. Then the fork's tests: every end board against brute force on both paths (one
// choice, and one type at a time, the latter also forced on every one-choice board), with no two paths alike and every
// end state exactly the start with only the moves (Soothing Wind receivers included); the shape decided once; branching
// pins; single-option choices applied without a decision; each distribution one certain branch with no game randomness;
// Rocky Helmet and Perish Body after the moves; the defender's Knock Out and a winning one after the moves; Carefree
// Steps leaving the 110 no damage target (no reaction frame below the choice); no Energy; Confusion; Mew ex's copy; both
// seats' revealed knowledge; km3 and W at every choice; the printings' status; and three smoke records (written to the
// files named by LUNALA_SMOKE_OUT, LUNALA_TIMES_OUT and LUNALA_HEAVY_TIMES_OUT when they are set; legality is all they
// assert).
use std::{
    cell::RefCell,
    collections::{BTreeMap, BTreeSet},
    fmt::Write as _,
    rc::Rc,
    sync::Mutex,
    time::Instant,
};

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{
        Card,
        EnergyType::{self, Colorless, Darkness, Fighting, Fire, Grass, Lightning, Psychic, Water},
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

// Upstream's tests/pokemon/c1_attacks/lunala.rs: its two tests, with `choose` (one whole distribution) in place of
// upstream's `move_to` (one Energy per choice).

/// One Wings of the Moone distribution: (amount, Energy type, Benched Pokémon) entries, lowest type first, then
/// ascending Benched Pokémon, no zero amounts.
type Moves = Vec<(u32, EnergyType, usize)>;

/// Applies the offered Wings of the Moone choice whose entries are `moves`.
fn choose(game: &mut Game<'static>, moves: &[(u32, EnergyType, usize)]) {
    let (actor, choices) = game.get_state_clone().generate_possible_actions();
    assert_eq!(actor, 0);
    let chosen = choices
        .into_iter()
        .find(|choice| {
            matches!(&choice.action, SimpleAction::DistributeActiveEnergyToBench { moves: offered }
                if offered.as_slice() == moves)
        })
        .unwrap_or_else(|| panic!("a choice moving {moves:?}"));
    game.apply_action(&chosen);
}

/// The 6 final boards of [P][P][W] on Benched Pokémon 1 and 2, as offered: the [W]'s splits vary slowest.
fn psychic_psychic_water_offer() -> Vec<Moves> {
    vec![
        vec![(1, Water, 2), (2, Psychic, 2)],
        vec![(1, Water, 2), (1, Psychic, 1), (1, Psychic, 2)],
        vec![(1, Water, 2), (2, Psychic, 1)],
        vec![(1, Water, 1), (2, Psychic, 2)],
        vec![(1, Water, 1), (1, Psychic, 1), (1, Psychic, 2)],
        vec![(1, Water, 1), (2, Psychic, 1)],
    ]
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

        // Fork: one choice of the 2 x 3 = 6 final boards (upstream: one Energy per choice, 2 types x 2 targets), and
        // no way to stop with Energy left on Lunala.
        assert_eq!(wings_offer(&game.get_state_clone()), psychic_psychic_water_offer(), "{id:?}");
        choose(&mut game, &[(1, Water, 1), (1, Psychic, 1), (1, Psychic, 2)]);

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

/// `count` Energy of each type listed, in the order listed.
fn energy_of(counts: &[(EnergyType, usize)]) -> Vec<EnergyType> {
    counts
        .iter()
        .flat_map(|&(energy_type, count)| std::iter::repeat(energy_type).take(count))
        .collect()
}

fn is_wings_move(action: &SimpleAction) -> bool {
    matches!(action, SimpleAction::DistributeActiveEnergyToBench { .. })
}

/// The Wings of the Moone choices offered now, as their entries in the frame's order; empty when no such choice is on
/// top.
fn wings_offer(state: &State) -> Vec<Moves> {
    let (_, actions) = state.generate_possible_actions();
    actions
        .into_iter()
        .filter_map(|action| match action.action {
            SimpleAction::DistributeActiveEnergyToBench { moves } => Some(moves),
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

/// Applies the forced `ResolveAttackRetaliation` frame the choice leaves below it: the attack's reactions, then its
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

/// Player 0's Lunala holding `energy` uses Wings of the Moone (game from `seed`) against a 1000-HP Snorlax, with each
/// Pokémon of `bench` in its Bench slot and the other slots empty.
fn after_wings_on(seed: u64, energy: Vec<EnergyType>, bench: &[(usize, PlayedCard)]) -> Game<'static> {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![lunala(energy)], vec![durable()]);
    let mut state = game.get_state_clone();
    for (in_play_idx, pokemon) in bench {
        state.in_play_pokemon[0][*in_play_idx] = Some(pokemon.clone());
    }
    game.set_state(state);
    attack(&mut game, CardId::C1066Lunala, 0);
    assert_eq!(defender_damage(&game), 110);
    game
}

/// The same with a 1000-HP Snorlax in each Bench slot of `bench`.
fn after_wings(seed: u64, energy: Vec<EnergyType>, bench: &[usize]) -> Game<'static> {
    let bench: Vec<(usize, PlayedCard)> = bench.iter().map(|&in_play_idx| (in_play_idx, durable())).collect();
    after_wings_on(seed, energy, &bench)
}

/// Every path of Wings of the Moone's choices from a state with one on top, through `Game::apply_action`.
#[derive(Default)]
struct Walk {
    /// Each decision node: its depth on the path (0 for the attack's own choice) and the entries it offered.
    nodes: Vec<(usize, Vec<Moves>)>,
    /// Each end state, with the number of decisions on its path.
    leaves: Vec<(usize, State)>,
}

impl Walk {
    /// (decision nodes, those of them with two or more options, end states).
    fn shape(&self) -> (usize, usize, usize) {
        let real = self.nodes.iter().filter(|(_, offer)| offer.len() > 1).count();
        (self.nodes.len(), real, self.leaves.len())
    }
}

fn explore(state: &State, depth: usize, walk: &mut Walk) {
    let (actor, actions) = state.generate_possible_actions();
    if !actions.iter().any(|action| is_wings_move(&action.action)) {
        walk.leaves.push((depth, state.clone()));
        return;
    }
    assert!(actor == 0 && actions.iter().all(|action| is_wings_move(&action.action)));
    walk.nodes.push((depth, wings_offer(state)));
    for action in &actions {
        let mut game = Game::from_state(state.clone(), Vec::new(), 0);
        game.apply_action(action);
        explore(&game.get_state_clone(), depth + 1, walk);
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

fn n_choose_k(n: usize, k: usize) -> usize {
    (0..k).fold(1, |acc, i| acc * (n - i) / (i + 1))
}

/// (type, count) of `energy`, lowest `EnergyType` first.
fn by_type(energy: &[EnergyType]) -> Vec<(EnergyType, usize)> {
    let mut per_type = BTreeMap::new();
    for e in energy {
        *per_type.entry(*e).or_insert(0usize) += 1;
    }
    per_type.into_iter().collect()
}

/// The product over the Energy types of C(k + b - 1, b - 1): a type's k Energy as a multiset on b Benched Pokémon.
fn board_count(energy: &[EnergyType], b: usize) -> usize {
    by_type(energy).iter().map(|&(_, k)| n_choose_k(k + b - 1, b - 1)).product()
}

/// Every way to put `count` Energy of `energy_type` on the Pokémon of `bench`, as entries in ascending Benched Pokémon
/// with no zero amounts: the test's own enumeration, not the engine's.
fn splits_of(energy_type: EnergyType, count: usize, bench: &[usize]) -> Vec<Moves> {
    let Some((&first, rest)) = bench.split_first() else {
        return if count == 0 { vec![Vec::new()] } else { Vec::new() };
    };
    (0..=count)
        .flat_map(|here| {
            splits_of(energy_type, count - here, rest).into_iter().map(move |tail| {
                let mut moves = Vec::new();
                if here > 0 {
                    moves.push((here as u32, energy_type, first));
                }
                moves.extend(tail);
                moves
            })
        })
        .collect()
}

/// A board for the end-board checks: Lunala's Energy, and each Bench slot's Pokémon as placed and as Soothing Wind
/// leaves it (the same card with no Special Condition). `soothing` is the Soothing Wind on the Bench, if any:
/// `Some(None)` cures a receiver of any Energy (Teal Mask Ogerpon ex), `Some(Some(t))` one that holds `t` (Comfey's
/// Flower Shield).
struct WingsBoard {
    energy: Vec<EnergyType>,
    bench: Vec<(usize, PlayedCard, PlayedCard)>,
    soothing: Option<Option<EnergyType>>,
}

impl WingsBoard {
    /// Lunala holding `energy`, with a 1000-HP Snorlax in each Bench slot of `slots`.
    fn plain(energy: Vec<EnergyType>, slots: &[usize]) -> Self {
        let bench = slots.iter().map(|&in_play_idx| (in_play_idx, durable(), durable())).collect();
        WingsBoard {
            energy,
            bench,
            soothing: None,
        }
    }

    fn slots(&self) -> Vec<usize> {
        self.bench.iter().map(|(in_play_idx, ..)| *in_play_idx).collect()
    }

    fn placed(&self) -> Vec<(usize, PlayedCard)> {
        self.bench.iter().map(|(in_play_idx, placed, _)| (*in_play_idx, placed.clone())).collect()
    }
}

/// Lunala holding `energy`, with `holder` (whose Soothing Wind is `soothing`) in slot 1 and a Poisoned Bulbasaur and
/// an Asleep 1000-HP Snorlax in slots 2 and 3 (Special Conditions set directly: Benched Pokémon cannot get them in
/// play).
fn soothing_board(energy: Vec<EnergyType>, holder: CardId, soothing: Option<EnergyType>) -> WingsBoard {
    let bulbasaur = PlayedCard::from_id(CardId::A1001Bulbasaur);
    WingsBoard {
        energy,
        bench: vec![
            (1, PlayedCard::from_id(holder), PlayedCard::from_id(holder)),
            (2, bulbasaur.clone().with_status_condition(StatusCondition::Poisoned), bulbasaur),
            (3, durable().with_status_condition(StatusCondition::Asleep), durable()),
        ],
        soothing: Some(soothing),
    }
}

/// The state Wings of the Moone must end in from `start` (the attack made, its first choice on top) on `end`: that
/// choice gone, Lunala's Energy gone, each Benched Pokémon as placed (or as Soothing Wind leaves it, when it covers what
/// the Pokémon received) with its new Energy in `EnergyType`'s order, and nothing else changed.
fn expected_end(start: &State, wings: &WingsBoard, end: &EndBoard) -> State {
    let mut expected = start.clone();
    expected.move_generation_stack.pop();
    expected.in_play_pokemon[0][0].as_mut().unwrap().attached_energy.clear();
    for (in_play_idx, gained) in end {
        let (_, placed, cured) = wings.bench.iter().find(|(slot, ..)| slot == in_play_idx).unwrap();
        let recovers = match wings.soothing {
            Some(None) => !gained.is_empty(),
            Some(Some(energy_type)) => gained.contains(&energy_type),
            None => false,
        };
        let mut pokemon = if recovers { cured.clone() } else { placed.clone() };
        pokemon.attached_energy.extend(gained.iter().copied());
        expected.in_play_pokemon[0][*in_play_idx] = Some(pokemon);
    }
    expected
}

/// Which way `check_end_boards` walks the choices.
#[derive(Clone, Copy, Debug, PartialEq)]
enum Path {
    /// As the attack offers them.
    AsOffered,
    /// The attack's first choice replaced by the splits of its lowest Energy type alone (built by `splits_of`, not by
    /// the engine), so the apply arm offers each later type one at a time: the per-type path on any board (design
    /// §D.5).
    ForcedPerType,
}

/// Condition 3 (coordinator-131) on `wings` along `path`, from the attack against a 1000-HP Snorlax:
/// - every option is in canonical order (no zero amount, strictly ascending (type, Benched Pokémon)), names an occupied
///   slot, and no two options of a choice are alike;
/// - one choice (as offered, at most 256 final boards): a single decision holding every type in every option, as many
///   options as final boards; one type at a time: one decision per type, the t-th holding the t-th type alone in each
///   of its C(k + b - 1, b - 1) options;
/// - the end boards equal brute force's, no two paths end alike, and there are as many as the product formula says;
/// - every end state has Lunala empty, no Wings of the Moone choice left, and equals `expected_end`.
///
/// Returns the end states by end board.
fn check_end_boards(wings: &WingsBoard, path: Path) -> BTreeMap<EndBoard, State> {
    let slots = wings.slots();
    let per_type = by_type(&wings.energy);
    let count = board_count(&wings.energy, slots.len());
    let label = format!("{per_type:?} on {slots:?}, {path:?}");
    // Through `Game::from_state`, as every state `explore` reaches, so the transient reveal queues match.
    let after = after_wings_on(0, wings.energy.clone(), &wings.placed()).get_state_clone();
    let start = Game::from_state(after, Vec::new(), 0).get_state_clone();
    for (in_play_idx, placed, _) in &wings.bench {
        assert!(start.in_play_pokemon[0][*in_play_idx].as_ref() == Some(placed), "{label}");
    }
    let mut from = start.clone();
    if path == Path::ForcedPerType {
        let (lowest, k) = per_type[0];
        let first = splits_of(lowest, k, &slots)
            .into_iter()
            .map(|moves| SimpleAction::DistributeActiveEnergyToBench { moves })
            .collect();
        let top = from.move_generation_stack.last_mut().expect("the attack's choice");
        assert!(top.1.iter().all(is_wings_move), "{label}");
        *top = (0, first);
    }
    let mut walk = Walk::default();
    explore(&from, 0, &mut walk);

    let one_choice = path == Path::AsOffered && count <= 256;
    let b = slots.len();
    for (depth, offer) in &walk.nodes {
        let held = if one_choice { per_type.clone() } else { vec![per_type[*depth]] };
        let options: usize = held.iter().map(|&(_, k)| n_choose_k(k + b - 1, b - 1)).product();
        assert_eq!(offer.len(), options, "{label}: options at depth {depth}");
        let distinct: BTreeSet<&Moves> = offer.iter().collect();
        assert_eq!(distinct.len(), offer.len(), "{label}: two options alike at depth {depth}");
        for moves in offer {
            assert!(
                moves.iter().all(|&(amount, _, to)| amount > 0 && slots.contains(&to))
                    && moves.windows(2).all(|pair| (pair[0].1, pair[0].2) < (pair[1].1, pair[1].2)),
                "{label}: {moves:?} is not canonical"
            );
            let mut moved = BTreeMap::new();
            for &(amount, energy_type, _) in moves {
                *moved.entry(energy_type).or_insert(0usize) += amount as usize;
            }
            assert_eq!(moved.into_iter().collect::<Vec<_>>(), held, "{label}: {moves:?} at depth {depth}");
        }
    }
    let decisions = if one_choice { 1 } else { per_type.len() };
    assert!(
        walk.leaves.iter().all(|(depth, _)| *depth == decisions),
        "{label}: a path of other than {decisions} decisions"
    );
    if one_choice {
        assert_eq!(walk.nodes.len(), 1, "{label}");
    }

    let mut ends = BTreeMap::new();
    for (_, leaf) in walk.leaves {
        assert!(leaf.get_active(0).attached_energy.is_empty() && !wings_frame_left(&leaf), "{label}");
        let end = end_board(&leaf, &slots);
        assert!(ends.insert(end.clone(), leaf).is_none(), "{label}: two paths end on {end:?}");
    }
    let boards: BTreeSet<EndBoard> = ends.keys().cloned().collect();
    assert!(boards == brute_force_boards(&wings.energy, &slots), "{label}: the end boards are not brute force's");
    assert_eq!(ends.len(), count, "{label}");
    for (end, leaf) in &ends {
        assert!(
            *leaf == expected_end(&start, wings, end),
            "{label}: the end state on {end:?} is not the start with only these moves"
        );
    }
    ends
}

/// Condition 3, one choice. On every board here the final boards number at most 256, so the attack offers all of them
/// as one choice. Along that path and along the forced per-type path `check_end_boards` holds, and both paths end in
/// the same states. Boards: [P]x3 on one Benched Pokémon (1), [P]x4 on three (15), [W][L][P][P] on three (54), [P]x3
/// on a gapped Bench, slots 1 and 3 (4), upstream's [P][P][W] on two (6), [W][P][P] with Comfey's Flower Shield ([P]
/// only) and with Teal Mask Ogerpon ex's Soothing Wind (any Energy) in slot 1 and a Poisoned and an Asleep receiver in
/// slots 2 and 3 (18 each), [W][L][P]x6 on three (252), and two boards of exactly 256: [R]x3 [W]x3 [L]x3 [P]x3 on the
/// gapped slots 1 and 3 (a count that read the slot number would be 10^4), and [G]x7 [W]x7 [P]x3 on slots 2 and 3.
#[test]
fn test_wings_of_the_moone_end_boards_equal_brute_force_in_one_choice() {
    let boards = [
        (WingsBoard::plain(vec![Psychic; 3], &[1]), 1),
        (WingsBoard::plain(vec![Psychic; 4], &[1, 2, 3]), 15),
        (WingsBoard::plain(vec![Water, Lightning, Psychic, Psychic], &[1, 2, 3]), 54),
        (WingsBoard::plain(vec![Psychic; 3], &[1, 3]), 4),
        (WingsBoard::plain(vec![Psychic, Psychic, Water], &[1, 2]), 6),
        (soothing_board(vec![Water, Psychic, Psychic], CardId::A3080Comfey, Some(Psychic)), 18),
        (soothing_board(vec![Water, Psychic, Psychic], CardId::B2017TealMaskOgerponEx, None), 18),
        (WingsBoard::plain(energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 6)]), &[1, 2, 3]), 252),
        (
            WingsBoard::plain(energy_of(&[(Fire, 3), (Water, 3), (Lightning, 3), (Psychic, 3)]), &[1, 3]),
            256,
        ),
        (WingsBoard::plain(energy_of(&[(Grass, 7), (Water, 7), (Psychic, 3)]), &[2, 3]), 256),
    ];
    for (wings, expected) in &boards {
        assert_eq!(board_count(&wings.energy, wings.bench.len()), *expected, "{:?}", wings.energy);
        let one_choice = check_end_boards(wings, Path::AsOffered);
        let per_type = check_end_boards(wings, Path::ForcedPerType);
        assert!(one_choice == per_type, "{:?}: the two paths end in different states", wings.energy);
    }
}

/// Condition 3, one type at a time. On every board here the final boards number over 256, so the attack offers the
/// lowest Energy type's splits alone and each later type follows the same way; `check_end_boards` holds (its forced
/// path is the same walk). Boards, on three Benched Pokémon: [W]x3 [L]x2 [P]x2 (10, 6 and 6 options: 360), [W]x4 [L]
/// [P]x2 (15, 3, 6: 270), [W]x5 [P]x4 (21, 15: 315), and [W]x3 [L]x2 [P]x2 with Comfey's Flower Shield and the
/// Poisoned and Asleep receivers, whose cure comes with a [P] in the last choice (360).
#[test]
fn test_wings_of_the_moone_end_boards_equal_brute_force_one_type_at_a_time() {
    let three_two_two = energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]);
    let boards = [
        (WingsBoard::plain(three_two_two.clone(), &[1, 2, 3]), 360),
        (WingsBoard::plain(energy_of(&[(Water, 4), (Lightning, 1), (Psychic, 2)]), &[1, 2, 3]), 270),
        (WingsBoard::plain(energy_of(&[(Water, 5), (Psychic, 4)]), &[1, 2, 3]), 315),
        (soothing_board(three_two_two, CardId::A3080Comfey, Some(Psychic)), 360),
    ];
    for (wings, expected) in &boards {
        assert_eq!(board_count(&wings.energy, wings.bench.len()), *expected, "{:?}", wings.energy);
        let as_offered = check_end_boards(wings, Path::AsOffered);
        assert!(as_offered == check_end_boards(wings, Path::ForcedPerType), "{:?}", wings.energy);
    }
}

/// The shape is decided once, when the attack resolves (coordinator-132). [W]x3 [L]x2 [P]x2 on three Benched Pokémon
/// (360 final boards) offers the 10 splits of the [W], then the 6 of the [L] (not the 6 x 6 = 36 final boards the two
/// types left would count), then the 6 of the [P]. [W][L][P]x6 on three (252) and [R]x3 [W]x3 [L]x3 [P]x3 on slots 1 and
/// 3 (256) offer one choice, every option holding every type.
#[test]
fn test_wings_of_the_moone_shape_is_decided_once_when_the_attack_resolves() {
    let mut game = after_wings(0, energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), &[1, 2, 3]);
    for (energy_type, options) in [(Water, 10), (Lightning, 6), (Psychic, 6)] {
        let offer = wings_offer(&game.get_state_clone());
        assert_eq!(offer.len(), options, "{energy_type:?}");
        assert!(offer.iter().flatten().all(|&(_, offered, _)| offered == energy_type), "{energy_type:?}");
        let first = offer[0].clone();
        choose(&mut game, &first);
    }
    assert!(!wings_frame_left(&game.get_state_clone()));
    for (energy, bench, options) in [
        (energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 6)]), vec![1, 2, 3], 252),
        (energy_of(&[(Fire, 3), (Water, 3), (Lightning, 3), (Psychic, 3)]), vec![1, 3], 256),
    ] {
        let types = by_type(&energy).len();
        let mut game = after_wings(0, energy, &bench);
        let offer = wings_offer(&game.get_state_clone());
        assert_eq!(offer.len(), options);
        for moves in &offer {
            let held: BTreeSet<EnergyType> = moves.iter().map(|&(_, energy_type, _)| energy_type).collect();
            assert_eq!(held.len(), types, "{moves:?}");
        }
        let last = offer.last().unwrap().clone();
        choose(&mut game, &last);
        let state = game.get_state_clone();
        assert!(state.get_active(0).attached_energy.is_empty() && !wings_frame_left(&state));
    }
}

/// N10: branching pins, as (decision nodes, nodes with two or more options, end boards). [P]x4 on three Benched
/// Pokémon: (1, 1, 15) (the per-Energy chain had (20, 10, 15), upstream's free order 40 nodes and 81 paths);
/// [W][L][P][P] on three: (1, 1, 54); [P]x3 on one: (1, 0, 1); [W]x3 [L]x2 [P]x2 on three, one type at a time: 1 + 10 +
/// 60 = 71 nodes, every one a real choice, and 360 end boards.
#[test]
fn test_wings_of_the_moone_branching_pins() {
    for (energy, bench, shape) in [
        (vec![Psychic; 4], vec![1, 2, 3], (1, 1, 15)),
        (vec![Water, Lightning, Psychic, Psychic], vec![1, 2, 3], (1, 1, 54)),
        (vec![Psychic; 3], vec![1], (1, 0, 1)),
        (energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), vec![1, 2, 3], (71, 71, 360)),
    ] {
        let start = after_wings(0, energy.clone(), &bench).get_state_clone();
        let mut walk = Walk::default();
        explore(&start, 0, &mut walk);
        assert_eq!(walk.shape(), shape, "{energy:?}");
    }
}

/// Picks the Wings of the Moone option that puts the most Energy furthest along the Bench (the largest sum of amount x
/// Bench slot), and keeps seat 0's public events.
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
            .max_by_key(|action| match &action.action {
                SimpleAction::DistributeActiveEnergyToBench { moves } => {
                    moves.iter().map(|&(amount, _, to)| amount as usize * to).sum::<usize>()
                }
                _ => 0,
            })
            .unwrap()
            .clone()
    }
}

/// Plays the rest of the choices through `Game::play_tick` with `Furthest` in both seats: the end state, and each
/// tick's action with its public event.
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

/// N2 and N5: through `Game::play_tick`. [P]x4 on three Benched Pokémon, all to the furthest: one real decision, of 15
/// options, and nothing after it. [P][P][W] on one Benched Pokémon (slot 2): one option, applied without a decision,
/// its Energy appended [W] first. No choice advances the game's random number generator (N6).
#[test]
fn test_wings_of_the_moone_single_option_choices_are_applied_without_a_decision() {
    let (end, ticks) = chain_through_play_tick(after_wings(0, vec![Psychic; 4], &[1, 2, 3]).get_state_clone());
    let choices: Vec<bool> = ticks.iter().map(|(_, event)| event.was_choice).collect();
    assert_eq!(choices, vec![true]);
    assert!(ticks.iter().all(|(action, event)| is_wings_move(&action.action) && !event.chance));
    assert_eq!(sorted_energy(&end, 0, 3), vec![Psychic; 4]);
    assert!(end.get_active(0).attached_energy.is_empty() && !wings_frame_left(&end));

    let (end, ticks) = chain_through_play_tick(
        after_wings(0, vec![Psychic, Psychic, Water], &[2]).get_state_clone(),
    );
    assert_eq!(ticks.len(), 1);
    assert!(ticks.iter().all(|(_, event)| !event.was_choice && !event.chance));
    assert!(end.get_active(0).attached_energy.is_empty());
    assert_eq!(end.in_play_pokemon[0][2].as_ref().unwrap().attached_energy, vec![Water, Psychic, Psychic]);
}

/// N6: every offered distribution, at every choice of [W][L][P][P] (one choice) and of [W]x3 [L]x2 [P]x2 (three) on
/// three Benched Pokémon, forecasts one branch with probability 1.
#[test]
fn test_wings_of_the_moone_each_choice_is_one_certain_branch() {
    for (energy, choices) in [
        (vec![Water, Lightning, Psychic, Psychic], 1),
        (energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), 3),
    ] {
        let mut game = after_wings(0, energy.clone(), &[1, 2, 3]);
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
        assert_eq!(steps, choices, "{energy:?}");
    }
}

/// N3 (divergence D8): Rocky Helmet (A2 148) on the defender, Lunala at 20 HP. The Helmet's 20 waits for the moves,
/// so every Energy reaches the Bench and only then is Lunala Knocked Out (upstream skips the move once the attacker is
/// Knocked Out). The opponent takes the point and player 0 promotes.
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
    assert_eq!(game.get_state_clone().get_active(0).get_remaining_hp(), 20);
    choose(&mut game, &[(1, Water, 1), (1, Psychic, 1), (1, Psychic, 2)]);
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
/// come after the moves: no catch-all Knock Out check removes it in between.
#[test]
fn test_wings_of_the_moone_knock_out_resolves_after_the_moves() {
    let mut game = board(
        vec![lunala(vec![Psychic, Psychic]), durable(), durable()],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), durable(), durable()],
    );
    attack(&mut game, CardId::C1066Lunala, 0);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_some(), "the Knocked Out Bulbasaur is still in play");
    assert_eq!(state.points, [0, 0]);
    choose(&mut game, &[(1, Psychic, 1), (1, Psychic, 2)]);
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

/// N14: Lunala's 110 takes the last point. The distribution is still offered and applied first (the game is not over
/// while a choice is offered), then the Knock Out, the third point and the win; no Wings of the Moone frame is left
/// once the game is over.
#[test]
fn test_wings_of_the_moone_winning_knock_out_comes_after_the_moves() {
    let mut game = board(
        vec![lunala(vec![Psychic, Psychic, Water]), durable(), durable()],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), durable()],
    );
    let mut state = game.get_state_clone();
    state.points = [2, 0];
    game.set_state(state);
    attack(&mut game, CardId::C1066Lunala, 0);
    assert!(!game.is_game_over());
    assert_eq!(game.get_state_clone().points, [2, 0]);
    choose(&mut game, &[(1, Water, 2), (2, Psychic, 1)]);
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
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[0][0].is_some() && state.in_play_pokemon[1][0].is_some());
    choose(&mut game, &[(1, Water, 1), (2, Psychic, 2)]);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[0][0].is_some() && state.in_play_pokemon[1][0].is_some());
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
/// frame is put below the choice and the distribution runs under the end-of-action Knock Out check. Nothing was
/// damaged, so every Energy still moves and only the turn's end is left to offer. On tails the frame is there and
/// Meowth's Knock Out waits for it. Both happen over 40 seeds.
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
        assert_eq!(wings_offer(&state), psychic_psychic_water_offer(), "seed {seed}");
        if defender_damage(&game) > 0 {
            damaged += 1;
            assert!(reaction_frame, "seed {seed}");
            assert!(state.in_play_pokemon[1][0].is_some(), "seed {seed}: the Knock Out waits for the reaction frame");
            continue;
        }
        prevented += 1;
        assert!(!reaction_frame, "seed {seed}");
        choose(&mut game, &[(1, Water, 1), (1, Psychic, 1), (1, Psychic, 2)]);
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
/// way no frame is left behind: the reactions resolve at once and the turn's end is all that is offered. The helpers'
/// own tests are in attack_helpers.rs.
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
/// 6 final boards are offered as usual. Both happen over 20 seeds.
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
            assert_eq!(wings_offer(&state), psychic_psychic_water_offer(), "seed {seed}");
        }
    }
    assert!(failed > 0 && used > 0, "{failed} failed, {used} went ahead");
}

/// N13: Mew ex (A1a 032) copies an opposing Lunala's Wings of the Moone with Genome Hacking ("Choose 1 of your
/// opponent's Active Pokémon's attacks and use it as this attack."). "This Pokémon" is Mew ex, so Mew ex's own Energy
/// goes to Mew ex's own Bench (its 4 final boards), and the opposing Lunala keeps its Energy.
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
    assert_eq!(
        wings_offer(&game.get_state_clone()),
        vec![
            vec![(3, Psychic, 2)],
            vec![(1, Psychic, 1), (2, Psychic, 2)],
            vec![(2, Psychic, 1), (1, Psychic, 2)],
            vec![(3, Psychic, 1)],
        ]
    );
    choose(&mut game, &[(1, Psychic, 1), (2, Psychic, 2)]);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_id(), "A1a 032");
    assert!(state.get_active(0).attached_energy.is_empty());
    assert_eq!(sorted_energy(&state, 0, 1), vec![Psychic]);
    assert_eq!(sorted_energy(&state, 0, 2), vec![Psychic, Psychic]);
    assert_eq!(sorted_energy(&state, 1, 0), vec![Psychic, Psychic]);
}

/// N7: player 0 knows the opponent's hand (Hand Scope, P-A 003) and its own top 3 cards (Pokédex, P-A 004). Neither
/// seat's revealed knowledge changes through the attack and every choice, on [W][L][P][P] (one choice) and [W]x3 [L]x2
/// [P]x2 (three) on three Benched Pokémon. The action's name holds none of the words the knowledge update reads
/// ("hand", "deck", "draw", "shuffle", ...; the per-Energy action's did hold "hand"): this guards a future rename.
#[test]
fn test_wings_of_the_moone_leaves_both_seats_revealed_knowledge_alone() {
    for (energy, choices) in [
        (vec![Water, Lightning, Psychic, Psychic], 1),
        (energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), 3),
    ] {
        let mut game = board(vec![lunala(energy.clone()), durable(), durable(), durable()], vec![durable()]);
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
            assert_eq!(
                [game.observation(0).revealed, game.observation(1).revealed],
                known,
                "{energy:?} step {steps}"
            );
            let (_, actions) = game.get_state_clone().generate_possible_actions();
            if !actions.iter().any(|action| is_wings_move(&action.action)) {
                break;
            }
            game.apply_action(actions.last().unwrap());
            steps += 1;
        }
        assert_eq!(steps, choices, "{energy:?}");
    }
}

/// N9 (smoke): km3 and WeightedRandomPlayer pick an offered option at every choice of [W][L][P][P] (one choice),
/// [W]x5 [P]x4 (two) and [W]x3 [L]x2 [P]x2 (three) on three Benched Pokémon, through `decision_fn` with each choice's
/// observation.
#[test]
fn test_km3_and_weighted_random_pick_an_offered_option_at_every_choice() {
    for code in [PlayerCode::KM { max_depth: 3 }, PlayerCode::W] {
        for (energy, choices) in [
            (vec![Water, Lightning, Psychic, Psychic], 1),
            (energy_of(&[(Water, 5), (Psychic, 4)]), 2),
            (energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), 3),
        ] {
            let mut game = after_wings(0, energy.clone(), &[1, 2, 3]);
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
            assert_eq!(steps, choices, "{code:?} {energy:?}");
            assert!(game.get_state_clone().get_active(0).attached_energy.is_empty(), "{code:?} {energy:?}");
        }
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

/// km3, y3 and x3.
fn searchers() -> [(&'static str, PlayerCode); 3] {
    [
        ("km3", PlayerCode::KM { max_depth: 3 }),
        ("y3", PlayerCode::Y { max_depth: 3, opponent_ply: 3 }),
        ("x3", PlayerCode::X { max_depth: 3, opponent_ply: 3 }),
    ]
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

/// The smoke records of design §5.2 and §D.9, recorded and not asserted beyond legality.
/// - R6: player 0 at 2 points (0 in the no-win rows), its Lunala holding `energy` with one or three Benched Bulbasaur,
///   against a 70-HP Bulbasaur whose Knock Out wins (in the no-win rows it does not), with a Charmander Benched (in the
///   no-win mixed row Charmander, Bulbasaur and Snorlax): does each searcher attack? With one choice ([P]x3 and [P]x2
///   on one Benched Pokémon: 1 option; [W][L][P][P] on three: 54) the 110's Knock Out is priced at the depth-3 tiers'
///   attack root; one type at a time with 2 types ([W]x5 [P]x4: 21, then 15) too; with 3 types (360 final boards each:
///   10, 6, 6 options, or 6, 6, 10 in the [P]-first row) the third choice is past the horizon (risk R6, narrowed), so
///   the root scores the board with the third type still on Lunala. The three 3-type rows move [P] last ([W]x3 [L]x2
///   [P]x2: Lunala still holds the attack's [P][P] there), second ([W]x3 [P]x2 [F]x2: it holds [F][F]) and first
///   (Wally's [C]: [P]x2 [D]x2 [C]x3: it holds [C][C][C]), as the choices go lowest `EnergyType` first. The [P]-second
///   and [P]-first rows record EndTurn instead of the winning attack: a known limit of R8 (coordinator-134 option (A)),
///   to be stated in the release notes' Lunala line (R8's docs commit), not a bug to fix here.
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
    let searchers = searchers();
    let bulbasaur = || PlayedCard::from_id(CardId::A1001Bulbasaur);
    let charmander = || PlayedCard::from_id(CardId::A1033Charmander);
    let mixed = vec![Water, Lightning, Psychic, Psychic];
    for (row, energy, our_bench, points, their_bench) in [
        ("3[P]", vec![Psychic; 3], 1, 2, vec![charmander()]),
        ("2[P]", vec![Psychic; 2], 1, 2, vec![charmander()]),
        ("mixed", mixed.clone(), 3, 2, vec![charmander()]),
        ("no-win 3[P]", vec![Psychic; 3], 1, 0, vec![charmander()]),
        (
            "no-win mixed",
            mixed,
            3,
            0,
            vec![charmander(), bulbasaur(), PlayedCard::from_id(CardId::A1211Snorlax)],
        ),
        ("2-type", energy_of(&[(Water, 5), (Psychic, 4)]), 3, 2, vec![charmander()]),
        ("3-type, [P] last", energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), 3, 2, vec![charmander()]),
        ("3-type, [P] second", energy_of(&[(Water, 3), (Psychic, 2), (Fighting, 2)]), 3, 2, vec![charmander()]),
        ("3-type, [P] first", energy_of(&[(Psychic, 2), (Darkness, 2), (Colorless, 3)]), 3, 2, vec![charmander()]),
    ] {
        let mut ours = vec![lunala(energy.clone())];
        ours.extend((0..our_bench).map(|_| bulbasaur()));
        let mut theirs = vec![bulbasaur()];
        theirs.extend(their_bench.iter().cloned());
        let game = get_initialized_game_with_board(0, 0, 3, ours, theirs);
        let mut state = game.get_state_clone();
        state.points = [points, 0];
        state.hands = [Vec::new(), Vec::new()];
        state.energy_zone[0].current = None;
        for (name, code) in &searchers {
            let _ = writeln!(
                out,
                "R6 {row} {name}: player 0's Lunala {energy:?} ({} final boards), {our_bench} Benched Bulbasaur, {points} points; player 1's Bulbasaur (70 HP) Active, {} Benched",
                board_count(&energy, our_bench),
                their_bench.len()
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

/// One timed `decision_fn` call by `player` for the actor to move in `game`: (the pick, the number of offered actions,
/// ms of wall clock).
fn timed_decision(player: &mut Box<dyn Player>, game: &Game<'static>) -> (Action, usize, f64) {
    let (actor, mut actions) = game.get_state_clone().generate_possible_actions();
    canonical_actions(&mut actions);
    let observation = game.observation(actor);
    let started = Instant::now();
    let chosen = player.decision_fn(&mut StdRng::seed_from_u64(0), &observation, &actions);
    let ms = started.elapsed().as_secs_f64() * 1000.0;
    assert!(actions.contains(&chosen), "picked an action it was not offered: {chosen:?}");
    (chosen, actions.len(), ms)
}

/// A timing row: its name, Lunala's Energy, the in-play indices of player 0's Benched Bulbasaur, and whether the turn is
/// live (see `smoke_record_wings_of_the_moone_decision_times`).
type TimingRow = (&'static str, Vec<EnergyType>, Vec<usize>, bool);

/// Condition 4 (coordinator-131, record only) and design §D.1: km3, y3 and x3's decision times, as ms of wall clock per
/// `decision_fn` call, on large boards (the largest are in the heavy test) and on both sides of the 256 switch, at
/// the turn root and at every Wings of the Moone choice after the Attack is applied directly. The opponent is a 70-HP
/// Bulbasaur with Charmander, Bulbasaur and Snorlax Benched, at 0 points each, so every Knock Out the search prices
/// carries the opponent's promotion. The "spent" rows have player 0's Energy Zone spent and empty hands. The "live" rows have the
/// Zone's [P], two X Speed and a Potion in hand, and Lunala 20 damage down, so the root also offers attaches (to Lunala:
/// [W][L][P]x5 becomes [W][L][P]x6, 252 final boards, one choice; [W][L][P]x6 becomes [W][L][P]x7, 324, one type at a
/// time), Items and retreats; attaches and Items reach the attack one action later (a retreat puts Lunala on the
/// Bench). The heavy rows have their own test (`smoke_record_wings_of_the_moone_heavy_decision_times`), and both timing
/// tests hold `TIMING_LOCK` while they time, so the heavy rows never run while these rows are timed (the two tests may
/// run in either order). A decision over 1 s is marked "OVER 1 s": report only (coordinator-134); a single decision over
/// 3 s on a committed row stops the work. Nothing is asserted beyond legality.
#[test]
fn smoke_record_wings_of_the_moone_decision_times() {
    let rows: [TimingRow; 9] = [
        ("spent [W][L][P]x2", energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 2)]), vec![1, 2, 3], false),
        ("spent [W][L][P]x6", energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 6)]), vec![1, 2, 3], false),
        (
            "spent [R]x3 [W]x3 [L]x3 [P]x3",
            energy_of(&[(Fire, 3), (Water, 3), (Lightning, 3), (Psychic, 3)]),
            vec![1, 3],
            false,
        ),
        ("spent [G]x7 [W]x7 [P]x3", energy_of(&[(Grass, 7), (Water, 7), (Psychic, 3)]), vec![2, 3], false),
        ("spent [W]x4 [L] [P]x2", energy_of(&[(Water, 4), (Lightning, 1), (Psychic, 2)]), vec![1, 2, 3], false),
        ("spent [W]x5 [P]x4", energy_of(&[(Water, 5), (Psychic, 4)]), vec![1, 2, 3], false),
        ("spent [W]x3 [L]x2 [P]x2", energy_of(&[(Water, 3), (Lightning, 2), (Psychic, 2)]), vec![1, 2, 3], false),
        ("live [W][L][P]x5", energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 5)]), vec![1, 2, 3], true),
        ("live [W][L][P]x6", energy_of(&[(Water, 1), (Lightning, 1), (Psychic, 6)]), vec![1, 2, 3], true),
    ];
    let out = decision_times_record(&rows);
    print!("{out}");
    if let Ok(path) = std::env::var("LUNALA_TIMES_OUT") {
        std::fs::write(path, &out).expect("the timing record is written");
    }
}

/// The heavy timing rows, on the same board as `smoke_record_wings_of_the_moone_decision_times` (spent, 3 Benched
/// Bulbasaur). One type at a time keeps each choice small, but a decision can still search every final board: with 2
/// types at the turn root (the attack is priced at depth 2 and each choice costs a ply, so the second choice's options
/// reach depth 0, where the Knock Out is still resolved; [W]x9 [P]x8: 55 x 45 = 2475) and with 3 types at the first
/// choice ([W]x4 [L]x4 [P]x3: 15 x 15 x 10 = 2250). [W]x3 [P]x2 [F]x2 (360, choices 10, 6, 6) is the 3-type board with
/// [P] moved second. The same rule as the other timing rows: "OVER 1 s" is report only; a single decision over 3 s
/// stops the work (coordinator-134).
#[test]
fn smoke_record_wings_of_the_moone_heavy_decision_times() {
    let rows: [TimingRow; 3] = [
        ("spent [W]x3 [P]x2 [F]x2", energy_of(&[(Water, 3), (Psychic, 2), (Fighting, 2)]), vec![1, 2, 3], false),
        ("spent [W]x4 [L]x4 [P]x3", energy_of(&[(Water, 4), (Lightning, 4), (Psychic, 3)]), vec![1, 2, 3], false),
        ("spent [W]x9 [P]x8", energy_of(&[(Water, 9), (Psychic, 8)]), vec![1, 2, 3], false),
    ];
    let out = decision_times_record(&rows);
    print!("{out}");
    if let Ok(path) = std::env::var("LUNALA_HEAVY_TIMES_OUT") {
        std::fs::write(path, &out).expect("the heavy timing record is written");
    }
}

/// Held by both timing tests while they time, so the libtest threads never run them at the same time.
static TIMING_LOCK: Mutex<()> = Mutex::new(());

/// The timing record of `rows`: per row, each searcher's turn-root decision and every Wings of the Moone choice after
/// the Attack, then the slowest decision. Holds `TIMING_LOCK` throughout.
fn decision_times_record(rows: &[TimingRow]) -> String {
    let _serial = TIMING_LOCK.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
    let mut out = String::from(
        "cargo test --release --features test-utils; ms of wall clock per decision_fn call\n",
    );
    let bulbasaur = || PlayedCard::from_id(CardId::A1001Bulbasaur);
    let over = |ms: f64| if ms > 1000.0 { " OVER 1 s" } else { "" };
    let mut slowest: f64 = 0.0;
    for (row, energy, bench, live) in rows {
        let mut ours = lunala(energy.clone());
        if *live {
            let hp = ours.get_remaining_hp();
            ours = ours.with_remaining_hp(hp - 20);
        }
        let game = get_initialized_game_with_board(
            0,
            0,
            3,
            vec![ours],
            vec![
                bulbasaur(),
                PlayedCard::from_id(CardId::A1033Charmander),
                bulbasaur(),
                PlayedCard::from_id(CardId::A1211Snorlax),
            ],
        );
        let mut state = game.get_state_clone();
        for &in_play_idx in bench {
            state.in_play_pokemon[0][in_play_idx] = Some(bulbasaur());
        }
        state.points = [0, 0];
        state.hands = [Vec::new(), Vec::new()];
        if *live {
            state.hands[0] = vec![
                get_card_by_enum(CardId::PA002XSpeed),
                get_card_by_enum(CardId::PA002XSpeed),
                get_card_by_enum(CardId::PA001Potion),
            ];
            state.energy_zone[0].current = Some(Psychic);
        } else {
            state.energy_zone[0].current = None;
        }
        let count = board_count(energy, bench.len());
        let shape = if count <= 256 { "one choice" } else { "one type at a time" };
        let _ = writeln!(out, "{row} on Bench {bench:?}: {count} final boards, {shape}");
        for (name, code) in &searchers() {
            let mut players = create_players(Deck::default(), Deck::default(), vec![code.clone(), code.clone()]);
            let mut game = Game::from_state(state.clone(), Vec::new(), 0);
            let (root, options, ms) = timed_decision(&mut players[0], &game);
            slowest = slowest.max(ms);
            let _ = writeln!(out, "  {name} turn root of {options}: {} ({ms:.1} ms){}", label(&root), over(ms));
            attack(&mut game, CardId::C1066Lunala, 0);
            while !wings_offer(&game.get_state_clone()).is_empty() {
                let (chosen, options, ms) = timed_decision(&mut players[0], &game);
                slowest = slowest.max(ms);
                let _ = writeln!(out, "  {name} choice of {options}: {} ({ms:.1} ms){}", label(&chosen), over(ms));
                game.apply_action(&chosen);
            }
        }
    }
    let _ = writeln!(out, "slowest decision: {slowest:.1} ms{}", over(slowest));
    out
}
