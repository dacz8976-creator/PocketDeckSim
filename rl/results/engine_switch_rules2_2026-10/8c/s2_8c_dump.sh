#!/usr/bin/env bash
# Rules switch 2, step 8c, the revert check again (the laptop session, Oct 11): s2_8c_run.sh built the two score dumps on plain engine
# copies, so they printed no candidates and every game was a FAIL (process). run_revert_gates.sh (tools_8c.tsv's revert_check, blob
# 0c7c2b90) builds each dump in its own engine copy patched with b77652d6's print-only dg_patch.py (PG_DUMP prints every candidate's
# score): dump_old = 8626a35 + b77652d6's score_dump.rs, dump_new = the candidate + score_dump_round2.rs. Same lookahead games.
set -uo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules2_2026-10
S="$REPO/$REL"; T="$S/tools_8c"
W=${W:-$HOME/runs/s2_8c}; JOBS=${JOBS:-12}
NEW=08a9b3ae607c904e7df9f6e999d3f830eccc930f; TOOLS=31380294; DUMP_OLD=b77652d6
log() { echo "[$(date -u +%FT%TZ)] $*"; }
stop() { log "STOP: $*"; exit 1; }
env | grep -qE '^(DECKGYM_[A-Z0-9_]*|PDL_EQUIV_DEALS|GOLDFISH_TRACE|PG_DUMP)=' && stop "a DECKGYM_* (or PDL_EQUIV_DEALS, GOLDFISH_TRACE, PG_DUMP) variable is set"
cd "$REPO" || stop "no repository"
OLD=$(git rev-parse --verify -q 8626a358^{commit}) || stop "no official engine commit"
want() { [ "$(git rev-parse "$1")" = "$2" ] || stop "$1 is not blob $2"; }
want "$TOOLS:rl/results/coin_prevention_round2_2026-10-01/revert_switches/run_revert_gates.sh" 0c7c2b90ed2614d96e92591c4285700de77f324b
want "$TOOLS:rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs" b2553655013be462be11de81d87126af6592593d
want "$DUMP_OLD:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs" 554bf07aa0c1ce0c61b07cd55e239dbc67679fba
[ "$(git hash-object "$T/revert_8c.py")" = efe9887443497b1e3d07653d0b73755216c7453d ] || stop "revert_8c.py is not its pinned blob"
git show "$DUMP_OLD:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/dg_patch.py" > "$W/tools/dg_patch.py"
echo "dg_patch.py blob $(git hash-object "$W/tools/dg_patch.py") (b77652d6)" | tee -a "$W/out/builds.txt"
rm -f "$W/bin_old_score_dump" "$W/bin_new_score_dump" && echo "bin_old_score_dump and bin_new_score_dump removed: built unpatched (no candidates printed)" >> "$W/out/builds.txt"

dump() {  # <name> <commit> <score_dump source as commit:path>
    local name=$1 rev=$2
    rm -rf "${W:?}/$name" && mkdir -p "$W/$name"
    git archive "$rev" engine | tar -x -C "$W/$name" || stop "archive $rev"
    find "$W/$name" -type f -exec touch {} +
    python3 -B "$W/tools/dg_patch.py" "$W/$name/engine" > "$W/out/dg_patch_$name.txt" 2>&1 || stop "dg_patch.py on $name: $W/out/dg_patch_$name.txt"
    grep -rqs PG_DUMP "$W/$name/engine/src" || stop "dg_patch.py left no PG_DUMP in $name's engine"
    git show "$3" > "$W/$name/engine/examples/score_dump.rs"
    log "build $name ($rev, patched) --example score_dump"
    (cd "$W/$name/engine" && CARGO_BUILD_JOBS=$JOBS CARGO_TARGET_DIR="$W/target_$name" nice -n 19 cargo build --release --locked --example score_dump) \
        > "$W/out/build_${name}.log" 2>&1 || stop "build $name failed: $W/out/build_${name}.log"
    cp "$W/target_$name/release/examples/score_dump" "$W/bin_${name}_score_dump"
    echo "bin_${name}_score_dump sha256 $(sha256sum < "$W/bin_${name}_score_dump" | cut -c1-64) ($rev + dg_patch.py)" | tee -a "$W/out/builds.txt"
}
dump dump_old "$OLD" "$DUMP_OLD:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs"
dump dump_new "$NEW" "$TOOLS:rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs"

L="$W/out/lookahead_all.tsv"
log "the revert check: $(($(wc -l < "$L") - 1)) lookahead games"
rm -rf "$W/out/revert"
PYTHONDONTWRITEBYTECODE=1 python3 -B "$T/revert_8c.py" --lookahead "$L" --counters "$S/counters.tsv" --handoff "$W/handoff_for_classify.tsv" \
    --root "$W/root" --seed-base 23100000000 --seed-base 23300000000 --seed-base 21106000000 \
    --p-program "$W/bin_dump_new_score_dump" --p-cwd "$W/dump_new/engine" --p-sha256 "$(sha256sum < "$W/bin_dump_new_score_dump" | cut -c1-64)" \
    --official-program "$W/bin_dump_old_score_dump" --official-cwd "$W/dump_old/engine" --official-sha256 "$(sha256sum < "$W/bin_dump_old_score_dump" | cut -c1-64)" \
    --out "$W/out/revert" --jobs "$JOBS" > "$W/out/revert_output.txt" 2>&1
RV=$?
log "revert exit $RV: $(cat "$W/out/revert/revert_8c_summary.txt" 2>/dev/null || echo 'no summary')"
log "DONE 8c revert: exit $RV"
