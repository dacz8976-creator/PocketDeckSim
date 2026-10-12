#!/usr/bin/env bash
# Rules switch 2's revert switches (PLAN (e); the coordinator via Dustin, Oct 9): one per gate of the round-2 package, made as P2's
# DECKGYM_FLAT_RETURN_DAMAGE. Every build is a git archive into a scratch folder with its own CARGO_TARGET_DIR.
#   1. The 8b deals (../../engine_switch_rules2_2026-10/early_warning_8b/: pairings 32-37, 40 deals, seeds 23,100,000,000 +
#      pairing x 10,000 + i, km3 then k3), played by legality_scan once per setting:
#        default (no variable): byte for byte the recorded new rows, and the engine before the switches (BASE);
#        DECKGYM_ROUND2_OFF=1: byte for byte the recorded old rows (the official engine, main-8626a35);
#        each gate off alone, and G1 + G2 together: each game equal to its new row or its old row, and which games go back to old.
#   2. The later round's smoke (../smoke/, km3, seeds 20,980,000,000 + pairing x 10,000 + i): every gate off = games_r_plain.jsonl
#      (R 1abdbe8, the official engine in behaviour); every gate off but G2 = games_round2_plain.jsonl (29e126a: the official
#      engine and the seven sites), each on every field both record.
#   3. The counter smoke (../../round2_readiness_2026-10-02/counter_smoke/, km3, seeds 20,990,000,000 + ...): P2 and G11 off =
#      games_round2_plain.jsonl (3090abb's engine, before P2 and P3).
#   4. The P3 smoke (../p3_smoke/, km3, seeds 20,920,000,000 + ...): the default and G11 off each = games_p3.jsonl.
#   5. deckgym simulate, km3 v km3, 240 games of altaria v blaziken at seed 7100: the default and DECKGYM_ROUND2_OFF=1 (the
#      whole-program path: the games run on worker threads) each game for game equal to the official program.
#   6. The revert check at the 21 look-ahead ticks of the 8b classification, and at its 4 control ticks: the official engine's
#      choice and every candidate's score (within 1e-9) against the switch head deciding that one decision with gates off
#      (score_dump_round2.rs): pairing 35's 17 with G1 + G2, pairing 37's 4 with P2, all 21 with every gate; the controls with
#      every single gate and with all.
# Usage: run_revert_gates.sh <work dir> <switch revision> <revision before the switches>   (from anywhere in the repository)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(git -C "$HERE" rev-parse --show-toplevel)
W=$1
NEW=$2
BASE=$3
OLD=8626a358     # main-8626a35: the official engine (rl/engine-2026-10-02/README.md)
MAIN=1163ebb7    # origin/main on Oct 9: the 8b rows' decks (as run_8b.sh)
R2=$REPO/rl/results/coin_prevention_round2_2026-10-01
B8=$REPO/rl/results/engine_switch_rules2_2026-10/early_warning_8b
CS=$REPO/rl/results/round2_readiness_2026-10-02/counter_smoke
mkdir -p "$W"
W=$(cd "$W" && pwd)
for c in "$NEW" "$BASE" "$OLD" "$MAIN" b77652d6; do git -C "$REPO" rev-parse --verify -q "$c^{commit}" > /dev/null || { echo "missing commit $c" >&2; exit 2; }; done
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/dg_patch.py > "$W/dg_patch.py"
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/trace_8c_sonnet/score_dump.rs > "$W/score_dump.rs"
git -C "$REPO" show b77652d6:rl/results/engine_switch_rules_2026-10/5a18d31_10_cli_km3.txt > "$W/pinned_10_cli_km3.txt"
rm -rf "$W/root" && mkdir -p "$W/root"
git -C "$REPO" archive "$MAIN" decks rl/results/engine_switch_rules_2026-10/scratch_8b | tar -x -C "$W/root"

src() {  # <name> <revision>: a fresh copy of that revision's engine/
    rm -rf "${W:?}/$1" "$W/target_$1"
    mkdir -p "$W/$1"
    git -C "$REPO" archive "$2" engine | tar -x -C "$W/$1"
}
build() {  # <name> <target...>
    local name=$1; shift
    for t in "$@"; do
        (cd "$W/$name/engine" && CARGO_TARGET_DIR="$W/target_$name" cargo build --release --locked $t 2>&1 | grep -E "^error" || true)
    done
}
sha() { sha256sum < "$1" | cut -c1-64; }

