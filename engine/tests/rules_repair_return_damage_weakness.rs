//! P2: return damage left by an attack takes Weakness; a Tool's and an Ability's stay flat.
//!
//! Five attacks read "During your opponent's next turn, if this Pokémon is damaged by an attack, do X
//! damage to the Attacking Pokémon": Mega Sableye ex's Cursed Jewel (40; B3b 041/081/088), Alolan
//! Sandslash's Spike Armor (40; A3 039), Togedemaru's Bristling Spikes (30; A3b 048, P-A 090),
//! Chesnaught's Needle Lariat (80; B2 010) and Turtonator's Shell Trap (20; B1 047). The hit back is part
//! of the attack that set it up, so it takes +20 when the Attacking Pokémon is weak to the holder's type
//! and is still in the Active Spot. Rocky Helmet's 20 and every `CounterattackDamage` Ability stay flat.
//!
//! Sources: `rl/results/engine_switch_rules2_2026-10/PLAN.md` section 0 part 3 and
//! `rules/02_damage_knockouts_points.md` section 2 (main b77652d6). Evidence: Dustin's recordings 183108
//! @306-308 and @384-386 (Cursed Jewel did 60 to a Darkness-weak Houndstone, twice), 215749 @99 and @161
//! (Rocky Helmet did a flat 20 to a Fire-weak Tinkatink) and 20261006_220700000 (Automated Combat did a
//! flat 20 to Darkness-weak attackers five times); triage in
//! `rl/results/new_pause_games_triage_2026-10-06/TRIAGE.md` section 2.1.
//!
//! The boards are constructed, not replays: each attack is used for real so the engine arms it, then a
//! stand-in Snorlax that took the setup hit is swapped for the attacker under test, so that hit can't add
//! Weakness of its own. `players/` is unchanged by P2.
//!
//! P2's off-switch (rules switch 2, PLAN (e); the coordinator via Dustin, Oct 9): with it off
//! (`with_return_weakness(false, ..)`, or `DECKGYM_FLAT_RETURN_DAMAGE=1` for a whole process), every
//! scenario here gives the engine before P2's numbers, and where P2 doesn't act the board is the same
//! with the switch on or off.

use deckgym::{
    actions::{with_return_weakness, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard},
    players::{EndTurnPlayer, Player},
    state::GameOutcome,
    Game, State,
};

const SEED: u64 = 20_000_000_260;

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

fn snorlax() -> PlayedCard {
    with_energy(CardId::A1211Snorlax, &[EnergyType::Colorless; 4])
}

/// Player 1's `holder` uses `title` on a full-HP stand-in Snorlax (player 0), the effect is checked as
/// armed with `amount`, player 1 ends the turn, and `attacker` replaces the stand-in in player 0's Active
/// Spot. Player 0 is to move.
fn armed_against(
    holder: PlayedCard,
    title: &str,
    amount: u32,
    attacker: PlayedCard,
    p0_bench: Vec<PlayedCard>,
    p1_bench: Vec<PlayedCard>,
    stadium: Option<CardId>,
) -> Game<'static> {
    let mut player_0 = vec![snorlax()];
    player_0.extend(p0_bench);
    let mut player_1 = vec![holder];
    player_1.extend(p1_bench);
    let mut game = game_with_board(player_0, player_1, 1, SEED);
    if let Some(stadium) = stadium {
        let mut state = game.get_state_clone();
        state.active_stadium = Some(get_card_by_enum(stadium));
        state.active_stadium_owner = None;
        game.set_state(state);
    }

    apply_attack(&mut game, title);
    assert_counterattack_armed(&game.get_state_clone(), 1, amount);
    end_turn_and_resolve_forced_actions(&mut game, 1);

    let mut state = game.get_state_clone();
    assert_eq!(state.current_player, 0);
    state.in_play_pokemon[0][0] = Some(attacker);
    game.set_state(state);
    game
}

struct Row {
    holder: PlayedCard,
    title: &'static str,
    amount: u32,
    holder_hp: u32,
    weak_attacker: PlayedCard,
    weak_attack: &'static str,
    weak_attacker_hp: u32,
    weak_damage: u32,
}

