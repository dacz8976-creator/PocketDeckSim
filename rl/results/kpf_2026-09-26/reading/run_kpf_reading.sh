#!/usr/bin/env bash
# kpf's reading runs (registration section 6; the cloud's BUILD.md "What the laptop runs next"), all at kpf's build
# 9bffbda (engine e935f42 = the repaired engine + koa and kpf player code; its legality_scan carries the --pairs patch).
# Built here from git archive in /home/dacz8976/engine-kpf-9bffbda (outside the repo). Inputs the tree lacks (the
# gauntlet's and B2e's TSVs and deck files) are copied from the working copy at the same relative paths; files the
# tree has must be byte-identical to the working copy. Identity first: k3 and kp3 on the table's first 40 deals equal
# the cloud's identity_{k3,kp3}_40.jsonl at the same build (moves, decisions if present, result).
# Runs, in priority order (each writes <name>.jsonl/.txt here; STATUS.txt logs; the last line is anchored):
#   table_<bot>   : the 28 table cells, 72,000,000 + p x 10,000 + i, i < 500 (default scan mode)
#   new17_<bot>   : the 17 new scoreboard cells, pairings 8-24 of the gauntlet's new_decks.tsv, base 21,108,000,000
#   b2e_<bot>     : B2e's 96 pairings (0-47 archetypes, 48-95 Dustin's files), base 21,106,000,000
#   scizor_<bot>  : the Scizor coverage row, pairings 0-7 of new_decks.tsv (the promotion repair is in this build)
# Bots: kpf3, kp3, k3, kpr3 on table/new17; kpf3, kp3 on b2e; kpg3 on table/new17; kpf3, kp3, k3 on scizor.
# Usage (WSL): nohup setsid bash run_kpf_reading.sh > run.log 2>&1 &
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/kpf_2026-09-26/reading"; B=/home/dacz8976/engine-kpf-9bffbda; C=9bffbda
BR=origin/claude/pensive-ptolemy-spwc0b
NEW=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv; B2E=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; echo "FAILED: $*" >&2; exit 1; }
for n in cargo rustc 'legality_scan.*' 'deckgym.*'; do ! pgrep -x "$n" >/dev/null || die "busy: $n running"; done
cd "$R"; git merge-base --is-ancestor "$C" "$BR" || die "$C not on $BR (fetch it)"

# 1. Build.
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  [ ! -e "$B" ] || die "$B exists without a built scan"
  mkdir -p "$B"; git rev-parse "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  s=$(date +%s)
  ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 14 ) > "$O/build.log" 2>&1 || die "build (build.log)"
  note "built $C in $(( $(date +%s) - s )) s"
fi
SCAN="$B/engine/target/release/examples/legality_scan"
note "scan sha256 $(sha256sum "$SCAN" | cut -c1-64) (laptop build of $C; the cloud's is 518d3f60...)"

# 2. Inputs.
for f in $(git ls-files decks/research); do cmp -s "$f" "$B/$f" || die "$f differs from $C's"; done
for T in "$NEW" "$B2E"; do
  mkdir -p "$B/$(dirname "$T")"; cp "$T" "$B/$T"
  for f in $(tail -n +2 "$T" | cut -f4,6 | tr '\t' '\n' | sort -u); do
    if [ -e "$B/$f" ]; then cmp -s "$f" "$B/$f" || die "$f differs from $C's"; else mkdir -p "$B/$(dirname "$f")"; cp "$f" "$B/$f"; fi
  done
done
note "inputs staged"

# 3. Identity against the cloud's runs at the same build.
cd "$B/engine"
for bot in k3 kp3; do
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --decks ../decks/research --games 40 --bot $bot \
    --games-out "$O/identity_${bot}_40.jsonl" > "$O/identity_${bot}_40.txt" 2>&1 || die "identity scan $bot"
  git -C "$R" show "$BR:rl/results/kpf_2026-09-26/identity_${bot}_40.jsonl" > "/tmp/cloud_identity_${bot}_40.jsonl"
  python3 - "$O/identity_${bot}_40.jsonl" "/tmp/cloud_identity_${bot}_40.jsonl" "$bot" >> "$O/identity_check.txt" <<'EOF' || die "IDENTITY FAILED ($bot; identity_check.txt)"
import json, sys
mine = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[1]))}
cloud = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[2]))}
fields = [f for f in ("moves", "decisions", "winner_seat", "points", "seed") if all(f in g for g in cloud.values())]
common = [k for k in cloud if k in mine]
bad = [k for k in common if any(mine[k][f] != cloud[k][f] for f in fields)]
print(f"{sys.argv[3]}: laptop build of 9bffbda vs the cloud's identity file: {len(common) - len(bad)} of {len(common)} common games equal on {fields} (cloud file {len(cloud)} games, laptop {len(mine)})")
sys.exit(1 if bad or len(common) < 900 else 0)
EOF
done
note "$(tail -2 "$O/identity_check.txt" | tr '\n' ' ')"

# 4. Runs.
run() {  # name bot args...
  local name=$1 bot=$2; shift 2
  [ ! -s "$O/${name}_${bot}.jsonl" ] || { note "$name $bot exists, skipped"; return; }
  local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --bot "$bot" --games-out "$O/${name}_${bot}.jsonl.part" \
    > "$O/${name}_${bot}.txt" 2>&1 || die "$name $bot scan"
  mv "$O/${name}_${bot}.jsonl.part" "$O/${name}_${bot}.jsonl"
  note "$name $bot done in $(( $(date +%s) - s )) s ($(wc -l < "$O/${name}_${bot}.jsonl") games)"
}
TABLE=(--decks ../decks/research)
NEW17=(--pairs "$B/$NEW" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
SCIZ=(--pairs "$B/$NEW" --seed-base 21108000000 --pairings "$(seq -s, 0 7)")
BB=(--pairs "$B/$B2E" --seed-base 21106000000 --pairings "$(seq -s, 0 95)")
for bot in kpf3 kp3; do run table $bot "${TABLE[@]}"; run new17 $bot "${NEW17[@]}"; done
for bot in k3 kpr3; do run table $bot "${TABLE[@]}"; run new17 $bot "${NEW17[@]}"; done
for bot in kpf3 kp3; do run b2e $bot "${BB[@]}"; done
run table kpg3 "${TABLE[@]}"; run new17 kpg3 "${NEW17[@]}"
for bot in kpf3 kp3 k3; do run scizor $bot "${SCIZ[@]}"; done
echo "$(date -u +%F\ %T) KPF READING RUNS DONE" >> "$O/STATUS.txt"
