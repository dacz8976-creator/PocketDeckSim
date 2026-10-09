use std::collections::BTreeSet;

use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{EnergyType, PlayedCard},
    test_support::get_initialized_game,
    Game, State,
};

fn setup(seed: u64) -> Game<'static> {
    let mut game = get_initialized_game(seed);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.current_player = 0;
    state.turn_count = 3;
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    game.set_state(state);
    game
}

fn offered_play(state: &State, wanted: CardId) -> Option<Action> {
    let wanted = get_card_by_enum(wanted).get_id();
    state.generate_possible_actions().1.into_iter().find(|action| {
        matches!(&action.action, SimpleAction::Play { trainer_card } if trainer_card.id == wanted)
    })
}

fn play(game: &mut Game<'static>, wanted: CardId) {
    let action = offered_play(&game.get_state_clone(), wanted)
        .unwrap_or_else(|| panic!("{} should be offered", get_card_by_enum(wanted).get_name()));
    game.apply_action(&action);
}

fn evolution_target_actions(state: &State) -> Vec<Action> {
    state
        .generate_possible_actions()
        .1
        .into_iter()
        .filter(|action| {
            matches!(
                action.action,
                SimpleAction::ChooseRandomEvolutionTarget { .. }
            )
        })
        .collect()
}

#[test]
fn mythical_slab_keeps_any_stage_psychic_and_bottoms_a_non_psychic_basic() {
    let slab = get_card_by_enum(CardId::A1a065MythicalSlab);
    let psychic_stage_one = get_card_by_enum(CardId::A1116Kadabra);
    let non_psychic_basic = get_card_by_enum(CardId::A1033Charmander);

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![slab.clone()];
    state.decks[0].cards = vec![psychic_stage_one.clone(), non_psychic_basic.clone()];
    game.set_state(state);
    play(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![psychic_stage_one]);
    assert_eq!(state.decks[0].cards, vec![non_psychic_basic.clone()]);

    let mut game = setup(1);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![slab];
    state.decks[0].cards = vec![
        non_psychic_basic.clone(),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    game.set_state(state);
    play(&mut game, CardId::A1a065MythicalSlab);
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards.last(), Some(&non_psychic_basic));
}

#[test]
fn stadium_play_limit_is_separate_from_using_the_stadium() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::B2a093Mesagoza),
        get_card_by_enum(CardId::B2153TrainingArea),
    ];
    state.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion)];
    game.set_state(state);

    play(&mut game, CardId::B2a093Mesagoza);
    let after_play = game.get_state_clone();
    let actions = after_play.generate_possible_actions().1;
    assert!(actions
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));
    assert!(offered_play(&after_play, CardId::B2153TrainingArea).is_none());

    let use_action = actions
        .into_iter()
        .find(|action| matches!(action.action, SimpleAction::UseStadium))
        .expect("newly played Mesagoza should still be usable");
    game.apply_action(&use_action);
    assert!(offered_play(&game.get_state_clone(), CardId::B2153TrainingArea).is_none());
}

#[test]
fn hidden_deck_contents_do_not_block_searches_but_an_empty_deck_does() {
    let nonmatching = get_card_by_enum(CardId::PA001Potion);
    for id in [
        CardId::A3a067Gladion,
        CardId::A2151TeamGalacticGrunt,
        CardId::B3150Cabbie,
        CardId::B1a068Clemont,
        CardId::B1a069Serena,
        CardId::B3a071Juliana,
        CardId::B4145OrderPad,
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(id)];
        state.decks[0].cards = vec![nonmatching.clone()];
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_some(),
            "{} should be legal against a nonempty hidden deck",
            get_card_by_enum(id).get_name()
        );

        let mut state = game.get_state_clone();
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_none(),
            "{} should be blocked by a visibly empty deck",
            get_card_by_enum(id).get_name()
        );
    }

    let mut game = setup(1);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![
        get_card_by_enum(CardId::A2146PokemonCommunication),
        get_card_by_enum(CardId::A1001Bulbasaur),
    ];
    state.decks[0].cards = vec![nonmatching];
    game.set_state(state);
    assert!(offered_play(&game.get_state_clone(), CardId::A2146PokemonCommunication).is_some());
}

