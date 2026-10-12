"""P2 smoke (Oct 8): adds a per-tick trace to a copy of legality_scan.rs, for the look-ahead check (first_difference.py). With
P2_TRACE="pairing:i,..." set, the scan writes one TRACE line to stderr per tick of those games: the turn, the mover, the chosen
move, and each side's board after it (points; each in-play Pokemon's id, HP, Energy and stored effects; hand; deck and discard
sizes). Without P2_TRACE it plays and writes exactly as before. Usage: python3 trace_patch.py <copy of legality_scan.rs>"""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8", newline="").read()
old = """        let after = game.get_state_clone();
        update_turn(&mut turn, &before, &after, chosen.actor, &chosen);"""
new = """        let after = game.get_state_clone();
        if std::env::var("P2_TRACE").map_or(false, |t| t.split(',').any(|x| x == format!("{pairing}:{i}"))) {
            let side = |s: &State, q: usize| {
                let slots: Vec<String> = s.in_play_pokemon[q].iter().map(|x| x.as_ref().map_or("-".to_string(), |p| format!(
                    "{} {} {:?} {:?}", p.card.get_id(), p.get_remaining_hp(), p.attached_energy, serde_json::to_value(p).map(|v| v["effects"].clone()).unwrap_or_default()))).collect();
                let mut hand: Vec<String> = s.hands[q].iter().map(|c| c.get_id()).collect();
                hand.sort();
                format!("pts {} | {} | hand {:?} | deck {} | discard {}", s.points[q], slots.join(" ; "), hand, s.decks[q].cards.len(), s.discard_piles[q].len())
            };
            eprintln!("TRACE {pairing}:{i} turn {} actor {} chose {:?} || {} || {}", before.turn_count, chosen.actor, chosen.action, side(&after, 0), side(&after, 1));
        }
        update_turn(&mut turn, &before, &after, chosen.actor, &chosen);"""
assert s.count(old) == 1, "anchor not found once"
open(p, "w", encoding="utf-8", newline="").write(s.replace(old, new))
print("patched", p)
