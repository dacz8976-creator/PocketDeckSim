"""Watch-only instrumentation of legality_scan for the engine switch's literal check (Dustin, Sept 26).
Adds two per-game counters to the --games-out line, changing no play:
- "pulse": ticks where the player ending its turn (the EndTurn tick, chosen or forced after an attack) has a
  Legendary Pulse Pokémon Active: Suicune ex, Entei ex or Raikou ex (all 13 printings carry EndTurnDrawCardIfActive,
  rules/09).
- "eot_ko": EndTurn or Checkup ticks during which either player's count of Pokémon in play drops, i.e. a Knock Out
  at the end of the turn or in the Checkup (Poison, Burn, Bad Dreams and the like).
Usage: python3 instrument_scan.py <legality_scan.rs>   (edits the file in place; every anchor must occur exactly once)"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
EDITS = [
    ("    fingerprint: u64,\n", "    pulse: u32,\n    eot_ko: u32,\n"),
    ("    let mut moves = DefaultHasher::new();\n", "    let (mut pulse_n, mut eot_ko_n) = (0u32, 0u32);\n"),
    ("        let after = game.get_state_clone();\n",
     "        {\n"
     "            let act = format!(\"{:?}\", chosen.action);\n"
     "            if act == \"EndTurn\" {\n"
     "                if let Some(p) = before.in_play_pokemon[chosen.actor][0].as_ref() {\n"
     "                    let n = p.get_name();\n"
     "                    if n == \"Suicune ex\" || n == \"Entei ex\" || n == \"Raikou ex\" { pulse_n += 1; }\n"
     "                }\n"
     "            }\n"
     "            let cnt = |s: &State, q: usize| s.in_play_pokemon[q].iter().filter(|x| x.is_some()).count();\n"
     "            if (act == \"EndTurn\" || act.contains(\"Checkup\")) && (0..2).any(|q| cnt(&after, q) < cnt(&before, q)) {\n"
     "                eot_ko_n += 1;\n"
     "            }\n"
     "        }\n"),
    ("        fingerprint: moves.finish(),\n", "        pulse: pulse_n,\n        eot_ko: eot_ko_n,\n"),
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
src = src[:end] + f"{indent}line[\"pulse\"] = serde_json::json!(r.pulse);\n{indent}line[\"eot_ko\"] = serde_json::json!(r.eot_ko);\n" + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("instrumented", path)
