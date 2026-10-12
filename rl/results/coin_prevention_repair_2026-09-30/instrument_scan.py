"""Watch-only instrumentation of legality_scan for the coin-flip damage prevention repair (Sept 30; RUN5's switch
template; exact counters added for the rules switch's F5). It adds per-game counters to the --games-out line, changing no
play (they only read the state before each tick, the offered and chosen moves, and forecasts of the chosen move on clones;
nothing touches the game).

Move numbers. A tick is one `play_tick`, one chosen move, numbered from 0 as `coin_trace.rs` and `vs_trace.rs` print it, so a
counter's ticks compare directly with a first-difference trace. A counter read from the OFFERED moves fires at the tick where
they are offered; one read from the CHOSEN move fires at that tick. Every exact counter is recorded as
{"n": the number of ticks at which it fired, "first": the first such tick or null, "ticks": every such tick, ascending}, so a
reader can ask whether it fired in a given turn or at a given tick, not only whether it ever fired (the rules switch's F5,
second read). Everything is counted on the board, for the moves the game offered or chose, never for the bots' lookahead.

The five coin-Ability Pokemon are keyed by id (COIN ids: finite cut A2 114 Bastiodon and B3b 050 Hisuian Goodra; full
prevention A4 080 Togekiss and B2 124 / B2 204 Meowth). Ids, not mechanics: a reprint (B4b Meowth 180 / 352) is not seen
until the lists below are extended. That item is on the switch README's backlog for the B4b refresh.

EXACT (these count as reach, as the mechanic check uses them). Each is {"n": ticks, "first": first tick or null}:
- "coin_cut_recorded" (B a): a heads finite cut was recorded for a Bastiodon or Goodra taking damage. The chosen move is an
  Attack or an ApplyQueuedAttackDamage, and the engine's forecast of it has more branches than the forecast of the same
  move on a clone where that Pokemon is replaced by a plain Bulbasaur. Repair B splits a branch in two (heads, tails)
  exactly for a coin-Ability Pokemon that takes damage in it, and records the finite cut on the heads half; so more
  branches with it than without it is that split, read off the engine's own forecast (suppression, the ignore-effects
  attacks and zero damage are all the engine's own decisions).
- "coin_full_prevention": the same split for a full-prevention Pokemon (Togekiss, Meowth): an attack's own damage, or a
  queued ApplyQueuedAttackDamage, at it. This is what step 2's `retain` check needs (full prevention drops the damage entry).
- "coin_queued_offered" (B b, Chase Order and the later round's sites): the queued coin-path choice was offered: an ApplyQueuedAttackDamage at a
  coin-Ability Pokemon of the mover's opponent, whose attack's mechanic is not AlsoChoiceBenchDamage[Filtered] (that one
  already queued it on the old engine, for its opponent-Bench form, so it is not the repair's doing). Seen among the moves
  the tick OFFERED, so a choice the bot then declines still counts.
- "coin_queued_offered_any": the same without the id list (a reprint of a coin Ability card is seen). Every
  ApplyQueuedAttackDamage that is not AlsoChoiceBenchDamage[Filtered] comes from `queued_attack_damage_choice`'s coin branch
  (the only other builder, the players' own lookahead choice in expectiminimax_player.rs, is never an offered move), so
  an offered one is the repair's doing whoever the target is.
- "offgate_helper_choice": an off-gate queued choice of a rewritten helper: an ApplyDamage (is_from_active_attack)
  at the mover's opponent is offered, in the same turn as an Attack whose mechanic is one of the helpers B rewrote
  (DirectDamage, DirectDamageAndSelfCardEffect, DirectDamageIfDamaged, the discard-all-energy-of-a-type and the
  self-discard-energy then damage-any-opponent-Pokemon attacks, damage per target energy, switch-in-then-damage, and Chase
  Order without the discard; and the later round's (claude/coin-prevention-round2, Oct 1): Wellspring Dance, Tornado Shot,
  Double Splash and Triple Bombardment, Mischievous Ring, Litter and Mega Kangaskhan ex's second punch). A plain
  ApplyDamage has the same fields whoever built it, so the source is told by the mechanic of the last Attack the mover
  chose that turn (copied attacks included). Built by `queued_attack_damage_targets_choice`'s else branch, or returned
  unchanged by `coin_gated_choice` (the later round). It is the proof that the table runs those rewritten lines.
  "offgate_helper_by_mechanic" splits it by that mechanic: {mechanic name: [every tick]}, one entry per helper that fired.
- "offgate_discard_then_damage": the fall-through ApplyDamage of `discard_then_damage_choice` (Chase Order with the discard,
  and Gyarados's Wild Swing): an ApplyDamage (is_from_active_attack) offered at the very next tick after a
  DiscardOwnBenchedThenDamage move. It does not pass through `queued_attack_damage_choice`, so it is its own counter. It
  fires in table games: the t-vespiquen list (`decks/screen/opponents/t-vespiquen.txt`, 2 Vespiquen ex B4 011 and 2 Combee)
  takes Chase Order's discard 131 to 606 times in each 500-game row of kp3's table (`rl/results/chase_order_2026-09-25/
  kp3_vespiquen.txt`: "discarded 286 of 525 (Combee 47, Shuckle ex 185, ...)"), and `counter_probe.rs` shows the counter on a built board: 1 at the tick after the discard into a
  non-coin Active, 0 into a Meowth B2 124 Active, where the same damage is queued as ApplyQueuedAttackDamage and
  `coin_queued_offered` reads it. The coin smoke has no Vespiquen, so there it reads 0.
SUPERSET (kept to back "all counters 0 means identical"; never reach):
- "coin_defender_attack": attack moves (an Attack, or a queued ApplyDamage / ApplyQueuedAttackDamage from an attack) while
  the mover's opponent has a Pokemon with a coin-flip damage Ability in play. A superset of both gates.
- "coin_queued_attack_damage": CHOSEN ApplyQueuedAttackDamage moves with a target that has one of those Abilities. It reads 0
  where the repair changed the offered choice but the bot picked another (Sonnet's S3): use "coin_queued_offered".
THE ROUND-2 PACKAGE (claude/coin-prevention-round2: the later coin round, the card-text job and its follow-up; added for the
readiness jobs, Oct 2). The lines are R2_FNS below (`r2_tick` and its helpers), put into legality_scan.rs before `play_one`; the
probe `rl/results/round2_readiness_2026-10-02/counter_probe_readiness.rs` runs the same lines (`--emit-fns`) on constructed
boards. Every counter is {"n", "first", "ticks"} as above, or {key: [every tick]} for a keyed one, and is written 0 or not. Where a
counter compares forecasts, the board "without" is the same board with one Pokemon's printed Ability taken away (its card's
ability set to none), so nothing else moves, and the engine's own forecast decides the rest (suppression, damage, knockouts).
EXACT:
- "coin_queued_by_attack" {attack: ticks}: the queued coin-path choice offered, keyed by its attack (Wild Swing, Wellspring Dance,
  Tornado Shot, Double Splash, Triple Bombardment, Mischievous Ring, Litter, Double-Punching Family; Chase Order and the first
  round's helpers too). "coin_queued_offered_any" split by site.
- "coin_plain_damage_by_attack" {attack: ticks} and "coin_plain_damage_chosen": an attack's plain queued damage (ApplyDamage from
  an attack) offered / chosen whose forecast has more branches than with a target's coin Ability taken away, on either side
  (A4: the opponent's Active in an own-Bench choice, your own Pokemon in an own choice; A5: a copied discard attack; a copied
  Wild Swing or Litter). Keyed by the attack the mover chose last this turn.
- "perish_plain_hit_offered", "perish_plain_hit_chosen" (E2): the same for the defending Active's Perish Body.
- "coin_own_side_split" (A4): the chosen Attack or ApplyQueuedAttackDamage has more branches than with a coin Ability on the
  attacker's own side taken away (Earthquake on your own Benched Meowth).
- "guts_own_side_split" (E1): the same for Guts on the attacker's own side.
- "will_confused_attack" (item 1): a Confused attacker's own attack (no block coin) with Will pending, whose forecast has a branch
  that uses Will or leaves a Victory Star pause. The old engine did neither (Will lapsed; no pause with Will pending).
- "will_block_coin_attack" (A2): an attack with a block coin and Will pending, whose forecast has a branch that uses Will.
- "vs_block_coin_built" (A1): an attack with a block coin whose forecast leaves a Victory Star pause (the old engine never paused
  with a block coin). "vs_block_coin_choice_offered": Keep or Reroll offered while the chooser's Active has a block coin (the
  heads half, a move or more later).
- "trap_territory_offer_changed" (item 4): with two or more Ariados (Trap Territory) on one side, the moves offered to the other
  side differ from those on the same board with every Ariados but one taken away (the old count).
  "trap_territory_outcome_changed": the chosen move's forecast leaves a different board there (each in-play Pokemon's card, HP
  and Energy, and the discard piles): Grass Knot, a retreat's Energy, Heavy Helmet.
- "luxury_coin_opp_stadium" (the follow-up): UseStadium on the opponent's Stadium with Gholdengo (Luxury Coin) in the mover's
  play, whose forecast leaves no Luxury Coin pause while it leaves one with the Stadium made the mover's own.
- "fossil_item_lock" (the follow-up): at a main-phase choice (EndTurn offered) the mover holds a Fossil that its own builder
  offers (`trainer_move_generation_implementation`), NoItemCards is in force and NoTrainerCards isn't: the old move generation
  offered it.
- "attack_return_weakness" (P2, Oct 8): the chosen move runs the hit back (`handle_attack_retaliation`) on a damaged opposing
  Active that carries an attack's return damage (CardEffect::Counterattack: Cursed Jewel, Spike Armor, Bristling Spikes,
  Needle Lariat, Shell Trap), and its forecast leaves a different board with the Attacking Pokemon's printed Weakness taken
  away. The moves that run it: Attack, ApplyDamage from an attack into the opposing Active, ApplyQueuedAttackDamage,
  KeepAttackCoinResults and RerollAttackCoins (Victory Star), and ResolveAttackRetaliation (the held-back hit back; its
  defender is `damaged_refs`' first). Only forecast branches where the hit back has landed count: not one still paused for
  Victory Star, not one where the move left a new ResolveAttackRetaliation frame (that hit back is counted at the tick that
  resolves it; frames already on the stack before the move, such as the empty one under a "1 of your opponent's Pokemon"
  choice, don't count), and not one where the defender took no damage. Taking the Weakness away moves nothing else here: an attack's self-damage is a flat
  `apply_damage`. The old engine gave the hit back no Weakness, so it never fired.
OFF THE GATE (the rewritten lines ran and gave the old answer: the proof that a table runs them):
- "offgate_by_attack" {attack: ticks}: a plain choice (no coin-Ability target) offered after an attack whose queued damage the
  later round rewrote (R2_SITES: its seven sites, and the first round's helpers and Chase Order, whose constructor it rewrote).
  "offgate_helper_by_mechanic" and "offgate_discard_then_damage" by attack, Wild Swing apart from Chase Order.
- "offgate_plain_attack_damage": a chosen plain ApplyDamage from an attack with neither split (`forecast_apply_damage`'s old path).
- "offgate_guts_opponent_split": the opponent's Guts split in an attack's outcome, as before (E1 rewrote `split_with_guts_survival`).
- "offgate_confused_attack": a Confused attacker's attack without Will pending (the Confusion gate, as before).
- "offgate_block_coin_attack": an attack with a block coin, no Will pending and no Victory Star pause (the block coin, as before).
- "offgate_vs_ungated_built": a Victory Star pause with no gate coin (the rewritten staging, as before).
- "offgate_trap_territory_one": one Ariados in play against an Active (the rewritten loop adds 1, as before).
- "offgate_luxury_coin_offered": a Luxury Coin reroll offered (`luxury_coin_covers` let it through).
- "offgate_fossil_offered": a Fossil offered (the Item-lock check let it through).
- "offgate_return_by_source" {sources: ticks} (P2): every other such tick on a defender with a return-damage source, keyed by its
  sources joined with "+" ("attack", "Rocky Helmet", "Ability", "attack+Rocky Helmet", ...). A defender with no source is not
  counted. "attack" here means the hit back took no Weakness: the attacker isn't weak to the holder, it is Benched (U-turn), or
  it is Knocked Out either way.
The coin split on the attack's opponent side keeps the counters above ("coin_cut_recorded", "coin_full_prevention"); they are A4's
off-gate too.
SUPERSET: "trap_territory_two_in_play": two or more Ariados in play against an Active (the gate held: the Retreat Cost is one more
than before, whether or not anything reads it).
On this branch the Victory Star script's "vs_confusion_first_built" also fires when Will is pending or a block coin is there too (the
old engine built no pause then); "will_confused_attack" and "vs_block_coin_built" tell those apart. Victini's caveat text
(card_validation.rs) changes no play and has no counter.
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once;
it applies with the Victory Star repair's script in either order, and alone)
       python3 instrument_scan.py --emit-fns <file.rs>   (writes R2_FNS alone, for the probe's include!)"""
