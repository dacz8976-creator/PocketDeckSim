// Jigglypuff (C1 051, C1 184) - Soothing Lullaby (R8-08g): "Your opponent's Active Pokémon is now Asleep. Your opponent
// flips 2 coins for this Special Condition, and if any of them are tails, that Pokémon is still Asleep." Upstream's four
// tests (#438, 20d1857: tests/pokemon/c1_attacks/jigglypuff.rs) with the helpers of upstream's c1_attacks/mod.rs, as
// c1_lunala_test.rs ports them, reading `sleep_checkup_coins()` where upstream reads `public_details().sleep_coins`. Then
// the fork's tests (design r808p2 §C.2, L1-L15): Crystal Body and Clear Veil; a shielded or immune Pokémon already Asleep
// keeps its 1 coin (divergence D1); Soothing Lullaby on a sleeper and twice; an ordinary Sleep after it resets the count
// (the reset reading); Paralysis and Confusion replace it; Poison and Burn keep it, with the Burn coin after both Sleep
// coins (the joint table); both seats' coins by prefix sums; the cures, switches, evolution, devolution and a Knock Out
// that end it; Bad Dreams before the coins; the deferred Checkup frame; the printings' status; Mew ex's copy; Will. Every
// step also checks the invariant (design A.2.2): a recorded count implies Asleep. And the coordinator's conditions
// (coordinator-129): C1, every saved row, State and observation without a Soothing Lullaby keeps its bytes (pinned at
// 45e87ed2, before the change: `BYTES_BEFORE`), old JSON loads with no count, a forged count reads as 1 coin, and both
// seats' observations carry the count; C2, every path that ends or replaces the Sleep leaves the raw field unset, read
// from the JSON (the key is skipped only when the field is `None`). The coin model's unit tests are in
// apply_action_helpers.rs.
use std::collections::BTreeMap;

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    data_exporter::ExportedDataPoint,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    observation::{PlayerObservation, RevealedKnowledge, INFORMATION_MODEL},
    test_support::{attack_action, get_initialized_game_with_board, play_trainer, trainer_from_id},
    Game, State,
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

// Upstream's tests/pokemon/c1_attacks/mod.rs (the fork's `attack` and `end_turn` also check the invariant).

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
fn attack(game: &mut Game<'static>, id: CardId, index: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, index),
        is_stack: false,
    });
    assert_invariant(&game.get_state_clone());
}
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    assert_invariant(&game.get_state_clone());
}
fn defender_damage(game: &Game<'static>) -> u32 {
    game.get_state_clone().get_active(1).taken()
}

// Upstream's tests/pokemon/c1_attacks/jigglypuff.rs: `lullaby_game`, then its four tests.

fn lullaby_game(id: CardId, seed: u64) -> Game<'static> {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    game
}

// The Sleep itself is not a coin flip: the defender is always Asleep afterwards, with 2 coins to
// flip at each Checkup.
#[test]
fn soothing_lullaby_always_puts_the_defender_to_sleep() {
    for id in JIGGLYPUFF {
        for seed in 0..20 {
            let game = lullaby_game(id, seed);
            assert_eq!(defender_damage(&game), 30, "{id:?}");
            let state = game.get_state_clone();
            assert!(state.get_active(1).is_asleep(), "{id:?}");
            assert_eq!(state.get_active(1).sleep_checkup_coins(), 2);
        }
    }
}

// Only both coins heads wake it, so after the Checkup 1 in 4 are awake (the exact 1/4 is checked
// on the Checkup itself).
#[test]
fn soothing_lullaby_defender_wakes_at_checkup_about_one_time_in_four() {
    let id = CardId::C1051Jigglypuff;
    let (mut asleep, mut awake) = (0, 0);
    for seed in 0..200 {
        let mut game = lullaby_game(id, seed);
        end_turn(&mut game, 0);
        if game.get_state_clone().get_active(1).is_asleep() {
            asleep += 1;
        } else {
            awake += 1;
        }
    }
    assert!(
        awake > 0 && asleep > awake * 2,
        "{asleep} asleep vs {awake} awake"
    );
}

// A Pokémon that cannot be Asleep (Hoothoot's Insomnia) does not carry the 2 coins either.
#[test]
fn soothing_lullaby_does_nothing_to_a_defender_that_cannot_sleep() {
    let id = CardId::C1051Jigglypuff;
    let mut game = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![ready(id, 0)],
        vec![durable_of(CardId::A4140Hoothoot)],
    );
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert!(!state.get_active(1).is_asleep());
    // Fork: upstream's `public_details` shows 0 coins for a Pokémon that is not Asleep; `sleep_checkup_coins` reads the
    // usual 1, and the raw count is unset.
    assert_eq!(state.get_active(1).sleep_checkup_coins(), 1);
    assert_eq!(raw_count(state.get_active(1)), None);
}

// Full Heal ends the Sleep, and with it the 2 coins: a later ordinary Sleep flips 1.
#[test]
fn soothing_lullaby_sleep_ends_with_full_heal() {
    let mut game = lullaby_game(CardId::C1051Jigglypuff, 0);
    let mut state = game.get_state_clone();
    state.hands[1] = vec![Card::Trainer(trainer_from_id(CardId::C1122FullHeal))];
    state.current_player = 1;
    game.set_state(state);
    play_trainer(&mut game, 1, trainer_from_id(CardId::C1122FullHeal));

    let mut state = game.get_state_clone();
    assert!(!state.get_active(1).is_asleep());
    assert_eq!(raw_count(state.get_active(1)), None, "C2: Full Heal unsets the count");
    state.apply_status_condition(1, 0, StatusCondition::Asleep);
    assert_eq!(state.get_active(1).sleep_checkup_coins(), 1);
}

// The fork's tests.

const JIGGLYPUFF: [CardId; 2] = [CardId::C1051Jigglypuff, CardId::C1184Jigglypuff];

/// The raw Soothing Lullaby count of `pokemon`, read from its JSON. The key is skipped only when the field is `None`, so
/// `None` here is the field itself unset, not only `sleep_checkup_coins() == 1`.
fn raw_count(pokemon: &PlayedCard) -> Option<u64> {
    serde_json::to_value(pokemon)
        .unwrap()
        .get("sleep_coins_override")
        .map(|count| count.as_u64().expect("a count"))
}

/// The invariant of design A.2.2 on every Pokémon in play: a recorded count implies Asleep.
fn assert_invariant(state: &State) {
    for (player, board) in state.in_play_pokemon.iter().enumerate() {
        for pokemon in board.iter().flatten() {
            assert!(
                raw_count(pokemon).is_none() || pokemon.is_asleep(),
                "player {player}'s {} holds a Soothing Lullaby count but is not Asleep",
                pokemon.get_name()
            );
        }
    }
}

/// Applies `action` for `actor` (a non-stack action) and checks the invariant.
fn act(game: &mut Game<'static>, actor: usize, action: SimpleAction) {
    game.apply_action(&Action {
        actor,
        action,
        is_stack: false,
    });
    assert_invariant(&game.get_state_clone());
}

