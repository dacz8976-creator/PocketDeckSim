use core::fmt;
use serde::{Deserialize, Serialize};

use super::State;
use crate::{
    actions::{
        abilities::AbilityMechanic, card_effect_from_ability_mechanic,
        get_in_play_ability_mechanic, has_in_play_ability_mechanic,
    },
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    hooks::is_ancient_pokemon,
    models::{Attack, Card, EnergyType, StatusCondition, TrainerType, BASIC_STAGE},
    tools::tool_count,
};

/// This represents a card in the mat. Has a pointer to the card
/// description, but captures the extra variable properties while in mat.
#[derive(Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct PlayedCard {
    pub card: Card,
    damage_counters: u32,
    base_hp: u32,
    stadium_hp_bonus: u32,
    /// Board-conditional HP granted by abilities in play. Stored
    /// rather than computed because `get_effective_total_hp` has no access to `State`; kept in
    /// sync by `State::refresh_hp_bonuses_all`, exactly like `stadium_hp_bonus`.
    ability_hp_bonus: u32,
    pub attached_energy: Vec<EnergyType>,
    /// All attached Tools in attachment order. Legacy single-Tool snapshots still deserialize.
    #[serde(
        default,
        alias = "attached_tool",
        deserialize_with = "deserialize_attached_tools"
    )]
    pub attached_tools: Vec<Card>,
    pub played_this_turn: bool,
    pub moved_to_active_this_turn: bool,
    /// Whether this Pokémon was damaged by an opponent's attack while it was in the Active Spot,
    /// tracked for the current and the previous turn (Wobbuffet's Reply Strongly: "If this
    /// Pokémon was damaged by an attack during your opponent's last turn while it was in the
    /// Active Spot ..."). Shifted in `end_turn_maintenance`.
    #[serde(default)]
    pub damaged_by_attack_while_active_this_turn: bool,
    #[serde(default)]
    pub damaged_by_attack_while_active_last_turn: bool,
    pub ability_used: bool,
    poisoned: bool,
    /// Pokémon Checkup poison damage override ("Do N damage to this Pokémon instead of the usual
    /// amount for this Special Condition", e.g. Toxicroak's Toxic). `None` = the usual 10.
    /// Set only while `poisoned` is true; cleared whenever the poison is cleared or re-applied.
    #[serde(default)]
    poison_checkup_damage: Option<u32>,
    paralyzed: bool,
    asleep: bool,
    burned: bool,
    confused: bool,
    pub cards_behind: Vec<Card>,
    pub prevent_first_attack_damage_used: bool,
    pub has_attacked_since_play: bool,

    /// Effects that should be cleared if moved to the bench (by retreat or similar).
    /// The second value is the number of turns left for the effect.
    effects: Vec<(CardEffect, u8)>,
}
fn deserialize_attached_tools<'de, D>(deserializer: D) -> Result<Vec<Card>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    #[derive(Deserialize)]
    #[serde(untagged)]
    enum ToolInput {
        Multiple(Vec<Card>),
        Legacy(Option<Card>),
    }
    Ok(match ToolInput::deserialize(deserializer)? {
        ToolInput::Multiple(tools) => tools,
        ToolInput::Legacy(tool) => tool.into_iter().collect(),
    })
}

impl PlayedCard {
    pub fn new(
        card: Card,
        damage_counters: u32,
        base_hp: u32,
        attached_energy: Vec<EnergyType>,
        played_this_turn: bool,
        cards_behind: Vec<Card>,
    ) -> Self {
        PlayedCard {
            card,
            damage_counters,
            base_hp,
            stadium_hp_bonus: 0,
            ability_hp_bonus: 0,
            attached_energy,
            played_this_turn,
            moved_to_active_this_turn: false,
            damaged_by_attack_while_active_this_turn: false,
            damaged_by_attack_while_active_last_turn: false,
            cards_behind,

            attached_tools: vec![],
            ability_used: false,
            poisoned: false,
            poison_checkup_damage: None,
            paralyzed: false,
            asleep: false,
            burned: false,
            confused: false,
            effects: vec![],
            prevent_first_attack_damage_used: false,
            has_attacked_since_play: false,
        }
    }