echo "== builds: switches $(git -C "$REPO" rev-parse --short "$NEW"), before them $(git -C "$REPO" rev-parse --short "$BASE"), official $OLD"
src new "$NEW";  build new "--example legality_scan" "--bin deckgym"
src base "$BASE"; build base "--example legality_scan"
src dump_new "$NEW"; python3 "$W/dg_patch.py" "$W/dump_new/engine" > /dev/null
cp "$HERE/score_dump_round2.rs" "$W/dump_new/engine/examples/score_dump.rs"; build dump_new "--example score_dump"
src dump_old "$OLD"; python3 "$W/dg_patch.py" "$W/dump_old/engine" > /dev/null
cp "$W/score_dump.rs" "$W/dump_old/engine/examples/score_dump.rs"; build dump_old "--example score_dump"
SCAN=$W/target_new/release/examples/legality_scan
DG=$W/target_new/release/deckgym
echo "legality_scan sha256 $(sha "$SCAN"); deckgym sha256 $(sha "$DG"); before the switches: legality_scan sha256 $(sha "$W/target_base/release/examples/legality_scan")"
(cd "$REPO/rl/engine-2026-10-02" && sha256sum -c SHA256SUMS --quiet) || { echo "pinned official programs: SHA256SUMS mismatch" >&2; exit 2; }
echo "official deckgym sha256 $(sha "$REPO/rl/engine-2026-10-02/deckgym") (SHA256SUMS verify)"

# The settings: a name and its environment variables.
GATE_VARS=(DECKGYM_FLAT_RETURN_DAMAGE DECKGYM_NO_PLAIN_HIT_COIN DECKGYM_PLAIN_QUEUED_SITES DECKGYM_NO_OWN_SIDE_COIN
    DECKGYM_WILL_SKIPS_GATE_COINS DECKGYM_NO_VICTORY_STAR_AFTER_BLOCK_COIN DECKGYM_TRAP_TERRITORY_ONCE DECKGYM_NO_OWN_SIDE_GUTS
    DECKGYM_NO_PERISH_ON_QUEUED_HIT DECKGYM_LUXURY_COIN_ANY_STADIUM DECKGYM_FOSSIL_UNDER_ITEM_LOCK DECKGYM_FOSSIL_NOT_ITEM)
GATES=(p2 g1 g2 g3 g4 g5 g6 g7 g8 g9 g10 g11)
envs() {  # <setting>: the env assignments for it
    case $1 in
        default) ;;
        all) echo DECKGYM_ROUND2_OFF=1 ;;
        all_but_g2) for v in "${GATE_VARS[@]}"; do [ "$v" = DECKGYM_PLAIN_QUEUED_SITES ] || echo "$v=1"; done ;;
        p2_g11) echo DECKGYM_FLAT_RETURN_DAMAGE=1; echo DECKGYM_FOSSIL_NOT_ITEM=1 ;;
        g1_g2) echo DECKGYM_NO_PLAIN_HIT_COIN=1; echo DECKGYM_PLAIN_QUEUED_SITES=1 ;;
        *) for i in "${!GATES[@]}"; do [ "${GATES[$i]}" = "$1" ] && echo "${GATE_VARS[$i]}=1"; done ;;
    esac
}
scan() {  # <setting> <program> <out> <legality_scan args...>
    local setting=$1 prog=$2 out=$3; shift 3
    env $(envs "$setting") "$prog" "$@" --games-out "$out" > "$out.page" 2>&1
}

echo "== 1. the 8b deals"
for bot in km3 k3; do
    (cd "$W/new/engine" && scan default "$W/target_base/release/examples/legality_scan" "$W/8b_base_$bot.jsonl" --pairs "$B8/pairs_8b.tsv" \
        --root "$W/root" --seed-base 23100000000 --pairings 32,33,34,35,36,37 --games 40 --bot "$bot")
    for s in default all g1_g2 "${GATES[@]}"; do
        (cd "$W/new/engine" && scan "$s" "$SCAN" "$W/8b_${s}_$bot.jsonl" --pairs "$B8/pairs_8b.tsv" --root "$W/root" \
            --seed-base 23100000000 --pairings 32,33,34,35,36,37 --games 40 --bot "$bot")
    done
