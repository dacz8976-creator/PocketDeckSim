#!/usr/bin/env python3
"""VAR2's second switch, in attack_outcome.rs's `split_with_damage_prevention`: with PG_CUT_BEFORE set, a finite coin cut (Guarded Grill -100,
Securely Sheltered -80) comes off the attack's raw damage before the damage modifiers, as in the old engine (d363ba8), instead of being recorded in
`heads_coin_cuts` and taken off after Weakness. Without the variable the code is R's. Usage: dg_var2.py <engine dir>"""
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "src/actions/attack_outcome.rs"
t = p.read_bytes().decode("utf-8")
start_marker = "outcome.damage.retain(|(_, is_opponent, idx)| {"
assert t.count(start_marker) == 1, "start marker"
s = t.index(start_marker)
end_marker = ".copied(),"
e = t.index(end_marker, s)
e_close = t.index(");", e) + 2          # the `);` that closes `outcome.heads_coin_cuts.extend(`
# the line start of the retain statement, to keep the indentation
ls = t.rfind("\n", 0, s) + 1
indent = t[ls:s]
assert indent.strip() == "", repr(indent)
# the R statements from the full-prevention comment line above the retain through the extend's end
c = t.rfind("// Full prevention", ls - 200, s)
seg_start = t.rfind("\n", 0, c) + 1 if c != -1 else ls
eol = "\r\n" if "\r\n" in t[seg_start:e_close] else "\n"
r_code = t[seg_start:e_close]
old_code = (
    f"{indent}// Old order (d363ba8): a finite cut comes off the raw damage, before the damage modifiers.{eol}"
    f"{indent}outcome.damage = outcome{eol}"
    f"{indent}    .damage{eol}"
    f"{indent}    .into_iter(){eol}"
    f"{indent}    .filter_map(|(amount, is_opponent, idx)| {{{eol}"
    f"{indent}        if is_opponent {{{eol}"
    f"{indent}            if let Some((_, reduction)) = reduced_now.iter().find(|(r_idx, _)| *r_idx == idx) {{{eol}"
    f"{indent}                let reduced = amount.saturating_sub(*reduction);{eol}"
    f"{indent}                return (reduced > 0).then_some((reduced, is_opponent, idx));{eol}"
    f"{indent}            }}{eol}"
    f"{indent}        }}{eol}"
    f"{indent}        Some((amount, is_opponent, idx)){eol}"
    f"{indent}    }}){eol}"
    f"{indent}    .collect();{eol}"
)
new = (f'{indent}if std::env::var_os("PG_CUT_BEFORE").is_some() {{{eol}{old_code}{indent}}} else {{{eol}'
       + r_code + f"{eol}{indent}}}")
t = t[:seg_start] + new + t[e_close:]
p.write_bytes(t.encode("utf-8"))
print("patched", p)
