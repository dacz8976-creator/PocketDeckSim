#!/usr/bin/env bash
# B2c for the Altaria detector network (README.md): replay the network's net|kp3 games in the engine, ask kp3 for its
# move at every network decision, and play out both moves where they differ, kp3 piloting both decks afterwards.
#   bash run_b2c.sh              the study: deals 0-399, 16 threads, nice 10, outputs in this folder
#   SMOKE=1 bash run_b2c.sh      the smoke: deals 400-404 (outside the study), 2 threads, nice 19, outputs in smoke/;
#                                also a replay-only sync check of the study's deals 0-9 (no probe, no play-out)
# Steps: 0. build check (the binary and inputs are identity.txt's); 1. the replay-sync check, which must pass on
# every deal before anything else runs (every recorded network move offered at its recorded index, as many network
# decisions as recorded, winner, points, turn and the per-game attack/bench counts equal); 2. probes and play-outs,
# writing decisions.jsonl, net_divergence.txt/.log and timing.txt; 3. analyze.py -> analysis.txt.
# Overrides (env): THREADS, NICE. Never overwrites an existing decisions.jsonl.
# Smoke-only overrides (review, Sept 26): SMOKE_FIRST, SMOKE_N, SMOKE_OUT (deals and folder; defaults 400, 5, smoke/),
# SYNC_FIRST, SYNC_N (the replay-only sync check of study deals; defaults 0, 10). Smoke deals must be 400 or above.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/altaria_network_divergence_2026-09-26"
C=7fc6ccb
B=/home/dacz8976/engine-b2c-$C
EX=net_divergence_kp
BIN="$B/${EX}_$C"
GAMES="$R/rl/results/altaria_network_readout/kp3_rows_games.jsonl"
die() { echo "B2C NOT RUN: $*" >&2; exit 1; }
if [ "${SMOKE:-0}" = 1 ]; then
  FIRST=${SMOKE_FIRST:-400}; N=${SMOKE_N:-5}; OUT=${SMOKE_OUT:-$D/smoke}; THREADS=${THREADS:-2}; NICE=${NICE:-19}
  SYNC_FIRST=${SYNC_FIRST:-0}; SYNC_N=${SYNC_N:-10}
  [ "$FIRST" -ge 400 ] || die "smoke deals start at 400 (the study is deals 0-399)"
else
  FIRST=0; N=400; OUT="$D"; THREADS=${THREADS:-16}; NICE=${NICE:-10}
fi

# 0. Build check: the binary, the example source it was built from (this folder's copy and the scratch copy), the
# decks and the games file are the ones identity.txt records.
[ -x "$BIN" ] || die "no binary at $BIN (run build_b2c.sh)"
SHA=$(sha256sum "$BIN" | cut -d' ' -f1)
[ "$(head -n 1 "$D/identity.txt" | cut -d' ' -f1)" = "$SHA" ] || die "identity.txt names another binary"
for f in "$D/$EX.rs" "$B/engine/examples/$EX.rs"; do
  grep -qxF "example sha256: $(sha256sum "$f" | cut -d' ' -f1)" "$D/identity.txt" \
    || die "$f is not the source identity.txt records (edited since the build? run REBUILD=1 bash build_b2c.sh)"
done
for f in decks/research/altaria.txt decks/research/lucario.txt; do
  grep -qxF "$(cd "$B" && sha256sum "$f")" "$D/identity.txt" || die "$B/$f is not the copy identity.txt records"
done
grep -qxF "$(sha256sum "$GAMES" | cut -d' ' -f1)  rl/results/altaria_network_readout/kp3_rows_games.jsonl" \
  "$D/identity.txt" || die "kp3_rows_games.jsonl changed since the build"
mkdir -p "$OUT"
[ ! -e "$OUT/decisions.jsonl" ] || die "$OUT/decisions.jsonl exists; move it away rather than overwrite it"
run() { RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$BIN" --games-file "$GAMES" --decks "$B/decks/research" "$@"; }
T="$OUT/timing.txt"
echo "$(date '+%F %T %Z') start: binary $SHA, deals $FIRST to $((FIRST + N - 1)), $THREADS threads, nice $NICE," \
     "$(nproc) cores, load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$T"

TIMEFORMAT='%R s wall, %U s user CPU, %S s system CPU'

# 1. The replay-sync check: all N deals, or nothing else runs.
{ time run --first "$FIRST" --games "$N" --sync-only > "$OUT/sync_check.txt" 2> "$OUT/sync_check.log" ; } \
  2> "$OUT/.time" || true
cat "$OUT/sync_check.txt"
grep -q "^SYNC PASS $N of $N games in sync" "$OUT/sync_check.txt" || die "the replay-sync check did not pass (sync_check.txt/.log)"
echo "sync check: $(cat "$OUT/.time")" >> "$T"
if [ "${SMOKE:-0}" = 1 ]; then
  run --first "$SYNC_FIRST" --games "$SYNC_N" --sync-only >> "$OUT/sync_check.txt" 2>> "$OUT/sync_check.log" || true
  tail -n 1 "$OUT/sync_check.txt"
  grep -q "^SYNC PASS $SYNC_N of $SYNC_N games in sync (deals $SYNC_FIRST to" "$OUT/sync_check.txt" \
    || die "the study's deals $SYNC_FIRST to $((SYNC_FIRST + SYNC_N - 1)) are not in sync"
fi

# 2. Probes and play-outs.
{ time run --first "$FIRST" --games "$N" --probes 3 --rollouts 8 --out "$OUT/decisions.jsonl" \
    > "$OUT/net_divergence.txt" 2> "$OUT/net_divergence.log" ; } 2> "$OUT/.time" \
  || die "net_divergence_kp exited non-zero (net_divergence.log)"
cat "$OUT/net_divergence.txt"
grep -q "^$N games (0 rejected" "$OUT/net_divergence.txt" || die "games were rejected in the full run (net_divergence.log)"
echo "divergence (net_divergence_kp $C, probes 3, rollouts 8): $(cat "$OUT/.time"); $(grep '^timing:' "$OUT/net_divergence.log")" >> "$T"
echo "$(date '+%F %T %Z') end, load $(cut -d' ' -f1-3 /proc/loadavg)" >> "$T"
rm -f "$OUT/.time"

# 3. The grouping.
python3 "$D/analyze.py" --file "$OUT/decisions.jsonl" > "$OUT/analysis.txt" || die "analyze.py failed"
echo "written: $OUT/decisions.jsonl, net_divergence.txt, analysis.txt, timing.txt"
