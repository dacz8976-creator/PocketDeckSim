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
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/decisions_candidate.jsonl" --check "$OUT/check_candidate.jsonl" --km3 2> "$OUT/stderr_candidate.txt"
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm ref --out "$OUT/decisions_km3.jsonl" --check "$OUT/check_km3.jsonl" --km3-all 2> "$OUT/stderr_km3.txt"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm X --out "$OUT/decisions_frozen.jsonl" --check "$OUT/check_frozen.jsonl" --km3 2> "$OUT/stderr_frozen.txt"
echo "== also: the development run's km3 games on the frozen build (they equal this run's arm ref)"
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm ref --out "$OUT/decisions_km3_dev.jsonl" --check "$OUT/check_km3_dev.jsonl"
python3 - "$OUT/decisions_km3.jsonl" "$OUT/decisions_km3_dev.jsonl" <<'PY'
import json, sys
strip = lambda p: [{k: v for k, v in json.loads(l).items() if not k.startswith("km3_")} for l in open(p)]
print("the km3 decisions are the same on both builds" if strip(sys.argv[1]) == strip(sys.argv[2]) else "the km3 decisions DIFFER between the builds")
PY
echo "== negative controls (the laptop's review, item c): each record below is changed one way and must fail the identity check"
python3 - "$C/games.jsonl" "$DEV/games.jsonl" "$OUT" <<'PY'
import json, random, sys
comb, dev, out = sys.argv[1:]
rnd = random.Random(20_990_000_000)
pick = {}
for src, path in (("comb", comb), ("dev", dev)):
    for line in open(path):
        g = json.loads(line)
        if src == "dev" and g["arm"] == "ref":
            continue                      # the development run's km3 games equal this run's arm ref
        pick.setdefault((src, g["arm"], g["deck"]), []).append(g)
chosen = {k: rnd.sample(v, 2) for k, v in sorted(pick.items())}
files = {}
def put(name, src, g):
    files.setdefault((name, src), []).append(json.dumps(g))
for (src, arm, deck), gs in chosen.items():
    for g in gs:
        s = dict(g, seed=g["seed"] + 1)                       # a wrong seed
        put("seed", src, s)
        o = dict(g, pilot_opp="km2")                          # a wrong opponent pilot
        put("opp", src, o)
        log = [dict(e) for e in g["log"]]                     # one logged move replaced by another label from the same game
        i = rnd.randrange(len(log))
        others = sorted({e["a"] for e in log if e["a"] != log[i]["a"]})
        log[i]["a"] = rnd.choice(others) if others else "EndTurn"
        put("label", src, dict(g, log=log))
for (name, src), lines in files.items():
    open(f"{out}/neg_{name}_{src}.jsonl", "w").write("\n".join(lines) + "\n")
print(len(chosen) * 2, "records, each changed three ways (seed, opponent pilot, one label):", len(chosen), "deck-and-arm cells, 2 records each")
PY
for name in seed opp label; do
  for arm in X ref; do
    "$W/target_combined/release/examples/skip_replay" --games "$OUT/neg_${name}_comb.jsonl" --manifest "$C/manifest.json" --arm $arm --out "$OUT/negd_${name}_comb_$arm.jsonl" --check "$OUT/negc_${name}_comb_$arm.jsonl" 2> /dev/null
  done
  "$W/target_frozen/release/examples/skip_replay" --games "$OUT/neg_${name}_dev.jsonl" --manifest "$DEV/manifest.json" --arm X --out "$OUT/negd_${name}_dev_X.jsonl" --check "$OUT/negc_${name}_dev_X.jsonl" 2> /dev/null
done
python3 - "$OUT" <<'PY' | tee "$OUT/negative_control.txt"
import glob, json, sys
out = sys.argv[1]
print("Negative controls (Oct 12): 2 records per deck and arm (candidate, km3, frozen kx3), each changed one way; every one must fail.")
for name, what in (("seed", "a wrong seed (+1)"), ("opp", "a wrong opponent pilot (km2)"), ("label", "one logged move replaced by another label of the same game")):
    cs = [json.loads(l) for f in sorted(glob.glob(f"{out}/negc_{name}_*.jsonl")) for l in open(f)]
    passed = [c["key"] for c in cs if c["replayed_exactly"]]
    print(f"{what}: {len(cs)} records, caught {len(cs) - len(passed)}, not caught {len(passed)} {passed}")
PY
echo "== the comparison"
python3 "$HERE/skip_exact.py" "$OUT" > /dev/null
cmp -s <(cut -f1-6 "$OUT/skip_turns_first_run.tsv") <(cut -f1-6 "$OUT/skip_turns.tsv") && echo "the skip turns are the first run's, row for row" \
  || echo "the skip turns differ from the first run's (cf2f27ca): $(diff <(cut -f1-6 "$OUT/skip_turns_first_run.tsv") <(cut -f1-6 "$OUT/skip_turns.tsv") | grep -c '^[<>]') rows changed"
echo "== the boards at the skip turns (a second pass over the same games, reading this run's skip_turns.tsv)"
B=(--boards "$OUT/skip_turns.tsv")
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm X --out "$OUT/pass2_candidate.jsonl" --check "$OUT/pass2c_candidate.jsonl" --km3 "${B[@]}" --bot candidate --boards-out "$OUT/boards_candidate.jsonl" 2> /dev/null
"$W/target_combined/release/examples/skip_replay" --games "$C/games.jsonl" --manifest "$C/manifest.json" --arm ref --out "$OUT/pass2_km3.jsonl" --check "$OUT/pass2c_km3.jsonl" --km3 "${B[@]}" --bot km3 --boards-out "$OUT/boards_km3.jsonl" 2> /dev/null
"$W/target_frozen/release/examples/skip_replay" --games "$DEV/games.jsonl" --manifest "$DEV/manifest.json" --arm X --out "$OUT/pass2_frozen.jsonl" --check "$OUT/pass2c_frozen.jsonl" --km3 "${B[@]}" --bot frozen --boards-out "$OUT/boards_frozen.jsonl" 2> /dev/null
cat "$OUT"/boards_candidate.jsonl "$OUT"/boards_frozen.jsonl "$OUT"/boards_km3.jsonl > "$OUT/skip_boards.jsonl"
echo "skip_boards.jsonl: $(wc -l < "$OUT/skip_boards.jsonl") records ($(cat "$OUT/boards_candidate.jsonl" | wc -l) candidate, $(cat "$OUT/boards_frozen.jsonl" | wc -l) frozen, $(cat "$OUT/boards_km3.jsonl" | wc -l) km3), replayed exactly $(grep -c '"replayed_exactly":true' "$OUT/skip_boards.jsonl")"
cp "$OUT/skip_boards.jsonl" "$HERE/skip_boards.jsonl"
cp "$OUT"/exact_summary.txt "$OUT"/negative_control.txt "$OUT"/skip_turns.tsv "$OUT"/check_candidate.jsonl "$OUT"/check_frozen.jsonl "$OUT"/check_km3.jsonl "$HERE/"
gzip -9 -c "$OUT/skip_decisions.tsv" > "$HERE/skip_decisions.tsv.gz"
for b in candidate frozen km3; do gzip -9 -c "$OUT/decisions_$b.jsonl" > "$HERE/decisions_$b.jsonl.gz"; done
for b in candidate frozen km3; do echo "$b: $(python3 -c "import json,sys; c=[json.loads(l) for l in open(sys.argv[1])]; print(len(c), 'games,', sum(x['replayed_exactly'] for x in c), 'replayed exactly')" "$OUT/check_$b.jsonl")"; done
