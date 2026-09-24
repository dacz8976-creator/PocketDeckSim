#!/usr/bin/env bash
# Write readable game transcripts for a training checkpoint. Run inside WSL Ubuntu:
#   bash "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/run_transcripts.sh"
#   (latest checkpoint; add --ckpt ckpt_500k for another one)
# Uses its own Python setup (transcript-venv) and its own add-on build (wheels/transcripts/),
# so the training run's setup is never touched. Light work; safe while training runs.
# Output: runs/brew03a-01/transcripts/<checkpoint>/INDEX.txt plus one text file per game.
ROOT="/mnt/c/Users/dacz8/Projects/Pocket Deck Lab"
HERE="$ROOT/Boss Folder/rl-feasibility-2026-09-18"
WHL="$HERE/wheels/transcripts/pdl_rl_env-0.3.0-cp38-abi3-manylinux_2_34_x86_64.whl"
VENV="$HOME/.cache/pocket-deck-lab/transcript-venv"
if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV" || { echo "SETUP FAILED (python3 -m venv)"; exit 1; }
fi
"$VENV/bin/python" -m pip install -q --force-reinstall --no-deps "$WHL" || { echo "INSTALL FAILED"; exit 1; }
"$VENV/bin/python" -c "import numpy" 2>/dev/null || "$VENV/bin/python" -m pip install -q numpy || { echo "INSTALL FAILED (numpy)"; exit 1; }
cd "$ROOT" && "$VENV/bin/python" "$HERE/transcripts.py" --run runs/brew03a-01 "$@"
