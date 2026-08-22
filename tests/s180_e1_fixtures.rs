//! §180 — E1 deterministic mechanics fixtures.
//! Built strictly from the sealed plan `s178_E1_FIXTURE_PLAN_v2.txt`
//! sha256 21f7279977c971bf613989db518340d07766d9018e4d8d43c6ee108ea486e05a.
//!
//! Every fixture CONSTRUCTS its state (seed 0 is an initialiser only; the board, hands and
//! discard under test are overwritten). No seed is scanned and no run is repeated for a
//! different outcome. Results are the behaviour of the s120 SOURCE at commit b6ae00c —
//! NOT automatically the behaviour of the qualified binary deckgym-bin-3518-s120k.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition, TrainerCard},
    test_support::{attack_action, get_initialized_game},
    Game,
};

// ---------------------------------------------------------------------------------------------
// helpers
// ---------------------------------------------------------------------------------------------

fn trainer(card_id: CardId) -> TrainerCard {
    match get_card_by_enum(card_id) {
        Card::Trainer(tc) => tc,
        _ => panic!("expected a trainer card"),
    }
}

fn play_trainer(game: &mut Game<'static>, actor: usize, card_id: CardId) {
    let trainer_card = trainer(card_id);
    game.apply_action(&Action {
        actor,
        action: SimpleAction::Play { trainer_card },
        is_stack: false,
    });
}

/// Apply the single offered action matching `pred`. Panics if it is not offered — an
/// unreachable choice is UNTESTABLE and must be reported as such, never worked around.
fn choose<F>(game: &mut Game<'static>, what: &str, pred: F)
where
    F: Fn(&SimpleAction) -> bool,
{
    let state = game.get_state_clone();
    let (_actor, choices) = state.generate_possible_actions();
    let chosen = choices
        .iter()
        .find(|a| pred(&a.action))
        .cloned()
        .unwrap_or_else(|| panic!("UNTESTABLE: no offered action matched {what}"));
    game.apply_action(&chosen);
}

fn offered(game: &Game<'static>) -> Vec<SimpleAction> {
    let state = game.get_state_clone();
    let (_actor, choices) = state.generate_possible_actions();
    choices.into_iter().map(|a| a.action).collect()
}

fn attach_tool_from_hand(game: &mut Game<'static>, actor: usize, tool: CardId, slot: usize) {
    play_trainer(game, actor, tool);
    choose(game, "AttachTool", |a| {
        matches!(a, SimpleAction::AttachTool { in_play_idx, .. } if *in_play_idx == slot)
    });
}

fn hp(game: &Game<'static>, player: usize, slot: usize) -> Option<u32> {
    game.get_state_clone().in_play_pokemon[player][slot]
        .as_ref()
        .map(|p| p.get_remaining_hp())
}

fn note(component: &str, msg: String) {
    println!("[{component}] {msg}");
}

// ---------------------------------------------------------------------------------------------
// C1 — Ancient Booster Energy Capsule B3a 069: +40 HP for Ancient, +0 for non-Ancient
// ---------------------------------------------------------------------------------------------

fn capsule_case(holder: CardId) -> u32 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(holder)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::B3a069AncientBoosterEnergyCapsule)];
    game.set_state(state);
    attach_tool_from_hand(
        &mut game,
        0,
        CardId::B3a069AncientBoosterEnergyCapsule,
        0,
    );
    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert!(
        active.attached_tool.is_some(),
        "the Tool must stay attached — attachment is legal on any Pokemon (§172)"
    );
    active.get_remaining_hp()
}

#[test]
fn c1_capsule_ancient_positive() {
    let observed = capsule_case(CardId::B3a003BruteBonnet);
    note("C1+", format!("Brute Bonnet B3a 003 (base 100) + Capsule -> {observed}"));
    assert_eq!(observed, 140, "Ancient holder must get +40 HP");
}

#[test]
fn c1_capsule_non_ancient_control() {
    let observed = capsule_case(CardId::A1a009Dhelmise);
    note("C1-", format!("Dhelmise A1a 009 (base 100, not Ancient) + Capsule -> {observed}"));
    assert_eq!(observed, 100, "non-Ancient holder must get +0 HP");
}

// ---------------------------------------------------------------------------------------------
// C2 — Leaf Cape A3 147: +30 HP for Grass, +0 for non-Grass
// ---------------------------------------------------------------------------------------------

fn leaf_cape_case(holder: CardId) -> u32 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(holder)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::A3147LeafCape)];
    game.set_state(state);
    attach_tool_from_hand(&mut game, 0, CardId::A3147LeafCape, 0);
    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert!(
        active.attached_tool.is_some(),
        "the Tool must stay attached regardless of type (§173)"
    );
    active.get_remaining_hp()
}

