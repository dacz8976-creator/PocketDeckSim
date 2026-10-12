#!/usr/bin/env bash
# coin_probe v2's P2 check, RETURN (the cloud, Oct 9): its checks, on the candidate engine (claude/coin-prevention-round2).
#   1. the self-test (boards A-G as before, H-N for RETURN), with P2 on (the default) and off (DECKGYM_FLAT_RETURN_DAMAGE=1:
#      exactly H, I, J and M must fail);
#   2. the three games P2's smoke changed (counter_smoke_p2/first_difference_output.txt, all "in look-ahead"), at the first
#      differing tick: RETURN inside the search with P2 on, nothing with it off;
#   3. golden: the seven smoke games where the exact counter attack_return_weakness fired (games_p2_watch.jsonl), at that tick:
#      ret 1 with P2 on (the move played there), nothing with it off;
#   4. controls: four ticks of pairings 2-3 (Mega Sableye ex v t-sceptile and t-blaziken, neither weak to Darkness) where only
#      the off-gate counter fired: nothing.
# Usage: p2_probe_checks.sh <work dir> <revision>   (from anywhere in the repository; builds a git archive of <revision>'s engine)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
REV=$2
mkdir -p "$W" && W=$(cd "$W" && pwd)   # absolute: the build and the probes run from inside it
SM=$HERE/counter_smoke_p2
rm -rf "${W:?}/src"
mkdir -p "$W/src"
git -C "$REPO" archive "$REV" engine | tar -x -C "$W/src"
python3 "$HERE/../coin_prevention_repair_2026-09-30/instrument_scan.py" --emit-fns "$W/src/engine/examples/r2_counter_fns.rs" > /dev/null
cp "$HERE/coin_probe_v2.rs" "$W/src/engine/examples/"
echo "== build: $(git -C "$REPO" rev-parse --short "$REV")'s engine, coin_probe_v2.rs sha256 $(sha256sum < "$HERE/coin_probe_v2.rs" | cut -c1-64)"
rm -f "$W/target/release/examples/coin_probe_v2"   # never run an earlier build
(cd "$W/src/engine" && CARGO_TARGET_DIR="$W/target" cargo build --release --locked --features test-utils --example coin_probe_v2 2>&1 | grep -E "Finished|^error") \
    || { echo "the build failed; stopping"; exit 1; }
PROBE=$W/target/release/examples/coin_probe_v2

echo "== 1. the self-test"
(cd "$W/src/engine" && "$PROBE" --selftest > "$W/selftest_on.txt" 2>&1)
echo "P2 on (exit $?): $(grep '^selftest:' "$W/selftest_on.txt")"
(cd "$W/src/engine" && DECKGYM_FLAT_RETURN_DAMAGE=1 "$PROBE" --selftest > "$W/selftest_off.txt" 2>&1)
echo "P2 off (exit $?): $(grep '^selftest:' "$W/selftest_off.txt"); failing: $(grep '^FAIL' "$W/selftest_off.txt" | cut -d: -f1 | sed 's/^FAIL //' | paste -sd ';')"

deck() { awk -F'\t' -v p="$1" -v c="$2" 'NR > 1 && $1 == p {print $c}' "$SM/pairs.tsv"; }
run() {  # <pairing> <deal> <tick> <on|off>: the RESULT lines on one line
    local env=()
    [ "$4" = off ] && env=(env DECKGYM_FLAT_RETURN_DAMAGE=1)
    (cd "$W/src/engine" && "${env[@]}" "$PROBE" --a "$REPO/$(deck "$1" 3)" --b "$REPO/$(deck "$1" 5)" --seed-base 20960000000 \
        --pairing "$1" --bot km3 --deal "$2" --tick "$3" > "$W/probe_$1_$2_$3_$4.txt" 2>&1)
    grep -E '^RESULT' "$W/probe_$1_$2_$3_$4.txt" | paste -sd ' '
    grep -q "search stopped" "$W/probe_$1_$2_$3_$4.txt" && echo "    (the search stopped at the node limit)"
    return 0
}
path() { grep -A1 "RETURN:" "$W/probe_$1_$2_$3_on.txt" | tail -1 | sed -E 's/Attack\(Attack \{[^;]*title: "([^"]*)"[^;]*\]?/Attack(\1)/g; s/^ +after \[/    path: [/; s/\] the hit back.*/]/'; }

echo "== 2. the three games P2 changed, at the first differing tick"
for g in "0 31 44" "1 21 84" "1 8 43"; do
    set -- $g
    echo "pairing $1 deal $2 tick $3: P2 on: $(run "$@" on); P2 off: $(run "$@" off)"
    path "$@"
done

echo "== 3. golden: the seven games where attack_return_weakness fired, at its tick"
for g in "0 13 70" "1 1 54" "1 2 43" "1 29 86" "1 34 62" "1 38 99" "1 43 76"; do
    set -- $g
    echo "pairing $1 deal $2 tick $3: P2 on: $(run "$@" on); P2 off: $(run "$@" off)"
done

echo "== 4. controls: only the off-gate counter fired there"
for g in "2 1 48" "2 5 51" "3 18 67" "3 19 53"; do
    set -- $g
    echo "pairing $1 deal $2 tick $3: $(run "$@" on)"
done
