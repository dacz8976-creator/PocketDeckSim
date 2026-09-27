#!/usr/bin/env bash
# kph's reading runs (REGISTRATION.md section 5), all at the cloud's kph build, in priority order. Written before the
# build lands; the commit and branch are arguments. Built from git archive outside the repo, as kpf's was.
#   0. identity: k3, kp3, kpg3, kpf3 on the table's first 40 deals per pairing equal their official references
#      (kpf's reading runs at 9bffbda, whose engine/ equals the official 83e17ae) on moves, decisions, result.
#   1. table_kph3, new17_kph3 (both sides kph3, the 45 cells); then the FOOTPRINT against kpg3's runs is noted
#      (read first, it fixes the route; nothing else is read before it is committed).
#   2. mixed rows for the vetoes: kph3 on one side, the base kpg3 on the other, 45 cells, first and second.
#   3. Rayquaza traces: 200 Rayquaza v Lucario deals (21,108,900,000+), kph3 on Rayquaza, kp3 on Lucario.
#   4. the mechanism check's dumps: the 840 diagnosed deals (../../kpf_2026-09-26/diagnosis/selected.json), kph3 on
#      the diagnosed deck and kp3 on the other (kpf's diagnosis config), on a watch-only dump build of the same commit.
#   5. held-out and coverage: B2e's 96 pairings (kph3 both sides; 0-47 gate, 48-95 reported), the Scizor row.
# The base is kpg3 (registration section 2). If the composed pilot is in force instead, rerun with BASE set to its code.
# Usage (WSL): nohup setsid bash run_kph_reading.sh <commit> <branch> > run.log 2>&1 &
set -euo pipefail
C=${1:?commit}; BR=${2:?branch, e.g. origin/claude/...}; BASE=${BASE:-kpg3}
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/kph_2026-09-27/reading"; K="$R/rl/results/kpf_2026-09-26/reading"; G="$R/rl/results/kpg_2026-09-27"
DG="$R/rl/results/kpf_2026-09-26/diagnosis"; B=/home/dacz8976/engine-kph-$C; BD=/home/dacz8976/engine-kphdump-$C
NEW=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv; B2E=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
source "$HOME/.cargo/env" 2>/dev/null || true
mkdir -p "$O"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; echo "FAILED: $*" >&2; exit 1; }
for n in cargo rustc 'legality_scan.*' 'deckgym.*'; do ! pgrep -x "$n" >/dev/null || die "busy: $n running"; done
cd "$R"; git fetch -q origin; git merge-base --is-ancestor "$C" "$BR" || die "$C not on $BR"
C=$(git rev-parse "$C")

# Build: the scan and deckgym (for the traces).
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  [ ! -e "$B" ] || die "$B exists without a built scan"
  mkdir -p "$B"; echo "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  s=$(date +%s)
  ( cd "$B/engine" && nice -n 10 cargo build --release -j 14 && nice -n 10 cargo build --release --example legality_scan -j 14 ) \
    > "$O/build.log" 2>&1 || die "build (build.log)"
  note "built $C in $(( $(date +%s) - s )) s"
fi
SCAN="$B/engine/target/release/examples/legality_scan"; DECKGYM="$B/engine/target/release/deckgym"
note "scan sha256 $(sha256sum "$SCAN" | cut -c1-64); deckgym sha256 $(sha256sum "$DECKGYM" | cut -c1-64)"

# Inputs the tree lacks, byte-checked where it has them.
for f in $(git ls-files decks/research); do cmp -s "$f" "$B/$f" || die "$f differs from $C's"; done
for T in "$NEW" "$B2E"; do
  mkdir -p "$B/$(dirname "$T")"; cp "$T" "$B/$T"
  for f in $(tail -n +2 "$T" | cut -f4,6 | tr '\t' '\n' | sort -u); do
    if [ -e "$B/$f" ]; then cmp -s "$f" "$B/$f" || die "$f differs from $C's"; else mkdir -p "$B/$(dirname "$f")"; cp "$f" "$B/$f"; fi
  done
done
note "inputs staged"

# 0. Identity against the official references.
cd "$B/engine"
for bot in k3 kp3 kpg3 kpf3; do
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --decks ../decks/research --games 40 --bot $bot \
    --games-out "$O/identity_${bot}_40.jsonl" > "$O/identity_${bot}_40.txt" 2>&1 || die "identity scan $bot"
  python3 - "$O/identity_${bot}_40.jsonl" "$K/table_${bot}.jsonl" "$bot" >> "$O/identity_check.txt" <<'EOF' || die "IDENTITY FAILED ($bot; identity_check.txt)"
import json, sys
mine = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[1]))}
ref = {}
for g in map(json.loads, open(sys.argv[2])):
    if g["i"] < 40:
        ref[(g["pairing"], g["i"])] = g
fields = [f for f in ("moves", "decisions", "winner_seat", "points", "seed") if all(f in g for g in ref.values())]
bad = [k for k in ref if k not in mine or any(mine[k][f] != ref[k][f] for f in fields)]
print(f"{sys.argv[3]}: kph build vs the official reference: {len(ref) - len(bad)} of {len(ref)} games equal on {fields}")
sys.exit(1 if bad or len(ref) != 1120 else 0)
EOF
done
note "identity: $(tail -4 "$O/identity_check.txt" | tr '\n' ' ')"

