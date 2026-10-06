//! The no-effect rule (Oct 6, quiz 4, item 2; Fable via Dustin; rl/results/playout_quiz4_items_2026-10-06/README.md):
//! whether an action's printed effect can do anything now, read from the card's text in the card database, never from a
//! list of names. Off by default (`_noeffect`); it is a within-noise tie-break at kx<N>'s own decision, the Tool
//! tie-break's shape: nothing leaves the pool.
//!
//! The reader splits a Trainer's or Ability's text into sentences and reads what each needs in order to do something:
//! - a heal needs a Pokémon in its reach with damage ("heal 20 damage from your Active Pokémon"), and a "recovers"
//!   clause one with a Special Condition;
//! - "put a random X from your deck into your hand" needs an X left in the deck (the deck's contents are the player's
//!   own knowledge), "... from your discard pile" one there;
//! - "during this turn, attacks used by your X do +N" (and costs, and "during your opponent's next turn, all of your X
//!   take -N") needs an X in play; "the Retreat Cost of your Active Pokémon is N less" a Retreat Cost to lower; a
//!   promise about your X (Hala's, Iris's) an X in play, Drayden's a Pokémon with Draco Meteor;
//! - discarding or returning the Tools in play (Guzma, Elesa) needs a Tool there;
//! - "take a [X] Energy from your Energy Zone and attach it to Y" and "choose 1 of your Y" need a Y in play;
//! - moving Energy from the Bench needs Benched Energy (of the type); discarding the opponent's Active's Energy needs
//!   some there; switching the opponent's Pokémon needs a Benched one (Basic, damaged, as the text says); switching your
//!   own needs a Bench;
//! - a draw needs a deck; "draw until N cards" a hand below N.
//! Sentences that always do something (damage, a Special Condition, looking, revealing, shuffling a hand) make the card
//! always effective; coin flips, usage conditions ("you can use this card only if", which the engine enforces) and
//! dependent clauses ("if you do", "if you healed any damage in this way") need nothing of their own. A sentence the
//! reader doesn't know makes the whole text unread, and an unread text never counts as doing nothing.
//!
//! Needs are alternatives: a text does something if any of its needs is met (so a text whose clauses must all hold, a
//! target and an Energy in the discard pile, counts as doing something when either holds: never a false "nothing").
//! A Tool card played (not its placement, which the Tool rule reads) does nothing when no Pokémon in play could ever
//! hold it with an effect (playout_tools.rs).
use crate::actions::{Action, SimpleAction};
use crate::hooks::is_ultra_beast;
use crate::models::{Card, EnergyType, PlayedCard, TrainerType};
use crate::State;

use super::playout_tools::{conditions_hold, tool_conditions};

/// What a Pokémon must be for a text to act on it.
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct PokemonFilter {
    /// Any of these names (lowercase); empty: any name.
    pub names: Vec<String>,
    /// The name contains this (lowercase), e.g. "team rocket".
    pub name_contains: Option<String>,
    pub energy: Option<EnergyType>,
    pub stage: Option<u8>,
    pub ex: bool,
    pub mega: bool,
    pub ultra_beast: bool,
    pub evolves_from: Option<String>,
    /// Some(None): with any Energy attached; Some(Some(t)): with that type attached.
    pub energy_attached: Option<Option<EnergyType>>,
    pub max_hp: Option<u32>,
    pub damaged: bool,
    pub min_retreat: Option<usize>,
    /// Has the attack of this name (lowercase), e.g. Drayden's "draco meteor".
    pub attack: Option<String>,
}

/// What a card must be.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CardKind {
    Pokemon(PokemonFilter),
    Item,
    Tool,
    Stadium,
    Supporter,
    /// Any card with one of these names (lowercase).
    Named(Vec<String>),
}

/// Where the Pokémon may be.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Scope {
    Active,
    Bench,
    Any,
    /// The Pokémon whose Ability it is.
    This,
}

/// One thing a text needs in order to do something now.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Need {
    /// A Pokémon of yours in reach, matching, with damage.
    Damaged(Scope, PokemonFilter),
    /// A Pokémon of yours in reach, matching, with a Special Condition.
    Condition(Scope, PokemonFilter),
    /// A Pokémon of yours in reach, matching.
    InPlay(Scope, PokemonFilter),
    InDeck(CardKind),
    InDiscard(CardKind),
    DeckNotEmpty,
    /// Fewer than this many cards in hand, and a deck to draw from.
    HandBelow(usize),
    /// The opponent's Active has Energy (of the type).
    OpponentActiveEnergy(Option<EnergyType>),
    /// A Benched Pokémon of yours has Energy (of the type), and your Active matches the filter.
    BenchedEnergy(Option<EnergyType>, PokemonFilter),
    /// The opponent has a Benched Pokémon that matches.
    OpponentBench(PokemonFilter),
    /// You have a Benched Pokémon, and your Active matches the filter.
    OwnSwitch(PokemonFilter),
    /// The opponent's Active has a Pokémon Tool attached.
    OpponentActiveTool,
    /// A Pokémon in play holds a Pokémon Tool: one of yours (`yours`), or of the opponent's (`theirs`).
    ToolsInPlay { yours: bool, theirs: bool },
    /// The opponent holds more than this many cards.
    OpponentHandAbove(usize),
    /// A card of this kind in the opponent's discard pile.
    InOpponentDiscard(CardKind),
}

