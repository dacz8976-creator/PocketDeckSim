#!/usr/bin/env bash
# builds the pause-games harness into its own target dir at nice 19 (a scratch copy of an engine source tree + the print-only patch + the example).
#   pgd_build.sh [JOBS]            the pinned engine (main-8626a35 engine/, archived to /home/dacz8976/pgd/src/engine)
# For another pilot, point it at an engine tree that contains that pilot (a branch's engine/ directory):
#   PGD_ENGINE=/path/to/engine PGD_TARGET=/path/to/target PGD_BIN=/path/to/pg_pos_other  pgd_build.sh 8
# The patch needs src/players/expectiminimax_player.rs with the anchors it expects (it asserts each one is found exactly once).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/pgd
ENG=${PGD_ENGINE:-$D/src/engine}
TARGET=${PGD_TARGET:-$D/target}
BIN=${PGD_BIN:-$D/pg_pos}
rm -rf "$D/build" && mkdir -p "$D/build"
cp -r "$ENG" "$D/build/engine"
find "$D/build" -type f -exec touch {} +
cp "$HERE/dg_patch.py" "$D/dg_patch.py" 2>/dev/null || cp "$HERE/../c8c/dg_patch.py" "$D/dg_patch.py"
cp "$HERE/pgd_patch.py" "$D/pgd_patch.py"
python3 -B "$D/pgd_patch.py" "$D/build/engine"
mkdir -p "$D/build/engine/examples"
cp "$HERE/pg_pos.rs" "$D/build/engine/examples/pg_pos.rs"
cd "$D/build/engine"
CARGO_BUILD_JOBS=${1:-8} CARGO_TARGET_DIR="$TARGET" nice -n 19 cargo build --release --locked --example pg_pos 2>&1 | grep -E "^(error|warning: unused)|-->|^\s+\|" | head -80 || true
ls -la "$TARGET/release/examples/pg_pos" && cp "$TARGET/release/examples/pg_pos" "$BIN" && sha256sum "$BIN" | cut -c1-16
