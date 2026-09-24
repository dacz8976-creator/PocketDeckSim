#!/usr/bin/env bash
# Run 5 (RUN5.md): step 0 (run 4's pilot on rules4 + add-on 0.7.2) or stage 1 (Weezing vs Lucario, plus an
# averaged copy of each network). In WSL Ubuntu, from the repo folder:
#   bash rl/run_training_v5.sh --step0
#   bash rl/run_training_v5.sh --stage1
# The Hydreigon run (RUN5.md plan item 2) is a practice-rule run with its own settings:
#   RUN=runs/diag-hydreigon-lucario SETTINGS_FILE=rl/diag_hydreigon_v5_settings.json bash rl/run_training_v5.sh --stage1
# The same line again resumes after any interruption. After training, without anyone asking: the paired
# confirmations, the knockout audit, the held-out test (step 0 only) and REPORT.txt.
# Step 0: about 1.2 h. Stage 1: at most about 8 h of training plus evaluation (it can stop earlier).
# Laptop plugged in, sleep off. Progress in plain words: runs/<run folder>/STATUS.txt beside this script.
#
# Practice runs (testing the program, not the bot) need a new folder and a small settings file:
#   RUN=runs/practice-<name> SETTINGS_FILE=<file.json> bash run_training_v5.sh --stage1 --workers 2
# Any other run folder, settings file or test option makes it a practice run. A practice run is refused in the
# real run folders, and its settings must give their own "seeds", every base at 9,000,000,000 or above (the
# practice block), so practice never uses a real run's seeds (Astra, Sept 23).
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # works from any folder
ROOT="$(cd "$HERE/.." && pwd)"   # the repo root
ADDON="$HERE/addon-0.7.2"   # the wheel goes in wheels/ here; README.md lists its SHA-256
WHL="$ADDON/wheels/pdl_rl_env-0.7.2-cp38-abi3-linux_x86_64.whl"
WHL_SHA="56ca0bad21a569b852da3c82c321f6ab3f08b162e8019d0cf5871c82636c925b"   # add-on README
SO_SHA="0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101"    # add-on README: installed library
VENV="${RUN5_VENV:-$HOME/.cache/pocket-deck-lab/run5-venv}"

MODE=""
ARGS=()
PRACTICE_ARG=0
NEED=""   # the option waiting for its number
# Only these reach the trainer: --workers N, --smoke, --stop-after N. The run folder and the settings are the
# launcher's own choice, so --run, --override and any other option (including the trainer's accepted
# abbreviations, like --ov or --ru) are refused (Astra, Sept 23).
for arg in "$@"; do
  if [ -n "$NEED" ]; then
    [[ "$arg" =~ ^[0-9]+$ ]] || { echo "REFUSED: $NEED needs a whole number, got '$arg'"; exit 2; }
    ARGS+=("$arg"); NEED=""; continue
  fi
  case "$arg" in
    --step0) MODE=step0 ;;
    --stage1) MODE=stage1 ;;
    --workers) ARGS+=("$arg"); NEED=--workers ;;
    --smoke) PRACTICE_ARG=1; ARGS+=("$arg") ;;
    --stop-after) PRACTICE_ARG=1; ARGS+=("$arg"); NEED=--stop-after ;;
    *)
      if [[ "$arg" =~ ^--workers=[0-9]+$ ]]; then ARGS+=("$arg")
      elif [[ "$arg" =~ ^--stop-after=[0-9]+$ ]]; then PRACTICE_ARG=1; ARGS+=("$arg")
      else
        echo "REFUSED: '$arg' isn't passed on. The launcher accepts --step0 or --stage1, plus --workers N, --smoke"
        echo "and --stop-after N. For a practice run, set RUN=runs/practice-<name> and SETTINGS_FILE=<file.json>."
        exit 2
      fi ;;
  esac
