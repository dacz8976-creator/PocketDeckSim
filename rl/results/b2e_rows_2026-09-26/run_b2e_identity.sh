#!/usr/bin/env bash
# Identity check of the B2e scan, before any B2e game is played or read. Table pairings 0, 5, 13 and 23 x 500 deals,
# for k3 and for kp3; every step must pass or the script writes IDENTITY FAIL and exits 1.
#   (a) DEFAULT flags (no --pairs, no --seed-base, no --root, no --decks: the table's eight decks from
#       ../decks/research and seeds 72,000,000 + pairing x 10,000 + i). Two comparisons:
#       - the specification's: compare.py against the table's reference files, field by field on a, b, seed,
#         first_seat, moves (the move hash), winner_seat, points, turns and first_deck_score:
#           k3:  ../per_game_table_2026-09-25/k3_500.jsonl
#           kp3: ../public_pricing_2026-09-25/kp3_500_worst5.jsonl + kp3_500_rest.jsonl
#       - stricter: every line byte for byte equal to the official, unpatched 7fc6ccb scan's own output on the same
#         deals (../engine_identity_2026-09-25/{k3,kp3}_500.jsonl, written by legality_scan d5c0a952...), so the
#         fields compare.py skips (hyper_ray, chase_order) and any added key are covered too.
#   (b) --PAIRS mode on the same deals: a pairings file listing the same four table pairings with their
#       decks/research files (b2e_checks.py table_tsv), run with --seed-base 72,000,000, must replay the same games
#       (compare.py against the table references; and equal to the official scan's lines once a_file and b_file
#       are removed). This is the code path that plays every B2e game. The equality relies on the table deals
#       having no findings (the official logs say "none"): in --pairs mode a game with findings also carries
#       findings and finding_examples, so such a deal would FAIL here (b2e_checks.py same names the keys), not pass.
#   (c) --pairs guards: the scan must refuse --pairs without --seed-base, --pairs with --decks, a seed_first that
#       doesn't match --seed-base, --games above 10,000 with --pairs, and --seed-base or --root without --pairs,
#       before playing anything.
# Never beside the network training, a build or another game run: idle_or_die (below) refuses to start while the
# run5-venv python (train_v5.py), cargo, rustc, deckgym or a legality_scan is running; the scans run niced with
# RAYON_NUM_THREADS = cores - 2 (spec section 4 "Time"; Fable's review M4).
# compare.py given the whole 14,000-game reference would print NOT IDENTICAL for any subset ("only in reference"
# > 0), so each reference is first cut to exactly these 2,000 games per pilot (b2e_checks.py subset, which also
# checks the pilot fields); compare.py must then say IDENTICAL with 2,000 games in both and none on one side only.
# Writes identity_check.txt, whose last line is either
#   IDENTITY PASS <sha256 of the binary> ...      or      IDENTITY FAIL: <why>
# and exits 1 on FAIL. run_b2e_rows.sh and read_b2e.py refuse to run without the PASS line for this binary.
# Usage (in WSL, after build_b2e_scan.sh):  bash run_b2e_identity.sh      8,000 games in all (about 8 minutes per
# pilot at cloud speed, more on the laptop).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/b2e_rows_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
OUT="$D/identity_check.txt"
CHECKS="$D/b2e_checks.py"
COMPARE="$D/../engine_identity_2026-09-25/compare.py"
PAIRINGS=0,5,13,23   # the minimum the spec asks for; 0,1,...,27 replays the whole table (14,000 games per pilot)
GAMES=500
TABLE_BASE=72000000  # the table's own seed base: (b) replays the table's deals, it uses no new seeds
N=$(python3 -c "print(f'{len(\"$PAIRINGS\".split(\",\")) * $GAMES:,}')")        # games per pilot, as compare.py prints it
N2=$(python3 -c "print(f'{2 * len(\"$PAIRINGS\".split(\",\")) * $GAMES:,}')")   # both pilots
REF_k3=("$D/../per_game_table_2026-09-25/k3_500.jsonl")
REF_kp3=("$D/../public_pricing_2026-09-25/kp3_500_worst5.jsonl" "$D/../public_pricing_2026-09-25/kp3_500_rest.jsonl")
OFF_k3=("$D/../engine_identity_2026-09-25/k3_500.jsonl")
OFF_kp3=("$D/../engine_identity_2026-09-25/kp3_500.jsonl")
XT="$B/identity_pairs.tsv"
fail() { echo "IDENTITY FAIL: $*" | tee -a "$OUT" >&2; exit 1; }
die() { echo "IDENTITY NOT RUN: $*" >&2; exit 1; }   # before anything is written (identity_check.txt untouched)

