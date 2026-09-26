#!/usr/bin/env bash
# Gauntlet run (a): the new decks against the 8 panel lists, plus Rayquaza v Altaria/Greninja.
# tsv/new_decks_run.tsv: the pairings of tsv/new_decks.tsv (25) minus any deck in tsv/not_run.json (a list with a
# card that is wrong in a way that changes play is not run; its pairing numbers and seeds stay reserved, so nothing
# shifts), x 500 deals, k3 on both sides, then kp3 on both sides on the same deals (as B2e).
# Seeds 21,108,000,000 + 10,000 x pairing + i, i < 500 (at most up to 21,108,240,499); even i = the new deck in seat 0.
# Pairings 0-7 Mega Scizor ex Revavroom (a COVERAGE row, never in an accuracy total); 8-15 Dragonair Mega Rayquaza
# ex and 16-23 Mega Altaria ex Greninja (SCOREBOARD rows); 24 Rayquaza v Altaria/Greninja (the 17th new cell).
# Pre-repair engine (the official 7fc6ccb, played by the B2e scan): re-run at the repaired engine when it becomes
# the baseline.
# Files written here: new_k3.{jsonl,txt}, new_kp3.{jsonl,txt} (a .jsonl appears only when its scan exits 0; it is
# .jsonl.part until then), timing_new.txt, deck_check_new.txt, rows_check_new.txt, and STATUS_new.txt, whose last line
# is "RUN DONE ..." (anchored at the start of the line) when everything passed, or "RUN FAILED: ..." otherwise.
# A refusal before the start (laptop busy, a gate) writes nothing, so the run can simply be launched again later.
# Gates: the B2e scan binary that passed B2e's identity check and this folder's identity/identity_check.txt; the
# staged inputs unchanged (inputs_sha256.txt, and each equal to the working copy); no finished output overwritten.
# Never beside the network training, a build or another game run: B2e's idle_or_die (below, unchanged) refuses to
# start while cargo, rustc, deckgym, a legality_scan or the run-5 training runs; checked once, at the start. The
# scans run niced (10) with RAYON_NUM_THREADS = cores - 2. Time: B2e's 48 pairings x 500 took about 20 min per pilot
# on this laptop with 14 threads, so about 7 to 13 min per pilot here, under half an hour in all.
# Usage (WSL): bash run_gauntlet_new.sh
# Dry run of the whole flow (tests only; used once on Sept 26): GAUNTLET_DRY_RUN=1 GAUNTLET_OUT=<scratch folder>
# GAUNTLET_GAMES=2 bash run_gauntlet_new.sh. It writes into <scratch folder> only (never this folder), plays at most 20
# deals, skips the idle check and runs at nice 19 with 2 threads.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/gauntlet_runs_2026-09-26"
O="${GAUNTLET_OUT:-$D}"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
TSV=rl/results/gauntlet_runs_2026-09-26/tsv/new_decks_run.tsv
BASE=21108000000
GAMES="${GAUNTLET_GAMES:-500}"
DRY="${GAUNTLET_DRY_RUN:-}"
STATUS="$O/STATUS_new.txt"
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
grep -q "  $TSV\$" "$D/inputs_sha256.txt" || die "$TSV is not among the staged inputs (run stage_inputs.sh)"
for bot in k3 kp3; do
  [ ! -e "$O/new_$bot.jsonl" ] || die "new_$bot.jsonl exists; move it away rather than overwrite it"
done
NP=$(( $(wc -l < "$B/$TSV") - 1 ))

# Started: from here on a failure is written to STATUS as "RUN FAILED: ...".
die() { echo "RUN FAILED: $* ($(date -u +%FT%TZ))" >> "$STATUS"; echo "RUN FAILED: $*" >&2; exit 1; }
trap 'die "stopped at line $LINENO (exit $?)"' ERR
note "START run (a) new decks${DRY:+ (DRY RUN)}: $TSV, $NP pairings x $GAMES, k3 then kp3, seed base $BASE; not run: $(tr -d '\n' < "$D/tsv/not_run.json"); pre-repair engine (7fc6ccb); re-run at the repaired engine when it becomes the baseline"
note "gates passed: scan $SHA; $(wc -l < "$D/inputs_sha256.txt") staged inputs unchanged; $PRIORITY"

# The new decks, as played.
( cd "$B" && python3 "$R/lib/deck_check.py" files decks/gauntlet_2026-09-26/g-*.txt ) > "$O/deck_check_new.txt" 2>&1 \
  || die "deck_check failed on the played new-deck copies (deck_check_new.txt)"

cd "$B/engine"
for bot in k3 kp3; do
  out="$O/new_$bot"
  note "$bot START"
  s=$(date +%s)
  scan --pairs "$B/$TSV" --seed-base "$BASE" --games "$GAMES" --bot "$bot" --games-out "$out.jsonl.part" \
    > "$out.txt" 2>&1 || die "the $bot scan exited non-zero (new_$bot.txt; games so far in new_$bot.jsonl.part)"
  mv "$out.jsonl.part" "$out.jsonl"
  echo "new_$bot $(( $(date +%s) - s )) s wall ($PRIORITY, $(date -u +%FT%TZ) end)" >> "$O/timing_new.txt"
  note "$bot DONE in $(( $(date +%s) - s )) s"
done

python3 "$D/gauntlet_checks.py" rows "$D/tsv/new_decks_run.tsv" "$BASE" "$GAMES" k3 "$O/new_k3.jsonl" \
  "$D/tsv/new_decks_run.tsv" "$BASE" "$GAMES" kp3 "$O/new_kp3.jsonl" > "$O/rows_check_new.txt" \
  || die "rows check failed (rows_check_new.txt)"
note "$(tail -n 1 "$O/rows_check_new.txt")"
echo "RUN DONE $(date -u +%FT%TZ) run (a)${DRY:+ (DRY RUN)}: new_k3.jsonl and new_kp3.jsonl, $NP pairings x $GAMES deals each, rows check PASS; next: python3 read_gauntlet.py" >> "$STATUS"
tail -n 1 "$STATUS"
