#!/usr/bin/env bash
# The floor check's Payback pre-use check (README.md). Run from anywhere in WSL; writes into this folder.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
F="python3 decks/screen/floor.py"
t() { local tag=$1; shift; local s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
t brew-06 $F decks/brews/brew-06-pyukumuku-silvally-payback.txt --out "$D"
t brew-06b $F decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt --out "$D"
t control-14-k3 $F decks/dustin/14-comfey-raticate-hypno.txt --out "$D/control_k3" --pilot k3 --meta-pilot k3
t brew-05b $F decks/brews/brew-05b-meowstic-hatterene-comfey.txt --out "$D"
t deck-07 $F decks/dustin/07-skarmory-stall.txt --out "$D"
t run_screen python3 decks/screen/run_screen.py decks/brews/brew-06-pyukumuku-silvally-payback.txt \
  decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt --games 240 > "$D/run_screen.txt" 2>&1
echo "payback check done" >> "$D/timing.txt"
