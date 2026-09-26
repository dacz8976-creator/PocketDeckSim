#!/usr/bin/env bash
# kpr3 on the 17 new scoreboard cells (Sept 26, diagnostic; pre-repair).
# Why: the pilot traces (../pilot_trace/) show kp3's Rayquaza declining its 100-damage discard attacks on about 40%
# of the turns they're offered; kpr3 (projected readiness; not adopted on the 28 cells, Sept 26) uses them, and a
# kpr3 Rayquaza beat a kp3 Lucario 109 of 200 vs kp3's 43 of 200 on the same deals. So: kpr3 on both sides of the 17
# new cells, on exactly the gauntlet's deals (seed base 21,108,000,000, tsv/new_decks_run.tsv), beside k3 and kp3.
# Build: kpr's commit e09fb46 (git archive engine + decks) + ../../b2e_rows_2026-09-26/legality_scan_pairs.patch
# (legality_scan example only), in /home/dacz8976/engine-kpr-pairs-e09fb46, outside the repo. The cloud showed k3 and
# kp3 play identical games at e09fb46 and at the table's build (1,120 of 1,120); the identity step below checks kp3
# again on 2 pairings x 20 deals of this TSV against ../new_kp3.jsonl before any kpr3 game.
# Usage (WSL): bash run_kpr3_new.sh
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
G="$R/rl/results/gauntlet_runs_2026-09-26"; O="$G/kpr3"
B=/home/dacz8976/engine-kpr-pairs-e09fb46; C=e09fb46
TSV=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks_run.tsv; BASE=21108000000
source "$HOME/.cargo/env" 2>/dev/null || true
die() { echo "$(date -u +%FT%TZ) FAILED: $*" | tee -a "$O/STATUS.txt" >&2; exit 1; }
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
for n in cargo rustc 'legality_scan.*' 'deckgym.*'; do ! pgrep -x "$n" >/dev/null || die "busy: $n running"; done
cd "$R"

# 1. Build.
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  [ ! -e "$B" ] || die "$B exists without a built scan; remove it to rebuild"
  mkdir -p "$B"; git rev-parse "$C" > "$B/COMMIT"
  git archive "$C" engine decks | tar -x -C "$B"
  ( cd "$B" && patch -p1 --no-backup-if-mismatch < "$R/rl/results/b2e_rows_2026-09-26/legality_scan_pairs.patch" ) > "$O/patch.log" 2>&1 \
    || die "patch failed (patch.log)"
  s=$(date +%s)
  ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 14 ) > "$O/build.log" 2>&1 || die "build failed (build.log)"
  note "built in $(( $(date +%s) - s )) s"
fi
SCAN="$B/engine/target/release/examples/legality_scan"
note "scan sha256 $(sha256sum "$SCAN" | cut -c1-64) ($C + legality_scan_pairs.patch)"

# 2. Inputs, at the same relative paths; files the tree already has must be byte-identical to the working copy.
mkdir -p "$B/$(dirname "$TSV")" "$B/decks/gauntlet_2026-09-26"
cp "$TSV" "$B/$TSV"
for f in $(tail -n +2 "$TSV" | cut -f4,6 | tr '\t' '\n' | sort -u); do
  if [ -e "$B/$f" ]; then cmp -s "$f" "$B/$f" || die "$f differs between the working copy and $C"; else cp "$f" "$B/$f"; fi
done
note "inputs staged: $(tail -n +2 "$TSV" | wc -l) pairings"

# 3. Identity: kp3 on the first 2 pairings x 20 deals equals ../new_kp3.jsonl's same games.
head -3 "$TSV" > "$B/$TSV.id2"
cd "$B/engine"
RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --pairs "$B/$TSV.id2" --seed-base "$BASE" --games 20 --bot kp3 \
  --games-out "$O/identity_kp3_2x20.jsonl" > "$O/identity_kp3_2x20.txt" 2>&1 || die "identity scan failed"
python3 - "$O/identity_kp3_2x20.jsonl" "$G/new_kp3.jsonl" > "$O/identity_check.txt" <<'EOF' || die "IDENTITY FAILED (identity_check.txt)"
import json, sys
new = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[1]))}
ref = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[2]))}
keys = ("moves", "winner_seat", "points", "seed", "turns")
bad = [k for k, g in new.items() if any(g[f] != ref[k][f] for f in keys)]
print(f"identity kp3 at e09fb46+pairs vs the gauntlet's 7fc6ccb kp3: {len(new) - len(bad)} of {len(new)} games equal on {keys}")
sys.exit(1 if bad or len(new) != 40 else 0)
EOF
note "$(cat "$O/identity_check.txt")"

# 4. kpr3, both sides, all 17 pairings x 500.
s=$(date +%s)
RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --pairs "$B/$TSV" --seed-base "$BASE" --games 500 --bot kpr3 \
  --games-out "$O/new_kpr3.jsonl.part" > "$O/new_kpr3.txt" 2>&1 || die "kpr3 scan failed"
mv "$O/new_kpr3.jsonl.part" "$O/new_kpr3.jsonl"
note "kpr3 DONE in $(( $(date +%s) - s )) s, $(wc -l < "$O/new_kpr3.jsonl") games"
echo "$(date -u +%F\ %T) KPR3 RUN DONE" >> "$O/STATUS.txt"
