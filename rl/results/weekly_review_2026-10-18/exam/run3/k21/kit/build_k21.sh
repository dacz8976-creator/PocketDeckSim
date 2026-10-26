#!/bin/bash
# K21's kx3 position player: frozen-7's own build_baseline.sh recipe (tag judge-prompt-frozen-7), with ONE change: the engine archive is cd20a97a's
# (the frozen tree 70652fff plus kx3's insertions only) instead of the tag's. Serial, low priority, never beside another cargo.
#   bash build_k21.sh   -> ~/k21_pgpos/bin/pg_pos_k21 and ~/k21_pgpos/build.json (sha256 and inputs)
set -euo pipefail
if pgrep -x cargo > /dev/null; then echo "another cargo is running; not building"; exit 3; fi
source ~/.cargo/env 2>/dev/null || true
TAG_DIR=/home/dacz8976/judge7_w                    # a checkout of judge-prompt-frozen-7
SRC_REPO=/home/dacz8976/exam_034_w                # any clone holding cd20a97a
SRC_COMMIT=cd20a97a
W=$HOME/k21_pgpos
[ "$(git -C $TAG_DIR rev-parse HEAD)" = 712593a1b77b203ec23fb15589c158c6bddb2bf2 ] || { echo "$TAG_DIR is not the frozen-7 tag"; exit 1; }
[ "$(git -C $SRC_REPO rev-parse $SRC_COMMIT:engine)" = 4ebb30a941737d16b80adddbd1466761e0670e63 ] || { echo "cd20a97a's engine is not 4ebb30a9"; exit 1; }
H=$TAG_DIR/rl/results/pause_games_decisions_2026-10-02/harness
for pair in "pgd_patch.py:904b9e86" "dg_patch.py:c98ccc63" "pg_pos.rs:224888a8"; do
  f=${pair%%:*}; want=${pair##*:}
  [ "$(sha256sum $H/$f | cut -c1-8)" = "$want" ] || { echo "$f is not frozen-7's ($want)"; exit 1; }
done
rm -rf "$W/src" && mkdir -p "$W/src" "$W/bin"
git -C $SRC_REPO archive $SRC_COMMIT engine | tar -x -C "$W/src"
cp $H/pgd_patch.py $H/dg_patch.py "$W/src/"
(cd "$W/src" && python3 -B pgd_patch.py "$W/src/engine") | tail -3
mkdir -p "$W/src/engine/examples"
cp $H/pg_pos.rs "$W/src/engine/examples/pg_pos.rs"
export CARGO_BUILD_JOBS=2 CARGO_TARGET_DIR="$W/t_pg"
(cd "$W/src/engine" && nice -n 19 cargo build --release --locked --offline --example pg_pos > "$W/build.log" 2>&1) || { echo "BUILD FAILED"; grep -E '^error' -A12 "$W/build.log" | head -50; exit 1; }
cp "$W/t_pg/release/examples/pg_pos" "$W/bin/pg_pos_k21"
python3 - "$W" <<'EOF'
import hashlib, json, subprocess, sys
W = sys.argv[1]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
H = '/home/dacz8976/judge7_w/rl/results/pause_games_decisions_2026-10-02/harness'
d = {'binary': f'{W}/bin/pg_pos_k21', 'binary_sha256': sha(f'{W}/bin/pg_pos_k21'), 'engine_commit': 'cd20a97a5', 'engine_tree': '4ebb30a941737d16b80adddbd1466761e0670e63',
     'recipe': "frozen-7's rl/ai_judge/build_baseline.sh with the archive switched to cd20a97a's engine (K21)",
     'pgd_patch_sha256': sha(f'{H}/pgd_patch.py'), 'dg_patch_sha256': sha(f'{H}/dg_patch.py'), 'pg_pos_rs_sha256': sha(f'{H}/pg_pos.rs'),
     'rustc': subprocess.run(['rustc', '--version'], capture_output=True, text=True).stdout.strip()}
json.dump(d, open(f'{W}/build.json', 'w'), indent=1)
print('BUILD OK', d['binary_sha256'])
EOF
