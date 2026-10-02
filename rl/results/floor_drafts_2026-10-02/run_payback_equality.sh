#!/usr/bin/env bash
# Step 1: Payback equality. floor.py (sha256 76327865..., ATTACKERS table) on brew-06 and brew-06b, its defaults
# (km3 both sides, seed 7100, 240 per matchup), into this scratch folder; then every output compared byte for byte with
# rl/results/floor_recheck_2026-10/ (made on main-8626a35 with floor.py 8e5395e6...). One after another, nice 10.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1
S="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_floor2/attackers"
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; cd "$R"
OUT="$S/payback"; REF="rl/results/floor_recheck_2026-10"; LOG="$S/step1.log"
mkdir -p "$OUT"
for f in "$OUT"/*; do [ -e "$f" ] && { echo "REFUSED: $f exists"; exit 2; }; done
want_dg=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
want_gf=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
want_fl=763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0
eng=$(python3 -c 'import sys;sys.path.insert(0,".");from current_engine import resolve;print(resolve(project="."))')
{
  echo "$(date -u +%F\ %T) UTC step 1 start; current_engine resolves $eng"
  sha256sum rl/engine-2026-10-02/deckgym rl/engine-2026-10-02/goldfish decks/screen/floor.py decks/screen/opponents/*.txt \
    decks/brews/brew-06-pyukumuku-silvally-payback.txt decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt \
    current_engine.py lib/deckgym-database.json lib/brew_pages.py engine/src/players/public_pricing_player.rs
  echo "git HEAD $(git log -1 --format=%H)"
  echo "git status (decks/screen decks/brews current_engine.py project_manifest.json rl/engine-2026-10-02 lib):"
  git status --short -- decks/screen decks/brews current_engine.py project_manifest.json rl/engine-2026-10-02 lib
} >> "$LOG"
[ "$(sha256sum < rl/engine-2026-10-02/deckgym | cut -d' ' -f1)" = "$want_dg" ] || { echo "deckgym hash differs" | tee -a "$LOG"; exit 1; }
[ "$(sha256sum < rl/engine-2026-10-02/goldfish | cut -d' ' -f1)" = "$want_gf" ] || { echo "goldfish hash differs" | tee -a "$LOG"; exit 1; }
[ "$(sha256sum < decks/screen/floor.py | cut -d' ' -f1)" = "$want_fl" ] || { echo "floor.py hash differs" | tee -a "$LOG"; exit 1; }
case "$eng" in */rl/engine-2026-10-02/deckgym) ;; *) echo "current_engine resolves $eng" | tee -a "$LOG"; exit 1;; esac
for d in brew-06-pyukumuku-silvally-payback brew-06b-pyukumuku-silvally-scyther-grass; do
  s=$(date +%s)
  echo "== $d $(date -u +%T)" >> "$LOG"
  nice -n 10 python3 decks/screen/floor.py "decks/brews/$d.txt" --out "$OUT" >> "$LOG" 2>&1
  echo "$d $(( $(date +%s) - s )) s wall" >> "$LOG"
done
echo "== comparison $(date -u +%T)" >> "$LOG"
neq=0
for d in brew-06-pyukumuku-silvally-payback brew-06b-pyukumuku-silvally-scyther-grass; do
  for x in .md _coverage.json _games.jsonl; do
    a="$OUT/$d$x"; b="$REF/$d$x"
    ha=$(sha256sum < "$a" | cut -d' ' -f1); hb=$(sha256sum < "$b" | cut -d' ' -f1)
    if cmp -s "$a" "$b"; then r=BYTE-EQUAL; else r=DIFFERS; neq=$((neq+1)); fi
    echo "$r $d$x new $ha ref $hb" >> "$LOG"
  done
done
[ "$(sha256sum < decks/screen/floor.py | cut -d' ' -f1)" = "$want_fl" ] && echo "floor.py unchanged after the runs" >> "$LOG"
echo "$(date -u +%F\ %T) UTC step 1 done; files differing: $neq" >> "$LOG"
ls "$OUT" >> "$LOG"
tail -20 "$LOG"
