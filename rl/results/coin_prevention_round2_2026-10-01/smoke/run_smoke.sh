#!/usr/bin/env bash
# The later round's smoke check (Oct 1; scratch decks only, no table deck). Three legality_scan programs, each built in
# a scratch copy: R (1abdbe8) plain, this branch's engine plain, and this branch's engine with the coin counters
# (../../coin_prevention_repair_2026-09-30/instrument_scan.py, as this branch has it). Each plays pairs.tsv with km3 on
# both sides, 40 games a pairing, seeds 20,980,000,000 + pairing x 10,000 + i (Claude Code's diagnostic block).
# Usage: run_smoke.sh <work dir> [<this branch's revision, default HEAD>]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
REV=${2:-HEAD}
mkdir -p "$W"

build() {  # <name> <revision> <instrument: yes|no>
    rm -rf "${W:?}/$1"
    mkdir -p "$W/$1"
    git -C "$REPO" archive "$2" engine | tar -x -C "$W/$1"
    if [ "$3" = yes ]; then
        git -C "$REPO" show "$2:rl/results/coin_prevention_repair_2026-09-30/instrument_scan.py" > "$W/instrument_scan.py"
        python3 "$W/instrument_scan.py" "$W/$1/engine/examples/legality_scan.rs"
    fi
    # git archive stamps files with the commit's time; re-stamp so the shared target folder can't serve an older build.
    find "$W/$1/engine" -type f -exec touch {} +
    (cd "$W/$1/engine" && CARGO_TARGET_DIR="$W/target" cargo build --release --example legality_scan 2>&1 | grep -E "Compiling deckgym|Finished|^error")
    cp "$W/target/release/examples/legality_scan" "$W/scan_$1"
    echo "scan_$1 sha256 $(sha256sum < "$W/scan_$1" | cut -c1-64) ($2: $(git -C "$REPO" rev-parse --short "$2"))"
}

build r_plain 1abdbe8 no
build round2_plain "$REV" no
build round2_watch "$REV" yes

for v in r_plain round2_plain round2_watch; do
    (cd "$HERE" && "$W/scan_$v" --pairs pairs.tsv --root . --seed-base 20980000000 --games 40 --bot km3 \
        --games-out "$HERE/games_$v.jsonl" > "$W/stdout_$v.txt" 2> "$W/stderr_$v.txt")
    echo "games_$v.jsonl: $(wc -l < "$HERE/games_$v.jsonl") games"
done
