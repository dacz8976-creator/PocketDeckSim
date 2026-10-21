#!/bin/bash
# ky3 item 7, stage A (the laptop, Oct 16; KINGAMBIT_ITEM7.md section 3 and EXPECTED_KG.md on sonnet/ky3-blade 0f5f234d).
# Builds one at a time (CARGO_BUILD_JOBS 6); step 0 = item 7's test 8 (the 80-deal replay) and the self-checks; part (a) = 92 pause-game
# positions x 12 seeds for km3, kmb3, kmbc3, kmbd3; part (b) = self-play, 2,000 games per arm (6 arms); then the slow ky3 self-checks.
set -uo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
W=/home/dacz8976/stageA
mkdir -p $W/bin $W/logs $W/out
log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAILED: $*"; touch $W/FAILED; exit 1; }
unset KX_EXTRA_LISTS
env | grep -q '^DECKGYM_' && fail "a DECKGYM_ variable is set"
cd "$REPO" || fail "no repo"
git fetch --no-auto-maintenance -q origin
BL=$(git rev-parse origin/sonnet/ky3-blade); PI=$(git rev-parse origin/sonnet/ky3-pilot); MAIN=$(git rev-parse origin/main)
log "start: blade ${BL:0:8}, pilot ${PI:0:8}, main ${MAIN:0:8}; free memory $(free -g | awk '/Mem/{print $7}') GB"
[ "${BL:0:8}" = 0f5f234d ] || fail "ky3-blade moved from 0f5f234d"
[ "${PI:0:8}" = 81ea31b5 ] || fail "ky3-pilot moved from 81ea31b5"
export CARGO_BUILD_JOBS=6

# ---- builds, one at a time ----
sb() {  # REF NAME
    env STRENGTH_BUILD_DIR=$W/sb_$2 STRENGTH_TARGET_DIR=$W/sb_$2/target STRENGTH_JOBS=6 bash "$REPO/rl/strength/build.sh" "$1" $W/bin/strength_$2 \
        > $W/logs/build_strength_$2.log 2>&1 || fail "strength $2 build (see logs/build_strength_$2.log)"
    log "strength_$2 built: $(tail -n 4 $W/logs/build_strength_$2.log | tr '\n' ' ' | cut -c1-300)"
}
[ -x $W/bin/strength_blade ] || sb origin/sonnet/ky3-blade blade
[ -x $W/bin/strength_pilot ] || sb origin/sonnet/ky3-pilot pilot
if [ ! -x $W/bin/kg_log ]; then
    rm -rf $W/src_kg && mkdir -p $W/src_kg && git archive origin/sonnet/ky3-blade engine | tar -x -C $W/src_kg
    (cd $W/src_kg/engine && CARGO_TARGET_DIR=$W/t_kg nice -n 10 cargo build --release --locked --example kg_log > $W/logs/build_kg.log 2>&1) || fail "kg_log build"
    cp $W/t_kg/release/examples/kg_log $W/bin/kg_log
    log "kg_log built: $(sha256sum < $W/bin/kg_log | cut -c1-16)"
fi
if [ ! -x $W/bin/pg_pos_blade ]; then
    H=rl/results/pause_games_decisions_2026-10-02/harness
    rm -rf $W/src_pg && mkdir -p $W/src_pg && git archive origin/sonnet/ky3-blade engine | tar -x -C $W/src_pg
    git show origin/main:$H/pgd_patch.py > $W/src_pg/pgd_patch.py
    git show origin/main:$H/dg_patch.py > $W/src_pg/dg_patch.py 2>/dev/null || git show origin/main:rl/results/pause_games_decisions_2026-10-02/c8c/dg_patch.py > $W/src_pg/dg_patch.py
    (cd $W/src_pg && python3 -B pgd_patch.py $W/src_pg/engine) > $W/logs/patch_pg.log 2>&1 || fail "pgd_patch on the blade engine (see logs/patch_pg.log)"
    mkdir -p $W/src_pg/engine/examples && git show origin/main:$H/pg_pos.rs > $W/src_pg/engine/examples/pg_pos.rs
    (cd $W/src_pg/engine && CARGO_TARGET_DIR=$W/t_pg nice -n 10 cargo build --release --locked --example pg_pos > $W/logs/build_pg.log 2>&1) || fail "pg_pos build"
    cp $W/t_pg/release/examples/pg_pos $W/bin/pg_pos_blade
    log "pg_pos_blade built: $(sha256sum < $W/bin/pg_pos_blade | cut -c1-16)"
fi
log "builds done"

# ---- step 0a: the fast self-checks (km3's pin: 81b572198c04d5d1) ----
SC="--deck-a decks/screen/opponents/t-altaria.txt --deck-b decks/screen/opponents/t-suicune.txt --games 12"
{ for p in km3 kmb3 kmbc3 kmbd3; do echo "blade: $(nice -n 10 $W/bin/strength_blade selfcheck --pilot $p $SC)"; done
  echo "pilot: $(nice -n 10 $W/bin/strength_pilot selfcheck --pilot km3 $SC)"; } > $W/out/selfcheck_fast.txt 2>&1
