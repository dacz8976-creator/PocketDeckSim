#!/usr/bin/env bash
# The B2e rows (../b2e_card_check_2026-09-26/README.md section 4): all 96 pairings of b2e_pairings.tsv x 500 deals,
# k3 on both sides, then kp3 on both sides on the same deals, seeds 21,106,000,000 + pairing x 10,000 + i, even i =
# the held deck in seat 0. Section 4's four block files: each pilot runs twice, --pairings 0-47 (block A, the
# archetype lists) into b2e_<pilot>_arch.{jsonl,txt} and --pairings 48-95 (block B, Dustin's files) into
# b2e_<pilot>_dustin.{jsonl,txt}; same seeds and games as one 96-row run, since each game's seed depends only on its
# pairing and deal. Each games-out file is written as .jsonl.part and renamed only when its scan exits 0, so a
# .jsonl here is always a finished block. Runs only after run_b2e_identity.sh has written its IDENTITY PASS line for
# this very binary. Before the games: lib/deck_check.py on the twelve held files (the copies that are played). After
# them: b2e_checks.py rows (each block file exactly its block's 48 x 500 lines, seeds/seats/decks/pilots as the TSV,
# k3 and kp3 on the same deals, each file's per-game findings = its log's, one example per finding code).
# Never beside the network training, a build or another game run: idle_or_die (below) refuses to start while the
# run5-venv python (train_v5.py), cargo, rustc, deckgym or a legality_scan is running (checked once, at the start:
# start nothing else on the laptop until it ends); the scans run niced with RAYON_NUM_THREADS = cores - 2 (spec
# section 4 "Time"; Fable's review M4).
# Usage (in WSL):  bash run_b2e_rows.sh        Time: about 1.7 h per pilot at cloud speed, more on the laptop.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/b2e_rows_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
TSV=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
BASE=21106000000
GAMES=500
ARCH=$(seq -s, 0 47)     # block A_archetype: the six archetype lists
DUSTIN=$(seq -s, 48 95)  # block B_dustin: Dustin's six files
die() { echo "ROWS NOT RUN: $*" >&2; exit 1; }

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

# 0. Gates: the identity PASS for this binary; the played TSV = the repo's; the played copies = identity.txt's
#    hashes; the TSV's blocks are 0-47 and 48-95; no finished block file overwritten.
[ -x "$SCAN" ] || die "no binary at $SCAN"
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ -f "$D/identity_check.txt" ] || die "no identity_check.txt (run run_b2e_identity.sh first)"
[ "$(tail -n 1 "$D/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] \
  || die "identity_check.txt does not end in the IDENTITY PASS line for $SHA"
[ "$(head -n 1 "$D/identity.txt" | cut -d' ' -f1)" = "$SHA" ] || die "identity.txt names another binary"
cmp -s "$R/$TSV" "$B/$TSV" || die "the repo's $TSV changed since the build; rebuild or check it"
# The copies that are played (the TSV and its 20 deck files in $B) must still be the ones identity.txt records.
[ "$(wc -l < "$B/inputs_sha256.txt")" -eq 21 ] || die "$B/inputs_sha256.txt does not list the TSV and 20 deck files"
( cd "$B" && sha256sum --quiet -c inputs_sha256.txt ) || die "a played input in $B changed since the build"
while IFS= read -r line; do
  grep -qxF -e "$line" "$D/identity.txt" || die "identity.txt does not record: $line"
done < "$B/inputs_sha256.txt"
[ "$(awk -F'\t' 'NR > 1 && $2 == "A_archetype" {print $1}' "$B/$TSV" | paste -sd,)" = "$ARCH" ] \
  || die "the TSV's block A_archetype is not pairings 0-47 in order"
[ "$(awk -F'\t' 'NR > 1 && $2 == "B_dustin" {print $1}' "$B/$TSV" | paste -sd,)" = "$DUSTIN" ] \
  || die "the TSV's block B_dustin is not pairings 48-95 in order"
for bot in k3 kp3; do
  for block in arch dustin; do
    [ ! -e "$D/b2e_${bot}_$block.jsonl" ] || die "b2e_${bot}_$block.jsonl exists; move it away rather than overwrite it"
  done
done

# 1. The held files, as played.
mapfile -t HELD < <(tail -n +2 "$R/$TSV" | cut -f4 | awk '!seen[$0]++')
[ "${#HELD[@]}" -eq 12 ] || die "expected 12 held files in the TSV, found ${#HELD[@]}"
( cd "$B" && python3 "$R/lib/deck_check.py" files "${HELD[@]}" ) > "$D/deck_check.txt" 2>&1 \
  || die "deck_check failed on the held files (deck_check.txt)"

# 2. The rows: k3, then kp3, same deals; per pilot block A, then block B. A block's .jsonl appears only when its
#    scan exits 0 (written as .jsonl.part until then).
echo "scan binary $SHA" > "$D/rows_check.txt"
cd "$B/engine"
for bot in k3 kp3; do
  for block in arch dustin; do
    if [ "$block" = arch ]; then PAIRINGS=$ARCH; else PAIRINGS=$DUSTIN; fi
    out="$D/b2e_${bot}_$block"
    s=$(date +%s)
    scan --pairs "$B/$TSV" --seed-base "$BASE" --games "$GAMES" --bot "$bot" --pairings "$PAIRINGS" \
      --games-out "$out.jsonl.part" > "$out.txt" 2>&1 \
      || die "the $bot $block rows exited non-zero (b2e_${bot}_$block.txt; the games so far are in b2e_${bot}_$block.jsonl.part)"
    mv "$out.jsonl.part" "$out.jsonl"
    echo "b2e_${bot}_$block $(( $(date +%s) - s )) s wall ($THREADS threads of $(nproc) cores, nice 10, $(date -u +%FT%TZ) end)" >> "$D/timing.txt"
  done
done

# 3. The rows check.
python3 "$D/b2e_checks.py" rows "$R/$TSV" "$BASE" "$GAMES" "$D/b2e_k3_arch.jsonl" "$D/b2e_k3_dustin.jsonl" \
  "$D/b2e_kp3_arch.jsonl" "$D/b2e_kp3_dustin.jsonl" >> "$D/rows_check.txt" || { tail -n 1 "$D/rows_check.txt"; exit 1; }
tail -n 1 "$D/rows_check.txt"
