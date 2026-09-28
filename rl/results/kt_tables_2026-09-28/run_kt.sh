#!/usr/bin/env bash
# kt on kog, the laptop's runs (amendment 2 of ../kt_2026-09-26/README.md; Dustin's word in README.md here). Every
# game is played by the kt build's own programs (amendment 2 item 1), built here from the cloud's kt commit C.
# Part A (no kt game): the build, the diff check, identity (item 7).
# Part B (kt games; waits for the flag GATE_koh_b2e_read, written once koh's B2e rows are read and committed):
#   timing; the four tables on the 45 cells; the footprint (noted for the laptop to read and commit alone); mixed rows
#   on all 45 cells both directions for kt3 and kta3 (the conservative set: it covers either route); coverage for kt3
#   and kta3 (B2e 96 both sides + mixed on the held deck, Scizor both sides + mixed, second lists both sides + mixed by side); clause (d)'s rows
#   (kta3 and kt3 on the census Rayquaza list v kog3 on the panel, and kog3 on both; 22,700,000,000 block); the Rayquaza
#   traces (kta3 and kog3 on Rayquaza, kog3 on Lucario, item 9). The Dustin-deck A/B and the readout counters are a
#   separate script. Output names start with the kt build's short commit (item 1).
# Usage (WSL): nohup setsid bash run_kt.sh <kt commit> <branch> > run.log 2>&1 &
set -euo pipefail
C=$(git -C "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim" rev-parse "$1"); BR=$2; S=${C:0:7}
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/kt_tables_2026-09-28"
K="$R/rl/results/kpf_2026-09-26/reading"; KOG="$R/rl/results/kog_composition_2026-09-27"; KL="$R/rl/results/koh_2026-09-28/laptop_runs"
T="$R/rl/results/gauntlet_runs_2026-09-26/tsv"; B2E="$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"
B=/home/dacz8976/engine-kt-$S
source "$HOME/.cargo/env" 2>/dev/null || true
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
die() { note "FAILED: $*"; exit 1; }
cd "$R"; git fetch -q origin; git merge-base --is-ancestor "$C" "$BR" || die "$C not on $BR"

# ---- Part A: the build, the diff, identity.
DIFF=$(git diff --name-only 233bced "$C" -- engine)
echo "$DIFF" | grep -v -E '^engine/src/players/' | grep -q . && die "the kt build changes engine/ outside src/players: $(echo $DIFF | tr '\n' ' ')"
note "diff 233bced..$S under engine/: $(echo "$DIFF" | tr '\n' ' ') (players/ only)"
if [ ! -x "$B/engine/target/release/examples/legality_scan" ]; then
  rm -rf "$B"; mkdir -p "$B"; echo "$C" > "$B/COMMIT"; git archive "$C" engine decks | tar -x -C "$B"
  ( cd "$B/engine" && nice -n 10 cargo build --release -j 14 && nice -n 10 cargo build --release --example legality_scan -j 14 ) \
    > "$O/build.log" 2>&1 || die "build (build.log)"