/// What a text needs in order to do something.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Reading {
    /// Something always happens when it is used.
    Always,
    /// Something happens only if one of these is met.
    Needs(Vec<Need>),
}

pub(crate) fn energy_symbol(s: &str) -> Option<EnergyType> {
    Some(match s {
        "[g]" => EnergyType::Grass,
        "[r]" => EnergyType::Fire,
        "[w]" => EnergyType::Water,
        "[l]" => EnergyType::Lightning,
        "[p]" => EnergyType::Psychic,
        "[f]" => EnergyType::Fighting,
        "[d]" => EnergyType::Darkness,
        "[m]" => EnergyType::Metal,
        "[c]" => EnergyType::Colorless,
        "[n]" => EnergyType::Dragon,
        _ => return None,
    })
}

/// "Ninetales, Rapidash, or Magmar" -> the names.
fn names(list: &str) -> Vec<String> {
    list.replace(", or ", ", ").replace(", and ", ", ").replace(" or ", ", ").replace(" and ", ", ")
        .split(", ")
        .map(|n| n.trim().to_string())
        .filter(|n| !n.is_empty())
        .collect()
}

/// A phrase naming Pokémon: "[g] pokémon", "basic pokémon with 50 hp or less", "stage 2 pokémon", "pokémon ex",
/// "mega evolution pokémon ex", "ultra beasts", "pokémon that evolve from eevee", "pokémon that has any [w] energy
/// attached", "pokémon that has damage on it", or a list of names.
fn pokemon_filter(phrase: &str) -> Result<PokemonFilter, String> {
    let mut f = PokemonFilter::default();
    let mut p = phrase.trim().trim_end_matches('.').replace(" in play", "");
    for (suffix, set) in [
        (" that has damage on it", 0),
        (" that have damage on them", 0),
    ] {
        if let Some(stripped) = p.strip_suffix(suffix) {
            let _ = set;
            f.damaged = true;
            p = stripped.to_string();
        }
    }
    if let Some(i) = p.find(" that has 2 or more ") {
        // "that has 2 or more [p] energy attached": read as having that type attached (a weaker need, never a false
        // "nothing").
        let rest = &p[i + " that has 2 or more ".len()..];
        f.energy_attached = Some(energy_symbol(rest.split_whitespace().next().unwrap_or("")));
        p = p[..i].to_string();
    }
    if let Some(i) = p.find(" that has any ") {
        let rest = &p[i + " that has any ".len()..];
        let e = rest.split_whitespace().next().unwrap_or("");
        f.energy_attached = Some(energy_symbol(e));
        if energy_symbol(e).is_none() && e != "energy" {
            return Err(format!("energy attached '{rest}'"));
        }
        p = p[..i].to_string();
    }
    for marker in [" that evolve from ", " that evolves from "] {
        if let Some(i) = p.find(marker) {
            f.evolves_from = Some(p[i + marker.len()..].trim().to_string());
            p = p[..i].to_string();
        }
    }
    if let Some(i) = p.find(" with a maximum hp of ") {
        let rest = &p[i + " with a maximum hp of ".len()..];
        f.max_hp = Some(rest.split_whitespace().next().and_then(|n| n.parse().ok()).ok_or_else(|| format!("'{rest}'"))?);
        p = p[..i].to_string();
    }
    if let Some(i) = p.find(" with ") {
        let rest = &p[i + 6..];
        let n = rest.split_whitespace().next().and_then(|n| n.parse::<u32>().ok());
        match (n, rest.contains("hp or less")) {
            (Some(n), true) => f.max_hp = Some(n),
            _ => return Err(format!("'with {rest}'")),
        }
        p = p[..i].to_string();
    }
    let words: Vec<&str> = p.split_whitespace().collect();
    if words.is_empty() {
        return Err("no Pokémon named".into());
    }
    // The noun at the end: "pokémon", "pokémon ex", "ultra beasts"; else names.
    let noun_at = words.iter().rposition(|w| *w == "pokémon" || *w == "beast" || *w == "beasts");
    match noun_at {
        Some(at) => {
            if words[at].starts_with("beast") {
                if at == 0 || words[at - 1] != "ultra" {
                    return Err(format!("'{p}'"));
                }
                f.ultra_beast = true;
            }
            let tail = &words[at + 1..];
            if tail == ["ex"] {
                f.ex = true;
            } else if !tail.is_empty() {
                return Err(format!("'{p}'"));
            }
            let mut k = 0;
            let quals = &words[..if f.ultra_beast { at - 1 } else { at }];
            while k < quals.len() {
                match quals[k] {
                    "basic" => f.stage = Some(0),
                    "stage" => {
                        f.stage = Some(quals.get(k + 1).and_then(|n| n.parse().ok()).ok_or("a stage without a number")?);
                        k += 1;
                    }
                    "mega" if quals.get(k + 1) == Some(&"evolution") => {
                        f.mega = true;
                        k += 1;
                    }
                    "active" | "benched" => {}
                    w => match energy_symbol(w) {
                        Some(e) => f.energy = Some(e),
                        None => return Err(format!("unknown qualifier '{w}' in '{p}'")),
                    },
                }
                k += 1;
            }
        }
        None => {
            if p.contains('[') || p.contains("card") {
                return Err(format!("'{p}'"));
            }
            f.names = names(&p);
        }
    }
    Ok(f)
}

