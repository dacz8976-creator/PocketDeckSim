#!/usr/bin/env bash
# Build legality_scan at e09fb46, the commit the cloud's kpr3 table runs at (rl/results/kpr_2026-09-25 on the cloud
# branch claude/pensive-ptolemy-spwc0b; its README: every later branch commit has the same engine/), into a scratch
# folder outside the repo, as the kd build was (git archive, cargo build --release --example legality_scan).
# Not the official engine; used only for kpr3's mixed rows. Usage: build_kpr_scan.sh   (in WSL)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
B=/home/dacz8976/engine-kpr-e09fb46
C=e09fb46
mkdir -p "$B"
cd "$R"
git cat-file -e "$C^{commit}"
git rev-parse "$C" | sed "s/^/$C /" > "$B/COMMIT"
git archive "$C" engine decks | tar -x -C "$B"
cd "$B/engine"
{ time cargo build --release --example legality_scan ; } > "$B/build.txt" 2>&1
cp target/release/examples/legality_scan "$B/legality_scan_$C"
sha256sum "$B/legality_scan_$C" | tee "$B/legality_scan_sha.txt"
