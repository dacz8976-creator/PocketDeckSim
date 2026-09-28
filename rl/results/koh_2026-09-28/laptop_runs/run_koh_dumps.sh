#!/usr/bin/env bash
# koh's mechanism check dumps (kph registration section 5 step 3): the 840 diagnosed deals
# (../../kpf_2026-09-26/diagnosis/selected.json), koh3 on the diagnosed deck and kp3 on the other (the diagnosis's
# config), traced move by move with the watch-only dump hook (../../kpf_2026-09-26/diagnosis/instrument_dump2.py) on a
# scratch tree of the official source 233bced. The same loop as run_dumps.sh, so a seed traced twice (both configs) is
# split where the tick restarts, in the same (pairing, config) order. Waits for run_koh_laptop.sh's anchored last line.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koh_2026-09-28/laptop_runs"
DG="$R/rl/results/kpf_2026-09-26/diagnosis"; C=233bced; BD=/home/dacz8976/engine-kohdump-$C
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS_dumps.txt"; }
if [ ! -x "$BD/engine/target/release/examples/legality_scan" ]; then
  rm -rf "$BD"; mkdir -p "$BD"; git -C "$R" archive $C engine decks | tar -x -C "$BD"
  python3 "$DG/instrument_dump2.py" "$BD/engine/examples/legality_scan.rs" >> "$O/STATUS_dumps.txt"
  ( cd "$BD/engine" && nice -n 10 cargo build --release --example legality_scan -j 6 ) > "$O/build_dump.log" 2>&1 || { note "FAILED build"; exit 1; }
  note "built the dump scan at $C"
fi
until grep -q 'KOH LAPTOP RUNS DONE' "$O/STATUS.txt" 2>/dev/null; do grep -q 'FAILED' "$O/STATUS.txt" 2>/dev/null && exit 1; sleep 60; done
[ -s "$O/dump_koh.txt" ] && { note "dump_koh.txt exists"; exit 0; }
cd "$BD/engine"
python3 -c "
import json, collections
d = json.load(open('$DG/selected.json')); g = collections.defaultdict(list)
for x in d: g[(x['pairing'], x['config'])].append(x)
for (p, c), xs in sorted(g.items()): print(p, c, max(x['i'] for x in xs) + 1, ','.join(str(x['seed']) for x in xs))
" | while read -r p cfg n seeds; do
  if [ "$cfg" = first ]; then ba=koh3; bb=kp3; else ba=kp3; bb=koh3; fi
  DUMP_SEEDS="$seeds" RAYON_NUM_THREADS=14 nice -n 10 ./target/release/examples/legality_scan --decks ../decks/research \
    --pairings "$p" --games "$n" --bot-a $ba --bot-b $bb 2>&1 | grep '^DUMP2 ' >> "$O/dump_koh.txt.part" || true
done
mv "$O/dump_koh.txt.part" "$O/dump_koh.txt"
echo "$(date -u +%F\ %T) KOH DUMPS DONE ($(wc -l < "$O/dump_koh.txt") lines)" >> "$O/STATUS_dumps.txt"
