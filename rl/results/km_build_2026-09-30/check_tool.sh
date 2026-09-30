#!/usr/bin/env bash
# The counter tool's tests and its identity check at km's build B, km on kta (the km registration, step 3 and section
# 4.1, identity 8a, as Amendment 1 (c) item 4 re-bases it). The tool's source is unchanged (sha256 05d7ba41...). It and
# the version before the Sept 29 round (816fd9c's, as tool_census_old) are built as examples in a scratch copy of B's
# engine/ (git archive), so B's diff stays engine/src/players/. Usage: bash check_tool.sh (after run_km.sh's item 7,
# whose smoke file 8a uses). kta3 and km3 play only 8a's own deals (i < 40 of the 17 cells) and their rows carry no
# counts (--no-counts); the counts are read only on kp3's games: the old-output test on the table's first 20 deals and
# the traced games on diagnostic seeds 20,000,920,000 + i. Test 1's stdout and games-out and test 3's rows and trace are
# committed with their sha256 and compared with 9c11b30's (kp3 is untouched by B).
set -euo pipefail
R=/home/user/PocketDeckSim; D=$R/rl/results/km_build_2026-09-30; BUILD=1f6319e; OLDD=$R/rl/results/km_build_2026-09-29
S=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/km
E=$S/censusB/engine; NEW=$E/target/release/examples/tool_census; OLD=$E/target/release/examples/tool_census_old
W=$S/toolB; T=${THREADS:-4}; KTA=$R/rl/results/kt_tables_2026-09-28
mkdir -p "$W"
note() { echo "$(date -u +%FT%TZ) $*" >> "$D/STATUS.txt"; }
die() { note "BLOCKED: $*"; exit 1; }
cmp -s "$R/rl/results/tool_turn_effect_census_2026-09-25/tool_census.rs" "$E/examples/tool_census.rs" || die "tool source differs from the scratch copy"
[ "$(sha256sum "$E/examples/tool_census.rs" | cut -c1-64)" = 05d7ba4183ce9e3098036de9acb5181ea71f7077ef9b3798ad4e5d165dc22365 ] || die "the tool's source is not 05d7ba41.."
rm -rf "$S/censusB_ref" && mkdir -p "$S/censusB_ref" && git -C "$R" archive $BUILD engine | tar -x -C "$S/censusB_ref"
diff -rq -x target -x tool_census.rs -x tool_census_old.rs "$S/censusB_ref/engine" "$E" > /dev/null || die "the scratch engine/ is not $BUILD's"
cmp -s <(git -C "$R" show 816fd9c:rl/results/tool_turn_effect_census_2026-09-25/tool_census.rs) "$E/examples/tool_census_old.rs" || die "the old tool is not 816fd9c's"
note "tool: source sha256 $(sha256sum "$E/examples/tool_census.rs" | cut -c1-64); program sha256 $(sha256sum "$NEW" | cut -c1-64) (built in a scratch copy of $BUILD's engine/); the old tool (816fd9c's source, sha256 $(sha256sum "$E/examples/tool_census_old.rs" | cut -c1-64)) program sha256 $(sha256sum "$OLD" | cut -c1-64)"
run() { ( cd "$R/engine" && RAYON_NUM_THREADS=$T "$@" ); }

