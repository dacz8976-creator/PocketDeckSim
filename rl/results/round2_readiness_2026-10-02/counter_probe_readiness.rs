//! Round-2 readiness, job 2 (the cloud, Oct 2; scratch): the round-2 package's counters on constructed boards. It runs the
//! counters' own lines (`r2_counter_fns.rs`, written out by `../coin_prevention_repair_2026-09-30/instrument_scan.py
//! --emit-fns`, the same text the script puts into legality_scan.rs) on boards built with `test_support`, and checks the exact
//! set of counters that fire at each tick: for every counter, a board where it must fire and a matching board where it must not.
//! Like F5's probe and `../coin_prevention_round2_2026-10-01/counter_probe_round2.rs`, whose site boards it reuses. It plays no
//! game and needs the `test-utils` feature. Built in a scratch copy of claude/coin-prevention-round2's engine:
//!   python3 instrument_scan.py --emit-fns engine/examples/r2_counter_fns.rs
//!   cp counter_probe_readiness.rs engine/examples/
//!   (cd engine && cargo run --release --locked --features test-utils --example counter_probe_readiness)
use deckgym::actions::{Action, SimpleAction};
use deckgym::card_ids::CardId;
use deckgym::database::get_card_by_enum;
use deckgym::effects::CardEffect;
use deckgym::models::{Attack, Card, EnergyType, PlayedCard, StatusCondition, TrainerType};
use deckgym::test_support::{attack_action, get_initialized_game, get_initialized_game_with_board, get_test_game_with_board};
use deckgym::{Game, State};
use std::collections::BTreeSet;

include!("r2_counter_fns.rs");

/// The counters that fire at the tick `state` when `chosen` is played: "name", or "name[key]" for a keyed one.
fn fired(state: &State, chosen: &Action, last: Option<&Attack>) -> BTreeSet<String> {
    let (_, actions) = state.generate_possible_actions();
    r2_tick(state, &actions, chosen, last)
        .into_iter()
        .map(|(name, key)| key.map_or(name.to_string(), |k| format!("{name}[{k}]")))
        .collect()
}

fn set(names: &[&str]) -> BTreeSet<String> {
    names.iter().map(|n| n.to_string()).collect()
}

fn attack_named(state: &State, title: &str) -> Action {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .find(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == title))
        .unwrap_or_else(|| panic!("{title} is not offered"))
}

fn offered(state: &State, pick: impl Fn(&SimpleAction) -> bool) -> Option<Action> {
    state.generate_possible_actions().1.into_iter().find(|a| pick(&a.action))
}

/// Player 1 uses `title` from `attacker` into `defenders` (with `hand` as its hand), choosing the copied attack `copy` when
/// one is offered and the largest discard whenever one is offered, until a frame of damage choices is offered to it with no
/// discard beside it; seeds are tried until one offers it (Wellspring Dance's heads). Returns that state and the last attack
/// player 1 chose (the copied one, for a copy). As `counter_probe_round2.rs`'s `damage_frame`, with the copy, and the discard
/// taken before the damage choices when a frame offers both (Chase Order's).
fn damage_frame(
    attacker: &[PlayedCard],
    defenders: &[PlayedCard],
    hand: &[CardId],
    title: &str,
    copy: Option<&str>,
) -> (State, Attack) {
    for seed in 0..40u64 {
        let mut game = get_initialized_game_with_board(seed, 1, 5, defenders.to_vec(), attacker.to_vec());
        let mut state = game.get_state_clone();
        state.current_player = 1;
        state.hands[1] = hand.iter().map(|id| get_card_by_enum(*id)).collect();
        game.set_state(state.clone());
        let attack = attack_named(&state, title);
        let SimpleAction::Attack(mut last) = attack.action.clone() else { unreachable!() };
        game.apply_action(&attack);
        for _ in 0..5 {
            let state = game.get_state_clone();
            let (actor, choices) = state.generate_possible_actions();
            if actor != 1 || state.move_generation_stack.is_empty() {
                break;
            }
            if let Some(copied) = choices.iter().find(|a| matches!(&a.action, SimpleAction::Attack(x) if Some(x.title.as_str()) == copy)) {
                let SimpleAction::Attack(x) = &copied.action else { unreachable!() };
                last = x.clone();
                game.apply_action(&copied.clone());
                continue;
            }
            let size = |a: &&Action| match &a.action {
                SimpleAction::DiscardOwnBenchedThenDamage { in_play_idxs, .. } => in_play_idxs.len(),
                SimpleAction::DiscardOwnCardsForAttackDamage { cards, .. } => cards.len(),
                _ => 0,
            };
            if let Some(discard) = choices.iter().filter(|a| size(a) > 0).max_by_key(size) {
                game.apply_action(&discard.clone());
                continue;
            }
            if choices.iter().any(|a| matches!(a.action, SimpleAction::ApplyDamage { .. } | SimpleAction::ApplyQueuedAttackDamage { .. })) {
                return (state, last);
            }
            game.apply_action(&choices[0].clone());
        }
    }
    panic!("{title}: no damage choices offered in 40 seeds");
}

