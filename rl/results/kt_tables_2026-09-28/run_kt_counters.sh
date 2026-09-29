#!/usr/bin/env bash
# kt on kog, the readout counters (registration "READOUT COUNTERS" in ../kt_2026-09-26/README.md, amendment 2 items 1 and 9;
# the laptop's run, next to run_kt.sh). For kog3, kt3, kta3, ktb3 and ktc3, on the first 100 deals of each of the 28 table
# pairings (the table's deals: 72,000,000 + pairing x 10,000 + i, i < 100, even i = the first-named deck in seat 0):
#   1. tool_census.rs (../tool_turn_effect_census_2026-09-25/): the per-card table (turns offered, turns played, holder by
#      spot and name, Field Blower's targets), stdout in <build>_census_<code>.txt, one fingerprint per game in .jsonl;
#   2. legality_scan's Hyper Ray, Chase Order, discard-attack and Ability counters, in <build>_scan_<code>_<deals>.txt
#      (.jsonl beside: per-game rows with the same counters and the move fingerprint).
# Fingerprints are then checked against each code's table file: kt3, kta3, ktb3, ktc3 <build>_<code>_table.jsonl (run_kt.sh
# part B), kog3 <build>_id_kog3_500.jsonl (else ../kog_composition_2026-09-27/table_kog3.jsonl, which the identity check
# shows equal). A table file that is not there yet leaves its check pending (noted; a later run does it).
# Every game is played by the kt build's own programs (amendment 2 item 1): legality_scan from the build, and tool_census
# built as one more example inside the build's own engine tree (the census README's procedure), so it links the same
# libdeckgym as deckgym and legality_scan. The kt build's deckgym and legality_scan hashes are checked before and after.
# Order: kog3 first (not a kt game), then a wait for GATE_koh_b2e_read (before any kt game), then kt3, kta3, ktb3, ktc3.
# Resumable: a finished output is skipped; outputs are written to .part and moved when done.
# Usage (WSL): nohup setsid bash run_kt_counters.sh [<kt build's short commit, default ec7e1a8>] > run_counters.log 2>&1 &
# Knobs (environment; the defaults are the real run): KT_OUT, KT_BUILD, THREADS (12), NICE (10), DEALS (100),
#   CODES ("kog3 kt3 kta3 ktb3 ktc3"), BUILD_JOBS (4, tool_census's build only), NO_WAIT (exit when the gate is closed).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
S=${1:-ec7e1a8}
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O=${KT_OUT:-$R/rl/results/kt_tables_2026-09-28}
GATE="$R/rl/results/kt_tables_2026-09-28/GATE_koh_b2e_read"
KOG="$R/rl/results/kog_composition_2026-09-27"
CSRC="$R/rl/results/tool_turn_effect_census_2026-09-25/tool_census.rs"
B=${KT_BUILD:-/home/dacz8976/engine-kt-$S}
THREADS=${THREADS:-12}; NICE=${NICE:-10}; DEALS=${DEALS:-100}
CODES=${CODES:-"kog3 kt3 kta3 ktb3 ktc3"}
GYM_EXPECT=407976366fa2104e; SCAN_EXPECT=924751ba0926993e       # the kt build's programs, sha256 prefixes (Sept 28)
GYM="$B/engine/target/release/deckgym"
SCAN="$B/engine/target/release/examples/legality_scan"
CENSUS="$B/engine/target/release/examples/tool_census"
source "$HOME/.cargo/env" 2>/dev/null || true
mkdir -p "$O"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; exit 1; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
check_build() {
  [ "$(sha "$GYM" | cut -c1-16)" = "$GYM_EXPECT" ] || die "run_kt_counters: deckgym is not the kt build's ($GYM_EXPECT)"
  [ "$(sha "$SCAN" | cut -c1-16)" = "$SCAN_EXPECT" ] || die "run_kt_counters: legality_scan is not the kt build's ($SCAN_EXPECT)"
}
[ "$(cut -c1-7 "$B/COMMIT" 2>/dev/null)" = "$S" ] || die "run_kt_counters: $B is not the build of $S"
[ -x "$GYM" ] && [ -x "$SCAN" ] || die "run_kt_counters: the kt build's programs are not in $B"
check_build
SCANH=$(sha "$SCAN")
note "run_kt_counters $S: codes $CODES, first $DEALS deals of the 28 table pairings, $THREADS threads; kt build legality_scan sha256 $SCANH, deckgym sha256 $(sha "$GYM")"