fi
SCAN="$B/engine/target/release/examples/legality_scan"; GYM="$B/engine/target/release/deckgym"
note "kt build $S: legality_scan $(sha256sum "$SCAN" | cut -c1-16), deckgym $(sha256sum "$GYM" | cut -c1-16)"
git show "$BR:rl/results/kt_2026-09-26/identity/official_kq3_500.jsonl" > /tmp/kt_ref_kq3.jsonl
git show "$BR:rl/results/kt_2026-09-26/identity/43cef0b_kd3_40.jsonl" > /tmp/kt_ref_kd3.jsonl
git show "$BR:rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl" > /tmp/kt_ref_b2e_kog3.jsonl
run() {  # name args... (in $B/engine, 12 threads)
  local name=$1; shift
  [ -s "$O/$name.jsonl" ] && return
  local s=$(date +%s)
  ( cd "$B/engine" && RAYON_NUM_THREADS=12 nice -n 10 "$SCAN" "$@" --games-out "$O/$name.jsonl.part" ) > "$O/$name.txt" 2>&1 || die "$name"
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"
}
same() {  # mine ref max_i expected label
  python3 - "$@" >> "$O/identity_check.txt" <<'EOF' || die "IDENTITY FAILED: $5"
import json, sys
mine = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[1]))}
ref = {(g["pairing"], g["i"]): g for g in map(json.loads, open(sys.argv[2])) if g["i"] < int(sys.argv[3])}
f = [x for x in ("moves", "decisions", "openings", "winner_seat", "points", "seed") if all(x in g for g in ref.values())]
bad = [k for k in ref if k not in mine or any(mine[k][x] != ref[k][x] for x in f)]
print(f"{sys.argv[5]}: {len(ref) - len(bad)} of {len(ref)} equal on {f}")
sys.exit(1 if bad or len(ref) != int(sys.argv[4]) else 0)
EOF
}
TAB=(--decks ../decks/research); N17=(--pairs "$T/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 8 24)")
SCZ=(--pairs "$T/new_decks.tsv" --root "$R" --seed-base 21108000000 --pairings "$(seq -s, 0 7)")
BB=(--pairs "$B2E" --root "$R" --seed-base 21106000000 --pairings "$(seq -s, 0 95)")
run ${S}_id_k3_500 "${TAB[@]}" --games 500 --bot k3;   same "$O/${S}_id_k3_500.jsonl" "$K/table_k3.jsonl" 500 14000 "k3 v official"
run ${S}_id_kp3_500 "${TAB[@]}" --games 500 --bot kp3; same "$O/${S}_id_kp3_500.jsonl" "$K/table_kp3.jsonl" 500 14000 "kp3 v official"
run ${S}_id_kog3_500 "${TAB[@]}" --games 500 --bot kog3; same "$O/${S}_id_kog3_500.jsonl" "$KOG/table_kog3.jsonl" 500 14000 "kog3 v table_kog3"
run ${S}_id_kog3_new17 "${N17[@]}" --games 500 --bot kog3; same "$O/${S}_id_kog3_new17.jsonl" "$KOG/new17_kog3.jsonl" 500 8500 "kog3 v new17_kog3"
run ${S}_id_kq3_500 "${TAB[@]}" --games 500 --bot kq3; same "$O/${S}_id_kq3_500.jsonl" /tmp/kt_ref_kq3.jsonl 500 14000 "kq3 v official"
run ${S}_id_kd3_40 "${TAB[@]}" --games 40 --bot kd3;   same "$O/${S}_id_kd3_40.jsonl" /tmp/kt_ref_kd3.jsonl 40 1120 "kd3 v 43cef0b (official then)"
run ${S}_id_kpr3_40 "${TAB[@]}" --games 40 --bot kpr3; same "$O/${S}_id_kpr3_40.jsonl" "$K/table_kpr3.jsonl" 40 1120 "kpr3 v official"
run ${S}_id_kog3_b2e40 "${BB[@]}" --games 40 --bot kog3; same "$O/${S}_id_kog3_b2e40.jsonl" /tmp/kt_ref_b2e_kog3.jsonl 40 3840 "kog3 B2e i<40 v b2e_kog3"
run ${S}_id_kog3_scz40 "${SCZ[@]}" --games 40 --bot kog3; same "$O/${S}_id_kog3_scz40.jsonl" "$KL/scizor_kog3.jsonl" 40 320 "kog3 Scizor i<40 v scizor_kog3"
for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
  [[ $v == *charizardy* ]] && base=21106000000 || base=72000000
  np=$(tail -n +2 "$T/var_$v.tsv" | wc -l)
  run ${S}_id_kog3_var_${v}40 --pairs "$T/var_$v.tsv" --root "$R" --seed-base $base --games 40 --bot kog3
  same "$O/${S}_id_kog3_var_${v}40.jsonl" "$KL/var_${v}_kog3.jsonl" 40 $((np * 40)) "kog3 $v i<40 v var_${v}_kog3"
done
note "identity: $(tr '\n' ' ' < "$O/identity_check.txt")"
echo "$(date -u +%F\ %T) KT PART A DONE $S" >> "$O/STATUS.txt"

