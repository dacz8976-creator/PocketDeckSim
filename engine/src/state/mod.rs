mod energy;
mod played_card;

use log::{debug, trace};
use rand::rngs::StdRng;
use rand::{seq::SliceRandom, Rng};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::fmt;
use std::hash::Hash;

use crate::{
    actions::abilities::AbilityMechanic,
    actions::{get_in_play_ability_mechanic, has_in_play_ability_mechanic, SimpleAction},
    card_ids::CardId,
    deck::Deck,
    effects::TurnEffect,
    models::{Attack, Card, EnergyType, StatusCondition, TrainerCard},
    move_generation,
    stadiums::is_starting_plains_active,
    tools::has_tool,
};

pub use played_card::{has_serperior_jungle_totem, PlayedCard};

#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum GameOutcome {
    Win(usize),
    Tie,
}

/// A player's energy zone. The zone holds two slots:
/// - `current`: the energy attachable this turn (None on the player going first's turn 1,
///   and None after the player has already attached this turn).
/// - `next`: the energy that will rotate into `current` at the start of this player's next turn.
///   Visible to the player as a preview.
#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct EnergyZone {
    pub current: Option<EnergyType>,
    pub next: Option<EnergyType>,
}

/// A sampled attack-effect coin batch which has not been committed yet because
/// Victory Star's controller must first choose whether to keep or replace it.
/// This is deliberately data-only: attack closures are reconstructed from the
/// unchanged state when the choice resolves.
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub struct PendingAttackCoinChoice {
    pub actor: usize,
    pub attack: Attack,
    pub original_is_stack: bool,
    /// Ordered coin faces (`true` = heads) from the sampled attack-effect batch.
    pub flips: Vec<bool>,
    /// Deterministic source attribution when multiple Victini are in play.
    pub victory_star_in_play_idx: usize,
}

#[derive(Clone, Copy, Hash, PartialEq, Eq)]
pub(crate) enum PrivateRevealKind {
    RandomHandCard,
    WholeHand,
}

#[derive(Clone, Hash, PartialEq, Eq)]
pub(crate) struct PrivateRevealEvent {
    pub viewer: usize,
    pub zone_owner: usize,
    pub cause: String,
    pub kind: PrivateRevealKind,
    pub cards: Vec<Card>,
}

/// Referee-to-Game side channel for resolved private information. Card identities must never
/// appear in serialized State or its derived Debug output.
#[derive(Clone, Default, Hash, PartialEq, Eq)]
pub(crate) struct PrivateRevealEvents(Vec<PrivateRevealEvent>);

impl fmt::Debug for PrivateRevealEvents {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("<private reveal events redacted>")
    }
}

impl PrivateRevealEvents {
    pub fn push(&mut self, event: PrivateRevealEvent) {
        self.0.push(event);
    }
    pub fn iter(&self) -> impl Iterator<Item = &PrivateRevealEvent> {
        self.0.iter()
    }
    pub fn clear(&mut self) {
        self.0.clear();
    }
}

/// The already-selected Trainer source whose one coin batch is awaiting Luxury Coin's choice.
/// Penny stores the copied Supporter once so a replacement cannot select a different source.
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrainerCoinEffectRoute {
    Direct {
        trainer: TrainerCard,
    },
    Penny {
        copied: TrainerCard,
        shuffle_owner: usize,
    },
    Stadium {
        stadium: TrainerCard,
        /// Preserved evidence only; provisional eligibility is based on the activating player.
        #[serde(default)]
        played_by: Option<usize>,
    },
}

impl TrainerCoinEffectRoute {
    pub fn effect_trainer(&self) -> &TrainerCard {
        match self {
            Self::Direct { trainer } => trainer,
            Self::Penny { copied, .. } => copied,
            Self::Stadium { stadium, .. } => stadium,
        }
    }
}

/// A selected Misty source awaiting its printed pre-coin Water-Pokemon target choice.
/// Copied-source details are retained only by the referee and acting player.
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum MistySourceRoute {
    Direct {
        misty: TrainerCard,
    },
    Penny {
        penny: TrainerCard,
        misty: TrainerCard,
        shuffle_owner: usize,
    },
    Portrait {
        misty: TrainerCard,
    },
    PortraitPenny {
        penny: TrainerCard,
        misty: TrainerCard,
        shuffle_owner: usize,
    },
}

impl MistySourceRoute {
    pub fn effect_trainer(&self) -> &TrainerCard {
        match self {
            Self::Direct { misty }
            | Self::Penny { misty, .. }
            | Self::Portrait { misty }
            | Self::PortraitPenny { misty, .. } => misty,
        }
    }

    pub fn penny_shuffle_owner(&self) -> Option<usize> {
        match self {
            Self::Penny { shuffle_owner, .. } | Self::PortraitPenny { shuffle_owner, .. } => {
                Some(*shuffle_owner)
            }
            Self::Direct { .. } | Self::Portrait { .. } => None,
        }
    }

    pub fn outer_is_trainer(&self) -> bool {
        matches!(self, Self::Direct { .. } | Self::Penny { .. })
    }
}

#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub struct PendingMistyTargetChoice {
    pub actor: usize,
    pub original_action: SimpleAction,
    pub original_is_stack: bool,
    /// Hidden copied-source detail is removed from the opponent's observation.
    pub route: Option<MistySourceRoute>,
}

#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub struct PendingTrainerCoinChoice {
    pub actor: usize,
    pub original_action: SimpleAction,
    pub original_is_stack: bool,
    /// Complete ordered public batch (`true` = heads).
    pub flips: Vec<bool>,
    pub luxury_coin_in_play_idx: usize,
    /// Public Water-Pokemon target fixed before a Misty batch was sampled.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub misty_target_in_play_idx: Option<usize>,
    /// Hidden copied-source detail is removed from the opponent's observation.
    pub route: Option<TrainerCoinEffectRoute>,
}

#[derive(Debug, Clone, Copy, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum LuxuryCoinDecision {
    Keep,
    Reroll,
}

#[derive(Debug, Clone, Hash, PartialEq, Eq)]
pub(crate) struct LuxuryCoinResolutionEvent {
    pub actor: usize,
    pub initial_faces: Vec<bool>,
    pub decision: LuxuryCoinDecision,
    pub replacement_faces: Option<Vec<bool>>,
}

#[derive(Clone, Default, Hash, PartialEq, Eq)]
pub(crate) struct LuxuryCoinResolutionEvents(Vec<LuxuryCoinResolutionEvent>);

impl fmt::Debug for LuxuryCoinResolutionEvents {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("<luxury coin resolution events>")
    }
}

impl LuxuryCoinResolutionEvents {
    pub fn push(&mut self, event: LuxuryCoinResolutionEvent) {
        self.0.push(event);
    }
    pub fn iter(&self) -> impl Iterator<Item = &LuxuryCoinResolutionEvent> {
        self.0.iter()
    }
    pub fn clear(&mut self) {
        self.0.clear();
    }
}

#[derive(Clone, Copy, Hash, PartialEq, Eq)]
pub(crate) enum PublicRevealKind {
    DeckPrefixThenShuffle,
}

#[derive(Clone, Hash, PartialEq, Eq)]
pub(crate) struct PublicRevealEvent {
    pub zone_owner: usize,
    pub cause: String,
    pub kind: PublicRevealKind,
    /// Exact pre-shuffle reveal order, retained only for the referee transcript.
    pub cards: Vec<Card>,
}

/// Transient public reveal evidence. Policies receive durable knowledge derived from this queue,
/// never the temporal payload itself.
#[derive(Clone, Default, Hash, PartialEq, Eq)]
pub(crate) struct PublicRevealEvents(Vec<PublicRevealEvent>);

impl fmt::Debug for PublicRevealEvents {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("<public reveal events redacted>")
    }
}

impl PublicRevealEvents {
    pub fn push(&mut self, event: PublicRevealEvent) {
        self.0.push(event);
    }
    pub fn iter(&self) -> impl Iterator<Item = &PublicRevealEvent> {
        self.0.iter()
    }
    pub fn clear(&mut self) {
        self.0.clear();
    }
}

fn all_false(flags: &[bool; 2]) -> bool {
    !flags[0] && !flags[1]
}