#[test]
fn every_confirmed_deck_taking_trainer_is_blocked_when_the_deck_is_empty() {
    for id in [
        CardId::A1a065MythicalSlab,
        CardId::A4a070TravelingMerchant,
        CardId::B1223May,
        CardId::B1226Lisia,
        CardId::B2a091Arven,
        CardId::B2150Sightseer,
        CardId::B3b067PuppyLovingGirl,
        CardId::B4145OrderPad,
        CardId::B4a069TeamRocketsResearcher,
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(id)];
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(
            offered_play(&game.get_state_clone(), id).is_none(),
            "{} should be blocked by an empty deck",
            get_card_by_enum(id).get_name()
        );
    }
}

#[test]
fn stadium_searches_follow_visible_nonempty_deck_legality() {
    for stadium in [CardId::B2a093Mesagoza, CardId::B3153FragrantForest] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.set_active_stadium(get_card_by_enum(stadium));
        state.decks[0].cards = vec![get_card_by_enum(CardId::PA001Potion)];
        game.set_state(state);
        assert!(game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseStadium)));

        let mut state = game.get_state_clone();
        state.decks[0].cards.clear();
        game.set_state(state);
        assert!(!game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .iter()
            .any(|action| matches!(action.action, SimpleAction::UseStadium)));
    }

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_active_stadium(get_card_by_enum(CardId::B3b069KidsRoom));
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1033Charmander)];
    game.set_state(state);
    assert!(game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));

    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_active_stadium(get_card_by_enum(CardId::B4a072Arcade));
    state.hands[0] = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    state.decks[0].cards.clear();
    game.set_state(state);
    assert!(!game
        .get_state_clone()
        .generate_possible_actions()
        .1
        .iter()
        .any(|action| matches!(action.action, SimpleAction::UseStadium)));
}

#[test]
fn quick_grow_extract_lets_the_user_choose_the_target_before_random_evolution() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.set_board(
        vec![
            PlayedCard::from_id(CardId::A1001Bulbasaur),
            PlayedCard::from_id(CardId::A2b005Sprigatito),
        ],
        vec![PlayedCard::from_id(CardId::A1033Charmander)],
    );
    state.hands[0] = vec![get_card_by_enum(CardId::B1a067QuickGrowExtract)];
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::A1002Ivysaur),
        get_card_by_enum(CardId::A2b006Floragato),
    ];
    game.set_state(state);

    play(&mut game, CardId::B1a067QuickGrowExtract);
    let choices = evolution_target_actions(&game.get_state_clone());
    assert_eq!(choices.len(), 2);
    assert_eq!(game.get_state_clone().get_active(0).get_name(), "Bulbasaur");

    let choose_bench = choices
        .into_iter()
        .find(|action| {
            matches!(
                action.action,
                SimpleAction::ChooseRandomEvolutionTarget { in_play_idx: 1, .. }
            )
        })
        .expect("Sprigatito should be a separate player choice");
    game.apply_action(&choose_bench);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).get_name(), "Bulbasaur");
    assert_eq!(
        state.in_play_pokemon[0][1].as_ref().unwrap().get_name(),
        "Floragato"
    );
}

#[test]
fn wallace_uses_effective_max_hp_and_randomizes_only_after_target_choice() {
    let mut seen = BTreeSet::new();
    for seed in 0..64 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::A1074Staryu)
                    .with_tool(get_card_by_enum(CardId::A2147GiantCape)),
                PlayedCard::from_id(CardId::A1077Magikarp),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        state.hands[0] = vec![get_card_by_enum(CardId::B3b068Wallace)];
        state.decks[0].cards = vec![
            get_card_by_enum(CardId::A1078Gyarados),
            get_card_by_enum(CardId::A1a018GyaradosEx),
            get_card_by_enum(CardId::A1075Starmie),
        ];
        game.set_state(state);

        play(&mut game, CardId::B3b068Wallace);
        let choices = evolution_target_actions(&game.get_state_clone());
        assert_eq!(choices.len(), 1, "Giant Cape makes Staryu's maximum HP 70");
        assert!(matches!(
            &choices[0].action,
            SimpleAction::ChooseRandomEvolutionTarget { in_play_idx: 1, .. }
        ));
        game.apply_action(&choices[0]);
        let evolved = game.get_state_clone().in_play_pokemon[0][1]
            .as_ref()
            .unwrap()
            .card
            .get_id();
        seen.insert(evolved);
    }
    assert_eq!(
        seen.len(),
        2,
        "Wallace should sample both eligible Magikarp evolutions, never Starmie"
    );
}

