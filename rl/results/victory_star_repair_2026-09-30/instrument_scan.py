"""Watch-only instrumentation of legality_scan for the Victory Star / Confusion repair (Sept 30; RUN5's switch template;
exact counters added for the rules switch's F5). It adds per-game counters to the --games-out line, changing no play
(they only read the states before each tick, the chosen move, and forecasts of it on clones; nothing touches the game).

Move numbers. A tick is one `play_tick`, one chosen move, numbered from 0 as `coin_trace.rs` and `vs_trace.rs` print it, so a
counter's ticks compare directly with a first-difference trace. Every exact counter is recorded as
{"n": the number of ticks at which it fired, "first": the first such tick or null, "ticks": every such tick, ascending}, so a
reader can ask whether it fired in a given turn or at a given tick, not only whether it ever fired (the rules switch's F5,
second read). Everything is counted for the move the game CHOSE or OFFERED, never for the bots' lookahead.

EXACT (these count as reach, as the mechanic check uses them):
- "vs_confusion_first_built": {"n", "first", "ticks"}. The Confusion-first branch was built for the attack the game chose: a Confused
  Active's own (not a copied) attack for which the engine's forecast contains a Victory Star pause. Detected by asking the
  engine: `try_forecast_action(before, chosen)`, then each branch's mutation is applied to a clone of `before` and any
  branch that leaves `pending_attack_coin_choice` set is a built pause. Only the Confusion-first path builds a pause for a
  Confused attacker (the legacy engine never does), so this holds exactly when the gate held (working Victini, Fire
  Active, Victory Star unused, no CoinFlipToBlockAttack, no Will pending, an attack with coins of its own), for the tails
  half and the heads half alike. The engine's own gate is the test, so ability suppression is read as the engine reads it.
  On an engine without the repair it is always 0.
- "vs_confused_choice" and "vs_confused_choice_first": Victory Star choices (Keep or Reroll) made while the chooser's
  Active is Confused. The legacy engine never offers one; the repaired engine offers one only after a Confusion heads. This
  is the heads half of the built branch, seen one or more moves later. Kept as the cloud wrote them (a count and the first
  tick); "vs_confused_choice_chosen" is the same counter with every tick.
- "vs_confused_choice_offered": {"n", "first", "ticks"}. Keep or Reroll among the moves a tick OFFERED while the chooser's
  Active is Confused, whether or not the bot took it (a declined choice still shows that the repaired code ran).
SUPERSET (kept to back "all counters 0 means identical"; never reach):
- "vs_confused_attack": attacks (not stack sub-attacks) by a Confused Fire Active whose side has a Victini in play and has
  not used Victory Star this turn. A superset of the repair's gate (the gate also needs an attack-effect coin batch and no
  CoinFlipToBlockAttack or pending Will), so 0 in a game means the new code never ran there.
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once;
it applies with the coin repair's script in either order, and alone)"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
if "vs_confused_attack" in src:
    raise SystemExit("already instrumented by this script (vs_confused_attack is in the file); apply it to a fresh copy")
EDITS = [
    ("    fingerprint: u64,\n",
     "    vs_confused_attack: u32,\n    vs_confused_choice: u32,\n"
     "    vs_confusion_first_built: (u32, Vec<u32>),\n    vs_confused_choice_first: Option<u32>,\n"
     "    vs_confused_choice_chosen: (u32, Vec<u32>),\n    vs_confused_choice_offered: (u32, Vec<u32>),\n"),
    ("    let mut moves = DefaultHasher::new();\n",
     "    let (mut vs_attack_n, mut vs_choice_n) = (0u32, 0u32);\n"
     "    let mut vs_tick = 0u32;\n"
     "    let mut vs_built = (0u32, Vec::<u32>::new());\n"
     "    let mut vs_choice_first = None::<u32>;\n"
     "    let mut vs_chosen = (0u32, Vec::<u32>::new());\n"
     "    let mut vs_offered = (0u32, Vec::<u32>::new());\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            let active = before.maybe_get_active(chosen.actor);\n"
     "            let confused = active.is_some_and(|p| p.is_confused());\n"
     "            let fire = active.is_some_and(|p| matches!(&p.card, Card::Pokemon(c) if c.energy_type == EnergyType::Fire));\n"
     "            let victini = before.enumerate_in_play_pokemon(chosen.actor).any(|(_, p)| p.get_name() == \"Victini\");\n"
     "            // A counter fires once per tick: its count is the number of ticks, its list every one of them.\n"
     "            let vs_fire = |c: &mut (u32, Vec<u32>), t: u32| {\n"
     "                if c.1.last() != Some(&t) {\n"
     "                    c.0 += 1;\n"
     "                    c.1.push(t);\n"
     "                }\n"
     "            };\n"
     "            // Exact: Keep or Reroll was among the offered moves while the chooser's Active is Confused.\n"
     "            if confused && actions.iter().any(|a| matches!(&a.action,\n"
     "                SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. })) {\n"
     "                vs_fire(&mut vs_offered, vs_tick);\n"
     "            }\n"
     "            match &chosen.action {\n"
     "                SimpleAction::Attack(_) if !chosen.is_stack && confused && fire && victini\n"
     "                    && !before.victory_star_used_this_turn[chosen.actor] => vs_attack_n += 1,\n"
     "                SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. } if confused => {\n"
     "                    vs_choice_n += 1;\n"
     "                    vs_choice_first.get_or_insert(vs_tick);\n"
     "                    vs_fire(&mut vs_chosen, vs_tick);\n"
     "                }\n"
     "                _ => {}\n"
     "            }\n"
     "            // Exact: the Confusion-first branch was built for this chosen attack (see the docstring of the script).\n"
     "            if confused && !chosen.is_stack && matches!(&chosen.action, SimpleAction::Attack(_)) {\n"
     "                if let Ok(outcomes) = deckgym::actions::try_forecast_action(&before, &chosen) {\n"
     "                    let (_, mutations) = outcomes.into_branches();\n"
     "                    let built = mutations.into_iter().any(|mutate| {\n"
     "                        let mut branch = before.clone();\n"
     "                        mutate(&mut <rand::rngs::StdRng as rand::SeedableRng>::seed_from_u64(0), &mut branch, &chosen);\n"
     "                        branch.pending_attack_coin_choice.is_some()\n"
     "                    });\n"
     "                    if built {\n"
     "                        vs_fire(&mut vs_built, vs_tick);\n"
     "                    }\n"
     "                }\n"
     "            }\n"
     "            vs_tick += 1;\n"
     "        }\n"),
    ("        fingerprint: moves.finish(),\n",
     "        vs_confused_attack: vs_attack_n,\n        vs_confused_choice: vs_choice_n,\n"
     "        vs_confusion_first_built: vs_built,\n        vs_confused_choice_first: vs_choice_first,\n"
     "        vs_confused_choice_chosen: vs_chosen,\n        vs_confused_choice_offered: vs_offered,\n"),
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
src = (src[:end]
       + f"{indent}line[\"vs_confused_attack\"] = serde_json::json!(r.vs_confused_attack);\n"
       + f"{indent}line[\"vs_confused_choice\"] = serde_json::json!(r.vs_confused_choice);\n"
       + f"{indent}line[\"vs_confused_choice_first\"] = serde_json::json!(r.vs_confused_choice_first);\n"
       + "".join(f"{indent}line[\"{name}\"] = serde_json::json!({{ \"n\": r.{name}.0, \"first\": r.{name}.1.first(), \"ticks\": r.{name}.1 }});\n"
                 for name in ("vs_confusion_first_built", "vs_confused_choice_chosen", "vs_confused_choice_offered"))
       + src[end:])
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
