//! B1' public pricing (`kp<N>`): the k<N> search, blind as ever, but effects whose text mentions the
//! opponent's hand or deck are priced instead of left unpriced.
//!
//! Blind, k<N> scores any such move as if nothing happened (`hidden_continuation_reason`'s text rule):
//! Darkness Claw's 80 damage counts as zero and Copycat as a no-op. The option B attribution
//! (rl/results/option_b_attribution_2026-09-24.md) found that pricing these, not information about
//! the opponent, is where the list guess moves the table. This player gets that pricing with no list:
//! the effect resolves against the opponent's Unknown cards, which have no identity, so only its public
//! parts count. Everything else is the k<N> search unchanged, and with none of these cards in play it
//! plays k<N>'s games move for move.
//!
//! The rule is lifted only for the effect texts in [`AUDITED_TEXTS`]: the 62 texts in the card database
//! that mention the opponent's hand or deck, each read on the laptop (tier-1 read of 858b6fe: no leak, no
//! panic). A text added later stays unpriced under kp, exactly as under k, until it is audited and added;
//! `the_audited_list_is_the_card_databases_whole_inventory` fails until then.
//!
//! What this does not do: an effect whose payoff is the identity of the opponent's hidden cards gets no
//! credit for it, because Unknown cards have none. Penny, Portrait, Team Rocket's Boss and similar cards
//! are priced for their public parts only.

use rand::rngs::StdRng;
use std::fmt::Debug;

use super::expectiminimax_player::ExpectiMiniMaxPlayer;
use super::Player;
use crate::actions::Action;
use crate::observation::{with_public_pricing, PlayerObservation};
use crate::{Deck, State};

