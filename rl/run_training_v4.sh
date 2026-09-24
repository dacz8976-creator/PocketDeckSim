#!/usr/bin/env bash
# Run 4: one network per deck for the five-deck pool (Blaziken, Lucario, Weezing, Altaria, Suicune), encoding v2.2.
# Start, or resume after any interruption, with the same line in WSL Ubuntu:
#   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v4.sh"
# The one-deck pilot first (about an hour): just add --pilot, from any folder.
#   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_training_v4.sh" --pilot
# No time limit: it stops when every network levels off (a 6M-game cap guards against a broken run).
# Then, without anyone asking: the paired confirmations, the audit, the held-out test, and REPORT.txt.
# Expect roughly 12-16 hours, possibly more; it needs no one watching. Laptop plugged in, sleep off.
# Progress, in plain words: Boss Folder/rl-feasibility-2026-09-18/runs/<the run folder>/STATUS.txt
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
ROOT="/mnt/c/Users/dacz8/Projects/Pocket Deck Lab"
HERE="$ROOT/Boss Folder/rl-feasibility-2026-09-18"
WHL="$HERE/wheels/run4/pdl_rl_env-0.6.0-cp38-abi3-manylinux_2_34_x86_64.whl"   # encoding v2.2
VENV="$HOME/.cache/pocket-deck-lab/run4-venv"
RUN="${RUN:-}"   # another run folder can be given as RUN=runs/<name> (e.g. a continuation)
# --pilot reads the settings file beside this script, so the command works from any folder (Astra's P3)
ARGS=()
PILOT=0
for arg in "$@"; do
  if [ "$arg" = "--pilot" ]; then
    PILOT=1
    [ -f "$HERE/pilot_v4_settings.json" ] || { echo "MISSING $HERE/pilot_v4_settings.json"; exit 1; }
    ARGS+=(--override "$(cat "$HERE/pilot_v4_settings.json")")
  else
    ARGS+=("$arg")
  fi
done
if [ -z "$RUN" ]; then
  RUN="runs/pool5-v22-perdeck-01"
  if [ "$PILOT" = "1" ]; then RUN="runs/pilot-v22-blaziken"; fi
  for arg in "$@"; do [ "$arg" = "--smoke" ] && RUN="runs/smoke_v4_laptop"; done   # a practice run never touches the real folder
fi
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV" || { echo "SETUP FAILED (python3 -m venv)"; exit 1; }
fi
"$VENV/bin/python" -c "import numpy" 2>/dev/null || "$VENV/bin/python" -m pip install -q numpy || { echo "INSTALL FAILED (numpy)"; exit 1; }
"$VENV/bin/python" -m pip install -q --force-reinstall --no-deps "$WHL" || { echo "INSTALL FAILED"; exit 1; }
"$VENV/bin/python" -c "from pdl_rl_env import RawEnv; assert RawEnv([], 'v2.2').features == 'v2.2'" || { echo "WRONG ADD-ON"; exit 1; }
mkdir -p "$HERE/runs"
cd "$ROOT"
"$VENV/bin/python" "$HERE/train_v4.py" --run "$RUN" ${ARGS[@]+"${ARGS[@]}"} 2>&1 | tee -a "$HERE/$RUN.log"
STATE=$("$VENV/bin/python" -c "import json,sys; print(json.load(open(sys.argv[1]))['status'])" "$HERE/$RUN/state.json")
if [ "$STATE" = "PASSED" ] || [ "$STATE" = "FINISHED" ]; then
  echo "== Report steps: audit, held-out test, REPORT.txt (about 1-1.5 h; each step is skipped if already done)"
  # a step that stops (e.g. a deck file changed since the run) doesn't block the others; REPORT.txt lists what's missing
  "$VENV/bin/python" "$HERE/audit_v4.py" --run "$RUN" --workers 8 2>&1 | tee -a "$HERE/$RUN.log" \
    || echo "== The audit step stopped (message above); REPORT.txt will say so" | tee -a "$HERE/$RUN.log"
  "$VENV/bin/python" "$HERE/transfer_v4.py" --run "$RUN" --workers 8 2>&1 | tee -a "$HERE/$RUN.log" \
    || echo "== The held-out step stopped (message above); REPORT.txt will say so" | tee -a "$HERE/$RUN.log"
  "$VENV/bin/python" "$HERE/report_v4.py" --run "$RUN" 2>&1 | tee -a "$HERE/$RUN.log"
fi
