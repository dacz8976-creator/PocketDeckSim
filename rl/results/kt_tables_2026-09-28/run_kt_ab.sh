#!/usr/bin/env bash
# kt on kog, the Dustin-deck A/B (registration "DUSTIN-DECK A/B" in ../kt_2026-09-26/README.md, amendment 2 items 1 and 8;
# the laptop's run, next to run_kt.sh). Decks 07, 05, 11, 01, 03 (decks/dustin/) against the 8 lists in
# decks/screen/opponents, 240 games per matchup (120 per seat) = 1,920 per deck and arm; arms kog3 / kt3 / kta3 on the
# deck's seat, kog3 on the opponent's seat in every arm. Seeds 22,600,000,000 + 10,000 x deck number + 1,000 x opponent
# index (+500 seat 1) + i, i < 120, --seed-stream (the A/B's block, START_HERE's seed table); every arm plays the same
# seeds, so the arms pair by seed. Measures (per-decision traces, kt_ab_play.py, which reuses decks/screen/floor.py's
# run_call): deck win rate, Jasmine offered/played, Barrier/Apron/Heavy Helmet placement; read by read_kt_ab.py.
# Every game is played by the kt build's own deckgym (amendment 2 item 1), its sha256 checked and noted; the output
# file names start with the build's short commit (<build>_ab_d<deck>_<arm>.jsonl, .txt beside).
# Order: kog3's arm for every deck first (not a kt game), then a wait for GATE_koh_b2e_read (before any kt game), then
# deck by deck, kt3 and kta3. Resumable: a finished output is skipped; a unit is written to .part and moved when done.
# Usage (WSL): nohup setsid bash run_kt_ab.sh [<kt build's short commit, default ec7e1a8>] > run_ab.log 2>&1 &
# Knobs (environment; the defaults are the real run): KT_OUT (output folder), KT_BUILD (the build's folder), THREADS (12),
#   NICE (10), DECKS ("07 05 11 01 03"), ARMS ("kog3 kt3 kta3", comparator first), GAMES (240 per matchup),
#   NO_WAIT (set: exit instead of waiting when the gate is closed).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
S=${1:-ec7e1a8}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O=${KT_OUT:-$R/rl/results/kt_tables_2026-09-28}
GATE="$R/rl/results/kt_tables_2026-09-28/GATE_koh_b2e_read"
B=${KT_BUILD:-/home/dacz8976/engine-kt-$S}
THREADS=${THREADS:-12}; NICE=${NICE:-10}; GAMES=${GAMES:-240}
DECKS=${DECKS:-"07 05 11 01 03"}; ARMS=${ARMS:-"kog3 kt3 kta3"}
GYM_EXPECT=407976366fa2104e            # the kt build's deckgym, sha256 prefix (Sept 28)
GYM="$B/engine/target/release/deckgym"
mkdir -p "$O"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; exit 1; }
[ "$(cut -c1-7 "$B/COMMIT" 2>/dev/null)" = "$S" ] || die "run_kt_ab: $B is not the build of $S"
[ -x "$GYM" ] || die "run_kt_ab: no deckgym at $GYM"
GYMFULL=$(sha256sum "$GYM" | cut -d' ' -f1); GYMH=${GYMFULL:0:16}
[ "$GYMH" = "$GYM_EXPECT" ] || die "run_kt_ab: deckgym sha256 $GYMH is not the kt build's $GYM_EXPECT"
# One run at a time (review, Sept 29: two writers on one .part otherwise).
exec 9> "$O/.run_kt_ab.lock"; flock -n 9 || { note "run_kt_ab: another run holds the lock; this one exits"; exit 2; }
# No game on a build whose identity checks haven't passed (run_kt.sh part A); a scratch run (KT_OUT set) skips this.
[ -n "${KT_OUT:-}" ] || grep -q "KT PART A DONE $S" "$O/STATUS.txt" || die "run_kt_ab: run_kt.sh part A (identity) has not passed for $S"
note "run_kt_ab $S: decks $DECKS, arms $ARMS, $GAMES games per matchup, $THREADS threads; kt build deckgym sha256 $GYMFULL; seeds 22,600,000,000 + 10,000 x deck + 1,000 x opponent (+500 seat 1) + i"

gate() {  # no kt game before koh's B2e rows are read and committed (../kt_tables_2026-09-28/README.md)
  if [ ! -e "$GATE" ]; then
    if [ -n "${NO_WAIT:-}" ]; then note "gate closed and NO_WAIT set: no kt game played"; echo "gate closed"; exit 3; fi
    note "waiting for GATE_koh_b2e_read before the first kt game"
    until [ -e "$GATE" ]; do sleep 60; done
    note "gate open: $(cat "$GATE")"
  fi
}
unit() {  # deck arm: 1,920 games (GAMES x 8 opponents), written to .part and moved when done
  local deck=$1 arm=$2 name=${S}_ab_d${1}_${2} s
  if [ -s "$O/$name.jsonl" ]; then  # reused only at its full size (a smoke run's file must never pass as an arm)
    [ "$(wc -l < "$O/$name.jsonl")" -eq $((8 * GAMES)) ] && return
    die "$name.jsonl has $(wc -l < "$O/$name.jsonl") games, not $((8 * GAMES)): move it away first"
  fi
  case $arm in kt*) gate;; esac
  s=$(date +%s)
  ( RAYON_NUM_THREADS=$THREADS nice -n "$NICE" python3 "$HERE/kt_ab_play.py" --deck "$deck" --pilot "$arm" --meta-pilot kog3 \
      --engine "$GYM" --expect-sha "$GYM_EXPECT" --games "$GAMES" --gate "$GATE" --out "$O/$name.jsonl.part" ) > "$O/$name.txt" 2>&1 || die "$name (see $name.txt)"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games); deckgym $GYMH"
}
# kog3's arm first: not a kt game, so it does not wait for the gate.
for arm in $ARMS; do case $arm in kt*) ;; *) for deck in $DECKS; do unit "$deck" "$arm"; done;; esac; done
# then the kt arms, deck by deck (07 first): the first one waits for the gate.
for deck in $DECKS; do for arm in $ARMS; do case $arm in kt*) unit "$deck" "$arm";; esac; done; done
python3 "$HERE/read_kt_ab.py" --dir "$O" --build "$S" --decks "${DECKS// /,}" --arms "${ARMS// /,}" --expect $((8 * GAMES)) > "$O/${S}_ab_table.txt" \
  || die "read_kt_ab.py"
note "A/B table written (${S}_ab_table.txt)"
echo "$(date -u +%F\ %T) KT AB DONE $S" >> "$O/STATUS.txt"
