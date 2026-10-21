#!/bin/bash
# Builds /home/dacz8976/pgx/pg_pos_D_cond: the OLDER engine (the Oct 2 harness tree /home/dacz8976/pgd/build/engine, main-8626a35, with the same print-only patch as the other runners)
# plus main's new pg_pos.rs (28df6315: reads `conditions` and `knockouts`). The old pg_pos of that tree ignores both, so a comparison with the official engine on 010837 t13/t15 was not like for like;
# with this build the two engines see the same position. About 4 minutes (a fresh cargo target dir), nice 19. Run from the repository root of a checkout of main.
set -euo pipefail
E=/home/dacz8976/pgd/build/engine
D=/home/dacz8976/pgx/D
mkdir -p "$D"
rsync -a --exclude target --exclude .git "$E/" "$D/engine/"
cp rl/results/pause_games_decisions_2026-10-02/harness/pg_pos.rs "$D/engine/examples/pg_pos.rs"
cd "$D/engine"
CARGO_TARGET_DIR=/home/dacz8976/pgx/target_D nice -n 19 cargo build --release --example pg_pos
cp /home/dacz8976/pgx/target_D/release/examples/pg_pos /home/dacz8976/pgx/pg_pos_D_cond
sha256sum /home/dacz8976/pgx/pg_pos_D_cond