struct Report {
    lines: Vec<String>,
    failures: usize,
}

impl Report {
    fn check(&mut self, label: &str, got: BTreeSet<String>, want: BTreeSet<String>) {
        let ok = got == want;
        self.failures += !ok as usize;
        self.lines.push(format!(
            "{} {label}: {got:?}{}",
            if ok { "ok  " } else { "FAIL" },
            if ok { String::new() } else { format!(" (wanted {want:?})") }
        ));
    }
}

fn mon(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id)
}

fn with(id: CardId, energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(energy)
}

/// A Pokemon with `hp` HP and no damage (a card that survives what the board throws at it).
fn sturdy(id: CardId, hp: u32) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(id), 0, hp, vec![], false, vec![])
}

/// Player 0 plays Will (A4 156) from its hand.
fn play_will(game: &mut Game) {
    let will = get_card_by_enum(CardId::A4156Will);
    let Card::Trainer(trainer_card) = will.clone() else { unreachable!() };
    let mut state = game.get_state_clone();
    state.hands[0].push(will);
    game.set_state(state);
    game.apply_action(&Action { actor: 0, action: SimpleAction::Play { trainer_card }, is_stack: false });
}

/// Team Rocket's Moltres ex (Heat Charged: flip 3 coins) for player 0 against a 400-HP Mega Latios ex, with the gates asked.
fn moltres_game(seed: u64, confused: bool, block: bool, will: bool, victini: bool) -> Game<'static> {
    let mut attacker = with(CardId::B4a007TeamRocketsMoltresEx, vec![EnergyType::Fire]);
    if confused {
        attacker = attacker.with_status_condition(StatusCondition::Confused);
    }
    if block {
        attacker.add_effect(CardEffect::CoinFlipToBlockAttack, 1);
    }
    let bench = mon(if victini { CardId::B3025Victini } else { CardId::A1001Bulbasaur });
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![attacker, bench], vec![sturdy(CardId::PB024MegaLatiosEx, 400)]);
    if will {
        play_will(&mut game);
    }
    game
}

fn moltres_board(seed: u64, confused: bool, block: bool, will: bool, victini: bool) -> State {
    moltres_game(seed, confused, block, will, victini).get_state_clone()
}

