#!/usr/bin/env bash
# Build the B2e scan: legality_scan from main at 7fc6ccb (the official engine's commit) plus legality_scan_pairs.patch
# (--pairs, --seed-base, --root; engine/examples/legality_scan.rs only, the engine crate is not touched), in a
# scratch folder outside the repo, as the kd and kpr builds were (git archive, cargo build --release --example
# legality_scan). The tree also gets the B2e pairings file and the deck files it names that 7fc6ccb doesn't have
# (the six archetype lists), copied from the working copy after checking each equals its committed version; the
# deck files 7fc6ccb does have (panel, Dustin's, brew-08) must equal the working copy's, or the build stops.
# Stops loudly if the folder exists, if the patch touches anything else, or if it doesn't apply.
# Never beside the network training, another build or a game run: idle_or_die (below) refuses to start while the
# run5-venv python (train_v5.py), cargo, rustc, deckgym or a legality_scan is running, and the build itself is
# capped at 2 jobs (cargo -j 2) and niced (spec section 4 "Time"; Fable's review M4).
# Usage (in WSL):  bash build_b2e_scan.sh        Writes identity.txt beside this script.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/b2e_rows_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
C=7fc6ccb
F=engine/examples/legality_scan.rs
TSV=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
PATCH="$D/legality_scan_pairs.patch"
die() { echo "BUILD FAILED: $*" >&2; exit 1; }

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

if [ -e "$B" ]; then die "$B already exists; remove it (rm -rf $B) to build from scratch"; fi
[ -f "$PATCH" ] || die "no patch at $PATCH"
cd "$R"
git cat-file -e "$C^{commit}" || die "commit $C not found"

# 1. The source at 7fc6ccb.
mkdir -p "$B"
git rev-parse "$C" | sed "s/^/$C /" > "$B/COMMIT"
git archive "$C" engine decks | tar -x -C "$B"

# 2. The pairings file and the deck files it names.
git show "HEAD:$TSV" | cmp -s - "$TSV" || die "$TSV differs from its committed version"
mkdir -p "$B/$(dirname "$TSV")"
cp "$TSV" "$B/$TSV"
mapfile -t DECKS < <(tail -n +2 "$TSV" | cut -f4,6 | tr '\t' '\n' | sort -u)
[ "${#DECKS[@]}" -eq 20 ] || die "expected 20 distinct deck files in $TSV, found ${#DECKS[@]}"
for f in "${DECKS[@]}"; do
  if [ -e "$B/$f" ]; then
    cmp -s "$f" "$B/$f" || die "$f in the working copy differs from $C's"
  else
    git show "HEAD:$f" | cmp -s - "$f" || die "$f differs from its committed version (or isn't committed)"
    mkdir -p "$(dirname "$B/$f")"
    cp "$f" "$B/$f"
  fi
done
( cd "$B" && sha256sum "$TSV" "${DECKS[@]}" ) > "$B/inputs_sha256.txt"
for f in "${DECKS[@]}"; do
  if git cat-file -e "$C:$f" 2>/dev/null; then echo "$f  from $C"
  else echo "$f  from the working copy = $(git log -1 --format=%h -- "$f")'s version"; fi
done > "$B/inputs_source.txt"

# 3. The patch: engine/examples/legality_scan.rs only, applied to 7fc6ccb's file.
cd "$B"
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then die "$B is inside a git work tree; git apply would misplace paths"; fi
( cd "$R" && git show "$C:$F" ) | cmp -s - "$B/$F" || die "$B/$F is not $C's file"
TOUCHED=$(git apply --numstat "$PATCH" | awk '{print $3}')
[ "$TOUCHED" = "$F" ] || die "the patch must touch $F only; it touches: $TOUCHED"
git apply --check "$PATCH" || die "the patch does not apply to $C's $F"
git apply "$PATCH" || die "git apply failed"
echo "patch applied: $(git apply --numstat "$PATCH" | awk '{print "+"$1" -"$2" "$3}')"

# 4. Build (niced, 2 jobs; --locked keeps 7fc6ccb's Cargo.lock exactly).
cd "$B/engine"
if ! { time nice -n 10 cargo build --release --locked -j 2 --example legality_scan ; } > "$B/build.txt" 2>&1; then
  tail -n 30 "$B/build.txt" >&2
  die "cargo build failed (log: $B/build.txt)"
fi
cp target/release/examples/legality_scan "$B/legality_scan_b2e_$C"
SHA=$(sha256sum "$B/legality_scan_b2e_$C" | cut -d' ' -f1)

# 5. identity.txt (the first line is the binary; run_b2e_identity.sh and read_b2e.py read it).
{
  echo "$SHA  legality_scan_b2e_$C  ($B/legality_scan_b2e_$C)"
  echo
  echo "source: $(cat "$B/COMMIT") (main; the official engine's commit) + legality_scan_pairs.patch"
  echo "patch sha256: $(sha256sum "$PATCH" | cut -d' ' -f1)"
  echo "official deckgym (rl/engine-2026-09-25/deckgym; not used to play B2e games): $(sha256sum "$R/rl/engine-2026-09-25/deckgym" | cut -d' ' -f1)"
  echo "official legality_scan (unpatched, same commit): $(sha256sum "$R/rl/engine-2026-09-25/legality_scan" | cut -d' ' -f1)"
  echo "built $(date -u +%FT%TZ) with $(cargo --version), $(rustc --version)"
  echo
  echo "inputs (sha256, path relative to the repo root; the copies in $B are the ones played):"
  cat "$B/inputs_sha256.txt"
  echo
  cat "$B/inputs_source.txt"
} > "$D/identity.txt"
echo "built $B/legality_scan_b2e_$C  sha256 $SHA"
