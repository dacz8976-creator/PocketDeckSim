//! The hit back an attack left is that attack's damage in every situation (Dustin, Oct 20, verbatim: "if you are asking if
//! Rocky helmet triggers after an attack back like mega sableye ex or alolan sandslash, the plain reading is the rule unless
//! otherwise stated. The attack back is treated as an attack in every situation (weakness, attack blocking, bounded field)
//! not like an ability. Abilities don't trigger heavy helmet, attacks do"; `rules/02` section 4, `rules/05` #31).
//!
//! Five attacks leave one: Mega Sableye ex's Cursed Jewel (40), Alolan Sandslash's Spike Armor (40), Togedemaru's Bristling
//! Spikes (30), Chesnaught's Needle Lariat (80) and Turtonator's Shell Trap (20). Weakness and Bounded Field already applied
//! (rules switch 2, `rules_repair_return_damage_weakness.rs`). Now the Attacking Pokémon's own cards treat it as an attack's
//! damage too: its cuts (Heavy Helmet: the recording 20261009_223237000 @03:32.5, a Bristling Spikes hit back cut from 30
//! to 10; Fur Coat, Metal Core Barrier, Shell Armor), its prevention (Safeguard, Disguise), and its answers to being damaged
//! by an attack: Rocky Helmet (upstream #367/#418) and the 20-damage Abilities, Poison Barb. A Tool's or an Ability's
//! return damage stays flat and sets off nothing; the Attacking Pokémon's own new hit back covers only the opponent's next
//! turn, so it never answers.
//!
//! The boards are constructed as in `rules_repair_return_damage_weakness.rs`: the holder really uses its attack on a
//! stand-in Snorlax, then the attacker under test replaces the stand-in. `players/` is unchanged.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    players::{EndTurnPlayer, Player},
    Game, State,
};

const SEED: u64 = 20_000_001_020;

fn game_with_board(
    player_0: Vec<PlayedCard>,
    player_1: Vec<PlayedCard>,
    current_player: usize,
    seed: u64,
) -> Game<'static> {
    let mut state = State::default();
    state.current_player = current_player;
    state.turn_count = 10;
    state.points = [0, 0];
    state.hands = [vec![], vec![]];
    state.energy_zone[0].current = None;
    state.energy_zone[0].next = None;
    state.energy_zone[1].current = None;
    state.energy_zone[1].next = None;
    state.set_board(player_0, player_1);

    let players: Vec<Box<dyn Player>> = vec![
        Box::new(EndTurnPlayer {
            deck: state.decks[0].clone(),
        }),
        Box::new(EndTurnPlayer {
            deck: state.decks[1].clone(),
        }),
    ];
    Game::from_state(state, players, seed)
}

fn action_matching(
    game: &Game<'_>,
    label: &str,
    predicate: impl Fn(&SimpleAction) -> bool,
) -> Action {
    let (_, choices) = game.get_state_clone().generate_possible_actions();
    choices
        .into_iter()
        .find(|choice| predicate(&choice.action))
        .unwrap_or_else(|| panic!("missing legal action: {label}"))
}

fn apply_attack(game: &mut Game<'_>, title: &str) {
    let action = action_matching(game, title, |choice| {
        matches!(choice, SimpleAction::Attack(attack) if attack.title == title)
    });
    game.apply_action(&action);
}

fn end_turn_and_resolve_forced_actions(game: &mut Game<'_>, actor: usize) {
    let end = action_matching(game, "end turn", |choice| {
        matches!(choice, SimpleAction::EndTurn)
    });
    assert_eq!(end.actor, actor);
    game.apply_action(&end);

    loop {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        if choices.len() != 1 || !choices[0].is_stack {
            break;
        }
        let forced = choices[0].clone();
        game.apply_action(&forced);
    }
}

fn assert_counterattack_armed(state: &State, player: usize, amount: u32) {
    // PlayedCard::get_active_effects is crate-private; the serialized state shows the same list.
    let serialized = serde_json::to_value(state).expect("state should serialize");
    let effects = serialized["in_play_pokemon"][player][0]["effects"]
        .as_array()
        .expect("active effects should be an array");
    assert!(
        effects
            .iter()
            .any(|entry| entry == &serde_json::json!([{"Counterattack": {"amount": amount}}, 1])),
        "the attack should store Counterattack {{ amount: {amount} }} for duration 1: {effects:?}"
    );
}