#[test]
fn c2_leaf_cape_grass_positive() {
    let observed = leaf_cape_case(CardId::A1a009Dhelmise);
    note("C2+", format!("Dhelmise A1a 009 (Grass, base 100) + Leaf Cape -> {observed}"));
    assert_eq!(observed, 130, "Grass holder must get +30 HP");
}

#[test]
fn c2_leaf_cape_non_grass_control() {
    let observed = leaf_cape_case(CardId::A1079Lapras);
    note("C2-", format!("Lapras A1 079 (Water, base 100) + Leaf Cape -> {observed}"));
    assert_eq!(observed, 100, "non-Grass holder must get +0 HP");
}

// ---------------------------------------------------------------------------------------------
// C3 — Field Blower removes an HP Tool: KO at the boundary, survival below it
// ---------------------------------------------------------------------------------------------

/// Returns (remaining_hp_after_removal_or_None_if_KO, tool_still_attached)
fn hp_tool_removal_case(damage: u32) -> (Option<u32>, bool) {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::B3a003BruteBonnet)
            .with_tool(get_card_by_enum(CardId::B3a069AncientBoosterEnergyCapsule))
            .with_damage(damage)],
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::B3147FieldBlower)];
    game.set_state(state);

    let before = hp(&game, 1, 0);
    note(
        "C3",
        format!("pre: Brute Bonnet+Capsule damage {damage} -> remaining {before:?}"),
    );

    play_trainer(&mut game, 0, CardId::B3147FieldBlower);
    choose(&mut game, "DiscardToolFromPokemon{player:1,idx:0}", |a| {
        matches!(
            a,
            SimpleAction::DiscardToolFromPokemon {
                player: 1,
                in_play_idx: 0
            }
        )
    });

    let state = game.get_state_clone();
    let still = state.in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.attached_tool.is_some())
        .unwrap_or(false);
    (hp(&game, 1, 0), still)
}

#[test]
fn c3_hp_tool_removal_ko_at_boundary() {
    // effective max 140; damage 120 -> 20 remaining. Removing the Tool drops max to 100,
    // which is <= the 120 damage already on it: immediate KO (§174).
    let (after, tool) = hp_tool_removal_case(120);
    note("C3+", format!("post-removal: remaining {after:?}, tool_attached {tool}"));
    assert_eq!(
        after, None,
        "removing the HP Tool must knock the holder out immediately at the boundary"
    );
}

#[test]
fn c3_hp_tool_removal_below_boundary_control() {
    // damage 90 < base 100: the holder must survive the same removal.
    let (after, tool) = hp_tool_removal_case(90);
    note("C3-", format!("post-removal: remaining {after:?}, tool_attached {tool}"));
    assert_eq!(after, Some(10), "below the boundary the holder survives at 100 - 90");
    assert!(!tool, "the selected Tool must have left play");
}

// ---------------------------------------------------------------------------------------------
// C4/C5/C6 — Pokémon Center Lady A2b 070
// ---------------------------------------------------------------------------------------------

fn center_lady_case(
    damage: u32,
    statuses: &[StatusCondition],
    play: bool,
) -> (u32, Vec<&'static str>) {
    let mut holder = PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(damage);
    for s in statuses {
        holder = holder.with_status_condition(*s);
    }
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![holder],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::A2b070PokemonCenterLady)];
    game.set_state(state);

    if play {
        play_trainer(&mut game, 0, CardId::A2b070PokemonCenterLady);
        choose(&mut game, "Heal{in_play_idx:0}", |a| {
            matches!(a, SimpleAction::Heal { in_play_idx: 0, .. })
        });
    }

    let state = game.get_state_clone();
    let active = state.get_active(0);
    let mut left = vec![];
    for (name, s) in [
        ("Poisoned", StatusCondition::Poisoned),
        ("Paralyzed", StatusCondition::Paralyzed),
        ("Asleep", StatusCondition::Asleep),
        ("Burned", StatusCondition::Burned),
        ("Confused", StatusCondition::Confused),
    ] {
        if active.has_status(s) {
            left.push(name);
        }
    }
    (active.get_remaining_hp(), left)
}

#[test]
fn c4_center_lady_damaged_only_heals_exactly_30() {
    let (hp_after, left) = center_lady_case(50, &[], true);
    note("C4", format!("damage 50, no status -> remaining {hp_after}, statuses {left:?}"));
    assert_eq!(hp_after, 50, "70 base, 50 damage healed by 30 -> 20 damage -> 50 remaining");
    assert!(left.is_empty());
}