/// The eight printings, each with an attacker weak to the holder's type. No holder is weak to its
/// attacker, so the hit itself is plain. Types and Weaknesses from `lib/card.py`.
fn rows() -> Vec<Row> {
    use EnergyType::*;
    let mut rows = vec![];
    for id in [
        CardId::B3b041MegaSableyeEx,
        CardId::B3b081MegaSableyeEx,
        CardId::B3b088MegaSableyeEx,
    ] {
        // Mega Sableye ex: Darkness, 170 HP. Houndstone B3a 024: Psychic, 130 HP, weak Darkness.
        rows.push(Row {
            holder: with_energy(id, &[Darkness, Darkness]),
            title: "Cursed Jewel",
            amount: 40,
            holder_hp: 170,
            weak_attacker: with_energy(CardId::B3a024Houndstone, &[Psychic, Psychic, Psychic]),
            weak_attack: "Spooky Shot",
            weak_attacker_hp: 130,
            weak_damage: 70,
        });
    }
    // Alolan Sandslash: Water, 100 HP. Magmar: Fire, 80 HP, weak Water.
    rows.push(Row {
        holder: with_energy(CardId::A3039AlolanSandslash, &[Water]),
        title: "Spike Armor",
        amount: 40,
        holder_hp: 100,
        weak_attacker: with_energy(CardId::A1044Magmar, &[Fire, Fire]),
        weak_attack: "Magma Punch",
        weak_attacker_hp: 80,
        weak_damage: 50,
    });
    for id in [CardId::A3b048Togedemaru, CardId::PA090Togedemaru] {
        // Togedemaru: Metal, 80 HP. Snover: Water, 70 HP, weak Metal.
        rows.push(Row {
            holder: with_energy(id, &[Metal, Metal]),
            title: "Bristling Spikes",
            amount: 30,
            holder_hp: 80,
            weak_attacker: with_energy(CardId::A2a020Snover, &[Water, Colorless]),
            weak_attack: "Corkscrew Punch",
            weak_attacker_hp: 70,
            weak_damage: 30,
        });
    }
    // Chesnaught: Grass, 160 HP. Stonjourner: Fighting, 120 HP, weak Grass.
    rows.push(Row {
        holder: with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]),
        title: "Needle Lariat",
        amount: 80,
        holder_hp: 160,
        weak_attacker: with_energy(CardId::A1a048Stonjourner, &[Fighting, Fighting, Fighting]),
        weak_attack: "Mega Kick",
        weak_attacker_hp: 120,
        weak_damage: 90,
    });
    // Turtonator: Fire, 110 HP. Bulbasaur: Grass, 70 HP, weak Fire.
    rows.push(Row {
        holder: with_energy(CardId::B1047Turtonator, &[Fire, Fire]),
        title: "Shell Trap",
        amount: 20,
        holder_hp: 110,
        weak_attacker: with_energy(CardId::A1001Bulbasaur, &[Grass, Colorless]),
        weak_attack: "Vine Whip",
        weak_attacker_hp: 70,
        weak_damage: 40,
    });
    rows
}

fn hit_back_once(row: &Row, attacker: PlayedCard, attack: &str, p0_bench: Vec<PlayedCard>) -> State {
    let mut game = armed_against(
        row.holder.clone(),
        row.title,
        row.amount,
        attacker,
        p0_bench,
        vec![],
        None,
    );
    apply_attack(&mut game, attack);
    game.get_state_clone()
}

/// "During your opponent's next turn, if this Pokémon is damaged by an attack, do X damage to the
/// Attacking Pokémon." The hit back is the attack's own damage, so an Attacking Pokémon weak to the
/// holder takes X + 20 (183108 @308: Houndstone took 60 from Cursed Jewel's 40). The old engine applied
/// X flat to every attacker.
#[test]
fn each_attack_hits_back_with_weakness_on_a_weak_attacker() {
    for row in rows() {
        let state = hit_back_once(&row, row.weak_attacker.clone(), row.weak_attack, vec![]);
        assert_eq!(hp(&state, 1, 0), row.holder_hp - row.weak_damage, "{}", row.title);
        assert_eq!(
            hp(&state, 0, 0),
            row.weak_attacker_hp - row.amount - 20,
            "{}: the hit back takes +20 on an attacker weak to the holder",
            row.title
        );
    }
}

/// The same five attacks against Snorlax (Colorless, weak Fighting): no holder is Fighting, so the hit
/// back stays X. Unchanged from the old engine; it guards the flat case.
#[test]
fn each_attack_hits_back_flat_on_an_attacker_not_weak_to_it() {
    for row in rows() {
        let state = hit_back_once(&row, snorlax(), "Rollout", vec![]);
        assert_eq!(hp(&state, 1, 0), row.holder_hp - 70, "{}", row.title);
        assert_eq!(hp(&state, 0, 0), 150 - row.amount, "{}: no Weakness, flat", row.title);
    }
}