fn hp(state: &State, player: usize, idx: usize) -> u32 {
    state.in_play_pokemon[player][idx]
        .as_ref()
        .unwrap_or_else(|| panic!("no Pokémon at ({player}, {idx})"))
        .get_remaining_hp()
}

fn with_energy(id: CardId, energy: &[EnergyType]) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(energy.to_vec())
}

fn with_tool(card: PlayedCard, tool: CardId) -> PlayedCard {
    card.with_tool(get_card_by_enum(tool))
}

fn snorlax() -> PlayedCard {
    with_energy(CardId::A1211Snorlax, &[EnergyType::Colorless; 4])
}

fn togedemaru() -> PlayedCard {
    with_energy(CardId::A3b048Togedemaru, &[EnergyType::Metal, EnergyType::Metal])
}

/// Player 1's `holder` uses `title` on a full-HP stand-in Snorlax (player 0), the effect is checked as armed with
/// `amount`, player 1 ends the turn, and `attacker` replaces the stand-in in player 0's Active Spot. Player 0 is to move.
fn armed_against(
    holder: PlayedCard,
    title: &str,
    amount: u32,
    attacker: PlayedCard,
    p1_bench: Vec<PlayedCard>,
) -> Game<'static> {
    let mut player_1 = vec![holder];
    player_1.extend(p1_bench);
    let mut game = game_with_board(vec![snorlax()], player_1, 1, SEED);
    apply_attack(&mut game, title);
    assert_counterattack_armed(&game.get_state_clone(), 1, amount);
    end_turn_and_resolve_forced_actions(&mut game, 1);

    let mut state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    state.in_play_pokemon[0][0] = Some(attacker);
    game.set_state(state);
    game
}

/// The recording 20261009_223237000 @03:32.5 (Oct 9): Heavy Helmet on the attacking Wailmer (Retreat Cost 3) cut
/// Togedemaru's Bristling Spikes hit back from 30 to 10. The engine applied 30.
#[test]
fn heavy_helmet_on_the_attacker_cuts_a_bristling_spikes_hit_back_from_30_to_10() {
    use EnergyType::*;
    for id in [CardId::A3b048Togedemaru, CardId::PA090Togedemaru] {
        let wailmer = with_tool(with_energy(CardId::B4036Wailmer, &[Water, Water, Water]), CardId::B1219HeavyHelmet);
        let holder = with_energy(id, &[Metal, Metal]);
        let mut game = armed_against(holder, "Bristling Spikes", 30, wailmer, vec![]);
        apply_attack(&mut game, "Wave Splash");
        let state = game.get_state_clone();
        assert_eq!(hp(&state, 1, 0), 20, "{id:?}: Wave Splash 60 into 80 HP");
        assert_eq!(hp(&state, 0, 0), 90, "{id:?}: 30 - 20 = 10 on Wailmer");
    }
    // Retreat Cost 1: the Helmet cuts nothing, and the full 30 lands.
    let bulbasaur = with_tool(with_energy(CardId::A1001Bulbasaur, &[Grass, Colorless]), CardId::B1219HeavyHelmet);
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, bulbasaur, vec![]);
    apply_attack(&mut game, "Vine Whip");
    assert_eq!(hp(&game.get_state_clone(), 0, 0), 40);
}

/// Upstream #367: Rocky Helmet on the attacker answers the hit back with 20 to its holder, every printing.
#[test]
fn rocky_helmet_on_the_attacker_answers_the_hit_back() {
    use EnergyType::*;
    for helmet in [CardId::A2148RockyHelmet, CardId::A4b322RockyHelmet, CardId::A4b323RockyHelmet] {
        let bulbasaur = with_tool(with_energy(CardId::A1001Bulbasaur, &[Grass, Colorless]), helmet);
        let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, bulbasaur, vec![]);
        apply_attack(&mut game, "Vine Whip");
        let state = game.get_state_clone();
        assert_eq!(hp(&state, 0, 0), 40, "{helmet:?}: Bulbasaur takes the 30");
        assert_eq!(hp(&state, 1, 0), 20, "{helmet:?}: Togedemaru 80 - 40 - 20");
    }
}

