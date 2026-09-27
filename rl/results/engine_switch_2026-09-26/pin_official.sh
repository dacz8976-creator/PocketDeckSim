#!/usr/bin/env bash
# Pin the repaired engine as official (Dustin, Sept 27: "merge, pin the hashes, point the screen at it"), as on Sept 25:
# build deckgym, legality_scan and goldfish from the merge commit in a scratch tree (git archive), then the identity:
# k3 and kp3 over the table's 14,000 deals must equal the repaired engine's references (the cloud's
# af8489f_{k3,kp3}_500.jsonl: moves, decisions, result) and the kpf build's table runs; the command line runs k3 and kp3
# on the screen's seed 7100 (--seed-stream); goldfish --coverage runs. Copies the programs to rl/engine-2026-09-27/ only
# when every check passes. Usage (WSL): bash pin_official.sh <merge commit>
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-26"
C=$1; B=/home/dacz8976/engine-official-$C; P="$R/rl/engine-2026-09-27"
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/PIN_STATUS.txt"; }
die() { note "PIN FAILED: $*"; exit 1; }
cd "$R"
if [ ! -x "$B/engine/target/release/examples/goldfish" ]; then
  rm -rf "$B"; mkdir -p "$B"; git rev-parse "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  ( cd "$B/engine" && nice -n 10 cargo build --release -j 8 && nice -n 10 cargo build --release --example legality_scan -j 8 \
    && nice -n 10 cargo build --release --example goldfish -j 8 ) > "$O/pin_build.log" 2>&1 || die "build (pin_build.log)"
  note "built $C"
fi
E="$B/engine/target/release"
for f in deckgym examples/legality_scan examples/goldfish; do note "sha256 $(sha256sum "$E/$f" | cut -c1-64) $(basename $f)"; done
# Identity over the table.
cd "$B/engine"
for bot in k3 kp3; do
  out="$O/pin_identity_${bot}_500"
  [ -s "$out.jsonl" ] || RAYON_NUM_THREADS=8 nice -n 10 "$E/examples/legality_scan" --decks ../decks/research --games 500 --bot $bot \
    --games-out "$out.jsonl" > "$out.txt" 2>&1 || die "$bot table scan"
  git -C "$R" show "origin/claude/pensive-ptolemy-spwc0b:rl/results/rules09_fixes_2026-09-26/af8489f_${bot}_500.jsonl" > /tmp/ref_${bot}.jsonl
  python3 - "$out.jsonl" /tmp/ref_${bot}.jsonl "$R/rl/results/kpf_2026-09-26/reading/table_${bot}.jsonl" "$bot" >> "$O/pin_identity.txt" <<'EOF' || die "IDENTITY FAILED ($bot)"
import json, sys
load = lambda p: {(g["pairing"], g["i"]): g for g in map(json.loads, open(p))}
new, ref, kpf = load(sys.argv[1]), load(sys.argv[2]), load(sys.argv[3])
f = ("moves", "decisions", "winner_seat", "points", "seed")
a = sum(all(new[k][x] == ref[k][x] for x in f) for k in ref)
b = sum(all(new[k][x] == kpf[k][x] for x in f) for k in kpf)
print(f"{sys.argv[4]}: official build v the repaired engine's reference {a} of {len(ref)}; v the kpf build's table run {b} of {len(kpf)} (fields {f})")
sys.exit(0 if a == len(ref) == 14000 and b == len(kpf) == 14000 else 1)
EOF
done
note "$(tail -2 "$O/pin_identity.txt" | tr '\n' ' ')"
# Command line and goldfish.
cd "$R"
for p in k3,k3 kp3,kp3; do
  "$E/deckgym" simulate --num 240 --players $p --seed 7100 --seed-stream -p decks/research/$(ls decks/research | head -1) decks/research/$(ls decks/research | sed -n 2p) \
    2>&1 | grep -E 'Player 0 won|Player 1 won|Draws' | tr '\n' ' ' | sed "s/^/cli $p: /" >> "$O/pin_identity.txt"; echo >> "$O/pin_identity.txt"
done
( cd "$R/engine" && "$E/examples/goldfish" --deck "$R/decks/research/$(ls "$R/decks/research" | head -1)" --panel "$R/decks/screen/opponents" \
  --games 0 --coverage "$O/pin_goldfish_coverage.json" ) > "$O/pin_goldfish.txt" 2>&1 || die "goldfish --coverage"
note "cli and goldfish ran ($(grep -c '^cli' "$O/pin_identity.txt") cli lines)"
# Pin.
mkdir -p "$P"; cp "$E/deckgym" "$P/deckgym"; cp "$E/examples/legality_scan" "$P/legality_scan"; cp "$E/examples/goldfish" "$P/goldfish"
( cd "$P" && sha256sum deckgym legality_scan goldfish > SHA256SUMS )
note "PINNED in rl/engine-2026-09-27: $(tr '\n' ' ' < "$P/SHA256SUMS")"
echo "$(date -u +%F\ %T) PIN DONE" >> "$O/PIN_STATUS.txt"
