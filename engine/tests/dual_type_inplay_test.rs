//! Dual Fusion prep, step 1 (in-play bypass sites and attack sites): a card's printed type SET.
//!
//! Every test builds a synthetic dual-type card (not one of the 7 Dual Fusion printings) by
//! cloning a real card and setting `secondary_energy_type`. Each routed site has two tests:
//! - `*_second_type`: only the synthetic card's SECOND printed type triggers the effect (this
//!   fails on main's single-type code);
//! - `*_single_type_control`: the same board with the unmodified single-type card behaves as on
//!   main.
//!
//! The last section (Dual Fusion release checklist item 11) is about the real Urshifu, whose
//! Double Type Ability changes its type in play: the sites now read it through
//! `State::pokemon_is_type`. Its synthetic cards change the *printed* type and keep the Ability.

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
    Game,
};

/// Mega Latios ex (P-B 024): printed [N], no Weakness, no Ability, 180 HP. A neutral defender.
const MEGA_LATIOS_EX_HP: u32 = 180;
const VENUSAUR_EX_HP: u32 = 190;

/// `id` with `second` as its second printed type (a synthetic dual-type card).
fn dual_type_card(id: CardId, second: EnergyType) -> Card {
    let Card::Pokemon(mut pokemon) = get_card_by_enum(id) else {
        panic!("a dual-type card must be cloned from a Pokémon card");
    };
    pokemon.secondary_energy_type = Some(second);
    Card::Pokemon(pokemon)
}

fn dual(id: CardId, second: EnergyType) -> PlayedCard {
    PlayedCard::from_card(&dual_type_card(id, second))
}

/// A Basic [R] Charmander with `second` as its second printed type and one `second` Energy.
fn dual_charmander(second: EnergyType) -> PlayedCard {
    dual(CardId::A1033Charmander, second).with_energy(vec![second])
}

/// The unmodified [R] Charmander with one `energy` Energy.
fn charmander_with(energy: EnergyType) -> PlayedCard {
    PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![energy])
}

fn legal_simple_actions(game: &Game) -> Vec<SimpleAction> {
    let (_actor, actions) = game.get_state_clone().generate_possible_actions();
    actions.into_iter().map(|action| action.action).collect()
}

fn use_ability(game: &mut Game, in_play_idx: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx },
        is_stack: false,
    });
}

fn ability_offered(game: &Game, in_play_idx: usize) -> bool {
    legal_simple_actions(game).contains(&SimpleAction::UseAbility { in_play_idx })
}

fn attack_offered(game: &Game) -> bool {
    legal_simple_actions(game)
        .iter()
        .any(|action| matches!(action, SimpleAction::Attack(_)))
}

fn end_turn(game: &mut Game, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
}

/// The damage player 0's Active `attacker` (card `attacker_id`, attack 0) does to player 1's
/// Active, with `discard` as player 0's discard pile and `top_of_deck` (if any) on top of player
/// 0's deck.
fn attack_damage(
    attacker_id: CardId,
    attacker: PlayedCard,
    opponent_board: Vec<PlayedCard>,
    discard: Vec<Card>,
    top_of_deck: Option<Card>,
) -> u32 {
    let mut game = get_initialized_game_with_board(0, 0, 3, vec![attacker], opponent_board);
    let mut state = game.get_state_clone();
    state.discard_piles[0] = discard;
    if let Some(card) = top_of_deck {
        state.decks[0].cards.insert(0, card);
    }
    game.set_state(state);
    let before = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(attacker_id, 0),
        is_stack: false,
    });
    before - game.get_state_clone().get_active(1).get_remaining_hp()
}

// ---- PlayedCard::has_printed_type (state/played_card.rs), the printed-set helper. Of the in-play
// sites only Leaf Cape still uses it; the others ask `State::pokemon_is_type`, which counts a
// printed dual-type card the same way.

#[test]
fn played_card_has_printed_type_second_type() {
    let pokemon = dual(CardId::A1001Bulbasaur, EnergyType::Darkness);
    assert!(pokemon.has_printed_type(EnergyType::Grass));
    assert!(pokemon.has_printed_type(EnergyType::Darkness));
    assert!(!pokemon.has_printed_type(EnergyType::Fire));
}

