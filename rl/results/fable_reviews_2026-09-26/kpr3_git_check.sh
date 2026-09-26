#!/usr/bin/env bash
# Read-only checks of the cloud branch for the kpr3 plan-compliance review. No checkout, working tree untouched.
set -u
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REF="origin/claude/pensive-ptolemy-spwc0b"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/75cb92d0-6f2d-44b8-a636-513a8f7ee71a/scratchpad/reviews"
REFD="$OUT/branch/ref"
cd "$REPO" || { echo "cannot cd to repo"; exit 1; }
mkdir -p "$REFD" "$OUT/branch/readme_history"

echo "=== branch head ==="
git log -1 --format='%H %ai %s' "$REF"
echo
echo "=== the kpr commits, with author dates (iso) ==="
for c in b356ff8 9a35f54 0adfeb7 1981bb4 53638a7 14c7d9b e09fb46 c002d2f aa87fa3; do
  git log -1 --format='%h %ai (committer %ci) %s' "$c" 2>/dev/null || echo "$c: not found"
done
echo
echo "=== is each commit on the branch? (merge-base --is-ancestor) ==="
for c in b356ff8 9a35f54 0adfeb7 1981bb4 53638a7 14c7d9b e09fb46 c002d2f; do
  if git merge-base --is-ancestor "$c" "$REF" 2>/dev/null; then echo "$c on branch"; else echo "$c NOT on branch"; fi
done
echo
echo "=== commits on the branch from 9a35f54 to head, oldest first, with engine/ file counts ==="
git log --reverse --format='%h %ai %s' 9a35f54^.."$REF" | while read -r h d t rest; do
  n=$(git show --stat --format= "$h" -- engine/ | grep -c '|')
  echo "$h $d $t  engine files: $n :: $rest"
done
echo
echo "=== diff --stat 53638a7..e09fb46 (everything) ==="
git diff --stat 53638a7 e09fb46
echo
echo "=== diff --stat 1981bb4..e09fb46 -- engine/ ==="
git diff --stat 1981bb4 e09fb46 -- engine/
echo
echo "=== diff 53638a7..e09fb46 -- engine/src (saved to branch/diff_53638a7_e09fb46_engine_src.patch) ==="
git diff 53638a7 e09fb46 -- engine/src > "$OUT/branch/diff_53638a7_e09fb46_engine_src.patch"
wc -l "$OUT/branch/diff_53638a7_e09fb46_engine_src.patch"
echo
echo "=== diff 53638a7..e09fb46 -- engine/src, hunks outside #[cfg(test)] regions: function names touched ==="
grep -E '^@@' "$OUT/branch/diff_53638a7_e09fb46_engine_src.patch" | head -60
echo
echo "=== diff --stat 858b6fe..e09fb46 -- engine/ (kp3 table build to kpr table build) ==="
git diff --stat 858b6fe e09fb46 -- engine/ | tail -40
echo
echo "=== diff --stat 858b6fe..e09fb46 -- engine/src excluding players/ ==="
git diff --stat 858b6fe e09fb46 -- engine/src ':(exclude)engine/src/players/' | tail -40
echo
echo "=== README history: every commit touching rl/results/kpr_2026-09-25/README.md ==="
git log --reverse --format='%h %ai %s' "$REF" -- rl/results/kpr_2026-09-25/README.md
echo
echo "=== README at 9a35f54 (registration) saved ==="
git show 9a35f54:rl/results/kpr_2026-09-25/README.md > "$OUT/branch/readme_history/README_9a35f54.md" 2>/dev/null && wc -l "$OUT/branch/readme_history/README_9a35f54.md" || echo "no README at 9a35f54"
for c in 0adfeb7 1981bb4 14c7d9b 53638a7 e09fb46 c002d2f; do
  git show "$c:rl/results/kpr_2026-09-25/README.md" > "$OUT/branch/readme_history/README_$c.md" 2>/dev/null && echo "README_$c.md: $(wc -l < "$OUT/branch/readme_history/README_$c.md") lines" || echo "no README at $c"
done
echo
echo "=== 'footprint' / 'census' lines in the registration README (9a35f54) ==="
grep -n -i -E 'footprint|census|formula|weight|500|100 per' "$OUT/branch/readme_history/README_9a35f54.md" | head -40
echo
echo "=== commit messages in full: 9a35f54 0adfeb7 1981bb4 14c7d9b 53638a7 e09fb46 ==="
for c in 9a35f54 0adfeb7 1981bb4 14c7d9b 53638a7 e09fb46; do echo "--- $c ---"; git log -1 --format='%B' "$c"; done
echo
echo "=== files in rl/results/kpr_2026-09-25/ on the branch, with sizes ==="
git ls-tree -r -l "$REF" -- rl/results/kpr_2026-09-25/
echo
echo "=== which commit added each kpr result file (first appearance) ==="
for f in kpr3_500.jsonl kpr3_500.txt table_commit_identity_k3_40.jsonl table_commit_identity_kp3_40.jsonl table_commit_identity_kq3_40.jsonl identity_k3_500.jsonl identity_kp3_500.jsonl identity_kq3_500.jsonl identity_kd3_40.jsonl identity_k3_9a35f54_partial.jsonl timing.txt mutation_results_e09fb46.txt review_1981bb4_workflow_output.json; do
  echo "$f: $(git log --reverse --format='%h %ai' "$REF" -- "rl/results/kpr_2026-09-25/$f" | head -1) ... last $(git log -1 --format='%h %ai' "$REF" -- "rl/results/kpr_2026-09-25/$f")"
