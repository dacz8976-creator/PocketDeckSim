use crate::{
    actions::{ability_mechanic_from_effect, EFFECT_MECHANIC_MAP},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, TrainerType},
    move_generation::trainer_move_generation_implementation,
    state::State,
    tools::is_tool_effect_implemented,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ImplementationStatus {
    Complete,
    CardNotFound,
    MissingAttack,
    MissingAbility,
    MissingTrainer,
    MissingTool,
    /// Mechanics are present, but known rule boundaries still need verification.
    RulesUnverified,
}

impl ImplementationStatus {
    pub fn is_complete(&self) -> bool {
        matches!(self, ImplementationStatus::Complete)
    }

    pub fn description(&self) -> &'static str {
        match self {
            ImplementationStatus::Complete => "Fully implemented",
            ImplementationStatus::CardNotFound => "Card ID not found",
            ImplementationStatus::MissingAttack => "Attack effect not implemented",
            ImplementationStatus::MissingAbility => "Ability not implemented",
            ImplementationStatus::MissingTrainer => "Trainer logic not implemented",
            ImplementationStatus::MissingTool => "Tool not implemented",
            ImplementationStatus::RulesUnverified => "Implemented with unverified rule boundaries",
        }
    }
}

pub fn get_implementation_status(card_id: CardId) -> ImplementationStatus {
    let card = get_card_by_enum(card_id);

    match card {
        Card::Pokemon(pokemon) => {
            // Verify attacks have no effects or effects are implemented
            for attack in &pokemon.attacks {
                if let Some(effect_text) = &attack.effect {
                    if EFFECT_MECHANIC_MAP.get(&effect_text[..]).is_none() {
                        return ImplementationStatus::MissingAttack;
                    }
                }
            }

            // Verify ability is implemented
            if let Some(ability) = &pokemon.ability {
                if ability_mechanic_from_effect(&ability.effect).is_none() {
                    return ImplementationStatus::MissingAbility;
                }
            }
        }
        Card::Trainer(trainer_card) => {
            if trainer_card.trainer_card_type == TrainerType::Tool
                && !is_tool_effect_implemented(&trainer_card)
            {
                return ImplementationStatus::MissingTool;
            }

            // Verify it can generate moves
            let moves = trainer_move_generation_implementation(&State::default(), &trainer_card);
            if moves.is_none() {
                return ImplementationStatus::MissingTrainer;
            };
        }
        // This sentinel is never present in the catalog, so it has no implementation status.
        Card::Unknown => return ImplementationStatus::CardNotFound,
    }

    if !implementation_limitations(card_id).is_empty() {
        return ImplementationStatus::RulesUnverified;
    }

    ImplementationStatus::Complete
}

/// Known limitations are explicit and printing-specific. This list is not a certification of
/// other mapped cards: the implementation-status checker only verifies dispatch coverage.
pub fn implementation_limitations(card_id: CardId) -> &'static [&'static str] {
    match card_id {
        CardId::B4115Revavroom => &[
            "Owner-approved assumption, not verified in Pokémon TCG Pocket: when suppression or devolution removes Dual Customization, discard excess Tools most-recently-attached first.",
            "Owner-approved assumption, not verified in Pokémon TCG Pocket: duplicate Sitrus Berries resolve sequentially and recheck current HP after every successful heal; Heal Block leaves them attached.",
            "Owner-approved assumption, not verified in Pokémon TCG Pocket: duplicate Lum Berries resolve sequentially; the first cure removes all Special Conditions, so later copies remain attached.",
        ],
        CardId::B3025Victini | CardId::PB049Victini => &[
            "Victory Star supports printed attack-effect coin batches; confusion and attacker-side coin gates currently bypass the reroll prompt pending Pocket rule verification.",
        ],
        CardId::B4a051Gholdengo | CardId::B4a109Gholdengo => &[
            "Provisional engine convention, not verified in Pokémon TCG Pocket: complete Trainer coin batches are public while Luxury Coin is pending.",
            "Provisional engine convention, not verified in Pokémon TCG Pocket: the player activating Arcade or Mesagoza may use Luxury Coin regardless of who played the Stadium.",
            "Unverified Pokémon TCG Pocket boundary: Luxury Coin applies to coin batches produced by a Trainer source selected by Penny, but not to Portrait or Portrait copying Penny because those outer effects are Abilities.",
            "Initial and replacement batches with infinitely many observable face sequences are explicitly unpriced (Misty, Team Rocket Grunt, and Team Rocket's Researcher), even when the resulting damage or Energy states eventually saturate.",
        ],
        CardId::B4a018HisuianBasculegion => &[
            "Pokémon Checkup points are attributed to the turn that just ended; whether Pocket includes between-turn Checkup in ‘during their last turn’ remains unverified.",
            "Legacy serialized states default the new turn-local point history to zero; a replay loaded midgame cannot reconstruct points from the preceding turn.",
        ],
        CardId::B4a069TeamRocketsResearcher | CardId::B4a085TeamRocketsResearcher => &[
            "Unverified Pokémon TCG Pocket boundary: random Pokémon transferred by this effect are not capped at a 10-card hand; this inherits the engine's existing random-search transfer policy.",
            "Unverified Pokémon TCG Pocket boundary: the deck is shuffled exactly once after resolution, including zero heads or no eligible Pokémon; this inherits the engine's hidden-zone normalization policy rather than printed card text.",
        ],
        _ => &[],
    }
}
