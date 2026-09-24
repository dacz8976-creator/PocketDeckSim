use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Octillery (A4 056 / 169) "Octazooka": "If the Defending Pokémon tries to use an attack, your
/// opponent flips a coin. If tails, that attack doesn't happen. This effect lasts until the
/// Defending Pokémon leaves the Active Spot, and it doesn't stack."
fn sponge(card_id: CardId, energy: Vec<EnergyType>) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(card_id), 0, 300, energy, false, vec![])
}

fn game_with_octillery(seed: u64) -> Game<'static> {
    get_initialized_game_with_board(
        seed,
        0,
        3,
        vec![PlayedCard::from_id(CardId::A4056Octillery)
            .with_energy(vec![EnergyType::Water, EnergyType::Water])],
        vec![
            sponge(
                CardId::A1001Bulbasaur,
                vec![EnergyType::Grass, EnergyType::Grass, EnergyType::Colorless],
            ),
            sponge(
                CardId::A1033Charmander,
                vec![EnergyType::Fire, EnergyType::Colorless],
            ),
        ],
    )
}

fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    game.play_until_stable();
}

fn octazooka(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A4056Octillery, 0),
        is_stack: false,
    });
}

fn vine_whip(game: &mut Game<'static>) {
    game.apply_action(&Action {
        actor: 1,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    game.play_until_stable();
}

/// Damage Octillery took from the Defending Pokémon's next attack: 0 when the Octazooka coin came
/// up tails, 40 when it came up heads.
fn damage_to_octillery_next_turn(seed: u64) -> u32 {
    let mut game = game_with_octillery(seed);
    octazooka(&mut game);
    end_turn(&mut game, 0);

    let before = game.get_state_clone().get_active(0).get_remaining_hp();
    vine_whip(&mut game);
    before - game.get_state_clone().get_active(0).get_remaining_hp()
}

#[test]
fn test_octazooka_deals_its_damage_and_makes_the_defender_flip_to_attack() {
    let mut blocked = 0;
    let mut allowed = 0;

    for seed in 0..40 {
        match damage_to_octillery_next_turn(seed) {
            0 => blocked += 1,
            40 => allowed += 1,
            other => panic!("seed {seed}: unexpected damage {other} from Vine Whip"),
        }
    }

    assert!(
        blocked > 0,
        "the Defending Pokémon's attack was never blocked in 40 seeds"
    );
    assert!(
        allowed > 0,
        "the Defending Pokémon's attack was always blocked in 40 seeds"
    );
}

#[test]
fn test_octazooka_does_its_printed_damage() {
    let mut game = game_with_octillery(0);
    octazooka(&mut game);

    assert_eq!(
        game.get_state_clone().get_active(1).get_remaining_hp(),
        250,
        "Octazooka should still do its printed 50 damage (300 - 50)"
    );
}

/// Negative: the block sits on the Defending Pokémon, so once it leaves the Active Spot it is
/// wiped. Bulbasaur retreats, comes back, and then attacks freely on every seed.
#[test]
fn test_octazooka_block_is_gone_after_the_defender_leaves_the_active_spot() {
    for seed in 0..12 {
        let mut game = game_with_octillery(seed);
        octazooka(&mut game);
        end_turn(&mut game, 0);

        // Opponent retreats Bulbasaur to the Bench (clearing the effect) and ends the turn.
        game.apply_action(&Action {
            actor: 1,
            action: SimpleAction::Retreat(1),
            is_stack: false,
        });
        end_turn(&mut game, 1);
        end_turn(&mut game, 0);

        // Bulbasaur comes back and attacks; the Octazooka coin should no longer exist.
        game.apply_action(&Action {
            actor: 1,
            action: SimpleAction::Retreat(1),
            is_stack: false,
        });
        let before = game.get_state_clone().get_active(0).get_remaining_hp();
        vine_whip(&mut game);
        let damage = before - game.get_state_clone().get_active(0).get_remaining_hp();

        assert_eq!(
            damage, 40,
            "seed {seed}: leaving the Active Spot should clear Octazooka's block"
        );
    }
}