#[derive(Debug, Clone, Hash, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct State {
    // Turn State
    pub winner: Option<GameOutcome>,
    pub points: [u8; 2],
    /// Points actually awarded during the turn in progress, indexed by recipient. This is public
    /// match history; denied points never enter it.
    #[serde(default)]
    pub points_gained_this_turn: [u8; 2],
    /// Points each player was awarded during their most recently completed own turn. A point
    /// received during the opponent's turn is deliberately excluded.
    #[serde(default)]
    pub points_gained_during_own_last_turn: [u8; 2],
    pub turn_count: u8, // Global turn count. Matches TCGPocket app.
    /// Observation/search metadata only. Concealed setup slots are not an empty board.
    /// Referee states keep this false and retain the actual starting Pokemon.
    #[serde(default, skip_serializing_if = "std::ops::Not::not")]
    pub setup_opponent_hidden: bool,
    // Player that needs to select from playable actions. Might not be aligned
    // with coin toss and the parity, see Sabrina.
    pub current_player: usize,
    pub(crate) end_turn_pending: bool,
    pub move_generation_stack: Vec<(usize, Vec<SimpleAction>)>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pending_attack_coin_choice: Option<PendingAttackCoinChoice>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pending_misty_target_choice: Option<PendingMistyTargetChoice>,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pending_trainer_coin_choice: Option<PendingTrainerCoinChoice>,
    #[serde(skip, default)]
    pub(crate) private_reveal_events: PrivateRevealEvents,
    #[serde(skip, default)]
    pub(crate) public_reveal_events: PublicRevealEvents,
    #[serde(skip, default)]
    pub(crate) luxury_coin_resolution_events: LuxuryCoinResolutionEvents,

    // Core state
    pub energy_zone: [EnergyZone; 2],
    pub hands: [Vec<Card>; 2],
    pub decks: [Deck; 2],
    pub discard_piles: [Vec<Card>; 2],
    pub discard_energies: [Vec<EnergyType>; 2],
    // 0 index is the active pokemon, 1..4 are the bench
    pub in_play_pokemon: [[Option<PlayedCard>; 4]; 2],
    // Stadium card currently in play (affects both players)
    pub active_stadium: Option<Card>,
    #[serde(default)]
    pub active_stadium_owner: Option<usize>,

    // Turn Flags (remember to reset these in reset_turn_states)
    pub(crate) has_played_support: bool,
    pub(crate) has_retreated: bool,
    /// A Stadium card has been played during the current player's turn. This is distinct from
    /// using an activated Stadium effect, which is tracked per player below.
    #[serde(default)]
    pub(crate) has_played_stadium: bool,
    pub has_used_stadium: [bool; 2], // Tracks if each player has used the stadium this turn
    /// Victory Star is limited across all copies a player controls, not per card.
    #[serde(default, skip_serializing_if = "all_false")]
    pub victory_star_used_this_turn: [bool; 2],
    #[serde(default, skip_serializing_if = "all_false")]
    pub luxury_coin_used_this_turn: [bool; 2],
    pub(crate) knocked_out_by_opponent_attack_this_turn: bool,
    pub(crate) knocked_out_by_opponent_attack_last_turn: bool,
    // Energy types of the Pokémon that were Knocked Out by damage from an opponent's attack
    // during the current/previous turn (companions to the two flags above, for type-filtered
    // vengeance attacks like Zarude's Dark Vengeance: "If any of your [D] Pokémon were Knocked
    // Out ..."). Fossils have no energy type and are only covered by the untyped flags.
    #[serde(default)]
    pub(crate) knocked_out_types_by_opponent_attack_this_turn: Vec<EnergyType>,
    #[serde(default)]
    pub(crate) knocked_out_types_by_opponent_attack_last_turn: Vec<EnergyType>,
    // Name of the attack (if any) each player used during their current/previous own turn
    // (e.g. for Vanilluxe's "Sweets Relay": "If 1 of your Pokémon used Sweets Relay during
    // your last turn, this attack does more damage.").
    pub(crate) attack_name_used_this_turn: [Option<String>; 2],
    pub(crate) attack_name_used_last_turn: [Option<String>; 2],
    // Number of times each player has used each named attack during the entire game (e.g. for
    // Alcremie's "Sweets Overload": "This attack does 40 damage for each time your Pokémon used
    // Sweets Relay during this game."). Using BTreeMap to keep State hashable.
    pub(crate) attack_name_used_count: [BTreeMap<String, u32>; 2],
    // Number of times each player's own Pokémon have been Knocked Out over the whole game (e.g.
    // for Kingambit's "Overlord's Blade": "This attack does 40 more damage for each time your
    // Pokémon have been Knocked Out during this game."). Indexed by the player who LOST the
    // Pokémon, not the one who scored the knockout.
    #[serde(default)]
    pub(crate) own_knockouts_this_game: [u32; 2],
    // Maps turn to a vector of effects (cards) for that turn. Using BTreeMap to keep State hashable.
    turn_effects: BTreeMap<u8, Vec<TurnEffect>>,
}

fn is_misty_trainer(trainer: &TrainerCard) -> bool {
    matches!(
        CardId::from_card_id(&trainer.id),
        Some(CardId::A1220Misty | CardId::A1267Misty)
    )
}

fn misty_route_matches_original(
    route: &MistySourceRoute,
    original: &SimpleAction,
    actor: usize,
) -> bool {
    match (route, original) {
        (MistySourceRoute::Direct { misty }, SimpleAction::Play { trainer_card }) => {
            is_misty_trainer(misty) && trainer_card.id == misty.id
        }
        (
            MistySourceRoute::Penny {
                penny,
                misty,
                shuffle_owner,
            },
            SimpleAction::Play { trainer_card },
        ) => {
            actor < 2
                && *shuffle_owner == 1 - actor
                && penny.name == "Penny"
                && trainer_card.id == penny.id
                && is_misty_trainer(misty)
        }
        (MistySourceRoute::Portrait { misty }, SimpleAction::UseAbility { .. }) => {
            is_misty_trainer(misty)
        }
        (
            MistySourceRoute::PortraitPenny {
                penny,
                misty,
                shuffle_owner,
            },
            SimpleAction::UseAbility { .. },
        ) => {
            actor < 2
                && *shuffle_owner == 1 - actor
                && penny.name == "Penny"
                && is_misty_trainer(misty)
        }
        _ => false,
    }
}

impl State {
    /// Drop forged, legacy, or redacted pending-choice payloads when a State is adopted by Game.
    /// A valid referee checkpoint must retain the private route and its matching public frame.
    pub(crate) fn sanitize_pending_choice_state(&mut self) {
        let pending_conflict = (self.pending_misty_target_choice.is_some()
            && self.pending_trainer_coin_choice.is_some())
            || (self.pending_attack_coin_choice.is_some()
                && (self.pending_misty_target_choice.is_some()
                    || self.pending_trainer_coin_choice.is_some()));
        let target_frame_valid = self.pending_misty_target_choice.as_ref().is_some_and(|pending| {
            pending.route.as_ref().is_some_and(|route| {
                misty_route_matches_original(route, &pending.original_action, pending.actor)
            }) && !pending_conflict
                && self.move_generation_stack.last().is_some_and(|(actor, choices)| {
                    *actor == pending.actor
                        && !choices.is_empty()
                        && choices.iter().all(|choice| {
                            matches!(choice, SimpleAction::ChooseMistyTarget { in_play_idx }
                                if self.in_play_pokemon.get(pending.actor)
                                    .and_then(|slots| slots.get(*in_play_idx))
                                    .and_then(Option::as_ref)
                                    .is_some_and(|pokemon| self.pokemon_is_type(pokemon, EnergyType::Water)))
                        })
                })
        });
        if self.pending_misty_target_choice.is_some() && !target_frame_valid {
            let pending_actor = self.pending_misty_target_choice.as_ref().unwrap().actor;
            self.pending_misty_target_choice = None;
            if self
                .move_generation_stack
                .last()
                .is_some_and(|(actor, choices)| {
                    (*actor == pending_actor && choices.is_empty())
                        || choices
                            .iter()
                            .any(|choice| matches!(choice, SimpleAction::ChooseMistyTarget { .. }))
                })
            {
                self.move_generation_stack.pop();
            }
        }

        let trainer_frame_valid = self.pending_trainer_coin_choice.as_ref().is_some_and(|pending| {
            let misty = pending.route.as_ref().is_some_and(|route| {
                is_misty_trainer(route.effect_trainer())
            });
            let route_valid = pending.route.as_ref().is_some_and(|route| match route {
                TrainerCoinEffectRoute::Direct { trainer } if is_misty_trainer(trainer) => {
                    matches!(&pending.original_action, SimpleAction::Play { trainer_card } if trainer_card.id == trainer.id)
                }
                TrainerCoinEffectRoute::Penny { copied, shuffle_owner }
                    if is_misty_trainer(copied) =>
                {
                    pending.actor < 2
                        && *shuffle_owner == 1 - pending.actor
                        && matches!(&pending.original_action, SimpleAction::Play { trainer_card } if trainer_card.name == "Penny")
                }
                TrainerCoinEffectRoute::Penny { shuffle_owner, .. } => {
                    pending.actor < 2 && *shuffle_owner == 1 - pending.actor
                }
                TrainerCoinEffectRoute::Direct { .. } | TrainerCoinEffectRoute::Stadium { .. } => true,
            });
            let source_valid = self.in_play_pokemon
                .get(pending.actor)
                .and_then(|slots| slots.get(pending.luxury_coin_in_play_idx))
                .and_then(Option::as_ref)
                .is_some_and(|pokemon| {
                    get_in_play_ability_mechanic(self, pokemon) == Some(&AbilityMechanic::LuxuryCoin)
                });
            let target_valid = match (misty, pending.misty_target_in_play_idx) {
                (false, None) => true,
                (true, Some(index)) => self.in_play_pokemon
                    .get(pending.actor)
                    .and_then(|slots| slots.get(index))
                    .and_then(Option::as_ref)
                    .is_some_and(|pokemon| self.pokemon_is_type(pokemon, EnergyType::Water)),
                _ => false,
            };
            route_valid
                && source_valid
                && target_valid
                && !pending_conflict
                && self.pending_misty_target_choice.is_none()
                && self.move_generation_stack.last().is_some_and(|(actor, choices)| {
                    *actor == pending.actor
                        && choices.len() == 2
                        && choices
                            .iter()
                            .filter(|choice| matches!(choice, SimpleAction::KeepTrainerCoinResults))
                            .count()
                            == 1
                        && choices
                            .iter()
                            .filter(|choice| matches!(choice, SimpleAction::RerollTrainerCoins { luxury_coin_in_play_idx } if *luxury_coin_in_play_idx == pending.luxury_coin_in_play_idx))
                            .count()
                            == 1
                })
        });
        if self.pending_trainer_coin_choice.is_some() && !trainer_frame_valid {
            let pending_actor = self.pending_trainer_coin_choice.as_ref().unwrap().actor;
            self.pending_trainer_coin_choice = None;
            if self
                .move_generation_stack
                .last()
                .is_some_and(|(actor, choices)| {
                    (*actor == pending_actor && choices.is_empty())
                        || choices.iter().any(|choice| {
                            matches!(
                                choice,
                                SimpleAction::KeepTrainerCoinResults
                                    | SimpleAction::RerollTrainerCoins { .. }
                            )
                        })
                })
            {
                self.move_generation_stack.pop();
            }
        }
    }