#[test]
fn piers_discards_random_energy_without_replacement() {
    let mut survivors = BTreeSet::new();
    for seed in 0..64 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.in_play_pokemon[0][1] = Some(PlayedCard::from_id(CardId::B2100GalarianObstagoon));
        state.in_play_pokemon[1][0] = Some(
            PlayedCard::from_id(CardId::A1033Charmander).with_energy(vec![
                EnergyType::Fire,
                EnergyType::Water,
                EnergyType::Lightning,
            ]),
        );
        state.hands[0] = vec![get_card_by_enum(CardId::B2152Piers)];
        game.set_state(state);
        play(&mut game, CardId::B2152Piers);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(1).attached_energy.len(), 1);
        assert_eq!(state.discard_energies[1].len(), 2);
        survivors.insert(state.get_active(1).attached_energy[0]);
    }
    assert!(
        survivors.len() > 1,
        "Piers must not always discard the last two Energy"
    );
}

#[test]
fn healing_trainers_offer_only_damaged_targets() {
    for (trainer, undamaged, damaged) in [
        (
            CardId::PA001Potion,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
        ),
        (
            CardId::A1219Erika,
            CardId::A1001Bulbasaur,
            CardId::A1001Bulbasaur,
        ),
        (
            CardId::B1221Marlon,
            CardId::B1067Carracosta,
            CardId::B1069Jellicent,
        ),
        (
            CardId::A3155Lillie,
            CardId::A1003Venusaur,
            CardId::A1003Venusaur,
        ),
    ] {
        let mut game = setup(0);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(undamaged),
                PlayedCard::from_id(damaged).with_damage(10),
            ],
            vec![PlayedCard::from_id(CardId::A1033Charmander)],
        );
        state.hands[0] = vec![get_card_by_enum(trainer)];
        game.set_state(state);

        play(&mut game, trainer);
        let heal_targets = game
            .get_state_clone()
            .generate_possible_actions()
            .1
            .into_iter()
            .filter_map(|action| match action.action {
                SimpleAction::Heal { in_play_idx, .. } => Some(in_play_idx),
                _ => None,
            })
            .collect::<Vec<_>>();
        assert_eq!(
            heal_targets,
            vec![1],
            "{} must not offer an undamaged target",
            get_card_by_enum(trainer).get_name()
        );
    }
}