log "fast self-checks:"; cat $W/out/selfcheck_fast.txt

# ---- self-play helper (part b and test 8): one kg_log call per opponent list and seat, 8 at a time ----
run_arm() {  # NAME DECK X DECK_PILOT OPP_PILOT GAMES (seed = 25,000,000,000 + X x 10,000,000 + o x 1,000,000 + S x 500,000 + i; EXPECTED_KG.md section 1)
    local name=$1 deck=$2 x=$3 dp=$4 op=$5 n=$6
    mkdir -p $W/out/parts_$name
    for o in 0 1 2 3 4 5 6 7; do for s in 0 1; do
        echo "$o $s $((25000000000 + x * 10000000 + o * 1000000 + s * 500000)) $deck $dp $op $n $W/out/parts_$name"
    done; done | xargs -P 8 -L 1 bash $W/kg_one.sh || fail "kg_log arm $name"
    cat $W/out/parts_$name/o*_s*.jsonl > $W/out/$name.jsonl
    log "arm $name: $(wc -l < $W/out/$name.jsonl) games"
}

# ---- step 0b: test 8, the replay (deck 01 file, X = 1, the 80 deals: 8 lists x 2 seats x 5) ----
D01=decks/dustin/01-muk-glimmora-kingambit-regigigas.txt
run_arm t8_km3 $D01 1 km3 km3 5
run_arm t8_kmb3 $D01 1 kmb3 km3 5
python3 $W/test8_compare.py $W/out/t8_km3.jsonl $W/out/t8_kmb3.jsonl > $W/out/test8.txt 2>&1
log "test 8:"; tail -n 12 $W/out/test8.txt

# ---- part (a): the 92 pause-game positions x 12 seeds, km3 / kmb3 / kmbc3 / kmbd3 on the blade engine ----
V=rl/results/pause_games_new_2026-10-13/v2
DECKARGS=""; for f in $V/decks/KW*.txt; do DECKARGS="$DECKARGS --deck $(basename "$f" .txt)=$f"; done
for bot in km3 kmb3 kmbc3 kmbd3; do
    mkdir -p $W/out/pos_$bot
    grep -v '^$' $V/run_ids.txt | xargs -P 6 -I{} bash -c "nice -n 10 $W/bin/pg_pos_blade --positions $V/positions_all.json $DECKARGS --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot $bot --only {} > $W/out/pos_$bot/out_{}.jsonl 2> $W/out/pos_$bot/err_{}.txt" \
        || fail "pg_pos $bot"
    log "part (a) $bot: $(ls $W/out/pos_$bot/out_*.jsonl | wc -l) positions"
done
python3 $W/parta_compare.py $V/runs_km3 $W/out $V/run_ids.txt > $W/out/parta.txt 2>&1
log "part (a):"; head -n 30 $W/out/parta.txt

# ---- part (b): self-play, his played list (X = 0), 125 per list and seat = 2,000 games per arm ----
DA=decks/dustin/01-kingambit-as-played.txt
run_arm b_km3 $DA 0 km3 km3 125
run_arm b_kmb3 $DA 0 kmb3 km3 125
run_arm b_kmbc3 $DA 0 kmbc3 km3 125
run_arm b_kmbd3 $DA 0 kmbd3 km3 125
run_arm b_km3_vkmb3 $DA 0 km3 kmb3 125
run_arm b_kmbc3_vkmb3 $DA 0 kmbc3 kmb3 125
git show origin/sonnet/ky3-blade:rl/results/next_pilot_2026-10/analyze_kg.py > $W/analyze_kg.py
{ python3 $W/analyze_kg.py --selftest
  for arm in kmb3 kmbc3 kmbd3; do echo "===== km3 v $arm"; python3 $W/analyze_kg.py $W/out/b_km3.jsonl $W/out/b_$arm.jsonl; done
  echo "===== Blade-aware opponent (kmb3): km3 v kmbc3"; python3 $W/analyze_kg.py $W/out/b_km3_vkmb3.jsonl $W/out/b_kmbc3_vkmb3.jsonl; } > $W/out/partb.txt 2>&1
log "part (b) written: $(wc -l < $W/out/partb.txt) lines"
touch $W/FAST_DONE
tmux wait-for -S stageA_fast 2>/dev/null || true

# ---- the slow self-checks (F's 31d638dbc818b0fa for ky3 with no switch, and ky3_blade / ky3_blade_count on the blade build) ----
K=ky3_r16_c12_z2_real_t0_poolmeta
for p in $K ${K}_blade ${K}_blade_count; do
    echo "blade: $(nice -n 10 $W/bin/strength_blade selfcheck --pilot $p $SC)" >> $W/out/selfcheck_slow.txt 2>&1
    log "slow self-check: $(tail -n 1 $W/out/selfcheck_slow.txt)"
done
echo "pilot: $(nice -n 10 $W/bin/strength_pilot selfcheck --pilot $K $SC)" >> $W/out/selfcheck_slow.txt 2>&1
log "slow self-check: $(tail -n 1 $W/out/selfcheck_slow.txt)"
log "driver finished"
touch $W/DONE