#[test]
fn played_card_has_printed_type_single_type_control() {
    let pokemon = PlayedCard::from_id(CardId::A1001Bulbasaur);
    assert!(pokemon.has_printed_type(EnergyType::Grass));
    assert!(!pokemon.has_printed_type(EnergyType::Darkness));
    // A Fossil plays "as if it were a Basic [C] Pokémon" but has no printed type, as on main.
    let fossil = PlayedCard::from_id(CardId::A1216HelixFossil);
    assert!(!fossil.has_printed_type(EnergyType::Colorless));
}

// ---- Leaf Cape, +30 HP for a [G] holder (state/played_card.rs, get_effective_total_hp).

#[test]
fn leaf_cape_hp_second_type() {
    let holder = dual(CardId::PB024MegaLatiosEx, EnergyType::Grass)
        .with_tool(get_card_by_enum(CardId::A3147LeafCape));
    assert_eq!(holder.get_remaining_hp(), MEGA_LATIOS_EX_HP + 30);
}

#[test]
fn leaf_cape_hp_single_type_control() {
    let leaf_cape = get_card_by_enum(CardId::A3147LeafCape);
    let dragon = PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_tool(leaf_cape.clone());
    assert_eq!(dragon.get_remaining_hp(), MEGA_LATIOS_EX_HP);
    let grass = PlayedCard::from_id(CardId::A1001Bulbasaur).with_tool(leaf_cape);
    assert_eq!(grass.get_remaining_hp(), 70 + 30);
}

// ---- Jungle Totem, each [G] Energy on a [G] Pokémon counts twice (state/played_card.rs,
// has_double_grass). Shaymin's Flap costs [C][C], so one [G] pays it only when doubled.

#[test]
fn jungle_totem_second_type() {
    let game = get_test_game_with_board(
        vec![
            dual(CardId::A2a081Shaymin, EnergyType::Grass).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1a006Serperior),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    assert!(attack_offered(&game));
}

#[test]
fn jungle_totem_single_type_control() {
    // A [C] Shaymin's one [G] is not doubled ...
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A2a081Shaymin).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1a006Serperior),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    assert!(!attack_offered(&game));
    // ... while a [G] Bulbasaur's is: one [G] pays Vine Whip's [G][C].
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur).with_energy(vec![EnergyType::Grass]),
            PlayedCard::from_id(CardId::A1a006Serperior),
        ],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    assert!(attack_offered(&game));
}

// ---- Deceptive Needle, 10 damage at the end of your turn from a [D] Active (hooks/core.rs,
// apply_deceptive_needle_damage).

fn deceptive_needle_damage(holder: PlayedCard) -> u32 {
    let holder = holder.with_tool(get_card_by_enum(CardId::B4148DeceptiveNeedle));
    let mut game = get_test_game_with_board(
        vec![holder],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    let before = game.get_state_clone().get_remaining_hp(1, 0);
    end_turn(&mut game, 0);
    before - game.get_state_clone().get_remaining_hp(1, 0)
}

#[test]
fn deceptive_needle_second_type() {
    let holder = dual(CardId::A1001Bulbasaur, EnergyType::Darkness);
    assert_eq!(deceptive_needle_damage(holder), 10);
}

#[test]
fn deceptive_needle_single_type_control() {
    let holder = PlayedCard::from_id(CardId::A1001Bulbasaur);
    assert_eq!(deceptive_needle_damage(holder), 0);
}

// ---- Vespiquen ex's Chase Order, may discard 1 Benched Basic [G] for 70 more
// (apply_attack_action.rs, benched_basic_indices_of_type).

fn chase_order_game(benched: PlayedCard) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::B4011VespiquenEx)
                .with_energy(vec![EnergyType::Grass, EnergyType::Grass]),
            benched,
        ],
        vec![PlayedCard::from_id(CardId::A1004VenusaurEx)],
    );
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::B4011VespiquenEx, 0),
        is_stack: false,
    });
    game
}

fn chase_order_discard_offered(game: &Game) -> bool {
    let discard = SimpleAction::DiscardOwnBenchedThenDamage {
        in_play_idxs: vec![1],
        damage: 70 + 70,
    };
    legal_simple_actions(game).contains(&discard)
}

