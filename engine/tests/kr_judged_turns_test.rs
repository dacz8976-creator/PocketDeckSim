//! kr = km + C2 (`rl/results/kn_build_2026-09-30/TIMING.md`) on the unplayed-Trainer diagnosis's ten judged
//! Goo-zooka turns (`rl/results/trainer_unplayed_diag_2026-09-30/README.md`, question 3). Each turn is reached by
//! replaying its floor game (`rl/results/floor_dustin_2026-09-30/`) with km3 on both sides, as `deckgym simulate
//! --seed-stream` played it (`create_players`, `Game::new` on the game's own seed, `play_tick`); a guard checks the
//! opponent's Active there is the one the diagnosis recorded. From the start of that turn the deck's side plays the
//! turn once as kr3 and once as km3 (the opponent km3 in both, `Game::from_state` on the game's seed).
//! - TIMING.md's reading: C2 plays Goo-zooka on the six turns where a benched threat of theirs would come in on their
//!   next turn behind an Active that can't pay the raised cost (9102 t4, 12600 t4, 9600 t3 in deck 14; 8101 t3,
//!   11602 t4, 7102 t2 in deck 15), and not on the three the diagnosis judged "no" (7100 t9, 8103 t4 in deck 14;
//!   14600 t4 in deck 15). 13600 t6 (deck 15), the seventh "yes", is one TIMING.md expected C2 to miss: it is printed,
//!   not asserted.
//! - km3 plays it on none of the ten (the floor's km3 didn't).
//! The lists are embedded as they are at this commit, so a later edit to a deck file can't change the test.
use deckgym::actions::SimpleAction;
use deckgym::players::{create_players, parse_player_code};
use deckgym::{Deck, Game};

/// `decks/dustin/14-comfey-raticate-hypno.txt` at this commit.
const DECK14: &str = "Energy: Psychic
1 Comfey A3 080
2 Team Rocket's Rattata B4a 058
2 Team Rocket's Raticate ex B4a 059
2 Team Rocket's Drowzee B4a 027
2 Team Rocket's Hypno B4a 028
2 Poké Ball P-A 005
1 Pokémon Flute A1a 064
1 Team Rocket's Goo-zooka B4a 068
1 Elegant Cape B3b 065
2 Professor's Research P-A 007
1 Cyrus A2 150
1 Copycat B1 225
1 Sightseer B2 150
1 Team Rocket's Researcher B4a 069\n";

/// `decks/dustin/15-jolteon-oricorio-raticate.txt` at this commit.
const DECK15: &str = "Energy: Lightning
2 Eevee B1 184
2 Jolteon ex B1 081
1 Oricorio A3 066
2 Team Rocket's Rattata B4a 058
2 Team Rocket's Raticate ex B4a 059
2 Poké Ball P-A 005
1 Team Rocket's Goo-zooka B4a 068
2 Professor's Research P-A 007
1 Sabrina A1 225
1 Cyrus A2 150
1 Pokémon Center Lady A2b 070
1 Ilima A3 149
1 Copycat B1 225
1 Lisia B1 226\n";

/// `decks/screen/opponents/t-altaria.txt` at this commit.
const T_ALTARIA: &str = "Energy: Psychic
2 Swablu B1 196
1 Mega Altaria ex B1 102
2 Eevee B1 184
2 Espeon B3a 020
2 Darkrai B2b 040
1 Igglybuff A4a 059
2 Professor's Research P-A 007
2 Copycat B1 225
1 Sabrina A1 225
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Small Balloon B3b 064
1 Training Area B2 153\n";

/// `decks/screen/opponents/t-blaziken.txt` at this commit.
const T_BLAZIKEN: &str = "Energy: Fire
2 Torchic B1 033
2 Mega Blaziken ex B1 036
1 Heatmor B1 044
1 Castform Sunny Form B3 024
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
2 Flame Patch B1 217
2 Rare Candy A3 144
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Rocky Helmet A2 148
1 Hiking Trail B2b 069\n";

/// `decks/screen/opponents/t-hydreigon.txt` at this commit.
const T_HYDREIGON: &str = "Energy: Darkness
2 Deino B1 155
2 Hydreigon B1 157
1 Bombirdier B3 115
1 Mega Absol ex B1 151
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
1 Sabrina A1 225
2 Poké Ball P-A 005
2 Rare Candy A3 144
2 Lucky Ice Pop B2 145
2 Deceptive Needle B4 148\n";

/// `decks/screen/opponents/t-sceptile.txt` at this commit.
const T_SCEPTILE: &str = "Energy: Grass
2 Caterpie B3b 001
2 Metapod B3b 002
2 Butterfree B3b 003
1 Treecko B3 005
1 Grovyle B3 006
1 Mega Sceptile ex B3 008
2 Professor's Research P-A 007
1 Erika A1 219
1 Copycat B1 225
1 Sabrina A1 225
1 Cyrus A2 150
2 Quick-Grow Extract B1a 067
1 Leaf Cape A3 147
2 Fragrant Forest B3 153\n";