/// Applies the offered action `pick` matches, as `generate_possible_actions` offers it (a stack choice keeps its frame),
/// and checks the invariant.
fn choose(game: &mut Game<'static>, pick: impl Fn(&SimpleAction) -> bool) {
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    let chosen = actions
        .into_iter()
        .find(|action| pick(&action.action))
        .expect("the action is offered");
    game.apply_action(&chosen);
    assert_invariant(&game.get_state_clone());
}

/// `actor` plays the Trainer `id` from hand, with the invariant checked after.
fn play(game: &mut Game<'static>, actor: usize, id: CardId) {
    let mut state = game.get_state_clone();
    state.hands[actor].push(get_card_by_enum(id));
    game.set_state(state);
    play_trainer(game, actor, trainer_from_id(id));
    assert_invariant(&game.get_state_clone());
}

/// The index of the attack titled `title` on `id`.
fn index_of(id: CardId, title: &str) -> usize {
    let Card::Pokemon(p) = get_card_by_enum(id) else {
        panic!("Pokémon required")
    };
    p.attacks
        .iter()
        .position(|attack| attack.title == title)
        .expect("the attack is printed")
}

/// `ready` for the attack titled `title`, and its use by player 0.
fn ready_for(id: CardId, title: &str) -> PlayedCard {
    ready(id, index_of(id, title))
}
fn attack_titled(game: &mut Game<'static>, id: CardId, title: &str) {
    attack(game, id, index_of(id, title));
}

/// `seed`'s game with `own` (player 0) and `theirs` (player 1) in play, `actor` to act: player 0 on turn 3 or player 1
/// on turn 4.
fn board_at(seed: u64, actor: usize, own: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> Game<'static> {
    get_initialized_game_with_board(seed, actor, 3 + actor as u8, own, theirs)
}

/// Player 0's Jigglypuff `id` uses Soothing Lullaby on player 1's `defender`, from `seed`'s game.
fn lullaby_on(id: CardId, seed: u64, defender: PlayedCard) -> Game<'static> {
    let mut game = board_at(seed, 0, vec![ready(id, 0)], vec![defender]);
    attack(&mut game, id, 0);
    game
}

/// `defender` after a Soothing Lullaby that landed (30 damage, Asleep, 2 coins), to set on any board.
fn lullabied(defender: PlayedCard) -> PlayedCard {
    let pokemon = lullaby_on(CardId::C1051Jigglypuff, 0, defender)
        .get_state_clone()
        .get_active(1)
        .clone();
    assert_eq!((pokemon.is_asleep(), raw_count(&pokemon)), (true, Some(2)));
    pokemon
}

/// `pokemon` as if its Sleep were ordinary: the same JSON without the key, a twin that never had Soothing Lullaby (and
/// what a state saved before the field existed loads as).
fn without_count(pokemon: &PlayedCard) -> PlayedCard {
    let mut encoded = serde_json::to_value(pokemon).unwrap();
    encoded.as_object_mut().unwrap().remove("sleep_coins_override");
    serde_json::from_value(encoded).unwrap()
}

/// `pokemon` with a hand-edited count.
fn forged(pokemon: &PlayedCard, count: u64) -> PlayedCard {
    let mut encoded = serde_json::to_value(pokemon).unwrap();
    encoded["sleep_coins_override"] = serde_json::json!(count);
    serde_json::from_value(encoded).unwrap()
}

fn end_turn_action(actor: usize) -> Action {
    Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    }
}

/// Each branch of `action`'s forecast from `state` with its probability and the state it leaves (rng seed 9, as the
/// Checkup pin), each checked for the invariant.
fn branches(state: &State, action: &Action) -> Vec<(f64, State)> {
    let (probabilities, mutations) = try_forecast_action(state, action).unwrap().into_branches();
    probabilities
        .into_iter()
        .zip(mutations)
        .map(|(probability, mutation)| {
            let mut next = state.clone();
            mutation(&mut StdRng::seed_from_u64(9), &mut next, action);
            assert_invariant(&next);
            (probability, next)
        })
        .collect()
}

fn probabilities(state: &State, action: &Action) -> Vec<f64> {
    branches(state, action).into_iter().map(|(probability, _)| probability).collect()
}

/// The chance that `player`'s Active Pokémon is awake after `action` (an `EndTurn` or a deferred Checkup frame).
fn wake_chance(state: &State, action: &Action, player: usize) -> f64 {
    branches(state, action)
        .iter()
        .filter(|(_, next)| !next.get_active(player).is_asleep())
        .map(|(probability, _)| probability)
        .sum()
}

/// After a Soothing Lullaby, the exact Checkup: 4 equally likely branches, awake in 1 of them; and the raw count is 2 on
/// both printings.
#[test]
fn test_soothing_lullaby_checkup_wakes_one_time_in_four_exactly() {
    for id in JIGGLYPUFF {
        let state = lullaby_game(id, 0).get_state_clone();
        assert_eq!(raw_count(state.get_active(1)), Some(2), "{id:?}");
        assert_eq!(probabilities(&state, &end_turn_action(0)), vec![0.25; 4], "{id:?}");
        assert_eq!(wake_chance(&state, &end_turn_action(0), 1), 0.25, "{id:?}");
    }
}

/// Player 0's Jigglypuff uses Soothing Lullaby on player 1's `defender`, which holds a [G] Energy, with Teal Mask Ogerpon
/// ex (B2 017) on player 1's Bench. Soothing Wind: "Each of your Pokémon that has any Energy attached recovers from all
/// Special Conditions and can't be affected by any Special Conditions." (an immunity inside `try_apply_status_condition`).
fn lullaby_under_soothing_wind(defender: PlayedCard) -> Game<'static> {
    let id = CardId::C1051Jigglypuff;
    let ogerpon = PlayedCard::from_id(CardId::B2017TealMaskOgerponEx);
    let defender = defender.with_energy(vec![EnergyType::Grass]);
    let mut game = board_at(0, 0, vec![ready(id, 0)], vec![defender, ogerpon]);
    attack(&mut game, id, 0);
    game
}

/// L1: Crystal Body (Regice A2 034: "Prevent all effects of attacks used by your opponent's Pokémon done to this
/// Pokémon.") and Clear Veil (B4 149, the same for its holder) stop the Sleep, and Soothing Wind makes its Pokémon
/// immune to it: the 30 damage lands, no Sleep, no count.
#[test]
fn test_crystal_body_clear_veil_and_soothing_wind_leave_no_sleep_and_no_count() {
    let clear_veil = durable().with_tool(get_card_by_enum(CardId::B4149ClearVeil));
    let soothing_wind = lullaby_under_soothing_wind(durable());
    for (name, game) in [
        ("Crystal Body", lullaby_on(CardId::C1051Jigglypuff, 0, durable_of(CardId::A2034Regice))),
        ("Clear Veil", lullaby_on(CardId::C1051Jigglypuff, 0, clear_veil)),
        ("Soothing Wind", soothing_wind),
    ] {
        let defender = game.get_state_clone().get_active(1).clone();
        assert_eq!(defender.taken(), 30, "{name}");
        assert!(!defender.is_asleep(), "{name}");
        assert_eq!((defender.sleep_checkup_coins(), raw_count(&defender)), (1, None), "{name}");
    }
}

