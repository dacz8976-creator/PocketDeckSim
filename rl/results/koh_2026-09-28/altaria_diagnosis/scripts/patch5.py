import sys
E = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria/code/eng/engine/src"
p = E + "/players/value_functions.rs"
src = open(p, encoding="utf-8").read()
if "B_FREE_ONLY" in src:
    print("already patched 5")
else:
    anchor = "    pub static WAIVE_READY: std::cell::Cell<bool> = std::cell::Cell::new(false);\n"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "    pub static B_FREE_ONLY: std::cell::Cell<bool> = std::cell::Cell::new(false);\n    pub static B_NO_PAY: std::cell::Cell<bool> = std::cell::Cell::new(false);\n    pub static B_SPARE: std::cell::Cell<bool> = std::cell::Cell::new(false);\n" + anchor)
    anchor = "    cost <= active.attached_energy.len() && !blocked && !(attack_this_turn && state.has_retreated)\n"
    assert src.count(anchor) == 1
    new = """    let pay_ok = if B_FREE_ONLY.with(|c| c.get()) {
        cost == 0
    } else if B_NO_PAY.with(|c| c.get()) {
        true
    } else if B_SPARE.with(|c| c.get()) {
        let need = active.card.get_attacks().iter().map(|a| a.energy_required.len()).min().unwrap_or(0);
        cost <= active.attached_energy.len().saturating_sub(need)
    } else {
        cost <= active.attached_energy.len()
    };
    pay_ok && !blocked && !(attack_this_turn && state.has_retreated)
"""
    src = src.replace(anchor, new)
    open(p, "w", encoding="utf-8").write(src)
    print("patched value_functions 5")

p = E + "/altpos.rs"
s = open(p, encoding="utf-8").read()
if "fn koh_f" in s:
    print("already patched altpos")
else:
    anchor = "fn kp_s(s: &State, me: usize) -> f64 {"
    assert s.count(anchor) == 1
    add = """fn koh_f(s: &State, me: usize) -> f64 {
    vf::B_FREE_ONLY.with(|c| c.set(true));
    let v = vf::public_clock_effect_koh_value_function(s, me);
    vf::B_FREE_ONLY.with(|c| c.set(false));
    v
}
fn koh_p(s: &State, me: usize) -> f64 {\n    vf::B_SPARE.with(|c| c.set(true));\n    let v = vf::public_clock_effect_koh_value_function(s, me);\n    vf::B_SPARE.with(|c| c.set(false));\n    v\n}\nfn koh_n(s: &State, me: usize) -> f64 {
    vf::B_NO_PAY.with(|c| c.set(true));
    let v = vf::public_clock_effect_koh_value_function(s, me);
    vf::B_NO_PAY.with(|c| c.set(false));
    v
}

"""
    s = s.replace(anchor, add + anchor)
    s = s.replace('        "kohs" => koh_s,\n', '        "kohs" => koh_s,\n        "kohf" => koh_f,\n        "kohn" => koh_n,\n        "kohp" => koh_p,\n')
    open(p, "w", encoding="utf-8").write(s)
    print("patched altpos")

