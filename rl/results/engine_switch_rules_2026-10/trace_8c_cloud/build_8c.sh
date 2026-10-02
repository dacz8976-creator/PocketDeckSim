#!/usr/bin/env bash
# Step 8c of the rules switch (the cloud, Oct 1-2): the programs and the deck root for tracing every changed game of
# step 8's hand-off (main 1ba07d9, handoff_8c.tsv). Each program is built from `git archive` in a fresh target folder.
#   old:   vs_trace on main d363ba8's engine/ (rl/engine-2026-09-30's source, tree 9c84fef)
#   new:   vs_trace and vs_probe on R f8cfa9c's engine/ (tree 38af8b0, the candidate 5a18d31's)
#   probe: coin_probe on R's engine/ with --features test-utils (coin_probe.rs's own build line)
# The tracer and probes are R's files (the candidate's: main lacks vs_trace.rs, vs_probe.rs and tightened_rule.py, so
# the candidate's copies are R's; coin_probe.rs is the same blob on main and R). The deck root holds main 1ba07d9's
# decks/ and this folder's carriers/ and scratch_8b/, the paths the hand-off rows name; trace_8c.py checks every row's
# held_blob and panel_blob against them.
# Usage: build_8c.sh <work dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
OLD=d363ba8; R=f8cfa9c; MAIN=1ba07d9
REL=rl/results/engine_switch_rules_2026-10
for c in "$OLD" "$R" "$MAIN"; do git -C "$REPO" rev-parse --verify -q "$c^{commit}" > /dev/null || { echo "missing commit $c" >&2; exit 2; }; done
[ "$(git -C "$REPO" rev-parse "$OLD:engine")" = "$(git -C "$REPO" rev-parse 9c84fef^{tree})" ] || { echo "old engine is not tree 9c84fef" >&2; exit 2; }
[ "$(git -C "$REPO" rev-parse "$R:engine")" = 38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5 ] || { echo "R's engine is not tree 38af8b0" >&2; exit 2; }
mkdir -p "$W"

rm -rf "$W/root" && mkdir -p "$W/root"
git -C "$REPO" archive "$MAIN" decks "$REL/carriers" "$REL/scratch_8b" | tar -x -C "$W/root"
git -C "$REPO" show "$MAIN:$REL/handoff_8c.tsv" > "$W/handoff_8c.tsv"
git -C "$REPO" show "$MAIN:$REL/pairs_8.tsv" > "$W/pairs_8.tsv"
mkdir -p "$W/tools"
git -C "$REPO" show "$R:$REL/tightened_rule.py" > "$W/tools/tightened_rule.py"
echo "handoff_8c.tsv sha256 $(sha256sum < "$W/handoff_8c.tsv" | cut -c1-64) (main $MAIN); tightened_rule.py blob $(git -C "$REPO" rev-parse "$R:$REL/tightened_rule.py")"

build() {  # <name> <commit> <features: none|test-utils> <examples...>
    local name=$1 rev=$2 feat=$3; shift 3
    rm -rf "${W:?}/$name" "$W/target_$name" && mkdir -p "$W/$name"
    git -C "$REPO" archive "$rev" engine | tar -x -C "$W/$name"
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs" > "$W/$name/engine/examples/vs_probe.rs"
    git -C "$REPO" show "$R:$REL/coin_probe.rs" > "$W/$name/engine/examples/coin_probe.rs"
    local flags=(--release --locked)
    [ "$feat" = test-utils ] && flags+=(--features test-utils)
    for ex in "$@"; do
        (cd "$W/$name/engine" && CARGO_TARGET_DIR="$W/target_$name" cargo build "${flags[@]}" --example "$ex" 2>&1 | grep -E "^error" || true)
        cp "$W/target_$name/release/examples/$ex" "$W/bin_${name}_$ex"
        echo "bin_${name}_$ex sha256 $(sha256sum < "$W/bin_${name}_$ex" | cut -c1-64) ($rev)"
    done
}
build old "$OLD" none vs_trace
build new "$R" none vs_trace vs_probe
build probe "$R" test-utils coin_probe
for f in vs_trace.rs vs_probe.rs; do echo "$f blob $(git -C "$REPO" rev-parse "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/$f")"; done
echo "coin_probe.rs blob $(git -C "$REPO" rev-parse "$R:$REL/coin_probe.rs") (main: $(git -C "$REPO" rev-parse "$MAIN:$REL/coin_probe.rs"))"
