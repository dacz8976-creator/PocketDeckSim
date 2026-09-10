use colored::Colorize;
use log::{debug, info, trace};
use rand::{rngs::StdRng, SeedableRng};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::{
    actions::{apply_action, Action},
    models::EnergyType,
    players::Player,
    simulation_event_handler::{CompositeSimulationEventHandler, SimulationEventHandler},
    state::GameOutcome,
    State,
};

/// Versioned replay identity. Search seeds never come from the gameplay RNG.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct GameRandomness {
    pub scheme: String,
    pub game_seed: u64,
    pub player_search_seeds: [u64; 2],
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DecisionRandomness {
    pub actor: usize,
    pub decision_index: u64,
    pub search_seed: u64,
}

/// Privileged forensic record of information a card effect actually revealed. This is available
/// to replay exporters, but is never part of a player's policy observation.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PrivateRevealRecord {
    pub viewer: usize,
    pub zone_owner: usize,
    #[serde(default)]
    pub cause: String,
    pub scope: String,
    pub cards: Vec<crate::models::Card>,
}

/// Privileged forensic record of a public reveal. Policy observations retain only the durable
/// knowledge authorized by the reveal, not this ordered temporal payload.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct PublicRevealRecord {
    pub zone_owner: usize,
    #[serde(default)]
    pub cause: String,
    pub scope: String,
    pub cards: Vec<crate::models::Card>,
}

/// Public, durable evidence for a resolved Luxury Coin decision. Copied Trainer source identity
/// is deliberately absent; only the batches and the player's decision are recorded.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LuxuryCoinResolutionRecord {
    pub actor: usize,
    pub initial_faces: Vec<bool>,
    pub decision: crate::state::LuxuryCoinDecision,
    pub replacement_faces: Option<Vec<bool>>,
}

// SplitMix64 finalizer with fixed domain tags; part of pdl-search-v1's replay contract.
fn mix_seed(mut value: u64) -> u64 {
    value = (value ^ (value >> 30)).wrapping_mul(0xbf58476d1ce4e5b9);
    value = (value ^ (value >> 27)).wrapping_mul(0x94d049bb133111eb);
    value ^ (value >> 31)
}

impl GameRandomness {
    fn new(game_seed: u64) -> Self {
        Self {
            scheme: "pdl-search-v1/rand-0.8-StdRng".into(),
            game_seed,
            player_search_seeds: [
                mix_seed(game_seed ^ 0x50444c5f53454130),
                mix_seed(game_seed ^ 0x50444c5f53454131),
            ],
        }
    }

    pub fn decision(&self, actor: usize, decision_index: u64) -> DecisionRandomness {
        DecisionRandomness {
            actor,
            decision_index,
            search_seed: mix_seed(
                self.player_search_seeds[actor]
                    .wrapping_add(decision_index.wrapping_mul(0x9e3779b97f4a7c15)),
            ),
        }
    }
}

// It has a lifetime to allow it to borrow the event handler mutably for the duration of the game
pub struct Game<'a> {
    seed: u64,
    rng: StdRng, // Used only for dealing and real action resolution.
    randomness: GameRandomness,
    decision_counts: [u64; 2],
    knowledge: [crate::observation::RevealedKnowledge; 2],
    private_reveal_history: Vec<PrivateRevealRecord>,
    public_reveal_history: Vec<PublicRevealRecord>,
    luxury_coin_resolution_history: Vec<LuxuryCoinResolutionRecord>,
    id: Uuid,
    players: Vec<Box<dyn Player>>,

    state: State,

    debug: bool,
    event_handler: Option<&'a mut CompositeSimulationEventHandler>,
}

impl<'a> Game<'a> {
    pub fn from_state(mut state: State, players: Vec<Box<dyn Player>>, seed: u64) -> Self {
        state.sanitize_pending_choice_state();
        state.private_reveal_events.clear();
        state.public_reveal_events.clear();
        state.luxury_coin_resolution_events.clear();
        let rng = StdRng::seed_from_u64(seed);
        Game {
            seed,
            rng,
            randomness: GameRandomness::new(seed),
            decision_counts: [0; 2],
            knowledge: Default::default(),
            private_reveal_history: Vec::new(),
            public_reveal_history: Vec::new(),
            luxury_coin_resolution_history: Vec::new(),
            id: Uuid::new_v4(),
            players,
            state,
            debug: false,
            event_handler: None,
        }
    }

