#!/bin/bash
# kr smoke: kn's smoke (../../kn_build_2026-09-30/smoke/: its scratch decks, its kn_smoke.rs, its seeds) with three
# arms for the deck's pilot: km3, kr3 and kro3 (km3 the opponent's in all three, on the same seeds). Builds kn_smoke in
# a scratch copy of the official engine's source (d363ba8's engine/) with the given commit's engine/src/players/.
# Seeds: Claude diagnostic 20,960,000,000 + 100,000 x deck + 10,000 x opponent + 5,000 x seat + game, as kn's smoke,
# so the km3 arm should repeat kn's smoke's km3 games exactly.
# Usage: bash run_smoke.sh <scratch dir> <commit with kr>   (writes games.jsonl here)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(git -C "$HERE" rev-parse --show-toplevel)
KN=$ROOT/rl/results/kn_build_2026-09-30/smoke
S=$1; KR=$2
rm -rf "$S/engine" "$S/base" && mkdir -p "$S/base"
git -C "$ROOT" archive d363ba8 engine | tar -x -C "$S/base"
git -C "$ROOT" archive d363ba8 engine | tar -x -C "$S"
rm -rf "$S/engine/src/players" && git -C "$ROOT" archive "$KR" engine/src/players | tar -x -C "$S"
cp "$KN/kn_smoke.rs" "$S/engine/examples/kn_smoke.rs"
# The scratch engine differs from d363ba8's only in src/players/ (the commit's) and the added example.
{ diff -rq "$S/base/engine" "$S/engine" || true; } | sed "s#$S#<scratch>#g" | tee "$HERE/scratch_engine_diff.txt"
(cd "$S/engine" && cargo build --release --example kn_smoke 2>&1 | tail -1)
BIN="$S/engine/target/release/examples/kn_smoke"
sha256sum "$BIN" | sed "s#  .*#  kn_smoke (scratch build)#" > "$HERE/kn_smoke.sha256"
sha256sum "$KN/kn_smoke.rs" | sed "s#  .*#  kn_smoke.rs (kn's smoke program, used as it is)#" >> "$HERE/kn_smoke.sha256"
rm -f "$S"/part_*.jsonl
d=0
for deck in goo grass_goo plaza psychic; do
  case $deck in plaza) card="Peculiar Plaza";; psychic) card="Cyrus";; *) card="Team Rocket's Goo-zooka";; esac
  o=0
  for opp in water_boat fire_balloon psychic; do
    for seat in 0 1; do
      seed=$((20960000000 + 100000 * d + 10000 * o + 5000 * seat))
      for code in km3 kr3 kro3; do
        "$BIN" --deck "$KN/$deck.txt" --opp "$KN/$opp.txt" --card "$card" --seat $seat --seed $seed --num 100 \
          --codes "$code,km3" > "$S/part_${deck}_${opp}_${seat}_${code}.jsonl" &
      done
    done
    wait
    o=$((o + 1))
  done
  d=$((d + 1))
done
cat "$S"/part_*.jsonl | sort > "$HERE/games.jsonl"
wc -l "$HERE/games.jsonl"