/// L2 (divergence D1): a Pokémon already Asleep from an ordinary Sleep that Soothing Lullaby cannot affect keeps its 1
/// coin. Clear Veil ("Existing effects are not removed") and Crystal Body stop the attack's effect; Insomnia, Steel
/// Apron on a [M] Pokémon and Soothing Wind are immunities inside `try_apply_status_condition`. Upstream records 2 coins
/// whenever the Pokémon is Asleep after the attempt, so all five would flip 2 there.
#[test]
fn test_a_shielded_or_immune_sleeper_keeps_its_one_coin() {
    let asleep = |defender: PlayedCard| defender.with_status_condition(StatusCondition::Asleep);
    let on = |defender: PlayedCard| lullaby_on(CardId::C1051Jigglypuff, 0, asleep(defender));
    let cases = [
        ("Clear Veil", on(durable().with_tool(get_card_by_enum(CardId::B4149ClearVeil)))),
        ("Crystal Body", on(durable_of(CardId::A2034Regice))),
        ("Insomnia", on(durable_of(CardId::A4140Hoothoot))),
        (
            "Steel Apron on a [M] Pokémon",
            on(durable_of(CardId::A1181Meltan).with_tool(get_card_by_enum(CardId::A4153SteelApron))),
        ),
        ("Soothing Wind", lullaby_under_soothing_wind(asleep(durable()))),
    ];
    for (name, game) in cases {
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert!(defender.is_asleep(), "{name}");
        assert_eq!((defender.sleep_checkup_coins(), raw_count(defender)), (1, None), "{name}");
        assert_eq!(wake_chance(&state, &end_turn_action(0), 1), 0.5, "{name}");
    }
}

/// L3: Soothing Lullaby on a Pokémon already Asleep (unshielded) gives it 2 coins; a second Soothing Lullaby leaves 2.
#[test]
fn test_soothing_lullaby_on_a_sleeper_and_twice_gives_two_coins() {
    let game = lullaby_on(CardId::C1051Jigglypuff, 0, durable().with_status_condition(StatusCondition::Asleep));
    assert_eq!(raw_count(game.get_state_clone().get_active(1)), Some(2));
    let mut game = lullaby_game(CardId::C1184Jigglypuff, 0);
    attack(&mut game, CardId::C1184Jigglypuff, 0);
    let state = game.get_state_clone();
    assert_eq!(defender_damage(&game), 60);
    assert_eq!((state.get_active(1).sleep_checkup_coins(), raw_count(state.get_active(1))), (2, Some(2)));
}

/// Player 0's attack titled `title` from `attacker` hits player 1's Soothing Lullaby sleeper, and the same on a twin
/// whose Sleep was ordinary: both end states, the Lullaby one first.
fn on_a_lullaby_sleeper_and_its_twin(attacker: CardId, title: &str) -> [State; 2] {
    let sleeper = lullabied(durable());
    [sleeper.clone(), without_count(&sleeper)].map(|defender| {
        let mut game = board_at(0, 0, vec![ready_for(attacker, title)], vec![defender]);
        attack_titled(&mut game, attacker, title);
        game.get_state_clone()
    })
}

/// L4 (the reset reading, RulesUnverified): an ordinary Sleep that lands on a Soothing Lullaby sleeper resets it to 1
/// coin. Frosmoth's Powder Snow (A1 093, an attack's Sleep): the end state equals that of a twin that never had Soothing
/// Lullaby. Hypno's Sleep Pendulum (A1 125, an Ability's coin): heads resets it, tails leaves 2; both occur. Gothitelle's
/// Stellar Cradle (B1 114: "During your opponent's next turn, if they attach Energy from their Energy Zone to the
/// Defending Pokémon, that Pokémon will be Asleep."): its effect alone changes nothing, the Energy's Sleep resets it.
#[test]
fn test_an_ordinary_sleep_after_soothing_lullaby_resets_it_to_one_coin() {
    let [lullaby, twin] = on_a_lullaby_sleeper_and_its_twin(CardId::A1093Frosmoth, "Powder Snow");
    let defender = lullaby.get_active(1);
    assert!(defender.is_asleep());
    assert_eq!((defender.sleep_checkup_coins(), raw_count(defender)), (1, None));
    assert!(lullaby == twin, "Powder Snow: the state differs from the twin's");

    let (mut heads, mut tails) = (0, 0);
    for seed in 0..20 {
        let mut game = board_at(seed, 0, vec![PlayedCard::from_id(CardId::A1125Hypno)], vec![lullabied(durable())]);
        act(&mut game, 0, SimpleAction::UseAbility { in_play_idx: 0 });
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert!(defender.is_asleep(), "seed {seed}");
        match raw_count(defender) {
            None => {
                heads += 1;
                assert_eq!(defender.sleep_checkup_coins(), 1, "seed {seed}");
            }
            Some(2) => tails += 1,
            other => panic!("seed {seed}: {other:?}"),
        }
    }
    assert!(heads > 0 && tails > 0, "{heads} heads, {tails} tails");

    let mut game = board_at(0, 0, vec![ready_for(CardId::B1114Gothitelle, "Stellar Cradle")], vec![lullabied(durable())]);
    attack_titled(&mut game, CardId::B1114Gothitelle, "Stellar Cradle");
    assert_eq!(raw_count(game.get_state_clone().get_active(1)), Some(2));
    act(
        &mut game,
        1,
        SimpleAction::Attach {
            attachments: vec![(1, EnergyType::Psychic, 0)],
            is_turn_energy: true,
        },
    );
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert!(defender.is_asleep());
    assert_eq!((defender.sleep_checkup_coins(), raw_count(defender)), (1, None));
}