/// Weakness decides the Knock Out: a weak attacker at X + 20 HP is Knocked Out by the hit back (the
/// holder's side takes a point and player 0 must promote, or loses with no Bench); at X + 21 it survives
/// at 1, which pins the extra at exactly 20. The old engine left it at 20 HP.
#[test]
fn weakness_decides_the_knockout_by_the_hit_back() {
    for row in rows() {
        let at = |remaining: u32| row.weak_attacker.clone().with_remaining_hp(remaining);

        let state = hit_back_once(
            &row,
            at(row.amount + 20),
            row.weak_attack,
            vec![PlayedCard::from_id(CardId::A1130Ralts)],
        );
        assert!(state.in_play_pokemon[0][0].is_none(), "{}: Knocked Out", row.title);
        assert_eq!(state.points, [0, 1], "{}", row.title);
        assert_eq!(state.winner, None, "{}", row.title);
        let (actor, choices) = state.generate_possible_actions();
        assert_eq!(actor, 0, "{}", row.title);
        assert!(
            choices
                .iter()
                .all(|choice| matches!(choice.action, SimpleAction::Promote { player: 0, .. })),
            "{}: player 0 must promote: {choices:?}",
            row.title
        );

        let state = hit_back_once(&row, at(row.amount + 21), row.weak_attack, vec![]);
        assert_eq!(hp(&state, 0, 0), 1, "{}: +20 exactly", row.title);

        let state = hit_back_once(&row, at(row.amount + 20), row.weak_attack, vec![]);
        assert!(state.in_play_pokemon[0][0].is_none(), "{}", row.title);
        assert_eq!(state.winner, Some(GameOutcome::Win(1)), "{}: no Bench", row.title);
    }
}

fn houndstone_last_respects(remaining_hp: u32) -> PlayedCard {
    with_energy(CardId::B2a053Houndstone, &[EnergyType::Psychic, EnergyType::Colorless])
        .with_remaining_hp(remaining_hp)
}

fn set_psychic_discard(game: &mut Game<'static>, ralts: usize) {
    let mut state = game.get_state_clone();
    state.discard_piles[0] = vec![get_card_by_enum(CardId::A1130Ralts); ralts];
    game.set_state(state);
}

/// 183108 turn 8, @306-308: Houndstone (B2a 053, 130/130; Last Respects: "This attack does 20 more damage
/// for each [P] Pokémon in your discard pile.") hits the Cursed-Jewel Mega Sableye ex from 170 to 40 and
/// ends at 70/130: it took 60. Four Psychic Pokémon in the discard make the 130. The old engine left
/// Houndstone at 90.
fn recording_t8() -> State {
    let sableye =
        with_energy(CardId::B3b041MegaSableyeEx, &[EnergyType::Darkness, EnergyType::Darkness]);
    let mut game = armed_against(
        sableye,
        "Cursed Jewel",
        40,
        houndstone_last_respects(130),
        vec![],
        vec![],
        None,
    );
    set_psychic_discard(&mut game, 4);
    apply_attack(&mut game, "Last Respects");
    game.get_state_clone()
}

#[test]
fn recording_183108_t8_cursed_jewel_returns_60() {
    let state = recording_t8();
    assert_eq!(hp(&state, 1, 0), 40);
    assert_eq!(hp(&state, 0, 0), 70);
}

/// 183108 turn 10, @384-386: Houndstone at 120/130 Knocks Out the Mega at 80 HP and ends at 60/130: the
/// hit back lands with Weakness even though the holder is Knocked Out by the same attack. The old engine
/// left Houndstone at 80.
fn recording_t10() -> State {
    let sableye =
        with_energy(CardId::B3b041MegaSableyeEx, &[EnergyType::Darkness, EnergyType::Darkness])
            .with_remaining_hp(80);
    let mut game = armed_against(
        sableye,
        "Cursed Jewel",
        40,
        houndstone_last_respects(120),
        vec![],
        vec![],
        None,
    );
    set_psychic_discard(&mut game, 2);
    apply_attack(&mut game, "Last Respects");
    game.get_state_clone()
}

#[test]
fn recording_183108_t10_hit_back_lands_when_the_holder_is_knocked_out() {
    let state = recording_t10();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points, [3, 0]);
    assert_eq!(state.winner, Some(GameOutcome::Win(0)));
    assert_eq!(hp(&state, 0, 0), 60);
}

