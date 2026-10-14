cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
git log --oneline -5 -- rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs
echo ----
git show 28df6315:rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs | grep -n "with_remaining_hp\|active_stadium = \|set_board\|refresh"
echo ----
git diff --stat 28df6315 -- rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs
echo ---- engine refresh callers context
grep -n "refresh_hp_bonuses_all" -B6 engine/src/state/energy.rs | head -30
grep -n "fn " engine/src/actions/apply_action.rs | awk -F: '$1<1300 && $1>1250'
sed -n 1285,1300p engine/src/actions/apply_action.rs
