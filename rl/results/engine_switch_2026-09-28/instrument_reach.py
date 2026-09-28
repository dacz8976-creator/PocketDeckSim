"""Watch-only instrumentation for the Sept 28 switch's touched-path check (Dustin, Sept 28: "the check has to be where
the change is"). Patches a scratch tree of the new commit so each --games-out line carries two per-game counters,
changing no play:
- "reach_barrier": damage applications on the board where Metal Core Barrier cut damage
  (get_metal_core_barrier_reduction returned more than 0);
- "reach_turn": damage applications on the board where a turn effect cut damage (Jasmine, Cheren, Blue and the other
  ReducedDamageFor* turn effects: get_turn_effect_damage_reduction returned more than 0).
"On the board" = inside Game::play_tick's apply of the chosen move; the bots' lookahead runs outside it and isn't
counted. Counters are thread-local; a game runs on one thread (the bots use no rayon).
Usage: python3 instrument_reach.py <engine dir of a scratch tree>   (every anchor must occur exactly once)"""
import os, sys
E = sys.argv[1]


def patch(rel, edits, append=None):
    path = os.path.join(E, rel)
    raw = open(path, "rb").read().decode("utf-8")
    crlf = "\r\n" in raw
    src = raw.replace("\r\n", "\n")
    for anchor, new in edits:
        n = src.count(anchor)
        if n != 1:
            raise SystemExit(f"{rel}: anchor found {n} times: {anchor!r}")
        src = src.replace(anchor, new)
    if append:
        src += append
    if crlf:
        src = src.replace("\n", "\r\n")
    open(path, "wb").write(src.encode("utf-8"))
    print("patched", rel)


patch("src/lib.rs", [], append="""
/// Watch-only counters for the Sept 28 engine switch's touched-path check (rl/results/engine_switch_2026-09-28/).
pub mod watch_reach {
    use std::cell::Cell;
    thread_local! {
        static ON: Cell<bool> = Cell::new(false);
        static BARRIER: Cell<u32> = Cell::new(0);
        static TURN: Cell<u32> = Cell::new(0);
    }
    pub fn set_on(v: bool) {
        ON.with(|c| c.set(v));
    }
    pub fn bump(barrier: u32, turn: u32) {
        if ON.with(|c| c.get()) {
            if barrier > 0 {
                BARRIER.with(|c| c.set(c.get() + 1));
            }
            if turn > 0 {
                TURN.with(|c| c.set(c.get() + 1));
            }
        }
    }
    pub fn take() -> (u32, u32) {
        (BARRIER.with(|c| c.replace(0)), TURN.with(|c| c.replace(0)))
    }
}
""")
patch("src/hooks/core.rs", [
    ("    metal_core_barrier_reduction(state, defending_pokemon)\n}\n",
     "    let v = metal_core_barrier_reduction(state, defending_pokemon);\n    crate::watch_reach::bump(v, 0);\n    v\n}\n"),
    ("fn get_turn_effect_damage_reduction(\n",
     "#[allow(clippy::too_many_arguments)]\n"
     "fn get_turn_effect_damage_reduction(\n"
     "    state: &State,\n    turn: u8,\n    target_player: usize,\n    target_pokemon: &crate::models::PlayedCard,\n"
     "    attacking_player: usize,\n    attacking_pokemon: &PlayedCard,\n    is_from_active_attack: bool,\n) -> u32 {\n"
     "    let v = get_turn_effect_damage_reduction_inner(state, turn, target_player, target_pokemon, attacking_player,\n"
     "        attacking_pokemon, is_from_active_attack);\n"
     "    crate::watch_reach::bump(0, v);\n    v\n}\n\n"
     "#[allow(clippy::too_many_arguments)]\n"
     "fn get_turn_effect_damage_reduction_inner(\n"),
])
patch("src/game.rs", [
    ("        self.apply_action(&action);\n        self.print_state();\n        action\n",
     "        crate::watch_reach::set_on(true);\n        self.apply_action(&action);\n        crate::watch_reach::set_on(false);\n"
     "        self.print_state();\n        action\n"),
])
scan = "examples/legality_scan.rs"
patch(scan, [
    ("    fingerprint: u64,\n", "    fingerprint: u64,\n    reach_barrier: u32,\n    reach_turn: u32,\n"),
    ("    let mut moves = DefaultHasher::new();\n", "    let _ = deckgym::watch_reach::take();\n    let mut moves = DefaultHasher::new();\n"),
    ("    let end = game.get_state_clone();\n", "    let end = game.get_state_clone();\n    let reach = deckgym::watch_reach::take();\n"),
    ("        fingerprint: moves.finish(),\n", "        fingerprint: moves.finish(),\n        reach_barrier: reach.0,\n        reach_turn: reach.1,\n"),
])
# The JSON line: the two fields right after the `let mut line = serde_json::json!({ ... });` statement.
path = os.path.join(E, scan)
raw = open(path, "rb").read().decode("utf-8"); crlf = "\r\n" in raw; src = raw.replace("\r\n", "\n")
key = "let mut line = serde_json::json!({"
if src.count(key) != 1:
    raise SystemExit("games-out json anchor not found exactly once")
start = src.find(key); end = src.find("});\n", start) + len("});\n")
indent = " " * (start - src.rfind("\n", 0, start) - 1)
src = src[:end] + (f"{indent}line[\"reach_barrier\"] = serde_json::json!(r.reach_barrier);\n"
                   f"{indent}line[\"reach_turn\"] = serde_json::json!(r.reach_turn);\n") + src[end:]
if crlf:
    src = src.replace("\n", "\r\n")
open(path, "wb").write(src.encode("utf-8"))
print("patched the json line")