/// `decks/screen/opponents/t-suicune.txt` at this commit.
const T_SUICUNE: &str = "Energy: Water
1 Frigibax B2a 034
1 Frigibax P-B 037
2 Baxcalibur B2a 036
2 Suicune ex A4a 020
1 Chien-Pao ex B2a 037
2 Professor's Research P-A 007
1 Team Rocket's Boss B4a 071
1 Pokémon Center Lady A2b 070
1 Copycat B1 225
2 Rare Candy A3 144
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Inflatable Boat A4a 067
1 Giant Cape A2 147
1 Soothing Shore B4 154\n";

/// `decks/screen/opponents/t-vespiquen.txt` at this commit.
const T_VESPIQUEN: &str = "Energy: Grass
2 Combee B4 010
2 Vespiquen ex B4 011
2 Shuckle ex A4 021
1 Teal Mask Ogerpon ex B2 017
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
1 Sabrina A1 225
2 X Speed P-A 002
1 Field Blower B3 147
2 Leaf Cape A3 147
2 Fragrant Forest B3 153\n";

/// `decks/screen/opponents/t-weezing.txt` at this commit.
const T_WEEZING: &str = "Energy: Darkness
2 Hoopa ex B4 103
2 Team Rocket's Koffing B4a 042
2 Team Rocket's Weezing ex B4a 043
1 Darkrai ex A2 110
2 Professor's Research P-A 007
2 Cyrus A2 150
2 Copycat B1 225
1 Mars A2 155
2 Poké Ball P-A 005
1 X Speed P-A 002
1 Field Blower B3 147
2 Deceptive Needle B4 148\n";

/// Whether the deck's side plays Team Rocket's Goo-zooka on `turn` of the floor game `seed` (deck in `seat` against
/// `opponent`), piloted by `code` from the start of that turn; also the opponent's Active at the start of the turn.
fn plays_goo_zooka(deck: &str, opponent: &str, seat: usize, seed: u64, turn: u8, code: &str) -> (bool, String) {
    let (deck, opponent) = (Deck::from_string(deck).unwrap(), Deck::from_string(opponent).unwrap());
    let (d0, d1) = if seat == 0 { (deck.clone(), opponent.clone()) } else { (opponent.clone(), deck.clone()) };
    let km3 = || parse_player_code("km3").unwrap();
    let mut game = Game::new(create_players(d0.clone(), d1.clone(), vec![km3(), km3()]), seed);
    loop {
        let state = game.get_state_clone();
        assert!(!game.is_game_over() && state.turn_count <= turn, "the floor game {seed} never reached turn {turn}");
        if state.turn_count == turn && state.current_player == seat {
            break;
        }
        game.play_tick();
    }
    let start = game.get_state_clone();
    let their_active = start.maybe_get_active(1 - seat).map(|a| a.get_name()).unwrap_or_default();
    let mut codes = vec![km3(), km3()];
    codes[seat] = parse_player_code(code).unwrap();
    let mut turn_game = Game::from_state(start, create_players(d0, d1, codes), seed);
    let mut played = false;
    while !turn_game.is_game_over() && turn_game.get_state_clone().turn_count == turn {
        let chosen = turn_game.play_tick();
        played |= chosen.actor == seat
            && matches!(&chosen.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Team Rocket's Goo-zooka");
    }
    (played, their_active)
}

#[test]
fn kr3_plays_goo_zooka_on_the_six_judged_turns_c2_reads_and_not_on_the_three_judged_no() {
    // (deck, opponent, seat, floor seed, turn, the opponent's Active the diagnosis recorded, kr3 expected to play it)
    let cases: [(&str, &str, usize, u64, u8, &str, Option<bool>); 10] = [
        (DECK14, T_HYDREIGON, 0, 9102, 4, "Deino", Some(true)),
        (DECK14, T_SUICUNE, 1, 12600, 4, "Chien-Pao ex", Some(true)),
        (DECK14, T_HYDREIGON, 1, 9600, 3, "Deino", Some(true)),
        (DECK15, T_BLAZIKEN, 0, 8101, 3, "Castform Sunny Form", Some(true)),
        (DECK15, T_SCEPTILE, 1, 11602, 4, "Butterfree", Some(true)),
        (DECK15, T_ALTARIA, 0, 7102, 2, "Igglybuff", Some(true)),
        (DECK14, T_ALTARIA, 0, 7100, 9, "Mega Altaria ex", Some(false)),
        (DECK14, T_BLAZIKEN, 0, 8103, 4, "Mega Blaziken ex", Some(false)),
        (DECK15, T_WEEZING, 1, 14600, 4, "Hoopa ex", Some(false)),
        (DECK15, T_VESPIQUEN, 1, 13600, 6, "Shuckle ex", None),
    ];
    let mut wrong = vec![];
    for (deck, opponent, seat, seed, turn, active, expected) in cases {
        let (kr3, their_active) = plays_goo_zooka(deck, opponent, seat, seed, turn, "kr3");
        let (km3, _) = plays_goo_zooka(deck, opponent, seat, seed, turn, "km3");
        assert_eq!(their_active, active, "floor game {seed}: the replay's board is not the diagnosis's");
        println!("seed {seed} turn {turn} (their Active {active}): kr3 plays Goo-zooka {kr3}, km3 {km3}");
        assert!(!km3, "km3 plays Goo-zooka on {seed} turn {turn}");
        if expected.is_some_and(|e| e != kr3) {
            wrong.push((seed, turn, kr3));
        }
    }
    assert!(wrong.is_empty(), "kr3 against TIMING.md's reading (seed, turn, played): {wrong:?}");
}