#[test]
fn c5_center_lady_status_only_clears_all_conditions() {
    let (hp_after, left) = center_lady_case(
        0,
        &[StatusCondition::Poisoned, StatusCondition::Asleep],
        true,
    );
    note("C5", format!("damage 0, Poisoned+Asleep -> remaining {hp_after}, statuses {left:?}"));
    assert_eq!(hp_after, 70, "an undamaged target must not gain or lose HP");
    assert!(left.is_empty(), "every Special Condition must clear");
}

#[test]
fn c6_center_lady_damaged_plus_status_does_both() {
    let (hp_after, left) = center_lady_case(
        50,
        &[StatusCondition::Poisoned, StatusCondition::Asleep],
        true,
    );
    note("C6", format!("damage 50, Poisoned+Asleep -> remaining {hp_after}, statuses {left:?}"));
    assert_eq!(hp_after, 50);
    assert!(left.is_empty());
}

#[test]
fn c6b_center_lady_not_played_control() {
    let (hp_after, left) = center_lady_case(
        50,
        &[StatusCondition::Poisoned, StatusCondition::Asleep],
        false,
    );
    note("C6ctl", format!("not played -> remaining {hp_after}, statuses {left:?}"));
    assert_eq!(hp_after, 20, "without the supporter nothing may change");
    assert_eq!(left.len(), 2, "without the supporter both conditions remain");
}

// ---------------------------------------------------------------------------------------------
// C7 — no-op target legality: OBSERVATION ONLY. The real-game rule is undetermined (§171),
// so nothing here is asserted as correct or incorrect.
// ---------------------------------------------------------------------------------------------

#[test]
fn c7_center_lady_no_op_target_observation() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(50), // makes the card playable
            PlayedCard::from_id(CardId::A1001Bulbasaur),                 // undamaged, unconditioned
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.hands[0] = vec![get_card_by_enum(CardId::A2b070PokemonCenterLady)];
    game.set_state(state);

    play_trainer(&mut game, 0, CardId::A2b070PokemonCenterLady);
    let choices = offered(&game);
    let no_op_offered = choices
        .iter()
        .any(|a| matches!(a, SimpleAction::Heal { in_play_idx: 1, .. }));
    note(
        "C7",
        format!(
            "heal targets offered: {} | no-op (undamaged, unconditioned bench) target offered: {}",
            choices
                .iter()
                .filter(|a| matches!(a, SimpleAction::Heal { .. }))
                .count(),
            no_op_offered
        ),
    );
    if no_op_offered {
        choose(&mut game, "Heal{in_play_idx:1}", |a| {
            matches!(a, SimpleAction::Heal { in_play_idx: 1, .. })
        });
        let state = game.get_state_clone();
        note(
            "C7",
            format!(
                "after healing the no-op target: bench remaining {:?}, active remaining {:?}",
                state.in_play_pokemon[0][1].as_ref().map(|p| p.get_remaining_hp()),
                state.in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp())
            ),
        );
    }
    note("C7", "OBSERVATION ONLY — no PASS, no DEFECT (rule undetermined, §171)".to_string());
}

// ---------------------------------------------------------------------------------------------
// C8/C9/C10 — Protective Poncho B2 147
// ---------------------------------------------------------------------------------------------

/// Hitmonlee's Stretch Kick: 30 damage to one of the opponent's Benched Pokemon.
fn poncho_attack_case(with_poncho: bool) -> Option<u32> {
    let mut bench = PlayedCard::from_id(CardId::A1001Bulbasaur);
    if with_poncho {
        bench = bench.with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho));
    }
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1154Hitmonlee).with_energy(vec![EnergyType::Fighting])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), bench],
    );
    state.current_player = 0;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1154Hitmonlee, 0),
        is_stack: false,
    });
    choose(&mut game, "ApplyDamage to opponent bench slot 1", |a| {
        matches!(a, SimpleAction::ApplyDamage { targets, .. }
            if targets.iter().any(|(_, p, i)| *p == 1 && *i == 1))
    });
    hp(&game, 1, 1)
}

#[test]
fn c8_poncho_prevents_bench_damage_from_attack() {
    let observed = poncho_attack_case(true);
    note("C8", format!("protected bench slot after Stretch Kick -> {observed:?}"));
    assert_eq!(observed, Some(70), "a Poncho'd benched Pokemon takes 0 from an attack");
}

