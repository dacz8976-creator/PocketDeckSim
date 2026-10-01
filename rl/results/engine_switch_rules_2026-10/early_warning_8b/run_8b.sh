#!/usr/bin/env bash
# PLAN.md step 8b's early-warning rows (the Fable coordinator via Dustin, Oct 1 morning), on the cloud's scratch build of
# R. Pairings 32-35 of the 23.1B block (pairs_8.tsv as sitting2_check.py pairs8 writes it), i < 40, seeds
# 23,100,000,000 + pairing x 10,000 + i; km3 then k3; each on the old engine (rl/engine-2026-09-30's source: main
# d363ba8's engine/), the new one (R, f8cfa9c; its engine/ is ab56bf4's, tree 38af8b0, the laptop's candidate's) and
# the watch build (R with both instrument_scan.py scripts, R's version). Every program is built from `git archive` in
# a fresh target folder, so no earlier build can be reused. The pinned old legality_scan (rl/engine-2026-09-30/) is also
# run, as a check that the old rows built from source are the program the laptop runs.
# Usage: run_8b.sh <work dir>   (then classify_8b.py, with the same work dir)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
OLD=d363ba8      # main's merge commit; its engine/ equals the pinned programs' build (rl/engine-2026-09-30/README.md)
R=f8cfa9c        # Sonnet's R; engine/ = ab56bf4's (tree 38af8b0)
MAIN=38e1c566    # main with sitting2.sh and its helpers (pairs8, touched, stepsum)
CARRIERS=e0d149a # the carrier lists' commit (sitting2.sh's 8-seeds takes them from here)
REL=rl/results/engine_switch_rules_2026-10
mkdir -p "$W"
for c in "$OLD" "$R" "$MAIN" "$CARRIERS"; do git -C "$REPO" rev-parse --verify -q "$c^{commit}" > /dev/null || { echo "missing commit $c" >&2; exit 2; }; done
[ "$(git -C "$REPO" rev-parse "$R:engine")" = 38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5 ] || { echo "R's engine is not tree 38af8b0" >&2; exit 2; }

# The deck root, laid out as the laptop's repository is when sitting 2 plays 8b (paths as pairs_8.tsv names them).
rm -rf "$W/root" && mkdir -p "$W/root/$REL/scratch_8b"
git -C "$REPO" archive "$MAIN" decks | tar -x -C "$W/root"
git -C "$REPO" archive "$CARRIERS" "$REL/carriers" | tar -x -C "$W/root"
for f in victory_star_repair_2026-09-30/smoke/fire_victini.txt victory_star_repair_2026-09-30/smoke/psychic_confuse.txt \
         coin_prevention_repair_2026-09-30/smoke/fire_heatmor.txt coin_prevention_repair_2026-09-30/smoke/meowth_carefree.txt; do
    git -C "$REPO" show "$R:rl/results/$f" > "$W/root/$REL/scratch_8b/$(basename "$f")"
done
mkdir -p "$W/tools"
for f in sitting1_check.py sitting2_check.py switch_check.py; do git -C "$REPO" show "$MAIN:$REL/$f" > "$W/tools/$f"; done
git -C "$REPO" show "$R:$REL/tightened_rule.py" > "$W/tools/tightened_rule.py"   # classify_8b.py imports it
python3 "$W/tools/sitting2_check.py" pairs8 --repo "$W/root" --out "$HERE/pairs_8.tsv" --seeds-out "$HERE/seeds_8.txt"

build() {  # <name> <commit> <features: none|test-utils> <instrument: yes|no> <examples...>
    local name=$1 rev=$2 feat=$3 instr=$4; shift 4
    rm -rf "${W:?}/$name" "$W/target_$name" && mkdir -p "$W/$name"
    git -C "$REPO" archive "$rev" engine | tar -x -C "$W/$name"
    if [ "$instr" = yes ]; then
        for s in victory_star_repair_2026-09-30 coin_prevention_repair_2026-09-30; do
            git -C "$REPO" show "$R:rl/results/$s/instrument_scan.py" > "$W/instrument_$s.py"
            python3 "$W/instrument_$s.py" "$W/$name/engine/examples/legality_scan.rs"
        done
    fi
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
    git -C "$REPO" show "$R:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_probe.rs" > "$W/$name/engine/examples/vs_probe.rs"
    git -C "$REPO" show "$R:$REL/coin_probe.rs" > "$W/$name/engine/examples/coin_probe.rs"
    local flags=(--release --locked)
    [ "$feat" = test-utils ] && flags+=(--features test-utils)
    for ex in "$@"; do
        (cd "$W/$name/engine" && CARGO_TARGET_DIR="$W/target_$name" cargo build "${flags[@]}" --example "$ex" 2>&1 | grep -E "^error|warning: unused" || true)
        cp "$W/target_$name/release/examples/$ex" "$W/bin_${name}_$ex"
        echo "bin_${name}_$ex sha256 $(sha256sum < "$W/bin_${name}_$ex" | cut -c1-64) ($rev)"
    done
}
build old "$OLD" none no legality_scan vs_trace
build new "$R" none no legality_scan vs_trace vs_probe
build watch "$R" none yes legality_scan
build probe "$R" test-utils no coin_probe

(cd "$REPO/rl/engine-2026-09-30" && sha256sum -c SHA256SUMS --quiet) && echo "pinned old programs: SHA256SUMS verify"
for bot in km3 k3; do
    for v in old new watch pinned; do
        prog="$W/bin_${v}_legality_scan"; cwd="$W/$v/engine"
        [ "$v" = pinned ] && { prog="$REPO/rl/engine-2026-09-30/legality_scan"; cwd="$W/old/engine"; }
        (cd "$cwd" && "$prog" --pairs "$HERE/pairs_8.tsv" --root "$W/root" --seed-base 23100000000 --pairings 32,33,34,35 \
            --games 40 --bot "$bot" --games-out "$W/8b_${v}_$bot.jsonl" > "$W/page_${v}_$bot.txt" 2> "$W/stderr_${v}_$bot.txt")
        echo "8b_${v}_$bot.jsonl: $(wc -l < "$W/8b_${v}_$bot.jsonl") games"
    done
done