done
python3 - "$W" "$B8" <<'PY'
import json, sys
W, B8 = sys.argv[1:]
load = lambda p: {(r["pairing"], r["i"]): r for r in map(json.loads, open(p))}
same_bytes = lambda a, b: open(a, "rb").read() == open(b, "rb").read()
for bot in ("km3", "k3"):
    new, old = load(f"{B8}/8b_new_{bot}.jsonl"), load(f"{B8}/8b_old_{bot}.jsonl")
    changed = sorted(k for k in new if new[k] != old[k])
    print(f"{bot}: {len(new)} deals; the official engine and the round-2 head differ in {len(changed)}: {changed}")
    print(f"  default: byte for byte the recorded new rows: {same_bytes(f'{W}/8b_default_{bot}.jsonl', f'{B8}/8b_new_{bot}.jsonl')}; "
          f"and the engine before the switches: {same_bytes(f'{W}/8b_default_{bot}.jsonl', f'{W}/8b_base_{bot}.jsonl')}")
    print(f"  all off (DECKGYM_ROUND2_OFF=1): byte for byte the recorded old rows: {same_bytes(f'{W}/8b_all_{bot}.jsonl', f'{B8}/8b_old_{bot}.jsonl')}")
    for s in ("g1_g2", "p2", "g1", "g2", "g3", "g4", "g5", "g6", "g7", "g8", "g9", "g10", "g11"):
        got = load(f"{W}/8b_{s}_{bot}.jsonl")
        neither = sorted(k for k in new if got[k] != new[k] and got[k] != old[k])
        to_old = sorted(k for k in changed if got[k] == old[k])
        print(f"  {s} off: as the official engine in {len(to_old)} of the {len(changed)} changed deals {to_old}; "
              f"as neither engine in {len(neither)} {neither}; every other deal as the round-2 head")
PY

echo "== 2. the later round's smoke"
for s in all all_but_g2; do
    (cd "$R2/smoke" && scan "$s" "$SCAN" "$W/smoke_$s.jsonl" --pairs pairs.tsv --root . --seed-base 20980000000 --games 40 --bot km3)
done
echo "== 3. the counter smoke"
(cd "$REPO" && scan p2_g11 "$SCAN" "$W/counter_p2_g11.jsonl" --pairs "$CS/pairs.tsv" --root . --seed-base 20990000000 --games 20 --bot km3)
echo "== 4. the P3 smoke"
for s in default g11; do
    (cd "$REPO" && scan "$s" "$SCAN" "$W/p3_$s.jsonl" --pairs "$R2/p3_smoke/pairs.tsv" --root . --seed-base 20920000000 --games 40 --bot km3)
done
python3 - "$W" "$R2" "$CS" <<'PY'
import json, sys
W, R2, CS = sys.argv[1:]
load = lambda p: {(r["pairing"], r["i"]): r for r in map(json.loads, open(p))}
def compare(label, got_path, ref_path):
    got, ref = load(got_path), load(ref_path)
    fields = set.intersection(*(set(r) for r in ref.values())) & set.intersection(*(set(r) for r in got.values()))
    bad = sorted(k for k in ref if k not in got or any(got[k][f] != ref[k][f] for f in fields))
    print(f"{label}: {len(got)} games against {len(ref)}; equal on the {len(fields)} fields both record in "
          f"{len(ref) - len(bad)}; different: {bad}")
compare("2. every gate off v games_r_plain.jsonl (R 1abdbe8)", f"{W}/smoke_all.jsonl", f"{R2}/smoke/games_r_plain.jsonl")
compare("2. every gate off but G2 v games_round2_plain.jsonl (29e126a)", f"{W}/smoke_all_but_g2.jsonl", f"{R2}/smoke/games_round2_plain.jsonl")
compare("3. P2 and G11 off v the counter smoke's games_round2_plain.jsonl (3090abb)", f"{W}/counter_p2_g11.jsonl", f"{CS}/games_round2_plain.jsonl")
compare("4. default v games_p3.jsonl", f"{W}/p3_default.jsonl", f"{R2}/p3_smoke/games_p3.jsonl")
compare("4. G11 off v games_p3.jsonl", f"{W}/p3_g11.jsonl", f"{R2}/p3_smoke/games_p3.jsonl")
PY

echo "== 5. km3 v km3, 240 games, altaria v blaziken, seed 7100"
for v in official default all; do
    rm -rf "$W/sim_$v"; mkdir -p "$W/sim_$v"
    bin=$DG; [ $v = official ] && bin=$REPO/rl/engine-2026-10-02/deckgym
    (cd "$REPO" && env $(envs "$([ $v = official ] && echo default || echo $v)") "$bin" simulate --num 240 --players km3,km3 --seed 7100 \
        --seed-stream -p --results-output "$W/sim_$v" decks/research/altaria.txt decks/research/blaziken.txt > "$W/simulate_$v.txt" 2>&1)
    if diff <(sed 6d "$W/simulate_$v.txt") <(sed 6d "$W/pinned_10_cli_km3.txt") > /dev/null; then
        echo "$v: equal to the pinned record 5a18d31_10_cli_km3.txt on every line but line 6 (the wall time)"
    else
        echo "$v: DIFFERENT from the pinned record"
    fi
done
python3 "$R2/switch_gates/compare_simulate.py" official="$W/sim_official" default="$W/sim_default"
python3 "$R2/switch_gates/compare_simulate.py" official="$W/sim_official" all="$W/sim_all"