    pub fn new(deck_a: &Deck, deck_b: &Deck) -> Self {
        Self {
            winner: None,
            points: [0, 0],
            points_gained_this_turn: [0, 0],
            points_gained_during_own_last_turn: [0, 0],
            turn_count: 0,
            setup_opponent_hidden: false,
            current_player: 0,
            end_turn_pending: false,
            move_generation_stack: Vec::new(),
            pending_attack_coin_choice: None,
            pending_misty_target_choice: None,
            pending_trainer_coin_choice: None,
            private_reveal_events: PrivateRevealEvents::default(),
            public_reveal_events: PublicRevealEvents::default(),
            luxury_coin_resolution_events: LuxuryCoinResolutionEvents::default(),
            energy_zone: [EnergyZone::default(), EnergyZone::default()],
            hands: [Vec::new(), Vec::new()],
            decks: [deck_a.clone(), deck_b.clone()],
            discard_piles: [Vec::new(), Vec::new()],
            discard_energies: [Vec::new(), Vec::new()],
            in_play_pokemon: [[None, None, None, None], [None, None, None, None]],
            active_stadium: None,
            active_stadium_owner: None,
            has_played_support: false,
            has_retreated: false,
            has_played_stadium: false,
            has_used_stadium: [false, false],
            victory_star_used_this_turn: [false, false],
            luxury_coin_used_this_turn: [false, false],

            knocked_out_by_opponent_attack_this_turn: false,
            knocked_out_by_opponent_attack_last_turn: false,
            knocked_out_types_by_opponent_attack_this_turn: Vec::new(),
            knocked_out_types_by_opponent_attack_last_turn: Vec::new(),
            attack_name_used_this_turn: [None, None],
            attack_name_used_last_turn: [None, None],
            attack_name_used_count: [BTreeMap::new(), BTreeMap::new()],
            own_knockouts_this_game: [0, 0],
            turn_effects: BTreeMap::new(),
        }
    }

    pub fn get_active_stadium_name(&self) -> Option<String> {
        self.active_stadium.as_ref().map(|c| c.get_name())
    }

    pub fn set_active_stadium(&mut self, stadium: Card) -> Option<Card> {
        self.active_stadium_owner = None;
        self.active_stadium.replace(stadium)
    }

    pub fn set_active_stadium_for_player(
        &mut self,
        player: usize,
        stadium: Card,
    ) -> Option<(Card, Option<usize>)> {
        let old_stadium = self.active_stadium.replace(stadium);
        let old_owner = self.active_stadium_owner.replace(player);
        old_stadium.map(|stadium| (stadium, old_owner))
    }

    pub fn take_active_stadium(&mut self) -> Option<(Card, Option<usize>)> {
        let stadium = self.active_stadium.take();
        let owner = self.active_stadium_owner.take();
        stadium.map(|stadium| (stadium, owner))
    }

    /// Recomputes every board-conditional HP bonus on every Pokémon in play: Starting Plains,
    /// team-wide HP abilities, and per-attached-Energy HP abilities.
    ///
    /// Both depend on what else is on the board, so this has to run after any change to the active
    /// Stadium *or* to the set of Pokémon in play — including a Pokémon leaving play, which can
    /// shrink the effective HP of the ones left behind and knock them out.
    pub(crate) fn refresh_hp_bonuses_all(&mut self) {
        let starting_plains_active = is_starting_plains_active(self);
        for player in 0..2 {
            let ability_bonuses = self.ability_hp_bonuses(player);
            // Types are resolved up-front because `pokemon_energy_types` needs `&self` while the
            // loop below holds a `&mut` borrow of the board.
            let energy_types: Vec<(usize, Vec<EnergyType>)> = self
                .enumerate_in_play_pokemon(player)
                .map(|(idx, pokemon)| (idx, self.pokemon_energy_types(pokemon)))
                .collect();
            for (idx, types) in energy_types {
                let pokemon = self.in_play_pokemon[player][idx]
                    .as_ref()
                    .expect("Pokemon should be there, it was just enumerated");
                let own_energy_bonus = match get_in_play_ability_mechanic(self, pokemon) {
                    Some(AbilityMechanic::IncreaseHpPerAttachedEnergy {
                        energy_type,
                        amount,
                    }) => {
                        pokemon
                            .get_effective_attached_energy(self, player)
                            .iter()
                            .filter(|energy| *energy == energy_type)
                            .count() as u32
                            * amount
                    }
                    _ => 0,
                };
                let bonus = own_energy_bonus
                    + ability_bonuses
                        .iter()
                        .filter(|(bonus_type, _)| types.contains(bonus_type))
                        .map(|(_, amount)| *amount)
                        .sum::<u32>();
                let pokemon = self.in_play_pokemon[player][idx]
                    .as_mut()
                    .expect("Pokemon should be there, it was just enumerated");
                pokemon.refresh_starting_plains_bonus(starting_plains_active);
                pokemon.set_ability_hp_bonus(bonus);
            }
        }
    }

    /// Every Energy type a Pokémon **in play** counts as right now.
    ///
    /// Normally that is just its printed type, but Urshifu's Double Type ("As long as this Pokémon
    /// is in play, it is [W] and [F] type") gives it two. This is the single chokepoint for the
    /// question — Weakness, the type damage boosts, the "each of your [X] Pokémon" filters and the
    /// typed Retreat discounts all go through here (or through [`Self::pokemon_is_type`]) rather
    /// than reading `PlayedCard::get_energy_type` directly, so a dual-typed Pokémon cannot be
    /// recognised by one of them and missed by another. `PlayedCard::get_energy_type` remains the
    /// *printed* type and is correct only where the printed value is what is wanted (display, and
    /// cards that are not in play).
    ///
    /// Reads the Ability through `get_in_play_ability_mechanic`, so Prickly Powder's `NoAbilities`
    /// reverts the Pokémon to its printed type.
    pub(crate) fn pokemon_energy_types(&self, pokemon: &PlayedCard) -> Vec<EnergyType> {
        if let Some(AbilityMechanic::DualType { types }) =
            get_in_play_ability_mechanic(self, pokemon)
        {
            return types.to_vec();
        }
        pokemon.get_energy_type().into_iter().collect()
    }

