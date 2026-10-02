#!/usr/bin/env bash
# VAR2 = VAR (R with the queued coin-target form switchable back to ApplyDamage) + the finite-cut order switchable back to before-modifiers.
# Its own dir and target dir (a copy of VAR's), so the programs a running check uses are not touched. Usage: dg_var2.sh [jobs, default 4]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/c8c/dg; J=${1:-4}
if [ ! -d "$D/var2" ]; then
    cp -a "$D/var" "$D/var2"
    [ -d "$D/target_var2" ] || cp -a "$D/target_var" "$D/target_var2"
    python3 -B "$HERE/dg_var2.py" "$D/var2/engine"
fi
cp "$HERE/score_dump.rs" "$D/var2/engine/examples/score_dump.rs"
touch "$D/var2/engine/examples/score_dump.rs" "$D/var2/engine/src/actions/attack_outcome.rs"
( cd "$D/var2/engine" && CARGO_BUILD_JOBS=$J CARGO_TARGET_DIR="$D/target_var2" nice -n 19 cargo build --release --locked --example score_dump 2>&1 | grep -E "^error" -A8 | head -30 || true )
cp "$D/target_var2/release/examples/score_dump" "$D/score_dump_var2"
echo "score_dump_var2 $(sha256sum < "$D/score_dump_var2" | cut -c1-64)"
