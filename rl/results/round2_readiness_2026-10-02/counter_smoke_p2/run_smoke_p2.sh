#!/usr/bin/env bash
# P2 (Oct 8): the return-damage counters in real games. Three legality_scan programs, each built from a scratch copy of
# claude/coin-prevention-round2's engine at a revision: P plain (the engine before P2), P2 plain, and P2 with both watch scripts
# (the coin repair's instrument_scan.py, with P2's counters, then the Victory Star repair's; read from this checkout). Each plays
# pairs.tsv (the two lists that hold Mega Sableye ex against t-altaria, whose Espeon is the panel's only Darkness-weak Pokemon;
# brew-09 v t-sceptile, no Darkness-weak attacker; brew-07 v t-blaziken, which holds Rocky Helmet) with km3 on both sides, 50
# games a pairing, seeds 20,960,000,000 + pairing x 10,000 + i (Claude Code's diagnostic block). No table game.
# Usage: run_smoke_p2.sh <work dir> <P revision> <P2 revision>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
P=$2
P2=$3
mkdir -p "$W"

build() {  # <name> <revision> <instrument? yes|no>
    rm -rf "${W:?}/$1"
    mkdir -p "$W/$1"
    git -C "$REPO" archive "$2" engine | tar -x -C "$W/$1"
    if [ "$3" = yes ]; then
        python3 "$REPO/rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py" "$W/$1/engine/examples/legality_scan.rs" > /dev/null
        python3 "$REPO/rl/results/victory_star_repair_2026-09-30/instrument_scan.py" "$W/$1/engine/examples/legality_scan.rs" > /dev/null
    fi
    find "$W/$1/engine" -type f -exec touch {} +
    (cd "$W/$1/engine" && CARGO_TARGET_DIR="$W/target" cargo build --release --locked --example legality_scan 2>&1 | grep -E "Finished|^error")
    cp "$W/target/release/examples/legality_scan" "$W/scan_$1"
    echo "scan_$1 sha256 $(sha256sum < "$W/scan_$1" | cut -c1-64) ($2: $(git -C "$REPO" rev-parse --short "$2"))"
}

build p_plain "$P" no
build p2_plain "$P2" no
build p2_watch "$P2" yes

for v in p_plain p2_plain p2_watch; do
    (cd "$REPO" && "$W/scan_$v" --pairs "$HERE/pairs.tsv" --root . --seed-base 20960000000 --games 50 --bot km3 \
        --games-out "$HERE/games_$v.jsonl" > "$W/stdout_$v.txt" 2> "$W/stderr_$v.txt")
    echo "games_$v.jsonl: $(wc -l < "$HERE/games_$v.jsonl") games"
done