    /// Whether an *attack's* non-damage effect aimed at this Pokémon is prevented — Regice's
    /// Crystal Body (A2 034): "Prevent all effects of attacks used by your opponent's Pokémon done
    /// to this Pokémon."
    ///
    /// This is the single chokepoint for that question. Attack code calls it (or
    /// [`Self::apply_attack_status_condition`], which is built on it) immediately before touching
    /// the defending Pokémon, so the shield covers Special Conditions, lingering `CardEffect`s,
    /// Energy and Tool removal, Energy-type changes, forced switches and devolution alike.
    ///
    /// Deliberately *not* called from Ability, Trainer or Stadium code: Crystal Body names attacks
    /// only. Damage is not an effect and is applied through the normal damage path regardless.
    /// Whether attack EFFECTS (Special Conditions, forced switches, energy discards, …) are
    /// prevented on this Pokémon. Damage is unaffected — only the rider is.
    ///
    /// Crystal Body, Clear Veil, and a current full damage-and-effects shield all protect attack
    /// effects here. Damage-only protection deliberately does not grant this effect immunity.
    /// Ability lookup stays suppression-aware; an earned temporary shield remains independent
    /// of the holder's current ability.
    pub(crate) fn prevents_attack_effects(&self, player: usize, in_play_idx: usize) -> bool {
        self.in_play_pokemon[player][in_play_idx]
            .as_ref()
            .is_some_and(|pokemon| {
                has_in_play_ability_mechanic(self, pokemon, &AbilityMechanic::PreventAttackEffects)
                    || crate::tools::has_tool(pokemon, crate::card_ids::CardId::B4149ClearVeil)
                    || pokemon
                        .get_effective_card_effects(self)
                        .contains(&crate::effects::CardEffect::PreventAllDamageAndEffects)
            })
    }

    /// [`Self::apply_status_condition`] for a Special Condition inflicted by an *attack*, which
    /// Crystal Body shields against. Every attack that gives a Pokémon a Special Condition goes
    /// through here; Abilities and Trainers keep using `apply_status_condition` directly.
    pub(crate) fn apply_attack_status_condition(
        &mut self,
        player: usize,
        in_play_idx: usize,
        status: StatusCondition,
    ) {
        if self.prevents_attack_effects(player, in_play_idx) {
            debug!("Crystal Body: preventing the attack's {status:?} effect");
            return;
        }
        self.apply_status_condition(player, in_play_idx, status);
    }

    /// Whether a Pokémon in play counts as `energy_type` right now. See
    /// [`Self::pokemon_energy_types`].
    pub(crate) fn pokemon_is_type(&self, pokemon: &PlayedCard, energy_type: EnergyType) -> bool {
        self.pokemon_energy_types(pokemon).contains(&energy_type)
    }

    /// The `IncreaseHpForTypeInPlay` bonuses `player` currently has in play, as (type, amount)
    /// pairs. Multiple copies stack, hence a list rather than a single value.
    fn ability_hp_bonuses(&self, player: usize) -> Vec<(EnergyType, u32)> {
        self.enumerate_in_play_pokemon(player)
            .filter_map(
                |(_, pokemon)| match get_in_play_ability_mechanic(self, pokemon) {
                    Some(AbilityMechanic::IncreaseHpForTypeInPlay {
                        energy_type,
                        amount,
                    }) => Some((*energy_type, *amount)),
                    _ => None,
                },
            )
            .collect()
    }

    pub fn debug_string(&self) -> String {
        format!(
            "P1 Hand:\t{:?}\n\
            P1 InPlay:\t{:?}\n\
            P2 InPlay:\t{:?}\n\
            P2 Hand:\t{:?}",
            to_canonical_names(self.hands[0].as_slice()),
            format_cards(&self.in_play_pokemon[0]),
            format_cards(&self.in_play_pokemon[1]),
            to_canonical_names(self.hands[1].as_slice())
        )
    }

    pub fn initialize(deck_a: &Deck, deck_b: &Deck, rng: &mut impl Rng) -> Self {
        let mut state = Self::new(deck_a, deck_b);

        // Shuffle the decks before starting the game and have players
        //  draw 5 cards each to start
        for deck in &mut state.decks {
            deck.shuffle(true, rng);
        }
        for _ in 0..5 {
            state.maybe_draw_card(0);
            state.maybe_draw_card(1);
        }
        // Flip a coin to determine the starting player
        state.current_player = rng.gen_range(0..2);

        // Pre-populate each player's `next` energy. On turn 1, neither player has rotated yet,
        // so both keep `current = None`. The player going second's queue will rotate at turn 2,
        // promoting `next` into `current`; the player going first's queue rotates at turn 3.
        state.energy_zone[0].next = Some(roll_energy(&state.decks[0], rng));
        state.energy_zone[1].next = Some(roll_energy(&state.decks[1], rng));

        state
    }

    pub fn get_remaining_hp(&self, player: usize, index: usize) -> u32 {
        self.in_play_pokemon[player][index]
            .as_ref()
            .unwrap()
            .get_remaining_hp()
    }

    pub(crate) fn remove_card_from_hand(&mut self, current_player: usize, card: &Card) {
        let index = self.hands[current_player]
            .iter()
            .position(|x| x == card)
            .expect("Player hand should contain card to remove");
        self.hands[current_player].swap_remove(index);
    }

    pub(crate) fn remove_card_from_deck(&mut self, player: usize, card: &Card) {
        let pos = self.decks[player]
            .cards
            .iter()
            .position(|c| c == card)
            .expect("Evolution card should be in deck");
        self.decks[player].cards.remove(pos);
    }

    pub(crate) fn discard_card_from_hand(&mut self, current_player: usize, card: &Card) {
        self.remove_card_from_hand(current_player, card);
        self.discard_piles[current_player].push(card.clone());
    }

    /// Returns an iterator over supporter cards in a player's hand
    pub(crate) fn iter_hand_supporters(&self, player: usize) -> impl Iterator<Item = &Card> {
        self.hands[player].iter().filter(|card| card.is_support())
    }

    pub(crate) fn maybe_draw_card(&mut self, player: usize) {
        if self.hands[player].len() >= 10 {
            debug!(
                "Player {} cannot draw a card, hand is full (10 cards)",
                player + 1
            );
            return;
        }
        if let Some(card) = self.decks[player].draw() {
            self.hands[player].push(card.clone());
            debug!(
                "Player {} drew: {:?}, now hand is: {:?} and deck has {} cards",
                player + 1,
                canonical_name(&card),
                to_canonical_names(&self.hands[player]),
                self.decks[player].cards.len()
            );
        } else {
            debug!("Player {} cannot draw a card, deck is empty", player + 1);
        }
    }

    pub(crate) fn transfer_card_from_deck_to_hand(&mut self, player: usize, card: &Card) {
        // Remove from deck and add to hand
        let pos = self.decks[player]
            .cards
            .iter()
            .position(|c| c == card)
            .expect("Card must exist in deck to transfer to hand");
        self.decks[player].cards.remove(pos);
        self.hands[player].push(card.clone());
    }

