#!/usr/bin/env bash
# Draft D a second time, from the private copy of floor.py (one ROLES entry: Victini as "bench piece/passive ability";
# proposed role, Dustin's to confirm). Same call, defaults and seeds as the first run; output in draft-D_victini-passive/.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; cd "$R"
S="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_floor/drafts"
D="rl/results/floor_drafts_2026-10-02"; O="$D/draft-D_victini-passive"
export PYTHONDONTWRITEBYTECODE=1
[ -s "$O/draft-D-entei-grimhound.md" ] && { echo "page exists, not replayed"; exit 1; }
[ "$(sha256sum < decks/screen/floor.py | cut -d' ' -f1)" = 8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a ] || { echo "committed floor.py changed"; exit 1; }
[ "$(sha256sum < "$S/floor_victini_passive.py" | cut -d' ' -f1)" = d5a751809b968c9a6a97e9a1f9ccb8e95a0fceab4cabc32861b7262f49c06db3 ] || { echo "copy changed"; exit 1; }
mkdir -p "$O"
cp "$0" "$O/run_d2.sh"; cp "$S/run_copy.py" "$O/run_copy.py"; cp "$S/floor_copy.diff" "$O/floor_copy.diff"
LOG="$O/run.log"
{ echo "$(date -u +%F\ %T) UTC start"; sha256sum decks/screen/floor.py "$S/floor_victini_passive.py" "$S/run_copy.py" rl/engine-2026-10-02/deckgym rl/engine-2026-10-02/goldfish; } >> "$LOG"
s=$(date +%s)
nice -n 10 python3 "$S/run_copy.py" "$S/floor_victini_passive.py" "$R/decks/screen/floor.py" \
  decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt --out "$O" >> "$LOG" 2>&1
echo "draft-D-entei-grimhound (copy, Victini passive) $(( $(date +%s) - s )) s wall" >> "$O/timing.txt"
sha256sum "$O/draft-D-entei-grimhound.md" >> "$LOG"
echo "$(date -u +%F\ %T) UTC done" >> "$LOG"
