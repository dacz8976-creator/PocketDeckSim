#!/usr/bin/env bash
# Addendum, Oct 2 afternoon (README.md and READOUT.md in rl/results/floor_drafts_2026-10-02/): floor.py after 9e139e6
# (sha256 76327865..., its ATTACKERS table names Mega Sharpedo ex for draft A). Run after the Payback equality passed
# (brew-06 and brew-06b: all six outputs byte-equal to rl/results/floor_recheck_2026-10/).
# 1. draft A again, into draft-A_attackers-sharpedo/ (same list, same games; only the main-attacker columns should move);
# 2. draft D as amended at 9e139e6 (one Mega Houndoom ex plus a Copycat), a first page, into draft-D_amended/.
# floor.py's own call with its defaults (km3 both sides, the official engine, 240 games per matchup, seed 7,100).
# One after another, never in parallel, at nice 10. A finished page is not replayed.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; cd "$R"
D="rl/results/floor_drafts_2026-10-02"
LOG="$D/run_addendum.log"
cp "$0" "$D/run_addendum.sh"
want_dg=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
want_gf=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
want_fl=763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0
want_a=3f39092ba6680cc5b8013b961e2f5a0f07bc779816ade7a6891983082b2e7417
want_d=31035755a6d09148a709dd9d869625b7e588f13d0150cac99a9c58ef5469be6f
eng=$(python3 -c 'import sys;sys.path.insert(0,".");from current_engine import resolve;print(resolve(project="."))')
{
  echo "$(date -u +%F\ %T) UTC start; current_engine resolves $eng"
  sha256sum rl/engine-2026-10-02/deckgym rl/engine-2026-10-02/goldfish decks/screen/floor.py decks/screen/opponents/*.txt \
    decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt \
    current_engine.py lib/deckgym-database.json lib/brew_pages.py engine/src/players/public_pricing_player.rs
  echo "git HEAD $(git log -1 --format=%H)"
  echo "git status (decks/screen decks/brews/drafts_2026-10-01 current_engine.py project_manifest.json rl/engine-2026-10-02 lib):"
  git status --short -- decks/screen decks/brews/drafts_2026-10-01 current_engine.py project_manifest.json rl/engine-2026-10-02 lib
} >> "$LOG"
chk() { [ "$(sha256sum < "$1" | cut -d' ' -f1)" = "$2" ] || { echo "$1 hash differs" | tee -a "$LOG"; exit 1; }; }
chk rl/engine-2026-10-02/deckgym $want_dg
chk rl/engine-2026-10-02/goldfish $want_gf
chk decks/screen/floor.py $want_fl
chk decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt $want_a
chk decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt $want_d
case "$eng" in */rl/engine-2026-10-02/deckgym) ;; *) echo "current_engine resolves $eng" | tee -a "$LOG"; exit 1;; esac
F="nice -n 10 python3 decks/screen/floor.py"
for job in "draft-A-shark-tempo draft-A_attackers-sharpedo" "draft-D-entei-grimhound draft-D_amended"; do
  set -- $job; d=$1; out="$D/$2"
  if [ -s "$out/$d.md" ]; then echo "$d: page exists in $out, not replayed" >> "$LOG"; continue; fi
  mkdir -p "$out"
  s=$(date +%s)
  echo "== $d into $out $(date -u +%T)" >> "$LOG"
  $F "decks/brews/drafts_2026-10-01/$d.txt" --out "$out" >> "$LOG" 2>&1
  echo "$d $(( $(date +%s) - s )) s wall" >> "$LOG"
done
chk decks/screen/floor.py $want_fl
echo "$(date -u +%F\ %T) UTC done; floor.py unchanged after the runs" >> "$LOG"
tail -30 "$LOG"