#[test]
fn chase_order_bench_basic_second_type() {
    let game = chase_order_game(dual(CardId::A1033Charmander, EnergyType::Grass));
    assert!(chase_order_discard_offered(&game));
}

#[test]
fn chase_order_bench_basic_single_type_control() {
    let game = chase_order_game(PlayedCard::from_id(CardId::A1033Charmander));
    assert!(!chase_order_discard_offered(&game));
    let state = game.get_state_clone();
    assert_eq!(state.get_active(1).get_remaining_hp(), VENUSAUR_EX_HP - 70);
    assert!(state.in_play_pokemon[0][1].is_some());
}

// ---- Sealeo's Frozen Splash, 70 more if the defender is a [F] Pokémon (apply_attack_action.rs,
// extra_damage_if_defender_type: upstream #374's site).

fn frozen_splash_damage(defender: PlayedCard) -> u32 {
    attack_damage(
        CardId::B4039Sealeo,
        PlayedCard::from_id(CardId::B4039Sealeo).with_energy(vec![EnergyType::Water; 3]),
        vec![defender],
        vec![],
        None,
    )
}

#[test]
fn defender_type_bonus_second_type() {
    let defender = dual(CardId::PB024MegaLatiosEx, EnergyType::Fighting);
    assert_eq!(frozen_splash_damage(defender), 50 + 70);
}

#[test]
fn defender_type_bonus_single_type_control() {
    let defender = PlayedCard::from_id(CardId::PB024MegaLatiosEx);
    assert_eq!(frozen_splash_damage(defender), 50);
}

// ---- Bronzong's Psychic Resonance, 50 more if the opponent has any [P] Pokémon in play
// (apply_attack_action.rs, extra_damage_if_opponent_has_type_in_play).

fn psychic_resonance_damage(opponent_bench: PlayedCard) -> u32 {
    attack_damage(
        CardId::B3118Bronzong,
        PlayedCard::from_id(CardId::B3118Bronzong).with_energy(vec![EnergyType::Metal; 2]),
        vec![
            PlayedCard::from_id(CardId::PB024MegaLatiosEx),
            opponent_bench,
        ],
        vec![],
        None,
    )
}

#[test]
fn opponent_type_in_play_second_type() {
    let benched = dual(CardId::A1001Bulbasaur, EnergyType::Psychic);
    assert_eq!(psychic_resonance_damage(benched), 50 + 50);
}

#[test]
fn opponent_type_in_play_single_type_control() {
    let bulbasaur = PlayedCard::from_id(CardId::A1001Bulbasaur);
    assert_eq!(psychic_resonance_damage(bulbasaur), 50);
    let abra = PlayedCard::from_id(CardId::A1115Abra);
    assert_eq!(psychic_resonance_damage(abra), 50 + 50);
}

// ---- Dugtrio's Cliff Crumbler, 60 more if the discarded top card is a [F] Pokémon
// (apply_attack_action.rs, discard_top_self_deck_extra_damage_if_type; a card off the board).

fn cliff_crumbler_damage(top_card: Card) -> u32 {
    attack_damage(
        CardId::A4a041Dugtrio,
        PlayedCard::from_id(CardId::A4a041Dugtrio).with_energy(vec![EnergyType::Fighting]),
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
        vec![],
        Some(top_card),
    )
}

#[test]
fn cliff_crumbler_top_card_second_type() {
    let top = dual_type_card(CardId::A1001Bulbasaur, EnergyType::Fighting);
    assert_eq!(cliff_crumbler_damage(top), 40 + 60);
}

#[test]
fn cliff_crumbler_top_card_single_type_control() {
    let bulbasaur = get_card_by_enum(CardId::A1001Bulbasaur);
    assert_eq!(cliff_crumbler_damage(bulbasaur), 40);
}

// ---- Houndstone's Last Respects, 20 more per [P] Pokémon in your discard pile
// (apply_attack_action.rs, extra_damage_per_pokemon_type_in_discard_attack; cards off the board).

fn last_respects_damage(discard: Vec<Card>) -> u32 {
    attack_damage(
        CardId::B2a053Houndstone,
        PlayedCard::from_id(CardId::B2a053Houndstone).with_energy(vec![EnergyType::Psychic; 2]),
        vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)],
        discard,
        None,
    )
}

