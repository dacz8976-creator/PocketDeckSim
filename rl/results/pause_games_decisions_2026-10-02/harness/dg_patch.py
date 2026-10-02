#!/usr/bin/env python3
"""Print-only instrumentation for the score dump (no behaviour change), in players/expectiminimax_player.rs:
  - PG_DUMP set: after the root scores are computed, print every candidate's score ("PGDUMP"), and before each candidate's evaluation a
    "PGCAND <action>" marker, and every time the search enters a pure queued attack-damage frame (the frame the bots resolve without a ply,
    :663-717) whose choices include a target that is a coin Ability Pokemon (A2 114, B3b 050, A4 080, B2 124, B2 204), "PGGATE ...".
  - PG_DUMP=tree: also each candidate's principal line ("PGTREE": the best child for the searching player, the worst for the opponent,
    every chance branch of a node up to 4).
Usage: dg_patch.py <engine dir>"""
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "src/players/expectiminimax_player.rs"
b = p.read_bytes()
eol = b"\r\n" if b"\r\n" in b else b"\n"
L = lambda s: s.replace("\n", eol.decode()).encode()


def sub(b, old, new):
    assert b.count(old) == 1, f"anchor count {b.count(old)} for {old[:60]!r}"
    return b.replace(old, new)


# 1. the scores and the principal lines
a1 = b'        trace!("Scores: {scores:?}");' + eol
b = sub(b, a1, a1 + L('''        if std::env::var_os("PG_DUMP").is_some() {
            eprintln!("PGDUMP actor={} candidates={}", myself, possible_actions.len());
            for (a, s) in possible_actions.iter().zip(scores.iter()) {
                eprintln!("PGDUMP   {:>24.15} {:?}", s, a.action);
            }
            if std::env::var("PG_DUMP").is_ok_and(|v| v == "tree") {
                for (idx, node) in root.children.iter().enumerate() {
                    eprintln!("PGTREE candidate {idx}");
                    let mut budget = 90usize;
                    pg_pv_action(node, 0, myself, &mut budget);
                }
            }
        }
'''))

# 2. a marker before each candidate's evaluation
a2 = b"            let before = OPPONENT_PLY_NODES.load(Ordering::Relaxed);" + eol
b = sub(b, a2, L('''            if std::env::var_os("PG_DUMP").is_some() {
                eprintln!("PGCAND {:?}", action.action);
            }
''') + a2)

# 3. the gate: the search enters a pure queued attack-damage frame with a coin target
a3 = b"        || queued_attack_damage_choice" + eol + b"    {" + eol
b = sub(b, a3, a3 + L('''        if queued_attack_damage_choice && std::env::var_os("PG_DUMP").is_some() {
            if let Some((frame_actor, choices)) = state.move_generation_stack.last() {
                for choice in choices {
                    if let SimpleAction::ApplyQueuedAttackDamage { attack, targets } = choice {
                        for (_, is_opp, idx) in targets {
                            let owner = if *is_opp { 1 - *frame_actor } else { *frame_actor };
                            let coin = state.in_play_pokemon[owner].get(*idx).and_then(|p| p.as_ref())
                                .is_some_and(|p| ["A2 114", "B3b 050", "A4 080", "B2 124", "B2 204"].contains(&p.card.get_id().as_str()));
                            if coin {
                                eprintln!("PGGATE queued coin-target frame: mover {} target (owner {}, slot {}) attack {:?} depth_left={}", frame_actor, owner, idx, attack.title, depth);
                            }
                        }
                    }
                }
            }
        }
'''))

# 4. the principal-line printers
helpers = L('''fn pg_pv_action(n: &DebugActionNode, depth: usize, myself: usize, budget: &mut usize) {
    if *budget == 0 { return; }
    *budget -= 1;
    eprintln!("PGTREE {:indent$}A {:?} value={:.6}{}", "", n.action.action, n.value,
        n.unpriced_reason.as_ref().map(|r| format!(" UNPRICED({r})")).unwrap_or_default(), indent = depth * 2);
    if depth >= 8 { return; }
    for s in n.children.iter().take(4) {
        pg_pv_state(s, depth + 1, myself, budget);
    }
}

fn pg_pv_state(s: &DebugStateNode, depth: usize, myself: usize, budget: &mut usize) {
    if *budget == 0 { return; }
    *budget -= 1;
    eprintln!("PGTREE {:indent$}S actor={} p={:.4} value={:.6} ({} moves)", "", s.acting_player, s.proba, s.value, s.children.len(), indent = depth * 2);
    let pick = s.children.iter().filter(|c| !c.value.is_nan()).fold(None::<&DebugActionNode>, |best, c| match best {
        None => Some(c),
        Some(b) => if (s.acting_player == myself && c.value > b.value) || (s.acting_player != myself && c.value < b.value) { Some(c) } else { Some(b) },
    });
    if let Some(c) = pick { pg_pv_action(c, depth + 1, myself, budget); }
}

''')
b = sub(b, b"fn chance_win_distance(", helpers + b"fn chance_win_distance(")
p.write_bytes(b)
print("patched", p, "eol", "CRLF" if eol == b"\r\n" else "LF")
