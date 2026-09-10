use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// Mega Latios ex (P-B 024): 180 HP, no weakness — a damage sponge that survives every attack in
/// this file, so `180 - remaining_hp` is the exact damage dealt.
fn sponge() -> PlayedCard {
    PlayedCard::from_id(CardId::PB024MegaLatiosEx)
}

fn game_with(seed: u64, attacker: PlayedCard, defender: PlayedCard) -> Game<'static> {
    get_initialized_game_with_board(seed, 0, 3, vec![attacker], vec![defender])
}

/// Put Will in player 0's hand and play it, forcing the first coin of this turn to be heads.
fn play_will(game: &mut Game<'static>) {
    let will = match get_card_by_enum(CardId::A4156Will) {
        Card::Trainer(trainer_card) => trainer_card,
        _ => panic!("Will should be a Trainer card"),
    };
    let mut state = game.get_state_clone();
    state.hands[0].push(Card::Trainer(will.clone()));
    game.set_state(state);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Play { trainer_card: will },
        is_stack: false,
    });
}

fn do_attack(game: &mut Game<'static>, attacker: CardId) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker, 0),
        is_stack: false,
    });
}

/// Lanturn ex (A4 065 et al.) "Flashing Signal": 80 damage; heads → Paralyzed, tails → Confused.
#[test]
fn test_lanturn_flashing_signal_heads_paralyzes() {
    let lanturn = || {
        PlayedCard::from_id(CardId::A4065LanturnEx).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])
    };
    for seed in 0..20 {
        let mut game = game_with(seed, lanturn(), sponge());
        play_will(&mut game);
        do_attack(&mut game, CardId::A4065LanturnEx);

        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(
            180 - defender.get_remaining_hp(),
            80,
            "seed {seed}: Flashing Signal always does 80"
        );
        assert!(
            defender.is_paralyzed(),
            "seed {seed}: forced heads must Paralyze"
        );
        assert!(
            !defender.is_confused(),
            "seed {seed}: heads must not Confuse"
        );
    }
}

#[test]
fn test_lanturn_flashing_signal_exactly_one_status_and_both_branches_occur() {
    let lanturn = || {
        PlayedCard::from_id(CardId::A4065LanturnEx).with_energy(vec![
            EnergyType::Lightning,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])
    };
    let (mut saw_paralyzed, mut saw_confused) = (false, false);
    for seed in 0..60 {
        let mut game = game_with(seed, lanturn(), sponge());
        do_attack(&mut game, CardId::A4065LanturnEx);

        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(180 - defender.get_remaining_hp(), 80, "seed {seed}");
        let paralyzed = defender.is_paralyzed();
        let confused = defender.is_confused();
        assert!(
            paralyzed ^ confused,
            "seed {seed}: exactly one of Paralyzed/Confused must be applied"
        );
        saw_paralyzed |= paralyzed;
        saw_confused |= confused;
    }
    assert!(saw_paralyzed, "some seed must land heads (Paralyzed)");
    assert!(saw_confused, "some seed must land tails (Confused)");
}

/// Arcanine (B1 029 / P-B 013) "Fire Fang": 50 damage; heads → Burned, tails → nothing extra.
#[test]
fn test_arcanine_fire_fang_burns_on_heads_only() {
    let arcanine = || {
        PlayedCard::from_id(CardId::B1029Arcanine)
            .with_energy(vec![EnergyType::Fire, EnergyType::Fire])
    };

    // Forced heads → Burned.
    let mut game = game_with(0, arcanine(), sponge());
    play_will(&mut game);
    do_attack(&mut game, CardId::B1029Arcanine);
    let state = game.get_state_clone();
    assert_eq!(180 - state.get_active(1).get_remaining_hp(), 50);
    assert!(state.get_active(1).is_burned(), "heads must Burn");

    // Negative: some seed lands tails → 50 damage but no Burn.
    let (mut saw_burn, mut saw_no_burn) = (false, false);
    for seed in 0..60 {
        let mut game = game_with(seed, arcanine(), sponge());
        do_attack(&mut game, CardId::B1029Arcanine);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(
            180 - defender.get_remaining_hp(),
            50,
            "seed {seed}: damage is unconditional"
        );
        saw_burn |= defender.is_burned();
        saw_no_burn |= !defender.is_burned();
    }
    assert!(saw_burn && saw_no_burn, "both coin branches must occur");
}