#[test]
fn discard_type_count_second_type() {
    let discard = vec![dual_type_card(CardId::A1001Bulbasaur, EnergyType::Psychic)];
    assert_eq!(last_respects_damage(discard), 50 + 20);
}

#[test]
fn discard_type_count_single_type_control() {
    let discard = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1115Abra),
    ];
    assert_eq!(last_respects_damage(discard), 50 + 20);
}

// ---- Leafeon ex's Forest Breath, a [G] Energy from the Zone to 1 of your [G] Pokémon
// (apply_abilities_action.rs, attach_energy_from_zone_to_your_typed_outcome).

fn forest_breath_game(benched: PlayedCard) -> Game<'static> {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A2a010LeafeonEx), benched],
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
    );
    use_ability(&mut game, 0);
    game
}

fn forest_breath_offers(game: &Game, in_play_idx: usize) -> bool {
    let attach = SimpleAction::Attach {
        attachments: vec![(1, EnergyType::Grass, in_play_idx)],
        is_turn_energy: false,
    };
    legal_simple_actions(game).contains(&attach)
}

#[test]
fn forest_breath_target_second_type() {
    let game = forest_breath_game(dual(CardId::A1033Charmander, EnergyType::Grass));
    assert!(forest_breath_offers(&game, 0));
    assert!(forest_breath_offers(&game, 1));
}

#[test]
fn forest_breath_target_single_type_control() {
    let game = forest_breath_game(PlayedCard::from_id(CardId::A1033Charmander));
    assert!(forest_breath_offers(&game, 0));
    assert!(!forest_breath_offers(&game, 1));
}

// ---- Lunala ex's Psychic Connect, all [P] Energy from 1 of your Benched [P] Pokémon to the
// Active: legality (move_generation_abilities.rs, has_benched_typed_pokemon_with_typed_energy) and
// the offered sources (apply_abilities_action.rs, move_all_typed_energy_from_bench_to_active).

fn psychic_connect_game(bench: Vec<PlayedCard>) -> Game<'static> {
    let mut board = vec![
        PlayedCard::from_id(CardId::A1001Bulbasaur),
        PlayedCard::from_id(CardId::A3087LunalaEx),
    ];
    board.extend(bench);
    get_test_game_with_board(board, vec![PlayedCard::from_id(CardId::A1002Ivysaur)])
}

fn psychic_connect_offers(game: &Game, from_in_play_idx: usize) -> bool {
    let move_energy = SimpleAction::MoveEnergy {
        from_in_play_idx,
        to_in_play_idx: 0,
        energy_type: EnergyType::Psychic,
        amount: 1,
    };
    legal_simple_actions(game).contains(&move_energy)
}

#[test]
fn psychic_connect_legality_second_type() {
    // The synthetic [R]/[P] Charmander is the only Benched source.
    let game = psychic_connect_game(vec![dual_charmander(EnergyType::Psychic)]);
    assert!(ability_offered(&game, 1));
}

#[test]
fn psychic_connect_legality_single_type_control() {
    let game = psychic_connect_game(vec![charmander_with(EnergyType::Psychic)]);
    assert!(!ability_offered(&game, 1));
}

#[test]
fn psychic_connect_source_second_type() {
    // Abra (idx 2) makes the Ability legal by itself, so only the source filter is tested.
    let mut game = psychic_connect_game(vec![
        PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Psychic]),
        dual_charmander(EnergyType::Psychic),
    ]);
    use_ability(&mut game, 1);
    assert!(psychic_connect_offers(&game, 2));
    assert!(psychic_connect_offers(&game, 3));
}

#[test]
fn psychic_connect_source_single_type_control() {
    let mut game = psychic_connect_game(vec![
        PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Psychic]),
        charmander_with(EnergyType::Psychic),
    ]);
    use_ability(&mut game, 1);
    assert!(psychic_connect_offers(&game, 2));
    assert!(!psychic_connect_offers(&game, 3));
}

