#!/usr/bin/env bash
# The small checks before the gauntlet runs (Sept 26): a few hundred games, run on Sept 26 while the laptop was
# running the cloud's engine-repair replays. By the coordinator's instruction (Dustin's CPU priority: the replays are
# the critical path) this script does NOT use B2e's idle_or_die refusal; it runs at the lowest priority instead,
# nice -n 19 with RAYON_NUM_THREADS=2. The big runs (run_gauntlet_new.sh, run_gauntlet_variation.sh) keep idle_or_die.
#
# 1. Identity of the variation mechanism, kp3 (the pilot of the variation check), 2 pairings x 20 deals each:
#    the MAIN lists through the same TSV rows the variants use (tsv/id_<deck>_main.tsv).
#    - Lucario (pairings 2 and 18), Suicune (4 and 25), Weezing (6 and 27): --seed-base 72000000, the table's pairing
#      numbers, the table's first-named deck held. Each deck is on the second side in the first pairing and on the
#      first side in the second, except Weezing, which is second-named in all 7. Compared with the table's kp3 games
#      (../public_pricing_2026-09-25/kp3_500_*.jsonl) by ../engine_identity_2026-09-25/compare.py (IDENTICAL), and
#      line by line with the official 7fc6ccb scan's own lines for those deals (../engine_identity_2026-09-25/
#      kp3_500.jsonl; b2e_checks.py same --drop a_file,b_file: equal once the two file keys are removed).
#    - Charizard Y (B2e pairings 40 and 47): --seed-base 21106000000, B2e's own rows; compared with
#      ../b2e_rows_2026-09-26/b2e_kp3_arch.jsonl byte for byte (b2e_checks.py same) and by compare.py.
# 2. Smokes at the real seeds, so the big runs replay these games (the reader checks that they do):
#    - (a) tsv/new_decks.tsv, all 25 pairings x 2 deals (one per seat), k3 and kp3.
#    - (b) every tsv/var_*.tsv, all its pairings x 2 deals, kp3 (87 pairings).
#    Each smoke file must pass gauntlet_checks.py rows. They test that every new list loads and plays under the
#    scan, list any legality findings early, and give the reader real files to be tested on.
# The last line of identity/identity_check.txt is "GAUNTLET IDENTITY PASS <scan sha256>: ..." or
# "GAUNTLET IDENTITY FAIL: ...". Usage (WSL): bash run_identity.sh  (after bash stage_inputs.sh)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/gauntlet_runs_2026-09-26"
I="$D/identity"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
RES="$R/rl/results"
CHK="$RES/b2e_rows_2026-09-26/b2e_checks.py"
CMP="$RES/engine_identity_2026-09-25/compare.py"
REF_KP3=("$RES/public_pricing_2026-09-25/kp3_500_worst5.jsonl" "$RES/public_pricing_2026-09-25/kp3_500_rest.jsonl")
OFF_KP3="$RES/engine_identity_2026-09-25/kp3_500.jsonl"
B2E_KP3="$RES/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl"
OUT="$I/identity_check.txt"
fail() { echo "GAUNTLET IDENTITY FAIL: $*" | tee -a "$OUT" >&2; exit 1; }
scan() { RAYON_NUM_THREADS=2 nice -n 19 "$SCAN" "$@"; }

mkdir -p "$I"
[ ! -e "$OUT" ] || { echo "$OUT exists; move it away to re-run" >&2; exit 1; }
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
{
  echo "gauntlet identity and smokes, $(date -u +%FT%TZ); scan $SCAN sha256 $SHA"
  echo "priority: nice -n 19, RAYON_NUM_THREADS=2, no idle refusal (the laptop was running the engine-repair replays)"
  echo "pre-repair engine (7fc6ccb); re-run at the repaired engine when it becomes the baseline"
} > "$OUT"
[ "$(tail -n 1 "$RES/b2e_rows_2026-09-26/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] \
  || fail "the B2e identity_check.txt does not end in the IDENTITY PASS line for $SHA"
( cd "$B" && sha256sum --quiet -c "$D/inputs_sha256.txt" ) || fail "a staged input in $B changed (inputs_sha256.txt)"
while read -r _ f; do cmp -s "$R/$f" "$B/$f" || fail "$f: the working copy differs from the staged copy"; done < "$D/inputs_sha256.txt"
echo "inputs: $(wc -l < "$D/inputs_sha256.txt") staged files equal inputs_sha256.txt and the working copy" >> "$OUT"