/// L5 and C2: Paralysis (Galvantula's Electric Shock, A3b 027) and Confusion (Kricketune's Entrancing Melody, A2 014)
/// replace a Soothing Lullaby Sleep, and the end state equals that of a twin that never had it. At the Pokémon itself
/// (`with_status_condition`, the raw setter), a Paralysis, a Confusion and an ordinary Sleep leave it equal to the twin
/// given the same; a Poison or a Burn keeps the 2 coins.
#[test]
fn test_paralysis_and_confusion_replace_a_soothing_lullaby_sleep() {
    for (attacker, title, condition) in [
        (CardId::A3b027Galvantula, "Electric Shock", StatusCondition::Paralyzed),
        (CardId::A2014Kricketune, "Entrancing Melody", StatusCondition::Confused),
    ] {
        let [lullaby, twin] = on_a_lullaby_sleeper_and_its_twin(attacker, title);
        let defender = lullaby.get_active(1);
        assert!(defender.has_status(condition) && !defender.is_asleep(), "{title}");
        assert_eq!(raw_count(defender), None, "{title}");
        assert!(lullaby == twin, "{title}: the state differs from the twin's");
    }

    let sleeper = lullabied(durable());
    use StatusCondition::*;
    for condition in [Paralyzed, Confused, Asleep] {
        let replaced = sleeper.clone().with_status_condition(condition);
        assert_eq!(raw_count(&replaced), None, "{condition:?}");
        assert!(replaced == without_count(&sleeper).with_status_condition(condition), "{condition:?}");
    }
    for condition in [Poisoned, Burned] {
        let kept = sleeper.clone().with_status_condition(condition);
        assert_eq!((kept.is_asleep(), kept.sleep_checkup_coins(), raw_count(&kept)), (true, 2, Some(2)), "{condition:?}");
    }
}

/// L6: a Poison or a Burn on a Soothing Lullaby sleeper keeps its 2 coins. With the Burn the Checkup has 8 branches of
/// 1/8; the Sleep coins come first and the Burn's after both, so the joint (awake, Burn cured) table is (yes, yes) 1,
/// (yes, no) 1, (no, yes) 3, (no, no) 3. A Burn coin read from the second Sleep coin would keep both marginals (1/4 and
/// 1/2) but give (yes, yes) 2 and (yes, no) 0. Each awake Pokémon has no count (C2: the Checkup wake).
#[test]
fn test_poison_or_burn_keeps_two_coins_and_the_burn_coin_comes_after_both() {
    let sleeper = lullabied(durable());
    let poisoned = sleeper.clone().with_status_condition(StatusCondition::Poisoned);
    let state = board_at(0, 0, vec![durable()], vec![poisoned]).get_state_clone();
    assert_eq!(probabilities(&state, &end_turn_action(0)), vec![0.25; 4]);

    let burned = sleeper.with_status_condition(StatusCondition::Burned);
    let state = board_at(0, 0, vec![durable()], vec![burned]).get_state_clone();
    let outcomes = branches(&state, &end_turn_action(0));
    assert_eq!(outcomes.iter().map(|(probability, _)| *probability).collect::<Vec<_>>(), vec![0.125; 8]);
    let mut table = BTreeMap::new();
    for (_, next) in &outcomes {
        let defender = next.get_active(1);
        if !defender.is_asleep() {
            assert_eq!(raw_count(defender), None);
        }
        *table.entry((!defender.is_asleep(), !defender.is_burned())).or_insert(0) += 1;
    }
    assert_eq!(
        table,
        BTreeMap::from([((false, false), 3), ((false, true), 3), ((true, false), 1), ((true, true), 1)])
    );
}

/// The Checkup ending `actor`'s turn: its probabilities, and how many branches leave each (player 0's Active awake,
/// player 1's Active awake) and each (Soothing Lullaby sleeper awake, Burn cured).
fn checkup_tables(
    state: &State,
    actor: usize,
    lullaby_player: usize,
) -> (Vec<f64>, BTreeMap<(bool, bool), usize>, BTreeMap<(bool, bool), usize>) {
    let outcomes = branches(state, &end_turn_action(actor));
    let (mut awake, mut burn) = (BTreeMap::new(), BTreeMap::new());
    for (_, next) in &outcomes {
        let up = |player: usize| !next.get_active(player).is_asleep();
        *awake.entry((up(0), up(1))).or_insert(0) += 1;
        let cured = !next.get_active(1 - lullaby_player).is_burned();
        *burn.entry((up(lullaby_player), cured)).or_insert(0) += 1;
    }
    (outcomes.into_iter().map(|(probability, _)| probability).collect(), awake, burn)
}

/// L7: one seat's Active carries Soothing Lullaby (2 coins), the other's an ordinary Sleep and a Burn (1 coin each):
/// 2^4 outcomes, wake chances 1/4 and 1/2, independent, and the Burn independent of both. The seat whose turn ends
/// flips first. When that is the ordinary sleeper (player 0's turn) the Lullaby coins are 1 and 2; when it is the
/// Lullaby sleeper (player 1's turn) the ordinary coin is 2, at the prefix sum, not at its index 1 among the sleepers.
#[test]
fn test_both_seats_sleep_coins_are_indexed_by_prefix_sums() {
    let ordinary = || durable().with_status_condition(StatusCondition::Asleep).with_status_condition(StatusCondition::Burned);
    let independent = BTreeMap::from([((false, false), 6), ((false, true), 2), ((true, false), 6), ((true, true), 2)]);
    let burn_apart = BTreeMap::from([((false, false), 6), ((false, true), 6), ((true, false), 2), ((true, true), 2)]);
    for actor in [0, 1] {
        let state = board_at(0, actor, vec![ordinary()], vec![lullabied(durable())]).get_state_clone();
        let (probabilities, awake, burn) = checkup_tables(&state, actor, 1);
        assert_eq!(probabilities, vec![1.0 / 16.0; 16], "player {actor}'s turn");
        assert_eq!(awake, independent, "player {actor}'s turn: (player 0 awake, player 1 awake)");
        assert_eq!(burn, burn_apart, "player {actor}'s turn: (Soothing Lullaby sleeper awake, Burn cured)");
        assert_eq!(wake_chance(&state, &end_turn_action(actor), 0), 0.5, "player {actor}'s turn");
        assert_eq!(wake_chance(&state, &end_turn_action(actor), 1), 0.25, "player {actor}'s turn");
    }
}