/// The reflected 20 can knock the holder out: the point goes to the attacker's side, and nothing answers it.
#[test]
fn the_answered_helmet_can_knock_the_holder_out() {
    let holder = togedemaru().with_remaining_hp(80);
    let mut game = armed_against(
        holder,
        "Bristling Spikes",
        30,
        with_tool(snorlax(), CardId::A2148RockyHelmet),
        vec![PlayedCard::from_id(CardId::B1033Torchic)],
    );
    apply_attack(&mut game, "Rollout");
    let state = game.get_state_clone();
    assert_eq!(state.points, [1, 0], "Rollout 70 leaves Togedemaru 10, the Helmet's 20 knocks it out");
    assert_eq!(hp(&state, 0, 0), 120, "Snorlax took the 30 only");
}

/// Weakness first, then the cut: Needle Lariat's 80 on the Grass-weak Stonjourner (Retreat Cost 3) with Heavy Helmet.
#[test]
fn weakness_first_then_the_attackers_cut() {
    use EnergyType::*;
    let stonjourner = with_tool(
        with_energy(CardId::A1a048Stonjourner, &[Fighting, Fighting, Fighting]),
        CardId::B1219HeavyHelmet,
    );
    let chesnaught = with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]);
    let mut game = armed_against(chesnaught, "Needle Lariat", 80, stonjourner, vec![]);
    apply_attack(&mut game, "Mega Kick");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 70);
    assert_eq!(hp(&state, 0, 0), 40, "80 + 20 - 20 = 80 on 120 HP");
}

/// The attacker's damage cuts: Fur Coat (-20), Metal Core Barrier (-50 on a [M]), Shell Armor and Heavy Helmet together.
#[test]
fn the_attackers_damage_cuts_apply_to_the_hit_back() {
    use EnergyType::*;
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, with_energy(CardId::B1a065Furfrou, &[Colorless]), vec![]);
    apply_attack(&mut game, "Tackle");
    assert_eq!(hp(&game.get_state_clone(), 0, 0), 60, "Fur Coat: 30 - 20 = 10 on 70 HP");

    let registeel = with_tool(with_energy(CardId::A2112Registeel, &[Metal, Metal, Metal]), CardId::B2148MetalCoreBarrier);
    let chesnaught = with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]);
    let mut game = armed_against(chesnaught, "Needle Lariat", 80, registeel, vec![]);
    apply_attack(&mut game, "Metal Claw");
    assert_eq!(hp(&game.get_state_clone(), 0, 0), 80, "Metal Core Barrier: 80 - 50 = 30 on 110 HP");

    let cloyster = with_tool(with_energy(CardId::A1067Cloyster, &[Water, Water, Colorless]), CardId::B1219HeavyHelmet);
    let turtonator = with_energy(CardId::B1047Turtonator, &[Fire, Fire]);
    let mut game = armed_against(turtonator, "Shell Trap", 20, cloyster, vec![]);
    apply_attack(&mut game, "Surf");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 20, "Surf 70 + 20 Weakness into 110 HP");
    assert_eq!(hp(&state, 0, 0), 120, "20 - 10 (Shell Armor) - 20 (Heavy Helmet): nothing");
}