# --- idle_or_die: identical in build_b2e_scan.sh, run_b2e_identity.sh and run_b2e_rows.sh ---
# B2e never runs beside the network training, a build or another game run (spec section 4 "Time"), and the
# operator confirms the queue is idle before starting. This refuses if any of these is running:
#   - cargo, rustc, deckgym or any legality_scan* program, matched on the process NAME with pgrep -x (the name is
#     /proc/<pid>/comm, cut to 15 characters, so 'legality_scan.*' also catches legality_scan_b2e_7fc6ccb);
#   - the run-5 training: a process started as the run5-venv's python (its exact path as argv[0]: train_v5.py,
#     its workers, the audit and held-out steps), or any python* process with train_v5.py among its arguments.
# Nothing is matched against whole command lines (no pgrep -f), so this script's own command line, an editor or a
# grep that mentions these names cannot trigger it. WSL (Linux) processes only; checked once, at the start.
IDLE_NAMES=(cargo rustc 'deckgym.*' 'legality_scan.*')
IDLE_VENV="${RUN5_VENV:-$HOME/.cache/pocket-deck-lab/run5-venv}"
IDLE_TRAINER=train_v5.py
idle_or_die() {
  local busy=() name pids pid proc a argv
  for name in "${IDLE_NAMES[@]}"; do
    # pgrep exits 1 when nothing matches; any other failure (no pgrep, a bad pattern) must not read as "idle".
    pids=$(pgrep -x "$name") || [ $? -eq 1 ] || die "pgrep -x '$name' failed, so the laptop can't be checked as idle"
    for pid in $pids; do busy+=("$pid $(cat "/proc/$pid/comm" 2>/dev/null || echo "$name")"); done
  done
  for proc in /proc/[0-9]*; do
    argv=()
    { mapfile -t -d '' argv < "$proc/cmdline"; } 2>/dev/null || continue
    [ "${#argv[@]}" -gt 0 ] || continue
    case "${argv[0]}" in
      "$IDLE_VENV/bin/python" | "$IDLE_VENV/bin/python3" | "$IDLE_VENV/bin/python3."*)
        busy+=("${proc#/proc/} ${argv[0]}"); continue ;;
    esac
    case "${argv[0]##*/}" in
      python*)
        for a in "${argv[@]:1}"; do
          if [ "${a##*/}" = "$IDLE_TRAINER" ]; then busy+=("${proc#/proc/} ${argv[0]##*/} ... $a"); break; fi
        done ;;
    esac
  done
  [ "${#busy[@]}" -eq 0 ] || die "B2e never runs beside the training, a build or a game run; running now (pid, name): ${busy[*]}"
}
# --- end idle_or_die ---
idle_or_die

# The scans: niced, all cores but two (at least one: RAYON_NUM_THREADS=0 would mean every core). nproc is asked
# without the OMP_* variables, which would otherwise cap its answer.
THREADS=$(( $(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc) - 2 ))
[ "$THREADS" -ge 1 ] || THREADS=1
scan() { RAYON_NUM_THREADS=$THREADS nice -n 10 "$SCAN" "$@"; }

# compare.py on one replay; $1 label, $2 new file, $3 reference cut.
compare_ok() {
  local cmp_out="$B/compare_$1.txt" ok
  python3 "$COMPARE" "$2" "$3" > "$cmp_out" && ok=1 || ok=0
  cat "$cmp_out" >> "$OUT"
  [ "$ok" = 1 ] || fail "$1: the replay differs from the reference (compare.py above)"
  grep -q "^games in both: $N; identical on .*: $N of $N$" "$cmp_out" || fail "$1: compare.py did not report $N of $N"
  grep -q "^only in new: 0; only in reference: 0$" "$cmp_out" || fail "$1: compare.py reports games on one side only"
  grep -q "^RESULT: IDENTICAL$" "$cmp_out" || fail "$1: compare.py did not print RESULT: IDENTICAL"
}

# The scan must stop with this message before any game; $1 what, $2 the message, the rest the arguments.
refuses() {
  local what="$1" msg="$2"; shift 2
  if scan "$@" > "$B/guard.txt" 2>&1; then fail "the scan accepted $what"; fi
  grep -qF -e "$msg" "$B/guard.txt" || fail "the scan stopped on $what, but not with \"$msg\" ($B/guard.txt)"
  echo "refused, as it should: $what (\"$msg\")" >> "$OUT"
}

: > "$OUT"
[ -x "$SCAN" ] || fail "no binary at $SCAN (run build_b2e_scan.sh first)"
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ "$(head -n 1 "$D/identity.txt" | cut -d' ' -f1)" = "$SHA" ] || fail "binary sha256 $SHA is not the one build_b2e_scan.sh recorded in identity.txt"
echo "identity check of $SCAN, sha256 $SHA, started $(date -u +%FT%TZ)" >> "$OUT"
echo "pairings $PAIRINGS x $GAMES deals; k3 then kp3; (a) default flags, (b) --pairs mode, (c) --pairs guards; $THREADS threads of $(nproc) cores, nice 10" >> "$OUT"
{ echo "reference files (sha256):"; sha256sum "${REF_k3[@]}" "${REF_kp3[@]}" "${OFF_k3[@]}" "${OFF_kp3[@]}" "$COMPARE"; } >> "$OUT"