    /// Create a fresh PlayedCard from a Card at full HP with no energy, tools, or status.
    pub fn from_card(card: &Card) -> Self {
        let base_hp = match card {
            Card::Pokemon(pokemon_card) => pokemon_card.hp,
            Card::Trainer(trainer_card) => {
                if trainer_card.trainer_card_type == TrainerType::Fossil {
                    40
                } else {
                    panic!(
                        "Cannot create PlayedCard from non-Fossil Trainer: {:?}",
                        trainer_card
                    );
                }
            }
            Card::Unknown => panic!("Unknown card cannot be played"),
        };
        Self::new(card.clone(), 0, base_hp, vec![], false, vec![])
    }

    /// Create a fresh PlayedCard from a CardId at full HP with no energy, tools, or status.
    pub fn from_id(card_id: CardId) -> Self {
        let card = get_card_by_enum(card_id);
        Self::from_card(&card)
    }

    pub fn with_energy(mut self, energy: Vec<EnergyType>) -> Self {
        self.attached_energy = energy;
        self
    }

    pub fn with_damage(mut self, damage: u32) -> Self {
        self.damage_counters = self.damage_counters.saturating_add(damage);
        self
    }

    pub fn with_remaining_hp(mut self, remaining_hp: u32) -> Self {
        self.set_remaining_hp(remaining_hp);
        self
    }

    /// Set the remaining HP to an exact value (e.g. Ursaluna's Guts leaves it at 10).
    pub(crate) fn set_remaining_hp(&mut self, remaining_hp: u32) {
        let effective_hp = self.get_effective_total_hp();
        let clamped_remaining = remaining_hp.min(effective_hp);
        self.damage_counters = effective_hp.saturating_sub(clamped_remaining);
    }

    pub fn with_tool(mut self, tool: Card) -> Self {
        self.attached_tools = vec![tool];
        self
    }

    /// Fixture builder: attach a specified collection without replaying attachment choices.
    /// Legal play uses the capacity check in `apply_attach_tool`.
    pub fn with_tools(mut self, tools: Vec<Card>) -> Self {
        for tool in &tools {
            crate::tools::ensure_tool_card(tool);
        }
        self.attached_tools = tools;
        self
    }

    /// Start this Pokémon already affected by `status`. Companion to the other `with_*` builders,
    /// for reaching a mid-game board without replaying the attack that inflicted the condition.
    /// Applies the condition directly, bypassing immunity checks, exactly like `set_status_raw`.
    pub fn with_status_condition(mut self, status: StatusCondition) -> Self {
        self.set_status_raw(status);
        self
    }

    pub fn get_id(&self) -> String {
        match &self.card {
            Card::Pokemon(pokemon_card) => pokemon_card.id.clone(),
            Card::Trainer(trainer_card) => trainer_card.id.clone(),
            Card::Unknown => "Unknown".to_string(),
        }
    }

    pub fn get_name(&self) -> String {
        match &self.card {
            Card::Pokemon(pokemon_card) => pokemon_card.name.clone(),
            Card::Trainer(trainer_card) => trainer_card.name.clone(),
            Card::Unknown => "Unknown".to_string(),
        }
    }

    /// Returns true if this card is a Fossil trainer card
    pub(crate) fn is_fossil(&self) -> bool {
        match &self.card {
            Card::Trainer(trainer_card) => trainer_card.trainer_card_type == TrainerType::Fossil,
            _ => false,
        }
    }

    pub(crate) fn get_attacks(&self) -> &Vec<Attack> {
        match &self.card {
            Card::Pokemon(pokemon_card) => &pokemon_card.attacks,
            _ => panic!("Unsupported playable card type"),
        }
    }

    /// Removes `amount` damage counters unconditionally.
    ///
    /// This is the *raw* primitive and it bypasses Heal Block (Claydol A3a 031). Healing effects
    /// must go through `State::heal_pokemon` / `State::heal_each_pokemon`, which are the single
    /// gate that Heal Block closes. Call this directly only for things that are not healing in the
    /// rules sense — chiefly *moving* damage counters between Pokémon (Dusknoir's Shadow Void,
    /// Brambleghast's Accept Pain), which Heal Block does not stop.
    pub(crate) fn heal_raw(&mut self, amount: u32) {
        self.damage_counters = self.damage_counters.saturating_sub(amount);
    }

