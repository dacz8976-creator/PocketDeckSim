// Appended to src/players/value_functions.rs:
/// Scratch-only probe: the opponent's clock on `myself` (km's, with C2 off and on) and its benched candidates' charges.
pub fn diag_kr_clock(state: &State, myself: usize) -> String {
    let owner = 1 - myself;
    let off = kt_clock_c2(state, myself, false, true, false, true, true, true, false);
    let on = kt_clock_c2(state, myself, false, true, false, true, true, true, true);
    let attack_damage = |atk: &Attack, slot: &PlayedCard| estimated_attack_damage_ex(atk, slot, state, owner, false).round() as u32;
    let cands = threat_candidates(state, owner, false, None, &attack_damage);
    let names: Vec<String> = cands
        .iter()
        .map(|c| {
            let name = state.in_play_pokemon[owner][c.slot].as_ref().map(|p| p.get_name()).unwrap_or_default();
            let charge = if c.slot != 0 { benched_retreat_shortfall(state, owner, c.missing) } else { 0 };
            format!("{name}@{} dmg {} missing {} +{charge}", c.slot, c.damage, c.missing)
        })
        .collect();
    let active = state.maybe_get_active(owner).map(|a| {
        format!("{} {}E board cost {} effects {:?}", a.get_name(), a.attached_energy.len(),
            crate::hooks::get_board_retreat_cost_for_player(state, owner, a).len(), a.get_effects())
    });
    format!("turn {} to move {} | their Active {:?} | off: lead {} total {} slot {:?} | on: lead {} total {} slot {:?} | {:?}",
        state.turn_count, state.current_player, active, off.lead, off.total(0.0), off.threat_slot, on.lead, on.total(0.0),
        on.threat_slot, names)
}

// Appended to src/players/expectiminimax_player.rs:
/// Scratch-only probe (never in a build that plays games): a public code's root scores at one decision, computed as
/// `PublicPricingPlayer::decision_fn` computes them, for the value function given.
pub fn diag_root_scores(
    deck: crate::Deck,
    value_function: fn(&crate::State, usize) -> f64,
    rng: &mut StdRng,
    observation: &crate::observation::PlayerObservation,
    actions: &[Action],
) -> Vec<(f64, Option<usize>)> {
    let search = ExpectiMiniMaxPlayer { deck, max_depth: 3, write_debug_trees: false, value_function: Box::new(value_function),
        opponent_ply: 0, consistent_horizon: false, soft_opponent: false };
    crate::observation::with_public_pricing(|| {
        let mut observation_rng = StdRng::seed_from_u64(rng.clone().next_u64() ^ 0x50444c5f4f425331);
        let state = observation.search_state(&mut observation_rng);
        search.score_candidates(rng, &state, actions, PublicReplyProvenance::from_observation(observation))
    })
}
