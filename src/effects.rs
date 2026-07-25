use serde::{Deserialize, Serialize};

use crate::models::EnergyType;

/// I believe these are the "clearable" ones by retreating...
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum CardEffect {
    NoRetreat,
    ReducedDamage {
        amount: u32,
    },
    IncreasedVulnerability {
        amount: u32,
    },
    IncreasedAttackCost {
        amount: u8,
    },
    CannotAttack,
    CannotUseAttack(String),
    IncreasedDamageForAttack {
        attack_name: String,
        amount: u32,
    },
    PreventAllDamageAndEffects,
    /// Prevent all damage from attacks if the incoming damage is at most `threshold` (e.g. Cascoon's Harden).
    PreventDamageIfLessOrEqual {
        threshold: u32,
    },
    /// Prevent all damage done by attacks from Basic Pokémon (e.g. Carracosta's Blocking Shell).
    PreventDamageFromBasic,
    NoWeakness,
    CoinFlipToBlockAttack,
    DelayedDamage {
        amount: u32,
    },
    /// If this Pokémon is damaged by an attack while in the Active Spot, deal `amount`
    /// damage to the Attacking Pokémon (e.g. Alolan Sandslash's Spike Armor). Temporary
    /// counterpart to RockyHelmet's always-on recoil.
    Counterattack {
        amount: u32,
    },
    /// This Pokémon is about to be Knocked Out, but its holder won the Dusknoir / Glimmora
    /// point-denial coin flip, so the opponent scores nothing for the knockout. Applied by a
    /// forecast branch's post-damage effect and consumed by `handle_knockouts` in the same
    /// resolution — it is never expected to survive to a later turn.
    DenyKnockoutPoints,
    // ---------------------------------------------------------------------------------------------
    // Ability-derived effects. These are not added via `add_effect`; they are *derived* on the fly
    // from a Pokémon's passive ability by `PlayedCard::get_effective_card_effects` (see
    // `card_effect_from_ability_mechanic`). Modeling passive abilities as `CardEffect`s lets damage
    // code check a single "effects on this Pokémon" list instead of scanning the board for
    // abilities, and lets attacks like Sawk's Brick Break ignore *all* effects on the opponent's
    // Active Pokémon uniformly. They have no turn duration — they are present exactly while the
    // ability-holder is in play.
    // ---------------------------------------------------------------------------------------------
    /// This Pokémon takes `amount` less damage from attacks (e.g. Cloyster's Shell Armor).
    /// Applies whether the holder is Active or Benched, mirroring `ReduceDamageFromAttacks`.
    ReduceDamageFromAttacks {
        amount: u32,
    },
    /// While this Pokémon is the Active Spot defender, attacks against it do `amount` less damage
    /// (e.g. Arbok's Intimidating Fang). Mirrors `ReduceOpponentActiveDamage`.
    ReduceOpponentActiveDamage {
        amount: u32,
    },
    /// Prevent all damage done to this Pokémon by attacks from the opponent's Pokémon ex
    /// (e.g. Oricorio's Safeguard). Mirrors `PreventAllDamageFromEx`.
    PreventAllDamageFromEx,
    /// Prevent all damage done to this Pokémon by attacks while it is on the Bench
    /// (e.g. Wartortle's Shell Shield). Mirrors `PreventDamageWhileBenched`.
    PreventDamageWhileBenched,
    /// If any damage is done to this Pokémon by attacks, flip a coin; on heads prevent that damage
    /// (e.g. Meowth's Carefree Steps). Mirrors `CoinFlipToPreventDamage`. Distinct from
    /// `CoinFlipToBlockAttack`, which is an attacker self-debuff on the holder's own attacks.
    CoinFlipToPreventIncomingDamage,
    /// If any damage is done to this Pokémon by attacks, flip a coin; on heads this Pokémon takes
    /// `amount` less damage from that attack (e.g. Bastiodon's Guarded Grill, Hisuian Goodra's
    /// Securely Sheltered). Mirrors `CoinFlipToReduceDamage`.
    CoinFlipToReduceIncomingDamage {
        amount: u32,
    },
}

/// Which of a player's Pokémon a `TurnEffect::ReducedDamageForTarget` protects. The defensive
/// Supporters/Items all read "During your opponent's next turn, <scope> take -N damage from
/// attacks from your opponent's Pokémon", differing only in the scope, so they share one effect.
#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum DamageReductionScope {
    /// "all of your Pokémon" (Blue).
    AllPokemon,
    /// "all of your <names>" (Jasmine: Steelix and Skarmory ex; Cheren: Watchog and Stoutland).
    NamedPokemon(Vec<String>),
    /// "all of your Ultra Beasts" (Beast Wall).
    UltraBeasts,
}

#[derive(Debug, Clone, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub enum TurnEffect {
    NoSupportCards,
    NoItemCards,
    NoTrainerCards,
    NoEnergyFromZoneToActive,
    ReducedRetreatCost {
        amount: u8,
    },
    ReducedDamageForType {
        amount: u32,
        energy_type: EnergyType,
        player: usize,
    },
    /// "During your opponent's next turn, <scope> take -`amount` damage from attacks from your
    /// opponent's Pokémon" (Blue, Jasmine, Beast Wall), or "... from your opponent's Pokémon ex"
    /// when `only_from_ex` is set (Cheren). `player` is the side being protected.
    ReducedDamageForTarget {
        amount: u32,
        player: usize,
        scope: DamageReductionScope,
        only_from_ex: bool,
    },
    IncreasedDamage {
        amount: u32,
    },
    IncreasedDamageForType {
        amount: u32,
        energy_type: EnergyType,
    },
    IncreasedDamageAgainstEx {
        amount: u32,
    },
    IncreasedDamageForEeveeEvolutions {
        amount: u32,
    },
    IncreasedDamageForSpecificPokemon {
        amount: u32,
        pokemon_names: Vec<String>,
    },
    IncreasedDamageForSpecificPokemonAgainstEx {
        amount: u32,
        pokemon_names: Vec<String>,
    },
    IncreasedDamageForTypeAgainstEx {
        amount: u32,
        energy_type: EnergyType,
    },
    DelayedSpotDamage {
        source_player: usize,
        target_player: usize,
        target_in_play_idx: usize,
        amount: u32,
    },
    ForceFirstHeads,
    BonusPointForHaxorusActiveKO,
    /// "During your opponent's next turn, if your <names> would be Knocked Out by damage from an
    /// attack, it is not Knocked Out and its remaining HP becomes `remaining_hp`" (Hala).
    /// `player` is the side being protected.
    SurviveKnockoutForSpecificPokemon {
        remaining_hp: u32,
        pokemon_names: Vec<String>,
        player: usize,
    },
    ReducedAttackCostForSpecificPokemon {
        amount: u8,
        pokemon_names: Vec<String>,
    },
}