# ---- Part B: kt games, after koh's B2e read.
until [ -e "$O/GATE_koh_b2e_read" ]; do sleep 60; done
note "gate open: $(cat "$O/GATE_koh_b2e_read")"
# Timing (item 4). Both arms always run fresh: a restart must not reuse a cached arm, which would time it at 0 s
# (Astra's review via Fable, Sept 28). kog3 then kt3 back to back, wall seconds gating as registered, with user+sys
# CPU seconds recorded beside. This laptop is shared with other runs, so if kt3 is over 1.25x on the first pair,
# both arms are rerun once and the second pair decides.
TIMEFORMAT='%R %U %S'
timing_pair() {
  local b
  for b in kog3 kt3; do
    rm -f "$O/${S}_timing_${b}_40.jsonl"
    { time run ${S}_timing_${b}_40 "${TAB[@]}" --games 40 --bot $b; } 2> "$O/${S}_timing_${b}.time"
  done
  python3 - "$O/${S}_timing_kog3.time" "$O/${S}_timing_kt3.time" <<'EOF'
import sys
(wa, ua, sa), (wb, ub, sb) = [tuple(map(float, open(p).read().split()[-3:])) for p in sys.argv[1:3]]
r, c = wb / wa, (ub + sb) / (ua + sa)
print(f"kog3 {wa:.0f} s wall, {ua + sa:.0f} s CPU; kt3 {wb:.0f} s wall, {ub + sb:.0f} s CPU; "
      f"kt3/kog3 wall {r:.2f} (limit 1.25: {'within' if r <= 1.25 else 'OVER'}), CPU {c:.2f}")
sys.exit(0 if r <= 1.25 else 1)
EOF
}
if timing_pair > "$O/${S}_timing_1.txt"; then note "timing: $(cat "$O/${S}_timing_1.txt")"
else
  note "timing, first pair: $(cat "$O/${S}_timing_1.txt"); rerunning both arms once"
  timing_pair > "$O/${S}_timing_2.txt" || die "timing: kt3 over 1.25x kog3 on both pairs ($(cat "$O/${S}_timing_2.txt")); item 4: the per-leaf Tool classification is rewritten before the table"
  note "timing, second pair (decides): $(cat "$O/${S}_timing_2.txt")"
fi
for bot in kt3 kta3 ktb3 ktc3; do
  run ${S}_${bot}_table "${TAB[@]}" --games 500 --bot $bot
  run ${S}_${bot}_new17 "${N17[@]}" --games 500 --bot $bot
done
python3 - "$O" "$S" "$KOG" > "$O/footprint.txt" <<'EOF'
import json, sys
O, S, KOG = sys.argv[1:4]
load = lambda p: {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(p))}
base = {**load(f"{KOG}/table_kog3.jsonl"), **load(f"{KOG}/new17_kog3.jsonl")}
for bot in ("kt3", "kta3", "ktb3", "ktc3"):
    new = {**load(f"{O}/{S}_{bot}_table.jsonl"), **load(f"{O}/{S}_{bot}_new17.jsonl")}
    assert new.keys() == base.keys()
    d = sum(base[k]["moves"] != new[k]["moves"] for k in base)
    fp = 100 * d / len(base)
    route = ("reserve route (a)-(e)" if fp < 15 else "ordinary adoption rule") if bot in ("kt3", "kta3") else "attribution only"
    print(f"FOOTPRINT {bot}: {d} of {len(base)} paired games on the 45 cells differ from kog3's = {fp:.2f}% -> {route}")