/// Turtonator at 40 HP with Shell Trap armed; Bulbasaur at 40 HP Knocks it Out with Vine Whip and the
/// 20 + 20 hit back Knocks Bulbasaur Out too. Both sides take a point and, after a double Knock Out, the
/// attacker promotes first (`RULES_FOR_AGENTS.md`, Dustin + a recording). The old engine left Bulbasaur
/// at 20 with points [1, 0].
fn double_knockout() -> State {
    let turtonator = with_energy(CardId::B1047Turtonator, &[EnergyType::Fire, EnergyType::Fire])
        .with_remaining_hp(40);
    let bulbasaur = with_energy(CardId::A1001Bulbasaur, &[EnergyType::Grass, EnergyType::Colorless])
        .with_remaining_hp(40);
    let mut game = armed_against(
        turtonator,
        "Shell Trap",
        20,
        bulbasaur,
        vec![PlayedCard::from_id(CardId::A1130Ralts)],
        vec![PlayedCard::from_id(CardId::B1033Torchic)],
        None,
    );
    apply_attack(&mut game, "Vine Whip");
    game.get_state_clone()
}

#[test]
fn double_knockout_by_the_hit_back_the_attacker_promotes_first() {
    let state = double_knockout();
    assert_eq!(
        state.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()),
        None,
        "Bulbasaur (40 HP, weak Fire) is Knocked Out by Shell Trap's 20 + 20"
    );
    assert!(state.in_play_pokemon[1][0].is_none(), "Turtonator is Knocked Out by Vine Whip");
    assert_eq!(state.points, [1, 1]);
    assert_eq!(state.winner, None);
    let (actor, choices) = state.generate_possible_actions();
    assert_eq!(actor, 0);
    assert!(choices
        .iter()
        .all(|choice| matches!(choice.action, SimpleAction::Promote { player: 0, .. })));
}

/// Rocky Helmet: "If the Pokémon this card is attached to is in the Active Spot and is damaged by an
/// attack from your opponent's Pokémon, do 20 damage to the Attacking Pokémon." 215749 @99 and @161:
/// Torchic (Fire) holding the Helmet, hit by Tinkatink (Metal, weak Fire); Tinkatink went 60 to 40 both
/// times (the second after a Potion). A Tool's return damage stays flat, in all three printings.
#[test]
fn rocky_helmet_stays_flat_on_a_weak_attacker() {
    for helmet in [
        CardId::A2148RockyHelmet,
        CardId::A4b322RockyHelmet,
        CardId::A4b323RockyHelmet,
    ] {
        let torchic = PlayedCard::from_id(CardId::B1033Torchic).with_tool(get_card_by_enum(helmet));
        let tinkatink = with_energy(CardId::A2b052Tinkatink, &[EnergyType::Metal]);
        let mut game = game_with_board(vec![tinkatink], vec![torchic], 0, SEED);
        apply_attack(&mut game, "Corkscrew Punch");
        let state = game.get_state_clone();
        assert_eq!(hp(&state, 1, 0), 40, "{helmet:?}");
        assert_eq!(hp(&state, 0, 0), 40, "{helmet:?}: flat 20");
    }
}

/// "If this Pokémon is in the Active Spot and is damaged by an attack from your opponent's Pokémon, do 20
/// damage to the Attacking Pokémon." (Automated Combat, Steel Spikes, Rough Skin.) Ability return damage
/// stays flat: 20261006_220700000 showed Automated Combat doing a flat 20 to Darkness-weak attackers five
/// times. No real card is weak to Dragon, so Rough Skin is checked on a Snorlax given a constructed Dragon
/// Weakness.
#[test]
fn ability_return_damage_stays_flat() {
    use EnergyType::*;
    // Iron Jugulis (Darkness) against Mewtwo ex (weak Darkness): Psychic Sphere 50.
    let mut game = game_with_board(
        vec![with_energy(CardId::A1129MewtwoEx, &[Psychic, Colorless])],
        vec![PlayedCard::from_id(CardId::B3a046IronJugulis)],
        0,
        SEED,
    );
    apply_attack(&mut game, "Psychic Sphere");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 50);
    assert_eq!(hp(&state, 0, 0), 130, "Automated Combat stays a flat 20");

    // Ferrothorn (Metal) against Snover (weak Metal): Corkscrew Punch 30.
    let mut game = game_with_board(
        vec![with_energy(CardId::A2a020Snover, &[Water, Colorless])],
        vec![PlayedCard::from_id(CardId::A3a052Ferrothorn)],
        0,
        SEED,
    );
    apply_attack(&mut game, "Corkscrew Punch");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 80);
    assert_eq!(hp(&state, 0, 0), 50, "Steel Spikes stays a flat 20");

    // Druddigon (Dragon) against a Snorlax given a Dragon Weakness: Rollout 70.
    let mut dragon_weak = snorlax();
    if let Card::Pokemon(card) = &mut dragon_weak.card {
        card.weakness = Some(Dragon);
    }
    let mut game = game_with_board(
        vec![dragon_weak],
        vec![PlayedCard::from_id(CardId::A1a056Druddigon)],
        0,
        SEED,
    );
    apply_attack(&mut game, "Rollout");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 30);
    assert_eq!(hp(&state, 0, 0), 130, "Rough Skin stays a flat 20");
}