/// Drapion (B1 153) "Stun Poison": 50 damage; heads → Poisoned AND Paralyzed, tails → neither.
#[test]
fn test_stun_poison_applies_both_conditions_on_heads_only() {
    let drapion = || {
        PlayedCard::from_id(CardId::B1153Drapion).with_energy(vec![
            EnergyType::Darkness,
            EnergyType::Darkness,
            EnergyType::Colorless,
        ])
    };

    let mut game = game_with(0, drapion(), sponge());
    play_will(&mut game);
    do_attack(&mut game, CardId::B1153Drapion);
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(180 - defender.get_remaining_hp(), 50);
    assert!(
        defender.is_poisoned() && defender.is_paralyzed(),
        "heads must apply both Poisoned and Paralyzed"
    );

    let (mut saw_status, mut saw_none) = (false, false);
    for seed in 0..60 {
        let mut game = game_with(seed, drapion(), sponge());
        do_attack(&mut game, CardId::B1153Drapion);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        assert_eq!(180 - defender.get_remaining_hp(), 50, "seed {seed}");
        assert_eq!(
            defender.is_poisoned(),
            defender.is_paralyzed(),
            "seed {seed}: the two conditions must be applied together or not at all"
        );
        saw_status |= defender.is_poisoned();
        saw_none |= !defender.is_poisoned();
    }
    assert!(saw_status && saw_none, "both coin branches must occur");
}

/// Drampa (A3b 054) "Dragon Breath": tails → the attack does nothing; heads → 70 and Paralyzed.
#[test]
fn test_drampa_dragon_breath_all_or_nothing() {
    let drampa = || {
        PlayedCard::from_id(CardId::A3b054Drampa)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
    };

    let mut game = game_with(0, drampa(), sponge());
    play_will(&mut game);
    do_attack(&mut game, CardId::A3b054Drampa);
    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(180 - defender.get_remaining_hp(), 70, "heads does 70");
    assert!(defender.is_paralyzed(), "heads must Paralyze");

    let (mut saw_hit, mut saw_nothing) = (false, false);
    for seed in 0..60 {
        let mut game = game_with(seed, drampa(), sponge());
        do_attack(&mut game, CardId::A3b054Drampa);
        let state = game.get_state_clone();
        let defender = state.get_active(1);
        let damage = 180 - defender.get_remaining_hp();
        match damage {
            70 => {
                assert!(defender.is_paralyzed(), "seed {seed}: heads must Paralyze");
                saw_hit = true;
            }
            0 => {
                assert!(
                    !defender.is_paralyzed(),
                    "seed {seed}: tails does nothing at all"
                );
                saw_nothing = true;
            }
            other => panic!("seed {seed}: Dragon Breath dealt unexpected damage {other}"),
        }
    }
    assert!(saw_hit && saw_nothing, "both coin branches must occur");
}

/// Salazzle (A3 036) "Heated Poison": 30 damage, opponent is always Poisoned and Burned.
#[test]
fn test_salazzle_heated_poison_always_applies_both() {
    let salazzle = PlayedCard::from_id(CardId::A3036Salazzle)
        .with_energy(vec![EnergyType::Fire, EnergyType::Fire]);
    let mut game = game_with(0, salazzle, sponge());
    do_attack(&mut game, CardId::A3036Salazzle);

    let state = game.get_state_clone();
    let defender = state.get_active(1);
    assert_eq!(180 - defender.get_remaining_hp(), 30);
    assert!(defender.is_poisoned(), "must be Poisoned");
    assert!(defender.is_burned(), "must be Burned");
    assert!(!defender.is_paralyzed() && !defender.is_confused() && !defender.is_asleep());
}

/// Musharna (A4 091) "Dream Dance": 60 damage and BOTH Active Pokémon are now Asleep.
#[test]
fn test_musharna_dream_dance_puts_both_actives_asleep() {
    let musharna = PlayedCard::from_id(CardId::A4091Musharna)
        .with_energy(vec![EnergyType::Psychic, EnergyType::Colorless]);
    let mut game = game_with(0, musharna, sponge());
    do_attack(&mut game, CardId::A4091Musharna);

    let state = game.get_state_clone();
    assert_eq!(180 - state.get_active(1).get_remaining_hp(), 60);
    assert!(state.get_active(1).is_asleep(), "defender must be Asleep");
    assert!(
        state.get_active(0).is_asleep(),
        "attacker must be Asleep too"
    );
}