/// Prevention on the attacker: Safeguard against a Pokémon ex holder (and its Rocky Helmet doesn't answer), Disguise.
#[test]
fn the_attackers_prevention_applies_to_the_hit_back() {
    use EnergyType::*;
    let sableye = || with_energy(CardId::B3b041MegaSableyeEx, &[Darkness, Darkness]);
    for helmet in [false, true] {
        let oricorio = with_energy(CardId::A3066Oricorio, &[Lightning, Colorless]);
        let oricorio = if helmet { with_tool(oricorio, CardId::A2148RockyHelmet) } else { oricorio };
        let mut game = armed_against(sableye(), "Cursed Jewel", 40, oricorio, vec![]);
        apply_attack(&mut game, "Zzzap");
        let state = game.get_state_clone();
        assert_eq!(hp(&state, 0, 0), 70, "helmet {helmet}: Safeguard prevents a Pokémon ex's hit back");
        assert_eq!(hp(&state, 1, 0), 120, "helmet {helmet}: Zzzap 50 only; no damage, so no answer");
    }
    // Togedemaru isn't an ex: Safeguard lets its hit back through.
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, with_energy(CardId::A3066Oricorio, &[Lightning, Colorless]), vec![]);
    apply_attack(&mut game, "Zzzap");
    assert_eq!(hp(&game.get_state_clone(), 0, 0), 40);

    // Disguise: the first damage from an attack after Mimikyu ex comes into play is prevented, the hit back's included.
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, with_energy(CardId::B2073MimikyuEx, &[Psychic, Psychic]), vec![]);
    apply_attack(&mut game, "Claw Slash");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 10);
    assert_eq!(hp(&state, 0, 0), 120);
    assert!(state.get_active(0).prevent_first_attack_damage_used);
}

/// The attacker's Ability with Rocky Helmet's trigger (Rough Skin) answers too, and Poison Barb poisons the holder.
#[test]
fn the_attackers_rough_skin_and_poison_barb_answer_the_hit_back() {
    use EnergyType::*;
    let chesnaught = with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]);
    let druddigon = with_energy(CardId::A1a056Druddigon, &[Fire, Water, Colorless]);
    let mut game = armed_against(chesnaught, "Needle Lariat", 80, druddigon, vec![]);
    apply_attack(&mut game, "Dragon Claw");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 0, 0), 20, "Druddigon takes the 80");
    assert_eq!(hp(&state, 1, 0), 50, "Chesnaught 160 - 90 - 20 (Rough Skin)");

    let bulbasaur = with_tool(with_energy(CardId::A1001Bulbasaur, &[Grass, Colorless]), CardId::A3146PoisonBarb);
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, bulbasaur, vec![]);
    apply_attack(&mut game, "Vine Whip");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 0, 0), 40);
    assert_eq!(hp(&state, 1, 0), 40);
    assert!(state.get_active(1).is_poisoned(), "Poison Barb: the holder is now Poisoned");
}

/// No chain: Ferrothorn attacks a Chesnaught that holds Rocky Helmet and has Needle Lariat armed. Chesnaught's Helmet
/// answers the attack (20) and Needle Lariat hits back (80); Ferrothorn's Steel Spikes answers the hit back (20, an
/// Ability's damage), and there it stops: the Helmet doesn't answer Steel Spikes.
#[test]
fn an_abilitys_answer_to_the_hit_back_ends_the_chain() {
    use EnergyType::*;
    let chesnaught = with_tool(with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]), CardId::A2148RockyHelmet);
    let ferrothorn = with_energy(CardId::A3a052Ferrothorn, &[Metal, Metal, Colorless]);
    let mut game = armed_against(chesnaught, "Needle Lariat", 80, ferrothorn, vec![]);
    apply_attack(&mut game, "Spinning Attack");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 0, 0), 10, "Ferrothorn 110 - 20 (Rocky Helmet) - 80 (the hit back)");
    assert_eq!(hp(&state, 1, 0), 70, "Chesnaught 160 - 70 - 20 (Steel Spikes), and no more");
}

/// The attacker's own new hit back covers the opponent's next turn: it doesn't answer the holder's hit back now.
#[test]
fn the_attackers_own_new_hit_back_does_not_answer() {
    use EnergyType::*;
    let attacker = with_energy(CardId::PA090Togedemaru, &[Metal, Metal]);
    let mut game = armed_against(togedemaru(), "Bristling Spikes", 30, attacker, vec![]);
    apply_attack(&mut game, "Bristling Spikes");
    let state = game.get_state_clone();
    assert_eq!((hp(&state, 1, 0), hp(&state, 0, 0)), (50, 50));
    assert_counterattack_armed(&state, 0, 30);
}