// ---- Vaporeon's Wash Out, a [W] Energy from 1 of your Benched [W] Pokémon to your Active [W]:
// legality (move_generation_abilities.rs, can_use_vaporeon_wash_out_inner) and the bounded
// candidates' sources (energy_moves.rs, eligible_sources). Its unbounded path
// (apply_abilities_action.rs, vaporeon_wash_out) runs only under DECKGYM_UNBOUNDED_ENERGY_MOVES=1
// and is not tested here.

fn wash_out_game(bench: Vec<PlayedCard>) -> Game<'static> {
    let mut board = vec![
        PlayedCard::from_id(CardId::A1053Squirtle),
        PlayedCard::from_id(CardId::A1a019Vaporeon),
    ];
    board.extend(bench);
    get_test_game_with_board(board, vec![PlayedCard::from_id(CardId::A1001Bulbasaur)])
}

/// Whether the bounded candidates include the RESCUE move that empties `from_in_play_idx`'s [W]
/// onto the Active (offered for every eligible source; `actions::energy_moves`).
fn wash_out_offers(game: &Game, from_in_play_idx: usize) -> bool {
    let rescue = SimpleAction::ConsolidateEnergyToPokemon {
        to_in_play_idx: 0,
        transfers: vec![(from_in_play_idx, vec![EnergyType::Water])],
    };
    legal_simple_actions(game).contains(&rescue)
}

#[test]
fn wash_out_legality_second_type() {
    // The synthetic [R]/[W] Charmander is the only Benched source.
    let game = wash_out_game(vec![dual_charmander(EnergyType::Water)]);
    assert!(ability_offered(&game, 1));
}

#[test]
fn wash_out_legality_single_type_control() {
    let game = wash_out_game(vec![charmander_with(EnergyType::Water)]);
    assert!(!ability_offered(&game, 1));
}

#[test]
fn wash_out_bounded_source_second_type() {
    // Blastoise (idx 2) makes the Ability legal by itself, so only the source filter is tested.
    let mut game = wash_out_game(vec![
        PlayedCard::from_id(CardId::A1055Blastoise).with_energy(vec![EnergyType::Water]),
        dual_charmander(EnergyType::Water),
    ]);
    use_ability(&mut game, 1);
    assert!(wash_out_offers(&game, 2));
    assert!(wash_out_offers(&game, 3));
}

#[test]
fn wash_out_bounded_source_single_type_control() {
    let mut game = wash_out_game(vec![
        PlayedCard::from_id(CardId::A1055Blastoise).with_energy(vec![EnergyType::Water]),
        charmander_with(EnergyType::Water),
    ]);
    use_ability(&mut game, 1);
    assert!(wash_out_offers(&game, 2));
    assert!(!wash_out_offers(&game, 3));
}

// ---- Urshifu's Double Type at the in-play sites (Dual Fusion release checklist item 11).
// Rapid Strike Urshifu (B3 051) is printed [W]: "As long as this Pokémon is in play, it is [W] and
// [F] type." Single Strike Urshifu (B3 113) is printed [D]: "... it is [F] and [D] type." Each is
// [F] only in play and only while its Ability is on. Before item 11 these sites read the printed
// set and missed it.

const URSHIFU: [CardId; 2] = [
    CardId::B3051RapidStrikeUrshifu,
    CardId::B3113SingleStrikeUrshifu,
];

/// `pokemon` with Prickly Powder's `NoAbilities` on it (Budew B3 013: "The Defending Pokémon loses
/// all Abilities."), so its Double Type is off.
fn switched_off(mut pokemon: PlayedCard) -> PlayedCard {
    pokemon.add_effect(CardEffect::NoAbilities, 1);
    pokemon
}

/// `id` with `printed` as its only printed type, in place of the real one. The Ability stays.
fn printed_as(id: CardId, printed: EnergyType) -> PlayedCard {
    let Card::Pokemon(mut pokemon) = get_card_by_enum(id) else {
        panic!("a retyped card must be cloned from a Pokémon card");
    };
    pokemon.energy_type = printed;
    PlayedCard::from_card(&Card::Pokemon(pokemon))
}

