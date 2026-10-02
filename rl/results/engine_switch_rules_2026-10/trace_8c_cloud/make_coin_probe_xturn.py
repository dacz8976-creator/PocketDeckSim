"""Step 8c (the cloud): writes coin_probe_xturn.rs, a SCRATCH VARIANT of R's coin_probe.rs for the by-hand traces of the
games the accepted rule leaves UNEXPLAINED. It is not the accepted probe and changes no verdict.

The one change: coin_probe's search stops at any state where the mover is not to move (`if mover != actor { return; }`),
so it never sees past the opponent's forced end of turn. The bots do: expectiminimax_player.rs (R, 630-655) resolves a
forced continuation (the move generation stack's top frame is exactly one of EndTurn, ResolveKnockoutPoints,
ResolveAttackRetaliation, ResolvePokemonCheckup, FinishPokemonCheckup, ResolveEndTurnEvolution, or the stack is empty
with end_turn_pending set) "without spending another ordinary action ply", whoever is to move, and then searches on with
the same depth (a Promote made during the opponent's turn, then that turn's forced end, then the mover's own next turn).
The variant applies exactly that test, read from the state (end_turn_pending through its serialised form, the field
being crate-private), and follows such a continuation at the same depth, over the same 12 sampled chance outcomes.
Everything else is coin_probe.rs, unchanged.
Usage: python3 make_coin_probe_xturn.py <coin_probe.rs> <out.rs>"""
import sys

src = open(sys.argv[1], encoding="utf-8").read()
EDITS = [
    ("fn explore(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found) {\n",
     """/// The bots' forced-continuation test (expectiminimax_player.rs, R, 630-655), read from the state.
fn forced_end_turn(state: &State) -> bool {
    state.turn_count > 0
        && match state.move_generation_stack.last() {
            Some((_, choices)) => matches!(choices.as_slice(), [SimpleAction::EndTurn
                | SimpleAction::ResolveKnockoutPoints { .. }
                | SimpleAction::ResolveAttackRetaliation { .. }
                | SimpleAction::ResolvePokemonCheckup
                | SimpleAction::FinishPokemonCheckup
                | SimpleAction::ResolveEndTurnEvolution { .. }]),
            None => serde_json::to_value(state).ok().and_then(|v| v.get("end_turn_pending").and_then(|b| b.as_bool()))
                .expect("State serialises end_turn_pending"),
        }
}

fn explore(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found) {
"""),
    ("""    let depth = path.len();
    let (mover, actions) = state.generate_possible_actions();
    if mover != actor {
        return;
    }
""",
     """    let depth = path.len();
    let (mover, actions) = state.generate_possible_actions();
    // XTURN: a forced continuation is resolved without a ply, as the bots resolve it, whoever is to move.
    if forced_end_turn(state) && actions.len() == 1 {
        path.push(format!("(forced) {}", short(&actions[0])));
        let saved = path.len();
        for next in successors(state, &actions[0]) {
            let mut p = path.clone();
            p.truncate(saved);
            explore_at(&next, actor, &mut p, found, depth);
        }
        path.pop();
        return;
    }
    if mover != actor {
        return;
    }
"""),
]
for old, new in EDITS:
    if src.count(old) != 1:
        sys.exit(f"anchor not found once: {old[:60]!r}")
    src = src.replace(old, new)
# The depth is the number of the mover's own moves; forced continuations are on the path for display but cost no ply.
src = src.replace("    let depth = path.len();\n", "    let depth = path.iter().filter(|m| !m.starts_with(\"(forced)\")).count();\n", 1)
src = src.replace("fn explore(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found) {\n",
                  "fn explore_at(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found, _depth: usize) {\n"
                  "    explore(state, actor, path, found)\n}\n\n"
                  "fn explore(state: &State, actor: usize, path: &mut Vec<String>, found: &mut Found) {\n", 1)
src = src.replace("//! Step 8c of the rules switch, the coin repair's side",
                  "//! XTURN VARIANT (step 8c's by-hand traces, the cloud, Oct 2; not the accepted probe; see make_coin_probe_xturn.py):\n"
                  "//! the opponent's forced continuations are resolved without a ply, as the bots resolve them.\n"
                  "//! Step 8c of the rules switch, the coin repair's side", 1)
open(sys.argv[2], "w", encoding="utf-8").write(src)
print("wrote", sys.argv[2])