/// L8 and C2, the cures: each leaves player 1's Active awake with no count. Lum Berry (A2 149) at the end of player 0's
/// turn, in `on_end_turn` before the coins, so the Checkup flips none. On player 1's turn: Pokémon Center Lady (A2b
/// 070), Whitney (A4a 069) on Miltank (A4a 062), Steel Apron (A4 153) attached to a [M] Pokémon (Meltan, A1 181), and a
/// Zone Energy attached under Teal Mask Ogerpon ex's Soothing Wind (B2 017). (Full Heal is upstream's test above.)
#[test]
fn test_lum_berry_and_the_cures_end_a_soothing_lullaby_sleep() {
    let mut game = lullaby_on(CardId::C1051Jigglypuff, 0, durable().with_tool(get_card_by_enum(CardId::A2149LumBerry)));
    let state = game.get_state_clone();
    assert_eq!(raw_count(state.get_active(1)), Some(2));
    assert_eq!(probabilities(&state, &end_turn_action(0)), vec![1.0]);
    end_turn(&mut game, 0);
    let state = game.get_state_clone();
    assert!(!state.get_active(1).is_asleep() && state.get_active(1).attached_tools.is_empty());
    assert_eq!(raw_count(state.get_active(1)), None, "Lum Berry");

    let on_player_1s_turn = |theirs: Vec<PlayedCard>| board_at(0, 1, vec![durable()], theirs);
    let mut cured = Vec::new();
    let mut game = on_player_1s_turn(vec![lullabied(durable())]);
    play(&mut game, 1, CardId::A2b070PokemonCenterLady);
    choose(&mut game, |action| matches!(action, SimpleAction::Heal { in_play_idx: 0, .. }));
    cured.push(("Pokémon Center Lady", game.get_state_clone()));
    let mut game = on_player_1s_turn(vec![lullabied(durable_of(CardId::A4a062Miltank))]);
    play(&mut game, 1, CardId::A4a069Whitney);
    choose(&mut game, |action| matches!(action, SimpleAction::HealAndCureConditions { in_play_idx: 0, .. }));
    cured.push(("Whitney", game.get_state_clone()));
    let mut game = on_player_1s_turn(vec![lullabied(durable_of(CardId::A1181Meltan))]);
    let tool_card = get_card_by_enum(CardId::A4153SteelApron);
    act(&mut game, 1, SimpleAction::AttachTool { in_play_idx: 0, tool_card });
    cured.push(("Steel Apron", game.get_state_clone()));
    let mut game = on_player_1s_turn(vec![lullabied(durable()), PlayedCard::from_id(CardId::B2017TealMaskOgerponEx)]);
    let attachments = vec![(1, EnergyType::Grass, 0)];
    act(&mut game, 1, SimpleAction::Attach { attachments, is_turn_energy: true });
    cured.push(("Soothing Wind", game.get_state_clone()));
    for (name, state) in cured {
        let defender = state.get_active(1);
        assert!(!defender.is_asleep(), "{name}");
        assert_eq!(raw_count(defender), None, "{name}");
    }
}

/// L8 and C2: a random Special Condition removed from a Soothing Lullaby sleeper that is also Poisoned, by Big
/// Malasada (A3 142) and by Blissey's Happiness Supplement (B3 128, from the Bench). When the Sleep is removed the
/// count goes with it; when the Poison is, the 2 coins stay. Both happen over 20 seeds.
#[test]
fn test_a_random_cure_ends_the_count_only_with_the_sleep() {
    for source in ["Big Malasada", "Happiness Supplement"] {
        let (mut sleep_removed, mut poison_removed) = (0, 0);
        for seed in 0..20 {
            let sleeper = lullabied(durable()).with_status_condition(StatusCondition::Poisoned);
            let game = if source == "Big Malasada" {
                let mut game = board_at(seed, 1, vec![durable()], vec![sleeper]);
                play(&mut game, 1, CardId::A3142BigMalasada);
                game
            } else {
                let mut game = board_at(seed, 1, vec![durable()], vec![sleeper, PlayedCard::from_id(CardId::B3128Blissey)]);
                act(&mut game, 1, SimpleAction::UseAbility { in_play_idx: 1 });
                game
            };
            let state = game.get_state_clone();
            let defender = state.get_active(1);
            if defender.is_asleep() {
                poison_removed += 1;
                assert!(!defender.is_poisoned(), "{source} seed {seed}");
                assert_eq!(raw_count(defender), Some(2), "{source} seed {seed}");
            } else {
                sleep_removed += 1;
                assert!(defender.is_poisoned(), "{source} seed {seed}");
                assert_eq!(raw_count(defender), None, "{source} seed {seed}");
            }
        }
        assert!(sleep_removed > 0 && poison_removed > 0, "{source}: {sleep_removed} and {poison_removed}");
    }
}

/// L9 and C2: switching out, evolving and devolving end it. Sabrina (A1 225, "Your opponent chooses the new Active
/// Pokémon") sends player 1's sleeper to the Bench through `apply_activate`, and a switch back by the frame a switch
/// card leaves (`Activate`) then an ordinary Sleep flips 1 coin. Player 1's Bulbasaur evolves into Ivysaur (a fresh
/// card). Celebi's Temporal Leaves (A4a 006) devolves player 1's Ivysaur into Bulbasaur (a fresh card).
#[test]
fn test_switching_evolving_and_devolving_end_a_soothing_lullaby_sleep() {
    let mut game = board_at(0, 0, vec![durable()], vec![lullabied(durable()), PlayedCard::from_id(CardId::A1033Charmander)]);
    play(&mut game, 0, CardId::A1225Sabrina);
    choose(&mut game, |action| matches!(action, SimpleAction::Activate { player: 1, in_play_idx: 1 }));
    let state = game.get_state_clone();
    let benched = state.in_play_pokemon[1][1].as_ref().unwrap();
    assert_eq!(benched.get_name(), "Snorlax");
    assert!(!benched.is_asleep());
    assert_eq!(raw_count(benched), None, "Sabrina");
    act(&mut game, 1, SimpleAction::Activate { player: 1, in_play_idx: 1 });
    let mut state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Snorlax");
    state.apply_status_condition(1, 0, StatusCondition::Asleep);
    assert_eq!((state.get_active(1).sleep_checkup_coins(), raw_count(state.get_active(1))), (1, None));

    let mut game = board_at(0, 1, vec![durable()], vec![lullabied(durable_of(CardId::A1001Bulbasaur))]);
    let ivysaur = get_card_by_enum(CardId::A1002Ivysaur);
    let mut state = game.get_state_clone();
    state.hands[1] = vec![ivysaur.clone()];
    game.set_state(state);
    act(&mut game, 1, SimpleAction::Evolve { evolution: ivysaur, in_play_idx: 0, from_deck: false });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Ivysaur");
    assert!(!state.get_active(1).is_asleep());
    assert_eq!(raw_count(state.get_active(1)), None, "evolution");

    let evolved = PlayedCard::new(
        get_card_by_enum(CardId::A1002Ivysaur),
        0,
        1000,
        vec![],
        false,
        vec![get_card_by_enum(CardId::A1001Bulbasaur)],
    );
    let sleeper = lullabied(evolved).with_remaining_hp(u32::MAX);
    let mut game = board_at(0, 0, vec![ready_for(CardId::A4a006Celebi, "Temporal Leaves")], vec![sleeper]);
    attack_titled(&mut game, CardId::A4a006Celebi, "Temporal Leaves");
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Bulbasaur");
    assert!(!state.get_active(1).is_asleep());
    assert_eq!(raw_count(state.get_active(1)), None, "devolution");
}

/// C2: a Knock Out takes the count out of play. Player 1's Bulbasaur, Asleep from Soothing Lullaby and Poisoned at 10
/// HP, is Knocked Out by the Poison in the Checkup. Its 2 coins are still flipped (4 branches: the coins come before the
/// Knock Out wave, as pin board 15), then player 1 promotes Charmander, and nothing in play holds a count.
#[test]
fn test_a_knock_out_takes_the_count_out_of_play() {
    let sleeper = lullabied(PlayedCard::from_id(CardId::A1001Bulbasaur))
        .with_status_condition(StatusCondition::Poisoned)
        .with_remaining_hp(10);
    let mut game = board_at(0, 0, vec![durable()], vec![sleeper, PlayedCard::from_id(CardId::A1033Charmander)]);
    assert_eq!(probabilities(&game.get_state_clone(), &end_turn_action(0)), vec![0.25; 4]);
    end_turn(&mut game, 0);
    choose(&mut game, |action| matches!(action, SimpleAction::Promote { player: 1, .. }));
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Charmander");
    assert_eq!(state.points, [1, 0]);
    for pokemon in state.in_play_pokemon.iter().flatten().flatten() {
        assert_eq!(raw_count(pokemon), None, "{}", pokemon.get_name());
    }
}