done
echo
echo "=== c002d2f partial kpr3_500.jsonl vs final: first 1000 lines identical? ==="
git show c002d2f:rl/results/kpr_2026-09-25/kpr3_500.jsonl > "$REFD/kpr3_500_partial_c002d2f.jsonl"
git show "$REF:rl/results/kpr_2026-09-25/kpr3_500.jsonl" | head -n "$(wc -l < "$REFD/kpr3_500_partial_c002d2f.jsonl")" > "$REFD/kpr3_500_final_head.jsonl"
if cmp -s "$REFD/kpr3_500_partial_c002d2f.jsonl" "$REFD/kpr3_500_final_head.jsonl"; then echo "IDENTICAL ($(wc -l < "$REFD/kpr3_500_partial_c002d2f.jsonl") lines)"; else echo "DIFFER"; diff "$REFD/kpr3_500_partial_c002d2f.jsonl" "$REFD/kpr3_500_final_head.jsonl" | head -5; fi
echo
echo "=== copy reference tables and the table-commit identity files for fingerprint checks ==="
copy() { if git show "$REF:$1" > "$REFD/$2" 2>/dev/null; then echo "copied $1 -> ref/$2 ($(wc -l < "$REFD/$2") lines)"; else echo "MISSING on branch: $1"; rm -f "$REFD/$2"; fi; }
copy rl/results/per_game_table_2026-09-25/k3_500.jsonl                 k3_500.jsonl
copy rl/results/public_pricing_2026-09-25/kp3_500_worst5.jsonl         kp3_500_worst5.jsonl
copy rl/results/public_pricing_2026-09-25/kp3_500_rest.jsonl           kp3_500_rest.jsonl
copy rl/results/kq_2026-09-25/kq3_500.jsonl                            kq3_500.jsonl
copy rl/results/kd_2026-09-25/kd3_500.jsonl                            kd3_500.jsonl
copy rl/results/kpr_2026-09-25/table_commit_identity_k3_40.jsonl       table_commit_identity_k3_40.jsonl
copy rl/results/kpr_2026-09-25/table_commit_identity_kp3_40.jsonl      table_commit_identity_kp3_40.jsonl
copy rl/results/kpr_2026-09-25/table_commit_identity_kq3_40.jsonl      table_commit_identity_kq3_40.jsonl
copy rl/results/kpr_2026-09-25/table_commit_identity_k3_40.txt         table_commit_identity_k3_40.txt
copy rl/results/kpr_2026-09-25/table_commit_identity_kp3_40.txt        table_commit_identity_kp3_40.txt
copy rl/results/kpr_2026-09-25/table_commit_identity_kq3_40.txt        table_commit_identity_kq3_40.txt
copy rl/results/kpr_2026-09-25/identity_k3_500.jsonl                   identity_k3_500.jsonl
copy rl/results/kpr_2026-09-25/identity_kq3_500.jsonl                  identity_kq3_500.jsonl
copy rl/results/kpr_2026-09-25/identity_kd3_40.jsonl                   identity_kd3_40.jsonl
copy rl/results/kpr_2026-09-25/identity_k3_9a35f54_partial.jsonl       identity_k3_9a35f54_partial.jsonl
copy rl/results/limitless_check_2026-09-23.md                          limitless_check_2026-09-23.md
copy rl/results/discard_attack_census_2026-09-25/README.md             discard_census_README.md
echo
echo "=== branch dirs mentioning footprint / census (rl/results) ==="
git ls-tree "$REF" -- rl/results/ | awk '{print $4}' | grep -i -E 'census|footprint|scoreboard|holdout'
echo
echo "=== grep 'footprint' on the branch (rl/ and docs/) ==="
git grep -n -i 'footprint' "$REF" -- rl docs | cut -c1-220 | head -30
echo
echo "=== main (local HEAD) vs branch: merge-base and scoreboard v2 location ==="
git rev-parse --abbrev-ref HEAD
git log -1 --format='%h %ai %s' HEAD
git merge-base HEAD "$REF"
git ls-tree HEAD -- rl/results/ | awk '{print $4}' | grep -i -E 'scoreboard|holdout|table_readings'
git ls-tree -r -l HEAD -- rl/results/scoreboard_v2_2026-09-25/ 2>/dev/null | head -20
echo
echo "=== is scoreboard v2 on the branch? ==="
git ls-tree -r -l "$REF" -- rl/results/scoreboard_v2_2026-09-25/ 2>/dev/null | head -20
echo
echo "=== local main: score.py location ==="
git ls-files HEAD | grep -E 'score\.py|scoreboard' | head -20
