#!/usr/bin/env bash
# The floor check under km3 on Dustin's decks and the brews (README.md). Run from anywhere in WSL; writes here.
# Same call as ../floor_brews_2026-09-28/run_floor.sh and ../floor_recheck_2026-09-30/run_check.sh: floor.py's defaults
# (km3 both sides since the Sept 30 engine switch, the official engine, 240 games per matchup, seed 7,100).
# Deck 07 and brew 05b are not re-run: today's re-check has their km3 pages (README). A finished page is not replayed.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
export PYTHONDONTWRITEBYTECODE=1
grep -q '"rl/engine-2026-09-30/deckgym"' project_manifest.json || { echo "the manifest doesn't name the Sept 30 engine"; exit 1; }
git diff --quiet HEAD -- "$D/README.md" "$D/run_floor.sh" && git ls-files --error-unmatch "$D/README.md" "$D/run_floor.sh" >/dev/null \
  || { echo "README.md and run_floor.sh must be committed unchanged before any game"; exit 1; }
F="nice -n 19 python3 decks/screen/floor.py"
t() { local tag=$1; shift; local s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
echo "$(date -u +%F\ %T) FLOOR DUSTIN START" >> "$D/timing.txt"
DECKS=(01-muk-glimmora-kingambit-regigigas 02-arceus-crobat 03-wailord-indeedee-wall 04-absol-hoopa-darkrai
       05-indeedee-stoutland 06-mega-blaziken-tournament-list 08-garchomp-toolbox 09-mega-manectric-heliolisk
       10-xatu-oricorio-tr-weezing 11-archaludon-haxorus-dragonair 12-ariados-whimsicott-ogerpon
       13-a-ninetales-raticate 14-comfey-raticate-hypno 15-jolteon-oricorio-raticate)
BREWS=(brew-02-arceus-tandemaus-persian brew-03b-arceus-crobat-nihilego-toxapex brew-07-hoopa-darkrai-sableye
       brew-08-entei-rainbow-cave brew-09-sableye-obstagoon brew-10-diancie-giratina)
for d in "${DECKS[@]}"; do
  [ -s "$D/$d.md" ] && { echo "$d: page exists, not replayed" >> "$D/timing.txt"; continue; }
  t "$d" $F "decks/dustin/$d.txt" --out "$D"
done
for b in "${BREWS[@]}"; do
  [ -s "$D/$b.md" ] && { echo "$b: page exists, not replayed" >> "$D/timing.txt"; continue; }
  t "$b" $F "decks/brews/$b.txt" --out "$D"
done
echo "$(date -u +%F\ %T) FLOOR DUSTIN DONE" >> "$D/timing.txt"