fn main() {
    let (meowth, bulbasaur) = (CardId::B2124Meowth, CardId::A1001Bulbasaur);
    let mut r = Report { lines: vec![], failures: 0 };

    // 1. The later coin round's sites (the boards of counter_probe_round2.rs). With the coin Pokemon there, the queued choice is
    //    offered (coin_queued_by_attack, keyed by the attack); without it, only plain choices (offgate_by_attack, and the plain
    //    damage's off-gate when one is chosen).
    let sites: Vec<(&str, Vec<PlayedCard>, Vec<CardId>, Vec<PlayedCard>, Vec<PlayedCard>, bool)> = vec![
        ("Wild Swing", vec![with(CardId::A4045Gyarados, vec![EnergyType::Water; 2]), mon(CardId::A1053Squirtle)], vec![],
            vec![mon(meowth)], vec![mon(bulbasaur)], false),
        ("Wellspring Dance", vec![with(CardId::B2048WellspringMaskOgerpon, vec![EnergyType::Water; 2])], vec![],
            vec![mon(bulbasaur), mon(meowth)], vec![mon(bulbasaur), mon(bulbasaur)], false),
        ("Tornado Shot", vec![with(CardId::B3051RapidStrikeUrshifu, vec![EnergyType::Water; 2])], vec![],
            vec![mon(bulbasaur), mon(meowth)], vec![mon(bulbasaur), mon(bulbasaur)], false),
        ("Double Splash", vec![with(CardId::B1a019Blastoise, vec![EnergyType::Water; 5])], vec![],
            vec![mon(bulbasaur), mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur), mon(bulbasaur)], true),
        ("Triple Bombardment", vec![with(CardId::B1a020MegaBlastoiseEx, vec![EnergyType::Water; 6])], vec![],
            vec![mon(bulbasaur), mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur), mon(bulbasaur)], false),
        ("Mischievous Ring", vec![with(CardId::B4077Hoopa, vec![EnergyType::Psychic])], vec![],
            vec![mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur)], false),
        ("Litter", vec![with(CardId::A4a018Slowking, vec![EnergyType::Water])], vec![CardId::A2147GiantCape, CardId::A2148RockyHelmet],
            vec![mon(meowth), mon(bulbasaur)], vec![mon(bulbasaur), mon(bulbasaur)], false),
        ("Double-Punching Family", vec![with(CardId::B2127MegaKangaskhanEx, vec![EnergyType::Colorless; 3])], vec![],
            vec![mon(CardId::A4080Togekiss), mon(bulbasaur)], vec![mon(CardId::PB024MegaLatiosEx), mon(bulbasaur)], false),
    ];
    for (title, attacker, hand, on, off, also_plain) in sites {
        let (state, last) = damage_frame(&attacker, &on, &hand, title, None);
        let queued = offered(&state, |a| matches!(a, SimpleAction::ApplyQueuedAttackDamage { .. })).expect("the queued choice");
        let mut want = vec![format!("coin_queued_by_attack[{title}]")];
        if also_plain {
            want.push(format!("offgate_by_attack[{title}]"));
        }
        r.check(&format!("{title}, a coin Ability where it lands, the queued choice chosen"), fired(&state, &queued, Some(&last)),
            want.iter().map(|s| s.to_string()).collect());
        let (state, last) = damage_frame(&attacker, &off, &hand, title, None);
        let plain = offered(&state, |a| matches!(a, SimpleAction::ApplyDamage { .. })).expect("a plain choice");
        r.check(&format!("{title}, no coin Ability there, a plain choice chosen"), fired(&state, &plain, Some(&last)),
            [format!("offgate_by_attack[{title}]"), "offgate_plain_attack_damage".to_string()].into_iter().collect());
    }

    // 2. A4: the opponent's Active in an own-Bench choice (Zapdos's Raging Thunder: 100 to the Active and 30 to a Benched
    //    Pokemon of the attacker's, one plain choice). A5: a copied discard attack (Ditto's Copy Anything copies Vespiquen ex's
    //    Chase Order, and discards a Benched Bulbasaur).
    let zapdos = vec![with(CardId::A1103Zapdos, vec![EnergyType::Lightning; 3]), mon(bulbasaur)];
    for (defender, want) in [(meowth, vec!["coin_plain_damage_by_attack[Raging Thunder]", "coin_plain_damage_chosen"]),
                             (bulbasaur, vec!["offgate_plain_attack_damage"])] {
        let (state, last) = damage_frame(&zapdos, &[mon(defender)], &[], "Raging Thunder", None);
        let plain = offered(&state, |a| matches!(a, SimpleAction::ApplyDamage { .. })).expect("a plain choice");
        r.check(&format!("Raging Thunder into an Active {defender:?}, the plain choice chosen"), fired(&state, &plain, Some(&last)), set(&want));
    }
    let ditto = vec![with(CardId::A1205Ditto, vec![EnergyType::Grass; 2]), mon(bulbasaur)];
    for (defender, want) in [
        (meowth, vec!["coin_plain_damage_by_attack[Chase Order]", "coin_plain_damage_chosen"]),
        (bulbasaur, vec!["offgate_by_attack[Chase Order]", "offgate_plain_attack_damage"]),
    ] {
        let defenders = [mon(defender), mon(CardId::B4011VespiquenEx)];
        let (state, last) = damage_frame(&ditto, &defenders, &[], "Copy Anything", Some("Chase Order"));
        let plain = offered(&state, |a| matches!(a, SimpleAction::ApplyDamage { .. })).expect("a plain choice");
        r.check(&format!("a copied Chase Order (Copy Anything) into an Active {defender:?}"), fired(&state, &plain, Some(&last)), set(&want));
    }

    // 3. E2: Chase Order with the discard (140) into an Active Galarian Cursola (80 HP), which it Knocks Out; against a 400-HP
    //    Cursola it doesn't, and no Perish Body coin is built.
    let vespiquen = vec![with(CardId::B4011VespiquenEx, vec![EnergyType::Grass; 2]), mon(bulbasaur), mon(bulbasaur)];
    for (cursola, want) in [
        (mon(CardId::A4a035GalarianCursola),
            vec!["perish_plain_hit_offered", "perish_plain_hit_chosen", "offgate_by_attack[Chase Order]"]),
        (sturdy(CardId::A4a035GalarianCursola, 400), vec!["offgate_by_attack[Chase Order]", "offgate_plain_attack_damage"]),
    ] {
        let hp = cursola.get_remaining_hp();
        let (state, last) = damage_frame(&vespiquen, &[cursola, mon(CardId::A1033Charmander)], &[], "Chase Order", None);
        let plain = offered(&state, |a| matches!(a, SimpleAction::ApplyDamage { .. })).expect("a plain choice");
        r.check(&format!("Chase Order with the discard into an Active Galarian Cursola, {hp} HP"), fired(&state, &plain, Some(&last)), set(&want));
    }

    // 4. An attack's own outcome. A4: Whiscash's Earthquake (10 to each of the attacker's Benched Pokemon) with its own Benched
    //    Meowth; E1: with its own Benched Ursaluna at 10 HP. Off the gate: Earthquake (130) into the opponent's Active Ursaluna at
    //    10 HP (the opponent's Guts, as before).
    let whiscash = || with(CardId::A3b039Whiscash, vec![EnergyType::Fighting; 4]);
    for (label, bench, defender, want) in [
        ("its own Benched Meowth", mon(meowth), mon(CardId::A1036CharizardEx), vec!["coin_own_side_split"]),
        ("its own Benched Bulbasaur", mon(bulbasaur), mon(CardId::A1036CharizardEx), vec![]),
        ("its own Benched Ursaluna at 10 HP", mon(CardId::B3b058Ursaluna).with_remaining_hp(10), mon(CardId::A1036CharizardEx),
            vec!["guts_own_side_split"]),
        ("its own Benched Ursaluna at 160 HP", mon(CardId::B3b058Ursaluna), mon(CardId::A1036CharizardEx), vec![]),
        ("into the opponent's Active Ursaluna at 10 HP", mon(bulbasaur), mon(CardId::B3b058Ursaluna).with_remaining_hp(10),
            vec!["offgate_guts_opponent_split"]),
    ] {
        let game = get_initialized_game_with_board(0, 0, 3, vec![whiscash(), bench], vec![defender]);
        let state = game.get_state_clone();
        r.check(&format!("Earthquake, {label}"), fired(&state, &attack_named(&state, "Earthquake"), None), set(&want));
    }

    // 5. The gate coins: Team Rocket's Moltres ex's Heat Charged (3 coins). Item 1: Will on a Confused attacker (with Victini
    //    on the Bench too: the Confusion-first pause). A2: Will on a block coin. A1: Victory Star after a block coin. Off the gate:
    //    a Confused attacker or a block coin without Will, and a Victory Star pause with no gate coin.
    for (label, confused, block, will, victini, want) in [
        ("Confused, Will pending", true, false, true, false, vec!["will_confused_attack"]),
        ("Confused, Will pending, Victini", true, false, true, true, vec!["will_confused_attack"]),
        ("Confused, no Will", true, false, false, false, vec!["offgate_confused_attack"]),
        ("Confused, no Will, Victini", true, false, false, true, vec!["offgate_confused_attack"]),
        ("a block coin, Will pending", false, true, true, false, vec!["will_block_coin_attack"]),
        ("a block coin, Will pending, Confused", true, true, true, false, vec!["will_block_coin_attack"]),
        ("a block coin, no Will", false, true, false, false, vec!["offgate_block_coin_attack"]),
        ("a block coin, no Will, Victini", false, true, false, true, vec!["vs_block_coin_built"]),
        ("a block coin, Will pending, Victini", false, true, true, true, vec!["will_block_coin_attack", "vs_block_coin_built"]),
        ("no gate coin, Victini", false, false, false, true, vec!["offgate_vs_ungated_built"]),
        ("no gate coin, Will pending", false, false, true, false, vec![]),
    ] {
        let state = moltres_board(0, confused, block, will, victini);
        r.check(&format!("Heat Charged, {label}"), fired(&state, &attack_named(&state, "Heat Charged"), None), set(&want));
    }
    // The heads half of A1: the Victory Star choice offered with the block coin still on the Active.
    let paused = (0..40u64).find_map(|seed| {
        let mut game = moltres_game(seed, false, true, false, true);
        let attack = attack_named(&game.get_state_clone(), "Heat Charged");
        game.apply_action(&attack);
        let after = game.get_state_clone();
        after.pending_attack_coin_choice.is_some().then_some(after)
    }).expect("a block coin heads in 40 seeds");
    let keep = offered(&paused, |a| matches!(a, SimpleAction::KeepAttackCoinResults)).expect("Keep");
    r.check("the Victory Star choice after a block coin's heads", fired(&paused, &keep, None), set(&["vs_block_coin_choice_offered"]));

    // 6. Trap Territory. The moves offered: player 0's Active Bulbasaur with 2 Energy against two Ariados (Retreat Cost 3; 2 with
    //    one Ariados, as before): Retreat is offered only on the old count. The outcome: Whimsicott ex's Grass Knot into Charizard
    //    ex (160 with two Ariados, 130 with one). Off the gate: one Ariados.
    for (label, energy, ariados, want) in [
        ("2 Energy, two Ariados", 2, 2, vec!["trap_territory_two_in_play", "trap_territory_offer_changed"]),
        ("4 Energy, two Ariados", 4, 2, vec!["trap_territory_two_in_play"]),
        ("2 Energy, one Ariados", 2, 1, vec!["offgate_trap_territory_one"]),
    ] {
        let mut opponent = vec![mon(bulbasaur)];
        opponent.extend((0..ariados).map(|_| mon(CardId::B1a006Ariados)));
        let state = get_test_game_with_board(vec![with(bulbasaur, vec![EnergyType::Grass; energy]), mon(CardId::A1053Squirtle)], opponent)
            .get_state_clone();
        let end_turn = offered(&state, |a| matches!(a, SimpleAction::EndTurn)).expect("EndTurn");
        r.check(&format!("player 0's moves, {label}, EndTurn chosen"), fired(&state, &end_turn, None), set(&want));
    }
    for (ariados, want) in [(2, vec!["trap_territory_two_in_play", "trap_territory_outcome_changed"]), (1, vec!["offgate_trap_territory_one"])] {
        let mut attacker = vec![with(CardId::B1016WhimsicottEx, vec![EnergyType::Grass; 2])];
        attacker.extend((0..ariados).map(|_| mon(CardId::B1a006Ariados)));
        let state = get_test_game_with_board(attacker, vec![mon(CardId::A1036CharizardEx)]).get_state_clone();
        r.check(&format!("Grass Knot into Charizard ex, {ariados} Ariados"), fired(&state, &attack_named(&state, "Grass Knot"), None), set(&want));
    }

    // 7. Luxury Coin (Gholdengo B4a 109) and Arcade, the board of gholdengo_luxury_coin_test.rs: UseStadium on the opponent's
    //    Arcade, then on player 0's own; the next tick offers the reroll (off the gate).
    let luxury = |owner: Option<usize>| {
        let mut game = get_initialized_game(7);
        let mut state = game.get_state_clone();
        state.current_player = 0;
        state.turn_count = 3;
        state.set_board(vec![mon(bulbasaur), mon(CardId::B4a109Gholdengo)], vec![mon(CardId::A1033Charmander)]);
        state.hands = [vec![], vec![]];
        state.discard_piles = [vec![], vec![]];
        state.active_stadium = Some(get_card_by_enum(CardId::B4a072Arcade));
        state.active_stadium_owner = owner;
        state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander); 8];
        game.set_state(state);
        game
    };
    let use_stadium = Action { actor: 0, action: SimpleAction::UseStadium, is_stack: false };
    r.check("UseStadium on the opponent's Arcade", fired(&luxury(Some(1)).get_state_clone(), &use_stadium, None),
        set(&["luxury_coin_opp_stadium"]));
    let mut own = luxury(Some(0));
    r.check("UseStadium on player 0's own Arcade", fired(&own.get_state_clone(), &use_stadium, None), set(&[]));
    own.apply_action(&use_stadium);
    let pending = own.get_state_clone();
    let keep = offered(&pending, |a| matches!(a, SimpleAction::KeepTrainerCoinResults)).expect("Keep");
    r.check("the Luxury Coin choice on player 0's own Arcade", fired(&pending, &keep, None), set(&["offgate_luxury_coin_offered"]));

    // 8. A Fossil (Helix Fossil) in player 0's hand, under Chingling's Jingly Noise and without it (the board of
    //    rules_repair_trainers.rs's an_item_lock_stops_a_fossil).
    for (locked, want) in [(true, vec!["fossil_item_lock"]), (false, vec!["offgate_fossil_offered"])] {
        let mut game = get_initialized_game_with_board(0, 1, 3, vec![mon(bulbasaur)], vec![mon(CardId::B1109Chingling), mon(CardId::A1033Charmander)]);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1216HelixFossil), get_card_by_enum(CardId::PA005PokeBall)];
        game.set_state(state);
        if locked {
            game.apply_action(&Action { actor: 1, action: attack_action(CardId::B1109Chingling, 0), is_stack: false });
            game.play_until_stable();
        }
        let state = game.get_state_clone();
        if state.generate_possible_actions().0 == 1 {
            game.apply_action(&offered(&state, |a| matches!(a, SimpleAction::EndTurn)).expect("player 1 ends the turn"));
            game.play_until_stable();
        }
        let state = game.get_state_clone();
        assert_eq!(state.generate_possible_actions().0, 0, "player 0's turn");
        let end_turn = offered(&state, |a| matches!(a, SimpleAction::EndTurn)).expect("EndTurn");
        let fossil_in_hand = state.hands[0].iter().any(|c| matches!(c, Card::Trainer(t) if t.trainer_card_type == TrainerType::Fossil));
        assert!(fossil_in_hand, "the Fossil is still in hand");
        r.check(&format!("player 0's main phase with a Fossil in hand, {}", if locked { "under an Item lock" } else { "no lock" }),
            fired(&state, &end_turn, None), set(&want));
    }

    for line in &r.lines {
        println!("{line}");
    }
    println!("{} checks, {} failures", r.lines.len(), r.failures);
    assert_eq!(r.failures, 0);
}
