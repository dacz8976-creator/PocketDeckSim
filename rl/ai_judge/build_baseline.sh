#!/bin/bash
# Rebuild pg_pos (the step-bot position player) with the target-preserving baseline printer, from THIS checkout's engine tree.
# Serial, low priority, never beside another cargo. Run from anywhere inside the repository.
#   bash rl/ai_judge/build_baseline.sh        -> ~/ai_judge_pgpos/bin/pg_pos_target_preserving, and the identity lines FROZEN.json records
if pgrep -x cargo > /dev/null; then echo "another cargo is running; not building"; pgrep -a cargo | cut -c1-120; exit 3; fi
source ~/.cargo/env 2>/dev/null
set -e
cd "$(git rev-parse --show-toplevel)"
H=rl/results/pause_games_decisions_2026-10-02/harness
W=${AI_JUDGE_PGPOS:-$HOME/ai_judge_pgpos}
rm -rf "$W/src" && mkdir -p "$W/src" "$W/bin"
git archive HEAD engine | tar -x -C "$W/src"
cp $H/pgd_patch.py $H/dg_patch.py "$W/src/"
(cd "$W/src" && python3 -B pgd_patch.py "$W/src/engine") | tail -3
mkdir -p "$W/src/engine/examples"
cp $H/pg_pos.rs "$W/src/engine/examples/pg_pos.rs"
export CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR="$W/t_pg"
(cd "$W/src/engine" && nice -n 19 cargo build --release --locked --offline --example pg_pos > "$W/build.log" 2>&1) || { echo "BUILD FAILED"; grep -E '^error' -A12 "$W/build.log" | head -50; exit 1; }
cp "$W/t_pg/release/examples/pg_pos" "$W/bin/pg_pos_target_preserving"
echo "BUILD OK"
echo "binary sha256:  $(sha256sum "$W/bin/pg_pos_target_preserving" | cut -c1-64)"
echo "engine tree:    $(git rev-parse HEAD:engine)"
echo "rustc:          $(rustc --version)"
echo "pgd_patch.py:   $(sha256sum $H/pgd_patch.py | cut -c1-64)"
echo "pg_pos.rs:      $(sha256sum $H/pg_pos.rs | cut -c1-64)"
