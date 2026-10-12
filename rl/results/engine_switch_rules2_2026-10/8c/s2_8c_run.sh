#!/usr/bin/env bash
# Rules switch 2, step 8c (the laptop session, Oct 11): the builds tools_8c/README.md's order needs, the hand-off adapter,
# classify_8c.py once per seed block (its trace cache and its (bot, pairing, i) keys are per run, and step 9's pairings 32-39
# share numbers with 8b's 32-37), then revert_8c.py over every lookahead game. Every tool at its pinned blob (tools_8c.tsv,
# handoff_8c.md); the official score dump is run_revert_gates.sh's (b77652d6's score_dump.rs on 8626a35). Nothing is committed
# here: the laptop session reads the outputs first. Re-running skips finished builds and reuses classify's trace cache.
# Usage: launch_detached.sh start s2-8c -- bash ~/runs/s2_8c_run.sh      Env: W (default ~/runs/s2_8c), JOBS (default 12)
set -uo pipefail
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REL=rl/results/engine_switch_rules2_2026-10
S="$REPO/$REL"; T="$S/tools_8c"
W=${W:-$HOME/runs/s2_8c}; JOBS=${JOBS:-12}
NEW=08a9b3ae607c904e7df9f6e999d3f830eccc930f
TOOLS=31380294; DUMP_OLD=b77652d6
log() { echo "[$(date -u +%FT%TZ)] $*"; }
stop() { log "STOP: $*"; exit 1; }

env | grep -qE '^(DECKGYM_[A-Z0-9_]*|PDL_EQUIV_DEALS|GOLDFISH_TRACE|PG_DUMP)=' && stop "a DECKGYM_* (or PDL_EQUIV_DEALS, GOLDFISH_TRACE, PG_DUMP) variable is set"
cd "$REPO" || stop "no repository"
OLD=$(git rev-parse --verify -q 8626a358^{commit}) || stop "no official engine commit"
[ "$(git rev-parse "$OLD:engine")" = "$(git rev-parse "$DUMP_OLD:engine")" ] || stop "the official engine's tree is not b77652d6's"
case "$(git rev-parse "$OLD:engine")" in 38af8b0*) ;; *) stop "the official engine is not tree 38af8b0";; esac
[ "$(git rev-parse "$NEW:engine")" = 70652fff03af511e32a169e16209e158a998dda6 ] || stop "the candidate's engine is not P's tree 70652ff"
want() { [ "$(git rev-parse "$1")" = "$2" ] || stop "$1 is not blob $2"; }
want "$TOOLS:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" 3fbc20d27e656d7134666bb54d0cbfdc8458fa51
want "$TOOLS:rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs" 318578349f3e138ccac2e23a32f413d5948ce5ff
want "$TOOLS:rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs" b2553655013be462be11de81d87126af6592593d
want "$DUMP_OLD:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs" 554bf07aa0c1ce0c61b07cd55e239dbc67679fba
wantf() { [ "$(git hash-object "$1")" = "$2" ] || stop "$1 is not blob $2"; }
wantf "$T/tightened_rule.py" 6b6a83649f4299af974c1b8a0dc4900b3e27f011
wantf "$T/classify_8c.py" b344367d5f85fa7512274edc7d85d9926c48eff0
wantf "$T/coin_lookahead.py" 76de39128667a03d72a6a9ca3aa155e3cc175f16
wantf "$T/revert_8c.py" efe9887443497b1e3d07653d0b73755216c7453d
wantf "$T/handoff_for_classify.py" cf8dcfb4729210525734ce167de6d7051f8d54ef
git diff --quiet HEAD -- "$REL/handoff_8c.tsv" "$REL/counters.tsv" || stop "handoff_8c.tsv or counters.tsv differs from its commit"
MAIN=$(git rev-parse HEAD)
mkdir -p "$W/out" "$W/tools"
log "main $MAIN; official $OLD (engine 38af8b0); candidate $NEW (engine 70652ff); W $W; jobs $JOBS"

