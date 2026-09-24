// Claude's independent review probes for 0.1.0-pdl.rules1 (2026-09-22). Each test prints a
// VERIFY line and always passes; expected values come from rules/ and Dustin's tests.
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Deck,
};
use rand::{rngs::StdRng, SeedableRng};

const T1_DECK: &str = "Energy: Fighting
2 Riolu B3 079
2 Poké Ball P-A 005
1 Pokémon Flute A1a 064
1 Lucky Ice Pop B2 145
1 Small Balloon B3b 064
2 Professor's Research P-A 007
1 Cynthia A2 152
1 Copycat B1 225
1 Wally B4 153
2 Team Rocket's Researcher B4a 069
2 Team Rocket's Master Plan B4a 070
1 Team Rocket's Boss B4a 071
1 Mesagoza B2a 093
1 Rainbow Cave B4 155
1 Arcade B4a 072
";

#[test]
fn opening_hand_distribution() {
    let base = Deck::from_string(T1_DECK).expect("deck parses");
    assert_eq!(base.cards.len(), 20);
    let n = 40_000u64;
    let (mut both, mut none) = (0u64, 0u64);
    for seed in 0..n {
        let mut deck = base.clone();
        let mut rng = StdRng::seed_from_u64(seed);
        deck.shuffle(true, &mut rng);
        let k = deck.cards.iter().take(5).filter(|c| c.is_basic()).count();
        if k == 2 { both += 1; }
        if k == 0 { none += 1; }
    }
    println!(
        "VERIFY opening hand, 2-Basic deck, {n} deals: both Basics {:.2}% (swap-in model 5.26%, Basic-first 21.05%), zero Basics {}",
        100.0 * both as f64 / n as f64, none
    );
}

#[test]
fn damage_order_skarmory_bounded_field() {
    for bounded in [false, true] {
        let attacker = PlayedCard::from_id(CardId::A1050Salazzle)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire]);
        let defender = PlayedCard::from_id(CardId::A4124SkarmoryEx)
            .with_tool(get_card_by_enum(CardId::B2148MetalCoreBarrier));
        let mut game = get_test_game_with_board(vec![attacker], vec![defender]);
        if bounded {
            let mut s = game.get_state_clone();
            s.set_active_stadium(get_card_by_enum(CardId::B3155BoundedField));
            game.set_state(s);
        }
        let before = game.get_state_clone().get_active(1).get_remaining_hp();
        game.apply_action(&Action { actor: 0, action: attack_action(CardId::A1050Salazzle, 0), is_stack: false });
        let after = game.get_state_clone().in_play_pokemon[1][0].as_ref().map(|p| p.get_remaining_hp());
        println!(
            "VERIFY 60 Fire into Skarmory ex + Metal Core Barrier, Bounded Field={bounded}: damage {} (official: {})",
            before - after.unwrap_or(0),
            if bounded { "60x2-50 = 70, seen in Dustin's game" } else { "60+20-50 = 30" }
        );
    }
}

#[test]
fn iron_jugulis_retaliates() {
    let attacker = PlayedCard::from_id(CardId::A1050Salazzle)
        .with_energy(vec![EnergyType::Fire, EnergyType::Fire]);
    let mut game = get_test_game_with_board(
        vec![attacker],
        vec![PlayedCard::from_id(CardId::B3a046IronJugulis), PlayedCard::from_id(CardId::A1206Eevee)],
    );
    let before = game.get_state_clone().get_active(0).get_remaining_hp();
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::A1050Salazzle, 0), is_stack: false });
    let after = game.get_state_clone().in_play_pokemon[0][0].as_ref().map(|p| p.get_remaining_hp());
    println!("VERIFY Iron Jugulis Automated Combat: attacker {before} -> {after:?} (expected 20 less)");
}

fn play_named(game: &mut deckgym::Game<'static>, name: &str) -> bool {
    let (actor, actions) = game.get_state_clone().generate_possible_actions();
    let found = actions.into_iter().find(|a| match &a.action {
        SimpleAction::Play { trainer_card } => trainer_card.name == name,
        _ => false,
    });
    match found {
        Some(a) => { game.apply_action(&Action { actor, ..a }); true }
        None => false,
    }
}

#[test]
fn one_stadium_play_per_turn() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1206Eevee)],
        vec![PlayedCard::from_id(CardId::A1206Eevee)],
    );
    let mut s = game.get_state_clone();
    s.hands[0] = vec![get_card_by_enum(CardId::B2a093Mesagoza), get_card_by_enum(CardId::B4a072Arcade)];
    game.set_state(s);
    let first = play_named(&mut game, "Mesagoza");
    let second = play_named(&mut game, "Arcade");
    println!("VERIFY Stadiums in one turn: Mesagoza played={first}, Arcade also offered={second} (expected true, false)");
}

#[test]
fn mythical_slab_psychic_not_basic() {
    for (top, label) in [(CardId::A1131Kirlia, "Kirlia (Psychic Stage 1)"), (CardId::A1206Eevee, "Eevee (Colorless Basic)")] {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1206Eevee)],
            vec![PlayedCard::from_id(CardId::A1206Eevee)],
        );
        let mut s = game.get_state_clone();
        s.hands[0] = vec![get_card_by_enum(CardId::A1a065MythicalSlab)];
        s.decks[0].cards.insert(0, get_card_by_enum(top));
        game.set_state(s);
        let played = play_named(&mut game, "Mythical Slab");
        let hand: Vec<String> = game.get_state_clone().hands[0].iter().map(|c| c.get_name()).collect();
        println!("VERIFY Mythical Slab with {label} on top: played={played}, hand after = {hand:?} (Kirlia should be in hand; Eevee should not)");
    }
}