echo "== 6. the revert check"
deck() { awk -F'\t' -v p="$1" -v c="$2" 'NR > 1 && $1 == p {print $c}' "$B8/pairs_8b.tsv"; }
dump() {  # <bot> <pairing> <deal> <tick> <old|new|gate list>
    local bin=$W/target_dump_new/release/examples/score_dump flags=()
    [ "$5" = old ] && bin=$W/target_dump_old/release/examples/score_dump
    [ "$5" != old ] && [ "$5" != new ] && flags=(--revert "$5")
    (cd "$W/root" && "$bin" --a "$(deck "$2" 4)" --b "$(deck "$2" 6)" --seed-base 23100000000 --pairing "$2" --bot "$1" --deal "$3" \
        --tick "$4" "${flags[@]}" > "$W/dump_$1_$2_$3_$4_$5.txt" 2>&1)
}
TICKS_35="km3:2:89 km3:3:44 km3:10:43 km3:13:60 km3:14:41 km3:26:44 km3:30:38 km3:31:58 km3:35:90 km3:37:48 km3:38:69
    k3:10:40 k3:13:59 k3:14:42 k3:19:35 k3:26:41 k3:30:38"
TICKS_37="km3:15:51 k3:23:77 k3:34:48 k3:35:68"
CONTROLS="km3:1:9 km3:3:8 k3:1:9 k3:3:8"
jobs=()
for t in $TICKS_35; do IFS=: read -r b i k <<< "$t"; for v in old new g1,g2 all; do jobs+=("$b 35 $i $k $v"); done; done
for t in $TICKS_37; do IFS=: read -r b i k <<< "$t"; for v in old new p2 all; do jobs+=("$b 37 $i $k $v"); done; done
for t in $CONTROLS; do IFS=: read -r b i k <<< "$t"; for v in old new all "${GATES[@]}"; do jobs+=("$b 33 $i $k $v"); done; done
export -f dump deck; export W B8
printf '%s\n' "${jobs[@]}" | xargs -P "$(nproc)" -I{} bash -c 'dump {}'
python3 - "$W" "$TICKS_35" "$TICKS_37" "$CONTROLS" <<'PY'
import re, sys
W, t35, t37, controls = sys.argv[1], *(s.split() for s in sys.argv[2:])
def read(name):
    lines = open(f"{W}/{name}", encoding="utf-8").read().splitlines()
    start = max(i for i, l in enumerate(lines) if l.startswith("PGTICK") and "asked about" in l)
    chosen = next(l.split("chose ", 1)[1] for l in lines if l.startswith("deal ") and "chose " in l)
    return chosen, [(float(m[1]), m[2]) for l in lines[start:] if (m := re.match(r"PGDUMP\s+(-?[\d.eE+-]+) (.*)$", l))]
same = lambda x, y: x[0] == y[0] and len(x[1]) == len(y[1]) and all(abs(p[0] - q[0]) < 1e-9 and p[1] == q[1] for p, q in zip(x[1], y[1]))
tally = {}
for pairing, ticks, reverts in ((35, t35, ("g1,g2", "all")), (37, t37, ("p2", "all"))):
    for t in ticks:
        bot, i, k = t.split(":")
        old, new = (read(f"dump_{bot}_{pairing}_{i}_{k}_{v}.txt") for v in ("old", "new"))
        row = [f"{bot} pairing {pairing} deal {i} tick {k}: {len(old[1])} candidates; the round-2 head changed the choice: "
               f"{'yes' if new[0] != old[0] else 'NO'}"]
        for v in reverts:
            ok = same(old, read(f"dump_{bot}_{pairing}_{i}_{k}_{v}.txt"))
            tally[(pairing, v)] = tally.get((pairing, v), 0) + ok
            row.append(f"{v} off: the official choice and every score {'yes' if ok else 'NO'}")
        print("; ".join(row))
for (pairing, v), n in tally.items():
    print(f"pairing {pairing}, {v} off for the one decision: {n} of {len(t35 if pairing == 35 else t37)} give the official choice and scores")
for t in controls:
    bot, i, k = t.split(":")
    old = read(f"dump_{bot}_33_{i}_{k}_old.txt")
    bad = [v for v in ("new", "all", "p2", *(f"g{n}" for n in range(1, 12))) if not same(old, read(f"dump_{bot}_33_{i}_{k}_{v}.txt"))]
    print(f"control {bot} pairing 33 deal {i} tick {k}: {len(old[1])} candidates; the head, every gate off alone and all off give the "
          f"official choice and scores: {'yes' if not bad else 'NO: ' + ', '.join(bad)}")
PY
