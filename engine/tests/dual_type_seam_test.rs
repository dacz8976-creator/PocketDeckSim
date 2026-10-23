//! Dual-type seam, step 1 (Dual Fusion prep): a `PokemonCard` can carry a printed type *set*
//! (`energy_type` + `secondary_energy_type`), every accepted JSON shape normalises to it, every
//! current card is still single-type and serializes byte for byte as before, and the in-play
//! chokepoint `State::pokemon_energy_types` reads the printed set.
//!
//! The dual-type cards here are synthetic: a real database card with `secondary_energy_type` set.
use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard, PokemonCard},
    test_support::{attack_action, get_initialized_game, get_test_game_with_board},
    State,
};
use serde_json::{json, Map, Value};
use strum::IntoEnumIterator;

const ALL_TYPES: [EnergyType; 10] = [
    EnergyType::Grass,
    EnergyType::Fire,
    EnergyType::Water,
    EnergyType::Lightning,
    EnergyType::Psychic,
    EnergyType::Fighting,
    EnergyType::Darkness,
    EnergyType::Metal,
    EnergyType::Dragon,
    EnergyType::Colorless,
];

/// Exactly what main's derived `Serialize` writes for A1 001 Bulbasaur: no
/// `secondary_energy_type` key, fields in declaration order. (Rarity is U+25CA.)
const BULBASAUR_LEGACY_JSON: &str = concat!(
    r#"{"id":"A1 001","name":"Bulbasaur","stage":0,"evolves_from":null,"hp":70,"#,
    r#""energy_type":"Grass","ability":null,"#,
    r#""attacks":[{"energy_required":["Grass","Colorless"],"title":"Vine Whip","#,
    r#""fixed_damage":40,"effect":null}],"#,
    "\"weakness\":\"Fire\",\"retreat_cost\":[\"Colorless\"],\"rarity\":\"\u{25CA}\",",
    r#""booster_pack":"Genetic Apex (A1)"}"#,
);

fn pokemon_card(card_id: CardId) -> PokemonCard {
    match get_card_by_enum(card_id) {
        Card::Pokemon(pokemon_card) => pokemon_card,
        other => panic!("{card_id:?} should be a Pokémon, got {other:?}"),
    }
}

/// A real database card made dual-type by giving it `secondary` as its second printed type.
fn dual_type_card(card_id: CardId, secondary: EnergyType) -> Card {
    let mut card = pokemon_card(card_id);
    card.secondary_energy_type = Some(secondary);
    Card::Pokemon(card)
}

fn bulbasaur_with_secondary(secondary: EnergyType) -> PokemonCard {
    let mut card = pokemon_card(CardId::A1001Bulbasaur);
    card.secondary_energy_type = Some(secondary);
    card
}

/// Bulbasaur's JSON fields with `changes` applied: `Some(value)` sets the key, `None` removes it.
fn bulbasaur_fields(changes: Vec<(&str, Option<Value>)>) -> Map<String, Value> {
    let mut fields = match serde_json::to_value(pokemon_card(CardId::A1001Bulbasaur)).unwrap() {
        Value::Object(fields) => fields,
        other => panic!("a PokemonCard serializes to an object, got {other}"),
    };
    for (key, value) in changes {
        match value {
            Some(value) => {
                fields.insert(key.to_string(), value);
            }
            None => {
                fields.remove(key);
            }
        }
    }
    fields
}

fn parse(fields: &Map<String, Value>) -> Result<PokemonCard, serde_json::Error> {
    serde_json::from_value(Value::Object(fields.clone()))
}

fn refusal(fields: &Map<String, Value>) -> String {
    match parse(fields) {
        Ok(card) => panic!(
            "expected a refusal, got {card:?} with printed types {:?}",
            card.printed_types()
        ),
        Err(error) => error.to_string(),
    }
}

/// `PokemonCard`'s `==` compares ids only, so compare the printed types and the whole
/// serialization instead.
fn assert_same_card(actual: &PokemonCard, expected: &PokemonCard, shape: &str) {
    assert_eq!(actual.energy_type, expected.energy_type, "{shape}");
    assert_eq!(
        actual.secondary_energy_type, expected.secondary_energy_type,
        "{shape}"
    );
    assert_eq!(
        serde_json::to_string(actual).unwrap(),
        serde_json::to_string(expected).unwrap(),
        "{shape}"
    );
}