import sys
R2_FNS = r'''// ---- The round-2 package's counters (`instrument_scan.py`; the readiness jobs, the cloud, Oct 2). Watch-only: they read the
// state before a tick, the moves it offered and chose, and the engine's own forecasts on clones; nothing touches the game. The
// constructed-board probe (rl/results/round2_readiness_2026-10-02/counter_probe_readiness.rs) runs these same lines, written
// out by `instrument_scan.py --emit-fns`.

/// The attack mechanics whose queued damage the later coin round (Oct 1) rewrote: its seven sites (Wild Swing's
/// DiscardOwnBenchedTypeForDamage and the six after it), and the first round's helpers and Chase Order, whose constructor
/// (`queued_attack_damage_choice`) it rewrote to hand its target to `queued_attack_damage_targets_choice`.
const R2_SITES: [&str; 15] = ["DirectDamage", "DirectDamageAndSelfCardEffect", "DirectDamageIfDamaged",
    "SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon", "SelfDiscardEnergyThenDamageAnyOpponentPokemon",
    "DamageToAnyOpponentPerTargetEnergy", "SwitchInOpponentBenchedThenDamage", "OptionalDiscardBenchedBasicForExtraDamage",
    "DiscardOwnBenchedTypeForDamage", "CoinFlipAlsoChoiceBenchDamage", "SelfDiscardEnergyAndChoiceBenchDamage",
    "ConditionalBenchDamage", "ShuffleOpponentToolsIntoDeckBeforeDamage", "DiscardToolsFromHandForDamage",
    "MegaKangaskhanExDoublePunchingFamily"];

/// The printed Ability of an in-play Pokemon, as the engine's map names its mechanic ("" for none). Read from the card, so a
/// reprint is seen; whether the Ability works on this board (suppression) is left to the engine's forecasts below.
fn r2_ability(p: &PlayedCard) -> String {
    match &p.card {
        Card::Pokemon(c) => c
            .ability
            .as_ref()
            .and_then(|a| deckgym::actions::ability_mechanic_from_effect(&a.effect))
            .map(|m| format!("{m:?}"))
            .unwrap_or_default(),
        _ => String::new(),
    }
}

/// Carefree Steps, Celestial Blessing (full prevention), Guarded Grill and Securely Sheltered (a cut).
fn r2_is_coin(p: &PlayedCard) -> bool {
    let m = r2_ability(p);
    m == "CoinFlipToPreventDamage" || m.starts_with("CoinFlipToReduceDamage")
}

fn r2_mechanic(attack: &deckgym::models::Attack) -> String {
    attack
        .effect
        .as_deref()
        .and_then(|e| deckgym::actions::EFFECT_MECHANIC_MAP.get(e))
        .map(|m| format!("{m:?}").chars().take_while(|c| c.is_alphanumeric()).collect::<String>())
        .unwrap_or_default()
}

/// `state` with the printed Ability of the Pokemon at (player, idx) taken away, nothing else changed: a move's forecast on it
/// against the forecast on `state` shows what that Ability adds.
fn r2_strip(state: &State, player: usize, idx: usize) -> State {
    let mut s = state.clone();
    if let Some(p) = s.in_play_pokemon[player][idx].as_mut() {
        if let Card::Pokemon(c) = &mut p.card {
            c.ability = None;
        }
    }
    s
}

/// The number of branches of the engine's forecast of `action` (0 if it can't forecast it).
fn r2_count(state: &State, action: &Action) -> usize {
    deckgym::actions::try_forecast_action(state, action).map_or(0, |o| o.into_branches().0.len())
}

/// The engine's forecast of `action`: each branch's probability and the state it leaves, each applied to a clone of `state`
/// with the same seeded generator (as the Victory Star counters do). Empty if the engine can't forecast it.
fn r2_branches(state: &State, action: &Action) -> Vec<(f64, State)> {
    let Ok(outcomes) = deckgym::actions::try_forecast_action(state, action) else {
        return vec![];
    };
    let (probabilities, mutations) = outcomes.into_branches();
    probabilities
        .into_iter()
        .zip(mutations)
        .map(|(probability, mutate)| {
            let mut s = state.clone();
            mutate(&mut <rand::rngs::StdRng as rand::SeedableRng>::seed_from_u64(0), &mut s, action);
            (probability, s)
        })
        .collect()
}

fn r2_variant(v: &serde_json::Value) -> String {
    match v {
        serde_json::Value::String(s) => s.clone(),
        serde_json::Value::Object(o) => o.keys().next().cloned().unwrap_or_default(),
        _ => String::new(),
    }
}

/// The turn effects the engine keeps for `turn`, by name (read through serde: the field is private).
fn r2_turn_effects(state: &State, turn: u8) -> Vec<String> {
    let v = serde_json::to_value(state).unwrap_or_default();
    v["turn_effects"][turn.to_string()].as_array().map(|e| e.iter().map(r2_variant).collect()).unwrap_or_default()
}

/// Will's pending heads (TurnEffect::ForceFirstHeads) in `turn`.
fn r2_will(state: &State, turn: u8) -> bool {
    r2_turn_effects(state, turn).iter().any(|e| e == "ForceFirstHeads")
}

/// A block coin on the Pokemon (CardEffect::CoinFlipToBlockAttack: Smokescreen and the like), read through serde.
fn r2_has_block_coin(p: &PlayedCard) -> bool {
    serde_json::to_value(p)
        .ok()
        .and_then(|v| v["effects"].as_array().cloned())
        .unwrap_or_default()
        .iter()
        .any(|e| r2_variant(&e[0]) == "CoinFlipToBlockAttack")
}

/// What a Retreat Cost can change on the board: each in-play Pokemon's card, remaining HP and Energy, and both discard piles.
fn r2_board(s: &State) -> String {
    let mut out = String::new();
    for q in 0..2 {
        for slot in &s.in_play_pokemon[q] {
            out += &match slot {
                Some(p) => format!("{} {} {:?}; ", p.card.get_id(), p.get_remaining_hp(), p.attached_energy),
                None => "-; ".to_string(),
            };
        }
        out += &format!("discard {} {:?} | ", s.discard_piles[q].len(), s.discard_energies[q]);
    }
    out
}

/// The return damage an attack left on the Pokemon (CardEffect::Counterattack, summed), read through serde.
fn r2_attack_return(p: &PlayedCard) -> u32 {
    serde_json::to_value(p)
        .ok()
        .and_then(|v| v["effects"].as_array().cloned())
        .unwrap_or_default()
        .iter()
        .filter_map(|e| e[0]["Counterattack"]["amount"].as_u64())
        .sum::<u64>() as u32
}

/// `state` with the printed Weakness of the Pokemon at (player, idx) taken away, nothing else changed.
fn r2_strip_weakness(state: &State, player: usize, idx: usize) -> State {
    let mut s = state.clone();
    if let Some(p) = s.in_play_pokemon[player][idx].as_mut() {
        if let Card::Pokemon(c) = &mut p.card {
            c.weakness = None;
        }
    }
    s
}

/// The Pokemon's return-damage sources joined with "+": an attack's (P2 gives it Weakness), Rocky Helmet's (by text, so a
/// reprint counts) and an Ability's (both flat). "" for none.
fn r2_return_sources(p: &PlayedCard) -> String {
    let mut sources = Vec::new();
    if r2_attack_return(p) > 0 {
        sources.push("attack");
    }
    if deckgym::tools::has_tool(p, deckgym::card_ids::CardId::A2148RockyHelmet) {
        sources.push("Rocky Helmet");
    }
    if r2_ability(p).starts_with("CounterattackDamage") {
        sources.push("Ability");
    }
    sources.join("+")
}

/// One tick's firings: (counter, key), the key None for an unkeyed counter. `actions` are the moves the tick offered,
/// `chosen` the one played, and `last_attack` the attack the mover chose last in this turn before it (a copied one included).
fn r2_tick(
    before: &State,
    actions: &[Action],
    chosen: &Action,
    last_attack: Option<&deckgym::models::Attack>,
) -> Vec<(&'static str, Option<String>)> {
    let mut out: Vec<(&'static str, Option<String>)> = Vec::new();
    let actor = chosen.actor;
    let opp = 1 - actor;
    let turn = before.turn_count;
    let at = |q: usize, i: usize| before.in_play_pokemon[q].get(i).and_then(|p| p.as_ref());
    let last_title = last_attack.map(|a| a.title.clone()).unwrap_or_default();
    let last_mechanic = last_attack.map(r2_mechanic).unwrap_or_default();

    // The later coin round's sites. Exact: the queued coin-path choice offered, by attack (built only for a target with a coin
    // Ability). Off the gate: a plain choice offered after one of the rewritten attacks, with no coin-Ability target.
    for a in actions {
        match &a.action {
            SimpleAction::ApplyQueuedAttackDamage { attack, .. }
                if !r2_mechanic(attack).starts_with("AlsoChoiceBenchDamage") =>
            {
                out.push(("coin_queued_by_attack", Some(attack.title.clone())));
            }
            SimpleAction::ApplyDamage { is_from_active_attack: true, targets, .. }
                if R2_SITES.contains(&last_mechanic.as_str())
                    && targets.iter().any(|(_, q, _)| *q == opp)
                    && !targets.iter().any(|(d, q, i)| *d > 0 && at(*q, *i).is_some_and(r2_is_coin)) =>
            {
                out.push(("offgate_by_attack", Some(last_title.clone())));
            }
            _ => {}
        }
    }

    // The card-text job (A4, A5) and its follow-up (E2): an attack's plain queued damage (`forecast_apply_damage`). Exact: its
    // forecast has more branches than with a target's coin Ability (either side) or the defending Active's Perish Body taken
    // away. Off the gate: neither.
    let plain = |a: &Action| -> Option<(bool, bool)> {
        let SimpleAction::ApplyDamage { attacking_ref, targets, is_from_active_attack: true } = &a.action else {
            return None;
        };
        let defender = 1 - attacking_ref.0;
        let coins: Vec<(usize, usize)> = targets
            .iter()
            .filter(|(d, q, i)| *d > 0 && at(*q, *i).is_some_and(r2_is_coin))
            .map(|(_, q, i)| (*q, *i))
            .collect();
        let perish = targets.iter().any(|(d, q, i)| *d > 0 && *q == defender && *i == 0)
            && at(defender, 0).is_some_and(|p| r2_ability(p) == "CoinFlipToKnockOutAttackerOnKnockout");
        if coins.is_empty() && !perish {
            return Some((false, false));
        }
        let n = r2_count(before, a);
        Some((
            coins.iter().any(|&(q, i)| r2_count(&r2_strip(before, q, i), a) < n),
            perish && r2_count(&r2_strip(before, defender, 0), a) < n,
        ))
    };
    for a in actions {
        if let Some((coin, perish)) = plain(a) {
            if coin {
                out.push(("coin_plain_damage_by_attack", Some(last_title.clone())));
            }
            if perish {
                out.push(("perish_plain_hit_offered", None));
            }
        }
    }
    if let Some((coin, perish)) = plain(chosen) {
        if coin {
            out.push(("coin_plain_damage_chosen", None));
        }
        if perish {
            out.push(("perish_plain_hit_chosen", None));
        }
        if !coin && !perish {
            out.push(("offgate_plain_attack_damage", None));
        }
    }

    // An attack's own outcome (A4: the coin Abilities on the attacker's own Pokemon; E1: Guts on them). Exact: the chosen move's
    // forecast has more branches than with that own Pokemon's Ability taken away. Off the gate: the opponent's Guts split.
    if matches!(&chosen.action, SimpleAction::Attack(_) | SimpleAction::ApplyQueuedAttackDamage { .. }) {
        let guts = |p: &PlayedCard| r2_ability(p) == "CoinFlipToSurviveKnockOut";
        let slots = |q: usize, f: &dyn Fn(&PlayedCard) -> bool| (0..4).filter(|&i| at(q, i).is_some_and(|p| f(p))).collect::<Vec<usize>>();
        let (own_coin, own_guts, opp_guts) = (slots(actor, &r2_is_coin), slots(actor, &guts), slots(opp, &guts));
        if !(own_coin.is_empty() && own_guts.is_empty() && opp_guts.is_empty()) {
            let n = r2_count(before, chosen);
            let split = |q: usize, s: &[usize]| s.iter().any(|&i| r2_count(&r2_strip(before, q, i), chosen) < n);
            if split(actor, &own_coin) {
                out.push(("coin_own_side_split", None));
            }
            if split(actor, &own_guts) {
                out.push(("guts_own_side_split", None));
            }
            if split(opp, &opp_guts) {
                out.push(("offgate_guts_opponent_split", None));
            }
        }
    }

    // The gate coins (item 1: Will on a Confused attacker; A1: Victory Star after a block coin; A2: Will on a block coin), read off
    // the engine's forecast of the chosen attack: a branch that uses Will, or one that leaves a Victory Star pause.
    if let (SimpleAction::Attack(_), false) = (&chosen.action, chosen.is_stack) {
        if let Some(active) = at(actor, 0) {
            let (confused, block) = (active.is_confused(), r2_has_block_coin(active));
            let victini = !before.victory_star_used_this_turn[actor]
                && (0..4).any(|i| at(actor, i).is_some_and(|p| r2_ability(p) == "VictoryStar"));
            if confused || block || victini {
                let will = r2_will(before, turn);
                let branches = r2_branches(before, chosen);
                let paused = branches.iter().any(|(_, s)| s.pending_attack_coin_choice.is_some());
                let will_used = will && branches.iter().any(|(_, s)| !r2_will(s, turn));
                if confused && !block && will && (will_used || paused) {
                    out.push(("will_confused_attack", None));
                }
                if block && will && will_used {
                    out.push(("will_block_coin_attack", None));
                }
                if block && paused {
                    out.push(("vs_block_coin_built", None));
                }
                if confused && !will {
                    out.push(("offgate_confused_attack", None));
                }
                if block && !will && !paused {
                    out.push(("offgate_block_coin_attack", None));
                }
                if !confused && !block && paused {
                    out.push(("offgate_vs_ungated_built", None));
                }
            }
        }
    }
    if actions.iter().any(|a| matches!(a.action, SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. }))
        && at(actor, 0).is_some_and(r2_has_block_coin)
    {
        out.push(("vs_block_coin_choice_offered", None));
    }

    // Trap Territory (item 4): against the same board with every Ariados but one taken away (the old engine's count). Exact: the
    // moves offered to that player's opponent differ, or the chosen move's forecast leaves a different board.
    for p in 0..2usize {
        if at(1 - p, 0).is_none() {
            continue;
        }
        let traps: Vec<usize> =
            (0..4).filter(|&i| at(p, i).is_some_and(|x| r2_ability(x).starts_with("IncreaseRetreatCostForOpponentActive"))).collect();
        if traps.len() == 1 {
            out.push(("offgate_trap_territory_one", None));
        }
        if traps.len() < 2 {
            continue;
        }
        out.push(("trap_territory_two_in_play", None));
        let mut old = before.clone();
        for &i in &traps[1..] {
            old = r2_strip(&old, p, i);
        }
        if actor == 1 - p {
            let shown = |v: &[Action]| v.iter().map(|a| format!("{:?}", a.action)).collect::<Vec<_>>();
            if shown(&old.generate_possible_actions().1) != shown(actions) {
                out.push(("trap_territory_offer_changed", None));
            }
        }
        let sig = |s: &State| r2_branches(s, chosen).iter().map(|(pr, b)| format!("{pr} {}", r2_board(b))).collect::<Vec<_>>();
        if sig(before) != sig(&old) {
            out.push(("trap_territory_outcome_changed", None));
        }
    }

    // Luxury Coin on the opponent's Stadium (the follow-up). Exact: the chosen UseStadium's forecast leaves a Luxury Coin pause
    // when the Stadium is made the mover's own, and none as it stands. Off the gate: a Luxury Coin reroll offered.
    if matches!(chosen.action, SimpleAction::UseStadium)
        && before.active_stadium_owner == Some(opp)
        && (0..4).any(|i| at(actor, i).is_some_and(|p| r2_ability(p) == "LuxuryCoin"))
    {
        let mut own = before.clone();
        own.active_stadium_owner = Some(actor);
        let paused = |s: &State| r2_branches(s, chosen).iter().any(|(_, b)| b.pending_trainer_coin_choice.is_some());
        if paused(&own) && !paused(before) {
            out.push(("luxury_coin_opp_stadium", None));
        }
    }
    if actions.iter().any(|a| matches!(a.action, SimpleAction::RerollTrainerCoins { .. })) {
        out.push(("offgate_luxury_coin_offered", None));
    }

    // A Fossil under an Item lock (the follow-up). Exact: at a main-phase choice (EndTurn offered), the mover holds a Fossil that
    // the old move generation offered (its own builder offers it, no NoTrainerCards), and NoItemCards is in force. Off the gate:
    // a Fossil offered.
    let is_fossil = |c: &Card| matches!(c, Card::Trainer(t) if t.trainer_card_type == TrainerType::Fossil);
    if turn > 0
        && actions.iter().any(|a| matches!(a.action, SimpleAction::EndTurn))
        && before.hands[actor].iter().any(is_fossil)
    {
        let effects = r2_turn_effects(before, turn);
        let playable = before.hands[actor].iter().any(|c| match c {
            Card::Trainer(t) if t.trainer_card_type == TrainerType::Fossil => {
                deckgym::move_generation::trainer_move_generation_implementation(before, t).is_some_and(|m| !m.is_empty())
            }
            _ => false,
        });
        if playable && effects.iter().any(|e| e == "NoItemCards") && !effects.iter().any(|e| e == "NoTrainerCards") {
            out.push(("fossil_item_lock", None));
        }
    }
    if actions.iter().any(|a| matches!(&a.action, SimpleAction::Place(c, _) if is_fossil(c))) {
        out.push(("offgate_fossil_offered", None));
    }

    // P2: return damage an attack left takes Weakness. The chosen move runs the hit back on a damaged opposing Active: (the
    // Attacking Pokemon, the defender, whether the damage landed at an earlier tick). Exact: the defender carries an attack's
    // return damage and a branch where the hit back landed leaves a different board with the attacker's printed Weakness taken
    // away. Off the gate: any other such tick on a defender with a return-damage source, by source.
    let gate = match &chosen.action {
        SimpleAction::Attack(_)
        | SimpleAction::ApplyQueuedAttackDamage { .. }
        | SimpleAction::KeepAttackCoinResults
        | SimpleAction::RerollAttackCoins { .. } => Some(((actor, 0), (opp, 0), false)),
        SimpleAction::ApplyDamage { attacking_ref, targets, is_from_active_attack: true }
            if targets.iter().any(|(d, q, i)| *d > 0 && *q == 1 - attacking_ref.0 && *i == 0) =>
        {
            Some((*attacking_ref, (1 - attacking_ref.0, 0), false))
        }
        SimpleAction::ResolveAttackRetaliation { attacking_ref, damaged_refs, .. } => {
            damaged_refs.first().map(|&d| (*attacking_ref, d, true))
        }
        _ => None,
    };
    if let Some(((aq, ai), (dq, di), held)) = gate {
        if let Some(defender) = at(dq, di) {
            let sources = r2_return_sources(defender);
            if !sources.is_empty() {
                let (id, hp) = (defender.card.get_id(), defender.get_remaining_hp());
                // Held-back hit backs on the stack. The move holds its own back when it leaves more than it found (the
                // ResolveAttackRetaliation it resolves counts as one fewer); frames from earlier moves don't count.
                let frames = |s: &State| {
                    s.move_generation_stack
                        .iter()
                        .flat_map(|(_, frame)| frame.iter())
                        .filter(|a| matches!(a, SimpleAction::ResolveAttackRetaliation { .. }))
                        .count()
                };
                let frames_before = frames(before);
                let landed = |s: &State| {
                    s.pending_attack_coin_choice.is_none()
                        && frames(s) + held as usize <= frames_before
                        && (held
                            || s.in_play_pokemon[dq][di]
                                .as_ref()
                                .is_none_or(|p| p.card.get_id() != id || p.get_remaining_hp() < hp))
                };
                let with = r2_branches(before, chosen);
                let live: Vec<usize> = (0..with.len()).filter(|&k| landed(&with[k].1)).collect();
                if !live.is_empty() {
                    let exact = r2_attack_return(defender) > 0 && {
                        let without = r2_branches(&r2_strip_weakness(before, aq, ai), chosen);
                        without.len() != with.len() || live.iter().any(|&k| r2_board(&with[k].1) != r2_board(&without[k].1))
                    };
                    if exact {
                        out.push(("attack_return_weakness", None));
                    } else {
                        out.push(("offgate_return_by_source", Some(sources)));
                    }
                }
            }
        }
    }
    out
}
'''
R2_COUNTERS = ["will_confused_attack", "will_block_coin_attack", "vs_block_coin_built", "vs_block_coin_choice_offered",
               "coin_own_side_split", "coin_plain_damage_chosen", "perish_plain_hit_offered", "perish_plain_hit_chosen",
               "guts_own_side_split", "trap_territory_offer_changed", "trap_territory_outcome_changed",
               "luxury_coin_opp_stadium", "fossil_item_lock",
               "offgate_plain_attack_damage", "offgate_guts_opponent_split", "offgate_confused_attack",
               "offgate_block_coin_attack", "offgate_vs_ungated_built", "offgate_trap_territory_one",
               "offgate_luxury_coin_offered", "offgate_fossil_offered", "trap_territory_two_in_play",
               "attack_return_weakness"]