/// L11: Darkrai's Bad Dreams (B2b 040: "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20
/// damage to that Pokémon.") Knocks Out player 1's Soothing Lullaby sleeper (20 HP left) in `on_end_turn`, before the
/// coins: the Checkup flips none for it, so `EndTurn` has 1 branch (sized from the state after `on_end_turn`, not 4).
#[test]
fn test_bad_dreams_knocks_out_a_soothing_lullaby_sleeper_before_its_coins() {
    let id = CardId::C1051Jigglypuff;
    let mut game = board_at(
        0,
        0,
        vec![ready(id, 0), PlayedCard::from_id(CardId::B2b040Darkrai)],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(50), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert_eq!((state.get_active(1).get_remaining_hp(), raw_count(state.get_active(1))), (20, Some(2)));
    assert_eq!(probabilities(&state, &end_turn_action(0)), vec![1.0]);
    end_turn(&mut game, 0);
    let state = game.get_state_clone();
    assert!(state.in_play_pokemon[1][0].is_none());
    assert_eq!(state.points, [1, 0]);
}

/// L12: the deferred Checkup frame. Player 0's Active carries Soothing Lullaby; player 1's Caterpie (B3b 001) evolves at
/// the end of player 0's turn (a Metapod on top of its deck), so `EndTurn` has 1 branch and leaves
/// `ResolveEndTurnEvolution` above `ResolvePokemonCheckup`, which is forecast on the live state: 2 coins, 4 branches,
/// awake in 1/4.
#[test]
fn test_the_deferred_checkup_flips_two_coins_for_a_soothing_lullaby_sleeper() {
    let mut game = board_at(0, 0, vec![lullabied(durable())], vec![PlayedCard::from_id(CardId::B3b001Caterpie)]);
    let mut state = game.get_state_clone();
    state.decks[1].cards = vec![get_card_by_enum(CardId::B3b002Metapod)];
    game.set_state(state.clone());
    assert_eq!(probabilities(&state, &end_turn_action(0)), vec![1.0]);
    end_turn(&mut game, 0);
    choose(&mut game, |action| matches!(action, SimpleAction::ResolveEndTurnEvolution { .. }));
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_name(), "Metapod");
    let (_, actions) = state.generate_possible_actions();
    let checkup = actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::ResolvePokemonCheckup))
        .expect("the deferred Checkup is offered");
    assert_eq!(probabilities(&state, &checkup), vec![0.25; 4]);
    assert_eq!(wake_chance(&state, &checkup, 0), 0.25);
}

/// L13: both printings are "Implemented with unverified rule boundaries", with exactly the one limitation line (the reset
/// reading).
#[test]
fn test_jigglypuff_printings_report_rules_unverified_with_the_reset_reading() {
    for id in JIGGLYPUFF {
        assert_eq!(get_implementation_status(id), ImplementationStatus::RulesUnverified, "{id:?}");
        assert_eq!(
            implementation_limitations(id),
            &["Unverified Pokémon TCG Pocket boundary (not filmed): an ordinary Sleep that lands on a Pokémon already Asleep from Soothing Lullaby replaces it, so that Pokémon flips 1 coin at Pokémon Checkup instead of 2 (the reset reading, as upstream). Card text, not filmed: a Soothing Lullaby Sleep flips 2 coins at Pokémon Checkup and wakes only if both are heads."],
            "{id:?}"
        );
    }
}

/// L14: Mew ex (A1a 032) copies an opposing Jigglypuff's Soothing Lullaby with Genome Hacking ("Choose 1 of your
/// opponent's Active Pokémon's attacks and use it as this attack."): that Jigglypuff, the copier's opponent's Active,
/// takes the 30 and is Asleep with 2 coins.
#[test]
fn test_soothing_lullaby_copied_by_mew_ex_puts_the_jigglypuff_to_sleep_with_two_coins() {
    let mew = CardId::A1a032MewEx;
    let mut game = board_at(
        0,
        0,
        vec![PlayedCard::from_id(mew).with_energy(vec![EnergyType::Psychic; 3])],
        vec![durable_of(CardId::C1051Jigglypuff).with_energy(vec![EnergyType::Psychic; 2])],
    );
    attack_titled(&mut game, mew, "Genome Hacking");
    choose(&mut game, |action| matches!(action, SimpleAction::Attack(copied) if copied.title == "Soothing Lullaby"));
    let state = game.get_state_clone();
    assert_eq!(defender_damage(&game), 30);
    assert!(state.get_active(1).is_asleep());
    assert_eq!((state.get_active(1).sleep_checkup_coins(), raw_count(state.get_active(1))), (2, Some(2)));
}

/// Whether Will (A4 156) is still pending (`TurnEffect::ForceFirstHeads`).
fn has_will(state: &State) -> bool {
    serde_json::to_string(state).unwrap().contains("ForceFirstHeads")
}

/// L15: Will, then Soothing Lullaby. The attack flips no coin, so Will is still pending after it; and Will never reaches
/// the Checkup, so the wake chance there is still 1/4 in 4 equal branches.
#[test]
fn test_will_is_not_spent_on_soothing_lullaby_or_its_checkup() {
    let id = CardId::C1051Jigglypuff;
    let mut game = board_at(0, 0, vec![ready(id, 0)], vec![durable()]);
    play(&mut game, 0, CardId::A4156Will);
    assert!(has_will(&game.get_state_clone()));
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert!(has_will(&state), "Will is still pending after Soothing Lullaby");
    assert_eq!(raw_count(state.get_active(1)), Some(2));
    assert_eq!(probabilities(&state, &end_turn_action(0)), vec![0.25; 4]);
    assert_eq!(wake_chance(&state, &end_turn_action(0), 1), 0.25);
}

fn fnv(text: &str) -> u64 {
    let mut hash = 0xcbf2_9ce4_8422_2325_u64;
    for byte in text.bytes() {
        hash ^= u64::from(byte);
        hash = hash.wrapping_mul(0x0000_0100_0000_01b3);
    }
    hash
}