// ---------------------------------------------------------------------------------------------
// Serde: accepted shapes
// ---------------------------------------------------------------------------------------------

#[test]
fn every_accepted_dual_type_shape_gives_the_same_card() {
    let expected = bulbasaur_with_secondary(EnergyType::Psychic);
    let both = || Some(json!(["Grass", "Psychic"]));
    let shapes = [
        (
            "#429 (a): energy_type + secondary_energy_type",
            vec![("secondary_energy_type", Some(json!("Psychic")))],
        ),
        ("energy_type as a list", vec![("energy_type", both())]),
        (
            "energy_type list + secondary_energy_type repeating its second entry",
            vec![
                ("energy_type", both()),
                ("secondary_energy_type", Some(json!("Psychic"))),
            ],
        ),
        (
            "#429 (b): energy_types alone",
            vec![("energy_type", None), ("energy_types", both())],
        ),
        (
            "energy_type + secondary_energy_type + agreeing energy_types",
            vec![
                ("secondary_energy_type", Some(json!("Psychic"))),
                ("energy_types", both()),
            ],
        ),
        (
            "energy_type list + agreeing energy_types",
            vec![("energy_type", both()), ("energy_types", both())],
        ),
        (
            "transitional: one-type energy_type kept as the primary + energy_types",
            vec![("energy_types", both())],
        ),
    ];
    for (shape, changes) in shapes {
        let card = parse(&bulbasaur_fields(changes))
            .unwrap_or_else(|error| panic!("{shape}: {error}"));
        assert_eq!(
            card.printed_types(),
            vec![EnergyType::Grass, EnergyType::Psychic],
            "{shape}"
        );
        assert_same_card(&card, &expected, shape);
    }
}

#[test]
fn every_accepted_single_type_shape_gives_todays_card() {
    let expected = pokemon_card(CardId::A1001Bulbasaur);
    let shapes = [
        ("today's energy_type string", vec![]),
        (
            "explicit null secondary_energy_type",
            vec![("secondary_energy_type", Some(Value::Null))],
        ),
        ("energy_type as a one-entry list", vec![("energy_type", Some(json!(["Grass"])))]),
        (
            "energy_types alone",
            vec![("energy_type", None), ("energy_types", Some(json!(["Grass"])))],
        ),
        (
            "energy_type + agreeing energy_types",
            vec![("energy_types", Some(json!(["Grass"])))],
        ),
    ];
    for (shape, changes) in shapes {
        let card = parse(&bulbasaur_fields(changes))
            .unwrap_or_else(|error| panic!("{shape}: {error}"));
        assert_eq!(card.printed_types(), vec![EnergyType::Grass], "{shape}");
        assert_same_card(&card, &expected, shape);
    }
}

#[test]
fn a_dual_type_card_deserializes_inside_the_card_enum() {
    let fields = bulbasaur_fields(vec![
        ("energy_type", None),
        ("energy_types", Some(json!(["Grass", "Psychic"]))),
    ]);
    let mut wrapper = Map::new();
    wrapper.insert("Pokemon".to_string(), Value::Object(fields));
    let card: Card = serde_json::from_value(Value::Object(wrapper)).unwrap();
    assert_eq!(card.get_types(), vec![EnergyType::Grass, EnergyType::Psychic]);
}

