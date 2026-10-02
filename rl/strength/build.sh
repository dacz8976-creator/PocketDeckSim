#!/usr/bin/env bash
# Builds the strength harness against an engine tree, at nice 19, in a scratch directory (nothing is written into the repo or its engine/).
#   rl/strength/build.sh [ENGINE_REF_OR_DIR] [OUT_BINARY]
# ENGINE_REF_OR_DIR: a git ref of this repository (default origin/main; the engine/ tree of that ref is archived), or a path to an engine
#   directory (for example the experimental pilot's branch checkout's engine/). The harness knows exactly the pilot codes that engine's
#   parse_player_code knows, so the experimental pilot is built by pointing this at its branch.
# OUT_BINARY: where to put the program (default ./strength next to this script's scratch build).
# Prints the engine tree hash (or directory), the program's sha256 and the harness source hash: put them in the pre-registration.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=${STRENGTH_REPO:-$(cd "$HERE/../.." && pwd)}   # the repository whose git objects hold the engine ref
REF=${1:-origin/main}
OUT=${2:-$HOME/strength_build/strength}
W=${STRENGTH_BUILD_DIR:-$HOME/strength_build}
TARGET=${STRENGTH_TARGET_DIR:-$W/target}
rm -rf "$W/tree" && mkdir -p "$W/tree/rl/strength" "$(dirname "$OUT")"
if [ -d "$REF" ]; then
    cp -r "$REF" "$W/tree/engine"; ENGINE_ID="dir:$REF"
else
    git -C "$REPO" archive "$REF" engine | tar -x -C "$W/tree"
    ENGINE_ID="$REF engine tree $(git -C "$REPO" rev-parse "$REF:engine")"
fi
find "$W/tree" -type f -exec touch {} +   # git archive gives every file the same mtime: touch so cargo rebuilds what changed
cp -r "$HERE/src" "$HERE/Cargo.toml" "$W/tree/rl/strength/"
# the engine's own lock file pins every dependency; the harness adds only itself
cp "$W/tree/engine/Cargo.lock" "$W/tree/rl/strength/Cargo.lock"
cd "$W/tree/rl/strength"
CARGO_TARGET_DIR="$TARGET" CARGO_BUILD_JOBS=${STRENGTH_JOBS:-8} nice -n 19 cargo build --release --offline 2>&1 | grep -E "^(error|warning: unused)|-->|^\s+\|" | head -60 || true
cp "$TARGET/release/strength" "$OUT"
echo "engine: $ENGINE_ID"
echo "program: $OUT"
echo "program sha256: $(sha256sum "$OUT" | cut -d' ' -f1)"
echo "harness source sha256: $(cat "$HERE"/src/*.rs "$HERE/Cargo.toml" | sha256sum | cut -d' ' -f1)"