    pub(crate) fn apply_damage(&mut self, damage: u32) {
        self.damage_counters = self.damage_counters.saturating_add(damage);
    }

    // Option because if playing an item card... (?)
    pub(crate) fn get_energy_type(&self) -> Option<EnergyType> {
        match &self.card {
            Card::Pokemon(pokemon_card) => Some(pokemon_card.energy_type),
            _ => None,
        }
    }

    /// Check if this Pokemon evolved from a specific Pokemon name
    pub(crate) fn evolved_from(&self, base_name: &str) -> bool {
        if let Card::Pokemon(pokemon_card) = &self.card {
            if let Some(evolves_from) = &pokemon_card.evolves_from {
                return evolves_from == base_name;
            }
        }
        false
    }

    pub(crate) fn is_damaged(&self) -> bool {
        self.damage_counters > 0
    }

    pub(crate) fn refresh_starting_plains_bonus(&mut self, starting_plains_active: bool) {
        let is_basic_pokemon = matches!(
            &self.card,
            Card::Pokemon(pokemon_card) if pokemon_card.stage == BASIC_STAGE
        );
        self.stadium_hp_bonus = if starting_plains_active && is_basic_pokemon {
            20
        } else {
            0
        };
    }

    /// Team-wide and per-attached-Energy HP bonuses. Set by
    /// `State::refresh_hp_bonuses_all` whenever the board changes; `bonus` is already the total
    /// across every matching ability in play.
    pub(crate) fn set_ability_hp_bonus(&mut self, bonus: u32) {
        self.ability_hp_bonus = bonus;
    }

    pub fn get_remaining_hp(&self) -> u32 {
        self.get_effective_total_hp()
            .saturating_sub(self.damage_counters)
    }

    pub(crate) fn is_knocked_out(&self) -> bool {
        self.damage_counters >= self.get_effective_total_hp()
    }

    pub(crate) fn get_damage_counters(&self) -> u32 {
        self.damage_counters
    }

    /// Returns effective total HP considering abilities like Reuniclus Infinite Increase
    pub(crate) fn get_effective_total_hp(&self) -> u32 {
        let mut effective_hp = self.base_hp;

        // Tool bonuses. Type/stage-specific caps only apply to matching Pokémon (the tools are
        // attachable to anything, but their HP bonus is gated by the holder).
        effective_hp += 20 * tool_count(self, CardId::A2147GiantCape);
        if self.get_energy_type() == Some(EnergyType::Grass) {
            effective_hp += 30 * tool_count(self, CardId::A3147LeafCape);
        }
        if matches!(&self.card, Card::Pokemon(p) if p.stage == 1) {
            effective_hp += 30 * tool_count(self, CardId::B3b065ElegantCape);
        }
        if is_ancient_pokemon(&self.get_name()) {
            effective_hp += 40 * tool_count(self, CardId::B3a069AncientBoosterEnergyCapsule);
        }

        effective_hp += self.stadium_hp_bonus;
        effective_hp += self.ability_hp_bonus;

        effective_hp
    }

    pub fn is_poisoned(&self) -> bool {
        self.poisoned
    }

    pub fn is_paralyzed(&self) -> bool {
        self.paralyzed
    }

    pub fn is_asleep(&self) -> bool {
        self.asleep
    }

    pub fn is_burned(&self) -> bool {
        self.burned
    }

    pub fn is_confused(&self) -> bool {
        self.confused
    }

    pub(crate) fn has_status_condition(&self) -> bool {
        self.poisoned || self.paralyzed || self.asleep || self.burned || self.confused
    }

    pub(crate) fn has_tool_attached(&self) -> bool {
        !self.attached_tools.is_empty()
    }

    /// Duration means:
    ///   - 0: only during this turn
    ///   - 1: during opponent's next turn
    ///   - 2: on your next turn
    pub fn add_effect(&mut self, effect: CardEffect, duration: u8) {
        self.effects.push((effect, duration));
    }

