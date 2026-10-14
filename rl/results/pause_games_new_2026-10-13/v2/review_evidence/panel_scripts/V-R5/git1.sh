cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/panel14/V-R5"
git cat-file -t cd20a97a 2>&1
git rev-parse cd20a97a^{tree} 2>&1
git cat-file -t 28df6315 2>&1
git show 28df6315:rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs > "$OUT/pg_pos_28df.rs" 2>&1
git hash-object "$OUT/pg_pos_28df.rs"
git hash-object "rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs"
diff <(git show 28df6315:rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs) "rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs" && echo SAME_AS_WORKTREE
git ls-tree -r cd20a97a --name-only | grep -E 'engine/src/(models/played_card|state/mod|state/energy|state/.*\.rs)' | head -40
