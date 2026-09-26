#!/usr/bin/env bash
# Gauntlet run (b): the variation check (Proposal B of ../gauntlet_proposal_2026-09-26/README.md, section 6), kp3 only.
# 12 versions (a second list and two single-card Trainer swaps for each of Lucario, Suicune, Weezing and Charizard Y),
# each on the SAME deals as its deck's main list, so the comparison is paired:
#   - Lucario, Suicune, Weezing: the table's own deals, seed 72,000,000 + table pairing x 10,000 + i, the table's
#     pairing numbers and seats (the table's first-named deck held); 7 pairings per version.
#   - Charizard Y: B2e's deals, seed 21,106,000,000 + pairing x 10,000 + i, pairings 40-47, the version held;
#     8 pairings per version.
# 87 pairings x 500 deals = 43,500 games. No new seeds are used: every deal is one the main list already played.
# Pre-repair engine (the official 7fc6ccb, played by the B2e scan): re-run at the repaired engine when it becomes
# the baseline.
# Files written here: var_<version>_kp3.{jsonl,txt} (a .jsonl appears only when its scan exits 0; .jsonl.part until
# then), timing_variation.txt, deck_check_variation.txt, rows_check_variation.txt, and STATUS_variation.txt, whose last
# line is "RUN DONE ..." (anchored at the start of the line) when everything passed, or "RUN FAILED: ..." otherwise.
# A refusal before the start (laptop busy, a gate) writes nothing, so the run can simply be launched again later.
# Gates, idle check and priority as run_gauntlet_new.sh (B2e's idle_or_die unchanged; nice 10; RAYON_NUM_THREADS =
# cores - 2). Time: about 0.06 s of wall time per game with 14 threads (B2e's kp3 blocks), so roughly 45 min.
# Usage (WSL): bash run_gauntlet_variation.sh
# Dry run of the whole flow (tests only; used once on Sept 26): GAUNTLET_DRY_RUN=1 GAUNTLET_OUT=<scratch folder>
# GAUNTLET_GAMES=2 bash run_gauntlet_variation.sh (writes only there, at most 20 deals, no idle check, nice 19, 2 threads).
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/gauntlet_runs_2026-09-26"
O="${GAUNTLET_OUT:-$D}"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
T=rl/results/gauntlet_runs_2026-09-26/tsv
GAMES="${GAUNTLET_GAMES:-500}"
DRY="${GAUNTLET_DRY_RUN:-}"
VERSIONS=(v-lucario_2 v-lucario_swap1 v-lucario_swap2 v-suicune_2 v-suicune_swap1 v-suicune_swap2
          v-weezing_2 v-weezing_swap1 v-weezing_swap2 l-charizardy v-charizardy_swap1 v-charizardy_swap2)
base_of() { if [[ "$1" == *charizardy* ]]; then echo 21106000000; else echo 72000000; fi; }
STATUS="$O/STATUS_variation.txt"
note() { echo "$(date -u +%FT%TZ) $*" >> "$STATUS"; }
die() { echo "RUN NOT STARTED: $*" >&2; exit 1; }

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

if [ -n "$DRY" ]; then
  [ "$(realpath -m "$O")" != "$(realpath -m "$D")" ] || die "a dry run must write to its own GAUNTLET_OUT, not $D"
  [ "$GAMES" -le 20 ] || die "a dry run plays at most 20 deals per pairing"
  mkdir -p "$O"
  THREADS=2; NICE=19; PRIORITY="DRY RUN, idle check skipped, nice 19, 2 threads"
else
  [ "$GAMES" -eq 500 ] || die "the real run plays 500 deals (GAUNTLET_GAMES is for dry runs)"
  [ "$O" = "$D" ] || die "the real run writes to $D (GAUNTLET_OUT is for dry runs)"
  THREADS=$(( $(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc) - 2 ))
  [ "$THREADS" -ge 1 ] || THREADS=1
  NICE=10; PRIORITY="laptop idle; $THREADS threads of $(nproc) cores, nice 10"