/// The committed fixtures: saved `ExportedDataPoint` rows, written before Soothing Lullaby existed.
const FIXTURES: [(&str, &str); 6] = [
    ("boiler_smog_ply23", include_str!("../fixtures/boiler_smog_ply23.json")),
    ("public_reply_observed", include_str!("../fixtures/public_reply_observed.json")),
    ("rocket-frenzy-root-612004-25", include_str!("../fixtures/rocket-frenzy-root-612004-25.json")),
    ("rocket-frenzy-root-612005-36", include_str!("../fixtures/rocket-frenzy-root-612005-36.json")),
    ("status_castform_asleep_ply_0059", include_str!("../fixtures/status_castform_asleep_ply_0059.json")),
    ("status_heatmor_asleep_ply_0037", include_str!("../fixtures/status_heatmor_asleep_ply_0037.json")),
];

/// Every State in the committed fixtures: each row's, and the opponent's turn that public_reply_observed.json carries
/// beside its row. Each with its row re-serialized (the `ExportedDataPoint` itself) when it has one.
fn fixture_states() -> Vec<(String, Option<String>, State)> {
    let mut states = Vec::new();
    for (name, source) in FIXTURES {
        let fixture: serde_json::Value = serde_json::from_str(source).unwrap();
        let row = fixture.get("row").cloned().unwrap_or_else(|| fixture.clone());
        let point: ExportedDataPoint = serde_json::from_value(row).unwrap();
        let row_json = serde_json::to_string(&point).unwrap();
        states.push((name.to_string(), Some(row_json), point.state));
        if let Some(opponent_turn) = fixture.get("opponent_turn_state") {
            let state: State = serde_json::from_value(opponent_turn.clone()).unwrap();
            states.push((format!("{name} opponent_turn_state"), None, state));
        }
    }
    states
}

/// Also Poisoned for 20 at Checkup, as Toxicroak's Toxic (A2a 052) leaves it (built as checkup_coin_trace_test.rs
/// builds one).
fn toxic(card: PlayedCard) -> PlayedCard {
    let mut encoded = serde_json::to_value(card.with_status_condition(StatusCondition::Poisoned)).unwrap();
    encoded["poison_checkup_damage"] = serde_json::json!(20);
    serde_json::from_value(encoded).unwrap()
}

