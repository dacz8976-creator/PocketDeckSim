#!/usr/bin/env bash
# The kog engine switch (Dustin, Sept 28: "Pin it now", with the conditions of the last switch), part 1: build and
# identity only, nothing pinned. Builds deckgym, legality_scan and goldfish from commit C (the cloud branch head; the
# branch contains main, so the merge is a fast-forward to C) in a scratch tree, then:
#   - k3 and kp3 over the table's 14,000 deals equal the official references (the kpf build's table runs, which equal
#     the cloud's af8489f references; moves, decisions, result);
#   - kog3 over the 14,000 equals the cloud's a823b6d_kog3_500.jsonl and the laptop's composition table_kog3;
#   - deckgym simulate runs k3, kp3 and kog3 on the screen's seed 7100 (--seed-stream); goldfish --coverage runs.
# Part 2 (pin_finish.sh) copies the programs and updates the manifest, only after Dustin's ruling on the hooks refactor.
# Usage (WSL): bash pin_prepare.sh <commit>
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-28"
C=$(git -C "$R" rev-parse "$1"); B=/home/dacz8976/engine-official-${C:0:7}
BR=origin/claude/pensive-ptolemy-spwc0b
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/PIN_STATUS.txt"; }
die() { note "PREPARE FAILED: $*"; exit 1; }
cd "$R"
if [ ! -x "$B/engine/target/release/examples/goldfish" ]; then
  rm -rf "$B"; mkdir -p "$B"; echo "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  ( cd "$B/engine" && nice -n 10 cargo build --release -j 14 && nice -n 10 cargo build --release --example legality_scan -j 14 \
    && nice -n 10 cargo build --release --example goldfish -j 14 ) > "$O/pin_build.log" 2>&1 || die "build (pin_build.log)"
  note "built $C"
fi
E="$B/engine/target/release"
for f in deckgym examples/legality_scan examples/goldfish; do note "sha256 $(sha256sum "$E/$f" | cut -c1-64) $(basename $f)"; done
git show "$BR:rl/results/kog_2026-09-27/a823b6d_kog3_500.jsonl" > /tmp/ref_kog3.jsonl
cd "$B/engine"
for bot in k3 kp3 kog3; do
  out="$O/pin_identity_${bot}_500"
  [ -s "$out.jsonl" ] || RAYON_NUM_THREADS=14 nice -n 10 "$E/examples/legality_scan" --decks ../decks/research --games 500 --bot $bot \
    --games-out "$out.jsonl" > "$out.txt" 2>&1 || die "$bot table scan"
  if [ $bot = kog3 ]; then refs=(/tmp/ref_kog3.jsonl "$R/rl/results/kog_composition_2026-09-27/table_kog3.jsonl")
  else refs=("$R/rl/results/kpf_2026-09-26/reading/table_${bot}.jsonl"); fi
  python3 - "$out.jsonl" "$bot" "${refs[@]}" >> "$O/pin_identity.txt" 2>> "$O/pin_identity.err" <<'EOF' || die "IDENTITY FAILED ($bot)"
import json, sys
load = lambda p: {(g["pairing"], g["i"]): g for g in map(json.loads, open(p))}
new = load(sys.argv[1]); ok = True; parts = []
for ref_path in sys.argv[3:]:
    ref = load(ref_path)
    f = [x for x in ("moves", "decisions", "openings", "winner_seat", "points", "seed") if all(x in g for g in ref.values())]
    a = sum(k in new and all(new[k][x] == ref[k][x] for x in f) for k in ref)
    ok &= a == len(ref) == 14000
    parts.append(f"v {ref_path.split('/rl/results/')[-1] if '/rl/results/' in ref_path else ref_path} {a} of {len(ref)}")
print(f"{sys.argv[2]} at the new build: " + "; ".join(parts))
sys.exit(0 if ok else 1)
EOF
done
note "$(tail -3 "$O/pin_identity.txt" | tr '\n' ' ')"
cd "$R"
for p in k3,k3 kp3,kp3 kog3,kog3; do
  "$E/deckgym" simulate --num 240 --players $p --seed 7100 --seed-stream -p decks/research/$(ls decks/research | head -1) decks/research/$(ls decks/research | sed -n 2p) \
    2>&1 | grep -E 'Player 0 won|Player 1 won|Draws' | tr '\n' ' ' | sed "s/^/cli $p: /" >> "$O/pin_identity.txt"; echo >> "$O/pin_identity.txt"
done
( cd "$R/engine" && "$E/examples/goldfish" --deck "$R/decks/research/$(ls "$R/decks/research" | head -1)" --panel "$R/decks/screen/opponents" \
  --games 0 --coverage "$O/pin_goldfish_coverage.json" ) > "$O/pin_goldfish.txt" 2>&1 || die "goldfish --coverage"
note "cli and goldfish ran ($(grep -c '^cli' "$O/pin_identity.txt") cli lines)"
echo "$(date -u +%F\ %T) PREPARE DONE $C" >> "$O/PIN_STATUS.txt"
