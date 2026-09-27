"""Watch-only per-move trace hook for kpf's veto diagnosis (Dustin, Sept 27: "trace the own-side-worse games ... count
what kpr's projection makes them do that kp3 doesn't"). For seeds in DUMP_SEEDS, prints each tick to stderr as
  DUMP2 <seed> <tick> t<turn> p<to move> <actor> :: <action> || <seat 0> || <seat 1>
with each seat as "Z<current>/<next> D<discard Energy> H<hand> P<points> | Active: name hp status E[types] | Bench: ...".
Apply to an unmodified legality_scan.rs. Usage: python3 instrument_dump2.py <legality_scan.rs>"""
import sys
path = sys.argv[1]
src = open(path, encoding="utf-8").read()
EDITS = [
    ("    let mut moves = DefaultHasher::new();\n",
     "    let mut dump_tick = 0u32;\n"
     "    let dump_on = std::env::var(\"DUMP_SEEDS\").map(|l| l.split(',').any(|x| x.trim() == seed.to_string())).unwrap_or(false);\n"),
    ("        let after = game.get_state_clone();\n",
     "        if dump_on {\n"
     "            dump_tick += 1;\n"
     "            let mon = |p: &PlayedCard| -> String {\n"
     "                let e: String = p.attached_energy.iter().map(|x| format!(\"{:?}\", x).chars().next().unwrap_or('?')).collect();\n"
     "                format!(\"{} {}hp{}{}{}{} E[{}]\", p.get_name(), p.get_remaining_hp(),\n"
     "                    if p.is_poisoned() { \" PSN\" } else { \"\" }, if p.is_burned() { \" BRN\" } else { \"\" },\n"
     "                    if p.is_asleep() { \" SLP\" } else { \"\" }, if p.is_paralyzed() { \" PAR\" } else { \"\" }, e)\n"
     "            };\n"
     "            let side = |s: &State, q: usize| -> String {\n"
     "                let a = s.in_play_pokemon[q][0].as_ref().map(|p| mon(p)).unwrap_or(\"-\".to_string());\n"
     "                let bench: Vec<String> = s.in_play_pokemon[q].iter().skip(1).flatten().map(|p| mon(p)).collect();\n"
     "                let z = &s.energy_zone[q];\n"
     "                format!(\"Z{:?}/{:?} D{} H{} P{} | {} | {}\", z.current, z.next, s.discard_energies[q].len(),\n"
     "                    s.hands[q].len(), s.points[q], a, bench.join(\", \"))\n"
     "            };\n"
     "            let act: String = format!(\"{:?}\", chosen.action).chars().take(160).collect();\n"
     "            eprintln!(\"DUMP2 {} {} t{} p{} {} :: {} || {} || {}\", seed, dump_tick, before.turn_count, before.current_player,\n"
     "                chosen.actor, act, side(&before, 0), side(&before, 1));\n"
     "        }\n"),
]
for anchor, add in EDITS:
    if src.count(anchor) != 1:
        raise SystemExit(f"anchor found {src.count(anchor)} times: {anchor!r}")
    src = src.replace(anchor, anchor + add)
open(path, "w", encoding="utf-8").write(src)
print("dump2 hook added", path)
