#!/usr/bin/env bash
# The literal check's follow-up: trace the promotion fix's changed games that showed no end-of-turn or Checkup Knock
# Out, on 5b75bf9 (before the fix) and 5bab907 (with it), and find where each first diverges (compare_dumps.py).
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/engine_switch_2026-09-26"
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
cd "$O"; python3 - > unexplained.json <<'EOF'
import json, subprocess
BR, FIX = "origin/claude/pensive-ptolemy-spwc0b", "rl/results/rules09_fixes_2026-09-26"
def cloud(c, b):
    t = subprocess.run(["git", "show", f"{BR}:{FIX}/{c}_{b}_500.jsonl"], capture_output=True, text=True, check=True).stdout
    return {(g["pairing"], g["i"]): g for g in map(json.loads, t.splitlines())}
out = {}
for bot in ("k3", "kp3"):
    a, b = cloud("5b75bf9", bot), cloud("5bab907", bot)
    w = {(g["pairing"], g["i"]): g for g in map(json.loads, open(f"watch_5b75bf9_{bot}_500.jsonl"))}
    out[bot] = [[p, i, b[(p, i)]["seed"]] for (p, i) in sorted(b) if a[(p, i)]["moves"] != b[(p, i)]["moves"] and w[(p, i)]["eot_ko"] == 0]
print(json.dumps(out))
EOF
note "unexplained: $(python3 -c "import json; d=json.load(open('unexplained.json')); print({k: len(v) for k, v in d.items()})")"
cd "$R"
for C in 5b75bf9 5bab907; do
  B=/home/dacz8976/engine-dump-$C
  if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
    rm -rf "$B"; mkdir -p "$B"; git archive "$C" engine decks | tar -x -C "$B"
    python3 "$O/instrument_scan.py" "$B/engine/examples/legality_scan.rs" >> "$O/STATUS.txt"
    python3 "$O/instrument_dump.py" "$B/engine/examples/legality_scan.rs" >> "$O/STATUS.txt"
    ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 6 ) > "$O/build_dump_$C.log" 2>&1
    note "built dump scan at $C"
  fi
done
for bot in k3 kp3; do
  SEEDS=$(python3 -c "import json; print(','.join(str(s) for _, _, s in json.load(open('$O/unexplained.json'))['$bot']))")
  for p in $(python3 -c "import json; print(' '.join(sorted({str(p) for p, _, _ in json.load(open('$O/unexplained.json'))['$bot']})))"); do
    N=$(python3 -c "import json; print(1 + max(i for q, i, _ in json.load(open('$O/unexplained.json'))['$bot'] if q == $p))")
    for C in 5b75bf9 5bab907; do
      ( cd /home/dacz8976/engine-dump-$C/engine && DUMP_SEEDS="$SEEDS" RAYON_NUM_THREADS=8 nice -n 10 \
        ./target/release/examples/legality_scan --decks ../decks/research --pairings "$p" --games "$N" --bot $bot 2>&1 \
        | grep '^DUMP ' >> "$O/dump_${C}_${bot}.txt" ) || true
    done
  done
done
echo "$(date -u +%F\ %T) DUMPS DONE" >> "$O/STATUS.txt"
