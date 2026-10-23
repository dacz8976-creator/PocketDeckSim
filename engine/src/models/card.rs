use core::fmt;
use std::hash::{Hash, Hasher};

use serde::{Deserialize, Serialize};

use crate::card_ids::CardId;

/// Represents the type of energy.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize, PartialOrd, Ord)]
pub enum EnergyType {
    Grass,
    Fire,
    Water,
    Lightning,
    Psychic,
    Fighting,
    Darkness,
    Metal,
    Dragon,
    Colorless,
}
impl EnergyType {
    pub(crate) fn from_str(energy_type: &str) -> Option<Self> {
        match energy_type {
            "Grass" => Some(EnergyType::Grass),
            "Fire" => Some(EnergyType::Fire),
            "Water" => Some(EnergyType::Water),
            "Lightning" => Some(EnergyType::Lightning),
            "Psychic" => Some(EnergyType::Psychic),
            "Fighting" => Some(EnergyType::Fighting),
            "Darkness" => Some(EnergyType::Darkness),
            "Metal" => Some(EnergyType::Metal),
            "Dragon" => Some(EnergyType::Dragon),
            "Colorless" => Some(EnergyType::Colorless),
            _ => None,
        }
    }

    /// Whether a deck can be built around this energy, i.e. whether the Energy Zone
    /// can generate it (upstream #344).
    ///
    /// Dragon and Colorless cannot. Colorless only ever appears as an attack cost
    /// (payable by any energy), and there is no Dragon energy in the game: Dragon
    /// Pokémon are powered by other types.
    pub fn is_selectable(&self) -> bool {
        !matches!(self, EnergyType::Dragon | EnergyType::Colorless)
    }

    pub fn as_str(&self) -> &'static str {
        match self {
            EnergyType::Grass => "Grass",
            EnergyType::Fire => "Fire",
            EnergyType::Water => "Water",
            EnergyType::Lightning => "Lightning",
            EnergyType::Psychic => "Psychic",
            EnergyType::Fighting => "Fighting",
            EnergyType::Darkness => "Darkness",
            EnergyType::Metal => "Metal",
            EnergyType::Dragon => "Dragon",
            EnergyType::Colorless => "Colorless",
        }
    }
}

/// Represents an attack of a card.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Attack {
    pub energy_required: Vec<EnergyType>,
    pub title: String,
    pub fixed_damage: u32,
    pub effect: Option<String>,
}

/// Represents an attack of a card.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Ability {
    pub title: String,
    pub effect: String,
}

pub const BASIC_STAGE: u8 = 0;

/// Represents the data of a single pokemon card.
///
/// Deserialization goes through the private `PokemonCardWire`, which accepts every printed-type
/// shape (see there). Serialization is the plain derive: `secondary_energy_type` is left out when
/// `None`, so a single-type card serializes exactly as before the field existed.
#[derive(Clone, Serialize, Deserialize)]
#[serde(try_from = "PokemonCardWire")]
pub struct PokemonCard {
    pub id: String,
    pub name: String,
    pub stage: u8, // 0 for Basic, 1 for Stage 1, 2 for Stage 2
    pub evolves_from: Option<String>,
    pub hp: u32,
    /// The *primary* printed type (the first one printed on a dual-type card).
    pub energy_type: EnergyType,
    /// The second printed type of a dual-type card (Dual Fusion's Mega Mewtwo X ex is
    /// Psychic/Fighting); `None` for every single-type card. Ask "is this a [X] Pokémon?" through
    /// [`Self::has_printed_type`] / [`Card::is_type`], not through `energy_type` alone.
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub secondary_energy_type: Option<EnergyType>,
    pub ability: Option<Ability>,
    pub attacks: Vec<Attack>,
    pub weakness: Option<EnergyType>,
    pub retreat_cost: Vec<EnergyType>,
    pub rarity: String,
    pub booster_pack: String,
}
impl PartialEq for PokemonCard {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}
impl Eq for PokemonCard {}
impl Hash for PokemonCard {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.id.hash(state);
    }
}
impl PokemonCard {
    /// Every printed type of this card: `[energy_type]`, or `[energy_type, secondary_energy_type]`
    /// for a dual-type card. Printed only: Abilities such as Urshifu's Double Type are counted by
    /// `State::pokemon_energy_types`, not here.
    pub fn printed_types(&self) -> Vec<EnergyType> {
        let mut types = vec![self.energy_type];
        types.extend(self.secondary_energy_type);
        types
    }

