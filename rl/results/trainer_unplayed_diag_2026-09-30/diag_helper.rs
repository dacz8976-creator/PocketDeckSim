
/// Scratch-only (rl/results/trainer_unplayed_diag_2026-09-30; appended to a scratch copy of main-d363ba8's engine to
/// build that folder's trace program; never in a build that plays games): km<N>'s root scores at one decision,
/// computed exactly as `PublicPricingPlayer::decision_fn` computes them. That is under public pricing, from the
/// player's observation, with the same determinization seed and `rng`, one (expected value, win distance) per offered
/// action. `rng` must be seeded as the game seeds that decision.
pub fn diag_km_root_scores(
    deck: crate::Deck,
    max_depth: usize,
    rng: &mut StdRng,
    observation: &crate::observation::PlayerObservation,
    actions: &[Action],
) -> Vec<(f64, Option<usize>)> {
    let search = ExpectiMiniMaxPlayer {
        deck,
        max_depth,
        write_debug_trees: false,
        value_function: Box::new(crate::players::value_functions::public_clock_effect_km_value_function),
        opponent_ply: 0,
        consistent_horizon: false,
        soft_opponent: false,
    };
    crate::observation::with_public_pricing(|| {
        let mut observation_rng = StdRng::seed_from_u64(rng.clone().next_u64() ^ 0x50444c5f4f425331);
        let state = observation.search_state(&mut observation_rng);
        search.score_candidates(rng, &state, actions, PublicReplyProvenance::from_observation(observation))
    })
}