/// "basic [g] pokémon", "item card", "pokémon tool card", "stadium card", "mega evolution pokémon ex",
/// "glameow, stunky, or croagunk", "pokémon that has “team rocket” in its name".
fn card_kind(phrase: &str) -> Result<CardKind, String> {
    let p = phrase.trim();
    Ok(match p {
        "item card" | "item cards" => CardKind::Item,
        "pokémon tool card" | "pokémon tool cards" => CardKind::Tool,
        "stadium card" => CardKind::Stadium,
        "supporter card" => CardKind::Supporter,
        _ if p.starts_with("pokémon that has “") && p.ends_with("” in its name") => {
            let inner = &p["pokémon that has “".len()..p.len() - "” in its name".len()];
            CardKind::Pokemon(PokemonFilter { name_contains: Some(inner.to_string()), ..Default::default() })
        }
        _ if p.starts_with("cards from among ") => CardKind::Named(names(&p["cards from among ".len()..])),
        _ => CardKind::Pokemon(pokemon_filter(p)?),
    })
}

/// The Pokémon a phrase points at: "your active pokémon", "your active [g] pokémon", "1 of your X", "each of your X",
/// "your benched X", "this pokémon", "the [p] pokémon in the active spot", "your X in the active spot", or names.
fn target(phrase: &str) -> Result<(Scope, PokemonFilter), String> {
    let p = phrase.trim().trim_end_matches('.').trim_start_matches("to ").trim();
    if matches!(p, "this pokémon" | "it" | "that pokémon" | "this card") {
        return Ok((Scope::This, PokemonFilter::default()));
    }
    if let Some(rest) = p.strip_prefix("your active ") {
        return Ok((Scope::Active, pokemon_filter(rest)?));
    }
    for prefix in ["the ", "your "] {
        if let Some(rest) = p.strip_prefix(prefix) {
            if let Some(x) = rest.strip_suffix(" in the active spot") {
                return Ok((Scope::Active, pokemon_filter(x)?));
            }
        }
    }
    for prefix in ["1 of your benched ", "your benched ", "each of your benched "] {
        if let Some(rest) = p.strip_prefix(prefix) {
            return Ok((Scope::Bench, pokemon_filter(rest)?));
        }
    }
    for prefix in ["1 of your ", "each of your ", "your ", "2 of your "] {
        if let Some(rest) = p.strip_prefix(prefix) {
            let rest = rest.trim_end_matches(" in play");
            return Ok((Scope::Any, pokemon_filter(rest)?));
        }
    }
    Ok((Scope::Any, pokemon_filter(p)?))
}