/// Snover's Ice Shard (A2 044), 10: "If your opponent's Active Pokémon is a [F] Pokémon, this
/// attack does 30 more damage." Both Urshifu have 120 HP and are weak to [L] (B3 051) or [G]
/// (B3 113), so the [W] attack's damage is exact.
fn ice_shard_damage(defender: PlayedCard) -> u32 {
    attack_damage(
        CardId::A2044Snover,
        PlayedCard::from_id(CardId::A2044Snover).with_energy(vec![EnergyType::Water]),
        vec![defender],
        vec![],
        None,
    )
}

/// The "+X if the defender is a [X] Pokémon" bonus (extra_damage_if_defender_type): Double Type
/// makes the Active Urshifu a [F] Pokémon.
#[test]
fn defender_type_bonus_double_type() {
    for id in URSHIFU {
        assert_eq!(ice_shard_damage(PlayedCard::from_id(id)), 10 + 30, "{id:?}");
    }
}

/// With its Ability off, each Urshifu is only its printed [W] / [D]: no bonus.
#[test]
fn defender_type_bonus_double_type_switched_off() {
    for id in URSHIFU {
        assert_eq!(ice_shard_damage(switched_off(PlayedCard::from_id(id))), 10, "{id:?}");
    }
}

/// The "if your opponent has any [X] Pokémon in play" bonus
/// (extra_damage_if_opponent_has_type_in_play) reads a Benched Pokémon's in-play type. Its one
/// card, Bronzong's Psychic Resonance, asks for [P], which Double Type never gives, so the real
/// Urshifu change nothing there. A synthetic Rapid Strike Urshifu printed [P] shows the read: in
/// play it "is [W] and [F] type" (Double Type replaces the printed type, as
/// `State::pokemon_energy_types` reads it), so it is a [P] Pokémon only with its Ability off.
#[test]
fn opponent_type_in_play_benched_double_type() {
    for id in URSHIFU {
        assert_eq!(psychic_resonance_damage(PlayedCard::from_id(id)), 50, "{id:?}");
    }
    let psychic = printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Psychic);
    assert_eq!(psychic_resonance_damage(psychic.clone()), 50);
    assert_eq!(psychic_resonance_damage(switched_off(psychic)), 50 + 50);
}

/// An own-side site, Deceptive Needle on the Active (hooks/core.rs, apply_deceptive_needle_damage).
/// Single Strike Urshifu is still [D] in play (its Double Type pair includes the printed [D]) and
/// Rapid Strike Urshifu is never [D]. For the real cards no own-side site changes: those sites ask
/// [G], [P], [W] or [D], and Double Type only adds [F]. A synthetic Single Strike Urshifu printed
/// [W] would have done no damage before item 11: in play it is [F] and [D].
#[test]
fn deceptive_needle_double_type() {
    let single_strike = PlayedCard::from_id(CardId::B3113SingleStrikeUrshifu);
    assert_eq!(deceptive_needle_damage(single_strike), 10);
    let rapid_strike = PlayedCard::from_id(CardId::B3051RapidStrikeUrshifu);
    assert_eq!(deceptive_needle_damage(rapid_strike), 0);
    let water = printed_as(CardId::B3113SingleStrikeUrshifu, EnergyType::Water);
    assert_eq!(deceptive_needle_damage(water.clone()), 10);
    assert_eq!(deceptive_needle_damage(switched_off(water)), 0);
}

// The other routed sites. For the real Urshifu none of them changes: Wash Out asks [W], which Rapid
// Strike Urshifu is printed anyway, and Forest Breath, Chase Order, Jungle Totem and Psychic
// Connect ask [G] or [P], which Double Type neither gives nor takes away. A synthetic Rapid Strike
// Urshifu with another printed type pins each site to the in-play read: each test fails if its
// site goes back to `has_printed_type`. The Wash Out test holds whether Double Type replaces the
// printed type or adds to it; the [G] and [P] tests rest on the replace reading, as
// `opponent_type_in_play_benched_double_type` does (see the TODO in
// `State::pokemon_energy_types`).

