#!/usr/bin/env bash
# P2's off-switch, gates 1 and 2 (the coordinator via Dustin, Oct 9). Every build is a git archive of claude/coin-prevention-round2
# into a scratch folder with its own CARGO_TARGET_DIR.
#   Gate 1, the default is P2:
#     (a) legality_scan replays the P2 smoke's 200 deals (../../round2_readiness_2026-10-02/counter_smoke_p2/, km3, seeds
#         20,960,000,000 + pairing x 10,000 + i) byte for byte as games_p2_plain.jsonl;
#     (b) deckgym simulate, km3 v km3, 240 games of altaria v blaziken at seed 7100 (the pinned record 5a18d31_10_cli_km3.txt):
#         game for game equal to the official program rl/engine-2026-10-02/deckgym (the table can't change: inventory 0 of 28);
#     (c) the counter probe prints counter_probe_readiness_output.txt exactly.
#   Gate 2, off (DECKGYM_FLAT_RETURN_DAMAGE=1) is the engine before P2:
#     (a) the same replay equals games_p_plain.jsonl (built from d3739b7d, the engine before P2) byte for byte;
#     (b) the same 240 games, equal again;
#     (c) the probe prints counter_probe_readiness_output_at_P.txt exactly (78 checks, 11 failures);
#     (d) the revert check at the three games P2 changed (all in look-ahead; first_difference_output.txt): at the first differing
#         tick, the P2 head deciding with the switch off for that one decision (score_dump_p2.rs --revert-return) gives the old
#         engine's choice and every candidate's score (within 1e-9). Scores come from main's print-only dg_patch.py (PG_DUMP),
#         applied to both scratch engines.
# Usage: run_switch_gates.sh <work dir> <switch revision> <before-P2 revision>   (from anywhere in the repository)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
NEW=$2
OLD=$3
SMOKE=$REPO/rl/results/round2_readiness_2026-10-02/counter_smoke_p2
RD=$REPO/rl/results/round2_readiness_2026-10-02
mkdir -p "$W"
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/dg_patch.py > "$W/dg_patch.py"
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs > "$W/score_dump.rs"
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/5a18d31_10_cli_km3.txt > "$W/pinned_10_cli_km3.txt"

src() {  # <name> <revision>: a fresh copy of that revision's engine/
    rm -rf "${W:?}/$1"
    mkdir -p "$W/$1"
    git -C "$REPO" archive "$2" engine | tar -x -C "$W/$1"
}
sha() { sha256sum < "$1" | cut -c1-64; }

echo "== builds ($NEW = $(git -C "$REPO" rev-parse --short "$NEW"), $OLD = $(git -C "$REPO" rev-parse --short "$OLD"))"
src new "$NEW"
python3 "$RD/../coin_prevention_repair_2026-09-30/instrument_scan.py" --emit-fns "$W/new/engine/examples/r2_counter_fns.rs" > /dev/null
cp "$RD/counter_probe_readiness.rs" "$W/new/engine/examples/"
(cd "$W/new/engine" && CARGO_TARGET_DIR="$W/target_new" cargo build --release --locked --example legality_scan 2>&1 | grep -E "Finished|^error"
 cd "$W/new/engine" && CARGO_TARGET_DIR="$W/target_new" cargo build --release --locked --bin deckgym 2>&1 | grep -E "Finished|^error"
 cd "$W/new/engine" && CARGO_TARGET_DIR="$W/target_new" cargo build --release --locked --features test-utils --example counter_probe_readiness 2>&1 | grep -E "Finished|^error")
for p in "dump_new $NEW score_dump_p2.rs" "dump_old $OLD score_dump.rs"; do
    set -- $p
    src "$1" "$2"
    python3 "$W/dg_patch.py" "$W/$1/engine" > /dev/null
    cp "$( [ "$3" = score_dump_p2.rs ] && echo "$HERE/$3" || echo "$W/$3")" "$W/$1/engine/examples/score_dump.rs"
    (cd "$W/$1/engine" && CARGO_TARGET_DIR="$W/target_$1" cargo build --release --locked --example score_dump 2>&1 | grep -E "Finished|^error")
done
SCAN=$W/target_new/release/examples/legality_scan
DG=$W/target_new/release/deckgym
PROBE=$W/target_new/release/examples/counter_probe_readiness
echo "legality_scan sha256 $(sha "$SCAN"); deckgym sha256 $(sha "$DG"); counter_probe_readiness sha256 $(sha "$PROBE")"
echo "official deckgym sha256 $(sha "$REPO/rl/engine-2026-10-02/deckgym")"

echo "== gate 1(a) and 2(a): the P2 smoke's 200 deals"
for v in on off; do
    env=(); [ $v = off ] && env=(env DECKGYM_FLAT_RETURN_DAMAGE=1)
    (cd "$REPO" && "${env[@]}" "$SCAN" --pairs "$SMOKE/pairs.tsv" --root . --seed-base 20960000000 --games 50 --bot km3 \
        --games-out "$W/smoke_$v.jsonl" > "$W/smoke_$v.page" 2>&1)