/// A Mega Sableye ex holding a Rocky Helmet arms Cursed Jewel. Each source keeps its own rule: against a
/// Darkness-weak Houndstone the Helmet's 20 stays flat and Cursed Jewel's 40 takes +20 (80 in all; the old
/// engine did 60); against Snorlax both are flat (60). With the Helmet test, this rules out "+20 per
/// source" and "+20 on any return damage".
fn helmet_and_cursed_jewel(houndstone: bool) -> State {
    use EnergyType::*;
    let (attacker, attack) = if houndstone {
        (with_energy(CardId::B3a024Houndstone, &[Psychic, Psychic, Psychic]), "Spooky Shot")
    } else {
        (snorlax(), "Rollout")
    };
    let start = attacker.get_remaining_hp();
    let sableye = with_energy(CardId::B3b041MegaSableyeEx, &[Darkness, Darkness])
        .with_tool(get_card_by_enum(CardId::A2148RockyHelmet));
    let mut game = armed_against(sableye, "Cursed Jewel", 40, attacker, vec![], vec![], None);
    assert_eq!(hp(&game.get_state_clone(), 0, 0), start);
    apply_attack(&mut game, attack);
    game.get_state_clone()
}

#[test]
fn tool_and_attack_return_on_one_defender_each_by_its_own_rule() {
    assert_eq!(hp(&helmet_and_cursed_jewel(true), 0, 0), 50, "Spooky Shot");
    assert_eq!(hp(&helmet_and_cursed_jewel(false), 0, 0), 90, "Rollout");
}

/// Constructed: an Iron Jugulis carrying both its Ability and an attack's `Counterattack { amount: 40 }`.
/// Against Mewtwo ex (weak Darkness) the Ability's 20 stays flat and the attack's 40 takes +20: Mewtwo ex
/// ends at 150 - 20 - 60 = 70. The old engine left it at 90.
fn jugulis_with_cursed_effect() -> State {
    let mut jugulis = PlayedCard::from_id(CardId::B3a046IronJugulis);
    jugulis.add_effect(CardEffect::Counterattack { amount: 40 }, 1);
    let mut game = game_with_board(
        vec![with_energy(CardId::A1129MewtwoEx, &[EnergyType::Psychic, EnergyType::Colorless])],
        vec![jugulis],
        0,
        SEED,
    );
    apply_attack(&mut game, "Psychic Sphere");
    game.get_state_clone()
}

#[test]
fn ability_and_attack_return_on_one_defender() {
    let state = jugulis_with_cursed_effect();
    assert_eq!(hp(&state, 1, 0), 50);
    assert_eq!(hp(&state, 0, 0), 70);
}

/// The held-back path (`ResolveAttackRetaliation`): Gardevoir's Psy Turbo ("Take 2 [P] Energy from your
/// Energy Zone and attach it to 1 of your Benched [P] Pokémon.") leaves an Attach choice after its damage,
/// so the hit back waits for it. Gardevoir (Psychic, weak Darkness) then takes 40 + 20; the old engine
/// did 40.
fn held_back() -> State {
    use EnergyType::*;
    let sableye = with_energy(CardId::B3b041MegaSableyeEx, &[Darkness, Darkness]);
    let gardevoir = with_energy(CardId::B2065Gardevoir, &[Psychic, Psychic]);
    let mut game = armed_against(
        sableye,
        "Cursed Jewel",
        40,
        gardevoir,
        vec![PlayedCard::from_id(CardId::A1130Ralts)],
        vec![],
        None,
    );
    apply_attack(&mut game, "Psy Turbo");
    let state = game.get_state_clone();
    assert_eq!(hp(&state, 1, 0), 110);
    assert_eq!(hp(&state, 0, 0), 130, "the hit back waits for the Attach");

    let attach = action_matching(&game, "Psy Turbo's Attach", |choice| {
        matches!(choice, SimpleAction::Attach { .. })
    });
    game.apply_action(&attach);
    let resolve = action_matching(&game, "ResolveAttackRetaliation", |choice| {
        matches!(choice, SimpleAction::ResolveAttackRetaliation { .. })
    });
    game.apply_action(&resolve);
    game.get_state_clone()
}

#[test]
fn held_back_hit_back_takes_weakness() {
    let state = held_back();
    assert_eq!(hp(&state, 0, 0), 70);
    assert_eq!(hp(&state, 1, 0), 110);
}