R2_KEYED = ["coin_queued_by_attack", "coin_plain_damage_by_attack", "offgate_by_attack", "offgate_return_by_source"]
if sys.argv[1:2] == ["--emit-fns"]:
    open(sys.argv[2], "w", encoding="utf-8").write(R2_FNS)
    print("wrote", sys.argv[2])
    sys.exit(0)
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
if "coin_defender_attack" in src:
    raise SystemExit("already instrumented by this script (coin_defender_attack is in the file); apply it to a fresh copy")
EXACT = ["coin_cut_recorded", "coin_full_prevention", "coin_queued_offered", "coin_queued_offered_any",
         "offgate_helper_choice", "offgate_discard_then_damage"]
VAR = {"coin_cut_recorded": "coin_cut_c", "coin_full_prevention": "coin_full_c", "coin_queued_offered": "coin_queued_c",
       "coin_queued_offered_any": "coin_queued_any_c", "offgate_helper_choice": "coin_helper_c",
       "offgate_discard_then_damage": "coin_discard_c"}
BY_MECHANIC = "offgate_helper_by_mechanic"
EDITS = [
    ("    fingerprint: u64,\n",
     "    coin_defender_attack: u32,\n    coin_queued_attack_damage: u32,\n"
     + "".join(f"    {name}: (u32, Vec<u32>),\n" for name in EXACT)
     + f"    {BY_MECHANIC}: std::collections::BTreeMap<String, Vec<u32>>,\n"),
    ("    let mut moves = DefaultHasher::new();\n",
     "    let (mut coin_attack_n, mut coin_queued_n) = (0u32, 0u32);\n"
     "    let mut coin_tick = 0u32;\n"
     + "".join(f"    let mut {VAR[name]} = (0u32, Vec::<u32>::new());\n" for name in EXACT)
     + "    let mut coin_helper_by: std::collections::BTreeMap<String, Vec<u32>> = std::collections::BTreeMap::new();\n"
     "    let mut coin_last_attack: [Option<(u8, String)>; 2] = [None, None];\n"
     "    let mut coin_after_discard: Option<usize> = None;\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            const COIN_IDS: [&str; 5] = [\"A2 114\", \"A4 080\", \"B2 124\", \"B2 204\", \"B3b 050\"];\n"
     "            const FINITE: [&str; 2] = [\"A2 114\", \"B3b 050\"];\n"
     "            const FULL: [&str; 3] = [\"A4 080\", \"B2 124\", \"B2 204\"];\n"
     "            const HELPERS: [&str; 14] = [\"DirectDamage\", \"DirectDamageAndSelfCardEffect\", \"DirectDamageIfDamaged\",\n"
     "                \"SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon\", \"SelfDiscardEnergyThenDamageAnyOpponentPokemon\",\n"
     "                \"DamageToAnyOpponentPerTargetEnergy\", \"SwitchInOpponentBenchedThenDamage\",\n"
     "                \"OptionalDiscardBenchedBasicForExtraDamage\",\n"
     "                // The later round (Oct 1).\n"
     "                \"CoinFlipAlsoChoiceBenchDamage\", \"SelfDiscardEnergyAndChoiceBenchDamage\", \"ConditionalBenchDamage\",\n"
     "                \"ShuffleOpponentToolsIntoDeckBeforeDamage\", \"DiscardToolsFromHandForDamage\",\n"
     "                \"MegaKangaskhanExDoublePunchingFamily\"];\n"
     "            // A counter fires once per tick: its count is the number of ticks, its list every one of them.\n"
     "            let fire = |c: &mut (u32, Vec<u32>), t: u32| {\n"
     "                if c.1.last() != Some(&t) {\n"
     "                    c.0 += 1;\n"
     "                    c.1.push(t);\n"
     "                }\n"
     "            };\n"
     "            let opp = 1 - chosen.actor;\n"
     "            let is_coin = |q: usize, i: usize| {\n"
     "                before.in_play_pokemon[q].get(i).and_then(|p| p.as_ref()).is_some_and(|p| COIN_IDS.contains(&p.card.get_id().as_str()))\n"
     "            };\n"
     "            let id_at = |i: usize| before.in_play_pokemon[opp].get(i).and_then(|p| p.as_ref()).map(|p| p.card.get_id());\n"
     "            let mechanic_of = |attack: &deckgym::models::Attack| -> String {\n"
     "                attack.effect.as_deref().and_then(|e| deckgym::actions::EFFECT_MECHANIC_MAP.get(e))\n"
     "                    .map(|m| format!(\"{m:?}\").chars().take_while(|c| c.is_alphanumeric()).collect::<String>())\n"
     "                    .unwrap_or_default()\n"
     "            };\n"
     "            // Superset counters (the Sept 30 originals).\n"
     "            let coin_in_play = (0..before.in_play_pokemon[opp].len()).any(|i| is_coin(opp, i));\n"
     "            let attack_move = match &chosen.action {\n"
     "                SimpleAction::Attack(_) | SimpleAction::ApplyQueuedAttackDamage { .. } => true,\n"
     "                SimpleAction::ApplyDamage { is_from_active_attack, .. } => *is_from_active_attack,\n"
     "                _ => false,\n"
     "            };\n"
     "            if attack_move && coin_in_play {\n"
     "                coin_attack_n += 1;\n"
     "            }\n"
     "            if let SimpleAction::ApplyQueuedAttackDamage { targets, .. } = &chosen.action {\n"
     "                if targets.iter().any(|(_, is_opp, i)| *is_opp && is_coin(opp, *i)) {\n"
     "                    coin_queued_n += 1;\n"
     "                }\n"
     "            }\n"
     "            // Exact: the queued coin-path choice was offered.\n"
     "            let queued_offered = actions.iter().any(|a| match &a.action {\n"
     "                SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {\n"
     "                    !mechanic_of(attack).starts_with(\"AlsoChoiceBenchDamage\")\n"
     "                        && targets.iter().any(|(_, is_opp, i)| *is_opp && is_coin(opp, *i))\n"
     "                }\n"
     "                _ => false,\n"
     "            });\n"
     "            if queued_offered {\n"
     "                fire(&mut coin_queued_c, coin_tick);\n"
     "            }\n"
     "            // Exact, without the id list: any offered ApplyQueuedAttackDamage that is not the AlsoChoiceBenchDamage form.\n"
     "            if actions.iter().any(|a| matches!(&a.action, SimpleAction::ApplyQueuedAttackDamage { attack, .. }\n"
     "                if !mechanic_of(attack).starts_with(\"AlsoChoiceBenchDamage\")))\n"
     "            {\n"
     "                fire(&mut coin_queued_any_c, coin_tick);\n"
     "            }\n"
     "            // Exact: the coin split ran for a finite-cut or a full-prevention Pokemon (the forecast has more branches than\n"
     "            // with that Pokemon replaced by a Bulbasaur).\n"
     "            if matches!(&chosen.action, SimpleAction::Attack(_) | SimpleAction::ApplyQueuedAttackDamage { .. }) {\n"
     "                let branches = |s: &State| deckgym::actions::try_forecast_action(s, &chosen).ok().map(|o| o.into_branches().0.len());\n"
     "                if let Some(n_real) = branches(&before) {\n"
     "                    for i in 0..before.in_play_pokemon[opp].len() {\n"
     "                        let Some(id) = id_at(i) else { continue };\n"
     "                        let (finite, full) = (FINITE.contains(&id.as_str()), FULL.contains(&id.as_str()));\n"
     "                        if !finite && !full {\n"
     "                            continue;\n"
     "                        }\n"
     "                        let mut without = before.clone();\n"
     "                        without.in_play_pokemon[opp][i] = Some(PlayedCard::from_id(deckgym::card_ids::CardId::A1001Bulbasaur));\n"
     "                        if branches(&without).is_some_and(|n| n < n_real) {\n"
     "                            fire(if finite { &mut coin_cut_c } else { &mut coin_full_c }, coin_tick);\n"
     "                        }\n"
     "                    }\n"
     "                }\n"
     "            }\n"
     "            // Exact: off-gate queued choices of the rewritten helpers, by the mechanic of the mover's last Attack this turn.\n"
     "            let plain_damage_offered = actions.iter().any(|a| matches!(&a.action,\n"
     "                SimpleAction::ApplyDamage { is_from_active_attack: true, targets, .. } if targets.iter().any(|(_, p, _)| *p == opp)));\n"
     "            let helper_mechanic = coin_last_attack[chosen.actor].as_ref()\n"
     "                .filter(|(turn, name)| *turn == before.turn_count && HELPERS.contains(&name.as_str()))\n"
     "                .map(|(_, name)| name.clone());\n"
     "            if let (true, Some(name)) = (plain_damage_offered, helper_mechanic) {\n"
     "                fire(&mut coin_helper_c, coin_tick);\n"
     "                let ticks = coin_helper_by.entry(name).or_default();\n"
     "                if ticks.last() != Some(&coin_tick) {\n"
     "                    ticks.push(coin_tick);\n"
     "                }\n"
     "            }\n"
     "            // Exact: the ApplyDamage straight after a DiscardOwnBenchedThenDamage move (Chase Order, Wild Swing).\n"
     "            if coin_after_discard == Some(chosen.actor) && plain_damage_offered {\n"
     "                fire(&mut coin_discard_c, coin_tick);\n"
     "            }\n"
     "            coin_after_discard = matches!(&chosen.action, SimpleAction::DiscardOwnBenchedThenDamage { .. }).then_some(chosen.actor);\n"
     "            if let SimpleAction::Attack(attack) = &chosen.action {\n"
     "                coin_last_attack[chosen.actor] = Some((before.turn_count, mechanic_of(attack)));\n"
     "            }\n"
     "            coin_tick += 1;\n"
     "        }\n"),
    ("        fingerprint: moves.finish(),\n",
     "        coin_defender_attack: coin_attack_n,\n        coin_queued_attack_damage: coin_queued_n,\n"
     + "".join(f"        {name}: {VAR[name]},\n" for name in EXACT)
     + f"        {BY_MECHANIC}: coin_helper_by,\n"),
]
# The round-2 package: its fields, its per-tick block (r2_tick, R2_FNS) and its functions before `play_one`.
EDITS += [
    ("    fingerprint: u64,\n",
     "    r2_fired: BTreeMap<String, (u32, Vec<u32>)>,\n    r2_keyed: BTreeMap<String, BTreeMap<String, Vec<u32>>>,\n"),
    ("    let mut moves = DefaultHasher::new();\n",
     "    let mut r2_fired: BTreeMap<String, (u32, Vec<u32>)> = BTreeMap::new();\n"
     "    let mut r2_keyed: BTreeMap<String, BTreeMap<String, Vec<u32>>> = BTreeMap::new();\n"
     "    let mut r2_tick_n = 0u32;\n"
     "    let mut r2_last: [Option<(u8, deckgym::models::Attack)>; 2] = [None, None];\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            // The round-2 package's counters (r2_tick): every tick at which each fires.\n"
     "            let last = r2_last[chosen.actor].as_ref().filter(|(t, _)| *t == before.turn_count).map(|(_, a)| a);\n"
     "            for (name, key) in r2_tick(&before, &actions, &chosen, last) {\n"
     "                match key {\n"
     "                    None => {\n"
     "                        let c = r2_fired.entry(name.to_string()).or_default();\n"
     "                        if c.1.last() != Some(&r2_tick_n) {\n"
     "                            c.0 += 1;\n"
     "                            c.1.push(r2_tick_n);\n"
     "                        }\n"
     "                    }\n"
     "                    Some(k) => {\n"
     "                        let ticks = r2_keyed.entry(name.to_string()).or_default().entry(k).or_default();\n"
     "                        if ticks.last() != Some(&r2_tick_n) {\n"
     "                            ticks.push(r2_tick_n);\n"
     "                        }\n"
     "                    }\n"
     "                }\n"
     "            }\n"
     "            if let SimpleAction::Attack(attack) = &chosen.action {\n"
     "                r2_last[chosen.actor] = Some((before.turn_count, attack.clone()));\n"
     "            }\n"
     "            r2_tick_n += 1;\n"
     "        }\n"),
    ("        fingerprint: moves.finish(),\n", "        r2_fired,\n        r2_keyed,\n"),
]
if src.count("\nfn play_one(") != 1:
    raise SystemExit("anchor found other than once: fn play_one(")