/// A Fossil is an Item card (its printed type; rules/01, rules/04 §6), so an Item lock stops it (the card-text
/// follow-up, Oct 2): player 1's Chingling uses Jingly Noise ("During your opponent's next turn, they can't play any
/// Item cards from their hand."), and on player 0's turn Helix Fossil in hand can't be placed on the free Bench slots.
/// The control: player 1 ends the turn without the lock, and the Fossil can be placed.
#[test]
fn an_item_lock_stops_a_fossil() {
    use deckgym::{
        actions::{Action, SimpleAction},
        card_ids::CardId,
        database::get_card_by_enum,
        models::{Card, PlayedCard},
        test_support::{attack_action, get_initialized_game_with_board},
    };
    for locked in [false, true] {
        let mut game = get_initialized_game_with_board(
            0,
            1,
            3,
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
            vec![
                PlayedCard::from_id(CardId::B1109Chingling),
                PlayedCard::from_id(CardId::A1033Charmander),
            ],
        );
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::A1216HelixFossil), get_card_by_enum(CardId::PA005PokeBall)];
        game.set_state(state);
        if locked {
            game.apply_action(&Action { actor: 1, action: attack_action(CardId::B1109Chingling, 0), is_stack: false });
            game.play_until_stable();
        }
        let (actor, actions) = game.get_state_clone().generate_possible_actions();
        if actor == 1 {
            let end_turn = actions
                .iter()
                .find(|choice| matches!(choice.action, SimpleAction::EndTurn))
                .expect("player 1 can end the turn")
                .clone();
            game.apply_action(&end_turn);
            game.play_until_stable();
        }
        let (actor, actions) = game.get_state_clone().generate_possible_actions();
        assert_eq!(actor, 0, "locked {locked}: player 0's turn");
        let fossil = actions.iter().any(|choice| {
            matches!(&choice.action, SimpleAction::Place(Card::Trainer(card), _) if card.name == "Helix Fossil")
        });
        // The lock is in force: Poke Ball, an Item, is stopped too.
        let poke_ball = actions.iter().any(|choice| {
            matches!(&choice.action, SimpleAction::Play { trainer_card } if trainer_card.name == "Poké Ball")
        });
        assert_eq!(poke_ball, !locked, "locked {locked}: Poke Ball is playable only without the Item lock");
        assert_eq!(fossil, !locked, "locked {locked}: the Fossil can be placed only without the Item lock");
    }
}

// P3 (rules switch 2, Oct 9): a Fossil is an Item card wherever a card says "Item card" (its printed type; rules/01,
// rules/04 §6), as the Item lock above already reads it. Seven more places read an Item card and missed the Fossil; each
// test below puts Helix Fossil (A1 216) where one of them looks. Mega Latios ex (P-B 024, 180 HP, no Weakness) takes the hits.

fn fossil() -> deckgym::models::Card {
    get_card_by_enum(CardId::A1216HelixFossil)
}

/// Player 0's `attacker` (with `energy`) uses its first attack into Mega Latios ex, after `prepare` sets the state up.
fn fossil_attack(seed: u64, attacker: CardId, energy: Vec<EnergyType>, prepare: impl FnOnce(&mut State)) -> State {
    use deckgym::test_support::{attack_action, get_initialized_game_with_board};
    let board = vec![PlayedCard::from_id(attacker).with_energy(energy)];
    let mut game = get_initialized_game_with_board(seed, 0, 3, board, vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)]);
    let mut state = game.get_state_clone();
    state.hands = [vec![], vec![]];
    state.discard_piles = [vec![], vec![]];
    prepare(&mut state);
    game.set_state(state);
    game.apply_action(&Action { actor: 0, action: attack_action(attacker, 0), is_stack: false });
    game.get_state_clone()
}

/// Alolan Raticate (A3 107), Scrounge-and-Scarf: "Discard a random Item card from your opponent's hand."
#[test]
fn fossil_scrounge_and_scarf_discards_a_fossil_from_the_opponents_hand() {
    let state = fossil_attack(0, CardId::A3107AlolanRaticate, vec![EnergyType::Darkness; 2], |state| {
        state.hands[1] = vec![get_card_by_enum(CardId::A1219Erika), fossil()];
    });
    assert_eq!(state.get_active(1).get_remaining_hp(), 130);
    assert_eq!(state.discard_piles[1], vec![fossil()], "the Fossil, an Item card, is discarded");
    assert_eq!(state.hands[1], vec![get_card_by_enum(CardId::A1219Erika)]);
}

/// Team Rocket's Thieving Machine (B4a 067): "Put a random Item card, except any Team Rocket's Thieving Machine, from
/// your opponent's discard pile into your hand." With only a Fossil there, it is playable and takes the Fossil.
#[test]
fn fossil_thieving_machine_takes_a_lone_fossil() {
    let mut game = setup(0);
    let mut state = game.get_state_clone();
    state.hands[0] = vec![get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine)];
    state.discard_piles[1] = vec![get_card_by_enum(CardId::A2152Cynthia), fossil()];
    game.set_state(state);
    play(&mut game, CardId::B4a067TeamRocketsThievingMachine);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0], vec![fossil()]);
    assert_eq!(state.discard_piles[1], vec![get_card_by_enum(CardId::A2152Cynthia)]);
}

