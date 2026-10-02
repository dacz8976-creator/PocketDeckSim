#!/usr/bin/env bash
# The floor check under km3 on the four brew drafts (README.md in rl/results/floor_drafts_2026-10-02/).
# floor.py's own call with its defaults (km3 both sides, the official engine, 240 games per matchup, seed 7,100).
# One draft after another, never in parallel, at nice 10. A finished page is not replayed.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; cd "$R"
D="rl/results/floor_drafts_2026-10-02"
export PYTHONDONTWRITEBYTECODE=1
LOG="$D/run.log"
cp "$0" "$D/run_floor.sh"
[ -s "$D/README.md" ] || { echo "README.md must exist before any game"; exit 1; }
want_dg=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
want_gf=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
want_fl=8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a
eng=$(python3 -c 'import sys;sys.path.insert(0,".");from current_engine import resolve;print(resolve(project="."))')
{
  echo "$(date -u +%F\ %T) UTC start; current_engine resolves $eng"
  sha256sum rl/engine-2026-10-02/deckgym rl/engine-2026-10-02/goldfish decks/screen/floor.py decks/screen/opponents/*.txt \
    decks/brews/drafts_2026-10-01/*.txt
  echo "git HEAD $(git log -1 --format=%H)"
  git status --short -- decks/screen decks/brews/drafts_2026-10-01 current_engine.py project_manifest.json rl/engine-2026-10-02 lib
} >> "$LOG"
[ "$(sha256sum < rl/engine-2026-10-02/deckgym | cut -d' ' -f1)" = "$want_dg" ] || { echo "deckgym hash differs" | tee -a "$LOG"; exit 1; }
[ "$(sha256sum < rl/engine-2026-10-02/goldfish | cut -d' ' -f1)" = "$want_gf" ] || { echo "goldfish hash differs" | tee -a "$LOG"; exit 1; }
[ "$(sha256sum < decks/screen/floor.py | cut -d' ' -f1)" = "$want_fl" ] || { echo "floor.py hash differs" | tee -a "$LOG"; exit 1; }
case "$eng" in */rl/engine-2026-10-02/deckgym) ;; *) echo "current_engine resolves $eng" | tee -a "$LOG"; exit 1;; esac
F="nice -n 10 python3 decks/screen/floor.py"
echo "$(date -u +%F\ %T) FLOOR DRAFTS START" >> "$D/timing.txt"
for d in draft-A-shark-tempo draft-B-tide-heal draft-C-meowstic-hatterene-v2 draft-D-entei-grimhound; do
  if [ -s "$D/$d.md" ]; then echo "$d: page exists, not replayed" >> "$D/timing.txt"; continue; fi
  s=$(date +%s)
  echo "== $d $(date -u +%T)" >> "$LOG"
  $F "decks/brews/drafts_2026-10-01/$d.txt" --out "$D" >> "$LOG" 2>&1
  echo "$d $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
done
echo "$(date -u +%F\ %T) FLOOR DRAFTS DONE" >> "$D/timing.txt"