#[test]
fn c10a_no_poncho_bench_control_attack() {
    let observed = poncho_attack_case(false);
    note("C10a", format!("unprotected bench slot after Stretch Kick -> {observed:?}"));
    assert_eq!(observed, Some(40), "without the Poncho the printed 30 must land");
}

/// Greninja's Water Shuriken: 20 damage to one of the opponent's Pokemon, from the bench.
fn poncho_ability_case(with_poncho: bool) -> Option<u32> {
    let mut bench = PlayedCard::from_id(CardId::A1001Bulbasaur);
    if with_poncho {
        bench = bench.with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho));
    }
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A1089Greninja),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), bench],
    );
    state.current_player = 0;
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx: 1 },
        is_stack: false,
    });
    choose(&mut game, "ApplyDamage to opponent bench slot 1", |a| {
        matches!(a, SimpleAction::ApplyDamage { targets, .. }
            if targets.iter().any(|(_, p, i)| *p == 1 && *i == 1))
    });
    hp(&game, 1, 1)
}

#[test]
fn c9_poncho_prevents_bench_damage_from_ability() {
    let observed = poncho_ability_case(true);
    note("C9", format!("protected bench slot after Water Shuriken -> {observed:?}"));
    assert_eq!(observed, Some(70), "a Poncho'd benched Pokemon takes 0 from an Ability");
}

#[test]
fn c10b_no_poncho_bench_control_ability() {
    let observed = poncho_ability_case(false);
    note("C10b", format!("unprotected bench slot after Water Shuriken -> {observed:?}"));
    assert_eq!(observed, Some(50), "without the Poncho the printed 20 must land");
}

#[test]
fn c10c_poncho_on_active_is_not_protected() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_tool(get_card_by_enum(CardId::B2147ProtectivePoncho))],
    );
    state.current_player = 0;
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    let observed = hp(&game, 1, 0);
    note("C10c", format!("Poncho holder in the ACTIVE spot after Vine Whip -> {observed:?}"));
    assert_eq!(observed, Some(30), "the Poncho protects the Bench only (70 - 40)");
}

// ---------------------------------------------------------------------------------------------
// C11 — Mega Burst discards all Fire/Lightning Energy it used (nonterminal transition)
// ---------------------------------------------------------------------------------------------

#[test]
fn c11_mega_burst_discards_fire_and_lightning_only() {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B4120MegaRayquazaEx).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Fire,
                EnergyType::Lightning,
                EnergyType::Lightning,
                EnergyType::Water,
            ]),
        ],
        vec![PlayedCard::from_id(CardId::B4037WailordEx)],
    );
    state.current_player = 0;
    state.discard_energies[0] = vec![];
    game.set_state(state);

    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B4120MegaRayquazaEx, 0),
        is_stack: false,
    });

    let state = game.get_state_clone();
    let attacker = state.in_play_pokemon[0][0]
        .as_ref()
        .expect("the attacker must survive its own nonterminal attack");
    let defender_hp = state.in_play_pokemon[1][0]
        .as_ref()
        .map(|p| p.get_remaining_hp());
    note(
        "C11",
        format!(
            "attacker energy after Mega Burst {:?} | opponent (Wailord ex 250) remaining {:?} | discard_energies {:?}",
            attacker.attached_energy, defender_hp, state.discard_energies[0]
        ),
    );
    assert!(
        defender_hp.is_some(),
        "the fixture must stay nonterminal, or the discard cannot be read"
    );
    assert!(
        !attacker.attached_energy.contains(&EnergyType::Fire)
            && !attacker.attached_energy.contains(&EnergyType::Lightning),
        "all Fire and Lightning Energy used by the effect must leave the attacker"
    );
    assert!(
        attacker.attached_energy.contains(&EnergyType::Water),
        "the Water negative control must remain attached"
    );
}

// ---------------------------------------------------------------------------------------------
// C12 — KO of a Mega Evolution Pokémon ex awards exactly 3 points (§179), non-Mega awards 1
// ---------------------------------------------------------------------------------------------

fn ko_points_case(defender: CardId, damage: u32) -> u8 {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        vec![PlayedCard::from_id(defender).with_damage(damage)],
    );
    state.current_player = 0;
    state.points = [0, 0];
    game.set_state(state);

    let before = game.get_state_clone().points[0];
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[1][0].is_none(),
        "UNTESTABLE: the defender was not knocked out by the fixture's attack"
    );
    state.points[0] - before
}

