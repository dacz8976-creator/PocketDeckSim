#!/usr/bin/env bash
# kog's composition check runs (READING_PLAN.md), at the cloud's kog build a823b6d, built here from git archive outside
# the repo. Identity first (k3/kp3 v the official references; table_kog3 v the cloud's own kog3 table), then the 17 new
# cells and the mixed rows v kp3 on the 45 cells. STATUS.txt logs; the last line is anchored.
# Usage (WSL): nohup setsid bash run_kog_composition.sh > run.log 2>&1 &
set -euo pipefail
C=a823b6d; BR=origin/claude/pensive-ptolemy-spwc0b
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/kog_composition_2026-09-27"; K="$R/rl/results/kpf_2026-09-26/reading"; B=/home/dacz8976/engine-kog-$C
NEW=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; echo "FAILED: $*" >&2; exit 1; }
for n in cargo rustc 'legality_scan.*' 'deckgym.*'; do ! pgrep -x "$n" >/dev/null || die "busy: $n running"; done
cd "$R"; git merge-base --is-ancestor "$C" "$BR" || die "$C not on $BR (fetch it)"

if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  [ ! -e "$B" ] || die "$B exists without a built scan"
  mkdir -p "$B"; git rev-parse "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  s=$(date +%s)
  ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 14 ) > "$O/build.log" 2>&1 || die "build (build.log)"
  note "built $C in $(( $(date +%s) - s )) s"
fi
SCAN="$B/engine/target/release/examples/legality_scan"
note "scan sha256 $(sha256sum "$SCAN" | cut -c1-64) (laptop build of $C; the cloud's is 1fbf3606...)"
for f in $(git ls-files decks/research); do cmp -s "$f" "$B/$f" || die "$f differs from $C's"; done
mkdir -p "$B/$(dirname "$NEW")"; cp "$NEW" "$B/$NEW"
for f in $(tail -n +2 "$NEW" | cut -f4,6 | tr '\t' '\n' | sort -u); do
  if [ -e "$B/$f" ]; then cmp -s "$f" "$B/$f" || die "$f differs from $C's"; else mkdir -p "$B/$(dirname "$f")"; cp "$f" "$B/$f"; fi
done
git show "$BR:rl/results/kog_2026-09-27/a823b6d_kog3_500.jsonl" > "$O/cloud_kog3_500.jsonl"

cmpgames() {  # mine ref label max_i expected_n
  python3 - "$@" >> "$O/identity_check.txt" <<'EOF'
import json, sys
mine = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[1]))}
ref = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[2])) if g["i"] < int(sys.argv[4])}
fields = [f for f in ("moves", "decisions", "openings", "winner_seat", "points", "seed") if all(f in g for g in ref.values())]
bad = [k for k in ref if k not in mine or any(mine[k][f] != ref[k][f] for f in fields)]
print(f"{sys.argv[3]}: {len(ref) - len(bad)} of {len(ref)} games equal on {fields}")
sys.exit(1 if bad or len(ref) != int(sys.argv[5]) else 0)
EOF
}
cd "$B/engine"
for bot in k3 kp3; do
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --decks ../decks/research --games 40 --bot $bot \
    --games-out "$O/identity_${bot}_40.jsonl" > "$O/identity_${bot}_40.txt" 2>&1 || die "identity scan $bot"
  cmpgames "$O/identity_${bot}_40.jsonl" "$K/table_${bot}.jsonl" "$bot at the laptop's $C v the official reference" 40 1120 \
    || die "IDENTITY FAILED ($bot)"
done

run() {  # name botA botB args...
  local name=$1 ba=$2 bb=$3; shift 3
  [ ! -s "$O/$name.jsonl" ] || { note "$name exists, skipped"; return; }
  local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --bot-a "$ba" --bot-b "$bb" --games-out "$O/$name.jsonl.part" \
    > "$O/$name.txt" 2>&1 || die "$name scan"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"
  note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
TABLE=(--decks ../decks/research)
NEW17=(--pairs "$B/$NEW" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
run table_kog3 kog3 kog3 "${TABLE[@]}"
cmpgames "$O/table_kog3.jsonl" "$O/cloud_kog3_500.jsonl" "table_kog3 (laptop) v the cloud's a823b6d_kog3_500" 500 14000 \
  || die "IDENTITY FAILED (table_kog3 v the cloud's)"
note "identity: $(tr '\n' ' ' < "$O/identity_check.txt")"
run new17_kog3 kog3 kog3 "${NEW17[@]}"
run mixed_table_kog3_first kog3 kp3 "${TABLE[@]}"; run mixed_table_kog3_second kp3 kog3 "${TABLE[@]}"
run mixed_new17_kog3_first kog3 kp3 "${NEW17[@]}"; run mixed_new17_kog3_second kp3 kog3 "${NEW17[@]}"
echo "$(date -u +%F\ %T) KOG COMPOSITION RUNS DONE" >> "$O/STATUS.txt"