# ---- builds (each its own engine copy and target folder; skipped when done) ----
build() {  # <name> <commit> <none|test-utils> <example>...
    local name=$1 rev=$2 feat=$3; shift 3
    rm -rf "${W:?}/$name" && mkdir -p "$W/$name"
    git archive "$rev" engine | tar -x -C "$W/$name" || stop "archive $rev"
    find "$W/$name" -type f -exec touch {} +
    case $name in
      old)   git show "$TOOLS:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
             git show "$DUMP_OLD:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs" > "$W/$name/engine/examples/score_dump.rs";;
      new)   git show "$TOOLS:rl/results/victory_star_repair_2026-09-30/smoke/rerun_R/vs_trace.rs" > "$W/$name/engine/examples/vs_trace.rs"
             git show "$TOOLS:rl/results/coin_prevention_round2_2026-10-01/revert_switches/score_dump_round2.rs" > "$W/$name/engine/examples/score_dump.rs";;
      probe) git show "$TOOLS:rl/results/round2_readiness_2026-10-02/coin_probe_v2.rs" > "$W/$name/engine/examples/coin_probe_v2.rs"
             # the probe include!s the exact counters' lines, written by P's coin script (coin_probe_v2.rs:16-19, its build recipe)
             git show "$NEW:rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py" > "$W/tools/instrument_scan.py"
             wantf "$W/tools/instrument_scan.py" 306f1f6969af39c54bd09a164c8fab27a083c194
             (cd "$W/$name" && python3 -B "$W/tools/instrument_scan.py" --emit-fns engine/examples/r2_counter_fns.rs) > /dev/null || stop "--emit-fns"
             echo "r2_counter_fns.rs sha256 $(sha256sum < "$W/$name/engine/examples/r2_counter_fns.rs" | cut -c1-64) (instrument_scan.py --emit-fns, blob 306f1f69)" | tee -a "$W/out/builds.txt";;
    esac
    local flags=(--release --locked)
    [ "$feat" = test-utils ] && flags+=(--features test-utils)
    for ex in "$@"; do
        log "build $name ($rev) --example $ex ${flags[*]}"
        (cd "$W/$name/engine" && CARGO_BUILD_JOBS=$JOBS CARGO_TARGET_DIR="$W/target_$name" nice -n 19 cargo build "${flags[@]}" --example "$ex") \
            > "$W/out/build_${name}_$ex.log" 2>&1 || stop "build $name $ex failed: $W/out/build_${name}_$ex.log"
        cp "$W/target_$name/release/examples/$ex" "$W/bin_${name}_$ex"
        echo "bin_${name}_$ex sha256 $(sha256sum < "$W/bin_${name}_$ex" | cut -c1-64) ($rev)" | tee -a "$W/out/builds.txt"
    done
    touch "$W/.built_$name"
}
[ -f "$W/.built_old" ] || build old "$OLD" none vs_trace score_dump
[ -f "$W/.built_new" ] || build new "$NEW" none vs_trace score_dump
if [ ! -f "$W/.built_probe" ]; then
    build probe "$NEW" test-utils coin_probe_v2
    (cd "$W/probe/engine" && nice -n 19 "$W/bin_probe_coin_probe_v2" --selftest) > "$W/out/probe_selftest.txt" 2>&1 || { rm -f "$W/.built_probe"; stop "the probe's self-test failed: $W/out/probe_selftest.txt"; }
    tail -n 1 "$W/out/probe_selftest.txt" | tee -a "$W/out/builds.txt"
fi
log "builds: $(grep -c sha256 "$W/out/builds.txt") programs; $(tail -n 1 "$W/out/probe_selftest.txt")"

# ---- the decks (the hand-off's paths, from main), the round-2 coin script, the adapter, the split by seed block ----
rm -rf "$W/root" && mkdir -p "$W/root"
git archive HEAD decks rl/results/engine_switch_rules_2026-10/scratch_8b "$REL/scratch_8b2" rl/results/engine_switch_rules_2026-10/carriers/alternates \
    rl/results/kt_carrier_census_2026-09-26/decks rl/results/b2e_card_check_2026-09-26/decks | tar -x -C "$W/root" || stop "the deck archive"
git show "$NEW:rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py" > "$W/tools/instrument_scan.py"
wantf "$W/tools/instrument_scan.py" 306f1f6969af39c54bd09a164c8fab27a083c194
rm -f "$W/handoff_for_classify.tsv"
python3 -B "$T/handoff_for_classify.py" --in "$S/handoff_8c.tsv" --out "$W/handoff_for_classify.tsv" || stop "the hand-off adapter refused"
rm -rf "$W/split" && mkdir -p "$W/split"
python3 -B - "$W/handoff_for_classify.tsv" "$W/split" <<'EOF' || stop "the split"
import sys
src, out = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8", newline="").read().split("\n")
head, body = lines[0], [l for l in lines[1:] if l]
cols = head.split("\t"); ix = {c: cols.index(c) for c in ("step", "pairing", "i", "seed")}
parts = {"A": [], "B": [], "C": []}
for l in body:
    f = l.split("\t")
    base = int(f[ix["seed"]]) - int(f[ix["pairing"]]) * 10000 - int(f[ix["i"]])
    name = {("8b", 23100000000): "A", ("8b", 23300000000): "B", ("9", 21106000000): "C"}.get((f[ix["step"]], base))
    if name is None:
        sys.exit(f"a row of no known block: step {f[ix['step']]}, base {base}")
    parts[name].append(l)
