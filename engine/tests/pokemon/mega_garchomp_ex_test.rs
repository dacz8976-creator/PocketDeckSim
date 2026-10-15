//! Mega Garchomp ex (P-B 099), added Oct 15 from Dustin's in-game screenshot (rl/results/mega_garchomp_2026-10-15/README.md):
//! Stage 2 from Gabite, Dragon, 220 HP, no Weakness, Retreat 2; Falling Edge [W][F][C] 190, "Discard 2 random Energy from
//! this Pokémon." Its knockout is worth 3 points (Mega Evolution ex). The card is looked up by its id, so before it is in
//! the database every test here fails with the message below rather than not compiling.
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_logic::can_rare_candy_evolve,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, PokemonCard},
    test_support::{get_initialized_game_with_board, get_test_game_with_board},
};

fn garchomp_id() -> CardId {
    CardId::from_card_id("P-B 099").expect("P-B 099 Mega Garchomp ex is not in the card database")
}

fn garchomp_card() -> PokemonCard {
    match get_card_by_enum(garchomp_id()) {
        Card::Pokemon(p) => p,
        _ => panic!("P-B 099 should be a Pokémon"),
    }
}

fn garchomp(energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::from_id(garchomp_id()).with_energy(energy)
}

fn falling_edge() -> SimpleAction {
    SimpleAction::Attack(garchomp_card().attacks[0].clone())
}

/// A 300-HP Bulbasaur (Grass, Weakness Fire): a damage sponge Falling Edge can't knock out.
fn sponge() -> PlayedCard {
    PlayedCard::new(get_card_by_enum(CardId::A1001Bulbasaur), 0, 300, vec![], false, vec![])
}

fn attack(game: &mut deckgym::Game<'static>) {
    game.apply_action(&Action { actor: 0, action: falling_edge(), is_stack: false });
}

#[test]
fn the_card_is_a_stage_2_dragon_mega_ex_with_220_hp() {
    let p = garchomp_card();
    assert_eq!(p.name, "Mega Garchomp ex");
    assert_eq!(p.stage, 2);
    assert_eq!(p.energy_type, EnergyType::Dragon);
    assert_eq!(p.hp, 220);
    assert!(p.ability.is_none());
    assert_eq!(p.attacks.len(), 1);
}

#[test]
fn falling_edge_costs_water_fighting_colorless() {
    let a = &garchomp_card().attacks[0];
    assert_eq!(a.title, "Falling Edge");
    assert_eq!(a.energy_required, vec![EnergyType::Water, EnergyType::Fighting, EnergyType::Colorless]);
    assert_eq!(a.effect.as_deref(), Some("Discard 2 random Energy from this Pokémon."));
}

#[test]
fn falling_edge_does_190() {
    let mut game = get_test_game_with_board(
        vec![garchomp(vec![EnergyType::Water, EnergyType::Fighting, EnergyType::Fighting])],
        vec![sponge()],
    );
    attack(&mut game);
    assert_eq!(game.get_state_clone().get_active(1).get_remaining_hp(), 300 - 190);
}

#[test]
fn falling_edge_discards_exactly_2_random_energy_from_itself() {
    // Four different Energy: over many seeds every one of them is discarded sometimes, and always exactly 2 go.
    let attached = vec![EnergyType::Water, EnergyType::Fighting, EnergyType::Grass, EnergyType::Lightning];
    let mut ever_discarded = std::collections::HashSet::new();
    for seed in 0..64 {
        let mut game =
            get_initialized_game_with_board(20_000_015_100 + seed, 0, 3, vec![garchomp(attached.clone())], vec![sponge()]);
        attack(&mut game);
        let state = game.get_state_clone();
        let left = &state.get_active(0).attached_energy;
        assert_eq!(left.len(), 2, "seed {seed}: 2 of 4 Energy stay");
        assert_eq!(state.discard_energies[0].len(), 2, "seed {seed}: 2 Energy go to the discard pile");
        let mut all: Vec<EnergyType> = left.iter().chain(state.discard_energies[0].iter()).cloned().collect();
        all.sort_by_key(|e| format!("{e:?}"));
        let mut want = attached.clone();
        want.sort_by_key(|e| format!("{e:?}"));
        assert_eq!(all, want, "seed {seed}: the discarded Energy are the attacker's own");
        ever_discarded.extend(state.discard_energies[0].iter().cloned());
        assert_eq!(state.get_active(1).get_remaining_hp(), 300 - 190);
        assert!(state.discard_energies[1].is_empty(), "nothing is discarded from the defender");
    }
    assert_eq!(ever_discarded.len(), 4, "the choice is random: every attached type is discarded in some seed");
}

#[test]
fn with_fewer_than_2_energy_attached_it_discards_what_is_there() {
    // Not reachable in play (the attack costs 3), but the effect must not fail: 1 attached, 1 discarded, damage as usual.
    let mut game = get_test_game_with_board(vec![garchomp(vec![EnergyType::Water])], vec![sponge()]);
    attack(&mut game);
    let state = game.get_state_clone();
    assert!(state.get_active(0).attached_energy.is_empty());
    assert_eq!(state.discard_energies[0], vec![EnergyType::Water]);
    assert_eq!(state.get_active(1).get_remaining_hp(), 300 - 190);
}

#[test]
fn its_knockout_gives_the_opponent_3_points() {
    // Player 1's Mega Garchomp ex has 20 HP left and a Bench; player 0's Falling Edge knocks it out.
    let low = PlayedCard::new(get_card_by_enum(garchomp_id()), 200, 220, vec![], false, vec![]);
    let mut game = get_test_game_with_board(
        vec![garchomp(vec![EnergyType::Water, EnergyType::Fighting, EnergyType::Fighting])],
        vec![low, PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    attack(&mut game);
    let state = game.get_state_clone();
    assert_eq!(state.points[0], 3, "a Mega Evolution ex is worth 3 points");
}

#[test]
fn retreat_costs_2_and_it_has_no_weakness() {
    let p = garchomp_card();
    assert_eq!(p.retreat_cost.len(), 2);
    assert!(p.retreat_cost.iter().all(|e| *e == EnergyType::Colorless));
    assert_eq!(p.weakness, None);
}

#[test]
fn it_evolves_from_gabite_and_from_gible_with_rare_candy() {
    let card = get_card_by_enum(garchomp_id());
    assert_eq!(garchomp_card().evolves_from.as_deref(), Some("Gabite"));
    for gabite in [CardId::A2122Gabite, CardId::A2a046Gabite, CardId::B4a053Gabite] {
        assert!(get_card_by_enum(gabite).can_evolve_into(&card), "{gabite:?} evolves into Mega Garchomp ex");
    }
    assert!(!get_card_by_enum(CardId::A2121Gible).can_evolve_into(&card), "not from Gible without Rare Candy");
    for gible in [CardId::A2121Gible, CardId::A2a045Gible, CardId::B4a052Gible] {
        assert!(can_rare_candy_evolve(&card, &PlayedCard::from_id(gible)), "Rare Candy: {gible:?} to Mega Garchomp ex");
    }
}