# The reference cuts, and the --pairs file for (b) and (c).
for bot in k3 kp3; do
  if [ "$bot" = k3 ]; then REF=("${REF_k3[@]}"); OFF=("${OFF_k3[@]}"); else REF=("${REF_kp3[@]}"); OFF=("${OFF_kp3[@]}"); fi
  python3 "$CHECKS" subset "$B/ref_$bot.jsonl" "$bot" "$PAIRINGS" "$GAMES" "${REF[@]}" >> "$OUT" \
    || fail "$bot: the table reference does not hold exactly pairings $PAIRINGS x $GAMES deals piloted by $bot"
  python3 "$CHECKS" subset "$B/off_$bot.jsonl" "$bot" "$PAIRINGS" "$GAMES" "${OFF[@]}" >> "$OUT" \
    || fail "$bot: the official scan's output does not hold exactly pairings $PAIRINGS x $GAMES deals piloted by $bot"
done
python3 "$CHECKS" table_tsv "$B/ref_k3.jsonl" "$TABLE_BASE" "$XT" >> "$OUT" || fail "could not write $XT"
cat "$XT" >> "$OUT"

cd "$B/engine"
# (c) the --pairs guards (nothing is played).
refuses "--pairs without --seed-base" "--pairs needs --seed-base" --pairs "$XT" --games 1 --bot k3
refuses "--pairs with --decks" "--pairs names its own deck files" --pairs "$XT" --seed-base "$TABLE_BASE" --decks ../decks/research --games 1 --bot k3
refuses "a seed_first that doesn't match --seed-base" "seed_first doesn't match --seed-base" --pairs "$XT" --seed-base "$((TABLE_BASE + 1))" --games 1 --bot k3
# These three fire before any file is read. The --games one gets a pairs file that doesn't exist, the other two
# one pairing and one deal, so even a missing guard plays at most one game.
refuses "--games above 10,000 with --pairs" "sub-block holds 10,000 seeds" --pairs "$B/no_such_pairs.tsv" --seed-base "$TABLE_BASE" --games 10001 --bot k3
refuses "--seed-base without --pairs" "--seed-base is only for --pairs" --seed-base "$TABLE_BASE" --games 1 --pairings 0 --bot k3
refuses "--root without --pairs" "--root is only for --pairs" --root .. --games 1 --pairings 0 --bot k3

for bot in k3 kp3; do
  { echo; echo "== $bot, (a) default flags"; } >> "$OUT"
  new="$D/identity_$bot.jsonl"
  s=$(date +%s)
  scan --games "$GAMES" --pairings "$PAIRINGS" --bot "$bot" --games-out "$new" > "$D/identity_$bot.txt" 2>&1 \
    || fail "the $bot replay exited non-zero (log identity_$bot.txt)"
  echo "identity_$bot $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
  python3 "$CHECKS" subset - "$bot" "$PAIRINGS" "$GAMES" "$new" >> "$OUT" \
    || fail "$bot: the new file is not exactly pairings $PAIRINGS x $GAMES deals piloted by $bot"
  compare_ok "$bot" "$new" "$B/ref_$bot.jsonl"
  python3 "$CHECKS" same "$new" "$B/off_$bot.jsonl" >> "$OUT" \
    || fail "$bot: default-flag lines are not byte-identical to the official 7fc6ccb scan's (b2e_checks.py same above)"

  { echo; echo "== $bot, (b) --pairs mode, --seed-base $TABLE_BASE"; } >> "$OUT"
  newp="$D/identity_pairs_$bot.jsonl"
  s=$(date +%s)
  scan --pairs "$XT" --seed-base "$TABLE_BASE" --games "$GAMES" --bot "$bot" --games-out "$newp" \
    > "$D/identity_pairs_$bot.txt" 2>&1 || fail "the $bot --pairs replay exited non-zero (log identity_pairs_$bot.txt)"
  echo "identity_pairs_$bot $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"
  python3 "$CHECKS" subset - "$bot" "$PAIRINGS" "$GAMES" "$newp" >> "$OUT" \
    || fail "$bot: the --pairs file is not exactly pairings $PAIRINGS x $GAMES deals piloted by $bot"
  compare_ok "pairs_$bot" "$newp" "$B/ref_$bot.jsonl"
  python3 "$CHECKS" same --drop a_file,b_file "$newp" "$B/off_$bot.jsonl" >> "$OUT" \
    || fail "$bot: --pairs lines differ from the official scan's once a_file and b_file are removed"
done
echo >> "$OUT"
echo "IDENTITY PASS $SHA: table pairings $PAIRINGS x $GAMES deals for k3 and kp3 ($N2 games): default flags identical to the table references on a, b, seed, first_seat, moves, winner_seat, points, turns, first_deck_score and byte for byte to the official 7fc6ccb scan's lines; --pairs mode with --seed-base $TABLE_BASE replays the same $N2 games; --pairs refuses a missing --seed-base, --decks, a mismatched seed_first and --games above 10,000; --seed-base and --root are refused without --pairs" >> "$OUT"
tail -n 1 "$OUT"
