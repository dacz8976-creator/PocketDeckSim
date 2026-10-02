#!/usr/bin/env bash
# Round-2 readiness, job 2 (Oct 2): the counters' smoke check. Two legality_scan programs, each built in a scratch copy of
# claude/coin-prevention-round2's engine: plain, and with both watch scripts (the coin repair's instrument_scan.py, with the
# round-2 package's counters, then the Victory Star repair's). Each plays pairs.tsv (lists where the package can act: Dustin's
# 12 with two Ariados, the Will lists v t-weezing, Wild Swing and the later round's sites v Carefree Steps) with km3 on both
# sides, 20 games a pairing, seeds 20,990,000,000 + pairing x 10,000 + i (Claude Code's diagnostic block). No table game.
# It also checks that the two scripts give the same lines in either order, and each alone applies.
# Usage: run_smoke.sh <work dir> [<revision, default HEAD>]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
REV=${2:-HEAD}
mkdir -p "$W"
COIN=rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py
VS=rl/results/victory_star_repair_2026-09-30/instrument_scan.py
git -C "$REPO" show "$REV:$COIN" > "$W/coin.py"
git -C "$REPO" show "$REV:$VS" > "$W/vs.py"

build() {  # <name> <scripts, in order, or none>
    rm -rf "${W:?}/$1"
    mkdir -p "$W/$1"
    git -C "$REPO" archive "$REV" engine | tar -x -C "$W/$1"
    for s in $2; do
        [ "$s" = none ] || python3 "$W/$s.py" "$W/$1/engine/examples/legality_scan.rs"
    done
    find "$W/$1/engine" -type f -exec touch {} +
    (cd "$W/$1/engine" && CARGO_TARGET_DIR="$W/target" cargo build --release --locked --example legality_scan 2>&1 | grep -E "Finished|^error")
    cp "$W/target/release/examples/legality_scan" "$W/scan_$1"
    echo "scan_$1 sha256 $(sha256sum < "$W/scan_$1" | cut -c1-64) ($REV: $(git -C "$REPO" rev-parse --short "$REV"))"
}

# The order check: coin then Victory Star, and Victory Star then coin, give the same sorted lines; each alone applies.
for order in "coin vs" "vs coin" "coin" "vs"; do
    mkdir -p "$W/order"
    git -C "$REPO" show "$REV:engine/examples/legality_scan.rs" > "$W/order/scan.rs"
    for s in $order; do python3 "$W/$s.py" "$W/order/scan.rs" > /dev/null; done
    sort "$W/order/scan.rs" > "$W/order/sorted_${order// /_}.txt"
done
cmp -s "$W/order/sorted_coin_vs.txt" "$W/order/sorted_vs_coin.txt" && echo "either order: the same sorted lines" \
    || echo "either order: DIFFERENT"

build round2_plain none
build round2_watch "coin vs"

for v in round2_plain round2_watch; do
    (cd "$REPO" && "$W/scan_$v" --pairs "$HERE/pairs.tsv" --root . --seed-base 20990000000 --games 20 --bot km3 \
        --games-out "$HERE/games_$v.jsonl" > "$W/stdout_$v.txt" 2> "$W/stderr_$v.txt")
    echo "games_$v.jsonl: $(wc -l < "$HERE/games_$v.jsonl") games"
done