src = src.replace("\nfn play_one(", "\n" + R2_FNS + "\nfn play_one(")
for anchor, add in EDITS:
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"anchor found {n} times: {anchor!r}")
    src = src.replace(anchor, anchor + add)
# The JSON line: add the fields right after the `let mut line = serde_json::json!({ ... });` statement.
start = src.find("let mut line = serde_json::json!({")
if start < 0 or src.count("let mut line = serde_json::json!({") != 1:
    raise SystemExit("games-out json anchor not found exactly once")
end = src.find("});\n", start) + len("});\n")
indent = " " * (start - src.rfind("\n", 0, start) - 1)
lines = (f"{indent}line[\"coin_defender_attack\"] = serde_json::json!(r.coin_defender_attack);\n"
         f"{indent}line[\"coin_queued_attack_damage\"] = serde_json::json!(r.coin_queued_attack_damage);\n"
         + "".join(f"{indent}line[\"{name}\"] = serde_json::json!({{ \"n\": r.{name}.0, \"first\": r.{name}.1.first(), \"ticks\": r.{name}.1 }});\n"
                   for name in EXACT)
         + f"{indent}line[\"{BY_MECHANIC}\"] = serde_json::json!(r.{BY_MECHANIC});\n"
         + "".join(f"{indent}line[\"{name}\"] = {{ let c = r.r2_fired.get(\"{name}\"); serde_json::json!({{ \"n\": c.map_or(0, |c| c.0), "
                   f"\"first\": c.and_then(|c| c.1.first()), \"ticks\": c.map(|c| c.1.clone()).unwrap_or_default() }}) }};\n"
                   for name in R2_COUNTERS)
         + "".join(f"{indent}line[\"{name}\"] = serde_json::json!(r.r2_keyed.get(\"{name}\").cloned().unwrap_or_default());\n"
                   for name in R2_KEYED))
src = src[:end] + lines + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