    pub(crate) fn get_active_effects(&self) -> Vec<CardEffect> {
        self.effects
            .iter()
            .map(|(effect, _)| effect.clone())
            .collect()
    }

    /// All effects currently on this Pokémon: the stored (turn-duration) effects from
    /// `add_effect`, plus effects *derived* from its passive ability (the "abilities-as-effects"
    /// model — see `card_effect_from_ability_mechanic`). Damage code should query this instead of
    /// separately scanning for defensive abilities, so a passive like Cloyster's Shell Armor and a
    /// stored effect like Carracosta's Blocking Shell are handled through one list. Derived effects
    /// are present exactly while the ability-holder is in play (no turn duration).
    /// Takes `state` because the derived half depends on the board: Power of Alchemy (Alolan Muk)
    /// switches off the Abilities of Basic Pokémon in play, so the lookup goes through the
    /// suppression-aware `get_in_play_ability_mechanic` rather than the raw printed one.
    pub(crate) fn get_effective_card_effects(&self, state: &State) -> Vec<CardEffect> {
        let mut effects = self.get_active_effects();
        if let Some(mechanic) = get_in_play_ability_mechanic(state, self) {
            if let Some(derived) = card_effect_from_ability_mechanic(mechanic) {
                effects.push(derived);
            }
        }
        effects
    }

    pub(crate) fn get_effects(&self) -> &Vec<(CardEffect, u8)> {
        &self.effects
    }

    pub(crate) fn clear_status_and_effects(&mut self) {
        self.poisoned = false;
        self.poison_checkup_damage = None;
        self.paralyzed = false;
        self.asleep = false;
        self.burned = false;
        self.confused = false;
        self.effects.clear();
    }

    pub(crate) fn cure_status_conditions(&mut self) {
        self.poisoned = false;
        self.poison_checkup_damage = None;
        self.paralyzed = false;
        self.asleep = false;
        self.burned = false;
        self.confused = false;
    }

    pub(crate) fn clear_status_condition(&mut self, status: StatusCondition) {
        match status {
            StatusCondition::Poisoned => {
                self.poisoned = false;
                self.poison_checkup_damage = None;
            }
            StatusCondition::Paralyzed => self.paralyzed = false,
            StatusCondition::Asleep => self.asleep = false,
            StatusCondition::Burned => self.burned = false,
            StatusCondition::Confused => self.confused = false,
        }
    }

    /// Raw status setter — does NOT check immunity. Use `State::apply_status_condition` instead.
    pub(crate) fn set_status_raw(&mut self, status: StatusCondition) {
        match status {
            StatusCondition::Asleep => self.asleep = true,
            StatusCondition::Paralyzed => self.paralyzed = true,
            StatusCondition::Poisoned => {
                self.poisoned = true;
                // A fresh (ordinary) poison replaces any modified poison; attacks with a
                // custom Checkup amount set it again right after poisoning.
                self.poison_checkup_damage = None;
            }
            StatusCondition::Burned => self.burned = true,
            StatusCondition::Confused => self.confused = true,
        }
    }

    /// Whether this Pokémon is currently affected by `status`.
    pub fn has_status(&self, status: StatusCondition) -> bool {
        match status {
            StatusCondition::Poisoned => self.poisoned,
            StatusCondition::Paralyzed => self.paralyzed,
            StatusCondition::Asleep => self.asleep,
            StatusCondition::Burned => self.burned,
            StatusCondition::Confused => self.confused,
        }
    }

    /// Override the Pokémon Checkup poison damage for the current poison ("Do N damage to this
    /// Pokémon instead of the usual amount"). Only meaningful while poisoned.
    pub(crate) fn set_poison_checkup_damage(&mut self, amount: u32) {
        self.poison_checkup_damage = Some(amount);
    }

    /// The Pokémon Checkup poison damage override for the current poison, if any.
    pub(crate) fn poison_checkup_damage(&self) -> Option<u32> {
        self.poison_checkup_damage
    }

