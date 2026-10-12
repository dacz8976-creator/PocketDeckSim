#!/usr/bin/env bash
# The exact attack-skipping measure (the cloud, Oct 12): skip_replay.rs built on the program each set of games was played with,
# run over the recorded games, then skip_exact.py. Usage: run_skip_exact.sh <scratch dir>   (from anywhere in the repository)
# Oct 12 follow-ups: km3 is asked at each decision with an attack legal (--km3; at every decision in km3's own games, --km3-all, the
# identity check), and the board at each decision of the listed skip turns (--boards, from the first run's skip_turns.tsv).
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
cp "$HERE/skip_turns.tsv" "$OUT/skip_turns_first_run.tsv"
B=(--boards "$OUT/skip_turns_first_run.tsv")
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/decisions_candidate.jsonl" --check "$OUT/check_candidate.jsonl" --km3 "${B[@]}" --bot candidate --boards-out "$OUT/boards_candidate.jsonl"
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm ref --out "$OUT/decisions_km3.jsonl" --check "$OUT/check_km3.jsonl" --km3-all "${B[@]}" --bot km3 --boards-out "$OUT/boards_km3.jsonl"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm X --out "$OUT/decisions_frozen.jsonl" --check "$OUT/check_frozen.jsonl" --km3 "${B[@]}" --bot frozen --boards-out "$OUT/boards_frozen.jsonl"
echo "== also: the development run's km3 games on the frozen build (they equal this run's arm ref)"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm ref --out "$OUT/decisions_km3_dev.jsonl" --check "$OUT/check_km3_dev.jsonl"
python3 - "$OUT/decisions_km3.jsonl" "$OUT/decisions_km3_dev.jsonl" <<'PY'
import json, sys
strip = lambda p: [{k: v for k, v in json.loads(l).items() if not k.startswith("km3_")} for l in open(p)]
print("the km3 decisions are the same on both builds" if strip(sys.argv[1]) == strip(sys.argv[2]) else "the km3 decisions DIFFER between the builds")
PY
echo "== negative control: 20 candidate records of 20+ decisions, each with its first logged attack changed to EndTurn"
echo "   (a change that leaves every recorded field the same can't be caught; one that changes the game must be)"
python3 - "$C/games.jsonl" "$OUT/negative20.jsonl" <<'PY'
import json, sys
out, n = open(sys.argv[2], "w"), 0
for line in open(sys.argv[1]):
    g = json.loads(line)
    att = [i for i, e in enumerate(g["log"]) if e["a"].startswith("Attack:")] if g["arm"] == "X" and len(g["log"]) >= 20 else []
    if len(att) >= 2:
        g["log"][att[0]]["a"] = "EndTurn"
        out.write(json.dumps(g) + "\n")
        n += 1
        if n == 20:
            break
PY
"$W/target_combined/release/examples/skip_replay" --games "$OUT/negative20.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/neg20_dec.jsonl" --check "$OUT/neg20_check.jsonl"
echo "== the comparison"
python3 "$HERE/skip_exact.py" "$OUT" > /dev/null
cmp -s <(cut -f1-6 "$OUT/skip_turns_first_run.tsv") <(cut -f1-6 "$OUT/skip_turns.tsv") && echo "the skip turns are the first run's, row for row" || echo "the skip turns DIFFER from the first run's"
cat "$OUT"/boards_candidate.jsonl "$OUT"/boards_frozen.jsonl "$OUT"/boards_km3.jsonl > "$OUT/skip_boards.jsonl"
echo "skip_boards.jsonl: $(wc -l < "$OUT/skip_boards.jsonl") records ($(cat "$OUT/boards_candidate.jsonl" | wc -l) candidate, $(cat "$OUT/boards_frozen.jsonl" | wc -l) frozen, $(cat "$OUT/boards_km3.jsonl" | wc -l) km3), replayed exactly $(grep -c '"replayed_exactly":true' "$OUT/skip_boards.jsonl")"
gzip -9 -c "$OUT/skip_boards.jsonl" > "$HERE/skip_boards.jsonl.gz"
cp "$OUT"/exact_summary.txt "$OUT"/skip_turns.tsv "$OUT"/check_candidate.jsonl "$OUT"/check_frozen.jsonl "$OUT"/check_km3.jsonl "$HERE/"
gzip -9 -c "$OUT/skip_decisions.tsv" > "$HERE/skip_decisions.tsv.gz"
for b in candidate frozen km3; do gzip -9 -c "$OUT/decisions_$b.jsonl" > "$HERE/decisions_$b.jsonl.gz"; done
for b in candidate frozen km3; do echo "$b: $(python3 -c "import json,sys; c=[json.loads(l) for l in open(sys.argv[1])]; print(len(c), 'games,', sum(x['replayed_exactly'] for x in c), 'replayed exactly')" "$OUT/check_$b.jsonl")"; done