/// The `ApplyDamage` path (`handle_damage`): a constructed 10-damage attack hit from Houndstone's Active
/// into the armed Mega. Houndstone takes 40 + 20; the old engine did 40.
fn apply_damage_path() -> State {
    use EnergyType::*;
    let sableye = with_energy(CardId::B3b041MegaSableyeEx, &[Darkness, Darkness]);
    let houndstone = with_energy(CardId::B3a024Houndstone, &[Psychic, Psychic, Psychic]);
    let mut game = armed_against(sableye, "Cursed Jewel", 40, houndstone, vec![], vec![], None);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::ApplyDamage {
            attacking_ref: (0, 0),
            targets: vec![(10, 1, 0)],
            is_from_active_attack: true,
        },
        is_stack: false,
    });
    game.get_state_clone()
}

#[test]
fn apply_damage_path_takes_weakness() {
    let state = apply_damage_path();
    assert_eq!(hp(&state, 1, 0), 160);
    assert_eq!(hp(&state, 0, 0), 70);
}

/// Weakness applies only to the Active Pokémon (`rules/02` section 2, [OFFICIAL] "Don't apply Weakness
/// for Benched Pokémon"). Scyther (Grass, weak Fire) uses U-turn ("Switch this Pokémon with 1 of your
/// Benched Pokémon.") into an armed Turtonator (Fire): the hit back waits for the switch and then lands
/// on the Benched Scyther flat. The same before and after P2; not yet seen in a recording.
fn benched_attacker() -> State {
    let turtonator = with_energy(CardId::B1047Turtonator, &[EnergyType::Fire, EnergyType::Fire]);
    let scyther = with_energy(CardId::B2b001Scyther, &[EnergyType::Colorless]);
    let mut game = armed_against(
        turtonator,
        "Shell Trap",
        20,
        scyther,
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![],
        None,
    );
    apply_attack(&mut game, "U-turn");
    let switch = action_matching(&game, "U-turn's switch", |choice| {
        matches!(choice, SimpleAction::Activate { player: 0, in_play_idx: 1 })
    });
    game.apply_action(&switch);
    let resolve = action_matching(&game, "ResolveAttackRetaliation", |choice| {
        matches!(choice, SimpleAction::ResolveAttackRetaliation { .. })
    });
    game.apply_action(&resolve);
    game.get_state_clone()
}

#[test]
fn hit_back_on_a_benched_attacker_stays_flat() {
    let state = benched_attacker();
    assert_eq!(hp(&state, 1, 0), 100);
    assert_eq!(state.get_active(0).get_name(), "Bulbasaur");
    assert_eq!(hp(&state, 0, 1), 50, "Benched: flat 20");
}

/// Steelix's Metal Defender: "During your opponent's next turn, this Pokémon has no Weakness." The effect
/// starts with the opponent's next turn, so it doesn't cover the hit back on Steelix's own attack. Steelix
/// (Metal, weak Fire) into an armed Turtonator (Fire) takes 20 + 20. The engine adds `NoWeakness` before
/// the hit back, so P2 doesn't read it there; the old engine did 20.
fn metal_defender() -> State {
    use EnergyType::*;
    let turtonator = with_energy(CardId::B1047Turtonator, &[Fire, Fire]);
    let steelix = with_energy(CardId::B1a051Steelix, &[Metal, Metal, Colorless, Colorless]);
    let mut game = armed_against(turtonator, "Shell Trap", 20, steelix, vec![], vec![], None);
    apply_attack(&mut game, "Metal Defender");
    game.get_state_clone()
}

#[test]
fn metal_defender_does_not_shield_its_own_hit_back() {
    let state = metal_defender();
    assert_eq!(hp(&state, 1, 0), 10);
    assert_eq!(hp(&state, 0, 0), 110);
}

/// Ledian's Swift: "This attack's damage isn't affected by Weakness or by any effects on your opponent's
/// Active Pokémon." That covers Swift's own damage, not the hit back, which is Shell Trap's: Ledian
/// (Grass, weak Fire) takes 20 + 20. A reading, stated in the README; the old engine did 20.
fn swift() -> State {
    let turtonator = with_energy(CardId::B1047Turtonator, &[EnergyType::Fire, EnergyType::Fire]);
    let ledian = with_energy(CardId::B2002Ledian, &[EnergyType::Colorless]);
    let mut game = armed_against(turtonator, "Shell Trap", 20, ledian, vec![], vec![], None);
    apply_attack(&mut game, "Swift");
    game.get_state_clone()
}

#[test]
fn swift_does_not_shield_the_hit_back() {
    let state = swift();
    assert_eq!(hp(&state, 1, 0), 70);
    assert_eq!(hp(&state, 0, 0), 40);
}