done
cmp -s "$W/smoke_on.jsonl" "$SMOKE/games_p2_plain.jsonl" && echo "switch on (default): byte for byte games_p2_plain.jsonl ($(wc -l < "$W/smoke_on.jsonl") games)" || echo "switch on: DIFFERENT from games_p2_plain.jsonl"
cmp -s "$W/smoke_off.jsonl" "$SMOKE/games_p_plain.jsonl" && echo "switch off: byte for byte games_p_plain.jsonl, the engine before P2 ($(wc -l < "$W/smoke_off.jsonl") games)" || echo "switch off: DIFFERENT from games_p_plain.jsonl"

echo "== gate 1(b) and 2(b): km3 v km3, 240 games, altaria v blaziken, seed 7100"
for v in official on off; do
    rm -rf "$W/sim_$v"; mkdir -p "$W/sim_$v"
    bin=$DG; env=()
    [ $v = official ] && bin=$REPO/rl/engine-2026-10-02/deckgym
    [ $v = off ] && env=(env DECKGYM_FLAT_RETURN_DAMAGE=1)
    (cd "$REPO" && "${env[@]}" "$bin" simulate --num 240 --players km3,km3 --seed 7100 --seed-stream -p --results-output "$W/sim_$v" \
        decks/research/altaria.txt decks/research/blaziken.txt > "$W/simulate_$v.txt" 2>&1)
    if diff <(sed 6d "$W/simulate_$v.txt") <(sed 6d "$W/pinned_10_cli_km3.txt") > /dev/null; then
        echo "$v: equal to the pinned record 5a18d31_10_cli_km3.txt on every line but line 6 (the wall time)"
    else
        echo "$v: DIFFERENT from the pinned record"
    fi
done
python3 "$HERE/compare_simulate.py" official="$W/sim_official" on="$W/sim_on"
python3 "$HERE/compare_simulate.py" official="$W/sim_official" off="$W/sim_off"

echo "== gate 1(c) and 2(c): the counter probe"
(cd "$W/new/engine" && "$PROBE" > "$W/probe_on.txt" 2>/dev/null || true)
(cd "$W/new/engine" && DECKGYM_FLAT_RETURN_DAMAGE=1 "$PROBE" > "$W/probe_off.txt" 2>/dev/null || true)
cmp -s "$W/probe_on.txt" "$RD/counter_probe_readiness_output.txt" && echo "switch on: counter_probe_readiness_output.txt exactly ($(tail -1 "$W/probe_on.txt"))" || echo "switch on: DIFFERENT probe output"
cmp -s "$W/probe_off.txt" "$RD/counter_probe_readiness_output_at_P.txt" && echo "switch off: counter_probe_readiness_output_at_P.txt exactly ($(tail -1 "$W/probe_off.txt"))" || echo "switch off: DIFFERENT probe output"

echo "== gate 2(d): the revert check at the three games P2 changed"
deck() { awk -F'\t' -v p="$1" -v c="$2" 'NR > 1 && $1 == p {print $c}' "$SMOKE/pairs.tsv"; }
for g in "0 31 44" "1 21 84" "1 8 43"; do
    set -- $g
    for v in old new revert; do
        bin=$W/target_dump_new/release/examples/score_dump; flags=()
        [ $v = old ] && bin=$W/target_dump_old/release/examples/score_dump
        [ $v = revert ] && flags=(--revert-return)
        (cd "$REPO" && "$bin" --a "$(deck "$1" 3)" --b "$(deck "$1" 5)" --seed-base 20960000000 --pairing "$1" --bot km3 --deal "$2" \
            --tick "$3" "${flags[@]}" > "$W/dump_${1}_${2}_$v.txt" 2>&1)
    done
done
python3 - "$W" <<'PY'
import re, sys
W = sys.argv[1]
def read(name):
    lines = open(f"{W}/{name}", encoding="utf-8").read().splitlines()
    start = max(i for i, l in enumerate(lines) if l.startswith("PGTICK") and "asked about" in l)
    chosen = next(l.split("chose ", 1)[1] for l in lines if l.startswith("deal ") and "chose " in l)
    cands = [(float(m[1]), m[2]) for l in lines[start:] if (m := re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", l))]
    return chosen, cands
same = lambda x, y: len(x) == len(y) and all(abs(p[0] - q[0]) < 1e-9 and p[1] == q[1] for p, q in zip(x, y))
for p, i, k in ((0, 31, 44), (1, 21, 84), (1, 8, 43)):
    old, new, rev = (read(f"dump_{p}_{i}_{v}.txt") for v in ("old", "new", "revert"))
    print(f"pairing {p} deal {i} tick {k}: {len(old[1])} candidates")
    print(f"  before P2: {old[0]}")
    print(f"  P2:        {new[0]}")
    print(f"  P2, switch off for this decision: {rev[0]}")
    print(f"  P2 changed the choice: {'yes' if new[0] != old[0] else 'NO'}; the switch gives the old choice back: "
          f"{'yes' if rev[0] == old[0] else 'NO'}; every candidate's score equal to the old engine's: {'yes' if same(old[1], rev[1]) else 'NO'}")
PY
