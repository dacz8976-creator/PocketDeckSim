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
- "coin_queued_offered" (B b and Chase Order): the queued coin-path choice was offered: an ApplyQueuedAttackDamage at a
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
  Order without the discard). A plain ApplyDamage has the same fields whoever built it, so the source is told by the
  mechanic of the last Attack the mover chose that turn (copied attacks included). Built by
  `queued_attack_damage_choice`'s else branch. It is the proof that the table runs those rewritten lines.
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
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once;
it applies with the Victory Star repair's script in either order, and alone)"""
import sys
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
     "            const HELPERS: [&str; 8] = [\"DirectDamage\", \"DirectDamageAndSelfCardEffect\", \"DirectDamageIfDamaged\",\n"
     "                \"SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon\", \"SelfDiscardEnergyThenDamageAnyOpponentPokemon\",\n"
     "                \"DamageToAnyOpponentPerTargetEnergy\", \"SwitchInOpponentBenchedThenDamage\",\n"
     "                \"OptionalDiscardBenchedBasicForExtraDamage\"];\n"
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
         + f"{indent}line[\"{BY_MECHANIC}\"] = serde_json::json!(r.{BY_MECHANIC});\n")
src = src[:end] + lines + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
