#!/usr/bin/env bash
# PLAN.md step 8c, the second independent run (Sonnet, on the laptop): fresh builds of the old engine and R, then classify_8c.py over the
# hand-off's rows (the cloud's run_8b.sh is the template). RUN IT ONLY WHEN THE LAPTOP OPUS SAYS SITTING 2 IS FINISHED: the builds and
# the traces use every core (at nice 19).
# Usage: run_8c.sh <work dir> [jobs] [extra classify_8c.py arguments, e.g. --limit 40]
# Env:   REPO (default the laptop's checkout), MAIN (default origin/main as fetched; its sha is recorded), OUT (default <work dir>/out)
set -euo pipefail
rc=0
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${REPO:-"/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"}
W=$1; JOBS=${2:-12}; shift $(( $# > 1 ? 2 : 1 )) || true
OLD=d363ba8      # main's merge commit; its engine/ equals the pinned programs' build (rl/engine-2026-09-30/README.md; engine tree 9c84fef)
R=f8cfa9c        # Sonnet's R; engine/ = ab56bf4's (tree 38af8b0), the candidate 5a18d31's engine
MAIN=${MAIN:-$(git -C "$REPO" rev-parse origin/main)}
REL=rl/results/engine_switch_rules_2026-10
OUT=${OUT:-$W/out}
mkdir -p "$W" "$OUT"
git -C "$REPO" fetch origin > /dev/null 2>&1 || true
for c in "$OLD" "$R" "$MAIN"; do git -C "$REPO" rev-parse --verify -q "$c^{commit}" > /dev/null || { echo "missing commit $c" >&2; exit 2; }; done
[ "$(git -C "$REPO" rev-parse "$R:engine")" = 38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5 ] || { echo "R's engine is not tree 38af8b0" >&2; exit 2; }
case "$(git -C "$REPO" rev-parse "$OLD:engine")" in 9c84fef*) ;; *) echo "the old engine is not tree 9c84fef" >&2; exit 2;; esac
git -C "$REPO" show "$MAIN:$REL/handoff_8c.tsv" > "$W/handoff_8c.tsv"
echo "main $MAIN; old $OLD (engine $(git -C "$REPO" rev-parse --short "$OLD:engine")); R $R (engine $(git -C "$REPO" rev-parse --short "$R:engine")); hand-off rows $(($(wc -l < "$W/handoff_8c.tsv") - 1))"

# the deck root, laid out as the repository is (the hand-off's paths), and the scan files the negative controls read
rm -rf "$W/root" "$W/scan" && mkdir -p "$W/root" "$W/scan" "$W/tools"
git -C "$REPO" archive "$MAIN" decks "$REL/carriers" "$REL/scratch_8b" | tar -x -C "$W/root"   # scratch_8b: the 8b rows' own deck lists
for bot in km3 k3; do for v in old new; do git -C "$REPO" show "$MAIN:$REL/5a18d31_8_${v}_${bot}.jsonl" > "$W/scan/5a18d31_8_${v}_${bot}.jsonl"; done; done
git -C "$REPO" show "$R:$REL/tightened_rule.py" > "$W/tools/tightened_rule.py"

build() {  # <name> <commit> <features: none|test-utils> <examples...>
    local name=$1 rev=$2 feat=$3; shift 3
    rm -rf "${W:?}/$name" "$W/target_$name" && mkdir -p "$W/$name"
    git -C "$REPO" archive "$rev" engine | tar -x -C "$W/$name"
    find "$W/$name" -type f -exec touch {} +        # git archive stamps the commit's time on every file: never let cargo reuse a stale library
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs" > "$W/$name/engine/examples/vs_probe.rs"
    git -C "$REPO" show "$R:$REL/coin_probe.rs" > "$W/$name/engine/examples/coin_probe.rs"
    local flags=(--release --locked)
    [ "$feat" = test-utils ] && flags+=(--features test-utils)
    for ex in "$@"; do
        (cd "$W/$name/engine" && CARGO_BUILD_JOBS=$JOBS CARGO_TARGET_DIR="$W/target_$name" nice -n 19 cargo build "${flags[@]}" --example "$ex" 2>&1 | grep -E "^error" || true)
        cp "$W/target_$name/release/examples/$ex" "$W/bin_${name}_$ex"
        echo "bin_${name}_$ex sha256 $(sha256sum < "$W/bin_${name}_$ex" | cut -c1-64) ($rev)"
    done
}
{
    build old "$OLD" none vs_trace
    build new "$R" none vs_trace vs_probe
    build probe "$R" test-utils coin_probe
} | tee "$OUT/builds.txt"
sha256sum "$W/handoff_8c.tsv" "$W/tools/tightened_rule.py" "$HERE/classify_8c.py" | sed "s#$W/##" | tee -a "$OUT/builds.txt"

PYTHONDONTWRITEBYTECODE=1 python3 -B "$HERE/classify_8c.py" --work "$W" --tsv "$W/handoff_8c.tsv" --out "$OUT" --steps 8,8b --jobs "$JOBS" \
    --controls-from "$W/scan" "$@" | tee "$OUT/classify_output.txt" || rc=$?

# the 8b cross-check: the cloud's classification of the same 63 games (3a107f4) must agree row for row; a disagreement is a stop
CLOUD=3a107f4
if git -C "$REPO" rev-parse --verify -q "$CLOUD^{commit}" > /dev/null; then
    git -C "$REPO" show "$CLOUD:$REL/early_warning_8b/classify_output.txt" > "$W/cloud_8b_classify_output.txt"
    python3 -B "$HERE/compare_8b.py" "$OUT/verdicts.tsv" "$W/cloud_8b_classify_output.txt" "$OUT/compare_8b.txt" || rc=$?
else
    echo "cloud commit $CLOUD not available: the 8b cross-check was NOT run" | tee "$OUT/compare_8b.txt"; rc=3
fi
exit "${rc:-0}"