/// What one sentence (lowercase) does: Ok(None) if it needs nothing of its own (a coin flip, a usage condition, a
/// dependent clause), Ok(Some(Always)) if it always does something, Ok(Some(Needs)) otherwise.
fn sentence(s: &str) -> Result<Option<Reading>, String> {
    let s = s.trim().trim_end_matches('.').trim();
    if s.is_empty() {
        return Ok(None);
    }
    // Preambles: the engine enforces when an Ability or a Stadium can be used.
    for pre in [
        "once during your turn, ",
        "once during each player's turn, ",
        "as often as you like during your turn, ",
        "if this pokémon is in the active spot, ",
        "if this pokémon is on your bench, ",
        "if you have arceus or arceus ex in play, ",
        "if this pokémon has a pokémon tool attached, ",
        "when you play this pokémon from your hand to evolve 1 of your pokémon, ",
        "when you put this pokémon from your hand onto your bench, ",
        "at the beginning of your turn, if this pokémon is in the active spot, ",
        "choose 1:",
        "you may ",
        "that player may ",
        "during your turn, ",
    ] {
        if let Some(rest) = s.strip_prefix(pre) {
            return sentence(rest);
        }
    }
    if s.contains("in order to use this ability") {
        return Ok(None);
    }
    for neutral in [
        "flip a coin",
        "flip 2 coins",
        "flip 3 coins",
        "you can use this card only if",
        "your turn ends",
        "if you use this ability, your turn ends",
        "(your opponent chooses",
        "choose either player",
        "use this ability",
        "for each pokémon you put into your hand in this way",
        "if you do,",
        "if you healed any damage in this way",
        "if heads, put this lucky ice pop",
        "you must discard a card from your hand in order to use this ability",
        "you can't use this card during your first turn",
        "you can't use more than",
        "if you can't shuffle in 2 cards, you can't use this card",
    ] {
        if s.starts_with(neutral) {
            return Ok(None);
        }
    }
    // Coin outcomes: what happens on heads is what the card can do.
    for pre in ["if heads, ", "for each heads, ", "if tails, ", "if all of them are heads, ", "if both of them are heads, "] {
        if let Some(rest) = s.strip_prefix(pre) {
            return sentence(rest);
        }
    }
    if let Some(i) = s.find(". if heads, ") {
        return sentence(&s[i + 2..]);
    }
    if s.starts_with("flip a coin until you get tails. ") {
        return sentence(&s["flip a coin until you get tails. ".len()..]);
    }
    // The player of a Stadium is "that player" / "they".
    let s = s
        .replace("that player puts", "put")
        .replace("that player ", "")
        .replace(" their deck", " your deck")
        .replace(" their hand", " your hand")
        .replace("they draw", "draw");
    let s = s.as_str();
    let needs = |n: Vec<Need>| Ok(Some(Reading::Needs(n)));

    // Heals.
    if let Some(i) = s.find(" damage from ") {
        if s.starts_with("heal ") || s.contains(" heal ") {
            let mut rest = s[i + " damage from ".len()..].to_string();
            let mut cond = false;
            for tail in [", and it recovers from all special conditions", " and it recovers from being asleep, paralyzed, and confused"] {
                if let Some(r) = rest.strip_suffix(tail) {
                    rest = r.to_string();
                    cond = true;
                }
            }
            if let Some(j) = rest.find(". ") {
                rest.truncate(j);
            }
            // "heal 10 damage and remove a random special condition from your active pokémon"
            let (scope, filter) = target(&rest)?;
            let mut n = vec![Need::Damaged(scope, filter.clone())];
            if cond {
                n.push(Need::Condition(scope, filter));
            }
            return needs(n);
        }
    }
    if let Some(rest) = s.strip_prefix("heal 10 damage and remove a random special condition from ") {
        let (scope, filter) = target(rest)?;
        return needs(vec![Need::Damaged(scope, filter.clone()), Need::Condition(scope, filter)]);
    }
    if let Some(rest) = s.strip_prefix("remove a random special condition from ") {
        let (scope, filter) = target(rest)?;
        return needs(vec![Need::Condition(scope, filter)]);
    }
    if let Some(rest) = s.strip_prefix("heal all damage from ") {
        let rest = rest.split(". ").next().unwrap_or(rest);
        let (scope, filter) = target(rest)?;
        return needs(vec![Need::Damaged(scope, filter)]);
    }
    // Searches.
    if let Some(i) = s.find(" from your deck into your hand") {
        let head = &s[..i];
        let what = head
            .strip_prefix("put ")
            .map(|h| h.trim_start_matches(|c: char| c.is_ascii_digit() || c == ' ').trim_start_matches("a ").trim_start_matches("an ").trim_start_matches("1 "))
            .map(|h| h.trim_start_matches("random "))
            .ok_or_else(|| format!("a search '{s}'"))?;
        let what = what.trim_start_matches("random ");
        let what = what.split(", except ").next().unwrap_or(what);
        return needs(vec![Need::InDeck(card_kind(what)?)]);
    }
    if s.starts_with("put a random item card") && s.contains("from your opponent's discard pile into your hand") {
        return needs(vec![Need::InOpponentDiscard(CardKind::Item)]);
    }
    if let Some(i) = s.find(" from your discard pile into your hand") {
        let head = &s[..i];
        let what = head
            .strip_prefix("put ")
            .map(|h| h.trim_start_matches(|c: char| c.is_ascii_digit() || c == ' ').trim_start_matches("a ").trim_start_matches("1 "))
            .map(|h| h.trim_start_matches("random "))
            .ok_or_else(|| format!("a discard search '{s}'"))?;
        return needs(vec![Need::InDiscard(card_kind(what)?)]);
    }
    if let Some(rest) = s.strip_prefix("a [w] pokémon is chosen at random from your discard pile") {
        let _ = rest;
        return needs(vec![Need::InDiscard(CardKind::Pokemon(PokemonFilter { energy: Some(EnergyType::Water), ..Default::default() }))]);
    }
    if s.contains("switch it with a random pokémon tool card in your deck") {
        return needs(vec![Need::InDeck(CardKind::Tool)]);
    }
    // Modifiers for this turn or the opponent's next.
    for pre in ["during this turn, attacks used by your ", "attacks used by your "] {
        if let Some(rest) = s.strip_prefix(pre) {
            let who = rest.split(" do +").next().unwrap().split(" cost ").next().unwrap();
            if who == rest {
                return Err(format!("a modifier '{s}'"));
            }
            let (_, filter) = target(who)?;
            return needs(vec![Need::InPlay(Scope::Any, filter)]);
        }
    }
    if let Some(rest) = s.strip_prefix("during your opponent's next turn, all of your ") {
        let who = rest.split(" take -").next().unwrap();
        if who == rest {
            return Err(format!("a modifier '{s}'"));
        }
        let (_, filter) = target(who)?;
        return needs(vec![Need::InPlay(Scope::Any, filter)]);
    }
    if s.starts_with("during this turn, the retreat cost of your active pokémon is ") {
        return needs(vec![Need::InPlay(Scope::Active, PokemonFilter { min_retreat: Some(1), ..Default::default() })]);
    }
    // Draws.
    if let Some(i) = s.find("draws cards until they have ").or_else(|| s.find("draw cards until you have ")) {
        let rest = &s[i..];
        let n = rest.split_whitespace().find_map(|w| w.parse::<usize>().ok()).ok_or("a hand size")?;
        return needs(vec![Need::HandBelow(n)]);
    }
    if s.starts_with("draw ") || s.contains(". draw a card") {
        return needs(vec![Need::DeckNotEmpty]);
    }
    // Energy from the Energy Zone, and targets chosen.
    if let Some(i) = s.find(" from your energy zone and attach it to ") {
        let to = &s[i + " from your energy zone and attach it to ".len()..];
        let to = to.split(". ").next().unwrap_or(to);
        let (scope, filter) = target(to)?;
        return needs(vec![Need::InPlay(scope, filter)]);
    }
    if s.starts_with("choose 1 of your opponent's benched pokémon and move") {
        return needs(vec![Need::OpponentBench(PokemonFilter { energy_attached: Some(None), ..Default::default() })]);
    }
    if s.starts_with("your opponent discards cards from your hand until they have ") {
        let n = s.split_whitespace().find_map(|w| w.parse::<usize>().ok()).ok_or("a hand size")?;
        return needs(vec![Need::OpponentHandAbove(n)]);
    }
    if s.starts_with("move 30 damage that your active pokémon has on it") {
        return needs(vec![Need::Damaged(Scope::Active, PokemonFilter::default())]);
    }
    if s.starts_with("move a random energy from your opponent's active pokémon") {
        return needs(vec![Need::OpponentActiveEnergy(None)]);
    }
    if let Some(rest) = s.strip_prefix("choose 1 of your ") {
        let who = rest.split(", and ").next().unwrap();
        let who = who.split(" that has damage on it").next().unwrap();
        let (_, filter) = target(&format!("1 of your {who}"))?;
        return needs(vec![Need::InPlay(Scope::Any, filter)]);
    }
    // Moving Energy from the Bench to the Active.
    if s.starts_with("move all [d] energy from each of your pokémon") {
        return Ok(Some(Reading::Always));
    }
    if let Some(rest) = s.strip_prefix("move ") {
        if let Some(j) = rest.find(" energy from ") {
            let kind = rest[..j].split_whitespace().last().and_then(energy_symbol);
            let after = &rest[j + " energy from ".len()..];
            if let Some(k) = after.find(" to ") {
                let from = &after[..k];
                if from.contains("benched") || from.contains("bench") {
                    let (scope, filter) = target(&after[k + 4..])?;
                    if scope != Scope::Active {
                        return Err(format!("a move to '{}'", &after[k + 4..]));
                    }
                    return needs(vec![Need::BenchedEnergy(kind, filter)]);
                }
            }
        }
        return Err(format!("a move '{s}'"));
    }
    // The opponent's Active's Energy.
    for pre in ["discard a ", "discard a random ", "discard 2 random ", "discard "] {
        if let Some(rest) = s.strip_prefix(pre) {
            if let Some(x) = rest.strip_suffix(" energy from your opponent's active pokémon") {
                let x = x.trim_start_matches("random ").trim();
                return needs(vec![Need::OpponentActiveEnergy(if x.is_empty() { None } else { energy_symbol(x) })]);
            }
        }
    }
    if s == "discard a random energy from your opponent's active pokémon" || s.ends_with("discard a random energy from your opponent's active pokémon") {
        return needs(vec![Need::OpponentActiveEnergy(None)]);
    }
    // Switching.
    if let Some(rest) = s.strip_prefix("switch out your opponent's active ") {
        let basic = rest.starts_with("basic ");
        return needs(vec![Need::OpponentBench(PokemonFilter { stage: basic.then_some(0), ..Default::default() })]);
    }
    if let Some(rest) = s.strip_prefix("switch in 1 of your opponent's benched ") {
        let mut f = PokemonFilter::default();
        f.stage = rest.starts_with("basic ").then_some(0);
        f.damaged = rest.contains("that has damage on it");
        return needs(vec![Need::OpponentBench(f)]);
    }
    if let Some(rest) = s.strip_prefix("switch your active ") {
        let who = rest.split(" with 1 of your benched").next().unwrap();
        let mut f = pokemon_filter(who.trim_end_matches(" that has damage on it"))?;
        f.damaged = who.ends_with("that has damage on it");
        return needs(vec![Need::OwnSwitch(f)]);
    }
    if s.starts_with("discard all pokémon tools from your opponent's active pokémon") {
        return needs(vec![Need::OpponentActiveTool]);
    }
    // Tools in play, and the Pokémon a turn's promise is about (Supporters the engine offers whatever the board).
    if s.starts_with("discard all pokémon tool cards attached to each of your opponent's pokémon") {
        return needs(vec![Need::ToolsInPlay { yours: false, theirs: true }]);
    }
    if s.starts_with("return all pokémon tools attached to each pokémon") {
        let both = s.contains("(both yours and your opponent's)");
        return needs(vec![Need::ToolsInPlay { yours: both, theirs: true }]);
    }
    if let Some(rest) = s.strip_prefix("during your opponent's next turn, if your ") {
        let who = rest.split(" would ").next().unwrap();
        if who == rest {
            return Err(format!("a promise '{s}'"));
        }
        return needs(vec![Need::InPlay(Scope::Any, pokemon_filter(who)?)]);
    }
    if s.starts_with("during this turn, if your opponent's active pokémon is knocked out") {
        let who = s.split(" an attack used by your ").nth(1).and_then(|r| r.split(',').next()).ok_or_else(|| format!("a promise '{s}'"))?;
        return needs(vec![Need::InPlay(Scope::Any, pokemon_filter(who)?)]);
    }
    if s.starts_with("during this turn, 1 of your opponent's pokémon is chosen") {
        let title = s.split(" for the ").nth(1).and_then(|r| r.split(" attack used by your").next()).ok_or_else(|| format!("a promise '{s}'"))?;
        let f = PokemonFilter { attack: Some(title.to_string()), ..Default::default() };
        return needs(vec![Need::InPlay(Scope::Any, f)]);
    }
    // Always something.
    for always in [
        "if you have a stage 2 card in your hand",
        "have your opponent shuffle",
        "discard a random energy from among the energy attached",
        "after you flip any coins",
        "when you flip any coins",
        "prevent all damage",
        "discard the energy that has been generated in their energy zone",
        "for each of your ",
        "switch it with your active pokémon",
        "move all [d] energy from each of your pokémon",
        "do ",
        "your opponent's active pokémon is now",
        "make your opponent's active pokémon",
        "look at",
        "your opponent reveals",
        "have your opponent reveal",
        "shuffle your hand into your deck",
        "each player shuffles",
        "your opponent shuffles",
        "your opponent discards cards from their hand",
        "a card from among both player's hands",
        "the next time you flip any number of coins",
        "use the effect of that card",
        "put your ",
        "put 1 of your ",
        "shuffle 1 of your ",
        "discard the top card of your opponent's deck",
        "discard the energy that has been generated in your energy zone",
        "attach ",
        "until the end of your opponent's next turn",
        "put a basic pokémon from your opponent's discard pile",
        "1 special condition from among",
        "shuffle a basic pokémon from your hand into your deck",
        "shuffle 2 cards from your hand into your deck",
        "choose a pokémon in your hand and switch it with a random pokémon in your deck",
        "discard a pokémon tool card from a pokémon",
        "put a random card from your deck that evolves from",
        "put a random [g] pokémon from your deck that evolves from",
        "put a random [w] pokémon from your deck that evolves from",
    ] {
        if s.starts_with(always) {
            return Ok(Some(Reading::Always));
        }
    }
    Err(format!("unread: '{s}'"))
}

