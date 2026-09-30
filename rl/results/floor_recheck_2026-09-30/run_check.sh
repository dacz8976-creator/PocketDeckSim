#!/usr/bin/env bash
# The floor's Payback pre-use check under km3 on the Sept 30 engine (PLAN.md). Run from anywhere in WSL; writes here.
# The same calls as ../floor_recheck_2026-09-28/run_check.sh; the pilots are floor.py's and run_screen.py's defaults
# (km3 since the Sept 30 pin), except the k3 control. Then check_verdicts.py writes verdicts.txt.
set -euo pipefail
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
python3 - <<'EOF' || exit 1
import json, sys
sys.path.insert(0, "decks/screen/panel_ladder_2026-09-26")
import calibrate
rel = json.load(open("project_manifest.json", encoding="utf-8"))["available_release"]
if rel["artifact"] != "rl/engine-2026-09-30/deckgym":
    sys.exit(f"the manifest names {rel['artifact']}, not the Sept 30 engine")
pilot, where = calibrate.working_pilot()
if pilot != "km3":
    sys.exit(f"the screen and the floor default to {pilot}, not km3: {where}")
print(f"engine {rel['name']} ({rel['artifact']}); screen and floor default km3")
EOF
for f in PLAN.md run_check.sh check_verdicts.py; do
  git ls-files --error-unmatch -- "$D/$f" > /dev/null 2>&1 || { echo "$f is not committed: the plan comes before any game"; exit 1; }
done
git diff --quiet HEAD -- "$D/PLAN.md" "$D/run_check.sh" "$D/check_verdicts.py" || { echo "the plan or runner differs from its commit"; exit 1; }
ls "$D" | grep -qE '_games\.jsonl$|_coverage\.json$|^timing\.txt$|^run_screen\.txt$|^verdicts\.txt$' && { echo "games or pages from an earlier run are here; move them aside first"; exit 1; }
[ ! -e "$D/control_k3" ] || { echo "control_k3/ from an earlier run is here; move it aside first"; exit 1; }
F="python3 decks/screen/floor.py"
t() { local tag=$1; shift; local s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }
t brew-06 $F decks/brews/brew-06-pyukumuku-silvally-payback.txt --out "$D"
t brew-06b $F decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt --out "$D"
t control-14-k3 $F decks/dustin/14-comfey-raticate-hypno.txt --out "$D/control_k3" --pilot k3 --meta-pilot k3
t brew-05b $F decks/brews/brew-05b-meowstic-hatterene-comfey.txt --out "$D"
t deck-07 $F decks/dustin/07-skarmory-stall.txt --out "$D"
t run_screen python3 decks/screen/run_screen.py decks/brews/brew-06-pyukumuku-silvally-payback.txt \
  decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt --games 240 > "$D/run_screen.txt" 2>&1
echo "$(date -u +%F\ %T) FLOOR RECHECK DONE" >> "$D/timing.txt"
python3 "$D/check_verdicts.py"
