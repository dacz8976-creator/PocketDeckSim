#!/usr/bin/env bash
# The split-run proof (the coordinator's job of Oct 9, item 2): one small registration played straight, and again as two workers that each
# play a slice (--only-deck) into their own folder; split_collect.py merges the two, and the merge must equal the straight run game for game
# (content, not timing). Also: the merge with one worker left out is flagged INCOMPLETE, naming the missing games.
# The registration (registration/manifest.json) is written here, not by strength_prereg.py (which is the slow report's to call): it has
# strength_prereg.py's fields, with the 12 self-check games it records (t-altaria v t-suicune, km3) run by this script the same way.
# 12 games: 3 decks (t-altaria, t-suicune, t-hydreigon) v t-blaziken, 1 deal, both seats, the arms ref and X, km3 v km3; seeds 20,910,000,000
# + (deck index x 1,000) x 10,000 (Claude Code's diagnostic block). Worker 1 plays t-altaria and t-suicune (8 games), worker 2 t-hydreigon (4).
# The program is the harness built on the official engine (main-8626a35, engine tree 38af8b0) by rl/strength/build.sh, in a scratch folder.
# Usage: run_proof.sh <scratch dir>   (from anywhere in the repository; writes its results beside this script)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
mkdir -p "$W" && W=$(cd "$W" && pwd)
SC=$REPO/rl/strength/split_collect.py
PROG=$W/strength
STRENGTH_BUILD_DIR=$W/build STRENGTH_TARGET_DIR=$W/target nice -n 19 "$REPO/rl/strength/build.sh" 8626a358 "$PROG" > "$W/build.txt" 2>&1 \
    || { echo "build failed:"; tail -5 "$W/build.txt"; exit 1; }
grep -E "^(engine|program sha256|harness source)" "$W/build.txt"
PSHA=$(sha256sum < "$PROG" | cut -c1-64)
TREE=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['engine_tree_archived'])" "$PROG.build.json")

REG=$HERE/registration
rm -rf "$REG" "$W/straight" "$W/w1" "$W/w2" "$W/merged" "$W/merged_w1_only"
mkdir -p "$REG"
SELF=$("$PROG" selfcheck --root "$REPO" --pilot km3 --deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12)
echo "self-check: $SELF"
python3 - "$REPO" "$REG/manifest.json" "$PSHA" "$TREE" "$PROG" "$SELF" <<'PY'
import datetime, hashlib, json, subprocess, sys
repo, out, psha, tree, prog, selfcheck = sys.argv[1:]
sha = lambda p: hashlib.sha256(open(f"{repo}/{p}", "rb").read()).hexdigest()
deck = lambda n: {"name": n, "path": f"decks/screen/opponents/{n}.txt", "sha256": sha(f"decks/screen/opponents/{n}.txt")}
m = {"name": "split_proof", "question": "Split-run proof: the merge of two --only-deck workers equals the straight run, game for game.",
     "repo_commit": subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
     "selfcheck": {"km3": selfcheck}, "selfcheck_source": {"km3": "run by run_proof.sh as strength_prereg.py runs it (t-altaria v t-suicune, 12 games)"},
     "created_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "stage": "dev", "repo_root": repo,
     "pilot": "km3", "reference": "km3", "decks": [deck(n) for n in ("t-altaria", "t-suicune", "t-hydreigon")], "opponents": [deck("t-blaziken")],
     "deals": 1, "seats": [0, 1], "seed_base": 20_910_000_000, "pair_stride": 10_000, "threads": 2, "log_level": "deck", "ext_timeout_s": None,
     "heldout_decks": [], "heldout_locked": True, "program": prog, "program_sha256": psha, "engine": f"main-8626a35, engine tree {tree}",
     "planned_pairs": 3, "planned_games": 12}
json.dump(m, open(out, "w"), indent=1)
open(out, "a").write("\n")
PY
(cd "$REG" && sha256sum manifest.json > manifest.sha256)
M=$REG/manifest.json

run() {  # <out dir> [--only-deck NAME]...
    local out=$1; shift
    mkdir -p "$out"
    nice -n 19 "$PROG" run --manifest "$M" --out "$out" --threads 2 "$@" 2> "$out/stderr.txt"
}
echo "== straight"
run "$W/straight"
python3 "$SC" stamp --manifest "$M" --program "$PROG" --worker straight --out "$W/straight"
echo "== worker 1 (t-altaria, t-suicune) and worker 2 (t-hydreigon), each into its own folder"
python3 "$SC" stamp --manifest "$M" --program "$PROG" --worker w1 --out "$W/w1" --only-deck t-altaria --only-deck t-suicune
run "$W/w1" --only-deck t-altaria --only-deck t-suicune
python3 "$SC" stamp --manifest "$M" --program "$PROG" --worker w2 --out "$W/w2" --only-deck t-hydreigon
run "$W/w2" --only-deck t-hydreigon
for d in straight w1 w2; do echo "$d: $(wc -l < "$W/$d/games.jsonl") games, errors: $(cat "$W/$d/errors.jsonl" 2>/dev/null | wc -l)"; done
echo "== merge"
python3 "$SC" merge --manifest "$M" --worker "$W/w1" --worker "$W/w2" --out "$W/merged" || true
echo "== the merge against the straight run"
python3 "$SC" compare "$W/merged/games.jsonl" "$W/straight/games.jsonl" || true
python3 - "$W" <<'PY'
import json, sys
W = sys.argv[1]
load = lambda p: [json.loads(l) for l in open(p)]
merged, straight = load(f"{W}/merged/games.jsonl"), load(f"{W}/straight/games.jsonl")
print("keys in the same order:", [r["key"] for r in merged] == [r["key"] for r in straight])
print("whole lines byte for byte (timing included, so expected to differ):",
      sum(a == b for a, b in zip(open(f"{W}/merged/games.jsonl"), open(f"{W}/straight/games.jsonl"))), "of", len(merged))
PY
echo "== the straight run, merged alone (one worker)"
python3 "$SC" merge --manifest "$M" --worker "$W/straight" --out "$W/merged_straight" || true
echo "== negative: worker 1 alone"
python3 "$SC" merge --manifest "$M" --worker "$W/w1" --out "$W/merged_w1_only" || true
grep -E "^\*\*|missing" "$W/merged_w1_only/MERGE_RECORD.md" | head -6
mkdir -p "$HERE/proof"
cp "$W/merged/games.jsonl" "$HERE/proof/merged_games.jsonl"
cp "$W/merged/MERGE_RECORD.md" "$HERE/proof/MERGE_RECORD.md"
cp "$W/straight/games.jsonl" "$HERE/proof/straight_games.jsonl"
cp "$W/merged_w1_only/MERGE_RECORD.md" "$HERE/proof/MERGE_RECORD_w1_only.md"
for d in w1 w2 straight; do cp "$W/$d/worker.json" "$HERE/proof/worker_$d.json"; done