/// The same with a Potion beside the Fossil: either can be taken.
#[test]
fn fossil_thieving_machine_can_take_a_fossil_or_a_potion() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let mut taken = BTreeSet::new();
    for seed in 0..60 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(CardId::B4a067TeamRocketsThievingMachine)];
        state.discard_piles[1] = vec![potion.clone(), fossil()];
        game.set_state(state);
        play(&mut game, CardId::B4a067TeamRocketsThievingMachine);
        let state = game.get_state_clone();
        assert_eq!(state.hands[0].len(), 1, "seed {seed}: one card taken");
        taken.insert(state.hands[0][0].get_name());
    }
    assert_eq!(taken, BTreeSet::from([potion.get_name(), fossil().get_name()]), "both Item cards can be taken");
}

/// Order Pad (B4 145) and Arven (B2a 091): "Flip a coin. If heads, put a random Item card from your deck into your
/// hand." (Arven's tails looks for a Pokemon Tool, and finds none here.) A deck holding only a Fossil: heads takes it.
fn fossil_deck_search(card: CardId) {
    let (mut heads, mut tails) = (0, 0);
    for seed in 0..30 {
        let mut game = setup(seed);
        let mut state = game.get_state_clone();
        state.hands[0] = vec![get_card_by_enum(card)];
        state.decks[0].cards = vec![fossil()];
        game.set_state(state);
        play(&mut game, card);
        let state = game.get_state_clone();
        if state.hands[0] == vec![fossil()] {
            heads += 1;
            assert!(state.decks[0].cards.is_empty(), "seed {seed}: the Fossil left the deck");
        } else {
            tails += 1;
            assert!(state.hands[0].is_empty(), "seed {seed}: nothing taken on tails");
            assert_eq!(state.decks[0].cards, vec![fossil()], "seed {seed}: the Fossil stays on tails");
        }
    }
    assert!(heads > 0 && tails > 0, "both coin results seen: heads {heads}, tails {tails}");
}

#[test]
fn fossil_order_pad_finds_a_fossil_on_heads() {
    fossil_deck_search(CardId::B4145OrderPad);
}

#[test]
fn fossil_arven_finds_a_fossil_on_heads() {
    fossil_deck_search(CardId::B2a091Arven);
}

/// Rotom ex (B4 055 and its reprints), Junk Spark: "This attack does 10 more damage for each Item card in your
/// discard pile." A Fossil and a Poke Ball: 30 + 20.
#[test]
fn fossil_junk_spark_counts_a_fossil() {
    for rotom in [CardId::B4055RotomEx, CardId::B4184RotomEx, CardId::B4202RotomEx] {
        let state = fossil_attack(0, rotom, vec![EnergyType::Lightning; 2], |state| {
            state.discard_piles[0] = vec![fossil(), get_card_by_enum(CardId::PA005PokeBall)];
        });
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50, "{rotom:?}");
    }
}

/// The control: Chandelure (B2 069), Past Friends, shares Junk Spark's code but counts Supporter cards; a Fossil and a
/// Potion beside one Cynthia don't count: 60 + 20.
#[test]
fn fossil_past_friends_still_counts_only_supporters() {
    let state = fossil_attack(0, CardId::B2069Chandelure, vec![EnergyType::Psychic; 2], |state| {
        state.discard_piles[0] =
            vec![get_card_by_enum(CardId::A2152Cynthia), fossil(), get_card_by_enum(CardId::PA001Potion)];
    });
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 80);
}

/// Pachirisu (B4 054, P-B 085), Crackling Snap: "Discard the top card of your deck, and if that card is an Item, this
/// attack does 20 more damage." A Fossil on top: 30 + 20.
#[test]
fn fossil_crackling_snap_counts_a_fossil_on_top() {
    for pachirisu in [CardId::B4054Pachirisu, CardId::PB085Pachirisu] {
        let state = fossil_attack(0, pachirisu, vec![EnergyType::Lightning], |state| state.decks[0].cards.insert(0, fossil()));
        assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 50, "{pachirisu:?}");
        assert_eq!(state.discard_piles[0], vec![fossil()], "{pachirisu:?}: the top card is discarded");
    }
}