run() {  # name bot args...
  local name=$1 bot=$2; shift 2
  [ ! -s "$O/${name}_${bot}.jsonl" ] || { note "$name $bot exists, skipped"; return; }
  local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" "$@" --games 500 --bot "$bot" --games-out "$O/${name}_${bot}.jsonl.part" \
    > "$O/${name}_${bot}.txt" 2>&1 || die "$name $bot scan"
  mv "$O/${name}_${bot}.jsonl.part" "$O/${name}_${bot}.jsonl"
  note "$name $bot done in $(( $(date +%s) - s )) s ($(wc -l < "$O/${name}_${bot}.jsonl") games)"
}
mix() {  # name botA botB args...
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
SCIZ=(--pairs "$B/$NEW" --seed-base 21108000000 --pairings "$(seq -s, 0 7)")
BB=(--pairs "$B/$B2E" --seed-base 21106000000 --pairings "$(seq -s, 0 95)")

# 1. The 45 cells, then the footprint (noted only; read and committed alone before anything else is read).
run table kph3 "${TABLE[@]}"; run new17 kph3 "${NEW17[@]}"
python3 - "$K/table_$BASE.jsonl" "$K/new17_$BASE.jsonl" "$O/table_kph3.jsonl" "$O/new17_kph3.jsonl" > "$O/footprint.txt" <<'EOF'
import json, sys
load = lambda f: {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(f))}
base = {**load(sys.argv[1]), **load(sys.argv[2])}; new = {**load(sys.argv[3]), **load(sys.argv[4])}
assert base.keys() == new.keys(), (len(base), len(new))
diff = [k for k in base if base[k]["moves"] != new[k]["moves"]]
fp = 100 * len(diff) / len(base)
print(f"FOOTPRINT: {len(diff)} of {len(base)} paired games on the 45 cells differ from the base's moves = {fp:.2f}%")
print(f"ROUTE (fixed on this number, before anything else is read): {'RESERVE route (a)-(e)' if fp < 15 else 'ORDINARY adoption rule'}")
EOF
note "footprint written (footprint.txt); commit it alone before reading anything else"

# 2. Mixed rows against the base, 45 cells.
mix mixed_table_kph3_first kph3 "$BASE" "${TABLE[@]}"; mix mixed_table_kph3_second "$BASE" kph3 "${TABLE[@]}"
mix mixed_new17_kph3_first kph3 "$BASE" "${NEW17[@]}"; mix mixed_new17_kph3_second "$BASE" kph3 "${NEW17[@]}"

# 3. Rayquaza traces (the same 200 deals and tracer as kpf's; kp3 on Lucario).
[ -s "$O/trace_rayquaza_v_lucario_kph3.txt" ] || { cd "$R"; nice -n 10 python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py \
  decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt decks/screen/opponents/t-lucario.txt --games 200 --pilot kph3 \
  --opp-pilot kp3 --engine "$DECKGYM" > "$O/trace_rayquaza_v_lucario_kph3.txt" 2>&1 || die "traces"; note "traces done"; }

# 4. The mechanism check's dumps (watch-only instrumentation, as kpf's diagnosis).
if [ ! -x "$BD/engine/target/release/examples/legality_scan" ]; then
  rm -rf "$BD"; mkdir -p "$BD"; git -C "$R" archive "$C" engine decks | tar -x -C "$BD"
  python3 "$DG/instrument_dump2.py" "$BD/engine/examples/legality_scan.rs" >> "$O/STATUS.txt"
  ( cd "$BD/engine" && nice -n 10 cargo build --release --example legality_scan -j 14 ) > "$O/build_dump.log" 2>&1 || die "dump build"
  note "built the dump scan"
fi
if [ ! -s "$O/dump_kph.txt" ]; then
  cd "$BD/engine"
  python3 -c "
import json, collections
d = json.load(open('$DG/selected.json')); g = collections.defaultdict(list)
for x in d: g[(x['pairing'], x['config'])].append(x)
for (p, c), xs in sorted(g.items()): print(p, c, max(x['i'] for x in xs) + 1, ','.join(str(x['seed']) for x in xs))
" | while read -r p cfg n seeds; do
    if [ "$cfg" = first ]; then ba=kph3; bb=kp3; else ba=kp3; bb=kph3; fi
    DUMP_SEEDS="$seeds" RAYON_NUM_THREADS=14 nice -n 10 ./target/release/examples/legality_scan --decks ../decks/research \
      --pairings "$p" --games "$n" --bot-a $ba --bot-b $bb 2>&1 | grep '^DUMP2 ' >> "$O/dump_kph.txt.part" || true
  done
  mv "$O/dump_kph.txt.part" "$O/dump_kph.txt"; note "dumps done ($(wc -l < "$O/dump_kph.txt") lines)"
fi

# 5. Held-out and coverage.
cd "$B/engine"
run b2e kph3 "${BB[@]}"
run scizor kph3 "${SCIZ[@]}"
echo "$(date -u +%F\ %T) KPH READING RUNS DONE" >> "$O/STATUS.txt"