/// The lowercased effect texts (as `hidden_continuation_reason` reads them) whose opponent-hand-or-deck rule
/// public pricing lifts, sorted so they can be binary-searched. Generated from the card database on Sept 25.
pub(crate) const AUDITED_TEXTS: [&str; 62] = [
    r#"1 attack from among the pokémon in your opponent's hand and deck is chosen at random, and you use the chosen attack as this attack."#,
    r#"as long as this pokémon is in the active spot, your opponent can't play any stadium cards from their hand."#,
    r#"as long as this pokémon is in the active spot, your opponent can't use any supporter cards from their hand."#,
    r#"at the end of your opponent's turn, if this pokémon is in the active spot, put a random card from your deck that evolves from this pokémon onto this pokémon to evolve it."#,
    r#"before doing damage, shuffle all pokémon tools from each of your opponent's pokémon into their deck."#,
    r#"discard a random card from your opponent's hand."#,
    r#"discard a random item card from your opponent's hand."#,
    r#"discard a random pokémon tool card from your opponent's hand."#,
    r#"discard the top 3 cards of your opponent's deck."#,
    r#"discard the top card of your opponent's deck."#,
    r#"draw cards until you have the same number of cards in your hand as your opponent."#,
    r#"during your opponent's next turn, they can't play any item cards from their hand."#,
    r#"during your opponent's next turn, they can't play any pokémon from their hand to evolve their pokémon."#,
    r#"during your opponent's next turn, they can't play any trainer cards from their hand."#,
    r#"flip 3 coins. for each heads, a card is chosen at random from your opponent's hand. your opponent reveals that card and shuffles it into their deck."#,
    r#"flip a coin until you get tails. for each heads, discard the top card of your opponent's deck."#,
    r#"flip a coin. if heads, discard a random card from your opponent's hand."#,
    r#"flip a coin. if heads, look at a random card from your opponent's hand and shuffle it into their deck."#,
    r#"flip a coin. if heads, put your opponent's active pokémon into their hand."#,
    r#"flip a coin. if heads, your opponent reveals a random card from their hand and shuffles it into their deck."#,
    r#"flip a coin. if heads, your opponent reveals their hand. choose a supporter card you find there and discard it."#,
    r#"flip a coin. if heads, your opponent shuffles their active pokémon into their deck."#,
    r#"for each of your [p] pokémon in play, look at that many cards from the top of your opponent's deck and put them back in any order."#,
    r#"if the [d] pokémon this card is attached to is in the active spot and is damaged by an attack from your opponent's pokémon, your opponent reveals a random card from their hand and shuffles it into their deck."#,
    r#"if the pokémon this card is attached to is knocked out by damage from an attack from your opponent's pokémon, draw cards until you have 5 cards in your hand."#,
    r#"if the pokémon this card is attached to is knocked out by damage from an attack from your opponent's pokémon, put it into your hand instead of the discard pile."#,
    r#"if this is the first time this pokémon has used an attack after coming into play, during your opponent's next turn, they can't use any trainer cards from their hand."#,
    r#"if you have the same number of cards in your hand as your opponent, this attack does 40 more damage."#,
    r#"if your opponent has exactly 2, 4, or 6 cards in their hand, this attack does 40 more damage."#,
    r#"if your opponent's active pokémon is an evolved pokémon, devolve it by putting the highest stage evolution card on it into your opponent's hand."#,
    r#"look at a random supporter card that's not penny from your opponent's deck and shuffle it back into their deck. use the effect of that card as the effect of this card."#,
    r#"look at your opponent's hand and put any number of basic pokémon you find there onto your opponent's bench."#,
    r#"once during your turn, if this pokémon is in the active spot, you may look at a random supporter card from your opponent's hand. use the effect of that card as the effect of this ability."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may discard a random energy from your opponent's active pokémon."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may do 20 damage to your opponent's active pokémon."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may do 30 damage to your opponent's active pokémon."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may flip a coin. if heads, your opponent's active pokémon is now paralyzed."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may have your opponent shuffle their hand into their deck. for each remaining point that your opponent needs to win, they draw a card."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may make your opponent's active pokémon poisoned and burned."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may move a random energy from your opponent's active pokémon to this pokémon."#,
    r#"once during your turn, when you play this pokémon from your hand to evolve 1 of your pokémon, you may prevent all damage from—and effects of—attacks from your opponent's pokémon done to this pokémon until the end of your opponent's next turn."#,
    r#"once during your turn, when you put this pokémon from your hand onto your bench, you may have your opponent reveal their hand."#,
    r#"once during your turn, when you put this pokémon from your hand onto your bench, you may switch out your opponent's active pokémon to the bench. (your opponent chooses the new active pokémon.)"#,
    r#"once during your turn, you may discard the top card of your opponent's deck."#,
    r#"once during your turn, you may look at a random card from your opponent's hand."#,
    r#"put a random item card, except any team rocket's thieving machine, from your opponent's discard pile into your hand."#,
    r#"return all pokémon tools attached to each pokémon (both yours and your opponent's) to their owner's hand."#,
    r#"shuffle your hand into your deck. draw a card for each card in your opponent's hand."#,
    r#"this attack does 20 more damage for each trainer card in your opponent's deck."#,
    r#"your opponent can't play any pokémon from their hand to evolve their active pokémon."#,
    r#"your opponent can't use any supporter cards from their hand during their next turn."#,
    r#"your opponent discards cards from their hand until they have 4 cards in their hand."#,
    r#"your opponent reveals a random card from their hand and shuffles it into their deck."#,
    r#"your opponent reveals a random card from their hand and shuffles it into their deck. shuffle this pokémon into your deck."#,
    r#"your opponent reveals all of the supporter cards in their deck."#,
    r#"your opponent reveals their hand."#,
    r#"your opponent reveals their hand. choose a card you find there and shuffle it into your opponent's deck."#,
    r#"your opponent reveals their hand. choose a supporter card you find there and discard it."#,
    r#"your opponent reveals their hand. choose a supporter card you find there and shuffle it into your opponent's deck."#,
    r#"your opponent shuffles their hand into their deck and draws 3 cards."#,
    r#"your opponent shuffles their hand into their deck and draws a card for each of their remaining points needed to win."#,
    r#"your opponent's active pokémon is now poisoned and paralyzed. shuffle this pokémon and all attached cards into your deck."#,
];

/// Whether public pricing may price this effect text (see [`AUDITED_TEXTS`]).
pub(crate) fn is_audited(text: &str) -> bool {
    AUDITED_TEXTS.binary_search(&text).is_ok()
}

pub struct PublicPricingPlayer {
    pub search: ExpectiMiniMaxPlayer,
}

impl Debug for PublicPricingPlayer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "PublicPricingPlayer")
    }
}

impl Player for PublicPricingPlayer {
    fn decision_fn(
        &mut self,
        rng: &mut StdRng,
        observation: &PlayerObservation,
        possible_actions: &[Action],
    ) -> Action {
        let search = &mut self.search;
        with_public_pricing(|| search.decision_fn(rng, observation, possible_actions))
    }

    fn decide_omniscient(&mut self, rng: &mut StdRng, state: &State, possible_actions: &[Action]) -> Action {
        let search = &mut self.search;
        with_public_pricing(|| search.decide_omniscient(rng, state, possible_actions))
    }