# Test 1: at the old base and lists, the new tool reproduces the old tool's output exactly (stdout, stderr, games-out).
run "$OLD" --games 20 --bot kp3 --games-out "$W/old_games.jsonl" > "$W/old_stdout.txt" 2> "$W/old_stderr.txt"
run "$NEW" --games 20 --bot kp3 --games-out "$W/new_games.jsonl" > "$W/new_stdout.txt" 2> "$W/new_stderr.txt"
for f in games.jsonl stdout.txt stderr.txt; do cmp "$W/old_$f" "$W/new_$f" || die "test 1: $f differs"; done
note "tool test 1 PASS: kp3, the table's first 20 deals of the 28 pairings (560 games), the old and new tools' stdout, stderr and games-out are byte-identical (stdout sha256 $(sha256sum "$W/new_stdout.txt" | cut -c1-64), games-out sha256 $(sha256sum "$W/new_games.jsonl" | cut -c1-64))"
cp "$W/new_stdout.txt" "$D/tool_test1_stdout.txt"; cp "$W/new_games.jsonl" "$D/tool_test1_games.jsonl"
t1=$(sha256sum "$W/new_stdout.txt" "$W/new_games.jsonl" | cut -c1-64 | paste -sd' ')
[ "$t1" = "a82786bb69fa10ca3bfba4c5854055911a280246440d9ab7b359319acb746997 057ae92e9a369d016bd10754313dd80f5eb7da1148bcdc79a1252cd642c67e0f" ] \
  && note "tool test 1's stdout and games-out equal 9c11b30's (the sha256 its STATUS.txt records)" \
  || note "tool test 1's stdout and games-out DIFFER from 9c11b30's ($t1)"

# Test 2: the same games through the new options (--seed-base 72,000,000 given, --rows-out): the same games-out and
# the same card table; each row's fingerprint equals games-out's.
run "$NEW" --seed-base 72000000 --games 20 --bot kp3 --games-out "$W/x_games.jsonl" --rows-out "$W/x_rows.jsonl" > "$W/x_stdout.txt" 2>/dev/null
cmp "$W/new_games.jsonl" "$W/x_games.jsonl" || die "test 2: games-out differs"
cmp <(tail -n +2 "$W/new_stdout.txt") <(tail -n +2 "$W/x_stdout.txt") || die "test 2: the card table differs"
python3 - "$W/x_rows.jsonl" "$W/x_games.jsonl" <<'EOF' || die "test 2: rows"
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]; games = [json.loads(l) for l in open(sys.argv[2])]
assert len(rows) == len(games) == 560
for r, g in zip(rows, games):
    assert (r["pairing"], r["i"], r["seed"], r["moves"]) == (g["pairing"], g["i"], g["seed"], g["moves"])
    assert r["first_seat"] == r["i"] % 2 and r["seat_decks"] == ([r["a"], r["b"]] if r["i"] % 2 == 0 else [r["b"], r["a"]])
EOF
note "tool test 2 PASS: the same 560 games with --seed-base 72000000 and --rows-out: games-out byte-identical, the same card table, every row's fingerprint, seed and seats equal games-out's"

# Test 3: traced games on diagnostic seeds (20,000,900,000 + pairing 2 x 10,000 + i, i < 20; Altaria v Lucario, the
# lists carrying Training Area and Arena of Antiquity; kp3 both sides): the rows' offered and played counts for the
# two Stadiums equal a recount from the move trace, with one game per card's trace lines printed in tool_check.txt.
run "$NEW" --seed-base 20000900000 --pairings 2 --games 20 --bot kp3 --rows-out "$W/trace_rows.jsonl" --trace-out "$W/trace.tsv" > /dev/null 2>&1
python3 "$D/tool_check.py" trace "tool test 3: traced games, kp3, Altaria v Lucario, seeds 20,000,920,000-019" "$W/trace_rows.jsonl" "$W/trace.tsv" > /dev/null || die "test 3 (tool_check.txt)"
cp "$W/trace_rows.jsonl" "$D/tool_test3_trace_rows.jsonl"; cp "$W/trace.tsv" "$D/tool_test3_trace.tsv"
note "tool $(tail -1 "$D/identity/identity_check.txt")"
note "tool test 3's rows sha256 $(sha256sum "$D/tool_test3_trace_rows.jsonl" | cut -c1-64), trace sha256 $(sha256sum "$D/tool_test3_trace.tsv" | cut -c1-64)"
cmp -s "$D/tool_test3_trace_rows.jsonl" "$OLDD/tool_test3_trace_rows.jsonl" && cmp -s "$D/tool_test3_trace.tsv" "$OLDD/tool_test3_trace.tsv" \
  && note "tool test 3's rows and trace equal 9c11b30's byte for byte" || note "tool test 3's rows or trace DIFFER from 9c11b30's"