/// The control: a Supporter on top does no more damage.
#[test]
fn fossil_crackling_snap_without_an_item_on_top() {
    let cynthia = get_card_by_enum(CardId::A2152Cynthia);
    let state = fossil_attack(0, CardId::B4054Pachirisu, vec![EnergyType::Lightning], |state| {
        state.decks[0].cards.insert(0, cynthia.clone())
    });
    assert_eq!(state.get_active(1).get_remaining_hp(), 180 - 30);
    assert_eq!(state.discard_piles[0], vec![cynthia]);
}

/// Team Rocket's Slowpoke (B4a 025), Scavenge: "Put a random Item card from your discard pile into your hand."
#[test]
fn fossil_scavenge_recovers_a_fossil() {
    let slowpoke = CardId::B4a025TeamRocketsSlowpoke;
    let state = fossil_attack(0, slowpoke, vec![EnergyType::Psychic], |state| state.discard_piles[0] = vec![fossil()]);
    assert_eq!(state.hands[0], vec![fossil()]);
    assert!(state.discard_piles[0].is_empty());
}

/// The same with a Potion beside the Fossil: either can come back.
#[test]
fn fossil_scavenge_can_recover_a_fossil_or_a_potion() {
    let potion = get_card_by_enum(CardId::PA001Potion);
    let mut taken = BTreeSet::new();
    for seed in 0..80 {
        let slowpoke = CardId::B4a025TeamRocketsSlowpoke;
        let state =
            fossil_attack(seed, slowpoke, vec![EnergyType::Psychic], |state| state.discard_piles[0] = vec![potion.clone(), fossil()]);
        assert_eq!(state.hands[0].len(), 1, "seed {seed}: one card recovered");
        taken.insert(state.hands[0][0].get_name());
    }
    assert_eq!(taken, BTreeSet::from([potion.get_name(), fossil().get_name()]), "both Item cards can come back");
}

/// Raticate (B4 130 and its reprints), Treasure Collecting: "...look at the top 4 cards of your deck and put all Item
/// cards you find there into your hand. Shuffle the other cards back into your deck." The top 4 hold a Fossil and a
/// Potion: both are taken.
#[test]
fn fossil_treasure_collecting_takes_a_fossil() {
    use deckgym::test_support::get_initialized_game;
    for raticate in [CardId::B4130Raticate, CardId::B4178Raticate, CardId::B4221Raticate] {
        let mut game = get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.turn_count = 3;
        state.current_player = 0;
        state.set_board(vec![PlayedCard::from_id(CardId::A1189Rattata)], vec![PlayedCard::from_id(CardId::A1001Bulbasaur)]);
        let evolution = get_card_by_enum(raticate);
        state.hands[0] = vec![evolution.clone()];
        state.decks[0].cards = vec![
            fossil(),
            get_card_by_enum(CardId::PA001Potion),
            get_card_by_enum(CardId::A2152Cynthia),
            get_card_by_enum(CardId::A1001Bulbasaur),
            get_card_by_enum(CardId::A1033Charmander),
        ];
        game.set_state(state);
        game.apply_action(&Action {
            actor: 0,
            action: SimpleAction::Evolve { evolution, in_play_idx: 0, from_deck: false },
            is_stack: false,
        });
        game.apply_action(&Action { actor: 0, action: SimpleAction::UseAbility { in_play_idx: 0 }, is_stack: true });
        let state = game.get_state_clone();
        assert_eq!(state.hands[0], vec![fossil(), get_card_by_enum(CardId::PA001Potion)], "{raticate:?}");
        assert_eq!(
            state.decks[0].cards,
            vec![
                get_card_by_enum(CardId::A2152Cynthia),
                get_card_by_enum(CardId::A1001Bulbasaur),
                get_card_by_enum(CardId::A1033Charmander)
            ],
            "{raticate:?}"
        );
    }
}