/// What a card text needs in order to do something now (`Err`: a sentence this reader can't read).
pub fn effect_needs(text: &str) -> Result<Reading, String> {
    let lower = text.to_lowercase().replace(".(", ". (");
    // Sentences: a period followed by a capital-less start in the lowercased text ("...in play.Switch in ..." too).
    let mut sentences: Vec<String> = Vec::new();
    let mut cur = String::new();
    let chars: Vec<char> = lower.chars().collect();
    for (i, &c) in chars.iter().enumerate() {
        cur.push(c);
        let end = c == '.' && (i + 1 == chars.len() || chars[i + 1] == ' ' || chars[i + 1].is_alphabetic() || chars[i + 1] == '(');
        if end {
            sentences.push(cur.trim().to_string());
            cur.clear();
        }
    }
    if !cur.trim().is_empty() {
        sentences.push(cur.trim().to_string());
    }
    let mut all: Vec<Need> = Vec::new();
    let mut read_any = false;
    let mut skip_next = false;
    for (k, sen) in sentences.iter().enumerate() {
        if skip_next {
            skip_next = false;
            continue;
        }
        // "flip a coin. if heads, ..." and "flip a coin until you get tails. for each heads, ..." read their second part.
        let joined;
        let sen = if (sen.starts_with("flip ") || sen.starts_with("choose 1 of your ")) && k + 1 < sentences.len() && sentences[k + 1].starts_with("if heads") {
            joined = sentences[k + 1].clone();
            skip_next = true;
            joined.as_str()
        } else {
            sen.as_str()
        };
        match sentence(sen)? {
            None => {}
            Some(Reading::Always) => return Ok(Reading::Always),
            Some(Reading::Needs(n)) => {
                read_any = true;
                all.extend(n);
            }
        }
    }
    if !read_any {
        return Err("no effect sentence read".into());
    }
    Ok(Reading::Needs(all))
}