# Identity 8a: kta3 on i < 40 of the 17 named cells (680 games) against ec7e1a8_kta3_table (13 cells) and
# ec7e1a8_kta3_new17 (4 cells); km3 on pairings 0 and 2, i < 40 (80 games), against item 7's smoke. Fingerprint, both
# decks, seed and seats only.
run "$NEW" --cells km17 --games 40 --bot kta3 --no-counts --rows-out "$W/8a_kta3_rows.jsonl" > /dev/null 2>&1
python3 "$D/tool_check.py" rows "identity 8a: the tool's kta3, the 17 named cells, i < 40" "$W/8a_kta3_rows.jsonl" 40 \
  cells=17 table="$KTA/ec7e1a8_kta3_table.jsonl" new_decks.tsv="$KTA/ec7e1a8_kta3_new17.jsonl" > /dev/null || die "IDENTITY 8a FAILED (kta3)"
note "$(tail -1 "$D/identity/identity_check.txt")"
run "$NEW" --cells km17 --pairings table:0,table:2 --games 40 --bot km3 --no-counts --rows-out "$W/8a_km3_rows.jsonl" > /dev/null 2>&1
python3 "$D/tool_check.py" rows "identity 8a: the tool's km3, pairings 0 and 2, i < 40, v item 7's smoke" "$W/8a_km3_rows.jsonl" 40 \
  cells=2 table="$D/identity/${BUILD}_km3_smoke_40.jsonl" > /dev/null || die "IDENTITY 8a FAILED (km3)"
note "$(tail -1 "$D/identity/identity_check.txt")"
cp "$W/8a_kta3_rows.jsonl" "$D/identity/${BUILD}_tool_kta3_km17_40.jsonl"; cp "$W/8a_km3_rows.jsonl" "$D/identity/${BUILD}_tool_km3_p02_40.jsonl"

# Test 4: --first-deal: kta3 on deals 20-39 of the 17 cells equals 8a's rows for those deals, row for row.
run "$NEW" --cells km17 --first-deal 20 --games 20 --bot kta3 --no-counts --rows-out "$W/t4_rows.jsonl" > /dev/null 2>&1
python3 - "$W/t4_rows.jsonl" "$W/8a_kta3_rows.jsonl" <<'EOF' || die "test 4"
import json, sys
t4 = [json.loads(l) for l in open(sys.argv[1])]
a8 = [r for r in map(json.loads, open(sys.argv[2])) if r["i"] >= 20]
assert len(t4) == len(a8) == 340 and t4 == a8
EOF
note "tool test 4 PASS: --first-deal 20 --games 20 gives 8a's rows for deals 20-39 of the 17 cells exactly (340 rows)"
# Test 5: the combinations the tool refuses exit with an error before any game is played (no games-out is written).
refused() {  # label args...
  local label=$1; shift
  rm -f "$W/t5_games.jsonl"
  if run "$NEW" "$@" --games 1 --bot kp3 --games-out "$W/t5_games.jsonl" > /dev/null 2>&1 || [ -e "$W/t5_games.jsonl" ]; then
    die "test 5: not refused: $label"
  fi
}
refused "--seed-base with --cells km17" --cells km17 --seed-base 20000900000
refused "--cells with --pairs" --cells km17 --pairs "$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv"
refused "--decks with --pairs" --pairs "$R/rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv" --seed-base 21108000000 --decks ../decks/research
refused "--root in table mode" --root ..
refused "--trace-out with --no-counts" --no-counts --trace-out "$W/t5_trace.tsv"
refused "deals past a pairing's 10,000 seeds" --first-deal 9999 --pairings 2 --games 2
note "tool test 5 PASS: the tool refuses --seed-base with --cells km17, --cells with --pairs, --decks with --pairs, --root in table mode, --trace-out with --no-counts, and deals past a pairing's 10,000 seeds, before any game"
note "STEP 3 COUNTER TOOL: done (tests 1-5 and identity 8a pass)"
