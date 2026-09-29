import sys
E = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria/code/eng/engine/src"


def patch(path, pairs, marker):
    src = open(path, encoding="utf-8").read()
    if marker in src:
        print("already patched", path)
        return
    for old, new in pairs:
        assert src.count(old) == 1, (path, old, src.count(old))
        src = src.replace(old, new)
    open(path, "w", encoding="utf-8").write(src)
    print("patched", path)


patch(E + "/state/mod.rs", [
    ("    pub(crate) has_retreated: bool,\n", "    pub(crate) has_retreated: bool,\n    /// SCRATCH (synth): the slot that received each player's turn Zone Energy this turn (reset when that player's turn starts).\n    #[serde(skip)]\n    pub(crate) zone_attach_idx: [Option<usize>; 2],\n"),
    ("            has_retreated: false,\n", "            has_retreated: false,\n            zone_attach_idx: [None, None],\n"),
    ("        self.energy_zone[player].current = self.energy_zone[player].next.take();\n", "        self.zone_attach_idx[player] = None;\n        self.energy_zone[player].current = self.energy_zone[player].next.take();\n"),
], "zone_attach_idx")

patch(E + "/state/energy.rs", [
    ("        if attached && is_turn_energy {\n            self.energy_zone[actor].current = None;\n        }\n", "        if attached && is_turn_energy {\n            self.energy_zone[actor].current = None;\n            self.zone_attach_idx[actor] = Some(in_play_idx);\n        }\n"),
], "zone_attach_idx")

patch(E + "/actions/apply_action.rs", [
    ("    if is_free {\n        apply_activate(player, state, bench_idx);\n        return;\n    }\n", "    if is_free {\n        apply_activate(player, state, bench_idx);\n        swap_zone_marker(player, state, bench_idx);\n        return;\n    }\n"),
    ("    state.has_retreated = true;\n    apply_activate(player, state, bench_idx);\n", "    state.has_retreated = true;\n    apply_activate(player, state, bench_idx);\n    swap_zone_marker(player, state, bench_idx);\n"),
    ("fn apply_retreat(player: usize, state: &mut State, bench_idx: usize, is_free: bool) {\n", "fn swap_zone_marker(player: usize, state: &mut State, bench_idx: usize) {\n    match state.zone_attach_idx[player] {\n        Some(0) => state.zone_attach_idx[player] = Some(bench_idx),\n        Some(i) if i == bench_idx => state.zone_attach_idx[player] = Some(0),\n        _ => {}\n    }\n}\n\nfn apply_retreat(player: usize, state: &mut State, bench_idx: usize, is_free: bool) {\n"),
], "swap_zone_marker")

patch(E + "/players/value_functions.rs", [
    ("    pub static B_SPARE: std::cell::Cell<bool> = std::cell::Cell::new(false);\n", "    pub static B_SPARE: std::cell::Cell<bool> = std::cell::Cell::new(false);\n    pub static B_HELD: std::cell::Cell<bool> = std::cell::Cell::new(false);\n"),
    ("    } else if B_SPARE.with(|c| c.get()) {\n", "    } else if B_HELD.with(|c| c.get()) {\n        let fresh = if state.zone_attach_idx[owner] == Some(0) { 1 } else { 0 };\n        cost <= active.attached_energy.len().saturating_sub(fresh)\n    } else if B_SPARE.with(|c| c.get()) {\n"),
], "B_HELD")

p = E + "/altpos.rs"
s = open(p, encoding="utf-8").read()
if "fn koh_h" in s:
    print("already patched altpos")
else:
    anchor = "fn koh_n(s: &State, me: usize) -> f64 {"
    assert s.count(anchor) == 1
    add = """fn koh_h(s: &State, me: usize) -> f64 {
    vf::B_HELD.with(|c| c.set(true));
    let v = vf::public_clock_effect_koh_value_function(s, me);
    vf::B_HELD.with(|c| c.set(false));
    v
}
"""
    s = s.replace(anchor, add + anchor)
    s = s.replace('        "kohn" => koh_n,\n', '        "kohn" => koh_n,\n        "kohh" => koh_h,\n')
    open(p, "w", encoding="utf-8").write(s)
    print("patched altpos")