    pub(crate) fn end_turn_maintenance(&mut self) {
        // Remove all the ones that are 0, and subtract 1 from the rest
        self.effects.retain_mut(|(_, duration)| {
            if *duration > 0 {
                *duration -= 1;
                true
            } else {
                false
            }
        });

        // Reset played_this_turn, moved_to_active_this_turn, and ability_used
        self.played_this_turn = false;
        self.moved_to_active_this_turn = false;
        self.ability_used = false;

        // Shift the "damaged by an attack while in the Active Spot" flag by one turn
        // (Wobbuffet's Reply Strongly).
        self.damaged_by_attack_while_active_last_turn =
            self.damaged_by_attack_while_active_this_turn;
        self.damaged_by_attack_while_active_this_turn = false;
    }

    /// Returns effective attached energy considering Serperior's Jungle Totem ability.
    /// If Jungle Totem is active for Grass Pokemon, Grass energy counts double.
    pub(crate) fn get_effective_attached_energy(
        &self,
        state: &State,
        player: usize,
    ) -> Vec<EnergyType> {
        let double_grass = self.has_double_grass(state, player);
        if double_grass {
            let mut doubled = Vec::new();
            for energy in &self.attached_energy {
                doubled.push(*energy);
                if *energy == EnergyType::Grass {
                    doubled.push(EnergyType::Grass); // Add another Grass energy
                }
            }
            doubled
        } else {
            self.attached_energy.to_vec()
        }
    }

    pub(crate) fn has_double_grass(&self, state: &State, player: usize) -> bool {
        let pokemon_type = self.card.get_type();
        let jungle_totem_active = has_serperior_jungle_totem(state, player);
        jungle_totem_active && pokemon_type == Some(EnergyType::Grass)
    }
}

impl fmt::Debug for PlayedCard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if f.alternate() {
            write!(
                f,
                "{}({}hp,{:?})",
                self.get_name(),
                self.get_remaining_hp(),
                self.attached_energy
            )
        } else {
            write!(
                f,
                "{}({}hp,{})",
                self.get_name(),
                self.get_remaining_hp(),
                self.attached_energy.len()
            )
        }
    }
}

pub fn has_serperior_jungle_totem(state: &State, player: usize) -> bool {
    state.enumerate_in_play_pokemon(player).any(|(_, pokemon)| {
        has_in_play_ability_mechanic(state, pokemon, &AbilityMechanic::DoubleGrassEnergy)
    })
}

#[cfg(test)]
mod tests {
    use crate::{
        card_ids::CardId, database::get_card_by_enum, hooks::to_playable_card,
        models::has_serperior_jungle_totem, state::State,
    };

    #[test]
    fn test_has_serperior_jungle_totem_with_serperior() {
        // Arrange: Create a state with Serperior on the bench
        let mut state = State::default();
        let serperior_card = get_card_by_enum(CardId::A1a006Serperior);
        let played_serperior = to_playable_card(&serperior_card, false);

        // Place Serperior in bench slot 1
        state.in_play_pokemon[0][1] = Some(played_serperior);

        // Act & Assert
        assert!(
            has_serperior_jungle_totem(&state, 0),
            "Should detect Serperior's Jungle Totem ability when Serperior is in play"
        );
    }

    #[test]
    fn test_has_serperior_jungle_totem_without_serperior() {
        // Arrange: Create a state without Serperior
        let mut state = State::default();
        let bulbasaur_card = get_card_by_enum(CardId::A1001Bulbasaur);
        let played_bulbasaur = to_playable_card(&bulbasaur_card, false);

        // Place Bulbasaur in active slot
        state.in_play_pokemon[0][0] = Some(played_bulbasaur);

        // Act & Assert
        assert!(
            !has_serperior_jungle_totem(&state, 0),
            "Should not detect Jungle Totem ability when Serperior is not in play"
        );
    }

    #[test]
    fn test_has_serperior_jungle_totem_wrong_player() {
        // Arrange: Create a state with Serperior for player 0
        let mut state = State::default();
        let serperior_card = get_card_by_enum(CardId::A1a006Serperior);
        let played_serperior = to_playable_card(&serperior_card, false);

        // Place Serperior in player 0's bench
        state.in_play_pokemon[0][1] = Some(played_serperior);

        // Act & Assert: Check for player 1
        assert!(
            !has_serperior_jungle_totem(&state, 1),
            "Should not detect Jungle Totem ability for opponent player"
        );
    }
}