    pub fn new(players: Vec<Box<dyn Player>>, seed: u64) -> Self {
        let mut rng = StdRng::seed_from_u64(seed);
        let deck_a = players[0].get_deck();
        let deck_b = players[1].get_deck();
        let state = State::initialize(&deck_a, &deck_b, &mut rng);
        Game {
            seed,
            rng,
            randomness: GameRandomness::new(seed),
            decision_counts: [0; 2],
            knowledge: Default::default(),
            private_reveal_history: Vec::new(),
            public_reveal_history: Vec::new(),
            luxury_coin_resolution_history: Vec::new(),
            id: Uuid::new_v4(),
            players,
            state,
            debug: true,
            event_handler: None,
        }
    }

    pub fn new_with_event_handlers(
        game_id: Uuid,
        players: Vec<Box<dyn Player>>,
        seed: u64,
        event_handler: &'a mut CompositeSimulationEventHandler,
    ) -> Self {
        let mut game = Game::new(players, seed);
        event_handler.on_game_randomness(game_id, &game.randomness);
        game.event_handler = Some(event_handler);
        game.id = game_id;
        game
    }

    pub fn is_game_over(&self) -> bool {
        self.state.is_game_over()
    }

    // Returns None if the game times out
    pub fn play(&mut self) -> Option<GameOutcome> {
        if self.debug {
            info!(
                "Playing game with seed: {}; randomness: {:?}",
                self.seed, self.randomness
            );
        }
        while !self.state.is_game_over() {
            self.play_tick();
        }
        self.state.winner
    }

    pub fn play_until_stable(&mut self) {
        while !self.state.is_game_over()
            && (self.state.turn_count == 0 || !self.state.move_generation_stack.is_empty())
        {
            self.play_tick();
        }
    }

    pub fn play_tick(&mut self) -> Action {
        let (actor, mut actions) = self.state.generate_possible_actions();
        crate::observation::canonical_actions(&mut actions);

        let player = &self.players[actor];
        let color = self.get_color(actor);
        self.print_turn_header(actor, player.as_ref(), &color);
        let mut decision_randomness = None;
        let mut unpriced = Vec::new();
        let mut public_reply_evidence = None;
        let collect_public_replies = self.event_handler.as_ref()
            .is_some_and(|handler| handler.wants_public_reply_evidence());
        let action = if actions.len() == 1 {
            debug!("Only one possible action, selecting it.");
            actions[0].clone()
        } else {
            let player = self.players[actor].as_mut();
            trace!(
                "Possible Actions: {:?}",
                actions.iter().map(|x| x.action.clone()).collect::<Vec<_>>()
            );
            let decision = self.randomness.decision(actor, self.decision_counts[actor]);
            self.decision_counts[actor] += 1;
            let mut search_rng = StdRng::seed_from_u64(decision.search_seed);
            decision_randomness = Some(decision);
            let observation = crate::observation::PlayerObservation::from_state(
                &self.state,
                actor,
                &self.knowledge[actor],
            );
            let ((chosen, mut branches), mut evidence) =
                crate::public_reply_evidence::collect_public_reply_evidence(collect_public_replies, || {
                    crate::observation::collect_unpriced(|| {
                        player.decision_fn(&mut search_rng, &observation, &actions)
                    })
                });
            crate::observation::mark_selected(&mut branches, &chosen);
            if let Some(evidence) = &mut evidence {
                crate::public_reply_evidence::mark_selected(evidence, &chosen);
            }
            public_reply_evidence = evidence;
            unpriced = branches;
            assert!(
                actions.contains(&chosen),
                "policy must select an offered legal action"
            );
            chosen
        };

        let player = &self.players[actor];
        self.print_action(&action, actor, player.as_ref(), &color);

        if self.event_handler.is_some() {
            if let Some(handler) = &mut self.event_handler {
                handler.on_decision_information(
                    self.id,
                    crate::observation::INFORMATION_MODEL,
                    &unpriced,
                );
                handler.on_decision_randomness(self.id, decision_randomness.as_ref());
                handler.on_public_reply_evidence(self.id, public_reply_evidence.as_ref());
                handler.on_action(self.id, &self.state, actor, &actions, &action);
            }
        }
        self.apply_action(&action);
        self.print_state();
        action
    }