/// Bounded Field: "When applying the opponent's Active Pokémon's Weakness to damage from attacks used by
/// Pokémon in play ... that aren't Mega Evolution Pokémon ex, apply Weakness as ×2." A stated choice for
/// Dustin to rule on: P2 gives the hit back a flat +20 under Bounded Field too (Chesnaught's 80 becomes
/// 100, not 160). Nothing recorded shows it.
fn bounded_field() -> State {
    use EnergyType::*;
    let chesnaught = with_energy(CardId::B2010Chesnaught, &[Grass, Grass, Grass, Grass]);
    let stonjourner = with_energy(CardId::A1a048Stonjourner, &[Fighting, Fighting, Fighting]);
    let mut game = armed_against(
        chesnaught,
        "Needle Lariat",
        80,
        stonjourner,
        vec![],
        vec![],
        Some(CardId::B3155BoundedField),
    );
    apply_attack(&mut game, "Mega Kick");
    game.get_state_clone()
}

#[test]
fn bounded_field_keeps_the_hit_back_extra_at_20() {
    let state = bounded_field();
    assert_eq!(hp(&state, 1, 0), 70);
    assert_eq!(
        state.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()),
        Some(20),
        "Needle Lariat's 80 + 20 under Bounded Field; a x2 reading (160, or 80 + 40) would Knock Out Stonjourner (120 HP)"
    );
}

/// The Perish Body branch of `ApplyDamage` (coin outcomes). Constructed: a Galarian Cursola (Psychic;
/// Perish Body) carrying `Counterattack { amount: 40 }` is Knocked Out by Paldean Tauros (Fighting, weak
/// Psychic). On tails Tauros survives with 40 + 20 taken; on heads Perish Body Knocks it Out. The old
/// engine left a tails Tauros at 60.
/// Tauros's remaining HP after each seed's coin (`None` where Perish Body's heads Knocked it Out).
fn perish_body_branch() -> Vec<Option<u32>> {
    let mut out = vec![];
    for seed in 0..32 {
        let mut cursola = PlayedCard::from_id(CardId::A4a035GalarianCursola).with_remaining_hp(40);
        cursola.add_effect(CardEffect::Counterattack { amount: 40 }, 1);
        let tauros = with_energy(
            CardId::B2a058PaldeanTauros,
            &[EnergyType::Fighting, EnergyType::Colorless],
        );
        let mut game = game_with_board(
            vec![tauros, PlayedCard::from_id(CardId::A1130Ralts)],
            vec![cursola, PlayedCard::from_id(CardId::B1033Torchic)],
            0,
            20_000_000_300 + seed,
        );
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::ApplyDamage {
                attacking_ref: (0, 0),
                targets: vec![(50, 1, 0)],
                is_from_active_attack: true,
            },
            is_stack: false,
        });
        let state = game.get_state_clone();
        assert!(state.in_play_pokemon[1][0].is_none(), "seed {seed}: Cursola Knocked Out");
        out.push(state.in_play_pokemon[0][0].as_ref().map(|tauros| tauros.get_remaining_hp()));
    }
    out
}

#[test]
fn perish_body_branch_hit_back_takes_weakness() {
    let tauros = perish_body_branch();
    let tails: Vec<u32> = tauros.iter().flatten().copied().collect();
    assert!(!tails.is_empty() && tails.len() < tauros.len(), "both coins seen: {tauros:?}");
    assert!(tails.iter().all(|&hp| hp == 40), "{tauros:?}");
}

// ---- P2's off-switch (rules switch 2, PLAN (e); the coordinator via Dustin, Oct 9). Off is the engine before P2: the
// "before" column of `tests_before_fix_p2.log` for every scenario P2 changes, and the same board where it doesn't act.

fn off<R>(f: impl FnOnce() -> R) -> R {
    with_return_weakness(false, f)
}

/// With the switch off, each attack's hit back on a weak attacker is X flat again, and the Knock Out it decided is gone.
#[test]
fn switch_off_each_attack_hits_back_flat_again() {
    for row in rows() {
        let state = off(|| hit_back_once(&row, row.weak_attacker.clone(), row.weak_attack, vec![]));
        assert_eq!(hp(&state, 1, 0), row.holder_hp - row.weak_damage, "{}", row.title);
        assert_eq!(hp(&state, 0, 0), row.weak_attacker_hp - row.amount, "{}: flat with the switch off", row.title);

        let at = row.weak_attacker.clone().with_remaining_hp(row.amount + 20);
        let state = off(|| hit_back_once(&row, at, row.weak_attack, vec![PlayedCard::from_id(CardId::A1130Ralts)]));
        assert_eq!(hp(&state, 0, 0), 20, "{}: survives at 20", row.title);
        assert_eq!(state.points, [0, 0], "{}", row.title);
    }
}