/// Mid-game boards with no Soothing Lullaby, from player 0's turn 3 at seed 0: Special Conditions set directly, a Sleep
/// from Frosmoth's Powder Snow (A1 093, through the attack-effect chokepoint) and the Checkup after it.
fn lullaby_free_boards() -> Vec<(String, State)> {
    use StatusCondition::*;
    let with = |id: CardId, conditions: &[StatusCondition]| {
        conditions.iter().fold(PlayedCard::from_id(id), |card, &condition| card.with_status_condition(condition))
    };
    let mut boards = Vec::new();
    let sleepers = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![with(CardId::A1053Squirtle, &[Asleep, Burned]), PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![toxic(with(CardId::A1001Bulbasaur, &[Asleep])), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    boards.push(("sleepers, a Burn and a Toxic".to_string(), sleepers.get_state_clone()));
    let replaced = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![with(CardId::A1053Squirtle, &[Asleep, Paralyzed])],
        vec![with(CardId::A1001Bulbasaur, &[Asleep, Confused])],
    );
    boards.push(("Paralysis and Confusion over Sleep".to_string(), replaced.get_state_clone()));
    let mut powder_snow = get_initialized_game_with_board(
        0,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A1093Frosmoth).with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::A1033Charmander)],
    );
    powder_snow.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1093Frosmoth, 0),
        is_stack: false,
    });
    assert!(powder_snow.get_state_clone().get_active(1).is_asleep());
    boards.push(("after Powder Snow".to_string(), powder_snow.get_state_clone()));
    powder_snow.apply_action(&Action {
        actor: 0,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    boards.push(("after Powder Snow's Checkup".to_string(), powder_snow.get_state_clone()));
    boards
}

/// One line of the bytes record: what was serialized, its length and its FNV-1a. No serialization of a state without
/// Soothing Lullaby holds the new key.
fn bytes_line(what: String, json: &str) -> (String, usize, String) {
    assert!(!json.contains("sleep_coins_override"), "{what}: the key without a Soothing Lullaby");
    (what, json.len(), format!("{:016x}", fnv(json)))
}

fn bytes_record() -> Vec<(String, usize, String)> {
    let mut record = Vec::new();
    let boards = lullaby_free_boards().into_iter().map(|(what, state)| (what, None, state));
    for (what, row, state) in fixture_states().into_iter().chain(boards) {
        if let Some(row) = row {
            record.push(bytes_line(format!("{what}: row"), &row));
        }
        record.push(bytes_line(format!("{what}: state"), &serde_json::to_string(&state).unwrap()));
        for seat in 0..2 {
            let observation = PlayerObservation::from_state(&state, seat, &RevealedKnowledge::default());
            record.push(bytes_line(
                format!("{what}: seat {seat} observation"),
                &serde_json::to_string(&observation).unwrap(),
            ));
        }
    }
    record
}

/// (what, bytes, FNV-1a) of every serialization in `bytes_record`, recorded at 45e87ed2, before Soothing Lullaby.
const BYTES_BEFORE: [(&str, usize, &str); 39] = [
    ("boiler_smog_ply23: row", 19308, "93e8c811db1b1af7"),
    ("boiler_smog_ply23: state", 18043, "212e3d5e7267710b"),
    ("boiler_smog_ply23: seat 0 observation", 14647, "2097f0529d8626fa"),
    ("boiler_smog_ply23: seat 1 observation", 13634, "3d15f66d4cded8f0"),
    ("public_reply_observed: row", 18275, "a5c2a085c9d0b700"),
    ("public_reply_observed: state", 14887, "025f538b45ad9ce7"),
    ("public_reply_observed: seat 0 observation", 12478, "53230b0668119ae3"),
    ("public_reply_observed: seat 1 observation", 12741, "51590764de38d2ab"),
    ("public_reply_observed opponent_turn_state: state", 10907, "ddb3a5537c9cfd29"),
    ("public_reply_observed opponent_turn_state: seat 0 observation", 11054, "fe36d75f3149d344"),
    ("public_reply_observed opponent_turn_state: seat 1 observation", 10162, "d7f3922264d111a4"),
    ("rocket-frenzy-root-612004-25: row", 24929, "1f744f3d8102419b"),
    ("rocket-frenzy-root-612004-25: state", 19592, "f2beee8c98402d00"),
    ("rocket-frenzy-root-612004-25: seat 0 observation", 14837, "c80af2d5fe30eac2"),
    ("rocket-frenzy-root-612004-25: seat 1 observation", 14674, "87ca76e527899bb9"),
    ("rocket-frenzy-root-612005-36: row", 26515, "e7702c92205f11e9"),
    ("rocket-frenzy-root-612005-36: state", 19658, "a2ef89939e1608e8"),
    ("rocket-frenzy-root-612005-36: seat 0 observation", 15170, "332b2a61edd29b34"),
    ("rocket-frenzy-root-612005-36: seat 1 observation", 14984, "86ea9e9bdbcfe6de"),
    ("status_castform_asleep_ply_0059: row", 27015, "51aadd382165dcad"),
    ("status_castform_asleep_ply_0059: state", 17364, "f9c6cec93d66fa0a"),
    ("status_castform_asleep_ply_0059: seat 0 observation", 15068, "ffd3388aea80183d"),
    ("status_castform_asleep_ply_0059: seat 1 observation", 15457, "bfc8c65ad6383e07"),
    ("status_heatmor_asleep_ply_0037: row", 22098, "cb4bb128ec7db04d"),
    ("status_heatmor_asleep_ply_0037: state", 17317, "c47c258a8b89679a"),
    ("status_heatmor_asleep_ply_0037: seat 0 observation", 14334, "f1e87273d758744c"),
    ("status_heatmor_asleep_ply_0037: seat 1 observation", 13936, "581b9277d907a835"),
    ("sleepers, a Burn and a Toxic: state", 15021, "e4251e105e27c36e"),
    ("sleepers, a Burn and a Toxic: seat 0 observation", 10214, "600ea1ac8dc3c7c6"),
    ("sleepers, a Burn and a Toxic: seat 1 observation", 9890, "4b0b35039f24a214"),
    ("Paralysis and Confusion over Sleep: state", 13327, "12c64667a3f37a17"),
    ("Paralysis and Confusion over Sleep: seat 0 observation", 8520, "b837b52d3bde436d"),
    ("Paralysis and Confusion over Sleep: seat 1 observation", 8196, "ba421c7bf503522f"),
    ("after Powder Snow: state", 14285, "7e6143ad242b2492"),
    ("after Powder Snow: seat 0 observation", 9478, "33b4fdc9fa0d31dc"),
    ("after Powder Snow: seat 1 observation", 9154, "8ff1eabc55ac59f2"),
    ("after Powder Snow's Checkup: state", 14323, "4df221ce04515261"),
    ("after Powder Snow's Checkup: seat 0 observation", 9491, "4cee3243130d497e"),
    ("after Powder Snow's Checkup: seat 1 observation", 9192, "39feb746a209b6db"),
];

/// C1 (coordinator-129): saved rows, States and observations without a Soothing Lullaby keep their bytes. Pinned at
/// 45e87ed2 (the constants above), asserted after. With LULLABY_BYTES_OUT set the record is also written there.
#[test]
fn test_states_and_observations_without_a_lullaby_keep_their_bytes() {
    let record = bytes_record();
    if let Ok(path) = std::env::var("LULLABY_BYTES_OUT") {
        let text: String = record
            .iter()
            .map(|(what, bytes, hash)| format!("    ({what:?}, {bytes}, {hash:?}),\n"))
            .collect();
        std::fs::write(path, text).unwrap();
    }
    let before: Vec<(String, usize, String)> = BYTES_BEFORE
        .iter()
        .map(|(what, bytes, hash)| (what.to_string(), *bytes, hash.to_string()))
        .collect();
    assert_eq!(record, before);
}

/// L10 and C1: a Soothing Lullaby count serializes once, as 2, and the State round-trips. JSON without the key (every
/// committed fixture, two of them with an Asleep Active, and a Lullaby sleeper with its key removed) loads with no
/// count and 1 coin. A hand-edited 0, 5 or 1000 reads as 1 coin, with a 2-branch Checkup and no panic; 1 and 4 (the
/// most one Sleep may ask for) read as themselves. A hand-edited 4 on a Benched sleeper (only an Active can be Asleep
/// in play) flips the usual 1 coin. Both seats' observations carry the count and parse back through the observation
/// wire (`deny_unknown_fields`) as the protocol bot reads `pdl_observation` (protocol/bot.rs), to the same observation
/// and bytes; an `EndTurn` forecast from either seat's `search_state` wakes the sleeper 1 time in 4. The information
/// model is still v8.
#[test]
fn test_a_lullaby_count_round_trips_and_old_or_forged_json_reads_as_one_coin() {
    let game = lullaby_game(CardId::C1051Jigglypuff, 0);
    let state = game.get_state_clone();
    let json = serde_json::to_string(&state).unwrap();
    assert_eq!(json.matches("sleep_coins_override").count(), 1);
    assert_eq!(json.matches("\"sleep_coins_override\":2").count(), 1);
    let loaded: State = serde_json::from_str(&json).unwrap();
    assert!(loaded == state);
    assert_eq!(serde_json::to_string(&loaded).unwrap(), json);

    let old = without_count(state.get_active(1));
    assert_eq!((old.is_asleep(), old.sleep_checkup_coins(), raw_count(&old)), (true, 1, None));
    let mut asleep = 0;
    for (name, _, fixture) in fixture_states() {
        for pokemon in fixture.in_play_pokemon.iter().flatten().flatten() {
            assert_eq!((pokemon.sleep_checkup_coins(), raw_count(pokemon)), (1, None), "{name}");
            asleep += usize::from(pokemon.is_asleep());
        }
    }
    assert!(asleep >= 2, "the Castform and Heatmor fixtures each hold an Asleep Active");

    // Each forged count is read, and checked, before its Checkup is forecast.
    for (count, coins) in [(0, 1), (5, 1), (1000, 1), (1, 1), (4, 4)] {
        let sleeper = forged(state.get_active(1), count);
        assert_eq!(sleeper.sleep_checkup_coins(), coins, "forged {count}");
        let board = board_at(0, 0, vec![durable()], vec![sleeper]).get_state_clone();
        let outcomes = 1usize << coins;
        assert_eq!(
            probabilities(&board, &end_turn_action(0)),
            vec![1.0 / outcomes as f64; outcomes],
            "forged {count}"
        );
    }
    let benched = forged(state.get_active(1), 4);
    let board = board_at(0, 0, vec![durable()], vec![durable(), benched]).get_state_clone();
    assert_eq!(board.in_play_pokemon[1][1].as_ref().unwrap().sleep_checkup_coins(), 4);
    assert_eq!(probabilities(&board, &end_turn_action(0)), vec![0.5; 2], "a forged Benched count");

    for seat in 0..2 {
        let observation = game.observation(seat);
        let json = serde_json::to_string(&observation).unwrap();
        assert_eq!(json.matches("\"sleep_coins_override\":2").count(), 1, "seat {seat}");
        let wire: serde_json::Value = serde_json::from_str(&json).unwrap();
        let parsed: PlayerObservation = serde_json::from_value(wire).unwrap();
        assert!(parsed == observation, "seat {seat}: the wire keeps the count");
        assert_eq!(serde_json::to_string(&parsed).unwrap(), json, "seat {seat}");
        let search = observation.search_state(&mut StdRng::seed_from_u64(2));
        assert_eq!(search.get_active(1).sleep_checkup_coins(), 2, "seat {seat}");
        assert_eq!(wake_chance(&search, &end_turn_action(0), 1), 0.25, "seat {seat}");
    }
    assert_eq!(INFORMATION_MODEL, "closed-counts-unpriced-v8");
}
