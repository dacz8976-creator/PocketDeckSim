#!/usr/bin/env bash
# Re-applies dg_patch.py (print-only) to the scratch copies of the old engine (d363ba8), R (f8cfa9c) and VAR (R with the queued attack-damage
# choice at a coin target reverted to the plain ApplyDamage, the one change the frame-purity reading names), then builds incrementally
# (target dirs kept; VAR's starts as a copy of R's). Usage: dg_repatch.sh [jobs per build, default 6]
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D=/home/dacz8976/c8c/dg; J=${1:-6}
if [ ! -d "$D/var" ]; then
    mkdir -p "$D/var"
    git -C "$REPO" archive f8cfa9c engine | tar -x -C "$D/var"
    find "$D/var" -type f -exec touch {} +
    [ -d "$D/target_var" ] || cp -a "$D/target_new" "$D/target_var"
fi
for pair in old:d363ba8 new:f8cfa9c var:f8cfa9c; do
    name=${pair%%:*}; rev=${pair##*:}
    git -C "$REPO" show "$rev:engine/src/players/expectiminimax_player.rs" > "$D/$name/engine/src/players/expectiminimax_player.rs"
    python3 -B "$HERE/dg_patch.py" "$D/$name/engine"
    cp "$HERE/score_dump.rs" "$D/$name/engine/examples/score_dump.rs"
    touch "$D/$name/engine/src/players/expectiminimax_player.rs" "$D/$name/engine/examples/score_dump.rs"
done
# VAR: queued_attack_damage_choice always returns the plain ApplyDamage (the old engine's form)
python3 -B - "$D/var/engine/src/actions/apply_attack_action.rs" "$REPO" <<'EOF'
import subprocess, sys
from pathlib import Path
p = Path(sys.argv[1])
b = subprocess.run(["git", "-C", sys.argv[2], "show", "f8cfa9c:engine/src/actions/apply_attack_action.rs"], capture_output=True, check=True).stdout
old = b"    if coin_target {\r\n        log::debug!(\r\n            \"Queued attack damage at a coin-flip damage Ability"
if old not in b:
    old = old.replace(b"\r\n", b"\n")
assert b.count(old) == 1, "variant anchor"
eol = b"\r\n" if b"\r\n" in old else b"\n"
p.write_bytes(b.replace(old, old.replace(b"if coin_target {", b"if coin_target && std::env::var_os(\"PG_QUEUED_AS_APPLYDAMAGE\").is_none() {")))
print("variant patched", p)
EOF
touch "$D/var/engine/src/actions/apply_attack_action.rs"
for name in old new var; do
    ( cd "$D/$name/engine" && CARGO_BUILD_JOBS=$J CARGO_TARGET_DIR="$D/target_$name" nice -n 19 cargo build --release --locked --example score_dump 2>&1 | grep -E "^error" -A6 | head -20 || true
      cp "$D/target_$name/release/examples/score_dump" "$D/score_dump_$name"
      echo "score_dump_$name $(sha256sum < "$D/score_dump_$name" | cut -c1-16)" ) &
done
wait