    /// Heal Block (Claydol A3a 031): "Pokémon (both yours and your opponent's) can't be healed."
    ///
    /// Symmetric, so a single board-wide check over both players covers it. Every healing effect in
    /// the engine — Abilities, attacks, Trainer cards, Tools/berries and Pokémon Checkup — funnels
    /// through `heal_pokemon`/`heal_each_pokemon` and is gated here, rather than each site
    /// re-checking. `PlayedCard::heal_raw` is the deliberate escape hatch for *moving* damage
    /// counters, which is not healing and is not blocked.
    pub(crate) fn is_healing_blocked(&self) -> bool {
        (0..2).any(|player| {
            self.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
                has_in_play_ability_mechanic(self, pokemon, &AbilityMechanic::PreventAllHealing)
            })
        })
    }

    /// Heal `amount` damage from one Pokémon in play, honouring Heal Block. Returns how many
    /// damage counters were actually removed, which callers such as Espeon ex's
    /// "heal, and if you do, discard an Energy" need in order to decide whether their *if you do*
    /// clause fires at all.
    pub(crate) fn heal_pokemon(&mut self, player: usize, in_play_idx: usize, amount: u32) -> u32 {
        if self.is_healing_blocked() {
            return 0;
        }
        let Some(pokemon) = self.in_play_pokemon[player][in_play_idx].as_mut() else {
            return 0;
        };
        let healed = amount.min(pokemon.get_damage_counters());
        pokemon.heal_raw(amount);
        healed
    }

    /// Heal `amount` damage from every Pokémon `player` has in play that satisfies `is_eligible`,
    /// honouring Heal Block. The board-wide counterpart of [`Self::heal_pokemon`].
    pub(crate) fn heal_each_pokemon(
        &mut self,
        player: usize,
        amount: u32,
        is_eligible: impl Fn(&PlayedCard) -> bool,
    ) {
        if self.is_healing_blocked() {
            return;
        }
        for pokemon in self.in_play_pokemon[player].iter_mut().flatten() {
            if is_eligible(pokemon) {
                pokemon.heal_raw(amount);
            }
        }
    }

    /// Move one copy of `card` from `player`'s discard pile into their hand (Delcatty's Search for
    /// Friends). Silently does nothing if the card is no longer there, so a choice that was
    /// generated before some other effect emptied the pile degrades to a no-op instead of panicking.
    pub(crate) fn transfer_card_from_discard_to_hand(&mut self, player: usize, card: &Card) {
        let Some(pos) = self.discard_piles[player].iter().position(|c| c == card) else {
            return;
        };
        self.discard_piles[player].remove(pos);
        self.hands[player].push(card.clone());
    }

    pub(crate) fn transfer_card_from_hand_to_deck(&mut self, player: usize, card: &Card) {
        // Remove from hand and add to deck
        let pos = self.hands[player]
            .iter()
            .position(|c| c == card)
            .expect("Card must exist in hand to transfer to deck");
        self.hands[player].remove(pos);
        self.decks[player].cards.push(card.clone());
    }

    pub(crate) fn iter_deck_pokemon(&self, player: usize) -> impl Iterator<Item = &Card> {
        self.decks[player]
            .cards
            .iter()
            .filter(|card| matches!(card, Card::Pokemon(_)))
    }

    pub fn iter_hand_pokemon(&self, player: usize) -> impl Iterator<Item = &Card> {
        self.hands[player]
            .iter()
            .filter(|card| matches!(card, Card::Pokemon(_)))
    }

    /// Rotates `player`'s energy zone: the previously-visible `next` becomes the new `current`
    /// (the energy attachable this turn), and a fresh `next` is rolled from the deck's energy
    /// types using the shared rng. Called from `advance_turn` for the player about to take their
    /// turn.
    pub(crate) fn rotate_energy_zone(&mut self, player: usize, rng: &mut impl Rng) {
        self.energy_zone[player].current = self.energy_zone[player].next.take();
        // A redacted search state has no declared opponent energy menu. Preserve
        // the visible preview in current, and leave the further future unknown.
        self.energy_zone[player].next = if self.decks[player].energy_types.is_empty() {
            None
        } else {
            Some(roll_energy(&self.decks[player], rng))
        };
    }

    pub(crate) fn end_turn_maintenance(&mut self) {
        // Maintain PlayedCard state for _all_ players
        for i in 0..2 {
            self.in_play_pokemon[i].iter_mut().for_each(|x| {
                if let Some(played_card) = x {
                    played_card.end_turn_maintenance();
                }
            });
        }

        self.has_played_support = false;
        self.has_retreated = false;
        self.has_played_stadium = false;
        self.has_used_stadium[self.current_player] = false;
        self.victory_star_used_this_turn[self.current_player] = false;
        self.luxury_coin_used_this_turn[self.current_player] = false;
    }

    /// Reconcile the continuous Soothing Wind / Flower Shield recovery for the one Pokémon
    /// that has just received Energy. Ability lookup is suppression-aware and belongs to the
    /// recipient's side; moving an opponent's Energy therefore cannot borrow the acting side's
    /// protection.
    pub(crate) fn apply_soothing_wind_to_pokemon(
        &mut self,
        player: usize,
        in_play_idx: usize,
    ) {
        let is_protected = self.in_play_pokemon[player][in_play_idx]
            .as_ref()
            .is_some_and(|recipient| {
                self.in_play_pokemon[player]
                    .iter()
                    .flatten()
                    .any(|pokemon| match get_in_play_ability_mechanic(self, pokemon) {
                        Some(AbilityMechanic::SoothingWind { energy_type }) => match energy_type {
                            None => !recipient.attached_energy.is_empty(),
                            Some(t) => recipient.attached_energy.contains(t),
                        },
                        _ => false,
                    })
            });
        if is_protected {
            debug!(
                "SoothingWind: newly energized Pokémon in slot {in_play_idx} recovers from Special Conditions"
            );
            self.in_play_pokemon[player][in_play_idx]
                .as_mut()
                .unwrap()
                .cure_status_conditions();
        }
    }

    /// Clear status conditions from energy-bearing Pokémon on a player's side.
    /// `energy_type` restricts which Pokémon are cured:
    ///   - `None`    → any energy (Soothing Wind / Ogerpon ex)
    ///   - `Some(t)` → only Pokémon that have that specific energy type attached (Flower Shield / Comfey)
    pub(crate) fn apply_soothing_wind_for_player(
        &mut self,
        player: usize,
        energy_type: Option<&EnergyType>,
    ) {
        for slot in self.in_play_pokemon[player].iter_mut().flatten() {
            let is_protected = match energy_type {
                None => !slot.attached_energy.is_empty(),
                Some(t) => slot.attached_energy.contains(t),
            };
            if is_protected {
                slot.cure_status_conditions();
            }
        }
    }

    /// Reconcile currently effective Soothing Wind / Flower Shield sources after a
    /// board-wide Basic-Ability suppressor has actually left play.
    pub(crate) fn apply_effective_soothing_wind_for_all_players(&mut self) {
        for player in 0..2 {
            let energy_filters: Vec<Option<EnergyType>> = self.in_play_pokemon[player]
                .iter()
                .flatten()
                .filter_map(|pokemon| match get_in_play_ability_mechanic(self, pokemon) {
                    Some(AbilityMechanic::SoothingWind { energy_type }) => Some(*energy_type),
                    _ => None,
                })
                .collect();
            for energy_filter in energy_filters {
                self.apply_soothing_wind_for_player(player, energy_filter.as_ref());
            }
        }
    }

    pub(crate) fn set_pending_will_first_heads(&mut self) {
        self.add_turn_effect(TurnEffect::ForceFirstHeads, 0);
    }

    pub(crate) fn has_pending_will_first_heads(&self) -> bool {
        self.get_current_turn_effects()
            .iter()
            .any(|effect| matches!(effect, TurnEffect::ForceFirstHeads))
    }

    pub(crate) fn consume_pending_will_first_heads(&mut self) -> bool {
        if let Some(turn_effects) = self.turn_effects.get_mut(&self.turn_count) {
            if let Some(pos) = turn_effects
                .iter()
                .position(|effect| matches!(effect, TurnEffect::ForceFirstHeads))
            {
                turn_effects.remove(pos);
                return true;
            }
        }
        false
    }

    /// Adds an effect card that will remain active for a specified number of turns.
    ///
    /// # Arguments
    ///
    /// * `effect` - The effect to be added.
    /// * `duration` - The number of turns the effect should remain active.
    ///   0 means current turn only,
    ///   1 means current turn and the next turn, etc.
    pub(crate) fn add_turn_effect(&mut self, effect: TurnEffect, duration: u8) {
        for turn_offset in 0..(duration + 1) {
            let target_turn = self.turn_count + turn_offset;
            self.turn_effects
                .entry(target_turn)
                .or_default()
                .push(effect.clone());
            trace!(
                "Adding effect {:?} for {} turns, current turn: {}, target turn: {}",
                effect,
                duration,
                self.turn_count,
                target_turn
            );
        }
    }

    /// Retrieves all effects scheduled for the current turn
    /// The turn effects registered for `turn` (kpr looks ahead to the owner's next attack turn).
    pub(crate) fn get_turn_effects(&self, turn: u8) -> Vec<TurnEffect> {
        self.turn_effects.get(&turn).cloned().unwrap_or_default()
    }

    pub(crate) fn get_current_turn_effects(&self) -> Vec<TurnEffect> {
        self.turn_effects
            .get(&self.turn_count)
            .cloned()
            .unwrap_or_default()
    }

    pub fn enumerate_in_play_pokemon(
        &self,
        player: usize,
    ) -> impl Iterator<Item = (usize, &PlayedCard)> {
        self.in_play_pokemon[player]
            .iter()
            .enumerate()
            .filter(|(_, x)| x.is_some())
            .map(|(i, x)| (i, x.as_ref().unwrap()))
    }

    // e.g. returns (1, Weezing) if player 1 has Weezing in 1st bench slot
    pub fn enumerate_bench_pokemon(
        &self,
        player: usize,
    ) -> impl Iterator<Item = (usize, &PlayedCard)> {
        self.enumerate_in_play_pokemon(player)
            .filter(|(i, _)| *i != 0)
    }

    pub(crate) fn queue_draw_action(&mut self, actor: usize, amount: u8) {
        self.move_generation_stack
            .push((actor, vec![SimpleAction::DrawCard { amount }]));
    }

    pub fn maybe_get_active(&self, player: usize) -> Option<&PlayedCard> {
        self.in_play_pokemon[player][0].as_ref()
    }

    pub fn get_active(&self, player: usize) -> &PlayedCard {
        self.in_play_pokemon[player][0]
            .as_ref()
            .expect("Active Pokemon should be there")
    }

    pub(crate) fn get_active_mut(&mut self, player: usize) -> &mut PlayedCard {
        self.in_play_pokemon[player][0]
            .as_mut()
            .expect("Active Pokemon should be there")
    }

    /// Apply a status condition to a Pokémon in play, enforcing all immunity rules.
    /// This is the single authoritative path for setting status conditions.
    pub fn apply_status_condition(
        &mut self,
        player: usize,
        in_play_idx: usize,
        status: StatusCondition,
    ) {
        let Some(pokemon) = self.in_play_pokemon[player][in_play_idx].as_ref() else {
            return;
        };

        // Fabled Luster (Arceus ex, blanket) and Insomnia (Hoothoot, Asleep only).
        if let Some(AbilityMechanic::ImmuneToStatusConditions { status: immune_to }) =
            get_in_play_ability_mechanic(self, pokemon)
        {
            if immune_to.is_none() || *immune_to == Some(status) {
                debug!("Pokémon's Ability makes it immune to {status:?}");
                return;
            }
        }

        // Steel Apron: "The [M] Pokémon this card is attached to ... can't be affected by any
        // Special Conditions." The immunity only applies to a [M] holder.
        if has_tool(pokemon, crate::card_ids::CardId::A4153SteelApron)
            && self.pokemon_is_type(pokemon, EnergyType::Metal)
        {
            debug!("Steel Apron: Pokémon is immune to status conditions");
            return;
        }

        // SoothingWind (Ogerpon ex) / Flower Shield (Comfey): if any of this player's Pokémon
        // has the ability, Pokémon meeting the energy requirement are immune to Special Conditions.
        for p in self.in_play_pokemon[player].iter().flatten() {
            if let Some(AbilityMechanic::SoothingWind { energy_type }) =
                get_in_play_ability_mechanic(self, p)
            {
                let is_protected = match energy_type {
                    None => !pokemon.attached_energy.is_empty(),
                    Some(t) => pokemon.attached_energy.contains(t),
                };
                if is_protected {
                    debug!(
                        "SoothingWind: Pokémon with matching energy is immune to status conditions"
                    );
                    return;
                }
            }
        }

        self.in_play_pokemon[player][in_play_idx]
            .as_mut()
            .unwrap()
            .set_status_raw(status);
    }

    // This function should be called only from turn 1 onwards
    pub(crate) fn advance_turn(&mut self, rng: &mut StdRng) {
        debug!(
            "Ending turn moving from player {} to player {}",
            self.current_player,
            (self.current_player + 1) % 2
        );
        self.end_turn_pending = false;
        let outgoing_player = self.current_player;
        self.points_gained_during_own_last_turn[outgoing_player] =
            self.points_gained_this_turn[outgoing_player];
        self.points_gained_this_turn = [0, 0];
        self.attack_name_used_last_turn[self.current_player] =
            self.attack_name_used_this_turn[self.current_player].take();
        self.current_player = (self.current_player + 1) % 2;
        self.turn_count += 1;
        if self.turn_count > 30 {
            self.winner = Some(GameOutcome::Tie);
            return;
        }
        self.end_turn_maintenance();
        self.queue_draw_action(self.current_player, 1);
        self.rotate_energy_zone(self.current_player, rng);
    }

    /// Awards public match points and records their turn-local provenance for attacks such as
    /// Hisuian Basculegion's Soul Counter. Call only after all point-denial effects are resolved.
    pub(crate) fn award_points(&mut self, player: usize, amount: u8) {
        self.points[player] += amount;
        self.points_gained_this_turn[player] += amount;
    }

    pub(crate) fn is_game_over(&self) -> bool {
        self.winner.is_some()
    }

    pub(crate) fn num_in_play_of_type(&self, player: usize, energy: EnergyType) -> usize {
        self.enumerate_in_play_pokemon(player)
            .filter(|(_, x)| self.pokemon_is_type(x, energy))
            .count()
    }

    pub(crate) fn is_users_first_turn(&self) -> bool {
        self.turn_count <= 2
    }

    /// Discards a Pokemon from play, moving it, its evolution chain, and its energies
    ///  to the discard pile.
    /// Rescue Scarf (A4 155): the Knocked Out Pokémon itself goes to its owner's hand instead of
    /// the discard pile. Everything else it was carrying — the tool, the cards it evolved from,
    /// and its attached Energy — is still discarded, and the board slot is still emptied, so the
    /// knockout and its points resolve exactly as normal.
    pub(crate) fn rescue_from_play(&mut self, ko_receiver: usize, ko_pokemon_idx: usize) {
        let ko_pokemon = self.in_play_pokemon[ko_receiver][ko_pokemon_idx]
            .as_ref()
            .expect("There should be a Pokemon to rescue");
        let mut cards_to_discard = ko_pokemon.cards_behind.clone();
        cards_to_discard.extend(ko_pokemon.attached_tools.iter().cloned());
        let rescued = ko_pokemon.card.clone();
        debug!("Rescue Scarf: returning {rescued:?} to hand, discarding {cards_to_discard:?}");
        self.discard_piles[ko_receiver].extend(cards_to_discard);
        self.discard_energies[ko_receiver].extend(ko_pokemon.attached_energy.iter().cloned());
        self.hands[ko_receiver].push(rescued);
        self.in_play_pokemon[ko_receiver][ko_pokemon_idx] = None;
        self.refresh_hp_bonuses_all();
    }

    pub(crate) fn discard_from_play(&mut self, ko_receiver: usize, ko_pokemon_idx: usize) {
        let ko_pokemon = self.in_play_pokemon[ko_receiver][ko_pokemon_idx]
            .as_ref()
            .expect("There should be a Pokemon to discard");
        let mut cards_to_discard = ko_pokemon.cards_behind.clone();
        cards_to_discard.extend(ko_pokemon.attached_tools.iter().cloned());
        cards_to_discard.push(ko_pokemon.card.clone());
        debug!("Discarding: {cards_to_discard:?}");
        self.discard_piles[ko_receiver].extend(cards_to_discard);
        self.discard_energies[ko_receiver].extend(ko_pokemon.attached_energy.iter().cloned());
        self.in_play_pokemon[ko_receiver][ko_pokemon_idx] = None;
        self.refresh_hp_bonuses_all();
    }

    /// Discard one explicitly selected Tool, preserving the other attachments and their order.
    pub(crate) fn discard_tool(&mut self, player: usize, in_play_idx: usize, tool_idx: usize) {
        let pokemon = self.in_play_pokemon[player][in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if discarding tool");
        let tool_card = pokemon.attached_tools.remove(tool_idx);
        self.discard_piles[player].push(tool_card);
    }

    pub(crate) fn discard_all_tools(&mut self, player: usize, in_play_idx: usize) {
        let pokemon = self.in_play_pokemon[player][in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if discarding tools");
        self.discard_piles[player].append(&mut pokemon.attached_tools);
    }

    /// Enforce the holder's current Tool capacity after an Ability or form change. When capacity
    /// shrinks, the owner-approved provisional rule is to discard the most recently attached Tool
    /// first. Attachment order is the vector order, so removing from the tail preserves every
    /// older attachment and avoids any choice or hidden state.
    pub(crate) fn discard_excess_tools(&mut self, player: usize, in_play_idx: usize) -> usize {
        let Some(pokemon) = self.in_play_pokemon[player][in_play_idx].as_ref() else {
            return 0;
        };
        let capacity = crate::tools::tool_capacity(self, pokemon);
        let mut discarded = Vec::new();
        {
            let pokemon = self.in_play_pokemon[player][in_play_idx]
                .as_mut()
                .expect("Pokemon should still be in play while enforcing Tool capacity");
            while pokemon.attached_tools.len() > capacity {
                discarded.push(
                    pokemon
                        .attached_tools
                        .pop()
                        .expect("Tool count was greater than capacity"),
                );
            }
        }
        let discarded_count = discarded.len();
        self.discard_piles[player].extend(discarded);
        discarded_count
    }

    /// A consumed Tool removes itself, never an unrelated attachment in the first slot.
    pub(crate) fn discard_one_matching_tool(
        &mut self,
        player: usize,
        in_play_idx: usize,
        card_id: crate::card_ids::CardId,
    ) -> bool {
        let tool_idx = self.in_play_pokemon[player][in_play_idx]
            .as_ref()
            .and_then(|pokemon| {
                pokemon.attached_tools.iter().position(|tool| {
                    crate::tools::tool_effects_equal(crate::tools::ensure_tool_card(tool), card_id)
                })
            });
        if let Some(tool_idx) = tool_idx {
            self.discard_tool(player, in_play_idx, tool_idx);
            true
        } else {
            false
        }
    }

    pub(crate) fn discard_from_active(&mut self, actor: usize, to_discard: &[EnergyType]) {
        self.discard_energy_from_in_play(actor, 0, to_discard);
    }

    pub(crate) fn discard_energy_from_in_play(
        &mut self,
        actor: usize,
        in_play_idx: usize,
        to_discard: &[EnergyType],
    ) {
        let pokemon = self.in_play_pokemon[actor][in_play_idx]
            .as_mut()
            .expect("Pokemon should be there if discarding energy");
        let mut discarded: Vec<EnergyType> = Vec::new();
        for energy in to_discard {
            if let Some(pos) = pokemon.attached_energy.iter().position(|e| *e == *energy) {
                pokemon.attached_energy.swap_remove(pos);
                discarded.push(*energy);
            } else {
                panic!("Pokemon does not have energy to discard");
            }
        }
        if !discarded.is_empty() {
            self.discard_energies[actor].extend(discarded);
        }
    }

    /// Triggers promotion from bench or declares winner if no bench pokemon available.
    /// This should be called when the active spot becomes empty (e.g., after KO or discard).
    pub(crate) fn trigger_promotion_or_declare_winner(&mut self, player_with_empty_active: usize) {
        // An effect-driven switch may already be queued when a later knockout hook removes its
        // target Active. Such a frame is no longer meaningful and would otherwise sit above the
        // compulsory promotion, allowing a stale choice to empty the Active Spot again. Remove
        // only frames wholly made of switches for this board (with an optional Noop); preserve
        // private empty frames, mixed-effect frames, other-player switches and true promotions.
        self.move_generation_stack.retain(|(_, choices)| {
            let has_switch_for_empty_player = choices.iter().any(|choice| {
                matches!(choice, SimpleAction::Activate { player, .. }
                    if *player == player_with_empty_active)
            });
            let only_same_player_switch_or_noop = choices.iter().all(|choice| {
                matches!(choice,
                    SimpleAction::Activate { player, .. }
                        if *player == player_with_empty_active)
                    || matches!(choice, SimpleAction::Noop)
            });
            !(has_switch_for_empty_player && only_same_player_switch_or_noop)
        });

        let enumerated_bench_pokemon = self
            .enumerate_bench_pokemon(player_with_empty_active)
            .collect::<Vec<_>>();

        if enumerated_bench_pokemon.is_empty() {
            // If no bench pokemon, opponent wins
            let opponent = (player_with_empty_active + 1) % 2;
            self.winner = Some(GameOutcome::Win(opponent));
            debug!("Player {player_with_empty_active} lost due to no bench pokemon");
        } else {
            // Queue up promotion actions
            let possible_moves = self
                .enumerate_bench_pokemon(player_with_empty_active)
                .map(|(i, _)| SimpleAction::Promote {
                    player: player_with_empty_active,
                    in_play_idx: i,
                })
                .collect::<Vec<_>>();
            debug!("Triggering Promote moves: {possible_moves:?} to player {player_with_empty_active}");

            // If we .push, we could make idxs in items of the stack stale. Consider Dialga's
            // user choosing to attach to idx 1, but then Dialga is K.O. by Rocky Helmet.
            // So we .insert(0, looking to have those settle before this one.

            // Using .insert(0, should not have issues with EndTurn mechanics, since those are
            // done only when move_generation_stack is stable (empty).
            // A paused Checkup must not advance or begin the next phase before promotion.
            let phase_floor = self.move_generation_stack.iter().rposition(|(_, choices)|
                choices.iter().any(|action| matches!(action,
                    SimpleAction::FinishPokemonCheckup | SimpleAction::ResolvePokemonCheckup)))
                .map_or(0, |idx| idx + 1);
            // A later hit (for example Double Punching Family) requires a replacement
            // before its damage forecast can inspect the new Active Pokémon.
            let pending_hit_floor = self.move_generation_stack.iter().rposition(|(_, choices)|
                choices.iter().any(|action| match action {
                    SimpleAction::ApplyDamage { attacking_ref, targets, .. } =>
                        *attacking_ref == (player_with_empty_active, 0)
                        || targets.iter().any(|(_, player, idx)|
                            *player == player_with_empty_active && *idx == 0),
                    _ => false,
                })).map_or(0, |idx| idx + 1);
            self.move_generation_stack
                .insert(phase_floor.max(pending_hit_floor), (player_with_empty_active, possible_moves));
        }
    }

    // =========================================================================
    // Test Helper Methods
    // These methods are public for integration tests but should be used carefully
    // =========================================================================

    /// Set up multiple in-play pokemon for both players at once.
    /// For each side: Index 0 = active, 1..3 = bench. Any board slot not provided is cleared
    /// to `None` — this makes test setups deterministic regardless of what setup-phase
    /// placements left behind.
    pub fn set_board(&mut self, player_0: Vec<PlayedCard>, player_1: Vec<PlayedCard>) {
        self.in_play_pokemon[0] = [None, None, None, None];
        self.in_play_pokemon[1] = [None, None, None, None];
        for (i, card) in player_0.into_iter().enumerate() {
            self.in_play_pokemon[0][i] = Some(card);
        }
        for (i, card) in player_1.into_iter().enumerate() {
            self.in_play_pokemon[1][i] = Some(card);
        }
        self.refresh_hp_bonuses_all();
    }

    /// Set the flag indicating a Pokemon was KO'd by opponent's attack last turn.
    /// Used for testing Marshadow's Revenge attack and similar mechanics.
    pub fn set_knocked_out_by_opponent_attack_last_turn(&mut self, value: bool) {
        self.knocked_out_by_opponent_attack_last_turn = value;
    }

    /// Set the energy types of the Pokémon KO'd by the opponent's attack last turn (companion to
    /// `set_knocked_out_by_opponent_attack_last_turn`, for type-filtered vengeance attacks).
    /// Used for testing Zarude's Dark Vengeance and similar mechanics.
    pub fn set_knocked_out_types_by_opponent_attack_last_turn(&mut self, types: Vec<EnergyType>) {
        self.knocked_out_types_by_opponent_attack_last_turn = types;
    }

    /// Get the flag indicating a Pokemon was KO'd by opponent's attack last turn.
    pub fn get_knocked_out_by_opponent_attack_last_turn(&self) -> bool {
        self.knocked_out_by_opponent_attack_last_turn
    }

    pub(crate) fn record_attack_used(&mut self, player: usize, attack_name: String) {
        *self.attack_name_used_count[player]
            .entry(attack_name.clone())
            .or_insert(0) += 1;
        self.attack_name_used_this_turn[player] = Some(attack_name);
    }

    pub(crate) fn used_attack_during_own_last_turn(
        &self,
        player: usize,
        attack_name: &str,
    ) -> bool {
        self.attack_name_used_last_turn[player].as_deref() == Some(attack_name)
    }

    pub(crate) fn count_attack_used_this_game(&self, player: usize, attack_name: &str) -> u32 {
        self.attack_name_used_count[player]
            .get(attack_name)
            .copied()
            .unwrap_or(0)
    }

    /// How many of `player`'s own Pokémon have been Knocked Out so far this game.
    pub(crate) fn count_own_knockouts_this_game(&self, player: usize) -> u32 {
        self.own_knockouts_this_game[player]
    }

    /// Set `player`'s game-long own-knockout tally directly. Mirrors `set_board` and
    /// `set_knocked_out_by_opponent_attack_last_turn`: it exists so tests can reach a mid-game
    /// board without replaying the knockouts that produced it.
    pub fn set_own_knockouts_this_game(&mut self, player: usize, count: u32) {
        self.own_knockouts_this_game[player] = count;
    }

    pub fn set_attack_name_used_last_turn(&mut self, player: usize, attack_name: Option<String>) {
        self.attack_name_used_last_turn[player] = attack_name;
    }

    /// Generate all possible actions for the current game state.
    /// Returns a tuple of (actor, actions) where actor is the player who must act.
    pub fn generate_possible_actions(&self) -> (usize, Vec<crate::actions::Action>) {
        move_generation::generate_possible_actions(self)
    }
}

fn format_cards(played_cards: &[Option<PlayedCard>]) -> Vec<String> {
    played_cards.iter().map(format_card).collect()
}

fn format_card(x: &Option<PlayedCard>) -> String {
    match x {
        Some(played_card) => format!(
            "{}({}hp,{:?})",
            played_card.get_name(),
            played_card.get_remaining_hp(),
            played_card.attached_energy.len(),
        ),
        None => "".to_string(),
    }
}

fn canonical_name(card: &Card) -> String {
    match card {
        Card::Pokemon(pokemon_card) => pokemon_card.name.clone(),
        Card::Trainer(trainer_card) => trainer_card.name.clone(),
        Card::Unknown => "Unknown".to_string(),
    }
}

fn to_canonical_names(cards: &[Card]) -> Vec<String> {
    cards.iter().map(canonical_name).collect()
}

/// Picks a random energy type from the deck's declared energy set, using the supplied rng.
/// Decks are guaranteed by `Deck::from_string` to have at least one energy type.
fn roll_energy(deck: &Deck, rng: &mut impl Rng) -> EnergyType {
    *deck
        .energy_types
        .choose(rng)
        .expect("Decks should have at least 1 energy")
}

#[cfg(test)]
mod tests {
    use crate::{
        card_ids::CardId, database::get_card_by_enum, deck::is_basic, hooks::to_playable_card,
        test_support::load_test_decks,
    };

    use super::*;

    #[test]
    fn test_draw_transfers_to_hand() {
        let (deck_a, deck_b) = load_test_decks();
        let mut state = State::new(&deck_a, &deck_b);

        assert_eq!(state.decks[0].cards.len(), 20);
        assert_eq!(state.hands[0].len(), 0);

        state.maybe_draw_card(0);

        assert_eq!(state.decks[0].cards.len(), 19);
        assert_eq!(state.hands[0].len(), 1);
    }

    #[test]
    fn test_players_start_with_five_cards_one_of_which_is_basic() {
        let (deck_a, deck_b) = load_test_decks();
        let state = State::initialize(&deck_a, &deck_b, &mut rand::thread_rng());

        assert_eq!(state.hands[0].len(), 5);
        assert_eq!(state.hands[1].len(), 5);
        assert_eq!(state.decks[0].cards.len(), 15);
        assert_eq!(state.decks[1].cards.len(), 15);
        assert!(state.hands[0].iter().any(is_basic));
        assert!(state.hands[1].iter().any(is_basic));
    }

    #[test]
    fn test_discard_from_play_basic_pokemon() {
        // Arrange: Create a state with a basic Pokemon in play
        let (deck_a, deck_b) = load_test_decks();
        let mut state = State::new(&deck_a, &deck_b);

        let bulbasaur_card = get_card_by_enum(CardId::A1001Bulbasaur);
        let played_bulbasaur = to_playable_card(&bulbasaur_card, false);

        // Place Bulbasaur in active slot for player 0
        state.in_play_pokemon[0][0] = Some(played_bulbasaur.clone());

        // Attach some energy to test energy discard
        state.attach_energy_from_zone(0, 0, EnergyType::Grass, 2, false);

        // Verify initial state
        assert!(state.in_play_pokemon[0][0].is_some());
        assert_eq!(state.discard_piles[0].len(), 0);
        assert_eq!(state.discard_energies[0].len(), 0);

        // Act: Discard the Pokemon from play
        state.discard_from_play(0, 0);

        // Assert: Pokemon slot is now empty
        assert!(state.in_play_pokemon[0][0].is_none());

        // Assert: Card is in discard pile
        assert_eq!(state.discard_piles[0].len(), 1);
        assert_eq!(state.discard_piles[0][0], bulbasaur_card);

        // Assert: Energy is in discard energy pile
        assert_eq!(state.discard_energies[0].len(), 2);
        assert_eq!(state.discard_energies[0][0], EnergyType::Grass);
        assert_eq!(state.discard_energies[0][1], EnergyType::Grass);
    }

    /// Both players' energy zones start with `current = None` (turn 1 has no energy to
    /// attach for the player going first) but `next = Some(_)` so that each side can
    /// preview the energy they'll receive on their first attaching turn.
    #[test]
    fn test_initialize_populates_next_energy_for_both_players() {
        use rand::SeedableRng;
        let (deck_a, deck_b) = load_test_decks();
        let mut rng = StdRng::seed_from_u64(7);
        let state = State::initialize(&deck_a, &deck_b, &mut rng);

        assert!(state.energy_zone[0].current.is_none());
        assert!(state.energy_zone[1].current.is_none());
        assert!(state.energy_zone[0].next.is_some());
        assert!(state.energy_zone[1].next.is_some());

        // The rolled energies must come from each deck's declared energy set.
        let n0 = state.energy_zone[0].next.unwrap();
        let n1 = state.energy_zone[1].next.unwrap();
        assert!(state.decks[0].energy_types.contains(&n0));
        assert!(state.decks[1].energy_types.contains(&n1));
    }

    /// Rotating a queue promotes `next` into `current` and rolls a fresh `next`.
    #[test]
    fn test_rotate_energy_zone_shifts_queue() {
        use rand::SeedableRng;
        let (deck_a, deck_b) = load_test_decks();
        let mut rng = StdRng::seed_from_u64(11);
        let mut state = State::initialize(&deck_a, &deck_b, &mut rng);

        let before = state.energy_zone[0].next.unwrap();
        state.rotate_energy_zone(0, &mut rng);

        assert_eq!(state.energy_zone[0].current, Some(before));
        assert!(state.energy_zone[0].next.is_some());
    }

    /// Two independent runs with the same seed produce identical energy_zone trajectories.
    /// This locks in the reproducibility guarantee.
    #[test]
    fn test_energy_generation_is_reproducible_under_shared_rng() {
        use rand::SeedableRng;
        let (deck_a, deck_b) = load_test_decks();

        let mut rng_a = StdRng::seed_from_u64(123);
        let mut state_a = State::initialize(&deck_a, &deck_b, &mut rng_a);
        state_a.rotate_energy_zone(1, &mut rng_a);
        state_a.rotate_energy_zone(0, &mut rng_a);

        let mut rng_b = StdRng::seed_from_u64(123);
        let mut state_b = State::initialize(&deck_a, &deck_b, &mut rng_b);
        state_b.rotate_energy_zone(1, &mut rng_b);
        state_b.rotate_energy_zone(0, &mut rng_b);

        assert_eq!(state_a.energy_zone, state_b.energy_zone);
    }

    #[test]
    fn test_maybe_draw_card_respects_10_card_hand_limit() {
        let (deck_a, deck_b) = load_test_decks();
        let mut state = State::new(&deck_a, &deck_b);

        for _ in 0..10 {
            state.maybe_draw_card(0);
        }
        assert_eq!(state.hands[0].len(), 10);

        // 11th draw should be a no-op
        state.maybe_draw_card(0);
        assert_eq!(state.hands[0].len(), 10);
        assert_eq!(state.decks[0].cards.len(), 10);
    }

    #[test]
    fn test_advance_turn_declares_tie_after_turn_30() {
        use rand::SeedableRng;
        let (deck_a, deck_b) = load_test_decks();
        let mut rng = StdRng::seed_from_u64(42);
        let mut state = State::initialize(&deck_a, &deck_b, &mut rng);

        state.turn_count = 30;
        state.advance_turn(&mut rng);

        assert_eq!(state.winner, Some(GameOutcome::Tie));
        assert!(state.is_game_over());
    }

    #[test]
    fn private_reveal_event_payload_is_redacted_from_state_debug_and_serialization() {
        let mut state = State::default();
        state.private_reveal_events.push(PrivateRevealEvent {
            viewer: 0,
            zone_owner: 1,
            cause: "test reveal".into(),
            kind: PrivateRevealKind::RandomHandCard,
            cards: vec![get_card_by_enum(CardId::PA001Potion)],
        });
        let debug = format!("{:?}", state.private_reveal_events);
        assert_eq!(debug, "<private reveal events redacted>");
        let json = serde_json::to_value(&state).unwrap();
        assert!(json.get("private_reveal_events").is_none());
    }

    #[test]
    fn public_reveal_event_payload_is_redacted_from_state_debug_and_serialization() {
        let mut state = State::default();
        state.public_reveal_events.push(PublicRevealEvent {
            zone_owner: 0,
            cause: "Rocket Frenzy".into(),
            kind: PublicRevealKind::DeckPrefixThenShuffle,
            cards: vec![get_card_by_enum(CardId::PB088TeamRocketsScyther)],
        });
        assert_eq!(
            format!("{:?}", state.public_reveal_events),
            "<public reveal events redacted>"
        );
        let json = serde_json::to_value(&state).unwrap();
        assert!(json.get("public_reveal_events").is_none());
    }
}