done
[ -z "$NEED" ] || { echo "REFUSED: $NEED needs a whole number after it"; exit 2; }
if [ -z "$MODE" ]; then echo "Say which: --step0 or --stage1"; exit 2; fi
if [ "$MODE" = step0 ]; then
  DEFAULT_SETTINGS="$HERE/pilot_v4_settings.json"; REAL_RUN="runs/run5-step0-blaziken-lucario"
else
  DEFAULT_SETTINGS="$HERE/stage1_v5_settings.json"; REAL_RUN="runs/run5-stage1-weezing-lucario"
fi
# The settings file is resolved ONCE, from the caller's folder, and read ONCE below; that same text is what gets
# checked and what the trainer receives (Astra, Sept 23: a relative name was checked in the caller's folder but
# read again from the project folder).
DEFAULT_SETTINGS=$(realpath -m -- "$DEFAULT_SETTINGS")
SETTINGS=$(realpath -m -- "${SETTINGS_FILE:-$DEFAULT_SETTINGS}")
RUN="${RUN:-$REAL_RUN}"
# The run folder as the trainer will see it (a relative RUN is taken from this script's folder), fully resolved,
# so another spelling of a real folder (trailing slash, absolute path, "./", "..") is still recognised.
resolve() { case "$1" in /*) realpath -m -- "$1" ;; *) realpath -m -- "$HERE/$1" ;; esac; }
RUN_ABS=$(resolve "$RUN")
REAL_ABS=$(resolve "$REAL_RUN")
REAL_STEP0=$(resolve "runs/run5-step0-blaziken-lucario")
REAL_STAGE1=$(resolve "runs/run5-stage1-weezing-lucario")
PRACTICE=0
# anything other than the standard folder with the standard settings and no test options is a practice run
if [ "$SETTINGS" != "$DEFAULT_SETTINGS" ] || [ "$PRACTICE_ARG" = 1 ] || [ "$RUN" != "$REAL_RUN" ]; then
  PRACTICE=1
  if [ "$RUN_ABS" = "$REAL_STEP0" ] || [ "$RUN_ABS" = "$REAL_STAGE1" ]; then
    echo "REFUSED: $RUN is a real run folder; a practice run needs RUN=runs/practice-<name>"; exit 1
  fi
fi
[ "$PRACTICE" = 1 ] || [ "$RUN_ABS" = "$REAL_ABS" ] || { echo "REFUSED: run folder check failed ($RUN_ABS)"; exit 1; }
[ -f "$SETTINGS" ] || { echo "MISSING $SETTINGS"; exit 1; }
SETTINGS_TEXT="$(cat "$SETTINGS")"
if [ "$PRACTICE" = 1 ]; then
  PDL_SETTINGS_TEXT="$SETTINGS_TEXT" python3 - <<'PYEOF' || { echo "REFUSED: practice settings must give their own \"seeds\" (train, k3, random, confirm, transfer), every base at 9,000,000,000 or above"; exit 1; }
import json, os, sys
seeds = json.loads(os.environ["PDL_SETTINGS_TEXT"]).get("seeds")
need = {"train", "k3", "random", "confirm", "transfer"}
sys.exit(0 if isinstance(seeds, dict) and need <= set(seeds) and all(v >= 9_000_000_000 for v in seeds.values()) else 1)
PYEOF
fi

# Every deck the run will load goes through the legality check first: the add-on loads decks with
# Deck::from_file and skips the check the command-line tool runs (Dustin, Sept 24).
RUN_DECKS=$(PDL_SETTINGS_TEXT="$SETTINGS_TEXT" python3 - <<'PYEOF'
import json, os
s = json.loads(os.environ["PDL_SETTINGS_TEXT"])
decks = list((s.get("pool") or {}).values()) + list((s.get("held_out") or {}).values())
print("\n".join(decks))
PYEOF
)
[ -n "$RUN_DECKS" ] || { echo "REFUSED: the settings name no decks (\"pool\"), so they can't be checked"; exit 1; }
DECK_PATHS=()
while IFS= read -r d; do case "$d" in /*) DECK_PATHS+=("$d") ;; *) DECK_PATHS+=("$ROOT/$d") ;; esac; done <<< "$RUN_DECKS"
python3 "$ROOT/lib/deck_check.py" files "${DECK_PATHS[@]}" || { echo "REFUSED: a deck failed lib/deck_check.py (above)"; exit 1; }

# the add-on: exactly the 0.7.2 wheel the add-on README names, or nothing
[ -f "$WHL" ] || { echo "MISSING $WHL"; exit 1; }
grep -q "$WHL_SHA" "$ADDON/README.md" || { echo "REFUSED: the add-on README does not list $WHL_SHA"; exit 1; }
GOT=$(sha256sum "$WHL" | cut -d' ' -f1)
[ "$GOT" = "$WHL_SHA" ] || { echo "REFUSED: wheel SHA-256 is $GOT, the add-on README says $WHL_SHA"; exit 1; }
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV" || { echo "SETUP FAILED (python3 -m venv)"; exit 1; }
fi
PY="$VENV/bin/python"
"$PY" -c "import numpy" 2>/dev/null || "$PY" -m pip install -q numpy || { echo "INSTALL FAILED (numpy)"; exit 1; }
"$PY" -m pip install -q --force-reinstall --no-deps "$WHL" || { echo "INSTALL FAILED (add-on wheel)"; exit 1; }
"$PY" - "$SO_SHA" <<'EOF' || { echo "WRONG ADD-ON (see the line above)"; exit 1; }
import hashlib, importlib.metadata, importlib.util, sys
from pdl_rl_env import RawEnv
so = importlib.util.find_spec("pdl_rl_env").origin
got = hashlib.sha256(open(so, "rb").read()).hexdigest()
ver = importlib.metadata.version("pdl_rl_env")
assert ver == "0.7.2", f"add-on version {ver}, expected 0.7.2"
assert got == sys.argv[1], f"installed library {so} has SHA-256 {got}, expected {sys.argv[1]}"
assert RawEnv([], "v2.2").features == "v2.2", "encoding v2.2 did not load"
print(f"add-on 0.7.2 OK: {so} {got[:12]}..., encoding v2.2 loads")
EOF

mkdir -p "$HERE/runs"
cd "$ROOT"
LOG="$HERE/$RUN.log"
mkdir -p "$(dirname "$LOG")"
"$PY" "$HERE/train_v5.py" --run "$RUN" --override "$SETTINGS_TEXT" ${ARGS[@]+"${ARGS[@]}"} 2>&1 | tee -a "$LOG"
STATE=$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1]))['status'])" "$HERE/$RUN/state.json")
if [ "$STATE" = "PASSED" ] || [ "$STATE" = "FINISHED" ]; then
  echo "== Report steps: audit, held-out test, REPORT.txt (each step is skipped if already done)" | tee -a "$LOG"
  # a step that stops doesn't block the others; REPORT.txt lists what's missing. pipefail makes the || fire.
  "$PY" "$HERE/audit_v5.py" --run "$RUN" --workers 8 2>&1 | tee -a "$LOG" \
    || echo "== The audit step stopped (message above); REPORT.txt will say so" | tee -a "$LOG"
  "$PY" "$HERE/transfer_v5.py" --run "$RUN" --workers 8 2>&1 | tee -a "$LOG" \
    || echo "== The held-out step stopped (message above); REPORT.txt will say so" | tee -a "$LOG"
  "$PY" "$HERE/report_v5.py" --run "$RUN" 2>&1 | tee -a "$LOG"
  if [ "$MODE" = step0 ]; then
    NOTE="RUN5.md step 0 rule: GO if Blaziken's confirmed margin is +5 or better; below +5, find out why before stage 1. (The PASS / not-a-pass line above is run 4's own +10 rule from the unchanged pilot settings.)"
    printf '\n%s\n' "$NOTE" >> "$HERE/$RUN/REPORT.txt"
    echo "$NOTE" | tee -a "$LOG"
  fi
else
  echo "== The run ended as $STATE; no report steps. See $HERE/$RUN/STATUS.txt" | tee -a "$LOG"
fi