fn pokemon_matches(f: &PokemonFilter, p: &PlayedCard) -> bool {
    let Card::Pokemon(pc) = &p.card else { return false };
    let name = pc.name.to_lowercase();
    (f.names.is_empty() || f.names.iter().any(|n| *n == name))
        && f.name_contains.as_ref().map_or(true, |s| name.contains(s.as_str()))
        && f.energy.map_or(true, |e| pc.energy_type == e)
        && f.stage.map_or(true, |s| pc.stage == s)
        && (!f.ex || name.ends_with(" ex"))
        && (!f.mega || (name.starts_with("mega ") && name.ends_with(" ex")))
        && (!f.ultra_beast || is_ultra_beast(&pc.name))
        && f.evolves_from.as_ref().map_or(true, |e| pc.evolves_from.as_ref().is_some_and(|x| x.to_lowercase() == *e))
        && match f.energy_attached {
            None => true,
            Some(None) => !p.attached_energy.is_empty(),
            Some(Some(t)) => p.attached_energy.contains(&t),
        }
        && f.max_hp.map_or(true, |h| pc.hp <= h)
        && (!f.damaged || p.is_damaged())
        && f.min_retreat.map_or(true, |n| pc.retreat_cost.len() >= n)
        && f.attack.as_ref().map_or(true, |t| pc.attacks.iter().any(|a| a.title.to_lowercase() == *t))
}

