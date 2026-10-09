#!/usr/bin/env bash
# P3's smoke (the cloud, Oct 9): does making a Fossil an Item card at the seven other places change any game? No list in any
# replayed set holds a Fossil (README, P3), so no recorded game can; this plays the lists nearest to it. pairs.tsv: brew-04
# (the only replayed list holding one of the affected cards: 2 Team Rocket's Slowpoke, Scavenge) and the Rayquaza carrier
# list (kt_carrier_census_2026-09-26; 1 Skull Fossil, no card reading it), each v the 8 panel lists; km3 on both sides, 40
# deals a pairing, seeds 20,920,000,000 + pairing x 10,000 + i. The engine before P3 and P3's, each built from `git archive`
# in its own target folder; every game's row must be the same.
# Usage: run_p3_smoke.sh <work dir> <revision before P3> <P3's revision>   (from anywhere in the repository)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
mkdir -p "$W"
for v in before:$2 p3:$3; do
    name=${v%%:*} rev=${v#*:}
    rm -rf "${W:?}/$name" "$W/target_$name" && mkdir -p "$W/$name"
    git -C "$REPO" archive "$rev" engine | tar -x -C "$W/$name"
    (cd "$W/$name/engine" && CARGO_TARGET_DIR="$W/target_$name" cargo build --release --locked --example legality_scan 2>&1 | grep -E "^error" || true)
    echo "$name: $(git -C "$REPO" rev-parse --short "$rev"), legality_scan sha256 $(sha256sum < "$W/target_$name/release/examples/legality_scan" | cut -c1-64)"
done
for name in before p3; do
    (cd "$REPO" && "$W/target_$name/release/examples/legality_scan" --pairs "$HERE/pairs.tsv" --root . --seed-base 20920000000 \
        --games 40 --bot km3 --games-out "$W/games_$name.jsonl" > "$W/page_$name.txt" 2>&1) &
done
wait
python3 - "$W" <<'PY'
import json, sys
W = sys.argv[1]
load = lambda n: {(r["pairing"], r["i"]): r for r in map(json.loads, open(f"{W}/games_{n}.jsonl"))}
a, b = load("before"), load("p3")
same = sum(a[k] == b.get(k) for k in a)
print(f"games: before P3 {len(a)}, P3 {len(b)}; the same row (every field) in {same}; different: {sorted(k for k in a if a[k] != b.get(k))}")
for p in sorted({k[0] for k in a}):
    ks = [k for k in a if k[0] == p]
    print(f"  pairing {p:2d} {a[ks[0]]['a']} v {a[ks[0]]['b']}: {sum(a[k] == b[k] for k in ks)} of {len(ks)} the same")
PY
