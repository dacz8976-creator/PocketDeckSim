"""Watch-only instrumentation of legality_scan for the Victory Star / Confusion repair (Sept 30; RUN5's switch template).
Adds two per-game counters to the --games-out line, changing no play (they only read the states before each tick and
the chosen move):
- "vs_confused_attack": attacks (not stack sub-attacks) by a Confused Fire Active whose side has a Victini in play
  and has not used Victory Star this turn. That is a superset of the repair's gate (the gate also needs an attack-effect
  coin batch and no CoinFlipToBlockAttack or pending Will), so 0 in a game means the new code never ran there.
- "vs_confused_choice": Victory Star choices (Keep or Reroll) made while the chooser's Active is Confused. The legacy
  engine never offers one; the repaired engine offers one only after a Confusion heads.
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once)"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
EDITS = [
    ("    fingerprint: u64,\n", "    vs_confused_attack: u32,\n    vs_confused_choice: u32,\n"),
    ("    let mut moves = DefaultHasher::new();\n", "    let (mut vs_attack_n, mut vs_choice_n) = (0u32, 0u32);\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            let active = before.maybe_get_active(chosen.actor);\n"
     "            let confused = active.is_some_and(|p| p.is_confused());\n"
     "            let fire = active.is_some_and(|p| matches!(&p.card, Card::Pokemon(c) if c.energy_type == EnergyType::Fire));\n"
     "            let victini = before.enumerate_in_play_pokemon(chosen.actor).any(|(_, p)| p.get_name() == \"Victini\");\n"
     "            match &chosen.action {\n"
     "                SimpleAction::Attack(_) if !chosen.is_stack && confused && fire && victini\n"
     "                    && !before.victory_star_used_this_turn[chosen.actor] => vs_attack_n += 1,\n"
     "                SimpleAction::KeepAttackCoinResults | SimpleAction::RerollAttackCoins { .. } if confused => vs_choice_n += 1,\n"
     "                _ => {}\n"
     "            }\n"
     "        }\n"),
    ("        fingerprint: moves.finish(),\n", "        vs_confused_attack: vs_attack_n,\n        vs_confused_choice: vs_choice_n,\n"),
]
for anchor, add in EDITS:
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"anchor found {n} times: {anchor!r}")
    src = src.replace(anchor, anchor + add)
# The JSON line: add the two fields right after the `let mut line = serde_json::json!({ ... });` statement.
start = src.find("let mut line = serde_json::json!({")
if start < 0 or src.count("let mut line = serde_json::json!({") != 1:
    raise SystemExit("games-out json anchor not found exactly once")
end = src.find("});\n", start) + len("});\n")
indent = " " * (start - src.rfind("\n", 0, start) - 1)
src = (src[:end] + f"{indent}line[\"vs_confused_attack\"] = serde_json::json!(r.vs_confused_attack);\n"
       f"{indent}line[\"vs_confused_choice\"] = serde_json::json!(r.vs_confused_choice);\n" + src[end:])
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
