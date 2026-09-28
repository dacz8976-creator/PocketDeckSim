#!/usr/bin/env bash
# The floor check on the unplayed brews (README.md). Run from anywhere in WSL; writes here.
# Same call as ../floor_recheck_2026-09-28/run_check.sh: floor.py's defaults (kog3 both sides, 240 games per matchup).
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
grep -q '"rl/engine-2026-09-28/deckgym"' project_manifest.json || { echo "the manifest doesn't name the new engine"; exit 1; }
F="nice -n 19 python3 decks/screen/floor.py"
t() { local tag=$1; shift; local s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
echo "$(date -u +%F\ %T) FLOOR BREWS START" >> "$D/timing.txt"
for b in brew-07-hoopa-darkrai-sableye brew-08-entei-rainbow-cave brew-09-sableye-obstagoon brew-10-diancie-giratina \
         brew-02-arceus-tandemaus-persian brew-03b-arceus-crobat-nihilego-toxapex; do
  t "$b" $F "decks/brews/$b.txt" --out "$D"
done
echo "$(date -u +%F\ %T) FLOOR BREWS DONE" >> "$D/timing.txt"