#[test]
fn c12_mega_ex_ko_awards_three_points() {
    // Mega Rayquaza ex B4 120, 180 HP, 150 damage -> 30 remaining; Vine Whip deals 40.
    let delta = ko_points_case(CardId::B4120MegaRayquazaEx, 150);
    note("C12+", format!("KO of Mega Rayquaza ex -> points delta {delta}"));
    assert_eq!(delta, 3, "the Mega Evolution ex rule box awards the opponent 3 points");
}

#[test]
fn c12_non_mega_ko_awards_one_point_control() {
    // Bulbasaur A1 001, 70 HP, 40 damage -> 30 remaining; the same attack KOs it.
    let delta = ko_points_case(CardId::A1001Bulbasaur, 40);
    note("C12-", format!("KO of a non-Mega Basic -> points delta {delta}"));
    assert_eq!(delta, 1, "an ordinary knockout must award exactly 1 point");
}

// ---------------------------------------------------------------------------------------------
// C13/C14/C15 — Professor Sada B3a 072
// ---------------------------------------------------------------------------------------------

fn sada_case(discard: Vec<EnergyType>) -> (usize, usize, Vec<usize>, usize) {
    let mut game = get_initialized_game(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::B3a003BruteBonnet), // Ancient, slot 0
            PlayedCard::from_id(CardId::B3a035SandyShocks), // Ancient, slot 1
            PlayedCard::from_id(CardId::A1001Bulbasaur),    // NOT Ancient, slot 2
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    state.current_player = 0;
    state.discard_energies[0] = discard;
    state.hands[0] = vec![get_card_by_enum(CardId::B3a072ProfessorSada)];
    game.set_state(state);

    play_trainer(&mut game, 0, CardId::B3a072ProfessorSada);

    // Every OFFERED assignment must respect the card: at most 3, one per type, Ancient only.
    let choices = offered(&game);
    let mut assignments_seen = 0usize;
    for a in &choices {
        if let SimpleAction::SadaAttach { assignments } = a {
            assignments_seen += 1;
            assert!(
                assignments.len() <= 3,
                "an offered assignment attaches more than 3 Energy"
            );
            let mut types: Vec<EnergyType> = assignments.iter().map(|(t, _)| *t).collect();
            let before = types.len();
            types.sort_by_key(|t| format!("{t:?}"));
            types.dedup();
            assert_eq!(before, types.len(), "an offered assignment duplicates an Energy type");
            assert!(
                assignments.iter().all(|(_, slot)| *slot == 0 || *slot == 1),
                "an offered assignment targets a non-Ancient slot"
            );
        }
    }

    choose(&mut game, "SadaAttach", |a| {
        matches!(a, SimpleAction::SadaAttach { .. })
    });

    let state = game.get_state_clone();
    let counts: Vec<usize> = (0..3)
        .map(|i| {
            state.in_play_pokemon[0][i]
                .as_ref()
                .map(|p| p.attached_energy.len())
                .unwrap_or(0)
        })
        .collect();
    let attached_total = counts[0] + counts[1];
    let mut all_types: Vec<EnergyType> = vec![];
    for i in 0..2 {
        if let Some(p) = state.in_play_pokemon[0][i].as_ref() {
            all_types.extend(p.attached_energy.iter().copied());
        }
    }
    let mut distinct = all_types.clone();
    distinct.sort_by_key(|t| format!("{t:?}"));
    distinct.dedup();
    (attached_total, distinct.len(), counts, assignments_seen)
}

#[test]
fn c13_sada_three_available_types_attaches_three_distinct() {
    let (total, distinct, counts, offers) = sada_case(vec![
        EnergyType::Fire,
        EnergyType::Lightning,
        EnergyType::Water,
    ]);
    note(
        "C13",
        format!("3 types available -> attached {total} (distinct {distinct}), per-slot {counts:?}, offered assignments {offers}"),
    );
    assert_eq!(total, 3, "three available distinct types must attach three Energy");
    assert_eq!(distinct, 3, "one Energy per type, pairwise distinct");
    assert_eq!(counts[2], 0, "C15: the non-Ancient slot must receive nothing");
}

#[test]
fn c14_sada_four_available_types_attaches_exactly_three_distinct() {
    let (total, distinct, counts, offers) = sada_case(vec![
        EnergyType::Fire,
        EnergyType::Lightning,
        EnergyType::Water,
        EnergyType::Grass,
    ]);
    note(
        "C14",
        format!("4 types available -> attached {total} (distinct {distinct}), per-slot {counts:?}, offered assignments {offers}"),
    );
    assert_eq!(total, 3, "with four available types exactly three Energy attach");
    assert_eq!(distinct, 3, "the three must be of pairwise distinct types");
    assert_eq!(counts[2], 0, "C15: the non-Ancient slot must receive nothing");
}
