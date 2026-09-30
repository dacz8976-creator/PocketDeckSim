"""Watch-only instrumentation of legality_scan for the coin-flip damage prevention repair (Sept 30; RUN5's switch
template). Adds two per-game counters to the --games-out line, changing no play (they only read the state before each
tick and the chosen move):
- "coin_defender_attack": attack moves (an Attack, or a queued ApplyDamage / ApplyQueuedAttackDamage from an attack)
  while the mover's opponent has a Pokemon with a coin-flip damage Ability in play: Bastiodon A2 114, Togekiss A4 080,
  Meowth B2 124 or B2 204, Hisuian Goodra B3b 050. That is a superset of both gates (a heads coin cut, and queued
  attack damage at a coin-Ability Pokemon), so 0 in a game means the repaired code never ran there.
- "coin_queued_attack_damage": queued ApplyQueuedAttackDamage moves with a target that has one of those Abilities. The
  repaired engine queues snipes at them this way. The old one did too, but only for also_choice_bench_damage's
  opponent-Bench form.
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once;
it can be applied after the Victory Star repair's script, which uses the same anchors)"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
EDITS = [
    ("    fingerprint: u64,\n", "    coin_defender_attack: u32,\n    coin_queued_attack_damage: u32,\n"),
    ("    let mut moves = DefaultHasher::new();\n", "    let (mut coin_attack_n, mut coin_queued_n) = (0u32, 0u32);\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            const COIN_IDS: [&str; 5] = [\"A2 114\", \"A4 080\", \"B2 124\", \"B2 204\", \"B3b 050\"];\n"
     "            let opp = 1 - chosen.actor;\n"
     "            let is_coin = |q: usize, i: usize| {\n"
     "                before.in_play_pokemon[q].get(i).and_then(|p| p.as_ref()).is_some_and(|p| COIN_IDS.contains(&p.card.get_id().as_str()))\n"
     "            };\n"
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
     "        }\n"),
    ("        fingerprint: moves.finish(),\n", "        coin_defender_attack: coin_attack_n,\n        coin_queued_attack_damage: coin_queued_n,\n"),
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
src = (src[:end] + f"{indent}line[\"coin_defender_attack\"] = serde_json::json!(r.coin_defender_attack);\n"
       f"{indent}line[\"coin_queued_attack_damage\"] = serde_json::json!(r.coin_queued_attack_damage);\n" + src[end:])
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
