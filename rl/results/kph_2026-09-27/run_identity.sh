#!/usr/bin/env bash
# kph's identity checks at its build (REGISTRATION.md section 4), on the table's deals (72,000,000 + pairing x 10,000
# + i, i < 40, even i = first-named deck in seat 0; all 28 pairings, a superset of the registered 2 x 40):
# - kp3, k3, kpg3 and kpf3 must equal their official references (../rules09_fixes_2026-09-26/af8489f_{kp3,k3}_500,
#   ../kpf_2026-09-26/reading/table_{kpg3,kpf3}, first 40 deals). kpf3 is kph with fixes A and B off, and kpg3 kph
#   with R off, so these two are also the switch identities in games;
# - kph3, kpha3 (fix A only) and kphb3 (fix B only) are smokes (clean runs). The laptop reads them.
# OUT (default: this folder) takes the outputs while they run; they are copied here when complete.
# Usage: [OUT=<dir>] run_identity.sh <legality_scan built at the kph build commit> <label>
set -euo pipefail
SCAN=$1; L=$2; D=$(cd "$(dirname "$0")" && pwd); O=${OUT:-$D}; cd "$D/../../../engine"
echo "$L scan sha256 $(sha256sum "$SCAN" | cut -c1-64)" >> "$O/timing.txt"
run() { local bot=$1 n=$2 s; s=$(date +%s)
  "$SCAN" --decks ../decks/research --games "$n" --bot "$bot" --games-out "$O/${L}_${bot}_${n}.jsonl" > "$O/${L}_${bot}_${n}.txt" 2>&1
  echo "${L}_${bot}_${n} $(( $(date +%s) - s )) s wall" >> "$O/timing.txt"; }
for bot in kp3 k3 kpg3 kpf3 kph3 kpha3 kphb3; do run "$bot" 40; done
echo "$L identity done" >> "$O/timing.txt"
