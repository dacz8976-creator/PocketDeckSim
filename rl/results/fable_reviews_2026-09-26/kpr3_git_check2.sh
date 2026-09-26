#!/usr/bin/env bash
# Follow-up read-only checks on the cloud branch.
set -u
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REF="origin/claude/pensive-ptolemy-spwc0b"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/75cb92d0-6f2d-44b8-a636-513a8f7ee71a/scratchpad/reviews"
cd "$REPO" || exit 1

echo "=== the two 'limits' e09fb46 says were 'written into the kpr README': present in the review JSON (df46e0a, pre-table)? ==="
git show "$REF:rl/results/kpr_2026-09-25/review_1981bb4_workflow_output.json" > "$OUT/branch/review_1981bb4_workflow_output.json"
for pat in 'promotion' 'pending' 'self-knockout' 'remaining_hp' 'HP now' 'Bad Dreams' 'Deceptive Needle' 'burn'; do
  echo "  '$pat': $(grep -o -i "$pat" "$OUT/branch/review_1981bb4_workflow_output.json" | wc -l) hits"
done
echo
echo "=== any file on the branch at e09fb46 (pre-table) that records the kpr spec or its limits, outside commit messages? ==="
git grep -l -i -E 'projected readiness|projected_active_energy|kpr' e09fb46 -- rl docs rules 2>/dev/null
echo "--- lines in rl/ and docs/ at e09fb46 mentioning kpr (first 30) ---"
git grep -n -i -E '\bkpr' e09fb46 -- rl docs 2>/dev/null | grep -v -E 'kpr_2026-09-25/(identity|mutate|mutation|run_|review_|timing)' | cut -c1-200 | head -30
echo
echo "=== the kd README at e09fb46: what does it say kpr's registration should carry? ==="
git show e09fb46:rl/results/kd_2026-09-25/README.md 2>/dev/null | grep -n -i -E 'kpr|footprint|census' | cut -c1-240 | head -12
echo
echo "=== RUN5.md on the branch: does it carry the Sept 25 plan? ==="
git show "$REF:rl/RUN5.md" | grep -n -E 'revised Sept 25|registered with its census footprint|reserve' | cut -c1-200 | head -10
echo "branch RUN5 last commit: $(git log -1 --format='%h %ai' "$REF" -- rl/RUN5.md)"
echo "main   RUN5 last commit: $(git log -1 --format='%h %ai' HEAD -- rl/RUN5.md)"
echo
echo "=== when did the table start? first partial commit d141623: lines in kpr3_500.jsonl ==="
echo "d141623: $(git show d141623:rl/results/kpr_2026-09-25/kpr3_500.jsonl | wc -l) lines at 2026-09-26 00:15:19"
echo "f6e8bca: $(git show f6e8bca:rl/results/kpr_2026-09-25/kpr3_500.jsonl | wc -l) lines at 00:16:30"
echo "c002d2f: $(git show c002d2f:rl/results/kpr_2026-09-25/kpr3_500.jsonl | wc -l) lines at 00:18:10"
echo "8f16338: $(git show 8f16338:rl/results/kpr_2026-09-25/kpr3_500.jsonl | wc -l) lines at 00:42:52"
echo
echo "=== run_kpr3_table.sh history (was it fixed before the table?) ==="
git log --reverse --format='%h %ai %s' "$REF" -- rl/results/kpr_2026-09-25/run_kpr3_table.sh | cut -c1-120
echo
echo "=== deck_averages.py history (fixed before the table?) ==="
git log --reverse --format='%h %ai %s' "$REF" -- rl/results/kpr_2026-09-25/deck_averages.py | cut -c1-120
echo
echo "=== kd3 and kq3 fit on the Sept 23 table (README lines 50-51) ==="
python3 - <<'PY'
import json, re, math
from pathlib import Path
R = Path("/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/75cb92d0-6f2d-44b8-a636-513a8f7ee71a/scratchpad/reviews/branch/ref")
lim = {}
text = (R / "limitless_check_2026-09-23.md").read_text(encoding="utf-8").split("### Rules4, every pairing")[1].split("## Part 2")[0]
for line in text.splitlines():
    m = re.match(r"\|\s*(\w+) v (\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+) ± ([\d.]+)\s*\|", line)
    if m:
        lim[(m.group(1), m.group(2))] = float(m.group(4))
for bot in ("kd3", "kq3"):
    s = {}
    for line in open(R / f"{bot}_500.jsonl"):
        if line.strip():
            g = json.loads(line); c = (g["a"], g["b"]); s.setdefault(c, []).append(g["first_deck_score"])
    miss = [100 * sum(v) / len(v) - lim[c] for c, v in s.items()]
    print(f"  {bot}: cells {len(miss)}, mean |miss| {sum(abs(m) for m in miss)/len(miss):.2f}, mean squared miss {sum(m*m for m in miss)/len(miss):.1f}")
PY
echo
echo "=== hidden_continuation_reason: what does it read? (observation.rs at e09fb46) ==="
git show e09fb46:engine/src/observation.rs | grep -n -A 30 'pub fn hidden_continuation_reason' | head -60