/// With the switch off, every other scenario P2 changes gives the engine before P2's number (tests_before_fix_p2.log).
#[test]
fn switch_off_gives_the_engine_before_p2() {
    assert_eq!(hp(&off(recording_t8), 0, 0), 90, "183108 t8");
    let t10 = off(recording_t10);
    assert_eq!(hp(&t10, 0, 0), 80, "183108 t10");
    assert_eq!(t10.points, [3, 0]);
    let double = off(double_knockout);
    assert_eq!(double.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()), Some(20), "double Knock Out");
    assert_eq!(double.points, [1, 0]);
    assert_eq!(hp(&off(|| helmet_and_cursed_jewel(true)), 0, 0), 70, "Helmet and Cursed Jewel");
    assert_eq!(hp(&off(jugulis_with_cursed_effect), 0, 0), 90, "Automated Combat and an attack's 40");
    assert_eq!(hp(&off(held_back), 0, 0), 90, "held back (Psy Turbo)");
    assert_eq!(hp(&off(apply_damage_path), 0, 0), 90, "ApplyDamage");
    assert_eq!(hp(&off(metal_defender), 0, 0), 130, "Metal Defender");
    assert_eq!(hp(&off(swift), 0, 0), 60, "Swift");
    assert_eq!(off(bounded_field).in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp()), Some(40), "Bounded Field");
    let tauros = off(perish_body_branch);
    let tails: Vec<u32> = tauros.iter().flatten().copied().collect();
    assert!(!tails.is_empty() && tails.iter().all(|&hp| hp == 60), "Perish Body branch, tails: {tauros:?}");
    // The same seeds give the same coins on and off: the switch draws nothing.
    assert_eq!(tauros.iter().map(Option::is_some).collect::<Vec<_>>(),
               perish_body_branch().iter().map(Option::is_some).collect::<Vec<_>>());
}

/// Where P2 doesn't act (an attacker not weak to the holder, a Tool's or an Ability's return damage, a Benched attacker),
/// the board is the same with the switch on and off.
#[test]
fn switch_changes_nothing_where_p2_does_not_act() {
    for row in rows() {
        let run = |on: bool| with_return_weakness(on, || hit_back_once(&row, snorlax(), "Rollout", vec![]));
        assert_eq!(run(true), run(false), "{}", row.title);
    }
    assert_eq!(with_return_weakness(true, || helmet_and_cursed_jewel(false)), off(|| helmet_and_cursed_jewel(false)));
    assert_eq!(with_return_weakness(true, benched_attacker), off(benched_attacker));
    let helmet_and_ability = || {
        let mut out = vec![];
        let torchic = PlayedCard::from_id(CardId::B1033Torchic).with_tool(get_card_by_enum(CardId::A2148RockyHelmet));
        let mut game = game_with_board(vec![with_energy(CardId::A2b052Tinkatink, &[EnergyType::Metal])], vec![torchic], 0, SEED);
        apply_attack(&mut game, "Corkscrew Punch");
        out.push(game.get_state_clone());
        let mut game = game_with_board(
            vec![with_energy(CardId::A1129MewtwoEx, &[EnergyType::Psychic, EnergyType::Colorless])],
            vec![PlayedCard::from_id(CardId::B3a046IronJugulis)],
            0,
            SEED,
        );
        apply_attack(&mut game, "Psychic Sphere");
        out.push(game.get_state_clone());
        out
    };
    assert_eq!(with_return_weakness(true, helmet_and_ability), off(helmet_and_ability));
}

/// The switch is on by default, an inner call overrides an outer one for its length, the setting comes back after a
/// return and after a panic, and another thread keeps its own setting.
#[test]
fn switch_scoping() {
    let houndstone = || hp(&recording_t8(), 0, 0);
    assert_eq!(houndstone(), 70, "on by default");
    assert_eq!(off(|| with_return_weakness(true, houndstone)), 70, "inner on");
    assert_eq!(off(|| (houndstone(), with_return_weakness(true, houndstone), houndstone())), (90, 70, 90));
    assert_eq!(houndstone(), 70, "restored after a return");
    let caught = std::panic::catch_unwind(|| off(|| -> u32 { panic!("inside the switch") }));
    assert!(caught.is_err());
    assert_eq!(houndstone(), 70, "restored after a panic");
    off(|| {
        assert_eq!(std::thread::spawn(houndstone).join().unwrap(), 70, "another thread keeps the default");
        assert_eq!(houndstone(), 90);
    });
}
