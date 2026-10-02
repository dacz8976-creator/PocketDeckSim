#!/usr/bin/env bash
# builds the pause-games harness into its own target dir at nice 19 (scratch copy of the pinned engine, print-only patch)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=/home/dacz8976/pgd
rm -rf "$D/build" && mkdir -p "$D/build"
cp -r "$D/src/engine" "$D/build/engine"
find "$D/build" -type f -exec touch {} +
cp "$HERE/../c8c/dg_patch.py" "$D/dg_patch.py"
cp "$HERE/pgd_patch.py" "$D/pgd_patch.py"
python3 -B "$D/pgd_patch.py" "$D/build/engine"
cp "$HERE/pg_pos.rs" "$D/build/engine/examples/pg_pos.rs"
cd "$D/build/engine"
CARGO_BUILD_JOBS=${1:-8} CARGO_TARGET_DIR="$D/target" nice -n 19 cargo build --release --locked --example pg_pos 2>&1 | grep -E "^(error|warning: unused)|-->|^\s+\|" | head -80 || true
ls -la "$D/target/release/examples/pg_pos" && cp "$D/target/release/examples/pg_pos" "$D/pg_pos" && sha256sum "$D/pg_pos" | cut -c1-16
