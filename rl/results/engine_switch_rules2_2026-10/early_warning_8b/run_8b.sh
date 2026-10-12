#!/usr/bin/env bash
# Rules switch 2, step 8b's early-warning rows (the Fable coordinator via Dustin, Oct 9, item 14), played by the cloud on
# claude/coin-prevention-round2's final engine against the official engine. The rows are Oct 1's four (pairings 32-35 of
# ../../engine_switch_rules_2026-10/pairs_8.tsv, the same seeds) and two new ones, 36 brew-07 v t-altaria and 37 brew-09 v
# t-altaria (P2's lists); seeds 23,100,000,000 + pairing x 10,000 + i, i < 40; km3 then k3, the same bot in both seats.
# The builds, each from `git archive` into its own target folder, so nothing earlier is reused:
#   old    main-8626a35's engine (the official program's source): legality_scan, vs_trace;
#   new    the candidate (NEW below): legality_scan, vs_trace;
#   watch  the candidate with both instrument_scan.py scripts (the round-2 and P2 counters): legality_scan;
#   probe  the candidate with coin_probe_v2.rs (QUEUED, CUT and P2's RETURN) and the counters' lines it includes, test-utils.
# The pinned official legality_scan (rl/engine-2026-10-02/) is also run, as the check that "old" built from source is the
# program the laptop runs. The tracer and the probe come from TOOLS (a commit of this branch); the decks from MAIN.
# Usage: run_8b.sh <work dir> <tools revision>   (then classify_8b.py with the same work dir)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
TOOLS=$2
OLD=8626a358     # main-8626a35: the official engine (rl/engine-2026-10-02/README.md)
NEW=140c0be2     # claude/coin-prevention-round2's final engine commit (P2, its off-switch, P3)
MAIN=1163ebb7    # origin/main on Oct 9: decks/, the scratch 8b lists, pairs_8.tsv and Oct 1's recorded 8b rows
ES=rl/results/engine_switch_rules_2026-10
mkdir -p "$W"
rm -f "$W"/trace_*.jsonl.gz   # classify_8b.py caches traces here; a rerun makes them again
for c in "$OLD" "$NEW" "$MAIN" "$TOOLS"; do git -C "$REPO" rev-parse --verify -q "$c^{commit}" > /dev/null || { echo "missing commit $c" >&2; exit 2; }; done
[ "$(git -C "$REPO" rev-parse "$OLD:engine")" = 38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5 ] || { echo "OLD's engine is not tree 38af8b0" >&2; exit 2; }
echo "old $OLD, new $NEW (engine tree $(git -C "$REPO" rev-parse --short "$NEW:engine")), main $MAIN, tools $(git -C "$REPO" rev-parse --short "$TOOLS")"

# The deck root (paths as pairs_8.tsv names them), and the pairs file: main's rows 32-35 and the two new rows.
rm -rf "$W/root" && mkdir -p "$W/root"
git -C "$REPO" archive "$MAIN" decks "$ES/scratch_8b" | tar -x -C "$W/root"
{ git -C "$REPO" show "$MAIN:$ES/pairs_8.tsv" | awk -F'\t' 'NR == 1 || ($1 >= 32 && $1 <= 35)'
  printf '36\trules8b\tbrew-07-hoopa-darkrai-sableye\tdecks/brews/brew-07-hoopa-darkrai-sableye.txt\taltaria\tdecks/screen/opponents/t-altaria.txt\t23100360000\t23100360039\t23100369999\n'
  printf '37\trules8b\tbrew-09-sableye-obstagoon\tdecks/brews/brew-09-sableye-obstagoon.txt\taltaria\tdecks/screen/opponents/t-altaria.txt\t23100370000\t23100370039\t23100379999\n'
} > "$HERE/pairs_8b.tsv"
(cd "$W/root" && sha256sum $(awk -F'\t' 'NR > 1 {print $4; print $6}' "$HERE/pairs_8b.tsv" | sort -u)) > "$HERE/decks_sha256.txt"
for bot in km3 k3; do git -C "$REPO" show "$MAIN:$ES/5a18d31_8b_new_$bot.jsonl" > "$W/oct1_8b_new_$bot.jsonl"; done

build() {  # <name> <commit> <features: none|test-utils> <instrument: yes|no> <examples...>
    local name=$1 rev=$2 feat=$3 instr=$4; shift 4
    rm -rf "${W:?}/$name" "$W/target_$name" && mkdir -p "$W/$name"
    git -C "$REPO" archive "$rev" engine | tar -x -C "$W/$name"
    if [ "$instr" = yes ]; then
        for s in victory_star_repair_2026-09-30 coin_prevention_repair_2026-09-30; do
            git -C "$REPO" show "$TOOLS:rl/results/$s/instrument_scan.py" > "$W/instrument_$s.py"
            python3 "$W/instrument_$s.py" "$W/$name/engine/examples/legality_scan.rs"
        done
    fi
    git -C "$REPO" show "$TOOLS:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
    git -C "$REPO" show "$TOOLS:rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs" > "$W/$name/engine/examples/coin_probe_v2.rs"
    git -C "$REPO" show "$TOOLS:rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py" > "$W/instrument_fns.py"
    python3 "$W/instrument_fns.py" --emit-fns "$W/$name/engine/examples/r2_counter_fns.rs" > /dev/null
    local flags=(--release --locked)
    [ "$feat" = test-utils ] && flags+=(--features test-utils)
    for ex in "$@"; do
        (cd "$W/$name/engine" && CARGO_TARGET_DIR="$W/target_$name" cargo build "${flags[@]}" --example "$ex" 2>&1 | grep -E "^error" || true)
        cp "$W/target_$name/release/examples/$ex" "$W/bin_${name}_$ex"
        echo "bin_${name}_$ex sha256 $(sha256sum < "$W/bin_${name}_$ex" | cut -c1-64) ($rev)"
    done
}
build old "$OLD" none no legality_scan vs_trace
build new "$NEW" none no legality_scan vs_trace
build watch "$NEW" none yes legality_scan
build probe "$NEW" test-utils no coin_probe_v2
(cd "$W/probe/engine" && "$W/bin_probe_coin_probe_v2" --selftest | tail -1)

(cd "$REPO/rl/engine-2026-10-02" && sha256sum -c SHA256SUMS --quiet) || { echo "pinned official programs: SHA256SUMS mismatch" >&2; exit 2; }
echo "pinned official programs: SHA256SUMS verify"
for bot in km3 k3; do
    for v in old new watch pinned; do
        prog="$W/bin_${v}_legality_scan"; cwd="$W/$v/engine"
        [ "$v" = pinned ] && { prog="$REPO/rl/engine-2026-10-02/legality_scan"; cwd="$W/old/engine"; }
        (cd "$cwd" && "$prog" --pairs "$HERE/pairs_8b.tsv" --root "$W/root" --seed-base 23100000000 --pairings 32,33,34,35,36,37 \
            --games 40 --bot "$bot" --games-out "$W/8b_${v}_$bot.jsonl" > "$W/page_${v}_$bot.txt" 2> "$W/stderr_${v}_$bot.txt")
        echo "8b_${v}_$bot.jsonl: $(wc -l < "$W/8b_${v}_$bot.jsonl") games"
    done
done
