#!/usr/bin/env bash
# Review helper (no build): extract 7fc6ccb's legality_scan.rs into review/, check the patch applies, keep the
# patched copy for reading. Also reports git state that the build script depends on.
set -uo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
V="$R/rl/results/b2e_rows_2026-09-26/review"
P="$R/rl/results/b2e_rows_2026-09-26/legality_scan_pairs.patch"
cd "$R"
echo "== git"
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git rev-parse 7fc6ccb
git log --oneline -1 7fc6ccb
echo "== diff of legality_scan.rs between 7fc6ccb and HEAD"
git diff --stat 7fc6ccb HEAD -- engine/examples/legality_scan.rs
echo "== extract"
T=$(mktemp -d)
mkdir -p "$T/engine/examples"
git show 7fc6ccb:engine/examples/legality_scan.rs > "$T/engine/examples/legality_scan.rs"
cp "$T/engine/examples/legality_scan.rs" "$V/legality_scan_7fc6ccb.rs"
cd "$T"
echo "== numstat"; git apply --numstat "$P"
echo "== check"; git apply --check "$P" && echo CHECK_OK || echo CHECK_FAIL
git apply "$P" && echo APPLY_OK || echo APPLY_FAIL
cp "$T/engine/examples/legality_scan.rs" "$V/legality_scan_patched.rs"
echo "== second apply (should fail)"; git apply --check "$P" 2>&1 | head -3
echo "== line endings of patch / original"
file "$P" "$V/legality_scan_7fc6ccb.rs"
grep -c $'\r' "$P" || true
rm -rf "$T"
echo "== sha256"
sha256sum "$P" "$V/legality_scan_7fc6ccb.rs" "$V/legality_scan_patched.rs"
echo "== official binaries"
sha256sum "$R/rl/engine-2026-09-25/deckgym" "$R/rl/engine-2026-09-25/legality_scan" 2>&1
echo "== scratch build folder exists?"
ls -d /home/dacz8976/engine-b2e-7fc6ccb 2>&1
ls -d /home/dacz8976/engine-* 2>&1
