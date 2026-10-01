#!/usr/bin/env bash
# F8 (Oct 1): the ported Lilligant test on d363ba8's engine, then under three planted faults, then
# upstream's own test at ca4b67f (09e964f's parent, before fix 1) and at 09e964f (with it).
# Everything runs in scratch copies under <work dir>; nothing in the repository changes.
# Usage: run_f8.sh <work dir> <clone of bcollazo/deckgym-core holding ca4b67f and 09e964f>
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
UP=$2
mkdir -p "$W"

# A fresh d363ba8 engine/ with the ported test in tests/.
fork_copy() {
    rm -rf "$W/fork"
    mkdir -p "$W/fork"
    git -C "$REPO" archive d363ba8 engine | tar -x -C "$W/fork"
    cp "$HERE/hp_aura_promotion_test.rs" "$W/fork/engine/tests/"
    fresh "$W/fork/engine"
}

# git archive stamps every file with the commit's time, older than any earlier build in a shared
# target directory, so cargo would reuse that build. Stamp the copy now to force a rebuild.
fresh() {
    find "$1" -type f -exec touch {} +
}

# Replace one exact, unique piece of apply_action_helpers.rs in the scratch copy.
plant() {
    python3 - "$W/fork/engine/src/actions/apply_action_helpers.rs" "$1" "$2" <<'EOF'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path, encoding="utf-8").read()
assert text.count(old) == 1, f"expected one match for {old!r}, found {text.count(old)}"
open(path, "w", encoding="utf-8").write(text.replace(old, new))
EOF
}

run() {  # <label> <crate dir> <target dir>
    echo "== $1"
    (cd "$2" && CARGO_TARGET_DIR="$3" cargo test --release --features test-utils \
        --test hp_aura_promotion_test 2>&1) |
        grep -E "Compiling deckgym|^test |^test result|panicked at|^  left|^ right|^assertion|^thread" |
        sed -e 's/finished in [0-9.]*s/finished/' -e 's/ (\/.*)$//' -e 's/^ *Compiling/compiled/'
    echo "exit status ${PIPESTATUS[0]}"
}

WAVE_END='        knockouts.extend(wave);
    }'
NESTED='    if !get_knocked_out(state).is_empty() {
        handle_knockouts(state, attacking_ref, false);'
PRUNE='        prune_stale_bench_activate_choices(state);'

fork_copy
echo "d363ba8 apply_action_helpers.rs sha256 $(sha256sum < "$W/fork/engine/src/actions/apply_action_helpers.rs" | cut -c1-64)"
run "fork d363ba8, as committed (expect pass)" "$W/fork/engine" "$W/target-fork"

fork_copy
plant "$WAVE_END" '        knockouts.extend(wave);
        break; // F8 fault a: one wave only
    }'
run "fault a: one knockout wave only (the nested pass at 842 still runs)" "$W/fork/engine" "$W/target-fork"

fork_copy
plant "$WAVE_END" '        knockouts.extend(wave);
        break; // F8 fault b: one wave only
    }'
plant "$NESTED" '    if false && !get_knocked_out(state).is_empty() { // F8 fault b: no nested pass
        handle_knockouts(state, attacking_ref, false);'
run "fault b: one knockout wave and no nested pass (upstream's single pass)" "$W/fork/engine" "$W/target-fork"

fork_copy
plant "$PRUNE" '        // F8 fault c: prune_stale_bench_activate_choices not called'
run "fault c: the prune at 892 not called" "$W/fork/engine" "$W/target-fork"

fork_copy
plant "$NESTED" '    if false && !get_knocked_out(state).is_empty() { // F8 fault d: no nested pass
        handle_knockouts(state, attacking_ref, false);'
run "fault d: no nested pass (the waves still run)" "$W/fork/engine" "$W/target-fork"

for rev in ca4b67f 09e964f; do
    rm -rf "$W/up_$rev"
    mkdir -p "$W/up_$rev"
    git -C "$UP" archive "$rev" | tar -x -C "$W/up_$rev"
    cp "$HERE/upstream_09e964f_hp_aura_promotion_test.rs" "$W/up_$rev/tests/hp_aura_promotion_test.rs"
    fresh "$W/up_$rev"
    run "upstream $rev, upstream's own test" "$W/up_$rev" "$W/target-up"
done