#[test]
fn a_dual_type_card_serializes_its_secondary_right_after_energy_type_and_round_trips() {
    let card = bulbasaur_with_secondary(EnergyType::Psychic);
    let text = serde_json::to_string(&card).unwrap();
    assert!(
        text.contains(r#""energy_type":"Grass","secondary_energy_type":"Psychic","ability":null"#),
        "{text}"
    );
    let back: PokemonCard = serde_json::from_str(&text).unwrap();
    assert_same_card(&back, &card, "round trip");
}

// ---------------------------------------------------------------------------------------------
// Serde: byte-identical legacy JSON
// ---------------------------------------------------------------------------------------------

#[test]
fn a_database_card_serializes_exactly_as_on_main() {
    let text = serde_json::to_string(&pokemon_card(CardId::A1001Bulbasaur)).unwrap();
    assert_eq!(text, BULBASAUR_LEGACY_JSON);
    assert!(!text.contains("secondary_energy_type"));
}

#[test]
fn legacy_card_json_round_trips_byte_identical() {
    let card: PokemonCard = serde_json::from_str(BULBASAUR_LEGACY_JSON).unwrap();
    assert_eq!(card.energy_type, EnergyType::Grass);
    assert_eq!(card.secondary_energy_type, None);
    assert_eq!(serde_json::to_string(&card).unwrap(), BULBASAUR_LEGACY_JSON);

    let wrapped = format!(r#"{{"Pokemon":{BULBASAUR_LEGACY_JSON}}}"#);
    let card: Card = serde_json::from_str(&wrapped).unwrap();
    assert_eq!(serde_json::to_string(&card).unwrap(), wrapped);
}

#[test]
fn every_database_card_round_trips_without_a_secondary_key() {
    for card_id in CardId::iter() {
        let card = get_card_by_enum(card_id);
        let text = serde_json::to_string(&card).unwrap();
        assert!(!text.contains("secondary_energy_type"), "{card_id:?}: {text}");
        let back: Card = serde_json::from_str(&text)
            .unwrap_or_else(|error| panic!("{card_id:?} does not deserialize: {error}"));
        assert_eq!(serde_json::to_string(&back).unwrap(), text, "{card_id:?}");
    }
}

#[test]
fn saved_state_omits_the_key_for_single_type_cards_and_carries_a_dual_type_card() {
    let plain = serde_json::to_string(&get_initialized_game(0).get_state_clone()).unwrap();
    assert!(!plain.contains("secondary_energy_type"));
    let _: State = serde_json::from_str(&plain).unwrap();

    let game = get_test_game_with_board(
        vec![PlayedCard::from_card(&dual_type_card(
            CardId::A1001Bulbasaur,
            EnergyType::Fighting,
        ))],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    let text = serde_json::to_string(&game.get_state_clone()).unwrap();
    assert!(text.contains(r#""energy_type":"Grass","secondary_energy_type":"Fighting""#));
    let restored: State = serde_json::from_str(&text).unwrap();
    assert_eq!(
        restored.pokemon_energy_types(restored.get_active(0)),
        vec![EnergyType::Grass, EnergyType::Fighting]
    );
}

// ---------------------------------------------------------------------------------------------
// Serde: refusals
// ---------------------------------------------------------------------------------------------

#[test]
fn malformed_printed_types_are_refused_with_a_clear_message() {
    let refusals = [
        ("is empty", vec![("energy_type", Some(json!([])))]),
        (
            "is empty",
            vec![("energy_type", None), ("energy_types", Some(json!([])))],
        ),
        (
            "3 printed types",
            vec![("energy_type", Some(json!(["Grass", "Psychic", "Fighting"])))],
        ),
        (
            "3 printed types",
            vec![
                ("energy_type", None),
                ("energy_types", Some(json!(["Grass", "Psychic", "Fighting"]))),
            ],
        ),
        (
            "given twice",
            vec![("secondary_energy_type", Some(json!("Grass")))],
        ),
        ("given twice", vec![("energy_type", Some(json!(["Grass", "Grass"])))]),
        (
            "given twice",
            vec![("energy_type", None), ("energy_types", Some(json!(["Grass", "Grass"])))],
        ),
        // energy_types disagrees with energy_type (+ secondary_energy_type).
        (
            "disagrees",
            vec![("energy_types", Some(json!(["Psychic", "Grass"])))],
        ),
        (
            "disagrees",
            vec![
                ("secondary_energy_type", Some(json!("Psychic"))),
                ("energy_types", Some(json!(["Psychic", "Grass"]))),
            ],
        ),
        (
            "disagrees",
            vec![
                ("energy_type", Some(json!(["Grass", "Psychic"]))),
                ("energy_types", Some(json!(["Grass"]))),
            ],
        ),
        // A secondary_energy_type next to an energy_type list must repeat the list's second entry.
        (
            "disagrees",
            vec![
                ("energy_type", Some(json!(["Grass", "Psychic"]))),
                ("secondary_energy_type", Some(json!("Fighting"))),
            ],
        ),
        (
            "disagrees",
            vec![
                ("energy_type", Some(json!(["Grass"]))),
                ("secondary_energy_type", Some(json!("Psychic"))),
            ],
        ),
        (
            "without `energy_type`",
            vec![
                ("energy_type", None),
                ("secondary_energy_type", Some(json!("Psychic"))),
            ],
        ),
        (
            "without `energy_type`",
            vec![
                ("energy_type", None),
                ("secondary_energy_type", Some(json!("Psychic"))),
                ("energy_types", Some(json!(["Grass", "Psychic"]))),
            ],
        ),
        ("missing field `energy_type`", vec![("energy_type", None)]),
        (
            "missing field `energy_type`",
            vec![("energy_type", Some(Value::Null))],
        ),
    ];
    for (expected, changes) in refusals {
        let shape = format!("{changes:?}");
        let message = refusal(&bulbasaur_fields(changes));
        assert!(message.contains(expected), "{shape}: {message}");
        assert!(message.contains("A1 001"), "{shape}: the message names the card: {message}");
    }
}

#[test]
fn unknown_or_mistyped_printed_types_are_refused() {
    let refusals = [
        ("unknown variant `Fairy`", vec![("energy_type", Some(json!("Fairy")))]),
        (
            "unknown variant `Fairy`",
            vec![("energy_type", Some(json!(["Grass", "Fairy"])))],
        ),
        (
            "unknown variant `Fairy`",
            vec![("secondary_energy_type", Some(json!("Fairy")))],
        ),
        (
            "unknown variant `Fairy`",
            vec![("energy_type", None), ("energy_types", Some(json!(["Fairy"])))],
        ),
        (
            "an energy type or a list of energy types",
            vec![("energy_type", Some(json!(3)))],
        ),
    ];
    for (expected, changes) in refusals {
        let shape = format!("{changes:?}");
        let message = refusal(&bulbasaur_fields(changes));
        assert!(message.contains(expected), "{shape}: {message}");
    }
}

/// Weakness stays one printed type: a list is not accepted in any length.
#[test]
fn a_weakness_list_is_refused() {
    for weakness in [json!(["Fire", "Water"]), json!(["Fire"])] {
        assert!(
            parse(&bulbasaur_fields(vec![("weakness", Some(weakness.clone()))])).is_err(),
            "weakness {weakness} must be refused"
        );
    }
    // The single string is still fine.
    let card = parse(&bulbasaur_fields(vec![("weakness", Some(json!("Water")))])).unwrap();
    assert_eq!(card.weakness, Some(EnergyType::Water));
}

// ---------------------------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------------------------

#[test]
fn printed_type_helpers_on_a_single_type_card() {
    let pokemon = pokemon_card(CardId::A1001Bulbasaur);
    let card = Card::Pokemon(pokemon.clone());
    assert_eq!(pokemon.printed_types(), vec![EnergyType::Grass]);
    assert_eq!(card.get_types(), vec![EnergyType::Grass]);
    for energy_type in ALL_TYPES {
        let expected = energy_type == EnergyType::Grass;
        assert_eq!(pokemon.has_printed_type(energy_type), expected, "{energy_type:?}");
        assert_eq!(card.is_type(energy_type), expected, "{energy_type:?}");
    }
}

#[test]
fn printed_type_helpers_on_a_dual_type_card() {
    let pokemon = bulbasaur_with_secondary(EnergyType::Psychic);
    let card = Card::Pokemon(pokemon.clone());
    assert_eq!(
        pokemon.printed_types(),
        vec![EnergyType::Grass, EnergyType::Psychic]
    );
    assert_eq!(card.get_types(), vec![EnergyType::Grass, EnergyType::Psychic]);
    for energy_type in ALL_TYPES {
        let expected = matches!(energy_type, EnergyType::Grass | EnergyType::Psychic);
        assert_eq!(pokemon.has_printed_type(energy_type), expected, "{energy_type:?}");
        assert_eq!(card.is_type(energy_type), expected, "{energy_type:?}");
    }
}

#[test]
fn printed_type_helpers_on_non_pokemon_cards() {
    for card in [get_card_by_enum(CardId::PA001Potion), Card::Unknown] {
        assert!(card.get_types().is_empty(), "{card:?}");
        for energy_type in ALL_TYPES {
            assert!(!card.is_type(energy_type), "{card:?} {energy_type:?}");
        }
    }
}

/// Every current card is single-type, so every membership helper equals the old `==`.
#[test]
fn every_database_pokemon_is_single_type() {
    let mut pokemon = 0;
    for card_id in CardId::iter() {
        let card = get_card_by_enum(card_id);
        let Card::Pokemon(pokemon_card) = &card else {
            assert!(card.get_types().is_empty(), "{card_id:?}");
            continue;
        };
        pokemon += 1;
        assert_eq!(pokemon_card.secondary_energy_type, None, "{card_id:?}");
        assert_eq!(
            pokemon_card.printed_types(),
            vec![pokemon_card.energy_type],
            "{card_id:?}"
        );
        assert_eq!(card.get_types(), vec![pokemon_card.energy_type], "{card_id:?}");
        for energy_type in ALL_TYPES {
            let old = pokemon_card.energy_type == energy_type;
            assert_eq!(pokemon_card.has_printed_type(energy_type), old, "{card_id:?}");
            assert_eq!(card.is_type(energy_type), old, "{card_id:?}");
        }
    }
    assert!(pokemon > 3000, "only {pokemon} Pokémon found");
}

/// The generator's input still parses through the new Deserialize, and every card in it is
/// single-type. (Integration tests run from `engine/`.)
#[test]
fn database_json_parses_and_is_single_type() {
    let text = std::fs::read_to_string("database.json").expect("database.json in engine/");
    let cards: Vec<Card> = serde_json::from_str(&text).expect("database.json should parse");
    let mut pokemon = 0;
    for card in &cards {
        if let Card::Pokemon(pokemon_card) = card {
            pokemon += 1;
            assert_eq!(pokemon_card.secondary_energy_type, None, "{}", pokemon_card.id);
            assert_eq!(
                pokemon_card.printed_types(),
                vec![pokemon_card.energy_type],
                "{}",
                pokemon_card.id
            );
        }
    }
    assert!(pokemon > 3000, "only {pokemon} Pokémon in database.json");
}

// ---------------------------------------------------------------------------------------------
// The in-play chokepoint
// ---------------------------------------------------------------------------------------------

#[test]
fn chokepoint_counts_both_printed_types_of_an_in_play_dual_type_card() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_card(&dual_type_card(
            CardId::A1001Bulbasaur,
            EnergyType::Fighting,
        ))],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    let state = game.get_state_clone();
    let active = state.get_active(0);
    assert_eq!(
        state.pokemon_energy_types(active),
        vec![EnergyType::Grass, EnergyType::Fighting]
    );
    assert!(state.pokemon_is_type(active, EnergyType::Grass));
    assert!(state.pokemon_is_type(active, EnergyType::Fighting));
    assert!(!state.pokemon_is_type(active, EnergyType::Water));
}

/// Control: a single-type card in play counts as its printed type and nothing else.
#[test]
fn chokepoint_single_type_card_is_its_printed_type_only() {
    let game = get_test_game_with_board(
        vec![PlayedCard::from_id(CardId::A1001Bulbasaur)],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    let state = game.get_state_clone();
    assert_eq!(
        state.pokemon_energy_types(state.get_active(0)),
        vec![EnergyType::Grass]
    );
    assert_eq!(
        state.pokemon_energy_types(state.get_active(1)),
        vec![EnergyType::Water]
    );
    for energy_type in ALL_TYPES {
        assert_eq!(
            state.pokemon_is_type(state.get_active(0), energy_type),
            energy_type == EnergyType::Grass,
            "{energy_type:?}"
        );
    }
}

/// Urshifu's Double Type still *replaces* the printed set (unchanged; see the TODO(dual-type) in
/// `State::pokemon_energy_types`), even on a synthetic card that also has a printed second type.
#[test]
fn double_type_ability_still_replaces_the_printed_set() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_card(&dual_type_card(
                CardId::B3113SingleStrikeUrshifu,
                EnergyType::Water,
            )),
            PlayedCard::from_id(CardId::B3113SingleStrikeUrshifu),
        ],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    let state = game.get_state_clone();
    let synthetic = state.in_play_pokemon[0][0].as_ref().unwrap();
    let printed = state.in_play_pokemon[0][1].as_ref().unwrap();
    for pokemon in [synthetic, printed] {
        assert_eq!(
            state.pokemon_energy_types(pokemon),
            vec![EnergyType::Fighting, EnergyType::Darkness]
        );
        assert!(!state.pokemon_is_type(pokemon, EnergyType::Water));
    }
}

/// With its Ability switched off (Prickly Powder's `NoAbilities`), the chokepoint falls back to
/// the printed set: both printed types of the synthetic card, the one printed type of the real one.
#[test]
fn switched_off_double_type_falls_back_to_the_printed_set() {
    let mut synthetic = PlayedCard::from_card(&dual_type_card(
        CardId::B3113SingleStrikeUrshifu,
        EnergyType::Water,
    ));
    synthetic.add_effect(CardEffect::NoAbilities, 1);
    let mut printed = PlayedCard::from_id(CardId::B3113SingleStrikeUrshifu);
    printed.add_effect(CardEffect::NoAbilities, 1);
    let game = get_test_game_with_board(
        vec![synthetic, printed],
        vec![PlayedCard::from_id(CardId::A1053Squirtle)],
    );
    let state = game.get_state_clone();
    assert_eq!(
        state.pokemon_energy_types(state.in_play_pokemon[0][0].as_ref().unwrap()),
        vec![EnergyType::Darkness, EnergyType::Water]
    );
    assert_eq!(
        state.pokemon_energy_types(state.in_play_pokemon[0][1].as_ref().unwrap()),
        vec![EnergyType::Darkness]
    );
}

// ---------------------------------------------------------------------------------------------
// Game level: Weakness reads the attacker's types through the chokepoint
// ---------------------------------------------------------------------------------------------

fn vine_whip_damage(attacker: Card, defender: CardId) -> u32 {
    let mut game = get_test_game_with_board(
        vec![PlayedCard::from_card(&attacker)
            .with_energy(vec![EnergyType::Grass, EnergyType::Grass])],
        vec![PlayedCard::from_id(defender)],
    );
    let hp_before = game.get_state_clone().get_active(1).get_remaining_hp();
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(CardId::A1001Bulbasaur, 0),
        is_stack: false,
    });
    let hp_after = game.get_state_clone().get_active(1).get_remaining_hp();
    assert!(hp_after > 0, "the defender must survive so damage is exact");
    hp_before - hp_after
}

/// Mega Ampharos ex (B1 085) is weak to [F]. Bulbasaur is printed [G], so Vine Whip (40) hits for
/// 60 only if the synthetic card's SECOND printed type, [F], counts.
#[test]
fn second_printed_type_triggers_weakness() {
    assert_eq!(
        vine_whip_damage(
            dual_type_card(CardId::A1001Bulbasaur, EnergyType::Fighting),
            CardId::B1085MegaAmpharosEx
        ),
        60
    );
}

/// Control: the real single-type Bulbasaur hits Mega Ampharos ex for plain damage.
#[test]
fn single_type_attacker_does_not_trigger_weakness() {
    assert_eq!(
        vine_whip_damage(
            get_card_by_enum(CardId::A1001Bulbasaur),
            CardId::B1085MegaAmpharosEx
        ),
        40
    );
}

/// NEGATIVE: a [G]/[F] card is not [W]; Mega Charizard Y ex (B1a 014) is weak to [W].
#[test]
fn dual_type_attacker_is_not_a_third_type() {
    assert_eq!(
        vine_whip_damage(
            dual_type_card(CardId::A1001Bulbasaur, EnergyType::Fighting),
            CardId::B1a014MegaCharizardYEx
        ),
        40
    );
}
