#!/usr/bin/env bash
# The laptop's share of the rules/09 fix replays (Dustin, Sept 26: "split them onto the laptop"). Same games and
# same program as the cloud's run_replay.sh on claude/pensive-ptolemy-spwc0b: k3 and kp3 over the table's 14,000
# games (28 pairings x the first 500 deals, 72,000,000 + pairing x 10,000 + i, even i = first-named deck in seat 0),
# legality_scan as it stands at each fix commit (the example is a03f491's at every one of them; the counters only
# watch). The cloud keeps 5bab907, 5b75bf9 and 3102c9e; the laptop takes 3c2250f, 14745ce, 050cf51 and a30b5f8.
# Each commit is built from git archive (engine + decks) in its own folder outside the repo, as the kd, kpr and B2e
# builds were, so the shared working copy is never checked out or built in. Outputs use the cloud's file names
# (<commit>_<bot>_500.jsonl/.txt) so compare.py reads both machines' files together; this script logs to
# timing_laptop.txt (never the cloud's timing.txt). Nothing else heavy runs on the laptop meanwhile.
# Usage (in WSL):  bash run_replay_laptop.sh [commit ...]      (default: the four above, in fix order)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/rules09_fixes_2026-09-26"
T="$D/timing_laptop.txt"
source "$HOME/.cargo/env" 2>/dev/null || true
COMMITS=("$@"); [ "${#COMMITS[@]}" -gt 0 ] || COMMITS=(3c2250f 14745ce 050cf51 a30b5f8)
die() { echo "$(date -u +%FT%TZ) FAILED: $*" | tee -a "$T" >&2; exit 1; }
# Never two builds or game runs at once on 7 GB (the Sept 25 load incident): wait while another cargo, rustc or
# scan program is running, matched on the process name (pgrep -x), so this script's own command line can't match.
wait_idle() { while pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null || pgrep -x 'legality_scan.*' >/dev/null \
  || pgrep -x 'deckgym.*' >/dev/null; do sleep 30; done; }
cd "$R"
echo "$(date -u +%FT%TZ) laptop replay start: ${COMMITS[*]}; $(rustc --version); $(nproc) cores" >> "$T"

# 1. Builds (all first, so a failed build shows before any hour of games).
for c in "${COMMITS[@]}"; do
  B="/home/dacz8976/engine-fix-$c"
  full=$(git rev-parse "$c^{commit}") || die "commit $c not found (fetch origin claude/pensive-ptolemy-spwc0b)"
  git merge-base --is-ancestor "$full" origin/claude/pensive-ptolemy-spwc0b || die "$c is not on the cloud branch"
  [ -z "$(git diff a03f491 "$full" -- engine/examples/legality_scan.rs)" ] || die "$c's legality_scan differs from a03f491's"
  [ -z "$(git diff 7fc6ccb "$full" -- decks/research)" ] || die "$c's decks/research differs from the table's (7fc6ccb)"
  if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
    [ ! -e "$B" ] || die "$B exists without a built scan; remove it to rebuild"
    mkdir -p "$B"; echo "$full" > "$B/COMMIT"
    git archive "$full" engine decks | tar -x -C "$B"
    wait_idle; s=$(date +%s)
    ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 14 > "$B/build.log" 2>&1 ) \
      || die "build of $c failed; see $B/build.log"
    echo "$c build $(( $(date +%s) - s )) s" >> "$T"
  fi
  echo "$c scan sha256 $(sha256sum "$B/engine/target/release/examples/legality_scan" | cut -c1-64) (laptop build, $full)" >> "$T"
done

# 2. Replays, in fix order, k3 then kp3 (the cloud's order within a commit).
for c in "${COMMITS[@]}"; do
  B="/home/dacz8976/engine-fix-$c"; SCAN="$B/engine/target/release/examples/legality_scan"
  cd "$B/engine"
  for bot in k3 kp3; do
    out="$D/${c}_${bot}_500"
    [ ! -s "$out.jsonl" ] || { echo "$c $bot already done, skipped" >> "$T"; continue; }
    wait_idle; s=$(date +%s)
    RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --decks ../decks/research --games 500 --bot "$bot" \
      --games-out "$out.jsonl.part" > "$out.txt" 2>&1 || die "$c $bot scan failed; see $out.txt"
    mv "$out.jsonl.part" "$out.jsonl"
    echo "${c}_${bot}_500 $(( $(date +%s) - s )) s wall (14 threads of $(nproc), nice 10, $(date -u +%FT%TZ) end; $(wc -l < "$out.jsonl") games)" >> "$T"
  done
done
echo "$(date -u +%F\ %T) LAPTOP REPLAY DONE" >> "$T"