    fn get_deck(&self) -> Deck {
        self.search.get_deck()
    }
}

#[cfg(test)]
mod tests {
    use super::super::{get_player, PlayerCode};
    use super::*;
    use crate::actions::SimpleAction;
    use crate::card_ids::CardId;
    use crate::models::{Card, EnergyType, PlayedCard};
    use crate::observation::{hidden_continuation_reason, RevealedKnowledge};
    use crate::players::value_functions;
    use crate::test_support::get_test_game_with_board;
    use crate::Game;
    use rand::SeedableRng;

    fn k3_search() -> ExpectiMiniMaxPlayer {
        // The K arm of get_player, field for field.
        ExpectiMiniMaxPlayer {
            deck: Deck::default(),
            max_depth: 3,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_clock_effect_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }
    }

    /// Mega Absol ex with Darkness Claw paid for, against the opponent's only Pokémon, a 60-HP Abra
    /// (80 damage, +20 Weakness): the attack knocks it out and wins. The opponent's hand holds a card, so blind it is Unknown.
    fn darkness_claw_wins() -> (State, Vec<Action>) {
        let real = darkness_claw_game();
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        let search_state = observation.search_state(&mut StdRng::seed_from_u64(7));
        assert!(search_state.hands[1].iter().all(|c| *c == Card::Unknown));
        let (actor, actions) = search_state.generate_possible_actions();
        assert_eq!(actor, 0);
        (search_state, actions)
    }