for k, v in parts.items():
    open(f"{out}/{k}.tsv", "w", encoding="utf-8", newline="").write(head + "\n" + "".join(x + "\n" for x in v))
    print(f"split {k}: {len(v)} rows")
print(f"total {sum(map(len, parts.values()))} of {len(body)}")
EOF
mkdir -p "$W/controls9"
ln -sfn "$REPO/rl/results/km_tables_2026-09-30/1f6319e_b2e_km3.jsonl" "$W/controls9/s9_old_km3.jsonl"
ln -sfn "$S/08a9b3a_cov_b2e_km3.jsonl" "$W/controls9/s9_new_km3.jsonl"
sha256sum "$W/handoff_for_classify.tsv" "$W/split/"*.tsv "$S/handoff_8c.tsv" | sed "s#$W/##; s#$REPO/##" | tee "$W/out/inputs.sha256"

# ---- classify_8c.py per seed block ----
declare -A RC
classify() {  # <name> <steps> <seed base> <controls dir> <controls tag>
    local n=$1 WX="$W/run_$1" O="$W/out/classify_$1"
    mkdir -p "$WX" "$O"
    for x in root old new probe bin_old_vs_trace bin_new_vs_trace bin_probe_coin_probe_v2; do ln -sfn "$W/$x" "$WX/$x"; done
    log "classify $n: steps $2, seed base $3, controls $5"
    PYTHONDONTWRITEBYTECODE=1 python3 -B "$T/classify_8c.py" --work "$WX" --tsv "$W/split/$n.tsv" --out "$O" --steps "$2" --jobs "$JOBS" \
        --seed-base "$3" --controls-from "$4" --controls-tag "$5" --instrument "$W/tools/instrument_scan.py" > "$O/output.txt" 2>&1
    RC[$n]=$?
    log "classify $n exit ${RC[$n]}: $(grep -E '"tally"' -A0 "$O/output.txt" | head -1) lookahead $(($(wc -l < "$O/lookahead.tsv" 2>/dev/null || echo 1) - 1))"
}
classify A 8b 23100000000 "$S" 08a9b3a_8b_cloud
classify B 8b 23300000000 "$S" 08a9b3a_8b_new2
classify C 9 21106000000 "$W/controls9" s9

# ---- revert_8c.py over every lookahead game ----
L="$W/out/lookahead_all.tsv"
{ head -n 1 "$W/out/classify_A/lookahead.tsv"; for n in A B C; do tail -n +2 "$W/out/classify_$n/lookahead.tsv"; done; } > "$L"
log "lookahead games for the revert check: $(($(wc -l < "$L") - 1))"
rm -rf "$W/out/revert"
PYTHONDONTWRITEBYTECODE=1 python3 -B "$T/revert_8c.py" --lookahead "$L" --counters "$S/counters.tsv" --handoff "$W/handoff_for_classify.tsv" \
    --root "$W/root" --seed-base 23100000000 --seed-base 23300000000 --seed-base 21106000000 \
    --p-program "$W/bin_new_score_dump" --p-cwd "$W/new/engine" --p-sha256 "$(sha256sum < "$W/bin_new_score_dump" | cut -c1-64)" \
    --official-program "$W/bin_old_score_dump" --official-cwd "$W/old/engine" --official-sha256 "$(sha256sum < "$W/bin_old_score_dump" | cut -c1-64)" \
    --out "$W/out/revert" --jobs "$JOBS" > "$W/out/revert_output.txt" 2>&1
RV=$?
log "revert exit $RV: $(cat "$W/out/revert/revert_8c_summary.txt" 2>/dev/null || echo 'no summary')"
log "DONE 8c run: classify A ${RC[A]} B ${RC[B]} C ${RC[C]}, revert $RV (main $MAIN)"