# tool_census: one more example in the kt build's engine tree (only new files: examples/tool_census.rs and its binary).
if [ ! -x "$CENSUS" ]; then
  cp "$CSRC" "$B/engine/examples/tool_census.rs"
  note "building tool_census in $B/engine (source $(sha "$CSRC" | cut -c1-16), from ../tool_turn_effect_census_2026-09-25/tool_census.rs)"
  ( cd "$B/engine" && nice -n "$NICE" cargo build --release --example tool_census -j "${BUILD_JOBS:-4}" ) > "$O/census_build.log" 2>&1 \
    || die "tool_census build (census_build.log)"
  check_build                      # the build must not have touched the kt build's own programs
fi
CENSH=$(sha "$CENSUS")
[ "$(sha "$CSRC")" = "$(sha "$B/engine/examples/tool_census.rs")" ] || die "tool_census.rs in the build differs from the repo's"
note "tool_census sha256 $CENSH (built in the kt build's tree at $S)"

gate() {  # no kt game before koh's B2e rows are read and committed (../kt_tables_2026-09-28/README.md)
  if [ ! -e "$GATE" ]; then
    if [ -n "${NO_WAIT:-}" ]; then note "gate closed and NO_WAIT set: no kt game played"; echo "gate closed"; exit 3; fi
    note "waiting for GATE_koh_b2e_read before the first kt game"
    until [ -e "$GATE" ]; do sleep 60; done
    note "gate open: $(cat "$GATE")"
  fi
}
run_census() {  # code
  local code=$1 name=${S}_census_${1} s
  [ -s "$O/$name.jsonl" ] && [ -s "$O/$name.txt" ] && return
  case $code in kt*) gate;; esac
  s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$CENSUS" --decks ../decks/research --games "$DEALS" --bot "$code" \
      --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt.part" 2> "$O/$name.log" || die "$name (see $name.log)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; mv "$O/$name.txt.part" "$O/$name.txt"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games); tool_census ${CENSH:0:16}"
}
run_scan() {  # code
  local code=$1 name=${S}_scan_${1}_${DEALS} s
  [ -s "$O/$name.jsonl" ] && [ -s "$O/$name.txt" ] && return
  case $code in kt*) gate;; esac
  s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$SCAN" --decks ../decks/research --games "$DEALS" --bot "$code" \
      --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt.part" 2>&1 || die "$name"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; mv "$O/$name.txt.part" "$O/$name.txt"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games); legality_scan ${SCANH:0:16}"
}
# kog3 first (no gate), then the kt codes: the census and the scan for one code, then the next code.
for code in $CODES; do run_census "$code"; run_scan "$code"; done
check_build

# Fingerprints against each code's table file (the census's own check: "fingerprints checked against the table file").
: > "$O/${S}_counters_fingerprints.txt"
pending=0
for code in $CODES; do
  table="$O/${S}_${code}_table.jsonl"
  if [ "$code" = kog3 ]; then
    table="$O/${S}_id_kog3_500.jsonl"; [ -s "$table" ] || table="$KOG/table_kog3.jsonl"
  fi
  if [ ! -s "$table" ]; then
    echo "$code: table file not there yet ($table); check pending" >> "$O/${S}_counters_fingerprints.txt"; pending=$((pending + 1)); continue
  fi
  python3 - "$table" "$DEALS" "$code" "$O/${S}_census_${code}.jsonl" "$O/${S}_scan_${code}_${DEALS}.jsonl" \
    >> "$O/${S}_counters_fingerprints.txt" <<'EOF' || die "FINGERPRINT MISMATCH for $code (see ${S}_counters_fingerprints.txt)"
import json, sys
table_path, deals, code = sys.argv[1], int(sys.argv[2]), sys.argv[3]
table = {(g["pairing"], g["i"]): (g["seed"], g["moves"]) for g in map(json.loads, open(table_path)) if g["i"] < deals}
ok = len(table) == 28 * deals
for label, path in (("tool_census", sys.argv[4]), ("legality_scan", sys.argv[5])):
    mine = {(g["pairing"], g["i"]): (g["seed"], g["moves"]) for g in map(json.loads, open(path))}
    bad = [k for k in table if mine.get(k) != table[k]]
    print(f"{code}: {label}: {len(table) - len(bad)} of {len(table)} seeds and move fingerprints equal the table file's "
          f"({table_path.split('/')[-1]}); {len(mine)} games in the counter file")
    ok = ok and not bad and len(mine) == len(table)
sys.exit(0 if ok else 1)
EOF
done
note "fingerprints: $(tr '\n' ' ' < "$O/${S}_counters_fingerprints.txt")"
if [ "$pending" -gt 0 ]; then note "KT COUNTERS: outputs done, $pending fingerprint check(s) pending their table files (rerun to check)"
else echo "$(date -u +%F\ %T) KT COUNTERS DONE $S" >> "$O/STATUS.txt"; fi
