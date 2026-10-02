#!/usr/bin/env python3
"""Print-only patch for the pause-games harness, on the scratch copy of the pinned engine: the 8c score-dump patch (dg_patch.py, unchanged)
plus a pub fn pg_label (a compact name for an action) used in the dump lines, so the harness and the dump speak the same labels.
No behaviour change. Usage: pgd_patch.py <engine dir>"""
import sys, runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
runpy.run_path(str(HERE / "dg_patch.py"), run_name="__main__")

p = Path(sys.argv[1]) / "src/players/expectiminimax_player.rs"
b = p.read_bytes()
eol = b"\r\n" if b"\r\n" in b else b"\n"
L = lambda s: s.replace("\n", eol.decode()).encode()


def sub(b, old, new):
    assert b.count(old) == 1, f"anchor count {b.count(old)} for {old[:70]!r}"
    return b.replace(old, new)


b = sub(b, b'eprintln!("PGDUMP   {:>24.15} {:?}", s, a.action);', b'eprintln!("PGDUMP   {:>24.15} {}", s, pg_label(a));')
b = sub(b, b'eprintln!("PGCAND {:?}", action.action);', b'eprintln!("PGCAND {}", pg_label(action));')
b = sub(b, b'"PGTREE {:indent$}A {:?} value={:.6}{}", "", n.action.action, n.value,', b'"PGTREE {:indent$}A {} value={:.6}{}", "", pg_label(&n.action), n.value,')
label_fn = L('''/// Compact action name (print-only, for the pause-games harness): e.g. Play:Misty, Evolve:Mega Sharpedo ex@0, Attach:1Water@1 zone, Attack:Turbo Shark.
pub fn pg_label(a: &Action) -> String {
    let nm = |c: &crate::models::Card| c.get_name();
    match &a.action {
        SimpleAction::Play { trainer_card } => format!("Play:{}", trainer_card.name),
        SimpleAction::Place(card, idx) => format!("Place:{}@{}", nm(card), idx),
        SimpleAction::Evolve { evolution, in_play_idx, .. } => format!("Evolve:{}@{}", nm(evolution), in_play_idx),
        SimpleAction::UseAbility { in_play_idx } => format!("Ability@{}", in_play_idx),
        SimpleAction::Attack(at) => format!("Attack:{}", at.title),
        SimpleAction::Retreat(i) => format!("Retreat:{}", i),
        SimpleAction::Attach { attachments, is_turn_energy } => format!(
            "Attach:{}{}",
            attachments.iter().map(|(n, e, i)| format!("{}{:?}@{}", n, e, i)).collect::<Vec<_>>().join("+"),
            if *is_turn_energy { " zone" } else { " fx" }
        ),
        SimpleAction::AttachTool { in_play_idx, tool_card } => format!("Tool:{}@{}", nm(tool_card), in_play_idx),
        SimpleAction::Heal { in_play_idx, amount, .. } => format!("Heal:{}@{}", amount, in_play_idx),
        SimpleAction::Activate { player, in_play_idx } => format!("Activate:{}@{}", player, in_play_idx),
        SimpleAction::Promote { player, in_play_idx } => format!("Promote:{}@{}", player, in_play_idx),
        SimpleAction::ChooseMistyTarget { in_play_idx } => format!("MistyTarget@{}", in_play_idx),
        SimpleAction::ChooseRetreatEnergy { to_in_play_idx, .. } => format!("RetreatPay:{}", to_in_play_idx),
        SimpleAction::EndTurn => "EndTurn".to_string(),
        other => format!("{:?}", other).split(|c: char| c == ' ' || c == '{' || c == '(').next().unwrap_or("?").to_string(),
    }
}

''')
b = sub(b, b"fn chance_win_distance(", label_fn + b"fn chance_win_distance(")
p.write_bytes(b)
print("pg_label added", p)
