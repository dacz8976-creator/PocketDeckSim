use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};

/// A high-HP damage sponge (Mega Latios ex card with an inflated base HP) so that even max-heads
/// rolls never knock it out and `hp_before - hp_after` is the exact damage dealt.
fn sponge(hp: u32) -> PlayedCard {
    let card = get_card_by_enum(CardId::PB024MegaLatiosEx);
    PlayedCard::new(card, 0, hp, vec![], false, vec![])
}

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

/// Runs the attack and returns damage dealt to the 250-HP sponge.
fn attack_damage(game: &mut Game<'static>, attacker: CardId) -> u32 {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker, 0),
        is_stack: false,
    });
    let state = game.get_state_clone();
    250 - state.get_active(1).get_remaining_hp()
}

/// Farigiraf (B3a 058) "Double Hit": flip 2 coins, 60 damage for each heads. The printed 60 is
/// REPLACED by the flip total, so 0 heads must deal 0, not 60.
#[test]
fn test_farigiraf_double_hit_damage_is_per_heads_only() {
    let farigiraf = || {
        PlayedCard::from_id(CardId::B3a058Farigiraf)
            .with_energy(vec![EnergyType::Colorless, EnergyType::Colorless])
    };
    let mut seen = [false; 3];
    for seed in 0..80 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![farigiraf()], vec![sponge(250)]);
        let damage = attack_damage(&mut game, CardId::B3a058Farigiraf);
        match damage {
            0 => seen[0] = true,
            60 => seen[1] = true,
            120 => seen[2] = true,
            other => panic!("seed {seed}: Double Hit dealt {other}, expected 0/60/120"),
        }
    }
    assert_eq!(
        seen, [true; 3],
        "all of 0, 60 and 120 damage must occur across seeds"
    );
}

/// Druddigon (B1 176) "Giga Claw": 120 damage; flip 2 coins, if BOTH are tails the attack does
/// nothing. Damage never scales — it is all (120) or nothing (0).
#[test]
fn test_druddigon_giga_claw_all_or_nothing_on_double_tails() {
    let druddigon = || {
        PlayedCard::from_id(CardId::B1176Druddigon).with_energy(vec![
            EnergyType::Fire,
            EnergyType::Water,
            EnergyType::Colorless,
            EnergyType::Colorless,
        ])
    };
    let (mut saw_hit, mut saw_nothing) = (false, false);
    for seed in 0..120 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![druddigon()], vec![sponge(250)]);
        let damage = attack_damage(&mut game, CardId::B1176Druddigon);
        match damage {
            120 => saw_hit = true,
            0 => saw_nothing = true,
            other => panic!("seed {seed}: Giga Claw dealt {other}, expected 0 or 120"),
        }
    }
    assert!(saw_hit, "at least one heads must deal the full 120");
    assert!(saw_nothing, "double tails must deal 0 (1/4 of seeds)");
}

/// Croagunk (A2 107) "Group Beatdown": flip a coin for each Pokémon you have in play,
/// 20 damage per heads.
#[test]
fn test_croagunk_group_beatdown_scales_with_pokemon_in_play() {
    let croagunk = || {
        PlayedCard::from_id(CardId::A2107Croagunk)
            .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])
    };

    // With 3 Pokémon in play (active + 2 bench): damage is a multiple of 20 up to 60.
    let mut max_seen = 0;
    for seed in 0..80 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                croagunk(),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
            vec![sponge(250)],
        );
        let damage = attack_damage(&mut game, CardId::A2107Croagunk);
        assert!(
            damage % 20 == 0 && damage <= 60,
            "seed {seed}: with 3 Pokémon in play damage must be 0/20/40/60, got {damage}"
        );
        max_seen = max_seen.max(damage);
    }
    assert_eq!(max_seen, 60, "3 heads (3 Pokémon in play) must occur");

    // Negative: with only the active in play there is exactly 1 coin — never more than 20.
    let mut max_solo = 0;
    for seed in 0..60 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![croagunk()], vec![sponge(250)]);
        let damage = attack_damage(&mut game, CardId::A2107Croagunk);
        assert!(
            damage == 0 || damage == 20,
            "seed {seed}: with 1 Pokémon in play damage must be 0 or 20, got {damage}"
        );
        max_solo = max_solo.max(damage);
    }
    assert_eq!(max_solo, 20);
}

