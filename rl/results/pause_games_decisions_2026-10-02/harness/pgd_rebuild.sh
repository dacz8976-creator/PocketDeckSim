#!/usr/bin/env bash
# incremental rebuild of the harness example only (engine already compiled in the same target dir)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/pgd
cp "$HERE/pg_pos.rs" "$D/build/engine/examples/pg_pos.rs"
cd "$D/build/engine"
CARGO_BUILD_JOBS=8 CARGO_TARGET_DIR="$D/target" nice -n 19 cargo build --release --locked --example pg_pos 2>&1 | grep -E "^error|^warning: unused var|-->|^\s+\|" | grep -v "value_functions\|energy_moves\|attack_outcome" | head -60 || true
cp "$D/target/release/examples/pg_pos" "$D/pg_pos" && sha256sum "$D/pg_pos" | cut -c1-16
# the position file and the deck
python3 "$HERE/positions_A.py" "$D/positions_A.json"
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
git -C "$REPO" show origin/main:decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt > "$D/draftA.txt"
wc -l "$D/draftA.txt"