EOF
note "footprint written (footprint.txt): read and commit it alone before anything else"
for bot in kt3 kta3; do
  run ${S}_mixed_table_${bot}_first "${TAB[@]}" --games 500 --bot-a $bot --bot-b kog3
  run ${S}_mixed_table_${bot}_second "${TAB[@]}" --games 500 --bot-a kog3 --bot-b $bot
  run ${S}_mixed_new17_${bot}_first "${N17[@]}" --games 500 --bot-a $bot --bot-b kog3
  run ${S}_mixed_new17_${bot}_second "${N17[@]}" --games 500 --bot-a kog3 --bot-b $bot
  run ${S}_b2e_${bot} "${BB[@]}" --games 500 --bot $bot
  # B2e's own-side mixed rows (Dustin, Sept 28 evening: coverage rows count for the mixed-row veto, so every time):
  # kt on the held deck (side a), kog3 on the panel; pairings 0-47 count, 48-95 (Dustin's files) reported.
  run ${S}_mixed_b2e_${bot}_first "${BB[@]}" --games 500 --bot-a $bot --bot-b kog3
  run ${S}_scizor_${bot} "${SCZ[@]}" --games 500 --bot $bot
  run ${S}_mixed_scizor_${bot}_first "${SCZ[@]}" --games 500 --bot-a $bot --bot-b kog3
  run ${S}_mixed_scizor_${bot}_second "${SCZ[@]}" --games 500 --bot-a kog3 --bot-b $bot
  for v in v-lucario_2 v-suicune_2 v-weezing_2 l-charizardy; do
    [[ $v == *charizardy* ]] && base=21106000000 || base=72000000
    f="$T/var_$v.tsv"
    sa=$(awk -F'\t' 'NR > 1 && $12 == "a" {print $1}' "$f" | paste -sd,); sb=$(awk -F'\t' 'NR > 1 && $12 == "b" {print $1}' "$f" | paste -sd,)
    run ${S}_var_${v}_${bot} --pairs "$f" --root "$R" --seed-base $base --games 500 --bot $bot
    [ -z "$sa" ] || run ${S}_var_${v}_${bot}_mixed_a --pairs "$f" --root "$R" --seed-base $base --pairings "$sa" --games 500 --bot-a $bot --bot-b kog3
    [ -z "$sb" ] || run ${S}_var_${v}_${bot}_mixed_b --pairs "$f" --root "$R" --seed-base $base --pairings "$sb" --games 500 --bot-a kog3 --bot-b $bot
  done
done
# Clause (d): the census Rayquaza list v the eight table lists, 22,700,000,000 + panel index x 10,000 + i.
H=$'pairing\tblock\theld_key\theld_file\topponent\tpanel_file\tseed_first\tseed_last\tsub_block_end'
{ echo "$H"; p=0; for opp in altaria blaziken hydreigon lucario sceptile suicune vespiquen weezing; do
    s=$((22700000000 + 10000 * p)); printf '%s\td\tc-rayquaza\trl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt\t%s\tdecks/research/%s.txt\t%s\t%s\t%s\n' $p $opp $opp $s $((s + 499)) $((s + 9999)); p=$((p + 1)); done
} > "$O/d_rayquaza.tsv"
DP=(--pairs "$O/d_rayquaza.tsv" --root "$R" --seed-base 22700000000 --pairings "$(seq -s, 0 7)")
run ${S}_d_kog3 "${DP[@]}" --games 500 --bot kog3
run ${S}_d_kta3 "${DP[@]}" --games 500 --bot-a kta3 --bot-b kog3
run ${S}_d_kt3 "${DP[@]}" --games 500 --bot-a kt3 --bot-b kog3
# The Rayquaza traces (item 9): kta3 and kog3 on Rayquaza, kog3 on Lucario, the kt build's deckgym, per-game rows.
cd "$R"
for p in kta3 kog3; do
  [ -s "$O/${S}_trace_rayquaza_${p}_pergame.jsonl" ] && continue
  nice -n 10 python3 rl/results/gauntlet_runs_2026-09-26/trace_pilot.py decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt \
    decks/screen/opponents/t-lucario.txt --games 200 --seed 21108900000 --pilot $p --opp-pilot kog3 --engine "$GYM" \
    --per-game "$O/${S}_trace_rayquaza_${p}_pergame.jsonl" > "$O/${S}_trace_rayquaza_${p}.txt" 2>&1 || die "trace $p"
  note "trace $p done"
done
echo "$(date -u +%F\ %T) KT PART B DONE $S" >> "$O/STATUS.txt"