    /// Seeds identify a fresh game, not a mid-game checkpoint. `set_state` does not
    /// rewind either chance or decision counters.
    pub fn observation(&self, actor: usize) -> crate::observation::PlayerObservation {
        crate::observation::PlayerObservation::from_state(
            &self.state,
            actor,
            &self.knowledge[actor],
        )
    }

    pub fn randomness(&self) -> &GameRandomness {
        &self.randomness
    }

    pub fn private_reveal_history(&self) -> &[PrivateRevealRecord] {
        &self.private_reveal_history
    }

    pub fn public_reveal_history(&self) -> &[PublicRevealRecord] {
        &self.public_reveal_history
    }

    pub fn luxury_coin_resolution_history(&self) -> &[LuxuryCoinResolutionRecord] {
        &self.luxury_coin_resolution_history
    }

    pub fn get_state_clone(&self) -> State {
        self.state.clone()
    }

    // TODO: Maybe make these only available for testing?
    pub fn apply_action(&mut self, action: &Action) {
        let before = self.state.clone();
        apply_action(&mut self.rng, &mut self.state, action);
        crate::observation::update_knowledge(&mut self.knowledge, &before, &self.state, action);
        let reveals = self
            .state
            .private_reveal_events
            .iter()
            .map(|event| PrivateRevealRecord {
                viewer: event.viewer,
                zone_owner: event.zone_owner,
                cause: event.cause.clone(),
                scope: match event.kind {
                    crate::state::PrivateRevealKind::RandomHandCard => "random_hand_card",
                    crate::state::PrivateRevealKind::WholeHand => "whole_hand",
                }
                .into(),
                cards: event.cards.clone(),
            })
            .collect::<Vec<_>>();
        self.private_reveal_history.extend(reveals.iter().cloned());
        if let Some(handler) = &mut self.event_handler {
            handler.on_private_reveals(self.id, &reveals);
        }
        let public_reveals = self
            .state
            .public_reveal_events
            .iter()
            .map(|event| PublicRevealRecord {
                zone_owner: event.zone_owner,
                cause: event.cause.clone(),
                scope: match event.kind {
                    crate::state::PublicRevealKind::DeckPrefixThenShuffle => {
                        "deck_prefix_then_shuffle"
                    }
                }
                .into(),
                cards: event.cards.clone(),
            })
            .collect::<Vec<_>>();
        self.public_reveal_history
            .extend(public_reveals.iter().cloned());
        if let Some(handler) = &mut self.event_handler {
            handler.on_public_reveals(self.id, &public_reveals);
        }
        let luxury_coin_resolutions = self
            .state
            .luxury_coin_resolution_events
            .iter()
            .map(|event| LuxuryCoinResolutionRecord {
                actor: event.actor,
                initial_faces: event.initial_faces.clone(),
                decision: event.decision,
                replacement_faces: event.replacement_faces.clone(),
            })
            .collect::<Vec<_>>();
        self.luxury_coin_resolution_history
            .extend(luxury_coin_resolutions.iter().cloned());
        if let Some(handler) = &mut self.event_handler {
            handler.on_luxury_coin_resolutions(self.id, &luxury_coin_resolutions);
        }
        self.state.private_reveal_events.clear();
        self.state.public_reveal_events.clear();
        self.state.luxury_coin_resolution_events.clear();
        if let Some(handler) = &mut self.event_handler {
            handler.on_action_resolved(self.id);
        }
    }