cd "$B/engine"
# 1. Identity.
for spec in "lucario 2,18" "suicune 4,25" "weezing 6,27" "charizardy 40,47"; do
  set -- $spec
  deck=$1; ps=$2
  if [ "$deck" = charizardy ]; then base=21106000000; else base=72000000; fi
  new="$I/id_${deck}_kp3.jsonl"
  echo "== $deck, main list, pairings $ps x 20 deals, kp3, --seed-base $base" >> "$OUT"
  s=$(date +%s)
  scan --pairs "$B/rl/results/gauntlet_runs_2026-09-26/tsv/id_${deck}_main.tsv" --seed-base "$base" --games 20 \
    --bot kp3 --pairings "$ps" --games-out "$new" > "$I/id_${deck}_kp3.txt" 2>&1 || fail "$deck: the scan exited non-zero"
  echo "   $(( $(date +%s) - s )) s wall" >> "$OUT"
  if [ "$deck" = charizardy ]; then
    python3 "$CHK" subset "$I/ref_${deck}_kp3.jsonl" kp3 "$ps" 20 "$B2E_KP3" >> "$OUT" || fail "$deck: reference cut"
    python3 "$CMP" "$new" "$I/ref_${deck}_kp3.jsonl" >> "$OUT" || fail "$deck: compare.py NOT IDENTICAL"
    python3 "$CHK" same "$new" "$I/ref_${deck}_kp3.jsonl" >> "$OUT" || fail "$deck: not byte for byte B2e's lines"
  else
    python3 "$CHK" subset "$I/ref_${deck}_kp3.jsonl" kp3 "$ps" 20 "${REF_KP3[@]}" >> "$OUT" || fail "$deck: reference cut"
    python3 "$CMP" "$new" "$I/ref_${deck}_kp3.jsonl" >> "$OUT" || fail "$deck: compare.py NOT IDENTICAL"
    python3 "$CHK" subset "$I/off_${deck}_kp3.jsonl" kp3 "$ps" 20 "$OFF_KP3" >> "$OUT" || fail "$deck: official cut"
    python3 "$CHK" same --drop a_file,b_file "$new" "$I/off_${deck}_kp3.jsonl" >> "$OUT" \
      || fail "$deck: not the official scan's lines"
  fi
done

# 2. Smokes (2 deals per pairing, the real seeds).
TSV="$B/rl/results/gauntlet_runs_2026-09-26/tsv"
ROWS=()
for bot in k3 kp3; do
  s=$(date +%s)
  scan --pairs "$TSV/new_decks.tsv" --seed-base 21108000000 --games 2 --bot "$bot" \
    --games-out "$I/smoke_new_$bot.jsonl" > "$I/smoke_new_$bot.txt" 2>&1 || fail "smoke (a) $bot exited non-zero"
  echo "== smoke (a) new_decks.tsv x 2 deals, $bot: $(( $(date +%s) - s )) s wall" >> "$OUT"
  ROWS+=("$D/tsv/new_decks.tsv" 21108000000 2 "$bot" "$I/smoke_new_$bot.jsonl")
done
for t in "$TSV"/var_*.tsv; do
  v=$(basename "$t" .tsv); v=${v#var_}
  if [[ "$v" == *charizardy* ]]; then base=21106000000; else base=72000000; fi
  s=$(date +%s)
  scan --pairs "$t" --seed-base "$base" --games 2 --bot kp3 --games-out "$I/smoke_var_${v}_kp3.jsonl" \
    > "$I/smoke_var_${v}_kp3.txt" 2>&1 || fail "smoke (b) $v exited non-zero"
  echo "== smoke (b) var_$v.tsv x 2 deals, kp3: $(( $(date +%s) - s )) s wall" >> "$OUT"
  ROWS+=("$D/tsv/var_$v.tsv" "$base" 2 kp3 "$I/smoke_var_${v}_kp3.jsonl")
done
python3 "$D/gauntlet_checks.py" rows "${ROWS[@]}" >> "$OUT" || fail "the smokes' rows check"
echo "GAUNTLET IDENTITY PASS $SHA: kp3 main lists through the variation TSVs replay the reference games (Lucario 2,18; Suicune 4,25; Weezing 6,27 on the table's deals: compare.py IDENTICAL and the official scan's lines once a_file/b_file are dropped; Charizard Y 40,47 on B2e's deals: byte for byte); smokes: 25 new-deck pairings x 2 deals under k3 and kp3 and 87 variation pairings x 2 deals under kp3, ROWS PASS" >> "$OUT"
tail -n 1 "$OUT"