fn card_matches(k: &CardKind, c: &Card) -> bool {
    match (k, c) {
        (CardKind::Pokemon(f), Card::Pokemon(pc)) => {
            let name = pc.name.to_lowercase();
            (f.names.is_empty() || f.names.iter().any(|n| *n == name))
                && f.name_contains.as_ref().map_or(true, |s| name.contains(s.as_str()))
                && f.energy.map_or(true, |e| pc.energy_type == e)
                && f.stage.map_or(true, |s| pc.stage == s)
                && (!f.ex || name.ends_with(" ex"))
                && (!f.mega || (name.starts_with("mega ") && name.ends_with(" ex")))
                && (!f.ultra_beast || is_ultra_beast(&pc.name))
                && f.max_hp.map_or(true, |h| pc.hp <= h)
                && f.evolves_from.as_ref().map_or(true, |e| pc.evolves_from.as_ref().is_some_and(|x| x.to_lowercase() == *e))
                && f.attack.as_ref().map_or(true, |t| pc.attacks.iter().any(|a| a.title.to_lowercase() == *t))
        }
        (CardKind::Item, Card::Trainer(t)) => t.trainer_card_type == TrainerType::Item,
        (CardKind::Tool, Card::Trainer(t)) => t.trainer_card_type == TrainerType::Tool,
        (CardKind::Stadium, Card::Trainer(t)) => t.trainer_card_type == TrainerType::Stadium,
        (CardKind::Supporter, Card::Trainer(t)) => t.trainer_card_type == TrainerType::Supporter,
        (CardKind::Named(ns), c) => ns.iter().any(|n| *n == c.get_name().to_lowercase()),
        _ => false,
    }
}