    pub fn set_state(&mut self, mut state: State) {
        state.sanitize_pending_choice_state();
        state.private_reveal_events.clear();
        state.public_reveal_events.clear();
        state.luxury_coin_resolution_events.clear();
        self.state = state;
        self.knowledge = Default::default();
        self.private_reveal_history.clear();
        self.public_reveal_history.clear();
        self.luxury_coin_resolution_history.clear();
    }

    fn print_turn_header(&self, actor: usize, player: &dyn Player, color: &str) {
        if self.debug {
            debug!(
                "{}{}",
                format!("===== {}|{:?}|", self.state.turn_count, self.state.points).color(color),
                format!("{actor}:{player:?}").color(color),
            );
        }
    }

    fn print_action(&self, action: &Action, _: usize, player: &dyn Player, color: &str) {
        if self.debug {
            info!(
                "{} chose {}",
                format!("{}:{:?}", self.state.turn_count, player).color(color),
                format!("{:?}", action.action).bold()
            );
        }
    }

    fn print_state(&self) {
        if self.debug {
            trace!("{}", self.state.debug_string());
        }
    }

    /// see https://github.com/colored-rs/colored?tab=readme-ov-file#colors
    fn get_color(&self, actor: usize) -> String {
        let energy = self.state.decks[actor].energy_types[0];
        let color = match energy {
            EnergyType::Colorless => todo!(),
            EnergyType::Fighting => "red",
            EnergyType::Fire => "red",
            EnergyType::Grass => "green",
            EnergyType::Lightning => "yellow",
            EnergyType::Psychic => "magenta",
            EnergyType::Water => "blue",
            EnergyType::Darkness => "bright_black",
            EnergyType::Metal => "bright_black",
            EnergyType::Dragon => todo!(),
        };
        color.to_string()
    }
}

#[cfg(test)]
mod tests {
    use crate::{
        card_ids::CardId,
        models::{PlayedCard, StatusCondition},
        players::{AttachAttackPlayer, EndTurnPlayer, Player},
        state::GameOutcome,
        test_support::load_test_decks,
        Game, State,
    };

    fn state_with_private_reveal() -> State {
        let mut state = State::default();
        state
            .private_reveal_events
            .push(crate::state::PrivateRevealEvent {
                viewer: 0,
                zone_owner: 1,
                cause: "Spy Ops".into(),
                kind: crate::state::PrivateRevealKind::RandomHandCard,
                cards: vec![crate::database::get_card_by_enum(CardId::PA001Potion)],
            });
        state
            .public_reveal_events
            .push(crate::state::PublicRevealEvent {
                zone_owner: 0,
                cause: "Rocket Frenzy".into(),
                kind: crate::state::PublicRevealKind::DeckPrefixThenShuffle,
                cards: vec![crate::database::get_card_by_enum(
                    CardId::PB088TeamRocketsScyther,
                )],
            });
        state
    }

    #[test]
    fn adopting_state_clears_stale_private_reveal_events() {
        let mut game = Game::from_state(state_with_private_reveal(), Vec::new(), 0);
        assert!(game.state.private_reveal_events.iter().next().is_none());
        assert!(game.state.public_reveal_events.iter().next().is_none());

        game.set_state(state_with_private_reveal());
        assert!(game.state.private_reveal_events.iter().next().is_none());
        assert!(game.state.public_reveal_events.iter().next().is_none());
        assert!(game.private_reveal_history.is_empty());
        assert!(game.public_reveal_history.is_empty());
    }