fi
[ ! -e "$STATUS" ] || die "$STATUS exists (a run was started before); move it away first"
[ -n "$DRY" ] || idle_or_die
scan() { RAYON_NUM_THREADS=$THREADS nice -n "$NICE" "$SCAN" "$@"; }

# Gates.
[ -x "$SCAN" ] || die "no binary at $SCAN"
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ "$(tail -n 1 "$R/rl/results/b2e_rows_2026-09-26/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] \
  || die "B2e's identity_check.txt does not end in the IDENTITY PASS line for $SHA"
[ "$(tail -n 1 "$D/identity/identity_check.txt" | cut -d' ' -f1-4)" = "GAUNTLET IDENTITY PASS $SHA:" ] \
  || die "identity/identity_check.txt does not end in the GAUNTLET IDENTITY PASS line for $SHA"
( cd "$B" && sha256sum --quiet -c "$D/inputs_sha256.txt" ) || die "a staged input in $B changed since stage_inputs.sh"
while read -r _ f; do cmp -s "$R/$f" "$B/$f" || die "$f: the working copy differs from the staged copy"; done < "$D/inputs_sha256.txt"
for v in "${VERSIONS[@]}"; do
  grep -q "  $T/var_$v.tsv\$" "$D/inputs_sha256.txt" || die "$T/var_$v.tsv is not among the staged inputs"
  [ ! -e "$O/var_${v}_kp3.jsonl" ] || die "var_${v}_kp3.jsonl exists; move it away rather than overwrite it"
done

# Started: from here on a failure is written to STATUS as "RUN FAILED: ...".
die() { echo "RUN FAILED: $* ($(date -u +%FT%TZ))" >> "$STATUS"; echo "RUN FAILED: $*" >&2; exit 1; }
trap 'die "stopped at line $LINENO (exit $?)"' ERR
note "START run (b) variation check${DRY:+ (DRY RUN)}: ${#VERSIONS[@]} versions, 87 pairings x $GAMES, kp3, on the main lists' own deals; pre-repair engine (7fc6ccb); re-run at the repaired engine when it becomes the baseline"
note "gates passed: scan $SHA; $(wc -l < "$D/inputs_sha256.txt") staged inputs unchanged; $PRIORITY"

# The versions' lists, as played.
( cd "$B" && python3 "$R/lib/deck_check.py" files decks/gauntlet_2026-09-26/v-*.txt \
    decks/screen/panel_ladder_2026-09-26/l-charizardy.txt ) > "$O/deck_check_variation.txt" 2>&1 \
  || die "deck_check failed on the played version copies (deck_check_variation.txt)"

cd "$B/engine"
ROWS=()
for v in "${VERSIONS[@]}"; do
  base=$(base_of "$v")
  out="$O/var_${v}_kp3"
  note "$v START (seed base $base)"
  s=$(date +%s)
  scan --pairs "$B/$T/var_$v.tsv" --seed-base "$base" --games "$GAMES" --bot kp3 --games-out "$out.jsonl.part" \
    > "$out.txt" 2>&1 || die "the $v scan exited non-zero (var_${v}_kp3.txt; games so far in its .jsonl.part)"
  mv "$out.jsonl.part" "$out.jsonl"
  echo "var_${v}_kp3 $(( $(date +%s) - s )) s wall ($PRIORITY, $(date -u +%FT%TZ) end)" >> "$O/timing_variation.txt"
  note "$v DONE in $(( $(date +%s) - s )) s"
  ROWS+=("$D/tsv/var_$v.tsv" "$base" "$GAMES" kp3 "$out.jsonl")
done

python3 "$D/gauntlet_checks.py" rows "${ROWS[@]}" > "$O/rows_check_variation.txt" || die "rows check failed (rows_check_variation.txt)"
note "$(tail -n 1 "$O/rows_check_variation.txt")"
echo "RUN DONE $(date -u +%FT%TZ) run (b)${DRY:+ (DRY RUN)}: 12 versions, 87 pairings x $GAMES deals, kp3, rows check PASS; next: python3 read_gauntlet.py" >> "$STATUS"
tail -n 1 "$STATUS"
