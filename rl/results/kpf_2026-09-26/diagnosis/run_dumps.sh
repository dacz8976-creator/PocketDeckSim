#!/usr/bin/env bash
# kpf veto diagnosis, step 1: pick each diagnosed deck's own-side games that changed under kpf3 (kpf's mixed rows v kp3's
# table, same deals: worse = the deck's score fell, better = rose; up to 20 of each per cell, lowest deal numbers first),
# then trace them move by move on both sides of the comparison: kp3 v kp3 (the baseline) and the mixed row (kpf3 on
# the deck only). Build: the official source 83e17ae + instrument_dump2.py (watch-only), outside the repo.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/kpf_2026-09-26/diagnosis"
K="$R/rl/results/kpf_2026-09-26/reading"; B=/home/dacz8976/engine-dump2-83e17ae
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
cd "$O"
python3 - "$K" > selected.json <<'EOF'
import json, sys
K = sys.argv[1]
load = lambda f: {(g["pairing"], g["i"]): g for g in map(json.loads, open(f"{K}/{f}"))}
base, first, second = load("table_kp3.jsonl"), load("mixed_table_kpf3_first.jsonl"), load("mixed_table_kpf3_second.jsonl")
out = []
for deck in ("altaria", "lucario", "vespiquen"):
    for p in sorted({k[0] for k in base}):
        g0 = base[(p, 0)]
        if deck not in (g0["a"], g0["b"]):
            continue
        rows, cfg = (first, "first") if g0["a"] == deck else (second, "second")
        own = (lambda g: g["first_deck_score"]) if cfg == "first" else (lambda g: 1 - g["first_deck_score"])
        ch = [(i, own(rows[(p, i)]) - own(base[(p, i)])) for i in range(500)]
        for sign, name in ((-1, "worse"), (1, "better")):
            pick = [(i, d) for i, d in ch if d * sign > 0][:20]
            out += [{"deck": deck, "pairing": p, "a": g0["a"], "b": g0["b"], "i": i, "seed": base[(p, i)]["seed"],
                     "config": cfg, "change": d, "kind": name} for i, d in pick]
print(json.dumps(out))
EOF
note "selected $(python3 -c "import json; d=json.load(open('selected.json')); print(len(d), 'games')")"
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  rm -rf "$B"; mkdir -p "$B"; git -C "$R" archive 83e17ae engine decks | tar -x -C "$B"
  python3 "$O/instrument_dump2.py" "$B/engine/examples/legality_scan.rs" >> "$O/STATUS.txt"
  ( cd "$B/engine" && nice -n 10 cargo build --release --example legality_scan -j 8 ) > "$O/build.log" 2>&1 || { note "FAILED build"; exit 1; }
  note "built dump2 scan"
fi
cd "$B/engine"
python3 -c "
import json, collections
d = json.load(open('$O/selected.json')); g = collections.defaultdict(list)
for x in d: g[(x['pairing'], x['config'])].append(x)
for (p, c), xs in sorted(g.items()): print(p, c, max(x['i'] for x in xs) + 1, ','.join(str(x['seed']) for x in xs))
" | while read -r p cfg n seeds; do
  DUMP_SEEDS="$seeds" RAYON_NUM_THREADS=8 nice -n 10 ./target/release/examples/legality_scan --decks ../decks/research \
    --pairings "$p" --games "$n" --bot kp3 2>&1 | grep '^DUMP2 ' >> "$O/dump_base.txt" || true
  if [ "$cfg" = first ]; then ba=kpf3; bb=kp3; else ba=kp3; bb=kpf3; fi
  DUMP_SEEDS="$seeds" RAYON_NUM_THREADS=8 nice -n 10 ./target/release/examples/legality_scan --decks ../decks/research \
    --pairings "$p" --games "$n" --bot-a $ba --bot-b $bb 2>&1 | grep '^DUMP2 ' >> "$O/dump_kpf.txt" || true
done
echo "$(date -u +%F\ %T) DUMPS DONE" >> "$O/STATUS.txt"
