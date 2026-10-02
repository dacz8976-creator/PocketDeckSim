// Appended to engine/src/players/value_functions.rs in the scratch copy of build B's engine/ that builds
// km_diag_trace (not in B; B is unchanged). kt's clocks from `myself`'s view as the public codes evaluate them
// (public evaluation, effect-aware, no reserve), under KTA and under KM: ((mine, theirs), (mine, theirs)).

/// Diagnostic helper (scratch copy only, not in build B).
pub fn km_diag_clocks(state: &State, myself: usize) -> ((f64, f64), (f64, f64)) {
    (kt_clocks(state, myself, true, true, false, EvalFeatures::KTA), kt_clocks(state, myself, true, true, false, EvalFeatures::KM))
}
