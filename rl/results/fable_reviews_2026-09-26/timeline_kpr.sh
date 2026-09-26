#!/usr/bin/env bash
# Read-only timeline check of the kpr work on the cloud branch. No checkout, working tree untouched.
set -u
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
REF="origin/claude/pensive-ptolemy-spwc0b"
OUT="/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/75cb92d0-6f2d-44b8-a636-513a8f7ee71a/scratchpad/reviews/branch"
cd "$REPO" || { echo "cannot cd to repo"; exit 1; }

echo "=== commits touching rl/results/kpr_2026-09-25 or engine/src/players (author date, committer date) ==="
git log --format='%h  a:%ad  c:%cd  %s' --date=iso "$REF" -- rl/results/kpr_2026-09-25 engine/src/players | head -40
echo
echo "=== every commit from 9a35f54 to head, with dates ==="
git log --format='%h  a:%ad  c:%cd  %s' --date=iso 9a35f54~1.."$REF" | cat
echo
echo "=== which commits changed kpr3_500.jsonl and README.md, with line counts of kpr3_500.jsonl at each ==="
for c in $(git log --format='%h' "$REF" -- rl/results/kpr_2026-09-25/kpr3_500.jsonl); do
  n=$(git show "$c:rl/results/kpr_2026-09-25/kpr3_500.jsonl" 2>/dev/null | wc -l)
  echo "$c $(git log -1 --format='%cd' --date=iso $c) kpr3_500.jsonl lines=$n"
done
echo
echo "=== engine/ tree hash per commit from 9a35f54 to head (same engine claim) ==="
for c in $(git log --format='%h' 9a35f54~1.."$REF"); do
  echo "$c $(git rev-parse "$c:engine") $(git log -1 --format='%s' $c | cut -c1-60)"
done
echo
echo "=== does the partial kpr3_500.jsonl at c002d2f equal the head file's same (pairing,i) records? ==="
git show c002d2f:rl/results/kpr_2026-09-25/kpr3_500.jsonl > "$OUT/kpr3_500_partial_c002d2f.jsonl"
echo "partial lines: $(wc -l < "$OUT/kpr3_500_partial_c002d2f.jsonl")"
echo
echo "=== kp3 table on branch: copy worst5 + rest for baseline identity check ==="
git show "$REF:rl/results/public_pricing_2026-09-25/kp3_500_worst5.jsonl" > "$OUT/kp3_500_worst5.jsonl"
git show "$REF:rl/results/public_pricing_2026-09-25/kp3_500_rest.jsonl" > "$OUT/kp3_500_rest.jsonl"
git show "$REF:rl/results/per_game_table_2026-09-25/k3_500.jsonl" > "$OUT/k3_500.jsonl"
wc -l "$OUT/kp3_500_worst5.jsonl" "$OUT/kp3_500_rest.jsonl" "$OUT/k3_500.jsonl"
echo
echo "=== limitless check md on branch -> copy ==="
git show "$REF:rl/results/limitless_check_2026-09-23.md" > "$OUT/limitless_check_2026-09-23.md" && echo "copied limitless ($(wc -l < "$OUT/limitless_check_2026-09-23.md") lines)"
echo
echo "=== table_commit_identity files on branch? ==="
git ls-tree -r -l "$REF" -- rl/results/kpr_2026-09-25/ | grep -i -E 'identity|review_|mutate|partial'
echo
echo "=== kpr README history: which commits touched it ==="
git log --format='%h %cd %s' --date=iso "$REF" -- rl/results/kpr_2026-09-25/README.md | cat
echo
echo "=== diff of README between c002d2f and head (only the table section) ==="
git diff c002d2f "$REF" -- rl/results/kpr_2026-09-25/README.md | head -150
echo
echo "=== legality_scan: where does it print Hyper Ray turns / KO-able (engine source) ==="
git grep -n -E 'Hyper Ray turns|KO-able|not KO-able' "$REF" -- engine/src | head -20
echo
echo "=== legality_scan parallelism: threads / rayon / par_iter in the scan binary ==="
git grep -n -E 'rayon|par_iter|thread::spawn|num_threads' "$REF" -- engine/src/bin | head -20
git ls-tree "$REF" -- engine/src/bin/ | cat