/// Whether `need` is met for `me` (`this`: the Ability's Pokémon, if any; `own_deck`: the cards left in my deck, which I
/// know).
pub fn need_met(need: &Need, state: &State, me: usize, this: Option<usize>, own_deck: &[Card]) -> bool {
    let mine = |scope: Scope| -> Vec<&PlayedCard> {
        (0..4)
            .filter(|&i| match scope {
                Scope::Active => i == 0,
                Scope::Bench => i > 0,
                Scope::Any => true,
                Scope::This => Some(i) == this,
            })
            .filter_map(|i| state.in_play_pokemon[me][i].as_ref())
            .collect()
    };
    match need {
        Need::Damaged(s, f) => mine(*s).iter().any(|p| pokemon_matches(f, p) && p.is_damaged()),
        Need::Condition(s, f) => mine(*s).iter().any(|p| pokemon_matches(f, p) && p.has_status_condition()),
        Need::InPlay(s, f) => mine(*s).iter().any(|p| pokemon_matches(f, p)),
        Need::InDeck(k) => own_deck.iter().any(|c| card_matches(k, c)),
        Need::InDiscard(k) => state.discard_piles[me].iter().any(|c| card_matches(k, c)),
        Need::DeckNotEmpty => !own_deck.is_empty(),
        Need::HandBelow(n) => state.hands[me].len() < *n && !own_deck.is_empty(),
        Need::OpponentActiveEnergy(t) => state.in_play_pokemon[1 - me][0]
            .as_ref()
            .is_some_and(|p| t.map_or(!p.attached_energy.is_empty(), |t| p.attached_energy.contains(&t))),
        Need::BenchedEnergy(t, active) => {
            mine(Scope::Active).iter().any(|p| pokemon_matches(active, p))
                && mine(Scope::Bench).iter().any(|p| t.map_or(!p.attached_energy.is_empty(), |t| p.attached_energy.contains(&t)))
        }
        Need::OpponentBench(f) => (1..4).filter_map(|i| state.in_play_pokemon[1 - me][i].as_ref()).any(|p| pokemon_matches(f, p)),
        Need::OwnSwitch(active) => mine(Scope::Active).iter().any(|p| pokemon_matches(active, p)) && !mine(Scope::Bench).is_empty(),
        Need::OpponentActiveTool => state.in_play_pokemon[1 - me][0].as_ref().is_some_and(|p| !p.attached_tools.is_empty()),
        Need::ToolsInPlay { yours, theirs } => [(me, *yours), (1 - me, *theirs)]
            .iter()
            .filter(|(_, counts)| *counts)
            .any(|(side, _)| state.in_play_pokemon[*side].iter().flatten().any(|p| !p.attached_tools.is_empty())),
        Need::OpponentHandAbove(n) => state.hands[1 - me].len() > *n,
        Need::InOpponentDiscard(k) => state.discard_piles[1 - me].iter().any(|c| card_matches(k, c)),
    }
}

/// The card text an action would use: a Trainer played (Item, Supporter), an Ability used, the Stadium used. Placing a
/// Pokémon, playing a Stadium card, a Fossil, Energy, attacks, evolving, retreating and ending the turn have no such
/// text: they always do something.
fn action_text(state: &State, a: &Action) -> Option<(String, String, Option<usize>)> {
    match &a.action {
        SimpleAction::Play { trainer_card } if matches!(trainer_card.trainer_card_type, TrainerType::Item | TrainerType::Supporter) => {
            Some((trainer_card.name.clone(), trainer_card.effect.clone(), None))
        }
        SimpleAction::UseAbility { in_play_idx } => {
            let p = state.in_play_pokemon[a.actor][*in_play_idx].as_ref()?;
            let Card::Pokemon(pc) = &p.card else { return None };
            let ab = pc.ability.as_ref()?;
            Some((format!("{}'s {}", pc.name, ab.title), ab.effect.clone(), Some(*in_play_idx)))
        }
        SimpleAction::UseStadium => match &state.active_stadium {
            Some(Card::Trainer(t)) => Some((t.name.clone(), t.effect.clone(), None)),
            _ => None,
        },
        _ => None,
    }
}

/// Whether an action's printed effect can do something now: `Some(true)` it can, `Some(false)` it can't, `None` the text
/// isn't read (so it counts as doing something). Actions without a card text always do something (`Some(true)`).
pub fn effect_now(state: &State, a: &Action, own_deck: &[Card]) -> Option<bool> {
    if let SimpleAction::Play { trainer_card } = &a.action {
        if trainer_card.trainer_card_type == TrainerType::Tool {
            // A Tool played does nothing now if no Pokémon in play could hold it with an effect.
            let c = tool_conditions(&trainer_card.effect).ok()?;
            return Some((0..4).any(|i| state.in_play_pokemon[a.actor][i].as_ref().is_some_and(|p| conditions_hold(&c, p, i))));
        }
    }
    let Some((_, text, this)) = action_text(state, a) else { return Some(true) };
    match effect_needs(&text) {
        Ok(Reading::Always) => Some(true),
        Ok(Reading::Needs(needs)) => Some(needs.iter().any(|n| need_met(n, state, a.actor, this, own_deck))),
        Err(_) => None,
    }
}

/// The name of the card text an action would use, for traces and counts.
pub fn action_card(state: &State, a: &Action) -> Option<String> {
    if let SimpleAction::Play { trainer_card } = &a.action {
        return Some(trainer_card.name.clone());
    }
    action_text(state, a).map(|(n, _, _)| n)
}
