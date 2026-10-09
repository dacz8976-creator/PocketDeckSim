pub(crate) mod abilities;
mod apply_abilities_action;
mod apply_action;
mod apply_action_helpers;
mod apply_attack_action;
mod apply_stadium_action;
mod apply_trainer_action;
pub(crate) mod attack_helpers;
pub(crate) mod attack_outcome;
pub(crate) mod attacks;
mod effect_ability_mechanic_map;
mod effect_mechanic_map;
pub(crate) mod energy_discard_choices;
pub(crate) mod energy_moves;
mod mutations;
mod outcomes;
pub mod professor_sada;
mod shared_mutations;
mod team_rockets_researcher;
mod trainer_coin_plan;
mod types;

pub(crate) use apply_abilities_action::selectable_status_conditions;
pub(crate) use apply_action::apply_action;
pub(crate) use apply_action::apply_evolve;
pub(crate) use apply_action::apply_place_card;
pub(crate) use apply_action::forecast_action;
pub use apply_action::try_forecast_action;
pub(crate) use apply_action_helpers::handle_attack_retaliation;
pub(crate) use apply_action_helpers::handle_damage;
pub(crate) use apply_action_helpers::handle_damage_only;
pub(crate) use apply_action_helpers::handle_knockouts;
pub use apply_action_helpers::with_return_weakness;
pub use apply_action_helpers::{
    with_fossil_as_item, with_fossil_item_lock, with_luxury_coin_own_stadium_only, with_own_side_coin, with_own_side_guts,
    with_perish_on_queued_hit, with_plain_hit_coin, with_queued_site_coin, with_round2, with_trap_territory_each,
    with_victory_star_after_block_coin, with_will_on_gate_coins,
};
pub(crate) use apply_action_helpers::{
    fossil_as_item_on, fossil_item_lock_on, luxury_coin_own_stadium_only_on, own_side_coin_on, own_side_guts_on,
    perish_on_queued_hit_on, plain_hit_coin_on, queued_site_coin_on, trap_territory_each_on, victory_star_after_block_coin_on,
    will_on_gate_coins_on,
};
pub use apply_trainer_action::may_effect;
pub(crate) use effect_ability_mechanic_map::abilities_switched_off;
pub use effect_ability_mechanic_map::ability_mechanic_from_effect;
pub(crate) use effect_ability_mechanic_map::card_effect_from_ability_mechanic;
pub(crate) use effect_ability_mechanic_map::get_ability_mechanic;
pub(crate) use effect_ability_mechanic_map::get_entering_play_ability_mechanic;
pub(crate) use effect_ability_mechanic_map::get_in_play_ability_mechanic;
pub use effect_ability_mechanic_map::has_ability_mechanic;
pub(crate) use effect_ability_mechanic_map::has_any_in_play_ability;
pub(crate) use effect_ability_mechanic_map::has_in_play_ability_mechanic;
pub use effect_ability_mechanic_map::EFFECT_ABILITY_MECHANIC_MAP;
pub use effect_mechanic_map::EFFECT_MECHANIC_MAP;
pub use outcomes::{CoinConditionError, CoinPaths, CoinSeq, ForecastBuildError, Outcomes};
pub use team_rockets_researcher::{UnpricedForecast, UnpricedForecastKind};
pub use types::Action;
pub use types::SimpleAction;