    /// Whether `energy_type` is one of this card's printed types (any-of over
    /// [`Self::printed_types`], without allocating). For a single-type card this is exactly
    /// `self.energy_type == energy_type`.
    pub fn has_printed_type(&self, energy_type: EnergyType) -> bool {
        self.energy_type == energy_type || self.secondary_energy_type == Some(energy_type)
    }
}

/// The accepted JSON shapes of a `PokemonCard` (database.json and every saved game state). Field
/// for field the same as `PokemonCard`, so a missing `ability`, `evolves_from` or `weakness` is
/// still `None`, unknown fields are still ignored and a `weakness` list is still an error. Only
/// the printed type has more than one shape:
/// - `"energy_type": "Psychic"` (every card today), optionally with
///   `"secondary_energy_type": "Fighting"` (upstream issue #429, option (a));
/// - `"energy_type": ["Psychic", "Fighting"]`;
/// - `"energy_types": ["Psychic", "Fighting"]` (#429 option (b)), alone, next to the fields
///   above when it repeats them exactly, or next to a one-type `"energy_type"` that is its first
///   entry (a transitional shape that keeps old readers working).
///
/// `TryFrom` normalises them to `energy_type` + `secondary_energy_type` and refuses an empty list,
/// more than two types, a repeated type, and shapes that disagree.
#[derive(Deserialize)]
struct PokemonCardWire {
    id: String,
    name: String,
    stage: u8,
    evolves_from: Option<String>,
    hp: u32,
    energy_type: Option<PrintedTypeField>,
    #[serde(default)]
    secondary_energy_type: Option<EnergyType>,
    #[serde(default)]
    energy_types: Option<Vec<EnergyType>>,
    ability: Option<Ability>,
    attacks: Vec<Attack>,
    weakness: Option<EnergyType>,
    retreat_cost: Vec<EnergyType>,
    rarity: String,
    booster_pack: String,
}

/// `energy_type` as written: one type, or a list of them.
enum PrintedTypeField {
    One(EnergyType),
    List(Vec<EnergyType>),
}

impl<'de> Deserialize<'de> for PrintedTypeField {
    fn deserialize<D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        struct PrintedTypeVisitor;
        impl<'de> serde::de::Visitor<'de> for PrintedTypeVisitor {
            type Value = PrintedTypeField;

            fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
                formatter.write_str("an energy type or a list of energy types")
            }

            // Parsed by `EnergyType`'s own Deserialize, so an unknown type keeps serde's usual
            // "unknown variant" message.
            fn visit_str<E: serde::de::Error>(self, value: &str) -> Result<Self::Value, E> {
                EnergyType::deserialize(serde::de::value::StrDeserializer::<E>::new(value))
                    .map(PrintedTypeField::One)
            }

            fn visit_seq<A: serde::de::SeqAccess<'de>>(
                self,
                seq: A,
            ) -> Result<Self::Value, A::Error> {
                Vec::<EnergyType>::deserialize(serde::de::value::SeqAccessDeserializer::new(seq))
                    .map(PrintedTypeField::List)
            }
        }
        deserializer.deserialize_any(PrintedTypeVisitor)
    }
}

impl TryFrom<PokemonCardWire> for PokemonCard {
    type Error = String;

