#!/bin/bash
# kn smoke: builds kn_smoke in a scratch copy of the official engine's source (d363ba8's engine/) with this commit's
# engine/src/players/, then plays each scratch deck against each scratch opponent, both seats, 100 games a seat, with
# km3 and then kn3 as the deck's pilot (km3 the opponent's in both arms, on the same seeds). Seeds: Claude diagnostic
# 20,960,000,000 + 100,000 x deck + 10,000 x opponent + 5,000 x seat + game.
# Usage: bash run_smoke.sh <scratch dir> <commit with kn>   (from anywhere; writes games.jsonl here)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(git -C "$HERE" rev-parse --show-toplevel)
S=$1; KN=$2
rm -rf "$S/engine" "$S/base" && mkdir -p "$S/base"
git -C "$ROOT" archive d363ba8 engine | tar -x -C "$S/base"
git -C "$ROOT" archive d363ba8 engine | tar -x -C "$S"
rm -rf "$S/engine/src/players" && git -C "$ROOT" archive "$KN" engine/src/players | tar -x -C "$S"
cp "$HERE/kn_smoke.rs" "$S/engine/examples/kn_smoke.rs"
# The scratch engine differs from d363ba8's only in src/players/ (the commit's) and the added example.
{ diff -rq "$S/base/engine" "$S/engine" || true; } | tee "$HERE/scratch_engine_diff.txt"
(cd "$S/engine" && cargo build --release --example kn_smoke 2>&1 | tail -1)
BIN="$S/engine/target/release/examples/kn_smoke"
sha256sum "$BIN" | sed "s#  .*#  kn_smoke (scratch build)#" > "$HERE/kn_smoke.sha256"
rm -f "$S"/part_*.jsonl
# psychic carries no N1 card: its arm is the control, counting Cyrus, for the games N1 changes elsewhere.
d=0
for deck in goo grass_goo plaza psychic; do
  case $deck in plaza) card="Peculiar Plaza";; psychic) card="Cyrus";; *) card="Team Rocket's Goo-zooka";; esac
  o=0
  for opp in water_boat fire_balloon psychic; do
    for seat in 0 1; do
      seed=$((20960000000 + 100000 * d + 10000 * o + 5000 * seat))
      for code in km3 kn3; do
        "$BIN" --deck "$HERE/$deck.txt" --opp "$HERE/$opp.txt" --card "$card" --seat $seat --seed $seed --num 100 \
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