    /// The real game state behind [`darkness_claw_wins`].
    fn darkness_claw_game() -> State {
        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::B1151MegaAbsolEx)
                .with_energy(vec![EnergyType::Darkness, EnergyType::Darkness])],
            vec![PlayedCard::from_id(CardId::A1115Abra)],
        );
        let mut state = game.get_state_clone();
        state.move_generation_stack.clear();
        if state.hands[1].is_empty() {
            state.hands[1].push(state.decks[1].cards.pop().unwrap());
        }
        game.set_state(state);
        game.get_state_clone()
    }

    fn darkness_claw(actions: &[Action]) -> usize {
        actions
            .iter()
            .position(|a| matches!(&a.action, SimpleAction::Attack(x) if x.title == "Darkness Claw"))
            .expect("Darkness Claw is offered")
    }

    #[test]
    fn the_opponent_hand_text_rule_is_lifted_only_under_public_pricing() {
        let (state, actions) = darkness_claw_wins();
        let claw = &actions[darkness_claw(&actions)];
        assert!(hidden_continuation_reason(&state, claw).is_some(), "blind k-tiers leave it unpriced");
        assert_eq!(with_public_pricing(|| hidden_continuation_reason(&state, claw)), None);
        // The flag is scoped: it is off again afterwards, and the strict rule ignores it.
        assert!(hidden_continuation_reason(&state, claw).is_some());
        assert!(with_public_pricing(|| crate::observation::hidden_continuation_reason_strict(&state, claw)).is_some());
    }

    #[test]
    fn public_pricing_sees_a_winning_darkness_claw_that_k3_scores_as_nothing() {
        let (state, actions) = darkness_claw_wins();
        let claw = darkness_claw(&actions);
        let provenance = crate::players::public_reply::PublicReplyProvenance::untrusted();
        let blind = k3_search().score_candidates(&mut StdRng::seed_from_u64(1), &state, &actions, provenance);
        let priced = with_public_pricing(|| {
            k3_search().score_candidates(&mut StdRng::seed_from_u64(1), &state, &actions, provenance)
        });
        let mut won = state.clone();
        won.winner = Some(crate::state::GameOutcome::Win(0));
        let win_value = value_functions::public_clock_effect_value_function(&won, 0);
        assert_eq!(priced[claw].0, win_value, "priced: the knockout ends the game");
        assert!(blind[claw].0 < win_value, "blind: scored as the position before the attack");
        let best = priced.iter().map(|s| s.0).fold(f64::NEG_INFINITY, f64::max);
        assert_eq!(priced[claw].0, best, "priced: Darkness Claw is the best move");
    }

    /// Through the player a `kp3` code builds, the way a game or a table run gets it: kp3 prices Darkness
    /// Claw and takes the win, and k3 built right after on the same thread still leaves it unpriced. If the
    /// KP arm of `get_player` stopped wrapping the search, kp would silently play as k and this fails.
    #[test]
    fn kp3_from_get_player_prices_darkness_claw_and_k3_on_the_same_thread_does_not() {
        let real = darkness_claw_game();
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        let (actor, mut actions) = real.generate_possible_actions();
        assert_eq!(actor, 0);
        crate::observation::canonical_actions(&mut actions);
        let claw = darkness_claw(&actions);
        let is_claw = |a: &Action| matches!(&a.action, SimpleAction::Attack(x) if x.title == "Darkness Claw");
        let claw_unpriced = |branches: &[crate::observation::UnpricedBranch]| {
            branches.iter().any(|b| b.reason == "effect or choice depends on unrevealed opponent cards" && is_claw(&b.action))
        };
        let decide = |code: &PlayerCode| {
            let mut player = get_player(Deck::default(), &Deck::default(), code);
            crate::observation::collect_unpriced(|| {
                player.decision_fn(&mut StdRng::seed_from_u64(3), &observation, &actions)
            })
        };
        let (kp_choice, kp_branches) = decide(&PlayerCode::KP { max_depth: 3 });
        assert!(!claw_unpriced(&kp_branches), "kp3 prices Darkness Claw");
        assert_eq!(kp_choice, actions[claw], "kp3 takes the winning Darkness Claw");
        let (_, k3_branches) = decide(&PlayerCode::K { max_depth: 3 });
        assert!(claw_unpriced(&k3_branches), "k3 on the same thread still leaves Darkness Claw unpriced");
    }

    /// kq3 is built the same way (get_player) and keeps kp's pricing: it prices Darkness Claw too.
    #[test]
    fn kq3_from_get_player_also_prices_darkness_claw() {
        let real = darkness_claw_game();
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        let (_, mut actions) = real.generate_possible_actions();
        crate::observation::canonical_actions(&mut actions);
        let claw = darkness_claw(&actions);
        let mut player = get_player(Deck::default(), &Deck::default(), &PlayerCode::KQ { max_depth: 3 });
        let (choice, branches) = crate::observation::collect_unpriced(|| {
            player.decision_fn(&mut StdRng::seed_from_u64(3), &observation, &actions)
        });
        assert!(!branches.iter().any(|b| b.reason == "effect or choice depends on unrevealed opponent cards"
            && matches!(&b.action.action, SimpleAction::Attack(x) if x.title == "Darkness Claw")));
        assert_eq!(choice, actions[claw]);
    }

    /// The B2c position, through get_player: Bonsly (free Teary Attack) Active, Riolu with 1 Fighting on
    /// the Bench, Mega Lucario ex in the deck, Bulbasaur with Vine Whip paid for across the table, this
    /// turn's Energy Fighting. kp3 (like k3) retreats Bonsly, pushing the unevolved Riolu into the Active
    /// Spot; kq3 powers Riolu on the Bench instead. If the KQ arm of get_player stopped using the kq value
    /// function, kq3 would play as kp3 and this fails.
    #[test]
    fn kq3_from_get_player_builds_the_benched_attacker_where_kp3_retreats_into_it() {
        let mut game = crate::test_support::get_initialized_game(0);
        let mut state = game.get_state_clone();
        state.set_board(
            vec![
                PlayedCard::from_id(CardId::B3078Bonsly),
                PlayedCard::from_id(CardId::B3079Riolu).with_energy(vec![EnergyType::Fighting]),
            ],
            vec![PlayedCard::from_id(CardId::A1001Bulbasaur)
                .with_energy(vec![EnergyType::Grass, EnergyType::Colorless])],
        );
        state.current_player = 0;
        state.turn_count = 4;
        state.move_generation_stack.clear();
        state.decks[0].cards.push(crate::database::get_card_by_enum(CardId::B3081MegaLucarioEx));
        state.energy_zone[0].current = Some(EnergyType::Fighting);
        game.set_state(state);
        let real = game.get_state_clone();
        let observation = PlayerObservation::from_state(&real, 0, &RevealedKnowledge::default());
        let (_, mut actions) = real.generate_possible_actions();
        crate::observation::canonical_actions(&mut actions);
        let decide = |code: PlayerCode| {
            let mut player = get_player(Deck::default(), &Deck::default(), &code);
            player.decision_fn(&mut StdRng::seed_from_u64(3), &observation, &actions).action
        };
        assert_eq!(decide(PlayerCode::KP { max_depth: 3 }), SimpleAction::Retreat(1));
        assert!(
            matches!(decide(PlayerCode::KQ { max_depth: 3 }),
                SimpleAction::Attach { ref attachments, .. } if attachments == &vec![(1, EnergyType::Fighting, 1)]),
            "kq3 attaches the turn's Fighting to the benched Riolu"
        );
    }

    /// The audited list is exactly the set of card texts the rule covers today, sorted. A new card with such
    /// a text fails this until it is audited and added (until then kp leaves it unpriced, as k does).
    #[test]
    fn the_audited_list_is_the_card_databases_whole_inventory() {
        use strum::IntoEnumIterator;
        let mut found = std::collections::BTreeSet::new();
        for id in CardId::iter() {
            let card = crate::database::get_card_by_enum(id);
            let mut texts = Vec::new();
            match &card {
                Card::Trainer(t) => texts.push(t.effect.clone()),
                Card::Pokemon(p) => {
                    texts.extend(p.attacks.iter().filter_map(|a| a.effect.clone()));
                    texts.extend(p.ability.iter().map(|a| a.effect.clone()));
                }
                _ => {}
            }
            for t in texts {
                let t = t.to_lowercase();
                if t.contains("opponent") && (t.contains("hand") || t.contains("deck")) {
                    found.insert(t);
                }
            }
        }
        let audited: std::collections::BTreeSet<String> = AUDITED_TEXTS.iter().map(|t| t.to_string()).collect();
        let new: Vec<_> = found.difference(&audited).collect();
        let gone: Vec<_> = audited.difference(&found).collect();
        assert!(new.is_empty() && gone.is_empty(), "not audited: {new:#?}\nno longer in the database: {gone:#?}");
        assert!(AUDITED_TEXTS.windows(2).all(|w| w[0] < w[1]), "AUDITED_TEXTS must stay sorted");
    }

    /// Under public pricing an audited text is priced (Copycat) and an unaudited one (a made-up Trainer
    /// whose text mentions the opponent's hand) is still left unpriced, as k leaves it.
    #[test]
    fn public_pricing_lifts_the_rule_only_for_audited_texts() {
        let (state, _) = darkness_claw_wins();
        let play = |effect: &str| Action {
            actor: 0,
            action: SimpleAction::Play {
                trainer_card: crate::models::TrainerCard {
                    id: "TEST 001".into(),
                    trainer_card_type: crate::models::TrainerType::Supporter,
                    name: "Test Supporter".into(),
                    effect: effect.into(),
                    rarity: String::new(),
                    booster_pack: String::new(),
                },
            },
            is_stack: false,
        };
        let copycat = match crate::database::get_card_by_enum(CardId::B1225Copycat) {
            Card::Trainer(t) => t.effect,
            _ => unreachable!(),
        };
        assert!(is_audited(&copycat.to_lowercase()));
        let unaudited = "Look at your opponent's hand and discard a card nobody has printed yet.";
        assert!(!is_audited(&unaudited.to_lowercase()));
        for text in [copycat.as_str(), unaudited] {
            assert!(hidden_continuation_reason(&state, &play(text)).is_some(), "blind: {text}");
        }
        assert_eq!(with_public_pricing(|| hidden_continuation_reason(&state, &play(&copycat))), None);
        assert!(with_public_pricing(|| hidden_continuation_reason(&state, &play(unaudited))).is_some());
    }

    /// Where neither deck has a card whose text mentions the opponent's hand or deck, kp3 must play k3's
    /// games move for move: the wrapper changes nothing else. (Every table list has Copycat, so these use
    /// example decks without any such card.)
    #[test]
    fn kp3_plays_k3_game_for_game_without_opponent_hand_cards() {
        let pairs = [("weezing-arbok", "fire"), ("mewtwoex", "blastoiseex"), ("hitmonlee", "arceusdialga")];
        let k3 = PlayerCode::K { max_depth: 3 };
        let kp3 = PlayerCode::KP { max_depth: 3 };
        for (a, b) in pairs {
            let deck = |n: &str| Deck::from_file(&format!("example_decks/{n}.txt")).unwrap();
            for seed in 0..6u64 {
                let play = |code: &PlayerCode| {
                    let empty = Deck::default();
                    let players = vec![get_player(deck(a), &empty, code), get_player(deck(b), &empty, code)];
                    let mut game = Game::new(players, 22_000_000_000 + seed);
                    let mut moves = Vec::new();
                    while !game.is_game_over() {
                        moves.push(game.play_tick());
                    }
                    moves
                };
                assert!(play(&k3) == play(&kp3), "{a} v {b}, seed {seed}: kp3 and k3 differ");
            }
        }
    }
}