    #[test]
    fn test_poison() {
        let (deck_a, deck_b) = load_test_decks();
        let player_a = Box::new(AttachAttackPlayer { deck: deck_a });
        let player_b = Box::new(EndTurnPlayer { deck: deck_b });
        let players: Vec<Box<dyn Player>> = vec![player_a, player_b];
        let mut game = Game::new(players, 3);

        // Play initial setup phase
        while game.get_state_clone().turn_count == 0 {
            game.play_tick();
        }

        // Make the intended poison target explicit; setup placement is randomized.
        let mut state = game.get_state_clone();
        state.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::A1176Koffing));
        state.current_player = 0;
        state.apply_status_condition(1, 0, StatusCondition::Poisoned);
        game.set_state(state);

        // The game starts with AA playing. After each turn 10 damage should be subtracted.
        // So ending 1 Koffing should have 60HP, 2 => 50HP, 3 => 40HP, 4 => 30HP, 5 => 20HP
        while game.get_state_clone().turn_count == 1 {
            game.play_tick();
        }
        // Koffing should have 60 HP starting turn 2
        assert_eq!(game.get_state_clone().get_remaining_hp(1, 0), 60);
        while game.get_state_clone().turn_count == 2 {
            game.play_tick();
        }
        // Koffing should have 50 HP starting turn 3
        assert_eq!(game.get_state_clone().get_remaining_hp(1, 0), 50);
        while game.get_state_clone().turn_count == 3 {
            game.play_tick();
        }

        // Now play the rest. AA should win b.c. ET has no bench pokemon
        let winner = game.play();
        assert_eq!(game.get_state_clone().turn_count, 5);
        assert_eq!(winner, Some(GameOutcome::Win(0)));
    }

    #[test]
    fn test_ko_by_posion() {
        let (deck_a, deck_b) = load_test_decks();
        let player_a = Box::new(EndTurnPlayer { deck: deck_a });
        let player_b = Box::new(AttachAttackPlayer { deck: deck_b });
        let players: Vec<Box<dyn Player>> = vec![player_a, player_b];
        let mut game = Game::new(players, 4); // EndTurnPlayer starts

        // Play the randomized setup phase, then fix the active cards and starter explicitly.
        // Turn 1, EE ends. Turn 2, AA attaches and attacks. Exeggcute should have 30 HP.
        // Turn 3, ET ends. We artificially poision, so that after playing out turn 4
        // (AA attacks) Exeggcute has 10 HP and KO from poison.
        while game.state.turn_count == 0 {
            game.play_tick();
        }
        let mut setup = game.get_state_clone();
        setup.in_play_pokemon[0][0] = Some(PlayedCard::from_id(CardId::A1021Exeggcute));
        setup.in_play_pokemon[1][0] = Some(PlayedCard::from_id(CardId::A1176Koffing));
        setup.current_player = 0;
        game.set_state(setup);
        while game.state.turn_count < 4 {
            game.play_tick();
        }
        assert_eq!(game.get_state_clone().get_remaining_hp(0, 0), 30);

        // Artificially poison Exeggcute
        let mut state = game.get_state_clone();
        state.apply_status_condition(0, 0, StatusCondition::Poisoned);
        game.set_state(state);

        // Turn 4, AA attacks. Checkup wins the game before another turn starts.
        while game.state.turn_count == 4 && !game.is_game_over() {
            game.play_tick();
        }
        assert_eq!(game.get_state_clone().points[0], 0);
        assert_eq!(game.get_state_clone().points[1], 1);
        game.play();
        assert_eq!(game.get_state_clone().turn_count, 4);
        assert_eq!(game.get_state_clone().winner, Some(GameOutcome::Win(1)));
    }

    // TODO: Look for a game that has bench, and pokemon can die from attack + poison
    //   to launche the complicated sequence of Poison K.O. then user having
    //   to select one pokemon to promote to active.

    // TODO: Multiple bench KO

    #[test]
    fn play_until_stable_preserves_a_terminal_state_with_pending_choices() {
        let (deck_a, deck_b) = load_test_decks();
        let players: Vec<Box<dyn Player>> = vec![
            Box::new(EndTurnPlayer { deck: deck_a }),
            Box::new(EndTurnPlayer { deck: deck_b }),
        ];
        let mut game = Game::new(players, 4);
        let mut state = game.get_state_clone();
        state.turn_count = 3;
        state.winner = Some(GameOutcome::Win(0));
        state.move_generation_stack.push((0, vec![crate::actions::SimpleAction::Noop]));
        game.set_state(state);
        let before = game.get_state_clone();
        game.play_until_stable();
        assert_eq!(game.get_state_clone(), before,
            "settling pending actions must not mutate an already completed game");
    }
}
