#!/usr/bin/env bash
# The Altaria detector network's pair checks (PRESET_READING.md: they must pass before anything is read), the
# Hydreigon run's checks with only the decks, the seeds (Claude Code's 21,101,000,000 block) and the rules4 identity
# lookup changed. Run before training, so a failed interface check costs minutes, not the run.
# Usage: run_checks.sh   (from anywhere in WSL; needs the run5 venv with add-on 0.7.2, which the launcher installs)
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
PY="${RUN5_VENV:-$HOME/.cache/pocket-deck-lab/run5-venv}/bin/python"
"$PY" "$D/paired_interface_checks.py" --output "$D/interface-full" > "$D/interface-full.log" 2>&1
"$PY" "$D/v22_checks.py" --output "$D/v22-full" > "$D/v22-full.log" 2>&1
"$PY" "$D/cli_addon_parity.py" --engine rl/addon-0.7.2/deckgym \
  --engine-sha256 e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415 --engine-version 0.1.0-pdl.rules4 \
  --addon-sha256 0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101 --addon-version 0.7.2 \
  --output "$D/parity-full" > "$D/parity-full.log" 2>&1
python3 "$D/readout.py" "$D/interface-full" "$D/v22-full" "$D/parity-full" | tee "$D/READOUT.txt"