    fn try_from(wire: PokemonCardWire) -> Result<Self, Self::Error> {
        let (energy_type, secondary_energy_type) = normalise_printed_types(
            wire.energy_type,
            wire.secondary_energy_type,
            wire.energy_types,
        )
        .map_err(|problem| format!("Pokémon card {:?}: {problem}", wire.id))?;
        Ok(PokemonCard {
            id: wire.id,
            name: wire.name,
            stage: wire.stage,
            evolves_from: wire.evolves_from,
            hp: wire.hp,
            energy_type,
            secondary_energy_type,
            ability: wire.ability,
            attacks: wire.attacks,
            weakness: wire.weakness,
            retreat_cost: wire.retreat_cost,
            rarity: wire.rarity,
            booster_pack: wire.booster_pack,
        })
    }
}

/// The printed-type fields of a `PokemonCardWire` as (primary, optional secondary). See
/// `PokemonCardWire` for the accepted shapes.
fn normalise_printed_types(
    energy_type: Option<PrintedTypeField>,
    secondary_energy_type: Option<EnergyType>,
    energy_types: Option<Vec<EnergyType>>,
) -> Result<(EnergyType, Option<EnergyType>), String> {
    // A one-type `energy_type` with no `secondary_energy_type`: beside an `energy_types` list it may
    // be just the list's first entry (the transitional shape that keeps old readers working).
    let mut lone_primary = None;
    // The set that `energy_type` (+ `secondary_energy_type`) gives, if `energy_type` is present.
    let from_energy_type = match (energy_type, secondary_energy_type) {
        (Some(PrintedTypeField::One(primary)), secondary) => {
            if secondary.is_none() {
                lone_primary = Some(primary);
            }
            Some(std::iter::once(primary).chain(secondary).collect::<Vec<_>>())
        }
        (Some(PrintedTypeField::List(types)), None) => Some(types),
        // A list is the whole printed set: a `secondary_energy_type` beside it may only repeat
        // the list's second entry.
        (Some(PrintedTypeField::List(types)), Some(secondary)) => {
            if types.len() != 2 || types[1] != secondary {
                return Err(format!(
                    "`secondary_energy_type` {secondary:?} disagrees with the `energy_type` list {types:?}"
                ));
            }
            Some(types)
        }
        (None, Some(secondary)) => {
            return Err(format!(
                "`secondary_energy_type` {secondary:?} is given without `energy_type`"
            ));
        }
        (None, None) => None,
    };
    let types = match (from_energy_type, energy_types) {
        (Some(_), Some(energy_types))
            if lone_primary.is_some() && energy_types.first() == lone_primary.as_ref() =>
        {
            energy_types
        }
        (Some(from_energy_type), Some(energy_types)) if from_energy_type != energy_types => {
            return Err(format!(
                "`energy_types` {energy_types:?} disagrees with `energy_type` + `secondary_energy_type` {from_energy_type:?}"
            ));
        }
        (Some(types), _) | (None, Some(types)) => types,
        (None, None) => return Err("missing field `energy_type` (or `energy_types`)".to_string()),
    };
    match types[..] {
        [primary] => Ok((primary, None)),
        [primary, secondary] if primary != secondary => Ok((primary, Some(secondary))),
        [primary, _] => Err(format!("printed type {primary:?} is given twice")),
        [] => Err("the printed type list is empty".to_string()),
        _ => Err(format!(
            "{} printed types {types:?}; a Pokémon card has one or two",
            types.len()
        )),
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum TrainerType {
    Supporter,
    Item,
    Tool,
    Fossil,
    Stadium,
}

impl TrainerType {
    /// Whether a card of this type is a card of the printed kind `printed`. A Fossil's printed kind is Item (rules/01,
    /// rules/04 §6): it is an "Item card" wherever a card text says so, though the engine plays it as a 40-HP Basic.
    /// Every other type matches only itself.
    pub fn is_printed_as(&self, printed: &TrainerType) -> bool {
        // G11 (P3) of rules switch 2's revert switches: off, every type matches only itself, as before.
        self == printed
            || (crate::actions::fossil_as_item_on()
                && *printed == TrainerType::Item
                && *self == TrainerType::Fossil)
    }
}

/// Represents the data of a single trainer card.
#[derive(Clone, Serialize, Deserialize)]
pub struct TrainerCard {
    pub id: String,
    pub trainer_card_type: TrainerType,
    pub name: String,
    pub effect: String,
    pub rarity: String,
    pub booster_pack: String,
}
impl PartialEq for TrainerCard {
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}
impl Eq for TrainerCard {}
impl Hash for TrainerCard {
    fn hash<H: Hasher>(&self, state: &mut H) {
        self.id.hash(state);
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum Card {
    Pokemon(PokemonCard),
    Trainer(TrainerCard),
    /// A count-preserving placeholder for a card whose identity is not observable.
    ///
    /// This is deliberately not a card from the catalog and must never be played or
    /// included in a legal deck. It exists only in sanitized observations/search worlds.
    Unknown,
}
impl Hash for Card {
    fn hash<H: Hasher>(&self, state: &mut H) {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.id.hash(state),
            Card::Trainer(trainer_card) => trainer_card.id.hash(state),
            Card::Unknown => "Unknown".hash(state),
        }
    }
}
impl Card {
    pub fn get_id(&self) -> String {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.id.clone(),
            Card::Trainer(trainer_card) => trainer_card.id.clone(),
            Card::Unknown => "Unknown".to_string(),
        }
    }

    pub fn get_name(&self) -> String {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.name.clone(),
            Card::Trainer(trainer_card) => trainer_card.name.clone(),
            Card::Unknown => "Unknown".to_string(),
        }
    }

    pub fn is_unknown(&self) -> bool {
        matches!(self, Card::Unknown)
    }

    pub(crate) fn get_attacks(&self) -> Vec<Attack> {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.attacks.clone(),
            _ => vec![],
        }
    }

    pub fn get_retreat_cost(&self) -> Option<Vec<EnergyType>> {
        match self {
            Card::Pokemon(pokemon_card) => Some(pokemon_card.retreat_cost.clone()),
            _ => None, // Fossils
        }
    }

    pub(crate) fn is_ex(&self) -> bool {
        // A pokemon is EX if after splitting by spaces in the name, the last word is "EX"
        match self {
            Card::Pokemon(pokemon_card) => {
                pokemon_card.name.to_lowercase().split(' ').next_back() == Some("ex")
            }
            _ => false,
        }
    }

    pub(crate) fn is_mega(&self) -> bool {
        // A pokemon is Mega if the name starts with "Mega "
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.name.starts_with("Mega "),
            _ => false,
        }
    }

    pub(crate) fn get_knockout_points(&self) -> u8 {
        if self.is_unknown() {
            return 0;
        }
        // Mega pokemon are worth 3 points, ex pokemon are worth 2, regular pokemon are worth 1
        if self.is_mega() {
            3
        } else if self.is_ex() {
            2
        } else {
            1
        }
    }

    pub(crate) fn get_ability(&self) -> Option<Ability> {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.ability.clone(),
            _ => None,
        }
    }

    pub(crate) fn is_support(&self) -> bool {
        match self {
            Card::Trainer(trainer_card) => trainer_card.trainer_card_type == TrainerType::Supporter,
            _ => false,
        }
    }

    /// The *primary* printed type of a Pokémon card (`None` otherwise). A value, for code that
    /// needs one type as data; ask "is this a [X] Pokémon?" with [`Self::is_type`] instead.
    /// Its only caller left is the Python binding.
    #[cfg_attr(not(feature = "python"), allow(dead_code))]
    pub(crate) fn get_type(&self) -> Option<EnergyType> {
        match self {
            Card::Pokemon(pokemon_card) => Some(pokemon_card.energy_type),
            _ => None,
        }
    }

    /// Every printed type of a Pokémon card ([`PokemonCard::printed_types`]); empty for a Trainer
    /// or an Unknown card. Same name and meaning as upstream deckgym #374.
    pub fn get_types(&self) -> Vec<EnergyType> {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.printed_types(),
            _ => vec![],
        }
    }

    /// Whether this is a Pokémon card printed as `energy_type`, counting either type of a
    /// dual-type card; `false` for a Trainer or an Unknown card (upstream deckgym #374's
    /// `is_type`). Printed only: Abilities such as Urshifu's Double Type are counted by
    /// `State::pokemon_is_type`, not here.
    pub fn is_type(&self, energy_type: EnergyType) -> bool {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.has_printed_type(energy_type),
            _ => false,
        }
    }

    pub fn get_card_id(&self) -> CardId {
        CardId::from_card_id(self.get_id().as_str()).expect("Card ID should be valid")
    }

    pub fn is_basic(&self) -> bool {
        match self {
            Card::Pokemon(pokemon_card) => pokemon_card.stage == BASIC_STAGE,
            _ => false,
        }
    }

    pub fn is_fossil(&self) -> bool {
        match self {
            Card::Trainer(trainer_card) => trainer_card.trainer_card_type == TrainerType::Fossil,
            _ => false,
        }
    }

    /// An Item card, a Fossil included (its printed kind; `TrainerType::is_printed_as`).
    pub fn is_item(&self) -> bool {
        matches!(self, Card::Trainer(t) if t.trainer_card_type.is_printed_as(&TrainerType::Item))
    }

    pub fn as_trainer(&self) -> TrainerCard {
        match self {
            Card::Trainer(trainer_card) => trainer_card.clone(),
            _ => panic!("Card is not a Trainer"),
        }
    }

    /// Whether `evolution_card` evolves from this card by the *printed* rule (name match).
    ///
    /// Ability-granted evolution (Eevee's Veevee 'volve) is deliberately not handled here: it
    /// depends on the board, because Power of Alchemy switches off Basic Pokémon's Abilities.
    /// Use `hooks::can_evolve_into` for a Pokémon that is in play.
    pub fn can_evolve_into(&self, evolution_card: &Card) -> bool {
        matches!(evolution_card, Card::Pokemon(evolution_pokemon)
            if evolution_pokemon.evolves_from.as_deref() == Some(self.get_name().as_str()))
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum StatusCondition {
    Poisoned,
    Paralyzed,
    Asleep,
    Burned,
    Confused,
}

impl fmt::Display for Card {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Card::Pokemon(pokemon_card) => write!(f, "{}", pokemon_card.name),
            Card::Trainer(trainer_card) => write!(f, "{}", trainer_card.name),
            Card::Unknown => write!(f, "Unknown"),
        }
    }
}

impl fmt::Display for EnergyType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            EnergyType::Grass => write!(f, "Grass"),
            EnergyType::Fire => write!(f, "Fire"),
            EnergyType::Water => write!(f, "Water"),
            EnergyType::Lightning => write!(f, "Lightning"),
            EnergyType::Psychic => write!(f, "Psychic"),
            EnergyType::Fighting => write!(f, "Fighting"),
            EnergyType::Darkness => write!(f, "Darkness"),
            EnergyType::Metal => write!(f, "Metal"),
            EnergyType::Dragon => write!(f, "Dragon"),
            EnergyType::Colorless => write!(f, "Colorless"),
        }
    }
}

impl fmt::Debug for PokemonCard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if f.alternate() {
            write!(f, "{}", self.name)
        } else {
            write!(f, "{} {}", self.id, self.name)
        }
    }
}

impl fmt::Debug for TrainerCard {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if f.alternate() {
            write!(f, "{}", self.name)
        } else {
            write!(f, "{} {}", self.id, self.name)
        }
    }
}
