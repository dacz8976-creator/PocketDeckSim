//! Upstream bcollazo/deckgym-core #367 (b8201002) and #418 (aab4bb9f), merged Oct 17, ported: Rocky Helmet answers the hit
//! back an attack left, and only that (Dustin, Oct 20: "Abilities don't trigger heavy helmet, attacks do"; `rules/02`
//! section 4). Adapted to the fork: the turn ends through the legal EndTurn and any forced stack actions, and the expected
//! numbers are the fork's (the same here: no Weakness, Bounded Field or cut is involved).

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_test_game_with_board},
    Game,
};

fn end_turn(game: &mut Game<'_>, actor: usize) {
    game.apply_action(&Action { actor, action: SimpleAction::EndTurn, is_stack: false });
    loop {
        let (_, choices) = game.get_state_clone().generate_possible_actions();
        if choices.len() != 1 || !choices[0].is_stack {
            break;
        }
        let forced = choices[0].clone();
        game.apply_action(&forced);
    }
}

fn mega_blastoise_ex() -> PlayedCard {
    PlayedCard::from_id(CardId::B1a020MegaBlastoiseEx)
        .with_energy(vec![EnergyType::Water, EnergyType::Water, EnergyType::Colorless])
        .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))
}

/// #367: Mega Sableye ex (170 HP) takes 20 from Mega Blastoise ex's Rocky Helmet on turn 1 (Cursed Jewel into it), 130
/// from Triple Bombardment on turn 2, and 20 more when Cursed Jewel's hit back lands on the Helmet's holder: 170, a Knock
/// Out worth 3 points.
#[test]
fn rocky_helmet_answers_mega_sableye_ex_cursed_jewel_hit_back() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::B3b041MegaSableyeEx)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Colorless])],
        vec![mega_blastoise_ex()],
    );
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B3b041MegaSableyeEx, 0), is_stack: false });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), 150, "Cursed Jewel's 80 (230 - 80)");
    assert_eq!(state.get_active(0).get_remaining_hp(), 150, "the Helmet's 20 for attacking into it (170 - 20)");

    end_turn(&mut game, 0);
    assert_eq!(game.get_state_clone().current_player, 1);
    game.apply_action(&Action { actor: 1, action: attack_action(CardId::B1a020MegaBlastoiseEx, 0), is_stack: false });
    let state = game.get_state_clone();
    assert!(
        state.in_play_pokemon[0][0].is_none(),
        "Mega Sableye ex is Knocked Out: 20 + 130 + 20 (the Helmet answering Cursed Jewel's hit back)"
    );
    assert_eq!(state.points[1], 3, "a Mega Evolution Pokémon ex is worth 3 points");
}

/// #367: Rocky Helmet's own 20 isn't damage from an attack, so with a Helmet on each side the attacker takes one 20 and
/// the defender only the attack's damage.
#[test]
fn rocky_helmet_damage_does_not_set_off_the_opposing_rocky_helmet() {
    let mut game = get_test_game_with_board(vec![mega_blastoise_ex()], vec![mega_blastoise_ex()]);
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::B1a020MegaBlastoiseEx, 0), is_stack: false });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 210, "the defender's Helmet: 230 - 20");
    assert_eq!(state.get_active(1).get_remaining_hp(), 100, "Triple Bombardment only: 230 - 130");
}

/// #418: Druddigon's Rough Skin is an Ability's return damage, not an attack's, so it doesn't set off the attacker's
/// Rocky Helmet: Bulbasaur takes Rough Skin's 20 and Druddigon only Vine Whip's 40.
#[test]
fn rough_skin_does_not_set_off_rocky_helmet() {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
            .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])
            .with_tool(get_card_by_enum(CardId::A2148RockyHelmet))],
        vec![PlayedCard::from_id(CardId::A1a056Druddigon)],
    );
    game.apply_action(&Action { actor: 0, action: attack_action(CardId::A1001Bulbasaur, 0), is_stack: false });
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_remaining_hp(), 50, "Rough Skin's 20 (70 - 20)");
    assert_eq!(state.get_active(1).get_remaining_hp(), 60, "Vine Whip's 40 only (100 - 40)");
}