/// Wash Out, legality (move_generation_abilities.rs, can_use_vaporeon_wash_out_inner) and the
/// bounded sources (energy_moves.rs, eligible_sources). A Rapid Strike Urshifu printed [R] is [W]
/// in play, so it is a Benched [W] source; with its Ability off it is not.
#[test]
fn wash_out_source_double_type() {
    let fire = || {
        printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Fire)
            .with_energy(vec![EnergyType::Water])
    };
    // The Urshifu is the only Benched source.
    assert!(ability_offered(&wash_out_game(vec![fire()]), 1));
    assert!(!ability_offered(&wash_out_game(vec![switched_off(fire())]), 1));
    // Blastoise (idx 2) makes the Ability legal by itself, so only the source filter is tested.
    for (urshifu, is_source) in [(fire(), true), (switched_off(fire()), false)] {
        let mut game = wash_out_game(vec![
            PlayedCard::from_id(CardId::A1055Blastoise).with_energy(vec![EnergyType::Water]),
            urshifu,
        ]);
        use_ability(&mut game, 1);
        assert!(wash_out_offers(&game, 2));
        assert_eq!(wash_out_offers(&game, 3), is_source);
    }
}

/// Psychic Connect, legality (move_generation_abilities.rs,
/// has_benched_typed_pokemon_with_typed_energy) and the sources (apply_abilities_action.rs,
/// move_all_typed_energy_from_bench_to_active). A Rapid Strike Urshifu printed [P] is [W] and [F]
/// in play: a Benched [P] source only with its Ability off.
#[test]
fn psychic_connect_source_double_type() {
    let psychic = || {
        printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Psychic)
            .with_energy(vec![EnergyType::Psychic])
    };
    // The Urshifu is the only Benched source.
    assert!(!ability_offered(&psychic_connect_game(vec![psychic()]), 1));
    assert!(ability_offered(&psychic_connect_game(vec![switched_off(psychic())]), 1));
    // Abra (idx 2) makes the Ability legal by itself, so only the source filter is tested.
    for (urshifu, is_source) in [(psychic(), false), (switched_off(psychic()), true)] {
        let mut game = psychic_connect_game(vec![
            PlayedCard::from_id(CardId::A1115Abra).with_energy(vec![EnergyType::Psychic]),
            urshifu,
        ]);
        use_ability(&mut game, 1);
        assert!(psychic_connect_offers(&game, 2));
        assert_eq!(psychic_connect_offers(&game, 3), is_source);
    }
}

/// Forest Breath's targets (apply_abilities_action.rs,
/// attach_energy_from_zone_to_your_typed_outcome). A Rapid Strike Urshifu printed [G] is a [G]
/// Pokémon only with its Ability off.
#[test]
fn forest_breath_target_double_type() {
    let grass = || printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Grass);
    let game = forest_breath_game(grass());
    assert!(forest_breath_offers(&game, 0));
    assert!(!forest_breath_offers(&game, 1));
    let game = forest_breath_game(switched_off(grass()));
    assert!(forest_breath_offers(&game, 1));
}

/// Chase Order's Benched Basic [G] filter (apply_attack_action.rs, benched_basic_indices_of_type).
/// Both Urshifu are Stage 1, so the synthetic one printed [G] is also made a Basic.
#[test]
fn chase_order_bench_basic_double_type() {
    let basic_grass = || {
        let mut urshifu = printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Grass);
        if let Card::Pokemon(pokemon) = &mut urshifu.card {
            pokemon.stage = 0;
        }
        urshifu
    };
    assert!(!chase_order_discard_offered(&chase_order_game(basic_grass())));
    assert!(chase_order_discard_offered(&chase_order_game(switched_off(basic_grass()))));
}

/// Jungle Totem (state/played_card.rs, has_double_grass), read through the Retreat Cost: Urshifu's
/// [C][C][C] is paid by two [G] Energy only when each provides 2. A Rapid Strike Urshifu printed
/// [G] is a [G] Pokémon only with its Ability off.
#[test]
fn jungle_totem_double_type() {
    let grass = || {
        printed_as(CardId::B3051RapidStrikeUrshifu, EnergyType::Grass)
            .with_energy(vec![EnergyType::Grass; 2])
    };
    for (urshifu, doubled) in [(grass(), false), (switched_off(grass()), true)] {
        let game = get_test_game_with_board(
            vec![urshifu, PlayedCard::from_id(CardId::A1a006Serperior)],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        );
        let retreat_offered = legal_simple_actions(&game).contains(&SimpleAction::Retreat(1));
        assert_eq!(retreat_offered, doubled);
    }
}
