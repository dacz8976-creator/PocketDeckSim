"""Second watch-only hook for the literal check's follow-up: for the seeds listed in the DUMP_SEEDS environment variable
(comma-separated), print every tick to stderr as
  DUMP <seed> <tick> t<turn> p<player to move> <actor> :: <chosen action> || <seat 0 board> || <seat 1 board>
where a board is "[Active hp status | Bench] pts N". Unlisted seeds print nothing and no play changes.
Usage: python3 instrument_dump.py <legality_scan.rs already instrumented by instrument_scan.py>"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
EDITS = [
    ("    let (mut pulse_n, mut eot_ko_n) = (0u32, 0u32);\n",
     "    let mut dump_tick = 0u32;\n"
     "    let dump_on = std::env::var(\"DUMP_SEEDS\").map(|l| l.split(',').any(|x| x.trim() == seed.to_string())).unwrap_or(false);\n"),
    ("        let after = game.get_state_clone();\n",
     "        if dump_on {\n"
     "            dump_tick += 1;\n"
     "            let side = |s: &State, q: usize| -> String {\n"
     "                let a = s.in_play_pokemon[q][0].as_ref().map(|p| format!(\"{} {}hp{}{}{}{}\", p.get_name(), p.get_remaining_hp(),\n"
     "                    if p.is_poisoned() { \" PSN\" } else { \"\" }, if p.is_burned() { \" BRN\" } else { \"\" },\n"
     "                    if p.is_asleep() { \" SLP\" } else { \"\" }, if p.is_paralyzed() { \" PAR\" } else { \"\" })).unwrap_or(\"-\".to_string());\n"
     "                let bench: Vec<String> = s.in_play_pokemon[q].iter().skip(1).flatten()\n"
     "                    .map(|p| format!(\"{} {}\", p.get_name(), p.get_remaining_hp())).collect();\n"
     "                format!(\"[{} | {}] pts {}\", a, bench.join(\", \"), s.points[q])\n"
     "            };\n"
     "            let act: String = format!(\"{:?}\", chosen.action).chars().take(160).collect();\n"
     "            eprintln!(\"DUMP {} {} t{} p{} {} :: {} || {} || {}\", seed, dump_tick, before.turn_count, before.current_player,\n"
     "                chosen.actor, act, side(&before, 0), side(&before, 1));\n"
     "        }\n"),
]
for anchor, add in EDITS:
    if src.count(anchor) != 1:
        raise SystemExit(f"anchor found {src.count(anchor)} times: {anchor!r}")
    src = src.replace(anchor, anchor + add)
open(path, "w", encoding="utf-8").write(src)
print("dump hook added", path)