/// Toxicroak (A2 108) shares the template at 40 per heads; forced heads with a lone attacker
/// deals exactly 40.
#[test]
fn test_toxicroak_group_beatdown_forced_heads() {
    let toxicroak = PlayedCard::from_id(CardId::A2108Toxicroak)
        .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness]);
    let mut game = get_initialized_game_with_board(0, 0, 3, vec![toxicroak], vec![sponge(250)]);
    play_will(&mut game);
    let damage = attack_damage(&mut game, CardId::A2108Toxicroak);
    assert_eq!(damage, 40, "1 Pokémon in play + forced heads = exactly 40");
}

/// Maushold (B2 143) "Family Beatdown": flip a coin for each Tandemaus and Maushold you have in
/// play, 60 damage per heads. Other Pokémon must NOT add coins.
#[test]
fn test_maushold_family_beatdown_counts_only_tandemaus_and_maushold() {
    let maushold =
        || PlayedCard::from_id(CardId::B2143Maushold).with_energy(vec![EnergyType::Colorless]);
    let mut max_seen = 0;
    for seed in 0..120 {
        let mut game = get_initialized_game_with_board(
            seed,
            0,
            3,
            vec![
                maushold(),
                PlayedCard::from_id(CardId::B2142Tandemaus),
                PlayedCard::from_id(CardId::A1001Bulbasaur),
            ],
            vec![sponge(250)],
        );
        let damage = attack_damage(&mut game, CardId::B2143Maushold);
        assert!(
            damage % 60 == 0 && damage <= 120,
            "seed {seed}: Maushold + Tandemaus = 2 coins, damage must be 0/60/120, got {damage} (Bulbasaur must not count)"
        );
        max_seen = max_seen.max(damage);
    }
    assert_eq!(max_seen, 120, "2 heads must occur across seeds");
}

/// Ambipom (B1 186) "Excited Tail": flip 2 coins, 30 per heads — but 4 coins if this Pokémon has
/// Lucky Mittens attached.
#[test]
fn test_ambipom_excited_tail_lucky_mittens_doubles_the_coins() {
    let ambipom =
        || PlayedCard::from_id(CardId::B1186Ambipom).with_energy(vec![EnergyType::Darkness]);

    // Without the tool: 2 coins, max 60.
    let mut max_plain = 0;
    for seed in 0..120 {
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![ambipom()], vec![sponge(250)]);
        let damage = attack_damage(&mut game, CardId::B1186Ambipom);
        assert!(
            damage % 30 == 0 && damage <= 60,
            "seed {seed}: without Lucky Mittens damage must be 0/30/60, got {damage}"
        );
        max_plain = max_plain.max(damage);
    }
    assert_eq!(max_plain, 60);

    // With Lucky Mittens: 4 coins, so some seed must exceed 60 and 120 must be reachable.
    let mut max_boosted = 0;
    for seed in 0..200 {
        let with_tool = ambipom().with_tool(get_card_by_enum(CardId::B1220LuckyMittens));
        let mut game =
            get_initialized_game_with_board(seed, 0, 3, vec![with_tool], vec![sponge(250)]);
        let damage = attack_damage(&mut game, CardId::B1186Ambipom);
        assert!(
            damage % 30 == 0 && damage <= 120,
            "seed {seed}: with Lucky Mittens damage must be a multiple of 30 up to 120, got {damage}"
        );
        max_boosted = max_boosted.max(damage);
    }
    assert_eq!(
        max_boosted, 120,
        "4 heads (120) must be reachable with Lucky Mittens attached"
    );
}
