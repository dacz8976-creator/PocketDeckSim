#!/bin/bash
# Smoke for the positions cost pilot's commands: F and C, one seed each, on the pilot's early position; km3 check on the five check positions.
set -u
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
P="$R/rl/results/pause_games_new_2026-10-12"
K="$R/rl/results/pause_positions_kx3_2026-10/runs_km3"
X=$HOME/pgx
OUT=$HOME/pilot_smoke; mkdir -p "$OUT"
env | grep -qE '^DECKGYM_' && { echo "STOP: DECKGYM_* set"; exit 1; }
DECKARGS=(); for f in "$P"/decks/KW*.txt; do DECKARGS+=(--deck "$(basename "$f" .txt)=$f"); done
echo "nproc $(nproc)"
for id in KW-261005_034953000-t02 KW-261005_034953000-t04 KW-261005_034953000-t08 KW-261005_034953000-t10 KW-261005_034953000-t16; do
  grep -qx "$id" "$R/rl/results/pause_positions_kx3_2026-10/run_ids.txt" || { echo "$id not in run_ids"; continue; }
  for b in F C; do
    "$X/pg_pos_$b" --positions "$P/positions_all.json" "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot km3 --only "$id" > "$OUT/km3_${b}_$id.jsonl" 2> "$OUT/km3_${b}_$id.err"
    python3 - "$OUT/km3_${b}_$id.jsonl" "$K/out_$id.jsonl" "$b $id" <<'EOF'
import json, sys
strip = lambda r: {k: v for k, v in r.items() if k not in ("ms", "time", "elapsed", "wall_s")}
a = [strip(json.loads(l)) for l in open(sys.argv[1]) if l.strip()]
b = [strip(json.loads(l)) for l in open(sys.argv[2]) if l.strip()]
print(f"km3 check {sys.argv[3]}: {'EQUAL' if a == b else 'DIFFERENT'} to the laptop's K run ({len(a)} lines)")
EOF
  done
done
for spec in F:kx3 C:kx3_r16_c12_z2_real_t0_poolmeta_tools_zs3_m64; do
  b=${spec%%:*}; bot=${spec#*:}
  s=$(date +%s.%N)
  /usr/bin/time -f "elapsed %e s, user %U s, sys %S s, maxrss %M KB" "$X/pg_pos_$b" --positions "$P/positions_all.json" "${DECKARGS[@]}" --seeds 1 --bot "$bot" --only KW-261005_034953000-t02 > "$OUT/${b}_t02_seed1.jsonl" 2> "$OUT/${b}_t02_seed1.err"
  echo "$b ($bot) seed 1 on t02: exit $?, $(tail -n 1 "$OUT/${b}_t02_seed1.err"); lines $(grep -c . "$OUT/${b}_t02_seed1.jsonl")"
done
echo "DONE pilot smoke"
