#!/usr/bin/env bash
# The exact attack-skipping measure (the cloud, Oct 12): skip_replay.rs built on the program each set of games was played with,
# run over the recorded games, then skip_exact.py. Usage: run_skip_exact.sh <scratch dir>   (from anywhere in the repository)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
mkdir -p "$W" && W=$(cd "$W" && pwd)
C=$REPO/rl/results/strength_2026-10-08_kx3_combined
DEV=$REPO/rl/results/strength_2026-10-03_kx3_dev
echo "== the deck files against both manifests (by sha256)"
python3 - "$REPO" "$C/manifest.json" "$DEV/manifest.json" <<'PY'
import hashlib, json, sys
repo = sys.argv[1]
for mp in sys.argv[2:]:
    m = json.load(open(mp))
    bad = [d["name"] for d in m["decks"] + m["opponents"] if hashlib.sha256(open(f"{repo}/{d['path']}", "rb").read()).hexdigest() != d["sha256"]]
    print(mp.split("/")[-2], "decks:", "all equal" if not bad else f"DIFFERENT {bad}")
    if bad:
        sys.exit(1)
PY
build() {  # <commit> <name>
    rm -rf "$W/$2" && mkdir -p "$W/$2"
    git -C "$REPO" archive "$1" engine | tar -x -C "$W/$2"
    cp "$HERE/skip_replay.rs" "$W/$2/engine/examples/"
    (cd "$W/$2/engine" && CARGO_TARGET_DIR="$W/target_$2" cargo build --release --locked --example skip_replay 2>&1 | grep -E "^error|Finished") \
        || { echo "build failed"; exit 1; }
    echo "$2: commit $(git -C "$REPO" rev-parse --short=12 "$1"), engine tree $(git -C "$REPO" rev-parse --short=12 "$1:engine"), skip_replay sha256 $(sha256sum < "$W/target_$2/release/examples/skip_replay" | cut -c1-16)"
}
echo "== builds"
build 172cbe9c combined
build d513e37b frozen
OUT=$W/out
mkdir -p "$OUT"
cd "$REPO"
echo "== replays"
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/decisions_candidate.jsonl" --check "$OUT/check_candidate.jsonl"
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm ref --out "$OUT/decisions_km3.jsonl" --check "$OUT/check_km3.jsonl"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm X --out "$OUT/decisions_frozen.jsonl" --check "$OUT/check_frozen.jsonl"
echo "== also: the development run's km3 games on the frozen build (they equal this run's arm ref)"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm ref --out "$OUT/decisions_km3_dev.jsonl" --check "$OUT/check_km3_dev.jsonl"
cmp -s <(cut -d'"' -f1- "$OUT/decisions_km3.jsonl") "$OUT/decisions_km3_dev.jsonl" && echo "the km3 decisions are byte for byte the same on both builds" || echo "the km3 decisions DIFFER between the builds"
echo "== negative control: one candidate record with one logged move changed must not replay"
python3 - "$C/games.jsonl" "$OUT/negative.jsonl" <<'PY'
import json, sys
for line in open(sys.argv[1]):
    g = json.loads(line)
    if g["arm"] == "X" and any(e["a"].startswith("Attack:") for e in g["log"]):
        i = next(i for i, e in enumerate(g["log"]) if e["a"].startswith("Attack:"))
        g["log"][i]["a"] = "EndTurn"
        open(sys.argv[2], "w").write(json.dumps(g) + "\n")
        print("changed", g["key"], "decision", i, "to EndTurn")
        break
PY
"$W/target_combined/release/examples/skip_replay" --games "$OUT/negative.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/negative_dec.jsonl" --check "$OUT/negative_check.jsonl"
python3 -c "import json,sys; c=json.loads(open(sys.argv[1]).readline()); print('negative control replayed_exactly:', c['replayed_exactly'], '; missing:', c['missing'][:2])" "$OUT/negative_check.jsonl"
echo "== the comparison"
python3 "$HERE/skip_exact.py" "$OUT" > /dev/null
cp "$OUT"/exact_summary.txt "$OUT"/skip_turns.tsv "$OUT"/skip_decisions.tsv "$OUT"/check_candidate.jsonl "$OUT"/check_frozen.jsonl "$OUT"/check_km3.jsonl "$HERE/"
for b in candidate frozen km3; do gzip -9 -c "$OUT/decisions_$b.jsonl" > "$HERE/decisions_$b.jsonl.gz"; done
for b in candidate frozen km3; do echo "$b: $(python3 -c "import json,sys; c=[json.loads(l) for l in open(sys.argv[1])]; print(len(c), 'games,', sum(x['replayed_exactly'] for x in c), 'replayed exactly')" "$OUT/check_$b.jsonl")"; done
